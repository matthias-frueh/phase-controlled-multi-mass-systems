"""
v2_bilanz_rang.py – Gegenprüfung NR-01, NR-02, NR-03 und NR-05 mit eigenem Rechenweg.

Teil A  Basislinie und Randterm im Zeitbereich: Nadelkräfte der Belegung B im starren Grenzfall aus der exakten
        Impuls- und Drallbilanz (Modulbahnen direkt aus der Egg-Formel, Geschwindigkeiten durch Quadratur), mit
        Schwerpunktversatz und anderer Modullage (G60h auf R = 50 mm, Module 20 mm über O). Mittel über ganze
        Perioden gegen (M g e_z; r_cm × M g e_z); Fenster mit Bruchteilen einer Periode gegen den Randterm
        (P(t₁) − P(t₀))/T_W bzw. (H_O(t₁) − H_O(t₀))/T_W; Einzelnadel-Mittel zwischen Phasenlagen.
Teil B  Rang und Nullraum exakt in rationaler Arithmetik (Koordinaten in mm): Belegungen A, B, B2, Bg, C, D7, D12.
Teil C  Formschluss ohne lineares Programm: über den exakten Nullraum (D7) bzw. einen exakten positiven
        Nullraumvektor (D12); sechs Nadeln: Rang 6 ⇒ Nullraum {0} ⇒ kein Formschluss.

Importiert nr_modell nur für den Rangvergleich (Teil B). Laufzeit wenige Sekunden; schreibt keine Dateien.
"""
import os
import sys
from fractions import Fraction

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import nr_modell as ziel            # noqa: E402  (nur Vergleichsziel für Teil B)

g0, f, hub, thold = 9.81, 10.0, 8e-3, 0.65
T = 1.0 / f


def kopf(text):
    print('\n' + '=' * 100 + '\n' + text + '\n' + '=' * 100)


# ───────────────────────────── Teil A ─────────────────────────────
kopf('Teil A – Basislinie, Randterm und Einzelnadel-Mittel im Zeitbereich (Belegung B, starr)')
m_mod = np.array([0.1, 0.1, 0.1])
m0, r0 = 0.35, np.array([0.012, -0.020, 0.030])
psi = np.radians([60.0, 180.0, 300.0])
R_mod = np.c_[0.05 * np.cos(psi), 0.05 * np.sin(psi), np.full(3, 0.02)]
M = m0 + m_mod.sum()
r_cm = (m0 * r0 + m_mod @ R_mod) / M
NADELN = [((0.0, 0.15, 0.04), (0, -1, 0)), ((0.0, -0.15, -0.04), (0, 1, 0)), ((0.15, 0.04, 0.0), (-1, 0, 0)),
          ((-0.15, -0.04, 0.0), (1, 0, 0)), ((0.04, 0.0, 0.15), (0, 0, -1)), ((-0.04, 0.0, -0.15), (0, 0, 1))]
Gm = np.array([np.r_[n, np.cross(r, n)] for r, n in NADELN], float).T

N = 200_000                                       # Stützstellen je Periode
t = np.arange(10 * N + 1) * (T / N)               # zehn Perioden, Randpunkte eingeschlossen


def a_rel(t, phi_deg):
    s = np.mod(f * t - phi_deg / 360.0, 1.0)
    tf = 1.0 - thold
    return hub * f ** 2 * np.where(s < thold, -np.pi ** 2 / thold * np.sin(np.pi * s / thold),
                                   np.pi ** 2 / tf * np.sin(np.pi * (s - thold) / tf))


def v_rel(t, a):
    """Geschwindigkeit durch Trapez-Quadratur, Konstante so, dass das Periodenmittel null ist (beschränkte Bahn)."""
    v = np.concatenate(([0.0], np.cumsum(0.5 * (a[1:] + a[:-1]) * np.diff(t))))
    return v - v[:N].mean()


ez = np.array([0.0, 0.0, 1.0])
basis = np.r_[M * g0 * ez, np.cross(r_cm, M * g0 * ez)]
print(f'M = {M:.3f} kg, r_cm = {np.round(r_cm * 1e3, 3).tolist()} mm, Basislinie = '
      + '  '.join(f'{x + 0.0:+.6f}' for x in basis))
