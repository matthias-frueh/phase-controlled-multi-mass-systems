"""
v4_resonanz_G.py – Gegenprüfung AUS-17 (§5.3(b) schützt (a) nicht vor resonanten hohen Harmonischen) und
Präreg A5 (Spitze bei 106° für μ = 0,4, 10 Hz, f_n = 120 Hz, ζ = 0,02).
Eigener FFT-Löser (vk_lib.fft_linear, n = 32 000), Stichproben mit exakter Zeitbereichslösung nachgeprüft.
ρ = f/f_n auf 0,010 … 0,1667 (Schritt 0,001 plus ρ = 1/6), ζ ∈ {0,02; 0,05; 0,1}; μ = 1, Referenzhub, 10 Hz
(G hängt nur von ρ, ζ ab – Ähnlichkeitsgesetz AUS-07, hier zusätzlich an zwei Sätzen nachgeprüft).
Ausgabe: v4_resonanz_G_ausgabe.txt, v4_resonanz_G.csv
"""
import time
import numpy as np
import pandas as pd
import vk_lib as vk

M, G = vk.M_REF, vk.G
MG = M * G
out = []


def p(s=''):
    print(s, flush=True)
    out.append(s)


t0 = time.time()
f, hub = 10.0, vk.HUB_REF
eps = vk.eps_of(1.0, hub, f)
dG0 = 0.15454
phs = [(0, 0, 0)] + [(0, a, 240.0) for a in vk.SECTION]
ws = [(1, 1, 1)] * len(phs)
# Ähnlichkeitsgesetz-Stichprobe: gleiche (ε, ρ, ζ) mit verschiedenen (μ, Hub, f, K, M)
def Gsyn(mu, hb, ff, rho, zeta, Mx):
    K = Mx * (2 * np.pi * ff / rho) ** 2
    s = vk.System((0, 0, 0), (1, 1, 1), mu, hb, ff, K, vk.zeta_to_C(zeta, K, Mx), M=Mx)
    N = s.periodic_linear()['N']
    return (Mx * G - N.min()) / (Mx * G * vk.eps_of(mu, hb, ff)), (N - Mx * G) / (Mx * G * vk.eps_of(mu, hb, ff))
a1, w1 = Gsyn(1.0, hub, 10.0, 0.1, 0.05, 0.65)
a2, w2 = Gsyn(0.5, hub * 4, 5.0, 0.1, 0.05, 1.3)
p(f'Ähnlichkeit: G_syn(μ=1, Hub_ref, 10 Hz, M=0,65) = {a1:.6f}; G_syn(μ=0,5, 4·Hub_ref, 5 Hz, M=1,3) = {a2:.6f}; '
  f'max|Δg̃| = {np.abs(w1-w2).max():.1e}')
rows = []
rhos = np.concatenate([np.round(np.arange(0.010, 0.1665, 0.001), 4), [1 / 6]])
for zeta in (0.02, 0.05, 0.1):
    for rho in rhos:
        K = M * (2 * np.pi * f / rho) ** 2
        N = vk.fft_linear(phs, ws, 1.0, hub, f, K, vk.zeta_to_C(zeta, K))
        fmin = N.min(1)
        Fs = fmin[1:]
        rows.append(dict(zeta=zeta, rho=rho, Gsyn=(MG - fmin[0]) / (MG * eps), Gsec=(MG - Fs.min()) / (MG * eps),
                         dG=(Fs.max() - Fs.min()) / (MG * eps), peak=vk.SECTION[Fs.argmax()]))
D = pd.DataFrame(rows)
D.to_csv('v4_resonanz_G.csv', index=False, float_format='%.6g')
for zeta in (0.02, 0.05, 0.1):
    s = D[D.zeta == zeta]
    j = s.Gsyn.idxmax()
    p(f'ζ = {zeta}: max G_syn = {s.Gsyn.max():.3f} bei ρ = {s.rho[j]:.4f}; G_syn(ρ = 1/6) = {s.Gsyn.iloc[-1]:.3f}; '
      f'max G_Schnitt = {s.Gsec.max():.3f} (starr 0,395); Spitze ≠ 120° bei ρ = '
      f'{", ".join(f"{r:.3f}({int(pk)}°)" for r, pk in zip(s.rho[s.peak != 120], s.peak[s.peak != 120]))}')
    low = s[s.dG < 0.9 * dG0].rho.values
    if low.size:
        # Bänder zusammenfassen
        bands, b0 = [], low[0]
        for a, b in zip(low[:-1], low[1:]):
            if b - a > 0.0015:
                bands.append((b0, a)); b0 = b
        bands.append((b0, low[-1]))
        p(f'   ΔG < 90 % des starren Werts in: ' + ', '.join(f'{a:.3f}–{b:.3f}' for a, b in bands))
    syn_dev = s[s.rho <= 0.05]
    p(f'   für ρ ≤ 0,05: max |G_syn/1 − 1| = {100*np.abs(syn_dev.Gsyn-1).max():.1f} %, max |ΔG/ΔG_starr − 1| = '
      f'{100*np.abs(syn_dev.dG/dG0-1).max():.1f} %')
# Stichprobe exakt
for zeta, rho in ((0.02, 1 / 6), (0.02, 0.111), (0.05, 1 / 6)):
    K = M * (2 * np.pi * f / rho) ** 2
    N = vk.System((0, 0, 0), (1, 1, 1), 1.0, hub, f, K, vk.zeta_to_C(zeta, K)).periodic_linear(fine=20000)['N']
    p(f'exakt (20 000/Periode) ζ = {zeta}, ρ = {rho:.4f}: G_syn = {(MG-N.min())/(MG*eps):.4f}')
# Präreg A5
K = 369518.0
C = vk.zeta_to_C(0.02, K)
Fm = np.array([vk.System((0, a, 240), (1, 1, 1), 0.4, hub, f, K, C).periodic_linear()['N'].min() for a in vk.SECTION])
p(f'Präreg A5 (μ = 0,4, 10 Hz, K = 369 518 N/m ⇒ f_n = {vk.fn_of(K):.2f} Hz, ζ = 0,02): Maximum bei {vk.SECTION[Fm.argmax()]:.0f}° '
  f'({Fm.max():.4f} N), F_min(120°) = {Fm[10]:.4f} N')
p(f'Rechenzeit {time.time()-t0:.0f} s')
open('v4_resonanz_G_ausgabe.txt', 'w').write('\n'.join(out) + '\n')
