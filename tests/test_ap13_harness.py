"""AP-13 Werkzeug 8 (Etappe 5): Raten mit MC-Fehler, Kampagnen mit festen Seeds, Kalibrier- und Prüfsimulation von c
mit Pool-Regel, H2-Überdeckung und Rückfallkette, gemeinsame Bestätigungswahrscheinlichkeit, Planungshaken,
Wahrheitstrennung (Negativtest), Reproduzierbarkeit, Ebenen Z/H, S₃, Software-Prüfsatz, Kriterienmatrix und
Kommandozeile aus einer frischen Ausgabestruktur.

Kampagnenzahlen sind hier klein (Softwareprüfung); jedes Ergebnis trägt die Kennzeichnung „reduziert“."""
import copy
import json
import os

import numpy as np
import pytest

from pcmms_auswertung import auswertung, cli, formate, pilot, regeln
from pcmms_auswertung.generator import kampagne
from pcmms_auswertung.harness import (dateien, ebenen, kalibrierung, kampagnen, kette, kriterien, metriken, planung,
                                      pruefsatz, s3)

PROFIL = regeln.profil('ENTW-2026-10').mit_reduktion(bootstrap_B=200, eps_ctrl_datensaetze=300, h3_mc=1000)
PLAN = kampagne.Plan(n0=20, n_pilot=20, n_bloecke=24)
FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')


def _ohne_zeit(b):
    return formate.sha256_json({k: v for k, v in b.items() if k != 'laufzeit_s'})


# ── Raten ────────────────────────────────────────────────────────────────────────────────────────────
def test_rate_mit_zaehler_nenner_und_mc_fehler():
    r = metriken.rate(3, 60, 'P(x)', szenario='N01-A4', stufe='L1', profil='P')
    assert r['rate'] == pytest.approx(0.05) and r['mc_se'] == pytest.approx(np.sqrt(0.05 * 0.95 / 60))
    assert r['reduziert'] and 'Entwicklungsdiagnostik' in r['lesart'] and r['szenario'] == 'N01-A4'
    assert not metriken.rate(50, 1000, 'P')['reduziert']
    assert metriken.rate(0, 0, 'P')['rate'] is None
    q = metriken.quantil(np.arange(1000.0), 0.95, B=200)
    assert q['wert'] == pytest.approx(np.quantile(np.arange(1000.0), 0.95)) and q['se'] > 0


# ── Kampagnen: Seeds, Prozesse ───────────────────────────────────────────────────────────────────────
def test_kampagnen_unabhaengig_von_der_prozesszahl():
    a = kampagnen.ausfuehren('A04-R4', 'L1', PROFIL, 3, 11, 'test', PLAN, 18, prozesse=1)
    b = kampagnen.ausfuehren('A04-R4', 'L1', PROFIL, 3, 11, 'test', PLAN, 18, prozesse=2)
    c = kampagnen.ausfuehren('A04-R4', 'L1', PROFIL, 3, 12, 'test', PLAN, 18, prozesse=1)
    assert [_ohne_zeit(x) for x in a['befunde']] == [_ohne_zeit(x) for x in b['befunde']]
    assert not {_ohne_zeit(x) for x in a['befunde']} & {_ohne_zeit(x) for x in c['befunde']}
    assert a['meta']['seeds'] == b['meta']['seeds'] and a['meta']['reduziert']
    r = kampagnen.raten(a)
    assert r['wahrheit']['klasse'] == 'R4'
    x = r['raten']['H1: falsifiziert']
    assert x['nenner'] == 3 and x['zaehler'] == 3 and x['mc_se'] == 0.0 and x['reduziert']
    # Regression (Prüfstand A07): Kontrollen ohne Bewertung zählen unter ihrem Status, nicht als „None“
    d = copy.deepcopy(a)
    d['befunde'][0]['E3'] = dict(bewertung=None, status='nicht auswertbar: T(kω) singulär')
    d['befunde'][1]['zuordnung'] = dict(ergebnis=None, klasse=None, status='nur numerisch: Regel offen')
    rd = kampagnen.raten(d)['raten']
    assert rd['E3: nicht auswertbar']['zaehler'] == 1 and rd['E3: nicht auswertbar']['nenner'] == 3
    assert rd['Zuordnung: nur numerisch']['zaehler'] == 1
    assert not [k for k in rd if 'None' in k]


