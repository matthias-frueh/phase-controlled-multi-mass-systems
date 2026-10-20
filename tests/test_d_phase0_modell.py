"""Teil d1/d2: Strukturmodell und Generator aus Phase 0 (generator.phase0_modell): Modus „bekannt“ bitgleich zum
Szenariogenerator, Parameter je Modul und Erweiterungen mit Wiedergewinnung, Rundreise Schätzer → Generator →
Schätzer über das Pilotskript, obere Grenzen je Komponente mit gemeinsamem Bodenfaktor, Strukturquellen, Modell ohne
Szenario, benannte Sensitivitäten, singuläre Kovarianzen.

Synthetische Phase-0-Daten; geprüft werden Schätz- und Dateikette, keine gemessenen Parameter."""
import numpy as np
import pytest

from pcmms_auswertung import formate, laufgroessen as lgm, pilot, regeln, zufall
from pcmms_auswertung import zusammenfassung as zf
from pcmms_auswertung.generator import ebene_h, kampagne as kp, phase0_modell as p0m, rauschen, systeme, szenarien
from pcmms_auswertung.generator import wahrheit
from pcmms_auswertung.harness import kette

PLAN = kp.Plan(n0=20, n_pilot=20, n_bloecke=4)
AKTUELL = regeln.profil('ENTW-2026-11').mit_reduktion(eps_ctrl_datensaetze=200)


def _gleich(a, b):
    return (formate.sha256_bytes(formate.npz_bytes(a.daten)) == formate.sha256_bytes(formate.npz_bytes(b.daten))
            and formate.sha256_json(a.koepfe) == formate.sha256_json(b.koepfe))


def _p0(laeufe):
    return [l for l in laeufe if l['phase'] == 0]


# ── Modus „bekannt“ ──────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize('sid', ['N01-A4', 'N04-laufart', 'N03-ungleich', 'A06-phase', 'A07-hertz50',
                                 'E07-basisdrift', 'I01-amplitude', 'S06-saettigung'])
def test_bekannt_bitgleich_zum_szenariogenerator(sid):
    """Gleiches Modell, gleiche Parameter, gleiche Anordnung, gleicher Strom: genau die Tabelle von ebene_h.erzeuge
    (Laufarten, Effekte, Hertz-Fall, Einstellung 2, Ereignisse)."""
    m = szenarien.modell(sid, 'L2', plan=PLAN)
    laeufe = kp.laufplan(m.plan, zufall.strom(3, 'reihenfolge'))
    a = ebene_h.erzeuge(m, laeufe, zufall.strom(3, 'generator'))
    b = p0m.erzeuge(m, laeufe, zufall.strom(3, 'generator'), p0m.aus_rauschmodell(m.rausch))
    c = p0m.erzeuge(m, laeufe, zufall.strom(3, 'generator'))                    # rauschen.Rauschmodell direkt
    assert _gleich(a, b) and _gleich(a, c)
    assert b.meta['generator']['erweiterungen'] == []


def test_je_modul_und_je_zelle_gleiche_werte_bitgleich():
    m = szenarien.modell('N01-A4', 'L2', plan=PLAN)
    laeufe = _p0(kp.laufplan(m.plan, zufall.strom(4, 'reihenfolge')))
    r = m.rausch
    st = p0m.aus_rauschmodell(r).mit(amp=(('L', (r.a('L'),) * 3), ('K', (r.a('K'),) * 3)),
                                     phase_grad=(('L', (r.p('L'),) * 3), ('K', (r.p('K'),) * 3)),
                                     jitter_grad=(r.jitter_grad,) * 2, index_versatz_grad=(r.index_versatz_grad,) * 2,
                                     sigma_zelle=(r.sigma_zelle,) * 3, sigma_h_zelle=(r.sigma_zelle,) * 3,
                                     sigma_m_zelle=(r.sigma_zelle,) * 3)
    a = ebene_h.erzeuge(m, laeufe, zufall.strom(4, 'generator'))
    b = p0m.erzeuge(m, laeufe, zufall.strom(4, 'generator'), st)
    assert _gleich(a, b) and 'je_modul' in st.erweiterungen()
    # anderer Wert eines Moduls: nicht mehr gleich
    d = p0m.erzeuge(m, laeufe, zufall.strom(4, 'generator'), st.mit(amp=(('L', (r.a('L'), 2 * r.a('L'), r.a('L'))),
                                                                          ('K', r.a('K')))))
    assert not _gleich(a, d)


