"""z1_km02_modell.py - Gegenpruefung KM-02 (3-FG-Zellmodell, Validierung gegen Engine und lineare Loesung).

Eigener Rechenweg: analytische Fourier-Koeffizienten, lineare Loesung ueber T(k w) mit FFT-Synthese
(kmax = 8000), Zeitbereich mit scipy DOP853 (adaptiv, nicht RK4), Engine nur als Referenzdaten
(finesweep.run, unveraendert importiert).
"""
import time
import numpy as np
from scipy.integrate import solve_ivp
import zm

t0 = time.time()
# ---------------- (0) Profil: analytische Koeffizienten gegen FFT der eigenen Profilfunktion ----------------
n = 2 ** 16
tt = np.arange(n) * zm.T_CYC / n
cfft = np.fft.rfft(zm.accel(tt)) / n
ca = zm.ck_analytic(12)
print('=== (0) Egg-Beschleunigung: A_k = 2|c_k| analytisch gegen FFT (2^16 Punkte) ===')
for k in range(1, 10):
    print(f' k={k}: A_k = {2*abs(ca[k]):.4f} m/s^2 (FFT {2*abs(cfft[k]):.4f}), arg c_k = {np.degrees(np.angle(ca[k])):8.2f} deg')
print(f' c_0 analytisch = {abs(ca[0]):.2e} (Gleichanteil null, da RBOT = RTOP*TFAST/THOLD)')

KMAX = 8000
NS = 16000                     # Stichproben je Periode (Engine: 2000 -> jede 8. Stichprobe)
CK = zm.ck_analytic(KMAX)


