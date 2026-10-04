"""P2/engine – Symmetrieanalyse der gespeicherten 19x19-Karte (data/sweep_19x19.csv).

Gruppe: Modulpermutation + globale Zeitverschiebung, wirkt auf Gitterindizes (i2, i3) mod 19
(phi = i * 360/19). Für eine Permutation, die Modul j zur neuen Referenz macht, gilt
abar_B(t) = abar_A(t + tau_j)  (reine Zeitverschiebung der Anregung), ausser für die
Vertauschung (2 3), die abar exakt unverändert lässt (auch der Standardstart ist dann identisch).

Ausgabe: Zählungen je Observable und Toleranz, getrennt nach Generator, plus Liste der verletzten Bahnen.
"""
import os
import sys, json, itertools
import numpy as np
import pandas as pd

N = 19
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data/sweep_19x19.csv')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')

# Gruppenelemente als Funktionen auf (i, j) mod N; Name, Abbildung, Zeitverschiebung (in Einheiten von phi)
G = {
    'e':    lambda i, j: (i % N, j % N),
    '(23)': lambda i, j: (j % N, i % N),            # Vertauschung Modul 2<->3, keine Zeitverschiebung
    '(12)': lambda i, j: ((-i) % N, (j - i) % N),   # Modul 2 wird Referenz, Verschiebung tau2
    '(13)': lambda i, j: ((i - j) % N, (-j) % N),   # Modul 3 wird Referenz, Verschiebung tau3
    '(123)': lambda i, j: ((j - i) % N, (-i) % N),  # zyklisch
    '(132)': lambda i, j: ((-j) % N, (i - j) % N),
}


def check_group():
    """Abgeschlossenheit: Verkettung zweier Elemente ergibt wieder ein Element."""
    pts = [(i, j) for i in range(N) for j in range(N)]
    names = list(G)
    for a, b in itertools.product(names, names):
        img = [G[a](*G[b](i, j)) for i, j in pts]
        ok = [n for n in names if all(G[n](i, j) == img[k] for k, (i, j) in enumerate(pts))]
        assert len(ok) == 1, (a, b)
    return True


def orbits():
    seen, orb = set(), []
    for i in range(N):
        for j in range(N):
            if (i, j) in seen:
                continue
            o = sorted({G[g](i, j) for g in G})
            seen |= set(o)
            orb.append(o)
    return orb


