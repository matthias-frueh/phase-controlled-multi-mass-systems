"""Bezugsmengen der Simulationen (Regel harness.mengen, Arbeitsfestlegung vom 20.10.2026; Präreg §5.4, §8.4, §8.6,
A9.11) und Nachziehen bis zur Sollzahl der Auswertungsmenge (Regel harness.nachziehen).

- G: alle begonnenen simulierten Kampagnen einer Rolle, einschließlich endgültig beendeter (Halt mit ausgeschöpften
  Wiederaufnahmen, zweites S2). Nenner von P(H1 und H2 bestätigt).
- A: abgeschlossene (auch nach Wiederaufnahme) Kampagnen mit gültigem ŷ¹ und allen benötigten endlichen Prüfgrößen:
  Rohresiduen und Varianzen von H1 (Summe, ŷ⁰ und ŷ¹, 147 Tests) und H1Z (Zellen, 441 Tests) und die H2-Intervalle.
  H1 und H1Z verwenden dieselbe Menge A; c (H1, H1Z), Prüfrate, b̂ und u(b̂), Restbias und H2-Überdeckung beziehen
  sich darauf. Gründe für G ohne A werden getrennt gezählt (der erste zutreffende Grund in der Reihenfolge GRUENDE).

Ein aus A bestimmtes c ist nicht allein wegen einer kleineren Zahl von Tests für jede anders selektierte
unvollständige Kampagne abgesichert; das bleibt eine nur unter benannten Annahmen geltende bzw. noch zu prüfende
Eigenschaft (Bericht).
"""
import math

import numpy as np

GRUENDE = ('nicht abgeschlossen', 'ŷ¹ ungültig', 'H1-Prüfgrößen nicht endlich', 'H1Z-Prüfgrößen nicht endlich',
           'H2-Intervalle fehlen')
FELDER_H1 = ('r0', 'v0', 'r1', 'v1')
FELDER_H1Z = ('rz0', 'vz0', 'rz1', 'vz1')


def grund(b):
    """None, wenn der Kurzbefund b zu A gehört, sonst der Ausschlussgrund (mit Ablaufstatus bzw. Halt)."""
    ab = b.get('ablauf')
    if ab is not None and ab.get('status') != 'abgeschlossen':
        w = ab.get('harness_wiederaufnahme') or {}
        return f'{GRUENDE[0]} ({w.get("grund") or ab.get("status")})'
    if not b.get('yhat1_gueltig'):
        return GRUENDE[1]
    f = b['felder']
    if not all(np.isfinite(np.asarray(f[x], float)).all() for x in FELDER_H1):
        return GRUENDE[2]
    if not all(np.isfinite(np.asarray(f[x], float)).all() for x in FELDER_H1Z):
        return GRUENDE[3]
    if not (b.get('H2') or {}).get('intervalle'):
        return GRUENDE[4]
    return None


def aufteilen(befunde):
    """Mengen G und A einer Rolle: Indizes von A, |G|, Ausschlüsse je Grund (Hauptgrund ohne Klammerzusatz) und je
    vollständigem Grund."""
    A, je, voll = [], {}, {}
    for i, b in enumerate(befunde):
        g = grund(b)
        if g is None:
            A.append(i)
            continue
        haupt = g.split(' (')[0]
        je[haupt] = je.get(haupt, 0) + 1
        voll[g] = voll.get(g, 0) + 1
    return dict(G=len(befunde), A=len(A), indizes_A=A, ausschluesse=je, ausschluesse_genau=voll,
                definition='G: alle begonnenen Kampagnen der Rolle; A: abgeschlossen, ŷ¹ gültig, H1-/H1Z-Prüfgrößen '
                           'endlich, H2-Intervalle vorhanden (Regel harness.mengen)')


def in_A(befunde):
    return [befunde[i] for i in aufteilen(befunde)['indizes_A']]


def nachziehen(laufe, soll_A, versuchslimit_faktor, start_n=None):
    """Kampagnen in Partien nachziehen, bis |A| ≥ soll_A oder das technische Versuchslimit
    ⌈versuchslimit_faktor·soll_A⌉ erreicht ist. laufe(start, n) → Liste von n Kurzbefunden mit den Seeds
    start … start + n − 1 der Rolle. Erste Partie start_n (Vorgabe soll_A), danach je der geschätzte Fehlbetrag.
    Rückgabe dict(befunde, status 'abgeschlossen'/'nicht abgeschlossen', G, A, limit, partien, grund)."""
    if soll_A < 1 or versuchslimit_faktor < 1:
        raise ValueError('nachziehen: soll_A ≥ 1 und versuchslimit_faktor ≥ 1')
    limit = int(math.ceil(versuchslimit_faktor * soll_A))
    befunde, partien = [], []
    n = min(int(start_n or soll_A), limit)
    while True:
        neu = laufe(len(befunde), n)
        if len(neu) != n:
            raise ValueError(f'nachziehen: {len(neu)} statt {n} Befunde')
        befunde += neu
        a = aufteilen(befunde)['A']
        partien.append(dict(start=len(befunde) - n, n=n, A_danach=a))
        if a >= soll_A:
            return dict(befunde=befunde, status='abgeschlossen', G=len(befunde), A=a, soll_A=soll_A, limit=limit,
                        partien=partien, grund=None)
        if len(befunde) >= limit:
            return dict(befunde=befunde, status='nicht abgeschlossen', G=len(befunde), A=a, soll_A=soll_A,
                        limit=limit, partien=partien,
                        grund=f'Versuchslimit {limit} erreicht mit |A| = {a} < {soll_A}: nicht abgeschlossen')
        anteil = a / len(befunde) if a else 1.0 / len(befunde)
        n = min(limit - len(befunde), max(1, int(math.ceil((soll_A - a) / anteil))))
