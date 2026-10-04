"""AP-08 Kontrollrechnung (keine Registrierungszahl).

Vereinfachtes Kampagnenmodell wie P2 statistik/s2_h1_oc_kampagne.py (A4-Beispiel: starr, mu = 0,4, 10 Hz,
identische Egg-Module, k_max = 9; weißes Restrauschen plus Lauf-zu-Lauf-Streuung je Modul in Amplitude und
Phase; n = n0 = 20, n1 = 21; Bootstrap B = 200). Geprüft wird die neue Entscheidungsregel des Entwurfs:
- äquivalent (bestätigt): alle 147 |r| + t(0,95; nu)·u <= Delta_q gegen y0 UND y1 (IUT-TOST)
- relevant abweichend (falsifiziert): an einem Test |r| - c·u > Delta_rel gegen y0 und y1, gleiches Vorzeichen
- sonst nicht entscheidbar
c = 95-%-Quantil von max|z0| aus eigenen Kalibrierkampagnen bei exakter Superposition (je Stufe), zum
Vergleich der Bonferroni-Wert c_B. Delta_q Fassung A (max|N_k|) und B (Durchmesser der Zeigermenge);
Delta_rel = Delta_q (Fassung A). Zum Vergleich die registrierte Regel (Nicht-Ablehnung + PB1).
Aufruf: python3 ap08_kontrolle.py LEVEL [NCAL] [NKAMP]
"""
import sys, time
import numpy as np, pandas as pd
from scipy.stats import t as tdist
import linear_solver as L

LEVELS = {0: ('Sensor+Jitter', 0.11e-3, 0.0, 0.02), 1: ('mech 0,3 %/0,03°', 0.11e-3, 0.003, 0.03),
          2: ('mech 1 %/0,1°', 0.11e-3, 0.01, 0.10), 3: ('mech 3 %/0,3°', 0.11e-3, 0.03, 0.30),
          4: ('mech 6 %/0,6°', 0.11e-3, 0.06, 0.60), 5: ('mech 10 %/1°', 0.11e-3, 0.10, 1.00)}
lev = int(sys.argv[1]); NCAL = int(sys.argv[2]) if len(sys.argv) > 2 else 400
NKAMP = int(sys.argv[3]) if len(sys.argv) > 3 else 300
N, N0, N1, KMAX, B, NTH = 20, 20, 21, 9, 200, 2000
label, SIG_H, SIG_AMP, SIG_PH = LEVELS[lev]
rng = np.random.default_rng(5000 + lev)
MU, M = 0.4, L.M
P, NF = L.profile_spectrum()
k = np.arange(1, KMAX + 1)
Nk_mod = 2 * MU * M * P[1:KMAX + 1] / 3 / NF
phi2 = np.arange(100, 140.1, 2.0)
PHI = np.radians(np.stack([np.zeros_like(phi2), phi2, np.full_like(phi2, 240.0)], 1))
E = np.exp(-1j * PHI[:, :, None] * k[None, None, :])
th = 2 * np.pi * np.arange(NTH) / NTH
COS, SIN = np.cos(np.outer(k, th)), np.sin(np.outer(k, th))
masks = []
for i in range(21):
    Ni = (Nk_mod[None, :] * E[i]).sum(0); m = np.zeros(NTH, bool)
    for g in (0.7, 0.9, 1.0, 1.1):
        cv = (Ni * g).real @ COS - (Ni * g).imag @ SIN; m |= cv < cv.min() + 0.3
    masks.append(m)


def qvec(Nc, m):
    out = [(Nc.real @ COS[:, m] - Nc.imag @ SIN[:, m]).min(-1)]
    for kk in range(3):
        out += [Nc[..., kk].real, Nc[..., kk].imag]
    return np.stack(out, -1)


def single_runs(n):
    eps = rng.normal(0, SIG_AMP, (3, n, 1)); dl = np.radians(rng.normal(0, SIG_PH, (3, n, 1)))
    w = SIG_H * (rng.standard_normal((3, n, KMAX)) + 1j * rng.standard_normal((3, n, KMAX)))
    return Nk_mod[None, None, :] * (1 + eps) * np.exp(-1j * k * dl) + w


def comb_runs(n, gfac):
    eps = rng.normal(0, SIG_AMP, (21, n, 3, 1)); dl = np.radians(rng.normal(0, SIG_PH, (21, n, 3, 1)))
    mods = Nk_mod * (1 + eps) * np.exp(-1j * k * dl) * E[:, None, :, :]
    w = SIG_H * (rng.standard_normal((21, n, KMAX)) + 1j * rng.standard_normal((21, n, KMAX)))
    return mods.sum(2) * gfac + w


def boot(X, nb):
    n = X.shape[1]
    W = rng.multinomial(n, np.full(n, 1.0 / n), size=(X.shape[0], nb)) / n
    return np.einsum('gbn,gnk->gbk', W, X)


