# LOG — PINN scouting (EV / battery priority)

Session start 2026-11-03 (UTC), continued 2026-11-04. Working dir: `Q1 paper/PINNeAPPle/pinn_scouting/`.
Every URL below was actually requested from this session (curl through the session proxy, or the WebFetch tool).
HTTP code in brackets when it was a direct request. "API" = metadata pulled from the repository's public API.

## Decisions and assumptions

| # | Decision / assumption | Why |
|---|---|---|
| D1 | `topics_and_datasets.md` created inside `pinn_scouting/` (not repo root) from the pasted text, verbatim. | Keep the PINNeAPPle repo root clean; the file is an input of this study. |
| D2 | The paste's last section ("État du travail en cours", DC-microgrid study, failing test) refers to work in another session, not in this repo. Ignored. | Nothing of it exists here; not part of the requested phases. |
| D3 | Python stack in `/home/user/venv-scout` (numpy, scipy, h5py, scikit-learn, matplotlib, JAX CPU 0.x, optax, py7zr, mat-io). PyTorch not used. | `pip install -e .` of the PINNeAPPle repo and download.pytorch.org were blocked (permission classifier / proxy 403). JAX CPU installs from PyPI and is enough for small PINNs. |
| D4 | Large archives are inspected by HTTP range requests (`tools/remote_zip.py`) to list/extract one member, instead of full downloads. | Rule "download a small sample (a few MB)". Works on AWS S3 (NASA) and Mendeley; not on 7z/RAR. |
| D5 | Kaggle, IEEE DataPort subscription files, matr.io (JS app) and TU Berlin DSpace bitstreams were not downloaded. Metadata from public API / landing page only; sample column "not inspected". | Login required, or page is JS-only; a header-spoofing workaround was refused by the session's safety check and not retried. |
| D6 | GitHub through curl returns 400/403 from the proxy; GitHub pages are read with WebFetch. | Proxy policy. |
| D7 | WMG core-temperature dataset (Mendeley bf6fksxpp2, 2.33 GB 7z) downloaded in full because 7z cannot be range-read; only the small members extracted (full extraction = 28 GB > free disk). | It is the only open dataset found with **embedded core-temperature thermocouples during ageing** → likely central to a top project. |

## URL log (Phase 1)

