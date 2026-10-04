"""
v1_referenz_einzelmodul.py – Gegenprüfung AUS-01 und AUS-02 mit eigenem Rechenweg:
  linear: exakte Zeitbereichslösung (vk_lib.System.periodic_linear, Schießverfahren, keine FFT);
  nichtlinear: ereignisgesteuerte, abschnittsweise exakte Lösung (vk_lib.System.simulate), λ = Flugzeitanteil.
Ausgabe: v1_referenz_einzelmodul_ausgabe.txt
"""
import time
import numpy as np
import vk_lib as vk

M, G = vk.M_REF, vk.G
MG = M * G
K, C, f, hub = vk.K_REF, vk.C_REF, vk.F_REF, vk.HUB_REF
out = []


def p(s=''):
    print(s, flush=True)
    out.append(s)


t0 = time.time()
fn = vk.fn_of(K)
p('=== AUS-01: Kennzahlen Referenzsatz (eigene Rechnung) ===')
p(f'f_n = sqrt(K/M)/(2π) = {fn:.4f} Hz; f/f_n = {f/fn:.4f}; 2f/f_n = {2*f/fn:.4f}; 3f/f_n = {3*f/fn:.4f}; '
  f'f_n/2 = {fn/2:.3f} Hz (Bedingung 3f ≤ f_n/2 verletzt um Faktor {3*f/(fn/2):.2f})')
for k in range(1, 5):
    w = 2 * np.pi * f * k
    H = (K + 1j * w * C) / (K - M * w ** 2 + 1j * w * C)
    p(f'  |H({k}ω)| = {abs(H):.3f}')
p(f'ε_ref = μ·π²·Hub·f²/(TH·g) = {vk.eps_of(1.0, hub, f):.5f}  (a_h = {vk.eps_of(1.0, hub, f)*G:.4f} m/s²)')
Fm = []
for a in vk.SECTION:
    s = vk.System((0, a, 240.0), (1, 1, 1), 1.0, hub, f, K, C)
    Fm.append(s.periodic_linear(nsamp=2000)['N'].min())
Fm = np.array(Fm)
i120 = 10
p(f'Schnitt φ₂ = 100…140° (φ₃ = 240°), Stichprobe 2000/Periode: F_min(120°) = {Fm[i120]:.6f} N, '
  f'F_min(100°) = {Fm[0]:.4f} N, F_min(140°) = {Fm[-1]:.4f} N, Maximum bei {vk.SECTION[Fm.argmax()]:.0f}°')
p(f'  2°-Sekanten 118→120 / 122→120: {(Fm[i120]-Fm[i120-1])/2:.4f} / {(Fm[i120]-Fm[i120+1])/2:.4f} N/°; '
  f'20°-Sekanten: {(Fm[i120]-Fm[0])/20:.4f} / {(Fm[i120]-Fm[-1])/20:.4f} N/°; ΔF_Zelt = {Fm.max()-Fm.min():.4f} N')
s = vk.System((0, 120, 240), (1, 1, 1), 1.0, hub, f, K, C)
Nf = s.periodic_linear(fine=200000)['N']
p(f'  F_min(120°) kontinuierlich (200 000/Periode): {Nf.min():.6f} N')

p('\n=== AUS-02: Einzelmodul beim Referenzsatz ===')
s1 = vk.System((0, 0, 0), (1, 0, 0), 1.0, hub, f, K, C)
r = s1.periodic_linear(fine=200000)
Fmin1, Fmax1 = r['N'].min(), r['N'].max()
xdyn = r['x'] + MG / K
p(f'linear (kontinuierlich): F_min = {Fmin1:.4f} N, F_max = {Fmax1:.3f} N, x_max = {r["x"].max()*1e3:.4f} mm')
s_c = MG / (MG - Fmin1)
s_r = 0.75 * MG / (MG - Fmin1)
s_x = (MG / K) / xdyn.max()
p(f'Grenzen (N − Mg und x + Mg/K linear im Hub): F_min = 0 bei s = {s_c:.4f}; 25-%-Reserve bei s = {s_r:.4f}; '
  f'x_max = 0 bei s = {s_x:.4f}')
p('nichtlinear, ereignisgesteuert exakt, Standardstart, 15 s, Fenster 5–15 s:')
for sh in (0.70, 0.755, 0.76, 0.80, 0.90, 1.00):
    sx = vk.System((0, 0, 0), (1, 0, 0), 1.0, sh * hub, f, K, C)
    o = sx.simulate(15.0, 5.0)
    p(f'  s = {sh:.3f}: λ = {o["lam"]:.3f} %, F_min = {o["F_min"]:.4f} N, F_max = {o["F_max"]:.3f} N, '
      f'Kontaktbeginne im Fenster {o["n_imp"]}')
sx = vk.System((0, 0, 0), (1, 0, 0), 1.0, hub, f, K, C)
o = sx.simulate(20.0, 16.0)
p(f'  s = 1,000, 20 s, Fenster letzte 4 s: λ = {o["lam"]:.3f} %')
o = sx.simulate(15.0, 5.0, h=2.5e-6)
p(f'  s = 1,000, Abtastschritt der Ereignissuche h/2: λ = {o["lam"]:.3f} %')
# Gleichheit Einzelmodul(μ) = synchron(μ/3)
a = vk.System((0, 0, 0), (1, 0, 0), 0.6, hub, f, 2.5e6, vk.zeta_to_C(0.05, 2.5e6)).periodic_linear()['N']
b = vk.System((0, 0, 0), (1, 1, 1), 0.2, hub, f, 2.5e6, vk.zeta_to_C(0.05, 2.5e6)).periodic_linear()['N']
p(f'Kontrolle Einzelmodul(μ=0,6) gegen synchron(μ=0,2): max|ΔN| = {np.abs(a-b).max():.2e} N')
p(f'Rechenzeit {time.time()-t0:.0f} s')
open('v1_referenz_einzelmodul_ausgabe.txt', 'w').write('\n'.join(out) + '\n')
