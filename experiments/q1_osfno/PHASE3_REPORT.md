# Phase 3: CNN vs FNO, hyper-parameters chosen by nested inner validation only

Grids and locks: `phase3.py`, `locks/phase3_<task>_<family>.json` (written before any outer evaluation). Macro-F1 pooled over the three held-out terciles, 5 seeds, Phase 1 partitions.

| task | family | macro-F1 (mean ± 95 % CI) | chosen config per fold (low, mid, high) |
|---|---|---|---|
| misalignment | cnn | 0.909 ± 0.016 | {'width': 16, 'blocks': 4}; {'width': 16, 'blocks': 4}; {'width': 32, 'blocks': 4} |
| misalignment | fno | 0.848 ± 0.022 | {'width': 32, 'modes': 64, 'layers': 3}; {'width': 64, 'modes': 64, 'layers': 3}; {'width': 32, 'modes': 128, 'layers': 3} |
| unbalance | cnn | 0.889 ± 0.051 | {'width': 16, 'blocks': 4}; {'width': 48, 'blocks': 5}; {'width': 16, 'blocks': 4} |
| unbalance | fno | 0.961 ± 0.028 | {'width': 32, 'modes': 64, 'layers': 3}; {'width': 64, 'modes': 64, 'layers': 3}; {'width': 32, 'modes': 64, 'layers': 3} |
| bearings | cnn | 0.904 ± 0.019 | {'width': 32, 'blocks': 4}; {'width': 32, 'blocks': 3}; {'width': 32, 'blocks': 3} |
| bearings | fno | 0.873 ± 0.016 | {'width': 32, 'modes': 64, 'layers': 3}; {'width': 64, 'modes': 64, 'layers': 3}; {'width': 64, 'modes': 64, 'layers': 3} |
| all | cnn | 0.913 ± 0.015 | {'width': 32, 'blocks': 3}; {'width': 32, 'blocks': 3}; {'width': 32, 'blocks': 3} |
| all | fno | 0.873 ± 0.012 | {'width': 64, 'modes': 64, 'layers': 3}; {'width': 64, 'modes': 64, 'layers': 3}; {'width': 64, 'modes': 64, 'layers': 3} |
| comfaulda7 | cnn | 0.769 ± 0.015 | {'width': 32, 'blocks': 3}; {'width': 48, 'blocks': 5}; {'width': 48, 'blocks': 5} |
| comfaulda7 | fno | 0.726 ± 0.022 | {'width': 64, 'modes': 64, 'layers': 3}; {'width': 32, 'modes': 128, 'layers': 3}; {'width': 64, 'modes': 64, 'layers': 3} |

| task | A | B | diff (seed mean ± 95 % CI) | seeds A>B | low | mid | high | McNemar p (Holm over all 15) |
|---|---|---|---|---|---|---|---|---|
| misalignment | cnn-tuned | fno-tuned (phase3) | +0.061 ± 0.032 | 5/5 | +0.108 | +0.023 | +0.056 | 0.03 (0.27) |
| unbalance | cnn-tuned | fno-tuned (phase3) | -0.072 ± 0.073 | 1/5 | -0.044 | -0.003 | -0.208 | 7.6e-05 (0.00092) |
| bearings | cnn-tuned | fno-tuned (phase3) | +0.032 ± 0.032 | 4/5 | -0.001 | +0.007 | +0.067 | 2.7e-07 (4.1e-06) |
| all | cnn-tuned | fno-tuned (phase3) | +0.040 ± 0.018 | 5/5 | +0.031 | +0.026 | +0.055 | 0.012 (0.13) |
| comfaulda7 | cnn-tuned | fno-tuned (phase3) | +0.043 ± 0.023 | 5/5 | -0.020 | +0.089 | +0.079 | 4.2e-05 (0.00054) |
| misalignment | cnn-tuned | cnn-spec (phase1) | -0.014 ± 0.016 | 0/5 | -0.036 | -0.006 | +0.000 | 0.79 (1) |
| unbalance | cnn-tuned | cnn-spec (phase1) | -0.009 ± 0.097 | 2/5 | -0.010 | -0.003 | -0.029 | 1 (1) |
| bearings | cnn-tuned | cnn-spec (phase1) | +0.001 ± 0.004 | 3/5 | +0.000 | -0.002 | +0.003 | 1 (1) |
| all | cnn-tuned | cnn-spec (phase1) | +0.013 ± 0.018 | 4/5 | +0.033 | -0.000 | +0.001 | 0.86 (1) |
| comfaulda7 | cnn-tuned | cnn-spec (phase1) | +0.015 ± 0.028 | 4/5 | +0.025 | +0.001 | +0.015 | 0.51 (1) |
| misalignment | fno-tuned | osfno-A-nospeed (phase1) | -0.007 ± 0.033 | 1/5 | +0.000 | +0.019 | -0.044 | 1 (1) |
| unbalance | fno-tuned | osfno-A-nospeed (phase1) | +0.000 ± 0.000 | 0/5 | +0.000 | +0.000 | +0.000 | 1 (1) |
| bearings | fno-tuned | osfno-A-nospeed (phase1) | +0.006 ± 0.010 | 4/5 | +0.000 | +0.009 | +0.011 | 0.82 (1) |
| all | fno-tuned | osfno-A-nospeed (phase1) | +0.023 ± 0.015 | 5/5 | +0.036 | +0.006 | +0.022 | 0.014 (0.14) |
| comfaulda7 | fno-tuned | osfno-A-nospeed (phase1) | +0.041 ± 0.028 | 5/5 | +0.028 | +0.047 | +0.051 | 1.2e-06 (1.7e-05) |
