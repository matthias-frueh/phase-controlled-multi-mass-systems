"""
ereignisloeser.py – ereignisgenauer Löser für das Einmassenmodell der Referenz-Engine mit einseitigem Kontakt:
Kontakt- und Flugphasen mit exakt lokalisierten Übergängen, Periodizität und Floquet-Multiplikatoren,
Einzugsprüfung des Kontaktasts gegen Würfe.

Die Festschritt-RK4 der Engine (Δt = 50 µs) ist im Kontaktast genau, erzeugt im Liftoff-Bereich aber
Artefakte: scheinbare Perioden und Einschwingzeiten, einen Quadraturrest im Zeitmittel und an steifem Kontakt
falsche Endzustände. Dieser Löser integriert ohne festen Zeitschritt.

Modell (Engine, verallgemeinert): Rahmen- bzw. Auflagerkoordinate x (x < 0: Kontakt eingefedert), Restmasse m₀,
Module j mit Masse m_j, Hub h_j (Spitze-Spitze) und Phase φ_j. Modul j bewegt sich relativ zum Rahmen auf
e_j(t) = h_j·p(t − τ_j), τ_j = φ_j/(360°·f), p = Egg- oder Sinusprofil. Impulssatz mit M = m₀ + Σ m_j:

    M·ẍ = −M·g + N(x, ẋ) − Q(t),    Q(t) = Σ_j m_j·ë_j(t),    v_S = ẋ + Σ_j m_j·ė_j(t)/M,    M·v̇_S = N − M·g

Engine: m₀ = 0, m_j = M/3, h_j = RTOP/THOLD = 7,692 mm (Egg); dann ist Q/M = ā(t) wie in finesweep.rhs.
Egg-Profil (u = Zeit seit Beginn der Haltephase): Halteast u < THOLD·T: ë = −THOLD·h·Ω_H²·sin(Ω_H·u),
Ω_H = π/(THOLD·T); schneller Ast: ë = TFAST·h·Ω_F²·sin(Ω_F·(u − THOLD·T)), Ω_F = π/(TFAST·T). Sinus:
ë = −(h/2)·ω²·sin(ω·(t − τ)). Zwischen den Knickstellen (Beginn von Halte- und schneller Phase je Modul) ist
Q eine Summe von Sinustermen.

Kontaktgesetze; Kontakt genau dann, wenn die Schaltfunktion s(x, ẋ) = min(−x, ψ) > 0 ist:
  kv  Kelvin-Voigt wie die Engine: N = −K·x − C·ẋ, ψ = N. Ablösung kraftbasiert bei N = 0 (vor x = 0),
      Aufsetzen bei x = 0 mit Kraftsprung C·|ẋ|. Stoßzahl ohne Schwerkraft e_kv_geklippt(ζ), größer als
      exp(−πζ/√(1−ζ²)), weil die Feder bei der Ablösung noch eingedrückt ist.
  hc  Hunt-Crossley: N = K_h·δⁿ·(1 + 1,5·α·δ̇), δ = −x, ψ = 1 − 1,5·α·ẋ (K_h in N/mⁿ, α in s/m). Stoßzahl
      ohne Schwerkraft exakt und unabhängig von n und K_h aus c·v·(1 + e) = ln((1 + c·v)/(1 − c·v·e)), c = 1,5·α
      (e_hc); erste Ordnung e ≈ 1 − α·v wie bei Hunt und Crossley (1975). hc_aequivalent() wählt K_h so, dass die
      Tangentensteifigkeit in der statischen Ruhelage K ist, K_h = (K/n)ⁿ·(M·g)^(1−n), und α so, dass die
      Stoßzahl bei v_ref (Standard 0,5 m/s, Aufprall im Hüpfzustand des V1-Kandidaten) der des KV-Kontakts gleicht.
      Die Dämpfung um die Ruhelage ist dann klein (c_lin = 1,5·α·M·g ≪ C). Beide Zuordnungen sind Annahmen;
      gemessen ist keine.

Integration:
  methode 'exakt' (Kelvin-Voigt, unterkritisch): je knickfreiem Stück geschlossen. Kontakt: lineare Schwingung
    mit Sinusanregung (Partikulärlösung über D(Ω) = K − M·Ω² + i·C·Ω, homogene Lösung des gedämpften Schwingers);
    Flug: ballistisch mit zweimal integrierter Anregung. Kontaktast: affine Periodenabbildung, Fixpunkt direkt.
  methode 'ivp' (Hunt-Crossley, Frequenzrampe, Gegenprobe): solve_ivp DOP853, rtol 1e-11, mit Ereignissen.
  Übergänge: Schaltfunktion auf einem Raster h = min(T/10000, 2π/(300·ω_n)) abgetastet, erster Vorzeichenwechsel
  mit brentq (xtol 1e-15 s) auf der geschlossenen bzw. dichten Lösung – auch kurze Ausflüge innerhalb eines
  Integratorschritts.
Ausgaben je Periode: ∫(N − M·g)^p dt (p = 1…3, Gauß-Legendre mit 8 Knoten je ≤ 100 µs) → exaktes Zeitmittel
und Schiefe; exakte Flugzeit → λ; F_min, F_max (Rasterextremum mit Brent nachgeschärft); Aufsetzer mit Zeit,
Aufprall- und Ablösegeschwindigkeit und Stoßspitze; Poincaré-Schnitt (x, ẋ, v_S) zu Periodenbeginn; Randterm
R = M·Δv_S/T_w mit ⟨N⟩ = M·g + R exakt. Parallel Stichproben im Raster der Engine (Δt = T/2000) für den
direkten Vergleich mit den CSV-Daten; Zustand und Kraft zu beliebigen Zeiten mit abtasten(). Darauf aufbauend:
Periodenerkennung P1/Pn/irregulär, Newton-Schießverfahren auf die p-fache Periodenabbildung,
Floquet-Multiplikatoren (zentrale Differenzen; die Jacobi-Matrix enthält die Stoß- und Ablösezeitpunkte,
anders als die der RK4-Abbildung), Einzugsprüfung: Start auf dem Kontaktast (oder in der statischen Ruhelage)
zur Wurfphase t₀, Geschwindigkeitsstoß Δv (Stoßimpuls M·Δv), Endzustand Kontaktast oder Hüpfen, kritische
Wurfgeschwindigkeit (Raster, dann Bisektion), Stoßspitzen; Anlauf über eine Frequenzrampe
ρ(t) = (1 − cos(πt/T_r))/2 mit Profilzeit Θ = ∫ρ dt.

Aufruf:
  python3 ereignisloeser.py --point 35 116 [--start std|imp|orbit] [--t-sim 15 --t-eval 10]
                                        Langlauf (Standard: Start wie die Engine), Kenngrößen exakt und im Raster
  python3 ereignisloeser.py --point 35 116 --orbit
                                        Kontaktast (falls vorhanden) und Newton auf den erreichten Zustand, Floquet
  python3 ereignisloeser.py --candidate --einzug
                                        V1-Kandidat (3×100 g, 8 mm, 10 Hz, K = 1,5e6 N/m, ζ = 0,05), synchron:
                                        kritischer Wurf über die Wurfphasen 0, T/4, T/2, 3T/4 (ca. 70 s)
  python3 ereignisloeser.py --candidate --einzug --law hc --wurfphase 0 --vmin 0.2 --dv 0.05
                                        dasselbe mit dem Hunt-Crossley-Gegenstück (n = 1,5; ca. 40 s)
  python3 ereignisloeser.py --candidate --stoss 0.5
                                        Einzelstoß beider Kontaktgesetze bei 0,5 m/s mit Energiebilanz
  python3 ereignisloeser.py --point 35 116 --rampe 2
                                        Anlauf mit Frequenzrampe T_r = 2 s statt Standardstart
Optionen: --K, --zeta oder --C, --f, --hub, --sinus, --law kv|hc|beide, --hc-n, --hc-vref, --wurfphase, --dv,
--vmin, --vmax; mit --start std beginnt die Einzugsprüfung in der statischen Ruhelage (wie die Nachrechnung 10/2026).
Die Einzugsprüfung startet standardmäßig auf dem Kontaktast; an Punkten ohne Kontaktast (z. B. (0°, 0°) der
Referenz) dort --start std verwenden. Hüpft schon der Start ohne Wurf, wird das gemeldet statt einer Schwelle.
Fehleingaben (z. B. --t-eval > --t-sim, leeres Wurfraster, Rampe kein Vielfaches von 2T) enden mit einer
einzeiligen Meldung und Rückgabewert 2. Überkritische Dämpfung (ζ ≥ 1) rechnet Kelvin-Voigt über solve_ivp.

Rechenzeit (ein Kern): Kelvin-Voigt geschlossen 5–8 ms je Periode (15-s-Langlauf ≈ 1 s, Kontaktast direkt
≈ 20 ms); solve_ivp (Hunt-Crossley, Rampe) ≈ 25 ms je Periode im Hüpfzustand, ≈ 0,1 s je Periode im Dauerkontakt
des steifen Kandidaten.

Abgleich (tests/test_ereignisloeser.py; Referenzwerte aus der Nachrechnung 10/2026 mit einem unabhängig
geschriebenen halbanalytischen Löser): Kontaktast gegen linear_solver auf ≤ 1e-6 N (Wellenform 1,3e-7 N;
F_min(120°, 240°) = 5,330390 N), gegen die liftoff-freien Punkte von sweep_19x19.csv und sweep_7x7_sinus.csv
auf ≤ 1e-4 und gegen finesweep.run (gleicher Start) auf ≤ 1e-5 N; Satelliteninsel (35°, 116°): Hüpfzustand
λ = 75,8154 %, F_max = 39,473 N, |μ| = 0,7426, Kontaktorbit F_min = 0,3665 N, |μ| = 0,2921 = e^{−CT/(2M)},
Stoßtabelle auf den Kontaktorbit (bei t₀ = 0 hüpft −0,10 m/s, +0,10 und +0,20 m/s nicht, +0,15 m/s aber doch:
das Einzugsgebiet ist nicht monoton), Frequenzrampe 2 s wählt den Kontaktorbit; V1-Kandidat synchron (ζ = 0,05),
Wurf aus der Ruhelage bei t₀ = 0: 0,25 m/s kehrt zurück, 0,30 m/s hüpft mit λ = 97,987 % und Stoßspitze
483,66 N, Aufsetzen bei t/T = 0,2485, |μ| ≈ e = 0,8588; Schwelle über die Wurfphase 0,30/0,24/0,26/0,60 m/s
(t₀/T = 0/0,25/0,5/0,75; alle kleineren Würfe kehren zurück); Hot-Spot (0°, 208,421°) ab ≈ 5 s auf dem Attraktor,
⟨N⟩ − M·g = +0,0205 mN im Fenster 5–15 s (die −43,5 mN der Engine sind ein Artefakt der Festschritt-RK4).
Gegenproben der Integrationswege: DOP853 gegen geschlossen und Hunt-Crossley (n = 1, α = 0) gegen Kelvin-Voigt
(C = 0) auf ≤ 1e-10 m; Einzelstoß: Stoßzahl gegen die geschlossenen Formeln auf ≤ 1e-8 (Kelvin-Voigt auch
überkritisch, ζ = 1…2, über solve_ivp), Energiebilanz ≤ 1e-7.
Am Kandidaten liefert Hunt-Crossley (n = 1,5) bei t₀ = 0 dieselbe Hüpfschwelle (0,29–0,30 m/s), aber
Stoßspitzen um 1050 N statt 484 N: Stöße von einigen 10² N sind in beiden Gesetzen belastbar, der Einzelwert
hängt vom Kontaktgesetz ab.

Matthias Früh · PCMMS · Oktober 2026
"""
import argparse
import math
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq, minimize_scalar
from scipy.special import lambertw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from finesweep import M, G, F_HZ, RTOP, THOLD, TFAST, K, C_DAMP  # noqa: E402

