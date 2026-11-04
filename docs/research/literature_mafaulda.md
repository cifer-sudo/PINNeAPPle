# Literature: MAFAULDA, COMFAULDA, physics-informed and operator models for rotating-machinery diagnosis

Structured search, 2026-11-04 (web search engines, arXiv, PMC, IEEE DataPort, Zenodo, publisher pages). It is not
yet a full systematic review: a PRISMA-style search of Scopus and Web of Science (query strings below, screening by
title / abstract / full text, extraction table) is still to do, and needs institutional access.

**Query strings used:** "MaFaulDa" / "MAFAULDA" with classification, deep learning, physics-informed, graph neural
network, Hamiltonian, cross-speed, unseen speed, domain shift, leakage, severity; "COMFAULDA" / "Composed Fault
Dataset"; "Fourier neural operator" with fault diagnosis, bearing, rotating machinery; "Lagrangian neural network" /
"port-Hamiltonian" with fault diagnosis.

## What is reported on MAFAULDA

| Work | Model | Reported score | Protocol, as far as stated | Leakage risk |
|---|---|---|---|---|
| Shen, Chowdhury, Banerjee, Terejanu, ICPRAM 2023 (arXiv 2301.02243) | Hamiltonian neural network energy as features + logistic regression / random forest | AUC 0.78 (normal vs abnormal), 0.84 (multi-class) | segments of the records | segments of one record on both sides unless stated |
| Rigas, Papachristou, Sotiropoulos, Alexandridis (arXiv 2412.01322, v3 2025) | shallow Kolmogorov-Arnold networks on selected features | F1 97.24 % fault classification on MaFaulDa | as in the paper | to check |
| t4pdm (arXiv 2204.03725) | transformer | 98.32 % | as in the paper | to check |
| 1D-CNN (cited in later work) | CNN | 99.58 % | as in the paper | to check |
| Similarity-based models (SBRT) | similarity / nearest neighbour | 96.43 % | as in the paper | to check |
| MLP with SMOTE (IEEE 8880437) | MLP | 96.2 % | as in the paper | to check |
| Image-based study testing on the lowest fault intensities | CNN on vibration images | 79.63 % (6 classes) | train on most severities, test on the lowest | low (severity held out) |
| Leakage-free benchmark (SBC BRESCI) | MLP, 1D-CNN, LSTM, RF, 132 features | (see paper) | stratified group k-fold by file; notes that >99 % results used k-fold with same-file leakage | low |
| MAFAULDA-rotor-perception (Hugging Face card) | -- | -- | highest severity of each class held out; speed-matched healthy baselines needed | low |
| Sanami & Aghdam, IEEE L-CSS 2026 (inverse PINN) | inverse PINN on stiffness / damping | (not retrieved) | unseen misalignment severities reported | DOI to obtain |

**No study found trains on some speeds and tests on held-out speeds** of MAFAULDA with reported numbers. Cross-speed
domain shift is studied on CWRU and other bearing sets (working-condition-indexed domain generalisation, DANN with
speed as the domain label), where the shift is reported to grow with the speed difference.

## Neural operators and physics-structured models for fault classification

- No application of a Fourier neural operator to fault *classification* of rotating machinery was found; Fourier-based
  work uses FFT / STFT preprocessing with CNNs or Fourier-enhanced transformers.
- Lagrangian networks: rotor balancing (Zhong & Hou, unsupervised deep Lagrangian network), not classification.
- Port-Hamiltonian networks with inputs and dissipation: system identification (arXiv 2502.14432), not diagnosis.

## COMFAULDA

Dataset (Zenodo 8208454 / IEEE DataPort 10.21227/89ye-ap56, CC BY 4.0): 2162 runs, seven scenarios (normal,
unbalance, horizontal and vertical misalignment, and three combinations), 50 kHz, 5 s, 12-60 Hz, tachometer, a
capacitive and a piezoelectric triaxial accelerometer. **No classification result on COMFAULDA was found.**

## Gaps this programme addresses

1. Generalisation to unseen rotation speeds on MAFAULDA, measured with splits that never share a run.
2. A Fourier neural operator on order spectra compared at equal protocol with feature models, KAN and an HNN-energy
   baseline.
3. Recording-session effects (1X phase drift, faulty tachometers, an anomalous accelerometer) and a channel-screened
   severity estimate.
4. First classification results on COMFAULDA, including combined faults recognised from single faults.

## Sources

arXiv 2301.02243; arXiv 2412.01322; arXiv 2204.03725; arXiv 2502.14432; arXiv 2509.09251; arXiv 2608.18716;
sol.sbc.org.br/index.php/bresci/article/download/44074/43837; huggingface.co/datasets/AI4Manufacturing/MAFAULDA-rotor-perception;
biblioteca.sbrt.org.br/articlefile/601.pdf; ieeexplore.ieee.org/document/8880437; pmc.ncbi.nlm.nih.gov/articles/PMC13469860;
pmc.ncbi.nlm.nih.gov/articles/PMC12074226; pmc.ncbi.nlm.nih.gov/articles/PMC13030059; zenodo.org/records/8208454;
ieee-dataport.org/node/8908.
