"""
sr_engine.py - Pruef-Engine der Gruppe symmetrie_randterm (P2).

Arithmetik wie finesweep.run / pcmms_v3a_phasen_sweep.py:
  RK4 mit festem Schritt dt, t_i = t0 + i*dt, Stufenzeiten t_i, t_i+dt/2, t_i+dt/2, t_i+dt,
  Kontaktkraft F = -K z - C zd, null wenn z >= 0 oder F <= 0,
  zdd = -g + F/M - abar(t),  abar = (a(t) + a(t - tau2) + a(t - tau3))/3,  tau = phi/(2 pi f).
Erweiterungen (nur Auswertung, nicht Bahn):
  - Startzeit t0 und Anfangszustand frei,
  - dt frei (ganzzahlige Schritte je Periode),
  - je Periode (Zyklus ab t0 + c*T): Summen Linksrechteck (Stufe-1-Kraft wie Engine),
    RK4-gewichtet (f1 + 2 f2 + 2 f3 + f4)/6, F^2, F^3, min, max, Liftoff-Zaehler,
    DFT-Summen fuer k = 1..KMAX (Zeitbezug absolut, t = t0 + i*dt),
  - Zustand und Schwerpunktgeschwindigkeit an jedem Zyklusbeginn,
  - wahlweise Profil 'egg' (Engine) oder 'skew' (zeitasymmetrisches Testprofil, nur Teil A).
Alle Groessen in SI-Einheiten, Phasen in Grad an der Schnittstelle.
"""
import numpy as np

M, G = 0.650, 9.81
MG = M * G
F_HZ = 10.0
T_CYC = 1.0 / F_HZ
RTOP = 0.005
THOLD = 0.65
TFAST = 1.0 - THOLD
RBOT = RTOP * TFAST / THOLD
K_REF, C_REF = 10000.0, 16.0
DT_REF = 5e-5
_A_HOLD = -RTOP * (np.pi / (THOLD * T_CYC)) ** 2
_A_FAST = RBOT * (np.pi / (TFAST * T_CYC)) ** 2
KMAX = 9


def z_egg_zdd(t):
    """identisch zu finesweep.z_egg_zdd"""
    phi = np.mod(t, T_CYC) / T_CYC
    return np.where(phi < THOLD, _A_HOLD * np.sin(np.pi * phi / THOLD),
                    _A_FAST * np.sin(np.pi * (phi - THOLD) / TFAST))


def z_egg_v(t):
    """Geschwindigkeit des Egg-Profils q(tau) (FV v2.7, Abschn. refprofil), dq/dt"""
    phi = np.mod(t, T_CYC) / T_CYC
    return np.where(phi < THOLD, RTOP * np.pi / (THOLD * T_CYC) * np.cos(np.pi * phi / THOLD),
                    -RBOT * np.pi / (TFAST * T_CYC) * np.cos(np.pi * (phi - THOLD) / TFAST))


# --- zeitasymmetrisches Testprofil (nur fuer Teil A, Spiegelungstest) -------------------------
# q(t) = A1 sin(w t) + A2 sin(2 w t + 0.6)  -> Beschleunigung; nicht zeitumkehrsymmetrisch,
# weil die Phase 0.6 rad der zweiten Harmonischen keine Wahl des Zeitursprungs zu 0 oder pi macht
# (Triadenphase 2*0 - 0.6 != 0, pi).  Amplituden so, dass Hub/Beschleunigung aehnlich egg.
_W = 2 * np.pi * F_HZ
_SK_A1, _SK_A2, _SK_PH = 0.0036, 0.0012, 0.6


def z_skew_zdd(t):
    return -(_W ** 2) * _SK_A1 * np.sin(_W * t) - (2 * _W) ** 2 * _SK_A2 * np.sin(2 * _W * t + _SK_PH)


def z_skew_v(t):
    return _W * _SK_A1 * np.cos(_W * t) + 2 * _W * _SK_A2 * np.cos(2 * _W * t + _SK_PH)


PROFILES = {'egg': (z_egg_zdd, z_egg_v), 'skew': (z_skew_zdd, z_skew_v)}


