"""Gegenprüfung ENG-05: Jacobi-Matrix der Festschritt-Periodenabbildung (eigene RK4-S) gegen SA-Floquet.

Hypothese der Gruppe: Die Festschritt-Abbildung hat (lokal) Multiplikatoren |mu| > 1, obwohl der Orbit im
ereignisgenauen Löser stabil ist; Ursache: die Jacobi-Matrix eines glatten Stücks enthält die
Stoßzeit-Sensitivität nicht. Test: zentrale Differenzen mit Schrittweiten s*(1 mm, 0,1 m/s), s = 1e-10 … 1e-3.
Kleine s -> Stück-Jacobi-Matrix, große s -> 'effektive' Abbildung über viele Sprünge.
Punkte: Insel (35°, 116°) Hüpfzustand, Hot-Spot (0°, 208,421°).
"""
import os
import sys
import numpy as np
import vk_model as m
import vk_rk4com as rk
import vk_sa as sa

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')


def main(dt):
    L = [f'RK4-S dt = {dt*1e6:.1f} µs']
    for nm, (p2, p3) in {'Insel': (35.0, 116.0), 'HotSpot': (0.0, 208.421)}.items():
        s = sa.SA(p2, p3)
        R = s.run(-m.MG / m.K, 0.0, 0.0, 200)
        x, mu, _ = sa.floquet(s, [R['PZ'][-1], R['PV'][-1]], 20.0, p=1)
        L.append(f'{nm}: SA-Fixpunkt z = {x[0]*1e3:.6f} mm, z\' = {x[1]:.6f} m/s, |mu|_SA = {", ".join(f"{abs(v):.4f}" for v in mu)}')
        # RK4-S auf eigenen Attraktor laufen lassen (100 Zyklen ab SA-Fixpunkt)
        r = rk.run([p2], [p3], start='user', dt=dt, n_cyc=100, z0=x[0], v0=x[1])
        xr = np.array([r['PZ'][-1, 0], r['PV'][-1, 0]])
        pv = r['PV'][50:, 0]
        L.append(f'   RK4-S-Endzustand: z\' = {xr[1]:.6f}; Streuung z\' (Zyklen 50–100) std {pv.std():.2e}, '
                 f'Abstand zum SA-Fixpunkt {abs(xr[1]-x[1]):.2e} m/s')
        for sc in (1e-10, 1e-8, 1e-6, 1e-5, 1e-4, 1e-3):
            hz, hv = sc * 1e-3, sc * 1e-1
            Z0 = np.array([xr[0], xr[0] + hz, xr[0] - hz, xr[0], xr[0]])
            V0 = np.array([xr[1], xr[1], xr[1], xr[1] + hv, xr[1] - hv])
            rr = rk.run([p2] * 5, [p3] * 5, start='user', dt=dt, n_cyc=1, z0=Z0, v0=V0, t0_cyc=0)
            Pz, Pv = rr['PZ'][1], rr['PV'][1]
            J = np.array([[(Pz[1] - Pz[2]) / (2 * hz), (Pz[3] - Pz[4]) / (2 * hv)],
                          [(Pv[1] - Pv[2]) / (2 * hz), (Pv[3] - Pv[4]) / (2 * hv)]])
            ev = np.linalg.eigvals(J)
            L.append(f'   s = {sc:.0e}: |mu|_RK4 = {", ".join(f"{abs(v):.4f}" for v in ev)}')
    txt = '\n'.join(L)
    print(txt)
    open(OUT + f'vk_rk4map_{dt*1e6:g}us_ausgabe.txt', 'w').write(txt + '\n')


if __name__ == '__main__':
    main(float(sys.argv[1]) * 1e-6 if len(sys.argv) > 1 else 5e-5)
