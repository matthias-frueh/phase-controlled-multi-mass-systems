"""AP-13 Nachbesserung (nur Planungszahl): Laufzeit einer H2-Kampagne nach A9.6 auf Ebene H.

Je Replikat (B = 1000): Läufe jeder Konfiguration in W und Einzelmodulläufe jedes Moduls mit Zurücklegen
gezogen; ȳ, ρⱼₖ und Abszissen φ̄₂^P = −arg ρ₂₁ neu; F_min − ⟨N⟩ der Messung und der Vorhersagen ŷ⁰, ŷ¹ aus der
bandbegrenzten Kurve; drei Zeltfits (Messung, ŷ⁰, ŷ¹) mit dem exakten Kandidatenverfahren (zelt_schnell.py).
Dazu der Jackknife für BCa (alle Läufe einzeln weggelassen) und die Vollraster-Fassung zum Vergleich.
V1-Kandidat G0 aus code/auslegung.py, Stufe L2 (1 %/0,1° je Modul, σ_h = 0,11 mN), n = n₀ = 20, n₁ = 21.
Nur Laufzeit und Plausibilität (Überdeckung grob), keine Registrierungszahl.
"""
import sys
import time
import numpy as np
import auslegung as A
from zelt_schnell import zelt_kand, zelt_voll

rng = np.random.default_rng(1306)
a = A.Aufbau()
KMAX = a.kmax_standard()
r1 = a.loesen(np.zeros((3, 3)), w=np.eye(3), kmax=KMAX, kout=KMAX)
Nk_mod = np.array([r1['Nk'][j] for j in range(3)]) / 2                 # Konvention: Kurve = Σ Re(N_k e^{ikθ})·…
k = np.arange(1, KMAX + 1)
NTH = 2000
th = 2 * np.pi * np.arange(NTH) / NTH
COS, SIN = np.cos(np.outer(k, th)), np.sin(np.outer(k, th))
SIG_H, SIG_AMP, SIG_PH, SIG_RHO = 0.11e-3, 0.01, 0.10, 0.02          # σ_RHO: über ρ erfasster Laufmittel-Jitter [°]
N, N0, N1 = 20, 20, 21


def kurve_min(Nc, m):
    return (Nc.real @ COS[:, m] - Nc.imag @ SIN[:, m]).min(-1)


def aufbau_w(w):
    p2 = np.arange(120.0 - w, 120.0 + w + 1e-9, 2.0)
    phi = np.c_[np.zeros_like(p2), p2, np.full_like(p2, 240.0)]
    E = np.exp(-1j * np.radians(phi)[:, :, None] * k)                   # (cfg, 3, K)
    masks = []
    for i in range(len(p2)):
        cv = (Nk_mod * E[i]).sum(0)
        cv = cv.real @ COS - cv.imag @ SIN
        masks.append(cv < cv.min() + 0.3)
    return phi, E, masks


def kampagne_daten(phi, E):
    nc = len(phi)
    eps = rng.normal(0, SIG_AMP, (nc, N, 3, 1))
    dl = np.radians(rng.normal(0, SIG_PH, (nc, N, 3, 1)))              # nicht erfasster Anteil
    dr = np.radians(rng.normal(0, SIG_RHO, (nc, N, 3, 1)))             # über die Zeiger erfasster Anteil
    dr[:, :, 0] = 0.0                                                   # Modul 1 definiert θ
    Z = np.exp(-1j * k * dr) * E[:, None]                               # Zeiger je Lauf (cfg, n, 3, K)
    Y = (Nk_mod * (1 + eps) * np.exp(-1j * k * dl) * Z).sum(2)
    Y = Y + SIG_H * (rng.standard_normal(Y.shape) + 1j * rng.standard_normal(Y.shape))
    S = []
    for n_ in (N0, N1):
        e = rng.normal(0, SIG_AMP, (3, n_, 1))
        d = np.radians(rng.normal(0, SIG_PH, (3, n_, 1)))
        S.append(Nk_mod[:, None] * (1 + e) * np.exp(-1j * k * d)
                 + SIG_H * (rng.standard_normal((3, n_, KMAX)) + 1j * rng.standard_normal((3, n_, KMAX))))
    return Y, Z, S[0], S[1]


def multinom(n, shape):
    return rng.multinomial(n, np.full(n, 1.0 / n), size=shape) / n


def jack(n, shape_lead):
    Wj = (1 - np.eye(n)) / (n - 1)
    return np.broadcast_to(Wj, shape_lead + (n, n))


