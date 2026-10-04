"""P2/engine – Robustheit des Kontaktorbits gegen Stöße (EL): Start auf dem linearen Kontaktorbit bei t0 (Phase
im Zyklus), Geschwindigkeitssprung Δż (= Stoß auf den Schwerpunkt, M Δż); Endzustand nach 15 s
(Auswertung 10–15 s). Punkte: Insel (35°, 116°), Hauptgebiet (113,684°, 227,368°), Rand (100°, 240°), Triphasik,
Präreg-Pilotkonfigurationen (110°, 250°), (130°, 230°), (110°, 252°) (Anhang A7).
Aufruf: python3 el_kick.py [I0 I1]"""
import os
import sys, json
import numpy as np
import eng, el_solver as E
import linear_solver as ls

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
pts = [('isl', 35.0, 116.0, [0.01, 0.02, 0.03, 0.05, 0.1, -0.05, -0.1, 0.3]),
       ('main', 113.684, 227.368, [0.1, 0.3, 1.0, 3.0, -0.3]),
       ('edge', 100.0, 240.0, [0.1, 0.3, 1.0, 3.0]),
       ('tri', 120.0, 240.0, [0.3, 1.0, 3.0]),
       ('pilot1', 110.0, 250.0, [0.1, 0.3, 1.0, 3.0]),
       ('pilot2', 130.0, 230.0, [0.1, 0.3, 1.0, 3.0]),
       ('pilot3', 110.0, 252.0, [0.1, 0.3, 1.0, 3.0])]
I0, I1 = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, len(pts))
with open(OUT + 'el_kick.jsonl', 'a') as fh:
    for name, a, b, kicks in pts[I0:I1]:
        z0, v0 = ls.orbit_state(a, b)
        lin = ls.solve(a, b)
        for t0 in (0.0, 0.05):
            # Orbitzustand zur Phase t0: kurzer EL-Lauf vom Orbit aus (Kontakt, exakt periodisch)
            if t0 > 0:
                s0 = E.EL(a, b)
                # bis t0 im Kontakt integrieren
                from scipy.integrate import solve_ivp
                sol = solve_ivp(s0.rhs_c, (0.0, t0), [z0, v0, 0, 0, 0], method='DOP853', rtol=1e-12, atol=1e-15)
                zs, vs = sol.y[0, -1], sol.y[1, -1]
            else:
                zs, vs = z0, v0
            for dv in kicks:
                s = E.EL(a, b)
                r = s.run(zs, vs + dv, t0, 150)
                st = E.stats(r, 100, 150)
                row = dict(name=name, phi2=a, phi3=b, F_min_lin=float(lin['F_min_lin'][0]), t0=t0, dv=dv,
                           lam=st['lam'], skew=st['skew'], Fmax=st['Fmax'], n_fix=s.n_fix)
                fh.write(json.dumps(row) + '\n'); fh.flush()
                print(f'{name:6s} ({a:7.3f},{b:7.3f}) F_min_lin={row["F_min_lin"]:.3f} N  t0={t0:.2f} s  Δż={dv:+.2f} m/s -> '
                      f'λ={st["lam"]:7.3f} %  γ1={st["skew"]:.4f}  Fmax={st["Fmax"]:.3f}', flush=True)
