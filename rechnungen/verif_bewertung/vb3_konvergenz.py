"""vb3_konvergenz.py – Zeitschrittkontrolle ausgewählter Hüpftreffer aus vb1/vb2 (T/2000, T/4000, T/8000)."""
import os
import sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../auslegung'))
import mu_modell as mm
mu, hub, f, K = 0.4615, 8e-3, 10.0, 1.5e6
cases = [  # (phis, weights, zeta, v0)
    ((180, 300, 60), (1, 1, 1), 0.02, 0.8),     # (120,240) shift 180
    ((270, 20, 162), (1, 1, 1), 0.02, 0.8),     # (110,252) shift 270
    ((180, 310, 50), (1, 1, 1), 0.02, 0.5),     # (130,230) shift 180
    ((0, 0, 180), (1, 1, 1), 0.05, 0.5),        # (0,180)
    ((0, 0, 0), (1, 0, 0), 0.05, 0.5),          # Einzelmodul
    ((60, 0, 0), (1, 0, 0), 0.02, 0.8),         # Einzelmodul
]
for n_per in (2000, 4000, 8000):
    PH = np.array([c[0] for c in cases], float); W = np.array([c[1] for c in cases], float)
    out = []
    for zeta in sorted(set(c[2] for c in cases)):
        idx = [i for i, c in enumerate(cases) if c[2] == zeta]
        C = mm.C_of_zeta(zeta, K)
        r = mm.rk4_mu(PH[idx], W[idx], mu, hub, f, K, C, t_sim=16.0, t_burn=12.0, n_per=n_per,
                      v0=np.array([cases[i][3] for i in idx]))
        for j, i in enumerate(idx):
            out.append((i, r['liftoff'][j], r['F_max'][j]))
    out.sort()
    print(f'n_per={n_per}: ' + ' | '.join(f'#{i} {cases[i][0]} w{cases[i][1]} z{cases[i][2]} v{cases[i][3]}: {l:.1f}%/{fm:.0f}N' for i, l, fm in out))
