"""
a4b_bistabilitaet.py – Aufgabe 4, Zusatz: Ist der Kontaktast an den steifen Vorschlägen der einzige
Endzustand? Wurfstarts (Anfangsgeschwindigkeit ż₀ aus der statischen Ruhelage bei t = 0) mit der RK4-μ-Engine.
 R   Gegenprobe Referenz (K = 1e4, C = 16, μ = 1, 10 Hz): (98°,240°), (120°,240°), (148°,240°), ż₀ = 3 m/s,
     15 s, Auswertung 10 s (linear_solver.py meldet dort λ = 0, „monostabil“).
 V1  μ = 0,4615, Hub 8 mm, 10 Hz, K = 1,5e6 N/m, ζ ∈ {0,02; 0,05; 0,1; 0,2}: (120°,240°) und synchron,
     ż₀ ∈ {0,05; 0,1; 0,2; 0,5} m/s, 16 s, Auswertung der letzten 4 s.
 KV  Konvergenz: V2 (ζ = 0,02), (120°,240°), ż₀ = 0,5 m/s, Δt = T/2000 und T/4000, 16 s, letzte 4 s.
Restitutionskoeffizient des Kelvin-Voigt-Kontakts (Stoß ohne Schwerkraft): e = exp(−πζ/√(1−ζ²)).
Ausgabe: a4b_bistabilitaet.csv, a4b_bistabilitaet_ausgabe.txt. Laufzeit ca. 5 min.
"""
import os
import sys
import time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mu_modell as mm  # noqa: E402

M, G, MG = mm.M_REF, mm.G, mm.M_REF * mm.G
out, rows = [], []


def p(s=''):
    print(s, flush=True)
    out.append(s)


t0 = time.time()
p('=== A4b  Wurfstarts: Endzustand Kontaktast oder Hüpfen? ===')
for z in (0.02, 0.05, 0.1, 0.2):
    p(f'  ζ = {z}: Restitutionskoeffizient e = {np.exp(-np.pi * z / np.sqrt(1 - z * z)):.3f}')
# R: Referenz
ph = np.array([[0, 98, 240], [0, 120, 240], [0, 148, 240]], float)
r = mm.rk4_mu(ph, np.ones((3, 3)), 1.0, mm.HUB_REF, 10.0, 1e4, 16.0, t_sim=15.0, t_burn=5.0, v0=3.0)
for j in range(3):
    p(f'R  Referenz ({ph[j, 1]:.0f}°,240°), ż₀ = 3 m/s: λ = {r["liftoff"][j]:.3f} %, F_min = {r["F_min"][j]:.4f} N')
    rows.append(dict(fall='R', zeta=mm.ZETA_REF, punkt=f'({ph[j, 1]:.0f},240)', v0=3.0, lam=r['liftoff'][j],
                     Fmin=r['F_min'][j], Fmax=r['F_max'][j]))
# V1 über ζ
mu, hub, f, K = 0.4615, 8e-3, 10.0, 1.5e6
pts = [('(120,240)', (0, 120, 240)), ('synchron', (0, 0, 0))]
v0s = [0.05, 0.1, 0.2, 0.5]
for zeta in (0.02, 0.05, 0.1, 0.2):
    C = mm.C_of_zeta(zeta, K)
    PH = np.array([pp[1] for pp in pts for _ in v0s], float)
    V0 = np.array([v for _ in pts for v in v0s])
    r = mm.rk4_mu(PH, np.ones((len(PH), 3)), mu, hub, f, K, C, t_sim=16.0, t_burn=12.0, v0=V0)
    for j in range(len(PH)):
        name = pts[j // len(v0s)][0]
        lin = mm.linear_run(PH[j], (1, 1, 1), mu, hub, f, K, C)
        p(f'V1 ζ = {zeta:<4} {name:<10} ż₀ = {V0[j]:.2f} m/s: λ = {r["liftoff"][j]:7.3f} %, F_min = {r["F_min"][j]:.4f} N '
          f'(linear {lin["F_min"]:.4f}), F_max = {r["F_max"][j]:8.2f} N (linear {lin["F_max"]:.2f})')
        rows.append(dict(fall='V1', zeta=zeta, punkt=name, v0=V0[j], lam=r['liftoff'][j], Fmin=r['F_min'][j],
                         Fmax=r['F_max'][j], Fmin_lin=lin['F_min'], Fmax_lin=lin['F_max']))
# Konvergenz
mu2, hub2, f2, K2, z2 = 0.40, mm.HUB_REF, 12.0, 2.5e6, 0.02
C2 = mm.C_of_zeta(z2, K2)
for nper in (2000, 4000):
    r = mm.rk4_mu(np.array([[0, 120, 240]], float), np.ones((1, 3)), mu2, hub2, f2, K2, C2, t_sim=16.0, t_burn=12.0,
                  v0=0.5, n_per=nper)
    p(f'KV V2 ζ = 0,02 (120°,240°) ż₀ = 0,5 m/s, Δt = {1e6 * r["dt"]:.2f} µs: λ = {r["liftoff"][0]:.3f} %, '
      f'F_max = {r["F_max"][0]:.2f} N')
    rows.append(dict(fall='KV', zeta=z2, punkt='(120,240)', v0=0.5, lam=r['liftoff'][0], Fmin=r['F_min'][0],
                     Fmax=r['F_max'][0], n_per=nper))
pd.DataFrame(rows).to_csv(os.path.join(HERE, 'a4b_bistabilitaet.csv'), index=False, float_format='%.6g')
p(f'Rechenzeit {time.time() - t0:.0f} s')
with open(os.path.join(HERE, 'a4b_bistabilitaet_ausgabe.txt'), 'w') as fh:
    fh.write('\n'.join(out) + '\n')
