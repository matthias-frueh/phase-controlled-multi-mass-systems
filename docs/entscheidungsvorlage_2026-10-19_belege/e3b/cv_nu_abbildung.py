# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 4.2 (Anisotropie und ν).
# Zweck: Referenzwerte für CV²(ŝ²), K und r der Nachzählungs-Inversion bei isotropem Σ und ν Freiheitsgraden.
# Seed: default_rng(91); je ν 20 000 Modellkampagnen mit B = 1000. Laufzeit: gemessen 10 s Wandzeit, 10 s CPU (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B cv_nu_abbildung.py > cv_nu_abbildung.out
# Herkunft: Nachprüfung 5. Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""Nachleseauftrag 5, Teil (4), Hilfsrechnung: Welche CV²(ŝ²) über Kampagnen erzeugt die Nachzählungs-Inversion
(ŝ aus u = SD der Bootstrap-Beträge, isotrop invertiert) bei isotropem wahrem Σ, D = 0 und ν Freiheitsgraden der
Kovarianz? Bootstrap linear genähert: D_b = D̂ + ε_b, ε_b ~ N(0, Σ̂·ν/(ν+1)), B = 1000. Dazu K = E q⁴/(E q²)² und
r = E q²/(2 E ŝ²) unter demselben Modell (Referenz für die Werte aus indirekt_aniso_nu.out)."""
import math

import numpy as np
from scipy import special

rng = np.random.default_rng(91)
_b = np.linspace(0, 40, 4001)
_x = _b * _b / 4
_m = np.sqrt(np.pi / 2) * ((1 + 2 * _x) * special.ive(0, _x) + 2 * _x * special.ive(1, _x))
_h = np.sqrt(np.maximum(2 + _b * _b - _m * _m, 0)) / math.sqrt(2) * math.sqrt(2)   # SD(Rice(b)) bei Skala 1


def h(b):
    return np.interp(b, _b, _h)


def invert(q, u):
    lo, hi = u * 0.999, u / 0.6551
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        f = mid * h(q / mid) - u
        lo = np.where(f < 0, mid, lo)
        hi = np.where(f >= 0, mid, hi)
    return 0.5 * (lo + hi)


print('ν      CV²(ŝ²)   1/CV²    K       r      (je 20 000 Modellkampagnen, B = 1000)')
for nu in (19, 25, 30, 35, 40, 60, 80):
    N, B = 20000, 1000
    l11 = np.sqrt(rng.chisquare(nu, N)); l22 = np.sqrt(rng.chisquare(nu - 1, N)); l21 = rng.standard_normal(N)
    a, b, c = l11 / math.sqrt(nu + 1), l21 / math.sqrt(nu + 1), l22 / math.sqrt(nu + 1)   # Cholesky von Σ̂·ν/(ν+1)
    D = rng.standard_normal(N) + 1j * rng.standard_normal(N)
    u = np.empty(N)
    for i in range(0, N, 2000):
        z1 = rng.standard_normal((2000, B)); z2 = rng.standard_normal((2000, B))
        Db = D[i:i + 2000, None] + a[i:i + 2000, None] * z1 + 1j * (b[i:i + 2000, None] * z1 + c[i:i + 2000, None] * z2)
        u[i:i + 2000] = np.abs(Db).std(1, ddof=1)
    q = np.abs(D)
    s = invert(q, u)
    cv2 = np.var(s ** 2, ddof=1) / np.mean(s ** 2) ** 2
    K = np.mean(q ** 4) / np.mean(q ** 2) ** 2
    r = np.mean(q ** 2) / (2 * np.mean(s ** 2))
    print(f'{nu:3d}   {cv2:7.4f}   {1 / cv2:6.1f}   {K:5.2f}   {r:5.2f}')
