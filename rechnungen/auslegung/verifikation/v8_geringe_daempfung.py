"""
v8_geringe_daempfung.py – Zusatzprüfung zu AUS-08/AUS-10: Robustheit der Vorschläge V1–V3 bei Dämpfungsgraden
unterhalb des von der Gruppe geprüften Bereichs (ζ = 0,005 und 0,01; metallische Wägezellen sind oft schwach gedämpft
– ANNAHME, im Bestand nicht gemessen). Feines K-Raster k_f = 0,70 … 1,30 (Schritt 0,0025), Laufmenge ZUSATZ,
eigener FFT-Löser (n = 32 000).
Ausgabe: v8_geringe_daempfung_ausgabe.txt
"""
import numpy as np
import vk_lib as vk

M, G = vk.M_REF, vk.G
MG = M * G
out = []


def p(s=''):
    print(s, flush=True)
    out.append(s)


V = [('V1', 0.4615, 8.0e-3, 10.0, 1.5e6), ('V2', 0.40, vk.HUB_REF, 12.0, 2.5e6), ('V3', 0.2308, 8.0e-3, 14.0, 3.0e6)]
RUNS = [r for r in vk.runs(5.0) if r[0] in ('schnitt', 'pilot', 'einzel', 'zweiergruppe', 'synchron')]
phs = [r[1] for r in RUNS]
ws = [r[2] for r in RUNS]
sec = [i for i, r in enumerate(RUNS) if r[0] == 'schnitt']
syn = [i for i, r in enumerate(RUNS) if r[0] == 'synchron'][0]
for name, mu, hub, f, K in V:
    for zeta in (0.005, 0.01, 0.02):
        res, dF, pk, kfs = [], [], [], np.round(np.arange(0.70, 1.30001, 0.0025), 4)
        for kf in kfs:
            Kx = K * kf
            N = vk.fft_linear(phs, ws, mu, hub, f, Kx, vk.zeta_to_C(zeta, Kx))
            fmin = N.min(1)
            res.append(fmin.min() / MG)
            Fs = fmin[sec]
            dF.append(Fs.max() - Fs.min())
            pk.append(vk.SECTION[Fs.argmax()])
        res, dF, pk = np.array(res), np.array(dF), np.array(pk)
        N0 = vk.fft_linear([phs[syn]], [ws[syn]], mu, hub, f, K, vk.zeta_to_C(zeta, K))
        p(f'{name} ζ = {zeta}: nominal synchrone Reserve {100*N0.min()/MG:.1f} %; über K ± 30 %: Reserve ≥ {100*res.min():.1f} % '
          f'(k_f = {kfs[res.argmin()]:.4f}), Anteil k_f mit Reserve < 25 %: {100*(res < 0.25).mean():.1f} %; '
          f'ΔF_Zelt ∈ [{dF.min():.3f}; {dF.max():.3f}] N, Anteil < 0,4693 N: {100*(dF < 0.4693).mean():.1f} %; '
          f'Spitze ∈ {sorted(set(pk))}')
open('v8_geringe_daempfung_ausgabe.txt', 'w').write('\n'.join(out) + '\n')
