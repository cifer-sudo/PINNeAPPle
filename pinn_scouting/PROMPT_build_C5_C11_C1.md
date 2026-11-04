# Prompt for Claude Code: build projects C5, C1 and C11 (from scouting to paper-grade experiments)

> Paste everything below the line into a new Claude Code session opened in `/home/user/Q1 paper/PINNeAPPle`
> (branch `pinn-scouting`). It is self-contained: it restates what the scouting phase found, so the new session
> does not need this conversation.

---

## ROLE

You are a senior research engineer in physics-informed machine learning for batteries and power electronics.
You work autonomously in this repository and verify every claim. You are building three research projects up to
a pre-registered **week-3 decision gate**. Each project must end either in a go decision with evidence or in a
documented stop. **Do not tune anything until it "looks good". A negative result reported honestly is a valid
outcome.**

## CONTEXT YOU MUST READ FIRST (in this order)

1. `pinn_scouting/TOP5.md` (project cards, kill criteria, prototype results) and `pinn_scouting/LOG.md` (every
   decision, every known data issue, decisions D1-D19).
2. `pinn_scouting/prototypes/README.md`, then both prototypes:
   - `prototypes/rw_health_nasa/`: C5, a neural-ECM fitted on random-walk voltage.
     - In distribution: RMSE 0.118 Ah (MAPE 5.1 %), which beats Coulomb counting at 0.147 Ah.
     - OOD (40 °C → room temperature): fails, 0.55 Ah, with the voltage residual rising from 8 to 24.5 mV.
   - `prototypes/coretemp_wmg/`: C1, core temperature.
     - The a-priori PINN reaches 0.391 K, against 0.260 K for a windowed MLP and 0.360 K for the Biot relation.
     - The simple heat model `R0·I²` misses the end-of-discharge peak.
     - Only `tau = Cc·Rc` and `R0/Cc` are identifiable.
3. `AGENTS.md` at the repo root (PINNeAPPle rules).
   - Apply the spirit: no result without physics checks; "tested" is not "validated"; no invented numbers or
     citations; never widen a tolerance to get a pass.
