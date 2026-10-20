"""Prüfsatz des zustandsbehafteten Phase-1-Ablaufs (Auftrag vom 17.10.2026, Teil C), getrennt vom Software-Prüfsatz
(harness.pruefsatz, Ablauf „statisch“, unverändert).

Je Prüfkampagne (Ebene H, kleiner Plan): Prüfsummen der ausgeführten Versuche (Datenfelder auf 12 Stellen gerundet wie
harness.pruefsatz, Köpfe mit Ablaufprotokoll), der Entscheidungen und Ziehungen und der Entscheidungsschwellen aus Teil B
(gerundet, ablauf.schwellen_kennung; Teil B als Ganzes enthält den Git-Stand und BLAS-abhängige letzte Bits), dazu
lesbare Inhaltsgrößen (Status, Laufzahlen, Rollen, Auswahl je Konfiguration und Block, Halt, Lücken). pruefen() rechnet neu und vergleicht beides; es
prüft zusätzlich inhaltlich, ohne gespeicherte Sollwerte: Der Fall ohne Ablaufoptionen ergibt dieselben Daten wie der
Laufplan des alten Ablaufs, Laufzahl = ausgeführte geplante + zusätzliche Versuche (alle geplanten genau dann, wenn
der Ablauf abgeschlossen ist), die Auswahl deckt jeden geplanten Platz genau einmal, und die Offline-Gültigkeit von
Stufe 2 gleicht den Entscheidungen des Ablaufs.

Zwei Stände (Auftrag vom 20.10.2026): der historische Prüfsatz (ablauf-3, Profil ENTW-2026-10, Phase-0-Anordnung
„historisch“; Datei tests/fixtures/ap13_ablauf_pruefsatz.json, unverändert) und der Prüfsatz des Regelstands 2026-11
(ablauf-4, ENTW-2026-11, P0.7-Anordnung; tests/fixtures/ap13_ablauf_pruefsatz_ablauf4.json). pruefen() liest den Stand
aus der Datei und rechnet mit genau diesem Stand nach.
"""
import platform

import numpy as np
import scipy

from .. import ablauf, auswertung, formate, regeln, verfahren as vf
from ..generator import kampagne as kp
from . import kette, pruefsatz

PLAN = dict(n0=20, n_pilot=20, n_bloecke=6)
N_MIN = 4
PROFIL = ('ENTW-2026-10', dict(bootstrap_B=200, h3_mc=200, eps_ctrl_datensaetze=300))
FAELLE = (('N01-A4', 'L1', 13, 'zustand'),          # reguläre Wiederholungen, G1 mit R₂/X′/R₃, Alarm, spätes G1
          ('N01-A4', 'L1', 13, 'aus'),              # alle Optionen aus: Daten des alten Laufplans
          ('S06-saettigung', 'L1', 7, 'zustand'),   # Übersteuerung S120 → Ersatz am gezogenen Platz
          ('S02-kontrolllauf', 'L1', 7, 'zustand'),  # Liftoff in L₂ der Phase 1 → S2, Halt
          ('I01-amplitude', 'L1', 7, 'zustand'))    # Einstellung 2: L′, Lücken G2–G4 und S-Regeln für L′


FASSUNG = 'ablauf-3'      # historischer Prüfsatz (PR #23): Fassung ablauf-3, Plan ohne p0_anordnung (historisch)
STAENDE = {'ablauf-3': dict(profil=PROFIL, plan=PLAN),
           'ablauf-4': dict(profil=('ENTW-2026-11', PROFIL[1]), plan=dict(PLAN, p0_anordnung='p07'))}


def _stand(fassung):
    if fassung not in STAENDE:
        raise ValueError(f'Ablauf-Prüfsatz: Fassung {fassung!r} unbekannt ({", ".join(STAENDE)})')
    return STAENDE[fassung]


def _profil(fassung=FASSUNG):
    p = _stand(fassung)['profil']
    return regeln.profil(p[0]).mit_reduktion(**p[1])


def _verfahren(art, fassung=FASSUNG):
    return vf.Verfahren('plan', 'zustand', ablauf.Ablaufoptionen() if art == 'zustand' else ablauf.AUS, fassung)


def fall(sid, stufe, seed, art, fassung=FASSUNG):
    """Eine Prüfkampagne: Ablauf, Tabelle, Bericht und die Prüfsummen."""
    prof = _profil(fassung)
    r = kette.kampagne_ablauf(sid, stufe, kp.plan_aus_dict(_stand(fassung)['plan']), seed, prof, n_min=N_MIN,
                              verfahren=_verfahren(art, fassung))
    a = r['ablauf']
    t1 = a.tabelle()
    b = a.bericht()
    inhalt = dict(status=a.status, halt=(a.z['halt'] or {}).get('regel'), laufzahl=b['laufzahl'], rollen=b['rollen'],
                  auswahl=b['auswahl_zaehler'], s2=b['s2'], luecken=b['luecken'], grenzen=len(b['grenzen']),
                  ziehungen=sum(1 for x in b['ziehungen'] if 'gezogen' in x))
    h = dict(daten=pruefsatz.hash_felder(t1.daten), koepfe=formate.sha256_json(t1.koepfe),
             entscheidungen=formate.sha256_json(a.z['entscheidungen']), ziehungen=formate.sha256_json(a.z['ziehungen']),
             schwellen=a.kennung['schwellen_sha256'])
    return dict(inhalt=inhalt, hashes=h), r


