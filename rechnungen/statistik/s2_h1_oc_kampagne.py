"""s2_h1_oc_kampagne.py – Operating Characteristic der H1-Entscheidungsregel (Präreg v2 §8.2–§8.5, §9.3, A8)
auf Kampagnenebene, mit Bootstrap-u_c, Welch–Satterthwaite-ν, Bonferroni-c, PB1 und ŷ⁰/ŷ¹.

Prüfgruppe statistik, P2. Nur lesend auf Repo-Code (linear_solver.py).

Modell (eigene Annahmen):
- Beispiel A4: starre Auflage, μ = 0,4, f = 10 Hz, identische Egg-Module, Bandbegrenzung k_max (Standard 9).
  Jeder Lauf ist durch seine Mittelkurve (Harmonische k = 1 … k_max) dargestellt.
- Laufrauschen: (i) weißes Restrauschen der Mittelkurve, sd(Re N_k) = sd(Im N_k) = σ_h je Lauf (aus s1:
  σ = 20 mN, f_s = 6,4 kHz, T_a = 10 s ergibt 0,11 mN); (ii) mechanische Lauf-zu-Lauf-Streuung je bewegtem
  Modul: Amplitudenfaktor (1 + ε), ε ~ N(0, σ_amp²), und nicht vom Encoder erfasster Phasenversatz
  δ ~ N(0, σ_ph²). Kombinationsläufe tragen die Streuung aller drei Module, Einzelmodulläufe nur die eigene.
  Gemessene Zeiger ρ = Sollphasen (Jitter ist über ρ exakt berücksichtigt, A2.4; nur der Rest in δ).
- Phase 0: n₀ Einzelmodulläufe je Modul (ŷ⁰); Phase 1: n₁ = 21 Kontrollläufe je Modul (ŷ¹, 20 Blöcke);
  21 Schnittpunkte mit je n Läufen.
- Abweichungsszenarien (Wahrheit der Kombinationsläufe): 'exakt'; 'kopplung' x: alle Harmonischen der
  Kombinationsläufe × (1 − x) (z. B. lastabhängige Aktoramplitude); 'N2' x: nur k = 2 × (1 + x);
  'drift' x: Superposition exakt, aber die Einzelmodulantwort der Phase 0 ist um den Faktor (1 + x) größer
  als in Phase 1 (Drift zwischen den Phasen; Kombinations- und Phase-1-Kontrollläufe gleich).
Verfahren wie registriert: r = ȳ − ŷ; Var_A, Var_B aus Bootstrap (B Replikate, statt 10 000), u_c² = Var_A + Var_B;
ν_eff nach §8.3; c = t(1 − 0,05/294; ν_eff); Δ_q = 0,25·D_q aus ŷ⁰; Entscheidung §9.3.
Zusätzlich (Vorschläge, nicht registriert): 'IUT' = Bestätigung nur über TOST je Test mit t(0,95; ν) gegen ŷ⁰ und
ŷ¹, ohne Signifikanzbedingung; 'MET' = Falsifikation nur, wenn |r| − c·u > Δ_q gegen ŷ⁰ und ŷ¹ (Mindesteffekt).
Aufruf: python3 s2_h1_oc_kampagne.py LEVEL [NKAMP] [N] [N0] [KMAX] [SZENARIEN, z. B. 0,8]
        → s2_h1_oc_L<LEVEL>_n<N>_n0<N0>_k<KMAX>.csv (nach jedem Szenario geschrieben)
"""
import sys
import time
import numpy as np
import pandas as pd
from scipy.stats import t as tdist
import linear_solver as L

