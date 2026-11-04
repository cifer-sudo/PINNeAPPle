"""Tables and figures for the NASA RW capacity prototype (reads results/rows.json and pred_*.npy)."""
import collections
import glob
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

M = ["coulomb", "ridge", "mlp", "necm"]
LAB = {"coulomb": "Coulomb count to cut-off (calibrated)", "ridge": "DD ridge on cycle features", "mlp": "DD MLP on cycle features",
       "necm": "neural-ECM (voltage only, label-free) + calibration"}
R = json.load(open("results/rows.json"))
A = collections.defaultdict(list)
for r in R:
    A[(r["split"], r["method"])].append(r)
L = ["# Prototype C5 — capacity from random-walk operation (NASA RW)", "",
     "ID = leave-one-cell-out inside RW25-28 (40 C, skewed high), 4 folds; OOD = train on RW25-28, test on RW3-6",
     "(room temperature, uniform 0.5-4 A, deeper ageing). Each reference capacity (1 A to 3.2 V) is predicted from the",
     "5 RW cycles that follow it. coulomb/ridge: deterministic (one value per fold); mlp/necm: 3 seeds per fold.",
     "Mean ± std over folds x seeds. The neural-ECM never sees a capacity label; only its scale calibration (a Q + b)",
     "is fitted on the training cells.", "",
     "| split | method | RMSE (Ah) | MAE (Ah) | max (Ah) | MAPE (%) | R2 | n refs per fold | voltage RMSE test (mV) |",
     "|---|---|---|---|---|---|---|---|---|"]
for s in ("ID", "OOD"):
    for m in M:
        rs = A[(s, m)]
        f = lambda k: (np.mean([r[k] for r in rs]), np.std([r[k] for r in rs]))
        vr = f"{1000 * f('v_rmse_test_V')[0]:.1f}" if m == "necm" else "-"
        L.append(f"| {s} | {LAB[m]} | {f('rmse_Ah')[0]:.3f} ± {f('rmse_Ah')[1]:.3f} | {f('mae_Ah')[0]:.3f} ± {f('mae_Ah')[1]:.3f} | "
                 f"{f('max_Ah')[0]:.3f} | {f('mape_pct')[0]:.2f} ± {f('mape_pct')[1]:.2f} | {f('r2')[0]:.3f} | "
                 f"{int(np.mean([r['n'] for r in rs]))} | {vr} |")
open("results/RESULTS.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))

fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
for j, s in enumerate(("ID", "OOD")):
    mu = [np.mean([r["rmse_Ah"] for r in A[(s, m)]]) for m in M]
    sd = [np.std([r["rmse_Ah"] for r in A[(s, m)]]) for m in M]
    ax[j].bar(range(4), mu, yerr=sd, color=["#8c8c8c", "#5f7f9f", "#d08c2f", "#3a7d44"], capsize=3)
    ax[j].set_xticks(range(4), ["Coulomb", "ridge", "MLP", "neural-ECM"], fontsize=9)
    ax[j].set_title({"ID": "ID: leave-one-cell-out (40 C)", "OOD": "OOD: train 40 C -> test room T, other loads"}[s], fontsize=10)
    ax[j].grid(axis="y", alpha=0.3)
ax[0].set_ylabel("reference-capacity RMSE (Ah)")
fig.tight_layout()
fig.savefig("results/fig_rmse_bars.png", dpi=160)

f = sorted(glob.glob("results/pred_OOD_*.npy"))
if f:
    P = np.load(f[0], allow_pickle=True).item()
    fig, ax = plt.subplots(figsize=(4.6, 4.2))
    lim = [min(P["y"].min(), 0.9), max(P["y"].max(), 2.2)]
    ax.plot(lim, lim, "k:", lw=1)
    for m, c in zip(M, ["#8c8c8c", "#5f7f9f", "#d08c2f", "#3a7d44"]):
        ax.scatter(P["y"], P[m], s=10, color=c, label=m, alpha=0.8)
    ax.set_xlabel("reference capacity (Ah)")
    ax.set_ylabel("estimate (Ah)")
    ax.set_title("OOD cells RW3-6 (seed 0)", fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig("results/fig_ood_scatter.png", dpi=160)
print("figures written")
