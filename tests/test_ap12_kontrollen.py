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


# ── Korrektur E: Unsicherheit der Übertragungsmatrix in E3 ───────────────────────────────────────────
R_Z = 0.1
ZELLEN = R_Z * np.c_[np.cos(np.radians([0, 120, 240])), np.sin(np.radians([0, 120, 240]))]
MODULE_G60H = 0.5 * R_Z * np.c_[np.cos(np.radians([60, 180, 300])), np.sin(np.radians([60, 180, 300]))]
F_HZ, FN, ZETA = 10.0, 240.0, 0.05
KETTE_P = np.array([[1.0, 2e-6, 0.0], [1.0, -1e-6, 0.0], [1.0, 3e-6, 0.0]])
AMP = (1.0, 0.9, 1.1)


def _t_referenz(g, x, y, module, kette_p, fn, zeta, f, k):
    """Unabhängige Formulierung von T(kω) (Zelle, Modul): baryzentrische Anteile über Flächenverhältnisse,
    G_F = g·e^{−i2πfτ}/(1 + i·f·w), H = (1 + 2iζr)/(1 − r² + 2iζr) mit r = kf/f_n."""
    P = np.c_[x, y]

    def fl(a, b, c):
        return 0.5 * ((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1]))
    w = np.array([[fl(m, P[1], P[2]), fl(P[0], m, P[2]), fl(P[0], P[1], m)] for m in np.asarray(module)]).T / fl(*P)
    fk = k * f
    G = np.array([p[0] * np.exp(-2j * np.pi * fk * p[1]) / (1 + 1j * fk * p[2]) for p in kette_p])
    r = fk / fn
    return np.asarray(g, float)[:, None] * G[:, None] * w * (1 + 2j * zeta * r) / (1 - r ** 2 + 2j * zeta * r)


def _t_nenn():
    return kontrollen.t_aus_parametern(np.ones(3), ZELLEN[:, 0], ZELLEN[:, 1], MODULE_G60H, KETTE_P, FN, ZETA, F_HZ)


def _beschr(C_gxy=None, C_kette=None, C_fz=None, fz_gezogen=False, d_fz=None):
    """Vollständige Unsicherheitsbeschreibung im Format von Teil B nr5; nicht angegebene Kovarianzen sind ausdrücklich
    null. d_fz: Verschiebung von (f_n, ζ) je Störrichtung der Kette (Zelle, Spalte) → [Δf_n, Δζ]."""
    kette = [dict(zelle=c + 1, modell='laufzeit', p=KETTE_P[c].copy(),
                  kovarianz=np.zeros((3, 3)) if C_kette is None else np.asarray(C_kette[c], float)) for c in range(3)]
    richt = [dict(zelle=c + 1, spalte=s, d_fn_zeta=list((d_fz or {}).get((c + 1, s), [0.0, 0.0])))
             for c in range(3) for s in range(sum(np.diag(kette[c]['kovarianz']) > 0))]
    return dict(format=kontrollen.T_FORMAT, modell=kontrollen.T_MODELL, f_hz=F_HZ, ks=[1, 2],
                gxy=dict(wert=np.r_[np.ones(3), ZELLEN[:, 0], ZELLEN[:, 1]],
                         kovarianz=np.zeros((9, 9)) if C_gxy is None else np.asarray(C_gxy, float)),
                kette=kette, fn_zeta=dict(wert=np.array([FN, ZETA]), gezogen=fz_gezogen,
                                          kovarianz_statistisch=np.zeros((2, 2)) if C_fz is None else np.asarray(C_fz),
                                          kette_richtungen=richt),
                module_nominal_m=MODULE_G60H, nicht_gezogen=[], unvollstaendig=[], naeherungen=[])


