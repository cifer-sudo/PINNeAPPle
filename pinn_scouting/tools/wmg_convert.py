"""Convert a WMG CoreTemperature_AgeingStudy MATLAB `table` (.mat v5 with MCOS objects) into one NPZ per cell.

python wmg_convert.py <table.mat> <out_prefix>

Each table row is a cell; each numeric column holds one array per test block. Blocks are concatenated and a
`block` index is kept. Time columns are in ms (1 s sampling in the ageing files). Core temperature is absent for
the three non-instrumented cells. Sentinel -3276.8 (sensor dropout) is kept as-is here and masked by the loaders.
"""
import sys
import warnings

import numpy as np

warnings.filterwarnings("ignore")
import matio  # noqa: E402  (package "mat-io")

COLS = {"Prog Time": "t_ms", "Step Time": "tstep_ms", "Cycle No": "cycle", "Step": "step", "Voltage [V]": "V",
        "Current [A]": "I", "Capacity [Ah]": "Q", "Surf Temp [C]": "Ts", "Core Temp [C]": "Tc"}


def main():
    src, prefix = sys.argv[1], sys.argv[2]
    d = matio.load_from_mat(src)
    name = [k for k in d if not k.startswith("__")][0]
    df = d[name]
    df.columns = [c.strip() for c in df.columns]
    for _, row in df.iterrows():
        blocks = {}
        for c, k in COLS.items():
            x = row.get(c)
            if isinstance(x, np.ndarray):
                blocks[k] = [np.asarray(b, dtype=float).ravel() for b in x.ravel() if isinstance(b, np.ndarray)]
        lens = [len(b) for b in blocks["V"]]
        sav = {k: np.concatenate(bl) for k, bl in blocks.items() if [len(b) for b in bl] == lens}
        sav["block"] = np.concatenate([np.full(n, i) for i, n in enumerate(lens)])
        st = row.get("Status")
        if isinstance(st, np.ndarray):
            s = [np.array([str(np.asarray(v).ravel()[0]) for v in b.ravel()]) for b in st.ravel()]
            if [len(v) for v in s] == lens:
                sav["status"] = np.concatenate(s)
        out = f"{prefix}_{row['Cell Name']}.npz"
        np.savez_compressed(out, **sav)
        print(out, row["Condition"], "blocks", lens, "keys", sorted(sav))


if __name__ == "__main__":
    main()