# ── Wiedergewinnung je Modul und Erweiterungen ───────────────────────────────────────────────────────
def _modell_a4(st, plan=PLAN):
    s = systeme.system('A4')
    return p0m.Phase0Modell(p0m.struktur_system(s), plan, s.delta_profil_grad, 9, st)


def test_wiedergewinnung_je_modul_und_erweiterungen():
    """Bekannte Parameter je Modul (Amplitude, Phase, Versatz, Jitter, Boden je Zelle) und Erweiterungen (orthogonaler
    Rest, Zufallspfad des Nullpunkts, Laufdrift, Fünftelanteile) über 30 Phase-0-Sätze wiedergewonnen."""
    base = p0m.aus_rauschmodell(szenarien.modell('N01-A4', 'L2', plan=PLAN).rausch)
    rest = np.zeros((3, 3, 9))
    rest[1, :, :3] = 2e-4
    st = base.mit(amp=(('L', (0.01, 0.02, 0.005)), ('K', (0.01, 0.02, 0.005))),
                  phase_grad=(('L', (0.05, 0.1, 0.2)), ('K', (0.05, 0.1, 0.2))), jitter_grad=(0.1, 0.3),
                  index_versatz_grad=(0.03, 0.08), versatz_korrelation=0.4, rest_N=rest.tolist(),
                  nullpunkt_diffusion_N2_je_s=3e-10, lauf_drift_sd_N=3e-4, laufintern_amp_sd=(0.002, 0.004, 0.0),
                  laufintern_phase_sd_grad=(0.05, 0.0, 0.1), sigma_h_zelle=(0.010, 0.012, 0.014),
                  sigma_m_zelle=(0.02, 0.015, 0.01))
    m = _modell_a4(st)
    Ta = PLAN.n_zyklen / m.system.f
    r = []
    for i in range(30):
        laeufe = _p0(kp.laufplan(PLAN, zufall.strom(i, 'reihenfolge')))
        tab = p0m.erzeuge(m, laeufe, zufall.strom(i, 'generator'), rng_zusatz=zufall.strom(i, 'zusatz'))
        lg = lgm.schaetzen(tab, np.ones(len(tab), bool), 9)
        k = lgm.komponenten(lg)
        r.append(np.r_[k['sigma_a'], k['sigma_delta_grad'], k['sigma_off_grad'][1:], k['sigma_jitter_grad'][1:],
                       k['sigma_h_zellen'], lg['boden']['s2_m_summe'], lg['nullpunkt']['diffusion']['wert'],
                       [lg['module'][1]['rest'][i]['q'] for i in range(3)],
                       lg['laufintern']['mittel_N']['streuung']['wert'],
                       [lg['laufintern']['module'][j]['amplitude']['wert'] for j in range(3)],
                       [lg['laufintern']['module'][j]['phase']['wert'] for j in range(3)]])
    mw = np.array(r).mean(0)
    assert np.allclose(mw[0:3], (0.01, 0.02, 0.005), rtol=0.1)
    assert np.allclose(mw[3:6], (0.05, 0.1, 0.2), rtol=0.1)
    assert np.allclose(mw[6:8], (0.03, 0.08), rtol=0.1) and np.allclose(mw[8:10], (0.1, 0.3), rtol=0.02)
    assert np.allclose(mw[10:13], st.sigma_h(Ta), rtol=0.02)
    assert mw[13] == pytest.approx((np.asarray(st.sigma_mittel(Ta)) ** 2).sum(), rel=0.1)
    assert mw[14] == pytest.approx(3e-10, rel=0.4)                                  # schwach identifiziert
    q_wahr = 3 * 4e-8 / (np.asarray(st.sigma_h(Ta)) ** 2).sum()
    assert np.allclose(mw[15:18], q_wahr, rtol=0.15)
    assert mw[18] == pytest.approx(0.8 * 3e-4, rel=0.1)                             # D_N = 0,8·Laufdrift
    assert np.allclose(mw[19:21], (0.002, 0.004), rtol=0.1) and mw[21] < 3e-4
    assert mw[22] == pytest.approx(0.05, rel=0.1) and mw[24] == pytest.approx(0.1, rel=0.1) and mw[23] < 0.02


