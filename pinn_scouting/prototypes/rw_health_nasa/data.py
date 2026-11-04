"""Loader for the NASA Randomized Battery Usage data (RW cells), S3 mirror of the PCoE repository.

Set NASA_RW to the folder holding the unzipped group folders (default /home/user/data_raw/nasa_rw).
Groups used in the prototype:
  RW_Skewed_High_40C_DataSet_2Post            RW25-RW28, 0.5-5 A skewed high, ~40 C
  Battery_Uniform_Distribution_Discharge_Room_Temp_DataSet_2Post  RW3-RW6, 0.5-4 A uniform, room T
A random-walk (RW) cycle = consecutive 'discharge (random walk)' / 'rest (random walk)' steps between a charge and
'rest post random walk discharge'. Reference capacity = Ah of each 'reference discharge' (1 A to 3.2 V).
"""
from __future__ import annotations

import glob
import os
from dataclasses import dataclass

import numpy as np
import scipy.io as sio

ROOT = os.environ.get("NASA_RW", "/home/user/data_raw/nasa_rw")
GROUPS = {"high40": "RW_Skewed_High_40C_DataSet_2Post", "uniRT": "Battery_Uniform_Distribution_Discharge_Room_Temp_DataSet_2Post"}


@dataclass
class RWCycle:
    cell: str
    idx: int          # RW cycle number within the cell
    t0: float         # experiment time at cycle start (s)
    t: np.ndarray     # s from cycle start
    I: np.ndarray     # A, discharge positive
    V: np.ndarray
    T: np.ndarray
    ah: np.ndarray    # Ah discharged since cycle start


def _arr(x):
    return np.atleast_1d(np.asarray(x, dtype=float))


def load_cell(group: str, cell: str, root: str = ROOT, dt: float = 10.0):
    path = os.path.join(root, GROUPS[group], "data", "Matlab", f"{cell}.mat")
    st = sio.loadmat(path, simplify_cells=True)["data"]["step"]
    cycles, refs, cur = [], [], []
    for s in st:
        c = s["comment"]
        if c in ("discharge (random walk)", "rest (random walk)"):
            cur.append(s)
        elif cur and c != "discharge (random walk)":
            cycles.append(cur)
            cur = []
        if c == "reference discharge":
            t, i = _arr(s["relativeTime"]), _arr(s["current"])
            refs.append((float(_arr(s["time"])[0]), float(np.trapezoid(i, t) / 3600.0)))
    out = []
    for n, steps in enumerate(cycles):
        t = np.concatenate([_arr(s["time"]) for s in steps])
        I = np.concatenate([_arr(s["current"]) for s in steps])
        V = np.concatenate([_arr(s["voltage"]) for s in steps])
        T = np.concatenate([_arr(s["temperature"]) for s in steps])
        o = np.argsort(t)
        t, I, V, T = t[o], I[o], V[o], T[o]
        bad = (T < -20) | (T > 90)          # sensor sentinel (e.g. -4094.1 C in RW3)
        if bad.all():
            T = np.full_like(T, np.nan)
        elif bad.any():
            T[bad] = np.interp(t[bad], t[~bad], T[~bad])
        if len(t) < 60:
            continue
        ah = np.r_[0.0, np.cumsum(0.5 * (I[1:] + I[:-1]) * np.diff(t))] / 3600.0
        # resample to dt
        grid = np.arange(t[0], t[-1], dt)
        f = lambda y: np.interp(grid, t, y)
        out.append(RWCycle(cell, n, float(t[0]), grid - grid[0], f(I), f(V), f(T), f(ah)))
    return out, np.array(refs)


def cycle_features(c: RWCycle) -> np.ndarray:
    """Hand-crafted per-cycle features for the data-driven baseline (no capacity label inside)."""
    q = c.ah[-1]
    e = np.trapezoid(c.V * c.I, c.t) / 3600.0
    v_at = lambda frac: np.interp(frac * q, c.ah, c.V)
    return np.array([q, e, c.V.mean(), c.I.mean(), c.I.std(), c.t[-1] / 3600.0, c.T.mean(), c.T.max(),
                     v_at(0.1), v_at(0.5), v_at(0.9)])


def label_cycles(cycles: list[RWCycle], refs: np.ndarray, k_after: int = 5):
    """Pairs (cycle indices, reference capacity): the k_after RW cycles that start right after each reference."""
    pairs = []
    starts = np.array([c.t0 for c in cycles])
    for tr, qr in refs:
        after = np.where(starts > tr)[0][:k_after]
        if len(after):
            pairs.append((after, qr, tr))
    return pairs


def all_cells(group: str):
    files = sorted(glob.glob(os.path.join(ROOT, GROUPS[group], "data", "Matlab", "RW*.mat")))
    return [os.path.basename(f)[:-4] for f in files]