def auswerten(Y, Z, S0, S1, WA, W0, W1, masks, fit):
    """WA (cfg, R, n), W0 (3, R, n0), W1 (3, R, n1) → Δφ*⁰, Δφ*¹ je Replikat (R,)."""
    Yb = np.einsum('crn,cnk->crk', WA, Y)
    rho = np.einsum('crn,cnjk->crjk', WA, Z)
    S0b = np.einsum('jrn,jnk->jrk', W0, S0)
    S1b = np.einsum('jrn,jnk->jrk', W1, S1)
    absz = -np.degrees(np.angle(rho[:, :, 1, 0])).T % 360               # (R, cfg)
    Fm = np.stack([kurve_min(Yb[c], masks[c]) for c in range(len(masks))], 1)
    out = []
    pm = fit(absz, Fm)
    for Sb in (S0b, S1b):
        yh = np.einsum('jrk,crjk->crk', Sb, rho)
        Fp = np.stack([kurve_min(yh[c], masks[c]) for c in range(len(masks))], 1)
        out.append(pm - fit(absz, Fp))
    return out


def h2_kampagne(phi, E, masks, B=1000, bca=True, fit=zelt_kand):
    Y, Z, S0, S1 = kampagne_daten(phi, E)
    nc = len(phi)
    d0, d1 = auswerten(Y, Z, S0, S1, multinom(N, (nc, B)), multinom(N0, (3, B)), multinom(N1, (3, B)), masks, fit)
    if bca:                                                             # Jackknife: jeden Lauf einzeln weglassen
        full = lambda n_, lead, R: np.full(lead + (R, n_), 1.0 / n_)
        for c in range(nc):
            WA = full(N, (nc,), N); WA[c] = (1 - np.eye(N)) / (N - 1)
            auswerten(Y, Z, S0, S1, WA, full(N0, (3,), N), full(N1, (3,), N), masks, fit)
        for j in range(3):
            W0 = full(N0, (3,), N0); W0[j] = (1 - np.eye(N0)) / (N0 - 1)
            W1 = full(N1, (3,), N1); W1[j] = (1 - np.eye(N1)) / (N1 - 1)
            WA = full(N, (nc,), N0)
            auswerten(Y, Z, S0, S1, WA, W0, full(N1, (3,), N0), masks, fit)
            auswerten(Y, Z, S0, S1, full(N, (nc,), N1), full(N0, (3,), N1), W1, masks, fit)
    return np.quantile(d0, [0.025, 0.975]), np.quantile(d1, [0.025, 0.975])


if __name__ == '__main__':
    print(f'k_max = {KMAX}; V1-G0, L2, n = n0 = 20, n1 = 21')
    for w in (6, 8, 20):
        phi, E, masks = aufbau_w(w)
        h2_kampagne(phi, E, masks, B=50, bca=False)
        for B, bca in ((1000, False), (1000, True)):
            t0 = time.perf_counter()
            rep = 3
            for _ in range(rep):
                iv = h2_kampagne(phi, E, masks, B=B, bca=bca)
            dt = (time.perf_counter() - t0) / rep
            print(f'w = {w:2d}° ({len(phi)} Punkte), B = {B}, drei Fits je Replikat{", mit Jackknife (BCa)" if bca else ""}:'
                  f' {dt:.2f} s je Kampagne; Intervall gegen ŷ⁰ [{iv[0][0]:+.3f}, {iv[0][1]:+.3f}]°', flush=True)
    phi, E, masks = aufbau_w(6)
    t0 = time.perf_counter()
    h2_kampagne(phi, E, masks, B=1000, bca=False, fit=zelt_voll)
    print(f'zum Vergleich Vollraster, w = 6°, B = 1000, ohne Jackknife: {time.perf_counter() - t0:.1f} s je Kampagne')
    # grobe Plausibilität: Überdeckung von Δφ* = 0 (identische Module, exakte Superposition) über 100 Kampagnen
    hits = np.array([[lo <= 0 <= hi for lo, hi in h2_kampagne(phi, E, masks, B=400, bca=False)] for _ in range(100)])
    print(f'Plausibilität w = 6°, B = 400, 100 Kampagnen: Anteil 0 ∈ [a⁰, b⁰] = {hits[:, 0].mean():.2f}, '
          f'0 ∈ [a¹, b¹] = {hits[:, 1].mean():.2f}')
