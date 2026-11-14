"""Herkunftsnachweis der Phase-0-Läufe und Bindung Phase 0 ↔ Teil B (herkunft.py, eingeführt mit pilot-0.5 und
teil_b-0.5; Entscheidung des Autors vom 12.11.2026, docs/entscheidungsnotiz_herkunft_phase0_2026-11-12.md), dazu die
Ergebnisprüfung der Werte über Kennwerte mit Toleranz (kennwerte.py, pilot-0.6 und teil_b-0.6; Entscheidung E-4).

Die Tests N1 bis N15 sind die Negativtests der Notiz (Abschnitt 7): Jeder verändert eine Angabe zur Herkunft und
erwartet, dass Teil B die Läufe zurückweist. P1 und P2 sind die Gegenproben, die angenommen werden müssen. Dazu: der
Inhalt des Nachweises in Teil B und die unveränderte Bindung unter den historischen Profilen. Die Tests W1 bis W6
prüfen die Ergebnisprüfung: Der Nachweis belegt die Herkunft, die Kennwerte prüfen die Werte.

Alle Daten sind synthetisch: Generator auf Ebene H, für Läufe mit Rohdatei Ebene Z mit Stufe 1. Geprüft wird die
Software, keine Apparatur."""
import dataclasses
import json
import os
import subprocess
import sys

import numpy as np
import pytest

from pcmms_auswertung import formate, herkunft, kennwerte, pilot, regeln, stufe1, teil_b, zufall
from pcmms_auswertung import zusammenfassung as zf
from pcmms_auswertung.generator import ebene_h, kampagne as kp, phase0_modell as p0m, rauschen, szenarien
from pcmms_auswertung.harness import kette

CODE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'code')
PROFIL = regeln.profil('ENTW-2026-11').mit_reduktion(bootstrap_B=50, h3_mc=50, eps_ctrl_datensaetze=200)
HIST = regeln.profil('ENTW-2026-10').mit_reduktion(bootstrap_B=50, h3_mc=50, eps_ctrl_datensaetze=200)
PLAN = kp.Plan(n0=20, n_pilot=20, n_bloecke=2)
SID, STUFE, SEED = 'N01-V1G0', 'L1', 7                       # k der Pilotgrößen = k_max: Teil B übernimmt den Satz
W8 = kette.testvorgabe_werkzeug8()
GN = zf.META_GENERATORNACHWEIS
ANDERE_DATEN = 'aus anderen Phase-0-Daten'
ANDERE_WERTE = 'dieselbe Herkunft wie in der Pilotausgabe, aber andere Werte'
SHA_A, SHA_B = 'a' * 64, 'b' * 64


def _phase0(tab):
    return tab.auswahl(tab.spalte('phase', int) == 0)


def _mit_kopf(tab, i, **aenderung):
    """Kopie der Tabelle, in der der Kopf des Laufs i geändert ist; Daten und Metadaten bleiben."""
    koepfe = [dict(k, **aenderung) if j == i else k for j, k in enumerate(tab.koepfe)]
    return zf.LaufTabelle(koepfe, tab.daten, meta=tab.meta)


def _mit_meta(tab, **meta):
    return zf.LaufTabelle(tab.koepfe, tab.daten, meta=dict(tab.meta, **meta))


def _satz(b, tab, pe=None, profil=PROFIL):
    return teil_b.phase0_satz(tab, b['kal'], b['pe'] if pe is None else pe, profil, b['plan'])


def _abgelehnt(b, tab, text=ANDERE_DATEN):
    """Teil B weist die Läufe tab zur Pilotausgabe der Basiskampagne zurück."""
    with pytest.raises(ValueError, match=text):
        _satz(b, tab)


def _blaetter(o):
    if isinstance(o, dict):
        for v in o.values():
            yield from _blaetter(v)
    elif isinstance(o, list):
        for v in o:
            yield from _blaetter(v)
    else:
        yield o


@pytest.fixture(scope='module')
def basis():
    """Kampagne auf Ebene H mit Kalibrierung und Pilotausgabe; t0 sind ihre Phase-0-Läufe."""
    m, laeufe, tab = kette.kampagne_erzeugen(SID, STUFE, PLAN, SEED)
    _, _, kal = kette.kalibrierung_erzeugen(szenarien.KATALOG[SID], m, SEED)
    t0 = _phase0(tab)
    pe = pilot.pilot_auswerten(t0, kal, PROFIL, m.system.f, seed=SEED)
    return dict(m=m, laeufe=laeufe, tab=tab, t0=t0, kal=kal, pe=pe, plan=kette.plan_info(m), nw=herkunft.nachweis(t0))


@pytest.fixture(scope='module')
def z(tmp_path_factory):
    """Phase 0 einer kleinen Kampagne auf Ebene Z (56 Läufe, 40 Zyklen): Rohdatei je Lauf, Stufe 1, Pilotausgabe.
    k der Pilotgrößen ist 30, k_max des Plans 9: Teil B rechnet den Satz neu."""
    verzeichnis = str(tmp_path_factory.mktemp('rohdaten'))
    sid, seed = 'N01-A4', 13
    m = szenarien.modell(sid, STUFE, plan=kp.Plan(n0=10, n_pilot=6, n_bloecke=2, ref_min_p0=8, n_zyklen=40))
    laeufe = kp.laufplan(m.plan, zufall.strom(seed, 'reihenfolge'))
    _, kwahr, kal = kette.kalibrierung_erzeugen(szenarien.KATALOG[sid], m, seed)
    kw = dict(nullpunkt_adc=kwahr['p01']['nullpunkt_adc'],
              empfindlichkeit_N_je_adc=kwahr['p01']['empfindlichkeit_N_je_adc'])
    messung = kette.MessungZ(m, laeufe, seed, verzeichnis, kw, kal, formate.synth_kennung('HERKUNFT', 'Z'))
    t0 = messung.phase0(laeufe)
    pe = pilot.pilot_auswerten(t0, kal, PROFIL, m.system.f, seed=seed)
    return dict(m=m, t0=t0, kal=kal, pe=pe, plan=kette.plan_info(m), verzeichnis=verzeichnis,
                manifest={x['lauf_id']: x for x in messung.manifest}, nw=herkunft.nachweis(t0))


