"""PCMMS v3a: 19x19-Phasensweep mit adaptivem Burn-in (Zyklus-Wiederkehr) und
Randterm/Quadratur-Zerlegung. Solver (rhs, RK4-Arithmetik) unveraendert aus
pcmms_v3a_phasen_sweep.py; Stufenkraefte werden zusaetzlich mitgefuehrt.

Kriterium: Fenster (100 Zyklen) wird am Zyklusstart geoeffnet, sobald fuer ein
k in 1..8 ueber die letzten 20 Zyklen  |zd(t+k*T_cyc) - zd(t)| < TOL_V  und
|z(t+k*T_cyc) - z(t)| < TOL_Z  gilt (fruehestens bei T_BURN_MIN, spaetestens
bei T_BURN_MAX; dann Flag converged=False).
Ausgabe je Punkt: N1-Mittel (Original-Linksrechteck), RK4-gewichtetes Mittel,
Randterm R, Quadratur Q, Funktionale aus N1, Burn-in-Zeit, Periode k, Jitter.
"""
import importlib.util, math, csv, json, sys, time, os
import numpy as np
from scipy.stats import skew

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'code', 'pcmms_v3a_phasen_sweep.py')  # Pfad angepasst: Engine aus code/
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resweep_19x19_burnin.csv')  # Pfad angepasst
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resweep_19x19_burnin.log')  # Pfad angepasst
T_BURN_MIN, T_BURN_MAX = 5.0, 40.0
T_WIN = 10.0
TOL_V, TOL_Z, N_LAST = 1e-3, 1e-4, 20
K_LIST = [1,2,3,4,5,6,7,8,10,20,25,50,100]

spec = importlib.util.spec_from_file_location('v3a', SRC)
s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
h = s.DT; M = s.M; MG = s.MG; K = s.K; G = s.G
T_CYC = s.T_CYC; THOLD = s.THOLD; TFAST = s.TFAST; RTOP = s.RTOP; RBOT = s.RBOT
STEPS_CYC = round(T_CYC/h); WIN_STEPS = round(T_WIN/h)
assert abs(STEPS_CYC*h - T_CYC) < 1e-12

def egg_v(t):
    phase = (t % T_CYC)/T_CYC
    if phase < THOLD:
        return RTOP*math.pi/(THOLD*T_CYC)*math.cos(math.pi*phase/THOLD)
    return -RBOT*math.pi/(TFAST*T_CYC)*math.cos(math.pi*(phase-THOLD)/TFAST)

def vcom(zd, t, tau2, tau3):
    return zd + (egg_v(t) + egg_v(t-tau2) + egg_v(t-tau3))/3.0

def converged(zh, vh):
    """Wiederkehr der Zyklusstart-Zustaende ueber die letzten N_LAST Zyklen fuer
    k aus K_LIST (k=100 entspricht dem Randterm eines 10-s-Fensters < 10 ppm)."""
    n = len(vh); best_j = None
    for k in K_LIST:
        if n < N_LAST + k:
            break
        jv = max(abs(vh[i+k]-vh[i]) for i in range(n-N_LAST-k, n-k))
        if k == 1:
            best_j = jv
        if jv < TOL_V:
            jz = max(abs(zh[i+k]-zh[i]) for i in range(n-N_LAST-k, n-k))
            if jz < TOL_Z:
                return k, jv
    return None, best_j

