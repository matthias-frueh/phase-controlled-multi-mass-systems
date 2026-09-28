#!/usr/bin/env python3
"""
PCMMS – Gegenprobe zur Vorzeichenregel der Schiefe (Stand 26.09.2026)

Offener Punkt aus einer Projektnotiz vom 30.07.2026: „Ein sauberer
Einzelmodul-Sweep (Amplitude/Frequenz eines einzelnen Oszillators über denselben
Liftoff-Bereich) fehlt noch als formaler Beleg.“

Modell und Parameter unverändert wie Engine v3a bzw. pcmms_pruefung_pr4_linearloeser.py:
M = 0,65 kg, f = 10 Hz, RTOP = 5 mm, Halteanteil 0,65, K = 1e4 N/m, C = 16 N·s/m,
RK4 fest, dt = 5e-5 s, 20 s, Auswertung letzte 4 s. Sensitivität wie im Arbeitspapier:
zeta fest (C ∝ √K). Nur Simulation, keine Messdaten.

  A  Validierung gegen Projektzahlen (Präreg-v2-Anhang, Arbeitspapier v2.3)
  B  Einzelmodul im Kontaktast: gamma1 über 3f/f_n, Nullstellen
  C  Amplitudensweep eines einzelnen Oszillators durch den Liftoff-Bereich
  D  Zweiergruppen-Linie (0°, phi3) bei vollem Hub, K = 6944 N/m; dt/2-Gegenprobe
  E  Triadenzerlegung des dritten Moments im Kontaktast (Gl. triaden, Arbeitspapier v2.4)
  F  19×19-Raster: Punkte mit Kontaktorbit gegen liftoff-freie Punkte der CSV
     (liest data/sweep_19x19.csv des Repositorys oder eine als erstes Argument übergebene Datei)

Laufzeit etwa 3 min, nur numpy (F zusätzlich pandas).
"""
import numpy as np

M, G = 0.650, 9.81; MG = M*G
RTOP, TH = 0.005, 0.65; TF = 1 - TH; RBOT = RTOP*TF/TH
K0, C0 = 1e4, 16.0; ZETA0 = C0/(2*np.sqrt(K0*M))            # 0,099228
F0 = 10.0

def c_of(K): return 2*ZETA0*np.sqrt(K*M)                      # Dämpfung bei festem zeta
def r3(K, f=F0): return 3*f/(np.sqrt(K/M)/(2*np.pi))          # 3f/f_n
def skew(x, axis=0):
    x = x - x.mean(axis, keepdims=True)
    return (x**3).mean(axis)/(x**2).mean(axis)**1.5

# ── Linearer Kontaktast (Frequenzbereich, gültig nur ohne Liftoff) ─────────────
KMAX = 4000; k = np.arange(KMAX+1)
def _half(kk, L):
    a = np.pi/L; b = 2*np.pi*kk
    return (1 + np.exp(-1j*b*L))*a/(a*a - b*b)
def coeff(f):
    T = 1/f
    c = (-RTOP*(np.pi/(TH*T))**2*_half(k, TH)
         + RBOT*(np.pi/(TF*T))**2*np.exp(-2j*np.pi*k*TH)*_half(k, TF))
    c[0] = 0.0; return c
def H(f, K=K0, C=C0, rigid=False):
    w = k*2*np.pi*f
    return np.ones_like(w, complex) if rigid else (K + 1j*w*C)/(K - M*w*w + 1j*w*C)
def force_lin(P, Hk, c, n=8000):
    Fk = M*Hk*c*P; kk = n//2 - 1
    s = np.zeros(n, complex); s[1:kk+1] = Fk[1:kk+1]; s[-kk:] = np.conj(Fk[1:kk+1][::-1])
    return MG + np.real(np.fft.ifft(s)*n)
def P3(p2, p3): return (1 + np.exp(-1j*k*np.radians(p2)) + np.exp(-1j*k*np.radians(p3)))/3
P1 = np.full(len(k), 1/3)                                     # nur Modul 1 läuft