HUB_REF = RTOP / THOLD                      # Hub Spitze-Spitze der Engine, 7,6923 mm
GL_X, GL_W = np.polynomial.legendre.leggauss(8)
N_STICH = 2000                              # Stichproben je Periode wie in der Engine (Δt = 50 µs bei 10 Hz)
T_TOL = 1e-12                               # kürzere Reststücke werden übersprungen [s]


def c_aus_zeta(zeta, K_c, M_ges=M):
    return 2.0 * zeta * math.sqrt(K_c * M_ges)


def e_kv_geklippt(zeta):
    """Stoßzahl des Engine-Kontakts ohne Schwerkraft: Ablösung bei N = 0, also bei ω_d·t_s = π − atan(2ζ√(1−ζ²)
    /(1 − 2ζ²)); e = exp(−ζ·ω_n·t_s)·|cos(ω_d t_s) − ζ/√(1−ζ²)·sin(ω_d t_s)|. Überkritisch (ζ > 1, Wurzeln
    r₁,₂ = −ζ ± √(ζ²−1) in Einheiten von ω_n): N = 0 bei ω_n·t_s = ln(r₂/r₁)/√(ζ²−1), e = exp(r₁·ω_n·t_s)·r₁/r₂;
    ζ = 1: e = e⁻² (stetig in ζ)."""
    if zeta > 1.0:
        s = math.sqrt(zeta**2 - 1.0)
        r1, r2 = -zeta + s, -zeta - s
        return math.exp(r1 * math.log(r2 / r1) / s) * r1 / r2
    if zeta == 1.0:
        return math.exp(-2.0)
    w = math.sqrt(1.0 - zeta**2)
    ph = math.pi - math.atan2(2.0 * zeta * w, 1.0 - 2.0 * zeta**2)
    return math.exp(-zeta * ph / w) * abs(math.cos(ph) - zeta / w * math.sin(ph))


