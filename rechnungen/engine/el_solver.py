"""P2/engine – Ereignislokalisierender Löser (EL) für das Engine-Modell, zur Kontrolle der Festschritt-RK4.

Modell identisch mit der Engine: z̈ = -g + N/M - abar(t), N = -K z - C ż, wenn z < 0 und N > 0, sonst 0.
Kontakt genau dann, wenn e(x) = min(-K z - C ż, -z) > 0. Übergänge werden als Nullstellen von e lokalisiert
(Kontakt -> frei: e fällt durch 0; frei -> Kontakt: e steigt durch 0, z. B. Aufsetzen bei z = 0 mit
Kraftsprung C|ż| oder Wiederanstieg von N bei z < 0). Integration mit DOP853 (rtol 1e-11, atol 1e-14)
stückweise zwischen den Knickstellen der Anregung (abar ist C0; je Modul Knicke bei t ≡ tau_k und
t ≡ tau_k + THOLD*T mod T) und den Zyklusgrenzen. Momente ∫N^p dt (p = 1..3) als Zusatzzustände -> exakte
kontinuierliche Mittel, Schiefe und Liftoff-Anteil; F_max aus dichter Ausgabe (Raster 5 µs je Kontaktstück).
"""
import math
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
import eng

M, G, K, C, T = eng.M, eng.G, eng.K, eng.C, eng.T_CYC
TH, TF, RTOP, RBOT = eng.THOLD, eng.TFAST, eng.RTOP, eng.RBOT
A_HOLD = -RTOP * (math.pi / (TH * T))**2
A_FAST = RBOT * (math.pi / (TF * T))**2


def zdd1(t):
    ph = (t % T) / T
    if ph < TH:
        return A_HOLD * math.sin(math.pi * ph / TH)
    return A_FAST * math.sin(math.pi * (ph - TH) / TF)