mittel = {}
for name, phis in (('T', (0.0, 120.0, 240.0)), ('Z', (0.0, 110.0, 240.0)), ('S', (0.0, 0.0, 0.0))):
    a = np.array([a_rel(t, p) for p in phis])                       # (3, n)
    v = np.array([v_rel(t, ai) for ai in a])
    # Impuls- und Drallsatz für den gehaltenen Körper (Träger ruht): w_Nadeln = −w_g + d/dt (P; H_O)
    F = (m_mod @ a)[None, :] * ez[:, None] + M * g0 * ez[:, None]
    mom = np.einsum('i,ic,in->cn', m_mod, np.cross(R_mod, ez), a)   # Σ m_i (R_i + s_i e_z) × s̈_i e_z = Σ m_i R_i × s̈_i e_z
    mom += np.cross(r_cm, M * g0 * ez)[:, None]                      # Gewichtsmoment (s_i e_z × g e_z = 0)
    w = np.vstack((F, mom))
    lam = np.linalg.solve(Gm, w)                                     # Nadelkräfte, statisch bestimmt
    ganze = slice(0, 10 * N)                                         # zehn ganze Perioden (Rechteckregel = periodisch exakt)
    w_mittel = w[:, ganze].mean(axis=1)
    mittel[name] = lam[:, ganze].mean(axis=1)
    # Fenster über 3,37 Perioden: Abweichung gegen den Randterm
    i1 = int(round(3.37 * N))
    T_W = i1 * (T / N)
    P = (m_mod @ v)[None, :] * ez[:, None]
    H = np.einsum('i,ic,in->cn', m_mod, np.cross(R_mod, ez), v)
    rand = np.r_[P[:, i1] - P[:, 0], H[:, i1] - H[:, 0]] / T_W
    abw = 0.5 * (w[:, :i1] + w[:, 1:i1 + 1]).sum(axis=1) * (T / N) / T_W - basis     # Trapezregel wie v_rel
    print(f'{name}: max|⟨w⟩_ganz − Basislinie| = {np.abs(w_mittel - basis).max():.2e};  Fenster 3,37 T: '
          f'Abweichung F_z {abw[2]:+.3e} N, M_x {abw[3]:+.3e}, M_y {abw[4]:+.3e} N·m; '
          f'Randterm F_z {rand[2]:+.3e}, M_x {rand[3]:+.3e}, M_y {rand[4]:+.3e};  '
          f'max|Abw − Randterm| = {np.abs(abw - rand).max():.1e}')
d_TS = np.abs(mittel['T'] - mittel['S']).max()
d_TZ = np.abs(mittel['T'] - mittel['Z']).max()
q_stat = np.linalg.solve(Gm, basis)
print('Einzelnadel-Mittel T [N]: ' + '  '.join(f'{x + 0.0:+.6f}' for x in mittel['T']))
print('statisch bestimmt G⁻¹·Basislinie: ' + '  '.join(f'{x + 0.0:+.6f}' for x in q_stat))
print(f'max|⟨q⟩_T − ⟨q⟩_S| = {d_TS:.1e} N, max|⟨q⟩_T − ⟨q⟩_Z| = {d_TZ:.1e} N, '
      f'max|⟨q⟩_T − G⁻¹·Basis| = {np.abs(mittel["T"] - q_stat).max():.1e} N')
print('Über ganze Perioden ist das Mittel die Basislinie; über ein Teilfenster weicht es genau um die Impuls- bzw.')
print('Drallbilanz des Fensters ab (Randterm, Trapezregel für Mittel und Geschwindigkeit gleich gewählt).')


