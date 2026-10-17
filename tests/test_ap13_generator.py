"""Etappe 2: AP-13 als Datenlieferant – Bezugssysteme, Physik-Gegenproben (analytisch, linear_solver, Aufbau,
ereignisgenauer Löser), Kampagnenplan, Ebene H und Z, synthetische P0-Daten, Wahrheit und Szenarienkatalog.

Langsame Prüfungen (@slow) laufen nur mit PCMMS_SLOW=1."""
import json
import os
import warnings

import numpy as np
import pytest

from pcmms_auswertung import formate, konventionen as kv, rohdaten, zusammenfassung as zf
from pcmms_auswertung.generator import (ebene_h, ebene_z, kalibrierdaten, kampagne, physik, rauschen, szenarien,
                                        systeme, wahrheit)
from pcmms_auswertung.generator.modell import Generatormodell

LANGSAM = os.environ.get('PCMMS_SLOW') == '1'
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    _SLOW = pytest.mark.slow


def slow(f):
    return _SLOW(pytest.mark.skipif(not LANGSAM, reason='langsam; mit PCMMS_SLOW=1 aktivieren')(f))


# ── Physik-Gegenproben ───────────────────────────────────────────────────────────────────────────────
def test_starre_auflage_g0_analytisch():
    """A4 (starr, G0): Zellharmonische = m_j·a_k⁽ʲ⁾ in Zelle j aus dem geschlossen integrierten Egg-Profil."""
    r = physik.gegenprobe_starr_g0()
    assert r['abw_N'] < 1e-6
    assert r['abw_profil'] < 1e-5
    assert r['F0_abw'] < 1e-12


def test_egg_fourier_grenzfall_und_reell():
    """Geschlossene Fourier-Koeffizienten: Grenzfall α = π/L stetig, Mittelwert der Beschleunigung null."""
    from pcmms_auswertung.generator.systeme import auslegung
    Th = auslegung.THOLD
    s = np.linspace(0, 1, 200001)[:-1]
    a = np.where(s < Th, -np.pi ** 2 / Th * np.sin(np.pi * s / Th), np.pi ** 2 / (1 - Th) * np.sin(np.pi * (s - Th) /
                                                                                                    (1 - Th)))
    for k in (1, 2, 3, 7):
        num = (a * np.exp(-2j * np.pi * k * s)).mean()
        assert abs(physik.egg_fourier(k, Th)[0] - num) < 1e-6 * np.pi ** 2
    assert abs(a.mean()) < 1e-9
    assert abs(physik.egg_fourier(1 / (2 * 0.5), 0.5)[0] - physik.egg_fourier(1 / (2 * 0.5) + 1e-9, 0.5)[0]) < 1e-6


def test_abgleich_linear_solver():
    """Summe der Generatorantworten (Superposition der 3-FG-Einzelmodulantworten) gegen linear_solver."""
    r = physik.abgleich_linear_solver()
    assert r['abw_harmonische_N'] < 1e-10
    assert r['abw_F_min_N'] < 1e-4                    # Bandbegrenzung k ≤ 60 gegen volles Spektrum


@pytest.mark.parametrize('name', ['V1-G0', 'V1-G60h'])
def test_frf_gleich_aufbau_uebertragung(name):
    """systeme.frf (P0.4-Daten) und auslegung.Aufbau._uebertragung beschreiben dieselbe 3-FG-Dynamik."""
    s = systeme.system(name)
    a = s.aufbau()
    _, T = a._uebertragung()
    f = a.w[1:40] / (2 * np.pi)
    for j in range(3):
        Tg = systeme.frf(s, f, a.module[j], mit_kette=False)
        assert np.abs(Tg - T[1:40, :, j].T).max() <= 1e-12 * np.abs(T[1:40]).max()


def test_kraftkette_wirkt_auf_harmonische():
    """Lineare Kette: N_c,k = G_F,c(kω)·N_c,k (Kraft); G(0) = 1."""
    kette = systeme.Kette(f_tp=(200.0, 180.0, 220.0), tau=(2e-4, 2.5e-4, 1.5e-4))
    s = systeme.system('V1-G0', kette=kette)
    ant = systeme.antworten(s)
    k = np.arange(1, ant.k_voll + 1)
    assert np.allclose(ant.Nz, ant.Nz_kraft * kette.G(s.f * k)[None], rtol=0, atol=1e-15)
    assert np.allclose(kette.G([0.0]), 1.0)


