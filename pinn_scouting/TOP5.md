# TOP 5 PINN projects for a Q1 paper: EV / battery priority

*Status 2026-11-04. Inputs: `datasets.csv` (59 datasets), `candidates.md` (13 candidates with saturation evidence),
`scoring.csv` (weighted scores), `prototypes/` (feasibility runs on real data). Every number below either comes
from a file opened in this session (LOG.md) or is marked UNVERIFIED.*

**How to read the ranking.** The weighted score (`scoring.csv`) was fixed **before** the prototypes ran. The
prototypes then changed the picture, and the order below reflects that (see "Post-prototype adjustment" at the end).
I did not tune any model to make it win.

**Journal facts verified here.**
- **Elsevier APCs** come from Elsevier's official price list (`journals/elsevier_apc.xlsx`, downloaded 2026-11-04). All journals named are hybrid, so publishing without an APC is possible, except *Energy and AI* (full OA, USD 4,270).
  - Applied Energy USD 4,210.
  - J. Power Sources USD 4,010.
  - eTransportation USD 4,630.
  - J. Energy Storage USD 4,410.
  - Energy USD 3,960.
  - Electrochimica Acta USD 3,760.
  - Energy Conversion and Management USD 4,500.
- **IEEE hybrid APC:** USD 2,800 in 2026 and USD 2,995 in 2027 (open.ieee.org).
- **Impact factors and review times: UNVERIFIED.** sciencedirect.com, elsevier.com, ieeexplore.ieee.org and cell.com all returned 403/418 to this session. Please check JCR before submitting.

---

## 1. C5 — Label-free tracking of capacity and resistance from random EV-like loads

**1. Working title.** *Physics-informed neural equivalent-circuit learning of battery health from random-walk
operation, validated against independent reference tests.*

**2. Research question and gap.** Can capacity and resistance be tracked from ordinary random-load operation only,
without capacity labels, and does the estimate transfer to another ambient temperature and load distribution?
*Gap: published work on this dataset regresses the sparse reference capacities with black boxes (e.g. an
event-window Transformer). None was found that identifies health states from the voltage response itself and then
uses the reference tests only as held-out ground truth.*

**3. Data.**
- **Source.** NASA PCoE Randomized Battery Usage, 28 × 18650 cells in 7 groups. Mirror: https://phm-datasets.s3.amazonaws.com/NASA/11.+Randomized+Battery+Usage+Data+Set.zip (1.07 GB; licence not specified, US Government work).
- **Citation to use.** Bole, Kulkarni, Daigle, PHM 2014, doi:10.36001/phmconf.2014.v6i1.2490.
- **Variables used.**
  - From the random-walk discharge steps (1 s): `voltage`, `current`, `temperature`, `time`.
  - Held out as validation targets only: Ah of the `reference discharge` (1 A to 3.2 V) and the `pulsed load` response.
- **Inspected here.**
  - RW25-28 (40 °C, 0.5-5 A skewed high): 593-650 RW cycles and 12-14 reference capacities per cell.
  - RW3-6 (room temperature, 0.5-4 A uniform): 22-44 reference capacities per cell, down to 1.06 Ah.

**4. Physics and architecture.**
- **Model equations.**
  - $V_k(t)=f_\theta\big(z_k(t)\big)-R_{0,k}(T)\,I(t)-v_{1}(t)$, with $z_k(t)=1-\frac{1}{Q_k}\int_0^t I\,d\tau$ and $\dot v_1=-\frac{v_1}{\tau}+\frac{R_{1,k}}{\tau}I$.
  - $f_\theta$ is a shared neural OCV (monotonicity penalty).
  - $(Q_k,R_{0,k},R_{1,k})$ are per cycle.
- **Full project additions.**
  - Lumped thermal state: $mc\,\dot T=I^2R_0+Iv_1-hA(T-T_{amb})$.
  - Arrhenius dependence: $R_0=R_{0}^{ref}\exp\!\big(\tfrac{E_a}{R}(\tfrac1T-\tfrac1{T_{ref}})\big)$.
  - Slow health dynamics: $\dot Q=-g_\phi(I,T,z)\le 0$ and $\dot R_0=h_\phi(\cdot)\ge0$, where $g_\phi, h_\phi$ are small networks constrained to be monotone.
