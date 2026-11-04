"""Estimators of core temperature from current, voltage and surface temperature.

B1  Biot quasi-steady relation:   Tc = Ts + G (Ts - Tamb)          (G fitted by least squares)
B2  one-state lumped thermal model driven by the measured surface temperature (classical physics):
        Cc dTc/dt = R0 I^2 - (Tc - Ts)/Rc,   Tc(0) = Ts(0)          (Cc, Rc, R0 fitted by simulation error)
DD  windowed MLP (data-driven), predicts Tc - Ts from the last w*DT seconds of features
PINN same MLP + discrete-time residual of the B2 equation evaluated on every cell, including the cells with no
     core sensor (unlabelled collocation); (Cc, Rc, R0) are learnable (log-parametrised).
"""
from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np
import optax
from scipy.optimize import least_squares

from data import DT, Series


# ------------------------------------------------------------------ physics
def lumped_step(tc, ts, i2, cc, rc, r0, dt=DT):
    """Explicit Euler step of Cc dTc/dt = R0 I^2 - (Tc - Ts)/Rc."""
    return tc + dt / cc * (r0 * i2 - (tc - ts) / rc)


def lumped_residual(tc_k, tc_k1, ts_k, i2_k, cc, rc, r0, dt=DT):
    """Discrete residual (W): Cc (Tc[k+1]-Tc[k])/dt - (R0 I^2 - (Tc[k]-Ts[k])/Rc). Zero on an exact Euler trajectory."""
    return cc * (tc_k1 - tc_k) / dt - (r0 * i2_k - (tc_k - ts_k) / rc)


def simulate_lumped(s: Series, cc, rc, r0, dt=DT):
    """Euler recursion Tc[k+1] = a Tc[k] + b[k] with a = 1 - dt/(Cc Rc), b = dt/Cc (R0 I2 + Ts/Rc), via lfilter."""
    from scipy.signal import lfilter
    a = 1.0 - dt / (cc * rc)
    ts = np.nan_to_num(s.Ts, nan=float(np.nanmean(s.Ts)))
    b = dt / cc * (r0 * s.I2 + ts / rc)
    tc = np.empty_like(ts)
    tc[0] = ts[0]
    # y[n] = a y[n-1] + b[n-1] for n >= 1, y[0] = ts[0]
    zi = np.array([a * ts[0]])
    tc[1:], _ = lfilter([1.0], [1.0, -a], b[:-1], zi=zi)
    return tc


def simulate_lumped_loop(s: Series, cc, rc, r0, dt=DT):
    """Reference implementation (slow) used by the unit tests."""
    tc = np.empty_like(s.Ts)
    tc[0] = s.Ts[0]
    for k in range(len(s.Ts) - 1):
        tc[k + 1] = lumped_step(tc[k], s.Ts[k], s.I2[k], cc, rc, r0, dt)
    return tc


# ------------------------------------------------------------------ B1
def fit_biot(series: list[Series]) -> float:
    x = np.concatenate([s.Ts - s.Tamb for s in series])
    y = np.concatenate([s.Tc - s.Ts for s in series])
    m = np.isfinite(x) & np.isfinite(y)
    return float((x[m] @ y[m]) / (x[m] @ x[m]))


def predict_biot(s: Series, g: float):
    return s.Ts + g * (s.Ts - s.Tamb)


# ------------------------------------------------------------------ B2
CC_FIX = 50.0  # J/K, nominal core heat capacity (LG M50 ~70 g; only tau = Cc Rc and R0/Cc are identifiable)


def fit_lumped(series: list[Series], x0=(1.5, 0.03), stride: int = 1):
    """Fit (Rc, R0) with Cc fixed: with Ts as input the model is identifiable only through Cc*Rc and R0/Cc
    (a 3-parameter fit drifts to a degenerate quasi-static solution, observed on this data)."""
    def res(p):
        rc, r0 = np.exp(p)
        cc = CC_FIX
        out = []
        for s in series:
            e = simulate_lumped(s, cc, rc, r0) - s.Tc
            out.append(np.nan_to_num(e[::stride]))
        return np.concatenate(out)
    sol = least_squares(res, np.log(x0), method="trf", x_scale=1.0, max_nfev=200)
    rc, r0 = np.exp(sol.x)
    return (CC_FIX, float(rc), float(r0))


# ------------------------------------------------------------------ MLP / PINN (JAX)
def init_mlp(key, sizes):
    params = []
    for a, b in zip(sizes[:-1], sizes[1:]):
        key, k = jax.random.split(key)
        params.append((jax.random.normal(k, (a, b)) * jnp.sqrt(2.0 / a), jnp.zeros(b)))
    return params


def mlp(params, x):
    for w, b in params[:-1]:
        x = jnp.tanh(x @ w + b)
    w, b = params[-1]
    return (x @ w + b)[..., 0]


def train(Xl, yl, Xu=None, phys=None, lam=0.0, hidden=(64, 64), epochs=4, batch=2048, lr=2e-3, seed=0,
          theta0=(50.0, 1.5, 0.03)):
    """Data loss on labelled rows (Xl, yl = Tc - Ts). If lam > 0, add the lumped residual on unlabelled rows:
    phys = dict(X1 = features at k+1, Ts, Ts1, I2) aligned with Xu (features at k)."""
    key = jax.random.PRNGKey(seed)
    params = {"net": init_mlp(key, (Xl.shape[1],) + tuple(hidden) + (1,)),
              "log_theta": jnp.log(jnp.asarray(theta0[1:]))}  # (Rc, R0); Cc fixed at theta0[0]
    cc_fix = float(theta0[0])
    opt = optax.adam(lr)
    state = opt.init(params)

    def loss_fn(p, xb, yb, xu, xu1, ts, ts1, i2):
        ld = jnp.mean((mlp(p["net"], xb) - yb) ** 2)
        if lam == 0.0:
            return ld, (ld, 0.0)
        rc, r0 = jnp.exp(p["log_theta"])
        cc = cc_fix
        tck = ts + mlp(p["net"], xu)
        tck1 = ts1 + mlp(p["net"], xu1)
        r = lumped_residual(tck, tck1, ts, i2, cc, rc, r0) / 0.1  # scale: 0.1 W
        lp = jnp.mean(r ** 2)
        return ld + lam * lp, (ld, lp)

    @jax.jit
    def step(p, s, xb, yb, xu, xu1, ts, ts1, i2):
        (l, aux), g = jax.value_and_grad(loss_fn, has_aux=True)(p, xb, yb, xu, xu1, ts, ts1, i2)
        u, s = opt.update(g, s, p)
        return optax.apply_updates(p, u), s, aux

    rng = np.random.default_rng(seed)
    nl = len(Xl)
    nu = 0 if Xu is None else len(Xu)
    hist = []
    dummy = np.zeros((1, Xl.shape[1]), np.float32)
    for ep in range(epochs):
        perm = rng.permutation(nl)
        for i in range(0, nl, batch):
            b = perm[i:i + batch]
            if lam > 0:
                u = rng.integers(0, nu, size=batch)
                args = (Xu[u], phys["X1"][u], phys["Ts"][u], phys["Ts1"][u], phys["I2"][u])
            else:
                args = (dummy, dummy, np.zeros(1), np.zeros(1), np.zeros(1))
            params, state, aux = step(params, state, Xl[b], yl[b], *args)
        hist.append((float(aux[0]), float(aux[1])))
    return params, hist


def predict_mlp(params, X):
    return np.asarray(mlp(params["net"], X))
