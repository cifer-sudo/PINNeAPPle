"""Unit tests: data pipeline and physics residual (run: pytest -q from the prototype folder)."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data import DT, NPZ_DIR, Series, clean_core, load_cell, resample_block, windows  # noqa: E402
from models import fit_biot, lumped_residual, simulate_lumped, simulate_lumped_loop  # noqa: E402


def synthetic(n=2000, cc=55.0, rc=1.8, r0=0.028, seed=0):
    rng = np.random.default_rng(seed)
    I = np.repeat(rng.choice([0.0, -5.0, 1.7], size=n // 50), 50)[:n]
    ts = 25 + np.cumsum(rng.normal(0, 0.01, n)) + 0.002 * np.arange(n) * (I != 0)
    s = Series("SYN", 0, np.arange(n) * DT, I, I ** 2, np.full(n, 3.7), ts, np.full(n, np.nan), 25.0)
    s.Tc = simulate_lumped_loop(s, cc, rc, r0)
    return s, (cc, rc, r0)


def test_residual_zero_on_exact_solution():
    s, (cc, rc, r0) = synthetic()
    r = lumped_residual(s.Tc[:-1], s.Tc[1:], s.Ts[:-1], s.I2[:-1], cc, rc, r0)
    assert np.max(np.abs(r)) < 1e-9


def test_residual_detects_wrong_parameters():
    s, (cc, rc, r0) = synthetic()
    r = lumped_residual(s.Tc[:-1], s.Tc[1:], s.Ts[:-1], s.I2[:-1], cc, rc * 1.5, r0)
    assert np.sqrt(np.mean(r ** 2)) > 1e-3


def test_fast_simulation_matches_loop():
    s, (cc, rc, r0) = synthetic()
    assert np.allclose(simulate_lumped(s, cc, rc, r0), s.Tc, atol=1e-9)


def test_biot_recovers_gain():
    s, _ = synthetic()
    s.Tc = s.Ts + 0.3 * (s.Ts - s.Tamb)
    assert abs(fit_biot([s]) - 0.3) < 1e-9


def test_clean_core_masks_sentinel():
    x = clean_core(np.array([25.0, -3276.8, 30.0, 150.0]))
    assert np.isnan(x[1]) and np.isnan(x[3]) and x[0] == 25.0


def test_resample_keeps_joule_heat():
    t = np.arange(0, 20.0, 1.0)
    I = np.r_[np.full(10, 5.0), np.full(10, -5.0)]
    r = resample_block(t, {"I": I, "I2": I ** 2, "V": np.ones(20)}, dt=20.0)
    assert r["I"][0] == pytest.approx(0.0) and r["I2"][0] == pytest.approx(25.0)


def test_windows_alignment():
    s, _ = synthetic(n=200)
    w = windows(s, w=10)
    k = w["k"]
    assert np.allclose(w["Ts"], s.Ts[k]) and np.allclose(w["Ts1"], s.Ts[k + 1])
    assert w["X"].shape == (len(k), 10 * 5)


@pytest.mark.skipif(not os.path.exists(os.path.join(NPZ_DIR, "short_VP010.npz")), reason="real data not present")
def test_real_file_structure():
    ss = load_cell("VP010")
    assert len(ss) == 5
    for s in ss:
        assert np.nanmedian(np.diff(s.t)) == DT
        assert np.isfinite(s.Tc).mean() > 0.99
        assert 20 < s.Tamb < 30
        assert np.nanmax(s.Tc - s.Ts) < 10 and np.nanmin(s.Tc - s.Ts) > -3
