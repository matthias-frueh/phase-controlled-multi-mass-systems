"""
a2_lineares_modell_abgleich.py – Aufgabe 2: lineares Dauerkontaktmodell mit bewegtem Massenanteil μ.
(1) Abgleich der eigenen, analytisch hergeleiteten Lösung (mu_modell.linear_run) mit code/linear_solver.py
    über μ, K, ζ, f und Phasen (F_min_lin, F_max, Schiefe, z_max);
(2) Normierung des Phasenfaktors: N_k(Konfiguration) = Φ_k·N_k(Einzelmodul), Φ_k = Σ e^{−ikφ_j} (ohne 1/3);
    Einzelmodul(μ) ≡ synchron(μ/3);
(3) Ähnlichkeitsgesetz: N/(Mg) − 1 = ε·g̃(t; φ, ρ, ζ) – zwei Parametersätze mit gleichem (ε, ρ, ζ) und
    verschiedenem (μ, Hub, f, K) liefern dieselbe normierte Kraft;
(4) Skalierung von F_min, F_max, |N_k|, ΔF_Zelt und Zeltsekanten mit μ, Hub, K, f (Tabellen).
Laufzeit < 1 min.
"""
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mu_modell as mm  # noqa: E402
import linear_solver as ls  # noqa: E402

M, G, MG, H0 = mm.M_REF, mm.G, mm.M_REF * mm.G, mm.HUB_REF
out = []


def p(s=''):
    print(s)
    out.append(s)


p('=== A2  Lineares Dauerkontaktmodell mit μ: Abgleich und Skalierung ===')
# (1) Abgleich mit linear_solver
rng = np.random.default_rng(20261002)
maxdev = dict(F_min_lin=0.0, F_max=0.0, skew=0.0, z_max=0.0)
ncmp = nvalid = 0
for mu in (0.25, 0.4, 0.7, 1.0):
    for K in (1e4, 1e5, 1e6, None):
        for zeta in (0.02, 0.1):
            for f in (8.0, 10.0, 14.0):
                C = 0.0 if K is None else mm.C_of_zeta(zeta, K)
                for _ in range(4):
                    p2, p3 = rng.uniform(0, 360, 2)
                    a = mm.linear_run((0, p2, p3), (1, 1, 1), mu, H0, f, K, C)
                    b = ls.solve(p2, p3, K, C, mu, f_hz=f)
                    ncmp += 1
                    maxdev['F_min_lin'] = max(maxdev['F_min_lin'], abs(a['F_min'] - b['F_min_lin'][0]))
                    if K is not None:
                        maxdev['z_max'] = max(maxdev['z_max'], abs(a['x_max'] - b['z_max'][0]))
                    if b['valid'][0]:
                        nvalid += 1
                        maxdev['F_max'] = max(maxdev['F_max'], abs(a['F_max'] - b['F_max'][0]))
                        maxdev['skew'] = max(maxdev['skew'], abs(a['skew'] - b['F_skew'][0]))
p(f'(1) {ncmp} Vergleiche (μ ∈ {{0,25; 0,4; 0,7; 1}}, K ∈ {{1e4, 1e5, 1e6, starr}}, ζ ∈ {{0,02; 0,1}}, '
  f'f ∈ {{8, 10, 14}} Hz, je 4 Zufallsphasen), davon {nvalid} mit Kontaktast:')
p('    max. Abweichung ' + ', '.join(f'{k} {v:.1e}' for k, v in maxdev.items()) +
  '  (N bzw. m bzw. dimensionslos; Ursache: analytische vs. FFT-Profilkoeffizienten)')

# (2) Normierung des Phasenfaktors
nk = 6
single = mm.linear_run((0, 0, 0), (1, 0, 0), 0.4, H0, 10.0, 1e5, mm.C_of_zeta(0.1, 1e5))
for ph in [(0, 120, 240), (0, 110, 250), (0, 0, 180), (0, 0, 0)]:
    conf = mm.linear_run(ph, (1, 1, 1), 0.4, H0, 10.0, 1e5, mm.C_of_zeta(0.1, 1e5))
    Phi = mm.phase_factor(ph, (1, 1, 1), nk)[1:5]
    dev = np.abs(conf['Nk'] - Phi * single['Nk']).max()
    p(f'(2) {ph}: max_k |N_k − Φ_k·N_k^(1)| = {dev:.1e} N;  |Φ_1..4| = ' +
      ', '.join(f'{abs(x):.3f}' for x in Phi))
syn3 = mm.linear_run((0, 0, 0), (1, 1, 1), 0.4 / 3, H0, 10.0, 1e5, mm.C_of_zeta(0.1, 1e5))
p(f'    Einzelmodul(μ = 0,4) gegen synchron(μ = 0,4/3): ΔF_min = {abs(single["F_min"] - syn3["F_min"]):.1e} N, '
  f'ΔF_max = {abs(single["F_max"] - syn3["F_max"]):.1e} N')
b = ls.solve(0.0, 0.0, 1e5, mm.C_of_zeta(0.1, 1e5), 0.4 / 3)
p(f'    linear_solver synchron μ/3: F_min = {b["F_min"][0]:.6f} N, eigenes Einzelmodul {single["F_min"]:.6f} N')