# ── Inhalt des Nachweises ────────────────────────────────────────────────────────────────────────────
def test_teil_b_fuehrt_den_nachweis_der_ebene_h(basis):
    """Teil B (teil_b-0.5) führt in nr1 den Nachweis statt einer Prüfsumme der Datenfelder; Läufe der Ebene H tragen
    keinen Rohdatei-Hash, die Tabelle den Generatornachweis mit dem Aufruf."""
    t0, pe = basis['t0'], basis['pe']
    tb = teil_b.erstellen(t0, basis['kal'], pe, PROFIL, basis['plan'], W8, seed_b0=1, B=50)
    n1, b = tb['nr1'], tb['nr2']['phase0_bindung']
    assert tb['version'] == teil_b.VERSION == 'teil_b-0.6' and pe['version'] == pilot.VERSION == 'pilot-0.6'
    assert 'phase0_sha256' not in n1 and 'phase0_optionale_sha256' not in n1
    nw = n1['phase0_herkunft']
    assert nw == basis['nw'] == pe['phase0_herkunft'] and n1['phase0_herkunft_sha256'] == herkunft.sha256(nw)
    assert (nw['version'], nw['datenart']) == (herkunft.VERSION, 'synthetisch') == ('herkunft-1', 'synthetisch')
    assert nw['klassen'] == dict(rohdatei=0, generator=len(t0)) and nw['optionale_felder'] == ['fuenftel_zeiger']
    assert [l['position'] for l in nw['laeufe']] == sorted(k['position'] for k in t0.koepfe)
    assert all(set(l) == {'lauf_id', 'position', 'klasse', 'version_stufe1'} and l['klasse'] == 'generator'
               and l['version_stufe1'] == ebene_h.VERSION for l in nw['laeufe'])        # kein Rohdatei-Hash
    g = nw['generator']
    assert set(g) == set(herkunft.GENERATOR_FELDER) and g['version'] == ebene_h.VERSION
    assert g['aufruf'] == dict(szenario=SID, stufe=STUFE, seed=SEED, stroeme=kette.STROEME)
    assert g['modell_sha256'] == formate.sha256_json(szenarien.beschreibung(basis['m']))
    assert g['strom_sha256'] == herkunft.strom_sha256(zufall.strom(SEED, 'generator'))
    assert g['laufplan_sha256'] == formate.sha256_json(basis['laeufe']) and g['zusatzstrom_sha256'] is None
    # nur exakte Angaben: keine Gleitkommazahl im Nachweis
    assert all(isinstance(x, (str, int)) or x is None for x in _blaetter(nw))
    # Bindung: Prüfsumme des Nachweises, keine Prüfsumme der Datenfelder
    assert b['bindung'][pilot.FELD_HERKUNFT] == b['phase0_herkunft_sha256'] == n1['phase0_herkunft_sha256']
    assert 'phase0_sha256' not in b['bindung'] and b['bindung']['version'] == 'pilot-0.6'
    assert b['quelle'] == 'Pilotskript, oberste Ebene' and b['pilot_herkunft'] == 'oberste Ebene'
    pilot.pruefe_ausgabe(pe)


def test_ebene_z_teil_b_fuehrt_die_rohdaten_pruefsummen(z):
    """A9.3 Nr. 1: Für Läufe mit Rohdatei nennt Teil B je Lauf die SHA-256-Prüfsumme der Rohdatei (gleich der Datei
    auf der Platte und dem Manifest), die des Kalibrierobjekts und die Version von Stufe 1."""
    t0 = z['t0']
    tb = teil_b.erstellen(t0, z['kal'], z['pe'], PROFIL, z['plan'], W8, seed_b0=1, B=50)
    nw = tb['nr1']['phase0_herkunft']
    assert nw == z['nw'] and nw['klassen'] == dict(rohdatei=len(t0), generator=0) and nw['generator'] is None
    assert len(nw['laeufe']) == len(z['manifest']) == len(t0) > 40
    for l in nw['laeufe']:
        assert set(l) == {'lauf_id', 'position', 'klasse', 'hash_rohdatei', 'kalibrier_hash', 'version_stufe1'}
        datei = os.path.join(z['verzeichnis'], l['lauf_id'] + '.npz')
        assert l['hash_rohdatei'] == z['manifest'][l['lauf_id']]['sha256_daten'] == formate.sha256_datei(datei)
        assert l['kalibrier_hash'] == formate.sha256_json(z['kal']) and l['version_stufe1'] == stufe1.VERSION
    b = tb['nr2']['phase0_bindung']
    assert b['neu_berechnet'] and b['bindung'][pilot.FELD_HERKUNFT] == tb['nr1']['phase0_herkunft_sha256']


