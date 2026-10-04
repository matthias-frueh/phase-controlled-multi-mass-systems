"""v3_kurztest.py – Kurztest: eigenes Zell-RK4 (μ=1, G0, T) gegen Engine finesweep (0°,0°) ab t = 0, 1 s."""
import numpy as np
import finesweep
from vf_modell import Geom, K_REF, C_REF
from v3_nichtlinear_zellen import rk4_zellen
g = Geom(1.0)
rec = rk4_zellen(np.linalg.inv(g.Mw)[None], g.Gw[None], (g.m[:, None] * g.Nm)[None], np.array([[0, 120, 240.]]),
                 K_REF, C_REF, (-3 * g.F0 / K_REF)[None], np.zeros((1, 3)), 50e-6, T_sim=1.0, T_burn=0.0)
finesweep.N_STEPS, finesweep.N_BURN = int(1.0 / 50e-6), 0
o, s = finesweep.run([0.0], [0.0], store_series=True, series_len=int(1.0 / 50e-6))
d = np.abs(3 * rec[:, 0, 0] - s[:, 0])
for tt in (0.1, 0.5, 1.0):
    print(f'bis {tt} s: max|3·F_1 − N_Engine(0,0)| = {d[:int(tt/50e-6)].max():.3e} N')
# bilateral-unabhängiger Plausibilitätstest: Summe der drei Zellen gegen Engine (120,240) in den ersten 0,3 s
o2, s2 = finesweep.run([120.0], [240.0], store_series=True, series_len=int(1.0 / 50e-6))
print(f'Summe 3 Zellen − Engine(120,240), erste 0,05 s: {np.abs(rec[:1000].sum(2)[:,0]-s2[:1000,0]).max():.3e} N (vor erstem Zell-Liftoff gleich?)')
lift = np.argmax(rec[:, 0, :].min(1) < 1e-9)
print(f'erster Zell-Liftoff bei t = {lift*50e-6:.4f} s')
