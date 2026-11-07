# Final report: speed generalisation and measurement robustness of fault classifiers on MAFAULDA and COMFAULDA

Branch `exp/q1-audit-osfno` (fork cifer-sudo/PINNeAPPle). Every number below is read from a generated table
(`tables/`) or report (`PHASE*_REPORT.md`), themselves generated from the per-run result files in `results/`.
Nothing in the manuscript (`paper/speed_generalisation_mafaulda/`) has been modified (rule 10).

## 0. Verdict against the final criterion

> "An improvement is validated only if it is reproducible, leakage-free and better than strong baselines. If no
> architecture beats these baselines, keep the critical study as the main contribution."

- No neural-operator variant (OS-FNO A/B/C/E, DRO, SupCon, nested-tuned FNO) beats the strong baselines: they win only
  on T2 (unbalance), and lose or tie elsewhere (R3 fails).
- The only model that passes R3 is a **baseline**: the residual 1-D CNN on order spectra (+0.022 to +0.064 vs the best
  feature model on T1, T3, T4, C1; not worse on T2).
- Fusion (exploratory α = 0.5), the nested stacker, multi-band envelopes and measurement-robust training are **not
  retained** by their pre-registered rules.
- **The critical study is the main contribution**, strengthened by a new measurement-robustness result (Section 6).

## 1. Data (Phase 0, `AUDIT.md`, T11)

- MAFAULDA: 1951 runs, 0 read errors, 56 tachometer exclusions (40 period spread > 5 %, 16 also speed ratio), 1895 used;
  no duplicate file or spectrum. COMFAULDA: 2162 runs, 1 CRC error in the published archive → 2161; **two byte-identical
  pairs published under different speeds** and two repeated nominal speeds (to report to the dataset authors).
- Tasks: T1 misalignment (547 runs), T2 unbalance (382), T3 bearings (1064), T4 all ten states (1895), C1 COMFAULDA seven
  states (2161). Protocol Pb: hold out one speed tercile (low and high = extrapolation); the 5-s record is never split.
- Manuscript claims that the audit found unsupported are listed in `AUDIT.md` §B and §F (e.g. "all models > 0.97",
  "leakage-free", causal FiLM ablation on one seed, "superposition refuted").

## 2. Main benchmark (Phase 1; T01, T03, F01, F02, F07)

Macro-F1 pooled over held-out terciles, mean of 5 seeds:

| model | T1 | T2 | T3 | T4 | C1 |
|---|---|---|---|---|---|
| RF | 0.876 | 0.852 | 0.866 | 0.878 | 0.634 |
| MLP | 0.838 | 0.884 | 0.837 | 0.817 | 0.690 |
| CNN on order spectra | **0.924** | 0.898 | **0.904** | **0.900** | **0.754** |
| OS-FNO A (no speed) | 0.856 | **0.961** | 0.867 | 0.850 | 0.684 |
| OS-FNO B (speed in head) | 0.856 | 0.942 | 0.859 | 0.836 | 0.689 |
| OS-FNO C = OC-FNO (FiLM) | 0.765 | 0.934 | 0.816 | 0.761 | 0.592 |
| OS-FNO E (physical speed) | 0.861 | 0.955 | 0.854 | 0.841 | 0.696 |

(SVM, XGBoost, KAN, train-only FNO, DRO, SupCon and ablations: T01.)

Pre-registered decisions (PROTOCOL.md):
- **R1 (B vs C)**: speed in the head beats FiLM on T1 +0.091 ± 0.015, T3 +0.043 ± 0.033, T4 +0.075 ± 0.057,
  C1 +0.097 ± 0.049 (McNemar–Holm ≤ 0.043); T2 n.s. → **FiLM speed conditioning hurts extrapolation.**
- **R2 (A vs B, E vs A/B)**: all differences within ±0.02 with CIs covering 0 → **no speed representation is needed**;
  variant A (no speed) is the default.
- **R3 (vs best feature baseline)**: CNN +0.047 ± 0.025 (T1; record-level McNemar n.s.), +0.037 ± 0.007 (T3),
  +0.022 ± 0.009 (T4), +0.064 ± 0.020 (C1), +0.014 ± 0.059 (T2) → **pass**. OS-FNO A: +0.077 on T2 only, −0.028 on T4 →
  **fail**; idem E, DRO, SupCon.
- **R4 (worst tercile, F02)**: the low-speed tercile is the hardest for every model; feature models are best at low
  speed (T1 low: RF 0.85 vs CNN 0.81), spectral models at high speed (T1 high: RF 0.70 vs CNN 0.95).

## 3. Fair tuning (Phase 3; T04, PHASE3_REPORT.md)

Hyper-parameters chosen only by leave-one-speed-block-out inside the training terciles, locked before evaluation:
tuned CNN − tuned FNO = +0.061 (T1), −0.072 (T2), +0.032 (T3), +0.040 (T4), +0.043 (C1). Tuning helps the FNO on C1
(+0.041) and T4 (+0.023) but does not change the ranking; it does not help the CNN.

## 4. Fusion, generalisation methods, bearings (Phases 4–6)

- Nested multi-expert stacker (RF + MLP + CNN, gate chosen on inner OOF): vs CNN −0.040 (T1) to +0.011 (C1), never
  significant; the exploratory α = 0.5 RF+CNN gain is **not confirmed** by a nested selection (PHASE5_REPORT.md).
