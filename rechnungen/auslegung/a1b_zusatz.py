"""
a1b_zusatz.py – Ergänzungen zu Aufgabe 1:
 (a) L2-026: 2°-Sekanten mit H₂ := 1 (Diagnose ohne Resonanz der 2. Harmonischen), eigene Rechnung.
 (b) Massenszenarien: Laborplan (3 × 50 … 150 g bei M ≈ 0,65 kg) und Index 01.09. (0,650 kg je Modul,
     2,2 Hz) in ε ausgedrückt; Hub, der für ΔF_Zelt ≥ 0,4693 N (starr) nötig wäre.
Laufzeit < 10 s.
"""
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mu_modell as mm  # noqa: E402

M, G, MG, H0 = mm.M_REF, mm.G, mm.M_REF * mm.G, mm.HUB_REF
out = []


def p(s=''):
    print(s)
    out.append(s)


# (a) H2 := 1
n = 16000
nk = n // 2 + 1
c = mm.profile_coeffs(nk, H0, 10.0)
H, _ = mm.transfer(1e4, 16.0, 10.0, nk)
H1 = H.copy()
H1[2] = 1.0


def fmin(phi2, Hk):
    Phi = mm.phase_factor((0, phi2, 240), (1, 1, 1), nk)
    return (MG + np.fft.irfft((M / 3) * Hk * c * Phi * n, n)[::8]).min()


for lab, Hk in (('Referenz', H), ('H_2 := 1', H1)):
    f = [fmin(q, Hk) for q in (118, 120, 122)]
    p(f'(a) {lab:<10} 2°-Sekanten 118→120 / 122→120: {(f[1] - f[0]) / 2:.4f} / {(f[1] - f[2]) / 2:.4f} N/°')

# (b) Massenszenarien
dG = 0.154534          # starres ΔG_Zelt je Mg·ε (a3a)
p('\n(b) Massenszenarien (Egg-Profil TH = 0,65, starr):')
for lab, m_mod, Mtot, f, hub in (('Laborplan 3×50 g', 0.05, 0.65, 10.0, H0),
                                 ('Laborplan 3×100 g', 0.10, 0.65, 10.0, H0),
                                 ('Laborplan 3×150 g', 0.15, 0.65, 10.0, H0),
                                 ('Index 01.09.: 3×0,650 kg, m0 = 0, 2,2 Hz', 0.65, 1.95, 2.2, H0)):
    mu = 3 * m_mod / Mtot
    eps = mm.eps_of(mu, hub, f)
    dF = dG * Mtot * G * eps
    eps_need = 0.4693 / (dG * Mtot * G)
    p(f'  {lab:<42} μ = {mu:.3f}, M = {Mtot:.3f} kg, f = {f} Hz, Hub {1e3 * hub:.2f} mm: ε = {eps:.4f}, '
      f'ΔF_Zelt = {dF:.3f} N, synchrone Reserve 1 − ε = {100 * (1 - eps):.1f} %; für ΔF_Zelt ≥ 0,4693 N nötig '
      f'ε ≥ {eps_need:.4f} ⇒ Hub ≥ {1e3 * mm.hub_of(eps_need, mu, f):.1f} mm')
p(f'  Verhältnis der Anregung (10/2,2)² = {(10 / 2.2) ** 2:.2f}')
with open(os.path.join(HERE, 'a1b_zusatz_ausgabe.txt'), 'w') as fh:
    fh.write('\n'.join(out) + '\n')
