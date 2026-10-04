"""
a4d_konvergenz.py – Zeitschritt- und Laufzeitprüfung der Hüpf- und E1-Befunde (AUS-12, AUS-13).
Aufruf: python3 a4d_konvergenz.py TEIL
  A: V1 synchron ζ = 0,05, ż₀ = 0,30 und 0,50 m/s, Δt = T/4000, 16 s (letzte 4 s)
  B: V1 synchron ζ = 0,05, ż₀ = 0,30 und 0,50 m/s, Δt = T/2000, 40 s (letzte 4 s)
  C: V1 synchron 14 Hz (E1), Standardstart, Δt = T/4000, 8 s (letzte 5 s);
     V2 Triphasik ζ = 0,02, ż₀ = 0,5 m/s, Δt = T/8000, 16 s (letzte 4 s)
  D: V1 synchron ζ = 0,05, ż₀ = 0,30 und 0,50 m/s, Δt = T/8000, 16 s (letzte 4 s)
Zusätzlich: Stoßfolge im Hüpfzustand (Zeitpunkte der Kontaktbeginne in den letzten 4 s) zur Periodizität.
Ausgabe: a4d_konvergenz_<TEIL>_ausgabe.txt
"""
import os
import sys
import time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mu_modell as mm  # noqa: E402

teil = sys.argv[1]
out = []


def p(s=''):
    print(s, flush=True)
    out.append(s)


def stoss_info(series, dt, f):
    on = (series > 1e-9).astype(int)
    starts = np.where(np.diff(on) == 1)[0] + 1
    if len(starts) < 3:
        return 'keine Stoßfolge'
    iv = np.diff(starts) * dt * f                      # Abstand in Perioden
    return (f'{len(starts)} Kontaktbeginne in {series.size * dt:.1f} s, Abstände [Perioden] '
            f'{np.round(iv[-6:], 4).tolist()}')


t0 = time.time()
V1 = (0.4615, 8e-3, 10.0, 1.5e6, 0.05)
mu, hub, f, K, z = V1
C = mm.C_of_zeta(z, K)
if teil in ('A', 'B', 'D'):
    nper, tsim = {'A': (4000, 16.0), 'B': (2000, 40.0), 'D': (8000, 16.0)}[teil]
    r = mm.rk4_mu(np.zeros((2, 3)), np.ones((2, 3)), mu, hub, f, K, C, t_sim=tsim, t_burn=tsim - 4.0,
                  v0=np.array([0.30, 0.50]), n_per=nper, keep_series=True)
    for j, v in enumerate((0.30, 0.50)):
        p(f'Teil {teil}: V1 synchron ζ = 0,05, ż₀ = {v:.2f} m/s, Δt = {1e6 * r["dt"]:.2f} µs, {tsim:.0f} s: '
          f'λ = {r["liftoff"][j]:.3f} %, F_max = {r["F_max"][j]:.2f} N; {stoss_info(r["series"][:, j], r["dt"], f)}')
elif teil == 'C':
    r = mm.rk4_mu(np.zeros((1, 3)), np.ones((1, 3)), mu, hub, 14.0, K, C, t_sim=8.0, t_burn=3.0, n_per=4000,
                  keep_series=True)
    p(f'Teil C: V1 synchron 14 Hz, Standardstart, Δt = {1e6 * r["dt"]:.2f} µs: λ = {r["liftoff"][0]:.3f} %, '
      f'F_max = {r["F_max"][0]:.2f} N; {stoss_info(r["series"][:, 0], r["dt"], 14.0)}')
    r2 = mm.rk4_mu(np.array([[0, 120, 240]], float), np.ones((1, 3)), 0.40, mm.HUB_REF, 12.0, 2.5e6,
                   mm.C_of_zeta(0.02, 2.5e6), t_sim=16.0, t_burn=12.0, v0=0.5, n_per=8000)
    p(f'Teil C: V2 (120°,240°) ζ = 0,02, ż₀ = 0,5 m/s, Δt = {1e6 * r2["dt"]:.2f} µs: λ = {r2["liftoff"][0]:.3f} %, '
      f'F_max = {r2["F_max"][0]:.2f} N')
p(f'Rechenzeit {time.time() - t0:.0f} s')
with open(os.path.join(HERE, f'a4d_konvergenz_{teil}_ausgabe.txt'), 'w') as fh:
    fh.write('\n'.join(out) + '\n')
