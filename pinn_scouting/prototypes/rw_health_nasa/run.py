"""Feasibility: estimate reference capacity of NASA RW cells from random-walk operation only.

Splits
  ID  : leave-one-cell-out inside the 40 C skewed-high group (RW25-28), 4 folds.
  OOD : train on all four 40 C cells, test on the room-temperature uniform group (RW3-6): different ambient,
        different load distribution (0.5-4 A uniform), deeper ageing (Q_ref down to ~1.06 Ah, never seen in training).
Methods
  coulomb : Ah discharged to the 3.2 V cut-off in the RW cycle, linear calibration on training cells.
  ridge / mlp : data-driven regression on 11 per-cycle features (sklearn), trained on training cells.
  necm    : neural-ECM fitted on voltage only (labels never used), linear calibration of Q on training cells.
Each reference capacity is matched with the 5 RW cycles that follow it; estimates are averaged over them.
Cycles shorter than 0.1 Ah (truncated) are dropped. Seeds 0-2 for mlp and necm.
"""
from __future__ import annotations

import json
import os
import time

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from data import all_cells, cycle_features, label_cycles, load_cell
from models import fit, pad

OUT = "results"
os.makedirs(OUT, exist_ok=True)
SEEDS = (0, 1, 2)
STEPS = 2500


def load_group(g):
    D = {}
    for c in all_cells(g):
        cy, refs = load_cell(g, c)
        cy = [x for x in cy if x.ah[-1] > 0.1 and np.isfinite(x.V).all()]
        D[c] = (cy, label_cycles(cy, refs))
    return D


def table(D, cells):
    """Per labelled group: feature mean, Ah mean, ref capacity, cycle ids."""
    X, A, y, ids, who = [], [], [], [], []
    for c in cells:
        cy, pairs = D[c]
        for idx, qr, _ in pairs:
            f = np.stack([cycle_features(cy[i]) for i in idx])
            X.append(f.mean(0)); A.append(f[:, 0].mean()); y.append(qr); ids.append(idx); who.append(c)
    return np.array(X), np.array(A), np.array(y), ids, who


def necm_estimates(D, cells, ocv=None, seed=0, every=5):
    """Fit on the labelled cycles plus every `every`-th cycle (the per-cycle parameters are independent given the
    shared OCV, so unused cycles only add cost)."""
    cyc, owner = [], []
    for c in cells:
        cy, pairs = D[c]
        need = set(range(0, len(cy), every)) | {int(i) for idx, _, _ in pairs for i in idx}
        for i in sorted(need):
            cyc.append(cy[i]); owner.append((c, i))
    A = pad(cyc, maxlen=None)
    p, vrmse = fit(A, ocv_params=ocv, seed=seed, steps=STEPS, train_ocv=ocv is None)
    Q = np.exp(np.asarray(p["logQ"]))
    lut = {o: q for o, q in zip(owner, Q)}
    return p, lut, vrmse


def group_q(lut, ids, who):
    return np.array([np.mean([lut[(c, i)] for i in idx]) for idx, c in zip(ids, who)])


def score(y, yh):
    e = yh - y
    return {"rmse_Ah": float(np.sqrt(np.mean(e ** 2))), "mae_Ah": float(np.mean(np.abs(e))), "max_Ah": float(np.max(np.abs(e))),
            "mape_pct": float(np.mean(np.abs(e) / y) * 100), "r2": float(1 - np.sum(e ** 2) / np.sum((y - y.mean()) ** 2)), "n": int(len(y))}


def run():
    t0 = time.time()
    H, R = load_group("high40"), load_group("uniRT")
    folds = [("ID", [c for c in H if c != t], [t], H, H) for t in H] + [("OOD", list(H), list(R), H, R)]
    rows = []
    for split, tr, te, Dtr, Dte in folds:
        Xtr, Atr, ytr, idtr, wtr = table(Dtr, tr)
        Xte, Ate, yte, idte, wte = table(Dte, te)
        # cycles whose temperature channel is entirely invalid give NaN features: impute with training medians
        med = np.nanmedian(Xtr, axis=0)
        Xtr = np.where(np.isfinite(Xtr), Xtr, med)
        Xte = np.where(np.isfinite(Xte), Xte, med)
        # coulomb
        a, b = np.polyfit(Atr, ytr, 1)
        rows.append({"split": split, "test": "+".join(te), "method": "coulomb", "seed": 0, **score(yte, a * Ate + b)})
        # data-driven
        rg = make_pipeline(StandardScaler(), Ridge(alpha=1.0)).fit(Xtr, ytr)
        rows.append({"split": split, "test": "+".join(te), "method": "ridge", "seed": 0, **score(yte, rg.predict(Xte))})
        for sd in SEEDS:
            ml = make_pipeline(StandardScaler(), MLPRegressor(hidden_layer_sizes=(32, 32), max_iter=3000, random_state=sd)).fit(Xtr, ytr)
            rows.append({"split": split, "test": "+".join(te), "method": "mlp", "seed": sd, **score(yte, ml.predict(Xte))})
            # neural-ECM: stage 1 on training cells (voltage only), stage 2 on test cells with OCV frozen
            p, lut_tr, v_tr = necm_estimates(Dtr, tr, seed=sd)
            _, lut_te, v_te = necm_estimates(Dte, te, ocv=p["ocv"], seed=sd)
            qtr, qte = group_q(lut_tr, idtr, wtr), group_q(lut_te, idte, wte)
            a2, b2 = np.polyfit(qtr, ytr, 1)
            rows.append({"split": split, "test": "+".join(te), "method": "necm", "seed": sd, **score(yte, a2 * qte + b2),
                         "v_rmse_train_V": v_tr, "v_rmse_test_V": v_te, "corr_raw_test": float(np.corrcoef(qte, yte)[0, 1])})
            if sd == 0:
                np.save(f"{OUT}/pred_{split}_{'+'.join(te)}.npy", {"y": yte, "coulomb": a * Ate + b, "ridge": rg.predict(Xte),
                        "mlp": ml.predict(Xte), "necm": a2 * qte + b2, "who": wte}, allow_pickle=True)
        print(f"{split} test={te} done {time.time() - t0:.0f}s")
    json.dump(rows, open(f"{OUT}/rows.json", "w"), indent=1)


if __name__ == "__main__":
    run()
