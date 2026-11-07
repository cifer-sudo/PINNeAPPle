# Phase 9: positioning, novelty and journal recommendation

All references below were checked on Crossref (DOI, title, venue, year) on 2026-11-04/07; see `LITERATURE.md` for the
full list and the items that remain unverified (they are not cited). A literature search can only show that a claim
was **not found**, never that it is absent from the literature; every novelty statement below is worded accordingly.

## 1. What already exists (and therefore cannot be claimed)

| Topic | Verified prior work | Consequence |
|---|---|---|
| Over-optimistic random splits; realistic evaluation | Vieira et al., MSSP 2026, 10.1016/j.ymssp.2026.114640 | "first to show split optimism" cannot be claimed |
| Domain generalisation under unseen working conditions / variable speed | TIM 2020 10.1109/tim.2020.2992829; TIM 2021 10.1109/tim.2021.3088489; RESS 2024 10.1016/j.ress.2024.110449; survey AEI 2025 10.1016/j.aei.2024.103063 | DG baselines (DRO, contrastive) are expected; we include them as baselines |
| Speed-conditioned networks | Speed adaptive gate, Measurement 2023, 10.1016/j.measurement.2023.113016 | speed conditioning / FiLM is not new |
| Frequency-domain / FNO-type encoders for cross-domain diagnosis | Gao et al., IEEE IoT J 2025, 10.1109/JIOT.2025.3565810 | no "first FNO for fault diagnosis" claim |
| Order tracking + CNN under variable speed | Ji et al., Sensors 2021, 10.3390/s21030675; review Liu et al., IEEE Sensors J 2023, 10.1109/jsen.2023.3326112 | the CNN-on-order-spectra baseline is standard; it is our baseline, not a contribution |
| Tacholess speed estimation (source of speed errors) | Lu et al., IEEE TIM 2019, 10.1109/tim.2019.2902806 | motivates the speed-error robustness test; their review evaluates speed estimation and order tracking, not the sensitivity of trained classifiers |
| Order-frequency normalisation + cross-dataset benchmark | Jeong et al., Sensors 2025, 10.3390/s25144383 | cross-domain benchmarks on public rotary datasets exist |

## 2. Novelty table (evidence from this study)

| Aspect | Closest prior work | This study | Evidence |
|---|---|---|---|
| Speed-extrapolation benchmark on MAFAULDA **and** COMFAULDA, with released per-run predictions, partitions, seeds and locks | Vieira 2026 (bearings, other datasets, other split types) | 26 models/variants × 5 tasks × 5 seeds, identical partitions, paired tests | T01, T03, F01, F02 |
| Speed conditioning can **hurt** speed extrapolation | Speed adaptive gate (2023) reports gains under its own protocol | FiLM worse than speed-in-head on 4/5 tasks (CI > 0); no speed input as good as any speed input (R2) | T03 R1/R2, F07 |
| Neural-operator claim tested against strong baselines with nested tuning | — (not found) | tuned CNN > tuned FNO on 4/5 tasks; FNO wins only unbalance (T2) | T03 Phase 3, T04 |
| **Test-time measurement robustness re-ranks the models** (speed-estimate error ±1–5 %, dead sensor, gain drift) | not found for these datasets/model families in our search | speed-aware FNOs collapse at ±2 % (T4 0.85 → 0.50, C1 → 0.15 at ±5 %); the CNN is speed-robust on MAFAULDA but loses up to 0.6 with one dead sensor; feature models depend on one critical sensor (overhang axial) | T08, F04, F05 |
| Measurement-robust training with a pre-registered decision | augmentation is common; pre-registered evaluation with a clean-accuracy constraint not found | robustness +0.13 to +0.37 (T3, T4, C1, CI > 0) but clean cost on T1 → **not retained** by the rule written in advance | T05, F06 |
| Compound faults from single faults + superposition test against a noise floor | multi-label DG (PHM-AP 2023, not read; not cited) | all methods fail (exact ≤ 0.09); superposition deviation within the run-to-run floor for unbalance pairs, above it for H+V | T06, T07, F08 |
| Data-quality findings on COMFAULDA | — | 2 byte-identical file pairs under different speeds, 1 CRC error, 2 repeated nominal speeds | AUDIT.md, T11 |

## 3. Contributions that survive (to be used in the revised manuscript)

1. A leakage-controlled, fully released speed-extrapolation benchmark on two public rotor datasets
   (recording-disjoint and speed-group-disjoint; identical partitions; 5 seeds; per-run predictions; locks).
2. Negative result with mechanism: neural operators with speed conditioning do not beat a residual CNN on order
   spectra, and FiLM speed conditioning degrades extrapolation; nested tuning does not change the ranking.
3. A measurement-robustness evaluation showing that ranking by clean accuracy is misleading: the most accurate model
   is the least tolerant to a failed accelerometer; the speed-aware operators are the least tolerant to speed errors.
4. A documented remedy (order-axis jitter + sensor dropout) with its cost, reported against a pre-registered rule.
5. Compositional-generalisation failure on COMFAULDA, with a superposition analysis measured against the intra-class
   noise floor, and data-quality corrections to the public COMFAULDA archive.

Not claimed: any FNO superiority; the RF + CNN fusion (exploratory, and not confirmed by the nested stacker); the
multi-band envelope gain (H6 not supported).

## 4. Journal recommendation

| Venue | Fit | Risk |
|---|---|---|
| **Measurement (Elsevier)** — recommended | benchmark + measurement-error robustness (speed estimation, sensor failure) is exactly a measurement-science contribution; published the speed-adaptive-gate paper we contradict | needs the robustness section in the main text, not an appendix |
| IEEE Transactions on Instrumentation and Measurement | same fit (tacholess speed estimation literature is in TIM) | stricter length; strong preference for a method |
| Mechanical Systems and Signal Processing | Vieira 2026 shows MSSP accepts evaluation papers | MSSP reviewers will expect a new method that beats baselines — we do not have one |
| Reliability Engineering & System Safety | robustness/deployment angle | less natural for a classifier benchmark |

Recommendation: submit as a **critical benchmark / measurement-robustness study to Measurement**, with TIM as the
alternative. Do not submit as a new-method paper to MSSP unless a future method passes R3 (beats all baselines
with CI > 0 on ≥ 3/5 tasks and is not worse on any) and the robustness constraint.
