"""Etappe 3: AP-11 – Anpassverfahren P0.1, P0.2, P0.4, P0.5 (Werkzeug 4) und Pilotskript (Werkzeug 5) an
unabhängig erzeugten synthetischen Phase-0-Daten: Parameter, Profilphasen, Unsicherheiten (Überdeckung über mehrere
feste Seeds), Modellabweichungen, nicht identifizierbare und bandfremde Fälle, Ausgabe ohne Residuen/Entscheidungen."""
import ast
import os

import numpy as np
import pytest

from pcmms_auswertung import anpassung, formate, gueltigkeit, pilot, regeln
from pcmms_auswertung.generator import ebene_h, kalibrierdaten, kampagne, szenarien, systeme

CODE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'code', 'pcmms_auswertung')
SEEDS = range(101, 141)


def _z(schaetz, wahr, u):
    return (np.asarray(schaetz) - np.asarray(wahr)) / np.asarray(u)


def _streuung_ok(z, lo=0.7, hi=1.35):
    z = np.ravel(z)
    return lo < z.std(ddof=1) < hi and abs(z.mean()) < 4 * z.std(ddof=1) / np.sqrt(z.size) + 0.15


# ── P0.1 ─────────────────────────────────────────────────────────────────────────────────────────────
def test_p01_kennlinie_und_ueberdeckung():
    s = systeme.system('V1-G0')
    z0, zs = [], []
    for seed in SEEDS:
        mes, w = kalibrierdaten.p01_daten(s, np.random.default_rng(seed), sigma_adc=3.0)
        for c in range(3):
            r = anpassung.p01_zelle(mes['einzeln'][c])
            z0.append(_z(r['nullpunkt_adc'], w['nullpunkt_adc'][c], r['u_nullpunkt_adc']))
            zs.append(_z(r['empfindlichkeit_N_je_adc'], w['empfindlichkeit_N_je_adc'][c],
                         r['u_empfindlichkeit_rel_statistisch'] * r['empfindlichkeit_N_je_adc']))
    assert _streuung_ok(z0) and _streuung_ok(zs)


def test_p01_nichtlinearitaet_und_umkehrspanne():
    s = systeme.system('V1-G0')
    mes, w = kalibrierdaten.p01_daten(s, np.random.default_rng(1), beta=(2e-3, 0.0, -1e-3), hysterese_N=(0, 5e-4, 0),
                                      sigma_adc=0.5)
    r = [anpassung.p01_zelle(e) for e in mes['einzeln']]
    assert r[0]['beta_je_N'] == pytest.approx(2e-3, abs=4 * r[0]['u_beta_je_N'])
    assert r[2]['beta_je_N'] == pytest.approx(-1e-3, abs=4 * r[2]['u_beta_je_N'])
    assert r[1]['umkehrspanne_N'] == pytest.approx(1e-3, abs=4 * r[1]['u_umkehrspanne_N'])
    assert r[0]['linearitaetsspanne_N'] > 10 * r[1]['linearitaetsspanne_N'] or r[1]['umkehrspanne_N'] > 0
    assert all(x['umrechnung'] == 'linear' for x in r)


def test_p01_laststellen_ueberdeckung():
    s = systeme.system('V1-G60h')
    zx, zg = [], []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        fehler = 1e-3 * rng.standard_normal((3, 2))
        gain = 1 + 2e-3 * rng.standard_normal(3)
        mes, w = kalibrierdaten.p01_daten(s, rng, zelllage_fehler=fehler, gain_rel=gain, sigma_lage_N=2e-5)
        r = anpassung.p01_laststellen(mes['laststellen'], mes['zellen_nominal_m'])
        assert r['bestimmbar'] and r['rang'] == 3
        zx.append(_z(np.r_[r['x_m'], r['y_m']], np.r_[w['zellen_m'][:, 0], w['zellen_m'][:, 1]],
                     np.r_[r['u_x_m'], r['u_y_m']]))
        zg.append(_z(r['g'], gain, r['u_g']))
    assert _streuung_ok(zx) and _streuung_ok(zg)


def test_p01_laststellen_nicht_identifizierbar():
    s = systeme.system('V1-G0')
    orte = np.array([[0.0, 0.0], [0.02, 0.0], [0.05, 0.0], [-0.04, 0.0], [0.08, 0.0]])    # auf einer Geraden
    mes, _ = kalibrierdaten.p01_daten(s, np.random.default_rng(1), orte=orte)
    r = anpassung.p01_laststellen(mes['laststellen'])
    assert not r['bestimmbar'] and r['rang'] == 2 and 'nicht bestimmbar' in r['diagnose']
    assert 'g' not in r and 'x_m' not in r                              # kein Optimiererwert
    mes, _ = kalibrierdaten.p01_daten(s, np.random.default_rng(1), orte=orte[:2])
    r = anpassung.p01_laststellen(mes['laststellen'])
    assert not r['bestimmbar'] and 'Laststellen' in r['diagnose']


