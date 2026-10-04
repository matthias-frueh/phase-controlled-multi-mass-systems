"""
k2b_umlaufsinn.py – Befund KM-04 (Ergänzung): Umlaufsinn und Rundheit des Momentvektors am Triphasik-Punkt
mit Kippdynamik. Netto-Umläufe des Vektors (M_x, M_y) je Zyklus um den Ursprung, |M|max/|M|min,
Verhältnis R−_2/R+_1 (rechtsdrehende 2f-Komponente zu linksdrehender Grundkomponente) und |H_t(kω)|.
Linear (Dauerkontakt angenommen; bei Einzelzell-Liftoff nur formal).
"""
import numpy as np
from km_modell import Geo, linear, rot_zerlegung, M

R_C = 0.10
K_ST = 369518.0
C_ST = 2 * 0.02 * np.sqrt(K_ST * M)


def umlaeufe(Mx, My):
    ang = np.unwrap(np.arctan2(My, Mx))
    # geschlossene Kurve: Endwinkel gegen Anfangswinkel inkl. Rückkehr zum Startpunkt
    ang = np.unwrap(np.r_[np.arctan2(My, Mx), np.arctan2(My[0], Mx[0])])
    return (ang[-1] - ang[0]) / (2 * np.pi)


print('Fall    μ      Geo   ρ_f/R_c  f_Kipp[Hz]  |H_t(ω)| |H_t(2ω)|  R+1[N·m]  R−2[N·m]  R−2/R+1  |M|max/min  Umläufe/Zyklus')
for lab, K, C, mu, starr in (('STARR', None, None, 1.0, True), ('STARR', None, None, 0.462, True),
                             ('STEIF', K_ST, C_ST, 0.462, False), ('REF', 1e4, 16.0, 0.462, False),
                             ('REF', 1e4, 16.0, 1.0, False)):
    for g, gk in (('G0', dict(R_m=R_C, dpsi_deg=0)), ('G60h', dict(R_m=R_C / 2, dpsi_deg=60))):
        for rf in ((0.5,) if mu == 1.0 or starr else (0.35, 0.5, 0.7)):
            geo = Geo(R_c=R_C, mu=mu, rho_f=rf * R_C, **gk)
            r = linear(geo, (0, 120, 240), K=K or 1.0, C=C or 0.0, starr=starr)
            q = linear(geo, (0, 120, 240), starr=True)
            Rp, Rm = rot_zerlegung(r['Mxk'], r['Myk'])
            Rpq, Rmq = rot_zerlegung(q['Mxk'], q['Myk'])
            Mabs = np.hypot(r['Mx'], r['My'])
            if starr:
                ft = np.inf
            else:
                J = geo.J()[0]
                ft = np.sqrt(K * R_C**2 / 2 / J) / (2 * np.pi)
            print(f'{lab:5s} {mu:5.3f}  {g:5s}  {rf:4.2f}   {ft:9.2f}   {Rp[1]/Rpq[1]:7.3f}  {Rm[2]/Rmq[2]:7.3f}   '
                  f'{Rp[1]:8.4f}  {Rm[2]:8.4f}  {Rm[2]/Rp[1]:7.3f}   {Mabs.max()/Mabs.min():8.2f}    {umlaeufe(r["Mx"], r["My"]):+.0f}')
print('\nUmläufe > 0: links (gegen den Uhrzeigersinn von oben, Sinn der Phasenfolge 0°→120°→240° bei Modulen in '
      'Linksreihenfolge); < 0: rechts. Ist R−2 > R+1, dreht der Vektor netto zweimal rechts herum je Zyklus.')
