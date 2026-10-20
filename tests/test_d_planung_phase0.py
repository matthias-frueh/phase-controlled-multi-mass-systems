"""Teil d2: Planungshaken mit dem Phase-0-Modell ohne Szenario-ID und ohne Szenario-Wahrheit, obere 80-%-Grenzen je
Komponente mit gemeinsamem Bodenfaktor, c_B in der Planung, Teil-B-Werte aus Punktschätzern mit Modellliste und
Sensitivitäten, c nach h1.c_rauschmodelle, Kampagnen aus einer Modellquelle, Rechnungen R1-d bis R3-d (Auftragslisten,
Kleinstlauf). Kampagnenzahlen sind Softwareprüfungen (1–2 Kampagnen), keine Kalibrierung."""
import numpy as np
import pytest
from scipy import stats

from pcmms_auswertung import formate, laufgroessen as lgm, pilot, regeln, zufall
from pcmms_auswertung.generator import kampagne as kp, phase0_modell as p0m, szenarien
from pcmms_auswertung.harness import kalibrierung, kampagnen, kette, phase0_rechnungen as p0r, planung

PLAN = kp.Plan(n0=20, n_pilot=20, n_bloecke=24)
AKTUELL = regeln.profil('ENTW-2026-11').mit_reduktion(bootstrap_B=200, eps_ctrl_datensaetze=300, h3_mc=200)
HIST = regeln.profil('ENTW-2026-10').mit_reduktion(bootstrap_B=200, eps_ctrl_datensaetze=300, h3_mc=200)
ZEIT = dict(T_park=2.0, T_ramp=2.0, T_ab=1.0, T_eP=4.0, T_aP=10.0, T_verfuegbar=4 * 86400.0, d=2, N_K=21, N_I=0)


def _mit(profil, rid, wert):
    """Profil mit geändertem Regelwert (für Prüfungen der Bindung)."""
    r = profil.eintrag(rid)
    neu = regeln.Regel(r.id, r.gegenstand, r.fundstelle, r.status, wert, r.herkunft, r.wirkung)
    return regeln.Regelprofil(profil.id, 'Test', [neu if x.id == rid else x for x in profil.regeln.values()],
                              profil.reduktion)


@pytest.fixture(scope='module')
def a4():
    m, laeufe, tab = kette.kampagne_erzeugen('N01-A4', 'L1', PLAN, 5)
    _, _, kal = kette.kalibrierung_erzeugen(szenarien.KATALOG['N01-A4'], m, 5)
    return m, tab.auswahl(tab.spalte('phase', int) == 0).sortiert(), kal


def _aufruf(m, t0, kal, k=9):
    s = pilot.satz_fuer_plan(t0, kal, AKTUELL, m.system.f, k, 5)
    ung = set(s['gueltigkeit']['gruende'])
    g = np.array([x['lauf_id'] not in ung for x in t0.koepfe])
    T_lauf = 2.0 + 2.0 + 3.0 + 10.0 + 1.0
    return dict(k=k, N_z=100, T_a=10.0, T_e=3.0, T_lauf=T_lauf, zeit=dict(ZEIT), s_q=s['streuungen'],
                kovarianzen=s['kovarianzen'], p_hat=s['p_hat'], n_max=pilot.n_max(T_lauf, s['p_hat'], ZEIT), tabelle=t0,
                gueltig=g, kal=kal, f=m.system.f, laufgroessen=s['laufgroessen'], bindung=s['bindung'])


# ── Regeln ──────────────────────────────────────────────────────────────────────────────────────────
def test_rauschquelle_und_teil_b_werte_an_regeln_gebunden():
    assert planung.rauschquelle_regel(HIST) == 'szenario' and planung.c_planung(HIST) is False
    assert planung.rauschquelle_regel(AKTUELL) == 'phase0_modell' and planung.c_planung(AKTUELL) is True
    assert planung.rauschquelle_regel(AKTUELL, 'szenario_orakel') == 'szenario_orakel'
    with pytest.raises(ValueError):
        planung.rauschquelle_regel(HIST, 'phase0_modell')
    with pytest.raises(ValueError, match='unbekannt'):
        planung.rauschquelle_regel(AKTUELL, 'gauss')
    for rid, wert, text in (('harness.planung_rauschen', 'szenario', 'nicht umgesetzt'),
                            ('planung.obere_grenze', 'ein_faktor', 'nicht umgesetzt'),
                            ('rauschmodelle', dict(AKTUELL.wert('rauschmodelle'), standard='gauss'),
                             'nicht umgesetzt')):
        with pytest.raises(ValueError, match=text):
            planung.rauschquelle_regel(_mit(AKTUELL, rid, wert))
    with pytest.raises(ValueError, match='nicht umgesetzt'):
        planung.c_planung(_mit(AKTUELL, 'planung.teil_b_werte', 'obere_grenze'))
    with pytest.raises(ValueError, match='p0.strukturmodell'):
        p0m.regeln_pruefen(_mit(AKTUELL, 'p0.strukturmodell', dict(punkt='ohne Abschneiden')))


