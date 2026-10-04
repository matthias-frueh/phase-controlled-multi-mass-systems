"""
v3_randterm.py - Gegenpruefung RT-01/RT-02 mit eigener RK4-Engine (v_engine), 155 s, Standardstart.
Aufruf:  python3 v3_randterm.py frame|com      (Lauf + Speichern)
         python3 v3_randterm.py fit             (nur Auswertung der gespeicherten Laeufe + Tab. 9.3)
Punkte: HS (0; 208,421) wie Archiv, HSx (0; 11*360/19 exakt), S0 (0,0).
Zerlegung je Fenster: delta = (N1 - Mg)/Mg = R + Q + E,  R = M dv_S/(T_w Mg),  Q = N1 - N_RK4,
E = N_RK4 - Mg - R  (in 'com' algebraisch 0).
"""
import sys, time, numpy as np
import v_engine as ve

MG = ve.MG
PTS = [('HS', 0.0, 208.421), ('HSx', 0.0, 11 * 360 / 19), ('S0', 0.0, 0.0)]
WIN_A = [(50, 150), (50, 350), (50, 750), (50, 1550)]            # ab 5 s: 10/30/70/150 s
WIN_B = [(250, 350), (450, 550), (950, 1050), (1450, 1550)]       # je 10 s ab 25/45/95/145 s


def potenzfit(Tw, d):
    p = np.polyfit(np.log(Tw), np.log(np.abs(d)), 1)
    return p[0]


def linfit(Tw, d):
    A = np.vstack([1 / Tw, np.ones_like(Tw)]).T
    c, *_ = np.linalg.lstsq(A, d, rcond=None)
    return c, d - A @ c


if sys.argv[1] in ('frame', 'com'):
    form = sys.argv[1]
    t1 = time.time()
    o = ve.run([p[1] for p in PTS], [p[2] for p in PTS], 1550, form=form)
    print(f'{form}: {time.time() - t1:.1f} s')
    np.savez(f'v3_randterm_{form}.npz', **{k: o[k] for k in ('S1', 'SW', 'S2', 'S3', 'Fmin', 'Fmax', 'LO', 'vS')},
             L=o['L'], vSend=o['vSend'])
    sys.exit()

# ---- Auswertung --------------------------------------------------------------------------------
print('Tab. 9.3 (AP v2.4, Z. 3540-3548): N = 6,333041 / 6,361711 / 6,369854 / 6,373122 N bei T_w = 10/30/70/150 s')
Tw = np.array([10., 30., 70., 150.])
Ntab = np.array([6.333041, 6.361711, 6.369854, 6.373122])
dtab = (Ntab - MG) / MG * 1e6
print('  delta/ppm =', np.round(dtab, 1), ' Potenzfit-Exponent (log|delta| ~ log T_w):', round(potenzfit(Tw, dtab), 4))
c, res = linfit(Tw, dtab)
print(f'  Fit delta = A/T + Q: A = {c[0]:.0f} ppm s, Q = {c[1]:.1f} ppm, max|Residuum| = {np.max(np.abs(res)):.1f} ppm')
for Qx in (0.0, -40.0, -78.0, 78.0):
    print(f'  synthetisch delta = -67377/T + ({Qx:+.0f}): Exponent {potenzfit(Tw, -67377 / Tw + Qx):.4f}')

for form in ('frame', 'com'):
    try:
        r = np.load(f'v3_randterm_{form}.npz')
    except FileNotFoundError:
        print(f'\n[{form}] kein Lauf vorhanden'); continue
    L = int(r['L'])
    o = {k: r[k] for k in ('S1', 'SW', 'S2', 'S3', 'Fmin', 'Fmax', 'LO', 'vS')}
    o['L'] = L; o['vSend'] = r['vSend']
    print(f'\n===== eigene Engine, Formulierung {form} =====')
    for j, (nm, p2, p3) in enumerate(PTS):
        print(f'--- {nm} ({p2}, {p3:.6f}) ---')
        rows = []
        for (a, b) in WIN_A + WIN_B:
            w = ve.window(o, a, b)
            rows.append((a * 0.1, (b - a) * 0.1, w['N1'][j], (w['N1'][j] - MG) / MG * 1e6, w['R'][j] / MG * 1e6,
                         w['Q'][j] / MG * 1e6, w['E'][j], w['dvS'][j], w['lam'][j]))
            x = rows[-1]
            print(f'  Fenster {x[0]:5.1f}+{x[1]:5.1f} s: N1 = {x[2]:.6f} N  delta = {x[3]:+9.1f} ppm  R = {x[4]:+9.1f}  '
                  f'Q = {x[5]:+7.1f}  E = {x[6]:+.2e} N  dv_S = {x[7]:+.5f} m/s  R*T = {x[4] * x[1]:+.0f} ppm s  lam {x[8]:.3f} %')
        A = np.array(rows[:4])
        d = A[:, 3]; Rr = A[:, 4]
        if np.all(np.abs(d) > 1):
            print(f'  Potenzfit delta: {potenzfit(Tw, d):.4f};  Potenzfit R: {potenzfit(Tw, Rr):.5f};  '
                  f'Spannweite R*T: {np.ptp(Rr * Tw) / abs(np.mean(Rr * Tw)) * 100:.3f} %')
            c, res = linfit(Tw, d)
            print(f'  Fit delta = A/T + Q: A = {c[0]:.0f} ppm s, Q = {c[1]:.1f} ppm, max|Res| = {np.max(np.abs(res)):.1f} ppm')
        vc = o['vS'][300:400, j]
        print(f'  sigma_v (v_S an Periodenbeginnen 30-40 s) = {np.std(vc):.2e} m/s;  sigma_v 100-155 s = '
              f'{np.std(o["vS"][1000:1550, j]):.2e} m/s')