def test_p01_kette_aus_bruecke():
    kette = systeme.Kette(f_tp=(150.0, 120.0, 180.0), tau=(1e-4, 2e-4, 5e-5))
    s = systeme.system('V1-G0', kette=kette)
    zs = []
    for seed in list(SEEDS)[:20]:
        mes, _ = kalibrierdaten.p01_daten(s, np.random.default_rng(seed))
        b = anpassung.p01_bruecke(mes['bruecke'])
        for c in range(3):
            zs.append(_z([b[c]['tau_s'], b[c]['w']], [kette.tau[c], 1 / kette.f_tp[c]], [b[c]['u_tau_s'], b[c]['u_w']]))
            assert b[c]['modell_passt'] and not b[c]['statik_widerspruch']
    assert _streuung_ok(zs, 0.6, 1.4)


def test_p01_falsche_bruecke_wird_gemeldet():
    """C03: systematischer Fehler des Brückensimulators wird gemeldet und nicht wegnormiert."""
    s = systeme.system('V1-G0', kette=systeme.Kette(f_tp=(150.0,) * 3, tau=(1e-4,) * 3))
    mes, _ = kalibrierdaten.p01_daten(s, np.random.default_rng(2), bruecke_fehler=1.05)
    b = anpassung.p01_bruecke(mes['bruecke'])
    assert all(x['statik_widerspruch'] for x in b)
    assert all(x['g'] == pytest.approx(1.05, rel=1e-3) for x in b)
    G = anpassung.gf_wert(b, [10.0, 20.0, 30.0])
    assert np.allclose(np.abs(G / s.kette.G([10.0, 20.0, 30.0])), 1.05, rtol=2e-3)


def test_p01_kettenmodell_unzureichend():
    """Modellabweichung: Tiefpass zweiter Ordnung ist mit dem Modell erster Ordnung nicht verträglich (χ²)."""
    class Kette2:
        f_tp = (100.0,) * 3
        tau = (0.0,) * 3

        def G(self, f):
            f = np.atleast_1d(np.asarray(f, float))
            return np.tile(1 / (1 + 1j * f / 100.0) ** 2, (3, 1))
    s = systeme.system('V1-G0')
    mes, _ = kalibrierdaten.p01_daten(s, np.random.default_rng(3), kette=Kette2())
    b = anpassung.p01_bruecke(mes['bruecke'])
    assert not any(x['modell_passt'] for x in b)


# ── P0.2 ─────────────────────────────────────────────────────────────────────────────────────────────
def test_p02_masse_konvention_b_und_m_L():
    s = systeme.system('V1-G0', m_luft=0.012)
    mes, w = kalibrierdaten.p02_daten(s, np.random.default_rng(1))
    r = anpassung.p02_auswerten(mes)
    assert r['konvention'] == 'b' and r['M_kg'] == pytest.approx(w['M'], abs=4 * r['u_M_kg'])
    assert r['M_traege_kg'] == pytest.approx(w['M_traege'], abs=1e-3)
    mes2, _ = kalibrierdaten.p02_daten(s, np.random.default_rng(1), m_L_angeben=False)
    r2 = anpassung.p02_auswerten(mes2)
    assert r2['M_traege_kg'] is None and 'm_L nicht angegeben' in r2['diagnose']


# ── P0.4 ─────────────────────────────────────────────────────────────────────────────────────────────
def _p04(s, rng, band=(20.0, 600.0), **kw):
    mes, w = kalibrierdaten.p0_messungen(s, rng, p04=kw)
    p01 = anpassung.p01_auswerten(mes['p01'])
    p02 = anpassung.p02_auswerten(mes['p02'])
    return anpassung.p04_auswerten(mes['p04'], p01, p02, band), w