4. The newly read close competitor for C5:
   - **Wang & Zhao, "Differentiable physics information neural network with equivalent circuit model constraints
     for lithium-ion battery parameter identification", J. Energy Storage 155 (2026) 121685,
     doi:10.1016/j.est.2026.121685.**
   - The PDF is in `/root/.claude/uploads/` (`875e201e-1-s2.0-S2352152X26013496-main.pdf`). Read it; facts already
     extracted:
     - **Model (DPINN).** Three MLPs (3×256, tanh, softplus outputs): OCV(SOC); [R0, C_i](SOC); R_i(SOC) or
       R_i(SOC, I). They feed a differentiable Rint/1RC/2RC ECM, discretised with forward Euler and variable Δt.
     - **Scaling.** Outputs use "physical-scale projection" (θ = θ_ref · softplus(z)) or a dynamic EMA z-score.
     - **Loss.** Voltage only: separate MSE terms for pulse and rest segments with learned log-σ weights, plus an L2
       smoothness penalty on consecutive parameter estimates. Adam at lr 1e-4, early stopping (patience 1000),
       batch 8, windows of 900 samples.
     - **Data.** **One** EVE 18650 2.5 Ah cell, HPPC at 22 °C (1 A for 13 % SOC, then a 5 A / 60 s pulse, then 1 h
       rest); 1 s sampling. Private ("available on request").
     - **Results.**
       - SOC-only 2RC-DPINN: voltage MAE 2.67 mV, RMSE 6.18 mV.
       - LSTM: MAE 46.2 mV.
       - Least-squares ECM: RMSE > 36 mV.
       - OCV against relaxation points: RMSE 6.2 mV, max 13.1 mV.
       - R0 against DCIR: mean absolute deviation 4.1 mΩ (2RC); estimates about 2× DCIR at low SOC.
       - One other cell at 10 °C on a dynamic profile: MAE 12.6 mV.
     - **What it does NOT do.**
       - SOC comes from Coulomb counting with the nominal capacity, so **capacity is not identified**.
       - No ageing or SOH, no temperature dependence, a single cell.
       - No uncertainty, no statistics, no multi-cell OOD protocol, no public data.
   - The other 2026 paper flagged in the scouting (**doi:10.1016/j.est.2026.125097**, "Physics-informed learning
     of health-aware equivalent circuit parameter evolution") is **still unread**.
     - Try to get it: Crossref abstract, publisher page, author preprint, or ask the user for the PDF.
     - Until it has been read, C5's novelty claim stays conditional.

## ENVIRONMENT AND DATA ALREADY ON DISK

- **Python environment.**
  - `/home/user/venv-scout`: numpy, scipy, JAX CPU, optax, scikit-learn, matplotlib, mat-io, py7zr, pytest.
  - PyTorch is not installed (download.pytorch.org is blocked by the proxy). Stay with JAX unless the user
    installs torch.
  - Try `pip install -e .` of PINNeAPPle into a separate venv. If it works, wrap each experiment in
    `pinneapple_lab.experiment(...)` and report `pp.trust_card` / `pp.validate` where they fit. If it is blocked,
    continue without it: **no science may depend on PINNeAPPle being installed.**
- **NASA Randomized Battery Usage.**
  - Location: `/home/user/data_raw/nasa_rw/`.
  - Already present: groups `RW_Skewed_High_40C` (RW25-28) and `Battery_Uniform_Distribution_Discharge_Room_Temp`
    (RW3-6).
  - Fetch the other 5 groups with `pinn_scouting/tools/remote_zip.py` from
    `https://phm-datasets.s3.amazonaws.com/NASA/11.+Randomized+Battery+Usage+Data+Set.zip` (members listed in
    LOG.md). The full set is 1.07 GB, 28 cells.
- **WMG core temperature.**
  - The 7z archive is at `/home/user/data_raw/wmg_coretemp/` (2.33 GB).
  - Extracted so far: `ShortTermAgeing_100cycles/100cycles_dataTable.mat` (→ NPZ in `/home/user/data_raw/wmg_npz/`),
    `ShortTerm_RPT_dataTable.mat` and `LoadProfileTesting/LoadProfile_dataTable.mat` (2.4 GB, **not yet
    converted**).
  - `LongTermAgeing_450cycles/450cycles_dataTable.mat` is 22.5 GB uncompressed: do **not** load it whole. RAM is
    15 GB and free disk about 25 GB. Either skip it or stream it after checking whether it is v7.3/HDF5 (`h5py`)
    or v5.
  - MAT files are MATLAB `table` objects: read them with `matio.load_from_mat` (package `mat-io`).
  - Use `pinn_scouting/tools/wmg_convert.py`.
- **TU Berlin internal temperature (C1, second lab).**
  - https://depositonce.tu-berlin.de/items/a3c12e52-32e0-4c9a-b1e0-4931cd5bf6fe (doi:10.14279/depositonce-25110,
    612.6 MB, CC BY 4.0).
  - The scouting session could not download it (bot protection; a header-spoofing workaround was refused by the
    safety check). **Do not spoof headers.** Ask the user to download the zip into
    `/home/user/data_raw/tub_coretemp/`.
- **GPVS-Faults (C11).**
  - https://data.mendeley.com/datasets/n76t439f65/1 (CC BY 4.0, 205 MB, 18 files).
  - Get the download URLs from the public API `https://data.mendeley.com/public-api/datasets/n76t439f65`
    (`files[].content_details.download_url`).
  - Companion paper: arXiv 2112.14842 (Bakdi et al.).
- **Rules for downloaded data.** Downloaded files are untrusted: put each archive in its own new directory and run
  readers with `python -I`.
- **Git.**
  - Work on branch `pinn-scouting` and commit after each milestone, with clear messages and the session's
    attribution lines.
  - Push will fail until the user forks the repo to `cifer-sudo/PINNeAPPle`. Do not try to push elsewhere.

