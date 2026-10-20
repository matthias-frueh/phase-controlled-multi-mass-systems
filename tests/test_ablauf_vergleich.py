"""Treiber der begrenzten Entwicklungsrechnung (harness.ablauf_vergleich): Auftragsliste im Budget, gemeinsame Seeds
mit PR #22, Checkpoint-Schlüssel mit Verfahren, schlanker Befund je Variante; Berichtsteil (Tabellen einsetzen)."""
import json
import os

import pytest

from pcmms_auswertung import regeln, verfahren as vf
from pcmms_auswertung.harness import ablauf_vergleich as av, ablauf_vergleich_bericht as avb, kampagnen, neulauf

KLEIN = dict(plan=dict(n0=20, n_pilot=20, n_bloecke=3), n_min=2, profil='ENTW-2026-10',
             profil_reduktion=dict(bootstrap_B=100, h3_mc=100, eps_ctrl_datensaetze=200))
KLEIN['profil_sha256'] = regeln.profil('ENTW-2026-10').mit_reduktion(**KLEIN['profil_reduktion']).sha256()


def test_auftragsliste_im_budget_mit_gemeinsamen_seeds():
    jobs = av.auftragsliste()
    n = sum(len(j['seeds']) * (2 if j['art'] == 'fortsetzung' else 1) for j in jobs)
    voll = sum(len(j['seeds']) for j in jobs if j['art'] == 'voll')
    assert n <= 120 and voll <= 12
    vergleich = [j for j in jobs if j['seedregel'] == 'vergleich' and j['art'] == 'schlank']
    assert sum(len(j['seeds']) for j in vergleich) == 90
    for sid in av.SYSTEME:
        pr22 = [kampagnen.kampagnen_seed(20261017, 'diagnose_g4', sid, 'L1', i) for i in range(10)]
        for v in av.VARIANTEN:
            s = [x for j in vergleich if j['szenario'] == sid and j['variante'] == v for x in j['seeds']]
            assert s == pr22                                              # dieselben Seeds in allen drei Varianten


def test_auftragsliste_der_korrekturrunde_im_zusatzbudget(tmp_path):
    """Korrekturrunde vom 18.10.2026: höchstens 40 Ausführungen, davon höchstens vier volle; die 30 Vergleichskampagnen
    der Variante „wiederholungen“ und alle übrigen Aufträge mit den Seeds der ursprünglichen Auftragsliste; gemeinsame
    Einstellungen bis auf das Checkpoint-Verzeichnis gleich; die committete Liste gleicht der erzeugten."""
    jobs = av.auftragsliste_korrektur()
    n = sum(len(j['seeds']) * (2 if j['art'] == 'fortsetzung' else 1) for j in jobs)
    voll = sum(len(j['seeds']) for j in jobs if j['art'] == 'voll')
    assert n <= av.KORREKTUR_GRENZEN['kampagnen'] and voll <= av.KORREKTUR_GRENZEN['voll']
    vergleich = [j for j in jobs if j['seedregel'] == 'vergleich' and j['art'] == 'schlank'
                 and j['variante'] == 'wiederholungen']
    assert sum(len(j['seeds']) for j in vergleich) == 30
    alt = {(j['szenario'], j['variante'], j['art'], j['ebene'], j['seedregel'], i): s
           for j in av.auftragsliste() for i, s in zip(j['indizes'], j['seeds'])}
    for j in jobs:
        for i, s in zip(j['indizes'], j['seeds']):
            assert alt[(j['szenario'], j['variante'], j['art'], j['ebene'], j['seedregel'], i)] == s
    a = av.vorbereiten_korrektur(str(tmp_path))
    orig = av.lies_auftrag()
    assert a['gemeinsam'] == dict(orig['gemeinsam'], ausgabe=av.KORREKTUR_AUSGABE) and a['werkzeug8'] == orig['werkzeug8']
    assert av.lies_auftrag(av.KORREKTUR_AUFTRAG) == a


def test_checkpointschluessel_enthaelt_das_verfahren():
    a = dict(gemeinsam=KLEIN)
    prof = regeln.profil('ENTW-2026-10').mit_reduktion(**KLEIN['profil_reduktion'])
    j1 = av._job('x', 'N01-A4', 'k_konsistent', [0])
    j2 = dict(j1, variante='wiederholungen')
    k1, k2 = av.schluessel(a, j1, prof, None), av.schluessel(a, j2, prof, None)
    assert k1['verfahren'] == vf.STATISCH.kennung() and k2['verfahren'] == vf.ZUSTAND_HISTORISCH.kennung() and k1 != k2


def test_berichtstabellen_lassen_den_text_zwischen_leeren_markierungen_stehen():
    text = ('A\n<!-- tabelle:a -->\n<!-- /tabelle -->\nText zwischen den Tabellen\n<!-- tabelle:b -->\n| alt |\n'
            '<!-- /tabelle -->\nEnde\n')
    neu = avb.einsetzen(text, dict(a='| x |', b='| y |'))
    assert neu == ('A\n<!-- tabelle:a -->\n| x |\n<!-- /tabelle -->\nText zwischen den Tabellen\n<!-- tabelle:b -->\n'
                   '| y |\n<!-- /tabelle -->\nEnde\n')
    assert avb.einsetzen(neu, dict(a='| x |', b='| y |')) == neu                  # wiederholbar
    lo, hi = avb.wilson(4, 30)
    assert abs(lo - 0.0531) < 1e-3 and abs(hi - 0.2968) < 1e-3


