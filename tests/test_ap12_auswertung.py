"""Etappe 4: AP-12 – Stufe 1 (Rohdaten → Laufzusammenfassung) und Stufe 2 (Zusammenfassungen → Ergebnis) mit
Entscheidungen und Grenzfällen, unabhängigem Abgleich von H1 und Zeltfit (referenz/, gleiche Bootstrap-Indizes) und
dem Vergleichssatz des Kandidatenverfahrens gegen das Vollraster.

Langsame Prüfungen (@slow, PCMMS_SLOW=1): Vergleichssatz mit ≥ 4000 Zeltfits gegen das Vollraster."""
import ast
import os
import warnings

import numpy as np
import pytest

from pcmms_auswertung import auswertung, formate, regeln, stufe1, zeltfit as zfit
from pcmms_auswertung.generator import ebene_h, ebene_z, kampagne, rauschen, systeme
from pcmms_auswertung.generator.modell import Generatormodell
from pcmms_auswertung.harness import abgleich, kette

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


# ── Stufe 1: Zeitmittel ⟨N⟩ aus den ursprünglichen Zeiten (Korrektur B) ───────────────────────────────
KAL_EINS = dict(zellen=[dict(zelle=c + 1, nullpunkt_adc=0.0, umrechnung='linear', empfindlichkeit_N_je_adc=1e-6)
                        for c in range(3)])


def _rohlauf_perioden(verz, perioden, kraft, f_s, t0=0.0, ts=0.1, auslassen=(), name='V'):
    """Einzelmodullauf L1 mit vorgegebenen Periodendauern ab dem Fensterbeginn ts (Indeximpulse von Modul 1 auf dem
    1-µs-Raster) und Zellkräften kraft(t, c) → (3, n) [N]; c: Zyklusnummer je Abtastwert (−1 vor dem Fenster).
    auslassen: Nummern fehlender Impulse. Rückgabe Pfad, Zeiten, Rohwerte in N (wie Stufe 1 sie sieht), Impulse."""
    from pcmms_auswertung import rohdaten
    impulse = rohdaten.index_quantisiert(ts + np.r_[0.0, np.cumsum(perioden)], 1e6)
    t = t0 + np.arange(int(np.floor((impulse[-1] + 0.05 - t0) * f_s))) / f_s
    F = np.asarray(kraft(t, np.searchsorted(impulse, t, side='right') - 1), float)
    adc = np.rint(F / 1e-6).astype(np.int64)
    inhalt = dict(lauf=dict(lauf_id=name, laufart='L', modul=1, einstellung=1,
                            konfiguration=dict(id='L1', gruppe='einzel', phi_soll_grad=None), phase=1, block=1,
                            messtag=1, position=0, kontrollsatz=None, t_start=0.0, t_ende=float(t[-1])),
                  erfassung=dict(f_soll=10.0, f_s=f_s, t0=t0, adc=dict(bits=24, vollausschlag=2 ** 23 - 1),
                                 f_takt=1e6, kanaele=[]),
                  protokoll=dict(t_rampe_ende=ts / 2, t_e=ts / 2, n_zyklen_fenster=len(perioden), stoerung=False,
                                 aufzeichnung_ok=True, park_ok=True, bediener='synthetisch', notizen=''),
                  umgebung={}, einstellungen={}, generator=dict(programm='test', szenario=None, seed=None))
    daten = dict(kraft_adc=adc, index_modul1=np.delete(impulse, list(auslassen)), index_modul2=np.zeros(0),
                 index_modul3=np.zeros(0), temperatur_zellen=np.full((3, 2), 21.0),
                 t_temperatur=np.array([0.0, float(t[-1])]), uebersteuerung=np.zeros(3, bool))
    os.makedirs(verz, exist_ok=True)
    rohdaten.schreibe_rohlauf(verz, inhalt, daten, formate.synth_kennung('ZEITMITTEL'))
    return os.path.join(verz, name), t, adc * 1e-6, impulse


def _integral_referenz(t, F, a, b):
    """Unabhängige Referenz: Trapez über die Stützstellen in (a, b) und die interpolierten Randwerte (exakt für den
    linear interpolierten Verlauf, der auch dem Resampling zugrunde liegt)."""
    x = np.r_[a, t[(t > a) & (t < b)], b]
    return np.array([np.trapezoid(np.interp(x, t, F[c]), x) for c in range(F.shape[0])])


