"""
v3c_phasenebene.py – Gegenprüfung AUS-15: kleinstes lineares F_min über die ganze Phasenebene (3°-Raster) an V1–V3
(ζ = 0,05), eigener FFT-Löser mit 16 000 Stützstellen je Periode (Kontrolle gegen exakte Lösung am synchronen Punkt).
Ausgabe: v3c_phasenebene_ausgabe.txt
"""
import time
import numpy as np
import vk_lib as vk

M, G = vk.M_REF, vk.G
MG = M * G
out = []


def p(s=''):
    print(s, flush=True)
    out.append(s)


V = [('V1', 0.4615, 8.0e-3, 10.0, 1.5e6), ('V2', 0.40, vk.HUB_REF, 12.0, 2.5e6), ('V3', 0.2308, 8.0e-3, 14.0, 3.0e6)]
t0 = time.time()
g = np.arange(0, 360, 3.0)
P2, P3 = np.meshgrid(g, g, indexing='ij')
phs = np.column_stack([np.zeros(P2.size), P2.ravel(), P3.ravel()])
for name, mu, hub, f, K in V:
    C = vk.zeta_to_C(0.05, K)
    ex = vk.System((0, 0, 0), (1, 1, 1), mu, hub, f, K, C).periodic_linear()['N'].min()
    fmin = np.empty(phs.shape[0])
    for i in range(0, phs.shape[0], 400):
        sl = slice(i, i + 400)
        fmin[sl] = vk.fft_linear(phs[sl], np.ones((len(phs[sl]), 3)), mu, hub, f, K, C, n=16000).min(1)
    j = fmin.argmin()
    p(f'{name}: min F_min = {fmin.min():.4f} N ({100*fmin.min()/MG:.1f} % Mg) bei ({phs[j,1]:.0f}°, {phs[j,2]:.0f}°) '
      f'[exakt synchron {ex:.4f} N]; Anteil F_min > 0: {100*(fmin > 0).mean():.1f} %; '
      f'Anteil F_min ≥ 0,25·Mg: {100*(fmin >= 0.25*MG).mean():.1f} %  ({time.time()-t0:.0f} s)')
open('v3c_phasenebene_ausgabe.txt', 'w').write('\n'.join(out) + '\n')
