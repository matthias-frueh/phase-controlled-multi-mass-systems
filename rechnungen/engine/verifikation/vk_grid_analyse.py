"""Gegenprüfung ENG-07/ENG-09: Symmetriezählung (eigene Gruppe aus vk_paare.elements) auf der CSV und auf den
eigenen RK4-S-Rastern; Startabhängigkeit über Starts; Kartenmediane.
"""
import json, os
import numpy as np
import pandas as pd
import vk_paare as vp

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
N = 19
D = 360.0 / N


def images(i, j):
    res = []
    for nm, (q2, q3), s in vp.elements(i * D, j * D):
        res.append((int(round(q2 / D)) % N, int(round(q3 / D)) % N))
    return res


IMG = {(i, j): images(i, j) for i in range(N) for j in range(N)}
ORBS = []
_seen = set()
for i in range(N):
    for j in range(N):
        if (i, j) not in _seen:
            o = sorted(set(IMG[(i, j)]))
            _seen |= set(o)
            ORBS.append(o)


def count(tab, tol):
    """tab: dict (i,j)->Wert. Punkt verletzt, wenn |Wert - Wert(gP)| > tol für irgendein g."""
    pts = {p for p in tab if any(abs(tab[p] - tab[q]) > tol for q in IMG[p])}
    orbs = sum(1 for o in ORBS if max(tab[p] for p in o) - min(tab[p] for p in o) > tol)
    return len(pts), orbs


def main():
    L = []
    csv = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data/sweep_19x19.csv'))
    csv['i2'] = np.rint(csv.phi2_deg / D).astype(int) % N
    csv['i3'] = np.rint(csv.phi3_deg / D).astype(int) % N
    L.append('CSV (Standardstart, 5–15 s, Engine-Arithmetik):')
    for q, tols in {'liftoff': [0.01, 0.1, 0.5, 1.0], 'F_skew': [1e-3, 1e-2, 0.1], 'F_min': [1e-4, 1e-3],
                    'F_mean': [1e-4, 1e-3], 'F_max': [1e-2, 0.1, 1.0]}.items():
        tab = {(r.i2, r.i3): getattr(r, q) for r in csv.itertuples()}
        L.append(f'  {q:8s} ' + '  '.join(f'>{t:g}: {count(tab, t)[0]}/{count(tab, t)[1]}' for t in tols))
    # Nur Generator (12) wie P1 vermutlich
    tab = {(r.i2, r.i3): r.liftoff for r in csv.itertuples()}
    g12 = lambda i, j: ((-i) % N, (j - i) % N)
    for tol in (0.1, 0.5, 1.0):
        n12 = sum(1 for p in tab if abs(tab[p] - tab[g12(*p)]) > tol)
        L.append(f'  nur (12), lambda > {tol}: {n12} Punkte')
    tabs = {'CSV': {(r.i2, r.i3): r.liftoff for r in csv.itertuples()}}
    grids = {}
    for st in ('std', 'imp', 'ramp2'):
        f = OUT + f'vk_grid_{st}.csv'
        if os.path.exists(f):
            g = pd.read_csv(f)
            grids[st] = g
            for w in ('a', 'b'):
                tabs[f'{st}_{w}'] = {(r.i2, r.i3): getattr(r, f'lam_{w}') for r in g.itertuples()}
    L.append('\nVerletzte Punkte/Bahnen (lambda, volle Gruppe); a = 5–15 s, b = 30–40 s:')
    for nm, tab in tabs.items():
        L.append(f'  {nm:9s} ' + '  '.join(f'>{t:g}: {count(tab, t)[0]}/{count(tab, t)[1]}' for t in (0.1, 0.5, 1.0, 5.0))
                 + f'   Median lambda {np.median(list(tab.values())):.2f} %, Punkte lambda>74 %: {sum(v > 74 for v in tab.values())}')
    if 'std' in grids:
        g = grids['std'].merge(csv, on=['i2', 'i3'])
        d = (g.lam_a - g.liftoff).abs()
        L.append(f'\nRK4-S std (5–15 s) gegen CSV: |dlambda| > 0.01: {(d > 0.01).sum()}, > 1: {(d > 1).sum()}, > 5: {(d > 5).sum()}')
        for r in g[d > 1].itertuples():
            L.append(f'   ({r.i2},{r.i3}) CSV {r.liftoff:.2f} -> RK4-S {r.lam_a:.2f} %')
        dd = (grids['std'].lam_b - grids['std'].lam_a).abs()
        L.append(f'RK4-S std: 5–15 s -> 30–40 s |dlambda| > 0.5: {(dd > 0.5).sum()} Punkte')
    if len(grids) >= 2:
        sts = list(grids)
        lam = np.stack([grids[s].lam_b.values for s in sts])
        span = lam.max(0) - lam.min(0)
        L.append(f'\nlambda-Spannweite über Starts {sts} (30–40 s): > 1 %-Pkt an {(span > 1).sum()} Punkten, > 5 an {(span > 5).sum()}')
        # Bahnen mit >= 2 Zustandsgruppen (Lückenkriterium) über Mitglieder x Starts
        key = {(r.i2, r.i3): k for k, r in enumerate(grids[sts[0]].itertuples())}
        for gap in (3.0, 5.0):
            nb, npts = 0, 0
            for o in ORBS:
                vals = np.sort(np.concatenate([lam[:, key[p]] for p in o]))
                if np.any(np.diff(vals) > gap):
                    nb += 1; npts += len(o)
            L.append(f'  Bahnen mit Lücke > {gap} %-Pkt in lambda (Mitglieder x Starts): {nb} Bahnen, {npts} Punkte')
        nb74 = sum(1 for o in ORBS if any(lam[:, key[p]].max() > 74 for p in o))
        L.append(f'  Bahnen, in denen lambda > 74 % vorkommt: {nb74} von {len(ORBS)}')
    txt = '\n'.join(L)
    print(txt)
    open(OUT + 'vk_grid_analyse_ausgabe.txt', 'w').write(txt + '\n')


if __name__ == '__main__':
    main()