class EL:
    def __init__(self, phi2, phi3, rtol=1e-11, atol=1e-14):
        self.t2, self.t3 = (float(x) for x in eng.taus(phi2, phi3))
        self.rtol, self.atol = rtol, atol
        self.log = None
        self.n_fix = 0          # Zahl der nachträglich gefundenen Vorzeichenwechsel
        kinks = []
        for tau in (0.0, self.t2, self.t3):
            kinks += [tau % T, (tau + TH * T) % T]
        self.kinks = np.unique(np.round(np.array(kinks + [0.0]), 15))

    def abar(self, t):
        return (zdd1(t) + zdd1(t - self.t2) + zdd1(t - self.t3)) / 3.0

    def vS(self, zd, t):
        return float(eng.v_com(zd, np.array(t), self.t2, self.t3))

    def rhs_c(self, t, y):
        F = -K * y[0] - C * y[1]
        return [y[1], -G + F / M - self.abar(t), F, F * F, F * F * F]

    def rhs_f(self, t, y):
        return [y[1], -G - self.abar(t), 0.0, 0.0, 0.0]

    @staticmethod
    def ev(t, y):
        return min(-K * y[0] - C * y[1], -y[0])

    def run(self, z0, v0, t0, n_cyc, keep_series=False, fmax_dt=5e-6):
        """n_cyc Zyklen ab t0 (t0 sollte Zyklusbeginn der Auswertung sein). Rückgabe je Zyklus:
        I1, I2, I3 (∫N^p dt), t_free, F_max, n_touch; Poincaré-Zustände PZ, PV, PS."""
        y = np.array([z0, v0, 0.0, 0.0, 0.0])
        mode = 1 if self.ev(t0, y) > 0 else 0
        cyc = dict(I1=np.zeros(n_cyc), I2=np.zeros(n_cyc), I3=np.zeros(n_cyc), tfree=np.zeros(n_cyc),
                   Fmax=np.zeros(n_cyc), ntouch=np.zeros(n_cyc, int))
        PZ, PV, PS = np.zeros(n_cyc + 1), np.zeros(n_cyc + 1), np.zeros(n_cyc + 1)
        series = []
        t = t0
        for c in range(n_cyc):
            tc0 = t0 + c * T
            PZ[c], PV[c], PS[c] = y[0], y[1], self.vS(y[1], tc0)
            y[2:] = 0.0
            # Knickstellen in diesem Zyklus
            base = math.floor(tc0 / T) * T
            bps = sorted(set([b for b in (base + self.kinks).tolist() + (base + T + self.kinks).tolist()
                              if tc0 + 1e-13 < b < tc0 + T - 1e-13] + [tc0 + T]))
            fmax, tfree, ntouch = 0.0, 0.0, 0
            for tb in bps:
                while t < tb - 1e-15:
                    ev = self.ev
                    ev.terminal = True
                    ev.direction = -1 if mode == 1 else 1
                    sol = solve_ivp(self.rhs_c if mode == 1 else self.rhs_f, (t, tb), y, method='DOP853',
                                    rtol=self.rtol, atol=self.atol, events=ev, dense_output=True)
                    t_end = sol.t[-1]
                    # Absicherung gegen übersehene Vorzeichenwechsel von e innerhalb eines Schritts (kurze
                    # Ausflüge, z. B. Wiederaufsetzen kurz nach einer Ablösung mit e(t_start) = +1e-14):
                    # e auf der dichten Ausgabe im 10-µs-Raster prüfen und den ersten Wechsel nachschärfen.
                    nchk = max(20, int((t_end - t) / 1e-5) + 2)
                    tt = np.linspace(t, t_end, nchk)
                    Yc = sol.sol(tt)
                    Ev = np.minimum(-K * Yc[0] - C * Yc[1], -Yc[0])
                    inside = Ev > 0 if mode == 0 else Ev < 0          # "falsche" Seite für den Modus
                    kbad = None
                    if mode == 0 and Ev[0] > 0 and Ev[1] >= Ev[0]:
                        kbad = 0                                      # Scheinablösung: sofort wieder Kontakt
                    else:
                        seen_ok = ~inside
                        cand = np.where(inside[1:] & np.maximum.accumulate(seen_ok)[:-1])[0]
                        if cand.size and tt[cand[0] + 1] < t_end - 1e-12:
                            kbad = cand[0] + 1
                    if kbad is not None:
                        if kbad == 0:
                            te = t
                        else:
                            fe = lambda s_: float(min(-K * sol.sol(s_)[0] - C * sol.sol(s_)[1], -sol.sol(s_)[0]))
                            te = brentq(fe, tt[kbad - 1], tt[kbad], xtol=1e-15, rtol=1e-15)
                        self.n_fix += 1
                        if mode == 1:
                            tt2 = np.arange(t, te, fmax_dt)
                            if tt2.size:
                                Y = sol.sol(tt2)
                                fmax = max(fmax, float(np.max(-K * Y[0] - C * Y[1])))
                        else:
                            tfree += te - t
                        y = sol.sol(te).copy() if te > t else y
                        t = te
                        mode = 1 - mode
                        ntouch += mode == 1
                        if self.log is not None:
                            self.log.append((t, mode, y[0], y[1], -K * y[0] - C * y[1]))
                        continue
                    if mode == 1:
                        tt = np.arange(t, t_end, fmax_dt)
                        if tt.size:
                            Y = sol.sol(tt)
                            fmax = max(fmax, float(np.max(-K * Y[0] - C * Y[1])))
                        if keep_series:
                            series.append(('c', t, t_end))
                    else:
                        tfree += t_end - t
                    y = sol.y[:, -1].copy()
                    if sol.status == 1 and sol.t_events[0].size:     # Ereignis -> Moduswechsel
                        t = float(sol.t_events[0][0])
                        y = sol.y_events[0][0].copy()
                        mode = 1 - mode
                        ntouch += mode == 1
                        if self.log is not None:
                            self.log.append((t, mode, y[0], y[1], -K * y[0] - C * y[1]))
                    else:
                        t = tb
            cyc['I1'][c], cyc['I2'][c], cyc['I3'][c] = y[2], y[3], y[4]
            cyc['tfree'][c], cyc['Fmax'][c], cyc['ntouch'][c] = tfree, fmax, ntouch
        PZ[n_cyc], PV[n_cyc], PS[n_cyc] = y[0], y[1], self.vS(y[1], t0 + n_cyc * T)
        cyc.update(PZ=PZ, PV=PV, PS=PS, t0=t0)
        return cyc


