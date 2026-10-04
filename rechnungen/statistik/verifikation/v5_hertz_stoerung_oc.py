"""v5_hertz_stoerung_oc.py – Gegenprüfung STA-11 (Hertz-Kontakt), STA-08/09 (Typ-I-Rate, P(falsifiziert) bei
kleinen Abweichungen auf Stufe L0).

1) Hertz-Kontakt N_el = κ·δ^{3/2}, linearisiert f_n0 bei statischer Last, ζ = 0,05 (wie s4), A4-Beispiel
   (μ = 0,4, 10 Hz). EIGENER RECHENWEG: Störungsrechnung 2. Ordnung im Frequenzbereich statt RK4:
     M·ÿ + c·ẏ + K₀·y + q·y² = μ·M·ā(t),  q = K₀/(4δ₀),  N − Mg = K₀y + cẏ + q·y²
     ⇒ N₂,k = (1 − H(kω))·FT[q·y₁²]_k ;  Superpositionsresiduum R_k = (1 − H(kω))·q·FT[(Σ_j y_j)² − Σ_j y_j²]_k
   (y_j: lineare Antwort auf Modul j allein). Gegenprobe: Vergleich mit den RK4-Werten der Gruppe.
2) Typ-I-Rate der H1-Falsifikationsregel analytisch (bivariat normal, Korrelation von z⁰ und z¹ aus dem
   Anteil der gemeinsamen Messseite) – Schranke Σ_Tests P(|z⁰| > c ∧ |z¹| > c, gleiches Vorzeichen).
3) P(falsifiziert) auf Stufe L0 (u_q je Test analytisch aus v1-Modell: σ_h = 0,11 mN, σ_p = 0,02°,
   n = n₀ = 20, n₁ = 21) für Residuen aus Hertz 300 Hz (eigene Störungsrechnung), Kopplung 0,1 %/1 %
   (Kombinationsläufe × (1 − x), wie s2/s4) – Monte Carlo über normalverteilte Fehler je Test.
"""
import os
import numpy as np
from scipy.stats import multivariate_normal, norm, t as tdist

M, G = 0.650, 9.81
MG = M * G
F = 10.0
T = 1 / F
w0 = 2 * np.pi * F
RTOP, THOLD = 0.005, 0.65
TFAST = 1 - THOLD
RBOT = RTOP * TFAST / THOLD
MU = 0.4
A_HOLD = -RTOP * (np.pi / (THOLD * T)) ** 2
A_FAST = RBOT * (np.pi / (TFAST * T)) ** 2


def accel(t):
    p = np.mod(t, T) / T
    return np.where(p < THOLD, A_HOLD * np.sin(np.pi * p / THOLD), A_FAST * np.sin(np.pi * (p - THOLD) / TFAST))


NF = 8192
tt = np.arange(NF) / NF * T
Ak = np.fft.rfft(accel(tt)) / NF                       # x(t) = Σ_k A_k e^{ikωt} (rfft-Konvention, beidseitig ×2)
kall = np.arange(Ak.size)
PHI2 = np.arange(100, 140.1, 2.0)
PHI = np.radians(np.stack([np.zeros(21), PHI2, np.full(21, 240.0)], 1))
out = []
pr = out.append


def to_time(Xk):
    return np.fft.irfft(Xk * NF, NF)


def harm_N(x):                                          # N_k-Konvention (2/N)·Σ x e^{−ikθ}
    return 2 * np.fft.rfft(x) / NF


def bandcurve(Nk, kmax, nth=4000):
    th = 2 * np.pi * np.arange(nth) / nth
    kk = np.arange(1, kmax + 1)
    return (Nk[..., 1:kmax + 1, None] * np.exp(1j * kk[:, None] * th[None, :])).real.sum(-2)


pr('=== 1) Hertz-Kontakt: Störungsrechnung 2. Ordnung (eigener Rechenweg) gegen RK4 der Gruppe (s4) ===')
RK4 = {300: (0.507, 0.786, 1.066, 0.0098, 0.1100, 0.4123), 120: (3.441, 6.291, 12.270, 0.0647, 0.7314, 2.8399),
       60: (19.040, 195.799, 207.441, 0.4333, 3.9097, 16.0948)}
