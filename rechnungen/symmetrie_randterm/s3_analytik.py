"""s3_analytik.py - Teil A analytisch/halbanalytisch (keine RK4-Laeufe).

A  S3-Gruppe: Zeitverschiebungsidentitaet abar_g(A)(t) = abar_A(t + tau_ref), Abgeschlossenheit,
   Invarianz der zyklischen Abstandsfolge; Spiegelung kehrt die Folge um.
B  120-Grad-Verschiebung: wo ist sie zufaellig eine Aequivalenz (Brute Force 0,5-Grad-Raster),
   Phasenfaktoren |Phi_k| vor/nach der Verschiebung.
C  Zeitumkehrsymmetrie des Egg-Profils (Engine) und des Testprofils 'skew'; Triadenphase des Profils.
D  Lineares Modell (Kontaktast, exakte Harmonische): Spiegelung phi -> -phi fuer
   (a) Referenz K=1e4, C=16; (b) C=0; (c) starre Auflage (H=1), je Profil egg und skew.
   Regeln fuer arg N_k unter S3 und unter Spiegelung.
E  Zeltschnitt phi3=240: Spiegelung bildet (phi2,240) auf (240-phi2,240) ab -> Symmetrie der
   Zeltkurve um 120 Grad genau dann, wenn die Spiegelung gilt.
F  Datenpruefung: sweep_19x19.csv (Vertauschung, volle Gruppe) und finesweep_2deg_120_240.csv (C3).
Konventionen: Modul j laeuft mit q(t - tau_j), tau_j = phi_j/(360 f) [phi in Grad];
N_k = (2/T) int N(t) exp(-i k w t) dt, N(t) = Mg + sum_k |N_k| cos(k w t + arg N_k)."""
import os
import itertools
import numpy as np
import pandas as pd
import sr_engine as se

np.set_printoptions(linewidth=160)
W = 2 * np.pi * se.F_HZ
T = se.T_CYC
NFINE = 16000                       # Stuetzstellen je Periode fuer die Profil-FFT
KH = NFINE // 2


def abar(t, p2, p3, prof='egg'):
    acc = se.PROFILES[prof][0]
    return (acc(t) + acc(t - p2 / 360 * T) + acc(t - p3 / 360 * T)) / 3.0


def canon(g):
    g = tuple(np.round(g, 6))
    return min(g[i:] + g[:i] for i in range(3))


print('=== A  S3-Gruppe ===')
rng = np.random.default_rng(1)
tt = np.linspace(0, 3 * T, 30001)
worst = 0.0
for _ in range(20):
    a, b = rng.uniform(0, 360, 2)
    ref = canon(se.gaps(a, b))
    for name, p2, p3, pref in se.s3_images(a, b):
        d = np.max(np.abs(abar(tt, p2, p3) - abar(tt + pref / 360 * T, a, b)))
        worst = max(worst, d)
        assert canon(se.gaps(p2, p3)) == ref, (a, b, name)
print(f'max |abar_gA(t) - abar_A(t + tau_ref)| ueber 20 Zufallspunkte x 6 Elemente: {worst:.2e} m/s^2 '
      f'(Skala der Beschleunigung {abs(se._A_HOLD):.1f} m/s^2)')
print('Zyklische Abstandsfolge (bis auf Rotation) fuer alle 6 Bilder gleich: ja (assert)')
# Abgeschlossenheit
a, b = 37.0, 151.0
imgs = {(round(p2, 9), round(p3, 9)) for _, p2, p3, _ in se.s3_images(a, b)}
clos = set()
for p in imgs:
    for _, p2, p3, _ in se.s3_images(*p):
        clos.add((round(p2, 9), round(p3, 9)))
print(f'Abgeschlossenheit: Bilder von (37,151): {len(imgs)}, nach erneuter Anwendung: {len(clos)}')
g = se.gaps(a, b); gm = se.gaps(-a, -b)
print(f'Abstaende (37,151): {g}; Spiegelbild (-37,-151): {gm}  (umgekehrte Reihenfolge, gleiche Menge)')
# Bahngroessen
print('Bahngroessen: (0,0) ->', len({(round(p, 6), round(q, 6)) for _, p, q, _ in se.s3_images(0, 0)}),
      '; (120,240) ->', len({(round(p, 6), round(q, 6)) for _, p, q, _ in se.s3_images(120, 240)}),
      '; (0,100) ->', len({(round(p, 6), round(q, 6)) for _, p, q, _ in se.s3_images(0, 100)}),
      '; (40,200) ->', len({(round(p, 6), round(q, 6)) for _, p, q, _ in se.s3_images(40, 200)}))