def _zeitmittel_referenz(t, F, intervalle):
    I = sum(_integral_referenz(t, F, a, b) for a, b in intervalle)
    return I / sum(b - a for a, b in intervalle)


def _phasenmittelkurve(t, F, intervalle):
    th = np.arange(2000) / 2000
    return np.mean([[np.interp(a + th * (b - a), t, F[c]) for c in range(3)] for a, b in intervalle], axis=0)


def test_stufe1_zeitmittel_bei_ungleichen_perioden(tmp_path):
    """Zehn Perioden abwechselnd 99 und 101 ms, Zelle 1 im kürzeren Zyklus 1 N, im längeren 3 N, Zellen 2 und 3 je
    1 N: analytisches Zeitmittel der Summe 4,010 N, Phasenmittel 4,000 N. Toleranz zum analytischen Wert: je
    Kraftsprung höchstens |ΔF|·Δt/2 durch die lineare Interpolation (10 Sprünge · 2 N · 10 µs/2 über 1 s = 1·10⁻⁴ N);
    gegen die unabhängige Integration des interpolierten Verlaufs 10⁻⁹ N. Mittelkurve und Harmonische unverändert."""
    per = np.tile([0.099, 0.101], 5)
    pfad, t, F, g = _rohlauf_perioden(str(tmp_path), per, lambda t, c: np.stack(
        [np.where((c >= 0) & (c < 10) & (c % 2 == 1), 3.0, 1.0), np.ones_like(t), np.ones_like(t)]), f_s=1e5)
    lz = stufe1.laufzusammenfassung(pfad, KAL_EINS, k_voll=12)
    iv = list(zip(g[:-1], g[1:]))
    assert lz.kopf['n_zyklen'] == 10
    assert lz.daten['N_mittel'] == pytest.approx(4.010, abs=1.0e-4)
    assert np.abs(lz.daten['N_mittel_zellen'] - _zeitmittel_referenz(t, F, iv)).max() < 1e-9
    assert lz.daten['N_mittel'] == pytest.approx(lz.daten['N_mittel_zellen'].sum(), abs=1e-12)
    kurve = _phasenmittelkurve(t, F, iv)
    assert kurve.mean(-1).sum() == pytest.approx(4.000, abs=1.0e-4)          # Phasenmittel bleibt eine andere Größe
    from pcmms_auswertung import konventionen as kv
    assert np.abs(lz.daten['Nk_zellen'] - kv.harmonische(kurve, 12)).max() < 1e-12
    assert np.abs(lz.daten['Nk_summe'] - lz.daten['Nk_zellen'].sum(0)).max() < 1e-12
    assert lz.kopf['version_stufe1'] == stufe1.VERSION and stufe1.VERSION != 'stufe1-0.1'


def test_stufe1_zeitmittel_grenzen_zwischen_abtastwerten_und_ausgelassener_zyklus(tmp_path):
    """Zyklusgrenzen zwischen Abtastwerten (f_s inkommensurabel, versetztes t₀) und ein fehlender Indeximpuls: die
    beiden betroffenen Zyklen gehen weder in Zähler noch Nenner ein (in ihnen läge Zelle 2 um 5 N höher)."""
    rng = np.random.default_rng(11)
    per = 0.1 + 0.003 * rng.uniform(-1, 1, 12)

    def kraft(t, c):
        luecke = np.where((c == 4) | (c == 5), 5.0, 0.0)
        return np.stack([1.0 + 0.3 * z + 0.2 * np.sin(2 * np.pi * 10 * t + z) + 0.05 * t + (luecke if z == 1 else 0)
                         for z in range(3)])
    pfad, t, F, g = _rohlauf_perioden(str(tmp_path), per, kraft, f_s=33333.0, t0=7.3e-6, auslassen=(5,))
    lz = stufe1.laufzusammenfassung(pfad, KAL_EINS, k_voll=12)
    iv = [(g[c], g[c + 1]) for c in range(12) if c not in (4, 5)]
    assert lz.kopf['n_zyklen'] == 10 and lz.daten['index_fehler'][0] == 1
    lage = (g - 7.3e-6) * 33333.0
    assert (np.abs(lage - np.round(lage)) > 1e-3).all()                       # Grenzen liegen zwischen Abtastwerten
    assert np.abs(lz.daten['N_mittel_zellen'] - _zeitmittel_referenz(t, F, iv)).max() < 1e-9
    assert lz.daten['N_mittel_zellen'][1] < 1.4                                # Lücke (≈ 6,3 N) nicht enthalten


