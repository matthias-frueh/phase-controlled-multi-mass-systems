"""Software-Prüfsatz (Plan AP-13, K20; Auftrag Etappe 5): Hashes von Katalog, Seeds, Regelprofilen und Testdaten.

Das fixiert einen reproduzierbaren Prüfsatz der Software, nicht Teil A der Präregistrierung. Die Testdaten sind die
Generatorausgaben (P0-Daten und Laufzusammenfassungen auf Ebene H) der festen Prüfkampagnen; ihre Werte werden vor dem
Hashen auf 12 Nachkommastellen (N, °) gerundet, damit Rundungsunterschiede verschiedener BLAS-Bibliotheken im
letzten Bit den Hash nicht ändern. Die Datei nennt die Umgebung, unter der sie erzeugt wurde.

Wertevergleich mit Toleranz (14.11.2026; Entscheidung E-4 vom 12.11.2026). Die Rundung reicht nicht: Die Prüfsummen
der berechneten Felder (RECHNERGEBUNDEN) hängen am Rechenkern von OpenBLAS und, weil sie über komprimierte NPZ-Bytes
gebildet sind, am zlib des Systems. Sie gelten für die Umgebung, in der der Prüfsatz entstand (Rechenkern SkylakeX,
zlib 1.3). pruefen() vergleicht deshalb getrennt:

- exakt: Plan, Seeds, Profile, normative Zahlen, Katalog, Laufköpfe, Laufzahl, das Skelett der P0-Messung;
- mit Toleranz: die berechneten Felder über ihre Kennwerte (kennwerte.py). Die Bezugswerte stehen in einer eigenen
  Datei neben dem Prüfsatz (<Pfad>_kennwerte.json); sie nennt die SHA-256-Prüfsumme der Prüfsatz-Datei, zu der sie
  gehört, die Toleranz und die Umgebung ihrer Erzeugung. Die Prüfsatz-Datei selbst bleibt unverändert;
- zur Auskunft: ob die Prüfsummen der berechneten Felder bitgleich wiederkehren (bitgleich). Das geht nicht in
  „gleich“ ein; wer es verlangt (derselbe Rechenkern, dasselbe zlib), prüft r['bitgleich'].
"""
import importlib
import json
import os
import platform
import zlib

import numpy as np
import scipy

from .. import formate, kennwerte, regeln, zufall, zusammenfassung as zf
from ..generator import kalibrierdaten, kampagne as kp, szenarien
from . import kette

STELLEN = 12
PRUEFKAMPAGNEN = (('N01-A4', 'L1', 7), ('N03-ungleich', 'L1', 7), ('A04-R4', 'L1', 7), ('H01-zelt', 'L1', 7),
                  ('C03-GF5', 'L1', 7), ('I01-amplitude', 'L1', 7), ('S06-saettigung', 'L1', 7))
PRUEFPLAN = dict(n0=20, n_pilot=20, n_bloecke=24)
PROFILE = ('AF-2026-10', 'ENTW-2026-10')
RECHNERGEBUNDEN = ('zusammenfassungen', 'p0_messung')   # Prüfsummen über berechnete Felder: an Rechenkern und zlib
KENNWERTE_ZUSATZ = '_kennwerte'                         # <Pfad>_kennwerte.json: Bezugswerte des Wertevergleichs


def _rund(x):
    a = np.asarray(x)
    if np.iscomplexobj(a):
        return np.round(a.real, STELLEN) + 1j * np.round(a.imag, STELLEN)
    if np.issubdtype(a.dtype, np.floating):
        return np.round(a, STELLEN)
    return a


def hash_felder(felder, ohne=()):
    """Prüfsumme gerundeter Felder; ohne: Felder, die es zum Stand eines historischen Prüfsatzes noch nicht gab."""
    return formate.sha256_bytes(formate.npz_bytes({k: _rund(v) for k, v in felder.items() if k not in ohne}))


HISTORISCH_OHNE = tuple(zf.OPTIONALE_FELDER)   # Fünftelzeiger seit 20.10.2026: nicht in historischen Prüfsummen


def hash_objekt(obj):
    skelett, felder = formate.zerlege(obj)
    return formate.sha256_json(dict(skelett=skelett, felder=hash_felder(felder)))


