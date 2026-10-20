# Kleine Proben zum Regelstand 2026-11

Stand 20.10.2026 · Skript [`kleine_proben.py`](kleine_proben.py) · Lizenz: Code MIT, Text CC BY 4.0.

Die Proben gehören zum Auftrag vom 20.10.2026 (Gesamtumsetzung a–d der Entscheidungsvorlage vom 19.10.2026, **ohne
große Kalibrierung**). Es sind Funktionsnachweise und Beispiele mit festen Seeds und kleinen Zahlen. Sie bestätigen
weder eine Fehlausschlussrate noch eine Power, eine Überdeckung oder eine Vollständigkeitsrate. Profil
`ENTW-2026-11` mit reduzierten Replikaten (B = 100, H3-MC = 100, ε_ctrl-Datensätze 200). Ein Prozess, ein BLAS-Thread (die
Umgebungsvariablen waren bei den Läufen gesetzt; das Skript setzt sie inzwischen selbst vor dem Import von NumPy und
hält sie im Ergebnis fest).

Die Ergebnisdateien sind nach den Korrekturen aus dem statischen Review vom 20.10.2026 neu gerechnet: G4-Schwellen der
Phase 1 aus den gültigen Phase-0-Läufen, Pilotgröße von B+ an der Soll-Lage, Reihenfolge und Zähler von ablauf-4.
Gegenüber dem ersten Lauf geändert sind nur die B+-Trenderkennung bei N01-A4 (0,5 %: 30 → 32 von 48 flach, 3 → 4 von 72
steil; 1 %: 35 → 37 von 72 steil), der Weg über Ebene Z (86 → 87 Versuche) und der neue Zähler
`aufwaermen_tagesbeginn`. Die Zähler unter dem Nullmodell und alle Ausgänge sind gleich.

```
python3 rechnungen/regelstand_2026-11/kleine_proben.py g4    # → probe_g4.json
python3 rechnungen/regelstand_2026-11/kleine_proben.py e2e   # → probe_e2e.json (Ebene Z in ebene_z/, nicht versioniert)
```

## G4: gepaarte Diagnose auf denselben Läufen (`probe_g4.json`, 35 s)

Je System 3 Kampagnen mit 8 Blöcken (Phase 1 statisch, G4 hängt nicht vom Ablauf ab), 504 K-Läufe der Einstellung 1.
Dieselben Läufe werden mit drei Schwellen geprüft: der historischen Regel je Laufart, B+ (Standard 2026-11) und D
(Diagnosemodus, `mit_diagnose(g4__verfahren='d')`). Zähler „ungültig durch G4“ unter dem Nullmodell:

| System | je Laufart (historisch) | B+ (Standard) | D (Diagnose) |
|---|---|---|---|
| N01-A4 | 16/504, davon 6 an steilen Punkten | 5/504, 1 steil | 8/504, 6 steil |
| N01-V1G0 | 29/504, 8 steil | 5/504, 1 steil | 9/504, 7 steil |
| N01-V1G60h | 29/504, 8 steil | 5/504, 1 steil | 9/504, 7 steil |

Flache Punkte (S100, S140) ohne Ausschluss in allen drei Fassungen. V1-G60h mit denselben Zählern wie V1-G0.

Erkennung eines Amplitudentrends ε im letzten Fünftel (exakt über F_min − ⟨N⟩ ∝ Amplitude; Zähler/Nenner, N01-A4 bzw.
V1):

| ε | Punkte | je Laufart | B+ | D |
|---|---|---|---|---|
| 0,5 % | flach | 32/48 bzw. 40/48 | 32/48 bzw. 40/48 | 48/48 |
| 0,5 % | steil | 17/72 bzw. 28/72 | 4/72 bzw. 5/72 | 30/72 bzw. 48/72 |
| 1 % | flach | 48/48 | 48/48 | 48/48 |
| 1 % | steil | 54/72 bzw. 63/72 | 37/72 bzw. 35/72 | 70/72 |

Lesart: B+ schließt unter dem Nullmodell weniger Läufe aus und erkennt Trends unter etwa 1 % an steilen Punkten kaum;
D erkennt sie, schließt aber an steilen Punkten mehr aus. Das entspricht der Abwägung der Vorlage (2.3, F-b1); die
Entscheidung „B+ als Standard, D als Diagnose“ ist eine Arbeitsfestlegung des Autors, keine Folge dieser Probe. Das
Arbeitsziel ≤ 1,5 % je Konfiguration und Lauf ist damit nicht bestätigt (5/504 ist eine Probe, keine Rate je
Konfiguration).

