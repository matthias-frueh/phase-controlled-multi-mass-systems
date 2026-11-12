"""Herkunftsnachweis der Phase-0-Läufe: Grundlage der Bindung Phase 0 ↔ Teil B (Präreg A9.3 Nr. 1).

Ab pilot-0.5 und teil_b-0.5 (Regelstand 2026-11) ist ein Satz von Phase-0-Größen nicht mehr über eine Prüfsumme der
berechneten Datenfelder an seine Läufe gebunden, sondern über deren Herkunft (Entscheidung des Autors vom 12.11.2026,
docs/entscheidungsnotiz_herkunft_phase0_2026-11-12.md). Der Nachweis enthält nur exakte Angaben: Kennungen,
Positionen, Prüfsummen gespeicherter Dateien, Versionen, den Zustand eines Zufallsstroms. Gleitkommafelder gehen
nicht ein. Er hängt deshalb weder an der Kompressionsbibliothek noch am Rechenkern der BLAS-Bibliothek. Unter den
historischen Profilen bleibt die Bindung die Prüfsumme der Datenfelder (pilot.daten_sha256).

Zwei Klassen von Läufen (Kopffeld ebene der Laufzusammenfassung):
  rohdatei    Lauf mit Rohdatei (Ebene Z). Nachweis: lauf_id, position, hash_rohdatei (SHA-256 der Datendatei),
              kalibrier_hash (SHA-256 des Kalibrierobjekts von Stufe 1), version_stufe1. Fehlt eine Angabe oder ist
              eine Prüfsumme keine SHA-256-Hexzahl, wird der Lauf zurückgewiesen.
  generator   Lauf ohne Rohdatei (Ebene H, immer synthetisch). Nachweis: lauf_id, position, version_stufe1
              (Generatorversion). Ein solcher Lauf trägt keinen Rohdatei-Hash, auch keinen künstlichen: gefüllte
              Felder hash_rohdatei oder kalibrier_hash werden zurückgewiesen. Dazu gehört der Generatornachweis der
              Tabelle.

Generatornachweis (Metadaten der Tabelle, zusammenfassung.META_GENERATORNACHWEIS; die Laufköpfe bleiben unverändert):
  version              Version des Generators (ebene_h-…, phase0_modell-…)
  modell_sha256        SHA-256 der Modellbeschreibung mit dem wirksamen Rauschmodell (System, Rauschmodell, Plan,
                       Effektstärke, Effekte, k_voll, Vollausschlag, Hertz-Modell)
  laufplan_sha256      SHA-256 der Laufliste, die der Generator erhalten hat (alle Läufe, auch die der Phase 1: sie
                       bestimmen, welche Ziehungen ein Lauf erhält)
  strom_sha256         SHA-256 des Zustands des Zufallsstroms vor der ersten Ziehung
  zusatzstrom_sha256   dasselbe für den Zusatzstrom des Strukturmodells, sonst None
  aufruf               None oder die Angaben, mit denen harness.kette die Tabelle erzeugt hat: szenario, stufe, seed,
                       stroeme (Namen der Ströme für Laufreihenfolge und Generator). Plan, Stärke, Rauschmodell und
                       k_max stehen in modell_sha256. Der Seed wird geprüft: zufall.strom(seed, Name) muss den
                       Zustand strom_sha256 ergeben.
Den Generatornachweis legt der Generator selbst an (generator.ebene_h.generatornachweis); er liest den Zustand des
Stroms, den er tatsächlich erhält. Der Nachweis belegt Herkunft und Rechenvorschrift, nicht die Werte: Dieselbe
Generatoridentität ergibt auf verschiedenen Prozessoren Werte, die sich im Rundungsrauschen unterscheiden, und
geänderte Datenfelder bei unverändertem Nachweis erkennt er nicht (Wertevergleich mit Toleranz: gesonderte Prüfung).

Nachweis eines Satzes (nachweis): version (herkunft-1), datenart, klassen (Zahl der Läufe je Klasse),
optionale_felder (Namen der vorhandenen optionalen Datenfelder), laeufe (Nachweise je Lauf in aufsteigender Position;
die Zeilenreihenfolge der Tabelle zählt nicht) und generator. Die Bindung ist die SHA-256-Prüfsumme dieses Objekts in
kanonischer JSON-Form (sha256).

Regeln: Positionen und Lauf-IDs sind im Satz eindeutig; derselbe Rohdatei-Hash bei zwei Läufen ist ein Fehler; Läufe
der Klasse generator verlangen den Generatornachweis; bei Datenart messung sind nur Läufe der Klasse rohdatei
zulässig. Beide Klassen in einem Satz sind bei synthetischen Daten zulässig und an klassen erkennbar. Eine Tabelle
ohne Angabe der Datenart gilt als synthetisch (diese Stufe verarbeitet nur synthetische Daten, formate.lies).
"""
import re
from collections import Counter

