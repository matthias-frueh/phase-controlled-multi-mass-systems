"""k-Konsistenz der Phase-0-Größen (Auftrag vom 17.10.2026, Teil A): Teil B bindet σ_Δ, Gültigkeitsmasken, ε_ctrl, p̂
und Streuungen an k_max und N_z des tatsächlich verwendeten Plans. Geprüft an direkt aus den Fünftelharmonischen
nachgerechneten Pilotdifferenzen, nicht nur an den Bindungsfeldern: k = 30 → 9 (A4), ohne k-Wechsel (V1-G0), extern
übergebener Plan, erfolgreicher Suchpfad, erneute Prüfung des Arbeitspunkts und Einordnung alter Dateien."""
import numpy as np
import pytest

from pcmms_auswertung import konventionen as kv, pilot, regeln, teil_b, verfahren as vf
from pcmms_auswertung.generator import kampagne as kp, szenarien
from pcmms_auswertung.harness import kette

PROFIL = regeln.profil('ENTW-2026-10').mit_reduktion(bootstrap_B=200, h3_mc=200, eps_ctrl_datensaetze=500)
PLAN = kp.Plan(n0=20, n_pilot=20, n_bloecke=24, p0_anordnung='historisch')   # Seedeigenschaft der alten Anordnung
W8 = kette.testvorgabe_werkzeug8()


def _kampagne(sid, seed, k_max=None):
    m, laeufe, tab = kette.kampagne_erzeugen(sid, 'L1', PLAN, seed, k_max=k_max)
    _, _, kal = kette.kalibrierung_erzeugen(szenarien.KATALOG[sid], m, seed)
    return m, tab, kal


def _gruppe(h):
    return 'R' if h['laufart'] == 'R' else ('K' if h['laufart'] == 'K' else f'L{h["modul"]}')


def direkt(tab0, k):
    """σ_Δ je Laufart und G4-Verstöße unmittelbar aus den Fünfteln: D_N, D_F = F_min − ⟨N⟩ (k ≤ k) des letzten minus
    des ersten Fünftels, σ_Δ = 1,4826·MAD je Laufart, Verstoß bei |D| > 3·σ_Δ (+ Rundungsboden)."""
    d = tab0.daten
    DN = d['fuenftel_N_mittel'][:, 1] - d['fuenftel_N_mittel'][:, 0]
    DF = kv.fmin_rel(d['fuenftel_Nk'][:, 1, :k]) - kv.fmin_rel(d['fuenftel_Nk'][:, 0, :k])
    gr = np.array([_gruppe(h) for h in tab0.koepfe])
    sig, g4 = {}, np.zeros(len(tab0), bool)

    def mad(x):
        return 1.4826 * np.median(np.abs(x - np.median(x)))
    for g in sorted(set(gr)):
        m = gr == g
        sig[g] = dict(N=mad(DN[m]), F=None if g == 'R' else mad(DF[m]))
        boden = 1e-12 * np.abs(d['N_mittel'][m])
        v = np.abs(DN[m]) > 3 * sig[g]['N'] + boden
        if g != 'R':
            v |= np.abs(DF[m]) > 3 * sig[g]['F'] + boden
        g4[m] = v
    return sig, {tab0.koepfe[i]['lauf_id'] for i in np.flatnonzero(g4)}


def _phase0(tab):
    return tab.auswahl(tab.spalte('phase', int) == 0).sortiert()


@pytest.fixture(scope='module')
def a4():
    """A4 (k_b = 30, k_max = 9), Seed 24: bei k = 9 sind vier Piloten und drei L₂ mehr G4-ungültig als bei k = 30."""
    m, tab, kal = _kampagne('N01-A4', 24)
    tb, pe = kette.teil_b_erzeugen(tab, kal, m, PROFIL, W8, 24, 18)
    tbh, _ = kette.teil_b_erzeugen(tab, kal, m, PROFIL, W8, 24, 18, verfahren=vf.HISTORISCH)
    return m, tab, kal, tb, tbh, pe


