# Prototype C5 — capacity from random-walk operation (NASA RW)

ID = leave-one-cell-out inside RW25-28 (40 C, skewed high), 4 folds; OOD = train on RW25-28, test on RW3-6
(room temperature, uniform 0.5-4 A, deeper ageing). Each reference capacity (1 A to 3.2 V) is predicted from the
5 RW cycles that follow it. coulomb/ridge: deterministic (one value per fold); mlp/necm: 3 seeds per fold.
Mean ± std over folds x seeds. The neural-ECM never sees a capacity label; only its scale calibration (a Q + b)
is fitted on the training cells.

| split | method | RMSE (Ah) | MAE (Ah) | max (Ah) | MAPE (%) | R2 | n refs per fold | voltage RMSE test (mV) |
|---|---|---|---|---|---|---|---|---|
| ID | Coulomb count to cut-off (calibrated) | 0.147 ± 0.042 | 0.135 ± 0.046 | 0.233 | 7.11 ± 2.29 | -1.068 | 12 | - |
| ID | DD ridge on cycle features | 0.154 ± 0.045 | 0.133 ± 0.041 | 0.273 | 7.08 ± 2.12 | -1.236 | 12 | - |
| ID | DD MLP on cycle features | 0.537 ± 0.176 | 0.418 ± 0.153 | 1.151 | 21.79 ± 7.81 | -26.745 | 12 | - |
| ID | neural-ECM (voltage only, label-free) + calibration | 0.118 ± 0.031 | 0.097 ± 0.016 | 0.253 | 5.14 ± 0.83 | -0.254 | 12 | 8.1 |
| OOD | Coulomb count to cut-off (calibrated) | 0.446 ± 0.000 | 0.418 ± 0.000 | 0.749 | 29.45 ± 0.00 | -2.471 | 146 | - |
| OOD | DD ridge on cycle features | 1.212 ± 0.000 | 1.082 ± 0.000 | 1.932 | 69.00 ± 0.00 | -24.611 | 146 | - |
| OOD | DD MLP on cycle features | 8.804 ± 1.177 | 8.414 ± 0.999 | 12.587 | 558.45 ± 59.72 | -1374.269 | 146 | - |
| OOD | neural-ECM (voltage only, label-free) + calibration | 0.552 ± 0.001 | 0.355 ± 0.002 | 2.714 | 25.68 ± 0.09 | -4.309 | 146 | 24.5 |
