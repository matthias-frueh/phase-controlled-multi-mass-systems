"""Etappe 4: AP-12 – Stufe 1 (Rohdaten → Laufzusammenfassung) und Stufe 2 (Zusammenfassungen → Ergebnis) mit
Entscheidungen und Grenzfällen, unabhängigem Abgleich von H1 und Zeltfit (referenz/, gleiche Bootstrap-Indizes) und
dem Vergleichssatz des Kandidatenverfahrens gegen das Vollraster.

Langsame Prüfungen (@slow, PCMMS_SLOW=1): Vergleichssatz mit ≥ 4000 Zeltfits gegen das Vollraster."""
import ast
import os
import time
import warnings

import numpy as np
import pytest

from pcmms_auswertung import (auswertung, bootstrap as bs, formate, h1, konventionen as kv, regeln, stufe1,
                              vorhersage as vh, zeltfit as zfit)
from pcmms_auswertung.generator import ebene_h, ebene_z, kampagne, rauschen, systeme
from pcmms_auswertung.generator.modell import Generatormodell
from pcmms_auswertung.harness import kette
from pcmms_auswertung.referenz import h1_referenz, zeltfit_referenz

CODE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'code', 'pcmms_auswertung')
LANGSAM = os.environ.get('PCMMS_SLOW') == '1'
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    _SLOW = pytest.mark.slow


def slow(f):
    return _SLOW(pytest.mark.skipif(not LANGSAM, reason='langsam; mit PCMMS_SLOW=1 aktivieren')(f))


PROFIL = regeln.profil('ENTW-2026-10').mit_reduktion(bootstrap_B=200, eps_ctrl_datensaetze=300, h3_mc=1000)
PLAN = kampagne.Plan(n0=20, n_pilot=20, n_bloecke=24)


def _kette(sid, stufe='L1', seed=7, **kw):
    return kette.kette(sid, stufe, kw.pop('profil', PROFIL), plan=kw.pop('plan', PLAN), seed=seed, n_min=18, **kw)


# ── Stufe 1 ──────────────────────────────────────────────────────────────────────────────────────────
def _z_laeufe(tmp_path, m, auswahl, seed=3):
    laeufe = kampagne.laufplan(m.plan, np.random.default_rng(2))
    pos = [l['position'] for l in laeufe if (l['konfiguration']['id'], l['phase']) in auswahl]
    kalw = dict(nullpunkt_adc=[1000.0, -2000.0, 500.0], empfindlichkeit_N_je_adc=[1e-6, 1.1e-6, 0.9e-6])
    kal = dict(zellen=[dict(zelle=c + 1, nullpunkt_adc=kalw['nullpunkt_adc'][c], umrechnung='linear',
                            empfindlichkeit_N_je_adc=kalw['empfindlichkeit_N_je_adc'][c]) for c in range(3)])
    zeilen, _ = ebene_z.erzeuge(m, laeufe, np.random.default_rng(seed), str(tmp_path), formate.synth_kennung('T'),
                                kalw, nur=pos)
    return laeufe, zeilen, kal


def test_stufe1_rauschfrei_gleich_ebene_h(tmp_path):
    """Rohdaten (Ebene Z) → Stufe 1 trifft Ebene H mit denselben Ziehungen: Harmonische bis auf den
    Interpolationsfehler von A6, Mittel, Zeiger bis auf die Zeitstempelquantisierung; alle Laufarten gleich."""
    s = systeme.system('A4', m=(0.0867, 0.0880, 0.0867), delta_profil_grad=(0.0, 0.3, 0.0))
    m = Generatormodell(s, rauschen.RAUSCHFREI, kampagne.Plan(n0=1, n_pilot=1, n_bloecke=1, n_zyklen=10))
    laeufe, zeilen, kal = _z_laeufe(tmp_path, m, {('S112', 1), ('L2', 0), ('R', 0), ('P110_250', 0)})
    tab = ebene_h.erzeuge(m, laeufe, np.random.default_rng(4))
    arten = set()
    for z in zeilen:
        lz = stufe1.laufzusammenfassung(os.path.join(str(tmp_path), z['lauf_id']), kal, k_voll=60)
        i = z['position']
        arten.add(lz.kopf['laufart'])
        assert lz.kopf['n_zyklen'] == 10 and lz.kopf['ebene'] == 'Z' and not lz.kopf['fehlende_kanaele']
        assert np.abs(lz.daten['Nk_zellen'][:, :12] - tab.daten['Nk_zellen'][i, :, :12]).max() < 3e-5
        assert np.abs(lz.daten['N_mittel_zellen'] - tab.daten['N_mittel_zellen'][i]).max() < 2e-6
        zh = tab.daten['zeiger'][i, :, :12]
        ok = np.isfinite(zh)
        assert np.array_equal(ok, np.isfinite(lz.daten['zeiger'][:, :12]))
        if ok.any():                                                    # Referenzlauf: keine Zeiger
            assert np.abs(lz.daten['zeiger'][:, :12][ok] - zh[ok]).max() < 1e-2      # 1 µs Quantisierung
        assert np.allclose(lz.daten['min_roh_zellen'], tab.daten['min_roh_zellen'][i], atol=2e-4)
    assert arten == {'R', 'L', 'K'}


