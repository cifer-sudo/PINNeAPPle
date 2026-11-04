"""GPVS-Faults loader and physics-residual features, computed per grid cycle (200 samples at 100 us = 20 ms).

Data: Bakdi et al., Mendeley Data doi:10.17632/n76t439f65.1 (CC BY 4.0). Files Fxy.mat (MATLAB v7.3 tables),
converted to NPZ with mat-io. Columns: Time, Ipv, Vpv, Vdc, ia, ib, ic, va, vb, vc, Iabc, If, Vabc, Vf.
Sampling is 100 us (measured; the ReadMe's 9.9989 us is wrong). Faults are introduced "halfway".

Fault scenarios (from Wali & Khan, arXiv 2112.14842, which cites Bakdi et al. IJEPES 125 (2021) 106457):
F1 inverter IGBT fault; F2 feedback (phase-voltage) sensor fault; F3 grid voltage anomaly; F4 partial shading;
F5 15 % open circuit in the PV array; F6 boost PI gain fault; F7 boost PI time-constant fault.
Only F2 is a SENSOR fault; F1, F3-F7 are PROCESS faults (F3 is external to the plant).

Physics residuals (all dimensionless after whitening on healthy data):
  Measurement-redundancy block (should be violated by sensor faults, not by process faults):
    r_vsum   = rms(va+vb+vc) / Vn                       3-wire, balanced source: phase voltages sum to ~0
    r_vmag   = (sqrt(2/3 (va^2+vb^2+vc^2)) - Vabc)/Vn    measured space-vector magnitude vs PMU estimate
    r_vimb   = std of the three phase-voltage rms values / mean   (one bad sensor breaks symmetry)
    r_isum   = rms(ia+ib+ic) / In
    r_imag   = (sqrt(2/3 (ia^2+ib^2+ic^2)) - Iabc)/In
    r_iimb   = std of phase-current rms / mean
  Process block (energy and control physics):
    r_pbal   = (P_ac - eta P_pv) / P_n       DC/AC power balance through the converter chain
    r_vdc    = (Vdc - Vdc_ref)/Vdc_ref       DC-link regulation (ref = healthy median of the same mode)
    r_dvdc   = C Vdc dVdc/dt / P_n proxy     DC-link energy-rate (time derivative of Vdc^2 / 2)
    r_ppv    = (P_pv - P_pv_ref)/P_n         PV power vs healthy operating point
    r_vpv    = (Vpv - Vpv_ref)/Vpv_ref       PV operating voltage vs healthy (MPPT/IPPT point)
    r_freq   = If - Vf                       current/voltage frequency consistency
"""
from __future__ import annotations

import os

import numpy as np

NPZ = os.environ.get("GPVS_NPZ", "/home/user/data_raw/gpvs/npz")
N_CYC = 200
FAULTS = {"F0": "healthy", "F1": "inverter IGBT", "F2": "feedback voltage sensor", "F3": "grid voltage anomaly",
          "F4": "partial shading", "F5": "PV open circuit 15%", "F6": "boost PI gain", "F7": "boost PI time constant"}
SENSOR_FAULTS = {"F2"}
RED = ["r_vsum", "r_vmag", "r_vimb", "r_isum", "r_imag", "r_iimb"]
PROC = ["r_pbal", "r_vdc", "r_dvdc", "r_ppv", "r_vpv", "r_freq"]


def load(name: str, npz: str = NPZ) -> dict:
    z = np.load(os.path.join(npz, f"{name}.npz"))
    return {k: z[k] for k in z.files}


def cycles(d: dict, n: int = N_CYC):
    m = len(d["Time"]) // n
    return {k: v[: m * n].reshape(m, n) for k, v in d.items()}


def raw_features(d: dict) -> dict:
    """Per-cycle physical quantities (no normalisation yet)."""
    c = cycles(d)
    va, vb, vc, ia, ib, ic = (c[k] for k in ("va", "vb", "vc", "ia", "ib", "ic"))
    rms = lambda x: np.sqrt(np.mean(x ** 2, axis=1))
    vrms = np.stack([rms(va), rms(vb), rms(vc)], 1)
    irms = np.stack([rms(ia), rms(ib), rms(ic)], 1)
    vmag = np.sqrt(2 / 3 * np.mean(va ** 2 + vb ** 2 + vc ** 2, axis=1))
    imag = np.sqrt(2 / 3 * np.mean(ia ** 2 + ib ** 2 + ic ** 2, axis=1))
    vdc = c["Vdc"].mean(1)
    return {
        "t": c["Time"].mean(1),
        "vsum": rms(va + vb + vc), "isum": rms(ia + ib + ic),
        "vmag": vmag, "Vabc": c["Vabc"].mean(1), "imag": imag, "Iabc": c["Iabc"].mean(1),
        "vimb": vrms.std(1) / vrms.mean(1), "iimb": irms.std(1) / np.maximum(irms.mean(1), 1e-6),
        "pac": np.mean(va * ia + vb * ib + vc * ic, axis=1), "ppv": np.mean(c["Vpv"] * c["Ipv"], axis=1),
        "vdc": vdc, "vpv": c["Vpv"].mean(1), "If": c["If"].mean(1), "Vf": c["Vf"].mean(1),
    }


def residuals(f: dict, ref: dict) -> np.ndarray:
    """Columns RED + PROC. `ref` holds healthy-operation constants of the same mode (fitted on F0 training part)."""
    vn, inn, pn = ref["Vn"], ref["In"], ref["Pn"]
    dvdc2 = np.r_[0.0, np.diff(0.5 * f["vdc"] ** 2)] / (N_CYC * 1e-4)  # V^2/s
    cols = {
        "r_vsum": f["vsum"] / vn, "r_vmag": (f["vmag"] - f["Vabc"]) / vn, "r_vimb": f["vimb"],
        "r_isum": f["isum"] / inn, "r_imag": (f["imag"] - f["Iabc"]) / inn, "r_iimb": f["iimb"],
        "r_pbal": (f["pac"] - ref["eta"] * f["ppv"]) / pn, "r_vdc": (f["vdc"] - ref["vdc"]) / ref["vdc"],
        "r_dvdc": ref["C"] * dvdc2 / pn, "r_ppv": (f["ppv"] - ref["ppv"]) / pn,
        "r_vpv": (f["vpv"] - ref["vpv"]) / ref["vpv"], "r_freq": f["If"] - f["Vf"],
    }
    return np.stack([cols[k] for k in RED + PROC], 1)


def fit_reference(f: dict, C: float = 1e-3) -> dict:
    """Healthy constants from F0 training cycles. eta = least-squares P_ac/P_pv. C (F) is a nominal DC-link value
    used only to scale r_dvdc (not identified; whitening makes the scale irrelevant)."""
    ppv, pac = f["ppv"], f["pac"]
    eta = float(np.dot(ppv, pac) / np.dot(ppv, ppv))
    return {"Vn": float(np.median(f["Vabc"])), "In": float(np.median(f["Iabc"])), "Pn": float(np.median(ppv)),
            "eta": eta, "vdc": float(np.median(f["vdc"])), "ppv": float(np.median(ppv)), "vpv": float(np.median(f["vpv"])),
            "C": C}
