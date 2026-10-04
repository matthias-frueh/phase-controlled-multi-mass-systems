"""
v2b_rho_empfindlichkeit.py – Empfindlichkeit der linearen Zellreserven gegen die ANNAHME Rahmen-Trägheitsradius ρ_f
(Gruppe: ρ_f = R_c/2 fest). (a) STEIF μ = 0,462, G0: Spannweite der Zellreserve über alle Präreg-Lauftypen bei
10/12 Hz; (b) REF μ = 0,462, G0, T: lineare kleinste Zellkraft (negativ -> Zell-Liftoff im nichtlinearen Modell).
"""
import numpy as np
from vf_modell import Geom, MG3, K_REF, C_REF, K_STEIF, C_STEIF
from vf_modell import zell_koeff, synth, starr_zeit
R = 0.10
# (dieselben Definitionen wie in v2_linear_zellkraefte.py, hier wiederholt, damit v2 nicht mitläuft)
LAUF = {'Einzel1': ((0, 0, 0), (1, 0, 0)), 'Paar0': ((0, 0, 0), (1, 1, 0)), 'Paar120': ((0, 120, 0), (1, 1, 0)),
        'Paar180': ((0, 180, 0), (1, 1, 0)), 'synchron': ((0, 0, 0), (1, 1, 1)), '(0,0,180)': ((0, 0, 180), (1, 1, 1)),
        'P110/250': ((0, 110, 250), (1, 1, 1)), 'P130/230': ((0, 130, 230), (1, 1, 1)),
        'P110/252': ((0, 110, 252), (1, 1, 1))}
SCHNITT = [((0, p, 240), (1, 1, 1)) for p in range(100, 141, 2)]


def zellkraefte(geo, phi, fall, f=10.0, hub=(1, 1, 1), n=8000):
    K, C = (K_REF, C_REF) if fall == 'REF' else (K_STEIF, C_STEIF)
    Fk = zell_koeff(geo, phi, K, C, f=f, hub=hub, kmax=400)
    return geo.F0[:, None] + synth(Fk, n), Fk

for rho in (0.35, 0.5, 0.6, 1 / np.sqrt(2)):
    g = Geom(0.462, R_c=R, rho_f=rho * R)
    txt = []
    for f in (10.0, 12.0):
        vals = {n: zellkraefte(g, ph, 'STEIF', f=f, hub=hb, n=4000)[0].min() / MG3 for n, (ph, hb) in LAUF.items()}
        vals['Schnitt'] = min(zellkraefte(g, ph, 'STEIF', f=f, hub=hb, n=4000)[0].min() for ph, hb in SCHNITT) / MG3
        lo = min(vals, key=vals.get)
        txt.append(f'{f:.0f} Hz: {100*min(vals.values()):.1f}…{100*max(vals.values()):.1f} % (min bei {lo}, synchron {100*vals["synchron"]:.1f} %)')
    F, _ = zellkraefte(g, (0, 120, 240), 'REF')
    print(f'ρ_f = {rho:.4f} R_c | STEIF μ=0,462 G0: ' + ' | '.join(txt) + f' || REF μ=0,462 G0 T: lineare Zelle min {F.min():+.4f} N ({100*F.min()/MG3:+.1f} %), N_min {F.sum(0).min():.4f} N')
