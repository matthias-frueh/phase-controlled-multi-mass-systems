"""
v6_mu_abgleich_kontaktanteil.py – Gegenprüfung AUS-06 (linear_solver mit μ ≠ 1: Übertragungsfunktion mit Gesamtmasse,
Normierung des Phasenfaktors) und AUS-14 (Kontaktanteil der Phasenebene bei K = 1e4 N/m über μ).
 Teil 1: exakte Zeitbereichslösung (vk_lib) gegen code/linear_solver.solve für 40 Zufallsfälle (μ, K, ζ, f, Phasen).
 Teil 2: Kontaktanteil (F_min > 0 und x_max < 0) im 1°-Raster aus der exakten Einzelmodulantwort (3600 Stützstellen
         je Periode, zyklische Verschiebung; Superposition N − Mg = Σ_j h(t − τ_j)), μ = 1; 0,5; 0,4.
Ausgabe: v6_mu_abgleich_kontaktanteil_ausgabe.txt
"""
import time
import numpy as np
import vk_lib as vk
import linear_solver as ls

M, G = vk.M_REF, vk.G
MG = M * G
out = []


def p(s=''):
    print(s, flush=True)
    out.append(s)


t0 = time.time()
rng = np.random.default_rng(20261002)
dmax = dict(F_min=0.0, F_max=0.0)
for i in range(40):
    mu = rng.uniform(0.2, 1.0)
    K = 10 ** rng.uniform(4, 6.5)
    zeta = rng.choice([0.02, 0.05, 0.1, 0.2])
    f = rng.choice([8.0, 10.0, 12.0, 14.0])
    p2, p3 = rng.uniform(0, 360, 2)
    C = vk.zeta_to_C(zeta, K)
    r = vk.System((0, p2, p3), (1, 1, 1), mu, vk.HUB_REF, f, K, C).periodic_linear(nsamp=2000)
    rl = ls.solve(p2, p3, K, C, mu, f_hz=f)
    for q, a, b in (('F_min', r['N'].min(), rl['F_min_lin'][0]), ('F_max', r['N'].max(), np.max(
            [rl['F_max'][0] if rl['valid'][0] else r['N'].max()]))):
        dmax[q] = max(dmax[q], abs(a - b))
p(f'Teil 1: 40 Zufallsfälle μ ∈ [0,2; 1], K ∈ [1e4; 3e6], ζ ∈ {{0,02…0,2}}, f ∈ {{8…14}} Hz: '
  f'max|ΔF_min| = {dmax["F_min"]:.1e} N, max|ΔF_max| (gültige Fälle) = {dmax["F_max"]:.1e} N')
p('  (linear_solver: N = Mg + μ·M·irfft(P·Φ/3·H), H mit Gesamtmasse M; vk_lib: Q = Σ (μM/3)·a_j, Gesamtmasse M im '
  'Impulssatz – unabhängig hergeleitet)')

# Teil 2
n = 3600
for mu in (1.0, 0.5, 0.4):
    s = vk.System((0, 0, 0), (1, 0, 0), mu, vk.HUB_REF, 10.0, 1e4, 16.0)
    r = s.periodic_linear(nsamp=n)
    h = r['N'] - MG                    # Beitrag eines Moduls
    xg = r['x'] + MG / 1e4             # dynamische Auflagerkoordinate eines Moduls
    # Modul j mit Phase φ_j: Beitrag h(t − τ_j) = roll(h, +10·φ_j[°])
    R = np.stack([np.roll(h, 10 * i) for i in range(360)])
    X = np.stack([np.roll(xg, 10 * i) for i in range(360)])
    ok = 0
    for i in range(360):
        Fmin = MG + (h[None, :] + R[i][None, :] + R).min(1)
        xmax = -MG / 1e4 + (xg[None, :] + X[i][None, :] + X).max(1)
        ok += int(((Fmin > 0) & (xmax < 0)).sum())
    p(f'Teil 2: μ = {mu}: Kontaktanteil (1°-Raster, F_min > 0 und x_max < 0) = {100*ok/360**2:.2f} %  ({time.time()-t0:.0f} s)')
open('v6_mu_abgleich_kontaktanteil_ausgabe.txt', 'w').write('\n'.join(out) + '\n')
