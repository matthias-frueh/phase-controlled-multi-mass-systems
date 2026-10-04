"""
v_exakt.py - ereignisgesteuerte, halbanalytische Integration des Kontaktmodells (Gegenpruefer, P2).
Unabhaengig vom festen RK4-Raster der Engine:
  * Flugphase (kein Kontakt) ANALYTISCH:  z_f'' = -g - abar(t)  =>
        z_f(t) = z0 + v0 (t-t0) - g (t-t0)^2/2 - [qbar(t) - qbar(t0) - qbar'(t0)(t-t0)]
    Kontaktbeginn = erste Nullstelle von min(-z_f, (-K z_f - C v_f)/K) (Abtastung 5 us + brentq).
  * Kontaktphase: lineare ODE M z'' = -Mg - K z - C z' - M abar(t), solve_ivp DOP853 (rtol 1e-12),
    Ereignis Kontaktkraft -K z - C v = 0 (abfallend) = Abheben.
Kontaktgesetz wie Modell: F = -K z - C v nur wenn z < 0 und F > 0.
Liefert Segmentliste; Kraft N(t) per Dense Output auswertbar.
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
import v_engine as ve

M, G, MG, T = ve.M, ve.G, ve.MG, ve.T


class Bahn:
    def __init__(self, phi2, phi3, K=ve.K0, C=ve.C0, rtol=1e-12, atol=1e-15):
        self.tau2 = phi2 / 360.0 * T
        self.tau3 = phi3 / 360.0 * T
        self.K, self.C, self.rtol, self.atol = K, C, rtol, atol
        self.seg = []          # (typ, t_a, t_b, daten)

    def pb(self, t):
        return ve.pbar(np.asarray(t, float), self.tau2, self.tau3)

    def flug(self, t0, z0, v0, t):
        q0, qd0, _ = self.pb(t0)
        q, qd, _ = self.pb(t)
        dt = t - t0
        z = z0 + v0 * dt - 0.5 * G * dt ** 2 - (q - q0 - qd0 * dt)
        v = v0 - G * dt - (qd - qd0)
        return z, v

    def rhs(self, t, y):
        _, _, a = ve.pbar(np.array([t]), self.tau2, self.tau3)
        return [y[1], -G + (-self.K * y[0] - self.C * y[1]) / M - a[0]]

    def integriere(self, t0, z0, v0, t_end):
        t, z, v = t0, z0, v0
        K, C = self.K, self.C
        in_kontakt = (z < 0) and (-K * z - C * v > 0)
        while t < t_end - 1e-15:
            if in_kontakt:
                ev = lambda tt, y: -K * y[0] - C * y[1]
                ev.terminal = True
                ev.direction = -1
                sol = solve_ivp(self.rhs, (t, t_end), [z, v], method='DOP853', rtol=self.rtol,
                                atol=self.atol, events=ev, dense_output=True, max_step=2e-3)
                if sol.t_events[0].size:
                    tb = sol.t_events[0][0]
                    yb = sol.sol(tb)
                else:
                    tb = sol.t[-1]
                    yb = sol.y[:, -1]
                self.seg.append(('K', t, tb, sol.sol))
                t, z, v = tb, float(yb[0]), float(yb[1])
                in_kontakt = False
            else:
                # Flug: suche Kontaktbeginn
                def ind(tt):
                    zz, vv = self.flug(t, z, v, tt)
                    return np.minimum(-zz, (-K * zz - C * vv) / K)
                step = 5e-6
                tb = None
                ta = t
                # grobe Abtastung in Bloecken
                while ta < t_end:
                    tg = ta + step * np.arange(1, 2001)
                    tg = tg[tg <= t_end + step]
                    vals = ind(tg)
                    idx = np.nonzero(vals > 0)[0]
                    if idx.size:
                        i0 = idx[0]
                        lo = tg[i0 - 1] if i0 > 0 else ta
                        hi = tg[i0]
                        if ind(lo) > 0:
                            lo = ta
                        tb = brentq(lambda s: float(ind(np.array([s]))[0]), lo, hi, xtol=1e-15, rtol=1e-15)
                        break
                    ta = tg[-1]
                if tb is None or tb >= t_end:
                    self.seg.append(('F', t, t_end, (t, z, v)))
                    zz, vv = self.flug(t, z, v, np.array([t_end]))
                    t, z, v = t_end, float(zz[0]), float(vv[0])
                    break
                self.seg.append(('F', t, tb, (t, z, v)))
                zz, vv = self.flug(t, z, v, np.array([tb]))
                t, z, v = tb, float(zz[0]), float(vv[0])
                in_kontakt = True
        return t, z, v

    def kraft(self, tt):
        """N(t) fuer ein Zeitarray (innerhalb integrierter Segmente)."""
        tt = np.asarray(tt, float)
        out = np.zeros_like(tt)
        for typ, a, b, d in self.seg:
            if typ != 'K':
                continue
            m = (tt >= a) & (tt < b)
            if m.any():
                y = d(tt[m])
                out[m] = np.maximum(-self.K * y[0] - self.C * y[1], 0.0)
        return out

    def zustand(self, tt):
        """(z_f, v_f) fuer ein Zeitarray."""
        tt = np.asarray(tt, float)
        z = np.full_like(tt, np.nan); v = np.full_like(tt, np.nan)
        for typ, a, b, d in self.seg:
            m = (tt >= a) & (tt < b)
            if not m.any():
                continue
            if typ == 'K':
                y = d(tt[m]); z[m] = y[0]; v[m] = y[1]
            else:
                z[m], v[m] = self.flug(d[0], d[1], d[2], tt[m])
        return z, v

    def impuls(self, a, b):
        """Exaktes Integral von N ueber [a,b] aus den Kontaktsegmenten (Gauss-Legendre je Teilstueck)."""
        xg, wg = np.polynomial.legendre.leggauss(40)
        tot = 0.0
        for typ, s0, s1, d in self.seg:
            if typ != 'K':
                continue
            lo, hi = max(a, s0), min(b, s1)
            if hi <= lo:
                continue
            nsub = max(1, int(np.ceil((hi - lo) / 2e-4)))
            ed = np.linspace(lo, hi, nsub + 1)
            for u, w_ in zip(ed[:-1], ed[1:]):
                tq = 0.5 * (w_ - u) * xg + 0.5 * (w_ + u)
                y = d(tq)
                tot += 0.5 * (w_ - u) * np.sum(wg * np.maximum(-self.K * y[0] - self.C * y[1], 0.0))
        return tot
