# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 2.2 (Option F) und 3.1.
# Zweck: Anlasszähler je PR-#23-Kampagne (Kontrollwiederholungen nach G4, Alarm, sonst) und Abgleich mit
#   PR #22 bei gleichem Seed.
# Eingaben: Argument 1 = g4L_daten.json (Standard: hier; aus g4L_daten.py).
# Seed: keiner. Laufzeit: gemessen unter 1 s (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B g4L_zaehlung.py > g4L_zaehlung.out
# Herkunft: Scratch-Ordner vor der Nachprüfung 2 (erste Fassung); von Nachprüfung 2 gelesen, erneut
#   ausgeführt und übernommen. Geändert: Pfad von g4L_daten.json.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
# Anlasszähler je PR-#23-Kampagne und Abgleich mit PR #22 (gleicher Seed)
import json, collections, os, sys
D = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'g4L_daten.json')))
d22, d23 = D['d22'], D['d23']
alle = collections.Counter()
print('System Idx Status Halt | kwdh_G4 kwdh_Alarm kwdh_sonst | rollen.kontrolle kontrollwdh | gueltig_je_modul | PR22: sonst_G4 (126 R+L), Seed gleich')
tot = collections.defaultdict(lambda: collections.Counter())
for key in sorted(d23, key=lambda s: (s.split('|')[0], int(s.split('|')[1]))):
    b = d23[key]; a = b['ablauf']
    an = a['anlaesse']
    for k, v in an.items(): alle[k] += v
    kg4 = sum(v for k, v in an.items() if k.startswith('kontrollwiederholung') and 'G4' in k)
    kal = sum(v for k, v in an.items() if k.startswith('kontrollwiederholung') and 'Nullpunktalarm' in k)
    kso = sum(v for k, v in an.items() if k.startswith('kontrollwiederholung')) - kg4 - kal
    p22 = d22.get(key)
    s22 = p22['phase1']['sonstige_ungueltig']['G4'] if p22 else None
    same = p22 and p22['seed'] == b['seed']
    st = a['status']
    halt = (a['halt'] or {}).get('regel') if isinstance(a['halt'], dict) else a['halt']
    sysn = key.split('|')[0]
    t = tot[(sysn, st == 'abgeschlossen')]
    t['n'] += 1; t['kg4'] += kg4; t['kal'] += kal; t['kso'] += kso; t['s22'] += s22 or 0
    t['kontrolle'] += a['rollen'].get('kontrolle', 0)
    print(key, st, halt, '|', kg4, kal, kso, '|', a['rollen'].get('kontrolle'), a['rollen'].get('kontrollwiederholung'), '|',
          b['kontrollen']['gueltig_je_modul'], '|', s22, same)
print()
for k, v in sorted(alle.items()):
    if 'kontroll' in k: print('Summe', k, v)
print()
for k, t in sorted(tot.items()):
    print(k, dict(t))