LEVELS = {  # Bezeichnung: (σ_h [N], σ_amp [–], σ_ph [°])
    0: ('Sensor+Jitter', 0.11e-3, 0.0, 0.02),
    1: ('mech 0,3 % / 0,03°', 0.11e-3, 0.003, 0.03),
    2: ('mech 1 % / 0,1°', 0.11e-3, 0.01, 0.10),
    3: ('mech 3 % / 0,3°', 0.11e-3, 0.03, 0.30),
    4: ('mech 6 % / 0,6°', 0.11e-3, 0.06, 0.60),
    5: ('mech 10 % / 1,0°', 0.11e-3, 0.10, 1.00),
    6: ('mech 20 % / 2,0°', 0.11e-3, 0.20, 2.00),
}
lev = int(sys.argv[1])
NKAMP = int(sys.argv[2]) if len(sys.argv) > 2 else 300
N = int(sys.argv[3]) if len(sys.argv) > 3 else 20
N0 = int(sys.argv[4]) if len(sys.argv) > 4 else 20
KMAX = int(sys.argv[5]) if len(sys.argv) > 5 else 9
N1 = 21
B = 200
ALPHA, MTEST = 0.05, 147
NTH = 2000
SCEN_ALL = [('exakt', 0.0), ('kopplung', 0.01), ('kopplung', 0.03), ('kopplung', 0.10),
        ('N2', 0.01), ('N2', 0.03), ('N2', 0.10), ('drift', 0.01), ('drift', 0.03),
        ('kopplung', 0.20), ('kopplung', 0.30)]
SCEN = SCEN_ALL[:9] if len(sys.argv) <= 6 else [SCEN_ALL[int(i)] for i in sys.argv[6].split(',')]   # Standard: 9 Szenarien wie in run_s2.sh
label, SIG_H, SIG_AMP, SIG_PH = LEVELS[lev]
rng = np.random.default_rng(1000 + lev)

MU, M = 0.4, L.M
P, NF = L.profile_spectrum()
k = np.arange(1, KMAX + 1)
Nk_mod = 2 * MU * M * P[1:KMAX + 1] / 3 / NF          # komplexe N_k eines Moduls (eigener Index), starr
phi2 = np.arange(100, 140.1, 2.0)
PHI = np.radians(np.stack([np.zeros_like(phi2), phi2, np.full_like(phi2, 240.0)], 1))   # 21 × 3
E = np.exp(-1j * PHI[:, :, None] * k[None, None, :])                                      # 21 × 3 × K
th = 2 * np.pi * np.arange(NTH) / NTH
COS, SIN = np.cos(np.outer(k, th)), np.sin(np.outer(k, th))                                # K × G


def curve_min(Nc, mask):
    """F_min − ⟨N⟩ der Kurve Σ Re(N_k e^{ikθ}) auf den Stützstellen in mask; Nc (..., K)."""
    return (Nc.real @ COS[:, mask] - Nc.imag @ SIN[:, mask]).min(-1)


def qvec(Nc, mask):
    """7 Größen: F_min − ⟨N⟩, Re/Im N_1..N_3."""
    out = [curve_min(Nc, mask)]
    for kk in range(3):
        out += [Nc[..., kk].real, Nc[..., kk].imag]
    return np.stack(out, -1)


# Stützstellenmasken je Schnittpunkt (wahre Kurven innerhalb 0,3 N über dem Minimum, inkl. Abweichungen)
masks = []
for i in range(21):
    Ni = (Nk_mod[None, :] * E[i]).sum(0)
    cv = Ni.real @ COS - Ni.imag @ SIN
    m = cv < cv.min() + 0.3
    for g in (0.9, 1.1):
        cv2 = (Ni * g).real @ COS - (Ni * g).imag @ SIN
        m |= cv2 < cv2.min() + 0.3
    masks.append(m)


def single_runs(n):
    """n Einzelmodulläufe je Modul: Array 3 × n × K."""
    eps = rng.normal(0, SIG_AMP, (3, n, 1))
    dl = np.radians(rng.normal(0, SIG_PH, (3, n, 1)))
    w = SIG_H * (rng.standard_normal((3, n, KMAX)) + 1j * rng.standard_normal((3, n, KMAX)))
    return Nk_mod[None, None, :] * (1 + eps) * np.exp(-1j * k * dl) + w


