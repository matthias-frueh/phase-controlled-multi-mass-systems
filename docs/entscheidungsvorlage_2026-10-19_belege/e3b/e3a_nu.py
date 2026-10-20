# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 4.1 und 4.3.
# Zweck: E3a am Rand: heutige Regel (z_B, Plug-in-u) gegen t-Quantil mit ν = n_A − 1 und n/(n−1), Anteil w
#   bekannter Varianz; obere Grenzen.
# Seed: default_rng(20261021); N = 2·10⁶. Laufzeit: einige Sekunden (Einschätzung; Ausgabe übernommen).
# Aufruf: python3 -I -B e3a_nu.py > e3a_nu.out
# Herkunft: Lesebericht zu c) (E3), 18.10.2026. Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""E3a am Rand: t-Quantil mit konservativem ν = n_A − 1 und n/(n−1)-Korrektur, Anteil w bekannter Varianz."""
import numpy as np
from scipy import stats
A1 = 0.05 / 43
ZB = stats.norm.isf(A1)
rng = np.random.default_rng(20261021)
N = 2_000_000
for n in (12, 22):
    for w in (0.0, 0.25, 0.5, 0.75):
        g = rng.chisquare(n - 1, N) / (n - 1)
        Z = rng.standard_normal(N)
        uk = np.sqrt((1 - w) * g + w)
        ub = np.sqrt((1 - w) * g * (n - 1) / n + w)
        tq = stats.t.isf(A1, n - 1)
        to = stats.t.isf(0.05, n - 1)
        print(f'n={n:2d} w={w:4.2f}: heutig {np.mean(Z - ZB * ub > 0) / A1:5.2f}·α′ | t(n−1) mit n/(n−1) '
              f'{np.mean(Z - tq * uk > 0) / A1:5.2f}·α′ | t(n−1) ohne Korrektur {np.mean(Z - tq * ub > 0) / A1:5.2f}·α′ |'
              f' obere: heutig {np.mean(Z + 1.645 * ub < 0):.4f}, t(0,95) korr. {np.mean(Z + to * uk < 0):.4f}')
