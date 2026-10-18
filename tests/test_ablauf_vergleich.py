"""Treiber der begrenzten Entwicklungsrechnung (harness.ablauf_vergleich): Auftragsliste im Budget, gemeinsame Seeds
mit PR #22, Checkpoint-Schlüssel mit Verfahren, schlanker Befund je Variante; Berichtsteil (Tabellen einsetzen)."""
import pytest

from pcmms_auswertung import regeln, verfahren as vf
from pcmms_auswertung.harness import ablauf_vergleich as av, ablauf_vergleich_bericht as avb, kampagnen

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


def test_checkpointschluessel_enthaelt_das_verfahren():
    a = dict(gemeinsam=KLEIN)
    prof = regeln.profil('ENTW-2026-10').mit_reduktion(**KLEIN['profil_reduktion'])
    j1 = av._job('x', 'N01-A4', 'k_konsistent', [0])
    j2 = dict(j1, variante='wiederholungen')
    k1, k2 = av.schluessel(a, j1, prof, None), av.schluessel(a, j2, prof, None)
    assert k1['verfahren'] == vf.STATISCH.kennung() and k2['verfahren'] == vf.ZUSTAND.kennung() and k1 != k2


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
