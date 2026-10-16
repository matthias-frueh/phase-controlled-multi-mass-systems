"""Korrekturen an den Kontrollen von AP-12 Stufe 2 (kontrollen.py): Phase der zweiten Harmonischen in E3a
(Korrektur C), Nullkontrolle bei verschwindenden Varianzen (Korrektur D).

Erwartungswerte stammen aus den vorgegebenen komplexen Zeigern bzw. aus einer unabhängigen Rechnung (SciPy), nicht
aus der Implementierung."""
import warnings

import numpy as np
import pytest
from scipy import stats

from pcmms_auswertung import kontrollen, regeln

ENTW = regeln.profil('ENTW-2026-10')


# ── Korrektur C: E3a aus k = 2 ───────────────────────────────────────────────────────────────────────
def _e3_einfach(phiP, delta=(0.0, 0.0, 0.0), n=4, B=50, amp=(1.0, 0.8, 1.2), seed=1):
    """Eine Konfiguration mit Profilphasen phiP [°] (Modul 1: 0°) und echtem Profilphasenfehler delta je Modul bei
    identischer Übertragung T = I: Zellzeiger = Modulzeiger aⱼ·e^{−ik(φⱼ^P + δⱼ)} (k = 1, 2), Indexzeiger
    n_z·e^{−ikφⱼ} mit Δδ = 0, kein Rauschen, keine Unsicherheit."""
    k = np.arange(1, 3)
    C = np.asarray(amp)[:, None] * np.exp(-1j * np.outer(np.radians(np.add(phiP, delta)), k))     # (Modul, k)
    nz = np.full(n, 100)
    Z = nz[:, None, None] * np.exp(-1j * np.outer(np.radians(phiP), k))[None]
    K = {'X': dict(Xz=np.repeat(C[None], n, 0), Z=Z, nz=nz)}
    E0 = [np.repeat((np.eye(3)[j][:, None] * np.asarray(amp)[j] * np.ones(2))[None], n, 0).astype(complex)
          for j in range(3)]
    rng = np.random.default_rng(seed)
    T = np.stack([np.eye(3, dtype=complex)] * 2)
    return kontrollen.e3_auswerten(K, E0, {'X': rng.integers(0, n, (B, n))}, {}, T, np.zeros((3, 2)), np.zeros(3),
                                   np.zeros(3), {}, None, ENTW, rng, 0.0)


def _abw(out, modul, k2=False):
    return out['e3a'][0]['e3a'][f'modul{modul}']['delta_phi_Z_k2_grad' if k2 else 'delta_phi_Z_grad']


def test_e3_k2_exakte_profilphasen_ohne_scheinfehler():
    """T = I, exakte Profilphasen 0°/120°/240°: k = 1 und k = 2 liefern 0° (vor Korrektur C bei k = 2 für die Module 2
    und 3 fälschlich 180°)."""
    out = _e3_einfach((0.0, 120.0, 240.0))
    for j in (2, 3):
        assert _abw(out, j) == pytest.approx(0.0, abs=1e-9)
        assert _abw(out, j, k2=True) == pytest.approx(0.0, abs=1e-9)


@pytest.mark.parametrize('phi2, phi3', [(179.7, 180.4), (359.8, 0.3), (90.0, 270.0), (200.0, 340.0),
                                        (120.0, 240.0)])
@pytest.mark.parametrize('d2, d3', [(0.25, -0.4), (-0.05, 0.12)])
def test_e3_k2_gleich_k1_im_eindeutigen_bereich(phi2, phi3, d2, d3):
    """Phasen über den Argument-Sprung von ±180° und 0°/360° hinweg mit kleinen positiven und negativen echten
    Profilphasenfehlern: k = 1 und k = 2 ergeben beide den vorgegebenen Fehler δⱼ (A2.7, A9.13)."""
    out = _e3_einfach((0.0, phi2, phi3), delta=(0.0, d2, d3))
    for j, d in ((2, d2), (3, d3)):
        assert _abw(out, j) == pytest.approx(d, abs=1e-9)
        assert _abw(out, j, k2=True) == pytest.approx(d, abs=1e-9)


