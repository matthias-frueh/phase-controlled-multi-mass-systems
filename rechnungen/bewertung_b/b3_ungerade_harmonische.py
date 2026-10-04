"""P3 bewertung_b, Uebertragung von Kandidat 19 (B12, Halbperioden-Antisymmetrie) auf Linie A.
Behauptung [E]: Ein Lageprofil nur aus ungeraden Harmonischen (x(t+T/2) = -x(t)) liefert im
linearen Kontaktast fuer JEDE Phasenkonfiguration gamma1 = 0, A = 1 und keine geraden
Harmonischen in N(t). Gerade Harmonische bzw. gamma1 != 0 entstehen erst durch Nichtlinearitaet
(hier: quadratische Kennlinie y = N + eps2*(N-Mg)^2), nicht durch lineare Modulkopplung.
Zusaetzlich: Skalierung des Restes mit der Amplitude (A^2 bei Nichtlinearitaet).
Modell: 1-FG-Kontakt H(w) = (K+iwC)/(K-Mw^2+iwC) wie Praereg §8.7 (A2.1), starre Module, mu=0,46.
Parameter [A]: V1-Kandidat aus P2 (3x100 g, 8 mm Spitze-Spitze, 10 Hz, K=1,5e6 N/m, zeta=0,05).
"""
import numpy as np

M, g = 0.650, 9.81
Mg = M * g
f = 10.0
w0 = 2 * np.pi * f
K = 1.5e6
zeta = 0.05
C = 2 * zeta * np.sqrt(K * M)
m = 0.100           # Masse je Modul
n = 4096
t = np.arange(n) / n / f
kmax = 40

def H(w):
    return (K + 1j * w * C) / (K - M * w * w + 1j * w * C)

def profile(kind, amp):
    th = 2 * np.pi * f * t
    if kind == "ungerade":      # zeitasymmetrisch, aber halbperioden-antisymmetrisch
        x = np.sin(th) + 0.35 * np.sin(3 * th + 0.9) + 0.12 * np.sin(5 * th + 2.1)
    elif kind == "egg":         # Linie-A-Egg, TH = 0,65 (enthaelt gerade Harmonische)
        TH, TF = 0.65, 0.35
        p = (t * f) % 1.0
        x = np.where(p < TH, np.sin(np.pi * p / TH), -(TF / TH) * np.sin(np.pi * (p - TH) / TF))
    x = x - x.mean()
    return amp * x / (x.max() - x.min())   # amp = Spitze-Spitze

def module_force(x, phi_deg, k_c=0.0, x_other=None):
    X = np.fft.rfft(x) / n
    k = np.arange(X.size)
    shift = np.exp(-1j * k * np.radians(phi_deg))
    A = -(k * w0) ** 2 * X * shift
    if k_c and x_other is not None:     # lineare Kopplung: Teil der Nachbarbeschleunigung
        Xo = np.fft.rfft(x_other) / n
        A = A + k_c * (-(k * w0) ** 2) * Xo
    F = m * H(k * w0) * A
    F[kmax + 1:] = 0
    F[0] = 0
    return np.fft.irfft(F * n, n)

def stats(N):
    d = N - N.mean()
    g1 = np.mean(d ** 3) / np.mean(d ** 2) ** 1.5
    S = np.abs(np.fft.rfft(d) / n)
    even = np.sqrt(np.sum(S[2:kmax + 1:2] ** 2))
    odd = np.sqrt(np.sum(S[1:kmax + 1:2] ** 2))
    A = (N.max() - N.mean()) / (N.mean() - N.min())
    return g1, even / odd, A

phases = [(0, 0), (120, 240), (110, 250), (35, 116), (60, 200)]
for kind in ("ungerade", "egg"):
    print(f"== Profil {kind}")
    x = profile(kind, 0.008)
    for p2, p3 in phases:
        N = Mg + module_force(x, 0) + module_force(x, p2) + module_force(x, p3)
        g1, r, A = stats(N)
        Nc = Mg + module_force(x, 0, 0.01, profile(kind, 0.008)) + module_force(x, p2) + module_force(x, p3)
        g1c, rc, _ = stats(Nc)
        y = N + 0.002 * (N - Mg) ** 2            # quadratische Kennlinie, eps2 = 0,002 1/N
        g1n, rn, _ = stats(y)
        print(f"  ({p2:3d},{p3:3d})  linear: g1={g1:+.2e} gerade/ungerade={r:.1e} A={A:.4f} | "
              f"lin. Kopplung 1 %: g1={g1c:+.1e} ger/ung={rc:.1e} | quadr. Kennlinie: g1={g1n:+.3e} ger/ung={rn:.2e}")

print("== Skalierung der geraden Harmonischen mit der Amplitude (Profil ungerade, (110,250), eps2=0,002)")
for amp in (0.004, 0.008):
    x = profile("ungerade", amp)
    N = Mg + module_force(x, 0) + module_force(x, 110) + module_force(x, 250)
    y = N + 0.002 * (N - Mg) ** 2
    d = y - y.mean()
    S2 = np.abs(np.fft.rfft(d) / n)[2]
    print(f"  Hub {amp*1e3:.0f} mm: |N_2| = {S2*2*1e3:.4f} mN")