# ── Kalibrier- und Prüfsimulation ────────────────────────────────────────────────────────────────────
@pytest.fixture(scope='module')
def kal():
    return kalibrierung.kalibrieren('N01-A4', 'L1', PROFIL, 6, 6, 101, PLAN, 18, prozesse=2)


def test_c_aus_kalibrierung_mit_biaskorrektur_und_pool_regel(kal):
    z = kal['zmax']
    c = kal['c_H1']
    roh = z['kalibrierung'][z['kalibrierung_vollstaendig']]
    pr = kal['pruefung']
    assert pr['nenner'] == int(z['pruefung_vollstaendig'].sum())
    assert pr['zaehler'] == int((z['pruefung'][z['pruefung_vollstaendig']] > kal['werkzeug8']['c_H1']).sum()) or \
        kal['gepoolt']
    if pr['rate'] > kal['pruefschwelle']:
        pool = np.r_[roh, z['pruefung'][z['pruefung_vollstaendig']]]
        assert kal['gepoolt'] and c['wert'] == pytest.approx(np.quantile(pool, 0.95))
        assert 'gepooltes Quantil' in kal['werkzeug8']['c_H1_herkunft']
    else:
        assert not kal['gepoolt'] and c['wert'] == pytest.approx(np.quantile(roh, 0.95))
    assert kal['werkzeug8']['c_H1'] == pytest.approx(c['wert'])
    assert 'reduziert' in kal['werkzeug8']['c_H1_herkunft'] and kal['meta']['reduziert']
    # Rauschbias: Mittel der Rohresiduen, u aus dem MC-Fehler; dieselbe Korrektur im c
    assert np.asarray(kal['rauschbias']['b0']).shape == (21,) and np.all(np.asarray(kal['rauschbias']['u_b0']) > 0)
    w8 = kal['werkzeug8']
    assert np.allclose(w8['bias0'], kal['rauschbias']['b0']) and np.asarray(w8['bias0_zellen']).shape == (21, 3)
    assert set(kal['restbias']) == {'yhat0', 'yhat1'}


def test_ueberdeckung_und_gemeinsame_bestaetigung_getrennt(kal):
    h2 = kal['h2']
    assert h2['typ'] in ('perzentil', 'bca', 'keiner') and h2['schwelle'] == 0.936
    for typ, u in h2['ueberdeckung'].items():
        assert u['yhat0']['nenner'] == 6 and u['yhat0']['groesse'].startswith('Überdeckung')
    g = kal['gemeinsame_bestaetigung']
    assert g['groesse'] == 'P(H1 und H2 bestätigt)' and g['nenner'] == 6
    assert kal['werkzeug8']['h2_intervall']['typ'] == h2['typ']


def test_rueckfallkette_der_intervalle(monkeypatch):
    """Wahl des Intervalltyps nach §8.6: Perzentil, sonst BCa, sonst Perzentil 0,96 … 0,99, sonst keiner."""
    monkeypatch.setattr(kalibrierung, 'h2_bezug', lambda wahr, W, profil: (0.0, 0.0))

    def lauf(abdeckung):
        bf = []
        for i in range(100):
            iv = {typ: ((-1.0, 1.0), (-1.0, 1.0)) if i < 100 * p else ((0.5, 1.0), (0.5, 1.0))
                  for typ, p in abdeckung.items()}
            bf.append(dict(H2=dict(W_ids=['S118', 'S120'], intervalle=iv)))
        return dict(meta=dict(szenario='T', stufe='L1', profil='P'), befunde=bf, wahrheit={})
    alle = ['perzentil_0.95', 'bca_0.95', 'perzentil_0.96', 'perzentil_0.97', 'perzentil_0.98', 'perzentil_0.99']
    f = lambda d: kalibrierung.h2_ueberdeckung(lauf({t: d.get(t, 0.9) for t in alle}), PROFIL)['schluessel']  # noqa
    assert f({'perzentil_0.95': 0.94}) == 'perzentil_0.95'
    assert f({'bca_0.95': 0.95}) == 'bca_0.95'
    assert f({'perzentil_0.97': 0.94, 'perzentil_0.98': 0.99}) == 'perzentil_0.97'
    r = kalibrierung.h2_ueberdeckung(lauf({t: 0.9 for t in alle}), PROFIL)
    assert r['typ'] == 'keiner' and r['schluessel'] is None
    # offene Regel (Profil AF): kein Typ, Grund benannt
    af = regeln.profil('AF-2026-10')
    assert kalibrierung.h2_ueberdeckung(lauf({}), af)['typ'] is None


