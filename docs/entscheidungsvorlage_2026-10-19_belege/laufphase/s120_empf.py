# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 2.2 (an S120 ändert das MAD(D_F) um höchstens −4/+2,4 %).
# Zweck: Empfindlichkeit von MAD(D_F) an S120 (A4) gegen den Schätzfehler der Laufgrößen (90-%-Intervalle bei
#   ν = 19 bzw. 57). Führt den Kopf von df_mc.py aus diesem Ordner aus.
# Seed: default_rng(11); N = 40 000. Laufzeit: gemessen 14 s Wandzeit, 14 s CPU (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: PCMMS_REPO=<auszug 0f63187> python3 -B s120_empf.py > s120_empf.out
# Herkunft: Nachprüfung 6. Geändert: Pfad von df_mc.py.
# Repository-Wurzel: drei Ebenen über diesem Ordner; abweichend über die Umgebungsvariable PCMMS_REPO (etwa ein
#   Auszug von main 0f63187: git archive 0f63187 code docs | tar -x -C <ziel>).
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
# NL6: Empfindlichkeit von MAD(D_F) an S120 (A4) gegen den Schätzfehler der Laufgrößen (90-%-Intervall bei ν = 19:
# Faktor 0,73 / 1,26 auf σ_δ und σ_a; ν = 57: 0,82 / 1,17 auf den Versatz), sonst L1.
import sys
import os
import numpy as np
sys.argv = ['x', 'A4', '40000']
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'df_mc.py')).read().split('if __name__')[0])
rng = np.random.default_rng(11)
ref = mad(df_ziehen(120.0, 240.0, PAR, rng, N))
for lab, ab in (('δ ×0,73', dict(delta=0.03*0.73)), ('δ ×1,26', dict(delta=0.03*1.26)),
                ('A ×0,73', dict(amp=0.003*0.73)), ('A ×1,26', dict(amp=0.003*1.26)),
                ('Versatz ×0,82', dict(versatz=0.05*0.82)), ('Versatz ×1,17', dict(versatz=0.05*1.17)),
                ('alle ×0,8', dict(delta=0.024, amp=0.0024, versatz=0.04)), ('alle ×1,2', dict(delta=0.036, amp=0.0036, versatz=0.06))):
    m = mad(df_ziehen(120.0, 240.0, dict(PAR, **ab), rng, N))
    print(f'{lab:14s}: MAD {m*1e3:.3f} mN, relativ zu L1 {m/ref:.3f}')
print(f'L1: {ref*1e3:.3f} mN')
