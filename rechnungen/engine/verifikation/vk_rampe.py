"""Gegenprüfung ENG-10 (und ENG-08): Frequenzhochlauf bei festen Phasen.

Eigene Umsetzung in Schwerpunktkoordinaten (vk_rk4com, Rampe ohne rho'-Term: z = Z - ebar(theta),
z' = V - rho*ebar'(theta)); Start aus Ruhe (rho(0) = 0, z = -Mg/K, z' = 0, V = 0).
Lauf 40 s mit RK4-S (Schritt DT), Auswertung 30–40 s; danach Fortsetzung des Endzustands mit dem
halbanalytischen Löser SA über 10 s (Klassifikation ohne Festschritt-Artefakt).
Aufruf: python3 vk_rampe.py TR DT_us
"""
import os
import sys, json, time
import numpy as np
import vk_model as m
import vk_rk4com as rk
import vk_sa as sa

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
D = 360.0 / 19
PTS = {'Insel': (35.0, 116.0), 'HotSpot': (0.0, 208.421), 'Sync': (0.0, 0.0),
       'P6A': (0, 6 * D), 'P6B': (13 * D, 13 * D), 'P13A': (6 * D, 6 * D), 'P13B': (13 * D, 0.0),
       'P49A': (3 * D, 7 * D), 'P49B': (16 * D, 4 * D), 'P45A': (12 * D, 17 * D), 'P45B': (14 * D, 2 * D),
       'P33A': (1 * D, 16 * D), 'P33B': (3 * D, 4 * D)}


def main(Tr, dt):
    names = list(PTS)
    p2 = np.array([PTS[k][0] for k in names]); p3 = np.array([PTS[k][1] for k in names])
    n_cyc = 400
    t = time.time()
    r = rk.run(p2, p3, dt=dt, n_cyc=n_cyc, Tr=Tr)
    w = rk.window(r, 300, 400)
    w2 = rk.window(r, 200, 300)
    L = [f'Rampe Tr = {Tr} s, RK4-S dt = {dt*1e6:.1f} µs, Laufzeit {time.time()-t:.0f} s']
    res = {}
    for j, nm in enumerate(names):
        s = sa.SA(p2[j], p3[j])
        R = s.run(r['PZ'][n_cyc, j], r['PV'][n_cyc, j], n_cyc * m.T, 100)
        st = sa.stats(R, 50, 100)
        per = sa.period(R, n_last=30, tol_v=1e-8, tol_z=1e-10)
        # Einschwingmaß aus RK4-S: letzter Zyklus, in dem der zyklusweise Liftoff-Anteil um > 1 %-Pkt vom
        # Mittel 30–40 s abweicht (grob)
        lam_c = r['LO'][:, j] / r['n_per'] * 100
        dev = np.where(np.abs(lam_c - w['lam'][j]) > 1.0)[0]
        res[nm] = dict(phi2=p2[j], phi3=p3[j], lam_20_30=float(w2['lam'][j]), lam_30_40=float(w['lam'][j]),
                       skew=float(w['skew'][j]), Fmax=float(w['Fmax'][j]), Fmin=float(w['Fmin'][j]),
                       sa_lam=st['lam'], sa_skew=st['skew'], sa_Fmax=st['Fmax'], sa_period=per[0])
        L.append(f'{nm:8s} ({p2[j]:8.3f},{p3[j]:8.3f}): RK4-S lam 20–30 s {w2["lam"][j]:7.3f}, 30–40 s {w["lam"][j]:7.3f} %, '
                 f'F_max {w["Fmax"][j]:6.2f}, F_min {w["Fmin"][j]:.4f} | SA-Fortsetzung 45–50 s: lam {st["lam"]:7.3f} %, '
                 f'gamma1 {st["skew"]:.4f}, F_max {st["Fmax"]:.2f}, Periode {per[0]}')
    txt = '\n'.join(L)
    print(txt)
    tag = f'Tr{Tr:g}_dt{dt*1e6:g}us'
    open(OUT + f'vk_rampe_{tag}_ausgabe.txt', 'w').write(txt + '\n')
    json.dump(res, open(OUT + f'vk_rampe_{tag}.json', 'w'), indent=1, default=float)


if __name__ == '__main__':
    main(float(sys.argv[1]), float(sys.argv[2]) * 1e-6)
