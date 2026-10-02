"""Tests für code/ereignisloeser.py (ereignisgenauer Löser, Floquet, Einzugsprüfung).

Referenzwerte ohne Quellenangabe im Test stammen aus der Nachrechnung 10/2026 mit einem unabhängig geschriebenen
halbanalytischen Löser (abschnittsweise geschlossene Lösung, Ereignisse per Abtastung und brentq) und einem
DOP853-Ereignislöser; Toleranzen: letzte angegebene Stelle der Referenz, höchstens 0,1 %.
Schnelle Tests laufen standardmäßig (zusammen ca. 25 s); langsame (@slow, ca. 35 s) mit PCMMS_SLOW=1.

Matthias Früh · PCMMS · Oktober 2026
"""
import math
import os
import subprocess
import sys
import warnings

import numpy as np
import pandas as pd
import pytest

import ereignisloeser as el
import finesweep as fs
import linear_solver as ls

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
with warnings.catch_warnings():                 # Marke „slow“ ohne pytest.ini, daher nicht registriert
    warnings.simplefilter('ignore', pytest.PytestUnknownMarkWarning)
    _SLOW = pytest.mark.slow
LANGSAM = os.environ.get('PCMMS_SLOW') == '1'


def slow(f):
    return _SLOW(pytest.mark.skipif(not LANGSAM, reason='langsam; mit PCMMS_SLOW=1 aktivieren')(f))


# ── Kontaktast ──────────────────────────────────────────────────────────────
def test_kontaktast_gleich_linear_solver():
    """Periodische Lösung bei (120°, 240°) gegen die FFT-Lösung von linear_solver: Wellenform und Stichproben-
    Kenngrößen auf ≤ 1e-6 N (linear_solver tastet das Profil mit 16 000 Punkten je Periode ab; feinere Raster
    ändern dort weniger als 1e-6). Floquet-Multiplikatoren analytisch exp(−C·T/(2M))."""
    sy = el.referenz(120.0, 240.0)
    zs, mu, ok = el.kontaktorbit(sy)
    assert ok
    np.testing.assert_allclose(np.abs(mu), math.exp(-sy.C * sy.T / (2 * sy.M)), rtol=1e-12)
    r = el.simulate(sy, *zs, 0.0, 1, keep=True)
    tt, N_lin = ls.waveform(120.0, 240.0)
    assert np.abs(el.abtasten(sy, r, tt)[2] - N_lin).max() <= 1e-6
    k, lin = el.kenngroessen(r), ls.solve(120.0, 240.0)
    assert k['liftoff'] == 0.0 and k['liftoff_s'] == 0.0
    assert abs(k['F_min_s'] - 5.330390) <= 1e-6                # Referenzsatz (Feinsweep-Spitze)
    for q in ('F_min', 'F_max', 'F_skew'):
        assert abs(k[q + '_s'] - lin[q][0]) <= 1e-6, q
    assert k['F_min'] <= k['F_min_s'] and k['F_min_s'] - k['F_min'] < 1e-6     # exaktes Minimum zwischen Stichproben
    assert abs(k['dF']) <= 1e-12 and abs(k['rest']) <= 1e-12   # Zeitmittel exakt M·g auf dem Orbit


def test_zeitmittel_gleich_mg_bis_randterm():
    """Impulssatz: ⟨N⟩ − M·g = R = M·Δv_S/T_w exakt, auch im Einschwingen (Standardstart der Engine, Fenster der
    ersten 2 s). Der Rest misst nur die Quadratur (Gauß-Legendre) und liegt auf Rundungsniveau."""
    sy = el.referenz(120.0, 240.0)
    k = el.kenngroessen(el.simulate(sy, sy.ruhelage(), 0.0, 0.0, 20))
    assert abs(k['R']) > 1e-4                                   # Einschwingen trägt zum Fenstermittel bei
    assert abs(k['rest']) <= 1e-12


@pytest.mark.parametrize('datei, c2, c3, profil, phi2, phi3', [
    ('sweep_19x19.csv', 'phi2_deg', 'phi3_deg', 'egg', 94.737, 227.368),
    ('sweep_19x19.csv', 'phi2_deg', 'phi3_deg', 'egg', 113.684, 227.368),
    ('sweep_19x19.csv', 'phi2_deg', 'phi3_deg', 'egg', 132.632, 265.263),
    ('sweep_7x7_sinus.csv', 'phi2', 'phi3', 'sinus', 102.85714285714286, 205.71428571428572)])
