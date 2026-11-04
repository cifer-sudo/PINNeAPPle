"""Run a queue of (dataset, task, model, seeds) jobs sequentially, skipping finished result files.

usage: python jobqueue.py <queue_name>
"""
import sys
import time

import models as M
import models2 as M2
import q1lib as L

M.REGISTRY.update(M2.EXTRA)
MAF = ["misalignment", "unbalance", "bearings", "all"]
SEEDS = [0, 1, 2, 3, 4]
QUEUES = {
    # fast feature baselines first (per-run predictions on the locked partitions)
    "features_maf": [("mafaulda", t, m, SEEDS) for m in ("rf", "mlp", "kan", "svm", "xgb") for t in MAF],
    "osfno_core_maf": [("mafaulda", t, m, SEEDS) for m in ("osfno-B-head", "osfno-C-film", "osfno-A-nospeed") for t in MAF],
    "features": [("mafaulda", t, m, SEEDS) for m in ("rf", "mlp", "kan", "svm", "xgb") for t in MAF]
                + [("comfaulda", "comfaulda7", m, SEEDS) for m in ("rf", "mlp", "kan", "svm", "xgb")],
    # Phase 1/3 core: speed handling in the spectral operator
    "osfno_core": [(d, t, m, SEEDS) for m in ("osfno-B-head", "osfno-C-film", "osfno-A-nospeed")
                   for d, t in [("mafaulda", x) for x in MAF] + [("comfaulda", "comfaulda7")]],
    "osfno_more": [(d, t, m, SEEDS) for m in ("osfno-E-phys", "osfno-B-noaug", "osfno-B-noprior", "osfno-B-commonaug")
                   for d, t in [("mafaulda", "all"), ("comfaulda", "comfaulda7")]],
    "deep_baselines": [(d, t, m, SEEDS) for m in ("cnn-spec", "fno-trainonly", "cnn-angle")
                       for d, t in [("mafaulda", x) for x in MAF] + [("comfaulda", "comfaulda7")]],
    "dg": [(d, t, m, SEEDS) for m in ("osfno-B-dro", "osfno-B-supcon", "fusion-rf-osfno")
           for d, t in [("mafaulda", x) for x in MAF] + [("comfaulda", "comfaulda7")]],
}

if __name__ == "__main__":
    q = QUEUES[sys.argv[1]]
    cache = {}
    for ds, task, model, seeds in q:
        if ds not in cache:
            cache = {ds: L.load_rows(ds)}
        for s in seeds:
            t0 = time.time()
            L.run(task, model, M.REGISTRY[model], cache[ds], s, exp="phase1", dataset=ds, config={"model": model})
            sys.stdout.flush()
