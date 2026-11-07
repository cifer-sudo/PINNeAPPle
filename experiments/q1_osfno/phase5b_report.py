"""Phase 5b decision per the pre-registration (PROTOCOL.md): (a) clean macro-F1 difference (phase5 vs phase1 parent,
paired by seed); (b) robustness score = mean macro-F1 over the 6 speed-error conditions and the dead-sensor conditions
(mean over sensors), per seed, from results/phase8_robust. Writes PHASE5B_REPORT.md and results/phase5b_decision.json."""
import glob
import json

import numpy as np

from q1lib import RESULTS
from stats_q1 import ci, compare

T = ["misalignment", "unbalance", "bearings", "all", "comfaulda7"]


def score(task, model):
    out = {}
    for f in sorted(glob.glob(str(RESULTS / "phase8_robust" / task / model / "seed*.json"))):
        d = json.load(open(f))
        c = {k: v["macro_f1"] for k, v in d["conditions"].items()}
        sp = [v for k, v in c.items() if k.startswith("speed")]
        dead = np.mean([v for k, v in c.items() if k.startswith("dead")])
        out[d["seed"]] = {"robust": float(np.mean(sp + [dead])), "speed": float(np.mean(sp)), "dead": float(dead),
                          "gain2": float(np.mean([v for k, v in c.items() if k.startswith("gain2")])),
                          "speed5": float(np.mean([c["speed:-0.05"], c["speed:0.05"]])), "clean": c["clean:None"]}
    return out



def main():
    L = ["# Phase 5b: measurement-robust training (pre-registered decision)", "",
         "(a) clean macro-F1 difference vs the Phase 1 parent; (b) robustness score = mean macro-F1 over the six speed-error "
         "conditions (±1/2/5 %) and the dead-sensor mean; paired by seed, mean ± 95 % t-interval. ±5 % and gain ×2 are "
         "outside the training perturbations (reported only).", "",
         "| task | model | parent | (a) clean diff | (b) robustness diff | speed-only diff | dead-sensor diff | ±5 % diff | gain ×2 diff | robust score model / parent |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    dec = {}
    for m, p in (("cnn-spec-rob", "cnn-spec"), ("rf-rob", "rf")):
        ok_b, bad_a = 0, 0
        for t in T:
            a = compare("phase5", m, "phase1", p, t, n_boot=500)["diff_seed"]
            A, B = score(t, m), score(t, p)
            s = sorted(set(A) & set(B))
            diffs = {k: np.array([A[i][k] - B[i][k] for i in s]) for k in ("robust", "speed", "dead", "speed5", "gain2")}
            cis = {k: (float(v.mean()), ci(v)[1]) for k, v in diffs.items()}
            ok_b += cis["robust"][0] - cis["robust"][1] > 0
            bad_a += a[0] + a[1] < 0
            dec[f"{t}/{m}"] = {"clean_diff": a, **cis}
            L.append(f"| {t} | {m} | {p} | {a[0]:+.3f} ± {a[1]:.3f} | " + " | ".join(f"{cis[k][0]:+.3f} ± {cis[k][1]:.3f}" for k in
                     ("robust", "speed", "dead", "speed5", "gain2")) +
                     f" | {np.mean([A[i]['robust'] for i in s]):.3f} / {np.mean([B[i]['robust'] for i in s]):.3f} |")
        verdict = "RETAINED" if ok_b >= 3 and bad_a == 0 else "NOT RETAINED"
        dec[m] = {"tasks_robust_ci_above_0": int(ok_b), "tasks_clean_ci_below_0": int(bad_a), "decision": verdict}
        L.append(f"| **{m}** | decision | | clean CI entirely < 0 on {bad_a} task(s) | robustness CI > 0 on {ok_b}/5 | | | | | **{verdict}** |")
    open(RESULTS.parent / "PHASE5B_REPORT.md", "w").write("\n".join(L) + "\n")
    json.dump(dec, open(RESULTS / "phase5b_decision.json", "w"), indent=1, default=float)
    print("\n".join(L))


if __name__ == "__main__":
    main()