def test_kontaktpunkte_gleich_csv(datei, c2, c3, profil, phi2, phi3):
    """Liftoff-freie Rasterpunkte der Engine-Datensätze: Stichproben-Kenngrößen wie in linear_solver.validate auf
    ≤ 1e-4 (CSV mit sechs Nachkommastellen, RK4-Fehler einige 1e-6)."""
    df = pd.read_csv(os.path.join(DATA, datei))
    row = df[(np.abs(df[c2] - phi2) < 1e-6) & (np.abs(df[c3] - phi3) < 1e-6)].iloc[0]
    assert row.liftoff == 0
    sy = el.referenz(phi2, phi3, profil=profil)
    zs, _, ok = el.kontaktorbit(sy)
    assert ok
    k = el.kenngroessen(el.simulate(sy, *zs, 0.0, 1))
    assert abs(k['F_mean'] - row.F_mean) <= 1e-5
    for q in ('F_min', 'F_max', 'F_skew'):
        assert abs(k[q + '_s'] - row[q]) <= 1e-4, q


def test_stichprobe_gegen_finesweep(monkeypatch):
    """Gleicher Anfangszustand (Standardstart), gleiche Stichprobenzeiten: Abweichung zur Festschritt-RK4
    (finesweep.run, hier auf 1 s verkürzt, Auswertung 0,5–1 s) im Rahmen der RK4-Genauigkeit (≈ 3e-6 N)."""
    monkeypatch.setattr(fs, 'N_STEPS', int(round(1.0 / fs.DT)))
    monkeypatch.setattr(fs, 'N_BURN', int(round(0.5 / fs.DT)))
    out, _ = fs.run([113.684], [227.368])
    sy = el.referenz(113.684, 227.368)
    k = el.kenngroessen(el.simulate(sy, sy.ruhelage(), 0.0, 0.0, 10), 5, 10)
    assert out['liftoff'][0] == 0.0 and k['liftoff_s'] == 0.0
    for q, tol in (('F_mean', 1e-6), ('F_min', 1e-5), ('F_max', 1e-5), ('F_skew', 1e-5)):
        assert abs(out[q][0] - k[q + '_s']) <= tol, q


# ── Liftoff-Zustände der Referenz ───────────────────────────────────────────
def test_satelliteninsel_bistabil():
    """Insel (35°, 116°): Kontaktorbit F_min 0,3665 N, F_max 19,812 N, Schiefe 0,82305, |μ| 0,2921; Hüpfzustand
    (Newton ab dem Zustand nach 3 s Standardstart) λ 75,8154 %, F_max 39,473 N, Schiefe 1,69813, |μ| 0,7426,
    Fixpunkt (10,100853 mm, −0,170574 m/s)."""
    sy = el.referenz(35.0, 116.0)
    zs, mu, ok = el.kontaktorbit(sy)
    k = el.kenngroessen(el.simulate(sy, *zs, 0.0, 1))
    assert ok and k['liftoff'] == 0.0
    assert k['F_min'] == pytest.approx(0.3665, abs=1e-4)
    assert k['F_max'] == pytest.approx(19.812, abs=1e-3) and k['F_skew'] == pytest.approx(0.82305, abs=1e-5)
    assert abs(mu[0]) == pytest.approx(0.2921, abs=1e-4)
    r = el.simulate(sy, sy.ruhelage(), 0.0, 0.0, 30, auswertung=False)
    o = el.newton(sy, (r['PX'][-1], r['PV'][-1]), 3.0, 1)
    assert o['konvergiert']
    assert o['z'][0] == pytest.approx(10.100853e-3, abs=1e-9) and o['z'][1] == pytest.approx(-0.170574, abs=1e-6)
    np.testing.assert_allclose(np.abs(o['mu']), 0.7426, atol=1e-4)
    rh = el.simulate(sy, *o['z'], 3.0, 40)
    assert el.periode(rh) == (1, 3.0)                           # streng periodisch ab dem Fixpunkt
    k = el.kenngroessen(rh)
    assert k['liftoff'] == pytest.approx(75.8154, abs=1e-4)
    assert k['F_max'] == pytest.approx(39.473, abs=1e-3) and k['F_skew'] == pytest.approx(1.69813, abs=1e-5)
    assert k['aufsetzer_je_periode'] == 1.0 and abs(k['dF']) < 1e-11


@pytest.mark.parametrize('t0, dv, huepft', [(0.0, 0.10, False), (0.0, -0.10, True), (0.0, 0.20, False),
                                             (0.0, 0.15, True), (0.05, 0.07, True), (0.05, -0.07, False)])
