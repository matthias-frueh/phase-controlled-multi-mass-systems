# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 3.1 und 1.2.
# Zweck: Häufigkeit der Vorprüfung, des Alarms und des reproduzierten Alarms am R₁ sowie des S1 an R₂ je G1-Fall.
# Annahmen: wie a_halt_s1_wege.py (Summenkanal, σ̂_ref aus 42 Referenzläufen, Leave-one-out, X mittig zwischen R₀
#   und R₁).
# Seed: default_rng(7); 2·10⁶ Läufe. Laufzeit: gemessen 1 s Wandzeit, 1 s CPU (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B a_halt_alarm_r1r2.py > a_halt_alarm_r1r2.out
# Herkunft: Nachprüfung 3. Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
# Null (exakte Superposition, keine Drift), nur Summenkanal, sigma je Lauf = 1, sigma_ref aus 42 Referenzlaeufen (LOO) wie A8.
# Folge: R0, X, [Vorpruefung |X-R0|>eps -> R1], G1(X) mit R0/R1 (Interpolation: X mittig zwischen R0 und R1 zeitlich? nein:
# R1 folgt unmittelbar auf X, R0 liegt einen Lauf davor -> X mittig), bei Verstoss R2 (Alarm gegen R1), X', R3.
import numpy as np
g = np.random.default_rng(7)
n = 2_000_000
R = g.standard_normal((n // 10, 42))
s_pool = (R[:, 1:-1] - (R[:, :-2] + R[:, 2:]) / 2).std(1, ddof=1)
s = g.choice(s_pool, n)                      # sigma_ref-Ziehungen
eps = 3 * s
t_al = 3 * (4 / 3) ** 0.5 * s                # Nullpunktalarm-Schwelle
R0, X, R1, R1w, R2, R2w = g.standard_normal((6, n))
vor = np.abs(X - R0) > eps                    # Vorpruefung -> R1
al1 = np.abs(R1 - R0) > t_al
s1_r1 = al1 & (np.abs(R1w - R0) > t_al)       # S1 ueber reproduzierten Alarm an R1
print('P(Vorpruefung)                    = %.4f' % vor.mean())
print('P(Alarm an R1 | Vorpruefung)       = %.4f   (unbedingt je R: %.4f)' % (al1[vor].mean(), al1.mean()))
print('P(S1 an R1 | Vorpruefung)          = %.2e  (unbedingt je R und Kanal: %.2e)' % (s1_r1[vor].mean(), s1_r1.mean()))
# G1 von X mit R0/R1 (X mittig), nur wenn R1 kein Alarm (sonst andere Folge); R2 gegen R1 (neues R0)
ok1 = vor & ~al1
g1 = ok1 & (np.abs(X - (R0 + R1) / 2) > eps)
al2 = np.abs(R2 - R1) > t_al
s1_r2 = al2 & (np.abs(R2w - R1) > t_al)
print('P(G1-Verstoss | Vorpruefung, R1 ok) = %.4f' % g1[ok1].mean())
print('P(Alarm an R2 | G1-Fall)           = %.4f' % al2[g1].mean())
print('P(S1 an R2 | G1-Fall)              = %.2e' % s1_r2[g1].mean())
print('Anzahl G1-Faelle in Stichprobe     =', int(g1.sum()))
