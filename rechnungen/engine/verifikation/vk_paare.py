"""Gegenprüfung ENG-07/ENG-08: Symmetriegruppe (eigene Herleitung, numerisch geprüft) und verletzte Paare
mit dem halbanalytischen Löser SA (kein RK4, kein DOP853).

Modus 'gruppe'          : Gruppenwirkung + Zeitverschiebung prüfen (abar_B(t) = abar_A(t+s)), Bahnzählung.
Modus 'lauf i0 i1'      : Mitglieder i0..i1-1 der Liste, Starts std und imp, 60 s SA; Statistik 40–60 s.
Modus 'shift'           : B äquivalent zu A gestartet (t0 = -s) – muss A reproduzieren.
Modus 'floquet NAME START P' : Newton/Floquet ab Endzustand des Laufs NAME/START mit Periode P.
"""
import sys, json, os, itertools
import numpy as np
import vk_model as m
import vk_sa as sa

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
N = 19
D = 360.0 / N
PAIRS = {'P6': ((0, 6), (13, 13)), 'P13': ((6, 6), (13, 0)), 'P49': ((3, 7), (16, 4)),
         'P45': ((12, 17), (14, 2)), 'P11': ((0, 11), (8, 8)), 'P33': ((1, 16), (3, 4))}


def elements(p2, p3):
    """Eigene Herleitung: Phasen {0, p2, p3}; neue Referenz j, Reihenfolge der übrigen zwei.
    Rückgabe Liste (name, (q2, q3), s) mit abar_B(t) = abar_A(t + s), s = tau_j."""
    ph = [0.0, p2, p3]
    out = []
    for j in range(3):
        rest = [k for k in range(3) if k != j]
        for order in (rest, rest[::-1]):
            q = tuple(((ph[k] - ph[j]) % 360.0) for k in order)
            out.append((f'ref{j+1}_{order[0]+1}{order[1]+1}', q, float(m.tau_of(ph[j]))))
    return out


def abar(t, p2, p3):
    taus = (0.0, float(m.tau_of(p2)), float(m.tau_of(p3)))
    return sum(m.e_acc(t - tk) for tk in taus) / 3.0


def mode_gruppe():
    L = []
    rng = np.random.default_rng(1)
    t = rng.uniform(0, 1, 2000)
    worst = 0.0
    for _ in range(200):
        p2, p3 = rng.uniform(0, 360, 2)
        for nm, (q2, q3), s in elements(p2, p3):
            worst = max(worst, float(np.max(np.abs(abar(t, q2, q3) - abar(t + s, p2, p3)))))
    L.append(f'abar_B(t) - abar_A(t+s) über 200 Zufallskonfigurationen x 6 Elemente: max {worst:.1e} m/s^2')
    # Gitter: Bahnen
    def img(i, j):
        res = set()
        for nm, (q2, q3), s in elements(i * D, j * D):
            res.add((int(round(q2 / D)) % N, int(round(q3 / D)) % N))
        return res
    seen, orbs = set(), []
    for i in range(N):
        for j in range(N):
            if (i, j) not in seen:
                o = img(i, j)
                seen |= o
                orbs.append(sorted(o))
    sizes = {}
    for o in orbs:
        sizes[len(o)] = sizes.get(len(o), 0) + 1
    L.append(f'19er-Raster: {len(orbs)} Bahnen, Größen {sizes}')
    for nm, (A, B) in PAIRS.items():
        ok = tuple(B) in img(*A)
        L.append(f'  Paar {nm}: {A} -> {B} in derselben Bahn: {ok}')
    # Spiegelung phi -> -phi als Kontrolle: keine Symmetrie (abar(t) -> abar(-t) nur mit Zeitumkehr)
    txt = '\n'.join(L)
    print(txt)
    open(OUT + 'vk_gruppe_ausgabe.txt', 'w').write(txt + '\n')
    json.dump([o for o in orbs], open(OUT + 'vk_bahnen.json', 'w'))


def members():
    lst = []
    for nm, (A, B) in PAIRS.items():
        lst.append((nm + 'A', A)); lst.append((nm + 'B', B))
    return lst


