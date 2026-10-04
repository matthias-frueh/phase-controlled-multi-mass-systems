"""
v2b_A4_frequenzgrenzen.py – Gegenprüfung AUS-04 (Präreg A4: Frequenzgrenzen, Zellreserve, F_max) analytisch:
starr gilt F_min/Mg = 1 − ε(f)·G, ε ∝ f², G und Ĝ direkt im Zeitbereich (vk_lib, 20 000 Stützstellen je Periode).
Ausgabe: v2b_A4_frequenzgrenzen_ausgabe.txt
"""
import numpy as np
import vk_lib as vk

M, G = vk.M_REF, vk.G
MG = M * G
hub = vk.HUB_REF
out = []


def p(s=''):
    print(s, flush=True)
    out.append(s)


def GG(ph, w):
    s = vk.System(ph, w, 1.0, hub, 10.0, None, 0.0)
    t = np.arange(20000) / (20000 * 10.0)
    q = s.Q(t) / (MG * vk.eps_of(1.0, hub, 10.0))
    return -q.min(), q.max()


e10 = vk.eps_of(0.4, hub, 10.0)
cases = {'Schnitt': [GG((0, a, 240), (1, 1, 1)) for a in vk.SECTION], 'Einzelmodul': [GG((0, 0, 0), (1, 0, 0))],
         '(0°,180°)': [GG((0, 0, 180), (1, 1, 1))], 'synchron': [GG((0, 0, 0), (1, 1, 1))]}
p(f'A4: starr, μ = 0,4, Referenzhub; ε(10 Hz) = {e10:.5f}, ε(f) = ε(10 Hz)·(f/10)²')
for nm, lst in cases.items():
    Gm = max(g for g, _ in lst)
    Gx = max(x for _, x in lst)
    f_lift = 10 * np.sqrt(1 / (e10 * Gm))
    f_25 = 10 * np.sqrt(0.75 / (e10 * Gm))
    p(f'  {nm:<12} G = {Gm:.5f}: Liftoff ab f = {f_lift:.2f} Hz (zwischen {int(f_lift)} und {int(f_lift)+1} Hz), '
      f'25-%-Grenze f = {f_25:.2f} Hz (ganzzahlig {int(f_25)} Hz); F_max(10 Hz) = {MG*(1+e10*Gx):.4f} N')
for f in (10, 12, 13):
    p(f'  synchrone Reserve bei {f} Hz: {100*(1 - e10*(f/10)**2):.1f} %')
open('v2b_A4_frequenzgrenzen_ausgabe.txt', 'w').write('\n'.join(out) + '\n')
