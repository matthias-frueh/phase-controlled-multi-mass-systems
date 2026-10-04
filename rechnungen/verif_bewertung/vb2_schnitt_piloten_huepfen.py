"""
vb2_schnitt_piloten_huepfen.py – Ergänzung zu vb1: Wurfstarts an Schnitträndern, Triphasik-Punkt und
Pilotkonfigurationen am V1-Vorschlag (P2-Modell mu_modell.rk4_mu, Δt = T/2000; Stichprobe T/4000).
"""
import os
import sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../auslegung'))
import mu_modell as mm
mu, hub, f, K = 0.4615, 8e-3, 10.0, 1.5e6
cfgs = [(0, 100, 240), (0, 110, 240), (0, 120, 240), (0, 140, 240), (0, 110, 250), (0, 130, 230), (0, 110, 252), (0, 0, 180)]
shifts = [0, 90, 180, 270]
v0s = [0.5, 0.8, 1.0]
for n_per in (2000,):
    for zeta in (0.02, 0.05):
        C = mm.C_of_zeta(zeta, K)
        PH, V0 = [], []
        for c in cfgs:
            for s in shifts:
                for v in v0s:
                    PH.append(tuple((x + s) % 360 for x in c)); V0.append(v)
        PH = np.array(PH, float); V0 = np.array(V0)
        r = mm.rk4_mu(PH, np.ones((len(PH), 3)), mu, hub, f, K, C, t_sim=16.0, t_burn=12.0, n_per=n_per, v0=V0)
        lam = np.asarray(r['liftoff']); fmax = np.asarray(r['F_max'])
        print(f'n_per={n_per} zeta={zeta}')
        i = 0
        for c in cfgs:
            hits = []
            for s in shifts:
                for v in v0s:
                    if lam[i] > 1: hits.append(f'shift{s}/v{v}:{lam[i]:.1f}%/{fmax[i]:.0f}N')
                    i += 1
            print(f'   {c}: {"keine Hüpfzustände" if not hits else "; ".join(hits)}')