print('\n=== B  120-Grad-Verschiebung ===')
step = 0.5
ph = np.arange(0, 360, step)
hits = []
for a in ph:
    for b in ph:
        g0 = se.gaps(a, b); g1 = se.gaps(a + 120, b + 120)
        if canon(g0) == canon(g1):
            hits.append((a, b, canon(g0)))
print(f'Raster {step} Grad: Punkte, an denen (phi2+120, phi3+120) zu (phi2, phi3) aequivalent ist: {len(hits)}')
for h in hits:
    el = [n for n, p2, p3, _ in se.s3_images(*h[:2])
          if abs(p2 - (h[0] + 120) % 360) < 1e-9 and abs(p3 - (h[1] + 120) % 360) < 1e-9]
    print(f'   ({h[0]:6.2f}, {h[1]:6.2f})  Abstaende (kanonisch) {h[2]}  -> realisiert durch S3-Element {el}')


def Phi(k, p2, p3):
    return 1 + np.exp(-1j * k * np.radians(p2)) + np.exp(-1j * k * np.radians(p3))


for (a, b) in [(0, 0), (110, 234), (157.3, 264.0), (40, 200)]:
    r = [abs(Phi(k, a + 120, b + 120)) / abs(Phi(k, a, b)) if abs(Phi(k, a, b)) > 1e-12 else np.nan
         for k in range(1, 10)]
    print(f'   |Phi_k(phi+120)|/|Phi_k(phi)| bei ({a},{b}), k=1..9: ' + ' '.join(f'{x:.3f}' for x in r))
print(f'   |Phi_1| (0,0) = {abs(Phi(1, 0, 0)):.4f}, (120,120) = {abs(Phi(1, 120, 120)):.4f} (= sqrt 3 = {3 ** .5:.4f})')

print('\n=== C  Zeitumkehrsymmetrie der Profile ===')
tf = np.arange(NFINE) * T / NFINE
for prof in ('egg', 'skew'):
    acc = se.PROFILES[prof][0]
    a_f = acc(tf)
    P = np.fft.rfft(a_f) / NFINE * 2          # einseitige Amplituden, Zeitursprung 0
    # beste Symmetrieachse suchen: minimiere max|a(t0+s) - a(t0-s)|
    s = np.linspace(0, T, 4001)
    best = (np.inf, None)
    for t0 in np.linspace(0, T, 2001)[:-1]:
        d = np.max(np.abs(acc(t0 + s) - acc(t0 - s)))
        if d < best[0]:
            best = (d, t0)
    triad = np.degrees(np.angle(P[1] ** 2 * np.conj(P[2])))
    print(f'{prof}: beste Achse t0 = {best[1] / T:.4f} T, max|a(t0+s)-a(t0-s)| = {best[0]:.3e} m/s^2; '
          f'Triadenphase arg(P1^2 P2*) = {triad:+.4f} Grad; |P_1..4| = ' +
          ' '.join(f'{abs(P[k]):.3f}' for k in range(1, 5)))
    if prof == 'egg':
        t0 = best[1]
        ph_rel = np.degrees(np.angle(P[1:7] * np.exp(1j * np.arange(1, 7) * W * t0)))
        print('     Phasen der P_k relativ zur Achse (sollen 0 oder +-180 sein), k=1..6: ' +
              ' '.join(f'{x:+.3f}' for x in ph_rel))
        print(f'     Mittelwert der Profilbeschleunigung je Periode: {a_f.mean():.2e} m/s^2; '
              f'Geschwindigkeitsamplitude RTOP*pi/(THOLD*T) = {se.RTOP * np.pi / (se.THOLD * T):.4f} m/s, '
              f'RBOT*pi/(TFAST*T) = {se.RBOT * np.pi / (se.TFAST * T):.4f} m/s')

print('\n=== D  Lineares Modell: Spiegelung und Harmonischenphasen ===')


