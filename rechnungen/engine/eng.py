"""P2/engine – Prüf-Engine (vektorisiert über "Bahnen" = Läufe), arithmetisch wie finesweep.run /
pcmms_v3a_phasen_sweep.simulate_point (RK4, Kontaktkraft aus Stufe 1, unilateraler Feder-Dämpfer,
t = t0 + i*dt; bei t0 = 0 identisch mit der Referenz t = i*DT), erweitert um:
  * beliebigen Anfangszustand (z0, v0) und Startzeit t0 je Lauf,
  * Frequenzrampe als Anlaufvariante (Phasen fest, rho(t) = f(t)/f0 von 0 auf 1, glatt),
  * zyklusweise Akkumulatoren (Linksrechteck-Summen, RK4-gewichtete Summe, Momente, min, max,
    Liftoff-Zählung, Aufsetzer) -> jedes Fenster aus ganzen Zyklen ist nachträglich auswertbar,
  * Poincaré-Schnitt (z, zdot, v_CoM) einmal je Zyklus (Zyklusbeginn, t = t0 + k*T).

Koordinaten (aus der Bewegungsgleichung der Engine abgeleitet):
  z      Lage des masselosen Rahmens/Auflagers (z < 0: Feder eingedrückt), ż dessen Geschwindigkeit
  Modul k: Lage relativ zum Rahmen  e(t - tau_k), e = Egg-Profil, Masse M/3
  Schwerpunkt  z_S = z + (1/3) * sum_k e(t - tau_k),  M * z̈_S = -M g + N(t)
  -> v_S(0) = ż(0) + (1/3) sum_k e'(-tau_k). Standardstart ż(0) = 0 -> v_S(0) = Mittel der Modulgeschwindigkeiten.

Es wird kein Repo-Code verändert; finesweep wird nur importiert (Parameter, z_egg_zdd).
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../code'))
import finesweep as fs  # noqa: E402

M, G, MG = fs.M, fs.G, fs.MG
F_HZ, T_CYC = fs.F_HZ, fs.T_CYC
K, C = fs.K, fs.C_DAMP
RTOP, RBOT, THOLD, TFAST = fs.RTOP, fs.RBOT, fs.THOLD, fs.TFAST
DT = fs.DT
OMEGA = 2 * np.pi * F_HZ
z_egg_zdd = fs.z_egg_zdd
VPK = RTOP * np.pi / (THOLD * T_CYC)          # Spitzengeschwindigkeit des Profils, 0,2417 m/s


def egg_v(t):
    """Profilgeschwindigkeit e'(t) (analytische Ableitung, C^0-stetig wegen RBOT = RTOP*TFAST/THOLD)."""
    ph = np.mod(t, T_CYC) / T_CYC
    return np.where(ph < THOLD, RTOP * np.pi / (THOLD * T_CYC) * np.cos(np.pi * ph / THOLD),
                    -RBOT * np.pi / (TFAST * T_CYC) * np.cos(np.pi * (ph - THOLD) / TFAST))


def egg_z(t):
    """Profillage e(t): Halteast +RTOP*sin, schneller Ast -RBOT*sin (zweimal integrierte z_egg_zdd)."""
    ph = np.mod(t, T_CYC) / T_CYC
    return np.where(ph < THOLD, RTOP * np.sin(np.pi * ph / THOLD),
                    -RBOT * np.sin(np.pi * (ph - THOLD) / TFAST))


def taus(phi2_deg, phi3_deg):
    """tau_k = phi_k/(2 pi f), phi in Grad -> Radiant wie in der Engine (math.radians/np.radians)."""
    phi2 = np.radians(np.asarray(phi2_deg, float))
    phi3 = np.radians(np.asarray(phi3_deg, float))
    return phi2 / (2 * np.pi * F_HZ), phi3 / (2 * np.pi * F_HZ)


def v_modules(t, tau2, tau3):
    return (egg_v(t) + egg_v(t - tau2) + egg_v(t - tau3)) / 3.0


def v_com(zd, t, tau2, tau3):
    return zd + v_modules(t, tau2, tau3)


def start_std(n):
    return np.full(n, -MG / K), np.zeros(n)


def start_imp(phi2, phi3, t0=0.0):
    """Impulskonsistent: v_S(t0) = 0 im Laborsystem -> ż(t0) = -Mittel der Modulgeschwindigkeiten;
    z(t0) = -Mg/K (statische Einfederung, Kraft beim Start Mg + C*|ż|... Feder wie Standardstart)."""
    tau2, tau3 = taus(phi2, phi3)
    t0 = np.broadcast_to(np.asarray(t0, float), tau2.shape)
    return np.full(tau2.shape, -MG / K), -v_modules(t0, tau2, tau3)


