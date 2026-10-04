"""z4_km11_messbarkeit.py - Gegenpruefung KM-11 (Messbarkeit Kippsignal gegen u_c und Zellrauschen).

Eigene Rechnung. Rauschannahmen wie KM-11 offengelegt ([A], nicht aus dem Bestand):
 5-kg-DMS-Zelle (Nennlast 5 kg * g), Kennwert 1 bzw. 2 mV/V, Speisung 5 V, Bruecke 1 kOhm (4kTR, 300 K),
 ADC eingangsbezogen 15 bzw. 50 nV/sqrt(Hz), Rauschbandbreite f_s/2, Fenster 10 s.
Analytisch: sigma_A = sigma_F*sqrt(2/N_s) = e_n/(S*sqrt(T_a)) -> unabhaengig von f_s.
"""
import numpy as np
import zm

kB, Temp = 1.380649e-23, 300.0
e_br = np.sqrt(4 * kB * Temp * 1000.0)
T_a = 10.0
print(f'Brueckenrauschen 1 kOhm: {e_br*1e9:.2f} nV/sqrt(Hz)')
rows = []
for kenn in (1e-3, 2e-3):
    S = kenn * 5.0 / (5.0 * zm.G)               # V/N
    for e_adc in (15e-9, 50e-9):
        e_n = np.hypot(e_br, e_adc)
        for fs in (2000.0, 3750.0):
            sF = e_n * np.sqrt(fs / 2) / S
            sA = sF * np.sqrt(2 / (T_a * fs))
            rows.append((kenn, e_adc, fs, sF, sA, e_n / (S * np.sqrt(T_a))))
            print(f' {kenn*1e3:.0f} mV/V, ADC {e_adc*1e9:.0f} nV, f_s {fs:.0f}: S = {S*1e6:.1f} uV/N, sigma_F = {sF*1e3:6.2f} mN, '
                  f'sigma_A = {sA*1e3:.4f} mN (analytisch e_n/(S sqrt T) = {e_n/(S*np.sqrt(T_a))*1e3:.4f} mN)')
sA_all = np.array([r[4] for r in rows])
print(f'sigma_F-Bereich {min(r[3] for r in rows)*1e3:.2f} ... {max(r[3] for r in rows)*1e3:.2f} mN; '
      f'sigma_A-Bereich (beide f_s) {sA_all.min()*1e3:.4f} ... {sA_all.max()*1e3:.4f} mN')
sM = sA_all * zm.R_C * np.sqrt(1.5)
print(f'Moment, Schaetzer wie KM-11 (sigma_A*R_c*sqrt(3/2)): {sM.min()*1e6:.2f} ... {sM.max()*1e6:.2f} uN m')
# Optimaler Schaetzer der gegenlaeufigen Komponente: P- = (1/N) sum m_n e^{+iwt_n}; Std von |P-| = sigma_Mx/sqrt(N)
# mit sigma_Mx = sigma_F * R_c*sqrt(3/2) je Stichprobe -> = sigma_A*R_c*sqrt(3/2)/sqrt(2)
sMopt = sM / np.sqrt(2)

geo = zm.Geo(Rm=zm.R_C, psi0=0.0, mu=0.462)
g = zm.module_phasors(geo, (0, 120, 240), 400)
F = zm.cell_phasors(geo, g, None, None)
t = np.arange(4000) * zm.T_CYC / 4000
Ft = zm.synth(F, t)
N = Ft.sum(0)
print(f'\nSTARR mu=0.462 G0, Triphasik: Zelle A1 = {2*abs(F[0,1]):.4f} N, A2 = {2*abs(F[0,2]):.4f} N; '
      f'u_c = 0.0327 N -> A1/u_c = {2*abs(F[0,1])/0.0327:.1f}, A2/u_c = {2*abs(F[0,2])/0.0327:.1f}')
print(f'  Zelle SS {np.ptp(Ft[0]):.4f} N, Summe SS {np.ptp(N):.4f} N, Verhaeltnis {np.ptp(Ft[0])/np.ptp(N):.3f}')
Mx, My = zm.moments(geo, F)
Pp1, Pm1 = zm.rot_components(Mx[1], My[1])
Pp2, Pm2 = zm.rot_components(Mx[2], My[2])
print(f'  R+1 = {abs(Pp1):.5f} N m, R-2 = {abs(Pm2):.5f} N m; A1/sigma_A = {2*abs(F[0,1])/sA_all.max():.0f} ... {2*abs(F[0,1])/sA_all.min():.0f}')
geo2 = zm.Geo(Rm=zm.R_C, psi0=0.0, mu=0.462, masses=geo.m * np.array([1, 1.01, 1]))
geo2.Mf, geo2.Jf = geo.Mf, geo.Jf
g2 = zm.module_phasors(geo2, (0, 120, 240), 2)
F2 = zm.cell_phasors(geo2, g2, None, None)
Mx2, My2 = zm.moments(geo, F2)
_, Rm1 = zm.rot_components(Mx2[1], My2[1])
print(f'  Masse M2 +1 %: R-1 = {abs(Rm1):.3e} N m; SNR (Schaetzer KM-11) {abs(Rm1)/sM.max():.0f} ... {abs(Rm1)/sM.min():.0f}; '
      f'SNR (optimaler Schaetzer) {abs(Rm1)/sMopt.max():.0f} ... {abs(Rm1)/sMopt.min():.0f}')
print(f'  Leckage in N1 bei Zellverstaerkung +1 %: 2|dN1| = {0.01*2*abs(F[1,1]):.4f} N')

for k in (2, 3, 5, 9):
    print(f'A6: k_max = {k}: f_s >= {np.pi*k*zm.F_HZ/np.sqrt(2e-3):.0f} Hz (f = 10 Hz); bei 12 Hz {np.pi*k*12/np.sqrt(2e-3):.0f} Hz')

# Zelllage 1 mm radial (Zelle 2), Momentbildung mit nominaler Lage: Gegenkomponente R-1/R+1
geo_n = zm.Geo(Rm=zm.R_C, psi0=0.0, mu=0.462)
a2 = np.radians(120)
geo_t = zm.Geo(Rm=zm.R_C, psi0=0.0, mu=0.462, cell_shift=[[0, 0], [1e-3*np.cos(a2), 1e-3*np.sin(a2)], [0, 0]])
for lab, gt in (('nominal', geo_n), ('Zelle 2 radial +1 mm', geo_t)):
    gg = zm.module_phasors(gt, (0, 120, 240), 2)
    FF = zm.cell_phasors(gt, gg, None, None)
    mx, my = zm.moments(geo_n, FF)
    pp, pm = zm.rot_components(mx[1], my[1])
    print(f'Ellipse k=1 ({lab}, Momente mit nominaler Lage): R-1/R+1 = {abs(pm)/abs(pp):.5f}')
print(f'Vergleich Masse M2 +1 %: R-1/R+1 = {abs(Rm1)/abs(Pp1):.5f} (= eps/3 = {0.01/3:.5f})')
