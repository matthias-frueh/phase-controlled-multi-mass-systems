"""
n3_rahmendynamik.py – Befund NR-08: Eigenmoden des gehaltenen Körpers und Übertragung der Moduldyname.

1. Eigenfrequenzen und Modenform: Belegung B (k_a = 10⁶ und 10⁷ N/m), Belegung C (k_a = 10⁶ N/m,
   k_t = 2·10⁴ und 10⁵ N/m), Belegung B mit Versatz A = 0,02 … 0,12 m.
2. Übertragung T(k·f) der Moduldyname auf die Nadeldyname: |T_ii| der sechs Komponenten und größtes
   Übersprechen, k = 1 … 6.
3. Übersprechen in F_x, F_y, M_z am Triphasik-Punkt, wenn der Trägerschwerpunkt 30 mm über O liegt.
4. Abweichung der Nadelkräfte mit Rahmendynamik vom starren Grenzfall; Auslegungsregel f₁ gegen k_max·f
   (Einmassenschwinger-Näherung).

Rahmendynamik heißt hier: der Körper auf elastischen Nadeln (Halterungsmoden), Rahmenstruktur und Fundament starr
und ortsfest. Maße, Steifigkeiten, Trägheiten und ζ = 0,02 (tiefste Mode, steifigkeitsproportional) sind Annahmen;
alle Frequenzen und Übertragungswerte gelten für diese Beispielparameter.
Laufzeit wenige Sekunden; schreibt keine Dateien.
"""
import numpy as np
from nr_modell import (NAMEN, KOMP, A_REF, D_REF, T_KONFIG, S_KONFIG, Koerper, rahmen, antwort, zeit, dyname,
                       amplituden, moden, uebertragung)

np.set_printoptions(precision=4, suppress=True, linewidth=150)
FG = ('u_x', 'u_y', 'u_z', 'θ_x', 'θ_y', 'θ_z')
RHO_BESCHR = 0.10       # Umrechnung Drehwinkel → Weg für die Modenbeschreibung [m]


def kopf(text):
    print('\n' + '=' * 100 + '\n' + text + '\n' + '=' * 100)


def e(a):
    return f'{a:.2e}' if a > 1e-15 else '   0    '


def beschreibung(phi):
    s = np.abs(phi) * np.r_[np.ones(3), np.full(3, RHO_BESCHR)]
    s = s / s.sum()
    i = np.argsort(s)[::-1]
    return f'{FG[i[0]]} {s[i[0]]:.2f}' + (f', {FG[i[1]]} {s[i[1]]:.2f}' if s[i[1]] > 0.05 else '')


kp = Koerper()
kp_hoch = Koerper(r0=(0.0, 0.0, 0.03))

# ───────────────────────────── 1. Moden ─────────────────────────────
kopf('1. Eigenfrequenzen des gehaltenen Körpers (V1-Kandidat, 0,65 kg) [Hz] und dominante Freiheitsgrade')
faelle = [('B, k_a = 1e6', rahmen('B', k_a=1e6)), ('B, k_a = 1e7', rahmen('B', k_a=1e7)),
          ('C, k_a = 1e6, k_t = 2e4', rahmen('C', k_a=1e6, k_t=2e4)),
          ('C, k_a = 1e6, k_t = 1e5', rahmen('C', k_a=1e6, k_t=1e5))]
for name, R in faelle:
    f, Phi = moden(kp, R)
    print(f'{name}:')
    for fi, ph in zip(f, Phi.T):
        print(f'   {fi:8.1f} Hz   {beschreibung(ph)}')
print('Gleich hohe Frequenzen sind entartet; ihre Modenformen sind dann beliebige Mischungen derselben Freiheitsgrade.')
print('\nB, k_a = 1e6 N/m: Eigenfrequenzen über den Versatz A der Wirkungslinien (D = 0,15 m)')
for A in (0.02, 0.04, 0.08, 0.12):
    f, _ = moden(kp, rahmen('B', A=A))
    print(f'   A = {A:.2f} m:  ' + '  '.join(f'{x:6.1f}' for x in f))
