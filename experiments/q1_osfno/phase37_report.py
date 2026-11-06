"""Phase 3 (nested-tuned CNN vs FNO) and Phase 7 (compound faults) reports, generated from the result files.
Writes PHASE3_REPORT.md, PHASE7_REPORT.md, results/phase3_comparisons.json."""
import glob
import json

import numpy as np

from q1lib import RESULTS
from stats_q1 import ci, compare, holm, load

T = ["misalignment", "unbalance", "bearings", "all", "comfaulda7"]
L = ["# Phase 3: CNN vs FNO, hyper-parameters chosen by nested inner validation only", "",
     "Grids and locks: `phase3.py`, `locks/phase3_<task>_<family>.json` (written before any outer evaluation). "
     "Macro-F1 pooled over the three held-out terciles, 5 seeds, Phase 1 partitions.", "",
     "| task | family | macro-F1 (mean ± 95 % CI) | chosen config per fold (low, mid, high) |", "|---|---|---|---|"]
for t in T:
    for fam in ("cnn", "fno"):
        lk = json.load(open(RESULTS.parent / "locks" / f"phase3_{t}_{fam}.json"))
        f = np.array([r["pooled"]["macro_f1"] for r in load("phase3", f"{fam}-tuned", t)])
        L.append(f"| {t} | {fam} | {f.mean():.3f} ± {ci(f)[1]:.3f} | " + "; ".join(str(v["chosen"]) for v in lk["folds"].values()) + " |")
pairs = [("phase3", "cnn-tuned", "phase3", "fno-tuned"), ("phase3", "cnn-tuned", "phase1", "cnn-spec"),
         ("phase3", "fno-tuned", "phase1", "osfno-A-nospeed")]
rows = [(t, p, compare(*p[:2], *p[2:], t, n_boot=2000)) for p in pairs for t in T]
padj = holm([r[2]["mcnemar"]["p"] for r in rows])
L += ["", "| task | A | B | diff (seed mean ± 95 % CI) | seeds A>B | low | mid | high | McNemar p (Holm over all 15) |",
      "|---|---|---|---|---|---|---|---|---|"]
out = {}
for (t, p, r), pa in zip(rows, padj):
    d, h = r["diff_seed"]
    L.append(f"| {t} | {p[1]} | {p[3]} ({p[2]}) | {d:+.3f} ± {h:.3f} | {r['n_seeds_positive']}/{len(r['seeds'])} | " +
             " | ".join(f"{r['bands'][b]['diff'][0]:+.3f}" for b in ("low", "mid", "high")) + f" | {r['mcnemar']['p']:.2g} ({pa:.2g}) |")
    out[f"{t}|{p[1]}|{p[3]}"] = {**r, "mcnemar_p_holm": pa}
open(RESULTS.parent / "PHASE3_REPORT.md", "w").write("\n".join(L) + "\n")
json.dump(out, open(RESULTS / "phase3_comparisons.json", "w"), indent=1, default=float)
print("\n".join(L))

M = ["# Phase 7: COMFAULDA compound faults recognised from single-fault training", "",
     "Train = normal + single-fault runs (all speeds); test = the 1143 combined runs. 5 seeds. `phase7.py`.", "",
     "| method | exact match (mean ± sd) | Hamming | F1 unbalance | F1 horizontal | F1 vertical | exact U+H | exact U+V | exact H+V |",
     "|---|---|---|---|---|---|---|---|---|"]
for m in ["br-rf", "br-mlp", "ml-cnn", "ml-cnn-mix"]:
    R = [json.load(open(f)) for f in sorted(glob.glob(str(RESULTS / "phase7" / m / "seed*.json")))]
    ex = np.array([r["exact_match"] for r in R])
    g = lambda k: np.mean([r["per_label_f1"][k] for r in R])
    b = lambda s: np.mean([r["by_combination"][s]["exact"] for r in R])
    M.append(f"| {m} ({len(R)}) | {ex.mean():.3f} ± {ex.std(ddof=1):.3f} | {np.mean([r['hamming_loss'] for r in R]):.3f} | "
             f"{g('unbalance'):.2f} | {g('horizontal'):.2f} | {g('vertical'):.2f} | {b('unbalance+horizontal'):.2f} | "
             f"{b('unbalance+vertical'):.2f} | {b('horizontal+vertical'):.2f} |")
S = json.load(open(RESULTS / "phase7" / "superposition.json"))
M += ["", "Superposition test (median relative error over 0-8X, `superposition.json`): "
      + ", ".join(f"{k} {v['full']:.2f}" for k, v in S["median_relative_error"].items())
      + "; same-class noise floor: " + ", ".join(f"{k} {v:.2f}" for k, v in S["noise_floor_median_same_class"].items()) + "."]
open(RESULTS.parent / "PHASE7_REPORT.md", "w").write("\n".join(M) + "\n")
print("\n".join(M))
