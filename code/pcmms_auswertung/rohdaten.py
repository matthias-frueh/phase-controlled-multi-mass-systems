"""Rohdatei eines Laufs (Ebene Z) und Manifest – Entwicklungsformat bis zur Festlegung durch AP-10.

Rohdatei: <lauf_id>.json (Kopf: Pflichtmetadaten nach formate.py, Inhalt: Metadaten nach A9.10 und Protokoll) und
<lauf_id>.npz (Daten). Inhalt:
  lauf          lauf_id, laufart, modul, einstellung, konfiguration, phase, block, messtag, position,
                kontrollsatz, t_start [s, Kampagnenuhr]
  erfassung     f_soll [Hz], f_s [Hz], t0 [s, erster Abtastwert relativ zum Laufbeginn], adc (bits,
                vollausschlag), f_takt [Hz] (Zeitstempel der Indeximpulse), kanaele (Liste)
  protokoll     t_rampe_ende [s], t_e [s], n_zyklen_fenster, stoerung (G8), aufzeichnung_ok (G10), park_ok (G9),
                bediener, notizen
  umgebung      Luftdruck, Lufttemperatur, Feuchte, Versorgungsspannung (A9.10)
  einstellungen Verstärker, Filter, Firmware- und Softwarestände, Kalibrier-IDs
  generator     nur synthetisch: Version, Szenario, Seed (die Wahrheit liegt nicht in der Rohdatei)
Daten (NPZ): kraft_adc (3, n) int64 Rohwerte je Kraftkanal in ADC-Einheiten; index_modul1 … index_modul3
(Zeitstempel [s] relativ zum Laufbeginn; Länge 0, wenn das Modul geparkt ist; fehlt der Schlüssel, fehlt der Kanal);
temperatur_zellen (3, m) [°C] mit t_temperatur (m) [s]; uebersteuerung (3) bool (Übersteuerungssignal der Kette).
Ein fehlender Pflichtkanal wird von Stufe 1 gemeldet und nicht ergänzt.

Manifest: eine Zeile je Lauf (auch ungültige und abgebrochene Läufe): Dateinamen, SHA-256 beider Dateien, Laufart,
Konfiguration, Block, Reihenfolge, Online-Gültigkeit (in dieser Stufe „nicht geprüft“: kein Monitor, AP-10).
"""
import csv
import os

import numpy as np

from . import formate

PFLICHTKANAELE = ('kraft_adc',)
INDEXKANAELE = ('index_modul1', 'index_modul2', 'index_modul3')


def schreibe_rohlauf(verzeichnis, inhalt, daten, kennung, datenart='synthetisch'):
    """Schreibt eine Rohdatei; Rückgabe Manifestzeile."""
    lid = inhalt['lauf']['lauf_id']
    pfad = os.path.join(verzeichnis, lid)
    k = formate.kopf('rohlauf', kennung, datenart)
    h = formate.schreibe(pfad, k, daten, inhalt)
    l = inhalt['lauf']
    return dict(lauf_id=lid, kopf=lid + '.json', daten=lid + '.npz', sha256_kopf=h['json'], sha256_daten=h['npz'],
                laufart=l['laufart'], modul=l.get('modul'), einstellung=l['einstellung'],
                konfiguration=l['konfiguration']['id'], phase=l['phase'], block=l.get('block'),
                position=l['position'], online_gueltigkeit='nicht geprüft (kein Monitor, AP-10)')


def lies_rohlauf(pfad):
    k, inhalt, daten = formate.lies(pfad, 'rohlauf')
    return k, inhalt, daten


def schreibe_manifest(verzeichnis, zeilen, kennung, datenart='synthetisch'):
    """manifest.json (maßgeblich) und manifest.csv (Lesefassung)."""
    zeilen = sorted(zeilen, key=lambda z: z['position'])
    k = formate.kopf('manifest', kennung, datenart)
    h = formate.schreibe(os.path.join(verzeichnis, 'manifest'), k, inhalt=dict(laeufe=zeilen))
    felder = list(zeilen[0]) if zeilen else []
    with open(os.path.join(verzeichnis, 'manifest.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=felder, lineterminator='\n')
        w.writeheader()
        for z in zeilen:
            w.writerow({a: ('' if v is None else v) for a, v in z.items()})
    return h


def lies_manifest(pfad, pruefe_dateien=True):
    """Liest manifest.json; prüft auf Wunsch jede Rohdatei gegen ihre SHA-256."""
    p = os.path.join(pfad, 'manifest') if os.path.isdir(pfad) else pfad
    k, inhalt, _ = formate.lies(p, 'manifest')
    basis = os.path.dirname(os.path.abspath(p + ('' if p.endswith('.json') else '.json')))
    zeilen = inhalt['laeufe']
    if pruefe_dateien:
        for z in zeilen:
            for datei, sha in ((z['kopf'], z['sha256_kopf']), (z['daten'], z['sha256_daten'])):
                q = os.path.join(basis, datei)
                if not os.path.exists(q):
                    raise formate.FormatFehler(f'Manifest: Datei {datei} fehlt')
                if formate.sha256_datei(q) != sha:
                    raise formate.FormatFehler(f'Manifest: SHA-256 von {datei} weicht ab')
    return k, zeilen, basis


def index_quantisiert(t, f_takt):
    """Zeitstempel auf das Raster des Zeitgebers (Quantisierung 360°·f/f_takt, §5.1)."""
    return np.round(np.asarray(t, float) * f_takt) / f_takt
