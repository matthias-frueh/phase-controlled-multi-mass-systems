# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 3.1 (Prüfschwelle, Reserve unter dem Wiederholungsablauf).
# Zweck: Prüfschwelle 0,069 und Überdeckungsschwelle 0,936 in Abhängigkeit von der Zahl gewerteter Kampagnen;
#   Reserve unter dem Wiederholungsablauf (Binomial, unabhängige Versuche).
# Seed: keiner. Laufzeit: gemessen unter 1 s (ein Prozess, ein Thread, 20.10.2026). Aufruf: python3 -I -B schwellen.py > schwellen.out
# Herkunft: Nachprüfung 4. Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""Nachrechnung: Prüfschwelle 0,069 (A8), 0,064, 'etwa 8 %', Überdeckungsschwelle 0,936 (§8.6) und ihre Abhängigkeit
von der Zahl gewerteter Kampagnen; Reserve unter dem Wiederholungsablauf (Platz fehlt nach drei ungültigen Versuchen)."""
import numpy as np
from scipy import stats
q = 0.05
def se(n, p=q):
    return np.sqrt(p * (1 - p) / n)
for n_k, n_p in ((1000, 1000), (833, 833), (950, 950), (1000, 833)):
    s_p, s_c = se(n_p), se(n_k)
    ges = np.hypot(s_p, s_c)
    print(f'n_kal={n_k} n_pruef={n_p}: SE_pruef={s_p:.5f} SE_c(Ratenskala)={s_c:.5f} gesamt={ges:.5f} '
          f'Schwelle={q + 2 * ges:.5f}  nur Prüffehler={q + 2 * s_p:.5f}  '
          f'P(Rate > 0,05+2SE_pruef | korrekt)={stats.norm.sf(2 * s_p / ges):.4f}')
for n in (1000, 950, 833):
    print(f'Überdeckungsschwelle bei n={n}: {0.95 - 2 * se(n, 0.95):.5f}')
# Reserve: Platz fehlt nach drei ungültigen Versuchen (Original + 2 Wiederholungen), unabhängig
for p in (0.01, 0.05, 0.1, 0.3):
    for n_min, r in ((18, 2), (18, 3)):
        n = n_min + r
        lost = p ** 3
        pp = stats.binom.sf(r, n, lost)           # mehr als r Plätze verloren
        alle = (1 - pp) ** 21
        print(f'p={p:.2f} n_min={n_min} r={r}: P(Platz fehlt)={lost:.2e} P(Punkt<n_min)={pp:.2e} '
              f'P(alle 21 Punkte >= n_min, unabh.)={alle:.4f}')