def katalog_hash():
    """Katalogtabelle und vollständige Modellbeschreibung je Szenario (Stufe L1, Plan des Prüfsatzes)."""
    plan = kp.plan_aus_dict(PRUEFPLAN)
    besch = {sid: szenarien.beschreibung(szenarien.modell(sid, 'L1', plan=plan)) for sid in szenarien.KATALOG}
    return formate.sha256_json(dict(tabelle=szenarien.katalog_tabelle(), modelle=besch))


def testdaten(sid, stufe, seed):
    """Prüfsummen der Testdaten einer Prüfkampagne (wie im Prüfsatz) und die Bezugsgrößen des Wertevergleichs:
    Kennwerte der Laufzusammenfassungen und der Felder der P0-Messung, dazu die Prüfsumme ihres Skeletts (exakt)."""
    plan = kp.plan_aus_dict(PRUEFPLAN)
    m, laeufe, tab = kette.kampagne_erzeugen(sid, stufe, plan, seed)
    sz = szenarien.KATALOG[sid]
    kw = {a: b for a, b in sz.kalibrierung}
    mes, _ = kalibrierdaten.p0_messungen(m.system, zufall.strom(seed, 'p0'), p01=kw.get('p01'), p04=kw.get('p04'),
                                         p05=kw.get('p05'))
    skelett, felder = formate.zerlege(mes)
    h = dict(zusammenfassungen=hash_felder(tab.daten, HISTORISCH_OHNE), koepfe=formate.sha256_json(tab.koepfe),
             p0_messung=hash_objekt(mes), n_laeufe=len(tab))
    werte = dict(zusammenfassungen=kennwerte.felder(tab.daten), p0_messung=kennwerte.felder(felder),
                 p0_skelett_sha256=formate.sha256_json(skelett))
    return h, werte


def testdaten_hash(sid, stufe, seed):
    return testdaten(sid, stufe, seed)[0]


def _erstellen(mit_katalog=True):
    """Prüfsatz und, je Prüfkampagne, die Bezugsgrößen des Wertevergleichs."""
    td = {f'{s}/{st}/{sd}': testdaten(s, st, sd) for s, st, sd in PRUEFKAMPAGNEN}
    out = dict(beschreibung='Software-Prüfsatz AP-11 bis AP-13 (kein Einfrieren von Teil A)',
               umgebung=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
               rundung_stellen=STELLEN, plan=PRUEFPLAN,
               seeds=[dict(szenario=s, stufe=st, seed=sd) for s, st, sd in PRUEFKAMPAGNEN],
               profile={p: regeln.profil(p).sha256() for p in PROFILE},
               normative_zahlen=dict(regeln.NORMATIVE_ZAHLEN),
               testdaten={k: v[0] for k, v in td.items()})
    if mit_katalog:
        out['katalog'] = katalog_hash()
    out['sha256_gesamt'] = formate.sha256_json({k: v for k, v in out.items() if k != 'umgebung'})
    return out, {k: v[1] for k, v in td.items()}


def erstellen(mit_katalog=True):
    return _erstellen(mit_katalog)[0]


def schreiben(pfad, ps=None):
    """Schreibt einen neuen Prüfsatz und die Kennwerte seiner berechneten Felder (<Pfad>_kennwerte.json). Mit einem
    übergebenen Prüfsatz ps entsteht nur die Prüfsatz-Datei; die Kennwerte schreibt dann schreiben_kennwerte."""
    if ps is not None:
        formate.schreibe_objekt(pfad, formate.kopf('pruefsatz', formate.synth_kennung('PRUEFSATZ')), ps)
        return ps
    ps, werte = _erstellen()
    formate.schreibe_objekt(pfad, formate.kopf('pruefsatz', formate.synth_kennung('PRUEFSATZ')), ps)
    kennwerte_schreiben(pfad, werte, True, formate.synth_kennung('PRUEFSATZ', 'KENNWERTE'))
    return ps


def _vergleich_exakt(alt, neu):
    """Exakte Teile und Prüfsummen der berechneten Felder: (Abweichungen, abweichende Prüfsummen)."""
    abw, summen = [], []
    for k in ('plan', 'seeds', 'profile', 'normative_zahlen', 'katalog', 'rundung_stellen'):
        if k in alt and formate.sha256_json(alt[k]) != formate.sha256_json(neu.get(k)):
            abw.append(k)
    for k, v in alt['testdaten'].items():
        n = neu['testdaten'].get(k)
        if n is None:
            abw.append(f'testdaten {k}: fehlt')
            continue
        for x, w in v.items():
            if n.get(x) != w:
                (summen if x in RECHNERGEBUNDEN else abw).append(f'testdaten {k}: {x}')
    return abw, summen


