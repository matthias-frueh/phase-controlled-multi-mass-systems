"""
km_modell.py – P2, Prüfgruppe "kippmoment": starrer Körper auf drei Wägezellen im Dreieck.

Eigene Implementierung (nur Konstanten und Profilfunktion werden aus code/finesweep.py importiert,
damit Profil und Referenzparameter identisch zur Engine sind; der Repo-Code wird nicht verändert).

Modell (Herleitung im PROTOKOLL.md, Befund KM-02)
-------------------------------------------------
Koordinaten q = (z, a, b): senkrechte Verschiebung eines Körperpunkts (x, y) ist w(x, y) = z + a·x + b·y
(z: Hub im Ursprung = Flächenschwerpunkt des Zelldreiecks; a, b: Neigungen = kleine Kippwinkel um die
y- bzw. x-Achse, a = −β, b = α mit α um x, β um y). Zelle j bei (x_j, y_j): Einfederung −w_j,
Zellkraft F_j = max(0, −(K/3)·w_j − (C/3)·ẇ_j) für w_j < 0, sonst 0 (einseitig, wie die Engine je Zelle).
Rahmen (Restmasse M_f = (1 − μ)·M, Schwerpunkt im Ursprung, Flächenträgheit ∫x² dm = ∫y² dm = M_f·ρ_f²),
Module i mit Masse m_i bei (X_i, Y_i), senkrechte Lage w(X_i, Y_i) + s_i(t), s_i vorgegeben:
    s_i(t) = h_i · z_egg(t − τ_i),   τ_i = φ_i/(2π f)   (positive Phase verzögert, wie Engine).
Lagrange (kleine Winkel, nur senkrechte Bewegungen, flacher Körper):
    Mq·q̈ = −g·(M, Σ m_i X_i, Σ m_i Y_i) + Σ_j F_j·B_j − Σ_i m_i·s̈_i·b_i,
    Mq = diag(M_f, M_f ρ_f², M_f ρ_f²) + Σ_i m_i b_i b_iᵀ,  B_j = (1, x_j, y_j),  b_i = (1, X_i, Y_i).
Momente der Zellkräfte um den Ursprung (rechtshändig, z nach oben):
    M_x = Σ_j F_j·y_j,   M_y = −Σ_j F_j·x_j.
Bei drei Zellen auf einem Kreis (Radius R_c, 120°) und symmetrischen Modulen sind Hub- und Kippbewegung
entkoppelt: Hub wie Engine (M, K, C), Kippen mit J = M_f ρ_f² + Σ m_i X_i² und K_t = K·R_c²/2,
C_t = C·R_c²/2.  Engine-Grenzfall: Summe der Zellkräfte = N(t) der Engine.

Einheiten SI; Phasen an den Schnittstellen in Grad, intern rad.
"""
import numpy as np
from finesweep import (M, G, MG, F_HZ, T_CYC, RTOP, RBOT, THOLD, K as K_REF,   # noqa: F401
                       C_DAMP as C_REF, DT, z_egg_zdd)

N_PER = int(round(T_CYC / DT))      # 2000 Stichproben je Periode wie in der Engine
OMEGA = 2 * np.pi * F_HZ


# ───────────────────────────────── Profil ─────────────────────────────────
def profil_c(f_hz=F_HZ, os=8, profil='egg'):
    """Komplexe Fourier-Koeffizienten c_k (k = 0 … n/2) der Profilbeschleunigung bei Hub-Faktor 1,
    so dass a(t) = Σ_{k≥1} 2·Re(c_k·e^{ikωt}). Bei f_hz ≠ 10 Hz gleicher Hub: Skalierung (f/10)²."""
    n = N_PER * os
    t = np.arange(n) * (T_CYC / n)
    if profil == 'egg':
        a = z_egg_zdd(t)
    elif profil == 'sinus':
        a = -((RTOP + RBOT) / 2) * OMEGA**2 * np.sin(OMEGA * t)
    else:
        raise ValueError(profil)
    c = np.fft.rfft(a) / n
    c[0] = 0.0
    return c * (f_hz / F_HZ) ** 2