def test_planungshaken_im_pilotskript():
    """Haken der AP-13-Planung (§5.4, A9.2): Pilotgrößen → Kalibrier-/Prüfsimulation je Kandidat → n_min, n₀;
    die Pilotausgabe enthält keine Residuen- oder Entscheidungsfelder."""
    m, laeufe, tab = kette.kampagne_erzeugen('N01-A4', 'L1', PLAN, 5)
    _, _, kal_ = kette.kalibrierung_erzeugen(kette.szenarien.KATALOG['N01-A4'], m, 5)
    prot = []
    hk = planung.haken('N01-A4', 'L1', PROFIL, 3, 3, 77, n_kandidaten=(18,), n0_kandidaten=(20,), plan_basis=PLAN,
                       prozesse=2, protokoll=prot, max_aufrufe=1)
    zeit = dict(T_park=2.0, T_ramp=2.0, T_ab=1.0, T_eP=4.0, T_aP=10.0, T_verfuegbar=4 * 86400.0, d=2, N_K=21, N_I=0)
    out = pilot.pilot_auswerten(tab.auswahl(tab.spalte('phase', int) == 0), kal_, PROFIL, m.system.f, zeit=zeit,
                                seed=5, planung=hk)
    pilot.pruefe_ausgabe(out)
    assert prot and prot[0]['kandidaten'][0]['nenner'] == 3 and prot[0]['reduziert']
    assert 'Entwicklungsdiagnostik' in prot[0]['quelle'] and prot[0]['kappa'] > 1
    assert all('Entwicklungsgrenze' in x['grund'] for x in prot[1:])
    s = out['suche']
    assert s['ergebnis'] in ('festgelegt', 'kein zulässiger Arbeitspunkt unter diesen Annahmen')
    if s['ergebnis'] == 'festgelegt':
        assert s['n_min'] == 18 and s['n0'] == 20 and 'Entwicklungsdiagnostik' in s['planung_quelle']
    ps = prot[0]['kandidaten'][0]['plan_simuliert']
    assert ps['n_zyklen'] == prot[0]['N_z'] and ps['tage'] == zeit['d']


