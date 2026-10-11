"""
n1_geometrie.py – Befunde NR-01 bis NR-03: Was sechs Nadeln geometrisch leisten können.

1. Rang, Nullraum (Vorspannzustände) und Kondition der Belegungen A, B, B2, Bg, C.
2. Paarstruktur: Differenz und Summe gegenüberliegender Nadeln bei zentraler (A) und versetzter (B) Belegung;
   blinde Lastrichtungen von A und Bg.
3. Statische Nadellasten der statisch bestimmten Belegung B unter dem Gewicht (Schwerpunktlagen als Beispiele).
4. Formschluss mit einseitigen, reibungsfreien Druckspitzen: sechs Nadeln nie, sieben bei passender Lage,
   zwölf (zwei je Fläche) im Beispiel; Zufallsstichprobe als Veranschaulichung des Satzes.
5. Rang-Nullraum-Bilanz der drei Ausführungen mit sechs Nadeln.

Alle Lagen sind Rechenbeispiele (D = 0,15 m Abstand der Fixierstellen von O, A = 0,04 m Versatz).
Laufzeit wenige Sekunden; schreibt keine Dateien.
"""
import numpy as np
from nr_modell import (NAMEN, KOMP, AUSSEN, ACHSE, D_REF, A_REF, EX, EY, EZ, rahmen, nadel, Rahmen, formschluss,
                       Koerper)

np.set_printoptions(precision=4, suppress=True, linewidth=150)


def vek(v, p=3):
    return '(' + ', '.join(f'{round(float(x), p) + 0.0:+.{p}f}' for x in v) + ')'


def kopf(text):
    print('\n' + '=' * 100 + '\n' + text + '\n' + '=' * 100)


# ───────────────────────────── 1. Rang, Nullraum, Kondition ─────────────────────────────
kopf('1. Belegungen mit je einer Nadel pro Fläche: Rang, Nullraum, Kondition ([F; M/l_ref])')
print('Belegung  Art je Nadel          gem. Komp.  Rang  Nullraum  Kond. l=A   Kond. l=D')
beschr = {'A': 'axial, zentral', 'B': 'axial, versetzt zykl.', 'B2': 'axial, versetzt zykl. 2',
          'Bg': 'axial, gleichseitig', 'C': '3 Kraftkomp., zentral'}
for v in ('A', 'B', 'B2', 'Bg', 'C'):
    R = rahmen(v, k_t=2e4)
    r, nul, kA, _ = R.rang(A_REF)
    _, _, kD, _ = R.rang(D_REF)
    print(f'{v:8s}  {beschr[v]:22s}  {R.gem.sum():6d}      {r:3d}  {nul:6d}    {kA:9.3f}   {kD:9.3f}')

# ───────────────────────────── 2. Paarstruktur ─────────────────────────────
kopf('2. Paarstruktur: Differenz = Kraft; Summe = Vorspannung (zentral) bzw. Moment (versetzt)')
RB, RA = rahmen('B'), rahmen('A')
print('Spalten von G der Belegung B (Dyname einer Druckkraft von 1 N, Momente in N·m):')
print('Nadel   Fixierstelle r [m]        Druckrichtung n   ' + '  '.join(f'{c:>7s}' for c in KOMP))
for j, nd in enumerate(RB.nadeln):
    print(f"{nd['name']:6s}  {vek(nd['r']):24s}  {vek(nd['n'], 0):16s}  "
          + '  '.join(f'{x + 0.0:7.3f}' for x in RB.G[:, j]))
Ginv = np.linalg.inv(RB.G)
print('\nB: Nadelkräfte aus der Dyname, q = G⁻¹·w (Zeilen: Nadeln; Spalten: Beitrag je Komponente):')
print('Nadel   ' + '  '.join(f'{c:>8s}' for c in KOMP))
for j, nd in enumerate(RB.nadeln):
    print(f"{nd['name']:6s}  " + '  '.join(f'{x + 0.0:8.3f}' for x in Ginv[j]))
pruef = dict(
    Fx=RB.G[0] - (np.isin(NAMEN, ['West']) * 1.0 - np.isin(NAMEN, ['Ost']) * 1.0),
    Fy=RB.G[1] - (np.isin(NAMEN, ['Süd']) * 1.0 - np.isin(NAMEN, ['Nord']) * 1.0),
    Fz=RB.G[2] - (np.isin(NAMEN, ['unten']) * 1.0 - np.isin(NAMEN, ['oben']) * 1.0),
    Mx=RB.G[3] - A_REF * np.isin(NAMEN, ['Nord', 'Süd']),
    My=RB.G[4] - A_REF * np.isin(NAMEN, ['oben', 'unten']),
    Mz=RB.G[5] - A_REF * np.isin(NAMEN, ['Ost', 'West']))
