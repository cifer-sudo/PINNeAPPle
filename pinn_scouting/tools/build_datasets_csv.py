"""Build datasets.csv from the verification notes in LOG.md (one dict per dataset).

Conventions: a field nobody could verify is "UNVERIFIED"; "n/s" = not stated on the page that was reached.
verification: VERIFIED-SAMPLE (page reached and a real file opened here), VERIFIED-PAGE (landing page/API reached,
no file opened), PARTIAL (page reached but key metadata missing), UNVERIFIED (page not reached).
"""
import csv

COLS = ["name", "domain", "topics", "url", "license", "access", "size", "sampling_rate", "measured_variables",
        "operating_conditions", "n_units", "labels", "ground_truth", "year", "papers_doi", "known_issues",
        "verification", "sample_inspected", "citation_to_use"]

R = []


def add(**kw):
    R.append({c: kw.get(c, "UNVERIFIED") for c in COLS})


# ------------------------------------------------------------------ batteries: cell level (lab)
add(name="NASA PCoE Li-ion Battery Aging (B0005-B0056)", domain="battery", topics="42",
    url="https://data.nasa.gov/dataset/li-ion-battery-aging-datasets ; mirror https://phm-datasets.s3.amazonaws.com/NASA/5.+Battery+Data+Set.zip",
    license="not specified on data.nasa.gov (US Gov work)", access="open (S3 mirror)", size="209.7 MB zip (6 inner zips)",
    sampling_rate="~10 Hz stated; median dt 9.4 s in B0049 discharge (measured here)",
    measured_variables="Voltage_measured, Current_measured, Temperature_measured, Current_load/charge, Voltage_load/charge, Time; per discharge Capacity; EIS: complex Battery_impedance (48 pts), Rectified_Impedance, Re, Rct",
    operating_conditions="CC 1.5 A charge to 4.2 V CV; discharges at different loads to varying cut-offs (some below 2.7 V); ambient 4, 24, 43 C groups (B0049: 4 C cycling, EIS at 24 C)",
    n_units="count UNVERIFIED; 6 inner zips (FY08Q4, 25-28, 25-44, 45-48, 49-52, 53-56); B0049-52 inspected", labels="capacity per discharge, Re, Rct (EOL 30 % fade)",
    ground_truth="lab measurement", year="2007-2010 (portal modified 2022)",
    papers_doi="Saha & Goebel 2007 NASA Ames (no DOI checked)",
    known_issues="Anomalous first discharge (B0049: 0.858 Ah then 1.42 Ah); few cycles at 4 C (25 discharges); irregular protocols between groups; very heavily used (saturated)",
    verification="VERIFIED-SAMPLE", sample_inspected="5.BatteryAgingARC_49_50_51_52.zip (8.7 MB): B0049.mat 62 operations, no NaN",
    citation_to_use="B. Saha and K. Goebel, Battery Data Set, NASA Ames Prognostics Data Repository")
add(name="NASA PCoE Randomized Battery Usage (RW1-RW28)", domain="battery", topics="42",
    url="https://phm-datasets.s3.amazonaws.com/NASA/11.+Randomized+Battery+Usage+Data+Set.zip",
    license="not specified (US Gov work)", access="open (S3 mirror)", size="1.07 GB zip (7 inner zips, 59-446 MB)",
    sampling_rate="1 s in random-walk steps (measured)",
    measured_variables="voltage, current, temperature, time, relativeTime, step type/comment",
    operating_conditions="charge 2 A CC-CV to 4.2 V; random-walk discharge 0.5-5 A, new set-point every 1 min, to 3.2 V; distributions uniform / skewed high / skewed low; room T and 40 C; reference 1 A discharge, 15 W discharge and 1 A pulsed load (10 min on / 20 min off) every 50 RW cycles",
    n_units="28 cells (7 groups of 4); RW25-28 inspected",
    labels="reference capacity every 50 RW cycles (RW25: 13 values 2.133 -> 1.675 Ah, computed here), pulse response every 50 cycles, 15 W runtime",
    ground_truth="lab measurement", year="2014 (files 2015)",
    papers_doi="Bole, Kulkarni, Daigle 2014 PHM Society, 10.36001/phmconf.2014.v6i1.2490",
    known_issues="Cell temperature swings 33-58 C at 40 C ambient (surface sensor); capacity only every 50 cycles (sparse labels); no EIS",
    verification="VERIFIED-SAMPLE", sample_inspected="RW_Skewed_High_40C (59 MB): RW25.mat 20 508 steps, 600 RW cycles, 98.8 days, no NaN in T",
    citation_to_use="Bole, Kulkarni, Daigle, PHM 2014, doi:10.36001/phmconf.2014.v6i1.2490")
add(name="CALCE CS2 / CX2 (prismatic LCO)", domain="battery", topics="42", url="https://calce.umd.edu/battery-data",
    license="open access, no explicit licence", access="open", size="n/s", sampling_rate="n/s",
    measured_variables="Arbin logs (V, I, capacity); CX2-4 thermocouple", operating_conditions="CS2: 0.5C/1C cycling, partial cycling, variable cut-off; CX2: 0.5C, 3C, pulsed, T steps 25-55 C",
    n_units="CS2 15 cells, CX2 12 cells", labels="capacity vs cycle", ground_truth="lab measurement", year="2011-2013",
    papers_doi="He et al. J. Power Sources 196 (2011) 10314, 10.1016/j.jpowsour.2011.08.040",
    known_issues="Mixed testers (Arbin xlsx vs CADEX txt); per-cell heterogeneous protocols; heavily used",
    verification="VERIFIED-PAGE", sample_inspected="no", citation_to_use="He et al. 2011 (doi above) + CALCE page")
add(name="CALCE INR18650-20R and A123 drive cycles / OCV", domain="battery", topics="42", url="https://calce.umd.edu/battery-data",
    license="open access, no explicit licence", access="open", size="n/s", sampling_rate="n/s",
    measured_variables="terminal voltage, current, capacity (variables not listed exhaustively)",
    operating_conditions="INR: C/20 OCV and incremental OCV at 0/25/45 C; DST, FUDS, US06, BJDST at 50 % and 80 % SOC start; A123: -10..50 C, DST/US06/FUDS",
    n_units="INR 3 samples (SP1-SP3); A123 n/s", labels="SOC via Coulomb counting", ground_truth="lab measurement", year="2014-2016",
    papers_doi="Zheng et al. Appl. Energy 183 (2016) 513 (DOI not checked)", known_issues="Single cell per condition; heavily used for SOC",
    verification="VERIFIED-PAGE", sample_inspected="no", citation_to_use="CALCE references listed on the page")
