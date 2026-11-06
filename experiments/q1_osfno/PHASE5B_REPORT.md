# Phase 5b: measurement-robust training (pre-registered decision)

(a) clean macro-F1 difference vs the Phase 1 parent; (b) robustness score = mean macro-F1 over the six speed-error conditions (±1/2/5 %) and the dead-sensor mean; paired by seed, mean ± 95 % t-interval. ±5 % and gain ×2 are outside the training perturbations (reported only).

| task | model | parent | (a) clean diff | (b) robustness diff | speed-only diff | dead-sensor diff | ±5 % diff | gain ×2 diff | robust score model / parent |
|---|---|---|---|---|---|---|---|---|---|
| misalignment | cnn-spec-rob | cnn-spec | -0.094 ± 0.043 | -0.027 ± 0.036 | -0.074 ± 0.032 | +0.255 ± 0.078 | -0.075 ± 0.047 | -0.045 ± 0.042 | 0.846 / 0.872 |
| unbalance | cnn-spec-rob | cnn-spec | -0.050 ± 0.062 | +0.008 ± 0.089 | -0.012 ± 0.105 | +0.131 ± 0.046 | -0.006 ± 0.111 | -0.058 ± 0.064 | 0.860 / 0.852 |
| bearings | cnn-spec-rob | cnn-spec | -0.022 ± 0.028 | +0.134 ± 0.126 | +0.105 ± 0.143 | +0.311 ± 0.033 | +0.142 ± 0.183 | -0.004 ± 0.017 | 0.884 / 0.749 |
| all | cnn-spec-rob | cnn-spec | -0.019 ± 0.021 | +0.148 ± 0.065 | +0.109 ± 0.076 | +0.383 ± 0.017 | +0.138 ± 0.091 | -0.001 ± 0.023 | 0.882 / 0.734 |
| comfaulda7 | cnn-spec-rob | cnn-spec | +0.037 ± 0.028 | +0.373 ± 0.030 | +0.355 ± 0.037 | +0.486 ± 0.054 | +0.422 ± 0.022 | +0.112 ± 0.010 | 0.774 / 0.400 |
| **cnn-spec-rob** | decision | | clean CI entirely < 0 on 1 task(s) | robustness CI > 0 on 3/5 | | | | | **NOT RETAINED** |
| misalignment | rf-rob | rf | -0.033 ± 0.017 | +0.021 ± 0.025 | +0.024 ± 0.028 | +0.005 ± 0.019 | +0.139 ± 0.073 | -0.074 ± 0.007 | 0.771 / 0.750 |
| unbalance | rf-rob | rf | +0.025 ± 0.007 | +0.112 ± 0.015 | +0.119 ± 0.017 | +0.068 ± 0.015 | +0.213 ± 0.040 | +0.024 ± 0.007 | 0.873 / 0.761 |
| bearings | rf-rob | rf | -0.009 ± 0.013 | +0.143 ± 0.018 | +0.157 ± 0.019 | +0.062 ± 0.012 | +0.281 ± 0.033 | -0.029 ± 0.011 | 0.838 / 0.695 |
| all | rf-rob | rf | -0.027 ± 0.010 | +0.136 ± 0.008 | +0.146 ± 0.010 | +0.076 ± 0.008 | +0.306 ± 0.010 | -0.046 ± 0.009 | 0.827 / 0.691 |
| comfaulda7 | rf-rob | rf | -0.002 ± 0.012 | +0.082 ± 0.013 | +0.092 ± 0.015 | +0.026 ± 0.005 | +0.150 ± 0.034 | -0.012 ± 0.009 | 0.580 / 0.498 |
| **rf-rob** | decision | | clean CI entirely < 0 on 2 task(s) | robustness CI > 0 on 4/5 | | | | | **NOT RETAINED** |
