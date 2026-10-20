"""G4 im Profilstand 2026-11 (Auftrag vom 20.10.2026, b1): B+ mit Laufgrößenmischung, Knickabsicherung, normierten
Ziehungen und Quantilschwelle; D mit Fünftelzeigern; n-abhängige Lⱼ-Schwelle und Pooling-Vergleich; Diagnosemodus,
fehlende Standardisierung, ältere Formate und unveränderte historische Profile.

Geprüft wird an konstruierten Kurven und einer kleinen synthetischen Kampagne, nicht an Raten."""
import numpy as np
import pytest
from scipy import stats

from pcmms_auswertung import ablauf, auswertung, g4, gueltigkeit, konventionen as kv, regeln, vorhersage as vh
from pcmms_auswertung import zusammenfassung as zf
from pcmms_auswertung.generator import kampagne as kp
from pcmms_auswertung.harness import kette

NEU = regeln.profil('ENTW-2026-11')
K = 9
NBAR = np.array([[1.0 + 0.4j, 0.35 - 0.2j, 0.12 + 0.05j, 0.04, 0.02j, 0.01, 0.005, 0.003, 0.002]] * 3)
DD = np.zeros(3)
JIT = np.array([0.0, 1.2, 1.2])
NF = 20
REGEL = NEU.wert('g4.b_plus')
KONF = [('S100', (0.0, 100.0, 240.0)), ('S120', (0.0, 120.0, 240.0)), ('S140', (0.0, 140.0, 240.0))]
PIL = [(0.0, p2, p3) for p2, p3 in kv.PILOTEN]


def _lg(off=0.0, delta=0.0, a=0.0):
    return dict(komponenten=dict(sigma_off_grad=[0.0, off, off], sigma_delta_grad=[delta] * 3, sigma_a=[a] * 3),
                versatz=dict(korrelation=dict(wert=0.0)))


def test_ohne_laufgroessen_gleich_der_standardisierung_v2():
    """Ohne Laufgrößenstreuung ist die bedingte Varianz konstant; die Quantilschwelle ist dann genau
    3·√(σ²_P + s_i² − s̄_P²) (v2 von PR #22), mindestens 3·σ_P."""
    sP = 0.06
    b = g4.bplus(KONF, PIL, NBAR, DD, np.zeros(3), JIT, NF, K, sP, _lg(), REGEL)
    assert b['alpha'] == pytest.approx(2 * stats.norm.sf(3.0))
    for c, _ in KONF:
        v2 = 3 * np.sqrt(sP ** 2 + max(0.0, b['s'][c] ** 2 - b['sbar_P'] ** 2))
        assert b['schwellen_F'][c] == pytest.approx(max(3 * sP, v2), rel=1e-6)
    assert b['sigma_W'] == pytest.approx(np.sqrt(sP ** 2 - b['sbar_P'] ** 2))


def test_laufgroessen_erhoehen_streuung_und_ziehen_schwere_raender_nach():
    sP = 0.06
    ohne = g4.bplus(KONF, PIL, NBAR, DD, np.zeros(3), JIT, NF, K, sP, _lg(), REGEL)
    mit = g4.bplus(KONF, PIL, NBAR, DD, np.zeros(3), JIT, NF, K, sP, _lg(off=3.0, delta=1.0, a=0.02), REGEL)
    assert any(mit['s'][c] > 1.02 * ohne['s'][c] for c, _ in KONF)
    for c, _ in KONF:                       # Skalenmischung: Quantil ≥ 3 × mittlere Streuung (schwere Ränder)
        assert mit['schwellen_F'][c] >= 3 * np.sqrt(mit['s'][c] ** 2 + mit['sigma_W'] ** 2) * (1 - 1e-9) or \
            mit['schwellen_F'][c] == pytest.approx(mit['untergrenze'])
    # Knickabsicherung: mit u(Δδⱼ) > 0 nie kleiner
    knick = g4.bplus(KONF, PIL, NBAR, DD, np.array([0.0, 0.5, 0.5]), JIT, NF, K, sP, _lg(off=3.0, delta=1.0, a=0.02),
                     REGEL)
    assert all(knick['s'][c] >= mit['s'][c] - 1e-15 for c, _ in KONF)
    with pytest.raises(ValueError, match='nicht umgesetzt'):
        g4.bplus(KONF, PIL, NBAR, DD, np.zeros(3), JIT, NF, K, sP, _lg(), dict(REGEL, schwelle='streuung'))


