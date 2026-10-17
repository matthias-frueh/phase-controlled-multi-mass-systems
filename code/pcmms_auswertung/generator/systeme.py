"""Bezugssysteme des Pipelinetests (Plan AP-13, Abschnitt 3.3) und ihre Modulantworten über `auslegung.Aufbau`.

Ein System ist ein Satz von Parametern für das 3-FG-Modell des Auslegungswerkzeugs (Werkzeug 2) mit möglichen
Modulunterschieden (Masse, Hub, Profilversatz δⱼ gegen den eigenen Indeximpuls, Profilform je Harmonischer) und einer
linearen, zeitinvarianten Kraftkette je Zelle. Die Antwort eines Moduls j auf seinen eigenen Takt (Profilphase 0) ist
N_c,k⁽ʲ⁾ = G_F,c(kω)·[T(kω)·m_j·a_k⁽ʲ⁾]_c; Summe = Σ_c. Bezug ist der eigene Indeximpuls: δⱼ dreht mit e^{−ikδⱼ}, also
Δδⱼ = δⱼ − δ₁ (Präreg A1). Die Bezugssysteme sind Rechenannahmen, keine Hardwarewahl (Plan 3.3, 5.4).
"""
import os
import sys
from dataclasses import dataclass, field, replace

import numpy as np

_CODE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)
import auslegung  # noqa: E402

HUB_REF = auslegung.HUB_REF
M_REF = auslegung.M_REF
G = auslegung.G


@dataclass(frozen=True)
class Kette:
    """Lineare, zeitinvariante Kraftkette je Zelle relativ zur statischen Kalibrierung: Tiefpass erster Ordnung
    (Grenzfrequenz f_tp) und Laufzeit τ, G(ω) = e^{−iωτ}/(1 + iω/ω_tp); identisch in allen Laufarten."""
    f_tp: tuple = (np.inf, np.inf, np.inf)
    tau: tuple = (0.0, 0.0, 0.0)

    def G(self, f_hz):
        f = np.atleast_1d(np.asarray(f_hz, float))
        w = 2 * np.pi * f
        out = np.empty((3, f.size), complex)
        for c in range(3):
            tp = 1.0 if np.isinf(self.f_tp[c]) else 1.0 / (1 + 1j * f / self.f_tp[c])
            out[c] = tp * np.exp(-1j * w * self.tau[c])
        return out


@dataclass(frozen=True)
class System:
    name: str
    m: tuple = (0.1, 0.1, 0.1)
    hub: tuple = (8e-3, 8e-3, 8e-3)
    m0: float = 0.35
    f: float = 10.0
    K: object = 1.5e6                       # None: starre Auflage
    zeta: object = 0.05
    C: object = None
    geometrie: str = 'G0'
    R_c: float = 0.1
    rho0: object = None
    xy0: tuple = (0.0, 0.0)
    k_rel: object = None
    profil: str = 'egg'
    k_max: int = 12
    m_luft: float = 0.0
    delta_profil_grad: tuple = (0.0, 0.0, 0.0)   # δⱼ: Profilverzögerung gegen den eigenen Indeximpuls
    profilform: tuple = ()                      # ((j, k, Faktor), …): Profilharmonische a_k⁽ʲ⁾·Faktor
    kette: Kette = field(default_factory=Kette)

    def mit(self, **kw):
        return replace(self, **kw)

    def aufbau(self, f=None, hub_faktor=1.0):
        return auslegung.Aufbau(m=self.m, hub=np.asarray(self.hub, float) * hub_faktor, m0=self.m0,
                                f=self.f if f is None else f, K=self.K, C=self.C, zeta=self.zeta,
                                profil_art=self.profil, geometrie_name=self.geometrie, R_c=self.R_c, rho0=self.rho0,
                                xy0=self.xy0, k_rel=self.k_rel, m_luft=self.m_luft)


def _a4():
    mu, M = 0.4, M_REF
    return System('A4', m=(mu * M / 3,) * 3, hub=(HUB_REF,) * 3, m0=(1 - mu) * M, f=10.0, K=None, zeta=None, C=None,
                  geometrie='G0', k_max=9)


BEZUGSSYSTEME = {
    'A4': _a4(),                                                      # Präreg A4: starr, μ = 0,4, 10 Hz, k_max = 9
    'V1-G0': System('V1-G0', k_max=12),                               # Kandidat, Kopf von auslegung.py
    'V1-G60h': System('V1-G60h', geometrie='G60h', k_max=12),
    'Referenz': System('Referenz', m=(M_REF / 3,) * 3, hub=(HUB_REF,) * 3, m0=0.0, f=10.0, K=1e4, zeta=None, C=16.0,
                       geometrie='G0', k_max=3),                      # Simulationsreferenz (Resonanzfall)
}


