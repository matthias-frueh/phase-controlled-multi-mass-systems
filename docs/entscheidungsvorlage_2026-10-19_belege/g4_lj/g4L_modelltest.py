# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 2.2 (Option F) und 3.1 (G4-Halte an Lⱼ).
# Zweck: Modell b-g4 (σ̂ je Modul aus n₀ = 20, D_N und D_F unabhängig normal) gegen PR #23 (G4-Kontroll-
#   wiederholungen) und PR #22 (G4 der Nicht-K-Läufe), auch bedingt auf die tatsächlichen σ̂.
# Eingaben: Argument 1 = g4L_daten.json (Standard: hier; aus g4L_daten.py).
# Seed: default_rng(20261019). Laufzeit: gemessen 41 s Wandzeit, 40 s CPU (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B g4L_modelltest.py > g4L_modelltest.out
# Herkunft: Scratch-Ordner vor der Nachprüfung 2 (erste Fassung); von Nachprüfung 2 gelesen, erneut
#   ausgeführt und übernommen. Geändert: Pfad von g4L_daten.json.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
# Modell b-g4 (σ̂ je Modul aus n₀ = 20, D_N und D_F unabhängig normal; R: D_N, σ̂ aus 61) gegen
# (a) PR #23: G4-Kontrollwiederholungen aller 30 Kampagnen mit tatsächlicher Exposition (auch angehaltene)
# (b) PR #22: G4 der 126 Nicht-K-Läufe im statischen Plan (je System 40 Kampagnen; A4 dort k-inkonsistent)
# (c) bedingt auf die tatsächlichen σ̂ (V1; Phase 0 in PR #22 und #23 gleich): erwartete Wiederholungen in PR #23
import json
import os
import sys
import numpy as np
from scipy import stats
DATEN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'g4L_daten.json')
D = json.load(open(DATEN)); d22, d23 = D['d22'], D['d23']
rng = np.random.default_rng(20261019)
c = 1.4826
def mads(n, shape):
    x = rng.standard_normal(shape + (n,))
    return c * np.median(np.abs(x - np.median(x, -1, keepdims=True)), -1)
B = 20000
def sim_kampagnen(nL, nR, B):
    """nL: (C,) L-Läufe je Modul (geplante Kontrollläufe), nR: (C,) Kontroll-R; Rückgabe Wiederholungen (B, C)"""
    C = len(nL)
    a = mads(20, (B, C, 3)); b = mads(20, (B, C, 3)); r = mads(61, (B, C))
    p = 1 - (1 - 2 * stats.norm.sf(3 * a)) * (1 - 2 * stats.norm.sf(3 * b))
    q = 2 * stats.norm.sf(3 * r)
    w1 = rng.binomial(np.broadcast_to(np.asarray(nL)[None, :, None], p.shape), p)
    w2 = rng.binomial(w1, p)
    wr1 = rng.binomial(np.broadcast_to(np.asarray(nR)[None, :], q.shape), q)
    wr2 = rng.binomial(wr1, q)
    return (w1 + w2).sum(-1), wr1 + wr2, p
keys = sorted(d23, key=lambda s: (s.split('|')[0], int(s.split('|')[1])))
obs = np.array([sum(v for k, v in d23[k]['ablauf']['anlaesse'].items() if k.startswith('kontrollwiederholung') and 'G4' in k) for k in keys])
kontrolle = np.array([d23[k]['ablauf']['rollen'].get('kontrolle', 0) for k in keys])
fertig = np.array([d23[k]['ablauf']['status'] == 'abgeschlossen' for k in keys])
nL = np.round(kontrolle * 3 / 4 / 3).astype(int); nR = np.round(kontrolle / 4).astype(int)
wL, wR, p = sim_kampagnen(nL, nR, B)
tot = wL + wR
print('(a) PR #23, Modell b-g4, Exposition aus rollen.kontrolle (L je Modul = kontrolle/4):')
print(f'    alle 30: beobachtet {obs.sum()}, Modell Mittel {tot.sum(1).mean():.1f} (davon Kontroll-R {wR.sum(1).mean():.2f}), '
      f'5-%-Quantil {np.quantile(tot.sum(1), 0.05):.0f}, P(≤ beob.) = {(tot.sum(1) <= obs.sum()).mean():.4f}')
print(f'    25 abgeschlossene: beobachtet {obs[fertig].sum()}, Modell Mittel {tot[:, fertig].sum(1).mean():.1f}, '
      f'P(≤ beob.) = {(tot[:, fertig].sum(1) <= obs[fertig].sum()).mean():.4f}')
print(f'    5 angehaltene: beobachtet {obs[~fertig].sum()} bei {kontrolle[~fertig].sum()} Kontrollläufen, Modell Mittel {tot[:, ~fertig].sum(1).mean():.1f}, '
      f'P(≥ beob.) = {(tot[:, ~fertig].sum(1) >= obs[~fertig].sum()).mean():.3f}')
