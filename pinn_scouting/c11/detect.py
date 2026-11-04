"""Physics-residual fault detection and sensor/process attribution on GPVS-Faults (v2: operating-point invariant).

Training: ONLY the two healthy runs F0M and F0L, first 60 % of their cycles each (after a 0.5 s start-up of the
PMU estimator). Validation (threshold): last 40 % of both F0 runs. Test: the 14 faulty runs; cycles before 0.45 T
are healthy (false alarms), cycles after 0.5 T are faulty (nominal onset 'halfway'; exact onset unpublished, so
delays are relative to T/2 and approximate).

Residuals are built to be invariant to the operating point (insolation, MPPT vs IPPT), because a single short
healthy run cannot span the between-experiment variability (v1, with residuals referenced to the F0 operating
point, gave ~100 % false alarms on the healthy halves of other runs):
  closure   e = P_pv - |P_ac| - (c0 + c1 P_pv)       converter loss model fitted on F0M+F0L (energy conservation)
  redundancy  vsum/Vabc, (vmag-Vabc)/Vabc, vimb, isum/Iabc, (imag-Iabc)/Iabc, iimb, If-Vf
  dynamics  rolling std (10 cycles) of Vdc/Vdc_ma, P_pv/P_pv_ma and of the closure e, ma = moving median 50 cycles
Whitening: median / MAD scaling + Ledoit-Wolf covariance on training cycles. Alarm: T^2 > q-quantile of validation
T^2, for `persist` consecutive cycles.

Attribution (physics, no labels): energy must be conserved by any real process change. After an alarm,
'sensor/measurement' if the closure residual is the dominant violation (|z_e| > k and |z_e| exceeds every other
|z|), else 'process'.
"""
from __future__ import annotations

import numpy as np
from sklearn.covariance import LedoitWolf

from gpvs import load, raw_features

NAMES = ["closure", "vsum", "vmag", "vimb", "isum", "imag", "iimb", "freq", "vdc_osc", "ppv_osc", "closure_osc"]
T_START = 0.5


def roll(x, w, fn):
    return np.array([fn(x[max(0, i - w + 1): i + 1]) for i in range(len(x))])


def loss_model(fs):
    """Least squares P_loss = c0 + c1 P_pv on the training cycles of the healthy runs."""
    ppv = np.concatenate([f["ppv"] for f in fs])
    loss = np.concatenate([f["ppv"] - np.abs(f["pac"]) for f in fs])
    A = np.stack([np.ones_like(ppv), ppv], 1)
    c, *_ = np.linalg.lstsq(A, loss, rcond=None)
    return c


def residual_matrix(f, c):
    e = f["ppv"] - np.abs(f["pac"]) - (c[0] + c[1] * f["ppv"])
    vab, iab = np.maximum(f["Vabc"], 1e-3), np.maximum(f["Iabc"], 1e-3)
    vdc_rel = f["vdc"] / np.maximum(roll(f["vdc"], 50, np.median), 1e-3)
    ppv_rel = f["ppv"] / np.maximum(roll(f["ppv"], 50, np.median), 1e-3)
    cols = [e, f["vsum"] / vab, (f["vmag"] - f["Vabc"]) / vab, f["vimb"], f["isum"] / iab, (f["imag"] - f["Iabc"]) / iab,
            f["iimb"], f["If"] - f["Vf"], roll(vdc_rel, 10, np.std), roll(ppv_rel, 10, np.std), roll(e, 10, np.std)]
    return np.stack(cols, 1)


def split_f0(f):
    idx = np.where(f["t"] > T_START)[0]
    n = int(0.6 * len(idx))
    return idx[:n], idx[n:]


class PhysicsDetector:
    def __init__(self, q=0.999, persist=3, k_sigma=6.0, cols=None):
        self.q, self.persist, self.k = q, persist, k_sigma
        self.cols = list(range(len(NAMES))) if cols is None else cols

    def fit(self):
        F = [raw_features(load(n)) for n in ("F0M", "F0L")]
        sp = [split_f0(f) for f in F]
        self.c = loss_model([{k: v[tr] for k, v in f.items()} for f, (tr, _) in zip(F, sp)])
        R = [residual_matrix(f, self.c)[:, self.cols] for f in F]
        Rtr = np.concatenate([r[tr] for r, (tr, _) in zip(R, sp)])
        Rva = np.concatenate([r[va] for r, (_, va) in zip(R, sp)])
        self.med = np.median(Rtr, 0)
        self.scale = 1.4826 * np.median(np.abs(Rtr - self.med), 0) + 1e-12
        self.cov = LedoitWolf().fit((Rtr - self.med) / self.scale)
        self.val_t2 = self.t2(Rva)
        self.thr = float(np.quantile(self.val_t2, self.q))
        return self

    def z(self, R):
        return (R - self.med) / self.scale

    def t2(self, R):
        return self.cov.mahalanobis(self.z(R))

    def alarms(self, R):
        a = self.t2(R) > self.thr
        out, c = np.zeros(len(a), bool), 0
        for i, v in enumerate(a):
            c = c + 1 if v else 0
            out[i] = c >= self.persist
        return out

    def attribute(self, R, idx):
        if "closure" not in [NAMES[c] for c in self.cols]:
            return "process", 0.0
        z = np.abs(self.z(R[idx]))
        j = [NAMES[c] for c in self.cols].index("closure")
        others = np.delete(z, j, axis=1).max(1)
        sensor = (z[:, j] > self.k) & (z[:, j] >= others)
        return ("sensor" if sensor.mean() > 0.5 else "process"), float(sensor.mean())

    def residuals(self, f):
        return residual_matrix(f, self.c)[:, self.cols]


def evaluate_file(det, name):
    f = raw_features(load(name))
    R = det.residuals(f)
    t, T = f["t"], f["t"][-1]
    al = det.alarms(R)
    healthy, faulty = (t > T_START) & (t < 0.45 * T), t > 0.5 * T
    hit = np.where(al & faulty)[0]
    att, share = det.attribute(R, hit) if len(hit) else ("none", float("nan"))
    return {"file": name, "fa_rate": float(al[healthy].mean()), "n_healthy": int(healthy.sum()),
            "det_rate": float(al[faulty].mean()), "n_faulty": int(faulty.sum()),
            "delay_s": float(t[hit[0]] - 0.5 * T) if len(hit) else float("nan"), "attribution": att, "sensor_share": share}
