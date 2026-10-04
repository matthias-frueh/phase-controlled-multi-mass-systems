"""
vk_lib.py – unabhängige Prüfbibliothek des Gegenprüfers (P2, "auslegung/verifikation").

Bewusst ANDERER Rechenweg als die Gruppe (mu_modell.py: analytische Fourierkoeffizienten + irfft;
RK4 mit festem Schritt) und als code/linear_solver.py (FFT des abgetasteten Profils):

 (1) Linearer Kontaktast EXAKT im Zeitbereich: Die Profilbeschleunigung ist zwischen ihren Knickstellen
     (Beginn Halte- bzw. Rückholphase je Modul) eine Summe von Sinusfunktionen. Je Abschnitt wird die
     Partikulärlösung geschlossen angegeben (komplexe Amplitude / D(Ω), D = K − MΩ² + iCΩ), die homogene
     Lösung mit der geschlossenen Formel des gedämpften Schwingers. Die periodische Lösung folgt aus der
     Ein-Perioden-Abbildung s(T) = Φ·s(0) + p (Schießverfahren, 2×2 linear) – keine FFT, kein Zeitschritt.
 (2) Nichtlinear (einseitiger Kelvin-Voigt-Kontakt wie Engine: N = −Kx − Cẋ nur wenn x < 0 und N > 0):
     ereignisgesteuerte, abschnittsweise EXAKTE Lösung. Kontaktphase: wie (1). Flugphase: ẍ = −g − Q(t)/M
     geschlossen doppelt integriert. Moduswechsel per Abtastung (Schritt h) + brentq auf der geschlossenen Form.
     Liftoff-Anteil λ = exakte Flugzeit / Fensterlänge (nicht Stichprobenanteil).

Modell (eigene Herleitung): Körperkoordinate x (x < 0: Kontakt eingefedert), Restmasse m0, Module m_j mit
vorgegebener Relativbeschleunigung a_j(t) = a(t − τ_j), τ_j = φ_j/(2πf) = φ_j[°]/(360·f).
Impulssatz: m0·ẍ + Σ m_j (ẍ + a_j) = N − M·g  ⇒  M·ẍ = N − M·g − Q(t),  Q(t) = Σ_j m_j·a_j(t).
Gleiche Module: m_j = w_j·μ·M/3 (w_j ∈ {0,1}). Engine: μ = 1, w = (1,1,1).
Profil (wie Engine): s = (t mod T)/T; s < TH: a = −RTOP·(π/(TH·T))²·sin(π s/TH); sonst a = RBOT·(π/(TF·T))²·
sin(π (s−TH)/TF), RTOP = TH·Hub, RBOT = TF·Hub (Hub = Spitze-Spitze = RTOP + RBOT; Referenz 7,6923 mm).
SI-Einheiten; Phasen an der Schnittstelle in Grad.
"""
import numpy as np
from scipy.optimize import brentq

G = 9.81
M_REF = 0.650
TH = 0.65
TF = 1.0 - TH
HUB_REF = 0.005 / TH          # 7,6923 mm
F_REF = 10.0
K_REF, C_REF = 1.0e4, 16.0


def zeta_to_C(zeta, K, M=M_REF):
    return 2.0 * zeta * np.sqrt(K * M)


def fn_of(K, M=M_REF):
    return np.sqrt(K / M) / (2 * np.pi)


def eps_of(mu, hub, f):
    """ε = μ·a_h/g, a_h = RTOP·(π/(TH·T))² = π²·Hub·f²/TH (unabhängig nachgerechnet)."""
    rtop = TH * hub
    return mu * rtop * (np.pi * f / TH) ** 2 / G


# ───────────────────────────── Profil ──────────────────────────────────────
def acc(t, hub, f):
    T = 1.0 / f
    s = np.mod(t, T) / T
    rtop, rbot = TH * hub, TF * hub
    return np.where(s < TH, -rtop * (np.pi / (TH * T)) ** 2 * np.sin(np.pi * s / TH),
                    rbot * (np.pi / (TF * T)) ** 2 * np.sin(np.pi * (s - TH) / TF))