def test_p04_einfreiheitsgrad_ueberdeckung():
    """f_n, ζ der Summe bei mittiger Anregung: Überdeckung der Unsicherheit über feste Seeds (Rauschen 2·10⁻³ N)."""
    s = systeme.system('V1-G0', kette=systeme.Kette(f_tp=(400.0,) * 3, tau=(5e-5,) * 3))
    zf, zz = [], []
    for seed in list(SEEDS)[:25]:
        rng = np.random.default_rng(seed)
        mes, w = kalibrierdaten.p0_messungen(s, rng, p04=dict(rauschpegel=2e-3, orte={'mitte': np.zeros(2)},
                                                                amplituden=(1.0,)))
        p01 = anpassung.p01_auswerten(mes['p01'])
        d = mes['p04']['daten']['mitte@1']
        f = mes['p04']['f_hz']
        sel = (f >= 20) & (f <= 600)
        G = anpassung.gf_wert(p01['bruecke'], f[sel])
        _, _, Ts, vs = anpassung._kanaele_mechanisch(dict(T=d['T'][:, sel], kohaerenz=d['kohaerenz'][:, sel],
                                                          n_mittel=d['n_mittel']), G)
        x, cov, chi2, dof, _ = anpassung._fit_1fg(f[sel], Ts, vs)
        zf.append((x[0] - w['p04']['f_n']) / np.sqrt(cov[0, 0]))
        zz.append((x[1] - w['p04']['zeta']) / np.sqrt(cov[1, 1]))
        assert 0.7 < chi2 / dof < 1.4
    assert _streuung_ok(zf, 0.6, 1.5) and _streuung_ok(zz, 0.6, 1.5)


def test_p04_moden_k_c_linearitaet():
    s = systeme.system('V1-G0', m_luft=0.01)
    r, w = _p04(s, np.random.default_rng(4))
    e = r['einfreiheitsgrad']
    assert e['f_n_hz'] == pytest.approx(w['p04']['f_n'], abs=5 * e['u_f_n_hz'])
    assert r['K_C']['K_N_je_m'] == pytest.approx(w['p04']['K'], rel=1e-4)
    assert [round(m['f_hz'], 1) for m in r['moden']] == [round(w['p04']['moden'][0], 1),
                                                         round(w['p04']['moden'][1], 1)]
    assert r['f_1_hz'] == pytest.approx(w['p04']['moden'][0], rel=1e-5)
    assert r['linearitaet']['linear'] and r['einfreiheitsgrad_ausreichend']['summe']
    assert r['einfreiheitsgrad_ausreichend']['kippmoden_hz']


def test_p04_modellabweichungen_werden_erkannt():
    """Amplitudenabhängige Steifigkeit (Linearität) und exzentrische Restmasse (1-FG der Summe unzureichend)."""
    r, _ = _p04(systeme.system('V1-G0'), np.random.default_rng(5), kappa_amplitude=0.02)
    assert not r['linearitaet']['linear']
    r, w = _p04(systeme.system('V1-G0', xy0=(0.02, 0.0)), np.random.default_rng(6))
    assert not r['einfreiheitsgrad_ausreichend']['summe']
    assert len(r['moden']) == 3
    assert np.allclose([m['f_hz'] for m in r['moden']], w['p04']['moden'], rtol=1e-4)


def test_p04_band_und_identifizierbarkeit():
    s = systeme.system('V1-G0')
    r, _ = _p04(s, np.random.default_rng(7), band=(20.0, 100.0), rauschpegel=5e-3)
    assert any('außerhalb des Anpassungsbands' in d for d in r['einfreiheitsgrad']['diagnose'])
    assert r['f_1_hz'] is None and 'untere Schranke' in r['f_1_hinweis']
    r, _ = _p04(s, np.random.default_rng(8), band=(20.0, 60.0), rauschpegel=2e-2)
    assert not r['einfreiheitsgrad']['identifizierbar']
    assert r['K_C']['K_N_je_m'] is None
    with pytest.raises(ValueError, match='Anpassungsband'):
        anpassung.p04_auswerten({}, {}, {}, None)


def test_p04_starre_auflage_ohne_mode():
    r, _ = _p04(systeme.system('A4'), np.random.default_rng(9))
    assert r['moden'] == [] and r['f_1_hz'] is None and 'untere Schranke' in r['f_1_hinweis']
    assert not r['einfreiheitsgrad']['identifizierbar'] and r['K_C']['K_N_je_m'] is None
    assert any('nicht aus allen Zellen messbar' in h for h in r['einfreiheitsgrad_ausreichend']['hinweise'])


