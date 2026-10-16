"""Dateiformate der Entwicklungsschnittstelle von AP-11, AP-12 und AP-13 (Werkzeuge 4–6 und 8, Präreg v2 §12).

Jede Datei besteht aus einem JSON-Kopf und, wenn Felder groß oder komplex sind, einer NPZ-Datei gleichen Namens.
Der Kopf trägt Pflichtmetadaten:

  schema          "pcmms.<art>", art aus SCHEMATA
  schema_version  Version des Schemas; fehlende oder unbekannte Versionen werden zurückgewiesen
  datenart        "synthetisch" oder "messung"; in dieser Entwicklungsstufe verarbeiten AP-11 und AP-12 nur
                  synthetische Daten, und eine Auswertung mischt nie beide Arten
  kennung         Registrierungs- bzw. Datensatzkennung; synthetische Kennungen beginnen mit "SYNTH-"
  registrierung   bei synthetischen Daten stets "keine (synthetisch)": keine Kennung behauptet eine Registrierung
  erzeugt_von     Programm und Paketversion; code_version: Paketversion und Git-Stand des Repositorys

Die NPZ-Datei wird deterministisch geschrieben (feste Zeitstempel im ZIP, sortierte Schlüssel), damit gleiche
Eingaben und Seeds bitgleiche Dateien und damit gleiche SHA-256-Prüfsummen ergeben. Der Kopf nennt Name, SHA-256,
Datentyp und Form jedes Felds; beim Lesen werden sie geprüft. Komplexe Zahlen stehen in NPZ als complex128, in JSON
als Paare [Re, Im].

Dieses Format ist eine Entwicklungsschnittstelle und legt das Rohdatenformat der Aufnahmesoftware (AP-10) nicht fest.
"""
import datetime
import functools
import hashlib
import io
import json
import os
import subprocess
import zipfile

import numpy as np

PAKET_VERSION = '0.1.0'
PRAEFIX_SYNTH = 'SYNTH-'
REGISTRIERUNG_SYNTH = 'keine (synthetisch)'
DATENARTEN = ('synthetisch', 'messung')
SCHEMATA = {
    'rohlauf': '0.1',             # Kopf einer Rohdatei der Ebene Z (Daten in NPZ)
    'manifest': '0.1',            # Liste der Rohdateien mit SHA-256 (JSON; CSV als Lesefassung)
    'p0_messung': '0.1',          # synthetische Messdaten von P0.1, P0.2, P0.4, P0.5 (Eingang von AP-11)
    'kalibrierung': '0.1',        # Ergebnis von Werkzeug 4 (AP-11): Kalibrier- und Profilgrößen
    'pilot': '0.1',               # Ergebnis von Werkzeug 5 (AP-11): Pilotgrößen ohne Residuen und Entscheidungen
    'teil_b': '0.1',              # synthetisches Teil B nach A9.3
    'laufzusammenfassung': '0.1', # Trennstelle Stufe 1 → Stufe 2 (Plan AP-13, Abschnitt 2.6 b)
    'zusammenfassungen': '0.1',   # Bündel vieler Laufzusammenfassungen
    'regelprofil': '0.1',         # Regelprofil mit Fundstelle, Status und Herkunft jedes Werts
    'bootstrap_indizes': '0.1',   # Indexmatrizen nach Plan 2.6 c
    'ergebnis': '0.1',            # Ergebnis von Werkzeug 6 (AP-12)
    'wahrheit': '0.1',            # Generatorwahrheit (nur der Harness liest sie)
    'bewertung': '0.1',           # Harness: Vergleich mit der Wahrheit, Raten mit MC-Fehler
    'katalog': '0.1',             # Szenarienkatalog
    'pruefsatz': '0.1',           # Hashes von Katalog, Seeds, Profilen und Testdaten
}
_ZIPZEIT = (1980, 1, 1, 0, 0, 0)


class FormatFehler(ValueError):
    """Eingabe verletzt das Format (fehlendes oder unbekanntes Schema, Pflichtfeld, Prüfsumme, Datenart)."""


@functools.lru_cache(maxsize=1)
def git_stand():
    """Commit-Hash des Repositorys (mit „+geändert“, wenn der Arbeitsbaum Änderungen enthält); None ohne Git."""
    wurzel = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        h = subprocess.run(['git', '-C', wurzel, 'rev-parse', 'HEAD'], capture_output=True, text=True, timeout=10)
        if h.returncode != 0:
            return None
        d = subprocess.run(['git', '-C', wurzel, 'status', '--porcelain', '--untracked-files=no'],
                           capture_output=True, text=True, timeout=10)
        return h.stdout.strip() + ('+geändert' if d.stdout.strip() else '')
    except (OSError, subprocess.SubprocessError):
        return None


def code_version():
    return dict(paket=PAKET_VERSION, git=git_stand())