def test_insel_stoesse_auf_den_kontaktorbit(t0, dv, huepft):
    """Stoß Δv auf den Kontaktorbit der Insel zur Phase t₀ (Stoßtabelle der Nachrechnung: bei t₀ = 0 führt −0,10 m/s
    in den Hüpfzustand, +0,10 und +0,20 m/s nicht; bei t₀ = T/2 +0,07 m/s ja, −0,07 m/s nein). +0,15 m/s bei t₀ = 0
    hüpft: Das Einzugsgebiet ist nicht monoton, kritischer_wurf() meldet nur die erste Grenze von unten."""
    w = el.wurf(el.referenz(35.0, 116.0), dv, t0, start='orbit', n_per=80, n_eval=20)
    assert w['zustand'] == ('Hüpfen' if huepft else 'Kontaktast')
    if huepft:
        assert w['liftoff'] == pytest.approx(75.8154, abs=1e-3)


def test_synchron_p2():
    """(0°, 0°) vom Standardstart: streng 2-periodisch (P2, ein Aufsetzer je Periode) mit λ 75,7874 %,
    F_max 41,107 N; der Hüpfzustand wird nach ≈ 5 s erreicht (lose Wiederkehr 1e-6 m/s, 1e-8 m)."""
    sy = el.referenz(0.0, 0.0)
    r = el.simulate(sy, sy.ruhelage(), 0.0, 0.0, 100)
    p, t_e = el.periode(r, n_last=20, tol_v=1e-6, tol_x=1e-8)
    assert p == 2 and 3.0 < t_e < 7.0
    k = el.kenngroessen(r, 80, 100)
    assert k['liftoff'] == pytest.approx(75.7874, abs=1e-4) and k['F_max'] == pytest.approx(41.107, abs=1e-3)


def test_hotspot_fenster_5_15():
    """Hot-Spot (0°, 208,421°), Standardstart: ab ≈ 5 s auf dem P1-Attraktor (lose Wiederkehr 1e-3 m/s, 1e-4 m:
    4,8 s), v_S(5 s) = −0,37443 m/s (Attraktor −0,37412), im Fenster 5–15 s ⟨N⟩ − M·g = +0,0205 mN,
    λ 75,0847 %, F_max 38,489 N. Die Engine (RK4, 50 µs) liefert dort −43,46 mN aus einem langen Scheintransienten.
    Läuft in < 1 s und deshalb standardmäßig; die längere Variante steht unten unter @slow."""
    sy = el.referenz(0.0, 208.421)
    r = el.simulate(sy, sy.ruhelage(), 0.0, 0.0, 150)
    k = el.kenngroessen(r, 50, 150)
    assert 1e3 * k['dF'] == pytest.approx(0.0205, abs=1e-4)
    assert abs(k['rest']) < 1e-12
    assert k['liftoff'] == pytest.approx(75.0847, abs=1e-4) and k['F_max'] == pytest.approx(38.489, abs=1e-3)
    assert r['PS'][50] == pytest.approx(-0.37443, abs=1e-5) and r['PS'][150] == pytest.approx(-0.37412, abs=1e-5)
    p, t_e = el.periode(r, tol_v=1e-3, tol_x=1e-4)
    assert p == 1 and t_e == pytest.approx(4.8, abs=0.15)


def test_rampe_waehlt_kontaktorbit_an_der_insel():
    """Frequenzhochlauf T_r = 2 s (solve_ivp während der Rampe) führt an der Insel auf den Kontaktorbit
    (Standardstart dagegen auf den Hüpfzustand, test_satelliteninsel_bistabil)."""
    sy = el.referenz(35.0, 116.0)
    r = el.simulate(sy, sy.ruhelage(), 0.0, 0.0, 40, rampe=2.0)
    k = el.kenngroessen(r, 30, 40)
    assert k['liftoff'] == 0.0 and k['F_min'] == pytest.approx(0.3665, abs=1e-4)
    assert abs(el.kenngroessen(r)['rest']) < 1e-9                # DOP853-Genauigkeit während der Rampe


# ── V1-Kandidat (3×100 g, 8 mm, 10 Hz, K = 1,5e6 N/m, ζ = 0,05), synchron ───
@pytest.fixture(scope='module')
def v1():
    return el.kandidat()


@pytest.fixture(scope='module')
def v1_wurf(v1):
    """Wurf aus der statischen Ruhelage bei t₀ = 0 wie in der Nachrechnung, 16 s, Auswertung der letzten 4 s."""
    return {dv: el.wurf(v1, dv, 0.0, start='ruhe', n_per=160, n_eval=40) for dv in (0.25, 0.30)}


