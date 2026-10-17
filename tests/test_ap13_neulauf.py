"""AP-13-Neuläufe (harness.neulauf, neulauf_vergleich): Risiken des Treibers – falsche Rolle oder Seeds, unbemerkte
Testvorgabe für Werkzeug 8, Wiederaufnahme nur bei passender Herkunft, E3-Nenner und Gründe ohne Umetikettierung."""
import copy
import json
import os

import numpy as np
import pytest

from pcmms_auswertung import formate, regeln
from pcmms_auswertung.harness import kampagnen, kette, neulauf, neulauf_vergleich, pruefstand

DOKU = os.path.join(neulauf.WURZEL, neulauf.DOKU_REL)
AUSWAHL = {('N01-A4', 'L1'): (200, 'pruefung_c', 'A4'), ('A06-phase', 'L1'): (30, 'pruefung', 'V1-G0'),
           ('H03-phase', 'L1'): (30, 'pruefung', 'V1-G0'), ('E04-kette', 'L1'): (30, 'pruefung', 'testvorgabe'),
           ('E07-verstaerkung', 'L1'): (40, 'pruefung', 'A4'), ('E07-basisdrift', 'L1'): (40, 'pruefung', 'A4'),
           ('N03-ungleich', 'L1'): (40, 'pruefung', 'A4'), ('N03-N3bindet', 'L1'): (40, 'pruefung', 'A4'),
           ('N01-A4', 'L0'): (40, 'pruefung', 'testvorgabe'), ('N01-A4', 'L2'): (40, 'pruefung', 'testvorgabe'),
           ('N01-A4', 'L4'): (40, 'pruefung', 'testvorgabe')}


def _auftrag():
    return neulauf.lies_auftrag(neulauf.AUFTRAG)


def test_auftragsliste_rollen_seeds_und_werkzeug8_wie_auftrag_und_altlauf():
    """Die versionierte Auftragsliste: die 570 E3-Kampagnen der Auswahl, N01-A4/L1 in der Prüfkohorte der
    Kalibrierung (Rolle pruefung_c), die übrigen Punkte mit den Seeds des Altlaufs, Testvorgabe genau dort, wo der
    Altlauf sie verwendete, und vollständige, unveränderte Werkzeug-8-Werte A4 und V1-G0."""
    a = _auftrag()
    with open(os.path.join(DOKU, 'altstand_auszug.json'), encoding='utf-8') as f:
        alt = json.load(f)
    e3 = [j for j in a['auftraege'] if j['art'] == 'kampagnen']
    assert {(j['szenario'], j['stufe']): (j['n'], j['rolle'], j['werkzeug8']) for j in e3} == AUSWAHL
    assert sum(j['n'] for j in e3) == 570 and len(e3) == 11
    basis = a['gemeinsam']['seed_basis']
    assert basis == 20261016 == pruefstand.STANDARD['seed']
    for j in e3:
        assert j['seeds'] == [kampagnen.kampagnen_seed(basis, j['rolle'], j['szenario'], j['stufe'], i)
                              for i in range(j['n'])]
        meta = alt['e3'][f'{j["szenario"]}/{j["stufe"]}']['meta']
        if j['rolle'] == 'pruefung_c':
            andere = {kampagnen.kampagnen_seed(basis, 'pruefung', 'N01-A4', 'L1', i) for i in range(200)}
            assert not andere & set(j['seeds'])                        # „pruefung“ wäre eine andere Kohorte
        else:
            assert j['seeds'] == meta['seeds']
        assert (j['werkzeug8'] == 'testvorgabe') == (j['alt']['werkzeug8'] == 'TESTVORGABE')
        neulauf.pruefe_werkzeug8_wahl(j)
    with open(os.path.join(neulauf.WURZEL, neulauf.HISTORISCH_REL), encoding='utf-8') as f:
        hist = json.load(f)['inhalt']['schritte']
    for name, c_alt in (('A4', hist['kalibrierung_a4']['c_H1']['wert']),
                        ('V1-G0', hist['kalibrierung_v1']['V1-G0']['c_H1']['wert'])):
        w8, h = neulauf.werkzeug8_laden(a, name)
        assert w8['c_H1'] == c_alt and h == a['werkzeug8'][name]['inhalt_sha256']
        assert all(w8[f] is not None for f in neulauf.W8_FELDER) and np.asarray(w8['bias0_zellen']).shape == (21, 3)
    assert neulauf.werkzeug8_laden(a, 'testvorgabe')[0] is None
    assert neulauf.git_blob(os.path.join(neulauf.WURZEL, neulauf.HISTORISCH_REL)) == neulauf.ALT_BLOB