def test_generator_legt_den_nachweis_an_und_dateien_erhalten_ihn(basis, tmp_path):
    """Jede Tabelle der Ebene H trägt den Nachweis vom Generator, ohne dass sich Daten oder Laufköpfe ändern; Vorrat
    (Ablauf) und erzeuge ergeben denselben Nachweis; Schreiben und Lesen erhalten ihn."""
    m, laeufe = basis['m'], basis['laeufe']
    a = ebene_h.erzeuge(m, laeufe, zufall.strom(SEED, 'generator'))
    v = ebene_h.Vorrat(m, laeufe, zufall.strom(SEED, 'generator')).tabelle([l for l in laeufe if l['phase'] == 0])
    assert a.meta[GN] == v.meta[GN] == dict(basis['tab'].meta[GN], aufruf=None)
    assert formate.sha256_json(a.koepfe) == formate.sha256_json(basis['tab'].koepfe)
    assert all(k['hash_rohdatei'] is None and k['kalibrier_hash'] is None for k in a.koepfe)
    assert all(np.array_equal(a.daten[f], basis['tab'].daten[f], equal_nan=True) for f in a.daten)
    assert kette.MessungH(m, laeufe, SEED).phase0(laeufe).meta[GN] == a.meta[GN]
    # Strukturgenerator: eigene Version, Zusatzstrom im Nachweis
    s = p0m.erzeuge(m, laeufe, zufall.strom(SEED, 'generator'), rng_zusatz=zufall.strom(SEED, 'generator_struktur'))
    assert s.meta[GN]['version'] == p0m.VERSION and s.meta[GN]['strom_sha256'] == a.meta[GN]['strom_sha256']
    assert s.meta[GN]['zusatzstrom_sha256'] == herkunft.strom_sha256(zufall.strom(SEED, 'generator_struktur'))
    assert herkunft.sha256(herkunft.nachweis(_phase0(s))) != herkunft.sha256(herkunft.nachweis(_phase0(a)))
    # Datei: Tabelle und Pilotausgabe
    basis['tab'].schreiben(str(tmp_path / 'zf'), formate.synth_kennung('HERKUNFT'))
    gelesen = zf.LaufTabelle.lesen(str(tmp_path / 'zf'))
    assert gelesen.meta[GN] == basis['tab'].meta[GN] and herkunft.nachweis(_phase0(gelesen)) == basis['nw']
    pilot.schreibe_pilot(str(tmp_path / 'pilot'), basis['pe'], formate.synth_kennung('HERKUNFT'))
    pe = pilot.lies_pilot(str(tmp_path / 'pilot'))[1]
    assert pe['phase0_herkunft'] == basis['nw']
    _, info = _satz(basis, _phase0(gelesen), pe)
    assert info['quelle'] == 'Pilotskript, oberste Ebene' and not info['neu_berechnet']


def test_satz_der_suche_mit_gekuerztem_fenster(basis):
    """Legt die Suche des Pilotskripts ein kürzeres Fenster fest (hier N_z = 20 mit einem Testhaken, kein
    qualifizierter Arbeitspunkt), trägt ihr Satz den Nachweis der dafür erzeugten Tabelle. Teil B nimmt genau diese
    Läufe an und ordnet sie dem Satz der Suche zu; eine andere Tabelle mit demselben Fenster und ein Fenster, das die
    Suche nicht festgelegt hat, weist es zurück, auch wenn es den Satz neu rechnen könnte."""
    m, laeufe, kal = basis['m'], basis['laeufe'], basis['kal']
    zeit = dict(T_park=2.0, T_ramp=2.0, T_ab=2.0, T_eP=3.0, T_aP=12.0, T_verfuegbar=8 * 3600, d=1, N_K=21, N_I=0)

    def tabelle_fuer(N_z, seed=SEED):
        m2 = szenarien.modell(SID, STUFE, plan=PLAN.mit(n_zyklen=N_z))
        return ebene_h.erzeuge(m2, laeufe, zufall.strom(seed, 'generator'))
    pe = pilot.pilot_auswerten(basis['t0'], kal, PROFIL, m.system.f, zeit=zeit, seed=SEED, tabelle_fuer=tabelle_fuer,
                               N_z_raster=(20, 60), planung=lambda e: dict(n_min=12, n0=20, quelle='Testhaken'))
    s = pe['suche']
    assert s['ergebnis'] == 'festgelegt' and (s['k_max'], s['N_z']) == (12, 20)
    oben, such = pe['phase0_herkunft'], s['satz']['phase0_herkunft']
    assert oben == basis['nw'] and such['laeufe'] == oben['laeufe']
    assert [x for x in oben['generator'] if oben['generator'][x] != such['generator'][x]] == ['modell_sha256', 'aufruf']
    assert pilot.herkunft_belege(pe) == [('oberste Ebene', herkunft.sha256(oben), oben),
                                        ('Suche', herkunft.sha256(such), such)]
    plan = dict(f=m.system.f, k_max=s['k_max'], N_z=s['N_z'], n_min=s['n_min'], n0=s['n0'], r=s['reserve_r'],
                n=s['n'], d=1, n_max=s['n_max'], zeit=s['zeit'], T_lauf=s['T_lauf'], p_hat=s['p_hat'])
    satz, info = teil_b.phase0_satz(_phase0(tabelle_fuer(20)), kal, pe, PROFIL, plan)
    assert info['pilot_herkunft'] == 'Suche' and info['quelle'] == 'Pilotskript, Suche' and not info['neu_berechnet']
    assert satz['bindung'][pilot.FELD_HERKUNFT] == herkunft.sha256(such) == info['phase0_herkunft_sha256']
    with pytest.raises(ValueError, match='strom_sha256'):                    # dasselbe Fenster, anderer Strom
        teil_b.phase0_satz(_phase0(tabelle_fuer(20, SEED + 1)), kal, pe, PROFIL, plan)
    with pytest.raises(ValueError, match='modell_sha256'):                   # Fenster, das die Suche nicht festlegte
        teil_b.phase0_satz(_phase0(tabelle_fuer(60)), kal, pe, PROFIL, dict(plan, N_z=60))
    with pytest.raises(ValueError, match='N_z = 100 Zyklen passen nicht zum Plan'):
        teil_b.phase0_satz(basis['t0'], kal, pe, PROFIL, plan)


# ── Negativtests: Läufe ohne Rohdatei (Ebene H) ──────────────────────────────────────────────────────
def test_n1_anderer_seed(basis):
    """N1: dieselbe Kampagne mit einem anderen Seed; dann nur der Generatorstrom anders (gleiche Läufe, gleiches
    Modell); dann derselbe Strom mit einem Seed im Aufruf, der ihn nicht ergibt."""
    _abgelehnt(basis, _phase0(kette.kampagne_erzeugen(SID, STUFE, PLAN, SEED + 1)[2]))
    t = _phase0(ebene_h.erzeuge(basis['m'], basis['laeufe'], zufall.strom(SEED + 1, 'generator')))
    assert [k['lauf_id'] for k in t.koepfe] == [k['lauf_id'] for k in basis['t0'].koepfe]
    _abgelehnt(basis, t, 'strom_sha256')
    with pytest.raises(herkunft.HerkunftFehler, match='ergeben nicht den Zustand'):
        herkunft.mit_aufruf(t, SID, STUFE, SEED, kette.STROEME)
    falsch = _mit_meta(t, **{GN: dict(t.meta[GN], aufruf=basis['nw']['generator']['aufruf'])})
    with pytest.raises(ValueError, match='ergeben nicht den Zustand'):
        _satz(basis, falsch)


