# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 4.2 (Anisotropie und ν).
# Zweck: indirekte Momentenprüfung von Anisotropie, Kalibrierung von ŝ und ν aus den gespeicherten E3b-Größen.
# Eingaben: Argument 1 = docs/e3b_g4_diagnose_2026-10-17/e3_pruefgroessen.csv. Seed: default_rng(55) (Bootstrap
#   über Kampagnen, 2000 Ziehungen). Laufzeit: gemessen 2 s Wandzeit, 2 s CPU (ein Prozess, ein Thread, 20.10.2026).
# Aufruf (Repository-Wurzel): python3 -I -B <dieser Ordner>/indirekt_aniso_nu.py docs/e3b_g4_diagnose_2026-10-17/
#   e3_pruefgroessen.csv > <dieser Ordner>/indirekt_aniso_nu.out
# Herkunft: Nachprüfung 5. Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""Nachleseauftrag 5, Teil (4): Was die gespeicherten E3b-Größen über Anisotropie und Freiheitsgrade verraten.
Gespeichert sind je Kampagne nur q_Z, u_q_Z, u_q_Z_ohne_T (e3_pruefgroessen.csv); keine Replikate, keine 2×2-Kovarianz.
Indirekte Momentenprüfungen an Punkten mit exakter Superposition (wahres D ≈ 0), Annahme: gleiches wahres Σ in allen
Kampagnen eines Punkts (gleicher Generator, nur Seeds verschieden):
  K = mean(q⁴)/mean(q²)²: 2 bei isotropem Σ, (3(1+ρ⁴)+2ρ²)/(1+ρ²)² allgemein (3 für ρ → 0); ein wahres D ≠ 0 senkt K.
  r = mean(q²)/(2·mean(ŝ²)) mit ŝ aus u (isotrope Inversion wie die Nachzählung): ≈ 1 bei kalibriertem ŝ (isotrop).
  CV²(ŝ²) über die Kampagnen: bei isotropem Σ ≈ 1/ν (Spur/2 hat 2ν FG); Streuung des wahren s zwischen
  Kampagnen erhöht CV², so dass ν_iso = 1/CV² eine untere Schätzung ist.
Unsicherheit: Bootstrap über die Kampagnen (2000 Ziehungen, Perzentilintervall 95 %)."""
import csv
import sys

import numpy as np
from scipy import optimize, stats

rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8')))
rng = np.random.default_rng(55)


def s_aus_u(q, u):
    f = lambda s: s * stats.rice.std(q / s) - u  # noqa: E731
    return optimize.brentq(f, u * 0.999, u / 0.6551)


def rho_aus_K(K):
    if K <= 2:
        return 1.0
    if K >= 3:
        return 0.0
    f = lambda r: (3 * (1 + r ** 4) + 2 * r ** 2) / (1 + r ** 2) ** 2 - K  # noqa: E731
    return optimize.brentq(f, 1e-6, 1.0)


print('Punkt                n    K = E q⁴/(E q²)² [95 %]     ρ aus K [95 %]       r = E q²/(2 E ŝ²) [95 %]   '
      'CV²(ŝ²)  ν_iso = 1/CV² [95 %]   u/u_ohne_T max−1')
for p in ('N01-A4/L1', 'N01-A4/L0', 'N01-A4/L2', 'N01-A4/L4', 'N03-N3bindet/L1', 'N03-ungleich/L1', 'E07-verstaerkung/L1'):
    R = [r for r in rows if r['punkt'] == p]
    q = np.array([float(r['q_Z']) for r in R])
    u = np.array([float(r['u_q_Z']) for r in R])
    u0 = np.array([float(r['u_q_Z_ohne_T']) for r in R])
    s = np.array([s_aus_u(a, b) for a, b in zip(q, u)])

    def stat(idx):
        qq, ss = q[idx], s[idx]
        K = np.mean(qq ** 4) / np.mean(qq ** 2) ** 2
        r = np.mean(qq ** 2) / (2 * np.mean(ss ** 2))
        cv2 = np.var(ss ** 2, ddof=1) / np.mean(ss ** 2) ** 2
        return K, r, cv2
    K, r, cv2 = stat(np.arange(q.size))
    bs = np.array([stat(rng.integers(0, q.size, q.size)) for _ in range(2000)])
    lo, hi = np.percentile(bs, [2.5, 97.5], axis=0)
    print(f'{p:20s} {q.size:3d}  {K:5.2f} [{lo[0]:4.2f}; {hi[0]:4.2f}]          {rho_aus_K(K):4.2f} [{rho_aus_K(hi[0]):4.2f}; '
          f'{rho_aus_K(lo[0]):4.2f}]     {r:5.2f} [{lo[1]:4.2f}; {hi[1]:4.2f}]           {cv2:6.4f}   {1 / cv2:6.1f} '
          f'[{1 / hi[2]:5.1f}; {1 / lo[2]:6.1f}]     {np.max(np.abs(u / u0 - 1)):.1e}')
