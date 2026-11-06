# Phase 4/5: multi-expert fusion, gate selected on inner validation only

`phase5.py`: experts rf, mlp, cnn-spec; gate (convex 0.25 grid, logistic stacker, speed-aware stacker) chosen per outer fold by inner leave-one-speed-block-out OOF macro-F1. `fuse-rf+cnn-spec` = the exploratory fixed α = 0.5 fusion.

| task | A | B | A macro-F1 | diff (seed mean ± 95 % CI) | seeds A>B | low | mid | high | McNemar p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| misalignment | stack-rf-mlp-cnn | cnn-spec | 0.884 ± 0.027 | -0.040 ± 0.017 | 0/5 | +0.000 | +0.000 | -0.143 | 1 (1) |
| unbalance | stack-rf-mlp-cnn | cnn-spec | 0.880 ± 0.029 | -0.017 ± 0.035 | 1/5 | +0.000 | +0.000 | -0.067 | 0.5 (1) |
| bearings | stack-rf-mlp-cnn | cnn-spec | 0.914 ± 0.006 | +0.010 ± 0.013 | 5/5 | +0.033 | +0.000 | -0.000 | 0.8 (1) |
| all | stack-rf-mlp-cnn | cnn-spec | 0.899 ± 0.005 | -0.001 ± 0.009 | 3/5 | +0.026 | +0.000 | -0.036 | 0.46 (1) |
| comfaulda7 | stack-rf-mlp-cnn | cnn-spec | 0.765 ± 0.019 | +0.011 ± 0.028 | 4/5 | +0.048 | +0.011 | -0.032 | 0.82 (1) |
| misalignment | stack-rf-mlp-cnn | rf | 0.884 ± 0.027 | +0.008 ± 0.030 | 3/5 | -0.037 | +0.000 | +0.104 | 0.5 (1) |
| unbalance | stack-rf-mlp-cnn | rf | 0.880 ± 0.029 | +0.028 ± 0.034 | 5/5 | +0.032 | +0.000 | +0.074 | 0.11 (1) |
| bearings | stack-rf-mlp-cnn | rf | 0.914 ± 0.006 | +0.047 ± 0.007 | 5/5 | +0.026 | +0.000 | +0.125 | 4e-08 (5.6e-07) |
| all | stack-rf-mlp-cnn | rf | 0.899 ± 0.005 | +0.021 ± 0.004 | 5/5 | +0.007 | +0.002 | +0.052 | 2.5e-07 (3.3e-06) |
| comfaulda7 | stack-rf-mlp-cnn | rf | 0.765 ± 0.019 | +0.131 ± 0.026 | 5/5 | +0.055 | +0.191 | +0.164 | 6.5e-70 (9.8e-69) |
| misalignment | stack-rf-mlp-cnn | fuse-rf+cnn-spec | 0.884 ± 0.027 | -0.048 ± 0.021 | 0/5 | -0.021 | +0.000 | -0.146 | 0.3 (1) |
| unbalance | stack-rf-mlp-cnn | fuse-rf+cnn-spec | 0.880 ± 0.029 | -0.001 ± 0.024 | 2/5 | -0.022 | +0.000 | +0.035 | 1 (1) |
| bearings | stack-rf-mlp-cnn | fuse-rf+cnn-spec | 0.914 ± 0.006 | -0.000 ± 0.006 | 2/5 | +0.017 | +0.000 | -0.012 | 0.42 (1) |
| all | stack-rf-mlp-cnn | fuse-rf+cnn-spec | 0.899 ± 0.005 | -0.007 ± 0.013 | 2/5 | +0.003 | -0.000 | -0.026 | 0.13 (1) |
| comfaulda7 | stack-rf-mlp-cnn | fuse-rf+cnn-spec | 0.765 ± 0.019 | -0.000 ± 0.028 | 3/5 | +0.026 | +0.003 | -0.036 | 0.68 (1) |

Chosen gates (15 folds x seeds per task):

- misalignment: convex(0.0, 0.0, 1.0) x5, convex(0.0, 0.5, 0.5) x3, stacker x3, convex(0.75, 0.0, 0.25) x2, convex(0.5, 0.25, 0.25) x1, convex(0.25, 0.25, 0.5) x1
- unbalance: convex(0.0, 0.0, 1.0) x4, stacker-speed x2, convex(0.0, 0.75, 0.25) x2, convex(0.0, 0.5, 0.5) x2, convex(0.0, 0.25, 0.75) x1, convex(0.5, 0.0, 0.5) x1, convex(0.75, 0.0, 0.25) x1, convex(0.25, 0.25, 0.5) x1, convex(0.25, 0.0, 0.75) x1
- bearings: convex(0.75, 0.0, 0.25) x7, convex(0.5, 0.0, 0.5) x3, convex(0.0, 0.25, 0.75) x2, convex(0.25, 0.25, 0.5) x2, convex(0.5, 0.25, 0.25) x1
- all: convex(0.75, 0.0, 0.25) x4, convex(0.5, 0.25, 0.25) x4, convex(0.25, 0.25, 0.5) x3, convex(0.5, 0.0, 0.5) x3, convex(0.0, 0.25, 0.75) x1
- comfaulda7: convex(0.25, 0.25, 0.5) x8, convex(0.0, 0.25, 0.75) x5, convex(0.5, 0.25, 0.25) x2