def test_e3_k2_lokal_mit_180_grad_mehrdeutigkeit():
    """Aus k = 2 ist der Profilphasenfehler nur modulo 180° bestimmt (Wertebereich (−90°, 90°]): δ = 100° erscheint bei
    k = 2 als −80°; k = 1 bleibt maßgeblich, k = 2 ist die zusätzliche Diagnose."""
    out = _e3_einfach((0.0, 120.0, 240.0), delta=(0.0, 100.0, -0.2))
    assert _abw(out, 2) == pytest.approx(100.0, abs=1e-9)
    assert _abw(out, 2, k2=True) == pytest.approx(-80.0, abs=1e-9)
    assert _abw(out, 3, k2=True) == pytest.approx(-0.2, abs=1e-9)
    assert '180°' in out['k2_hinweis']


# ── Korrektur D: Nullkontrolle ───────────────────────────────────────────────────────────────────────
def _nk(x, y, eps=0.01):
    with warnings.catch_warnings():
        warnings.simplefilter('error')                                  # keine 0/0- oder Überlaufwarnung
        return kontrollen.nullkontrolle(x, y, eps, ENTW)


def _ohne_testaussage(r):
    regel = ENTW.wert('h0.sammeltest')
    assert r['pruefbar'] is False and r['grund']
    assert r.get('aussage') is None and r.get('lage') is None and r.get('intervall') is None
    assert all(a not in str(r) for a in regel['aussagen']) and 'Gleichheit nachgewiesen' not in str(r)


def test_nullkontrolle_beide_varianzen_null():
    """Zehnmal 0,125 N gegen zehnmal 0 N, ε_ctrl = 0,01 N: Differenz bleibt sichtbar, kein gültiges „kein Unterschied“
    (vor Korrektur D: NaN-Grenzen, prüfbar und „kein Unterschied nachgewiesen“)."""
    r = _nk(np.full(10, 0.125), np.zeros(10))
    _ohne_testaussage(r)
    assert r['differenz'] == pytest.approx(0.125) and r['n_komb'] == 10 and r['n_ref'] == 10
    assert 'varianzen' in r['grund'].lower()


def test_nullkontrolle_gleiche_konstanten_ohne_gleichheitsaussage():
    r = _nk(np.full(8, 0.3), np.full(12, 0.3))
    _ohne_testaussage(r)
    assert r['differenz'] == 0.0 and r['n_komb'] == 8 and r['n_ref'] == 12


def _welch_referenz(x, y):
    with warnings.catch_warnings():         # SciPy warnt bei identischen Werten über Rundung im eigenen Moment
        warnings.simplefilter('ignore', RuntimeWarning)
        res = stats.ttest_ind(x, y, equal_var=False)
    ci = res.confidence_interval(0.95)
    return float(res.df), float(ci.low), float(ci.high)


def test_nullkontrolle_eine_konstante_stichprobe_regulaer():
    """Einseitig verschwindende Varianz bei positiver Gesamtvarianz bleibt auswertbar (ν = n_ref − 1)."""
    y = np.random.default_rng(3).normal(0.0, 0.004, 15)
    x = np.full(10, 0.002)
    r = _nk(x, y)
    nu, lo, hi = _welch_referenz(x, y)
    assert r['pruefbar'] is True and r['nu'] == pytest.approx(nu, rel=1e-12) and nu == pytest.approx(14.0, rel=1e-12)
    assert r['intervall'] == pytest.approx([lo, hi], rel=1e-10, abs=1e-15)
    assert r['aussage'] in ENTW.wert('h0.sammeltest')['aussagen']


def test_nullkontrolle_gewoehnlicher_welch_gegen_scipy():
    rng = np.random.default_rng(5)
    x, y = rng.normal(0.003, 0.002, 30), rng.normal(0.0, 0.005, 12)
    r = _nk(x, y)
    nu, lo, hi = _welch_referenz(x, y)
    assert r['pruefbar'] is True and r['nu'] == pytest.approx(nu, rel=1e-12)
    assert r['intervall'] == pytest.approx([lo, hi], rel=1e-10)
    assert r['differenz'] == pytest.approx(x.mean() - y.mean(), rel=1e-12)
    erwartet = ENTW.wert('h0.sammeltest')['aussagen'][0 if (lo > 0 or hi < 0) else 1]
    assert r['aussage'] == erwartet


def test_nullkontrolle_zu_wenige_und_nicht_endliche_werte():
    r = _nk([0.1], np.zeros(5))
    assert r['pruefbar'] is False and 'zu wenige' in r['grund'] and r.get('aussage') is None
    r = _nk(np.array([1e300, -1e300] * 5), np.random.default_rng(1).normal(0, 1e-3, 10))
    _ohne_testaussage(r)
    assert 'nicht endlich' in r['grund']