def test_v1_huepfschwelle(v1, v1_wurf):
    """0,25 m/s: Rückkehr in den Kontaktast (F_max 13,17 N wie die lineare Lösung); 0,30 m/s: dauerhafter
    Hüpfzustand, λ 97,987 %, ein Stoß je Periode mit Stoßspitze 483,66 N (≈ 76·M·g)."""
    w = v1_wurf[0.25]
    assert w['zustand'] == 'Kontaktast' and w['F_max'] == pytest.approx(13.17, abs=0.01)
    w = v1_wurf[0.30]
    assert w['zustand'] == 'Hüpfen' and w['aufsetzer_je_periode'] == 1.0
    assert w['liftoff'] == pytest.approx(97.987, abs=1e-3)
    assert w['stoss_spitze'] == pytest.approx(483.66, abs=0.01) and w['F_max'] == w['stoss_spitze']
    assert w['stoss_spitze_max'] > w['stoss_spitze']            # erster Landestoß nach dem Wurf ist höher


def test_v1_wurf_vom_kontaktast(v1):
    """Gleiche Klassifikation beim Start auf dem Kontaktast (Wurf als Geschwindigkeitsstoß auf den Orbitzustand)."""
    _, _, ok = el.kontaktorbit(v1)
    assert ok
    w = el.wurf(v1, 0.30, 0.0, start='orbit', n_per=160, n_eval=40)
    assert w['zustand'] == 'Hüpfen' and w['stoss_spitze'] == pytest.approx(483.66, abs=0.01)
    assert w['impuls'] == pytest.approx(0.65 * 0.30)


def test_v1_huepforbit_floquet(v1):
    """Newton auf den Hüpforbit: P1 mit Aufsetzen bei t/T = 0,2485, komplexe Multiplikatoren mit |μ| ≈ e
    (Stoßzahl des Engine-Kontakts 0,8588; das Produkt der Multiplikatoren ist ≈ e², Abweichung durch die
    Schwerkraft während des Stoßes), stabil."""
    r = el.simulate(v1, v1.ruhelage(), 0.30, 0.0, 120, auswertung=False)
    o = el.newton(v1, (r['PX'][-1], r['PV'][-1]), 12.0, 1)
    assert o['konvergiert'] and np.all(np.abs(o['mu']) < 1)
    np.testing.assert_allclose(np.abs(o['mu']), el.e_kv_geklippt(0.05), atol=2e-3)
    a = el.simulate(v1, *o['z'], 12.0, 1)['aufsetzer']
    assert a.shape[0] == 1 and (a[0, 0] - 12.0) / v1.T == pytest.approx(0.2485, abs=1e-4)
    assert a[0, 5] == pytest.approx(483.66, abs=0.01)


# ── Kontaktgesetze ──────────────────────────────────────────────────────────
def test_ivp_gleich_geschlossen_und_hc_grenzfall():
    """Gegenprobe der beiden Integrationswege an der Insel vom Standardstart (Liftoff mit Aufsetzern): Kelvin-
    Voigt über solve_ivp (DOP853, rtol 1e-11) gegen die geschlossene Lösung, und Hunt-Crossley mit n = 1, α = 0
    gegen Kelvin-Voigt mit C = 0 (identisches Gesetz): Poincaré-Zustände auf ≤ 1e-10 m bzw. 1e-9 m/s."""
    sy = el.referenz(35.0, 116.0)
    for s_a, s_b, met in ((sy, sy, 'ivp'), (sy.mit(C=0.0), sy.mit(C=0.0, gesetz='hc', n=1.0, alpha=0.0), 'auto')):
        ra = el.simulate(s_a, s_a.ruhelage(), 0.0, 0.0, 5)
        rb = el.simulate(s_b, s_b.ruhelage(), 0.0, 0.0, 5, methode=met)
        assert ra['ntd'].sum() >= 4 and ra['ntd'].sum() == rb['ntd'].sum()
        assert np.abs(ra['PX'] - rb['PX']).max() <= 1e-10 and np.abs(ra['PV'] - rb['PV']).max() <= 1e-9
        assert el.kenngroessen(ra)['liftoff'] == pytest.approx(el.kenngroessen(rb)['liftoff'], abs=1e-7)