def test_zusatzstrom_ist_pflicht():
    st = p0m.Strukturparameter(lauf_drift_sd_N=1e-4)
    m = _modell_a4(st)
    laeufe = _p0(kp.laufplan(PLAN, zufall.strom(1, 'reihenfolge')))
    with pytest.raises(ValueError, match='rng_zusatz'):
        p0m.erzeuge(m, laeufe, zufall.strom(1, 'generator'))


# ── Rundreise über das Pilotskript ───────────────────────────────────────────────────────────────────
@pytest.fixture(scope='module')
def satz_a4():
    m = szenarien.modell('N01-A4', 'L2', plan=PLAN)
    tab = ebene_h.erzeuge(m, _p0(kp.laufplan(m.plan, zufall.strom(1, 'reihenfolge'))),
                          zufall.strom(1, 'generator')).sortiert()
    _, _, kal = kette.kalibrierung_erzeugen(szenarien.KATALOG['N01-A4'], m, 1)
    s = pilot.satz_fuer_plan(tab, kal, AKTUELL, m.system.f, 9, 1)
    ung = set(s['gueltigkeit']['gruende'])
    g = np.array([x['lauf_id'] not in ung for x in tab.koepfe])
    return m, tab, kal, s, g


def test_rundreise_schaetzer_generator_schaetzer(satz_a4):
    """Pilotskript (Satz bei k = 9) → Strukturmodell (Punktschätzer, Struktur aus P0.8) → 10 Phase-0-Sätze →
    Pilotskript: Komponenten, Boden, σ̂_ref und p̂ im Rahmen der Schätzunsicherheit wiedergewonnen; Kohärenz über k."""
    m, tab, kal, s1, g = satz_a4
    q = p0m.quelle_aus_phase0(tab, g, kal, s1['laufgroessen'], 'punkt')
    assert 'szenario' not in q.herkunft and q.herkunft['quelle'] == 'Phase 0'
    mm = q.modell(PLAN)
    k1 = lgm.komponenten(s1['laufgroessen'])
    r = []
    for i in range(10):
        laeufe = _p0(kp.laufplan(PLAN, zufall.strom(100 + i, 'reihenfolge')))
        t2 = p0m.erzeuge(mm, laeufe, zufall.strom(100 + i, 'generator'), rng_zusatz=zufall.strom(100 + i, 'z'))
        s2 = pilot.satz_fuer_plan(t2, kal, AKTUELL, m.system.f, 9, 1)
        k2 = lgm.komponenten(s2['laufgroessen'])
        koh = [s2['laufgroessen']['module'][j]['kohaerenz'][x]['p'] for j in range(3) for x in ('amplitude', 'phase')]
        r.append(np.r_[k2['sigma_a'], k2['sigma_delta_grad'], k2['sigma_off_grad'][1:], k2['sigma_h_zellen'],
                       s2['sigma_ref']['sigma_ref'], s2['p_hat'], min(koh)])
    r = np.array(r)
    mw = r.mean(0)
    soll = np.r_[k1['sigma_a'], k1['sigma_delta_grad'], k1['sigma_off_grad'][1:], k1['sigma_h_zellen']]
    assert np.allclose(mw[:8], soll[:8], rtol=0.2)                    # ν = 19 bzw. 55 je Satz, 10 Sätze
    assert np.allclose(mw[8:11], soll[8:11], rtol=0.03)
    assert mw[11] == pytest.approx(s1['sigma_ref']['sigma_ref'], rel=0.2)
    assert abs(mw[12] - s1['p_hat']) < 0.05 and (r[:, 13] < 1e-3).mean() <= 0.2


