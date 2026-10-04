"""
v3_arbeitspunkte.py – Gegenprüfung AUS-10 (Vorschläge V1–V5), AUS-08 (Robustheit), AUS-15 (ganze Phasenebene),
AUS-14 (normierte Kennzahlen an V1–V3).
 Teil A: exakte Zeitbereichslösung (Schießverfahren, vk_lib) für alle Lauftypen, ζ = 0,02/0,05/0,1; Vergleich mit
         a3b_vorschlaege.csv der Gruppe.
 Teil B: Robustheit mit feinem K-Raster (k_f = 0,70…1,30 in Schritten 0,0025 statt 0,05) × ζ ∈ {0,02; 0,05; 0,1; 0,2},
         eigener FFT-Löser (vk_lib.fft_linear, zuvor gegen Teil A geprüft).
 Teil C ausgelagert nach v3c_phasenebene.py.
Ausgabe: v3_arbeitspunkte_ausgabe.txt, v3_arbeitspunkte.csv, v3_robustheit_fein.csv
"""
import time
import numpy as np
import pandas as pd
from scipy.stats import skew
import vk_lib as vk

M, G = vk.M_REF, vk.G
MG = M * G
out = []


def p(s=''):
    print(s, flush=True)
    out.append(s)


V = [('V1', 0.4615, 8.0e-3, 10.0, 1.5e6), ('V2', 0.40, vk.HUB_REF, 12.0, 2.5e6), ('V3', 0.2308, 8.0e-3, 14.0, 3.0e6),
     ('V4', 0.4615, 8.0e-3, 10.0, 3.2e5), ('V5', 0.60, vk.HUB_REF, 12.0, 2.5e6)]
RUNS = vk.runs(5.0)
t0 = time.time()
rows = []
p('=== Teil A: exakte lineare Lösung je Lauftyp (Reserve = kleinstes F_min/Mg; Zelle = Summe/3 als Annahme) ===')
p(f'{"V":<3}{"ζ":>5}{"ε":>7}{"f_n":>7}{"3f/fn":>7}{"Einz":>7}{"Paar":>7}{"Syn":>7}{"0/180":>7}{"Pil":>7}{"Schn":>7}'
  f'{"ΔF_Z":>7}{"s_L":>8}{"s_R":>8}{"Sp.":>5}{"Fmax/3":>7}{"G120":>7}{"γ1(120)":>8}{"|H2|":>7}')
for name, mu, hub, f, K in V:
    for zeta in (0.02, 0.05, 0.1):
        C = vk.zeta_to_C(zeta, K)
        res, Fmax = {}, {}
        sec = []
        for grp, ph, w in RUNS:
            r = vk.System(ph, w, mu, hub, f, K, C).periodic_linear(nsamp=2000)
            N = r['N']
            res[grp] = min(res.get(grp, 9e9), N.min() / MG)
            Fmax[grp] = max(Fmax.get(grp, -9e9), N.max())
            if grp == 'schnitt':
                sec.append(N)
        Fm = np.array([s.min() for s in sec])
        eps = vk.eps_of(mu, hub, f)
        w2 = 2 * np.pi * f * 2
        H2 = abs((K + 1j * w2 * C) / (K - M * w2 ** 2 + 1j * w2 * C))
        d = dict(V=name, zeta=zeta, eps=eps, fn=vk.fn_of(K), r3=3 * f / vk.fn_of(K), **{f'res_{g}': v for g, v in res.items()},
                 dF=Fm.max() - Fm.min(), sL=(Fm[10] - Fm[9]) / 2, sR=(Fm[10] - Fm[11]) / 2,
                 peak=vk.SECTION[Fm.argmax()], cellmax=max(Fmax.values()) / 3, Fmax_syn=Fmax['synchron'],
                 G120=(MG - Fm[10]) / (MG * eps), skew120=float(skew(sec[10])), H2=H2)
        rows.append(d)
        p(f'{name:<3}{zeta:>5}{eps:>7.3f}{d["fn"]:>7.1f}{d["r3"]:>7.3f}' + ''.join(
            f'{100*res[g]:>6.1f}%' for g in ('einzel', 'paar', 'synchron', 'zweiergruppe', 'pilot', 'schnitt')) +
          f'{d["dF"]:>7.3f}{d["sL"]:>8.4f}{d["sR"]:>8.4f}{d["peak"]:>5.0f}{d["cellmax"]:>7.3f}{d["G120"]:>7.4f}'
          f'{d["skew120"]:>8.3f}{H2:>7.3f}')