def test_stufe1_regeln_aus_rohkanal(tmp_path):
    """Sättigung einer Zelle und ein fehlender Indeximpuls erscheinen in der Zusammenfassung (G5, G2), ohne dass
    die Summe auffällt; ein fehlender Kanal wird gemeldet, nicht ergänzt."""
    from pcmms_auswertung.generator import szenarien
    m = szenarien.modell('S06-saettigung', 'L1', plan=kampagne.Plan(n0=3, n_pilot=1, n_bloecke=1, n_zyklen=20))
    laeufe, zeilen, kal = _z_laeufe(tmp_path, m, {('S120', 1), ('L1', 0)})
    lz = [stufe1.laufzusammenfassung(os.path.join(str(tmp_path), z['lauf_id']), kal) for z in zeilen]
    ue = {x.kopf['konfiguration']['id']: x.daten['uebersteuert_zellen'].tolist() for x in lz}
    assert ue['S120'] == [False, False, True] and [False, False, True] in [ue['L1']] or ue['L1'][2]
    m2 = szenarien.modell('S-indexfehler', 'L1', plan=kampagne.Plan(n0=1, n_pilot=1, n_bloecke=1, n_zyklen=20))
    laeufe2, zeilen2, kal2 = _z_laeufe(tmp_path / 'b', m2, {('S110', 1)})
    lz2 = stufe1.laufzusammenfassung(os.path.join(str(tmp_path / 'b'), zeilen2[0]['lauf_id']), kal2)
    assert lz2.daten['index_fehler'][1] >= 1 and lz2.kopf['n_zyklen'] < 20
    # fehlender Kanal
    p = os.path.join(str(tmp_path / 'b'), zeilen2[0]['lauf_id'])
    k, inhalt, daten = formate.lies(p, 'rohlauf')
    daten = {x: v for x, v in daten.items() if x != 'temperatur_zellen'}
    formate.schreibe(str(tmp_path / 'c' / 'lauf'), formate.kopf('rohlauf', formate.synth_kennung('T')), daten, inhalt)
    lz3 = stufe1.laufzusammenfassung(str(tmp_path / 'c' / 'lauf'), kal2)
    assert 'temperatur_zellen' in lz3.kopf['fehlende_kanaele'] and np.isnan(lz3.daten['temperatur_min_zellen']).all()


# ── Stufe 2: Entscheidungen ──────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope='module')
def exakt():
    return _kette('N01-A4')


def test_exakt_bestaetigt_und_herkunft(exakt):
    e = exakt['ergebnis']
    assert e['H1']['ausgang'] == 'bestätigt' and e['H1Z']['ausgang'] == 'bestätigt'
    assert e['H2']['ausgang'] == 'bestätigt' and e['H4']['ausgang'] == 'bestätigt'
    assert e['H1']['abweichung_nachgewiesen'] is False
    hk = e['herkunft']
    assert hk['reduziert'] and '+red(' in hk['profil']['profil_id'] and hk['B'] == 200
    assert 'TESTVORGABE' in e['H1']['c_herkunft']
    # A4 ist starr: H3 nicht entscheidbar mit Grund (P0.4 nicht identifizierbar), kein Platzhalterausgang
    assert e['H3']['ausgang'] == 'nicht entscheidbar' and e['H3']['grund'] == 'Verfahren'
    assert e['H0']['vermerk'].startswith('Einzellauftoleranz') and 'Gleichheit nachgewiesen' not in e['H0']['aussage']