print('\nB, geschlossen: Fx = q_West − q_Ost, Fy = q_Süd − q_Nord, Fz = q_unten − q_oben,')
print('               Mx = A·(q_Nord + q_Süd), My = A·(q_oben + q_unten), Mz = A·(q_Ost + q_West)')
print(f'   max. Abweichung von G: {max(np.abs(v).max() for v in pruef.values()):.1e}')
print('\nA (zentral): Nullraum von G = Vorspannzustände (je Paar gleicher Druck):')
N_A = RA.nullraum()
N_A = N_A @ np.linalg.inv(N_A[[0, 2, 4]])      # auf Nord, Ost, oben normiert
for i in range(N_A.shape[1]):
    print('   ' + '  '.join(f'{nm}={round(float(x), 3) + 0.0:+.3f}' for nm, x in zip(NAMEN, N_A[:, i])))
print('A: blinde Lastrichtungen (Linksnullraum, skaliert [F; M/A]):')
for b in RA.blind(A_REF).T:
    print('   ' + '  '.join(f'{c}={round(float(x), 3) + 0.0:+.3f}' for c, x in zip(KOMP, b)))
print('Bg (gleichseitig versetzt): blinde Lastrichtungen:')
for b in rahmen('Bg').blind(A_REF).T:
    print('   ' + '  '.join(f'{c}={round(float(x), 3) + 0.0:+.3f}' for c, x in zip(KOMP, b)))

# ───────────────────────────── 3. Statik B ─────────────────────────────
kopf('3. Statisch bestimmte Belegung B: Nadellasten unter dem Gewicht (V1-Kandidat, M = 0,65 kg)')
print('Schwerpunkt r_cm [mm]          ' + '  '.join(f'{nm:>7s}' for nm in NAMEN) + '   (N, + Druck, − Zug)')
k0 = Koerper()
fak = k0.M / k0.m0                               # Trägerschwerpunkt so legen, dass r_cm den Beispielwert hat
for r_cm in ((0.0, 0.0, 0.0), (-A_REF, 0.0, 0.0), (0.0, 0.01, 0.0)):
    kp = Koerper(r0=fak * np.asarray(r_cm))
    q = np.linalg.solve(RB.G, kp.basis())
    print(f'{vek(kp.r_cm * 1e3, 1):30s} ' + '  '.join(f'{x + 0.0:7.3f}' for x in q))
print('Gewicht in O: oben trägt Mg/2 Zug, unten Mg/2 Druck (das Moment My = 0 verlangt q_oben = −q_unten).')
print('Schwerpunkt auf der Wirkungslinie der unteren Nadel (x_cm = −A): oben lastfrei.')

# ───────────────────────────── 4. Formschluss ─────────────────────────────
kopf('4. Formschluss mit einseitigen, reibungsfreien Druckspitzen (jede Nadel kann nur drücken)')
print('Satz: Spalten W positiv aufspannend ⇔ Rang 6 und ∃ λ > 0 mit W·λ = 0. Sechs Vektoren können den R⁶ nicht')
print('positiv aufspannen: Wären sie aufspannend, wären sie eine Basis; −Σ G_j = Σ c_j G_j mit c_j ≥ 0 gäbe')
print('Σ (1 + c_j) G_j = 0 mit positiven Gewichten, also lineare Abhängigkeit – Widerspruch. Mindestens sieben.')
print('\nBeispiel                              Nadeln  Rang  Formschluss  t* (max. min λ bei Σλ = 1)')
for name, R in (('A zentral', RA), ('B versetzt zyklisch', RB), ('Bg gleichseitig', rahmen('Bg'))):
    ok, t, r, _ = formschluss(R.Gm)
    print(f'{name:36s}  {R.Gm.shape[1]:6d}  {r:4d}  {str(ok):11s}  {t:+.4f}')
# zwölf Druckspitzen: zwei je Fläche, versetzt um ±A entlang der zyklisch nächsten Achse
n12 = []
for nm in NAMEN:
    quer = np.eye(3)[(ACHSE[nm] + 1) % 3]
    n12 += [nadel(nm, +A_REF * quer), nadel(nm, -A_REF * quer)]