def linear_cells(geo, phi, K, C, kmax=KMAX, ns=NS):
    """Zellkraefte (ohne statischen Anteil) auf dem Raster ns je Periode, FFT-Synthese."""
    k = np.arange(kmax + 1)
    g = (geo.m[:, None] * CK[None, :kmax + 1]) * np.exp(-1j * np.outer(np.radians(phi), k))
    F = np.zeros((3, kmax + 1), complex)
    if K is None:
        T = geo.T(0.0, None)
        F[:, 1:] = T @ g[:, 1:]
    else:
        for kk in range(1, kmax + 1):
            F[:, kk] = geo.T(zm.OMEGA * kk, K, C) @ g[:, kk]
    spec = np.zeros((3, ns // 2 + 1), complex)
    spec[:, :kmax + 1] = F * ns
    return np.fft.irfft(spec, ns, axis=1), F


def geo_of(name, mu):
    if name == 'G0':
        return zm.Geo(Rm=zm.R_C, psi0=0.0, mu=mu)
    if name == 'G60h':
        return zm.Geo(Rm=zm.R_C / 2, psi0=60.0, mu=mu)
    raise ValueError


# ---------------- (a) Summe der Zellkraefte gegen die Engine (REF, mu = 1, G0, Triphasik) ----------------
print('\n=== (a) Summe der linearen Zellkraefte (eigenes Modell) gegen Engine finesweep.run(120, 240) ===')
geo = geo_of('G0', 1.0)
Fc, Fk = linear_cells(geo, (0, 120, 240), zm.K_REF, zm.C_REF)
stat = zm.static_cell_loads(geo)
N_lin = (Fc + stat[:, None]).sum(0)
print(f' statische Zelllasten {stat} N (Summe {stat.sum():.6f}, M g = {zm.MG:.6f})')
import finesweep as fs
t1 = time.time()
out, ser = fs.run([120.0], [240.0], store_series=True, series_len=int(0.3 / fs.DT))
eng = ser[:, 0]
i0 = fs.N_BURN  # Engine-Stichprobe i: t = (N_BURN + i)*DT; 5 s = 50 Perioden -> Phase 0
idx = (np.arange(eng.size) * 8) % NS
d = np.abs(N_lin[idx] - eng)
print(f' Engine-Lauf {time.time()-t1:.0f} s; Engine F_min {out["F_min"][0]:.6f}, F_max {out["F_max"][0]:.6f}, '
      f'mean {out["F_mean"][0]:.9f}, liftoff {out["liftoff"][0]:.3f} %')
Ne = N_lin[::8]
print(f' eigenes Modell (2000 Stichproben/Periode wie Engine): F_min {Ne.min():.6f}, F_max {Ne.max():.6f}, mean {Ne.mean():.9f}')
print(f' max|N_3FG,linear - N_Engine| ueber 0,3 s ab 5 s: {d.max():.2e} N')
# Entkopplung Hub/Kippen bei symmetrischer Anordnung: Nebendiagonale Mq[0,1:] und Kq[0,1:]
print(f' Kopplung Hub-Kippen in Mq: {np.abs(geo.Mq[0,1:]).max():.1e}, in Kq: {np.abs(geo.Kq(1.0)[0,1:]).max():.1e}')
# mu = 1, G0: Mq = (M/3) Bc Bc^T  -> drei unabhaengige Einmassenschwinger (siehe PROTOKOLL)
print(f' mu=1, G0: max|Mq - (M/3) Bc Bc^T| = {np.abs(geo.Mq - zm.M/3*geo.Bc@geo.Bc.T).max():.1e}')

# ---------------- (b) lineare Zellkraefte/Momente der 12 P2-Faelle ----------------
print('\n=== (b) Eigene lineare Loesung fuer die 12 Faelle aus k3 (F_min Zelle, R+1, R-2) ===')
cases = [('REF', 1.0, 'G0'), ('REF', 1.0, 'G60h'), ('REF', 0.462, 'G0'), ('REF', 0.462, 'G60h'),
         ('STEIF', 0.462, 'G0'), ('STEIF', 0.462, 'G60h')]
res_b = {}
for lab, mu, gname in cases:
    K, C = (zm.K_REF, zm.C_REF) if lab == 'REF' else (zm.K_ST, zm.C_ST)
    geo = geo_of(gname, mu)
    stat = zm.static_cell_loads(geo)
    for phi in ((0, 120, 240), (0, 110, 240)):
        Fc, Fk = linear_cells(geo, phi, K, C, kmax=2000, ns=4000)
        F = Fc + stat[:, None]
        Mx, My = zm.moments(geo, Fk)
        Pp1, Pm1 = zm.rot_components(Mx[1], My[1])
        Pp2, Pm2 = zm.rot_components(Mx[2], My[2])
        res_b[(lab, mu, gname, phi)] = (F, K, C)
        print(f' {lab:5s} mu={mu:.3f} {gname:4s} phi={phi}: F_min Zelle {F[:, ::2].min():9.5f} N (2000/Periode), '
              f'R+1 {abs(Pp1):.5f}, R-2 {abs(Pm2):.5f} N m')

# ---------------- (c) Zeitbereich DOP853 (bilateral) gegen lineare Loesung ----------------
print('\n=== (c) DOP853 (rtol 1e-10) bilateral gegen eigene lineare Loesung, letzte 2 Perioden nach 3 s ===')


def ode_cells(geo, phi, K, C, t_end=3.0):
    tau = np.radians(phi) / zm.OMEGA
    Kq, Cq = geo.Kq(K), geo.Kq(C)
    Minv = np.linalg.inv(geo.Mq)
    mvec = np.array([geo.Mf, 0, 0]) + geo.Bm @ geo.m
    q0 = np.linalg.solve(Kq, -zm.G * mvec)

    def rhs(t, y):
        q, v = y[:3], y[3:]
        sdd = zm.accel(t - tau)
        f = -zm.G * mvec - Kq @ q - Cq @ v - geo.Bm @ (geo.m * sdd)
        return np.concatenate([v, Minv @ f])
    ts = t_end - 2 * zm.T_CYC + np.arange(400) * zm.T_CYC / 200
    sol = solve_ivp(rhs, (0, t_end), np.concatenate([q0, np.zeros(3)]), method='DOP853', rtol=1e-10,
                    atol=1e-13, t_eval=ts, max_step=2e-4)
    q, v = sol.y[:3], sol.y[3:]
    w, wd = geo.Bc.T @ q, geo.Bc.T @ v
    return ts, -(K / 3) * w - (C / 3) * wd


for key in [('REF', 1.0, 'G0', (0, 120, 240)), ('REF', 0.462, 'G0', (0, 110, 240)),
            ('STEIF', 0.462, 'G60h', (0, 120, 240))]:
    F, K, C = res_b[key]
    geo = geo_of(key[2], key[1])
    t1 = time.time()
    ts, Fode = ode_cells(geo, key[3], K, C)
    # lineare Loesung auf denselben Zeiten (Phase mod Periode; Raster 4000/Periode -> Index 20*j)
    idx = (np.round(np.mod(ts, zm.T_CYC) / zm.T_CYC * 4000).astype(int)) % 4000
    dmax = np.abs(Fode - F[:, idx]).max()
    print(f' {key}: max|F_DOP853 - F_linear| = {dmax:.2e} N ({time.time()-t1:.0f} s)')

print(f'\nLaufzeit {time.time()-t0:.0f} s')
