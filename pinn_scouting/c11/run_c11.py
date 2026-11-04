"""C11 experiments on GPVS-Faults.

Protocol (leave-one-experiment-out, LOEO). For each of the 14 faulty runs r:
  healthy training/validation pool = F0M, F0L (after 0.5 s) + the healthy parts (0.5 s .. 0.45 T) of the 13 OTHER
  faulty runs. Faults were introduced halfway (dataset ReadMe), so these parts are healthy by construction; no
  fault label is used. 70 % of each healthy segment trains, the last 30 % validates (threshold at quantile q).
  Test on run r: healthy part -> false alarms, post-onset part (t > 0.5 T) -> detection.
Methods (all unsupervised, same pool, same threshold rule):
  PHYS  physics residuals (closure with fitted loss model, redundancy, dynamics), robust whitening, T^2
  PCA   PCA T^2 + SPE on the 52 statistical signatures of Wali & Khan (mean/std/max/min of 13 signals per cycle)
  PCA-R PCA on the physics residuals (ablation: physics features, data-driven statistic)
Supervised references (use fault labels, multiclass F0..F7, MPPT runs as in Wali & Khan):
  RF-random  random 70/30 split of cycles (the published protocol)
  RF-time    train on the first 60 % of each run's cycles, test on the last 40 % (temporal split)
  RF-mode    train on MPPT runs, test on IPPT runs (cross-mode)
"""
from __future__ import annotations

import json
import os

import numpy as np
from sklearn.covariance import LedoitWolf
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from detect import NAMES, T_START, loss_model, residual_matrix
from gpvs import cycles, load, raw_features

OUT = "results"
os.makedirs(OUT, exist_ok=True)
RUNS = [f"F{i}{m}" for m in "ML" for i in range(1, 8)]
SIG = ["Ipv", "Vpv", "Vdc", "ia", "ib", "ic", "va", "vb", "vc", "Iabc", "If", "Vabc", "Vf"]
Q, PERSIST, K = 0.999, 3, 6.0


def signatures(d):
    c = cycles(d)
    return np.concatenate([np.stack([c[s].mean(1), c[s].std(1), c[s].max(1), c[s].min(1)], 1) for s in SIG], 1)


DATA = {}
for n in ["F0M", "F0L"] + RUNS:
    d = load(n)
    f = raw_features(d)
    t, T = f["t"], f["t"][-1]
    healthy = (t > T_START) & ((t < 0.45 * T) if n not in ("F0M", "F0L") else np.ones_like(t, bool))
    DATA[n] = {"f": f, "sig": signatures(d), "t": t, "T": T, "healthy": healthy, "faulty": (t > 0.5 * T) & (n not in ("F0M", "F0L"))}


def split_seg(mask):
    idx = np.where(mask)[0]
    k = int(0.7 * len(idx))
    return idx[:k], idx[k:]


def persist(a, p=PERSIST):
    out, c = np.zeros(len(a), bool), 0
    for i, v in enumerate(a):
        c = c + 1 if v else 0
        out[i] = c >= p
    return out


class Whitened:
    def fit(self, X):
        self.m = np.median(X, 0)
        self.s = 1.4826 * np.median(np.abs(X - self.m), 0) + 1e-12
        self.cov = LedoitWolf().fit((X - self.m) / self.s)
        return self

    def z(self, X):
        return (X - self.m) / self.s

    def score(self, X):
        return self.cov.mahalanobis(self.z(X))


class PCAdet:
    def fit(self, X, var=0.95):
        self.sc = StandardScaler().fit(X)
        Z = self.sc.transform(X)
        self.p = PCA(n_components=var, svd_solver="full").fit(Z)
        self.lam = self.p.explained_variance_
        return self

    def score(self, X):
        Z = self.sc.transform(X)
        S = self.p.transform(Z)
        t2 = np.sum(S ** 2 / self.lam, 1)
        spe = np.sum((Z - self.p.inverse_transform(S)) ** 2, 1)
        return t2, spe