def test_k30_auf_9_teil_b_an_k_max_gebunden(a4):
    m, tab, kal, tb, tbh, pe = a4
    n2 = tb['nr2']
    assert pe['k_pilotgroessen'] == 30 and n2['k_max'] == 9 == m.system.k_max
    t0 = _phase0(tab)
    sig9, g4_9 = direkt(t0, 9)
    sig30, g4_30 = direkt(t0, 30)
    for g, v in sig9.items():                                         # σ_Δ je Laufart beim k_max des Plans
        assert n2['sigma_delta'][g]['N'] == pytest.approx(v['N'], rel=1e-12)
        if v['F'] is not None:
            assert n2['sigma_delta'][g]['F'] == pytest.approx(v['F'], rel=1e-12)
    assert abs(n2['sigma_delta']['K']['F'] - sig30['K']['F']) > 0.05 * sig30['K']['F']   # alter Stand: k = 30
    assert tbh['nr2']['sigma_delta']['K']['F'] == pytest.approx(sig30['K']['F'], rel=1e-12)
    # Gültigkeitsmaske: G4-Verstöße des gebundenen Satzes = direkt bei k = 9, verschieden von k = 30
    s = pilot.satz_fuer_plan(t0, kal, PROFIL, m.system.f, 9, 24)
    g4_satz = {i for i, r in s['gueltigkeit']['gruende'].items() if 'G4' in r}
    assert g4_satz == g4_9 and g4_9 != g4_30
    # ŷ⁰-Basis: gültige Einzelmodulläufe der Phase 0 ohne die bei k = 9 ungültigen
    ung = set(s['gueltigkeit']['gruende'])
    assert g4_9 <= ung
    for j, e in enumerate(tb['nr3']['einzel0'], start=1):
        alle = [h['lauf_id'] for h in t0.koepfe if h['laufart'] == 'L' and h['modul'] == j and h['einstellung'] == 1]
        assert e['lauf_ids'] == [x for x in alle if x not in ung]
    assert [len(e['lauf_ids']) for e in tb['nr3']['einzel0']] != [len(e['lauf_ids']) for e in tbh['nr3']['einzel0']]
    # p̂ der Piloten direkt: Anteil der Piloten unter den bei k = 9 ungültigen Läufen
    pil = [h['lauf_id'] for h in t0.koepfe if h['konfiguration']['gruppe'] == 'pilot']
    p_direkt = np.mean([x in ung for x in pil])
    assert n2['p_hat'] == pytest.approx(p_direkt, abs=0) and p_direkt == pytest.approx(5 / 60)
    assert tbh['nr2']['p_hat'] == pytest.approx(1 / 60)
    b = n2['phase0_bindung']
    assert b['modus'] == 'plan' and b['k'] == 9 and b['N_z'] == 100 and b['neu_berechnet'] and b['qualifiziert']
    assert b['bindung']['k'] == 9 and b['bindung']['phase0_sha256'] == pilot.daten_sha256(t0)
    hb = tbh['nr2']['phase0_bindung']
    assert hb['modus'] == 'historisch' and hb['k'] == 30 and not hb['qualifiziert']
    assert tbh['nr2']['arbeitspunkt']['status'] == 'nicht abgesichert'


def test_kontrollgrenze_und_kovarianz_folgen_dem_satz():
    """ε_ctrl hängt über die gültigen Pilot- und Einzelmodulläufe von k ab (A4, Seed 2: σ̂_betr ändert sich); die
    Pilotkovarianzen haben die Dimension 3 + 6·k des gebundenen k."""
    m, tab, kal = _kampagne('N01-A4', 2)
    t0 = _phase0(tab)
    pe = pilot.pilot_auswerten(t0, kal, PROFIL, m.system.f, seed=2)
    s9 = pilot.satz_fuer_plan(t0, kal, PROFIL, m.system.f, 9, 2)
    assert s9['eps_ctrl']['eps_ctrl'] != pe['eps_ctrl']['eps_ctrl']
    tb, _ = kette.teil_b_erzeugen(tab, kal, m, PROFIL, W8, 2, 18)
    assert tb['nr2']['eps_ctrl'] == s9['eps_ctrl']['eps_ctrl'] and tb['nr10']['eps_kritisch'] == s9['eps_ctrl']['kritisch']
    assert s9['kovarianzen']['K']['kovarianz'].shape == (3 + 6 * 9,) * 2
    assert pe['kovarianzen']['K']['kovarianz'].shape == (3 + 6 * 30,) * 2
    assert s9['sigma_ref']['sigma_ref'] == pe['sigma_ref']['sigma_ref']           # Referenzläufe: G4 nur mit ⟨N⟩