def run(phi2_deg, phi3_deg, n_cyc, dt=DT_REF, t0=0.0, z0=None, zd0=None, K=K_REF, C=C_REF,
        profile='egg', store_cycles=None, kmax=KMAX, log_td=False):
    """Simuliert n_cyc Perioden fuer alle Punkte (vektorisiert).
    t0: Startzeit (Skalar oder Array je Punkt).  store_cycles: (c_a, c_b) -> Zeitreihe der
    Stufe-1-Kraft fuer Zyklen c_a..c_b-1 wird zurueckgegeben (Speicher!).
    Rueckgabe: dict mit Arrays (Zyklus, Punkt)."""
    acc, vel = PROFILES[profile]
    phi2 = np.radians(np.atleast_1d(np.asarray(phi2_deg, float)))
    phi3 = np.radians(np.atleast_1d(np.asarray(phi3_deg, float)))
    n = phi2.size
    tau2 = phi2 / (2 * np.pi * F_HZ)
    tau3 = phi3 / (2 * np.pi * F_HZ)
    t0 = np.broadcast_to(np.asarray(t0, float), (n,)).copy()
    L = int(round(T_CYC / dt))
    assert abs(L * dt - T_CYC) < 1e-12, 'dt muss die Periode ganzzahlig teilen'
    z = np.full(n, -MG / K) if z0 is None else np.broadcast_to(np.asarray(z0, float), (n,)).copy()
    zd = np.zeros(n) if zd0 is None else np.broadcast_to(np.asarray(zd0, float), (n,)).copy()
    # DFT-Basis je Zyklus (exakt periodisch): exp(-i k w (j dt)); Phase von t0 + c T am Ende
    jj = np.arange(L)
    kk = np.arange(1, kmax + 1)
    E = np.exp(-1j * np.outer(jj * dt * 2 * np.pi * F_HZ, kk))       # (L, kmax)
    out = {k: np.empty((n_cyc, n)) for k in
           ('S1', 'SW', 'S2', 'S3', 'Fmin', 'Fmax', 'LO', 'z', 'zd', 'vcom', 'F0', 'tstart')}
    out['DFT'] = np.empty((n_cyc, n, kmax), complex)
    ser = None
    if store_cycles is not None:
        ca, cb = store_cycles
        ser = np.empty(((cb - ca) * L, n))
    h = dt
    half = 0.5 * dt
    td = []      # Aufsetzer: (Zyklus, j, Punkt, z_alt, zd_alt, z_neu, zd_neu, w_RK4, f1, F_folge)
    for c in range(n_cyc):
        i0 = c * L
        ii = i0 + jj
        # Zeiten exakt wie in der Engine: t = t0 + i*dt; Stufen t + 0.5*dt, t + dt
        tt = t0[None, :] + ii[:, None] * dt                            # (L, n)
        t2 = tt + 0.5 * dt
        t4 = tt + dt
        A1 = (acc(tt) + acc(tt - tau2) + acc(tt - tau3)) / 3.0
        A2 = (acc(t2) + acc(t2 - tau2) + acc(t2 - tau3)) / 3.0
        A4 = (acc(t4) + acc(t4 - tau2) + acc(t4 - tau3)) / 3.0
        F1 = np.empty((L, n))
        FW = np.empty((L, n))
        out['z'][c] = z
        out['zd'][c] = zd
        ts = tt[0]
        out['tstart'][c] = ts
        out['vcom'][c] = zd + (vel(ts) + vel(ts - tau2) + vel(ts - tau3)) / 3.0
        for j in range(L):
            F = -K * z - C * zd
            f1 = np.where((z >= 0.0) | (F <= 0.0), 0.0, F)
            k1z = zd
            k1d = -G + f1 / M - A1[j]
            z2 = z + half * k1z
            zd2 = zd + half * k1d
            F = -K * z2 - C * zd2
            f2 = np.where((z2 >= 0.0) | (F <= 0.0), 0.0, F)
            k2z = zd2
            k2d = -G + f2 / M - A2[j]
            z3 = z + half * k2z
            zd3 = zd + half * k2d
            F = -K * z3 - C * zd3
            f3 = np.where((z3 >= 0.0) | (F <= 0.0), 0.0, F)
            k3z = zd3
            k3d = -G + f3 / M - A2[j]
            z4 = z + h * k3z
            zd4 = zd + h * k3d
            F = -K * z4 - C * zd4
            f4 = np.where((z4 >= 0.0) | (F <= 0.0), 0.0, F)
            k4z = zd4
            k4d = -G + f4 / M - A4[j]
            if log_td:
                z_old, zd_old = z, zd
            z = z + h * (k1z + 2 * k2z + 2 * k3z + k4z) / 6.0
            zd = zd + h * (k1d + 2 * k2d + 2 * k3d + k4d) / 6.0
            F1[j] = f1
            FW[j] = (f1 + 2 * f2 + 2 * f3 + f4) / 6.0
            if log_td:
                cr = (z_old >= 0.0) & (z < 0.0)
                if cr.any():
                    for p_ in np.nonzero(cr)[0]:
                        Fn = -K * z[p_] - C * zd[p_]
                        td.append((c, j, p_, z_old[p_], zd_old[p_], z[p_], zd[p_], FW[j, p_], f1[p_],
                                   Fn if Fn > 0.0 else 0.0))
        out['S1'][c] = F1.sum(0)
        out['SW'][c] = FW.sum(0)
        out['S2'][c] = (F1 ** 2).sum(0)
        out['S3'][c] = (F1 ** 3).sum(0)
        out['Fmin'][c] = F1.min(0)
        out['Fmax'][c] = F1.max(0)
        out['LO'][c] = (F1 < 1e-9).sum(0)
        out['F0'][c] = F1[0]
        out['DFT'][c] = F1.T @ E
        if ser is not None and ca <= c < cb:
            ser[(c - ca) * L:(c - ca + 1) * L] = F1
    # Endzustand
    tend = t0 + n_cyc * L * dt
    F = -K * z - C * zd
    out['F_end'] = np.where((z >= 0.0) | (F <= 0.0), 0.0, F)
    out['z_end'], out['zd_end'] = z, zd
    out['vcom_end'] = zd + (vel(tend) + vel(tend - tau2) + vel(tend - tau3)) / 3.0
    out['t_end'] = tend
    out['L'], out['dt'], out['t0'], out['n'] = L, dt, t0, n
    out['phi2_deg'], out['phi3_deg'] = np.degrees(phi2), np.degrees(phi3)
    out['series'] = ser
    out['td'] = np.array(td, float).reshape(-1, 10)
    return out