def test_normierte_ziehungen():
    Z, E = g4.ziehungen()
    assert np.allclose(Z.mean(0), 0, atol=1e-12) and np.allclose(np.cov(Z, rowvar=False), np.eye(8), atol=1e-10)
    assert np.allclose(np.cov(E, rowvar=False), np.eye(2), atol=1e-10)


def test_d_entfernt_phasenbedingte_aenderung_und_erhaelt_den_trend():
    rng = np.random.default_rng(4)
    k = np.arange(1, K + 1)
    phi = np.array([0.0, 120.0, 240.0])
    fz = np.empty((2, 3), complex)
    Nf = []
    for f in range(2):
        e = np.r_[0.0, rng.normal(0, 0.8, 2)]
        r = np.r_[1.0, 0.999, 0.998]
        fz[f] = NF * r * np.exp(-1j * np.radians(phi + e))
        rho = np.exp(-1j * np.outer(np.radians(phi + e), k)) * r[:, None] ** (k ** 2)[None]
        Nf.append((rho * NBAR).sum(0))
    DF = kv.fmin_rel(Nf[1][:K]) - kv.fmin_rel(Nf[0][:K])
    assert abs(DF) > 1e-3                                                   # Phase ändert F_min
    assert g4.d_statistik(DF, fz, NBAR, NF, K) == pytest.approx(0.0, abs=1e-9)
    trend = kv.fmin_rel(1.01 * Nf[1][:K]) - kv.fmin_rel(Nf[0][:K])          # 1 % Amplitudentrend im letzten Fünftel
    assert g4.d_statistik(trend, fz, NBAR, NF, K) == pytest.approx(0.01 * kv.fmin_rel(Nf[1][:K]), rel=1e-9)
    fz_fehlt = fz.copy()
    fz_fehlt[1, 2] = np.nan
    assert np.isnan(g4.d_statistik(DF, fz_fehlt, NBAR, NF, K))


def test_n_abhaengiger_faktor_und_pooling_vergleich():
    k20, k60, k400 = (g4.faktor_n(n) for n in (20, 60, 400))
    assert k20 > k60 > k400 > 3.0 and k400 < 3.08
    sd = {g: dict(N=0.001, F=0.002 * s) for g, s in (('L1', 1.0), ('L2', 1.0), ('L3', 1.0))}
    n0 = {'L1': 20, 'L2': 20, 'L3': 20}
    sk = {g: dict(N=1.0, F=1.0) for g in sd}
    r = g4.lj_schwellen(sd, n0, sk)
    assert r['n_abhaengig']['L1']['F'] == pytest.approx(k20 * 0.002)
    assert r['pooling']['F']['bartlett']['p'] > 0.99 and r['pooling']['F']['faktor'] == pytest.approx(k60)
    sd['L3'] = dict(N=0.001, F=0.006)
    assert g4.lj_schwellen(sd, n0, sk)['pooling']['F']['bartlett']['p'] < 1e-3      # ungleiche Module erkannt


# ── Prüfung je Lauf ──────────────────────────────────────────────────────────────────────────────────────
def _tab(dF=0.0, fz=True):
    d = zf.leere_daten(K, 1)
    d['N_mittel'][:] = 10.0
    d['N_mittel_zellen'][:] = 10.0 / 3
    d['fuenftel_N_mittel'][:] = 10.0
    d['Nk_summe'][0] = NBAR.sum(0)
    d['Nk_zellen'][0] = NBAR / 1.0
    d['fuenftel_Nk'][0] = NBAR.sum(0)[None]
    d['fuenftel_Nk'][0, 1, 0] += dF
    d['index_fehler'][:] = 0
    d['fuenftel_zeiger'][0] = NF
    if not fz:
        d.pop('fuenftel_zeiger')
    kopf = dict(lauf_id='1-01000-S120', laufart='K', modul=None, einstellung=1,
                konfiguration=dict(id='S120', gruppe='schnitt', phi_soll_grad=[0.0, 120.0, 240.0]), phase=1, block=1,
                messtag=1, position=1000, kontrollsatz=None, t_start=0.0, t_ende=1.0, f_soll=10.0, f_mittel=10.0,
                n_zyklen=100, n_fuenftel=NF, k_voll=K, n_theta=kv.N_THETA, stoerung=False, aufzeichnung_ok=True,
                park_ok=None, fehlende_kanaele=[], hash_rohdatei=None, version_stufe1='test', kalibrier_hash=None,
                ebene='H')
    return zf.LaufTabelle([kopf], d)