@pytest.mark.parametrize('zeta', [0.02, 0.05, 0.2, 1.0, 1.2, 2.0])
def test_stoss_kelvin_voigt(zeta):
    """Einzelstoß ohne Schwerkraft: Stoßzahl gleich der geschlossenen Formel des geklippten Kontakts (größer als
    exp(−πζ/√(1−ζ²))); Energiebilanz ΔE = Dämpfungsarbeit + Federenergie bei der Ablösung. ζ ≥ 1: überkritische
    Formel gegen solve_ivp (der geschlossene Weg setzt ζ < 1 voraus), stetig bei ζ = 1 (e = e⁻²)."""
    sy = el.kandidat(zeta=zeta)
    o = el.stoss(sy, 0.5)
    assert o['e'] == pytest.approx(el.e_kv_geklippt(zeta), abs=1e-9)
    if zeta < 1:
        assert o['e'] > math.exp(-math.pi * zeta / math.sqrt(1 - zeta**2))
    assert o['dE'] == pytest.approx(o['D'] + o['U'], rel=1e-8) and o['U'] > 0
    for z in (1 - 1e-7, 1 + 1e-7):
        assert el.e_kv_geklippt(z) == pytest.approx(math.exp(-2.0), abs=1e-6)


def test_stoss_mit_hub_je_modul():
    """Der Einzelstoß ignoriert die Anregung; ein Ausgangssystem mit Hub je Modul (Einzelmodullauf) ist zulässig."""
    o = el.stoss(el.kandidat().mit(hub=(8e-3, 0.0, 0.0)), 0.5)
    assert o['e'] == pytest.approx(el.e_kv_geklippt(0.05), abs=1e-9)
    with pytest.raises(ValueError):
        el.stoss(el.kandidat(), -0.5)


@pytest.mark.parametrize('n', [1.0, 1.5])
def test_stoss_hunt_crossley(v1, n):
    """Hunt-Crossley: Stoßzahl gleich der exakten Beziehung c·v(1 + e) = ln((1 + c·v)/(1 − c·v·e)), unabhängig
    von n; für kleine α·v gilt e = 1 − α·v + (α·v)² + O((α·v)³) (Koeffizient dritter Ordnung ≈ −1,1, daher
    Schranke 2·(α·v)³); Energiebilanz ΔE = D (Ablösung bei δ = 0, U = 0). Der Abgleich hc_aequivalent trifft
    die Stoßzahl des Engine-Kontakts bei v_ref = 0,5 m/s."""
    hc = el.hc_aequivalent(v1, 0.05, n=n)
    for v in (0.02, 0.5):
        o = el.stoss(hc, v)
        assert o['e'] == pytest.approx(el.e_hc(hc.alpha, v), abs=1e-8)
        assert o['dE'] == pytest.approx(o['D'], rel=1e-7) and o['U'] < 1e-20
    av = hc.alpha * 0.02
    assert abs(el.stoss(hc, 0.02)['e'] - (1 - av + av**2)) < 2 * av**3
    assert el.e_hc(hc.alpha, 0.5) == pytest.approx(el.e_kv_geklippt(0.05), abs=1e-12)


def test_v1_kontaktgesetze_vergleich(v1, v1_wurf):
    """Wurf 0,30 m/s am V1-Kandidaten mit Hunt-Crossley (n = 1,5, gleiche Tangentensteifigkeit in der Ruhelage,
    gleiche Stoßzahl bei 0,5 m/s): ebenfalls Hüpfen mit einem Stoß je Periode; die Stoßspitze ist wegen der
    Hertz-Versteifung bei großer Eindrückung rund doppelt so hoch (Plausibilität, keine Referenz)."""
    hc = el.hc_aequivalent(v1, 0.05)
    w = el.wurf(hc, 0.30, 0.0, start='ruhe', n_per=40, n_eval=10)
    assert w['zustand'] == 'Hüpfen' and w['aufsetzer_je_periode'] == 1.0 and w['liftoff'] > 95.0
    assert 1.5 < w['stoss_spitze'] / v1_wurf[0.30]['stoss_spitze'] < 3.0


