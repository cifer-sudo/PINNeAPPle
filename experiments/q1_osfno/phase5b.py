"""Phase 5b confirmation (pre-registered): standard Phase 1-format results of cnn-spec-rob and rf-rob (exp phase5),
then their Phase 8 robustness (phase8_robust.py). usage: python phase5b.py <dataset> <task> <model>"""
import sys

import q1lib as L
from models import REGISTRY, _register_extra

if __name__ == "__main__":
    ds, task, model = sys.argv[1:4]
    _register_extra()
    rows = L.load_rows(ds)
    for s in range(5):
        L.run(task, model, REGISTRY[model], rows, s, exp="phase5", dataset=ds,
              config={"model": model, "preregistered": "PROTOCOL.md Phase 5b"})
    import phase8_robust
    phase8_robust.main(ds, task, model, list(range(5)))
