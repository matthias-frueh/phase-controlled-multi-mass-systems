"""v6_praezisionsparadox_oc.py – Gegenprüfung STA-09 (Präzisionsparadox) und STA-08 (OC unter Abweichungen)
mit eigenem, vereinfachtem Kampagnenmodell: analytische u_q je Test (lineare Fortpflanzung, Rauschmodell der
Gruppe: σ_h = 0,11 mN, Modulamplitude σ_a, Modulphase σ_p; Kombinationslauf drei Module, Einzellauf eines),
normalverteilte Fehler je Test, Tests unabhängig, geschätztes u über χ²_37 (ν_eff der Gruppe ≈ 37).
Regel §9.3 (registriert) sowie IUT-TOST-Vorschlag der Gruppe (t(0,95; 37), gegen ŷ⁰ und ŷ¹, ohne Signifikanzbedingung).
Szenarien: exakt; Kopplung x (Kombinationsläufe × (1 − x)); N₂ × (1 + x).
"""
import os
import numpy as np
from scipy.stats import t as tdist

M, G = 0.650, 9.81
F = 10.0
T = 1 / F
RTOP, THOLD = 0.005, 0.65
TFAST = 1 - THOLD
RBOT = RTOP * TFAST / THOLD
MU = 0.4
A_HOLD = -RTOP * (np.pi / (THOLD * T)) ** 2
A_FAST = RBOT * (np.pi / (TFAST * T)) ** 2


def accel(t):
    p = np.mod(t, T) / T
    return np.where(p < THOLD, A_HOLD * np.sin(np.pi * p / THOLD), A_FAST * np.sin(np.pi * (p - THOLD) / TFAST))


KMAX = 9
kk = np.arange(1, KMAX + 1)
cmod = 2 * np.fft.rfft(MU * M / 3 * accel(np.arange(16000) / 16000 * T))[1:KMAX + 1] / 16000
PHI2 = np.arange(100, 140.1, 2.0)
PHI = np.radians(np.stack([np.zeros(21), PHI2, np.full(21, 240.0)], 1))
E = np.exp(-1j * PHI[:, :, None] * kk)
NTH = 4000
th = 2 * np.pi * np.arange(NTH) / NTH
EXP = np.exp(1j * np.outer(kk, th))


def fmin_of(Nk):
    return (Nk[..., :, None] * EXP).real.sum(-2).min(-1)


NKc = (cmod * E).sum(1)
cv = (NKc[:, :, None] * EXP[None]).real.sum(1)
thmin = th[cv.argmin(1)]
d = np.array([[(cmod * E[i, j] * np.exp(1j * kk * thmin[i])).real.sum() for j in range(3)] for i in range(21)])
g = np.array([[(cmod * E[i, j] * (-1j * kk) * np.exp(1j * kk * thmin[i])).real.sum() for j in range(3)] for i in range(21)])
DELTA = np.array([0.1293, 0.1126, 0.1126, 0.0731, 0.0731, 0.1383, 0.1383])
LEVELS = [(0.11e-3, 0.0, 0.02), (0.11e-3, 0.003, 0.03), (0.11e-3, 0.01, 0.10), (0.11e-3, 0.03, 0.30),
          (0.11e-3, 0.06, 0.60), (0.11e-3, 0.10, 1.00)]


def var_parts(sh, sa, spd, nA, nB):
    sp = np.radians(spd)
    vA = np.empty((21, 7)); vB = np.empty((21, 7))
    mod_F = sa ** 2 * (d ** 2).sum(1) + sp ** 2 * (g ** 2).sum(1)
    vA[:, 0] = (KMAX * sh ** 2 + mod_F) / nA
    vB[:, 0] = (3 * KMAX * sh ** 2 + mod_F) / nB
    for q in range(3):
        a_ = cmod[q] * E[:, :, q]
        p_ = -1j * (q + 1) * a_
        for part, col in ((np.real, 1 + 2 * q), (np.imag, 2 + 2 * q)):
            mod_q = sa ** 2 * (part(a_) ** 2).sum(1) + sp ** 2 * (part(p_) ** 2).sum(1)
            vA[:, col] = (sh ** 2 + mod_q) / nA
            vB[:, col] = (3 * sh ** 2 + mod_q) / nB
    return vA, vB


def resid(name, x):
    r = np.zeros((21, 7))
    if name == 'exakt':
        return r
    Nd = NKc * (1 - x) if name == 'kopplung' else NKc.copy()
    if name == 'N2':
        Nd[:, 1] *= (1 + x)
    r[:, 0] = fmin_of(Nd) - fmin_of(NKc)
    for q in range(3):
        r[:, 1 + 2 * q] = (Nd[:, q] - NKc[:, q]).real
        r[:, 2 + 2 * q] = (Nd[:, q] - NKc[:, q]).imag
    return r


c = tdist.ppf(1 - 0.05 / 294, 37)
ce = tdist.ppf(0.95, 37)
rng = np.random.default_rng(17)
RR = 10000
out = []
pr = out.append
pr(f'c = {c:.3f}, c_eq = {ce:.3f}; {RR} Kampagnen je Zelle; Einträge P(falsifiziert)/P(bestätigt) [P(IUT-bestätigt)]')
pr('| Szenario | ' + ' | '.join(f'L{L}' for L in range(6)) + ' |')
pr('|---|' + '---|' * 6)
for name, x in (('exakt', 0), ('kopplung', 0.01), ('kopplung', 0.03), ('kopplung', 0.10), ('N2', 0.01), ('N2', 0.03)):
    r = resid(name, x)
    cells = []
    for (sh, sa, sp) in LEVELS:
        vA, vB0 = var_parts(sh, sa, sp, 20, 20)
        _, vB1 = var_parts(sh, sa, sp, 20, 21)
        u0, u1 = np.sqrt(vA + vB0), np.sqrt(vA + vB1)
        fals = conf = iut = 0
        for c0 in range(0, RR, 1000):
            nb = 1000
            eA = rng.standard_normal((nb, 21, 7)) * np.sqrt(vA)
            r0 = r + eA - rng.standard_normal((nb, 21, 7)) * np.sqrt(vB0)
            r1 = r + eA - rng.standard_normal((nb, 21, 7)) * np.sqrt(vB1)
            s0 = np.sqrt(rng.chisquare(37, (nb, 21, 7)) / 37)
            s1 = np.sqrt(rng.chisquare(37, (nb, 21, 7)) / 37)
            U0, U1 = u0 * s0, u1 * s1
            z0, z1 = r0 / U0, r1 / U1
            sig0, sig1 = np.abs(z0) > c, np.abs(z1) > c
            f_ = (sig0 & sig1 & (np.sign(z0) == np.sign(z1))).any((1, 2))
            pb1 = (np.abs(r0) + c * U0 <= DELTA).all((1, 2))
            cf = ~sig0.any((1, 2)) & ~sig1.any((1, 2)) & pb1
            it = (np.abs(r0) + ce * U0 <= DELTA).all((1, 2)) & (np.abs(r1) + ce * U1 <= DELTA).all((1, 2))
            fals += f_.sum(); conf += cf.sum(); iut += it.sum()
        cells.append(f'{fals/RR:.3f}/{conf/RR:.3f} [{iut/RR:.2f}]')
    pr(f'| {name} {100*x:.0f} % | ' + ' | '.join(cells) + ' |')
txt = '\n'.join(out)
print(txt)
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v6_praezisionsparadox_oc_ausgabe.txt'), 'w').write(txt + '\n')