@pytest.mark.parametrize('zeta', [0.3, 0.52, 0.9, 1.2, 3.0])
def test_hc_aequivalent_grosse_daempfung(zeta):
    """Der Abgleich gelingt für jedes ζ (e_hc fällt streng in α und geht gegen 0); für c·v > 1 rechnet e_hc
    über die Lambertsche W-Funktion, stetig an c·v = 1 und mit Residuum der exakten Beziehung auf Rundungsniveau
    (nur bis c·v = 5 prüfbar, darüber ist 1 − c·v·e ≈ (1 + c·v)·e^{−1−c·v} zu klein; dort diese Asymptotik)."""
    hc = el.hc_aequivalent(el.referenz(), zeta)
    assert el.e_hc(hc.alpha, 0.5) == pytest.approx(el.e_kv_geklippt(zeta), abs=1e-12)
    for a in (1.0 - 1e-9, 1.0 + 1e-9, 2.0, 5.0):
        e = el.e_hc(a / 1.5, 1.0)
        assert abs(a * (1 + e) - math.log((1 + a) / (1 - a * e))) < 1e-12
    assert el.e_hc((1 - 1e-9) / 1.5, 1.0) == pytest.approx(el.e_hc((1 + 1e-9) / 1.5, 1.0), abs=1e-8)
    a = 20.0
    assert 1 - a * el.e_hc(a / 1.5, 1.0) == pytest.approx((1 + a) * math.exp(-1 - a), rel=1e-6)


def test_startzustaende():
    """imp: v_S(t₀) = 0; orbit für Hunt-Crossley und überkritisches Kelvin-Voigt (ζ = 1,2) über Newton ab der
    Ruhelage: Fixpunkt der Periodenabbildung ohne Flugphase. kontaktorbit lehnt ζ ≥ 1 verständlich ab."""
    sy = el.referenz(120.0, 240.0)
    for t0 in (0.0, 0.037):
        z = el.startzustand(sy, 'imp', t0)
        assert z[0] == sy.ruhelage() and abs(z[1] + float(sy.v_mod(t0))) < 1e-15
    s_od = sy.mit(C=el.c_aus_zeta(1.2, sy.K, sy.M))
    with pytest.raises(ValueError, match='ζ < 1'):
        el.kontaktorbit(s_od)
    for s_ in (el.hc_aequivalent(sy, 0.0992), s_od):
        zs = el.startzustand(s_, 'orbit')
        r = el.simulate(s_, *zs, 0.0, 1)
        assert r['tflug'][0] == 0.0 and abs(r['PX'][1] - zs[0]) < 1e-12 and abs(r['PV'][1] - zs[1]) < 1e-10
    with pytest.raises(ValueError, match='--start std'):
        el.startzustand(el.referenz(0.0, 0.0), 'orbit')


@pytest.mark.parametrize('hub, t0_T', [((8e-3,) * 3, 0.25), ((8e-3,) * 3, 0.375), ((8e-3,) * 3, 0.75),
                                       ((8e-3,) * 3, 0.875), ((8e-3, 0.0, 0.0), 0.875)])
def test_startzustand_hunt_crossley_am_kandidaten(v1, hub, t0_T):
    """Abnahmebefund: Ab der Ruhelage divergierte Newton für Hunt-Crossley am steifen Kandidaten an diesen
    Wurfphasen (synchron und L1) in den Flug, und startzustand meldete fälschlich „kein Kontaktast“. Mit dem
    Start am Kelvin-Voigt-Orbit gleicher Tangentensteifigkeit: Fixpunkt ohne Flugphase."""
    hc = el.hc_aequivalent(v1.mit(hub=hub), 0.05)
    t0 = t0_T * hc.T
    zs = el.startzustand(hc, 'orbit', t0)
    r = el.simulate(hc, *zs, t0, 1)
    assert r['tflug'][0] == 0.0 and abs(r['PX'][1] - zs[0]) < 1e-12 and abs(r['PV'][1] - zs[1]) < 1e-10


def test_kenngroessen_fenster_und_kurzer_lauf():
    """Auswertefenster außerhalb des Laufs wird abgelehnt (früher stilles Umwickeln des Slice). Periodenerkennung
    auch bei kurzen Läufen: (120°, 240°) ist nach 3 s auf dem Kontaktast (|μ|³⁰ ≈ 1e-16), also P1."""
    sy = el.referenz(120.0, 240.0)
    r = el.simulate(sy, sy.ruhelage(), 0.0, 0.0, 30)
    for c0, c1 in ((-5, 30), (10, 31), (20, 20)):
        with pytest.raises(ValueError):
            el.kenngroessen(r, c0, c1)
    assert el.periode(r)[0] == 1
    p, t_e = el.periode(el.simulate(sy, sy.ruhelage(), 0.0, 0.0, 1, auswertung=False))
    assert p == -1 and math.isnan(t_e)                          # eine Periode reicht für keine Aussage