def test_obere_grenzen_je_komponente_mit_gemeinsamem_bodenfaktor(satz_a4):
    m, tab, kal, s1, g = satz_a4
    lg = s1['laufgroessen']
    o, pkt = p0m.aus_laufgroessen(lg, 'oben80'), p0m.aus_laufgroessen(lg, 'punkt')
    k = lgm.komponenten(lg)
    assert np.allclose(p0m._arr(o.a('L')), k['sigma_a_oben80']) and np.allclose(p0m._arr(pkt.a('L')), k['sigma_a'])
    assert np.allclose(p0m._arr(o.p('K')), k['sigma_delta_grad_oben80'])               # K wie L (Annahme)
    assert np.allclose(p0m._arr(o.index_versatz_grad, 2), k['sigma_off_grad_oben80'][1:])
    # Boden von ⟨N⟩: ein gemeinsamer Faktor κ(ν_m) für alle Zellen (und damit alle Laufarten)
    f = np.asarray(o.sigma_m_zelle) / np.asarray(pkt.sigma_m_zelle)
    assert np.allclose(f, lgm.kappa(lg['boden']['nu_m'])) and dict(o.herkunft)['faktor_boden_mittel'] == f[0]
    # Harmonischer Boden je Zelle mit eigenem ν (2·k·(n_R − 1))
    fh = np.asarray(o.sigma_h_zelle) / np.asarray(pkt.sigma_h_zelle)
    assert np.allclose(fh, lgm.kappa(lg['boden']['nu_h']))
    assert 'keine gemeinsame 80-%-Garantie' in dict(o.herkunft)['lesart']
    with pytest.raises(ValueError, match='unbekannt'):
        p0m.aus_laufgroessen(lg, 'oben95')


def test_familienanpassung_ist_szenariofamilie(satz_a4):
    m, tab, kal, s1, g = satz_a4
    lg = s1['laufgroessen']
    fam = p0m.familienanpassung(lg)
    k = lgm.komponenten(lg)
    assert isinstance(fam, rauschen.Rauschmodell)
    assert fam.a('L') == pytest.approx(np.sqrt(np.mean(k['sigma_a'] ** 2))) and fam.a('K') == fam.a('L')
    assert fam.jitter_grad == pytest.approx(np.sqrt(np.mean(k['sigma_jitter_grad'][1:] ** 2)))
    q = p0m.quelle_aus_phase0(tab, g, kal, lg, 'punkt', modell='familie')
    t = p0m.erzeuge(q.modell(PLAN), _p0(kp.laufplan(PLAN, zufall.strom(2, 'reihenfolge'))), zufall.strom(2, 'g'))
    assert t.meta['generator']['erweiterungen'] == []


