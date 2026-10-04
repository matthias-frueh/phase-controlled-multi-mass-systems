"""s1b_rauschbias_triphasik.py – Rauschbias-Bedingung (Präreg §5.4: |b_i| ≤ 0,1·u_c,erw,i) und Verhalten des
Bootstrap-z am Triphasik-Punkt, wo F_min das Minimum dreier (bei identischen Modulen gleich tiefer) Minima ist.

Prüfgruppe statistik, P2. Nur lesend auf Repo-Code.

Modell: A4-Beispiel (starr, μ = 0,4, 10 Hz, k_max = 9), Lauf-Mittelkurven auf Ebene der Harmonischen.
Rauschmodelle je Lauf (Annahmen):
 'weiss'  : weißes Restrauschen, gleich in Einzel- und Kombinationsläufen (sd(Re N_k) = σ_h);
 'modul'  : Amplitudenstreuung je bewegtem Modul (σ_amp), Kombinationslauf trägt drei Module;
 'jitter' : Laufmittel der Phasen von Modul 2, 3 streut um σ_φ/√N_z (nur Kombinationsläufe; Einzelmodulläufe
            sind auf den eigenen Index bezogen und haben diesen Anteil nicht).
Je Modell: b = E[F_min(Messmittel)] − E[F_min(Vorhersage)], u_c,erw = √(Var_Mess + Var_Vorh), Quotient |b|/u_c,erw
für n = 20 und n₀ = 20, 40, 60; dazu Verteilung von z = r/u_Bootstrap (B = 400) am Triphasik-Punkt und
Anteil |z| > c (c = t(1 − 0,05/294; 37) ≈ 3,95) bzw. |z| > 1,96.
"""
import numpy as np
from scipy.stats import t as tdist
import linear_solver as L

rng = np.random.default_rng(11)
KMAX, NTH = 9, 2000
P, NF = L.profile_spectrum()
k = np.arange(1, KMAX + 1)
Nm = 2 * 0.4 * L.M * P[1:KMAX + 1] / 3 / NF
th = 2 * np.pi * np.arange(NTH) / NTH
COS, SIN = np.cos(np.outer(k, th)), np.sin(np.outer(k, th))


def E_of(p2):
    PH = np.radians(np.array([0.0, p2, 240.0]))
    return np.exp(-1j * PH[:, None] * k[None, :])             # 3 × K


def fmin(Nc):
    return (Nc.real @ COS - Nc.imag @ SIN).min(-1)


def runs(model, n, p2, single=None, s=1.0):
    """n Läufe (n × K). single=j: Einzelmodullauf von Modul j (eigener Index, Phase 0)."""
    E = E_of(p2)
    if model == 'weiss':
        sig_h = s
        if single is None:
            base = (Nm[None, :] * E).sum(0)
        else:
            base = Nm
        return base[None, :] + sig_h * (rng.standard_normal((n, KMAX)) + 1j * rng.standard_normal((n, KMAX)))
    if model == 'modul':
        if single is None:
            eps = rng.normal(0, s, (n, 3, 1))
            return (Nm[None, None, :] * (1 + eps) * E[None]).sum(1)
        eps = rng.normal(0, s, (n, 1))
        return Nm[None, :] * (1 + eps)
    if model == 'jitter':
        if single is None:
            dl = np.radians(rng.normal(0, s, (n, 3, 1)))
            dl[:, 0] = 0
            return (Nm[None, None, :] * E[None] * np.exp(-1j * k * dl)).sum(1)
        return np.repeat(Nm[None, :], n, 0)
    raise ValueError


# Rauschstärken so gewählt, dass sd(F_min) eines Kombinationslaufs bei 120° etwa 1 mN beträgt (linear skalierbar)
MODELS = {'weiss': 1e-3 / 3.0, 'modul': 0.003, 'jitter': 0.2 / 10}
print('Rauschbias b = E[F_min(Messmittel)] − E[F_min(Vorhersage)], n = 20 Läufe je Punkt; R = 4000')
for model, s in MODELS.items():
    for p2 in (120.0, 119.0, 118.0, 116.0):
        for n0 in (20, 40, 60):
            R, n = 4000, 20
            fm = np.array([fmin(runs(model, n, p2, s=s).mean(0)) for _ in range(R)])
            mods = [np.array([runs(model, n0, p2, single=j, s=s).mean(0) for _ in range(R)]) for j in range(3)]
            E = E_of(p2)
            pred = sum(mods[j] * E[j][None, :] for j in range(3))
            fp = fmin(pred)
            ftrue = fmin((Nm[None, :] * E).sum(0)[None, :])[0]
            b = fm.mean() - fp.mean()
            u = np.sqrt(fm.var() + fp.var())
            print(f'{model:6s} φ₂={p2:5.1f} n₀={n0}: sd_Mess={1e3*fm.std():.3f} mN sd_Vorh={1e3*fp.std():.3f} mN '
                  f'Bias_Mess={1e3*(fm.mean()-ftrue):+.3f} Bias_Vorh={1e3*(fp.mean()-ftrue):+.3f} '
                  f'b={1e3*b:+.3f} mN u_c,erw={1e3*u:.3f} mN |b|/u={abs(b)/u:.3f} {"VERLETZT" if abs(b) > 0.1*u else "ok"}',
                  flush=True)

print('\nBootstrap-z am Triphasik-Punkt (n = n₀ = 20, B = 400, 2000 Kampagnen)')
c = tdist.ppf(1 - 0.05 / 294, 37)
for model, s in MODELS.items():
    zs = []
    for _ in range(2000):
        Y = runs(model, 20, 120.0, s=s)
        S = [runs(model, 20, 120.0, single=j, s=s) for j in range(3)]
        E = E_of(120.0)
        r = fmin(Y.mean(0)) - fmin(sum(S[j].mean(0) * E[j] for j in range(3)))
        W = rng.multinomial(20, np.full(20, 0.05), size=400) / 20
        vA = fmin(W @ Y).var(ddof=1)
        predb = sum((rng.multinomial(20, np.full(20, 0.05), size=400) / 20 @ S[j]) * E[j] for j in range(3))
        vB = fmin(predb).var(ddof=1)
        zs.append(r / np.sqrt(vA + vB) if vA + vB > 0 else np.nan)
    zs = np.array(zs)
    print(f'{model:6s}: Mittel z = {np.nanmean(zs):+.3f}, sd z = {np.nanstd(zs):.3f}, P(|z|>1,96) = {np.nanmean(np.abs(zs)>1.96):.3f}, '
          f'P(|z|>c={c:.2f}) = {np.nanmean(np.abs(zs)>c):.4f}', flush=True)