- **Loss.**
  $$\mathcal L=\tfrac1N\sum\|V-\hat V\|^2+\lambda_{T}\|T-\hat T\|^2+\lambda_{h}\sum_k\|Q_{k+1}-Q_k+g_\phi\Delta t\|^2+\lambda_m\,\|\mathrm{ReLU}(-f_\theta')\|^2$$
- **Training.** Stage 1: the OCV and health networks are fitted on training cells. Stage 2: the OCV is frozen and the per-cycle states of unseen cells are fitted. No capacity label enters the loss; a scale calibration is fitted on training cells only.

**5. Baselines and numbers to beat.**
1. Coulomb counting to cut-off.
2. ECM + EKF with per-temperature parameters.
3. Data-driven regressors (ridge, MLP, GRU/Transformer on event windows).
4. The event-window Transformer of *J. Phys. Energy* 2026 (doi:10.1088/2515-7655/aebb63). Trained on RW9 and RW10 and tested on RW11, it reports **R² 0.955, MAE 2.387** (SOH units). Its full table was not read.
5. The 2026 health-aware ECM-evolution paper (doi:10.1016/j.est.2026.125097). Its abstract was not available; read it in full before starting.

Prototype numbers on held-out cells: see "Prototype results (C5)" below.

**6. Validation protocol.**
- **Splits.**
  - Leave-one-cell-out inside each group.
  - Leave-one-group-out across the 7 groups: 3 load distributions × 2 ambients, plus the variable-charge group.
  - No random sample splits.
- **OOD tests.** Unseen ambient (train 40 °C, test room temperature and the reverse), unseen load distribution, and ageing beyond the training range (room-temperature cells reach 1.06 Ah, 40 °C cells only 1.68 Ah).
- **Metrics.** RMSE, MAE and max error in Ah, MAPE (%), R², and voltage residual (mV); mean ± std over 5 seeds and ≥ 8 test cells.
- **Calibration.** Prediction intervals with conformal calibration and coverage reported.
- **Ablations.** Without the physics model (pure regression); without the thermal state; fixed vs learned τ; sparse labels used as weak supervision (0, 1, all references); additive voltage noise (5, 10, 20 mV); fraction of RW cycles used.
- **Statistics.** Paired Wilcoxon over cells, with Holm correction.

**7. Expected contributions and risks.**
- **Contributions.**
  - A label-free health estimator for random EV-like operation, validated on independent reference tests.
  - Transfer across ambient and load distribution, with interpretable R and OCV trajectories.
  - An open benchmark protocol for all 28 RW cells (the current literature uses 3-4 cells).
- **Risks and mitigations.**
  - (i) *Identifiability of Q against the OCV scale.* Fix the OCV end-points from the reference discharge of the first check-up; report the Fisher information.
  - (ii) *The JES 2026 paper may already do this.* Read it first; if it does, pivot to the cross-group OOD benchmark and the thermal extension.
  - (iii) *18650 consumer cells and lab random walks are not vehicle data.* Add a second dataset with drive cycles (Stanford UDDS ageing, OSF) as external validation.

**8. Target journals (ranked).**

| # | Journal | APC | Fit | IF and review time |
|---|---|---|---|---|
| 1 | eTransportation (Elsevier, hybrid) | USD 4,630 | battery health for EVs | UNVERIFIED |
| 2 | Applied Energy (hybrid) | USD 4,210 | — | UNVERIFIED |
| 3 | IEEE Trans. Transportation Electrification (hybrid) | USD 2,800 (2026) | — | UNVERIFIED |
| 4 | Energy and AI (gold OA) | USD 4,270 | — | UNVERIFIED |
| 5 | J. Energy Storage (hybrid, safety net) | USD 4,410 | — | UNVERIFIED |

**9. Work plan (weeks).**
- W1-2: full data pipeline for 28 cells; unit tests (done for 8 cells).
- W3: read the JES 2026 paper; freeze the protocol (pre-registration file in the repo).
- W4-6: ECM-thermal-health model, EKF baseline, data-driven baselines.
- W7-8: leave-one-group-out; uncertainty.
- W9-10: ablations and statistics.
- W11-13: figures, paper, code release.
- Deliverables: code, a 5-figure set (pipeline, health trajectories vs reference, OOD bars, ablations, residual maps), 3 tables.

**10. Kill criterion (week 3).** On leave-one-group-out, the physics model must give a lower RMSE than the best data-driven regressor on at least 5 of the 7 groups and a mean MAPE below 3 %. If not, stop (or keep only as a negative-result benchmark). The JES 2026 overlap check is a second kill switch.

---

## 2. C1 — Core temperature of 21700 cells against embedded thermocouples, across cells, ageing and ambient

**1. Working title.** *When does physics help? Core-temperature estimation of 21700 cells validated on embedded
thermocouples across cells, ageing and ambient temperature.*

**2. Research question and gap.** Does a physics-informed estimator beat (a) the quasi-steady Biot relation, (b) a
two-state Kalman observer and (c) a black box on cells, ageing states and ambient temperatures it never saw?
*Gap: no study found validates core-temperature estimators on two independent embedded-sensor datasets with
leave-one-cell-out and cross-ambient splits against these three baselines.*

**3. Data.**
- **WMG (Warwick).** https://data.mendeley.com/datasets/bf6fksxpp2/2 (CC BY 4.0; cite Gulsoy et al., *J. Energy Storage* 54 (2022) 105260).
  - Variables: `Voltage [V]`, `Current [A]`, `Surf Temp [C]`, `Core Temp [C]`, `Step`, `Cycle No`.
  - 1 Hz; 3 instrumented and 3 pristine LG M50 cells; 550 cycles.
  - Known issues: the VP011 core sensor drops out (sentinel −3276.8 °C, a whole block missing); 0.01 V / 0.1 °C resolution.
- **TU Berlin.** https://depositonce.tu-berlin.de/items/a3c12e52-32e0-4c9a-b1e0-4931cd5bf6fe (CC BY 4.0; doi:10.14279/depositonce-25110).
  - 3 LG M50LT cells with a drilled-in type-K core sensor; 12 drive cycles × 5 ambients.
  - Voltage and current channels not confirmed; file not downloaded here (D5).

**4. Physics and architecture.**
- **Two-state model.** $C_c\dot T_c=\dot Q-\frac{T_c-T_s}{R_c}$ and $C_s\dot T_s=\frac{T_c-T_s}{R_c}-\frac{T_s-T_{amb}}{R_u}$.
- **Heat generation.** $\dot Q=I\,(U_{ocv}(z)-V)+I\,T\,\frac{\partial U_{ocv}}{\partial T}$, with SOC-dependent resistance. The prototype shows a constant-$R_0\,I^2$ heat model misses the end-of-discharge peak.
- **Identifiability.** With $T_s$ as input, only $\tau=C_cR_c$ and $R_0/C_c$ are identifiable (verified in the prototype: a 3-parameter fit drifts to a degenerate solution).
- **Estimator.** An MLP or GRU estimator $\hat T_c=T_s+N_\phi(\text{window of }I,V,T_s)$.
- **Loss.** $\mathcal L=\|\hat T_c-T_c\|^2_{\text{labelled}}+\lambda\|C_c\Delta\hat T_c/\Delta t-\dot Q+(\hat T_c-T_s)/R_c\|^2_{\text{all cells}}$. The residual also runs on non-instrumented cells.
- **Full-project upgrade.** A differentiable two-state Kalman filter whose process model includes the neural heat term.

**5. Baselines and numbers to beat.**
- **On WMG (prototype, leave-one-cell-out, held-out cell):**

  | Method | RMSE (K) |
  |---|---|
  | Biot relation | 0.360 ± 0.094 |
  | Lumped 1-state | 0.402 ± 0.048 |
  | Windowed MLP | **0.260 ± 0.044** |
  | PINN (λ = 1) | 0.391 ± 0.063 |

- **Published on other data (not comparable):**
  - Physics-guided Bi-LSTM, MAE 0.16 °C (0.31 °C on unseen cells): IEEE TTE 2025, doi:10.1109/tte.2025.3649230.
  - PINN-KAN, core MAE 0.752 °C: IECON 2025, doi:10.1109/iecon58223.2025.11221787.
  - A withdrawn 2026 Zenodo record (abstract seen via OpenAlex; page now HTTP 410) reported 0.13 K RMSE for a calibrated Biot relation and a worse inverse PINN. It is unpublished, so it cannot be cited, but reviewers may know it.
- **On the WMG data itself:** no published estimator numbers were found (the 2022 paper is about instrumentation).

**6. Validation protocol.**
- **Splits.** Leave-one-instrumented-cell-out within each lab; train on WMG and test on TU Berlin and the reverse (cross-lab).
- **OOD tests.** Leave-one-ambient-out on TU Berlin (5 levels); late ageing blocks.
- **Metrics.** RMSE, MAE, max error and RMSE at the peak gradient (K); interval coverage; physics residual (W); mean ± std over 5 seeds and all held-out cells.
- **Ablations.** λ sweep chosen on a validation cell (never the test cell); heat model (I²R vs I(U−V) vs + entropic); with/without non-instrumented collocation; label fraction; sensor noise and 0.1 °C quantisation; window length.
- **Statistics.** Paired tests per cell and ambient.

**7. Expected contributions and risks.**
- **Contributions.**
  - The first two-lab, cross-ambient benchmark of core-temperature estimators on embedded sensors.
  - A quantified answer to *when* physics helps (identifiability analysis plus ablations).
  - A semi-supervised residual that uses non-instrumented cells.
- **Risks and mitigations.**
  - (i) *Physics does not help (the prototype already shows it).* Upgrade the heat model, then fall back to a benchmark-and-identifiability paper.
  - (ii) *Only 3 + 3 instrumented cells.* Report per-cell results; avoid significance claims that n cannot support.
  - (iii) *Instrumentation perturbs the cells, and a 0.3-0.5 K core-surface offset is visible at rest* (possibly thermocouple calibration). Estimate an offset term and report it.

**8. Target journals.**

| # | Journal | APC | Fit | IF and review time |
|---|---|---|---|---|
| 1 | IEEE Trans. Transportation Electrification (hybrid) | USD 2,800 | — | UNVERIFIED |
| 2 | Applied Energy | USD 4,210 | — | UNVERIFIED |
| 3 | J. Power Sources | USD 4,010 | — | UNVERIFIED |
| 4 | eTransportation | USD 4,630 | — | UNVERIFIED |
| 5 | J. Energy Storage (safety net) | USD 4,410 | — | UNVERIFIED |

**9. Work plan (weeks).**
- W1: convert the WMG long-term and load-profile tables (28 GB extracted: needs a disk or a streaming reader); download TU Berlin.
- W2-3: heat-model upgrade and the kill test.
- W4-6: two-state differentiable KF, GRU baseline.
- W7-8: cross-lab and cross-ambient tests.
- W9-10: ablations and identifiability.
- W11-13: writing.
- Deliverables: code, 6 figures, 3 tables.

**10. Kill criterion (week 3).** With the upgraded heat model and λ selected on a validation cell, the physics-informed estimator must beat the windowed MLP **and** the Biot relation by ≥ 15 % RMSE at the peak gradient on held-out cells (WMG) and on at least 3 of 5 held-out ambients (TU Berlin). The current prototype fails this. A post-hoc small λ = 0.01 gave 0.285 ± 0.076 K against 0.310 ± 0.066 K for the MLP in the scarce-label scenario: within one std, so not a result.

---

## 3. C4 — Arrhenius / √t-structured ageing model that extrapolates to unseen temperature and depth of discharge

**1. Working title.** *Kinetics-structured physics-informed learning of calendar and cycle ageing that extrapolates
across temperature and depth of discharge for three Li-ion chemistries.*

**2. Research question and gap.** Can a hybrid model with Arrhenius/SEI structure predict capacity fade at a
temperature or depth of discharge (DoD) that was entirely held out of training?
*Gap: the closest work (PiDDM, arXiv 2026) extrapolates in time on one chemistry. No study found holds out
whole temperatures or DoD levels across NCA/NMC/LFP.*

**3. Data.**
- **Sandia** (Preger et al., *J. Electrochem. Soc.* 167 (2020), doi:10.1149/1945-7111/abae37), via Battery Archive: 18650 NCA/NMC/LFP × temperature × DoD × rate. Licence: Battery Archive code of conduct (cite the article and the site).
- **ISU-ILCC** (238 NMC pouch cells, 63 conditions; doi:10.1016/j.xcrp.2024.101891).
- **CALCE PLN storage** (144 cells, 4 temperatures × 3 SOC; calendar ageing).
- **Variables.** Cycle-level discharge capacity, Ah/Wh throughput, temperature, DoD, C-rates. Files not yet inspected here (UNVERIFIED structure).

**4. Physics and architecture.**
- **Ageing law.**
  - $Q_{loss}=k_{cal}(T,\bar z)\sqrt{t}+k_{cyc}(T,c,\mathrm{DoD})\,\mathrm{Ah}^{\beta}$.
  - $k=k_0\exp\!\big(-\frac{E_a}{R}(\frac1T-\frac1{T_{ref}})\big)$.
  - Optional plating/knee term $k_{pl}\,\mathrm{ReLU}(\cdot)$ at low $T$ and high $c$.
- **Network.** A network $N_\phi$ predicts bounded corrections to $(k_0,E_a,\beta)$ from condition embeddings.
- **Loss.** $\|Q-\hat Q\|^2+\lambda_1\|\mathrm{ReLU}(\partial_t\hat Q)\|^2+\lambda_2\|\partial_{1/T}\ln k-(-E_a/R)\|^2$.

**5. Baselines.**
- Pure empirical fit (sum of power laws).
- Gaussian process on condition features.
- MLP/GRU.
- PiDDM-style PINN: its abstract gives no number; the authors report improvement over an MLP and a baseline PINN on XJTU.
- Numbers to beat on Sandia/ISU-ILCC: **UNVERIFIED** (no published leave-one-condition-out numbers found).

**6. Validation.**
- **Splits.** Leave-one-temperature-out, leave-one-DoD-out, leave-one-chemistry-out; whole cells only.
- **Metrics.** RMSE (Ah and %), end-of-life cycle error, calibration of intervals.
- **Ablations.** Remove each physics term; data fraction.
- **Seeds.** 5.

**7. Contributions and risks.**
- **Contributions.** Condition-level extrapolation; interpretable activation energies per chemistry; a joint calendar and cycle model.
- **Risks and mitigations.**
  - (i) *Only 3 Sandia temperature levels.* Add CALCE PLN (4 levels).
  - (ii) *Battery Archive copies may differ from the originals.* Cross-check against the papers.
  - (iii) *Knee behaviour not captured.* Add the plating term and report its failure cases.

**8. Journals.**

| # | Journal | APC | IF and review time |
|---|---|---|---|
| 1 | J. Power Sources | USD 4,010 | UNVERIFIED |
| 2 | Applied Energy | USD 4,210 | UNVERIFIED |
| 3 | eTransportation | USD 4,630 | UNVERIFIED |
| 4 | Energy and AI | USD 4,270 | UNVERIFIED |

**9. Plan.**
- W1-2: data and protocol.
- W3-5: models.
- W6-8: hold-out experiments.
- W9-10: ablations.
- W11-12: writing.

**10. Kill criterion (week 3).** On leave-one-temperature-out, the end-of-life error must be ≥ 20 % lower than the empirical fit and the GP. Otherwise stop.

---

## 4. C13 — Physically consistent impedance-ageing trajectories (HPPC + EIS)

**1. Working title.** *Kramers-Kronig- and Arrhenius-consistent learning of impedance ageing from HPPC and EIS on
drive-cycle-aged cells.*

**2. Question and gap.** Can a physics-constrained impedance model trained on some cells predict the impedance and
capacity evolution of others? *Gap: joint HPPC + EIS on drive-cycle-aged cells with leave-cell-out validation was
not found.*

**3. Data.**
- **Stanford** (Pozzato, Allam, Onori, *Data in Brief* 41 (2022) 107995, OSF osf.io/qsabn): 10 LG M50T cells, UDDS, HPPC and EIS from 0.01 Hz to 10 kHz at 20/50/80 % SOC. Dataset licence not stated, so ask the authors.
- **Cambridge EIS** (Zenodo 3633835, CC BY 4.0).
- **Tongji impedance** (Zenodo 6405084, CC BY 4.0).

**4. Physics.**
- **Impedance model.** Transmission-line or Randles ECM, $Z(\omega)=R_\Omega+\frac{R_{ct}}{1+(j\omega\tau)^{\alpha}}+Z_W$.
- **Constraints.** Kramers-Kronig residual, DRT $\gamma(\tau)\ge0$, Arrhenius $R_{ct}(T)$.
- **Ageing links.** $\dot R_{SEI}\propto$ capacity-loss rate; the network maps (cycle, SOC, T) to ECM parameters.

**5. Baselines.**
- ECM fit per spectrum plus regression.
- GPR on EIS (Zhang et al., *Nat. Commun.* 2020); its numbers were not read (UNVERIFIED).
- MLP on raw spectra.

**6. Validation.**
- **Splits.** Leave-one-cell-out; held-out SOC level; held-out charge rate.
- **Metrics.** Impedance RMSE (mΩ), capacity RMSE.
- **Ablations.** Drop KK, DRT or the Arrhenius term.

**7. Contributions and risks.**
- **Contributions.** Consistent impedance trajectories; capacity from impedance; open code.
- **Risks.**
  - Fast-growing niche (45 OpenAlex hits in 2026).
  - Unclear OSF licence.
  - Only 10 cells at one temperature.

**8. Journals.**

| # | Journal | APC | IF and review time |
|---|---|---|---|
| 1 | J. Power Sources | USD 4,010 | UNVERIFIED |
| 2 | Electrochimica Acta | USD 3,760 | UNVERIFIED |
| 3 | J. Energy Storage | USD 4,410 | UNVERIFIED |

**9. Plan.**
- W1-3: data and licence.
- W4-7: models.
- W8-10: validation.
- W11-12: writing.

**10. Kill criterion.** If the physics constraints do not reduce the leave-cell-out impedance error by ≥ 15 % at 3 weeks, stop.

---

## 5. C11 — Sensor fault vs process fault on a real grid-tied PV inverter with physics residuals (outside EV priority)

**1. Working title.** *Telling a wrong sensor from a wrong process: whitened physics residuals on the GPVS-Faults
grid-connected PV dataset.*

**2. Question and gap.** Can physics residuals (DC-link energy balance, dq current dynamics, single-diode model)
attribute faults to sensors or to the process on measured data, without training a classifier on the fault labels?
*Gap: not found among 76 hits.*

**3. Data.** GPVS-Faults, https://data.mendeley.com/datasets/n76t439f65/1 (CC BY 4.0; 205 MB; MPPT/IPPT; faults
F0-F7 including inverter IGBT fault and feedback-sensor fault). Exact columns: UNVERIFIED (not inspected).

