"""s0_validierung.py - Abgleich sr_engine gegen finesweep.run (Repo, nur importiert) und
sweep_19x19.csv, Standardlauf 15 s, Fenster 5-15 s (Zyklen 50..149)."""
import os
import time
import numpy as np
import pandas as pd
import finesweep as fs
import sr_engine as se

pts = [(0.0, 0.0), (113.684, 227.368), (151.579, 265.263), (246.316, 113.684)]
p2 = [p[0] for p in pts]; p3 = [p[1] for p in pts]
t = time.time()
o = se.run(p2, p3, 150)
w = se.window(o, 50, 150)
t_se = time.time() - t
t = time.time()
ref, _ = fs.run(p2, p3)
t_fs = time.time() - t
csv = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data/sweep_19x19.csv'))
print(f'Laufzeit sr_engine {t_se:.1f} s, finesweep {t_fs:.1f} s (4 Punkte, 15 s)')
for j, (a, b) in enumerate(pts):
    r = csv[(np.isclose(csv.phi2_deg, a)) & (np.isclose(csv.phi3_deg, b))]
    print(f'--- ({a}, {b})')
    for key_se, key_fs in (('mean_N1', 'F_mean'), ('skew', 'F_skew'), ('liftoff', 'liftoff'),
                           ('F_min', 'F_min'), ('F_max', 'F_max')):
        v1 = w[key_se][j]; v2 = ref[key_fs][j]
        vc = r[key_fs].iloc[0] if len(r) else np.nan
        print(f'  {key_fs:8s} sr_engine {v1:.12g}  finesweep {v2:.12g}  diff {v1 - v2:+.3e}  CSV {vc}')
    print(f'  mean_RK4 {w["mean_RK4"][j]:.12g}  mean_TR {w["mean_TR"][j]:.12g}  R {w["R"][j]:+.4e} N')
