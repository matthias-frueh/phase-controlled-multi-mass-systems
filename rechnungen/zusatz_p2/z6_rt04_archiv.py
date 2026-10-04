"""z6_rt04_archiv.py - Gegenpruefung RT-04 (Zerlegung der Archivresiduen in Randterm R, Quadraturrest Q, Simpson-Defekt E).

Rechenweg (eigene Herleitung, siehe PROTOKOLL):
  RK4-Impulsbilanz exakt in diskreter Form:  zd_end - zd_start = DT * sum_i [ -g + Fbar_i/M - abar_Simpson,i ]
  mit Fbar_i = (Fc1 + 2Fc2 + 2Fc3 + Fc4)/6 und abar_Simpson,i = (a(t) + 4a(t+DT/2) + a(t+DT))/6.
  => N_RK4 := mean_i Fbar_i = M g + R + E,  R = M (zd_end - zd_start)/T_w,  E = M mean_i abar_Simpson,i.
  Der Archivwert ist das Linksrechteck N1 = mean_i Fc1;  Q := N1 - N_RK4.
  (Ueber 100 ganze Perioden ist die mittlere Modulgeschwindigkeit periodisch, also R = M dv_S/T_w = M dzd/T_w.)
  E wird UNABHAENGIG aus dem Profil allein (eigene Profilfunktion zm.accel) berechnet; die Identitaet
  N_RK4 - Mg - R - E = 0 ist damit eine Probe.
  Zur bitgleichen Reproduktion der Bahn (Einschwingen, Liftoff) wird die rechte Seite der Referenz-Engine
  code/pcmms_v3a_phasen_sweep.rhs unveraendert importiert; Schleife und Bilanz sind eigener Code.
Aufruf: python3 z6_rt04_archiv.py [Anzahl Prozesse]
"""
import os
import sys
import time
import math
import numpy as np
import pandas as pd
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'code'))
import pcmms_v3a_phasen_sweep as eng   # noqa: E402
import zm                              # noqa: E402

DT, NST, NB, M, MG = eng.DT, eng.N_STEPS, eng.N_BURN, eng.M, eng.MG
TW = (NST - NB) * DT


def E_profile(p2, p3):
    """E = M * mean_i Simpson(abar) ueber die Fensterschritte, nur aus dem Profil (vektorisiert)."""
    t = np.arange(NB, NST) * DT
    tau2, tau3 = math.radians(p2) / (2 * math.pi * eng.F_HZ), math.radians(p3) / (2 * math.pi * eng.F_HZ)
    ab = lambda tt: (zm.accel(tt) + zm.accel(tt - tau2) + zm.accel(tt - tau3)) / 3
    s = (ab(t) + 4 * ab(t + 0.5 * DT) + ab(t + DT)) / 6
    return M * s.mean()


def point(args):
    p2, p3 = args
    tau2 = math.radians(p2) / (2 * math.pi * eng.F_HZ)
    tau3 = math.radians(p3) / (2 * math.pi * eng.F_HZ)
    rhs = eng.rhs
    z, zd = -MG / eng.K, 0.0
    s1 = 0.0; srk = 0.0; lift = 0; zd_start = None
    h = DT
    for i in range(NST):
        t = i * h
        if i == NB:
            zd_start = zd
        k1z, k1d, F1 = rhs(z, zd, t, tau2, tau3)
        k2z, k2d, F2 = rhs(z + 0.5 * h * k1z, zd + 0.5 * h * k1d, t + 0.5 * h, tau2, tau3)
        k3z, k3d, F3 = rhs(z + 0.5 * h * k2z, zd + 0.5 * h * k2d, t + 0.5 * h, tau2, tau3)
        k4z, k4d, F4 = rhs(z + h * k3z, zd + h * k3d, t + h, tau2, tau3)
        z = z + h * (k1z + 2 * k2z + 2 * k3z + k4z) / 6.0
        zd = zd + h * (k1d + 2 * k2d + 2 * k3d + k4d) / 6.0
        if i >= NB:
            s1 += F1
            srk += (F1 + 2 * F2 + 2 * F3 + F4) / 6.0
            lift += F1 < 1e-9
    n = NST - NB
    N1, NRK = s1 / n, srk / n
    R = M * (zd - zd_start) / TW
    E = E_profile(p2, p3)
    return dict(phi2=p2, phi3=p3, N1=N1, NRK=NRK, R=R, E=E, Q=N1 - NRK, ident=NRK - MG - R - E,
                liftoff=100 * lift / n)