class System:
    """Parameter eines Laufs: Phasen (3,) in Grad, Gewichte (3,), μ, Hub, f, K, C, M."""

    def __init__(self, phis_deg, weights, mu, hub, f, K, C, M=M_REF):
        self.phis = np.asarray(phis_deg, float)
        self.w = np.asarray(weights, float)
        self.mu, self.hub, self.f, self.K, self.C, self.M = mu, hub, f, K, C, M
        self.T = 1.0 / f
        self.tau = np.mod(self.phis / (360.0 * f), self.T)
        self.m = self.w * mu * M / 3.0
        rtop, rbot = TH * hub, TF * hub
        self.Ah = rtop * (np.pi / (TH * self.T)) ** 2
        self.Af = rbot * (np.pi / (TF * self.T)) ** 2
        self.Oh = np.pi / (TH * self.T)
        self.Of = np.pi / (TF * self.T)
        act = np.where(self.w != 0)[0]
        self.act = act
        kinks = []
        for j in act:
            kinks += [self.tau[j], np.mod(self.tau[j] + TH * self.T, self.T)]
        kinks = np.unique(np.round(np.array(kinks + [0.0]), 15))
        self.kinks = np.sort(kinks)          # in [0, T)
        if K is not None:
            self.wn = np.sqrt(K / M)
            self.sig = C / (2 * M)
            self.wd = np.sqrt(self.wn ** 2 - self.sig ** 2)

    # Sinusterme der Last Q(t) = Σ m_j a_j(t) im Abschnitt, der t_mid enthält: Liste (amp, Ω, ψ),
    # Q = Σ amp·sin(Ω t + ψ)
    def terms(self, t_mid):
        out = []
        T = self.T
        for j in self.act:
            tl = t_mid - self.tau[j]
            n = np.floor(tl / T)
            s = (tl - n * T) / T
            t0 = self.tau[j] + n * T                       # Beginn der Haltephase dieses Zyklus
            if s < TH:
                out.append((-self.m[j] * self.Ah, self.Oh, -self.Oh * t0))
            else:
                out.append((self.m[j] * self.Af, self.Of, -self.Of * (t0 + TH * T)))
        return out

    def Q(self, t):
        return sum(self.m[j] * acc(t - self.tau[j], self.hub, self.f) for j in self.act)

    # ── Kontaktphase: x = −Mg/K + y, M ÿ + C ẏ + K y = −Q(t) ──
    def _part(self, terms, t):
        yp = np.zeros_like(t, dtype=float)
        vp = np.zeros_like(t, dtype=float)
        for amp, Om, psi in terms:
            D = self.K - self.M * Om ** 2 + 1j * self.C * Om
            e = np.exp(1j * (Om * t + psi))
            yp += np.imag(-amp * e / D)
            vp += np.imag(-amp * 1j * Om * e / D)
        return yp, vp

    def _hom(self, d0, d1, tau):
        s, wd, wn = self.sig, self.wd, self.wn
        ex = np.exp(-s * tau)
        c, sn = np.cos(wd * tau), np.sin(wd * tau)
        y = ex * (d0 * c + (d1 + s * d0) / wd * sn)
        v = ex * (d1 * c - (s * d1 + wn ** 2 * d0) / wd * sn)
        return y, v

    def _contact_eval_terms(self, terms, ta, xa, va, t):
        ya = xa + self.M * G / self.K
        ypa, vpa = self._part(terms, np.array([ta]))
        yp, vp = self._part(terms, np.atleast_1d(np.asarray(t, float)))
        yh, vh = self._hom(ya - ypa[0], va - vpa[0], np.atleast_1d(t) - ta)
        y, v = yp + yh, vp + vh
        x = y - self.M * G / self.K
        N = -self.K * x - self.C * v
        return x, v, N

    # ── Flugphase: ẍ = −g − Q(t)/M ──
    def _flight_terms(self, terms, ta, xa, va, t):
        t = np.atleast_1d(np.asarray(t, float))
        tau = t - ta
        x = xa + va * tau - 0.5 * G * tau ** 2
        v = va - G * tau
        for amp, Om, psi in terms:
            u = -(np.sin(Om * t + psi) - np.sin(Om * ta + psi)) / Om ** 2 + np.cos(Om * ta + psi) * tau / Om
            ud = -(np.cos(Om * t + psi) - np.cos(Om * ta + psi)) / Om
            x -= amp * u / self.M
            v -= amp * ud / self.M
        return x, v

    # ── periodische lineare Lösung (Schießverfahren) ──
    def _segments(self, t0, t1):
        """Knickabschnitte in [t0, t1] (absolute Zeiten)."""
        T = self.T
        n0, n1 = int(np.floor(t0 / T)) - 1, int(np.ceil(t1 / T)) + 1
        ks = np.concatenate([self.kinks + n * T for n in range(n0, n1 + 1)])
        ks = ks[(ks > t0 + 1e-15) & (ks < t1 - 1e-15)]
        b = np.concatenate([[t0], np.sort(ks), [t1]])
        return list(zip(b[:-1], b[1:]))

    def periodic_linear(self, nsamp=2000, rigid=False, fine=None):
        """Periodische lineare Lösung. Rückgabe dict: t (nsamp Stützstellen je Periode, t_n = n·T/nsamp),
        N, x. rigid: N = Mg + Q(t). fine: zusätzliche feinere Abtastung zur Minimumssuche."""
        T = self.T
        if rigid or self.K is None:
            t = np.arange(nsamp) * T / nsamp
            N = self.M * G + self.Q(t)
            return dict(t=t, N=N, x=np.zeros_like(t))
        segs = self._segments(0.0, T)

        def propagate(xa, va):
            x, v = xa, va
            for a, b in segs:
                terms = self.terms(0.5 * (a + b))
                xx, vv, _ = self._contact_eval_terms(terms, a, x, v, np.array([b]))
                x, v = xx[0], vv[0]
            return x, v
        # y = x + Mg/K; Abbildung affin in (y, v)
        x0s = -self.M * G / self.K
        p = np.array(propagate(x0s, 0.0)) - np.array([x0s, 0.0])
        e1 = np.array(propagate(x0s + 1e-3, 0.0)) - np.array([x0s, 0.0]) - p
        e2 = np.array(propagate(x0s, 1e-3)) - np.array([x0s, 0.0]) - p
        Phi = np.column_stack([e1, e2]) / 1e-3
        d = np.linalg.solve(np.eye(2) - Phi, p)
        xs0, vs0 = x0s + d[0], d[1]
        n = nsamp if fine is None else fine
        tg = np.arange(n) * T / n
        N = np.empty(n)
        X = np.empty(n)
        x, v = xs0, vs0
        for a, b in segs:
            terms = self.terms(0.5 * (a + b))
            msk = (tg >= a) & (tg < b)
            if msk.any():
                xx, vv, NN = self._contact_eval_terms(terms, a, x, v, tg[msk])
                N[msk], X[msk] = NN, xx
            xx, vv, _ = self._contact_eval_terms(terms, a, x, v, np.array([b]))
            x, v = xx[0], vv[0]
        per_err = abs(x - xs0) + abs(v - vs0) / max(self.wn, 1.0)
        return dict(t=tg, N=N, x=X, per_err=per_err, x0=xs0, v0=vs0)

    # ── nichtlineare, ereignisgesteuerte Lösung ──
    def simulate(self, t_end, t_eval_start, x0=None, v0=0.0, h=5e-6):
        """Einseitiger Kontakt. Start bei t = 0 mit x0 (Standard: statische Ruhelage −Mg/K), v0.
        Rückgabe: lam [%] = exakte Flugzeit im Fenster [t_eval_start, t_end] / Fensterlänge,
        F_max, F_min (Abtastpunkte im Fenster; F_min = 0, sobald eine Flugphase im Fenster liegt),
        n_imp = Kontaktbeginne im Fenster, starts = alle Kontaktbeginn-Zeiten."""
        M, K, C = self.M, self.K, self.C
        x = -M * G / K if x0 is None else x0
        v = v0
        mode = 'c' if (x < 0 and -K * x - C * v > 0) else 'f'
        flight = 0.0
        Fmax, Fmin = -np.inf, np.inf
        n_imp = 0
        starts = []
        stall = 0
        for a, b in self._segments(0.0, t_end):
            terms = self.terms(0.5 * (a + b))
            ta = a
            while ta < b - 1e-15:
                ng = max(int(np.ceil((b - ta) / h)), 1)
                tg = np.linspace(ta, b, ng + 1)[1:]
                if mode == 'c':
                    xx, vv, NN = self._contact_eval_terms(terms, ta, x, v, tg)
                    neg = np.where(NN <= 0.0)[0]
                    if neg.size == 0 or (stall >= 2 and neg[0] == 0 and neg.size == 1):
                        te, keep = b, np.ones(tg.size, bool)
                        newmode = 'c'
                    else:
                        i = neg[0]
                        tl = ta if i == 0 else tg[i - 1]
                        f_ = lambda s: self._contact_eval_terms(terms, ta, x, v, np.array([s]))[2][0]
                        flo = f_(tl)
                        te = brentq(f_, tl, tg[i], xtol=1e-14) if flo > 0 else tl
                        keep = tg < te
                        newmode = 'f'
                    win = keep & (tg >= t_eval_start)
                    if win.any():
                        Fmax = max(Fmax, NN[win].max())
                        Fmin = min(Fmin, NN[win].min())
                    if te == b:
                        x, v = xx[-1], vv[-1]
                    else:
                        X, V, _ = self._contact_eval_terms(terms, ta, x, v, np.array([te]))
                        x, v = X[0], V[0]
                else:
                    xx, vv = self._flight_terms(terms, ta, x, v, tg)
                    gg = np.minimum(-xx, -K * xx - C * vv)
                    pos = np.where(gg > 0.0)[0]
                    if pos.size == 0:
                        te = b
                        newmode = 'f'
                    else:
                        i = pos[0]
                        tl = ta if i == 0 else tg[i - 1]

                        def g_(s):
                            X, V = self._flight_terms(terms, ta, x, v, np.array([s]))
                            return min(-X[0], -K * X[0] - C * V[0])
                        glo = g_(tl)
                        te = brentq(g_, tl, tg[i], xtol=1e-14) if glo < 0 else tl
                        newmode = 'c'
                    lo = max(ta, t_eval_start)
                    if te > lo:
                        flight += te - lo
                        Fmin = min(Fmin, 0.0)
                    if te == b:
                        x, v = xx[-1], vv[-1]
                    else:
                        X, V = self._flight_terms(terms, ta, x, v, np.array([te]))
                        x, v = X[0], V[0]
                    if newmode == 'c':
                        starts.append(te)
                        if te >= t_eval_start:
                            n_imp += 1
                stall = stall + 1 if te - ta < 1e-12 else 0
                if stall > 50:
                    raise RuntimeError('Ereignissuche steckt fest bei t = %.9f' % ta)
                ta = te
                mode = newmode
        return dict(lam=100.0 * flight / (t_end - t_eval_start), F_max=Fmax, F_min=Fmin, n_imp=n_imp,
                    starts=np.array(starts), x_end=x, v_end=v, mode_end=mode)


