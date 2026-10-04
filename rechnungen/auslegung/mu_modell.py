"""
mu_modell.py – eigene, vom Repo-Code unabhängige Implementierung (P2, Prüfgruppe "auslegung").

Modell (Herleitung im PROTOKOLL.md, Befund AUS-02):
  Körper (Gehäuse) mit Restmasse m0, drei Module m_j mit vorgegebener Relativlage z_j(t) = z(t − τ_j),
  τ_j = φ_j/(2πf) (positive Phase verzögert), Gesamtmasse M = m0 + Σ m_j, Körperkoordinate x
  (x < 0: Kontakt eingefedert), einseitiger Kelvin-Voigt-Kontakt N = max(0, −K·x − C·ẋ) für x < 0.
  Impulssatz:  M·ẍ = −M·g + N − Σ_j m_j·z̈_j(t)
  Bei gleichen Modulen m_j = μ·M/3 (μ = bewegter Massenanteil) und Lauf-Gewichten w_j ∈ {0, 1}
  (w_j = 0: Modul geparkt) gilt:  M·ẍ = −M·g + N − (μ·M/3)·Σ_j w_j·a(t − τ_j).
  Die Referenz-Engine ist der Fall μ = 1, w = (1, 1, 1).

Profil: geglättetes Egg-Profil der Engine, Halteanteil TH = 0,65, Hub (Spitze-Spitze) h = RTOP + RBOT,
  RTOP = TH·h, RBOT = TF·h (Referenz: h = 7,6923 mm, RTOP = 5 mm, RBOT = 2,6923 mm).
  Größte Abwärtsbeschleunigung (Haltephase): a_h = RTOP·(π/(TH·T))² = π²·h·f²/TH.

Dimensionslose Kennzahlen: ε = μ·a_h/g (Anregungsstärke), ρ = f/f_n, f_n = √(K/M)/(2π), ζ = C/(2√(K·M)).
  Im Dauerkontakt gilt N(t)/(M·g) = 1 + ε·g̃(t; φ, w, ρ, ζ, Profilform).

Alle Einheiten SI (m, s, kg, N); Phasen in Grad an den Schnittstellen, intern in rad.
"""
import numpy as np
from scipy.stats import skew as _skew

G = 9.81
TH = 0.65
TF = 1.0 - TH
M_REF = 0.650
F_REF = 10.0
RTOP_REF = 0.005
HUB_REF = RTOP_REF / TH            # 7,6923 mm Spitze-Spitze
K_REF, C_REF = 1.0e4, 16.0
ZETA_REF = C_REF / (2.0 * np.sqrt(K_REF * M_REF))   # 0,099228


# ─────────────────────────────── Kennzahlen ────────────────────────────────
def a_hold(hub, f):
    """Betrag der größten Abwärtsbeschleunigung des Profils (Haltephase) [m/s²]."""
    return np.pi**2 * hub * f**2 / TH


def a_fast(hub, f):
    """Größte Aufwärtsbeschleunigung (Rückholphase) [m/s²] = a_hold·TH/TF."""
    return np.pi**2 * hub * f**2 / TF


def eps_of(mu, hub, f):
    return mu * a_hold(hub, f) / G


def hub_of(eps, mu, f):
    return eps * G * TH / (mu * np.pi**2 * f**2)


def f_n(K, M=M_REF):
    return np.sqrt(K / M) / (2 * np.pi)


def K_of_rho(rho, f, M=M_REF):
    """K für gegebenes ρ = f/f_n."""
    return M * (2 * np.pi * f / rho) ** 2


def C_of_zeta(zeta, K, M=M_REF):
    return 2 * zeta * np.sqrt(K * M)


# ───────────────────────── Profil: analytische Fourierkoeffizienten ─────────
def _half(k, L):
    """∫_0^L sin(π s/L)·e^{−i2πks} ds (s = t/T), geschlossen; L·k ≠ 1/2 vorausgesetzt."""
    a = np.pi / L
    b = 2 * np.pi * k
    return (1 + np.exp(-1j * b * L)) * a / (a * a - b * b)


def profile_coeffs(nk, hub=HUB_REF, f=F_REF):
    """c_k, k = 0 … nk−1, mit a(t) = Σ_{k∈ℤ} c_k e^{ikωt} (c_{−k} = c_k*). Analytisch hergeleitet:
    Haltephase a = −A_h sin(π s/TH), s ∈ [0, TH); Rückholphase a = +A_f sin(π (s−TH)/TF)."""
    T = 1.0 / f
    rtop, rbot = TH * hub, TF * hub
    A_h = rtop * (np.pi / (TH * T)) ** 2
    A_f = rbot * (np.pi / (TF * T)) ** 2
    k = np.arange(nk)
    c = -A_h * _half(k, TH) + A_f * np.exp(-2j * np.pi * k * TH) * _half(k, TF)
    c[0] = 0.0          # Gleichanteil exakt null (RBOT = RTOP·TF/TH)
    return c