def pruefen(pfad):
    """Vergleicht den gespeicherten Prüfsatz mit einer Neuberechnung: exakte Teile exakt, berechnete Felder über ihre
    Kennwerte mit Toleranz (Datei <Pfad>_kennwerte.json). Rückgabe dict(gleich, abweichungen, bitgleich,
    pruefsummen_abweichend, werte, umgebung_alt, umgebung_neu): gleich – exakte Teile gleich und Werte innerhalb der
    Toleranz; bitgleich – auch die Prüfsummen der berechneten Felder kehren wieder (nur bei gleichem Rechenkern und
    zlib zu erwarten); werte – Ergebnis des Wertevergleichs mit Auslastung der Toleranz."""
    _, alt = formate.lies_objekt(pfad, 'pruefsatz')
    neu, werte = _erstellen(mit_katalog='katalog' in alt)
    abw, summen = _vergleich_exakt(alt, neu)
    v = kennwerte_vergleichen(kennwerte_lesen(pfad), werte)
    return dict(gleich=not (abw or v['abweichungen']), abweichungen=abw + v['abweichungen'], bitgleich=not summen,
                pruefsummen_abweichend=summen, werte={k: w for k, w in v.items() if k != 'abweichungen'},
                umgebung_alt=alt['umgebung'], umgebung_neu=umgebung())


def schreiben_kennwerte(pfad, erzwingen=False):
    """Bezugswerte des Wertevergleichs zu einem vorhandenen Prüfsatz (die Prüfsatz-Datei bleibt unverändert). Verlangt,
    dass die Neuberechnung die exakten Teile und – ohne erzwingen – auch die Prüfsummen der berechneten Felder
    bitgleich wiedergibt: Die Kennwerte stammen dann aus genau der Rechnung, die der Prüfsatz festhält."""
    _, alt = formate.lies_objekt(pfad, 'pruefsatz')
    neu, werte = _erstellen(mit_katalog='katalog' in alt)
    abw, summen = _vergleich_exakt(alt, neu)
    kennwerte_pruefe_anker(abw, summen, erzwingen)
    return kennwerte_schreiben(pfad, werte, not summen, formate.synth_kennung('PRUEFSATZ', 'KENNWERTE'))


# ── Kennwerte neben einem Prüfsatz (auch für harness.ablauf_pruefsatz) ───────────────────────────────
def umgebung():
    """Umgebung der Rechnung: Versionen, zlib und, wenn threadpoolctl installiert ist, Rechenkern und Thread-Zahl der
    geladenen BLAS-Bibliotheken (sonst None; die Tests brauchen das Paket nicht)."""
    out = dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
               zlib=zlib.ZLIB_RUNTIME_VERSION, maschine=platform.machine(), blas=None)
    try:
        from threadpoolctl import threadpool_info
    except ImportError:
        return out
    importlib.import_module('scipy.linalg')                              # lädt auch die BLAS von SciPy
    out['blas'] = sorted({(b.get('internal_api'), b.get('version'), b.get('architecture'), b.get('num_threads'))
                          for b in threadpool_info() if b.get('user_api') == 'blas'})
    out['blas'] = [dict(bibliothek=a, version=v, rechenkern=k, threads=t) for a, v, k, t in out['blas']]
    return out


def kennwerte_pruefe_anker(abw, summen, erzwingen=False):
    if abw:
        raise ValueError(f'Kennwerte zum Prüfsatz: Die Neuberechnung weicht in exakten Teilen ab ({abw[:3]}); der '
                         'Prüfsatz passt nicht zu diesem Softwarestand')
    if summen and not erzwingen:
        raise ValueError('Kennwerte zum Prüfsatz: Die Prüfsummen der berechneten Felder kehren hier nicht bitgleich '
                         f'wieder ({len(summen)} abweichend; anderer Rechenkern oder anderes zlib als bei der '
                         'Erzeugung des Prüfsatzes). Kennwerte nur in der Umgebung des Prüfsatzes erzeugen oder '
                         'ausdrücklich erzwingen')


def _einzeilig(o, ein=0, grenze=400):
    """JSON-Text mit Einrückung; ein dict, das in eine Zeile der Länge grenze passt und keine dicts mit dicts enthält,
    steht in einer Zeile (die Kennwerte eines Feldes)."""
    if isinstance(o, dict):
        kurz = json_zeile(o)
        if len(kurz) <= grenze and not any(isinstance(w, dict) and any(isinstance(x, dict) for x in w.values())
                                           for w in o.values()):
            return kurz
        teile = [f'{" " * (ein + 1)}{json_zeile(str(k))}: {_einzeilig(o[k], ein + 1, grenze)}' for k in sorted(o)]
        return '{\n' + ',\n'.join(teile) + '\n' + ' ' * ein + '}'
    return json_zeile(o)


