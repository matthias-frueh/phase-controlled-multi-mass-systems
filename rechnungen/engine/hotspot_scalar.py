"""P2/engine – Hot-Spot (0°, 208,421°) mit der skalaren Referenz-Engine (pcmms_v3a_phasen_sweep.rhs,
math.sin – dieselbe Arithmetik, mit der data/sweep_19x19.csv erzeugt wurde), 120 s, Standardstart.

Prüft: CSV-Reproduktion (5–15 s), Einschwingzeit und Periode (Poincaré je Zyklus), Randterm/Quadratur,
Fensterreihe ab 5 s (10/50/110 s; L4-038), Δż zwischen 5 s und Fensterende (L1b-041), δ nach dem
Einschwingen (AP v2.4 §8.3: −2 ppm; L2-044: δ = −64,7, R = −2,0, Q = −62,8 ppm ab 18,8 s).
Zusätzlich dieselbe Prüfung mit Δt/2 (eigene skalare Kopie der rhs mit DT/2).
Aufruf: python3 hotspot_scalar.py [phi2 phi3 T_s]
"""
import os
import sys, math, time, json
import numpy as np
import pcmms_v3a_phasen_sweep as s

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
phi2 = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
phi3 = float(sys.argv[2]) if len(sys.argv) > 2 else 208.421
T_SIM = float(sys.argv[3]) if len(sys.argv) > 3 else 120.0


def egg_v(t):
    ph = (t % s.T_CYC) / s.T_CYC
    if ph < s.THOLD:
        return s.RTOP * math.pi / (s.THOLD * s.T_CYC) * math.cos(math.pi * ph / s.THOLD)
    return -s.RBOT * math.pi / (s.TFAST * s.T_CYC) * math.cos(math.pi * (ph - s.THOLD) / s.TFAST)


def run(dt):
    tau2 = math.radians(phi2) / (2 * math.pi * s.F_HZ)
    tau3 = math.radians(phi3) / (2 * math.pi * s.F_HZ)
    n_per = round(s.T_CYC / dt)
    n_cyc = int(round(T_SIM / s.T_CYC))
    rhs = s.rhs
    z, zd = -s.MG / s.K, 0.0
    PZ, PV, PS = [], [], []
    S1, SW, S2, S3, LO, MX = (np.zeros(n_cyc) for _ in range(6))
    h = dt
    for c in range(n_cyc):
        t = c * n_per * h
        PZ.append(z); PV.append(zd); PS.append(zd + (egg_v(t) + egg_v(t - tau2) + egg_v(t - tau3)) / 3)
        s1 = s2 = s3 = sw = 0.0; lo = 0; mx = 0.0
        for k in range(n_per):
            t = (c * n_per + k) * h
            k1z, k1d, f1 = rhs(z, zd, t, tau2, tau3)
            k2z, k2d, f2 = rhs(z + 0.5 * h * k1z, zd + 0.5 * h * k1d, t + 0.5 * h, tau2, tau3)
            k3z, k3d, f3 = rhs(z + 0.5 * h * k2z, zd + 0.5 * h * k2d, t + 0.5 * h, tau2, tau3)
            k4z, k4d, f4 = rhs(z + h * k3z, zd + h * k3d, t + h, tau2, tau3)
            z = z + h * (k1z + 2 * k2z + 2 * k3z + k4z) / 6.0
            zd = zd + h * (k1d + 2 * k2d + 2 * k3d + k4d) / 6.0
            d = f1 - s.MG
            s1 += d; s2 += d * d; s3 += d * d * d
            sw += (f1 + 2 * f2 + 2 * f3 + f4) / 6.0 - s.MG
            lo += f1 < 1e-9
            mx = f1 if f1 > mx else mx
        S1[c], S2[c], S3[c], SW[c], LO[c], MX[c] = s1, s2, s3, sw, lo, mx
    t = n_cyc * n_per * h
    PZ.append(z); PV.append(zd); PS.append(zd + (egg_v(t) + egg_v(t - tau2) + egg_v(t - tau3)) / 3)
    return dict(PZ=np.array(PZ), PV=np.array(PV), PS=np.array(PS), S1=S1, S2=S2, S3=S3, SW=SW, LO=LO, MX=MX,
                n_per=n_per, dt=dt)