def _gegenprobe(sid, stufe, seed, art, r, fassung=FASSUNG):
    """Inhaltliche Prüfung ohne gespeicherte Sollwerte; Rückgabe Liste der Abweichungen."""
    a, out = r['ablauf'], []
    b = a.bericht()
    lz = b['laufzahl']
    if lz['ausgefuehrt'] != lz['geplant_ausgefuehrt'] + lz['zusaetzlich'] or lz['geplant_ausgefuehrt'] > lz['geplant']:
        out.append('Laufzahl ≠ ausgeführte geplante + zusätzliche Versuche')
    if (a.status == 'abgeschlossen') != (lz['geplant_ausgefuehrt'] == lz['geplant']):
        out.append('abgeschlossener Ablauf ohne alle geplanten Läufe oder umgekehrt')
    n_plaetze = sum(1 for l in a.geplant if l['laufart'] == 'K')
    if len(b['auswahl']) != n_plaetze or any(x['status'] == 'doppelt' for x in b['auswahl'].values()):
        out.append('Auswahl deckt die geplanten Plätze nicht genau einmal')
    tab = kette.ablauf_tabelle(r)
    try:
        auswertung.datenlage(tab, r['teil_b'], _profil(fassung))
    except formate.FormatFehler as e:
        out.append(f'Stufe 2: {e}')
    if art == 'aus':
        m, laeufe, alt = kette.kampagne_erzeugen(sid, stufe, kp.plan_aus_dict(_stand(fassung)['plan']), seed)
        if not all(np.array_equal(alt.daten[f], tab.daten[f], equal_nan=True) for f in alt.daten):
            out.append('ohne Ablaufoptionen: Daten ≠ Laufplan des alten Ablaufs')
        if formate.sha256_json([{k: v for k, v in x.items() if k != 'versuch'} for x in tab.koepfe]) != \
                formate.sha256_json(alt.koepfe):
            out.append('ohne Ablaufoptionen: Köpfe ≠ Laufplan des alten Ablaufs')
    return out


def erstellen(fassung=FASSUNG):
    st_ = _stand(fassung)
    faelle, gegen = {}, {}
    for sid, st, sd, art in FAELLE:
        f, r = fall(sid, st, sd, art, fassung)
        key = f'{sid}/{st}/{sd}/{art}'
        faelle[key] = f
        gegen[key] = _gegenprobe(sid, st, sd, art, r, fassung)
    out = dict(beschreibung='Prüfsatz des zustandsbehafteten Phase-1-Ablaufs (getrennt vom Software-Prüfsatz)',
               umgebung=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
               ablauf_version=fassung, verfahren=_verfahren('zustand', fassung).kennung(), plan=st_['plan'],
               n_min=N_MIN,
               profil=dict(id=st_['profil'][0], reduktion=st_['profil'][1], sha256=_profil(fassung).sha256()),
               rundung_stellen=pruefsatz.STELLEN, faelle=faelle, gegenprobe=gegen)
    out['sha256_gesamt'] = formate.sha256_json({k: v for k, v in out.items() if k != 'umgebung'})
    return out


def schreiben(pfad, ps=None, fassung=FASSUNG):
    ps = ps or erstellen(fassung)
    if any(ps['gegenprobe'].values()):
        raise ValueError(f'Gegenprobe nicht bestanden: {ps["gegenprobe"]}')
    formate.schreibe_objekt(pfad, formate.kopf('pruefsatz', formate.synth_kennung('ABLAUF-PRUEFSATZ')), ps)
    return ps


def pruefen(pfad):
    """Neuberechnung gegen den gespeicherten Prüfsatz: Inhalt, Prüfsummen und Gegenprobe; Rückgabe dict(gleich, …)."""
    _, alt = formate.lies_objekt(pfad, 'pruefsatz')
    neu = erstellen(alt.get('ablauf_version'))
    abw = [k for k in ('ablauf_version', 'verfahren', 'plan', 'n_min', 'profil', 'rundung_stellen')
           if formate.sha256_json(alt.get(k)) != formate.sha256_json(neu.get(k))]
    for key, f in alt['faelle'].items():
        g = neu['faelle'].get(key)
        if g is None:
            abw.append(f'{key}: fehlt')
            continue
        abw += [f'{key}: Inhalt {x}' for x in f['inhalt'] if formate.sha256_json(f['inhalt'][x]) !=
                formate.sha256_json(g['inhalt'].get(x))]
        abw += [f'{key}: Prüfsumme {x}' for x in f['hashes'] if f['hashes'][x] != g['hashes'].get(x)]
    abw += [f'{k}: Gegenprobe {v}' for k, v in neu['gegenprobe'].items() if v]
    return dict(gleich=not abw, abweichungen=abw, umgebung_alt=alt['umgebung'], umgebung_neu=neu['umgebung'],
                inhalt={k: v['inhalt'] for k, v in neu['faelle'].items()})
