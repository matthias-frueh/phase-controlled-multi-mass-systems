"""Teil d0: Komponentenschätzer der Laufgrößen aus Phase 0 (laufgroessen.py), Bindung an Regel und Profil, Felder im
Pilotskript und in Teil B; unter dem historischen Profil bleiben Pilotskript, Teil B und Planungshaken bitgleich
(Prüfsummen aus dem Ausgangsstand ad8fe2a, Werte auf 10 Stellen gerundet).

Alle Datensätze sind synthetisch (Szenariogenerator Ebene H, für den Nullpunkt über die Betriebszeit das
Strukturmodell aus generator.phase0_modell, nur Phase 0); geprüft wird die Schätzkette, keine Apparatur."""
import json

import numpy as np
import pytest

from pcmms_auswertung import laufgroessen as lgm, pilot, regeln, teil_b, zufall
from pcmms_auswertung.generator import ebene_h, kampagne as kp, phase0_modell as p0m, rauschen, szenarien
from pcmms_auswertung.harness import kette

PLAN = kp.Plan(n0=20, n_pilot=20, n_bloecke=24)
AKTUELL = regeln.profil('ENTW-2026-11').mit_reduktion(eps_ctrl_datensaetze=200, bootstrap_B=50)
HIST = regeln.profil('ENTW-2026-10').mit_reduktion(eps_ctrl_datensaetze=200, bootstrap_B=50)


def _phase0(sid, stufe, seed, plan=PLAN, rausch=None):
    m = szenarien.modell(sid, stufe, plan=plan, rausch=rausch)
    laeufe = kp.laufplan(m.plan, zufall.strom(seed, 'reihenfolge'))
    tab = ebene_h.erzeuge(m, [l for l in laeufe if l['phase'] == 0], zufall.strom(seed, 'generator'))
    return m, tab


def _alle(tab):
    return np.ones(len(tab), bool)


@pytest.fixture(scope='module')
def a4():
    m, tab = _phase0('N01-A4', 'L1', 5)
    _, _, kal = kette.kalibrierung_erzeugen(szenarien.KATALOG['N01-A4'], m, 5)
    return m, tab, kal


# ── Wiedergewinnung ──────────────────────────────────────────────────────────────────────────────────
def test_wiedergewinnung_der_szenarioparameter():
    """16 Phase-0-Sätze (N01-A4, L3): Mittel der Schätzer innerhalb weniger Standardfehler der wahren Werte; Kohärenz
    über k ohne systematische Ablehnung; kein Nullpunktprozess nachgewiesen."""
    st = []
    for s in range(16):
        m, tab = _phase0('N01-A4', 'L3', 100 + s)
        lg = lgm.schaetzen(tab, _alle(tab), 9)
        k = lgm.komponenten(lg)
        koh = [lg['module'][j]['kohaerenz'][x]['p'] for j in range(3) for x in ('amplitude', 'phase')]
        st.append(np.r_[k['sigma_a'], k['sigma_delta_grad'], k['sigma_off_grad'][1:], k['sigma_jitter_grad'][1:],
                        k['sigma_h_zellen'], np.sqrt((k['sigma_mittel_zellen'] ** 2).sum()),
                        lg['nullpunkt']['diffusion']['nachgewiesen'], np.min(koh)])
    st = np.array(st)
    r, Ta = m.rausch, PLAN.n_zyklen / m.system.f
    mw = st.mean(0)
    assert np.allclose(mw[0:3], r.a('L'), rtol=0.10)                                  # σ_a,j
    assert np.allclose(mw[3:6], r.p('L'), rtol=0.10)                                  # σ_δ,j [°]
    assert np.allclose(mw[6:8], r.index_versatz_grad, rtol=0.10)                      # σ_off,j [°]
    assert np.allclose(mw[8:10], r.jitter_grad, rtol=0.02)                            # Jitter je Zyklus [°]
    assert np.allclose(mw[10:13], r.sigma_h(Ta), rtol=0.03)                           # Boden Re/Im N_c,k
    assert mw[13] == pytest.approx(np.sqrt(3) * r.sigma_mittel(Ta), rel=0.10)         # Boden von ⟨N⟩ (Summe)
    assert mw[14] <= 0.25                                                             # Diffusion selten „nachgewiesen“
    assert (st[:, 15] < 1e-3).mean() <= 0.2                                           # Kohärenz über k


