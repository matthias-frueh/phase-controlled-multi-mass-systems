# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 2.1 (Tabelle MAD(D_F) an S120, schwere Ränder am Knick).
# Zweck: nachgebildete MAD(D_F) je Variante (df_mc_*.json) gegen die beobachteten mad_DF aus PR #22; Faktoren an
#   S120, Randverhalten.
# Eingaben: df_mc_A4.json und df_mc_V1-G0.json hier; docs/e3b_g4_diagnose_2026-10-17/ergebnisse.json.
# Seed: keiner. Laufzeit: gemessen unter 1 s (ein Prozess, ein Thread, 20.10.2026). Aufruf: python3 -I -B df_vergleich.py > df_vergleich.out
# Herkunft: Nachprüfung 6. Geändert: Pfade.
# Repository-Wurzel: drei Ebenen über diesem Ordner; abweichend über die Umgebungsvariable PCMMS_REPO (etwa ein
#   Auszug von main 0f63187: git archive 0f63187 code docs | tar -x -C <ziel>).
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
# NL6: Vergleich der nachgebildeten MAD(D_F) je Variante mit den beobachteten mad_DF aus ergebnisse.json (PR #22).
import json
import os
import numpy as np
P = os.path.dirname(os.path.abspath(__file__)) + os.sep
REPO = os.environ.get('PCMMS_REPO') or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))   # Repository-Wurzel (Kopf)
erg = json.load(open(os.path.join(REPO, 'docs', 'e3b_g4_diagnose_2026-10-17', 'ergebnisse.json')))['inhalt']['g4']['systeme']
for name, sids in (('A4', ('N01-A4',)), ('V1-G0', ('N01-V1G0', 'N01-V1G60h'))):
    M = json.load(open(P + f'df_mc_{name}.json'))
    V = list(M['res'])
    print(f'== {name} (N = {M["N"]} je Punkt), MAD(D_F) [mN]; beobachtet: ' + ', '.join(sids))
    print('Punkt ' + ' | '.join(f'{v[:14]:>14s}' for v in V) + ' | ' + ' | '.join(f'{s[4:]:>9s}' for s in sids))
    ids = erg[sids[0]]['punkte']['id'] + ['P1', 'P2', 'P3']
    rat = {v: [] for v in V}
    for c, pid in enumerate(ids):
        mc = [M['res'][v][c]['mad'] * 1e3 for v in V]
        if c < 21:
            ob = [erg[s]['punkte']['mad_DF'][c] * 1e3 for s in sids]
        else:
            ob = [erg[s]['piloten']['beobachtet'][c - 21] * 1e3 for s in sids]
        for v, x in zip(V, mc):
            rat[v].append(np.mean(ob) / x)
        if pid in ('S100', 'S104', 'S110', 'S114', 'S116', 'S118', 'S120', 'S122', 'S124', 'S130', 'S140', 'P1', 'P2', 'P3'):
            print(f'{pid:5s} ' + ' | '.join(f'{x:14.3f}' for x in mc) + ' | ' + ' | '.join(f'{x:9.3f}' for x in ob))
    for v in V:
        r = np.array(rat[v])
        ohne = np.r_[r[:10], r[11:21]]
        print(f'  beobachtet/MC {v:34s}: S120 {r[10]:.3f}; übrige 20 Punkte Mittel {ohne.mean():.3f} (min {ohne.min():.3f}, max {ohne.max():.3f}); Piloten {np.round(r[21:],3)}')
    # Faktor an S120 relativ zur Sollphase, und Form der Verteilung
    i = 10
    s0 = M['res'][V[0]][i]; s1 = M['res'][V[-1]][i]
    print(f'  S120: MAD voll/soll = {s1["mad"]/s0["mad"]:.3f}, SD voll/soll = {s1["sd"]/s0["sd"]:.3f}; '
          f'SD/MAD voll {s1["sd"]/s1["mad"]:.3f}, soll {s0["sd"]/s0["mad"]:.3f}; q99(|D|)/MAD voll {s1["q"][2]/s1["mad"]:.3f} '
          f'(normal 2,576), q99.9/MAD {s1["q"][3]/s1["mad"]:.3f} (normal 3,291)')
    for v in V[1:]:
        print(f'   S120 Faktor MAD {v}/soll = {M["res"][v][i]["mad"]/s0["mad"]:.3f}; S118: {M["res"][v][9]["mad"]/M["res"][V[0]][9]["mad"]:.3f}; S100: {M["res"][v][0]["mad"]/M["res"][V[0]][0]["mad"]:.3f}')