def test_ergebnis_reproduzierbar_und_seedabhaengig(exakt):
    tab, kal, tb = exakt['tabelle'], exakt['kalibrierung'], exakt['teil_b']
    a = auswertung.auswerten(tab, kal, tb, PROFIL)
    b = auswertung.auswerten(tab, kal, tb, PROFIL)
    c = auswertung.auswerten(tab, kal, tb, PROFIL, seed=12345)
    ha = formate.sha256_json({k: a[k] for k in ('H1', 'H1Z', 'H2', 'H3', 'H4', 'H0', 'E3')})
    hb = formate.sha256_json({k: b[k] for k in ('H1', 'H1Z', 'H2', 'H3', 'H4', 'H0', 'E3')})
    hc = formate.sha256_json({k: c[k] for k in ('H1', 'H1Z', 'H2', 'H3', 'H4', 'H0', 'E3')})
    assert ha == hb and ha != hc
    assert c['H1']['ausgang'] == a['H1']['ausgang']


@pytest.mark.parametrize('sid,erwartet', [('A04-R4', 'falsifiziert'), ('A04-R1', 'bestätigt')])
def test_kopplung_unter_und_ueber_der_grenze(sid, erwartet):
    e = _kette(sid)['ergebnis']
    assert e['H1']['ausgang'] == erwartet
    assert e['H1']['abweichung_nachgewiesen'] is True                  # L1: Abweichung nachgewiesen
    if erwartet == 'bestätigt':
        assert e['H1']['zusaetze'][0] == 'Abweichung nachgewiesen, innerhalb der Äquivalenzgrenze'
        assert e['H1_sensitivitaet']['faktor_0_1']['ausgang'] == 'falsifiziert'   # Sensitivität getrennt berichtet


def test_kopplung_an_der_grenze_nicht_bestaetigt():
    e = _kette('A04-R2', 'L0')['ergebnis']
    assert e['H1']['ausgang'] != 'bestätigt'


def test_yhat1_ungueltig_und_fehlende_punkte():
    e = _kette('S02-kontrolllauf')['ergebnis']
    assert not e['yhat1_gueltig'] and e['H1']['grund'] == 'Datenlage' and e['H2']['grund'] == 'Datenlage'
    assert e['gueltigkeit']['abbruch']['S2']
    e = _kette('H-fehlend')['ergebnis']
    assert not e['konfigurationen']['S118']['auswertbar'] and e['H1']['grund'] == 'Datenlage'
    assert e['H2']['ausgang'] == 'nicht entscheidbar' and e['H2']['grund'] == 'Datenlage'


def test_drift_zusatz_und_getrennte_vorhersagen():
    e = _kette('E07-verstaerkung')['ergebnis']
    assert e['H1']['ausgang'] == 'bestätigt' and e['H1']['drift'] is True
    assert any('Drift' in z for z in e['H1']['zusaetze'])
    T0, T1 = e['H1']['tests0'], e['H1']['tests1']
    assert np.nanmax(np.abs(T0['z'])) > 10 and np.nanmax(np.abs(T1['z'])) < e['H1']['c']


def test_fehlende_teil_b_werte_und_offene_regeln(exakt):
    tab, kal, tb = exakt['tabelle'], exakt['kalibrierung'], dict(exakt['teil_b'])
    tb2 = dict(tb, nr10=dict(tb['nr10'], c_H1=None, h2_intervall=None))
    e = auswertung.auswerten(tab, kal, tb2, PROFIL)
    assert e['H1']['ausgang'] == 'bestätigt' and e['H1']['abweichung_nachgewiesen'] is None
    assert any('c fehlt' in g['text'] for g in e['H1']['gruende'])
    assert e['H2']['ausgang'] == 'nicht entscheidbar' and e['H2']['grund'] == 'Verfahren'
    tb3 = dict(tb, nr4=dict(tb['nr4'], bias0=None))
    e = auswertung.auswerten(tab, kal, tb3, PROFIL)
    assert e['H1']['ausgang'] == 'nicht entscheidbar' and e['H1']['grund'] == 'Verfahren'
    # Profil AF-2026-10: offene Regeln (δ_H2, Grenzen H1Z, H3) → nicht entscheidbar mit Regelgrund
    af = regeln.profil('AF-2026-10').mit_reduktion(bootstrap_B=200, h3_mc=1000)
    e = auswertung.auswerten(tab, kal, tb, af)
    assert e['H2']['ausgang'] == 'nicht entscheidbar' and any('Regel offen' in g['text'] for g in e['H2']['gruende'])
    assert e['H1']['ausgang'] == 'bestätigt'                           # H1 hängt an keiner offenen Regel
    assert e['E3'].get('bewertung') is None and 'nur beschreibend' in e['E3']['status']