def _konfig(T0, phi=(0.0, 120.0, 240.0), delta=(0.0, 0.0, 0.0), n=6, rauschen=0.0, seed=0):
    """Läufe einer Konfiguration: Zellzeiger N_k = T(kω)·C_k mit Modulzeigern aⱼ·e^{−ik(φⱼ + δⱼ)}, Indexzeiger der
    Sollphasen (Δδ = 0), optional komplexes Rauschen je Lauf."""
    k = np.arange(1, 3)
    C = np.asarray(AMP)[:, None] * np.exp(-1j * np.outer(np.radians(np.add(phi, delta)), k))
    N = np.stack([T0[i] @ C[:, i] for i in range(2)], -1)
    rng = np.random.default_rng(seed)
    Xz = N[None] + rauschen * (rng.standard_normal((n, 3, 2)) + 1j * rng.standard_normal((n, 3, 2)))
    nz = np.full(n, 100)
    return dict(Xz=Xz, Z=nz[:, None, None] * np.exp(-1j * np.outer(np.radians(phi), k))[None], nz=nz)


def _e3(K, T0, tz, B, idxA=None, seed=3, triphasik=None, profil=ENTW):
    rng = np.random.default_rng(seed)
    if idxA is None:
        idxA = {kid: rng.integers(0, d['Xz'].shape[0], (B, d['Xz'].shape[0])) for kid, d in K.items()}
    E0 = [np.repeat(np.stack([T0[i][:, j] * AMP[j] for i in range(2)], -1)[None], 5, 0) for j in range(3)]
    idxB0 = [rng.integers(0, 5, (B, 5)) for _ in range(3)]
    return kontrollen.e3_auswerten(K, E0, idxA, idxB0, T0, ZELLEN, np.zeros(3), np.zeros(3), {}, triphasik, profil,
                                   np.random.default_rng(seed + 1), 0.0, T_zieh=tz)


def _u(out, kid=0):
    return {j: out['e3a'][kid]['e3a'][f'modul{j}']['u_grad'] for j in (2, 3)}


def test_e3_t_modell_gleich_unabhaengiger_formulierung():
    T0 = _t_nenn()
    for i, k in enumerate((1, 2)):
        ref = _t_referenz(np.ones(3), ZELLEN[:, 0], ZELLEN[:, 1], MODULE_G60H, KETTE_P, FN, ZETA, F_HZ, k)
        assert np.abs(T0[i] - ref).max() < 1e-12


def test_e3_nullkovarianzen_gleich_festem_T():
    """Vollständige Beschreibung mit ausdrücklich verschwindenden Kovarianzen: alle Ziehungen gleich dem Nennwert,
    Zahlen wie mit festem T; nur mit Beschreibung gibt es die dreiwertige Aussage."""
    T0 = _t_nenn()
    K = {'S118': _konfig(T0, delta=(0, 0.05, -0.03), rauschen=2e-3, seed=1), 'S120': _konfig(T0, rauschen=2e-3,
                                                                                            seed=2)}
    tz = kontrollen.t_ziehungen(_beschr(), np.random.default_rng(9), 400)
    assert tz['gueltig'].all() and np.array_equal(tz['T'], np.broadcast_to(T0, tz['T'].shape))
    a, b = _e3(K, T0, tz, 400), _e3(K, T0, None, 400)
    for ea, eb in zip(a['e3a'], b['e3a']):
        for m in ('modul2', 'modul3'):
            for f in ('delta_phi_Z_grad', 'u_grad', 'delta_phi_Z_k2_grad'):
                assert ea['e3a'][m][f] == pytest.approx(eb['e3a'][m][f], abs=1e-12)
    assert a['bewertung'] in ('auffällig', 'unauffällig', 'unbestimmt') and a['t_unsicherheit']['gezogen']
    assert b['bewertung'] is None and b['status'].startswith('nur numerisch') and 'fehlt' in b['status']


