"""
vf_modell.py – P2 Gegenprüfung "kippmoment": UNABHÄNGIGE Implementierung (kein Import aus km_modell.py
und kein Import aus code/finesweep.py; Konstanten und Egg-Profil hier neu geschrieben).

Anderer Rechenweg als die Prüfgruppe:
  * Koordinaten = die drei Zelleinfederungen w_j (statt Hub z und Neigungen a, b).
    Senkrechte Lage eines Körperpunkts über lineare Formfunktionen des Zelldreiecks:
        w(x, y) = Σ_j N_j(x, y)·w_j,   N_j = 1/3 + 2/(3 R_c²)·(x·x_j + y·y_j)
    (gilt für ein gleichseitiges Dreieck mit Ecken auf dem Radius R_c um den Flächenschwerpunkt).
  * Massenmatrix in Zellkoordinaten:
        M_w = M_f·[1/9 + 4ρ_f²/(9R_c²)·cos(ψ_j − ψ_k)] + Σ_i m_i·N(X_i)·N(X_i)ᵀ
    (Rahmen: Masse M_f, Schwerpunkt im Ursprung, ∫x²dm = ∫y²dm = M_f ρ_f², ∫xy dm = 0).
  * Steifigkeit und Dämpfung je Zelle K/3, C/3 -> diagonal in w (Zellkraft wirkt direkt auf w_j).
  * Bewegungsgleichung: M_w ẅ = −g·G + F(w, ẇ) − Σ_i m_i h_i s̈_i(t)·N(X_i),  G_j = M_f/3 + Σ_i m_i N_j(X_i).
  * Fourier-Koeffizienten des Egg-Profils ANALYTISCH (geschlossene Integrale der Sinusbögen), nicht per FFT.
  * Quasistatisch ("starr") direkt im Zeitbereich: F_j = F0_j + Σ_i m_i h_i N_j(X_i)·s̈_i(t).

Phasenkonvention: Modul i mit Phase φ_i läuft verzögert, s̈_i(t) = h_i·a(t − τ_i), τ_i = φ_i/(2πf)
(wie Engine, pcmms_v3a_phasen_sweep.py Z. 21–23 des Docstrings); Fourier: c_k·e^{−ikφ_i}.
Einheiten SI, Winkel an Schnittstellen in Grad.
"""
import numpy as np

# ---- Referenzparameter (aus dem Auftrag / Engine-Quelltext abgelesen, hier neu gesetzt) ----
M_TOT = 0.650
GRAV = 9.81
F0_HZ = 10.0
TH = 0.65                       # Hold-Anteil
R_TOP = 0.005
R_BOT = R_TOP * (1 - TH) / TH   # 2.6923 mm (C1-stetig)
K_REF = 1.0e4
C_REF = 16.0
K_STEIF = 369518.0              # f_n = 120 Hz bei M = 0.65 kg (Präreg A5)
C_STEIF = 2 * 0.02 * np.sqrt(K_STEIF * M_TOT)
MG3 = M_TOT * GRAV / 3


def a_egg(t, f=F0_HZ):
    """Egg-Beschleunigung bei Hubfaktor 1; bei f != 10 Hz gleicher Hub (Zeit gestaucht, a ~ f²)."""
    T = 1.0 / f
    ph = np.mod(t, T) / T
    AH = R_TOP * (np.pi / (TH * T)) ** 2
    AF = R_BOT * (np.pi / ((1 - TH) * T)) ** 2
    return np.where(ph < TH, -AH * np.sin(np.pi * ph / TH), AF * np.sin(np.pi * (ph - TH) / (1 - TH)))


def _sinbogen(k, L, start):
    """∫_start^{start+L} sin(π(u−start)/L)·e^{−i2πku} du (u = Phase in Perioden), analytisch."""
    b = 2 * np.pi * k * L
    return np.exp(-2j * np.pi * k * start) * L * np.pi * (1 + np.exp(-1j * b)) / (np.pi ** 2 - b ** 2)


def c_egg(kmax, f=F0_HZ):
    """Zweiseitige komplexe Koeffizienten c_k, k = 0..kmax: a(t) = c_0 + Σ_{k≥1} 2 Re(c_k e^{ikωt})."""
    T = 1.0 / f
    AH = R_TOP * (np.pi / (TH * T)) ** 2
    AF = R_BOT * (np.pi / ((1 - TH) * T)) ** 2
    k = np.arange(kmax + 1, dtype=float)
    c = -AH * _sinbogen(k, TH, 0.0) + AF * _sinbogen(k, 1 - TH, TH)
    return c