def egg_acc(t, hub=HUB_REF, f=F_REF):
    """Profilbeschleunigung im Zeitbereich (wie z_egg_zdd der Engine, mit Hub und f als Parameter)."""
    T = 1.0 / f
    rtop, rbot = TH * hub, TF * hub
    ph = np.mod(t, T) / T
    return np.where(ph < TH, -rtop * (np.pi / (TH * T)) ** 2 * np.sin(np.pi * ph / TH),
                    rbot * (np.pi / (TF * T)) ** 2 * np.sin(np.pi * (ph - TH) / TF))


# ─────────────────────────────── Lineares Modell ───────────────────────────
def transfer(K, C, f, nk, M=M_REF):
    """H(kω) (Kraft) und Y(kω) (Nachgiebigkeit) für k = 0 … nk−1; K = None: starr."""
    w = 2 * np.pi * f * np.arange(nk)
    if K is None:
        return np.ones(nk, complex), np.zeros(nk, complex)
    den = K - M * w**2 + 1j * w * C
    return (K + 1j * w * C) / den, -1.0 / den


def phase_factor(phis_deg, weights, nk):
    """Φ_k = Σ_j w_j e^{−ikφ_j} (FV-Konvention ohne 1/3)."""
    k = np.arange(nk)
    ph = np.radians(np.asarray(phis_deg, float))
    w = np.asarray(weights, float)
    return (w[None, :] * np.exp(-1j * np.outer(k, ph))).sum(1)


def linear_run(phis_deg, weights, mu, hub, f, K, C, M=M_REF, n=16000, nsamp=2000, k_max=None):
    """Stationäre lineare Lösung (Kontaktast). Rückgabe dict: N(θ) auf nsamp Stützstellen je Periode,
    F_min, F_max, mean, skew, x_max (Körperkoordinate), N_k (k = 1..4, Konvention Präreg §4:
    N_k = (2/Nθ)·Σ N(θ_n)·e^{−ikθ_n}), valid (F_min > 0 und x_max < 0).
    k_max: optionale Bandbegrenzung (nur Harmonische k ≤ k_max)."""
    nk = n // 2 + 1
    c = profile_coeffs(nk, hub, f)
    H, Y = transfer(K, C, f, nk, M)
    Phi = phase_factor(phis_deg, weights, nk)
    m_mod = mu * M / 3.0
    Fk = m_mod * H * c * Phi                    # komplexe Harmonische (zweiseitige Konvention)
    Xk = m_mod * Y * c * Phi
    if k_max is not None:
        Fk[k_max + 1:] = 0.0
        Xk[k_max + 1:] = 0.0
    # irfft erwartet die Koeffizienten der Form X_k = n·c_k
    N = M * G + np.fft.irfft(Fk * n, n)
    x = (-M * G / K if K is not None else 0.0) + np.fft.irfft(Xk * n, n)
    step = n // nsamp
    Ns, xs = N[::step], x[::step]
    out = dict(N=Ns, F_min=Ns.min(), F_max=Ns.max(), mean=Ns.mean(), skew=float(_skew(Ns)),
               x_max=(xs.max() if K is not None else -np.inf),
               Nk=np.array([2 * Fk[k] for k in range(1, 5)]))
    out['valid'] = (out['F_min'] > 0) and (out['x_max'] < 0)
    return out


# ─────────────────────────────── Lauftypen ─────────────────────────────────
SECTION_PHI2 = np.arange(100.0, 140.0 + 1e-9, 2.0)      # 21 Schnittpunkte bei φ₃ = 240°
PILOTS = [(110.0, 250.0), (130.0, 230.0), (110.0, 252.0)]


def run_types(pair_step=5.0):
    """Liste (Name, Gruppe, Phasen (φ1, φ2, φ3) [°], Gewichte w)."""
    L = [('Einzelmodul', 'einzel', (0, 0, 0), (1, 0, 0))]
    for d in np.arange(0.0, 360.0, pair_step):
        L.append((f'Paar Δ={d:g}°', 'paar', (0, d, 0), (1, 1, 0)))
    L.append(('synchron (0°,0°)', 'synchron', (0, 0, 0), (1, 1, 1)))
    L.append(('Zweiergruppe (0°,180°)', 'zweiergruppe', (0, 0, 180), (1, 1, 1)))
    for p2, p3 in PILOTS:
        L.append((f'Pilot ({p2:g}°,{p3:g}°)', 'pilot', (0, p2, p3), (1, 1, 1)))
    for p2 in SECTION_PHI2:
        L.append((f'Schnitt ({p2:g}°,240°)', 'schnitt', (0, p2, 240.0), (1, 1, 1)))
    return L


