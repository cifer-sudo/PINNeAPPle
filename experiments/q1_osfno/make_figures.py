"""Deliverable figures, generated only from result files: figures/F*.pdf + .png, and the plotted numbers in
figures/data/F*.csv. Colours: validated categorical palette (fixed slot per model family, never cycled); identity is
also carried by marker shape / line style and direct labels.
usage: python make_figures.py
"""
import csv
import glob
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from q1lib import RESULTS
from stats_q1 import ci, load

OUT = RESULTS.parent / "figures"
(OUT / "data").mkdir(parents=True, exist_ok=True)
TASKS = ["misalignment", "unbalance", "bearings", "all", "comfaulda7"]
TN = {"misalignment": "T1 misalignment", "unbalance": "T2 unbalance", "bearings": "T3 bearings", "all": "T4 ten states",
      "comfaulda7": "C1 COMFAULDA"}
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4",
                                                           "#008300", "#6250d6", "#e34948")
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
                     "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
                     "figure.facecolor": "white", "axes.facecolor": "white", "lines.linewidth": 2, "pdf.fonttype": 42})
# model -> (label, family colour, marker)
M = {"rf": ("RF", BLUE, "o"), "mlp": ("MLP", BLUE, "s"), "kan": ("KAN", BLUE, "^"), "svm": ("SVM-RBF", BLUE, "v"),
     "xgb": ("XGBoost", BLUE, "D"), "cnn-spec": ("CNN (order spectra)", ORANGE, "o"),
     "phase3:cnn-tuned": ("CNN nested-tuned", ORANGE, "s"), "phase5:cnn-spec-rob": ("CNN robust (5b)", ORANGE, "D"),
     "phase6:cnn-mb": ("CNN + band envelopes", ORANGE, "^"),
     "osfno-A-nospeed": ("OS-FNO A (no speed)", AQUA, "o"), "osfno-B-head": ("OS-FNO B (speed in head)", AQUA, "s"),
     "osfno-C-film": ("OS-FNO C = OC-FNO (FiLM)", AQUA, "v"), "osfno-E-phys": ("OS-FNO E (physical speed)", AQUA, "^"),
     "phase3:fno-tuned": ("FNO nested-tuned", AQUA, "D"),
     "phase5:stack-rf-mlp-cnn": ("Stack RF+MLP+CNN (nested gate)", VIOLET, "o"),
     "fuse-rf+cnn-spec": ("RF+CNN fusion α=0.5 (exploratory)", VIOLET, "s"), "phase5:rf-rob": ("RF robust (5b)", BLUE, "P")}


def get(key, task):
    exp, m = key.split(":") if ":" in key else ("phase1", key)
    return load(exp, m, task)