def window(o, ca, cb, kmax=KMAX):
    """Observablen im Fenster aus den Zyklen ca..cb-1 (ganze Perioden).
    Mittel: 'mean_N1' (Linksrechteck = Engine), 'mean_RK4' (RK4-gewichtet), 'mean_TR' (Trapez).
    Randterm R = M*(vcom(Ende) - vcom(Anfang))/T_w."""
    L, dt = o['L'], o['dt']
    N = (cb - ca) * L
    Tw = N * dt
    S1 = o['S1'][ca:cb].sum(0)
    SW = o['SW'][ca:cb].sum(0)
    S2 = o['S2'][ca:cb].sum(0)
    S3 = o['S3'][ca:cb].sum(0)
    mu = S1 / N
    m2 = S2 / N - mu ** 2
    m3 = S3 / N - 3 * mu * S2 / N + 2 * mu ** 3
    F_end = o['F0'][cb] if cb < o['F0'].shape[0] else o['F_end']
    v_end = o['vcom'][cb] if cb < o['vcom'].shape[0] else o['vcom_end']
    v_sta = o['vcom'][ca]
    trap = (S1 - 0.5 * o['F0'][ca] + 0.5 * F_end) / N
    # DFT: Zeitbezug absolut; Phase des Zyklusbeginns t0 + c*T ist fuer ganze Perioden exp(-i k w t0)
    kk = np.arange(1, kmax + 1)
    ph0 = np.exp(-1j * np.outer(o['t0'] * 2 * np.pi * F_HZ, kk))
    Nk = 2.0 / N * o['DFT'][ca:cb].sum(0) * ph0
    R = M * (v_end - v_sta) / Tw
    return dict(Tw=Tw, mean_N1=mu, mean_RK4=SW / N, mean_TR=trap, skew=m3 / m2 ** 1.5,
                liftoff=o['LO'][ca:cb].sum(0) / N * 100.0, F_min=o['Fmin'][ca:cb].min(0),
                F_max=o['Fmax'][ca:cb].max(0), Nk=Nk, R=R, dv=v_end - v_sta,
                v_start=v_sta, v_end=v_end)


def s3_images(p2, p3):
    """Die sechs Bilder (phi2, phi3) der Gruppe S3 und die zugehoerige Zeitverschiebung (Grad der
    Referenzphase, die neu zur Null wird).  Rueckgabe: Liste (Name, phi2', phi3', phi_ref)."""
    w = lambda x: float(np.mod(x, 360.0))
    return [('id', w(p2), w(p3), 0.0),
            ('(23)', w(p3), w(p2), 0.0),
            ('(12)', w(-p2), w(p3 - p2), w(p2)),
            ('(123)', w(p3 - p2), w(-p2), w(p2)),
            ('(13)', w(p2 - p3), w(-p3), w(p3)),
            ('(132)', w(-p3), w(p2 - p3), w(p3))]


def gaps(p2, p3):
    s = sorted([0.0, float(np.mod(p2, 360)), float(np.mod(p3, 360))])
    return (s[1] - s[0], s[2] - s[1], 360.0 - s[2])