**4. Physics.**
- **DC link.** $C\,v_{dc}\dot v_{dc}=P_{pv}-P_{ac}$.
- **Inverter current dynamics.** $L\,\dot i_{dq}=v_{dq}^{inv}-v_{dq}^{g}-R i_{dq}\mp\omega L i_{qd}$.
- **PV array.** $I=I_{ph}-I_0(e^{(V+IR_s)/(nV_t)}-1)-\frac{V+IR_s}{R_{sh}}$.
- **Residuals.** Whitened on healthy runs; fault-signature directions separate sensor faults from process faults.

**5. Baselines.**
- Classifiers in the dataset paper (numbers UNVERIFIED).
- Sliding-mode observer.
- Data-driven autoencoder residuals.

**6. Validation.**
- Train on F0 (healthy) only; test on all faults and both modes.
- Report detection delay, false alarms per hour, and attribution accuracy.
- Ablations: whitening, each residual.

**7. Contributions and risks.**
- **Contributions.** A real-data counterpart of the user's simulated study.
- **Risks.**
  - One plant only.
  - Not EV: transfer to traction inverters must be argued, not shown.

**8. Journals.**
- IEEE TIE or TPEL (hybrid, USD 2,800).
- Energy Conversion and Management (USD 4,500).
- IF: UNVERIFIED.

