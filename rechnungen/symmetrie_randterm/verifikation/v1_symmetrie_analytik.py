"""
v1_symmetrie_analytik.py - Gegenpruefung SYM-01/02/03 ohne Zeitintegration.
 A  Kennzeichnung von Konfigurationen ueber die zyklische Abstandsfolge (eigene Implementierung):
    Aequivalenzklasse = minimale Rotation der Abstandsfolge der sortierten Phasenmenge {0, phi2, phi3}.
    -> Brute force: wo ist (phi2+120, phi3+120) aequivalent zu (phi2, phi3)?  (0,25-Grad-Raster)
    -> |Phi_k| unter 120-Grad-Verschiebung
 B  Lineares Frequenzbereichsmodell im Kontaktast (eigene Implementierung, Fourierkoeffizienten des
    Egg-Profils per FFT der Lage q, N_k = M Abar_k (K + i k w C)/(K - M (k w)^2 + i k w C)):
    Spiegelpaare (phi) <-> (-phi) fuer C = 16, C = 0, starr; Zeltschnitt phi3 = 240 Grad.
"""
import numpy as np
import v_engine as ve

np.set_printoptions(linewidth=160)
M, G, MG, T = ve.M, ve.G, ve.MG, ve.T
W = 2 * np.pi / T


def klasse(p2, p3, dez=6):
    """kanonische Abstandsfolge (minimale Rotation) - Arrays in Grad"""
    p = np.stack([np.zeros_like(p2), np.mod(p2, 360), np.mod(p3, 360)], -1)
    p = np.sort(p, -1)
    g = np.stack([p[..., 1] - p[..., 0], p[..., 2] - p[..., 1], 360 - p[..., 2] + p[..., 0]], -1)
    g = np.round(g, dez)
    rots = [np.roll(g, r, axis=-1) for r in range(3)]
    # lexikographisch minimale Rotation
    best = rots[0]
    for r in rots[1:]:
        lt = (r[..., 0] < best[..., 0]) | ((r[..., 0] == best[..., 0]) & (r[..., 1] < best[..., 1])) | \
             ((r[..., 0] == best[..., 0]) & (r[..., 1] == best[..., 1]) & (r[..., 2] < best[..., 2]))
        best = np.where(lt[..., None], r, best)
    return best


print('=== A: 120-Grad-Verschiebung gegen Aequivalenz (Abstandsfolge bis auf Rotation) ===')
h = 0.25
g = np.arange(0, 360, h)
P2, P3 = np.meshgrid(g, g, indexing='ij')
k0 = klasse(P2, P3, 4)
k1 = klasse(P2 + 120, P3 + 120, 4)
eq = np.all(np.abs(k0 - k1) < 1e-6, -1)
idx = np.nonzero(eq)
print(f'Raster {h} Grad, {P2.size} Punkte: {eq.sum()} aequivalente Punkte:')
for a, b in zip(P2[idx], P3[idx]):
    print(f'   ({a:g}, {b:g})  Abstaende {klasse(np.array(a), np.array(b))}')
# Kontrolle Spiegelung: (phi) ~ (-phi) aequivalent nur fuer gleichschenklige Abstandsfolgen
km = klasse(-P2, -P3, 4)
eqm = np.all(np.abs(k0 - km) < 1e-6, -1)
print(f'Spiegelung (-phi2,-phi3) aequivalent auf {eqm.sum()} von {P2.size} Rasterpunkten (gleichschenklig/entartet)')

print('\n|Phi_k| = |1 + e^{-ik phi2} + e^{-ik phi3}| an (0,0) und (110,234) vor/nach +120 Grad:')
for (a, b) in [(0, 0), (110, 234)]:
    r = []
    for k in range(1, 7):
        f0 = abs(1 + np.exp(-1j * k * np.radians(a)) + np.exp(-1j * k * np.radians(b)))
        f1 = abs(1 + np.exp(-1j * k * np.radians(a + 120)) + np.exp(-1j * k * np.radians(b + 120)))
        r.append(f'k={k}: {f0:.4f}->{f1:.4f}')
    print(f'  ({a},{b}): ' + '; '.join(r))

