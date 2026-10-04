#!/usr/bin/env python3
"""P3 / bewertung_a – B02 (neuer Kandidat Profilglätte): Wie viel der Resonanzempfindlichkeit des
ungebänderten F_min (Präreg §5.3(a), P2 AUS-14/AUS-17) stammt aus Profilharmonischen oberhalb k = 12,
und wie stark würde eine glattere Profilform (simuliert als Tiefpass auf P_k) sie verringern?

Modell: lineares Dauerkontaktmodell (code/linear_solver: profile_spectrum, transfer), Egg-Profil,
V1-Annahmen (P2 Tab. 2.1): mu*Hub wie 3 x 100 g, 8 mm; f = 10 Hz; K = 1,5e6 N/m; zeta = 0,02 / 0,05.
'Glättung' = Multiplikation der P_k mit exp(-(k/k0)^2) für k0 = 30, 15 (Annahme: Aktor- bzw.
Profilglättung wirkt wie ein glatter Tiefpass; das ersetzt keine konkrete C2-Profilauslegung).
Ausgabe: F_min(120°,240°) und F_min am Schnittrand (100°,240°), ΔF_Zelt, synchrones F_min,
jeweils ungebändert gegen starr, und der Anteil k > 12.
"""
import numpy as np
from linear_solver import profile_spectrum, transfer, c_for
from finesweep import MG, M

HUB_REF = 0.005 * (1 + 0.35 / 0.65)
mu = 0.3 / 0.65 * 0.008 / HUB_REF
P0, n = profile_spectrum('egg')
k = np.arange(P0.size)


def fmin(phi2, phi3, K, C, P, kmax=None):
    H, _ = transfer(K, C, P.size)
    comb = (1 + np.exp(-1j * k * np.radians(phi2)) + np.exp(-1j * k * np.radians(phi3))) / 3
    A = P * comb * H
    if kmax is not None:
        A = A.copy(); A[kmax + 1:] = 0
    N = MG + mu * M * np.fft.irfft(A, n)
    return N.min()


cut = np.arange(100.0, 140.0 + 1e-9, 2.0)
for label, filt in [('ideales Egg', np.ones_like(k, float)),
                    ('Tiefpass k0 = 30', np.exp(-(k / 30.0) ** 2)),
                    ('Tiefpass k0 = 15', np.exp(-(k / 15.0) ** 2))]:
    P = P0 * filt
    print(f'--- {label}: |P_k|/|P_1| bei k = 12/24: {abs(P[12])/abs(P[1]):.2e}/{abs(P[24])/abs(P[1]):.2e}')
    for name, K, C in [('starr', None, 0.0), ('zeta=0,05', 1.5e6, c_for(1.5e6, 0.05)), ('zeta=0,02', 1.5e6, c_for(1.5e6, 0.02))]:
        f120 = fmin(120, 240, K, C, P)
        f100 = fmin(100, 240, K, C, P)
        fsyn = fmin(0, 0, K, C, P)
        zelt = [fmin(p, 240, K, C, P) for p in cut]
        f120b = fmin(120, 240, K, C, P, 12)
        print(f'  {name:>10}: F_min(120) = {f120:.4f} N (k<=12: {f120b:.4f}), F_min(100) = {f100:.4f} N, '
              f'Spitze bei {cut[int(np.argmax(zelt))]:.0f}°, dF_Zelt = {max(zelt)-min(zelt):.4f} N, '
              f'synchron F_min = {fsyn:.4f} N (Reserve {fsyn/MG*100:.1f} % von Mg)')