# ── Rampe (Frequenzhochlauf bei festen Phasen) ───────────────────────────────
def ramp_theta(t, Tr):
    """Profilzeit Θ(t) = ∫ rho dt, rho = (1 - cos(pi t/Tr))/2 für t < Tr, sonst 1.
    Rückgabe Θ, rho, rho'. Nach der Rampe Θ = t - Tr/2 (Tr/2 als Vielfaches von T wählen).
    Tr je Lauf (Array); Tr = 0 bedeutet keine Rampe (Θ = t exakt, rho = 1, rho' = 0)."""
    Tr = np.asarray(Tr, float)
    Trs = np.where(Tr > 0, Tr, 1.0)
    tt = np.minimum(t, Trs)
    on = t < Tr
    th = np.where(on, tt / 2 - Trs / (2 * np.pi) * np.sin(np.pi * tt / Trs), t - Tr / 2)
    rho = np.where(on, 0.5 * (1 - np.cos(np.pi * tt / Trs)), 1.0)
    rhod = np.where(on, np.pi / (2 * Trs) * np.sin(np.pi * tt / Trs), 0.0)
    return th, rho, rhod


def forcing(t, TAU, Tr=None):
    """Mittlere Modulbeschleunigung abar(t). TAU: (3, n) mit Zeile 0 = 0. Ohne Rampe
    arithmetisch wie die Engine: (zdd(t) + zdd(t - tau2) + zdd(t - tau3)) / 3."""
    if Tr is None:
        A = z_egg_zdd(t - TAU)
        return (A[0] + A[1] + A[2]) / 3.0
    th, rho, rhod = ramp_theta(t, Tr)
    U = th - TAU
    A = z_egg_zdd(U) * (rho * rho) + egg_v(U) * rhod
    return (A[0] + A[1] + A[2]) / 3.0


def contact(z, zd):
    F = -K * z - C * zd
    return np.where((z >= 0.0) | (F <= 0.0), 0.0, F)


def integrate(phi2, phi3, z0, v0, t0=0.0, dt=DT, n_cyc=150, Tr=None, keep_last=0, verbose=False, i0=0):
    """Integriert n_cyc ganze Anregungsperioden je Lauf. Gibt dict mit zyklusweisen Größen zurück:
      S1, S2, S3  Summen von (N1 - Mg)^p je Zyklus (N1 = Kontaktkraft der Stufe 1, wie die Engine speichert)
      SW          Summe von (N_RK4 - Mg), N_RK4 = (N1 + 2 N2 + 2 N3 + N4)/6 (RK4-gewichtet)
      MN, MX      Min/Max von N1 je Zyklus; LO Anzahl N1 < 1e-9; TD Aufsetzer (0 -> >0) je Zyklus
      PZ, PV      Zustand (z, ż) zu Zyklusbeginn, Zeilen 0..n_cyc (letzte = Endzustand)
      PS          v_S zu Zyklusbeginn
      tail        N1 der letzten keep_last Zyklen (optional)
    Tr: None (keine Rampe, Arithmetik exakt wie Engine) oder Array je Lauf (0 = keine Rampe).
    i0: globaler Schrittversatz für bitgenaue Fortsetzung (t = t0 + (i0 + i)*dt).
    """
    phi2 = np.atleast_1d(np.asarray(phi2, float))
    phi3 = np.atleast_1d(np.asarray(phi3, float))
    n = phi2.size
    tau2, tau3 = taus(phi2, phi3)
    if Tr is not None:
        Tr = np.broadcast_to(np.asarray(Tr, float), (n,)).copy()
        if not np.any(Tr > 0):
            Tr = None
    TAU = np.stack([np.zeros(n), tau2, tau3])
    t0 = np.broadcast_to(np.asarray(t0, float), (n,)).copy()
    n_per = int(round(T_CYC / dt))
    assert abs(n_per * dt - T_CYC) < 1e-12
    z = np.broadcast_to(np.asarray(z0, float), (n,)).copy()
    zd = np.broadcast_to(np.asarray(v0, float), (n,)).copy()
    out = {k: np.zeros((n_cyc, n)) for k in ('S1', 'S2', 'S3', 'SW', 'MN', 'MX', 'LO', 'TD')}
    PZ, PV, PS = np.zeros((n_cyc + 1, n)), np.zeros((n_cyc + 1, n)), np.zeros((n_cyc + 1, n))
    buf1 = np.empty((n_per, n))
    bufw = np.empty((n_per, n))
    tail = np.empty((keep_last * n_per, n)) if keep_last else None
    h2 = 0.5 * dt

    def vS(zd_, t_):
        if Tr is None:
            return v_com(zd_, t_, tau2, tau3)
        th, rho, _ = ramp_theta(t_, Tr)
        return zd_ + rho * (egg_v(th) + egg_v(th - tau2) + egg_v(th - tau3)) / 3.0

    # Nach Rampenende (alle Läufe t >= Tr) schneller Pfad mit verschobenen Phasen TAU + Tr/2
    # (physikalisch identisch, Rundung von t - Tr/2 - tau statt (t - Tr/2) - tau).
    TAU_R = TAU if Tr is None else TAU + Tr / 2
    for c in range(n_cyc):
        tc = t0 + (i0 + c * n_per) * dt
        PZ[c], PV[c], PS[c] = z, zd, vS(zd, tc)
        ramp_on = Tr is not None and bool(np.any(tc < Tr))
        Tr_c = Tr if ramp_on else None
        TAU_c = TAU if ramp_on else TAU_R
        for k in range(n_per):
            i = i0 + c * n_per + k
            t = t0 + i * dt
            a1 = forcing(t, TAU_c, Tr_c)
            ah = forcing(t + h2, TAU_c, Tr_c)
            a4 = forcing(t + dt, TAU_c, Tr_c)
            F1 = contact(z, zd)
            k1z, k1d = zd, -G + F1 / M - a1
            z2, d2 = z + h2 * k1z, zd + h2 * k1d
            F2 = contact(z2, d2)
            k2z, k2d = d2, -G + F2 / M - ah
            z3, d3 = z + h2 * k2z, zd + h2 * k2d
            F3 = contact(z3, d3)
            k3z, k3d = d3, -G + F3 / M - ah
            z4, d4 = z + dt * k3z, zd + dt * k3d
            F4 = contact(z4, d4)
            k4z, k4d = d4, -G + F4 / M - a4
            z = z + dt * (k1z + 2 * k2z + 2 * k3z + k4z) / 6.0
            zd = zd + dt * (k1d + 2 * k2d + 2 * k3d + k4d) / 6.0
            buf1[k] = F1
            bufw[k] = (F1 + 2 * F2 + 2 * F3 + F4) / 6.0
        d = buf1 - MG
        out['S1'][c] = d.sum(0)
        out['S2'][c] = (d * d).sum(0)
        out['S3'][c] = (d * d * d).sum(0)
        out['SW'][c] = (bufw - MG).sum(0)
        out['MN'][c] = buf1.min(0)
        out['MX'][c] = buf1.max(0)
        lo = buf1 < 1e-9
        out['LO'][c] = lo.sum(0)
        out['TD'][c] = (lo[:-1] & ~lo[1:]).sum(0)
        if keep_last and c >= n_cyc - keep_last:
            j = c - (n_cyc - keep_last)
            tail[j * n_per:(j + 1) * n_per] = buf1
        if verbose and (c + 1) % 100 == 0:
            print(f'  Zyklus {c + 1}/{n_cyc}', flush=True)
    tc = t0 + (i0 + n_cyc * n_per) * dt
    PZ[n_cyc], PV[n_cyc], PS[n_cyc] = z, zd, vS(zd, tc)
    out.update(PZ=PZ, PV=PV, PS=PS, tail=tail, n_per=n_per, dt=dt, t0=t0 + i0 * dt, phi2=phi2, phi3=phi3)
    return out


