"""
auslegung.py – Auslegungswerkzeug für den Arbeitspunkt (Präregistrierung v2 §5.3 und §12, Werkzeug 2):
exakte stationäre Lösung des linearen Modells im Dauerkontakt für einen frei gewählten Modulsatz, mit
Summenkraft, Kräften der drei Wägezellen und den Prüfungen (a) und (b) aus §5.3.

Modell. Ein Körper mit Restmasse m₀ (Schwerpunkt (x₀, y₀), Trägheitsradius ρ₀ oder Flächenträgheit J₀) trägt
J Module mit Masse m_j, Hub h_j (Spitze-Spitze), Profilphase φ_j und Profil a_j(t) = h_j·f²·ã(f·t − φ_j/360°)
(Egg mit Halteanteil THOLD wie die Engine, oder Sinus); M = m₀ + Σ m_j, μ = Σ m_j/M. Ein geparktes Modul
(Laufgewicht w_j = 0) steht still, seine Masse bleibt an Bord. Solange keine Zelle abhebt, ist das Modell
linear; für die Harmonische k der Anregungsfrequenz f (ω = 2πf) gilt im eingeschwungenen Zustand
  Zellen, 3 FG (Hub z, Neigungen α, β; senkrechte Lage eines Körperpunkts w = z + α·x + β·y):
      M_q·q̈ + C_q·q̇ + K_q·q = −Σ_j w_j·m_j·a_j(t)·b_j,     M_q = M₀ + Σ_j m_j·b_j·b_jᵀ,  K_q = Σ_c K_c·B_c·B_cᵀ
      F_c,k = Σ_j T_cj(kω)·w_j·m_j·a_k⁽ʲ⁾·e^{−ikφ_j},      T(ω) = diag(K_c + iωC_c)·B·Z(ω)⁻¹·bᵀ
  mit Z(ω) = K_q − ω²·M_q + iω·C_q, den Zeilen B_c = (1, x_c, y_c) der Zellen, b_j = (1, X_j, Y_j) der Module,
  M₀ dem Anteil der Restmasse und K = Σ K_c, C = Σ C_c. Starre Auflage: T = B⁻ᵀ·bᵀ (Hebelgesetz).
  Summe N = Σ_c F_c (was die Zellen zusammen messen). Statische Zelllasten F₀ aus Bᵀ·F₀ = g·(M, Σ m·x, Σ m·y);
  Momente M_x = Σ F_c·y_c, M_y = −Σ F_c·x_c.
  Kontrolle 1 FG (Präreg A2.1, §8.7, linear_solver.py): N_k = H(kω)·Σ_j w_j·m_j·a_k⁽ʲ⁾·e^{−ikφ_j},
  H(ω) = (K + iωC)/(K − M·ω² + iωC). Bei symmetrischer Lage (gleiche Zellen, Σ m_j·b_j ∥ (1, 0, 0)) entkoppeln
  Hub und Kippen, dann ist N = N_1FG; sonst wird max_t |N − N_1FG| (abw_1FG) ausgewiesen und gewarnt, wenn er
  0,1·u_c übersteigt. Kontaktast: N > 0 und K-gewichtete Zelleinfederung Σ k_c·w_c < 0 (valid, im 1-FG-Fall wie
  linear_solver.py); je Zelle F_c > 0 (valid_zellen; im Maximum von w_c ist ẇ_c = 0, also F_c = −K_c·w_c, und
  F_c > 0 erzwingt w_c < 0).
Gemessene Einzelmodul-Harmonische (Präreg §8.2; Python: Aufbau(N_mess=…, N_mess_zellen=…)) ersetzen Profil und
Übertragung: N_k = Σ_j w_j·N_k⁽ʲ⁾·e^{−ikφ_j}. Alle Phasen sind Profilphasen φ_j^P = φ_j + Δδ_j (Präreg A1). Auf
den eigenen Indeximpuls bezogene Harmonische werden mit delta_delta = (Δδ₁, Δδ₂, Δδ₃) [°] intern mit e^{+ikΔδ_j}
auf den Profilbezug gedreht; ohne delta_delta müssen sie schon profilbezogen sein.
Konventionen wie Präreg A1: N_k = (2/N_θ)·Σ_n N(θ_n)·e^{−ikθ_n}, N_θ = 2000 Stützstellen je Periode, das
Spektrum wird achtfach feiner gebildet (wie linear_solver.py). Bandbegrenzt heißt k ≤ k_max (Vorgabe
max(k_b, 3), k_b = ⌊f₁/(2f)⌋), ungebändert das volle Spektrum; Bedingung (a) wird ungebändert geprüft.

Kennzahlen: f_n = √(K/M)/2π, ρ = f/f_n, ζ = C/(2√(K·M)); ε = −min_t Σ_j m_j·a_j(t)/(M·g) bei synchroner
Phasung (identische Egg-Module: ε = μ·π²·Hub·f²/(THOLD·g)); im Kontaktast ist N/(M·g) = 1 + ε·g̃(t; φ, ρ, ζ).
Abhebeschwelle eines Laufs: ε_c = ε·F₀/(F₀ − F_min) (Summe F₀ = M·g, Zelle: statische Zelllast). Moden aus
M_q⁻¹·K_q (Hub und zwei Kippmoden), f₁ = kleinste Mode.
Laufarten (Präreg §5.3, §5.4, §6): Einzelmodulläufe L₁–L₃, Paare (zwei Module, Abstand Δ), synchron (0°, 0°),
(0°, 180°), Piloten (110°, 250°), (130°, 230°), (110°, 252°), 21 Schnittpunkte φ₂ = 100° … 140° bei φ₃ = 240°.
Laufmengen wie die Nachrechnung 10/2026: PFLICHT = Schnitt, Piloten, Einzelmodulläufe; ZUSATZ = PFLICHT,
synchron und (0°, 180°); ALLE = ZUSATZ und Paare (keine Messkonfiguration, nur zur Information).
Prüfung §5.3: (a) kleinste Zellkraft ≥ 25 % der statischen Zelllast in PFLICHT (entscheidet; bestimmt f_zul,
A9.2 „ohne Zusatzkonfigurationen“), getrennt je Zusatzkonfiguration, ob sie (a) erfüllt und damit gemessen
wird; (b) 3f ≤ f₁/2; robust: f/f₁ ≤ 0,05 und ζ ≥ 0,02, sonst ρ-Bänder meiden, in denen hohe Profilharmonische
die Kontaktresonanz treffen (ε-Fenster der Menge ZUSATZ bei ζ = 0,02 schmaler als 0,15); Signal: ΔF_Zelt
(Spannweite von F_min auf dem Schnitt, kleinerer Wert von ungebändert und bandbegrenzt) ≥ 0,4693 N wie A4;
PB1: u_c ≤ 0,25·D/c, c = t(1 − 0,05/294; ν) (H1, A8: 3,583 für ν → ∞, 4,356 für ν = 19), D = ΔF_Zelt bzw.
max |N_k| auf dem Schnitt. Zeltsekanten sind 2°-Sekanten an 120° (bei verschobener Spitze auch negativ).

Aufruf:
  python3 auslegung.py --candidate                  V1-Kandidat: Kennzahlen, Laufarten, Prüfung §5.3
  python3 auslegung.py --point 120 240              Summe, Zellen, N_k und ∂ŷ/∂f an (φ₂, φ₃)
  python3 auslegung.py --runs                       alle Laufarten: Reserve der Summe und jeder Zelle
  python3 auslegung.py --window [--zetas 0.02 0.1]  ε- und Hubfenster je Laufmenge über den ζ-Bereich, K-Untergrenzen
  python3 auslegung.py --bands                      zu meidende ρ-Bänder bei ζ = 0,02 (ca. 30 s)
  python3 auslegung.py --reference --point 120 240  Simulationsreferenz (Abgleich mit linear_solver.py)
Optionen: --m (drei Modulmassen, kg), --hub (mm, Spitze-Spitze, ein Wert oder drei), --m0, --f, --K / --Kcells /
--rigid, --C / --zeta, --kmax, --sinus, --thold, --geometry G0|G60h|zentral, --Rc, --rho0, --df-req, --nu, --json.
Vorgabe ist der V1-Kandidat: 3 × 100 g, 8 mm, M = 0,65 kg, 10 Hz, K = 1,5·10⁶ N/m, ζ = 0,05, G0 mit
R_c = 100 mm, ρ₀ = R_c/2. Geometrien: Zellen auf R_c bei 0°, 120°, 240°; G0 Module über den Zellen (Präreg
A2.5), G60h Module um 60° gedreht auf R_c/2 (Kantenmitten), zentral alle Module im Zellschwerpunkt
(Zellkraft = Summe/3).

Rechenzeit: ein Punkt ca. 10 ms, alle 101 Laufarten ca. 0,3–0,6 s, Fenster über vier ζ ca. 2 s,
ρ-Bänder (157 Rasterpunkte) ca. 30 s.
Abgleich (tests/test_auslegung.py): Summe gleich linear_solver.solve() auf ≤ 1e-6 N (tatsächlich ≈ 1e-14 N),
auch bei μ = 0,4, 12 Hz, Sinus und starrer Auflage; V1-Kandidat, ε- und Hubfenster und K-Untergrenze wie
die Nachrechnung 10/2026 (exakte Zeitbereichslösung des 1-FG-Modells); Zellreserven, Zellminima und
Kippfrequenzen wie das unabhängig hergeleitete 3-FG-Modell derselben Nachrechnung (5 Stellen); unsymmetrische
Zellsteifigkeiten gegen eine Zeitbereichsintegration (scipy.signal.lsim) auf ≤ 2e-5 N.
Beispiel --candidate (G0): f_n = 241,8 Hz, f_Kipp = 282,8 Hz, ε = 0,5715; kleinste Reserve der Summe 42,6 %
(synchron), kleinste Zellreserve 41,1 % (Schnitt, φ₂ = 100°); ΔF_Zelt = 0,560 N; (a), (b), robust und Signal erfüllt.
Grenzen: Kelvin-Voigt-Kontakt je Zelle (Dämpfung wie die Steifigkeit verteilt, also ζ_Kipp = ζ·f_Kipp/f_Hub),
flacher starrer Körper ohne Horizontal-FG, ideal geführte Module; Abheben und Hüpfzustände rechnet nur die
Zeitintegration.

Matthias Früh · PCMMS · Oktober 2026
"""
import argparse
import json
import os
import sys