# ── RK4-Nachbildung der Engine (einseitiger Kelvin-Voigt-Kontakt) ──────────────
def rk4(Afun, K, C, f=F0, h=2.5e-5, Tsim=20.0, Tev=4.0):
    """Afun(th) -> Array (n_runs, NH) der Modulbeschleunigung je Halbschritt"""
    T = 1/f; NH = int(round(T/h)); DT = 2*T/NH
    A = Afun(np.arange(NH)*(DT/2), T); n = A.shape[0]; idx = np.arange(n)
    z = np.full(n, -MG/K); v = np.zeros(n)
    NST = int(round(Tsim/DT)); NEV = int(round(Tev/DT)); Fs = np.empty((NEV, n))
    def acc(z, v, j):
        F = -K*z - C*v; F = np.where((z >= 0) | (F <= 0), 0.0, F)
        return -G + F/M - A[idx, j], F
    for i in range(NST):
        j0 = (2*i) % NH; j1 = (2*i+1) % NH; j2 = (2*i+2) % NH
        q1, F = acc(z, v, j0)
        if i >= NST - NEV: Fs[i-(NST-NEV)] = F
        q2, _ = acc(z + .5*DT*v, v + .5*DT*q1, j1)
        q3, _ = acc(z + .5*DT*(v + .5*DT*q1), v + .5*DT*q2, j1)
        q4, _ = acc(z + DT*(v + .5*DT*q2), v + DT*q3, j2)
        z, v = z + DT*(v + DT*(q1 + q2 + q3)/6), v + DT*(q1 + 2*q2 + 2*q3 + q4)/6
    return skew(Fs), (Fs < 1e-9).mean(0), Fs.mean(0)/MG - 1
def a1(t, T):
    ph = (t % T)/T
    return np.where(ph < TH, -RTOP*(np.pi/(TH*T))**2*np.sin(np.pi*ph/TH),
                    RBOT*(np.pi/(TF*T))**2*np.sin(np.pi*(ph - TH)/TF))

# ═════════════════════════════════════════════════════════════════════════════
print("=== A  Validierung (Referenz K = 1e4 N/m, C = 16 N·s/m, 10 Hz)")
c10, H10 = coeff(F0), H(F0)
F = force_lin(P3(120, 240), H10, c10)
print(f"  Triphasik (120°, 240°): gamma1 = {skew(F):+.3f}, F_min = {F.min():.4f} N   [Anhang: +0,067; 5,3304 N]")
print(f"  Triphasik, starr      : gamma1 = {skew(force_lin(P3(120, 240), H(F0, rigid=True), c10)):+.3f}            [Anhang: −0,450]")
for (p2, p3), ref in [((113.68, 227.37), "−0,273 / 2,882 N"), ((94.74, 227.37), "−0,092 / 0,753 N")]:
    F = force_lin(P3(p2, p3), H10, c10)
    print(f"  ({p2:.1f}°, {p3:.1f}°): gamma1 = {skew(F):+.3f}, F_min = {F.min():.3f} N   [AP v2.3 Tab. liftoff-frei: {ref}]")
print(f"  f_n = {np.sqrt(K0/M)/(2*np.pi):.2f} Hz; 2f/f_n = {2*F0/(np.sqrt(K0/M)/(2*np.pi)):.3f}; "
      f"|H_1..3| = {abs(H10[1]):.2f} / {abs(H10[2]):.2f} / {abs(H10[3]):.2f}")

print("\n=== B  Einzelmodul im Kontaktast: gamma1 gegen 3f/f_n (zeta fest; im Kontaktast hubunabhängig)")
def g1_single(x):
    K = M*(2*np.pi*3*F0/x)**2
    return skew(force_lin(P1, H(F0, K, c_of(K)), c10))
xs = np.linspace(0.2, 8.0, 7801); gs = np.array([g1_single(x) for x in xs])
zc = xs[:-1][np.sign(gs[:-1]) != np.sign(gs[1:])]
print(f"  Nullstellen bei 3f/f_n = {', '.join(f'{z:.3f}' for z in zc)}"
      f"  (K bei 10 Hz: {', '.join(f'{M*(2*np.pi*30/z)**2:.0f}' for z in zc)} N/m)")
for x in [0.48, 0.88, 1.0, 1.4, 1.52, 1.6, 1.7, 1.82, 2.0, 2.4, 2.77, 3.0, 4.81]:
    print(f"  3f/f_n = {x:4.2f}   gamma1 = {g1_single(x):+.3f}")