def json_zeile(o):
    return json.dumps(formate._json_wert(o), ensure_ascii=False, sort_keys=True, allow_nan=False)


def kennwerte_schreiben(pfad, werte, bitgleich, kennung):
    """Schreibt <pfad>_kennwerte.json: Kennwerte je Eintrag des Prüfsatzes, Toleranz, Umgebung und die Prüfsumme der
    Prüfsatz-Datei, zu der sie gehören."""
    k = formate.kopf('pruefsatz', kennung)
    obj = dict(kopf=k, inhalt=dict(
        beschreibung='Kennwerte der berechneten Felder zu einem Prüfsatz: Bezugswerte des Wertevergleichs mit '
                     'Toleranz (kennwerte.py). Die Prüfsummen dieser Felder im Prüfsatz gelten nur für Rechenkern und '
                     'zlib seiner Erzeugung.',
        version=kennwerte.VERSION, toleranz=kennwerte.toleranz(),
        pruefsatz=dict(datei=os.path.basename(pfad) + '.json', sha256=formate.sha256_datei(pfad + '.json')),
        pruefsummen_bitgleich=bool(bitgleich), umgebung=umgebung(), kennwerte=werte))
    with open(pfad + KENNWERTE_ZUSATZ + '.json', 'w', encoding='utf-8') as f:
        f.write(_einzeilig(obj) + '\n')
    return obj['inhalt']


def kennwerte_lesen(pfad):
    """Liest <pfad>_kennwerte.json und prüft, dass die Datei zu genau dieser Prüfsatz-Datei gehört."""
    p = pfad + KENNWERTE_ZUSATZ
    if not os.path.exists(p + '.json'):
        raise formate.FormatFehler(f'Kennwerte zum Prüfsatz fehlen ({p}.json): Die Prüfsummen der berechneten Felder '
                                   'gelten nur für einen Rechenkern; ohne Kennwerte sind die Werte nicht prüfbar')
    _, k = formate.lies_objekt(p, 'pruefsatz')
    if k.get('version') != kennwerte.VERSION:
        raise formate.FormatFehler(f'{p}.json: Kennwerte in der Fassung {k.get("version")!r} statt '
                                   f'{kennwerte.VERSION!r}')
    if (k.get('pruefsatz') or {}).get('sha256') != formate.sha256_datei(pfad + '.json'):
        raise formate.FormatFehler(f'{p}.json gehört zu einer anderen Fassung der Prüfsatz-Datei (SHA-256 der Datei '
                                   'stimmt nicht)')
    return k


def kennwerte_vergleichen(bezug, werte):
    """Wertevergleich je Eintrag: Zeichenketten (Prüfsummen exakter Teile) exakt, Feldsätze über ihre Kennwerte mit
    der Toleranz der Bezugsdatei. Rückgabe dict(abweichungen, kennwerte_gleich, auslastung, stelle_auslastung,
    toleranz)."""
    tol = bezug['toleranz']
    abw, last, wo, genau = [], 0.0, None, True
    for key in sorted(set(bezug['kennwerte']) | set(werte)):
        a, b = bezug['kennwerte'].get(key), werte.get(key)
        if a is None or b is None:
            abw.append(f'{key}: ' + ('fehlt' if b is None else 'ohne Bezugswerte'))
            genau = False
            continue
        for teil in sorted(set(a) | set(b)):
            x, y = a.get(teil), b.get(teil)
            if isinstance(x, dict) and isinstance(y, dict):
                v = kennwerte.vergleich_felder(x, y, tol['rtol'], tol['atol'])
                abw += [f'{key}: {teil}: {t}' for t in v['abweichungen']]
                genau = genau and v['kennwerte_gleich']
                if v['auslastung'] > last:
                    last, wo = v['auslastung'], f'{key}: {teil}: {v["feld_auslastung"]}'
            elif x != y:
                abw.append(f'{key}: {teil}')
                genau = False
    return dict(abweichungen=abw, kennwerte_gleich=genau, auslastung=last, stelle_auslastung=wo,
                toleranz=dict(rtol=tol['rtol'], atol=tol['atol']))
