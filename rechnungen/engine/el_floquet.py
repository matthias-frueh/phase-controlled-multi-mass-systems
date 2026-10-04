"""P2/engine – Floquet-Multiplikatoren der gefundenen periodischen Zustände mit dem ereignislokalisierenden
Löser: Vorlauf vom RK4-Endzustand (100 s) aus, dann Newton auf die EL-Periodenabbildung (p Zyklen) mit
zentralen Differenzen. |µ| < 1 für beide Multiplikatoren -> orbital stabil (lokaler Attraktor).
Die Jacobi-Matrix der EL-Abbildung enthält die Stoß-/Ablösezeitpunkte (Saltationsterme), anders als die
Festschritt-RK4-Abbildung (orbit_hopping.py)."""
import os
import numpy as np
import eng, el_solver as E, run_seg

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
cases = [('spec_rep_dt.json', 'run_rep_dt', 'hot_std', 1), ('spec_rep_dt.json', 'run_rep_dt', 'isl_std', 1),
         ('spec_rep_dt.json', 'run_rep_dt', 'syn_std', 2), ('spec_rep_dt.json', 'run_rep_dt', 'isl_orb', 1),
         ('spec_pairs_dt.json', 'run_pairs_dt', 'P6A_std', 1), ('spec_pairs_dt.json', 'run_pairs_dt', 'P6B_std', 1),
         ('spec_pairs_dt.json', 'run_pairs_dt', 'P49B_std', 1), ('spec_pairs_dt.json', 'run_pairs_dt', 'P45B_std', 3),
         ('spec_pairs_dt.json', 'run_pairs_dt', 'P45A_std', 30), ('spec_pairs_dt.json', 'run_pairs_dt', 'P33B_std', 2)]
cache = {}
for spec, od, name, p in cases:
    if od not in cache:
        cache[od] = run_seg.load(OUT + spec, OUT + od)
    r, L = cache[od]
    k = [l['name'] for l in L].index(name)
    a, b = L[k]['phi2'], L[k]['phi3']
    s = E.EL(a, b)
    pre = s.run(float(r['PZ'][-1, k]), float(r['PV'][-1, k]), 100.0, 60)    # Vorlauf 6 s im EL
    x0 = np.array([pre['PZ'][-1], pre['PV'][-1]])
    drift = float(np.max(np.abs(pre['PV'][-p - 1:] - pre['PV'][-2 * p - 1:-p]))) if pre['PV'].size > 2 * p else np.nan
    x, mult, res = E.newton_el(a, b, x0, t0=106.0, p=p, iters=6)
    st = E.stats(pre, 0, 60)
    print(f'{name:9s} ({a:.3f},{b:.3f}) p={p:2d}: EL-Vorlauf λ={st["lam"]:.4f} % γ1={st["skew"]:.4f} '
          f'Fmax={st["Fmax"]:.3f}; Wiederkehr nach Vorlauf |Δż|={drift:.1e}; Newton-Residuen '
          + ' '.join(f'{v:.0e}' for v in res) + ' | |µ| = ' + ', '.join(f'{abs(m):.4f}' for m in mult)
          + f'  -> {"stabil" if np.all(np.abs(mult) < 1) else "INSTABIL"} (n_fix={s.n_fix})', flush=True)