def comb_runs(n, gfac):
    """n Läufe an jedem der 21 Punkte: 21 × n × K; gfac (K,) = Abweichungsfaktor der Kombinationsläufe."""
    eps = rng.normal(0, SIG_AMP, (21, n, 3, 1))
    dl = np.radians(rng.normal(0, SIG_PH, (21, n, 3, 1)))
    mods = Nk_mod * (1 + eps) * np.exp(-1j * k * dl) * E[:, None, :, :]
    w = SIG_H * (rng.standard_normal((21, n, KMAX)) + 1j * rng.standard_normal((21, n, KMAX)))
    return mods.sum(2) * gfac + w


def boot_var_mean(X, nb):
    """Bootstrap-Mittel über Achse 1 (Läufe): X (G, n, K) → (G, nb, K)."""
    n = X.shape[1]
    W = rng.multinomial(n, np.full(n, 1.0 / n), size=(X.shape[0], nb)) / n   # G × nb × n
    return np.einsum('gbn,gnk->gbk', W, X)


def campaign(gfac, drift=0.0):
    S0, S1 = single_runs(N0) * (1 + drift), single_runs(N1)
    Y = comb_runs(N, gfac)
    Ybar, A0, A1 = Y.mean(1), S0.mean(1), S1.mean(1)
    yh0 = np.einsum('jk,ijk->ik', A0, E)
    yh1 = np.einsum('jk,ijk->ik', A1, E)
    # Bootstrap
    Yb = boot_var_mean(Y, B)                       # 21 × B × K
    S0b, S1b = boot_var_mean(S0, B), boot_var_mean(S1, B)      # 3 × B × K
    yh0b = np.einsum('jbk,ijk->ibk', S0b, E)
    yh1b = np.einsum('jbk,ijk->ibk', S1b, E)
    q_meas, q0, q1 = np.empty((21, 7)), np.empty((21, 7)), np.empty((21, 7))
    vA, vB0, vB1 = np.empty((21, 7)), np.empty((21, 7)), np.empty((21, 7))
    for i in range(21):
        m = masks[i]
        q_meas[i] = qvec(Ybar[i], m)
        q0[i], q1[i] = qvec(yh0[i], m), qvec(yh1[i], m)
        vA[i] = qvec(Yb[i], m).var(0, ddof=1)
        vB0[i] = qvec(yh0b[i], m).var(0, ddof=1)
        vB1[i] = qvec(yh1b[i], m).var(0, ddof=1)
    r0, r1 = q_meas - q0, q_meas - q1
    u0, u1 = np.sqrt(vA + vB0), np.sqrt(vA + vB1)
    nu0 = u0 ** 4 / (vA ** 2 / (N - 1) + vB0 ** 2 / (N0 - 1))
    nu1 = u1 ** 4 / (vA ** 2 / (N - 1) + vB1 ** 2 / (N1 - 1))
    c0 = tdist.ppf(1 - ALPHA / (2 * MTEST), nu0)
    c1 = tdist.ppf(1 - ALPHA / (2 * MTEST), nu1)
    z0, z1 = r0 / u0, r1 / u1
    D = np.empty(7)
    D[0] = q0[:, 0].max() - q0[:, 0].min()
    for kk in range(3):
        D[1 + 2 * kk] = D[2 + 2 * kk] = np.abs(yh0[:, kk]).max() * 2 / 2   # |N̂_k| (N_k-Konvention)
    Dl = 0.25 * D[None, :]
    sig0, sig1 = np.abs(z0) > c0, np.abs(z1) > c1
    fals = np.any(sig0 & sig1 & (np.sign(z0) == np.sign(z1)))
    pb1 = np.all(np.abs(r0) + c0 * u0 <= Dl)
    conf = (not sig0.any()) and (not sig1.any()) and pb1
    # Vorschläge
    ce0, ce1 = tdist.ppf(0.95, nu0), tdist.ppf(0.95, nu1)
    iut = np.all(np.abs(r0) + ce0 * u0 <= Dl) and np.all(np.abs(r1) + ce1 * u1 <= Dl)
    met = np.any((np.abs(r0) - c0 * u0 > Dl) & (np.abs(r1) - c1 * u1 > Dl) & (np.sign(r0) == np.sign(r1)))
    return dict(fals=fals, conf=conf, pb1=pb1, sig0=sig0.any(), sig1=sig1.any(), iut=iut, met=met,
                maxz0=np.abs(z0).max(), corr01=np.corrcoef(z0.ravel(), z1.ravel())[0, 1],
                u_F=np.median(u0[:, 0]), u_N1=np.median(u0[:, 1:3]), u_N2=np.median(u0[:, 3:5]),
                u_N3=np.median(u0[:, 5:7]), nu_F=np.median(nu0[:, 0]), Delta_F=Dl[0, 0], Delta_N2=Dl[0, 3],
                r0_F_max=np.abs(r0[:, 0]).max(), r0_N2_max=np.abs(r0[:, 3:5]).max(),
                pb1_ratio=np.max((np.abs(r0) + c0 * u0) / Dl))


