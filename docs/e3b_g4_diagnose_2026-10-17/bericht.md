# Diagnose E3b und G4 mit Pilotreserve – Entscheidungsvorlage (17.10.2026)

Synthetische Entwicklungsdiagnostik zu AP-08, AP-09 und AP-13 (Auftrag „E3b und G4 – Diagnose und
Entscheidungsvorlage“ vom 17.10.2026). Grundlage ist der Stand `main` 0a8eb1b. Gegenstand sind drei Punkte:

- warum E3 bei exakter Superposition überwiegend „unbestimmt“ bleibt und welche Regelfassung zur Messfrage passt;
- warum die aus den Piloten abgeleitete G4-Schwelle und Ausfallreserve an einzelnen Konfigurationen nicht ausreichen;
- die Begründung der Pilotsuche.

Fachliche Änderungen stehen nur als Vorschläge in Abschnitt 5. Präregistrierung, Regelprofile, H1/H2/H3, Schwellen,
Bonferroni-Regel und produktive Ausschlussentscheidungen sind unverändert. Die G4-Varianten rechnet nur das
Diagnoseskript.

**Ergebnis in Kürze.**

- **E3b.** „Unbestimmt“ ist bei exakter Superposition eine Folge des Betrags:
  - Der Betrag eines verrauschten komplexen Nullresiduums ist im Mittel 1,25-mal so groß wie die Streuung je Komponente.
  - Für P(unauffällig) ≥ 0,8 muss diese Streuung unter q_tol/3,28 liegen. Auf L1 ist sie 2,2-mal so groß.
  - Das Modell sagt P(unauffällig) = 0,07 voraus, beobachtet sind 14/200.
  - Empfohlen: feste Schwellen mit Rückfall je Prüfgröße, „auffällig“ bleibt dabei erhalten, und eine feste Prüfzahl
    m = 43. Damit bliebe E3a dreiwertig, E3b würde auf L1 einseitig ausgewertet.
- **G4, Schwelle.** σ_Δ,F aus den Piloten unterschätzt die Fünftel-Streuung an steilen Flanken um bis zu den
  Faktor 2. Ursache ist der Jitter der Indexphasen mal der Flankensteigung.
  - Nach A7 zulässige Piloten erreichen diese Steilheit nicht.
  - Eine vorab aus Phase 0 bestimmte, konfigurationsabhängige Standardisierung senkt die G4-Rate von 2,8–4,5 % auf
    0,9–1,5 % (Orakel 0,8–1,2 %), ohne Empfindlichkeit an flachen Punkten zu verlieren.
- **G4, Reserve.** „Erwartete Ausfälle plus zwei“ reicht nur mit den Wiederholungen nach A9.12.
  - Ohne Wiederholungen ist bei n_min + r(p̂) nur ein Teil der Kampagnen vollständig, mit Wiederholungen alle 120.
  - Der Generator bildet die Wiederholungen nicht ab; die historischen Verluste „Datenlage“ überschätzen daher die
    Lage für das registrierte Protokoll.
  - Planungs- und Kalibriersimulation sollten die Wiederholungen enthalten und die gemeinsame Vollständigkeit direkt
    zählen.
- **Nebenbefund.** Bei A4 bildet die Pilotanalyse σ_Δ,F mit k = 30 statt mit k_max = 9 (technische Korrektur, 3.7).

**Aufruf** (vom Repository-Stamm):

```bash
python3 code/pcmms_auswertung harness diagnose-e3b-g4 --vorbereiten <vollständige Ausgabe des Altlaufs ohne Endung>   # einmalig, erledigt
python3 code/pcmms_auswertung harness diagnose-e3b-g4 --startsatz --prozesse 4                                         # Laufzeitmessung
python3 code/pcmms_auswertung harness diagnose-e3b-g4 --prozesse 4                                                     # alle 120 Kampagnen
python3 code/pcmms_auswertung harness diagnose-e3b-g4 --bericht                                                        # Auswertung, Tabellen
```

Rechnungen laufen nur aus einem sauberen Git-Stand und nur mit passenden Checkpoints.

- Checkpoints liegen unter `/tmp/pcmms-diagnose-e3b-g4-20261017/`, nicht im Repository.
- Der Schlüssel umfasst Rechencode ohne Berichtsteil, Auftrag, Profil, Werkzeug 8, Seeds und Bibliotheken.
- Berichtskorrekturen (`harness/diagnose_e3b_g4_bericht.py`) wiederholen keine Rechnung.
- Der E3-Teil braucht keine temporären Ausgaben: Er liest den versionierten Auszug `e3_pruefgroessen.csv`.

## 1 Ausgangsstand und Arbeitsweise

