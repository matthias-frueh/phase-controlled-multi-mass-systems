# Kontrollrechnung zur Entwurfsfassung der Entscheidungsregeln (AP-08)

Stand 02.10.2026 (Skripte und gespeicherte Ausgaben), übernommen 04.10.2026. **Kontrollrechnung zu einem Entwurf, keine
Registrierungszahl**, keine Messdaten. Geprüft wurde die damalige Entwurfsfassung der Entscheidungsregel für H1
(Äquivalenztest nach dem Intersection-Union-Prinzip gegen ŷ⁰ und ŷ¹, Mindesteffekttest mit Δ_rel, simuliertes c mit
Bonferroni-Wert c_B zum Vergleich) gegen die registrierte Regel vom 25.09.2026 (Nicht-Ablehnung plus PB1). Die
Entwurfsfassung ist seither mit PR #14 als vorläufige Arbeitsfestlegung in die
[Präregistrierung v2](../../docs/praeregistrierung_v2_entwurf.md) übernommen (§8.4–§8.6, A8, A9.11); dort gilt
Fassung B als Primärmaß für Re und Im N_k, hier sind A und B nebeneinander gerechnet und Δ_rel = Δ_q in Fassung A.
Der Plan des Pipelinetests ([`docs/plan_ap13_pipelinetest.md`](../../docs/plan_ap13_pipelinetest.md)) zitiert diese
Rechnung als „AP-08-Kontrolle“.

Modell: vereinfachtes Kampagnenmodell wie [`../statistik/s2_h1_oc_kampagne.py`](../statistik/s2_h1_oc_kampagne.py)
(A4-Beispiel: starre Auflage, μ = 0,4, 10 Hz, identische Egg-Module, k_max = 9; weißes Restrauschen σ_h = 0,11 mN plus
Lauf-zu-Lauf-Streuung je Modul in Amplitude und Phase; n = n₀ = 20, n₁ = 21; Bootstrap B = 200). Je Stufe L0–L5:
400 Kalibrierkampagnen bei exakter Superposition → c = q95(max|z⁰|), dann 300 Kampagnen je Szenario (am Rand der
Äquivalenzzone 400). Monte-Carlo-Standardfehler einer Rate 0,05 bei 300 Kampagnen ≈ 0,013.

Start aus diesem Verzeichnis:

```bash
sh run_ap08.sh 0 1 2 3 4 5        # Szenarien exakt, Kopplung 1/3/10/10,6/20/30 %, N₂ 3 %, Drift 3 %; je Stufe ≈ 2–3 min
sh run_ap08_rand.sh 0 1 2 3       # Rand der Äquivalenzzone: Kopplung 10,638 % (Residuum = Δ_F) und 11,5 %
PYTHONPATH=../../code python3 ap08_zahlen.py        # Zahlen der Entwurfstexte (Auslegungsgrenzen, Rauschbias)
PYTHONPATH=../../code python3 ap08_durchmesser.py   # Fassung A gegen B für N₁–N₃ am Schnitt
```

Ausgaben: `ap08_kontrolle_L<n>_ausgabe.txt` und `ap08_kontrolle_L<n>.csv` (Spalten: Stufe, Szenario, Stärke x,
simuliertes c für z⁰ und z¹, Raten der Ausgänge für Fassung A und B, Raten mit c_B, Raten der alten Regel);
`…_rand.csv` für die Randszenarien; `ap08_zahlen_ausgabe.txt`, `ap08_durchmesser_ausgabe.txt`.

Ergebnis in Kurzform (bedingt auf die angenommenen Rauschmodelle):

| Szenario | Regel | L0 | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|---|---|
| Streuung je Modul (Amplitude/Phase) | | Sensor | 0,3 %/0,03° | 1 %/0,1° | 3 %/0,3° | 6 %/0,6° | 10 %/1° |
| simuliertes c (z⁰) gegen c_B ≈ 3,95 | neu | 3,84 | 3,92 | 3,86 | 3,89 | 3,88 | 3,92 |
| exakt: P(bestätigt) | neu A | 1,000 | 1,000 | 1,000 | 1,000 | 0,170 | 0,000 |
| | neu B | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 | 0,290 |
| | alt | 0,957 | 0,937 | 0,940 | 0,900 | 0 | 0 |
| Kopplung 1 %: P(falsifiziert) | neu A | 0 | 0 | 0 | 0 | 0 | 0 |
| | alt | 1,000 | 1,000 | 1,000 | 0,093 | 0,007 | 0 |
| Kopplung 10,638 % (Residuum = Δ_F): P(bestätigt) | neu A/B | 0 | 0 | 0 | 0 | – | – |
| Kopplung 20 %: P(falsifiziert) | neu A | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 | 0,773 |
| | neu B | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 | 0,853 |
| N₂ 3 % / Drift 3 %: P(falsifiziert) | neu A | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |

Abhängigkeiten: `code/linear_solver.py`; numpy, scipy, pandas. Übernahme: Startskripte auf dieses Verzeichnis und
`PYTHONPATH=../../code` umgestellt, Umgebungsbegriff im Docstring ersetzt; Rechenweg und Zahlen unverändert.

Grenzen: nur das A4-Beispiel (starr, identische Module), multiplikative Abweichungen, alle 21 Schnittpunkte
auswertbar, B = 200; die Kalibrierung mit dem vollständigen Verfahren ist Aufgabe von Werkzeug 8 (AP-13).
