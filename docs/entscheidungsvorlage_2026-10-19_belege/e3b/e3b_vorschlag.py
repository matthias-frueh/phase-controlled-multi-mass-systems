# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 4.1 und 4.2.
# Zweck: erste Konstruktion einer gültigen E3b-Grenze mit geschätzter 2×2-Kovarianz; Größe am Rand der Regeln R0
#   (heute), R1, R1a, R2 (Vorlage Option B) und R3 (F-Scheibe) und Macht; Monte Carlo mit linearem Bootstrap.
# Seed: default_rng(20261019); N = 200 000 je Zelle, B = 200. Laufzeit: mehrere Minuten (Einschätzung; nicht neu
#   gerechnet, e3b_vorschlag.out ist übernommen).
# Aufruf: python3 -I -B e3b_vorschlag.py > e3b_vorschlag.out
# Herkunft: Lesebericht zu c) (E3) der ersten Fassung, 18.10.2026. Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""Teststatistik-Ebene: Vorschlag für eine gültige untere Grenze von E3b mit geschätzter 2×2-Kovarianz.

Modell: D̂ = D + ε, ε ~ N₂(0, Σ), Σ = diag(1, ρ²) (s = 1 entlang der großen Achse); Bootstrap-Kovarianz
Σ̂_boot = W/(ν+1) mit W ~ Wishart(ν, Σ) (Plug-in-Varianz des Mittels aus n = ν+1 Läufen, Faktor (n−1)/n).
Regeln für „auffällig“ (Überschreitung von q_tol nachgewiesen), wahrer Betrag |D| = t am Rand, Richtung θ:
  R0  heutig:   X − z_B·u > t, u = Streuung des Betrags der Bootstrap-Replikate (≈ ŝ·rice_std(X/ŝ))
  R1  Rice plug-in:     X > ŝ·Rice⁻¹(1 − α/m; t/ŝ), ŝ² = λ_max(Σ̂_boot)
  R2  Rice korrigiert:  wie R1 mit ŝ² = λ_max(Σ̂_boot)·n/(n−1) und ŝ·κ_ν, κ_ν = t_ν⁻¹(1 − α/m)/z⁻¹(1 − α/m)
  R3  F-Scheibe:        X − ŝ·√(2·F⁻¹(1 − α/m; 2, ν)) > t, ŝ² = λ_max·n/(n−1)