add(name="CALCE PL pouch partial-SOC + PLN storage", domain="battery", topics="42", url="https://calce.umd.edu/battery-data",
    license="open access, no explicit licence", access="open", size="n/s", sampling_rate="n/s",
    measured_variables="discharge capacity, CCV, OCV; storage: capacity and impedance",
    operating_conditions="PL: 8 SOC windows x 2 rates; PLN: 0/50/100 % SOC x -40/-5/25/50 C storage", n_units="PL 16; PLN 144",
    labels="capacity fade (cycle and calendar)", ground_truth="lab measurement", year="2016 (PL)",
    papers_doi="Saxena, Hendricks, Pecht, J. Power Sources 327 (2016) 394 (DOI not checked)", known_issues="PLN chemistry not stated",
    verification="VERIFIED-PAGE", sample_inspected="no", citation_to_use="Saxena et al. 2016")
add(name="Oxford Battery Degradation Dataset 1", domain="battery", topics="42",
    url="https://ora.ox.ac.uk/objects/uuid:03ba4b01-cfed-46d3-9b1a-7d4a7bdf6fac", license="ODC-ODbL", access="open",
    size="253.8 MB .mat", sampling_rate="n/s", measured_variables="per Battery Archive: V, I, T, charge (readme not opened)",
    operating_conditions="40 C, CC-CV charge, Artemis urban drive-cycle discharge, characterisation every 100 cycles",
    n_units="8 Kokam 740 mAh pouch", labels="capacity + pseudo-OCV every 100 cycles", ground_truth="lab measurement", year="2017",
    papers_doi="dataset DOI 10.5287/bodleian:KO2kdmYGg; Birkl PhD thesis", known_issues="Single temperature; 8 cells only",
    verification="VERIFIED-PAGE", sample_inspected="no", citation_to_use="Birkl, Oxford Battery Degradation Dataset 1, doi:10.5287/bodleian:KO2kdmYGg")
add(name="Toyota-MIT-Stanford fast charge (Severson 2019)", domain="battery", topics="42",
    url="https://data.matr.io/1/projects/5c48dd2bc625d700019f3204", license="UNVERIFIED (JS page not readable)", access="open (download in-app)",
    size="UNVERIFIED", sampling_rate="UNVERIFIED", measured_variables="from paper: V, I, T, capacity, internal resistance per cycle",
    operating_conditions="from paper: 72 fast-charging policies, 30 C chamber", n_units="124 LFP/graphite A123 cells (paper)",
    labels="cycle life, capacity per cycle", ground_truth="lab measurement", year="2019",
    papers_doi="10.1038/s41560-019-0356-8 (Crossref-checked)", known_issues="Most-used early-life dataset (saturated); LFP only; batch 2 cells with protocol changes (reported in literature, not checked here)",
    verification="PARTIAL", sample_inspected="no", citation_to_use="Severson et al., Nat. Energy 4 (2019), doi:10.1038/s41560-019-0356-8")
add(name="MIT-Stanford-TRI closed-loop (Attia 2020)", domain="battery", topics="42",
    url="https://data.matr.io/1/projects/5d80e633f405260001c0b60a", license="UNVERIFIED", access="open (in-app)", size="UNVERIFIED",
    sampling_rate="UNVERIFIED", measured_variables="UNVERIFIED (same platform as Severson)", operating_conditions="fast-charge protocol optimisation (paper)",
    n_units="UNVERIFIED", labels="cycle life", ground_truth="lab measurement", year="2020", papers_doi="10.1038/s41586-020-1994-5 (Crossref-checked)",
    known_issues="Short runs (early-cycle) by design", verification="PARTIAL", sample_inspected="no",
    citation_to_use="Attia et al., Nature 578 (2020), doi:10.1038/s41586-020-1994-5")
add(name="Sandia National Labs cycling (Preger 2020) via Battery Archive", domain="battery", topics="42",
    url="https://www.batteryarchive.org/study_summaries.html", license="Battery Archive code of conduct; cite article", access="open",
    size="UNVERIFIED", sampling_rate="UNVERIFIED", measured_variables="Battery Archive standard: V, I, T, capacity, energy per cycle",
    operating_conditions="18650 NCA, NMC, LFP; temperature, DoD and discharge current varied; capacity check 0.5C every round",
    n_units="UNVERIFIED (paper)", labels="capacity, cycle", ground_truth="lab measurement", year="2020",
    papers_doi="10.1149/1945-7111/abae37 (Crossref-checked)", known_issues="Cycling 'still ongoing' at upload; check versions",
    verification="VERIFIED-PAGE", sample_inspected="no", citation_to_use="Preger et al., J. Electrochem. Soc. 167 (2020) 120532, doi:10.1149/1945-7111/abae37")
add(name="HNEI 18650 NMC-LCO via Battery Archive", domain="battery", topics="42", url="https://www.batteryarchive.org/study_summaries.html",
    license="Battery Archive code of conduct", access="open", size="UNVERIFIED", sampling_rate="UNVERIFIED",
    measured_variables="V, I, T, capacity (standard format)", operating_conditions="1.5C, 100 % DoD, room T, >1000 cycles",
    n_units="UNVERIFIED (batch)", labels="capacity", ground_truth="lab measurement", year="2018",
    papers_doi="Devie, Baure, Dubarry, Energies 11 (2018) 1031, 10.3390/en11051031 (Crossref)", known_issues="Single condition (variability study)",
    verification="VERIFIED-PAGE", sample_inspected="no", citation_to_use="Devie et al. 2018")
add(name="ISU-ILCC 238 NMC pouch (Li et al. 2024)", domain="battery", topics="42", url="https://www.batteryarchive.org/study_summaries.html",
    license="see group website", access="open", size="UNVERIFIED", sampling_rate="UNVERIFIED", measured_variables="UNVERIFIED",
    operating_conditions="30 C, 63 conditions (charge C-rate, discharge C-rate, DoD)", n_units="238", labels="capacity, life",
    ground_truth="lab measurement", year="2024", papers_doi="10.1016/j.xcrp.2024.101891 (Crossref)", known_issues="single temperature",
    verification="VERIFIED-PAGE", sample_inspected="no", citation_to_use="Li et al., Cell Rep. Phys. Sci. 2024")
