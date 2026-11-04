"""MAFAULDA fault classification: a Fourier neural operator on the order spectra against classical models on chosen
features, with splits that never share a run and a split across rotation speed.

Tasks (:data:`TASKS`): misalignment (normal / horizontal / vertical), unbalance (normal / imbalance), bearings
(normal / three faults at two positions) and all ten states. Inputs:

* chosen features per channel (:func:`feature_matrix`): RMS, kurtosis, skewness, crest factor, peak, amplitudes at
  1X-4X from the order spectrum, envelope amplitudes at FTF, BSF, about 3X and about 5X, and the speed;
* spectra (:func:`spectrum_tensor`): amplitude and envelope order spectra on 0-``max_order`` orders, log-scaled.

Models: random forest and MLP on the features (scikit-learn), :class:`FNOClassifier` on the spectra (the library's
1-D :class:`~pinneapple_neural.architectures.neural_operators.fno.FourierNeuralOperator`, mean and max over the order axis,
the speed appended, a linear layer). Protocols (:func:`splits`): ``"folds"`` stratified k-fold by run; ``"speed"``
speed terciles, train on two and test on the third.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import numpy as np

from .mafaulda import BEARING_ORDERS

BEARINGS = [f"{p}/{f}" for p in ("underhang", "overhang") for f in ("ball_fault", "cage_fault", "outer_race")]
TASKS = {
    "misalignment": ["normal", "horizontal-misalignment", "vertical-misalignment"],
    "unbalance": ["normal", "imbalance"],
    "bearings": ["normal"] + BEARINGS,
    "all": ["normal", "imbalance", "horizontal-misalignment", "vertical-misalignment"] + BEARINGS,
}
STEP = 0.01                                   # order grid of the cached spectra


def _amp(spec: np.ndarray, order: float, half_width: float = 0.03) -> np.ndarray:
    i0, i1 = int(round((order - half_width) / STEP)), int(round((order + half_width) / STEP)) + 1
    return spec[max(i0, 0):i1].max(0)


def select(rows: list[dict[str, Any]], task: str) -> tuple[list[dict[str, Any]], np.ndarray]:
    """Rows of the task's states (reliable tachometer, no read error) and their integer labels."""
    states = TASKS[task]
    keep = [r for r in rows if "error" not in r and r.get("tach_ok", True) and r["state"] in states]
    return keep, np.array([states.index(r["state"]) for r in keep])


def feature_names(n_channels: int = 7) -> list[str]:
    per = ["rms", "kurtosis", "skewness", "crest", "peak", "1X", "2X", "3X", "4X", "env_FTF", "env_BSF", "env_3X",
           "env_5X"]
    return [f"{p}_c{c}" for c in range(n_channels) for p in per] + ["speed_hz"]


def feature_matrix(rows: list[dict[str, Any]]) -> np.ndarray:
    out = []
    for r in rows:
        S, E = r["order_spectrum"], r["envelope_spectrum"]
        per = [r["rms"], r["kurtosis"], r["skewness"], r["crest"], r["peak"]]
        per += [_amp(S, k) for k in (1, 2, 3, 4)]
        per += [_amp(E, BEARING_ORDERS["FTF"]), _amp(E, BEARING_ORDERS["BSF"]), _amp(E, 3.0, 0.05), _amp(E, 5.0, 0.05)]
        out.append(np.concatenate([np.stack(per, 1).ravel(), [r["speed_hz"]]]))
    return np.array(out)


def spectrum_tensor(rows: list[dict[str, Any]], max_order: float = 8.0) -> tuple[np.ndarray, np.ndarray]:
    """(n, 2 x channels, n_orders) log-scaled amplitude and envelope order spectra, and the speeds."""
    n = int(round(max_order / STEP)) + 1
    X = np.stack([np.concatenate([r["order_spectrum"][:n].T, r["envelope_spectrum"][:n].T], 0) for r in rows])
    return np.log1p(X / np.median(X[X > 0])).astype(np.float32), np.array([r["speed_hz"] for r in rows], np.float32)


def splits(y: np.ndarray, speed: np.ndarray, protocol: str, k: int = 5, seed: int = 0):
    """``(name, train index, test index)`` for ``"folds"`` (stratified k-fold) or ``"speed"`` (terciles)."""
    if protocol == "folds":
        from sklearn.model_selection import StratifiedKFold
        for i, (tr, te) in enumerate(StratifiedKFold(k, shuffle=True, random_state=seed).split(np.zeros(len(y)), y)):
            yield f"fold{i}", tr, te
    elif protocol == "speed":
        edges = np.quantile(speed, [0, 1 / 3, 2 / 3, 1])
        band = np.clip(np.searchsorted(edges, speed, side="right") - 1, 0, 2)
        for b, name in enumerate(("low", "mid", "high")):
            yield f"speed_{name}_{edges[b]:.0f}-{edges[b + 1]:.0f}Hz", np.flatnonzero(band != b), np.flatnonzero(band == b)
    else:
        raise ValueError(protocol)


