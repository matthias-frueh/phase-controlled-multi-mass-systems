"""P2/engine – Zusammenfassung der sechs Äquivalenzpaare: λ [%] (RK4 50–100 s, EL letzte 10–13 s bzw. 20–30 s)
je Start; Quelle: tab_pairs_dt.csv, tab_transfer_dt.csv, tab_dt2.csv, el_pairs.jsonl, el_ramp.jsonl, CSV-Archiv."""
import os
import json
import numpy as np
import pandas as pd
from make_specs import PAIRS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
N = 19
csv = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data/sweep_19x19.csv'))
csv['i2'] = np.round(csv.phi2_deg / (360 / N)).astype(int) % N
csv['i3'] = np.round(csv.phi3_deg / (360 / N)).astype(int) % N
ref = {(r.i2, r.i3): r for r in csv.itertuples()}
t = pd.concat([pd.read_csv(OUT + f) for f in ('tab_pairs_dt.csv', 'tab_transfer_dt.csv')])
t2 = pd.read_csv(OUT + 'tab_dt2.csv')
lam = dict(zip(t.name, t['lam@50_100']))
lam5 = dict(zip(t.name, t['lam@eng']))
lam2 = dict(zip(t2.name, t2['lam@50_100']))
el = {}
for f in ('el_pairs.jsonl',):
    for line in open(OUT + f):
        r = json.loads(line); el[r['name']] = r['last']['lam']
elr = {}
for line in open(OUT + 'el_ramp.jsonl'):
    r = json.loads(line); elr[(r['name'], r['Tr'])] = r['lam']
rows = []
for pn, d in PAIRS.items():
    for role in ('A', 'B'):
        k = f'{pn}{role}'
        rows.append(dict(paar=pn, mitglied=role, idx=str(d[role]), CSV_5_15=ref[d[role]].liftoff,
                         stdR_5_15=lam5.get(f'{k}_stdR'), stdR=lam.get(f'{k}_stdR'), std=lam.get(f'{k}_std'),
                         imp=lam.get(f'{k}_imp'), ramp2=lam.get(f'{k}_ramp2'), stdshift=lam.get(f'{k}_stdshift'),
                         vom_Partner=lam.get(f'{k}_fromA' if role == 'B' else f'{k}_fromB'),
                         stdR_dt2=lam2.get(f'{k}_stdR'), EL_std=el.get(f'{k}_std'), EL_imp=el.get(f'{k}_imp'),
                         EL_ramp2=elr.get((k, 2.0)), EL_ramp10=elr.get((k, 10.0))))
df = pd.DataFrame(rows)
df.to_csv(OUT + 'paare_tabelle.csv', index=False, float_format='%.4f')
with pd.option_context('display.width', 300, 'display.float_format', '{:.2f}'.format):
    print(df.to_string(index=False))