def win(r, c0, c1):
    Nn = (c1 - c0) * r['n_per']
    A1, A2, A3 = r['S1'][c0:c1].sum() / Nn, r['S2'][c0:c1].sum() / Nn, r['S3'][c0:c1].sum() / Nn
    m2 = A2 - A1**2; m3 = A3 - 3 * A1 * A2 + 2 * A1**3
    W = r['SW'][c0:c1].sum() / Nn
    Tw = (c1 - c0) * s.T_CYC
    R = s.M * (r['PS'][c1] - r['PS'][c0]) / Tw
    return dict(T_w=Tw, dF_mN=A1 * 1e3, delta_ppm=A1 / s.MG * 1e6, R_ppm=R / s.MG * 1e6,
                Q_ppm=(A1 - W) / s.MG * 1e6, rk4_minus_R_N=W - R, skew=m3 / m2**1.5,
                lam=r['LO'][c0:c1].sum() / Nn * 100, Fmax=r['MX'][c0:c1].max(),
                dzd=r['PV'][c1] - r['PV'][c0])


def settle(r, p_max=30, tol_v=1e-6, tol_z=1e-8, n_last=100):
    v, z = r['PV'], r['PZ']
    n = v.size - 1
    for p in range(1, p_max + 1):
        idx = np.arange(n - n_last - p + 1, n - p + 1)
        if np.max(np.abs(v[idx + p] - v[idx])) < tol_v and np.max(np.abs(z[idx + p] - z[idx])) < tol_z:
            ok = (np.abs(v[p:] - v[:-p]) < tol_v) & (np.abs(z[p:] - z[:-p]) < tol_z)
            bad = np.where(~ok)[0]
            return p, (0 if bad.size == 0 else bad[-1] + 1) * s.T_CYC
    return -1, float('nan')


if __name__ == '__main__':
    res = {}
    for dt in (s.DT, s.DT / 2):
        tic = time.time()
        r = run(dt)
        el = time.time() - tic
        ps, ts = settle(r)
        pl, tl = settle(r, tol_v=1e-3, tol_z=1e-4, n_last=20)
        print(f'=== ({phi2}, {phi3}) skalare Engine, dt = {dt * 1e6:.0f} µs, {T_SIM:.0f} s ({el:.0f} s Rechenzeit)')
        print(f'  Periode streng p = {ps}, eingeschwungen ab t = {ts:.1f} s; locker (1e-3 m/s, 1e-4 m) p = {pl}, ab {tl:.1f} s')
        out = {}
        for name, (c0, c1) in {'5-15 s (Engine/CSV)': (50, 150), '5-55 s': (50, 550), '5-115 s': (50, 1150),
                               '20-30 s': (200, 300), '18.8-28.8 s': (188, 288), '30-40 s': (300, 400),
                               '60-120 s': (600, 1200), '100-110 s': (1000, 1100)}.items():
            if c1 >= r['PV'].size:
                continue
            w = win(r, c0, c1)
            out[name] = w
            print(f'  {name:20s} ⟨F⟩−Mg = {w["dF_mN"]:+9.4f} mN ({w["delta_ppm"]:+9.1f} ppm), R = {w["R_ppm"]:+9.1f} ppm, '
                  f'Q = {w["Q_ppm"]:+7.2f} ppm, N_RK4−Mg−R = {w["rk4_minus_R_N"]:+.1e} N, λ = {w["lam"]:.4f} %, '
                  f'γ1 = {w["skew"]:.4f}, Fmax = {w["Fmax"]:.3f} N, Δż = {w["dzd"]:+.4f} m/s')
        print(f'  ż(5 s) = {r["PV"][50]:+.4f} m/s, ż(15 s) = {r["PV"][150]:+.4f}, ż(55 s) = {r["PV"][550]:+.4f}, ż(115 s) = {r["PV"][1150] if r["PV"].size > 1150 else float("nan"):+.4f}')
        res[f'{dt * 1e6:.0f}us'] = dict(per_streng=ps, t_streng=ts, per_locker=pl, t_locker=tl,
                                       fenster=out, PV=r['PV'].tolist(), PZ=r['PZ'].tolist())
    json.dump(res, open(OUT + f'hotspot_scalar_{phi2:.10g}_{phi3:.14g}.json', 'w'))