def _sw(**kw):
    return gueltigkeit.Schwellen(f_soll=10.0, kmax=K, sigma_delta={'K': dict(N=0.01, F=0.01)}, **kw)


def test_g4_konfiguration_b_plus_d_und_nicht_pruefbar():
    t = _tab(dF=0.03)
    DF = gueltigkeit.fuenftel_differenzen(t, K)[1][0]
    alt = gueltigkeit.pruefe(t, _sw(), regeln=('G4',))
    assert alt['regeln']['G4'][0] is bool(abs(DF) > 0.03)
    T = abs(DF) + 1e-3
    ok = gueltigkeit.pruefe(t, _sw(g4_modus='b_plus', g4_konfig=dict(schwellen_F={'S120': T})), regeln=('G4',))
    assert ok['regeln']['G4'][0] is False
    zu = gueltigkeit.pruefe(t, _sw(g4_modus='b_plus', g4_konfig=dict(schwellen_F={'S120': T / 2})), regeln=('G4',))
    assert zu['regeln']['G4'][0] is True
    for sw, grund in ((_sw(g4_modus='b_plus', g4_konfig=None), 'B+: Standardisierung für S120 fehlt'),
                      (_sw(g4_modus='b_plus', g4_konfig=dict(schwellen_F={})), 'B+: Standardisierung für S120 fehlt'),
                      (_sw(g4_modus='d', g4_konfig=None), 'D: Schwelle aus den Piloten fehlt')):
        p = gueltigkeit.pruefe(t, sw, regeln=('G4',))
        assert p['regeln']['G4'][0] is None and any(grund in g for _, g in p['nicht_pruefbar'].get('G4', []))
    dk = dict(schwelle_D=1.0, Nbar0=NBAR, n_f=NF)
    p = gueltigkeit.pruefe(_tab(dF=0.03, fz=False), _sw(g4_modus='d', g4_konfig=dk), regeln=('G4',))
    assert p['regeln']['G4'][0] is None
    assert any('Fünftelzeiger fehlen' in g and 'nicht durch B+ ersetzt' in g for _, g in p['nicht_pruefbar'].get('G4', []))
    p = gueltigkeit.pruefe(t, _sw(g4_modus='d', g4_konfig=dk), regeln=('G4',))
    assert p['regeln']['G4'][0] is False                       # Fünftelzeiger = n_f: Vorhersage ohne Phasenänderung


def test_alte_zusammenfassung_ohne_fuenftelzeiger_gueltig_und_erkannt():
    t = _tab(fz=False)
    assert not zf.hat_fuenftelzeiger(t.daten) and zf.hat_fuenftelzeiger(_tab().daten)
    d = dict(_tab().daten, unbekannt=np.zeros(1))
    with pytest.raises(Exception, match='unbekannt'):
        zf.LaufTabelle(t.koepfe, d)


def test_diagnosemodus_ausdruecklich_und_kennung():
    d = NEU.mit_diagnose(g4__verfahren='d').mit_reduktion(bootstrap_B=200)
    assert d.id == 'ENTW-2026-11+diag(g4.verfahren=d)+red(bootstrap_B=200,e3_mc=200,h2_replikate=200)'
    assert d.wert('g4.verfahren') == 'd' and d.eintrag('g4.verfahren').status == regeln.EP
    assert NEU.wert('g4.verfahren') == 'b_plus' and d.sha256() != NEU.mit_reduktion(bootstrap_B=200).sha256()
    with pytest.raises(ValueError, match='nicht vorgesehen'):
        NEU.mit_diagnose(g4__verfahren='v2')
    with pytest.raises(KeyError):
        regeln.profil('ENTW-2026-10').mit_diagnose(g4__verfahren='d')