def test_n2_anderes_szenario_oder_geaendertes_modell(basis):
    """N2: ein anderes Szenario; dann dasselbe Szenario mit einem geänderten Modellwert bei gleichem Laufplan, Strom
    und Aufruf."""
    _abgelehnt(basis, _phase0(kette.kampagne_erzeugen('N01-A4', STUFE, PLAN, SEED)[2]))
    m2 = dataclasses.replace(basis['m'], vollausschlag_N=40.0)
    t = _phase0(ebene_h.erzeuge(m2, basis['laeufe'], zufall.strom(SEED, 'generator')))
    herkunft.mit_aufruf(t, SID, STUFE, SEED, kette.STROEME)
    _abgelehnt(basis, t, 'Generatornachweis: modell_sha256 abweichend')


@pytest.mark.parametrize('aenderung', [dict(plan=PLAN.mit(n_bloecke=3)), dict(k_max=7),
                                       dict(rausch=rauschen.stufe('L2'))], ids=['plan', 'k_max', 'rauschmodell'])
def test_n3_anderer_plan_k_max_oder_rauschmodell(basis, aenderung):
    """N3: derselbe Aufruf (Szenario, Stufe, Seed), aber ein anderer Plan, ein anderes k_max oder ein anderes
    Rauschmodell. Die Phase-0-Läufe haben dieselben Kennungen und Positionen; die Modellprüfsumme unterscheidet sie."""
    kw = dict(dict(plan=PLAN), **aenderung)
    t = _phase0(kette.kampagne_erzeugen(SID, STUFE, kw.pop('plan'), SEED, **kw)[2])
    assert [k['lauf_id'] for k in t.koepfe] == [k['lauf_id'] for k in basis['t0'].koepfe]
    assert t.meta[GN]['aufruf'] == basis['nw']['generator']['aufruf']
    _abgelehnt(basis, t, 'modell_sha256')


def test_n3_effektstaerke_steht_in_der_modellpruefsumme():
    """N3: zwei Effektstärken desselben Szenarios unterscheiden sich nur in der Modellprüfsumme."""
    laeufe = kp.laufplan(PLAN, zufall.strom(SEED, 'reihenfolge'))
    a, b = (ebene_h.generatornachweis(szenarien.modell('A04-R4', STUFE, plan=PLAN, staerke=x), laeufe,
                                      zufall.strom(SEED, 'generator')) for x in (0.01, 0.02))
    assert [x for x in a if a[x] != b[x]] == ['modell_sha256']


def test_n4_andere_generatorversion(basis, monkeypatch):
    """N4: dieselbe Kampagne mit einer anderen Generatorversion."""
    monkeypatch.setattr(ebene_h, 'VERSION', 'ebene_h-0.2')
    t = _phase0(kette.kampagne_erzeugen(SID, STUFE, PLAN, SEED)[2])
    assert t.meta[GN]['version'] == 'ebene_h-0.2' and {k['version_stufe1'] for k in t.koepfe} == {'ebene_h-0.2'}
    _abgelehnt(basis, t, 'Generatornachweis: version abweichend')


def test_n5_ebene_h_ohne_generatornachweis(basis):
    """N5: eine Tabelle der Ebene H ohne Generatornachweis (von Hand gebaut oder aus einer älteren Datei) wird vom
    Pilotskript und von Teil B zurückgewiesen; ebenso ein unvollständiger oder erweiterter Nachweis."""
    t0 = basis['t0']
    ohne = zf.LaufTabelle(t0.koepfe, t0.daten)
    with pytest.raises(herkunft.HerkunftFehler, match='ohne Generatornachweis'):
        herkunft.nachweis(ohne)
    with pytest.raises(ValueError, match='ohne Generatornachweis'):
        _satz(basis, ohne)
    with pytest.raises(ValueError, match='ohne Generatornachweis'):
        pilot.pilot_auswerten(ohne, basis['kal'], PROFIL, basis['m'].system.f, seed=SEED)
    g = t0.meta[GN]
    for falsch, text in (({k: v for k, v in g.items() if k != 'strom_sha256'}, 'strom_sha256 fehlt'),
                         (dict(g, modell_sha256='abc'), 'modell_sha256 fehlt oder ist keine SHA-256'),
                         (dict(g, version=None), 'version fehlt'), (dict(g, quelle='x'), 'unbekannte Felder'),
                         (dict(g, aufruf=dict(g['aufruf'], plan={})), 'aufruf mit genau den Feldern')):
        with pytest.raises(herkunft.HerkunftFehler, match=text):
            herkunft.nachweis(_mit_meta(t0, **{GN: falsch}))
    # ein Lauf der Ebene H mit einem Rohdatei-Hash, auch einem künstlichen
    for feld in ('hash_rohdatei', 'kalibrier_hash'):
        with pytest.raises(herkunft.HerkunftFehler, match='trägt keinen Rohdatei-Hash'):
            herkunft.nachweis(_mit_kopf(t0, 3, **{feld: SHA_A}))


def test_n6_lauf_entfernt_oder_hinzugefuegt(basis):
    """N6: ein Lauf fehlt; ein Lauf ist zusätzlich."""
    t0 = basis['t0']
    _abgelehnt(basis, t0.auswahl(np.arange(1, len(t0))), '1 Lauf fehlt')
    k = dict(t0.koepfe[-1], lauf_id='0-99999-R', position=99999)
    mehr = zf.LaufTabelle(t0.koepfe + [k], {n: np.concatenate([v, v[-1:]]) for n, v in t0.daten.items()}, meta=t0.meta)
    _abgelehnt(basis, mehr, '1 Lauf zusätzlich')


def test_n7_position_geaendert(basis):
    """N7: die Position eines Laufs geändert; die Positionen zweier Läufe vertauscht."""
    t0 = basis['t0']
    _abgelehnt(basis, _mit_kopf(t0, 5, position=99999), 'position abweichend')
    p5, p6 = t0.koepfe[5]['position'], t0.koepfe[6]['position']
    _abgelehnt(basis, _mit_kopf(_mit_kopf(t0, 5, position=p6), 6, position=p5), 'position abweichend')


