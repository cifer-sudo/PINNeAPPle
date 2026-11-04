# Topics and datasets (input, as pasted by the user on 2026-11-03)

> Transcribed verbatim from the user's message. The "État du travail en cours" section at the end refers to a
> simulated DC-microgrid study done in another session; it is not in this repository and is not used here.

Oui, plusieurs de ces sujets ont des données réelles publiques. J'ai vérifié en ligne aujourd'hui celles qui portent un lien ; celles marquées « connu » sont des références classiques que je n'ai pas revérifiées ce soir.

## Sujets avec données réelles publiques

### Diagnostic vibratoire (sujets n°27 à 31)

| Sujet | Données réelles | Ce qu'il y a dedans |
|---|---|---|
| 27 Roulements, 31 balourd et désalignement | **MAFAULDA** (UFRJ), votre exemple | Banc SpectraQuest, 1951 séries à 50 kHz : normal, balourd, désalignements, défauts de roulement. Les fréquences BPFO, BPFI, FTF et BSF sont données, utiles comme contraintes physiques. |
| 27 Roulements | **CWRU** (connu) | Défauts usinés par électroérosion, 12 et 48 kHz. Le plus cité. |
| 27 Roulements + courant moteur | **Paderborn KAt** (connu) | Vibration, courants de phase, couple, température. Défauts artificiels et réels. |
| 27, 31 Machine tournante | **KAIST**, Jung et al., Data in Brief 2023 ([Mendeley](https://data.mendeley.com/datasets/ztmf3m7h5x)) | 4 accéléromètres, micro, 2 thermocouples, 3 capteurs de courant. Roulement, désalignement, balourd à 3 charges. CC BY 4.0. |
| 30 Durée de vie résiduelle des roulements | **XJTU-SY**, **IMS (NASA)**, **FEMTO PRONOSTIA** (connus) | Essais jusqu'à la rupture. |
| 28 Engrenages, 40 éolien | **NREL GRC** ([OEDI](https://data.openei.org/submissions/738)) | Boîte de vitesses d'éolienne saine et endommagée sur dynamomètre. CC BY 4.0. |

### Machines électriques (sujets n°36, 41, 46)

| Sujet | Données réelles | Ce qu'il y a dedans |
|---|---|---|
| 46 Température des aimants d'un PMSM | **Paderborn Electric Motor Temperature** (Kaggle) | Environ 185 h à 2 Hz, température des aimants mesurée. |
| 36 Barres cassées, moteur asynchrone | **Treml et al.** ([IEEE DataPort](https://ieee-dataport.org/open-access/experimental-database-detecting-and-diagnosing-rotor-broken-bar-three-phase-induction)) | Tensions et courants triphasés, 5 vibrations, 1 à 4 barres cassées, 8 niveaux de charge. Des utilisateurs signalent des phases tension/courant désalignées. |
| 36, 41 Court-circuit entre spires d'un PMSM | **Xu et Fu (HUST)** ([IEEE DataPort](https://ieee-dataport.org/documents/three-phase-pmsm-itsc-faults-stator-winding-dataset)) ; jeu Mendeley PMSM 1 / 1,5 / 3 kW ([Mendeley](https://data.mendeley.com/datasets/rgn5brrgrn/1)) | 12 points couple-vitesse, 9 pourcentages de spires, courant de court-circuit mesuré. |

### Convertisseurs et composants magnétiques (sujets n°21, 24, 35)

| Sujet | Données réelles | Ce qu'il y a dedans |
|---|---|---|
| 24 Vieillissement IGBT, 21 santé des condensateurs | **NASA PCoE** : IGBT Accelerated Aging ([data.nasa.gov](https://data.nasa.gov/dataset/igbt-accelerated-aging-data-set)), condensateurs ([miroir PHM](https://data.phmsociety.org/nasa/)) | Vieillissement accéléré mesuré. Le jeu MOSFET semble hors ligne, sur demande. |
| 35 Hystérésis et pertes fer | **MagNet** (Princeton, Dartmouth, Plexim) ([projet](https://collaborate.princeton.edu/en/publications/magnet-an-open-source-database-for-data-driven-magnetic-core-loss/)) | Plus de 500 000 formes d'onde B-H mesurées sur ferrites. Très bon terrain pour un PINN avec Jiles-Atherton, mais concurrence forte (MagNet Challenge). |
| 35 Thermique de transformateur | **ETDataset (ETT)** (connu) | Température d'huile et charges réelles. |

### Réseaux électriques et leurs défauts (sujets n°13, 14, 32 à 34)

| Sujet | Données réelles | Ce qu'il y a dedans |
|---|---|---|
| 32 à 34 Événements et défauts réseau | **GESL** (ORNL, LLNL, PNNL) ([gesl.ornl.gov](https://gesl.ornl.gov)) | Formes d'onde réelles tension, courant, fréquence, étiquetées par des exploitants. Gratuit. |
| 32 Lignes MT | **VSB Power Line Fault Detection** (Kaggle, connu) | Signaux mesurés de décharges partielles. |
| 14 Prévision charge et production | **OPSD**, **ENTSO-E** (connus), **ONS** (déjà dans le dépôt) | Séries réelles. |

### Renouvelables et stockage (sujets n°37, 38, 40 à 43)

| Sujet | Données réelles | Ce qu'il y a dedans |
|---|---|---|
| 38 Défauts PV, et 33 défaut capteur vs défaut procédé | **GPVS-Faults** (Bakdi et al.) ([Mendeley](https://data.mendeley.com/datasets/n76t439f65)) | Micro-réseau PV raccordé, essais de labo. Défaut IGBT d'onduleur, **défaut de capteur de retour**, creux de tension, ombrage partiel, circuit ouvert, défauts MPPT/IPPT. |
| 37 Paramètres PV, prévision | **NREL PVDAQ** (connu) | Production réelle d'installations PV. |
| 40, 41 Éolien avec journaux de pannes | **CARE to Compare** ([Zenodo](https://zenodo.org/records/14006163)) ; **Kelmarsh** ([Zenodo](https://zenodo.org/records/16807551)) ; **Penmanshiel** ([Zenodo](https://zenodo.org/record/5946808)) | SCADA 10 min. CARE : 36 turbines avec défauts étiquetés. Utiliser la dernière version. |
| 42 Batteries (SOC, SOH, durée de vie) | **NASA PCoE**, **CALCE**, **Severson et al.** (Toyota-MIT-Stanford), **Oxford** (connus) | Cyclage jusqu'au vieillissement. |
| 43 Pile à combustible PEM | **IEEE PHM 2014 Data Challenge** (FCLAB, connu) | Dégradation mesurée. |

### Contrôle (sujets n°2 à 4)

| Sujet | Données réelles | Ce qu'il y a dedans |
|---|---|---|
| 2 à 4 Identification et observateurs | **nonlinearbenchmark.org** (connu) : Silverbox, Wiener-Hammerstein, Cascaded Tanks, EMPS | Mesures sur de vrais systèmes. |

## Sujets sans données réelles publiques

Pour ces sujets, il faudra un banc HIL ou votre propre montage :
- **Micro-réseau DC** (n°16 à 20 et le n°33 que j'ai lancé). Seules les données ORNL/Adjuntas existent, et elles portent sur la stabilité, pas sur les défauts.
- **Convertisseur commuté, FCS-MPC, PLL** (n°22, 25, 26).
- **OPF, estimation d'état, stabilité transitoire** (n°8, 10 à 12). Les cas IEEE et PGLib sont des modèles, pas des mesures.
- **Inertie depuis PMU** (n°9). Les mesures PMU publiques sont rares ; GESL contient quelques événements de fréquence.

Les sujets théoriques (n°6, 7, 19 : Lyapunov, HJB, région d'attraction) se valident par simulation, ce que les revues acceptent pour ce type de travail.

## Recommandation (du message d'origine)

**GPVS-Faults** est le meilleur pont avec ce qui a déjà été construit. **MAFAULDA** est aussi un bon choix pour la vibration, mais le domaine est très encombré.

## Sources citées dans le message d'origine

- GPVS-Faults (Mendeley) https://data.mendeley.com/datasets/n76t439f65 · arXiv 2112.14842
- NASA PCoE mirror https://data.phmsociety.org/nasa/ · IGBT https://data.nasa.gov/dataset/igbt-accelerated-aging-data-set
- MOSFET thermal stress https://catalog.data.gov/dataset/prognostics-of-power-mosfets-under-thermal-stress-accelerated-aging-using-data-driven-and-
- GESL https://gesl.ornl.gov
- Treml broken rotor bar https://ieee-dataport.org/open-access/experimental-database-detecting-and-diagnosing-rotor-broken-bar-three-phase-induction · arXiv 2501.03746
- MagNet https://collaborate.princeton.edu/en/publications/magnet-an-open-source-database-for-data-driven-magnetic-core-loss/
- CARE to Compare https://zenodo.org/records/14006163 · Kelmarsh https://zenodo.org/records/16807551 · Penmanshiel https://zenodo.org/record/5946808
- KAIST https://data.mendeley.com/datasets/ztmf3m7h5x
- PMSM ITSC (HUST) https://ieee-dataport.org/documents/three-phase-pmsm-itsc-faults-stator-winding-dataset · Mendeley https://data.mendeley.com/datasets/rgn5brrgrn/1
- NREL GRC https://data.openei.org/submissions/738
