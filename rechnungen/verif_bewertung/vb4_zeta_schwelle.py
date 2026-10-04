"""vb4_zeta_schwelle.py – Trägt die Schwelle ζ ≈ 0,152 (bewertung_a, 1-periodischer Orbit) auch für große
Würfe (bis 1,5 m/s) und andere Orbittypen? P2-Modell rk4_mu, V1-Vorschlag, synchron und (0°,180°),
vier Wurfphasen, Δt = T/2000."""
import os
import sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../auslegung'))
import mu_modell as mm
mu, hub, f, K = 0.4615, 8e-3, 10.0, 1.5e6
cfgs = [(0, 0, 0), (0, 0, 180)]
shifts = [0, 90, 180, 270]
v0s = [0.5, 1.0, 1.5]
for zeta in (0.1, 0.14, 0.17, 0.2):
    C = mm.C_of_zeta(zeta, K)
    PH, V0 = [], []
    for c in cfgs:
        for s in shifts:
            for v in v0s:
                PH.append(tuple((x + s) % 360 for x in c)); V0.append(v)
    PH = np.array(PH, float); V0 = np.array(V0)
    r = mm.rk4_mu(PH, np.ones((len(PH), 3)), mu, hub, f, K, C, t_sim=16.0, t_burn=12.0, n_per=2000, v0=V0)
    lam = np.asarray(r['liftoff']); fmax = np.asarray(r['F_max'])
    i = 0
    for c in cfgs:
        hits = []
        for s in shifts:
            for v in v0s:
                if lam[i] > 1: hits.append(f's{s}/v{v}:{lam[i]:.1f}%/{fmax[i]:.0f}N')
                i += 1
        print(f'zeta={zeta}: {c}: {"keine" if not hits else "; ".join(hits)}')
