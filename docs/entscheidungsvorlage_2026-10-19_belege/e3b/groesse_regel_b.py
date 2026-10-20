# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 4.2 (Größe am Rand, Gegenproben).
# Zweck: Größe der E3b-Regel B am Schwellenrand über das volle Raster ν ∈ {10, 19, 21, 40, 80}, ρ ∈ {1; 0,5;
#   0,25; 0,1}, t = 0,05 … 10, θ in 15°-Schritten (bedingt exakte Quadratur), Gegenregeln R1/R1a/R1spur/Bspur,
#   Fehlerrate von „unauffällig“ (O1).
# Eingaben: Argument 1 = Ausgabe (JSON); Tabelle auf stdout.
# Annahmen: D̂ zweidimensional normal, Σ̂ = W/ν mit W ~ Wishart(ν, Σ), unabhängig von D̂ (siehe Modulbeschreibung).
# Seed: 20261019 + 100·i + j je Zelle (ν_i, ρ_j); N_W = 400 000. Laufzeit: 287 s Wandzeit mit vier Prozessen
#   (Pool(4), etwa 19 Kernminuten; Angabe der übernommenen Ausgabe). Nicht neu gerechnet; geprüft wurde nur die
#   Aufrufbarkeit der Zellfunktion mit kleinem N_W in einem Prozess (README).
# Aufruf: python3 -B groesse_regel_b.py groesse_regel_b.json > groesse_regel_b.out
# Herkunft: Nachprüfung 5 (E3b-Grenze). Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""Nachleseauftrag 5, Teil (2): unabhängige Prüfung der Größe der E3b-Regel B der Entscheidungsvorlage (Abschnitt 4.2)
am Schwellenrand, auf Ebene der Teststatistik. Eigene Implementierung, kein Code aus agenda/ übernommen.

Modell (Annahmen): D̂ = D + ε, ε ~ N₂(0, Σ), Σ = diag(1, ρ²) (λ_max(Σ) = 1 normiert, große Achse entlang Re);
Σ̂ = W/ν, W ~ Wishart(ν, Σ), unabhängig von ε (Gauß: Mittel und Stichprobenkovarianz unabhängig). Σ̂ ist die mit
n/(n−1) korrigierte Bootstrap-Kovarianz (B → ∞). Wahrer Wert am Rand: D = t·e^{iθ}, |D| = t = q_tol/s.

Methode (bedingt-exakt statt reines Monte Carlo): Für jedes gezogene Σ̂ ist die kritische Schranke c(Σ̂) fest; die
Wahrscheinlichkeit P_ε(|D + ε| > c) des anisotropen Gaußvektors wird durch Quadratur berechnet (Gauß-Legendre in
ψ mit u = c·sin ψ), über ein c-Gitter tabelliert und interpoliert; gemittelt wird nur über Σ̂ (N_W Ziehungen).

Regeln „auffällig“ (X = |D̂|):
  B     : X > κ·ŝ·Rice⁻¹(1 − α/m; t/(κ·ŝ)), ŝ² = λ_max(Σ̂), κ = t(1 − α/m; ν)/z(1 − α/m)   (Vorlage, Option B)
  R1    : X > ŝ_b·Rice⁻¹(1 − α/m; t/ŝ_b), ŝ_b² = λ_max(Σ̂)·(n−1)/n  (c-2: Bootstrap-Kovarianz eingesetzt, kein κ)
  R1a   : wie R1 mit ŝ² = λ_max(Σ̂) (nur n/(n−1), kein κ)
  R1spur: wie R1 mit ŝ_b² = Spur(Σ̂)/2·(n−1)/n
  Bspur : wie B mit ŝ² = Spur(Σ̂)/2