import numpy as np
import scipy.fft as sfft
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from finesweep import (M as M_REF, G, F_HZ, T_CYC, RTOP, THOLD, K as K_REF,  # noqa: E402
                       C_DAMP as C_REF, DT)

N_THETA = int(round(T_CYC / DT))        # 2000 Stützstellen je Periode (Engine, Präreg A1)
OVERSAMPLE = 8
N_FEIN = N_THETA * OVERSAMPLE           # Raster des Spektrums wie linear_solver.py
HUB_REF = RTOP / THOLD                  # Hub der Simulationsreferenz, 7,6923 mm Spitze-Spitze
R_ZELLE = 0.10                          # Zellradius der vorgefertigten Geometrien [m] (Annahme)
DF_REQ = 0.4693                         # ΔF_Zelt des A4-Beispiels [N], Signalfestlegung
RESERVE_MIN = 0.25                      # §5.3 (a)
SCHNITT = np.arange(100.0, 140.0 + 1e-9, 2.0)
I120 = int(np.flatnonzero(SCHNITT == 120.0)[0])
PILOTEN = ((110.0, 250.0), (130.0, 230.0), (110.0, 252.0))
MENGEN = dict(pflicht=('einzel', 'pilot', 'schnitt'),
              zusatz=('einzel', 'pilot', 'schnitt', 'synchron', 'zweiergruppe'),
              alle=('einzel', 'pilot', 'schnitt', 'synchron', 'zweiergruppe', 'paar'))
RANG = ('synchron', 'zweiergruppe', 'einzel', 'pilot', 'schnitt', 'paar')     # Meldung bei Gleichstand
GLEICH = 1e-9                           # Gleichstand von Reserven
KANDIDAT = dict(m=(0.1, 0.1, 0.1), hub=8e-3, m0=0.35, f=10.0, K=1.5e6, C=None, zeta=0.05)
REFERENZ = dict(m=(M_REF / 3,) * 3, hub=HUB_REF, m0=0.0, f=F_HZ, K=K_REF, C=C_REF, zeta=None)


def c_pb1(nu=np.inf):
    """Kritischer Wert der H1-Familie (147 Tests, zweiseitig, α = 0,05): t(1 − 0,05/294; ν), Präreg §8.4, A8."""
    return float(stats.t.ppf(1 - 0.05 / 294, nu))


C_PB1 = c_pb1()                         # 3,583 (ν → ∞)


def profil(n=N_FEIN, art='egg', thold=THOLD):
    """Normierte Profilbeschleunigung ã(s) auf n Stützstellen der Zyklusphase s ∈ [0, 1); a(t) = Hub·f²·ã(f·t)
    mit Hub = Spitze-Spitze (Egg: Halteanteil thold, wie z_egg_zdd der Engine; Sinus: Amplitude Hub/2)."""
    s = np.arange(n) / n
    if art == 'sinus':
        return -0.5 * (2 * np.pi) ** 2 * np.sin(2 * np.pi * s)
    if art != 'egg':
        raise ValueError(f'unbekanntes Profil {art!r}')
    tf = 1.0 - thold
    return np.where(s < thold, -np.pi ** 2 / thold * np.sin(np.pi * s / thold),
                    np.pi ** 2 / tf * np.sin(np.pi * (s - thold) / tf))


def geometrie(name='G0', R_c=R_ZELLE):
    """Zell- und Modullagen (je 3 × 2, m) der vorgefertigten Geometrien G0, G60h und zentral."""
    ang = np.radians([0.0, 120.0, 240.0])
    zellen = R_c * np.c_[np.cos(ang), np.sin(ang)]
    if name == 'G0':
        return zellen, zellen.copy()
    if name == 'G60h':
        return zellen, 0.5 * R_c * np.c_[np.cos(ang + np.pi / 3), np.sin(ang + np.pi / 3)]
    if name == 'zentral':
        return zellen, np.zeros((3, 2))
    raise ValueError(f'unbekannte Geometrie {name!r} (G0, G60h, zentral)')


