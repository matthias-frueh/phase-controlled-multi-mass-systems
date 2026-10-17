"""Etappe 1: Schnittstellen von pcmms_auswertung – Formate, Konventionen, Regelprofile, Laufzusammenfassung,
Beispieldatensatz (docs/ap11_ap12_ap13_schnittstellen.md)."""
import json
import os

import numpy as np
import pytest
from scipy import stats

from pcmms_auswertung import beispiel, formate, konventionen as kv, regeln, zusammenfassung as zf

FIXTURE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', 'ap1x_beispiel')


# ── Pflichtmetadaten ─────────────────────────────────────────────────────────────────────────────────
def test_kopf_pflichtfelder_und_versionen():
    k = formate.kopf('laufzusammenfassung', formate.synth_kennung('T'))
    assert formate.pruefe_kopf(k) == 'laufzusammenfassung'
    for feld in ('schema', 'schema_version', 'datenart', 'kennung'):
        k2 = dict(k)
        del k2[feld]
        with pytest.raises(formate.FormatFehler, match=feld):
            formate.pruefe_kopf(k2)
    with pytest.raises(formate.FormatFehler, match='Version'):
        formate.pruefe_kopf({**k, 'schema_version': '9.9'})
    with pytest.raises(formate.FormatFehler, match='unbekanntes Schema'):
        formate.pruefe_kopf({**k, 'schema': 'pcmms.unbekannt'})
    with pytest.raises(formate.FormatFehler, match='statt'):
        formate.pruefe_kopf(k, 'teil_b')


def test_synthetische_kennung_und_keine_registrierung():
    with pytest.raises(formate.FormatFehler, match='SYNTH-'):
        formate.kopf('ergebnis', 'OSF-1234')
    k = formate.kopf('ergebnis', 'SYNTH-X')
    assert k['registrierung'] == formate.REGISTRIERUNG_SYNTH
    with pytest.raises(formate.FormatFehler, match='Registrierung'):
        formate.pruefe_kopf({**k, 'registrierung': 'OSF Registries, eingefroren'})


def test_messdaten_in_dieser_stufe_abgelehnt_und_nie_gemischt():
    k = dict(schema='pcmms.rohlauf', schema_version=formate.SCHEMATA['rohlauf'], datenart='messung', kennung='REG-1')
    with pytest.raises(formate.FormatFehler, match='nicht zugelassen'):
        formate.pruefe_kopf(k)
    assert formate.pruefe_kopf(k, datenarten=formate.DATENARTEN) == 'rohlauf'
    with pytest.raises(formate.FormatFehler, match='synthetischer Kennung'):
        formate.pruefe_kopf({**k, 'kennung': 'SYNTH-1'}, datenarten=formate.DATENARTEN)
    with pytest.raises(formate.FormatFehler, match='gemischte'):
        formate.gleiche_datenart(formate.kopf('ergebnis', 'SYNTH-A'), k)


def test_npz_deterministisch_und_pruefsumme(tmp_path):
    felder = dict(b=np.arange(5.0), a=np.array([1 + 2j, 3 - 1j]), c=np.zeros((2, 3), bool))
    assert formate.npz_bytes(felder) == formate.npz_bytes(dict(reversed(list(felder.items()))))
    k = formate.kopf('wahrheit', 'SYNTH-W')
    formate.schreibe(str(tmp_path / 'x'), k, felder, inhalt=dict(n=float('nan'), w=float('inf'), z=1 + 1j))
    k2, inhalt, f2 = formate.lies(str(tmp_path / 'x'), 'wahrheit')
    assert inhalt == dict(n=None, w='inf', z=[1.0, 1.0])
    assert formate.float_aus_json(inhalt['w']) == np.inf and np.isnan(formate.float_aus_json(inhalt['n']))
    for n in felder:
        assert f2[n].dtype == np.asarray(felder[n]).dtype and np.array_equal(f2[n], felder[n])
    b = bytearray((tmp_path / 'x.npz').read_bytes())
    b[-30] ^= 1
    (tmp_path / 'x.npz').write_bytes(bytes(b))
    with pytest.raises(formate.FormatFehler, match='SHA-256'):
        formate.lies(str(tmp_path / 'x'), 'wahrheit')


def test_objekt_arrays_unzulaessig():
    with pytest.raises(formate.FormatFehler, match='Objekt'):
        formate.npz_bytes(dict(x=np.array([None, 1], dtype=object)))


# ── Konventionen ─────────────────────────────────────────────────────────────────────────────────────
def _zufall_nk(K=9, seed=1):
    r = np.random.default_rng(seed)
    return (r.normal(size=K) + 1j * r.normal(size=K)) / np.arange(1, K + 1)


