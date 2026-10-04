"""
vb1_einzelmodul_huepfen.py – Gegenprüfung P3/bewertung_a B06 (P2-2):
Gilt die Hüpfgefahr bei steifem V1-Kontakt nur für die synchrone Phasung, oder auch für die
Einzelmodulläufe L_j, die in JEDEM Block der Phase 1 und in P0.8 laufen?
Näherung nach der Stoßabbildung (bewertung_a, P2 AUS-12): 1-periodischer Hüpforbit existiert, wenn
v_drive >= g*T*(1-e)/(2(1+e)), e = exp(-pi*zeta/sqrt(1-zeta^2)); für das Einzelmodul ist die
Anregung 1/3 der synchronen (v_drive = mu*pi*Hub*f/3).
Numerik: P2-Modell mu_modell.rk4_mu (einseitiger Kelvin-Voigt, kraftbasierte Ablösung), Gewichte
w = (1,0,0), Wurfstarts v0 bei verschiedenen Wurfphasen (über die Modulphase phi1), Δt = T/2000 und T/4000.
Nur lokale Rechnung, liest P2-Modul, schreibt nichts ins Repo.
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../auslegung'))
import mu_modell as mm

mu, hub, f, K = 0.4615, 8e-3, 10.0, 1.5e6
T = 1 / f
print('Naeherung Stossabbildung (1-periodischer Orbit):')
for lab, fac in (('synchron', 1.0), ('Einzelmodul', 1 / 3)):
    v = mu * np.pi * hub * f * fac
    q = v / (9.81 * T / 2)
    e_c = (1 - q) / (1 + q)
    # e = exp(-pi z/sqrt(1-z^2)) >= e_c  ->  z <= ...
    L = -np.log(e_c) / np.pi
    zc = L / np.sqrt(1 + L * L)
    print(f'  {lab:12s}: v_drive = {v:.4f} m/s, e_krit = {e_c:.3f}, zeta_krit = {zc:.3f}')

phases = [0, 60, 120, 180, 240, 300]
v0s = [0.1, 0.2, 0.3, 0.5, 0.8]
for n_per in (2000, 4000):
    for zeta in (0.02, 0.05, 0.1):
        C = mm.C_of_zeta(zeta, K)
        PH, V0 = [], []
        for p1 in phases:
            for v in v0s:
                PH.append((p1, 0, 0)); V0.append(v)
        PH = np.array(PH, float); V0 = np.array(V0)
        W = np.tile([1.0, 0.0, 0.0], (len(PH), 1))
        r = mm.rk4_mu(PH, W, mu, hub, f, K, C, t_sim=16.0, t_burn=12.0, n_per=n_per, v0=V0)
        lam = np.asarray(r['liftoff']); fmax = np.asarray(r['F_max'])
        print(f'n_per={n_per} zeta={zeta}:')
        for i, p1 in enumerate(phases):
            s = ' '.join(f'{V0[i*len(v0s)+j]:.1f}:{lam[i*len(v0s)+j]:5.1f}%/{fmax[i*len(v0s)+j]:6.1f}N'
                         for j in range(len(v0s)))
            print(f'   phi1={p1:3d}  {s}')