def run_point(i2, i3, phi2_deg, phi3_deg):
    tau2 = math.radians(phi2_deg)/(2*math.pi*s.F_HZ)
    tau3 = math.radians(phi3_deg)/(2*math.pi*s.F_HZ)
    rhs = s.rhs
    z, zd = -MG/K, 0.0
    zh, vh = [], []
    i = 0; t_open = None; k_per = None; jit = None
    n_max = round(T_BURN_MAX/h)
    # ---- Burn-in mit Wiederkehr-Kriterium ----
    while True:
        t = i*h
        if i % STEPS_CYC == 0:
            zh.append(z); vh.append(zd)
            if t >= T_BURN_MIN - 1e-9:
                k_per, jit = converged(zh, vh)
                if k_per is not None or i >= n_max:
                    t_open = t
                    break
        k1z, k1d, f1 = rhs(z, zd, t, tau2, tau3)
        k2z, k2d, f2 = rhs(z+0.5*h*k1z, zd+0.5*h*k1d, t+0.5*h, tau2, tau3)
        k3z, k3d, f3 = rhs(z+0.5*h*k2z, zd+0.5*h*k2d, t+0.5*h, tau2, tau3)
        k4z, k4d, f4 = rhs(z+h*k3z, zd+h*k3d, t+h, tau2, tau3)
        z = z + h*(k1z+2*k2z+2*k3z+k4z)/6.0
        zd = zd + h*(k1d+2*k2d+2*k3d+k4d)/6.0
        i += 1
    # ---- Auswertefenster: 100 Zyklen ab t_open ----
    vc_s = vcom(zd, t_open, tau2, tau3); zd_s = zd
    N1 = np.empty(WIN_STEPS); sumrk = 0.0; touchdowns = 0; Fprev = None
    for j in range(WIN_STEPS):
        t = (i+j)*h
        k1z, k1d, f1 = rhs(z, zd, t, tau2, tau3)
        k2z, k2d, f2 = rhs(z+0.5*h*k1z, zd+0.5*h*k1d, t+0.5*h, tau2, tau3)
        k3z, k3d, f3 = rhs(z+0.5*h*k2z, zd+0.5*h*k2d, t+0.5*h, tau2, tau3)
        k4z, k4d, f4 = rhs(z+h*k3z, zd+h*k3d, t+h, tau2, tau3)
        N1[j] = f1
        sumrk += (f1+2*f2+2*f3+f4)/6.0
        if Fprev is not None and Fprev == 0.0 and f1 > 0.0:
            touchdowns += 1
        Fprev = f1
        z = z + h*(k1z+2*k2z+2*k3z+k4z)/6.0
        zd = zd + h*(k1d+2*k2d+2*k3d+k4d)/6.0
    t_end = (i+WIN_STEPS)*h
    vc_e = vcom(zd, t_end, tau2, tau3)
    mean1 = float(np.mean(N1)); meanrk = sumrk*h/T_WIN
    R = M*(vc_e-vc_s)/T_WIN
    lo, hi = float(N1.min()), float(N1.max())
    D = MG - lo
    return dict(i2=i2, i3=i3, phi2_deg=repr(phi2_deg), phi3_deg=repr(phi3_deg),
        t_burn_s=t_open, converged=k_per is not None, period_k=k_per if k_per else -1,
        jitter_v_m_s=jit,
        mean_N1_N=mean1, mean_RK4_N=meanrk,
        delta_ppm=(mean1-MG)/MG*1e6, R_ppm=R/MG*1e6, Q_ppm=(mean1-meanrk)/MG*1e6,
        E_RK4_N=meanrk-MG-R,
        skew=float(skew(N1)), liftoff_pct=float(np.mean(N1 < 1e-9)*100),
        N_max_N=hi, N_min_N=lo, A_Mg=(hi-MG)/D if D > 1e-6 else float('nan'),
        touchdowns_per_s=touchdowns/T_WIN, zd_start=zd_s, zd_end=zd)

def main():
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 1e9
    phis = np.linspace(0.0, 360.0, s.N_GRID, endpoint=False)
    done = set()
    if os.path.exists(OUT):
        for r in csv.DictReader(open(OUT)):
            done.add((int(r['i2']), int(r['i3'])))
    fields = None; t0 = time.time(); n_done = 0
    for i2 in range(s.N_GRID):
        for i3 in range(s.N_GRID):
            if (i2, i3) in done:
                continue
            if time.time() - t0 > budget:
                with open(LOG, 'a') as f: f.write(f'PAUSE nach {n_done} Punkten ({time.time()-t0:.0f} s)\n')
                return
            tp = time.time()
            r = run_point(i2, i3, float(phis[i2]), float(phis[i3]))
            if fields is None:
                fields = list(r.keys())
                new = not os.path.exists(OUT) or os.path.getsize(OUT) == 0
                w = csv.DictWriter(open(OUT, 'a', newline=''), fieldnames=fields)
                if new:
                    w.writeheader()
            w = csv.DictWriter(open(OUT, 'a', newline=''), fieldnames=fields)
            w.writerow(r); n_done += 1
            with open(LOG, 'a') as f:
                f.write(f"{i2:2d} {i3:2d} phi=({phis[i2]:7.3f},{phis[i3]:7.3f}) burn={r['t_burn_s']:5.1f}s conv={r['converged']} k={r['period_k']} "
                        f"delta={r['delta_ppm']:8.1f} R={r['R_ppm']:8.1f} Q={r['Q_ppm']:6.1f} lift={r['liftoff_pct']:6.2f} "
                        f"skew={r['skew']:7.4f} Nmax={r['N_max_N']:7.3f} A={r['A_Mg']:6.3f}  [{time.time()-tp:4.1f}s, gesamt {time.time()-t0:6.0f}s]\n")
    with open(LOG, 'a') as f:
        f.write(f"FERTIG: {n_done} Punkte in {time.time()-t0:.0f} s\n")

if __name__ == '__main__':
    main()
