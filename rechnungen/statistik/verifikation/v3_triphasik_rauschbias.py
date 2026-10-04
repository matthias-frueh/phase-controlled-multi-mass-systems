"""v3_triphasik_rauschbias.py – Gegenprüfung STA-04 (Rauschbias-Bedingung |b| ≤ 0,1·u_c,erw am Triphasik-Punkt).

Eigener Rechenweg:
 1) Analytisch über Ordnungsstatistiken: Am Triphasik-Punkt (identische Module, k_max = 9) hat die Kurve drei
    gleich tiefe Minima θ_m (Abstand T/3). In erster Ordnung ist F_min = min_m (F* + e_m), e_m = Rauschen der
    Kurve an θ_m. b = E[min_m e_m^Mess] − E[min_m e_m^Vorh]. Kovarianz der e_m je Rauschmodell exakt aus den
    Harmonischen; E[min] dreier (korrelierter) Normalgrößen per Quadratur bzw. 10⁶ Ziehungen.
    Zwei Lesarten von u_c,erw: (i) Präreg §4: u_c,erw² = s_q²/n_min + u²(ŷ), s_q aus Pilotläufen (Einzelminimum,
    also sd eines e_m); (ii) Gruppe (s1b): sd des Minimums aus drei.
 2) Rauschmodelle: 'weiss' (gleiches σ_h in Einzel- und Kombinationsläufen), 'modul' (Amplitude je Modul),
    'phase_beide' (nicht erfasster Phasenversatz je Modul in Kombinations- UND Einzelläufen, physikalisch
    konsistent), 'phase_nur_komb' (Modell der Gruppe: nur Kombinationsläufe, Vorhersage rauschfrei),
    'jitter_rho' (erfasster Jitter: Vorhersage mit gemessenen Zeigern, §8.2/A9.5).
 3) Monte-Carlo-Gegenprobe auf Ebene der Harmonischen (eigene Implementierung), n = 20, n₀ = 20/40/60.
 4) Wie groß muss ein realer Modulunterschied sein, damit der Effekt verschwindet?
"""
import os
import numpy as np

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


KMAX, NF, NTH = 9, 16000, 6000
k = np.arange(1, KMAX + 1)
cmod = 2 * np.fft.rfft(MU * M / 3 * accel(np.arange(NF) / NF * T))[1:KMAX + 1] / NF
th = 2 * np.pi * np.arange(NTH) / NTH
EXP = np.exp(1j * np.outer(k, th))                          # K × NTH


def curve(Nk):
    return (Nk[..., :, None] * EXP).real.sum(-2)


phis = np.radians([0.0, 120.0, 240.0])
Em = np.exp(-1j * np.outer(phis, k))                        # 3 × K
Ntrue = (cmod * Em).sum(0)
cv = curve(Ntrue)
# drei Minima
loc = np.where((cv < np.roll(cv, 1)) & (cv <= np.roll(cv, -1)))[0]   # lokale Minima (periodisch)
mins = np.sort(loc[np.argsort(cv[loc])[:3]])
thm = th[mins]
out = []
pr = out.append
pr(f'Minima bei θ = {np.degrees(thm).round(2)} °, Werte {cv[mins].round(6)} N (gleich tief)')

# Linearformen des Kurvenrauschens an den Minima
def lin_white(theta):            # Kurvenwert = Σ_k Re(w_k e^{ikθ}) → Koeffizienten für Re w_k, Im w_k
    return np.concatenate([np.cos(k * theta), -np.sin(k * theta)])


Wm = np.stack([lin_white(t_) for t_ in thm])                # 3 × 2K
C_white = Wm @ Wm.T                                         # Kovarianz je Lauf bei σ_h = 1
d = np.array([[(cmod * Em[j] * np.exp(1j * k * t_)).real.sum() for j in range(3)] for t_ in thm])    # 3(m) × 3(j)
g = np.array([[(cmod * Em[j] * (-1j * k) * np.exp(1j * k * t_)).real.sum() for j in range(3)] for t_ in thm])
pr(f'Korrelation des weißen Rauschens zwischen den Minima: {(C_white[0,1]/C_white[0,0]):.4f}')
pr(f'Modulbeiträge d_mj [N] =\n{d.round(4)}\nPhasensensitivität g_mj [N/rad] =\n{g.round(3)}')

