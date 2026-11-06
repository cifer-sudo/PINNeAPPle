# Phase 6: band-limited envelope spectra for bearings (pre-registered H6)

`phase6.py`; decision rule in PROTOCOL.md (difference > 0 with CI above 0 on both T3 and T4). Fisher-ratio diagnosis: `results/phase6_diagnose.json`.

| task | A | B | A macro-F1 | diff (seed mean ± 95 % CI) | seeds A>B | low | mid | high | McNemar p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| bearings | rf-mb | rf | 0.853 ± 0.011 | -0.013 ± 0.020 | 1/5 | -0.041 | +0.001 | +0.005 | 0.2 (0.6) |
| all | rf-mb | rf | 0.869 ± 0.002 | -0.010 ± 0.003 | 0/5 | -0.032 | -0.001 | +0.002 | 0.24 (0.6) |
| bearings | cnn-mb | cnn-spec | 0.904 ± 0.022 | +0.000 ± 0.013 | 3/5 | +0.000 | +0.002 | +0.019 | 0.35 (0.6) |
| all | cnn-mb | cnn-spec | 0.925 ± 0.007 | +0.025 ± 0.010 | 5/5 | +0.076 | +0.000 | +0.012 | 0.00025 (0.00099) |

H6 for rf-mb: **NOT SUPPORTED** (pre-registered rule).

H6 for cnn-mb: **NOT SUPPORTED** (pre-registered rule).