def test_historische_schwellen_und_kennung_unveraendert():
    """Leere neue Felder gehen nicht in die Kennung der Schwellen ein (historische Ablaufstände und Prüfsätze)."""
    import copy
    sw = _sw()
    assert all(getattr(sw, f) is None for f in gueltigkeit.NEUE_FELDER_2026_11)
    alt = copy.copy(sw)
    for f in gueltigkeit.NEUE_FELDER_2026_11:
        delattr(alt, f)
    assert ablauf.schwellen_kennung(sw, {}) == ablauf.schwellen_kennung(alt, {})
    assert ablauf.schwellen_kennung(_sw(g4_modus='b_plus'), {}) != ablauf.schwellen_kennung(sw, {})
    tb = dict(nr2=dict(f=10.0, k_max=K, delta_delta_grad=np.zeros(3)))
    assert auswertung._g4_2026_11(tb, regeln.profil('ENTW-2026-10')) == (None, None, None)


# ── kleine Kampagne ───────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope='module')
def kampagne_neu():
    prof = NEU.mit_reduktion(bootstrap_B=100, h3_mc=100, eps_ctrl_datensaetze=200)
    plan = kp.Plan(n0=20, n_pilot=20, n_bloecke=3)
    r = kette.kampagne_ablauf('N01-A4', 'L1', plan, 11, prof, n_min=2, wiederaufnahme=False)
    return prof, r


def test_kampagne_mit_b_plus_d_und_lj_aus_teil_b(kampagne_neu):
    prof, r = kampagne_neu
    g = r['teil_b']['nr2']['g4']
    assert g['modus_profil'] == 'b_plus' and g['bindung']['k_max'] == r['teil_b']['nr2']['k_max']
    assert set(g['b_plus']['schwellen_F']) >= {c['id'] for c in r['teil_b']['nr2']['konfigurationen']
                                              if c['einstellung'] == 1}
    assert all(T >= g['b_plus']['untergrenze'] for T in g['b_plus']['schwellen_F'].values())
    assert g['d']['n_piloten'] >= 50 and g['lj']['n_abhaengig']['L1']['faktor'] > 3.0
    sw = auswertung._schwellen(r['teil_b'], prof)
    assert sw.g4_modus == 'b_plus' and sw.g4_konfig is g['b_plus'] and set(sw.g4_lj) == {'L1', 'L2', 'L3'}
    tab = kette.ablauf_tabelle(r)
    auswertung.datenlage(tab, r['teil_b'], prof)                         # online = offline mit B+
    t1 = tab.auswahl(tab.spalte('phase', int) == 1)
    p = gueltigkeit.pruefe(t1, sw, regeln=('G4',))
    assert not any('fehlt' in gr for _, gr in p['nicht_pruefbar'].get('G4', []))
    # D als Diagnosemodus auf denselben Läufen; ohne Fünftelzeiger nicht prüfbar, nicht B+
    sd = auswertung._schwellen(r['teil_b'], prof.mit_diagnose(g4__verfahren='d'))
    assert sd.g4_modus == 'd' and sd.g4_konfig is g['d']
    pd = gueltigkeit.pruefe(t1, sd, regeln=('G4',))
    assert not pd['nicht_pruefbar'].get('G4', [])
    alt = zf.LaufTabelle(t1.koepfe, {k: v for k, v in t1.daten.items() if k != 'fuenftel_zeiger'})
    pa = gueltigkeit.pruefe(alt, sd, regeln=('G4',))
    nk = sum(k['laufart'] == 'K' for k in alt.koepfe)
    assert len(pa['nicht_pruefbar'].get('G4', [])) + sum(bool(v) for v, k in zip(pa['regeln']['G4'], alt.koepfe)
                                                 if k['laufart'] == 'K') >= nk
