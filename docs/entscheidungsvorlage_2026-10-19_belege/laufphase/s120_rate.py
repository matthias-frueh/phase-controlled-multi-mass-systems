# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 2.1 (G4-Rate unter v2 an S120).
# Zweck: G4-Rate an S120, S118, S100 aus der nachgebildeten D_F-Verteilung mit den kampagnenweisen v2-Schwellen
#   aus csv_s120.json; Vergleich mit der gezählten Rate unter v2. Führt den Kopf von df_mc.py aus diesem Ordner aus.
# Eingaben: Argument 1 = System (A4 oder V1-G0); csv_s120.json hier; Code des Repositorys.
# Seed: default_rng(20261020); N = 200 000. Laufzeit: etwa 1 min je System (Einschätzung; Ausgaben übernommen).
# Aufruf: PCMMS_REPO=<auszug 0f63187> python3 -B s120_rate.py A4 > s120_rate_A4.out  (V1-G0 > s120_rate_V1G0.out)
# Herkunft: Nachprüfung 6. Geändert: Pfade von df_mc.py und csv_s120.json.
# Repository-Wurzel: drei Ebenen über diesem Ordner; abweichend über die Umgebungsvariable PCMMS_REPO (etwa ein
#   Auszug von main 0f63187: git archive 0f63187 code docs | tar -x -C <ziel>).
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
# NL6: G4-Rate an S120 (und am Piloten P2 = (130°, 230°)) aus der nachgebildeten D_F-Verteilung (df_mc.py) mit den
# kampagnenweisen v2-Schwellen aus g4_konfigurationen.csv; Vergleich mit der gezählten Rate unter v2.
import sys, json, os
import numpy as np
sys.argv = ['x', sys.argv[1] if len(sys.argv) > 1 else 'A4', '200000']
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'df_mc.py')).read().split('if __name__')[0])
C = json.load(open(os.path.join(HIER, 'csv_s120.json')))
sids = {'A4': ('N01-A4',), 'V1-G0': ('N01-V1G0', 'N01-V1G60h')}[name]
rng = np.random.default_rng(20261020)
var = {'soll': dict(amp=0, delta=0, versatz=0), 'Phase (Versatz + δ)': dict(amp=0), 'voll L1': {}}
for pid, (p2, p3) in (('S120', (120.0, 240.0)), ('S118', (118.0, 240.0)), ('S100', (100.0, 240.0))):
    for vn, ab in var.items():
        d = df_ziehen(p2, p3, dict(PAR, **ab), rng, N) * 1e3
        m = mad(d)
        for sid in sids:
            c = C[sid][pid]
            thr = 3 * np.array(c['sv2_kamp'])
            pF = np.mean([(np.abs(d) > t).mean() for t in thr])
            pN = c['G4_N'] / c['n']
            p = 1 - (1 - pF) * (1 - pN)
            print(f'{pid} {vn:20s} {sid:11s}: MAD {m:.3f} mN; v2-Schwelle Mittel {thr.mean()/3:.3f}; P(|D_F|>3σ_v2) = {100*pF:.2f} %, '
                  f'mit D_N (gezählt {100*pN:.2f} %) {100*p:.2f} %; gezählt v2 {c["G4_v2"]}/{c["n"]} = {100*c["G4_v2"]/c["n"]:.2f} %; '
                  f'P(|D_F| > 3·MAD) = {100*(np.abs(d) > 3*m).mean():.2f} %')
