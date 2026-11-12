# Statusvermerk — Ergebnisnotiz vom 13.09.2026 (adaptiver Burn-in)

**Stand: 12.11.2026 · Matthias Früh · ORCID 0009-0005-9984-4207**

**Betrifft:** [`PCMMS_Ergebnisnotiz_Sweep_Burnin_2026-09-13_v2.txt`](PCMMS_Ergebnisnotiz_Sweep_Burnin_2026-09-13_v2.txt) in diesem Ordner.\
**Status der Notiz:** historischer Rechenstand, im Liftoff-Bereich teilweise überholt. Die Notiz bleibt unverändert erhalten.\
**Grundlage:** Entscheidung des Autors vom 12.11.2026 zu AP-17 ([`docs/arbeitsplan_status.md`](../../arbeitsplan_status.md)).

Dieser Vermerk nennt die Angaben der Notiz, die spätere Prüfungen eingeschränkt oder überholt haben, und das, was weiter verwendet werden kann. Er enthält keine neue Rechnung; jede Angabe verweist auf ein vorhandenes Dokument. Alle Zahlen sind Simulation, Messdaten gibt es nicht.

## Einordnung

Die Notiz dokumentiert die Nachrechnung des 19×19-Rasters mit adaptivem Burn-in (Festschritt-RK4, Δt = 50 µs, Standardstart). Sie ist Beleg der Korrektur im Arbeitspapier v2.3: Das Residuum des Zeitmittels zerfällt in Randterm und Quadratur. Diese Zerlegung gilt weiter.

Überholt oder eingeschränkt sind Angaben, die auf Periodenlabels, Einschwingdauern und Zustandszuordnungen der Festschritt-Rechnung im Liftoff-Bereich beruhen. Die zwölf Dauerkontaktpunkte des Rasters sind nicht betroffen.

Spätere Prüfungen, auf die sich dieser Vermerk stützt:

- Engine-Prüfung, Stand 02.10.2026: [`rechnungen/engine/PROTOKOLL.md`](../../../rechnungen/engine/PROTOKOLL.md) (ENG-01 bis ENG-10, „Korrekturen an Quellen“ Nr. 4 bis 6)
- unabhängige Gegenprüfung dazu, Stand 02.10.2026: [`rechnungen/engine/verifikation/PROTOKOLL.md`](../../../rechnungen/engine/verifikation/PROTOKOLL.md)
- Arbeitspapier v2.5 vom 16.10.2026: [`PCMMS_Arbeitspapier_v2_5.pdf`](../PCMMS_Arbeitspapier_v2_5.pdf), Abschnitt „Prüfung gegen die erhaltene Basislinie“, Anhang A.1 („Hinweis zum Einschwingen“), Anhang B.4 („Numerik“) und B.6 („Bekannte Grenzen des Modells“)

## Überholte oder eingeschränkte Angaben

### 1 Periodenlabels und Einschwingzeiten

- **Notiz:** §2 („Orbitperioden: P1 211, P2 104, P3 8, …; nicht periodisch bis 40 s: 23“; „Burn-in: Median 5,0 s, 90 % ≤ 8,5 s, max 40 s“), §2b, §4c („Bifurkationsstruktur“). Die Notiz schränkt die Labels selbst ein: Die Karte zeigt die Wiederkehr bei Fensteröffnung.
- **Späterer Stand:** Die Labels stammen aus der Festschritt-RK4 mit einer Wiederkehrtoleranz von 10⁻³ m/s. Hüpfzustände streuen dort proportional zur Schrittweite um 3–6·10⁻⁴ m/s. Periodenlabels und Einschwingzeiten der Festschritt-Rechnung sind im Liftoff-Bereich nicht belastbar. Bestätigt ist die Periode 2 bei (0,0): Sie ist ereignisgenau stabil (|µ| = 0,551).
- **Fundstellen:** Engine-Prüfung ENG-05 und Korrektur Nr. 6; Gegenprüfung ENG-05 (bestätigt); Arbeitspapier v2.5, Anhang B.4.

### 2 (12,17)/(17,12) und (2,14)/(14,2)