print('\n=== B: lineares Modell im Kontaktast ===')
NS = 2 ** 18
ts = np.arange(NS) * T / NS
q = ve.prof(ts)[0]
Qk = np.fft.fft(q) / NS                 # q(t) = sum Qk e^{+i k w t}
KM = 600
kk = np.arange(1, KM + 1)
Ak = -(kk * W) ** 2 * Qk[1:KM + 1]       # Beschleunigung
# Kontrolle gegen FFT der Beschleunigung direkt
Ak2 = np.fft.fft(ve.prof(ts)[2])[1:KM + 1] / NS
print(f'Kontrolle A_k aus q vs. aus qdd: max abs. Abw. k<=20: {np.max(np.abs(Ak[:20] - Ak2[:20])):.2e} m/s^2 (|A_1| = {abs(Ak[0]):.4f}; A_10 = {abs(Ak[9]):.1e} verschwindet)')
# Profil-Zeitumkehrsymmetrie: Phasen der A_k bzgl. t0 = 0.325 T
t0 = 0.325 * T
ph = np.degrees(np.angle(Ak[:8] * np.exp(1j * kk[:8] * W * t0)))
print('arg A_k relativ zur Achse t0 = 0,325 T (k=1..8) [Grad]:', np.round(ph, 6))
NT = 20000
tg = np.arange(NT) * T / NT
E = np.exp(1j * np.outer(kk, W * tg))     # (KM, NT)


def welle(p2, p3, K=ve.K0, C=ve.C0, starr=False):
    Phi = (1 + np.exp(-1j * kk * np.radians(p2)) + np.exp(-1j * kk * np.radians(p3))) / 3.0
    Ab = Ak * Phi
    if starr:
        H = np.ones(KM, complex)
    else:
        w = kk * W
        H = (K + 1j * w * C) / (K - M * w ** 2 + 1j * w * C)
    Nk = M * H * Ab                           # zweiseitige Amplitude (k>0)
    N = MG + 2 * np.real(Nk @ E)
    return N, 2 * np.abs(Nk)                 # einseitige Amplituden |N_k|


def kenn(N):
    m = N.mean()
    s = N.std()
    gam = np.mean((N - m) ** 3) / s ** 3
    return m, gam, N.min(), N.max()


paare = [(110, 234), (100, 240)]
for (a, b) in paare:
    for lab, kw in [('Referenz K=1e4, C=16', {}), ('C = 0', {'C': 0.0}), ('starr', {'starr': True})]:
        N1, A1 = welle(a, b, **kw)
        N2, A2 = welle(-a, -b, **kw)
        m1, g1, mi1, ma1 = kenn(N1)
        m2, g2, mi2, ma2 = kenn(N2)
        print(f'({a},{b}) vs ({-a % 360},{-b % 360}) {lab:22s}: mean {m1:.6f}/{m2:.6f}  gamma1 {g1:+.4f}/{g2:+.4f}  '
              f'F_min {mi1:.4f}/{mi2:.4f}  F_max {ma1:.4f}/{ma2:.4f}  max d|N_k| {np.max(np.abs(A1 - A2)):.1e}')
# Validierung gegen eigene RK4-Engine (K1 aus v0-Rauchtest: gamma1 -0.18016, F_min 3.98960, F_max 8.57755)
N1, _ = welle(110, 234)
print('K1 lineares Modell: mean %.6f gamma1 %.5f F_min %.5f F_max %.5f  (eigene RK4: -0.18016 / 3.98960 / 8.57755)'
      % kenn(N1))
# 120-Grad-Bild im linearen Modell (nur Hinweis: verlaesst ggf. den Kontaktast)
N3, A3 = welle(230, 354)
_, A0 = welle(110, 234)
print('K1 -> (230,354) lineares Modell: F_min %.3f N (negativ = Kontaktast verlassen), |N_1| %.3f -> %.3f N'
      % (N3.min(), A0[0], A3[0]))

print('\nZeltschnitt phi3 = 240 Grad, F_min(phi2) im linearen Modell (C=16 / C=0 / starr)')
for lab, kw in [('C=16', {}), ('C=0', {'C': 0.0}), ('starr', {'starr': True})]:
    p2s = np.arange(100, 140.01, 0.5)
    fm = np.array([welle(p, 240, **kw)[0].min() for p in p2s])
    i120 = np.argmin(np.abs(p2s - 120)); i110 = np.argmin(np.abs(p2s - 110)); i130 = np.argmin(np.abs(p2s - 130))
    imax = np.argmax(fm)
    sl_l = (fm[i120] - fm[i110]) / 10; sl_r = (fm[i120] - fm[i130]) / 10
    asym = np.max(np.abs(fm[i120:][:41] - fm[:i120 + 1][::-1][:len(fm[i120:])]))
    print(f'  {lab:6s}: F_min(110/120/130) = {fm[i110]:.4f}/{fm[i120]:.4f}/{fm[i130]:.4f} N; Steigung links '
          f'{sl_l:.4f} N/Grad, rechts {sl_r:.4f} N/Grad; Maximum bei phi2 = {p2s[imax]:.1f}; '
          f'max|F_min(120+d)-F_min(120-d)| (d<=20) = {asym:.2e} N')
