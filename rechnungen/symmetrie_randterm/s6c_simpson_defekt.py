"""s6c_simpson_defekt.py - E = N_RK4 - Mg - R als Simpson-Defekt der vorgegebenen Modulbeschleunigung:
im stationaeren Zustand gilt mean_RK4(F) = Mg + M * mean_Simpson(abar) + R, mit
mean_Simpson(abar) = (1/L) sum_j [abar(t_j) + 4 abar(t_j + dt/2) + abar(t_j + dt)]/6 ueber eine Periode."""
import json
import numpy as np
import sr_engine as se

pts = [('HS', 0.0, 208.421), ('S0', 0.0, 0.0), ('L1', 157.3, 264.0), ('K1', 110.0, 234.0), ('Tri', 120.0, 240.0)]
for dt in (5e-5, 2.5e-5, 1.25e-5, 6.25e-6):
    L = int(round(se.T_CYC / dt))
    t = 30.0 + np.arange(L) * dt
    out = []
    for nm, a, b in pts:
        tau2, tau3 = a / 360 * se.T_CYC, b / 360 * se.T_CYC
        A = lambda x: (se.z_egg_zdd(x) + se.z_egg_zdd(x - tau2) + se.z_egg_zdd(x - tau3)) / 3.0
        simp = np.mean((A(t) + 2 * A(t + 0.5 * dt) + 2 * A(t + 0.5 * dt) + A(t + dt)) / 6.0)
        out.append(f'{nm} {se.M * simp:+.3e}')
    js = json.load(open(f's6_p2_{dt * 1e6:g}us.json'))
    print(f'dt = {dt * 1e6:5.2f} us: M*mean_Simpson(abar) / N: ' + ', '.join(out) +
          '   | E aus Lauf: ' + ', '.join(f'{k} {v["E_RK4_N"]:+.3e}' for k, v in js.items()))
