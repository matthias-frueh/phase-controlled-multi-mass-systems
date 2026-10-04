"""z7_sta10_drift.py - Gegenpruefung STA-10 (Drift-Logik z0/z1, PB1) mit eigenem, halbanalytischem Rechenweg.

Eigene Rechnung:
 (1) A4-Beispiel (starr, mu = 0,4, 10 Hz, Egg, k_max = 9) mit eigener Profilreihe: y_q,i fuer F_min - <N>
     und Re/Im N_1..3 an den 21 Schnittpunkten (phi2 = 100..140 Grad, phi3 = 240 Grad), Delta_q nach Praereg §8.5.
 (2) Kritischer Wert c = t(1 - 0,05/294; nu) fuer nu = 37 (nu_eff der s2-Laeufe) und Grenzfaelle.
 (3) Verstaerkungsdrift 0,1 % (G7) und Modulantwort-Drift 1 %/3 % zwischen Phase 0 und 1:
     r0 = -d*y (Vorhersage aus Phase 0 um (1+d) groesser), r1 = 0; z0-Erwartung je Test mit u_c aus s2 (Mediane).
 (4) Gauss-/t-Naeherung je Test: P(bestaetigt) = P(kein |z0| > c, kein |z1| > c) und P(falsifiziert) =
     P(es gibt q mit |z0_q| > c, |z1_q| > c, gleiches Vorzeichen), Tests unabhaengig (Obergrenze fuer die
     Vereinigung), Paarkorrelation z0/z1 rho = 0,5 (Anteil der Messseite).
 (5) PB1-Bindung analytisch: noetiges Delta_q/u_q, damit max(|r| + c u) <= Delta mit Wahrscheinlichkeit 0,9.
"""
import numpy as np
from scipy.stats import t as tdist, norm
import zm

mu, KMAX, NTH = 0.4, 9, 2000
ck = zm.ck_analytic(KMAX)
th = np.arange(NTH) * 2 * np.pi / NTH
k = np.arange(1, KMAX + 1)


def curve(p2, p3):
    phis = np.radians([0.0, p2, p3])
    comb = np.exp(-1j * np.outer(k, phis)).sum(1)
    Nk_ = mu * zm.M / 3 * ck[1:] * comb             # einseitige Koeffizienten (zweiseitig c_k)
    N = zm.MG + 2 * np.real(Nk_ @ np.exp(1j * np.outer(k, th)))
    return N, 2 * Nk_                               # N_k = (2/N_th) sum N e^{-ik theta}


P2 = np.arange(100, 141, 2.0)
Y = {'F': [], 'N1': [], 'N2': [], 'N3': []}
for p2 in P2:
    N, Nk_ = curve(p2, 240.0)
    Y['F'].append(N.min() - N.mean())
    for j in (1, 2, 3):
        Y[f'N{j}'].append(Nk_[j - 1])
YF = np.array(Y['F'])
print('=== (1) A4-Beispiel, k_max = 9 ===')
Nm, _ = curve(120, 240); N100, _ = curve(100, 240)
print(f' F_min(120) = {Nm.min():.4f} N, F_min(100) = {N100.min():.4f} N (Praereg A6: 5,6781 / 5,1608 N)')
D_F = (YF + zm.MG).max() - (YF + zm.MG).min()
Delta = {'F': 0.25 * D_F}
tests = {'F': YF}
for j in (1, 2, 3):
    a = np.array(Y[f'N{j}'])
    Delta[f'N{j}'] = 0.25 * np.abs(a).max()
    tests[f'Re N{j}'] = a.real
    tests[f'Im N{j}'] = a.imag
print(f' Delta_F = {Delta["F"]*1e3:.1f} mN, Delta_N1..3 = {Delta["N1"]*1e3:.1f}/{Delta["N2"]*1e3:.1f}/{Delta["N3"]*1e3:.1f} mN')
print(f' max|y|: F {np.abs(YF).max():.4f} N; ' + ', '.join(f'{q} {np.abs(v).max():.4f}' for q, v in tests.items() if q != 'F'))

print('\n=== (2) Kritischer Wert ===')
for nu in (19, 37, 1e9):
    print(f' nu = {nu:g}: c = {tdist.ppf(1 - 0.05/294, nu):.3f}')
c = tdist.ppf(1 - 0.05 / 294, 37)

