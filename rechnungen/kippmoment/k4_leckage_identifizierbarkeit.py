"""
k4_leckage_identifizierbarkeit.py – Befunde KM-09/KM-10: Leckage in die Summenkraft am Triphasik-Punkt
durch Modulungleichheit und wie sie im Kipp-/Zellkanal erscheint; Identifizierbarkeit.

Störungen (je einzeln, Modul 2 bzw. Zelle 2): Masse +1 %, Hub +1 %, Phase +1°, Zellverstärkung +1 %
(Messfehler), Zellposition 1 mm radial falsch angenommen (Messfehler bei der Momentbildung).
Fälle: STARR μ = 0,462 (Laborplan-Mitte), STEIF μ = 0,462 (K = 369 518 N/m, ζ = 0,02), REF μ = 1.
Geometrien: G0 (Module über Zellen, Präreg A2.5), G60h (Module auf Kantenmitten).
Identifizierbarkeit: Rückrechnung der drei komplexen Modulzeiger g_i,k (Modulkraft je Harmonischer) aus den
drei Zellzeigern über die bekannte Übertragungsmatrix T(kω) (Zelle j ← Modul i), gegen die Summe allein.
"""
import numpy as np
from km_modell import Geo, linear, rot_zerlegung, profil_c, M, MG, OMEGA

R_C = 0.10
K_ST = 369518.0
C_ST = 2 * 0.02 * np.sqrt(K_ST * M)
U_C = 0.0327
FAELLE = [('STARR', None, None, 0.462, True), ('STEIF', K_ST, C_ST, 0.462, False), ('REF', 1e4, 16.0, 1.0, False)]
GEOS = {'G0': dict(R_m=R_C, dpsi_deg=0.0), 'G60h': dict(R_m=R_C / 2, dpsi_deg=60.0)}
PHI0 = (0.0, 120.0, 240.0)


def transfer_matrix(geo, k, K, C, starr):
    """T[j, i]: komplexe Zellkraft j je Einheits-Modulkraftzeiger (m_i·s̈_i = 1·e^{ikωt}) des Moduls i."""
    T = np.zeros((3, 3), complex)
    w = k * OMEGA
    for i in range(3):
        Q = -geo.b[i]                                   # generalisierte Kraft von m_i s̈_i = 1
        if starr:
            T[:, i] = np.linalg.solve(geo.B.T, -Q)
        else:
            D = -w**2 * geo.Mq + 1j * w * C / 3 * geo.BBt + K / 3 * geo.BBt
            q = np.linalg.solve(D, Q)
            T[:, i] = -(K / 3 + 1j * w * C / 3) * (geo.B @ q)
    return T


def run(geo, K, C, starr, phi=PHI0, hub=(1, 1, 1)):
    return linear(geo, phi, K=K if K else 1.0, C=C if C else 0.0, starr=starr, hub=hub)