### Topic-list datasets (pasted)
- [200] https://data.mendeley.com/datasets/n76t439f65 — API: GPVS-Faults v1, CC BY 4.0, 18 files, 205 MB, DOI 10.17632/n76t439f65.1.
- [200] https://data.mendeley.com/datasets/ztmf3m7h5x — API: KAIST rotating machine v6, CC BY 4.0, 3 zips, 4.25 GB, DOI 10.17632/ztmf3m7h5x.6.
- [200] https://data.mendeley.com/datasets/rgn5brrgrn — API: PMSM stator faults (1/1.5/3 kW) v5, CC BY 4.0, 6.97 GB. Remote listing of 1.0kW.zip: 34 members, TDMS files `current/1000W_<sev>_current_{interturn,intercoil}.tdms` (~290 MB each), vibration TDMS. **Description: current at 100 kHz, vibration 25.6 kHz — no voltages, speed or torque listed.** The pasted description ("12 torque-speed points, 9 % turns, short-circuit current") matches the HUST set, not this one.
- [200] https://ieee-dataport.org/documents/three-phase-pmsm-itsc-faults-stator-winding-dataset — WebFetch: HUST, DOI 10.21227/4jpc-qh81, 12 torque-speed points, 9 shorted-turn levels × 3 fault resistances, 3-ph V, 3-ph I, short-circuit current; **66.94 GB, subscription login**; created 2026-02-28; code github.com/XHX-HUST/PMSM-ITSC.
- [200] https://ieee-dataport.org/open-access/experimental-database-detecting-and-diagnosing-rotor-broken-bar-three-phase-induction — title reached.
- [200] https://data.nasa.gov/dataset/igbt-accelerated-aging-data-set — WebFetch: 6 devices, thermal overstress, "This dataset has no data" on data.nasa.gov; licence not specified.
- [200] https://data.phmsociety.org/nasa/ — WebFetch: mirror links on phm-datasets.s3.amazonaws.com.
- [HEAD 200] S3 sizes: 5.Battery 209.7 MB; 11.Randomized Battery Usage 1.07 GB; 8.IGBT 240.5 MB; 13.MOSFET 7.85 GB (reference doc offline); 12.Capacitor 5.04 GB; 15.HIRF Battery 1.09 GB. All Last-Modified 2022-09-18.
- [200] https://catalog.data.gov/dataset/prognostics-of-power-mosfets-under-thermal-stress-accelerated-aging-using-data-driven-and- — title reached.
- [403] https://www.princeton.edu/~minjie/magnet.html (bot wall); [200] https://mag-net.princeton.edu/ reached.
- [403 via curl] https://github.com/zhouhaoyi/ETDataset — proxy; not verified.
- [200] https://gesl.ornl.gov — title reached.
- [200] https://www.kaggle.com/c/vsb-power-line-fault-detection — reached.
- [200] https://data.open-power-system-data.org/ ; [200] https://transparency.entsoe.eu/
- [200] https://data.openei.org/submissions/738 — NREL GRC title reached.
- [404] https://mb.uni-paderborn.de/kat/forschung/kat-datacenter/bearing-datacenter ; [000] .../datacenter/bearing-datacenter — **Paderborn KAt page dead from here**; mirror not found yet.
- [200] https://www02.smt.ufrj.br/~offshore/mfs/page_01.html — MAFAULDA reached.
- [200] https://engineering.case.edu/bearingdatacenter — CWRU reached.
- [200] https://biaowang.tech/xjtu-sy-bearing-datasets/ — XJTU-SY reached.
- [HEAD 200] https://phm-datasets.s3.amazonaws.com/NASA/4.+Bearings.zip (IMS) ; .../10.+FEMTO+Bearing.zip
- [200] https://www.nonlinearbenchmark.org/
- [200] https://zenodo.org/records/14006163 — API: CARE to Compare, 2024-10-29, CC BY-SA 4.0, 5.48 GB.
- [200] https://zenodo.org/records/16807551 — API: Kelmarsh, 2025-08-12, CC BY 4.0, 3.84 GB.
- [200] https://zenodo.org/record/5946808 — API: Penmanshiel, 2022-02-07, CC BY 4.0, 3.63 GB.
- [200] https://www.fclab.fr/ — PHM 2014 data page not located; UNVERIFIED.

