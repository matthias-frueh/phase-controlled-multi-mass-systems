"""Folgelaeufe zum Burn-in-Sweep (Originalsolver unveraendert).
Modus 'klass' : Punktliste (i2,i3) ueber T_TOTAL s simulieren; Zyklusstart-Zustaende,
                Flugbruchteil je Zyklus und N1 mitloggen; nachtraeglich Periode,
                Konvergenzzeit, Regimewechsel und Fensterstatistik bestimmen.
Modus 'fenster': Punkt mit Fensterlaenge in Zyklen auswerten (Burn-in fest).
"""
import importlib.util, math, csv, sys, json, time
import numpy as np
from scipy.stats import skew

import os
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'code', 'pcmms_v3a_phasen_sweep.py')  # Pfad angepasst: Engine aus code/
spec = importlib.util.spec_from_file_location('v3a', SRC)
s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
h = s.DT; M = s.M; MG = s.MG; K = s.K
T_CYC = s.T_CYC; STEPS_CYC = round(T_CYC/h)
PHIS = np.linspace(0.0, 360.0, s.N_GRID, endpoint=False)
TOL_V, TOL_Z = 1e-3, 1e-4

def simulate(i2, i3, t_total):
    tau2 = math.radians(float(PHIS[i2]))/(2*math.pi*s.F_HZ); tau3 = math.radians(float(PHIS[i3]))/(2*math.pi*s.F_HZ)
    rhs = s.rhs; z, zd = -MG/K, 0.0
    n = round(t_total/h); ncyc = n//STEPS_CYC
    zc = np.empty(ncyc); vc = np.empty(ncyc); lamc = np.empty(ncyc); N1 = np.empty(n); Irk = np.empty(n)
    fly = 0
    for i in range(n):
        t = i*h
        if i % STEPS_CYC == 0:
            c = i//STEPS_CYC; zc[c] = z; vc[c] = zd
            if c > 0: lamc[c-1] = fly/STEPS_CYC
            fly = 0
        k1z, k1d, f1 = rhs(z, zd, t, tau2, tau3)
        k2z, k2d, f2 = rhs(z+0.5*h*k1z, zd+0.5*h*k1d, t+0.5*h, tau2, tau3)
        k3z, k3d, f3 = rhs(z+0.5*h*k2z, zd+0.5*h*k2d, t+0.5*h, tau2, tau3)
        k4z, k4d, f4 = rhs(z+h*k3z, zd+h*k3d, t+h, tau2, tau3)
        N1[i] = f1; Irk[i] = (f1+2*f2+2*f3+f4)/6.0
        if f1 < 1e-9: fly += 1
        z = z + h*(k1z+2*k2z+2*k3z+k4z)/6.0
        zd = zd + h*(k1d+2*k2d+2*k3d+k4d)/6.0
    lamc[ncyc-1] = fly/STEPS_CYC
    return dict(zc=zc, vc=vc, lamc=lamc, N1=N1, Irk=Irk, zd_end=zd)

def period_of(vc, zc, c0, c1, kmax=150, nlast=100):
    """kleinstes k mit Wiederkehr der Zyklusstart-Zustaende ueber [c0,c1)."""
    for k in range(1, kmax+1):
        a, b = max(c0, c1-nlast-k), c1-k
        if b <= a: break
        if np.max(np.abs(vc[a+k:b+k]-vc[a:b])) < TOL_V and np.max(np.abs(zc[a+k:b+k]-zc[a:b])) < TOL_Z:
            return k
    return None

def window_stats(sim, c_start, n_cyc):
    i0, i1 = c_start*STEPS_CYC, (c_start+n_cyc)*STEPS_CYC
    N = sim['N1'][i0:i1]; T = n_cyc*T_CYC
    mean1 = float(N.mean()); meanrk = float(sim['Irk'][i0:i1].sum()*h/T)
    v0 = sim['vc'][c_start]; v1 = sim['vc'][c_start+n_cyc] if c_start+n_cyc < len(sim['vc']) else sim['zd_end']
    R = M*(v1-v0)/T          # innere Beitraege heben sich an Zyklusstarts exakt weg
    lo, hi = float(N.min()), float(N.max())
    return dict(n_cyc=n_cyc, t_start=c_start*T_CYC, delta_ppm=(mean1-MG)/MG*1e6, R_ppm=R/MG*1e6,
                Q_ppm=(mean1-meanrk)/MG*1e6, liftoff=float(np.mean(N < 1e-9)*100), skew=float(skew(N)),
                N_max=hi, N_min=lo, A=(hi-MG)/(MG-lo) if MG-lo > 1e-6 else float('nan'))

