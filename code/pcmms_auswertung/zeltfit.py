"""AP-12: Zeltfit nach Präreg §8.6 und A9.6 mit exaktem Kandidatenverfahren (Plan AP-13, Abschnitt 4.1).

Modell: stetiges Zelt F(φ) = F* − s_L·(φ* − φ) für φ ≤ φ*, F* − s_R·(φ − φ*) sonst, ungewichtet; φ* auf dem Raster
min W + m·0,001° über [min W, max W] (Regel h2.rasterursprung: Ursprung ist die kleinste Abszisse); gewählt wird
die kleinste Residuenquadratsumme, bei Gleichstand das kleinste φ* (Regel h2.gleichstand) mit der Toleranz
RSS ≤ RSS_min·(1 + 10⁻⁹) + 10⁻¹²·SST + 10⁻²⁸·n·max F² (Regel h2.gleichstand_toleranz, technisch; A9.6 nennt keine
Toleranz).

Kandidatenverfahren: Zwischen zwei benachbarten Abszissen p_s ≤ φ* < p_{s+1} ist die Aufteilung links/rechts fest.
Mit den getrennten Geradenanpassungen beider Seiten (zentriert, RSS_L, RSS_R) gilt dort
RSS(φ*) = RSS_L + RSS_R + d(φ*)²/Q(φ*), d linear (Differenz der beiden Geraden bei φ*), Q > 0 quadratisch
(1/n_L + (φ* − φ̄_L)²/S_L + 1/n_R + (φ* − φ̄_R)²/S_R). d²/Q hat genau ein Minimum (d = 0) und ein Maximum; das
Rasterminimum des Segments liegt an den Rasternachbarn der Nullstelle oder an den Rasterpunkten der Segmentenden.
Hat eine Seite nur einen Punkt, ist RSS im Segment konstant (kleinster Rasterpunkt), ausgenommen φ* = min W (der
einzelne linke Punkt liegt dann in der Spitze); dort und bei φ* = max W gilt eine Gerade durch alle Punkte. Vektorisiert über Replikate (Zeilen) gleicher Punktzahl.
"""
import numpy as np

SCHRITT = 0.001
REL_TOL = 1e-9
SST_TOL = 1e-12


