# Q1 study: speed generalisation and measurement robustness of rotor-fault classifiers (MAFAULDA, COMFAULDA)

Experimental branch `exp/q1-audit-osfno` of the PINNeAPPle fork. The manuscript in
`paper/speed_generalisation_mafaulda/` is **not modified** (it will be revised only after the authors validate the
conclusions). Start with **`FINAL_REPORT.md`** (results and verdict), then `POSITIONING.md` (novelty, journal).

**Headline.** No neural-operator variant beats strong baselines under speed extrapolation; the residual 1-D CNN on
order spectra is the only model that passes the pre-registered rule; FiLM speed conditioning hurts; speed inputs are
unnecessary. A new measurement-robustness evaluation re-ranks the models (speed-aware FNOs collapse with a 2 % speed
error; the most accurate CNN collapses with one dead sensor), and robust training trades clean accuracy for large
robustness gains (not retained by the rule written in advance). Compound faults are not recognised from single faults.

## Contents

| What | Where |
|---|---|
| Final report, verdict, physical analysis, failure log | `FINAL_REPORT.md` |
| Positioning, verified novelty table, journal recommendation | `POSITIONING.md`, `LITERATURE.md` |
| Phase 0 audit (data counts, duplicates, manuscript claims) | `AUDIT.md`, `results/audit_data.json`, `results/data_manifest_*.json` |
| Locked protocol, decision rules, pre-registrations (Phases 5b, 6, 8), deviations | `PROTOCOL.md` |
| Per-phase reports (generated) | `PHASE1_REPORT.md`, `PHASE3_REPORT.md`, `PHASE5_REPORT.md`, `PHASE5B_REPORT.md`, `PHASE6_REPORT.md`, `PHASE7_REPORT.md`, `PHASE8_CALIBRATION.md`, `PHASE8_ROBUSTNESS.md` |
| Tables T01–T11 (CSV + LaTeX, generated) | `tables/` (`make_tables.py`) |
| Figures F01–F10 (PDF + PNG) and the plotted numbers | `figures/`, `figures/data/` (`make_figures.py`) |
| Every result: per-run predictions and probabilities, partitions, config, provenance | `results/<phase>/<task>/<model>/speed_seed<k>.json`; Phase 7 `results/phase7/`; Phase 8 `results/phase8_robust/` |
| Nested-selection locks (written before evaluation) | `locks/phase3_<task>_<family>.json` |
| History: append-only ledger (file, SHA-256, metrics, commit) and summary | `HISTORY.jsonl`, `SUMMARY.md` |
| Logs (extraction, local runs, all 39 remote shards) | `logs/`, `logs/shards/` |
| Environment | `env/environment.txt`, `env/pip_freeze.txt` |
| Tests (protocol rules checked on code and results) | `tests/test_q1.py` |
| Compact data (spectra 0–8X, features, band envelopes; verified identical inputs) | `data_slim/` |

### Tables
T01 macro-F1 of every model × task (mean ± 95 % CI, per tercile, worst) · T02 balanced accuracy · T03 all paired
comparisons (seed diff, bands, bootstrap, McNemar, Holm) · T04 Phase 3 locks · T05 robust-training decision ·
T06 compound faults · T07 superposition vs noise floor · T08 robustness to speed error / dead sensor / gain ·
T09 calibration and cost · T10 per-class F1 · T11 data audit.

### Figures
F01 main benchmark · F02 per-tercile heatmap · F03 accuracy vs speed · F04 speed-error robustness · F05 dead sensor ·
F06 clean vs robustness trade-off · F07 paired differences (forest) · F08 compound faults and superposition ·
F09 reliability diagrams · F10 confusion matrices (T4).

## Models (code)

| Name | File | Description |
|---|---|---|
| rf, mlp, svm, xgb, kan | `models.py` | features of the repository (`classify.feature_matrix`: RMS, kurtosis, skewness, crest, peak, 1X–4X, FTF/BSF/BPFO/BPFI envelope amplitudes, speed) |
| osfno-A/B/C/E (+ -noaug, -noprior, -commonaug), fno-trainonly | `models.py` | order-spectrum FNO; speed: none / head / FiLM / physical descriptor |
| cnn-spec, cnn-angle, osfno-B-dro, osfno-B-supcon | `models2.py` | residual 1-D CNN on order spectra; GroupDRO; supervised contrastive |
| cnn-spec-rob, rf-rob | `models3.py` | measurement-robust training (order jitter ±2 %, sensor dropout) |
| cnn-tuned, fno-tuned | `phase3.py` | nested hyper-parameter selection (grids in the file) |
| stack-rf-mlp-cnn | `phase5.py` | multi-expert fusion, gate chosen on inner OOF predictions |
| rf-mb, cnn-mb | `phase6.py` | band-limited envelope spectra (4 carrier bands) |
| br-rf, br-mlp, ml-cnn, ml-cnn-mix | `phase7.py` | compound faults from single faults |
| fuse-* | `fusion.py` | exploratory fixed fusion α = 0.5 |