@dataclass
class FNOClassifier:
    """FNO on the order spectra -> mean and max over the order axis, with the speed -> small MLP -> class logits."""
    width: int = 32
    modes: int = 48
    layers: int = 3
    epochs: int = 80
    lr: float = 2e-3
    batch: int = 64
    seed: int = 0

    def _net(self, in_c, n_cls):
        import torch.nn as nn

        from pinneapple_neural.architectures.neural_operators.fno import FourierNeuralOperator

        class Net(nn.Module):
            def __init__(s):
                super().__init__()
                s.fno = FourierNeuralOperator(in_c, self.width, width=self.width, modes=self.modes,
                                              layers=self.layers, use_grid=True)
                s.head = nn.Sequential(nn.Linear(2 * self.width + 1, 64), nn.GELU(), nn.Linear(64, n_cls))

            def forward(s, x, sp):
                import torch
                h = s.fno(x).y                                   # mean and max over orders: a line is a peak
                return s.head(torch.cat([h.mean(-1), h.amax(-1), sp[:, None]], 1))
        return Net()

    def fit(self, X, sp, y):
        import torch
        torch.manual_seed(self.seed)
        self.n_cls = int(y.max()) + 1
        self.sp_mu, self.sp_sd = float(sp.mean()), float(sp.std() + 1e-9)
        self.net = self._net(X.shape[1], self.n_cls)
        opt = torch.optim.AdamW(self.net.parameters(), lr=self.lr, weight_decay=1e-4)
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, self.epochs)
        Xt, St, yt = torch.as_tensor(X), torch.as_tensor((sp - self.sp_mu) / self.sp_sd), torch.as_tensor(y)
        w = torch.as_tensor(len(y) / (self.n_cls * np.bincount(y, minlength=self.n_cls).clip(1)), dtype=torch.float32)
        loss_fn = torch.nn.CrossEntropyLoss(weight=w)
        g = torch.Generator().manual_seed(self.seed)
        t0 = time.perf_counter()
        for _ in range(self.epochs):
            self.net.train()
            for idx in torch.randperm(len(y), generator=g).split(self.batch):
                opt.zero_grad()
                loss_fn(self.net(Xt[idx], St[idx]), yt[idx]).backward()
                opt.step()
            sched.step()
        self.seconds = time.perf_counter() - t0
        return self

    def predict(self, X, sp):
        import torch
        self.net.eval()
        with torch.no_grad():
            return self.net(torch.as_tensor(X), torch.as_tensor((sp - self.sp_mu) / self.sp_sd)).argmax(1).numpy()


def _fit_predict(model, Xf, Xs, sp, y, tr, te, seed):
    if model == "fno":
        return FNOClassifier(seed=seed).fit(Xs[tr], sp[tr], y[tr]).predict(Xs[te], sp[te])
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.neural_network import MLPClassifier
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    if model == "rf":
        clf = RandomForestClassifier(500, class_weight="balanced", random_state=seed, n_jobs=4)
    elif model == "mlp":
        clf = make_pipeline(StandardScaler(), MLPClassifier((128, 64), alpha=1e-3, max_iter=3000,
                                                            random_state=seed))
    else:
        raise ValueError(model)
    return clf.fit(Xf[tr], y[tr]).predict(Xf[te])


def run_task(rows, task, models=("rf", "mlp", "fno"), protocols=("folds", "speed"), seed=0, log=print,
             done: dict | None = None, save=None, budget_s: float | None = None):
    """Every (protocol, model) of a task. ``done``: results already computed (``"protocol/model"`` keys), skipped;
    ``save(out)`` is called after each new result and ``budget_s`` stops before starting a new one once the time is
    spent, so a long study can be resumed after an interruption."""
    from sklearn.metrics import confusion_matrix, f1_score
    sel, y = select(rows, task)
    Xf = feature_matrix(sel)
    Xs, sp = spectrum_tensor(sel)
    out = {"task": task, "classes": TASKS[task], "n": int(len(y)), "counts": np.bincount(y).tolist(),
           "results": dict(done or {})}
    t_start = time.perf_counter()
    for proto in protocols:
        for model in models:
            key = f"{proto}/{model}"
            if key in out["results"]:
                continue
            if budget_s is not None and time.perf_counter() - t_start > budget_s:
                out["incomplete"] = True
                return out
            pred = np.full(len(y), -1)
            per = {}
            t0 = time.perf_counter()
            for name, tr, te in splits(y, sp, proto, seed=seed):
                pred[te] = _fit_predict(model, Xf, Xs, sp, y, tr, te, seed)
                per[name] = float(f1_score(y[te], pred[te], average="macro"))
            out["results"][key] = {
                "macro_f1": float(f1_score(y, pred, average="macro")), "accuracy": float(np.mean(pred == y)),
                "per_split_macro_f1": per, "confusion": confusion_matrix(y, pred).tolist(),
                "seconds": time.perf_counter() - t0}
            log(f"{task:12s} {proto:5s} {model:4s} macro-F1 {out['results'][key]['macro_f1']:.3f} "
                f"({', '.join(f'{k} {v:.2f}' for k, v in per.items())})")
            if save:
                save(out)
    out.pop("incomplete", None)
    return out


def criteria(results: dict[str, dict]) -> dict[str, Any]:
    """The pre-registered criteria C1-C4 of the research log."""
    def f1(t, key):
        return results[t]["results"][key]["macro_f1"]
    models = ("rf", "mlp", "fno")
    c1 = all(f1(t, f"folds/{m}") >= 0.95 for t in ("misalignment", "unbalance") for m in models)
    gains = {t: f1(t, "speed/fno") - f1(t, "speed/rf") for t in results}
    c2 = sum(g >= 0.03 for g in gains.values()) >= 2
    c3 = {m: f1("bearings", f"folds/{m}") >= 0.90 for m in models} if "bearings" in results else None
    drops = {t: {m: f1(t, f"folds/{m}") - f1(t, f"speed/{m}") for m in models} for t in results}
    return {"C1_easy_tasks_ge_0.95": c1, "C2_fno_gain_over_rf_speed": gains, "C2_pass": c2,
            "C3_bearings_ge_0.90": c3, "C4_drop_folds_to_speed": drops,
            "C4_models_not_generalising": {t: [m for m, d in v.items() if d > 0.15] for t, v in drops.items()}}