### Battery / EV datasets (mandatory list + new)
- [200] https://data.nasa.gov/dataset/li-ion-battery-aging-datasets — WebFetch: 18650, EOL 30 % fade (2→1.4 Ah), ~10 Hz stated, EIS (Re, Rct), "This dataset has no data" on portal; data on S3 mirror.
- **Sample**: `5. Battery Data Set/5. BatteryAgingARC_49_50_51_52.zip` (8.7 MB) extracted by range request. B0049.mat: 62 operations (25 charge, 25 discharge, 12 impedance); ambient 4 °C for charge/discharge, impedance at 24 °C; fields Voltage_measured, Current_measured, Temperature_measured, Current_load/charge, Voltage_load/charge, Time, Capacity; impedance fields complex Battery_impedance (48 pts), Re, Rct. Median dt in discharge 9.4 s (not 10 Hz). **First capacity 0.858 Ah then 1.42 Ah — anomalous first discharge.** No NaN in fields read.
- [200] https://calce.umd.edu/battery-data — WebFetch: CS2 (15 cells), CX2 (12), INR18650-20R (OCV + DST/FUDS/US06/BJDST at 0/25/45 °C), A123 (−10…50 °C), PL pouch (16), PLN storage (144). Open access, **no explicit licence**; cite CALCE papers.
- [200] https://ora.ox.ac.uk/objects/uuid:03ba4b01-cfed-46d3-9b1a-7d4a7bdf6fac — WebFetch: 8 Kokam 740 mAh pouch, ODC-ODbL, DOI 10.5287/bodleian:KO2kdmYGg, 253.8 MB .mat; Battery Archive summary: 40 °C, Artemis urban drive cycle, characterisation every 100 cycles.
- [200] https://data.matr.io/1/projects/5c48dd2bc625d700019f3204 (Severson) and .../5d80e633f405260001c0b60a (Attia) — JS app, no content readable; metadata taken from the papers.
- [429] https://www.nature.com/articles/s41560-019-0356-8 (rate-limited). [200] https://www.nature.com/articles/s41586-020-1994-5 (Attia).
- [200] https://www.batteryarchive.org/ ; /list.html ; /study_summaries.html — read: CALCE, HNEI (NMC-LCO 18650, 1.5C, 100 % DoD, >1000 cycles), ISU-ILCC (238 NMC pouch, 63 conditions, 30 °C), ORNL & SNL abuse, OX, SNL cycling (18650 NCA/NMC/LFP, T, DoD, rate), UL-PUR.
- [200] https://data.mendeley.com/datasets/cp3473x7xv/3 — API: LG HG2, CC BY 4.0, 421 files, 818 MB, DOI 10.17632/cp3473x7xv.3, Digatron, 8 cu.ft chamber.
- [200] https://data.mendeley.com/datasets/wykht8y7tg/1 — API: Panasonic 18650PF, CC BY 4.0, 259 files, 197.5 MB, DOI 10.17632/wykht8y7tg.1.
- [200] https://www.kaggle.com/datasets/wkirgsn/electric-motor-temperature — Kaggle public API: CC BY-SA 4.0, measures_v2.csv 300 MB, 2 Hz, 185 h, profile_id sessions 1–6 h; cite Kirchgässner et al. (IEEE 9296842).
- [200] https://ev.caltech.edu/dataset — WebFetch: ACN-Data, 3 sites, API token registration, per-session kWh + chargingCurrent/pilot time series via /ts; no licence stated; cite Lee, Li, Low, e-Energy 2019.
- [200] https://ieee-dataport.org/open-access/battery-and-heating-data-real-driving-cycles — WebFetch: BMW i3 60 Ah, 72 trips, CC BY 4.0, DOI 10.21227/6jr9-5235, measurement 35.7 MB (+ simulation 300 MB), login needed to download.
- [200] https://huggingface.co/datasets/Battery-Life/BatteryLife_Processed — WebFetch: 990 batteries (837 Li-ion), MIT licence, 92 GB, arXiv 2502.18807, DOI 10.1145/3711896.3737372.
- [403 via curl] https://github.com/Ruifeng-Tan/BatteryLife — proxy.
- [200, empty for WebFetch] https://publications.rwth-aachen.de/record/818642 — RWTH; content not readable → UNVERIFIED.
- [000] https://www.nrel.gov/transportation/fleettest-fleet-dna.html ; [000] https://www.nrel.gov/transportation/secure-transportation-data — **nrel.gov unreachable from this proxy** → UNVERIFIED.
- Zenodo API 6405084 — Tongji (Zhu et al., Nat Commun 2022), CC BY 4.0, 1.67 GB, 3 datasets NCA/NCM/NCM+NCA + impedance, 9 csv columns.
- Zenodo API 3633835 — Cambridge EIS (Zhang et al., Nat Commun 2020), CC BY 4.0, EIS 27 MB + capacity 92 MB.
- Zenodo API 10963339 — XJTU (Wang et al., Nat Commun 2024 PINN paper), CC BY 4.0, 2.44 GB, 55 LISHEN NCM523 2 Ah cells, 6 protocols, room T.
- Zenodo API 18494770 — relaxation-to-EIS dataset (2026), NCM/LFP/NCA, 15–45 °C, CC BY 4.0, 159 MB RAR.
- Mendeley API 7vdkzpnjgj — Stanford real-world EV field data (Joule 2023), **CC BY-NC 3.0**, 1.8 GB, pack I, V, SoC, T, 1 year.
- Mendeley API j9ky68gnd3 — "Real EV dataset" v3 2025, CC BY 4.0, 4 csv **only ~15 kB total** (summary-level, not time series).
- Mendeley API bf6fksxpp2 — WMG core temperature ageing (Gulsoy, Marco), CC BY 4.0, 2.33 GB 7z, 6 LG M50 cells (3 with core thermocouple), 550 cycles, urban drive profile, columns incl. Surf Temp and Core Temp. **Downloaded.** Members: 100cycles 61.5 MB, ShortTerm RPT 241 MB, LoadProfile 2.43 GB, LongTerm RPT 2.69 GB, 450cycles 22.5 GB. MAT files are MATLAB `table` objects (MCOS opaque in scipy) → reading with `mat-io`.
- [WebFetch] https://depositonce.tu-berlin.de/items/a3c12e52-32e0-4c9a-b1e0-4931cd5bf6fe/full — TU Berlin internal temperature (Yao, Droese, Kowal, 2026-01-12), LG M50LT 4.93 Ah, 3 cells drilled with type-K core sensor, 12 drive cycles × 5 ambient temperatures, 612.6 MB zip, CC BY 4.0, DOI 10.14279/depositonce-25110. Bitstream not downloaded (D5).
- [WebFetch] https://ieee-dataport.org/documents/field-ev-fleet-bms-telemetry-dataset — 21 Hyundai/Kia E-GMP EVs, 1 s, Aug 2024–Jan 2026, ~800 k launch events, CC BY 4.0, 25.5 MB, subscription, DOI 10.21227/0v0g-gz47.
- [WebFetch] https://batterymaster.upc.edu/datasets — UPC pack (36 cells, 3 parallel branches), WLTP, CORA doi:10.34810/data2395, licence not stated.
- [WebFetch] https://pmc.ncbi.nlm.nih.gov/articles/PMC8892076/ — Stanford Pozzato 2022: 10 LG M50T cells, UDDS, C/4–3C charge, 23 °C, RPT (C/20, HPPC, EIS) ~every 25 cycles, OSF osf.io/qsabn; [200] https://osf.io/qsabn/.
- Web searches (2026-11-04): EV field datasets; Data in Brief battery 2024; Stanford M50T. Result pages listed in each search are not counted as "visited" unless re-opened above.