# ── Haken ohne Szenario ─────────────────────────────────────────────────────────────────────────────
def test_haken_phase0_modellquelle_und_obere_grenzen(a4, monkeypatch):
    """Der Haken baut das Modell nur aus dem Aufruf des Pilotskripts: Struktur aus P0.8, Strukturmodell an den
    oberen 80-%-Grenzen je Komponente (gemeinsamer Bodenfaktor), c_B; kein Zugriff auf Szenario oder Wahrheit."""
    m, t0, kal = a4
    e = _aufruf(m, t0, kal)
    gesehen = []

    def attrappe(sid_, stufe_, profil_, n_kal, n_pruef, seed, plan=None, n_min=None, **kw):
        gesehen.append(dict(sid=sid_, stufe=stufe_, plan=plan, n_min=n_min, **kw))
        return dict(gemeinsame_bestaetigung=dict(rate=0.9, mc_se=0.0, zaehler=1, nenner=1), c_H1=dict(wert=3.7),
                    h2=dict(schluessel='perzentil_0.95'), pruefung=None)

    def verboten(*a, **kw):
        raise AssertionError('Szenariozugriff im Phase-0-Haken')
    monkeypatch.setattr(planung.kalibrierung, 'kalibrieren', attrappe)
    monkeypatch.setattr(szenarien, 'modell', verboten)
    monkeypatch.setattr(szenarien, 'KATALOG', {})
    monkeypatch.setattr(kampagnen, 'wahrheit_kurz', verboten)
    prot = []
    hk = planung.haken_phase0(AKTUELL, 2, 2, 77, n_kandidaten=(18,), plan_basis=PLAN, protokoll=prot)
    out = hk(e)
    g = gesehen[0]
    q = g['quelle']
    assert g['sid'] is None and g['c_planung'] is True and isinstance(q, p0m.Modellquelle)
    assert g['plan'].n_zyklen == 100 and g['plan'].n_bloecke == 18 + out['kandidaten'][0]['reserve_r']
    soll = p0m.aus_laufgroessen(e['laufgroessen'], 'oben80')
    assert g['rauschvarianten'] == [soll] and q.rausch == soll
    assert 'szenario' not in str(q.kennung()['beschreibung']['herkunft']).lower()
    assert out['rauschquelle'] == 'phase0_modell' and out['c_planung'] == 'c_B' and out['kappa'] is None
    og = out['obere_grenzen']
    assert og['sigma_a']['oben80'] == e['laufgroessen']['komponenten']['sigma_a_oben80']
    assert og['boden_mittel']['faktor'] == pytest.approx(lgm.kappa(e['laufgroessen']['boden']['nu_m']))
    assert 'keine gemeinsame 80-%-Garantie' in og['lesart'] and out['szenario_kennzeichnung'] is None
    assert 'Phase-0-Modell' in out['quelle'] and out['n_min'] == 18
    pilot.pruefe_ausgabe(dict(planung=out))
    # ohne Laufgrößen im Aufruf: aus Tabelle, Gültigkeit und k berechnet (gleiches Ergebnis)
    e2 = {x: v for x, v in e.items() if x != 'laufgroessen'}
    hk(e2)
    assert gesehen[-1]['rauschvarianten'] == [soll]
    with pytest.raises(ValueError, match='passen nicht'):
        hk(dict(e, k=8))


