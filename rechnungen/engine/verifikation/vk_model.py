"""Gegenprüfung P2/engine – eigenes Modellmodul (unabhängig von eng.py/el_solver.py geschrieben).

Parameter aus code/pcmms_v3a_phasen_sweep.py (Block KONFIGURATION) abgeschrieben, nicht importiert:
  M = 0,650 kg, g = 9,81, f = 10 Hz, THOLD = 0,65, RTOP = 5 mm, RBOT = RTOP*TFAST/THOLD, K = 1e4, C = 16.
Profil: Beschleunigung a(u) mit u = Zyklusphase in s ∈ [0, T):
  Halteast  u <  THOLD*T:  a = -RTOP*wH^2 * sin(wH*u),           wH = pi/(THOLD*T)
  schneller u >= THOLD*T:  a = +RBOT*wF^2 * sin(wF*(u-THOLD*T)), wF = pi/(TFAST*T)
Zweimal integriert (periodisch, also Integrationskonstanten 0 – siehe Herleitung im PROTOKOLL):
  e'(u) = RTOP*wH*cos(wH*u) bzw. -RBOT*wF*cos(wF*(u-THOLD*T));  e(u) = RTOP*sin(wH*u) bzw. -RBOT*sin(...)
Modul k: e(t - tau_k), tau_k = phi_k[rad]/(2*pi*f) = phi_k[deg]/360 * T  (Grad -> Zeit direkt, ohne Radiant).
Schwerpunkt Z = z + ebar(t), ebar = (1/3) sum_k e(t - tau_k); Bewegungsgleichung M*Z'' = -M g + N.
"""
import numpy as np

M = 0.650
G = 9.81
MG = M * G
F_HZ = 10.0
T = 1.0 / F_HZ
THOLD = 0.65
TFAST = 1.0 - THOLD
RTOP = 0.005
RBOT = RTOP * TFAST / THOLD
K = 1.0e4
C = 16.0
WH = np.pi / (THOLD * T)
WF = np.pi / (TFAST * T)
AH = -RTOP * WH**2
AF = RBOT * WF**2
ALPHA = C / (2 * M)
W0 = np.sqrt(K / M)
WD = np.sqrt(W0**2 - ALPHA**2)


def tau_of(phi_deg):
    """Grad -> Zeitversatz. Bewusst anderer Rechenweg als die Engine (dort radians/(2*pi*f))."""
    return np.asarray(phi_deg, float) / 360.0 * T


def _u(t):
    return np.mod(t, T)


def e_pos(t):
    u = _u(t)
    return np.where(u < THOLD * T, RTOP * np.sin(WH * u), -RBOT * np.sin(WF * (u - THOLD * T)))


def e_vel(t):
    u = _u(t)
    return np.where(u < THOLD * T, RTOP * WH * np.cos(WH * u), -RBOT * WF * np.cos(WF * (u - THOLD * T)))


def e_acc(t):
    u = _u(t)
    return np.where(u < THOLD * T, AH * np.sin(WH * u), AF * np.sin(WF * (u - THOLD * T)))


def ebar(t, taus):
    return sum(e_pos(t - tk) for tk in taus) / 3.0


def ebar_v(t, taus):
    return sum(e_vel(t - tk) for tk in taus) / 3.0


def contact_force(z, zd):
    F = -K * z - C * zd
    return np.where((z < 0.0) & (F > 0.0), F, 0.0)
