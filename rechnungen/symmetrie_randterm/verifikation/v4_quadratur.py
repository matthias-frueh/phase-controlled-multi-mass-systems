"""
v4_quadratur.py - Gegenpruefung RT-03: Quadraturrest Q = N1 - N_RK4 gegen dt, mit eigener RK4-Engine,
und Vergleich mit der EXAKTEN Bahn (ereignisgesteuert, v_exakt) am streng periodischen Punkt L1.
Aufruf: python3 v4_quadratur.py lauf   (RK4-Laeufe, speichert v4_quadratur_rk4.npz)
        python3 v4_quadratur.py exakt  (exakte Bahn L1/K1, Abtastmodell, Ausgabe)
Ablauf RK4: Standardstart, 300 Perioden mit dt = 50 us (frame) -> Zustand bei 30 s; Neustart mit
dt = 50/25/12,5/6,25 us, 20 Perioden Vorlauf, Fenster 32-42 s (100 Perioden).
Exakte Bahn: Start aus dem RK4-Zustand bei 30 s, 3 s integriert; letzte Periode = Attraktor.
  Q_abtast(dt) = (1/L) sum_i N_exakt(t_i) - <N>_exakt   (Linksrechteck exakter Werte, gleiches Raster)
  RK4-Stufenmodell (Gruppe): Q = (J/2 - w)/L mit w = 5J/6 (theta < 1/2) bzw. J/6 (theta > 1/2)
"""
import sys, time, numpy as np
import v_engine as ve

MG = ve.MG
PTS = [('L1', 157.3, 264.0), ('K1', 110.0, 234.0), ('HS', 0.0, 208.421)]
DTS = [5e-5, 2.5e-5, 1.25e-5, 6.25e-6]

if sys.argv[1] == 'lauf':
    P2 = [p[1] for p in PTS]; P3 = [p[2] for p in PTS]
    t1 = time.time()
    o = ve.run(P2, P3, 300, form='frame')
    x30, v30 = o['xend'].copy(), o['vend'].copy()
    print(f'Vorlauf 30 s: {time.time() - t1:.1f} s')
    res = {'x30': x30, 'v30': v30}
    for dt in DTS:
        t1 = time.time()
        o = ve.run(P2, P3, 120, dt=dt, t0=30.0, z0=x30, v0=v30, form='frame')
        w = ve.window(o, 20, 120)
        print(f'dt = {dt * 1e6:6.2f} us ({time.time() - t1:.0f} s): Q/ppm = {np.round(w["Q"] / MG * 1e6, 3)}  '
              f'E/N = {w["E"]}  R/ppm = {np.round(w["R"] / MG * 1e6, 3)}  lam = {w["lam"]}  Fmax = {w["Fmax"]}  '
              f'gam = {w["gam"]}')
        for k in ('Q', 'E', 'R', 'lam', 'Fmax', 'gam', 'N1', 'NW'):
            res[f'{k}_{dt:g}'] = w[k]
    np.savez('v4_quadratur_rk4.npz', **res)
    sys.exit()

import v_exakt as vx
r = np.load('v4_quadratur_rk4.npz')
print('RK4 (eigene Engine, frame), Fenster 32-42 s, Q in ppm von Mg:')
print('  dt/us      ' + '  '.join(f'{p[0]:>10s}' for p in PTS))
for dt in DTS:
    print(f'  {dt * 1e6:6.2f}   ' + '  '.join(f'{q:+10.4f}' for q in r[f'Q_{dt:g}'] / MG * 1e6) +
          '   E/N: ' + ' '.join(f'{e:+.2e}' for e in r[f'E_{dt:g}']))
print('  HS-Observablen: lam ' + ' -> '.join(f'{r[f"lam_{dt:g}"][2]:.4f}' for dt in DTS) +
      ';  F_max ' + ' -> '.join(f'{r[f"Fmax_{dt:g}"][2]:.3f}' for dt in DTS))

for j, nm in [(0, 'L1'), (1, 'K1')]:
    p2, p3 = PTS[j][1], PTS[j][2]
    b = vx.Bahn(p2, p3)
    t1 = time.time()
    b.integriere(30.0, float(r['x30'][j]), float(r['v30'][j]), 33.0)
    ta, tb = 32.9, 33.0
    Iex = b.impuls(ta, tb) / (tb - ta)
    tc = np.array([32.0, 32.5, 32.9])
    z, v = b.zustand(tc)
    print(f'\n{nm} exakt ({time.time() - t1:.0f} s): <N> letzte Periode = {Iex:.12f} N, (<N>-Mg)/Mg = '
          f'{(Iex - MG) / MG * 1e6:+.2e} ppm; Zustand bei 32,0/32,5/32,9 s: z = {z}, v = {v}')
    tds = [s for s in b.seg if s[0] == 'K' and ta <= s[1] < tb]
    for dt in DTS:
        L = int(round(ve.T / dt))
        tg = ta + np.arange(L) * dt
        Fg = b.kraft(tg)
        Qs = (Fg.mean() - Iex) / MG * 1e6
        line = f'  dt = {dt * 1e6:6.2f} us: Q_abtast(exakt) = {Qs:+9.4f} ppm | Q_RK4 = {r[f"Q_{dt:g}"][j] / MG * 1e6:+9.4f} ppm'
        if tds:
            t_td = tds[0][1]
            zz, vv = b.zustand(np.array([t_td - 1e-9]))
            J = ve.C0 * abs(vv[0])
            th = ((t_td - ta) / dt) % 1.0
            Qj = J * (th - 0.5) / L / MG * 1e6   # Euler-Maclaurin fuer exakte Werte mit Sprung J bei theta
            Qrk = (J / 2 - (5 * J / 6 if th < 0.5 else J / 6)) / L / MG * 1e6
            line += f' | Aufsetzen theta = {th:.3f}, J = {J:.4f} N, Abtastmodell J(theta-1/2)/L {Qj:+9.4f} ppm, Stufenmodell {Qrk:+9.4f} ppm, Schranke J/(3L) = {J / 3 / L / MG * 1e6:.4f} ppm'
        print(line)