**9. Plan.** 10 weeks.

**10. Kill criterion.** Attribution accuracy below 90 % on the sensor-fault cases at 3 weeks means stop.

---

## Post-prototype adjustment

The pre-prototype weighted scores put C1 (4.05) just ahead of C5 (4.00). The C1 prototype then showed the planned
PINN losing to a plain windowed MLP (0.391 K vs 0.260 K RMSE), with the simple physics model being misspecified at
the end-of-discharge peak. I therefore lowered C1's physics-depth score from 3 to 2 in practice (`scoring.csv`,
column `post_prototype_note`), which moves it to second place. C5's prototype result is reported below and decides
whether it keeps first place.

## Prototype results (C5): what the real data say

From `prototypes/rw_health_nasa/results/RESULTS.md`. These are feasibility runs: hyper-parameters were fixed in advance and the test cells were never used for tuning.

**In distribution (leave-one-cell-out, RW25-28, 40 °C).** About 36 training labels per fold; 12 reference capacities per test cell.

| Method | RMSE (Ah) | MAPE |
|---|---|---|
| **neural-ECM (label-free)** | **0.118 ± 0.031** | 5.1 ± 0.8 % |
| Coulomb count to cut-off | 0.147 ± 0.042 | 7.1 % |
| Ridge on cycle features | 0.154 ± 0.045 | 7.1 % |
| MLP on cycle features | 0.537 ± 0.176 | 21.8 % |