def test_n8_doppelte_position(basis):
    """N8: zwei Läufe mit derselben Position sind ein Fehler."""
    t0 = basis['t0']
    with pytest.raises(herkunft.HerkunftFehler, match='Positionen mehrfach vergeben'):
        herkunft.nachweis(_mit_kopf(t0, 5, position=t0.koepfe[4]['position']))
    with pytest.raises(ValueError, match='Positionen mehrfach vergeben'):
        _satz(basis, _mit_kopf(t0, 5, position=t0.koepfe[4]['position']))


# ── Negativtests: Läufe mit Rohdatei (Ebene Z) ───────────────────────────────────────────────────────
def test_n9_n10_rohdatei_hash_geaendert_oder_vertauscht(z):
    """N9: der Rohdatei-Hash eines Laufs geändert; N10: die Hashes zweier Läufe vertauscht."""
    t0 = z['t0']
    _abgelehnt(z, _mit_kopf(t0, 3, hash_rohdatei=SHA_A), 'hash_rohdatei abweichend')
    h3, h4 = t0.koepfe[3]['hash_rohdatei'], t0.koepfe[4]['hash_rohdatei']
    _abgelehnt(z, _mit_kopf(_mit_kopf(t0, 3, hash_rohdatei=h4), 4, hash_rohdatei=h3), 'hash_rohdatei abweichend')


def test_n11_derselbe_rohdatei_hash_bei_zwei_laeufen(z):
    """N11: eine Rohdatei gehört zu genau einem Lauf."""
    t0 = z['t0']
    doppelt = _mit_kopf(t0, 3, hash_rohdatei=t0.koepfe[4]['hash_rohdatei'])
    with pytest.raises(herkunft.HerkunftFehler, match='derselbe Rohdatei-Hash bei mehreren Läufen'):
        herkunft.nachweis(doppelt)
    with pytest.raises(ValueError, match='derselbe Rohdatei-Hash bei mehreren Läufen'):
        _satz(z, doppelt)


def test_n12_kalibrier_hash_oder_version_geaendert(z):
    """N12: der Kalibrier-Hash oder die Version von Stufe 1 eines Laufs geändert."""
    _abgelehnt(z, _mit_kopf(z['t0'], 3, kalibrier_hash=SHA_B), 'kalibrier_hash abweichend')
    _abgelehnt(z, _mit_kopf(z['t0'], 3, version_stufe1='stufe1-0.1'), 'version_stufe1 abweichend')


def test_n13_ebene_z_ohne_rohdatei_hash(z):
    """N13: ein Lauf der Ebene Z ohne Rohdatei-Hash, mit leerem Hash oder mit etwas anderem als einer SHA-256."""
    for feld in ('hash_rohdatei', 'kalibrier_hash'):
        for wert in (None, '', 'abc', SHA_A.upper()):
            with pytest.raises(herkunft.HerkunftFehler, match=f'{feld} fehlt oder ist keine SHA-256'):
                herkunft.nachweis(_mit_kopf(z['t0'], 3, **{feld: wert}))
    with pytest.raises(ValueError, match='hash_rohdatei fehlt'):
        _satz(z, _mit_kopf(z['t0'], 3, hash_rohdatei=None))


def test_n14_datenart_messung_und_mischung(basis, z):
    """N14: bei Datenart messung sind Läufe ohne Rohdatei unzulässig; die Datenart geht in die Bindung ein. Bei
    synthetischen Daten sind beide Klassen in einem Satz zulässig und im Nachweis gekennzeichnet."""
    with pytest.raises(herkunft.HerkunftFehler, match='Datenart messung: Läufe ohne Rohdatei'):
        herkunft.nachweis(_mit_meta(basis['t0'], datenart='messung'))
    with pytest.raises(ValueError, match='Datenart messung'):
        _satz(basis, _mit_meta(basis['t0'], datenart='messung'))
    mess = herkunft.nachweis(_mit_meta(z['t0'], datenart='messung'))            # nur Läufe mit Rohdatei: zulässig
    assert mess['datenart'] == 'messung' and mess['laeufe'] == z['nw']['laeufe']
    assert herkunft.sha256(mess) != herkunft.sha256(z['nw'])
    _abgelehnt(z, _mit_meta(z['t0'], datenart='messung'), 'datenart')
    # Mischung: fünf Läufe mit Rohdatei und fünf ohne
    hk = [dict(k, lauf_id=k['lauf_id'] + '-H', position=k['position'] + 1000) for k in basis['t0'].koepfe[:5]]
    daten = {n: np.concatenate([z['t0'].daten[n][:5], basis['t0'].daten[n][:5]]) for n in z['t0'].daten}
    misch = zf.LaufTabelle(z['t0'].koepfe[:5] + hk, daten, meta=basis['t0'].meta)
    nw = herkunft.nachweis(misch)
    assert nw['klassen'] == dict(rohdatei=5, generator=5) and nw['generator'] == basis['nw']['generator']
    assert [l['klasse'] for l in nw['laeufe']] == ['rohdatei'] * 5 + ['generator'] * 5
    assert all(('hash_rohdatei' in l) == (l['klasse'] == 'rohdatei') for l in nw['laeufe'])
    with pytest.raises(herkunft.HerkunftFehler, match='Datenart messung'):
        herkunft.nachweis(_mit_meta(misch, datenart='messung'))
    with pytest.raises(herkunft.HerkunftFehler, match='ohne Generatornachweis'):
        herkunft.nachweis(zf.LaufTabelle(misch.koepfe, misch.daten))