add(name="Tongji NCA/NCM 18650 (Zhu et al. 2022)", domain="battery", topics="42", url="https://zenodo.org/records/6405084",
    license="CC BY 4.0", access="open", size="1.67 GB (3 zips + impedance)", sampling_rate="UNVERIFIED",
    measured_variables="9 csv columns incl. time/s, control/V/mA, voltage, current, capacity (per description); impedance raw + fit",
    operating_conditions="3 chemistries, several temperatures and charge/discharge rates (encoded in file names CYX-Y_Z)",
    n_units="UNVERIFIED (paper)", labels="capacity", ground_truth="lab measurement", year="2022",
    papers_doi="10.1038/s41467-022-29837-w (Crossref-checked)", known_issues="Used in Wang 2024 PINN benchmark (saturating)",
    verification="VERIFIED-PAGE", sample_inspected="no", citation_to_use="Zhu et al., Nat. Commun. 13 (2022) 2261, doi:10.1038/s41467-022-29837-w")
add(name="XJTU 55 NCM cells (Wang et al. 2024)", domain="battery", topics="42", url="https://zenodo.org/records/10963339",
    license="CC BY 4.0", access="open", size="2.44 GB", sampling_rate="UNVERIFIED", measured_variables="UNVERIFIED (cycling V, I, T)",
    operating_conditions="LISHEN NCM523 2 Ah; 6 charge/discharge protocols; room temperature", n_units="55",
    labels="capacity / SOH", ground_truth="lab measurement", year="2024", papers_doi="10.1038/s41467-024-48779-z (Crossref-checked)",
    known_issues="Comes with the reference PINN-SOH paper -> any SOH-PINN on it competes with a Nat. Commun. baseline",
    verification="VERIFIED-PAGE", sample_inspected="no", citation_to_use="Wang et al., Nat. Commun. 15 (2024) 4332, doi:10.1038/s41467-024-48779-z")
add(name="Cambridge EIS + capacity (Zhang et al. 2020)", domain="battery", topics="42", url="https://zenodo.org/records/3633835",
    license="CC BY 4.0", access="open", size="EIS 27 MB + capacity 92 MB", sampling_rate="EIS spectra per cycle",
    measured_variables="EIS spectra; capacity", operating_conditions="25/35/45 C (paper)", n_units="UNVERIFIED (paper)",
    labels="capacity, RUL", ground_truth="lab measurement", year="2020", papers_doi="10.1038/s41467-020-15235-7 (Crossref-checked)",
    known_issues="Small number of cells per temperature (paper)", verification="VERIFIED-PAGE", sample_inspected="no",
    citation_to_use="Zhang et al., Nat. Commun. 11 (2020) 1706")
add(name="RWTH Aachen ageing dataset", domain="battery", topics="42", url="https://publications.rwth-aachen.de/record/818642",
    license="UNVERIFIED", access="UNVERIFIED", size="UNVERIFIED", sampling_rate="UNVERIFIED", measured_variables="UNVERIFIED",
    operating_conditions="UNVERIFIED", n_units="UNVERIFIED", labels="UNVERIFIED", ground_truth="UNVERIFIED", year="UNVERIFIED",
    papers_doi="UNVERIFIED", known_issues="Page returned 200 but no readable content (JS); record id assumed, not confirmed",
    verification="UNVERIFIED", sample_inspected="no", citation_to_use="UNVERIFIED")
add(name="LG 18650HG2 (McMaster, Kollmeyer)", domain="battery", topics="42", url="https://data.mendeley.com/datasets/cp3473x7xv/3",
    license="CC BY 4.0", access="open", size="817.8 MB, 421 files (.mat)", sampling_rate="UNVERIFIED (not inspected)",
    measured_variables="from file names: drive cycles (Mixed1-8, UDDS, LA92, US06, HWFET), charges; tester V, I, T (description)",
    operating_conditions="3 Ah cell; 8 cu.ft chamber; -20..40 C (file names show 0 C etc.)", n_units="1 cell (new)",
    labels="SOC (Coulomb counting)", ground_truth="lab measurement", year="2020",
    papers_doi="dataset 10.17632/cp3473x7xv.3; Vidal et al. ITEC 2019 10.1109/itec.2019.8790543 (Crossref)",
    known_issues="Single cell -> no cell-to-cell split possible; heavily used for SOC (saturated)",
    verification="VERIFIED-PAGE", sample_inspected="no (file list via API)", citation_to_use="Kollmeyer et al., Mendeley Data v3, doi:10.17632/cp3473x7xv.3")
add(name="Panasonic 18650PF (Kollmeyer, UW-Madison)", domain="battery", topics="42", url="https://data.mendeley.com/datasets/wykht8y7tg/1",
    license="CC BY 4.0", access="open", size="197.5 MB, 259 files", sampling_rate="UNVERIFIED",
    measured_variables="drive cycles, pulse tests, charges (V, I, T, Ah)", operating_conditions="-20..25 C (description)", n_units="1 cell",
    labels="SOC", ground_truth="lab measurement", year="2018", papers_doi="dataset 10.17632/wykht8y7tg.1",
    known_issues="Single cell; saturated SOC benchmark", verification="VERIFIED-PAGE", sample_inspected="no",
    citation_to_use="Kollmeyer, Mendeley Data, doi:10.17632/wykht8y7tg.1")
add(name="Samsung INR18650-20R (CALCE)", domain="battery", topics="42", url="https://calce.umd.edu/battery-data",
    license="open access, no explicit licence", access="open", size="n/s", sampling_rate="n/s", measured_variables="V, I, capacity",
    operating_conditions="see CALCE INR row", n_units="3 samples", labels="SOC", ground_truth="lab measurement", year="2014-2016",
    papers_doi="see CALCE INR row", known_issues="same as CALCE INR row", verification="VERIFIED-PAGE", sample_inspected="no",
    citation_to_use="CALCE INR references")