HRES = {}
for fn in (300.0, 120.0, 60.0):
    K0 = M * (2 * np.pi * fn) ** 2
    c = 2 * 0.05 * np.sqrt(K0 * M)
    d0 = 1.5 * MG / K0
    q = K0 / (4 * d0)
    om = kall * w0
    Y = 1 / (K0 - M * om ** 2 + 1j * om * c)
    H = (K0 + 1j * om * c) * Y
    res_k = {}
    # y_j je Konfiguration (Modul j allein, Zeitbereich)
    Rk_all = np.empty((21, kall.size), complex)
    Nlin_all = np.empty((21, kall.size), complex)
    for i in range(21):
        ys = [to_time(MU * M / 3 * Ak * np.exp(-1j * kall * PHI[i, j]) * Y) for j in range(3)]
        cross = (sum(ys)) ** 2 - sum(y_ ** 2 for y_ in ys)
        self_ = sum(y_ ** 2 for y_ in ys)
        Ck = np.fft.rfft(q * cross) / NF
        Sk = np.fft.rfft(q * self_) / NF
        Lk = (MU * M / 3 * Ak * H) * (1 + np.exp(-1j * kall * PHI[i, 1]) + np.exp(-1j * kall * PHI[i, 2]))
        Rk_all[i] = 2 * (1 - H) * Ck                    # N_k-Konvention
        Nlin_all[i] = 2 * (Lk + (1 - H) * Sk)           # Vorhersage (Summe der Einzelläufe inkl. Eigenanteil)
    rF = {}
    for km in (3, 6, 9):
        pred = bandcurve(Nlin_all, km)
        meas = bandcurve(Nlin_all + Rk_all, km)
        rF[km] = 1e3 * np.abs(meas.min(1) - pred.min(1)).max()
    rN = [1e3 * max(np.abs(Rk_all[:, kk].real).max(), np.abs(Rk_all[:, kk].imag).max()) for kk in (1, 2, 3)]
    ymax = max(np.abs(to_time(MU * M * Ak * Y)).max(), 0)
    g = RK4[int(fn)]
    pr(f'f_n0 = {fn:5.0f} Hz (K₀ = {K0:.3e} N/m, δ₀ = {1e6*d0:.2f} µm, y_max(synchron) ≈ {1e6*ymax:.2f} µm, '
       f'y/δ₀ ≈ {ymax/d0:.2f}): max|r_F| k_max = 3/6/9: {rF[3]:.3f}/{rF[6]:.3f}/{rF[9]:.3f} mN '
       f'(RK4 Gruppe {g[0]}/{g[1]}/{g[2]}); max|r| N1/N2/N3: {rN[0]:.4f}/{rN[1]:.4f}/{rN[2]:.4f} mN '
       f'(RK4 {g[3]}/{g[4]}/{g[5]})')
    HRES[int(fn)] = (Nlin_all, Rk_all)

# ---------------- 2) Typ-I-Schranke analytisch ----------------
pr('\n=== 2) Typ-I-Rate der Falsifikationsregel (|z⁰| > c ∧ |z¹| > c, gleiches Vorzeichen), exakte Superposition ===')
for nu in (37, np.inf):
    c = tdist.ppf(1 - 0.05 / 294, nu) if np.isfinite(nu) else norm.ppf(1 - 0.05 / 294)
    for label, rho in (('weiß (Var_A : Var_B = 1 : 3)', 0.25), ('Modulstreuung (1 : 1)', 0.5), ('Grenzfall', 0.8)):
        p2 = multivariate_normal(mean=[0, 0], cov=[[1, rho], [rho, 1]]).cdf([-c, -c])
        pr(f'ν = {nu}, c = {c:.3f}, {label}: ρ(z⁰,z¹) = {rho}: je Test 2·P(Z⁰<−c, Z¹<−c) = {2*p2:.2e}; '
           f'Bonferroni-Schranke über 147 Tests: {147*2*p2:.2e}; ohne z¹ (nur z⁰): {147*2*norm.sf(c):.4f}')

# ---------------- 3) P(falsifiziert) auf L0 ----------------
pr('\n=== 3) P(falsifiziert), P(bestätigt) auf Stufe L0 (Monte Carlo, Fehler normal, Tests unabhängig, ν = 37) ===')
KMAX = 9
kk = np.arange(1, KMAX + 1)
nmod = MU * M / 3 * accel(np.arange(16000) / 16000 * T)
cmod = 2 * np.fft.rfft(nmod)[1:KMAX + 1] / 16000
E = np.exp(-1j * PHI[:, :, None] * kk)
NKc = (cmod * E).sum(1)
NTH = 4000
th = 2 * np.pi * np.arange(NTH) / NTH
curves = (NKc[:, :, None] * np.exp(1j * kk[None, :, None] * th[None, None, :])).real.sum(1)
thmin = th[curves.argmin(1)]
FminN = curves.min(1)
d = np.array([[(cmod * E[i, j] * np.exp(1j * kk * thmin[i])).real.sum() for j in range(3)] for i in range(21)])
g = np.array([[(cmod * E[i, j] * (-1j * kk) * np.exp(1j * kk * thmin[i])).real.sum() for j in range(3)] for i in range(21)])
sh, sp = 0.11e-3, np.radians(0.02)


