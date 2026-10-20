# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 3.1.
# Zweck: beobachtete G1, R₁, X′ der 30 Kampagnen gegen das Teststatistikmodell bei ihrem u; Nullverteilung von
#   Spearman(ε, G1) über 30 Kampagnen; KS-Test der u-Verteilung.
# Eingaben: Argument 1 = dieser Ordner (gitter.json, eps_tabelle.csv, phase0.py), Argument 2 =
#   Verzeichnis mit den Checkpoint-Ordnern korr-N01-{A4,V1G0,V1G60h}-wiederholungen/ der Korrekturrunde von PR #23
#   (flüchtig, am 18.10.2026 unter /tmp/pcmms-ablauf-vergleich-20261018/ erzeugt; SHA-256 der ablauf_*.json in
#   docs/ap13_kmax_wiederholungen_2026-10-17/ergebnisse.json, Schlüssel "checkpoints")
# Seed: default_rng(3) (200 000 Phase-0-Datensätze, 4000 Modellstichproben). Laufzeit: gemessen 8 s Wandzeit, 8 s CPU (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -B vergleich.py . <checkpoint-basis> > vergleich.out
# Herkunft: Nachprüfung 1. Geändert: Checkpoint-Pfad als Argument 2 (vorher fest).
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""Beobachtet (30 Checkpoint-Kampagnen) gegen das Teststatistik-Modell bei gegebenem u = ε/(3·√1,5·σ)."""
import sys, json, csv
import numpy as np
from scipy import stats
d = json.load(open(sys.argv[1] + '/gitter.json'))
F = d['felder']; us = np.array([float(u) for u in d['gitter']])
M = np.array([d['gitter'][k]['mittel'] for k in d['gitter']]); V = np.array([d['gitter'][k]['var'] for k in d['gitter']])
def erw(name, u):
    j = F.index(name)
    return np.exp(np.interp(u, us, np.log(np.maximum(M[:, j], 1e-6))))
print('Dispersion (Var/Mittel) je u für G1, R1, Xs:')
for i in range(0, len(us), 4):
    print(' u', us[i], [round(V[i, F.index(x)] / max(M[i, F.index(x)], 1e-9), 2) for x in ('G1', 'R1', 'Xs', 'alarm')])
rows = list(csv.DictReader(open(sys.argv[1] + '/eps_tabelle.csv')))
BAS = sys.argv[2]                       # flüchtige Checkpoints (Kopf)
konf = {}
for a in ('A4', 'V1G0', 'V1G60h'):
    j = json.load(open(f'{BAS}/korr-N01-{a}-wiederholungen/ablauf_korr-N01-{a}-wiederholungen.json'))
    for b in j['inhalt']['befunde']:
        konf[(b['szenario'], b['index'])] = b['ablauf']['rollen'].get('konfiguration', 0)
u = np.array([float(r['u']) for r in rows])
f = np.array([konf[(r['szenario'], int(r['index']))] / 504 for r in rows])
obs = {k: np.array([float(r[k]) for r in rows]) for k in ('G1', 'R1', 'X_strich', 'alarmwdh')}
for name, o in (('G1', obs['G1']), ('R1', obs['R1']), ('Xs', obs['X_strich'])):
    e = f * erw(name, u)
    chi = ((o - e) ** 2 / np.maximum(e, 1e-9)).sum()
    print(f'{name}: beobachtet {o.sum():.0f}, erwartet {e.sum():.1f}; Pearson-χ² {chi:.1f} (30 Kampagnen)')
    # mit u = 1 für alle (homogen): erwartet
    e1 = f * erw(name, np.ones_like(u))
    print(f'   homogen (u = 1): erwartet {e1.sum():.1f}; mit u_i: Spearman(e_i, o_i) = {stats.spearmanr(e, o).statistic:.2f}')
i2 = [i for i, r in enumerate(rows) if r['szenario'] == 'N01-V1G0' and r['index'] == '2'][0]
for name, k in (('G1', 'G1'), ('R1', 'R1'), ('Xs', 'X_strich')):
    print(f'V1G0 Nr. 2 (u = {u[i2]}): {name} beob. {obs[k][i2]:.0f}, erw. {f[i2] * erw(name, u[i2:i2+1])[0]:.1f}')
# Nullverteilung der Rangkorrelation ε~G1 über 30 Kampagnen im Modell (u aus Phase-0-Modell mit F-Test, G1 ~ NB/Poisson)
sys.path.insert(0, sys.argv[1]); import phase0 as p0
rng = np.random.default_rng(3)
o0 = p0.simuliere(200000, rng, 61, 2, True, krit=1.581)
um = o0['eps'] / (3 * np.sqrt(1.5))
rs = []
for _ in range(4000):
    uu = rng.choice(um, 30)
    lam = erw('G1', np.clip(uu, 0.7, 1.3)) * rng.choice(f, 30)
    g = rng.poisson(lam)
    rs.append(stats.spearmanr(uu, g).statistic)
rs = np.array(rs)
print('Modell: Spearman(ε, G1) über 30 Kampagnen: Median %.2f, 5–95 %% [%.2f; %.2f]; P(≤ −0,81) = %.2f' %
      (np.nanmedian(rs), np.nanquantile(rs, 0.05), np.nanquantile(rs, 0.95), np.nanmean(rs <= -0.808)))
print('beobachtet sd(u) = %.4f, Modell sd(u) = %.4f' % (u.std(ddof=1), um.std()))
print('beobachtet u: min %.3f; P_Modell(min von 30 ≤ %.3f) = %.2f' % (u.min(), u.min(), 1 - (1 - (um <= u.min()).mean()) ** 30))
print('KS-Test u gegen Modell: p = %.2f' % stats.kstest(u, um).pvalue)
