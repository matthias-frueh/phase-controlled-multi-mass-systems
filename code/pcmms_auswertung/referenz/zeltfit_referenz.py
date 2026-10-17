"""Zeltfit auf dem Vollraster als Referenz (§8.6, A9.6), nur NumPy.

Stetiges Zelt F(φ) = F* − s_L·(φ* − φ) für φ ≤ φ*, F* − s_R·(φ − φ*) sonst. Für jedes φ* des Rasters
φ*_m = min φ + m·Schritt, m = 0 … M, M = ⌊(max φ − min φ)/Schritt + 1e-9⌋, werden F*, s_L, s_R
ungewichtet nach kleinsten Quadraten bestimmt; gewählt wird die kleinste Residuenquadratsumme, bei
Gleichstand das kleinste φ* (A9.6). Spalten mit zentrierter Abszisse d = φ_i − φ*, Lösung über SVD.
"""

import numpy as np

EPS_RASTER = 1e-9   # |φ_i − φ*| ≤ EPS_RASTER·Schritt gilt als 0 (Rundung von min φ + m·Schritt)


def _pruefe(phi, F, schritt):
    phi = np.asarray(phi, dtype=float)
    F = np.asarray(F, dtype=float)
    if phi.ndim != 1 or phi.shape != F.shape or phi.size < 1:
        raise ValueError('phi und F: gleich lange eindimensionale Felder (n ≥ 1) erwartet')
    if not (np.all(np.isfinite(phi)) and np.all(np.isfinite(F))):
        raise ValueError('phi und F müssen endlich sein')
    if not (np.isfinite(schritt) and schritt > 0):
        raise ValueError('Schritt muss endlich und positiv sein')
    return phi, F


def raster(phi, schritt=0.001):
    """Suchraster φ*_m = min φ + m·Schritt, m = 0 … M."""
    phi = np.asarray(phi, dtype=float)
    lo, hi = phi.min(), phi.max()
    M = int(np.floor((hi - lo) / schritt + 1e-9))
    return lo + np.arange(M + 1) * schritt


def _mkq(A, y):
    """Minimum-Norm-Lösung kleinster Quadrate je Stapelelement von A (G, n, p) für y (n,).

    SVD; Singulärwerte ≤ ε·max(n, p)·σ_max gelten als null (wie numpy.linalg.lstsq).
    """
    U, s, Vt = np.linalg.svd(A, full_matrices=False)
    grenze = np.finfo(float).eps * max(A.shape[1], A.shape[2]) * s[:, :1]
    with np.errstate(divide='ignore'):
        sinv = np.where(s > grenze, 1.0 / s, 0.0)
    return np.einsum('grp,gr->gp', Vt, sinv * np.einsum('gnr,n->gr', U, y))


def rss_vollraster(phi, F, schritt=0.001, block=None):
    """Raster, RSS(φ*_m) und Parameter (F*, s_L, s_R) je Rasterpunkt; blockweise über das Raster.

    Hat eine Seite keinen Punkt mit d ≠ 0, entfällt ihre Steigungsspalte (Steigung 0); sonst
    rangdefizit → Minimum-Norm-Lösung.
    """
    phi, F = _pruefe(phi, F, schritt)
    gitter = raster(phi, schritt)
    n = phi.size
    rss = np.empty(gitter.size)
    par = np.zeros((gitter.size, 3))
    block = block or max(1, 200_000 // n)
    for s in range(0, gitter.size, block):
        g = gitter[s:s + block]
        d = phi[None, :] - g[:, None]                       # zentrierte Abszisse φ_i − φ*
        d[np.abs(d) <= EPS_RASTER * schritt] = 0.0
        A = np.empty(d.shape + (3,))
        A[..., 0] = 1.0
        A[..., 1] = np.minimum(d, 0.0)                      # links (d ≤ 0): F = F* + s_L·d
        A[..., 2] = -np.maximum(d, 0.0)                     # rechts (d > 0): F = F* − s_R·d
        links = (d < 0).any(axis=1)
        rechts = (d > 0).any(axis=1)
        x = np.zeros((g.size, 3))
        for hat_l in (True, False):
            for hat_r in (True, False):
                sel = (links == hat_l) & (rechts == hat_r)
                if not sel.any():
                    continue
                sp = [0] + [1] * hat_l + [2] * hat_r        # Spalten leerer Seiten entfallen
                x[np.ix_(sel, sp)] = _mkq(A[sel][:, :, sp], F)
        res = F[None, :] - np.einsum('gnp,gp->gn', A, x)
        rss[s:s + block] = np.einsum('gn,gn->g', res, res)
        par[s:s + block] = x
    return gitter, rss, par


def zeltfit_vollraster(phi, F, schritt=0.001, rel_tol=1e-9):
    """Zeltfit nach A9.6 auf dem Vollraster.

    Gleichstand: alle m mit RSS_m ≤ RSS_min·(1 + rel_tol) + 1e-12·SST, SST = Σ(F − F̄)²;
    gewählt wird das kleinste φ* darunter. Rückgabe: phi_stern, rss, F_stern, s_L, s_R, m,
    n_raster, gleichstand (Zahl der gleichstehenden Rasterpunkte).
    """
    if not (np.isfinite(rel_tol) and rel_tol >= 0):
        raise ValueError('rel_tol muss endlich und ≥ 0 sein')
    gitter, rss, par = rss_vollraster(phi, F, schritt)
    F = np.asarray(F, dtype=float)
    sst = float(np.sum((F - F.mean()) ** 2))
    rmin = float(rss.min())
    gleich = rss <= rmin + rel_tol * rmin + 1e-12 * sst
    m = int(np.argmax(gleich))                              # erstes True = kleinstes φ*
    return dict(phi_stern=float(gitter[m]), rss=float(rss[m]), F_stern=float(par[m, 0]),
                s_L=float(par[m, 1]), s_R=float(par[m, 2]), m=m, n_raster=int(gitter.size),
                gleichstand=int(gleich.sum()))