# ── Strukturquellen, Modell ohne Szenario ────────────────────────────────────────────────────────────
def test_strukturquellen():
    m = szenarien.modell('N01-V1G0', 'L1', plan=PLAN)
    _, _, kal = kette.kalibrierung_erzeugen(szenarien.KATALOG['N01-V1G0'], m, 3)
    for f in (10.0, 8.0):                                                   # Arbeitspunkt und Kandidatenfrequenz
        b = p0m.struktur_kalibrierung(kal, f, 60)
        a = p0m.struktur_system(m.system, f=f)
        assert np.abs(b.Ns[:, :6] - a.Ns[:, :6]).max() <= 2e-3 * np.abs(a.Ns[:, :6]).max()
        assert np.allclose(b.F0, a.F0, rtol=1e-3)
    m4 = szenarien.modell('N01-A4', 'L1', plan=PLAN)
    _, _, kal4 = kette.kalibrierung_erzeugen(szenarien.KATALOG['N01-A4'], m4, 3)
    with pytest.raises(ValueError, match='f_n'):                           # starre Auflage: nur ausdrücklich H = 1
        p0m.struktur_kalibrierung(kal4, 10.0, 60)
    assert p0m.struktur_kalibrierung(kal4, 10.0, 60, starr=True).herkunft['starr'] is True
    tab = ebene_h.erzeuge(m, _p0(kp.laufplan(m.plan, zufall.strom(3, 'r'))), zufall.strom(3, 'g'))
    s = p0m.struktur_p08(tab, np.ones(len(tab), bool))
    art, mod = tab.spalte('laufart', object), tab.spalte('modul', object)
    assert np.allclose(s.Nz[1], tab.daten['Nk_zellen'][(art == 'L') & (mod == 2)].mean(0))
    assert s.herkunft['n0'] == [20, 20, 20]


def test_phase0modell_ohne_szenario_exakte_superposition(satz_a4):
    m, tab, kal, s1, g = satz_a4
    q = p0m.quelle_aus_phase0(tab, g, kal, s1['laufgroessen'], 'punkt')
    mm = q.modell(PLAN.mit(n_bloecke=2))
    assert mm.szenario is None and mm.system.name == q.name
    w, _ = wahrheit.berechne(mm, kp.schnitt_konfigurationen(mm.plan))
    assert w['klasse'] == 'R0'
    with pytest.raises(ValueError, match='exakten Superposition'):
        q.modell(PLAN, effekte=({'art': 'kopplung', 'x': 0.01},))
    with pytest.raises(ValueError, match='Einstellung 2'):
        q.modell(PLAN.mit(einstellung2=dict(art='amplitude', s=0.5, punkte_I=(116.0,))))
    k1, k2 = q.kennung(), q.mit(rausch=q.rausch.mit(jitter_grad=0.3)).kennung()
    assert k1['sha256'] != k2['sha256'] and 'szenario' not in k1['beschreibung']['herkunft']


def test_optionales_feld_fuenftelzeiger():
    """Führt das Format das optionale Feld fuenftel_zeiger, füllt der Generator es (Modul 1: n_f, nicht laufende
    Module nan); sonst bleibt die Tabelle wie bisher."""
    m = szenarien.modell('N01-A4', 'L2', plan=PLAN)
    laeufe = [l for l in kp.laufplan(m.plan, zufall.strom(5, 'r')) if l['phase'] == 0][:12]
    st = p0m.parameter(m.rausch)
    daten = zf.leere_daten(m.k_voll, len(laeufe))
    daten['fuenftel_zeiger'] = np.full((len(laeufe), 2, 3), np.nan + 0j)
    rng = zufall.strom(5, 'g')
    for idx in ebene_h._gruppen(laeufe):
        z = p0m._ziehen(m, [laeufe[i] for i in idx], rng, st, None)
        p0m._bilden(m, z, np.arange(len(idx)), np.zeros(len(idx)), daten, idx)
    nf = PLAN.n_zyklen // 5
    for i, l in enumerate(laeufe):
        fz = daten['fuenftel_zeiger'][i]
        if l['laufart'] == 'K':
            assert np.allclose(fz[:, 0], nf) and np.isfinite(fz).all()
        elif l['laufart'] == 'L':
            j = l['modul'] - 1
            assert np.allclose(fz[:, j], nf) and np.isnan(np.delete(fz, j, 1)).all()
        else:
            assert np.isnan(fz).all()