def main():
    check_group()
    df = pd.read_csv(DATA)
    df['i2'] = np.round(df.phi2_deg / (360 / N)).astype(int) % N
    df['i3'] = np.round(df.phi3_deg / (360 / N)).astype(int) % N
    assert len(df) == 361 and df[['i2', 'i3']].drop_duplicates().shape[0] == 361
    tab = {(r.i2, r.i3): r for r in df.itertuples()}
    orb = orbits()
    sizes = pd.Series([len(o) for o in orb]).value_counts().to_dict()
    print(f'Gruppe geschlossen (6 Elemente). Bahnen: {len(orb)}; Bahngrößen: {sizes}')

    obs = {'F_skew': [1e-4, 1e-3, 1e-2, 0.1],
           'liftoff': [0.01, 0.1, 0.5, 1.0],
           'F_min': [1e-4, 1e-3, 1e-2, 0.1],
           'F_mean': [1e-5, 1e-4, 1e-3],
           'F_max': [1e-3, 1e-2, 0.1, 1.0]}
    res = {}
    lines = []
    for q, tols in obs.items():
        for tol in tols:
            row = {}
            for gname in ['(23)', '(12)', '(13)', 'alle']:
                viol_pts = set()
                for (i, j), r in tab.items():
                    gl = [gname] if gname != 'alle' else ['(23)', '(12)', '(13)', '(123)', '(132)']
                    for g in gl:
                        i2, j2 = G[g](i, j)
                        if abs(getattr(r, q) - getattr(tab[(i2, j2)], q)) > tol:
                            viol_pts.add((i, j))
                row[gname] = len(viol_pts)
            # Bahnen mit Spannweite > tol
            n_orb = sum(1 for o in orb if (max(getattr(tab[p], q) for p in o) - min(getattr(tab[p], q) for p in o)) > tol)
            row['Bahnen'] = n_orb
            res[f'{q}|{tol:g}'] = row
            lines.append(f'{q:8s} tol={tol:<7g} verletzte Punkte: (23) {row["(23)"]:3d}  (12) {row["(12)"]:3d}  '
                         f'(13) {row["(13)"]:3d}  volle Gruppe {row["alle"]:3d}   verletzte Bahnen {n_orb:2d}/{len(orb)}')
    print('\n'.join(lines))

    # P1-Kriterium nachstellen: nur (12), beliebige Observable – welche Toleranz liefert 30?
    def count12(q, tol):
        return sum(1 for (i, j), r in tab.items() if abs(getattr(r, q) - getattr(tab[G['(12)'](i, j)], q)) > tol)
    p1 = {q: {f'{t:g}': count12(q, t) for t in [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 0.05, 0.1, 0.5, 1]}
          for q in ['F_skew', 'liftoff', 'F_min', 'F_max', 'F_mean', 'peak_ratio']}
    print('\nNur Generator (12) [P1-Prüfung], Anzahl Punkte mit |Δ| > tol:')
    for q, d in p1.items():
        print(f'  {q:10s} ' + '  '.join(f'{t}:{n}' for t, n in d.items()))

    # Bahnweise Tabelle: Spannweiten
    rows = []
    for k, o in enumerate(orb):
        vals = {q: [getattr(tab[p], q) for p in o] for q in ['F_skew', 'liftoff', 'F_min', 'F_max', 'F_mean']}
        rows.append(dict(bahn=k, groesse=len(o), punkte=' '.join(f'({a},{b})' for a, b in o),
                         lam_min=min(vals['liftoff']), lam_max=max(vals['liftoff']),
                         d_lam=max(vals['liftoff']) - min(vals['liftoff']),
                         d_skew=max(vals['F_skew']) - min(vals['F_skew']),
                         d_Fmin=max(vals['F_min']) - min(vals['F_min']),
                         d_Fmax=max(vals['F_max']) - min(vals['F_max']),
                         d_Fmean=max(vals['F_mean']) - min(vals['F_mean'])))
    bt = pd.DataFrame(rows).sort_values('d_lam', ascending=False)
    bt.to_csv(OUT + 'sym_bahnen_19x19.csv', index=False, float_format='%.6g')
    print('\nBahnen nach Spannweite in lambda (Top 20):')
    with pd.option_context('display.width', 250, 'display.max_colwidth', 80):
        print(bt.head(20).to_string(index=False))

    # (23)-Paare mit Differenz: rein numerisch (Rundung), da ODE und Start identisch
    d23 = []
    for (i, j), r in tab.items():
        if i < j:
            s = tab[(j, i)]
            d23.append(dict(i2=i, i3=j, d_lam=r.liftoff - s.liftoff, d_skew=r.F_skew - s.F_skew,
                            d_Fmean=r.F_mean - s.F_mean, d_Fmax=r.F_max - s.F_max, lam=r.liftoff))
    d23 = pd.DataFrame(d23)
    nz = d23[(d23[['d_lam', 'd_skew', 'd_Fmean', 'd_Fmax']].abs() > 0).any(axis=1)]
    print(f'\n(23)-Paare (171): mit irgendeiner Differenz > 0 bei CSV-Auflösung: {len(nz)}; '
          f'max |dF_mean| = {d23.d_Fmean.abs().max():.6f} N, max |d_lam| = {d23.d_lam.abs().max():.4f} %, '
          f'max |d_skew| = {d23.d_skew.abs().max():.6f}; Mittel dF_mean = {d23.d_Fmean.mean():.2e}')
    print('  Liftoff-Anteil der (23)-Paare mit Differenz: min', nz.lam.min() if len(nz) else None)
    json.dump(dict(bahnen=len(orb), bahngroessen={str(k): v for k, v in sizes.items()}, zaehlung=res, p1_12=p1,
                   n23_diff=int(len(nz))),
              open(OUT + 'sym_count_19x19.json', 'w'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
