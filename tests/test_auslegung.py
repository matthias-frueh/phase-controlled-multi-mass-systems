"""Tests für code/auslegung.py (Auslegungswerkzeug, Präregistrierung v2 §12, Werkzeug 2).

Referenzen: linear_solver.py (Repo), Zahlen der Präregistrierung (Anhang A4, A6, A8) und die Nachrechnung 10/2026
(unabhängige exakte Zeitbereichslösung des 1-FG-Modells bzw. eigenes 3-FG-Zellmodell, Zellen auf R_c = 100 mm,
Restmasse als Scheibe mit ρ₀ = R_c/2). Toleranzen: Vergleiche mit linear_solver.py 1e-6 N (gleiches Modell,
gleiches Raster; tatsächlich ≈ 1e-14 N), Referenzzahlen auf eine halbe Einheit ihrer letzten angegebenen Stelle
(plus 1/5 als Reserve für Rundung, z. B. μ = 0,4615 statt 3·0,1/0,65 in der Nachrechnung). Als Regressionswert
gekennzeichnete Zahlen stammen aus dem Werkzeug selbst und sichern nur gegen unbeabsichtigte Änderungen.
Langsame Prüfungen (@slow) laufen nur mit PCMMS_SLOW=1.
"""
import json
import os
import sys
import warnings

import numpy as np
import pytest
from scipy import signal

import auslegung as al
import linear_solver as ls

with warnings.catch_warnings():                 # Marke „slow“ ohne pytest.ini, daher nicht registriert
    warnings.simplefilter('ignore', pytest.PytestUnknownMarkWarning)
    _SLOW = pytest.mark.slow
LANGSAM = os.environ.get('PCMMS_SLOW') == '1'
M = al.M_REF
K_STEIF = 369518.0                      # f_n = 120 Hz bei M = 0,65 kg (Präreg A5), ζ = 0,02
C_STEIF = 2 * 0.02 * np.sqrt(K_STEIF * M)


def slow(f):
    return _SLOW(pytest.mark.skipif(not LANGSAM, reason='langsam; mit PCMMS_SLOW=1 aktivieren')(f))


def satz(mu, K=None, C=None, geo='G0', f=10.0, hub=al.HUB_REF, **kw):
    """Gleiche Module mit bewegtem Massenanteil μ bei M = 0,65 kg (wie linear_solver.py, μ-Modell)."""
    return al.Aufbau(m=(mu * M / 3,) * 3, m0=(1 - mu) * M, hub=hub, f=f, K=K, C=C, zeta=None, geometrie_name=geo, **kw)


def lauf(b, name):
    return [x['name'] for x in b['laeufe']].index(name)


PUNKTE = np.array([(120, 240), (110, 250), (130, 230), (110, 252), (100, 240), (140, 240), (240, 120),
                   (0, 0), (0, 180), (35, 116)], float)


# ── Summenkraft gegen linear_solver.py ────────────────────────────────────────────────────────────
def test_referenz_gleich_linear_solver():
    """Referenzsatz M = 0,650 kg, μ = 1, K = 1e4 N/m, C = 16 N·s/m, Egg, 10 Hz: F_min, F_max, γ₁, A, z_max und
    die Klassifikation stimmen mit linear_solver.solve() überein; (0°,0°) und (0°,180°) heben ab."""
    a = al.Aufbau(**al.REFERENZ)
    r = a.loesen(PUNKTE)
    s = ls.solve(PUNKTE[:, 0], PUNKTE[:, 1])
    v = s['valid']
    assert (r['valid'] == v).all() and v.sum() == 8
    assert np.abs(r['voll']['F_min'] - s['F_min_lin']).max() <= 1e-6
    for q, c in (('F_max', 'F_max'), ('gamma1', 'F_skew'), ('A', 'peak_ratio')):
        assert np.abs(r['voll'][q][v] - s[c][v]).max() <= 1e-6, q
    assert np.abs(r['z_max'] - s['z_max']).max() <= 1e-12
    assert r['voll']['abw_1FG'].max() < 1e-9            # symmetrisch: Σ F_c = N_1FG
    assert r['voll']['F_min'][0] == pytest.approx(5.330390, abs=5e-7)      # Präreg A3, data/finesweep_2deg_120_240.csv
    kz = a.kennzahlen()
    assert kz['f_n'] == pytest.approx(19.7407, abs=5e-5)
    assert 3 * a.f / kz['f_n'] == pytest.approx(1.5197, abs=5e-5)
    assert kz['zeta'] == pytest.approx(ls.ZETA0, rel=1e-12)


def test_referenz_harmonische_gleich_linear_solver():
    """N_k (Präreg-Konvention, k = 1 … 20) gleich dem Spektrum von linear_solver.waveform()."""
    a = al.Aufbau(**al.REFERENZ)
    for p in [(120.0, 240.0), (110.0, 250.0), (0.0, 0.0)]:
        _, N = ls.waveform(*p)
        Nk = 2 * np.fft.rfft(N) / N.size
        assert np.abs(a.loesen([p], kout=20)['Nk'][0] - Nk[1:21]).max() <= 1e-9


