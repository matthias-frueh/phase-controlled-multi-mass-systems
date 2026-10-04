"""s4_identifizierbarkeit.py – Welche Alternativursachen erzeugen eine H1-Signatur (Verletzung der Superposition
der einzeln gemessenen Modulantworten), und wie groß ist sie im Vergleich zu Δ_q und zur Nachweisgrenze c·u_c?

Prüfgruppe statistik, P2. Nur lesend auf Repo-Code (linear_solver.py, finesweep.z_egg_zdd).

Grundsatz (analytisch, A2.1): Für jedes lineare zeitinvariante (LTI) System aus Mechanik und Messkette gilt die
Superposition der gemessenen Einzelantworten exakt; LTI-Artefakte (Übersprechen, lineare Kipp-/Querkraftanteile,
Strukturresonanzen, lineare Kabel- und Luftkräfte, EM-Einstreuung je Antrieb) erzeugen KEINE H1-Signatur.
Eine H1-Signatur entsteht nur durch (i) Nichtlinearität, (ii) Zeitvarianz zwischen Einzel- und Kombinationsläufen,
(iii) Wechselwirkung der Antriebe, die in Einzelläufen fehlt. Hier werden Beispiele beziffert (A4-Beispiel:
μ = 0,4, 10 Hz, Egg-Profil, k_max = 9, Δ_q aus s0/s2: Δ_F = 129,3 mN, Δ_N1 = 112,6, Δ_N2 = 73,1, Δ_N3 = 138,3 mN).

a) Hertzscher Kontakt statt linearer Feder (RK4, Δt = 25 µs, 3 s, letzter Zyklus): N = κ·δ^{3/2} + c·δ̇,
   linearisierte Eigenfrequenz f_n0 bei statischer Last ∈ {40, 60, 120, 300} Hz, ζ = 0,05; Gegenprobe mit linearer
   Feder gleicher f_n0 (Residuum muss ≈ 0 sein).
b) Quadratische Kennlinie der Wägezellen, N_c,mess = N_c + β·N_c², β = 4·ε_lin/FS (Parabel mit größter
   Abweichung ε_lin·FS bei halber Nennlast); ε_lin = 0,02 % bzw. 0,05 %, FS = 10 N bzw. 49 N; Geometrie 'über Zelle'
   (A2.5: jedes Modul über einer Zelle) und 'zentral' (jedes Modul verteilt sich zu je 1/3 auf alle Zellen).
c) Verstärkungsdrift zwischen Phase 0 und Phase 1 (0,1 % entspricht der G7-Grenze).
d) Lastabhängige Aktoramplitude (Kopplung): Kombinationsläufe × (1 − x), x = 0,1 % und 1 %.
e) Nicht erfasster Jitter zwischen Encoder und Masse (σ_u = 0,2°): Dämpfung e^{−k²σ_u²/2}, nicht in ρ.
f) Konstanter, konfigurationsabhängiger Phasenversatz 0,05° von Modul 2 nur in Kombinationsläufen
   (z. B. lastabhängige Nachgiebigkeit der Übertragung).
Aufruf: python3 s4_identifizierbarkeit.py [a:40,60 | a:120,300 | b]   (Teilläufe wegen Wandzeitbudget)
Ausgabe: s4_identifizierbarkeit_hertz_*.csv, s4_identifizierbarkeit_rest.csv und Text.
"""
import sys
import numpy as np
import pandas as pd
import linear_solver as L
from finesweep import z_egg_zdd

M, G, MG, F = L.M, 9.81, L.MG, 10.0
T = 1.0 / F
MU = 0.4
KMAX = 9
PHI2 = np.arange(100, 140.1, 2.0)
DELTA = dict(F=0.1293, N1=0.1126, N2=0.0731, N3=0.1383)          # s0 (k_max = 9)
UC = {'L0 Sensor+Jitter': dict(F=0.26e-3, N=0.12e-3, c=3.95), 'L2 mech 1 %/0,1°': dict(F=3.3e-3, N=1.7e-3, c=3.95)}
rows = []


