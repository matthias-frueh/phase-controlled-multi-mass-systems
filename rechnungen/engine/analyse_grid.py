"""P2/engine – Auswertung 19x19 mit drei Starts (std, imp, ramp2), je 40 s, exakte Phasen i*360/19.

1. Abgleich std (5–15 s) mit data/sweep_19x19.csv (skalare Engine, gerundete Phasen).
2. Symmetrieverletzungen je Start und Fenster (5–15 s, 30–40 s), volle Gruppe der Ordnung 6.
3. Startabhängigkeit je Rasterpunkt (30–40 s): |Δλ| zwischen den Starts.
4. Je Symmetriebahn alle Läufe (Mitglieder x Starts = bis zu 18 Anfangsbedingungen derselben Konfiguration):
   Anzahl unterscheidbarer Endzustände (Untergrenze für die Zahl der Attraktoren).
"""
import os
import json
import numpy as np
import pandas as pd
import eng, run_seg
from sym_count import G, orbits

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
N = 19
csv = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data/sweep_19x19.csv'))
csv['i2'] = np.round(csv.phi2_deg / (360 / N)).astype(int) % N
csv['i3'] = np.round(csv.phi3_deg / (360 / N)).astype(int) % N
ref = {(r.i2, r.i3): r for r in csv.itertuples()}

data = {}
for st in ('std', 'imp', 'ramp2'):
    r, L = run_seg.load(OUT + f'spec_grid_{st}.json', OUT + f'run_grid_{st}')
    nC = r['S1'].shape[0]
    for wn, (c0, c1) in {'eng': (50, 150), 'late': (nC - 100, nC)}.items():
        w = eng.window(r, c0, c1)
        for k, l in enumerate(L):
            key = (l['i2'], l['i3'])
            d = data.setdefault((st, wn), {})
            d[key] = dict(lam=w['lam'][k], skew=w['skew'][k], Fmin=w['Fmin'][k], Fmax=w['Fmax'][k],
                          Fmean=eng.MG + w['dF_left_ppm'][k] * eng.MG / 1e6, R=w['R_ppm'][k])
    # Periode (locker) aus dem Poincaré-Schnitt
    for k, l in enumerate(L):
        p, ts = eng.periodicity(r, k, n_last=50, tol_v=1e-3, tol_z=1e-4)
        data[(st, 'late')][(l['i2'], l['i3'])]['per'] = p

lines = []
P = lambda s: (lines.append(s), print(s))

# 1. Abgleich mit CSV
d = data[('std', 'eng')]
dl = np.array([abs(d[k]['lam'] - ref[k].liftoff) for k in d])
ds = np.array([abs(d[k]['skew'] - ref[k].F_skew) for k in d])
P(f'1. std (exakte Phasen, numpy) 5–15 s gegen CSV: |Δλ| > 0,01 %-Pkt an {int((dl > 0.01).sum())}, > 1 %-Pkt an '
  f'{int((dl > 1).sum())} Punkten; |Δγ1| > 1e-3 an {int((ds > 1e-3).sum())}; max |Δλ| = {dl.max():.2f} %-Pkt')
big = sorted([(dl[i], k) for i, k in enumerate(d)], reverse=True)[:8]
P('   größte Abweichungen: ' + '; '.join(f'{k}: {ref[k].liftoff:.2f} -> {d[k]["lam"]:.2f}' for _, k in big))

# 2. Symmetrieverletzungen
orb = orbits()
TOL = dict(lam=0.5, skew=0.01, Fmax=0.1, Fmean=1e-3, Fmin=1e-3)
P('2. Verletzte Punkte (volle Gruppe) je Start/Fenster, Toleranzen ' + ', '.join(f'{q} {t:g}' for q, t in TOL.items()))
sym = {}
for (st, wn), dd in sorted(data.items()):
    row = {}
    for q, tol in TOL.items():
        bad = set()
        for (i, j), v in dd.items():
            for gname in ('(23)', '(12)', '(13)', '(123)', '(132)'):
                if abs(v[q] - dd[G[gname](i, j)][q]) > tol:
                    bad.add((i, j))
        row[q] = len(bad)
    nb = sum(1 for o in orb if max(dd[p]['lam'] for p in o) - min(dd[p]['lam'] for p in o) > TOL['lam'])
    sym[f'{st}|{wn}'] = dict(row, bahnen_lam=nb)
    P(f'   {st:6s} {wn:5s}: ' + '  '.join(f'{q} {n:3d}' for q, n in row.items()) + f'   Bahnen (λ) {nb}/70')
dd = {k: dict(lam=ref[k].liftoff, skew=ref[k].F_skew, Fmax=ref[k].F_max, Fmean=ref[k].F_mean, Fmin=ref[k].F_min) for k in ref}
row = {}
for q, tol in TOL.items():
    bad = set()
    for (i, j), v in dd.items():
        for gname in ('(23)', '(12)', '(13)', '(123)', '(132)'):
            if abs(v[q] - dd[G[gname](i, j)][q]) > tol:
                bad.add((i, j))
    row[q] = len(bad)
P('   CSV           : ' + '  '.join(f'{q} {n:3d}' for q, n in row.items()))

