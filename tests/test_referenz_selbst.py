"""Selbsttests der Referenzimplementierungen: analytische Fälle, ohne Produktionsmodule."""
import numpy as np
import pytest

from pcmms_auswertung.referenz import h1_referenz, zeltfit_referenz

THETA = 2 * np.pi * np.arange(h1_referenz.N_THETA) / h1_referenz.N_THETA


def _direkt(N):
    """x(θ_n) = Σ_k Re(N_k·e^{ikθ_n}) als direkte Summe."""
    N = np.atleast_2d(N)
    k = np.arange(1, N.shape[1] + 1)
    return np.real(N @ np.exp(1j * np.outer(k, THETA)))


# ---------------------------------------------------------------- Kurve, F_min

@pytest.mark.parametrize('kmax', [3, 7, 20])
def test_kurve_irfft_gleich_direkter_summe(kmax):
    rng = np.random.default_rng(kmax)
    N = rng.normal(size=(40, kmax)) + 1j * rng.normal(size=(40, kmax))
    x = h1_referenz.kurve(N)
    assert x.shape == (40, h1_referenz.N_THETA)
    assert np.max(np.abs(x - _direkt(N))) <= 1e-12
    assert np.max(np.abs(h1_referenz.f_min_rel(N, block=7) - _direkt(N).min(axis=1))) <= 1e-12


def test_groessen_reihenfolge():
    N = np.array([1 + 2j, 3 - 4j, -5 + 6j, 7 + 8j])
    q = h1_referenz.groessen(N)
    assert np.allclose(q[1:], [1, 2, 3, -4, -5, 6], rtol=0, atol=0)
    assert q[0] == pytest.approx(_direkt(N).min(), abs=1e-12)


# ---------------------------------------------------------------- H1: Testdaten

PUNKTE = [f'S{p:03d}' for p in range(100, 141, 2)]


def _schnitt(rng, rauschen=0.0, B=200, kmax=4, K=6, Delta=None):
    """Schnitt mit exakter Superposition: feste Phasen (0, φ₂, 240°) je Punkt, Basis ohne Streuung
    (rauschen = 0) oder mit kleinem komplexem Rauschen; Harmonische über k_max sind Störwerte."""
    grund = np.array([1.0, 0.45 * np.exp(0.7j), 0.30 * np.exp(-1.2j), 0.12 * np.exp(2.1j), 0.05, 0.02])
    basis = np.stack([grund[:K] * a * np.exp(1j * p * np.arange(1, K + 1))
                      for a, p in ((1.0, 0.0), (0.95, 0.03), (1.05, -0.02))])
    basis[:, kmax:] = 50.0

    def streuung(n):
        return rauschen * (rng.normal(size=(n, K)) + 1j * rng.normal(size=(n, K)))

    n0, n1 = (20, 21, 22), (12, 13, 14)
    einzel0 = [np.repeat(basis[j][None], n0[j], 0) + streuung(n0[j]) for j in range(3)]
    einzel1 = [np.repeat(basis[j][None], n1[j], 0) + streuung(n1[j]) for j in range(3)]
    k = np.arange(1, K + 1)
    laeufe, indizes = {}, {}
    for i, pid in enumerate(PUNKTE):
        w = np.exp(-1j * np.outer(np.deg2rad([0.0, 100.0 + 2 * i, 240.0]), k))   # e^{−ikφ_j}
        n = 12 + i % 4
        nz = rng.integers(280, 321, size=n)
        laeufe[pid] = dict(Nk=np.repeat((basis * w).sum(axis=0)[None], n, 0) + streuung(n),
                           zeiger=nz[:, None, None] * w[None], nz=nz)
        indizes[f'A/{pid}'] = rng.integers(0, n, size=(B, n))
    for j in range(3):
        indizes[f'B0/modul{j + 1}'] = rng.integers(0, n0[j], size=(B, n0[j]))
        indizes[f'B1/modul{j + 1}'] = rng.integers(0, n1[j], size=(B, n1[j]))
    if Delta is None:
        # Δ_q = 0,25·D_q aus ŷ⁰ (Fassung B): Spannweite von F_min, Durchmesser der Zeigermenge
        Nq = np.array([x[:, :kmax].mean(axis=0) for x in einzel0])
        yh = np.array([(Nq * L['zeiger'][:, :, :kmax].sum(0) / L['nz'].sum()).sum(0)
                       for L in laeufe.values()])
        F = h1_referenz.f_min_rel(yh)
        D = [F.max() - F.min()]
        for kk in range(3):
            d = np.abs(yh[:, kk][:, None] - yh[:, kk][None]).max()
            D += [d, d]
        Delta = 0.25 * np.array(D)
    null = np.zeros(21)
    return dict(kmax=kmax, punkte=list(PUNKTE), laeufe=laeufe, einzel0=einzel0, einzel1=einzel1,
                bias0=null.copy(), bias1=null.copy(), u_bias0=null.copy(), u_bias1=null.copy(),
                Delta=np.asarray(Delta, float), Delta_rel=np.asarray(Delta, float).copy(),
                c=4.0, indizes=indizes)