def summarize(name, Nk_res, F_res, note=''):
    """Nk_res: 21 × 3 komplex (Residuum N_k, k = 1..3), F_res: 21 (Residuum F_min − ⟨N⟩) in N."""
    r = dict(ursache=name, max_r_F_mN=1e3 * np.abs(F_res).max(), anmerkung=note)
    for kk in range(3):
        r[f'max_r_N{kk + 1}_mN'] = 1e3 * max(np.abs(Nk_res[:, kk].real).max(), np.abs(Nk_res[:, kk].imag).max())
    r['max_r_durch_Delta'] = max(r['max_r_F_mN'] / 1e3 / DELTA['F'],
                                 *[r[f'max_r_N{kk + 1}_mN'] / 1e3 / DELTA[f'N{kk + 1}'] for kk in range(3)])
    for lab, u in UC.items():
        r[f'z_max_{lab}'] = max(r['max_r_F_mN'] / 1e3 / u['F'],
                                max(r[f'max_r_N{kk + 1}_mN'] for kk in range(3)) / 1e3 / u['N'])
    rows.append(r)
    print(f'{name:60s} max|r|: F {r["max_r_F_mN"]:9.4f} mN, N1 {r["max_r_N1_mN"]:8.4f}, N2 {r["max_r_N2_mN"]:8.4f}, '
          f'N3 {r["max_r_N3_mN"]:8.4f} mN | /Δ = {r["max_r_durch_Delta"]:.2e} | z(L0) ≈ {r["z_max_L0 Sensor+Jitter"]:.1f}, '
          f'z(L2) ≈ {r["z_max_L2 mech 1 %/0,1°"]:.1f}  {note}', flush=True)


def harm(x):
    """Harmonische N_k, k = 1..KMAX, eines Zyklus (n Abtastwerte), Konvention (2/n)·Σ x e^{−ikθ}."""
    X = np.fft.rfft(x, axis=-1)
    return 2 * X[..., 1:KMAX + 1] / x.shape[-1]


def curve(Nk, nth=2000):
    th = 2 * np.pi * np.arange(nth) / nth
    kk = np.arange(1, Nk.shape[-1] + 1)
    return Nk.real @ np.cos(np.outer(kk, th)) - Nk.imag @ np.sin(np.outer(kk, th))


def shift(Nk, phi_deg):
    kk = np.arange(1, Nk.shape[-1] + 1)
    return Nk * np.exp(-1j * kk * np.radians(phi_deg))


# ---------- a) Hertz-Kontakt ----------
def simulate(f_n0, zeta, hertz, dt=2.5e-5, t_sim=3.0):
    K0 = M * (2 * np.pi * f_n0) ** 2
    c = 2 * zeta * np.sqrt(K0 * M)
    if hertz:
        d0 = 1.5 * MG / K0
        kap = MG / d0 ** 1.5
    else:
        d0 = MG / K0
    tau = np.concatenate([np.radians(PHI2) / (2 * np.pi * F), [0.0]])             # 21 Kombinationen + 1 Einzelmodul
    tau3 = np.concatenate([np.full(21, np.radians(240.0) / (2 * np.pi * F)), [0.0]])
    single = np.zeros(22, bool)
    single[-1] = True
    nst = int(round(t_sim / dt))
    ncyc = int(round(T / dt))
    d = np.full(22, d0)
    v = np.zeros(22)                                                              # dδ/dt

    def abar(t):
        a1 = z_egg_zdd(np.full(22, t))
        a = (a1 + z_egg_zdd(t - tau) + z_egg_zdd(t - tau3)) / 3
        return np.where(single, a1 / 3, a)

    def force(d, v):
        el = kap * np.clip(d, 0, None) ** 1.5 if hertz else K0 * d
        Fc = el + c * v
        return np.where((d > 0) & (Fc > 0), Fc, 0.0)

    def rhs(d, v, t):
        # Körperkoordinate x = −δ: M·ẍ = −Mg + N − μM·ā  ⇒  δ̈ = g − N/M + μ·ā
        return v, G - force(d, v) / M + MU * abar(t)

    Nrec = np.empty((ncyc, 22))
    for i in range(nst):
        t = i * dt
        if i >= nst - ncyc:
            Nrec[i - (nst - ncyc)] = force(d, v)
        k1d, k1v = rhs(d, v, t)
        k2d, k2v = rhs(d + 0.5 * dt * k1d, v + 0.5 * dt * k1v, t + 0.5 * dt)
        k3d, k3v = rhs(d + 0.5 * dt * k2d, v + 0.5 * dt * k2v, t + 0.5 * dt)
        k4d, k4v = rhs(d + dt * k3d, v + dt * k3v, t + dt)
        d = d + dt * (k1d + 2 * k2d + 2 * k3d + k4d) / 6
        v = v + dt * (k1v + 2 * k2v + 2 * k3v + k4v) / 6
    return Nrec.T                                                                 # 22 × ncyc


