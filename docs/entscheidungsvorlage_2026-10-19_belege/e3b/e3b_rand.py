# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 4.1 (Warum die Intervallregel am Rand versagt).
# Zweck: heutige E3b-Regel am Rand (Rice, B → ∞), Obergrenze der Macht für „unauffällig“ (MP-Test), Vorschläge mit
#   geschätzter Streuung, Anisotropie, Macht, E3a mit z_B gegen t-Quantil.
# Seed: default_rng(20261018); N = 400 000 je Zelle. Laufzeit: etwa 1–2 min (Einschätzung; Ausgabe übernommen).
# Aufruf: python3 -I -B e3b_rand.py > e3b_rand.out
# Herkunft: Lesebericht zu c) (E3), 18.10.2026. Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""Teststatistik-Ebene: E3b-Grenzen am Schwellenrand (Rice-Modell) und Vorschläge.

Normierung: Streuung s = 1 je Komponente des komplexen Residuums D = R₋₁ − R̂₋₁ (bezogen auf |R̂₊₁|),
t = q_tol/s, wahrer Betrag |D| = t am Schwellenrand. Nur Statistik, keine Kampagnen.
"""
import math
import sys

import numpy as np
from scipy import optimize, special, stats

M = 43
ALPHA = 0.05
A1 = ALPHA / M
ZB = stats.norm.ppf(1 - A1)


def rice_std(b):
    x = b * b / 4
    m = math.sqrt(math.pi / 2) * ((1 + 2 * x) * special.ive(0, x) + 2 * x * special.ive(1, x))
    return math.sqrt(max(2.0 + b * b - m * m, 0.0))


def heutig_rand(t, zB=ZB, z_o=1.645):
    """Heutige Regel, B → ∞: u(X) = Streuung von Rice(X) (Bootstrap um den Schätzwert)."""
    xu = optimize.brentq(lambda x: x - zB * rice_std(x) - t, t, t + zB + 20.0)
    f = lambda x: x + z_o * rice_std(x) - t  # noqa: E731
    po = 0.0 if f(0.0) >= 0 else float(stats.rice.cdf(optimize.brentq(f, 0.0, t), t))
    return float(stats.rice.sf(xu, t)), po


def teil1():
    print('== 1 Heutige Regel am Rand (Rice, B → ∞), z_B =', round(ZB, 4), 'alpha/m =', round(A1, 6))
    print(' t     P(auff|rand)  Faktor  P(unauff|rand)  | mit u = s (wahre Streuung)  | Bonferroni-Summe 42·α/m + p')
    for t in (0.0, 0.1, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 20.0):
        pa, po = heutig_rand(t)
        p_s = float(stats.rice.sf(t + ZB, t)) if t > 0 else float(stats.rayleigh.sf(ZB))
        print(f'{t:5.2f}  {pa:.5f}      {pa / A1:5.2f}   {po:.4f}          | {p_s:.5f} ({p_s / A1:4.2f})            | {42 * A1 + pa:.4f}')


def teil2():
    """Bestmöglicher gültiger Einhaltungstest (Niveau 0,05 am Rand) gegen D = 0: MP-Test (Rice, s bekannt)."""
    print('\n== 2 Obergrenze der Macht für „unauffällig“ (E3b) bei D = 0, s bekannt (MP-Test)')
    print(' t     c=Rice.ppf(0.05,t)   P(unauff|D=0)')
    for t in (1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0):
        c = stats.rice.ppf(0.05, t)
        print(f'{t:5.2f}  {c:.3f}               {stats.rayleigh.cdf(c):.3f}')
    ts = optimize.brentq(lambda t: stats.rayleigh.cdf(stats.rice.ppf(0.05, t)) - 0.8, 1.0, 6.0)
    print(f' t* (Macht 0,8) = {ts:.3f}')
    return ts


def kritisch_rice(t0, a=A1):
    return stats.rice.isf(a, t0) if t0 > 0 else stats.rayleigh.isf(a)


def teil3(rng, N=400_000):
    """Vorschläge für „auffällig“ am Rand bei geschätzter Streuung ŝ (ν Freiheitsgrade je Komponente,
    isotrop gepoolt: 2ν), wahr s = 1. Gegenprobe der bekannten-s-Variante."""
    print('\n== 3 Größe am Rand: Vorschläge mit geschätzter Streuung (MC, N =', N, 'je Zelle; SE ≈',
          f'{math.sqrt(A1 / N) / A1:.2f}·α/m)')
    print(' nu     t     P1 Rice s bekannt | P2 Rice plug-in ŝ | P3 F-Scheibe | P4 Rice-ncF plug-in | heutig plug-in')
    out = []
    for nu in (19, 40, 80, None):
        for t in (0.25, 0.5, 1.0, 1.5, 3.0, 10.0):
            X = np.abs(t + rng.standard_normal(N) + 1j * rng.standard_normal(N))
            if nu is None:
                sh = np.ones(N)
                r = math.sqrt(stats.chi2.isf(A1, 2))
            else:
                sh = np.sqrt(rng.chisquare(2 * nu, N) / (2 * nu))
                r = math.sqrt(2 * stats.f.isf(A1, 2, 2 * nu))
            c1 = kritisch_rice(t)
            p1 = float((X > c1).mean())
            t0 = t / sh
            # P2: Rice-Quantil mit ŝ (Gitter für Geschwindigkeit)
            grid = np.linspace(max(t0.min(), 1e-6), t0.max(), 400)
            cg = np.array([kritisch_rice(g) for g in grid])
            c2 = np.interp(t0, grid, cg) * sh
            p2 = float((X > c2).mean())
            p3 = float((X - r * sh > t).mean())
            if nu is None:
                p4 = p1
            else:
                cg4 = np.array([math.sqrt(2 * stats.ncf.isf(A1, 2, 2 * nu, g * g)) if g > 1e-6 else
                                math.sqrt(2 * stats.f.isf(A1, 2, 2 * nu)) for g in grid])
                c4 = np.interp(t0, grid, cg4) * sh
                p4 = float((X > c4).mean())
            # heutige Regel mit plug-in: u = ŝ·rice_std(X/ŝ)
            xs = X / sh
            gx = np.linspace(0, xs.max() + 1, 600)
            gu = np.array([rice_std(g) for g in gx])
            u = np.interp(xs, gx, gu) * sh
            p0 = float((X - ZB * u > t).mean())
            nus = '∞' if nu is None else str(nu)
            print(f' {nus:4s} {t:5.2f}  {p1 / A1:5.2f}             | {p2 / A1:5.2f}             | {p3 / A1:5.2f}        | '
                  f'{p4 / A1:5.2f}               | {p0 / A1:5.2f}   (Vielfache von α/m)')
            out.append((nu, t, p1, p2, p3, p4, p0))
    return out


def teil4(rng, N=400_000):
    """Anisotropie: Σ = diag(1, ρ²), wahrer Betrag t entlang der großen (θ = 0) bzw. kleinen Achse (θ = 90°).
    Rice-Test mit s = √λ_max (konservativ?) bzw. s = √(Spur/2)."""
    print('\n== 4 Anisotropie (s bekannt): Größe am Rand in Vielfachen von α/m')
    print(' rho   t     θ      s=√λmax   s=√(Spur/2)')
    for rho in (1.0, 0.5, 0.25):
        for t in (0.5, 1.5, 3.0):
            for th in (0.0, 90.0):
                D = t * np.exp(1j * np.radians(th))
                Z = D + rng.standard_normal(N) + 1j * rho * rng.standard_normal(N)
                X = np.abs(Z)
                c_max = kritisch_rice(t)
                sm = math.sqrt((1 + rho * rho) / 2)
                c_mit = sm * kritisch_rice(t / sm)
                print(f' {rho:4.2f} {t:5.2f} {th:5.0f}   {float((X > c_max).mean()) / A1:6.2f}    '
                      f'{float((X > c_mit).mean()) / A1:6.2f}')


def teil5():
    """Macht der gültigen Grenze (P1, s bekannt) und der heutigen Regel bei |D| = k·q_tol."""
    print('\n== 5 Macht „auffällig“ bei |D| = k·q_tol (s bekannt); k = 2 ≙ 0,2°, 3 ≙ 0,3°, 5,74 ≙ 1 % Amplitude')
    print(' t     k     P1 Rice      heutig (B → ∞)')
    for t in (0.5, 1.5, 3.0, 10.0):
        c1 = kritisch_rice(t)
        xu = optimize.brentq(lambda x: x - ZB * rice_std(x) - t, t, t + ZB + 20.0)
        for k in (1.0, 2.0, 3.0, 5.74):
            print(f'{t:5.2f} {k:5.2f}  {stats.rice.sf(c1, k * t):.4f}       {stats.rice.sf(xu, k * t):.4f}')


def teil6():
    """E3a (reellwertig) am Rand mit geschätzter Streuung (ν Freiheitsgrade): z_B gegen t-Quantil."""
    print('\n== 6 E3a am Rand: Größe der Regel |x| − z_B·u > Schwelle bei u mit ν Freiheitsgraden')
    for nu in (19, 40, 80, 200):
        p = stats.t.sf(ZB, nu)
        print(f' ν = {nu:3d}: P = {p:.5f} = {p / A1:4.2f}·α/m;  t-Quantil t(1−α/m; ν) = {stats.t.isf(A1, nu):.3f};'
              f'  Bonferroni-Summe bei 43 solchen Prüfungen: {43 * p:.4f}')


if __name__ == '__main__':
    rng = np.random.default_rng(20261018)
    teil1()
    ts = teil2()
    teil3(rng)
    teil4(rng)
    teil5()
    teil6()