from . import formate, zufall
from . import zusammenfassung as zf

VERSION = 'herkunft-1'
KLASSEN = ('rohdatei', 'generator')
EBENE_KLASSE = {'Z': 'rohdatei', 'H': 'generator'}
ROHDATEI_FELDER = ('hash_rohdatei', 'kalibrier_hash')                       # SHA-256, nur Klasse rohdatei
GENERATOR_PFLICHT = ('version', 'modell_sha256', 'laufplan_sha256', 'strom_sha256')
GENERATOR_FELDER = GENERATOR_PFLICHT + ('zusatzstrom_sha256', 'aufruf')
AUFRUF_FELDER = ('szenario', 'stufe', 'seed', 'stroeme')
_SHA256 = re.compile(r'[0-9a-f]{64}\Z')


class HerkunftFehler(formate.FormatFehler):
    """Die Herkunft der Läufe ist nicht belegt, oder der Nachweis verletzt eine seiner Regeln."""


def ist_sha256(x):
    return isinstance(x, str) and bool(_SHA256.match(x))


def strom_sha256(rng):
    """SHA-256 des Zustands eines numpy.random.Generator (ganze Zahlen, exakt). Liest nur, zieht keine Zahl."""
    return formate.sha256_json(rng.bit_generator.state)


def lauf_nachweis(kopf):
    """Nachweis eines Laufs aus dem Kopf seiner Laufzusammenfassung (Klasse nach dem Kopffeld ebene)."""
    lid = kopf['lauf_id']
    klasse = EBENE_KLASSE[kopf['ebene']]
    out = dict(lauf_id=lid, position=int(kopf['position']), klasse=klasse)
    if klasse == 'rohdatei':
        for feld in ROHDATEI_FELDER:
            if not ist_sha256(kopf.get(feld)):
                raise HerkunftFehler(f'Lauf {lid} (Ebene Z): {feld} fehlt oder ist keine SHA-256-Prüfsumme')
            out[feld] = kopf[feld]
    else:
        gefuellt = [feld for feld in ROHDATEI_FELDER if kopf.get(feld) is not None]
        if gefuellt:
            raise HerkunftFehler(f'Lauf {lid} (Ebene H): {", ".join(gefuellt)} gefüllt; ein Lauf ohne Rohdatei '
                                 'trägt keinen Rohdatei-Hash')
    if not kopf.get('version_stufe1'):
        raise HerkunftFehler(f'Lauf {lid}: version_stufe1 fehlt')
    out['version_stufe1'] = str(kopf['version_stufe1'])
    return out


def pruefe_generatornachweis(g):
    """Form des Generatornachweises; nennt er einen Aufruf, muss dessen Seed den Zustand des Stroms ergeben.
    Rückgabe: der Nachweis in JSON-Form."""
    if not isinstance(g, dict):
        raise HerkunftFehler('Läufe der Ebene H ohne Generatornachweis der Tabelle: Herkunft nicht belegt')
    unbekannt = sorted(set(g) - set(GENERATOR_FELDER))
    if unbekannt:
        raise HerkunftFehler(f'Generatornachweis: unbekannte Felder {unbekannt}')
    if not g.get('version'):
        raise HerkunftFehler('Generatornachweis: version fehlt')
    for feld in GENERATOR_PFLICHT[1:] + ('zusatzstrom_sha256',):
        if not (ist_sha256(g.get(feld)) or (feld == 'zusatzstrom_sha256' and g.get(feld) is None)):
            raise HerkunftFehler(f'Generatornachweis: {feld} fehlt oder ist keine SHA-256-Prüfsumme')
    a = g.get('aufruf')
    if a is not None:
        if not isinstance(a, dict) or set(a) != set(AUFRUF_FELDER) or 'generator' not in (a.get('stroeme') or {}):
            raise HerkunftFehler(f'Generatornachweis: aufruf mit genau den Feldern {list(AUFRUF_FELDER)} und dem '
                                 'Namen des Generatorstroms erwartet')
        if strom_sha256(zufall.strom(int(a['seed']), a['stroeme']['generator'])) != g['strom_sha256']:
            raise HerkunftFehler(f'Generatornachweis: Seed {a["seed"]} und Strom „{a["stroeme"]["generator"]}“ des '
                                 'Aufrufs ergeben nicht den Zustand des verwendeten Zufallsstroms')
    return formate._json_wert({feld: g.get(feld) for feld in GENERATOR_FELDER})


