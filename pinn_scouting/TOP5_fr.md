# Les cinq meilleurs projets PINN pour un article Q1 (priorité VE / batteries)

*État au 4 novembre 2026. Sources :*
- *`datasets.csv` : 59 jeux de données ;*
- *`candidates.md` : 13 candidats, avec les preuves de saturation ;*
- *`scoring.csv` : scores pondérés ;*
- *`prototypes/` : essais de faisabilité sur données réelles.*

*Chaque chiffre provient d'un fichier consulté au cours de cette session (voir LOG.md) ou porte la mention NON VÉRIFIÉ.*

**Lecture du classement.** Le score pondéré de `scoring.csv` a été fixé **avant** l'exécution des prototypes.
Les prototypes ont ensuite modifié l'appréciation, et l'ordre ci-dessous en tient compte (voir « Ajustement après
prototypes » à la fin du document). Aucun modèle n'a été réglé pour le faire gagner.

**Informations éditoriales vérifiées.**
- **Frais de publication (APC) Elsevier** : liste officielle `journals/elsevier_apc.xlsx`, téléchargée le 4 novembre 2026.
  - Applied Energy : 4 210 USD.
  - J. Power Sources : 4 010 USD.
  - eTransportation : 4 630 USD.
  - J. Energy Storage : 4 410 USD.
  - Energy : 3 960 USD.
  - Electrochimica Acta : 3 760 USD.
  - Energy Conversion and Management : 4 500 USD.
  - Toutes ces revues sont hybrides : la publication sans APC reste possible.
  - Seule exception : *Energy and AI*, en libre accès intégral (4 270 USD).
- **IEEE (revues hybrides)** : 2 800 USD en 2026, 2 995 USD en 2027 (open.ieee.org).
- **Facteurs d'impact et délais d'évaluation : NON VÉRIFIÉS.** Les sites sciencedirect.com, elsevier.com,
  ieeexplore.ieee.org et cell.com ont renvoyé une erreur 403 ou 418 à cette session. À contrôler dans le JCR
  avant toute soumission.

---

## 1. C5 — Suivi sans étiquette de la capacité et de la résistance sous charges aléatoires de type VE

**1. Titre provisoire.** *Apprentissage informé par la physique d'un circuit équivalent neuronal pour l'état de
santé des batteries en fonctionnement aléatoire, validé par des essais de référence indépendants.*

**2. Question de recherche et lacune.** Peut-on suivre la capacité et la résistance à partir du seul
fonctionnement courant sous charges aléatoires, sans étiquette de capacité ? L'estimation se transpose-t-elle à une
autre température ambiante et à une autre distribution de charge ?

