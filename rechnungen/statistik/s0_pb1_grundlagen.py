"""s0_pb1_grundlagen.py – PB1-Herleitung nachrechnen und Äquivalenzgrenzen Δ_q im A4-Beispiel.

Prüfgruppe statistik, P2. Nur lesend auf Repo-Code (linear_solver.py). Ausgabe nach stdout.

1. Nachrechnung von A4/A8: Δ(F_min) = 0,25·ΔF_Zelt, u_c ≤ Δ/c mit c = t(1 − α/(2·147); ν).
2. Δ_q für alle sieben Größen (F_min − ⟨N⟩, Re/Im N_1..N_3) im A4-Beispiel (starr, μ = 0,4, 10 Hz),
   volles Spektrum und bandbegrenzt (k_max = 3, 6, 9).
3. Was PB1 wirklich verlangt: Die Bedingung u_c ≤ Δ/c ist nur notwendig (Bestätigung genau bei r = 0).
   Gesucht ist u_c, bei dem PB1 und „kein |z| > c“ mit Wahrscheinlichkeit 0,8 (Präreg §5.4) bzw. 0,5
   eintreten, bei exakter Superposition (r ~ N(0, u²)), mit geschätztem u (χ²_ν) und
   (a) einem einzigen Test, (b) 21 unabhängigen Tests (nur F_min), (c) 147 unabhängigen Tests mit
   gleichem Verhältnis Δ/u. Unabhängigkeit ist die ungünstige Annahme (Korrelation erhöht P).
4. IUT-Vergleich: Für „alle 147 äquivalent“ genügt nach dem Intersection-Union-Prinzip je Test ein
   TOST auf Niveau α, also c_eq = t(1 − α; ν) statt c = t(1 − α/294; ν).
"""
import numpy as np
from scipy.stats import norm, t, chi2
import linear_solver as L

MG = L.MG
alpha, m = 0.05, 147

print('=== 1. Nachrechnung A4/A8 ===')
for (lab, args) in (('starr mu=0.4 10 Hz', (None, 0.0, 0.4)),):
    p2 = np.arange(100, 140.1, 2.0)
    r = L.solve(p2, 240.0, *args)
    Fmin = r['F_min_lin']
    dF = Fmin.max() - Fmin.min()
    D = 0.25 * dF
    print(f'{lab}: Delta F_Zelt = {dF:.4f} N, Delta(F_min) = {D:.4f} N')
    for nu in (np.inf, 9, 19, 29):
        c = norm.ppf(1 - alpha / (2 * m)) if np.isinf(nu) else t.ppf(1 - alpha / (2 * m), nu)
        print(f'   nu = {nu}: c = {c:.3f}, u_c <= Delta/c = {D / c:.4f} N ({100 * D / c / MG:.2f} % von Mg)')


def harmonics_section(K_c, C_c, mu, kmax=None, f_hz=10.0):
    """Harmonische N_k (k = 1..3, komplex, Konvention N_k = (2/n) sum N e^{-ik theta}) und F_min − ⟨N⟩ auf dem
    Schnitt, optional bandbegrenzt (alle k > kmax null)."""
    P, n = L.profile_spectrum()
    P = P * (f_hz / 10.0) ** 2
    k = np.arange(P.size)
    H, _ = L.transfer(K_c, C_c, P.size, f_hz=f_hz)
    p2 = np.arange(100, 140.1, 2.0)
    comb = (1 + np.exp(-1j * np.outer(np.radians(p2), k)) + np.exp(-1j * k * np.radians(240.0))) / 3
    A = mu * L.M * P * comb * H
    if kmax is not None:
        A[:, kmax + 1:] = 0
    F = MG + np.fft.irfft(A, n, axis=1)[:, ::8]
    Nk = 2 * A[:, 1:4] / n
    return p2, F.min(1) - MG, Nk


print('\n=== 2. Delta_q = 0,25 D_q im A4-Beispiel (starr, mu = 0,4, 10 Hz) ===')
print('k_max | D(F_min) Delta(F_min) | D|N1| Delta1 | D|N2| Delta2 | D|N3| Delta3 | u_c-Grenze Delta/c (nu=19): F_min N1 N2 N3')
c19 = t.ppf(1 - alpha / (2 * m), 19)
for kmax in (None, 9, 6, 3):
    p2, fm, Nk = harmonics_section(None, 0.0, 0.4, kmax)
    D = [fm.max() - fm.min()] + [np.abs(Nk[:, j]).max() for j in range(3)]
    De = [0.25 * d for d in D]
    print(f'{str(kmax):>5} | {D[0]:.4f} {De[0]:.4f} | {D[1]:.4f} {De[1]:.4f} | {D[2]:.4f} {De[2]:.4f} | '
          f'{D[3]:.4f} {De[3]:.4f} | ' + ' '.join(f'{d / c19:.4f}' for d in De))
