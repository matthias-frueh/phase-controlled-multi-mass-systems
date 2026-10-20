# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 3.1.
# Zweck: erwartete S1-Halte der 30 Kampagnen von PR #23 bei ihrem ε_ctrl (Gitter, ohne Wiederaufnahme), Anteil von
#   V1-G0 Nr. 2, κ(ν) der oberen 80-%-Grenze und ν_eff analytisch für 40 bzw. 59 Leave-one-out-Werte.
# Eingaben: Argument 1 = dieser Ordner (gitter.json, eps_tabelle.csv; schreibt eps_tabelle_mit_erwartung.csv
#   dorthin), Argument 2 = Verzeichnis mit den Checkpoint-Ordnern korr-N01-{A4,V1G0,V1G60h}-wiederholungen/ der Korrekturrunde von PR #23
#   (flüchtig, am 18.10.2026 unter /tmp/pcmms-ablauf-vergleich-20261018/ erzeugt; SHA-256 der ablauf_*.json in
#   docs/ap13_kmax_wiederholungen_2026-10-17/ergebnisse.json, Schlüssel "checkpoints")
# Seed: keiner. Laufzeit: gemessen unter 1 s (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B erwartung30.py . <checkpoint-basis> > erwartung30.out
# Herkunft: Nachprüfung 1. Geändert: Checkpoint-Pfad als Argument 2 (vorher fest).
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""Erwartete S1-Halte der 30 Kampagnen bei ihrem ε_ctrl (Gitter, ohne Wiederaufnahme: P(mindestens ein S1))."""
import sys, json, csv
import numpy as np
from scipy.stats import chi2
D = sys.argv[1]
g = json.load(open(D + '/gitter.json')); F = g['felder']; us = np.array([float(u) for u in g['gitter']])
M = np.array([g['gitter'][k]['mittel'] for k in g['gitter']])
f = lambda name, u: np.exp(np.interp(np.clip(u, 0.7, 1.3), us, np.log(np.maximum(M[:, F.index(name)], 1e-7))))
rows = list(csv.DictReader(open(D + '/eps_tabelle.csv')))
BAS = sys.argv[2]                       # flüchtige Checkpoints (Kopf)
konf = {}
for a in ('A4', 'V1G0', 'V1G60h'):
    j = json.load(open(f'{BAS}/korr-N01-{a}-wiederholungen/ablauf_korr-N01-{a}-wiederholungen.json'))
    for b in j['inhalt']['befunde']:
        konf[(b['szenario'], b['index'])] = b['ablauf']['rollen'].get('konfiguration', 0)
u = np.array([float(r['u']) for r in rows]); fr = np.array([konf[(r['szenario'], int(r['index']))] / 504 for r in rows])
lx, la = f('S1X', u), f('S1A', u)
lam = (lx + la)
p_halt = 1 - np.exp(-lam)            # volle Kampagne, ohne Wiederaufnahme
print('erwartete Zahl Kampagnen mit S1 (volle Länge): %.2f (davon X′-Pfad λ-Summe %.2f, Alarm %.2f); beobachtet 4' % (p_halt.sum(), lx.sum(), la.sum()))
lh = lam.mean(); print('homogen: je Kampagne λ = %.3f → %.2f' % (lh, 30 * (1 - np.exp(-lh))))
order = np.argsort(-lam)
out = []
for i in order:
    r = rows[i]
    out.append(dict(r, lambda_S1X=round(float(lx[i]), 4), lambda_S1A=round(float(la[i]), 4), konfig_anteil=round(float(fr[i]), 3)))
for x in out[:8]:
    print(x['szenario'], x['index'], 'u', x['u'], 'λ_X', x['lambda_S1X'], 'λ_A', x['lambda_S1A'], 'Halt', x['halt'] or '-')
with open(D + '/eps_tabelle_mit_erwartung.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(sorted(out, key=lambda x: (x['szenario'], int(x['index']))))
# Anteil der X′-Pfad-Erwartung aus V1-G0 Nr. 2
i2 = [i for i, r in enumerate(rows) if r['szenario'] == 'N01-V1G0' and r['index'] == '2'][0]
print('Anteil λ_X von V1-G0 Nr. 2 an der Summe: %.2f' % (lx[i2] / lx.sum()))
k = lambda nu: np.sqrt(nu / chi2.ppf(0.2, nu))
print('κ(ν) obere 80-%%: ν=41 %.4f, ν=39 %.4f, ν=21 %.4f, ν=31 %.4f, ν=57 %.4f, ν=19 %.4f' % (k(41), k(39), k(21), k(31), k(57), k(19)))
# ν_eff analytisch: n LOO-Werte mit Lag-Korrelationen −2/3, 1/6
for n in (40, 59):
    print('ν_eff analytisch n =', n, round(n / (1 + 2 * ((2 / 3) ** 2 + (1 / 6) ** 2)), 1))
