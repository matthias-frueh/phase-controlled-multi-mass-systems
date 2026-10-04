"""P2/engine – Aufgabe 1: Koordinaten der Engine und Impulskonsistenz des Standardstarts.

Herleitung (aus der Bewegungsgleichung in pcmms_v3a_phasen_sweep.py, Kopf und rhs()):
  M z̈ = -M g + N(z, ż) - (M/3) sum_k ë(t - tau_k)
  z ist die Lage des masselosen Rahmens (Auflagerpunkt; Feder eingedrückt für z < 0), die drei Module
  (je M/3) sitzen relativ zum Rahmen bei e(t - tau_k). Mit z_S = z + (1/3) sum_k e(t - tau_k) folgt
  M z̈_S = -M g + N  (Impulssatz für den Schwerpunkt; der Rahmen trägt keine Masse, mu = 1).
  Standardstart z(0) = -Mg/K, ż(0) = 0  ->  v_S(0) = (1/3) sum_k e'(-tau_k)  (Anfangsimpuls M v_S(0)).

Prüfungen:
  1. v_S(0) an den P1-Punkten (L2-004) und Maximum über die Phasenebene.
  2. Numerischer Nachweis der Schwerpunktdefinition: M (v_S(t2) - v_S(t1)) = ∫ (N - Mg) dt (RK4-gewichtet)
     über 10 Zyklen an drei Punkten.
  3. Auf dem 19x19-Raster: v_S(0) gegen den Zustand, in dem die Engine landet (lambda aus der CSV), für die
     Bahnen mit Mehrdeutigkeit.
"""
import os
import numpy as np
import pandas as pd
import eng

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
print(f'Profil: Spitzengeschwindigkeit e\'(0) = RTOP*pi/(THOLD*T) = {eng.VPK:.5f} m/s; '
      f'e\'(Ende Halteast) = {float(eng.egg_v(0.065 - 1e-12)):.5f}, e\'(Anfang schneller Ast) = {float(eng.egg_v(0.065)):.5f} m/s (C1-stetig)')
pts = [(0, 0), (0, 208.421), (120, 240), (35, 116), (113.684, 227.368), (100, 240)]
for a, b in pts:
    t2, t3 = eng.taus(a, b)
    v = float(eng.v_modules(0.0, t2, t3))
    print(f'  ({a:7.3f}°, {b:7.3f}°): v_S(0) Standardstart = {v:+.4f} m/s, Anfangsimpuls M v_S = {eng.M * v * 1e3:+.1f} mN·s '
          f'({eng.M * v / (eng.MG * eng.T_CYC) * 100:+.1f} % des Gewichtsimpulses je Zyklus); '
          f'kinetische Energie 1/2 M v^2 = {0.5 * eng.M * v**2 * 1e3:.3f} mJ')
E_stat = 0.5 * eng.K * (eng.MG / eng.K)**2
print(f'  Vergleich: Federenergie der statischen Einfederung 1/2 K (Mg/K)^2 = {E_stat * 1e3:.3f} mJ; '
      f'Abhebeschwelle (ungedämpft) |v| > g/omega_n = {eng.G / np.sqrt(eng.K / eng.M):.4f} m/s')
g = np.arange(0, 360, 1.0)
P2, P3 = np.meshgrid(g, g, indexing='ij')
V = eng.v_modules(0.0, *eng.taus(P2, P3))
print(f'  1°-Raster: max v_S(0) = {V.max():+.4f} m/s bei {np.unravel_index(V.argmax(), V.shape)}°, '
      f'min {V.min():+.4f} m/s; Median |v_S(0)| = {np.median(np.abs(V)):.4f} m/s')

# 2. Impulsbilanz des Schwerpunkts
a = np.array([0.0, 0.0, 120.0]); b = np.array([0.0, 208.421, 240.0])
z0, v0 = eng.start_std(3)
r = eng.integrate(a, b, z0, v0, n_cyc=12)
c0, c1 = 2, 12
imp = (r['SW'][c0:c1].sum(0)) * eng.DT                     # ∫(N_RK4 - Mg) dt
dP = eng.M * (r['PS'][c1] - r['PS'][c0])
print('Impulsbilanz Schwerpunkt über Zyklen 2..12 (Standardstart):')
for k in range(3):
    print(f'  ({a[k]:.0f},{b[k]:.3f}): M Δv_S = {dP[k]:+.9f} N·s, ∫(N_RK4 - Mg) dt = {imp[k]:+.9f} N·s, '
          f'Differenz {dP[k] - imp[k]:+.2e} N·s; Linksrechteck ∫(N1 - Mg) = {r["S1"][c0:c1].sum(0)[k] * eng.DT:+.9f}')

# 3. 19x19: v_S(0) gegen erreichten Zustand
df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data/sweep_19x19.csv'))
df['vS0'] = eng.v_modules(0.0, *eng.taus(df.phi2_deg.values, df.phi3_deg.values))
bt = pd.read_csv(OUT + 'sym_bahnen_19x19.csv')
multi = bt[bt.d_lam > 3.0]
rows = []
for _, o in multi.iterrows():
    for p in o.punkte.split():
        i, j = map(int, p.strip('()').split(','))
        r_ = df.iloc[((np.round(df.phi2_deg / (360 / 19)) % 19 == i) & (np.round(df.phi3_deg / (360 / 19)) % 19 == j)).values].iloc[0]
        rows.append(dict(bahn=o.bahn, i2=i, i3=j, phi2=r_.phi2_deg, phi3=r_.phi3_deg, lam=r_.liftoff, vS0=r_.vS0))
mt = pd.DataFrame(rows)
mt['hochzustand'] = mt.lam > 74.0
print('Bahnen mit Spannweite lambda > 3 %-Pkt: v_S(0) der Mitglieder im Hochzustand (lambda > 74 %) und sonst:')
print(mt.to_string(index=False))
hi, lo = mt[mt.hochzustand], mt[~mt.hochzustand]
print(f'  Hochzustand: n = {len(hi)}, v_S(0) Mittel {hi.vS0.mean():+.4f}, Spanne [{hi.vS0.min():+.4f}, {hi.vS0.max():+.4f}] m/s')
print(f'  übrige:      n = {len(lo)}, v_S(0) Mittel {lo.vS0.mean():+.4f}, Spanne [{lo.vS0.min():+.4f}, {lo.vS0.max():+.4f}] m/s')
allhi = df[df.liftoff > 74.0]
print(f'  ganzes Raster: {len(allhi)} Punkte mit lambda > 74 %, v_S(0) in [{allhi.vS0.min():+.4f}, {allhi.vS0.max():+.4f}]; '
      f'Punkte mit v_S(0) > 0,1 m/s: {int((df.vS0 > 0.1).sum())}, davon lambda > 74 %: {int(((df.vS0 > 0.1) & (df.liftoff > 74)).sum())}')
mt.to_csv(OUT + 'impuls_start_bahnen.csv', index=False)