- **Notiz:** Änderungslog, §2b und §3 („langer Transient, ab 21 s Orbit P30“; „Archivwert λ 75,6 % (5–15 s) war Transient“; „(2,14)/(14,2): P3“; „Burn-in-Fälle, keine Bistabilität nachgewiesen“).
- **Späterer Stand:** Der Wert um 75,6 % ist kein Transient, sondern ein stabiler Hüpfzustand (ereignisgenau |µ| = 0,741). Im ereignisgenauen Modell führt der Standardstart an (12,17), (14,2) und (2,14) in diesen Zustand. Daneben besteht ein aperiodischer Zustand um 35 %. Die Orbits P30 und P3 existieren ereignisgenau, sind aber instabil (|µ| = 29,5 bzw. 1,24); die Festschritt-RK4 stabilisiert sie künstlich. Welchen Zustand die Festschritt-Rechnung wählt, kippt mit Schrittweite und Arithmetik.
- **Grenze:** Der Zustand um 35 % ist ereignisgenau über 40 s (Engine-Prüfung) und 100 s (Gegenprüfung) geprüft, ohne Floquet-Analyse; ein sehr langer Transient ist nicht ausgeschlossen. Die Multiplikatoren von P30 und P3 hat die Gegenprüfung nicht nachgerechnet.
- **Fundstellen:** Engine-Prüfung ENG-05, ENG-08 und Korrektur Nr. 5; Gegenprüfung ENG-05, ENG-08 (eingeschränkt), ENG-10 und Zusatzbefund 2.

### 3 (2,13)/(13,2) mit (6,8)/(8,6) und (11,17)

- **Notiz:** §2b und §3 („Transient ≈ 40 s, dann P6“; „Burn-in-Fall, keine Bistabilität nachgewiesen“; (6,8)/(8,6) und (11,17) „aperiodisch, Fensterstatistik variabel“). Die Punkte gehören zu derselben Bahn gleichwertiger Konfigurationen (Bahn 44).
- **Späterer Stand:** Im Raster mit drei Starts hat diese Bahn mindestens zwei Zustandsgruppen: Tiefzustände um 36–38 % Liftoff und einen Hüpfzustand um 75,3 % (impulskonsistenter Start). Eine ereignisgenaue Prüfung des P6-Orbits ist in den Protokollen nicht aufgeführt.
- **Grenze:** Die aperiodischen Tiefzustände sind ohne Floquet-Analyse geprüft; sehr lange Transienten sind nicht ausgeschlossen.
- **Fundstellen:** [`rechnungen/engine/grid_bahnen_zustaende.csv`](../../../rechnungen/engine/grid_bahnen_zustaende.csv) (Bahn 44); Engine-Prüfung ENG-09; Gegenprüfung ENG-09 (Einschränkung).

### 4 (1,16)/(16,1) und (15,16)/(16,15)

- **Notiz:** §2b, §3 und §4e („aperiodisch, statistisch stationär“; A_max = 6,928 als „Kennzahl eines aperiodischen, statistisch stationären Zustands“; R ±3700 ppm bzw. ±6500 ppm).
- **Späterer Stand:** Der Zustand mit A_max bei (1,16)/(16,1) ist ereignisgenau ein stabiler Orbit der Periode 3 (λ = 71,857 %, γ₁ = 1,976, F_max = 50,53 N, |µ| = 0,354). An derselben Konfiguration besteht daneben ein stabiler Zustand der Periode 1 mit λ = 76,195 %. Auch (15,16)/(16,15) liegt ereignisgenau auf einem Orbit der Periode 3. Der Randterm entsteht an diesen Punkten, weil das Fenster von 100 Zyklen kein Vielfaches der Orbitperiode ist (Ursache 2 in §4a der Notiz, nicht Ursache 3). Die Fensterwerte der Notiz für λ und A stimmen damit überein.
- **Fundstellen:** Engine-Prüfung ENG-08 (Paar P33); Gegenprüfung ENG-05, ENG-08 und Zusatzbefund 2.

### 5 Hot-Spot (0,11)/(11,0)

- **Notiz:** §3 und §4a („Archiv einschwing-kontaminiert“; Einschwingen als Ursache des Randterms von −6816 ppm).
- **Späterer Stand:** Die Attraktorwerte der Notiz gelten: ereignisgenau λ = 75,08 % und F_max = 38,5 N auf einem stabilen Orbit der Periode 1. Das lange Einschwingen ist aber keine Eigenschaft der Konfiguration, sondern ein Artefakt der Festschritt-RK4 bei Δt = 50 µs. Ereignisgenau liegt die Bahn nach etwa 5 s auf dem Orbit, und im Fenster 5–15 s weicht das Zeitmittel um +0,02 mN von M·g ab.
- **Fundstellen:** Arbeitspapier v2.5, Abschnitt „Prüfung gegen die erhaltene Basislinie“ und Anhang A.1; Engine-Prüfung ENG-03 mit Gegenprüfung (eingeschränkt); [`data/README.md`](../../../data/README.md); [`tests/test_ereignisloeser.py`](../../../tests/test_ereignisloeser.py).

### 6 Robustheit der Karte

