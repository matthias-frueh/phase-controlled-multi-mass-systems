"""
linear_solver.py – exakte stationäre Lösung der Referenz-Engine im liftoff-freien Bereich.

Solange der Körper nicht abhebt, ist das Modell der Engine linear:

    M·ẍ + C·ẋ + K·x = −μ·M·ā(t),     N(t) = M·g − K·x − C·ẋ

mit ā(t) = [a(t) + a(t−τ₂) + a(t−τ₃)]/3 der mittleren Beschleunigung der drei Module, τₖ = φₖ/(2π·f)
und μ dem Anteil der Masse, der sich mit den Modulen bewegt (Engine: μ = 1, masseloser Rahmen).
Im eingeschwungenen Zustand gilt für jede Harmonische k der Anregungsfrequenz f

    N_k = μ·M · H(kω) · P_k · (1 + e^{−ikφ₂} + e^{−ikφ₃}) / 3,     H(ω) = (K + iωC) / (K − Mω² + iωC)

mit P_k den Fourier-Koeffizienten des Bewegungsprofils. Die Phasenlage wirkt nur über den Faktor
(1 + e^{−ikφ₂} + e^{−ikφ₃})/3; bei (120°, 240°) verschwindet er für alle k, die kein Vielfaches von 3
sind (wie beim Massenausgleich des Dreizylindermotors). Die Kontaktsteifigkeit wirkt nur über H.

Die Lösung ist gültig, wenn N(t) > 0 und die Auflagerkoordinate z(t) < 0 bleiben; sonst hebt der
Körper ab, und nur die RK4-Engine liefert die Wellenform. Das Skript kennzeichnet solche Punkte
(valid = False) und gibt dort nur das lineare Minimum F_min_lin < 0 aus. Ob die Engine aus ihrer
Startbedingung tatsächlich in den liftoff-freien Zustand einschwingt, sagt die lineare Lösung allein nicht;
für alle Punkte der drei Datensätze trifft es zu (--validate).

Aufruf:
  python3 linear_solver.py --validate                 Abgleich mit allen drei Datensätzen in data/ (Exit-Code 1 bei Abweichung)
  python3 linear_solver.py --point 120 240            Observablen an einem Punkt
  python3 linear_solver.py --ktable                   F_min(120°, 240°) über K, ζ konstant und C fest
  python3 linear_solver.py --map karte.csv --step 2   Karte über [0°, 360°)², Anteil liftoff-freier Punkte
Optionen für --point und --map: --K, --C oder --zeta, --mu, --rigid (starre Auflage), --sinus (Sinusprofil).

Rechenzeit: ca. 1 ms je Punkt (Engine: ca. 2 s). Stichproben wie in der Engine (Δt = 50 µs, 2000 je
Periode), damit F_min, F_max und Schiefe direkt mit den CSV-Werten vergleichbar sind. Das Spektrum wird
auf einem achtfach feineren Raster gebildet; feinere Raster ändern die Observablen um weniger als 1e-6.
Abgleich mit der RK4-Engine (--validate): alle 851 Punkte der drei Datensätze richtig als liftoff-frei
oder abhebend klassifiziert, Observablen der 442 liftoff-freien Punkte auf ≤ 6e-6 gleich.

Matthias Früh · PCMMS · September 2026
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import skew

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
sys.path.insert(0, HERE)
from finesweep import (M, MG, F_HZ, T_CYC, RTOP, RBOT, K, C_DAMP, DT,  # noqa: E402
                       z_egg_zdd)

N_PER = int(round(T_CYC / DT))          # 2000 Stichproben je Periode wie in der Engine
OVERSAMPLE = 8                          # feineres Raster für das Spektrum des Profils
SINUS_AMPLITUDE = (RTOP + RBOT) / 2     # aus sweep_7x7_sinus.csv rekonstruiert (data/README.md)
OMEGA = 2 * np.pi * F_HZ


def sinus_zdd(t, amplitude=SINUS_AMPLITUDE):
    return -amplitude * OMEGA**2 * np.sin(OMEGA * t)


def profile_spectrum(profile='egg', oversample=OVERSAMPLE):
    """Fourier-Koeffizienten P_k der Profilbeschleunigung auf einem Raster mit N_PER·oversample Punkten."""
    n = N_PER * oversample
    t = np.arange(n) * (T_CYC / n)
    a = z_egg_zdd(t) if profile == 'egg' else sinus_zdd(t)
    P = np.fft.rfft(a)
    P[0] = 0.0      # Mittelwert der Profilbeschleunigung ist exakt null (Rasterfehler ~1e-7 m/s² verwerfen)
    return P, n


def transfer(K_c, C_c, n_harm):
    """H(kω) für k = 0 … n_harm−1; K_c = None bedeutet starre Auflage (H = 1)."""
    w = OMEGA * np.arange(n_harm)
    if K_c is None:
        return np.ones(n_harm, complex), np.zeros(n_harm, complex)
    den = K_c - M * w**2 + 1j * w * C_c
    return (K_c + 1j * w * C_c) / den, -1.0 / den      # Kraft- und Nachgiebigkeitsübertragung


def solve(phi2_deg, phi3_deg, K_c=K, C_c=C_DAMP, mu=1.0, profile='egg', oversample=OVERSAMPLE,
          chunk=256):
    """Stationäre Lösung für beliebig viele Phasenpunkte. Gibt ein Dict mit Arrays zurück
    (Spalten wie in den CSV-Dateien der Engine, dazu valid und F_min_lin)."""
    phi2 = np.atleast_1d(np.asarray(phi2_deg, float))
    phi3 = np.atleast_1d(np.asarray(phi3_deg, float))
    P, n = profile_spectrum(profile, oversample)
    k = np.arange(P.size)
    H, Y = transfer(K_c, C_c, P.size)
    out = {c: np.empty(phi2.size) for c in
           ('F_mean', 'F_skew', 'liftoff', 'F_max', 'F_min', 'peak_ratio', 'F_min_lin', 'z_max')}
    out['valid'] = np.empty(phi2.size, bool)
    for s in range(0, phi2.size, chunk):
        sl = slice(s, s + chunk)
        comb = (1 + np.exp(-1j * np.outer(np.radians(phi2[sl]), k))
                + np.exp(-1j * np.outer(np.radians(phi3[sl]), k))) / 3
        A = P * comb
        F_fine = MG + mu * M * np.fft.irfft(A * H, n, axis=1)
        F = F_fine[:, ::oversample]                         # Stichproben wie in der Engine
        if K_c is None:
            z_max = np.full(F.shape[0], -np.inf)
        else:                                               # Auflagerkoordinate um die statische Einfederung
            z_max = (-MG / K_c + mu * M * np.fft.irfft(A * Y, n, axis=1)[:, ::oversample]).max(1)
        F_min, F_max = F.min(1), F.max(1)
        valid = (F_min > 0) & (z_max < 0)
        denom = MG - F_min
        out['F_mean'][sl] = F_fine.mean(1)
        out['F_skew'][sl] = np.where(valid, skew(F, axis=1), np.nan)
        out['liftoff'][sl] = np.where(valid, 0.0, np.nan)
        out['F_max'][sl] = np.where(valid, F_max, np.nan)
        out['F_min'][sl] = np.where(valid, F_min, np.nan)
        out['peak_ratio'][sl] = np.where(valid & (denom > 1e-6),
                                         (F_max - MG) / np.where(denom > 1e-6, denom, 1.0), np.nan)
        out['F_min_lin'][sl] = F_min
        out['z_max'][sl] = z_max
        out['valid'][sl] = valid
    out['phi2_deg'], out['phi3_deg'] = phi2, phi3
    return out


def waveform(phi2_deg, phi3_deg, K_c=K, C_c=C_DAMP, mu=1.0, profile='egg', oversample=OVERSAMPLE):
    """N(t) der linearen Lösung über eine Periode auf dem feinen Raster (Zeit in s, Kraft in N)."""
    P, n = profile_spectrum(profile, oversample)
    k = np.arange(P.size)
    H, _ = transfer(K_c, C_c, P.size)
    comb = (1 + np.exp(-1j * k * np.radians(phi2_deg)) + np.exp(-1j * k * np.radians(phi3_deg))) / 3
    return np.arange(n) * (T_CYC / n), MG + mu * M * np.fft.irfft(P * comb * H, n)


def c_for(K_c, zeta):
    return 2 * zeta * np.sqrt(K_c * M)


# ── Kommandos ────────────────────────────────────────────────────────────────
def validate():
    """Abgleich mit den Engine-Datensätzen: Liftoff-Klassifikation aller Punkte und Observablen aller
    liftoff-freien Punkte. Toleranz 1e-4 (N bzw. dimensionslos), F_mean 1e-5 N."""
    checks = [('sweep_19x19.csv', 'phi2_deg', 'phi3_deg', 'peak_ratio', 'egg'),
              ('finesweep_2deg_120_240.csv', 'phi2_deg', 'phi3_deg', 'peak_ratio', 'egg'),
              ('sweep_7x7_sinus.csv', 'phi2', 'phi3', 'asym', 'sinus')]
    ok = True
    for fname, c2, c3, ca, prof in checks:
        df = pd.read_csv(os.path.join(DATA, fname))
        r = solve(df[c2].values, df[c3].values, profile=prof)
        free = (df.liftoff == 0).values
        mis = int((r['valid'] != free).sum())
        dev = {'F_mean': np.abs(r['F_mean'][free] - df.F_mean.values[free]).max(),
               'F_min': np.abs(r['F_min'][free] - df.F_min.values[free]).max(),
               'F_max': np.abs(r['F_max'][free] - df.F_max.values[free]).max(),
               'F_skew': np.abs(r['F_skew'][free] - df.F_skew.values[free]).max(),
               'A': np.abs(r['peak_ratio'][free] - df[ca].values[free]).max()}
        tol = {'F_mean': 1e-5, 'F_min': 1e-4, 'F_max': 1e-4, 'F_skew': 1e-4, 'A': 1e-4}
        bad = [q for q in dev if not dev[q] <= tol[q]]
        ok &= (mis == 0) and not bad
        print(f'{fname}: {len(df)} Punkte, {free.sum()} liftoff-frei, Klassifikation abweichend: {mis}')
        print('   max |Δ| ' + '  '.join(f'{q} {v:.1e}' for q, v in dev.items())
              + ('   OK' if not bad and mis == 0 else f'   FEHLER: {bad or "Klassifikation"}'))
    print('Ergebnis:', 'bestanden' if ok else 'NICHT bestanden')
    return ok


def ktable():
    print('F_min bei (120°, 240°), Referenzparameter bis auf K und C')
    print(f'{"K [N/m]":>10} {"3f/f_n":>7} {"ζ konst. (C ~ √K)":>18} {"C = 16 N·s/m":>14}')
    for K_c in [1e4, 2e4, 2.3e4, 2.5e4, 3e4, 1e5, 1e6, 1e7]:
        f_n = np.sqrt(K_c / M) / (2 * np.pi)
        vals = []
        for C_c in (C_DAMP * np.sqrt(K_c / K), C_DAMP):
            r = solve(120.0, 240.0, K_c, C_c)
            vals.append(f'{r["F_min"][0]:.4f}' if r['valid'][0] else f'Liftoff ({r["F_min_lin"][0]:+.2f})')
        print(f'{K_c:>10.0f} {3 * F_HZ / f_n:>7.2f} {vals[0]:>18} {vals[1]:>14}')
    r = solve(120.0, 240.0, None)
    print(f'{"starr":>10} {0:>7.2f} {r["F_min"][0]:>18.4f} {r["F_min"][0]:>14.4f}')


def params(a):
    K_c = None if a.rigid else a.K
    C_c = 0.0 if a.rigid else (c_for(a.K, a.zeta) if a.zeta is not None else a.C)
    return K_c, C_c


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--validate', action='store_true')
    ap.add_argument('--ktable', action='store_true')
    ap.add_argument('--point', nargs=2, type=float, metavar=('PHI2', 'PHI3'))
    ap.add_argument('--map', metavar='CSV')
    ap.add_argument('--step', type=float, default=2.0, help='Rasterweite der Karte in Grad')
    ap.add_argument('--K', type=float, default=K)
    ap.add_argument('--C', type=float, default=C_DAMP)
    ap.add_argument('--zeta', type=float, default=None, help='setzt C = 2ζ·√(K·M)')
    ap.add_argument('--mu', type=float, default=1.0, help='Anteil der bewegten Masse')
    ap.add_argument('--rigid', action='store_true')
    ap.add_argument('--sinus', action='store_true')
    a = ap.parse_args()
    prof = 'sinus' if a.sinus else 'egg'
    if a.validate:
        sys.exit(0 if validate() else 1)
    if a.ktable:
        ktable()
    if a.point:
        K_c, C_c = params(a)
        r = solve(*a.point, K_c, C_c, a.mu, prof)
        for q in ('valid', 'F_mean', 'F_skew', 'F_max', 'F_min', 'peak_ratio', 'F_min_lin'):
            print(f'{q:>10}: {r[q][0]}')
    if a.map:
        K_c, C_c = params(a)
        g = np.arange(0.0, 360.0, a.step)
        P2, P3 = np.meshgrid(g, g, indexing='ij')
        r = solve(P2.ravel(), P3.ravel(), K_c, C_c, a.mu, prof)
        cols = ['phi2_deg', 'phi3_deg', 'valid', 'F_mean', 'F_skew', 'liftoff', 'F_max', 'F_min',
                'peak_ratio', 'F_min_lin']
        pd.DataFrame({c: r[c] for c in cols}).to_csv(a.map, index=False, float_format='%.6f')
        print(f'{a.map}: {r["valid"].size} Punkte, liftoff-frei {100 * r["valid"].mean():.1f} %')
    if not (a.validate or a.ktable or a.point or a.map):
        ap.print_help()


if __name__ == '__main__':
    main()
