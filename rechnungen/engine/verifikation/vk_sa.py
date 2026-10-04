"""Gegenprüfung P2/engine – halbanalytischer ereignisgenauer Löser ("SA").

Unabhängiger Rechenweg (kein Runge-Kutta, kein DOP853):
  * Freiflug: Schwerpunkt ballistisch, Z(t) = Z_a + V_a*s - g*s^2/2, z = Z - ebar(t) (geschlossen).
  * Kontakt: lineare ODE z'' + 2*alpha*z' + w0^2*z = -g - abar(t); abar ist zwischen den Knicken eine
    Summe von Sinustermen -> geschlossene Lösung (partikulär + gedämpft homogen), Neustart an jedem Knick.
  * Ereignisse: Kontakt -> frei bei N = -K z - C z' = 0 (fallend); frei -> Kontakt bei min(-z, -K z - C z') > 0.
    Erste Vorzeichenwechsel auf 1-µs-Raster, dann brentq (xtol 1e-16).
  * Momente int N^p dt (p = 1..3) mit Gauss-Legendre (8 Knoten je <= 50 µs) -> exakte Zeitmittel.
Rückgabe je Zyklus: I1..I3, t_frei, Fmax, Fmin_kontakt, Aufsetzer; Poincaré-Zustand (z, z') zu Zyklusbeginn.
"""
import math
import numpy as np
from scipy.optimize import brentq
import vk_model as m

GRID = 1e-6
GL_X, GL_W = np.polynomial.legendre.leggauss(8)