def _synth(X, kmax=None):
    """Zeitverlauf auf N_θ Stützstellen aus zweiseitigen Koeffizienten X_k (x = Σ_k 2·Re X_k·e^{ikθ}, k ≥ 1)
    des feinen Spektrums; kmax: nur k ≤ kmax."""
    if kmax is not None and kmax < 1:
        raise ValueError(f'k_max ≥ 1 erwartet, nicht {kmax}')
    if kmax is None or kmax >= N_THETA // 2:
        Y = X if kmax is None else np.where(np.arange(X.shape[-1]) <= kmax, X, 0)
        return sfft.irfft(Y, N_FEIN, axis=-1, norm='forward')[..., ::OVERSAMPLE]
    Y = X[..., :N_THETA // 2 + 1].copy()
    Y[..., kmax + 1:] = 0
    return sfft.irfft(Y, N_THETA, axis=-1, norm='forward')


def _kenngroessen(x, mean):
    """F_min, F_max, F_min − ⟨N⟩, Schiefe m₃/m₂^{3/2} (wie scipy.stats.skew; nan bei konstanter Kurve) und A."""
    mn, mx = x.min(-1), x.max(-1)
    d = x - x.mean(-1, keepdims=True)
    m2, m3 = (d ** 2).mean(-1), (d ** 3).mean(-1)
    eben = m2 <= (1e-12 * mean) ** 2
    den = mean - mn
    return dict(F_min=mn, F_max=mx, F_min_rel=mn - mean,
                gamma1=np.where(eben, np.nan, m3 / np.where(eben, 1, m2) ** 1.5),
                A=np.where(np.abs(den) > 1e-12, (mx - mean) / np.where(np.abs(den) > 1e-12, den, 1.0), np.nan))


def _verketten(teile):
    if isinstance(teile[0], dict):
        return {k: _verketten([t[k] for t in teile]) for k in teile[0]}
    return np.concatenate(teile)


def _gewichte(v, name, streng=True):
    v = np.full(3, 1.0) if v is None else np.asarray(v, float)
    if v.shape != (3,) or (v < 0).any() or (streng and (v <= 0).any()) or v.sum() <= 0:
        raise ValueError(f'{name}: drei {"positive" if streng else "nichtnegative"} Zellanteile erwartet')
    return v / v.sum()


class Aufbau:
    """Modulsatz, Kontakt und Geometrie eines Arbeitspunkts (SI, Phasen in Grad). K = None: starre Auflage.
    C hat Vorrang vor zeta (C = 2ζ√(K·M)). k_rel, c_rel: Aufteilung von K und C auf die drei Zellen
    (Vorgabe je ein Drittel). N_mess (J × k) bzw. N_mess_zellen (J × 3 × k): gemessene komplexe Harmonische
    k = 1 … der Einzelmodulläufe in Präreg-Konvention; sie ersetzen die Modellantwort von Summe bzw. Zellen
    (ohne N_mess ist die Summe Σ_c N_mess_zellen). delta_delta: Δδ_j [°], wenn die Messwerte auf den eigenen
    Indeximpuls bezogen sind (Drehung mit e^{+ikΔδ_j} auf die Profilphase)."""

    def __init__(self, m=KANDIDAT['m'], hub=KANDIDAT['hub'], m0=KANDIDAT['m0'], f=KANDIDAT['f'],
                 K=KANDIDAT['K'], C=None, zeta=KANDIDAT['zeta'], profil_art='egg', thold=THOLD,
                 geometrie_name='G0', R_c=R_ZELLE, zellen=None, module=None, rho0=None, J0=None,
                 xy0=(0.0, 0.0), k_rel=None, c_rel=None, N_mess=None, N_mess_zellen=None, delta_delta=None):
        self._kw = {k: v for k, v in locals().items() if k != 'self'}
        self.m = np.atleast_1d(np.asarray(m, float))
        nmod = self.m.size
        hub = np.atleast_1d(np.asarray(hub, float))
        if self.m.ndim != 1 or (self.m <= 0).any() or hub.ndim != 1 or hub.size not in (1, nmod) or (hub <= 0).any():
            raise ValueError('Modulmassen m_j > 0 und Hub > 0 (ein Wert oder einer je Modul) erwartet')
        if module is None and nmod != 3:
            raise ValueError(f'vorgefertigte Geometrien haben drei Module, nicht {nmod}; sonst module = (J × 2) angeben')
        if not (m0 >= 0 and f > 0 and R_c > 0 and (K is None or K > 0) and (C is None or C >= 0)
                and (zeta is None or zeta >= 0)):
            raise ValueError('m₀ ≥ 0, f > 0, R_c > 0, K > 0 (oder None), C ≥ 0 und ζ ≥ 0 erwartet')
        if profil_art == 'egg' and not 0 < thold < 1:
            raise ValueError(f'Halteanteil 0 < THOLD < 1 erwartet, nicht {thold}')
        self.hub = np.broadcast_to(hub, (nmod,)).astype(float)
        self.m0, self.f, self.thold, self.profil_art = float(m0), float(f), float(thold), profil_art
        self.M = self.m0 + self.m.sum()
        self.MG = self.M * G
        self.mu = self.m.sum() / self.M
        self.starr = K is None
        zg, mg = geometrie(geometrie_name, R_c) if zellen is None or module is None else (None, None)
        self.zellen = np.asarray(zg if zellen is None else zellen, float).reshape(3, 2)
        self.module = np.asarray(mg if module is None else module, float).reshape(nmod, 2)
        self.k_rel = _gewichte(k_rel, 'k_rel')
        self.c_rel = self.k_rel if c_rel is None else _gewichte(c_rel, 'c_rel', streng=False)
        if self.starr:
            self.K, self.C, self.f_n, self.zeta = np.inf, 0.0, np.inf, np.nan
        else:
            self.K = float(K)
            self.C = float(C) if C is not None else (2 * zeta * np.sqrt(self.K * self.M) if zeta is not None else 0.0)
            self.f_n = np.sqrt(self.K / self.M) / (2 * np.pi)
            self.zeta = self.C / (2 * np.sqrt(self.K * self.M))
        self.rho = self.f / self.f_n
        # Massenmatrix des 3-FG-Modells und statische Zelllasten
        self.B = np.c_[np.ones(3), self.zellen]
        if abs(np.linalg.det(self.B)) <= 1e-9 * max(np.abs(self.zellen).max(), 1e-12) ** 2:
            raise ValueError('die drei Zellen liegen auf einer Geraden')
        self.b = np.c_[np.ones(nmod), self.module]
        b0 = np.r_[1.0, np.asarray(xy0, float)]
        rho0 = 0.5 * R_c if rho0 is None else rho0
        J0 = self.m0 * rho0 ** 2 * np.eye(2) if J0 is None else np.asarray(J0, float)
        self.Mq = self.m0 * np.outer(b0, b0) + np.einsum('j,ja,jb->ab', self.m, self.b, self.b)
        self.Mq[1:, 1:] += J0
        self.F0 = np.linalg.solve(self.B.T, G * (self.m0 * b0 + self.m @ self.b))
        if not self.starr and self.C == 0:              # ungedämpft: keine Harmonische darf eine Mode treffen
            fm = np.r_[self.f_n, self.moden()[0]]
            r = fm[np.isfinite(fm)] / self.f
            k = np.rint(r)
            treffer = (k >= 1) & (k <= N_FEIN // 2) & (np.abs(1 - (k / r) ** 2) < 1e-9)
            if treffer.any():
                i = int(np.flatnonzero(treffer)[0])
                raise ValueError(f'ungedämpfte Resonanz: k = {k[i]:.0f}, k·f = {k[i] * self.f:g} Hz trifft die Mode '
                                 f'{r[i] * self.f:.6g} Hz; ζ > 0 oder C > 0 angeben')
        # Profilspektren (zweiseitige Koeffizienten je Modul) und Übertragung
        a1 = np.fft.rfft(profil(N_FEIN, profil_art, thold)) / N_FEIN
        a1[0] = 0.0                     # Gleichanteil exakt null (∫a dt = 0), wie linear_solver.py
        self.a = (self.hub * self.f ** 2)[:, None] * a1[None, :]
        self.w = 2 * np.pi * self.f * np.arange(a1.size)
        H = np.ones(a1.size, complex) if self.starr else \
            (self.K + 1j * self.w * self.C) / (self.K - self.M * self.w ** 2 + 1j * self.w * self.C)
        ma = self.m[:, None] * self.a
        BX, T = self._uebertragung()
        self.Rc = np.einsum('kcj,jk->jck', T, ma)                                # Zellen je Modul (eigener Takt)
        self.Ry = None if BX is None else -np.einsum('c,kcj,jk->jk', self.k_rel, BX, ma)   # Σ k_c·w_c je Modul
        self.Rs1 = ma * H                                                        # Kontrolle 1 FG (Präreg A2.1)
        self.gemessen = N_mess is not None or N_mess_zellen is not None
        dd = np.zeros(nmod) if delta_delta is None else np.broadcast_to(np.asarray(delta_delta, float), (nmod,))
        dreh = lambda n: np.exp(1j * np.radians(dd)[:, None] * np.arange(1, n + 1))     # noqa: E731
        if N_mess_zellen is not None:
            Nc = np.asarray(N_mess_zellen, complex).reshape(nmod, 3, -1)
            self.Rc = np.zeros_like(self.Rc)
            self.Rc[:, :, 1:Nc.shape[2] + 1] = Nc / 2 * dreh(Nc.shape[2])[:, None, :]
        self.Rs = self.Rc.sum(1)                                                 # Summe = Σ Zellen
        if N_mess is not None:
            Nm = np.asarray(N_mess, complex).reshape(nmod, -1)
            self.Rs = np.zeros_like(self.Rs)
            self.Rs[:, 1:Nm.shape[1] + 1] = Nm / 2 * dreh(Nm.shape[1])
        if self.gemessen:
            self.Ry = self.Rs1 = None

    def _uebertragung(self):
        """B·Z(kω)⁻¹·bᵀ und T(kω) für alle k des feinen Spektrums, Form (k, Zelle, Modul); starr (None, B⁻ᵀ·bᵀ)."""
        nmod = self.m.size
        if self.starr:
            return None, np.broadcast_to(np.linalg.solve(self.B.T, self.b.T), (self.w.size, 3, nmod))
        Kc, Cc = self.K * self.k_rel, self.C * self.c_rel
        Kq, Cq = self.B.T @ (Kc[:, None] * self.B), self.B.T @ (Cc[:, None] * self.B)
        w = self.w[:, None, None]
        Z = Kq - w ** 2 * self.Mq + 1j * w * Cq
        BX = self.B @ np.linalg.solve(Z, np.broadcast_to(self.b.T.astype(complex), (self.w.size, 3, nmod)))
        return BX, (Kc + 1j * self.w[:, None] * Cc)[:, :, None] * BX

    def mit(self, **kw):
        """Kopie mit geänderten Parametern (zeta ersetzt C und umgekehrt)."""
        if 'zeta' in kw and 'C' not in kw:
            kw['C'] = None
        if 'C' in kw and 'zeta' not in kw:
            kw['zeta'] = None
        return Aufbau(**{**self._kw, **kw})

    def moden(self, K=None):
        """Eigenfrequenzen [Hz] im Dauerkontakt (aufsteigend) und Hubanteil |⟨w_c⟩|/rms(w_c) jeder Mode
        (1 = reiner Hub), bei der Gesamtsteifigkeit K (Vorgabe: die des Aufbaus; starr: K angeben)."""
        Kq = self.B.T @ ((self.K if K is None else K) * self.k_rel[:, None] * self.B)
        lam, V = np.linalg.eig(np.linalg.solve(Kq, self.Mq))
        lam, V = lam.real, V.real
        f = np.where(lam > 1e-14 * np.abs(lam).max(), 1 / (2 * np.pi * np.sqrt(np.abs(lam))), np.inf)
        u = self.B @ V
        hubanteil = np.abs(u.mean(0)) / np.sqrt((u ** 2).mean(0))
        i = np.argsort(f)
        return f[i], hubanteil[i]

    def kennzahlen(self):
        q = (self.m * self.hub).sum() * self.f ** 2 * profil(N_FEIN, self.profil_art, self.thold)  # Σ m_j a_j, synchron
        K_ref = 1.0 if self.starr else self.K
        fm, ha = self.moden(K_ref)
        f1_ref = min(np.sqrt(K_ref / self.M) / (2 * np.pi), fm.min())
        i_hub = int(np.argmax(ha))
        skal = np.inf if self.starr else 1.0
        f1 = skal * f1_ref
        return dict(M=self.M, m0=self.m0, mu=self.mu, f=self.f, K=self.K, C=self.C, zeta=self.zeta,
                    f_n=self.f_n, rho=self.rho, eps=-q.min() / self.MG, eps_spitze=np.abs(q).max() / self.MG,
                    f_hub=skal * fm[i_hub], f_kipp=skal * np.delete(fm, i_hub), f1=f1, rho1=self.f / f1,
                    r3=3 * self.f / f1, k_b=None if self.starr else int(np.floor(f1 / (2 * self.f))),
                    F0=self.F0, K_min_b=K_ref * (6 * self.f / f1_ref) ** 2,
                    K_min_robust=K_ref * (20 * self.f / f1_ref) ** 2)

    def kmax_standard(self, kmax=None):
        """k_max = Vorgabe, sonst max(k_b, 3) (Präreg §5.3 c); starr: ungebändert (None)."""
        if kmax is not None:
            return kmax
        kb = self.kennzahlen()['k_b']
        return None if kb is None else max(kb, 3)

    def loesen(self, phi, w=None, kmax=None, kout=None, block=25):
        """Stationäre Lösung für R Konfigurationen. phi: (R, J) Profilphasen aller Module in Grad oder (R, J − 1)
        ohne φ₁ = 0; w: Laufgewichte (1 läuft, 0 geparkt). Rückgabe: Dict mit N_k, Zell- und Moment-
        harmonischen (k ≤ kout, Vorgabe kmax bzw. 12) und je 'voll'/'band' (ungebändert/k ≤ kmax): Kurven N und
        Fz, F_min, F_max, F_min_rel = F_min − ⟨N⟩, gamma1, A, Fz_min, Fz_max, abw_1FG = max|N − N_1FG|;
        dazu Reserven, valid (Summe) und valid_zellen."""
        if kmax is not None and kmax < 1:
            raise ValueError(f'k_max ≥ 1 erwartet, nicht {kmax}')
        phi = np.atleast_2d(np.asarray(phi, float))
        nmod = self.m.size
        if phi.shape[1] == nmod - 1:
            phi = np.c_[np.zeros(len(phi)), phi]
        w = np.ones(phi.shape) if w is None else np.broadcast_to(np.asarray(w, float), phi.shape)
        kout = (kmax or 12) if kout is None else kout
        u, inv = np.unique(phi.ravel(), return_inverse=True)       # Phasenfaktoren nur je verschiedener Phase
        inv = inv.reshape(phi.shape)
        Eu = np.exp(-1j * np.radians(u)[:, None] * np.arange(self.a.shape[1]))
        teile = []
        for s in range(0, len(phi), block):
            sl = slice(s, s + block)
            S, Sc, Sy, S1 = 0, 0, 0, 0
            for j in range(nmod):
                e = w[sl, j, None] * Eu[inv[sl, j]]
                S, Sc = S + e * self.Rs[j], Sc + e[:, None, :] * self.Rc[j]
                if self.Ry is not None:
                    Sy = Sy + e * self.Ry[j]
                if self.Rs1 is not None:
                    S1 = S1 + e * self.Rs1[j]
            res = dict(Nk=2 * S[:, 1:kout + 1], Fzk=2 * Sc[:, :, 1:kout + 1])
            res['Mxk'] = np.einsum('rck,c->rk', res['Fzk'], self.zellen[:, 1])
            res['Myk'] = -np.einsum('rck,c->rk', res['Fzk'], self.zellen[:, 0])
            for name, km in (('voll', None), ('band', kmax)):
                if name == 'band' and kmax is None:
                    continue
                N = self.MG + _synth(S, km)
                Fz = self.F0[None, :, None] + _synth(Sc, km)
                abw = np.full(len(S), np.nan) if self.Rs1 is None else np.abs(_synth(S - S1, km)).max(-1)
                res[name] = dict(_kenngroessen(N, self.MG), N=N, Fz=Fz, Fz_min=Fz.min(-1), Fz_max=Fz.max(-1),
                                 abw_1FG=abw)
            res['z_max'] = np.full(len(S), -np.inf) if self.Ry is None else (-self.MG / self.K + _synth(Sy)).max(-1)
            teile.append(res)
        out = _verketten(teile)
        if kmax is None:
            out['band'] = out['voll']
        out.update(phi=phi, w=w, kmax=kmax, F0=self.F0)
        out['valid'] = (out['voll']['F_min'] > 0) & (out['z_max'] < 0)
        out['valid_zellen'] = (out['voll']['Fz_min'] > 0).all(1)
        out['reserve_summe'] = out['voll']['F_min'] / self.MG
        out['reserve_zellen'] = out['voll']['Fz_min'] / self.F0
        out['reserve_zelle'] = out['reserve_zellen'].min(1)
        return out


# ── Laufarten, Prüfung, Fenster ─────────────────────────────────────────────────────────────────────
def laufarten(paar_schritt=15.0):
    """Laufarten der Präreg für drei Module: (Name, Gruppe, Phasen (φ₁, φ₂, φ₃), Laufgewichte)."""
    L = [(f'L{j + 1}', 'einzel', (0.0, 0.0, 0.0), tuple(float(i == j) for i in range(3))) for j in range(3)]
    for a, b in ((0, 1), (0, 2), (1, 2)):
        for d in np.arange(0.0, 360.0, paar_schritt):
            ph, wt = [0.0] * 3, [0.0] * 3
            ph[b], wt[a], wt[b] = d, 1.0, 1.0
            L.append((f'Paar {a + 1}{b + 1} Δ={d:g}°', 'paar', tuple(ph), tuple(wt)))
    L.append(('synchron (0°,0°)', 'synchron', (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)))
    L.append(('(0°,180°)', 'zweiergruppe', (0.0, 0.0, 180.0), (1.0, 1.0, 1.0)))
    L += [(f'Pilot ({p2:g}°,{p3:g}°)', 'pilot', (0.0, p2, p3), (1.0, 1.0, 1.0)) for p2, p3 in PILOTEN]
    L += [(f'Schnitt ({p2:g}°,240°)', 'schnitt', (0.0, p2, 240.0), (1.0, 1.0, 1.0)) for p2 in SCHNITT]
    return L


def _kleinster(werte, idx, L):
    """Kleinster Wert unter den Läufen idx und sein Lauf; bei Gleichstand (< 1e-9) der erste nach RANG mit Zusatz."""
    v = werte[idx].min()
    gleich = idx[werte[idx] <= v + GLEICH]
    i = min(gleich, key=lambda n: (RANG.index(L[n][1]), n))
    return v, (L[i][0] if len(gleich) == 1 else f'{L[i][0]} u. a. ({len(gleich)} gleich)')


def bewerte(aufbau, kmax=None, paar_schritt=15.0, nu=np.inf):
    """Alle Laufarten: je Lauf Reserve der Summe (F_min/(M·g)) und jeder Zelle (F_c,min/F₀,c), ungebändert;
    je Gruppe und je Laufmenge (MENGEN) das Minimum mit bindendem Lauf; Schnittgrößen (ΔF_Zelt, 2°-Sekanten an
    120°, Spitze, D_k, PB1-Anforderung mit c = t(1 − 0,05/294; ν))."""
    L = laufarten(paar_schritt)
    r = aufbau.loesen([x[2] for x in L], [x[3] for x in L], kmax=kmax, kout=max(kmax or 0, 3))
    eps = aufbau.kennzahlen()['eps']
    grp = np.array([x[1] for x in L])
    with np.errstate(divide='ignore'):
        ec_s = np.where(r['reserve_summe'] < 1, eps / (1 - r['reserve_summe']), np.inf)
        ec_z = np.where(r['reserve_zelle'] < 1, eps / (1 - r['reserve_zelle']), np.inf)
    laeufe = [dict(name=x[0], gruppe=x[1], reserve_summe=r['reserve_summe'][i], reserve_zelle=r['reserve_zelle'][i],
                   reserve_zellen=r['reserve_zellen'][i], F_min=r['voll']['F_min'][i], F_max=r['voll']['F_max'][i],
                   Fz_max=r['voll']['Fz_max'][i].max(), eps_c_summe=ec_s[i], eps_c_zelle=ec_z[i],
                   valid=bool(r['valid'][i]), valid_zellen=bool(r['valid_zellen'][i])) for i, x in enumerate(L)]

    def zusammen(idx):
        rs, lauf_s = _kleinster(r['reserve_summe'], idx, L)
        rz, lauf_z = _kleinster(r['reserve_zelle'], idx, L)
        return dict(reserve_summe=rs, lauf_summe=lauf_s, reserve_zelle=rz, lauf_zelle=lauf_z,
                    F_max=r['voll']['F_max'][idx].max(), Fz_max=r['voll']['Fz_max'][idx].max(),
                    alle_valid=bool(r['valid'][idx].all()), abw_1FG=r['voll']['abw_1FG'][idx].max(),
                    abw_1FG_band=r['band']['abw_1FG'][idx].max())

    gruppen = {g: zusammen(np.flatnonzero(grp == g)) for g in dict.fromkeys(grp)}
    mengen = {n: zusammen(np.flatnonzero(np.isin(grp, gs))) for n, gs in MENGEN.items()}
    sch = grp == 'schnitt'
    schnitt = {}
    for name in ('voll', 'band'):
        fm = r[name]['F_min'][sch]
        schnitt[name] = dict(F_min=fm, dF=fm.max() - fm.min(), s_L=(fm[I120] - fm[I120 - 1]) / 2,
                             s_R=(fm[I120] - fm[I120 + 1]) / 2, spitze=SCHNITT[np.argmax(fm)],
                             gamma1=r[name]['gamma1'][sch])
    D = np.abs(r['Nk'][sch, :3]).max(0)
    dF, c = min(schnitt['voll']['dF'], schnitt['band']['dF']), c_pb1(nu)
    schnitt.update(dF=dF, D=D, nu=nu, c=c, uc_Fmin=0.25 * dF / c, uc_Nk=0.25 * D.min() / c)
    return dict(laeufe=laeufe, gruppen=gruppen, mengen=mengen, schnitt=schnitt, kmax=kmax, eps=eps, roh=r)


def _fenster_eins(aufbau, kmax, df_req, reserve_min, paar_schritt):
    """ε-Fenster eines Aufbaus bei festem K, C: ε_sig aus dem Signal, ε_max je Laufmenge aus der kleinsten
    Reserve (Zellen und Summe skalieren linear mit dem gemeinsamen Hubfaktor)."""
    b = bewerte(aufbau, kmax, paar_schritt)
    out = dict(eps_sig=b['eps'] * df_req / b['schnitt']['dF'], dF=b['schnitt']['dF'], eps_max={}, bindend={},
               reserve_zelle={})
    for name, m in b['mengen'].items():
        uz, us = 1 - m['reserve_zelle'], 1 - m['reserve_summe']
        out['eps_max'][name] = b['eps'] * (1 - reserve_min) / max(uz, us) if max(uz, us) > 0 else np.inf
        out['bindend'][name] = m['lauf_zelle'] if uz >= us else m['lauf_summe']
        out['reserve_zelle'][name] = m['reserve_zelle']
    return out


def fenster(aufbau, zetas=(0.02, 0.05, 0.1, 0.2), kmax=None, df_req=DF_REQ, reserve_min=RESERVE_MIN,
            paar_schritt=15.0):
    """Zulässiges ε- und Hubfenster je Laufmenge (eps_hi, hub_hi: Dicts pflicht/zusatz/alle; maßgeblich für
    f_zul ist pflicht) für die Massen, f, K und Geometrie des Aufbaus über den ζ-Bereich (starr: ein Fall)
    und die K-Untergrenzen für (b) 3f ≤ f₁/2 und robust f ≤ f₁/20."""
    kz = aufbau.kennzahlen()
    zeilen = []
    for z in ([None] if aufbau.starr else list(zetas)):
        a = aufbau if z is None else aufbau.mit(zeta=z)
        zeilen.append(dict(zeta=z, **_fenster_eins(a, a.kmax_standard(kmax), df_req, reserve_min, paar_schritt)))
    lo = max(z['eps_sig'] for z in zeilen)
    hi = {m: min(z['eps_max'][m] for z in zeilen) for m in MENGEN}
    skal = aufbau.hub / kz['eps']
    return dict(zeilen=zeilen, eps_lo=lo, eps_hi=hi, leer={m: lo > v for m, v in hi.items()}, hub_lo=skal * lo,
                hub_hi={m: skal * v for m, v in hi.items()}, K_min_b=kz['K_min_b'], K_min_robust=kz['K_min_robust'])


def rho_baender(aufbau, zeta=0.02, rho_min=0.01, rho_max=1 / 6, schritt=0.001, breite_min=0.15, kmax=None,
                df_req=DF_REQ, reserve_min=RESERVE_MIN, paar_schritt=30.0, menge='zusatz'):
    """ρ = f/f_n, in denen das ε-Fenster der Laufmenge bei ζ schmaler als breite_min ist (Resonanz hoher
    Profilharmonischer; K = M·(2πf/ρ)², übrige Parameter wie der Aufbau). Vorgabe ZUSATZ wie die Nachrechnung
    10/2026, damit (0°,0°) und (0°,180°) messbar bleiben. Rückgabe: Raster, Breiten, Bänder [(ρ_lo, ρ_hi)]."""
    rhos = np.arange(rho_min, rho_max + 1e-12, schritt)
    breite = []
    for rho in rhos:
        a = aufbau.mit(K=aufbau.M * (2 * np.pi * aufbau.f / rho) ** 2, zeta=zeta)
        e = _fenster_eins(a, a.kmax_standard(kmax), df_req, reserve_min, paar_schritt)
        breite.append(e['eps_max'][menge] - e['eps_sig'])
    breite = np.array(breite)
    schlecht = np.r_[False, breite < breite_min, False]
    kanten = np.flatnonzero(np.diff(schlecht.astype(int)))
    return dict(rho=rhos, breite=breite, baender=[(rhos[i], rhos[j - 1]) for i, j in zip(kanten[::2], kanten[1::2])])


def pruefung(aufbau, kmax=None, df_req=DF_REQ, reserve_min=RESERVE_MIN, zeta_min=0.02, breite_min=0.15,
             nu=np.inf, menge_band='zusatz', bew=None):
    """Prüfung des Arbeitspunkts nach §5.3: (a) über PFLICHT (entscheidet), je Zusatzkonfiguration „messbar“,
    Paare zur Information; (b); robuste Empfehlung, ρ-Band; Signal gegen PB1; Kontrolle des 1-FG-Modells."""
    kz = aufbau.kennzahlen()
    km = aufbau.kmax_standard(kmax)
    bew = bewerte(aufbau, km, nu=nu) if bew is None else bew
    p, s = bew['mengen']['pflicht'], bew['schnitt']
    zusatz = {x['name']: dict(ok=bool(x['reserve_zelle'] >= reserve_min and x['valid']), reserve_zelle=x['reserve_zelle'])
              for x in bew['laeufe'] if x['gruppe'] in ('synchron', 'zweiergruppe')}
    paare = bew['gruppen'].get('paar', {})
    band = dict(ok=True, entfaellt=aufbau.starr, breite=np.nan, zeta=np.nan, menge=menge_band)
    if not aufbau.starr:
        z = min(aufbau.zeta, zeta_min)
        a = aufbau.mit(zeta=z)
        e = _fenster_eins(a, a.kmax_standard(kmax), df_req, reserve_min, 30.0)
        br = e['eps_max'][menge_band] - e['eps_sig']
        band.update(ok=bool(br >= breite_min), breite=br, zeta=z)
    abw = bew['mengen']['alle']
    return dict(
        a=dict(ok=bool(p['reserve_zelle'] >= reserve_min and p['alle_valid']), menge='pflicht',
               reserve_zelle=p['reserve_zelle'], lauf=p['lauf_zelle'], reserve_summe=p['reserve_summe'],
               zusatz=zusatz, paare=dict(reserve_zelle=paare.get('reserve_zelle'), lauf=paare.get('lauf_zelle'))),
        b=dict(ok=bool(3 * kz['f'] <= kz['f1'] / 2), f1=kz['f1'], r3=kz['r3'], k_b=kz['k_b'], kmax=km),
        robust=dict(ok=bool(aufbau.starr or (kz['rho1'] <= 0.05 and aufbau.zeta >= 0.02)), rho1=kz['rho1'],
                    zeta=aufbau.zeta),
        band=band,
        signal=dict(ok=bool(s['dF'] >= df_req), dF=s['dF'], dF_voll=s['voll']['dF'], dF_band=s['band']['dF'],
                    df_req=df_req, s_L_band=s['band']['s_L'], s_R_band=s['band']['s_R'], s_L_voll=s['voll']['s_L'],
                    s_R_voll=s['voll']['s_R'], spitze_band=s['band']['spitze'], spitze_voll=s['voll']['spitze'],
                    nu=s['nu'], c=s['c'], uc_Fmin=s['uc_Fmin'], uc_Nk=s['uc_Nk']),
        modell=dict(abw_1FG=abw['abw_1FG'], abw_1FG_band=abw['abw_1FG_band'], grenze=0.1 * s['uc_Fmin'],
                    warnung=bool(abw['abw_1FG'] > 0.1 * s['uc_Fmin'])))


def ableitung_f(aufbau, phi, w=None, kmax=None, rel=1e-4):
    """∂ŷ/∂f bei gleichem Hub, K und C (zentraler Differenzenquotient) für F_min − ⟨N⟩, γ₁ (k ≤ kmax) und N_k."""
    if aufbau.gemessen:
        raise ValueError('∂ŷ/∂f braucht die Modellantwort, nicht gemessene Harmonische')
    df = aufbau.f * rel
    rp = aufbau.mit(f=aufbau.f + df, C=aufbau.C if not aufbau.starr else None).loesen(phi, w, kmax)
    rm = aufbau.mit(f=aufbau.f - df, C=aufbau.C if not aufbau.starr else None).loesen(phi, w, kmax)
    return dict(F_min_rel=(rp['band']['F_min_rel'] - rm['band']['F_min_rel']) / (2 * df),
                gamma1=(rp['band']['gamma1'] - rm['band']['gamma1']) / (2 * df), Nk=(rp['Nk'] - rm['Nk']) / (2 * df))


# ── Kommandozeile ────────────────────────────────────────────────────────────────────────────────────
def _pct(x):
    return f'{100 * x:6.1f} %'


def _band(kmax):
    return 'ungebändert' if kmax is None else f'k ≤ {kmax}'


def _nu(nu):
    return 'ν → ∞' if np.isinf(nu) else f'ν = {nu:g}'


def _json(o):
    if isinstance(o, dict):
        return {str(k): _json(v) for k, v in o.items() if k != 'roh'}
    if isinstance(o, (list, tuple)):
        return [_json(v) for v in o]
    if isinstance(o, np.ndarray):
        return _json(o.tolist())
    if isinstance(o, (complex, np.complexfloating)):
        return [_json(o.real), _json(o.imag)]
    if isinstance(o, (float, np.floating)):
        return float(o) if np.isfinite(o) else None
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def _drucke_kennzahlen(a, kz):
    K = 'starr' if a.starr else f'{a.K:.4g} N/m'
    print(f'Aufbau: m_j = {", ".join(f"{1e3 * v:.1f}" for v in a.m)} g, Hub = '
          f'{", ".join(f"{1e3 * v:.3f}" for v in a.hub)} mm (Spitze-Spitze), m₀ = {a.m0:.3f} kg, M = {a.M:.4f} kg, '
          f'μ = {a.mu:.4f}, f = {a.f:g} Hz, K = {K}, C = {a.C:.4g} N·s/m, Profil {a.profil_art}')
    print(f'f_n = {kz["f_n"]:.2f} Hz, ρ = {kz["rho"]:.4f}, ζ = {kz["zeta"]:.4f}; ε = {kz["eps"]:.4f} '
          f'(Lastspitze {kz["eps_spitze"]:.4f}); f_Hub = {kz["f_hub"]:.2f} Hz, f_Kipp = '
          f'{", ".join(f"{v:.2f}" for v in kz["f_kipp"])} Hz, f₁ = {kz["f1"]:.2f} Hz, 3f/f₁ = {kz["r3"]:.4f}, '
          f'k_b = {kz["k_b"]}; statische Zelllasten {", ".join(f"{v:.4f}" for v in a.F0)} N')


def _drucke_laeufe(bew, alle=False):
    if alle:
        print(f'{"Lauf":<24}{"Summe":>9}{"Zelle 1":>9}{"Zelle 2":>9}{"Zelle 3":>9}{"F_max":>8}{"Fz_max":>8}'
              f'{"ε_c Σ":>8}{"ε_c Z":>8}')
        for x in bew['laeufe']:
            print(f'{x["name"]:<24}{_pct(x["reserve_summe"]):>9}' + ''.join(f'{_pct(v):>9}' for v in x['reserve_zellen'])
                  + f'{x["F_max"]:>8.3f}{x["Fz_max"]:>8.3f}{x["eps_c_summe"]:>8.3f}{x["eps_c_zelle"]:>8.3f}')
    print(f'{"Gruppe/Menge":<14}{"Reserve Summe":>14}  {"(Lauf)":<38}{"Reserve Zelle":>14}  {"(Lauf)":<38}'
          f'{"F_max":>8}{"Fz_max":>8}')
    for g, x in list(bew['gruppen'].items()) + [(m.upper(), x) for m, x in bew['mengen'].items()]:
        print(f'{g:<14}{_pct(x["reserve_summe"]):>14}  {x["lauf_summe"]:<38}{_pct(x["reserve_zelle"]):>14}  '
              f'{x["lauf_zelle"]:<38}{x["F_max"]:>8.3f}{x["Fz_max"]:>8.3f}')
    s, km = bew['schnitt'], bew['kmax']
    print(f'Schnitt: ΔF_Zelt ungebändert {s["voll"]["dF"]:.4f} N'
          + ('' if km is None else f', {_band(km)}: {s["band"]["dF"]:.4f} N')
          + f'; 2°-Sekanten an 120° (ungebändert) {s["voll"]["s_L"]:.4f} / {s["voll"]["s_R"]:.4f} N/°; Spitze '
          f'{s["voll"]["spitze"]:g}° (ungebändert)' + ('' if km is None else f', {s["band"]["spitze"]:g}° ({_band(km)})')
          + '; D_k = '
          f'{", ".join(f"{v:.4f}" for v in s["D"])} N; PB1 u_c ≤ {s["uc_Fmin"]:.4f} N (F_min), {s["uc_Nk"]:.4f} N '
          f'(N_k) mit c = {s["c"]:.3f} ({_nu(s["nu"])})')


def _drucke_pruefung(p):
    ja = {True: 'erfüllt', False: 'VERLETZT'}
    a = p['a']
    print(f'(a) Zellreserve ≥ 25 % (Schnitt, Piloten, Einzel): {ja[a["ok"]]} (kleinste {_pct(a["reserve_zelle"]).strip()} '
          f'bei {a["lauf"]}; Summe {_pct(a["reserve_summe"]).strip()})')
    print('    Zusatzkonfigurationen: ' + '; '.join(f'{n} {"messbar" if v["ok"] else "NICHT messbar"} '
                                                  f'({_pct(v["reserve_zelle"]).strip()})' for n, v in a['zusatz'].items())
          + (f'; Paare (nur Information) kleinste {_pct(a["paare"]["reserve_zelle"]).strip()} bei {a["paare"]["lauf"]}'
             if a['paare']['lauf'] else ''))
    print(f'(b) 3f ≤ f₁/2: {ja[p["b"]["ok"]]} (f₁ = {p["b"]["f1"]:.2f} Hz, 3f/f₁ = {p["b"]["r3"]:.4f}, '
          f'k_b = {p["b"]["k_b"]}, k_max = {p["b"]["kmax"]})')
    bd = p['band']
    btxt = 'entfällt (starr)' if bd['entfaellt'] else \
        f'{ja[bd["ok"]]} (ε-Fenster {bd["menge"].upper()} bei ζ = {bd["zeta"]:.3f}: Breite {bd["breite"]:.3f})'
    print(f'robust f/f₁ ≤ 0,05 und ζ ≥ 0,02: {ja[p["robust"]["ok"]]} (f/f₁ = {p["robust"]["rho1"]:.4f}, '
          f'ζ = {p["robust"]["zeta"]:.4f}); ρ-Band: {btxt}')
    s = p['signal']
    kb = 'ungebändert' if p['b']['kmax'] is None else 'k ≤ k_max'
    print(f'Signal ΔF_Zelt ≥ {s["df_req"]:.4f} N: {ja[s["ok"]]} ({s["dF"]:.4f} N'
          + ('' if p['b']['kmax'] is None else f'; ungebändert {s["dF_voll"]:.4f}, {kb} {s["dF_band"]:.4f}')
          + f'); Sekanten an 120° ({kb}) {s["s_L_band"]:.4f} / {s["s_R_band"]:.4f} N/°, '
          f'Spitze {s["spitze_band"]:g}°; PB1 verlangt u_c ≤ {s["uc_Fmin"]:.4f} N (F_min) bzw. {s["uc_Nk"]:.4f} N '
          f'(N_k), c = {s["c"]:.3f} ({_nu(s["nu"])})')
    m = p['modell']
    if m['warnung']:
        print(f'WARNUNG: Die 1-FG-Summe (Präreg A2.1, §8.7) weicht um bis zu {m["abw_1FG"]:.4f} N (k ≤ k_max '
              f'{m["abw_1FG_band"]:.4f} N) von Σ F_c ab, mehr als 0,1·u_c = {m["grenze"]:.4f} N (Hub-Kipp-Kopplung).')


def _drucke_punkt(r, d, kmax):
    for name, lab in (('voll', 'ungebändert'), ('band', _band(kmax))):
        v = r[name]
        print(f'Summe {lab:>12}: F_min {v["F_min"][0]:.6f} N, F_max {v["F_max"][0]:.6f} N, F_min − ⟨N⟩ '
              f'{v["F_min_rel"][0]:+.6f} N, γ₁ {v["gamma1"][0]:+.5f}, A {v["A"][0]:.5f}; Zellen min '
              + ', '.join(f'{x:.4f}' for x in v['Fz_min'][0]) + ' N, max ' + ', '.join(f'{x:.4f}' for x in v['Fz_max'][0])
              + f' N; max|N − N_1FG| {v["abw_1FG"][0]:.2e} N')
    print(f'Kontaktast: Summe {bool(r["valid"][0])}, Zellen {bool(r["valid_zellen"][0])}; Reserve Summe '
          f'{_pct(r["reserve_summe"][0])}, Zellen ' + ', '.join(_pct(x) for x in r['reserve_zellen'][0]))
    print(f'{"k":>3}{"Re N_k":>11}{"Im N_k":>11}{"|N_k|":>10}{"∂Re/∂f":>11}{"∂Im/∂f":>11}{"|Zelle 1|":>11}'
          f'{"|M| links":>11}{"|M| rechts":>11}')
    for k in range(r['Nk'].shape[1]):
        n, mx, my = r['Nk'][0, k], r['Mxk'][0, k] / 2, r['Myk'][0, k] / 2
        dk = d['Nk'][0, k] if d else np.nan
        print(f'{k + 1:>3}{n.real:>11.6f}{n.imag:>11.6f}{abs(n):>10.6f}{np.real(dk):>11.6f}{np.imag(dk):>11.6f}'
              f'{abs(r["Fzk"][0, 0, k]):>11.6f}{abs(mx + 1j * my):>11.6f}{abs(np.conj(mx) + 1j * np.conj(my)):>11.6f}')
    if d:
        print(f'∂(F_min − ⟨N⟩)/∂f = {d["F_min_rel"][0]:+.6f} N/Hz, ∂γ₁/∂f = {d["gamma1"][0]:+.6f} 1/Hz '
              f'({_band(kmax)})')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--candidate', action='store_true', help='V1-Kandidat: Kennzahlen, Laufarten, Prüfung §5.3')
    ap.add_argument('--reference', action='store_true',
                    help='Simulationsreferenz: M = 0,65 kg, μ = 1, Hub 7,69 mm, K = 1e4 N/m, C = 16 N·s/m')
    ap.add_argument('--point', nargs=2, type=float, metavar=('PHI2', 'PHI3'))
    ap.add_argument('--runs', action='store_true', help='Tabelle aller Laufarten')
    ap.add_argument('--window', action='store_true', help='ε- und Hubfenster je Laufmenge, K-Untergrenzen')
    ap.add_argument('--bands', action='store_true', help='zu meidende ρ-Bänder bei ζ = 0,02')
    ap.add_argument('--m', nargs=3, type=float, help='drei Modulmassen [kg]')
    ap.add_argument('--hub', nargs='+', type=float, help='Hub [mm], Spitze-Spitze: ein Wert oder drei')
    ap.add_argument('--m0', type=float, help='Restmasse [kg]')
    ap.add_argument('--f', type=float, help='Anregungsfrequenz [Hz]')
    ap.add_argument('--K', type=float, help='Kontaktsteifigkeit gesamt [N/m]')
    ap.add_argument('--Kcells', nargs=3, type=float, help='Steifigkeit je Zelle [N/m] (ersetzt --K)')
    ap.add_argument('--rigid', action='store_true', help='starre Auflage')
    ap.add_argument('--C', type=float, help='Dämpfung gesamt [N·s/m]')
    ap.add_argument('--zeta', type=float, help='Dämpfungsgrad, C = 2ζ√(K·M)')
    ap.add_argument('--kmax', type=int, help='Bandbegrenzung (Vorgabe max(k_b, 3))')
    ap.add_argument('--sinus', action='store_true')
    ap.add_argument('--thold', type=float, default=THOLD)
    ap.add_argument('--geometry', default='G0', choices=('G0', 'G60h', 'zentral'))
    ap.add_argument('--Rc', type=float, default=R_ZELLE, help='Zellradius [m]')
    ap.add_argument('--rho0', type=float, help='Trägheitsradius der Restmasse [m] (Vorgabe R_c/2)')
    ap.add_argument('--zetas', nargs='+', type=float, default=[0.02, 0.05, 0.1, 0.2])
    ap.add_argument('--df-req', type=float, default=DF_REQ, help='Signalschwelle ΔF_Zelt [N]')
    ap.add_argument('--nu', type=float, default=np.inf, help='Freiheitsgrade ν für c der PB1-Anforderung (Vorgabe ∞)')
    ap.add_argument('--json', action='store_true', help='Ausgabe als JSON')
    a = ap.parse_args(argv)
    pruef = [(a.m is not None and min(a.m) <= 0, '--m: Massen > 0'),
             (a.hub is not None and (len(a.hub) not in (1, 3) or min(a.hub) <= 0), '--hub: ein oder drei Werte > 0'),
             (a.m0 is not None and a.m0 < 0, '--m0 ≥ 0'), (a.f is not None and a.f <= 0, '--f > 0'),
             (a.K is not None and a.K <= 0, '--K > 0'), (a.Kcells is not None and min(a.Kcells) <= 0, '--Kcells > 0'),
             (a.C is not None and a.C < 0, '--C ≥ 0'), (a.zeta is not None and a.zeta < 0, '--zeta ≥ 0'),
             (a.kmax is not None and a.kmax < 1, '--kmax ≥ 1'), (not 0 < a.thold < 1, '0 < --thold < 1'),
             (a.Rc <= 0, '--Rc > 0'), (a.rho0 is not None and a.rho0 < 0, '--rho0 ≥ 0'),
             (min(a.zetas) < 0, '--zetas ≥ 0'), (a.df_req <= 0, '--df-req > 0'), (a.nu <= 0, '--nu > 0')]
    for falsch, text in pruef:
        if falsch:
            ap.error(text)
    kw = dict(REFERENZ if a.reference else KANDIDAT)
    for key, val in (('m', a.m), ('m0', a.m0), ('f', a.f)):
        if val is not None:
            kw[key] = val
    if a.hub is not None:
        kw['hub'] = np.array(a.hub) * 1e-3
    if a.K is not None:
        kw['K'] = a.K
    k_rel = None
    if a.Kcells is not None:
        kw['K'], k_rel = sum(a.Kcells), a.Kcells
    if a.rigid:
        kw['K'] = None
    if a.zeta is not None:
        kw['zeta'], kw['C'] = a.zeta, None
    if a.C is not None:
        kw['C'], kw['zeta'] = a.C, None
    try:
        aufbau = Aufbau(**kw, profil_art='sinus' if a.sinus else 'egg', thold=a.thold, geometrie_name=a.geometry,
                        R_c=a.Rc, rho0=a.rho0, k_rel=k_rel)
    except ValueError as e:
        ap.error(str(e))
    kz = aufbau.kennzahlen()
    km = aufbau.kmax_standard(a.kmax)
    if not (a.candidate or a.point or a.runs or a.window or a.bands):
        ap.print_help()
        return
    out = dict(kennzahlen=kz)
    if a.candidate or a.runs:
        out['laufarten'] = bewerte(aufbau, km, nu=a.nu)
        out['pruefung'] = pruefung(aufbau, km, a.df_req, nu=a.nu, bew=out['laufarten'])
    if a.point:
        r = aufbau.loesen([a.point], kmax=km)
        d = None if aufbau.gemessen else ableitung_f(aufbau, [a.point], kmax=km)
        out['punkt'] = dict(phi=a.point, ergebnis={k: v for k, v in r.items() if k not in ('voll', 'band')},
                            voll={k: v for k, v in r['voll'].items() if k not in ('N', 'Fz')},
                            band={k: v for k, v in r['band'].items() if k not in ('N', 'Fz')}, ableitung_f=d)
    if a.window:
        out['fenster'] = fenster(aufbau, a.zetas, a.kmax, a.df_req)
    if a.bands:
        out['baender'] = rho_baender(aufbau, zeta=min(a.zetas), kmax=a.kmax, df_req=a.df_req)
    if a.json:
        print(json.dumps(_json(out), ensure_ascii=False, indent=1))
        return
    _drucke_kennzahlen(aufbau, kz)
    if 'laufarten' in out:
        _drucke_laeufe(out['laufarten'], alle=a.runs)
        _drucke_pruefung(out['pruefung'])
    if a.point:
        print(f'Punkt (φ₂, φ₃) = ({a.point[0]:g}°, {a.point[1]:g}°):')
        _drucke_punkt(r, d, km)
    if a.window:
        fe = out['fenster']
        for z in fe['zeilen']:
            zt = 'starr' if z['zeta'] is None else f'ζ = {z["zeta"]:g}'
            print(f'{zt:>10}: ε_sig = {z["eps_sig"]:.4f} (ΔF_Zelt {z["dF"]:.4f} N); ε_max '
                  + '; '.join(f'{m.upper()} {z["eps_max"][m]:.4f} ({z["bindend"][m]})' for m in MENGEN))
        for m in MENGEN:
            print(f'ε-Fenster {m.upper():<8} [{fe["eps_lo"]:.4f}; {fe["eps_hi"][m]:.4f}]{" (leer)" if fe["leer"][m] else ""}'
                  + ', Hub ' + ', '.join(f'[{1e3 * lo:.2f}; {1e3 * hi:.2f}] mm' for lo, hi in zip(fe['hub_lo'], fe['hub_hi'][m]))
                  + (' (maßgeblich für f_zul)' if m == 'pflicht' else ''))
        print(f'K ≥ {fe["K_min_b"]:.4g} N/m für (b), K ≥ {fe["K_min_robust"]:.4g} N/m für f ≤ f₁/20')
    if a.bands:
        bd = out['baender']
        print(f'ρ-Bänder mit ε-Fenster (ZUSATZ) < 0,15 bei ζ = {min(a.zetas):g}: '
              + (', '.join(f'{lo:.3f}–{hi:.3f}' for lo, hi in bd['baender']) or 'keine')
              + f'; aktueller Arbeitspunkt ρ = {kz["rho"]:.4f}')


if __name__ == '__main__':
    main()