# ── Kampagnenplan ────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize('n,d,e2', [(20, 1, False), (8, 2, False), (6, 1, True)])
def test_laufzahlen_a9_12(n, d, e2):
    """Phase 1: (N_K + 5)·n + 5·d, mit Einstellung 2 (N_K + N_I + 8)·n + 8·d (A9.12), zuzüglich je Messtag des
    letzten Aufwärm-Referenzlaufs; Phase 0: P0.7 mindestens 42 Referenzläufe."""
    plan = kampagne.Plan(n_bloecke=n, tage=d, einstellung2=dict(art='amplitude', s=0.5, punkte_I=(116.0, 120.0, 124.0))
                         if e2 else None)
    laeufe = kampagne.laufplan(plan, np.random.default_rng(1))
    p1 = [l for l in laeufe if l['phase'] == 1]
    NK, NI = 21, (3 if e2 else 0)
    soll = ((NK + NI + 8) * n + 8 * d) if e2 else ((NK + 5) * n + 5 * d)
    assert len(p1) == soll + d
    p0 = [l for l in laeufe if l['phase'] == 0]
    assert sum(l['laufart'] == 'R' for l in p0) >= 42
    assert [l['position'] for l in laeufe] == list(range(len(laeufe)))
    t = np.array([l['t_start'] for l in laeufe])
    assert np.all(np.diff(t) > 0)
    # jede Konfiguration genau einmal je Block, Referenzlauf nach der zwölften Konfiguration
    for b in range(1, n + 1):
        blk = [l for l in p1 if l['block'] == b and l['laufart'] == 'K']
        assert sorted(l['konfiguration']['id'] for l in blk) == sorted(kampagne.konfigurationsliste(plan))


def test_konfigurationsliste_reihenfolge():
    plan = kampagne.Plan(zusatz=True, einstellung2=dict(art='frequenz', f2=7.0, punkte_I=(116.0, 120.0, 124.0)))
    ids = kampagne.konfigurationsliste(plan)
    assert ids[:21] == [f'S{p:g}' for p in kv.SCHNITT_PHI2]
    assert ids[21:] == ['Z0_0', 'Z0_180', 'I116′', 'I120′', 'I124′']


def test_s3_bilder_im_plan():
    plan = kampagne.Plan(pruef=((105.0, 247.0),))
    k = [x for x in kampagne.schnitt_konfigurationen(plan) if x['konfiguration']['gruppe'] == 'pruef']
    assert len(k) == 6
    assert all(x['konfiguration']['phi_soll_grad'][0] == 0.0 for x in k)


# ── Ebene H ──────────────────────────────────────────────────────────────────────────────────────────
def _tab(m, seed=3):
    laeufe = kampagne.laufplan(m.plan, np.random.default_rng(seed))
    return laeufe, ebene_h.erzeuge(m, laeufe, np.random.default_rng(seed + 100))


def test_ebene_h_rauschfrei_superposition_und_struktur():
    """Rauschfrei: Kombinationslauf = Σⱼ e^{−ikφⱼ}·Lⱼ (Indexphasen = Profilphasen − Δδⱼ), Zellen und Summe."""
    s = szenarien.KATALOG['N03-ungleich'].system()
    m = Generatormodell(s, rauschen.RAUSCHFREI, kampagne.Plan(n0=2, n_pilot=1, n_bloecke=1))
    laeufe, tab = _tab(m)
    k = np.arange(1, m.k_voll + 1)
    L = {l['modul']: i for i, l in enumerate(laeufe) if l['laufart'] == 'L' and l['phase'] == 0}
    for i, l in enumerate(laeufe):
        if l['laufart'] != 'K':
            continue
        phi = m.index_soll_grad(l['konfiguration']['phi_soll_grad'])
        Z = kv.zeigerfaktor(phi, k)
        sup = sum(Z[j][None] * tab.daten['Nk_zellen'][L[j + 1]] for j in range(3))
        assert np.abs(tab.daten['Nk_zellen'][i] - sup).max() < 1e-12
        assert np.allclose(tab.daten['zeiger'][i], m.plan.n_zyklen * Z, atol=1e-9)
    zf.pruefe_daten(tab.daten, m.k_voll, len(laeufe))
    for kopf in tab.koepfe:
        zf.pruefe_kopf_lauf(kopf)
    assert np.isnan(tab.daten['zeiger'][L[1], 1]).all() and not np.isnan(tab.daten['zeiger'][L[1], 0]).any()