@pytest.mark.parametrize('sid,ausgang,abw', [('N01-A4', 'bestätigt', False), ('A04-R1', 'bestätigt', True),
                                               ('A04-R4', 'falsifiziert', True)])
def test_rauschfreier_grenzfall(sid, ausgang, abw):
    """u = 0 (rauschfreie Kampagne, auch Phase 0): Regel h1.grenzfall – exakte Superposition bestätigt, Abweichungen
    unter der Grenze bestätigt mit nachgewiesener Abweichung, über der Grenze falsifiziert; H2-Intervall entartet."""
    r = _kette(sid, 'L0', rausch=rauschen.RAUSCHFREI)
    e = r['ergebnis']
    assert e['H1']['ausgang'] == ausgang and e['H1']['abweichung_nachgewiesen'] is abw
    assert np.nanmax(e['H1']['tests0']['u']) == 0.0
    if sid == 'N01-A4':
        assert e['H2']['ausgang'] == 'bestätigt'
        assert e['H2']['intervalle']['perzentil_0.95']['yhat0'] == [0.0, 0.0]


def test_n3_bindet_unter_fassung_b():
    e = _kette('N03-N3bindet')['ergebnis']
    T0 = e['H1']['tests0']
    D = np.asarray(e['H1']['Delta'])
    bindung = np.nanmax(T0['teq'] * T0['u'], 0) / D                    # je Größe: größter Anteil von Δ_q
    assert np.argmax(bindung) in (5, 6)                                 # Re/Im N₃


def test_h3_falsche_kette_nicht_verdeckt():
    """C03: 5 % Fehler des Brückensimulators bleibt in H3 sichtbar (Abweichung nachgewiesen); H1, H2 unberührt; P0.1
    meldet den Widerspruch zur Statik. C04 ohne Fehler: H3 bestätigt ohne nachgewiesene Abweichung."""
    r = _kette('C03-GF5')
    e = r['ergebnis']
    assert all(b['statik_widerspruch'] for b in r['kalibrierung']['p0_1']['bruecke'])
    assert e['H3']['zusaetze'] and e['H1']['ausgang'] == 'bestätigt'
    rel = [abs(t['r'] / t['vorhersage']) for t in e['H3']['tests'] if t['k'] == 1 and abs(t['vorhersage']) > 1e-3]
    assert np.median(rel) == pytest.approx(0.05 / 1.05, abs=0.01)
    assert 'Masse, Profil und Kalibrierung' in e['H3']['kennzeichnung']
    e4 = _kette('C04-steif')['ergebnis']
    assert e4['H3']['ausgang'] == 'bestätigt' and not e4['H3']['zusaetze']


def test_zuordnung_kopplung_klasse_p1():
    e = _kette('I01-amplitude')['ergebnis']
    assert e['zuordnung']['ausgeloest'] and e['zuordnung']['klasse'] == 1
    chi = e['zuordnung']['werte']['yhat0']['chi2']
    assert chi[1] < e['zuordnung']['quantil95'] < min(chi[0], chi[2])


@pytest.mark.parametrize('datei', ['auswertung.py', 'stufe1.py', 'h1.py', 'h2.py', 'h3.py', 'h4.py', 'zeltfit.py',
                                   'bootstrap.py', 'vorhersage.py', 'kontrollen.py', 'teil_b.py', 'bericht.py'])
def test_ap12_importiert_weder_generator_noch_harness(datei):
    baum = ast.parse(open(os.path.join(CODE, datei), encoding='utf-8').read())
    namen = set()
    for n in ast.walk(baum):
        if isinstance(n, ast.ImportFrom):
            namen.add(n.module or '')
            namen.update(a.name for a in n.names)
        elif isinstance(n, ast.Import):
            namen.update(a.name for a in n.names)
    assert not any(x in ('generator', 'harness', 'wahrheit', 'referenz') or 'generator' in x or 'harness' in x
                   for x in namen)


