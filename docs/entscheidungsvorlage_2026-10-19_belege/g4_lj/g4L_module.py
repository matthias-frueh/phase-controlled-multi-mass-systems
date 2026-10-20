# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 2.2 (Option F) und 3.1 (G4-Halte an Lⱼ).
# Zweck: Homogenität der Rauschskalen L1–L3 (Voraussetzung für Pooling, Option F) über 40 PR-#22-Kampagnen.
# Eingaben: Argument 1 = g4L_daten.json (Standard: hier; aus g4L_daten.py).
# Seed: keiner. Laufzeit: gemessen unter 1 s (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B g4L_module.py > g4L_module.out
# Herkunft: Nachprüfung 2 (G4 an Lⱼ). Geändert: Pfad von g4L_daten.json.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
# Homogenität der Rauschskalen L1–L3 (Voraussetzung für Pooling, Option F): log σ̂_Δ je Modul über 40 PR-#22-Kampagnen
import json
import os
import sys
import numpy as np
from scipy import stats
DATEN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'g4L_daten.json')
d22 = json.load(open(DATEN))['d22']
for s in ('N01-A4', 'N01-V1G0', 'N01-V1G60h'):
    for x in ('N', 'F'):
        v = np.log(np.array([[d22[f'{s}|{i}']['sigma_delta'][g][x] for g in ('L1', 'L2', 'L3')] for i in range(40)]))
        fr = stats.friedmanchisquare(*v.T)
        kw = stats.kruskal(*v.T)
        m = np.exp(v.mean(0))
        print(f'{s} {x}: geom. Mittel L1–L3 {np.round(1e3*m,3)} mN, Verhältnis max/min {m.max()/m.min():.3f}, '
              f'Kruskal-Wallis p {kw.pvalue:.3f}, Friedman p {fr.pvalue:.3f}')