add(name="BatteryLife (aggregated benchmark)", domain="battery", topics="42",
    url="https://huggingface.co/datasets/Battery-Life/BatteryLife_Processed", license="MIT (aggregate; underlying licences differ)",
    access="open", size="92 GB", sampling_rate="per source", measured_variables="uniform format of source datasets",
    operating_conditions="16+ sources; Li-ion, Zn-ion, Na-ion, CALB", n_units="990 (837 Li-ion)", labels="cycle life",
    ground_truth="lab measurement (aggregated)", year="2025", papers_doi="10.1145/3711896.3737372 (Crossref-checked); arXiv 2502.18807",
    known_issues="Aggregation inherits source issues; MIT licence on processed copy may conflict with source licences (e.g. NC)",
    verification="VERIFIED-PAGE", sample_inspected="no", citation_to_use="Tan et al., KDD 2025 + every source dataset used")
add(name="Stanford INR21700-M50T UDDS ageing (Pozzato 2022)", domain="battery", topics="42", url="https://osf.io/qsabn/",
    license="article CC BY; dataset licence not stated", access="open (OSF)", size="UNVERIFIED", sampling_rate="n/s",
    measured_variables="V, I, capacity, HPPC resistance, EIS 0.01 Hz-10 kHz at 20/50/80 % SOC, surface T (T-type)",
    operating_conditions="23 C; CC-CV charge C/4-3C; UDDS discharge 80->20 % SOC; RPT ~every 25 cycles", n_units="10 cells",
    labels="capacity, HPPC R, EIS", ground_truth="lab measurement", year="2022", papers_doi="10.1016/j.dib.2022.107995 (Crossref-checked)",
    known_issues="Single temperature; irregular RPT spacing per cell", verification="VERIFIED-PAGE", sample_inspected="no",
    citation_to_use="Pozzato, Allam, Onori, Data in Brief 41 (2022) 107995")
add(name="WMG core-temperature ageing (Gulsoy, Marco)", domain="battery", topics="42 (thermal)",
    url="https://data.mendeley.com/datasets/bf6fksxpp2/2", license="CC BY 4.0", access="open", size="2.33 GB 7z (28 GB extracted)",
    sampling_rate="1 Hz (measured: median dt 1000 ms)",
    measured_variables="Voltage [V] (0.01 V resolution), Current [A], Capacity [Ah], Surf Temp [C], Core Temp [C] (0.1 C resolution), step, status, cycle, time",
    operating_conditions="LG M50 21700 5 Ah; 25 C ambient (measured ~24-25 C start); ageing CC charge ~1.7 A / 5 A discharge, 100 + 450 cycles; urban drive load profile 45 min; RPTs",
    n_units="6 cells (3 with embedded core thermocouple VP010-012, 3 pristine VP016-018)",
    labels="core temperature (direct), capacity", ground_truth="lab measurement (embedded thermocouple)", year="2022 data / 2026 Mendeley v2",
    papers_doi="10.1016/j.est.2022.105260 (Crossref-checked)",
    known_issues="MATLAB table objects (need mat-io); VP011 core sensor sentinel -3276.8 C (dropout); temperature resolution 0.1 C; only one ambient; RPT table holds V,Q only; instrumentation changes the cell",
    verification="VERIFIED-SAMPLE", sample_inspected="100cycles_dataTable.mat converted: 6 cells x 5 blocks x ~300k samples; core 23.9-39.0 C, surface 23.9-37.4 C; NaN <0.02 %",
    citation_to_use="Gulsoy et al., J. Energy Storage 54 (2022) 105260 + Mendeley doi:10.17632/bf6fksxpp2.2")
add(name="TU Berlin internal temperature (Yao, Droese, Kowal 2026)", domain="battery", topics="42 (thermal)",
    url="https://depositonce.tu-berlin.de/items/a3c12e52-32e0-4c9a-b1e0-4931cd5bf6fe", license="CC BY 4.0 (+ item licence file)",
    access="open", size="612.6 MB zip", sampling_rate="UNVERIFIED", measured_variables="surface and internal temperature (other channels not listed)",
    operating_conditions="LG M50LT 4.93 Ah; 12 drive cycles x 5 ambient temperatures", n_units="3 cells (drilled, type-K core sensor)",
    labels="core temperature (direct)", ground_truth="lab measurement (inserted sensor)", year="2026", papers_doi="dataset 10.14279/depositonce-25110; paper not named",
    known_issues="Drilling alters cell; V/I channels not confirmed; file not downloaded here (D5)", verification="VERIFIED-PAGE", sample_inspected="no",
    citation_to_use="Yao, Droese, Kowal, DepositOnce 2026, doi:10.14279/depositonce-25110")
add(name="Relaxation-EIS dataset (Chen 2026)", domain="battery", topics="42", url="https://zenodo.org/records/18494770",
    license="CC BY 4.0", access="open", size="158.9 MB RAR", sampling_rate="UNVERIFIED", measured_variables="EIS and relaxation voltage",
    operating_conditions="NCM, LFP, NCA; multiple SOC; 15-45 C", n_units="3 cells (Dataset 1)", labels="EIS spectra",
    ground_truth="lab measurement", year="2026", papers_doi="UNVERIFIED (kinetics-informed NN paper)", known_issues="Only 3 cells",
    verification="VERIFIED-PAGE", sample_inspected="no", citation_to_use="Chen, Zenodo 2026, doi:10.5281/zenodo.18494770")
add(name="Battery Archive (portal)", domain="battery", topics="42", url="https://www.batteryarchive.org/",
    license="per source; code of conduct (cite article + site)", access="open", size="n/s", sampling_rate="per source",
    measured_variables="standardised cycle and time-series tables", operating_conditions="CALCE, HNEI, ISU-ILCC, OX, SNL, UL-PUR, ORNL/SNL abuse",
    n_units="n/s", labels="per source", ground_truth="lab", year="2020-", papers_doi="per source", known_issues="Converted copies; check against originals",
    verification="VERIFIED-PAGE", sample_inspected="no", citation_to_use="www.batteryarchive.org + source article")
add(name="NASA HIRF Battery", domain="battery", topics="42", url="https://phm-datasets.s3.amazonaws.com/NASA/15.+HIRF+Battery+Data+Set.zip",
    license="not specified", access="open (S3)", size="1.09 GB", sampling_rate="UNVERIFIED", measured_variables="UNVERIFIED",
    operating_conditions="UNVERIFIED (reference document offline)", n_units="UNVERIFIED", labels="UNVERIFIED", ground_truth="lab", year="UNVERIFIED",
    papers_doi="UNVERIFIED", known_issues="Reference document offline", verification="PARTIAL", sample_inspected="no", citation_to_use="UNVERIFIED")