- GroupDRO and SupCon on OS-FNO B: no gain (T01/T03).
- Multi-band envelopes (pre-registered H6): RF −0.013 (T3), −0.010 (T4); CNN 0.000 (T3), +0.025 ± 0.010 (T4) →
  **H6 not supported** (requires both). Fisher ratios of defect orders are only 1.2–1.6× higher in the best band than
  in the broadband envelope (`results/phase6_diagnose.json`).

## 5. Compound faults (Phase 7; T06, T07, F08)

Trained on normal + single faults, tested on the 1143 compound COMFAULDA runs: exact match 0.014 (binary-relevance RF),
0.076 (BR-MLP), 0.019 (multi-label CNN), 0.088 (CNN + synthetic mixtures). Unbalance masks misalignment: most U+H and
U+V runs are predicted "unbalance only". Superposition Y_A + Y_B − Y_0 vs the real compound spectrum: median relative
error 0.85 (U+H), 0.90 (U+V), 1.25 (H+V), against same-class noise floors 0.61 (U), 0.92 (H), 0.85 (V). The journal's
"superposition refuted" is therefore supported only for the two-misalignment pair.

## 6. Measurement robustness and calibration (Phase 8, 5b; T05, T08, T09, F04–F06, F09)

Models trained exactly as in Phase 1; only the held-out runs are perturbed (`phase8_robust.py`; clean predictions
reproduce Phase 1 exactly).

- **Speed-estimate error.** Feature models tolerate ±1 % (their ±0.03-order windows) and break at ±2 %
  (T4 RF 0.878 → 0.70). The speed-aware OS-FNO variants are the most fragile (T4 0.84–0.85 → 0.50–0.53 at ±2 %,
  C1 → 0.12–0.16 at ±5 %). The CNN is almost insensitive on T1/T2 (0.924 → 0.904 at +5 %) but not on C1 (−1 %: 0.52).
- **Dead sensor.** Feature models and FNOs depend on one critical sensor (MAFAULDA overhang axial accelerometer for
  T1/T2/T4: RF 0.47–0.70 when it is lost; overhang radial / microphone for bearings). The CNN spreads its dependence
  over all sensors and loses 0.17–0.62 whichever sensor fails (T4 mean over sensors 0.48, C1 worst 0.13).
- **Robust training (pre-registered 5b)**: order-axis jitter ±2 % + sensor dropout raises the robustness score of the
  CNN from 0.749 to 0.884 (T3), 0.734 to 0.882 (T4), 0.400 to 0.774 (C1) and its clean C1 score to 0.791 (best C1
  result), but costs 0.094 clean macro-F1 on T1 → **not retained** by the rule; RF-rob likewise (cost on T1, T4).
  The trade-off is a result in itself and is reported as such (F06).
- **Calibration**: the CNN is the best-calibrated model on T3/T4/C1 (ECE 0.05–0.07); RF is strongly under-confident
  (ECE 0.19–0.27); OS-FNO under-confident (0.13–0.19).
- **Weakest class everywhere: `normal`** (T4 F1: RF 0.72, CNN 0.81, OS-FNO A 0.63) — at an unseen speed, a healthy
  machine's speed-dependent response is mistaken for a fault.

## 7. Physical interpretation (hypotheses consistent with the evidence, not separately proven)

1. The low-speed tercile is hardest because the 1X–4X amplitudes there are small relative to the background and the
   structure's response differs from the training speeds; hand-made amplitude ratios at known orders transfer better
   than learned spectral shapes (feature models win the low tercile).
2. Order normalisation makes harmonic lines speed-invariant only if the speed is exact; a global spectral filter
   (FNO modes on a 0.01-order grid) is sensitive to a uniform stretch of the order axis, whereas convolution + max
   pooling is locally shift-tolerant — consistent with the speed-error ranking (F04).
3. Unbalance and misalignment are mostly 1X/2X phenomena seen best by the axial accelerometer next to the overhung
   rotor; models that rely on hand-picked 1X–4X amplitudes inherit this single point of failure.
4. In compound runs the unbalance 1X line dominates; superposition holds to within the run-to-run variability for
   unbalance pairs, but the two misalignments interact (H+V error above the floor).

## 8. Failure and ablation log (all kept, rule 1)

FiLM (R1), speed inputs (R2), all OS-FNO variants vs baselines (R3), GroupDRO, SupCon, no-augmentation /
no-prior / common-gain ablations, train-only FNO, nested FNO tuning, RF+CNN fusion (exploratory), nested stacker,
multi-band envelopes (H6), robust training (5b), compositional models (Phase 7). Operational incidents: local container
too slow for Phase 6 CNN (moved to workers, `logs/local_phase6.log`); worker 2-h job limit (jobs split per seed; no
result changed). Deviations: none from the decision rules; fusion is labelled exploratory (PROTOCOL.md).

## 9. Reproducibility

`README.md` gives the commands. Each result JSON stores code commit, library versions, partition hash, per-split
metrics and every run's prediction and probabilities; `HISTORY.jsonl` is the append-only ledger of every result file
(SHA-256); `locks/` holds the Phase 3 selections written before evaluation; `tests/` (21 tests) checks the protocol
rules on the code and on the released results.

## 10. Next step that needs the authors

Approve the conclusions above; then the manuscript can be revised (claims of AUDIT.md §B/§F, new robustness section,
positioning of `POSITIONING.md`, target journal Measurement).