# ── P0.5 ─────────────────────────────────────────────────────────────────────────────────────────────
def test_p05_delta_delta_ueberdeckung_und_anforderung():
    s = systeme.system('V1-G0', delta_profil_grad=(0.0, 0.35, -0.15))
    z = []
    for seed in list(SEEDS)[:30]:
        mes, w = kalibrierdaten.p05_daten(s, np.random.default_rng(seed), jitter_grad=0.05, sigma_weg_m=5e-7)
        r = anpassung.p05_auswerten(mes)
        z.append(_z(r['delta_delta_grad'][1:], w['delta_delta_grad'][1:], r['u_delta_delta_grad'][1:]))
        assert r['anforderung_u_delta_delta']['erfuellt']
        xk = r['module'][1]['x_m'][:3]
        assert np.all(np.abs(xk - w['X'][1, :3]) < 5 * np.hypot(r['module'][1]['u_x_re_m'][:3],
                                                                 r['module'][1]['u_x_im_m'][:3]) + 1e-12)
    assert _streuung_ok(z, 0.6, 1.45)
    mes, _ = kalibrierdaten.p05_daten(s, np.random.default_rng(1), jitter_grad=2.0, n_zyklen=8)
    r = anpassung.p05_auswerten(mes)
    assert not r['anforderung_u_delta_delta']['erfuellt']             # Anforderung ist Prüfung, keine Zusage


def test_p05_wegkanal_modellabweichung():
    """Falsches Datenblatt von G_x: bei gemeinsamem Wegkanal fällt die Phase in Δδⱼ heraus, x_k ist verfälscht;
    bei getrennten Kanälen verschiebt eine unerkannte Laufzeit Δδⱼ (Grenze der Unsicherheitsangabe)."""
    s = systeme.system('V1-G0', delta_profil_grad=(0.0, 0.3, 0.0))
    wahr_gx = dict(f_tp=3000.0, tau=50e-6, gain=1.0)
    blatt = dict(f_tp=3000.0, u_f_tp=30.0, tau=20e-6, u_tau=1e-7, gain=1.0, u_gain=1e-4)
    mes, w = kalibrierdaten.p05_daten(s, np.random.default_rng(1), G_x=wahr_gx, G_x_datenblatt=blatt)
    r = anpassung.p05_auswerten(mes)
    assert r['delta_delta_grad'][1] == pytest.approx(0.3, abs=4 * r['u_delta_delta_grad'][1])
    dphi = np.degrees(np.angle(r['module'][0]['x_m'][0] / w['X'][0, 0]))
    assert dphi == pytest.approx(-360 * 10.0 * 30e-6, abs=2e-3)       # nicht korrigierte Laufzeit 30 µs
    gx = [dict(f_tp=3000.0, tau=20e-6, gain=1.0), dict(f_tp=3000.0, tau=50e-6, gain=1.0),
          dict(f_tp=3000.0, tau=20e-6, gain=1.0)]
    mes, _ = kalibrierdaten.p05_daten(s, np.random.default_rng(2), G_x=gx, G_x_datenblatt=blatt,
                                      getrennte_sensoren=True)
    r = anpassung.p05_auswerten(mes)
    bias = r['delta_delta_grad'][1] - 0.3
    assert bias == pytest.approx(360 * 10.0 * 30e-6, abs=3e-3) and abs(bias) > 3 * r['u_delta_delta_grad'][1]


def test_p05_zu_wenige_impulse():
    s = systeme.system('V1-G0')
    mes, _ = kalibrierdaten.p05_daten(s, np.random.default_rng(1))
    mes['module'][2]['index_s'] = mes['module'][2]['index_s'][:2]
    r = anpassung.p05_auswerten(mes)
    assert not r['bestimmbar'] and 'Zyklen' in r['diagnose']


# ── Kalibrierung als gehashte Eingabe ────────────────────────────────────────────────────────────────
def test_kalibrierung_schreiben_lesen_und_trennung(tmp_path):
    s = systeme.system('V1-G0', m_luft=0.01, kette=systeme.Kette(f_tp=(150.0,) * 3, tau=(1e-4,) * 3))
    mes, w = kalibrierdaten.p0_messungen(s, np.random.default_rng(11))
    k = formate.synth_kennung('T')
    kalibrierdaten.schreibe_p0(str(tmp_path / 'eingang' / 'p0'), mes, k)
    _, mes2 = anpassung.lies_p0(str(tmp_path / 'eingang' / 'p0'))
    kal = anpassung.kalibrieren(mes2, band_hz=(20.0, 600.0))
    assert kal['hinterlegung']['eingang_sha256']['p01'] == formate.sha256_json(mes['p01'])
    h1 = anpassung.schreibe_kalibrierung(str(tmp_path / 'eingang' / 'kalibrierung'), kal, k)
    h2 = anpassung.schreibe_kalibrierung(str(tmp_path / 'b' / 'kalibrierung'), anpassung.kalibrieren(
        mes2, band_hz=(20.0, 600.0)), k)
    assert h1 == h2                                                     # reproduzierbar, ohne Zeitstempel
    _, kal2 = anpassung.lies_kalibrierung(str(tmp_path / 'eingang' / 'kalibrierung'))
    assert kal2['p0_5']['delta_delta_grad'] == kal['p0_5']['delta_delta_grad']
    e = anpassung.h3_eingaenge(kal2)
    assert e['fehlend'] == [] and e['zellanteile'].shape == (3, 3)
    assert np.allclose(e['zellanteile'].sum(0), 1.0)
    with pytest.raises(formate.FormatFehler):
        formate.lies(str(tmp_path / 'eingang' / 'kalibrierung'), 'wahrheit')


