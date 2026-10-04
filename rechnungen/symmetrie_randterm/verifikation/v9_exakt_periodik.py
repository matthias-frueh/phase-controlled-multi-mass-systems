"""
v9_exakt_periodik.py - Periodenstruktur von S0 (0,0) und HS (0; 208,421) mit der ereignisgesteuerten,
halbanalytischen Integration (v_exakt), Standardstart, 0-25 s. v_S = v_f + qbar' an den Periodenbeginnen 10-25 s.
Frage (RT-05/RT-02): ist S0 aperiodisch (Gruppe: sigma_v = 0,030 m/s) oder ein Orbit der Periode 2?
"""
import sys, time, numpy as np
import v_engine as ve, v_exakt as vx
nm = sys.argv[1]
p2, p3 = {'S0': (0.0, 0.0), 'HS': (0.0, 208.421)}[nm]
t1 = time.time()
b = vx.Bahn(p2, p3)
b.integriere(0.0, -ve.MG / ve.K0, 0.0, 25.0)
tc = np.arange(100, 250) * ve.T + 1e-12
z, v = b.zustand(tc)
_, qd, _ = ve.pbar(tc, b.tau2, b.tau3)
vS = v + qd
print(f'{nm} exakt ({time.time() - t1:.0f} s), v_S an Periodenbeginnen 10-25 s:')
print(f'  sigma_v alle = {vS.std():.3e} m/s')
for p in (1, 2, 3, 4):
    subs = [vS[k::p] for k in range(p)]
    print(f'  Periode {p}: Mittel ' + ' '.join('%.6f' % s.mean() for s in subs) + ' | std ' + ' '.join('%.2e' % s.std() for s in subs))
print('  letzte 6 Werte:', np.round(vS[-6:], 7))
for n in (100, 101):
    dv = vS[n:] - vS[:-n]
    print(f'  Fenster n = {n} Perioden (phasenstarr): max|dv_S| = {np.max(np.abs(dv)):.2e} m/s')