def save(fig, name, header=None, rows=None):
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    if rows is not None:
        with open(OUT / "data" / f"{name}.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)


def f01_main():
    order = ["rf", "mlp", "kan", "svm", "xgb", "cnn-spec", "phase3:cnn-tuned", "phase5:cnn-spec-rob", "osfno-A-nospeed",
             "osfno-B-head", "osfno-C-film", "osfno-E-phys", "phase3:fno-tuned", "fuse-rf+cnn-spec", "phase5:stack-rf-mlp-cnn"]
    fig, axs = plt.subplots(1, 5, figsize=(12, 4.2), sharey=True)
    rows = []
    for ax, t in zip(axs, TASKS):
        for i, k in enumerate(order):
            R = get(k, t)
            if len(R) < 5:
                continue
            f = np.array([r["pooled"]["macro_f1"] for r in R])
            lab, col, mk = M[k]
            ax.errorbar(f.mean(), i, xerr=ci(f)[1], fmt=mk, color=col, ms=5, elinewidth=1.2, capsize=0)
            rows.append([t, lab, f"{f.mean():.4f}", f"{ci(f)[1]:.4f}"])
        best_feat = max(np.mean([r["pooled"]["macro_f1"] for r in get(k, t)]) for k in ["rf", "mlp", "kan", "svm", "xgb"])
        ax.axvline(best_feat, color=INK2, lw=0.8, ls=":")
        ax.set_title(TN[t], fontsize=8.5, color=INK)
        ax.set_xlabel("macro-F1 (held-out terciles)")
        ax.grid(axis="y", visible=False)
    axs[0].set_yticks(range(len(order)), [M[k][0] for k in order])
    axs[0].invert_yaxis()
    fig.suptitle("Speed-tercile protocol: mean ± 95 % CI over 5 seeds (dotted line = best feature baseline)",
                 fontsize=9, color=INK, x=0.55)
    save(fig, "F01_main_macro_f1", ["task", "model", "macro_f1_mean", "ci95_halfwidth"], rows)


def f02_bands():
    order = ["rf", "mlp", "svm", "xgb", "cnn-spec", "phase5:cnn-spec-rob", "osfno-A-nospeed", "osfno-B-head",
             "osfno-C-film", "osfno-E-phys", "fuse-rf+cnn-spec", "phase5:stack-rf-mlp-cnn"]
    cols = [(t, b) for t in TASKS for b in ("low", "mid", "high")]
    A = np.full((len(order), len(cols)), np.nan)
    for i, k in enumerate(order):
        for j, (t, b) in enumerate(cols):
            R = get(k, t)
            if len(R) >= 5:
                A[i, j] = np.mean([v["macro_f1"] for r in R for n, v in r["per_split"].items() if f"_{b}_" in n])
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("blue", ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
    fig, ax = plt.subplots(figsize=(11, 4.6))
    im = ax.imshow(A, cmap=cmap, vmin=0.4, vmax=1.0, aspect="auto")
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            if not np.isnan(A[i, j]):
                ax.text(j, i, f"{A[i, j]:.2f}", ha="center", va="center", fontsize=6.5,
                        color="white" if A[i, j] > 0.78 else INK)
    ax.set_xticks(range(len(cols)), [f"{TN[t].split()[0]}\n{b}" for t, b in cols], fontsize=7)
    ax.set_yticks(range(len(order)), [M[k][0] for k in order])
    for x in (2.5, 5.5, 8.5, 11.5):
        ax.axvline(x, color="white", lw=2)
    ax.grid(False)
    fig.colorbar(im, ax=ax, fraction=0.025, label="macro-F1 of the held-out tercile")
    ax.set_title("Per held-out speed tercile (low and high are extrapolation), 5-seed mean", fontsize=9)
    save(fig, "F02_band_heatmap", ["model"] + [f"{t}_{b}" for t, b in cols],
         [[M[k][0]] + [f"{v:.4f}" for v in A[i]] for i, k in enumerate(order)])


def f03_speed_curves():
    d = json.load(open(RESULTS / "phase8_calibration.json"))
    models = [("rf", "rf"), ("cnn-spec", "cnn-spec"), ("osfno-A-nospeed", "osfno-A-nospeed"), ("cnn-spec-rob", "phase5:cnn-spec-rob")]
    fig, axs = plt.subplots(1, 5, figsize=(12, 2.8), sharey=True)
    rows = []
    for ax, t in zip(axs, TASKS):
        for short, key in models:
            c = d.get(f"{t}/{short}")
            if not c:
                continue
            x = [(b["speed_lo"] + b["speed_hi"]) / 2 for b in c["speed_curve"]]
            y = [b["acc"] for b in c["speed_curve"]]
            lab, col, mk = M[key]
            ax.plot(x, y, marker=mk, ms=4, color=col, ls="--" if "rob" in short else "-", label=lab)
            rows += [[t, lab, f"{a:.2f}", f"{b:.4f}"] for a, b in zip(x, y)]
        ax.set_title(TN[t], fontsize=8.5)
        ax.set_xlabel("shaft speed (Hz)")
    axs[0].set_ylabel("accuracy (5-seed vote)")
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, fontsize=7, bbox_to_anchor=(0.5, -0.1))
    fig.suptitle("Accuracy against speed: 10 equal-count speed bins, each run predicted by the model that never saw its tercile",
                 fontsize=9, x=0.5, y=1.04)
    save(fig, "F03_speed_resolved_accuracy", ["task", "model", "speed_hz_bin_centre", "accuracy"], rows)


def f04_robust_speed():
    d = json.load(open(RESULTS / "phase8_robust_summary.json"))
    models = [("rf", "rf"), ("rf-rob", "phase5:rf-rob"), ("cnn-spec", "cnn-spec"), ("cnn-spec-rob", "phase5:cnn-spec-rob"),
              ("osfno-A-nospeed", "osfno-A-nospeed"), ("osfno-E-phys", "osfno-E-phys")]
    E = [-0.05, -0.02, -0.01, 0.0, 0.01, 0.02, 0.05]
    fig, axs = plt.subplots(1, 5, figsize=(12, 2.9), sharey=True)
    rows = []
    for ax, t in zip(axs, TASKS):
        for short, key in models:
            c = d.get(f"{t}/{short}")
            if not c:
                continue
            y = [c["clean:None"] if e == 0 else c[f"speed:{e}"] for e in E]
            lab, col, mk = M[key]
            ax.plot([100 * e for e in E], y, marker=mk, ms=4, color=col, ls="--" if "rob" in short else "-", label=lab)
            rows += [[t, lab, 100 * e, f"{v:.4f}"] for e, v in zip(E, y)]
        ax.axvspan(-2, 2, color=GRID, alpha=0.5, lw=0)
        ax.set_title(TN[t], fontsize=8.5)
        ax.set_xlabel("speed-estimate error (%)")
    axs[0].set_ylabel("macro-F1")
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=6, fontsize=7, bbox_to_anchor=(0.5, -0.1))
    fig.suptitle("Test-time speed error (grey band = range of the 5b training jitter); dashed = robust training",
                 fontsize=9, y=1.04)
    save(fig, "F04_robustness_speed_error", ["task", "model", "speed_error_percent", "macro_f1"], rows)


