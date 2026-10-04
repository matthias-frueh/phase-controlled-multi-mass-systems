"""Gegenprüfung ENG-09: Sind die per lambda-Lücke (RK4-S, 3 Starts, 30–40 s) gefundenen Mehrfachzustände
echte koexistierende Zustände des Modells? Für jede markierte Bahn werden der Lauf mit kleinstem und der mit
größtem lambda (Mitglied x Start) ab ihrem RK4-S-Endzustand (40 s) mit dem halbanalytischen Löser SA 20 s
fortgesetzt (Statistik 50–60 s). Bleiben beide getrennt, koexistieren zwei Zustände (Gleichwertigkeit der
Mitglieder per exakter Gruppensymmetrie, vk_paare.elements).
Aufruf: python3 vk_grid_sa.py i0 i1   (Index in der Liste markierter Bahnen)
"""
import os
import sys, json
import numpy as np
import pandas as pd
import vk_model as m
import vk_sa as sa
from vk_grid_analyse import ORBS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')


def flagged(gap=3.0):
    g = {st: pd.read_csv(OUT + f'vk_grid_{st}.csv') for st in ('std', 'imp', 'ramp2')}
    key = {(r.i2, r.i3): k for k, r in enumerate(g['std'].itertuples())}
    out = []
    for bi, o in enumerate(ORBS):
        lanes = [(st, p, g[st].lam_b.values[key[p]]) for p in o for st in g]
        vals = np.sort([x[2] for x in lanes])
        if np.any(np.diff(vals) > gap):
            lo = min(lanes, key=lambda x: x[2]); hi = max(lanes, key=lambda x: x[2])
            out.append((bi, lo, hi, g, key))
    return out


def main(i0, i1):
    fl = flagged()
    res = {}
    fn = OUT + f'vk_grid_sa_{i0}_{i1}.json'
    for bi, lo, hi, g, key in fl[i0:i1]:
        rr = []
        for st, p, lam in (lo, hi):
            row = g[st].iloc[key[p]]
            s = sa.SA(row.phi2, row.phi3)
            R = s.run(row.z_end, row.zd_end, 40.0, 200)
            stt = sa.stats(R, 100, 200)
            per = sa.period(R, n_last=50, tol_v=1e-8, tol_z=1e-10)
            blocks = [sa.stats(R, c, c + 50)['lam'] for c in range(0, 200, 50)]
            rr.append(dict(start=st, punkt=[int(p[0]), int(p[1])], lam_rk4=float(lam), lam_sa=stt['lam'],
                           Fmax_sa=stt['Fmax'], period=per[0], blocks=blocks))
        sep = abs(rr[0]['lam_sa'] - rr[1]['lam_sa'])
        res[str(bi)] = dict(lanes=rr, getrennt=bool(sep > 3.0), size=len(ORBS[bi]))
        print(f'Bahn {bi} (Größe {len(ORBS[bi])}): ' + ' | '.join(
            f'{x["start"]} {tuple(x["punkt"])}: RK4-S {x["lam_rk4"]:.2f} -> SA {x["lam_sa"]:.3f} % (P{x["period"]}, Blöcke '
            + ' '.join(f'{b:.2f}' for b in x['blocks']) + ')' for x in rr) + f'  getrennt: {sep > 3.0}', flush=True)
        json.dump(res, open(fn, 'w'), indent=1)


if __name__ == '__main__':
    main(int(sys.argv[1]), int(sys.argv[2]))
