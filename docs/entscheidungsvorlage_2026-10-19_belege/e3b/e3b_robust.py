# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 4.1 und 4.2.
# Zweck: R2 bei kleinen ν und starker Anisotropie, obere Grenze O1 für „unauffällig“, Macht bei D = 0 gegen den
#   MP-Test, E3a am Rand mit t-Quantil. Importiert e3b_vorschlag.py aus diesem Ordner.
# Seed: default_rng(20261020); N = 400 000. Laufzeit: etwa 1–2 min (Einschätzung; Ausgabe übernommen).
# Aufruf: python3 -B e3b_robust.py > e3b_robust.out
# Herkunft: Lesebericht zu c) (E3), 18.10.2026. Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""Ergänzung: R2 (auffällig) bei kleinen ν und starker Anisotropie; obere Grenze für „unauffällig“
O1: X + t(0,95; ν)·ŝ_max ≤ t (Projektionsschranke), ŝ²_max = λ_max(Σ̂_boot)·n/(n−1), Größe am Rand ≤ 0,05?
Macht bei D = 0 gegen den MP-Test (s bekannt). E3a: Größe am Rand mit t-Quantil und Anteil bekannter Varianz."""
import math

import numpy as np
from scipy import stats

import importlib.util
import os

_spec = importlib.util.spec_from_file_location('v', os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                 'e3b_vorschlag.py'))
v = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v)

A1, ZB = v.A1, v.ZB


def r2(X, lm_boot, nu, t):
    n = nu + 1
    sk = np.sqrt(lm_boot * n / (n - 1))
    kap = stats.t.isf(A1, nu) / ZB
    return X > kap * sk * v.rice_q(t / (kap * sk))


def o1(X, lm_boot, nu, t):
    n = nu + 1
    sk = np.sqrt(lm_boot * n / (n - 1))
    return X + stats.t.isf(0.05, nu) * sk <= t


def main(rng, N=400_000):
    print('R2 „auffällig“ und O1 „unauffällig“ am Rand (sup über θ ∈ {0°, 45°, 90°}); R2 in Vielfachen von α/m, O1 absolut')
    print(' ν    ρ     t     | R2/α′  | O1 P(unauff | Rand)')
    for nu in (10, 21, 40):
        for rho in (1.0, 0.5, 0.1):
            for t in (0.25, 1.0, 1.5, 3.0, 5.0, 10.0):
                b2 = bo = 0.0
                for th in (0.0, 45.0, 90.0):
                    D = t * np.exp(1j * np.radians(th))
                    X = np.abs(D + rng.standard_normal(N) + 1j * rho * rng.standard_normal(N))
                    lm = v.wishart(nu, rho, N, rng)[3] * nu / (nu + 1)
                    b2 = max(b2, r2(X, lm, nu, t).mean() / A1)
                    bo = max(bo, o1(X, lm, nu, t).mean())
                print(f' {nu:3d} {rho:4.2f} {t:5.2f}   | {b2:5.2f}  | {bo:.4f}', flush=True)
    print('\nMacht „unauffällig“ bei D = 0 (isotrop): O1 mit ν = 40 gegen MP-Test (s bekannt) und heutige Regel (PR #22)')
    for t in (1.5, 2.0, 3.0, 3.5, 4.0, 5.0):
        X = np.abs(rng.standard_normal(N) + 1j * rng.standard_normal(N))
        lm = v.wishart(40, 1.0, N, rng)[3] * 40 / 41
        mp = stats.rayleigh.cdf(stats.rice.ppf(0.05, t))
        print(f' t = {t:4.2f}: O1 {o1(X, lm, 40, t).mean():.3f}   MP {mp:.3f}')
    # t*, O1 mit s bekannt: P(Rayleigh ≤ t − 1,645) = 0,8
    print(' t* (O1, s bekannt, ν = ∞) =', round(1.645 + math.sqrt(-2 * math.log(0.2)), 3))
    print('\nE3a am Rand: Größe der Regeln mit n = 22 Läufen (Bootstrap-Anteil mit (n−1)/n und ν = 21), '
          'Anteil w bekannter Varianz (Δδ, T, Quantisierung) an u²')
    n = 22
    for w in (0.0, 0.25, 0.5, 0.75):
        g = rng.chisquare(n - 1, N) / (n - 1)
        u_boot = np.sqrt((1 - w) * g * (n - 1) / n + w)               # heutige u (Plug-in-Bootstrap)
        u_korr = np.sqrt((1 - w) * g + w)
        Z = rng.standard_normal(N)
        nu_eff = 1.0 / (((1 - w) * g) ** 2 / (n - 1) / u_korr ** 4)
        heut = (Z - ZB * u_boot > 0).mean() / A1
        tq = stats.t.isf(A1, nu_eff)
        korr = (Z - tq * u_korr > 0).mean() / A1
        print(f' w = {w:4.2f}: heutig z_B {heut:5.2f}·α′ | t(ν_eff) mit n/(n−1) {korr:5.2f}·α′ | ν_eff Median '
              f'{np.median(nu_eff):7.1f}')


if __name__ == '__main__':
    main(np.random.default_rng(20261020))