rng = np.random.default_rng(5)
Z = rng.standard_normal((2_000_000, 3))


def emin(C):
    lam, V = np.linalg.eigh(C)                       # auch für singuläre Kovarianz (Phase: Σ_j g_mj = 0)
    L_ = V * np.sqrt(np.clip(lam, 0, None))
    x = Z @ L_.T
    mn = x.min(1)
    return mn.mean(), mn.std()


pr('\n1) Analytisch (erste Ordnung), n = 20; Quotient |b|/u_c,erw in Lesart (i) Präreg / (ii) Gruppe')
n = 20
for model in ('weiss', 'modul', 'phase_beide', 'phase_nur_komb', 'jitter_rho'):
    for n0 in (20, 40, 60):
        if model == 'weiss':
            Cm, Cp = C_white / n, 3 * C_white / n0                       # Vorhersage: 3 Module, Punkte T/3 versetzt
            # Vorhersage-Kovarianz exakt: Σ_j Kovarianz von e_j an (θ_m − φ_j)
            Lp = np.stack([np.stack([lin_white(t_ - phis[j]) for t_ in thm]) for j in range(3)])  # j × m × 2K
            Cp = sum(Lp[j] @ Lp[j].T for j in range(3)) / n0
        elif model == 'modul':
            Cm, Cp = d @ d.T / n, d @ d.T / n0
        elif model == 'phase_beide':
            Cm, Cp = g @ g.T / n, g @ g.T / n0
        elif model == 'phase_nur_komb':
            gg = g[:, 1:]                                                  # Modul 1 definiert θ (wie Gruppe)
            Cm, Cp = gg @ gg.T / n, np.zeros((3, 3))
        else:                                                              # Jitter erfasst: Vorhersage folgt exakt
            Cm = Cp = np.zeros((3, 3))
        em_m, sd_m = emin(Cm) if Cm.any() else (0.0, 0.0)
        em_p, sd_p = emin(Cp) if Cp.any() else (0.0, 0.0)
        b = em_m - em_p
        u_i = np.sqrt(Cm[0, 0] + Cp[0, 0])                    # Einzelminimum (Präreg-Lesart, Pilot-s_q)
        u_ii = np.sqrt(sd_m ** 2 + sd_p ** 2)                 # sd des Minimums aus drei (Gruppe)
        q_i = abs(b) / u_i if u_i > 0 else np.nan
        q_ii = abs(b) / u_ii if u_ii > 0 else np.nan
        pr(f'  {model:15s} n₀={n0}: b/σ-Einheit = {b:+.4f}; |b|/u (i) = {q_i:.3f}, (ii) = {q_ii:.3f} '
           f'→ {"VERLETZT" if q_i > 0.1 else "ok"} (i), {"VERLETZT" if q_ii > 0.1 else "ok"} (ii)')

# 3) MC-Gegenprobe auf Ebene der Harmonischen (unabhängig von 1)
pr('\n3) Monte Carlo (Harmonische, R = 20 000 Kampagnen), n = 20; σ so, dass sd eines Minimums je Lauf ≈ 1 mN')
R = 20000


SEL = np.concatenate([np.arange(mm - 135, mm + 135) % NTH for mm in mins])
EXPS = EXP[:, SEL]


def fmin_batch(Nk):
    # Minimum auf feinem Raster nahe den drei Minima (±8°), in Blöcken (Speicher)
    out_ = np.empty(Nk.shape[0])
    for c0 in range(0, Nk.shape[0], 1000):
        blk = Nk[c0:c0 + 1000]
        out_[c0:c0 + 1000] = (blk.real @ EXPS.real - blk.imag @ EXPS.imag).min(1)
    return out_