# ------------------------------------------------------------------ EV field / pack
add(name="BMW i3 battery and heating, 72 real trips (TUM)", domain="EV field", topics="42",
    url="https://ieee-dataport.org/open-access/battery-and-heating-data-real-driving-cycles", license="CC BY 4.0",
    access="registration (IEEE DataPort login)", size="35.7 MB measurement + 300 MB simulation", sampling_rate="UNVERIFIED",
    measured_variables="battery voltage, current, temperature, SoC; speed, throttle; heating power, cabin T; ambient T, elevation",
    operating_conditions="real driving, BMW i3 60 Ah, seasons", n_units="1 vehicle, 72 trips", labels="BMS SoC only",
    ground_truth="field data (BMS signals)", year="2020", papers_doi="dataset 10.21227/6jr9-5235; Steinstraeter et al. WEVJ 11 (2020) 41, 10.3390/wevj11020041 (Crossref)",
    known_issues="Users asked how SoC was recorded (2025 comments); no SOH/capacity ground truth; single vehicle", verification="VERIFIED-PAGE",
    sample_inspected="no", citation_to_use="Steinstraeter, Buberger, Trifonov, IEEE DataPort, doi:10.21227/6jr9-5235")
add(name="Stanford real-world EV field data (Pozzato 2023, Joule)", domain="EV field", topics="42", url="https://data.mendeley.com/datasets/7vdkzpnjgj/2",
    license="CC BY-NC 3.0 (non-commercial)", access="open", size="1.80 GB", sampling_rate="per-signal timestamps",
    measured_variables="pack current, pack voltage, pack SoC, pack temperature (+ energy), each with own timestamp", operating_conditions="1 year driving + charging",
    n_units="1 vehicle (pack level)", labels="none beyond BMS SoC", ground_truth="field data", year="2023", papers_doi="10.1016/j.joule.2023.07.018 (Crossref)",
    known_issues="NC licence; asynchronous timestamps per signal; no capacity reference", verification="VERIFIED-PAGE", sample_inspected="no",
    citation_to_use="Pozzato et al., Joule 7 (2023), doi:10.1016/j.joule.2023.07.018")
add(name="Field EV fleet BMS telemetry (Korea, E-GMP)", domain="EV field", topics="42",
    url="https://ieee-dataport.org/documents/field-ev-fleet-bms-telemetry-dataset", license="CC BY 4.0", access="subscription (IEEE DataPort)",
    size="25.5 MB (event-level parquet)", sampling_rate="1 s (source); events", measured_variables="pack V, I, T, SoC, speed, motor speed, odometer, vendor SoH; derived resistance",
    operating_conditions="20 taxis + 1 reference vehicle, Aug 2024-Jan 2026", n_units="21 vehicles; ~800k launch events",
    labels="vendor SoH (when available); lab resistance on 1 vehicle", ground_truth="field data", year="2026", papers_doi="dataset 10.21227/0v0g-gz47; IEEE TTE article not named",
    known_issues="Subscription; event-level extracts, not raw series", verification="VERIFIED-PAGE", sample_inspected="no",
    citation_to_use="Choi et al., IEEE DataPort, doi:10.21227/0v0g-gz47")
add(name="UPC battery pack WLTP cycling", domain="EV pack (lab)", topics="42", url="https://batterymaster.upc.edu/datasets",
    license="not stated", access="open (CORA)", size="UNVERIFIED", sampling_rate="UNVERIFIED", measured_variables="cell voltages, currents, surface temperatures, pack resistance",
    operating_conditions="WLTP-derived discharge (Tesla Model 3 model), CC-CV", n_units="up to 36 cells, 3 parallel branches", labels="UNVERIFIED",
    ground_truth="lab measurement (commercial BMS units)", year="2024 (v3)", papers_doi="dataset doi:10.34810/data2395", known_issues="licence missing",
    verification="VERIFIED-PAGE", sample_inspected="no", citation_to_use="de la Vega, Ortega, Riba, CORA doi:10.34810/data2395")
add(name="Real EV dataset (e-buses, Mendeley j9ky68gnd3)", domain="EV field", topics="42", url="https://data.mendeley.com/datasets/j9ky68gnd3",
    license="CC BY 4.0", access="open", size="~15 kB (4 csv)", sampling_rate="UNVERIFIED", measured_variables="UNVERIFIED (summary level)",
    operating_conditions="commercial electric buses", n_units="4 files (vin1/5/12/19)", labels="UNVERIFIED", ground_truth="field", year="2025",
    papers_doi="UNVERIFIED", known_issues="Too small to be time series; not usable as is", verification="VERIFIED-PAGE", sample_inspected="no",
    citation_to_use="Mendeley doi:10.17632/j9ky68gnd3.3")
add(name="NREL EV duty cycles (Fleet DNA / TSDC)", domain="EV field", topics="42", url="https://www.nrel.gov/transportation/fleettest-fleet-dna.html",
    license="UNVERIFIED", access="UNVERIFIED", size="UNVERIFIED", sampling_rate="UNVERIFIED", measured_variables="UNVERIFIED", operating_conditions="UNVERIFIED",
    n_units="UNVERIFIED", labels="UNVERIFIED", ground_truth="UNVERIFIED", year="UNVERIFIED", papers_doi="UNVERIFIED",
    known_issues="nrel.gov unreachable from this session (HTTP 000)", verification="UNVERIFIED", sample_inspected="no", citation_to_use="UNVERIFIED")
add(name="ACN-Data EV charging (Caltech, JPL, Office001)", domain="EV charging", topics="14,42", url="https://ev.caltech.edu/dataset",
    license="not stated", access="registration (API token)", size="n/s", sampling_rate="session level; current time series via /ts",
    measured_variables="kWhDelivered, connection/disconnect/doneCharging times, chargingCurrent and pilotSignal series, user inputs",
    operating_conditions="workplace charging, 3 sites", n_units="112 EVSEs", labels="none (no vehicle SOC)", ground_truth="field metering", year="2019-",
    papers_doi="10.1145/3307772.3328313 (Crossref-checked)", known_issues="Web-interface timestamps before 2019-10-10 offset 7-8 h; no battery SOC",
    verification="VERIFIED-PAGE", sample_inspected="no", citation_to_use="Lee, Li, Low, e-Energy 2019, doi:10.1145/3307772.3328313")
