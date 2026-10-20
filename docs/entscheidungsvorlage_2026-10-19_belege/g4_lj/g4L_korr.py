# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 2.2 (Option F, D_N und D_F unabhängig).
# Zweck: (1) Phase 0 von PR #22 und PR #23 gleich (σ̂_Δ,K gleicher Seeds)? (2) Korrelation von D_N und D_F an
#   K-Läufen (Stellvertreter für L) aus den PR-#22-npz; gemeinsame Überschreitungen aus g4_konfigurationen.csv.
# Eingaben: Argument 1 = Verzeichnis mit den Diagnose-Checkpoints von PR #22 (Ordner G4-N01-*-start/-rest; flüchtig, am 17.10.2026 unter
#   /tmp/pcmms-diagnose-e3b-g4-20261017/ erzeugt; SHA-256 in docs/e3b_g4_diagnose_2026-10-17/ergebnisse.json)
#   Argument 2 = g4L_daten.json (Standard: hier); docs/e3b_g4_diagnose_2026-10-17/g4_konfigurationen.csv.
# Seed: keiner. Laufzeit: gemessen 1 s Wandzeit, 1 s CPU (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B g4L_korr.py <checkpoints-pr22> > g4L_korr.out
# Herkunft: Scratch-Ordner vor der Nachprüfung 2 (erste Fassung); von Nachprüfung 2 gelesen, erneut ausgeführt und
#   übernommen. Geändert: Pfade (Checkpoints als Argument, Repository relativ).
# Repository-Wurzel: drei Ebenen über diesem Ordner; abweichend über die Umgebungsvariable PCMMS_REPO (etwa ein
#   Auszug von main 0f63187: git archive 0f63187 code docs | tar -x -C <ziel>).
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
# (1) Phase 0 von PR #22 und PR #23 gleich? (σ̂_Δ,K gleicher Seeds)  (2) Korrelation D_N/D_F – nur K-Läufe gespeichert
# (Stellvertreter, nicht L): Pilot- und Phase-1-K-Läufe aus den PR-#22-npz; gemeinsame Überschreitungen aus g4_konfigurationen.csv
import json, csv, glob, os, sys
import numpy as np
from scipy import stats
BASIS22 = sys.argv[1]                   # flüchtige Checkpoints von PR #22 (Kopf)
DATEN = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'g4L_daten.json')
REPO = os.environ.get('PCMMS_REPO') or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))   # Repository-Wurzel (Kopf)
D = json.load(open(DATEN)); d22, d23 = D['d22'], D['d23']
for key, b in sorted(d23.items()):
    s22 = d22[key]['sigma_delta']['K']; s23 = b['teil_b']['sigma_delta_K']
    if key.endswith('|0') or key.endswith('|5'):
        print(key, 'σ̂N gleich', np.isclose(s22['N'], s23['N'], rtol=1e-12), 'σ̂F 22/23 [mN]', round(1e3*s22['F'], 4), round(1e3*s23['F'], 4))
print()
for sysn in ('N01-A4', 'N01-V1G0', 'N01-V1G60h'):
    rP, rL, rLp = [], [], []
    for f in sorted(glob.glob(f'{BASIS22}/G4-{sysn}-*/g4_*.npz')):
        if 'verworfen' in f: continue
        z = np.load(f, allow_pickle=False)
        idx = sorted({int(k.split('__')[1]) for k in z.files})
        for i in idx:
            g = lambda n: z[f'befunde__{i}__felder__{n}']
            rP.append(stats.spearmanr(g('pilot_DN'), g('pilot_DF'))[0])
            ro = g('laeufe_rolle') == 0
            rL.append(np.corrcoef(g('laeufe_DN')[ro], g('laeufe_DF')[ro])[0, 1])
            rLp.append(stats.pearsonr(g('pilot_DN'), g('pilot_DF'))[0])
    rP, rL, rLp = map(np.array, (rP, rL, rLp))
    print(f'{sysn}: K-Pilot (60 Läufe je Kampagne) Pearson Mittel {rLp.mean():+.3f} (SD über Kampagnen {rLp.std(ddof=1):.3f}, '
          f'Normaltheorie SD {1/np.sqrt(59):.3f}); Phase-1-K-Originalläufe (504 je Kampagne, gepoolt über Punkte) Pearson Mittel {rL.mean():+.3f} (SD {rL.std(ddof=1):.3f})')
rows = list(csv.DictReader(open(os.path.join(REPO, 'docs', 'e3b_g4_diagnose_2026-10-17', 'g4_konfigurationen.csv'))))
for sysn in ('N01-A4', 'N01-V1G0', 'N01-V1G60h'):
    r = [x for x in rows if x['system'] == sysn]
    n = sum(int(x['laeufe']) for x in r); gN = sum(int(x['G4_N']) for x in r); gF = sum(int(x['G4_F']) for x in r)
    g = sum(int(x['G4_v0']) for x in r)
    beide = gN + gF - g
    erw = gN * gF / n
    print(f'{sysn} (K, g4_konfigurationen.csv): Läufe {n}, D_N {gN}, D_F {gF}, G4 (v0) {g}, beide {beide}, bei Unabhängigkeit erwartet {erw:.2f}')