def test_ebene_h_weisses_rauschen_streuung():
    """Weißes Rauschen: Var(Re N_c,k) = σ_h², Var⟨N_c⟩ = σ_m² (Einzelmodulläufe, sonst rauschfrei)."""
    r = rauschen.RAUSCHFREI.mit(name='weiss', sigma_zelle=0.05)
    m = Generatormodell(systeme.system('A4'), r, kampagne.Plan(n0=400, n_pilot=1, n_bloecke=1))
    laeufe, tab = _tab(m)
    i = [j for j, l in enumerate(laeufe) if l['laufart'] == 'L' and l['modul'] == 2 and l['phase'] == 0]
    T_a = m.plan.n_zyklen / m.system.f
    x = tab.daten['Nk_zellen'][i][:, :, :3]
    v = np.r_[x.real.var(0, ddof=1).ravel(), x.imag.var(0, ddof=1).ravel()] / r.sigma_h(T_a) ** 2
    assert abs(v.mean() - 1) < 0.05 and v.min() > 0.75 and v.max() < 1.25
    vm = tab.daten['N_mittel_zellen'][i].var(0, ddof=1) / r.sigma_mittel(T_a) ** 2
    assert np.all(np.abs(vm - 1) < 0.25)


def test_ebene_h_amplitude_und_phase_je_laufart():
    """Getrennte Lauf-Streuungen: relative Streuung von |N₁| = a(Laufart), Phasenstreuung ≈ p(Laufart)."""
    r = rauschen.getrennt('t', 0.01, 0.03, 0.1, 0.3, sigma_zelle=0.0, jitter_grad=0.0, index_versatz_grad=0.0)
    m = Generatormodell(systeme.system('A4'), r, kampagne.Plan(n0=300, n_pilot=1, n_bloecke=300))
    laeufe, tab = _tab(m)
    iL = [j for j, l in enumerate(laeufe) if l['laufart'] == 'L' and l['modul'] == 1]
    a = np.abs(tab.daten['Nk_summe'][iL, 0])
    assert abs(a.std(ddof=1) / a.mean() / 0.01 - 1) < 0.15
    ph = np.degrees(np.angle(tab.daten['Nk_summe'][iL, 0] / tab.daten['Nk_summe'][iL, 0].mean()))
    assert abs(ph.std(ddof=1) / 0.1 - 1) < 0.15
    iK = [j for j, l in enumerate(laeufe) if l['konfiguration']['id'] == 'S120']
    aK = np.abs(tab.daten['Nk_summe'][iK, 0])
    # Summe dreier Module mit je 3 % (S120: Grundwellen heben sich teilweise auf, daher nur Größenordnung)
    assert aK.std(ddof=1) / aK.mean() > 0.02


def test_ebene_h_reproduzierbar_und_seedabhaengig():
    m = szenarien.modell('N01-A4', 'L2', plan=kampagne.Plan(n0=3, n_pilot=2, n_bloecke=2))
    h = []
    for seed in (5, 5, 6):
        laeufe = kampagne.laufplan(m.plan, np.random.default_rng(seed))
        tab = ebene_h.erzeuge(m, laeufe, np.random.default_rng(seed))
        h.append(formate.sha256_bytes(formate.npz_bytes(tab.daten)))
    assert h[0] == h[1] and h[0] != h[2]


def test_ebene_h_ereignisse_nach_auswahl():
    m = szenarien.modell('S06-saettigung', 'L1', plan=kampagne.Plan(n0=3, n_pilot=2, n_bloecke=2))
    laeufe, tab = _tab(m)
    ue = tab.daten['uebersteuert_zellen']
    treffer = [(laeufe[i]['konfiguration']['id'], laeufe[i]['phase'], c) for i, c in zip(*np.nonzero(ue))]
    assert sorted(treffer) == [('L1', 0, 2), ('S120', 1, 2)]
    # die Summe bleibt unauffällig: dieselben Harmonischen wie ohne Ereignis
    m0 = szenarien.modell('N01-A4', 'L1', plan=m.plan)
    _, tab0 = _tab(m0)
    assert np.array_equal(tab.daten['Nk_summe'], tab0.daten['Nk_summe'])