def test_stufe1_zeitmittel_der_fuenftel(tmp_path):
    """Erstes und letztes Fünftel (⌊10/5⌋ = 2 Zyklen nach der bisherigen Auswahl) mit verschiedenen Perioden und
    Kräften: Zeitmittel je Fünftel 4,010 N und 5,575 N (Phasenmittel 4,0 und 5,5 N)."""
    per = np.array([0.099, 0.101, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.095, 0.105])
    f1 = np.array([1.0, 3.0, 2, 2, 2, 2, 2, 2, 2.0, 5.0])
    pfad, t, F, g = _rohlauf_perioden(str(tmp_path), per, lambda t, c: np.stack(
        [np.where((c >= 0) & (c < 10), f1[np.clip(c, 0, 9)], 2.0), np.ones_like(t), np.ones_like(t)]), f_s=1e5)
    lz = stufe1.laufzusammenfassung(pfad, KAL_EINS, k_voll=12)
    iv = list(zip(g[:-1], g[1:]))
    ref = [_zeitmittel_referenz(t, F, iv[:2]).sum(), _zeitmittel_referenz(t, F, iv[-2:]).sum()]
    assert np.abs(lz.daten['fuenftel_N_mittel'] - ref).max() < 1e-9
    assert lz.daten['fuenftel_N_mittel'] == pytest.approx([4.010, 5.575], abs=3e-4)  # 3 Sprünge · 3 N · 5 µs / 0,2 s


def test_stufe1_zeitmittel_gleich_phasenmittel_bei_gleichen_perioden(tmp_path):
    """Standardfall gleicher Perioden mit Grenzen auf Abtastwerten: Zeitmittel = bisheriges Phasenmittel innerhalb der
    numerischen Genauigkeit; Harmonische und Zellensumme gesondert geprüft."""
    per = np.full(10, 0.1)

    def kraft(t, c):
        return np.stack([1.0 + 0.3 * z + 0.4 * np.cos(2 * np.pi * 10 * (t - 0.1) + z) + 0.1 * np.sin(
            4 * np.pi * 10 * (t - 0.1)) for z in range(3)])
    pfad, t, F, g = _rohlauf_perioden(str(tmp_path), per, kraft, f_s=1e4)
    lz = stufe1.laufzusammenfassung(pfad, KAL_EINS, k_voll=12)
    iv = list(zip(g[:-1], g[1:]))
    kurve = _phasenmittelkurve(t, F, iv)
    assert np.abs(lz.daten['N_mittel_zellen'] - kurve.mean(-1)).max() < 1e-9
    assert np.abs(lz.daten['N_mittel_zellen'] - _zeitmittel_referenz(t, F, iv)).max() < 1e-9
    from pcmms_auswertung import konventionen as kv
    assert np.abs(lz.daten['Nk_zellen'] - kv.harmonische(kurve, 12)).max() < 1e-12
    assert np.abs(lz.daten['Nk_summe'] - lz.daten['Nk_zellen'].sum(0)).max() < 1e-12
    assert lz.daten['N_mittel'] == pytest.approx(lz.daten['N_mittel_zellen'].sum(), abs=1e-12)


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


def test_verarbeitungsstand_alte_bedeutung_des_zeitmittels_gemeldet(exakt):
    """Korrektur B: Laufzusammenfassungen von stufe1-0.1 (⟨N⟩ als Phasenmittel) gelten in Stufe 2 nicht
    stillschweigend als neu berechnet; Teil B und Ergebnis nennen den Verarbeitungsstand."""
    from pcmms_auswertung import zusammenfassung as zf
    vb = exakt['ergebnis']['herkunft']['verarbeitung']
    assert vb['alte_bedeutung'] == [] and 'ebene_h-0.1' in vb['versionen']
    assert exakt['teil_b']['nr1']['phase0_verarbeitung']['alte_bedeutung'] == []
    tab = exakt['tabelle']
    alt = zf.LaufTabelle([dict(k, version_stufe1='stufe1-0.1') if k['phase'] == 1 else k for k in tab.koepfe],
                         tab.daten, meta=tab.meta)
    erg = auswertung.auswerten(alt, exakt['kalibrierung'], exakt['teil_b'], PROFIL)
    assert erg['herkunft']['verarbeitung']['alte_bedeutung'] == ['stufe1-0.1']
    assert 'Phasenmittel' in erg['herkunft']['verarbeitung']['mittel_bedeutung']['stufe1-0.1']
    assert 'alter Bedeutung' in erg['text']


