"""Kalibrierbeispiel (Auftrag vom 20.10.2026, Abschnitt 9): Der Trockenlauf startet keine Kampagne; die große Rechnung
verlangt den ausdrücklichen Bestätigungsparameter; die Demonstration ist klein und gekennzeichnet; Checkpoints und
Ausgabeverzeichnisse werden nicht vermischt oder überschrieben. Gerechnet wird hier nichts Großes (Attrappen)."""
import json
import os

import pytest

from pcmms_auswertung import cli
from pcmms_auswertung.harness import kalibrierbeispiel as kb, kalibrierung, kampagnen as kpn

WURZEL = os.path.join(os.path.dirname(__file__), '..', 'rechnungen', 'kalibrierbeispiel')
GROSS = os.path.join(WURZEL, 'konfig_gross_N01-A4.json')
DEMO = os.path.join(WURZEL, 'konfig_demo.json')


@pytest.fixture
def kein_rechnen(monkeypatch):
    def verboten(*a, **k):
        raise AssertionError('Kampagne gestartet')
    monkeypatch.setattr(kpn, 'ausfuehren', verboten)
    monkeypatch.setattr(kalibrierung, 'kalibrieren', verboten)


def test_trockenlauf_startet_nichts_und_nennt_kosten(kein_rechnen, capsys):
    k = kb.lies(GROSS)
    t = kb.trockenlauf(k)
    assert t['gerechnet'] is False and t['betriebsart'] == 'trockenlauf'
    assert t['profil']['id'] == 'ENTW-2026-11' and t['plan']['p0_anordnung'] == 'p07'
    assert t['kosten']['kampagnen_min'] == 2000 and t['kosten']['kernstunden_min'] > 4
    assert [r['rolle'] for r in t['auftragsliste']][:2] == ['kalibrierung_c', 'pruefung_c']
    assert t['auftragsliste'][0]['versuchslimit'] == 1500 and len(t['auftragsliste'][0]['erste_seeds']) == 5
    assert '--bestaetigung' in t['ausfuehrung']
    assert cli.main(['harness', 'kalibrierbeispiel', '--konfig', GROSS]) == 0
    assert json.loads(capsys.readouterr().out)['gerechnet'] is False


def test_grosse_rechnung_nur_mit_bestaetigung(kein_rechnen, tmp_path):
    k = kb.lies(GROSS)
    for b in (None, 'ja', 'grosse kalibrierung starten'):
        with pytest.raises(kb.BeispielFehler, match='nichts gerechnet'):
            kb.ausfuehren(k, str(tmp_path / 'aus'), b)
    assert not (tmp_path / 'aus').exists()


def test_konfiguration_wird_streng_geprueft():
    with open(DEMO, encoding='utf-8') as f:
        demo = json.load(f)
    with open(GROSS, encoding='utf-8') as f:
        gross = json.load(f)
    kb.pruefen(demo)
    for aenderung, muster in ((dict(soll_A=50), 'Demonstration zu groß'), (dict(profil='ENTW-2026-10'), 'historisch'),
                              (dict(prozesse=5), 'Prozesse'), (dict(modus='mittel'), 'modus'),
                              (dict(szenario='X99'), 'Katalog')):
        with pytest.raises(kb.BeispielFehler, match=muster):
            kb.pruefen(dict(demo, **aenderung))
    with pytest.raises(kb.BeispielFehler, match='soll_A = 1000'):
        kb.pruefen(dict(gross, soll_A=500))
    with pytest.raises(kb.BeispielFehler, match='keine normative'):
        kb.pruefen(dict(gross, reduktion=dict(bootstrap_B=200)))


def _attrappe(aufrufe):
    def ausfuehren(sid, stufe, profil, n, seed_basis, rolle='pruefung', plan=None, n_min=None, werkzeug8=None,
                   rausch=None, start=0, **kw):
        aufrufe.append((rolle, start, n))
        seeds = [kpn.kampagnen_seed(seed_basis, rolle, sid, stufe, i) for i in range(start, start + n)]
        return dict(meta=dict(n=n, seeds=seeds, laufzeit_s=0.0), befunde=[dict(seed=s) for s in seeds],
                    wahrheit=dict())
    return ausfuehren


def test_checkpoints_je_partie_fortsetzbar_und_nicht_vermischt(monkeypatch, tmp_path):
    aufrufe = []
    monkeypatch.setattr(kpn, 'ausfuehren', _attrappe(aufrufe))
    k = kb.lies(DEMO)
    cp = kb.Checkpoints(k, str(tmp_path))
    a = cp('N01-A4', 'L1', k['_profil'], 5, k['seed_basis'], 'kalibrierung_c', k['_plan'], 2, None, None)
    assert [x[1:] for x in aufrufe] == [(0, 2), (2, 2), (4, 1)] and cp.gerechnet == 3
    b = kb.Checkpoints(k, str(tmp_path))('N01-A4', 'L1', k['_profil'], 5, k['seed_basis'], 'kalibrierung_c',
                                         k['_plan'], 2, None, None)
    assert len(aufrufe) == 3 and b['befunde'] == a['befunde'] and b['meta']['seeds'] == a['meta']['seeds']
    k2 = kb.pruefen(dict({x: v for x, v in k.items() if not x.startswith('_')}, seed_basis=1))
    with pytest.raises(kb.BeispielFehler, match='inkompatibler Checkpoint'):
        kb.Checkpoints(k2, str(tmp_path))('N01-A4', 'L1', k2['_profil'], 2, 1, 'kalibrierung_c', k2['_plan'], 2,
                                          None, None)


def test_fremdes_ausgabeverzeichnis_wird_nicht_ueberschrieben(kein_rechnen, tmp_path):
    with open(tmp_path / 'konfiguration.json', 'w', encoding='utf-8') as f:
        json.dump(dict(konfiguration_sha256='andere'), f)
    with pytest.raises(kb.BeispielFehler, match='anderen Konfiguration'):
        kb.ausfuehren(kb.lies(DEMO), str(tmp_path))
