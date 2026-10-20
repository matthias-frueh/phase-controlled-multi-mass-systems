# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 3.1 (Spalte „σ bekannt“) und 8.
# Zweck: Gegenprobe zu a_halt_s1_wege.py mit bekanntem σ (σ̂_ref = √1,5·σ fest), sonst gleich. Der Pool aus 42
#   Referenzläufen wird weiterhin gezogen, aber nicht verwendet; so bleibt der Zufallsstrom wie in a_halt_s1_wege.py.
# Seed: default_rng(11); 4·10⁶ Läufe je Lage. Laufzeit: gemessen 6 s Wandzeit, 6 s CPU (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B wege_sigma_bekannt.py > wege_sigma_bekannt.out
# Herkunft: Gegenprobe des Hauptbearbeiters (gegenprobe_r1). Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
# S1-Wege je Lauf X unter exakter Superposition (A8-Annahmen: gleiche Streuung, keine Drift), nur Summenkanal.
# Folge nach ablauf.py: Vorpruefung |X-R0|>eps -> R1 (Alarm gegen R0, Wiederholung gegen R0, reproduziert -> S1;
# sonst ersetzt die Wiederholung). G1(X) mit R0 und dem naechsten gueltigen Referenzlauf B (R1 bzw. planmaessiger Lauf
# nach m weiteren Laeufen); Verstoss -> R2 (Alarm gegen B), X', R3 (Alarm gegen R2); S1 wenn X' gegen R2/R3 > eps.
import numpy as np
from scipy.stats import norm
g = np.random.default_rng(11)
n = 4_000_000
Rr = g.standard_normal((200_000, 42))
pool = (Rr[:, 1:-1] - (Rr[:, :-2] + Rr[:, 2:]) / 2).std(1, ddof=1)
def lauf(k, m):
    s = np.full(n, np.sqrt(1.5)); eps = 3 * s; ta = 3 * (4 / 3) ** 0.5 * s
    R0, X, A, Aw, Bp, R2, R2w, Xs, R3, R3w = g.standard_normal((10, n))
    al = lambda r, ref: np.abs(r - ref) > ta
    vor = np.abs(X - R0) > eps
    # Weg A: Alarm an R1, reproduziert
    a1 = vor & al(A, R0); sA = a1 & al(Aw, R0)
    R1 = np.where(a1, Aw, A)                     # nicht reproduziert: Wiederholung ersetzt R1
    okA = vor & ~sA
    # naechster gueltiger Referenzlauf B: R1 (Vorpruefung) bzw. planmaessig m Laeufe nach X
    B = np.where(vor, R1, Bp)
    w = np.where(vor, k / (k + 1), k / (k + m))  # Gewicht von B in der Interpolation
    dN = X - (R0 + w * (B - R0))
    g1 = np.abs(dN) > eps
    g1 &= ~sA
    # planmaessiges B (ohne Vorpruefung) kann selbst alarmieren; vereinfachend ignoriert (A8 zaehlt es dort)
    # Weg C: Alarm an R2 gegen B, reproduziert
    sC2 = g1 & al(R2, B) & al(R2w, B)
    R2e = np.where(g1 & al(R2, B) & ~al(R2w, B), R2w, R2)
    ok2 = g1 & ~sC2
    sC3 = ok2 & al(R3, R2e) & al(R3w, R2e)
    R3e = np.where(ok2 & al(R3, R2e) & ~al(R3w, R2e), R3w, R3)
    ok3 = ok2 & ~sC3
    sB = ok3 & (np.abs(Xs - (R2e + R3e) / 2) > eps)
    return dict(vor=vor.mean(), g1=g1.mean(), A=sA.mean(), B=sB.mean(), C2=sC2.mean(), C3=sC3.mean())
for k, m in ((1, 1), (6, 6), (12, 1)):
    r = lauf(k, m)
    print(f'k={k:2d} m={m:2d}: P(Vorpr.)={r["vor"]:.4f} P(G1-Fall)={r["g1"]:.4f} | S1 je Lauf: '
          f'ueber X\' {r["B"]:.2e}, Alarm R1 {r["A"]:.2e}, Alarm R2 {r["C2"]:.2e}, Alarm R3 {r["C3"]:.2e}, '
          f'Summe {r["A"]+r["B"]+r["C2"]+r["C3"]:.2e}')
print('A8: S1 ueber G1 je Lauf 2,5e-4 (Vorpruefung nicht beruecksichtigt), Nullpunktalarm 7,3e-4 je Referenzlauf und Kanal')