# ------------------------------------------------------------------ EV powertrain
add(name="Paderborn PMSM temperature (Kaggle)", domain="EV powertrain", topics="46", url="https://www.kaggle.com/datasets/wkirgsn/electric-motor-temperature",
    license="CC BY-SA 4.0", access="registration (Kaggle)", size="300 MB (measures_v2.csv)", sampling_rate="2 Hz",
    measured_variables="u_d, u_q, i_d, i_q, motor_speed, torque, coolant, ambient, stator_yoke, stator_tooth, stator_winding, pm (rotor magnet) temperature, profile_id",
    operating_conditions="prototype OEM PMSM on bench, random-walk speed-torque drive cycles", n_units="1 motor; profiles of 1-6 h, 185 h total (count n/s)",
    labels="pm, stator temperatures (measured)", ground_truth="lab measurement (telemetry on rotor)", year="2019, updated 2021",
    papers_doi="Kirchgaessner et al. IEEE TPEL 2021, 10.1109/tpel.2020.3045596; TNN EAAI 2023, 10.1016/j.engappai.2022.105537 (Crossref)",
    known_issues="Single motor; benchmarked to death by the dataset authors' own TNN (physics-informed)", verification="VERIFIED-PAGE",
    sample_inspected="no (Kaggle API metadata only)", citation_to_use="Kirchgaessner, Wallscheid, Boecker, IEEE TPEL 2021")
add(name="HUST PMSM ITSC (Xu, Fu, Luo, Liu)", domain="EV powertrain", topics="36,41",
    url="https://ieee-dataport.org/documents/three-phase-pmsm-itsc-faults-stator-winding-dataset", license="CC BY 4.0", access="subscription (IEEE DataPort)",
    size="66.94 GB", sampling_rate="n/s", measured_variables="3-phase voltage, 3-phase current, short-circuit current",
    operating_conditions="12 torque-speed points", n_units="1 motor (n/s)", labels="9 shorted-turn levels x 3 fault resistances",
    ground_truth="lab measurement", year="2026", papers_doi="dataset 10.21227/4jpc-qh81; no paper named; code github.com/XHX-HUST/PMSM-ITSC",
    known_issues="Subscription + 67 GB; motor ratings not stated", verification="VERIFIED-PAGE", sample_inspected="no", citation_to_use="Xu et al., IEEE DataPort, doi:10.21227/4jpc-qh81")
add(name="PMSM stator faults 1/1.5/3 kW (Jung et al., Mendeley)", domain="EV powertrain", topics="36,41", url="https://data.mendeley.com/datasets/rgn5brrgrn/5",
    license="CC BY 4.0", access="open", size="6.97 GB (3 zips)", sampling_rate="current 100 kHz, vibration 25.6 kHz",
    measured_variables="3-phase currents, z-axis vibration (TDMS); no voltage, speed or torque listed",
    operating_conditions="inter-turn and inter-coil faults, severities 0-21.69 %", n_units="3 motors", labels="fault type, severity %",
    ground_truth="lab measurement", year="2022-2023", papers_doi="10.1016/j.dib.2023.108952 (Crossref)",
    known_issues="Current-only -> voltage-based fault models not applicable; operating point not varied (as far as listed)",
    verification="VERIFIED-PAGE", sample_inspected="member list of 1.0kW.zip (34 TDMS) by range request", citation_to_use="Jung et al., Data in Brief 2023")
add(name="NASA IGBT accelerated aging", domain="power electronics", topics="24", url="https://phm-datasets.s3.amazonaws.com/NASA/8.+IGBT+Accelerated+Aging.zip",
    license="not specified", access="open (S3); data.nasa.gov shows 'no data'", size="240.5 MB", sampling_rate="high-speed transients in some cases",
    measured_variables="gate voltage, collector-emitter voltage, collector current (some runs)", operating_conditions="thermal overstress; DC or squared gate bias",
    n_units="6 devices", labels="aging time to failure", ground_truth="lab measurement", year="UNVERIFIED (modified 2020)", papers_doi="UNVERIFIED",
    known_issues="6 devices only; 'preliminary data'", verification="VERIFIED-PAGE", sample_inspected="no", citation_to_use="NASA PCoE, Celaya et al. (DOI not checked)")
add(name="NASA MOSFET thermal overstress aging", domain="power electronics", topics="24", url="https://phm-datasets.s3.amazonaws.com/NASA/13.+MOSFET+Thermal+Overstress+Aging.zip",
    license="not specified", access="open (S3)", size="7.85 GB", sampling_rate="UNVERIFIED", measured_variables="UNVERIFIED (reference doc offline)",
    operating_conditions="thermal overstress", n_units="UNVERIFIED", labels="UNVERIFIED", ground_truth="lab", year="UNVERIFIED", papers_doi="UNVERIFIED",
    known_issues="Reference document offline (mirror note)", verification="PARTIAL", sample_inspected="no", citation_to_use="UNVERIFIED")
add(name="NASA capacitor electrical stress (1 and 2)", domain="power electronics", topics="21", url="https://phm-datasets.s3.amazonaws.com/NASA/12.+Capacitor+Electrical+Stress.zip",
    license="not specified", access="open (S3)", size="5.04 GB (+ set 2)", sampling_rate="UNVERIFIED", measured_variables="UNVERIFIED", operating_conditions="electrical stress",
    n_units="UNVERIFIED", labels="UNVERIFIED", ground_truth="lab", year="UNVERIFIED", papers_doi="UNVERIFIED", known_issues="set 2 reference offline",
    verification="PARTIAL", sample_inspected="no", citation_to_use="UNVERIFIED")
add(name="MagNet (Princeton)", domain="magnetics", topics="35", url="https://mag-net.princeton.edu/", license="UNVERIFIED", access="open",
    size="UNVERIFIED (>500k waveforms per topic list)", sampling_rate="UNVERIFIED", measured_variables="B(t), H(t), core loss", operating_conditions="ferrite materials, f, T, DC bias",
    n_units="10+ materials", labels="core loss", ground_truth="lab measurement", year="2022-", papers_doi="10.1109/apec43599.2022.9773372 (Crossref)",
    known_issues="MagNet Challenge -> strong competition", verification="VERIFIED-PAGE (home page only)", sample_inspected="no", citation_to_use="Li et al., APEC 2022")
