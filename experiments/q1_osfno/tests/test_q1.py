"""Tests of the Q1 study: protocol rules checked on the code AND on the published result files.
run: cd experiments/q1_osfno && Q1_SLIM=1 python -m pytest -q tests/"""
import glob
import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
os.environ.setdefault("Q1_SLIM", "1")

import q1lib as L  # noqa: E402
from stats_q1 import ci, holm  # noqa: E402

TASKS = {"misalignment": "mafaulda", "unbalance": "mafaulda", "bearings": "mafaulda", "all": "mafaulda",
         "comfaulda7": "comfaulda"}
EXPECTED_N = {"misalignment": 547, "unbalance": 382, "bearings": 1064, "all": 1895, "comfaulda7": 2161}


@pytest.fixture(scope="module")
def rows():
    return {ds: L.load_rows(ds) for ds in ("mafaulda", "comfaulda")}


@pytest.mark.parametrize("task", list(TASKS))
def test_population_and_outer_partition(rows, task):
    sel, y, paths, sp = L.task_data(rows[TASKS[task]], task)
    assert len(y) == EXPECTED_N[task]                                  # audit counts (1895 = 1951 - 56; 2161)
    splits = L.outer_splits(y, sp)
    te_all = np.concatenate([te for _, _, te in splits])
    assert sorted(te_all) == list(range(len(y)))                       # each run tested exactly once (rule 5)
    for name, tr, te in splits:
        assert not set(tr) & set(te)
        assert sp[te].min() > sp[tr].max() or sp[te].max() < sp[tr].min() or "mid" in name   # terciles are speed blocks
        if "mid" in name:
            lo, hi = sp[te].min(), sp[te].max()
            assert not np.any((sp[tr] >= lo) & (sp[tr] <= hi))         # no training run inside the held-out speeds


@pytest.mark.parametrize("task", list(TASKS))
def test_inner_splits_use_training_runs_only(rows, task):
    sel, y, paths, sp = L.task_data(rows[TASKS[task]], task)
    for _, tr, te in L.outer_splits(y, sp):
        tr = np.asarray(tr)
        blocks = L.inner_splits(sp[tr])
        va_all = np.concatenate([va for _, _, va in blocks])
        assert sorted(va_all) == list(range(len(tr)))                  # indices are relative to the outer training set
        for _, itr, iva in blocks:
            assert not set(itr) & set(iva)
            assert set(tr[iva]).isdisjoint(set(np.asarray(te)))        # rule 4: no test speed used for selection


@pytest.mark.parametrize("task", list(TASKS))
def test_every_result_file_uses_the_same_partitions(rows, task):
    sel, y, paths, sp = L.task_data(rows[TASKS[task]], task)
    h = L.partition_hash(paths, L.outer_splits(y, sp))
    files = [f for e in ("phase1", "phase3", "phase5", "phase6") for f in glob.glob(str(L.RESULTS / e / task / "*" / "speed_seed*.json"))]
    assert files
    for f in files:                                                    # rule 6
        assert json.load(open(f))["partition_hash"] == h, f
    for f in glob.glob(str(L.RESULTS / "phase8_robust" / task / "*" / "seed*.json")):
        assert json.load(open(f))["partition_hash"] == h, f


def test_every_model_has_five_seeds():
    for e in ("phase1", "phase3", "phase5", "phase6"):
        for d in glob.glob(str(L.RESULTS / e / "*" / "*")):
            if os.path.isdir(d):
                assert len(glob.glob(os.path.join(d, "speed_seed*.json"))) == 5, d     # rule 7


def test_phase3_locks_written_before_outer_evaluation():
    for f in glob.glob(str(L.RESULTS.parent / "locks" / "phase3_*.json")):
        lk = json.load(open(f))
        for r in glob.glob(str(L.RESULTS / "phase3" / lk["task"] / f"{lk['family']}-tuned" / "speed_seed*.json")):
            assert json.load(open(r))["provenance"]["utc_finished"] > lk["utc_end"]   # rule 8


def test_clean_perturbation_is_identity_and_speed_shift_moves_orders(rows):
    from phase8_robust import perturb
    r = rows["mafaulda"][0]
    assert perturb(r, "clean", None) is r
    S = np.zeros((1201, 1)); S[300, 0] = 1.0                          # a line at 3X
    q = perturb({**r, "order_spectrum": np.repeat(S, 7, 1), "envelope_spectrum": np.repeat(S, 7, 1)}, "speed", 0.02)
    k = int(np.argmax(q["order_spectrum"][:, 0]))
    assert abs(k * 0.01 - 3.0 / 1.02) < 0.011                          # true order k appears at k / (1 + e)
    assert np.isclose(q["speed_hz"], r["speed_hz"] * 1.02)


def test_order_jitter_matches_definition():
    import torch
    from models3 import _order_jitter
    x = torch.as_tensor(np.tile(np.arange(801, dtype=np.float32) * 0.01, (2, 3, 1)))
    y = _order_jitter(x, np.array([0.02, 0.0]))
    assert abs(float(y[0, 0, 100]) - 1.02) < 1e-5 and abs(float(y[1, 0, 100]) - 1.0) < 1e-6


def test_statistics_helpers():
    assert ci([0.5] * 5)[1] == 0.0
    p = [0.01, 0.04, 0.03, 0.5]
    a = holm(p)
    assert all(ai >= pi for ai, pi in zip(a, p)) and max(a) <= 1.0
    assert np.isclose(a[0], 0.04)                                      # smallest p x 4


def test_tables_are_generated_from_results():
    import csv
    rows = list(csv.DictReader(open(L.RESULTS.parent / "tables" / "T01_main_macro_f1.csv")))
    r = next(x for x in rows if x["task"] == "T4" and x["model"] == "cnn-spec")
    f = [json.load(open(p))["pooled"]["macro_f1"] for p in sorted(glob.glob(str(L.RESULTS / "phase1" / "all" / "cnn-spec" / "speed_seed*.json")))]
    assert r["macro_f1 mean ± 95% CI"].startswith(f"{np.mean(f):.3f}")                 # rule 3