def klass(points, t_total, out_csv):
    rows = []
    for (i2, i3) in points:
        t0 = time.time(); sim = simulate(i2, i3, t_total); ncyc = len(sim['vc'])
        # Konvergenzzeit: erster Zyklus c, ab dem ueber 100 Zyklen Wiederkehr fuer ein k<=150 gilt
        per_end = period_of(sim['vc'], sim['zc'], 0, ncyc)
        t_conv = None
        if per_end:
            for c in range(50, ncyc-100-per_end, 10):
                if period_of(sim['vc'], sim['zc'], 0, c+100+per_end, kmax=per_end, nlast=100) == per_end:
                    t_conv = c*T_CYC; break
        # Regimewechsel: Blockmittel des Flugbruchteils (10 Bloecke)
        nb = 10; blk = sim['lamc'][:ncyc - ncyc % nb].reshape(nb, -1).mean(axis=1)*100
        # Fensterstatistik: fuenf 10-s-Fenster ab 50 s
        wins = [window_stats(sim, c, 100) for c in range(500, ncyc-100+1, 100)]
        Rs = [w['R_ppm'] for w in wins]; lams = [w['liftoff'] for w in wins]; As = [w['A'] for w in wins]
        # Fenster ueber ganze Orbitperioden, falls Periode erkannt
        wper = None
        if per_end:
            ncw = (100//per_end)*per_end
            wper = window_stats(sim, ncyc-ncw, ncw)
        if per_end and t_conv is not None:
            cls = 'periodisch (P%d) ab %.1f s' % (per_end, t_conv)
        elif blk.max()-blk.min() > 5:
            cls = 'Regimewechsel/intermittent'
        else:
            cls = 'aperiodisch, statistisch stationaer' if (max(lams)-min(lams) < 1.0) else 'aperiodisch, Fensterstatistik variabel'
        r = dict(i2=i2, i3=i3, klasse=cls, periode=per_end or -1, t_conv_s=t_conv if t_conv is not None else -1,
                 lam_block_min=float(blk.min()), lam_block_max=float(blk.max()),
                 R_10s_min=min(Rs), R_10s_max=max(Rs), lam_10s_min=min(lams), lam_10s_max=max(lams),
                 A_10s_min=min(As), A_10s_max=max(As),
                 R_orbitfenster=wper['R_ppm'] if wper else float('nan'), n_cyc_orbitfenster=wper['n_cyc'] if wper else -1,
                 lam_orbitfenster=wper['liftoff'] if wper else float('nan'), A_orbitfenster=wper['A'] if wper else float('nan'),
                 sek=round(time.time()-t0, 1))
        rows.append(r)
        print(json.dumps(r), flush=True)
    with open(out_csv, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        if f.tell() == 0: w.writeheader()
        w.writerows(rows)

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'klass':
        pts = [tuple(int(x) for x in p.split(',')) for p in sys.argv[2].split(';')]
        klass(pts, float(sys.argv[3]), sys.argv[4])
    elif mode == 'fenster':
        i2, i3 = int(sys.argv[2]), int(sys.argv[3]); t_burn = float(sys.argv[4]); ncw = int(sys.argv[5])
        sim = simulate(i2, i3, t_burn + ncw*T_CYC + 2*T_CYC)
        c0 = round(t_burn/T_CYC)
        print(json.dumps(dict(i2=i2, i3=i3, **window_stats(sim, c0, ncw))))
        print("Periode (letzte 100 Zyklen):", period_of(sim['vc'], sim['zc'], 0, len(sim['vc'])))
        print("zd an Zyklusstarts, letzte 12:", np.round(sim['vc'][-12:], 4).tolist())
