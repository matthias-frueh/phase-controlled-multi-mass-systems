# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 4.2 und 4.3.
# Zweck: Zusatzrechnungen Z1–Z7 zu Regel B (Grenzwert, kleine ν, zusammengesetzte Kovarianz, endliches B, schwere
#   Ränder, Macht, c-2-Obergrenze, E3a am Rand, Satterthwaite); siehe Modulbeschreibung.
# Eingaben: Argument 1 = Ausgabe (JSON), danach die Teile (z1 … z7). Importiert groesse_regel_b.py aus diesem Ordner.
# Seed: ein gemeinsamer Generator default_rng(20261019 + 5) für die Teile in Aufrufreihenfolge; z7 mit eigenem
#   default_rng(77). Die Ausgaben stammen aus drei getrennten Aufrufen (README); die Werte hängen von der Reihenfolge ab.
# Laufzeit: einige Minuten je Aufruf (Einschätzung; nicht neu gerechnet, nur Aufrufbarkeit mit kleinem N geprüft).
# Aufrufe: python3 -B zusatz_b.py zusatz_z1_z6.json z1 z2 z3 z5 z6 > zusatz_z1_z6.out;
#   python3 -B zusatz_b.py zusatz_z4.json z4 > zusatz_z4.out;  python3 -B zusatz_b.py zusatz_z7.json z7
# Herkunft: Nachprüfung 5. Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""Nachleseauftrag 5, Zusatzrechnungen auf Ebene der Teststatistik (eigene Implementierung):
 Z1  Grenzwert der Größe von Regel B für t → ∞, ρ → 0 (soll von unten gegen α/m gehen) und kleine ν (5, 7).
 Z2  Zusammengesetzte Kovarianz: Σ̂ = W_A/ν_A + Σ_j W_Bj/ν_B (Messung, drei Module der Vorhersage), Regel mit
     ν = min(ν_A, ν_B); verschiedene Anteile und Orientierungen.
 Z3  Endliche Bootstrap-Zahl B = 1000 (Σ̂_boot | Daten ≈ Wishart(B − 1, Σ̂_plug-in)/(B − 1)).
 Z4  Schwere Ränder der Einzelläufe (multivariat t mit 5 FG, Kontamination), n = 20 Läufe, direktes Monte Carlo.
 Z5  Macht von B und P(unauffällig | D = 0) für ν = 19 und 40; t* für O1.
 Z6  c-2-Obergrenze („unauffällig“ mit Rice-Quantil und eingesetztem ŝ): Fehlerrate am Rand.
 Z7  E3a: Größe am Rand für z-Regel, t-Regel (ν = n − 1, n/(n−1) auf Bootstrap-Anteil bzw. auf ganz u²),
     Satterthwaite mit geschätzten Gewichten; Faltungsterm bei kleinem Schwelle/u; obere Grenze.