print('Die drei Drehmoden werden nur über die Paare mit Hebel A gehalten (Drehsteifigkeit 2·k_a·A²): f_Dreh ∝ A.')

# ───────────────────────────── 2. Übertragung ─────────────────────────────
kopf('2. Übertragung der Moduldyname auf die Nadeldyname: |T_ii(k·f)| und größtes Übersprechen (skaliert mit D)')
S = np.diag([1, 1, 1, 1 / D_REF, 1 / D_REF, 1 / D_REF])
for name, R in faelle:
    print(f'{name}:')
    print('   k   ' + '  '.join(f'{c:>7s}' for c in KOMP) + '   max|T_ij|, i ≠ j')
    for k in range(1, 7):
        T = S @ uebertragung(kp, R, k) @ np.linalg.inv(S)
        off = np.abs(T - np.diag(np.diag(T))).max()
        print(f'   {k}   ' + '  '.join(f'{abs(T[i, i]):7.4f}' for i in range(6)) + f'   {off:.1e}')

# ───────────────────────────── 3. Übersprechen durch Schwerpunkthöhe ─────────────────────────────
kopf('3. Übersprechen in F_x, F_y, M_z am Triphasik-Punkt: Trägerschwerpunkt in O gegen 30 mm über O')
print(f'Schwerpunkthöhe des Körpers z_cm = 0 bzw. {kp_hoch.r_cm[2] * 1e3:.1f} mm')
for name, R in faelle[:2]:
    for kb, lage in ((kp, 'z_cm = 0'), (kp_hoch, 'z_cm > 0')):
        w = dyname(R, antwort(kb, R, T_KONFIG))
        amp = amplituden(w)
        print(f'{name}, {lage}: 2|w_k| k = 1 … 3:  F_x ' + ' '.join(e(a) for a in amp[0, :3])
              + '   F_y ' + ' '.join(e(a) for a in amp[1, :3])
              + '   M_z ' + ' '.join(e(a) for a in amp[5, :3]))
print('Mit dem Schwerpunkt über O koppelt das Kippen an waagerechte Beschleunigungen; F_x und F_y sind dann keine')
print('Nullkomponenten mehr (Kopplung über die Halterung, nicht L3). Starrer Grenzfall: exakt null (n2, Abschnitt 2).')

# ───────────────────────────── 4. Nadelkräfte dynamisch gegen starr ─────────────────────────────
kopf('4. Nadelkräfte mit Rahmendynamik gegen den starren Grenzfall (Belegung B), max. Abweichung über die Periode [N]')
for name, R in faelle[:2]:
    for kname, phi in (('T', T_KONFIG), ('S', S_KONFIG)):
        d = zeit(antwort(kp, R, phi)).real - zeit(antwort(kp, R, phi, starr=True)).real
        print(f'{name}, {kname}: ' + '  '.join(f'{n}={np.abs(dj).max():.4f}' for n, dj in zip(NAMEN, d)))
print('\nAuslegungsregel (Einmassenschwinger, ohne Korrektur): |T − 1| ≈ (k·f/f₁)² ≤ ε  ⇒  f₁ ≥ k_max·f/√ε')
for eps in (1e-2, 1e-3):
    print(f'   ε = {eps:g}, k_max = 6, f = 10 Hz:  f₁ ≥ {60 / np.sqrt(eps):.0f} Hz')
print('Mit gemessener Übertragung (dynamische Kalibrierung H_cal(f) des Gesamtaufbaus) begrenzt deren Unsicherheit,')
print('nicht |T − 1|. Die Moden hängen von Körper und Nadeln ab (Rahmenstruktur hier starr) und gehören zur')
print('Versuchskonfiguration.')
