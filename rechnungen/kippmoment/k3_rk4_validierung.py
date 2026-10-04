"""
k3_rk4_validierung.py – Befund KM-02 (Modellprüfung): eigenes 3-FG-RK4 gegen Referenz-Engine und
gegen die eigene lineare Lösung.

(a) Bilaterale Zellen, G0, μ = 1, K = 1e4, C = 16, (0°, 120°, 240°): Summe der Zellkräfte gegen
    finesweep.run (Engine, vektorisiert) – gleiche Δt, gleicher Standardstart, gleiche Stichproben (k1).
(b) Bilateral, Zellkräfte und Momente gegen linear() (eingeschwungen, 10 s Fenster) für mehrere Geometrien
    und Fälle (REF μ = 1/0,462, STEIF μ = 0,462) und Konfigurationen.
Δt-Konvergenz: (c) dieselben Läufe mit Δt/2 an einem Punkt.
"""
import numpy as np
import finesweep
from km_modell import Geo, rk4, linear, harmonische, momente, rot_zerlegung, M, MG, DT

R_C = 0.10
K_ST = 369518.0
C_ST = 2 * 0.02 * np.sqrt(K_ST * M)

print('=== (a) Summe der bilateralen Zellkräfte gegen Engine (finesweep), (0°,120°,240°), REF μ = 1 ===')
out, ser = finesweep.run([120.0], [240.0], store_series=True, series_len=int(10.0 / DT))
geo = Geo(R_c=R_C, mu=1.0)
r = rk4([geo], [(0, 120, 240)], bilateral=True)
N3 = r['F'][:, 0, :].sum(1)
Ne = ser[:, 0]
print(f'Engine: F_min {out["F_min"][0]:.6f}  F_max {out["F_max"][0]:.6f}  mean {out["F_mean"][0]:.9f}  liftoff {out["liftoff"][0]:.3f} %')
print(f'3-FG  : F_min {N3.min():.6f}  F_max {N3.max():.6f}  mean {N3.mean():.9f}')
print(f'max|N_3FG − N_Engine| über 10 s = {np.max(np.abs(N3 - Ne)):.3e} N')
print(f'Kippkoordinaten am Ende: a = {r["q"][0,1]:.3e}, b = {r["q"][0,2]:.3e} (≠ 0 erwartet, Kippmoment)')

print('\n=== (b) RK4 bilateral gegen lineare Lösung (Zellkräfte, Momente) ===')
cases = []
for (lab, K, C, mu) in (('REF', 1e4, 16.0, 1.0), ('REF', 1e4, 16.0, 0.462), ('STEIF', K_ST, C_ST, 0.462)):
    for gname, gk in (('G0', dict(R_m=R_C, dpsi_deg=0)), ('G60h', dict(R_m=R_C / 2, dpsi_deg=60))):
        for phi in ((0, 120, 240), (0, 110, 240)):
            cases.append((lab, K, C, mu, gname, gk, phi))
for lab, K, C in (('REF', 1e4, 16.0), ('STEIF', K_ST, C_ST)):
    sub = [c for c in cases if c[0] == lab]
    geos = [Geo(R_c=R_C, mu=c[3], **c[5]) for c in sub]
    phis = [c[6] for c in sub]
    rr = rk4(geos, phis, K=K, C=C, bilateral=True)
    for i, c in enumerate(sub):
        Fr = rr['F'][:, i, :].T                       # 3 × n
        lin = linear(geos[i], c[6], K=K, C=C)
        Fl = np.tile(lin['F'], (1, Fr.shape[1] // lin['F'].shape[1]))
        Mx, My = momente(geos[i], Fr.T)
        Xk, Yk = harmonische(Mx), harmonische(My)
        Rp, Rm = rot_zerlegung(Xk, Yk)
        Rpl, Rml = rot_zerlegung(lin['Mxk'], lin['Myk'])
        print(f'{c[0]:5s} μ={c[3]:5.3f} {c[4]:4s} φ={c[6]}: max|F_RK4 − F_lin| = {np.abs(Fr - Fl).max():.2e} N; '
              f'F_min RK4/lin = {Fr.min():.5f}/{lin["F"].min():.5f}; R+1 {Rp[1]:.5f}/{Rpl[1]:.5f}, R−2 {Rm[2]:.5f}/{Rml[2]:.5f} N·m')

print('\n=== (c) Δt-Konvergenz (bilateral, REF μ = 0,462, G0, (0°,110°,240°)) ===')
geo = Geo(R_c=R_C, mu=0.462)
for dt in (DT, DT / 2):
    rr = rk4([geo], [(0, 110, 240)], bilateral=True, dt=dt)
    F = rr['F'][:, 0, :]
    print(f'dt = {dt*1e6:.0f} µs: F_min Zelle {F.min():.7f} N, F_max {F.max():.7f} N, mean Zelle 1 {F[:,0].mean():.9f}')