def stats(r, c0, c1):
    Tw = (c1 - c0) * T
    m = r['I1'][c0:c1].sum() / Tw
    e2 = r['I2'][c0:c1].sum() / Tw
    e3 = r['I3'][c0:c1].sum() / Tw
    m2 = e2 - m * m
    m3 = e3 - 3 * m * e2 + 2 * m**3
    R = M * (r['PS'][c1] - r['PS'][c0]) / Tw
    return dict(dF_ppm=(m - eng.MG) / eng.MG * 1e6, R_ppm=R / eng.MG * 1e6, rest_N=m - eng.MG - R,
                skew=m3 / m2**1.5, lam=r['tfree'][c0:c1].sum() / Tw * 100, Fmax=r['Fmax'][c0:c1].max(),
                touch_per_cyc=r['ntouch'][c0:c1].mean())


def periodicity(r, n_last=50, pmax=40, tol_v=1e-8, tol_z=1e-10):
    v, z = r['PV'], r['PZ']
    n = v.size - 1
    for p in range(1, pmax + 1):
        if n < n_last + p:
            break
        idx = np.arange(n - n_last - p + 1, n - p + 1)
        if np.max(np.abs(v[idx + p] - v[idx])) < tol_v and np.max(np.abs(z[idx + p] - z[idx])) < tol_z:
            ok = (np.abs(v[p:] - v[:-p]) < tol_v) & (np.abs(z[p:] - z[:-p]) < tol_z)
            bad = np.where(~ok)[0]
            return p, (0 if bad.size == 0 else bad[-1] + 1) * T
    return -1, float('nan')


def pmap_el(phi2, phi3, x, t0, p=1):
    s = EL(phi2, phi3)
    r = s.run(x[0], x[1], t0, p)
    return np.array([r['PZ'][p], r['PV'][p]])


def newton_el(phi2, phi3, x0, t0=0.0, p=1, iters=8, h=(1e-8, 1e-6)):
    x = np.array(x0, float)
    J = np.eye(2)
    res = []
    for _ in range(iters):
        Fx = pmap_el(phi2, phi3, x, t0, p) - x
        res.append(float(np.max(np.abs(Fx / [1e-3, 1e-1]))))
        cols = []
        for j in range(2):
            e = np.zeros(2); e[j] = h[j]
            cols.append((pmap_el(phi2, phi3, x + e, t0, p) - pmap_el(phi2, phi3, x - e, t0, p)) / (2 * h[j]))
        J = np.column_stack(cols)
        if res[-1] < 1e-11:
            break
        x = x + np.linalg.solve(J - np.eye(2), -Fx)
    return x, np.linalg.eigvals(J), res


class ELRamp(EL):
    """EL mit Frequenzhochlauf (Phasen fest): Profilzeit Θ(t) wie eng.ramp_theta, rho = f/f0 von 0 auf 1
    in Tr (glatt, (1 - cos)/2). Während der Rampe ohne Knick-Aufteilung (adaptive Schrittweite), danach
    wie EL (Tr/2 ganzzahliges Vielfaches von T, daher keine Phasenverschiebung)."""

    def __init__(self, phi2, phi3, Tr=2.0, **kw):
        super().__init__(phi2, phi3, **kw)
        self.Tr = Tr
        assert abs((Tr / 2) / T - round((Tr / 2) / T)) < 1e-9

    def _rho(self, t):
        if t >= self.Tr:
            return t - self.Tr / 2, 1.0, 0.0
        x = math.pi * t / self.Tr
        return t / 2 - self.Tr / (2 * math.pi) * math.sin(x), 0.5 * (1 - math.cos(x)), math.pi / (2 * self.Tr) * math.sin(x)

    def abar(self, t):
        if t >= self.Tr:
            return super().abar(t)
        th, rho, rhod = self._rho(t)
        a = 0.0
        for tau in (0.0, self.t2, self.t3):
            u = th - tau
            a += zdd1(u) * rho * rho + float(eng.egg_v(np.array(u))) * rhod
        return a / 3.0

    def vS(self, zd, t):
        th, rho, _ = self._rho(t)
        return zd + rho * float(eng.v_modules(np.array(th), self.t2, self.t3))
