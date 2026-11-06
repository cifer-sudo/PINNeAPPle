"""Phase 5 (stacker with gate selected on inner validation) and Phase 6 (multi-band envelopes) reports from result files.
Writes PHASE5_REPORT.md, PHASE6_REPORT.md, results/phase56_comparisons.json."""
import json
from collections import Counter

import numpy as np

from q1lib import RESULTS
from stats_q1 import ci, compare, holm, load

T = ["misalignment", "unbalance", "bearings", "all", "comfaulda7"]
out = {}


def table(title, intro, pairs, fname):
    L = [title, "", intro, "", "| task | A | B | A macro-F1 | diff (seed mean ± 95 % CI) | seeds A>B | low | mid | high | McNemar p (Holm) |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    rows = [(t, ea, a, eb, b, compare(ea, a, eb, b, t, n_boot=2000)) for t, ea, a, eb, b in pairs]
    padj = holm([r[5]["mcnemar"]["p"] for r in rows])
    for (t, ea, a, eb, b, r), pa in zip(rows, padj):
        f = np.array([x["pooled"]["macro_f1"] for x in load(ea, a, t)])
        d, h = r["diff_seed"]
        L.append(f"| {t} | {a} | {b} | {f.mean():.3f} ± {ci(f)[1]:.3f} | {d:+.3f} ± {h:.3f} | {r['n_seeds_positive']}/{len(r['seeds'])} | "
                 + " | ".join(f"{r['bands'][x]['diff'][0]:+.3f}" for x in ("low", "mid", "high")) + f" | {r['mcnemar']['p']:.2g} ({pa:.2g}) |")
        out[f"{t}|{a}|{b}"] = {**r, "mcnemar_p_holm": pa}
    return L


L = table("# Phase 4/5: multi-expert fusion, gate selected on inner validation only",
          "`phase5.py`: experts rf, mlp, cnn-spec; gate (convex 0.25 grid, logistic stacker, speed-aware stacker) chosen per "
          "outer fold by inner leave-one-speed-block-out OOF macro-F1. `fuse-rf+cnn-spec` = the exploratory fixed α = 0.5 fusion.",
          [(t, "phase5", "stack-rf-mlp-cnn", "phase1", b) for b in ("cnn-spec", "rf", "fuse-rf+cnn-spec") for t in T], None)
L += ["", "Chosen gates (15 folds x seeds per task):", ""]
for t in T:
    g = Counter(v["chosen_gate"] for r in load("phase5", "stack-rf-mlp-cnn", t) for v in r["split_info"].values())
    L.append(f"- {t}: " + ", ".join(f"{k} x{n}" for k, n in g.most_common()))
open(RESULTS.parent / "PHASE5_REPORT.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
M = table("# Phase 6: band-limited envelope spectra for bearings (pre-registered H6)",
          "`phase6.py`; decision rule in PROTOCOL.md (difference > 0 with CI above 0 on both T3 and T4). Fisher-ratio diagnosis: "
          "`results/phase6_diagnose.json`.",
          [(t, "phase6", a, "phase1", b) for a, b in (("rf-mb", "rf"), ("cnn-mb", "cnn-spec")) for t in ("bearings", "all")], None)
for a in ("rf-mb", "cnn-mb"):
    ok = all(out[f"{t}|{a}|{ 'rf' if a == 'rf-mb' else 'cnn-spec'}"]["diff_seed"][0] - out[f"{t}|{a}|{ 'rf' if a == 'rf-mb' else 'cnn-spec'}"]["diff_seed"][1] > 0
             for t in ("bearings", "all"))
    M.append(f"\nH6 for {a}: **{'SUPPORTED' if ok else 'NOT SUPPORTED'}** (pre-registered rule).")
open(RESULTS.parent / "PHASE6_REPORT.md", "w").write("\n".join(M) + "\n")
json.dump(out, open(RESULTS / "phase56_comparisons.json", "w"), indent=1, default=float)
print("\n".join(M))
