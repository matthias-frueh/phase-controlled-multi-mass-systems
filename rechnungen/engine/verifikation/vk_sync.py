"""Gegenprüfung ENG-05: synchroner Punkt (0°, 0°) mit SA – Periode, Einschwingzeit, Floquet (P2)."""
import os
import numpy as np, vk_model as m, vk_sa as sa
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
L = []
s = sa.SA(0.0, 0.0)
for nm, v0 in (('std', 0.0), ('imp', -float(m.ebar_v(0.0, s.taus)))):
    R = s.run(-m.MG / m.K, v0, 0.0, 300)
    st = sa.stats(R, 200, 300)
    per = sa.period(R, n_last=60)
    L.append(f'SA (0,0) {nm}: lam {st["lam"]:.4f} %, gamma1 {st["skew"]:.4f}, F_max {st["Fmax"]:.3f}; Periode {per[0]} ab {per[1]:.1f} s (Tol 1e-9/1e-11)')
    if nm == 'std':
        x, mu, rr = sa.floquet(s, [R['PZ'][-1], R['PV'][-1]], 30.0, p=2)
        L.append(f'   Floquet P2: |mu| = {", ".join(f"{abs(v):.4f}" for v in mu)}; Residuen {rr[0]:.0e} -> {rr[-1]:.0e}')
        x1, mu1, rr1 = sa.floquet(s, [R['PZ'][-1], R['PV'][-1]], 30.0, p=1, iters=6)
        L.append(f'   Newton P1 (Kontrolle): Residuen {rr1[0]:.0e} -> {rr1[-1]:.0e}, |mu| = {", ".join(f"{abs(v):.3f}" for v in mu1)}')
txt = '\n'.join(L); print(txt); open(OUT + 'vk_sync_ausgabe.txt', 'w').write(txt + '\n')
