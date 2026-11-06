"""Phase 5b: measurement-robust training (pre-registered in PROTOCOL.md "Phase 5b", configuration fixed a priori).

Motivation (Phase 8): the order-spectrum CNN loses 0.1-0.4 macro-F1 when one sensor is dead or (COMFAULDA, T3, T4)
when the speed estimate is off by 1-2 %; feature models break at +-2 %. Both are measurement errors expected in
service (speed estimated from vibration, failed accelerometer).
  cnn-spec-rob  cnn-spec of Phase 1, same architecture and schedule; each training sample is, with probability 0.5,
                re-sampled on the order axis as if the speed were off by e ~ U(-2 %, +2 %) (x'(o) = x(o (1+e)), the
                speed input scaled by (1+e)), and each sensor is dropped (its amplitude and envelope channels set to
                0 in the log-normalised space, i.e. the dead-sensor level) with probability 0.1 (at least one kept).
  rf-rob        RF of Phase 1 trained on the training runs plus, for each, two copies with a speed error
                e ~ U(-2 %, +2 %) and one copy with one random dead sensor (phase8_robust.perturb).
The test runs are never augmented; the +-5 % and gain x2 conditions of Phase 8 are outside the training perturbations.
"""
from __future__ import annotations

import numpy as np

from models import n_params, spectra
from models2 import _resnet1d, _torch, _train_loop

JITTER, P_JIT, P_DROP = 0.02, 0.5, 0.1


def _order_jitter(x, e):
    """x: (B, C, L) tensor, e: (B,) array; returns x(o (1+e)) by linear interpolation (edge-clamped)."""
    torch = _torch()
    L = x.shape[-1]
    p = torch.as_tensor(np.arange(L)[None, :] * (1 + e[:, None]), dtype=torch.float32).clamp(0, L - 1)
    i0 = p.floor().long().clamp(max=L - 2)
    w = (p - i0).unsqueeze(1)
    idx0 = i0.unsqueeze(1).expand(-1, x.shape[1], -1)
    return x.gather(2, idx0) * (1 - w) + x.gather(2, idx0 + 1) * w


def cnn_spec_rob(epochs=100, lr=1e-3, width=32, blocks=4):
    def fp(sel, y, sp, tr, te, seed):
        torch = _torch()
        torch.manual_seed(seed)
        X = spectra(sel, 8.0)
        med = np.maximum(np.median(X[tr], axis=(0, 2)), 1e-12)
        Z = np.log1p(X / med[None, :, None]).astype(np.float32)
        mu, sd = sp[tr].mean(), sp[tr].std() + 1e-9
        S = torch.as_tensor(((sp - mu) / sd)[:, None], dtype=torch.float32)
        n_cls = int(y.max()) + 1
        n_s = Z.shape[1] // 2
        net = _resnet1d(Z.shape[1], n_cls, width, blocks)
        Zt = torch.as_tensor(Z)
        trv = np.asarray(tr)

        def batches(idx, rng):
            ii = trv[idx]
            xb = Zt[ii].clone()
            e = np.where(rng.random(len(ii)) < P_JIT, rng.uniform(-JITTER, JITTER, len(ii)), 0.0)
            xb = _order_jitter(xb, e)
            drop = rng.random((len(ii), n_s)) < P_DROP
            drop[drop.all(1)] = False
            m = torch.as_tensor(np.concatenate([~drop, ~drop], 1).astype(np.float32))[:, :, None]
            sb = torch.as_tensor(((sp[ii] * (1 + e) - mu) / sd)[:, None], dtype=torch.float32)
            return xb * m, sb
        secs = _train_loop(net, batches, len(tr), y[tr], epochs, lr, seed, n_cls)
        net.eval()
        with torch.no_grad():
            pr = torch.softmax(net(Zt[te], S[te]), 1).numpy()
        return pr.argmax(1), pr, {"fit_seconds": secs, "n_params": n_params(net)}
    return fp


def rf_rob():
    def fp(sel, y, sp, tr, te, seed):
        from sklearn.ensemble import RandomForestClassifier

        import q1lib as L
        from phase8_robust import perturb
        rng = np.random.default_rng(seed)
        n_ch = np.asarray(sel[0]["order_spectrum"]).shape[1]
        aug, ya = [], []
        for i in np.asarray(tr):
            for _ in range(2):
                aug.append(perturb(sel[i], "speed", float(rng.uniform(-JITTER, JITTER)))); ya.append(y[i])
            aug.append(perturb(sel[i], "dead", int(rng.integers(n_ch)))); ya.append(y[i])
        Xtr = np.concatenate([L.C.feature_matrix([sel[i] for i in tr]), L.C.feature_matrix(aug)])
        ytr = np.concatenate([y[tr], ya])
        clf = RandomForestClassifier(500, class_weight="balanced", random_state=seed, n_jobs=4).fit(Xtr, ytr)
        pr = np.zeros((len(te), int(y.max()) + 1))
        pr[:, clf.classes_] = clf.predict_proba(L.C.feature_matrix([sel[i] for i in te]))
        return pr.argmax(1), pr, {"n_train_aug": int(len(ytr))}
    return fp


EXTRA3 = {"cnn-spec-rob": cnn_spec_rob(), "rf-rob": rf_rob()}
