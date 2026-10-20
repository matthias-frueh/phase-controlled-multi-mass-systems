# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 3.1.
# Zweck: unabhängige Nachzählung derselben Tabelle durch die Nachprüfung 1 (ε_ctrl), mit Prüfung der SHA-256 gegen
#   schluessel.json, Abgleich von Seed, Status und Halt mit docs/ap13_kmax_wiederholungen_2026-10-17/kampagnen.csv,
#   Rängen der angehaltenen Kampagnen nach ε_ctrl und Spearman/Kendall (auch ohne V1-G0 Nr. 2).
# Eingaben: Argument 1 = Verzeichnis mit den Checkpoint-Ordnern korr-N01-{A4,V1G0,V1G60h}-wiederholungen/ der Korrekturrunde von PR #23
#   (flüchtig, am 18.10.2026 unter /tmp/pcmms-ablauf-vergleich-20261018/ erzeugt; SHA-256 der ablauf_*.json in
#   docs/ap13_kmax_wiederholungen_2026-10-17/ergebnisse.json, Schlüssel "checkpoints")
#   Argument 2 = Ausgabedatei (CSV); dazu kampagnen.csv aus dem Repository. Liest nur.
# Annahmen: wie tabelle_eps_halte.py. Seed: keiner. Laufzeit: gemessen unter 1 s (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B tabelle.py <checkpoint-basis> eps_tabelle.csv > tabelle.out 2>&1
# Herkunft: Nachprüfung 1. Geändert: Checkpoint-Pfad und Ausgabedatei als Argumente, Repository relativ (vorher
#   feste Pfade; die Ausgabedatei war Argument 1).
# Repository-Wurzel: drei Ebenen über diesem Ordner; abweichend über die Umgebungsvariable PCMMS_REPO (etwa ein
#   Auszug von main 0f63187: git archive 0f63187 code docs | tar -x -C <ziel>).
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""Nachlese: ε_ctrl × G1 × R1 × X′ × Halt je Ablaufkampagne aus den flüchtigen Checkpoints (nur lesen)."""
import csv, hashlib, json, os, sys
import numpy as np
from scipy import stats

BASIS = sys.argv[1]                     # flüchtige Checkpoints (Kopf)
REPO = os.environ.get('PCMMS_REPO') or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))   # Repository-Wurzel (Kopf)
SIG = 20e-3 / np.sqrt(6400 * 10.0)      # σ von ⟨N⟩ (Summe) je Lauf, Ebene H, T_a = 10 s (rauschen.py)
rows = []
for sys_ in ('A4', 'V1G0', 'V1G60h'):
    a = f'korr-N01-{sys_}-wiederholungen'
    f = f'{BASIS}/{a}/ablauf_{a}.json'
    sch = json.load(open(f'{BASIS}/{a}/schluessel.json'))
    h = hashlib.sha256(open(f, 'rb').read()).hexdigest()
    ok = h == sch['dateien'][f'ablauf_{a}.json']
    d = json.load(open(f))
    print(a, 'sha256 ok' if ok else 'SHA ABWEICHUNG', 'git', d['inhalt']['meta']['code_version']['git'][:7],
          d['inhalt']['meta']['verfahren']['ablauf_version'], file=sys.stderr)
    for b in d['inhalt']['befunde']:
        ab, p1, tb = b['ablauf'], b['phase1'], b['teil_b']
        xs = ab['x_strich']
        ro = ab['rollen']
        rows.append(dict(
            szenario=b['szenario'], index=b['index'], seed=b['seed'],
            eps_ctrl_mN=round(1e3 * tb['eps_ctrl'], 4),
            u=round(tb['eps_ctrl'] / (3 * np.sqrt(1.5) * SIG), 4),
            n_laeufe_p1=p1['n_laeufe'], G1=p1['regeln'].get('G1', 0), G1_konfig=p1['konfig_regeln'].get('G1', 0),
            R1=ro.get('R1', 0), R2=ro.get('R2', 0), X_strich=ro.get('X_strich', 0), R3=ro.get('R3', 0),
            X_strich_G1=sum(1 for x in xs if x.get('g1') is True),
            X_strich_ungueltig=sum(1 for x in xs if x.get('gueltig') is False),
            alarmwdh=ro.get('alarmwiederholung', 0),
            halt=('' if ab['halt'] is None else ab['halt']) + ''.join(
                f" ({x.get('regel')} {x.get('versuch')})" for x in ab['halte']),
            halt_xstrich=sum(1 for x in xs if x.get('halt')),
            status=ab['status'], grund=ab['grund'][:90],
            max_x_r0_eps=round(max([abs(x['abweichung_r0_N']) for x in xs if x.get('abweichung_r0_N') is not None],
                                   default=float('nan')) / tb['eps_ctrl'], 4)))
out = sys.argv[2]
with open(out, 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)
# Abgleich mit kampagnen.csv (Seeds und Status der Variante „wiederholungen“)
kc = [r for r in csv.DictReader(open(f'{REPO}/docs/ap13_kmax_wiederholungen_2026-10-17/kampagnen.csv'))
      if r['variante'] == 'wiederholungen' and r['szenario'].startswith('N01') and r['art'] == 'schlank']
km = {(r['szenario'], int(r['index'])): r for r in kc}
nm = 0
for r in rows:
    k = km.get((r['szenario'], r['index']))
    if k is None or int(k['seed']) != r['seed'] or k['status'] != r['status'] or (k['halt'] or '') != r['halt'].split(' (')[0]:
        nm += 1; print('Abweichung', r['szenario'], r['index'], k and (k['seed'], k['status'], k['halt']), file=sys.stderr)
print('Kampagnen', len(rows), 'Abweichungen zu kampagnen.csv', nm, 'Zeilen kampagnen.csv', len(kc), file=sys.stderr)
e = np.array([r['eps_ctrl_mN'] for r in rows]); g = np.array([r['G1'] for r in rows]); x = np.array([r['X_strich'] for r in rows])
r1 = np.array([r['R1'] for r in rows]); gk = np.array([r['G1_konfig'] for r in rows])
print('eps min/median/max', e.min(), np.median(e), e.max(), 'Mittel', round(e.mean(), 4), 'sd', round(e.std(ddof=1), 4))
print('3*sqrt(1.5)*sigma_true [mN]', round(1e3 * 3 * np.sqrt(1.5) * SIG, 4), 'u median', round(np.median(e) / (1e3 * 3 * np.sqrt(1.5) * SIG), 4))
for name, v in (('G1', g), ('G1_konfig', gk), ('X_strich', x), ('R1', r1)):
    rs = stats.spearmanr(e, v); kt = stats.kendalltau(e, v)
    print(f'Spearman eps~{name}: {rs.statistic:.3f} p={rs.pvalue:.2g}; Kendall {kt.statistic:.3f} p={kt.pvalue:.2g}')
# ohne V1-G0 Nr. 2
m = ~((np.array([r['szenario'] for r in rows]) == 'N01-V1G0') & (np.array([r['index'] for r in rows]) == 2))
rs = stats.spearmanr(e[m], g[m]); print('ohne V1G0#2 Spearman eps~G1', round(rs.statistic, 3), '%.2g' % rs.pvalue)
rs = stats.spearmanr(e[m], x[m]); print('ohne V1G0#2 Spearman eps~X', round(rs.statistic, 3), '%.2g' % rs.pvalue)
# Rang von eps der Halte
order = np.argsort(e)
for i, r in enumerate(rows):
    if r['halt']:
        print('Halt', r['szenario'], r['index'], r['halt'], 'eps', r['eps_ctrl_mN'], 'Rang (aufsteigend) von 30:', int(np.where(order == i)[0][0]) + 1)