class SA:
    def __init__(self, phi2_deg, phi3_deg, taus=None):
        if taus is None:
            self.taus = (0.0, float(m.tau_of(phi2_deg)), float(m.tau_of(phi3_deg)))
        else:
            self.taus = tuple(float(x) for x in taus)
        kinks = []
        for tk in self.taus:
            kinks += [tk % m.T, (tk + m.THOLD * m.T) % m.T]
        self.kinks = np.unique(np.array(kinks))
        self.n_ev = 0

    # ---- Anregung als Sinusterme auf einem knickfreien Stück -------------------------------------
    def terms(self, ta):
        """Für das Stück ab ta (knickfrei bis zum nächsten Knick): Liste (A, w, psi) mit
        a_k(ta + s) = A*sin(w*s + psi)."""
        out = []
        for tk in self.taus:
            u = (ta - tk) % m.T
            # Rundung am Knick: Stück gehört zu dem Ast, der ab ta gilt
            if u >= m.T - 1e-13:
                u = 0.0
            if u < m.THOLD * m.T - 1e-13:
                out.append((m.AH, m.WH, m.WH * u))
            else:
                out.append((m.AF, m.WF, m.WF * max(u - m.THOLD * m.T, 0.0)))
        return out

    def contact_piece(self, ta, za, va):
        """Geschlossene Lösung ab ta: Funktionen z(s), zd(s) für s >= 0 (bis zum nächsten Knick gültig)."""
        a, w0, wd = m.ALPHA, m.W0, m.WD
        Gs, ws = [], []
        for (A, w, psi) in self.terms(ta):
            Gs.append(-(A / 3.0) * np.exp(1j * psi) / (w0**2 - w**2 + 2j * a * w))
            ws.append(w)
        Gs, ws = np.array(Gs), np.array(ws)
        zp0 = -m.G / w0**2 + np.sum(np.imag(Gs))
        vp0 = np.sum(np.imag(1j * ws * Gs))
        Ah = za - zp0
        Bh = (va - vp0 + a * Ah) / wd

        def zz(s):
            s = np.asarray(s, float)
            E = np.exp(1j * np.multiply.outer(s, ws))
            zp = -m.G / w0**2 + np.imag(E @ Gs)
            vp = np.imag(E @ (1j * ws * Gs))
            ex = np.exp(-a * s)
            c, sn = np.cos(wd * s), np.sin(wd * s)
            z = zp + ex * (Ah * c + Bh * sn)
            zd = vp + ex * ((-a * Ah + wd * Bh) * c + (-a * Bh - wd * Ah) * sn)
            return z, zd
        return zz

    def free_piece(self, ta, za, va):
        Za = za + float(m.ebar(ta, self.taus))
        Va = va + float(m.ebar_v(ta, self.taus))

        def zz(s):
            s = np.asarray(s, float)
            t = ta + s
            Z = Za + Va * s - 0.5 * m.G * s * s
            V = Va - m.G * s
            return Z - m.ebar(t, self.taus), V - m.ebar_v(t, self.taus)
        return zz

    @staticmethod
    def Nf(z, zd):
        return -m.K * z - m.C * zd

    def run(self, z0, v0, t0, n_cyc, keep=False):
        """n_cyc Zyklen ab t0 (Zyklusgrenzen t0 + c*T)."""
        z, zd = float(z0), float(v0)
        mode = 1 if (z < 0 and self.Nf(z, zd) > 0) else 0
        R = {k: np.zeros(n_cyc) for k in ('I1', 'I2', 'I3', 'tfree', 'Fmax', 'Fminc', 'ntd')}
        PZ, PV, PS = np.zeros(n_cyc + 1), np.zeros(n_cyc + 1), np.zeros(n_cyc + 1)
        log = [] if keep else None
        for c in range(n_cyc):
            tc = t0 + c * m.T
            PZ[c], PV[c] = z, zd
            PS[c] = zd + float(m.ebar_v(tc, self.taus))
            base = math.floor(tc / m.T) * m.T
            bps = [b for b in np.concatenate([base + self.kinks, base + m.T + self.kinks])
                   if tc + 1e-12 < b < tc + m.T - 1e-12]
            bps = sorted(bps) + [tc + m.T]
            I1 = I2 = I3 = tfree = 0.0
            fmax, fminc, ntd = 0.0, np.inf, 0
            t = tc
            for tb in bps:
                while t < tb - 1e-15:
                    L = tb - t
                    n = max(4, int(math.ceil(L / GRID)) + 1)
                    s = np.linspace(0.0, L, n)
                    if mode == 1:
                        f = self.contact_piece(t, z, zd)
                        zz_, vv_ = f(s)
                        Ns = self.Nf(zz_, vv_)
                        idx = np.where(Ns[1:] <= 0.0)[0]
                        if idx.size:
                            j = idx[0] + 1
                            g = lambda x: float(self.Nf(*f(x)))
                            se = brentq(g, s[j - 1], s[j], xtol=1e-16, rtol=1e-15) if Ns[j - 1] > 0 else s[j - 1]
                            self.n_ev += 1
                        else:
                            se = L
                        # Momente und Extrema auf [0, se]
                        if se > 0:
                            nsub = max(1, int(math.ceil(se / 5e-5)))
                            edges = np.linspace(0.0, se, nsub + 1)
                            mid = 0.5 * (edges[1:] + edges[:-1])[:, None]
                            hw = 0.5 * (edges[1:] - edges[:-1])[:, None]
                            xs = (mid + hw * GL_X[None, :]).ravel()
                            ws = (hw * GL_W[None, :]).ravel()
                            Nq = self.Nf(*f(xs))
                            I1 += np.dot(ws, Nq); I2 += np.dot(ws, Nq**2); I3 += np.dot(ws, Nq**3)
                            sel = s <= se
                            Ng = Ns[sel]
                            if Ng.size:
                                fmax = max(fmax, float(Ng.max())); fminc = min(fminc, float(Ng.min()))
                        zn, vn = f(se)
                        z, zd = float(zn), float(vn)
                        t = t + se
                        if se < L:
                            mode = 0
                            if keep:
                                log.append((t, 0, z, zd))
                    else:
                        f = self.free_piece(t, z, zd)
                        zz_, vv_ = f(s)
                        H = np.minimum(-zz_, self.Nf(zz_, vv_))
                        idx = np.where(H[1:] > 0.0)[0]
                        if idx.size:
                            j = idx[0] + 1
                            g = lambda x: float(np.minimum(-f(x)[0], self.Nf(*f(x))))
                            se = brentq(g, s[j - 1], s[j], xtol=1e-16, rtol=1e-15) if H[j - 1] <= 0 else s[j - 1]
                            self.n_ev += 1
                        else:
                            se = L
                        zn, vn = f(se)
                        z, zd = float(zn), float(vn)
                        tfree += se
                        t = t + se
                        if se < L:
                            mode = 1
                            ntd += 1
                            # Am Aufsetzpunkt kann min(...) numerisch 0 sein -> Kraft >= 0 erzwingen
                            if keep:
                                log.append((t, 1, z, zd))
                t = tb
            R['I1'][c], R['I2'][c], R['I3'][c] = I1, I2, I3
            R['tfree'][c], R['Fmax'][c], R['Fminc'][c], R['ntd'][c] = tfree, fmax, fminc, ntd
        tc = t0 + n_cyc * m.T
        PZ[n_cyc], PV[n_cyc] = z, zd
        PS[n_cyc] = zd + float(m.ebar_v(tc, self.taus))
        R.update(PZ=PZ, PV=PV, PS=PS, t0=t0, mode_end=mode, log=log)
        return R