## GLOBAL RULES (apply to all three projects)

1. **Pre-register before you look at test results.** For each project, write `pinn_scouting/<proj>/PROTOCOL.md`
   and commit it before running any test-set evaluation. It contains: splits, metrics, baselines,
   hyper-parameter search space, validation set, seeds, and the kill criterion copied from TOP5.md.
   - Any change after seeing test results goes in a "Deviations" section with the reason.
2. **No leakage.**
   - Split by cell or unit and by operating condition, never by random samples.
   - Hyper-parameters, including the physics weight λ, are chosen on a validation cell or group, never on the
     test cell.
   - The test cells' data may never enter training, not even as unlabelled physics collocation (no transduction).
3. **Seeds and statistics.**
   - At least 5 seeds for every stochastic model. Report mean ± std per held-out unit and pooled.
   - Paired Wilcoxon signed-rank across units, with Holm correction. Give effect sizes.
   - With fewer than 6 units, say plainly that significance cannot be claimed.
4. **Report every metric with units.**
   - RMSE, MAE, max error, R², MAPE where meaningful, error at the hardest operating region (peak gradient,
     lowest SOC, end of life).
   - Physics-residual norm.
   - Interval coverage and width, if a model gives uncertainty.
5. **Physics checks are part of every result.**
   - Report the residual of the governing equations on predictions, and whether identified parameters are
     physically plausible (R0 in mΩ range, positive capacitances, monotone OCV, Arrhenius sign).
   - Compare identified parameters with independent measurements where they exist: DCIR from pulses, OCV from
     relaxation, reference capacity.
6. **Identifiability first.**
   - Before training any physics model, do a structural or practical identifiability check: Fisher information or
     profile likelihood on a synthetic trajectory generated from the same equations.
   - Fix or reparametrise unidentifiable parameters. In C1 only `Cc·Rc` and `R0/Cc` are identifiable from the
     surface temperature.
7. **Tests.**
   - Every module gets unit tests: data loaders against the real file structure (skip if absent), physics residual
     ≈ 0 on an exact synthetic solution, parameter recovery on synthetic data with known parameters, no-leakage
     test on the split functions.
   - Keep the existing 12 tests green.
8. **Code layout.** Reusable code goes in `pinn_scouting/ev_pinn/` (a small package: `data/`, `physics/`,
   `models/`, `eval/`), with experiment scripts in `pinn_scouting/<proj>/experiments/`. Configs are YAML or
   dataclass, results go to JSON, and figures are produced by scripts, never by hand.
9. **Logging.** Append every URL visited, every download, every decision and every deviation to
   `pinn_scouting/LOG.md`. New references go into `pinn_scouting/references.bib` only after their metadata was
   opened (Crossref or DataCite).
10. **Honesty.**
    - Never fabricate a number, DOI, licence, impact factor or published result; write UNVERIFIED instead.
    - If a model shows no advantage, say so in the results file and in the chat.
    - Post-hoc experiments are allowed only when labelled "post-hoc" everywhere.

---

## PROJECT C5 (priority 1): label-free health tracking from random EV-like loads (NASA RW)

**Research question.** Can capacity Q and resistances R0/R1 be identified from random-walk operation alone (no
capacity labels), track ageing across 28 cells, and transfer across ambient temperature and load distribution
better than (a) classical ECM/EKF, (b) data-driven regressors and (c) a reproduction of the Wang & Zhao 2026 DPINN?

**Positioning against Wang & Zhao 2026, to state in the paper.**
- They identify SOC-dependent ECM parameters on one fresh cell from HPPC, with capacity given.
- We identify **capacity itself and its evolution with ageing** from operation data, with temperature dependence.
  We validate on independent reference tests over 28 public cells and 7 load/temperature groups, with OOD splits
  and uncertainty.
- Their architecture is our strongest neural-ECM baseline, not our method.