def loeo():
    rows = []
    for test in RUNS:
        pool = [n for n in DATA if n != test]
        tr_idx = {n: split_seg(DATA[n]["healthy"]) for n in pool}
        c = loss_model([{k: v[tr_idx[n][0]] for k, v in DATA[n]["f"].items()} for n in pool])
        R = {n: residual_matrix(DATA[n]["f"], c) for n in pool + [test]}
        Xtr = lambda key: np.concatenate([key(n)[tr_idx[n][0]] for n in pool])
        Xva = lambda key: np.concatenate([key(n)[tr_idx[n][1]] for n in pool])
        D = DATA[test]
        res = {}
        # PHYS
        w = Whitened().fit(Xtr(lambda n: R[n]))
        thr = np.quantile(w.score(Xva(lambda n: R[n])), Q)
        al = persist(w.score(R[test]) > thr)
        res["PHYS"] = al
        # attribution on PHYS alarms
        hit = np.where(al & D["faulty"])[0]
        att, share = "none", float("nan")
        if len(hit):
            z = np.abs(w.z(R[test][hit]))
            j = NAMES.index("closure")
            sensor = (z[:, j] > K) & (z[:, j] >= np.delete(z, j, 1).max(1))
            share = float(sensor.mean())
            att = "sensor" if share > 0.5 else "process"
        # PCA on signatures and on residuals
        for name, key in (("PCA", lambda n: DATA[n]["sig"]), ("PCA-R", lambda n: R[n])):
            p = PCAdet().fit(Xtr(key))
            t2v, spev = p.score(Xva(key))
            t2, spe = p.score(key(test))
            res[name] = persist((t2 > np.quantile(t2v, Q)) | (spe > np.quantile(spev, Q)))
        for m, a in res.items():
            hitm = np.where(a & D["faulty"])[0]
            rows.append({"run": test, "fault": test[:2], "mode": test[2], "method": m,
                         "fa_rate": float(a[D["healthy"]].mean()), "det_rate": float(a[D["faulty"]].mean()),
                         "delay_s": float(D["t"][hitm[0]] - 0.5 * D["T"]) if len(hitm) else None,
                         "attribution": att if m == "PHYS" else None, "sensor_share": share if m == "PHYS" else None,
                         "n_healthy": int(D["healthy"].sum()), "n_faulty": int(D["faulty"].sum())})
        print(test, {m: (round(r["fa_rate"], 3), round(r["det_rate"], 3)) for m in res for r in rows[-3:] if r["method"] == m}, att)
    return rows


def supervised():
    out = {}
    def xy(names, part=None):
        X, y = [], []
        for n in names:
            D = DATA[n]
            lab = np.where(D["faulty"], int(n[1]), 0)
            keep = D["healthy"] | D["faulty"]
            idx = np.where(keep)[0]
            if part == "first":
                idx = idx[: int(0.6 * len(idx))]
            elif part == "last":
                idx = idx[int(0.6 * len(idx)):]
            X.append(D["sig"][idx]); y.append(lab[idx])
        return np.concatenate(X), np.concatenate(y)
    M = ["F0M"] + [r for r in RUNS if r.endswith("M")]
    L = ["F0L"] + [r for r in RUNS if r.endswith("L")]
    X, y = xy(M)
    accs = []
    for sd in range(5):
        Xa, Xb, ya, yb = train_test_split(X, y, test_size=0.3, random_state=sd, stratify=y)
        rf = RandomForestClassifier(n_estimators=18, max_features="log2", random_state=sd).fit(Xa, ya)
        accs.append((accuracy_score(yb, rf.predict(Xb)), f1_score(yb, rf.predict(Xb), average="macro")))
    out["RF-random (published protocol)"] = np.mean(accs, 0).tolist() + np.std(accs, 0).tolist()
    accs = []
    for sd in range(5):
        Xa, ya = xy(M, "first"); Xb, yb = xy(M, "last")
        rf = RandomForestClassifier(n_estimators=18, max_features="log2", random_state=sd).fit(Xa, ya)
        accs.append((accuracy_score(yb, rf.predict(Xb)), f1_score(yb, rf.predict(Xb), average="macro")))
    out["RF-time (first 60% -> last 40% of each run)"] = np.mean(accs, 0).tolist() + np.std(accs, 0).tolist()
    accs = []
    for sd in range(5):
        Xa, ya = xy(M); Xb, yb = xy(L)
        rf = RandomForestClassifier(n_estimators=18, max_features="log2", random_state=sd).fit(Xa, ya)
        accs.append((accuracy_score(yb, rf.predict(Xb)), f1_score(yb, rf.predict(Xb), average="macro")))
    out["RF-mode (MPPT -> IPPT)"] = np.mean(accs, 0).tolist() + np.std(accs, 0).tolist()
    return out


if __name__ == "__main__":
    rows = loeo()
    sup = supervised()
    json.dump({"loeo": rows, "supervised": sup, "q": Q, "persist": PERSIST, "k_sigma": K}, open(f"{OUT}/results.json", "w"), indent=1)
    print(json.dumps(sup, indent=1))