def test_kein_stiller_rueckfall_auf_testvorgabe(tmp_path):
    a = _auftrag()
    j = next(x for x in a['auftraege'] if x['id'] == 'E3-E07-verstaerkung-L1')
    for aenderung in (dict(werkzeug8=None), dict(werkzeug8='testvorgabe')):
        with pytest.raises(neulauf.AuftragFehler):
            neulauf.pruefe_werkzeug8_wahl({**j, **aenderung})
    j0 = next(x for x in a['auftraege'] if x['id'] == 'E3-N01-A4-L0')
    with pytest.raises(neulauf.AuftragFehler):                         # Altlauf mit Testvorgabe, Auftrag mit A4
        neulauf.pruefe_werkzeug8_wahl({**j0, 'werkzeug8': 'A4'})
    k19 = next(x for x in a['auftraege'] if x['art'] == 'ebenen_verrauscht')
    with pytest.raises(neulauf.AuftragFehler):
        neulauf.pruefe_werkzeug8_wahl({**k19, 'werkzeug8': 'testvorgabe'})
    # unvollständige, als Testvorgabe gekennzeichnete oder veränderte Werkzeug-8-Datei
    _, w8 = formate.lies_objekt(os.path.join(neulauf.WURZEL, a['werkzeug8']['A4']['datei']), 'werkzeug8')
    for name, w in (('fehlt', {k: v for k, v in w8.items() if k != 'u_bias0_zellen'}),
                    ('tv', dict(w8, c_H1_herkunft=kette.testvorgabe_werkzeug8()['c_H1_herkunft'])),
                    ('anders', dict(w8, c_H1=w8['c_H1'] + 1e-9))):
        p = os.path.join(tmp_path, name)
        formate.schreibe_objekt(p, formate.kopf('werkzeug8', formate.synth_kennung('W8', name)), w)
        b = copy.deepcopy(a)
        b['werkzeug8']['A4']['datei'] = os.path.relpath(p, neulauf.WURZEL)
        with pytest.raises(neulauf.AuftragFehler):
            neulauf.werkzeug8_laden(b, 'A4')


@pytest.fixture
def klein(tmp_path, monkeypatch):
    """Kleine Auftragsliste (ein E3-Punkt mit 2 Kampagnen, reduzierte Replikate) unter einer gleich verkleinerten
    Standardkonfiguration."""
    red = dict(bootstrap_B=100, h3_mc=200, eps_ctrl_datensaetze=200)
    monkeypatch.setattr(pruefstand, 'STANDARD', dict(pruefstand.STANDARD, profil_reduktion=red))
    prof = regeln.profil('ENTW-2026-10').mit_reduktion(**red)
    tv = kette.testvorgabe_werkzeug8()
    j = dict(id='E3-N01-A4-L0', art='kampagnen', kriterium='E3', szenario='N01-A4', stufe='L0', n=2,
             rolle='pruefung', werkzeug8='testvorgabe', alt=dict(werkzeug8='TESTVORGABE'))
    j['seeds'] = neulauf.seeds(j, 20261016)
    a = dict(kennung='TEST', altlauf={}, gemeinsam=dict(
        profil='ENTW-2026-10', profil_reduktion=red, profil_sha256=prof.sha256(), plan=pruefstand.STANDARD['plan'],
        n_min=18, seed_basis=20261016, hauptstufe='L1', prozesse=1, ausgabe=str(tmp_path / 'aus')),
        werkzeug8=dict(testvorgabe=dict(inhalt_sha256=formate.sha256_json(tv))), auftraege=[j])
    pfad = tmp_path / 'auftrag.json'
    pfad.write_text(json.dumps(a, ensure_ascii=False), encoding='utf-8')
    return pfad, a, prof


def test_wiederaufnahme_nur_bei_passender_herkunft(klein):
    pfad, a, prof = klein
    lauf = dict(streng=False, protokoll=lambda *x: None)
    assert neulauf.ausfuehren(str(pfad), **lauf) == {'E3-N01-A4-L0': 'gerechnet'}
    ziel = neulauf.verzeichnis(a, a['auftraege'][0])
    s = neulauf.checkpoint(ziel)
    assert s and s['schluessel']['rechencode'] == neulauf.rechencode_sha256()
    _, l0 = formate.lies_objekt(os.path.join(ziel, 'kampagnen_N01-A4_L0_pruefung'), 'bewertung')
    assert l0['meta']['werkzeug8'] == 'TESTVORGABE' and l0['meta']['seeds'] == a['auftraege'][0]['seeds']
    assert neulauf.ausfuehren(str(pfad), **lauf) == {'E3-N01-A4-L0': 'übernommen'}
    # veränderte Ergebnisdatei: kein Übernehmen
    with open(os.path.join(ziel, 'kampagnen_N01-A4_L0_pruefung.csv'), 'a', encoding='utf-8') as f:
        f.write('x\n')
    assert neulauf.ausfuehren(str(pfad), **lauf) == {'E3-N01-A4-L0': 'gerechnet'}
    # anderer Auftrag (Rolle und damit Seeds): neu gerechnet, der alte Stand beiseitegelegt
    b = copy.deepcopy(a)
    b['auftraege'][0].update(rolle='pruefung_c')
    with pytest.raises(neulauf.AuftragFehler):                         # Seeds der Liste passen nicht zur Rolle
        pfad.write_text(json.dumps(b, ensure_ascii=False), encoding='utf-8')
        neulauf.ausfuehren(str(pfad), **lauf)
    b['auftraege'][0]['seeds'] = neulauf.seeds(b['auftraege'][0], 20261016)
    pfad.write_text(json.dumps(b, ensure_ascii=False), encoding='utf-8')
    assert neulauf.ausfuehren(str(pfad), **lauf) == {'E3-N01-A4-L0': 'gerechnet'}
    assert len([d for d in os.listdir(os.path.dirname(ziel)) if '.verworfen-' in d]) == 2
    # E3 über alle Kampagnen; die Regel der Gegenprobe gibt die gespeicherte Bewertung wieder
    _, l1 = formate.lies_objekt(os.path.join(ziel, 'kampagnen_N01-A4_L0_pruefung_c'), 'bewertung')
    p = neulauf_vergleich.e3_punkt(l1, prof.wert('e3.schwellen'))
    assert sum(r['zaehler'] for r in p['raten'].values()) == p['n'] == 2
    assert all(r['nenner'] == 2 for r in p['raten'].values())
    assert p['gegenprobe_regel']['gleich'] == p['gegenprobe_regel']['geprueft']
    assert p['t_ziehungen']['kampagnen_mit_ziehungen']['nenner'] == 2


