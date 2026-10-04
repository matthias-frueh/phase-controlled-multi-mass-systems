#!/usr/bin/env python3
"""P3 / bewertung_a – B01 (P2-8, Kandidat 70): Wie groß ist die Spiegelungsbrechung (phi -> -phi),
die P2 (SYM-02) als Messgröße der komplexen Kontaktübertragung vorschlägt, am steifen V1-Arbeitspunkt?

Rechnung mit code/linear_solver.solve (lineares Dauerkontaktmodell, Präreg A2.1). Hub 8 mm wird über
mu_eff = mu * 8 mm / 7,6923 mm abgebildet (alle Kraftabweichungen sind linear in mu*Hub, P2 AUS-07).
Spiegelpaar auf dem Schnitt: (phi2, 240°) <-> (240° - phi2, 240°) (Spiegelung um 120°, P2 SYM-02).
Ausgabe: max |Delta F_min| über das Paar, Zeltsekanten links/rechts, Schiefe-Differenz; zum Vergleich
die Referenz (K = 1e4, C = 16, mu = 1) und die starre Auflage.
Bandbegrenzung: ohne (wie linear_solver) – Obergrenze; Präreg wertet bandbegrenzt aus.
"""
import numpy as np
from linear_solver import solve, c_for

HUB_REF = 0.005 * (1 + 0.35 / 0.65)
cases = [
    ('Referenz K=1e4, C=16, mu=1', 1e4, 16.0, 1.0),
    ('V1 K=1,5e6, zeta=0,05, 3x100 g, 8 mm', 1.5e6, c_for(1.5e6, 0.05), 0.3 / 0.65 * 0.008 / HUB_REF),
    ('V1 K=1,5e6, zeta=0,02', 1.5e6, c_for(1.5e6, 0.02), 0.3 / 0.65 * 0.008 / HUB_REF),
    ('V3 K=3e6, zeta=0,05, 3x50 g, 14 Hz', 3e6, c_for(3e6, 0.05), 0.15 / 0.65 * 0.008 / HUB_REF),
    ('starr, mu wie V1', None, 0.0, 0.3 / 0.65 * 0.008 / HUB_REF),
]
p2 = np.arange(100.0, 120.0 + 1e-9, 2.0)
for name, K, C, mu in cases:
    f = 14.0 if 'V3' in name else 10.0
    a = solve(p2, 240.0, K, C, mu, f_hz=f)
    b = solve(240.0 - p2, 240.0, K, C, mu, f_hz=f)
    d = a['F_min_lin'] - b['F_min_lin']
    ds = a['F_skew'] - b['F_skew']
    tri = solve([120.0], [240.0], K, C, mu, f_hz=f)
    span = solve(np.arange(100.0, 140.0 + 1e-9, 2.0), 240.0, K, C, mu, f_hz=f)['F_min_lin']
    sl = (tri['F_min_lin'][0] - solve([118.0], [240.0], K, C, mu, f_hz=f)['F_min_lin'][0]) / 2
    sr = (tri['F_min_lin'][0] - solve([122.0], [240.0], K, C, mu, f_hz=f)['F_min_lin'][0]) / 2
    print(f'{name:>40}: max|dF_min| = {np.abs(d).max()*1e3:8.4f} mN (bei phi2 = {p2[np.argmax(np.abs(d))]:.0f}°), '
          f'max|d gamma1| = {np.nanmax(np.abs(ds)):.5f}; 2°-Sekanten L/R = {sl*1e3:.3f}/{sr*1e3:.3f} mN/°; '
          f'Zeltspannweite {(span.max()-span.min())*1e3:.1f} mN; Kontaktast überall: {bool(np.all(a["valid"]) and np.all(b["valid"]))}')


# --- Ergänzung: bandbegrenzt wie Präreg §4/A9.4 (Koeffizienten oberhalb k_max null) ---
from linear_solver import profile_spectrum, transfer
from finesweep import MG, M as M_TOT


def fmin_bl(phi2, phi3, K, C, mu, f, kmax, n_out=2000):
    P, n = profile_spectrum('egg')
    P = P * (f / 10.0) ** 2
    k = np.arange(P.size)
    H, _ = transfer(K, C, P.size, f_hz=f)
    comb = (1 + np.exp(-1j * k * np.radians(phi2)) + np.exp(-1j * k * np.radians(phi3))) / 3
    A = P * comb * H
    A[kmax + 1:] = 0.0
    N = MG + mu * M_TOT * np.fft.irfft(A, n)
    N = N[:: n // n_out]
    return N.min() - N.mean(), ((N - N.mean()) ** 3).mean() / ((N - N.mean()) ** 2).mean() ** 1.5


print('\nBandbegrenzt (k <= k_max), Spiegelpaare (phi2, 240) <-> (240 - phi2, 240), phi2 = 100..118°:')
for name, K, C, mu in cases:
    f = 14.0 if 'V3' in name else 10.0
    out = []
    for kmax in (3, 6, 9, 12):
        d = [fmin_bl(p, 240, K, C, mu, f, kmax)[0] - fmin_bl(240 - p, 240, K, C, mu, f, kmax)[0] for p in p2]
        g = [fmin_bl(p, 240, K, C, mu, f, kmax)[1] - fmin_bl(240 - p, 240, K, C, mu, f, kmax)[1] for p in p2]
        out.append(f'k_max={kmax}: max|dF_min| {np.abs(d).max()*1e3:7.3f} mN, max|d gamma1| {np.abs(g).max():.4f}')
    print(f'{name:>40}: ' + '; '.join(out))
