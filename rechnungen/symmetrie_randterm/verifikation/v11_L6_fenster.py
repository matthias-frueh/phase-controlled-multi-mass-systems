"""v11_L6_fenster.py - L6-Fenstermittel und Randterm aus dem eigenen 60-s-Lauf (v2_laeufe_std_frame.npz):
Fenster ueber 100 / 150 / 300 Perioden und Periodenstruktur von v_S an den Periodenbeginnen (30-60 s)."""
import numpy as np, v_engine as ve
r = np.load('v2_laeufe_std_frame.npz'); names = list(r['names'])
o = {k: r[k] for k in ('S1', 'SW', 'S2', 'S3', 'Fmin', 'Fmax', 'LO', 'vS', 'DFT')}; o['L'] = int(r['L']); o['vSend'] = r['vSend']
for nm in ('L6:g0', 'L6:g2'):
    j = names.index(nm)
    for a, b in [(500, 600), (450, 600), (300, 600)]:
        w = ve.window(o, a, b)
        print(f'{nm} Fenster {a / 10:.0f}-{b / 10:.0f} s ({b - a} Perioden): delta {(w["N1"][j] - ve.MG) / ve.MG * 1e6:+8.1f} ppm, '
              f'R {w["R"][j] / ve.MG * 1e6:+8.1f} ppm, dv_S {w["dvS"][j]:+.4f} m/s, lam {w["lam"][j]:.3f}')
    v = r['vS'][300:600, j]
    for p in (1, 2, 3):
        print(f'   {nm} Periode {p}: std der Teilfolgen', ' '.join('%.2e' % v[k::p].std() for k in range(p)))
