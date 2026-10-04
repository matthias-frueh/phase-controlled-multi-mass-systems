"""Gegenprüfung: 19x19 mit SA (Standardstart, CSV-Phasen) gegen CSV (RK4, dt = 50 µs) und gegen RK4-S.
Zählt Abweichungen und Symmetrieverletzungen (volle Gruppe) im exakten Modell.
"""
import os
import glob
import numpy as np
import pandas as pd
import vk_model as m
from vk_grid_analyse import count, ORBS, IMG

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
N = 19
D = 360.0 / N


def main():
    L = []
    sa_ = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(OUT + 'vk_gridsa_csv_*.csv'))]).drop_duplicates(['i2', 'i3'])
    L.append(f'SA-Raster: {len(sa_)} von 361 Punkten')
    csv = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data/sweep_19x19.csv'))
    csv['i2'] = np.rint(csv.phi2_deg / D).astype(int) % N
    csv['i3'] = np.rint(csv.phi3_deg / D).astype(int) % N
    g = sa_.merge(csv, on=['i2', 'i3'])
    rk = pd.read_csv(OUT + 'vk_grid_std.csv')[['i2', 'i3', 'lam_a', 'lam_b']].rename(columns={'lam_a': 'rk_a', 'lam_b': 'rk_b'})
    g = g.merge(rk, on=['i2', 'i3'])
    d = (g.lam_a - g.liftoff).abs()
    L.append(f'SA 5–15 s gegen CSV (lambda): |d| > 0.01: {(d > 0.01).sum()}, > 0.1: {(d > 0.1).sum()}, > 1: {(d > 1).sum()}, > 5: {(d > 5).sum()}')
    dF = (g.dF_ppm_a * m.MG * 1e-6 - (g.F_mean - m.MG)).abs()
    L.append(f'SA 5–15 s gegen CSV (<N>-Mg): |d| > 0.1 mN: {(dF > 1e-4).sum()}, > 1 mN: {(dF > 1e-3).sum()}, > 10 mN: {(dF > 1e-2).sum()}')
    dk = (g.Fmax_a - g.F_max).abs()
    L.append(f'SA 5–15 s gegen CSV (F_max): |d| > 0.1 N: {(dk > 0.1).sum()}, > 1 N: {(dk > 1).sum()}')
    lo = g[g.lam_a == 0]
    L.append(f'Kontaktpunkte (SA lambda = 0): {len(lo)}; max |dF_min| gegen CSV {np.max(np.abs(lo.Fmin_a - lo.F_min)):.2e} N, '
             f'max |dgamma1| {np.max(np.abs(lo.skew_a - lo.F_skew)):.2e}')
    L.append('Punkte mit |dlambda| > 1 %-Pkt (CSV -> SA 5–15 s; RK4-S std 5–15 s):')
    for r in g[d > 1].sort_values('i2').itertuples():
        L.append(f'   ({r.i2},{r.i3}) = ({r.phi2_deg:.3f},{r.phi3_deg:.3f}): CSV {r.liftoff:.2f}, SA {r.lam_a:.2f} (10–20 s {r.lam_b:.2f}), '
                 f'RK4-S {r.rk_a:.2f}; <N>-Mg CSV {(r.F_mean-m.MG)*1e3:+.2f} mN, SA {r.dF_ppm_a*m.MG*1e-3:+.3f} mN')
    hs = g[(g.i2 == 0) & (g.i3 == 11)].iloc[0]
    L.append(f'Hot-Spot (0,11): CSV <N>-Mg {(hs.F_mean-m.MG)*1e3:+.3f} mN, lambda {hs.liftoff:.3f}, F_max {hs.F_max:.3f} | '
             f'SA {hs.dF_ppm_a*m.MG*1e-3:+.4f} mN, lambda {hs.lam_a:.4f}, F_max {hs.Fmax_a:.3f}')
    # Symmetrieverletzungen im SA-Raster
    for w in ('a', 'b'):
        tab = {(r.i2, r.i3): getattr(r, f'lam_{w}') for r in g.itertuples()}
        L.append(f'SA std, Fenster {"5–15" if w == "a" else "10–20"} s, verletzte Punkte/Bahnen (lambda): '
                 + '  '.join(f'>{t:g}: {count(tab, t)[0]}/{count(tab, t)[1]}' for t in (0.1, 0.5, 1.0, 5.0))
                 + f'; Median {np.median(list(tab.values())):.2f} %, lambda>74 %: {sum(v > 74 for v in tab.values())}')
    tabc = {(r.i2, r.i3): r.liftoff for r in g.itertuples()}
    tabs = {(r.i2, r.i3): r.lam_b for r in g.itertuples()}
    # Bahnen verletzt in CSV (> 0.5) vs SA
    vc = {bi for bi, o in enumerate(ORBS) if max(tabc[p] for p in o) - min(tabc[p] for p in o) > 0.5}
    vs = {bi for bi, o in enumerate(ORBS) if max(tabs[p] for p in o) - min(tabs[p] for p in o) > 0.5}
    L.append(f'Bahnen verletzt (> 0,5 %-Pkt): CSV {len(vc)}, SA {len(vs)}, beide {len(vc & vs)}; nur CSV {sorted(vc - vs)}, nur SA {sorted(vs - vc)}')
    for bi in sorted(vc | vs):
        o = ORBS[bi]
        L.append(f'   Bahn {bi}: CSV ' + ' '.join(f'{tabc[p]:.1f}' for p in o) + ' | SA ' + ' '.join(f'{tabs[p]:.1f}' for p in o))
    # (23)-Paare (Vertauschung Modul 2<->3, keine Zeitverschiebung, Start identisch)
    for nm, col in (('CSV', 'liftoff'), ('SA 5–15 s', 'lam_a'), ('SA 10–20 s', 'lam_b')):
        tab = {(r.i2, r.i3): getattr(r, col) for r in g.itertuples()}
        dd = [abs(tab[(i, j)] - tab[(j, i)]) for i in range(N) for j in range(N) if i < j]
        L.append(f'(23)-Paare {nm}: {sum(x > 0 for x in dd)} von {len(dd)} mit Differenz > 0, > 0.01: {sum(x > 0.01 for x in dd)}, '
                 f'> 0.1: {sum(x > 0.1 for x in dd)}, max {max(dd):.3f} %-Pkt')
    tabF = {(r.i2, r.i3): r.F_mean for r in g.itertuples()}
    ddF = [abs(tabF[(i, j)] - tabF[(j, i)]) for i in range(N) for j in range(N) if i < j]
    L.append(f'(23)-Paare CSV F_mean: max {max(ddF)*1e3:.2f} mN, Paare mit > 0: {sum(x > 0 for x in ddF)}')
    txt = '\n'.join(L)
    print(txt)
    open(OUT + 'vk_gridsa_analyse_ausgabe.txt', 'w').write(txt + '\n')


if __name__ == '__main__':
    main()