def mit_aufruf(tab, szenario, stufe, seed, stroeme):
    """Ergänzt den Generatornachweis einer Tabelle um den Aufruf, mit dem sie erzeugt wurde (geprüft)."""
    g = tab.meta.get(zf.META_GENERATORNACHWEIS)
    if not isinstance(g, dict):
        raise HerkunftFehler('Tabelle ohne Generatornachweis: Aufruf nicht ergänzbar')
    tab.meta[zf.META_GENERATORNACHWEIS] = pruefe_generatornachweis(
        dict(g, aufruf=dict(szenario=szenario, stufe=stufe, seed=int(seed), stroeme=dict(stroeme))))
    return tab


def nachweis(tab):
    """Herkunftsnachweis der Läufe einer Tabelle (LaufTabelle, in der Regel die Phase-0-Läufe eines Satzes)."""
    if not len(tab):
        raise HerkunftFehler('keine Läufe: Herkunft nicht belegbar')
    datenart = tab.meta.get('datenart') or 'synthetisch'
    if datenart not in formate.DATENARTEN:
        raise HerkunftFehler(f'Datenart {datenart!r} unbekannt')
    koepfe = sorted(tab.koepfe, key=lambda k: int(k['position']))
    for name, werte in (('Positionen', [int(k['position']) for k in koepfe]),
                        ('Lauf-IDs', [k['lauf_id'] for k in koepfe])):
        doppelt = sorted(x for x, n in Counter(werte).items() if n > 1)
        if doppelt:
            raise HerkunftFehler(f'{name} mehrfach vergeben ({doppelt[:5]}): die Läufe sind nicht eindeutig geordnet')
    laeufe = [lauf_nachweis(k) for k in koepfe]
    doppelt = sorted(x for x, n in Counter(l['hash_rohdatei'] for l in laeufe if l['klasse'] == 'rohdatei').items()
                     if n > 1)
    if doppelt:
        raise HerkunftFehler(f'derselbe Rohdatei-Hash bei mehreren Läufen ({doppelt[0][:12]}…): jede Rohdatei gehört '
                             'zu genau einem Lauf')
    klassen = {x: sum(l['klasse'] == x for l in laeufe) for x in KLASSEN}
    generator = None
    if klassen['generator']:
        if datenart == 'messung':
            raise HerkunftFehler('Datenart messung: Läufe ohne Rohdatei (Ebene H) sind nicht zulässig')
        generator = pruefe_generatornachweis(tab.meta.get(zf.META_GENERATORNACHWEIS))
    return formate._json_wert(dict(version=VERSION, datenart=datenart, klassen=klassen,
                                   optionale_felder=sorted(n for n in zf.OPTIONALE_FELDER if n in tab.daten),
                                   laeufe=laeufe, generator=generator))


def sha256(nw):
    """Die Bindung: SHA-256 des Nachweises in kanonischer JSON-Form."""
    return formate.sha256_json(nw)


def unterschied(erwartet, vorgefunden):
    """Erster Unterschied des vorgefundenen Nachweises gegenüber dem erwarteten in Worten (für Fehlermeldungen):
    Kopfangaben, Generatornachweis, fehlende oder zusätzliche Läufe, dann die Angaben je Lauf. „kein Unterschied“ bei
    Gleichheit."""
    a, b = erwartet, vorgefunden
    if not isinstance(a, dict) or not isinstance(b, dict):
        return 'ein Nachweis fehlt'
    for feld in ('version', 'datenart', 'optionale_felder'):
        if a.get(feld) != b.get(feld):
            return f'{feld}: {b.get(feld)!r} statt {a.get(feld)!r}'
    ga, gb = a.get('generator'), b.get('generator')
    if ga != gb and ga is not None and gb is not None:
        return 'Generatornachweis: ' + ', '.join(x for x in GENERATOR_FELDER if ga.get(x) != gb.get(x)) + ' abweichend'
    la = {l['lauf_id']: l for l in a.get('laeufe', [])}
    lb = {l['lauf_id']: l for l in b.get('laeufe', [])}
    fehlt, mehr = [x for x in la if x not in lb], [x for x in lb if x not in la]
    if fehlt or mehr:
        x, wort = (fehlt, 'fehlt' if len(fehlt) == 1 else 'fehlen') if fehlt else (mehr, 'zusätzlich')
        return f'{len(x)} {"Lauf" if len(x) == 1 else "Läufe"} {wort} (erster: {x[0]})'
    for lid, l in la.items():
        ab = [x for x in sorted(set(l) | set(lb[lid])) if l.get(x) != lb[lid].get(x)]
        if ab:
            return f'Lauf {lid}: {", ".join(ab)} abweichend'
    if ga != gb:
        return 'Generatornachweis nur auf einer Seite'
    if a.get('klassen') != b.get('klassen'):
        return f'klassen: {b.get("klassen")!r} statt {a.get("klassen")!r}'
    if [l['lauf_id'] for l in a.get('laeufe', [])] != [l['lauf_id'] for l in b.get('laeufe', [])]:
        return 'Reihenfolge der Läufe abweichend'
    return 'kein Unterschied'
