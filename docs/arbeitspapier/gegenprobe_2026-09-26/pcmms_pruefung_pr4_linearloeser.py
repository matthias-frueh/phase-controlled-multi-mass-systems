#!/usr/bin/env python3
"""
PCMMS – unabhängige Prüfung zu PR #4 (code/linear_solver.py)

Nachgerechnet mit eigenem Löser (exakte Fourierkoeffizienten des Egg-Profils,
kein Code aus PR #4) und einer RK4-Nachbildung von pcmms_v3a_phasen_sweep.py.
Modell und Parameter unverändert: M = 0,65 kg, f = 10 Hz, RTOP = 5 mm,
Halteanteil 0,65, K = 1e4 N/m, C = 16 N·s/m, dt = 5e-5 s.

  A  K-Tabelle Werkstattbericht: Herkunft der Werte 1,5028 / 3,4080
  B  Band um 3f = f_n, in dem der triphasische Punkt selbst abhebt
  C  Zweite Harmonische in Resonanz: Anteil an Zeltsteigung und Liftoff-Karte
  D  Liftoff-freie Menge: Hauptgebiete und Satelliteninseln
  E  RK4-Gegenproben: Abheben bei K = 23 000; Bistabilität in den Inseln

Laufzeit etwa 1–2 min, nur numpy/scipy.
"""
import numpy as np
from scipy import ndimage

M, G = 0.650, 9.81; MG = M*G
T = 0.1; W0 = 2*np.pi/T
RTOP, TH = 0.005, 0.65; TF = 1 - TH; RBOT = RTOP*TF/TH
K0, C0 = 1e4, 16.0
ZETA0 = C0/(2*np.sqrt(K0*M))                  # 0,099228 (exakt aus C = 16)

# ── Linearer Referenzlöser (nur gültig ohne Liftoff) ─────────────────────────
KMAX = 8000
k = np.arange(KMAX+1)

def _half(kk, L):                             # ∫_0^L sin(πu/L) e^{-2πiku} du
    a = np.pi/L; b = 2*np.pi*kk
    return (1 + np.exp(-1j*b*L))*a/(a*a - b*b)

c = (-RTOP*(np.pi/(TH*T))**2*_half(k, TH)
     + RBOT*(np.pi/(TF*T))**2*np.exp(-2j*np.pi*k*TH)*_half(k, TF))
c[0] = 0.0                                    # Zyklusbilanz: Mittel der Beschleunigung exakt 0

def H(K=K0, C=C0, rigid=False):
    w = k*W0
    return np.ones_like(w, complex) if rigid else (K + 1j*w*C)/(K - M*w*w + 1j*w*C)

def force(p2, p3, Hk, n=16000):
    """stationäre Kontaktkraft F(t) auf n Punkten je Zyklus; ⟨F⟩ = Mg per Konstruktion"""
    P = (1 + np.exp(-1j*k*np.radians(p2)) + np.exp(-1j*k*np.radians(p3)))/3
    Fk = M*Hk*c*P; kk = n//2 - 1
    s = np.zeros(n, complex); s[1:kk+1] = Fk[1:kk+1]; s[-kk:] = np.conj(Fk[1:kk+1][::-1])
    return MG + np.real(np.fft.ifft(s)*n)

def Hz(K): return H(K, 2*ZETA0*np.sqrt(K*M))  # ζ fest, C ∝ √K

def fmin(p2, p3, Hk): return force(p2, p3, Hk).min()

print("=== A  K-Tabelle (triphasischer Punkt 120°/240°), F_min [N]")
wb = {1e4: 5.3304, 3e4: 1.5028, 1e5: 3.4080, 1e6: 4.3404, 1e7: 4.4823}
print("  K        zeta exakt   zeta=0,0993   C=16 fest   Werkstattbericht")
for K, v in wb.items():
    print(f"  {K:8.0e}  {fmin(120,240,Hz(K)):8.4f}     "
          f"{fmin(120,240,H(K, 2*0.0993*np.sqrt(K*M))):8.4f}      "
          f"{fmin(120,240,H(K, C0)):8.4f}     {v:.4f}")
d = (fmin(120,240,H(3e4, 2*1.01*ZETA0*np.sqrt(3e4*M))) - fmin(120,240,H(3e4, 2*0.99*ZETA0*np.sqrt(3e4*M))))/2
print(f"  Empfindlichkeit bei K=3e4: +1 % zeta -> {d:+.4f} N")
print(f"  starrer Grenzfall: {fmin(120,240,H(rigid=True)):.5f} N (Zeitbereich exakt: 4,54827)")

print("\n=== B  Triphasischer Punkt über K (zeta fest)")
Ks = np.arange(20000, 28001, 250)
v = np.array([fmin(120, 240, Hz(K)) for K in Ks])
neg = Ks[v <= 0]
print(f"  F_min <= 0 für K = {neg.min()} … {neg.max()} N/m "
      f"(3f/f_n = {30/(np.sqrt(neg.max()/M)/(2*np.pi)):.2f} … {30/(np.sqrt(neg.min()/M)/(2*np.pi)):.2f}); "
      f"Minimum {v.min():+.3f} N bei K = {Ks[v.argmin()]}; 3f = f_n bei K = {M*(2*np.pi*30)**2:.0f}")

print("\n=== C  Harmonische der Referenz (Einzelmodul, volle Masse)")
Hr = H()
print(f"  f_n = {np.sqrt(K0/M)/(2*np.pi):.2f} Hz")
for kk in range(1, 5):
    print(f"  k={kk}  {10*kk:2d} Hz  |H|={abs(Hr[kk]):4.2f}  Kraftamplitude 2M|Hc| = {2*M*abs(Hr[kk]*c[kk]):6.3f} N")
