"""Gegenprüfung ENG-01: Koordinaten, Profilgeschwindigkeit und Anfangsimpuls des Standardstarts.

Eigener Rechenweg: e'(u) analytisch aus der Profilbeschleunigung (Integrationskonstante aus Periodizität
von e), Kontrolle durch numerische Quadratur der Engine-Beschleunigung (Trapez, 1e6 Stützstellen) und
Periodizitätsprüfung; v_S(0) = z'(0) + (1/3) sum e'(-tau_k) mit z'(0) = 0 (Standardstart).
Impulsbilanz mit dem halbanalytischen Löser (exakte Integrale).
"""
import os
import numpy as np
import vk_model as m
import vk_sa as sa

out = []
P = out.append
# 1) Analytische Spitzengeschwindigkeit
V0 = m.RTOP * np.pi / (m.THOLD * m.T)
P(f'e\'(0) = RTOP*pi/(THOLD*T) = {V0:.6f} m/s;  RBOT*pi/(TFAST*T) = {m.RBOT*np.pi/(m.TFAST*m.T):.6f} m/s (C1-Stetigkeit)')
# 2) Numerische Kontrolle: Engine-Beschleunigung (Formel aus pcmms_v3a z_egg_zdd) zweimal integrieren
n = 1_000_000
t = np.linspace(0, m.T, n + 1)
a = m.e_acc(t)
v = np.concatenate([[0.0], np.cumsum(0.5 * (a[1:] + a[:-1]) * np.diff(t))])
c1 = -np.trapezoid(v, t) / m.T        # Konstante so, dass Mittel der Geschwindigkeit 0 (e periodisch)
v = v + c1
P(f'numerisch: Integral a dt über Zyklus = {np.trapezoid(a, t):.3e} m/s (muss 0 sein); '
  f'v(0) mit periodischem e = {v[0]:.6f} m/s; max|v_num - e\'_analyt| = {np.max(np.abs(v - m.e_vel(t))):.2e}')
# 3) v_S(0) im Standardstart an den Punkten
pts = [(0, 0), (0, 208.421), (120, 240), (35, 116), (113.684, 227.368), (100, 240)]
for p2, p3 in pts:
    taus = (0.0, float(m.tau_of(p2)), float(m.tau_of(p3)))
    vs = float(m.ebar_v(0.0, taus))
    P(f'  v_S(0) bei ({p2}, {p3}) = {vs:+.4f} m/s')
vs00 = float(m.ebar_v(0.0, (0, 0, 0)))
P(f'(0,0): M*v = {m.M*vs00*1e3:.2f} mN*s; M*g*T = {m.MG*m.T*1e3:.2f} mN*s; Anteil {m.M*vs00/(m.MG*m.T)*100:.2f} %; '
  f'1/2 M v^2 = {0.5*m.M*vs00**2*1e3:.2f} mJ; (Mg)^2/(2K) = {m.MG**2/(2*m.K)*1e3:.3f} mJ')
# 4) 1°-Raster
p = np.arange(360.0)
P2, P3 = np.meshgrid(p, p, indexing='ij')
VS = (m.e_vel(0.0) + m.e_vel(-m.tau_of(P2)) + m.e_vel(-m.tau_of(P3))) / 3.0
P(f'1°-Raster: max {VS.max():+.4f}, min {VS.min():+.4f} (bei {np.unravel_index(VS.argmin(), VS.shape)}), '
  f'Median |v_S(0)| {np.median(np.abs(VS)):.4f} m/s, Mittel v_S(0) {VS.mean():+.2e}')
e1 = m.e_vel(-m.tau_of(p))
P(f'  Einzelmodul e\'(-tau) über tau: max {e1.max():.4f}, min {e1.min():.4f}; Minimum der Summe = (V0 + 2*min)/3 = {(V0+2*e1.min())/3:+.4f}')
# 5) Impulsbilanz mit SA: M*(V_S(t1)-V_S(t0)) = int (N - Mg) dt
for p2, p3 in [(0, 0), (0, 208.421), (120, 240)]:
    s = sa.SA(p2, p3)
    R = s.run(-m.MG / m.K, 0.0, 0.0, 12)
    I = R['I1'][2:12].sum() - m.MG * 10 * m.T
    dP = m.M * (R['PS'][12] - R['PS'][2])
    P(f'  Impulsbilanz SA ({p2},{p3}), Zyklen 2-12: int(N-Mg)dt = {I:+.6e} N*s, M*dV_S = {dP:+.6e}, Differenz {I-dP:+.1e}')
txt = '\n'.join(out)
print(txt)
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vk_impuls_ausgabe.txt'), 'w').write(txt + '\n')
