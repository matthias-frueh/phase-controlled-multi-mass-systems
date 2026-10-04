"""P2/engine – Newton auf die Periodenabbildung für Hüpfzustände (Hot-Spot P1, Insel-Hüpfzustand P1,
synchron P2), Start aus dem Endzustand der 100-s-Läufe (run_rep_dt). Prüft, ob ein exakter Fixpunkt der
diskreten Abbildung existiert, und schätzt Floquet-Multiplikatoren (Differenzen mit mehreren h)."""
import os
import numpy as np
import eng, orbit, run_seg
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
r, L = run_seg.load(OUT + 'spec_rep_dt.json', OUT + 'run_rep_dt')
idx = {l['name']: k for k, l in enumerate(L)}
for name, p in (('hot_std', 1), ('isl_std', 1), ('syn_std', 2)):
    k = idx[name]; a, b = L[k]['phi2'], L[k]['phi3']
    x0 = np.array([r['PZ'][-1, k], r['PV'][-1, k]])
    for h in ((1e-9, 1e-7), (1e-7, 1e-5), (1e-6, 1e-4)):
        x, mult, hist = orbit.newton_orbit(a, b, x0, p=p, iters=6, h=h)
        res = [max(abs(hh['res_z']) / 1e-3, abs(hh['res_v']) / 1e-1) for hh in hist]
        print(f'{name} p={p} h={h}: Residuen (skaliert) ' + ' '.join(f'{v:.1e}' for v in res)
              + f' | |µ| = ' + ', '.join(f'{abs(m):.3f}' for m in mult) + f' | x = ({x[0]:.6e}, {x[1]:.6f})')