# ── JSON ─────────────────────────────────────────────────────────────────────────────────────────────
def _json_wert(o):
    if isinstance(o, dict):
        return {str(k): _json_wert(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_json_wert(v) for v in o]
    if isinstance(o, np.ndarray):
        return _json_wert(o.tolist())
    if isinstance(o, (complex, np.complexfloating)):
        return [_json_wert(float(np.real(o))), _json_wert(float(np.imag(o)))]
    if isinstance(o, (float, np.floating)):
        o = float(o)
        if np.isnan(o):
            return None
        if np.isinf(o):
            return 'inf' if o > 0 else '-inf'
        return o
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


def json_text(obj):
    """Deterministische Textform (sortierte Schlüssel, UTF-8, NaN als null, ±∞ als Zeichenkette)."""
    return json.dumps(_json_wert(obj), ensure_ascii=False, indent=1, sort_keys=True, allow_nan=False) + '\n'


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_datei(pfad):
    h = hashlib.sha256()
    with open(pfad, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def sha256_json(obj):
    """Prüfsumme eines Objekts in kanonischer JSON-Form (ohne Einrückung)."""
    t = json.dumps(_json_wert(obj), ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
    return sha256_bytes(t.encode('utf-8'))


def komplex_aus_json(x):
    """[Re, Im] (auch geschachtelt) → complex-Array."""
    a = np.asarray(x, float)
    if a.shape[-1] != 2:
        raise FormatFehler('komplexe Zahl als Paar [Re, Im] erwartet')
    return a[..., 0] + 1j * a[..., 1]


def float_aus_json(x):
    """Gegenstück zu _json_wert für Gleitkommazahlen: null → NaN, 'inf' → ∞."""
    if x is None:
        return float('nan')
    if isinstance(x, str):
        return {'inf': float('inf'), '-inf': float('-inf')}[x]
    return float(x)


# ── deterministische NPZ ─────────────────────────────────────────────────────────────────────────────
def npz_bytes(felder):
    """NPZ als Bytes mit festen ZIP-Zeitstempeln und sortierten Schlüsseln (bitgleich bei gleichem Inhalt)."""
    puffer = io.BytesIO()
    with zipfile.ZipFile(puffer, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name in sorted(felder):
            a = np.require(np.asarray(felder[name]), requirements='C')       # 0-d bleibt 0-d
            if a.dtype == object:
                raise FormatFehler(f'Feld {name}: Objekt-Arrays sind nicht zulässig')
            b = io.BytesIO()
            np.lib.format.write_array(b, a, allow_pickle=False)
            info = zipfile.ZipInfo(name + '.npy', date_time=_ZIPZEIT)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, b.getvalue())
    return puffer.getvalue()


def feldbeschreibung(felder):
    return {k: dict(dtype=str(np.asarray(v).dtype), form=list(np.asarray(v).shape)) for k, v in sorted(felder.items())}


# ── Kopf ─────────────────────────────────────────────────────────────────────────────────────────────
def kopf(art, kennung, datenart='synthetisch', **weitere):
    """Pflichtkopf für ein Objekt der Art art (Schlüssel von SCHEMATA)."""
    if art not in SCHEMATA:
        raise FormatFehler(f'unbekannte Art {art!r}')
    k = dict(schema=f'pcmms.{art}', schema_version=SCHEMATA[art], datenart=datenart, kennung=kennung,
             erzeugt_von=dict(programm='pcmms_auswertung', version=PAKET_VERSION), code_version=code_version())
    if datenart == 'synthetisch':
        k['registrierung'] = REGISTRIERUNG_SYNTH
    k.update(weitere)
    pruefe_kopf(k, art)
    return k


def synth_kennung(*teile):
    """Kennung synthetischer Daten: „SYNTH-“ und die Teile, mit Bindestrich verbunden."""
    return PRAEFIX_SYNTH + '-'.join(str(t) for t in teile)


def pruefe_kopf(k, art=None, datenarten=('synthetisch',)):
    """Prüft die Pflichtmetadaten. art: erwartete Art; datenarten: zugelassene Datenarten dieser Stufe."""
    if not isinstance(k, dict):
        raise FormatFehler('Kopf fehlt oder ist kein JSON-Objekt')
    for feld in ('schema', 'schema_version', 'datenart', 'kennung'):
        if feld not in k:
            raise FormatFehler(f'Pflichtfeld {feld!r} fehlt im Kopf')
    schema = str(k['schema'])
    if not schema.startswith('pcmms.') or schema[6:] not in SCHEMATA:
        raise FormatFehler(f'unbekanntes Schema {schema!r}')
    a = schema[6:]
    if art is not None and a != art:
        raise FormatFehler(f'Schema {schema!r} statt pcmms.{art}')
    if k['schema_version'] != SCHEMATA[a]:
        raise FormatFehler(f'Schema {schema}: Version {k["schema_version"]!r} unbekannt (erwartet {SCHEMATA[a]})')
    if k['datenart'] not in DATENARTEN:
        raise FormatFehler(f'Datenart {k["datenart"]!r} unbekannt (zulässig: {", ".join(DATENARTEN)})')
    kenn = str(k['kennung'])
    if k['datenart'] == 'synthetisch':
        if not kenn.startswith(PRAEFIX_SYNTH):
            raise FormatFehler(f'synthetische Kennung muss mit {PRAEFIX_SYNTH!r} beginnen: {kenn!r}')
        if k.get('registrierung') != REGISTRIERUNG_SYNTH:
            raise FormatFehler('synthetische Daten dürfen keine Registrierung behaupten '
                               f'(registrierung = {REGISTRIERUNG_SYNTH!r} erwartet)')
    elif kenn.startswith(PRAEFIX_SYNTH):
        raise FormatFehler('Messdaten mit synthetischer Kennung')
    if k['datenart'] not in datenarten:
        raise FormatFehler(f'Datenart {k["datenart"]!r} ist in dieser Stufe nicht zugelassen '
                           '(AP-11/AP-12 verarbeiten hier nur synthetische Daten; AP-10-Format offen)')
    return a


def gleiche_datenart(*koepfe):
    """Eine Auswertung mischt nie Mess- und synthetische Daten."""
    arten = {k['datenart'] for k in koepfe if k is not None}
    if len(arten) > 1:
        raise FormatFehler(f'gemischte Datenarten {sorted(arten)}: Mess- und synthetische Daten werden nicht '
                           'gemeinsam ausgewertet')
    return arten.pop() if arten else None


# ── Schreiben und Lesen ──────────────────────────────────────────────────────────────────────────────
def schreibe(pfad_ohne_endung, k, felder=None, inhalt=None):
    """Schreibt <pfad>.json (Kopf, Inhalt) und, falls felder, <pfad>.npz. Rückgabe: SHA-256 beider Dateien."""
    pruefe_kopf(k, datenarten=DATENARTEN)
    os.makedirs(os.path.dirname(os.path.abspath(pfad_ohne_endung)), exist_ok=True)
    obj = dict(kopf=dict(k))
    hashes = {}
    if felder:
        b = npz_bytes(felder)
        name = os.path.basename(pfad_ohne_endung) + '.npz'
        with open(pfad_ohne_endung + '.npz', 'wb') as f:
            f.write(b)
        obj['kopf']['daten'] = dict(datei=name, sha256=sha256_bytes(b), felder=feldbeschreibung(felder))
        hashes['npz'] = obj['kopf']['daten']['sha256']
    if inhalt is not None:
        obj['inhalt'] = inhalt
    t = json_text(obj)
    with open(pfad_ohne_endung + '.json', 'w', encoding='utf-8') as f:
        f.write(t)
    hashes['json'] = sha256_bytes(t.encode('utf-8'))
    return hashes


def lies(pfad, art=None, datenarten=('synthetisch',)):
    """Liest <pfad>.json (und die NPZ-Datei, falls genannt) und prüft Schema, Datenart, Prüfsumme und Felder.
    Rückgabe: (Kopf, Inhalt oder None, Felder als dict oder {})."""
    p = pfad[:-5] if pfad.endswith('.json') else (pfad[:-4] if pfad.endswith('.npz') else pfad)
    if not os.path.exists(p + '.json'):
        raise FormatFehler(f'Kopfdatei {p}.json fehlt')
    with open(p + '.json', encoding='utf-8') as f:
        obj = json.load(f)
    if not isinstance(obj, dict) or 'kopf' not in obj:
        raise FormatFehler(f'{p}.json: Kopf fehlt')
    k = obj['kopf']
    pruefe_kopf(k, art, datenarten)
    felder = {}
    if 'daten' in k:
        d = k['daten']
        npz = os.path.join(os.path.dirname(p + '.json'), d['datei'])
        if not os.path.exists(npz):
            raise FormatFehler(f'Datendatei {npz} fehlt')
        with open(npz, 'rb') as f:
            b = f.read()
        if sha256_bytes(b) != d['sha256']:
            raise FormatFehler(f'{npz}: SHA-256 stimmt nicht mit dem Kopf überein')
        with np.load(io.BytesIO(b), allow_pickle=False) as z:
            felder = {n: z[n] for n in z.files}
        erwartet = d.get('felder', {})
        if set(erwartet) != set(felder):
            raise FormatFehler(f'{npz}: Felder {sorted(felder)} statt {sorted(erwartet)}')
        for n, beschr in erwartet.items():
            if str(felder[n].dtype) != beschr['dtype'] or list(felder[n].shape) != list(beschr['form']):
                raise FormatFehler(f'{npz}: Feld {n} hat {felder[n].dtype}{list(felder[n].shape)}, '
                                   f'erwartet {beschr["dtype"]}{beschr["form"]}')
    return k, obj.get('inhalt'), felder


def zeitstempel():
    """Nur für Protokollzwecke; Ergebnisdateien enthalten keine Zeitstempel, damit sie reproduzierbar bleiben."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
