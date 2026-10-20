# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 1.4, 3.1, 3.4,
# 5.2 und 8 („σ̂_ref mit effektiv etwa 21 Freiheitsgraden“; Gegenprobe „analytisch 20,6, Monte Carlo 19,8“;
# „A8-Schranke 2,5·10⁻⁴ je Lauf als Mittel über σ̂_ref, bei bekanntem σ 2,53·10⁻⁵“).
# Zweck: effektive Freiheitsgrade ν_eff von σ̂_ref aus den Leave-one-out-Werten (LOO) der Referenzläufe und die
#   A8-Rate p1 (S1 über G1 je Lauf) marginal über σ̂_ref gegenüber bekanntem σ.
# Eingaben: keine (reine Teststatistik). Ausgabe: Text auf stdout; mit Argument 1 zusätzlich eine JSON-Datei.
# Annahmen: ⟨N⟩ der Referenzläufe unabhängig normal mit gleicher Streuung σ = 1, keine Drift. LOO-Wert wie
#   gueltigkeit.sigma_ref (Code main 0f63187): d_i = R_i − ((1 − β_i)·R_{i−1} + β_i·R_{i+1}), β_i aus den Zeiten der
#   Nachbarn; σ̂_ref = Standardabweichung (ddof = 1) der n − 2 LOO-Werte. Gleich getaktet heißt β_i = 1/2; dann sind
#   benachbarte LOO-Werte mit −2/3 (Abstand 1) und 1/6 (Abstand 2) korreliert, und asymptotisch gilt
#   ν_eff = (n − 2)/(1 + 2·((2/3)² + (1/6)²)). ν_eff hängt von der Zahl UND der Anordnung der Referenzläufe ab;
#   „etwa 21“ gilt nur für 42 gleich getaktete Referenzläufe. Zur Anordnung rechnet das Skript als Beispiel einen
#   ungleichen Takt (Abstände abwechselnd 1 und 3, β_i abwechselnd 1/4 und 3/4); das ist eine Annahme zur
#   Veranschaulichung, keine Anordnung aus Teil B.
#   p1 nach Anhang Tab. F Z. 1437: q(v) = 2·Φ(−3·σ̂_ref/√v), p1 = E[q(2)·q(1,5)] (erster Lauf in ungünstigster Lage,
#   Wiederholung mittig), Mittel über σ̂_ref; bei bekanntem σ ist σ̂_ref = √1,5·σ.
# Seeds: n = 42 default_rng(1) mit 400 000 × 42 Ziehungen (identisch mit dem Befehl in Tab. F Z. 1437),
#   n = 61 default_rng(2), ungleicher Takt default_rng(3); je 400 000 Datensätze.
# Laufzeit: gemessen 6 s Wandzeit, 6 s CPU (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B nu_eff_sigma_ref.py nu_eff_sigma_ref.json > nu_eff_sigma_ref.out
# Herkunft: neu für dieses Belegpaket (20.10.2026); rechnet die Gegenprobe des Hauptbearbeiters nach, deren
#   Skript nicht im Scratch-Ordner liegt.
import json
import sys

import numpy as np
from scipy import integrate, stats

RHO1, RHO2 = 2 / 3, 1 / 6
N_MC = 400_000


def nu_analytisch(n):
    """Asymptotische Näherung für n gleich getaktete Referenzläufe (n − 2 LOO-Werte)."""
    return (n - 2) / (1 + 2 * (RHO1 ** 2 + RHO2 ** 2))


def beta_folge(n, takt):
    """β_i der inneren Referenzläufe i = 1 … n − 2 (Index der Folge)."""
    if takt == 'gleich':
        return np.full(n - 2, 0.5)
    # Abstände abwechselnd 1 und 3: Lauf i hat links Abstand a_i, rechts a_{i+1}
    abst = np.where(np.arange(n - 1) % 2 == 0, 1.0, 3.0)
    return abst[:-1] / (abst[:-1] + abst[1:])


def loo_matrix(n, takt):
    """L mit d = L·R (d: n − 2 LOO-Werte, R: n Referenzläufe)."""
    b = beta_folge(n, takt)
    L = np.zeros((n - 2, n))
    for i in range(n - 2):
        L[i, i], L[i, i + 1], L[i, i + 2] = -(1 - b[i]), 1.0, -b[i]
    return L


def nu_exakt(n, takt):
    """Exakte Momente der quadratischen Form s² = dᵀ·A·d/(m − 1), d ~ N(0, C), A = I − J/m (Satterthwaite).
    ν_E = 2·E[s²]²/Var[s²] = tr(AC)²/tr(ACAC); ν_nom = 2·v²/Var[s²] mit der nominalen LOO-Varianz v = mittleres
    diag(C) (gleich getaktet 1,5); ν_nom < ν_E, weil E[s²] > v (negative Korrelation benachbarter LOO-Werte)."""
    L = loo_matrix(n, takt)
    C = L @ L.T
    m = n - 2
    A = np.eye(m) - np.ones((m, m)) / m
    AC = A @ C
    t1, t2 = np.trace(AC), np.trace(AC @ AC)
    v = float(np.mean(np.diag(C)))
    es2 = t1 / (m - 1)
    vs2 = 2 * t2 / (m - 1) ** 2
    return dict(nu_E=float(2 * es2 ** 2 / vs2), nu_nominal=float(2 * v ** 2 / vs2), E_s2=float(es2), v_nominal=v)