def f05_sensor():
    d = json.load(open(RESULTS / "phase8_robust_summary.json"))
    models = [("rf", "rf"), ("rf-rob", "phase5:rf-rob"), ("mlp", "mlp"), ("xgb", "xgb"), ("cnn-spec", "cnn-spec"),
              ("cnn-spec-rob", "phase5:cnn-spec-rob"), ("osfno-A-nospeed", "osfno-A-nospeed"), ("osfno-B-head", "osfno-B-head"),
              ("osfno-E-phys", "osfno-E-phys")]
    fig, axs = plt.subplots(1, 5, figsize=(12, 3.4), sharey=True)
    rows = []
    for ax, t in zip(axs, TASKS):
        for i, (short, key) in enumerate(models):
            c = d.get(f"{t}/{short}")
            if not c:
                continue
            dead = [v for k, v in c.items() if k.startswith("dead")]
            lab, col, mk = M.get(key, (short, BLUE, "o"))
            ax.plot([min(dead), c["clean:None"]], [i, i], color=col, lw=1.5, alpha=0.6)
            ax.plot(c["clean:None"], i, marker=mk, color=col, ms=5)
            ax.plot(np.mean(dead), i, marker=mk, color=col, ms=5, mfc="white", mew=1.5)
            ax.plot(min(dead), i, marker="|", color=col, ms=8)
            rows.append([t, lab, f"{c['clean:None']:.4f}", f"{np.mean(dead):.4f}", f"{min(dead):.4f}"])
        ax.set_title(TN[t], fontsize=8.5)
        ax.set_xlabel("macro-F1")
        ax.grid(axis="y", visible=False)
    axs[0].set_yticks(range(len(models)), [M.get(k, (s,))[0] for s, k in models])
    axs[0].invert_yaxis()
    fig.suptitle("One dead sensor: filled = clean, open = mean over sensors, bar = worst sensor", fontsize=9, y=1.02)
    save(fig, "F05_dead_sensor", ["task", "model", "clean", "dead_mean", "dead_worst"], rows)