def test_planungshaken_simuliert_gewaehlte_fensterlaenge(monkeypatch, tmp_path):
    """Korrektur A: N_z des Kandidaten, T_a = N_z/f, T_Lauf und d kommen im Plan der Kampagnensimulation an (nicht
    nur im Seed). Instrumentierter Aufruf je Fensterlänge, dann echte Läufe mit genau diesem Plan: Ebene H (Köpfe,
    Laufdauer, Messtage, Zeitbudget) und ein Rohlauf auf Ebene Z durch Stufe 1 (gezählte Zyklen, Fensterdauer)."""
    from pcmms_auswertung import stufe1, zufall
    from pcmms_auswertung.generator import ebene_z, kampagne as kp
    sid, f = 'N01-A4', 10.0
    gesehen = []

    def kal_attrappe(sid_, stufe_, profil_, n_kal, n_pruef, seed, plan=None, n_min=None, **kw):
        gesehen.append(plan)
        return dict(gemeinsame_bestaetigung=dict(rate=1.0, mc_se=0.0, zaehler=1, nenner=1), c_H1=dict(wert=3.7),
                    h2=dict(schluessel='perzentil_0.95'), pruefung=None)

    monkeypatch.setattr(planung.kalibrierung, 'kalibrieren', kal_attrappe)
    zeit = dict(T_park=2.0, T_ramp=2.0, T_ab=1.0, T_eP=4.0, T_aP=10.0, T_verfuegbar=4 * 86400.0, d=2, N_K=21, N_I=0)
    T_e = 3.0
    hk = planung.haken(sid, 'L1', PROFIL, 1, 1, 77, n_kandidaten=(18,), plan_basis=PLAN)
    kal = dict(zellen=[dict(zelle=c + 1, nullpunkt_adc=0.0, umrechnung='linear', empfindlichkeit_N_je_adc=1e-6)
                       for c in range(3)])
    for Nz in (20, 80):
        T_a = Nz / f
        T_lauf = zeit['T_park'] + zeit['T_ramp'] + T_e + T_a + zeit['T_ab']
        n_max = pilot.n_max(T_lauf, 0.0, zeit)
        out = hk(dict(k=9, N_z=Nz, T_a=T_a, T_e=T_e, T_lauf=T_lauf, zeit=zeit, s_q=dict(nu_p=57), p_hat=0.0,
                      n_max=n_max, f=f))
        plan_ = gesehen[-1]
        assert plan_.n_zyklen == Nz and plan_.T_lauf == pytest.approx(T_lauf) and plan_.tage == zeit['d']
        ps = out['kandidaten'][0]['plan_simuliert']
        assert ps['n_zyklen'] == Nz and ps['T_a_s'] == pytest.approx(T_a) and ps['T_lauf_s'] == pytest.approx(T_lauf)
        assert out['fenster'] == dict(N_z=Nz, T_a_s=pytest.approx(T_a), T_e_s=T_e, T_lauf_s=pytest.approx(T_lauf),
                                      f_hz=f)
        # Ebene H mit diesem Plan: Fensterlänge, Laufdauer, Messtage und Zeitbudget wie in der Kandidatenrechnung
        m, laeufe, tab = kette.kampagne_erzeugen(sid, 'L1', plan_, 5)
        assert {k['n_zyklen'] for k in tab.koepfe} == {Nz}
        assert np.allclose([k['t_ende'] - k['t_start'] for k in tab.koepfe], T_lauf, rtol=0, atol=1e-9)
        assert {k['messtag'] for k in tab.koepfe if k['phase'] == 1} == {1, 2}
        n1 = sum(v for (ph, _, _), v in kp.zaehlung(laeufe).items() if ph == 1)
        assert plan_.n_bloecke <= n_max
        assert n1 <= (zeit['N_K'] + zeit['N_I'] + 8) * plan_.n_bloecke + 18 * zeit['d']   # Budget von n_max (§5.3 c)
        # Ebene Z: ein Kombinationslauf der Phase 1 mit diesem Plan durch Stufe 1
        pos = next(l['position'] for l in laeufe if l['phase'] == 1 and l['laufart'] == 'K')
        ziel = str(tmp_path / f'z{Nz}')
        os.makedirs(ziel, exist_ok=True)
        zeilen, _ = ebene_z.erzeuge(m, laeufe, zufall.strom(5, 'z'), ziel, formate.synth_kennung('PLAN', sid),
                                    dict(nullpunkt_adc=[0.0] * 3, empfindlichkeit_N_je_adc=[1e-6] * 3), nur=[pos])
        lz = stufe1.laufzusammenfassung(os.path.join(ziel, zeilen[0]['lauf_id']), kal, k_voll=tab.k_voll)
        assert lz.kopf['n_zyklen'] == Nz
        assert lz.kopf['n_zyklen'] / lz.kopf['f_mittel'] == pytest.approx(T_a, abs=2e-6)   # 1-µs-Zeitstempel
    assert [p.n_zyklen for p in gesehen] == [20, 80]