### C5 Step 0: data (week 1)
1. **Download and load the cells.**
   - Download the 5 missing RW groups.
   - Extend `prototypes/rw_health_nasa/data.py` into `ev_pinn/data/nasa_rw.py` to load all 28 cells.
   - Handle sentinels (temperature −4094.1 °C seen in RW3), truncated cycles (< 0.1 Ah), and the variable-charge
     group.
2. **Extract per cell:**
   - (a) the RW cycles (1 s);
   - (b) `reference discharge` capacity (1 A to 3.2 V) with its time stamp;
   - (c) `reference power discharge` (15 W) runtime;
   - (d) the **pulsed-load** sequences (1 A, 10 min on / 20 min off, every 50 RW cycles). These are HPPC-like, so
     compute DCIR R0 = ΔV/ΔI at each pulse edge (Wang & Zhao use the same definition) and OCV at the end of each
     20-min rest.
3. **Write `DATA_CARD.md`.** Groups (load distribution, ambient, current range, cells), counts of cycles,
   references and pulses, temperature ranges, and anomalies found (with cell and step numbers). Include a figure of
   reference capacity against Ah throughput for all 28 cells.

### C5 Step 1: identifiability and physics (week 1)
- **Model per RW cycle k.**
  - $V = U_{ocv}(z,T) - R_0(z,T,h)\,I - \sum_i v_i$, with $\dot v_i = -v_i/(R_iC_i) + I/C_i$.
  - $z = z_0 - \int I\,dt / Q_k$.
  - Lumped thermal state: $mc\,\dot T = I(U_{ocv}-V) + I\,T\,\partial_T U_{ocv} - hA(T - T_{amb})$. The surface
    temperature is measured, so use it as an observation.
- **Temperature dependence.**
  - Arrhenius: $R_0 = R_0^{ref}\exp(\frac{E_a}{R}(\frac1T - \frac1{T_{ref}}))$.
  - An entropic term or a small temperature correction of the OCV.
  - The prototype's OOD failure is the motivation.
- **Anchoring the OCV.** Anchor its scale with the end-of-rest voltages of the pulse tests (z from the reference
  discharge). This removes the Q-versus-OCV-scale ambiguity that forced a post-hoc linear calibration in the
  prototype.
- **Identifiability check.** On synthetic random-walk cycles generated from this model (realistic parameters,
  5 mV noise), compute the Fisher information of (Q, R0, R1, τ, Ea) for:
  - full cycles;
  - partial cycles. At 40 °C the RW cycles span only 30-40 % of capacity, because the 5 A steps reach 3.2 V early.

  Report which parameters are identifiable from one cycle and which only from many cycles pooled.

### C5 Step 2: models (weeks 2-3)

| id | model | notes |
|---|---|---|
| B0 | Coulomb count to cut-off + calibration | prototype baseline |
| B1 | 2RC ECM + EKF/dual-EKF, parameters from the pulse tests, Arrhenius-scaled | classical physics |
| B2 | Data-driven: ridge, GRU on event windows, and a re-implementation of the event-window Transformer idea (J. Phys. Energy 2026, doi:10.1088/2515-7655/aebb63) | use **leakage-safe inputs** only |
| B3 | **Wang & Zhao DPINN reproduction**: 3 sub-networks, softplus + physical-scale projection, pulse/idle heteroscedastic loss, smoothness penalty, 2RC, SOC computed with nominal capacity as in the paper | trained on pulse tests and RW data |
| M1 | **Ours**: health-aware neural-ECM | see below |

- **Validating B3.** Before using it as a baseline, check that the reproduction reaches a voltage MAE of a few mV
  on pulse tests. If it does not, document why; do not claim to beat a broken baseline.