Ausgabe: Größe am Rand in Vielfachen von α/m (sup über θ ∈ {0°, 90°}) und Macht bei |D| = k·t.
"""
import math

import numpy as np
from scipy import special, stats

M, ALPHA = 43, 0.05
A1 = ALPHA / M
ZB = stats.norm.isf(A1)


def rice_std(b):
    x = b * b / 4
    m = math.sqrt(math.pi / 2) * ((1 + 2 * x) * special.ive(0, x) + 2 * x * special.ive(1, x))
    return math.sqrt(max(2.0 + b * b - m * m, 0.0))


_G = np.linspace(0, 60, 3001)
_RS = np.array([rice_std(g) for g in _G])
_RQ = np.array([stats.rice.isf(A1, g) if g > 0 else stats.rayleigh.isf(A1) for g in _G])


def rice_q(t0):
    return np.interp(t0, _G, _RQ)


def wishart(nu, rho, N, rng):
    """2×2-Wishart(ν, diag(1, ρ²))/ν über Bartlett (W = L·Lᵀ): Rückgabe (w11, w21, w22, λ_max)."""
    c1 = np.sqrt(rng.chisquare(nu, N))
    c2 = np.sqrt(rng.chisquare(nu - 1, N))
    z = rng.standard_normal(N)
    # W = S^{1/2} L Lᵀ S^{1/2},  S = diag(1, ρ²)
    l11, l21, l22 = c1, z, c2
    w11 = l11 ** 2
    w21 = rho * l21 * l11
    w22 = rho ** 2 * (l21 ** 2 + l22 ** 2)
    tr, det = w11 + w22, w11 * w22 - w21 ** 2
    return w11 / nu, w21 / nu, w22 / nu, (tr / 2 + np.sqrt(np.maximum(tr * tr / 4 - det, 0))) / nu


def bootstrap_u(Dh, w, f, B, rng):
    """Heutige Regel: u = Streuung von |D̂ + ε_b|, ε_b ~ N₂(0, f·Σ̂) (lineare Näherung des Bootstraps)."""
    w11, w21, w22 = (f * x for x in w)
    a = np.sqrt(w11)
    b = w21 / a
    c = np.sqrt(np.maximum(w22 - b * b, 0))
    z1 = rng.standard_normal((Dh.size, B))
    z2 = rng.standard_normal((Dh.size, B))
    Db = Dh[:, None] + (a[:, None] * z1) + 1j * (b[:, None] * z1 + c[:, None] * z2)
    return np.abs(Db).std(1, ddof=1)


def regeln(X, lmax_boot, nu, t, u0):
    n = nu + 1
    s_boot = np.sqrt(lmax_boot)
    r0 = X - ZB * u0 > t
    r1 = X > s_boot * rice_q(t / s_boot)
    ra = X > np.sqrt(lmax_boot * n / (n - 1)) * rice_q(t / np.sqrt(lmax_boot * n / (n - 1)))
    s_k = np.sqrt(lmax_boot * n / (n - 1))
    kap = stats.t.isf(A1, nu) / ZB
    r2 = X > kap * s_k * rice_q(t / (kap * s_k))
    r3 = X - s_k * math.sqrt(2 * stats.f.isf(A1, 2, nu)) > t
    return r0, r1, ra, r2, r3


def ziehen(D, rho, nu, N, rng, B):
    Dh = D + rng.standard_normal(N) + 1j * rho * rng.standard_normal(N)
    w11, w21, w22, lm = wishart(nu, rho, N, rng)
    f = nu / (nu + 1)                                                    # Plug-in-Faktor (n−1)/n
    u0 = np.concatenate([bootstrap_u(Dh[i:i + 5000], (w11[i:i + 5000], w21[i:i + 5000], w22[i:i + 5000]), f, B, rng)
                         for i in range(0, N, 5000)])
    return np.abs(Dh), lm * f, u0


def lauf(rng, N=200_000, B=200):
    print('Größe am Rand (Vielfache von α/m = %.5f), sup über θ ∈ {0°, 90°}; MC-SE ≈ %.2f; Bootstrap B = %d'
          % (A1, math.sqrt(1 / (A1 * N)), B))
    print(' ν    ρ     t     | R0 heutig | R1 Rice plug-in | R1a nur n/(n−1) | R2 Rice korrigiert | R3 F-Scheibe')
    for nu in (21, 40, 80):
        for rho in (1.0, 0.5, 0.25):
            for t in (0.25, 1.0, 1.5, 3.0, 10.0):
                best = np.zeros(5)
                for th in (0.0, 90.0):
                    X, lb, u0 = ziehen(t * np.exp(1j * np.radians(th)), rho, nu, N, rng, B)
                    p = np.array([r.mean() for r in regeln(X, lb, nu, t, u0)]) / A1
                    best = np.maximum(best, p)
                print(f' {nu:3d} {rho:4.2f} {t:5.2f}   | {best[0]:6.2f}    | {best[1]:6.2f}          | {best[2]:6.2f}'
                      f'          | {best[3]:6.2f}             | {best[4]:6.2f}', flush=True)


def macht(rng, N=50_000, B=200):
    print('\nMacht „auffällig“ bei |D| = k·t (isotrop, θ = 0), ν = 40; k = 2 ≙ 0,2°, 3 ≙ 0,3°, 5,74 ≙ 1 % Amplitude')
    print(' t     k     R0      R1      R1a     R2      R3')
    nu = 40
    for t in (0.5, 1.5, 3.0, 10.0):
        for k in (2.0, 3.0, 5.74):
            X, lb, u0 = ziehen(k * t + 0j, 1.0, nu, N, rng, B)
            p = [r.mean() for r in regeln(X, lb, nu, t, u0)]
            print(f'{t:5.2f} {k:5.2f}  ' + '  '.join(f'{x:.4f}' for x in p))


if __name__ == '__main__':
    rng = np.random.default_rng(20261019)
    lauf(rng)
    macht(rng)
