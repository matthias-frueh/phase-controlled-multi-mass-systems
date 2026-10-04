"""AP-13 Nachbesserung (nur Laufzeit): (1) Kampagne Ebene H mit Bootstrap A nach A9.5 (ρⱼₖ und ŷ je
Replikat aus den gezogenen Läufen mit ihren Zeigern), n = 20, 40, 80, B = 1000; (2) Lauf Ebene Z bei f_s = 8,5 kHz
(A6: k_max = 12 bei 10 Hz verlangt f_s ≥ 8,4 kHz) statt 6,4 kHz, mit Restfehler rauschfrei.
Grundlage: ap13_zeit.py (Modell der Kurzmessung), nur Teile (a)–(c)."""
import time
import numpy as np
src = open('ap13_zeit.py', encoding='utf-8').read().split('# (d)')[0]
src = src.replace("for B in (200, 1000):", "for B in ():")
src = src.replace("zeit('(c) ein Lauf", "pass  # zeit('(c) ein Lauf")
exec(src)


def runs_comb_z(n):
    eps = rng.normal(0, SIG_AMP, (21, n, 3, 1))
    dl = np.radians(rng.normal(0, SIG_PH, (21, n, 3, 1)))
    dr = np.radians(rng.normal(0, 0.02, (21, n, 3, 1))); dr[:, :, 0] = 0
    Z = np.exp(-1j * k * dr) * E[:, None, :, :]                       # Zeiger je Lauf
    Y = (Nk_mod / 2 * (1 + eps) * np.exp(-1j * k * dl) * Z).sum(2)
    return Y + SIG_H * (rng.standard_normal(Y.shape) + 1j * rng.standard_normal(Y.shape)), Z


def kampagne_a95(B, n, n0, n1):
    S0, S1 = runs_single(n0), runs_single(n1)
    Y, Z = runs_comb_z(n)
    S0b, S1b = boot(S0, B), boot(S1, B)                                # (3, B, K)
    S0m, S1m = S0.mean(1), S1.mean(1)
    z = np.empty((2, 21, 7))
    for i in range(21):
        m = masks[i]
        W = rng.multinomial(n, np.full(n, 1.0 / n), size=B) / n        # Bootstrap A: Läufe mit ihren Zeigern
        Yb = W @ Y[i]
        rb = np.einsum('bn,njk->bjk', W, Z[i])
        rm = Z[i].mean(0)
        qm = qvec(Y[i].mean(0), m)
        for s, (Sm, Sb) in enumerate(((S0m, S0b), (S1m, S1b))):
            yh = (Sm * rm).sum(0)
            vA = (qvec(Yb, m) - qvec((Sm[None] * rb).sum(1), m)).var(0, ddof=1)      # ȳ, ρ, ŷ je Replikat neu
            vB = qvec(np.einsum('jbk,jk->bk', Sb, rm), m).var(0, ddof=1)            # Einzelmodulläufe, ρ fest
            z[s, i] = (qm - qvec(yh, m)) / np.sqrt(vA + vB)
    return np.abs(z).max()


for n in (20, 40, 80):
    kampagne_a95(50, n, n, n + 1)
    t0 = time.perf_counter()
    mz = [kampagne_a95(1000, n, n, n + 1) for _ in range(5)]
    print(f'Ebene H, A9.5 mit ρ je Replikat, n = n0 = {n}, n1 = {n + 1}, B = 1000: '
          f'{(time.perf_counter() - t0) / 5:.3f} s je Kampagne (max|z| {np.median(mz):.2f})', flush=True)

FS = 8500
NS = int(FS / F)
for fs in (6400, 8500):
    FS = fs; NS = int(FS / F)
    lauf_zeitreihe()
    t0 = time.perf_counter()
    for _ in range(10):
        lauf_zeitreihe()
    dt = (time.perf_counter() - t0) / 10
    mk = lauf_zeitreihe(sig=0.0, jit=0.0)
    soll = (Fzk * np.exp(-1j * np.radians(np.array([0, 120, 240]))[:, None, None] * kz)).sum(0) * 2
    print(f'Ebene Z, f_s = {fs} Hz, 100 Zyklen, Summe + 3 Zellen, Kette A9.4: {1e3 * dt:.1f} ms je Lauf; '
          f'rauschfrei max|Δ| Zellen {np.abs(mk[:3] - soll).max():.2e} N, Summe {np.abs(mk[3] - soll.sum(0)).max():.2e} N',
          flush=True)