class System:
    """Parameter eines Laufs. phis [°] je Modul, m_mod [kg] und hub [m] je Modul (Skalar: alle gleich), m0
    Restmasse [kg], f [Hz], profil 'egg' | 'sinus', gesetz 'kv' (K [N/m], C [N·s/m]) | 'hc' (K = K_h [N/mⁿ],
    alpha [s/m], n). Ohne Angaben: Engine bei (0°, 120°, 240°)."""

    def __init__(self, phis=(0.0, 120.0, 240.0), m_mod=None, m0=0.0, hub=HUB_REF, f=F_HZ, profil='egg',
                 gesetz='kv', K=K, C=C_DAMP, alpha=0.0, n=1.5, g=G):
        self._kw = dict(phis=phis, m_mod=m_mod, m0=m0, hub=hub, f=f, profil=profil, gesetz=gesetz, K=K, C=C,
                        alpha=alpha, n=n, g=g)
        self.phis = np.atleast_1d(np.asarray(phis, float))
        nm = self.phis.size
        self.m = np.broadcast_to(np.asarray(M / 3 if m_mod is None else m_mod, float), (nm,)).astype(float)
        self.hub = np.broadcast_to(np.asarray(hub, float), (nm,)).astype(float)
        self.m0, self.f, self.T, self.g = float(m0), float(f), 1.0 / f, float(g)
        self.M = M if (m_mod is None and m0 == 0.0 and nm == 3) else self.m0 + float(self.m.sum())
        self.profil, self.gesetz = profil, gesetz
        self.K, self.C, self.alpha, self.n = float(K), float(C), float(alpha), float(n)
        self.tau = np.mod(self.phis / (360.0 * self.f), self.T)
        self.oh, self.of, self.w = math.pi / (THOLD * self.T), math.pi / (TFAST * self.T), 2 * math.pi * self.f
        kn = [] if profil == 'sinus' else [k for t in self.tau for k in (t, (t + THOLD * self.T) % self.T)]
        self.kinks = np.unique(np.round(np.array(kn, float), 15))
        if gesetz == 'kv':
            self.sig, self.wn2 = self.C / (2 * self.M), self.K / self.M
            self.wd = math.sqrt(self.wn2 - self.sig**2) if self.wn2 > self.sig**2 else float('nan')
            self.w_k = math.sqrt(self.wn2)
        else:                                       # Tangentensteifigkeit in der Ruhelage (g = 0: grob)
            d0 = (self.M * max(self.g, 1.0) / self.K) ** (1.0 / self.n)
            self.w_k = math.sqrt(self.n * self.K * d0 ** (self.n - 1.0) / self.M)

    def mit(self, **kw):
        return System(**{**self._kw, **kw})

    def ruhelage(self):
        if self.gesetz == 'kv':
            return -self.M * self.g / self.K
        return -(self.M * self.g / self.K) ** (1.0 / self.n)

    def schalt(self, x, v):
        psi = (-self.K * x - self.C * v) if self.gesetz == 'kv' else (1.0 - 1.5 * self.alpha * v)
        return np.minimum(-x, psi)

    def kraft(self, x, v):
        if self.gesetz == 'kv':
            return -self.K * x - self.C * v
        return self.K * np.maximum(-x, 0.0) ** self.n * (1.0 - 1.5 * self.alpha * v)

    def daempfung(self, x, v):
        """Momentane Dissipationsleistung des Kontakts (für die Energiebilanz des Einzelstoßes)."""
        if self.gesetz == 'kv':
            return self.C * v * v
        return 1.5 * self.alpha * self.K * np.maximum(-x, 0.0) ** self.n * v * v

    # ── Profil ──
    def _profil(self, u, ordnung):
        """Ableitung 1 oder 2 der Modulbahnen nach der Zeit bei Modulphase u (Feld (..., nm))."""
        h = self.hub
        if self.profil == 'sinus':
            return 0.5 * h * self.w * np.cos(self.w * u) if ordnung == 1 else -0.5 * h * self.w**2 * np.sin(self.w * u)
        uf = u - THOLD * self.T
        if ordnung == 1:
            return np.where(u < THOLD * self.T, THOLD * h * self.oh * np.cos(self.oh * u),
                            -TFAST * h * self.of * np.cos(self.of * uf))
        return np.where(u < THOLD * self.T, -THOLD * h * self.oh**2 * np.sin(self.oh * u),
                        TFAST * h * self.of**2 * np.sin(self.of * uf))

    def v_mod(self, t, rampe=0.0):
        """Σ m_j·ė_j(t)/M, mit Frequenzrampe: ρ·Σ m_j·e_j'(Θ)/M."""
        th, rho, _ = rampe_theta(t, rampe)
        u = np.mod(np.subtract.outer(np.asarray(th, float), self.tau), self.T)
        return rho * (self._profil(u, 1) @ self.m) / self.M

    def q_rampe(self, t, Tr):
        th, rho, rhod = rampe_theta(t, Tr)
        u = np.mod(th - self.tau, self.T)
        return float(self.m @ (self._profil(u, 2) * rho * rho + self._profil(u, 1) * rhod))

    def terme(self, ta, tb):
        """Sinusterme von Q auf dem knickfreien Stück [ta, tb]: Q(ta + s) = Σ amp·sin(Om·s + ph)."""
        L = tb - ta
        u = np.mod(0.5 * (ta + tb) - self.tau, self.T) - 0.5 * L          # Modulphase bei ta
        if self.profil == 'sinus':
            return -self.m * 0.5 * self.hub * self.w**2, np.full(u.size, self.w), self.w * u
        hold = u + 0.5 * L < THOLD * self.T
        amp = np.where(hold, -self.m * THOLD * self.hub * self.oh**2, self.m * TFAST * self.hub * self.of**2)
        return amp, np.where(hold, self.oh, self.of), np.where(hold, self.oh * u, self.of * (u - THOLD * self.T))

    # ── geschlossene Stücke (Kelvin-Voigt) ──
    def kontakt_stueck(self, amp, Om, ph, xa, va):
        Gc = -amp * np.exp(1j * ph) / (self.K - self.M * Om**2 + 1j * self.C * Om)
        Gv = 1j * Om * Gc
        xs = -self.M * self.g / self.K
        d0 = xa - xs - np.imag(Gc.sum())
        d1 = va - np.imag(Gv.sum())
        sig, wd = self.sig, self.wd
        b1, b2 = (d1 + sig * d0) / wd, -(sig * d1 + self.wn2 * d0) / wd

        def fn(s):                                  # Im(e^{iΩs}·G) = sin(Ωs)·Re G + cos(Ωs)·Im G
            s = np.asarray(s, float)
            P = np.multiply.outer(s, Om)
            sP, cP = np.sin(P), np.cos(P)
            ex, co, si = np.exp(-sig * s), np.cos(wd * s), np.sin(wd * s)
            return (xs + (sP * Gc.real + cP * Gc.imag).sum(-1) + ex * (d0 * co + b1 * si),
                    (sP * Gv.real + cP * Gv.imag).sum(-1) + ex * (d1 * co + b2 * si))
        return fn

    def flug_stueck(self, amp, Om, ph, xa, va):
        a, s0, c0, g = amp / self.M, np.sin(ph), np.cos(ph), self.g

        def fn(s):
            s = np.asarray(s, float)
            P = np.multiply.outer(s, Om) + ph
            ux = (s0 - np.sin(P)) / Om**2 + np.multiply.outer(s, c0 / Om)
            uv = (c0 - np.cos(P)) / Om
            return xa + va * s - 0.5 * g * s * s - (ux * a).sum(-1), va - g * s - (uv * a).sum(-1)
        return fn


def rampe_theta(t, Tr):
    """Profilzeit Θ(t) = ∫ρ dt, ρ = (1 − cos(πt/T_r))/2 für t < T_r, danach Θ = t − T_r/2; Rückgabe Θ, ρ, ρ'."""
    if Tr <= 0 or np.all(np.asarray(t) >= Tr):
        return np.asarray(t, float) - 0.5 * Tr, 1.0, 0.0
    x = math.pi * float(t) / Tr
    return float(t) / 2 - Tr / (2 * math.pi) * math.sin(x), 0.5 * (1 - math.cos(x)), math.pi / (2 * Tr) * math.sin(x)


def _ivp_stueck(sy, t, tb, x, v, kontakt, qf, rtol):
    def rhs(tt, y):
        F = float(sy.kraft(y[0], y[1])) if kontakt else 0.0
        return (y[1], -sy.g + (F - qf(tt)) / sy.M)

    def ev(tt, y):
        return float(sy.schalt(y[0], y[1]))
    ev.terminal, ev.direction = True, (-1 if kontakt else 1)
    sol = solve_ivp(rhs, (t, tb), (x, v), method='DOP853', rtol=rtol, atol=(1e-15, 1e-12), events=ev,
                    dense_output=True)
    return (lambda s: sol.sol(t + np.asarray(s, float))), sol.t[-1] - t, sol.status == 1


def _wechsel(sy, fn, L, kontakt, h):
    """Erster Moduswechsel auf (0, L]: Abtastung der Schaltfunktion, brentq im ersten Wechselintervall.
    Rückgabe s_e (None ohne Wechsel), Raster s, Zustände X, V auf dem Raster."""
    s = np.linspace(0.0, L, max(2, int(math.ceil(L / h))) + 1)[1:]
    X, V = fn(s)
    gt = sy.schalt(X, V)
    hit = np.flatnonzero(gt <= 0.0) if kontakt else np.flatnonzero(gt > 0.0)
    if hit.size == 0:
        return None, s, X, V
    k = hit[0]
    lo = 0.0 if k == 0 else s[k - 1]
    g_lo = float(sy.schalt(*fn(lo))) if k == 0 else gt[k - 1]
    if (g_lo > 0.0) if kontakt else (g_lo <= 0.0):
        se = brentq(lambda u: float(sy.schalt(*fn(u))), lo, s[k], xtol=1e-15, rtol=8.9e-16)
    else:
        se = lo                                     # Wechsel schon am Stückanfang (streifender Übergang)
    return se, s, X, V


