"""P2/engine – Frequenzhochlauf (Tr = 2 s und 10 s, Start aus Ruhe) mit dem ereignislokalisierenden Löser an
Insel und den Paaren mit Mehrdeutigkeit; Auswertung 20–30 s."""
import os
import sys, json
import numpy as np
import eng, el_solver as E
from make_specs import PAIRS, g
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
pts = [('isl', 35.0, 116.0), ('hot', 0.0, 208.421), ('syn', 0.0, 0.0)]
for pn in ('P6', 'P13', 'P49', 'P45', 'P33'):
    for role in ('A', 'B'):
        pts.append((f'{pn}{role}', g(PAIRS[pn][role][0]), g(PAIRS[pn][role][1])))
I0, I1 = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, len(pts))
with open(OUT + 'el_ramp.jsonl', 'a') as fh:
    for name, a, b in pts[I0:I1]:
        for Tr in (2.0, 10.0):
            s = E.ELRamp(a, b, Tr=Tr)
            r = s.run(-eng.MG / eng.K, 0.0, 0.0, 300)
            st = E.stats(r, 200, 300)
            p, ts = E.periodicity(r, n_last=50)
            print(f'{name:5s} ({a:8.3f},{b:8.3f}) Tr={Tr:4.0f} s: λ={st["lam"]:8.4f} % γ1={st["skew"]:.4f} '
                  f'Fmax={st["Fmax"]:.3f} p={p} ab {ts:.1f} s', flush=True)
            fh.write(json.dumps(dict(name=name, phi2=a, phi3=b, Tr=Tr, per=p, t_e=ts, **{k: float(v) for k, v in st.items()})) + '\n')