def _dphi_referenz(g, x, y, kette_p, N1, phiP):
    """Δφⱼ^Z (k = 1) der Module 2, 3 aus festen Zellzeigern N1 mit T aus der unabhängigen Formulierung."""
    C = np.linalg.solve(_t_referenz(g, x, y, MODULE_G60H, kette_p, FN, ZETA, F_HZ, 1), N1)
    return np.array([(np.degrees(np.angle(C[0]) - np.angle(C[j])) - phiP[j] + 180) % 360 - 180 for j in (1, 2)])


@pytest.mark.parametrize('fall', ['kette_tau2', 'lage_1_korreliert', 'verstaerkung_2'])
def test_e3_unsicherheit_aus_t_gleich_linearer_referenz(fall):
    """Bekannte Kovarianz eines Kettenphasen-, Zelllage- oder Verstärkungsfehlers: u(Δφⱼ^Z) aus den T-Ziehungen gleich
    der unabhängigen linearen Sensitivitätsrechnung √(sᵀ·C·s) (G60h, rauschfreie Läufe: kein Bootstrap-Anteil).
    Toleranz 5 %: Standardfehler einer Standardabweichung aus B = 4000 Ziehungen ≈ 1,1 %, dazu Linearisierung."""
    T0 = _t_nenn()
    K = {'S120': _konfig(T0)}
    th = dict(g=np.ones(3), x=ZELLEN[:, 0].copy(), y=ZELLEN[:, 1].copy(), kette=KETTE_P.copy())
    if fall == 'kette_tau2':
        Ck = [np.zeros((3, 3)) for _ in range(3)]
        Ck[1][1, 1] = (5e-6) ** 2
        be, wege, C = _beschr(C_kette=Ck), [('kette', (1, 1))], np.array([[(5e-6) ** 2]])
    elif fall == 'lage_1_korreliert':
        s, rho = 2e-4, 0.6
        Cg = np.zeros((9, 9))
        Cg[np.ix_([3, 6], [3, 6])] = [[s * s, rho * s * s], [rho * s * s, s * s]]
        be, wege, C = _beschr(C_gxy=Cg), [('x', 0), ('y', 0)], Cg[np.ix_([3, 6], [3, 6])]
    else:
        Cg = np.zeros((9, 9))
        Cg[1, 1] = (2e-3) ** 2
        be, wege, C = _beschr(C_gxy=Cg), [('g', 1)], np.array([[(2e-3) ** 2]])
    N1 = K['S120']['Xz'][0, :, 0]
    phiP = np.array([0.0, 120.0, -120.0])
    S = []
    for name, i in wege:
        h = 1e-7 if name == 'kette' else (1e-6 if name in ('x', 'y') else 1e-5)
        plus, minus = {k: v.copy() for k, v in th.items()}, {k: v.copy() for k, v in th.items()}
        plus[name][i] += h
        minus[name][i] -= h
        S.append((_dphi_referenz(plus['g'], plus['x'], plus['y'], plus['kette'], N1, phiP) -
                  _dphi_referenz(minus['g'], minus['x'], minus['y'], minus['kette'], N1, phiP)) / (2 * h))
    S = np.array(S)                                                      # (Parameter, Modul)
    u_ref = np.sqrt(np.einsum('pj,pq,qj->j', S, C, S))
    tz = kontrollen.t_ziehungen(be, np.random.default_rng(21), 4000)
    out = _e3(K, T0, tz, 4000)
    u = _u(out)
    assert u_ref.min() > 1e-4                                            # der Fall erzeugt eine merkliche Unsicherheit
    for j, ur in zip((2, 3), u_ref):
        assert u[j] == pytest.approx(ur, rel=0.05)
    assert max(_u(_e3(K, T0, None, 4000)).values()) < 1e-9               # ohne T-Anteil nur Rundungsrest