def test_ohne_k_wechsel_satz_uebernommen():
    """V1-G0: k der Pilotgrößen = k_max = 12. Der Satz der Pilotausgabe wird unverändert übernommen und stimmt mit
    der direkten Nachrechnung und der historischen Bindung überein."""
    m, tab, kal = _kampagne('N01-V1G0', 5)
    tb, pe = kette.teil_b_erzeugen(tab, kal, m, PROFIL, W8, 5, 18)
    tbh, _ = kette.teil_b_erzeugen(tab, kal, m, PROFIL, W8, 5, 18, verfahren=vf.HISTORISCH)
    assert pe['k_pilotgroessen'] == tb['nr2']['k_max'] == 12
    b = tb['nr2']['phase0_bindung']
    assert b['quelle'] == 'Pilotskript, oberste Ebene' and not b['neu_berechnet']
    sig, _ = direkt(_phase0(tab), 12)
    assert tb['nr2']['sigma_delta']['K']['F'] == pytest.approx(sig['K']['F'], rel=1e-12)
    for x in ('sigma_delta', 'eps_ctrl', 'sigma_ref', 'p_hat'):
        assert tb['nr2'][x] == tbh['nr2'][x]
    assert tb['nr3']['einzel0'][1]['lauf_ids'] == tbh['nr3']['einzel0'][1]['lauf_ids']
    assert tb['nr2']['arbeitspunkt']['status'] == 'nicht geprüft'


def test_extern_uebergebener_plan(a4):
    """Ein direkt übergebener Plan mit k_max = 5 und N_z = 100: Teil B rechnet den Satz bei k = 5 neu. Ein Plan mit
    anderem N_z, Pilotgrößen anderer Daten und eine alte Pilotausgabe ohne Seed werden zurückgewiesen."""
    m, tab, kal, tb, tbh, pe = a4
    t0 = _phase0(tab)
    plan = dict(kette.plan_info(m, 18), k_max=5, N_z=100)
    tb5 = teil_b.erstellen(t0, kal, pe, PROFIL, plan, W8, seed_b0=1, B=50)
    sig5, g4_5 = direkt(t0, 5)
    assert tb5['nr2']['k_max'] == 5 and tb5['nr2']['phase0_bindung']['k'] == 5
    assert tb5['nr2']['sigma_delta']['K']['F'] == pytest.approx(sig5['K']['F'], rel=1e-12)
    with pytest.raises(ValueError, match='N_z = 100 Zyklen passen nicht zum Plan'):
        teil_b.erstellen(t0, kal, pe, PROFIL, dict(plan, N_z=60), W8, seed_b0=1, B=50)
    fremd = dict(pe, bindung=dict(pe['bindung'], k=5, phase0_sha256='0' * 64))
    with pytest.raises(ValueError, match='aus anderen Phase-0-Daten'):
        teil_b.erstellen(t0, kal, fremd, PROFIL, plan, W8, seed_b0=1, B=50)
    alt = {k: v for k, v in pe.items() if k not in ('bindung', 'seed')}
    alt['version'] = 'pilot-0.2'
    with pytest.raises(ValueError, match='ohne Seed der ε_ctrl-Simulation nicht neu berechenbar'):
        teil_b.erstellen(t0, kal, alt, PROFIL, plan, W8, seed_b0=1, B=50)
    tb_alt = teil_b.erstellen(t0, kal, alt, PROFIL, plan, W8, seed_b0=1, B=50, seed_pilot=24)
    assert tb_alt['nr2']['sigma_delta'] == tb5['nr2']['sigma_delta'] and tb_alt['nr2']['p_hat'] == tb5['nr2']['p_hat']
    e = pilot.einordnen(alt)
    assert not e['gebunden'] and e['k'] == 30 and 'keine Bindung an k_max' in e['bedeutung']
    with pytest.raises(ValueError, match='Bindung'):
        teil_b.erstellen(t0, kal, pe, PROFIL, plan, W8, seed_b0=1, B=50, bindung='k_pilot')