def mode_lauf(i0, i1, n_cyc=600):
    res = {}
    fn = OUT + f'vk_paare_lauf_{i0}_{i1}.json'
    for name, (i, j) in members()[i0:i1]:
        p2, p3 = i * D, j * D
        s = sa.SA(p2, p3)
        for st_name in ('std', 'imp'):
            v0 = 0.0 if st_name == 'std' else -float(m.ebar_v(0.0, s.taus))
            R = s.run(-m.MG / m.K, v0, 0.0, n_cyc)
            st = sa.stats(R, 400, 600)
            st1 = sa.stats(R, 50, 150)
            per = sa.period(R, n_last=60, tol_v=1e-8, tol_z=1e-10)
            lam_blocks = [sa.stats(R, c, c + 50)['lam'] for c in range(100, 600, 50)]
            res[f'{name}_{st_name}'] = dict(phi=(p2, p3), lam_5_15=st1['lam'], lam=st['lam'], skew=st['skew'],
                                            Fmax=st['Fmax'], period=per[0], tset=per[1], lam_blocks=lam_blocks,
                                            x_end=[float(R['PZ'][-1]), float(R['PV'][-1])])
            print(f'{name} {st_name} ({p2:.3f},{p3:.3f}): lam 5–15 s {st1["lam"]:.3f}, 40–60 s {st["lam"]:.4f} %, gamma1 {st["skew"]:.4f}, '
                  f'F_max {st["Fmax"]:.2f}, Periode {per[0]} (ab {per[1]:.1f} s), 5-s-Blöcke 10–60 s: '
                  + ' '.join(f'{x:.2f}' for x in lam_blocks), flush=True)
            json.dump(res, open(fn, 'w'), indent=1, default=float)


def mode_shift(n_cyc=300):
    L = []
    res = {}
    for nm, (A, B) in PAIRS.items():
        pA = (A[0] * D, A[1] * D)
        # Element und Verschiebung suchen, das A auf B abbildet
        for en, (q2, q3), s in elements(*pA):
            if (int(round(q2 / D)) % N, int(round(q3 / D)) % N) == tuple(B):
                break
        sA = sa.SA(*pA)
        sB = sa.SA(q2, q3)          # B mit exakt abgebildeten Phasen
        RA = sA.run(-m.MG / m.K, 0.0, 0.0, n_cyc)
        RB = sB.run(-m.MG / m.K, 0.0, -s, n_cyc)     # B-Zeit t' = t - s
        stA, stB = sa.stats(RA, 200, 300), sa.stats(RB, 200, 300)
        dmax = float(np.max(np.abs(RA['PV'] - RB['PV'])))
        dfirst = float(np.max(np.abs(RA['PV'][:50] - RB['PV'][:50])))
        L.append(f'{nm}: A{A} std vs. B{B} mit t0 = -{s:.6f} s ({en}): lam A {stA["lam"]:.4f}, B {stB["lam"]:.4f} %; '
                 f'max|dz\'| Zyklen 0–50 {dfirst:.1e}, 0–300 {dmax:.1e} m/s')
        res[nm] = dict(lamA=stA['lam'], lamB=stB['lam'], d50=dfirst, d300=dmax, element=en, s=s)
        print(L[-1], flush=True)
    open(OUT + 'vk_paare_shift_ausgabe.txt', 'w').write('\n'.join(L) + '\n')
    json.dump(res, open(OUT + 'vk_paare_shift.json', 'w'), indent=1)


def mode_floquet(spec):
    """spec: Liste 'NAME_START:P' – Endzustände aus vk_paare_lauf_*.json."""
    allr = {}
    for f in os.listdir(OUT):
        if f.startswith('vk_paare_lauf_') and f.endswith('.json'):
            allr.update(json.load(open(OUT + f)))
    L = []
    for item in spec:
        key, p = item.split(':'); p = int(p)
        r = allr[key]
        s = sa.SA(*r['phi'])
        x, mu, rr = sa.floquet(s, r['x_end'], 60.0, p=p)
        R = s.run(x[0], x[1], 0.0, 3 * p)
        st = sa.stats(R, 0, 3 * p)
        L.append(f'{key} P{p}: |mu| = {", ".join(f"{abs(v):.4f}" for v in mu)}; Residuen {rr[0]:.0e} -> {rr[-1]:.0e}; '
                 f'Orbit lam {st["lam"]:.4f} %, gamma1 {st["skew"]:.4f}, F_max {st["Fmax"]:.2f} N')
        print(L[-1], flush=True)
    open(OUT + f'vk_paare_floquet_{spec[0].split(":")[0]}_ausgabe.txt', 'w').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    md = sys.argv[1]
    if md == 'gruppe':
        mode_gruppe()
    elif md == 'lauf':
        mode_lauf(int(sys.argv[2]), int(sys.argv[3]))
    elif md == 'shift':
        mode_shift()
    elif md == 'floquet':
        mode_floquet(sys.argv[2:])
