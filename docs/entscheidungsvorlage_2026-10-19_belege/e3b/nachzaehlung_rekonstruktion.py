# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 4.2 (Modellnachzählung) und 8.
# Zweck: Rekonstruktion der E3b-Nachzählung der 570 gespeicherten Prüfgrößen (e3b_nachzaehlung.out in diesem
#   Ordner, Originalausgabe vom 18.10.2026); das Originalskript ist überschrieben und verloren (README).
# Eingaben: Argument 1 = docs/e3b_g4_diagnose_2026-10-17/e3_pruefgroessen.csv. Liest nur, schreibt auf stdout.
# Annahmen: ŝ aus der isotropen Umkehrung von u (Σ̂ ist nicht gespeichert), m = 43.
# Seed: keiner (deterministisch). Laufzeit: gemessen 1 s Wandzeit, 1 s CPU (ein Prozess, ein Thread, 20.10.2026).
# Aufruf (Repository-Wurzel als Arbeitsverzeichnis): python3 -I -B
#   docs/entscheidungsvorlage_2026-10-19_belege/e3b/nachzaehlung_rekonstruktion.py
#   docs/e3b_g4_diagnose_2026-10-17/e3_pruefgroessen.csv > docs/entscheidungsvorlage_2026-10-19_belege/e3b/nachzaehlung_rekonstruktion.out
# Herkunft: Nachprüfung 5. Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""Nachleseauftrag 5: Rekonstruktion der Tabelle in agenda/e3b_nachzaehlung.out (c-e3, Befund 10), deren
erzeugendes Skript überschrieben ist. Eigene Neufassung nach der Kopfzeile der .out-Datei:
  ŝ je Kampagne aus (q_Z, u_q_Z) über u = ŝ·SD(Rice(q_Z/ŝ)) invertiert (isotrop), m = 43;
  heutig: q − z_B·u > q_tol / q + 1,645·u ≤ q_tol mit z_B und m aus der Datei;
  R1: Rice mit eingesetztem ŝ (ohne n/(n−1), ohne κ): Rice.sf(q/ŝ; q_tol/ŝ) ≤ α/m;
  R2(ν): ŝ_k = ŝ·√(n/(n−1)), n = ν+1, κ = t(1−α/m; ν)/z(1−α/m), Rice.sf(q/(κŝ_k); q_tol/(κŝ_k)) ≤ α/m;
  MP-unauff.: Rice.cdf(q/ŝ; q_tol/ŝ) ≤ 0,05 (s als bekannt behandelt);
  E3a a/u/b aus e3a_max_unter_grad > 0,1 bzw. e3a_max_ober_grad ≤ 0,1.
Zusätzlich (neu, nicht in der .out): R2 mit ν = 19 (Regel der Vorlage bei n₀ = 20) und O1(ν) „unauffällig“
q + t(0,95; ν)·ŝ_k ≤ q_tol. Liest nur die CSV; schreibt nur auf stdout."""
import collections
import csv
import sys

import numpy as np
from scipy import optimize, stats

QTOL = 5.8e-4
M = 43
A1 = 0.05 / M
ZB = stats.norm.isf(A1)


def s_aus_u(q, u):
    f = lambda s: s * stats.rice.std(q / s) - u  # noqa: E731
    lo, hi = u * 0.999, u / 0.6551
    if f(lo) * f(hi) > 0:
        return None
    return optimize.brentq(f, lo, hi, xtol=1e-16, rtol=1e-13)


def r2(q, s, nu):
    sk = s * np.sqrt((nu + 1) / nu)
    kap = stats.t.isf(A1, nu) / ZB
    c = kap * sk
    return stats.rice.sf(q / c, QTOL / c) <= A1


def o1(q, s, nu):
    sk = s * np.sqrt((nu + 1) / nu)
    return q + stats.t.isf(0.05, nu) * sk <= QTOL


rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8')))
Z = collections.OrderedDict()
for r in rows:
    p = r['punkt']
    z = Z.setdefault(p, collections.Counter())
    z['n'] += 1
    z.setdefault('s', [])
    eo, eu = float(r['e3a_max_ober_grad']), float(r['e3a_max_unter_grad'])
    z['e3a_' + ('a' if eu > 0.1 else ('u' if eo <= 0.1 else 'b'))] += 1
    q, u, zb = float(r['q_Z']), float(r['u_q_Z']), float(r['z_B'])
    z['h_' + ('a' if q - zb * u > QTOL else ('u' if q + 1.645 * u <= QTOL else 'b'))] += 1
    s = s_aus_u(q, u)
    if s is None:
        z['s_nicht'] += 1
        continue
    z['s'].append(s)
    z['R1'] += int(stats.rice.sf(q / s, QTOL / s) <= A1)
    for nu in (40, 21, 19):
        z[f'R2_{nu}'] += int(r2(q, s, nu))
        z[f'O1_{nu}'] += int(o1(q, s, nu))
    z['MP'] += int(stats.rice.cdf(q / s, QTOL / s) <= 0.05)

print('Punkt                 n   ŝ med [1e-4]  t=q_tol/ŝ  | heutig a/u/b (m aus Daten) | R1 a | R2(ν=40) a | R2(ν=21) a | '
      'MP-unauff. | E3a a/u/b')
for p, z in Z.items():
    s = np.array(z['s'])
    print(f"{p:20s} {z['n']:4d}   {np.median(s) * 1e4:6.3f}      {np.median(QTOL / s):6.2f}    | {z['h_a']:3d}/{z['h_u']:3d}/{z['h_b']:3d}"
          f"                |{z['R1']:4d}  |{z['R2_40']:4d}        |{z['R2_21']:4d}        |{z['MP']:4d}        | "
          f"{z['e3a_a']}/{z['e3a_u']}/{z['e3a_b']}")
print('\nZusatz (nicht in der .out): Regel B der Vorlage mit ν = 19 (n₀ = 20) und O1 „unauffällig“')
print('Punkt                 R2(ν=19) a | O1(ν=40) u | O1(ν=21) u | O1(ν=19) u | ŝ nicht bestimmbar')
for p, z in Z.items():
    print(f"{p:20s}  {z['R2_19']:4d}       | {z['O1_40']:4d}       | {z['O1_21']:4d}       | {z['O1_19']:4d}       | {z['s_nicht']}")
