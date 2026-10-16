"""AP-12 Stufe 2: Konfigurationsmittel, Superpositionsvorhersage mit gemessenen Zeigern und die Größen von H1, H1Z,
H2, H4 (Präreg §4, §8.1, §8.2, A1, A9.4 Schritt 7).

ȳ: Mittel der Harmonischen der gültigen Läufe einer Konfiguration (gleich gewichtet, A1); ρⱼₖ = Σ Zeiger/Σ Zyklen
über alle Zyklen aller gültigen Läufe; ŷ_k = Σⱼ N̄_k⁽ʲ⁾·ρⱼₖ mit den Einzelmodulmitteln bezogen auf den eigenen Index,
für die Summe und je Zelle. Größen aus der bandbegrenzten Kurve (k ≤ k_max) auf N_θ = 2000 Stützstellen:
F_min − ⟨N⟩, Re/Im N₁…N₃, γ₁, F_max − ⟨N⟩, A. Das Minimum vieler Kurven bestimmt fmin_rel_viele exakt auf dem
2000-Punkte-Raster: Grobraster jedes zehnten Punkts, Verfeinerung um die drei tiefsten Grobpunkte und eine
Schranke max|x''|·h²/8 ≤ Σ k²|N_k|·h²/8 für die Lücken; reicht die Schranke nicht, wird die Kurve voll ausgewertet.
"""
import numpy as np

from . import konventionen as kv

GROB = 10                                # jeder zehnte Rasterpunkt im Grobraster


def _basis(kmax, punkte):
    th = 2 * np.pi * np.asarray(punkte) / kv.N_THETA
    k = np.arange(1, kmax + 1)
    return np.cos(np.outer(k, th)), -np.sin(np.outer(k, th))


_CACHE = {}


def _basen(kmax):
    if kmax not in _CACHE:
        grob = np.arange(0, kv.N_THETA, GROB)
        _CACHE[kmax] = (grob, _basis(kmax, grob))
    return _CACHE[kmax]


def fmin_rel_viele(Nk, block=8192):
    """F_min − ⟨N⟩ auf dem N_θ-Raster für viele Kurven (…, kmax), exakt gleich kv.fmin_rel."""
    Nk = np.asarray(Nk, complex)
    form = Nk.shape[:-1]
    K = Nk.shape[-1]
    X = Nk.reshape(-1, K)
    n = X.shape[0]
    out = np.empty(n)
    if n == 0:
        return out.reshape(form)
    grob, (C, S) = _basen(K)
    G = grob.size
    k = np.arange(1, K + 1)
    h = 2 * np.pi * GROB / kv.N_THETA
    off = np.arange(-GROB, GROB + 1)
    E_off = np.exp(1j * np.outer(k, 2 * np.pi * off / kv.N_THETA))                 # (K, 21)
    E_grob = np.exp(1j * np.outer(2 * np.pi * grob / kv.N_THETA, k))               # (G, K)
    k2 = k ** 2
    for s0 in range(0, n, block):
        Xb = X[s0:s0 + block]
        nb = Xb.shape[0]
        xg = Xb.real @ C + Xb.imag @ S                                     # Grobraster (nb, G)
        kand = np.argpartition(xg, 3, axis=1)[:, :3]
        Y = Xb[:, None, :] * E_grob[kand]                                  # (nb, 3, K): Zeiger am Kandidaten
        xf = np.real(Y.reshape(-1, K) @ E_off).reshape(nb, -1)             # (nb, 63)
        m = xf.min(1)
        # Schranke für nicht verfeinerte Grobintervalle [g, g+1]
        schranke = (k2 * np.abs(Xb)).sum(1) * h ** 2 / 8
        abgedeckt = np.zeros((nb, G), bool)
        zeilen = np.arange(nb)[:, None]
        abgedeckt[zeilen, kand] = True                                     # Intervall [c, c+1]
        abgedeckt[zeilen, (kand - 1) % G] = True                           # Intervall [c−1, c]
        lo = np.minimum(xg, np.roll(xg, -1, axis=1)) - schranke[:, None]
        unsicher = ((lo < m[:, None]) & ~abgedeckt).any(1)
        if unsicher.any():
            m[unsicher] = kv.fmin_rel(Xb[unsicher])
        out[s0:s0 + nb] = m
    return out.reshape(form)


def groessen(Nk, kmax):
    """Die sieben H1-Größen (…, 7) aus Harmonischen (…, ≥ kmax)."""
    Nk = np.asarray(Nk, complex)[..., :kmax]
    F = fmin_rel_viele(Nk)
    return np.concatenate([F[..., None], np.stack([f(Nk[..., k]) for k in range(3) for f in (np.real, np.imag)],
                                                  -1)], -1)


def zeiger_mittel(zeiger, nz):
    """ρⱼₖ = Σ_Läufe Zeiger / Σ_Läufe Zyklen (über alle Zyklen aller Läufe)."""
    return np.asarray(zeiger).sum(0) / np.asarray(nz, float).sum()


def vorhersage(Nbar, rho, zellen=False):
    """ŷ_k = Σⱼ N̄_k⁽ʲ⁾·ρⱼₖ. Nbar: (Modul, k) Summe bzw. (Modul, Zelle, k); rho: (…, Modul, k)."""
    Nbar, rho = np.asarray(Nbar), np.asarray(rho)
    K = min(Nbar.shape[-1], rho.shape[-1])
    if zellen:
        return np.einsum('jck,...jk->...ck', Nbar[..., :K], rho[..., :K])
    return np.einsum('jk,...jk->...k', Nbar[..., :K], rho[..., :K])


def profilphase2(rho, delta_delta_grad):
    """Gemessene Profilphase von Modul 2: φ̄₂^P = −arg ρ₂₁ + Δδ₂ (A1), in Grad, auf (0°, 360°)."""
    return np.mod(-np.degrees(np.angle(np.asarray(rho)[..., 1, 0])) + delta_delta_grad[1], 360.0)


def kontaktast(Nbar_zellen_voll, rho_voll, N_s_zellen, F_stat_zellen, reserve):
    """Bedingung (a) aus §5.3 mit ŷ⁰ je Zelle ohne Bandbegrenzung: min_θ N̂_c ≥ reserve·F_c,stat (Präreg §4)."""
    y = vorhersage(Nbar_zellen_voll, rho_voll, zellen=True)
    mn = np.asarray(N_s_zellen) + kv.kurve(y).min(-1)
    return bool((mn >= reserve * np.asarray(F_stat_zellen)).all()), mn