Shared code: `q1lib.py` (data loading, partitions, inner splits, runner, provenance), `stats_q1.py` (paired statistics).

## Reproduce

```bash
python3 -m venv venv && venv/bin/pip install numpy scipy scikit-learn xgboost torch matplotlib pytest
```

```bash
cd experiments/q1_osfno && export Q1_SLIM=1
```

1. **Data** (optional: the slim caches in `data_slim/` are committed and give identical inputs). Full extraction from the
   public archives: `python extract_mafaulda.py`, `python extract_comfaulda.py` (MAFAULDA
   https://www02.smt.ufrj.br/~offshore/mfs/database/mafaulda/full.zip, COMFAULDA Zenodo record 8208454), then
   `python audit_data.py`, `python make_slim.py`, `python make_envbands_slim.py`, `python history.py manifest mafaulda`.
2. **Phase 1** (one job per model × task, 5 seeds): `python jobqueue.py <queue>` (queues listed in the file) or
   `python run_phase1.py`; fusion `python fusion.py`.
3. **Phase 3**: `python phase3.py select <dataset> <task> <cnn|fno>` then `python phase3.py confirm ...`.
4. **Phase 4/5**: `python phase5.py <dataset> <task> [seeds]`; **5b**: `python phase5b.py <dataset> <task> <rf-rob|cnn-spec-rob> [seeds]`.
5. **Phase 6**: `python phase6.py diagnose`; `python phase6.py run <bearings|all> <rf-mb|cnn-mb> [seeds]`.
6. **Phase 7**: `python phase7.py superposition`; `python phase7.py run <br-rf|br-mlp|ml-cnn|ml-cnn-mix>`.
7. **Phase 8**: `python phase8_robust.py <dataset> <task> <model> [seeds]`; `python phase8_analysis.py`.
8. **Reports, tables, figures, ledger, tests**:

```bash
python phase1_report.py misalignment unbalance bearings all comfaulda7 && python phase37_report.py && python phase56_report.py && python phase5b_report.py && python phase8_report.py
```

```bash
python make_tables.py && python make_figures.py && python history.py update && python -m pytest -q tests/
```

Datasets: `mafaulda` tasks `misalignment` (T1), `unbalance` (T2), `bearings` (T3), `all` (T4); `comfaulda` task
`comfaulda7` (C1). Remote parallel execution: `WORKER.md`, `WORKER_P3P7.md`, `merge_shards.sh` (results are merged
without overwriting; every shard log is kept in `logs/shards/`). Existing result files are never overwritten by any
script (`q1lib.run(..., overwrite=False)`).

## Rules (as required) and where they are enforced

| Rule | Enforcement |
|---|---|
| 1 keep every result, including failures | append-only `HISTORY.jsonl`; failures reported in FINAL_REPORT §8 |
| 2 separate experimental branch | `exp/q1-audit-osfno`; shards on `exp/q1-shard-*` |
| 3 never edit scores in tables | tables and reports are generated (`make_tables.py`, `phase*_report.py`); test `test_tables_are_generated_from_results` |
| 4 no hyper-parameter chosen on test speeds | `q1lib.inner_splits` on training runs only; test `test_inner_splits_use_training_runs_only` |
| 5 a 5-s record is indivisible | partitions are by run; test `test_population_and_outer_partition` |
| 6 same partitions for all comparisons | partition hash in every result; `stats_q1.compare` asserts it; test `test_every_result_file_uses_the_same_partitions` |
| 7 publish every seed, config, partition, metric | result JSON + `HISTORY.jsonl`; test `test_every_model_has_five_seeds` |
| 8 exploration separated from locked confirmation | `locks/`, pre-registrations in `PROTOCOL.md`; test `test_phase3_locks_written_before_outer_evaluation` |
| 9 verify every reference and novelty claim | `LITERATURE.md` (Crossref-checked), `POSITIONING.md` ("not found" wording) |
| 10 manuscript untouched before validation | no change under `paper/` on this branch |

## Résumé (français)

Aucune variante d'opérateur neuronal (OS-FNO A/B/C/E, DRO, SupCon, FNO réglé par validation imbriquée) ne bat les
baselines solides en extrapolation de vitesse. Le seul modèle qui passe la règle pré-enregistrée est le CNN résiduel
sur spectres d'ordres, qui est une baseline. Le conditionnement FiLM par la vitesse nuit, et l'entrée vitesse est
inutile. Les fusions, l'empileur à porte sélectionnée, les enveloppes multi-bandes et l'entraînement robuste ne sont
pas retenus par leurs règles. L'entraînement robuste apporte pourtant de gros gains de robustesse, au prix d'une perte
de score propre sur T1. La phase 8 montre qu'un classement par précision propre est trompeur. Les FNO qui utilisent la
vitesse s'effondrent avec 2 % d'erreur de vitesse. Le CNN, le plus précis, s'effondre avec un capteur mort. Les défauts
combinés de COMFAULDA ne sont pas reconnus à partir des défauts simples. Contribution principale : l'étude critique et
la découverte sur la robustesse. Revue recommandée : Measurement (alternative : IEEE TIM).
