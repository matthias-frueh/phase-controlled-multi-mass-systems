"""
n4_nebenschluss.py – Befund NR-07: Querkräfte, die eine Nadel überträgt, ihre Schnittstelle aber nicht misst.

Belegungen B (versetzt) und A (zentral) mit je einer gemessenen axialen Komponente pro Nadel und einer
ungemessenen Quersteifigkeit k_q = κ·k_a in beiden Querrichtungen (Biegung, Gelenkreibung, Haftreibung an der
Spitze). Quasistatisch (starrer Grenzfall der Verteilung).

1. Statisch: Fehlbetrag der gemessenen Resultierenden gegen die Basislinie (Gewicht, Schwerpunkt 10 mm in x
   versetzt) und Abweichung der Einzelnadel-Mittel von der statisch bestimmten Vorhersage (B).
2. Dynamisch: relativer Fehler der gemessenen Harmonischen F_z,3 und R+₁ (T) sowie F_z,1 und M_y,1 (Einzelmodul 1);
   Faustformel Kraftfehler ≈ 2κ, Momentenfehler ≈ κ·(1 + 2(D/A)²).
3. A (zentral): die Momente gehen vollständig in ungemessene Pfade; Fehlbetrag in F_z.

Laufzeit wenige Sekunden; schreibt keine Dateien.
"""
import numpy as np
from nr_modell import NAMEN, KOMP, A_REF, D_REF, T_KONFIG, S_KONFIG, Koerper, rahmen, antwort, dyname

np.set_printoptions(precision=4, suppress=True, linewidth=150)
KAPPA = (1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1)


def kopf(text):
    print('\n' + '=' * 100 + '\n' + text + '\n' + '=' * 100)


k0 = Koerper()
kp = Koerper(r0=np.array([0.01, 0.0, 0.0]) * k0.M / k0.m0)      # Schwerpunkt 10 mm Richtung Ost
basis = kp.basis()
q_vorhersage = np.linalg.solve(rahmen('B').G, basis)

kopf('1. Belegung B: statischer Fehlbetrag der gemessenen (axialen) Dyname, Schwerpunkt x_cm = 10 mm')
print(f'Basislinie: F_z = {basis[2]:.4f} N, M_y = {basis[4]:.5f} N·m; Vorhersage der Nadelmittel (statisch bestimmt): '
      + '  '.join(f'{n}={q + 0.0:+.3f}' for n, q in zip(NAMEN, q_vorhersage)))
print('     κ        ΔF_z/(M g)     ΔM_y/M_y     max|Δq_Nadel| [N]')
for kap in KAPPA:
    R = rahmen('B', k_q=kap * 1e6)
    lam0 = antwort(kp, R, T_KONFIG, starr=True)[:, 0].real
    w = dyname(R, lam0)
    q = lam0[R.axial]
    print(f'   {kap:7.0e}   {(w[2] - basis[2]) / basis[2]:+12.3e}   {(w[4] - basis[4]) / basis[4]:+10.3e}   '
          f'{np.abs(q - q_vorhersage).max():12.3e}')

kopf('2. Belegung B: relativer Fehler gemessener Harmonischer (starr), Triphasik-Punkt und Einzelmodul 1')
print('     κ        F_z,3 (T)     R+₁ (T)      F_z,1 (E1)    M_y,1 (E1)')
for kap in KAPPA:
    R = rahmen('B', k_q=kap * 1e6)
    zeile = []
    for phi, aktiv, teil in ((T_KONFIG, (1, 1, 1), ('Fz', 3)), (T_KONFIG, (1, 1, 1), ('R+', 1)),
                             (S_KONFIG, (1, 0, 0), ('Fz', 1)), (S_KONFIG, (1, 0, 0), ('My', 1))):
        W = k0.w_mod(phi, aktiv)
        w = dyname(R, antwort(k0, R, phi, starr=True, aktiv=aktiv))
        c, k = teil
        if c == 'R+':
            a, b = w[3, k] + 1j * w[4, k], W[3, k] + 1j * W[4, k]
        else:
            i = KOMP.index(c)
            a, b = w[i, k], W[i, k]
        zeile.append(abs(a - b) / abs(b))
    print(f'   {kap:7.0e}   ' + '   '.join(f'{z:10.3e}' for z in zeile))
print('Faustformel: Kraftfehler ≈ 2κ (vier Nadeln quer gegen zwei axial in derselben Richtung);')
print(f'Momentenfehler ≈ κ·(1 + 2·(D/A)²) = {1 + 2 * (D_REF / A_REF) ** 2:.1f}·κ: zwei Nadelpaare tragen quer mit dem '
      f'Hebel D, eines mit A, axial nur ein Paar mit dem Hebel A.')

kopf('3. Belegung A (zentral): Fehlbetrag in F_z; Momente vollständig in ungemessenen Pfaden')
print('     κ        ΔF_z/(M g)    gemessener Anteil von R+₁ (T)')
for kap in KAPPA:
    R = rahmen('A', k_q=kap * 1e6)
    lam = antwort(kp, R, T_KONFIG, starr=True)
    w0 = dyname(R, lam[:, 0].real)
    w1 = dyname(R, lam[:, 1])
    W = kp.w_mod(T_KONFIG)
    print(f'   {kap:7.0e}   {(w0[2] - basis[2]) / basis[2]:+12.3e}   '
          f'{abs(w1[3] + 1j * w1[4]) / abs(W[3, 1] + 1j * W[4, 1]):.1e}')
print('Die zentrale Belegung hält die Drehungen nur über die ungemessene Quersteifigkeit; deren Kräfte bilden das')
print('Kippmoment vollständig ab, die axialen Schnittstellen sehen davon nichts.')