# ── unabhängiger Abgleich mit referenz/ ──────────────────────────────────────────────────────────────
def _referenz_eingabe(r, B, seed):
    """Gültige Läufe aus dem Ergebnis, dieselben Indexmatrizen für Produktion und Referenz."""
    e, tb, tab = r['ergebnis'], r['teil_b'], r['tabelle']
    t1 = tab.auswahl(tab.spalte('phase', int) == 1).sortiert()
    ungueltig = set(e['gueltigkeit']['gruende'])
    schnitt = [c['id'] for c in tb['nr2']['konfigurationen'] if c['gruppe'] == 'schnitt']
    sel = lambda pr: sorted([i for i, k in enumerate(t1.koepfe) if pr(k) and k['lauf_id'] not in ungueltig],
                            key=lambda i: t1.koepfe[i]['position'])
    lauf = {kid: sel(lambda k, kid=kid: k['laufart'] == 'K' and k['konfiguration']['id'] == kid) for kid in schnitt}
    ctr = [sel(lambda k, j=j: k['laufart'] == 'L' and k['modul'] == j and k['einstellung'] == 1) for j in (1, 2, 3)]
    rng = np.random.default_rng(seed)
    idx = {f'A/{k}': rng.integers(0, len(v), size=(B, len(v))) for k, v in lauf.items()}
    idx.update({f'B1/modul{j + 1}': rng.integers(0, len(ctr[j]), size=(B, len(ctr[j]))) for j in range(3)})
    E0 = [np.asarray(x['Nk_zellen']).sum(1) for x in tb['nr3']['einzel0']]
    d = t1.daten
    ein = dict(kmax=tb['nr2']['k_max'], punkte=schnitt,
               laeufe={k: dict(Nk=d['Nk_summe'][v], zeiger=d['zeiger'][v], nz=np.array(
                   [t1.koepfe[i]['n_zyklen'] for i in v])) for k, v in lauf.items()},
               einzel0=E0, einzel1=[d['Nk_summe'][c] for c in ctr], bias0=np.asarray(tb['nr4']['bias0']),
               bias1=np.asarray(tb['nr4']['bias1']), u_bias0=np.asarray(tb['nr4']['u_bias0']),
               u_bias1=np.asarray(tb['nr4']['u_bias1']), Delta=np.asarray(tb['nr4']['Delta']),
               Delta_rel=np.asarray(tb['nr4']['Delta_rel']), c=tb['nr10']['c_H1'],
               indizes={**idx, **{k: np.asarray(v)[:B] for k, v in tb['nr3']['indizes'].items() if k.startswith('B0/')}})
    return ein, idx


@pytest.mark.parametrize('sid,stufe', [('N01-A4', 'L2'), ('A04-R2', 'L1'), ('A04-R4', 'L1')])
def test_h1_gleich_referenz_mit_denselben_indizes(sid, stufe):
    """Produktion (h1, bootstrap, vorhersage) gegen referenz/h1_referenz aus dem Regeltext: Toleranzen nach Plan
    2.6 e (Kräfte, Residuen 10⁻⁹ N + 10⁻⁹·|Wert|; u 10⁻¹² N + 10⁻⁹·u; z 10⁻⁷ + 10⁻⁹·|z|; ν relativ 10⁻⁹)."""
    r = _kette(sid, stufe)
    B = 150
    ein, idx = _referenz_eingabe(r, B, seed=99)
    e = auswertung.auswerten(r['tabelle'], r['kalibrierung'], r['teil_b'], PROFIL, bootstrap_indizes=idx)
    ref = h1_referenz.h1_referenz(ein)
    for p, T in (('0', e['H1']['tests0']), ('1', e['H1']['tests1'])):
        np.testing.assert_allclose(T['r'], ref['r' + p], rtol=1e-9, atol=1e-9)
        np.testing.assert_allclose(T['u'], ref['u' + p], rtol=1e-9, atol=1e-12)
        np.testing.assert_allclose(T['z'], ref['z' + p], rtol=1e-9, atol=1e-7)
        np.testing.assert_allclose(T['nu'], ref['nu' + p], rtol=1e-9)
    assert np.array_equal(e['H1']['tost0'], ref['tost0']) and np.array_equal(e['H1']['tost1'], ref['tost1'])
    assert np.array_equal(e['H1']['relevant'], ref['relevant'])
    assert e['H1']['ausgang'].replace('ä', 'ae') == ref['ausgang']        # Referenz schreibt „bestaetigt“
    assert e['H1']['abweichung_nachgewiesen'] == ref['abweichung_nachgewiesen'] and e['H1']['drift'] == ref['drift']