print(f"  starre Auflage: gamma1 = {skew(force_lin(P1, H(F0, rigid=True), c10)):+.3f}")
Fs1 = force_lin(P1, H10, c10)
print(f"  Referenz, Einzelmodul, voller Hub: linear F_min = {Fs1.min():+.3f} N -> hebt ab, Kontaktast dort ungültig")

print("\n=== C  Amplitudensweep eines einzelnen Oszillators (s = 1/3: ein Modul, s = 1: synchron)")
svals = np.array([0.10, 0.20, 0.25, 1/3, 0.40, 0.50, 0.60, 0.75, 1.00])
for K in (K0, 6944.0):
    g1, lam, dm = rk4(lambda th, T: svals[:, None]*a1(th, T)[None, :], K, c_of(K) if K != K0 else C0)
    print(f"  K = {K:.0f} N/m, C = {c_of(K) if K != K0 else C0:.2f} N·s/m, 3f/f_n = {r3(K):.2f}")
    for s_, g, l, d in zip(svals, g1, lam, dm):
        tag = "   <- ein Modul, Referenzhub" if abs(s_ - 1/3) < 1e-9 else ("   <- synchron" if s_ == 1 else "")
        print(f"    s = {s_:4.2f}   gamma1 = {g:+.3f}   Liftoff {100*l:5.1f} %   <N>/Mg−1 = {d:+.1e}{tag}")

print("\n=== D  Zweiergruppen-Linie (0°, phi3), voller Hub, K = 6944 N/m (3f/f_n = 1,82; zeta fest)")
K = 6944.0; C = c_of(K)
p3 = np.arange(0, 360, 20.0)
g1, lam, _ = rk4(lambda th, T: np.array([(2*a1(th, T) + a1(th - q/360*T, T))/3 for q in p3]), K, C)
print("  " + "  ".join(f"{q:.0f}°: {g:+.2f}/{100*l:.0f} %" for q, g, l in zip(p3, g1, lam)))
p3f = np.array([170.0, 180.0, 190.0])
for h in (2.5e-5, 1.25e-5):
    g1, lam, _ = rk4(lambda th, T: np.array([(2*a1(th, T) + a1(th - q/360*T, T))/3 for q in p3f]), K, C, h=h)
    print(f"  dt = {2*h:.1e} s: " + "  ".join(f"{q:.0f}°: gamma1 = {g:+.3f}, Liftoff {100*l:.1f} %" for q, g, l in zip(p3f, g1, lam)))
g1r, _, _ = rk4(lambda th, T: np.array([(2*a1(th, T) + a1(th - q/360*T, T))/3 for q in p3]), K0, C0)
print(f"  zum Vergleich Referenz K = 1e4: min gamma1 auf der Linie = {g1r.min():+.3f} bei {p3[g1r.argmin()]:.0f}°"
      f"   [AP v2.3: Paarlinien +0,60 … +1,72]")

