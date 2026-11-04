# Research programme: physics-based fault diagnosis on real data (working log)

This log is updated at every work session. Each paper keeps its hypotheses and decision criteria as fixed *before*
the run that tests them, the measured results with how they were measured, and what is still missing before
submission. A result that fails its criterion stays in the log. No acceptance in a given journal can be promised:
the target venues are where the work would fit once it meets the listed conditions.

## P1 -- MAFAULDA: physics-consistent severity, leakage-free, across sessions and speeds

**Question.** Can the severity of rotor faults (unbalance mass, misalignment offset) be estimated from vibration
with a physical model that holds at unseen speeds and in recording sessions it was not calibrated on, and where do
phase-referenced and learned models fail?

**Data.** MAFAULDA (SMT/COPPE/UFRJ): normal, imbalance 6-35 g, horizontal / vertical misalignment, under- and
overhang bearing faults with 0/6/20/35 g; 5 s at 50 kHz, tachometer, two triaxial accelerometers, microphone.

**Code.** `pinneapple_analysis.inspection.rotating` (`orders`, `mafaulda`, `influence`, `unbalance_study`),
example `examples/mafaulda_unbalance_pilot/`.

| Step | Status | Result |
|---|---|---|
| Pilot: calibrated 1X inversion for the unbalance mass (criteria fixed before the run) | done, NO GO | magnitude of the equivalent unbalance follows the added mass (6.6 ... 35 g); the 1X phase reference drifts between mass levels (44 to 0 deg); the classical phase-free calibration is the most accurate (1.70 g seen speeds, 2.30 g held-out speed bands); the linear dissipative modal model fails across speed bands (8.5-9.7 g); no model extrapolates in speed (about 7-9 g) |
| Tachometer quality | done | 81 underhang runs (79 ball fault, 2 cage fault) and 17 overhang runs have spurious or missing pulses (period spread up to 160 %); pulse detection now uses a minimum pulse width and a refractory period from the spectral fundamental; runs whose periods spread more than 5 % or whose speed is not 0.9-1.05 x the nominal one are excluded and counted |
| A1 cross-session, joint phase-free calibration (pre-registered) | done, FAIL | overhang (held out): 19.4 g (ball fault 54 g, cage 9.0 g, outer race 2.9 g); underhang: ball 3.1 g, cage 2.8 g, outer race 42.7 g. One overhang radial accelerometer reads up to 66 times its healthy 1X in some sessions: a measurement anomaly, not unbalance |
| A2 phase reference inside each bearing folder (pre-registered) | done, drift recurs | angle spans 20-38 deg in all six bearing folders: the 1X phase reference is not consistent between mass levels in any MAFAULDA session |
| A3 within-session calibration (reference) | done | 1.9-2.2 g (94-97 % right level) in five folders, 4.6 g in underhang ball fault (tachometer-affected) |
| A4 weighted median of channels (pre-registered on overhang) | done, FAIL | overhang 14.6 g |
| A5 screened estimator, biweight c = 12 selected on the development set (pre-registered on overhang) | done, FAIL by 0.79 g | overhang 3.79 g (90 % right level; outer race 2.17 g, cage 4.14 g, ball 5.42 g), five times below the joint calibration; healthy sessions 1.68 g against 1.70 g; it rejects the anomalous overhang radial channel in 99 % of the overhang ball-fault runs. Remaining error: the larger masses of overhang ball fault (35 g estimated 39 g) |
| B. Phase-free physics prior for speed extrapolation (pre-registered) | done, FAIL | outer bands: hold 14.3 / 1.65 g, physics w^4 / w^2 15.5 / 1.21 g, local log-slope 12.6 / 1.01 g (low band 11.8-20.2 Hz / high band 51.3-60.5 Hz). Above the resonances the mass-controlled w^2 law extrapolates; below about 20 Hz, where the modal fits put resonances, nothing does |
| Misalignment (2X, horizontal vs vertical, offset in mm) | planned | |
| Bearing faults (envelope order spectra; BPFO 2.998 and BPFI 5.002 are not resolvable from 3X and 5X in 5 s) | planned | |
| Literature: Shen et al. 2023 (HNN), Rigas et al. (KAN, arXiv 2412.01322), Sanami & Aghdam 2026 (inverse PINN, DOI to obtain), leakage-free benchmark (SBC BRESCI) | partly read | |

**Criteria of steps A and B (written 2026-11-04, before the bearing folders were opened):**

- A1 cross-session transfer: the phase-free calibration fitted on normal + imbalance estimates the added mass (0, 6,
  20, 35 g) of every run of the bearing folders with MAE <= 3 g (reported per folder and fault).