# (3) Ähnlichkeitsgesetz
zeta = 0.1
A = dict(mu=1.0, f=10.0, K=1e4)
B = dict(mu=0.5, f=5.0, K=2500.0)                 # gleiches ρ = f/f_n
eA = mm.eps_of(A['mu'], H0, A['f'])
hB = mm.hub_of(eA, B['mu'], B['f'])
for ph in [(0, 120, 240), (0, 0, 0)]:
    ra = mm.linear_run(ph, (1, 1, 1), A['mu'], H0, A['f'], A['K'], mm.C_of_zeta(zeta, A['K']))
    rb = mm.linear_run(ph, (1, 1, 1), B['mu'], hB, B['f'], B['K'], mm.C_of_zeta(zeta, B['K']))
    p(f'(3) {ph}: Satz A (μ=1, f=10, K=1e4, Hub {1e3 * H0:.2f} mm) gegen B (μ=0,5, f=5, K=2500, Hub {1e3 * hB:.2f} mm), '
      f'ε = {eA:.4f}, ρ = {A["f"] / mm.f_n(A["K"]):.4f}: max|N_A − N_B| = {np.abs(ra["N"] - rb["N"]).max():.1e} N')
# Masse: gleiche (ε, ρ, ζ), M verdoppelt → N/(Mg) gleich
M2 = 1.3
ra = mm.linear_run((0, 110, 240), (1, 1, 1), 0.4, H0, 10.0, 1e5, mm.C_of_zeta(zeta, 1e5))
rb = mm.linear_run((0, 110, 240), (1, 1, 1), 0.4, H0, 10.0, 2e5, mm.C_of_zeta(zeta, 2e5, M2), M=M2)
p(f'    M = 0,65 → 1,3 kg bei gleichem ε, ρ, ζ (K verdoppelt): max|N_A/(M_A g) − N_B/(M_B g)| = '
  f'{np.abs(ra["N"] / MG - rb["N"] / (M2 * G)).max():.1e}')


# (4) Skalierung der Kennzahlen
def kennzahlen(mu, hub, f, K, zeta):
    C = 0.0 if K is None else mm.C_of_zeta(zeta, K)
    sec = [mm.linear_run((0, q, 240), (1, 1, 1), mu, hub, f, K, C) for q in mm.SECTION_PHI2]
    fmin = np.array([s['F_min'] for s in sec])
    syn = mm.linear_run((0, 0, 0), (1, 1, 1), mu, hub, f, K, C)
    one = mm.linear_run((0, 0, 0), (1, 0, 0), mu, hub, f, K, C)
    return dict(eps=mm.eps_of(mu, hub, f), rho=0 if K is None else f / mm.f_n(K),
                Fmin120=fmin[10], dF=fmin.max() - fmin.min(), sL=(fmin[10] - fmin[9]) / 2,
                sR=(fmin[10] - fmin[11]) / 2, peak=mm.SECTION_PHI2[fmin.argmax()],
                syn_min=syn['F_min'], syn_max=syn['F_max'], one_min=one['F_min'],
                N1=abs(one['Nk'][0]), N2=abs(one['Nk'][1]), N3=abs(one['Nk'][2]))


p('\n(4) Skalierung (ζ = 0,1 fest; „Einzel |N_k|“ = Betrag der Harmonischen eines Moduls):')
hdr = (f'{"Fall":<34}{"ε":>7}{"ρ":>7}{"F_min120":>9}{"ΔF_Zelt":>9}{"s_L":>8}{"s_R":>8}{"Spitze":>7}'
       f'{"syn_min":>9}{"syn_max":>9}{"ein_min":>9}{"|N1|":>8}{"|N2|":>8}{"|N3|":>8}')
p(hdr)
cases = [('starr μ=0,4 10 Hz Hub_ref', 0.4, H0, 10, None),
         ('starr μ=0,2 10 Hz Hub_ref', 0.2, H0, 10, None),
         ('starr μ=0,4 10 Hz 2·Hub_ref', 0.4, 2 * H0, 10, None),
         ('starr μ=0,4 14,14 Hz Hub_ref', 0.4, H0, 10 * np.sqrt(2), None),
         ('K=1e6 μ=0,4 10 Hz Hub_ref', 0.4, H0, 10, 1e6),
         ('K=1e5 μ=0,4 10 Hz Hub_ref', 0.4, H0, 10, 1e5),
         ('K=1e4 μ=0,4 10 Hz Hub_ref', 0.4, H0, 10, 1e4),
         ('K=1e4 μ=1 10 Hz Hub_ref (Ref.)', 1.0, H0, 10, 1e4)]
for name, mu, hub, f, K in cases:
    k = kennzahlen(mu, hub, f, K, 0.1)
    p(f'{name:<34}{k["eps"]:>7.4f}{k["rho"]:>7.3f}{k["Fmin120"]:>9.4f}{k["dF"]:>9.4f}{k["sL"]:>8.4f}{k["sR"]:>8.4f}'
      f'{k["peak"]:>7.0f}{k["syn_min"]:>9.4f}{k["syn_max"]:>9.4f}{k["one_min"]:>9.4f}{k["N1"]:>8.4f}{k["N2"]:>8.4f}'
      f'{k["N3"]:>8.4f}')
k0 = kennzahlen(0.4, H0, 10, None, 0.1)
p(f'Normierte starre Kennzahlen (je Mg·ε): ΔG_Zelt = {k0["dF"] / (MG * k0["eps"]):.5f}, '
  f'Sekanten {k0["sL"] / (MG * k0["eps"]):.6f} / {k0["sR"] / (MG * k0["eps"]):.6f} 1/°, '
  f'G_syn = {(MG - k0["syn_min"]) / (MG * k0["eps"]):.5f}, G_ein = {(MG - k0["one_min"]) / (MG * k0["eps"]):.5f}, '
  f'(F_max,syn − Mg)/(Mg ε) = {(k0["syn_max"] - MG) / (MG * k0["eps"]):.5f} (TH/TF = {mm.TH / mm.TF:.5f})')

with open(os.path.join(HERE, 'a2_lineares_modell_abgleich_ausgabe.txt'), 'w') as fh:
    fh.write('\n'.join(out) + '\n')
