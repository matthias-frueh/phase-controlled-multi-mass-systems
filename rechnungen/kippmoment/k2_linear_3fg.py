"""
k2_linear_3fg.py – Befunde KM-05/KM-06/KM-08: lineare 3-FG-Lösung (Hub z, Kippen a, b) für Einzelzellkräfte,
Summenkraft und Kippmomente; Kipp-Eigenfrequenzen; Einzelzell-Minimum gegen Summe/3.

Fälle (Kontakt): REF (K = 1e4 N/m, C = 16 N·s/m, Engine), STEIF (K = 369 518 N/m, ζ = 0,02 wie Präreg A5,
f_n = 120 Hz), STARR (quasistatisch, H = 1). μ = 1 (Engine) und μ = 0,462 (Laborplan-Mitte: 100 g je Modul
bei M = 0,65 kg), bei STARR zusätzlich μ = 0,4 (Präreg A4).
Geometrien (R_c = 100 mm, Annahme): G0 Module über den Zellen (Präreg A2.5), G60 Module um 60° versetzt auf
R_c, G0h/G60h auf R_c/2 (G60h = Kantenmitten), Z alle Module im Zentrum (= Modell „Summe/3“).
Rahmen: homogene Scheibe mit Radius R_c (ρ_f = R_c/2), Annahme.
Konfigurationen: T (0°, 120°, 240°) Referenzhub; Z (0°, 110°, 240°) Zeltschnittpunkt, Referenzhub;
S (0°, 0°, 0°) mit reduziertem Hub h_S (Dauerkontakt je Zelle, siehe Ausgabe).
"""
import numpy as np
import pandas as pd
from km_modell import Geo, linear, rot_zerlegung, M, MG

R_C = 0.10
GEOS = {'G0': dict(R_m=R_C, dpsi_deg=0.0), 'G60': dict(R_m=R_C, dpsi_deg=60.0),
        'G0h': dict(R_m=R_C / 2, dpsi_deg=0.0), 'G60h': dict(R_m=R_C / 2, dpsi_deg=60.0),
        'Z': dict(R_m=1e-9, dpsi_deg=0.0)}
K_ST = 369518.0
C_ST = 2 * 0.02 * np.sqrt(K_ST * M)
FAELLE = [('REF', 1e4, 16.0, 1.0, False), ('REF', 1e4, 16.0, 0.462, False),
          ('STEIF', K_ST, C_ST, 0.462, False), ('STEIF', K_ST, C_ST, 1.0, False),
          ('STARR', None, None, 1.0, True), ('STARR', None, None, 0.462, True), ('STARR', None, None, 0.4, True)]
F_STAT = MG / 3


def eval_case(geo, phi, K, C, starr, hub=1.0):
    r = linear(geo, phi, K=K if K else 1.0, C=C if C else 0.0, starr=starr, hub=(hub,) * 3)
    F, N = r['F'], r['N']
    Rp, Rm = rot_zerlegung(r['Mxk'], r['Myk'])
    Mabs = np.hypot(r['Mx'], r['My'])
    d = dict(N_min=N.min(), N_max=N.max(), N_pp=N.max() - N.min(),
             Fz_min=F.min(), Fz_min_rel=F.min() / F_STAT, Fz_max=F.max(),
             Fz_pp=(F.max(1) - F.min(1)).max(), Nsum3_min_rel=N.min() / 3 / F_STAT,
             M_min=Mabs.min(), M_mean=Mabs.mean(), M_max=Mabs.max())
    for k in range(1, 7):
        d[f'N{k}'] = 2 * abs(r['Nk'][k])
        d[f'F1_{k}'] = 2 * abs(r['Fk'][0, k])           # Amplitude Zelle 1
        d[f'Mp{k}'] = Rp[k]
        d[f'Mm{k}'] = Rm[k]
    return d, r


def hub_max(geo, phi, K, C, starr, reserve=0.25):
    """größter Hubfaktor h mit min_j F_j ≥ reserve·F_stat (linear, Zellkraft-Abweichung ∝ h)."""
    r = linear(geo, phi, K=K if K else 1.0, C=C if C else 0.0, starr=starr)
    dmin = (r['F'] - geo.F0[:, None]).min()
    return (1 - reserve) * F_STAT / (-dmin) if dmin < 0 else np.inf


