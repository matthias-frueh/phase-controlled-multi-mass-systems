"""Prüfer AP-13 (unabhängig): Zeltfit nach A9.6 (Raster 0,001°, Abszissen je Replikat neu), segmentweise geschlossene
Form (O(1) je Rasterpunkt über kumulierte Summen). Kontrolle gegen die naive Fassung m_zelt.py an 20 Replikaten."""
import time
import numpy as np
rng = np.random.default_rng(5)


def zelt_seg(X, Y, step=1e-3, chunk=200):
    R, n = X.shape
    o = np.argsort(X, 1); X = np.take_along_axis(X, o, 1); Y = np.take_along_axis(Y, o, 1)
    z = np.zeros((R, 1))
    cx = np.c_[z, np.cumsum(X, 1)]; cy = np.c_[z, np.cumsum(Y, 1)]
    cxx = np.c_[z, np.cumsum(X * X, 1)]; cxy = np.c_[z, np.cumsum(X * Y, 1)]
    Sy2 = (Y * Y).sum(1)
    out = np.empty(R)
    for c0 in range(0, R, chunk):
        sl = slice(c0, c0 + chunk)
        x = X[sl]; lo, hi = x[:, 0], x[:, -1]
        G = int(np.ceil((hi - lo).max() / step)) + 1
        ph = lo[:, None] + step * np.arange(G)[None, :]
        valid = ph <= hi[:, None] + 1e-12
        m = (x[:, None, :] < ph[:, :, None]).sum(-1)                 # Zahl der Punkte links (x < phi)
        ix = np.arange(len(x))[:, None]
        nl = m; nr = n - m
        Lx, Ly, Lxx, Lxy = cx[sl][ix, m], cy[sl][ix, m], cxx[sl][ix, m], cxy[sl][ix, m]
        Rx, Ry, Rxx, Rxy = cx[sl][:, -1:] - Lx, cy[sl][:, -1:] - Ly, cxx[sl][:, -1:] - Lxx, cxy[sl][:, -1:] - Lxy
        a11 = n; a12 = -(nl * ph - Lx); a13 = -(Rx - nr * ph)
        a22 = nl * ph ** 2 - 2 * ph * Lx + Lxx; a33 = Rxx - 2 * ph * Rx + nr * ph ** 2; a23 = 0.0
        ty = cy[sl][:, -1:]; tL = -(ph * Ly - Lxy); tR = -(Rxy - ph * Ry)
        c11 = a22 * a33 - a23 ** 2; c12 = a13 * a23 - a12 * a33; c13 = a12 * a23 - a13 * a22
        c22 = a11 * a33 - a13 ** 2; c23 = a12 * a13 - a11 * a23; c33 = a11 * a22 - a12 ** 2
        det = a11 * c11 + a12 * c12 + a13 * c13
        with np.errstate(invalid='ignore', divide='ignore'):
            b1 = (c11 * ty + c12 * tL + c13 * tR) / det
            b2 = (c12 * ty + c22 * tL + c23 * tR) / det
            b3 = (c13 * ty + c23 * tL + c33 * tR) / det
            rss = Sy2[sl][:, None] - (b1 * ty + b2 * tL + b3 * tR)
        rss = np.where(valid & np.isfinite(rss), rss, np.inf)
        out[sl] = ph[np.arange(len(x)), np.argmin(rss, 1)]
    return out


for w in (6, 8, 20):
    x0 = np.arange(120 - w, 120 + w + 0.1, 2.0)
    B = 1000
    X = x0[None, :] + rng.normal(0, 0.05, (B, x0.size))
    Y = -0.02 * np.abs(X - 120.3) + rng.normal(0, 1e-3, X.shape)
    t0 = time.perf_counter(); r = zelt_seg(X, Y); dt = time.perf_counter() - t0
    print(f'A9.6-Raster 0,001°, segmentweise, w={w} ({x0.size} Punkte), B={B}: {dt:.2f} s je Fit-Satz; Median phi* {np.median(r):.3f}', flush=True)
