"""Capacity estimation from random-walk operation (no capacity label used by the physics model).

Neural-ECM (PINN-type hybrid): a shared neural OCV curve f(z) inside a 1RC equivalent-circuit model,
    V(t) = f(z(t)) - R0_k I(t) - v1(t),  z(t) = 1 - Ah(t)/Q_k,  dv1/dt = -v1/tau + I R1_k / tau,
with per-cycle (Q_k, R0_k, R1_k) and the voltage residual as the only loss (+ a monotonicity penalty on f).
Stage 1 fits f and the per-cycle parameters on training cells; stage 2 freezes f and fits the per-cycle
parameters of unseen cells. The capacity estimate of a cycle is Q_k; a linear calibration Q_ref ~ a Q + b is
fitted on training cells only (the z-domain of f is defined up to scale).
"""
from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np
import optax
from scipy.signal import lfilter

TAU = 60.0  # s, fixed RC time constant (assumption logged)
DT = 10.0


def rc_input(I: np.ndarray, tau: float = TAU, dt: float = DT) -> np.ndarray:
    """u such that v1 = R1 * u for the Euler-exact (ZOH) 1RC recursion v1[n+1] = a v1[n] + (1-a) R1 I[n], v1[0]=0."""
    a = np.exp(-dt / tau)
    u = np.zeros_like(I)
    u[1:] = lfilter([1 - a], [1, -a], I[:-1])
    return u


def ecm_voltage(ocv, ah, I, u, Q, R0, R1):
    z = 1.0 - ah / Q
    return ocv(z) - R0 * I - R1 * u


def pad(cycles, maxlen=None):
    n = len(cycles)
    L = max(len(c.t) for c in cycles) if maxlen is None else maxlen
    A = {k: np.zeros((n, L), np.float32) for k in ("ah", "I", "V", "u", "m")}
    for i, c in enumerate(cycles):
        m = min(len(c.t), L)
        A["ah"][i, :m], A["I"][i, :m], A["V"][i, :m] = c.ah[:m], c.I[:m], c.V[:m]
        A["u"][i, :m] = rc_input(c.I)[:m]
        A["m"][i, :m] = 1.0
    return {k: jnp.asarray(v) for k, v in A.items()}


def init_ocv(key, h=32):
    k1, k2, k3 = jax.random.split(key, 3)
    return [(jax.random.normal(k1, (1, h)) * 1.0, jnp.zeros(h)), (jax.random.normal(k2, (h, h)) / jnp.sqrt(h), jnp.zeros(h)),
            (jax.random.normal(k3, (h, 1)) / jnp.sqrt(h), jnp.zeros(1))]


def ocv_apply(p, z):
    x = z[..., None] * 2.0 - 1.0
    for w, b in p[:-1]:
        x = jnp.tanh(x @ w + b)
    w, b = p[-1]
    return 3.7 + 0.5 * (x @ w + b)[..., 0]


def fit(A, ocv_params=None, seed=0, steps=3000, lr=1e-2, train_ocv=True):
    n = A["V"].shape[0]
    key = jax.random.PRNGKey(seed)
    params = {"logQ": jnp.full(n, jnp.log(2.0)), "R0": jnp.full(n, 0.08), "R1": jnp.full(n, 0.03)}
    params["ocv"] = ocv_params if ocv_params is not None else init_ocv(key)
    zgrid = jnp.linspace(-0.2, 1.0, 64)

    def loss(p):
        ocv = lambda z: ocv_apply(p["ocv"], z)
        Vh = ecm_voltage(ocv, A["ah"], A["I"], A["u"], jnp.exp(p["logQ"])[:, None], p["R0"][:, None], p["R1"][:, None])
        res = (Vh - A["V"]) * A["m"]
        mse = jnp.sum(res ** 2) / jnp.sum(A["m"])
        mono = jnp.mean(jax.nn.relu(-jnp.diff(ocv(zgrid))) ** 2) * 1e3
        return mse + mono, mse

    opt = optax.adam(lr)

    def masked(g):
        if not train_ocv:
            g = dict(g)
            g["ocv"] = jax.tree_util.tree_map(jnp.zeros_like, g["ocv"])
        return g

    @jax.jit
    def step(p, s):
        (l, mse), g = jax.value_and_grad(loss, has_aux=True)(p)
        u, s = opt.update(masked(g), s, p)
        return optax.apply_updates(p, u), s, mse

    s = opt.init(params)
    for _ in range(steps):
        params, s, mse = step(params, s)
    return params, float(np.sqrt(mse))