TEIL = sys.argv[1] if len(sys.argv) > 1 else 'alles'          # 'a:40,60' = nur Hertz-Teil mit diesen f_n0; 'b' = Rest
FN = [float(v) for v in TEIL.split(':')[1].split(',')] if TEIL.startswith('a:') else (40.0, 60.0, 120.0, 300.0)
for f_n0 in (FN if TEIL != 'b' else ()):
    for hertz in (False, True):
        Ncyc = simulate(f_n0, 0.05, hertz)
        Hk = harm(Ncyc)                                                           # 22 × K
        single = Hk[-1]
        pred = np.stack([single + shift(single, p) + shift(single, 240.0) for p in PHI2])
        meas = Hk[:21]
        Fm = curve(meas).min(1)
        Fp = curve(pred).min(1)
        res_rel = np.abs(meas[:, 2]).max()
        kb = int(np.floor(f_n0 / (2 * F)))                      # k_b = ⌊f₁/(2f)⌋ nach §5.4
        fk = {km: 1e3 * np.abs(curve(meas[:, :km]).min(1) - curve(pred[:, :km]).min(1)).max() for km in (3, 6, 9)}
        summarize(f'a) {"Hertz" if hertz else "linear (Gegenprobe)"} f_n0 = {f_n0:g} Hz, ζ = 0,05', meas[:, :3] - pred[:, :3],
                  Fm - Fp, note=f'N_min = {Ncyc[:21].min():.3f} N, max|N3| = {res_rel:.4f} N; k_b = {kb}; '
                                f'max|r_F| bei k_max = 3/6/9: {fk[3]:.3f}/{fk[6]:.3f}/{fk[9]:.3f} mN')

if TEIL.startswith('a:'):
    pd.DataFrame(rows).to_csv('s4_identifizierbarkeit_hertz_' + TEIL[2:].replace(',', '_') + '.csv', index=False)
    sys.exit(0)
# Wellenformen des linearen A4-Beispiels (starr) für b)–f)
P, NF = L.profile_spectrum()
kk = np.arange(1, KMAX + 1)
Nm = 2 * MU * M * P[1:KMAX + 1] / 3 / NF                                         # Modul, eigener Index
E = np.exp(-1j * np.radians(np.stack([np.zeros(21), PHI2, np.full(21, 240.0)], 1))[:, :, None] * kk)
true = (Nm[None, None, :] * E).sum(1)
Ftrue = curve(true).min(1)

