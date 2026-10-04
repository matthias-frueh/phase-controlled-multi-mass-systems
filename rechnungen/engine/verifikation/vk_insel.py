"""Gegenprüfung ENG-06 (und Teil ENG-05): Satelliteninsel (35°, 116°).

Modus 'sa'   : halbanalytischer Löser – std/imp/Orbitstart, Newton+Floquet beider Zustände, Stöße auf den
               Kontaktorbit (dz' = ±0,03 … ±0,30 m/s an Zyklusphase 0 und 0,5).
Modus 'rk4 DT': eigene Schwerpunkt-RK4 mit Schritt DT, 100 s, Starts std/imp/orb; Poincaré-Streuung 50–100 s.
"""
import os
import sys, json
import numpy as np
import vk_model as m
import vk_sa as sa
from vk_kontakt import N_series

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
P2, P3 = 35.0, 116.0


def fmt(st):
    return (f'lam {st["lam"]:.4f} %, gamma1 {st["skew"]:.5f}, F_min {st["Fmin"]:.4f}, F_max {st["Fmax"]:.3f} N, '
            f'Aufsetzer/Zyklus {st["td"]:.2f}')


def mode_sa():
    L = []
    s = sa.SA(P2, P3)
    _, zq, zdq = N_series(P2, P3, np.array([0.0, 0.05]))
    orb0 = (float(zq[0]), float(zdq[0]))
    res = {}
    for nm, (a, b) in {'std': (-m.MG / m.K, 0.0), 'imp': (-m.MG / m.K, -float(m.ebar_v(0.0, s.taus))),
                       'orb': orb0}.items():
        R = s.run(a, b, 0.0, 200)
        st = sa.stats(R, 150, 200)
        per = sa.period(R)
        L.append(f'SA {nm}: {fmt(st)}; Periode {per[0]}, Einschwingen {per[1]:.1f} s (Tol 1e-9 m/s)')
        res[nm] = dict(st, period=per[0], tset=per[1], x_end=[R['PZ'][-1], R['PV'][-1]])
    # Floquet beider Zustände
    for nm in ('std', 'orb'):
        x, mu, rr = sa.floquet(s, res[nm]['x_end'], 20.0, p=1)
        R = s.run(x[0], x[1], 0.0, 10)
        st = sa.stats(R, 0, 10)
        L.append(f'Floquet ({nm}-Zustand): Fixpunkt z={x[0]*1e3:.6f} mm, z\'={x[1]:.6f} m/s, |mu| = '
                 f'{", ".join(f"{abs(v):.4f}" for v in mu)}, Residuen {", ".join(f"{v:.0e}" for v in rr)}; Orbit: {fmt(st)}')
        res[nm]['mu'] = [abs(v) for v in mu]
        res[nm]['orbit'] = st
    # Stöße auf den Kontaktorbit
    kicks = [0.03, -0.03, 0.05, -0.05, 0.07, -0.07, 0.10, -0.10, 0.20, -0.20, 0.30, -0.30]
    kres = []
    for ph, (zz, vv) in ((0.0, (zq[0], zdq[0])), (0.5, (zq[1], zdq[1]))):
        t0 = 3.0 + ph * m.T
        for dv in kicks:
            R = s.run(float(zz), float(vv) + dv, t0, 150)
            st = sa.stats(R, 100, 150)
            kres.append(dict(phase=ph, dv=dv, lam=st['lam'], Fmax=st['Fmax']))
        L.append(f'Stöße Phase {ph}: ' + '; '.join(f'{k["dv"]:+.2f}: {k["lam"]:.2f} %' for k in kres if k['phase'] == ph))
    res['kicks'] = kres
    L.append(f'M*g*T = {m.MG*m.T:.4f} N*s; M*0.05 = {m.M*0.05:.4f}, M*0.10 = {m.M*0.10:.4f} N*s')
    txt = '\n'.join(L)
    print(txt)
    open(OUT + 'vk_insel_sa_ausgabe.txt', 'w').write(txt + '\n')
    json.dump(res, open(OUT + 'vk_insel_sa.json', 'w'), indent=1, default=float)


def mode_rk4(dt):
    import vk_rk4com as rk
    _, zq, zdq = N_series(P2, P3, np.array([0.0]))
    n = 1000
    rs = {}
    L = []
    taus = (0.0, float(m.tau_of(P2)), float(m.tau_of(P3)))
    z0 = np.array([-m.MG / m.K, -m.MG / m.K, zq[0]])
    v0 = np.array([0.0, -float(m.ebar_v(0.0, taus)), zdq[0]])
    r = rk.run([P2] * 3, [P3] * 3, start='user', dt=dt, n_cyc=n, z0=z0, v0=v0)
    w = rk.window(r, 500, 1000)
    for j, nm in enumerate(('std', 'imp', 'orb')):
        pv = r['PV'][500:1001, j]
        L.append(f'RK4-S dt={dt*1e6:.1f} µs {nm}: lam {w["lam"][j]:.4f} %, gamma1 {w["skew"][j]:.5f}, F_min {w["Fmin"][j]:.4f}, '
                 f'F_max {w["Fmax"][j]:.3f} N, Q {w["Q_ppm"][j]:+.2f} ppm, Poincaré-Streuung z\' (std) {pv.std():.2e} m/s, '
                 f'Spannweite {pv.max()-pv.min():.2e} m/s')
        rs[nm] = {k: float(v[j]) for k, v in w.items()}
        rs[nm]['pv_std'] = float(pv.std())
        rs[nm]['pv_range'] = float(pv.max() - pv.min())
    txt = '\n'.join(L)
    print(txt)
    open(OUT + f'vk_insel_rk4_{int(round(dt*1e6))}us_ausgabe.txt', 'w').write(txt + '\n')
    json.dump(rs, open(OUT + f'vk_insel_rk4_{int(round(dt*1e6))}us.json', 'w'), indent=1)


if __name__ == '__main__':
    if sys.argv[1] == 'sa':
        mode_sa()
    else:
        mode_rk4(float(sys.argv[2]))
