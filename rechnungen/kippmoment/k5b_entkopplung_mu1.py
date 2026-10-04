"""
k5b_entkopplung_mu1.py – Befund KM-07: Bei μ = 1 (masseloser Rahmen) und Modulen über den Zellen (G0) zerfällt
das 3-FG-Modell exakt in drei unabhängige Einmassenschwinger (Masse M/3, Steifigkeit K/3, Dämpfung C/3, je ein
Modul). Jede Zellkraft ist dann ein Drittel der Engine-Kontaktkraft bei synchroner Phasung (0°, 0°),
zeitverschoben um τ_j – auch mit Liftoff. Prüfung: Zelle 1 (Phase 0, gleicher Start) gegen finesweep (0°, 0°).
Zusätzlich: Wie stark streut die Summenkraft am Triphasik-Punkt zwischen Startbedingungen (Zelle 2, 3 starten an
anderer Profilphase)?
"""
import numpy as np
from scipy.stats import skew
import finesweep
from km_modell import Geo, rk4, DT, N_PER, MG

out, ser = finesweep.run([0.0], [0.0], store_series=True, series_len=int(10.0 / DT))
geo = Geo(R_c=0.10, mu=1.0)
r = rk4([geo], [(0, 120, 240)])
F = r['F'][:, 0, :]
Fe = ser[:, 0]
print(f'Engine (0°,0°): λ = {out["liftoff"][0]:.4f} %, F_max = {out["F_max"][0]:.4f} N, F_min = {out["F_min"][0]:.4f} N, '
      f'Schiefe {out["F_skew"][0]:.4f}')
print(f'3·Zelle 1 bei (0°,120°,240°): λ = {100*np.mean(F[:,0] < 1e-9):.4f} %, F_max = {3*F[:,0].max():.4f} N, '
      f'Schiefe {skew(F[:,0]):.4f}; max|3·F_1 − N_Engine(0,0)| = {np.max(np.abs(3*F[:,0]-Fe)):.3e} N')
for j in (1, 2):
    lam = 100 * np.mean(F[:, j] < 1e-9)
    # bester Zeitversatz (ganze Stichproben) zur Engine-Reihe
    sh = int(round(j * N_PER / 3))
    d = np.max(np.abs(3 * F[sh:, j] - Fe[:-sh]))
    print(f'Zelle {j+1}: λ = {lam:.4f} %, F_max·3 = {3*F[:,j].max():.4f} N, max|3·F_j(t) − N_Engine(t − τ_j)| = {d:.3e} N')
N = F.sum(1)
print(f'Summe (Triphasik, 3 Zellen): F_min {N.min():.4f} N, F_max {N.max():.4f} N, λ_Summe {100*np.mean(N<1e-9):.3f} %, '
      f'Schiefe {skew(N):.4f}  (Engine 1-FG am selben Punkt: F_min 5,3304 N, λ = 0)')
# Periodizität der Engine-Reihe (0,0)
for p in (1, 2, 3, 4, 5, 6):
    dev = np.max(np.abs(Fe[-p * N_PER - 5 * N_PER:-p * N_PER] - Fe[-5 * N_PER:]))
    print(f'Engine (0°,0°): max|N(t) − N(t − {p}T)| über die letzten 5 T = {dev:.3e} N')

# Punktweiser Vergleich ab t = 0 (ohne Burn-in), um Rundungsverstärkung von Modellfehlern zu trennen
import km_modell as _km
geo = Geo(R_c=0.10, mu=1.0)
r0 = rk4([geo], [(0, 120, 240)], T_sim=3.0, T_burn=0.0)
_save = (finesweep.T_SIM, finesweep.T_BURN, finesweep.N_STEPS, finesweep.N_BURN)
finesweep.N_STEPS, finesweep.N_BURN = int(3.0 / DT), 0
o0, s0 = finesweep.run([0.0], [0.0], store_series=True, series_len=int(3.0 / DT))
finesweep.N_STEPS, finesweep.N_BURN = _save[2], _save[3]
d = np.abs(3 * r0['F'][:, 0, 0] - s0[:, 0])
for tt in (0.1, 0.5, 1.0, 2.0, 3.0):
    n = int(round(tt / DT))
    print(f'ab t = 0: max|3·F_1 − N_Engine(0,0)| bis t = {tt:.1f} s: {d[:n].max():.3e} N')