def window(res, c0, c1):
    """Kenngrößen je Lauf im Fenster der Zyklen [c0, c1)."""
    sl = slice(c0, c1)
    Nn = (c1 - c0) * res['n_per']
    A1 = res['S1'][sl].sum(0) / Nn
    A2 = res['S2'][sl].sum(0) / Nn
    A3 = res['S3'][sl].sum(0) / Nn
    m2 = A2 - A1**2
    m3 = A3 - 3 * A1 * A2 + 2 * A1**3
    W = res['SW'][sl].sum(0) / Nn
    T_w = (c1 - c0) * T_CYC
    R = M * (res['PS'][c1] - res['PS'][c0]) / T_w          # Randterm M*Δv_S/T_w
    Fmin = res['MN'][sl].min(0)
    return dict(dF_left_ppm=A1 / MG * 1e6, dF_rk4_ppm=W / MG * 1e6, R_ppm=R / MG * 1e6,
                rest_rk4_minus_R_N=W - R,
                skew=m3 / m2**1.5, lam=res['LO'][sl].sum(0) / Nn * 100.0,
                Fmin=Fmin, Fmax=res['MX'][sl].max(0), td_per_cyc=res['TD'][sl].mean(0),
                A=np.where(MG - Fmin > 1e-6, (res['MX'][sl].max(0) - MG) / np.maximum(MG - Fmin, 1e-12), np.nan))


def periodicity(res, lane, n_last=100, pmax=60, tol_v=1e-6, tol_z=1e-8):
    """Periode aus dem Poincaré-Schnitt (Zyklusbeginn): kleinstes p <= pmax mit
    max|x_{n+p} - x_n| < tol über die letzten n_last Zyklen. Einschwingzeit: frühester Zyklus n0, ab dem
    die Wiederkehr mit dieser Periode bis zum Ende gilt. Rückgabe (p oder -1, t_settle [s] oder nan)."""
    v = res['PV'][:, lane]
    z = res['PZ'][:, lane]
    nC = v.size - 1
    for p in range(1, pmax + 1):
        if nC < n_last + p:
            break
        idx = np.arange(nC - n_last - p + 1, nC - p + 1)
        if np.max(np.abs(v[idx + p] - v[idx])) < tol_v and np.max(np.abs(z[idx + p] - z[idx])) < tol_z:
            ok = (np.abs(v[p:] - v[:-p]) < tol_v) & (np.abs(z[p:] - z[:-p]) < tol_z)
            bad = np.where(~ok)[0]
            n0 = 0 if bad.size == 0 else bad[-1] + 1
            return p, float(res['t0'][lane] + n0 * T_CYC)
    return -1, float('nan')