for s in ('N01-A4', 'N01-V1G0', 'N01-V1G60h'):
    m = np.array([k.startswith(s + '|') for k in keys])
    print(f'    {s}: beob. {obs[m].sum()}, Modell Mittel {tot[:, m].sum(1).mean():.1f}, P(≤ beob.) {(tot[:, m].sum(1) <= obs[m].sum()).mean():.3f}')
# Kampagnenstreuung im Modell: Wiederholungen je vollständiger Kampagne
w1c, wr1c, _ = sim_kampagnen(np.array([25]), np.array([25]), 100000)
x = (w1c + wr1c)[:, 0]
print(f'    Modell je vollständiger Kampagne: Mittel {x.mean():.2f}, Varianz {x.var():.2f}, P(0) {np.mean(x == 0):.3f}, P(≥5) {np.mean(x >= 5):.3f}')
print(f'    beobachtet (25 abgeschlossene): Mittel {obs[fertig].mean():.2f}, Varianz {obs[fertig].var(ddof=1):.2f}, '
      f'Anteil 0 {np.mean(obs[fertig] == 0):.3f}, max {obs[fertig].max()}')
print()
print('(b) PR #22, statischer Plan, G4 der 126 Nicht-K-Läufe (75 L + 51 R) je Kampagne, je System 40 Kampagnen:')
wLs, wRs, _ = sim_kampagnen(np.full(40, 25), np.full(40, 51), B)
# im statischen Plan keine Wiederholung: nur erste Stufe zählen → eigene Ziehung ohne w2
a = mads(20, (B, 40, 3)); b_ = mads(20, (B, 40, 3)); r = mads(61, (B, 40))
pS = 1 - (1 - 2 * stats.norm.sf(3 * a)) * (1 - 2 * stats.norm.sf(3 * b_)); qS = 2 * stats.norm.sf(3 * r)
st = rng.binomial(25, pS).sum(-1) + rng.binomial(51, qS)
for s in ('N01-A4', 'N01-V1G0', 'N01-V1G60h'):
    o = np.array([d22[f'{s}|{i}']['phase1']['sonstige_ungueltig']['G4'] for i in range(40)])
    S = st.sum(1)
    print(f'    {s}: beobachtet {o.sum()} (Mittel {o.mean():.2f}, Var {o.var(ddof=1):.2f}); Modell Mittel {S.mean():.1f}, '
          f'90-%-Bereich [{np.quantile(S, 0.05):.0f}; {np.quantile(S, 0.95):.0f}], P(≤ beob.) {(S <= o.sum()).mean():.3f}; '
          f'Modell je Kampagne Var {st.var(1).mean():.2f}')
print()
print('(c) bedingt auf die tatsächlichen σ̂ (PR-#22-Phase-0 = PR-#23-Phase-0), wahres σ = Mittel σ̂ über 40 / 0,958 bzw. 0,987:')
for s in ('N01-V1G0', 'N01-V1G60h', 'N01-A4'):
    rows = [d22[f'{s}|{i}'] for i in range(40)]
    sig = {(g, x): np.mean([r['sigma_delta'][g][x] for r in rows]) / (0.958 if g != 'R' else 0.987)
           for g in ('L1', 'L2', 'L3', 'R') for x in ('N', 'F') if rows[0]['sigma_delta'][g][x] is not None}
    e_all, e_fertig, o_all, o_fertig = 0, 0, 0, 0
    for k in keys:
        if not k.startswith(s + '|'): continue
        r = d22[k]; b = d23[k]
        nl = b['ablauf']['rollen'].get('kontrolle', 0) / 4
        e = 0
        for g in ('L1', 'L2', 'L3'):
            qN = 2 * stats.norm.sf(3 * r['sigma_delta'][g]['N'] / sig[(g, 'N')])
            qF = 2 * stats.norm.sf(3 * r['sigma_delta'][g]['F'] / sig[(g, 'F')])
            pj = 1 - (1 - qN) * (1 - qF)
            e += nl * pj * (1 + pj)
        qR = 2 * stats.norm.sf(3 * r['sigma_delta']['R']['N'] / sig[('R', 'N')])
        e += nl * qR * (1 + qR)
        o = sum(v for kk, v in b['ablauf']['anlaesse'].items() if kk.startswith('kontrollwiederholung') and 'G4' in kk)
        e_all += e; o_all += o
        if b['ablauf']['status'] == 'abgeschlossen': e_fertig += e; o_fertig += o
    hinweis = ' (A4: σ̂_F,L in PR #22 bei k = 30, in PR #23 bei k = 9 – nicht übertragbar)' if s == 'N01-A4' else ''
    print(f'    {s}: alle 10: beob. {o_all}, erwartet {e_all:.1f}, Poisson-P(≤ beob.) {stats.poisson.cdf(o_all, e_all):.3f}; '
          f'abgeschlossene: beob. {o_fertig}, erwartet {e_fertig:.1f}, P(≤) {stats.poisson.cdf(o_fertig, e_fertig):.3f}{hinweis}')
