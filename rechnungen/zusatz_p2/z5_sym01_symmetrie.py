"""z5_sym01_symmetrie.py - Gegenpruefung SYM-01 (Aequivalenzgruppe S3, Phasenregel fuer arg N_k).

Eigene Rechnung:
 (a) Bahngroessen per Brute Force auf dem 1-Grad-Raster (360 x 360) unter den sechs Abbildungen.
 (b) Anregungsidentitaet a_gA(t) = a_A(t + tau_ref) an Zufallspunkten (eigene Profilfunktion).
 (c) Lineares 1-FG-Modell (eigene Formel N_k = mu M H(kw) c_k Phi_k / 3): Phasenregel und Triadenphase.
 (d) Nichtlinear: eigene vektorisierte RK4-Engine (gleiche Gleichung wie Referenz, neu geschrieben),
     zwei Liftoff-Punkte mit je sechs Bildern, aequivalenter Start (t0 = -tau_ref) und Standardstart.
"""
import time
import numpy as np
from scipy.stats import skew
import zm

MAPS = [('id', lambda a, b: (a, b), 'none'), ('(23)', lambda a, b: (b, a), 'none'),
        ('(12)', lambda a, b: (-a, b - a), 'p2'), ('(123)', lambda a, b: (b - a, -a), 'p2'),
        ('(13)', lambda a, b: (a - b, -b), 'p3'), ('(132)', lambda a, b: (-b, a - b), 'p3')]


def ref_phase(kind, a, b):
    return {'none': 0.0, 'p2': a, 'p3': b}[kind]


# (a) Bahngroessen
print('=== (a) Bahngroessen auf dem 1-Grad-Raster ===')
sizes = {}
special = {1: [], 2: [], 3: []}
for a in range(360):
    for b in range(360):
        orb = {tuple(int(x) % 360 for x in f(a, b)) for _, f, _ in MAPS}
        s = len(orb)
        sizes[s] = sizes.get(s, 0) + 1
        if s < 6:
            special[s].append((a, b))
print(' Anzahl Punkte je Bahngroesse:', dict(sorted(sizes.items())))
print(' Groesse 1:', special[1])
print(' Groesse 2:', special[2])
ok3 = all((a == 0 or b == 0 or a == b) and (a, b) != (0, 0) for a, b in special[3])
print(f' Groesse 3: {len(special[3])} Punkte, alle mit zwei gleichen Phasen (phi2=0, phi3=0 oder phi2=phi3): {ok3}')
print(f' erwartet 3*359 = {3*359}')
# Abgeschlossenheit: Komposition zweier Abbildungen ist wieder eine der sechs
rng = np.random.default_rng(1)
closed = True
for _ in range(50):
    a, b = rng.uniform(0, 360, 2)
    imgs = [tuple(np.mod(f(a, b), 360)) for _, f, _ in MAPS]
    for _, f, _ in MAPS:
        for (x, y) in imgs:
            z = np.mod(f(x, y), 360)
            if min(np.hypot(*(np.mod(z - np.array(im) + 180, 360) - 180)) for im in imgs) > 1e-9:
                closed = False
print(f' Abgeschlossenheit (50 Zufallspunkte, 36 Kompositionen): {closed}')

# (b) Anregungsidentitaet
print('\n=== (b) a_gA(t) gegen a_A(t + tau_ref) ===')
t = np.linspace(0, 0.3, 3001)
mx = 0.0
for _ in range(20):
    a, b = rng.uniform(0, 360, 2)
    abar = lambda p2, p3, tt: (zm.accel(tt) + zm.accel(tt - np.radians(p2) / zm.OMEGA) + zm.accel(tt - np.radians(p3) / zm.OMEGA)) / 3
    for name, f, kind in MAPS:
        a2, b2 = f(a, b)
        tr = np.radians(ref_phase(kind, a, b)) / zm.OMEGA
        mx = max(mx, np.abs(abar(a2, b2, t) - abar(a, b, t + tr)).max())
print(f' max Abweichung ueber 20 Punkte x 6 Bilder: {mx:.1e} m/s^2')

# (c) lineares Modell
print('\n=== (c) Lineares 1-FG-Modell (Referenz K, C, mu = 1): Phasenregel arg N_k(gA) = arg N_k(A) + k phi_ref ===')
ck = zm.ck_analytic(9)
k = np.arange(10)
w = zm.OMEGA * k
H = (zm.K_REF + 1j * w * zm.C_REF) / (zm.K_REF - zm.M * w ** 2 + 1j * w * zm.C_REF)


def Nk(p2, p3):
    Phi = 1 + np.exp(-1j * k * np.radians(p2)) + np.exp(-1j * k * np.radians(p3))
    return 2 * zm.M * H * ck * Phi / 3      # N_k = (2/T) int N e^{-ikwt} dt


a, b = 110.0, 234.0
NA = Nk(a, b)
print(f' Punkt (110, 234): |N_1..3| = {np.round(np.abs(NA[1:4]), 5)} N; Triadenphase arg(N1^2 N2*) = '
      f'{np.degrees(np.angle(NA[1]**2*np.conj(NA[2]))):.4f} deg')