p2, fm, Nk = harmonics_section(None, 0.0, 0.4, None)
print('Kammfaktor |N_k|/|N_k(synchron)| auf dem Schnitt, max:',
      [round(float(np.abs(Nk[:, j]).max() / (2 * 0.4 * L.M * np.abs(L.profile_spectrum()[0][j + 1]) / L.profile_spectrum()[1])), 3)
       for j in range(3)])

print('\n=== 3. Was PB1 bei exakter Superposition verlangt ===')
rng = np.random.default_rng(20261002)


def p_confirm(ratio, nu, ntest, nsim=200_000):
    """P(|r| + c û <= Delta und |r| <= c û) je Test, hoch ntest (unabhängig); ratio = Delta/u (wahres u)."""
    c = norm.ppf(1 - alpha / (2 * m)) if np.isinf(nu) else t.ppf(1 - alpha / (2 * m), nu)
    r = rng.standard_normal(nsim)
    uh = np.ones(nsim) if np.isinf(nu) else np.sqrt(chi2.rvs(nu, size=nsim, random_state=rng) / nu)
    ok = (np.abs(r) + c * uh <= ratio) & (np.abs(r) <= c * uh)
    p1 = ok.mean()
    return p1, p1 ** ntest


for nu in (np.inf, 19, 29):
    c = norm.ppf(1 - alpha / (2 * m)) if np.isinf(nu) else t.ppf(1 - alpha / (2 * m), nu)
    print(f'nu = {nu}: c = {c:.3f}; notwendige Grenze Delta/u = c -> P(PB1) = 0')
    for ntest in (1, 21, 147):
        out = []
        for target in (0.5, 0.8):
            lo, hi = c, 4 * c
            for _ in range(30):
                mid = (lo + hi) / 2
                if p_confirm(mid, nu, ntest, 100_000)[1] >= target:
                    hi = mid
                else:
                    lo = mid
            out.append(hi)
        print(f'   {ntest:>3} Tests: P = 0,5 bei Delta/u = {out[0]:.2f} (u <= {1 / out[0]:.4f} Delta), '
              f'P = 0,8 bei Delta/u = {out[1]:.2f} (u <= {1 / out[1]:.4f} Delta); '
              f'F_min (Delta = 0,1173 N): u <= {0.1173 / out[1]:.4f} N statt {0.1173 / c:.4f} N')

print('\n=== 4. IUT: TOST je Test auf Niveau alpha genügt ===')
for nu in (np.inf, 19):
    c = norm.ppf(1 - alpha / (2 * m)) if np.isinf(nu) else t.ppf(1 - alpha / (2 * m), nu)
    ceq = norm.ppf(1 - alpha) if np.isinf(nu) else t.ppf(1 - alpha, nu)
    print(f'nu = {nu}: c(Bonferroni 147, zweis.) = {c:.3f}, c_eq(IUT-TOST) = {ceq:.3f}, Faktor {c / ceq:.2f}; '
          f'F_min-Grenze u <= Delta/c_eq = {0.1173 / ceq:.4f} N')
    # tatsächliche Fehlerrate „fälschlich bestätigt“ am Rand der Äquivalenzzone, ein Test, PB1 wie registriert
    nsim = 400_000
    u = 0.1173 / (2 * c)
    r = 0.1173 + u * rng.standard_normal(nsim)       # wahre Abweichung genau Delta
    uh = u * (np.ones(nsim) if np.isinf(nu) else np.sqrt(chi2.rvs(nu, size=nsim, random_state=rng) / nu))
    print(f'   wahre Abweichung = Delta, u = Delta/(2c): P(Intervall in ±Delta) PB1 = '
          f'{np.mean(np.abs(r) + c * uh <= 0.1173):.2e}, IUT-TOST = {np.mean(np.abs(r) + ceq * uh <= 0.1173):.4f} (Soll <= 0,05)')