class Geom:
    """Zellen bei 0°, 120°, 240° auf R_c. Module i (i = 0, 1, 2 mit Phasen φ_1..φ_3) bei Winkel
    psi0 + 120°·i auf R_m (Linksreihenfolge). Rahmen: Masse (1 − μ)M, Trägheitsradius rho_f (Default R_c/2)."""

    def __init__(self, mu, R_c=0.10, R_m=None, psi0=0.0, rho_f=None, m_rel=(1, 1, 1), cell_dr=None):
        self.R_c = R_c
        self.R_m = R_c if R_m is None else R_m
        self.rho_f = R_c / 2 if rho_f is None else rho_f
        self.psi_c = np.radians([0.0, 120.0, 240.0])
        self.xc = R_c * np.c_[np.cos(self.psi_c), np.sin(self.psi_c)]
        self.psi_m = np.radians(psi0 + 120.0 * np.arange(3))
        self.xm = self.R_m * np.c_[np.cos(self.psi_m), np.sin(self.psi_m)]
        self.m = mu * M_TOT / 3 * np.asarray(m_rel, float)
        self.Mf = (1 - mu) * M_TOT
        # Formfunktionen der Module: Nm[i, j] = N_j(X_i)
        self.Nm = 1 / 3 + 2 / (3 * R_c ** 2) * (self.xm @ self.xc.T)
        dpsi = self.psi_c[:, None] - self.psi_c[None, :]
        Mframe = self.Mf * (1 / 9 + 4 * self.rho_f ** 2 / (9 * R_c ** 2) * np.cos(dpsi))
        self.Mw = Mframe + np.einsum('i,ij,ik->jk', self.m, self.Nm, self.Nm)
        self.Gw = self.Mf / 3 + self.m @ self.Nm          # statische generalisierte Gewichte /g
        self.F0 = GRAV * self.Gw                          # statische Zellkräfte

    def eig(self, K, C=0.0):
        A = np.linalg.solve(self.Mw, (K / 3) * np.eye(3))
        w2 = np.sort(np.linalg.eigvals(A).real)
        return np.sqrt(w2) / (2 * np.pi)


def zell_koeff(geo, phi_deg, K=None, C=None, f=F0_HZ, hub=(1, 1, 1), kmax=400):
    """Komplexe Koeffizienten der dynamischen Zellkräfte F_jk (3 × kmax+1), zweiseitige Normierung.
    K=None -> quasistatisch (starr)."""
    c = c_egg(kmax, f)
    c[0] = 0.0
    k = np.arange(kmax + 1)
    phi = np.radians(np.asarray(phi_deg, float))
    E = np.exp(-1j * np.outer(phi, k))                    # (3 Module × k)
    mh = geo.m * np.asarray(hub, float)
    P = (geo.Nm.T * mh[None, :]) @ E * c[None, :]         # Σ_i m_i h_i N_j(X_i) c_k e^{-ikφ_i}  (3 Zellen × k)
    if K is None:
        return P
    Fk = np.zeros_like(P)
    w = 2 * np.pi * f * k
    I3 = np.eye(3)
    for kk in range(1, kmax + 1):
        D = -w[kk] ** 2 * geo.Mw + (1j * w[kk] * C / 3 + K / 3) * I3
        W = np.linalg.solve(D, -P[:, kk])
        Fk[:, kk] = -(K / 3 + 1j * w[kk] * C / 3) * W
    return Fk


def synth(Xk, n=4000):
    """Zeitreihe über eine Periode aus zweiseitigen Koeffizienten (k ≥ 1), n Stützstellen."""
    Xk = np.atleast_2d(Xk)
    kmax = Xk.shape[1] - 1
    t = np.arange(n) / n
    E = np.exp(2j * np.pi * np.outer(np.arange(1, kmax + 1), t))
    return 2 * np.real(Xk[:, 1:] @ E)


def starr_zeit(geo, phi_deg, f=F0_HZ, hub=(1, 1, 1), n=20000):
    """Quasistatische Zellkräfte direkt im Zeitbereich (ohne Fourier), n Stützstellen je Periode."""
    T = 1.0 / f
    t = np.arange(n) * T / n
    tau = np.radians(np.asarray(phi_deg, float)) / (2 * np.pi * f)
    s = np.stack([hub[i] * a_egg(t - tau[i], f) for i in range(3)])     # (3 Module × n)
    return geo.F0[:, None] + geo.Nm.T @ (geo.m[:, None] * s)


def momente(geo, F):
    """M_x = Σ F_j y_j, M_y = −Σ F_j x_j (F: 3 × n)."""
    return geo.xc[:, 1] @ F, -(geo.xc[:, 0] @ F)
