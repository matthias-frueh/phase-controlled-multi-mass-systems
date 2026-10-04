"""
v8_skalar_tab93.py - Gegenpruefung RT-01 an der ARCHIV-Realisierung: Schleife mit der unveraenderten skalaren
Referenz-Engine (pcmms_v3a_phasen_sweep.rk4_step, Standardstart, t = i*DT), 155 s, (0; 208,421).
Eigene Auswertung: N1 (Linksrechteck der Stufe-1-Kraft wie Engine), v_S = zd + qbar'(t) mit EIGENER
Profilgeschwindigkeit (v_engine.pbar), R = M dv_S/T_w, Rest Q+E = delta - R.
"""
import math, time, numpy as np
import pcmms_v3a_phasen_sweep as ref
import v_engine as ve

phi2, phi3 = 0.0, 208.421
tau2 = math.radians(phi2) / (2 * math.pi * ref.F_HZ)
tau3 = math.radians(phi3) / (2 * math.pi * ref.F_HZ)
DT = ref.DT
N = int(round(155.0 / DT))
F = np.empty(N)
marks = {int(round(t / DT)): None for t in (5, 15, 25, 35, 45, 55, 75, 95, 105, 145, 155)}
z, zd = -ref.MG / ref.K, 0.0
t1 = time.time()
for i in range(N):
    if i in marks:
        marks[i] = (z, zd)
    z, zd, Fc = ref.rk4_step(z, zd, i * DT, tau2, tau3)
    F[i] = Fc
marks[N] = (z, zd)
print(f'Lauf {time.time() - t1:.0f} s')


def vS(i):
    t = i * DT
    _, qd, _ = ve.pbar(np.array([t]), tau2, tau3)
    return marks[i][1] + qd[0]


MG = ref.MG
rows = []
for a, b in [(5, 15), (5, 35), (5, 75), (5, 155), (25, 35), (45, 55), (95, 105), (145, 155)]:
    ia, ib = int(round(a / DT)), int(round(b / DT))
    N1 = F[ia:ib].mean()
    d = (N1 - MG) / MG * 1e6
    dv = vS(ib) - vS(ia)
    R = ref.M * dv / (b - a) / MG * 1e6
    rows.append((b - a, N1, d, R, d - R, dv))
    print(f'Fenster {a:5.1f}-{b:5.1f} s: N1 = {N1:.6f} N  delta = {d:+9.1f} ppm  R = {R:+9.1f} ppm  Q+E = {d - R:+7.1f} ppm  '
          f'dv_S = {dv:+.5f} m/s  R*T = {R * (b - a):+.0f} ppm s')
A = np.array(rows[:4])
Tw = A[:, 0]
print('Tab. 9.3: 6,333041 / 6,361711 / 6,369854 / 6,373122 N')
print(f'Potenzfit delta: {np.polyfit(np.log(Tw), np.log(np.abs(A[:, 2])), 1)[0]:.4f}; Potenzfit R: '
      f'{np.polyfit(np.log(Tw), np.log(np.abs(A[:, 3])), 1)[0]:.5f}; Spannweite R*T {np.ptp(A[:, 3] * Tw) / abs(np.mean(A[:, 3] * Tw)) * 100:.3f} %')
np.save('v8_skalar_F.npy', F[::20])   # ausgeduennt (1 ms) fuer Kontrolle
