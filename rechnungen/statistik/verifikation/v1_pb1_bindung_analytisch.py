"""v1_pb1_bindung_analytisch.py – Gegenprüfung STA-01 / STA-03 (Prüfgruppe statistik, P2).

Unabhängig von den Skripten der Gruppe geschrieben (eigene Kurvenberechnung im Zeitbereich, analytische
Fehlerfortpflanzung und numerische Quadratur statt Monte Carlo / Bootstrap).

A) Δ_q = 0,25·D_q im A4-Beispiel (starr, μ = 0,4, 10 Hz), volles Spektrum und k_max = 9, eigene Implementierung:
   Modulkurve n(t) = (μM/3)·a(t − τ_j), a(t) = Egg-Profilbeschleunigung (Formel aus finesweep.py, hier neu
   geschrieben), τ_j = φ_j/(2πf) (Modul verzögert), Summe im Zeitbereich auf 16 000 Punkten je Periode.
B) P(PB1 ∧ kein |z| > c | exakte Superposition) je Test analytisch:
   ν → ∞: p₁ = 2Φ(R − c) − 1 (R = Δ/u ≥ c, sonst 0) ; ν endlich: Quadratur über S² ~ χ²_ν/ν mit
   p₁ = E_S[2Φ(min(R − cS, cS)) − 1]⁺.  P = p₁^m; gesucht R mit P = 0,8 (m = 1, 21, 147).
C) Analytische u_q aller 7 Größen an allen 21 Punkten (lineare Fortpflanzung, Hüllkurvensatz für F_min)
   für das Rauschmodell der Gruppe (s2: weißes Rest-σ_h je Re/Im N_k und Lauf; Modulamplitude σ_a; nicht
   erfasster Modulphasenversatz σ_p; Kombinationslauf trägt drei Module, Einzellauf eines) – Vergleich mit
   den Bootstrap-Medianen der Gruppe und Frage, WELCHE Größe PB1 bindet.
D) Analytische Operating Characteristic „bestätigt | exakt“ je Rauschstufe (unabhängige Tests, ν = 37).
"""
import os
import numpy as np
from scipy.stats import norm, t as tdist, chi2
from scipy import integrate, optimize

# ---------------- Parameter (Engine) ----------------
M, G = 0.650, 9.81
MG = M * G
F_HZ = 10.0
T = 1.0 / F_HZ
RTOP, THOLD = 0.005, 0.65
TFAST = 1.0 - THOLD
RBOT = RTOP * TFAST / THOLD
MU = 0.4
A_HOLD = -RTOP * (np.pi / (THOLD * T)) ** 2
A_FAST = RBOT * (np.pi / (TFAST * T)) ** 2


def accel(t):
    p = np.mod(t, T) / T
    return np.where(p < THOLD, A_HOLD * np.sin(np.pi * p / THOLD), A_FAST * np.sin(np.pi * (p - THOLD) / TFAST))


NF = 16000                       # feines Zeitraster je Periode
tt = np.arange(NF) * T / NF
PHI2 = np.arange(100, 140.1, 2.0)
PHI = np.stack([np.zeros(21), PHI2, np.full(21, 240.0)], 1)          # Grad