def campaign(gfac, drift=0.0):
    S0, S1 = single_runs(N0) * (1 + drift), single_runs(N1)
    Y = comb_runs(N, gfac)
    Ybar, A0, A1 = Y.mean(1), S0.mean(1), S1.mean(1)
    yh0, yh1 = np.einsum('jk,ijk->ik', A0, E), np.einsum('jk,ijk->ik', A1, E)
    Yb, S0b, S1b = boot(Y, B), boot(S0, B), boot(S1, B)
    yh0b, yh1b = np.einsum('jbk,ijk->ibk', S0b, E), np.einsum('jbk,ijk->ibk', S1b, E)
    qm, q0, q1, vA, vB0, vB1 = (np.empty((21, 7)) for _ in range(6))
    for i in range(21):
        m = masks[i]
        qm[i], q0[i], q1[i] = qvec(Ybar[i], m), qvec(yh0[i], m), qvec(yh1[i], m)
        vA[i] = qvec(Yb[i], m).var(0, ddof=1)
        vB0[i], vB1[i] = qvec(yh0b[i], m).var(0, ddof=1), qvec(yh1b[i], m).var(0, ddof=1)
    r0, r1 = qm - q0, qm - q1
    u0, u1 = np.sqrt(vA + vB0), np.sqrt(vA + vB1)
    nu0 = u0 ** 4 / (vA ** 2 / (N - 1) + vB0 ** 2 / (N0 - 1))
    nu1 = u1 ** 4 / (vA ** 2 / (N - 1) + vB1 ** 2 / (N1 - 1))
    DA, DB = np.empty(7), np.empty(7)
    DA[0] = DB[0] = q0[:, 0].max() - q0[:, 0].min()
    for kk in range(3):
        z = yh0[:, kk]
        DA[1 + 2 * kk] = DA[2 + 2 * kk] = np.abs(z).max()
        DB[1 + 2 * kk] = DB[2 + 2 * kk] = np.abs(z[:, None] - z[None, :]).max()
    return dict(r0=r0, r1=r1, u0=u0, u1=u1, nu0=nu0, nu1=nu1, DlA=0.25 * DA, DlB=0.25 * DB)


def decide(d, c0, c1):
    r0, r1, u0, u1 = d['r0'], d['r1'], d['u0'], d['u1']
    te0, te1 = tdist.ppf(0.95, d['nu0']), tdist.ppf(0.95, d['nu1'])
    out = {}
    for tag, Dl in (('A', d['DlA']), ('B', d['DlB'])):
        eq = np.all(np.abs(r0) + te0 * u0 <= Dl) and np.all(np.abs(r1) + te1 * u1 <= Dl)
        rel = np.any((np.abs(r0) - c0 * u0 > Dl) & (np.abs(r1) - c1 * u1 > Dl) & (np.sign(r0) == np.sign(r1)))
        out['best_' + tag], out['fals_' + tag], out['beide_' + tag] = eq, rel, eq and rel
    z0, z1 = r0 / u0, r1 / u1
    out['sig_beide'] = np.any((np.abs(z0) > c0) & (np.abs(z1) > c1) & (np.sign(z0) == np.sign(z1)))
    return out


t0 = time.time()
# Kalibrierung von c: q95 von max|z0| bei exakter Superposition (eigene Kampagnen)
cal = [campaign(np.ones(KMAX)) for _ in range(NCAL)]
mz0 = np.array([np.abs(d['r0'] / d['u0']).max() for d in cal])
mz1 = np.array([np.abs(d['r1'] / d['u1']).max() for d in cal])
c_sim0, c_sim1 = np.quantile(mz0, 0.95), np.quantile(mz1, 0.95)
c_B = float(np.median([tdist.ppf(1 - 0.05 / 294, d['nu0']).mean() for d in cal]))
print(f'[{time.time()-t0:6.1f} s] L{lev} {label}: c_sim(z0) = {c_sim0:.3f}, c_sim(z1) = {c_sim1:.3f}, c_B ≈ {c_B:.3f}', flush=True)
SCEN = [('exakt', 0.0), ('kopplung', 0.01), ('kopplung', 0.03), ('kopplung', 0.10), ('kopplung', 0.106),
        ('kopplung', 0.20), ('kopplung', 0.30), ('N2', 0.03), ('drift', 0.03)]
TAG = ''
if len(sys.argv) > 4:   # z. B. kopplung:0.10638,kopplung:0.115
    SCEN = [(s.split(':')[0], float(s.split(':')[1])) for s in sys.argv[4].split(',')]
    TAG = '_rand'
rows = []
for name, x in SCEN:
    g = np.ones(KMAX)
    if name == 'kopplung':
        g[:] = 1 - x
    elif name == 'N2':
        g[1] = 1 + x
    res = []
    for _ in range(NKAMP):
        d = campaign(g, x if name == 'drift' else 0.0)
        o = decide(d, c_sim0, c_sim1)
        cB0, cB1 = tdist.ppf(1 - 0.05 / 294, d['nu0']), tdist.ppf(1 - 0.05 / 294, d['nu1'])
        oB = decide(d, cB0, cB1)
        o['fals_A_cB'], o['sig_beide_cB'] = oB['fals_A'], oB['sig_beide']
        # registrierte Regel (Entwurf September) zum Vergleich
        z0, z1 = d['r0'] / d['u0'], d['r1'] / d['u1']
        s0, s1 = np.abs(z0) > cB0, np.abs(z1) > cB1
        o['alt_fals'] = np.any(s0 & s1 & (np.sign(z0) == np.sign(z1)))
        o['alt_best'] = (not s0.any()) and (not s1.any()) and np.all(np.abs(d['r0']) + cB0 * d['u0'] <= d['DlA'])
        res.append(o)
    df = pd.DataFrame(res).mean()
    row = dict(level=lev, rauschen=label, szenario=name, x=x, nkamp=NKAMP, c_sim0=c_sim0, c_sim1=c_sim1, **df.to_dict())
    rows.append(row)
    print(f'[{time.time()-t0:6.1f} s] L{lev} {name:8s} {x:5.3f}: neu A best {df.best_A:.3f} fals {df.fals_A:.3f} (c_B {df.fals_A_cB:.3f}) | '
          f'B best {df.best_B:.3f} fals {df.fals_B:.3f} | beide {df.beide_A:.3f}/{df.beide_B:.3f} | sig beide {df.sig_beide:.3f} | '
          f'alt best {df.alt_best:.3f} fals {df.alt_fals:.3f}', flush=True)
    pd.DataFrame(rows).to_csv(f'ap08_kontrolle_L{lev}{TAG}.csv', index=False)
