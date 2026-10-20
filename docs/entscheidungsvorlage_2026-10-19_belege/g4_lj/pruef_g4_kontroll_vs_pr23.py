# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 2.2 (Option F).
# Zweck: Prüfung des Normalmodells für G4 an Lⱼ (n₀ = 20 je Modul, D_N und D_F unabhängig) gegen die 41 gespeicherten
#   G4-Kontrollwiederholungen der 25 abgeschlossenen PR-#23-Kampagnen.
# Seed: default_rng(20261019); B = 40 000. Laufzeit: gemessen 2 s Wandzeit, 2 s CPU (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B pruef_g4_kontroll_vs_pr23.py > pruef_g4_kontroll_vs_pr23.out
# Herkunft: Kritik zur ersten Fassung (Prüfung des Modells aus g4_kontroll.py). Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
# Prüfung: Modell aus g4_kontroll.py (n0 = 20 je Modul, D_N und D_F unabhängig, Normalmodell) gegen die
# gespeicherten G4-Kontrollwiederholungen der 25 abgeschlossenen PR-#23-Kampagnen (41, aus den Checkpoint-Befunden).
import numpy as np
from scipy import stats
rng = np.random.default_rng(20261019)
c = 1.4826
def mads(n, B):
    x = rng.standard_normal((B, n))
    return c * np.median(np.abs(x - np.median(x, 1, keepdims=True)), 1)
B = 40000
sN = mads(20, 3 * B).reshape(B, 3); sF = mads(20, 3 * B).reshape(B, 3)
p = 1 - (1 - 2 * stats.norm.sf(3 * sN)) * (1 - 2 * stats.norm.sf(3 * sF))
L = 25
# Wiederholungen je Kampagne: je Modul L Läufe, erste Wiederholung mit p, zweite mit p (bedingt)
w1 = rng.binomial(L, p)                         # erste Wiederholungen
w2 = rng.binomial(w1, p)                        # zweite Wiederholungen
w = (w1 + w2).sum(1)
summe = np.array([rng.choice(w, 25).sum() for _ in range(20000)])
print('Modell: Wiederholungen je Kampagne Mittel %.2f, SD %.2f' % (w.mean(), w.std()))
print('Summe über 25 Kampagnen: Mittel %.1f, 1-%%-Quantil %.0f, P(Summe <= 41) = %.4f' % (
    summe.mean(), np.quantile(summe, 0.01), (summe <= 41).mean()))