# ── Versionierung und Altbestand ─────────────────────────────────────────────────────────────────────
def test_n15_satz_ohne_herkunftsnachweis_gilt_nicht_als_gebunden(basis):
    """N15: Eine Pilotausgabe ohne Herkunftsnachweis (historisches Profil, Fassung pilot-0.3; oder der Stand
    pilot-0.4 mit der Prüfsumme der Datenfelder) wird unter teil_b-0.5 nicht übernommen, auch wenn k, N_z und die
    Datenfelder passen. Ein Nachweis, der nicht zu seiner Prüfsumme passt, ebenso wenig."""
    t0, kal, pe = basis['t0'], basis['kal'], basis['pe']
    alt = pilot.pilot_auswerten(t0, kal, HIST, basis['m'].system.f, seed=SEED)
    assert alt['version'] == 'pilot-0.3' and alt['bindung']['phase0_sha256'] == pilot.daten_sha256(t0)
    with pytest.raises(ValueError, match='Pilotausgabe ohne Herkunftsnachweis'):
        teil_b.erstellen(t0, kal, alt, PROFIL, basis['plan'], W8, seed_b0=1, B=50)
    b04 = {k: v for k, v in pe['bindung'].items() if k != pilot.FELD_HERKUNFT}
    b04.update(phase0_sha256=pilot.daten_sha256(t0), version='pilot-0.4')
    p04 = dict({k: v for k, v in pe.items() if k != 'phase0_herkunft'}, bindung=b04, version='pilot-0.4')
    with pytest.raises(ValueError, match='Pilotausgabe ohne Herkunftsnachweis'):
        _satz(basis, t0, p04)
    for falsch in (dict(pe, bindung=dict(pe['bindung'], **{pilot.FELD_HERKUNFT: SHA_A})),
                   dict(pe, phase0_herkunft=dict(pe['phase0_herkunft'], datenart='messung')),
                   {k: v for k, v in pe.items() if k != 'phase0_herkunft'}):
        with pytest.raises(ValueError, match='fehlt oder passt nicht zu seiner Prüfsumme'):
            _satz(basis, t0, falsch)
    # gleich_gebunden: nur Bindungen derselben Fassung mit einer Angabe zu den Läufen bezeichnen denselben Satz
    neu = pe['bindung']
    assert teil_b.gleich_gebunden(neu, dict(neu, quelle='andere Quellangabe'))
    assert not teil_b.gleich_gebunden(neu, dict(neu, **{pilot.FELD_HERKUNFT: SHA_A}))
    assert not teil_b.gleich_gebunden(neu, dict(b04, version=neu['version']))
    ohne = {k: v for k, v in neu.items() if k != pilot.FELD_HERKUNFT}
    assert not teil_b.gleich_gebunden(ohne, ohne) and not teil_b.gleich_gebunden(neu, None)


def test_historische_profile_binden_unveraendert(basis):
    """Unter den historischen Profilen bleiben Pilotausgabe (pilot-0.3), Teil B (teil_b-0.3) und die Bindung über
    die Prüfsumme der Datenfelder, wie sie waren; ein Generatornachweis wird dort nicht verlangt."""
    t0, kal = basis['t0'], basis['kal']
    ohne = zf.LaufTabelle(t0.koepfe, t0.daten)
    pe = pilot.pilot_auswerten(ohne, kal, HIST, basis['m'].system.f, seed=SEED)
    assert pe['version'] == 'pilot-0.3' and 'phase0_herkunft' not in pe and pilot.FELD_HERKUNFT not in pe['bindung']
    assert pe['bindung']['phase0_sha256'] == pilot.daten_sha256(t0)
    tb = teil_b.erstellen(ohne, kal, pe, HIST, basis['plan'], W8, seed_b0=1, B=50)
    n1, b = tb['nr1'], tb['nr2']['phase0_bindung']
    assert tb['version'] == 'teil_b-0.3' and 'phase0_herkunft' not in n1 and 'phase0_herkunft_sha256' not in b
    assert n1['phase0_sha256'] == formate.sha256_bytes(formate.npz_bytes(zf.pflichtfelder(t0.daten)))
    assert b['bindung']['phase0_sha256'] == pilot.daten_sha256(t0) and 'pilot_herkunft' not in b
    fremd = dict(pe, bindung=dict(pe['bindung'], phase0_sha256=SHA_A))
    with pytest.raises(ValueError, match=ANDERE_DATEN):
        _satz(basis, ohne, fremd, HIST)


# ── Gegenproben und Grenze ───────────────────────────────────────────────────────────────────────────
def test_p1_andere_zeilenreihenfolge_wird_angenommen(basis, z):
    """P1: dieselben Läufe in anderer Zeilenreihenfolge ergeben denselben Nachweis; Teil B übernimmt den Satz."""
    for b in (basis, z):
        t0 = b['t0']
        um = t0.auswahl(np.arange(len(t0))[::-1])
        assert [k['lauf_id'] for k in um.koepfe] != [k['lauf_id'] for k in t0.koepfe]
        assert herkunft.nachweis(um) == b['nw']
    s, info = _satz(basis, basis['t0'].auswahl(np.arange(len(basis['t0']))[::-1]))
    assert info['quelle'] == 'Pilotskript, oberste Ebene' and not info['neu_berechnet'] and info['qualifiziert']
    assert s['bindung'][pilot.FELD_HERKUNFT] == herkunft.sha256(basis['nw'])


KERNE = ('HASWELL', 'SANDYBRIDGE')
SKRIPT_P2 = """
import json, sys
sys.path.insert(0, sys.argv[1])
from pcmms_auswertung import formate, herkunft, pilot
from pcmms_auswertung.generator import kampagne as kp
from pcmms_auswertung.harness import kette
tab = kette.kampagne_erzeugen('N01-V1G0', 'L1', kp.Plan(n0=20, n_pilot=20, n_bloecke=2), 7)[2]
t0 = tab.auswahl(tab.spalte('phase', int) == 0)
print(json.dumps(dict(nachweis=herkunft.sha256(herkunft.nachweis(t0)), datenfelder=pilot.daten_sha256(t0),
                      kennwerte=formate._json_wert(pilot.phase0_kennwerte(t0)))))
"""