# ------------------------------------------------------------------ others from the topic list
add(name="GPVS-Faults (Bakdi et al.)", domain="PV / inverter", topics="33,38", url="https://data.mendeley.com/datasets/n76t439f65/1", license="CC BY 4.0",
    access="open", size="205 MB (18 files: .mat + CSV zip)", sampling_rate="UNVERIFIED", measured_variables="UNVERIFIED (PV/grid V, I per paper)",
    operating_conditions="MPPT and IPPT modes; faults F0-F7 incl. inverter IGBT, feedback sensor fault, grid sag, shading, open circuit", n_units="1 lab microgrid",
    labels="fault class", ground_truth="lab measurement", year="2020", papers_doi="dataset 10.17632/n76t439f65.1; arXiv 2112.14842", known_issues="one plant; class balance n/s",
    verification="VERIFIED-PAGE", sample_inspected="no", citation_to_use="Bakdi et al., Mendeley Data doi:10.17632/n76t439f65.1")
add(name="KAIST rotating machine (Jung et al. 2023)", domain="vibration", topics="27,31", url="https://data.mendeley.com/datasets/ztmf3m7h5x/6", license="CC BY 4.0",
    access="open", size="4.25 GB", sampling_rate="UNVERIFIED", measured_variables="4 accelerometers, microphone, 2 thermocouples, 3 current sensors",
    operating_conditions="bearing faults, misalignment, unbalance, 3 loads", n_units="1 bench", labels="fault class", ground_truth="lab", year="2023",
    papers_doi="10.1016/j.dib.2023.109049 (Crossref)", known_issues="-", verification="VERIFIED-PAGE", sample_inspected="no", citation_to_use="Jung et al., Data in Brief 2023")
add(name="MAFAULDA", domain="vibration", topics="27,31", url="https://www02.smt.ufrj.br/~offshore/mfs/page_01.html", license="UNVERIFIED", access="open",
    size="UNVERIFIED", sampling_rate="50 kHz (topic list, not re-read)", measured_variables="UNVERIFIED", operating_conditions="UNVERIFIED", n_units="1 bench",
    labels="fault class", ground_truth="lab", year="UNVERIFIED", papers_doi="UNVERIFIED", known_issues="crowded topic", verification="VERIFIED-PAGE (title only)",
    sample_inspected="no", citation_to_use="UNVERIFIED")
add(name="CWRU bearing", domain="vibration", topics="27", url="https://engineering.case.edu/bearingdatacenter", license="UNVERIFIED", access="open", size="UNVERIFIED",
    sampling_rate="12/48 kHz (topic list)", measured_variables="UNVERIFIED", operating_conditions="EDM faults", n_units="1 bench", labels="fault class", ground_truth="lab",
    year="UNVERIFIED", papers_doi="UNVERIFIED", known_issues="saturated", verification="VERIFIED-PAGE (title only)", sample_inspected="no", citation_to_use="UNVERIFIED")
add(name="Paderborn KAt bearing", domain="vibration", topics="27", url="https://mb.uni-paderborn.de/kat/forschung/kat-datacenter/bearing-datacenter", license="UNVERIFIED",
    access="UNVERIFIED", size="UNVERIFIED", sampling_rate="UNVERIFIED", measured_variables="UNVERIFIED", operating_conditions="UNVERIFIED", n_units="UNVERIFIED",
    labels="UNVERIFIED", ground_truth="UNVERIFIED", year="UNVERIFIED", papers_doi="UNVERIFIED", known_issues="404 / no response from this session; mirror not found",
    verification="UNVERIFIED", sample_inspected="no", citation_to_use="UNVERIFIED")
add(name="XJTU-SY bearing run-to-failure", domain="vibration", topics="30", url="https://biaowang.tech/xjtu-sy-bearing-datasets/", license="UNVERIFIED", access="open",
    size="UNVERIFIED", sampling_rate="UNVERIFIED", measured_variables="UNVERIFIED", operating_conditions="UNVERIFIED", n_units="UNVERIFIED", labels="RUL",
    ground_truth="lab", year="UNVERIFIED", papers_doi="UNVERIFIED", known_issues="-", verification="VERIFIED-PAGE (title only)", sample_inspected="no", citation_to_use="UNVERIFIED")
add(name="IMS bearing (NASA)", domain="vibration", topics="30", url="https://phm-datasets.s3.amazonaws.com/NASA/4.+Bearings.zip", license="not specified", access="open (S3)",
    size="UNVERIFIED", sampling_rate="UNVERIFIED", measured_variables="UNVERIFIED", operating_conditions="run-to-failure", n_units="UNVERIFIED", labels="RUL", ground_truth="lab",
    year="UNVERIFIED", papers_doi="UNVERIFIED", known_issues="-", verification="VERIFIED-PAGE (HEAD 200)", sample_inspected="no", citation_to_use="UNVERIFIED")
add(name="FEMTO PRONOSTIA", domain="vibration", topics="30", url="https://phm-datasets.s3.amazonaws.com/NASA/10.+FEMTO+Bearing.zip", license="not specified", access="open (S3 mirror)",
    size="UNVERIFIED", sampling_rate="UNVERIFIED", measured_variables="UNVERIFIED", operating_conditions="run-to-failure", n_units="UNVERIFIED", labels="RUL", ground_truth="lab",
    year="UNVERIFIED", papers_doi="UNVERIFIED", known_issues="-", verification="VERIFIED-PAGE (HEAD 200)", sample_inspected="no", citation_to_use="UNVERIFIED")
add(name="NREL GRC gearbox vibration", domain="wind / gears", topics="28,40", url="https://data.openei.org/submissions/738", license="CC BY 4.0 (topic list; not re-read)",
    access="open", size="UNVERIFIED", sampling_rate="UNVERIFIED", measured_variables="UNVERIFIED", operating_conditions="healthy vs damaged gearbox on dynamometer", n_units="2 gearboxes",
    labels="health state", ground_truth="lab", year="UNVERIFIED", papers_doi="OSTI 1844194 (topic list)", known_issues="-", verification="VERIFIED-PAGE (title only)", sample_inspected="no", citation_to_use="UNVERIFIED")