def _verfeinern(sy, fn, a, b, sgn):
    """Extremum von sgn·N auf [a, b] (Brent, beschränkt); Rückgabe Wert, Stelle."""
    r = minimize_scalar(lambda u: -sgn * float(sy.kraft(*fn(u))), bounds=(a, b), method='bounded',
                        options=dict(xatol=1e-13))
    return -sgn * r.fun, r.x


def simulate(sy, x0, v0, t0=0.0, n_per=150, methode='auto', h=None, rampe=0.0, keep=False, rtol=1e-11,
             auswertung=True):
    """n_per Perioden ab t0 (Zustand x0, v0). Rückgabe dict mit Feldern je Periode (D1…D3 = ∫(N − Mg)^p dt,
    tflug, Fmax, Fmin, ntd; Stichproben S1…S3, Smin, Smax, Slo, Sn), Poincaré-Schnitt PX, PV, PS (n_per + 1),
    Aufsetzerliste (t_auf, ẋ_auf, t_ab, ẋ_ab, x_ab, F_spitze, t_spitze) und Endzustand. rampe = T_r > 0: Anlauf
    mit Frequenzrampe ab t = 0 (T_r/2 ganzzahliges Vielfaches von T). auswertung=False: nur Poincaré-Schnitt."""
    T, MGs = sy.T, sy.M * sy.g
    exakt = methode != 'ivp' and sy.gesetz == 'kv' and math.isfinite(sy.wd)
    if methode == 'exakt' and not exakt:
        raise ValueError('geschlossene Lösung nur für Kelvin-Voigt, unterkritisch')
    if rampe > 0 and (t0 != 0.0 or abs(rampe / (2 * T) - round(rampe / (2 * T))) > 1e-9):
        raise ValueError('Rampe nur ab t0 = 0 und mit T_r/2 als Vielfachem von T')
    h = min(T / 10000, 2 * math.pi / (300 * sy.w_k)) if h is None else h
    dt_gl, dt_s = min(T / 1000, 2 * math.pi / (20 * sy.w_k)), T / N_STICH
    names = ('D1', 'D2', 'D3', 'tflug', 'Fmax', 'Fmin', 'ntd', 'S1', 'S2', 'S3', 'Smin', 'Smax', 'Slo', 'Sn')
    R = {k: np.zeros(n_per) for k in names}
    PX, PV, PS = (np.zeros(n_per + 1) for _ in range(3))
    auf, stuecke = [], []
    x, v, t = float(x0), float(v0), float(t0)
    kontakt = bool(sy.schalt(x, v) > 0)
    ph_best = None                                  # (Wert, fn, a, b, t) der laufenden Kontaktphase
    if kontakt:                                     # Start im Kontakt: Phase ohne Aufsetzen (ẋ_auf = nan)
        auf.append([t, np.nan, np.nan, np.nan, np.nan, -np.inf, np.nan])
    stall = 0
    for c in range(n_per):
        tc = t0 + c * T
        PX[c], PV[c], PS[c] = x, v, v + float(sy.v_mod(tc, rampe))
        acc = dict(D1=0.0, D2=0.0, D3=0.0, tflug=0.0, ntd=0, S1=0.0, S2=0.0, S3=0.0, Smin=np.inf, Smax=-np.inf,
                   Slo=0, Sn=0)
        best = {1: (-np.inf, None, 0, 0, 0), -1: (np.inf, None, 0, 0, 0)}   # Periodenmaximum und -minimum
        im_rampe = tc < rampe - 1e-12
        if im_rampe or sy.kinks.size == 0:
            breaks = [tc + T]
        else:
            base = math.floor(tc / T) * T
            kk = np.concatenate([base + sy.kinks, base + T + sy.kinks])
            breaks = sorted(kk[(kk > tc + T_TOL) & (kk < tc + T - T_TOL)].tolist()) + [tc + T]
        for tb in breaks:
            while tb - t > T_TOL:
                if exakt and not im_rampe:
                    amp, Om, ph = sy.terme(t, tb)
                    fn = (sy.kontakt_stueck if kontakt else sy.flug_stueck)(amp, Om, ph, x, v)
                    L, ev_end = tb - t, False
                else:
                    if im_rampe:
                        qf = (lambda tt: sy.q_rampe(tt, rampe))
                    else:
                        amp, Om, ph = sy.terme(t, tb)
                        qf = (lambda tt, ta=t, a=amp, o=Om, p=ph: float(a @ np.sin(o * (tt - ta) + p)))
                    fn, L, ev_end = _ivp_stueck(sy, t, tb, x, v, kontakt, qf, rtol)
                se, s, X, V = _wechsel(sy, fn, L, kontakt, h)
                if se is None and ev_end:
                    se = L
                e = L if se is None else se
                stall = stall + 1 if e < T_TOL else 0
                if stall > 50:
                    raise RuntimeError(f'Ereignissuche steckt fest bei t = {t:.12f} s')
                xe, ve = (float(q) for q in fn(e))
                if keep and e > 0:
                    stuecke.append((t, e, kontakt, fn))
                if auswertung and e > 0:
                    ka = math.ceil(round((t - t0) / dt_s, 6))
                    kb = math.ceil(round((t + e - t0) / dt_s, 6))
                    ss = t0 + np.arange(ka, kb) * dt_s - t
                    if kontakt:
                        nsub = max(1, int(math.ceil(e / dt_gl)))
                        ed = np.linspace(0.0, e, nsub + 1)
                        mid, hw = 0.5 * (ed[1:] + ed[:-1]), 0.5 * (ed[1:] - ed[:-1])
                        d = sy.kraft(*fn((mid[:, None] + hw[:, None] * GL_X).ravel())) - MGs
                        wq = (hw[:, None] * GL_W).ravel()
                        acc['D1'] += (wq * d).sum()
                        acc['D2'] += (wq * d * d).sum()
                        acc['D3'] += (wq * d * d * d).sum()
                        sel = s < e
                        sa = np.concatenate([[0.0], s[sel], [e]])
                        Na = np.concatenate([[float(sy.kraft(x, v))], sy.kraft(X[sel], V[sel]),
                                             [float(sy.kraft(xe, ve))]])
                        for sgn in (1, -1):
                            k = int(np.argmax(sgn * Na))
                            if sgn * Na[k] > sgn * best[sgn][0]:
                                best[sgn] = (Na[k], fn, sa[max(k - 1, 0)], sa[min(k + 1, sa.size - 1)], t)
                            if sgn == 1 and (ph_best is None or Na[k] > ph_best[0]):
                                ph_best = (Na[k], fn, sa[max(k - 1, 0)], sa[min(k + 1, sa.size - 1)], t)
                        Ns = sy.kraft(*fn(ss)) if ss.size else np.zeros(0)
                    else:
                        acc['tflug'] += e
                        acc['D1'] -= MGs * e
                        acc['D2'] += MGs**2 * e
                        acc['D3'] -= MGs**3 * e
                        Ns = np.zeros(ss.size)
                    if Ns.size:
                        dN = Ns - MGs
                        acc['S1'] += dN.sum()
                        acc['S2'] += (dN * dN).sum()
                        acc['S3'] += (dN**3).sum()
                        acc['Smin'] = min(acc['Smin'], Ns.min())
                        acc['Smax'] = max(acc['Smax'], Ns.max())
                        acc['Slo'] += int((Ns < 1e-9).sum())
                        acc['Sn'] += Ns.size
                x, v = xe, ve
                if se is None:
                    t = tb
                    continue
                t += e
                kontakt = not kontakt
                if kontakt:
                    acc['ntd'] += 1
                    auf.append([t, v, np.nan, np.nan, np.nan, -np.inf, np.nan])
                    ph_best = None
                elif auf:
                    auf[-1][2:5] = [t, v, x]
                    if ph_best is not None and ph_best[1] is not None:
                        val, ts = _verfeinern(sy, ph_best[1], ph_best[2], ph_best[3], 1) \
                            if ph_best[3] > ph_best[2] else (ph_best[0], ph_best[2])
                        auf[-1][5:7] = [max(val, ph_best[0]), ph_best[4] + ts]
        for sgn, key in ((1, 'Fmax'), (-1, 'Fmin')):
            val, fb, a, b, _ = best[sgn] if best[sgn][1] is not None else (0.0, None, 0, 0, 0)
            if fb is not None and b > a:
                val = sgn * max(sgn * val, sgn * _verfeinern(sy, fb, a, b, sgn)[0])
            R[key][c] = val
        for k_ in acc:
            R[k_][c] = acc[k_]
    PX[n_per], PV[n_per], PS[n_per] = x, v, v + float(sy.v_mod(t0 + n_per * T, rampe))
    if kontakt and auf and ph_best is not None:     # offene Kontaktphase am Laufende
        auf[-1][5:7] = [ph_best[0], ph_best[4] + 0.5 * (ph_best[2] + ph_best[3])]
    R.update(PX=PX, PV=PV, PS=PS, aufsetzer=np.array(auf, float).reshape(-1, 7), t0=t0, T=T, M=sy.M, MG=MGs,
             kontakt_end=kontakt, stuecke=stuecke, rampe=rampe)
    return R


