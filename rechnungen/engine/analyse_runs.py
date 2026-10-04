"""P2/engine – Auswertung segmentierter Läufe: Fenster-Kenngrößen, Periodizität (Poincaré-Schnitt einmal je
Zyklus), Einschwingzeit, Blockstatistik.

Aufruf: python3 analyse_runs.py SPEC.json OUTDIR [CSV_OUT]
Fenster (Zyklen): W_eng = [50,150) (5–15 s, wie Engine), W_20_100 = [200, N), W_50_100 = [500, N),
W_90_100 = [N-100, N), W_orb = letzte floor(800/p)*p Zyklen bei Periode p (ganze Orbitperioden).
Periodizität: streng |Δż| < 1e-6 m/s, |Δz| < 1e-8 m (letzte 100 Zyklen, p <= 60);
locker wie Burn-in-Skript 13.09.: |Δż| < 1e-3 m/s, |Δz| < 1e-4 m.
"""
import sys
import numpy as np
import pandas as pd
import eng
import run_seg


def analyse(spec, outdir):
    r, L = run_seg.load(spec, outdir)
    N = r['S1'].shape[0]
    rows = []
    for k, l in enumerate(L):
        row = dict(name=l['name'], point=l['point'], start=l['start'], phi2=l['phi2'], phi3=l['phi3'],
                   dt_us=r['dt'] * 1e6, T_s=N * eng.T_CYC, t0=l.get('t0', 0.0))
        p_s, ts_s = eng.periodicity(r, k)
        p_l, ts_l = eng.periodicity(r, k, tol_v=1e-3, tol_z=1e-4)
        row.update(per_streng=p_s, t_einschw_streng=ts_s - row['t0'] if p_s > 0 else np.nan,
                   per_locker=p_l, t_einschw_locker=ts_l - row['t0'] if p_l > 0 else np.nan)
        wins = {'eng': (50, 150), '20_100': (200, N), '50_100': (500, N), 'last10': (N - 100, N)}
        if p_s > 0:
            n = (800 // p_s) * p_s
            wins['orb'] = (N - n, N)
        for wn, (c0, c1) in wins.items():
            if c1 > N or c0 < 0:
                continue
            w = eng.window(r, c0, c1)
            for q in ('dF_left_ppm', 'dF_rk4_ppm', 'R_ppm', 'skew', 'lam', 'Fmin', 'Fmax', 'td_per_cyc', 'A'):
                row[f'{q}@{wn}'] = float(w[q][k])
            row[f'rk4mR_N@{wn}'] = float(w['rest_rk4_minus_R_N'][k])
        # Blockstatistik 10-s-Blöcke ab 20 s
        lam_b, sk_b = [], []
        for c0 in range(200, N - 99, 100):
            w = eng.window(r, c0, c0 + 100)
            lam_b.append(float(w['lam'][k])); sk_b.append(float(w['skew'][k]))
        row.update(lam_block_min=min(lam_b), lam_block_max=max(lam_b), skew_block_min=min(sk_b),
                   skew_block_max=max(sk_b))
        # Zustandsklasse grob
        rows.append(row)
    return pd.DataFrame(rows), r, L


if __name__ == '__main__':
    df, r, L = analyse(sys.argv[1], sys.argv[2])
    if len(sys.argv) > 3:
        df.to_csv(sys.argv[3], index=False, float_format='%.6g')
    cols = ['name', 'per_streng', 't_einschw_streng', 'per_locker', 't_einschw_locker', 'lam@eng', 'lam@50_100',
            'skew@eng', 'skew@50_100', 'Fmin@50_100', 'Fmax@eng', 'Fmax@50_100', 'dF_left_ppm@eng', 'dF_left_ppm@50_100',
            'dF_rk4_ppm@50_100', 'R_ppm@50_100', 'lam_block_min', 'lam_block_max']
    with pd.option_context('display.width', 300, 'display.max_columns', 40, 'display.float_format', '{:.4g}'.format):
        print(df[[c for c in cols if c in df]].to_string(index=False))
