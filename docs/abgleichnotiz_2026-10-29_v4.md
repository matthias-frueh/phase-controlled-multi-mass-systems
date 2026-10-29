# PCMMS – Abgleichnotiz 2026-10-29, v4

Projekt: Phasenkontrollierte Mehrmassensysteme (PCMMS)
Autor: Matthias Früh, ORCID 0009-0005-9984-4207
Erstellt: 29.10.2026, Chat-Sitzung (Claude), auf Wunsch des Autors („Informationen festhalten“); v2 nach der zweiten externen Rückmeldung vom selben Tag; v3 nach der dritten Rückmeldung (PR-Umfang) und der Reststellenprüfung; v4 mit den Korrekturen K-1 bis K-4 des Autors (vierte Rückmeldung), erstellt im Dokumentations-PR
Status: Notiz zum Sitzungsstand – hält eine Entscheidung (D-1) und offene Punkte fest; kein Arbeitsauftrag
Zuordnung: Projektführung; berührt AP-01, AP-04, AP-06, AP-14, AP-28, AP-29
Lizenz: CC BY 4.0 (Ordner docs/, siehe LICENSE-CC-BY-4.0)

> **Vermerk (29.10.2026).** Originaldatei `PCMMS_Abgleichnotiz_2026-10-29_v4.md`, v4 vom 29.10.2026; hier unverändert
> bis auf diesen Vermerk und die Lizenzzeile. Sitzungs- und Entscheidungsnotiz, abgelegt neben der
> [Entscheidungsvorlage vom 19.10.2026](entscheidungsvorlage_2026-10-19.md): hält die Abgrenzung der Linien A/B/C
> durch den Autor, den Abgleich mit dem Repository-Stand `8c83b07`, die Prüfung einer externen Neubewertung, vier
> Rückmeldungen (R-1 bis R-7) und die Entscheidung D-1 fest; D-2 bis D-6 sind offen und in
> [`arbeitsplan_status.md`](arbeitsplan_status.md) geführt. Die Notiz ändert keine Regel und keinen Plan. Die
> genannten Entwürfe liegen in [`konzepte/`](konzepte/README.md) und [`linie_b/`](linie_b/README.md); die
> Arbeitsübersicht Technik vom 29.10.2026, die Notiz „Trennungsbedingungen“ (Linie C, v4) und der Auftrag an Claude
> Code liegen nicht im Repository.

Zahlenherkunft wie in der Anforderungsspezifikation v0.4: [FV] Formelverzeichnis v2.8, heute im Volltext geprüft; [AÜT] Arbeitsübersicht Technik 29.10., heute gelesen; [PA] Projektablage-Dokument, heute als Auszug gelesen; [AP] übernommene Projektangabe, heute nicht neu geprüft – vor Zitat prüfen; [Ü] modellabhängiger Überschlag; [LB] Lehrbuchbeziehung.

## 0. Zweck

Hält die Präzisierungen des Autors vom 29.10.2026 („Projektausarbeitung und Weiterführung“), den Abgleich mit dem Projektstand, die Prüfung einer externen Neubewertung und die zweite externe Rückmeldung fest. Abschnitt 6 nennt die angelegten Entwürfe.

