# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 2.1 (Zählung an S120).
# Zweck: aus g4_konfigurationen.csv und ergebnisse.json von PR #22 je System und Punkt Läufe, G4 unter v2, D_N-Anteil,
#   σ_F,v2 je Kampagne und s_i; Ausgabe csv_s120.json für s120_rate.py.
# Eingaben: docs/e3b_g4_diagnose_2026-10-17/; Argument 1 = Ausgabe (Standard csv_s120.json hier).
# Seed: keiner. Laufzeit: gemessen unter 1 s (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B csv_s120.py csv_s120.json > csv_s120.out
# Herkunft: Nachprüfung 6. Geändert: Repository- und Ausgabepfad.
# Repository-Wurzel: drei Ebenen über diesem Ordner; abweichend über die Umgebungsvariable PCMMS_REPO (etwa ein
#   Auszug von main 0f63187: git archive 0f63187 code docs | tar -x -C <ziel>).
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
# NL6: g4_konfigurationen.csv (PR #22) je System und Punkt: Läufe, G4 unter v2, D_N-Anteil (G4_N, produktiv = alle
# Varianten), mittleres σ_F,v2 und s_i (jitter_phase0); dazu ergebnisse.json (mad_DF, σ_P = v0k, Piloten).
import csv, json, os, sys
import numpy as np
REPO = os.environ.get('PCMMS_REPO') or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))   # Repository-Wurzel (Kopf)
D = os.path.join(REPO, 'docs', 'e3b_g4_diagnose_2026-10-17') + os.sep
rows = list(csv.DictReader(open(D + 'g4_konfigurationen.csv')))
erg = json.load(open(D + 'ergebnisse.json'))['inhalt']['g4']['systeme']
out = {}
for sid in ('N01-A4', 'N01-V1G0', 'N01-V1G60h'):
    e = erg[sid]
    sP = e['sigma_F']['v0k'][0] * 1e3
    sp = np.array(e['piloten']['jitter_phase0'][:3]) * 1e3
    sn2 = sP**2 - np.mean(sp**2)
    print(f'== {sid}: σ_P (v0k) = {sP:.3f} mN, s_p Piloten = {np.round(sp,3)}, σ_n² = σ_P² − s̄_P² = {sn2:.3f} mN² (σ_n = {np.sqrt(sn2):.3f})')
    print(' Punkt  n   G4_v2  G4_N   σ_v2[mN]  s_i[mN]  mad_DF[mN]  mad/σ_v2   Jitteranteil/s_i')
    out[sid] = {}
    for c, pid in enumerate(e['punkte']['id']):
        R = [r for r in rows if r['system'] == sid and r['punkt'] == pid]
        n = sum(int(r['laeufe']) for r in R)
        g2 = sum(int(r['G4_v2']) for r in R)
        gN = sum(int(r['G4_N']) for r in R)
        sv2 = np.mean([float(r['sigma_F_v2_mN']) for r in R])
        si = np.mean([float(r['jitter_phase0_mN']) for r in R])
        md = e['punkte']['mad_DF'][c] * 1e3
        jit = np.sqrt(max(md**2 - sn2, 0)) / si
        out[sid][pid] = dict(n=n, G4_v2=g2, G4_N=gN, sigma_v2=sv2, s_i=si, mad=md,
                             sv2_kamp=[float(r['sigma_F_v2_mN']) for r in R])
        if pid in ('S100', 'S110', 'S116', 'S118', 'S120', 'S122', 'S124', 'S130', 'S140'):
            print(f' {pid}  {n}  {g2:4d} ({100*g2/n:.2f} %)  {gN:3d} ({100*gN/n:.2f} %)  {sv2:.3f}  {si:.3f}  {md:.3f}  {md/sv2:.3f}  {jit:.3f}')
json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'csv_s120.json'), 'w'))