for name, f, kind in MAPS:
    a2, b2 = f(a, b)
    NB = Nk(a2, b2)
    pr = ref_phase(kind, a, b)
    dev = np.degrees(np.angle(NB[1:] / NA[1:] * np.exp(-1j * k[1:] * np.radians(pr))))
    print(f'  {name:6s} -> ({np.mod(a2,360):6.1f}, {np.mod(b2,360):6.1f}): max|Phasenregel-Rest| = {np.abs(dev).max():.1e} deg, '
          f'max|d|N_k|| = {np.abs(np.abs(NB)-np.abs(NA)).max():.1e} N, Triade {np.degrees(np.angle(NB[1]**2*np.conj(NB[2]))):.4f} deg')

# (d) nichtlinear, eigene RK4-Engine
print('\n=== (d) Eigene RK4-Engine (dt = 50 us), 30 s, Fenster 20-30 s ===')
DT = 5e-5


def run(p2, p3, t0, T_sim=30.0, T_w0=20.0, kmax=3):
    p2, p3, t0 = map(np.asarray, (p2, p3, t0))
    tau2, tau3 = np.radians(p2) / zm.OMEGA, np.radians(p3) / zm.OMEGA
    n = p2.size
    z = np.full(n, -zm.MG / zm.K_REF)
    v = np.zeros(n)

    def f(z, v, t):
        Fs = -zm.K_REF * z - zm.C_REF * v
        Fc = np.where((z < 0) & (Fs > 0), Fs, 0.0)
        ab = (zm.accel(t) + zm.accel(t - tau2) + zm.accel(t - tau3)) / 3
        return v, -zm.G + Fc / zm.M - ab, Fc
    nst, nw = int(round(T_sim / DT)), int(round(T_w0 / DT))
    S1 = np.zeros(n); S2 = np.zeros(n); S3 = np.zeros(n); Fmin = np.full(n, np.inf); Fmax = np.full(n, -np.inf)
    lift = np.zeros(n); DFT = np.zeros((kmax, n), complex); cnt = 0
    for i in range(nst):
        t = t0 + i * DT
        k1z, k1v, Fc = f(z, v, t)
        k2z, k2v, _ = f(z + 0.5 * DT * k1z, v + 0.5 * DT * k1v, t + 0.5 * DT)
        k3z, k3v, _ = f(z + 0.5 * DT * k2z, v + 0.5 * DT * k2v, t + 0.5 * DT)
        k4z, k4v, _ = f(z + DT * k3z, v + DT * k3v, t + DT)
        if i >= nw:
            S1 += Fc; S2 += Fc ** 2; S3 += Fc ** 3; Fmin = np.minimum(Fmin, Fc); Fmax = np.maximum(Fmax, Fc)
            lift += Fc < 1e-9
            DFT += Fc[None, :] * np.exp(-1j * np.outer(np.arange(1, kmax + 1), zm.OMEGA * t))
            cnt += 1
        z = z + DT * (k1z + 2 * k2z + 2 * k3z + k4z) / 6
        v = v + DT * (k1v + 2 * k2v + 2 * k3v + k4v) / 6
    m = S1 / cnt
    var = S2 / cnt - m ** 2
    sk = (S3 / cnt - 3 * m * var - m ** 3) / var ** 1.5
    return dict(mean=m, skew=sk, Fmin=Fmin, Fmax=Fmax, lam=100 * lift / cnt, Nk=2 * DFT / cnt)


t1 = time.time()
base = [(157.3, 264.0), (198.2, 267.4)]
P2, P3, T0E, T0S, PR, LAB = [], [], [], [], [], []
for (a, b) in base:
    for name, f, kind in MAPS:
        a2, b2 = f(a, b)
        P2.append(np.mod(a2, 360)); P3.append(np.mod(b2, 360))
        pr = ref_phase(kind, a, b)
        PR.append(pr); LAB.append((a, b, name))
        T0E.append(-np.radians(pr) / zm.OMEGA)
P2 = np.array(P2); P3 = np.array(P3); PR = np.array(PR)
rE = run(np.r_[P2, P2], np.r_[P3, P3], np.r_[np.array(T0E), np.zeros(len(P2))])
print(f' Laufzeit {time.time()-t1:.0f} s')
nb = len(P2)
for mode, off in (('aequivalenter Start', 0), ('Standardstart', nb)):
    print(f' -- {mode}')
    for bi in range(len(base)):
        sl = slice(off + 6 * bi, off + 6 * bi + 6)
        i0 = off + 6 * bi
        pr = PR[6 * bi:6 * bi + 6]
        Nk_ = rE['Nk'][:, sl]
        phase_rest = np.degrees(np.angle(Nk_ / Nk_[:, [0]] * np.exp(-1j * np.outer(np.arange(1, 4), np.radians(pr)))))
        print(f'   Basis {base[bi]}: lambda {np.round(rE["lam"][sl], 3)} %')
        print(f'      max|d mean| {np.ptp(rE["mean"][sl]):.2e} N, max|d skew| {np.ptp(rE["skew"][sl]):.2e}, '
              f'max|d F_min| {np.ptp(rE["Fmin"][sl]):.2e} N, max|d F_max| {np.ptp(rE["Fmax"][sl]):.2e} N, '
              f'max|d|N_k|| {np.ptp(np.abs(Nk_), axis=1).max():.2e} N, max|Phasenregel-Rest| {np.abs(phase_rest).max():.2e} deg')
