# k-Konsistenz und Wiederholungsablauf für AP-13 (17.10.2026)

Synthetische Entwicklungsdiagnostik zu AP-11 und AP-13 (Auftrag „k-Konsistenz und Wiederholungsablauf für AP-13“ vom
17.10.2026). Ausgangsstand ist `main` 2ab6d28 (PR #22 gemergt; `main` hat sich bis zum PR nicht weiterbewegt). Der
Auftrag umfasst zwei technische Änderungen:

- Die Phase-0-Größen, von denen G4 und die übrigen Phase-1-Schwellen abhängen, sind an k_max und N_z des tatsächlich
  verwendeten Plans gebunden (Abschnitt 1).
- Phase 1 läuft in der Simulation auf Wunsch als zustandsbehafteter Ablauf mit den Wiederholungen nach §6, §8.8, §9.1,
  §9.2 und A9.12, auf Ebene H und über Ebene Z/Stufe 1 (Abschnitt 2).

Präregistrierung, Regelprofile, G4-Formel mit Faktor 3, Poolregel und normative Schwellen sind unverändert. Alle Zahlen
sind Entwicklungswerte: reduzierte Replikatzahlen (Profil ENTW-2026-10 mit B = 1000, H3-MC 1000, 1000
ε_ctrl-Datensätze), zehn Kampagnen je System und Variante. Sie qualifizieren keine Wahrscheinlichkeit. Es gibt keine
Power-Aussage und keine 0,95-Aussage.

**Ergebnis in Kürze.**

- **Frage 1 – Phase-0-Größen.** Bis `teil_b-0.2` stammten σ_Δ, die Gültigkeitsmaske der Phase 0 (damit die n₀ⱼ
  Einzelmodulläufe für ŷ⁰ und der S3-Bezug), σ̂_ref, ε_ctrl, p̂, Rauschkovarianzen und gepoolte Streuungen aus einem
  Satz bei k der Pilotgrößen. Teil B prüfte Phase 1 aber mit k_max des Plans. Bei A4 waren das k = 30 gegen k_max = 9,
  bei V1-G0 und V1-G60h stimmen beide überein (12).
  - Jetzt entstehen alle diese Größen als ein Satz bei k_max und N_z des verwendeten Plans, mit Bindung und
    Datenprüfsumme. Unvereinbare Eingaben brechen ab, der Arbeitspunkt wird ohne Nachoptimieren neu geprüft, alte
    Dateien gelten als historisch.
  - A4 (zehn Seeds): Ausfälle der Piloten 12/600 → 8/600; σ_Δ,F im Mittel 1,84 → 1,66 mN, im Einzelfall in beide
    Richtungen; G4-Ausfälle der Konfigurationsläufe in Phase 1 166 → 221 von 5040. V1-G0 und V1-G60h sind bitgleich.
- **Frage 2 – Ablauf.** Mit Wiederholungen kommen je Kampagne 11–78 Versuche hinzu (Mittel 33).
  - Die Laufzeit abgeschlossener Kampagnen steigt im Mittel um 5,4 % (höchstens 9,5 %).
  - In den 25 abgeschlossenen Kampagnen (12 600 Plätze) sind 580 Plätze ersetzt. Es fehlen 11: 7 nach ausgeschöpfter
    Grenze, 4 nach spät erkannter Ungültigkeit.
  - 5 von 30 Kampagnen halten an und zählen nicht als abgeschlossen: S1 nach reproduziertem Nullpunktalarm (2), S1
    nach G1-Verstoß von X′ (2), S3 (1).
- **Frage 3 – Vollständigkeit.** Gemeinsam vollständig sind 25/30 (historisch), 24/30 (k-konsistent ohne
  Wiederholungen) und 25/30 (mit Wiederholungen).
  - Der k-Effekt betrifft nur A4: 10/10 → 9/10, weil ein Punkt (S116) mit 17 gültigen Läufen unter n_min = 18 fällt.
  - Der Ablauf ändert die Ursache. Ohne Wiederholungen fehlen in 6 Kampagnen einzelne Punkte (weniger als n_min
    gültige Läufe). Mit Wiederholungen ist jede abgeschlossene Kampagne vollständig (mindestens 23 von 24 gültigen
    Läufen je Punkt); verloren gehen Kampagnen nur durch Halte.
  - Mit zehn Seeds je System sind die Unterschiede nicht aufgelöst (Wilson-Intervalle in Abschnitt 3).
- **Frage 4 – nicht übertragbar.** Nicht übertragbar sind: Werkzeug 8 (c, Rauschbias, H2-Intervalltyp) von PR #21 und
  #22, die gemeinsame Bestätigungswahrscheinlichkeit und alle Raten des Prüfstands, das Planungsergebnis K12, die
  E3-Zähler und die Reserveaussage „40/40 mit Wiederholungen“ von PR #22 (Abschnitt 4). Sie sind mit statischem
  Laufplan und bei A4 mit Phase-0-Größen bei k = 30 gerechnet. Die Neuläufe sind abgeschätzt, nicht gestartet
  (Abschnitt 5).

**Rechenumfang.** Insgesamt 104 Kampagnenausführungen (Grenze 120):

- 90 Vergleichskampagnen;
- 6 volle Ketten mit Stufe 2, davon 2 über Ebene Z/Stufe 1 (Grenze 12);
- 3 Regelpfadfälle;
- die Fortsetzung, gezählt doppelt (unterbrochen und fortgesetzt sowie ununterbrochen);
- außerhalb der Auftragsliste eine Diagnosekampagne (S06) und zwei Gegenproben am Endstand (Abschnitt 7).

Gerechnet mit 4 Prozessen und je einem BLAS-Thread: 0,20 Kernstunden (Grenze 4). Die Wandzeit betrug 33 s für den
Startsatz und 9 min 19 s für die übrigen Aufträge. Kein Matrixlauf, keine Kalibrierung, keine Schwellenoptimierung.

**Aufruf** (vom Repository-Stamm):

```bash
python3 code/pcmms_auswertung harness ablauf-vergleich --vorbereiten   # einmalig, erledigt (auftrag.json, committet vor den Rechnungen)
python3 code/pcmms_auswertung harness ablauf-vergleich --startsatz     # Startsatz: Laufzeitmessung und Hochrechnung
python3 code/pcmms_auswertung harness ablauf-vergleich                 # alle Aufträge; passende Checkpoints werden übernommen
python3 code/pcmms_auswertung harness ablauf-vergleich --bericht       # ergebnisse.json, kampagnen.csv, Tabellen dieses Berichts
python3 code/pcmms_auswertung harness ablauf-pruefsatz --pruefen tests/fixtures/ap13_ablauf_pruefsatz
```

Rechnungen laufen nur aus einem sauberen Git-Stand; die Checkpoints liegen unter `/tmp/pcmms-ablauf-vergleich-20261017/`,
nicht im Repository. Ihr Schlüssel umfasst den Rechencode ohne Kommandozeile und Berichtsteil, den Auftrag, die
gemeinsamen Einstellungen, das Profil, Werkzeug 8, die Seeds, das Verfahren der Variante (Bindung, Ablauf, Ablaufversion,
Optionen) und die Bibliotheken. Berichtskorrekturen (`harness/ablauf_vergleich_bericht.py`) wiederholen keine Rechnung.
Die Checkpoints passen zum Rechencode von 13f2a20; `--bericht` und Übernahmen laufen auf diesem Stand (Abschnitt 7).

## 1 Phase-0-Größen: bisher an k der Pilotgrößen, jetzt an den Plan gebunden (Frage 1)

**Bis `pilot-0.2`/`teil_b-0.2`.** Das Pilotskript bildete vor der Arbeitspunktsuche einen vorläufigen Satz bei
k = max(min(k_b, K), 3), mit k_b aus der Bandgrenze der Pilotanalyse. Teil B übernahm diesen Satz und setzte k_max aus
dem Plan. Auch nach einer erfolgreichen Suche blieb der vorläufige Satz maßgeblich; der Satz beim gefundenen Paar
(k, N_z) wurde nicht weitergereicht. Betroffen sind alle Größen der Reihenfolge der Schwellen nach A9.2, nicht nur σ_Δ:

| Größe | hängt ab von | Wirkung in Phase 1 |
|---|---|---|
| σ_Δ,N, σ_Δ,F (Fünftel-Differenzen der Piloten) | k (D_F über F_min aus k Harmonischen), N_z (Fünftel) | Schwelle von G4 (Faktor 3) |
| Gültigkeitsmaske der Phase 0 (G2–G10, darin G4 mit diesem σ_Δ) | σ_Δ, k | Auswahl der n₀ⱼ Einzelmodulläufe für ŷ⁰, Bezug von S3 |
| σ̂_ref (Summe, Zellen) | Maske der Referenzläufe | Nullpunktalarm, ε_ctrl |
| ε_ctrl mit simuliertem kritischem Wert (A9.8) | Maske, σ̂_ref, Seed der Simulation | G1, Vorprüfung, S1 |
| p̂ (Anteil ungültiger Piloten nach G1) | Maske, ε_ctrl | Reserve r(p̂), n_max |
| Rauschkovarianzen je Laufart, gepoolte Streuungen s_q | Maske, k | Planung, Streuungsangaben in Teil B |
| Rampenhinweis (Liftoff in Piloten) | Maske | Hinweis T_ramp |

Bei A4 war k_b = 30 (Bandende als untere Schranke für f₁, starre Auflage), k_max des Plans aber 9: Phase 1 verglich
D_F aus 9 Harmonischen mit 3·σ_Δ,F aus 30 Harmonischen, und Phase-0-Maske, p̂ und Reserve stammten aus derselben
Rechnung bei k = 30. Bei V1-G0 und V1-G60h ist k_b = k_max = 12.

**Jetzt (`pilot-0.3`, `teil_b-0.3`).** Alle Größen der Tabelle entstehen als ein Satz bei k_max und N_z des
verwendeten Plans, mit demselben Code und Seed wie im Pilotskript (`pilot.satz_fuer_plan`). Der Satz trägt seine
Bindung: k, N_z, Fünftelzahl, T_a, Herkunft, Prüfsumme der Phase-0-Läufe, Zahl der Läufe und Piloten, Seed und
Datensatzzahl der ε_ctrl-Simulation, Version.

- Teil B (`teil_b.phase0_satz`) übernimmt einen Satz der Pilotausgabe nur bei gleichem k, N_z und gleicher Prüfsumme
  (oberste Ebene oder Satz der Suche), sonst rechnet es ihn neu.
- Abweichendes N_z der Läufe, ein Satz gleicher Bindung aus anderen Phase-0-Daten und ein fehlender Seed brechen ab;
  es entsteht kein scheinbar qualifizierter Teil B.
- `nr2.phase0_bindung` nennt Modus, k, N_z, Herkunft und ob neu gerechnet wurde.
- `nr2.arbeitspunkt` prüft den Plan mit dem gebundenen p̂ erneut, ohne neue Suche: Reserve r(p̂), n ≤ n_max(p̂) bei
  Zeitangaben, p̂ des Plans, Übereinstimmung mit der Suche. Status „abgesichert“ (Plan aus der Suche, alle Prüfungen
  bestanden), „nicht abgesichert“ (eine Prüfung verfehlt, auch jede historische Bindung) oder „nicht geprüft“
  (externer Plan).
- Ältere Pilot- und Teil-B-Dateien bleiben lesbar. `pilot.einordnen` und `teil_b.einordnen` ordnen sie als
  „historisch, Größen bei k der Pilotgrößen, nicht qualifiziert“ ein; Stufe 2 nennt die Einordnung unter
  `herkunft.teil_b`.
- Alle Aufrufpfade nutzen die Bindung an den Plan: Kette, Dateikette (`ap11 teil-b`), Kampagnen, Kalibrierung,
  Planungshaken, Ebenenvergleich und Prüfstand. Die Treiber von PR #21 und PR #22 rechnen ausdrücklich `historisch`
  nach; ihre Ergebnisse sind unverändert.
- Regressionen (`tests/test_ap13_kmax.py`): k = 30 → 9 an A4, ein Fall ohne k-Wechsel (V1-G0), ein extern übergebener
  Plan (k = 5) mit Zurückweisungen, der Planungshaken (k = 7) und der Suchpfad (k = 8, „abgesichert“). Geprüft wird an
  direkt aus den Fünfteln nachgerechneten Differenzen D_N, D_F. Am alten Stand scheitern die Prüfungen: σ_Δ,F 1,987 mN
  im alten Teil B gegen 1,237 mN direkt bei k = 9 (A4, Seed 24).

**Wirkung in der begrenzten Rechnung** (gleiche Phase-0-Daten und Seeds, Plan n = 24, n_min = 18, r = 6):

- **A4, k = 30 → 9** (zehn Kampagnen, Variante historisch gegen k-konsistent ohne Wiederholungen):
  - σ_Δ,F: im Mittel 1,840 → 1,661 mN. Die Einzelwerte ändern sich um −0,59 bis +0,55 mN, in 7 von 10 Kampagnen nach
    unten. σ_Δ,N bleibt gleich (⟨N⟩ hängt nicht von k ab).
  - Ungültige Piloten (p̂): 12/600 → 8/600, je Kampagne 0–5 → 0–2 von 60.
  - Gültige Einzelmodulläufe der Phase 0 (n₀ⱼ, Grundlage von ŷ⁰ und des S3-Bezugs): 582 → 585 von 600.
  - ε_ctrl ist in allen zehn Kampagnen gleich.
  - G4 in Phase 1: 166 → 221 von 5040 Konfigurationsläufen (3,3 % → 4,4 %). Je Kampagne ändert sich die Zahl in beide
    Richtungen (2–42 → 10–36).
- **V1-G0 und V1-G60h** (k_b = k_max = 12): p̂, σ_Δ, ε_ctrl, n₀ⱼ, Gültigkeit und Auswertbarkeit sind zwischen
  historisch und k-konsistent bitgleich – der Fall ohne k-Wechsel.
- **Arbeitspunkt:** Der Plan der Rechnung ist extern vorgegeben (n = 24, n_min = 18). Die Reserve r(p̂) = 2–4 liegt
  in allen Kampagnen unter r = 6; n ≤ n_max ist ohne Zeitbudget nicht prüfbar.
  - Status k-konsistent: „nicht geprüft“ (30/30).
  - Status historisch: „nicht abgesichert“ (30/30, historische Bindung).
- **Gegenprobe:** Die Variante „historisch“ gibt für alle 30 Kampagnen die gespeicherten Werte von PR #22 wieder
  (Seed, Zahl ungültiger Phase-1-Läufe, p̂, σ_Δ,F, k der Pilotgrößen; `ergebnisse.json`, `pr22`).

## 2 Ablauf der Phase 1: zusätzliche Versuche, Messzeit, Ersatz, Fehlen und Halt (Frage 2)

**Umsetzung** (`ablauf.py`, Version `ablauf-1`; Verfahren `zustand` in `verfahren.py`):

- Die geplante Reihenfolge (Laufplan mit dem Reihenfolgegenerator von §6) und die ausgeführte Reihenfolge sind
  getrennt. Jeder Versuch hat eine Kennung, den Bezug zum geplanten Lauf, einen Versuchszähler, Rolle, Anlass,
  Zeitpunkt sowie Gültigkeits- und Alarmgründe. Verworfene und ersetzte Versuche bleiben in der Tabelle.
- Jeder Versuch dauert T_Lauf. Spätere Läufe verschieben sich, die zeitabhängigen Effekte (Nullpunktdrift) folgen dem
  tatsächlichen Zeitpunkt, ein Messtag beginnt nach der Tagespause.
- Die Messung erhält nur die Kopfangaben. Entschieden wird mit dem, was zu diesem Zeitpunkt feststeht: G2–G10 nach dem
  Lauf, Vorprüfung gegen R₀ sofort, G1 mit dem nächsten gültigen Referenzlauf, Nullpunktalarm gegen den vorangehenden
  gültigen Referenzlauf, S1–S4. Wahrheit, H1/H2, E3 und Messwerte anderer Versuche zur Auswahl werden nicht benutzt
  (Test mit Prüfung der Quelltexte).
- Wiederholungsplätze zieht der Reihenfolgegenerator des Laufplans (Strom `reihenfolge`) gleichverteilt unter den m
  offenen Konfigurationsplätzen des Blocks und dem Platz vor dem Schlusskontrollsatz (`rng.integers(0, m + 1)`). Jede
  Ziehung wird mit m, gezogenem Platz und Einfügestelle protokolliert; die übrigen Läufe behalten ihre Reihenfolge.
- Zufallsströme: Messwerte der geplanten Läufe aus dem Strom `generator` (dieselben Ziehungen wie im statischen
  Laufplan), zusätzliche Versuche aus `generator_versuch` je Versuchsnummer, Ebene Z aus `generator_z_versuch` je
  Kennung, Phase 0 aus `p0` und `generator`, Bootstrap aus `bootstrap` und `teil_b`. Seeds, Ablaufversion und
  Optionen gehören zur Checkpoint-Kennung; ein Ablaufstand mit anderer Kennung wird nicht fortgesetzt.
- Regeln: Konfigurationswiederholung am gezogenen Platz, höchstens zwei je Konfiguration und Block, nur vor Beginn des
  Schlusskontrollsatzes; G1 mit R₀/R₁, beidseitiger Klammerung, R₂/X′/R₃ auch über die Grenze (X′ zählt als
  Wiederholung), S1 bei G1-Verstoß von X′ oder reproduziertem Nullpunktalarm; Kontrolllauf sofort wiederholt,
  höchstens zweimal, dann Halt, bei L′ Fehlen ohne Halt; S2 mit Ausschluss und weiterer Messung, zweites S2 beendet
  Phase 1; S3 mit sofortiger Wiederholung; S4; Aufwärm-Referenzläufe nach §6.
- Ein Halt gibt einen fortsetzbaren Ablaufstand mit Grund zurück. Fortgesetzt wird nur mit einem ausdrücklich
  übergebenen externen Ereignis (Quelle, Zeitpunkt, Befund, Angaben zu mechanischem Eingriff und Apparaturfehler),
  danach mit einem vollständigen Kontrollsatz ohne Alarm. Ein angehaltener Ablauf ist keine abgeschlossene Kampagne:
  Stufe 2 sperrt dann alle Ausgänge („Datenlage“).
- Übergabe an Stufe 2: Die Tabelle enthält alle Versuche mit Ablaufstand. Stufe 2 prüft offline, dass ihre Gültigkeit
  den Entscheidungen des Ablaufs gleicht, und zählt je Konfiguration und Block höchstens einen gültigen Versuch; ein
  Ersatzversuch erzeugt keinen zusätzlichen Block. Ein mit dem Folgeblock geteilter Kontrollsatz zählt einmal.

**Ergebnis** (zehn Kampagnen je System; Plan mit 630 geplanten Läufen der Phase 1, T_Lauf = 17 s):

- **Zusätzliche Versuche:** 995 in 30 Kampagnen (11–78 je Kampagne).
  - 658 Konfigurationswiederholungen, alle nach G4; andere Ungültigkeitsgründe traten in diesen Nullfällen nicht auf.
  - 93 R₁ nach der Vorprüfung, je 31 R₂, X′ und R₃ nach feststehendem G1-Verstoß.
  - 60 Kontrollwiederholungen (55 nach G4, 5 nach Nullpunktalarm eines Kontroll-R).
  - 55 Aufwärm-Referenzläufe über den geplanten hinaus, 25 S3-Wiederholungen, 11 Alarmwiederholungen.
- **Messzeit:** In abgeschlossenen Kampagnen steigt die Laufzeit (Laufzahl × T_Lauf) um 5,0–6,2 % im Mittel je System,
  höchstens um 9,5 %. Die Spanne bis zum letzten Lauf wächst gleich, weil alle Läufe an einem Messtag liegen. Geplant
  sind 10 710 s Laufzeit; die Planungsangabe im Haken trennt geplante und realisierte Zeit, die normative Formel
  bleibt unverändert.
- **Plätze (Konfiguration × Block):**
  - In den 25 abgeschlossenen Kampagnen sind von 12 600 Plätzen 12 009 im ersten Versuch gültig und 580 ersetzt
    (4,6 %). Es fehlen 11: 7 nach ausgeschöpfter Grenze von zwei Wiederholungen, 4 nach Ungültigkeit, die erst nach
    Beginn des Schlusskontrollsatzes feststand.
  - Kein Platz hat mehr als einen gültigen Versuch (Prüfung in Stufe 2).
- **Halte:** 5 von 30 Kampagnen halten an und bleiben ohne Fortsetzung unvollständig:
  - S1 nach reproduziertem Nullpunktalarm: A4 Kampagne 4 (Zelle 3), V1-G0 Kampagne 1 (Zelle 2). Von den 16 sofortigen
    Wiederholungen nach einem Nullpunktalarm (11 außerhalb, 5 innerhalb von Kontrollsätzen) überschritten 2 die
    Schwelle im selben Kanal erneut.
  - S1 nach G1-Verstoß von X′: V1-G0 Kampagnen 2 und 7. Vor dem Schlusskontrollsatz standen bei V1-G0 22 G1-Verstöße
    fest, bei A4 2 und bei V1-G60h 7.
  - S3: V1-G60h Kampagne 7 (Im N₃ in einem Kontrolllauf und in seiner sofortigen Wiederholung über der Schwelle).
  - Die Halte sind Regelausgänge bei exakter Superposition, also Fehlalarme im Sinn von §9.2. S1 hielt 4 von
    30 Kampagnen an (Wilson [5 %; 30 %]). Die Präregistrierung nennt dafür Bonferroni-Schranken von etwa 25–28 % je
    Kampagne mit 565–688 Läufen, für ein reproduziertes S3 höchstens 9,5·10⁻⁴ je Kontrollsatz. Zehn Kampagnen je System
    prüfen diese Raten nicht.

<!-- tabelle:ablauf -->
| System | nicht abgeschlossen (Halt/Abbruch) | Haltregeln | abgeschlossene Kampagnen: zusätzliche Läufe (Mittel, max) | abgeschlossene: Laufzeit realisiert/geplant (Mittel, max) | abgeschlossene: Plätze gültig / ersetzt / fehlend (Grenze, spät) | angehaltene: Plätze bis zum Halt gültig / ersetzt / fehlend, nicht gemessen |
|---|---|---|---|---|---|---|
| N01-A4 | 1/10 [2 %; 40 %] | S1: 1 | 32,9, 55 | 1,052, 1,087 | 4321 / 212 / 3 (1, 2) | 176 / 5 / 0, 323 |
| N01-V1G0 | 3/10 [11 %; 60 %] | S1: 3 | 39,0, 60 | 1,062, 1,095 | 3341 / 184 / 3 (1, 2) | 804 / 41 / 5, 662 |
| N01-V1G60h | 1/10 [2 %; 40 %] | S3: 1 | 31,6, 52 | 1,050, 1,083 | 4347 / 184 / 5 (5, 0) | 143 / 4 / 0, 357 |
<!-- /tabelle -->

Zusätzliche Versuche nach Anlass (Summe über die zehn Kampagnen je System, Variante mit Wiederholungen):

<!-- tabelle:anlaesse -->
| Anlass (Rolle: Grund) | N01-A4 | N01-V1G0 | N01-V1G60h |
|---|---|---|---|
| R1: Vorprüfung | 35 | 38 | 20 |
| R2: G1 | 2 | 22 | 7 |
| R3: G1 | 2 | 22 | 7 |
| X_strich: G1 | 2 | 22 | 7 |
| alarmwiederholung: Nullpunktalarm Summe | 1 | 2 | 1 |
| alarmwiederholung: Nullpunktalarm Summe, Zelle 3 | 1 | 0 | 0 |
| alarmwiederholung: Nullpunktalarm Zelle 1, Zelle 3 | 1 | 0 | 0 |
| alarmwiederholung: Nullpunktalarm Zelle 2 | 0 | 2 | 0 |
| alarmwiederholung: Nullpunktalarm Zelle 3 | 1 | 1 | 1 |
| aufwaermen: Aufwärmen (§6) | 16 | 20 | 19 |
| kontrollwiederholung: Nullpunktalarm (Zelle 1) | 1 | 0 | 0 |
| kontrollwiederholung: Nullpunktalarm (Zelle 2) | 1 | 0 | 0 |
| kontrollwiederholung: Nullpunktalarm (Zelle 3) | 1 | 2 | 0 |
| kontrollwiederholung: ungültig (G4) | 14 | 27 | 14 |
| s3_wiederholung: S3 F_min_rel, Im_N1 | 0 | 1 | 0 |
| s3_wiederholung: S3 F_min_rel, Im_N1, Re_N2, Re_N3 | 0 | 0 | 2 |
| s3_wiederholung: S3 F_min_rel, Im_N2, Re_N3 | 1 | 0 | 0 |
| s3_wiederholung: S3 F_min_rel, Re_N1, Im_N1, Im_N2, Re_N3 | 0 | 1 | 2 |
| s3_wiederholung: S3 F_min_rel, Re_N1, Im_N2, Re_N3 | 0 | 1 | 0 |
| s3_wiederholung: S3 Im_N1, Re_N2 | 0 | 1 | 0 |
| s3_wiederholung: S3 Im_N3 | 4 | 2 | 2 |
| s3_wiederholung: S3 Re_N1 | 0 | 1 | 1 |
| s3_wiederholung: S3 Re_N1, Im_N2 | 0 | 0 | 1 |
| s3_wiederholung: S3 Re_N1, Re_N3 | 0 | 0 | 1 |
| s3_wiederholung: S3 Re_N2 | 0 | 0 | 2 |
| s3_wiederholung: S3 Re_N2, Im_N3 | 0 | 0 | 1 |
| s3_wiederholung: S3 Re_N3 | 0 | 0 | 1 |
| wiederholung: ungültig (G4) | 225 | 227 | 206 |
<!-- /tabelle -->

Regelpfade (Ebene H, je eine Kampagne mit eigenem Seed):

<!-- tabelle:regelpfad -->
| Fall | Status | Halt | zusätzliche Läufe | Ersatz und Fehlen | auswertbar | vollständig |
|---|---|---|---|---|---|---|
| S06-saettigung | angehalten | S3 | 18 | ersetzt: 5, fehlt: spät erkannt: 1, gueltig: 120, nicht gemessen: 378 | 0/21 | nein |
| H-fehlend | abgeschlossen | – | 69 | ersetzt: 52, fehlt: spät erkannt: 1, gueltig: 451 | 21/21 | ja |
| S02-kontrolllauf | angehalten | S2 | 3 | gueltig: 21, nicht gemessen: 483 | 0/21 | nein |
<!-- /tabelle -->

- **S06-saettigung:**
  - Die Übersteuerung von S120 in Block 1 (G5) ist am gezogenen Platz ersetzt.
  - Der übersteuerte Einzelmodullauf der Phase 0 fehlt im S3-Bezug von Modul 1 (n₀₁ = 18).
  - Die Kampagne hält in Block 6 nach S3 an: Re N₂ von L₁ lag in Kontrollsatz 7 und in der sofortigen Wiederholung
    über der Schwelle.
  - Eine zusätzliche Diagnosekampagne mit demselben Seed (ohne Stufe 2, nicht in der Auftragsliste, 2,2 s) zeigt: Die
    Folge stammt nicht aus der Übersteuerung. Beide L₁ sind gültig und ohne Ereignis.
- **H-fehlend:**
  - Alle geplanten Läufe von S118 und S140 sind gestört (G8). Die Wiederholungen ersetzen 52 Plätze, die Kampagne ist
    vollständig.
  - Damit prüft der Fall unter dem Ablauf nicht mehr „fehlende Punkte“. Katalogereignisse betreffen nur geplante Läufe
    (Abschnitt 6); dauerhaft fehlende Punkte prüfen die Tests.
- **S02-kontrolllauf:** Ein Liftoff in L₂ der Phase 1 ist das erste S2. Phase 1 hält nach 32 Versuchen an; der Stand
  ist fortsetzbar, ŷ¹ wäre ungültig (§8.2). Fortgesetzt wird nicht.
- **Fortsetzung aus einem Ablaufstand** (N01-V1G60h, Seed der Vergleichskampagne 0):
  - Der Ablauf ist nach 300 Versuchen technisch unterbrochen und als Datei gespeichert (JSON und NPZ, SHA-256
    `7177b4f9…`).
  - Aus der Datei fortgesetzt, gleicht er dem ununterbrochenen Ablauf in Daten und Köpfen. Eine Fortsetzung mit anderen
    Ablaufoptionen wird zurückgewiesen („anderer Kennung“).
  - Auf Auftragsebene übernahm der zweite Aufruf die neun Checkpoints des Startsatzes („Checkpoint passt –
    übernommen“, `laufprotokoll.txt`).

## 3 Gemeinsame Vollständigkeit und Ausschlüsse: k und Ablauf getrennt (Frage 3)

„Vollständig“ heißt: alle 21 Schnittpunkte auswertbar (Kontaktast und mindestens n_min = 18 gültige Läufe), ŷ¹ gültig
und keine Sperre aller Ausgänge (beim Ablauf auch kein Halt). Ein Randanteil gültiger Einzelläufe ersetzt diese
gemeinsame Zählung nicht. Kampagnenanteile mit 95-%-Wilson-Intervall.

<!-- tabelle:vergleich -->
| System | Variante | vollständig (95-%-Wilson) | auswertbar (Mittel, min) | min. gültige Läufe (Mittel) | G4 je Konfigurationslauf | p̂ (Mittel) | σ_Δ,F [mN] |
|---|---|---|---|---|---|---|---|
| N01-A4 | historisch | 10/10 [72 %; 100 %] | 21,0, 21 | 20,9 | 3,29 % | 0,020 | 1,840 |
| N01-A4 | k-konsistent ohne Wiederholungen | 9/10 [60 %; 98 %] | 20,9, 20 | 19,9 | 4,38 % | 0,013 | 1,661 |
| N01-A4 | k-konsistent mit Wiederholungen | 9/10 [60 %; 98 %] | 18,9, 0 | 22,1 | 4,42 % | 0,013 | 1,661 |
| N01-V1G0 | historisch | 7/10 [40 %; 89 %] | 20,7, 20 | 18,3 | 4,80 % | 0,017 | 1,913 |
| N01-V1G0 | k-konsistent ohne Wiederholungen | 7/10 [40 %; 89 %] | 20,7, 20 | 18,3 | 4,80 % | 0,017 | 1,913 |
| N01-V1G0 | k-konsistent mit Wiederholungen | 7/10 [40 %; 89 %] | 16,8, 0 | 20,3 | 4,83 % | 0,017 | 1,913 |
| N01-V1G60h | historisch | 8/10 [49 %; 94 %] | 20,8, 20 | 19,4 | 4,05 % | 0,012 | 1,957 |
| N01-V1G60h | k-konsistent ohne Wiederholungen | 8/10 [49 %; 94 %] | 20,8, 20 | 19,4 | 4,05 % | 0,012 | 1,957 |
| N01-V1G60h | k-konsistent mit Wiederholungen | 9/10 [60 %; 98 %] | 18,9, 0 | 21,9 | 4,10 % | 0,012 | 1,957 |
<!-- /tabelle -->

Gepaart über dieselben Seeds (k: historisch → k-konsistent; Ablauf: k-konsistent ohne → mit Wiederholungen):

<!-- tabelle:gepaart -->
| System | Unterschied | vollständig vorher → nachher | gewonnen / verloren | Δ G4-Läufe (Mittel ± SE) | Δ auswertbar | Δ min. gültige Läufe |
|---|---|---|---|---|---|---|
| N01-A4 | k (historisch → k-konsistent ohne Wiederholungen) | 10/10 → 9/10 | 0 / 1 | 5,5 ± 5,1 | -0,1 | -1,0 |
| N01-A4 | Ablauf (k-konsistent ohne Wiederholungen → k-konsistent mit Wiederholungen) | 9/10 → 9/10 | 1 / 1 | 0,5 ± 0,8 | -2,0 | 2,2 |
| N01-V1G0 | k (historisch → k-konsistent ohne Wiederholungen) | 7/10 → 7/10 | 0 / 0 | 0,0 ± 0,0 | 0,0 | 0,0 |
| N01-V1G0 | Ablauf (k-konsistent ohne Wiederholungen → k-konsistent mit Wiederholungen) | 7/10 → 7/10 | 3 / 3 | -1,2 ± 2,6 | -3,9 | 2,0 |
| N01-V1G60h | k (historisch → k-konsistent ohne Wiederholungen) | 8/10 → 8/10 | 0 / 0 | 0,0 ± 0,0 | 0,0 | 0,0 |
| N01-V1G60h | Ablauf (k-konsistent ohne Wiederholungen → k-konsistent mit Wiederholungen) | 8/10 → 9/10 | 2 / 1 | 0,7 ± 2,2 | -1,9 | 2,5 |
<!-- /tabelle -->

- **k (historisch → k-konsistent):** Der Effekt betrifft nur A4. Eine Kampagne geht verloren (Kampagne 2: S116 mit 17
  gültigen Läufen); G4 steigt im Mittel um 5,5 ± 5,1 Läufe je Kampagne. Bei V1-G0 und V1-G60h ändert sich nichts.
- **Ablauf (ohne → mit Wiederholungen):** Die Zahl vollständiger Kampagnen bleibt fast gleich (24 → 25 von 30), die
  Ursachen tauschen:
  - Gewonnen werden die 6 Kampagnen, in denen ohne Wiederholungen ein Punkt unter n_min fiel (A4 Kampagne 2, V1-G0
    4, 6, 8, V1-G60h 1, 9).
  - Verloren gehen 5 Kampagnen durch Halte (A4 4, V1-G0 1, 2, 7, V1-G60h 7).
  - In abgeschlossenen Kampagnen hat jeder Punkt mindestens 23 von 24 gültigen Läufen, ohne Wiederholungen 16–22.
  - Der G4-Anteil je Versuch bleibt fast gleich (4,1–4,8 % mit und ohne Wiederholungen). „Auswertbar“ und „min.
    gültige Läufe“ im Mittel enthalten die angehaltenen Kampagnen mit gesperrten Ausgängen.
- **Unsicherheit:** Gewonnen und verloren stehen in derselben Größenordnung, und die Wilson-Intervalle überlappen
  weit. Ob der Ablauf die gemeinsame Vollständigkeit erhöht, entscheidet die Haltrate. Diese hängt an S1/S3 und an der
  nicht simulierbaren Wiederaufnahme. Mit zehn Seeds ist das nicht bestimmbar.

Volle Ketten mit Stufe 2 (Werkzeug 8 A4 aus PR #21 nur als Testwert, B = 1000):

<!-- tabelle:voll -->
| Auftrag | Status | zusätzliche Läufe | Auswahl | H1 | H2 | H3 | H4 | E3 | Datenlage = schlank |
|---|---|---|---|---|---|---|---|---|---|
| N01-A4 k-konsistent ohne Wiederholungen Ebene H | statisch | 0 | – | bestätigt | bestätigt | nicht entscheidbar | bestätigt | unbestimmt | ja |
| A04-R4 k-konsistent ohne Wiederholungen Ebene H | statisch | 0 | – | falsifiziert | bestätigt | nicht entscheidbar | bestätigt | unbestimmt | ja |
| N01-A4 k-konsistent mit Wiederholungen Ebene H | abgeschlossen | 40 | ersetzt: 32, fehlt: Grenze ausgeschöpft: 1, gueltig: 471 | bestätigt | bestätigt | nicht entscheidbar | bestätigt | unbestimmt | ja |
| A04-R4 k-konsistent mit Wiederholungen Ebene H | abgeschlossen | 20 | ersetzt: 17, gueltig: 487 | falsifiziert | bestätigt | nicht entscheidbar | bestätigt | unbestimmt | ja |
| N01-A4 k-konsistent mit Wiederholungen Ebene Z | abgeschlossen | 39 | ersetzt: 24, gueltig: 480 | bestätigt | bestätigt | nicht entscheidbar | bestätigt | unbestimmt | ja |
| A04-R4 k-konsistent mit Wiederholungen Ebene Z | abgeschlossen | 34 | ersetzt: 19, fehlt: spät erkannt: 1, gueltig: 484 | falsifiziert | bestätigt | nicht entscheidbar | bestätigt | unbestimmt | ja |
<!-- /tabelle -->

- Die Entscheidungen bleiben in allen sechs Ketten gleich:
  - N01-A4: H1, H1Z, H2 und H4 bestätigt.
  - A04-R4: H1 und H1Z falsifiziert, H2 und H4 bestätigt.
  - H3 ist bei A4 nicht entscheidbar (starre Auflage, P0.4 nicht identifizierbar); E3 ist „unbestimmt“.
- Das gilt auf Ebene H und über Ebene Z/Stufe 1, wo dieselbe Ablaufsteuerung auf den Stufe-1-Zusammenfassungen
  entscheidet (39 bzw. 34 zusätzliche Versuche).
- Die Datenlage von Stufe 2 gleicht in allen sechs Ketten der schlanken Auswertung. Die Herkunft des Ergebnisses nennt
  den Ablaufstand („abgeschlossen“).
- c ist ein Testwert aus PR #21; die Ketten prüfen den Durchlauf, nicht die Fehlerraten.

## 4 Nicht übertragbare Kalibrierungen und Aussagen (Frage 4)

Historische Ergebnisse behalten ihre Herkunft und bleiben unverändert im Repository. Für den neuen Ablauf und die
Bindung an den Plan gelten sie nicht automatisch: Ausschlussmasken, Zahl und Zeitlage der gültigen Läufe je Punkt und
der Anteil verwertbarer Kampagnen ändern sich.

| Ergebnis (Herkunft) | Rechenweg | warum nicht übertragbar | nötig |
|---|---|---|---|
| Werkzeug 8 A4 und V1-G0: c_H1, c_H1Z, Rauschbias b⁰/b¹ (Summe, Zellen), H2-Intervalltyp, Prüfraten, Poolentscheid (PR #21, `ap13_neulaeufe_2026-10-17/`) | statischer Laufplan; A4 mit Phase-0-Größen bei k = 30 | A4: andere G4-Schwelle, Phase-0-Maske, n₀ⱼ und p̂; beide: der Ablauf ändert Zahl, Auswahl und Zeitlage der gültigen Läufe je Punkt und lässt Kampagnen anhalten; c ist ein Quantil über die Kampagnen, b und die H2-Überdeckung hängen an denselben Stichproben | Kalibrier- und Prüfsimulation mit Bindung an den Plan und Ablauf `zustand` |
| Werkzeug 8 V1-G60h (PR #22, `e3b_g4_diagnose_2026-10-17/`) | statischer Laufplan, k = k_max | Ablauf wie oben | wie oben |
| Testvorgabe von Werkzeug 8 | keine Kalibrierung | nur Software-Testwert | – |
| P(H1 und H2 bestätigt \| exakt) 0,965 / 0,82 / 0,75 (Prüfstand `7a259ef`) | statisch, historische Bindung | Datenlage-Verluste entfallen mit dem Ablauf weitgehend, dafür halten Kampagnen an (Abschnitt 3) | Neuberechnung mit neu kalibriertem c |
| Planungsergebnis K12 „kein zulässiger Arbeitspunkt“ (PR #21) | Kandidatenraten mit statischem Laufplan, Satz bei k der Pilotgrößen | Raten je Kandidat ändern sich mit Ablauf und Bindung | Planungssimulation je Kandidat mit `--verfahren zustand` |
| Raten des Prüfstands und Kriterienmatrix (`7a259ef`, `docs/ap11_ap12_ap13_pruefstand.json`) | statisch, historisch | wie oben; Ablauf- und Haltraten fehlen ganz | Matrix mit dem neuen Ablauf (nicht beauftragt) |
| E3-Raten (570 Kampagnen, PR #21) und E3b-Nachzählung (PR #22) | statisch; A4 mit Phase-0-Maske bei k = 30 | n₀ⱼ (ŷ⁰) und gültige Kontrollläufe (ŷ¹, mit Kontrollwiederholungen) ändern sich; die Ursache „Betrag des komplexen Residuums“ bleibt strukturell, die Zähler sind historisch | Neulauf der gewählten E3-Punkte |
| Reserve „erwartete Ausfälle + 2 reicht mit Wiederholungen“, mit Wiederholungen 40/40 je System vollständig, alle 120 (PR #22, Abschnitt 3) | Ersatzläufe am ursprünglichen Zeitplatz, ohne Referenzen, Alarm und Halt | der Ablauf zeigt zusätzlich Halte nach S1 und S3 (Abschnitt 3); 40/40 war kein Nachweis einer Vollständigkeitswahrscheinlichkeit | Ziel der gemeinsamen Vollständigkeit festlegen, dann Planung |
| G4-Raten je Konfiguration (PR #22) | A4 in Variante „v0“ mit σ_Δ bei k = 30; „v0k“ entspricht der neuen Bindung | Variante v0 bei A4 nicht mehr maßgeblich | Entscheidung zur Standardisierung bleibt offen |
| Software-Prüfsatz `tests/fixtures/ap13_pruefsatz` | Generatorausgaben des statischen Laufplans | gilt weiter als Softwarereferenz des statischen Laufplans, nicht für den Ablauf | Ablauf-Prüfsatz ergänzt |

## 5 Künftige Neuläufe (grobe Abschätzung, nicht gestartet)

Gemessene Laufzeiten dieser Rechnung (je Kampagne und Kern):

<!-- tabelle:laufzeit -->
| Art | Kampagnen | Sekunden je Kampagne (Mittel, max) |
|---|---|---|
| fortsetzung/H/wiederholungen | 1 | 9,0, 9,0 |
| schlank/H/historisch | 30 | 2,0, 2,7 |
| schlank/H/k_konsistent | 30 | 2,0, 2,6 |
| schlank/H/wiederholungen | 33 | 2,6, 3,6 |
| voll/H/k_konsistent | 2 | 5,1, 5,2 |
| voll/H/wiederholungen | 2 | 5,6, 5,7 |
| voll/Z/wiederholungen | 2 | 234,2, 234,8 |
| zusammen | 100 | 704 Kernsekunden (0,196 Kernstunden), Wandzeit 589 s |
<!-- /tabelle -->

<!-- tabelle:abschaetzung -->
| künftiger Lauf (nicht gestartet) | Kernstunden (grob) |
|---|---|
| Kalibrier- und Prüfsimulation von c je System (1000 + 1000 Kampagnen, B = 10 000) | 18,4–81,1 |
| dasselbe für A4, V1-G0 und V1-G60h | 55,1–243,3 |
| Planungssimulation je Kandidat (n_min, n₀) und Paar (k, T_a) | 18,4–81,1 |
| Zähl- und Ablaufdiagnose ohne Stufe 2 je 1000 Kampagnen | 0,7 |
| Ebene Z/Stufe 1 mit Stufe 2 (B = 1000) je 10 Kampagnen | 0,7 |
<!-- /tabelle -->

- **Annahmen:** je System 1000 Kalibrier- und 1000 Prüfkampagnen (normative Zahl), ohne Wiederholung beim Poolen.
  Die Spannen ergeben sich so:
  - untere Grenze: Laufzeiten dieser Rechnung (B = 1000), Bootstrap-Anteil linear auf B = 10 000 skaliert
    (≈ 33 s je Kampagne);
  - obere Grenze: die im Softwaredokument (Abschnitt 5) gemessenen Kampagnen mit normativen Replikatzahlen (68–139 s,
    statisch), mit 5 % Zuschlag für die zusätzlichen Versuche.
- **Planungssimulation:** je Kandidat (n_min, n₀) und Paar (k, T_a) so teuer wie eine Kalibrierung.
- **Reihenfolge, wenn sie beauftragt wird:**
  1. Ziel der gemeinsamen Vollständigkeit und Umgang mit Halten festlegen (offen).
  2. Halt- und Vollständigkeitsraten des Ablaufs mit Zähldiagnosen ohne Stufe 2 bestimmen (≈ 0,7 Kernstunden je 1000
     Kampagnen).
  3. Werkzeug 8 je Referenzsystem neu kalibrieren.
  4. Danach Planungssimulation, Prüfstandsauswahl und E3-Punkte neu rechnen.
- Ebene Z kostet je Kampagne rund 4 min auf einem Kern und bleibt Gegenproben vorbehalten.
- Nichts davon ist gestartet.

## 6 Grenzen, Lesarten und offene Entscheidungen

**Lesarten des Ablaufs**, wo der Regeltext nicht ausdrücklich ist (`ablauf.py`, im Kopf des Moduls geführt; keine
neue Fachregel):

- Der Schlusskontrollsatz eines Blocks ist der Kontrollsatz an seinem Ende; ein mit dem Folgeblock geteilter Satz
  gehört als Schlusskontrollsatz zum vorangehenden Block.
- G1, S1 und die Vorprüfung gegen R₀ betreffen nur Läufe ohne Verstoß gegen G2–G10; ein sonst ungültiger Lauf folgt
  der Wiederholungsregel seiner Art.
- Ein G1-Verstoß, der erst mit dem ersten Referenzlauf des Schlusskontrollsatzes feststeht, gilt als nach dessen
  Beginn festgestellt (keine Wiederholung, keine S1-Prüfung).
- Ein Referenzlauf außerhalb eines Kontrollsatzes, der gegen G2–G10 verstößt, wird nicht wiederholt und ist kein Bezug.
  Ein Alarm der Wiederholung nur in anderen Kanälen führt zu einer weiteren Wiederholung; nach mehr als zehn
  solchen Wiederholungen hält der Ablauf an (technische Grenze ohne Regelausgang; in dieser Rechnung nicht erreicht).
- S3 wird an Lⱼ ohne Verstoß gegen G2–G10 geprüft; eine gültige S3-Wiederholung ist ein gültiger Kontrolllauf.
- Das erste S2 hält an (Abbruchregel S2, §9.2); die Konfiguration bleibt in den Blöcken und ist von Tests
  ausgeschlossen, ein zweites S2 ohne festgestellten Apparaturfehler beendet Phase 1.
- Der Kontrollsatz einer Wiederaufnahme wird in einer vom Reihenfolgegenerator gezogenen Reihenfolge gemessen und muss
  ohne Alarm bleiben; eine Wiederaufnahme nach mechanischem Eingriff ist nicht umgesetzt (Vergleich mit Phase 0, §9.2,
  Testlogik offen) und wird zurückgewiesen.
- Katalogereignisse mit Auswahl nach Konfiguration oder Lauf betreffen die geplanten Läufe; zusätzliche Versuche nur
  Ereignisse mit Versuchsauswahl (`versuch`). In H-fehlend und S06 sind die Wiederholungen daher ungestört; eine
  dauerhafte Störung aller Versuche prüfen die Tests (ausgeschöpfte Grenze).

**Einstellung 2.** G2–G4 sind für L′ nicht gefasst, und ob S1, S2 und S4 für L′ gelten, ist offen (§12). Der Ablauf
wendet sie nicht an, vermerkt beide Lücken, sobald ein L′ läuft, und gibt keine Qualifikationsaussage für Einstellung 2
(`qualifikation_einstellung2 = „ausgeschlossen“`). Darstellbar und geprüft sind die vorhandenen L′-Ausnahmen (Fehlen
nach zwei ungültigen Wiederholungen ohne Halt). Primärer Funktionsnachweis ist Einstellung 1.

**Grenzen.**

- Nur Simulation (Ebene H und Ebene Z/Stufe 1); keine DAQ- oder Hardwaresteuerung, keine Echtzeitfunktion.
- Angehaltene Kampagnen werden nicht automatisch fortgesetzt: Eine Wiederaufnahme braucht eine Ursachenanalyse, die
  sich nicht simulieren lässt. Ob eine angehaltene Kampagne nach der Analyse vollständig würde, bleibt offen; als
  abgeschlossen zählt sie hier nicht.
- Zehn Kampagnen je System und Variante lösen Raten nicht auf. Die Wilson-Intervalle sind breit; eine
  Vollständigkeits- oder Haltrate ist damit nicht bestimmt.
- Reduzierte Replikatzahlen (B = 1000). Werkzeug 8 A4 stammt aus PR #21 (alter Ablauf, historische Bindung) und dient
  in den vollen Ketten nur als Testwert.
- Die Messzeit ist Laufzahl × T_Lauf und die Spanne vom ersten bis zum letzten Lauf der Phase 1. Umschalt-, Park- und
  Rampenzeiten zwischen den Läufen sind darin nicht gesondert modelliert. Die normative Zeitformel (§5.3 c) ist
  unverändert.

**Offen** (Entscheidungen des Autors, durch diesen Auftrag nicht berührt): G4-Standardisierung je Konfiguration aus
Phase 0 (PR #22), E3-Grenzen und Rückfall, feste E3-Prüfzahl, Ziel der gemeinsamen Vollständigkeit (Mindestwert und
Umgang mit Halten in der Planung), S-Regeln und G2–G4 für L′, Wiederaufnahme nach mechanischem Eingriff. AP-13 bleibt
teilweise bearbeitet.

## 7 Herkunft und Dateien

- Branch `ap13-kmax-wiederholungen-2026-10` in einem eigenen Worktree, Basis `main` = 2ab6d28. Commits:
  - k-Konsistenz (9e3bde8), Ablaufsteuerung und Integration (0ea898f), Tests (edb6460);
  - Auftragsliste vor den Rechnungen (13f2a20);
  - nach den Rechnungen: Berichtsteil (597fc7c, nur `harness/ablauf_vergleich_bericht.py` und dessen Test, außerhalb
    des Rechencodes), Ergebnisse mit diesem Bericht (f33f205), Zurückweisung des Ablaufs in der Dateikette (28bc9dc),
    Dokumentation.
- Alle Kampagnen der Auftragsliste sind auf 13f2a20 aus sauberem Arbeitsbaum gerechnet (Git-Stand je Checkpoint vor
  und nach der Rechnung in `ergebnisse.json`, `checkpoints`), mit vier Arbeitsprozessen und je einem BLAS-Thread.
- 28bc9dc ändert nur die Dateikette, die die Rechnung nicht benutzt. Weil der Rechencode Teil des Checkpoint-Schlüssels
  ist, passen die Checkpoints aber nur zu 13f2a20; `--bericht` und eine Übernahme laufen deshalb auf 13f2a20.
- Gegenprobe am Endstand 28bc9dc: zwei Kampagnen neu gerechnet, ihre Befunde sind ohne Laufzeit gleich
  (`laufprotokoll.txt`). Es sind N01-A4 mit Wiederholungen, Kampagne 0, und N01-V1G0, Kampagne 1 (mit S1-Halt).
- `auftrag.json`: Aufträge, Seeds und ihre Ableitung, Zufallsströme, Varianten mit Verfahrenskennung, Profil mit
  Prüfsumme, Werkzeug 8 mit Inhaltsprüfsumme, Budget.
- `ergebnisse.json`: Vergleich, gepaarte Unterschiede, Gegenprobe gegen PR #22, volle Ketten, Regelpfade, Fortsetzung,
  Laufzeiten, Abschätzung; je Auftrag die Checkpoint-Angaben (Git-Stand, Zeiten, Prüfsummen der Dateien).
- `kampagnen.csv`: eine Zeile je Kampagne (Teil-B-Größen, Gültigkeit, Auswertbarkeit, Ablauf, Laufzeit).
- `laufprotokoll.txt`: Ausgabe der Rechnung (Startsatz und übrige Aufträge, Übernahme der Checkpoints).
- Rohdaten der Ebene Z (je Kampagne rund 0,5 GB) lagen in temporären Verzeichnissen und sind gelöscht; die
  Checkpoints liegen außerhalb des Repositorys.
- Ablauf-Prüfsatz: `tests/fixtures/ap13_ablauf_pruefsatz.json` (fünf Prüfkampagnen, Prüfsummen und lesbare
  Inhaltsgrößen, inhaltliche Gegenprobe ohne gespeicherte Sollwerte). Der Software-Prüfsatz
  `tests/fixtures/ap13_pruefsatz.json` ist unverändert und weiter gleich.