def test_kritischer_wurf_bisektion(v1):
    """Bisektion zwischen dem letzten zurückkehrenden und dem ersten hüpfenden Rasterwurf (V1, t₀ = 0, Start in
    der Ruhelage, 10-s-Läufe; mit 16 s gleich): 0,28 → Rückkehr, 0,30 → Hüpfen, dann 0,29 → Rückkehr, 0,295 →
    Hüpfen (vom Kontaktast meldet die CLI ebenfalls 0,2950 m/s)."""
    o = el.kritischer_wurf(v1, 0.0, [0.28, 0.30], bisekt=2, start='ruhe', n_per=100, n_eval=30)
    assert not o['start_huepft'] and len(o['laeufe']) == 4
    assert o['v_rueck'] == pytest.approx(0.29) and o['v_krit'] == pytest.approx(0.295)
    assert 0.29 < o['v_krit'] <= 0.30 and o['impuls_krit'] == pytest.approx(0.65 * 0.295)


def test_kritischer_wurf_start_huepft():
    """Insel (35°, 116°) aus der Ruhelage: schon ohne Wurf Hüpfzustand. Früher wurde Δv = 0 ungerechnet als
    Rückkehr gewertet (Scheinschwelle 0,0025 m/s); jetzt wird der Start nachgerechnet und gemeldet."""
    o = el.kritischer_wurf(el.referenz(35.0, 116.0), 0.0, [0.02], bisekt=3, start='ruhe', n_per=60, n_eval=10)
    assert o['start_huepft'] and o['v_rueck'] is None and o['v_krit'] is None
    assert [w['dv'] for w in o['laeufe']] == [0.0, 0.02]


def test_cli_als_skript():
    """Aufruf als Skript (eigener Prozess): Einzelstoß beider Kontaktgesetze."""
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    prog = os.path.join(HERE, '..', 'code', 'ereignisloeser.py')
    out = subprocess.run([sys.executable, prog, '--candidate', '--stoss', '0.5'], capture_output=True, text=True,
                         env=env, timeout=120, check=True).stdout
    assert 'Hunt-Crossley' in out and 'e = 0.85876' in out


def _cli(monkeypatch, capsys, *args):
    """main() im Testprozess (spart den Interpreterstart je Fall); Rückgabe Rückgabewert, stdout, stderr."""
    monkeypatch.setattr(sys, 'argv', ['ereignisloeser.py', *args])
    try:
        el.main()
        rc = 0
    except SystemExit as ex:
        rc = ex.code
    out, err = capsys.readouterr()
    return rc, out, err


@pytest.mark.parametrize('args, erwartet', [
    (('--point', '120', '240', '--start', 'orbit', '--t-sim', '1', '--t-eval', '0.5'), ('F_min 5.33039',)),
    (('--candidate', '--orbit', '--t-sim', '4'), ('Kontaktast: existiert', '|μ| = 0.0005', 'stabil')),
    (('--point', '120', '240', '--zeta', '0.6', '--t-sim', '1', '--t-eval', '0.5'), ('ζ = 0.6000', 'P1')),
    (('--point', '120', '240', '--zeta', '1.2', '--t-sim', '1', '--t-eval', '0.5'), ('ζ = 1.2000', 'λ = 0.0000 %')),
    (('--point', '120', '240', '--rampe', '0.2', '--t-sim', '1', '--t-eval', '0.5', '--law', 'beide'),
     ('Kelvin-Voigt K', 'Hunt-Crossley n = 1.5', 'Rampe 0.2 s')),
    (('--point', '35', '116', '--einzug', '--start', 'std', '--wurfphase', '0', '--vmax', '0.04', '--t-sim', '6',
      '--t-eval', '1'), ('schon der Startzustand ohne Wurf hüpft',)),
])
def test_cli_laeufe(monkeypatch, capsys, args, erwartet):
    """Kommandozeile: Einzelstoß, Langlauf, Orbit, große und überkritische Dämpfung mit dem Standardgesetz kv
    (früher Abbruch im immer mitgebildeten Hunt-Crossley-Gegenstück), Rampe mit beiden Gesetzen, Einzug mit
    hüpfendem Start."""
    rc, out, err = _cli(monkeypatch, capsys, *args)
    assert rc == 0, err
    for txt in erwartet:
        assert txt in out, txt


