"""Gegenprüfung P2/engine – eigene vektorisierte RK4 in Schwerpunktkoordinaten ("RK4-S").

Zustand (Z, V) = Schwerpunktlage/-geschwindigkeit. z = Z - ebar(t), z' = V - ebar'(t) (analytisch),
  Z' = V,  V' = -g + N(z, z')/M.
Andere Diskretisierung als die Engine (dort Rahmenkoordinate z mit expliziter Anregung -abar(t)):
die Modulbewegung geht hier exakt über ebar, ebar' in die Kontaktkraft ein. Für dt -> 0 identisch.
ebar, ebar' werden je Punkt für eine Periode auf dem Halbschrittraster tabelliert (periodisch exakt).
Optional Frequenzrampe: Profilzeit theta(t) = int rho, rho = (1-cos(pi t/Tr))/2 (wie Gruppe, aber hier
ohne rho'-Term nötig: z = Z - ebar(theta), z' = V - rho*ebar'(theta)).
Akkumuliert je Zyklus: S1 (Linksrechteck N1), SW (RK4-gewichtet), S2, S3, Min, Max, Liftoff-Zahl, PS/PZ.
"""
import numpy as np
import vk_model as m


def make_tables(taus_list, dt):
    n_per = int(round(m.T / dt))
    assert abs(n_per * dt - m.T) < 1e-15
    j = np.arange(2 * n_per) * (dt / 2)
    EB = np.empty((2 * n_per, len(taus_list)))
    EV = np.empty_like(EB)
    for i, taus in enumerate(taus_list):
        EB[:, i] = m.ebar(j, taus)
        EV[:, i] = m.ebar_v(j, taus)
    return EB, EV, n_per


def ramp_theta(t, Tr):
    if t >= Tr:
        return t - Tr / 2, 1.0
    x = np.pi * t / Tr
    return t / 2 - Tr / (2 * np.pi) * np.sin(x), 0.5 * (1 - np.cos(x))