R12 = Rahmen(n12, 'D12')
ok, t, r, lam = formschluss(R12.Gm)
print(f'{"D12 zwei je Fläche (±A)":36s}  {12:6d}  {r:4d}  {str(ok):11s}  {t:+.4f}')
# sieben Druckspitzen: die sechs Nadeln der Festhaltung (versetzt) und eine zweite Nadel unten
d = h = e = 0.05
n7 = [nadel('Nord', r=(d, D_REF, h)), nadel('Süd', r=(-d, -D_REF, -h)), nadel('Ost', r=(D_REF, d, 0.0)),
      nadel('West', r=(-D_REF, -d, 0.0)), nadel('oben', r=(0.0, e, D_REF)), nadel('unten', r=(e, 0.0, -D_REF)),
      nadel('unten', r=(-e, 0.0, -D_REF))]
R7 = Rahmen(n7, 'D7')
ok7, t7, r7, lam7 = formschluss(R7.Gm)
print(f'{"D7 sechs + zweite Nadel unten":36s}  {7:6d}  {r7:4d}  {str(ok7):11s}  {t7:+.4f}')
print('   Lagen D7 [m]: ' + '; '.join(f"{nd['name']} {vek(nd['r'], 2)}" for nd in n7))
v7 = R7.nullraum()[:, 0]
v7 = v7 / v7[0]
print('   Nullraum D7 (einziger Vorspannzustand, auf Nord = 1 normiert): '
      + '  '.join(f'{x:.3f}' for x in v7) + f'   (Rang {R7.rang(D_REF)[0]}, Nullraum {R7.rang(D_REF)[1]})')

rng = np.random.default_rng(11)
treffer6 = treffer7 = rang6 = rang7 = 0
N_ZUFALL = 2000
for _ in range(N_ZUFALL):
    nd6 = []
    for nm in NAMEN:
        a = ACHSE[nm]
        p = rng.uniform(-0.8 * D_REF, 0.8 * D_REF, 3)
        p[a] = D_REF * AUSSEN[nm][a]
        nd6.append(nadel(nm, r=p))
    ok, _, r, _ = formschluss(Rahmen(nd6).Gm)
    treffer6 += ok
    rang6 += r == 6
    nm = NAMEN[rng.integers(6)]
    p = rng.uniform(-0.8 * D_REF, 0.8 * D_REF, 3)
    p[ACHSE[nm]] = D_REF * AUSSEN[nm][ACHSE[nm]]
    ok, _, r, _ = formschluss(Rahmen(nd6 + [nadel(nm, r=p)]).Gm)
    treffer7 += ok
    rang7 += r == 6
print(f'\nZufallsstichprobe ({N_ZUFALL} Lagen, je eine Nadel pro Fläche, Normalen achsparallel, Lage auf der Fläche '
      f'gleichverteilt in ±0,8·D):')
print(f'   sechs Nadeln:  Rang 6 in {rang6}/{N_ZUFALL}, Formschluss in {treffer6}/{N_ZUFALL}')
print(f'   sieben Nadeln (zusätzlich eine auf zufälliger Fläche): Rang 6 in {rang7}/{N_ZUFALL}, '
      f'Formschluss in {treffer7}/{N_ZUFALL}')

# ───────────────────────────── 5. Rang-Nullraum-Bilanz ─────────────────────────────
kopf('5. Rang-Nullraum-Bilanz: übertragene Komponenten = Rang + Nullraum')
print('Ausführung (sechs Nadeln)                     Komp.  Rang  Nullraum  Vorspannung  Momente  Einzelnadel-Nulltest')
zeilen = (('A  axial, zentral', rahmen('A')), ('B  axial, versetzt (zyklisch)', RB),
          ('C  drei Kraftkomponenten, zentral', rahmen('C', k_t=2e4)))
for name, R in zeilen:
    r, nul, _, _ = R.rang(D_REF)
    print(f'{name:44s}  {R.G.shape[1]:5d}  {r:4d}  {nul:8d}  {"möglich" if nul else "unmöglich":11s}  '
          f'{"ja" if r == 6 else "nein":7s}  {"ja" if (r == 6 and nul == 0) else "nein"}')
print('A: Momente nicht gemessen und von den Nadeln nicht gehalten (Mechanismus in drei Drehrichtungen).')
print('B: statisch bestimmt; Nadeln müssen Zug und Druck tragen (Fixierstelle und Schnittstelle zugfest).')
print('C: statisch unbestimmt; Vorspannung (Einspannen) möglich, Nulltest nur für die sechs Resultierenden.')