Regel „unauffällig“ O1 (Vorlage): X + t(0,95; ν)·ŝ ≤ t, ŝ² = λ_max(Σ̂); Fehlerrate bei |D| = t·(1 + δ).
Ausgabe: Größe in Vielfachen von α/m (Maximum über θ), Standardfehler aus der Streuung über Σ̂.
"""
import json
import math
import sys
import time

import numpy as np
from scipy import interpolate, special, stats

M, ALPHA = 43, 0.05
A1 = ALPHA / M
ZQ = stats.norm.isf(A1)

# Rice-Quantil Rice⁻¹(1 − α/m; b) (Skala 1) auf feinem Gitter, kubisch interpoliert; Fehlerprüfung unten
_BG = np.linspace(0.0, 80.0, 8001)
_RQ = stats.rice.isf(A1, np.maximum(_BG, 1e-12))
_RQ[0] = math.sqrt(-2 * math.log(A1))
_RQS = interpolate.CubicSpline(_BG, _RQ)


def rice_q(b):
    b = np.asarray(b, float)
    if np.any(b > _BG[-1]):
        raise ValueError('b außerhalb des Gitters')
    return _RQS(b)


# Gauß-Legendre-Knoten auf ψ ∈ (−π/2, π/2), stückweise für steile Integranden bei kleinem ρ
_XG, _WG = np.polynomial.legendre.leggauss(32)
_KANTEN = np.linspace(-np.pi / 2, np.pi / 2, 17)       # 512 Knoten; gegen 2048 Knoten rel. Fehler < 1e-8 geprüft
_PSI = np.concatenate([(a + b) / 2 + (b - a) / 2 * _XG for a, b in zip(_KANTEN[:-1], _KANTEN[1:])])
_WPSI = np.concatenate([(b - a) / 2 * _WG for a, b in zip(_KANTEN[:-1], _KANTEN[1:])])


def p_innen_aussen(c, mu_u, mu_v, rho):
    """(P(|Z| ≤ c), P(|Z| > c)) für Z = U + iV, U ~ N(mu_u, 1), V ~ N(mu_v, ρ²); c ≥ 0 als Vektor."""
    c = np.asarray(c, float)[:, None]
    u = c * np.sin(_PSI)[None]
    h = c * np.cos(_PSI)[None]
    dens = stats.norm.pdf(u - mu_u) * h
    a, b = (h - mu_v) / rho, (-h - mu_v) / rho
    innen = (dens * (special.ndtr(a) - special.ndtr(b))) @ _WPSI
    aussen_streifen = (dens * (special.ndtr(-a) + special.ndtr(b))) @ _WPSI
    c1 = c[:, 0]
    aussen = special.ndtr(-(c1 - mu_u)) + special.ndtr(-(c1 + mu_u)) + aussen_streifen
    return innen, aussen


def tabelle(fn, cmin, cmax, k=600):
    cg = np.linspace(max(cmin, 0.0), cmax, k)
    return cg, fn(cg)


def lam_ziehen(nu, rho, N, rng):
    """λ_max und Spur von Σ̂ = W/ν, W ~ Wishart(ν, diag(1, ρ²)), über Bartlett-Zerlegung."""
    l11 = np.sqrt(rng.chisquare(nu, N))
    l22 = np.sqrt(rng.chisquare(nu - 1, N))
    l21 = rng.standard_normal(N)
    w11, w21, w22 = l11 ** 2, rho * l11 * l21, rho ** 2 * (l21 ** 2 + l22 ** 2)
    sp, det = w11 + w22, w11 * w22 - w21 ** 2
    lmax = sp / 2 + np.sqrt(np.maximum(sp * sp / 4 - det, 0.0))
    return lmax / nu, sp / nu


def mittel_se(werte):
    return float(werte.mean()), float(werte.std(ddof=1) / math.sqrt(werte.size))


def groesse(c, t, th, rho):
    """E über Σ̂ von P_ε(|D + ε| > c(Σ̂)) mit D = t·e^{iθ}."""
    mu_u, mu_v = t * math.cos(th), t * math.sin(th)
    lo, hi = float(c.min()), float(c.max())
    cg, (_, pa) = tabelle(lambda x: p_innen_aussen(x, mu_u, mu_v, rho), lo, hi)
    lp = np.log(np.maximum(pa, 1e-300))
    return mittel_se(np.exp(np.interp(c, cg, lp)))


def fehler_o1(c, t, th, rho):
    """E über Σ̂ von P_ε(|D + ε| ≤ c(Σ̂)), c ≤ 0 → 0."""
    mu_u, mu_v = t * math.cos(th), t * math.sin(th)
    pos = c > 0
    if not pos.any():
        return 0.0, 0.0
    cg, (pi, _) = tabelle(lambda x: p_innen_aussen(x, mu_u, mu_v, rho), 0.0, float(c[pos].max()))
    w = np.zeros_like(c)
    w[pos] = np.interp(c[pos], cg, pi)
    return mittel_se(w)


def pruefungen():
    """Kontrollen der Hilfsmittel: Quadratur gegen Rice (ρ = 1) und gegen Monte Carlo (ρ = 0,1); Rice-Gitter."""
    out = {}
    c = np.array([0.5, 2.0, 3.676, 5.0, 7.5, 9.0])
    for t in (0.0, 1.5, 6.0):
        _, pa = p_innen_aussen(c, t, 0.0, 1.0)
        ex = stats.rice.sf(c, max(t, 1e-12))
        ok = ex > 1e-10
        out[f'rice_rel_fehler_t{t}'] = float(np.max(np.abs(pa[ok] / ex[ok] - 1)))
    rng = np.random.default_rng(5)
    N = 4_000_000
    for th in (0.0, math.pi / 2, math.pi / 4):
        Z = np.abs(1.5 * np.exp(1j * th) + rng.standard_normal(N) + 1j * 0.1 * rng.standard_normal(N))
        cc = np.array([1.0, 2.0, 3.0, 4.5])
        inn, pa = p_innen_aussen(cc, 1.5 * math.cos(th), 1.5 * math.sin(th), 0.1)
        mc = np.array([(Z > x).mean() for x in cc])
        se = np.sqrt(np.maximum(mc * (1 - mc), 1.0 / N) / N)
        out[f'mc_rho0.1_th{round(math.degrees(th))}_max_abw_in_se'] = float(np.max(np.abs(pa - mc) / np.maximum(se, 1e-12)))
        out[f'summe_innen_aussen_th{round(math.degrees(th))}'] = float(np.max(np.abs(inn + pa - 1)))
    bt = np.random.default_rng(6).uniform(0, 30, 200)
    out['rice_gitter_max_rel_fehler'] = float(np.max(np.abs(rice_q(bt) / stats.rice.isf(A1, bt) - 1)))
    # λ_max-Ziehung gegen direkte Wishart-Ziehung (KS-Test)
    nu, rho = 19, 0.3
    lm, _ = lam_ziehen(nu, rho, 20000, np.random.default_rng(7))
    G = np.random.default_rng(8).standard_normal((20000, 2, nu)) * np.array([1.0, rho])[None, :, None]
    Wd = np.einsum('nik,njk->nij', G, G) / nu
    lmd = np.linalg.eigvalsh(Wd)[:, -1]
    out['ks_p_lambda_bartlett_vs_direkt'] = float(stats.ks_2samp(lm, lmd).pvalue)
    return out


NUS = (10, 19, 21, 40, 80)
RHOS = (1.0, 0.5, 0.25, 0.1)
TS = (0.05, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0)
THS = np.radians([0, 15, 30, 45, 60, 75, 90])
DELTAS = (0.0, 0.02, 0.05, 0.1, 0.2, 0.5)


def zelle(arg):
    nu, rho, seed, N_W = arg
    rng = np.random.default_rng(seed)
    kap = stats.t.isf(A1, nu) / ZQ
    t95 = stats.t.isf(0.05, nu)
    f = nu / (nu + 1)                                       # (n − 1)/n mit n = ν + 1
    lmax, sp = lam_ziehen(nu, rho, N_W, rng)
    s_B, s_R1, s_spB, s_spR = np.sqrt(lmax), np.sqrt(lmax * f), np.sqrt(sp / 2), np.sqrt(sp / 2 * f)
    erg = []
    for t in TS:
        regeln = {
            'B': kap * s_B * rice_q(t / (kap * s_B)),
            'R1': s_R1 * rice_q(t / s_R1),
            'R1a': s_B * rice_q(t / s_B),
            'R1spur': s_spR * rice_q(t / s_spR),
            'Bspur': kap * s_spB * rice_q(t / (kap * s_spB)),
        }
        zeile = dict(nu=nu, rho=rho, t=t)
        for name, c in regeln.items():
            best = (-1.0, 0.0, 0.0)
            for th in THS:
                p, se = groesse(c, t, th, rho)
                if p > best[0]:
                    best = (p, se, th)
            zeile[name] = dict(faktor=best[0] / A1, se2=2 * best[1] / A1, theta=round(math.degrees(best[2])))
        o1 = []
        c = t - t95 * s_B
        for d in DELTAS:
            o1.append(max(fehler_o1(c, t * (1 + d), th, rho)[0] for th in THS))
        zeile['O1'] = o1
        erg.append(zeile)
    return erg


def main(N_W=400_000, seed=20261019):
    from multiprocessing import Pool
    t0 = time.time()
    kontrollen = pruefungen()
    print('Kontrollen der Hilfsmittel:', json.dumps(kontrollen))
    args = [(nu, rho, seed + 100 * i + j, N_W) for i, nu in enumerate(NUS) for j, rho in enumerate(RHOS)]
    with Pool(4) as pool:
        teile = pool.map(zelle, args)
    erg = [z for teil in teile for z in teil]
    print(f'\nGröße am Rand, Vielfache von α/m = {A1:.6f} (Maximum über θ ∈ 0°…90° in 15°-Schritten; θ des Maximums, '
          f'2·SE); N_W = {N_W} Ziehungen von Σ̂ je (ν, ρ)')
    print(' ν   ρ     t    |  B (Vorlage)         |  R1 (c-2, plug-in)   | R1a  | R1spur | Bspur | '
          'O1-Fehler bei |D| = t·(1+δ), δ = ' + ', '.join(str(d) for d in DELTAS))
    for zeile in erg:
        def fm(k):
            z = zeile[k]
            return f"{z['faktor']:5.2f} ({z['theta']:2d}°, ±{z['se2']:.3f})"
        print(f"{zeile['nu']:3d} {zeile['rho']:4.2f} {zeile['t']:5.2f}  | {fm('B')} | {fm('R1')} | {zeile['R1a']['faktor']:4.2f} "
              f"| {zeile['R1spur']['faktor']:6.2f} | {zeile['Bspur']['faktor']:5.2f} | " + ' '.join(f'{x:.4f}' for x in zeile['O1']))
    zus = {}
    for k in ('B', 'R1', 'R1a', 'R1spur', 'Bspur'):
        z = max(erg, key=lambda e: e[k]['faktor'])
        zus[k] = dict(max_faktor=round(z[k]['faktor'], 3), se2=round(z[k]['se2'], 3),
                      bei=dict(nu=z['nu'], rho=z['rho'], t=z['t'], theta=z[k]['theta']))
    for i, d in enumerate(DELTAS):
        z = max(erg, key=lambda e: e['O1'][i])
        zus[f'O1_max_delta{d}'] = dict(wert=round(z['O1'][i], 5), bei=dict(nu=z['nu'], rho=z['rho'], t=z['t']))
    print('\nZusammenfassung:', json.dumps(zus, ensure_ascii=False))
    print(f'Laufzeit {time.time() - t0:.0f} s')
    json.dump(dict(kontrollen=kontrollen, ergebnisse=erg, zusammenfassung=zus), open(sys.argv[1], 'w'), ensure_ascii=False,
              indent=1)


if __name__ == '__main__':
    main()