@pytest.mark.parametrize('datei', ['anpassung.py', 'pilot.py', 'gueltigkeit.py', 'laufgroessen.py', 'g4.py',
                                   'e3_grenzen.py', 'teil_b.py'])
def test_ap11_importiert_weder_generator_noch_harness(datei):
    baum = ast.parse(open(os.path.join(CODE, datei), encoding='utf-8').read())
    namen = set()
    for n in ast.walk(baum):
        if isinstance(n, ast.ImportFrom):
            namen.add(n.module or '')
            namen.update(a.name for a in n.names)
        elif isinstance(n, ast.Import):
            namen.update(a.name for a in n.names)
    assert not any('generator' in x or 'harness' in x or 'wahrheit' in x for x in namen)


# ── Pilotskript ──────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope='module')
def phase0():
    m = szenarien.modell('N01-V1G0', 'L2', plan=kampagne.Plan(n0=20, n_pilot=20, n_bloecke=2))
    mes, _ = kalibrierdaten.p0_messungen(m.system, np.random.default_rng(5))
    kal = anpassung.kalibrieren(mes, band_hz=(20.0, 600.0))
    laeufe = kampagne.laufplan(m.plan, np.random.default_rng(1))
    tab = ebene_h.erzeuge(m, laeufe, np.random.default_rng(2))
    return m, kal, laeufe, tab


ZEIT = dict(T_park=2.0, T_ramp=2.0, T_ab=2.0, T_eP=3.0, T_aP=12.0, T_verfuegbar=8 * 3600, d=1, N_K=21, N_I=0)


def _flach(o, p=''):
    if isinstance(o, dict):
        for k, v in o.items():
            yield f'{p}/{k}'
            yield from _flach(v, f'{p}/{k}')
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _flach(v, f'{p}/{i}')


def test_pilot_ohne_planung_nur_vorbereitende_groessen(phase0):
    m, kal, laeufe, tab = phase0
    prof = regeln.profil('ENTW-2026-10').mit_reduktion(eps_ctrl_datensaetze=2000)
    out = pilot.pilot_auswerten(tab, kal, prof, 10.0, zeit=ZEIT, seed=3)
    assert out['suche']['ergebnis'] == 'offen' and 'nicht angebunden' in out['suche']['grund']
    assert out['k_b'] == 12 and out['sigma_ref']['ausreichend']
    assert out['eps_ctrl']['quelle'] == '3·σ̂_ref' and out['eps_ctrl']['n_sim'] == 2000
    assert set(out['streuungen_volles_fenster']['s_q']) == set(('F_min_rel', 'Re_N1', 'Im_N1', 'Re_N2', 'Im_N2',
                                                                'Re_N3', 'Im_N3'))
    sc = out['sigma_c']
    assert np.allclose(sc, m.rausch.sigma_zelle, rtol=1e-6)
    assert np.allclose(out['F_LO_zellen'], 5 * np.asarray(sc))
    assert 'G3' in out['gueltigkeit']['nicht_pruefbar'] and 'untere Schranke' in out['p_hat_hinweis']
    pfade = list(_flach({k: v for k, v in out.items() if k != 'profil'}))
    verboten = ('residu', 'yhat', 'vorhersage', 'superposition', 'bestaetigt', 'falsifiziert', 'entscheid')
    assert not [p for p in pfade if any(v in p.lower() for v in verboten)]


def test_pilot_ausgabepruefung_weist_residuen_zurueck():
    for feld in ('r0', 'z1', 'residuum_F', 'yhat0', 'H1_entscheidung', 'falsifiziert'):
        with pytest.raises(ValueError, match='unzulässiges Feld'):
            pilot.pruefe_ausgabe({'suche': {'schritte': [{feld: 1.0}]}})
    pilot.pruefe_ausgabe({'sigma_delta': {'R': {'N': 1.0}}, 'reserve_r': 3})