U = {  # u_c je Groesse [N], Mediane der s2-Laeufe (statistik/s2_h1_oc_L*_n20_n020_k9.csv, Szenario exakt)
    'L0': dict(F=0.262e-3, N1=0.176e-3, N2=0.121e-3, N3=0.084e-3),
    'L1': dict(F=0.994e-3, N1=1.472e-3, N2=0.508e-3, N3=0.233e-3),
    'L2': dict(F=3.30e-3, N1=4.936e-3, N2=1.695e-3, N3=0.771e-3),
    'L3': dict(F=9.86e-3, N1=14.73e-3, N2=5.065e-3, N3=2.292e-3)}


def uvec(L):
    out = []
    for q, v in tests.items():
        key = 'F' if q == 'F' else q.split()[1]
        out.append(np.full(v.size, U[L][key]))
    return np.concatenate(out)


yall = np.concatenate(list(tests.values()))
Dall = np.concatenate([np.full(v.size, Delta['F' if q == 'F' else q.split()[1]]) for q, v in tests.items()])
print(f' Anzahl Tests: {yall.size} (erwartet 147)')

print('\n=== (3) Erwartete z0 bei Drift zwischen Phase 0 und Phase 1 ===')
for d, lab in ((0.001, 'Verstaerkung 0,1 % (G7)'), (0.01, 'Modulantwort 1 %'), (0.03, 'Modulantwort 3 %')):
    for L in ('L0', 'L1', 'L2', 'L3'):
        z0 = d * np.abs(yall) / uvec(L)
        names = [q for q, v in tests.items() for _ in v]
        i = np.argmax(z0)
        zF = (d * np.abs(YF) / U[L]['F']).max()
        print(f' {lab:24s} {L}: max z0 = {z0.max():5.1f} ({names[i]}), max z0(F_min) = {zF:5.1f}, '
              f'Tests mit E|z0| > c: {(z0 > c).sum():3d}/147')

print('\n=== (4) Gauss/t-Naeherung, Tests unabhaengig, rho(z0, z1) = 0,5, nu = 37 ===')
rng = np.random.default_rng(7)
NMC = 20000
for d in (0.0, 0.01, 0.03):
    for L in ('L0', 'L1', 'L2', 'L3'):
        mz0 = -d * yall / uvec(L)
        n = yall.size
        e1 = rng.standard_normal((NMC, n)); e2 = rng.standard_normal((NMC, n)); e3 = rng.standard_normal((NMC, n))
        s = np.sqrt(rng.chisquare(37, (NMC, n)) / 37)
        z0 = (mz0 + np.sqrt(0.5) * e1 + np.sqrt(0.5) * e2) / s     # gemeinsamer Messanteil e1
        z1 = (np.sqrt(0.5) * e1 + np.sqrt(0.5) * e3) / s
        r0 = z0 * uvec(L)
        sig0, sig1 = np.abs(z0) > c, np.abs(z1) > c
        fals = (sig0 & sig1 & (np.sign(z0) == np.sign(z1))).any(1)
        pb1 = ((np.abs(r0) + c * uvec(L)) <= Dall).all(1)
        best = (~sig0.any(1)) & (~sig1.any(1)) & pb1
        print(f' Drift {d*100:3.0f} % {L}: P(falsifiziert) = {fals.mean():.4f}, P(bestaetigt) = {best.mean():.3f}, '
              f'P(PB1) = {pb1.mean():.3f}, P(ein |z0|>c) = {sig0.any(1).mean():.3f}, P(ein |z1|>c) = {sig1.any(1).mean():.3f}')
print(f' Analytische Obergrenze P(falsifiziert | Drift, alle z0 signifikant): 147 * P(t_37 > c) = {147*(0.05/294):.4f}')

print('\n=== (5) PB1-Bindung: noetiges Delta/u fuer P(max_q(|r|/u) + c <= Delta/u) = 0,9 bei 21 bzw. 147 Tests ===')
for m in (21, 42, 147):
    zq = norm.ppf(1 - (1 - 0.9 ** (1 / m)) / 2)
    print(f' m = {m}: Delta/u >= c + {zq:.2f} = {c+zq:.2f}')
for key, ratio in (('F', 1.0), ('N1', 1.495), ('N2', 0.514), ('N3', 0.234)):
    need = c + norm.ppf(1 - (1 - 0.9 ** (1 / 21)) / 2)
    print(f' {key}: Delta = {Delta[key]*1e3:.1f} mN -> PB1 bindet ab u_{key} = {Delta[key]/need*1e3:.1f} mN '
          f'(u_c(F_min) ~ {Delta[key]/need/ratio*1e3:.1f} mN; Verhaeltnis u_{key}/u_F aus s2 = {ratio})')
