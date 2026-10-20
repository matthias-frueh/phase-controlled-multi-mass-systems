"""E3-Grenzen des Regelstands 2026-11 auf Statistikebene (e3_grenzen, Option B der Entscheidungsvorlage vom 19.10.2026,
Abschnitt 4): Größe am Rand und Fehlerrate von „unauffällig“ durch deterministische Quadratur, nicht durch Kampagnen.

Modell der Prüfung (Annahmen der Konstruktion): E3a x̂ = θ + u·Z, ũ = u·V mit V² = w + (1 − w)·χ²_ν/ν unabhängig
(w: bekannter Varianzanteil); E3b d̂ = D + ε, ε ~ N₂(0, Σ), Σ = diag(1, ρ²) (λ_max(Σ) = 1, große Achse Re),
Σ̂ = W/ν mit W ~ Wishart(ν, Σ) nach Bartlett, unabhängig von ε; wahrer Wert am Rand |D| = t = q_tol/s, Richtung θ.
Gerechnet wird E über ũ bzw. Σ̂ von P_ε(Regel spricht) – Gauß-Legendre im Logarithmus der χ²-Variablen, Gauß-Hermite
für die Normalvariable der Bartlett-Zerlegung, die anisotrope Gaußwahrscheinlichkeit außerhalb eines Kreises als
Integral über ψ. Die Regeln selbst kommen aus dem Code (e3_grenzen.e3a_faktor, e3b_kritisch). Selten Ereignisse
werden nicht mit Kampagnen „bestätigt“; Vergleichswerte der Vorlage dienen als unabhängige Grenzfälle.
"""
import math

import numpy as np
import pytest
from scipy import special, stats

from pcmms_auswertung import e3_grenzen as eg

A_M = 0.05 / 43


# ── Quadraturhilfen (unabhängig vom Code) ─────────────────────────────────────────────────────────────
def _chi2_knoten(nu, n):
    """Knoten und Gewichte für E[f(X)], X ~ χ²_ν: Gauß-Legendre in log X über [F⁻¹(10⁻¹⁶), F̄⁻¹(10⁻¹⁶)]."""
    lo, hi = math.log(stats.chi2.ppf(1e-16, nu)), math.log(stats.chi2.isf(1e-16, nu))
    x, w = np.polynomial.legendre.leggauss(n)
    y, w = 0.5 * (hi - lo) * x + 0.5 * (hi + lo), 0.5 * (hi - lo) * w
    X = np.exp(y)
    return X, w * stats.chi2.pdf(X, nu) * X


def _wishart_lmax(nu, rho, na=48, nb=40, nz=24):
    """λ_max(Σ̂) mit Gewichten: Σ̂ = W/ν, W = S^½·L·Lᵀ·S^½, L = [[a, 0], [z, b]], a² ~ χ²_ν, b² ~ χ²_{ν−1},
    z ~ N(0, 1)."""
    a2, wa = _chi2_knoten(nu, na)
    b2, wb = _chi2_knoten(nu - 1, nb)
    z, wz = np.polynomial.hermite_e.hermegauss(nz)
    wz = wz / math.sqrt(2 * math.pi)
    A, Bq, Z = np.meshgrid(a2, b2, z, indexing='ij')
    w11, w21, w22 = A, rho * np.sqrt(A) * Z, rho ** 2 * (Z ** 2 + Bq)
    tr, det = w11 + w22, w11 * w22 - w21 ** 2
    lmax = (tr / 2 + np.sqrt(np.maximum(tr * tr / 4 - det, 0.0))) / nu
    return lmax.ravel(), (wa[:, None, None] * wb[None, :, None] * wz[None, None, :]).ravel()


def _wishart_spur_halbe(nu, rho, na=48, nb=40, nz=24):
    """Spur(Σ̂)/2 an denselben Knoten wie _wishart_lmax (Gegenprobe mit isotroper Ersatzstreuung)."""
    a2, wa = _chi2_knoten(nu, na)
    b2, wb = _chi2_knoten(nu - 1, nb)
    z, wz = np.polynomial.hermite_e.hermegauss(nz)
    A, Bq, Z = np.meshgrid(a2, b2, z, indexing='ij')
    sp = (A + rho ** 2 * (Z ** 2 + Bq)) / nu / 2
    return sp.ravel(), (wa[:, None, None] * wb[None, :, None] * wz[None, None, :] / math.sqrt(2 * math.pi)).ravel()


