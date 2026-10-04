"""Gegenprüfung ENG-09 (P1-These Impulskonsistenz): Symmetrieverletzungen im exakten Modell (SA) mit
impulskonsistentem Start (V_S(0) = 0), 30 s, Fenster 20–30 s, gegen SA-Standardstart (10–20 s) und CSV.
Zustandsgruppen je Bahn über Mitglieder x {SA std, SA imp} (lambda-Lücke > 3 %-Pkt).
"""
import os
import glob
import numpy as np
import pandas as pd
from vk_grid_analyse import count, ORBS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')


def main():
    L = []
    imp = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(OUT + 'vk_gridsa_imp_csv_*.csv'))]).drop_duplicates(['i2', 'i3'])
    std = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(OUT + 'vk_gridsa_csv_*.csv'))]).drop_duplicates(['i2', 'i3'])
    L.append(f'SA imp: {len(imp)} Punkte, SA std: {len(std)} Punkte')
    ti = {(r.i2, r.i3): r.lam_b for r in imp.itertuples()}
    ts = {(r.i2, r.i3): r.lam_b for r in std.itertuples()}
    for nm, tab in (('SA std 10–20 s', ts), ('SA imp 20–30 s', ti)):
        L.append(f'{nm}: verletzte Punkte/Bahnen ' + '  '.join(f'>{t:g}: {count(tab, t)[0]}/{count(tab, t)[1]}' for t in (0.1, 0.5, 1.0, 5.0))
                 + f'; Median {np.median(list(tab.values())):.2f} %, lambda>74 %: {sum(v > 74 for v in tab.values())}')
    vi = {bi for bi, o in enumerate(ORBS) if max(ti[p] for p in o) - min(ti[p] for p in o) > 0.5}
    vs = {bi for bi, o in enumerate(ORBS) if max(ts[p] for p in o) - min(ts[p] for p in o) > 0.5}
    L.append(f'Bahnen verletzt (> 0,5): std {sorted(vs)}; imp {sorted(vi)}; gemeinsam {sorted(vs & vi)}')
    for bi in sorted(vs | vi):
        o = ORBS[bi]
        L.append(f'   Bahn {bi}: std ' + ' '.join(f'{ts[p]:.1f}' for p in o) + ' | imp ' + ' '.join(f'{ti[p]:.1f}' for p in o))
    nb = npts = 0
    for o in ORBS:
        vals = np.sort([ts[p] for p in o] + [ti[p] for p in o])
        if np.any(np.diff(vals) > 3.0):
            nb += 1; npts += len(o)
    L.append(f'Bahnen mit >= 2 Zustandsgruppen (Lücke > 3 %-Pkt) aus SA std + SA imp: {nb} Bahnen, {npts} Punkte')
    span = np.array([abs(ts[p] - ti[p]) for p in ts])
    L.append(f'|lambda_std - lambda_imp| > 1 %-Pkt an {(span > 1).sum()} Punkten, > 5 an {(span > 5).sum()}')
    txt = '\n'.join(L)
    print(txt)
    open(OUT + 'vk_gridsa_imp_analyse_ausgabe.txt', 'w').write(txt + '\n')


if __name__ == '__main__':
    main()
