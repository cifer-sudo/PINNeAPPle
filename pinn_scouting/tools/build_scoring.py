"""scoring.csv: 0-5 per criterion, weighted total (weights from the brief), one-line reason per score."""
import csv

W = {"data": 0.20, "physics": 0.20, "novelty": 0.20, "feasibility": 0.15, "q1fit": 0.15, "ev": 0.10}
S = [
 ("C1", "Core temperature, embedded thermocouples, two labs",
  5, "Two independent open CC BY datasets with DIRECT core-temperature measurement (WMG 6 cells/550 cycles, TU Berlin 3 cells/5 ambients); WMG inspected here",
  3, "Two-state thermal ODE is real physics but simple; prototype shows only tau=Cc*Rc and R0/Cc are identifiable from surface T",
  3, "139 hits (40 in 2026); embedded-sensor + ageing + cross-ambient combination not found, but a withdrawn 2026 record reports the Biot relation beats an inverse PINN",
  5, "1 Hz, few states, CPU-only; data already converted; prototype ran in minutes",
  4, "Fits IEEE TTE / Applied Energy / J. Power Sources thermal-management scope; needs a strong OOD result to clear review",
  5, "Thermal safety and fast-charge limits of EV cells; direct BMS value"),
 ("C5", "Health-aware ECM evolution from random EV-like loads (NASA RW)",
  4, "28 cells, 7 load/temperature groups, measured reference capacity and pulse tests; no licence stated (US Gov work); 18650 not automotive-grade",
  4, "ECM + thermal + health dynamics constrain capacity and resistance on every second of operation; neural OCV inside the ODE",
  4, "56 hits for the dataset family; the closest method paper (JES 2026, health-aware ECM evolution) not readable: must be checked",
  4, "1.07 GB, CPU/1 GPU; prototype fit in minutes; identifiability of Q vs OCV scale needs care",
  4, "eTransportation / Applied Energy / IEEE TTE (label-scarce SOH from operation data is an editor topic)",
  4, "Random EV-like duty is closer to vehicle use than CC cycling; 18650 consumer cells limit industrial claim"),
 ("C4", "Arrhenius / sqrt-t ageing law, leave-one-temperature-out",
  4, "Sandia (3 chemistries x T x DoD x rate) + ISU-ILCC 238 cells + CALCE storage; files not inspected here",
  4, "Kinetic structure (Arrhenius, SEI sqrt-t, throughput) is exactly what should extrapolate",
  3, "49 hits, 33 in 2026; PiDDM (arXiv 2026) already puts Arrhenius SEI kinetics into training (time extrapolation on XJTU)",
  4, "Small tabular cycle-level data; 10-14 weeks",
  4, "J. Power Sources / Applied Energy / eTransportation lifetime-modelling scope",
  4, "Warranty and second-life ageing prediction for EV packs"),
 ("C13", "Impedance (HPPC/EIS) ageing trajectories, physics-consistent",
  4, "Stanford 10 cells with HPPC + EIS on UDDS ageing; Cambridge and Tongji EIS (CC BY); OSF licence unclear",
  4, "Kramers-Kronig, DRT positivity, Arrhenius R_ct and R_SEI-capacity link",
  3, "57 hits, 45 in 2026: fastest-growing niche of the list",
  4, "Light data; 10-12 weeks",
  4, "J. Power Sources / Electrochimica Acta / JES",
  4, "Diagnostics with on-board passive EIS is an industry trend"),
 ("C11", "Sensor vs process faults with physics residuals (GPVS-Faults)",
  4, "Real lab grid-tied PV with labelled sensor and process faults, CC BY 4.0; one plant",
  4, "PV single-diode, DC-link energy balance, dq inverter dynamics -> structured residuals",
  4, "Physics-residual sensor/process attribution on GPVS not found in 76 hits",
  4, "205 MB; the user already has the simulated pipeline",
  4, "IEEE TIE / TPEL / IJEPES",
  2, "PV, not EV; method transfers to traction-inverter sensor faults but data does not"),
 ("C6", "Field EV pack resistance / capacity (Stanford, Korea fleet, BMW i3)",
  3, "Real vehicles but no capacity ground truth; NC licence (Stanford), subscription (Korea), login (BMW)",
  4, "Pack ECM + thermal + Arrhenius",
  3, "Lab-to-field PI domain adaptation already in TIE 2026, TII 2026",
  3, "Heterogeneous logging, asynchronous timestamps; 12-16 weeks",
  5, "Exactly what eTransportation / TTE / Applied Energy want now",
  5, "Fleet-level BMS value"),
 ("C7", "PMSM temperature (Paderborn)",
  5, "185 h measured rotor/stator temperatures, CC BY-SA",
  4, "LPTN + loss model", 1, "Dataset owners' TNN (EAAI 2023) is already the physics-informed answer; many follow-ups",
  5, "Small data; 8 weeks", 3, "Recent follow-ups on this dataset land in Energies / AI / Automotive Innovation", 5, "Traction motor"),
 ("C2", "SOC PINN incl. cross-temperature (McMaster, CALCE)",
  4, "Measured but one cell per dataset (no cell split)", 4, "ECM + thermal",
  1, "293 hits, 194 in 2026; LG HG2 cross-temperature PINN already published (Batteries 2026)",
  5, "Trivial", 3, "Saturated topic -> mostly mid-tier venues now", 5, "BMS core function"),
 ("C12", "Core loss / hysteresis (MagNet)",
  5, "Large measured database", 4, "Jiles-Atherton / iGSE", 1, "159 hits, 106 in 2026 + MagNet Challenge",
  4, "8-12 weeks", 4, "TPEL / TMAG", 3, "OBC / DC-DC magnetics"),
 ("C8", "PMSM inter-turn short circuit severity",
  3, "HUST: subscription and 67 GB; Mendeley: currents only (no voltage)", 4, "Fault dq model with hidden fault current",
  3, "13 hits, 11 in 2026 (TIE 2026 fault-model-informed NN)", 3, "Data volume and access", 4, "TIE / TTE / TII", 4, "Traction motor reliability"),
 ("C3", "SOH PINN across protocols (XJTU, Severson, Tongji)",
  5, "Large measured datasets", 2, "Empirical degradation residuals are weak constraints",
  1, "833 hits; Nat. Commun. 2024 reference PINN on the same datasets", 5, "Easy", 3, "Saturated", 4, "SOH"),
 ("C10", "Charging-session physics (ACN-Data)",
  3, "Real station data, registration, no licence, no vehicle SOC", 2, "Only CC-CV taper", 3, "Few battery-side papers",
  4, "Easy", 3, "TSG / Applied Energy (grid side)", 4, "Charging infrastructure"),
 ("C9", "IGBT / MOSFET ageing (NASA)",
  2, "6 IGBTs, MOSFET reference document offline", 3, "Thermal / Coffin-Manson", 3, "42 hits",
  4, "Light", 3, "TPEL needs more devices", 3, "Inverter reliability"),
]
rows = []
for cid, title, d, dr, p, pr, n, nr, f, fr, q, qr, e, er in S:
    tot = W["data"] * d + W["physics"] * p + W["novelty"] * n + W["feasibility"] * f + W["q1fit"] * q + W["ev"] * e
    rows.append({"id": cid, "title": title, "data_realism(20%)": d, "why_data": dr, "physics_depth(20%)": p, "why_physics": pr,
                 "novelty(20%)": n, "why_novelty": nr, "feasibility(15%)": f, "why_feasibility": fr, "q1_fit(15%)": q, "why_q1": qr,
                 "ev_relevance(10%)": e, "why_ev": er, "weighted_total": round(tot, 2)})
rows.sort(key=lambda r: (-r["weighted_total"], -r["ev_relevance(10%)"]))
for i, r in enumerate(rows, 1):
    r["rank"] = i
with open("scoring.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["rank"] + [k for k in rows[0] if k != "rank"])
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print(r["rank"], r["id"], r["weighted_total"], r["title"])