def test_e3_u_ohne_T_diagnose_gleich_festem_T_aus_denselben_replikaten():
    """Diagnose „u ohne T-Anteil“ (AP-13-Neuläufe): aus denselben Replikaten mit festem T und festen Zelllagen gleich
    u einer Auswertung ohne T-Ziehungen; mit unsicherem T ist u selbst größer. Der Kurzbefund trägt beide Spalten."""
    from pcmms_auswertung.harness import kampagnen
    T0 = _t_nenn()
    K = {'S118': _konfig(T0, delta=(0, 0.05, -0.03), rauschen=2e-3, seed=1), 'S120': _konfig(T0, rauschen=2e-3,
                                                                                            seed=2)}
    Ck = [np.zeros((3, 3)) for _ in range(3)]
    Ck[1][1, 1] = (5e-5) ** 2
    Cg = np.zeros((9, 9))
    Cg[3:, 3:] = np.eye(6) * (5e-4) ** 2
    tz = kontrollen.t_ziehungen(_beschr(C_gxy=Cg, C_kette=Ck), np.random.default_rng(7), 800)
    mit, fest = _e3(K, T0, tz, 800, triphasik='S120'), _e3(K, T0, None, 800, triphasik='S120')
    for em, ef in zip(mit['e3a'], fest['e3a']):
        for m in ('modul2', 'modul3'):
            assert em['e3a'][m]['u_ohne_T_grad'] == pytest.approx(ef['e3a'][m]['u_grad'], abs=1e-12)
            assert ef['e3a'][m]['u_ohne_T_grad'] == ef['e3a'][m]['u_grad']
            assert em['e3a'][m]['u_grad'] > 1.5 * em['e3a'][m]['u_ohne_T_grad']
    assert mit['e3b']['u_q_Z_ohne_T'] == pytest.approx(fest['e3b']['u_q_Z'], abs=1e-12)
    kb = kampagnen._e3_kurz(mit)
    assert kb['e3a'].shape == (4, 3) and kb['e3a'][0, 2] == mit['e3a'][0]['e3a']['modul2']['u_ohne_T_grad']
    assert kb['e3b'][1] == mit['e3b']['u_q_Z'] and kb['t']['gezogen'] and kb['bewertung'] == mit['bewertung']


def test_e3_gemeinsamer_faktor_hebt_sich_in_der_modulphase_auf():
    """Nur f_n, ζ unsicher: H(kω) ist ein gemeinsamer komplexer Faktor aller Zellen und Module und ändert u(Δφ) nicht;
    E3b (ohne T, exakte Superposition) bleibt ebenfalls unverändert."""
    T0 = _t_nenn()
    K = {'S118': _konfig(T0, rauschen=3e-3, seed=4), 'S120': _konfig(T0, rauschen=3e-3, seed=5)}
    tz = kontrollen.t_ziehungen(_beschr(C_fz=np.diag([0.5 ** 2, 0.002 ** 2]), fz_gezogen=True),
                                np.random.default_rng(2), 500)
    assert np.ptp(tz['parameter']['fn_zeta'][:, 0]) > 1.0                 # f_n streut tatsächlich
    a, b = _e3(K, T0, tz, 500, triphasik='S120'), _e3(K, T0, None, 500, triphasik='S120')
    for i in range(2):
        assert _u(a, i) == pytest.approx(_u(b, i), abs=1e-9)
    assert a['e3b']['u_q_Z'] == pytest.approx(b['e3b']['u_q_Z'], abs=1e-12)


def test_e3_zelllagen_in_e3b_gemeinsam_fuer_messung_und_vorhersage():
    """E3b zieht die Zelllagen je Replikat gemeinsam für Messung und Vorhersage: bei exakter Superposition hebt sich
    ihre Unsicherheit in R₋₁ − R̂₋₁ auf (q_Z und u(q_Z) null), obwohl die Lagen streuen."""
    T0 = _t_nenn()
    K = {'S120': _konfig(T0)}
    Cg = np.zeros((9, 9))
    Cg[3:, 3:] = np.eye(6) * (5e-4) ** 2
    tz = kontrollen.t_ziehungen(_beschr(C_gxy=Cg), np.random.default_rng(4), 600)
    assert np.std(tz['xy'][:, 0, 0]) > 1e-4
    out = _e3(K, T0, tz, 600, triphasik='S120')
    assert out['e3b']['q_Z'] == pytest.approx(0.0, abs=1e-12) and out['e3b']['u_q_Z'] == pytest.approx(0.0, abs=1e-12)


