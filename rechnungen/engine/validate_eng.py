"""Validierung der Prüf-Engine eng.py gegen data/sweep_19x19.csv und finesweep.run (Standardstart, 15 s,
Fenster 5–15 s). Zusätzlich: Laufzeit je Schritt."""
import os
import time
import numpy as np
import pandas as pd
import eng
import finesweep as fs

pts = [(0.0, 0.0), (113.684, 227.368), (151.579, 265.263), (0.0, 208.421), (246.316, 246.316), (0.0, 113.684)]
p2 = np.array([p[0] for p in pts]); p3 = np.array([p[1] for p in pts])
ref = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data/sweep_19x19.csv'))
t = time.time()
z0, v0 = eng.start_std(len(pts))
r = eng.integrate(p2, p3, z0, v0, n_cyc=150)
el = time.time() - t
w = eng.window(r, 50, 150)
print(f'eng.integrate: {len(pts)} Läufe x 300000 Schritte in {el:.1f} s ({el / 3e5 * 1e6:.1f} µs/Schritt)')
t = time.time()
fo, _ = fs.run(p2, p3)
print(f'finesweep.run: {time.time() - t:.1f} s')
for j, (a, b) in enumerate(pts):
    rr = ref[(ref.phi2_deg == a) & (ref.phi3_deg == b)].iloc[0]
    print(f'({a:7.3f},{b:7.3f}) F_mean eng {eng.MG + w["dF_left_ppm"][j] * eng.MG / 1e6:.6f} fs {fo["F_mean"][j]:.6f} csv {rr.F_mean:.6f} | '
          f'skew {w["skew"][j]:.6f} {fo["F_skew"][j]:.6f} {rr.F_skew:.6f} | lam {w["lam"][j]:.4f} {fo["liftoff"][j]:.4f} {rr.liftoff:.4f} | '
          f'Fmax {w["Fmax"][j]:.6f} {fo["F_max"][j]:.6f} {rr.F_max:.6f} | Fmin {w["Fmin"][j]:.6f} {fo["F_min"][j]:.6f} {rr.F_min:.6f}')