@pytest.fixture(scope='module')
def kerne():
    """Die Basiskampagne, in zwei Prozessen mit verschiedenen Rechenkernen von OpenBLAS erzeugt (HASWELL und
    SANDYBRIDGE laufen auf jedem x86-64-Prozessor mit AVX2): Prüfsumme des Nachweises, Prüfsumme der Datenfelder und
    Kennwerte der Phase-0-Läufe je Kern."""
    erg = {}
    for kern in KERNE:
        lauf = subprocess.run([sys.executable, '-c', SKRIPT_P2, CODE], capture_output=True, text=True,
                              env=dict(os.environ, OPENBLAS_CORETYPE=kern, OPENBLAS_NUM_THREADS='1'))
        if lauf.returncode < 0:
            pytest.skip(f'Rechenkern {kern} auf diesem Prozessor nicht ausführbar (Signal {-lauf.returncode})')
        assert lauf.returncode == 0, lauf.stderr[-2000:]
        erg[kern] = json.loads(lauf.stdout.strip().splitlines()[-1])
    return erg


def test_p2_nachweis_gleich_unter_zwei_rechenkernen(basis, kerne):
    """P2: dieselbe Kampagne, mit zwei Rechenkernen erzeugt, ergibt denselben Nachweis wie in diesem Prozess. Die
    Prüfsumme der Datenfelder (Bindung der historischen Profile) unterscheidet sich zwischen diesen Kernen, wo
    OpenBLAS die Vorgabe befolgt (gemessen am 12.11.2026: d1243250… und bc747fdf…); das wird hier nicht verlangt,
    weil eine andere BLAS-Bibliothek die Vorgabe nicht kennt."""
    assert kerne[KERNE[0]]['nachweis'] == kerne[KERNE[1]]['nachweis'] == herkunft.sha256(basis['nw'])


# ── Ergebnisprüfung der Werte (Entscheidung E-4; pilot-0.6, teil_b-0.6) ──────────────────────────────
def _mit_daten(tab, **felder):
    """Kopie der Tabelle mit geänderten Datenfeldern; Köpfe und Metadaten (und damit der Nachweis) bleiben."""
    return zf.LaufTabelle(tab.koepfe, dict(tab.daten, **felder), meta=tab.meta)


def _geaendert(tab, feld, fn):
    a = np.array(tab.daten[feld])
    fn(a)
    return _mit_daten(tab, **{feld: a})


def test_w1_pilotausgabe_und_teil_b_fuehren_die_kennwerte(basis, z):
    """Die Pilotausgabe führt je Satz die Kennwerte der Phase-0-Datenfelder neben der Bindung, nicht in ihr; Teil B
    führt die Kennwerte der übergebenen Läufe in nr1 und das Ergebnis des Vergleichs in nr2.phase0_bindung."""
    for b in (basis, z):
        t0, pe = b['t0'], b['pe']
        kw = pe['phase0_kennwerte']
        assert kw == pilot.phase0_kennwerte(t0) and kw['version'] == kennwerte.VERSION == 'kennwerte-1'
        assert set(kw['felder']) == set(t0.daten) and 'phase0_kennwerte' not in pe['bindung']
        assert not any('kennwert' in str(x).lower() for x in _blaetter(pe['bindung']))
        assert set(kw['felder']['index_fehler']) == {'dtype', 'form', 'n', 'sha256'}            # exaktes Feld
        assert kw['felder']['Nk_zellen']['n'] == 2 * t0.daten['Nk_zellen'].size
        tb = teil_b.erstellen(t0, b['kal'], pe, PROFIL, b['plan'], W8, seed_b0=1, B=50)
        assert tb['nr1']['phase0_kennwerte'] == kw
        pw = tb['nr2']['phase0_bindung']['pilot_werte']
        assert pw == dict(satz='oberste Ebene', gleich=True, kennwerte_gleich=True, auslastung=0.0,
                          feld_auslastung=None, toleranz=kennwerte.toleranz(), version='kennwerte-1')
        assert tb['nr2']['phase0_bindung']['pilot_herkunft'] == 'oberste Ebene'
    # die Zeilenreihenfolge hat keinen Einfluss (kanonische Ordnung wie im Nachweis)
    um = basis['t0'].auswahl(np.arange(len(basis['t0']))[::-1])
    assert pilot.phase0_kennwerte(um) == basis['pe']['phase0_kennwerte']
    assert kennwerte.felder(um.daten) != basis['pe']['phase0_kennwerte']['felder']


W2_FAELLE = {
    'N_mittel aller Läufe um 1 mN größer': ('N_mittel', lambda a: a.__iadd__(1e-3)),
    'Harmonische eines Laufs um 1 ‰ größer': ('Nk_zellen', lambda a: a[3].__imul__(1.001)),
    'Werte zweier Läufe vertauscht': ('Nk_summe', lambda a: a.__setitem__([2, 9], a[[9, 2]])),
    'optionales Feld um 1 ‰ größer': ('fuenftel_zeiger', lambda a: a.__imul__(1.001)),
    'ein Indexfehler mehr': ('index_fehler', lambda a: a[0].__iadd__(1)),
    'Übersteuerung gesetzt': ('uebersteuert_zellen', lambda a: a.__setitem__((0, 0), not a[0, 0])),
    'ein Wert fehlt (NaN)': ('sigma_grad', lambda a: a.__setitem__((5, 1), np.nan)),
    'eine Phase um 10⁻⁶ ° verschoben': ('phi_mittel_grad', lambda a: a.__iadd__(1e-6)),
}


@pytest.mark.parametrize('fall', W2_FAELLE)
def test_w2_geaenderte_werte_bei_gleicher_herkunft_werden_zurueckgewiesen(basis, fall):
    """W2: Die Läufe tragen denselben Nachweis wie in der Pilotausgabe, ihre Werte sind aber verändert. Bis teil_b-0.5
    nahm Teil B solche Läufe an (Grenze der Notiz, Abschnitt 4); die Ergebnisprüfung weist sie zurück und nennt Feld
    und Kennwert."""
    feld, fn = W2_FAELLE[fall]
    geaendert = _geaendert(basis['t0'], feld, fn)
    assert herkunft.nachweis(geaendert) == basis['nw']                  # Herkunft unverändert
    with pytest.raises(ValueError, match=f'{ANDERE_WERTE} \\(Feld {feld}: '):
        _satz(basis, geaendert)
    with pytest.raises(ValueError, match=ANDERE_WERTE):
        teil_b.erstellen(geaendert, basis['kal'], basis['pe'], PROFIL, basis['plan'], W8, seed_b0=1, B=50)


