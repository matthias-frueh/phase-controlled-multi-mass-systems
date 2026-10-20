# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 1.2, 3.1.
# Zweck: Modul. Phase-1-Ablauf auf Ebene der Teststatistik (Plan von PR #23: N_K = 21, n = 24, ein Messtag, 630
#   geplante Läufe) mit Vorprüfung, G1, R₂/X′/R₃, S1 und Nullpunktalarm; Wiederaufnahme ohne Befund, unbegrenzt.
# Annahmen: siehe Modulbeschreibung; kein S3, kein G2–G10, keine Drift, kein Aufwärmen.
# Seed: vom Aufrufer (random.Random). Laufzeit: etwa 5 ms je Kampagne (aus s1_verteilung, 20 000 Kampagnen in
#   107–111 s).
# Herkunft: Nachprüfung 1. Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""Phase-1-Ablauf auf Ebene der Teststatistik ⟨N⟩ (σ = 1 Summe, Zellen σ/√3), Nullfall, keine Drift.

Regeln (Entwurf §8.8, §9.2; Anhang A9.12 Z. 1179–1185; ablauf-3 sinngemäß, vereinfacht):
- Vorprüfung: |X − R₀| > ε → R₁ sofort; G1(X) mit R₀/R₁, sonst mit R₀ und dem nächsten gültigen Referenzlauf
  (lineare Interpolation über die Zeit, β aus der Laufposition).
- G1-Verstoß, der feststeht, bevor der Schlusskontrollsatz des Blocks begonnen hat → R₂, X′, R₃ unmittelbar (je Fall
  eigene Klammer); später festgestellt (auch jeder G1-Verstoß eines Kontrolllaufs im Schlusskontrollsatz) → weder
  Wiederholung noch S1. X′ ohne Vorprüfung; G1(X′) mit R₂/R₃ → S1-Halt.
- Nullpunktalarm: Referenzlauf gegen den vorangehenden gültigen um mehr als 3·√(4/3)·σ̂ (Summe bzw. Zelle) →
  sofortige Wiederholung; überschreitet sie im selben Kanal erneut → S1-Halt, sonst ersetzt sie den alarmierten Lauf.
- Halt → Wiederaufnahme ohne Befund mit vollständigem Kontrollsatz (R + Einzelmodulläufe, kein Schlusssatz), dann
  weiter im Plan (unbegrenzt; W wird nachträglich ausgewertet). Kein Aufwärmen, kein G2–G10, kein S3.
"""
import math
from collections import deque

SQ43 = 3 * math.sqrt(4 / 3)


def plan(N_K=21, n=24, mitte=12):
    """Planfolge wie generator.kampagne.laufplan (ein Messtag): ('R'|'CS'|'K', Block, Schlusssatz)."""
    seq = [('R', 0, False), ('CS', 1, False)]
    for b in range(1, n + 1):
        seq += [('K', b, False)] * mitte + [('R', b, False)] + [('K', b, False)] * (N_K - mitte) + [('CS', b, True)]
    seq += [('R', n, False)]
    return seq


def kampagne(eps, sref, srefc, rnd, seq, n_L=3, streng=False):
    """Zähler: G1 (online, alle), G1_frueh (mit X′), R1, Xs, S1X, S1A, alarm, n_lauf, n_ref, G1_L, WA.
    streng=True: Ein Nullpunktalarm im Kontrollsatz einer Wiederaufnahme hält sofort an (wie ablauf.py:
    Halt „Wiederaufnahme“), R₀ bleibt der letzte gültige Referenzlauf vor dem Halt; gezählt als WA."""
    tS, tC = SQ43 * sref, [SQ43 * s for s in srefc]
    sc = 1 / math.sqrt(3)
    g = rnd.gauss
    q = deque()

    def cs(block, schluss, vorn=False):
        x = [('R', block, schluss, 'W' if vorn else 'plan')] + [('L', block, schluss, 'W' if vorn else 'plan')] * n_L
        rnd.shuffle(x)
        if vorn:
            q.extendleft(reversed(x))
        else:
            q.extend(x)

    for it in seq:
        if it[0] == 'CS':
            cs(it[1], it[2])
        else:
            q.append(it + ('plan',))
    t = 0
    R0 = None
    pend = []                   # (x, t, art, block, schluss)
    begonnen = set()            # Blöcke, deren Schlusskontrollsatz begonnen hat
    G1 = G1f = R1 = Xs = S1X = S1A = alarm = nref = G1L = WA = 0

    def ziehe():
        c = (g(0, sc), g(0, sc), g(0, sc))
        return c[0] + c[1] + c[2], c

    while q:
        it = q.popleft()
        art, block, schluss = it[0], it[1], it[2]
        if schluss:
            begonnen.add(block)
        if art in ('R', 'R1', 'R2', 'R3'):
            s, c = ziehe(); tt = t; t += 1; nref += 1
            if R0 is not None:
                ch = ([3] if abs(s - R0[0]) > tS else []) + [k for k in range(3) if abs(c[k] - R0[1][k]) > tC[k]]
                if ch:
                    alarm += 1
                    if streng and it[3] == 'W':
                        WA += 1
                        cs(block, False, vorn=True)          # erneute Wiederaufnahme, R₀ unverändert
                        continue
                    s2, c2 = ziehe(); t2 = t; t += 1; nref += 1
                    rep = [k for k in ch if (abs(s2 - R0[0]) > tS if k == 3 else abs(c2[k] - R0[1][k]) > tC[k])]
                    if rep:
                        S1A += 1
                        cs(block, False, vorn=True)          # Wiederaufnahme
                        continue
                    s, c, tt = s2, c2, t2
            if R0 is not None and pend:
                ins, halt = [], False
                for x, tx, xart, xb, xs in pend:
                    be = (tx - R0[2]) / (tt - R0[2])
                    if abs(x - ((1 - be) * R0[0] + be * s)) > eps:
                        G1 += 1
                        G1L += xart == 'L'
                        if xart == 'XS':
                            S1X += 1; halt = True
                        elif (xart == 'L' and xs) or (xb in begonnen):
                            pass                               # spät erkannt: weder Wiederholung noch S1
                        else:
                            G1f += 1
                            ins += [('R2', xb, False), ('XS', xb, False), ('R3', xb, False)]
                if halt:
                    ins += [None]
                q.extendleft(reversed([z + ('plan',) for z in ins if z is not None]))
                if halt:
                    pend = []
                    R0 = (s, c, tt)
                    cs(block, False, vorn=True)              # Wiederaufnahme nach R₃
                    continue
            pend = []
            R0 = (s, c, tt)
        else:                                  # K, L, XS
            s, c = ziehe(); tx = t; t += 1
            Xs += art == 'XS'
            pend.append((s, tx, art, block, schluss))
            if art != 'XS' and R0 is not None and abs(s - R0[0]) > eps:
                R1 += 1
                q.appendleft(('R1', block, False, 'plan'))
    return G1, G1f, R1, Xs, S1X, S1A, alarm, t, nref, G1L, WA
