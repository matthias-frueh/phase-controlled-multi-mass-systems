"""Gegenprüfung ENG-09: 19x19-Raster mit eigener Schwerpunkt-RK4 (RK4-S), Starts std / imp / ramp2, 40 s.
Aufruf: python3 vk_grid.py START [DT_us]   -> vk_grid_START.csv
"""
import os
import sys, time
import numpy as np
import pandas as pd
import vk_model as m
import vk_rk4com as rk

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
N = 19


def main(start, dt):
    ii, jj = np.meshgrid(np.arange(N), np.arange(N), indexing='ij')
    i2, i3 = ii.ravel(), jj.ravel()
    p2, p3 = i2 * 360.0 / N, i3 * 360.0 / N
    t = time.time()
    if start == 'ramp2':
        r = rk.run(p2, p3, dt=dt, n_cyc=400, Tr=2.0, verbose=True)
    else:
        r = rk.run(p2, p3, start=start, dt=dt, n_cyc=400, verbose=True)
    rows = {'i2': i2, 'i3': i3, 'phi2': p2, 'phi3': p3}
    for tag, (c0, c1) in {'a': (50, 150), 'b': (300, 400), 'c': (200, 300)}.items():
        w = rk.window(r, c0, c1)
        for k in ('lam', 'skew', 'Fmin', 'Fmax', 'dF_left_ppm', 'Q_ppm', 'R_ppm'):
            rows[f'{k}_{tag}'] = w[k]
    rows['z_end'] = r['PZ'][400]; rows['zd_end'] = r['PV'][400]
    df = pd.DataFrame(rows)
    df.to_csv(OUT + f'vk_grid_{start}{"" if dt == 5e-5 else "_dt%g" % (dt*1e6)}.csv', index=False, float_format='%.17g')
    print(f'{start}: fertig in {time.time()-t:.0f} s')


if __name__ == '__main__':
    main(sys.argv[1], float(sys.argv[2]) * 1e-6 if len(sys.argv) > 2 else 5e-5)
