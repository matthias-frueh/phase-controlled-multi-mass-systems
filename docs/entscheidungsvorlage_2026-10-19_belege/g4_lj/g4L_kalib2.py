# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 2.2 (Option F) und 3.1 (G4-Halte an Lⱼ).
# Zweck: Ergänzung zu g4L_kalib.py: Test an nicht selektierten Daten, Homogenität, Unsicherheit von κ und
#   der Haltquote, erwartete G4-Halte an Lⱼ in den 30 PR-#23-Kampagnen.
# Eingaben: Argument 1 = g4L_daten.json (Standard: hier; aus g4L_daten.py).
# Seed: default_rng(42). Laufzeit: gemessen 7 s Wandzeit, 7 s CPU (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B g4L_kalib2.py > g4L_kalib2.out
# Herkunft: Nachprüfung 2 (G4 an Lⱼ). Geändert: Pfad von g4L_daten.json.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
# Ergänzung zu g4L_kalib.py: Test des b-g4-Modells an nicht selektierten Daten, Homogenität der Systeme,
# Unsicherheit von κ und der Haltquote, erwartete G4-Halte an Lⱼ in den 30 PR-#23-Kampagnen (Exposition).
import json
import os
import sys
import numpy as np
from scipy import stats, optimize

DATEN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'g4L_daten.json')
D = json.load(open(DATEN)); d22, d23 = D['d22'], D['d23']
rng = np.random.default_rng(42)
c = 1.4826


def mads(n, shape):
    x = rng.standard_normal(tuple(shape) + (n,))
    return c * np.median(np.abs(x - np.median(x, -1, keepdims=True)), -1)


B = 100000
aN, aF, r61 = mads(20, (B, 3)), mads(20, (B, 3)), mads(61, (B,))


def pL(kap, sN=aN, sF=aF):
    return 1 - (1 - 2 * stats.norm.sf(3 * kap * sN)) * (1 - 2 * stats.norm.sf(3 * kap * sF))


# (1) b-g4-Modell (κ = 1) gegen PR #22 V1, statisch, 80 Kampagnen (75 L + 51 R je Kampagne)
lam = 25 * pL(1.0).sum(1) + 51 * 2 * stats.norm.sf(3 * r61)
o = {s: np.array([d22[f'{s}|{i}']['phase1']['sonstige_ungueltig']['G4'] for i in range(40)]) for s in ('N01-V1G0', 'N01-V1G60h')}
S80 = np.array([rng.poisson(rng.choice(lam, 80)).sum() for _ in range(20000)])
ob = o['N01-V1G0'].sum() + o['N01-V1G60h'].sum()
print(f'(1) PR #22 V1 (80 Kampagnen): beobachtet {ob}, Modell κ = 1 Mittel {S80.mean():.1f}, P(≤ beob.) {(S80 <= ob).mean():.3f}, '
      f'P(≥ beob.) {(S80 >= ob).mean():.3f}')
# Homogenität V1G0 gegen V1G60h: Permutationstest der Kampagnensummen
x, y = o['N01-V1G0'], o['N01-V1G60h']
z = np.concatenate([x, y]); d0 = x.sum() - y.sum()
perm = np.array([(lambda p: p[:40].sum() - p[40:].sum())(rng.permutation(z)) for _ in range(20000)])
print(f'    V1G0 {x.sum()} gegen V1G60h {y.sum()}: Permutations-p (zweiseitig) {(np.abs(perm) >= abs(d0)).mean():.3f}')

# (2) Unsicherheit der L-Rate und von κ (V1 gepoolt; R empirisch 0,21 % abgezogen; SE aus Kampagnenstreuung)
qR = 2 / 933
for lab, arr in (('V1 gepoolt', np.concatenate([x, y])), ('N01-V1G0', x), ('N01-V1G60h', y)):
    n = arr.size
    rate = (arr.sum() - n * 51 * qR) / (75 * n)
    se = np.sqrt(arr.var(ddof=1) * n) / (75 * n)
    out = []
    for rr in (rate - 1.96 * se, rate, rate + 1.96 * se):
        k = optimize.brentq(lambda k: pL(k).mean() - rr, 0.4, 3.0)
        p = pL(k)
        halt = 1 - np.prod((1 - p ** 3) ** 25, 1)
        out.append((100 * rr, k, (25 * (p + p ** 2)).sum(1).mean(), 100 * halt.mean()))
    print(f'(2) {lab}: Rate/L [{out[0][0]:.2f}; {out[1][0]:.2f}; {out[2][0]:.2f}] % → κ [{out[2][1]:.3f}; {out[1][1]:.3f}; {out[0][1]:.3f}], '
          f'Wdh./Kampagne [{out[0][2]:.2f}; {out[1][2]:.2f}; {out[2][2]:.2f}], G4-Halt an Lⱼ [{out[0][3]:.2f}; {out[1][3]:.2f}; {out[2][3]:.2f}] %')

# (3) erwartete G4-Halte an Lⱼ in den 30 PR-#23-Kampagnen (Exposition = Kontrollsätze bis zum Ende/Halt), P(0)
keys = sorted(d23)
ks = np.array([d23[k]['ablauf']['rollen'].get('kontrolle', 0) / 4 for k in keys])
for kap in (1.0, 1.003, 0.962, 1.054, 1.144):
    p = pL(kap)[:20000]
    # je Kampagne zufällige σ̂-Ziehung; Halt-Wahrscheinlichkeit 1 − Π_j (1 − p_j³)^Lk
    idx = rng.integers(0, p.shape[0], (5000, ks.size))
    h = 1 - np.prod((1 - p[idx] ** 3) ** ks[None, :, None], -1)
    e = h.sum(1)
    p0 = np.prod(1 - h, 1)
    print(f'(3) κ = {kap:.3f}: erwartete G4-Halte an Lⱼ in den 30 Kampagnen {e.mean():.2f}, P(0 Halte) {p0.mean():.2f}')

# (4) Anteil der Haltwahrscheinlichkeit aus Kampagnen mit kleinem σ̂ (κ = 1): oberstes Zehntel der Rate je Kampagne
p = pL(1.0); halt = 1 - np.prod((1 - p ** 3) ** 25, 1); rm = p.max(1)
top = rm >= np.quantile(rm, 0.9)
print(f'(4) κ = 1: Anteil der Haltwahrscheinlichkeit aus dem Zehntel der Kampagnen mit der höchsten Modulrate: '
      f'{halt[top].sum()/halt.sum():.2f}; dort Rate des ungünstigsten Moduls ≥ {100*np.quantile(rm,0.9):.1f} %')