## End-to-End mit Ablauf ablauf-4 (`probe_e2e.json`, 105 s)

Plan n₀ = n_Pilot = 20, 8 Blöcke, P0.7-Anordnung, Verfahren `zustand` (ablauf-4), n_min = 6, je Fall eine Kampagne:

| Fall | H1 | H2 | Ablauf | Halte, Wiederaufnahmen |
|---|---|---|---|---|
| N01-A4/201 | bestätigt | bestätigt | abgeschlossen | – |
| N01-V1G0/202 | bestätigt | bestätigt | abgeschlossen | – |
| A04-R4/203 (Kopplung) | falsifiziert | bestätigt | abgeschlossen | – |
| S02-kontrolllauf/204 | nicht entscheidbar (Datenlage) | nicht entscheidbar | abgeschlossen | S2, eine simulierte Wiederaufnahme, 4 Kontrollsatzläufe |
| S01a-liftoff/205 | nicht entscheidbar (Datenlage) | nicht entscheidbar | abgebrochen | zweites S2 ohne Apparaturfehler: endgültig beendet |

E3 in allen Fällen „unbestimmt“ bzw. nicht gerechnet (Option B mit Rückfall; einzelne Kampagnen sagen über die Raten
nichts). Weg über Ebene Z/Stufe 1 (N01-A4, 3 Blöcke): abgeschlossen, 87 Versuche, Fünftelzeiger in der
Laufzusammenfassung vorhanden (`stufe1-0.2`).

## Weitere kleine Rechnungen dieses Auftrags

| Rechnung | Umfang | Kernsekunden | Ort |
|---|---|---|---|
| Belegpaket der Entscheidungsvorlage (Nachrechnung der Vorlagezahlen auf Statistikebene) | Skripte des Belegpakets | 385 | [`docs/entscheidungsvorlage_2026-10-19_belege/`](../../docs/entscheidungsvorlage_2026-10-19_belege/README.md) |
| E3 Option B: Grenzen, Randprüfung | kleine Monte-Carlo-Prüfungen der Grenzen während der Umsetzung | ≈ 190 | – (geprüft durch `tests/test_e3_grenzen.py`) |
| Teil d: R1-d, R2-d, R3-d in Kleinstgröße, Diagnosen | 45 Sätze; 2 × 2 × (3 + 3) Kampagnen; 2 + 2 Kampagnen; Schätzer- und Bitgleichheitsprüfungen | ≈ 540 | Ergebnisse in der Softwaredoku, Abschnitt 1d |
| G4-Probe und End-to-End (oben), erster Lauf | | 141 | – |
| G4-Probe und End-to-End nach den Korrekturen aus dem Review (Stand oben) | | 140 | `probe_g4.json`, `probe_e2e.json` |
| Gegenprobe der historischen Vorgaben gegen `main` (ENTW-2026-10: Dateikette, zwei Ablaufkampagnen, je Stand) | | 20 | Softwaredoku, Abschnitt 1d |
| Demonstration des Kalibrierbeispiels | 9 Kampagnen, Fortsetzung aus Checkpoints | 73 | [`rechnungen/kalibrierbeispiel/demo_ergebnis/`](../kalibrierbeispiel/README.md) |
| Laufzeitproben vor den Teilrechnungen, Kleinstproben während der Umsetzung | | ≈ 20 | – |
| R3-d-Nachrechnung des Phase-0-Hakens im Gesamtstand | 2 + 2 Kampagnen, ein Kandidat | 18 | Softwaredoku, Abschnitt 1d |
| Ablauf-Prüfsatz ablauf-4 (Erzeugung) | 5 Prüfkampagnen | 23 | `tests/fixtures/ap13_ablauf_pruefsatz_ablauf4.json` |

Zusammen etwa 1560 Kernsekunden (≈ 0,45 Kernstunden) neben der Testsuite, unter der Grenze von zwei Kernstunden;
höchstens vier Prozesse, ein BLAS-Thread je Prozess. Die Angaben „≈“ sind aus den Berichten der Teilbearbeitungen
übernommen (process_time bzw. Wandzeit bei einem Prozess). **Die große Kalibrierung, die volle Matrix und große
Planungsläufe wurden nicht ausgeführt.**