# ── Wahrheitstrennung, Reproduzierbarkeit, Durchgängigkeit ───────────────────────────────────────────
def test_wahrheit_aendern_oder_entfernen_aendert_ap12_nicht(tmp_path):
    r = dateien.kette_dateien(str(tmp_path / 'a'), 'A04-R4', 'L1', PROFIL, plan=PLAN, seed=7, ebene='H', n_min=18)
    p = r['pfade']
    h0 = dateien.ergebnis_hash(r['ergebnis'])
    dateien.wahrheit_verfaelschen(str(tmp_path / 'a'), 'aendern')
    assert dateien.bewerten(p['ergebnis'], p['wahrheit'])['klasse'] == 'R4'           # Harness sieht die Änderung
    e1 = dateien.ap12_auswerten(p['zusammenfassungen'], p['kalibrierung'], p['teil_b'], PROFIL, p['ergebnis'] + '1')
    dateien.wahrheit_verfaelschen(str(tmp_path / 'a'), 'entfernen')
    e2 = dateien.ap12_auswerten(p['zusammenfassungen'], p['kalibrierung'], p['teil_b'], PROFIL, p['ergebnis'] + '2')
    assert dateien.ergebnis_hash(e1) == h0 == dateien.ergebnis_hash(e2)
    # AP-12 weist eine Wahrheitsdatei als Eingang zurück
    r2 = dateien.kette_dateien(str(tmp_path / 'b'), 'N01-A4', 'L1', PROFIL, plan=PLAN, seed=7, ebene='H', n_min=18)
    with pytest.raises(formate.FormatFehler):
        auswertung.auswerten(r2['pfade']['zusammenfassungen'], r2['pfade']['kalibrierung'], r2['pfade']['wahrheit'],
                             PROFIL)


def test_dateikette_reproduzierbar_und_gleich_speicherkette(tmp_path):
    a = dateien.kette_dateien(str(tmp_path / 'a'), 'N03-ungleich', 'L1', PROFIL, plan=PLAN, seed=9, ebene='H',
                              n_min=18)
    b = dateien.kette_dateien(str(tmp_path / 'b'), 'N03-ungleich', 'L1', PROFIL, plan=PLAN, seed=9, ebene='H',
                              n_min=18)
    assert dateien.ergebnis_hash(a['ergebnis']) == dateien.ergebnis_hash(b['ergebnis'])
    k = kette.kette('N03-ungleich', 'L1', PROFIL, plan=PLAN, seed=9, n_min=18)
    teile = ('H1', 'H1Z', 'H2', 'H3', 'H4', 'H0', 'E3')
    assert formate.sha256_json({h: a['ergebnis'][h] for h in teile}) == \
        formate.sha256_json({h: k['ergebnis'][h] for h in teile})
    # AP-11-Kalibrierung und Teil B aus den Dateien werden tatsächlich verwendet
    _, kal = dateien.anpassung.lies_kalibrierung(a['pfade']['kalibrierung'])
    assert a['ergebnis']['herkunft']['kalibrierung_sha256'] == formate.sha256_json(kal)
    # Rundreise der neuen Metadaten (Korrekturen B und E): Kettenrichtungen in P0.4, T-Unsicherheit in Teil B
    from pcmms_auswertung import teil_b
    _, tb = teil_b.lesen(a['pfade']['teil_b'])
    u = tb['nr5']['unsicherheit']
    assert u['format'] == 'e3_T_unsicherheit-0.1' and u['herkunft']['kalibrierung_sha256'] == formate.sha256_json(kal)
    assert u['fn_zeta']['kette_richtungen'] == kal['p0_4']['einfreiheitsgrad']['kette_richtungen']
    assert np.allclose(u['gxy']['kovarianz'], kal['p0_1']['laststellen']['kovarianz_g_x_y'])
    assert tb['nr1']['phase0_verarbeitung']['alte_bedeutung'] == []
    assert a['ergebnis']['E3']['t_unsicherheit']['gezogen'] is True
    with pytest.raises(FileExistsError):
        dateien.generator_schreiben(str(tmp_path / 'a'), 'N01-A4', 'L1', PLAN, 1, 'H')


def test_ebenen_rauschfrei_gleich(tmp_path):
    r = ebenen.vergleich_rauschfrei('N01-A4', 'L1', str(tmp_path))
    assert r['gleich'] and set(r['laufarten']) == {'R', 'L', 'K'}, r['abweichung']


def test_s3_bilder_und_vorhersage():
    f1, f3 = s3.pruefen('F01-S3'), s3.pruefen('F03-S3ungleich')
    assert f1['bilder_gleich'] and f1['vorhersage_exakt'] and f1['maximum']['phase_grad'] < 1e-6
    assert f1['maximum']['betrag_N'] < 1e-9 and f1['F_min_in_rasterschranke']
    assert not f3['bilder_gleich'] and f3['vorhersage_exakt'] and f3['maximum']['betrag_N'] > 1e-3


def test_pruefsatz_unveraendert():
    r = pruefsatz.pruefen(os.path.join(FIXTURES, 'ap13_pruefsatz'))
    assert r['gleich'], r['abweichungen']