def test_pilot_suchreihenfolge_und_kein_arbeitspunkt(phase0):
    m, kal, laeufe, tab = phase0
    prof = regeln.profil('ENTW-2026-10').mit_reduktion(eps_ctrl_datensaetze=500)
    aufrufe = []

    def tabelle_fuer(Nz):
        m2 = szenarien.modell('N01-V1G0', 'L2', plan=m.plan.mit(n_zyklen=Nz))
        return ebene_h.erzeuge(m2, laeufe, np.random.default_rng(2))

    def planung_zu_gross(e):                                            # Testhaken: nie zulässig
        aufrufe.append((e['k'], e['N_z']))
        return dict(n_min=10 ** 6, n0=20, quelle='Testhaken')
    out = pilot.pilot_auswerten(tab, kal, prof, 10.0, zeit=ZEIT, seed=3, planung=planung_zu_gross,
                                tabelle_fuer=tabelle_fuer, N_z_raster=(20, 60))
    assert out['suche']['ergebnis'] == 'kein zulässiger Arbeitspunkt unter diesen Annahmen'
    assert aufrufe == [(k, nz) for k in range(12, 2, -1) for nz in (20, 60)]   # k absteigend, je k T_a aufsteigend
    assert 'Reduktion' in out['suche']['reduktion']

    def planung_klein(e):
        return dict(n_min=12, n0=20, quelle='Testhaken')
    out = pilot.pilot_auswerten(tab, kal, prof, 10.0, zeit=ZEIT, seed=3, planung=planung_klein,
                                tabelle_fuer=tabelle_fuer, N_z_raster=(20, 60))
    s = out['suche']
    assert s['ergebnis'] == 'festgelegt' and s['k_max'] == 12 and s['N_z'] == 20 and s['n'] == 12 + s['reserve_r']


def _paar(planung, erfuellt=None):
    s = dict(k=12, N_z=100, planung=planung)
    if erfuellt is not None:
        s.update(erfuellt=erfuellt)
    return s


BEDINGUNG = dict(n_min=None, n0=None, grund='kein Kandidat erreicht P(H1 und H2 bestätigt | exakt) ≥ 0,8',
                 kandidaten=[dict(n_min=18, n0=20, reserve_r=2, P_gemeinsam=0.25, erfuellt=False)])
GRENZE = dict(n_min=None, n0=None, kandidaten=[], reduziert=True,
              grund='nicht simuliert: Entwicklungsgrenze von 2 Planungsaufrufen erreicht')
UEBERSPRUNGEN = dict(n_min=None, n0=None, grund='kein Kandidat erreicht P(H1 und H2 bestätigt | exakt) ≥ 0,8',
                     kandidaten=[dict(n_min=18, n0=20, reserve_r=2, uebersprungen='n = n_min + r > n_max')])


def test_suchbegruendung_nennt_den_tatsaechlichen_abbruchgrund():
    """Grundklassen der Begründung ohne Arbeitspunkt aus den Rückgaben je Paar (k, T_a): nur Zeitbudget (auch wenn der
    Haken alle Kandidaten wegen n > n_max überspringt) → bisheriger Text; nicht erreichte Bedingung und Aufrufgrenze
    mit Zahlen und ohne Unzulässigkeit außerhalb der reduzierten Suche; sonstiger Grund des Hakens; leeres Raster."""
    budget = 'kein Paar (k, T_a) erfüllt n = n_min + r ≤ n_max'
    gb = pilot.grund_ohne_arbeitspunkt
    assert gb([_paar(dict(n_min=10 ** 6, n0=20), erfuellt=False)] * 3) == budget
    assert gb([_paar(UEBERSPRUNGEN)] * 2) == budget
    assert gb([_paar(UEBERSPRUNGEN)], 'nur N_z = 100') == budget + (' – reduzierte Suche ausgeschöpft, kein Nachweis '
                                                                     'der Unzulässigkeit außerhalb dieser Suche')
    g = gb([_paar(BEDINGUNG)] * 2 + [_paar(GRENZE)] * 26)
    assert g.startswith('an 2 Paaren (k, T_a) erreicht kein simulierter Kandidat P(H1 und H2 bestätigt | exakt) ≥ 0,8')
    assert '26 Paare wegen der Grenze der Planungsaufrufe nicht simuliert' in g and 'reduzierte Suche ausgeschöpft' in g
    assert 'n_min + r ≤ n_max' not in g
    g = gb([_paar(BEDINGUNG), _paar(UEBERSPRUNGEN), _paar(dict(n_min=None, grund='keine Pilotstreuungen (ν_p = 0)',
                                                                kandidaten=[]))])
    assert g == ('an 1 Paar (k, T_a) erreicht kein simulierter Kandidat P(H1 und H2 bestätigt | exakt) ≥ 0,8; an 1 Paar '
                 'überschreitet n = n_min + r das Zeitbudget n_max; 1 Paar ohne Planung (keine Pilotstreuungen (ν_p = 0))')
    assert gb([]).startswith('kein Paar (k, T_a) im Suchraster')