def _psi(n=2048, stuecke=32):
    xg, wg = np.polynomial.legendre.leggauss(n // stuecke)
    k = np.linspace(-np.pi / 2, np.pi / 2, stuecke + 1)
    return (np.concatenate([(a + b) / 2 + (b - a) / 2 * xg for a, b in zip(k[:-1], k[1:])]),
            np.concatenate([(b - a) / 2 * wg for a, b in zip(k[:-1], k[1:])]))


PSI, WPSI = _psi()


def _p_kreis(c, mu_u, mu_v, rho):
    """(P(|Z| ≤ c), P(|Z| > c)) für Z = U + iV, U ~ N(μ_u, 1), V ~ N(μ_v, ρ²); u = c·sin ψ, Streifen |u| ≤ c."""
    c = np.asarray(c, float)[:, None]
    u, h = c * np.sin(PSI)[None], c * np.cos(PSI)[None]
    dens = stats.norm.pdf(u - mu_u) * h
    a, b = (h - mu_v) / rho, (-h - mu_v) / rho
    innen = (dens * (special.ndtr(a) - special.ndtr(b))) @ WPSI
    streifen = (dens * (special.ndtr(-a) + special.ndtr(b))) @ WPSI
    c1 = c[:, 0]
    return innen, special.ndtr(-(c1 - mu_u)) + special.ndtr(-(c1 + mu_u)) + streifen


def _interp_log(x, xg, yg):
    return np.exp(np.interp(np.log(x), np.log(xg), np.log(yg)))


def _groesse_b(nu, rho, t, theta_grad, kn, kritisch=None):
    """Größe von „auffällig“ in Vielfachen von α/m am Rand |D| = t (λ_max(Σ) = 1)."""
    kritisch = kritisch or (lambda s: eg.e3b_kritisch(s, nu, t, A_M))
    lmax, W = kn
    s = np.sqrt(lmax)
    sg = np.geomspace(s.min(), s.max(), 240)
    c = _interp_log(s, sg, np.array([kritisch(x) for x in sg]))
    cg = np.linspace(c.min(), c.max(), 500)
    th = math.radians(theta_grad)
    _, pa = _p_kreis(cg, t * math.cos(th), t * math.sin(th), rho)
    p = np.exp(np.interp(c, cg, np.log(np.maximum(pa, 1e-300))))
    return float(p @ W) / A_M


def _fehler_unauffaellig_b(nu, rho, t, theta_grad, kn, delta=0.0):
    """P(q + t(0,95; ν)·ŝ ≤ q_tol) bei |D| = q_tol·(1 + δ), q_tol = t."""
    lmax, W = kn
    c = t - stats.t.isf(0.05, nu) * np.sqrt(lmax)
    pos = c > 0
    if not pos.any():
        return 0.0
    cg = np.linspace(c[pos].min(), c[pos].max(), 500)
    th = math.radians(theta_grad)
    pin, _ = _p_kreis(cg, t * (1 + delta) * math.cos(th), t * (1 + delta) * math.sin(th), rho)
    return float(np.where(pos, np.interp(c, cg, pin), 0.0) @ W)


def _k_tabelle(nu):
    tg = np.r_[0.0, np.geomspace(1e-4, 1e3, 300)]
    return tg, np.array([eg.e3a_faktor(nu, x, A_M) for x in tg])


def _groesse_a(nu, tau, tab, w=0.0, gegenseite=True):
    """Größe der gefalteten E3a-Regel |x̂| > s + k(s/ũ)·ũ in Vielfachen von α/m bei θ = s, τ = s/u."""
    X, W = _chi2_knoten(nu, 400)
    V = np.sqrt(w + (1 - w) * X / nu)
    tg, kg = tab
    if gegenseite:
        k = np.where(tau / V > tg[-1], kg[-1], np.interp(tau / V, tg, kg))
    else:
        k = np.full_like(V, stats.t.isf(A_M, nu))            # einseitig, Gegenseite ignoriert
    return float((special.ndtr(-k * V) + special.ndtr(-2 * tau - k * V)) @ W) / A_M


# ── Hilfsmittel gegen geschlossene Formeln ────────────────────────────────────────────────────────────
def test_quadraturhilfen_gegen_geschlossene_formeln():
    """Kreiswahrscheinlichkeit isotrop gleich der Rice-Verteilung, innen + außen = 1 auch stark anisotrop;
    χ²-Knoten reproduzieren Masse und Mittel; Wishart-Knoten E[Spur Σ̂] = 1 + ρ² und E[Σ̂₁₁²] = 1 + 2/ν."""
    c = np.array([0.3, 2.0, 3.676, 6.0, 9.0])
    for t in (0.0, 1.5, 6.0):
        _, pa = _p_kreis(c, t, 0.0, 1.0)
        ex = np.exp(-c * c / 2) if t == 0 else stats.ncx2.sf(c * c, 2, t * t)
        assert np.max(np.abs(pa / ex - 1)) < 1e-7
    for rho in (0.5, 0.03):
        inn, pa = _p_kreis(c, 1.2, -0.7, rho)
        assert np.max(np.abs(inn + pa - 1)) < 1e-12
    for nu in (4, 19):
        X, W = _chi2_knoten(nu, 400)
        assert W.sum() == pytest.approx(1, abs=1e-12) and X @ W == pytest.approx(nu, rel=1e-12)
    lmax, W = _wishart_lmax(5, 0.3)                                   # Testknoten (48 · 40 · 24): Fehler ~10⁻⁷
    assert W.sum() == pytest.approx(1, abs=1e-6)
    sp, _ = _wishart_spur_halbe(5, 0.3)
    assert 2 * sp @ W == pytest.approx(1 + 0.3 ** 2, rel=1e-6)
    a2, wa = _chi2_knoten(5, 48)
    assert (a2 / 5) ** 2 @ wa == pytest.approx(1 + 2 / 5, rel=1e-6)
    assert (lmax >= 0).all() and lmax @ W > 1.0                        # E λ_max(Σ̂) > λ_max(Σ) = 1


# ── E3a: gefaltete t-Grenze ───────────────────────────────────────────────────────────────────────────
def test_e3a_faktor_grenzen_und_monotonie():
    """k(τ) fällt von t(1 − α/(2m); ν) (τ = 0, Gegenseite voll) auf t(1 − α/m; ν) (τ → ∞) und löst die
    Faltungsgleichung."""
    for nu in (5, 21):
        k = [eg.e3a_faktor(nu, x, A_M) for x in (0.0, 0.1, 0.5, 2.0, 1e4, math.inf)]
        assert k[0] == pytest.approx(stats.t.isf(A_M / 2, nu), rel=1e-10)
        assert k[-1] == pytest.approx(stats.t.isf(A_M, nu), rel=1e-12) and k[-2] == pytest.approx(k[-1], rel=1e-9)
        assert all(a >= b for a, b in zip(k, k[1:]))
        assert stats.t.sf(k[2], nu) + stats.t.sf(k[2] + 1.0, nu) == pytest.approx(A_M, rel=1e-9)
    with pytest.raises(ValueError):
        eg.e3a_faktor(10, -0.1, A_M)


@pytest.mark.parametrize('nu', [5, 6, 10, 21, 60])
def test_e3a_groesse_am_rand_hoechstens_alpha_m(nu):
    """Gefalteter Betrag: Größe am Rand ≤ α/m über τ = s/u ∈ {0} ∪ [10⁻³, 200], auch an nu_min = 5; in beiden
    Grenzen genau α/m (τ = 0 Vereinigungsschranke, τ → ∞ einseitiger t-Test); mit bekanntem Varianzanteil (w = 0,7)
    kleiner. Ohne Gegenseite (einseitiges t-Quantil auf |x̂|) wären es bei τ → 0 2·α/m."""
    tab = _k_tabelle(nu)
    taus = np.r_[0.0, np.geomspace(1e-3, 200, 36)]
    g = np.array([_groesse_a(nu, x, tab) for x in taus])
    assert g.max() <= 1 + 1e-9
    assert g[0] == pytest.approx(1, abs=1e-9) and g[-1] == pytest.approx(1, abs=1e-9)
    assert g.min() < 0.995                                             # dazwischen echt kleiner
    assert max(_groesse_a(nu, x, tab, w=0.7) for x in taus[::4]) <= 1 + 1e-9
    assert _groesse_a(nu, 0.0, tab, gegenseite=False) == pytest.approx(2, abs=1e-6)
    assert _groesse_a(nu, 0.5, tab, gegenseite=False) > 1.01


def test_e3a_unauffaellig_fehler_hoechstens_005():
    """„Unauffällig“ |x̂| + t(0,95; ν)·ũ ≤ s bei wahrem |θ| = s·(1 + δ): Fehlerrate ≤ 0,05 (Projektion), auch bei
    nu_min."""
    for nu in (5, 21):
        X, W = _chi2_knoten(nu, 400)
        V = np.sqrt(X / nu)
        t95 = stats.t.isf(0.05, nu)
        for tau in np.geomspace(0.05, 100, 25):
            for d in (0.0, 0.02, 0.1):
                hi = tau - t95 * V
                p = np.where(hi > 0, special.ndtr(hi - tau * (1 + d)) - special.ndtr(-hi - tau * (1 + d)), 0.0) @ W
                assert p <= 0.05 + 1e-12


# ── E3b: κ·ŝ·Rice⁻¹ mit λ_max ─────────────────────────────────────────────────────────────────────────
def test_nu_eff_kappa_und_rice_quantil():
    assert eg.nu_eff(19, 10000) == 19 and eg.nu_eff(19, 200) == pytest.approx(1 / (1 / 19 + 1 / 199), rel=1e-14)
    assert eg.e3b_kappa(19, A_M) == pytest.approx(stats.t.isf(A_M, 19) / stats.norm.isf(A_M), rel=1e-14)
    assert eg.e3b_kappa(5, A_M) > eg.e3b_kappa(19, A_M) > eg.e3b_kappa(1e6, A_M) > 0.9999
    for b in (0.0, 0.7, 4.0, 300.0, 9e3):
        q = eg.rice_quantil(A_M, b)
        assert stats.ncx2.sf(q * q, 2, b * b) / A_M == pytest.approx(1, rel=1e-7)
    z = stats.norm.isf(A_M)
    for b in (1.0001e4, 5e4):                                          # Näherung oberhalb des Quantils (SciPy ≤ 10⁵)
        q = eg.rice_quantil(A_M, b)
        assert q == b + z + 1 / b and q > stats.rice.isf(A_M, b) > b + z + 0.4 / b
    assert np.isfinite(eg.rice_quantil(A_M, 1e9))


def test_e3b_vergleichswerte_der_vorlage_und_gegenproben():
    """Unabhängige Vergleichswerte der Nachprüfung (Hauptbearbeiter: 0,908 und 0,146·α/m; Monte Carlo über Σ̂,
    2 SE ≈ 0,012 bzw. 0,001) und Gegenproben: ohne n/(n − 1) und κ (eingesetztes ŝ, Regel c-2) bzw. mit √(Spur/2) statt
    λ_max hält die Regel die Größe nicht – eine eingesetzte Rice-Verteilung ist bei geschätzter, anisotroper Streuung
    keine exakte Grenze."""
    kn = _wishart_lmax(10, 0.1)
    assert _groesse_b(10, 0.1, 10.0, 0, kn) == pytest.approx(0.908, abs=0.015)
    assert _groesse_b(19, 1.0, 1.5, 0, _wishart_lmax(19, 1.0)) == pytest.approx(0.146, abs=0.005)
    rf = math.sqrt(10 / 11)                                            # (n − 1)/n: Bootstrap-Kovarianz eingesetzt

    def c_2(s):                                                        # ŝ·Rice⁻¹(1 − α/m; q_tol/ŝ) ohne κ
        return s * rf * eg.rice_quantil(A_M, 10.0 / (s * rf))
    assert _groesse_b(10, 0.1, 10.0, 0, kn, kritisch=c_2) > 5           # Vorlage: 6,4·α/m
    assert _groesse_b(10, 0.1, 10.0, 0, _wishart_spur_halbe(10, 0.1)) > 5  # √(Spur/2) mit κ; Vorlage: 6,5·α/m


@pytest.mark.parametrize('nu', [5, 19])
def test_e3b_groesse_am_rand_anisotropie_richtung_kleine_nu(nu):
    """Größe von „auffällig“ ≤ α/m über ρ ∈ {1; 0,25; 0,03}, t ∈ {0,25; 1,5; 10; 40} und θ ∈ {0°, 30°, 90°},
    einschließlich nu_min = 5 (unterhalb des Rasters der Nachprüfung, das bei ν = 10 begann)."""
    best = 0.0
    for rho in (1.0, 0.25, 0.03):
        kn = _wishart_lmax(nu, rho)
        for t in (0.25, 1.5, 10.0, 40.0):
            for th in ((0,) if rho == 1.0 else (0, 30, 90)):
                g = _groesse_b(nu, rho, t, th, kn)
                assert g < 1.0, (nu, rho, t, th, g)
                best = max(best, g)
    assert best > 0.9                                                  # der Rand wird erreicht, nicht verfehlt


def test_e3b_grenzfall_einseitiger_t_test_und_unauffaellig():
    """ρ → 0, t → ∞ mit D auf der großen Achse: B wird zum einseitigen t-Test, Größe → α/m (von unten); auf der
    kleinen Achse verschwindet sie. „Unauffällig“ q_Z + t(0,95; ν)·ŝ ≤ q_tol: Fehlerrate ≤ 0,05 am Rand und darüber
    (Projektionsungleichung), auch bei ν = 5 und starker Anisotropie."""
    kn = _wishart_lmax(5, 1e-3)
    g0 = _groesse_b(5, 1e-3, 1000.0, 0, kn)
    assert 0.98 < g0 < 1.0
    assert _groesse_b(5, 1e-3, 1000.0, 90, kn) < 1e-6
    for rho in (1.0, 0.1):
        knr = _wishart_lmax(5, rho)
        for t in (1.5, 10.0):
            for th in (0, 90):
                for d in (0.0, 0.05):
                    assert _fehler_unauffaellig_b(5, rho, t, th, knr, d) <= 0.05 + 1e-9
    # Grenze bei großem t: Fehlerrate am Rand → 0,05 (die Schranke wird ausgeschöpft, nicht verschenkt)
    assert _fehler_unauffaellig_b(5, 1e-3, 1000.0, 0, kn) == pytest.approx(0.05, abs=2e-3)