# ── Kriterienmatrix ──────────────────────────────────────────────────────────────────────────────────
def test_kriterienmatrix_ohne_gesamtampel():
    rt = dict(raten={'H1: falsifiziert': metriken.rate(0, 20, 'x'), 'H1: bestätigt': metriken.rate(1, 20, 'x')},
              wahrheit=dict(klasse='R3', r_max_rel=1.4))
    ps = dict(profil=PROFIL.id, code_version={}, konfiguration=dict(stufe='L1', plan=dict(n_bloecke=24), n_min=18,
                                                                    planung_kandidaten=[18], profil_reduktion={}),
              schritte=dict(szenarien_a4={'A04-R4/L1': rt, 'N05-F/L1': rt}, eigene={'A07-hertz50/L1': rt}))
    z = kriterien.bewerten(ps)
    ids = [x['id'] for x in z]
    assert {f'K{i:02d}' for i in range(1, 22)} <= set(ids) and {'H1Z', 'E3', 'Zuordnung'} <= set(ids)
    assert all(x['status'] in kriterien.STATUS for x in z)
    assert 'geprüft' not in {x['status'] for x in z if x['id'] in ('K04', 'K07')}           # reduziert
    assert next(x for x in z if x['id'] == 'K21')['status'] == 'in diesem Modell nicht prüfbar'
    md = kriterien.markdown(z)
    assert 'Keine Gesamtampel' in md and 'Zählung der Status' in md


# ── Kommandozeile ────────────────────────────────────────────────────────────────────────────────────
def test_cli_kette_aus_frischer_struktur(tmp_path, capsys):
    ziel = str(tmp_path / 'k')
    rc = cli.main(['kette', '--szenario', 'A04-R1', '--stufe', 'L1', '--seed', '3', '--ebene', 'H', '--ausgabe', ziel,
                   '--band', '20', '600', '--profil', 'ENTW-2026-10', '--red',
                   'bootstrap_B=200,h3_mc=1000,eps_ctrl_datensaetze=300', '--n-min', '18'])
    out = capsys.readouterr().out
    assert rc == 0 and 'Wahrheit: Klasse R1' in out and 'REDUZIERT' in out
    for teil in ('eingang/kalibrierung.json', 'eingang/teil_b.json', 'eingang/pilot.json', 'ergebnis/ergebnis.json',
                 'ergebnis/bewertung.json', 'wahrheit/wahrheit.json'):
        assert os.path.exists(os.path.join(ziel, teil)), teil
    assert not any('wahrheit' in f for f in os.listdir(os.path.join(ziel, 'eingang')))
    _, erg = auswertung.lies_ergebnis(os.path.join(ziel, 'ergebnis', 'ergebnis'))
    assert erg['herkunft']['kennung'].startswith('SYNTH-')
    with pytest.raises(SystemExit):                                       # kein stiller Profil-Vorgabewert
        cli.main(['ap12', 'auswerten', '--zusammenfassungen', 'x', '--kalibrierung', 'x', '--teil-b', 'x',
                  '--ausgabe', 'x'])


def test_cli_matrix_wird_nicht_gestartet(tmp_path, capsys):
    p = str(tmp_path / 'matrix')
    assert cli.main(['harness', 'matrix', '--ausgabe', p, '--kampagnen', '1000', '--seed', '1']) == 0
    _, m = formate.lies_objekt(p, 'bewertung')
    assert m['gestartet'] is False and all(a['kampagnen'] == 1000 for a in m['auftraege'])
    assert 'nicht gestartet' in capsys.readouterr().out


def test_werkzeug8_datei_rundreise(tmp_path, kal):
    p = str(tmp_path / 'w8')
    formate.schreibe_objekt(p, formate.kopf('werkzeug8', formate.synth_kennung('W8')), kal['werkzeug8'])
    w = dateien.lies_werkzeug8(p)
    assert w['c_H1'] == pytest.approx(kal['werkzeug8']['c_H1']) and np.allclose(w['bias0'], kal['werkzeug8']['bias0'])
    assert json.loads(open(p + '.json', encoding='utf-8').read())['kopf']['schema'] == 'pcmms.werkzeug8'
