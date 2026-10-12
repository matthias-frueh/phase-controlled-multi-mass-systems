"""
n5_kalibrierrang.py – Befund NR-09: Rang tatsächlicher Kalibrierlasten (statische Kalibrierung des Rahmens).

Anlass: Das Konzept (Fassung vom 11.10.2026, Abschnitt 8) nannte drei Rahmenlagen und das Eigengewicht des Prüflings
als Kalibrierlasten, ohne den Rang der dabei entstehenden Lastvektoren zu prüfen. Eine statische Kalibrierlast ist eine
Kraft F mit Angriffspunkt r; ihr Lastvektor um O ist (F; r × F). Alle sechs Komponenten sind nur kalibrierbar, wenn die
Lastvektoren des tatsächlichen Lastsatzes den Rang 6 haben.

1. Eigengewicht des Prüflings (eine Last am Schwerpunkt) in 1, 2, 3 und 24 Rahmenlagen; dazu Gewichtsstücke an einem
   bzw. zwei weiteren Punkten.
2. Gewichtsstücke an zwölf Stellen: eine Lage, zwei Lagen, drei Lagen mit linear unabhängigen Schwerkraftrichtungen,
   drei Lagen mit koplanaren Schwerkraftrichtungen (Drehen um eine waagerechte Achse, 0°/90°/180°).
3. Lastpunkte auf einer Geraden (Hochachse) in drei unabhängigen Lagen.
4. Eine Lage mit Gewichtsstücken und waagerechten Lasten über Umlenkrollen: je eine in x und y, dann eine zweite in x
   mit anderer Wirkungslinie.

Schwerkraftrichtungen im Rahmenbezug, Lastpunkte und Beträge sind Rechenbeispiele [A]. Rang mit [F; M/l_ref],
l_ref = D = 0,15 m. Laufzeit unter 1 s; schreibt keine Dateien.
"""
import numpy as np
from nr_modell import KOMP, D_REF

np.set_printoptions(precision=4, suppress=True, linewidth=150)
G0 = 9.81
UNTEN, NORD, OST = np.array([0.0, 0.0, -1.0]), np.array([0.0, 1.0, 0.0]), np.array([1.0, 0.0, 0.0])


def lastvektor(r, F):
    r, F = np.asarray(r, float), np.asarray(F, float)
    return np.r_[F, np.cross(r, F)]


def lastsatz_rang(lasten, l_ref=D_REF, tol=1e-9):
    """Rang, Kondition (bei Rang 6) und Basis der nicht angeregten Richtungen eines Lastsatzes [(r, F), …]."""
    W = np.array([lastvektor(r, F) for r, F in lasten]).T
    W[3:] /= l_ref
    U, s, _ = np.linalg.svd(W)
    r = int((s > tol * s[0]).sum())
    return r, (s[0] / s[5] if r == 6 else np.inf), U[:, r:]


def gewichte(punkte, richtungen, m=1.0):
    return [(p, m * G0 * g) for g in richtungen for p in punkte]


def zeile(name, lasten):
    r, kond, blind = lastsatz_rang(lasten)
    if r == 6:
        fehlt = ''
    elif r == 5:
        b = blind[:, 0] * np.sign(blind[np.argmax(np.abs(blind[:, 0])), 0])
        fehlt = '  fehlt: ' + ' '.join(f'{c}{x:+.2f}' for c, x in zip(KOMP, b) if abs(x) > 5e-3)
    else:
        fehlt = f'  fehlen {6 - r} Richtungen'
    kond_s = f'{kond:7.2f}' if np.isfinite(kond) else '      –'
    print(f'{name:72s} {len(lasten):4d}  {r:4d}  {kond_s}{fehlt}')


