"""Unit tests for the NASA RW prototype: data pairing and ECM physics (pytest -q)."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data import GROUPS, ROOT, RWCycle, label_cycles, load_cell  # noqa: E402
from models import DT, TAU, ecm_voltage, rc_input  # noqa: E402


def test_rc_input_matches_explicit_recursion():
    rng = np.random.default_rng(0)
    I = rng.uniform(0.5, 5, 300)
    a = np.exp(-DT / TAU)
    v = np.zeros_like(I)
    for n in range(len(I) - 1):
        v[n + 1] = a * v[n] + (1 - a) * I[n]
    assert np.allclose(rc_input(I), v, atol=1e-12)


def test_ecm_residual_zero_on_synthetic_cycle():
    rng = np.random.default_rng(1)
    I = np.repeat(rng.uniform(0.5, 5, 30), 6)
    ah = np.r_[0, np.cumsum(I[:-1]) * DT / 3600]
    ocv = lambda z: 3.2 + 1.0 * z - 0.1 * (1 - z) ** 3
    Q, R0, R1 = 2.0, 0.07, 0.03
    u = rc_input(I)
    V = ocv(1 - ah / Q) - R0 * I - R1 * u
    assert np.max(np.abs(ecm_voltage(ocv, ah, I, u, Q, R0, R1) - V)) < 1e-12
    assert np.max(np.abs(ecm_voltage(ocv, ah, I, u, 1.8, R0, R1) - V)) > 1e-3   # wrong capacity is visible


def test_label_pairing_takes_cycles_after_reference():
    cy = [RWCycle("X", i, float(t0), np.arange(3.0), np.ones(3), np.ones(3), np.ones(3), np.zeros(3)) for i, t0 in enumerate([0, 10, 20, 30, 40, 50])]
    pairs = label_cycles(cy, np.array([[25.0, 2.0]]), k_after=2)
    assert list(pairs[0][0]) == [3, 4] and pairs[0][1] == 2.0


@pytest.mark.skipif(not os.path.exists(os.path.join(ROOT, GROUPS["high40"], "data", "Matlab", "RW25.mat")), reason="real data absent")
def test_real_file_structure():
    cy, refs = load_cell("high40", "RW25")
    assert len(refs) == 13 and 1.5 < refs[0, 1] < 2.3
    v0 = np.array([c.V[0] for c in cy])
    assert np.median(v0) > 4.15                     # every RW cycle starts after a full charge
    assert all(np.all(np.diff(c.ah) >= -1e-9) for c in cy[:50])
    assert all(np.isfinite(c.T).all() for c in cy[:50])
