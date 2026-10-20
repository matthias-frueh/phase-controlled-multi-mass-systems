# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 2.2 (Option F) und 3.1 (G4-Halte an Lⱼ).
# Zweck: liest die Checkpoint-Befunde von PR #22 (G4-Diagnose, 120 Kampagnen) und PR #23 (30 Ablaufkampagnen),
#   prüft jede Datei per SHA-256 gegen die ergebnisse.json in docs/ und schreibt sie unverändert als g4L_daten.json.
# Eingaben: Argument 1 = Verzeichnis mit den Diagnose-Checkpoints von PR #22 (Ordner G4-N01-*-start/-rest; flüchtig, am 17.10.2026 unter
#   /tmp/pcmms-diagnose-e3b-g4-20261017/ erzeugt; SHA-256 in docs/e3b_g4_diagnose_2026-10-17/ergebnisse.json)
#   Argument 2 = Verzeichnis mit den Checkpoint-Ordnern korr-N01-{A4,V1G0,V1G60h}-wiederholungen/ der Korrekturrunde von PR #23
#   (flüchtig, am 18.10.2026 unter /tmp/pcmms-ablauf-vergleich-20261018/ erzeugt; SHA-256 der ablauf_*.json in
#   docs/ap13_kmax_wiederholungen_2026-10-17/ergebnisse.json, Schlüssel "checkpoints")
#   Argument 3 = Ausgabe (Standard g4L_daten.json hier).
# Seed: keiner. Laufzeit: gemessen 2 s Wandzeit, 0 s CPU (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B g4L_daten.py <checkpoints-pr22> <checkpoints-pr23> g4L_daten.json > g4L_daten.out
# Herkunft: Scratch-Ordner vor der Nachprüfung 2 (erste Fassung); von Nachprüfung 2 gelesen, erneut ausgeführt und
#   übernommen. Geändert: Checkpoint-Pfade als Argumente, Repository relativ, Ausgabepfad.
# Repository-Wurzel: drei Ebenen über diesem Ordner; abweichend über die Umgebungsvariable PCMMS_REPO (etwa ein
#   Auszug von main 0f63187: git archive 0f63187 code docs | tar -x -C <ziel>).
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
# Nur lesen: PR-#22-Diagnosecheckpoints (σ̂_Δ je L-Modul, G4 der übrigen Phase-1-Läufe im statischen Plan)
# und PR-#23-Checkpoint-Befunde (Anlasszähler je Kampagne). Hashes gegen die ergebnisse.json in docs/ geprüft.
import json, hashlib, glob, collections, os, sys
import numpy as np
REPO = os.environ.get('PCMMS_REPO') or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))   # Repository-Wurzel (Kopf)
REPO = os.path.join(REPO, 'docs')
BASIS22, BASIS23 = sys.argv[1], sys.argv[2]   # flüchtige Checkpoints (Kopf)
e22 = json.load(open(f'{REPO}/e3b_g4_diagnose_2026-10-17/ergebnisse.json'))['inhalt']['herkunft']['checkpoints'] \
    if 'herkunft' in json.load(open(f'{REPO}/e3b_g4_diagnose_2026-10-17/ergebnisse.json'))['inhalt'] else None
def finde(o, key):
    if isinstance(o, dict):
        if key in o: return o[key]
        for v in o.values():
            r = finde(v, key)
            if r is not None: return r
    return None
e22 = finde(json.load(open(f'{REPO}/e3b_g4_diagnose_2026-10-17/ergebnisse.json')), 'checkpoints')
d22 = {}
for auf, info in e22.items():
    for f, h in info['dateien'].items():
        p = f'{BASIS22}/{auf}/{f}'
        assert hashlib.sha256(open(p, 'rb').read()).hexdigest() == h, p
        if f.endswith('.json'):
            for b in json.load(open(p))['inhalt']['befunde']:
                d22[(b['szenario'], b['index'])] = b
e23 = json.load(open(f'{REPO}/ap13_kmax_wiederholungen_2026-10-17/ergebnisse.json'))['checkpoints']
d23 = {}
for auf in ('korr-N01-A4-wiederholungen', 'korr-N01-V1G0-wiederholungen', 'korr-N01-V1G60h-wiederholungen'):
    for f, h in e23[auf]['dateien'].items():
        p = f'{BASIS23}/{auf}/{f}'
        assert hashlib.sha256(open(p, 'rb').read()).hexdigest() == h, p
        for b in json.load(open(p))['inhalt']['befunde']:
            d23[(b['szenario'], b['index'])] = b
print('PR22 Kampagnen', len(d22), 'PR23 Kampagnen', len(d23))
json.dump(dict(d22={f'{k[0]}|{k[1]}': v for k, v in d22.items()}, d23={f'{k[0]}|{k[1]}': v for k, v in d23.items()}),
          open(sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'g4L_daten.json'), 'w'), ensure_ascii=False)
