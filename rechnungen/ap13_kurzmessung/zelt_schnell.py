"""AP-13 Nachbesserung (nur Planungszahl): exakter, schneller Zeltfit nach Präreg A9.6.

A9.6: φ* in Schritten von 0,001° über [min W, max W]; für jedes φ* F*, s_L, s_R ungewichtet nach kleinsten
Quadraten; gewählt wird φ* mit der kleinsten Residuenquadratsumme (RSS), bei Gleichstand das kleinste.

Das Zeltmodell sind zwei Geraden, die sich bei φ* treffen. Zwischen zwei benachbarten Abszissen x_m < x_{m+1}
ist die Aufteilung links/rechts fest; mit den getrennten Geradenanpassungen (a_L, b_L), (a_R, b_R) gilt dort
  RSS(φ) = RSS_L + RSS_R + d(φ)²/Q(φ),  d = (a_L − a_R) + (b_L − b_R)·φ,  Q = (1, φ)(C_L + C_R)(1, φ)ᵀ,
C = (XᵀX)⁻¹ je Seite (Konvention: Punkt mit x = φ rechts). d²/Q hat genau eine Nullstelle φ₀ (Minimum) und ein
Maximum; auf einem Segment liegt das Rasterminimum deshalb an den Rasternachbarn von φ₀ oder an den Rasterpunkten
der Segmentenden. Mit höchstens einem Punkt auf einer Seite ist RSS auf dem Segment konstant (Geradenfit der
anderen Seite); bei Gleichstand gilt der kleinste Rasterpunkt. Kandidaten: je Segment Enden ±1, ⌊φ₀⌋, ⌈φ₀⌉ ±1.

Prüfung: Kandidatenverfahren gegen Vollraster mit derselben RSS-Funktion (Logik, muss identisch sein) und
gegen die unabhängige Vollraster-Fassung des Prüfers (m_zelt2.py, Numerik).
"""
import sys
import time
import numpy as np

H = 1e-3


def _stats(U, Y):
    z = np.zeros((U.shape[0], 1))
    c = lambda a: np.concatenate([z, np.cumsum(a, 1)], 1)
    return c(np.ones_like(U)), c(U), c(U * U), c(Y), c(U * Y), c(Y * Y)


def _linefit(n, su, suu, sy, suy, syy):
    det = n * suu - su * su
    with np.errstate(invalid='ignore', divide='ignore'):
        b = (n * suy - su * sy) / det
        a = (sy - b * su) / n
    rss = syy - a * sy - b * suy
    return a, b, rss, det


def rss_eval(U, Y, P):
    """RSS des Zeltfits für sortierte, zentrierte Abszissen U (R, n), Werte Y (R, n) und Spitzenlagen P (R, G)."""
    R, n = U.shape
    S = _stats(U, Y)
    tot = [s[:, -1:] for s in S]
    m = (U[:, None, :] < P[:, :, None]).sum(-1)                       # Zahl der Punkte links (x < φ)
    ix = np.arange(R)[:, None]
    Lf = [s[ix, m] for s in S]
    Rf = [t - l for t, l in zip(tot, Lf)]
    aL, bL, rL, dL = _linefit(*Lf)
    aR, bR, rR, dR = _linefit(*Rf)
    with np.errstate(invalid='ignore', divide='ignore'):
        # C = [[suu, −su], [−su, n]]/det je Seite
        q = (Lf[2] - 2 * P * Lf[1] + P * P * Lf[0]) / dL + (Rf[2] - 2 * P * Rf[1] + P * P * Rf[0]) / dR
        d = (aL - aR) + (bL - bR) * P
        inner = np.maximum(rL, 0) + np.maximum(rR, 0) + d * d / q
    # Randfälle: links ≤ 1 Punkt → Geradenfit rechts; rechts 1 Punkt → Geradenfit links;
    # rechts genau ein Punkt bei x = φ (oder links leer) → Gerade durch alle Punkte
    _, _, r_all, _ = _linefit(*tot)
    nl, nr = m, n - m
    out = np.where((nl >= 2) & (nr >= 2), inner, np.nan)
    out = np.where(nl <= 1, np.maximum(rR, 0), out)
    out = np.where((nr == 1) & (nl >= 2), np.maximum(rL, 0), out)
    at_end = (nr == 1) & (U[:, -1:] == P)
    out = np.where(at_end | (nl == 0), np.maximum(r_all, 0), out)
    return out


def _prep(X, Y):
    o = np.argsort(X, 1)
    X = np.take_along_axis(X, o, 1)
    Y = np.take_along_axis(Y, o, 1)
    xc = X[:, :1]                                                       # Rasterursprung = min W
    yc = Y.mean(1, keepdims=True)
    J = np.floor((X[:, -1] - X[:, 0]) / H + 1e-9).astype(int)
    return X - xc, Y - yc, xc[:, 0], J


