"""Gegenprüfung ENG-07/08/09 und Hot-Spot: das 19x19-Raster mit dem halbanalytischen Löser SA (ohne
Festschritt), Standardstart (z = -Mg/K, z' = 0, t = 0), CSV-Phasen auf 3 Stellen gerundet wie in der CSV
und exakte Phasen i*360/19 wahlweise. 20 s; Fenster 5–15 s (wie CSV) und 10–20 s.
Aufruf: python3 vk_grid_sa_full.py CHUNK NCHUNK [exakt|csv] [std|imp] [NCYC]  -> vk_gridsa_[imp_]{tag}_{CHUNK}.csv (inkrementell);
Fenster b = letzte 10 s.
"""
import sys, os, time
import numpy as np
import pandas as pd
import vk_model as m
import vk_sa as sa

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
N = 19


def main(ch, nch, tag, start='std', ncyc=200):
    pts = [(i, j) for i in range(N) for j in range(N)]
    mine = pts[ch::nch]
    fn = OUT + (f'vk_gridsa_{tag}_{ch}.csv' if start == 'std' else f'vk_gridsa_{start}_{tag}_{ch}.csv')
    done = set()
    if os.path.exists(fn):
        d = pd.read_csv(fn)
        done = {(int(a), int(b)) for a, b in zip(d.i2, d.i3)}
    for (i, j) in mine:
        if (i, j) in done:
            continue
        if tag == 'csv':
            p2, p3 = round(i * 360.0 / N, 3), round(j * 360.0 / N, 3)
        else:
            p2, p3 = i * 360.0 / N, j * 360.0 / N
        t = time.time()
        s = sa.SA(p2, p3)
        v0 = 0.0 if start == 'std' else -float(m.ebar_v(0.0, s.taus))
        R = s.run(-m.MG / m.K, v0, 0.0, ncyc)
        a = sa.stats(R, 50, 150)
        b = sa.stats(R, ncyc - 100, ncyc)
        row = dict(i2=i, i3=j, phi2=p2, phi3=p3, lam_a=a['lam'], skew_a=a['skew'], Fmax_a=a['Fmax'], Fmin_a=a['Fmin'],
                   dF_ppm_a=a['dF_ppm'], lam_b=b['lam'], skew_b=b['skew'], Fmax_b=b['Fmax'], Fmin_b=b['Fmin'],
                   z_end=R['PZ'][-1], zd_end=R['PV'][-1], sec=time.time() - t)
        pd.DataFrame([row]).to_csv(fn, mode='a', header=not os.path.exists(fn), index=False, float_format='%.17g')
        print(f'({i},{j}) lam 5–15 {a["lam"]:.3f}  10–20 {b["lam"]:.3f}  [{time.time()-t:.1f} s]', flush=True)


if __name__ == '__main__':
    main(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else 'csv',
         sys.argv[4] if len(sys.argv) > 4 else 'std', int(sys.argv[5]) if len(sys.argv) > 5 else 200)