- **M1 (ours), the health-aware neural-ECM.**
  - Shared neural OCV(z,T), monotone in z (positive-derivative parametrisation, not only a penalty).
  - A slow health state $h_k=(Q_k, R_{0,k})$ evolving per cycle as $Q_{k+1} = Q_k - g_\phi(\text{throughput}, \bar I, \bar T, \bar z)\ge0$.
  - A process-noise term, so it can also run as a filter.
  - Loss: voltage residual (all RW seconds) + temperature residual + health-dynamics residual + OCV anchoring on
    pulse rests + monotonicity.
  - **No reference capacity in the loss.** Use the references only for validation, plus an ablation with sparse
    supervision (0, 1, or all references of the training cells).
  - Uncertainty: deep ensemble (5 seeds) or Laplace, with conformal calibration on the validation group.

### C5 Step 3: evaluation protocol (frozen in PROTOCOL.md)
- **Splits.** (i) Leave-one-cell-out within each group. (ii) **Leave-one-group-out** over the 7 groups (the main
  result). (iii) Train on 40 °C groups, test on room-temperature groups, and the reverse.
- **Metrics.**
  - Capacity: RMSE, MAE and max error (Ah); MAPE (%); R² per cell and pooled.
  - Resistance: R0 against DCIR from the pulses (mΩ), and OCV against rest voltages (mV). The same validation
    style as Wang & Zhao, so their 4.1 mΩ and 6.2 mV numbers are a reference point.
  - Voltage residual (mV) and 90 % interval coverage.
- **Ablations.** No thermal state; no Arrhenius; fixed τ vs learned; 1RC vs 2RC; no OCV anchoring; λ weights;
  additive voltage noise of 5/10/20 mV; fraction of RW cycles used (100/50/20/5 %).

### C5 Week-3 kill criterion (from TOP5.md, unchanged)
- **Pass condition.** On leave-one-group-out, M1 must beat the best data-driven model on ≥ 5 of 7 groups **and**
  reach a mean MAPE < 3 %.
- **Second kill switch.** If doi:10.1016/j.est.2026.125097 turns out to do the same thing.
- **On failure:** write `c5/DECISION.md` with the numbers and propose the fallback (an OOD benchmark paper, or
  stop).

### C5 deliverables
- `ev_pinn/` modules with tests.
- `c5/PROTOCOL.md`, `c5/DATA_CARD.md`, `c5/RESULTS.md` (tables mean ± std, n), `c5/DECISION.md`.
- Figures: capacity trajectories against reference (all cells); OOD bar chart; R0 against DCIR; OCV against rest
  voltages; ablation chart; Fisher-information heat-map.

---

## PROJECT C1 (priority 2, cheap kill test first): core temperature against embedded thermocouples

**Current state.** The a-priori PINN lost (0.391 K against 0.260 K for the MLP). Only one honest rescue path is
allowed:
- better physics, selected on a validation cell;
- then the kill test.

### C1 Step 0: data (week 1)
1. **Convert the WMG load-profile table.**
   - Convert `LoadProfile_dataTable.mat` (2.4 GB) to per-cell NPZ with `tools/wmg_convert.py`.
   - Check memory first; if mat-io cannot hold it, process in chunks or report.
   - Document the 45-min urban drive profile, the cells tested, and at which ageing stage.
2. **Long-term data.**
   - Decide how to use `LongTerm_RPT_dataTable.mat` (2.7 GB).
   - For `450cycles_dataTable.mat` (22.5 GB): check whether it is HDF5 and streamable. If it is not, skip it and
     log why.
3. **TU Berlin.**
   - Once the user has placed the zip, inspect it: channels (are V and I present?), sampling, ambients, drive
     cycles.
   - If V and I are absent, the heat source must come from current only. Say so; it weakens the cross-lab test.
4. **Known issues** (carry into `DATA_CARD.md`):
   - VP011 core sentinel −3276.8 °C, with block 2 missing.
   - 0.1 °C / 0.01 V quantisation.
   - A 0.3-0.5 K core-surface offset at rest, which could be a thermocouple calibration offset: estimate it as a
     parameter.
   - Ambient temperature is not logged: estimated as the 1st percentile of the surface temperature per block.

