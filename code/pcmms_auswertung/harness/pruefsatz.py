"""Software-Prüfsatz (Plan AP-13, K20; Auftrag Etappe 5): Hashes von Katalog, Seeds, Regelprofilen und Testdaten.

Das fixiert einen reproduzierbaren Prüfsatz der Software, nicht Teil A der Präregistrierung. Die Testdaten sind die
Generatorausgaben (P0-Daten und Laufzusammenfassungen auf Ebene H) der festen Prüfkampagnen; ihre Werte werden vor dem
Hashen auf 12 Nachkommastellen (N, °) gerundet, damit Rundungsunterschiede verschiedener BLAS-Bibliotheken im
letzten Bit den Hash nicht ändern. Die Datei nennt die Umgebung, unter der sie erzeugt wurde.
"""
import platform

import numpy as np
import scipy

from .. import formate, regeln, zufall
from ..generator import kalibrierdaten, kampagne as kp, szenarien
from . import kette

STELLEN = 12
PRUEFKAMPAGNEN = (('N01-A4', 'L1', 7), ('N03-ungleich', 'L1', 7), ('A04-R4', 'L1', 7), ('H01-zelt', 'L1', 7),
                  ('C03-GF5', 'L1', 7), ('I01-amplitude', 'L1', 7), ('S06-saettigung', 'L1', 7))
PRUEFPLAN = dict(n0=20, n_pilot=20, n_bloecke=24)
PROFILE = ('AF-2026-10', 'ENTW-2026-10')


def _rund(x):
    a = np.asarray(x)
    if np.iscomplexobj(a):
        return np.round(a.real, STELLEN) + 1j * np.round(a.imag, STELLEN)
    if np.issubdtype(a.dtype, np.floating):
        return np.round(a, STELLEN)
    return a


def hash_felder(felder):
    return formate.sha256_bytes(formate.npz_bytes({k: _rund(v) for k, v in felder.items()}))


def hash_objekt(obj):
    skelett, felder = formate.zerlege(obj)
    return formate.sha256_json(dict(skelett=skelett, felder=hash_felder(felder)))


def katalog_hash():
    """Katalogtabelle und vollständige Modellbeschreibung je Szenario (Stufe L1, Plan des Prüfsatzes)."""
    plan = kp.plan_aus_dict(PRUEFPLAN)
    besch = {sid: szenarien.beschreibung(szenarien.modell(sid, 'L1', plan=plan)) for sid in szenarien.KATALOG}
    return formate.sha256_json(dict(tabelle=szenarien.katalog_tabelle(), modelle=besch))


def testdaten_hash(sid, stufe, seed):
    plan = kp.plan_aus_dict(PRUEFPLAN)
    m, laeufe, tab = kette.kampagne_erzeugen(sid, stufe, plan, seed)
    sz = szenarien.KATALOG[sid]
    kw = {a: b for a, b in sz.kalibrierung}
    mes, _ = kalibrierdaten.p0_messungen(m.system, zufall.strom(seed, 'p0'), p01=kw.get('p01'), p04=kw.get('p04'),
                                         p05=kw.get('p05'))
    return dict(zusammenfassungen=hash_felder(tab.daten), koepfe=formate.sha256_json(tab.koepfe),
                p0_messung=hash_objekt(mes), n_laeufe=len(tab))


def erstellen(mit_katalog=True):
    out = dict(beschreibung='Software-Prüfsatz AP-11 bis AP-13 (kein Einfrieren von Teil A)',
               umgebung=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
               rundung_stellen=STELLEN, plan=PRUEFPLAN,
               seeds=[dict(szenario=s, stufe=st, seed=sd) for s, st, sd in PRUEFKAMPAGNEN],
               profile={p: regeln.profil(p).sha256() for p in PROFILE},
               normative_zahlen=dict(regeln.NORMATIVE_ZAHLEN),
               testdaten={f'{s}/{st}/{sd}': testdaten_hash(s, st, sd) for s, st, sd in PRUEFKAMPAGNEN})
    if mit_katalog:
        out['katalog'] = katalog_hash()
    out['sha256_gesamt'] = formate.sha256_json({k: v for k, v in out.items() if k != 'umgebung'})
    return out


def schreiben(pfad, ps=None):
    ps = ps or erstellen()
    formate.schreibe_objekt(pfad, formate.kopf('pruefsatz', formate.synth_kennung('PRUEFSATZ')), ps)
    return ps


def pruefen(pfad):
    """Vergleicht den gespeicherten Prüfsatz mit einer Neuberechnung; Rückgabe dict(gleich, abweichungen)."""
    _, alt = formate.lies_objekt(pfad, 'pruefsatz')
    neu = erstellen(mit_katalog='katalog' in alt)
    abw = []
    for k in ('plan', 'seeds', 'profile', 'normative_zahlen', 'katalog', 'rundung_stellen'):
        if k in alt and formate.sha256_json(alt[k]) != formate.sha256_json(neu.get(k)):
            abw.append(k)
    for k, v in alt['testdaten'].items():
        if neu['testdaten'].get(k) != v:
            abw.append(f'testdaten {k}')
    return dict(gleich=not abw, abweichungen=abw, umgebung_alt=alt['umgebung'], umgebung_neu=neu['umgebung'])
