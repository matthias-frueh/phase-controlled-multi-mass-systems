"""H1-Entscheidung als Referenz aus dem Regeltext (§8.2, §8.3, §8.5, §9.3; A1, A8, A9.5).

Nur NumPy/SciPy. Größen q je Schnittpunkt i in der Reihenfolge GROESSEN: F_min − ⟨N⟩ der
bandbegrenzten Kurve x(θ_n) = Σ_{k≤k_max} Re(N_k·e^{ikθ_n}), θ_n = 2πn/N_θ, N_θ = 2000
(Minimum auf den Stützstellen, A1), dazu Re und Im von N₁, N₂, N₃.
"""

import numpy as np
from scipy import stats

N_THETA = 2000
GROESSEN = ('F_min_rel', 'Re N1', 'Im N1', 'Re N2', 'Im N2', 'Re N3', 'Im N3')
N_PUNKTE = 21
N_MODULE = 3
T_NIVEAU = 0.95        # t_eq = t(0,95; ν_eff), PB1 (§8.5)
EPS_ENTARTET = 1e-14   # u ≤ EPS_ENTARTET·S gilt als u = 0 (rauschfreie Daten)
BLOCK = 256            # Kurven je irfft-Block (≈ 4 MB, bleibt im Cache)


def kurve(N, n_theta=N_THETA):
    """x(θ_n) = Σ_k Re(N_k·e^{ikθ_n}) für N der Form (..., k_max); Index 0 ↔ k = 1.

    irfft mit norm='forward' liefert a_0 + 2·Σ_k Re(a_k·e^{ikθ_n}); mit a_k = N_k/2 folgt x.
    """
    N = np.asarray(N, dtype=complex)
    kmax = N.shape[-1]
    if not 1 <= kmax < n_theta // 2:
        raise ValueError('k_max muss in [1, N_θ/2) liegen')
    a = np.zeros(N.shape[:-1] + (n_theta // 2 + 1,), dtype=complex)
    a[..., 1:kmax + 1] = 0.5 * N
    return np.fft.irfft(a, n=n_theta, axis=-1, norm='forward')


def f_min_rel(N, block=BLOCK):
    """F_min − ⟨N⟩ = min_n x(θ_n) je Zeile von N (..., k_max), blockweise ausgewertet."""
    N = np.asarray(N, dtype=complex)
    flach = N.reshape(-1, N.shape[-1])
    aus = np.empty(flach.shape[0])
    for s in range(0, flach.shape[0], block):
        aus[s:s + block] = kurve(flach[s:s + block]).min(axis=-1)
    return aus.reshape(N.shape[:-1])


def groessen(N):
    """Die sieben Größen q(N): (..., k_max) → (..., 7), Reihenfolge GROESSEN."""
    N = np.asarray(N, dtype=complex)
    if N.shape[-1] < 3:
        raise ValueError('mindestens drei Harmonische nötig')
    q = np.empty(N.shape[:-1] + (len(GROESSEN),))
    q[..., 0] = f_min_rel(N)
    for k in range(3):
        q[..., 1 + 2 * k] = N[..., k].real
        q[..., 2 + 2 * k] = N[..., k].imag
    return q


def _zaehlmatrix(idx, n, name):
    """Ziehungsmatrix (B, n) → Häufigkeiten (B, n): wie oft Lauf r in Replikat b gezogen ist."""
    idx = np.asarray(idx)
    if idx.ndim != 2 or idx.shape[0] < 2 or idx.shape[1] != n:
        raise ValueError(f'{name}: Indexmatrix der Form (B ≥ 2, {n}) erwartet, nicht {idx.shape}')
    if not np.issubdtype(idx.dtype, np.integer):
        raise ValueError(f'{name}: ganzzahlige Indizes erwartet')
    if idx.min() < 0 or idx.max() >= n:
        raise ValueError(f'{name}: Index außerhalb 0 … {n - 1}')
    B = idx.shape[0]
    flach = (np.arange(B)[:, None] * n + idx).ravel()
    return np.bincount(flach, minlength=B * n).reshape(B, n).astype(float)


def _basis(einzel, indizes, praefix, kmax):
    """Einzelmodulmittel N̄⁽ʲ⁾ (3, k_max), Bootstrap-B-Replikate (B, 3, k_max), n_B = min_j n_j."""
    if len(einzel) != N_MODULE:
        raise ValueError(f'{praefix}: drei Module erwartet')
    mittel, repl, n_j = [], [], []
    for j in range(N_MODULE):
        X = np.asarray(einzel[j], dtype=complex)
        if X.ndim != 2 or X.shape[0] < 2 or X.shape[1] < kmax:
            raise ValueError(f'{praefix}/modul{j + 1}: Form (n ≥ 2, K ≥ k_max) erwartet')
        X = X[:, :kmax]
        if not np.all(np.isfinite(X)):
            raise ValueError(f'{praefix}/modul{j + 1}: nicht endliche Harmonische')
        C = _zaehlmatrix(indizes[f'{praefix}/modul{j + 1}'], X.shape[0], f'{praefix}/modul{j + 1}')
        mittel.append(X.mean(axis=0))
        repl.append(C @ X / X.shape[0])
        n_j.append(X.shape[0])
    if len({r.shape[0] for r in repl}) != 1:
        raise ValueError(f'{praefix}: gleiche Replikatzahl für alle Module nötig')
    return np.array(mittel), np.stack(repl, axis=1), min(n_j)


def _kombination(r, varA, varB, ub, nA, nB, qy, qh, Delta):
    """u_c, ν_eff, z, TOST je Größe für eine Vorhersage (§8.3, §8.5, A9.5).

    u² = Var_A + Var_B + u_b²; ν = u⁴/(Var_A²/(n_A − 1) + Var_B²/(n_B − 1)), der Biasterm mit ν = ∞.
    Entartet (u ≤ 1e-14·S, S = max(|q(ȳ)|, |q(ŷ)|, Δ_q, 1e-300)): u = 0, ν = ∞, z = 0 oder ±∞.
    """
    u2 = varA + varB + ub ** 2
    u = np.sqrt(u2)
    with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
        a, b = varA / u2, varB / u2                    # Anteile; ν = 1/(a²/(n_A−1) + b²/(n_B−1))
        nenner = a ** 2 / (nA - 1) + b ** 2 / (nB - 1)
        nu = np.where(nenner > 0, 1.0 / nenner, np.inf)
        z = r / u
    S = np.maximum.reduce([np.abs(qy), np.abs(qh), Delta, np.full_like(r, 1e-300)])
    entartet = u <= EPS_ENTARTET * S
    u = np.where(entartet, 0.0, u)
    nu = np.where(entartet, np.inf, nu)
    z = np.where(entartet, np.where(np.abs(r) <= EPS_ENTARTET * S, 0.0, np.copysign(np.inf, r)), z)
    teq = stats.t.ppf(T_NIVEAU, nu)
    tost = (r - teq * u >= -Delta) & (r + teq * u <= Delta)
    return u, nu, z, tost


def _vektor(e, name, n, nichtnegativ=False):
    v = np.asarray(e[name], dtype=float)
    if v.shape != (n,) or not np.all(np.isfinite(v)):
        raise ValueError(f'{name}: endliches Feld der Form ({n},) erwartet')
    if nichtnegativ and np.any(v < 0):
        raise ValueError(f'{name}: Werte ≥ 0 erwartet')
    return v


def h1_referenz(e):
    """H1 aus dem Regeltext: Residuen, u_c, ν_eff, z, TOST (PB1), Mindesteffekt, Ausgang (§9.3).

    e: kmax; punkte (21 Ids, Schnittreihenfolge); laeufe {Id: {Nk (n_i, K), zeiger (n_i, 3, K),
    nz (n_i,)}}, fehlende Id = nicht auswertbar; einzel0, einzel1 (je 3 Felder (n_j, K));
    bias0, bias1, u_bias0, u_bias1 (21,) für F_min − ⟨N⟩; Delta, Delta_rel (7,); c (oder None);
    indizes {'A/<Id>': (B, n_i), 'B0/modul<j>': (B, n0_j), 'B1/modul<j>': (B, n1_j)}.
    Nur k = 1 … k_max (Index 0 … k_max − 1) wird verwendet.

    Rückgabe: Felder (21, 7) r0, r1, u0, u1, varA0, varB0, varA1, varB1, nu0, nu1, z0, z1,
    yquer, yhat0, yhat1 (NaN an fehlenden Punkten); tost0, tost1, relevant (bool, dort False);
    ausgang, abweichung_nachgewiesen, drift (None ohne c), max_abs_z0, n_punkte.
    """
    kmax = int(e['kmax'])
    if not 3 <= kmax < N_THETA // 2:
        raise ValueError('k_max muss in [3, N_θ/2) liegen')
    punkte = list(e['punkte'])
    if len(punkte) != N_PUNKTE or len(set(punkte)) != N_PUNKTE:
        raise ValueError(f'{N_PUNKTE} verschiedene Punkte erwartet')
    P, Q = N_PUNKTE, len(GROESSEN)
    bias0 = _vektor(e, 'bias0', P)
    bias1 = _vektor(e, 'bias1', P)
    u_bias0 = _vektor(e, 'u_bias0', P, nichtnegativ=True)
    u_bias1 = _vektor(e, 'u_bias1', P, nichtnegativ=True)
    Delta = _vektor(e, 'Delta', Q, nichtnegativ=True)
    Delta_rel = _vektor(e, 'Delta_rel', Q, nichtnegativ=True)
    c = e.get('c')
    if c is not None:
        c = float(c)
        if not (np.isfinite(c) and c > 0):
            raise ValueError('c muss endlich und positiv sein')
    laeufe, indizes = e['laeufe'], e['indizes']

    # Vorhersageseite: Mittel und Bootstrap B je Basis (Phase 0 → ŷ⁰, Phase 1 → ŷ¹)
    Nq0, R0, nB0 = _basis(e['einzel0'], indizes, 'B0', kmax)
    Nq1, R1, nB1 = _basis(e['einzel1'], indizes, 'B1', kmax)

    namen = ('r0', 'r1', 'u0', 'u1', 'varA0', 'varB0', 'varA1', 'varB1', 'nu0', 'nu1',
             'z0', 'z1', 'yquer', 'yhat0', 'yhat1')
    aus = {n: np.full((P, Q), np.nan) for n in namen}
    for n in ('tost0', 'tost1', 'relevant'):
        aus[n] = np.zeros((P, Q), dtype=bool)
    n_punkte = 0

    for i, pid in enumerate(punkte):
        if pid not in laeufe:
            continue
        L = laeufe[pid]
        Nk = np.asarray(L['Nk'], dtype=complex)
        Z = np.asarray(L['zeiger'], dtype=complex)
        nz = np.asarray(L['nz'], dtype=float)
        nA = Nk.shape[0] if Nk.ndim == 2 else -1
        if (nA < 2 or Nk.shape[1] < kmax or Z.ndim != 3 or Z.shape[:2] != (nA, N_MODULE)
                or Z.shape[2] < kmax or nz.shape != (nA,) or np.any(nz <= 0)):
            raise ValueError(f'Punkt {pid}: Nk (n ≥ 2, K), zeiger (n, 3, K), nz (n,) > 0 erwartet')
        Nk, Z = Nk[:, :kmax], Z[:, :, :kmax]
        if not (np.all(np.isfinite(Nk)) and np.all(np.isfinite(Z)) and np.all(np.isfinite(nz))):
            raise ValueError(f'Punkt {pid}: nicht endliche Eingangswerte')
        n_punkte += 1

        # Punktschätzer: ȳ, ρ_jk = Σ zeiger / Σ nz, ŷ = Σ_j N̄⁽ʲ⁾·ρ_j (§8.2, A1)
        ybar = Nk.mean(axis=0)
        rho = Z.sum(axis=0) / nz.sum()
        yh0 = np.sum(Nq0 * rho, axis=0)
        yh1 = np.sum(Nq1 * rho, axis=0)

        # Bootstrap A: Läufe mit ihren Zeigern ziehen; ȳ_b, ρ_b, ŷ_b mit festen Basismitteln
        CA = _zaehlmatrix(indizes[f'A/{pid}'], nA, f'A/{pid}')
        BA = CA.shape[0]
        ybar_b = CA @ Nk / nA
        rho_b = (CA @ Z.reshape(nA, -1)).reshape(BA, N_MODULE, kmax) / (CA @ nz)[:, None, None]
        yh0_A = np.einsum('jk,bjk->bk', Nq0, rho_b)
        yh1_A = np.einsum('jk,bjk->bk', Nq1, rho_b)

        # Bootstrap B: Basisreplikate, ρ fest aus allen Läufen des Punkts
        yh0_B = np.einsum('bjk,jk->bk', R0, rho)
        yh1_B = np.einsum('bjk,jk->bk', R1, rho)

        q = groessen(np.concatenate([np.stack([ybar, yh0, yh1]),
                                     ybar_b, yh0_A, yh1_A, yh0_B, yh1_B]))
        qy, qh0, qh1 = q[0], q[1], q[2]
        s = 3
        q_yb, s = q[s:s + BA], s + BA
        q_h0A, s = q[s:s + BA], s + BA
        q_h1A, s = q[s:s + BA], s + BA
        q_h0B, s = q[s:s + R0.shape[0]], s + R0.shape[0]
        q_h1B = q[s:s + R1.shape[0]]

        # Residuen; F_min − ⟨N⟩ um den Rauschbias korrigiert (§8.3)
        b0 = np.zeros(Q)
        b0[0] = bias0[i]
        b1 = np.zeros(Q)
        b1[0] = bias1[i]
        r0 = qy - qh0 - b0
        r1 = qy - qh1 - b1
        varA0 = (q_yb - q_h0A).var(axis=0, ddof=1)
        varA1 = (q_yb - q_h1A).var(axis=0, ddof=1)
        varB0 = (qy - q_h0B).var(axis=0, ddof=1)
        varB1 = (qy - q_h1B).var(axis=0, ddof=1)
        ub0 = np.zeros(Q)
        ub0[0] = u_bias0[i]
        ub1 = np.zeros(Q)
        ub1[0] = u_bias1[i]

        u0, nu0, z0, tost0 = _kombination(r0, varA0, varB0, ub0, nA, nB0, qy, qh0, Delta)
        u1, nu1, z1, tost1 = _kombination(r1, varA1, varB1, ub1, nA, nB1, qy, qh1, Delta)

        # Mindesteffekt (§8.5): |r⁰| − c·u⁰ > Δ_rel und |r¹| − c·u¹ > Δ_rel, gleiches Vorzeichen
        if c is not None:
            aus['relevant'][i] = ((np.abs(r0) - c * u0 > Delta_rel)
                                  & (np.abs(r1) - c * u1 > Delta_rel)
                                  & (np.sign(r0) == np.sign(r1)))

        for n, v in (('r0', r0), ('r1', r1), ('u0', u0), ('u1', u1), ('varA0', varA0),
                     ('varB0', varB0), ('varA1', varA1), ('varB1', varB1), ('nu0', nu0),
                     ('nu1', nu1), ('z0', z0), ('z1', z1), ('yquer', qy), ('yhat0', qh0),
                     ('yhat1', qh1), ('tost0', tost0), ('tost1', tost1)):
            aus[n][i] = v

    # Ausgang (§9.3): falsifiziert vor bestätigt; bestätigt nur mit allen 21 Punkten und PB1
    aequivalent = n_punkte == P and bool(aus['tost0'].all()) and bool(aus['tost1'].all())
    if c is None:
        ausgang = 'bestaetigt' if aequivalent else 'nicht entscheidbar'
        abweichung = drift = None
    else:
        if aus['relevant'].any():
            ausgang = 'falsifiziert'
        elif aequivalent:
            ausgang = 'bestaetigt'
        else:
            ausgang = 'nicht entscheidbar'
        # Zusätze (§9.3): Abweichung nachgewiesen; Drift der Einzelmodulbasis
        g0 = np.abs(aus['z0']) > c
        g1 = np.abs(aus['z1']) > c
        gleich = np.sign(aus['z0']) == np.sign(aus['z1'])
        abweichung = bool((g0 & g1 & gleich).any())
        drift = bool(((g0 & ~(g1 & gleich)) | (g1 & ~(g0 & gleich))).any())

    az0 = np.abs(aus['z0'])
    aus.update(ausgang=ausgang, abweichung_nachgewiesen=abweichung, drift=drift,
               max_abs_z0=float(np.nanmax(az0)) if n_punkte else float('nan'),
               n_punkte=n_punkte)
    return aus
