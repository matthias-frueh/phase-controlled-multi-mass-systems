"""v0_selbsttest.py – Selbsttest der Prüfbibliothek vk_lib gegen Repo-Engine/linear_solver (nur Abgleich)."""
import time, numpy as np
import vk_lib as vk
import linear_solver as ls
import finesweep as fs

MG = vk.M_REF * vk.G
# 1) linear exakt vs linear_solver an Referenzpunkten
for p2, p3 in [(120, 240), (118, 240), (122, 240), (100, 240), (140, 240), (113.684, 227.368)]:
    s = vk.System((0, p2, p3), (1, 1, 1), 1.0, vk.HUB_REF, 10.0, 1e4, 16.0)
    r = s.periodic_linear(nsamp=2000)
    rl = ls.solve(p2, p3)
    print(f'({p2},{p3}) exakt F_min {r["N"].min():.6f} F_max {r["N"].max():.6f} mean {r["N"].mean():.7f} '
          f'| linear_solver F_min_lin {rl["F_min_lin"][0]:.6f} F_max {rl["F_max"][0]:.6f}  per_err {r["per_err"]:.1e}')
# 2) FFT-Löser vs exakt, steif
s = vk.System((0, 0, 0), (1, 1, 1), 0.4615, 8e-3, 10.0, 1.5e6, vk.zeta_to_C(0.05, 1.5e6))
r = s.periodic_linear()
N = vk.fft_linear([(0, 0, 0)], [(1, 1, 1)], 0.4615, 8e-3, 10.0, 1.5e6, vk.zeta_to_C(0.05, 1.5e6))
print('V1 synchron exakt F_min %.6f F_max %.6f | FFT %.6f %.6f' % (r['N'].min(), r['N'].max(), N.min(), N.max()))
# 3) nichtlinear ereignisgesteuert vs finesweep an drei Punkten (15 s, Fenster 5..15 s)
t0 = time.time()
for p2, p3 in [(120, 240), (0, 0)]:
    s = vk.System((0, p2, p3), (1, 1, 1), 1.0, vk.HUB_REF, 10.0, 1e4, 16.0)
    o = s.simulate(15.0, 5.0)
    print(f'nichtlinear ({p2},{p3}): λ = {o["lam"]:.3f} %  F_min {o["F_min"]:.6f}  F_max {o["F_max"]:.4f}  ({time.time()-t0:.1f} s)')
