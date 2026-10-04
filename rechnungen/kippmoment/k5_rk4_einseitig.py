"""
k5_rk4_einseitig.py – Befunde KM-06/KM-07: nichtlineares 3-FG-RK4 mit einseitigem Kontakt JE ZELLE.
Frage: Wo die lineare Lösung eine negative Zellkraft vorhersagt (Einzelzell-Liftoff), was passiert dann mit
Summenkraft (Engine-Observablen), Zellkräften und Kippmoment? Wo die lineare Lösung positiv bleibt: stimmt
die nichtlineare Lösung überein (λ = 0)?
Start: Standardstart (statisches Gleichgewicht, Ruhe, wie Engine) und für die Liftoff-Fälle zusätzlich
„linearer Orbit“ (5 s bilateral eingeschwungen, dann einseitig weiter; Zustand bei t = 50 T übernommen).
Auswertung: 10 s nach 5 s Burn-in (wie Engine).  Aufruf: python3 k5_rk4_einseitig.py [REF|STEIF]
"""
import sys
import numpy as np
import pandas as pd
from scipy.stats import skew
from km_modell import Geo, rk4, linear, harmonische, momente, rot_zerlegung, M, MG, N_PER, DT

R_C = 0.10
K_ST = 369518.0
C_ST = 2 * 0.02 * np.sqrt(K_ST * M)
GK = {'G0': dict(R_m=R_C, dpsi_deg=0.0), 'G60': dict(R_m=R_C, dpsi_deg=60.0),
      'G0h': dict(R_m=R_C / 2, dpsi_deg=0.0), 'G60h': dict(R_m=R_C / 2, dpsi_deg=60.0)}
CFG = {'T': ((0, 120, 240), 1.0), 'Z': ((0, 110, 240), 1.0), 'S': ((0, 0, 0), 0.15)}
GRUPPEN = {
    'REF': (1e4, 16.0, [(1.0, 'G0', 'T'), (1.0, 'G0', 'Z'), (1.0, 'G0', 'S'), (1.0, 'G0h', 'T'), (1.0, 'G60h', 'T'),
                        (0.462, 'G0', 'T'), (0.462, 'G0', 'Z'), (0.462, 'G60h', 'T'), (0.462, 'G0', 'S')]),
    'STEIF': (K_ST, C_ST, [(0.462, 'G0', 'T'), (0.462, 'G0', 'Z'), (0.462, 'G0', 'S'), (0.462, 'G60', 'T'),
                           (1.0, 'G0', 'T'), (1.0, 'G0', 'Z')]),
}
F_STAT = MG / 3


def auswertung(geo, F, lin):
    """F: (n_rec × 3) Zellkräfte."""
    N = F.sum(1)
    Mx, My = momente(geo, F)
    Rp, Rm = rot_zerlegung(harmonische(Mx), harmonische(My))
    Nk = harmonische(N)
    Mabs = np.hypot(Mx, My)
    per = np.max(np.abs(F[-5 * N_PER:] - F[-6 * N_PER:-N_PER]))       # Abweichung von T-Periodizität
    d = dict(N_mean=N.mean(), N_min=N.min(), N_max=N.max(), N_skew=skew(N), lam_sum=100 * np.mean(N < 1e-9),
             Fz_min=F.min(), Fz_max=F.max(), lam_zelle_max=100 * np.max(np.mean(F < 1e-9, 0)),
             lam_zelle_mittel=100 * np.mean(F < 1e-9), Fz_mean_max_abw=np.max(np.abs(F.mean(0) - lin['F0'])),
             M_mean=Mabs.mean(), M_min=Mabs.min(), M_max=Mabs.max(), Mx_mean=Mx.mean(), My_mean=My.mean(),
             Rp1=Rp[1], Rm1=Rm[1], Rp2=Rp[2], Rm2=Rm[2], Rp4=Rp[4], Rm5=Rm[5],
             N1=2 * abs(Nk[1]), N2=2 * abs(Nk[2]), N3=2 * abs(Nk[3]), periodizitaet=per,
             lin_N_min=lin['N'].min(), lin_Fz_min=lin['F'].min(), lin_N_skew=skew(np.tile(lin['N'], 5)))
    return d


if __name__ == '__main__':
    grp = sys.argv[1] if len(sys.argv) > 1 else 'REF'
    K, C, cases = GRUPPEN[grp]
    geos = [Geo(R_c=R_C, mu=mu, **GK[g]) for mu, g, cfg in cases]
    phis = [CFG[cfg][0] for mu, g, cfg in cases]
    hubs = [(CFG[cfg][1],) * 3 for mu, g, cfg in cases]
    lins = [linear(geo, ph, K=K, C=C, hub=hb) for geo, ph, hb in zip(geos, phis, hubs)]
    rows, series = [], {}
    # Standardstart
    r = rk4(geos, phis, K=K, C=C, hubs=hubs)
    for i, (mu, g, cfg) in enumerate(cases):
        d = auswertung(geos[i], r['F'][:, i, :], lins[i])
        rows.append(dict(gruppe=grp, mu=mu, geo=g, cfg=cfg, start='standard', **d))
        series[f'{grp}_{mu}_{g}_{cfg}_standard'] = r['F'][:3 * N_PER, i, :]
    # linearer Orbit für Fälle mit linearem Zell-Liftoff
    idx = [i for i in range(len(cases)) if lins[i]['F'].min() < 0]
    if idx:
        rb = rk4([geos[i] for i in idx], [phis[i] for i in idx], K=K, C=C, hubs=[hubs[i] for i in idx],
                 T_sim=5.0, T_burn=5.0, bilateral=True, store=False)
        ru = rk4([geos[i] for i in idx], [phis[i] for i in idx], K=K, C=C, hubs=[hubs[i] for i in idx],
                 q0=rb['q'], v0=rb['v'])
        for jj, i in enumerate(idx):
            mu, g, cfg = cases[i]
            d = auswertung(geos[i], ru['F'][:, jj, :], lins[i])
            rows.append(dict(gruppe=grp, mu=mu, geo=g, cfg=cfg, start='lin_orbit', **d))
            series[f'{grp}_{mu}_{g}_{cfg}_lin_orbit'] = ru['F'][:3 * N_PER, jj, :]
    df = pd.DataFrame(rows)
    df.to_csv(f'k5_rk4_einseitig_{grp}.csv', index=False, float_format='%.6g')
    np.savez_compressed(f'k5_rk4_einseitig_{grp}_reihen.npz', **series)
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 50)
    print(f'=== Gruppe {grp}: K = {K:.0f} N/m, C = {C:.3f} N·s/m; Zellreserve-Bezug F_stat = {F_STAT:.4f} N ===')
    print(df[['mu', 'geo', 'cfg', 'start', 'lin_Fz_min', 'Fz_min', 'lam_zelle_max', 'lam_zelle_mittel', 'lam_sum',
              'lin_N_min', 'N_min', 'N_max', 'N_mean', 'lin_N_skew', 'N_skew', 'periodizitaet']].to_string(
        index=False, float_format=lambda x: f'{x:.4f}'))
    print()
    print(df[['mu', 'geo', 'cfg', 'start', 'M_min', 'M_mean', 'M_max', 'Mx_mean', 'My_mean', 'Rp1', 'Rm1', 'Rp2', 'Rm2',
              'N1', 'N2', 'N3', 'Fz_mean_max_abw']].to_string(index=False, float_format=lambda x: f'{x:.4f}'))
