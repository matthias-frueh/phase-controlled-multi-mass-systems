# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 5.1 (Summenharmonische von A4).
# Zweck: Summen- und Zellharmonische der Einzelmodule von A4, V1-G0, V1-G60h aus generator/systeme.antworten
#   (deterministisch); Ausgabe struktur.json für ident.py und d2_nach.py.
# Eingaben: Code des Repositorys (code/pcmms_auswertung); Argument 1 = Ausgabe (Standard struktur.json hier).
# Seed: keiner. Laufzeit: gemessen unter 1 s (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: PCMMS_REPO=<auszug 0f63187> python3 -B a4_struktur.py struktur.json > a4_struktur.out
# Herkunft: Nachprüfung 6 (Laufphasenstreuung). Geändert: Code- und Ausgabepfad.
# Repository-Wurzel: drei Ebenen über diesem Ordner; abweichend über die Umgebungsvariable PCMMS_REPO (etwa ein
#   Auszug von main 0f63187: git archive 0f63187 code docs | tar -x -C <ziel>).
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
# NL6: Summen- und Zellharmonische der Einzelmodule der Bezugssysteme (deterministisch, generator/systeme.antworten),
# nur gelesen/ausgewertet, keine Kampagne. Aufruf: python3 -B (keine __pycache__ im Repository).
import sys, json
import numpy as np
import os
HIER = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get('PCMMS_REPO') or os.path.abspath(os.path.join(HIER, '..', '..', '..'))   # Kopf
sys.path.insert(0, os.path.join(REPO, 'code'))
from pcmms_auswertung.generator import systeme
out = {}
for name in ('A4', 'V1-G0', 'V1-G60h'):
    s = systeme.system(name)
    a = systeme.antworten(s, k_voll=15)
    Ns = a.Ns_kraft            # (Modul, k) Summe ohne Kette
    Nz = a.Nz_kraft            # (Modul, Zelle, k)
    print(f'== {name}: f = {a.f} Hz, k_max = {s.k_max}, starr = {s.K is None}, m_j = {s.m}, F0 = {np.round(a.F0,3)}')
    print('  |Summe| Modul 1, k = 1..12 [N]:', np.round(np.abs(Ns[0, :12]), 4))
    print('  |Summe| Modul 2, k = 1..12 [N]:', np.round(np.abs(Ns[1, :12]), 4))
    print('  |Zelle c| Modul 1 k = 1..3 [N]:', [np.round(np.abs(Nz[0, c, :3]), 4).tolist() for c in range(3)])
    out[name] = dict(f=a.f, k_max=s.k_max, summe_abs=np.abs(Ns[:, :12]).tolist(), summe=[[ [z.real, z.imag] for z in row[:12]] for row in Ns],
                     zelle_abs=np.abs(Nz[:, :, :12]).tolist())
json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HIER, 'struktur.json'), 'w'), indent=1)