"""
import importlib.util
import json
import math
import os
import sys

import numpy as np
from scipy import integrate, stats

_sp = importlib.util.spec_from_file_location('g', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'groesse_regel_b.py'))
g = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(g)
A1, ZQ = g.A1, g.ZQ
OUT = {}


def rice_q_breit(b):
    """Rice⁻¹(1 − α/m; b) auch für große b (exakt über scipy, auf Gitter bis 2000)."""
    b = np.asarray(b, float)
    out = np.empty_like(b)
    klein = b <= 80
    out[klein] = g.rice_q(b[klein])
    if (~klein).any():
        bg = np.linspace(80, max(2000.0, float(b.max()) + 1), 4000)
        out[~klein] = np.interp(b[~klein], bg, stats.rice.isf(A1, bg))
    return out


def regel_b_c(lmax, nu, t):
    kap = stats.t.isf(A1, nu) / ZQ
    s = np.sqrt(lmax)
    return kap * s * rice_q_breit(t / (kap * s))


def z1(rng, N=400_000):
    res = []
    for nu in (5, 7, 10, 19):
        for rho in (0.1, 0.03, 0.01):
            lmax, _ = g.lam_ziehen(nu, rho, N, rng)
            for t in ((1.5, 10.0, 30.0, 100.0, 300.0) if nu >= 10 else (0.25, 1.5, 3.0, 10.0, 100.0)):
                c = regel_b_c(lmax, nu, t)
                p, se = max(g.groesse(c, t, th, rho) for th in np.radians([0, 45, 90]))
                res.append(dict(nu=nu, rho=rho, t=t, faktor=round(p / A1, 4), se2=round(2 * se / A1, 4)))
    for nu in (5, 7):
        for rho in (1.0, 0.5):
            lmax, _ = g.lam_ziehen(nu, rho, N, rng)
            for t in (0.25, 1.5, 10.0):
                c = regel_b_c(lmax, nu, t)
                p, se = max(g.groesse(c, t, th, rho) for th in np.radians([0, 45, 90]))
                res.append(dict(nu=nu, rho=rho, t=t, faktor=round(p / A1, 4), se2=round(2 * se / A1, 4)))
    # Grenzfall ρ = 0, t → ∞: einseitiger t-Test mit ν FG, exakt α/m
    OUT['Z1'] = res
    print('Z1 Grenzwert/kleine ν:', json.dumps(res))


def wishart2(nu, S, N, rng):
    """N Ziehungen W/ν mit W ~ Wishart(ν, S) (S 2×2) als (N, 2, 2)."""
    L = np.linalg.cholesky(S)
    c1 = np.sqrt(rng.chisquare(nu, N))
    c2 = np.sqrt(rng.chisquare(nu - 1, N))
    z = rng.standard_normal(N)
    B = np.zeros((N, 2, 2))
    B[:, 0, 0], B[:, 1, 0], B[:, 1, 1] = c1, z, c2
    A = L[None] @ B
    return A @ np.swapaxes(A, 1, 2) / nu


def rot(phi):
    c, s = math.cos(phi), math.sin(phi)
    return np.array([[c, -s], [s, c]])


def groesse_allg(Sig, Sh, nu_regel, t, ths=(0, 30, 45, 60, 90, 120, 135, 150)):
    """Größe von B für allgemeines wahres Σ (2×2) und gezogene Σ̂ (N,2,2); max über Richtungen von D."""
    lam, V = np.linalg.eigh(Sig)
    s1 = math.sqrt(lam[1])                                  # große Achse
    rho = math.sqrt(lam[0] / lam[1])
    lmax = np.linalg.eigvalsh(Sh)[:, 1] / lam[1]            # normiert auf λ_max(Σ) = 1
    c = regel_b_c(lmax, nu_regel, t)
    best = (0.0, 0.0)
    for th in np.radians(ths):
        p = g.groesse(c, t, th, rho)
        best = max(best, p)
    return best


def z2(rng, N=300_000):
    res = []
    nuA, nuB = 22, 19
    faelle = {
        'A dominiert, anisotrop 0,1': [(0.9, 0.1, 0.0)] + [(0.1 / 3, 1.0, 0.0)] * 3,
        'B dominiert, ein Modul': [(0.1, 1.0, 0.0), (0.8, 0.1, 0.0), (0.05, 1.0, 0.0), (0.05, 1.0, 0.0)],
        'gleich verteilt, Achsen gedreht': [(0.25, 0.1, 0.0), (0.25, 0.1, math.pi / 2), (0.25, 0.1, math.pi / 4),
                                            (0.25, 0.1, -math.pi / 4)],
        'A und ein Modul gleich, gleiche Achse': [(0.5, 0.05, 0.0), (0.5, 0.05, 0.0), (1e-9, 1.0, 0.0), (1e-9, 1.0, 0.0)],
    }
    for name, teile in faelle.items():
        Sig = np.zeros((2, 2))
        Sh = np.zeros((N, 2, 2))
        for k, (w, rho, phi) in enumerate(teile):
            S = w * rot(phi) @ np.diag([1.0, rho ** 2]) @ rot(phi).T
            Sig += S
            Sh += wishart2(nuA if k == 0 else nuB, S + 1e-15 * np.eye(2), N, rng)
        for t in (0.5, 1.5, 3.0, 10.0):
            p, se = groesse_allg(Sig, Sh, min(nuA, nuB), t)
            res.append(dict(fall=name, t=t, faktor=round(p / A1, 4), se2=round(2 * se / A1, 4)))
    OUT['Z2'] = res
    print('Z2 zusammengesetzte Kovarianz (ν_A = 22, ν_B = 19, Regel ν = 19):', json.dumps(res, ensure_ascii=False))


def z3(rng, N=300_000, Bb=1000):
    res = []
    for nu in (19, 40):
        for rho in (1.0, 0.1):
            S = np.diag([1.0, rho ** 2])
            Sh = wishart2(nu, S, N, rng)                    # unverzerrte Kovarianz aus den Daten
            Lh = np.linalg.cholesky(Sh + 1e-15 * np.eye(2))
            Wb = wishart2(Bb - 1, np.eye(2), N, rng)        # Bootstrap-Rauschen bei B Replikaten
            Shb = Lh @ Wb @ np.swapaxes(Lh, 1, 2)
            for t in (1.5, 10.0):
                p0, _ = groesse_allg(S, Sh, nu, t, ths=(0, 45, 90))
                p1, se = groesse_allg(S, Shb, nu, t, ths=(0, 45, 90))
                res.append(dict(nu=nu, rho=rho, t=t, B_unendlich=round(p0 / A1, 4), B_1000=round(p1 / A1, 4),
                                se2=round(2 * se / A1, 4)))
    OUT['Z3'] = res
    print('Z3 endliche Bootstrap-Zahl:', json.dumps(res))


def z4(rng, N=2_000_000, n=20, chunk=200_000):
    """Direktes MC: n Läufe je Kampagne, D̂ = Mittel, Σ̂ = Stichprobenkovarianz/n; wahre Kovarianz des Mittels
    = Σ_lauf/n mit Σ_lauf = diag(1, ρ²) (Verteilungen auf Einheitskovarianz skaliert)."""
    res = []
    nu = n - 1
    kap = stats.t.isf(A1, nu) / ZQ
    t95 = stats.t.isf(0.05, nu)
    for vert in ('normal', 't5', 'kontaminiert'):
        for rho in (1.0, 0.1):
            for t in (1.5, 10.0):
                treffer = 0
                o1 = 0
                for _ in range(N // chunk):
                    if vert == 'normal':
                        E = rng.standard_normal((chunk, n, 2))
                    elif vert == 't5':
                        E = rng.standard_normal((chunk, n, 2)) / np.sqrt(rng.chisquare(5, (chunk, n, 1)) / 5) * math.sqrt(3 / 5)
                    else:                                   # 10 % Läufe mit dreifacher Streuung, auf Varianz 1 skaliert
                        f = np.where(rng.random((chunk, n, 1)) < 0.1, 3.0, 1.0)
                        E = rng.standard_normal((chunk, n, 2)) * f / math.sqrt(0.9 + 0.1 * 9)
                    E[..., 1] *= rho
                    m = E.mean(1)
                    d = E - m[:, None]
                    S = np.einsum('nki,nkj->nij', d, d) / (n - 1) / n
                    lmax = np.linalg.eigvalsh(S)[:, 1] * n          # normiert: λ_max(Σ) des Mittels = 1/n → 1
                    X = np.abs((t + m[:, 0] * math.sqrt(n)) + 1j * m[:, 1] * math.sqrt(n))
                    s = np.sqrt(lmax)
                    c = kap * s * rice_q_breit(t / (kap * s))
                    treffer += int((X > c).sum())
                    o1 += int((X + t95 * s <= t).sum())
                p = treffer / N
                res.append(dict(verteilung=vert, rho=rho, t=t, faktor=round(p / A1, 3),
                                se2=round(2 * math.sqrt(p * (1 - p) / N) / A1, 3), O1_fehler=round(o1 / N, 4)))
    OUT['Z4'] = res
    print('Z4 schwere Ränder (n = 20, ν = 19, θ = 0):', json.dumps(res, ensure_ascii=False))


def z5(rng, N=400_000):
    res = {}
    for nu in (19, 40):
        lmax, _ = g.lam_ziehen(nu, 1.0, N, rng)
        t95 = stats.t.isf(0.05, nu)
        for t in (1.5, 3.0):
            c = regel_b_c(lmax, nu, t)
            for k in (2.0, 3.0, 5.74):
                p, _ = g.groesse(c, k * t, 0.0, 1.0)
                res[f'macht_nu{nu}_t{t}_k{k}'] = round(p, 4)
        # P(unauffällig | D = 0) und t*
        def pu(t):
            cc = t - t95 * np.sqrt(lmax)
            return float(np.where(cc > 0, stats.rayleigh.cdf(np.maximum(cc, 0)), 0.0).mean())
        res[f'P_unauff_D0_nu{nu}_t1.5'] = round(pu(1.5), 4)
        from scipy.optimize import brentq
        res[f't_stern_O1_nu{nu}'] = round(brentq(lambda t: pu(t) - 0.8, 2.0, 8.0), 3)
    res['t_stern_O1_s_bekannt'] = round(stats.norm.isf(0.05) + math.sqrt(-2 * math.log(0.2)), 3)
    OUT['Z5'] = res
    print('Z5 Macht und unauffällig:', json.dumps(res))


def z6(rng, N=400_000):
    res = []
    from scipy import interpolate
    bg = np.linspace(0, 80, 4001)
    q05 = interpolate.CubicSpline(bg, stats.rice.ppf(0.05, np.maximum(bg, 1e-12)))
    for nu in (10, 19, 40):
        f = nu / (nu + 1)
        for rho in (1.0, 0.5, 0.1):
            lmax, _ = g.lam_ziehen(nu, rho, N, rng)
            sb = np.sqrt(lmax * f)
            for t in (1.5, 3.0, 10.0):
                c = sb * q05(t / sb)
                p = max(g.fehler_o1(c, t, th, rho)[0] for th in np.radians([0, 45, 90]))
                res.append(dict(nu=nu, rho=rho, t=t, fehler=round(p, 4)))
    OUT['Z6'] = res
    print('Z6 c-2-Obergrenze mit eingesetztem ŝ, Fehler am Rand (nominal 0,05):', json.dumps(res))


def z7():
    """E3a: x̂ = s + e, e ~ N(0, 1), Schwelle s/σ = h; u² = (1 − w)·g·f_b + w, g ~ χ²_ν/ν, f_b = (n−1)/n
    (Plug-in-Bootstrap). Größe = E_g[Φ̄(c·u) + Φ̄(2h + c·u)] (exakt bis auf Quadratur über g)."""
    res = []
    def E(fun, nu):
        return integrate.quad(lambda x: fun(x / nu) * stats.chi2.pdf(x, nu), 0, np.inf, limit=400, epsabs=1e-13)[0]
    for n in (12, 20, 22, 24):
        nu = n - 1
        fb = (n - 1) / n
        tq = stats.t.isf(A1, nu)
        t95 = stats.t.isf(0.05, nu)
        for w in (0.0, 0.25, 0.5, 0.75):
            for h in (math.inf, 1.0, 0.5, 0.25, 0.0):
                zus = (lambda c, u: stats.norm.sf(2 * h + c * u)) if math.isfinite(h) else (lambda c, u: 0.0)
                u_b = lambda gg: math.sqrt((1 - w) * gg * fb + w)          # heutiges u (Plug-in)
                u_k1 = lambda gg: math.sqrt((1 - w) * gg + w)              # n/(n−1) nur auf Bootstrap-Anteil
                u_k2 = lambda gg: math.sqrt(((1 - w) * gg * fb + w) / fb)  # n/(n−1) auf ganz u²
                z = E(lambda gg: stats.norm.sf(ZQ * u_b(gg)) + zus(ZQ, u_b(gg)), nu)
                t1 = E(lambda gg: stats.norm.sf(tq * u_k1(gg)) + zus(tq, u_k1(gg)), nu)
                t2 = E(lambda gg: stats.norm.sf(tq * u_k2(gg)) + zus(tq, u_k2(gg)), nu)
                ob = E(lambda gg: stats.norm.cdf(-t95 * u_k2(gg)), nu) if not math.isfinite(h) else None
                res.append(dict(n=n, w=w, schwelle_durch_sigma=('∞' if not math.isfinite(h) else h),
                                z_regel=round(z / A1, 3), t_regel_boot=round(t1 / A1, 3), t_regel_ganz=round(t2 / A1, 3),
                                obere_t_ganz=None if ob is None else round(ob, 4)))
    # Satterthwaite mit geschätzten Gewichten (MC), n = 22
    rng = np.random.default_rng(77)
    N = 4_000_000
    sat = []
    for w in (0.0, 0.25, 0.5, 0.75):
        n = 22
        gg = rng.chisquare(n - 1, N) / (n - 1)
        Zs = rng.standard_normal(N)
        uk = np.sqrt((1 - w) * gg + w)
        nu_eff = uk ** 4 / (((1 - w) * gg) ** 2 / (n - 1))
        p = np.mean(Zs > stats.t.isf(A1, nu_eff) * uk)
        sat.append(dict(w=w, faktor=round(p / A1, 3), se2=round(2 * math.sqrt(p / N) / A1, 3)))
    OUT['Z7'] = dict(tabelle=res, satterthwaite_geschaetzt=sat)
    print('Z7 E3a:', json.dumps(OUT['Z7'], ensure_ascii=False))


if __name__ == '__main__':
    rng = np.random.default_rng(20261019 + 5)
    teile = sys.argv[2:] or ['z1', 'z2', 'z3', 'z4', 'z5', 'z6', 'z7']
    for name in teile:
        fn = globals()[name]
        if name == 'z7':
            fn()
        else:
            fn(rng)
    json.dump(OUT, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1)