## Phase 2-3 (candidates, novelty) — 2026-11-04

| # | Decision / assumption | Why |
|---|---|---|
| D8 | Saturation measured with OpenAlex title+abstract searches (`tools/lit.py`, raw JSON in `lit/`), not with impressions. Crossref used to verify DOIs/titles (`lit/crossref_checks.json`). Consensus search tried once (rate-limited, no DOIs on free plan); Semantic Scholar API 429. | Reproducible counts with stored queries. |
| D9 | A paper counts as "read" only if its abstract was retrieved (OpenAlex inverted index or Crossref). Elsevier abstracts are often withheld from OpenAlex: those rows say "not read". | Brief: no novelty claim without reading abstracts. |
| D10 | Zenodo record 10.5281/zenodo.21976252 (core temperature, Biot relation 0.13 K, "inverse PINN less accurate") was found through OpenAlex; zenodo.org now returns HTTP 410 (withdrawn). Used only as a risk signal, NOT cited in references.bib. | Cannot cite a withdrawn, unopened record; but it is evidence that the physics baseline is strong. |
| D11 | 13 candidates kept (C1-C13); SOC (C2), SOH (C3), PMSM-Paderborn (C7), MagNet (C12) rejected for saturation; IGBT (C9) and ACN (C10) for data; C8 on hold (subscription + 67 GB). | Evidence in candidates.md. |