def stats(R, c0, c1):
    Tw = (c1 - c0) * m.T
    mu = R['I1'][c0:c1].sum() / Tw
    e2 = R['I2'][c0:c1].sum() / Tw
    e3 = R['I3'][c0:c1].sum() / Tw
    m2 = e2 - mu * mu
    m3 = e3 - 3 * mu * e2 + 2 * mu**3
    lam = R['tfree'][c0:c1].sum() / Tw * 100.0
    Rb = m.M * (R['PS'][c1] - R['PS'][c0]) / Tw
    fmin = 0.0 if lam > 0 else R['Fminc'][c0:c1].min()
    return dict(dF_ppm=(mu - m.MG) / m.MG * 1e6, R_ppm=Rb / m.MG * 1e6, rest_N=mu - m.MG - Rb,
                skew=m3 / m2**1.5, lam=lam, Fmax=R['Fmax'][c0:c1].max(), Fmin=fmin,
                td=R['ntd'][c0:c1].mean())


def period(R, n_last=40, pmax=40, tol_v=1e-9, tol_z=1e-11):
    v, z = R['PV'], R['PZ']
    n = v.size - 1
    for p in range(1, pmax + 1):
        if n < n_last + p:
            break
        idx = np.arange(n - n_last - p + 1, n - p + 1)
        if np.max(np.abs(v[idx + p] - v[idx])) < tol_v and np.max(np.abs(z[idx + p] - z[idx])) < tol_z:
            ok = (np.abs(v[p:] - v[:-p]) < tol_v) & (np.abs(z[p:] - z[:-p]) < tol_z)
            bad = np.where(~ok)[0]
            return p, (0 if bad.size == 0 else bad[-1] + 1) * m.T
    return -1, float('nan')


def pmap(sa, x, t0, p):
    r = sa.run(x[0], x[1], t0, p)
    return np.array([r['PZ'][p], r['PV'][p]])


def floquet(sa, x0, t0, p=1, iters=10, h=(1e-9, 1e-7), verbose=False):
    """Newton auf P^p(x) = x (zentrale Differenzen); Rückgabe Fixpunkt, Multiplikatoren, Residuen."""
    x = np.array(x0, float)
    res = []
    J = None
    for it in range(iters):
        Px = pmap(sa, x, t0, p)
        Fx = Px - x
        res.append(float(max(abs(Fx[0]) / 1e-3, abs(Fx[1]) / 1e-1)))
        cols = []
        for j in range(2):
            e = np.zeros(2); e[j] = h[j]
            cols.append((pmap(sa, x + e, t0, p) - pmap(sa, x - e, t0, p)) / (2 * h[j]))
        J = np.column_stack(cols)
        if verbose:
            print(f'   Newton {it}: res {res[-1]:.2e}', flush=True)
        if res[-1] < 1e-12:
            break
        x = x + np.linalg.solve(J - np.eye(2), -Fx)
    return x, np.linalg.eigvals(J), res
