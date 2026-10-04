"""
v7_triphasik_zulaessig.py – Gegenprüfung zweier Aussagen der Gruppe:
 (1) Zusammenfassung/AUS-14: „Die Referenzzahlen (5,33 N, …, positive Triphasik-Schiefe, …) sind Resonanzeffekte von
     2f ≈ f_n“. Prüfung: Am Triphasik-Punkt verschwindet Φ_k = 1 + e^{−ik·120°} + e^{−ik·240°} für k ≠ 3m exakt,
     H(2ω) geht also nicht ein. Nachweis numerisch: Referenz mit H(2ω) := 1, mit H(3ω) := 1, mit H(6ω) := 1.
 (2) AUS-08: Anteil zulässiger ρ ∈ (0, 1/6] für die Laufmenge ZUSATZ (89,2 % bei ζ = 0,02; 94,3 % bei 0,05;
     100 % bei 0,1). Eigene FFT-Rechnung auf demselben Raster ρ = 0,010 … 0,166 (Schritt 0,001).
Ausgabe: v7_triphasik_zulaessig_ausgabe.txt
"""
import numpy as np
from scipy.stats import skew
import vk_lib as vk

M, G = vk.M_REF, vk.G
MG = M * G
out = []


def p(s=''):
    print(s, flush=True)
    out.append(s)


def N_mod(ph, K, C, mu=1.0, hub=vk.HUB_REF, f=10.0, set_one=(), n=32000, nsamp=2000):
    T = 1 / f
    t = np.arange(n) * T / n
    A = np.fft.rfft(vk.acc(t, hub, f)) / n
    A[0] = 0
    k = np.arange(A.size)
    w = 2 * np.pi * f * k
    H = (K + 1j * w * C) / (K - M * w ** 2 + 1j * w * C)
    for j in set_one:
        H[j] = 1.0
    Phi = sum(np.exp(-1j * np.radians(a) * k) for a in ph)
    return MG + np.fft.irfft((mu * M / 3) * H * A * Phi * n, n)[::n // nsamp]


p('=== (1) Triphasik-Punkt (120°, 240°), Referenz K = 1e4, C = 16, μ = 1 ===')
Phi = [abs(1 + np.exp(-1j * k * 2 * np.pi / 3) + np.exp(-1j * k * 4 * np.pi / 3)) for k in range(1, 7)]
p('|Φ_k| für k = 1…6: ' + ', '.join(f'{v:.1e}' for v in Phi))
for lab, so in (('Referenz', ()), ('H(2ω) := 1', (2,)), ('H(3ω) := 1', (3,)), ('H(6ω) := 1', (6,)),
                ('H(3ω), H(6ω) := 1', (3, 6))):
    N = N_mod((0, 120, 240), 1e4, 16.0, set_one=so)
    N118 = N_mod((0, 118, 240), 1e4, 16.0, set_one=so)
    N122 = N_mod((0, 122, 240), 1e4, 16.0, set_one=so)
    p(f'  {lab:<20} F_min(120°) = {N.min():.6f} N, γ₁(120°) = {skew(N):+.4f}, 2°-Sekanten '
      f'{(N.min()-N118.min())/2:.4f}/{(N.min()-N122.min())/2:.4f} N/°')
Nr = vk.System((0, 120, 240), (1, 1, 1), 1.0, vk.HUB_REF, 10.0, None, 0.0).periodic_linear(rigid=True)['N']
p(f'  starr                F_min(120°) = {Nr.min():.6f} N, γ₁(120°) = {skew(Nr):+.4f}')

p('\n=== (2) Anteil zulässiger ρ ∈ (0, 1/6], Laufmenge ZUSATZ (Schnitt, Piloten, Einzelmodul, (0°,180°), synchron) ===')
RUNS = [r for r in vk.runs(5.0) if r[0] in ('schnitt', 'pilot', 'einzel', 'zweiergruppe', 'synchron')]
phs = [r[1] for r in RUNS]
ws = [r[2] for r in RUNS]
sec = [i for i, r in enumerate(RUNS) if r[0] == 'schnitt']
eps = vk.eps_of(1.0, vk.HUB_REF, 10.0)
rhos = np.round(np.arange(0.010, 0.1665, 0.001), 4)
for zeta in (0.02, 0.05, 0.1, 0.2):
    ok = []
    for rho in rhos:
        K = M * (2 * np.pi * 10.0 / rho) ** 2
        N = vk.fft_linear(phs, ws, 1.0, vk.HUB_REF, 10.0, K, vk.zeta_to_C(zeta, K))
        fmin = N.min(1)
        Gset = (MG - fmin.min()) / (MG * eps)
        Fs = fmin[sec]
        dG = (Fs.max() - Fs.min()) / (MG * eps)
        ok.append(0.75 / Gset >= 0.4693 / (MG * dG))
    ok = np.array(ok)
    p(f'  ζ = {zeta}: zulässig {100*ok.mean():.1f} % von {ok.size} Rasterpunkten; unzulässig z. B. ρ = '
      f'{", ".join(f"{r:.3f}" for r in rhos[~ok][:8])}{" …" if (~ok).sum() > 8 else ""}')
open('v7_triphasik_zulaessig_ausgabe.txt', 'w').write('\n'.join(out) + '\n')