# ── benannte Sensitivitäten ──────────────────────────────────────────────────────────────────────────
def test_benannte_sensitivitaeten_feste_staerken():
    base = p0m.aus_rauschmodell(szenarien.modell('N01-A4', 'L2', plan=PLAN).rausch)
    m = _modell_a4(base)
    laeufe = kp.laufplan(PLAN.mit(n_bloecke=1), zufall.strom(6, 'r'))
    ref = p0m.erzeuge(m, laeufe, zufall.strom(6, 'g'))
    art = ref.spalte('laufart', object)
    assert p0m.regeln_pruefen(AKTUELL, sensitivitaeten=True)
    for name in p0m.SENSITIVITAETEN:
        st, eff = p0m.sensitivitaet(base, name, plan=PLAN, f=10.0)
        assert dict(st.herkunft)['sensitivitaet'] == name
        mm = _modell_a4(st)
        if eff:
            mm = p0m.Phase0Modell(m.struktur, PLAN.mit(n_bloecke=1), systeme.system('A4').delta_profil_grad, 9, st,
                                  effekte=eff)
        t = p0m.erzeuge(mm, laeufe, zufall.strom(6, 'g'), rng_zusatz=zufall.strom(6, 'z'))
        if name in ('jitter_farbig', 'jitter_korreliert', 'jitter_lastabhaengig', 'phasendrift_lauf',
                    'kombination_doppelt', 'laufzeit_gemeinsam'):
            # nur Kombinationsläufe betroffen, gleicher Hauptstrom: R- und Lⱼ-Läufe bitgleich
            nk = art != 'K'
            assert np.array_equal(t.daten['Nk_zellen'][nk], ref.daten['Nk_zellen'][nk])
            assert not np.array_equal(t.daten['Nk_zellen'][~nk], ref.daten['Nk_zellen'][~nk]), name
        elif name == 'amplitude_doppelt':
            l = art == 'L'
            assert not np.array_equal(t.daten['Nk_zellen'][l], ref.daten['Nk_zellen'][l])
        elif name == 'drift_phase1':                                       # nur Phase 1, Phase 0 bitgleich
            p1 = ref.spalte('phase', int) == 1
            assert np.array_equal(t.daten['Nk_zellen'][~p1], ref.daten['Nk_zellen'][~p1])
            b = p1 & (art != 'R')
            assert not np.array_equal(t.daten['Nk_zellen'][b], ref.daten['Nk_zellen'][b])
        else:                                                               # Nullpunkt: ⟨N⟩ ändert sich
            assert name == 'nullpunkt_diffusion' and not np.array_equal(t.daten['N_mittel'], ref.daten['N_mittel'])
    with pytest.raises(ValueError, match='unbekannt'):
        p0m.sensitivitaet(base, 'jitter_rosa')


# ── singuläre Kovarianzen ────────────────────────────────────────────────────────────────────────────
def test_singulaere_kovarianz_unterraum_und_regularisierung():
    """Empirische Kovarianz aus weniger Läufen als Dimensionen (Rang n − 1): Ziehung im Unterraum reproduziert sie,
    Cholesky scheitert, die Regularisierung mit dem Boden macht sie positiv definit."""
    rng = np.random.default_rng(1)
    d, n = 57, 20
    X = rng.standard_normal((n, d)) @ np.diag(np.linspace(0.5, 2.0, d))
    C = np.cov(X, rowvar=False)
    assert np.linalg.matrix_rank(C) == n - 1
    with pytest.raises(np.linalg.LinAlgError):
        np.linalg.cholesky(C)
    Z, ber = p0m.gauss_unterraum(C, 40000, np.random.default_rng(2))
    assert ber['rang'] == n - 1 and ber['dimension'] == d and np.linalg.matrix_rank(Z[:200]) == n - 1
    assert np.abs(np.cov(Z, rowvar=False) - C).max() < 0.05 * np.abs(C).max()
    Cr, b2 = p0m.regularisieren(C, 0.01)
    assert b2['rang_nachher'] == d and b2['min_eigenwert'] > 0
    np.linalg.cholesky(Cr)
    with pytest.raises(ValueError):
        p0m.regularisieren(C, 0.0)