def f06_tradeoff():
    from phase5b_report import score
    pairs = [("rf", "rf-rob", "rf", "phase5:rf-rob"), ("cnn-spec", "cnn-spec-rob", "cnn-spec", "phase5:cnn-spec-rob")]
    others = [("mlp", "mlp"), ("xgb", "xgb"), ("osfno-A-nospeed", "osfno-A-nospeed"), ("osfno-B-head", "osfno-B-head"),
              ("osfno-E-phys", "osfno-E-phys")]
    fig, axs = plt.subplots(1, 5, figsize=(12, 2.9))
    rows = []
    for ax, t in zip(axs, TASKS):
        for short, key in others:
            s = score(t, short)
            if s:
                x, y = np.mean([v["clean"] for v in s.values()]), np.mean([v["robust"] for v in s.values()])
                lab, col, mk = M[key]
                ax.plot(x, y, marker=mk, color=col, ms=5, ls="none", label=lab)
                rows.append([t, lab, f"{x:.4f}", f"{y:.4f}"])
        for p, r, kp, kr in pairs:
            sp, sr = score(t, p), score(t, r)
            xp, yp = np.mean([v["clean"] for v in sp.values()]), np.mean([v["robust"] for v in sp.values()])
            xr, yr = np.mean([v["clean"] for v in sr.values()]), np.mean([v["robust"] for v in sr.values()])
            col = M[kp][1]
            ax.annotate("", (xr, yr), (xp, yp), arrowprops=dict(arrowstyle="->", color=col, lw=1.5))
            ax.plot(xp, yp, marker=M[kp][2], color=col, ms=6, ls="none", label=M[kp][0])
            ax.plot(xr, yr, marker=M[kr][2], color=col, ms=6, ls="none", mfc="white", mew=1.5, label=M[kr][0])
            ax.text(xr, yr, "  " + M[kr][0].split(" (")[0], fontsize=6, color=INK2, va="center")
            rows += [[t, M[kp][0], f"{xp:.4f}", f"{yp:.4f}"], [t, M[kr][0], f"{xr:.4f}", f"{yr:.4f}"]]
        ax.plot([0, 1], [0, 1], color=GRID, lw=1)
        ax.set_title(TN[t], fontsize=8.5)
        ax.set_xlabel("clean macro-F1")
        lo = min(float(r[3]) for r in rows if r[0] == t) - 0.05
        ax.set_ylim(lo, 1.0)
        ax.set_xlim(min(float(r[2]) for r in rows if r[0] == t) - 0.03, 1.0)
    axs[0].set_ylabel("robustness score")
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=5, fontsize=7, bbox_to_anchor=(0.5, -0.16))
    fig.suptitle("Clean accuracy vs robustness (mean over ±1/2/5 % speed error and dead sensor); arrows: parent → robust training",
                 fontsize=9, y=1.04)
    save(fig, "F06_clean_vs_robustness", ["task", "model", "clean_macro_f1", "robustness_score"], rows)


def f07_forest():
    c1 = json.load(open(RESULTS / "phase1_comparisons.json"))["comparisons"]
    c3 = json.load(open(RESULTS / "phase3_comparisons.json"))
    c56 = json.load(open(RESULTS / "phase56_comparisons.json"))
    groups = [("B − C (FiLM hurts)", lambda t: c1.get(f"R1: B (speed in head) vs C (FiLM)|{t}")),
              ("E − A (physical speed)", lambda t: c1.get(f"R2: E (physical speed) vs A|{t}")),
              ("CNN − best feature baseline", lambda t: c1.get(f"R3: cnn-spec vs best feature baseline|{t}")),
              ("OS-FNO A − best feature baseline", lambda t: c1.get(f"R3: osfno-A-nospeed vs best feature baseline|{t}")),
              ("CNN tuned − FNO tuned (nested)", lambda t: c3.get(f"{t}|cnn-tuned|fno-tuned")),
              ("Stack (nested gate) − CNN", lambda t: c56.get(f"{t}|stack-rf-mlp-cnn|cnn-spec")),
              ("CNN + band env. − CNN", lambda t: c56.get(f"{t}|cnn-mb|cnn-spec"))]
    fig, axs = plt.subplots(1, len(groups), figsize=(14, 2.9), sharey=True)
    rows = []
    cols = [BLUE, ORANGE, AQUA, VIOLET, MAGENTA]
    for ax, (g, fn) in zip(axs, groups):
        for i, t in enumerate(TASKS):
            r = fn(t)
            if not r:
                continue
            d, h = r["diff_seed"]
            ax.errorbar(d, i, xerr=h, fmt="o", color=cols[i], ms=4.5, elinewidth=1.4)
            rows.append([g, t, f"{d:.4f}", f"{h:.4f}", f"{r.get('mcnemar_p_holm', np.nan):.3g}"])
        ax.axvline(0, color=INK2, lw=0.8)
        import textwrap
        ax.set_title(textwrap.fill(g, 20), fontsize=7.5)
        ax.set_xlabel("Δ macro-F1")
        ax.grid(axis="y", visible=False)
    axs[0].set_yticks(range(5), [TN[t] for t in TASKS])
    axs[0].invert_yaxis()
    fig.suptitle("Paired differences (same partitions and seeds): seed mean ± 95 % t-interval", fontsize=9, y=1.05)
    save(fig, "F07_paired_differences", ["comparison", "task", "diff", "ci95_halfwidth", "mcnemar_p_holm"], rows)