def test_haken_phase0_im_pilotskript_ohne_szenario(a4, monkeypatch):
    """Pilotskript mit Phase-0-Haken (eine Kampagne je Simulation): die Kampagnen laufen ohne Szenario
    (szenarien.modell und der Katalog sind gesperrt), die Prüfsimulation rechnet mit c_B."""
    m, t0, kal = a4

    def verboten(*a, **kw):
        raise AssertionError('Szenariozugriff')
    monkeypatch.setattr(szenarien, 'modell', verboten)
    monkeypatch.setattr(szenarien, 'KATALOG', {})
    monkeypatch.setattr(kampagnen, 'wahrheit_kurz', verboten)
    erg = []
    alt = kalibrierung.kalibrieren

    def mitschnitt(*a, **kw):
        r = alt(*a, **kw)
        erg.append(r)
        return r
    monkeypatch.setattr(planung.kalibrierung, 'kalibrieren', mitschnitt)
    prot = []
    hk = planung.haken_phase0(AKTUELL, 1, 1, 77, n_kandidaten=(18,), plan_basis=PLAN, protokoll=prot, max_aufrufe=1)
    out = pilot.pilot_auswerten(t0, kal, AKTUELL, m.system.f, zeit=ZEIT, seed=5, planung=hk)
    pilot.pruefe_ausgabe(out)
    k = erg[0]
    nu = 18 + prot[0]['kandidaten'][0]['reserve_r'] - 1
    assert k['werkzeug8']['c_H1'] == pytest.approx(stats.t.ppf(1 - 0.05 / 294, nu)) and k['c_planung'] == 'c_B'
    assert k['meta']['szenario'] is None and k['laeufe']['pruefung']['szenario'].startswith('phase0:')
    assert k['modellquelle']['sha256'] == k['laeufe']['pruefung']['modellquelle']
    assert k['raten_pruefung']['wahrheit']['klasse'] == 'R0'
    assert prot[0]['kandidaten'][0]['nenner'] == 1 and prot[0]['reduziert']


# ── Kampagnen aus einer Modellquelle ────────────────────────────────────────────────────────────────
def test_kampagne_aus_modellquelle_teil_b_und_wahrheit(a4):
    m, t0, kal = a4
    e = _aufruf(m, t0, kal)
    q, lg = planung.quelle_aus_aufruf(e, 'punkt', profil=AKTUELL)
    r = p0r.kampagne_quelle(q, AKTUELL, PLAN, 11, n_min=18)
    tb = r['teil_b']
    assert r['tabelle'].meta['generator']['parameter'] == q.rausch.name and r['modell'].szenario is None
    assert tb['nr2']['laufgroessen']['bindung']['k'] == 9 and len(tb['nr2']['sigma_a_j']['wert']) == 3
    assert r['ergebnis']['n_auswertbar'] == 21
    w = p0r.wahrheit_quelle(q, PLAN)
    assert w['klasse'] == 'R0' and 'keine Szenario-Wahrheit' in w['quelle']
    b = kampagnen.kurzbefund(r['ergebnis'], tb, 11)
    assert b['seed'] == 11 and b['teil_b']['bindung'] == 'plan'
    with pytest.raises(ValueError, match='statische Laufplan'):
        from pcmms_auswertung import verfahren as vf
        p0r.kampagne_quelle(q, AKTUELL, PLAN, 11, verfahren=vf.ZUSTAND)


def test_c_nach_regel_standardmodell_und_maximum():
    rng = np.random.default_rng(3)

    def lauf(s, name):
        return dict(meta=dict(rauschmodell=name), befunde=[dict(felder=dict(r0=s * rng.standard_normal((21, 7)),
                                                                            v0=np.ones((21, 7)))) for _ in range(60)])
    kal = [lauf(1.0, 'struktur'), lauf(1.5, 'familie')]
    b0 = dict(bias=np.zeros(21), u=np.zeros(21))
    ca, je = kalibrierung.c_nach_regel(kal, 'a', b0, 0)
    cb, _ = kalibrierung.c_nach_regel(kal, 'b', b0, 0)
    assert ca['c'] == pytest.approx(je[0]['c']) and cb['c'] == pytest.approx(max(x['c'] for x in je))
    assert je[1]['c'] > je[0]['c'] and [x['rauschmodell'] for x in je] == ['struktur', 'familie']
    with pytest.raises(ValueError, match='nicht umgesetzt'):
        kalibrierung.c_nach_regel(kal, 'c', b0, 0)


