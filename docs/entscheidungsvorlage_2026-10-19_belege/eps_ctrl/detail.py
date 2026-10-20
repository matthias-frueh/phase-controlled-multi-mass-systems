# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 1.2 und 3.1.
# Zweck: je Kampagne u und alle Zähler aus phase1b.py (strenge Lesart wie ablauf-3), gespeichert als
#   detail_<variante>_<seed>.npz in Argument 1; Grundlage von auswertung_detail.py.
# Eingaben: 1 = dieser Ordner (Import, Ausgabe), 2 = Variante (gen_F, A8_F, A8), 3 = Zahl der Kampagnen, 4 = Seed.
# Annahmen: wie phase0.py/phase1b.py; kritische Werte des F-Tests fest 1,581 (61 R) bzw. 1,745 (42 R).
# Seeds der Vorlage: gen_F 201, A8_F 202, je 20 000 Kampagnen. Laufzeit: etwa 2 min je Variante (Einschätzung
#   wie s1_verteilung.py). Die npz-Dateien (je 2,7 MB) liegen nicht im Paket; sie entstehen mit
#   python3 -B detail.py . gen_F 20000 201 > log_det_genF.txt  und  python3 -B detail.py . A8_F 20000 202 > log_det_A8F.txt
# Herkunft: Nachprüfung 1. Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""Je Kampagne: u, Zähler (phase1b), gespeichert als npz; strenge Lesart (Code ablauf-3)."""
import sys, random, numpy as np
sys.path.insert(0, sys.argv[1])
import phase0 as p0, phase1b as p1
name, N, seed = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
rng = np.random.default_rng(seed); rnd = random.Random(seed)
if name == 'gen_F':
    o = p0.simuliere(N, rng, 61, 2, True, krit=1.581)
elif name == 'A8_F':
    o = p0.simuliere(N, rng, 42, 2, True, krit=1.745)
elif name == 'A8':
    o = p0.simuliere(N, rng, 42, 2, False)
plan = p1.plan()
z = np.array([p1.kampagne(o['eps'][i], o['sref'][i], list(o['sref_c'][i]), rnd, plan, streng=True) for i in range(N)], float)
np.savez(sys.argv[1] + f'/detail_{name}_{seed}.npz', z=z, u=o['eps'] / (3 * np.sqrt(1.5)), uref=o['sref'] / np.sqrt(1.5),
         betr=o['betr'])
print(name, 'fertig', z.mean(0).round(4).tolist())