@pytest.mark.filterwarnings('ignore:Precision loss')     # linear_solver: Schiefe einer konstanten Kurve
@pytest.mark.parametrize('profil', ['egg', 'sinus'])
@pytest.mark.parametrize('K, C', [(1e6, ls.c_for(1e6, 0.05)), (3e4, 16.0), (None, 0.0)])
def test_skalierung_gleich_linear_solver(profil, K, C):
    """μ = 0,4 (Restmasse an Bord), 12 Hz bei gleichem Hub, weicher, steifer und starrer Kontakt, beide Profile."""
    a = satz(0.4, K, C, f=12.0, profil_art=profil)
    r = a.loesen(PUNKTE)
    s = ls.solve(PUNKTE[:, 0], PUNKTE[:, 1], K_c=K, C_c=C, mu=0.4, profile=profil, f_hz=12.0)
    v = s['valid'] & np.isfinite(s['F_skew'])          # Sinus bei (120°, 240°): N konstant, Schiefe undefiniert
    assert (r['valid'] == s['valid']).all()
    assert np.abs(r['voll']['F_min'] - s['F_min_lin']).max() <= 1e-6
    assert np.abs(r['voll']['F_max'][v] - s['F_max'][v]).max() <= 1e-6
    assert np.abs(r['voll']['gamma1'][v] - s['F_skew'][v]).max() <= 1e-6


