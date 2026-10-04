"""s5_oc_tabelle.py – fasst die H1-OC-Läufe (s2_h1_oc_L*_n20_n020_k9.csv) zu einer Tabelle zusammen.
Ausgabe: s5_oc_tabelle.csv und Markdown-Tabellen nach stdout (für PROTOKOLL.md, STA-08/09/10).
"""
import glob
import numpy as np
import pandas as pd

d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob('s2_h1_oc_L*_n20_n020_k9.csv'))], ignore_index=True)
d.to_csv('s5_oc_tabelle.csv', index=False)
d['szen'] = d.szenario + np.where(d.x > 0, ' ' + (100 * d.x).round(0).astype(int).astype(str) + ' %', '')
lev = d.groupby('level').agg(rauschen=('rauschen', 'first'), u_F=('u_F_mN', 'median'), u_N2=('u_N2_mN', 'median'),
                             Delta_F=('Delta_F_mN', 'median'), Delta_N2=('Delta_N2_mN', 'median'), nu=('nu_F', 'median'))
print('Rauschstufen (Median über Szenarien):')
print('| Stufe | Lauf-zu-Lauf-Streuung [A] | u_c(F_min) [mN] | u_c(N₂) [mN] | Δ_F/u_c | Δ_N2/u_c | ν_eff |')
print('|---|---|---|---|---|---|---|')
for L, r in lev.iterrows():
    print(f'| L{L} | {r.rauschen} | {r.u_F:.2f} | {r.u_N2:.2f} | {r.Delta_F / r.u_F:.0f} | {r.Delta_N2 / r.u_N2:.0f} | {r.nu:.0f} |')
order = ['exakt', 'kopplung 1 %', 'kopplung 3 %', 'kopplung 10 %', 'N2 1 %', 'N2 3 %', 'N2 10 %', 'drift 1 %', 'drift 3 %']
for col, lab in (('P_falsifiziert', 'P(falsifiziert)'), ('P_bestaetigt', 'P(bestätigt)'),
                 ('P_nicht_entscheidbar', 'P(nicht entscheidbar)'), ('P_IUT_bestaetigt', 'P(bestätigt) nach IUT-TOST-Vorschlag'),
                 ('P_MET_falsifiziert', 'P(falsifiziert) nach Mindesteffekt-Vorschlag')):
    p = d.pivot_table(index='szen', columns='level', values=col).reindex(order)
    print(f'\n{lab} (Zeilen: Szenario, Spalten: Rauschstufe)')
    print('| Szenario | ' + ' | '.join(f'L{c}' for c in p.columns) + ' |')
    print('|---|' + '---|' * len(p.columns))
    for s, r in p.iterrows():
        print(f'| {s} | ' + ' | '.join(f'{v:.3f}' if np.isfinite(v) else '–' for v in r.values) + ' |')
print('\nKorrelation z⁰/z¹ und 95-%-Quantil von max|z⁰| bei exakter Superposition:')
e = d[d.szenario == 'exakt']
for _, r in e.iterrows():
    print(f'  L{r.level}: corr = {r.corr_z0_z1:.2f}, q95 max|z0| = {r.q95_maxz0:.2f}, P(|z0|>c an mind. einem Test) = {r.P_sig_z0:.3f}, '
          f'P(|z1|>c) = {r.P_sig_z1:.3f}, P(fals) = {r.P_falsifiziert:.3f}, P(best) = {r.P_bestaetigt:.3f}, P(PB1) = {r.P_PB1:.3f}')