def test_planungshaken_und_harness_binden_an_das_k_des_aufrufs():
    """kette mit k_max = 7 (wie die Kampagnen des Planungshakens je Paar (k, T_a)): Teil B bei k = 7."""
    m, tab, kal = _kampagne('N01-A4', 24, k_max=7)
    tb, pe = kette.teil_b_erzeugen(tab, kal, m, PROFIL, W8, 24, 18)
    sig7, _ = direkt(_phase0(tab), 7)
    assert tb['nr2']['k_max'] == 7 and tb['nr2']['sigma_delta']['K']['F'] == pytest.approx(sig7['K']['F'], rel=1e-12)
    assert tb['verfahren'] == vf.STANDARD.kennung()


@pytest.fixture(scope='module')
def v1_suche():
    from pcmms_auswertung import anpassung
    from pcmms_auswertung.generator import ebene_h, kalibrierdaten
    m = szenarien.modell('N01-V1G0', 'L2', plan=kp.Plan(n0=20, n_pilot=20, n_bloecke=2))
    mes, _ = kalibrierdaten.p0_messungen(m.system, np.random.default_rng(5))
    kal = anpassung.kalibrieren(mes, band_hz=(20.0, 600.0))
    laeufe = kp.laufplan(m.plan, np.random.default_rng(1))
    tab = ebene_h.erzeuge(m, laeufe, np.random.default_rng(2))
    zeit = dict(T_park=2.0, T_ramp=2.0, T_ab=2.0, T_eP=3.0, T_aP=12.0, T_verfuegbar=8 * 3600, d=1, N_K=21, N_I=0)

    def haken(e):                                                    # Testhaken: erst bei k ≤ 8 zulässig
        return dict(n_min=12, n0=20, quelle='Testhaken') if e['k'] <= 8 else dict(n_min=None, n0=None,
                                                                                    grund='Testhaken', kandidaten=[])
    prof = regeln.profil('ENTW-2026-10').mit_reduktion(eps_ctrl_datensaetze=300)
    pe = pilot.pilot_auswerten(tab, kal, prof, 10.0, zeit=zeit, seed=3, planung=haken)
    return m, tab, kal, pe, prof


def test_suchpfad_satz_beim_festgelegten_paar(v1_suche):
    m, tab, kal, pe, prof = v1_suche
    s = pe['suche']
    assert s['ergebnis'] == 'festgelegt' and s['k_max'] == 8 and pe['k_pilotgroessen'] == 12
    assert s['satz']['bindung']['k'] == 8 and s['satz']['p_hat'] == s['p_hat']
    t0 = _phase0(tab)
    plan = dict(f=10.0, k_max=s['k_max'], N_z=s['N_z'], n_min=s['n_min'], n0=s['n0'], r=s['reserve_r'], n=s['n'],
                d=1, n_max=s['n_max'], zeit=s['zeit'], T_lauf=s['T_lauf'], p_hat=s['p_hat'])
    tb = teil_b.erstellen(t0, kal, pe, prof, plan, W8, seed_b0=1, B=50)
    sig8, _ = direkt(t0, 8)
    assert tb['nr2']['phase0_bindung']['quelle'] == 'Pilotskript, Suche'
    assert tb['nr2']['sigma_delta']['K']['F'] == pytest.approx(sig8['K']['F'], rel=1e-12)
    assert pe['sigma_delta']['K']['F'] != pytest.approx(sig8['K']['F'], rel=1e-3)     # oberste Ebene: k = 12
    ap = tb['nr2']['arbeitspunkt']
    assert ap['status'] == 'abgesichert' and ap['aus_suche'] and not ap['verfehlt']
    # derselbe Plan mit zu kleiner Reserve und ein vom Suchergebnis abweichender Plan: nicht abgesichert
    tb2 = teil_b.erstellen(t0, kal, pe, prof, dict(plan, n=plan['n_min'] + 1, r=1), W8, seed_b0=1, B=50)
    assert tb2['nr2']['arbeitspunkt']['status'] == 'nicht abgesichert'
    assert any('n_min + r(p̂)' in x for x in tb2['nr2']['arbeitspunkt']['verfehlt'])
    tb3 = teil_b.erstellen(t0, kal, pe, prof, dict(plan, k_max=7), W8, seed_b0=1, B=50)
    v = tb3['nr2']['arbeitspunkt']['verfehlt']
    assert tb3['nr2']['arbeitspunkt']['status'] == 'nicht abgesichert' and any('k_max' in x for x in v)