def test_kurve_harmonische_umkehrung():
    Nk = _zufall_nk()
    x = kv.kurve(Nk)
    th = kv.theta_raster()
    direkt = sum((Nk[k - 1] * np.exp(1j * k * th)).real for k in range(1, 10))
    assert np.abs(x - direkt).max() < 1e-12
    assert np.abs(kv.harmonische(x, 9) - Nk).max() < 1e-12
    assert kv.fmin_rel(Nk) == pytest.approx(x.min(), abs=0)
    assert np.allclose(kv.reell(Nk) @ kv.basis(9), x, atol=1e-12)


def test_momente_und_schiefe_aus_harmonischen():
    for seed in range(5):
        Nk = _zufall_nk(12, seed)
        x = kv.kurve(Nk)
        m2, m3 = kv.momente(Nk)
        assert m2 == pytest.approx((x ** 2).mean(), rel=1e-12)
        assert m3 == pytest.approx((x ** 3).mean(), rel=1e-10, abs=1e-14)
        assert kv.schiefe(Nk) == pytest.approx(stats.skew(x), rel=1e-9)
    assert np.isnan(kv.schiefe(np.zeros(5, complex)))


def test_h1_vektor_reihenfolge():
    Nk = _zufall_nk()
    q = kv.h1_vektor(Nk)
    assert q[0] == kv.fmin_rel(Nk)
    assert list(q[1:]) == [Nk[0].real, Nk[0].imag, Nk[1].real, Nk[1].imag, Nk[2].real, Nk[2].imag]
    with pytest.raises(ValueError, match='k_max'):
        kv.h1_vektor(Nk[:2])


def test_s3_gruppe_und_phasenregel():
    """Identische Module: alle sechs Bilder haben dieselben |N_k| und γ₁, arg N_k folgt k·φ_ref. F_min − ⟨N⟩ ist
    auf den N_θ Stützstellen nur gleich, wenn φ_ref auf dem Raster liegt (360°/2000 = 0,18°); sonst weicht das
    Rasterminimum höchstens um ½·max|x''|·(π/N_θ)² ab (Befund zur Toleranz 10⁻⁹ N von K16, Plan 1.3)."""
    Nj = _zufall_nk(9, 3)                                   # Antwort eines Moduls (eigener Takt)
    k = np.arange(1, 10)
    basis_phi = (0.0, 110.0, 234.0)

    def konf(phi):
        return (Nj * kv.zeigerfaktor(np.array(phi), k)).sum(0)

    N0 = konf(basis_phi)
    x2 = np.abs(kv.kurve(-(k ** 2) * N0)).max()             # max|x''| in N/rad²
    schranke = 0.5 * x2 * (np.pi / kv.N_THETA) ** 2
    bilder = kv.s3_bilder(110.0, 234.0)
    assert len(bilder) == 6 and len({(round(b[1][0], 9), round(b[1][1], 9)) for b in bilder}) == 6
    for perm, (p2, p3), ref in bilder:
        N = konf((0.0, p2, p3))
        assert np.abs(N - N0 * np.exp(1j * k * np.radians(ref))).max() < 1e-12
        assert np.abs(np.abs(N) - np.abs(N0)).max() < 1e-12
        assert kv.schiefe(N) == pytest.approx(kv.schiefe(N0), abs=1e-12)
        auf_raster = abs(ref / 0.18 - round(ref / 0.18)) < 1e-9
        assert abs(kv.fmin_rel(N) - kv.fmin_rel(N0)) <= (1e-12 if auf_raster else schranke)
    assert {round(b[2], 6) for b in bilder} == {0.0, 110.0, 234.0}


def test_abtastrate_a6():
    assert kv.abtastrate_a6(10.0, 9) == pytest.approx(6322.3, abs=0.1)     # A6: „etwa f_s ≥ 6,3 kHz“
    assert kv.abtastrate_a6(10.0, 12) == pytest.approx(8429.7, abs=0.1)    # Plan 4.1: ≥ 8,4 kHz
    fs = kv.abtastrate_a6(14.0, 7)
    assert (np.pi * 7 * 14.0 / fs) ** 2 / 2 == pytest.approx(1e-3)


# ── Regelprofile ─────────────────────────────────────────────────────────────────────────────────────
def test_regeln_vollstaendig_gekennzeichnet():
    for name in regeln.PROFILE:
        p = regeln.profil(name)
        for r in p.regeln.values():
            assert r.status in regeln.STATUS and r.fundstelle and r.gegenstand
            if r.status == regeln.EP:
                assert name == 'ENTW-2026-10' and r.herkunft, r.id
            if r.status in (regeln.OF, regeln.NI):
                assert r.wert is None, r.id