def zeltfit(phi, F, schritt=SCHRITT, rel_tol=REL_TOL):
    """φ* je Zeile (phi, F: (R, n) oder (n,)). Rückgabe dict phi_stern (R,), m (R,), rss (R,), sst (R,)."""
    phi = np.atleast_2d(np.asarray(phi, float))
    F = np.atleast_2d(np.asarray(F, float))
    R, n = phi.shape
    o = np.argsort(phi, axis=1, kind='stable')
    p = np.take_along_axis(phi, o, 1)
    y = np.take_along_axis(F, o, 1)
    p0 = p[:, :1]
    x = p - p0                                                          # Abstand zur kleinsten Abszisse (≥ 0)
    ym_all = y.mean(1, keepdims=True)
    yc = y - ym_all
    sst = (yc ** 2).sum(1)
    M = np.floor((x[:, -1]) / schritt + 1e-9).astype(np.int64)
    # Präfixsummen (zentriert um die Zeilenmittel für die Stabilität)
    xs = x - x.mean(1, keepdims=True)
    c1 = np.cumsum(np.ones_like(xs), 1)
    cx, cy = np.cumsum(xs, 1), np.cumsum(yc, 1)
    cxx, cxy, cyy = np.cumsum(xs * xs, 1), np.cumsum(xs * yc, 1), np.cumsum(yc * yc, 1)
    tx, ty, txx, txy, tyy = cx[:, -1:], cy[:, -1:], cxx[:, -1:], cxy[:, -1:], cyy[:, -1:]
    xoff = x.mean(1)                                                    # xs = x − xoff
    kand_m, kand_r = [], []

    def stats_seite(nn, sx, sy, sxx, sxy, syy):
        with np.errstate(invalid='ignore', divide='ignore'):
            xm, ymn = sx / nn, sy / nn
            Sxx = sxx - nn * xm ** 2
            Sxy = sxy - nn * xm * ymn
            Syy = syy - nn * ymn ** 2
            b = np.where(Sxx > 0, Sxy / np.where(Sxx > 0, Sxx, 1), 0.0)
            rss = np.maximum(Syy - b * Sxy, 0.0)
        return xm, ymn, Sxx, b, rss

    Lall = stats_seite(n, tx[:, 0], ty[:, 0], txx[:, 0], txy[:, 0], tyy[:, 0])

    def rasterbereich(lo, hi_excl):
        """Rasterindizes m mit lo ≤ m·schritt < hi_excl (lo, hi_excl als Abstand zu p0)."""
        a = np.ceil(lo / schritt - 1e-9).astype(np.int64)
        b = np.ceil(hi_excl / schritt - 1e-9).astype(np.int64) - 1
        return a, np.minimum(b, M)

    for s in range(n - 1):                                              # links: Punkte 0 … s
        nL, nR = s + 1, n - s - 1
        L = stats_seite(nL, cx[:, s], cy[:, s], cxx[:, s], cxy[:, s], cyy[:, s])
        Rr = stats_seite(nR, tx[:, 0] - cx[:, s], ty[:, 0] - cy[:, s], txx[:, 0] - cxx[:, s], txy[:, 0] - cxy[:, s],
                         tyy[:, 0] - cyy[:, s])
        a_m, b_m = rasterbereich(x[:, s], x[:, s + 1])
        leer = b_m < a_m
        if nL == 1 or nR == 1:                                         # RSS im Segment konstant
            rss_c = np.zeros(R) if (nL == 1 and nR == 1) else (Rr[4] if nL == 1 else L[4])
            if nL == 1:
                # φ* = p₀ selbst: der linke Punkt liegt in der Spitze, das Zelt wird zur Geraden durch alle Punkte;
                # konstant ist RSS erst für φ* > p₀
                kand_m.append(np.where(leer, -1, 0))
                kand_r.append(np.where(leer, np.inf, Lall[4]))
                a1 = np.maximum(a_m, 1)
                ok = ~leer & (a1 <= b_m)
                kand_m.append(np.where(ok, a1, -1))
                kand_r.append(np.where(ok, rss_c, np.inf))
            else:
                kand_m.append(np.where(leer, -1, a_m))
                kand_r.append(np.where(leer, np.inf, rss_c))
            continue
        aL = L[1] - L[3] * L[0]
        aR = Rr[1] - Rr[3] * Rr[0]
        dA, dB = aL - aR, L[3] - Rr[3]

        def rss_bei(m):
            ph = m * schritt - xoff                                    # φ* in zentrierten Koordinaten
            d = dA + dB * ph
            with np.errstate(invalid='ignore', divide='ignore'):
                Q = 1 / nL + (ph - L[0]) ** 2 / L[2] + 1 / nR + (ph - Rr[0]) ** 2 / Rr[2]
                return L[4] + Rr[4] + d ** 2 / Q
        with np.errstate(invalid='ignore', divide='ignore'):
            wurzel = np.where(dB != 0, -dA / np.where(dB != 0, dB, 1) + xoff, np.nan)    # in x-Koordinaten
        mw = np.floor(wurzel / schritt + 1e-12)
        for m in (a_m, b_m, mw, mw + 1):
            m = np.asarray(m)
            ok = ~leer & np.isfinite(m) & (m >= a_m) & (m <= b_m)
            mi = np.where(ok, m, 0).astype(np.int64)
            kand_m.append(np.where(ok, mi, -1))
            kand_r.append(np.where(ok, rss_bei(mi), np.inf))
    # φ* = max W (rechte Seite leer), nur wenn auf dem Raster
    auf = np.abs(M * schritt - x[:, -1]) <= 1e-9 * np.maximum(1.0, x[:, -1])
    kand_m.append(np.where(auf, M, -1))
    kand_r.append(np.where(auf, Lall[4], np.inf))
    Km, Kr = np.stack(kand_m, 1), np.stack(kand_r, 1)
    rmin = Kr.min(1)
    tol = rmin + rel_tol * rmin + SST_TOL * sst + 1e-28 * n * (y ** 2).max(1)     # Rundungsboden bei SST ≈ 0
    gleich = (Kr <= tol[:, None]) & (Km >= 0)
    m_best = np.where(gleich, Km, np.iinfo(np.int64).max).min(1)
    best_rss = np.where(np.isfinite(rmin), np.take_along_axis(Kr, np.argmax((Km == m_best[:, None]) & gleich, 1)[:,
                                                                        None], 1)[:, 0], np.nan)
    return dict(phi_stern=p0[:, 0] + m_best * schritt, m=m_best, rss=best_rss, sst=sst, rss_min=rmin)


def rss_exakt(phi, F, phi_stern):
    """RSS des Zelts bei festem φ* durch direkte Ausgleichsrechnung (zentriert bei φ*), für Prüfungen."""
    phi, F = np.asarray(phi, float), np.asarray(F, float)
    d = phi - phi_stern
    links = d <= 0
    cols = [np.ones_like(d)]
    if links.any():
        cols.append(np.where(links, d, 0.0))
    if (~links).any():
        cols.append(np.where(~links, d, 0.0))
    X = np.stack(cols, 1)
    beta = np.linalg.lstsq(X, F, rcond=None)[0]
    r = F - X @ beta
    return float(r @ r)