def system(name, **abweichungen):
    s = BEZUGSSYSTEME[name]
    return s.mit(**abweichungen) if abweichungen else s


@dataclass
class Antworten:
    """Modulantworten eines Systems bei einer Einstellung (Frequenz f, Hubfaktor)."""
    system: System
    f: float
    hub_faktor: float
    k_voll: int
    Nz: np.ndarray            # (Modul, Zelle, k) mit Kraftkette, Bezug eigener Index
    Nz_kraft: np.ndarray      # (Modul, Zelle, k) ohne Kraftkette (physikalische Zellkraft)
    A: np.ndarray             # (Modul, k) Profilbeschleunigung a_k⁽ʲ⁾, Bezug eigener Index
    X: np.ndarray             # (Modul, k) Profilweg x_k⁽ʲ⁾ = a_k/(−(kω)²)
    F0: np.ndarray            # statische Zelllasten (nur Gewicht) [N]
    MG: float
    M: float
    M_traege: float
    f_n: float
    zeta: float
    moden: np.ndarray
    G_F: np.ndarray           # (Zelle, k) Kraftkette bei kω
    H1fg: np.ndarray          # (k,) 1-FG-Übertragung H(kω) mit M + m_L
    kennzahlen: dict

    @property
    def Ns(self):
        return self.Nz.sum(1)

    @property
    def Ns_kraft(self):
        return self.Nz_kraft.sum(1)


def antworten(s, f=None, hub_faktor=1.0, k_voll=60):
    """Antworten der drei Module von System s bei Frequenz f (Vorgabe s.f) und Hubfaktor (Einstellung 2)."""
    f = s.f if f is None else f
    a = s.aufbau(f, hub_faktor)
    k = np.arange(1, k_voll + 1)
    Nz = 2 * a.Rc[:, :, 1:k_voll + 1].copy()
    A = 2 * a.a[:, 1:k_voll + 1].copy()
    for j, kk, fak in s.profilform:
        Nz[j - 1, :, kk - 1] *= fak
        A[j - 1, kk - 1] *= fak
    dreh = np.exp(-1j * np.outer(np.radians(s.delta_profil_grad), k))
    Nz *= dreh[:, None, :]
    A = A * dreh
    w = 2 * np.pi * f * k
    X = A / (-(w ** 2))
    GF = s.kette.G(f * k)
    kz = a.kennzahlen()
    H = np.ones(k_voll, complex) if a.starr else (a.K + 1j * w * a.C) / (a.K - a.M_traege * w ** 2 + 1j * w * a.C)
    return Antworten(system=s, f=f, hub_faktor=hub_faktor, k_voll=k_voll, Nz=Nz * GF[None], Nz_kraft=Nz, A=A, X=X,
                     F0=a.F0.copy(), MG=a.MG, M=a.M, M_traege=a.M_traege, f_n=a.f_n, zeta=a.zeta,
                     moden=a.moden(1.0 if a.starr else None)[0], G_F=GF, H1fg=H, kennzahlen=kz)


def frf(s, f_hz, ort_xy, mit_kette=True):
    """Übertragungsfunktion äußere Kraft (senkrecht, am Ort ort_xy, Module geparkt) → Zellkräfte (Zelle, f) aus dem
    3-FG-Modell des Aufbaus (dieselben Matrizen wie Aufbau._uebertragung, bei beliebigen Frequenzen)."""
    a = s.aufbau()
    w = 2 * np.pi * np.atleast_1d(np.asarray(f_hz, float))
    b = np.r_[1.0, np.asarray(ort_xy, float)]
    if a.starr:
        T = np.linalg.solve(a.B.T, b)[:, None] * np.ones(w.size)
    else:
        Kc, Cc = a.K * a.k_rel, a.C * a.c_rel
        Kq, Cq = a.B.T @ (Kc[:, None] * a.B), a.B.T @ (Cc[:, None] * a.B)
        Z = Kq[None] - w[:, None, None] ** 2 * a.Mq[None] + 1j * w[:, None, None] * Cq[None]
        X = np.linalg.solve(Z, np.broadcast_to(b.astype(complex), (w.size, 3))[..., None])[..., 0]   # (f, 3)
        T = ((Kc[None, :] + 1j * w[:, None] * Cc[None, :]) * (X @ a.B.T)).T                           # (Zelle, f)
    return T * (s.kette.G(w / (2 * np.pi)) if mit_kette else 1.0)
