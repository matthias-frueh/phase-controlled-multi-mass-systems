"""AP-12 Stufe 2: Bootstrap A und B nach Präreg A9.5 mit Indexmatrizen nach Plan AP-13 2.6 c.

Indexmatrizen: numpy.random.SeedSequence(seed).spawn in fester Reihenfolge – A_i für alle Konfigurationen in der
Listenreihenfolge von Teil B, B¹₁ … B¹₃, H3, H4, E3, danach die Quellen bei Einstellung 2 (B¹′₁ … B¹′₃); je Kind
Generator(PCG64(kind)).integers(0, n, size=(B, n)) über die gültigen Läufe der Quelle in aufsteigender Position.
Zuletzt der Strom E3/T der Ziehungen von T (keine Indexmatrix); die übrigen Ströme ändern sich dadurch nicht.
B⁰ⱼ stehen fest in Teil B (nicht neu gezogen). Übergebene Indizes ersetzen die Ziehung vollständig.

Bootstrap A (Messung): Läufe der Konfiguration mit Zurücklegen, mit ihren Zeigern; ȳ, ρⱼₖ und ŷ je Replikat neu.
Bootstrap B (Vorhersage): Einzelmodulläufe jedes Moduls mit Zurücklegen, ρⱼₖ fest. Varianz der Replikate mit
ddof = 1 (Regel bootstrap.varianz). H2 verwendet je Replikat b die Zeile b aller Quellen gemeinsam.
"""
import numpy as np

from . import vorhersage as vh


def quellen_reihenfolge(konfig_ids, einstellung2=False):
    """Schlüssel der gezogenen Quellen in Spawn-Reihenfolge (B⁰ fehlt: steht in Teil B)."""
    q = [f'A/{k}' for k in konfig_ids] + [f'B1/modul{j}' for j in (1, 2, 3)] + ['H3', 'H4', 'E3']
    if einstellung2:
        q += [f"B1′/modul{j}" for j in (1, 2, 3)]
    return q + ['E3/T']                  # Ziehungen der Übertragungsmatrix (Korrektur E), zuletzt


def indexmatrizen(seed, groessen, B, reihenfolge):
    """groessen: Schlüssel → Zahl gültiger Läufe; Rückgabe Schlüssel → (B, n) int64 (nur für Schlüssel mit n)."""
    kinder = np.random.SeedSequence(seed).spawn(len(reihenfolge))
    out = {}
    for key, kind in zip(reihenfolge, kinder):
        n = groessen.get(key)
        if n:
            out[key] = np.random.Generator(np.random.PCG64(kind)).integers(0, n, size=(B, n))
    return out


def mc_strom(seed, reihenfolge, key):
    """Zufallsstrom einer Monte-Carlo-Quelle (H3, E3) aus derselben Spawn-Reihenfolge."""
    kinder = np.random.SeedSequence(seed).spawn(len(reihenfolge))
    return np.random.Generator(np.random.PCG64(kinder[reihenfolge.index(key)]))


def zaehlmatrix(idx, n):
    """(B, n): wie oft jeder Lauf in jedem Replikat gezogen ist."""
    idx = np.asarray(idx)
    C = np.zeros((idx.shape[0], n))
    np.add.at(C, (np.repeat(np.arange(idx.shape[0]), idx.shape[1]), idx.ravel()), 1.0)
    return C


def varianz(x):
    return np.var(x, axis=0, ddof=1)


def _q4(Yz, kmax):
    """Größen (…, 4, 7): Summe und drei Zellen aus Zellharmonischen (…, 3, K)."""
    Ys = Yz.sum(-2)
    return np.concatenate([vh.groessen(Ys, kmax)[..., None, :], vh.groessen(Yz, kmax)], -2)


def h1_varianzen(X, Z, nz, Nbar0, Nbar1, E0, E1, idxA, idxB0, idxB1, rho, kmax, block=1000):
    """Var_A und Var_B je Vorhersage für eine Konfiguration (Summe und Zellen, 7 Größen).
    X (n, 3, K) Zellharmonische der Läufe, Z (n, 3, K) Zeiger, nz (n); Nbar0/1 (Modul, Zelle, K); E0/E1: Liste je Modul
    (n_j, 3, K); idx*: Indexmatrizen; rho: ρ aus allen Läufen. Rückgabe dict varA0, varA1, varB0, varB1 (4, 7)."""
    n = X.shape[0]
    K = kmax
    X, Z = X[..., :K], Z[..., :K]
    y = X.mean(0)
    qy = _q4(y, kmax)
    rA0, rA1 = [], []
    for s0 in range(0, idxA.shape[0], block):
        C = zaehlmatrix(idxA[s0:s0 + block], n)
        yb = (C @ X.reshape(n, -1)).reshape(-1, 3, K) / n
        rb = (C @ Z.reshape(n, -1)).reshape(-1, 3, K) / (C @ nz)[:, None, None]
        q = _q4(yb, kmax)
        rA0.append(q - _q4(vh.vorhersage(Nbar0[..., :K], rb, zellen=True), kmax))
        rA1.append(q - _q4(vh.vorhersage(Nbar1[..., :K], rb, zellen=True), kmax))
    out = dict(varA0=varianz(np.concatenate(rA0)), varA1=varianz(np.concatenate(rA1)))
    for name, E, idx in (('varB0', E0, idxB0), ('varB1', E1, idxB1)):
        rB = []
        Bn = idx[0].shape[0]
        for s0 in range(0, Bn, block):
            Nb = []
            for j in range(3):
                nj = E[j].shape[0]
                C = zaehlmatrix(idx[j][s0:s0 + block], nj)
                Nb.append((C @ E[j][..., :K].reshape(nj, -1)).reshape(-1, 3, K) / nj)
            Nb = np.stack(Nb, 1)                                        # (b, Modul, Zelle, K)
            yhat = np.einsum('bjck,jk->bck', Nb, rho[..., :K])
            rB.append(qy[None] - _q4(yhat, kmax))
        out[name] = varianz(np.concatenate(rB))
    return out
