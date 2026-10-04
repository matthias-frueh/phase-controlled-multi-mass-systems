"""zm.py - eigenes, unabhaengig hergeleitetes Modell fuer die Gegenpruefung (P3, Rolle zusatz_p2).

Nicht aus den P2-Skripten abgeleitet. Herleitung (Lagrange) und Konventionen:
  q = (z, a, b): Hub des Rahmens im Ursprung und Neigungen, Lage eines Punkts w(x, y) = z + a*x + b*y.
  Rahmen: Masse M_f = (1 - mu)*M im Ursprung, Kippträgheit J_f = M_f*rho_f**2 um beide Achsen.
  Modul i: Masse m_i = mu*M/3 bei (X_i, Y_i), absolute Lage w(X_i, Y_i) + s_i(t), s_i = h_i*q_egg(t - tau_i).
  Zelle j bei (x_j, y_j): Druckkraft F_j = -(K/3)*w_j - (C/3)*dw_j/dt (zweiseitig im linearen Teil).
  Bewegungsgleichung:  Mq*qdd = -g*mvec + sum_j F_j*B_j - sum_i m_i*sdd_i*b_i,
     Mq = diag(M_f, J_f, J_f) + sum_i m_i b_i b_i^T,  b_i = (1, X_i, Y_i),  B_j = (1, x_j, y_j).
  Linear, Harmonische k:  F_k = T(k*omega) g_k,  g_{i,k} = m_i*h_i*c_k*exp(-i*k*phi_i)  (Modulzeiger),
     T = (K/3 + i k w C/3) * Bc^T * Z^{-1} * Bm,  Z = Kq - (k w)^2 Mq + i k w Cq,  Kq = (K/3) Bc Bc^T.
  Quasistatisch (starr):  T = Bc^{-1} Bm.
  Momente der Zellkraefte um den Ursprung: M_x = sum F_j*y_j, M_y = -sum F_j*x_j.
  Profil: Fourier-Koeffizienten c_k der Egg-Beschleunigung ANALYTISCH (stueckweise Sinus), Zeitachse
  a(t) = sum_k c_k exp(+i k w t)  (zweiseitig), Modul j verzoegert um tau_j = phi_j/(2 pi f).
"""
import numpy as np

# Parameter der Referenz (Quelle: code/pcmms_v3a_phasen_sweep.py, Block KONFIGURATION; hier neu eingetippt)
M = 0.650
G = 9.81
MG = M * G
F_HZ = 10.0
T_CYC = 1.0 / F_HZ
OMEGA = 2 * np.pi * F_HZ
RTOP = 0.005
THOLD = 0.65
TFAST = 1.0 - THOLD
RBOT = RTOP * TFAST / THOLD
A_HOLD = -RTOP * (np.pi / (THOLD * T_CYC)) ** 2
A_FAST = RBOT * (np.pi / (TFAST * T_CYC)) ** 2
K_REF, C_REF = 1.0e4, 16.0
# Steifer Fall (Praereg A5-Beispiel nach P2-Protokoll KM-05): f_n = 120 Hz, zeta = 0.02, M gesamt
K_ST = M * (2 * np.pi * 120.0) ** 2
C_ST = 2 * 0.02 * np.sqrt(K_ST * M)
R_C = 0.100


def accel(t):
    """Egg-Beschleunigung (eigene Implementierung der stueckweisen Definition)."""
    ph = np.mod(t, T_CYC) / T_CYC
    return np.where(ph < THOLD, A_HOLD * np.sin(np.pi * ph / THOLD),
                    A_FAST * np.sin(np.pi * (ph - THOLD) / TFAST))


def ck_analytic(kmax):
    """Zweiseitige Fourier-Koeffizienten c_k (k = 0..kmax) der Egg-Beschleunigung, analytisch:
    int_0^L sin(alpha*x) e^{-i beta x} dx = alpha (1 + e^{-i beta L})/(alpha^2 - beta^2), alpha*L = pi."""
    k = np.arange(kmax + 1)
    beta = 2 * np.pi * k
    ah, af = np.pi / THOLD, np.pi / TFAST
    ch = A_HOLD * ah * (1 + np.exp(-1j * beta * THOLD)) / (ah ** 2 - beta ** 2)
    cf = A_FAST * np.exp(-1j * beta * THOLD) * af * (1 + np.exp(-1j * beta * TFAST)) / (af ** 2 - beta ** 2)
    return ch + cf


