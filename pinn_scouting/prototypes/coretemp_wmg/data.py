"""Data pipeline for the WMG core-temperature ageing dataset (Mendeley bf6fksxpp2, CC BY 4.0).

Input: per-cell NPZ files written by `pinn_scouting/tools/wmg_convert.py` from
`ShortTermAgeing_100cycles/100cycles_dataTable.mat` (1 Hz, 5 test blocks of ~20 cycles per cell).
Set WMG_NPZ to the folder holding `short_VP0xx.npz` (default /home/user/data_raw/wmg_npz).

Processing (all choices are logged in LOG.md):
* core-temperature sentinel -3276.8 C and any value outside [-40, 90] C -> NaN (sensor dropout, VP011);
* resample each block to DT seconds by block-averaging; the Joule driver is the mean of I^2 over the
  interval (not the square of the mean current), so heat input is not lost by averaging;
* ambient temperature is not logged: T_amb per block = 1st percentile of the surface temperature in that block
  (the chamber set-point is 25 C; the cells start each block at rest near ambient).
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np

NPZ_DIR = os.environ.get("WMG_NPZ", "/home/user/data_raw/wmg_npz")
INSTRUMENTED = ("VP010", "VP011", "VP012")
PRISTINE = ("VP016", "VP017", "VP018")
DT = 10.0  # s
SENTINEL = -3276.8


@dataclass
class Series:
    """One test block of one cell, resampled to DT."""
    cell: str
    block: int
    t: np.ndarray       # s, from block start
    I: np.ndarray       # A, mean over interval (positive = charge in this dataset's convention)
    I2: np.ndarray      # A^2, mean of I^2 over interval
    V: np.ndarray       # V
    Ts: np.ndarray      # surface temperature, C
    Tc: np.ndarray      # core temperature, C (NaN where unavailable)
    Tamb: float         # C


def clean_core(tc: np.ndarray) -> np.ndarray:
    tc = np.asarray(tc, dtype=float).copy()
    bad = (np.abs(tc - SENTINEL) < 1e-6) | (tc < -40) | (tc > 90)
    tc[bad] = np.nan
    return tc


def _bin_mean(x: np.ndarray, idx: np.ndarray, n: int) -> np.ndarray:
    s = np.bincount(idx, weights=np.nan_to_num(x), minlength=n)
    c = np.bincount(idx, weights=np.isfinite(x).astype(float), minlength=n)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(c > 0, s / c, np.nan)


def resample_block(t_s: np.ndarray, cols: dict, dt: float = DT) -> dict:
    """Average every column over consecutive dt windows of the time axis t_s (seconds)."""
    t0 = t_s[0]
    idx = np.floor((t_s - t0) / dt).astype(int)
    n = int(idx.max()) + 1
    out = {k: _bin_mean(v, idx, n) for k, v in cols.items()}
    out["t"] = np.arange(n) * dt
    keep = np.isfinite(out["V"])
    return {k: v[keep] for k, v in out.items()}


def load_cell(cell: str, npz_dir: str = NPZ_DIR, dt: float = DT) -> list[Series]:
    z = np.load(os.path.join(npz_dir, f"short_{cell}.npz"))
    t = z["t_ms"] / 1000.0
    tc = clean_core(z["Tc"]) if "Tc" in z.files else np.full_like(t, np.nan)
    out = []
    for b in np.unique(z["block"]):
        m = z["block"] == b
        if m.sum() < 100:
            continue
        cols = {"I": z["I"][m], "I2": z["I"][m] ** 2, "V": z["V"][m], "Ts": z["Ts"][m], "Tc": tc[m]}
        r = resample_block(t[m], cols, dt)
        ts = r["Ts"][np.isfinite(r["Ts"])]
        out.append(Series(cell, int(b), r["t"], r["I"], r["I2"], r["V"], r["Ts"], r["Tc"],
                          float(np.percentile(ts, 1))))
    return out


def load_all(cells=INSTRUMENTED + PRISTINE, npz_dir: str = NPZ_DIR, dt: float = DT) -> dict[str, list[Series]]:
    return {c: load_cell(c, npz_dir, dt) for c in cells}


# ------------------------------------------------------------------ features for windowed estimators
FEATURES = ("I2", "I", "V", "dTs_amb", "dTs")


def windows(s: Series, w: int = 30):
    """Rows k >= w: lagged features over the last w steps (w*DT seconds) -> X (n, w*F).
    Targets: y = Tc - Ts at k. Also returns aligned (Ts, Tc, I2) at k and k+1 for the physics residual."""
    dts = np.r_[0.0, np.diff(s.Ts)]
    F = np.stack([s.I2 / 25.0, s.I / 5.0, (s.V - 3.6) / 0.6, (s.Ts - s.Tamb) / 10.0, dts * 10.0], axis=1)
    F = np.nan_to_num(F)
    n = len(s.t)
    if n <= w + 1:
        return None
    idx = np.arange(w, n - 1)
    X = np.stack([F[k - w + 1:k + 1].ravel() for k in idx]).astype(np.float32)
    return {"X": X, "y": (s.Tc[idx] - s.Ts[idx]).astype(np.float32), "Ts": s.Ts[idx], "Tc": s.Tc[idx],
            "Ts1": s.Ts[idx + 1], "I2": s.I2[idx], "Tamb": np.full(len(idx), s.Tamb), "block": np.full(len(idx), s.block),
            "k": idx}


def stack(series: list[Series], w: int = 30) -> dict:
    parts = [p for p in (windows(s, w) for s in series) if p is not None]
    return {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