add(name="Treml broken rotor bar (induction motor)", domain="machines", topics="36", url="https://ieee-dataport.org/open-access/experimental-database-detecting-and-diagnosing-rotor-broken-bar-three-phase-induction",
    license="UNVERIFIED", access="open access (title)", size="UNVERIFIED", sampling_rate="UNVERIFIED", measured_variables="3-ph V, I, 5 vibration (topic list)",
    operating_conditions="1-4 broken bars, 8 loads (topic list)", n_units="1 motor", labels="broken bars", ground_truth="lab", year="UNVERIFIED", papers_doi="arXiv 2501.03746 (topic list)",
    known_issues="users report V/I phase misalignment (topic list, not re-read)", verification="VERIFIED-PAGE (title only)", sample_inspected="no", citation_to_use="UNVERIFIED")
add(name="CARE to Compare (wind SCADA, labelled faults)", domain="wind", topics="40,41", url="https://zenodo.org/records/14006163", license="CC BY-SA 4.0", access="open",
    size="5.48 GB", sampling_rate="10 min (topic list)", measured_variables="SCADA", operating_conditions="3 wind farms", n_units="36 turbines (topic list)", labels="fault events",
    ground_truth="field", year="2024", papers_doi="dataset 10.5281/zenodo.14006163", known_issues="use latest version", verification="VERIFIED-PAGE", sample_inspected="no", citation_to_use="Zenodo doi:10.5281/zenodo.14006163")
add(name="Kelmarsh wind farm", domain="wind", topics="40,41", url="https://zenodo.org/records/16807551", license="CC BY 4.0", access="open", size="3.84 GB",
    sampling_rate="10 min", measured_variables="SCADA + grid meter", operating_conditions="6 turbines (n/s here)", n_units="UNVERIFIED", labels="status logs",
    ground_truth="field", year="2025 version", papers_doi="dataset 10.5281/zenodo.16807551", known_issues="-", verification="VERIFIED-PAGE", sample_inspected="no", citation_to_use="Zenodo doi:10.5281/zenodo.16807551")
add(name="Penmanshiel wind farm", domain="wind", topics="40,41", url="https://zenodo.org/record/5946808", license="CC BY 4.0", access="open", size="3.63 GB",
    sampling_rate="10 min", measured_variables="SCADA", operating_conditions="WT01-15", n_units="15 turbines (file names)", labels="status logs", ground_truth="field",
    year="2022", papers_doi="dataset 10.5281/zenodo.5946808", known_issues="-", verification="VERIFIED-PAGE", sample_inspected="no", citation_to_use="Zenodo doi:10.5281/zenodo.5946808")
add(name="GESL grid event signature library", domain="grid", topics="32-34", url="https://gesl.ornl.gov", license="UNVERIFIED", access="free (registration n/s)",
    size="UNVERIFIED", sampling_rate="UNVERIFIED", measured_variables="voltage, current, frequency waveforms (topic list)", operating_conditions="utility events", n_units="UNVERIFIED",
    labels="event type", ground_truth="field", year="UNVERIFIED", papers_doi="UNVERIFIED", known_issues="-", verification="VERIFIED-PAGE (title only)", sample_inspected="no", citation_to_use="UNVERIFIED")
add(name="VSB power line fault (Kaggle)", domain="grid", topics="32", url="https://www.kaggle.com/c/vsb-power-line-fault-detection", license="competition rules",
    access="registration", size="UNVERIFIED", sampling_rate="UNVERIFIED", measured_variables="UNVERIFIED", operating_conditions="MV lines", n_units="UNVERIFIED", labels="PD fault",
    ground_truth="field", year="2019", papers_doi="UNVERIFIED", known_issues="-", verification="VERIFIED-PAGE (title only)", sample_inspected="no", citation_to_use="UNVERIFIED")
add(name="OPSD / ENTSO-E", domain="grid", topics="14", url="https://data.open-power-system-data.org/ ; https://transparency.entsoe.eu/", license="UNVERIFIED", access="open / registration",
    size="UNVERIFIED", sampling_rate="15-60 min", measured_variables="load, generation, prices", operating_conditions="EU", n_units="countries", labels="-", ground_truth="field",
    year="-", papers_doi="-", known_issues="-", verification="VERIFIED-PAGE (title only)", sample_inspected="no", citation_to_use="UNVERIFIED")
add(name="ETDataset (ETT)", domain="transformer thermal", topics="35", url="https://github.com/zhouhaoyi/ETDataset", license="UNVERIFIED", access="open",
    size="UNVERIFIED", sampling_rate="15 min / 1 h", measured_variables="oil temperature, loads", operating_conditions="2 stations", n_units="2", labels="-", ground_truth="field",
    year="2021", papers_doi="UNVERIFIED", known_issues="GitHub blocked from curl (proxy 403)", verification="UNVERIFIED", sample_inspected="no", citation_to_use="UNVERIFIED")
add(name="NREL PVDAQ", domain="PV", topics="37", url="(not opened)", license="UNVERIFIED", access="UNVERIFIED", size="UNVERIFIED", sampling_rate="UNVERIFIED",
    measured_variables="UNVERIFIED", operating_conditions="UNVERIFIED", n_units="UNVERIFIED", labels="UNVERIFIED", ground_truth="field", year="UNVERIFIED", papers_doi="UNVERIFIED",
    known_issues="nrel.gov unreachable", verification="UNVERIFIED", sample_inspected="no", citation_to_use="UNVERIFIED")
add(name="IEEE PHM 2014 Data Challenge (FCLAB PEMFC)", domain="fuel cell", topics="43", url="https://www.fclab.fr/", license="UNVERIFIED", access="UNVERIFIED", size="UNVERIFIED",
    sampling_rate="UNVERIFIED", measured_variables="UNVERIFIED", operating_conditions="UNVERIFIED", n_units="2 stacks (literature)", labels="degradation", ground_truth="lab", year="2014",
    papers_doi="UNVERIFIED", known_issues="data page not located on fclab.fr", verification="UNVERIFIED", sample_inspected="no", citation_to_use="UNVERIFIED")
add(name="nonlinearbenchmark.org (Silverbox, WH, Cascaded Tanks, EMPS)", domain="control", topics="2-4", url="https://www.nonlinearbenchmark.org/", license="UNVERIFIED",
    access="open", size="small", sampling_rate="per benchmark", measured_variables="input/output", operating_conditions="per benchmark", n_units="-", labels="-", ground_truth="lab",
    year="-", papers_doi="-", known_issues="-", verification="VERIFIED-PAGE (title only)", sample_inspected="no", citation_to_use="per benchmark")

with open("datasets.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    w.writerows(R)
from collections import Counter  # noqa: E402
print(len(R), "rows;", Counter(r["verification"].split(" ")[0] for r in R))