def _befund(bewertung=None, status=None, e3=True, grund=None, ung=0.0, A=((1.0, 0.1, 0.05),), q=None):
    if not e3:
        return dict(E3=None, E3_grund=grund)
    t = dict(gezogen=True, B=1000, anteil_ungueltig=ung, gruende={'g_c ≤ 0': int(round(ung * 1000))} if ung else {},
             anteil_w_gespiegelt=0.0, unvollstaendig=[], nicht_gezogen=['Kippmoden'], naeherungen=[],
             modell='e3_T-0.2', format='e3_T_unsicherheit-0.1')
    return dict(E3=dict(bewertung=bewertung, status=status, e3a=np.array(A, float),
                        e3b=None if q is None else np.array(q, float), t=t), E3_grund=None)


def test_e3_nenner_und_gruende_ohne_umetikettierung():
    """Alle Kampagnen im Nenner; ohne dreiwertige Bewertung getrennt mit Grund, nicht als „unbestimmt“; Nullzähler
    erscheinen; unzulässige Ziehungen mit Zähler und Nenner."""
    sw = dict(phase_grad=0.5, q_tol=0.1)
    bf = [_befund('auffällig', 'Entwicklungsprofil', A=((1.0, 0.1, 0.05), (0.0, 0.1, 0.05))),
          _befund('unbestimmt', 'Entwicklungsprofil', A=((0.4, 0.1, 0.01), (0.0, 0.1, 0.01))),
          _befund(None, 'nur numerisch: 3 von 1000 T-Ziehungen unzulässig ({…}); u nur aus den zulässigen Ziehungen, '
                        'keine dreiwertige Aussage', ung=0.003),
          _befund(None, 'nur numerisch: Unsicherheitsbeschreibung von T unvollständig: P0.4 …'),
          _befund(e3=False, grund=kampagnen._e3_fehlt({'nr5': {'T': None}})),
          dict(E3=dict(bewertung=None, status='nicht auswertbar: T(kω) singulär …', e3a=np.zeros((0, 3)), e3b=None,
                       t=None), E3_grund=None)]
    p = neulauf_vergleich.e3_punkt(dict(befunde=bf), sw)
    assert p['n'] == 6 and all(r['nenner'] == 6 for r in p['raten'].values())
    assert [p['raten'][k]['zaehler'] for k in ('auffällig', 'unauffällig', 'unbestimmt')] == [1, 0, 1]
    assert p['raten'][neulauf_vergleich.OHNE]['zaehler'] == 4
    g = p['ohne_dreiwertige_bewertung']
    assert {k: v['zaehler'] for k, v in g.items()} == {
        'unzulässige T-Ziehungen': 1, 'T-Beschreibung unvollständig': 1, 'keine E3-Auswertung': 1,
        'nicht auswertbar (T singulär oder schlecht konditioniert)': 1}
    assert 'T(kω) fehlt' in next(iter(g['keine E3-Auswertung']['wortlaute']))
    assert p['t_ziehungen']['unzulaessige_ziehungen'] == dict(zaehler=3, nenner=4000, rate=3 / 4000,
                                                              mc_se=pytest.approx(np.sqrt(3 / 4000 * (1 - 3 / 4000)
                                                                                          / 4000)))
    assert p['t_ziehungen']['kampagnen_mit_unzulaessigen']['zaehler'] == 1
    assert p['gegenprobe_regel'] == dict(geprueft=2, gleich=2)
    # alte Lesart (u ohne T-Anteil): die zweite Kampagne wird mit kleinerem u unauffällig
    assert p['alte_lesart_je_kampagne'][:2] == ['auffällig', 'unauffällig']
