"""
a4c_einzugsbereich.py – Aufgabe 4, Zusatz: Schwelle der Wurfgeschwindigkeit ż₀, oberhalb derer der Körper
nicht in den Kontaktast zurückkehrt (V1 synchron, ζ = 0,05; V2 Triphasik, ζ = 0,02).
16 s je Lauf, Auswertung der letzten 4 s. Fallhöhe h = ż₀²/(2g) als Anschauung.
Ausgabe: a4c_einzugsbereich.csv, a4c_einzugsbereich_ausgabe.txt. Laufzeit ca. 2 min.
"""
import os
import sys
import time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mu_modell as mm  # noqa: E402

G = mm.G
out, rows = [], []


def p(s=''):
    print(s, flush=True)
    out.append(s)


t0 = time.time()
cases = [('V1 synchron ζ=0,05', (0.4615, 8e-3, 10.0, 1.5e6, 0.05), (0, 0, 0)),
         ('V2 (120°,240°) ζ=0,02', (0.40, mm.HUB_REF, 12.0, 2.5e6, 0.02), (0, 120, 240))]
v0s = np.array([0.25, 0.30, 0.35, 0.40, 0.45])
p('=== A4c  Einzugsbereich des Kontaktasts (Wurfstart aus der statischen Ruhelage bei t = 0) ===')
for name, (mu, hub, f, K, zeta), ph in cases:
    C = mm.C_of_zeta(zeta, K)
    vv = v0s if 'V1' in name else np.array([0.10, 0.20, 0.30, 0.40, 0.50])
    r = mm.rk4_mu(np.tile(ph, (len(vv), 1)), np.ones((len(vv), 3)), mu, hub, f, K, C, t_sim=16.0, t_burn=12.0, v0=vv)
    for j, v in enumerate(vv):
        p(f'  {name:<24} ż₀ = {v:.2f} m/s (h = {1e3 * v * v / (2 * G):5.1f} mm): λ = {r["liftoff"][j]:7.3f} %, '
          f'F_max = {r["F_max"][j]:8.2f} N')
        rows.append(dict(fall=name, v0=v, h_mm=1e3 * v * v / (2 * G), lam=r['liftoff'][j], Fmax=r['F_max'][j]))
pd.DataFrame(rows).to_csv(os.path.join(HERE, 'a4c_einzugsbereich.csv'), index=False, float_format='%.6g')
p(f'Rechenzeit {time.time() - t0:.0f} s')
with open(os.path.join(HERE, 'a4c_einzugsbereich_ausgabe.txt'), 'w') as fh:
    fh.write('\n'.join(out) + '\n')
