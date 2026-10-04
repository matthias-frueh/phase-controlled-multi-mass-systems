"""
k1_harmonische_auswahlregel.py – Befunde KM-03/KM-04 (Drehfeld-These exakt).

1. Harmonische der Egg-Profilbeschleunigung (Hub-Faktor 1, 10 Hz), Amplituden A_k = 2|c_k|.
2. Auswahlregel: geometrischer Phasenfaktor S_k = Σ_i e^{iψ_i}·e^{−ikφ_i} (links umlaufend) und
   S'_k = Σ_i e^{iψ_i}·e^{+ikφ_i} (rechts umlaufend) bei (0°, 120°, 240°) und ψ_i = 0°, 120°, 240°
   (sinn = +1) bzw. 0°, −120°, −240° (sinn = −1); Summenfaktor Σ_i e^{−ikφ_i}.
3. Moment am Triphasik-Punkt (quasistatisch, Module auf R_m): Betrag |M(t)| über einen Zyklus für
   Egg (volles Spektrum, k ≤ 6, k ≤ 3) und Sinus; Mittelwert des Momentvektors; Kontrolle der Formel
   |M| = (3/2)·m·A_1·R_m (P1, L4-026) für die Grundharmonische.
"""
import numpy as np
from km_modell import profil_c, Geo, linear, rot_zerlegung, M, MG, N_PER

np.set_printoptions(linewidth=160)
c = profil_c()
A = 2 * np.abs(c)
print('=== 1. Egg-Profilbeschleunigung, Harmonische (Hub-Faktor 1, f = 10 Hz) ===')
print(' k   A_k [m/s²]   arg c_k [°]   A_k/A_1')
for k in range(1, 13):
    print(f'{k:2d}  {A[k]:10.4f}   {np.degrees(np.angle(c[k])):9.2f}    {A[k]/A[1]:7.4f}')
rms_tot = np.sqrt(np.sum(2 * np.abs(c[1:])**2))
print(f'RMS gesamt {rms_tot:.4f} m/s²; Anteil Leistung k=1: {2*abs(c[1])**2/rms_tot**2:.4f}, k=2: '
      f'{2*abs(c[2])**2/rms_tot**2:.4f}, k≡0 mod 3: {np.sum(2*np.abs(c[3::3])**2)/rms_tot**2:.4f}')

print('\n=== 2. Auswahlregel bei (φ₁, φ₂, φ₃) = (0°, 120°, 240°) ===')
phi = np.radians([0, 120, 240])
for sinn in (+1, -1):
    psi = np.radians(sinn * np.array([0, 120, 240]))
    print(f'Geometrie sinn = {sinn:+d} (Module bei ψ = {np.degrees(psi).round().tolist()}°)')
    print(' k  |Σ e^{-ikφ}|  |S_k| (links)  |S\'_k| (rechts)')
    for k in range(1, 10):
        Sk = np.sum(np.exp(1j * psi) * np.exp(-1j * k * phi))
        Sk2 = np.sum(np.exp(1j * psi) * np.exp(+1j * k * phi))
        Ss = np.sum(np.exp(-1j * k * phi))
        print(f'{k:2d}   {abs(Ss):6.3f}       {abs(Sk):6.3f}         {abs(Sk2):6.3f}')

print('\n=== 3. Moment am Triphasik-Punkt, quasistatisch (starre Auflage), Module über den Zellen ===')
R = 0.10
for mu in (1.0, 0.462, 0.4):
    geo = Geo(R_c=R, mu=mu)
    m = geo.m[0]
    for lab, kmax, prof in (('Egg voll', None, 'egg'), ('Egg k≤6', 6, 'egg'), ('Egg k≤3', 3, 'egg'),
                            ('Egg k≤2', 2, 'egg'), ('Sinus', None, 'sinus')):
        r = linear(geo, (0, 120, 240), starr=True, k_max=kmax, profil=prof)
        Mabs = np.hypot(r['Mx'], r['My'])
        Rp, Rm = rot_zerlegung(r['Mxk'], r['Myk'])
        ang = np.unwrap(np.arctan2(r['My'], r['Mx']))
        umlauf = (ang[-1] - ang[0]) / (2 * np.pi)
        print(f'μ={mu:5.3f} {lab:9s}: |M| min/mittel/max = {Mabs.min():.5f}/{Mabs.mean():.5f}/{Mabs.max():.5f} N·m; '
              f'max/min = {Mabs.max()/max(Mabs.min(),1e-15):8.3f}; <Mx>,<My> = {r["Mx"].mean():.1e},{r["My"].mean():.1e}; '
              f'Netto-Umläufe/Zyklus {umlauf:+.3f}')
        if lab == 'Egg voll':
            print('      k :  R+ [N·m]   R- [N·m]   (3/2)·m·A_k·R_m   Summe 2|N_k| [N]   (R±: Radien der umlaufenden Kreise)')
            for k in range(1, 10):
                print(f'     {k:2d} : {Rp[k]:9.5f}  {Rm[k]:9.5f}   {1.5*m*A[k]*geo.R_m:9.5f}        {2*abs(r["Nk"][k]):8.5f}')
            # Periodizität von |M|: Spektrum von |M|
            S = np.abs(np.fft.rfft(Mabs)) / Mabs.size
            nz = [k for k in range(1, 13) if S[k] > 1e-6 * S[0]]
            print(f'      Harmonische von |M(t)| ≠ 0 (k ≤ 12): {nz}')
            print(f'      Summenkraft: N_max − N_min = {r["N"].max()-r["N"].min():.5f} N; '
                  f'Einzelzelle: F_max − F_min = {r["F"][0].max()-r["F"][0].min():.5f} N; F_min Zelle {r["F"].min():.5f} N '
                  f'(statisch {MG/3:.4f} N); Summe/3 min {r["N"].min()/3:.5f} N')

print('\nDrehsinn: R+ = links (gegen Uhrzeigersinn von oben, mathematisch positiv), R− = rechts.')