# ---------------------------------------------------------------- H1: Fälle

def test_h1_rauschfrei_bestaetigt():
    e = _schnitt(np.random.default_rng(7))
    a = h1_referenz.h1_referenz(e)
    assert a['ausgang'] == 'bestaetigt'
    assert a['abweichung_nachgewiesen'] is False and a['drift'] is False
    assert a['n_punkte'] == 21 and a['max_abs_z0'] == 0.0
    assert np.max(np.abs(a['r0'])) <= 1e-12 and np.max(np.abs(a['r1'])) <= 1e-12
    # Entartungsregel: Bootstrapstreuung nur Rundung → u = 0, ν = ∞, z = 0
    S = np.maximum.reduce([np.abs(a['yquer']), np.abs(a['yhat0']), np.broadcast_to(e['Delta'], (21, 7))])
    assert np.all(np.sqrt(a['varA0'] + a['varB0']) <= 1e-14 * S)
    for p in '01':
        assert np.all(a['u' + p] == 0) and np.all(np.isinf(a['nu' + p])) and np.all(a['z' + p] == 0)
        assert a['tost' + p].all()
    assert not a['relevant'].any()
    assert np.allclose(a['yhat0'], a['yquer'], rtol=0, atol=1e-12)


def test_h1_ohne_c_nur_aequivalenz():
    e = _schnitt(np.random.default_rng(8))
    e['c'] = None
    a = h1_referenz.h1_referenz(e)
    assert a['ausgang'] == 'bestaetigt'
    assert a['abweichung_nachgewiesen'] is None and a['drift'] is None
    assert not a['relevant'].any()


def test_h1_fehlender_punkt_nicht_entscheidbar():
    e = _schnitt(np.random.default_rng(9))
    del e['laeufe']['S120']
    a = h1_referenz.h1_referenz(e)
    i = PUNKTE.index('S120')
    assert a['ausgang'] == 'nicht entscheidbar' and a['n_punkte'] == 20
    assert np.all(np.isnan(a['r0'][i])) and np.all(np.isnan(a['u1'][i]))
    assert not a['tost0'][i].any() and not a['relevant'][i].any()
    assert np.delete(a['tost0'], i, axis=0).all() and np.delete(a['tost1'], i, axis=0).all()


def test_h1_biaskorrektur():
    e = _schnitt(np.random.default_rng(10))
    e['bias0'] = 0.004 * np.linspace(-1, 1, 21)
    e['bias1'] = -0.002 * np.linspace(-1, 1, 21)
    e['u_bias0'] = np.full(21, 0.003)
    e['u_bias1'] = np.full(21, 0.005)
    a = h1_referenz.h1_referenz(e)
    assert np.allclose(a['r0'][:, 0], -e['bias0'], rtol=0, atol=1e-12)
    assert np.allclose(a['r1'][:, 0], -e['bias1'], rtol=0, atol=1e-12)
    assert np.allclose(a['u0'][:, 0], 0.003, rtol=1e-9) and np.allclose(a['u1'][:, 0], 0.005, rtol=1e-9)
    assert np.allclose(a['z0'][:, 0], -e['bias0'] / 0.003, rtol=1e-9, atol=1e-12)
    assert np.all(a['nu0'][:, 0] > 1e20)                  # Biasterm zählt mit ν = ∞
    assert np.all(a['u0'][:, 1:] == 0)                    # Bias nur bei F_min − ⟨N⟩
    assert a['ausgang'] == 'bestaetigt' and a['abweichung_nachgewiesen'] is False