def test_suchbegruendung_im_ablauf_mit_aufrufgrenze(phase0):
    """Durch die Suche des Pilotskripts mit einem Haken im Rückgabeformat von harness.planung.haken: erster Aufruf
    simuliert ohne Erfolg, alle weiteren wegen der Aufrufgrenze nicht; Ergebnis und Suchreihenfolge unverändert."""
    m, kal, laeufe, tab = phase0
    prof = regeln.profil('ENTW-2026-10').mit_reduktion(eps_ctrl_datensaetze=200)
    aufrufe = []

    def haken(e):
        aufrufe.append((e['k'], e['N_z']))
        return dict(BEDINGUNG) if len(aufrufe) == 1 else dict(GRENZE)
    s = pilot.pilot_auswerten(tab, kal, prof, 10.0, zeit=ZEIT, seed=3, planung=haken)['suche']
    assert s['ergebnis'] == 'kein zulässiger Arbeitspunkt unter diesen Annahmen' and len(s['schritte']) == len(aufrufe)
    n = len(aufrufe)
    assert n > 2 and s['grund'] == (f'an 1 Paar (k, T_a) erreicht kein simulierter Kandidat P(H1 und H2 bestätigt | '
                                    f'exakt) ≥ 0,8; {n - 1} Paare wegen der Grenze der Planungsaufrufe nicht simuliert'
                                    ' – reduzierte Suche ausgeschöpft, kein Nachweis der Unzulässigkeit außerhalb dieser '
                                    'Suche')


RESERVEGRENZE = dict(n_min=None, n0=None, grund='kein Kandidat erfüllt P ≥ 0,8 und die Reservebedingung: Reservegrenze',
                     kandidaten=[dict(n_min=18, n0=20, reserve_r=12, P_gemeinsam=0.9, P_erfuellt=True, erfuellt=False,
                                      grund='Reservegrenze: Bedingung nach zusatz_max = 10 Erhöhungen verfehlt')])


def test_suchbegruendung_reservegrenze_eigener_grund():
    """Regelstand 2026-11: Ein Paar, an dem P ≥ 0,8 erreicht, die Reservebedingung aber verfehlt wird, steht nicht
    unter „kein Kandidat erreicht P ≥ 0,8“."""
    g = pilot.grund_ohne_arbeitspunkt([_paar(RESERVEGRENZE), _paar(BEDINGUNG)])
    assert g == ('an 1 Paar (k, T_a) erreicht kein simulierter Kandidat P(H1 und H2 bestätigt | exakt) ≥ 0,8; an 1 Paar '
                 '(k, T_a) erreicht ein Kandidat P ≥ 0,8, verfehlt aber die Reservebedingung 0,95 auch nach den '
                 'zulässigen Erhöhungen von r (Reservegrenze)')


def test_suche_uebernimmt_die_erhoehte_reserve_des_hakens(phase0):
    """A9.2 (v): Hat der Haken r wegen der Reservebedingung erhöht, legt die Suche n = n_min + r mit diesem r fest
    (nicht mit der Formel allein); ohne Angabe des Hakens gilt die Formel wie bisher."""
    m, kal, laeufe, tab = phase0
    prof = regeln.profil('ENTW-2026-10').mit_reduktion(eps_ctrl_datensaetze=200)

    def haken(e):
        return dict(n_min=18, n0=20, reserve_r=9, n=27, kandidaten=[], quelle='Test')
    s = pilot.pilot_auswerten(tab, kal, prof, 10.0, zeit=ZEIT, seed=3, planung=haken)['suche']
    assert s['ergebnis'] == 'festgelegt' and s['reserve_r'] == 9 and s['n'] == 27
    assert s['schritte'][-1]['reserve_r_formel'] < 9

    def ohne(e):
        return dict(n_min=18, n0=20, kandidaten=[], quelle='Test')
    s0 = pilot.pilot_auswerten(tab, kal, prof, 10.0, zeit=ZEIT, seed=3, planung=ohne)['suche']
    assert s0['reserve_r'] == s['schritte'][-1]['reserve_r_formel'] and 'reserve_r_formel' not in s0['schritte'][-1]


