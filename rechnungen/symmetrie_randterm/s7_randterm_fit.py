"""s7_randterm_fit.py - Teil B, Aufgabe 5: Zerlegung delta(T_w) = R(T_w) + Q und Potenzfit.

1. Quelle Tab. 9.3 (AP v2.4, Tab. konvergenz): delta = -6816, -2319, -1042, -530 ppm bei T_w = 10, 30, 70, 150 s.
2. Eigene skalare Reproduktion (s5_randterm_skalar_0_208.421.json, gleiche Engine wie Tab. 9.3).
3. Eigene vektorisierte Laeufe (sr_engine, Arithmetik finesweep) am Hot-Spot mit phi3 = 208.421 und mit
   dem exakten Gitterwert 11*360/19 sowie bei (0, 0): Fenster ab 5 s mit 10/30/70/150 s.
Fits: log|delta| = p log T + c (Potenzfit, kleinste Quadrate in log-log) und delta = A/T + Q (linear)."""
import json
import sys
import numpy as np
import sr_engine as se

T = np.array([10.0, 30.0, 70.0, 150.0])


def fits(delta, label):
    d = np.asarray(delta, float)
    p, c = np.polyfit(np.log(T), np.log(np.abs(d)), 1)
    X = np.vstack([1 / T, np.ones_like(T)]).T
    (A, Q), *_ = np.linalg.lstsq(X, d, rcond=None)
    res = d - (A / T + Q)
    loc = (A / T) / (A / T + Q)
    print(f'{label}: Potenzfit Exponent p = {p:+.4f} (Vorfaktor {np.exp(c) * np.sign(d[0]):.0f} ppm*s^-p); '
          f'delta = A/T + Q: A = {A:.0f} ppm*s, Q = {Q:+.1f} ppm, Residuen {np.round(res, 1)} ppm; '
          f'lokale Steigung -dln|delta|/dlnT bei T=10..150: {np.round(-loc, 3)}')
    return p, A, Q


print('=== Quelle Tab. 9.3 (gerundete Werte) ===')
fits([-6816, -2319, -1042, -530], 'Tab. 9.3')
print('Kontrolle: reines 1/T (Q = 0) ergibt p = -1 exakt; Exponent als Funktion von Q bei A = -67377 ppm*s:')
for Q in (0, -20, -40, -78, -120, +78):
    d = -67377 / T + Q
    p = np.polyfit(np.log(T), np.log(np.abs(d)), 1)[0]
    print(f'   Q = {Q:+4d} ppm -> p = {p:+.4f}')

print('\n=== Eigene skalare Reproduktion (Engine von Tab. 9.3) ===')
js = json.load(open('s5_randterm_skalar_0_208.421.json'))
r = [x for x in js['results'] if x['t_a'] == 5.0]
print(' T/s   N1/N        delta/ppm   R/ppm      Q/ppm    E_RK4/N    dv_S/(m/s)   R*T/(ppm*s)')
for x in r:
    print(f'{x["T"]:5.0f} {x["mean_N1"]:.6f}  {x["delta_ppm"]:9.1f}  {x["R_ppm"]:9.1f}  {x["Q_ppm"]:7.1f}  '
          f'{x["E_RK4_N"]:.2e}  {x["dvcom"]:+.5f}   {x["RT_ppm_s"]:.1f}')
fits([x['delta_ppm'] for x in r], 'skalar')
RT = np.array([x['RT_ppm_s'] for x in r])
print(f'R*T: Mittel {RT.mean():.1f} ppm*s, Spannweite {np.ptp(RT):.1f} ppm*s ({np.ptp(RT) / abs(RT.mean()) * 100:.3f} %); '
      f'Q: Mittel {np.mean([x["Q_ppm"] for x in r]):.1f}, Spannweite {np.ptp([x["Q_ppm"] for x in r]):.1f} ppm')
print('Potenzfit nur an R (ohne Q):', f'{np.polyfit(np.log(T), np.log(np.abs([x["R_ppm"] for x in r])), 1)[0]:+.5f}')
print('Fenster nach dem Einschwingen (10 s):')
for x in js['results']:
    if x['t_a'] > 5:
        print(f'   [{x["t_a"]:.0f},{x["t_b"]:.0f}] s: delta {x["delta_ppm"]:+.1f} ppm = R {x["R_ppm"]:+.2f} + Q {x["Q_ppm"]:+.2f} '
              f'+ E {x["E_RK4_N"] / se.MG * 1e6:+.3f} ppm')
js0 = json.load(open('s5_randterm_skalar_0_0.json'))
print('(0,0) skalar, alle Fenster: ' + '; '.join(
    f'[{x["t_a"]:.0f},{x["t_b"]:.0f}] delta {x["delta_ppm"]:+.1f} R {x["R_ppm"]:+.2f} Q {x["Q_ppm"]:+.2f}' for x in js0['results']))

if len(sys.argv) > 1 and sys.argv[1] == 'vektor':
    pts = [(0.0, 208.421), (0.0, 11 * 360 / 19), (0.0, 0.0)]
    o = se.run([p[0] for p in pts], [p[1] for p in pts], 1550)
    np.savez('s7_vektor_fensterreihe.npz', **{k: v for k, v in o.items() if isinstance(v, np.ndarray)})
if len(sys.argv) > 1:
    o = dict(np.load('s7_vektor_fensterreihe.npz'))
    o['L'] = 2000; o['dt'] = 5e-5
    print('\n=== Vektor-Engine (finesweep-Arithmetik), Fenster ab 5 s ===')
    names = ['HS 208.421', 'HS exakt 11*360/19', '(0,0)']
    for j, nm in enumerate(names):
        rows = []
        for Tw in T:
            w = se.window(o, 50, 50 + int(Tw * 10))
            d = (w['mean_N1'][j] - se.MG) / se.MG * 1e6
            rows.append((Tw, d, w['R'][j] / se.MG * 1e6, (w['mean_N1'][j] - w['mean_RK4'][j]) / se.MG * 1e6,
                         w['dv'][j], (w['mean_RK4'][j] - se.MG - w['R'][j])))
        print(f'-- {nm}')
        for x in rows:
            print(f'   T {x[0]:5.0f} s: delta {x[1]:+9.1f} ppm, R {x[2]:+9.1f}, Q {x[3]:+7.1f}, dv_S {x[4]:+.5f} m/s, E {x[5]:.2e} N')
        if abs(rows[0][1]) > 50:
            fits([x[1] for x in rows], f'   Fit {nm}')
        w = se.window(o, 1450, 1550)
        print(f'   Attraktor 145-155 s: lambda {w["liftoff"][j]:.3f} %, Schiefe {w["skew"][j]:.4f}, F_max {w["F_max"][j]:.3f} N, '
              f'delta {(w["mean_N1"][j] - se.MG) / se.MG * 1e6:+.1f} ppm, Q {(w["mean_N1"][j] - w["mean_RK4"][j]) / se.MG * 1e6:+.1f} ppm')
        vc = o['vcom'][:, j]
        k = np.argmax(np.abs(np.diff(vc[50:]))[::-1] > 1e-3)
        print(f'   v_S(Zyklusbeginn): 5 s {vc[50]:+.4f}, 10 s {vc[100]:+.4f}, 30 s {vc[300]:+.4f}, 150 s {vc[1500]:+.4f} m/s; '
              f'letzte Periode mit |Aenderung| > 1e-3 m/s: t = {(len(vc) - 1 - k) * 0.1:.1f} s')