def test_bindung_an_k_und_fenster():
    """Die Schätzung hängt an k (Projektion, Kohärenz) und N_z (Boden ∝ 1/√T_a); die Bindung nennt beide."""
    _, tab = _phase0('N01-A4', 'L2', 7)
    _, tab50 = _phase0('N01-A4', 'L2', 7, PLAN.mit(n_zyklen=50))
    a9, a3 = lgm.schaetzen(tab, _alle(tab), 9), lgm.schaetzen(tab, _alle(tab), 3)
    b = lgm.schaetzen(tab50, _alle(tab50), 9)
    assert (a9['bindung']['k'], a9['bindung']['N_z'], a3['bindung']['k'], b['bindung']['N_z']) == (9, 100, 3, 50)
    assert len(a9['module'][0]['rest']) == 9 and len(a3['module'][0]['rest']) == 3
    assert a9['komponenten']['sigma_a'] != a3['komponenten']['sigma_a']
    v = np.array(b['komponenten']['sigma_h_zellen']) / np.array(a9['komponenten']['sigma_h_zellen'])
    assert np.allclose(v, np.sqrt(2), rtol=0.06)
    assert b['bindung']['T_a_s'] == pytest.approx(5.0) and a9['boden']['nu_h'] == 2 * 9 * 41


def test_uebertragungstest_erkennt_andere_streuung_der_kombinationslaeufe():
    """N04-laufart (Streuungen der Kombinationsläufe doppelt so groß): Verhältnis beobachtet/Modell an den Piloten
    deutlich über 1; bei gleicher Streuung (N01-A4) nahe 1. Bei L0 trägt der erfasste Phasenanteil den Großteil."""
    _, t4 = _phase0('N04-laufart', 'L2', 3)
    _, t1 = _phase0('N01-A4', 'L2', 3)
    _, t0 = _phase0('N01-A4', 'L0', 3)
    u4 = lgm.schaetzen(t4, _alle(t4), 9)['uebertragung']['harmonische'][0]
    u1 = lgm.schaetzen(t1, _alle(t1), 9)['uebertragung']['harmonische'][0]
    u0 = lgm.schaetzen(t0, _alle(t0), 9)['uebertragung']['harmonische'][0]
    assert u4['verhaeltnis'] > 2.5 and u4['p_zweiseitig'] < 1e-6
    assert 0.6 < u1['verhaeltnis'] < 1.6
    assert u0['erfasster_anteil'] > 0.6 and u1['erfasster_anteil'] < 0.1


# ── Regularisierung, nicht identifizierbare Komponenten ─────────────────────────────────────────────
def test_nicht_identifizierbar_und_rauschfrei():
    _, tab = _phase0('N01-A4', 'L2', 11)
    art, mod = tab.spalte('laufart', object), tab.spalte('modul', object)
    maske = _alle(tab)
    l1 = np.flatnonzero((art == 'L') & (mod == 1))
    maske[l1[1:]] = False                                                  # nur ein gültiger L1-Lauf
    lg = lgm.schaetzen(tab, maske, 9)
    a = lg['module'][0]['sigma_a']
    assert a['wert'] is None and not a['identifiziert'] and '1 gültige' in a['grund']
    assert any(x['komponente'] == 'sigma_a, Modul 1' for x in lg['nicht_identifizierbar'])
    assert np.isnan(lgm.komponenten(lg)['sigma_a'][0]) and lg['uebertragung']['pruefbar'] is False
    # entartete Basis (N̄⁽²⁾ = 0): nicht identifizierbar statt Division durch null
    t2 = tab.auswahl(np.arange(len(tab)))
    t2.daten['Nk_zellen'][(art == 'L') & (mod == 2)] = 0.0
    lg2 = lgm.schaetzen(t2, _alle(t2), 9)
    assert lg2['module'][1]['sigma_delta']['identifiziert'] is False and 'entartet' in lg2['module'][1]['sigma_delta'][
        'grund']
    # rauschfreie Daten: alle Streuungen null, kein Fehler
    _, t0 = _phase0('N01-A4', 'L2', 11, rausch=rauschen.RAUSCHFREI)
    lg0 = lgm.schaetzen(t0, _alle(t0), 9)
    k0 = lgm.komponenten(lg0)
    assert np.allclose(k0['sigma_a'], 0) and np.allclose(k0['sigma_delta_grad'], 0)
    assert np.allclose(k0['sigma_h_zellen'], 0) and lg0['module'][0]['gewichtet'] is False
    # nicht aus Phase 0 identifizierbare Unterschiede sind ausdrücklich benannt
    namen = ' '.join(x['komponente'] for x in lg0['nicht_identifizierbar'])
    assert 'farbiger Jitter' in namen and 'Drift zwischen Phase 0 und Phase 1' in namen