- The physics-structured estimator is the best of the four.
- R² is negative for every method, because the capacity range within one cell (1.7-2.15 Ah) is narrow compared with the errors. **No method is good yet.**
- Even the best MAPE (5.1 %) misses the 3 % target set in the kill criterion.

**Out of distribution (train on 40 °C skewed-high, test on room-temperature uniform cells RW3-6, 146 references).** Every method fails.

| Method | RMSE (Ah) | MAPE |
|---|---|---|
| Coulomb count | 0.446 | 29 % |
| neural-ECM | 0.552 | 26 % (outliers up to 2.7 Ah) |
| Ridge | 1.21 | — |
| MLP | 8.8 | diverges |

The diagnosis is clear:
- The neural-ECM voltage residual rises from 8 mV to 24.5 mV.
- The correlation of the raw capacity estimate with the reference capacity falls from 0.08-0.83 to 0.09.

So the OCV learned at 40 °C, with a fixed τ and no temperature dependence, does not transfer. In addition, the test cells age to 1.06 Ah, far below anything seen in training (≥ 1.68 Ah). The model therefore needs the temperature-dependent physics planned in the card: Arrhenius R(T), dU/dT, the thermal state, and the OCV anchored on a reference test.

**Verdict.** There is a positive but weak in-distribution signal: the label-free physics model beats supervised regressors trained on very few labels. OOD fails for an identifiable reason. C5 stays first, conditional on the week-3 kill test with the temperature-aware model.

## Final order after both prototypes

1. **C5** NASA RW label-free health tracking. Pre-prototype score 4.00, unchanged; positive in-distribution signal, OOD fails.
2. **C1** Core temperature with embedded sensors. Score 4.05 → 3.85 after the prototype (physics depth 3 → 2): the a-priori PINN loses to an MLP.
3. **C4** Arrhenius / √t ageing extrapolation. Score 3.80; no prototype.
4. **C13** HPPC/EIS impedance-ageing consistency. Score 3.80; no prototype.
5. **C11** GPVS sensor-vs-process faults. Score 3.80; outside the EV priority.

Runner-up: **C6** (EV field data). It has the best journal fit but no capacity ground truth.
