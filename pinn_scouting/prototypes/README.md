# Phase 6 prototypes (feasibility only)

Two minimal prototypes for the two top-scored candidates, run on the real downloaded files. They answer "does the
pipeline work, and is there any sign that physics helps?". They are not the paper experiments.

| folder | candidate | data (local path, env var) | run | tests |
|---|---|---|---|---|
| `coretemp_wmg/` | C1 core temperature | WMG Mendeley bf6fksxpp2, converted to NPZ by `../tools/wmg_convert.py` (`WMG_NPZ`) | `python run.py && python report.py` (~90 s on 4 CPU cores) | `pytest -q tests` (8 tests) |
| `rw_health_nasa/` | C5 capacity from random loads | NASA RW groups unzipped from the S3 mirror (`NASA_RW`) | `python run.py && python report.py` (~20 min) | `pytest -q tests` (4 tests) |

Environment: `/home/user/venv-scout` (numpy, scipy, JAX CPU, optax, scikit-learn, matplotlib, mat-io, py7zr).

## Getting the data again

```bash
# WMG (2.33 GB 7z; extract only the members you need, the full archive is 28 GB)
curl -L -o CoreTemperature_AgeingStudy.7z "https://data.mendeley.com/public-files/datasets/bf6fksxpp2/files/7e956baf-2380-4ffa-a06f-dd22466f0f29/file_downloaded"
```

```bash
python ../tools/wmg_convert.py CoreTemperature_AgeingStudy/ShortTermAgeing_100cycles/100cycles_dataTable.mat $WMG_NPZ/short
```

```bash
# NASA RW: one group (59-446 MB) without downloading the 1.07 GB outer zip
python ../tools/remote_zip.py get "https://phm-datasets.s3.amazonaws.com/NASA/11.+Randomized+Battery+Usage+Data+Set.zip" "11. Randomized Battery Usage Data Set/4. RW_Skewed_High_40C_DataSet_2Post.zip" rw_high40.zip
```

Results: `*/results/RESULTS.md` and the PNG figures next to them. Post-hoc runs are in folders whose names say
`posthoc` and are labelled as such in every table.
