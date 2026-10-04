"""
v1_eigenfrequenzen.py – Gegenprüfung KM-05 (Kipp-Eigenfrequenzen).
Weg: Massenmatrix in Zellkoordinaten (Formfunktionen, vf_modell.Geom), Eigenwerte von M_w⁻¹·(K/3)·I;
zusätzlich geschlossene Formel aus Hub-/Kippträgheit:
    f_Hub = √(K/M)/2π,  K_t = (K/3)·Σ y_j² = K R_c²/2,  J = M_f ρ_f² + Σ m_i Y_i² = (1−μ)Mρ_f² + μ M R_m²/2
    f_Kipp = √(K_t/J)/2π = f_Hub · R_c/(√2·ρ),  ρ² = J/M.
Außerdem: Bedingung für exakte Entkopplung der Zellen (M_w ∝ I) bei G0.
"""
import numpy as np
from vf_modell import Geom, M_TOT, K_REF, K_STEIF

R = 0.10


def analytisch(mu, R_m, rho_f, K):
    fH = np.sqrt(K / M_TOT) / (2 * np.pi)
    J = (1 - mu) * M_TOT * rho_f ** 2 + mu * M_TOT * R_m ** 2 / 2
    fK = np.sqrt(K * R ** 2 / 2 / J) / (2 * np.pi)
    return fH, fK


print('Fall               μ      Geo    ρ_f/R_c | f (numerisch, Zellkoord.) [Hz]      | f_Hub, f_Kipp analytisch | 2f/f_Kipp 3f/f_Kipp')
for lab, K in (('REF', K_REF), ('STEIF', K_STEIF)):
    for mu in (1.0, 0.462):
        for gname, Rm, psi0 in (('G0', R, 0.0), ('G60h', R / 2, 60.0)):
            for rr in ((0.35, 0.5, 0.7) if mu < 1 else (0.5,)):
                g = Geom(mu, R_c=R, R_m=Rm, psi0=psi0, rho_f=rr * R)
                fn = g.eig(K)
                fH, fK = analytisch(mu, Rm, rr * R, K)
                print(f'{lab:6s} {mu:5.3f} {gname:5s} {rr:4.2f}    | {fn[0]:8.3f} {fn[1]:8.3f} {fn[2]:8.3f} | '
                      f'{fH:8.3f} {fK:8.3f} | {20/fK:6.3f} {30/fK:6.3f}')

# Beispiel der Gruppe: Platte mit Radius 1,5·R_c (homogene Scheibe, ρ_f = 0,75 R_c), μ = 0,462, G0
fH, fK = analytisch(0.462, R, 0.75 * R, K_REF)
print(f'\nPlatte 1,5·R_c, μ = 0,462, G0: f_Kipp/f_Hub = {fK/fH:.4f}')

# Entkopplungsbedingung bei G0: M_w ∝ I ?
print('\nMassenmatrix in Zellkoordinaten (Einheit kg) – Entkopplung, wenn diagonal:')
for mu, rr in ((1.0, 0.5), (0.462, 0.5), (0.462, 1 / np.sqrt(2)), (0.2, 1 / np.sqrt(2))):
    g = Geom(mu, R_c=R, rho_f=rr * R)
    off = np.max(np.abs(g.Mw - np.diag(np.diag(g.Mw))))
    print(f'  μ = {mu:5.3f}, ρ_f/R_c = {rr:.4f}: diag = {np.round(np.diag(g.Mw), 6)}, max|offdiag| = {off:.2e} kg, '
          f'f = {np.round(g.eig(K_REF), 4)} Hz')
# Dämpfungsverhältnis Kippen
zeta = 16.0 / (2 * np.sqrt(K_REF * M_TOT))
g = Geom(0.462, R_c=R, rho_f=0.5 * R)
fH, fK = analytisch(0.462, R, 0.5 * R, K_REF)
J = (1 - 0.462) * M_TOT * (0.5 * R) ** 2 + 0.462 * M_TOT * R ** 2 / 2
zt = 16.0 * R ** 2 / 2 / (2 * np.sqrt(K_REF * R ** 2 / 2 * J))
print(f'\nζ_Hub = {zeta:.4f}; ζ_Kipp (REF μ = 0,462, ρ_f = R_c/2) = {zt:.4f}; ζ·f_Kipp/f_Hub = {zeta*fK/fH:.4f}')