class Geo:
    """Zellen auf R_c bei 0/120/240 Grad; Module auf R_m bei psi0 + 0/120/240 Grad (sinn=+1) bzw. -120/-240."""

    def __init__(self, Rm=R_C, psi0=0.0, mu=1.0, rho_f=R_C / 2, Rc=R_C, sinn=+1, cell_shift=None,
                 masses=None):
        self.Rc, self.mu = Rc, mu
        ang_c = np.radians([0.0, 120.0, 240.0])
        self.xc, self.yc = Rc * np.cos(ang_c), Rc * np.sin(ang_c)
        if cell_shift is not None:                 # (dx, dy) je Zelle, wahre Lage
            self.xc = self.xc + np.asarray(cell_shift)[:, 0]
            self.yc = self.yc + np.asarray(cell_shift)[:, 1]
        ang_m = np.radians(psi0 + sinn * np.array([0.0, 120.0, 240.0]))
        self.Xm, self.Ym = Rm * np.cos(ang_m), Rm * np.sin(ang_m)
        self.m = np.full(3, mu * M / 3) if masses is None else np.asarray(masses, float)
        self.Mf = M - self.m.sum() if masses is None else (1 - mu) * M
        self.Jf = self.Mf * rho_f ** 2
        self.Bc = np.vstack([np.ones(3), self.xc, self.yc])   # Spalten B_j
        self.Bm = np.vstack([np.ones(3), self.Xm, self.Ym])   # Spalten b_i
        self.Mq = np.diag([self.Mf, self.Jf, self.Jf]) + (self.Bm * self.m) @ self.Bm.T

    def Kq(self, K):
        return (K / 3) * self.Bc @ self.Bc.T

    def T(self, w, K=None, C=None):
        """Uebertragungsmatrix Modulzeiger -> Zellkraftzeiger bei Kreisfrequenz w (K=None: starr)."""
        if K is None:
            return np.linalg.solve(self.Bc, self.Bm).astype(complex)
        Z = self.Kq(K) - w ** 2 * self.Mq + 1j * w * self.Kq(C)
        return (K / 3 + 1j * w * C / 3) * self.Bc.T @ np.linalg.solve(Z, self.Bm)


def module_phasors(geo, phi_deg, kmax, hub=(1, 1, 1), extra_phase_deg=(0, 0, 0), f_hz=F_HZ):
    """g[i, k] = m_i h_i c_k e^{-i k phi_i}; Profil skaliert mit (f/10 Hz)^2 bei gleichem Hub."""
    c = ck_analytic(kmax) * (f_hz / F_HZ) ** 2
    k = np.arange(kmax + 1)
    ph = np.radians(np.asarray(phi_deg, float) + np.asarray(extra_phase_deg, float))
    return (geo.m * np.asarray(hub, float))[:, None] * c[None, :] * np.exp(-1j * np.outer(ph, k))


def cell_phasors(geo, g, K=None, C=None, f_hz=F_HZ, gains=(1, 1, 1)):
    kmax = g.shape[1] - 1
    F = np.zeros((3, kmax + 1), complex)
    for k in range(1, kmax + 1):
        F[:, k] = geo.T(2 * np.pi * f_hz * k, K, C) @ g[:, k]
    return np.asarray(gains, float)[:, None] * F


def synth(Fk, t, f_hz=F_HZ):
    """Zeitreihe aus zweiseitigen Koeffizienten (k >= 1), reell: 2 Re sum_k F_k e^{ikwt}."""
    k = np.arange(Fk.shape[-1])
    E = np.exp(1j * 2 * np.pi * f_hz * np.outer(k, t))
    return 2 * np.real(Fk[..., 1:] @ E[1:, :])


def static_cell_loads(geo):
    """Statische Zelllasten (starr) aus Kraft- und Momentengleichgewicht."""
    mvec = np.array([geo.Mf, 0.0, 0.0]) + geo.Bm @ geo.m
    return np.linalg.solve(geo.Bc, G * mvec)


def moments(geo_eval, F):
    """M_x, M_y aus Zellkraeften F[3, ...] mit den (ggf. nominalen) Zelllagen von geo_eval."""
    Mx = np.tensordot(geo_eval.yc, F, axes=(0, 0))
    My = -np.tensordot(geo_eval.xc, F, axes=(0, 0))
    return Mx, My


def rot_components(Mxk, Myk):
    """Fuer eine Harmonische: m(t) = Mx + i My = P+ e^{ikwt} + P- e^{-ikwt}. Mx(t) = 2Re(Mxk e^{ikwt})."""
    Pp = Mxk + 1j * Myk
    Pm = np.conj(Mxk) + 1j * np.conj(Myk)
    return Pp, Pm
