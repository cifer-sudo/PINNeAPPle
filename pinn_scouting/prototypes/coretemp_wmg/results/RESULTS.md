# Prototype C1 — core temperature (WMG LG M50, embedded thermocouples)

Leave-one-instrumented-cell-out (3 folds: VP010, VP011, VP012). DD and PINN: 3 seeds per fold (n = 9); B1, B2
deterministic (n = 3). Mean ± std over folds (and seeds). Errors on core temperature in kelvin; 'peak' = samples
with the 10 % largest true core-surface gradient; residual = RMS of the one-state model residual (W) under the
parameters fitted on the training cells. Hyper-parameters fixed before looking at test cells (lambda = 1, 6 epochs,
window 5 min, MLP 64x64 tanh). Non-instrumented cells VP016-018 enter only the PINN residual.

| scenario | method | RMSE (K) | MAE (K) | max (K) | RMSE peak (K) | R2 | residual (W) | n |
|---|---|---|---|---|---|---|---|---|
| full | B1 Biot quasi-steady | 0.360 ± 0.094 | 0.229 ± 0.077 | 2.13 ± 0.58 | 0.781 ± 0.349 | 0.983 | 0.369 | 3 |
| full | B2 lumped 1-state | 0.402 ± 0.048 | 0.242 ± 0.031 | 3.03 ± 0.54 | 0.930 ± 0.263 | 0.980 | 0.272 | 3 |
| full | DD windowed MLP | 0.260 ± 0.044 | 0.186 ± 0.032 | 1.38 ± 0.41 | 0.573 ± 0.141 | 0.992 | 0.224 | 9 |
| full | PINN (MLP + residual, lambda=1) | 0.391 ± 0.063 | 0.236 ± 0.040 | 3.04 ± 0.60 | 0.947 ± 0.305 | 0.981 | 0.038 | 9 |
| scarce | B1 Biot quasi-steady | 0.375 ± 0.081 | 0.237 ± 0.063 | 2.10 ± 0.54 | 0.808 ± 0.339 | 0.982 | 0.368 | 3 |
| scarce | B2 lumped 1-state | 0.409 ± 0.057 | 0.246 ± 0.033 | 3.12 ± 0.51 | 1.019 ± 0.274 | 0.980 | 0.263 | 3 |
| scarce | DD windowed MLP | 0.310 ± 0.066 | 0.210 ± 0.046 | 1.67 ± 0.57 | 0.718 ± 0.237 | 0.988 | 0.320 | 9 |
| scarce | PINN (MLP + residual, lambda=1) | 0.413 ± 0.084 | 0.251 ± 0.053 | 3.10 ± 0.55 | 1.084 ± 0.308 | 0.979 | 0.083 | 9 |

**Post-hoc sensitivity (NOT a pre-registered result; lambda chosen after seeing lambda = 1 fail):**

| scenario | lambda | PINN RMSE (K) | PINN RMSE peak (K) | residual (W) |
|---|---|---|---|---|
| full | 0.1 | 0.313 ± 0.068 | 0.727 ± 0.274 | 0.062 |
| scarce | 0.1 | 0.344 ± 0.074 | 0.821 ± 0.322 | 0.090 |
| full | 0.01 | 0.274 ± 0.054 | 0.633 ± 0.192 | 0.125 |
| scarce | 0.01 | 0.285 ± 0.076 | 0.650 ± 0.265 | 0.142 |