# ──────────────────────────────── Geometrie ────────────────────────────────
class Geo:
    """Zellen auf Radius R_c bei 0°, 120°, 240°; Module i = 0, 1, 2 (Phasen φ₁ = 0, φ₂, φ₃) auf Radius R_m
    bei dpsi + sinn·120°·i. mu: bewegter Massenanteil (m_i = μ·M/3·m_rel_i), Rahmen M_f = (1 − μ)·M mit
    ρ_f (Default R_c/2 = homogene Kreisscheibe mit Radius R_c). cell_xy/mod_xy überschreiben Positionen."""

    def __init__(self, R_c=0.10, R_m=None, dpsi_deg=0.0, sinn=+1, mu=1.0, rho_f=None,
                 m_rel=(1.0, 1.0, 1.0), cell_xy=None, mod_xy=None, M_tot=M):
        self.R_c = R_c
        self.R_m = R_c if R_m is None else R_m
        self.dpsi_deg, self.sinn, self.mu = dpsi_deg, sinn, mu
        self.rho_f = R_c / 2 if rho_f is None else rho_f
        ang_c = np.radians(np.array([0.0, 120.0, 240.0]))
        self.xc = np.c_[R_c * np.cos(ang_c), R_c * np.sin(ang_c)] if cell_xy is None else np.asarray(cell_xy, float)
        ang_m = np.radians(dpsi_deg + sinn * 120.0 * np.arange(3))
        self.xm = (np.c_[self.R_m * np.cos(ang_m), self.R_m * np.sin(ang_m)] if mod_xy is None
                   else np.asarray(mod_xy, float))
        self.m = mu * M_tot / 3 * np.asarray(m_rel, float)
        self.M_f = (1 - mu) * M_tot
        self.M = self.M_f + self.m.sum()
        self.B = np.c_[np.ones(3), self.xc]           # Zeilen B_j = (1, x_j, y_j)
        self.b = np.c_[np.ones(3), self.xm]           # Zeilen b_i = (1, X_i, Y_i)
        J_f = self.M_f * self.rho_f**2
        self.Mq = np.diag([self.M_f, J_f, J_f]) + np.einsum('i,ia,ib->ab', self.m, self.b, self.b)
        self.BBt = self.B.T @ self.B                  # Σ_j B_j B_jᵀ
        # statische Zellkräfte (Schwerpunkt des Rahmens im Ursprung)
        self.F0 = np.linalg.solve(self.B.T, G * np.array([self.M, self.m @ self.xm[:, 0], self.m @ self.xm[:, 1]]))

    def J(self):
        return self.Mq[1, 1], self.Mq[2, 2]

    def eigenfreq(self, K=K_REF, C=C_REF):
        """Ungedämpfte Eigenfrequenzen [Hz] (aufsteigend) und Eigenvektoren des Systems im Dauerkontakt."""
        Kq = K / 3 * self.BBt
        w2, V = np.linalg.eig(np.linalg.solve(self.Mq, Kq))
        idx = np.argsort(w2.real)
        return np.sqrt(w2.real[idx]) / (2 * np.pi), V[:, idx].real


# ──────────────────────────── lineare Lösung ────────────────────────────
def linear(geo, phi_deg, K=K_REF, C=C_REF, f_hz=F_HZ, hub=(1.0, 1.0, 1.0), profil='egg', os=8,
           starr=False, k_max=None):
    """Stationäre lineare Lösung (alle Zellen im Kontakt, bilateral). phi_deg: (φ₁, φ₂, φ₃) in Grad.
    Rückgabe: dict mit Fk (3 Zellen × nh, komplexe Koeffizienten wie profil_c), F (3 × N_PER Zeitreihe
    auf dem Engine-Raster), Summe, Mx, My, Koeffizienten Mxk, Myk, Nk."""
    c = profil_c(f_hz, os, profil)
    nh = c.size
    k = np.arange(nh)
    if k_max is not None:
        c = np.where(k <= k_max, c, 0)
    w = 2 * np.pi * f_hz * k
    phi = np.radians(np.asarray(phi_deg, float))
    mh = geo.m * np.asarray(hub, float)
    # Generalisierte Anregung Q_k = −Σ_i m_i h_i c_k e^{−ikφ_i} b_i   (3 × nh)
    E = np.exp(-1j * np.outer(phi, k))                # (3 Module × nh)
    S = (mh[:, None] * E * c[None, :])                # m_i h_i c_k e^{−ikφ_i}
    Qk = -(geo.b.T @ S)                               # (3 Koord × nh)
    Fk = np.zeros((3, nh), complex)
    if starr:
        Fk = np.linalg.solve(geo.B.T, -Qk)            # Σ_j F_j B_j = −Q
    else:
        Kq, Cq = K / 3 * geo.BBt, C / 3 * geo.BBt
        for kk in range(1, nh):
            if c[kk] == 0:
                continue
            D = -w[kk]**2 * geo.Mq + 1j * w[kk] * Cq + Kq
            qk = np.linalg.solve(D, Qk[:, kk])
            Fk[:, kk] = -(K / 3 + 1j * w[kk] * C / 3) * (geo.B @ qk)
    n = N_PER * os
    F = geo.F0[:, None] + np.fft.irfft(Fk * n, n, axis=1)[:, ::os]
    Mxk = Fk.T @ geo.xc[:, 1]
    Myk = -(Fk.T @ geo.xc[:, 0])
    return dict(c=c, Fk=Fk, F=F, N=F.sum(0), Nk=Fk.sum(0), Mxk=Mxk, Myk=Myk,
                Mx=geo.xc[:, 1] @ F, My=-(geo.xc[:, 0] @ F), F0=geo.F0)


