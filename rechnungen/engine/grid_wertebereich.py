"""P2/engine – Wertebereich der Funktionale (AP v2.4 Tab. Wertebereich) je Start, 19x19, Fenster 30–40 s und
5–15 s, im Vergleich zum Archiv (data/sweep_19x19.csv)."""
import os
import numpy as np, pandas as pd
import eng, run_seg
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
csv = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data/sweep_19x19.csv'))
def line(name, lam, sk, A, fmax):
    print(f'{name:22s} λ: Median {np.median(lam):6.2f} %, Max {np.max(lam):6.2f} % | γ1: Min {np.min(sk):+.3f}, Median {np.median(sk):.3f}, '
          f'Max {np.max(sk):.3f} | A: Median {np.nanmedian(A):.3f}, Max {np.nanmax(A):.3f} | Fmax: Median {np.median(fmax):.2f}, Max {np.max(fmax):.2f} N | '
          f'λ > 74 %: {int((lam > 74).sum())} Punkte | γ1 < 0: {int((sk < 0).sum())}')
line('Archiv (CSV)', csv.liftoff.values, csv.F_skew.values, csv.peak_ratio.values, csv.F_max.values)
for st in ('std', 'imp', 'ramp2'):
    r, L = run_seg.load(OUT + f'spec_grid_{st}.json', OUT + f'run_grid_{st}')
    for wn, (c0, c1) in (('5-15 s', (50, 150)), ('30-40 s', (300, 400))):
        w = eng.window(r, c0, c1)
        line(f'{st} {wn}', w['lam'], w['skew'], w['A'], w['Fmax'])