c = profil_c()
for (fall, K, C, mu, starr) in FAELLE:
    for gname, gk in GEOS.items():
        print(f'\n================ {fall}  μ = {mu}  Geometrie {gname} ================')
        g0 = Geo(R_c=R_C, mu=mu, **gk)
        base = run(g0, K, C, starr)
        Rp0, Rm0 = rot_zerlegung(base['Mxk'], base['Myk'])
        print(f'Basis: 2|N_1|={2*abs(base["Nk"][1]):.2e}  2|N_2|={2*abs(base["Nk"][2]):.2e}  2|N_3|={2*abs(base["Nk"][3]):.4f} N; '
              f'F_min Summe {base["N"].min():.5f} N; R+1={Rp0[1]:.5f} R−1={Rm0[1]:.2e} R+2={Rp0[2]:.2e} R−2={Rm0[2]:.5f} N·m')
        print('Störung              | 2|δN_1| [N] 2|δN_2| [N]  δF_min Σ [N] | R−1 [N·m] R−1/R+1  R+2/R−2 | Ellipse-Achse k=1 [°] | '
              'Zellzeiger 2, k=1: δ|F|/|F|, δarg [°]')
        geo_true = {}
        cases = [('Masse M2 +1 %', dict(geo=Geo(R_c=R_C, mu=mu, m_rel=(1, 1.01, 1), **gk))),
                 ('Hub M2 +1 %', dict(hub=(1, 1.01, 1))),
                 ('Phase M2 +1°', dict(phi=(0, 121, 240))),
                 ('Phase M3 +1°', dict(phi=(0, 120, 241))),
                 ('Zellverst. Z2 +1 %', dict(gain=(1, 1.01, 1))),
                 ('Zellpos. Z2 +1 mm', dict(pos=True))]
        recon = {}
        for lab, opt in cases:
            geo = opt.get('geo', g0)
            if opt.get('pos'):
                xc = g0.xc.copy()
                xc[1] *= (R_C + 1e-3) / R_C
                geo = Geo(R_c=R_C, mu=mu, cell_xy=xc, **gk)
            r = run(geo, K, C, starr, phi=opt.get('phi', PHI0), hub=opt.get('hub', (1, 1, 1)))
            gain = np.asarray(opt.get('gain', (1, 1, 1)), float)
            Fk = r['Fk'] * gain[:, None]                     # gemessene Zellzeiger
            F = r['F'] * gain[:, None]
            Nk = Fk.sum(0)
            # Momente mit der NOMINALEN Zelllage (Messauswertung)
            Mxk, Myk = Fk.T @ g0.xc[:, 1], -(Fk.T @ g0.xc[:, 0])
            Rp, Rm = rot_zerlegung(Mxk, Myk)
            # Ellipse k=1: Hauptachse
            X, Y = Mxk[1], Myk[1]
            th = np.linspace(0, 2 * np.pi, 3601)
            mx, my = 2 * np.real(X * np.exp(1j * th)), 2 * np.real(Y * np.exp(1j * th))
            iax = np.argmax(np.hypot(mx, my))
            ax_deg = np.degrees(np.arctan2(my[iax], mx[iax])) % 180
            dF = Fk[1, 1] / base['Fk'][1, 1]
            print(f'{lab:20s} | {2*abs(Nk[1]-base["Nk"][1]):10.2e}  {2*abs(Nk[2]-base["Nk"][2]):10.2e}  {F.sum(0).min()-base["N"].min():+10.2e} | '
                  f'{Rm[1]:9.2e} {Rm[1]/Rp[1]:8.5f} {Rp[2]/max(Rm[2],1e-30):8.5f} | {ax_deg:7.1f}             | '
                  f'{abs(dF)-1:+.5f}, {np.degrees(np.angle(dF)):+.4f}')
            # Rückrechnung der Modulzeiger aus den Zellzeigern (nominale Übertragungsmatrix, k = 1, 2)
            rec = []
            for k in (1, 2):
                T = transfer_matrix(g0, k, K, C, starr)
                g_hat = np.linalg.solve(T, Fk[:, k])
                g_nom = g0.m * c[k] * np.exp(-1j * k * np.radians(PHI0))
                rel = g_hat / g_nom
                rec.append(rel)
            recon[lab] = rec
        print('Rückrechnung Modulzeiger aus den drei Zellen (ĝ_i/g_i,nom − 1 bzw. arg in °), k = 1 | k = 2:')
        for lab, rec in recon.items():
            s = ' | '.join('  '.join(f'M{i+1}: {abs(rr[i])-1:+.4f}/{np.degrees(np.angle(rr[i])):+.3f}°' for i in range(3)) for rr in rec)
            print(f'  {lab:20s} {s}')
        cond = [np.linalg.cond(transfer_matrix(g0, k, K, C, starr)) for k in (1, 2, 4, 5)]
        print(f'Kondition von T(kω) für k = 1, 2, 4, 5: {np.round(cond, 3).tolist()}')
print(f'\nVergleich: u_c ≤ {U_C} N (PB1, Präreg A4/A8).')
print('Summe allein: eine komplexe Gleichung je Harmonischer (Σ_i δg_i) – welches Modul abweicht, ist nicht bestimmbar;')
print('Masse, Hub und Zellverstärkung wirken als reine Skalenfaktoren (für alle k gleich) und sind aus Kräften allein')
print('nicht unterscheidbar; eine Phasenabweichung dreht den Zeiger um k·δ und ist dadurch unterscheidbar.')