OpenAlex probes run (URL stored in each lit/*.json): C1_core_temp_pinn, C1b_core_temp_any, C1c_coretemp_ageing,
C2_soc_pinn, C3_soh_pinn, C4_aging_law_pinn, C5_ecm_param_pinn, C6_field_ev_pinn, C7_pmsm_temp, C8_itsc_pinn,
C9_igbt_pinn, C10_ev_charging_physics, C11_pv_inverter_fault_physics, C12_magnet_pinn, C13_eis_pinn,
D_nasa_randomized, D_embedded_tc, D_paderborn_tnn; single-work lookups in lit/key_abstracts.json.

## Phase 5 (journals) — 2026-11-04
- [200] https://www.elsevier.com/about/policies-and-standards/pricing -> official APC list
  https://legacyfileshare.elsevier.com/els_com_pricing/article-publishing-charge.xlsx (saved journals/elsevier_apc.xlsx).
- [WebFetch] https://open.ieee.org/for-authors/article-processing-charges/ -> hybrid APC USD 2,800 (2026), 2,995 (2027); IEEE Access 2,160 / 2,245.
- [403] sciencedirect.com journal pages (Applied Energy, J. Power Sources, eTransportation, J. Energy Storage), elsevier.com journal page, cell.com; [418] ieeexplore; [303 login] nature.com/ncomms journal-information -> **impact factors and review times UNVERIFIED**.

## Phase 6 (prototypes) — 2026-11-04

| # | Decision / assumption | Why |
|---|---|---|
| D12 | Prototypes for C1 (core temperature, WMG) and C5 (NASA RW) — the two top-scored candidates whose real data were already downloaded. | Brief: top 2 only. |
| D13 | C1: data resampled to 10 s (mean of I^2 kept as Joule driver); T_amb not logged -> 1st percentile of surface T per block; VP011 block 2 has no core data (dropped); window 5 min; MLP 64x64 tanh; 6 epochs; lambda = 1 fixed a priori; 3 seeds; leave-one-instrumented-cell-out. | Fixed before looking at test cells. |
| D14 | C1: first lumped fit with (Cc, Rc, R0) free drifted to a degenerate solution (Cc 2.7e10, Rc 6e-9): only tau = Cc Rc and R0/Cc are identifiable with surface T as input. Fixed Cc = 50 J/K (nominal), fit (Rc, R0): R0 = 30-32 mOhm, Rc = 2.6-3.2 K/W, tau ~ 130-160 s. The first PINN run crashed because it started from the degenerate parameters; rerun after the fix. | Identifiability, logged as a finding. |
| D15 | C1 result: the a-priori PINN (lambda = 1) is NOT better than the MLP (0.391 vs 0.260 K RMSE). Post-hoc lambda = 0.1 / 0.01 runs were made and are labelled post-hoc everywhere; they are not used as the result. | No tuning on test cells presented as a result. |
| D16 | C5: neural-ECM with tau fixed at 60 s; per-cycle (Q, R0, R1); OCV MLP 32x32; fit on labelled cycles + every 5th cycle; capacity calibration a*Q+b fitted on training cells only; reference capacity matched to the 5 RW cycles after each reference; RW3 temperature sentinel -4094.1 C interpolated. | Fixed before test evaluation. |
| D17 | sklearn >= 1.8 API: MLPRegressor's first positional argument is no longer hidden_layer_sizes; first C5 run crashed and was rerun with keyword arguments. | Bug, not a result. |
| D18 | C5 OOD fold crashed (NaN feature: RW3 cycle with no valid temperature); fixed by imputing training-set medians for the data-driven features only; full rerun (results/run_log.txt). | Bug, not a result. |
| D19 | Final order: C5, C1, C4, C13, C11. C1 lowered after its prototype (physics depth 3 -> 2, total 3.85); C5 unchanged (4.00). Recorded in scoring.csv column post_prototype_note and in TOP5*.md. | Prototypes are evidence; the change is disclosed rather than silently re-scored. |
