"""Phase 5b confirmation (pre-registered): standard Phase 1-format results of cnn-spec-rob and rf-rob (exp phase5),
then their Phase 8 robustness (phase8_robust.py). usage: python phase5b.py <dataset> <task> <model> [seeds, e.g. 0,1]"""
import sys

import q1lib as L
from models import REGISTRY, _register_extra

if __name__ == "__main__":
    ds, task, model = sys.argv[1:4]
    seeds = [int(s) for s in sys.argv[4].split(",")] if len(sys.argv) > 4 else list(range(5))
    _register_extra()
    rows = L.load_rows(ds)
    for s in seeds:
        L.run(task, model, REGISTRY[model], rows, s, exp="phase5", dataset=ds,
              config={"model": model, "preregistered": "PROTOCOL.md Phase 5b"})
    import phase8_robust
    phase8_robust.main(ds, task, model, seeds)