# ── Nullpunkt über die Betriebszeit ──────────────────────────────────────────────────────────────────
def _mit_pause(tab, nach, dauer=3600.0):
    """Kopie von tab mit einer Pause in Phase 0: alle Läufe nach den ersten nach Läufen (zeitliche Reihenfolge) liegen
    um dauer [s] später; Messwerte unverändert."""
    t = tab.auswahl(np.arange(len(tab)))
    for i in np.argsort(t.spalte('t_start', float), kind='stable')[nach:]:
        t.koepfe[i].update(t_start=t.koepfe[i]['t_start'] + dauer, t_ende=t.koepfe[i]['t_ende'] + dauer)
    return t


def test_betriebszeit_lueckenlos_gleich_uhrzeit():
    """Synthetischer Laufplan: Phase 0 lückenlos ab t = 0 (Beginn jedes Laufs = Ende des vorigen); die Betriebszeit
    der Laufmitte ist genau die Uhrzeit der Laufmitte, die Korrektur dort also ohne Wirkung (bitgleich). Mit Pause
    bleibt die Betriebszeit gleich, die Lücke wird ausgewiesen."""
    _, tab = _phase0('N01-A4', 'L2', 7)
    t0, t1 = tab.spalte('t_start', float), tab.spalte('t_ende', float)
    o = np.argsort(t0)
    assert t0[o][0] == 0.0 and np.array_equal(t0[o][1:], t1[o][:-1])
    tb, luecken = lgm.betriebszeit(tab)
    assert np.array_equal(tb, 0.5 * (t0 + t1)) and luecken.size == len(tab) - 1 and not luecken.any()
    tbp, lp = lgm.betriebszeit(_mit_pause(tab, 40))
    assert np.array_equal(tbp, tb) and lp.sum() == 3600.0 and np.count_nonzero(lp) == 1