def test_e3_t_ziehungen_reproduzierbar_gemeinsam_und_korreliert():
    """Gleicher Strom → gleiche Ziehungen; je Replikat ein Parametersatz für k = 1 und k = 2 (gegen die unabhängige
    Formulierung) und für alle Konfigurationen; Korrelation von Zelllagen und von Kette ↔ f_n erhalten, ohne die Kette
    in f_n doppelt zu zählen."""
    s, rho = 3e-4, 0.6
    Cg = np.zeros((9, 9))
    Cg[np.ix_([3, 6], [3, 6])] = [[s * s, rho * s * s], [rho * s * s, s * s]]
    Ck = [np.zeros((3, 3)) for _ in range(3)]
    Ck[1][1, 1] = (4e-6) ** 2
    be = _beschr(C_gxy=Cg, C_kette=Ck, C_fz=np.diag([0.2 ** 2, 1e-6]), fz_gezogen=True, d_fz={(2, 0): [0.3, 0.0]})
    a = kontrollen.t_ziehungen(be, np.random.default_rng(5), 4000)
    b = kontrollen.t_ziehungen(be, np.random.default_rng(5), 4000)
    c = kontrollen.t_ziehungen(be, np.random.default_rng(6), 4000)
    assert np.array_equal(a['T'], b['T']) and np.array_equal(a['xy'], b['xy']) and not np.allclose(a['T'], c['T'])
    P = a['parameter']
    for bi in (0, 17, 3999):
        for i, k in enumerate((1, 2)):
            ref = _t_referenz(P['g'][bi], P['x'][bi], P['y'][bi], MODULE_G60H, P['kette'][bi], P['fn_zeta'][bi, 0],
                              P['fn_zeta'][bi, 1], F_HZ, k)
            assert np.abs(a['T'][bi, i] - ref).max() < 1e-12
    assert np.corrcoef(P['x'][:, 0], P['y'][:, 0])[0, 1] == pytest.approx(rho, abs=0.05)
    tau = P['kette'][:, 1, 1] - KETTE_P[1, 1]
    dfn = P['fn_zeta'][:, 0] - FN
    assert np.var(dfn) == pytest.approx(0.3 ** 2 + 0.2 ** 2, rel=0.08)  # Kettenanteil einmal, nicht zweimal
    assert np.cov(tau, dfn)[0, 1] / 4e-6 == pytest.approx(0.3, rel=0.08)
    # dieselben Ziehungen für alle Konfigurationen: zwei gleiche Konfigurationen mit denselben Bootstrap-Indizes
    T0 = _t_nenn()
    kf = _konfig(T0, delta=(0, 0.04, 0.0), rauschen=2e-3, seed=8)
    I = np.random.default_rng(1).integers(0, 6, (4000, 6))
    out = _e3({'S118': kf, 'S120': kf}, T0, a, 4000, idxA={'S118': I, 'S120': I})
    assert _u(out, 0) == _u(out, 1)
    assert out['e3a'][0]['e3a'] == out['e3a'][1]['e3a']


