# Phase 7: COMFAULDA compound faults recognised from single-fault training

Train = normal + single-fault runs (all speeds); test = the 1143 combined runs. 5 seeds. `phase7.py`.

| method | exact match (mean ± sd) | Hamming | F1 unbalance | F1 horizontal | F1 vertical | exact U+H | exact U+V | exact H+V |
|---|---|---|---|---|---|---|---|---|
| br-rf (5) | 0.014 ± 0.003 | 0.402 | 0.86 | 0.37 | 0.42 | 0.00 | 0.01 | 0.03 |
| br-mlp (5) | 0.076 ± 0.022 | 0.383 | 0.80 | 0.49 | 0.52 | 0.02 | 0.03 | 0.16 |
| ml-cnn (5) | 0.019 ± 0.007 | 0.422 | 0.81 | 0.28 | 0.57 | 0.01 | 0.01 | 0.04 |
| ml-cnn-mix (5) | 0.088 ± 0.019 | 0.401 | 0.88 | 0.37 | 0.53 | 0.04 | 0.08 | 0.13 |

Superposition test (median relative error over 0-8X, `superposition.json`): unbalance+horizontal 0.85, unbalance+vertical 0.90, horizontal+vertical 1.25; same-class noise floor: unbalance 0.61, horizontal 0.92, vertical 0.85.