rows = []
t0 = time.time()
for name, x in SCEN:
    g = np.ones(KMAX)
    if name == 'kopplung':
        g[:] = 1 - x
    elif name == 'N2':
        g[1] = 1 + x
    res = [campaign(g, x if name == 'drift' else 0.0) for _ in range(NKAMP)]
    d = pd.DataFrame(res)
    row = dict(level=lev, rauschen=label, sig_h_mN=1e3 * SIG_H, sig_amp=SIG_AMP, sig_ph_deg=SIG_PH, n=N, n0=N0,
               n1=N1, kmax=KMAX, szenario=name, x=x, nkamp=NKAMP,
               P_falsifiziert=d.fals.mean(), P_bestaetigt=d.conf.mean(),
               P_nicht_entscheidbar=1 - d.fals.mean() - d.conf.mean(), P_PB1=d.pb1.mean(),
               P_sig_z0=d.sig0.mean(), P_sig_z1=d.sig1.mean(), P_IUT_bestaetigt=d.iut.mean(),
               P_MET_falsifiziert=d.met.mean(), q95_maxz0=d.maxz0.quantile(0.95),
               corr_z0_z1=d.corr01.mean(), u_F_mN=1e3 * d.u_F.median(), u_N1_mN=1e3 * d.u_N1.median(),
               u_N2_mN=1e3 * d.u_N2.median(), u_N3_mN=1e3 * d.u_N3.median(), nu_F=d.nu_F.median(),
               Delta_F_mN=1e3 * d.Delta_F.median(), Delta_N2_mN=1e3 * d.Delta_N2.median(),
               max_r0_F_mN=1e3 * d.r0_F_max.median(), max_r0_N2_mN=1e3 * d.r0_N2_max.median(),
               pb1_quotient_median=d.pb1_ratio.median())
    rows.append(row)
    print(f'[{time.time() - t0:6.1f} s] L{lev} {label:22s} {name:8s} x={x:4.2f}: '
          f'P(fals)={row["P_falsifiziert"]:.3f} P(best)={row["P_bestaetigt"]:.3f} P(PB1)={row["P_PB1"]:.3f} '
          f'P(IUT)={row["P_IUT_bestaetigt"]:.3f} P(MET)={row["P_MET_falsifiziert"]:.3f} '
          f'u_F={row["u_F_mN"]:.2f} u_N2={row["u_N2_mN"]:.2f} mN nu_F={row["nu_F"]:.1f} '
          f'q95max|z0|={row["q95_maxz0"]:.2f} corr={row["corr_z0_z1"]:.2f}', flush=True)
    tag = '' if len(sys.argv) <= 6 else '_s' + sys.argv[6].replace(',', '-')
    pd.DataFrame(rows).to_csv(f's2_h1_oc_L{lev}_n{N}_n0{N0}_k{KMAX}{tag}.csv', index=False)   # nach jedem Szenario
