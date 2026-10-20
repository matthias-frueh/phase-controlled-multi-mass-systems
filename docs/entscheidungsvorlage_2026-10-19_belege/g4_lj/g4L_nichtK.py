# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 2.2 (Option F).
# Zweck: G4 an Nicht-K-Läufen der Phase 1 (PR #23) gegen G4-Kontrollwiederholungen; Rollenzahlen.
# Eingaben: Argument 1 = g4L_daten.json (Standard: hier; aus g4L_daten.py).
# Seed: keiner. Laufzeit: gemessen unter 1 s (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B g4L_nichtK.py > g4L_nichtK.out
# Herkunft: Scratch-Ordner vor der Nachprüfung 2 (erste Fassung); von Nachprüfung 2 gelesen, erneut
#   ausgeführt und übernommen. Geändert: Pfad von g4L_daten.json.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
# G4 an Nicht-K-Läufen der Phase 1 (PR #23: regeln.G4 − konfig_g4) gegen G4-Kontrollwiederholungen; Rollenzahlen
import json, collections, os, sys
D = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'g4L_daten.json')))
d23 = D['d23']
S = collections.Counter()
for key in sorted(d23, key=lambda s: (s.split('|')[0], int(s.split('|')[1]))):
    b = d23[key]; a = b['ablauf']; p1 = b['phase1']
    an = a['anlaesse']
    kg4 = sum(v for k, v in an.items() if k.startswith('kontrollwiederholung') and 'G4' in k)
    nk = p1['regeln'].get('G4', 0) - p1['konfig_g4']
    r = a['rollen']
    nR_aus = sum(r.get(x, 0) for x in ('referenz_block', 'schlussreferenz', 'aufwaermen', 'R1', 'R2', 'R3', 'alarmwiederholung'))
    s3 = sum(v for k, v in an.items() if k.startswith('s3_wiederholung'))
    print(key, a['status'][:5], 'nichtK_G4', nk, 'kwdh_G4', kg4, 'Diff', nk - kg4, '| R ausserhalb Kontrollsatz', nR_aus,
          '| s3wdh', s3, '| sum(gueltig_je_modul)-75', sum(b['kontrollen']['gueltig_je_modul']) - 75,
          '| regeln', p1['regeln'], 'n_laeufe', p1['n_laeufe'])
    S['nk'] += nk; S['kg4'] += kg4; S['nR_aus'] += nR_aus
    if a['status'] == 'abgeschlossen':
        S['nk_ab'] += nk; S['kg4_ab'] += kg4; S['nR_aus_ab'] += nR_aus; S['s3_ab'] += s3
        S['ueber_ab'] += sum(b['kontrollen']['gueltig_je_modul']) - 75
print(dict(S))