def test_nullpunkt_ueber_betriebszeit_pause_ohne_wirkung():
    """A9.2, Regel p0.strukturmodell: Nullpunktdrift [N/s] und Zufallspfad D [N²/s] je Sekunde Betriebszeit, wie sie
    das Strukturmodell anwendet (nullpunkt_zeit = 'betriebszeit'). Eine Pause von 1 h nach der Hälfte der Phase-0-Läufe
    (gleiche Messwerte, spätere Läufe nur verschoben) ändert Drift und Diffusion nicht; die Pause steht im Ergebnis."""
    m = szenarien.modell('N01-A4', 'L2', plan=PLAN)
    s2m = 3 * m.rausch.sigma_mittel(PLAN.n_zyklen / m.system.f) ** 2               # Boden von ⟨N⟩ der Summe
    st = p0m.aus_rauschmodell(m.rausch).mit(nullpunkt_drift_N_je_s=2e-5, nullpunkt_zeit='betriebszeit',
                                            nullpunkt_diffusion_N2_je_s=20 * s2m / (13 * m.plan.T_lauf))
    laeufe = [l for l in kp.laufplan(m.plan, zufall.strom(21, 'reihenfolge')) if l['phase'] == 0]
    tab = p0m.erzeuge(m, laeufe, zufall.strom(21, 'generator'), st, rng_zusatz=zufall.strom(21, 'zusatz'))
    a = lgm.schaetzen(tab, _alle(tab), 9, uebertragungstest=False)['nullpunkt']
    b = lgm.schaetzen(_mit_pause(tab, len(tab) // 2), _alle(tab), 9, uebertragungstest=False)['nullpunkt']
    assert a['diffusion']['identifiziert'] and a['diffusion']['nachgewiesen'] and a['diffusion']['wert'] > 0
    for x, f in (('drift', 'wert'), ('drift', 'u'), ('diffusion', 'wert'), ('diffusion', 'oben80'),
                 ('diffusion', 'u'), ('sigma_loo', 'wert')):
        assert b[x][f] == pytest.approx(a[x][f], rel=1e-9), (x, f)
    # Pause sichtbar: Summe der Lücken, Verhältnis der Spannen der Referenzfolge in Uhrzeit und Betriebszeit
    za, zb = a['zeitachse'], b['zeitachse']
    assert za['lueckenlos'] and za['summe_luecken_s'] == 0.0 and za['verhaeltnis_uhrzeit_betriebszeit'] == 1.0
    assert not zb['lueckenlos'] and zb['summe_luecken_s'] == 3600.0 and zb['n_luecken'] == 1
    assert zb['groesste_luecke_s'] == 3600.0 and zb['spanne_betriebszeit_s'] == za['spanne_betriebszeit_s']
    assert zb['verhaeltnis_uhrzeit_betriebszeit'] == pytest.approx(1 + 3600.0 / zb['spanne_betriebszeit_s'])


def test_obere_grenze_marginal_je_komponente():
    """oben80 = √max(0, s²·ν/χ²₀,₂(ν) − Boden) je Komponente mit eigenem ν (marginal)."""
    c = lgm.komponente(4.0, 1.0, 19, 'N', 'Test')
    k = lgm.kappa(19)
    assert c['wert'] == pytest.approx(np.sqrt(3.0)) and c['oben80'] == pytest.approx(np.sqrt(4.0 * k * k - 1.0))
    assert c['nachgewiesen'] and lgm.komponente(1.05, 1.0, 19, 'N', 'Test')['nachgewiesen'] is False
    assert lgm.komponente(0.5, 1.0, 19, 'N', 'Test')['wert'] == 0.0                   # abgeschnitten bei null
    assert k == pytest.approx(pilot.obere_grenze(1.0, 19))


# ── Profil, Pilotskript, Teil B ──────────────────────────────────────────────────────────────────────
def test_regel_gebunden_und_nur_im_aktuellen_stand(a4):
    m, tab, kal = a4
    s = pilot.satz_fuer_plan(tab, kal, AKTUELL, m.system.f, 9, 5)
    lg = s['laufgroessen']
    assert (lg['bindung']['k'], lg['bindung']['N_z'], lg['version']) == (9, 100, lgm.VERSION)
    assert s['bindung']['version'] == pilot.VERSION == 'pilot-0.4'
    pilot.pruefe_ausgabe(s)
    assert AKTUELL.wert('p0.laufgroessen') == lgm.REGELWERT
    h = pilot.satz_fuer_plan(tab, kal, HIST, m.system.f, 9, 5)
    assert 'laufgroessen' not in h and h['bindung']['version'] == 'pilot-0.3'
    # ein anderer Regelwert ist nicht umgesetzt: kein stiller Ersatzweg
    r = AKTUELL.eintrag('p0.laufgroessen')
    falsch = regeln.Regelprofil(AKTUELL.id, 'Test', [regeln.Regel(r.id, r.gegenstand, r.fundstelle, r.status,
                                                                    dict(r.wert, boden='Pilotläufe'), r.herkunft,
                                                                    r.wirkung) if x.id == r.id else x
                                                       for x in AKTUELL.regeln.values()], AKTUELL.reduktion)
    with pytest.raises(ValueError, match='nicht umgesetzt'):
        pilot.satz_fuer_plan(tab, kal, falsch, m.system.f, 9, 5)


def test_teil_b_felder_sigma_a_delta_off(a4):
    m, tab, kal = a4
    pe = pilot.pilot_auswerten(tab, kal, AKTUELL, m.system.f, seed=5)
    assert pe['version'] == 'pilot-0.4' and pe['laufgroessen']['bindung']['k'] == pe['k_pilotgroessen']
    pl = kette.plan_info(m, 18)
    tb = teil_b.erstellen(tab, kal, pe, AKTUELL, pl, kette.testvorgabe_werkzeug8(), seed_b0=1, B=50)
    n2 = tb['nr2']
    assert tb['version'] == 'teil_b-0.4' and n2['laufgroessen']['bindung'] == dict(
        n2['laufgroessen']['bindung'], k=9, N_z=100)
    for name in ('sigma_a_j', 'sigma_delta_j', 'sigma_off_j'):
        assert len(n2[name]['wert']) == 3 and len(n2[name]['nu']) == 3 and n2[name]['bindung'] == dict(k=9, N_z=100)
    assert n2['sigma_off_j']['wert'][0] == 0.0
    assert n2['sigma_a_j']['nu'] == [float(n - 1) for n in n2['laufgroessen']['bindung']['n0']]   # ν = n₀ⱼ − 1 (gültig)
    assert tb['nr10']['werte_regel']['planung_teil_b_werte'] == 'punktschaetzer'
    assert n2['phase0_bindung']['laufgroessen_quelle'] == 'mit dem Satz neu berechnet (Code des Pilotskripts)'
    # Pilotausgabe eines historischen Profils mit passendem Satz (k = 9): Laufgrößen in Teil B aus diesem Satz berechnet
    ph = pilot.pilot_auswerten(tab, kal, HIST, m.system.f, seed=5)
    s9 = pilot.satz_fuer_plan(tab, kal, HIST, m.system.f, 9, 5)
    ph = dict(ph, k_pilotgroessen=9, bindung=s9['bindung'], streuungen_volles_fenster=s9['streuungen'],
              **{x: s9[x] for x in pilot.SATZ_FELDER if x != 'streuungen'})
    tbx = teil_b.erstellen(tab, kal, ph, AKTUELL, pl, kette.testvorgabe_werkzeug8(), seed_b0=1, B=50)
    assert tbx['nr2']['phase0_bindung']['laufgroessen_quelle'].startswith('in Teil B')
    assert tbx['nr2']['sigma_a_j']['wert'] == pytest.approx(n2['sigma_a_j']['wert'])
    tbh = teil_b.erstellen(tab, kal, ph, HIST, pl, kette.testvorgabe_werkzeug8(), seed_b0=1, B=50)
    assert tbh['version'] == 'teil_b-0.3' and 'sigma_a_j' not in tbh['nr2'] and 'werte_regel' not in tbh['nr10']


# ── historisches Profil gleich main ──────────────────────────────────────────────────────────────────
def test_historisches_profil_gleich_main():
    """Unter ENTW-2026-10 und mit der historischen Anordnung (Stand bis PR #23) sind Pilotskript ohne und mit
    Planungshaken (Kalibrierung als Attrappe: Argumente und Protokoll des Hakens), Teil B und Satz beim k des Plans gleich
    der mit dem Code von main berechneten Referenz (tests/historisch_referenz.py: Vergleich mit Toleranz, Prüfsummen
    über Gleitkommadaten und die Codeversion ausgenommen; die letzten Bits hängen von der Rechenumgebung ab)."""
    import historisch_referenz as hr
    ref = hr.lies_referenz()['pilot_teil_b']
    neu = json.loads(json.dumps(hr.pilot_teil_b()))
    assert neu['ergebnis_suche'] == 'festgelegt' and neu['teil_b']['version'] == 'teil_b-0.3'
    abw = hr.vergleich(ref, neu)
    assert not abw, abw[:10]


def test_schaetzer_ohne_generator_harness_und_wahrheit():
    """Wahrheitstrennung: Der Schätzer (Teil des Pilotskripts) importiert weder Generator noch Harness noch Wahrheit
    und liest nur Laufzusammenfassungen."""
    import ast
    import os
    baum = ast.parse(open(lgm.__file__, encoding='utf-8').read())
    namen = set()
    for n in ast.walk(baum):
        if isinstance(n, ast.ImportFrom):
            namen.add(n.module or '')
            namen.update(a.name for a in n.names)
        elif isinstance(n, ast.Import):
            namen.update(a.name for a in n.names)
    assert not any('generator' in x or 'harness' in x or 'wahrheit' in x or 'szenari' in x for x in namen)
    assert os.path.basename(lgm.__file__) == 'laufgroessen.py'