def test_e3_ohne_unsicherheit_von_T_nur_numerisch(exakt):
    """Korrektur E: Teil B mit Unsicherheitsbeschreibung von T → E3 mit T-Ziehungen (eigener Strom E3/T); ein Teil B
    ohne Beschreibung (älterer Stand) gilt nicht als „Unsicherheit null“: nur numerische Diagnostik."""
    e = exakt['ergebnis']['E3']
    nr5 = exakt['teil_b']['nr5']
    assert nr5['unsicherheit']['format'] == 'e3_T_unsicherheit-0.1' and nr5['unsicherheit']['herkunft']['quelle']
    assert e['t_unsicherheit']['gezogen'] and e['t_unsicherheit']['anteil_ungueltig'] == 0.0
    assert e.get('bewertung') in ('auffällig', 'unauffällig', 'unbestimmt')
    tb = dict(exakt['teil_b'], nr5={k: v for k, v in nr5.items() if k != 'unsicherheit'})
    alt = auswertung.auswerten(exakt['tabelle'], exakt['kalibrierung'], tb, PROFIL)['E3']
    assert alt['bewertung'] is None and alt['status'].startswith('nur numerisch') and not alt['t_unsicherheit']['gezogen']
    assert [x['e3a']['modul2']['delta_phi_Z_grad'] for x in alt['e3a']] == \
        [x['e3a']['modul2']['delta_phi_Z_grad'] for x in e['e3a']]


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
@pytest.mark.parametrize('sid,stufe', [('N01-A4', 'L2'), ('A04-R2', 'L1'), ('A04-R4', 'L1')])
def test_h1_gleich_referenz_mit_denselben_indizes(sid, stufe):
    """Produktion (h1, bootstrap, vorhersage) gegen referenz/h1_referenz aus dem Regeltext: Toleranzen nach Plan
    2.6 e (Kräfte, Residuen 10⁻⁹ N + 10⁻⁹·|Wert|; u 10⁻¹² N + 10⁻⁹·u; z 10⁻⁷ + 10⁻⁹·|z|; ν relativ 10⁻⁹)."""
    r = _kette(sid, stufe)
    a = abgleich.h1_abgleich(r, PROFIL, B=150, seed=99)
    assert all(v['innerhalb'] for v in a['werte'].values()), a['werte']
    assert all(a['gleich'].values()), a['gleich']


_vergleich = abgleich.zeltfit_vergleich


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


def test_h2_intervalltyp_keiner_nicht_entscheidbar(exakt):
    """Regression (Befund der Planungssimulation): Teil B nr10 mit Intervalltyp „keiner“ (keine Überdeckung erreicht)
    führt zu H2 „nicht entscheidbar“ (Verfahren), nicht zu einem Abbruch."""
    import copy
    tb = copy.deepcopy(exakt['teil_b'])
    tb['nr10']['h2_intervall'] = dict(typ='keiner', niveau=None, quelle='Test')
    e = auswertung.auswerten(exakt['tabelle'], exakt['kalibrierung'], tb, PROFIL)
    assert e['H2']['ausgang'] == 'nicht entscheidbar' and e['H2']['grund'] == 'Verfahren'
    assert any('0,936' in g['text'] for g in e['H2']['gruende'])


def test_stressszenario_ohne_zulaessigen_arbeitspunkt():
    """Regression (Befund im Prüfstand): A07 verletzt die Auslegungsregel (b) bewusst (k_b = 2 < 3). Das Pilotskript
    meldet „kein zulässiger Arbeitspunkt“, liefert aber die Pilotgrößen (mit k = 3); Teil B entsteht mit den
    Planwerten, das Ergebnis nennt den Pilotbefund, und E3 ist bei singulärem T(kω) nicht auswertbar statt abzubrechen."""
    r = _kette('A07-hertz50')
    e = r['ergebnis']
    assert r['pilot']['suche']['ergebnis'].startswith('kein zulässiger') and r['pilot']['k_pilotgroessen'] == 3
    assert e['herkunft']['pilot_suche']['ergebnis'].startswith('kein zulässiger')
    assert 'Pilotskript: kein zulässiger Arbeitspunkt' in e['text']
    assert e['E3']['bewertung'] is None and e['E3']['status'].startswith('nicht auswertbar')
    assert e['H1']['ausgang'] in ('bestätigt', 'falsifiziert', 'nicht entscheidbar')


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