def test_hub_ist_spitze_spitze():
    """Das normierte Profil hat den Weg-Spitze-Spitze-Wert 1 (Hub = RTOP + RBOT, Egg und Sinus) und das Egg-ε
    die Formel μ·π²·Hub·f²/(THOLD·g)."""
    k = np.arange(1, al.N_FEIN // 2 + 1)
    for art in ('egg', 'sinus'):
        c = np.fft.rfft(al.profil(art=art))[1:] / al.N_FEIN
        x = np.fft.irfft(np.r_[0, c / -(2 * np.pi * k) ** 2] * al.N_FEIN, al.N_FEIN)
        assert x.max() - x.min() == pytest.approx(1.0, abs=1e-6)
    a = al.Aufbau()
    assert a.kennzahlen()['eps'] == pytest.approx(a.mu * np.pi ** 2 * 8e-3 * 100 / (al.THOLD * al.G), rel=1e-12)


# ── Präreg A4/A6: starre Auflage, μ = 0,4 ────────────────────────────────────────────────────────────
def test_A4_A6_starr():
    """Schnitt, Bandbegrenzung, Laufarten und Zellreserve des A4-Beispiels (Präreg A4, A6)."""
    a = satz(0.4)
    b = al.bewerte(a)
    s = b['schnitt']['voll']
    assert s['F_min'][10] == pytest.approx(5.6452, abs=6e-5)
    assert s['F_min'][0] == pytest.approx(5.1759, abs=6e-5)
    assert s['dF'] == pytest.approx(0.4693, abs=6e-5)
    assert (s['s_L'], s['s_R']) == pytest.approx((0.0469, 0.0468), abs=6e-5)
    assert s['gamma1'][10] == pytest.approx(-0.4498, abs=6e-5)
    g = b['gruppen']
    assert b['roh']['voll']['A'][lauf(b, 'Schnitt (120°,240°)')] == pytest.approx(0.6529, abs=6e-5)
    assert g['schnitt']['F_max'] == pytest.approx(7.0752, abs=6e-5)
    assert g['synchron']['F_max'] == pytest.approx(12.0163, abs=6e-5)
    assert g['zweiergruppe']['F_max'] == pytest.approx(9.1241, abs=6e-5)
    assert g['einzel']['F_max'] == pytest.approx(8.2564, abs=6e-5)
    assert g['einzel']['reserve_summe'] * a.MG == pytest.approx(5.3642, abs=6e-5)
    assert b['mengen']['alle']['reserve_zelle'] == pytest.approx(0.524, abs=6e-4)  # jede Zelle 52,4 % (A4)
    assert b['mengen']['alle']['Fz_max'] == pytest.approx(4.0054, abs=6e-5)
    b9 = al.bewerte(a, kmax=9)['schnitt']['band']
    assert (b9['F_min'][10], b9['F_min'][0], b9['dF']) == pytest.approx((5.6781, 5.1608, 0.5173), abs=6e-5)
    assert b9['gamma1'][10] == pytest.approx(-0.4305, abs=6e-5)
    tri = [(0.0, 120.0, 240.0)]
    assert a.loesen(tri, kmax=6)['band']['gamma1'][0] == pytest.approx(-0.3775, abs=6e-5)
    for km in (3, 4, 5):                               # nur die dritte Harmonische: Schiefe null
        assert abs(a.loesen(tri, kmax=km)['band']['gamma1'][0]) < 1e-9


def test_pb1_mit_nu():
    """PB1-Anforderung u_c ≤ 0,25·ΔF_Zelt/c mit c = t(1 − 0,05/294; ν) (Präreg A8: 3,583 für ν → ∞, 4,356 für
    ν = 19); A4-Beispiel: 0,0327 bzw. 0,0269 N (Nachrechnung 10/2026)."""
    assert al.c_pb1() == pytest.approx(3.583, abs=5e-4) and al.c_pb1(19) == pytest.approx(4.356, abs=5e-4)
    a = satz(0.4)
    assert al.bewerte(a)['schnitt']['uc_Fmin'] == pytest.approx(0.0327, abs=6e-5)
    assert al.bewerte(a, nu=19)['schnitt']['uc_Fmin'] == pytest.approx(0.0269, abs=6e-5)


# ── Fenster, V1-Kandidat (Nachrechnung 10/2026) ──────────────────────────────────────────────────────
def test_fenster_starr():
    """3 × 100 g, 10 Hz, starr (Nachrechnung 10/2026): unten ε = 0,476 (Signal ΔF_Zelt ≥ 0,4693 N wie A4), oben
    0,750 (G0: jede Zelle 1 − ε in jedem Lauf; zentral: synchron, Mengen ZUSATZ/ALLE) bzw. 1,853 (zentral,
    PFLICHT: Piloten, 0,75/0,40479); Hub 6,67–10,50 mm; K ≥ M·(12πf)² für (b), K ≥ 1,03e6 N/m für ρ ≤ 0,05."""
    soll = dict(G0=dict(pflicht=0.7500, zusatz=0.7500, alle=0.7500),
                zentral=dict(pflicht=0.75 / 0.40479, zusatz=0.7500, alle=0.7500))
    for geo, hi in soll.items():
        fe = al.fenster(al.Aufbau(K=None, geometrie_name=geo))
        assert fe['eps_lo'] == pytest.approx(0.4763, abs=5e-5)
        for m, v in hi.items():
            assert fe['eps_hi'][m] == pytest.approx(v, abs=5e-5), (geo, m)
        assert 1e3 * fe['hub_lo'][0] == pytest.approx(6.67, abs=5e-3)
        assert 1e3 * fe['hub_hi']['zusatz'][0] == pytest.approx(10.50, abs=5e-3)
        assert fe['K_min_b'] == pytest.approx(M * (12 * np.pi * 10) ** 2, rel=1e-9)
        assert fe['K_min_robust'] == pytest.approx(1.0264e6, rel=1e-4)
    z = al.fenster(al.Aufbau(K=None, geometrie_name='zentral'))['zeilen'][0]
    assert z['bindend']['pflicht'] == 'Pilot (110°,252°)' and z['bindend']['zusatz'] == 'synchron (0°,0°)'
    # A4-Beispiel liegt genau auf der Signalgrenze: ε = 0,47625 ↔ ΔF_Zelt = 0,4693 N (Präreg A4)
    a4 = satz(0.4)
    assert a4.kennzahlen()['eps'] == pytest.approx(0.47625, abs=6e-6)
    assert al.fenster(a4)['zeilen'][0]['eps_sig'] == pytest.approx(0.47625, abs=6e-6)


def test_fenster_elastisch():
    """V1-Massen, K = 1,5e6 N/m, G0, ζ = 0,02 und 0,1: ε-Fenster [0,5034; 0,7119] in allen Laufmengen
    (Regressionswert; in G0 bindet die Zelle unter dem laufenden Modul, daher gleiche Obergrenzen)."""
    fe = al.fenster(al.Aufbau(), zetas=(0.02, 0.1))
    assert fe['eps_lo'] == pytest.approx(0.5034, abs=5e-5)
    assert fe['eps_hi'] == pytest.approx(dict(pflicht=0.7119, zusatz=0.7119, alle=0.7119), abs=5e-5)
    assert len(fe['zeilen']) == 2 and not any(fe['leer'].values())


def test_v1_kandidat():
    """V1 (3 × 100 g, 8 mm Spitze-Spitze, 10 Hz, K = 1,5e6 N/m, ζ = 0,05), Nachrechnung 10/2026: Die Reserven
    (gerundet 81 / 62 / 43 / 74 / 76 / 76 %) sind kleinstes F_min/(M·g) je Laufart; als Zellreserven gelten sie im
    Modell Summe/3 (Geometrie zentral), die größte Zellkraft 4,39 N ist F_max(synchron)/3. In G0 (3-FG-Dynamik)
    liegt die kleinste Zellreserve bei 41,137 % (Schnitt 100°), die größte Zellkraft bei 4,4109 N (unabhängiges
    3-FG-Zeitbereichsmodell der Nachrechnung 10/2026)."""
    a = al.Aufbau(geometrie_name='zentral')
    kz = a.kennzahlen()
    assert kz['f_n'] == pytest.approx(241.8, abs=0.05)
    assert kz['eps'] == pytest.approx(0.5715, abs=5e-5)
    assert kz['k_b'] == 12
    b = al.bewerte(a, a.kmax_standard())
    soll = dict(einzel=0.809, paar=0.618, synchron=0.426, zweiergruppe=0.738, pilot=0.757, schnitt=0.760)
    for g, v in soll.items():
        assert b['gruppen'][g]['reserve_summe'] == pytest.approx(v, abs=6e-4), g
        assert b['gruppen'][g]['reserve_zelle'] == pytest.approx(b['gruppen'][g]['reserve_summe'], abs=1e-12)
    assert b['gruppen']['paar']['lauf_summe'].startswith('Paar 12 Δ=0°')
    assert b['schnitt']['voll']['dF'] == pytest.approx(0.560, abs=5e-4)
    assert b['schnitt']['band']['dF'] == pytest.approx(0.588, abs=5e-4)          # k ≤ 12
    assert (b['schnitt']['voll']['s_L'], b['schnitt']['voll']['s_R']) == pytest.approx((0.0545, 0.0571), abs=6e-5)
    assert b['schnitt']['uc_Fmin'] == pytest.approx(0.039, abs=5e-4)
    assert b['schnitt']['uc_Nk'] == pytest.approx(0.025, abs=5e-4)
    assert b['mengen']['alle']['Fz_max'] == pytest.approx(4.390, abs=5e-4)
    assert b['mengen']['alle']['alle_valid']
    g0 = al.bewerte(al.Aufbau(), 12)
    assert g0['gruppen']['synchron']['Fz_max'] == pytest.approx(4.390, abs=5e-4)    # synchron momentfrei
    assert g0['mengen']['pflicht']['reserve_zelle'] == pytest.approx(0.41137, abs=1e-5)
    assert g0['mengen']['pflicht']['lauf_zelle'] == 'Schnitt (100°,240°)'
    assert g0['mengen']['alle']['Fz_max'] == pytest.approx(4.4109, abs=5e-5)
    starr = al.bewerte(al.Aufbau(K=None))                # starr jede Zelle 1 − ε (Präreg A2.5)
    for g in ('einzel', 'synchron', 'zweiergruppe', 'schnitt'):
        assert starr['gruppen'][g]['reserve_zelle'] == pytest.approx(0.4285, abs=6e-5)
    assert starr['mengen']['alle']['lauf_zelle'] == 'synchron (0°,0°) u. a. (101 gleich)'   # Gleichstand


def test_pruefung():
    """V1-Kandidat erfüllt (a) über Schnitt, Piloten und Einzelmodulläufe (kleinste Zellreserve 41,137 %), (b),
    die robuste Empfehlung und das Signal; (0°,0°) und (0°,180°) sind messbar. Mit 12 mm Hub in „zentral“ gilt
    (a) noch (Pilot (110°,252°): 1 − 1,5·(1 − 0,757)), aber synchron (1 − 1,5·(1 − 0,426)) ist nicht messbar.
    Die Simulationsreferenz verletzt (a) (ein Modul hebt ab, lineares F_min −2,0571 N) und (b) (3f/f_n = 1,52)."""
    p = al.pruefung(al.Aufbau())
    assert all(p[x]['ok'] for x in ('a', 'b', 'robust', 'band', 'signal')) and not p['modell']['warnung']
    assert p['a']['reserve_zelle'] == pytest.approx(0.41137, abs=1e-5) and p['a']['lauf'] == 'Schnitt (100°,240°)'
    assert p['a']['zusatz']['synchron (0°,0°)']['ok'] and p['a']['zusatz']['(0°,180°)']['ok']
    assert p['a']['zusatz']['synchron (0°,0°)']['reserve_zelle'] == pytest.approx(0.426, abs=6e-4)
    assert p['b']['kmax'] == 12 and p['signal']['spitze_band'] == 120.0
    assert (p['signal']['s_L_band'], p['signal']['s_R_band']) == pytest.approx((0.0435, 0.0435), abs=6e-5)
    z = al.pruefung(al.Aufbau(geometrie_name='zentral', hub=12e-3))
    assert z['a']['ok'] and z['a']['lauf'] == 'Pilot (110°,252°)'
    assert z['a']['reserve_zelle'] == pytest.approx(1 - 1.5 * (1 - 0.757), abs=9e-4)
    assert not z['a']['zusatz']['synchron (0°,0°)']['ok'] and z['a']['zusatz']['(0°,180°)']['ok']
    assert z['a']['zusatz']['synchron (0°,0°)']['reserve_zelle'] == pytest.approx(1 - 1.5 * (1 - 0.426), abs=9e-4)
    r = al.pruefung(al.Aufbau(**al.REFERENZ))
    assert not r['a']['ok'] and not r['b']['ok'] and not r['robust']['ok']
    einzel = al.Aufbau(**al.REFERENZ).loesen([(0, 0, 0)], w=[(1, 0, 0)])
    assert einzel['voll']['F_min'][0] == pytest.approx(-2.0571, abs=6e-5)       # Nachrechnung 10/2026
    s = al.pruefung(al.Aufbau(K=None))
    assert s['band']['entfaellt'] and s['a']['ok']


def test_rho_baender_punkte():
    """Resonanzlücken bei ζ = 0,02 (Nachrechnung 10/2026: ε-Fenster < 0,15 in ρ ≈ 0,053–0,055, 0,062–0,067,
    0,077–0,084, 0,100–0,112, 0,138–0,141); ρ = 0,05 ist frei (robust bis ρ ≈ 0,052)."""
    a = al.Aufbau(geometrie_name='zentral')
    frei = al.rho_baender(a, rho_min=0.05, rho_max=0.05)
    assert frei['baender'] == [] and frei['breite'][0] > 0.15
    for rho in (0.054, 0.065, 0.080, 0.105, 0.139):
        assert len(al.rho_baender(a, rho_min=rho, rho_max=rho)['baender']) == 1, rho


@slow
def test_rho_baender_raster():
    """Volles Raster ρ = 0,010 … 0,166 bei ζ = 0,02: Bänder liegen in den Lücken der Nachrechnung."""
    bd = al.rho_baender(al.Aufbau(geometrie_name='zentral'), zeta=0.02)
    assert bd['baender'][0][0] >= 0.053
    for rho in (0.054, 0.065, 0.080, 0.105, 0.139):
        assert any(lo - 1e-9 <= rho <= hi + 1e-9 for lo, hi in bd['baender']), rho


# ── 3-FG-Zellmodell (Nachrechnung 10/2026, unabhängig gegengeprüft) ─────────────────────────────
@pytest.mark.parametrize('K, C', [(None, None), (K_STEIF, C_STEIF)])
def test_auswahlregel_triphasik(K, C):
    """(0°, 120°, 240°), Module über den Zellen: Summe nur k ≡ 0 (mod 3), Moment nur k ≢ 0; k ≡ 1 läuft
    links, k ≡ 2 rechts um."""
    r = satz(0.462, K, C).loesen([(0.0, 120.0, 240.0)], kout=12)
    k = np.arange(1, 13)
    Nk, mx, my = r['Nk'][0], r['Mxk'][0] / 2, r['Myk'][0] / 2
    links, rechts = np.abs(mx + 1j * my), np.abs(np.conj(mx) + 1j * np.conj(my))
    assert np.abs(Nk[k % 3 != 0]).max() < 1e-12 and np.abs(Nk[k % 3 == 0]).min() > 1e-3
    assert max(links[k % 3 == 0].max(), rechts[k % 3 == 0].max()) < 1e-12
    assert rechts[k % 3 == 1].max() < 1e-12 and links[k % 3 == 2].max() < 1e-12
    assert links[0] == pytest.approx(0.2247 if K is None else 0.22585, abs=6e-5)        # R+₁ [N·m]


def test_zellreserven_starr():
    """STARR, μ = 0,462, Referenzhub, 10 Hz (Nachrechnung 10/2026): Schnitt Zelle | Summe/3 = 45,0 | 78,3 % (G0),
    56,9 % (G60h), 78,3 % (zentral); synchron überall 45,0 %, Einzelmodul G60h 72,5 %."""
    soll = dict(G0=0.450, G60h=0.569, zentral=0.783)
    for geo, v in soll.items():
        g = al.bewerte(satz(0.462, geo=geo))['gruppen']
        assert g['schnitt']['reserve_zelle'] == pytest.approx(v, abs=6e-4), geo
        assert g['schnitt']['reserve_summe'] == pytest.approx(0.783, abs=6e-4)
        assert g['synchron']['reserve_zelle'] == pytest.approx(0.450, abs=6e-4)
    assert al.bewerte(satz(0.462, geo='G60h'))['gruppen']['einzel']['reserve_zelle'] == pytest.approx(0.725, abs=6e-4)


def test_zellkraefte_dynamisch():
    """Kleinste Zellkraft der linearen 3-FG-Lösung (Nachrechnung, fünf Stellen): REF μ = 1 G0 am Triphasik-Punkt
    −6,30814 N; STEIF μ = 0,462: G0 0,84977 N (N_min 4,9416 N), G60h bei (0°,110°,240°) 1,14061 N."""
    tri, zelt = (0.0, 120.0, 240.0), (0.0, 110.0, 240.0)
    r = satz(1.0, 1e4, 16.0).loesen([tri])
    assert r['voll']['Fz_min'][0].min() == pytest.approx(-6.30814, abs=6e-6)
    assert r['valid'][0] and not r['valid_zellen'][0]          # Summe im Kontakt, eine Zelle hebt ab
    r = satz(0.462, K_STEIF, C_STEIF).loesen([tri])
    assert r['voll']['Fz_min'][0].min() == pytest.approx(0.84977, abs=6e-6)
    assert r['voll']['F_min'][0] == pytest.approx(4.9416, abs=6e-5)
    r = satz(0.462, K_STEIF, C_STEIF, geo='G60h').loesen([zelt])
    assert r['voll']['Fz_min'][0].min() == pytest.approx(1.14061, abs=6e-6)
    r = satz(0.462, 1e4, 16.0, geo='G60h').loesen([tri, zelt])
    assert r['voll']['Fz_min'].min(1) == pytest.approx([0.76576, 0.58700], abs=6e-6)


def test_kippfrequenzen():
    """Kipp-Eigenfrequenzen (Nachrechnung 10/2026): STEIF μ = 0,462 G0 155,7 / 140,4 / 120,7 Hz für
    ρ₀ = 0,35 / 0,5 / 0,7·R_c, G60h 241,3 / 193,5 / 149,7 Hz; REF μ = 1 G0 entartet bei f_Hub = 19,74 Hz; V1 analytisch
    f_Kipp = f_Hub·√(M·R_c²/(2·J)) mit J = m₀ρ₀² + Σ m_j R_c²/2."""
    for geo, soll in (('G0', (155.725, 140.353, 120.651)), ('G60h', (241.302, 193.523, 149.680))):
        for r0, f in zip((0.35, 0.5, 0.7), soll):
            kz = satz(0.462, K_STEIF, C_STEIF, geo=geo, rho0=r0 * 0.1).kennzahlen()
            assert kz['f_kipp'] == pytest.approx([f, f], abs=1e-3)
            assert kz['f_hub'] == pytest.approx(120.0, abs=1e-4)
    assert satz(1.0, 1e4, 16.0).kennzahlen()['f_kipp'] == pytest.approx([19.7407, 19.7407], abs=1e-4)
    a = al.Aufbau()
    J = a.m0 * 0.05 ** 2 + a.m.sum() * 0.1 ** 2 / 2
    assert a.kennzahlen()['f_kipp'][0] == pytest.approx(a.f_n * np.sqrt(M * 0.1 ** 2 / (2 * J)), rel=1e-9)


@pytest.mark.parametrize('geo', ['G0', 'G60h', 'zentral'])
def test_summe_der_zellen_gleich_summenkraft(geo):
    """Bei symmetrischer Lage entkoppeln Hub und Kippen: Σ F_c(t) = N(t) = N_1FG(t) für alle Laufarten, voll und
    k ≤ 12; die Mittel der Zellkräfte sind die statischen Zelllasten."""
    r = al.bewerte(al.Aufbau(geometrie_name=geo), kmax=12)['roh']
    for name in ('voll', 'band'):
        assert np.abs(r[name]['Fz'].sum(1) - r[name]['N']).max() < 1e-9
        assert r[name]['abw_1FG'].max() < 1e-9
    assert np.abs(r['voll']['Fz'].mean(-1) - r['F0']).max() < 1e-9


def test_ungleiche_zellen_zeitbereich():
    """K_c = 1e6 / 0,25e6 / 0,25e6 N/m (V1, G0, ζ = 0,05), Pilot (130°, 230°): Zellkräfte und Summe gleich einer
    Zeitbereichsintegration der Bewegungsgleichungen (scipy.signal.lsim, Halteglied 1. Ordnung, 16 000 Schritte
    je Periode, vier Perioden aus der Ruhelage; Restfehler aus Interpolation und Einschwingen ≈ 4e-6 N). Die
    ausgewiesene Summe ist Σ F_c; die 1-FG-Summe weicht hier um 0,21 N ab (hubartige Mode 178,6 Hz statt
    f_n = 241,8 Hz), über alle Laufarten um 0,3765 N (Nachrechnung 10/2026), und die Prüfung warnt."""
    kc = np.array([1e6, 0.25e6, 0.25e6])
    a = al.Aufbau(K=kc.sum(), k_rel=kc)
    phi = np.array([0.0, 130.0, 230.0])
    r = a.loesen([phi])
    # Bewegungsgleichung unabhängig aufgebaut: Zellen und Module auf R_c = 0,1 m bei 0°, 120°, 240°, Scheibe ρ₀ = R_c/2
    ang = np.radians([0.0, 120.0, 240.0])
    B = np.c_[np.ones(3), 0.1 * np.cos(ang), 0.1 * np.sin(ang)]
    m, m0, cc = np.full(3, 0.1), 0.35, kc / kc.sum() * a.C
    Mq = np.diag([m0, m0 * 0.05 ** 2, m0 * 0.05 ** 2]) + sum(mj * np.outer(bj, bj) for mj, bj in zip(m, B))
    Kq, Cq, Mi = B.T @ (kc[:, None] * B), B.T @ (cc[:, None] * B), np.linalg.inv(Mq)
    A = np.block([[np.zeros((3, 3)), np.eye(3)], [-Mi @ Kq, -Mi @ Cq]])
    Bu = np.vstack([np.zeros((3, 3)), -Mi @ B.T])                  # Eingang m_j·a_j(t)
    Cy = np.hstack([-kc[:, None] * B, -cc[:, None] * B])            # dynamische Zellkräfte
    n, f = 16000, a.f
    t = np.arange(4 * n + 1) / (n * f)
    s = (f * t[:, None] - phi / 360.0) % 1.0
    th, tf = al.THOLD, 1 - al.THOLD
    acc = 8e-3 * f ** 2 * np.where(s < th, -np.pi ** 2 / th * np.sin(np.pi * s / th),
                                    np.pi ** 2 / tf * np.sin(np.pi * (s - th) / tf))
    _, y, _ = signal.lsim(signal.StateSpace(A, Bu, Cy, np.zeros((3, 3))), m * acc, t)
    F0 = np.linalg.solve(B.T, al.G * np.r_[0.65, 0.0, 0.0])
    Fz = (F0 + y[-n - 1:-1:al.OVERSAMPLE]).T                       # letzte Periode auf dem Raster N_θ
    assert np.abs(Fz - r['voll']['Fz'][0]).max() < 2e-5
    assert np.abs(Fz.sum(0) - r['voll']['N'][0]).max() < 2e-5
    assert r['voll']['abw_1FG'][0] == pytest.approx(0.2054, abs=5e-4)              # Regressionswert
    p = al.pruefung(a)
    assert p['modell']['warnung'] and p['modell']['abw_1FG'] == pytest.approx(0.3765, abs=5e-4)
    assert a.kennzahlen()['f1'] == pytest.approx(178.6, abs=0.05)


def test_starrer_grenzfall_der_zellen():
    """Sehr steifer Kontakt nähert die starre Auflage (Hebelgesetz T = B⁻ᵀ·bᵀ) an."""
    phi = [(0.0, 110.0, 250.0)]
    r_s = satz(0.462, geo='G60h').loesen(phi)
    r_k = satz(0.462, 1e12, 0.0, geo='G60h').loesen(phi)
    assert np.abs(r_s['voll']['Fz'] - r_k['voll']['Fz']).max() < 1e-4


# ── gemessene Harmonische, Δδ, ∂ŷ/∂f ─────────────────────────────────────────────────────────────────
def test_superposition_gemessener_einzelmodule():
    """Einzelmodulläufe aus linear_solver.py (ein Modul ≡ synchrone Phasung mit μ/3, Präreg A2.1) als gemessene
    N_k⁽ʲ⁾: Die Superposition gibt linear_solver.solve() am Triphasik-Punkt und an einem Piloten."""
    _, N1 = ls.waveform(0.0, 0.0, mu=1.0 / 3)
    Nk1 = (2 * np.fft.rfft(N1) / N1.size)[1:]
    a = al.Aufbau(**al.REFERENZ, N_mess=np.tile(Nk1, (3, 1)))
    pts = np.array([(120.0, 240.0), (110.0, 250.0)])
    r, s = a.loesen(pts), ls.solve(pts[:, 0], pts[:, 1])
    assert np.abs(r['voll']['F_min'] - s['F_min']).max() <= 1e-9
    assert np.abs(r['voll']['gamma1'] - s['F_skew']).max() <= 1e-9
    m = al.Aufbau(geometrie_name='G60h')                  # Zellen: Modellharmonische k ≤ 9 als Messung
    g = al.Aufbau(geometrie_name='G60h', N_mess=2 * m.Rs[:, 1:10], N_mess_zellen=2 * m.Rc[:, :, 1:10])
    rm, rg = m.loesen(pts, kmax=9), g.loesen(pts)
    assert np.abs(rg['voll']['Fz'] - rm['band']['Fz']).max() < 1e-12
    assert np.abs(rg['voll']['N'] - rm['band']['N']).max() < 1e-12
    with pytest.raises(ValueError):
        al.ableitung_f(g, pts)


def test_indexbezogene_messung_mit_delta_delta():
    """Auf den Indeximpuls bezogene Harmonische N_k⁽ʲ⁾·e^{−ikΔδ_j} (Präreg A1: φ^P = φ + Δδ) mit delta_delta
    zurückgedreht geben die profilbezogene Superposition; ohne Drehung verschiebt schon Δδ₂ = 1° den Schnitt um
    mehr als die PB1-Anforderung 0,039 N (Prüfbefund 10/2026: 0,0443 N)."""
    m = al.Aufbau()
    k = np.arange(1, 13)
    dd = np.array([0.0, 1.0, -2.5])
    idx = np.exp(-1j * np.radians(dd)[:, None] * k)
    Ns, Nc = 2 * m.Rs[:, 1:13], 2 * m.Rc[:, :, 1:13]
    pts = [(0.0, p2, 240.0) for p2 in al.SCHNITT]
    soll = m.loesen(pts, kmax=12)['band']
    g = al.Aufbau(N_mess=Ns * idx, N_mess_zellen=Nc * idx[:, None, :], delta_delta=dd).loesen(pts)['voll']
    assert np.abs(g['N'] - soll['N']).max() < 1e-12 and np.abs(g['Fz'] - soll['Fz']).max() < 1e-12
    falsch = al.Aufbau(N_mess=Ns * idx[[0, 1, 0]]).loesen(pts)['voll']              # nur Δδ₂ = 1°, nicht gedreht
    assert np.abs(falsch['F_min'] - soll['F_min']).max() > 0.039


def test_ableitung_f():
    """Starr skaliert N − M·g mit f² (Präreg A4): ∂(F_min − ⟨N⟩)/∂f = 2·(F_min − ⟨N⟩)/f, ∂N_k/∂f = 2·N_k/f,
    ∂γ₁/∂f = 0. Elastisch (V1, G0 symmetrisch, also 1-FG) analytisch ∂N_k/∂f = N_k·(2/f + 2πk·H′(kω)/H(kω))."""
    a = al.Aufbau(K=None)
    pts = [(120.0, 240.0), (110.0, 252.0)]
    r, d = a.loesen(pts, kmax=9), al.ableitung_f(a, pts, kmax=9)
    assert d['F_min_rel'] == pytest.approx(2 * r['band']['F_min_rel'] / a.f, rel=1e-7)
    assert np.abs(d['Nk'] - 2 * r['Nk'] / a.f).max() < 1e-9
    assert np.abs(d['gamma1']).max() < 1e-7
    b = al.Aufbau()
    r, d = b.loesen(pts, kmax=12), al.ableitung_f(b, pts, kmax=12)
    w = 2 * np.pi * b.f * np.arange(1, 13)
    den = b.K - b.M * w ** 2 + 1j * w * b.C
    H = (b.K + 1j * w * b.C) / den
    dH = (1j * b.C * den - (b.K + 1j * w * b.C) * (-2 * b.M * w + 1j * b.C)) / den ** 2
    soll = r['Nk'] * (2 / b.f + 2 * np.pi * np.arange(1, 13) * dH / H)
    assert np.abs(d['Nk'] - soll).max() < 1e-8                  # Differenzenquotient, rel = 1e-4
    assert np.abs(soll).max() > 0.1


# ── Eingaben und Kommandozeile ─────────────────────────────────────────────────────────────────────
def test_ungueltige_eingaben():
    """Klare ValueError statt Tracebacks aus numpy: falsche Modulzahl, f, K, THOLD, k_max, ungedämpfte Resonanz."""
    for kw in (dict(m=(0.1, 0.1)), dict(f=0.0), dict(K=-1.0), dict(thold=1.2), dict(hub=(8e-3, 8e-3)),
               dict(k_rel=(1.0, 0.0, 0.0)), dict(K=M * (2 * np.pi * 120) ** 2, zeta=0.0)):
        with pytest.raises(ValueError):
            al.Aufbau(**kw)
    with pytest.raises(ValueError, match='Resonanz'):
        al.Aufbau(K=M * (2 * np.pi * 120) ** 2, zeta=0.0)          # k = 12 trifft f_n = 120 Hz
    with pytest.raises(ValueError):
        al.Aufbau().loesen([(120.0, 240.0)], kmax=0)


def test_cli_json(capsys):
    """--candidate --json und --point 120 240 --json laufen und geben die Werte der Python-Schnittstelle aus."""
    al.main(['--candidate', '--json'])
    out = json.loads(capsys.readouterr().out)
    assert out['pruefung']['a']['ok'] and out['pruefung']['a']['reserve_zelle'] == pytest.approx(0.41137, abs=1e-5)
    assert out['kennzahlen']['f_n'] == pytest.approx(241.8, abs=0.05)
    al.main(['--point', '120', '240', '--json', '--reference'])
    out = json.loads(capsys.readouterr().out)
    assert out['punkt']['voll']['F_min'][0] == pytest.approx(5.330390, abs=5e-7)


def test_cli_text_und_vorrang(capsys, monkeypatch):
    """Textausgabe: Hub in mm, --Kcells ersetzt --K (Warnung zur 1-FG-Summe), --rigid hat Vorrang, Gleichstand."""
    al.main(['--candidate', '--hub', '8', '--Kcells', '1e6', '0.25e6', '0.25e6'])
    txt = capsys.readouterr().out
    assert 'Hub = 8.000, 8.000, 8.000 mm' in txt and 'K = 1.5e+06 N/m' in txt and 'WARNUNG' in txt
    monkeypatch.setattr(sys, 'argv', ['auslegung.py', '--window', '--rigid', '--K', '1e6'])
    al.main()
    txt = capsys.readouterr().out
    assert 'K = starr' in txt and 'u. a. (101 gleich)' in txt and 'ε-Fenster PFLICHT  [0.4763; 0.7500]' in txt


@pytest.mark.parametrize('argv', [['--kmax', '0'], ['--m', '0.1', '0.1'], ['--hub', '8', '8'], ['--f', '0'],
                                  ['--K=-1e6'], ['--Kcells', '1e6', '0', '0'], ['--thold', '1.2'],
                                  ['--zeta', '0', '--K', str(M * (2 * np.pi * 120) ** 2)]])
def test_cli_fehler(argv):
    """Ungültige Eingaben enden mit argparse-Fehler (Exit-Code 2) statt Traceback oder stillem Unsinn."""
    with pytest.raises(SystemExit) as e:
        al.main(argv + ['--candidate'])
    assert e.value.code == 2
