#!/usr/bin/env python3
"""
Gegenprüfung LB-01 (KC und Kennzahlen des Trägers, Linie B, fluid_drift_v2).

UNABHÄNGIGER RECHENWEG: geschlossene Formeln statt numerischer Integration der Skriptkurve.
  Linie-B-Egg (egg_vel, Skript Z. 66-71): Geschwindigkeits-Halbsinus,
    Schnellphase Dauer tf*T, Spitze V_FAST;  Langsamphase Dauer HOLD*T, Spitze V_SLOW = V_FAST*tf/HOLD.
  Weg eines Moduls in der Schnellphase:  s = V_FAST * tf*T * 2/pi  (= Hub, Spitze-Spitze).
  Träger: v_osc = -RATIO * (1/3) * sum_j egg_vel(t - tau_j)  ->  synchron: Spitze-Spitze = RATIO * s.
  Für beliebige Phasen wird der Hub über ein feines Raster (Mittelpunktsregel, N = 20000/Periode)
  berechnet, nur um das Maximum über das 13x13-Raster zu bestimmen (Kontrolle "synchron = größte Amplitude").
Parameter aus pcmms_fluid_drift_v2.py (Z. 44-57) als Quellenangabe abgeschrieben, nicht importiert.
Luft: rho = 1,2 kg/m^3, mu = 1,8e-5 Pa s (wie Gruppe; Annahme 20 °C).
"""
import numpy as np

# Quellparameter (pcmms_fluid_drift_v2.py Z. 44-57)
M_SHELL, M_ARM, N_ARMS = 0.6, 0.05, 3
M_TOT = M_SHELL + N_ARMS * M_ARM
RATIO = N_ARMS * M_ARM / M_TOT
F, HOLD, V_FAST = 10.0, 0.65, 0.06
T = 1.0 / F
TF = 1.0 - HOLD
V_SLOW = V_FAST * TF / HOLD
W = 2 * np.pi * F
AREA, CD = 0.03, 0.8
RHO_L, MU = 1.2, 1.8e-5
NU = MU / RHO_L

print("=" * 100)
print("vb1 – KC/Kennzahlen Linie B analytisch")
print("=" * 100)
s_mod = V_FAST * TF * T * 2 / np.pi
s_slow = V_SLOW * HOLD * T * 2 / np.pi
print(f"RATIO = {RATIO:.4f}, M_tot = {M_TOT} kg")
print(f"Modulweg Schnellphase {s_mod*1e3:.5f} mm, Langsamphase {s_slow*1e3:.5f} mm (müssen gleich sein)")
pp = RATIO * s_mod
a = pp / 2
Umax = RATIO * V_FAST
print(f"Träger synchron: Spitze-Spitze {pp*1e3:.5f} mm, a = pp/2 = {a*1e3:.5f} mm, U_max = {Umax*1e3:.4f} mm/s, "
      f"U_max/omega = {Umax/W*1e3:.4f} mm")

Ds = {"D = 0,2 m (Notiz)": 0.2, "D = sqrt(4A/pi)": np.sqrt(4 * AREA / np.pi), "D = sqrt(A)": np.sqrt(AREA)}
delta = np.sqrt(2 * NU / W)
for name, D in Ds.items():
    KCa = 2 * np.pi * a / D
    KCu = Umax * T / D
    Re = Umax * D / NU
    beta = F * D**2 / NU
    print(f"  {name:20s} D={D:.4f}: KC_a = 2 pi a/D = {KCa:.5f}, KC_U = U_max T/D = {KCu:.5f}, "
          f"Re = {Re:.1f}, beta = {beta:.4g}, beta_check Re/KC_U = {Re/KCu:.4g}")
print(f"  Notizwert mit a = 0,3 mm, D = 0,2 m: KC = {2*np.pi*0.3e-3/0.2:.5f}")
print(f"  delta = sqrt(2 nu/omega) = {delta*1e3:.4f} mm; delta/D(0,2) = {delta/0.2:.3e}; delta/a = {delta/a:.3f}; "
      f"Re_s = omega a^2/nu = {W*a**2/NU:.4f}")
print(f"  Wasser (nu = 1e-6): delta = {np.sqrt(2*1e-6/W)*1e3:.4f} mm")


# ---- Kontrolle: Hub des Trägers über das 13x13-Raster (Maximum bei synchron?) ----
def egg_vel(ph):
    ph = np.mod(ph, 1.0)
    return np.where(ph < TF, V_FAST * np.sin(np.pi * ph / TF), -V_SLOW * np.sin(np.pi * (ph - TF) / HOLD))


N = 20000
ph = (np.arange(N) + 0.5) / N           # Mittelpunktsregel
best = (0, None)
phis = np.linspace(0, 360, 13, endpoint=False)
amps = []
for p2 in phis:
    for p3 in phis:
        v = -RATIO * (egg_vel(ph) + egg_vel(ph - p2 / 360) + egg_vel(ph - p3 / 360)) / 3
        x = np.cumsum(v) * T / N
        A = 0.5 * (x.max() - x.min())
        amps.append(A)
        if A > best[0]:
            best = (A, (p2, p3), np.abs(v).max())
amps = np.array(amps)
print(f"  Raster 13x13: größte Trägeramplitude a = {best[0]*1e3:.5f} mm bei {best[1]}, U_max = {best[2]*1e3:.3f} mm/s; "
      f"kleinste a = {amps.min()*1e6:.3f} µm; Median {np.median(amps)*1e3:.4f} mm")
v = -RATIO * (egg_vel(ph) + egg_vel(ph - 1 / 3) + egg_vel(ph - 2 / 3)) / 3
x = np.cumsum(v) * T / N
At = 0.5 * (x.max() - x.min())
print(f"  Triphasik (120,240): a = {At*1e6:.3f} µm, KC_a(D=0,2) = {2*np.pi*At/0.2:.3e}")