Geprüfte Grundlagen: Repo main 8c83b07 (PR #26, 22.10.) [AP], Arbeitsplan AP-01–30 (Stand 22.10.) [AP], Formelverzeichnis v2.8 (§3, §10.6–10.7, §11.1) [FV], `neuheitsgrad.md` und `PCMMS_Forschungslinie_Gegenstand_und_Vorarbeit_Frueh_korrigiert.md` (§6.8, §7) [PA], `00_UEBERSICHT_Linie_B_C.md` [PA], Evidenzmatrix P1 (L4-027 bis L4-030) [PA], `PCMMS_Arbeitsuebersicht_Technik_2026-10-29.md` (83 Arbeitspunkte, nachfolgend „AÜT-Punkt“) [AÜT].

## 1. Eingänge

- E-1 Notiz „Projektausarbeitung und Weiterführung“ (Autor, 29.10.) mit Extrakt zur Abgrenzung der Linien A/B/C.
- E-2 Leitsatz-Notiz: Man kann keine Kräfte messen, sondern nur Kräfteverschiebungen (Metrologen würden widersprechen); die alten, falschen Gleichungen dienen der Erinnerung an den Schwerpunktsatz als Basislinie zum Nullergebnis.
- E-3 Externe Neubewertung des Projekts (29.10., Quelle nicht genannt).
- E-4 Zweite externe Rückmeldung (29.10.) zu den drei Entwürfen, mit Präzisierungen des Autors (Abschnitt 7).

## 2. Präzisierungen des Autors (29.10.2026)

- P-1 Neuheitsanspruch: eine spezielle Konstruktionsform für den Bewegungsablauf der inneren Massen (N ≥ 3, Konstellation je Modul); der menschliche Arm dual-robotisch nachgebildet, um gehaltene Massen bzw. das Massezentrum gezielt anzusteuern; Bewegungsprofile ermitteln und optimieren; Maximallasten, Grenzwerte, Trennungsbedingungen und Messungen im kleinsten Bereich. Keine neue Kraftwirkung; Rahmen bleibt klassische Mechanik einschließlich Auftrieb.
- P-2 Linie A: ohne Helium oder andere Gase; Messung und ruhender Körper.
- P-3 Linie B: z. B. sechs Arme (zwei je Masse), Prototyp in einer speziell konstruierten Heliumhülle, um in der jeweiligen Atmosphäre leichter zu sein, grenznah zum Abhebepunkt; Abstand zum Abhebepunkt variabel darunter, knapp darüber oder nahe dran („unterschiedliche Blickwinkel“). Im Extrakt wird B als eigentlicher konstruktiver und experimenteller Kern bezeichnet.
- P-4 Linie C: Trennungsbedingungen, energetische Verteilung, umfangreichere Messungen.
- P-5 Repo: frühe Simulations- und Dokumentationsbasis, noch nicht weit ausgearbeitet.
- P-6 Selbstbeschreibung der Forschungsfelder: experimentelle Physik, experimentelle Dynamik, Grenzforschung, teilweise Primärforschung, Messarchitekturen im PCMMS-Kontext, Laborplanung.

## 3. Abgleich mit dem Projektstand

- A-1 Leitsatz (E-2): deckt sich mit dem fachlichen Leitsatz vom 01.10.2026 und der Ausrichtung seit September (Schwerpunktsatz als Baseline, Kraftverschiebungen als primäre Observablen). Metrologisch verträgliche Fassung für externe Dokumente: Die Messkette wird absolut rückgeführt (Kalibrierung) nur für die Kontrollgröße ΔF̄_Zustand; das Zielsignal sind Verschiebungen innerhalb der Wellenform (F_min − ⟨N⟩, Harmonische 1–3). Formelverzeichnis Gl. (6) [FV]: ⟨F_c⟩ = Mg − ⟨F_ext,z⟩ + b_w.
- A-2 Neuheitsanspruch (P-1) – Korrektur zur Chat-Aussage vom 29.10. („deckt sich mit dem Literaturabgleich“): `neuheitsgrad.md` §7.1 und das Vorarbeit-Dokument §7.1 [PA] führen „mehr als zwei innere Massen, Phasendifferenz als Steuerparameter“ und „asymmetrische Bahnform als Optimierungsdimension“ ausdrücklich als besetzt; beansprucht wird allein die Wellenformstatistik der unilateralen Kontaktkraft als entworfene Zielgröße (§7.2). Eine Formulierung „Neuheit = N ≥ 3 mit optimierten Profilen“ widerspräche dem eigenen Neuheitsgrad-Dokument. Tragfähig ist nur: eine spezifische Konstruktions- und Führungsform (dual, armähnlich, Massezentrum als Sollgröße) im Dienst dieser Zielgröße – als Ingenieurbeitrag, nicht als Prinzipneuheit. Bimanuale/duale Manipulation ist in der Robotik ein eigenes Feld; vor jeder externen Verwendung Literatur prüfen (AÜT-Punkt 57).
- A-3 Antrieb: Die Dual-Armführung ist eine Ausprägung der Option „programmierbarer Aktor“ (AP-01, AÜT-Punkt 03). Sie passt zum Simulationsbefund, dass asymmetrische Profile zwingend sind (Sinus kollabiert auf R = |1 + e^{iφ₂} + e^{iφ₃}|, γ₁ = 0 ohne Liftoff [AP]) und zur Egg-Definition mit aktiv geführter Rückholung (Formelverzeichnis §10.6 [FV]). AP-01 bleibt formal offen.
- A-4 Rolle der Robotik: Das Anschlusspapier Robotik (Evidenzmatrix L4-027/028 [PA]) führt Robotik als nachgelagerte Vergleichs- und Validierungsebene und schließt den umgekehrten Weg (Dynamik aus einem Manipulator ableiten) aus; AÜT-Punkt 65 setzt die robotische Validierung auf „nach V1“. Die Armführung vom 29.10. gibt der Robotik eine zweite Rolle: Aktorik der Ebene L2. Kein Widerspruch zur Reihenfolge Baustein 14 → L3 → Vergleich, solange beide Rollen getrennt geführt werden; das Anschlusspapier wäre um die Aktorik-Rolle zu ergänzen.
- A-5 Linie B: Zwei Definitionen stehen nebeneinander. Forschungsrahmen v3.5 / Richtungsnotiz v5.2 [PA, FV §11.1]: äußere Medienkopplung – Relativgeschwindigkeit zum Medium, Widerstandsgesetz, stationäre Drift und gebundene mittlere Reaktionskraft getrennt; Modelle A (vorgegebene Trägerbewegung, F̄_A), B (freie Drift, F̄_B = 0), C (aufgehängt, F̄_C = k⟨x⟩); Dichteabhängigkeit modellabhängig; Ballon-Demonstrator = austarierter Heliumballon, vertikale Drift, keine Messdaten. Abgrenzung 29.10.: grenznahe Kontaktdynamik unter Auftriebshilfe mit Armführung. Gemeinsame Plattform (Helium, nahe am Abhebepunkt), verschiedene Zielgrößen (Drift bzw. gebundene Kraft gegenüber Wellenform und Kontaktverlust). Festlegung für v3.6 (AP-28, AÜT-Punkte 66–73). Entwurf: Abschnitt 6.
- A-6 Physik-Flag zur Auftriebshilfe: Mit Hülle gilt ⟨F_c⟩ = Mg − F_auf − ⟨F_med,z⟩ (Symbol F_auf für den Auftrieb ist neu; F̄_A ist im Projekt belegt). Der Driftmechanismus von F_auf hängt vom Hüllentyp ab [LB] (Präzisierung v3): bei volumenfester, gespannter Hülle folgt F_auf der Umgebungsluftdichte (ideale Gasgleichung: ≈ 0,35 %/K bei 293 K, ≈ 1 %/10 hPa bei 1013 hPa); bei freier, nicht gespannter Hülle gleicht sich der Innendruck an, die verdrängte Luftmasse bleibt in erster Näherung n_He·M_Luft, Umgebungsdruck und -temperatur heben sich auf, und maßgeblich sind die Temperaturdifferenz Füllgas–Umgebungsluft (≈ 0,34 % der verdrängten Luftlast je Kelvin), die Feuchte und die Permeation; Eigenwärme der Antriebe erzeugt dann eine betriebskorrelierte Drift; der Leerlauf-Modus ist dafür eine Gegenprobe, deren thermische Vergleichbarkeit nachzuweisen ist (K-4). Überschlag [Ü] mit den Annahmen M ≈ 0,65 kg (V1-Kandidat [FV]), ρ_Luft ≈ 1,20 kg/m³, ρ_He ≈ 0,17 kg/m³, 20 °C: V ≈ 0,6–0,7 m³ ohne Hüllenmasse, verdrängte Luft ≈ 7–8 N, Drift ≈ 0,03 N je Kelvin; bei 5 % Restlast (≈ 0,3 N) knapp 10 % je Kelvin. Zusätzlich: zugesetzte Luftmasse der Hülle (Kugel: ½·ρ_Luft·V [LB] ≈ 0,4 kg [Ü]) in der Größenordnung von M – die Massenkonvention (AÜT-Punkt 22) und das Linie-A-Modell tragen nicht unverändert; andere Hüllenformen liegen anders, die Aussage ist die Größenordnung. Konsequenz: F_auf mitmessen (Referenzwägung, Dichtekompensation), Restlast als Stellgröße führen, zugesetzte Luftmasse für die reale Geometrie bestimmen (AÜT-Punkt 32).
- A-7 Linie C: P-4 deckt sich mit der C-Notiz (zuletzt v4 laut Arbeitsübersicht Technik [AÜT]) und Formelverzeichnis §11.1 [FV] (Umlenkung oder Abspaltung außerhalb der Systemgrenze; bei Medium als Träger setzt C die Klärung von B voraus). AP-29 bleibt geparkt. Wortbedeutung „Trennung“: Kontaktverlust (Liftoff) in A/B gegenüber Abspaltung in C – nicht vermischen (AÜT-Punkt 75).
- A-8 Repo/Konzepte: Robotik, Lageregelung und Ringstruktur liegen seit PR #25/#26 als Konzeptpapiere mit Vermerk in docs/konzepte/ – angelegt, nicht ausgearbeitet, nicht gerechnet (Recheck RC-211 [PA]). P-5 ist damit zutreffend.
- A-9 Kopfzeile: ORCID stimmt. Schreibweise „experimentelle“, falls P-6 für Profil oder ORCID gedacht ist.

## 4. Prüfung der externen Neubewertung (E-3)

Tragfähig: Einordnung (klassische Mechanik einschließlich Auftrieb; Beitrag in Konstruktion, Steuerung und grenznaher Messmethodik; kein Paradigmenwechsel), Stärkenliste, Bewertungstabelle.

Korrekturen:
- K-1 Tor: Die Bewertung macht Linie B zum Entscheidungspunkt. Im Arbeitsplan liegt B in Stufe S5 (geparkt); die ersten Messdaten kommen nach Plan aus Linie A (Phase 0/1 nach Präreg v2). Mit D-1 (Abschnitt 5) bleibt das so: Stufenfolge unverändert, B2 als langfristige Randbedingung.
- K-2 Maßstab: „Gebaut und gemessen“ ignoriert die fixierte Projektphase (Vorbereitung ohne Experimente bis zur Anbindung; V1 bewusst nicht gebaut). Maßstab für den jetzigen Stand ist Messreife: Präreg eingefroren (AP-14), Antrieb festgelegt (AP-01), Messkette und Kalibrierablauf (AP-06, AÜT-Punkte 14–20), Sensor Modulkinematik (AP-07). „Reifegrad niedrig“ ist daran gemessen korrekt, aber aus anderem Grund: S1 ist nicht abgeschlossen.
- K-3 Dokumentation: „gut“ gilt für main. Nach außen wirken zuerst die 17 Zenodo-Altstände ohne Superseded-Hinweis, einschließlich der zurückgezogenen Mittelkraftlinie (AP-17/AP-30) [AP].
- K-4 Trennschärfe: Die Bewertung übernimmt die B-Definition vom 29.10.; der gültige Forschungsrahmen v3.5 definiert B anders (A-5). Erst v3.6 löst das auf.
- K-5 Risiken B: benannt, aber ohne Größenordnung; der harte Punkt ist die Drift von F_auf relativ zur Restlast und die zugesetzte Luftmasse (A-6), nicht „Strömung“ allgemein.

## 5. Entscheidungen und offene Punkte (nur geführt, kein Entwicklungsauftrag)

- D-1 entschieden (Autor, 29.10.2026): Die Stufenfolge des Arbeitsplans bleibt. B2 wird als langfristige Randbedingung für AP-01, AP-04 und AP-06 berücksichtigt – das heißt zunächst: Erweiterbarkeit prüfen und Folgen dokumentieren. Es verpflichtet V1 weder zur Armführung noch zu gemeinsamer Hardware. Fernziel und nächster Arbeitsschritt sind getrennte Festlegungen; ihre einzige Kopplung ist die Erweiterbarkeit der S1-Entscheidungen. Beantwortet F-2 des Abgrenzungsentwurfs (dort bei der nächsten Fassung nachzuführen).
- D-2 offen: B-Definition in v3.6 – Umwidmung, Ergänzung (B1/B2) oder Übergabe des Grenznähe-Teils an C. Die B1/B2-Aufteilung bleibt Vorschlag; ihre Annahme erfolgt nicht stillschweigend durch redaktionelle Überarbeitungen, sondern nur durch ausdrückliche Festlegung des Autors.
- D-3 offen: Neuheitsformulierung (A-2) – Ingenieurbeitrag ohne Prinzipneuheit oder Ergänzung von `neuheitsgrad.md` um die Konstruktionsform.
- D-4 offen: Rolle der Robotik (A-4) – Aktorik-Rolle im Anschlusspapier ergänzen oder als eigenes Konzeptpapier führen.
- D-5 offen: Armführung bereits als Antrieb in Linie A (AP-01) oder erst in B. Nach D-1 besteht keine Verpflichtung; zu prüfen ist die Erweiterbarkeit (Anforderungsspezifikation O-2).
- D-6 offen: Messkonzept für F_auf (Referenzwägung, Dichtekompensation, beides) – gehört zu AP-06; erst nach D-2.

## 6. Angelegte Entwürfe (29.10.2026)

- `PCMMS_Anforderungsspezifikation_Dual-Armfuehrung_v0_4_2026-10-29.md` – Anforderungen AF-01 bis AF-32, offene Fragen O-1 bis O-14, Zahlenherkunft gekennzeichnet; ersetzt v0.3 bis v0.1.
- `PCMMS_Linie_B_Abgrenzung_v3_6_Entwurf3_2026-10-29.md` (Entwurf 3) – Gegenüberstellung, Varianten V-1 bis V-3 mit Vorschlag V-2, Kurzformel, messtechnische Folgen, Änderungsliste gegenüber v3.5; F-2 durch D-1 beantwortet; ersetzt Entwurf 2 und 1.
- `ANWEISUNG_Claude_Code_2026-10-29_Dokumentations-PR.md` (v2) – Auftrag für den Dokumentations-PR (Abschnitt 8).

Ablage im Repo mit dem Dokumentations-PR vom 29.10.; nicht in der Projektablage (Ablage über der Maximalgröße, Schreibversuch am 29.10. abgewiesen).

## 7. Zweite externe Rückmeldung (E-4) und Einarbeitung

- R-1 D-1: kein zwingender Gegensatz zwischen Fernziel und Stufenfolge; getrennte Festlegungen. Übernommen mit der Präzisierung des Autors (Abschnitt 5, D-1) und in v0.2 (Abschnitt 1, Abschnitt 4, O-2).
- R-2 AF-06: geschlossene Schleife ist Konsequenz des Konzepts, aber nicht gleich statische Überbestimmung; Freiheitsgrade, Gelenke, Nachgiebigkeit, Lastaufteilung bleiben auszulegen. Übernommen (v0.2 AF-06 bedingt, O-6).
- R-3 AF-07: „keine Horizontalbewegung“ zu streng; gefordert ist, dass unerwünschte Querkräfte und Kippmomente innerhalb festgelegter, messtechnisch überprüfter Grenzen bleiben; Konstruktionsweg offen. Übernommen (v0.2 AF-07, O-13).
- R-4 Zahlenherkunft: direkt geprüfte Werte, übernommene Projektangaben und modellabhängige Überschläge unterscheiden. Übernommen (Kennzeichnung [FV]/[AÜT]/[PA]/[AP]/[Ü]/[LB] in beiden Dokumenten).
- R-5 B1/B2 bleibt Vorschlag; keine stillschweigende Annahme durch redaktionelle Überarbeitung. Übernommen (D-2; v0.2 Abschnitt 1 und 4).
- Zur Kenntnis: Die Rückmeldung korrigiert ihr eigenes früheres Dokument bei Linie C (Kontaktverlust in A/B2 gegenüber Umlenkung/Abspaltung in C) – deckt sich mit A-7. Die Rückmeldung hat Repo-Befunde und Zahlen aus den Entwürfen übernommen, nicht unabhängig geprüft; daher die Kennzeichnung nach R-4.
- R-6 (dritte Rückmeldung, PR-Umfang): Dokumentations-PR mit Claude Code in fünf Schritten (Ist-Abgleich; Aufnahme von Spezifikation und Abgleichnotiz; Abgrenzungsentwurf mit Verweis auf D-1; AP-01/04/06 knapp ergänzen; Index und Querverweise, prüfbarer PR); vorher fachliche Reststellen prüfen – genannt: verbliebener Satz zu horizontalen Freiheitsgraden in AF-07, Bilanzformulierungen, Hüllenüberschläge. Übernommen als ANWEISUNG (Abschnitt 8); das frühere externe Entwicklungsdokument (Abgrenzungs-Extrakt) kommt erst nach Korrektur seiner Linie-C-Abgrenzung in Frage.

Ergebnis der Reststellenprüfung (29.10., vor dem PR):
- AF-07: Satz entfernt; Freiheitsgrade bleiben Teil der Kinematikauslegung (v0.3).
- Bilanzen (berichtigt in v4): Liftoff-Bedingung S_true ≤ −W_R + F_med,z + F_par aus Gl. 4 [FV] stimmt. Die Fesselbilanz in v0.3 war falsch – vor ⟨F_med,z⟩ stand ein Minus; richtig ist ⟨F_F⟩ = F_auf − M·g + ⟨F_med,z⟩ (K-1, vom Autor erkannt). Der Vermerk „Bilanzen geprüft und stimmen“ aus v3 war damit nicht haltbar; die Prüfung galt nur für die Liftoff-Bedingung.
- Hüllenüberschlag: Mechanismus war in v0.2 nur für die gespannte Hülle richtig; bei freier Hülle heben sich Umgebungsdruck und -temperatur auf, Treiber ist die Gas–Luft-Temperaturdifferenz (A-6 und v0.3 AF-29 korrigiert, O-14 neu). Größenordnung (≈ 0,03 N je Kelvin, zugesetzte Luftmasse ≈ 0,4 kg) unverändert; Volumen auf 0,6–0,7 m³ präzisiert.

- R-7 (vierte Rückmeldung, Prüfung der vier Dateien durch den Autor): PR-Umfang passt; vier Korrekturen, eingearbeitet als K-1 bis K-4: K-1 AF-30 Vorzeichen der Fesselkraft (M·z̈_S = F_auf + F_med,z − M·g − F_F, also ⟨F_F⟩ = F_auf − M·g + ⟨F_med,z⟩); K-2 AF-21 Nulltest vollständig (F_c − ⟨F_c⟩ = (S_true − ⟨S_true⟩) − (F_ext,z − ⟨F_ext,z⟩), Bedingung an zeitveränderliche äußere Kräfte); K-3 AF-30/M-4 Regimewechsel zulassen (Konfiguration je Lauf eindeutig, Wechsel des Kontaktzustands erkennen und getrennt auswerten; w_R bestimmt den momentanen Kontaktzustand nicht); K-4 AF-29 Leerlauf als Gegenprobe, thermische Vergleichbarkeit nachzuweisen. Ausführungsregeln: benannte Korrekturen nachvollziehbar einarbeiten und im Änderungslog ausweisen; weitere Befunde melden; [AP✓] nur bei passender Fundstelle; Dokumentations- und Linkprüfung reichen; ein gebündelter PR, B1/B2 Vorschlag, Merge durch den Autor; keine weitere komplette Dokumentenrunde vor dem Start.

## 8. Dokumentations-PR (29.10.2026)

Ausführung: direkt in Claude Code am 29.10.2026 nach Auftrag v2; Korrekturen K-1 bis K-4 vorab in v0.4, Entwurf 3 und diese v4 eingearbeitet.

Umfang nach R-6 und Abgleich mit dem Repo-Stand: Spezifikation v0.3 → docs/konzepte/; Abgrenzungsentwurf 2 → docs/linie_b/; Abgleichnotiz v3 → docs/ neben der Entscheidungsvorlage vom 19.10.; C-Notiz v4, falls noch nicht im Repo; arbeitsplan_status.md um D-1 (AP-01/04/06) und D-2 bis D-6 ergänzt; Querverweise in overview und konzepte/README; FV-Offene-Punkte um O-11. Vor der Ablage prüft Claude Code die [AP]-Angaben gegen docs/arbeitspapier und den Volltext von docs/konzepte/ (O-1). Keine Linienentscheidung; B1/B2 bleibt Vorschlag; Arbeitsübersicht Technik nur auf ausdrücklichen Wunsch. Auftrag: `ANWEISUNG_Claude_Code_2026-10-29_Dokumentations-PR.md`.

## Änderungslog

- v4 (29.10.2026, im Dokumentations-PR): R-7 mit K-1 bis K-4 in Abschnitt 7; Prüfvermerk zu den Bilanzen berichtigt (Fesselbilanz war falsch); A-6 Leerlauf als Gegenprobe; Abschnitt 6 und 8 auf v0.4, Entwurf 3, Auftrag v2 und Ausführung.
- v3 (29.10.2026): R-6 und Reststellenprüfung in Abschnitt 7; A-6 Driftmechanismus nach Hüllentyp korrigiert; Abschnitt 6 auf v0.3, Entwurf 2 und ANWEISUNG; Abschnitt 8 neu.
- v2 (29.10.2026): Abschnitt 7 neu (zweite Rückmeldung R-1 bis R-5); D-1 als Entscheidung des Autors gefasst, D-2 mit Vorbehalt gegen stillschweigende Annahme; K-1 nachgeführt; Zahlenherkunft gekennzeichnet; Abschnitt 6 auf v0.2 und Ablageort korrigiert.
- v1 (29.10.2026): erstellt; Abschnitt 6 (Ablageort) einmal korrigiert.
