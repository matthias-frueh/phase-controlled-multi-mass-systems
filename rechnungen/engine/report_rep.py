"""P2/engine – Zusammenfassende Tabelle der repräsentativen Punkte: RK4 (Δt, Δt/2, 100 s) und EL (30 s).
Liest tab_rep_dt.csv, tab_dt2.csv, el_rep.jsonl; schreibt rep_tabelle.csv und druckt eine kompakte Tabelle.
Kenngrößen aus dem Fenster 50–100 s (RK4) bzw. 20–30 s (EL); Einschwingzeit aus dem Poincaré-Schnitt."""
import os
import json
import numpy as np
import pandas as pd

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
a = pd.read_csv(OUT + 'tab_rep_dt.csv')
b = pd.read_csv(OUT + 'tab_dt2.csv')
b = b[~b.name.str.startswith('P')]
el = {}
for line in open(OUT + 'el_rep.jsonl'):
    r = json.loads(line)
    el[r['name']] = r
rows = []
for df, tag in ((a, 'RK4 50 µs'), (b, 'RK4 25 µs')):
    for _, r in df.iterrows():
        rows.append(dict(lauf=r['name'], loeser=tag, lam=r['lam@50_100'], skew=r['skew@50_100'], Fmin=r['Fmin@50_100'],
                         Fmax=r['Fmax@50_100'], dF_left_ppm=r['dF_left_ppm@50_100'], dF_rk4_ppm=r['dF_rk4_ppm@50_100'],
                         R_ppm=r['R_ppm@50_100'], lam_5_15=r['lam@eng'], dF_left_5_15=r['dF_left_ppm@eng'],
                         Fmax_5_15=r['Fmax@eng'], per_streng=r['per_streng'], per_locker=r['per_locker'],
                         t_einschw_streng=r['t_einschw_streng'], t_einschw_locker=r['t_einschw_locker']))
for n, r in el.items():
    rows.append(dict(lauf=n, loeser='EL', lam=r['last']['lam'], skew=r['last']['skew'], Fmin=np.nan, Fmax=r['last']['Fmax'],
                     dF_left_ppm=np.nan, dF_rk4_ppm=r['last']['dF_ppm'], R_ppm=r['last']['R_ppm'],
                     lam_5_15=r['eng']['lam'] if r['eng'] else np.nan, dF_left_5_15=r['eng']['dF_ppm'] if r['eng'] else np.nan,
                     Fmax_5_15=r['eng']['Fmax'] if r['eng'] else np.nan, per_streng=r['per'], per_locker=np.nan,
                     t_einschw_streng=r['t_einschw'], t_einschw_locker=np.nan))
t = pd.DataFrame(rows)
t['punkt'] = t.lauf.str.split('_').str[0]
t['start'] = t.lauf.str.split('_').str[1]
order = {'tri': 0, 'main': 1, 'edge': 2, 'isl': 3, 'hot': 4, 'syn': 5}
t = t.sort_values(['punkt', 'start', 'loeser'], key=lambda s: s.map(order) if s.name == 'punkt' else s)
t.to_csv(OUT + 'rep_tabelle.csv', index=False, float_format='%.6g')
with pd.option_context('display.width', 320, 'display.max_rows', 200, 'display.float_format', '{:.5g}'.format):
    print(t[['punkt', 'start', 'loeser', 'lam', 'skew', 'Fmin', 'Fmax', 'dF_left_ppm', 'dF_rk4_ppm', 'R_ppm', 'lam_5_15',
             'dF_left_5_15', 'Fmax_5_15', 'per_streng', 'per_locker', 't_einschw_streng', 't_einschw_locker']].to_string(index=False))