def test_e3_unzulaessige_ziehungen_und_singulaeres_T():
    """Unzulässige Ziehungen (g_c ≤ 0, f_n ≤ 0) werden gekennzeichnet und gezählt, nicht ersetzt; dann keine
    dreiwertige Aussage. Ein singuläres Nenn-T ergibt „nicht auswertbar“."""
    T0 = _t_nenn()
    K = {'S120': _konfig(T0, rauschen=1e-3, seed=3)}
    Cg = np.zeros((9, 9))
    Cg[1, 1] = 1.0
    tz = kontrollen.t_ziehungen(_beschr(C_gxy=Cg, C_fz=np.diag([200.0 ** 2, 0.0]), fz_gezogen=True),
                                np.random.default_rng(7), 1000)
    assert 0 < tz['anteil_ungueltig'] < 1 and tz['gruende']['g_c ≤ 0'] > 0 and tz['gruende']['f_n ≤ 0 oder ζ ≤ 0'] > 0
    assert np.isnan(tz['T'][~tz['gueltig']]).all() and np.isfinite(tz['T'][tz['gueltig']]).all()
    out = _e3(K, T0, tz, 1000)
    assert out['bewertung'] is None and 'unzulässig' in out['status'] and np.isfinite(_u(out)[2])
    assert out['t_unsicherheit']['anteil_ungueltig'] == tz['anteil_ungueltig']
    M = MODULE_G60H.copy()
    M[2] = M[1]                                                          # zwei Module am selben Ort: T singulär
    Ts = kontrollen.t_aus_parametern(np.ones(3), ZELLEN[:, 0], ZELLEN[:, 1], M, KETTE_P, FN, ZETA, F_HZ)
    out = _e3({'S120': _konfig(T0)}, Ts, None, 50)
    assert out['bewertung'] is None and out['status'].startswith('nicht auswertbar')


def test_e3_beschreibung_aus_kalibrierung_und_fehlende_teile():
    """t_beschreibung aus einer AP-11-Kalibrierung (V1-G60h: f_n, ζ gezogen; A4: nicht identifizierbar, H nominal mit
    Begründung) mit Kettenrichtungen passend zur Brückenanpassung; ohne Kettenrichtungen (ältere Kalibrierung) ist die
    Beschreibung unvollständig und E3 nur numerisch."""
    from pcmms_auswertung import anpassung
    from pcmms_auswertung.generator import kampagne as kp
    from pcmms_auswertung.harness import kette
    out = {}
    for sid in ('N01-V1G60h', 'N01-A4'):
        sz = kette.szenarien.KATALOG[sid]
        m = kette.szenarien.modell(sz, 'L1', plan=kp.Plan(n0=20, n_pilot=20, n_bloecke=24))
        _, _, kal = kette.kalibrierung_erzeugen(sz, m, 7)
        be = kontrollen.t_beschreibung(kal, m.system.f)
        assert be['format'] == kontrollen.T_FORMAT and be['modell'] == kontrollen.T_MODELL and not be['unvollstaendig']
        assert be['gxy']['kovarianz'].shape == (9, 9) and len(be['kette']) == 3
        assert any('Modullagen' in x for x in be['nicht_gezogen']) and any('Kippmoden' in x for x in be['nicht_gezogen'])
        n_r = sum(len(idx) for _, idx, _ in anpassung.kette_cholesky(kal['p0_1']['bruecke']))
        assert len(be['fn_zeta']['kette_richtungen']) == n_r
        out[sid] = (kal, be, m)
    assert out['N01-V1G60h'][1]['fn_zeta']['gezogen'] is True
    assert out['N01-A4'][1]['fn_zeta']['gezogen'] is False
    assert any('hebt sich' in x for x in out['N01-A4'][1]['nicht_gezogen'])
    kal, _, m = out['N01-V1G60h']
    alt = {**kal, 'p0_4': {**kal['p0_4'], 'einfreiheitsgrad': {k: v for k, v in kal['p0_4']['einfreiheitsgrad'].items()
                                                               if k != 'kette_richtungen'}}}
    be = kontrollen.t_beschreibung(alt, m.system.f)
    assert be['unvollstaendig']
    T0 = _t_nenn()
    tz = kontrollen.t_ziehungen({**be, 'module_nominal_m': MODULE_G60H}, np.random.default_rng(1), 50)
    res = _e3({'S120': _konfig(T0, rauschen=1e-3)}, T0, tz, 50)
    assert res['bewertung'] is None and 'unvollständig' in res['status']