def f08_compound():
    methods = ["br-rf", "br-mlp", "ml-cnn", "ml-cnn-mix"]
    labs = {"br-rf": "Binary relevance RF", "br-mlp": "Binary relevance MLP", "ml-cnn": "Multi-label CNN",
            "ml-cnn-mix": "Multi-label CNN + synthetic mixtures"}
    cols = [BLUE, ORANGE, AQUA, VIOLET]
    combos = ["unbalance+horizontal", "unbalance+vertical", "horizontal+vertical"]
    faults = ["unbalance", "horizontal", "vertical"]
    fig, axs = plt.subplots(1, 3, figsize=(12, 2.8))
    rows = []
    w = 0.2
    for j, m in enumerate(methods):
        R = [json.load(open(f)) for f in sorted(glob.glob(str(RESULTS / "phase7" / m / "seed*.json")))]
        ex = [np.mean([r["by_combination"][c]["exact"] for r in R]) for c in combos]
        pf = [np.mean([r["per_label_f1"][f] for r in R]) for f in faults]
        axs[0].bar(np.arange(3) + (j - 1.5) * w, ex, w * 0.9, color=cols[j], label=labs[m])
        axs[1].bar(np.arange(3) + (j - 1.5) * w, pf, w * 0.9, color=cols[j])
        rows += [[m, f"exact {c}", f"{v:.4f}"] for c, v in zip(combos, ex)] + [[m, f"F1 {f}", f"{v:.4f}"] for f, v in zip(faults, pf)]
    axs[0].set_xticks(range(3), ["U+H", "U+V", "H+V"]); axs[0].set_ylabel("exact match"); axs[0].set_title("Compound runs recognised exactly")
    axs[1].set_xticks(range(3), faults); axs[1].set_ylabel("F1"); axs[1].set_title("Per-fault F1 on compound runs")
    axs[0].legend(fontsize=6.3, loc="upper left")
    S = json.load(open(RESULTS / "phase7" / "superposition.json"))
    err = [S["median_relative_error"][c]["full"] for c in combos]
    axs[2].bar(range(3), err, 0.55, color=MAGENTA, label="superposition error")
    nf = S["noise_floor_median_same_class"]
    for i, c in enumerate(combos):
        a, b = c.split("+")
        axs[2].plot([i - 0.3, i + 0.3], [nf[a]] * 2, color=INK, lw=1.5, label="noise floor, 1st fault class" if i == 0 else None)
        axs[2].plot([i - 0.3, i + 0.3], [nf[b]] * 2, color=INK2, lw=1.5, ls="--", label="noise floor, 2nd fault class" if i == 0 else None)
    axs[2].legend(fontsize=6.3, loc="upper left")
    axs[2].set_xticks(range(3), ["U+H", "U+V", "H+V"]); axs[2].set_ylabel("median relative error (0-8X)")
    axs[2].set_title("Superposition error vs same-class noise floor")
    rows += [["superposition", c, f"{e:.4f}"] for c, e in zip(combos, err)] + [["noise_floor", k, f"{v:.4f}"] for k, v in nf.items()]
    for ax in axs:
        ax.grid(axis="x", visible=False)
    save(fig, "F08_compound_faults", ["method_or_item", "metric", "value"], rows)


