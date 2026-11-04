"""Tables and figures for the core-temperature prototype (reads results*/rows.json)."""
import collections
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

M = ["biot", "lumped", "mlp", "pinn"]
LAB = {"biot": "B1 Biot quasi-steady", "lumped": "B2 lumped 1-state", "mlp": "DD windowed MLP", "pinn": "PINN (MLP + residual, lambda=1)"}


def agg(path):
    R = json.load(open(path))
    a = collections.defaultdict(list)
    for r in R:
        a[(r["scenario"], r["method"])].append(r)
    return a


def ms(rs, k):
    v = np.array([r[k] for r in rs])
    return v.mean(), v.std()


main = agg("results/rows.json")
post = {lam: agg(f"results_posthoc_lam{lam}/rows.json") for lam in ("0.1", "0.01") if os.path.exists(f"results_posthoc_lam{lam}/rows.json")}
lines = ["# Prototype C1 — core temperature (WMG LG M50, embedded thermocouples)", "",
         "Leave-one-instrumented-cell-out (3 folds: VP010, VP011, VP012). DD and PINN: 3 seeds per fold (n = 9); B1, B2",
         "deterministic (n = 3). Mean ± std over folds (and seeds). Errors on core temperature in kelvin; 'peak' = samples",
         "with the 10 % largest true core-surface gradient; residual = RMS of the one-state model residual (W) under the",
         "parameters fitted on the training cells. Hyper-parameters fixed before looking at test cells (lambda = 1, 6 epochs,",
         "window 5 min, MLP 64x64 tanh). Non-instrumented cells VP016-018 enter only the PINN residual.", "",
         "| scenario | method | RMSE (K) | MAE (K) | max (K) | RMSE peak (K) | R2 | residual (W) | n |", "|---|---|---|---|---|---|---|---|---|"]
for s in ("full", "scarce"):
    for m in M:
        rs = main[(s, m)]
        f = lambda k: ms(rs, k)
        lines.append(f"| {s} | {LAB[m]} | {f('rmse')[0]:.3f} ± {f('rmse')[1]:.3f} | {f('mae')[0]:.3f} ± {f('mae')[1]:.3f} | "
                     f"{f('max')[0]:.2f} ± {f('max')[1]:.2f} | {f('rmse_peak')[0]:.3f} ± {f('rmse_peak')[1]:.3f} | {f('r2')[0]:.3f} | "
                     f"{f('phys_res_rms_W')[0]:.3f} | {len(rs)} |")
lines += ["", "**Post-hoc sensitivity (NOT a pre-registered result; lambda chosen after seeing lambda = 1 fail):**", "",
          "| scenario | lambda | PINN RMSE (K) | PINN RMSE peak (K) | residual (W) |", "|---|---|---|---|---|"]
for lam, a in post.items():
    for s in ("full", "scarce"):
        rs = a[(s, "pinn")]
        lines.append(f"| {s} | {lam} | {ms(rs, 'rmse')[0]:.3f} ± {ms(rs, 'rmse')[1]:.3f} | {ms(rs, 'rmse_peak')[0]:.3f} ± {ms(rs, 'rmse_peak')[1]:.3f} | {ms(rs, 'phys_res_rms_W')[0]:.3f} |")
open("results/RESULTS.md", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))

# Figure 1: bars
fig, ax = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
for j, s in enumerate(("full", "scarce")):
    keys = M + [f"pinn lam={l}" for l in post]
    mu, sd = [], []
    for k in keys:
        rs = main[(s, k)] if k in M else post[k.split("=")[1]][(s, "pinn")]
        mu.append(ms(rs, "rmse")[0]); sd.append(ms(rs, "rmse")[1])
    col = ["#8c8c8c", "#5f7f9f", "#d08c2f", "#3a7d44"] + ["#9ccc9c"] * len(post)
    ax[j].bar(range(len(keys)), mu, yerr=sd, color=col, capsize=3)
    ax[j].set_xticks(range(len(keys)), ["Biot", "lumped", "MLP", "PINN\nlam=1"] + [f"PINN\nlam={l}\n(post-hoc)" for l in post], fontsize=8)
    ax[j].set_title({"full": "S1 all labels", "scarce": "S2 labels from first 20 cycles only"}[s], fontsize=10)
    ax[j].grid(axis="y", alpha=0.3)
ax[0].set_ylabel("core temperature RMSE on held-out cell (K)")
fig.tight_layout()
fig.savefig("results/fig_rmse_bars.png", dpi=160)

# Figure 2: time series, held-out VP012, last block, one window
F = np.load("results/fig_series.npy", allow_pickle=True).item()
t, ts, tc, _ = F["scarce|VP012|biot"]
k0 = int(np.nanargmax(tc - ts)) - 360
sl = slice(max(k0, 0), max(k0, 0) + 1080)
fig, ax = plt.subplots(figsize=(9, 3.6))
th = (t[sl] - t[sl][0]) / 3600
ax.plot(th, tc[sl], "k", lw=2, label="core (thermocouple)")
ax.plot(th, ts[sl], color="0.6", lw=1, label="surface")
for m, c in zip(M, ["#8c8c8c", "#5f7f9f", "#d08c2f", "#3a7d44"]):
    ax.plot(th, F[f"scarce|VP012|{m}"][3][sl], color=c, lw=1.2, ls="--" if m in ("biot", "lumped") else "-", label=LAB[m])
ax.set_xlabel("time (h)")
ax.set_ylabel("temperature (C)")
ax.set_title("Held-out cell VP012, last ageing block (scenario S2), seed 0", fontsize=10)
ax.legend(fontsize=7, ncol=2)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("results/fig_timeseries_VP012.png", dpi=160)
print("figures written")