- **Notiz:** §3 („Rund 97 % der Karte sind robust; der Burn-in von 5 s reichte dort“) und §6 Nr. 1 (Bistabilität offen).
- **Späterer Stand:** Die Aussage gilt gegenüber der Burn-in-Länge beim Standardstart. Gegenüber dem Startprotokoll ist die Karte im Liftoff-Bereich nicht eindeutig: Mindestens 99 von 361 Rasterpunkten (18 von 70 Bahnen) gehören zu Konfigurationen mit koexistierenden Zuständen. Ein längerer Burn-in ändert daran nichts. Die Rasterwerte sind dort die vom Standardstart gewählten Zustände. Die in §6 Nr. 1 offene Frage nach Bistabilität an (12,17) und (2,13) ist damit im Grundsatz beantwortet; die Grenzen stehen unter Nr. 2 und 3.
- **Fundstellen:** Engine-Prüfung ENG-08, ENG-09 und Korrektur Nr. 4; Gegenprüfung ENG-09 (bestätigt, Untergrenze auch ereignisgenau gestützt); Arbeitspapier v2.5, Anhang B.6; [`README.md`](../../../README.md), Abschnitt zum 19×19-Phasensweep.

### 7 Extremwerte (Prüfhinweis)

- **Notiz:** §3 („Unverändert: A_max = 6,928 …; N_max,max = 50,55 N“) und §5 Nr. 5.
- **Späterer Stand:** Die Werte sind Extremwerte der Festschritt-Rechnung und über die drei geprüften Starts stabil (λ bis 76,2 %, A 6,90–6,93, F_max 50,4–50,6 N). Als Schranken des Modells sind sie nicht zu lesen: Im ereignisgenauen Raster der Gegenprüfung liegt (3,3) = (56,84°, 56,84°) mit Standardstart in einem aperiodischen Zustand mit λ = 70,7 %, γ₁ = 1,999 und F_max = 51,6 N (Fenster 30–40 s); im Fenster 10–20 s ist A = 7,07. Die Festschritt-Raster zeigen an diesem Punkt λ = 76,2 %.
- **Einordnung:** Prüfhinweis nach Entscheidung des Autors vom 12.11.2026. Das [`README.md`](../../../README.md) nennt weiter die Spannweiten des Festschritt-Rasters (F_max bis 50,6 N) und ist mit diesem Vermerk nicht geändert. Der Befund stammt aus dem ereignisgenauen Raster mit Standardstart und beruht auf einzelnen Fenstern von 10 s; der Zustand ist dort als aperiodisch geführt.
- **Fundstellen:** Engine-Prüfung ENG-09; Gegenprüfung, Zusatzbefund 4.

## Weiterhin verwendbar

- Die Zerlegung des Residuums in Randterm und Quadratur mit den Kernzahlen aus §2 (315 / 24 / 22 Konfigurationen; größter Randterm 3714 ppm; Quadratur überall unter 100 ppm). Sie steht so im Arbeitspapier v2.5.
- Die Unterscheidung der drei Ursachen des Randterms in §4a. Die Zuordnung einzelner Punkte ist nach Nr. 2 bis 5 zu berichtigen.
- Die 36 Rasterpunkte mit negativer Schiefe; sie sind in allen geprüften Startvarianten dieselben (Engine-Prüfung ENG-09).
- Die Folgerungen für das Verfahren in §5 Nr. 4: Wiederkehr und Fensterstatistik fortlaufend mitführen, über ganze Orbitperioden auswerten, den Randterm getrennt berichten.

## Grenzen der späteren Prüfungen

- Die Rasterzählung beruht auf Festschritt-RK4 mit drei Starts über 40 s. Ereignisgenau gerechnet sind sechs Bahnpaare, einzelne repräsentative Punkte und in der Gegenprüfung das Raster mit zwei Starts über 20 s bzw. 30 s.
- Aperiodische Zustände sind ohne Floquet-Analyse und über höchstens 100 s geprüft.
- Einzugsgebiete und Häufigkeiten der koexistierenden Zustände sind am Referenzparametersatz nicht bestimmt. Die Nacharbeit der Karten als Attraktormengen ist AP-25 mit Status „später“ ([`docs/arbeitsplan_status.md`](../../arbeitsplan_status.md)).

## Hinweise zur Notiz

- Zahlen der Notiz zum Liftoff-Bereich sind nur zusammen mit diesem Vermerk zu verwenden.
- R und Q der Notiz heißen im Formelverzeichnis δ_w und δ_Q ([`LIESMICH.md`](LIESMICH.md)).
- Zwei in der Notiz genannte Dateien liegen nicht im Repository: `PCMMS_Sweep_Karten_Periode_Randterm_2026-09-13.txt` und `sweep_19x19_burnin_2026-09-13.log`.

---

*Vermerk:* Erstellt am 12.11.2026, Chat-Sitzung (Claude), nach Auftrag des Autors. Die Fundstellen sind am Repository-Stand `e9eb170` geprüft. Lizenz: CC BY 4.0 wie `docs/`.