def f09_reliability():
    models = ["rf", "mlp", "cnn-spec", "osfno-A-nospeed"]
    cols = {"rf": BLUE, "mlp": YELLOW, "cnn-spec": ORANGE, "osfno-A-nospeed": AQUA}
    fig, axs = plt.subplots(1, 2, figsize=(7.5, 3.2))
    rows = []
    edges = np.linspace(0, 1, 11)
    for ax, t in zip(axs, ["all", "comfaulda7"]):
        for m in models:
            R = load("phase1", m, t)
            conf, acc = [], []
            for d in R:
                P = np.array([r["proba"] for r in d["runs"]]); y = np.array([r["y"] for r in d["runs"]])
                conf.append(P.max(1)); acc.append(P.argmax(1) == y)
            conf, acc = np.concatenate(conf), np.concatenate(acc)
            xs, ys = [], []
            for lo, hi in zip(edges[:-1], edges[1:]):
                k = (conf > lo) & (conf <= hi)
                if k.sum() >= 20:
                    xs.append(conf[k].mean()); ys.append(acc[k].mean())
            ax.plot(xs, ys, marker=M[m][2], ms=4, color=cols[m], label=M[m][0])
            rows += [[t, m, f"{a:.4f}", f"{b:.4f}"] for a, b in zip(xs, ys)]
        ax.plot([0, 1], [0, 1], color=INK2, lw=0.8, ls=":")
        ax.set_title(TN[t], fontsize=8.5); ax.set_xlabel("confidence"); ax.set_ylabel("accuracy")
    axs[1].legend(fontsize=6.5, loc="upper left")
    fig.suptitle("Reliability (10 bins, ≥ 20 runs per point, 5 seeds pooled)", fontsize=9, y=1.03)
    save(fig, "F09_reliability", ["task", "model", "confidence", "accuracy"], rows)


def f10_confusion():
    d = json.load(open(RESULTS / "phase8_calibration.json"))
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.3))
    rows = []
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("blue", ["#ffffff", "#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
    for ax, m in zip(axs, ["rf", "cnn-spec", "osfno-A-nospeed"]):
        c = np.array(d[f"all/{m}"]["confusion_seed_sum"], float)
        cn = c / c.sum(1, keepdims=True)
        ax.imshow(cn, cmap=cmap, vmin=0, vmax=1)
        cls = list(d[f"all/{m}"]["per_class_f1"])
        short = [s.replace("underhang/", "UH ").replace("overhang/", "OH ").replace("-misalignment", " mis.").replace("_fault", "")
                 for s in cls]
        for i in range(len(cls)):
            for j in range(len(cls)):
                if cn[i, j] >= 0.02:
                    ax.text(j, i, f"{cn[i, j]:.2f}", ha="center", va="center", fontsize=5.5,
                            color="white" if cn[i, j] > 0.55 else INK)
                rows.append([m, cls[i], cls[j], int(c[i, j])])
        ax.set_xticks(range(len(cls)), short, rotation=60, ha="right", fontsize=6)
        ax.set_yticks(range(len(cls)), short, fontsize=6)
        ax.set_title(f"T4, {M[m][0]}", fontsize=8.5); ax.set_xlabel("predicted"); ax.grid(False)
    axs[0].set_ylabel("true")
    fig.suptitle("Row-normalised confusion, held-out terciles, 5 seeds summed", fontsize=9)
    save(fig, "F10_confusion_T4", ["model", "true", "predicted", "count_5_seeds"], rows)


if __name__ == "__main__":
    for fn in (f01_main, f02_bands, f03_speed_curves, f04_robust_speed, f05_sensor, f06_tradeoff, f07_forest,
               f08_compound, f09_reliability, f10_confusion):
        fn()
        print("ok", fn.__name__, flush=True)
