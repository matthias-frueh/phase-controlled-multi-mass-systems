"""P2/engine – Segmentweiser Lauf einer Läufe-Spezifikation (JSON) mit bitgenauer Fortsetzung.

Aufruf: python3 run_seg.py SPEC.json OUTDIR SEG N_CYC_PER_SEG
  SEG = 0 startet aus den Anfangszuständen der Spezifikation, SEG = k > 0 setzt den Endzustand von
  Segment k-1 fort (t = t0 + (i0 + i)*dt, i0 = k*N_CYC*n_per).
Ablage: OUTDIR/seg_<k>.npz (zyklusweise Akkumulatoren, Poincaré-Schnitt, letzte 2 Zyklen N1),
        OUTDIR/state_<k>.npz (Endzustand).
"""
import sys, os, json, time
import numpy as np
import eng

KEYS = ('S1', 'S2', 'S3', 'SW', 'MN', 'MX', 'LO', 'TD', 'PZ', 'PV', 'PS')


def main():
    spec_path, outdir, seg, ncyc = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    spec = json.load(open(spec_path))
    dt = spec['dt']
    L = spec['lanes']
    os.makedirs(outdir, exist_ok=True)
    phi2 = np.array([l['phi2'] for l in L]); phi3 = np.array([l['phi3'] for l in L])
    t0 = np.array([l.get('t0', 0.0) for l in L])
    Tr = np.array([l.get('Tr', 0.0) for l in L])
    n_per = int(round(eng.T_CYC / dt))
    if seg == 0:
        z0 = np.array([l['z0'] for l in L]); v0 = np.array([l['v0'] for l in L])
    else:
        st = np.load(os.path.join(outdir, f'state_{seg - 1}.npz'))
        z0, v0 = st['z'], st['zd']
    i0 = seg * ncyc * n_per
    tic = time.time()
    r = eng.integrate(phi2, phi3, z0, v0, t0=t0, dt=dt, n_cyc=ncyc, Tr=Tr, keep_last=2, verbose=True, i0=i0)
    np.savez(os.path.join(outdir, f'seg_{seg}.npz'), tail=r['tail'], **{k: r[k] for k in KEYS})
    np.savez(os.path.join(outdir, f'state_{seg}.npz'), z=r['PZ'][-1], zd=r['PV'][-1])
    print(f'Segment {seg}: {len(L)} Läufe, {ncyc} Zyklen, dt = {dt * 1e6:.1f} µs, {time.time() - tic:.0f} s')


def load(spec_path, outdir):
    """Fügt alle vorhandenen Segmente zusammen; Rückgabe im Format von eng.integrate."""
    spec = json.load(open(spec_path))
    dt = spec['dt']; L = spec['lanes']
    segs = []
    k = 0
    while os.path.exists(os.path.join(outdir, f'seg_{k}.npz')):
        segs.append(np.load(os.path.join(outdir, f'seg_{k}.npz')))
        k += 1
    res = {}
    for key in ('S1', 'S2', 'S3', 'SW', 'MN', 'MX', 'LO', 'TD'):
        res[key] = np.concatenate([s[key] for s in segs], 0)
    for key in ('PZ', 'PV', 'PS'):
        res[key] = np.concatenate([s[key][:-1] for s in segs] + [segs[-1][key][-1:]], 0)
    res['tail'] = segs[-1]['tail']
    res['n_per'] = int(round(eng.T_CYC / dt)); res['dt'] = dt
    res['t0'] = np.array([l.get('t0', 0.0) for l in L])
    res['phi2'] = np.array([l['phi2'] for l in L]); res['phi3'] = np.array([l['phi3'] for l in L])
    return res, L


if __name__ == '__main__':
    main()