# ── Ebene Z ──────────────────────────────────────────────────────────────────────────────────────────
def test_abtastrate_aus_a6():
    assert ebene_z.abtastrate(10.0, 9) == pytest.approx(6330.0)
    assert ebene_z.abtastrate(10.0, 12) == pytest.approx(8430.0)
    fs = ebene_z.abtastrate(7.0, 12)
    assert (np.pi * 12 * 7.0 / fs) ** 2 / 2 <= 1e-3


def _fenster_harmonische(inhalt, daten, kalib, kmax):
    """Einfache Gegenprobe ohne AP-12: Fenster ab dem ersten Bezugsindex nach t_e, lineare Interpolation je Zyklus
    auf N_θ, Mittelkurve, DFT."""
    fs, t0 = inhalt['erfassung']['f_s'], inhalt['erfassung']['t0']
    F = (daten['kraft_adc'] - np.asarray(kalib['nullpunkt_adc'])[:, None]) * np.asarray(
        kalib['empfindlichkeit_N_je_adc'])[:, None]
    t = t0 + np.arange(F.shape[1]) / fs
    idx = daten[f'index_modul{inhalt["lauf"]["modul"] or 1}']            # θ = 0 am Index von Modul 1 bzw. j
    n = inhalt['protokoll']['n_zyklen_fenster']
    T_w0 = inhalt['protokoll']['t_rampe_ende'] + inhalt['protokoll']['t_e']
    start = int(np.searchsorted(idx, T_w0 - 0.25 / inhalt['erfassung']['f_soll']))
    th = np.arange(kv.N_THETA) / kv.N_THETA
    kurven = []
    for c in range(n):
        a, b = idx[start + c], idx[start + c + 1]
        kurven.append(np.array([np.interp(a + th * (b - a), t, F[z]) for z in range(3)]))
    x = np.mean(kurven, 0)
    return kv.harmonische(x, kmax), x.mean(-1)


def test_ebene_z_rauschfrei_gleich_ebene_h(tmp_path):
    """Rauschfreie Rohzeitreihe → Fensterharmonische wie Ebene H mit denselben Ziehungen (Kombinations- und
    Einzelmodullauf, A4 mit ungleichem Modul 2)."""
    s = systeme.system('A4', m=(0.0867, 0.0880, 0.0867), delta_profil_grad=(0.0, 0.3, 0.0))
    m = Generatormodell(s, rauschen.RAUSCHFREI, kampagne.Plan(n0=1, n_pilot=1, n_bloecke=1, n_zyklen=10))
    laeufe = kampagne.laufplan(m.plan, np.random.default_rng(2))
    wahl = [l['position'] for l in laeufe if l['konfiguration']['id'] in ('S112', 'L2')][:2]
    kalib = dict(nullpunkt_adc=[1000.0, -2000.0, 500.0], empfindlichkeit_N_je_adc=[1e-6, 1.1e-6, 0.9e-6])
    zeilen, sig = ebene_z.erzeuge(m, laeufe, np.random.default_rng(3), str(tmp_path), formate.synth_kennung('T'),
                                  kalib, nur=wahl)
    tab = ebene_h.erzeuge(m, laeufe, np.random.default_rng(4))
    assert len(zeilen) == 2
    for z in zeilen:
        _, inhalt, daten = rohdaten.lies_rohlauf(os.path.join(str(tmp_path), z['lauf_id']))
        Nk, mittel = _fenster_harmonische(inhalt, daten, kalib, 9)
        i = inhalt['lauf']['position']
        assert np.abs(Nk - tab.daten['Nk_zellen'][i, :, :9]).max() < 2e-5
        assert np.abs(mittel - tab.daten['N_mittel_zellen'][i]).max() < 2e-5


def test_ebene_z_ereignisse(tmp_path):
    m = szenarien.modell('S-indexfehler', 'L1', plan=kampagne.Plan(n0=1, n_pilot=1, n_bloecke=1, n_zyklen=10))
    laeufe = kampagne.laufplan(m.plan, np.random.default_rng(2))
    pos = [l['position'] for l in laeufe if l['konfiguration']['id'] == 'S110' and l['phase'] == 1][:1]
    kalib = dict(nullpunkt_adc=[0.0, 0.0, 0.0], empfindlichkeit_N_je_adc=[1e-6, 1e-6, 1e-6])
    zeilen, _ = ebene_z.erzeuge(m, laeufe, np.random.default_rng(3), str(tmp_path), formate.synth_kennung('T'),
                                kalib, nur=pos)
    _, inhalt, daten = rohdaten.lies_rohlauf(os.path.join(str(tmp_path), zeilen[0]['lauf_id']))
    d1, d2 = np.diff(daten['index_modul1']), np.diff(daten['index_modul2'])
    assert d1.max() < 1.5 / inhalt['erfassung']['f_soll'] and d2.max() > 1.5 / inhalt['erfassung']['f_soll']