- A2 phase reference: inside each bearing folder, the angle of the free complex unbalance of 6, 20 and 35 g spans at
  most 10 deg; otherwise the phase drift of the imbalance sessions recurs.
- A3 within-session reference: leave-one-run-out inside each bearing folder with the same model, to separate the
  cost of changing session from the cost of the model.
- B speed extrapolation: continuing the phase-free calibration outside the training band with the physical power
  laws of an unbalance response (acceleration ~ w^4 below the resonances, ~ w^2 above them) brings the error of the
  two outer held-out speed bands to <= 4 g (it is 7-8 g when the calibration is held constant outside its band);
  compared with continuing the local log-slope of the data.

- A4 (written 2026-11-04 after the underhang folders, before the overhang folders were opened): the channel-robust
  estimator (weighted median of the per-channel phase-free mass estimates, weights from the calibration residuals and
  the channel sensitivity) brings A1 on the overhang folders to MAE <= 3 g, and it is at least as accurate as the
  weighted mean where no channel is abnormal.
- A5 (written 2026-11-04, after the underhang folders, before the overhang folders were opened; development set =
  calibration sessions + underhang, confirmation set = overhang): the screened estimator
  (`influence.ScreenedEstimator`: per-channel estimates with their joint-least-squares weights; distances
  standardised by the spreads measured in cross-validation on the calibration sessions; Tukey-biweight M-estimate
  of the common mass started from the unweighted median, its constant set at the 99.5 % quantile of the
  standardised calibration errors; a channel with zero weight is flagged) gives MAE <= 3 g on the overhang folders
  and stays within 0.2 g of the joint weighted estimate on the calibration sessions. Versions tried on the
  development set only, in order: weighted median (a dominant faulty channel became the centre), unweighted median
  (+0.86 g on healthy sessions), biweight with the normal-theory constant 4.685 (+0.78 g: the errors are
  heavy-tailed). Constant selected on the development set by the smallest worst-case MAE over the grid
  4.685-48 (calibration cross-validation and the three underhang folders): c = 12 (worst case 3.03 g; calibration
  1.68 g against 1.70 g for the joint estimate).

**Venue if the conditions are met:** Mechanical Systems and Signal Processing, Measurement, IEEE Trans.
Instrumentation and Measurement.

## P2 -- Process, sensor or model? Physics-residual diagnosis on a real PV microgrid

**Question.** Do whitened physics residuals with a likelihood ratio per hypothesis tell process faults from sensor
faults from a fast model outside its domain on laboratory data, not only in simulation?

**Data.** Simulated DC microgrid (done, `pinneapple_systems.digital_twin.dc_microgrid`); GPVS-Faults (Bakdi et al.,
Mendeley Data, DOI 10.17632/n76t439f65.1): grid-connected PV system in the laboratory, faults in the array, the
inverter, a feedback sensor, the grid and the MPPT controller.

| Step | Status | Result |
|---|---|---|
| Simulated four-bus DC microgrid twin | done | 80/80 controlled cases right (kind and target), 1 case with a false alarm; one confusable pair (joints next to bus 2, 25 % of operating points); PINN fast model 1.4 sigma with 8 labels against 13.4 sigma for the same network without physics |
| GPVS-Faults: signals, residuals that the measured quantities allow, benchmark | planned | |

**Venue if the conditions are met:** IEEE Trans. Industrial Electronics, IEEE Trans. Industrial Informatics,
International Journal of Electrical Power and Energy Systems.

## P3 -- COMFAULDA: combined faults recognised from single faults

**Question.** Trained on single faults only, can a phase-free physical representation recognise and size the
components of combined faults (unbalance + misalignment, two misalignments) that were never seen?

**Data.** COMFAULDA (Zenodo 8208454, CC BY 4.0, 23 GB, 2162 runs, 7 scenarios, 12-60 Hz).

| Step | Status | Result |
|---|---|---|
| Check its tachometer phase consistency and whether its bench matches MAFAULDA | planned | |

**Venue if the conditions are met:** Mechanical Systems and Signal Processing, Reliability Engineering & System
Safety.

## Session log

- 2026-11-03: DC microgrid twin (simulated); MAFAULDA unbalance pilot, NO GO for phase-referenced inversion.
- 2026-11-04: envelope and order spectra added to the MAFAULDA features; robust tachometer; steps A (cross-session, six bearing folders) and B (speed extrapolation) run against their pre-registered criteria: A1, A4, A5 and B fail, A2 shows the phase drift in every session; the screened estimator divides the cross-session error by five.
- Next: re-run the development results on the features of the corrected tachometer (pipeline running); misalignment (2X); P2 data (GPVS-Faults).