# ---------- b) Zellkennlinie ----------
nth = 4000
th = 2 * np.pi * np.arange(nth) / nth
dmod = np.stack([curve(Nm[None, :] * E[:, j, :], nth) for j in range(3)], 1)      # 21 × 3 × nth, Modul j in Konfig i
for eps_lin, FS in ((2e-4, 10.0), (5e-4, 10.0), (5e-4, 49.0)):
    beta = 4 * eps_lin / FS
    for geo in ('ueber_Zelle', 'zentral'):
        Gm = np.eye(3) if geo == 'ueber_Zelle' else np.full((3, 3), 1 / 3)       # Zelle c erhält Gm[c, j]·d_j
        # Kombination: Zellkraft c = Mg/3 + Σ_j Gm[c,j] d_j
        Nc = MG / 3 + np.einsum('cj,ijt->ict', Gm, dmod)
        meas = (Nc + beta * Nc ** 2).sum(1)
        # Einzelläufe (je Modul j, gleiche Zeitlage wie in der Konfiguration, eigener Index → verschoben):
        pred = np.full((21, nth), 0.0)
        stat = 3 * (MG / 3 + beta * (MG / 3) ** 2)
        for j in range(3):
            Ncj = MG / 3 + Gm[:, j][None, :, None] * dmod[:, j][:, None, :]
            pred += (Ncj + beta * Ncj ** 2).sum(1) - stat
        pred += stat
        Hm, Hp = harm(meas), harm(pred)
        Fm = meas.min(1) - meas.mean(1)
        Fp = pred.min(1) - pred.mean(1)
        summarize(f'b) Zellkennlinie ε_lin = {100 * eps_lin:.2f} % FS, FS = {FS:g} N, {geo}', (Hm - Hp)[:, :3], Fm - Fp)

# ---------- c) Verstärkungsdrift Phase 0 → Phase 1 ----------
for g in (1e-3, 1e-4):
    summarize(f'c) Verstärkung Phase 0 um {100 * g:.2f} % anders (nur gegen ŷ⁰; ŷ¹ folgt)', (true * g)[:, :3], Ftrue * g)

# ---------- d) Kopplung über Aktorlast ----------
for x in (1e-3, 1e-2):
    summarize(f'd) Kombinationsläufe × (1 − {100 * x:.1f} %)', (-true * x)[:, :3], -Ftrue * x)

# ---------- e) nicht erfasster Jitter ----------
su = np.radians(0.2)
damp = np.exp(-0.5 * (kk * su) ** 2)
meas = Nm[None, :] * E[:, 0, :] + (Nm[None, :] * damp * E[:, 1, :]) + (Nm[None, :] * damp * E[:, 2, :])
summarize('e) nicht erfasster Jitter σ_u = 0,2° (Modul 2, 3)', (meas - true)[:, :3], curve(meas).min(1) - Ftrue)

# ---------- f) konfigurationsabhängiger Phasenversatz ----------
meas = Nm[None, :] * E[:, 0, :] + shift(Nm[None, :] * E[:, 1, :], 0.05) + Nm[None, :] * E[:, 2, :]
summarize('f) Phasenversatz 0,05° von Modul 2 nur in Kombinationsläufen', (meas - true)[:, :3], curve(meas).min(1) - Ftrue)

# ---------- g) Größenordnungen ohne Simulation (Annahmen im Protokoll) ----------
v_amp = 2 * 21.7 * 0.035 / np.pi                           # Geschwindigkeitshub der schnellen Phase [m/s]
drag = 0.5 * 1.2 * 1.0 * 1e-3 * (v_amp / 2) ** 2
print(f'\ng) Luftwiderstand je Modul (A = 10 cm², c_w = 1, v ≈ {v_amp/2:.2f} m/s): {1e3*drag:.3f} mN; wirkt je Modul '
      f'einzeln → in Einzelläufen enthalten, H1-Signatur nur über Wechselwirkung (≪ 0,04 mN).')
print(f'   Kabelschlaufe k = 100 N/m bei Körperweg ≤ 1 µm: ≤ {1e3*100*1e-6:.2f} mN, linear → keine H1-Signatur.')
print(f'   Elektrostatik ε0·A·U²/(2d²), A = 10 cm², U = 100 V, d = 1 mm: {1e3*8.85e-12*1e-3*1e4/(2*1e-6):.3f} mN.')
pd.DataFrame(rows).to_csv('s4_identifizierbarkeit.csv' if TEIL == 'alles' else 's4_identifizierbarkeit_rest.csv', index=False)