# ───────────────────────────── Teil B ─────────────────────────────
def rang_exakt(spalten):
    """Rang und Basis des Nullraums in rationaler Arithmetik (Gauß-Jordan)."""
    A = [[Fraction(x) for x in zeile] for zeile in np.array(spalten, dtype=object).T.tolist()]
    zeilen, sp = len(A), len(A[0])
    piv, r = [], 0
    for c in range(sp):
        p = next((i for i in range(r, zeilen) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        A[r] = [x / A[r][c] for x in A[r]]
        for i in range(zeilen):
            if i != r and A[i][c] != 0:
                A[i] = [x - A[i][c] * y for x, y in zip(A[i], A[r])]
        piv.append(c)
        r += 1
        if r == zeilen:
            break
    frei = [c for c in range(sp) if c not in piv]
    basis_n = []
    for fr in frei:
        v = [Fraction(0)] * sp
        v[fr] = Fraction(1)
        for i, c in enumerate(piv):
            v[c] = -A[i][fr]
        basis_n.append(v)
    return r, basis_n


def spalte(r_mm, n):
    r = [Fraction(x) for x in r_mm]
    n = [Fraction(x) for x in n]
    m = [r[1] * n[2] - r[2] * n[1], r[2] * n[0] - r[0] * n[2], r[0] * n[1] - r[1] * n[0]]
    return n + m                                                      # Momente in N·mm


AXEN = {'Nord': (1, +1), 'Süd': (1, -1), 'Ost': (0, +1), 'West': (0, -1), 'oben': (2, +1), 'unten': (2, -1)}


def belegung(variante, D=150, A=40):
    sp = []
    for name, (a, s) in AXEN.items():
        r = [0, 0, 0]
        r[a] = s * D
        n = [0, 0, 0]
        n[a] = -s
        if variante == 'B':
            r[(a + 1) % 3] += s * A
        elif variante == 'B2':
            r[(a + 2) % 3] += s * A
        elif variante == 'Bg':
            r[(a + 1) % 3] += A
        if variante == 'C':
            t1 = [0, 0, 0]
            t1[(a + 1) % 3] = 1
            t2 = [n[1] * t1[2] - n[2] * t1[1], n[2] * t1[0] - n[0] * t1[2], n[0] * t1[1] - n[1] * t1[0]]
            sp += [spalte(r, n), spalte(r, t1), spalte(r, t2)]
        else:
            sp.append(spalte(r, n))
    return sp


kopf('Teil B – Rang und Nullraum exakt (rationale Arithmetik, Koordinaten in mm)')
D7 = [((50, 150, 50), (0, -1, 0)), ((-50, -150, -50), (0, 1, 0)), ((150, 50, 0), (-1, 0, 0)),
      ((-150, -50, 0), (1, 0, 0)), ((0, 50, 150), (0, 0, -1)), ((50, 0, -150), (0, 0, 1)), ((-50, 0, -150), (0, 0, 1))]
D12 = []
for name, (a, s) in AXEN.items():
    for vz in (+1, -1):
        r = [0, 0, 0]
        r[a] = s * 150
        r[(a + 1) % 3] = vz * 40
        n = [0, 0, 0]
        n[a] = -s
        D12.append((tuple(r), tuple(n)))
faelle = {v: belegung(v) for v in ('A', 'B', 'B2', 'Bg', 'C')}
faelle['D7'] = [spalte(r, n) for r, n in D7]
faelle['D12'] = [spalte(r, n) for r, n in D12]
print('Belegung  Spalten  Rang exakt  Nullraum exakt  Rang nr_modell')
ergebnis = {}
for v, sp in faelle.items():
    r, nb = rang_exakt(sp)
    ergebnis[v] = (r, nb)
    if v in ('A', 'B', 'B2', 'Bg', 'C'):
        rz = ziel.rahmen(v, k_t=2e4).rang(ziel.D_REF)[0]
    else:
        rz = '–'
    print(f'{v:8s}  {len(sp):7d}  {r:10d}  {len(nb):14d}  {rz}')

kopf('Teil C – Formschluss mit einseitigen Druckspitzen, exakt')
r7, nb7 = ergebnis['D7']
v7 = [x / nb7[0][0] for x in nb7[0]]
print(f'D7: Rang {r7}, Nullraum 1, Basisvektor (auf Nord = 1): {[str(x) for x in v7]} → alle positiv: '
      f'{all(x > 0 for x in v7)} → Formschluss {r7 == 6 and all(x > 0 for x in v7)}')
r12, _ = ergebnis['D12']
eins = [sum(Fraction(c[i]) for c in faelle['D12']) for i in range(6)]
print(f'D12: Rang {r12}; G·(1, …, 1) = {[str(x) for x in eins]} → positiver Nullraumvektor → '
      f'Formschluss {r12 == 6 and all(x == 0 for x in eins)}')
for v in ('A', 'B', 'B2', 'Bg'):
    r, nb = ergebnis[v]
    print(f'{v}: Rang {r}, Nullraum {len(nb)} → Formschluss nur bei Rang 6 und positivem Nullraumvektor: False')
rC, nbC = ergebnis['C']
vorsp = [Fraction(0)] * 18
for j in range(6):
    vorsp[3 * j] = Fraction(1)                                       # gleiche Druckvorspannung aller axialen Komponenten
GC = faelle['C']
rest = [sum(vorsp[j] * GC[j][i] for j in range(18)) for i in range(6)]
print(f'C: Rang {rC}, Nullraum {len(nbC)}; G·λ_V für 1 N Druck auf allen sechs axialen Komponenten = '
      f'{[str(x) for x in rest]} → Vorspannung im Nullraum: {all(x == 0 for x in rest)}')