def test_teil_b_werte_mit_punktschaetzern_modellliste_und_sensitivitaeten(a4, monkeypatch):
    m, t0, kal = a4
    e = _aufruf(m, t0, kal)
    gesehen = []

    def attrappe(sid_, stufe_, profil_, n_kal, n_pruef, seed, plan=None, n_min=None, **kw):
        gesehen.append(dict(seed=seed, n_min=n_min, **kw))
        return dict(werkzeug8=dict(c_H1=3.9), c_varianten=[], gemeinsame_bestaetigung=dict(rate=0.9),
                    rauschbias=dict(b0=np.zeros(21)), h2=dict(schluessel='perzentil_0.95'), meta={}, pruefung=None,
                    c_H1=dict(wert=3.9))
    monkeypatch.setattr(planung.kalibrierung, 'kalibrieren', attrappe)
    r = planung.teil_b_werte(e, AKTUELL, 10, 10, 5, PLAN, 18, sensitivitaeten=('jitter_farbig', 'drift_phase1'))
    g = gesehen[0]
    lg = e['laufgroessen']
    assert g['rauschvarianten'][0] == p0m.aus_laufgroessen(lg, 'punkt')
    assert g['rauschvarianten'][1] == p0m.familienanpassung(lg, 'punkt') and 'c_planung' not in g
    assert r['werkzeug8']['teil_b_werte'] == 'punktschaetzer' and r['werkzeug8']['rauschmodelle'][1].startswith(
        'familie')
    assert set(r['sensitivitaeten']) == {'jitter_farbig', 'drift_phase1'}
    assert gesehen[1]['rauschvarianten'][0].jitter_ar1 == 0.9 and gesehen[1]['seed'] == g['seed']   # gepaart
    assert gesehen[2]['quelle'].effekte == ({'art': 'drift_basis', 'faktor': 0.001},)
    with pytest.raises(ValueError, match='2026-11'):
        planung.teil_b_werte(e, HIST, 10, 10, 5, PLAN, 18)
    with pytest.raises(ValueError, match='rauschmodelle'):
        planung.teil_b_werte(e, _mit(AKTUELL, 'rauschmodelle', dict(AKTUELL.wert('rauschmodelle'),
                                                                   bootstrap='pflicht')), 10, 10, 5, PLAN, 18)


# ── Rechnungen R1-d bis R3-d ────────────────────────────────────────────────────────────────────────
def test_auftragslisten_r1d_r2d_r3d_ohne_start():
    a1 = p0r.r1d_auftraege()
    assert len(a1) == 9 * 1000 and len({a['seed'] for a in a1}) == len(a1) and a1 == p0r.r1d_auftraege()
    assert {(a['szenario'], a['stufe']) for a in a1} == set(p0r.R1D_PUNKTE)
    a2 = p0r.r2d_auftraege()
    assert len(a2) == 4 and all(a['n_kal'] == a['n_pruef'] == 400 and a['bootstrap_B'] == 1000 for a in a2)
    assert a2[0]['seed'] == a2[1]['seed'] and a2[0]['generator'] != a2[1]['generator']        # gepaart
    a3 = p0r.r3d_auftraege()
    assert [a['haken'] for a in a3] == ['phase0_modell', 'szenario_orakel'] and a3[0]['seed'] == a3[1]['seed']
    assert a3[0]['n_kal'] == a3[0]['n_pruef'] == 200


def test_r1d_kleinstlauf_und_auswertung():
    a = p0r.r1d_auftraege(n_saetze=2, punkte=(('N01-A4', 'L2'),))
    erg = [p0r.r1d_satz(x) for x in a]
    z = p0r.r1d_auswerten(erg)['N01-A4/L2']
    assert z['n'] == 2 and len(z['sigma_a']['verhaeltnis_mittel']) == 3
    assert all(0.5 < v < 1.5 for v in z['sigma_a']['verhaeltnis_mittel'])
    assert all(0.9 < v < 1.1 for v in z['sigma_h_zellen']['verhaeltnis_mittel'])
    assert 'ueberdeckung_oben80' in z['sigma_delta_grad'] and erg[0]['wahr']['sigma_a'] == [0.01] * 3
    formate.sha256_json(erg)                                               # JSON-fähig


def test_r2d_variante_bekannt_bitgleich():
    r = p0r.r2d_bekannt_gleich('N01-A4', 'L1', PLAN, 7, AKTUELL)
    assert r['tabelle_gleich'] and r['gleich']