H2q = Hr.copy(); H2q[2] = 1.0                 # Diagnose: 2. Harmonische nur quasistatisch
for lab, Hk in [("Referenz", Hr), ("H_2 := 1", H2q)]:
    f0 = fmin(120, 240, Hk)
    print(f"  {lab:9s} Zeltsteigung 118->120: {(f0-fmin(118,240,Hk))/2:.3f} N/°, 122->120: {(f0-fmin(122,240,Hk))/2:.3f} N/°")

def fmin_map(Hk, N=3600):
    Fk = M*Hk[:N//2]*c[:N//2]
    s = np.zeros(N, complex); s[1:N//2] = Fk[1:]; s[-(N//2-1):] = np.conj(Fk[1:][::-1])
    h = np.real(np.fft.ifft(s)*N); st = N//360
    Hs = np.stack([np.roll(h, j*st) for j in range(360)])
    return np.array([MG + ((h + Hs[i])[None, :] + Hs).min(1)/3 for i in range(360)])

m_ref = fmin_map(Hr)
print(f"  liftoff-freier Anteil 1°-Karte: Referenz {100*np.mean(m_ref>0):.2f} %, "
      f"mit H_2 := 1: {100*np.mean(fmin_map(H2q)>0):.1f} %")
print(f"  Vergleich README: starr {100*np.mean(fmin_map(H(rigid=True))>0):.1f} %, "
      f"K=1e6 zeta fest {100*np.mean(fmin_map(Hz(1e6))>0):.1f} % / C=16 fest {100*np.mean(fmin_map(H(1e6, C0))>0):.1f} %")

print("\n=== D  Zusammenhangskomponenten der liftoff-freien Menge (periodisch)")
lab, _ = ndimage.label(np.tile(m_ref > 0, (3, 3)))
L = lab[360:720, 360:720]
ids, cnt = np.unique(L[L > 0], return_counts=True)
for i in np.argsort(-cnt):
    P = np.argwhere(L == ids[i])
    print(f"  {cnt[i]:5d} Punkte um ({P[:,0].mean():.0f}°, {P[:,1].mean():.0f}°), F_min max {m_ref[L==ids[i]].max():.3f} N")

print("\n=== E  RK4 (Engine-Nachbildung, dt = 5e-5, 20 s, Auswertung letzte 4 s)")
DT = 5e-5; NH = int(round(T/(DT/2)))          # 4000 Halbschritte je Zyklus
def a1(t):
    ph = (t % T)/T
    return np.where(ph < TH, -RTOP*(np.pi/(TH*T))**2*np.sin(np.pi*ph/TH),
                    RBOT*(np.pi/(TF*T))**2*np.sin(np.pi*(ph-TH)/TF))
def lin_state(p2, p3, K=K0, C=C0):
    P = (1 + np.exp(-1j*k*np.radians(p2)) + np.exp(-1j*k*np.radians(p3)))/3; w = k*W0
    zk = -M*c*P/(K - M*w*w + 1j*w*C); zk[0] = 0
    return float(-MG/K + 2*np.real(zk[1:].sum())), float(2*np.real((1j*w*zk)[1:].sum()))
runs = [  # (Bezeichnung, phi2, phi3, K, C, z0, v0)
    ("K=23000, zeta fest, Standardstart", 120, 240, 23000., 2*ZETA0*np.sqrt(23000*M), -MG/23000, 0.0),
    ("Insel (35,116), Standardstart",      35, 116, K0, C0, -MG/K0, 0.0),
    ("Insel (35,116), Start auf Kontaktorbit", 35, 116, K0, C0, *lin_state(35, 116)),
    ("Insel (28,115), Standardstart",      28, 115, K0, C0, -MG/K0, 0.0),
    ("Insel (28,115), Start auf Kontaktorbit", 28, 115, K0, C0, *lin_state(28, 115)),
    ("Hauptgebiet (98,240), Wurf v0=3 m/s", 98, 240, K0, C0, -MG/K0, 3.0),
    ("Hauptgebiet (148,240), Wurf v0=3 m/s", 148, 240, K0, C0, -MG/K0, 3.0),
]
th = np.arange(NH)*(DT/2)
A = np.array([(a1(th) + a1(th - p2/360*T) + a1(th - p3/360*T))/3 for _, p2, p3, *_ in runs])
Kv = np.array([r[3] for r in runs]); Cv = np.array([r[4] for r in runs])
z = np.array([r[5] for r in runs], float); v = np.array([r[6] for r in runs], float)
NST = int(round(20/DT)); NEV = int(round(4/DT)); lift = np.zeros(len(runs)); idx = np.arange(len(runs))
def acc(z, v, j):
    F = -Kv*z - Cv*v; F = np.where((z >= 0) | (F <= 0), 0.0, F)
    return -G + F/M - A[idx, j], F
for i in range(NST):
    j0 = (2*i) % NH; j1 = (2*i+1) % NH; j2 = (2*i+2) % NH
    a_1, F = acc(z, v, j0)
    if i >= NST - NEV: lift += (F < 1e-9)
    a_2, _ = acc(z + .5*DT*v, v + .5*DT*a_1, j1)
    a_3, _ = acc(z + .5*DT*(v + .5*DT*a_1), v + .5*DT*a_2, j1)
    a_4, _ = acc(z + DT*(v + .5*DT*a_2), v + DT*a_3, j2)
    z, v = (z + DT*(v + DT*(a_1 + a_2 + a_3)/6),
            v + DT*(a_1 + 2*a_2 + 2*a_3 + a_4)/6)
for (name, *_), lf in zip(runs, lift):
    print(f"  {name:42s} Liftoff {100*lf/NEV:6.2f} %")
