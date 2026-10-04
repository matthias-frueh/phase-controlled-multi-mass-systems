"""
a5_qualitativ.py – Aufgabe 5: Welche Aussagen aus AP v2.4 / Präreg v2 skalieren bei μ < 1 und neuem
Arbeitspunkt nur mit ε, welche ändern sich qualitativ?
Vergleicht die Referenz (μ = 1, K = 1e4, C = 16, 10 Hz) mit dem starren Grenzfall und den Vorschlägen
V1–V3 (a3b) in normierten, ε-unabhängigen Kennzahlen: F_min(120°)/Mg-Abstand je ε, ΔF_Zelt und Sekanten je
Mg·ε, Seitenverhältnis s_L/s_R, Lage der Spitze, Schiefe γ₁ an Triphasik/synchron/(0°,180°)/Einzelmodul und
auf dem Schnitt, Spitzenkraftverhältnis A bei 120°, Anteil des Phasenraums (2°-Raster) mit Kontaktast und mit
25-%-Reserve, |H(kω)| für k = 1 … 3 und das Maximum über k.
Zusätzlich: wie stark weichen die normierten Kennzahlen im Bereich ρ ≤ 1/6 vom starren Wert ab (aus
a3a_G_funktionen.csv)?  Laufzeit < 1 min.
"""
import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mu_modell as mm  # noqa: E402

M, G, MG = mm.M_REF, mm.G, mm.M_REF * mm.G
out = []


def p(s=''):
    print(s)
    out.append(s)


def phase_map(mu, hub, f, K, C, step=2.0, per_step=10):
    """F_min über das Phasenraster (φ₂, φ₃) ∈ [0, 360)² mit zyklischer Verschiebung der Einzelmodulantwort."""
    m = int(round(360 / step))
    n = m * per_step
    nk = n // 2 + 1
    c = mm.profile_coeffs(nk, hub, f)
    H, _ = mm.transfer(K, C, f, nk)
    h = np.fft.irfft((mu * M / 3) * H * c * n, n)          # Beitrag eines Moduls zu N − Mg
    R = np.stack([np.roll(h, i * per_step) for i in range(m)])
    Fmin = np.empty((m, m))
    for i in range(m):
        Fmin[i] = MG + ((h + R[i])[None, :] + R).min(1)
    return Fmin


def kennzahlen(name, mu, hub, f, K, C):
    eps = mm.eps_of(mu, hub, f)
    sec = [mm.linear_run((0, q, 240), (1, 1, 1), mu, hub, f, K, C) for q in mm.SECTION_PHI2]
    fmin = np.array([s['F_min'] for s in sec])
    sk = np.array([s['skew'] for s in sec])
    t = sec[10]
    A120 = (t['F_max'] - MG) / (MG - t['F_min'])
    one = mm.linear_run((0, 0, 0), (1, 0, 0), mu, hub, f, K, C)
    syn = mm.linear_run((0, 0, 0), (1, 1, 1), mu, hub, f, K, C)
    zg = mm.linear_run((0, 0, 180), (1, 1, 1), mu, hub, f, K, C)
    Fm = phase_map(mu, hub, f, K, C)
    H, _ = mm.transfer(K, C, f, 200)
    return dict(Fall=name, eps=eps, rho=(0 if K is None else f / mm.f_n(K)),
                F120=fmin[10], G120=(MG - fmin[10]) / (MG * eps), dG=(fmin.max() - fmin.min()) / (MG * eps),
                SL=(fmin[10] - fmin[9]) / 2 / (MG * eps), SR=(fmin[10] - fmin[11]) / 2 / (MG * eps),
                SL_SR=(fmin[10] - fmin[9]) / (fmin[10] - fmin[11]), Spitze=mm.SECTION_PHI2[fmin.argmax()],
                g120=t['skew'], g_min_sec=sk.min(), g_max_sec=sk.max(), g_syn=syn['skew'], g_zg=zg['skew'],
                g_one=one['skew'], A120=A120, kontakt=100 * (Fm > 0).mean(), reserve25=100 * (Fm >= 0.25 * MG).mean(),
                H1=abs(H[1]), H2=abs(H[2]), H3=abs(H[3]), Hmax=abs(H[1:]).max(),
                kHmax=int(np.argmax(abs(H[1:])) + 1), valid_syn=syn['valid'], valid_one=one['valid'])