def kenngroessen(r, c0=0, c1=None):
    """Kenngrößen im Fenster der Perioden [c0, c1): exakt (Zeitmittel, Schiefe, λ, F_min, F_max, Randterm R,
    Rest ⟨N⟩ − M·g − R, Aufsetzer je Periode) und aus den Engine-Stichproben (Endung _s)."""
    c1 = len(r['D1']) if c1 is None else c1
    if not 0 <= c0 < c1 <= len(r['D1']):
        raise ValueError(f'Auswertefenster der Perioden [{c0}, {c1}) liegt nicht im Lauf (0 … {len(r["D1"])})')
    sl, Tw, MGs = slice(c0, c1), (c1 - c0) * r['T'], r['MG']
    out = {}
    for suf, (a1, a2, a3), nrm in (('', ('D1', 'D2', 'D3'), Tw), ('_s', ('S1', 'S2', 'S3'), r['Sn'][sl].sum())):
        m1, m2, m3 = (r[a][sl].sum() / nrm for a in (a1, a2, a3))
        var = m2 - m1 * m1
        out['F_mean' + suf] = MGs + m1
        out['F_skew' + suf] = (m3 - 3 * m1 * m2 + 2 * m1**3) / var**1.5 if var > 0 else np.nan
    out['liftoff'] = 100.0 * r['tflug'][sl].sum() / Tw
    out['liftoff_s'] = 100.0 * r['Slo'][sl].sum() / r['Sn'][sl].sum()
    out['F_max'], out['F_max_s'] = r['Fmax'][sl].max(), r['Smax'][sl].max()
    out['F_min'] = 0.0 if out['liftoff'] > 0 else r['Fmin'][sl].min()
    out['F_min_s'] = r['Smin'][sl].min()
    out['R'] = r['M'] * (r['PS'][c1] - r['PS'][c0]) / Tw
    out['dF'] = out['F_mean'] - MGs
    out['rest'] = out['dF'] - out['R']
    out['aufsetzer_je_periode'] = r['ntd'][sl].mean()
    out['peak_ratio'] = (out['F_max'] - MGs) / (MGs - out['F_min']) if MGs - out['F_min'] > 1e-6 else np.nan
    return out


