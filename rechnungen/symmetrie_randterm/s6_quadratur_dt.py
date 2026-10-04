"""s6_quadratur_dt.py - Teil B, Aufgabe 6: Quadraturrest Q in Abhaengigkeit von dt und Quadratur.

Punkte: HS = (0, 208.421) Hot-Spot (Attraktor P1), S0 = (0, 0) synchron, L1 = (157.3, 264.0)
(lambda ~ 12 %), K1 = (110, 234) liftoff-frei.
Phase p1: dt = 50 us, Standardstart, 400 Perioden; Zustand bei t = 30 s als Neustart; letzte Periode
          als Zeitreihe (fuer v_S,max).
Phase p2 <dt>: Neustart bei t0 = 30 s mit dem p1-Zustand, 150 Perioden, Fenster = Perioden 50..149
          (t = 35..45 s).  Quadraturen: Linksrechteck N1 (Engine), Trapez TR, RK4-gewichtet.
          Aufsetzer werden protokolliert: theta = Bruchteil des Schritts bis z = 0 (lineare
          Interpolation), Sprung J = -C*zd (Daempfer).  Vorhersage des Sprung-Quadraturfehlers
          (Euler-Maclaurin, Sprung in Schritt mit Bruchteil theta):  Q_J = (1/N) sum J (theta - 1/2).
          Zweites Modell (RK4-Stufen, massgeblich): Q_RK = (1/N) sum (F_folge/2 + f1/2 - w_RK4) je Aufsetzer.
Ausgabe: s6_p1.npz, s6_p2_<dt_us>.json, s6_p2_<dt_us>_td.npz"""
import json
import sys
import time
import numpy as np
import sr_engine as se

PTS = [('HS', 0.0, 208.421), ('S0', 0.0, 0.0), ('L1', 157.3, 264.0), ('K1', 110.0, 234.0)]
P2 = [p[1] for p in PTS]; P3 = [p[2] for p in PTS]


def td_stats(o, ca, cb, j_point):
    td = o['td']
    if td.size == 0:
        return 0, 0.0, 0.0, [], 0.0, td
    m = (td[:, 2] == j_point) & (td[:, 0] >= ca) & (td[:, 0] < cb)
    ev = td[m]
    if ev.size == 0:
        return 0, 0.0, 0.0, [], 0.0, ev
    th = ev[:, 3] / (ev[:, 3] - ev[:, 5])
    J = -se.C_REF * ev[:, 4]
    # Modell 'RK4-Stufen': im Sprungschritt verteilt RK4 den Impuls als w = (f1+2f2+2f3+f4)/6
    # (~5J/6 fuer theta<1/2, ~J/6 fuer theta>1/2); Linksrechteck minus RK4 je Aufsetzer = F_folge/2 - w
    # (Telekopsumme der glatten Kontaktphase, Fluganfang F = 0) -> Q_RK = (1/N) sum (F_folge/2 - w + f1/2)
    q_rk = (ev[:, 9] / 2 - ev[:, 7] + ev[:, 8] / 2)
    return len(ev), float(np.mean(J)), float(np.sum(J * (th - 0.5))), th, float(np.sum(q_rk)), ev


if __name__ == '__main__':
    mode = sys.argv[1]
    tic = time.time()
    if mode == 'p1':
        o = se.run(P2, P3, 400, dt=5e-5, store_cycles=(399, 400), log_td=True)
        w = se.window(o, 300, 400)
        L = o['L']
        F = o['series']                                         # (L, n), letzte Periode
        vS = o['vcom'][399][None, :] + np.cumsum((F - se.MG) / se.M, axis=0) * o['dt']
        np.savez('s6_p1.npz', z300=o['z'][300], zd300=o['zd'][300], vS_last=vS, F_last=F,
                 vcom=o['vcom'], z=o['z'], zd=o['zd'])
        for j, (nm, a, b) in enumerate(PTS):
            print(f'{nm} ({a},{b}) p1 30-40 s: lambda {w["liftoff"][j]:.3f} %, dv_S {w["dv"][j]:+.2e} m/s, '
                  f'max|v_S| letzte Periode {np.max(np.abs(vS[:, j])):.4f} m/s, '
                  f'v_S(Zyklusbeginn) Streuung 30-40 s {np.ptp(o["vcom"][300:400, j]):.2e} m/s, '
                  f'F_max {w["F_max"][j]:.3f} N, F_min {w["F_min"][j]:.4f} N')
        print(f'Laufzeit {time.time() - tic:.0f} s')
    else:
        dt = float(mode)
        r0 = np.load('s6_p1.npz')
        o = se.run(P2, P3, 150, dt=dt, t0=30.0, z0=r0['z300'], zd0=r0['zd300'], log_td=True)
        w = se.window(o, 50, 150)
        N = 100 * o['L']
        res = {}
        evs = {}
        for j, (nm, a, b) in enumerate(PTS):
            n_td, Jm, SJ, th, SRK, ev = td_stats(o, 50, 150, j)
            evs[nm] = ev
            QJ = SJ / N
            r = dict(point=nm, phi2=a, phi3=b, dt=dt, N=N,
                     mean_N1=w['mean_N1'][j], mean_TR=w['mean_TR'][j], mean_RK4=w['mean_RK4'][j],
                     R_N=w['R'][j], dv=w['dv'][j],
                     Q_N1_ppm=(w['mean_N1'][j] - w['mean_RK4'][j]) / se.MG * 1e6,
                     Q_TR_ppm=(w['mean_TR'][j] - w['mean_RK4'][j]) / se.MG * 1e6,
                     QJ_pred_ppm=QJ / se.MG * 1e6,
                     Q_rest_ppm=(w['mean_N1'][j] - QJ - w['mean_RK4'][j]) / se.MG * 1e6,
                     QRK_pred_ppm=SRK / N / se.MG * 1e6,
                     QRK_rest_ppm=(w['mean_N1'][j] - SRK / N - w['mean_RK4'][j]) / se.MG * 1e6,
                     frac_theta_lt_half=float(np.mean(np.asarray(th) < 0.5)) if len(th) else float('nan'),
                     Q_bound_RK_ppm=(n_td * Jm / 3 / N) / se.MG * 1e6,
                     E_RK4_N=w['mean_RK4'][j] - se.MG - w['R'][j],
                     delta_N1_ppm=(w['mean_N1'][j] - se.MG) / se.MG * 1e6,
                     delta_RK4_ppm=(w['mean_RK4'][j] - se.MG) / se.MG * 1e6,
                     n_touchdowns=n_td, J_mean_N=Jm,
                     Q_bound_ppm=(n_td * Jm / 2 / N) / se.MG * 1e6,
                     theta_unique=sorted(set(np.round(th, 4).tolist()))[:6] if len(th) else [],
                     liftoff=w['liftoff'][j], skew=w['skew'][j], F_min=w['F_min'][j], F_max=w['F_max'][j],
                     absN1=abs(w['Nk'][j, 0]), absN2=abs(w['Nk'][j, 1]))
            res[nm] = r
            print(json.dumps(r))
        json.dump(res, open(f's6_p2_{dt * 1e6:g}us.json', 'w'), indent=1)
        np.savez(f's6_p2_{dt * 1e6:g}us_td.npz', **evs)
        print(f'Laufzeit {time.time() - tic:.0f} s')