def test_offene_regel_ohne_stillen_vorgabewert():
    af, entw = regeln.profil('AF-2026-10'), regeln.profil('ENTW-2026-10')
    for rid in ('h2.delta_grad', 'h3.delta', 'h3.relevanz', 'h1z.grenzen', 'e3.schwellen', 'zuordnung.regel',
                'h2.w_grad', 'h2.mittelpunkt', 'h2.intervallkette', 'drift.zusatz'):
        with pytest.raises(regeln.RegelOffen) as e:
            af.wert(rid)
        assert 'offen' in e.value.grund
        assert entw.eintrag(rid).status == regeln.EP and entw.hat(rid)
    assert entw.wert('h2.delta_grad') == 1.0 and entw.wert('h3.delta') == 0.10
    for rid in ('h1.faktor', 'h1.d_fassung', 'h1.delta_rel', 'h2.logik', 'h3.logik', 'M.konvention'):
        assert af.eintrag(rid).status == regeln.AF and af.wert(rid) == entw.wert(rid)
    with pytest.raises(regeln.RegelOffen):
        entw.wert('ni.fassung_I')


def test_reduktion_sichtbar_und_profil_rundreise(tmp_path):
    p = regeln.profil('ENTW-2026-10')
    assert p.zahl('bootstrap_B') == 10000 and not p.reduziert
    q = p.mit_reduktion(bootstrap_B=200, h2_replikate=200)
    assert q.reduziert and q.zahl('bootstrap_B') == 200 and q.id.startswith('ENTW-2026-10+red(')
    assert q.kurz()['reduktion']['normativ'] == {'bootstrap_B': 10000, 'h2_replikate': 10000, 'e3_mc': 10000}
    assert q.zahl('e3_mc') == 200                                   # H2 und E3 nutzen die Bootstrap-Zeilen
    with pytest.raises(ValueError, match='folgt bootstrap_B'):
        p.mit_reduktion(bootstrap_B=200, h2_replikate=300)
    regeln.schreibe_profil(str(tmp_path / 'p'), q)
    assert regeln.lade_profil(str(tmp_path / 'p')).sha256() == q.sha256()
    obj = json.loads((tmp_path / 'p.json').read_text(encoding='utf-8'))
    obj['inhalt']['regeln']['h2.delta_grad']['wert'] = 0.5                 # stille Änderung
    (tmp_path / 'p.json').write_text(json.dumps(obj), encoding='utf-8')
    with pytest.raises(formate.FormatFehler, match='weicht'):
        regeln.lade_profil(str(tmp_path / 'p'))


def test_regelmatrix_nennt_jede_regel():
    m = regeln.matrix_markdown()
    for rid in regeln.profil('AF-2026-10').regeln:
        assert f'`{rid}`' in m


# ── Laufzusammenfassung ──────────────────────────────────────────────────────────────────────────────
def _kopf(i=0, **kw):
    k = dict(lauf_id=f'T{i}', laufart='K', modul=None, einstellung=1,
             konfiguration=dict(id='S120', gruppe='schnitt', phi_soll_grad=[0.0, 120.0, 240.0]), phase=1, block=1,
             messtag=1, position=i, kontrollsatz=None, t_start=10.0 * i, t_ende=10.0 * i + 9.0, f_soll=10.0,
             f_mittel=10.0, n_zyklen=100, n_fuenftel=20, k_voll=12, n_theta=2000, stoerung=False,
             aufzeichnung_ok=True, park_ok=None, fehlende_kanaele=[], hash_rohdatei=None, version_stufe1='H',
             kalibrier_hash=None, ebene='H')
    k.update(kw)
    return k


def test_laufzusammenfassung_pruefung_und_rundreise(tmp_path):
    d = zf.leere_daten(12)
    lz = zf.Laufzusammenfassung(_kopf(), d)
    lz.schreiben(str(tmp_path / 'l'), 'SYNTH-L')
    l2 = zf.Laufzusammenfassung.lesen(str(tmp_path / 'l'))
    assert l2.kopf == lz.kopf and l2.meta['kennung'] == 'SYNTH-L'
    with pytest.raises(formate.FormatFehler, match='Kopffelder'):
        zf.Laufzusammenfassung({k: v for k, v in _kopf().items() if k != 'phase'}, d)
    with pytest.raises(formate.FormatFehler, match='Nk_summe'):
        zf.Laufzusammenfassung(_kopf(), {**d, 'Nk_summe': np.zeros(11, complex)})
    with pytest.raises(formate.FormatFehler, match='Laufart'):
        zf.Laufzusammenfassung(_kopf(laufart='X'), d)