- `main` = 0a8eb1b (PR #21 gemergt; Baum gleich dem PR-Kopf ea02eed). Gearbeitet im Worktree
  `diagnose-e3b-g4-2026-10`. Gerechnet auf 778e1b2 aus sauberem Stand, nachdem Treiber, Auftragsliste und Seeds
  committet waren (c320d62, 778e1b2).
- **Gespeicherte Befunde:**
  - E3-Prüfgrößen der 570 Neulaufkampagnen in voller Genauigkeit aus den Checkpoints von PR #21. Herkunft je Punkt geprüft
    (Auftrags-Hash, Seeds, Rechenstand 020e131), abgeglichen mit `kampagnen_e3.csv` (Bewertung, Seed, q_Z, u auf 6
    Stellen).
  - Historische Referenzwerte aus `docs/ap11_ap12_ap13_pruefstand.json` (unverändert) und Befund 1 des
    Softwaredokuments.
  - Der K12-Ablauf aus `docs/ap13_neulaeufe_2026-10-17/altstand_auszug.json`.
- **Neue Rechnungen:** 120 G4-Kampagnen (Abschnitt 3.1). Punktweise G4-Größen (D_N, D_F, gültige Läufe je Punkt)
  waren in keinem vorhandenen Ergebnis gespeichert; vorhanden sind nur Anteile je Regel und Kampagne.
- **Hypothetische Varianten:** nur im Berichtsteil, auf denselben simulierten Läufen.
- Werkzeug 8: A4 und V1-G0 aus PR #21 unverändert; V1-G60h unverändert aus der vollständigen Ausgabe des Altlaufs
  übernommen (`werkzeug8_V1G60h`, Herkunft und Prüfsummen im Kopf). Keine Kalibrierkampagnen.

## 2 E3b

### 2.1 Nachzählung der 570 Kampagnen

Alle Kampagnen stehen im Nenner. „a/u/b“ zählt auffällig/unauffällig/unbestimmt, nachgezählt aus dem Auszug nach A9.13
mit 0,1° und q_tol = 5,8·10⁻⁴. Die nachgezählte Gesamtbewertung gleicht in allen 570 Kampagnen der gespeicherten.

<!-- tabelle:e3_punkte -->
| Punkt | n | auffällig | unauffällig | unbestimmt | E3a a/u/b | E3b a/u/b | „unauffällig“ nur an E3b verfehlt | u(q_Z) > q_tol/1,645 | auffällig E3a / E3b bei H1Z bestätigt | Prüfzahl m (Kampagnen) |
|---|---|---|---|---|---|---|---|---|---|---|
| N01-A4/L1 | 200 | 0 | 14 | 186 | 0/200/0 | 0/14/186 | 186 | 27 | 0 / 0 | 37: 2, 41: 5, 43: 193 |
| A06-phase/L1 | 30 | 30 | 0 | 0 | 30/0/0 | 3/0/27 | 0 | 17 | 23 / 0 | 37: 1, 41: 6, 43: 23 |
| H03-phase/L1 | 30 | 30 | 0 | 0 | 30/0/0 | 30/0/0 | 0 | 22 | 24 / 24 | 39: 1, 41: 5, 43: 24 |
| E04-kette/L1 | 30 | 30 | 0 | 0 | 30/0/0 | 0/4/26 | 0 | 3 | 22 / 0 | 39: 1, 41: 7, 43: 22 |
| E07-verstaerkung/L1 | 40 | 0 | 6 | 34 | 0/40/0 | 0/6/34 | 34 | 9 | 0 / 0 | 41: 3, 43: 37 |
| E07-basisdrift/L1 | 40 | 36 | 0 | 4 | 0/39/1 | 36/0/4 | 4 | 40 | 0 / 35 | 41: 1, 43: 39 |
| N03-ungleich/L1 | 40 | 0 | 3 | 37 | 0/40/0 | 0/3/37 | 37 | 6 | 0 / 0 | 35: 1, 41: 5, 43: 34 |
| N03-N3bindet/L1 | 40 | 0 | 40 | 0 | 0/40/0 | 0/40/0 | 0 | 0 | 0 / 0 | 43: 40 |
| N01-A4/L0 | 40 | 0 | 40 | 0 | 0/40/0 | 0/40/0 | 0 | 0 | 0 / 0 | 41: 3, 43: 37 |
| N01-A4/L2 | 40 | 0 | 0 | 40 | 0/2/38 | 0/0/40 | 2 | 40 | 0 / 0 | 41: 2, 43: 38 |
| N01-A4/L4 | 40 | 3 | 0 | 37 | 1/0/39 | 2/0/38 | 0 | 40 | 0 / 0 | 43: 40 |
<!-- /tabelle -->

- E3a ist bei exakter Superposition auf L1 in 200/200 Kampagnen „unauffällig“.
  - Die größte obere Grenze |Δφ| + 1,645·u je Kampagne liegt bei 0,029°–0,054° (Median 0,038°), weit unter 0,1°.
  - E3a erkennt A06, H03 und E04 in 30/30 Kampagnen, an der Mehrzahl davon bei bestätigtem H1Z.
- Auf L1 entsteht „unbestimmt“ allein an E3b.
- E3b ist „auffällig“ an H03 (30/30) und E07-basisdrift (36/40), in 24 bzw. 35 Fällen bei bestätigtem H1Z.
  - E3b ist von H1Z nicht unabhängig (§8.10), trägt aber an diesen Artefakten Nachweisinformation über die
    Äquivalenzaussage von H1Z hinaus.
- Die Prüfzahl m hängt von der Datenlage ab: Kampagnen mit nicht auswertbaren Punkten haben m = 35–41 statt 43.

### 2.2 N01-A4/L1: Präzisionsgrenze und Punktschätzer

<!-- tabelle:e3b_verteilung -->
| Größe [10⁻⁴] | Min | 10 % | 25 % | Median | 75 % | 90 % | Max |
|---|---|---|---|---|---|---|---|
| q_Z | 0,65 | 2,01 | 3,06 | 4,47 | 6,36 | 8,34 | 12,12 |
| u(q_Z) | 2,05 | 2,52 | 2,75 | 2,96 | 3,30 | 3,60 | 4,21 |
| q_Z + 1,645·u(q_Z) | 4,13 | 6,12 | 7,57 | 9,40 | 11,76 | 14,13 | 18,64 |
<!-- /tabelle -->

<!-- tabelle:e3b_zerlegung -->
| Kampagnen N01-A4/L1 | Anzahl |
|---|---|
| u(q_Z) > q_tol/1,645 = 3,526·10⁻⁴: „unauffällig“ schon wegen q_Z ≥ 0 ausgeschlossen | 27 |
| u(q_Z) unter dieser Grenze, aber q_Z > q_tol − 1,645·u(q_Z) | 159 |
| „unauffällig“ (q_Z + 1,645·u(q_Z) ≤ q_tol) | 14 |
| zusammen | 200 |
<!-- /tabelle -->

- Oberhalb von u(q_Z) = q_tol/1,645 ist „unauffällig“ schon wegen q_Z ≥ 0 ausgeschlossen. Das ist die reine
  Unsicherheitsgrenze; unabhängig nachgezählt sind es wie aus der gerundeten CSV 27/200.
- Die übrigen 159 Fehlschläge gehen auf den positiven Punktschätzer zurück: Der Median von q_Z liegt mit 4,5·10⁻⁴
  schon nahe q_tol.
- „Auffällig“ ist bei exakter Superposition nie erreicht: Die größte untere Grenze q_Z − z_B·u ist 0,20·q_tol.

### 2.3 Betrag eines verrauschten komplexen Residuums

**Herleitung.** Bei exakter Superposition ist die wahre Differenz R₋₁ − R̂₋₁ null. Geschätzt wird ein komplexer Wert mit
zwei etwa normalverteilten, unabhängigen Komponenten der Streuung s; q_Z ist sein Betrag (bezogen auf |R̂₊₁|).
- Der Betrag ist Rayleigh-verteilt: Mittel s·√(π/2) ≈ 1,25 s, Median 1,18 s, Streuung 0,66 s, P(|R| ≤ x) = 1 − e^{−x²/(2s²)}.
- Der Punktschätzer ist also auch bei wahrer Differenz null typischerweise positiv.
- Die Bootstrap-Streuung u ist die Streuung des Betrags der Replikate um R̂ (Rice-Verteilung). Sie liegt bei etwa
  0,81 s, also unter s.
- „Unauffällig“ verlangt q_Z + 1,645·u ≤ q_tol, typisch also 1,25 s + 1,33 s ≈ 2,6 s ≤ q_tol.

**Kleine unabhängige Simulation.**
- 20 000 Nullresiduen R = Z₁ + iZ₂ mit je 1000 Replikaten R + Z′₁ + iZ′₂, Seed 20261017, z_B = 3,045 (m = 43).
- Beide Größen skalieren mit s; maßgeblich ist nur q_tol/s.

<!-- tabelle:nullresiduum -->
| q_tol/s | P(unauffällig) | P(auffällig) |
|---|---|---|
| 0,00 | 0,000 | 0,0126 |
| 0,25 | 0,000 | 0,0052 |
| 0,50 | 0,000 | 0,0022 |
| 1,00 | 0,000 | 0,0004 |
| 1,50 | 0,069 | 0,0000 |
| 2,00 | 0,260 | 0,0000 |
| 2,50 | 0,491 | 0,0000 |
| 3,00 | 0,703 | 0,0000 |
| 3,50 | 0,859 | 0,0000 |
| 4,00 | 0,949 | 0,0000 |
| 5,00 | 0,997 | 0,0000 |
<!-- /tabelle -->

- P(unauffällig) ≥ 0,8 verlangt q_tol/s ≥ 3,28, also s ≤ 1,77·10⁻⁴. Aus q_Z der 200 Kampagnen folgt s = 3,86·10⁻⁴
  (Rayleigh-Schätzer, q_tol/s = 1,50).
- Das Modell sagt dafür P(unauffällig) = 0,07 voraus, beobachtet sind 14/200 = 0,07. Ebenso: Median u vorhergesagt
  3,12·10⁻⁴, beobachtet 2,96·10⁻⁴; q_Z/u im Median 1,47 gegen 1,48.
- Die Streuung müsste also um den Faktor 2,2 sinken. Wie sich das auf Messung, Vorhersage und Kalibrierung verteilt
  und welche Laufzahl daraus folgt, lässt sich ohne getrenntes Modell nicht angeben; hier wird es nicht umgerechnet.
- „Auffällig“ ist bei q_tol/s ≥ 1,5 praktisch ausgeschlossen. Bei sehr geringer Präzision (q_tol/s → 0) erreicht es
  1,3 % je Kampagne statt 0,05/43 = 0,12 % für diese eine Prüfung. Daher gilt auch die untere Grenze eines Betrags nur
  bei ausreichender Präzision als kalibriert (vgl. N01-A4/L4: E3b auffällig 2/40).
- Das ist eine Verfahrensdiagnose. Sie ersetzt die Kampagnensimulation nicht und legt keine neue Intervallregel fest.

### 2.4 Zelllagen und T in E3b

- E3b enthält T nicht. Die Zelllagen werden je Replikat gemeinsam für Messung und Vorhersage gezogen (Korrektur E).
- Laut Modell ändert das u(q_Z) um höchstens 3,5·10⁻⁶ relativ (N01-A4/L1); über alle elf Punkte sind es höchstens
  9,7·10⁻⁵.
- Grund: Ein Lagefehler wirkt auf R₋₁ und R̂₋₁ gleich und multipliziert in der Differenz nur das kleine Residuum. Im
  Nenner |R̂₊₁| ändert er den Wert relativ um etwa δx/r.
- Das zeigt nur, dass das Modell (genaue synthetische Kalibrierung, Zelllagen ≤ 0,1 mm) die Kalibrierunsicherheit klein
  hält. Für reale Kalibrierfehler ist es kein Nachweis der Vernachlässigbarkeit, etwa für lastabhängige
  Zellverstärkungen, Kippmoden oder Modullagen, die das T-Modell nicht enthält.

### 2.5 Nachträgliche Sensitivität von q_tol (nur beschreibend)

Auf denselben 200 Kampagnen, ohne neue Rechnung. Die Tabelle legt keine Schwelle fest. Eine Anhebung von q_tol allein,
damit die Rate 0,8 erreicht, widerspräche der Bedeutung von q_tol als Wirkung von 0,1° an einem Modul (A2.7).

<!-- tabelle:qtol_sensitivitaet -->
| q_tol (nachträglich, nur beschreibend) | „unauffällig“ an E3b | „auffällig“ an E3b |
|---|---|---|
| 1,00 × 5,8·10⁻⁴ | 14/200 | 0/200 |
| 1,25 × 5,8·10⁻⁴ | 41/200 | 0/200 |
| 1,50 × 5,8·10⁻⁴ | 79/200 | 0/200 |
| 2,00 × 5,8·10⁻⁴ | 147/200 | 0/200 |
| 2,50 × 5,8·10⁻⁴ | 183/200 | 0/200 |
| 3,00 × 5,8·10⁻⁴ | 197/200 | 0/200 |
<!-- /tabelle -->

### 2.6 Entscheidungsvorlage E3

| Option (§12) | Welche Präzision verlangt sie, was bleibt? | Einordnung |
|---|---|---|
| (a) feste Schwellen 0,1° und q_tol mit Rückfall | E3a erreicht beide Kriterien auf L1 (unauffällig 200/200, auffällig 0/200). E3b braucht s ≤ q_tol/3,28 (L1: Faktor 2,2 darüber). Ein Rückfall für E3 als Ganzes nähme auf L1 auch E3a und die Nachweise von E3b weg; ein Rückfall je Prüfgröße nicht. | bevorzugt, mit Rückfall je Prüfgröße |
| (b) Schwellen als Vielfaches der erwarteten Unsicherheit | Bei jeder Präzision entscheidbar. Die Schwelle wächst mit dem Rauschen. Auf L2 und L4 läge κ·u über der Wirkung von 0,1° bzw. q_tol, und „unauffällig“ hieße dann nur „nicht größer als das Rauschen“. Der Bezug zur Profilphase (P0.5, A2.7) ginge verloren. | nicht empfohlen |
| (c) E3 nur beschreibend | Werte mit Unsicherheit bleiben. Die dreiwertige Aussage entfällt auch dort, wo sie funktioniert: E3a an A06/H03/E04 und E3b an H03/E07, meist bei bestätigtem H1Z. | nur als Rückfall |

- **Auffällig erkennen und unauffällig bestätigen** sind getrennte Fragen.
  - „Auffällig“ hält auf L1 das Kriterium P ≤ 0,05 ein, für E3a wie für E3b (je 0/200).
  - „Unauffällig“ verfehlt nur E3b.
  - Verfehlt eine Prüfgröße nur die Bestätigung, kann sie einseitig ausgewertet werden: „auffällig“ oder „keine
    Überschreitung nachgewiesen“. Das bewahrt die Nachweise von E3b.
  - Ein Rückfall auf beschreibend oder einseitig ist kein bestandener Test. E3 insgesamt ist dann nie „unauffällig“.
- **H1Z.** E3b fasst die H1Z-Residuen von N_c,1 am Triphasik-Punkt zusammen. Die konfirmatorische Aussage zu diesen
  Residuen bleibt bei H1Z. Der Verlust der Bestätigung von E3b kostet daher wenig, der Verlust seiner Nachweise mehr
  (2.1).
- **Prüfmenge und Bonferroni.** Die Prüfmenge sind die auswertbaren Schnittkonfigurationen und der Triphasik-Punkt,
  ohne Zusatz- und Identifizierbarkeitskonfigurationen. Eine feste Prüfzahl m = 2·N_K + 1 = 43 entkoppelt z_B von
  der Datenlage (heute m = 35–43); sie ist bei fehlenden Punkten etwas konservativ.
- E3b bleibt eine Differenz gegen die Vorhersage. Eine absolute Fassung würde zulässige konstante Modulunterschiede und
  Zelllagefehler bewerten (§8.10). Eine relative E3a-Fassung ist für die Entscheidung nicht nötig, weil E3a absolut
  auf L1 beide Kriterien erreicht.

**Bevorzugt:** Option (a) mit Rückfall je Prüfgröße und einseitiger Auswertung bei verfehlter Bestätigung, feste
Prüfzahl. Wortlaut in Abschnitt 5.

## 3 G4 und Pilotreserve

### 3.1 Daten und Läufe

- **Kampagnen:** 120 neue Kampagnen auf Ebene H, Stufe L1, je 40 für N01-A4, N01-V1G0 und N01-V1G60h.
  - Seeds vorab festgelegt: `zufall.unterseed(20261017, 'diagnose_g4', System, 'L1', i)`, i = 0 … 39 (eigene Rolle,
    keine Überschneidung mit früheren Seeds).
  - Plan wie Prüfstand: n₀ = 20, n_pilot = 20, n = 24 Blöcke (feste historische Wahl), n_min = 18.
  - Harmonische: k_max des Systems (A4: 9, V1: 12).
- **Profil:** ENTW-2026-10 mit der Reduktion des Prüfstands (bootstrap_B = 1000, h3_mc = 1000,
  eps_ctrl_datensaetze = 1000; H2 und E3 folgen B; Hash 49dc74ab…). G4-Faktor fest 3, unverändert.
- **Je Kampagne:** Generator, Kalibrierung, Pilotanalyse, Teil B und Gültigkeitsprüfung der Phase 1 wie die Kette,
  ohne Bootstrap. Volle Ketten nur für die vorab bestimmten Kampagnen 0–3 je System (12); dort ist die schlanke
  Gültigkeitsprüfung gleich der vollen.
- **Nur für die Diagnose,** aus eigenen Zufallsströmen derselben Kampagne:
  - 20 Läufe eines gezielten Phase-0-Piloten (130°, 262°). Das ist die steilste Konfiguration in φ₂ 90°–150°,
    φ₃ 200°–280°, deren zyklische Abstände (130°/132°/98°) wie die registrierten Piloten mindestens 10° von 120°
    entfernt sind (A7). Gewählt wurde nach der vorhergesagten Jitterstreuung am rauschfreien Modell vor Phase 0.
  - Ein Vorrat von zwei Wiederholungsläufen je Konfigurationsplatz, am Platz des ursprünglichen Laufs (A9.12, G1-Sonderablauf
    nicht nachgebildet).
- **Laufzeit:** 120 Kampagnen in 2 min Wandzeit mit 4 Prozessen zu je einem BLAS-Thread. Der Startsatz ergab
  10 Kernsekunden je voller und 3 je schlanker Kampagne; der Umfang wurde deshalb nicht reduziert.

<!-- tabelle:laufzeiten -->
| Auftrag | Kampagnen | Wandzeit [s] | Kernsekunden |
|---|---|---|---|
| G4-N01-A4-start | 4 | 9,0 | 29,4 |
| G4-N01-A4-rest | 36 | 31,7 | 117,9 |
| G4-N01-V1G0-start | 4 | 13,3 | 48,1 |
| G4-N01-V1G0-rest | 36 | 28,5 | 108,4 |
| G4-N01-V1G60h-start | 4 | 12,4 | 43,6 |
| G4-N01-V1G60h-rest | 36 | 27,5 | 103,1 |
| zusammen | 120 | 122,4 | 450,5 (0,125 Kernstunden) |
<!-- /tabelle -->

### 3.2 Befunde je Konfiguration (produktive Regel)

Raten je Lauf als Mittel über Kampagnen ± Standardfehler mit Kampagnen als Einheiten. Kampagnenanteile mit
95-%-Wilson-Intervall. Läufe derselben Kampagne zählen nicht als unabhängige Kampagnen.

<!-- tabelle:g4_uebersicht -->
| | N01-A4 | N01-V1G0 | N01-V1G60h |
|---|---|---|---|
| k der Prüfgröße (k_max) / k der Pilotgrößen | 9 / 30 | 12 / 12 | 12 / 12 |
| p̂ der Piloten: Mittel, Max, Kampagnen mit p̂ = 0 | 0,020, 0,083, 16/40 | 0,011, 0,067, 20/40 | 0,010, 0,050, 22/40 |
| n = n_min + r(p̂) mit „+2“ (Kampagnen) | 20: 16, 21: 19, 22: 5 | 20: 20, 21: 19, 22: 1 | 20: 22, 21: 18 |
| σ_Δ,N [mN] | 0,236 | 0,253 | 0,251 |
| σ_Δ,F produktiv / bei k_max [mN] | 1,95 / 1,73 | 1,95 / 1,95 | 1,93 / 1,93 |
| ungültig durch D_N (G4) je Lauf | 0,87 % | 0,53 % | 0,51 % |
| ungültig durch D_F (G4) je Lauf | 1,98 % | 3,80 % | 3,99 % |
| G4 insgesamt ± SE (Kampagnen) | 2,84 % ± 0,33 % | 4,31 % ± 0,32 % | 4,47 % ± 0,44 % |
| nur G4 | 2,82 % | 4,30 % | 4,45 % |
| andere Regeln (G1 …) | 0,66 % | 0,51 % | 0,51 % |
| ungültig insgesamt je Lauf: Mittel; ungünstigster Punkt | 3,48 %; 7,4 % | 4,80 %; 14,5 % | 4,96 %; 15,2 % |
| ungünstigster Punkt (G4) | S118: 7,0 % | S118: 14,1 % | S118: 14,7 % |
| Kampagnen mit einem Punkt < n_min (n = 24, ohne Wiederholung) | 0/40 [0,00; 0,09] | 4/40 [0,04; 0,23] | 9/40 [0,12; 0,38] |
| Binomialnäherung P(vollständig), n = 24: mit p̂ / mit punktweisen Raten | 0,996 / 0,996 | 1,000 / 0,910 | 1,000 / 0,906 |
| kleinster Bestand je Kampagne (Anzahl Kampagnen) | 18: 4, 19: 1, 20: 13, 21: 10, 22: 9, 23: 3 | 16: 2, 17: 2, 18: 7, 19: 7, 20: 13, 21: 6, 22: 2, 23: 1 | 16: 3, 17: 6, 18: 5, 19: 4, 20: 11, 21: 5, 22: 6 |
| historisch (Prüfstand 16.10.2026): G4-Anteil aller Läufe der Phase 1; H1 „Datenlage“; H1 und H2 bestätigt | 2,3 %; 7/200; 193/200 | 4,4 %; 11/60; 49/60 | 5,0 %; 15/60; 45/60 |
<!-- /tabelle -->

- G4 verletzt fast nur über D_F; D_N trägt 0,5–0,9 %.
- Die Pilot-Ausfallrate p̂ (1–2 %) unterschätzt die mittlere Ausfallrate der Kombinationsläufe (3,5–5,0 %) und vor
  allem die der ungünstigsten Punkte (S114–S118: bis 7,4 % bei A4, 14,5 % bei V1-G0, 15,2 % bei V1-G60h).
- Die direkt gezählte Vollständigkeit liegt unter der Binomialnäherung mit punktweisen Raten (V1-G60h: 31/40 gegen
  0,91). Grund: σ̂_Δ wird je Kampagne aus 60 Pilotläufen geschätzt (Variationskoeffizient 14–16 %), und eine kleine
  Schätzung trifft alle Punkte derselben Kampagne zugleich.

**Zusammenhang mit Phasenlage und Flanke.** Die vorhergesagte Jitterstreuung ist √(2·Var F(φ + e)) für Phasenstörungen
e in der Größe der Fünftelmittel (σⱼ/√n_f = 0,2°/√20). Sie folgt dem Zelt:
- Sie steigt bis S118 und fällt am Knick S120, wo zwei Minima gleich tief sind.
- Die beobachtete Streuung MAD(D_F) und die G4-Rate folgen ihr.
- Die Piloten liegen mit 1,2–1,7 mN Jitterstreuung bei 40–55 % des steilsten Punkts (3,1 bzw. 3,9 mN).

<!-- tabelle:g4_punkte -->
| Punkt | φ₂ | Jitterstreuung Modell A4 / V1 [mN] | MAD(D_F) A4 / V1-G0 / V1-G60h [mN] | G4 produktiv A4 / V1-G0 / V1-G60h | davon D_N A4 / V1-G0 / V1-G60h |
|---|---|---|---|---|---|
| S100 | 100° | 1,68 / 1,57 | 2,02 / 1,87 / 1,99 | 1,4 % / 0,8 % / 0,8 % | 0,9 % / 0,6 % / 0,3 % |
| S102 | 102° | 1,81 / 1,75 | 2,15 / 2,23 / 2,26 | 2,2 % / 2,0 % / 1,4 % | 0,8 % / 0,7 % / 0,3 % |
| S104 | 104° | 1,95 / 1,96 | 2,04 / 2,20 / 2,14 | 2,7 % / 2,0 % / 2,3 % | 0,8 % / 0,4 % / 0,3 % |
| S106 | 106° | 2,10 / 2,19 | 2,51 / 2,47 / 2,37 | 2,8 % / 3,5 % / 3,2 % | 1,0 % / 0,9 % / 0,8 % |
| S108 | 108° | 2,26 / 2,45 | 2,52 / 2,66 / 2,62 | 3,6 % / 4,2 % / 3,8 % | 1,1 % / 0,2 % / 0,1 % |
| S110 | 110° | 2,42 / 2,72 | 2,55 / 2,88 / 2,96 | 4,6 % / 6,1 % / 7,4 % | 0,9 % / 0,4 % / 0,9 % |
| S112 | 112° | 2,59 / 3,00 | 2,71 / 3,05 / 3,18 | 4,4 % / 8,1 % / 7,9 % | 0,8 % / 0,4 % / 0,7 % |
| S114 | 114° | 2,75 / 3,29 | 2,96 / 3,46 / 3,42 | 6,8 % / 9,5 % / 10,4 % | 1,2 % / 0,5 % / 0,2 % |
| S116 | 116° | 2,92 / 3,58 | 3,06 / 3,80 / 3,38 | 6,5 % / 12,4 % / 11,5 % | 1,1 % / 0,6 % / 0,8 % |
| S118 | 118° | 3,08 / 3,87 | 3,07 / 4,03 / 3,84 | 7,0 % / 14,1 % / 14,7 % | 1,0 % / 0,5 % / 0,5 % |
| S120 | 120° | 1,65 / 2,11 | 2,29 / 2,88 / 2,87 | 2,8 % / 6,5 % / 6,5 % | 0,7 % / 0,7 % / 0,8 % |
| S122 | 122° | 2,15 / 2,70 | 2,40 / 3,05 / 2,83 | 2,3 % / 4,8 % / 5,9 % | 0,3 % / 0,2 % / 0,5 % |
| S124 | 124° | 2,03 / 2,48 | 2,38 / 2,69 / 2,72 | 2,1 % / 4,8 % / 5,2 % | 0,6 % / 0,7 % / 0,7 % |
| S126 | 126° | 1,90 / 2,26 | 2,10 / 2,55 / 2,49 | 1,9 % / 3,8 % / 3,9 % | 1,1 % / 0,7 % / 0,3 % |
| S128 | 128° | 1,78 / 2,06 | 2,09 / 2,46 / 2,43 | 2,2 % / 2,2 % / 2,7 % | 1,2 % / 0,2 % / 0,3 % |
| S130 | 130° | 1,65 / 1,86 | 2,00 / 2,22 / 2,15 | 1,5 % / 1,2 % / 1,9 % | 0,7 % / 0,5 % / 0,5 % |
| S132 | 132° | 1,53 / 1,65 | 1,96 / 2,22 / 2,04 | 1,4 % / 0,8 % / 1,2 % | 0,6 % / 0,2 % / 0,2 % |
| S134 | 134° | 1,41 / 1,46 | 1,66 / 1,86 / 1,91 | 1,2 % / 1,2 % / 1,1 % | 0,9 % / 0,4 % / 0,6 % |
| S136 | 136° | 1,30 / 1,29 | 1,72 / 1,69 / 1,70 | 0,9 % / 0,8 % / 0,4 % | 0,8 % / 0,4 % / 0,2 % |
| S138 | 138° | 1,19 / 1,14 | 1,53 / 1,69 / 1,59 | 0,5 % / 0,9 % / 0,7 % | 0,5 % / 0,8 % / 0,4 % |
| S140 | 140° | 1,10 / 1,02 | 1,53 / 1,53 / 1,71 | 0,9 % / 0,6 % / 1,0 % | 0,6 % / 0,6 % / 0,9 % |
| Piloten (110°, 250°), (130°, 230°), (110°, 252°) | | 1,68, 1,23, 1,55 / 1,57, 1,39, 1,41 | 1,79, 1,71, 1,79 / 1,99, 2,06, 1,83 / 1,95, 2,07, 1,90 | | |
| Zielpilot (130°, 262°) | | 2,28 / 2,47 | 2,38 / 2,69 / 2,62 | | |
<!-- /tabelle -->

### 3.3 Ursache 1: Schwellenübertragung

| Variante | σ_Δ,F | verfügbar? |
|---|---|---|
| v0 produktiv | 1,4826·MAD der 60 Pilotläufe, gepoolt, bei k der Pilotgrößen (A4: 30) | ja (heutiger Stand) |
| v0k k-konsistent | dieselben Läufe bei k_max (Prüfgröße der Phase 1) | ja; bei V1 gleich v0 |
| v1 gezielter Pilot | 1,4826·MAD der 20 Läufe von (130°, 262°), für alle Punkte | ja |
| v2 Standardisierung aus Phase 0 | σ²_F,i = σ²_P + max(0, s²_i − s̄²_P): σ_P wie v0k, s_i die aus Phase 0 vorhergesagte Jitterstreuung von D_F am Punkt i, s̄²_P ihr Mittel über die drei Piloten | ja (vor Phase 1 festgelegt) |
| v3 Orakel | 1,4826·MAD von D_F je Punkt über alle 40 Kampagnen | nein, nur Illustration |

σ_Δ,N, Faktor 3 und Rundungsboden bleiben in allen Varianten produktiv. Die übrigen Regeln, auch G1, hängen nicht
von G4 der Kombinationsläufe ab. ε_ctrl und p̂ bleiben produktiv.

- **v2 aus Phase-0-Größen:** Die Vorhersage ŷ⁰ stammt aus den gültigen Einzelmodulläufen P0.8 und Δδⱼ (P0.5), der
  Jitter σⱼ aus den Piloten, n_f aus dem Plan. Für die Vorhersage dienen 512 feste antithetische Ziehungen.
- **Prüfung an den Piloten:** Vorhergesagt sind 1,9/1,5/1,8 mN (A4) und 2,0/1,9/1,9 mN (V1-G0), beobachtet
  1,8/1,7/1,8 bzw. 2,0/2,1/1,8 mN (ergebnisse.json, g4.systeme.*.piloten).

<!-- tabelle:g4_varianten -->
| System | Variante | G4 je Lauf | ungünstigster Punkt | Kampagnen mit Punkt < n_min (n = 24) ohne / mit Wiederholung | vollständig bei n_min + r(p̂) ohne / mit Wiederholung | Wiederholungsläufe je Kampagne |
|---|---|---|---|---|---|---|
| N01-A4 | v0 produktiv | 2,84 % | S118: 7,0 % | 0/40 / 0/40 | 28/40 / 40/40 | 18,8 |
| N01-A4 | v0k k-konsistent | 4,30 % | S118: 10,8 % | 2/40 / 0/40 | 17/40 / 40/40 | 27,0 |
| N01-A4 | v1 gezielter Pilot | 2,42 % | S116: 5,6 % | 2/40 / 0/40 | 29/40 / 40/40 | 17,0 |
| N01-A4 | v2 Standardisierung aus Phase 0 | 1,47 % | S120: 3,1 % | 0/40 / 0/40 | 37/40 / 40/40 | 11,2 |
| N01-A4 | v3 Orakel (Illustration) | 1,21 % | S104: 2,0 % | 0/40 / 0/40 | 39/40 / 40/40 | 9,8 |
| N01-V1G0 | v0 produktiv | 4,31 % | S118: 14,1 % | 4/40 / 0/40 | 6/40 / 40/40 | 26,4 |
| N01-V1G0 | v0k k-konsistent | 4,31 % | S118: 14,1 % | 4/40 / 0/40 | 6/40 / 40/40 | 26,4 |
| N01-V1G0 | v1 gezielter Pilot | 2,45 % | S118: 8,5 % | 4/40 / 0/40 | 27/40 / 40/40 | 16,4 |
| N01-V1G0 | v2 Standardisierung aus Phase 0 | 0,87 % | S120: 2,3 % | 0/40 / 0/40 | 38/40 / 40/40 | 7,2 |
| N01-V1G0 | v3 Orakel (Illustration) | 0,78 % | S136: 1,4 % | 0/40 / 0/40 | 38/40 / 40/40 | 6,7 |
| N01-V1G60h | v0 produktiv | 4,47 % | S118: 14,7 % | 9/40 / 0/40 | 10/40 / 40/40 | 27,2 |
| N01-V1G60h | v0k k-konsistent | 4,47 % | S118: 14,7 % | 9/40 / 0/40 | 10/40 / 40/40 | 27,2 |
| N01-V1G60h | v1 gezielter Pilot | 3,64 % | S118: 10,4 % | 6/40 / 1/40 | 24/40 / 39/40 | 24,2 |
| N01-V1G60h | v2 Standardisierung aus Phase 0 | 0,85 % | S120: 2,3 % | 0/40 / 0/40 | 38/40 / 40/40 | 7,0 |
| N01-V1G60h | v3 Orakel (Illustration) | 0,82 % | S116: 1,5 % | 0/40 / 0/40 | 38/40 / 40/40 | 6,8 |
<!-- /tabelle -->

- **Gezielte Piloten** genügen nicht.
  - Nach A7 zulässige Konfigurationen erreichen in der Umgebung des Schnitts höchstens 2,3 mN (A4) bzw. 2,5 mN (V1)
    vorhergesagte Jitterstreuung, gegen 3,1 bzw. 3,9 mN an S118.
  - Ein Pilot mit 20 Läufen streut zudem stärker als der Pool und hebt die Schwelle auch an flachen Punkten an.
- **Die Standardisierung v2** kommt dem Orakel nahe.
  - Sie senkt die G4-Rate auf 0,85–1,5 % und den ungünstigsten Punkt auf 2,3–3,1 %.
  - Sie nimmt nur den aus Phase 0 vorhergesagten Jitteranteil auf und liegt nie unter σ_P.
  - Eine Anpassung an Daten der Phase 1 findet nicht statt.
- **v0k bei A4:** Mit konsistentem k steigt die produktive G4-Rate von 2,8 % auf 4,3 % (3.7). Die A4-Werte der Altläufe
  fallen durch die Inkonsistenz also zu günstig aus.

### 3.4 Ursache 2: Reserve

**Feste Wahl gegen berechnete Reserve.**
- n = 24 ist die feste Wahl des Entwicklungsplans, nicht das Ergebnis einer Planung; Teil B trägt r = 2 als Platzhalter.
- Aus p̂ der Piloten folgt mit „+2“ n = 20–22.
- Die Zeilen „n_min + r(p̂)“ kürzen die simulierten 24 Blöcke auf die ersten n Blöcke, mit einem Lauf je Konfiguration
  und Block. Das ist eine Auswertung, keine neu ausgeführte Planung.

Vollständigkeit aller 21 Punkte je Kampagne (Anzahl von 40), ohne/mit Wiederholungen nach A9.12:

<!-- tabelle:g4_vollstaendigkeit -->
| System | Variante | n = 18 | n = 19 | n = 20 | n = 21 | n = 22 | n = 23 | n = 24 |
|---|---|---|---|---|---|---|---|---|
| N01-A4 | v0 | 0 / 36 | 4 / 40 | 18 / 40 | 27 / 40 | 36 / 40 | 36 / 40 | 40 / 40 |
| N01-A4 | v2 | 0 / 38 | 15 / 40 | 29 / 40 | 40 / 40 | 40 / 40 | 40 / 40 | 40 / 40 |
| N01-V1G0 | v0 | 0 / 33 | 1 / 40 | 5 / 40 | 11 / 40 | 24 / 40 | 31 / 40 | 36 / 40 |
| N01-V1G0 | v2 | 3 / 39 | 24 / 40 | 37 / 40 | 39 / 40 | 40 / 40 | 40 / 40 | 40 / 40 |
| N01-V1G60h | v0 | 0 / 39 | 0 / 40 | 8 / 40 | 14 / 40 | 23 / 40 | 28 / 40 | 31 / 40 |
| N01-V1G60h | v2 | 5 / 40 | 25 / 40 | 34 / 40 | 39 / 40 | 40 / 40 | 40 / 40 | 40 / 40 |
<!-- /tabelle -->

<!-- tabelle:g4_reserve -->
| System | r mit „+2“ aus p̂ | r gemeinsam (Näherung), p̂ | r gemeinsam, obere 80-%-Grenze von p̂ | r gemeinsam, obere Grenze, mit Wiederholung |
|---|---|---|---|---|
| N01-A4 | 2: 16, 3: 19, 4: 5 | 0: 16, 3: 12, 4: 7, 6: 3, 7: 2 | 3: 16, 5: 12, 6: 7, 8: 3, 9: 2 | 0: 28, 1: 12 |
| N01-V1G0 | 2: 20, 3: 19, 4: 1 | 0: 20, 3: 16, 4: 2, 5: 1, 6: 1 | 3: 20, 5: 16, 6: 2, 7: 1, 8: 1 | 0: 36, 1: 4 |
| N01-V1G60h | 2: 22, 3: 18 | 0: 22, 3: 13, 4: 4, 5: 1 | 3: 22, 5: 13, 6: 4, 7: 1 | 0: 35, 1: 5 |
<!-- /tabelle -->

- **Ohne Wiederholungen** reicht „+2“ nicht:
  - Bei n_min + r(p̂) sind unter produktivem G4 nur 28 (A4), 6 (V1-G0) und 10 (V1-G60h) von 40 Kampagnen vollständig.
  - Selbst n = 24 lässt bei V1 4 bzw. 9 unvollständig.
- **Mit Wiederholungen** sind bei n_min + r(p̂) in allen Varianten außer v1 alle 120 Kampagnen vollständig, schon bei
  n = 19 alle produktiven.
  - A9.12 deckt die punktweisen Ausfälle also weitgehend; die Reserve muss nur den Rest decken.
  - Der Preis sind 19–27 Wiederholungsläufe je Kampagne unter v0 (3–4 % der Phase-1-Läufe, gegen den Zeitfaktor
    1/(1 − p̂) mit p̂ ≈ 1–2 %), unter v2 7–11.
- **Die Binomialnäherung** ist eine gekennzeichnete Näherung mit gleicher Rate p an allen Punkten, unabhängigen Läufen
  und Ziel 0,95.
  - Mit p̂ fordert sie bei p̂ = 0 gar keine Reserve, obwohl bei n = 18 ohne Wiederholung keine Kampagne vollständig ist.
  - Mit der oberen 80-%-Grenze von p̂ wären es r = 3–9.
  - Maßgeblich bleibt deshalb die direkte Zählung je simulierter Kampagne.
- **Folge:** Die Verluste „Datenlage“ der Altläufe überschätzen die Lage für das Protokoll mit Wiederholungen.
  - Die gemeinsamen Bestätigungsraten 0,965/0,82/0,75 sind für dieses Protokoll eher zu niedrig.
  - Aus vollständigeren Daten folgt aber noch keine Bestätigung von H1/H2. Wie hoch die Raten mit Wiederholungen
    liegen, zeigt erst eine Kalibrierung mit Wiederholungen.

### 3.5 Kontrollierter Trendfall

Echter Trend innerhalb eines Laufs an den Kampagnen des Startsatzes (4 je System, 2016 Läufe):
- **Amplitudentrend:** Das letzte Fünftel wird um 1 + ε skaliert. Exakt gilt D_F′ = D_F + ε·(F_min − ⟨N⟩)_letztes, weil
  F_min − ⟨N⟩ homogen in den Harmonischen ist.
- **Nullpunkttrend δ** in D_N.

Angegeben ist der Anteil der von G4 erfassten Läufe an den steilsten Punkten (S114–S118) / an flachen Punkten
(S130–S140).

<!-- tabelle:g4_trend -->
| System | Trend | Stärke | v0 | v0k | v1 | v2 | v3 |
|---|---|---|---|---|---|---|---|
| N01-A4 | amplitude | 0,0 % | 8 % / 2 % | 8 % / 1 % | 1 % / 0 % | 0 % / 1 % | 0 % / 1 % |
| N01-A4 | amplitude | 0,5 % | 41 % / 64 % | 42 % / 66 % | 14 % / 15 % | 5 % / 64 % | 4 % / 59 % |
| N01-A4 | amplitude | 1,0 % | 89 % / 99 % | 89 % / 100 % | 62 % / 98 % | 41 % / 100 % | 38 % / 100 % |
| N01-A4 | nullpunkt | 0,5 mN | 23 % / 19 % | 23 % / 18 % | 16 % / 17 % | 16 % / 18 % | 16 % / 18 % |
| N01-A4 | nullpunkt | 1,0 mN | 77 % / 78 % | 77 % / 78 % | 76 % / 78 % | 76 % / 78 % | 76 % / 78 % |
| N01-V1G0 | amplitude | 0,0 % | 11 % / 1 % | 11 % / 1 % | 11 % / 1 % | 0 % / 1 % | 0 % / 1 % |
| N01-V1G0 | amplitude | 0,5 % | 41 % / 71 % | 41 % / 71 % | 36 % / 56 % | 5 % / 67 % | 5 % / 71 % |
| N01-V1G0 | amplitude | 1,0 % | 91 % / 100 % | 91 % / 100 % | 84 % / 100 % | 41 % / 100 % | 40 % / 100 % |
| N01-V1G0 | nullpunkt | 0,5 mN | 23 % / 12 % | 23 % / 12 % | 22 % / 13 % | 12 % / 12 % | 12 % / 12 % |
| N01-V1G0 | nullpunkt | 1,0 mN | 82 % / 82 % | 82 % / 82 % | 83 % / 82 % | 81 % / 82 % | 81 % / 82 % |
| N01-V1G60h | amplitude | 0,0 % | 13 % / 1 % | 13 % / 1 % | 3 % / 1 % | 1 % / 1 % | 1 % / 1 % |
| N01-V1G60h | amplitude | 0,5 % | 47 % / 67 % | 47 % / 67 % | 16 % / 13 % | 7 % / 62 % | 11 % / 73 % |
| N01-V1G60h | amplitude | 1,0 % | 87 % / 100 % | 87 % / 100 % | 65 % / 97 % | 44 % / 100 % | 51 % / 100 % |
| N01-V1G60h | nullpunkt | 0,5 mN | 27 % / 18 % | 27 % / 18 % | 19 % / 17 % | 17 % / 17 % | 17 % / 18 % |
| N01-V1G60h | nullpunkt | 1,0 mN | 86 % / 85 % | 86 % / 85 % | 85 % / 85 % | 84 % / 85 % | 84 % / 86 % |
<!-- /tabelle -->

- Ohne Trend verwirft v0 an den steilen Punkten 8–13 % der Läufe, v2 0–1 %.
- An flachen Punkten erkennen v2 und v0 einen Amplitudentrend gleich gut, weil v2 dort σ_P verwendet.
- An den steilsten Punkten erkennt v2 einen Trend von 0,5 % (≈ 5 mN) nur in 5–7 % der Läufe.
  - Er liegt dort innerhalb der stationären Jitterstreuung (σ ≈ 4 mN) und ist mit D_F eines Laufs nicht vom Jitter
    trennbar.
  - v0 erfasst ihn häufiger nur, weil es zugleich 8–13 % trendfreie Läufe verwirft.
- Ein Amplitudentrend wirkt an allen Konfigurationen eines Blocks und bleibt an den flachen Punkten sichtbar.
- Nullpunkttrends erkennen alle Varianten gleich, weil σ_Δ,N unverändert ist.
- v2 nimmt also keine Nichtstationarität in eine größere Schwelle auf. Die Schwelle wächst nur um den vorab bekannten
  stationären Jitteranteil.
- Eine Phasendrift eines Moduls ist nicht untersucht; G2 begrenzt die Profilphase mit δφ_tol = 0,5°.

### 3.6 Volle Ketten

<!-- tabelle:g4_volle_ketten -->
| System | Kampagne | H1 | H2 | kleinster Bestand | alle Schnittpunkte auswertbar | Bestand schlank = voll |
|---|---|---|---|---|---|---|
| N01-A4 | 0 | bestätigt | bestätigt | 18 | ja | ja |
| N01-A4 | 1 | bestätigt | bestätigt | 20 | ja | ja |
| N01-A4 | 2 | bestätigt | bestätigt | 20 | ja | ja |
| N01-A4 | 3 | bestätigt | bestätigt | 23 | ja | ja |
| N01-V1G0 | 0 | bestätigt | bestätigt | 19 | ja | ja |
| N01-V1G0 | 1 | bestätigt | bestätigt | 18 | ja | ja |
| N01-V1G0 | 2 | bestätigt | bestätigt | 20 | ja | ja |
| N01-V1G0 | 3 | bestätigt | bestätigt | 19 | ja | ja |
| N01-V1G60h | 0 | bestätigt | bestätigt | 22 | ja | ja |
| N01-V1G60h | 1 | nicht entscheidbar (Datenlage) | nicht entscheidbar (Datenlage) | 17 | nein | ja |
| N01-V1G60h | 2 | bestätigt | bestätigt | 19 | ja | ja |
| N01-V1G60h | 3 | bestätigt | bestätigt | 20 | ja | ja |
<!-- /tabelle -->

- In allen 12 Ketten gleicht der Bestand der schlanken Prüfung dem der Auswertung.
- „Datenlage“ für H1 und H2 tritt genau bei einem Punkt unter n_min auf (N01-V1G60h, Kampagne 1, Bestand 17).

### 3.7 Nebenbefund: k der Pilotgrößen (A4)

- Ohne festgelegten Arbeitspunkt bildet die Pilotanalyse σ_Δ mit k = max(min(k_b, K), 3). Bei A4 ist das k_b = 30,
  weil kein Mode im Band liegt (Befund 6).
- Teil B übernimmt dieses σ_Δ (`pilot_erg['sigma_delta']`), Phase 1 prüft D_F aber mit k_max = 9.
- Auch nach einer erfolgreichen Suche bliebe σ_Δ beim Start-k und nicht beim festgelegten k_max.
- §9.1 bezieht G4 auf F_min − ⟨N⟩ mit k ≤ k_max. σ_Δ,F bei k = 30 ist um 13 % größer (1,95 gegen 1,73 mN), mit
  konsistentem k steigt die G4-Rate bei A4 von 2,8 % auf 4,3 %.
- Das ist eine technische Korrektur ohne Regeländerung. Sie ändert aber Ausschlussmasken und damit c bei A4 und ist
  hier nicht umgesetzt.

### 3.8 Später nötige Kalibrierschritte

Jede Variante, die Ausschlussmasken, Bestände oder Planung ändert (v0k, v2, Wiederholungen), macht c_H1, c_H1Z, den
Rauschbias und die H2-Intervallkalibrierung für sie nicht automatisch gültig. Nötig wären:

1. **Generator und Harness:**
   - Wiederholungen nach A9.12 abbilden (Wiederholungsplatz, Grenze zwei je Konfiguration und Block, G1-Ablauf mit R₂,
     X′, R₃) und die Messzeit mitzählen.
   - σ_Δ,F beim festgelegten k_max übergeben.
   - Bei Übernahme von v2: s_i aus Phase 0 in Teil B und G4 je Konfiguration.
2. **Kalibriersimulation** mit diesen Regeln neu (c_H1, c_H1Z, Rauschbias, Restbias, Überdeckung und Typ des
   H2-Intervalls), dazu P(H1 und H2 bestätigt | exakt) je Referenzsystem.
3. **Planungssimulation** mit Wiederholungen. Sie zählt die gemeinsame Vollständigkeit aller Punkte direkt und die
   G4-Ausschlussrate je Punkt.
4. **Prüfsimulation** der G4-Empfindlichkeit für festgelegte Trendklassen (Amplitude, Nullpunkt, gegebenenfalls Phase)
   als Kriterium in A9.11.

## 4 Begründung der Pilotsuche

`pilot.suche` nennt bei „kein zulässiger Arbeitspunkt“ jetzt die tatsächlich beobachteten Gründe je Paar (k, T_a):
- Grenze der Planungsaufrufe;
- kein simulierter Kandidat erreicht die gemeinsame Bedingung;
- Zeitbudget n_min + r > n_max;
- sonstiger, nicht näher aufgeschlüsselter Grund.

Ist nur eine reduzierte Suche ausgeschöpft, behauptet der Text keine Unzulässigkeit außerhalb dieser Suche. Status,
Suchreihenfolge, Auswahl, Kandidaten, Formeln und Rückgabefelder sind unverändert (`pilot-0.2`). Gegenprüfung am
versionierten K12-Ablauf des Altlaufs:

<!-- tabelle:pilotsuche -->
| | Begründung (Ergebnis unverändert: „kein zulässiger Arbeitspunkt unter diesen Annahmen“) |
|---|---|
| bisher | kein Paar (k, T_a) erfüllt n = n_min + r ≤ n_max |
| neu | an 2 Paaren (k, T_a) erreicht kein simulierter Kandidat P(H1 und H2 bestätigt \| exakt) ≥ 0,8; 26 Paare wegen der Grenze der Planungsaufrufe nicht simuliert – reduzierte Suche ausgeschöpft, kein Nachweis der Unzulässigkeit außerhalb dieser Suche |
| Klassen je Paar (k, T_a) | aufrufgrenze: 26, bedingung: 2 |
<!-- /tabelle -->

Tests:
- die vier Grundklassen, gemischte Fälle und das leere Suchraster;
- ein Ablauf von `pilot_auswerten` mit Aufrufgrenze, der den Text aus den tatsächlichen Rückgaben bildet.

## 5 Entscheidungstabelle

| Zu entscheidender Punkt | Empfehlung | Nachteil / Aufwand | Vorgeschlagener Wortlaut | Spätere Implementierung und Kalibrierung |
|---|---|---|---|---|
| E1 Fassung der E3-Schwellen (§12) | Option (a): feste Schwellen 0,1° und q_tol = 5,8·10⁻⁴ unverändert | E3b ist auf L1 nicht bestätigbar (14/200); die nötige Präzision ist s ≤ q_tol/3,28 | §12, Zeile „Schwellen von E3“: „Festgelegt: (a) mit Rückfall je Prüfgröße (A9.11); (b) und (c) entfallen.“ | keine Codeänderung an den Schwellen; Kriterien je Prüfgröße in Teil B berichten |
| E2 Rückfall je Prüfgröße und Richtung (A9.11, §8.10) | Rückfall je Prüfgröße; bei verfehlter Bestätigung, aber eingehaltenem P(auffällig \| exakt) ≤ 0,05 einseitige Auswertung | weiterer Ausgang „keine Überschreitung nachgewiesen“; E3 insgesamt ist dann nie „unauffällig“ | A9.11: „Verfehlt eine E3-Prüfgröße (E3a, E3b) in Teil B ein Kriterium, gilt der Rückfall nur für sie. Ist P(auffällig \| exakt) ≤ 0,05 eingehalten und nur P(unauffällig \| exakt) ≥ 0,8 verfehlt, wird sie einseitig ausgewertet: ‚auffällig‘ (Überschreitung nachgewiesen) oder ‚keine Überschreitung nachgewiesen‘; sonst nur beschreibend. Beides ist kein bestandener Test; E3 ist dann nicht ‚unauffällig‘.“ | `kontrollen.e3_auswerten`: Status je Prüfgröße; Kalibriersimulation: beide Kriterien je Prüfgröße und Präzisionsstufe |
| E3 Bonferroni-Prüfzahl und Prüfmenge (A9.13) | feste Prüfzahl m = 2·N_K + 1 (43) über die Schnittkonfigurationen und den Triphasik-Punkt, ohne Zusatz- und Identifizierbarkeitskonfigurationen | bei fehlenden Punkten etwas konservativ (z_B 3,05 statt 3,00) | A9.13: „z_B ist das einseitige Bonferroni-Quantil zu α = 0,05 mit m = 2·N_K + 1, unabhängig von der Zahl auswertbarer Konfigurationen; Prüfmenge sind die Schnittkonfigurationen und der Triphasik-Punkt.“ | `e3_auswerten` mit festem m aus Teil B; Raten neu zählen (gleiche Kampagnen) |
| G1 k der Pilotgrößen für G4 (technisch) | σ_Δ,F mit dem festgelegten k_max bilden | A4: G4-Rate 2,8 % → 4,3 % (v0k); c von A4 neu | A9.2 (Reihenfolge der Schwellen), Klarstellung: „σ_Δ für F_min − ⟨N⟩ wird mit dem festgelegten k_max gebildet.“ | `pilot`/`teil_b`: σ_Δ beim festgelegten k_max übergeben; Kalibrierung A4 neu |
| G2 Schwellenübertragung von G4 (§9.1) | konfigurationsabhängige Standardisierung v2, vor Phase 1 aus Phase 0 festgelegt | Methodik in Teil A und B; an den steilsten Punkten werden Amplitudentrends unter etwa 1 % nicht mehr erkannt, weil sie dort im Jitter liegen; flache Punkte unverändert | §9.1 G4, Zusatz: „Für X = F_min − ⟨N⟩ an der Kombinationskonfiguration i gilt σ²_Δ,F,i = σ²_Δ,F + max(0, s²_i − s̄²_P); s_i ist die aus Phase 0 vorhergesagte Jitterstreuung der Fünftel-Differenz (Vorhersage ŷ⁰, Jitter σⱼ der Piloten, ⌊N_z/5⌋ Zyklen je Fünftel, feste Ziehungen) und s̄²_P ihr Mittel über die Pilotkonfigurationen [Teil B]. Die Schwelle ist nie kleiner als 3·σ_Δ,F.“ | `gueltigkeit` (σ je Konfiguration), `teil_b` (s_i), Tests; Kalibrierung c_H1/c_H1Z/Rauschbias/H2 neu; G4-Ausschlussrate je Punkt und Trendempfindlichkeit als Kriterium |
| G3 Reserve und Wiederholungen (A9.2 (v), A9.12) | „+2“ beibehalten; Planungs- und Kalibriersimulation mit Wiederholungen; gemeinsame Vollständigkeit direkt zählen | Generator und Planung brauchen Wiederholungsplätze und mehr simulierte Läufe; die Messzeit enthält die Wiederholungen | A9.2 (v), Zusatz: „Die Planungssimulation bildet die Wiederholungen nach A9.12 ab. r = ⌈n_min·p̂/(1 − p̂)⌉ + 2 gilt, wenn alle Punkte in mindestens 95 % der simulierten Kampagnen n_min gültige Läufe erreichen; sonst wird r erhöht, bis das erreicht ist.“ | Generator (`kampagne.laufplan`, Ebene H/Z), Planungshaken, Zeitformel; Kalibrierung mit Wiederholungen |

Vom Autor zu entscheiden sind E1/E2 (zusammen) und G2. E3, G1 und G3 sind Folgerungen mit wenig Ermessen: E3 und G1
betreffen Prüfzahl bzw. Konsistenz mit dem vorhandenen Wortlaut, G3 die Abbildung des registrierten Ablaufs. Offen
bleibt bei G3 das Ziel 0,95.

## 6 Grenzen

- **Umfang:** synthetisch, Ebene H, L1, drei Referenzsysteme mit exakter Superposition, je 40 Kampagnen. Kampagnenanteile
  tragen Wilson-Intervalle von etwa ±10 Prozentpunkten.
- **Wiederholungen:** am Platz des ursprünglichen Laufs, ohne den G1-Sonderablauf (andere Regeln, überwiegend G1,
  machen auf L1 0,5–0,7 % der Läufe ungültig).
- **Rauschmodell:** Der Jitter ist weiß je Zyklus, der Generator stationär. Ein farbiger oder zwischen Modulen
  korrelierter Jitter ändert s_i. Die Vorhersage aus Phase 0 lässt sich an den Piloten prüfen (3.3), muss aber an realen
  Daten bestätigt werden.
- **Varianten:** ε_ctrl, G1 und p̂ bleiben produktiv. Der Trendfall prüft Amplituden- und Nullpunkttrends, keine
  Phasendrift.
- **E3:** stammt aus den Neuläufen von PR #21, mit den Grenzen des T-Modells (keine Kippmoden, keine Modullagen, keine
  Kreuzkovarianzen getrennter Kalibriermessungen).
