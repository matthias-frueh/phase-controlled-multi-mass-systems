"""
v10_exakt_mehrstabil.py - Ist die Mehrstabilitaet aus SYM-04 physikalisch (nicht RK4-bedingt)?
Ereignisgesteuerte Integration (v_exakt) des S3-Bildes g4 von L4: (117,1; 87,7) Grad
  (a) Standardstart t0 = 0           (eigene RK4: lambda 75,80 %)
  (b) aequivalenter Start t0 = -tau_ref, phi_ref = 242,9 Grad  (eigene RK4: lambda 43,84 %)
Auswertung 15-20 s (lambda, gamma1, F_max) auf 5-us-Raster.
"""
import sys, time, numpy as np
import v_engine as ve, v_exakt as vx
case = sys.argv[1]
t0 = 0.0 if case == 'std' else -(242.9 / 360.0) * ve.T
t1 = time.time()
b = vx.Bahn(117.1, 87.7)
b.integriere(t0, -ve.MG / ve.K0, 0.0, 20.0)
tg = 15.0 + np.arange(1000000) * 5e-6
F = b.kraft(tg)
m, s = F.mean(), F.std()
print(f'L4:g4 (117.1, 87.7) {case} t0 = {t0:+.5f} s exakt [{time.time() - t1:.0f} s]: lambda {np.mean(F < 1e-9) * 100:.3f} %  '
      f'gamma1 {np.mean((F - m) ** 3) / s ** 3:+.4f}  F_max {F.max():.3f} N  <N> {b.impuls(15.0, 20.0) / 5:.6f} N')