# 3. Startabhängigkeit je Punkt (30–40 s)
lam = {st: np.array([data[(st, 'late')][(i, j)]['lam'] for i in range(N) for j in range(N)]) for st in ('std', 'imp', 'ramp2')}
spread = np.max(np.stack(list(lam.values())), 0) - np.min(np.stack(list(lam.values())), 0)
P(f'3. Startabhängigkeit 30–40 s: Spannweite λ über drei Starts > 1 %-Pkt an {int((spread > 1).sum())} von 361 Punkten '
  f'({100 * (spread > 1).mean():.1f} %), > 5 %-Pkt an {int((spread > 5).sum())}; '
  f'|λ_std − λ_imp| > 1: {int((np.abs(lam["std"] - lam["imp"]) > 1).sum())}, |λ_std − λ_ramp2| > 1: '
  f'{int((np.abs(lam["std"] - lam["ramp2"]) > 1).sum())}')
lt5 = np.array([data[('std', 'eng')][(i, j)]['lam'] for i in range(N) for j in range(N)])
ch = np.abs(lam['std'] - lt5)
P(f'   Längerer Burn-in (std, 5–15 s -> 30–40 s): |Δλ| > 0,5 %-Pkt an {int((ch > 0.5).sum())}, > 5 %-Pkt an {int((ch > 5).sum())} Punkten')

# 4. Zustände je Bahn
rows = []
for oi, o in enumerate(orb):
    runs = []
    for p in o:
        for st in ('std', 'imp', 'ramp2'):
            v = data[(st, 'late')][p]
            runs.append((v['lam'], v['skew'], v['Fmax'], st, p, v['per']))
    runs.sort()
    clusters = []
    for x in runs:
        for cl in clusters:
            if abs(cl[0][0] - x[0]) < 1.0 and abs(cl[0][1] - x[1]) < 0.03:
                cl.append(x); break
        else:
            clusters.append([x])
    rows.append(dict(bahn=oi, groesse=len(o), n_laeufe=len(runs), n_zustaende=len(clusters),
                     zustaende=' | '.join(f'λ={np.mean([c[0] for c in cl]):.2f} γ1={np.mean([c[1] for c in cl]):.3f} '
                                          f'Fmax={np.mean([c[2] for c in cl]):.2f} n={len(cl)} '
                                          f'[{",".join(sorted(set(c[3] for c in cl)))}]' for cl in clusters),
                     punkte=' '.join(f'({a},{b})' for a, b in o)))
bz = pd.DataFrame(rows).sort_values('n_zustaende', ascending=False)
bz.to_csv(OUT + 'grid_bahnen_zustaende.csv', index=False)
multi = bz[bz.n_zustaende > 1]
npts = int(multi.groesse.sum())
P(f'4. Bahnen mit >= 2 unterscheidbaren Endzuständen (λ-Abstand >= 1 %-Pkt oder γ1-Abstand >= 0,03; 30–40 s): '
  f'{len(multi)} von 70 Bahnen = {npts} von 361 Rasterpunkten ({100 * npts / 361:.1f} %); davon mit 3+ Zuständen: '
  f'{int((bz.n_zustaende > 2).sum())}')
with pd.option_context('display.width', 400, 'display.max_colwidth', 300):
    P(multi[['bahn', 'groesse', 'n_zustaende', 'zustaende', 'punkte']].to_string(index=False))
# robuste Zählung: Einzelverknüpfung in λ mit Lückenkriterium (statistische Schwankung chaotischer Zustände
# über 10 s liegt bei <= 2,5 %-Pkt, Blockstatistik der Nachrechnung 13.09.)
def gapclusters(vals, gap):
    v = sorted(vals)
    n = 1
    for x, y in zip(v[:-1], v[1:]):
        if y - x > gap:
            n += 1
    return n
for gap in (3.0, 5.0):
    nb = [(oi, len(o)) for oi, o in enumerate(orb)
          if gapclusters([data[(st, 'late')][p]['lam'] for p in o for st in ('std', 'imp', 'ramp2')], gap) > 1]
    P(f'   robust (λ-Lücke > {gap:g} %-Pkt zwischen Zustandsgruppen): {len(nb)} Bahnen = {sum(n for _, n in nb)} Rasterpunkte '
      f'({100 * sum(n for _, n in nb) / 361:.1f} %)')
    if gap == 3.0:
        robust_multi = nb
for st in ('std', 'imp', 'ramp2'):
    viol = [oi for oi, o in enumerate(orb) if max(data[(st, 'late')][p]['lam'] for p in o) - min(data[(st, 'late')][p]['lam'] for p in o) > 0.5]
    P(f'   {st}: Bahnen mit λ-Spannweite > 0,5 %-Pkt (30–40 s): {viol}')
hop = sum(1 for o in orb if any(data[(st, 'late')][p]['lam'] > 74 for p in o for st in ('std', 'imp', 'ramp2')))
P(f'   Bahnen, in denen ein Hüpfzustand (λ > 74 %) erreicht wird: {hop} von 70')
json.dump(dict(sym=sym, n_multi_bahnen=len(multi), n_multi_punkte=npts, robust_multi_3pp=robust_multi), open(OUT + 'grid_auswertung.json', 'w'), indent=1)
open(OUT + 'analyse_grid_ausgabe.txt', 'w').write('\n'.join(lines) + '\n')