def test_suchtreffer_ohne_k_wechsel_dem_satz_der_suche_zugeordnet(v1_suche):
    """Gegenprobe vom 18.10.2026 (Testhaken: reiner Softwareprüffall, keine Qualifikation eines Arbeitspunkts): Legt die
    Suche schon beim ersten Paar fest, ist k = 12 → 12 und N_z = 100 wie beim vorläufigen Satz auf oberster Ebene.
    Teil B ordnet den Satz der Suche zu (Quelle und Bindung), der Arbeitspunkt ist abgesichert; am Stand vor der
    Korrektur wurde der gleich gebundene vorläufige Satz übernommen und allein wegen seiner Quelle abgelehnt. Fremde
    Daten, ein abweichender Plan, eine zu kleine Reserve und eine andere Bindung bleiben zurückgewiesen bzw. nicht
    abgesichert."""
    m, tab, kal, _, prof = v1_suche
    zeit = dict(T_park=2.0, T_ramp=2.0, T_ab=2.0, T_eP=3.0, T_aP=12.0, T_verfuegbar=8 * 3600, d=1, N_K=21, N_I=0)
    pe = pilot.pilot_auswerten(tab, kal, prof, 10.0, zeit=zeit, seed=3,
                               planung=lambda e: dict(n_min=12, n0=20, quelle='Testhaken'))
    s = pe['suche']
    assert s['ergebnis'] == 'festgelegt' and len(s['schritte']) == 1                     # erstes Paar
    assert s['k_max'] == pe['k_pilotgroessen'] == 12 and s['N_z'] == pe['bindung']['N_z'] == 100
    t0 = _phase0(tab)
    plan = dict(f=10.0, k_max=s['k_max'], N_z=s['N_z'], n_min=s['n_min'], n0=s['n0'], r=s['reserve_r'], n=s['n'],
                d=1, n_max=s['n_max'], zeit=s['zeit'], T_lauf=s['T_lauf'], p_hat=s['p_hat'])
    tb = teil_b.erstellen(t0, kal, pe, prof, plan, W8, seed_b0=1, B=50)
    b, ap = tb['nr2']['phase0_bindung'], tb['nr2']['arbeitspunkt']
    assert ap['status'] == 'abgesichert' and ap['aus_suche'] and not ap['verfehlt']     # Fehler vor der Korrektur
    assert b['quelle'] == 'Pilotskript, Suche' and b['bindung']['quelle'] == 'Suche: Paar (k = 12, N_z = 100)'
    assert b['k'] == 12 and not b['neu_berechnet'] and b['bindung']['phase0_sha256'] == pilot.daten_sha256(t0)
    sig12, _ = direkt(t0, 12)                                                           # unabhängig nachgerechnet
    assert tb['nr2']['sigma_delta']['K']['F'] == pytest.approx(sig12['K']['F'], rel=1e-12)
    assert tb['nr2']['p_hat'] == s['p_hat'] and tb['nr2']['n'] == s['n']
    fremd = dict(pe, suche=dict(s, satz=dict(s['satz'], bindung=dict(s['satz']['bindung'], phase0_sha256='0' * 64))))
    with pytest.raises(ValueError, match='aus anderen Phase-0-Daten'):
        teil_b.erstellen(t0, kal, fremd, prof, plan, W8, seed_b0=1, B=50)
    for anders, text in ((dict(n0=19), 'Plan weicht vom Ergebnis der Suche ab'),
                         (dict(n=plan['n_min'] + 1, r=1), 'n_min + r(p̂)')):
        ax = teil_b.erstellen(t0, kal, pe, prof, dict(plan, **anders), W8, seed_b0=1, B=50)['nr2']['arbeitspunkt']
        assert ax['status'] == 'nicht abgesichert' and any(text in x for x in ax['verfehlt'])
    anders = dict(b, bindung=dict(b['bindung'], seed_eps_ctrl=b['bindung']['seed_eps_ctrl'] + 1))
    ax = teil_b.arbeitspunkt(plan, s['satz'], anders, pe, prof)
    assert ax['status'] == 'nicht abgesichert' and any('Bindung des Satzes' in x for x in ax['verfehlt'])


