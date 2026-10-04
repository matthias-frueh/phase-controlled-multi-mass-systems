"""s3b_h2_bootstrap_check.py – Stichprobe: Liefert das registrierte Bootstrap-Intervall für Δφ* (A9.6) dieselbe
Halbbreite wie die Monte-Carlo-Verteilung in s3, und hält es die Überdeckung 0,95 (A9.11, Soll ≥ 0,95)?

Prüfgruppe statistik, P2. Nutzt die Funktionen aus s3_h2_zeltfit_mc.py (Kopie der Logik, Import über exec
der Funktionsdefinitionen wäre fragil; daher hier minimal neu aufgebaut).
Fälle: 'ref' s = 1, SNR = 1, n = n₀ = 20 (w = 16) und 'A4' s = 1, SNR = 1, n = n₀ = 20 (w = 6);
Läufe einzeln simuliert (weißes Restrauschen je Lauf), Bootstrap über Läufe der Konfigurationen und über
Einzelmodulläufe (B Replikate), 95-%-Perzentilintervall; Wahrheit Δφ* = 0 (exakte Superposition).
Aufruf: python3 s3b_h2_bootstrap_check.py [NKAMP] [B]
"""
import sys
import numpy as np
import linear_solver as L

rng = np.random.default_rng(99)
KMAX, NTH = 9, 2000
M = L.M
P, NF = L.profile_spectrum()
k = np.arange(1, KMAX + 1)
th = 2 * np.pi * np.arange(NTH) / NTH
COS, SIN = np.cos(np.outer(k, th)), np.sin(np.outer(k, th))
PHI2 = np.arange(100, 140.1, 2.0)
NKAMP = int(sys.argv[1]) if len(sys.argv) > 1 else 150
B = int(sys.argv[2]) if len(sys.argv) > 2 else 400


def module_harm(shape):
    if shape == 'ref':
        H, _ = L.transfer(1e4, 16.0, P.size)
        return 2 * M * (P * H)[1:KMAX + 1] / 3 / NF
    return 2 * 0.4 * M * P[1:KMAX + 1] / 3 / NF


def tent_fit(x, Y, step1=0.02):
    Y = np.atleast_2d(Y)
    ps = np.arange(x.min(), x.max() + 1e-9, step1)
    X = np.stack([np.ones((ps.size, x.size)), -np.clip(ps[:, None] - x[None, :], 0, None),
                  -np.clip(x[None, :] - ps[:, None], 0, None)], -1)
    Pm = np.einsum('gnp,gpq,gmq->gnm', X, np.linalg.pinv(np.einsum('gnp,gnq->gpq', X, X)), X)
    c = np.empty(Y.shape[0])
    for c0 in range(0, Y.shape[0], 100):
        Yc = Y[c0:c0 + 100]
        rss = ((Yc[:, None, :] - np.einsum('gnm,rm->rgn', Pm, Yc)) ** 2).sum(-1)
        c[c0:c0 + 100] = ps[np.argmin(rss, 1)]
    rel = np.arange(-step1, step1 + 1e-9, 0.001)
    fine = np.clip(c[:, None] + rel[None, :], x.min(), x.max())
    Xd = np.stack([np.ones(fine.shape + (x.size,)), -np.clip(fine[:, :, None] - x, 0, None),
                   -np.clip(x - fine[:, :, None], 0, None)], -1)
    beta = np.einsum('rgpq,rgq->rgp', np.linalg.pinv(np.einsum('rgnp,rgnq->rgpq', Xd, Xd)),
                     np.einsum('rgnp,rn->rgp', Xd, Y))
    rss = ((Y[:, None, :] - np.einsum('rgnp,rgp->rgn', Xd, beta)) ** 2).sum(-1)
    return fine[np.arange(Y.shape[0]), np.argmin(rss, 1)]


for shape, w in (('ref', 16), ('A4', 6)):
    Nm = module_harm(shape)
    sel = (PHI2 >= 120 - w) & (PHI2 <= 120 + w)
    x = PHI2[sel]
    PH = np.radians(np.stack([np.zeros(sel.sum()), x, np.full(sel.sum(), 240.0)], 1))
    E = np.exp(-1j * PH[:, :, None] * k)
    Ntrue = (Nm * E).sum(1)
    cv = Ntrue.real @ COS - Ntrue.imag @ SIN
    F = cv.min(1)
    sbar = ((F[x == 120][0] - F[x == 118][0]) + (F[x == 120][0] - F[x == 122][0])) / 4
    s_run = sbar / 1.0                              # SNR = 1
    sig_h = s_run / np.sqrt(KMAX)
    masks = [cv[i] < cv[i].min() + max(0.3, 8 * s_run) for i in range(sel.sum())]
    n = n0 = 20

    def fmin_all(Nc):                              # Nc: (R, npt, K)
        return np.stack([(Nc[:, i].real @ COS[:, masks[i]] - Nc[:, i].imag @ SIN[:, masks[i]]).min(-1)
                         for i in range(sel.sum())], 1)

    est, lo, hi = [], [], []
    for _ in range(NKAMP):
        Y = Ntrue[:, None, :] + sig_h * (rng.standard_normal((sel.sum(), n, KMAX)) + 1j * rng.standard_normal((sel.sum(), n, KMAX)))
        S = Nm[None, None, :] + sig_h * (rng.standard_normal((3, n0, KMAX)) + 1j * rng.standard_normal((3, n0, KMAX)))
        # Punktschätzung
        Fm = fmin_all(Y.mean(1)[None])[0]
        Fp = fmin_all(np.einsum('jk,ijk->ik', S.mean(1), E)[None])[0]
        d0 = tent_fit(x, Fm[None])[0] - tent_fit(x, Fp[None])[0]
        # Bootstrap
        Wm = rng.multinomial(n, np.full(n, 1 / n), size=(sel.sum(), B)) / n            # npt × B × n
        Yb = np.einsum('ibn,ink->bik', Wm, Y)
        Ws = rng.multinomial(n0, np.full(n0, 1 / n0), size=(3, B)) / n0
        Sb = np.einsum('jbn,jnk->bjk', Ws, S)
        Pb = np.einsum('bjk,ijk->bik', Sb, E)
        db = tent_fit(x, fmin_all(Yb)) - tent_fit(x, fmin_all(Pb))
        q = np.quantile(db, [0.025, 0.975])
        est.append(d0)
        lo.append(q[0])
        hi.append(q[1])
    est, lo, hi = map(np.array, (est, lo, hi))
    qmc = np.quantile(est, [0.025, 0.975])
    print(f'{shape} (w = {w}, SNR = 1, n = n0 = 20, {NKAMP} Kampagnen, B = {B}): '
          f'MC-Halbbreite {(qmc[1]-qmc[0])/2:.3f}°, mittlere Bootstrap-Halbbreite {np.mean((hi-lo)/2):.3f}° '
          f'(Median {np.median((hi-lo)/2):.3f}°), Überdeckung von 0: {np.mean((lo <= 0) & (hi >= 0)):.3f}, '
          f'P(Halbbreite ≤ 1°) = {np.mean((hi-lo)/2 <= 1):.3f}', flush=True)
