# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 5.1 (Faktor 2,2–2,4 bei L0, 1,03–1,21 bei L1).
# Zweck: Zerlegung der Lauf-zu-Lauf-Varianz einer Summenharmonischen (d2) mit den tatsächlichen Summenharmonischen,
#   Faktor der Überschätzung, wenn der erfasste Phasenanteil als Laufrauschen gezogen würde (analytisch).
# Eingaben: Argument 1 = struktur.json (Standard: hier). Seed: keiner. Laufzeit: gemessen unter 1 s (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B d2_nach.py > d2_nach.out
# Herkunft: Nachprüfung 6. Geändert: Pfad von struktur.json.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
# NL6: d2 (Zerlegung der Lauf-zu-Lauf-Varianz einer Summenharmonischen im Kombinationslauf) mit den tatsächlichen
# Summenharmonischen der Einzelmodule aus generator/systeme.antworten (struktur.json, a4_struktur.py), k = 1 … k_max.
# Komponenten wie agenda/d2_zerlegung.py (Szenariorauschmodell rauschen.stufe, Jitter 0,2°, Versatz 0,05°, N_z = 100,
# f = 10 Hz, f_s = 6400 Hz, σ_zelle = 0,02/√3 N). Gesamtvarianz E|dN_k|² der Summe:
#   Amplitude 3·a²·|N|², Phasenrest 3·(k·p)²·|N|², erfasst 2·k²·(v² + j²/N_z)·|N|², weiß 3 Zellen × 2 × σ_h².
# Faktor = √(gesamt / (gesamt − erfasst)): Überschätzung der Residuenstreuung, wenn der erfasste Anteil als Laufrauschen
# gezogen würde. Zusätzlich die Variante, in der die Pilotkovarianz Re/Im getrennt betrachtet wird (nicht nötig, isotrop).
import json
import os
import sys
import numpy as np
S = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'struktur.json')))
stufen = {'L0': (0.0, 0.02), 'L1': (0.003, 0.03), 'L2': (0.01, 0.10), 'L3': (0.03, 0.30)}
jit, v, Nz, f, fs = 0.2, 0.05, 100, 10.0, 6400.0
sz = 0.02 / np.sqrt(3)
sh = sz * np.sqrt(2.0 / (fs * Nz / f))
rad = np.pi / 180
alt = {1: 1.30, 2: 0.43, 3: 0.18}
for name in ('A4', 'V1-G0'):
    N = np.array(S[name]['summe_abs'][0])
    km = S[name]['k_max']
    print(f'== {name} (k_max = {km}); |N_k| Summe Einzelmodul [N]:', np.round(N[:km], 4))
    for st, (a, p) in stufen.items():
        fak, ant = [], []
        for k in range(1, km + 1):
            n2 = N[k - 1] ** 2
            A = 3 * a**2 * n2; P = 3 * (k * p * rad)**2 * n2
            E = 2 * k**2 * (v**2 + jit**2 / Nz) * rad**2 * n2; W = 6 * sh**2
            tot = A + P + E + W
            fak.append(np.sqrt(tot / (tot - E))); ant.append(E / tot)
        print(f'  {st}: Faktor k=1..{km}: ' + ' '.join(f'{x:.2f}' for x in fak) + '   Anteil erfasst k=1..3: ' + ' '.join(f'{x:.2f}' for x in ant[:3]))
    if name == 'A4':
        print('  d2 mit 1,30/0,43/0,18 N (alt), L0/L1 k=1..3:')
        for st in ('L0', 'L1'):
            a, p = stufen[st]
            r = []
            for k in (1, 2, 3):
                n2 = alt[k]**2
                A = 3 * a**2 * n2; P = 3 * (k * p * rad)**2 * n2
                E = 2 * k**2 * (v**2 + jit**2 / Nz) * rad**2 * n2; W = 6 * sh**2
                tot = A + P + E + W; r.append(np.sqrt(tot / (tot - E)))
            print(f'    {st}: ' + ' '.join(f'{x:.3f}' for x in r))
# Grenzwert ohne weißes Rauschen und ohne Amplitude: √(1 + 2(v² + j²/N_z)/(3p²))
for st, (a, p) in stufen.items():
    print(f'  Grenzwert {st} (W → 0, a = 0): {np.sqrt(1 + 2*(v**2 + jit**2/Nz)/(3*p**2)):.3f}')