def lin(p2, p3, K=se.K_REF, C=se.C_REF, prof='egg', nsamp=2000):
    """stationaere Loesung im Kontaktast: N(t) auf nsamp Stuetzstellen, komplexe N_k (k=1..),
    Gueltigkeit (N > 0)."""
    acc = se.PROFILES[prof][0]
    A = np.fft.rfft(acc(tf)) / NFINE                    # a(t) = sum A_k e^{ikwt} (zweiseitig)
    k = np.arange(A.size)
    w = W * k
    H = np.ones(A.size, complex) if K is None else (K + 1j * w * C) / (K - se.M * w ** 2 + 1j * w * C)
    Ab = A * Phi(k, p2, p3) / 3
    Nk2 = se.M * H * Ab                                  # zweiseitige Koeffizienten von N - Mg
    Nk2[0] = 0.0
    Nfull = se.MG + np.fft.irfft(Nk2 * NFINE, NFINE)
    Ns = Nfull[::NFINE // nsamp]
    return Ns, 2 * Nk2[1:10], H[1:10], A[1:10]


def obs(N):
    mu = N.mean(); m2 = ((N - mu) ** 2).mean(); m3 = ((N - mu) ** 3).mean()
    return mu, m3 / m2 ** 1.5, N.min(), N.max()


cases = [('Referenz K=1e4,C=16', se.K_REF, se.C_REF), ('C=0 (ungedaempft)', se.K_REF, 0.0),
         ('starr (H=1)', None, 0.0)]
pts = [(110.0, 234.0), (128.0, 246.0), (114.0, 252.0), (100.0, 240.0)]
for prof in ('egg', 'skew'):
    for cname, K, C in cases:
        print(f'-- Profil {prof}, {cname}')
        for (a, b) in pts:
            N1, Nk1, H, A = lin(a, b, K, C, prof)
            N2, Nk2, _, _ = lin(-a % 360, -b % 360, K, C, prof)
            o1, o2 = obs(N1), obs(N2)
            dmag = np.max(np.abs(np.abs(Nk1[:6]) - np.abs(Nk2[:6])))
            # Regel Spiegelung: arg N_k(A*) = 2 arg(H_k A_k) - arg N_k(A)
            pred = 2 * np.angle(H[:6] * A[:6]) - np.angle(Nk1[:6])
            dph = np.max(np.abs(np.angle(np.exp(1j * (np.angle(Nk2[:6]) - pred)))))
            print(f'   ({a:5.1f},{b:5.1f}) vs Spiegel: Schiefe {o1[1]:+.5f}/{o2[1]:+.5f}  F_min {o1[2]:.4f}/{o2[2]:.4f}'
                  f'  F_max {o1[3]:.4f}/{o2[3]:.4f}  max d|N_k| {dmag:.1e} N  Regel arg: {np.degrees(dph):.1e} Grad'
                  f'  (Kontaktast {"ja" if min(N1.min(), N2.min()) > 0 else "nein"})')
# Regel unter S3 (lineares Modell; exakt auch nichtlinear wegen Zeitverschiebung)
a, b = 110.0, 234.0
_, NkA, _, _ = lin(a, b)
print('-- S3-Regel arg N_k(gA) = arg N_k(A) + k*phi_ref an (110,234), k=1..6, Abweichung in Grad:')
for name, p2, p3, pref in se.s3_images(a, b):
    _, NkB, _, _ = lin(p2, p3)
    d = np.angle(NkB[:6] * np.exp(-1j * np.arange(1, 7) * np.radians(pref)) / NkA[:6])
    print(f'   {name:6s} ({p2:6.1f},{p3:6.1f}) phi_ref={pref:6.1f}:  ' + ' '.join(f'{np.degrees(x):+.1e}' for x in d)
          + f'   |N_k| max Abw. {np.max(np.abs(np.abs(NkB) - np.abs(NkA))):.1e} N')
tri = lambda Nk: np.degrees(np.angle(Nk[0] ** 2 * np.conj(Nk[1])))
print(f'   Triadenphase arg(N1^2 N2*) invariant: ' + ' '.join(f'{tri(lin(p2, p3)[1]):+.4f}' for _, p2, p3, _ in se.s3_images(a, b)))
_, NkM, H, A = lin(-a % 360, -b % 360)
thH = np.degrees(np.angle(H[0] ** 2 * np.conj(H[1])))
print(f'   Spiegel: Triade A {tri(NkA):+.3f}, A* {tri(NkM):+.3f}; Transferanteil arg(H1^2 H2*) = {thH:+.3f} Grad '
      f'-> Triade(A*) = 2*{thH:.3f} - Triade(A) = {2 * thH - tri(NkA):+.3f} (mod 360)')

print('\n=== E  Zeltschnitt phi3 = 240 Grad, Spiegelung = Spiegelung um phi2 = 120 Grad ===')
for (x, y) in [(100, 240), (110, 240), (135, 240)]:
    _, m2, m3, _ = se.s3_images(-x, -y)[0]
    print(f'   Spiegel von ({x},{y}) = ({m2:.0f},{m3:.0f}); S3-Bahn enthaelt ' +
          str([(round(p, 1), round(q, 1)) for _, p, q, _ in se.s3_images(m2, m3) if abs(q - 240) < 1e-9]))
for cname, K, C in cases:
    d = np.arange(0, 21, 2.0)
    fp = np.array([lin(120 + x, 240, K, C)[0].min() for x in d])
    fm = np.array([lin(120 - x, 240, K, C)[0].min() for x in d])
    sl_p = (fp[0] - fp[5]) / 10; sl_m = (fm[0] - fm[5]) / 10
    print(f'   {cname:22s} F_min(120+d) - F_min(120-d), d=0..20: max |.| = {np.max(np.abs(fp - fm)):.2e} N; '
          f'Steigung 120->130: {sl_p:.4f} N/Grad, 120->110: {sl_m:.4f} N/Grad; F_min(120,240) = {fp[0]:.4f} N')
    fpf = np.array([lin(120 + x, 240, K, C, nsamp=NFINE)[0].min() for x in d])
    fmf = np.array([lin(120 - x, 240, K, C, nsamp=NFINE)[0].min() for x in d])
    print(f'   {"":22s} dieselbe Differenz mit 8-fach feinerer Abtastung (16000/Periode): {np.max(np.abs(fpf - fmf)):.2e} N')

print('\n=== F  Datenpruefung der gespeicherten Karten ===')
d19 = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data/sweep_19x19.csv'))
u = 360 / 19
d19['i2'] = np.round(d19.phi2_deg / u).astype(int) % 19
d19['i3'] = np.round(d19.phi3_deg / u).astype(int) % 19
tab = {(r.i2, r.i3): r for r in d19.itertuples()}
pairs = [(i, j) for i in range(19) for j in range(19) if i < j]
dF = np.array([tab[(i, j)].F_mean - tab[(j, i)].F_mean for i, j in pairs])
print(f'Vertauschung (23), 171 Paare i<j: mittlere Differenz F_mean {dF.mean():+.3e} N, max |.| {np.abs(dF).max():.4f} N, '
      f'Paare mit |dF_mean| > 1e-6 N: {(np.abs(dF) > 1e-6).sum()}')
print('   (ueber alle 342 geordneten Paare ist die mittlere Differenz per Konstruktion exakt 0)')
for col, tol in (('F_skew', 1e-3), ('liftoff', 0.1), ('F_min', 1e-3), ('F_max', 1e-2)):
    nviol = 0; nb = set()
    for (i, j), r in tab.items():
        for _, p2, p3, _ in se.s3_images(i * u, j * u):
            k2, k3 = int(round(p2 / u)) % 19, int(round(p3 / u)) % 19
            if abs(getattr(tab[(k2, k3)], col) - getattr(r, col)) > tol:
                nviol += 1; nb.add(tuple(sorted([(i, j), (k2, k3)])))
                break
    print(f'   volle S3-Gruppe, {col} |Diff| > {tol}: {nviol} von 361 Punkten verletzt')
# liftoff-freie Punkte der Karte
lf = d19[d19.liftoff == 0]
print(f'   liftoff-freie Punkte der Karte: {len(lf)}; verschiedene (Schiefe, F_min)-Werte: '
      f'{len(set(zip(lf.F_skew.round(5), lf.F_min.round(5))))}')
orb = {}
for r in lf.itertuples():
    key = min((round(p2, 1), round(p3, 1)) for _, p2, p3, _ in se.s3_images(r.phi2_deg, r.phi3_deg))
    orb.setdefault(key, []).append(r)
for key, rs in orb.items():
    print(f'   S3-Bahn {key}: {len(rs)} Punkte; Spannweite F_min {max(x.F_min for x in rs) - min(x.F_min for x in rs):.2e} N, '
          f'Schiefe {max(x.F_skew for x in rs) - min(x.F_skew for x in rs):.2e}, F_max {max(x.F_max for x in rs) - min(x.F_max for x in rs):.2e} N')
fsw = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data/finesweep_2deg_120_240.csv'))
ft = {(int(round(r.phi2_deg)), int(round(r.phi3_deg))): r for r in fsw.itertuples()}
cnt = 0; mx = {c: 0.0 for c in ('F_skew', 'F_min', 'F_max', 'liftoff', 'F_mean')}
for (a, b), r in ft.items():
    for name, p2, p3, _ in se.s3_images(a, b):
        key = (int(round(p2)), int(round(p3)))
        if name != 'id' and key in ft:
            cnt += 1
            for c in mx:
                mx[c] = max(mx[c], abs(getattr(ft[key], c) - getattr(r, c)))
print(f'Feinsweep 2 Grad (441 Punkte): {cnt} Paare (Punkt, S3-Bild) liegen beide im Fenster; max |Diff|: ' +
      ', '.join(f'{c} {v:.2e}' for c, v in mx.items()))