def test_w2_ebene_z_und_bindung_historisch(basis, z):
    """W2 für Läufe mit Rohdatei und für die Bindungsart „historisch“: Auch dort werden geänderte Werte bei gleicher
    Herkunft zurückgewiesen. Unter den historischen Profilen erkennt wie bisher die Prüfsumme der Datenfelder sie."""
    geaendert = _geaendert(z['t0'], 'N_mittel_zellen', lambda a: a.__iadd__(1e-3))
    assert herkunft.nachweis(geaendert) == z['nw']
    _abgelehnt(z, geaendert, ANDERE_WERTE)
    g = _geaendert(basis['t0'], 'N_mittel', lambda a: a.__iadd__(1e-3))
    with pytest.raises(ValueError, match=ANDERE_WERTE):
        teil_b.phase0_satz(g, basis['kal'], basis['pe'], PROFIL, basis['plan'], bindung='historisch')
    alt = pilot.pilot_auswerten(basis['t0'], basis['kal'], HIST, basis['m'].system.f, seed=SEED)
    with pytest.raises(ValueError, match=ANDERE_DATEN):
        _satz(basis, g, alt, HIST)


def test_w3_rundungsrauschen_wird_angenommen(basis):
    """W3: Abweichungen in der Größe des Rundungsrauschens zwischen zwei Rechnern (hier 10⁻¹³ relativ in jedem
    Gleitkommafeld, mehr als das Hundertfache des gemessenen) nimmt die Ergebnisprüfung an und weist sie im Ergebnis
    aus: Kennwerte nicht genau gleich, Auslastung der Toleranz unter 1."""
    t0 = basis['t0']
    rausch = _mit_daten(t0, **{k: v * (1 + 1e-13) for k, v in t0.daten.items() if v.dtype.kind in 'fc'})
    assert pilot.daten_sha256(rausch) != pilot.daten_sha256(t0)         # die alte Prüfsumme hätte angeschlagen
    s, info = _satz(basis, rausch)
    pw = info['pilot_werte']
    assert info['quelle'] == 'Pilotskript, oberste Ebene' and pw['gleich'] and not pw['kennwerte_gleich']
    assert 0 < pw['auslastung'] < 0.01 and pw['feld_auslastung'] in t0.daten
    # dieselbe Änderung tausendfach größer liegt außerhalb der Toleranz
    grob = _mit_daten(t0, **{k: v * (1 + 1e-9) for k, v in t0.daten.items() if v.dtype.kind in 'fc'})
    _abgelehnt(basis, grob, ANDERE_WERTE)


def test_w4_pilotausgabe_ohne_kennwerte_oder_in_anderer_fassung(basis):
    """W4: Eine Pilotausgabe mit Herkunftsnachweis, aber ohne Kennwerte (pilot-0.5) gilt unter teil_b-0.6 nicht als
    prüfbar und wird zurückgewiesen, nicht umgedeutet; ebenso Kennwerte einer anderen Fassung."""
    pe = basis['pe']
    ohne = {k: v for k, v in pe.items() if k != 'phase0_kennwerte'}
    with pytest.raises(ValueError, match='Pilotausgabe ohne Kennwerte der Phase-0-Daten'):
        _satz(basis, basis['t0'], ohne)
    with pytest.raises(ValueError, match='Pilotausgabe ohne Kennwerte der Phase-0-Daten'):
        teil_b.erstellen(basis['t0'], basis['kal'], ohne, PROFIL, basis['plan'], W8, seed_b0=1, B=50)
    fremd = dict(pe, phase0_kennwerte=dict(pe['phase0_kennwerte'], version='kennwerte-0'))
    with pytest.raises(ValueError, match="Fassung 'kennwerte-0' statt 'kennwerte-1'"):
        _satz(basis, basis['t0'], fremd)
    verkuerzt = dict(pe, phase0_kennwerte=dict(pe['phase0_kennwerte'], felder={
        k: v for k, v in pe['phase0_kennwerte']['felder'].items() if k != 't_phi'}))
    with pytest.raises(ValueError, match=f'{ANDERE_WERTE} \\(Feld t_phi: zusätzlich'):
        _satz(basis, basis['t0'], verkuerzt)


def test_w5_historische_profile_ohne_kennwerte(basis):
    """W5: Unter den historischen Profilen bleiben Pilotausgabe (pilot-0.3) und Teil B (teil_b-0.3) ohne Kennwerte und
    ohne Ergebnisprüfung; dort bindet weiter die Prüfsumme der Datenfelder."""
    t0, kal = basis['t0'], basis['kal']
    pe = pilot.pilot_auswerten(t0, kal, HIST, basis['m'].system.f, seed=SEED)
    assert pe['version'] == 'pilot-0.3' and 'phase0_kennwerte' not in pe
    assert pilot.werte_beleg(pe, 'oberste Ebene') is None
    tb = teil_b.erstellen(t0, kal, pe, HIST, basis['plan'], W8, seed_b0=1, B=50)
    assert tb['version'] == 'teil_b-0.3' and 'phase0_kennwerte' not in tb['nr1']
    assert 'pilot_werte' not in tb['nr2']['phase0_bindung']


def test_w6_werte_eines_anderen_rechenkerns_werden_angenommen(basis, kerne):
    """W6: Die Pilotausgabe trägt die Kennwerte derselben Kampagne, gerechnet mit einem anderen Rechenkern von
    OpenBLAS; die Läufe stammen aus diesem Prozess. Teil B nimmt sie an (gleiche Herkunft, Werte innerhalb der
    Toleranz) und weist den Abstand zur Toleranz aus. Gemessen am 13.11.2026 in einem Prozess mit dem Kern SkylakeX:
    Auslastung 2,2·10⁻⁶ gegen HASWELL und gegen SANDYBRIDGE."""
    for kern in KERNE:
        assert kerne[kern]['kennwerte']['version'] == kennwerte.VERSION
        pe = dict(basis['pe'], phase0_kennwerte=kerne[kern]['kennwerte'])
        s, info = _satz(basis, basis['t0'], pe)
        pw = info['pilot_werte']
        assert info['quelle'] == 'Pilotskript, oberste Ebene' and pw['gleich'], (kern, pw['auslastung'])
