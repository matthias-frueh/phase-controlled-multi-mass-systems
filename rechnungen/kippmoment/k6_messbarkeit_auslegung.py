"""
k6_messbarkeit_auslegung.py – Befunde KM-08 (Auslegung je Zelle) und KM-11 (Messbarkeit).

Teil A – Messbarkeit: Signale am Triphasik-Punkt (Zellwechselamplitude, Summe, Moment) gegen
  (i) u_c ≤ 0,0327 N (PB1, Präreg A4/A8), (ii) weißes Zellrauschen einer DMS-Wägezelle mit 24-bit-ADC
  (ANNAHMEN, im Bestand keine Rauschdichte: 5-kg-Zelle, Kennwert 1 mV/V bzw. 2 mV/V, Speisung 5 V,
  Brücke 1 kΩ, eingangsbezogene Rauschdichte 15 bzw. 50 nV/√Hz, Rauschbandbreite f_s/2),
  (iii) systematische Fehler aus k4 (Verstärkung, Lage).
Teil B – Auslegung: Zellreserve min_j F_j / (M·g/3) für alle Lauftypen der Präreg (Einzelmodul, Paar,
  synchron, (0°,180°), Piloten, 21 Schnittpunkte) je Geometrie, starr und steif, μ = 0,462 und 0,4,
  f = 10/12/14 Hz; Vergleich mit Summe/3.
"""
import numpy as np
from km_modell import Geo, linear, rot_zerlegung, M, MG, F_HZ

R_C = 0.10
K_ST = 369518.0
C_ST = 2 * 0.02 * np.sqrt(K_ST * M)
U_C = 0.0327
F_STAT = MG / 3
kB, Temp = 1.380649e-23, 295.0

print('=== Teil A: Rauschmodell (Annahmen) ===')
F_FS = 5 * 9.80665
szen = []
for S_r in (1e-3, 2e-3):
    for e_adc in (15e-9, 50e-9):
        for fs in (2000.0, 3750.0):
            e_J = np.sqrt(4 * kB * Temp * 1e3)
            e_n = np.hypot(e_adc, e_J)
            sens = S_r * 5.0 / F_FS                       # V/N
            sig = e_n * np.sqrt(fs / 2) / sens           # N je Stichprobe
            szen.append((S_r, e_adc, fs, sig))
            print(f'Kennwert {S_r*1e3:.0f} mV/V, e_ADC {e_adc*1e9:4.0f} nV/√Hz, f_s {fs:5.0f} Hz: '
                  f'Empfindlichkeit {sens*1e6:6.1f} µV/N, σ_F je Stichprobe {sig*1e3:6.2f} mN')
print(f'(Brückenrauschen 1 kΩ: {np.sqrt(4*kB*Temp*1e3)*1e9:.2f} nV/√Hz; Bestand: PCMMFM-Fehlerbudget elektrisch '
      f'0,001–0,005 N, Gesamt-Beispiel σ_total ≈ 0,024 N, nicht bandbreitenbezogen)')

sig_lo, sig_hi = min(s[3] for s in szen), max(s[3] for s in szen)
T_a = 10.0
print(f'\nHarmonische aus einem Lauf (Fenster T_a = {T_a:.0f} s): σ_A = σ_F·√(2/N_s)')
for fs in (2000.0, 3750.0):
    Ns = T_a * fs
    print(f'  f_s = {fs:.0f} Hz, N_s = {Ns:.0f}: σ_A = {sig_lo*np.sqrt(2/Ns)*1e3:.4f} … {sig_hi*np.sqrt(2/Ns)*1e3:.4f} mN; '
          f'Moment (R_c = 100 mm, σ_M = σ_F·R_c·√(3/2)·√(2/N_s)): {sig_lo*R_C*np.sqrt(1.5)*np.sqrt(2/Ns)*1e6:.2f} … '
          f'{sig_hi*R_C*np.sqrt(1.5)*np.sqrt(2/Ns)*1e6:.2f} µN·m')

