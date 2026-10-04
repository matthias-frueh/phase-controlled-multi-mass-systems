"""P2/engine – Stufe 2 der Paarprüfung (exakte Gitterphasen i*360/19):
  B_stdshift  B mit Standardzustand, aber t0 = -s  (äquivalent zu A_std: abar_B(t) = abar_A(t + s))
  A_stdshift  A mit Standardzustand, t0 = +s       (äquivalent zu B_std)
  B_fromA     B mit dem Endzustand von A_std (t = 100 s), t0 = 100 - s  (Start auf A's Orbit, zeitverschoben)
  A_fromB     A mit dem Endzustand von B_std, t0 = 100 + s
s = tau_j(A), j = Modul, das unter der Permutation zur neuen Referenz wird.
"""
import os
import json
import numpy as np
import eng
import run_seg
from make_specs import PAIRS, g

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')


def shift(pn):
    d = PAIRS[pn]
    a2, a3 = g(d['A'][0]), g(d['A'][1])
    j = {'(12)': 2, '(123)': 2, '(13)': 3, '(132)': 3}[d['g']]
    s = float(eng.taus(a2 if j == 2 else a3, 0.0)[0])
    # Kontrolle abar_B(t) = abar_A(t + s)
    b2, b3 = g(d['B'][0]), g(d['B'][1])
    t = np.linspace(0, 0.1, 997)
    TA = np.stack([np.zeros(1), *[np.atleast_1d(x) for x in eng.taus(a2, a3)]])
    TB = np.stack([np.zeros(1), *[np.atleast_1d(x) for x in eng.taus(b2, b3)]])
    fa = np.array([eng.forcing(np.array([tt + s]), TA)[0] for tt in t])
    fb = np.array([eng.forcing(np.array([tt]), TB)[0] for tt in t])
    err = np.max(np.abs(fa - fb))
    assert err < 1e-6, (pn, err)
    return s, err


if __name__ == '__main__':
    r, L = run_seg.load(OUT + 'spec_pairs_dt.json', OUT + 'run_pairs_dt')
    idx = {l['name']: k for k, l in enumerate(L)}
    lanes = []
    for pn, d in PAIRS.items():
        s, err = shift(pn)
        A = (g(d['A'][0]), g(d['A'][1])); B = (g(d['B'][0]), g(d['B'][1]))
        zA, vA = float(r['PZ'][-1, idx[f'{pn}A_std']]), float(r['PV'][-1, idx[f'{pn}A_std']])
        zB, vB = float(r['PZ'][-1, idx[f'{pn}B_std']]), float(r['PV'][-1, idx[f'{pn}B_std']])
        TEND = 100.0
        base = dict(Tr=0.0)
        lanes += [dict(name=f'{pn}B_stdshift', point=f'{pn}B', phi2=B[0], phi3=B[1], start='stdshift',
                       z0=-eng.MG / eng.K, v0=0.0, t0=-s, **base),
                  dict(name=f'{pn}A_stdshift', point=f'{pn}A', phi2=A[0], phi3=A[1], start='stdshift',
                       z0=-eng.MG / eng.K, v0=0.0, t0=s, **base),
                  dict(name=f'{pn}B_fromA', point=f'{pn}B', phi2=B[0], phi3=B[1], start='fromA',
                       z0=zA, v0=vA, t0=TEND - s, **base),
                  dict(name=f'{pn}A_fromB', point=f'{pn}A', phi2=A[0], phi3=A[1], start='fromB',
                       z0=zB, v0=vB, t0=TEND + s, **base)]
        print(f'{pn}: g = {d["g"]}, s = {s * 1e3:.6f} ms, max|abar_B(t) - abar_A(t+s)| = {err:.1e} m/s²')
    json.dump(dict(dt=eng.DT, lanes=lanes), open(OUT + 'spec_transfer_dt.json', 'w'), indent=1)
    print(len(lanes), 'Läufe')
