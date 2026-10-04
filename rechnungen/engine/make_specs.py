"""P2/engine – Läufe-Spezifikationen für die repräsentativen Punkte und die Äquivalenzpaare (Stufe 1).

Starts:
  std     z = -Mg/K, ż = 0, t0 = 0 (Engine)
  imp     z = -Mg/K, ż = -(1/3) sum e'(-tau_k)  -> v_S(0) = 0 (impulskonsistent)
  ramp2   Frequenzrampe 0 -> 10 Hz in 2 s bei festen Phasen, Start aus Ruhe (Module stehen, v_S = 0)
  ramp10  dito in 10 s
  orb     Fixpunkt der diskreten Periodenabbildung (Newton, orbit.py), nur Kontaktast
"""
import os
import json
import numpy as np
import eng
import orbit
import linear_solver as ls

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
GR = 360.0 / 19


def g(i):
    return i * GR


def gr(i):
    return round(i * GR, 3)


REP = {'tri': (120.0, 240.0), 'syn': (0.0, 0.0), 'hot': (0.0, 208.421), 'isl': (35.0, 116.0),
       'main': (113.684, 227.368), 'edge': (100.0, 240.0)}
CONTACT = ['tri', 'main', 'edge', 'isl']

# Äquivalenzpaare (Gitterindizes), Gruppenelement und Referenzmodul der Zeitverschiebung
PAIRS = {'P6':  dict(A=(0, 6),   B=(13, 13), g='(13)'),
         'P13': dict(A=(6, 6),   B=(13, 0),  g='(12)'),
         'P49': dict(A=(3, 7),   B=(16, 4),  g='(12)'),
         'P45': dict(A=(12, 17), B=(14, 2),  g='(13)'),
         'P11': dict(A=(0, 11),  B=(8, 8),   g='(13)'),
         'P33': dict(A=(1, 16),  B=(3, 4),   g='(132)')}


def lane(name, point, a, b, start, dt, Tr=0.0, orbit_x=None):
    if start == 'std' or start.startswith('ramp'):
        z0, v0 = -eng.MG / eng.K, 0.0
    elif start == 'imp':
        zz, vv = eng.start_imp(a, b)
        z0, v0 = float(zz), float(vv)
    elif start == 'orb':
        z0, v0 = float(orbit_x[0]), float(orbit_x[1])
    return dict(name=name, point=point, phi2=float(a), phi3=float(b), start=start, z0=float(z0), v0=float(v0),
                t0=0.0, Tr=float(Tr))


def rep_lanes(dt):
    L = []
    for p, (a, b) in REP.items():
        for st, Tr in (('std', 0.0), ('imp', 0.0), ('ramp2', 2.0), ('ramp10', 10.0)):
            L.append(lane(f'{p}_{st}', p, a, b, st, dt, Tr))
        if p in CONTACT:
            x, mult, _ = orbit.newton_orbit(a, b, np.array(ls.orbit_state(a, b)), dt=dt, iters=4)
            L.append(lane(f'{p}_orb', p, a, b, 'orb', dt, orbit_x=x))
    return L


def pair_lanes(dt, starts=('stdR', 'std', 'imp', 'ramp2')):
    L = []
    for pn, d in PAIRS.items():
        for role in ('A', 'B'):
            i, j = d[role]
            for st in starts:
                if st == 'stdR':
                    L.append(lane(f'{pn}{role}_stdR', f'{pn}{role}', gr(i), gr(j), 'std', dt))
                elif st == 'ramp2':
                    L.append(lane(f'{pn}{role}_ramp2', f'{pn}{role}', g(i), g(j), 'ramp2', dt, 2.0))
                else:
                    L.append(lane(f'{pn}{role}_{st}', f'{pn}{role}', g(i), g(j), st, dt))
    return L


if __name__ == '__main__':
    v = eng.v_modules(0.0, *eng.taus(*np.array([[0, 0, 120], [0, 208.421, 240]])))
    print('v_S(0) Standardstart bei (0,0), (0,208.421), (120,240):', np.round(v, 4), 'm/s')
    json.dump(dict(dt=eng.DT, lanes=rep_lanes(eng.DT)), open(OUT + 'spec_rep_dt.json', 'w'), indent=1)
    json.dump(dict(dt=eng.DT, lanes=pair_lanes(eng.DT)), open(OUT + 'spec_pairs_dt.json', 'w'), indent=1)
    L2 = rep_lanes(eng.DT / 2) + pair_lanes(eng.DT / 2, starts=('stdR',))
    json.dump(dict(dt=eng.DT / 2, lanes=L2), open(OUT + 'spec_dt2.json', 'w'), indent=1)
    for f in ('spec_rep_dt.json', 'spec_pairs_dt.json', 'spec_dt2.json'):
        s = json.load(open(OUT + f))
        print(f, len(s['lanes']), 'Läufe')
