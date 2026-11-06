"""Phase 8 robustness report from results/phase8_robust (mean over the seeds present; n shown).
Columns: clean macro-F1, speed error -5/-2/-1/+1/+2/+5 %, dead sensor (mean and worst over sensors), gain x2 (mean, worst).
Writes PHASE8_ROBUSTNESS.md and results/phase8_robust_summary.json."""
import glob
import json

import numpy as np

from q1lib import RESULTS

TASKS = ["misalignment", "unbalance", "bearings", "all", "comfaulda7"]
MODELS = ["rf", "mlp", "xgb", "cnn-spec", "osfno-A-nospeed", "osfno-B-head", "osfno-E-phys"]
lines = ["# Phase 8: robustness to test-time measurement errors", "",
         "Models trained exactly as in Phase 1; perturbations applied to the held-out runs only (phase8_robust.py). "
         "Macro-F1 pooled over the three held-out terciles, mean over seeds (n). Dead / gain: mean and worst over sensors.", ""]
out = {}
for t in TASKS:
    lines += [f"## {t}", "", "| model | n | clean | -5 % | -2 % | -1 % | +1 % | +2 % | +5 % | dead mean | dead worst | gain x2 mean | gain x2 worst |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        R = [json.load(open(f)) for f in sorted(glob.glob(str(RESULTS / "phase8_robust" / t / m / "seed*.json")))]
        if not R:
            continue
        c = {k: float(np.mean([r["conditions"][k]["macro_f1"] for r in R])) for k in R[0]["conditions"]}
        dead = [v for k, v in c.items() if k.startswith("dead")]
        gain = [v for k, v in c.items() if k.startswith("gain2")]
        sp = [c[f"speed:{e}"] for e in (-0.05, -0.02, -0.01, 0.01, 0.02, 0.05)]
        out[f"{t}/{m}"] = {"n_seeds": len(R), **c}
        lines.append(f"| {m} | {len(R)} | {c['clean:None']:.3f} | " + " | ".join(f"{v:.3f}" for v in sp) +
                     f" | {np.mean(dead):.3f} | {min(dead):.3f} | {np.mean(gain):.3f} | {min(gain):.3f} |")
    lines.append("")
open(RESULTS.parent / "PHASE8_ROBUSTNESS.md", "w").write("\n".join(lines) + "\n")
json.dump(out, open(RESULTS / "phase8_robust_summary.json", "w"), indent=1)
print("\n".join(lines))
