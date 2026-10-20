# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 4.2 und 4.3.
# Zweck: kleine Kontrollrechnungen zu E3a (obere Grenze heute, Fehlalarm auf L4, Faltungsfaktor) und zu κ.
# Seed: keiner (Quadratur). Laufzeit: gemessen unter 1 s (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B kleinrechnungen.py > kleinrechnungen.out
# Herkunft: Nachprüfung 5. Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""Nachleseauftrag 5: kleine Kontrollrechnungen (analytisch/Quadratur)."""
import math
import numpy as np
from scipy import integrate, stats
A1 = 0.05 / 43
ZB = stats.norm.isf(A1)
# E3a obere Grenze heute (z = 1,645, Plug-in-u) am Rand, n = 22, w = 0
n = 22
f = lambda x: stats.norm.cdf(-1.645 * math.sqrt(x / (n - 1) * (n - 1) / n)) * stats.chi2.pdf(x, n - 1)
print('E3a obere Grenze heute, n=22, w=0:', round(integrate.quad(f, 0, np.inf)[0], 4))
# E3a L4 Kampagne 31: Fehlalarm unter t-Regel?
x, unter = 0.510286, 0.1440597560816373
u = (x - unter) / ZB
print('L4 K31: u falls gleiche Prüfung wie max|Δφ| =', round(u, 4))
for na in (20, 22, 24):
    tq = stats.t.isf(A1, na - 1) * math.sqrt(na / (na - 1))
    print(f'  n_A={na}: t·√(n/(n−1)) = {tq:.3f}; untere Grenze mit u={u:.3f}: {x - tq * u:.4f}; mit u=0.160 (Median): '
          f'{x - tq * 0.160:.4f}; nötiges u für Wegfall: {(unter - 0.1) / (tq - ZB):.4f}')
# Faltungsfaktor E3a bei Schwelle/u (t-Regel, ν = 21, exakt am Rand x = s)
for h in (0.5, 0.6, 1.0):
    nu = 21
    tq = stats.t.isf(A1, nu)
    g = lambda y: (stats.norm.sf(tq * math.sqrt(y / nu)) + stats.norm.sf(2 * h + tq * math.sqrt(y / nu))) * stats.chi2.pdf(y, nu)
    print(f'Faltung h={h}: {integrate.quad(g, 0, np.inf)[0] / A1:.3f}·α/m')
# κ, t-Quantile
for nu in (19, 21, 40):
    print(f'ν={nu}: t(1−α/m)={stats.t.isf(A1, nu):.4f}, κ={stats.t.isf(A1, nu) / ZB:.4f}, t(0,95)={stats.t.isf(0.05, nu):.4f}')
print('z_B =', round(ZB, 4), 'α/m =', A1)