print("\n=== E  Triadenzerlegung im Kontaktast: <(N-Mg)^3> = 6 Σ Re(N_j^2 N_2j*) + 12 Σ_{j<l} Re(N_j N_l N_{j+l}*)")
def harm(P, Hk): return (M*Hk*c10*P)[1:]          # komplexe Harmonische N_j, j >= 1
def m3_triaden(Nj, J=120):
    Nj = Nj[:J]; d = sum(6*np.real(Nj[a]**2*np.conj(Nj[2*a+1])) for a in range(J//2 - 1))
    o = sum(12*np.real(Nj[a]*Nj[b]*np.conj(Nj[a+b+1])) for a in range(J) for b in range(a+1, J) if a+b+1 < J)
    return d + o
for x in (1.52, 1.82):
    Kx = M*(2*np.pi*3*F0/x)**2; Hk = H(F0, Kx, c_of(Kx)); Nj = harm(P1, Hk)
    Fx = force_lin(P1, Hk, c10); m3 = ((Fx - Fx.mean())**3).mean()
    t112 = 6*np.real(Nj[0]**2*np.conj(Nj[1]))
    print(f"  3f/f_n = {x}: m3 direkt {m3:+.4e}, Triadensumme {m3_triaden(Nj):+.4e}; "
          f"Triade (1,1,2) {100*t112/m3:.0f} % von m3; cos arg(N1^2 N2*) = {np.cos(np.angle(Nj[0]**2*np.conj(Nj[1]))):+.3f}")
Nr = harm(P1, H(F0, rigid=True))
print(f"  starr: cos arg(N1^2 N2*) = {np.cos(np.angle(Nr[0]**2*np.conj(Nr[1]))):+.3f} (Profil zeitumkehrsymmetrisch -> Triadenphasen 0 oder pi)")
print(f"  Referenz: Kontaktanteil arg(T1^2 T2*) = {np.degrees(np.angle(H10[1]**2*np.conj(H10[2]))):+.1f}°, "
      f"arg T1 = {np.degrees(np.angle(H10[1])):+.1f}°, arg T2 = {np.degrees(np.angle(H10[2])):+.1f}°")
def g_red(x):                                        # Zwei-Harmonischen-Reduktion
    Kx = M*(2*np.pi*3*F0/x)**2; Nj = harm(P1, H(F0, Kx, c_of(Kx)))
    return 6*np.real(Nj[0]**2*np.conj(Nj[1]))/(2*(abs(Nj[0])**2 + abs(Nj[1])**2))**1.5
xr = np.linspace(1.3, 3.0, 1701); gr = np.array([g_red(v) for v in xr])
print(f"  Nullstellen der Zwei-Harmonischen-Reduktion: {', '.join(f'{z:.3f}' for z in xr[:-1][np.sign(gr[:-1]) != np.sign(gr[1:])])}")
zs = np.linspace(0.01, 0.5, 4901)
gz = np.array([skew(force_lin(P1, H(F0, K0, 2*z*np.sqrt(K0*M)), c10)) for z in zs])
print(f"  Einzelmodul bei K = 1e4 N/m: Vorzeichenwechsel bei zeta = {', '.join(f'{z:.4f}' for z in zs[:-1][np.sign(gz[:-1]) != np.sign(gz[1:])])}")
for Kx in (K0, 6944.0):
    Cx = C0 if Kx == K0 else c_of(Kx)
    print(f"  Paar (0°, 180°) im Kontaktast, K = {Kx:.0f}: gamma1 = {skew(force_lin(P3(0, 180), H(F0, Kx, Cx), c10)):+.3f}")
for p2, p3 in [(0, 0), (0, 180), (0, 120)]:
    Ph = lambda j: 1 + np.exp(-1j*j*np.radians(p2)) + np.exp(-1j*j*np.radians(p3))
    print(f"  Konfigurationsanteil arg(Phi1^2 Phi2*) bei ({p2}°, {p3}°): {np.degrees(np.angle(Ph(1)**2*np.conj(Ph(2)))):+.1f}°")

print("\n=== F  19×19-Raster: Kontaktorbit (lineares F_min > 0) gegen liftoff-freie Punkte der CSV")
import os, sys
hier = os.path.dirname(os.path.abspath(__file__))
cand = [a for a in sys.argv[1:2]] + [os.path.join(hier, "..", "..", "..", "data", "sweep_19x19.csv"), "data/sweep_19x19.csv", "sweep_19x19.csv"]
path = next((q for q in cand if os.path.exists(q)), None)
if path is None:
    print("  sweep_19x19.csv nicht gefunden – Abschnitt F übersprungen")
else:
    import pandas as pd
    df = pd.read_csv(path)
    fl = np.array([force_lin(P3(a, b), H10, c10, n=4000).min() for a, b in zip(df.phi2_deg, df.phi3_deg)])
    orbit = fl > 0; frei = df.liftoff.values == 0
    print(f"  Punkte mit Kontaktorbit: {orbit.sum()}, liftoff-frei in der CSV: {frei.sum()}, übereinstimmend: {(orbit & frei).sum()}")
    print("  -> kein Rasterpunkt liegt in einer bistabilen Satelliteninsel" if (orbit == frei).all() else "  -> ABWEICHUNG, prüfen")
    gp = (np.abs(df.phi2_deg) < 1e-6) | (np.abs(df.phi3_deg) < 1e-6) | (np.abs(df.phi2_deg - df.phi3_deg) < 1e-6)
    print(f"  gleichphasige Paare im Raster: {gp.sum()} Konfigurationen, Liftoff {df.liftoff[gp].min():.1f} … {df.liftoff[gp].max():.1f} %, "
          f"gamma1 {df.F_skew[gp].min():+.3f} … {df.F_skew[gp].max():+.3f}")