def test_arbeitspunkt_nach_neuberechnung_nicht_mehr_abgesichert(a4):
    """Ein Plan, dessen Reserve mit p̂ bei k = 30 gebildet wurde (A4, Seed 24: 1/60 → r = 3), ist mit dem gebundenen
    p̂ = 5/60 bei k = 9 (r = 4) nicht mehr abgesichert; nachoptimiert wird nicht."""
    m, tab, kal, tb, tbh, pe = a4
    t0 = _phase0(tab)
    r_alt = int(np.ceil(18 * pe['p_hat'] / (1 - pe['p_hat']))) + 2
    plan = dict(kette.plan_info(m, 18), n=18 + r_alt, r=r_alt, p_hat=pe['p_hat'])
    tbx = teil_b.erstellen(t0, kal, pe, PROFIL, plan, W8, seed_b0=1, B=50)
    ap = tbx['nr2']['arbeitspunkt']
    assert r_alt == 3 and ap['r_soll'] == 4 and ap['status'] == 'nicht abgesichert'
    assert tbx['nr2']['n'] == 21 and any('p̂ des Plans' in x for x in ap['verfehlt'])


def test_arbeitspunkt_logik():
    """Statusregeln ohne Daten: Reserve, n_max aus den Zeitangaben, Herkunft aus der Suche (Quelle und Bindung)."""
    bindung = dict(k=9, N_z=100, n_fuenftel=20, T_a_s=10.0, quelle='Suche: Paar (k = 9, N_z = 100)',
                   phase0_sha256='a' * 64, n_laeufe=140, n_pilot=60, seed_eps_ctrl=1, n_sim_eps_ctrl=300,
                   version='pilot-0.3')
    satz = dict(p_hat=0.05, bindung=bindung)
    info = dict(modus='plan', quelle='Pilotskript, Suche', bindung=bindung)
    zeit = dict(T_verfuegbar=10 * 3600, d=1, N_K=21, N_I=0)
    pe = dict(suche=dict(ergebnis='festgelegt', k_max=9, N_z=100, n_min=18, n0=20, n=22, satz=satz))
    plan = dict(k_max=9, N_z=100, n_min=18, n0=20, n=22, zeit=zeit, T_lauf=17.0)
    nmax = pilot.n_max(17.0, 0.05, zeit)
    a = teil_b.arbeitspunkt(plan, satz, info, pe, PROFIL)
    assert a['r_soll'] == 3 and a['n_max_neu'] == nmax
    assert a['status'] == ('abgesichert' if 22 <= nmax else 'nicht abgesichert')
    b = teil_b.arbeitspunkt(dict(plan, zeit=dict(zeit, T_verfuegbar=3600.0)), satz, info, pe, PROFIL)
    assert b['status'] == 'nicht abgesichert' and any('n_max(p̂)' in x for x in b['verfehlt'])
    c = teil_b.arbeitspunkt(plan, satz, dict(info, quelle='neu berechnet (Code des Pilotskripts)'), pe, PROFIL)
    assert c['status'] == 'nicht abgesichert'
    d = teil_b.arbeitspunkt(plan, satz, info, dict(suche=dict(ergebnis='offen')), PROFIL)
    assert d['status'] == 'nicht geprüft' and 'externer Plan' in d['hinweis']
    # Quelle „Suche“, aber eine andere oder fehlende Bindung als die des Satzes der Suche
    for b2 in (dict(bindung, phase0_sha256='b' * 64), dict(bindung, n_sim_eps_ctrl=200), None):
        e = teil_b.arbeitspunkt(plan, satz, dict(info, bindung=b2), pe, PROFIL)
        assert e['status'] == 'nicht abgesichert' and any('Bindung des Satzes' in x for x in e['verfehlt'])
    assert teil_b.gleich_gebunden(bindung, dict(bindung, quelle='andere Quellangabe'))


def test_einordnung_alter_teil_b(a4):
    m, tab, kal, tb, tbh, pe = a4
    alt = dict(tb, version='teil_b-0.2', nr2={k: v for k, v in tb['nr2'].items()
                                              if k not in ('phase0_bindung', 'arbeitspunkt', 'N_z')})
    e = teil_b.einordnen(alt)
    assert e['modus'] == 'historisch' and not e['qualifiziert'] and 'nicht an k_max = 9 gebunden' in e['bedeutung']
    n = teil_b.einordnen(tb)
    assert n['modus'] == 'plan' and n['qualifiziert'] and n['arbeitspunkt'] == 'nicht geprüft'