if __name__ == '__main__':
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    t0 = time.time()
    arch = pd.read_csv(os.path.join(REPO, 'data', 'sweep_19x19.csv'))
    arch['d_ppm'] = (arch.F_mean - MG) / MG * 1e6
    big = arch[arch.d_ppm.abs() > 200]
    mid = arch[(arch.d_ppm.abs() > 50) & (arch.d_ppm.abs() <= 200)]
    small = arch[arch.d_ppm.abs() <= 50]
    rng = np.random.default_rng(20261002)
    pick = pd.concat([big, mid.iloc[rng.choice(len(mid), 10, replace=False)],
                      small.iloc[rng.choice(len(small), 8, replace=False)]])
    extra = arch[(arch.phi2_deg.round(3) == 246.316) & (arch.phi3_deg.round(3) == 113.684)]
    pick = pd.concat([pick, extra]).drop_duplicates(['phi2_deg', 'phi3_deg'])
    print(f'Archiv: {len(arch)} Punkte; |delta| > 200 ppm: {len(big)}, 50-200 ppm: {len(mid)}, <= 50 ppm: {len(small)}')
    print(f'Stichprobe: alle {len(big)} mit > 200 ppm, 10 von {len(mid)} (50-200 ppm), 8 von {len(small)} (<= 50 ppm), + (246.316, 113.684)')
    jobs = list(zip(pick.phi2_deg.astype(float), pick.phi3_deg.astype(float)))
    # Kontrolle: drei Punkte mit exakten Rasterphasen (k*360/19) statt der 3-stelligen CSV-Phasen
    exact = [(0.0, 11 * 360 / 19), (15 * 360 / 19, 16 * 360 / 19), (0.0, 360 / 19)]
    with Pool(nproc) as pool:
        res = pool.map(point, jobs + exact)
    r = pd.DataFrame(res[:len(jobs)])
    r = r.merge(arch[['phi2_deg', 'phi3_deg', 'F_mean', 'liftoff', 'd_ppm']], left_on=['phi2', 'phi3'],
                right_on=['phi2_deg', 'phi3_deg'])
    for c in ('R', 'Q', 'E', 'ident'):
        r[c + '_ppm'] = r[c] / MG * 1e6
    r['delta_ppm_N1'] = (r.N1 - MG) / MG * 1e6
    r['repro'] = r.N1 - r.F_mean
    r['R_anteil'] = r.R_ppm / r.delta_ppm_N1
    pd.set_option('display.width', 200)
    cols = ['phi2', 'phi3', 'liftoff_x', 'd_ppm', 'delta_ppm_N1', 'R_ppm', 'Q_ppm', 'E_ppm', 'ident_ppm', 'repro', 'R_anteil']
    r = r.rename(columns={'liftoff_x': 'liftoff_x'}) if 'liftoff_x' in r else r.rename(columns={'liftoff': 'liftoff_x'})
    print(r.sort_values('d_ppm', key=abs, ascending=False)[cols].to_string(index=False, float_format=lambda x: f'{x:.4g}'))
    print(f'\nReproduktion Archiv-F_mean: max|N1 - F_mean| = {r.repro.abs().max():.2e} N (CSV-Rundung 5e-7)')
    print(f'Identitaet N_RK4 - Mg - R - E: max {r.ident_ppm.abs().max():.1e} ppm')
    b = r[r.d_ppm.abs() > 200]
    print(f'|delta| > 200 ppm ({len(b)} Punkte): R/delta min {b.R_anteil.min():.4f}, Median {b.R_anteil.median():.4f}, '
          f'max {b.R_anteil.max():.4f}; |Q| max {b.Q_ppm.abs().max():.1f} ppm, Median {b.Q_ppm.abs().median():.1f}')
    m_ = r[(r.d_ppm.abs() > 50) & (r.d_ppm.abs() <= 200)]
    print(f'50 < |delta| <= 200 ppm ({len(m_)} Punkte): |R| > |Q| an {(m_.R_ppm.abs() > m_.Q_ppm.abs()).sum()}; '
          f'|Q| max {m_.Q_ppm.abs().max():.1f}, |R| max {m_.R_ppm.abs().max():.1f} ppm')
    s_ = r[r.d_ppm.abs() <= 50]
    print(f'|delta| <= 50 ppm ({len(s_)} Punkte): |R| max {s_.R_ppm.abs().max():.1f}, |Q| max {s_.Q_ppm.abs().max():.1f} ppm')
    print(f'|E| max ueber alle {len(r)} Punkte: {r.E_ppm.abs().max():.3f} ppm')
    print('\nKontrolle mit exakten Rasterphasen k*360/19 (nicht 3-stellig gerundet):')
    for (p2, p3), q in zip(exact, res[len(jobs):]):
        a = arch.iloc[((arch.phi2_deg - p2).abs() + (arch.phi3_deg - p3).abs()).argmin()]
        print(f'  ({p2:.6f}, {p3:.6f}): N1 = {q["N1"]:.6f} N gegen Archiv {a.F_mean:.6f} N (Diff {q["N1"]-a.F_mean:+.2e}); '
              f'R = {q["R"]/MG*1e6:.1f} ppm, Q = {q["Q"]/MG*1e6:.1f} ppm')
    print('\nE an Kontaktpunkten (nur Profil): (246.316, 113.684): %.3f ppm; K1 (110, 234): %.3f ppm; (120, 240): %.1e ppm' %
          (E_profile(246.316, 113.684) / MG * 1e6, E_profile(110, 234) / MG * 1e6, E_profile(120, 240) / MG * 1e6))
    print(f'CSV-Rundung 1e-6 N = {1e-6/MG*1e6:.3f} ppm')
    r.to_csv(os.path.join(HERE, 'z6_rt04_archiv.csv'), index=False)
    print(f'Laufzeit {time.time()-t0:.0f} s')