def sref_ziehen(n, takt, seed):
    g = np.random.default_rng(seed)
    R = g.standard_normal((N_MC, n))
    if takt == 'gleich':
        d = R[:, 1:-1] - (R[:, :-2] + R[:, 2:]) / 2          # wie Anhang Tab. F Z. 1437
    else:
        b = beta_folge(n, takt)
        d = R[:, 1:-1] - ((1 - b) * R[:, :-2] + b * R[:, 2:])
    return d.std(1, ddof=1)


def q(s, v):
    return 2 * stats.norm.sf(3 * s / v ** 0.5)


def p1_chi2(nu, v=1.5):
    """p1 unter der Annahme σ̂_ref² ~ v·χ²_ν/ν (Quadratur)."""
    f = lambda x: q(np.sqrt(v * x / nu), 2) * q(np.sqrt(v * x / nu), 1.5) * stats.chi2.pdf(x, nu)  # noqa: E731
    return integrate.quad(f, 0, np.inf, limit=200, epsabs=1e-14)[0]


def main():
    out = {}
    print('Effektive Freiheitsgrade von σ̂_ref (Leave-one-out) und A8-Rate p1 je Lauf')
    print('\n1) ν_eff analytisch (gleich getaktet): (n − 2)/(1 + 2·((2/3)² + (1/6)²)) = (n − 2)/1,9444')
    out['analytisch'] = {}
    for n in (11, 41, 42, 61):
        out['analytisch'][str(n)] = round(nu_analytisch(n), 3)
        print(f'   n = {n:2d} Referenzläufe ({n - 2} LOO-Werte): ν_eff = {nu_analytisch(n):6.2f}')
    print('\n2) exakte Momente (Satterthwaite über die Kovarianz der LOO-Werte)')
    print('   ν_E: bezogen auf E[σ̂²]; ν_nom: bezogen auf die nominale LOO-Varianz (gleich getaktet 1,5·σ²)')
    out['exakt'] = {}
    for takt, ns in (('gleich', (11, 41, 42, 61)), ('ungleich_1_3', (42, 61))):
        for n in ns:
            e = nu_exakt(n, takt)
            out['exakt'][f'{takt}_{n}'] = {k: round(x, 4) for k, x in e.items()}
            print(f'   {takt:13s} n = {n:2d}: ν_E = {e["nu_E"]:6.2f}, ν_nom = {e["nu_nominal"]:6.2f}, '
                  f'E[σ̂²] = {e["E_s2"]:.4f}, nominal {e["v_nominal"]:.4f}')
    print(f'\n3) Monte Carlo ({N_MC} Datensätze je Fall) und p1 marginal über σ̂_ref (Formel Anhang Tab. F Z. 1437)')
    out['monte_carlo'] = {}
    for takt, n, seed in (('gleich', 42, 1), ('gleich', 61, 2), ('ungleich_1_3', 42, 3)):
        s = sref_ziehen(n, takt, seed)
        s2 = s ** 2
        v = nu_exakt(n, takt)['v_nominal']
        nu_e = 2 * s2.mean() ** 2 / s2.var()
        nu_n = 2 * v ** 2 / s2.var()
        p1 = float((q(s, 2) * q(s, 1.5)).mean())
        u = s / np.sqrt(1.5)
        r = dict(seed=seed, nu_E=round(float(nu_e), 3), nu_nominal=round(float(nu_n), 3), p1_marginal=p1,
                 q15=float(q(s, 1.5).mean()), q2=float(q(s, 2).mean()), P_u_lt_0_8=float((u < 0.8).mean()),
                 anteil_p1_aus_u_lt_0_8=float((q(s, 2) * q(s, 1.5))[u < 0.8].sum() / (q(s, 2) * q(s, 1.5)).sum()))
        out['monte_carlo'][f'{takt}_{n}'] = r
        print(f'   {takt:13s} n = {n:2d} (Seed {seed}): ν_E = {nu_e:6.2f}, ν_nom = {nu_n:6.2f}; '
              f'q(1,5) = {r["q15"]:.4f}, q(2) = {r["q2"]:.4f}, p1 = {p1:.3e}; '
              f'P(u < 0,8) = {r["P_u_lt_0_8"]:.3f} mit Anteil {r["anteil_p1_aus_u_lt_0_8"]:.2f} an p1')
    s = np.sqrt(1.5)
    p1_fest = float(q(s, 2) * q(s, 1.5))
    out['sigma_bekannt'] = dict(q15=float(q(s, 1.5)), q2=float(q(s, 2)), p1=p1_fest)
    print(f'   σ bekannt (σ̂_ref = √1,5·σ): q(1,5) = {q(s, 1.5):.4f}, q(2) = {q(s, 2):.4f}, p1 = {p1_fest:.3e}')
    print('\n4) p1 unter der Näherung σ̂_ref² ~ 1,5·σ²·χ²_ν/ν (Quadratur): naiv ν = n − 2 gegen ν_eff')
    out['chi2_naeherung'] = {}
    for lab, nu in (('n = 42, naiv ν = 40', 40), ('n = 42, ν_eff analytisch', nu_analytisch(42)),
                    ('n = 61, naiv ν = 59', 59), ('n = 61, ν_eff analytisch', nu_analytisch(61))):
        p = p1_chi2(nu)
        out['chi2_naeherung'][lab] = dict(nu=round(nu, 3), p1=p)
        print(f'   {lab:26s} (ν = {nu:5.2f}): p1 = {p:.3e} = {p / p1_fest:4.1f}-fach gegenüber σ bekannt')
    if len(sys.argv) > 1:
        json.dump(out, open(sys.argv[1], 'w'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
