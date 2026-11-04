"""Minimal feasibility study: core temperature of LG M50 cells (WMG data), leave-one-instrumented-cell-out.

Scenarios
  S1 'full'   : labels = all blocks of the two training instrumented cells; test = all blocks of the held-out cell.
  S2 'scarce' : labels = block 0 only (first ~20 cycles) of the two training cells; test = blocks 1-4 of the
                held-out cell (later ageing). The PINN residual uses all blocks of the training cells and of the
                three non-instrumented cells (never the test cell: no transductive use of test data).
Methods: Biot quasi-steady (B1), one-state lumped model (B2), windowed MLP (DD), same MLP + lumped residual (PINN).
Seeds: 3 for DD and PINN (B1/B2 deterministic). No tuning was done on the test cells; hyper-parameters fixed below.
"""
from __future__ import annotations

import json
import os
import time

import numpy as np

from data import DT, INSTRUMENTED, PRISTINE, load_all, stack
from models import (fit_biot, fit_lumped, lumped_residual, predict_biot, predict_mlp, simulate_lumped, train)

W = 30            # 5 min window
EPOCHS = 6
SEEDS = (0, 1, 2)
LAM = float(os.environ.get("LAM", "1.0"))   # a-priori value 1.0; other values = post-hoc sensitivity
OUT = os.environ.get("OUT", "results")
os.makedirs(OUT, exist_ok=True)


def metrics(y, yhat, ts, i2, theta, dtc_true):
    m = np.isfinite(y) & np.isfinite(yhat)
    e = yhat[m] - y[m]
    peak = m & (dtc_true >= np.nanpercentile(dtc_true[m], 90))
    cc, rc, r0 = theta
    r = lumped_residual(yhat[:-1], yhat[1:], ts[:-1], i2[:-1], cc, rc, r0)
    r = r[np.isfinite(r)]
    return {"rmse": float(np.sqrt(np.mean(e ** 2))), "mae": float(np.mean(np.abs(e))), "max": float(np.max(np.abs(e))),
            "r2": float(1 - np.sum(e ** 2) / np.sum((y[m] - y[m].mean()) ** 2)),
            "rmse_peak": float(np.sqrt(np.mean((yhat[peak] - y[peak]) ** 2))), "phys_res_rms_W": float(np.sqrt(np.mean(r ** 2)))}


def series_pred(method, s, ctx):
    """Prediction of Tc on the full resampled series s (NaN where the window is not filled)."""
    if method == "biot":
        return predict_biot(s, ctx["g"])
    if method == "lumped":
        return simulate_lumped(s, *ctx["theta"])
    from data import windows
    w = windows(s, W)
    out = np.full_like(s.Ts, np.nan)
    if w is not None:
        out[w["k"]] = w["Ts"] + predict_mlp(ctx["params"], w["X"])
    return out


def run():
    t0 = time.time()
    D = load_all()
    rows, figs = [], {}
    for scen in ("full", "scarce"):
        for test in INSTRUMENTED:
            train_cells = [c for c in INSTRUMENTED if c != test]
            lab = [s for c in train_cells for s in D[c] if np.isfinite(s.Tc).mean() > 0.5 and (scen == "full" or s.block == 0)]
            tst = [s for s in D[test] if np.isfinite(s.Tc).mean() > 0.5 and (scen == "full" or s.block >= 1)]
            unl = [s for c in train_cells + list(PRISTINE) for s in D[c]]
            g = fit_biot(lab)
            theta = fit_lumped(lab, stride=3)
            L = stack(lab, W)
            ok = np.isfinite(L["y"])
            U = stack(unl, W)
            # features at k+1 for the residual: next row of the same series (windows are consecutive)
            nxt = np.r_[U["k"][1:] == U["k"][:-1] + 1, False]
            phys = {"X1": U["X"][1:][nxt[:-1]], "Ts": U["Ts"][:-1][nxt[:-1]], "Ts1": U["Ts1"][:-1][nxt[:-1]],
                    "I2": U["I2"][:-1][nxt[:-1]]}
            Xu = U["X"][:-1][nxt[:-1]]
            ctxs = {"biot": [{"g": g}], "lumped": [{"theta": theta}]}
            for name, lam in (("mlp", 0.0), ("pinn", LAM)):
                ctxs[name] = []
                for sd in SEEDS:
                    p, hist = train(L["X"][ok], L["y"][ok], Xu if lam else None, phys if lam else None, lam=lam,
                                    epochs=EPOCHS, seed=sd, theta0=theta)
                    ctxs[name].append({"params": p, "hist": hist,
                                       "theta_learned": [float(theta[0])] + [float(v) for v in np.exp(np.asarray(p["log_theta"]))]})
            for name, cl in ctxs.items():
                for si, ctx in enumerate(cl):
                    yh = np.concatenate([series_pred(name, s, ctx) for s in tst])
                    y = np.concatenate([s.Tc for s in tst])
                    ts = np.concatenate([s.Ts for s in tst])
                    i2 = np.concatenate([s.I2 for s in tst])
                    met = metrics(y, yh, ts, i2, theta, y - ts)
                    rows.append({"scenario": scen, "test_cell": test, "method": name, "seed": si, **met,
                                 "theta_lumped": [float(v) for v in theta], "biot_G": g,
                                 "theta_pinn": ctx.get("theta_learned")})
                    if si == 0:
                        figs[(scen, test, name)] = (tst[-1].t, tst[-1].Ts, tst[-1].Tc, series_pred(name, tst[-1], ctx))
            print(f"[{scen}] test={test} done ({time.time() - t0:.0f}s) G={g:.3f} theta={np.round(theta, 4)}")
    json.dump(rows, open(f"{OUT}/rows.json", "w"), indent=1)
    np.save(f"{OUT}/fig_series.npy", {f"{k[0]}|{k[1]}|{k[2]}": v for k, v in figs.items()}, allow_pickle=True)
    print("total", time.time() - t0)


if __name__ == "__main__":
    run()