def rot_zerlegung(Xk, Yk):
    """Zerlegung des Momentvektors je Harmonischer in links (+, gegen den Uhrzeigersinn von oben) und
    rechts (−) umlaufende Kreise: R+ = |X_k + iY_k|, R− = |X_k − iY_k| (Koeffizienten wie profil_c)."""
    Rp = np.abs(Xk + 1j * Yk)
    Rm = np.abs(Xk - 1j * Yk)
    return Rp, Rm


def harmonische(x, nh=13):
    """Koeffizienten c_k (k = 0 … nh−1) einer reellen Zeitreihe über ganze Perioden (Länge Vielfaches von
    N_PER), Normierung wie profil_c (Amplitude = 2|c_k|)."""
    x = np.asarray(x)
    n = x.shape[-1]
    per = n // N_PER
    X = np.fft.rfft(x, axis=-1) / n
    return X[..., ::per][..., :nh] if per > 1 else X[..., :nh]


# ──────────────────────────── nichtlineares RK4 ────────────────────────────
def rk4(geos, phis_deg, K=K_REF, C=C_REF, f_hz=F_HZ, hubs=None, T_sim=15.0, T_burn=5.0, dt=DT,
        bilateral=False, q0=None, v0=None, store=True):
    """RK4 für n Konfigurationen gleichzeitig (Listen geos, phis_deg). Standardstart: statisches
    Gleichgewicht, Ruhe (wie Engine). Zellkräfte werden wie in der Engine am Schrittanfang (k1) gespeichert.
    f_hz ≠ 10 Hz: Profil zeitlich gestaucht bei gleichem Hub. Rückgabe: dict mit F (n_rec × n × 3)."""
    n = len(geos)
    if hubs is None:
        hubs = [(1.0, 1.0, 1.0)] * n
    T = 1.0 / f_hz
    nper = int(round(T / dt))
    assert abs(nper * dt - T) < 1e-12, 'Periode muss Vielfaches von dt sein'
    sc = (f_hz / F_HZ)
    # Tabelle der generalisierten Modulanregung auf dem Halbschritt-Raster (2·nper je Periode)
    th = np.arange(2 * nper) * (dt / 2)
    Qtab = np.empty((2 * nper, n, 3))
    Minv = np.empty((n, 3, 3))
    Bm = np.empty((n, 3, 3))
    Qg = np.empty((n, 3))
    for c_, (geo, ph, hb) in enumerate(zip(geos, phis_deg, hubs)):
        tau = np.radians(np.asarray(ph, float)) / (2 * np.pi * f_hz)
        sdd = np.stack([hb[i] * sc**2 * z_egg_zdd((th - tau[i]) * sc) for i in range(3)], 1)   # (2nper × 3)
        Qtab[:, c_, :] = -(sdd * geo.m[None, :]) @ geo.b
        Minv[c_] = np.linalg.inv(geo.Mq)
        Bm[c_] = geo.B
        Qg[c_] = -G * np.array([geo.M, geo.m @ geo.xm[:, 0], geo.m @ geo.xm[:, 1]])
    if q0 is None:
        q = np.empty((n, 3))
        for c_, geo in enumerate(geos):
            w0 = -3 * geo.F0 / K
            q[c_] = np.linalg.solve(geo.B, w0)
    else:
        q = np.array(q0, float)
    v = np.zeros((n, 3)) if v0 is None else np.array(v0, float)
    k3, c3 = K / 3, C / 3
    BT = np.transpose(Bm, (0, 2, 1))

    def rhs(q, v, ih):
        w = np.einsum('njc,nc->nj', Bm, q)
        wd = np.einsum('njc,nc->nj', Bm, v)
        F = -k3 * w - c3 * wd
        if not bilateral:
            F = np.where((w < 0.0) & (F > 0.0), F, 0.0)
        gen = Qg + np.einsum('ncj,nj->nc', BT, F) + Qtab[ih % (2 * nper)]
        return v, np.einsum('nab,nb->na', Minv, gen), F

    n_steps = int(round(T_sim / dt))
    n_burn = int(round(T_burn / dt))
    rec = np.empty((n_steps - n_burn, n, 3)) if store else None
    for i in range(n_steps):
        ih = 2 * i
        k1q, k1v, F = rhs(q, v, ih)
        k2q, k2v, _ = rhs(q + 0.5 * dt * k1q, v + 0.5 * dt * k1v, ih + 1)
        k3q, k3v, _ = rhs(q + 0.5 * dt * k2q, v + 0.5 * dt * k2v, ih + 1)
        k4q, k4v, _ = rhs(q + dt * k3q, v + dt * k3v, ih + 2)
        q = q + dt * (k1q + 2 * k2q + 2 * k3q + k4q) / 6.0
        v = v + dt * (k1v + 2 * k2v + 2 * k3v + k4v) / 6.0
        if store and i >= n_burn:
            rec[i - n_burn] = F
    return dict(F=rec, q=q, v=v)


def momente(geo, F):
    """M_x, M_y aus Zellkräften F (… × 3)."""
    return F @ geo.xc[:, 1], -(F @ geo.xc[:, 0])