for model, s in (('weiss', 1e-3 / 3), ('modul', None), ('phase_beide', None), ('phase_nur_komb', None)):
    for n0 in (20, 60):
        if model == 'modul':
            s = 1e-3 / np.sqrt((d[0] ** 2).sum())
        if model.startswith('phase'):
            s = 1e-3 / np.sqrt((g[0] ** 2).sum())
        def comb(nr):
            if model == 'weiss':
                return Ntrue + s * (rng.standard_normal((R, KMAX)) + 1j * rng.standard_normal((R, KMAX))) / np.sqrt(nr)
            if model == 'modul':
                eps = rng.standard_normal((R, 3, 1)) * s / np.sqrt(nr)
                return (cmod * Em * (1 + eps)).sum(1)
            dl = rng.standard_normal((R, 3, 1)) * s / np.sqrt(nr)
            if model == 'phase_nur_komb':
                dl[:, 0] = 0
            return (cmod * Em * np.exp(-1j * k * dl)).sum(1)
        def pred(nr):
            if model == 'weiss':
                return sum((cmod + s * (rng.standard_normal((R, KMAX)) + 1j * rng.standard_normal((R, KMAX))) / np.sqrt(nr)) * Em[j]
                           for j in range(3))
            if model == 'modul':
                eps = rng.standard_normal((R, 3, 1)) * s / np.sqrt(nr)
                return (cmod * Em * (1 + eps)).sum(1)
            if model == 'phase_nur_komb':
                return np.repeat(Ntrue[None], R, 0)
            dl = rng.standard_normal((R, 3, 1)) * s / np.sqrt(nr)
            return (cmod * Em * np.exp(-1j * k * dl)).sum(1)
        fm, fp = fmin_batch(comb(n)), fmin_batch(pred(n0))
        ftrue = cv.min()
        b = fm.mean() - fp.mean()
        # Lesart (i): sd eines Einzelminimums je Seite (aus derselben Simulation: Kurvenwert am festen θ_m0)
        e_m = (comb(n) * np.exp(1j * k * thm[0])).real.sum(1)
        e_p = (pred(n0) * np.exp(1j * k * thm[0])).real.sum(1)
        u_i = np.sqrt(e_m.var() + e_p.var())
        u_ii = np.sqrt(fm.var() + fp.var())
        pr(f'  {model:15s} n₀={n0}: Bias Mess {1e3*(fm.mean()-ftrue):+.4f} mN, Vorh {1e3*(fp.mean()-ftrue):+.4f} mN, '
           f'b = {1e3*b:+.4f} mN; |b|/u (i) = {abs(b)/u_i:.3f}, (ii) = {abs(b)/u_ii:.3f}')

# 4) Realer Modulunterschied: Abstand der beiden tiefsten Minima bei 120°
pr('\n4) Modulunterschied (Amplitude von Modul 2, 3 um ±δ): Abstand zwischen tiefstem und zweittiefstem Minimum bei 120°')
for dlt in (1e-4, 1e-3, 1e-2):
    Nk = cmod * Em[0] + cmod * (1 + dlt) * Em[1] + cmod * (1 - dlt) * Em[2]
    c2 = curve(Nk)
    vals = np.sort([c2[(np.arange(mm - 135, mm + 135)) % NTH].min() for mm in mins])
    pr(f'  δ = {100*dlt:.2f} %: Minima {1e3*(vals - vals[0]).round(3)} mN über dem tiefsten')
# Abstand auf dem 2°-Raster: Gitterpunkt nächst der verschobenen Zeltspitze (Sekante 0,0343 N/° je Flanke)
pr('  Auf dem 2°-Raster liegt die Spitze bei ungleichen Modulen i. A. zwischen zwei Punkten; am nächsten Punkt beträgt '
   'der Abstand der beiden konkurrierenden Minima ≈ (s_L + s_R)·|Δφ| = 0,069 N/°·|Δφ|, für |Δφ| gleichverteilt in [0, 1°]: '
   f'P(Abstand < 2·0,3 mN) ≈ {0.6e-3/0.0686:.3f}')
txt = '\n'.join(out)
print(txt)
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v3_triphasik_rauschbias_ausgabe.txt'), 'w').write(txt + '\n')