FAELLE = [('Referenz K=1e4, C=16, μ=1', 1.0, mm.HUB_REF, 10.0, 1e4, 16.0),
          ('starr, μ=1', 1.0, mm.HUB_REF, 10.0, None, 0.0),
          ('starr, μ=0,4 (Präreg A4)', 0.4, mm.HUB_REF, 10.0, None, 0.0),
          ('V1 (ζ=0,05)', 0.4615, 8e-3, 10.0, 1.5e6, mm.C_of_zeta(0.05, 1.5e6)),
          ('V2 (ζ=0,05)', 0.40, mm.HUB_REF, 12.0, 2.5e6, mm.C_of_zeta(0.05, 2.5e6)),
          ('V3 (ζ=0,05)', 0.2308, 8e-3, 14.0, 3.0e6, mm.C_of_zeta(0.05, 3.0e6)),
          ('V4 (ζ=0,02)', 0.4615, 8e-3, 10.0, 3.2e5, mm.C_of_zeta(0.02, 3.2e5)),
          ('Referenz-K, μ=0,4 (nur μ geändert)', 0.4, mm.HUB_REF, 10.0, 1e4, 16.0)]
rows = [kennzahlen(*fa) for fa in FAELLE]
T = pd.DataFrame(rows)
T.to_csv(os.path.join(HERE, 'a5_qualitativ.csv'), index=False, float_format='%.6g')
p('=== A5  Normierte Kennzahlen: Referenz gegen starren Grenzfall und Vorschläge ===')
cols = ['eps', 'rho', 'F120', 'G120', 'dG', 'SL', 'SR', 'SL_SR', 'Spitze', 'g120', 'g_min_sec', 'g_max_sec',
        'g_syn', 'g_zg', 'g_one', 'A120', 'kontakt', 'reserve25', 'H1', 'H2', 'H3', 'Hmax', 'kHmax']
with pd.option_context('display.width', 250, 'display.max_columns', 40):
    p(T.set_index('Fall')[cols].T.to_string(float_format=lambda v: f'{v:.4f}'))
p('Legende: G120 = (Mg − F_min(120°))/(Mg·ε); dG, SL, SR = ΔF_Zelt bzw. 2°-Sekanten je Mg·ε [1, 1/°]; '
  'g = Schiefe γ₁ (g_syn, g_zg, g_one nur aussagekräftig, wenn der Lauf einen Kontaktast hat); A120 = (F_max − Mg)/(Mg − F_min) '
  'bei 120°; kontakt / reserve25 = Anteil des 2°-Phasenrasters mit F_min > 0 bzw. ≥ 0,25·Mg (Summe); kHmax = Harmonische '
  'mit größtem |H|.')
p('Kontaktast vorhanden? ' + '; '.join(f'{r["Fall"]}: synchron {r["valid_syn"]}, Einzelmodul {r["valid_one"]}'
                                       for r in rows))

# Abweichung der normierten Kennzahlen vom starren Wert im Bereich ρ ≤ 1/6
df = pd.read_csv(os.path.join(HERE, 'a3a_G_funktionen.csv'))
r0 = df[df.rho == 0].iloc[0]
p('\nGrößte relative Abweichung normierter Kennzahlen vom starren Grenzfall für ρ ∈ (0, ρ_max] (a3a, Raster 0,001):')
p(f'{"ζ":>5}{"ρ_max":>7}{"G_syn":>8}{"G_ein":>8}{"G_schn":>8}{"ΔG":>8}{"S_L":>8}{"S_R":>8}{"Spitze≠120":>11}')
for zeta in (0.02, 0.05, 0.1, 0.2):
    for rmax in (0.04, 0.05, 0.1, 1 / 6):
        s = df[(df.zeta == zeta) & (df.rho > 0) & (df.rho <= rmax + 1e-9)]
        dev = {q: (s[q] / r0[q] - 1).abs().max() for q in ('G_synchron', 'G_einzel', 'G_schnitt', 'dG', 'SL', 'SR')}
        p(f'{zeta:>5}{rmax:>7.3f}' + ''.join(f'{100 * dev[q]:>7.1f}%' for q in dev) +
          f'{int((s.peak != 120).sum()):>11}')
p('Referenz (ρ = 0,507) zum Vergleich: ' + ', '.join(
    f'{q} {T.iloc[0][q] / T.iloc[1][q] - 1:+.0%}' for q in ('G120', 'dG', 'SL', 'SR')) +
  ' gegenüber starr (gleiches ε)')

with open(os.path.join(HERE, 'a5_qualitativ_ausgabe.txt'), 'w') as fh:
    fh.write('\n'.join(out) + '\n')
