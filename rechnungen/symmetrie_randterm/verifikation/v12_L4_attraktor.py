"""
v12_L4_attraktor.py - Existiert der 43,84-%-Zustand von L4 (330,6; 242,9) auch in der exakten Dynamik?
 'rk4'  : eigene RK4 (frame), Standardstart, 2000 Perioden (200 s); lambda je 10-s-Fenster.
 'exakt': RK4-Zustand bei 30 s (frame) als Anfangswert der ereignisgesteuerten Integration bis 60 s;
          lambda/gamma1 in 30-35, 40-45, 55-60 s.  Zusaetzlich exakte Integration ab Standardstart (0-20 s).
"""
import sys, time, numpy as np
import v_engine as ve
p2, p3 = 330.6, 242.9
if sys.argv[1] == 'rk4':
    t1 = time.time()
    o = ve.run([p2], [p3], 2000, form='frame')
    lam = [ve.window(o, a, a + 100)['lam'][0] for a in range(0, 2000, 100)]
    print(f'RK4 200 s ({time.time() - t1:.0f} s): lambda je 10 s: ' + ' '.join('%.2f' % l for l in lam))
    sys.exit()
import v_exakt as vx
o = ve.run([p2], [p3], 300, form='frame')
w = ve.window(o, 200, 300)
print(f'RK4 20-30 s: lambda {w["lam"][0]:.3f} %, gamma1 {w["gam"][0]:+.4f}; Zustand bei 30 s z = {o["xend"][0]:.6e}, v = {o["vend"][0]:.6f}')
for lab, (t0, z0, v0, tend, wins) in {'ab RK4-Zustand 30 s': (30.0, float(o['xend'][0]), float(o['vend'][0]), 60.0,
                                                          [(30, 35), (40, 45), (55, 60)]),
                                      'ab Standardstart': (0.0, -ve.MG / ve.K0, 0.0, 20.0, [(5, 10), (15, 20)])}.items():
    t1 = time.time()
    b = vx.Bahn(p2, p3)
    b.integriere(t0, z0, v0, tend)
    res = []
    for a, c in wins:
        tg = a + np.arange(int((c - a) / 5e-6)) * 5e-6
        F = b.kraft(tg); m, s = F.mean(), F.std()
        res.append(f'{a}-{c} s: lambda {np.mean(F < 1e-9) * 100:.3f} %, gamma1 {np.mean((F - m) ** 3) / s ** 3:+.4f}')
    print(f'exakt {lab} [{time.time() - t1:.0f} s]: ' + ' | '.join(res), flush=True)