def config_curve(phis_deg, kmax=None, nout=2000):
    """N(θ) − ⟨N⟩ einer Konfiguration, Zeitbereich; kmax: Bandbegrenzung (FFT-Abschneiden)."""
    tau = np.radians(np.asarray(phis_deg)) / (2 * np.pi * F_HZ)
    n = sum(MU * M / 3 * accel(tt - tj) for tj in tau)
    X = np.fft.rfft(n)
    X[0] = 0
    if kmax is not None:
        X[kmax + 1:] = 0
    x = np.fft.irfft(X, NF)
    return x[:: NF // nout], 2 * X[1:4] / NF            # Kurve (nout Punkte), N_1..N_3 (Konvention 2/N Σ x e^{−ikθ})


out = []
pr = out.append
pr('=== A) Δ_q im A4-Beispiel (eigene Zeitbereichsrechnung) ===')
for kmax in (None, 9):
    Fm, Nk = [], []
    for i in range(21):
        c, nk = config_curve(PHI[i], kmax)
        Fm.append(c.min())
        Nk.append(nk)
    Fm, Nk = np.array(Fm), np.array(Nk)
    D = [Fm.max() - Fm.min()] + [np.abs(Nk[:, j]).max() for j in range(3)]
    pr(f'k_max = {kmax}: ΔF_Zelt = {D[0]:.4f} N → Δ(F_min) = {0.25*D[0]:.4f} N; max|N1|,|N2|,|N3| = '
       f'{D[1]:.4f}, {D[2]:.4f}, {D[3]:.4f} N → Δ = {0.25*D[1]:.4f}, {0.25*D[2]:.4f}, {0.25*D[3]:.4f} N; '
       f'F_min(120°) − ⟨N⟩ = {Fm[10]:.4f} N, F_min(100°) − ⟨N⟩ = {Fm[0]:.4f} N')
    if kmax == 9:
        DELTA9 = np.array([0.25 * D[0]] + [0.25 * D[1]] * 2 + [0.25 * D[2]] * 2 + [0.25 * D[3]] * 2)
for nu in (np.inf, 19):
    c = norm.ppf(1 - 0.05 / 294) if np.isinf(nu) else tdist.ppf(1 - 0.05 / 294, nu)
    pr(f'   ν = {nu}: c = {c:.3f}; notwendige Grenze Δ/c = {0.11733 / c * 1e3:.1f} mN (volles Spektrum)')

# ---------------- B) analytische Bestätigungswahrscheinlichkeit ----------------
pr('\n=== B) P(PB1 ∧ kein |z| > c | exakt) je Test analytisch (ν = ∞ geschlossen, ν endlich Quadratur) ===')


def p1_test(R, nu, c):
    if np.isinf(nu):
        return max(0.0, 2 * norm.cdf(min(R - c, c)) - 1)
    f = lambda s: (max(0.0, 2 * norm.cdf(min(R - c * s, c * s)) - 1) * 2 * s * nu * chi2.pdf(nu * s * s, nu))
    return integrate.quad(f, 0, 4, limit=400, points=[R / (2 * c), R / c])[0]


for nu in (np.inf, 19, 37):
    c = norm.ppf(1 - 0.05 / 294) if np.isinf(nu) else tdist.ppf(1 - 0.05 / 294, nu)
    line = f'ν = {nu}: c = {c:.3f}; P(PB1) je Test bei R = c: {p1_test(c, nu, c):.4f} (147 Tests: {p1_test(c, nu, c)**147:.2e})'
    for m in (1, 21, 147):
        Rm = optimize.brentq(lambda R: p1_test(R, nu, c) ** m - 0.8, c * 0.6, 4 * c)
        line += f'; m = {m}: R(0,8) = {Rm:.3f} → u ≤ {117.33 / Rm:.1f} mN'
    pr(line)
pr('   geschlossen ν = ∞, m = 147: R = c + Φ⁻¹((1 + 0,8^(1/147))/2) = '
   f'{norm.ppf(1 - 0.05/294) + norm.ppf((1 + 0.8 ** (1 / 147)) / 2):.3f}')

# ---------------- C) analytische u_q (Rauschmodell wie s2) ----------------
KMAX = 9
kk = np.arange(1, KMAX + 1)
nmod = MU * M / 3 * accel(tt)
cmod = 2 * np.fft.rfft(nmod)[1:KMAX + 1] / NF        # Modulharmonische c_k (eigener Index)
NTH = 2000
th = 2 * np.pi * np.arange(NTH) / NTH
E = np.exp(-1j * np.radians(PHI)[:, :, None] * kk)    # 21 × 3 × K
NKc = (cmod * E).sum(1)                               # 21 × K
curves = (NKc[:, :, None] * np.exp(1j * kk[None, :, None] * th[None, None, :])).real.sum(1)
imin = curves.argmin(1)
thmin = th[imin]
# Sensitivitäten je Modul j am Minimum: Amplitude d_j, Phase g_j (je rad)
d = np.empty((21, 3)); g = np.empty((21, 3))
for i in range(21):
    ph = np.exp(1j * kk * thmin[i])
    for j in range(3):
        d[i, j] = (cmod * E[i, j] * ph).real.sum()
        g[i, j] = (cmod * E[i, j] * (-1j * kk) * ph).real.sum()
# Harmonische: Re/Im von c_k e^{−ikφ_j} (Amplitude) und von −ik c_k e^{−ikφ_j} (Phase), k = 1..3
LEVELS = {0: ('L0 Sensor+Jitter', 0.11e-3, 0.0, 0.02), 1: ('L1 0,3 %/0,03°', 0.11e-3, 0.003, 0.03),
          2: ('L2 1 %/0,1°', 0.11e-3, 0.01, 0.10), 3: ('L3 3 %/0,3°', 0.11e-3, 0.03, 0.30),
          4: ('L4 6 %/0,6°', 0.11e-3, 0.06, 0.60), 5: ('L5 10 %/1°', 0.11e-3, 0.10, 1.00)}
GRUPPE = {0: (0.26, 0.176, 0.121, 0.084), 1: (0.99, 1.47, 0.51, 0.23), 2: (3.30, 4.94, 1.70, 0.77),
          3: (9.86, 14.7, 5.07, 2.29), 4: (19.6, 29.5, 10.1, 4.56), 5: (32.5, 48.9, 16.8, 7.64)}
n, n0, n1 = 20, 20, 21


def u_all(sh, sa, sp_deg, nB):
    sp = np.radians(sp_deg)
    U = np.empty((21, 7))
    vF_run = KMAX * sh ** 2 + sa ** 2 * (d ** 2).sum(1) + sp ** 2 * (g ** 2).sum(1)
    vF_pred = 3 * KMAX * sh ** 2 + sa ** 2 * (d ** 2).sum(1) + sp ** 2 * (g ** 2).sum(1)
    U[:, 0] = np.sqrt(vF_run / n + vF_pred / nB)
    for q in range(3):
        a_ = cmod[q] * E[:, :, q]                       # 21 × 3
        p_ = -1j * (q + 1) * a_
        for part, col in ((np.real, 1 + 2 * q), (np.imag, 2 + 2 * q)):
            vr = sh ** 2 + sa ** 2 * (part(a_) ** 2).sum(1) + sp ** 2 * (part(p_) ** 2).sum(1)
            vp = 3 * sh ** 2 + sa ** 2 * (part(a_) ** 2).sum(1) + sp ** 2 * (part(p_) ** 2).sum(1)
            U[:, col] = np.sqrt(vr / n + vp / nB)
    return U


pr('\n=== C) analytische u_q (Median über Punkte; in Klammern Bootstrap-Median der Gruppe, s2) und Δ_q/u_q ===')
pr('Δ_q (k_max = 9) [mN]: F ' + ', '.join(f'{1e3*x:.1f}' for x in DELTA9[[0, 1, 3, 5]]) + ' (F, N1, N2, N3)')
c37 = tdist.ppf(1 - 0.05 / 294, 37)
names = ['F', 'ReN1', 'ImN1', 'ReN2', 'ImN2', 'ReN3', 'ImN3']
OC = {}
for L, (lab, sh, sa, sp) in LEVELS.items():
    U = u_all(sh, sa, sp, n0)
    U1 = u_all(sh, sa, sp, n1)
    med = [np.median(U[:, 0]), np.median(U[:, 1:3]), np.median(U[:, 3:5]), np.median(U[:, 5:7])]
    R = DELTA9[None, :] / U                                      # 21 × 7
    Rmin_q = [R[:, 0].min(), R[:, 1:3].min(), R[:, 3:5].min(), R[:, 5:7].min()]
    bind = ['F_min', 'N1', 'N2', 'N3'][int(np.argmin(Rmin_q))]
    # D) OC: Produkt über 147 Tests (unabhängig), ν = 37; z¹-Nichtablehnung je Test (1 − α/147)
    p = np.prod([p1_test(r, 37, c37) for r in R.ravel()])
    p_nr1 = (1 - 0.05 / 147) ** 147
    OC[L] = p * p_nr1
    pr(f'{lab:18s} u [mN]: F {1e3*med[0]:6.2f} ({GRUPPE[L][0]}), N1 {1e3*med[1]:6.2f} ({GRUPPE[L][1]}), '
       f'N2 {1e3*med[2]:6.2f} ({GRUPPE[L][2]}), N3 {1e3*med[3]:6.2f} ({GRUPPE[L][3]}) | min Δ/u: F {Rmin_q[0]:6.1f}, '
       f'N1 {Rmin_q[1]:6.1f}, N2 {Rmin_q[2]:6.1f}, N3 {Rmin_q[3]:6.1f} → bindend: {bind} | '
       f'P(bestätigt|exakt) analytisch ≈ {OC[L]:.3f}')

# Welche Modulamplitudenstreuung (σ_p = σ_a·10°/1 %-Verhältnis wie s2, d. h. σ_p[°] = 10·σ_a) macht PB1 bindend?
pr('\nσ_a (σ_p = 10°·σ_a), bei dem P(bestätigt|exakt) = 0,8 (analytisch, ν = 37), und bindende Größe dort:')


def oc_sa(sa):
    U = u_all(0.11e-3, sa, 10 * sa, n0)
    R = DELTA9[None, :] / U
    return np.prod([p1_test(r, 37, c37) for r in R.ravel()]) * (1 - 0.05 / 147) ** 147, R


sa80 = optimize.brentq(lambda s: oc_sa(s)[0] - 0.8, 0.005, 0.08)
_, R80 = oc_sa(sa80)
U80 = u_all(0.11e-3, sa80, 10 * sa80, n0)
pr(f'   σ_a = {100*sa80:.2f} % (σ_p = {10*sa80:.2f}°): u_F (Median) = {1e3*np.median(U80[:, 0]):.1f} mN, '
   f'u_N1 = {1e3*np.median(U80[:, 1:3]):.1f} mN; min Δ/u: F {R80[:, 0].min():.2f}, N1 {R80[:, 1:3].min():.2f}, '
   f'N2 {R80[:, 3:5].min():.2f}, N3 {R80[:, 5:7].min():.2f}')
# nur F_min betrachtet (wie STA-01-Lesart „u_c(F_min) ≤ 14–17 mN“):
pF = lambda s: np.prod([p1_test(r, 37, c37) for r in (DELTA9[0] / u_all(0.11e-3, s, 10 * s, n0)[:, 0])])
saF = optimize.brentq(lambda s: pF(s) * (1 - 0.05 / 147) ** 147 - 0.8, 0.005, 0.2)
pr(f'   nur F_min (21 Tests) bindend: σ_a = {100*saF:.2f} % → u_F (Median) = '
   f'{1e3*np.median(u_all(0.11e-3, saF, 10*saF, n0)[:, 0]):.1f} mN')
# reines weißes Rauschen: welche Größe bindet?
U = u_all(1e-3, 0, 0, n0)
R = DELTA9[None, :] / U
pr(f'reines weißes Rauschen (σ_h = 1 mN): min Δ/u: F {R[:, 0].min():.1f}, N1 {R[:, 1:3].min():.1f}, '
   f'N2 {R[:, 3:5].min():.1f}, N3 {R[:, 5:7].min():.1f}; u_N2/u_F = {np.median(U[:, 3:5])/np.median(U[:, 0]):.2f}')
U = u_all(0, 0.01, 0, n0)
R = DELTA9[None, :] / U
pr(f'reine Modulamplitude (σ_a = 1 %): min Δ/u: F {R[:, 0].min():.1f}, N1 {R[:, 1:3].min():.1f}, '
   f'N2 {R[:, 3:5].min():.1f}, N3 {R[:, 5:7].min():.1f}')
U = u_all(0, 0, 0.1, n0)
R = DELTA9[None, :] / U
pr(f'reine Modulphase (σ_p = 0,1°): min Δ/u: F {R[:, 0].min():.1f}, N1 {R[:, 1:3].min():.1f}, '
   f'N2 {R[:, 3:5].min():.1f}, N3 {R[:, 5:7].min():.1f}')

# Sensorrauschen → σ_h
for sig, fs, Ta in ((0.02, 6400, 10), (0.005, 6400, 10), (0.001, 6400, 10)):
    sh = sig * np.sqrt(2 / (fs * Ta))
    pr(f'σ = {1e3*sig:.0f} mN, f_s = {fs} Hz, T_a = {Ta} s: σ_h = sd(Re N_k) = {1e3*sh:.4f} mN; '
       f'sd(F_min − ⟨N⟩) je Lauf = √k_max·σ_h = {1e3*np.sqrt(KMAX)*sh:.3f} mN')
txt = '\n'.join(out)
print(txt)
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v1_pb1_bindung_analytisch_ausgabe.txt'), 'w').write(txt + '\n')