### C1 Step 1: physics upgrade (week 1-2)
- **Two-state model.** $C_c\dot T_c = \dot Q - (T_c - T_s)/R_c$ and $C_s\dot T_s = (T_c-T_s)/R_c - (T_s - T_{amb})/R_u$.
- **Heat source candidates (compare all):**
  - (a) $R_0 I^2$, constant R0 (prototype);
  - (b) $I\,(U_{ocv}(z) - V)$, irreversible heat from measured V. Needs U_ocv(z): get it from RPT pseudo-OCV or
    C/20 data;
  - (c) (b) + entropic $I\,T\,\partial U_{ocv}/\partial T$, with dU/dT either from literature for NMC811/Si-graphite
    (cite it) or identified;
  - (d) (b) + a small neural correction $\delta\dot Q_\phi(z, I, T)$ with a sign and magnitude prior.
- **Identifiability.**
  - With $T_s$ as input, fix $C_c$ (or identify only τ and gains). Redo the Fisher analysis for the two-state model
    when $T_s$ is an output.
- **Observer baseline.** A two-state Kalman filter (B3) with the best heat model. This is the classical baseline
  reviewers expect.

### C1 Step 2: models and the kill test (week 2-3)
- **Baselines.**
  - B1: Biot relation $T_c = T_s + G(T_s - T_{amb})$.
  - B2: one-state lumped model.
  - B3: two-state KF.
  - DD: windowed MLP and GRU.
- **Physics-informed models.**
  - PINN: estimator + residual of the chosen heat model on training cells **and** non-instrumented cells
    (VP016-018, no test-cell data).
  - Differentiable KF: a KF whose process model includes the neural heat term, trained end-to-end.
- **λ selection.** λ and the heat model are chosen by leave-one-cell-out **inside the two training cells**
  (nested). The test cell is touched once.
- **Scenarios.** S1: all labels. S2: labels from the first 20 cycles only, tested on later ageing. S3: drive
  profile (LoadProfile) never seen in training. S4: TU Berlin cross-lab and leave-one-ambient-out (5 ambients),
  if V and I are available.
- **Kill criterion (week 3, unchanged).** The physics-informed model must beat both the windowed MLP and the Biot
  relation by ≥ 15 % RMSE at the peak gradient:
  - on held-out WMG cells;
  - on ≥ 3 of 5 held-out TU Berlin ambients.

  Otherwise write `c1/DECISION.md`. Fallback: a "when does physics help" benchmark + identifiability paper
  (honest negative result), or stop.

### C1 deliverables
- `c1/PROTOCOL.md`, `c1/DATA_CARD.md`, `c1/RESULTS.md`, `c1/DECISION.md`.
- Figures: time series at the end-of-discharge peak; error against core-surface gradient; per-ambient bars;
  heat-model ablation; identifiability.

---

## PROJECT C11 (priority 3): sensor fault vs process fault on GPVS-Faults with physics residuals

**Question.** Can whitened physics residuals, fitted on healthy data only, detect faults and attribute them to a
sensor or to the process on a measured grid-tied PV system? This is the real-data counterpart of the user's
simulated DC-microgrid study.
- That study is not in this repo. Ask the user for its path or code before re-implementing; reuse its residual
  and whitening logic if provided.
- Its last known state: the sensor-type classification was fixed, but 6/20 process faults became misclassified as
  sensor faults, and one test was failing. The planned fix was to estimate noise after removing the fitted fault
  signature.

### C11 Step 0: data (week 1)
1. **Download and verify.**
   - Download all 18 files via the Mendeley API into a fresh directory; record the licence and DOI
     10.17632/n76t439f65.1.
   - Read the companion paper (arXiv 2112.14842) and write `c11/DATA_CARD.md` from the **real files**, not from
     the paper: variables, units, sampling rate, MPPT vs IPPT, fault codes F0-F7 (what each one is, onset time,
     duration), class balance, NaN rate.