def test_h1_injizierte_abweichung_falsifiziert():
    e = _schnitt(np.random.default_rng(11), rauschen=1e-6)
    i = PUNKTE.index('S120')
    e['laeufe']['S120']['Nk'] = 1.5 * e['laeufe']['S120']['Nk']
    a = h1_referenz.h1_referenz(e)
    assert a['ausgang'] == 'falsifiziert'
    assert a['relevant'][i].any() and not np.delete(a['relevant'], i, axis=0).any()
    assert a['abweichung_nachgewiesen'] is True
    assert not a['tost0'][i].all()
    # F_min skaliert mit dem Faktor: r ≈ 0,5·F̂_min
    assert a['r0'][i, 0] == pytest.approx(0.5 * a['yhat0'][i, 0], rel=1e-4)


def test_h1_bootstrap_wie_definition():
    """Varianzen, ν und u gegen eine direkte Schleife über die Replikate (Ziehen statt Zählmatrix,
    F_min als direkte Summe)."""
    rng = np.random.default_rng(12)
    e = _schnitt(rng, rauschen=0.01, B=40)
    a = h1_referenz.h1_referenz(e)
    km = e['kmax']

    def q(N):
        return np.concatenate([[_direkt(N).min()], np.column_stack([N[:3].real, N[:3].imag]).ravel()])

    for basis, p in (('einzel0', '0'), ('einzel1', '1')):
        X = [x[:, :km] for x in e[basis]]
        Nq = np.array([x.mean(axis=0) for x in X])
        idxB = [e['indizes'][f'B{p}/modul{j + 1}'] for j in range(3)]
        for pid in ('S100', 'S124'):
            i = PUNKTE.index(pid)
            L = e['laeufe'][pid]
            Nk, Z, nz = L['Nk'][:, :km], L['zeiger'][:, :, :km], L['nz']
            rho = Z.sum(0) / nz.sum()
            qy = q(Nk.mean(0))
            rA = [q(Nk[ix].mean(0)) - q((Nq * Z[ix].sum(0) / nz[ix].sum()).sum(0))
                  for ix in e['indizes'][f'A/{pid}']]
            rB = [qy - q((np.array([X[j][idxB[j][b]].mean(0) for j in range(3)]) * rho).sum(0))
                  for b in range(40)]
            vA, vB = np.var(rA, axis=0, ddof=1), np.var(rB, axis=0, ddof=1)
            assert np.allclose(a['varA' + p][i], vA, rtol=1e-8, atol=0)
            assert np.allclose(a['varB' + p][i], vB, rtol=1e-8, atol=0)
            u = np.sqrt(vA + vB)
            nB = min(x.shape[0] for x in X)
            nu = u ** 4 / (vA ** 2 / (Nk.shape[0] - 1) + vB ** 2 / (nB - 1))
            assert np.allclose(a['u' + p][i], u, rtol=1e-8)
            assert np.allclose(a['nu' + p][i], nu, rtol=1e-8)
            assert np.allclose(a['r' + p][i], qy - q((Nq * rho).sum(0)), rtol=0, atol=1e-12)


# ---------------------------------------------------------------- Zeltfit

def _zelt(phi, ps, Fs, sL, sR):
    phi = np.asarray(phi, float)
    return np.where(phi <= ps, Fs - sL * (ps - phi), Fs - sR * (phi - ps))


@pytest.mark.parametrize('phi, m', [
    (np.arange(114.0, 127.0, 2.0), 6000),
    (np.array([114.137, 116.02, 117.95, 120.31, 121.88, 124.07, 125.96]), 5863),
])
def test_zelt_exakt_asymmetrisch(phi, m):
    phi = np.random.default_rng(1).permutation(phi)       # unsortiert
    r = zeltfit_referenz.zeltfit_vollraster(phi, _zelt(phi, 120.0, -4.2, 0.8, 2.3))
    assert r['m'] == m and r['gleichstand'] == 1
    assert r['phi_stern'] == pytest.approx(120.0, abs=1e-12)
    assert (r['F_stern'], r['s_L'], r['s_R']) == pytest.approx((-4.2, 0.8, 2.3), abs=1e-9)
    assert r['rss'] <= 1e-20


