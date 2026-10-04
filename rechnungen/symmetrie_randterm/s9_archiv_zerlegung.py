"""s9_archiv_zerlegung.py - Teil B, Aufgabe 6 (Archivresiduen): Zerlegung des Archiv-Residuums
delta = (F_mean - Mg)/Mg aus data/sweep_19x19.csv (Fenster 5-15 s, Linksrechteck) in
R = M*dv_S/T_w, Q = N1 - N_RK4 und E = N_RK4 - Mg - R, mit der SKALAREN Referenz-Engine
(pcmms_v3a_phasen_sweep.rhs, unveraendert; Phasen wie im Archiv auf 3 Stellen gerundet).
Punkte: alle 45 mit |delta| > 50 ppm und eine Zufallsstichprobe von 25 der uebrigen 316.
Ausgabe: s9_archiv_zerlegung.csv"""
import os
import math
import time
import numpy as np
import pandas as pd
import pcmms_v3a_phasen_sweep as s

h = s.DT; M = s.M; MG = s.MG
T_CYC, THOLD, TFAST, RTOP, RBOT = s.T_CYC, s.THOLD, s.TFAST, s.RTOP, s.RBOT


def egg_v(t):
    phase = (t % T_CYC) / T_CYC
    if phase < THOLD:
        return RTOP * math.pi / (THOLD * T_CYC) * math.cos(math.pi * phase / THOLD)
    return -RBOT * math.pi / (TFAST * T_CYC) * math.cos(math.pi * (phase - THOLD) / TFAST)


def point(p2, p3):
    tau2 = math.radians(p2) / (2 * math.pi * s.F_HZ)
    tau3 = math.radians(p3) / (2 * math.pi * s.F_HZ)
    vcom = lambda zd, t: zd + (egg_v(t) + egg_v(t - tau2) + egg_v(t - tau3)) / 3.0
    z, zd = -MG / s.K, 0.0
    rhs = s.rhs
    s1 = 0.0; sw = 0.0; v0 = None
    F1 = np.empty(s.N_STEPS - s.N_BURN)
    for i in range(s.N_STEPS):
        t = i * h
        if i == s.N_BURN:
            v0 = vcom(zd, t)
        k1z, k1d, f1 = rhs(z, zd, t, tau2, tau3)
        k2z, k2d, f2 = rhs(z + 0.5 * h * k1z, zd + 0.5 * h * k1d, t + 0.5 * h, tau2, tau3)
        k3z, k3d, f3 = rhs(z + 0.5 * h * k2z, zd + 0.5 * h * k2d, t + 0.5 * h, tau2, tau3)
        k4z, k4d, f4 = rhs(z + h * k3z, zd + h * k3d, t + h, tau2, tau3)
        if i >= s.N_BURN:
            F1[i - s.N_BURN] = f1
            sw += (f1 + 2 * f2 + 2 * f3 + f4) / 6.0
        z = z + h * (k1z + 2 * k2z + 2 * k3z + k4z) / 6.0
        zd = zd + h * (k1d + 2 * k2d + 2 * k3d + k4d) / 6.0
    v1 = vcom(zd, s.N_STEPS * h)
    N = s.N_STEPS - s.N_BURN
    m1 = float(np.mean(F1)); mw = sw / N
    R = M * (v1 - v0) / (N * h)
    return m1, mw, R, v1 - v0, float(np.mean(F1 < 1e-9) * 100)


d = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data/sweep_19x19.csv'))
d['delta'] = (d.F_mean - MG) / MG * 1e6
big = d[d.delta.abs() > 50]
rest = d[d.delta.abs() <= 50].sample(25, random_state=7)
sel = pd.concat([big, rest])
rows = []
tic = time.time()
for r in sel.itertuples():
    m1, mw, R, dv, lam = point(r.phi2_deg, r.phi3_deg)
    rows.append(dict(phi2=r.phi2_deg, phi3=r.phi3_deg, arch_F_mean=r.F_mean, F_mean_N1=m1,
                     repro_diff_N=m1 - r.F_mean, arch_liftoff=r.liftoff, liftoff=lam,
                     delta_ppm=(m1 - MG) / MG * 1e6, R_ppm=R / MG * 1e6, Q_ppm=(m1 - mw) / MG * 1e6,
                     E_ppm=(mw - MG - R) / MG * 1e6, dv=dv, gruppe='gross' if abs(r.delta) > 50 else 'stichprobe'))
out = pd.DataFrame(rows)
out.to_csv('s9_archiv_zerlegung.csv', index=False, float_format='%.6g')
print(f'{len(out)} Punkte, Laufzeit {time.time() - tic:.0f} s')
print(f'Reproduktion der Archiv-F_mean: max |Diff| {out.repro_diff_N.abs().max():.2e} N '
      f'(CSV hat 6 Nachkommastellen); Punkte mit |Diff| > 1e-6 N: {(out.repro_diff_N.abs() > 1e-6).sum()}')
for g in ('gross', 'stichprobe'):
    o = out[out.gruppe == g]
    print(f'-- {g} ({len(o)} Punkte): |delta| max {o.delta_ppm.abs().max():.1f} ppm; |R| max {o.R_ppm.abs().max():.1f}; '
          f'|Q| max {o.Q_ppm.abs().max():.1f}, Median {o.Q_ppm.abs().median():.1f}; |E| max {o.E_ppm.abs().max():.3f} ppm')
o = out[out.delta_ppm.abs() > 200]
print(f'|delta| > 200 ppm: {len(o)} Punkte; Anteil R an delta: min {(o.R_ppm / o.delta_ppm).min():.3f}, '
      f'Median {(o.R_ppm / o.delta_ppm).median():.3f}')
o = out[(out.delta_ppm.abs() > 50)]
print(f'|delta| > 50 ppm: {len(o)} Punkte, davon mit |R| > |Q|: {(o.R_ppm.abs() > o.Q_ppm.abs()).sum()}')
print('Groesste zehn:')
print(out.reindex(out.delta_ppm.abs().sort_values(ascending=False).index).head(10)[
    ['phi2', 'phi3', 'arch_liftoff', 'delta_ppm', 'R_ppm', 'Q_ppm', 'E_ppm', 'dv']].to_string(index=False))
