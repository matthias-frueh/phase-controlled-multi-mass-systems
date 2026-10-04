"""s5_randterm_skalar.py - Teil B, Aufgabe 5: Fensterreihe mit der SKALAREN Referenz-Engine
(pcmms_v3a_phasen_sweep.rhs, nur importiert, unveraendert), Standardstart, dt = 50 us.
Aufruf: python3 s5_randterm_skalar.py <phi2> <phi3> <t_end_max>
Fenster: Beginn 5 s, Enden 15, 35, 75, 155 s (Tab. 9.3) sowie Fenster nach dem Einschwingen
[25,35], [45,55], [95,105], [145,155] s.  Ausgabe je Fenster: Linksrechteck-Mittel N1 (Engine),
RK4-gewichtetes Mittel, delta, R = M*dv_S/T_w, Q = N1 - N_RK4, E = N_RK4 - Mg - R.
Schreibt s5_randterm_skalar_<phi2>_<phi3>.json."""
import json
import math
import sys
import time
import pcmms_v3a_phasen_sweep as s

PHI2, PHI3 = float(sys.argv[1]), float(sys.argv[2])
T_MAX = float(sys.argv[3]) if len(sys.argv) > 3 else 155.0
h = s.DT; M = s.M; MG = s.MG
tau2 = math.radians(PHI2) / (2 * math.pi * s.F_HZ)
tau3 = math.radians(PHI3) / (2 * math.pi * s.F_HZ)
T_CYC, THOLD, TFAST, RTOP, RBOT = s.T_CYC, s.THOLD, s.TFAST, s.RTOP, s.RBOT


def egg_v(t):
    phase = (t % T_CYC) / T_CYC
    if phase < THOLD:
        return RTOP * math.pi / (THOLD * T_CYC) * math.cos(math.pi * phase / THOLD)
    return -RBOT * math.pi / (TFAST * T_CYC) * math.cos(math.pi * (phase - THOLD) / TFAST)


def vcom(zd, t):
    return zd + (egg_v(t) + egg_v(t - tau2) + egg_v(t - tau3)) / 3.0


WINDOWS = [(5.0, 15.0), (5.0, 35.0), (5.0, 75.0), (5.0, 155.0),
           (25.0, 35.0), (45.0, 55.0), (95.0, 105.0), (145.0, 155.0)]
WINDOWS = [w for w in WINDOWS if w[1] <= T_MAX + 1e-9]
n_end = round(T_MAX / h)
marks = sorted({round(a / h) for w in WINDOWS for a in w})
# kumulative Summen (Kahan-frei, aber blockweise in Python-Floats; Fehler << 1e-9 N)
cum1 = 0.0; cumw = 0.0
snap = {}
z, zd = -MG / s.K, 0.0
rhs = s.rhs
tic = time.time()
blk1 = 0.0; blkw = 0.0
for i in range(n_end):
    if marks and i == marks[0]:
        snap[i] = (cum1 + blk1, cumw + blkw, vcom(zd, i * h), zd)
        marks.pop(0)
    t = i * h
    k1z, k1d, f1 = rhs(z, zd, t, tau2, tau3)
    k2z, k2d, f2 = rhs(z + 0.5 * h * k1z, zd + 0.5 * h * k1d, t + 0.5 * h, tau2, tau3)
    k3z, k3d, f3 = rhs(z + 0.5 * h * k2z, zd + 0.5 * h * k2d, t + 0.5 * h, tau2, tau3)
    k4z, k4d, f4 = rhs(z + h * k3z, zd + h * k3d, t + h, tau2, tau3)
    blk1 += f1
    blkw += (f1 + 2 * f2 + 2 * f3 + f4) / 6.0
    if (i + 1) % 2000 == 0:
        cum1 += blk1; cumw += blkw; blk1 = 0.0; blkw = 0.0
    z = z + h * (k1z + 2 * k2z + 2 * k3z + k4z) / 6.0
    zd = zd + h * (k1d + 2 * k2d + 2 * k3d + k4d) / 6.0
snap[n_end] = (cum1 + blk1, cumw + blkw, vcom(zd, n_end * h), zd)
res = []
for (a, b) in WINDOWS:
    ia, ib = round(a / h), round(b / h)
    N = ib - ia; Tw = N * h
    m1 = (snap[ib][0] - snap[ia][0]) / N
    mw = (snap[ib][1] - snap[ia][1]) / N
    R = M * (snap[ib][2] - snap[ia][2]) / Tw
    r = dict(t_a=a, t_b=b, T=Tw, mean_N1=m1, mean_RK4=mw, delta_ppm=(m1 - MG) / MG * 1e6,
             R_ppm=R / MG * 1e6, Q_ppm=(m1 - mw) / MG * 1e6, E_RK4_N=mw - MG - R,
             dvcom=snap[ib][2] - snap[ia][2], RT_ppm_s=R / MG * 1e6 * Tw)
    res.append(r)
    print(json.dumps(r), flush=True)
print(f'Laufzeit {time.time() - tic:.0f} s')
json.dump(dict(phi2=PHI2, phi3=PHI3, dt=h, engine='pcmms_v3a_phasen_sweep.rhs (skalar)', results=res),
          open(f's5_randterm_skalar_{PHI2:g}_{PHI3:g}.json', 'w'), indent=1)