def test_suche_offen_wenn_die_reservebedingung_nicht_pruefbar_ist(phase0):
    """Meldet der Haken die Reservebedingung als nicht prüfbar (Phase-0-Modellquelle mit statischem Laufplan), endet
    die Suche nach dem ersten Paar „offen“, statt alle Paare zu simulieren und Unzulässigkeit zu melden."""
    m, kal, laeufe, tab = phase0
    prof = regeln.profil('ENTW-2026-10').mit_reduktion(eps_ctrl_datensaetze=200)
    aufrufe = []

    def haken(e):
        aufrufe.append(e['k'])
        return dict(n_min=None, n0=None, reserve_pruefbar=False, kandidaten=[], kandidat_nur_P=dict(n_min=18, n0=20),
                    grund='kein Kandidat erfüllt P ≥ 0,8 und die Reservebedingung: nicht prüfbar')
    s = pilot.pilot_auswerten(tab, kal, prof, 10.0, zeit=ZEIT, seed=3, planung=haken)['suche']
    assert s['ergebnis'] == 'offen' and len(aufrufe) == 1 and 'nicht prüfbar' in s['grund']
    assert s['kandidat_nur_P']['n_min'] == 18


def test_pilot_eps_ctrl_betriebsstreuung_und_p_hat(phase0):
    m, kal, laeufe, tab = phase0
    prof = regeln.profil('ENTW-2026-10').mit_reduktion(eps_ctrl_datensaetze=2000)
    t2 = tab.auswahl(np.arange(len(tab)))
    art = t2.spalte('laufart', object)
    rng = np.random.default_rng(9)
    zus = 5e-4 * rng.standard_normal(len(t2))
    t2.daten['N_mittel'] = np.where(art != 'R', t2.daten['N_mittel'] + zus, t2.daten['N_mittel'])
    out = pilot.pilot_auswerten(t2, kal, prof, 10.0, zeit=ZEIT, seed=3)
    assert out['eps_ctrl']['betrieb_streut_staerker'] and out['eps_ctrl']['quelle'] == '3·σ̂_betr'
    # Störungen in vier Pilotläufen → p̂ = 4/60 (bei sonst gültigen Läufen)
    pil = [i for i, k in enumerate(tab.koepfe) if k['konfiguration']['gruppe'] == 'pilot']
    t3 = tab.auswahl(np.arange(len(tab)))
    for i in pil[:4]:
        t3.koepfe[i] = dict(t3.koepfe[i], stoerung=True)
    out0 = pilot.pilot_auswerten(tab, kal, prof, 10.0, zeit=ZEIT, seed=3)
    out3 = pilot.pilot_auswerten(t3, kal, prof, 10.0, zeit=ZEIT, seed=3)
    assert out3['p_hat'] == pytest.approx(out0['p_hat'] + 4 / 60, abs=1e-12)


def test_gueltigkeit_regeln_aus_rohkanal(phase0):
    """G5/G6 aus dem Zellkanal, G2 aus Indexfehlern; nicht prüfbare Regeln werden genannt, nicht als erfüllt gezählt."""
    m, kal, laeufe, tab = phase0
    t = tab.auswahl(np.arange(len(tab)))
    i = next(j for j, k in enumerate(t.koepfe) if k['laufart'] == 'K')
    t.daten['uebersteuert_zellen'][i, 2] = True
    t.daten['min_roh_zellen'][i + 1, 1] = 0.0
    t.daten['index_fehler'][i + 2, 1] = 1
    sw = gueltigkeit.Schwellen(f_soll=10.0, kmax=12, sigma_tol_grad={2: 1.0, 3: 1.0}, F_LO_zellen=[0.05] * 3,
                               delta_delta_grad=kal['p0_5']['delta_delta_grad'])
    sw.sigma_delta = gueltigkeit.sigma_delta(t, 12)
    pr = gueltigkeit.pruefe(t, sw)
    assert pr['regeln']['G5'][i] is True and pr['regeln']['G6'][i + 1] is True
    assert pr['regeln']['G2'][i + 2] is True or t.koepfe[i + 2]['laufart'] == 'R'
    assert 'G1' in pr['nicht_pruefbar'] and 'G3' in pr['nicht_pruefbar']
    assert pr['regeln']['G1'][i] is None
