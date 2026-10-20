# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 3.1.
# Zweck: Erwartungswerte der Ablaufzähler je Kampagne auf einem Gitter u = 0,700 … 1,300 (25 Punkte, je 2000
#   Kampagnen), milde Lesart (streng=False); Grundlage von erwartung30.py, vergleich.py und der Mischungsnäherung
#   in s1_verteilung.py.
# Eingaben: Argument 1 = dieser Ordner (Import von phase1.py), Argument 2 = Ausgabe (gitter.json).
# Annahmen: wie phase1.py; σ̂_ref,c der Zellen mit demselben u wie ε (Näherung).
# Seed: random.Random(20261019). Laufzeit: etwa 4–5 min (Einschätzung aus der Laufzeit je Kampagne; nicht neu
#   gemessen, gitter.json ist übernommen).
# Aufruf: python3 -B gitter.py . gitter.json
# Herkunft: Nachprüfung 1. Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""E[Zähler | u] auf einem Gitter u = ε/(3·√1,5·σ) (σ̂_ref = ε/3, Zellen σ̂_ref,c mit gleichem u)."""
import sys, random, math, json
import numpy as np
sys.path.insert(0, sys.argv[1])
import phase1 as p1
rnd = random.Random(20261019)
seq = p1.plan()
s, sc = math.sqrt(1.5), math.sqrt(0.5)
us = np.round(np.arange(0.70, 1.301, 0.025), 3)
out = {}
for u in us:
    a = np.array([p1.kampagne(3 * s * u, s * u, [sc * u] * 3, rnd, seq) for _ in range(2000)], float)
    out[str(u)] = dict(mittel=a.mean(0).tolist(), var=a.var(0).tolist())
json.dump(dict(felder=['G1', 'G1f', 'R1', 'Xs', 'S1X', 'S1A', 'alarm', 'n', 'nref', 'G1L'], gitter=out),
          open(sys.argv[2], 'w'), indent=0)
