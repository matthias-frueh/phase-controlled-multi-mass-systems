"""
v5e_einzugsschwelle.py – Gegenprüfung AUS-12 (Schwelle ż₀ ≥ 0,30 m/s „bei ζ = 0,02, 0,05 und 0,1“):
Wurfstart aus der statischen Ruhelage, ereignisgesteuert exakt (vk_lib), V1 synchron, 16 s, Fenster letzte 4 s.
 (a) ζ ∈ {0,02; 0,05; 0,1}, Wurf bei t₀ = 0, ż₀ = 0,10 … 0,60 m/s (Schritt 0,02)
 (b) ζ = 0,05, Wurf bei t₀ ∈ {0; T/4; T/2; 3T/4} (Start in anderer Profilphase; umgesetzt als Phasenverschiebung
     aller drei Module um −360°·t₀/T)
Ausgabe: v5e_einzugsschwelle_ausgabe.txt
"""
import time
import numpy as np
import vk_lib as vk

M, G = vk.M_REF, vk.G
mu, hub, f, K = 0.4615, 8.0e-3, 10.0, 1.5e6
out = []


def p(s=''):
    print(s, flush=True)
    out.append(s)


t0 = time.time()
v0s = np.round(np.arange(0.10, 0.6001, 0.02), 3)
for zeta, th_list in ((0.02, [0.0]), (0.05, [0.0, 90.0, 180.0, 270.0]), (0.1, [0.0])):
    C = vk.zeta_to_C(zeta, K)
    for th in th_list:
        res = []
        for v0 in v0s:
            o = vk.System((-th, -th, -th), (1, 1, 1), mu, hub, f, K, C).simulate(16.0, 12.0, v0=v0)
            res.append(o['lam'])
        res = np.array(res)
        hop = v0s[res > 50]
        p(f'ζ = {zeta}, Wurfphase t₀/T = {th/360:.2f}: Hüpfen (λ > 50 %) bei ż₀ = '
          f'{", ".join(f"{v:.2f}" for v in hop) if hop.size else "keinem"}; kleinstes ż₀ mit Hüpfen = '
          f'{hop.min() if hop.size else float("nan"):.2f} m/s (h = {1e3*(hop.min()**2)/(2*G) if hop.size else float("nan"):.1f} mm); '
          f'λ-Werte {sorted(set(np.round(res, 2)))}  ({time.time()-t0:.0f} s)')
open('v5e_einzugsschwelle_ausgabe.txt', 'w').write('\n'.join(out) + '\n')
