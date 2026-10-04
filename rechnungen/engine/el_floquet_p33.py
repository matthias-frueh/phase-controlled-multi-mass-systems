"""P2/engine – Ergänzung zu el_floquet.py: Floquet-Multiplikatoren des A_max-Zustands (P33A, im EL Periode 3)
und des Hüpfzustands von P13/P49/P45 (Mitglied A) mit dem ereignislokalisierenden Löser."""
import os
import numpy as np
import eng, el_solver as E, run_seg
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
r, L = run_seg.load(OUT + 'spec_pairs_dt.json', OUT + 'run_pairs_dt')
for name, p in (('P33A_std', 3), ('P13A_std', 1), ('P49A_std', 1), ('P45A_imp', 1)):
    k = [l['name'] for l in L].index(name)
    a, b = L[k]['phi2'], L[k]['phi3']
    s = E.EL(a, b)
    pre = s.run(float(r['PZ'][-1, k]), float(r['PV'][-1, k]), 100.0, 90)
    x0 = np.array([pre['PZ'][-1], pre['PV'][-1]])
    x, mult, res = E.newton_el(a, b, x0, t0=109.0, p=p, iters=6)
    st = E.stats(pre, 30, 90)
    print(f'{name:9s} ({a:.3f},{b:.3f}) p={p}: EL λ={st["lam"]:.4f} % γ1={st["skew"]:.4f} Fmax={st["Fmax"]:.3f}; '
          f'Newton-Residuen ' + ' '.join(f'{v:.0e}' for v in res) + ' | |µ| = '
          + ', '.join(f'{abs(m):.4f}' for m in mult) + f'  -> {"stabil" if np.all(np.abs(mult) < 1) else "INSTABIL"} (n_fix={s.n_fix})', flush=True)