def zelt_voll(X, Y, chunk=100):
    """Vollraster nach A9.6 (Referenz), gleiche RSS-Funktion."""
    U, V, xc, J = _prep(X, Y)
    R = U.shape[0]
    out = np.empty(R)
    chunk = max(1, int(5e5 // (J.max() + 1)))
    for c0 in range(0, R, chunk):
        sl = slice(c0, c0 + chunk)
        G = J[sl].max() + 1
        jj = np.arange(G)[None, :]
        P = jj * H
        rss = rss_eval(U[sl], V[sl], np.broadcast_to(P, (U[sl].shape[0], G)).copy())
        rss = np.where(jj <= J[sl][:, None], rss, np.inf)
        out[sl] = xc[sl] + H * np.argmin(rss, 1)
    return out


def zelt_kand(X, Y):
    """Kandidatenverfahren: je Segment Enden ±1 und Rasternachbarn der Nullstelle φ₀ ±1."""
    U, V, xc, J = _prep(X, Y)
    R, n = U.shape
    S = _stats(U, V)
    tot = [s[:, -1:] for s in S]
    cand = []
    for mseg in range(1, n):                                            # Segment zwischen U[m−1] und U[m]
        lo = np.ceil(U[:, mseg - 1] / H - 1e-9)
        hi = np.floor(U[:, mseg] / H + 1e-9)
        cand += [lo - 1, lo, lo + 1, hi - 1, hi, hi + 1]
        if mseg >= 2 and n - mseg >= 2:
            Lf = [s[:, mseg] for s in S]
            Rf = [t[:, 0] - l for t, l in zip(tot, Lf)]
            aL, bL, _, _ = _linefit(*Lf)
            aR, bR, _, _ = _linefit(*Rf)
            with np.errstate(invalid='ignore', divide='ignore'):
                p0 = -(aL - aR) / (bL - bR)
            p0 = np.where(np.isfinite(p0) & (p0 >= U[:, mseg - 1]) & (p0 <= U[:, mseg]), p0, U[:, mseg - 1])
            f0 = np.floor(p0 / H)
            cand += [f0 - 1, f0, f0 + 1, f0 + 2]
    C = np.clip(np.stack(cand, 1), 0, J[:, None]).astype(int)
    C = np.sort(C, 1)                                                   # kleinster Index zuerst (Gleichstand)
    rss = rss_eval(U, V, C * H)
    return xc + H * C[np.arange(R), np.argmin(rss, 1)]


def testsatz(rng, R, w, art):
    x0 = np.arange(120 - w, 120 + w + 0.1, 2.0)
    X = x0[None, :] + rng.normal(0, 0.05, (R, x0.size))
    if art == 'asym':
        pk = 120.3 + rng.normal(0, 0.3, (R, 1))
        Y = np.where(X < pk, -0.0435 * (pk - X), -0.0571 * (X - pk)) + rng.normal(0, 2e-3, X.shape)
    elif art == 'sym':
        pk = 120.0
        Y = -0.0435 * np.abs(X - pk) + rng.normal(0, 2e-3, X.shape)
    elif art == 'sym_fein':
        Y = -0.0435 * np.abs(X - 120.0) + rng.normal(0, 1e-5, X.shape)
    elif art == 'rauschen':
        Y = rng.normal(0, 1e-3, X.shape)
    elif art == 'gerade':
        Y = 0.01 * X + rng.normal(0, 1e-4, X.shape)
    elif art == 'knick_flach':                                          # Zelt mit geknickten Flanken (Formfehler)
        Y = -0.0435 * np.abs(X - 120.0) - 0.004 * np.maximum(np.abs(X - 120.0) - 6, 0) ** 1.5 \
            + rng.normal(0, 1e-3, X.shape)
    return X, Y


if __name__ == '__main__':
    rng = np.random.default_rng(613)
    sys.path.insert(0, '.')
    src = open('m_zelt2.py', encoding='utf-8').read().split('for w in (6, 8, 20):')[0]
    ns = {}
    exec(src, ns)
    zelt_pruefer = ns['zelt_seg']
    print('Gleichheit Kandidatenverfahren gegen Vollraster (gleiche RSS-Funktion) und gegen Prüferfassung')
    tot_n = tot_mis = 0
    for w in (6, 8, 20):
        for art in ('asym', 'sym', 'sym_fein', 'rauschen', 'gerade', 'knick_flach'):
            R = 300 if w < 20 else 100
            X, Y = testsatz(rng, R, w, art)
            a = zelt_kand(X, Y)
            b = zelt_voll(X, Y)
            c = zelt_pruefer(X, Y)
            mis = np.sum(np.abs(a - b) > 1e-9)
            mis_p = np.sum(np.abs(a - c) > 1e-6)
            tot_n += R
            tot_mis += mis
            print(f'  w = {w:2d}°, {art:12s} R = {R}: Abweichungen gegen Vollraster {mis}, gegen Prüferfassung '
                  f'{mis_p} (max |Δφ*| = {np.abs(a - c).max():.4f}°)', flush=True)
    print(f'  zusammen {tot_n} Replikate, {tot_mis} Abweichungen gegen Vollraster')
    print()
    print('Laufzeit je Satz von 1000 Fits (ein Fit je Replikat)')
    for w in (6, 8, 20):
        X, Y = testsatz(rng, 1000, w, 'asym')
        zelt_kand(X, Y)
        t0 = time.perf_counter()
        for _ in range(5):
            zelt_kand(X, Y)
        dk = (time.perf_counter() - t0) / 5
        t0 = time.perf_counter()
        zelt_voll(X, Y)
        dv = time.perf_counter() - t0
        print(f'  w = {w:2d}° ({X.shape[1]} Punkte): Kandidatenverfahren {1e3 * dk:.1f} ms, Vollraster {dv:.2f} s',
              flush=True)
