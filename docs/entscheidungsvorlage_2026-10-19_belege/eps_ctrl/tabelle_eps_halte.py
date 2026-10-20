# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 3.1 und 3.5.
# Zweck: Tabelle ε_ctrl, u, G1-Fälle, R₁, R₂, X′, R₃, Alarmwiederholungen und Halt je Kampagne der 30 Ablauf-
#   kampagnen von PR #23 (N01-A4, N01-V1G0, N01-V1G60h je 10, Variante „wiederholungen“; laut Checkpoint-Metadaten
#   ablauf-2, Code c8c0a36) und Rangkorrelationen gegen ε_ctrl.
# Eingaben: Argument 1 = Verzeichnis mit den Checkpoint-Ordnern korr-N01-{A4,V1G0,V1G60h}-wiederholungen/ der Korrekturrunde von PR #23
#   (flüchtig, am 18.10.2026 unter /tmp/pcmms-ablauf-vergleich-20261018/ erzeugt; SHA-256 der ablauf_*.json in
#   docs/ap13_kmax_wiederholungen_2026-10-17/ergebnisse.json, Schlüssel "checkpoints")
#   Argument 2 = Ausgabedatei (CSV). Das Skript liest nur.
# Annahmen: σ von ⟨N⟩ (Summe) je Lauf 0,02/√(6400·10) N (Rauschmodell L1, T_a = 10 s), u = ε_ctrl/(3·√1,5·σ).
#   G1_p1 = phase1.regeln["G1"] (nach Vorlage 3.1 einschließlich Referenzläufen mit Nullpunktalarm);
#   G1_konfig = nur Konfigurationsläufe.
# Seed: keiner (Zählung). Laufzeit: gemessen unter 1 s (ein Prozess, ein Thread, 20.10.2026).
# Aufruf (in diesem Ordner): python3 -I -B tabelle_eps_halte.py <checkpoint-basis> eps_ctrl_halte_je_kampagne.csv
#   > tabelle_eps_halte.out
# Herkunft: erste Fassung der Vorlage (Scratch-Ordner, vor den Nachprüfungen). Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""Tabelle eps_ctrl x G1 x R1 x X' x Halt je Kampagne aus den Checkpoint-Befunden (nur lesen)."""
import csv
import glob
import json
import sys

import numpy as np
from scipy.stats import spearmanr, kendalltau

BASIS = sys.argv[1]
AUS = sys.argv[2]
SIGMA = 0.02 / np.sqrt(6400.0 * 10.0)          # wahres sd von <N> (Summe) je Lauf, rauschen.py/ebene_h.py, T_a = 10 s
EPS_WAHR = 3 * np.sqrt(1.5) * SIGMA

zeilen = []
for f in sorted(glob.glob(f'{BASIS}/korr-N01-*-wiederholungen/ablauf_*.json')):
    d = json.load(open(f))
    for b in d['inhalt']['befunde']:
        a = b['ablauf']
        ro = a['rollen']
        xs = a.get('x_strich') or []
        halt = a['halt']
        art = ''
        if halt == 'S1':
            art = 'S1 X′' if any(x.get('halt') for x in xs) else 'S1 Nullpunktalarm'
        elif halt:
            art = halt
        an = a['anlaesse']
        alarmw = sum(v for k, v in an.items() if k.startswith('alarmwiederholung'))
        zeilen.append(dict(
            szenario=b['szenario'], index=b['index'], seed=b['seed'],
            eps_ctrl_mN=1e3 * b['teil_b']['eps_ctrl'], u=b['teil_b']['eps_ctrl'] / EPS_WAHR,
            n_laeufe_p1=b['phase1']['n_laeufe'], G1_p1=b['phase1']['regeln'].get('G1', 0),
            G1_konfig=b['phase1']['konfig_regeln'].get('G1', 0),
            R1=ro.get('R1', 0), R2=ro.get('R2', 0), X_strich=ro.get('X_strich', 0), R3=ro.get('R3', 0),
            X_strich_G1=sum(1 for x in xs if x.get('g1')), X_strich_ungueltig=sum(1 for x in xs if not x['gueltig']),
            alarmwiederholung=alarmw, halt=art, status=a['status'],
            max_xr0_eps=max([x['abweichung_r0_N'] / b['teil_b']['eps_ctrl'] for x in xs
                             if x.get('abweichung_r0_N') is not None], default=float('nan'))))

zeilen.sort(key=lambda z: (z['szenario'], z['index']))
with open(AUS, 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(zeilen[0]))
    w.writeheader()
    for z in zeilen:
        w.writerow({k: (f'{v:.4f}' if isinstance(v, float) else v) for k, v in z.items()})

hdr = ('szenario', 'index', 'eps_ctrl_mN', 'u', 'n_laeufe_p1', 'G1_p1', 'R1', 'R2', 'X_strich', 'R3', 'X_strich_G1',
       'alarmwiederholung', 'halt')
print(' | '.join(hdr))
for z in zeilen:
    print(' | '.join(f'{z[h]:.3f}' if isinstance(z[h], float) else str(z[h]) for h in hdr))
e = np.array([z['eps_ctrl_mN'] for z in zeilen])
g = np.array([z['G1_p1'] for z in zeilen])
x = np.array([z['X_strich'] for z in zeilen])
r1 = np.array([z['R1'] for z in zeilen])
n = np.array([z['n_laeufe_p1'] for z in zeilen])
print('N', len(e), 'eps min/median/max', e.min(), np.median(e), e.max(), 'eps_wahr_mN', 1e3 * EPS_WAHR)
print('u min/median/max', e.min() / (1e3 * EPS_WAHR), np.median(e) / (1e3 * EPS_WAHR), e.max() / (1e3 * EPS_WAHR),
      'sd(u)', np.std(e / (1e3 * EPS_WAHR), ddof=1))
for nm, y in (('G1', g), ('X′', x), ('R1', r1), ('G1/Lauf', g / n)):
    rs = spearmanr(e, y)
    kt = kendalltau(e, y)
    print(nm, 'Spearman', round(rs.statistic, 3), 'p', f'{rs.pvalue:.2g}', 'Kendall', round(kt.statistic, 3),
          'p', f'{kt.pvalue:.2g}')
print('Summen: G1', g.sum(), 'R1', r1.sum(), "X'", x.sum(), 'Läufe', n.sum())