# ── synthetische P0-Daten ────────────────────────────────────────────────────────────────────────────
def test_p01_statik_und_kalibrierung():
    s = systeme.system('V1-G60h')
    mes, wahr = kalibrierdaten.p01_daten(s, np.random.default_rng(1), sigma_adc=0.0, sigma_lage_N=0.0,
                                         zelllage_fehler=[[1e-3, 0.0], [0.0, 0.0], [0.0, -5e-4]])
    for c, e in enumerate(mes['einzeln']):
        assert np.allclose(e['adc'], wahr['nullpunkt_adc'][c] + e['last_N'] / wahr['empfindlichkeit_N_je_adc'][c])
    ls = mes['laststellen']
    for o, dN in zip(ls['orte_m'], ls['delta_N']):
        assert dN.sum() == pytest.approx(ls['last_N'])
        assert dN @ wahr['zellen_m'] == pytest.approx(ls['last_N'] * o, abs=1e-12)


def test_p04_rauscharm_gleich_frf():
    s = systeme.system('V1-G0')
    mes, wahr = kalibrierdaten.p04_daten(s, np.random.default_rng(1), rauschpegel=1e-12)
    d = mes['daten']['mitte@1']
    T = systeme.frf(s, mes['f_hz'], (0.0, 0.0))
    assert np.abs(d['T'][:3] - T).max() < 1e-8 * np.abs(T).max()
    assert d['kohaerenz'].min() > 0.999999
    assert wahr['f_n'] == pytest.approx(s.aufbau().f_n)


def test_p05_weg_harmonische():
    s = systeme.system('V1-G0', delta_profil_grad=(0.0, 0.4, -0.2))
    Gx = dict(f_tp=3000.0, tau=30e-6, gain=1.01)
    mes, wahr = kalibrierdaten.p05_daten(s, np.random.default_rng(1), sigma_weg_m=0.0, jitter_grad=0.0, G_x=Gx)
    k = np.arange(1, 13)
    f = mes['f_hz']
    for j, mod in enumerate(mes['module']):
        t, x = mod['t_s'], mod['weg_m']
        n = int(round(mes['f_s'] / f))
        sel = t < t[0] + 40 / f
        X = 2 * np.exp(-2j * np.pi * np.outer(k, t[sel] * f)) @ x[sel] / sel.sum()
        Gk = Gx['gain'] * np.exp(-1j * k * 2 * np.pi * f * Gx['tau']) / (1 + 1j * k * f / Gx['f_tp'])
        assert np.abs(X[:3] - (wahr['X'][j] * Gk)[:3]).max() < 2e-3 * np.abs(wahr['X'][j, 0]), n
    assert np.allclose(wahr['delta_delta_grad'], [0.0, 0.4, -0.2], atol=1e-9)


# ── Wahrheit und Katalog ─────────────────────────────────────────────────────────────────────────────
def _wahr(sid, **kw):
    m = szenarien.modell(sid, 'L2', **kw)
    return m, wahrheit.berechne(m, kampagne.schnitt_konfigurationen(m.plan))


@pytest.mark.parametrize('sid', ['N01-A4', 'N01-V1G0', 'N01-V1G60h', 'N03-ungleich', 'N03-N3bindet', 'E04-kette',
                                 'C04-steif', 'F03-S3ungleich'])
def test_lineare_szenarien_exakt(sid):
    _, (out, felder) = _wahr(sid)
    assert out['klasse'] == 'R0' and out['r_max_rel_yhat0'] < 1e-12 and out['r_max_rel_yhat1'] < 1e-12


@pytest.mark.parametrize('sid,klasse,ziel', [('A04-R1', 'R1', 0.5), ('A04-R2', 'R2', 1.0), ('A04-R3', 'R3', 1.5),
                                             ('A04-R4', 'R4', 2.5), ('N05-F', 'R2', 1.0), ('N05-N2', 'R2', 1.0),
                                             ('N05-N3', 'R2', 1.0)])