2. **Confirm the labels.** Confirm from the files which faults are sensor faults (feedback-sensor fault) and which
   are process faults (inverter IGBT, grid sag, partial shading, open circuit, MPPT/IPPT controller faults).
   **If the dataset has only one sensor-fault class, say so: it limits the attribution claim.**

### C11 Step 1: physics residuals
- **Models available from the measured channels** (only the ones the channels support):
  - DC-link energy balance $C v_{dc}\dot v_{dc} = P_{pv} - P_{ac}$;
  - inverter dq current dynamics $L\dot i_{dq} = v^{inv}_{dq} - v^g_{dq} - R i_{dq} \mp \omega L i_{qd}$;
  - PV single-diode I-V consistency;
  - power balance between DC and AC sides.
- **Unknown plant parameters** (C, L, R, diode parameters): identify them on F0 healthy runs only; report
  plausibility.
- **Whitening.** Residual covariance on healthy data, with time-varying noise scaling. Fault-signature directions
  come from physics, e.g. a sensor bias enters only through one measured channel, while a process fault violates
  the balance in a structured way.
  - Estimate the noise **after removing the fitted fault signature**: this was the fix for the microgrid
    regression.

### C11 Step 2: evaluation
- **Train** on F0 only. **Test** on all faults × both modes.
- **Metrics.**
  - Detection: AUC, detection delay (s), false alarms per hour on healthy hold-out runs.
  - Attribution: sensor vs process confusion matrix, balanced accuracy.
  - Magnitude estimate, where it exists.
- **Baselines.**
  - Classifiers reported in the dataset paper: copy their numbers **only** after reading them; otherwise UNVERIFIED.
  - Sliding-mode or Luenberger observer residuals.
  - Autoencoder/PCA residuals trained on F0.
  - A supervised classifier, as an upper bound that uses labels.
- **Ablations.** No whitening; each residual alone; MPPT→IPPT transfer.
- **Kill criterion (week 3).** Attribution accuracy below 90 % on the sensor-fault cases means stop.

### C11 deliverables
- `c11/PROTOCOL.md`, `c11/DATA_CARD.md`, `c11/RESULTS.md`, `c11/DECISION.md`.
- Figures: residual time series per fault; ROC; confusion matrix.
- A short paragraph on how the method would transfer to an EV traction inverter (argued, not claimed).

---

## SCHEDULE AND REPORTING

| week | C5 | C1 | C11 |
|---|---|---|---|
| 1 | all 28 cells loaded, DATA_CARD, pulse-derived DCIR/OCV, Fisher analysis, PROTOCOL committed | LoadProfile converted, TU Berlin requested, heat models (a)-(d) implemented, PROTOCOL committed | data downloaded and verified, DATA_CARD, PROTOCOL committed |
| 2 | baselines B0-B3 incl. DPINN reproduction checked against the paper's mV-level fit | nested λ / heat-model selection, two-state KF | residual models on F0, whitening |
| 3 | M1 + leave-one-group-out → **decision** | kill test S1-S4 → **decision** | full test → **decision** |

**Order of work.** Start with C5 Step 0 and C1 Step 0 in parallel; run long jobs in the background. Do C11 Step 0
while those run.

**At the end of each week, report in chat** (max one page): what was done; the numbers with n and std; what failed;
the next decisions.

**Stop and ask the user only if:**
- a dataset needs their action (TU Berlin download, missing JES 2026 paper, the simulated microgrid code);
- a decision blocks all three projects.

Otherwise make a reasonable assumption, log it in LOG.md, and continue.

## FINAL OUTPUT AFTER WEEK 3
A `pinn_scouting/DECISIONS_week3.md` covering, for each project:
- go / pivot / stop;
- the evidence table;
- the revised paper plan and target journal (APC from `journals/elsevier_apc.xlsx` or open.ieee.org; impact factor
  UNVERIFIED unless checked on JCR);
- the three biggest remaining risks.

Commit everything; push only if the fork remote exists.