@pytest.mark.parametrize('args, meldung', [
    (('--point', '0', '0', '--einzug', '--wurfphase', '0', '--t-sim', '2', '--t-eval', '1'), '--start std'),
    (('--point', '120', '240', '--t-sim', '1', '--t-eval', '3'), '--t-eval'),
    (('--candidate', '--einzug', '--wurfphase', '0', '--vmin', '0.5', '--vmax', '0.3'), 'leeres Wurfraster'),
    (('--candidate', '--stoss', '-0.5'), '--stoss'),
    (('--point', '0', '0', '--f', '0'), '--f'),
    (('--point', '35', '116', '--rampe', '0.15', '--t-sim', '1'), 'Rampe'),
])
def test_cli_fehleingaben(monkeypatch, capsys, args, meldung):
    """Fehleingaben und Punkte ohne Kontaktast enden mit einer einzeiligen Meldung und Rückgabewert 2 (jede andere
    Ausnahme ließe den Test scheitern)."""
    rc, _, err = _cli(monkeypatch, capsys, *args)
    assert rc == 2 and meldung in err.strip().splitlines()[-1]


# ── langsame Prüfungen (PCMMS_SLOW=1) ───────────────────────────────────────
@slow
def test_hotspot_lang_und_1ulp():
    """Hot-Spot über 60 s und mit der um 1 ULP kleineren Phase 208,42105263157893° (np.linspace des Burn-in-
    Skripts): Attraktor λ 75,0847 %, F_max 38,474 N, Einschwingen (lose) bei beiden ≈ 5 s – robust, anders als
    die 18,8 s der Festschritt-RK4."""
    for phi3, t_ref in ((208.421, 4.8), (208.42105263157893, 5.0)):
        sy = el.referenz(0.0, phi3)
        r = el.simulate(sy, sy.ruhelage(), 0.0, 0.0, 600)
        p, t_e = el.periode(r, tol_v=1e-3, tol_x=1e-4)
        assert p == 1 and t_e == pytest.approx(t_ref, abs=0.2)
        assert el.periode(r)[0] == 1
        k = el.kenngroessen(r, 300, 600)
        assert k['liftoff'] == pytest.approx(75.0847, abs=1e-4) and k['F_max'] == pytest.approx(38.474, abs=1e-3)
        assert abs(k['dF']) < 1e-9


@slow
def test_v1_kritischer_wurf_ueber_wurfphase(v1):
    """Hüpfschwelle im 0,02-m/s-Raster (Start in der Ruhelage wie die Nachrechnung): t₀/T = 0 → 0,30 m/s,
    0,25 → 0,24 m/s, 0,5 → 0,26 m/s, 0,75 → 0,60 m/s; mit ζ = 0,1 bei t₀ = 0 erst 0,32 m/s, mit ζ = 0,2 Rückkehr
    bis 0,60 m/s (ca. 30 s). Grobe Stützwürfe unterhalb der Schwelle (Vollraster der Nachrechnung: am Kandidaten
    kehren alle kleineren Würfe zurück) sichern, dass die Schwelle die erste Grenze von unten ist."""
    for th, v_krit, v0 in ((0.0, 0.30, 0.26), (0.25, 0.24, 0.20), (0.5, 0.26, 0.22), (0.75, 0.60, 0.56)):
        unten = [0.05, 0.15, 0.30, 0.45] if th == 0.75 else [0.10]
        dvs = unten + np.round(np.arange(v0, v_krit + 0.0201, 0.02), 6).tolist()
        o = el.kritischer_wurf(v1, th * v1.T, dvs, start='ruhe')
        assert o['v_krit'] == pytest.approx(v_krit) and o['v_rueck'] == pytest.approx(v_krit - 0.02)
        assert [w['dv'] for w in o['laeufe']] == [d for d in dvs if d < v_krit + 1e-9]
        assert all(w['zustand'] == 'Kontaktast' for w in o['laeufe'][:-1])
        assert o['stoss_spitze'] == pytest.approx(483.7, abs=0.5)
    o = el.kritischer_wurf(el.kandidat(zeta=0.1), 0.0, [0.30, 0.32], start='ruhe')
    assert o['v_krit'] == pytest.approx(0.32)
    o = el.kritischer_wurf(el.kandidat(zeta=0.2), 0.0, [0.3, 0.45, 0.6], start='ruhe')
    assert o['v_krit'] is None and o['v_rueck'] == pytest.approx(0.6) and not o['start_huepft']


@slow
def test_v1_hunt_crossley_rueckkehr(v1):
    """Hunt-Crossley-Kandidat: 0,25 m/s kehrt wie bei Kelvin-Voigt in den Kontaktast zurück (Dauerkontakt über
    solve_ivp, ca. 5 s Rechenzeit)."""
    w = el.wurf(el.hc_aequivalent(v1, 0.05), 0.25, 0.0, start='ruhe', n_per=40, n_eval=10)
    assert w['zustand'] == 'Kontaktast'
