"""Gegenprüfung ENG-03/ENG-04: Hot-Spot (0°, 208,421°) – Fensterreihe, Randterm R, Quadraturrest Q.

Modus 'sa'      : halbanalytisch (exakte Zeitmittel), std-Start, 120 s: <N>-Mg = R exakt? Fensterreihe ab 5 s,
                  Einschwingzeit (Poincaré, Wiederkehr P1), Floquet des Endzustands.
Modus 'rk4 DT'  : eigene Schwerpunkt-RK4, 120 s: Linksrechteck-Mittel, RK4-gewichtet, R, Q je Fenster.
"""
import os
import sys, json
import numpy as np
import vk_model as m
import vk_sa as sa

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
P2, P3 = 0.0, 208.421
WINS = [(50, 150), (50, 550), (50, 1150), (300, 600), (300, 1000), (600, 1100), (200, 1200)]


def settle(PV, PZ, tol_v=1e-3, tol_z=1e-4):
    ok = (np.abs(PV[1:] - PV[:-1]) < tol_v) & (np.abs(PZ[1:] - PZ[:-1]) < tol_z)
    bad = np.where(~ok)[0]
    return (0 if bad.size == 0 else bad[-1] + 1) * m.T


def mode_sa(phi3=P3, tag=''):
    s = sa.SA(P2, phi3)
    R = s.run(-m.MG / m.K, 0.0, 0.0, 1200)
    L = []
    for c0, c1 in WINS:
        st = sa.stats(R, c0, c1)
        L.append(f'SA Fenster {c0*m.T:.0f}–{c1*m.T:.0f} s: <N>-Mg = {st["dF_ppm"]*m.MG*1e-3:+.4f} mN ({st["dF_ppm"]:+.1f} ppm), '
                 f'R = {st["R_ppm"]:+.1f} ppm, Rest {st["rest_N"]:+.1e} N, lam {st["lam"]:.4f} %, gamma1 {st["skew"]:.4f}, '
                 f'F_max {st["Fmax"]:.3f}')
    L.append(f'v_S(5 s) = {R["PS"][50]:+.4f}, v_S(15 s) = {R["PS"][150]:+.4f}, v_S(55 s) = {R["PS"][550]:+.4f}, '
             f'v_S(115 s) = {R["PS"][1150]:+.4f} m/s')
    L.append(f'Einschwingende (Wiederkehr P1, |dz\'|<1e-3, |dz|<1e-4): {settle(R["PV"], R["PZ"]):.1f} s; '
             f'streng (1e-8/1e-10): {settle(R["PV"], R["PZ"], 1e-8, 1e-10):.1f} s')
    x, mu, rr = sa.floquet(s, [R['PZ'][-1], R['PV'][-1]], 120.0, p=1)
    R2 = s.run(x[0], x[1], 0.0, 5)
    st = sa.stats(R2, 0, 5)
    L.append(f'Floquet P1-Orbit: |mu| = {", ".join(f"{abs(v):.4f}" for v in mu)}; Orbit lam {st["lam"]:.4f} %, '
             f'gamma1 {st["skew"]:.5f}, F_max {st["Fmax"]:.3f} N, v_S Zyklusbeginn {R2["PS"][0]:+.4f} m/s')
    txt = '\n'.join(L)
    print(txt)
    open(OUT + f'vk_hotspot_sa{tag}_ausgabe.txt', 'w').write(txt + '\n')


def mode_rk4(dt):
    import vk_rk4com as rk
    r = rk.run([P2], [P3], start='std', dt=dt, n_cyc=1200)
    L = [f'RK4-S dt = {dt*1e6:.1f} µs, Hot-Spot std']
    for c0, c1 in WINS:
        w = rk.window(r, c0, c1)
        L.append(f'  Fenster {c0*m.T:.0f}–{c1*m.T:.0f} s: Linksrechteck {w["dF_left_ppm"][0]*m.MG*1e-3:+.4f} mN '
                 f'({w["dF_left_ppm"][0]:+.1f} ppm), RK4-gew. {w["dF_rk4_ppm"][0]:+.2f} ppm, R {w["R_ppm"][0]:+.2f} ppm, '
                 f'Q {w["Q_ppm"][0]:+.2f} ppm, lam {w["lam"][0]:.3f}, gamma1 {w["skew"][0]:.4f}, F_max {w["Fmax"][0]:.3f}')
    L.append(f'  v_S(5 s) = {r["PS"][50,0]:+.4f}; Einschwingende (1e-3/1e-4): {settle(r["PV"][:,0], r["PZ"][:,0]):.1f} s')
    txt = '\n'.join(L)
    print(txt)
    open(OUT + f'vk_hotspot_rk4_{dt*1e6:g}us_ausgabe.txt', 'w').write(txt + '\n')


if __name__ == '__main__':
    if sys.argv[1] == 'sa':
        mode_sa(float(sys.argv[2]) if len(sys.argv) > 2 else P3, sys.argv[3] if len(sys.argv) > 3 else '')
    else:
        mode_rk4(float(sys.argv[2]) * 1e-6)