def test_zelt_gerade_gleichstand_ueberall():
    phi = np.arange(114.0, 127.0, 2.0)
    F = 3.0 + 0.7 * (phi - 110.0)
    g, rss, _ = zeltfit_referenz.rss_vollraster(phi, F)
    sst = np.sum((F - F.mean()) ** 2)
    assert np.max(rss) <= 1e-20 * sst
    r = zeltfit_referenz.zeltfit_vollraster(phi, F)
    assert r['m'] == 0 and r['phi_stern'] == 114.0
    assert r['gleichstand'] == r['n_raster'] == 12001


@pytest.mark.parametrize('phi, m', [(np.arange(115.0, 126.0, 2.0), 5000),
                                    (np.arange(114.0, 127.0, 2.0), 6000)])
def test_zelt_symmetrisch(phi, m):
    r = zeltfit_referenz.zeltfit_vollraster(phi, _zelt(phi, 120.0, 1.0, 1.3, 1.3))
    assert r['m'] == m and r['phi_stern'] == pytest.approx(120.0, abs=1e-12)
    assert r['gleichstand'] == 1
    assert (r['s_L'], r['s_R']) == pytest.approx((1.3, 1.3), abs=1e-9)


def test_zelt_einzelpunkt_rechts():
    """Ein Punkt rechts: auf [124°, 126°) wird er exakt getroffen, RSS konstant (≈ 0) → 124,000°."""
    phi = np.arange(114.0, 127.0, 2.0)
    F = 10.0 + 0.5 * (phi - 114.0)
    F[-1] = 2.0
    g, rss, _ = zeltfit_referenz.rss_vollraster(phi, F)
    r = zeltfit_referenz.zeltfit_vollraster(phi, F)
    assert r['m'] == 10000 and r['phi_stern'] == 124.0 and r['gleichstand'] == 2000
    assert rss[-1] > 1.0                                   # φ* = 126°: rechte Seite leer
    assert r['s_L'] == pytest.approx(0.5, abs=1e-9)


def test_zelt_einzelpunkt_links():
    """Ein Punkt links: Plateau (114°, 116°]; bei 114° liegt er auf der Spitze → kleinstes 114,001°."""
    phi = np.arange(114.0, 127.0, 2.0)
    F = 10.0 - 0.5 * (phi - 114.0)
    F[0] = 2.0
    g, rss, _ = zeltfit_referenz.rss_vollraster(phi, F)
    r = zeltfit_referenz.zeltfit_vollraster(phi, F)
    assert r['m'] == 1 and r['phi_stern'] == pytest.approx(114.001, abs=1e-12)
    assert r['gleichstand'] == 2000 and rss[0] > 1.0
    assert r['s_R'] == pytest.approx(0.5, abs=1e-9)


def test_zelt_rss_wie_lstsq():
    """RSS je Rasterpunkt gegen numpy.linalg.lstsq mit gestrichenen leeren Seiten."""
    rng = np.random.default_rng(3)
    phi = np.sort(rng.uniform(114.0, 126.0, 7))
    F = _zelt(phi, 120.3, 0.0, 1.0, 1.4) + rng.normal(0, 0.05, 7)
    g, rss, par = zeltfit_referenz.rss_vollraster(phi, F)
    for m in np.r_[0, 1, rng.integers(0, g.size, 25), g.size - 1]:
        d = phi - g[m]
        sp = [np.ones_like(d)] + [np.minimum(d, 0)] * bool((d < 0).any()) + [-np.maximum(d, 0)] * bool((d > 0).any())
        x, *_ = np.linalg.lstsq(np.column_stack(sp), F, rcond=None)
        res = F - np.column_stack(sp) @ x
        assert rss[m] == pytest.approx(res @ res, rel=1e-9, abs=1e-15)
    r = zeltfit_referenz.zeltfit_vollraster(phi, F)
    assert r['rss'] == rss.min() and r['gleichstand'] == 1


def test_zelt_wenige_punkte():
    r = zeltfit_referenz.zeltfit_vollraster([120.0], [3.0])
    assert (r['n_raster'], r['m'], r['phi_stern'], r['F_stern'], r['rss']) == (1, 0, 120.0, 3.0, 0.0)
    r = zeltfit_referenz.zeltfit_vollraster([121.0, 120.0], [1.0, 3.0])
    assert r['n_raster'] == 1001 and r['gleichstand'] == 1001 and r['phi_stern'] == 120.0
    assert (r['F_stern'], r['s_R']) == pytest.approx((3.0, 2.0), abs=1e-12)