def run(phi2, phi3, start='std', dt=5e-5, n_cyc=100, Tr=0.0, z0=None, v0=None, t0_cyc=0, verbose=False):
    """phi2, phi3 Arrays in Grad. start: 'std' (z=-Mg/K, z'=0), 'imp' (V=0), 'user' (z0, v0 Rahmen).
    Tr > 0: Rampe ab t=0 aus Ruhe (Module stehen, z=-Mg/K, z'=0). t0_cyc: Startzeit in Zyklen (ganzzahlig)."""
    phi2 = np.atleast_1d(np.asarray(phi2, float)); phi3 = np.atleast_1d(np.asarray(phi3, float))
    n = phi2.size
    taus_list = [(0.0, float(m.tau_of(a)), float(m.tau_of(b))) for a, b in zip(phi2, phi3)]
    EB, EV, n_per = make_tables(taus_list, dt)
    TA = np.array(taus_list)  # (n,3)
    z = np.full(n, -m.MG / m.K) if z0 is None else np.broadcast_to(np.asarray(z0, float), (n,)).copy()
    zd = np.zeros(n) if v0 is None else np.broadcast_to(np.asarray(v0, float), (n,)).copy()
    if start == 'imp':
        zd = -EV[0].copy()
    Z = z + EB[0]
    V = zd + EV[0]
    if Tr > 0:
        assert t0_cyc == 0
        Z = z + EB[0]          # theta(0) = 0, rho(0) = 0 -> Module stehen bei ebar(0)
        V = zd.copy()
    acc = {k: np.zeros((n_cyc, n)) for k in ('S1', 'S2', 'S3', 'SW', 'MN', 'MX', 'LO')}
    PS = np.zeros((n_cyc + 1, n)); PZ = np.zeros((n_cyc + 1, n)); PV = np.zeros((n_cyc + 1, n))
    h = dt; h2 = dt / 2
    n_ramp = int(np.ceil(Tr / dt)) if Tr > 0 else 0

    def eb_ramp(t):
        th, rho = ramp_theta(t, Tr)
        eb = sum(m.e_pos(th - TA[:, k]) for k in range(3)) / 3.0
        ev = rho * sum(m.e_vel(th - TA[:, k]) for k in range(3)) / 3.0
        return eb, ev

    i_glob = t0_cyc * n_per
    for c in range(n_cyc):
        s1 = np.zeros(n); s2 = np.zeros(n); s3 = np.zeros(n); sw = np.zeros(n)
        mn = np.full(n, np.inf); mx = np.full(n, -np.inf); lo = np.zeros(n)
        if c * n_per < n_ramp:
            eb0, ev0 = eb_ramp(c * n_per * dt)
        else:
            jj = (2 * (i_glob % n_per)) % (2 * n_per)
            eb0, ev0 = EB[jj], EV[jj]
        PZ[c] = Z - eb0; PV[c] = V - ev0; PS[c] = V
        for k in range(n_per):
            i = c * n_per + k
            if i < n_ramp:
                t = i * dt
                ea, va_ = eb_ramp(t); eh, vh = eb_ramp(t + h2); ee, ve = eb_ramp(t + h)
            else:
                jj = 2 * ((i_glob + k) % n_per)
                ea, va_ = EB[jj], EV[jj]
                eh, vh = EB[jj + 1], EV[jj + 1]
                j2 = (jj + 2) % (2 * n_per)
                ee, ve = EB[j2], EV[j2]
            F1 = m.contact_force(Z - ea, V - va_)
            k1Z, k1V = V, -m.G + F1 / m.M
            Z2, V2 = Z + h2 * k1Z, V + h2 * k1V
            F2 = m.contact_force(Z2 - eh, V2 - vh)
            k2Z, k2V = V2, -m.G + F2 / m.M
            Z3, V3 = Z + h2 * k2Z, V + h2 * k2V
            F3 = m.contact_force(Z3 - eh, V3 - vh)
            k3Z, k3V = V3, -m.G + F3 / m.M
            Z4, V4 = Z + h * k3Z, V + h * k3V
            F4 = m.contact_force(Z4 - ee, V4 - ve)
            k4V = -m.G + F4 / m.M
            Z = Z + h * (k1Z + 2 * k2Z + 2 * k3Z + V4) / 6.0
            V = V + h * (k1V + 2 * k2V + 2 * k3V + k4V) / 6.0
            d = F1 - m.MG
            s1 += d; s2 += d * d; s3 += d * d * d
            sw += (F1 + 2 * F2 + 2 * F3 + F4) / 6.0 - m.MG
            np.minimum(mn, F1, out=mn); np.maximum(mx, F1, out=mx)
            lo += F1 < 1e-9
        i_glob += n_per
        acc['S1'][c] = s1; acc['S2'][c] = s2; acc['S3'][c] = s3; acc['SW'][c] = sw
        acc['MN'][c] = mn; acc['MX'][c] = mx; acc['LO'][c] = lo
        if verbose and (c + 1) % 50 == 0:
            print(f'   Zyklus {c + 1}/{n_cyc}', flush=True)
    if n_cyc * n_per < n_ramp:
        ebE, evE = eb_ramp(n_cyc * n_per * dt)
    else:
        jj = (2 * (i_glob % n_per)) % (2 * n_per)
        ebE, evE = EB[jj], EV[jj]
    PZ[n_cyc] = Z - ebE; PV[n_cyc] = V - evE; PS[n_cyc] = V
    acc.update(PS=PS, PZ=PZ, PV=PV, n_per=n_per, dt=dt, phi2=phi2, phi3=phi3, t0=t0_cyc * m.T)
    return acc


def window(r, c0, c1):
    sl = slice(c0, c1)
    Nn = (c1 - c0) * r['n_per']
    A1 = r['S1'][sl].sum(0) / Nn; A2 = r['S2'][sl].sum(0) / Nn; A3 = r['S3'][sl].sum(0) / Nn
    m2 = A2 - A1**2; m3 = A3 - 3 * A1 * A2 + 2 * A1**3
    W = r['SW'][sl].sum(0) / Nn
    Tw = (c1 - c0) * m.T
    Rb = m.M * (r['PS'][c1] - r['PS'][c0]) / Tw
    return dict(dF_left_ppm=A1 / m.MG * 1e6, dF_rk4_ppm=W / m.MG * 1e6, R_ppm=Rb / m.MG * 1e6,
                Q_ppm=(A1 - W) / m.MG * 1e6, skew=m3 / m2**1.5, lam=r['LO'][sl].sum(0) / Nn * 100,
                Fmin=r['MN'][sl].min(0), Fmax=r['MX'][sl].max(0))
