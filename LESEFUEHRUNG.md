# Leseführung

**PCMMS — Phasenkontrollierte Mehrmassensysteme**\
Matthias Früh · Unabhängiger Forscher · ORCID [0009-0005-9984-4207](https://orcid.org/0009-0005-9984-4207)\
Stand: 11. November 2026 · abgeglichen mit dem Repository-Stand `d8384bc` (nach Pull Request #30)

Diese Datei führt durch das Repository: was man in welcher Reihenfolge liest und was beim Lesen gilt. Sie ordnet
nach Anliegen und ersetzt nichts. Die durchgehende Lesereihenfolge steht im Wegweiser
[`docs/overview.md`](docs/overview.md), der Inhalt der Ordner in der Inhaltstabelle des [README](README.md), der
Bearbeitungsstand der Arbeitspakete in [`docs/arbeitsplan_status.md`](docs/arbeitsplan_status.md).

---

## Schnelleinstieg

| Anliegen | Einstieg |
|---|---|
| ohne Vorwissen | [`docs/was_ist_pcmms.md`](docs/was_ist_pcmms.md) |
| fachlich beurteilen | [`docs/werkstattbericht.md`](docs/werkstattbericht.md), dann [`docs/einordnung.md`](docs/einordnung.md) |
| nachrechnen | [README, „Nachrechnen“](README.md#nachrechnen), dann [`data/README.md`](data/README.md) |
| Messtechnik und Messrahmen | [`docs/konzepte/README.md`](docs/konzepte/README.md), darin der [Sechs-Nadel-Messrahmen](docs/konzepte/nadelrahmen_dreimassenkoerper_2026-10.md) (Konzepte) |
| Stand und offene Punkte | [`docs/arbeitsplan_status.md`](docs/arbeitsplan_status.md) |

Ausführlich: die Lesepfade A bis H unten.

## Drei Dinge, die beim Lesen gelten

1. **Alles ist Simulation oder Analytik.** Messdaten existieren nicht. Jede Zahl gilt für den Parametersatz, der
   bei ihr steht.
2. **Das Zeitmittel ist Kontrollgröße, kein Ergebnis.** ⟨N⟩ = M·g folgt aus dem Schwerpunktsatz. Untersucht wird
   die Wellenform der Kontaktkraft N(t), ausgewertet als Abweichung gegen diese Referenz.
3. **Der Status gehört zur Aussage.** Entwurf, Konzept, Vermerk, zurückgezogen: Die Dokumente nennen am Kopf, was
   sie sind. Die Begriffe stehen unten unter [Kennzeichnungen](#kennzeichnungen).

## Lesepfade nach Anliegen

Das Repository hat rund 1100 Dateien. Zum Verstehen genügen wenige: 697 Dateien sind das Nachweisarchiv
[`rechnungen/`](rechnungen/README.md), weitere 154 liegen in vier Beleg- und Berichtsordnern unter `docs/`
(Skripte, Ausgaben und Daten zu den Softwareberichten und zur Entscheidungsvorlage). Für den Einstieg ist davon
nichts nötig. Die Minutenangaben sind Richtwerte aus dem Textumfang (rund 200 Wörter je Minute).

### A · Ohne Vorwissen (etwa 10 Minuten)

1. [`docs/was_ist_pcmms.md`](docs/was_ist_pcmms.md) (≈ 6 min) – Grundidee, was gemessen wird, was nicht behauptet
   wird.
2. [README, „Abbildungen“](README.md#abbildungen) – Zeltkurve, Phasenkarten und Wellenformen aus der Simulation.
3. [`docs/zehn_fragen.md`](docs/zehn_fragen.md) (≈ 4 min) – die üblichen Einwände in Kurzform.

### B · Fachlich einordnen (etwa 1 Stunde)

In der Reihenfolge des Wegweisers; der Literaturabgleich folgt in C:

1. [`docs/werkstattbericht.md`](docs/werkstattbericht.md) (≈ 11 min) – warum die Wellenform und nicht der
   Mittelwert; wie stark die Leitzahlen an der angenommenen Kontaktsteifigkeit hängen.
2. [`docs/expose_2026-09.md`](docs/expose_2026-09.md) (≈ 10 min) – Kernfrage, Stand, messbares Signal, offene
   Entscheidungen zum Aufbau.
3. [`docs/praeregistrierung_2026-06.md`](docs/praeregistrierung_2026-06.md) (≈ 2 min) – Hypothesen,
   Falsifikationskriterien und Abbruchregeln vom Juni 2026.
4. [`docs/neuheitsgrad.md`](docs/neuheitsgrad.md) (≈ 8 min) – was nicht neu ist und was als möglicher Beitrag
   übrig bleibt (§7, §8).
5. [`docs/einordnung.md`](docs/einordnung.md) (≈ 14 min) – geschrieben für Leser, die Mechanik können und PCMMS
   nicht kennen; Abschnitt 8 nennt, wo die Argumentation dünn ist.
6. [`docs/archiv_vermerk_kernhypothese_v3.md`](docs/archiv_vermerk_kernhypothese_v3.md) (≈ 3 min) – Rückzug der
   Mittelwertverschiebung: Artefakt des damaligen Kontaktmodells.

Vertiefung: [README, „Simulationsstand“](README.md#simulationsstand) mit Parametersatz, Befunden und Aufrufen.
Dann das [Arbeitspapier v2.5](docs/arbeitspapier/README.md) – wer nicht alle 112 Seiten liest: Kurzfassung,
„Status und Versionshinweis“, Kapitel 1 (mit „Beitrag dieser Arbeit“), Kapitel 9 (Simulationsstudie), Kapitel 10
(Artefaktanalyse) und Kapitel 12 (Fazit). Symbole und Definitionen stehen im
[Formelverzeichnis v2.8](docs/formelverzeichnis/README.md) (36 Seiten, zum Nachschlagen).

### C · Kritisch prüfen: Rückzüge, Literatur, Beitragsaussagen

Setzt B voraus; dort stehen Neuheitsgrad, Archiv-Vermerk und die Schwachstellen (Einordnung, Abschnitt 8).

1. [`docs/arbeitspapier/README.md`](docs/arbeitspapier/README.md) – Änderungen v2.3 bis v2.5, darunter der Rückzug
   der Vorzeichenregel der Schiefe, und die Berichtigung vom 10.11.2026 zu Anhang C; die Belege der Korrekturen
   liegen in den Unterordnern.
2. [`docs/literaturabgleich_2026-09-12.md`](docs/literaturabgleich_2026-09-12.md) – Abgleich mit der Ratchet-,
   Tribologie- und Kontaktdynamik-Literatur; noch nicht ins Arbeitspapier übernommen.
3. [`docs/abgleichnotiz_2026-11-10_gutachten.md`](docs/abgleichnotiz_2026-11-10_gutachten.md), Abschnitte 1, 2
   und 4 – Abgleich eines simulierten Fachgutachtens (keine unabhängige Begutachtung), Prüfung dreier
   Literaturangaben, Abweichungen zwischen den Beitragsaussagen (BA-1 bis BA-5).
4. [`PCMMS_Arbeitspapier_Offene_Punkte.md`](docs/arbeitspapier/PCMMS_Arbeitspapier_Offene_Punkte.md) – offene
   Punkte, darunter die Primärquellenprüfung der Literatur (Nr. 42).

### D · Nachrechnen

1. [README, „Nachrechnen“](README.md#nachrechnen) – Installation, Aufrufe, Laufzeiten. Was welches Skript tut,
   steht in der Inhaltstabelle des README.
2. [`data/README.md`](data/README.md) – Spalten, Parametersatz und Eigenheiten jedes Datensatzes.
3. [`docs/abgleichnotiz_2026-11-10_gutachten.md`](docs/abgleichnotiz_2026-11-10_gutachten.md), Abschnitt 5 – fünf
   Referenzfälle mit Sollwerten und Aufrufen; nachgerechnet ist dort nur R-1.
4. [`docs/praeregistrierung_v2_anhang.md`](docs/praeregistrierung_v2_anhang.md), Abschnitt Z – Zahlennachweis mit
   den Befehlen zu den Zahlen der Präregistrierung v2.
5. [`tests/`](tests/) – Testsuite; Aufruf im README.
6. [`rechnungen/README.md`](rechnungen/README.md) – Nachweisarchiv der Gesamtprojektanalyse, historischer Stand
   02.10.2026; nur bei Bedarf.

### E · Messkampagne und Auswertung

Entwurf und Anhang der Präregistrierung v2 haben zusammen rund 47 000 Wörter; gezielt lesen.

1. [`docs/praeregistrierung_v2_entwurf.md`](docs/praeregistrierung_v2_entwurf.md) – zuerst Kurzfassung und §0,
   dann §3 (Hypothesen) und §12 (offene Punkte vor dem Einfrieren).
2. [`docs/praeregistrierung_v2_anhang.md`](docs/praeregistrierung_v2_anhang.md) – A0 (Änderungen gegenüber v1),
   Tabelle C (Artefakte und Kontrollen), Tabelle F (Festlegungen).
3. [`docs/abnahme_ap02_ap03.md`](docs/abnahme_ap02_ap03.md) und
   [`docs/einzugsgebiete_v1_kandidat.md`](docs/einzugsgebiete_v1_kandidat.md) – Auslegungswerkzeug, ereignisgenauer
   Löser und Attraktorkarten des V1-Kandidaten.
4. [`docs/ap11_ap12_ap13_software.md`](docs/ap11_ap12_ap13_software.md) – Kurzfassung zuerst; dazu
   [Schnittstellen](docs/ap11_ap12_ap13_schnittstellen.md), [Regelmatrix](docs/ap11_ap12_ap13_regelmatrix.md),
   [Kriterienmatrix](docs/ap11_ap12_ap13_kriterien.md) und der
   [Plan des Pipelinetests](docs/plan_ap13_pipelinetest.md). Nur synthetische Daten; AP-13 ist nicht abgenommen,
   die große Kalibrierung nicht ausgeführt.
5. [`docs/entscheidungsvorlage_2026-10-19.md`](docs/entscheidungsvorlage_2026-10-19.md) – Herkunft des Regelstands
   2026-11 (Abschnitt 9); Skripte und Ausgaben dazu im
   [Belegordner](docs/entscheidungsvorlage_2026-10-19_belege/README.md). Berichte vom 17.10.2026:
   [Neuläufe](docs/ap13_neulaeufe_2026-10-17/bericht.md),
   [Diagnose E3b/G4](docs/e3b_g4_diagnose_2026-10-17/bericht.md),
   [k-Konsistenz und Ablauf](docs/ap13_kmax_wiederholungen_2026-10-17/bericht.md). Beispiele zum Regelstand:
   [`rechnungen/kalibrierbeispiel/`](rechnungen/kalibrierbeispiel/README.md),
   [`rechnungen/regelstand_2026-11/`](rechnungen/regelstand_2026-11/README.md).

### F · Messtechnik, Aufbau und Messrahmen

Alle Dokumente in `docs/konzepte/` sind Konzepte: nicht umgesetzt, nicht an Hardware geprüft.

1. [`docs/konzepte/README.md`](docs/konzepte/README.md) – Tabelle aller Konzepte mit Stand, Arbeitspaket und
   Status.
2. [`nadelrahmen_dreimassenkoerper_2026-10.md`](docs/konzepte/nadelrahmen_dreimassenkoerper_2026-10.md) –
   Sechs-Nadel-Messrahmen (Nord, Süd, Ost, West, oben, unten) mit eingebettetem Dreimassenkörper: die
   Rundum-Messung. Rechnungen dazu in [`rechnungen/nadelrahmen/`](rechnungen/nadelrahmen/PROTOKOLL.md).
3. [`mehrkanal_messarchitektur_2026-05.md`](docs/konzepte/mehrkanal_messarchitektur_2026-05.md) und
   [`messtechnik_anschluss_v2_2026-09.md`](docs/konzepte/messtechnik_anschluss_v2_2026-09.md) – Messkanäle, Mess-
   und Prüfrahmen.
4. Konzeptentwürfe vom Oktober 2026:
   [Dual-Armführung v0.4](docs/konzepte/anforderungsspezifikation_dual_armfuehrung_v0_4_2026-10-29.md),
   [Massenkonzentration v0.1](docs/konzepte/massenkonzentration_v0_1_2026-10-31.md),
   [Messoption Schwerkraftbezug v0.1](docs/konzepte/messoption_schwerkraftbezug_lageadaptive_fuehrung_v0_1_2026-10-31.md).
5. [`laborplan_v1_2026-05.md`](docs/konzepte/laborplan_v1_2026-05.md) – Laborplan Variante 1. Die Varianten 2
   und 3, Gate-Matrix und Anforderungsprofil sind Nebeninformation.

### G · Linie B und Linie C

Linie B ist optional und hat eine eigene Apparatur; im Arbeitsplan Stufe S5, Status „später“. Linie C ist geparkt.

1. [`docs/linie_b/README.md`](docs/linie_b/README.md) – Übersicht der Dokumente mit Status.
2. [`abgrenzung_v3_6_entwurf3_2026-10-29.md`](docs/linie_b/abgrenzung_v3_6_entwurf3_2026-10-29.md) – zwei
   Fassungen der Linie B, Teilung B1/B2 als Vorschlag; Entscheidung D-2 offen.
3. [`forschungsrahmen_v3_5_2026-05.md`](docs/linie_b/forschungsrahmen_v3_5_2026-05.md) und
   [`richtungsnotiz_medienkopplung_2026-09-06_v5_2.md`](docs/linie_b/richtungsnotiz_medienkopplung_2026-09-06_v5_2.md)
   – jeweils zuerst den Vermerk am Kopf lesen.
4. [`rechnungen/linie_b/PROTOKOLL.md`](rechnungen/linie_b/PROTOKOLL.md) – Kontrollrechnungen zu den Modellen.
5. Demonstrator: [Konzept](docs/konzepte/demonstrator_ballon_2026-05.md),
   [Auswerteskripte](code/demonstrator/README.md), [Firmware-Muster](code/firmware/README.md) – nicht getestet,
   keine Messdaten.
6. Linie C: [`linie_c_energiebilanz_modellvergleich_2026-09-05.md`](docs/konzepte/linie_c_energiebilanz_modellvergleich_2026-09-05.md)
   – methodische Notiz.

### H · Aktueller Stand und offene Punkte

1. [`docs/arbeitsplan_status.md`](docs/arbeitsplan_status.md) – Arbeitspakete AP-01 bis AP-30 mit Status; am Ende
   die offenen Entscheidungen des Autors.
2. [`docs/abgleichnotiz_2026-10-29_v4.md`](docs/abgleichnotiz_2026-10-29_v4.md) – Abgrenzung der Linien A, B
   und C, Entscheidung D-1, offen D-2 bis D-6.
3. [`docs/abgleichnotiz_2026-11-10_gutachten.md`](docs/abgleichnotiz_2026-11-10_gutachten.md), Abschnitt 7 –
   offen E-1 bis E-4.
4. [`docs/overview.md`](docs/overview.md) – verbindliche Begriffe; was nicht im Repository liegt.

## Kennzeichnungen

| Kennzeichnung | Bedeutung |
|---|---|
| Simulation, keine Messdaten | gilt für jede Zahl und jeden Datensatz |
| Arbeitsfassung | Präregistrierung vom Juni 2026: nicht extern registriert, unverändert |
| Entwurf, Entwicklungsversion | Präregistrierung v2: nicht eingefroren, nicht registriert |
| Arbeitsfestlegung | vorläufige Regel des Autors, vor dem Einfrieren überarbeitbar |
| Konzept, Nebeninformation | nicht umgesetzt; keine Entscheidung |
| Vermerk am Kopf | sagt, was seit der Entstehung überholt oder offen ist; zuerst lesen |
| zurückgezogen, Archiv | Mittelwertverschiebung; Netto-Impulsübertragung ohne äußeren Partner; allgemeine Vorzeichenregel der Schiefe |
| historisch | nicht nachgeführt: Protokolle in `rechnungen/`, Regelstand 2026-10 |
| vorhanden · vorläufig · in Bearbeitung · noch nicht umgesetzt · später | Status der Arbeitspakete, definiert in [`docs/arbeitsplan_status.md`](docs/arbeitsplan_status.md); Stufe S5 ist geparkt |
| Notiz, kein Arbeitsauftrag | Abgleichnotizen: halten fest, lösen nichts aus |
| offene Entscheidung des Autors | wird geführt; daraus entsteht kein Entwicklungsauftrag |

Vorrang bei Widerspruch:

- Konzept gegen Präregistrierung v2 oder Werkzeuge in `code/`: Für Hypothesen, Entscheidungsregeln und Auslegung
  gelten die Präregistrierung v2 (Entwicklungsversion) und die Werkzeuge; für die Linie-B-Unterlagen stattdessen
  die Kontrollrechnungen in `rechnungen/linie_b/` und die Dokumente in `docs/linie_b/`
  ([`docs/konzepte/README.md`](docs/konzepte/README.md)).
- Protokoll in `rechnungen/` gegen Text in `docs/`: `docs/` gilt ([`rechnungen/README.md`](rechnungen/README.md)).
- Fassungen außerhalb des Repositorys gegen dieses Repository: das Repository gilt
  ([`docs/overview.md`](docs/overview.md)).

## Gültige Fassungen

| Gegenstand | Gültig | Hinweis |
|---|---|---|
| Arbeitspapier | [v2.5](docs/arbeitspapier/PCMMS_Arbeitspapier_v2_5.pdf), 16.10.2026 | PDF am 02.11.2026 neu gesetzt, 112 Seiten; die Berichtigung vom 10.11.2026 zu Anhang C steht im [README des Ordners](docs/arbeitspapier/README.md), nicht im PDF |
| Symbol- und Formelverzeichnis | [v2.8](docs/formelverzeichnis/PCMMS_Formelverzeichnis_v2_8.pdf), 16.10.2026 | PDF am 02.11.2026 neu gesetzt, 36 Seiten |
| Präregistrierung | [Juni 2026](docs/praeregistrierung_2026-06.md), Arbeitsfassung | für die Messkampagne liegt v2 als [Entwurf](docs/praeregistrierung_v2_entwurf.md) vor |
| Exposé | [September 2026](docs/expose_2026-09.md) | ersetzt die Fassungen Mai und Juli 2026 |
| Regeln der Auswertesoftware | [Regelstand 2026-11](docs/ap11_ap12_ap13_regelmatrix.md) | Arbeitsfestlegungen, statistisch nicht kalibriert; [Regelstand 2026-10](docs/ap11_ap12_ap13_regelmatrix_2026-10.md) ist historisch |
| Linie B | [Forschungsrahmen v3.5](docs/linie_b/forschungsrahmen_v3_5_2026-05.md), [Richtungsnotiz v5.2](docs/linie_b/richtungsnotiz_medienkopplung_2026-09-06_v5_2.md) | v3.5 ist korrekturbedürftig; der Nachfolger v3.6 liegt nicht vor |

## Stolperstellen

- **`peak_ratio`** in Code und CSV ist das Asymmetrieverhältnis A = (F_max − M·g)/(M·g − F_min), nicht das
  Spitzen-zu-Mittel-Verhältnis Π_N der Präregistrierung vom Juni 2026.
- **Engine-Name.** Die Referenz-Engine heißt `pcmms_v3a_phasen_sweep.py`. Das Kürzel v3a bezeichnet auch den
  zurückgezogenen Simulationszyklus v3a–v3d; die Engine ist die Referenz, ihr Name wurde nur beibehalten.
- **Leitzahlen.** 5,3304 N an der Zeltspitze und rund 0,2 N je Grad Steigung gelten für den weichen
  Referenzkontakt (K = 10⁴ N/m). Sie illustrieren das Modell und sind keine Vorhersage für eine Apparatur.
- **Liftoff-Bereich.** Der Wert eines einzelnen Rasterpunkts hängt dort von der Startbedingung ab; belastbar sind
  die Spannweiten.
- **Mehrfach belegte Kennungen.** H1 bedeutet in der Präregistrierung vom Juni 2026 etwas anderes als im Entwurf
  v2. E-1 bis E-4 sind in der Notiz vom 10.11.2026 Entscheidungen, in der Notiz vom 29.10.2026 Eingänge, und E1
  bis E5 gehören zur Präregistrierung v2. R-1 bis R-5 (Referenzfälle, 10.11.) sind nicht R-1 bis R-7
  (Rückmeldungen, 29.10.). AP1 bis AP5 im Laborplan V1 sind nicht AP-01 bis AP-30 des Arbeitsplans. Kennungen
  immer mit dem Dokument nennen.
- **V1.** V1 ist die erste Apparatur, der V1-Kandidat ihr Auslegungskandidat. Bei den Laborplänen steht V1 bis V3
  für die Varianten 1 bis 3, in `rechnungen/auslegung/` V1 bis V5 für Arbeitspunktvorschläge, im
  Abgrenzungsentwurf der Linie B V-1 bis V-3 für Varianten der Linienstruktur. Klein geschrieben (v1, v2) sind
  es Dokument- und Skriptfassungen.
- **Egg-Profil.** Das „Egg“-Profil der Linie B ist nicht das der Linie A (Befund LB-14 in
  [`rechnungen/linie_b/PROTOKOLL.md`](rechnungen/linie_b/PROTOKOLL.md)).
- **Zeilenangaben** in der Abgleichnotiz vom 10.11.2026 gelten am Stand `51f79a2`, nicht am aktuellen.
- **Verweise ins Leere.** Kennungen wie „L1a-019“ oder „P1 §3“ in `rechnungen/` zeigen auf Arbeitsdokumente, die
  nicht im Repository liegen.

## Was nicht hier liegt

Messdaten gibt es nicht. Nicht im Repository liegen der Forschungsrahmen v3.6 und die Notiz „Trennungsbedingungen“
zur Linie C. Ältere Fassungen, die außerhalb kursieren, sind überholt
([`docs/overview.md`](docs/overview.md), Abschnitt „Was nicht im Repository liegt“).

---

*Reading guide (EN):* All documents are in German. An English summary closes the [README](README.md); the working
paper v2.5 contains an English abstract. Everything here is simulation output; measured data do not exist.

*Vermerk:* Erstellt am 11.11.2026, Chat-Sitzung (Claude), nach Auftrag des Autors. Pfade, Versionsstände und
Zahlen sind am Repository-Stand `d8384bc` geprüft; die Lesezeiten sind Schätzwerte. Lizenz: CC BY 4.0 wie `docs/`.