print(f'{"Lastsatz":72s} Lasten Rang  Kond.  (Kraft in N, Moment/l_ref)')
print('-' * 122)
r_cm = np.array([0.005, -0.003, 0.020])
unabh3 = [UNTEN, NORD, OST]                                   # drei linear unabhängige Schwerkraftrichtungen
koplanar3 = [UNTEN, NORD, -UNTEN]                             # Drehen um die x-Achse: 0°, 90°, 180°
rng = np.random.default_rng(3)
zufall24 = rng.normal(size=(24, 3))
zufall24 /= np.linalg.norm(zufall24, axis=1)[:, None]

print('1. Eigengewicht des Prüflings (0,65 kg am Schwerpunkt r_cm = (5, −3, 20) mm)')
zeile('   eine Rahmenlage', gewichte([r_cm], [UNTEN], 0.65))
zeile('   zwei Lagen', gewichte([r_cm], [UNTEN, NORD], 0.65))
zeile('   drei Lagen, unabhängige Schwerkraftrichtungen', gewichte([r_cm], unabh3, 0.65))
zeile('   24 zufällige Lagen', gewichte([r_cm], list(zufall24), 0.65))
p2, p3 = np.array([0.04, 0.03, -0.05]), np.array([-0.06, 0.05, 0.01])
zeile('   drei Lagen + 0,5-kg-Stück an einem zweiten Punkt (40, 30, −50) mm',
      gewichte([r_cm], unabh3, 0.65) + gewichte([p2], unabh3, 0.5))
zeile('   drei Lagen + Stücke an zwei weiteren Punkten (nicht auf einer Geraden)',
      gewichte([r_cm], unabh3, 0.65) + gewichte([p2, p3], unabh3, 0.5))

stellen = rng.uniform(-0.1, 0.1, (12, 3))
print('2. Gewichtsstücke (1 kg) an zwölf Stellen, gleichverteilt in ±100 mm')
zeile('   eine Rahmenlage', gewichte(stellen, [UNTEN]))
zeile('   zwei Lagen', gewichte(stellen, [UNTEN, NORD]))
zeile('   drei Lagen, unabhängige Schwerkraftrichtungen', gewichte(stellen, unabh3))
zeile('   drei Lagen, koplanar (um x gedreht: 0°, 90°, 180°)', gewichte(stellen, koplanar3))

print('3. Lastpunkte nur auf der Hochachse (z = −100, −50, 50, 100 mm)')
achse = [np.array([0.0, 0.0, z]) for z in (-0.1, -0.05, 0.05, 0.1)]
zeile('   drei Lagen, unabhängige Schwerkraftrichtungen', gewichte(achse, unabh3))

print('4. Eine Rahmenlage: Gewichtsstücke an zwölf Stellen und waagerechte Lasten über Umlenkrollen (je 5 N)')
senkrecht = gewichte(stellen, [UNTEN])
zug_x1 = (np.array([0.0, 0.05, 0.03]), 5.0 * OST)
zug_y = (np.array([0.04, 0.0, -0.02]), 5.0 * NORD)
zug_x2 = (np.array([0.0, -0.06, 0.03]), 5.0 * OST)
zeile('   + je ein Zug in x und in y', senkrecht + [zug_x1, zug_y])
zeile('   + zweiter Zug in x mit anderer Wirkungslinie', senkrecht + [zug_x1, zug_y, zug_x2])

print('\nEine einzelne Last am Schwerpunkt erzeugt nur Lastvektoren (F; r_cm × F) mit Wirkungslinie durch r_cm: Rang')
print('höchstens 3, gleich in wie vielen Lagen. Liegen alle Lastpunkte auf einer Geraden – auch Schwerpunkt und ein')
print('weiteres Stück –, fehlt das Moment um diese Gerade (Rang 5). Drei Rahmenlagen genügen nur mit linear unabhängigen')
print('Schwerkraftrichtungen und mindestens drei Lastpunkten, die nicht auf einer Geraden liegen; koplanare Richtungen')
print('lassen eine Kraftrichtung aus. Eine waagerechte Last je Richtung lässt M_z mit F_x, F_y gekoppelt. Entscheidend ist')
print('der Rang des tatsächlichen Lastsatzes, nicht die Zahl der Lagen.')
