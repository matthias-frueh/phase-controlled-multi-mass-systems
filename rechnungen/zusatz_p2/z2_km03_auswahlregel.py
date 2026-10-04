"""z2_km03_auswahlregel.py - Gegenpruefung KM-03 (Auswahlregel Summe/Moment am Triphasik-Punkt).

Analytisch: Moment als komplexe Zahl m = Mx + i My = -i * sum_j F_j * (x_j + i y_j)  (Zellen)
           bzw. quasistatisch = -i * sum_i f_i(t) * R_m e^{i psi_i}  (Module, Lastverteilung exakt).
f_i(t) = sum_k c_k e^{ik w (t - tau_i)} + c.c.  =>  Koeffizient von e^{+ikwt} (links, gegen Uhrzeigersinn von oben):
S_k = sum_i e^{i psi_i} e^{-ik phi_i};  von e^{-ikwt} (rechts): S'_k = sum_i e^{i psi_i} e^{+ik phi_i}.
Numerisch: eigenes Modell zm (STARR und STEIF), Drehsinn ueber den Windungszaehler des k-Anteils.
"""
import numpy as np
import zm

phi = np.radians([0.0, 120.0, 240.0])
print('=== Analytische Faktoren (psi = Modulwinkel, phi = Phasen 0/120/240) ===')
for sinn in (+1, -1):
    psi = sinn * np.radians([0.0, 120.0, 240.0])
    print(f'Modulreihenfolge sinn = {sinn:+d}:  k | |sum e^-ikphi| | |S_k| links | |S\'_k| rechts')
    for k in range(1, 10):
        s = abs(np.exp(-1j * k * phi).sum())
        Sk = abs((np.exp(1j * psi) * np.exp(-1j * k * phi)).sum())
        Spk = abs((np.exp(1j * psi) * np.exp(1j * k * phi)).sum())
        print(f'   {k} | {s:6.3f} | {Sk:6.3f} | {Spk:6.3f}')

print('\n=== Eigenes lineares Modell: Harmonische von Summe, Zelle 1 und Moment (R+ links, R- rechts) ===')
for lab, K, C, mu in (('STARR', None, None, 0.462), ('STEIF', zm.K_ST, zm.C_ST, 0.462), ('REF', zm.K_REF, zm.C_REF, 1.0)):
    for sinn in (+1, -1):
        geo = zm.Geo(Rm=zm.R_C, psi0=0.0, mu=mu, sinn=sinn)
        g = zm.module_phasors(geo, (0, 120, 240), 9)
        F = zm.cell_phasors(geo, g, K, C)
        Mx, My = zm.moments(geo, F)
        print(f'{lab} mu={mu} sinn={sinn:+d}')
        for k in range(1, 10):
            Pp, Pm = zm.rot_components(Mx[k], My[k])
            print(f'   k={k}: 2|N_k| = {2*abs(F[:, k].sum()):.4f} N, 2|F_1,k| = {2*abs(F[0, k]):.4f} N, '
                  f'R+ = {abs(Pp):.5f}, R- = {abs(Pm):.5f} N m')

# Drehsinn direkt aus der Zeitreihe der k = 1- bzw. k = 2-Komponente (Windungszahl je Periode)
print('\n=== Drehsinn aus der Zeitreihe (STARR, sinn = +1): Windungszahl je Periode des k-Anteils ===')
geo = zm.Geo(Rm=zm.R_C, psi0=0.0, mu=0.462, sinn=+1)
g = zm.module_phasors(geo, (0, 120, 240), 9)
F = zm.cell_phasors(geo, g, None, None)
t = np.linspace(0, zm.T_CYC, 4001)
for k in (1, 2, 4, 5):
    Fk = np.zeros_like(F)
    Fk[:, k] = F[:, k]
    Ft = zm.synth(Fk, t)
    Mx, My = zm.moments(geo, Ft)
    ang = np.unwrap(np.arctan2(My, Mx))
    print(f'  k={k}: Windungen je Periode = {(ang[-1]-ang[0])/(2*np.pi):+.3f} (+ = gegen Uhrzeigersinn von oben)')

# Einzelzellkraft enthaelt alle Ordnungen: G0 quasistatisch ist T = Einheitsmatrix
geo = zm.Geo(Rm=zm.R_C, psi0=0.0, mu=0.462)
print(f'\nG0 quasistatisch: T = Bc^-1 Bm =\n{np.round(geo.T(0, None).real, 12)}')
# Quasistatische Lastverteilung allgemein: F_j = P [1/3 + 2 R_m/(3 R_c) cos(psi_i - psi_j)]
geo = zm.Geo(Rm=0.037, psi0=23.0, mu=0.462)
T = geo.T(0, None).real
psi_c = np.radians([0, 120, 240]); psi_m = np.radians(23 + np.array([0, 120, 240]))
Tf = 1/3 + 2*0.037/(3*zm.R_C)*np.cos(psi_m[None, :] - psi_c[:, None])
print(f'Formel 1/3 + 2R_m/(3R_c) cos(dpsi) gegen Gleichgewichtsloesung (R_m = 37 mm, psi0 = 23 Grad): max diff {np.abs(T-Tf).max():.1e}')
