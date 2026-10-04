"""Gegenprüfung ENG-09 (Wertebereich): Rasterpunkt (3,3) = (56,842°, 56,842°) im SA – Zustand, Periode, Floquet."""
import os
import numpy as np, vk_model as m, vk_sa as sa
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
p = round(3 * 360 / 19, 3)
L = []
s = sa.SA(p, p)
R = s.run(-m.MG / m.K, 0.0, 0.0, 400)
st = sa.stats(R, 300, 400)
per = sa.period(R, n_last=60, pmax=40, tol_v=1e-8, tol_z=1e-10)
L.append(f'SA ({p},{p}) std 30–40 s: lam {st["lam"]:.4f} %, gamma1 {st["skew"]:.4f}, F_max {st["Fmax"]:.3f} N, Periode {per[0]} ab {per[1]:.1f} s')
if per[0] > 0:
    x, mu, rr = sa.floquet(s, [R['PZ'][-1], R['PV'][-1]], 40.0, p=per[0])
    R2 = s.run(x[0], x[1], 0.0, 3 * per[0]); st2 = sa.stats(R2, 0, 3 * per[0])
    L.append(f'  Floquet P{per[0]}: |mu| = {", ".join(f"{abs(v):.4f}" for v in mu)}; Orbit lam {st2["lam"]:.4f} %, F_max {st2["Fmax"]:.3f} N, '
             f'A = {(st2["Fmax"]-m.MG)/m.MG:.3f}')
txt = '\n'.join(L); print(txt); open(OUT + 'vk_punkt33_ausgabe.txt', 'w').write(txt + '\n')
