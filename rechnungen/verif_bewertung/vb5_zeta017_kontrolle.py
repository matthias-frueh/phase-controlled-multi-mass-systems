"""vb5_zeta017_kontrolle.py – Zeitschrittkontrolle des Hüpftreffers bei ζ = 0,17 (synchron, Wurf 0,5 m/s, t0 = 0)
und Feinabtastung ζ = 0,15…0,20 (Δt = T/4000), P2-Modell rk4_mu, V1-Vorschlag."""
import os
import sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../auslegung'))
import mu_modell as mm
mu, hub, f, K = 0.4615, 8e-3, 10.0, 1.5e6
for zeta in (0.15, 0.16, 0.17, 0.18, 0.19, 0.20):
    C = mm.C_of_zeta(zeta, K)
    PH = np.array([[0, 0, 0]] * 3, float); V0 = np.array([0.5, 0.7, 1.0])
    r = mm.rk4_mu(PH, np.ones((3, 3)), mu, hub, f, K, C, t_sim=16.0, t_burn=12.0, n_per=4000, v0=V0)
    print(f'zeta={zeta}: ' + ' | '.join(f'v0={V0[j]}: lambda={r["liftoff"][j]:.1f}%, F_max={r["F_max"][j]:.0f} N' for j in range(3)))