def test_klassen_nach_zielverhaeltnis(sid, klasse, ziel):
    m, (out, _) = _wahr(sid)
    assert out['klasse'] == klasse
    assert out['r_max_rel_beide'] == pytest.approx(ziel, rel=1e-8)


def test_kopplung_a4_wie_plan_n05():
    """Plan N05: F_min genau an Δ_q bei Kopplung 10,638 % im A4 (Kopplung linear: r = x·|F_rel(ŷ)|)."""
    x, r = szenarien.staerke_suchen('N05-F')
    assert x == pytest.approx(0.10638, abs=5e-5)


def test_n3_bindet_unter_fassung_b():
    """N03-N3bindet: kleinstes Δ_q unter Fassung B bei Re/Im N₃, unter Fassung A nicht."""
    _, (out, felder) = _wahr('N03-N3bindet')
    dB, dA = felder['Delta_B'], felder['Delta_A']
    assert np.argmin(dB) in (5, 6) and np.argmin(dA) not in (5, 6)


def test_drift_nur_gegen_yhat0():
    for sid in ('E07-verstaerkung', 'E07-basisdrift'):
        _, (out, _) = _wahr(sid)
        assert out['r_max_rel_yhat0'] > 0.05 and out['r_max_rel_yhat1'] < 1e-12 and out['klasse'] == 'R0'


def test_s01a_zellminimum_bei_schwelle():
    m, (out, _) = _wahr('S01a-liftoff')
    assert out['zellminimum_min_N'] == pytest.approx(3 * m.rausch.sigma_zelle, rel=1e-6)
    # die Summe bleibt weit im Kontakt
    assert m.antwort().MG + min(kv.kurve(physik.superposition(m.antwort(), m.index_soll_grad((0, p, 240.0)))).min()
                                for p in kv.SCHNITT_PHI2) > 1.0


def test_wahrheit_getrennt_gespeichert(tmp_path):
    m, (out, felder) = _wahr('A04-R1')
    k = formate.synth_kennung('T')
    p = str(tmp_path / 'wahrheit' / 'A04-R1')
    wahrheit.speichern(p, m, out, felder, k, 'A04-R1')
    kk, inhalt, f2 = wahrheit.laden(p)
    assert inhalt['klasse'] == 'R1' and np.array_equal(f2['r0_wahr'], felder['r0_wahr'])
    with pytest.raises(formate.FormatFehler):
        formate.lies(p, 'zusammenfassungen')


def test_katalog_vollstaendig_und_serialisierbar():
    tab = szenarien.katalog_tabelle()
    json.dumps(tab)
    ids = [t['id'] for t in tab]
    assert len(ids) == len(set(ids))
    pflicht = {'N01', 'N03', 'A04', 'N05', 'E07', 'I01', 'I02', 'A07', 'C03', 'F01', 'F03', 'H01', 'S01a', 'S06'}
    assert pflicht <= {t['plan_id'] for t in tab} | {p for t in tab for p in t['plan_id'].split('/')}
    for t in tab:
        assert t['art'] in szenarien.ARTEN
    b = szenarien.beschreibung(szenarien.modell('I02-amplitude', 'L1'))
    json.dumps(b)
    assert b['effekte'][0]['beta'] == 2e-3 and b['plan']['einstellung2']['s'] == 0.5


def test_hertz_fall_klein():
    """Ereignisgenauer Löser (Hunt-Crossley): Dauerkontakt, Mittelkraft = M·g, Residuum gegen die Superposition
    ungleich null und klein gegen die Antwort; zwei Konfigurationen."""
    r = physik.hertz_fall(konfigurationen={'S120': (120.0, 240.0), 'S100': (100.0, 240.0)})
    for kid, inf in r['info'].items():
        assert inf['t_flug'] == 0.0
        assert inf['mittel'] == pytest.approx(r['modell']['M'] * systeme.G, rel=1e-8)
    for kid, res in r['residuum'].items():
        a = np.abs(r['kombination'][kid][:9]).max()
        assert 1e-6 * a < np.abs(res[:9]).max() < 0.2 * a


@slow
def test_hertz_szenario_wahrheit():
    m, (out, felder) = _wahr('A07-hertz50')
    assert out['klasse'] in ('R1', 'R2', 'R3', 'R4')
    assert np.abs(felder['r0_wahr'][:, 0]).max() == pytest.approx(0.135, abs=0.01)