*Lacune : les travaux publiés sur ce jeu régressent les rares capacités de référence au moyen de modèles boîte noire
(par exemple un Transformer à fenêtres d'événements). Aucun travail trouvé n'identifie les états de santé à partir de
la réponse en tension pour n'utiliser ensuite les essais de référence que comme vérité terrain réservée.*

**3. Données.**
- **Source.** NASA PCoE « Randomized Battery Usage » : 28 cellules 18650 réparties en 7 groupes.
  - Miroir : https://phm-datasets.s3.amazonaws.com/NASA/11.+Randomized+Battery+Usage+Data+Set.zip (1,07 Go).
  - Licence non précisée (œuvre du gouvernement américain).
  - Citation : Bole, Kulkarni, Daigle, PHM 2014, doi:10.36001/phmconf.2014.v6i1.2490.
- **Variables d'entrée.** Pendant les décharges en marche aléatoire (1 s) : `voltage`, `current`, `temperature`, `time`.
- **Variables réservées à la validation.** La charge (Ah) de la `reference discharge` (1 A jusqu'à 3,2 V) et la
  réponse au `pulsed load`.
- **Groupes inspectés.**
  - RW25-28 (40 °C, 0,5 à 5 A, distribution asymétrique vers les forts courants) : 593 à 650 cycles et 12 à 14 capacités de référence par cellule.
  - RW3-6 (température ambiante, 0,5 à 4 A, distribution uniforme) : 22 à 44 références, jusqu'à 1,06 Ah.

**4. Physique et architecture.**
- **Modèle du prototype.**
  - Tension : $V_k(t)=f_\theta\big(z_k(t)\big)-R_{0,k}(T)\,I(t)-v_{1}(t)$.
  - État de charge : $z_k=1-\frac{1}{Q_k}\int I\,d\tau$.
  - Branche RC : $\dot v_1=-\frac{v_1}{\tau}+\frac{R_{1,k}}{\tau}I$.
  - $f_\theta$ est une tension à vide (OCV) neuronale partagée, avec une pénalité de monotonie.
- **Projet complet.**
  - État thermique localisé : $mc\,\dot T=I^2R_0+Iv_1-hA(T-T_{amb})$.
  - Dépendance d'Arrhenius de $R_0$.
  - Dynamique lente de santé : $\dot Q=-g_\phi\le0$, $\dot R_0=h_\phi\ge0$ (petits réseaux contraints en monotonie).
- **Perte.**
  $$\mathcal L=\tfrac1N\sum\|V-\hat V\|^2+\lambda_{T}\|T-\hat T\|^2+\lambda_{h}\sum_k\|Q_{k+1}-Q_k+g_\phi\Delta t\|^2+\lambda_m\|\mathrm{ReLU}(-f_\theta')\|^2.$$
- **Entraînement en deux étapes.** L'OCV est apprise sur les cellules d'entraînement. Elle est ensuite figée, et les
  états des cellules inédites sont identifiés.
- **Usage des étiquettes.** Aucune étiquette de capacité n'entre dans la perte. Une simple mise à l'échelle est
  calibrée sur les cellules d'entraînement.

**5. Références à battre.**
- Comptage coulométrique jusqu'à la tension de coupure.
- ECM + EKF.
- Régresseurs data-driven (ridge, MLP, GRU/Transformer).
- Transformer à fenêtres d'événements (*J. Phys. Energy* 2026, doi:10.1088/2515-7655/aebb63) : R² 0,955 et MAE 2,387
  (unités de SOH) sur RW11, avec entraînement sur RW9-10.
- Article *J. Energy Storage* 2026 sur l'évolution des paramètres ECM (doi:10.1016/j.est.2026.125097) : résumé
  inaccessible, à lire intégralement avant de démarrer.

**6. Protocole de validation.**
- **Découpages.**
  - Une cellule exclue par groupe (leave-one-cell-out).
  - Un groupe exclu parmi les 7 (leave-one-group-out).
  - Jamais de découpage aléatoire par échantillon.
- **Tests hors distribution.**
  - Température ambiante inédite (40 °C vers ambiante, et inversement).
  - Distribution de charge inédite.
  - Vieillissement au-delà de la plage d'entraînement.
- **Métriques.** RMSE, MAE et erreur maximale (Ah), MAPE (%), R², résidu de tension (mV). Moyenne ± écart-type sur
  5 graines et au moins 8 cellules de test. Intervalles conformes avec leur couverture.
- **Ablations.**
  - Sans physique.
  - Sans état thermique.
  - τ fixe ou appris.
  - 0, 1 ou toutes les références en supervision faible.
  - Bruit de mesure de 5, 10 et 20 mV.
  - Fraction de cycles utilisée.
- **Statistiques.** Test de Wilcoxon apparié par cellule, avec correction de Holm.

**7. Contributions attendues et risques.**
- **Contributions.**
  - Estimateur de santé sans étiquette, validé sur des essais indépendants.
  - Transfert entre températures ambiantes et entre distributions de charge.
  - Protocole ouvert couvrant les 28 cellules.
- **Risques et parades.**
  - (i) Identifiabilité de Q face à l'échelle de l'OCV : fixer les bornes de l'OCV à partir de la première décharge de référence, et rapporter l'information de Fisher.
  - (ii) Recouvrement possible avec l'article *J. Energy Storage* 2026 : le lire d'abord. En cas de recouvrement, se recentrer sur le banc d'essai hors distribution et sur l'extension thermique.
  - (iii) Cellules grand public et marches aléatoires de laboratoire : ajouter une validation externe sur cycles de conduite (données Stanford UDDS, OSF).

**8. Revues visées.**

| Rang | Revue | APC | IF et délais |
|---|---|---|---|
| 1 | eTransportation | 4 630 USD | NON VÉRIFIÉS |
| 2 | Applied Energy | 4 210 USD | NON VÉRIFIÉS |
| 3 | IEEE Trans. Transportation Electrification | 2 800 USD | NON VÉRIFIÉS |
| 4 | Energy and AI (libre accès intégral) | 4 270 USD | NON VÉRIFIÉS |
| 5 | J. Energy Storage (repli) | 4 410 USD | NON VÉRIFIÉS |

**9. Plan de travail.**
- S1-2 : chaîne de données pour les 28 cellules.
- S3 : lecture de l'article *J. Energy Storage* 2026 et gel du protocole.
- S4-6 : modèles et références.
- S7-8 : exclusion par groupe et incertitude.
- S9-10 : ablations.
- S11-13 : rédaction et publication du code.

**10. Critère d'arrêt (semaine 3).** En exclusion par groupe, le modèle physique doit battre le meilleur régresseur
data-driven sur au moins 5 des 7 groupes, avec une MAPE moyenne inférieure à 3 %. Sinon, on arrête. Un recouvrement
avec l'article *J. Energy Storage* 2026 constitue un second motif d'arrêt.

---

## 2. C1 — Température à cœur de cellules 21700 confrontée à des thermocouples internes

**1. Titre provisoire.** *Quand la physique aide-t-elle ? Estimation de la température à cœur de cellules 21700,
validée par thermocouples internes entre cellules, stades de vieillissement et températures ambiantes.*

**2. Question et lacune.** Un estimateur informé par la physique bat-il :
- (a) la relation quasi-statique de Biot ;
- (b) un observateur de Kalman à deux états ;
- (c) une boîte noire,

sur des cellules, des états de vieillissement et des ambiances jamais vus à l'entraînement ?

*Lacune : aucune étude trouvée ne valide ces estimateurs sur deux jeux indépendants à capteurs internes, avec
exclusion par cellule et par ambiance, face à ces trois références.*

**3. Données.**
- **WMG (Warwick).**
  - https://data.mendeley.com/datasets/bf6fksxpp2/2, CC BY 4.0 ; citer Gulsoy et al., *J. Energy Storage* 54 (2022) 105260.
  - Variables : `Voltage [V]`, `Current [A]`, `Surf Temp [C]`, `Core Temp [C]`.
  - Cellules : 1 Hz ; 3 cellules LG M50 instrumentées et 3 vierges ; 550 cycles.
  - Défauts connus : décrochage du capteur de VP011 (valeur sentinelle −3276,8 °C, un bloc entier manquant) ; résolution de 0,01 V et 0,1 °C.
- **TU Berlin.**
  - https://depositonce.tu-berlin.de/items/a3c12e52-32e0-4c9a-b1e0-4931cd5bf6fe, CC BY 4.0 ; doi:10.14279/depositonce-25110.
  - 3 cellules M50LT percées, sonde de type K au cœur ; 12 cycles de conduite × 5 températures ambiantes.
  - Fichier non téléchargé ici ; voies tension et courant non confirmées.

**4. Physique et architecture.**
- **Modèle thermique à deux états.**
  - $C_c\dot T_c=\dot Q-\frac{T_c-T_s}{R_c}$.
  - $C_s\dot T_s=\frac{T_c-T_s}{R_c}-\frac{T_s-T_{amb}}{R_u}$.
- **Source de chaleur.** $\dot Q=I(U_{ocv}-V)+IT\,\partial_T U_{ocv}$, avec une résistance dépendante du SOC. Le
  prototype montre qu'un terme $R_0I^2$ à résistance constante manque le pic de fin de décharge.
- **Identifiabilité.** Avec $T_s$ en entrée, seuls $\tau=C_cR_c$ et $R_0/C_c$ sont identifiables. Le prototype l'a
  vérifié : un ajustement à trois paramètres dérive vers une solution dégénérée.
- **Estimateur.** $\hat T_c=T_s+N_\phi(\cdot)$.
- **Perte.** $\mathcal L=\|\hat T_c-T_c\|^2_{\text{étiq.}}+\lambda\|C_c\Delta\hat T_c/\Delta t-\dot Q+(\hat T_c-T_s)/R_c\|^2_{\text{toutes cellules}}$.
  Le résidu physique s'applique aussi aux cellules non instrumentées.

**5. Références à battre.**
- **Prototype sur les données WMG** (exclusion d'une cellule à tour de rôle, cellule réservée) :

  | Méthode | RMSE (K) |
  |---|---|
  | Relation de Biot | 0,360 ± 0,094 |
  | Modèle localisé à un état | 0,402 ± 0,048 |
  | MLP fenêtré | **0,260 ± 0,044** |
  | PINN (λ = 1) | 0,391 ± 0,063 |

- **Résultats publiés sur d'autres données (non comparables).**
  - Bi-LSTM guidé par la physique : MAE 0,16 °C (*IEEE TTE* 2025, doi:10.1109/tte.2025.3649230).
  - PINN-KAN : MAE à cœur 0,752 °C (IECON 2025, doi:10.1109/iecon58223.2025.11221787).
- **Avertissement.** Un dépôt Zenodo de 2026, aujourd'hui retiré (erreur HTTP 410, résumé vu via OpenAlex),
  rapportait 0,13 K pour la relation de Biot et un PINN inverse moins précis. Il ne peut pas être cité, mais des
  relecteurs peuvent le connaître.

**6. Protocole.**
- **Découpages.** Exclusion par cellule au sein de chaque laboratoire ; croisement entre laboratoires.
- **Hors distribution.** Exclusion par température ambiante sur TU Berlin (5 niveaux) ; blocs de vieillissement tardifs.
- **Métriques.** RMSE, MAE, erreur maximale et RMSE au gradient maximal (K) ; couverture des intervalles ; résidu physique (W).
- **Ablations.**
  - Balayage de λ sur une cellule de validation, jamais sur la cellule de test.
  - Modèle de chaleur.
  - Points de collocation sur cellules non instrumentées.
  - Fraction d'étiquettes.
  - Bruit et quantification à 0,1 °C.

**7. Contributions et risques.**
- **Contributions.**
  - Premier banc d'essai à deux laboratoires et plusieurs ambiances.
  - Réponse chiffrée à la question « quand la physique aide-t-elle ? ».
  - Résidu semi-supervisé exploitant les cellules non instrumentées.
- **Risques et parades.**
  - (i) La physique n'aide pas (le prototype le montre déjà) : enrichir le modèle de chaleur, sinon publier un article de banc d'essai et d'identifiabilité.
  - (ii) Seulement 3 + 3 cellules instrumentées.
  - (iii) Cellules perturbées par l'instrumentation, et décalage de 0,3 à 0,5 K entre cœur et surface au repos : estimer un terme de décalage.

**8. Revues visées.**

| Rang | Revue | APC | IF et délais |
|---|---|---|---|
| 1 | IEEE TTE | 2 800 USD | NON VÉRIFIÉS |
| 2 | Applied Energy | 4 210 USD | NON VÉRIFIÉS |
| 3 | J. Power Sources | 4 010 USD | NON VÉRIFIÉS |
| 4 | eTransportation | 4 630 USD | NON VÉRIFIÉS |
| 5 | J. Energy Storage (repli) | 4 410 USD | NON VÉRIFIÉS |

**9. Plan de travail.**
- S1 : conversion des tables WMG à long terme (28 Go une fois décompressées) et téléchargement de TU Berlin.
- S2-3 : modèle de chaleur enrichi et test d'arrêt.
- S4-6 : filtre de Kalman différentiable et GRU.
- S7-8 : tests entre laboratoires et entre ambiances.
- S9-10 : ablations.
- S11-13 : rédaction.

**10. Critère d'arrêt (semaine 3).** L'estimateur informé par la physique, avec λ choisi sur une cellule de
validation, doit battre le MLP **et** la relation de Biot d'au moins 15 % de RMSE au gradient maximal, sur les
cellules réservées et sur au moins 3 des 5 ambiances. Le prototype actuel échoue à ce test. Un λ = 0,01 choisi
a posteriori donne 0,285 ± 0,076 K contre 0,310 ± 0,066 K pour le MLP en régime d'étiquettes rares : l'écart reste
dans un écart-type, ce n'est donc pas un résultat.

---

## 3. C4 — Loi de vieillissement structurée par Arrhenius et √t, extrapolée à des températures et profondeurs de décharge inédites

**1. Titre.** *Apprentissage informé par la cinétique du vieillissement calendaire et en cyclage, extrapolable en
température et en profondeur de décharge pour trois chimies Li-ion.*

**2. Question et lacune.** Un modèle hybride à structure Arrhenius/SEI prédit-il le vieillissement à une température
ou à une profondeur de décharge entièrement exclue de l'entraînement ? *Lacune : PiDDM (arXiv 2026) extrapole dans le
temps sur une seule chimie ; aucune étude trouvée n'exclut des températures entières sur NCA, NMC et LFP.*

**3. Données.**
- Sandia (Preger et al., *J. Electrochem. Soc.* 2020, doi:10.1149/1945-7111/abae37), via Battery Archive.
- ISU-ILCC : 238 cellules NMC pochette, doi:10.1016/j.xcrp.2024.101891.
- CALCE PLN (stockage) : 144 cellules, 4 températures × 3 SOC.
- Structure des fichiers NON VÉRIFIÉE.

**4. Physique.**
- Perte de capacité : $Q_{loss}=k_{cal}(T,\bar z)\sqrt t+k_{cyc}(T,c,\mathrm{DoD})\,\mathrm{Ah}^\beta$.
- Loi d'Arrhenius : $k=k_0e^{-\frac{E_a}{R}(\frac1T-\frac1{T_{ref}})}$.
- Terme optionnel de dépôt de lithium.
- Un réseau corrige $(k_0,E_a,\beta)$ ; la monotonie est imposée.

**5. Références à battre.**
- Ajustement empirique.
- Processus gaussien.
- MLP/GRU.
- PINN de type PiDDM.
- Chiffres publiés en exclusion par condition sur ces données : NON VÉRIFIÉS (aucun trouvé).

**6. Validation.**
- Exclusion par température, par profondeur de décharge et par chimie.
- Erreur sur la fin de vie.
- Calibration des intervalles.
- Ablations par terme physique.
- 5 graines.

**7. Risques.**
- Seulement 3 niveaux de température chez Sandia (parade : ajouter CALCE PLN).
- Copies Battery Archive à contrôler contre les données d'origine.
- Coude de vieillissement mal capté.

**8. Revues.**

| Revue | APC |
|---|---|
| J. Power Sources | 4 010 USD |
| Applied Energy | 4 210 USD |
| eTransportation | 4 630 USD |
| Energy and AI | 4 270 USD |

Facteurs d'impact : NON VÉRIFIÉS.

**9. Plan.** 12 semaines.

**10. Critère d'arrêt.** L'erreur de fin de vie doit être inférieure d'au moins 20 % à celle de l'ajustement
empirique et du processus gaussien.

---

## 4. C13 — Trajectoires d'impédance physiquement cohérentes (HPPC + SIE)

**1. Titre.** *Apprentissage cohérent avec Kramers-Kronig et Arrhenius du vieillissement de l'impédance, à partir
d'essais HPPC et de spectroscopie d'impédance (SIE) sur cellules vieillies en cycle de conduite.*

**2. Lacune.** L'association HPPC + SIE sur cellules vieillies en cycle de conduite, avec validation par exclusion
de cellule, n'a pas été trouvée.

**3. Données.**
- Stanford (Pozzato et al., *Data in Brief* 2022, OSF osf.io/qsabn) : 10 cellules M50T.
- Cambridge (Zenodo 3633835).
- Tongji (Zenodo 6405084).
- La licence OSF est à confirmer auprès des auteurs.

**4. Physique.**
- Circuit de Randles ou ligne de transmission.
- Résidu de Kramers-Kronig.
- Distribution des temps de relaxation (DRT) positive.
- $R_{ct}$ selon Arrhenius.
- Lien entre $R_{SEI}$ et la perte de capacité.

**5. Références.**
- Ajustement ECM suivi d'une régression.
- Régression par processus gaussien (GPR) sur SIE (Zhang 2020 ; chiffres NON VÉRIFIÉS).
- MLP.

**6. Validation.** Exclusion de cellule, de niveau de SOC et de régime de charge.

**7. Risques.**
- Créneau en forte croissance (45 publications en 2026 selon OpenAlex).
- Licence incertaine.
- Une seule température.

**8. Revues.**

| Revue | APC |
|---|---|
| J. Power Sources | 4 010 USD |
| Electrochimica Acta | 3 760 USD |
| J. Energy Storage | 4 410 USD |

**9. Plan.** 12 semaines.

**10. Critère d'arrêt.** Moins de 15 % de gain sur l'erreur d'impédance au bout de 3 semaines.

---

## 5. C11 — Défaut capteur ou défaut procédé sur un onduleur PV réel raccordé au réseau, par résidus physiques (hors priorité VE)

**1. Titre.** *Distinguer un capteur défaillant d'un procédé défaillant : résidus physiques blanchis sur le jeu
GPVS-Faults.*

**2. Lacune.** Aucune attribution capteur/procédé par résidus physiques sur ces données réelles parmi les 76 travaux
recensés.

**3. Données.** GPVS-Faults (https://data.mendeley.com/datasets/n76t439f65/1, CC BY 4.0, 205 Mo). Colonnes exactes
NON VÉRIFIÉES.

**4. Physique.**
- Bilan énergétique du bus continu.
- Dynamique des courants dq de l'onduleur.
- Modèle à une diode du générateur PV.
- Blanchiment des résidus sur les essais sains.

**5. Références.**
- Classifieurs de l'article d'origine (chiffres NON VÉRIFIÉS).
- Observateur par modes glissants.
- Auto-encodeur.

**6. Validation.**
- Apprentissage sur F0 uniquement.
- Retard de détection, fausses alarmes par heure, exactitude d'attribution.

**7. Risques.**
- Une seule installation.
- Le transfert vers l'onduleur de traction doit être argumenté, il n'est pas démontré.

**8. Revues.**
- IEEE TIE ou TPEL (2 800 USD).
- Energy Conversion and Management (4 500 USD).

**9. Plan.** 10 semaines.

**10. Critère d'arrêt.** Exactitude d'attribution inférieure à 90 % sur les défauts capteur.

---

## Ajustement après prototypes

Le score pondéré initial plaçait C1 (4,05) juste devant C5 (4,00). Le prototype C1 a ensuite montré que le PINN prévu
perdait face à un simple MLP fenêtré (0,391 K contre 0,260 K de RMSE), parce que le modèle physique simplifié est mal
spécifié au pic de fin de décharge. La note de profondeur physique de C1 a donc été ramenée de 3 à 2 (colonne
`post_prototype_note` de `scoring.csv`), ce qui fait passer C1 au deuxième rang. Le résultat du prototype C5 figure
ci-dessous et décide s'il conserve la première place.

## Résultats du prototype C5 : ce que disent les données réelles

D'après `prototypes/rw_health_nasa/results/RESULTS.md`. Il s'agit d'essais de faisabilité : les hyperparamètres ont été fixés à l'avance, et les cellules de test n'ont jamais servi au réglage.

**Intra-distribution (exclusion par cellule, RW25-28, 40 °C).** Environ 36 étiquettes d'entraînement par pli ; 12 références par cellule de test.

| Méthode | RMSE (Ah) | MAPE |
|---|---|---|
| **neural-ECM (sans étiquette)** | **0,118 ± 0,031** | 5,1 ± 0,8 % |
| Comptage coulométrique | 0,147 ± 0,042 | 7,1 % |
| Ridge | 0,154 ± 0,045 | 7,1 % |
| MLP | 0,537 ± 0,176 | 21,8 % |

- L'estimateur structuré par la physique est le meilleur des quatre.
- Le R² est négatif pour toutes les méthodes, car la plage de capacité au sein d'une cellule (1,7 à 2,15 Ah) est étroite au regard des erreurs. **Aucune méthode n'est encore satisfaisante.**
- La meilleure MAPE (5,1 %) reste au-dessus du seuil de 3 % fixé par le critère d'arrêt.

**Hors distribution (entraînement à 40 °C, test sur RW3-6 à température ambiante, charges uniformes, 146 références).** Toutes les méthodes échouent.

| Méthode | RMSE (Ah) | MAPE |
|---|---|---|
| Comptage coulométrique | 0,446 | 29 % |
| neural-ECM | 0,552 | 26 % (valeurs aberrantes jusqu'à 2,7 Ah) |
| Ridge | 1,21 | — |
| MLP | 8,8 | diverge |

Le diagnostic est net :
- Le résidu de tension du neural-ECM passe de 8 mV à 24,5 mV.
- La corrélation entre la capacité brute estimée et la référence tombe de 0,08-0,83 à 0,09.

L'OCV apprise à 40 °C, avec τ fixe et sans dépendance en température, ne se transpose donc pas. De plus, les cellules de test vieillissent jusqu'à 1,06 Ah, bien en dessous de tout ce qui a été vu à l'entraînement (≥ 1,68 Ah). Il faut la physique dépendante de la température prévue dans la fiche : R(T) selon Arrhenius, dU/dT, l'état thermique et une OCV ancrée sur un essai de référence.

**Verdict.** Le signal intra-distribution est positif mais faible : le modèle physique sans étiquette bat des régresseurs supervisés disposant de très peu d'étiquettes. L'échec hors distribution a une cause identifiable. C5 reste premier, sous réserve du test d'arrêt de la semaine 3 avec le modèle sensible à la température.

## Ordre final après les deux prototypes

1. **C5** : suivi de santé sans étiquette (NASA RW). Score 4,00, inchangé.
2. **C1** : température à cœur. Score ramené de 4,05 à 3,85 : le PINN prévu a priori perd face au MLP.
3. **C4** : loi de vieillissement Arrhenius/√t. Score 3,80 ; pas de prototype.
4. **C13** : cohérence de l'impédance HPPC/SIE. Score 3,80 ; pas de prototype.
5. **C11** : défauts capteur/procédé sur GPVS. Score 3,80 ; hors priorité VE.

Second choix hors classement : **C6** (données de flotte VE réelles). Meilleure adéquation éditoriale, mais aucune vérité terrain sur la capacité.
