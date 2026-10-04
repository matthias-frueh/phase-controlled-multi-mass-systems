"""s6b_quadratur_tabelle.py - Tabelle und Konvergenzordnungen aus s6_p2_<dt>us.json."""
import json
import numpy as np

DTS = [50, 25, 12.5, 6.25]
res = {dt: json.load(open(f's6_p2_{dt:g}us.json')) for dt in DTS}
pts = ['HS', 'S0', 'L1', 'K1']
cols = [('Q_N1_ppm', 'Q Linksrechteck'), ('Q_TR_ppm', 'Q Trapez'), ('QRK_pred_ppm', 'Q Modell RK4-Stufen'),
        ('QRK_rest_ppm', 'Q - Modell'), ('QJ_pred_ppm', 'Q Modell exakte Abtastung'), ('Q_bound_RK_ppm', 'Schranke J/3 je Aufsetzer'),
        ('delta_RK4_ppm', 'delta RK4-gewichtet'), ('R_N', 'R / N'), ('E_RK4_N', 'E = N_RK4 - Mg - R / N'),
        ('frac_theta_lt_half', 'Anteil theta<1/2'), ('n_touchdowns', 'Aufsetzer im Fenster'), ('J_mean_N', 'mittl. Sprung J / N'),
        ('liftoff', 'lambda / %'), ('skew', 'Schiefe'), ('F_max', 'F_max / N'), ('F_min', 'F_min / N'), ('absN1', '|N_1| / N'),
        ('absN2', '|N_2| / N')]
for p in pts:
    print(f'\n=== {p} ({res[50][p]["phi2"]}, {res[50][p]["phi3"]}), Fenster 35-45 s (100 Perioden) ===')
    print(f'{"Groesse":32s}' + ''.join(f'{"dt=" + format(dt, "g") + " us":>16s}' for dt in DTS))
    for key, lab in cols:
        vals = [res[dt][p][key] for dt in DTS]
        print(f'{lab:32s}' + ''.join(f'{v:16.6g}' for v in vals))
    E = np.array([res[dt][p]['E_RK4_N'] for dt in DTS])
    if np.all(np.abs(E) > 1e-11):
        print('Ordnung E (log2 Verhaeltnis aufeinanderfolgender dt): ' + ' '.join(f'{np.log2(E[i] / E[i + 1]):.2f}' for i in range(3)))
    Qb = np.array([res[dt][p]['Q_bound_RK_ppm'] for dt in DTS])
    if np.all(Qb > 0):
        print('Ordnung der Schranke: ' + ' '.join(f'{np.log2(Qb[i] / Qb[i + 1]):.2f}' for i in range(3)))
        Qr = np.array([abs(res[dt][p]['QRK_rest_ppm']) for dt in DTS])
        print('|Q - Modell| je dt (ppm): ' + ' '.join(f'{x:.3f}' for x in Qr) +
              ';  Ordnung: ' + ' '.join(f'{np.log2(Qr[i] / Qr[i + 1]):.2f}' for i in range(3)))
        Qn = np.array([res[dt][p]['Q_N1_ppm'] for dt in DTS])
        print('Q/Schranke je dt: ' + ' '.join(f'{Qn[i] / Qb[i]:+.3f}' for i in range(4)))
