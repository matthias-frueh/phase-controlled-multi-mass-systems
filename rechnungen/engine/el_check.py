"""P2/engine – Kontrollläufe mit dem ereignislokalisierenden Löser (el_solver.EL).

Aufgaben (Name, phi2, phi3, Start):
  std   z = -Mg/K, ż = 0, t0 = 0         imp  ż = -v_Module(0)
  orb   linearer Kontaktorbit (linear_solver.orbit_state)
  rk4:<lauf>  Endzustand eines RK4-Laufs (100 s) als Start, t0 = dessen Endzeit -> bleibt der RK4-Attraktor
              auch ohne Festschritt-Artefakt erhalten?
Aufruf: python3 el_check.py GRUPPE [N_CYC [I0 I1]]   (GRUPPE: rep | pairs | rk4; Ausgabe wird angehängt)
Ausgabe: el_<GRUPPE>.jsonl (eine Zeile je Aufgabe).
"""
import os
import sys, json, time
import numpy as np
import eng, el_solver as E, run_seg
import linear_solver as ls
from make_specs import PAIRS, g

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
grp = sys.argv[1]
NC = int(sys.argv[2]) if len(sys.argv) > 2 else 300
I0 = int(sys.argv[3]) if len(sys.argv) > 3 else 0          # Aufgabenbereich [I0, I1) für Läufe <= 540 s
I1 = int(sys.argv[4]) if len(sys.argv) > 4 else 10**6
tasks = []
if grp == 'rep':
    for p, (a, b) in {'tri': (120.0, 240.0), 'syn': (0.0, 0.0), 'hot': (0.0, 208.421), 'isl': (35.0, 116.0),
                      'main': (113.684, 227.368), 'edge': (100.0, 240.0)}.items():
        tasks.append((f'{p}_std', a, b, -eng.MG / eng.K, 0.0, 0.0))
        z, v = eng.start_imp(a, b)
        tasks.append((f'{p}_imp', a, b, float(z), float(v), 0.0))
        if p in ('tri', 'isl', 'main', 'edge'):
            x = ls.orbit_state(a, b)
            tasks.append((f'{p}_orb', a, b, float(x[0]), float(x[1]), 0.0))
elif grp == 'pairs':
    for pn, d in PAIRS.items():
        for role in ('A', 'B'):
            a, b = g(d[role][0]), g(d[role][1])
            tasks.append((f'{pn}{role}_std', a, b, -eng.MG / eng.K, 0.0, 0.0))
            z, v = eng.start_imp(a, b)
            tasks.append((f'{pn}{role}_imp', a, b, float(z), float(v), 0.0))
elif grp == 'rk4':
    for spec, od, names in (('spec_pairs_dt.json', 'run_pairs_dt',
                             ['P6A_std', 'P6B_std', 'P13A_std', 'P13B_std', 'P49A_std', 'P49B_std', 'P45A_std',
                              'P45B_std', 'P45A_imp', 'P33A_std', 'P33B_std']),
                            ('spec_rep_dt.json', 'run_rep_dt', ['isl_std', 'hot_std', 'syn_std'])):
        r, L = run_seg.load(OUT + spec, OUT + od)
        idx = {l['name']: k for k, l in enumerate(L)}
        for n in names:
            k = idx[n]
            tasks.append((f'rk4:{n}', L[k]['phi2'], L[k]['phi3'], float(r['PZ'][-1, k]), float(r['PV'][-1, k]), 100.0))

with open(OUT + f'el_{grp}.jsonl', 'a') as fh:
    for name, a, b, z0, v0, t0 in tasks[I0:I1]:
        tic = time.time()
        s = E.EL(a, b)
        r = s.run(z0, v0, t0, NC)
        p, ts = E.periodicity(r, n_last=50)
        nl = NC // 3
        w_last = E.stats(r, NC - nl, NC)
        if p > 0:
            n = (nl // p) * p
            w_last = E.stats(r, NC - n, NC)
        w_eng = E.stats(r, 50, 150) if NC >= 150 else None
        blk = [E.stats(r, c, c + 50)['lam'] for c in range(NC - 4 * 50, NC, 50)]
        row = dict(name=name, phi2=a, phi3=b, z0=z0, v0=v0, t0=t0, n_cyc=NC, per=p, t_einschw=ts,
                   last=w_last, eng=w_eng, lam_blocks=blk, PV_tail=r['PV'][-12:].tolist(),
                   zd_spread_last50=float(np.ptp(r['PV'][-50:])), n_fix=s.n_fix, sec=time.time() - tic)
        fh.write(json.dumps(row, default=float) + '\n'); fh.flush()
        print(f'{name:14s} p={p:3d} t_e={ts:6.1f} s  λ={w_last["lam"]:8.4f} %  γ1={w_last["skew"]:.5f}  '
              f'Fmax={w_last["Fmax"]:.3f}  δ={w_last["dF_ppm"]:+.2e} ppm  R={w_last["R_ppm"]:+.2e}  '
              f'Spanne ż(50 Zyklen)={row["zd_spread_last50"]:.1e} n_fix={s.n_fix} [{row["sec"]:.0f} s]', flush=True)