@pytest.mark.parametrize('variante, k', [('historisch', 30), ('k_konsistent', 9), ('wiederholungen', 9)])
def test_schlanker_befund_je_variante(variante, k):
    seed = av.vergleichs_seeds('N01-A4')[0]
    b = av.kampagne(('N01-A4', variante, 0, seed, 'schlank', 'H', KLEIN, None))
    assert b['teil_b']['k'] == k and b['teil_b']['k_max'] == 9
    assert b['verfahren'] == av.VARIANTEN[variante].kennung()
    assert b['auswertbar']['von'] == 21 and ('ablauf' in b) == (variante == 'wiederholungen')
    if variante == 'wiederholungen':                                    # Referenzbezüge der X′, S2-Bilanz
        assert all(x['vor_rolle'] and x['vorgesehen'] in (True, False) for x in b['ablauf']['x_strich'])
        assert all(isinstance(x['vorpruefung_ablauf_1'], bool) for x in b['ablauf']['x_strich'] if x['vor'])
        assert b['ablauf']['s2_bilanz']['beendet'] is False and b['ablauf']['s2_waehrend_halt'] == 0


def _befund(**ablauf):
    a = dict(status='abgeschlossen', halt=None, grund='alle Blöcke gemessen', laufzahl=dict(ausgefuehrt=700, zusaetzlich=70),
             messzeit_s=dict(realisiert_laeufe=11900.0, realisiert_spanne=11900.0), halte=[], rollen=dict(R1=3),
             auswahl=dict(gueltig=500, ersetzt=4), auswahl_status={'S100|1': 'ersetzt'}, x_strich=[], s2_waehrend_halt=0)
    a.update(ablauf)
    return dict(vollstaendig=True, auswertbar=dict(n=21, min_gueltig=23), phase1=dict(konfig_g4=20, S2=0), sperren=[],
                teil_b=dict(p_hat=0.01), ablauf=a)


def test_vorher_nachher_ursachen_ohne_kampagnen():
    """Vorher/Nachher je Kampagne (Korrekturrunde): gleiche Befunde, nur ein anderer Platzstatus, eine Abzweigung an einem
    X′ (unter ablauf-1 mit R₁) und ein unerklärter Unterschied werden unterschieden."""
    alt = _befund()
    assert avb.vorher_nachher_kampagne(alt, _befund())['gleich']
    d = avb.vorher_nachher_kampagne(alt, _befund(auswahl_status={'S100|1': 'ersetzt', 'S102|3': 'fehlt: Halt'}))
    assert not d['gleich'] and d['plaetze'] == {'S102|3': ['gueltig', 'fehlt: Halt']}
    assert d['ursache'] and d['ursache'][0].startswith('Platzstatus')
    x = dict(versuch='V00042', konfiguration='S104', block=2, abweichung_r0_N=0.0003, vorpruefung_ablauf_1=True,
             g1=False, vorgesehen=True, gueltig=True)
    d = avb.vorher_nachher_kampagne(alt, _befund(x_strich=[x], rollen=dict(R1=2), laufzahl=dict(ausgefuehrt=699,
                                                                                                zusaetzlich=69)))
    assert d['rollen'] == {'R1': [3, 2]} and 'V00042' in d['ursache'][0] and 'ablauf-1' in d['ursache'][0]
    d = avb.vorher_nachher_kampagne(alt, _befund(status='angehalten', halt='S3', grund='S3: Drift'))
    assert d['ursache'] == ['ungeklärt: grund, halt, status']
    s = avb._x_strich_summe([x, dict(x, g1=None, gueltig=False, abweichung_r0_N=None, vorpruefung_ablauf_1=None)],
                            [0.0004, 0.0004])
    assert (s['n'], s['g1_geprueft'], s['andere_ungueltig'], s['vorpruefung_ablauf_1']) == (2, 1, 1, 1)
    assert s['max_verhaeltnis_eps'] == pytest.approx(0.75)


def test_ergebnisse_der_korrekturrunde_gelten_fuer_ablauf_3():
    """Nachtrag (ablauf-3): ablauf-3 entscheidet nur dann anders als ablauf-2, wenn ein nach G2–G10 gültiges X′ eine
    S3-Wiederholung auslöst; sie folgt jetzt nach R₃, unter ablauf-2 stand sie zwischen X′ und dem Referenzlauf, der es
    schließt. In den 37 neu gerechneten Ablaufkampagnen der Korrekturrunde (ergebnisse.json, Befunde aus den Checkpoints)
    folgt auf jedes X′ mit G1-Prüfung unmittelbar sein R₃; nur eines ist ein Kontrolllauf. Die Ergebnisse gelten deshalb
    unverändert für ablauf-3."""
    with open(os.path.join(neulauf.WURZEL, av.DOKU_REL, 'ergebnisse.json'), encoding='utf-8') as f:
        vn = json.load(f)['vorher_nachher']
    xs = [x for k in vn for x in k['x_strich']]
    geprueft = [x for x in xs if x['g1'] is not None]
    assert (len(vn), len(xs), len(geprueft)) == (37, 35, 33)
    assert all(x['nach_rolle'] == 'R3' and int(x['nach'][1:]) == int(x['versuch'][1:]) + 1 for x in geprueft)
    assert all(x['halt'] in (None, 'S1') for x in xs)
    assert [x['konfiguration'] for x in geprueft if x['konfiguration'] in ('L1', 'L2', 'L3')] == ['L1']
