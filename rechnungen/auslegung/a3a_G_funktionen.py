"""
a3a_G_funktionen.py – Aufgabe 3, Teil A: dimensionslose Last- und Signalfunktionen des linearen
Dauerkontaktmodells über ρ = f/f_n und ζ, je Lauftyp.

Im Kontaktast gilt N(t)/(M·g) = 1 + ε·g̃(t; φ, w, ρ, ζ) mit ε = μ·a_h/g (mu_modell.py). Daraus:
  G_i   = −min g̃  (F_min/(Mg) = 1 − ε·G_i)          Gmax_i = max g̃ (F_max/(Mg) = 1 + ε·Gmax_i)
  X_i   = K·max(x_dyn)/(Mg·ε)  (Körperkoordinate: x < 0 ⇔ ε·X_i < 1)
  ΔG    = Spannweite von F_min über die 21 Schnittpunkte / (Mg·ε);  S_L, S_R = 2°-Sekanten an der Spitze / (Mg·ε)
  D_k   = max über den Schnitt |N_k| / (Mg·ε), k = 1, 2, 3 (PB1-Bezugsgröße für Re/Im N_k)
Die Werte hängen nur von (ρ, ζ) und der Profilform ab, nicht von μ, Hub, f, M einzeln (A2 (3)).
Rechnung mit ε_ref (μ = 1, Referenzhub, 10 Hz) und K = M·(2πf/ρ)², C = 2ζ√(KM); ρ = 0: starre Auflage.
Spalten mit Suffix _bl: Schnittgrößen bandbegrenzt auf k ≤ k_b = ⌊1/(2ρ)⌋ (Präreg §5.3 b: nur k·f ≤ f₁/2),
für ρ = 0 bzw. k_b > 50 ohne Begrenzung; zusätzlich Spalten _k3 (k_max = 3).
Ausgabe: a3a_G_funktionen.csv. Laufzeit ca. 1 min.
"""
import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mu_modell as mm  # noqa: E402

M, G, MG = mm.M_REF, mm.G, mm.M_REF * mm.G
f0, H0 = 10.0, mm.HUB_REF
EPS = mm.eps_of(1.0, H0, f0)
N_FFT, N_S = 16000, 2000
NK = N_FFT // 2 + 1
c = mm.profile_coeffs(NK, H0, f0)

RT = mm.run_types(pair_step=5.0)
names = [r[0] for r in RT]
groups = np.array([r[1] for r in RT])
PHI = np.array([mm.phase_factor(r[2], r[3], NK) for r in RT])       # (nrun, NK)
sec_idx = np.where(groups == 'schnitt')[0]


def evaluate(rho, zeta):
    if rho == 0:
        K, C = None, 0.0
    else:
        K = mm.K_of_rho(rho, f0)
        C = mm.C_of_zeta(zeta, K)
    H, Y = mm.transfer(K, C, f0, NK)
    F1 = (M / 3.0) * H * c                     # Einzelmodul, μ = 1
    X1 = (M / 3.0) * Y * c
    Fk = PHI * F1[None, :]
    N = np.fft.irfft(Fk * N_FFT, N_FFT, axis=1)[:, ::N_FFT // N_S]   # N − Mg
    res = {}
    Gi = -N.min(1) / (MG * EPS)
    Gmax = N.max(1) / (MG * EPS)
    if K is not None:
        x = np.fft.irfft(PHI * X1[None, :] * N_FFT, N_FFT, axis=1)[:, ::N_FFT // N_S]
        Xi = K * x.max(1) / (MG * EPS)
    else:
        Xi = np.zeros(len(RT))
    for g in ('einzel', 'paar', 'synchron', 'zweiergruppe', 'pilot', 'schnitt'):
        m = groups == g
        j = np.argmax(Gi[m])
        res[f'G_{g}'] = Gi[m][j]
        res[f'Gmax_{g}'] = Gmax[m].max()
        res[f'X_{g}'] = Xi[m].max()
        if g == 'paar':
            res['paar_worst'] = names[np.where(m)[0][j]]
    # Schnittgrößen, volles Spektrum und bandbegrenzt
    kb = int(np.floor(1.0 / (2 * rho))) if rho > 0 else 10**9
    for suf, kmax in (('', None), ('_bl', kb if kb <= 50 else None), ('_k3', 3)):
        if kmax is None:
            Ns = N[sec_idx]
        else:
            Fb = Fk[sec_idx].copy()
            Fb[:, kmax + 1:] = 0.0
            Ns = np.fft.irfft(Fb * N_FFT, N_FFT, axis=1)[:, ::N_FFT // N_S]
        fmin = Ns.min(1) / (MG * EPS)            # (F_min − Mg)/(Mg ε)
        j = int(np.argmax(fmin))
        res[f'dG{suf}'] = fmin.max() - fmin.min()
        res[f'peak{suf}'] = mm.SECTION_PHI2[j]
        res[f'G120{suf}'] = -fmin[10]
        res[f'SL{suf}'] = (fmin[10] - fmin[9]) / 2
        res[f'SR{suf}'] = (fmin[10] - fmin[11]) / 2
    res['kb'] = kb if rho > 0 else -1
    for k in (1, 2, 3):
        res[f'D{k}'] = np.abs(2 * Fk[sec_idx, k]).max() / (MG * EPS)
    absH = np.abs(H)
    res['Hmax_k_le_kb'] = absH[1:min(kb, 60) + 1].max() if rho > 0 else 1.0
    res['Hmax_all'] = absH[1:].max()
    return res


rows = []
rhos = np.concatenate([[0.0], np.round(np.arange(0.01, 0.3001, 0.001), 4)])
for zeta in (0.02, 0.05, 0.1, 0.2):
    for rho in rhos:
        r = evaluate(float(rho), zeta)
        r.update(rho=float(rho), zeta=zeta)
        rows.append(r)
df = pd.DataFrame(rows)
df.to_csv(os.path.join(HERE, 'a3a_G_funktionen.csv'), index=False, float_format='%.6g')
print(f'{len(df)} Zeilen geschrieben; ε_ref = {EPS:.5f}')
cols = ['G_einzel', 'G_paar', 'G_synchron', 'G_zweiergruppe', 'G_pilot', 'G_schnitt', 'dG', 'dG_bl', 'dG_k3',
        'SL', 'SR', 'peak', 'D1', 'D2', 'D3', 'X_synchron']
print(df[df.rho == 0].iloc[0][cols].to_string())
for zeta in (0.02, 0.1):
    sub = df[(df.zeta == zeta) & (df.rho.isin([0.05, 0.08, 0.1, 0.111, 0.125, 0.143, 0.1667, 0.2]))]
    print(f'ζ = {zeta}')
    print(sub[['rho'] + cols].to_string(index=False, float_format=lambda v: f'{v:.4f}'))