def test_lauftabelle_spalten_auswahl_buendel(tmp_path):
    t = zf.LaufTabelle.aus_liste([zf.Laufzusammenfassung(_kopf(i, position=5 - i), zf.leere_daten(12))
                                  for i in range(4)])
    assert len(t) == 4 and t.daten['Nk_summe'].shape == (4, 12)
    s = t.sortiert()
    assert s.spalte('position') == [2, 3, 4, 5]
    t.schreiben(str(tmp_path / 'b'), 'SYNTH-B')
    t2 = zf.LaufTabelle.lesen(str(tmp_path / 'b'))
    assert t2.konfig_ids() == t.konfig_ids()
    with pytest.raises(formate.FormatFehler, match='doppelte'):
        zf.LaufTabelle([_kopf(0), _kopf(0)], zf.leere_daten(12, 2))


def test_konfig_id():
    assert zf.konfig_id('K', (0, 120, 240), gruppe='schnitt') == 'S120'
    assert zf.konfig_id('K', (0, 110, 250), gruppe='pilot') == 'P110_250'
    assert zf.konfig_id('K', (0, 116, 240), gruppe='identifizierbarkeit', einstellung=2) == 'I116′'
    assert zf.konfig_id('L', modul=2, einstellung=2) == 'L2′'
    assert zf.konfig_id('R') == 'R'


# ── Beispieldatensatz ────────────────────────────────────────────────────────────────────────────────
def _ohne_codeversion(o):
    if isinstance(o, dict):
        return {k: _ohne_codeversion(v) for k, v in o.items() if k != 'code_version'}
    if isinstance(o, list):
        return [_ohne_codeversion(v) for v in o]
    return o


def test_beispiel_reproduzierbar_und_gleich_fixture(tmp_path):
    """Der eingecheckte Beispieldatensatz entsteht bitgleich neu (NPZ) bzw. inhaltsgleich (JSON ohne Codestand)."""
    beispiel.erzeugen(str(tmp_path))
    n = 0
    for wurzel, _, dateien in os.walk(FIXTURE):
        for d in dateien:
            a = os.path.join(wurzel, d)
            b = os.path.join(str(tmp_path), os.path.relpath(a, FIXTURE))
            assert os.path.exists(b), b
            if d.endswith('.json'):
                ja, jb = (json.load(open(x, encoding='utf-8')) for x in (a, b))
                if d == 'manifest.json':                    # Kopf-SHA-256 hängt am Codestand im Kopf der Rohdatei
                    for z in ja['inhalt']['laeufe'] + jb['inhalt']['laeufe']:
                        z.pop('sha256_kopf')
                assert _ohne_codeversion(ja) == _ohne_codeversion(jb), d
            elif d.endswith('.npz'):
                assert open(a, 'rb').read() == open(b, 'rb').read(), d
            n += 1
    assert n == 12
    k, zeilen, _ = __import__('pcmms_auswertung.rohdaten', fromlist=['x']).lies_manifest(
        os.path.join(str(tmp_path), 'eingang', 'laeufe'))
    assert [z['lauf_id'] for z in zeilen] == ['B-R-001', 'B-L1-001']


def test_beispiel_wahrheit_getrennt_vom_eingang():
    ein = os.path.join(FIXTURE, 'eingang')
    for wurzel, _, dateien in os.walk(ein):
        for d in dateien:
            if d.endswith('.json'):
                assert '"pcmms.wahrheit"' not in open(os.path.join(wurzel, d), encoding='utf-8').read()
    assert os.path.exists(os.path.join(FIXTURE, 'wahrheit', 'wahrheit.json'))
    assert beispiel.abtastrate() == 2110.0 >= kv.abtastrate_a6(10.0, 3)


def test_regelmatrix_dokument_gleich_code():
    """docs/ap11_ap12_ap13_regelmatrix.md enthält die aus regeln.py erzeugte Tabelle unverändert."""
    pfad = os.path.join(os.path.dirname(FIXTURE), '..', '..', 'docs', 'ap11_ap12_ap13_regelmatrix.md')
    text = open(pfad, encoding='utf-8').read()
    teil = text.split('<!-- MATRIX-ANFANG', 1)[1].split('-->', 1)[1].split('<!-- MATRIX-ENDE -->', 1)[0]
    assert teil.strip() == regeln.matrix_markdown().strip()


def test_zufallsstroeme_unabhaengig_und_deterministisch():
    from pcmms_auswertung import zufall
    a = zufall.strom(7, 'generator', 'N01', 2, 15).normal(size=4)
    assert np.array_equal(a, zufall.strom(7, 'generator', 'N01', 2, 15).normal(size=4))
    for andere in (('kalibrierung_c', 'N01', 2, 15), ('generator', 'N01', 2, 16), ('generator', 'N02', 2, 15)):
        assert not np.allclose(a, zufall.strom(7, *andere).normal(size=4))
    assert zufall.katalog_seed('f' * 64) == 2 ** 64 - 1