def var_parts(nB):
    """Var_A (Messseite) und Var_B (Vorhersage) je Test (21 × 7) für Stufe L0."""
    vA = np.empty((21, 7)); vB = np.empty((21, 7))
    vA[:, 0] = (KMAX * sh ** 2 + sp ** 2 * (g ** 2).sum(1)) / 20
    vB[:, 0] = (3 * KMAX * sh ** 2 + sp ** 2 * (g ** 2).sum(1)) / nB
    for qq in range(3):
        a_ = cmod[qq] * E[:, :, qq]
        p_ = -1j * (qq + 1) * a_
        for part, col in ((np.real, 1 + 2 * qq), (np.imag, 2 + 2 * qq)):
            vA[:, col] = (sh ** 2 + sp ** 2 * (part(p_) ** 2).sum(1)) / 20
            vB[:, col] = (3 * sh ** 2 + sp ** 2 * (part(p_) ** 2).sum(1)) / nB
    return vA, vB


vA, vB0 = var_parts(20)
_, vB1 = var_parts(21)
u0, u1 = np.sqrt(vA + vB0), np.sqrt(vA + vB1)
c37 = tdist.ppf(1 - 0.05 / 294, 37)
DELTA = np.array([0.1293, 0.1126, 0.1126, 0.0731, 0.0731, 0.1383, 0.1383])
pr(f'L0: u_F je Punkt [mN]: Median {1e3*np.median(u0[:,0]):.3f}, Spanne {1e3*u0[:,0].min():.3f}–{1e3*u0[:,0].max():.3f}; c = {c37:.3f}')
# Residuen der Szenarien (21 × 7)
scen = {}
Nlin, Rk = HRES[300]
predc = bandcurve(Nlin, 9)
measc = bandcurve(Nlin + Rk, 9)
rH = np.zeros((21, 7))
rH[:, 0] = measc.min(1) - predc.min(1)
for qq in range(3):
    rH[:, 1 + 2 * qq] = Rk[:, qq + 1].real
    rH[:, 2 + 2 * qq] = Rk[:, qq + 1].imag
scen['Hertz 300 Hz (k ≤ 9)'] = rH
for x in (0.001, 0.003, 0.01):
    r = np.zeros((21, 7))
    r[:, 0] = -x * FminN
    for qq in range(3):
        r[:, 1 + 2 * qq] = -x * NKc[:, qq].real
        r[:, 2 + 2 * qq] = -x * NKc[:, qq].imag
    scen[f'Kopplung {100*x:.1f} %'] = r
scen['exakt'] = np.zeros((21, 7))
rng = np.random.default_rng(3)
RR = 20000
for name, r in scen.items():
    zmax = np.abs(r / u0).max()
    ia = np.unravel_index(np.argmax(np.abs(r / u0)), r.shape)
    fals = np.zeros(RR, bool); conf = np.zeros(RR, bool)
    for c0 in range(0, RR, 2000):
        nb = min(2000, RR - c0)
        eA = rng.standard_normal((nb, 21, 7)) * np.sqrt(vA)
        r0 = r + eA - rng.standard_normal((nb, 21, 7)) * np.sqrt(vB0)
        r1 = r + eA - rng.standard_normal((nb, 21, 7)) * np.sqrt(vB1)
        # geschätzte u (χ²_37) – vereinfachend gemeinsamer Faktor je Test
        s0 = np.sqrt(rng.chisquare(37, (nb, 21, 7)) / 37)
        z0, z1 = r0 / (u0 * s0), r1 / (u1 * s0)
        sig0, sig1 = np.abs(z0) > c37, np.abs(z1) > c37
        fals[c0:c0 + nb] = (sig0 & sig1 & (np.sign(z0) == np.sign(z1))).any((1, 2))
        pb1 = (np.abs(r0) + c37 * u0 * s0 <= DELTA).all((1, 2))
        conf[c0:c0 + nb] = ~sig0.any((1, 2)) & ~sig1.any((1, 2)) & pb1
    pr(f'{name:22s}: max|r| F = {1e3*np.abs(r[:,0]).max():.3f} mN; größtes |r|/u = {zmax:.2f} (Test {ia}); '
       f'P(falsifiziert) = {fals.mean():.3f}, P(bestätigt) = {conf.mean():.3f}, '
       f'max|r|/Δ = {np.max(np.abs(r)/DELTA):.4f}')
txt = '\n'.join(out)
print(txt)
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v5_hertz_stoerung_oc_ausgabe.txt'), 'w').write(txt + '\n')
