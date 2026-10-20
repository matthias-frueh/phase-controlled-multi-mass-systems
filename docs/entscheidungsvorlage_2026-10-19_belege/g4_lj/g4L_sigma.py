# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 2.2 (Option F, kalibriertes Normalmodell).
# Zweck: σ̂_Δ der Gruppen L1–L3 und R über die 120 PR-#22-Kampagnen gegen die Normal-MAD-Theorie; G4 der
#   Nicht-K-Läufe gegen die Vorhersage des Normalmodells bei gegebenem σ̂.
# Eingaben: Argument 1 = g4L_daten.json (Standard: hier; aus g4L_daten.py).
# Seed: default_rng(1). Laufzeit: gemessen 3 s Wandzeit, 3 s CPU (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B g4L_sigma.py > g4L_sigma.out
# Herkunft: Scratch-Ordner vor der Nachprüfung 2 (erste Fassung); von Nachprüfung 2 gelesen, erneut
#   ausgeführt und übernommen. Geändert: Pfad von g4L_daten.json.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
# σ̂_Δ der Einzelmodulgruppen L1–L3 und R über die 120 PR-#22-Kampagnen; Streuung gegen die Normal-MAD-Theorie;
# G4 der Nicht-K-Läufe (75 L + 51 R, statischer Plan) gegen die Vorhersage des Normalmodells bei gegebenem σ̂.
import json, collections, os, sys
import numpy as np
from scipy import stats
D = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'g4L_daten.json')))
d22 = D['d22']
rng = np.random.default_rng(1)
def mad_sim(n, B=200000):
    x = rng.standard_normal((B, n))
    return 1.4826 * np.median(np.abs(x - np.median(x, 1, keepdims=True)), 1)
m20, m61 = mad_sim(20), mad_sim(61)
print('Theorie Normal-MAD: n=20 E=%.3f CV=%.3f; n=61 E=%.3f CV=%.3f' % (m20.mean(), m20.std()/m20.mean(), m61.mean(), m61.std()/m61.mean()))
p_mod20 = (1 - (1 - 2*stats.norm.sf(3*m20[:100000])) * (1 - 2*stats.norm.sf(3*m20[100000:])))
print('Modell b-g4 (n0=20, beide Größen): mittlere Rate je L-Lauf %.3f %%' % (100*p_mod20.mean()))
sysn = ['N01-A4', 'N01-V1G0', 'N01-V1G60h']
for s in sysn:
    rows = [d22[f'{s}|{i}'] for i in range(40)]
    print('\n==', s, 'k_b', rows[0]['k_b'], 'k_max', rows[0]['k_max'])
    for g in ('L1', 'L2', 'L3', 'R', 'K'):
        for x in ('N', 'F'):
            v = np.array([r['sigma_delta'][g][x] for r in rows if r['sigma_delta'][g][x] is not None], float)
            if v.size == 0: continue
            n = rows[0]['sigma_delta'][g]['n']
            print(f'  {g} {x}: n={n} Mittel {1e3*v.mean():.3f} mN, Median {1e3*np.median(v):.3f}, CV {v.std(ddof=1)/v.mean():.3f}, '
                  f'min/max {1e3*v.min():.3f}/{1e3*v.max():.3f}')
    # Vorhersage je Kampagne: wahres σ je Gruppe = Mittel(σ̂)/E[MAD-Faktor] (Normalmodell), Rate aus σ̂/σ
    sig = {}
    for g in ('L1', 'L2', 'L3', 'R'):
        for x in ('N', 'F'):
            v = np.array([r['sigma_delta'][g][x] for r in rows], dtype=object)
            if v[0] is None: continue
            v = v.astype(float)
            sig[(g, x)] = v.mean() / (m20.mean() if g != 'R' else m61.mean())
    obs, pred, predL, predR, g1 = [], [], [], [], []
    for r in rows:
        pL = 0
        for g in ('L1', 'L2', 'L3'):
            qN = 2*stats.norm.sf(3*r['sigma_delta'][g]['N']/sig[(g, 'N')])
            qF = 2*stats.norm.sf(3*r['sigma_delta'][g]['F']/sig[(g, 'F')])
            pL += 25 * (1 - (1-qN)*(1-qF))
        pR = (r['phase1']['sonstige_n'] - 75) * 2*stats.norm.sf(3*r['sigma_delta']['R']['N']/sig[('R', 'N')])
        obs.append(r['phase1']['sonstige_ungueltig']['G4']); predL.append(pL); predR.append(pR); pred.append(pL + pR)
        g1.append(r['phase1']['sonstige_ungueltig']['G1'])
    obs, pred, predL, predR = map(np.array, (obs, pred, predL, predR))
    print(f'  G4 Nicht-K (126 Läufe) beobachtet: Summe {obs.sum()} über 40, Mittel {obs.mean():.2f}, Varianz {obs.var(ddof=1):.2f}, '
          f'Verteilung {sorted(collections.Counter(obs).items())}')
    print(f'  Normalmodell bei gegebenem σ̂ (wahres σ = Mittel σ̂ / E-Faktor): L {predL.sum():.1f}, R {predR.sum():.1f}, '
          f'zusammen {pred.sum():.1f}; Rang-Korrelation beob./vorh. {stats.spearmanr(obs, pred)[0]:.2f} (p={stats.spearmanr(obs, pred)[1]:.2f})')
    print(f'  G1 Nicht-K beobachtet Summe {sum(g1)}; Spearman(G4, G1) {stats.spearmanr(obs, g1)[0]:.2f}')
    print('  erste 10 Kampagnen: beob', obs[:10].tolist(), ' vorh', np.round(pred[:10], 1).tolist())