# ───────────────────────────── Lauftypen ───────────────────────────────────
SECTION = np.arange(100.0, 140.0 + 1e-9, 2.0)
PILOTS = [(110.0, 250.0), (130.0, 230.0), (110.0, 252.0)]


def runs(pair_step=5.0):
    L = [('einzel', (0, 0, 0), (1, 0, 0))]
    for d in np.arange(0.0, 360.0, pair_step):
        L.append(('paar', (0, d, 0), (1, 1, 0)))
    L.append(('synchron', (0, 0, 0), (1, 1, 1)))
    L.append(('zweiergruppe', (0, 0, 180), (1, 1, 1)))
    for a, b in PILOTS:
        L.append(('pilot', (0, a, b), (1, 1, 1)))
    for a in SECTION:
        L.append(('schnitt', (0, a, 240.0), (1, 1, 1)))
    return L


# ───────────────── schneller FFT-Löser (eigene Implementierung, für Sweeps) ───────────────────
def fft_linear(phis_list, w_list, mu, hub, f, K, C, M=M_REF, n=32000, nsamp=2000):
    """Lineare periodische Lösung über die FFT des fein abgetasteten Profils (eigene Implementierung).
    phis_list (r,3) in Grad, w_list (r,3). Rückgabe N (r, nsamp). Phasenverschiebung exakt im
    Frequenzbereich (e^{−ikωτ}), daher keine Rasterbindung der Phasen."""
    T = 1.0 / f
    t = np.arange(n) * T / n
    A = np.fft.rfft(acc(t, hub, f)) / n          # c_k (einseitig, k ≥ 0)
    A[0] = 0.0
    k = np.arange(A.size)
    w = 2 * np.pi * f * k
    if K is None:
        H = np.ones_like(w, dtype=complex)
    else:
        H = (K + 1j * w * C) / (K - M * w ** 2 + 1j * w * C)
    phis = np.radians(np.asarray(phis_list, float))
    W = np.asarray(w_list, float)
    Phi = (W[:, :, None] * np.exp(-1j * phis[:, :, None] * k[None, None, :])).sum(1)
    Nk = (mu * M / 3.0) * H[None, :] * A[None, :] * Phi
    N = M * G + np.fft.irfft(Nk * n, n, axis=1)
    return N[:, ::n // nsamp]