def _testsatz(rng, n_fits):
    """Vergleichssatz: asymmetrisches und symmetrisches Zelt, verrauschte Kurven, reines Rauschen, Gerade; Fenster 6°,
    8° und 20° (7, 9, 21 Punkte), Abszissen mit Messrauschen."""
    faelle = []
    arten = ('asymmetrisch', 'symmetrisch', 'verrauscht', 'rauschen', 'gerade')
    for i in range(n_fits):
        art = arten[i % 5]
        n = (7, 9, 21)[(i // 5) % 3]
        phi = 120 - (n - 1) + 2 * np.arange(n) + 0.01 * rng.standard_normal(n)
        spitze = 120 + rng.uniform(-1.5, 1.5)
        if art == 'asymmetrisch':
            F = np.where(phi <= spitze, 0.044 * (phi - spitze), -0.031 * (phi - spitze))
        elif art == 'symmetrisch':
            F = -0.04 * np.abs(phi - spitze)
        elif art == 'verrauscht':
            F = -0.04 * np.abs(phi - spitze) + 0.004 * rng.standard_normal(n)
        elif art == 'rauschen':
            F = 0.01 * rng.standard_normal(n)
        else:
            F = 0.3 + 0.01 * phi
        faelle.append((art, phi, F))
    return faelle


def _vergleich(n_fits, seed=5):
    rng = np.random.default_rng(seed)
    faelle = _testsatz(rng, n_fits)
    gleich = gleichstand = 0
    abweichung = []
    t_k = t_v = 0.0
    for art, phi, F in faelle:
        t = time.perf_counter()
        k = zfit.zeltfit(phi[None], F[None])
        t_k += time.perf_counter() - t
        t = time.perf_counter()
        v = zeltfit_referenz.zeltfit_vollraster(phi, F)
        t_v += time.perf_counter() - t
        if abs(k['phi_stern'][0] - v['phi_stern']) < 1e-9:
            gleich += 1
            continue
        rk, rv = zfit.rss_exakt(phi, F, k['phi_stern'][0]), zfit.rss_exakt(phi, F, v['phi_stern'])
        sst = float(((F - F.mean()) ** 2).sum())
        tol = 1e-9 * max(rk, rv) + 1e-12 * sst + 1e-28 * F.size * float((F ** 2).max())
        if abs(rk - rv) <= tol:
            gleichstand += 1
        else:
            abweichung.append((art, phi.size, k['phi_stern'][0], v['phi_stern'], rk, rv))
    return dict(n=n_fits, gleich=gleich, gleichstand=gleichstand, abweichung=abweichung, t_kandidat=t_k,
                t_vollraster=t_v)


def test_zeltfit_kandidat_gleich_vollraster_klein():
    r = _vergleich(150)
    assert not r['abweichung'], r['abweichung'][:3]
    assert r['gleich'] + r['gleichstand'] == 150


@slow
def test_zeltfit_kandidat_gleich_vollraster_4000():
    r = _vergleich(4000)
    print(f"\nZeltfit-Vergleichssatz: {r['n']} Fits, gleich {r['gleich']}, Gleichstand {r['gleichstand']}, "
          f"abweichend {len(r['abweichung'])}; Kandidat {r['t_kandidat']:.2f} s, Vollraster {r['t_vollraster']:.1f} s")
    assert not r['abweichung'] and r['n'] >= 4000


def test_zeltfit_grenzfaelle():
    phi = np.array([114.0, 116.0, 118.0, 120.0, 122.0, 124.0, 126.0])
    # Gerade: Gleichstand über das ganze Raster → kleinstes φ*
    r = zfit.zeltfit(phi[None], (0.3 + 0.01 * phi)[None])
    assert r['phi_stern'][0] == pytest.approx(114.0)
    # exaktes Zelt mit Spitze auf einem Rasterpunkt
    F = np.where(phi <= 120.5, 0.04 * (phi - 120.5), -0.03 * (phi - 120.5))
    assert zfit.zeltfit(phi[None], F[None])['phi_stern'][0] == pytest.approx(120.5, abs=1e-9)
    # symmetrisches Zelt mit Spitze auf einer Abszisse
    assert zfit.zeltfit(phi[None], (-0.04 * np.abs(phi - 120.0))[None])['phi_stern'][0] == pytest.approx(120.0)