- **Orakel:** kein Messverfahren.
- **Nicht Teil dieses Auftrags:** Drift-Zusatz, ungleiche Periodendauern in K19, weitere Szenariogruppen, Hardware.

## 7 Dateien und Abnahme

| Datei | Inhalt |
|---|---|
| `auftrag.json` | Auftragsliste vor den Rechnungen: Seeds, Profil, Plan, Werkzeug 8, Zielpilot, E3-Herkunft |
| `werkzeug8_V1G60h.json/.npz` | Werkzeug 8 V1-G60h, wiederverwendet (Herkunft im Kopf) |
| `e3_pruefgroessen.csv` | E3a (zusammengefasst) und E3b je Kampagne der 570 Neulaufkampagnen, volle Genauigkeit |
| `g4_kampagnen.csv` | je Kampagne: Seed, p̂, r(p̂), σ_Δ, Jitter, Wiederholungen je Variante, Ausgänge der vollen Ketten |
| `g4_konfigurationen.csv` | je Kampagne und Punkt: Verletzungen (D_N, D_F, nur G4, andere), je Variante G4, Bestand und Block des 18. gültigen Platzes ohne/mit Wiederholung |
| `g4_trendfall.csv` | Trendfall je System, Trend, Stärke und Variante |
| `ergebnisse.json` | alle Zähler und Raten, Nullresiduum, Herkunft (Checkpoints, Code, Profil, Seeds, Laufzeiten) |

Alle Zähler dieses Berichts lassen sich aus den CSV-Dateien nachzählen. Beispiel: Ein Punkt unter n_min bei n Blöcken
heißt `b18_<Variante> > n`, mit Wiederholungen `b18w_<Variante> > n`.

Abnahme am finalen Codestand: siehe PR-Beschreibung.