A = pd.DataFrame(rows)
A.to_csv('v3_arbeitspunkte.csv', index=False, float_format='%.6g')
# Vergleich mit der Gruppe
grp = pd.read_csv('../a3b_vorschlaege.csv')
grp['V'] = grp['name'].str[:2]
mg = A.merge(grp, on=['V', 'zeta'], suffixes=('', '_g'))
cols = ['res_einzel', 'res_paar', 'res_synchron', 'res_zweiergruppe', 'res_pilot', 'res_schnitt', 'dF', 'sL', 'sR']
dev = {c: np.abs(mg[c] - mg[c + '_g']).max() for c in cols}
dev['cellmax'] = np.abs(mg['cellmax'] - mg['cell_max_sum3']).max()
dev['skew120'] = np.abs(mg['skew120'] - mg['skew120_g']).max()
p('Größte Abweichung zur Gruppe (a3b_vorschlaege.csv) über alle 15 Fälle: ' +
  ', '.join(f'{c} {v:.1e}' for c, v in dev.items()))
p(f'(Rechenzeit bisher {time.time()-t0:.0f} s)')

# ── Teil B: Robustheit, feines K-Raster ──
p('\n=== Teil B: Robustheit über K ∈ [0,70; 1,30]·K_nenn (Schritt 0,0025) × ζ ∈ {0,02; 0,05; 0,1; 0,2}, FFT-Löser ===')
# Kontrolle FFT gegen exakt
nm, mu, hub, f, K = V[0]
C = vk.zeta_to_C(0.02, K)
ph = [r[1] for r in RUNS]
ws = [r[2] for r in RUNS]
Nf = vk.fft_linear(ph, ws, mu, hub, f, K, C)
Ne = np.array([vk.System(a, b, mu, hub, f, K, C).periodic_linear()['N'] for a, b in zip(ph, ws)])
p(f'Kontrolle FFT gegen exakt (V1, ζ = 0,02, alle {len(RUNS)} Läufe): max|ΔN| = {np.abs(Nf-Ne).max():.2e} N')
ZUS = [i for i, r in enumerate(RUNS) if r[0] in ('schnitt', 'pilot', 'einzel', 'zweiergruppe', 'synchron')]
PFL = [i for i, r in enumerate(RUNS) if r[0] in ('schnitt', 'pilot', 'einzel')]
SEC = [i for i, r in enumerate(RUNS) if r[0] == 'schnitt']
rrows = []
for name, mu, hub, f, K in V:
    phz = [RUNS[i][1] for i in ZUS]
    wz = [RUNS[i][2] for i in ZUS]
    secpos = [ZUS.index(i) for i in SEC]
    pflpos = [ZUS.index(i) for i in PFL]
    for kf in np.round(np.arange(0.70, 1.30001, 0.0025), 4):
        for zeta in (0.02, 0.05, 0.1, 0.2):
            Kx = K * kf
            N = vk.fft_linear(phz, wz, mu, hub, f, Kx, vk.zeta_to_C(zeta, Kx))
            fmin = N.min(1)
            Fs = fmin[secpos]
            rrows.append(dict(V=name, kf=kf, zeta=zeta, res_zus=fmin.min() / MG, res_pfl=fmin[pflpos].min() / MG,
                              dF=Fs.max() - Fs.min(), peak=vk.SECTION[Fs.argmax()]))
R = pd.DataFrame(rrows)
R.to_csv('v3_robustheit_fein.csv', index=False, float_format='%.6g')
coarse = np.isclose((R.kf * 20) % 1, 0) | np.isclose((R.kf * 20) % 1, 1)
for name in R.V.unique():
    s = R[R.V == name]
    sc = s[coarse[s.index]]
    key = 'res_pfl' if name == 'V5' else 'res_zus'
    j = s[key].idxmin()
    jd = s.dF.idxmin()
    p(f'  {name} ({"PFLICHT" if name=="V5" else "ZUSATZ"}): fein: Reserve ≥ {100*s[key].min():.1f} % (bei k_f = {s.kf[j]:.4f}, ζ = {s.zeta[j]}), '
      f'ΔF_Zelt ≥ {s.dF.min():.3f} N (k_f = {s.kf[jd]:.4f}, ζ = {s.zeta[jd]}), Spitze ∈ {sorted(set(s.peak))}; '
      f'grob (Schritt 0,05): Reserve ≥ {100*sc[key].min():.1f} %, ΔF_Zelt ≥ {sc.dF.min():.3f} N, Spitze ∈ {sorted(set(sc.peak))}')
    for z in (0.02, 0.05):
        sz = s[s.zeta == z]
        p(f'      ζ = {z}: Reserve min {100*sz[key].min():.1f} %, ΔF_Zelt min {sz.dF.min():.3f} N, '
          f'Anteil k_f mit ΔF_Zelt < 0,4693 N: {100*(sz.dF < 0.4693).mean():.1f} %, Spitze ≠ 120° bei {100*(sz.peak != 120).mean():.1f} %')
p(f'(Rechenzeit bisher {time.time()-t0:.0f} s)')

p(f'Rechenzeit {time.time()-t0:.0f} s')
open('v3_arbeitspunkte_ausgabe.txt', 'w').write('\n'.join(out) + '\n')