def periode(r, n_last=30, pmax=30, tol_v=1e-9, tol_x=1e-11):
    """Periode aus dem Poincaré-Schnitt: kleinstes p ≤ pmax mit |Δẋ| < tol_v und |Δx| < tol_x über die letzten
    n_last Perioden (höchstens der halbe Lauf), dessen p Schnittpunkte sich um mehr als 1000·tol unterscheiden
    (sonst täuscht eine spiralförmige Annäherung an einen P1-Orbit bei komplexen Multiplikatoren eine höhere
    Periode vor); Einschwingzeit = Beginn der Wiederkehr bis zum Laufende. (−1, nan): irregulär oder nicht
    eingeschwungen."""
    X, V = r['PX'], r['PV']
    n = V.size - 1
    n_last = max(1, min(n_last, n // 2))
    for p in range(1, pmax + 1):
        if n < n_last + p:
            break
        idx = np.arange(n - n_last - p + 1, n - p + 1)
        dist = [max(abs(V[n] - V[n - j]) / tol_v, abs(X[n] - X[n - j]) / tol_x) for j in range(1, p)]
        if dist and min(dist) < 1e3:
            continue
        if np.max(np.abs(V[idx + p] - V[idx])) < tol_v and np.max(np.abs(X[idx + p] - X[idx])) < tol_x:
            bad = np.flatnonzero((np.abs(V[p:] - V[:-p]) >= tol_v) | (np.abs(X[p:] - X[:-p]) >= tol_x))
            return p, r['t0'] + (0 if bad.size == 0 else bad[-1] + 1) * r['T']
    return -1, float('nan')


def periodenname(p):
    return 'irregulär oder nicht eingeschwungen' if p < 0 else f'P{p}'


def kontaktorbit(sy, t0=0.0):
    """Kontaktast (Kelvin-Voigt): Im Dauerkontakt ist die Periodenabbildung affin, z ↦ Φ·z + p, mit
    Φ = e^{−σT}·[[c + σ·s/ω_d, s/ω_d], [−ω_n²·s/ω_d, c − σ·s/ω_d]], c = cos ω_d T, s = sin ω_d T, σ = C/(2M).
    Fixpunkt z* = (I − Φ)⁻¹·p, Floquet-Multiplikatoren e^{(−σ ± iω_d)T}. Rückgabe z*, Multiplikatoren, gültig
    (N > 0 und x < 0 auf der ganzen Periode; sonst existiert kein Kontaktast)."""
    if sy.gesetz != 'kv' or not math.isfinite(sy.wd):
        raise ValueError('kontaktorbit geschlossen nur für Kelvin-Voigt mit ζ < 1; sonst newton() ab der Ruhelage '
                         '(startzustand(..., "orbit") wählt das selbst)')
    T, sig, wd = sy.T, sy.sig, sy.wd
    z = np.zeros(2)
    tbs = sorted(((sy.kinks - t0) % T)[((sy.kinks - t0) % T) > T_TOL].tolist()) + [T]
    t = 0.0
    for tb in tbs:
        z = np.array([float(q) for q in sy.kontakt_stueck(*sy.terme(t0 + t, t0 + tb), *z)(tb - t)])
        t = tb
    c, s = math.cos(wd * T), math.sin(wd * T)
    Phi = math.exp(-sig * T) * np.array([[c + sig * s / wd, s / wd], [-sy.wn2 * s / wd, c - sig * s / wd]])
    zs = np.linalg.solve(np.eye(2) - Phi, z)
    r = simulate(sy, zs[0], zs[1], t0, 1)
    return zs, np.linalg.eigvals(Phi), bool(r['tflug'][0] == 0 and r['Fmin'][0] > 0)


def newton(sy, z0, t0=0.0, p=1, iters=12, dz=(1e-9, 1e-7), tol=1e-11, **kw):
    """Newton-Schießverfahren auf P^p(z) = z (Poincaré-Schnitt bei t0 + k·T), Jacobi-Matrix aus zentralen
    Differenzen; Floquet-Multiplikatoren = Eigenwerte der Jacobi-Matrix am Fixpunkt. Residuum skaliert mit
    1 mm bzw. 0,1 m/s."""
    def pm(z):
        r = simulate(sy, z[0], z[1], t0, p, auswertung=False, **kw)
        return np.array([r['PX'][p], r['PV'][p]])
    z, res, J = np.array(z0, float), [], np.eye(2)
    for _ in range(iters):
        Fz = pm(z) - z
        res.append(float(max(abs(Fz[0]) / 1e-3, abs(Fz[1]) / 1e-1)))
        cols = []
        for j in range(2):
            e = np.zeros(2)
            e[j] = dz[j]
            cols.append((pm(z + e) - pm(z - e)) / (2 * dz[j]))
        J = np.column_stack(cols)
        if res[-1] < tol:
            break
        z = z + np.linalg.solve(J - np.eye(2), -Fz)
    return dict(z=z, mu=np.linalg.eigvals(J), res=res, konvergiert=res[-1] < tol)


def startzustand(sy, art='std', t0=0.0):
    """std/ruhe: statische Ruhelage, ẋ = 0 (Start der Engine); imp: v_S(t0) = 0; orbit: auf dem Kontaktast
    (Kelvin-Voigt unterkritisch geschlossen, sonst Newton ab der Ruhelage)."""
    if art == 'orbit':
        if sy.gesetz == 'kv' and math.isfinite(sy.wd):
            zs, _, ok = kontaktorbit(sy, t0)
        else:
            ok = False
            if sy.gesetz == 'hc':
                # Newton ab dem Kelvin-Voigt-Orbit gleicher Tangentensteifigkeit, um die Differenz der statischen
                # Einfederungen verschoben; ab der Ruhelage divergiert Newton am steifen Kandidaten je nach
                # Wurfphase in den Flug.
                kv = sy.mit(gesetz='kv', K=sy.M * sy.w_k ** 2)
                if math.isfinite(kv.wd):
                    zk, _, okk = kontaktorbit(kv, t0)
                    if okk:
                        o = newton(sy, zk + np.array([sy.ruhelage() - kv.ruhelage(), 0.0]), t0, iters=12)
                        zs = o['z']
                        ok = o['konvergiert'] and simulate(sy, *zs, t0, 1)['tflug'][0] == 0
            if not ok:
                zs = newton(sy, (sy.ruhelage(), 0.0), t0, iters=6)['z']
                ok = simulate(sy, *zs, t0, 1)['tflug'][0] == 0
        if not ok:
            raise ValueError('kein Kontaktast an diesem Punkt: Start auf dem Orbit nicht möglich '
                             '(Start in der Ruhelage: start="std", CLI --start std)')
        return zs
    v0 = -float(sy.v_mod(t0)) if art == 'imp' else 0.0
    return np.array([sy.ruhelage(), v0])


def wurf(sy, dv, t0=0.0, start='orbit', n_per=160, n_eval=40, z=None, **kw):
    """Geschwindigkeitsstoß Δv (Stoßimpuls M·Δv) zur Wurfphase t0 aus dem Startzustand (orbit: Kontaktast, ruhe:
    statische Ruhelage wie in der Nachrechnung 10/2026; z: vorgegeben); Endzustand über die letzten n_eval
    Perioden: Kontaktast (λ = 0) oder Hüpfen, Stoßspitzen im Fenster und im ganzen Lauf."""
    z = startzustand(sy, start, t0) if z is None else z
    r = simulate(sy, z[0], z[1] + dv, t0, n_per, **kw)
    k = kenngroessen(r, n_per - n_eval, n_per)
    a = r['aufsetzer'][np.isfinite(r['aufsetzer'][:, 1])]
    win = a[a[:, 0] >= t0 + (n_per - n_eval) * sy.T]
    return dict(t0=t0, dv=dv, impuls=sy.M * dv, liftoff=k['liftoff'], F_max=k['F_max'],
                zustand='Kontaktast' if k['liftoff'] == 0 else 'Hüpfen',
                periode=periode(r, n_last=min(20, n_eval), tol_v=1e-6, tol_x=1e-8)[0],
                stoss_spitze=win[:, 5].max() if win.size else np.nan,
                stoss_spitze_max=a[:, 5].max() if a.size else np.nan,
                aufsetzer_je_periode=k['aufsetzer_je_periode'])


def kritischer_wurf(sy, t0=0.0, dvs=None, bisekt=0, start='orbit', **kw):
    """Kleinster Wurf im Raster dvs, der in einen Hüpfzustand führt (danach bisekt Bisektionsschritte zum
    letzten zurückkehrenden Wurf). Das Einzugsgebiet muss nicht monoton sein: Die Angabe gilt für die erste
    Grenze von unten. v_rueck ist stets ein gerechneter Wurf (None ohne Rückkehr); hüpft schon der erste Wurf,
    wird der Start ohne Wurf (Δv = 0) nachgerechnet. Hüpft auch dieser, gibt es keine kritische
    Wurfgeschwindigkeit (start_huepft = True, v_rueck = v_krit = None)."""
    dvs = np.round(np.arange(0.02, 0.6001, 0.02), 6) if dvs is None else np.asarray(dvs, float)
    z = startzustand(sy, start, t0)
    rows, lo, hi = [], None, None
    for dv in dvs:
        rows.append(wurf(sy, float(dv), t0, z=z, **kw))
        if rows[-1]['zustand'] == 'Hüpfen':
            hi = float(dv)
            break
        lo = float(dv)
    if hi is not None and lo is None:
        w0 = rows[0] if hi == 0.0 else wurf(sy, 0.0, t0, z=z, **kw)
        rows = rows if hi == 0.0 else [w0] + rows
        if w0['zustand'] == 'Hüpfen':
            return dict(t0=t0, v_rueck=None, v_krit=None, impuls_krit=None, stoss_spitze=np.nan, laeufe=rows,
                        start_huepft=True)
        lo = 0.0
    for _ in range(bisekt if hi is not None else 0):
        w = wurf(sy, 0.5 * (lo + hi), t0, z=z, **kw)
        rows.append(w)
        lo, hi = (lo, w['dv']) if w['zustand'] == 'Hüpfen' else (w['dv'], hi)
    hop = [w for w in rows if w['zustand'] == 'Hüpfen']
    return dict(t0=t0, v_rueck=lo, v_krit=hi, impuls_krit=None if hi is None else sy.M * hi,
                stoss_spitze=hop[-1]['stoss_spitze'] if hop else np.nan, laeufe=rows, start_huepft=False)


def e_hc(alpha, v):
    """Stoßzahl des Hunt-Crossley-Kontakts ohne Schwerkraft, exakt und unabhängig von n und K_h: Aus
    M·δ̇·dδ̇/dδ = −K_h·δⁿ·(1 + cδ̇), c = 1,5·α, folgt ∫ δ̇/(1 + cδ̇) dδ̇ = 0 zwischen v und −e·v, also
    c·v·(1 + e) = ln((1 + c·v)/(1 − c·v·e)). Entwicklung: e = 1 − α·v + (α·v)² + O((α·v)³). Für c·v > 1
    geschlossen über die Lambertsche W-Funktion, e = (1 + W₀(−(1 + c·v)·e^{−(1+c·v)}))/(c·v) → 1/(c·v)."""
    a = 1.5 * alpha * v
    if a < 1e-8:
        return 1.0 - alpha * v
    if a > 1.0:
        return float((1.0 + lambertw(-(1.0 + a) * math.exp(-1.0 - a)).real) / a)
    f = lambda e: a * (1 + e) - math.log((1 + a) / (1 - a * e))
    return brentq(f, 1e-12, min(1.0, (1 - 1e-15) / a), xtol=1e-15)


def hc_aequivalent(sy, zeta, n=1.5, v_ref=0.5):
    """Hunt-Crossley-Gegenstück zu einem Kelvin-Voigt-System: gleiche Tangentensteifigkeit in der Ruhelage,
    K_h = (K/n)ⁿ·(M·g)^(1−n), und gleiche Stoßzahl bei v_ref, e_hc(α, v_ref) = e_kv_geklippt(ζ) (für jedes ζ
    lösbar, weil e_hc mit α streng fällt und gegen 0 geht)."""
    Kh = (sy.K / n) ** n * (sy.M * sy.g) ** (1.0 - n)
    e0 = e_kv_geklippt(zeta)
    alpha = 0.0
    if e0 < 1 - 1e-12:
        hi = 3 * (1 - e0) / v_ref
        while e_hc(hi, v_ref) > e0:
            hi *= 2.0
        alpha = brentq(lambda al: e_hc(al, v_ref) - e0, 0.0, hi, xtol=1e-14)
    return sy.mit(gesetz='hc', K=Kh, alpha=alpha, n=n)


def stoss(sy, v_in):
    """Einzelstoß ohne Schwerkraft und Anregung: Aufsetzen bei x = 0 mit ẋ = −v_in. Rückgabe Stoßzahl e,
    Stoßspitze, Kontaktdauer, Energieverlust ΔE, Dämpfungsarbeit D und die bei der Ablösung in der
    eingedrückten Feder verbliebene Energie U (Energiebilanz ΔE = D + U)."""
    if not v_in > 0:
        raise ValueError('Aufprallgeschwindigkeit v_in muss positiv sein')
    n = 1.0 if sy.gesetz == 'kv' else sy.n
    dm = ((n + 1) * sy.M * v_in**2 / (2 * sy.K)) ** (1.0 / (n + 1))     # größte Eindrückung ohne Dämpfung
    s0 = sy.mit(phis=(), m_mod=(), m0=sy.M, hub=0.0, g=0.0, f=v_in / (12.0 * dm))
    r = simulate(s0, 0.0, -v_in, 0.0, 1, keep=True, h=s0.T / 40000)
    a = r['aufsetzer'][0]
    D = 0.0
    for (_, e, kon, fn) in r['stuecke']:
        if kon:
            ed = np.linspace(0.0, e, 201)
            mid, hw = 0.5 * (ed[1:] + ed[:-1]), 0.5 * (ed[1:] - ed[:-1])
            D += (hw[:, None] * GL_W).ravel() @ s0.daempfung(*fn((mid[:, None] + hw[:, None] * GL_X).ravel()))
    U = sy.K * max(-a[4], 0.0) ** (n + 1) / (n + 1)
    return dict(e=a[3] / v_in, F_spitze=a[5], t_kontakt=a[2] - a[0], dE=0.5 * sy.M * (v_in**2 - a[3]**2),
                D=D, U=U)


def abtasten(sy, r, t):
    """Zustand x, ẋ und Kontaktkraft N an beliebigen Zeiten t im Lauf (simulate(..., keep=True))."""
    t = np.atleast_1d(np.asarray(t, float))
    out = np.full((3, t.size), np.nan)
    for (ta, e, kon, fn) in r['stuecke']:
        sel = (t >= ta) & (t < ta + e)
        if sel.any():
            out[0, sel], out[1, sel] = fn(t[sel] - ta)
            out[2, sel] = sy.kraft(out[0, sel], out[1, sel]) if kon else 0.0
    return out


# ── Kommandos ────────────────────────────────────────────────────────────────
def referenz(phi2=120.0, phi3=240.0, **kw):
    return System(phis=(0.0, phi2, phi3), **kw)


def kandidat(phi2=0.0, phi3=0.0, zeta=0.05, K_c=1.5e6, **kw):
    """V1-Kandidat: 3×100 g Module (μ = 0,4615), Restmasse 0,35 kg, Hub 8 mm, 10 Hz, K = 1,5e6 N/m."""
    return System(phis=(0.0, phi2, phi3), m_mod=0.1, m0=0.35, hub=8e-3, f=10.0, K=K_c,
                  C=c_aus_zeta(zeta, K_c, 0.65), **kw)


def _system(a):
    """System aus den Optionen; --zeta setzt C = 2ζ√(K·M), sonst bleibt C fest. Rückgabe gewähltes Gesetz
    (das Hunt-Crossley-Gegenstück nur bei --law hc|beide), Kelvin-Voigt-System und dessen ζ."""
    phis = a.point if a.point else ((0.0, 0.0) if a.candidate else (120.0, 240.0))
    base = kandidat(*phis) if a.candidate else referenz(*phis)
    K_c = a.K if a.K is not None else base.K
    C_c = a.C if a.C is not None else (c_aus_zeta(a.zeta, K_c, base.M) if a.zeta is not None else base.C)
    kw = dict(K=K_c, C=C_c, profil='sinus' if a.sinus else 'egg')
    kw.update({k: v for k, v in (('f', a.f), ('hub', a.hub)) if v is not None})
    sy = base.mit(**kw)
    zeta = C_c / (2 * math.sqrt(K_c * sy.M))
    if a.law == 'kv':
        return [sy], sy, zeta
    hc = hc_aequivalent(sy, zeta, a.hc_n, a.hc_vref)
    return ([hc] if a.law == 'hc' else [sy, hc]), sy, zeta


def _zeile(k):
    return (f'⟨N⟩ − Mg = {1e3 * k["dF"]:+.4f} mN (R = {1e3 * k["R"]:+.4f} mN, Rest {k["rest"]:+.1e} N), '
            f'λ = {k["liftoff"]:.4f} %, Schiefe {k["F_skew"]:.5f}, F_min {k["F_min"]:.6f} N, '
            f'F_max {k["F_max"]:.4f} N, Aufsetzer/Periode {k["aufsetzer_je_periode"]:.2f}')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--point', nargs=2, type=float, metavar=('PHI2', 'PHI3'),
                    help='Phasen [°]; ohne --orbit/--einzug: Langlauf mit Kenngrößen')
    ap.add_argument('--orbit', action='store_true', help='Newton-Schießverfahren und Floquet-Multiplikatoren')
    ap.add_argument('--einzug', action='store_true', help='kritischer Wurf über die Wurfphasen')
    ap.add_argument('--stoss', type=float, metavar='V', help='Einzelstoß mit Aufprallgeschwindigkeit V [m/s]')
    ap.add_argument('--candidate', action='store_true', help='V1-Kandidat 3×100 g, 8 mm, 10 Hz, K = 1,5e6, ζ = 0,05')
    ap.add_argument('--law', choices=('kv', 'hc', 'beide'), default='kv', help='Kontaktgesetz (beide: Vergleich)')
    ap.add_argument('--hc-n', type=float, default=1.5)
    ap.add_argument('--hc-vref', type=float, default=0.5, help='Abgleich der Stoßzahl bei dieser Geschwindigkeit')
    ap.add_argument('--K', type=float)
    ap.add_argument('--C', type=float)
    ap.add_argument('--zeta', type=float, help='setzt C = 2ζ·√(K·M)')
    ap.add_argument('--f', type=float)
    ap.add_argument('--hub', type=float, help='Hub Spitze-Spitze [m]')
    ap.add_argument('--sinus', action='store_true')
    ap.add_argument('--start', choices=('std', 'imp', 'orbit'),
                    help='Startzustand (Langlauf: std = statische Ruhelage wie die Engine; Einzug: orbit)')
    ap.add_argument('--rampe', type=float, default=0.0, help='Anlauf mit Frequenzrampe T_r [s]')
    ap.add_argument('--t-sim', type=float, help='Laufzeit [s] (Langlauf 15, Einzug 16 bzw. 6 bei hc)')
    ap.add_argument('--t-eval', type=float,
                    help='Auswertefenster am Laufende [s] (Langlauf min(10, 2/3·t_sim), Einzug min(4 bzw. 1, t_sim/4))')
    ap.add_argument('--wurfphase', type=float, nargs='+', default=[0.0, 0.25, 0.5, 0.75], help='t₀/T')
    ap.add_argument('--dv', type=float, default=0.02, help='Raster der Wurfgeschwindigkeit [m/s]')
    ap.add_argument('--vmin', type=float, help='kleinster Wurf (Standard: --dv)')
    ap.add_argument('--vmax', type=float, default=0.6)
    a = ap.parse_args()
    for name, val, null_ok in (('--K', a.K, False), ('--f', a.f, False), ('--t-sim', a.t_sim, False),
                               ('--t-eval', a.t_eval, False), ('--dv', a.dv, False), ('--stoss', a.stoss, False),
                               ('--hc-n', a.hc_n, False), ('--hc-vref', a.hc_vref, False), ('--C', a.C, True),
                               ('--zeta', a.zeta, True), ('--hub', a.hub, True), ('--rampe', a.rampe, True),
                               ('--vmin', a.vmin, True)):
        if val is not None and not (val >= 0 if null_ok else val > 0):
            ap.error(f'{name} muss {"nichtnegativ" if null_ok else "positiv"} sein')
    if a.t_sim is not None and a.t_eval is not None and a.t_eval > a.t_sim:
        ap.error('--t-eval darf nicht größer als --t-sim sein')
    if a.einzug and (a.dv if a.vmin is None else a.vmin) > a.vmax:
        ap.error('leeres Wurfraster: --vmin (Standard --dv) größer als --vmax')
    if not (a.point or a.orbit or a.einzug or a.stoss is not None or a.rampe):
        ap.print_help()
        return
    try:
        systeme, sy_kv, zeta = _system(a)
        if a.stoss is not None:
            _kopf(sy_kv, zeta)
            for name, s_ in (('Kelvin-Voigt', sy_kv),
                             ('Hunt-Crossley', hc_aequivalent(sy_kv, zeta, a.hc_n, a.hc_vref))):
                o = stoss(s_, a.stoss)
                print(f'{name:14s} v = {a.stoss:g} m/s: e = {o["e"]:.5f}, Stoßspitze {o["F_spitze"]:.2f} N, '
                      f'Kontakt {1e3 * o["t_kontakt"]:.3f} ms, ΔE = {o["dE"]:.6f} J = D {o["D"]:.6f} + '
                      f'U {o["U"]:.6f} J')
            e_frei = f'{math.exp(-math.pi * zeta / math.sqrt(1 - zeta**2)):.5f}' if zeta < 1 else '0 (überkritisch)'
            print(f'Stoßzahl Kelvin-Voigt: ungeklippt exp(−πζ/√(1−ζ²)) = {e_frei}, '
                  f'geklippt (Engine) {e_kv_geklippt(zeta):.5f}')
        for sy in (systeme if (a.point or a.orbit or a.einzug or a.rampe) else []):
            _kopf(sy, zeta)
            _ausgabe(a, sy)
    except ValueError as err:                       # Fehleingaben und Punkte ohne Kontaktast: einzeilig melden
        ap.exit(2, f'{ap.prog}: Fehler: {err}\n')


def _kopf(sy, zeta):
    print(f'M = {sy.M:.4f} kg, Phasen {sy.phis.tolist()}°, f = {sy.f:g} Hz, Hub {1e3 * sy.hub[0]:.4f} mm, '
          + (f'Kelvin-Voigt K = {sy.K:.4g} N/m, C = {sy.C:.4g} N·s/m (ζ = {zeta:.4f})' if sy.gesetz == 'kv' else
             f'Hunt-Crossley n = {sy.n:g}, K_h = {sy.K:.4g} N/m^n, α = {sy.alpha:.4g} s/m (Abgleich ζ = {zeta:.4f})'))


def _ausgabe(a, sy):
    t_sim, start = a.t_sim or 15.0, a.start or 'std'
    t_eval = a.t_eval or min(10.0, t_sim * 2 / 3)
    n_per, n_eval = int(round(t_sim / sy.T)), int(round(t_eval / sy.T))
    if not 1 <= n_eval <= n_per:
        raise ValueError(f'Auswertefenster {t_eval:g} s passt nicht in die Laufzeit {t_sim:g} s (T = {sy.T:g} s)')
    if a.point and not (a.orbit or a.einzug) or a.rampe:
        z = startzustand(sy, start) if not a.rampe else (sy.ruhelage(), 0.0)
        r = simulate(sy, z[0], z[1], 0.0, n_per, rampe=a.rampe)
        (p, ts), (pl, tl) = periode(r), periode(r, tol_v=1e-3, tol_x=1e-4)
        print(f'Langlauf {t_sim:g} s ({"Rampe %g s" % a.rampe if a.rampe else "Start " + start}), Fenster der '
              f'letzten {n_eval * sy.T:g} s: {periodenname(p)}, eingeschwungen ab {ts:.2f} s (streng), {tl:.2f} s '
              f'(lose, {periodenname(pl)})')
        k = kenngroessen(r, n_per - n_eval, n_per)
        print('  exakt   ' + _zeile(k))
        print(f'  Raster  ⟨N⟩ = {k["F_mean_s"]:.6f} N, λ = {k["liftoff_s"]:.4f} %, Schiefe {k["F_skew_s"]:.6f}, '
              f'F_min {k["F_min_s"]:.6f} N, F_max {k["F_max_s"]:.6f} N (Δt = T/{N_STICH} wie die Engine)')
    if a.orbit:
        if sy.gesetz == 'kv' and math.isfinite(sy.wd):
            zs, mu, ok = kontaktorbit(sy)
            k = kenngroessen(simulate(sy, *zs, 0.0, 1))
            print(f'Kontaktast: {"existiert" if ok else "existiert nicht (hebt ab)"}; z* = ({zs[0]:.9e} m, '
                  f'{zs[1]:.9e} m/s), |μ| = {abs(mu[0]):.4f}'
                  + (f'; F_min {k["F_min"]:.6f} N, F_max {k["F_max"]:.4f} N, Schiefe {k["F_skew"]:.5f}' if ok else ''))
        z = startzustand(sy, start)
        r = simulate(sy, z[0], z[1], 0.0, n_per)
        p = max(periode(r, tol_v=1e-6, tol_x=1e-8)[0], 1)
        o = newton(sy, (r['PX'][-1], r['PV'][-1]), n_per * sy.T, p)
        k = kenngroessen(simulate(sy, *o['z'], n_per * sy.T, p))
        print(f'Zustand nach {t_sim:g} s (Start {start}): Newton auf P{p}, Residuen '
              + ' '.join(f'{x:.0e}' for x in o['res']) + f'; |μ| = {abs(o["mu"][0]):.4f}, {abs(o["mu"][1]):.4f} → '
              f'{"stabil" if np.all(np.abs(o["mu"]) < 1) else "instabil"}')
        print('  Orbit   ' + _zeile(k))
    if a.einzug:
        kv = sy.gesetz == 'kv'
        t_e = a.t_sim or (16.0 if kv else 6.0)
        n_e, n_w = int(round(t_e / sy.T)), int(round((a.t_eval or min(4.0 if kv else 1.0, t_e / 4)) / sy.T))
        if not 1 <= n_w <= n_e:
            raise ValueError(f'Auswertefenster passt nicht in die Laufzeit {t_e:g} s je Wurf (T = {sy.T:g} s)')
        v_lo, st = a.dv if a.vmin is None else a.vmin, a.start or 'orbit'
        print(f'Einzugsprüfung: Start {"auf dem Kontaktast" if st == "orbit" else st} zur Wurfphase t₀, Wurf Δv = '
              f'{v_lo:g} … {a.vmax:g} m/s (Raster {a.dv:g}, dann 3 Bisektionen), {n_e * sy.T:g} s je Lauf, '
              f'Auswertung der letzten {n_w * sy.T:g} s')
        for th in a.wurfphase:
            o = kritischer_wurf(sy, th * sy.T, np.round(np.arange(v_lo, a.vmax + 1e-9, a.dv), 6), bisekt=3,
                                start=st, n_per=n_e, n_eval=n_w)
            if o['start_huepft']:
                print(f'  t₀/T = {th:.2f}: schon der Startzustand ohne Wurf hüpft '
                      f'(λ = {o["laeufe"][0]["liftoff"]:.3f} %) – keine kritische Wurfgeschwindigkeit')
                continue
            if o['v_krit'] is None:
                print(f'  t₀/T = {th:.2f}: Rückkehr bis {o["v_rueck"]:.4f} m/s (kein Hüpfen im Raster)')
                continue
            w = [x for x in o['laeufe'] if x['zustand'] == 'Hüpfen'][-1]
            print(f'  t₀/T = {th:.2f}: Rückkehr bis {o["v_rueck"]:.4f} m/s, Hüpfen ab {o["v_krit"]:.4f} m/s '
                  f'(Stoßimpuls {o["impuls_krit"]:.4f} N·s, Fallhöhe {1e3 * o["v_krit"]**2 / (2 * sy.g):.1f} mm): '
                  f'λ = {w["liftoff"]:.3f} %, {periodenname(w["periode"])}, Stoßspitze {w["stoss_spitze"]:.2f} N '
                  f'(größte im Lauf {w["stoss_spitze_max"]:.2f} N)')


if __name__ == '__main__':
    main()