# ─────────────────────────────── RK4-μ-Engine ──────────────────────────────
def rk4_mu(phis_deg, weights, mu, hub, f, K, C, M=M_REF, t_sim=15.0, t_burn=5.0, n_per=2000,
           z0=None, v0=0.0, keep_series=False):
    """Zeitintegration wie Referenz-Engine (klassisches RK4, Kontaktkraft der ersten Stufe als
    Stichprobe, einseitiger Kelvin-Voigt-Kontakt, Standardstart z = −Mg/K, ż = 0 bei t = 0), aber mit μ,
    Hub, f, K, C, M und Laufgewichten. Δt = T/n_per (bei 10 Hz und n_per = 2000 genau 50 µs wie die
    Engine; bei anderen f ganzzahlig viele Schritte je Periode). Vektorisiert über Punkte:
    phis_deg (n,3), weights (n,3). Auswertung über ganze Perioden ab t_burn."""
    phis = np.atleast_2d(np.asarray(phis_deg, float))
    w = np.atleast_2d(np.asarray(weights, float))
    npt = phis.shape[0]
    T = 1.0 / f
    dt = T / n_per
    tau = np.radians(phis) / (2 * np.pi * f)               # (n,3)
    n_steps = int(round(t_sim / dt))
    n_burn = int(round(t_burn / dt))
    n_eval = ((n_steps - n_burn) // n_per) * n_per          # ganze Perioden
    n_burn = n_steps - n_eval
    rtop, rbot = TH * hub, TF * hub
    A_h = -rtop * (np.pi / (TH * T)) ** 2
    A_f = rbot * (np.pi / (TF * T)) ** 2
    fac = mu / 3.0

    def acc_mod(t):
        tt = t - tau                                        # (n,3)
        ph = np.mod(tt, T) / T
        a = np.where(ph < TH, A_h * np.sin(np.pi * ph / TH), A_f * np.sin(np.pi * (ph - TH) / TF))
        return fac * (w * a).sum(1)

    def rhs(z, zd, t):
        F = -K * z - C * zd
        Fc = np.where((z >= 0.0) | (F <= 0.0), 0.0, F)
        return zd, -G + Fc / M - acc_mod(t), Fc

    z = np.full(npt, -M * G / K) if z0 is None else np.broadcast_to(z0, (npt,)).astype(float).copy()
    zd = np.broadcast_to(v0, (npt,)).astype(float).copy()
    Fe = np.empty((n_eval, npt))
    for i in range(n_steps):
        t = i * dt
        k1z, k1d, Fc = rhs(z, zd, t)
        k2z, k2d, _ = rhs(z + 0.5 * dt * k1z, zd + 0.5 * dt * k1d, t + 0.5 * dt)
        k3z, k3d, _ = rhs(z + 0.5 * dt * k2z, zd + 0.5 * dt * k2d, t + 0.5 * dt)
        k4z, k4d, _ = rhs(z + dt * k3z, zd + dt * k3d, t + dt)
        z = z + dt * (k1z + 2 * k2z + 2 * k3z + k4z) / 6.0
        zd = zd + dt * (k1d + 2 * k2d + 2 * k3d + k4d) / 6.0
        if i >= n_burn:
            Fe[i - n_burn] = Fc
    # Mittelkurve über die Perioden (Fenster beginnt bei einem Vielfachen von T, weil n_burn = n_steps − n_eval
    # und n_steps ein Vielfaches von n_per ist, sofern t_sim ganzzahlig viele Perioden umfasst)
    ncyc = n_eval // n_per
    start_phase = (n_burn % n_per)
    mc = Fe.reshape(ncyc, n_per, npt).mean(0)               # (n_per, n)
    mc = np.roll(mc, start_phase, axis=0)                   # Stützstelle 0 ↔ θ = 0
    th = 2 * np.pi * np.arange(n_per) / n_per
    Nk = np.array([(2.0 / n_per) * (mc * np.exp(-1j * k * th)[:, None]).sum(0) for k in range(1, 5)])
    out = dict(liftoff=100.0 * (Fe < 1e-9).mean(0), F_min=Fe.min(0), F_max=Fe.max(0), mean=Fe.mean(0),
               skew=_skew(Fe, axis=0), Nk=Nk, mc_min=mc.min(0), mc_max=mc.max(0), dt=dt, ncyc=ncyc)
    if keep_series:
        out['series'] = Fe
    return out