print('\nSignale am Triphasik-Punkt (linear) gegen u_c und Rauschen:')
for lab, K, C, mu, starr in (('STARR', None, None, 0.462, True), ('STEIF', K_ST, C_ST, 0.462, False),
                             ('STARR', None, None, 0.4, True), ('REF', 1e4, 16.0, 1.0, False)):
    for g, gk in (('G0', dict(R_m=R_C, dpsi_deg=0)), ('G60h', dict(R_m=R_C / 2, dpsi_deg=60))):
        geo = Geo(R_c=R_C, mu=mu, **gk)
        r = linear(geo, (0, 120, 240), K=K or 1.0, C=C or 0.0, starr=starr)
        Rp, Rm = rot_zerlegung(r['Mxk'], r['Myk'])
        A1, A2 = 2 * abs(r['Fk'][0, 1]), 2 * abs(r['Fk'][0, 2])
        N3 = 2 * abs(r['Nk'][3])
        pp_z = (r['F'][0].max() - r['F'][0].min())
        pp_N = r['N'].max() - r['N'].min()
        Ns = T_a * 2000
        sA = sig_hi * np.sqrt(2 / Ns)
        print(f'{lab:5s} μ={mu:5.3f} {g:4s}: Zelle SS {pp_z:.3f} N (A1 {A1:.3f}, A2 {A2:.3f} N) | Summe SS {pp_N:.3f} N '
              f'(A3 {N3:.3f} N) | Zelle/Summe SS {pp_z/pp_N:.2f} | A1/u_c = {A1/U_C:.0f}, A2/u_c = {A2/U_C:.0f} | '
              f'A1/σ_A(pessim.) = {A1/sA:.1e} | R+1 = {Rp[1]:.4f} N·m, R−2 = {Rm[2]:.4f} N·m')

print('\nAbtastrate nach Präreg A6, (π·k_max·f/f_s)²/2 ≤ 1e-3:')
for kmax in (2, 3, 5, 6, 9):
    print(f'  k_max = {kmax}: f_s ≥ {np.pi*kmax*F_HZ/np.sqrt(2e-3):.0f} Hz bei f = 10 Hz')

print('\n=== Teil B: Zellreserve min_j F_j/(M·g/3) je Lauftyp (linear, volles Spektrum) ===')
LAUFTYPEN = {'Einzelmodul 1': ((0, 0, 0), (1, 0, 0)), 'Paar Δ=0': ((0, 0, 0), (1, 1, 0)),
             'Paar Δ=120': ((0, 120, 0), (1, 1, 0)), 'Paar Δ=180': ((0, 180, 0), (1, 1, 0)),
             'synchron': ((0, 0, 0), (1, 1, 1)), '(0,180)': ((0, 0, 180), (1, 1, 1)),
             'Pilot 110/250': ((0, 110, 250), (1, 1, 1)), 'Pilot 130/230': ((0, 130, 230), (1, 1, 1)),
             'Pilot 110/252': ((0, 110, 252), (1, 1, 1))}
SCHNITT = [((0, p2, 240), (1, 1, 1)) for p2 in range(100, 141, 2)]
GEOS = {'G0': dict(R_m=R_C, dpsi_deg=0.0), 'G60': dict(R_m=R_C, dpsi_deg=60.0),
        'G0h': dict(R_m=R_C / 2, dpsi_deg=0.0), 'G60h': dict(R_m=R_C / 2, dpsi_deg=60.0),
        'Z': dict(R_m=1e-9, dpsi_deg=0.0)}


def reserve(geo, phi, hub, K, C, starr, f):
    r = linear(geo, phi, K=K or 1.0, C=C or 0.0, starr=starr, hub=hub, f_hz=f)
    return r['F'].min() / F_STAT, r['N'].min() / 3 / F_STAT


for lab, K, C, mu, starr in (('STARR', None, None, 0.462, True), ('STEIF', K_ST, C_ST, 0.462, False),
                             ('STARR', None, None, 0.4, True)):
    for f in (10.0, 12.0, 14.0):
        print(f'\n{lab} μ = {mu}, f = {f:.0f} Hz (Zelle | Summe/3), Schnitt = min über 21 Punkte:')
        hdr = '  Geometrie ' + ''.join(f'{k:>16s}' for k in list(LAUFTYPEN) + ['Schnitt'])
        print(hdr)
        for g, gk in GEOS.items():
            geo = Geo(R_c=R_C, mu=mu, **gk)
            vals = [reserve(geo, ph, hb, K, C, starr, f) for ph, hb in LAUFTYPEN.values()]
            sch = [reserve(geo, ph, hb, K, C, starr, f) for ph, hb in SCHNITT]
            vals.append((min(v[0] for v in sch), min(v[1] for v in sch)))
            print(f'  {g:9s} ' + ''.join(f'  {v[0]*100:5.1f}|{v[1]*100:5.1f} %' for v in vals))
print('\nPräreg §5.3(a): Reserve ≥ 25 % je Zelle. Z = alle Module im Zentrum (≙ Modell „Summe/3“).')
