#!/usr/bin/env python3
"""P3 / bewertung_a – B07 (Kandidaten 62, 76, 50): Größenordnung der Terme im kinematischen
Impulsbilanz-Kanal  N_kin(t) = M*g + M*a_R(t) + sum_j m_j*a_j(t)  am V1-Arbeitspunkt.

a_R: Beschleunigung des Rahmens (Auflagerkoordinate), a_j: Modulbeschleunigung relativ zum Rahmen.
Im linearen 1-FG-Modell (Präreg A2.1) gilt N_k = H(k w) * R_k mit R_k = sum_j m_j a_j,k (starre Antwort),
also M*a_R,k = (H(k w) - 1) * R_k. Frage: Wie groß ist der Rahmenterm gegen die H1-Nachweisgrenze
(c*u_c ~ 1 mN bei Sensorrauschen, ~10-20 mN bei mechanischer Streuung; P2 STA-11, zusatz_p2 STA-10)?
Annahmen (P2 Tab. 2.1, V1): M = 0,65 kg, 3 x 100 g, Hub 8 mm, f = 10 Hz, K = 1,5e6 N/m, zeta = 0,05.
Profil Egg (code/finesweep.py), auf 8 mm skaliert. Ausgabe je Konfiguration: |R_k|, |M a_R,k|, Verhältnis.
"""
import numpy as np
from finesweep import z_egg_zdd, T_CYC, M, MG

HUB_REF = 0.005 * (1 + 0.35 / 0.65)
hub, m_mod, K, zeta, f = 0.008, 0.100, 1.5e6, 0.05, 10.0
C = 2 * zeta * np.sqrt(K * M)
n = 2000 * 8
t = np.arange(n) * (T_CYC / n)
a = z_egg_zdd(t) * hub / HUB_REF
P = np.fft.rfft(a) * 2 / n                     # Amplitudenkoeffizienten
P[0] = 0
k = np.arange(P.size)
w = 2 * np.pi * f * k
H = (K + 1j * w * C) / (K - M * w ** 2 + 1j * w * C)
print(f'f_n = {np.sqrt(K / M) / 2 / np.pi:.1f} Hz, rho = {f / (np.sqrt(K / M) / 2 / np.pi):.4f}, C = {C:.2f} N s/m')
for cfg in [(0, 0, 0), (0, 120, 240), (0, 100, 240), (0, 140, 240), ('einzel',)]:
    if cfg == ('einzel',):
        comb = np.ones(P.size)
        name = 'Einzelmodul'
    else:
        comb = sum(np.exp(-1j * k * np.radians(p)) for p in cfg)
        name = str(cfg)
    R = m_mod * P * comb                          # starre Antwort (Summe m_j a_j)
    Fr = (H - 1) * R                              # M * a_R
    print(f'{name:>14}: ' + ' | '.join(f'k={kk}: |R|={abs(R[kk])*1e3:7.2f} mN, |M a_R|={abs(Fr[kk])*1e3:6.3f} mN'
                                       for kk in (1, 2, 3, 6, 9)))
    # Zeitbereich: max |M a_R(t)| (Spitze) bis k = 12
    Fr_t = np.fft.irfft(np.where(k <= 12, Fr, 0) * n / 2, n)
    print(f'{"":>14}  max|M a_R(t)| (k <= 12) = {np.abs(Fr_t).max()*1e3:.3f} mN; '
          f'erforderliche relative Genauigkeit der Modulbeschleunigung für 1 mN auf N_1: '
          f'{(1e-3 / max(abs(R[1]), 1e-12))*100:.3f} %')