if __name__ == '__main__':
    print('=== Eigenfrequenzen im Dauerkontakt (R_c = 100 mm; ρ_f Rahmen-Trägheitsradius) ===')
    print('Fall          μ      Geometrie  ρ_f/R_c   f_Hub [Hz]  f_Kipp [Hz] (2×)   f_Kipp/f  2f/f_Kipp  3f/f_Kipp  ζ_Kipp')
    for name, K, C, mu, starr in FAELLE:
        if starr:
            continue
        for g in ('G0', 'G60h', 'Z'):
            for rf in (0.35, 0.5, 0.7):
                geo = Geo(R_c=R_C, mu=mu, rho_f=rf * R_C, **GEOS[g])
                fr, V = geo.eigenfreq(K, C)
                J = geo.J()[0]
                Kt, Ct = K * R_C**2 / 2, C * R_C**2 / 2
                ft = np.sqrt(Kt / J) / (2 * np.pi)
                zt = Ct / (2 * np.sqrt(Kt * J))
                fh = np.sqrt(K / geo.M) / (2 * np.pi)
                print(f'{name:6s} {mu:6.3f}   {g:5s}     {rf:4.2f}     {fh:8.3f}     {ft:8.3f} ({fr.round(3).tolist()})  '
                      f'{ft/10:6.3f}   {20/ft:6.3f}    {30/ft:6.3f}   {zt:.4f}')
                if mu == 1.0:
                    break                                   # ρ_f ohne Einfluss (M_f = 0)
    print('\nAnalytisch: f_Kipp = f_Hub·R_c/(√2·ρ), J = M·ρ²; bei μ = 1 und Modulen auf R_m = R_c gilt ρ = R_c/√2 → f_Kipp = f_Hub.')

    rows = []
    print('\n=== Reduzierter Hub für die synchrone Phasung S (0°,0°): größter Hubfaktor mit Zellreserve ≥ 25 % ===')
    for name, K, C, mu, starr in FAELLE:
        hs = [hub_max(Geo(R_c=R_C, mu=mu, **GEOS[g]), (0, 0, 0), K, C, starr) for g in GEOS]
        print(f'{name:6s} μ={mu:5.3f}: ' + '  '.join(f'{g}: {h:.3f}' for g, h in zip(GEOS, hs)))
    H_S = 0.15
    print(f'→ verwendet: h_S = {H_S} (reicht für alle Fälle/Geometrien, s. o.)')

    print('\n=== Hubgrenzen für T und Z (Zellreserve ≥ 25 %) ===')
    for name, K, C, mu, starr in FAELLE:
        for cfg, phi in (('T', (0, 120, 240)), ('Z', (0, 110, 240))):
            hs = [hub_max(Geo(R_c=R_C, mu=mu, **GEOS[g]), phi, K, C, starr) for g in GEOS]
            print(f'{name:6s} μ={mu:5.3f} {cfg}: ' + '  '.join(f'{g}: {h:.3f}' for g, h in zip(GEOS, hs)))

    for name, K, C, mu, starr in FAELLE:
        for g, gk in GEOS.items():
            geo = Geo(R_c=R_C, mu=mu, **gk)
            for cfg, phi, hub in (('T', (0, 120, 240), 1.0), ('Z', (0, 110, 240), 1.0), ('S', (0, 0, 0), H_S)):
                d, _ = eval_case(geo, phi, K, C, starr, hub)
                rows.append(dict(fall=name, mu=mu, geo=g, cfg=cfg, hub=hub, **d))
    df = pd.DataFrame(rows)
    df.to_csv('k2_linear_3fg.csv', index=False, float_format='%.6g')
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 300)
    print('\n=== Kernzahlen (linear, alle Zellen bilateral; Fz = Zellkraft, Werte in N bzw. N·m) ===')
    cols = ['fall', 'mu', 'geo', 'cfg', 'hub', 'N_min', 'N_pp', 'Fz_min', 'Fz_min_rel', 'Nsum3_min_rel', 'Fz_max', 'Fz_pp',
            'M_min', 'M_mean', 'M_max']
    print(df[cols].to_string(index=False, float_format=lambda x: f'{x:.4f}'))
    print('\n=== Harmonische am Triphasik-Punkt T: Summe 2|N_k|, Zelle 1 2|F_k|, Moment R+_k / R−_k ===')
    sub = df[df.cfg == 'T']
    cols = ['fall', 'mu', 'geo'] + [f'N{k}' for k in (1, 2, 3, 6)] + [f'F1_{k}' for k in (1, 2, 3)] + \
           [f'Mp{k}' for k in (1, 4)] + [f'Mm{k}' for k in (2, 5)]
    print(sub[cols].to_string(index=False, float_format=lambda x: f'{x:.4f}'))
    print('\n=== Harmonische am Zeltschnittpunkt Z (0°,110°,240°) ===')
    sub = df[df.cfg == 'Z']
    cols = ['fall', 'mu', 'geo'] + [f'N{k}' for k in (1, 2, 3)] + [f'Mp{k}' for k in (1, 2)] + [f'Mm{k}' for k in (1, 2)]
    print(sub[cols].to_string(index=False, float_format=lambda x: f'{x:.4f}'))
    print('\n=== Synchron S (0°,0°,0°), Hub 0,15: Moment ===')
    sub = df[df.cfg == 'S']
    print(sub[['fall', 'mu', 'geo', 'N_pp', 'Fz_pp', 'M_max', 'Fz_min_rel', 'Nsum3_min_rel']].to_string(
        index=False, float_format=lambda x: f'{x:.4g}'))
