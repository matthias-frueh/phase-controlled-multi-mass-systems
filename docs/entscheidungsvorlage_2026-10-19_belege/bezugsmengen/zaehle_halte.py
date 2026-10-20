# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 3.1 (Wie viele Halte das heute betrifft).
# Zweck: Zählung der angehaltenen Kampagnen in den Checkpoint-Befunden und ob z⁰ heute an allen Punkten endlich
#   wäre (alle 21 Punkte auswertbar und ŷ¹ gültig).
# Eingaben: Argument 1 = Verzeichnis mit den Checkpoint-Ordnern korr-N01-{A4,V1G0,V1G60h}-wiederholungen/ der Korrekturrunde von PR #23
#   (flüchtig, am 18.10.2026 unter /tmp/pcmms-ablauf-vergleich-20261018/ erzeugt; SHA-256 der ablauf_*.json in
#   docs/ap13_kmax_wiederholungen_2026-10-17/ergebnisse.json, Schlüssel "checkpoints")
# Seed: keiner. Laufzeit: gemessen unter 1 s (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B zaehle_halte.py <checkpoint-basis> > zaehle_halte.out
# Herkunft: Nachprüfung 4 (Bezugsmengen). Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""Zählt in den Checkpoint-Befunden (schlank, ablauf-2) die angehaltenen Kampagnen und ob z0 heute an allen
Punkten endlich wäre (alle 21 Schnittpunkte auswertbar und yhat1 gültig; vgl. auswertung.py Z. 254-266)."""
import glob, json, sys
basis = sys.argv[1]
ges = dict(n=0, halt=0, halt_z_alle=0, halt_z_teil=0, halt_z_keine=0, abg=0, abg_voll=0)
for p in sorted(glob.glob(basis + '/korr-N01-*-wiederholungen/ablauf_*.json')):
    d = json.load(open(p))
    for b in d['inhalt']['befunde']:
        ges['n'] += 1
        st = b['ablauf']['status']
        a = b['auswertbar']
        y1 = b['kontrollen']['yhat1_gueltig']
        z_alle = (a['n'] == a['von']) and y1
        z_teil = (0 < a['n'] < a['von']) and y1
        if st != 'abgeschlossen':
            ges['halt'] += 1
            ges['halt_z_alle'] += z_alle
            ges['halt_z_teil'] += z_teil
            ges['halt_z_keine'] += not (z_alle or z_teil)
            print(b['szenario'], b['index'], st, b['ablauf'].get('halt'), 'auswertbar', a['n'], '/', a['von'],
                  'min_gueltig', a['min_gueltig'], 'yhat1', y1, 'vollstaendig', b['vollstaendig'],
                  'sperren', b['sperren'])
        else:
            ges['abg'] += 1
            ges['abg_voll'] += bool(b['vollstaendig'])
            if not z_alle:
                print('abgeschlossen ohne alle z:', b['szenario'], b['index'], a)
print(ges)
