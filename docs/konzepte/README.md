# Konzepte zu Laboraufbau, Messtechnik und Steuerung

Stand: 4. Oktober 2026, Nachträge 11. Oktober 2026 und 22. Oktober 2026. Lizenz dieses Ordners: CC BY 4.0, siehe [`../../LICENSE-CC-BY-4.0`](../../LICENSE-CC-BY-4.0). Namensnennung: „Matthias Früh, PCMMS“, https://github.com/matthias-frueh/phase-controlled-multi-mass-systems

Dieser Ordner enthält die vorhandenen Konzeptdokumente des Projekts zu Laboraufbau, Messtechnik und Steuerung,
dazu die Demonstrator-Unterlagen der Linie B (Mai 2026), Anwendungs- und Anschlusspapiere (Lageregelung, Robotik)
und eine Notiz zu Linie C.
Alle Dokumente sind **Konzepte**: Entwürfe aus dem Jahr 2026, nicht umgesetzt, nicht an Hardware geprüft; es gibt
keine Messdaten. Maßgeblich für Hypothesen, Entscheidungsregeln und Auslegung sind die
[Präregistrierung v2](../praeregistrierung_v2_entwurf.md) (Entwicklungsversion) und die Werkzeuge in
[`../../code/`](../../code/); wo ein Konzept davon abweicht oder überholt ist, steht das im Vermerk am Kopf des
Dokuments. Für die Linie-B-Unterlagen gelten statt der Präregistrierung v2 die Kontrollrechnungen in
[`../../rechnungen/linie_b/`](../../rechnungen/linie_b/PROTOKOLL.md) und die Dokumente in
[`../linie_b/`](../linie_b/README.md). Die Texte selbst sind bis auf Querverweise und die Kontaktzeile unverändert,
die am 22. Oktober 2026 übernommenen bis auf den Vermerk. Das Konzept zum Sechs-Nadel-Messrahmen (Oktober 2026) ist
neu ausgearbeitet; sein Vermerk nennt Grundlage und Status.

| Datei | Inhalt | Stand | Arbeitspaket | Status |
|---|---|---|---|---|
| [`laborplan_v1_2026-05.md`](laborplan_v1_2026-05.md) | Laborplan Variante 1 (kostengünstig): Messprinzip, mechanischer Aufbau, Aktuatorik, Kraftmessung, Kontrollen, Messablauf, Stückliste | Mai 2026 | AP-01, AP-04, AP-05, AP-06 | Konzept; Parameter, Antrieb, Messgrößen und Sicherheit durch Auslegungswerkzeug, Präregistrierung v2 und Arbeitsplan in Teilen überholt (Vermerk) |
| [`messtechnik_anschluss_v2_2026-09.md`](messtechnik_anschluss_v2_2026-09.md) | Mess- und Prüfrahmen: Status, zentrale Aussagen, geplanter Prüfstand, gesuchte Anbindung | 1. September 2026 | AP-06, AP-18 | Konzept; eine Aussage zurückgezogen, eine Zahl als Artefakt erkannt (Vermerk) |
| [`mehrkanal_messarchitektur_2026-05.md`](mehrkanal_messarchitektur_2026-05.md) | Konzeptbaustein Mehrkanal-Messarchitektur: Kraft-, Weg-, Referenz- und Rahmenkanal, Synchronisation, Verarbeitungskette, Detektionsstrategien | Mai 2026 | AP-06, AP-10 | Konzept; im Rahmen der zurückgezogenen Kernhypothese v3 entstanden, Architektur davon unabhängig; Driftabzug und Residuumslogik abweichend von der Präregistrierung v2 (Vermerk) |
| [`nadelrahmen_dreimassenkoerper_2026-10.md`](nadelrahmen_dreimassenkoerper_2026-10.md) | Sechs-Nadel-Messrahmen (Nord, Süd, Ost, West, oben, unten) mit eingebettetem Dreimassenkörper: Begriffe und Lastbilanz, Nadelregel, ausgearbeitete Varianten kinematisch (B) und eingespannt (C), Formschluss im Modell, Vollmodell-Vorhersagen, Rahmendynamik, Änderungen gegenüber der Einzelauflage, Kalibrierrang, Kanalplan | 11. Oktober 2026 | AP-27 (mit AP-04, AP-06) | Konzept- und Modellarbeit; Rechnungen in [`../../rechnungen/nadelrahmen/`](../../rechnungen/nadelrahmen/PROTOKOLL.md) (Simulation, Analytik); kinematische Lagerung und Einspannung als anwendungsabhängige Möglichkeiten offen, keine Bauentscheidung |
| [`demonstrator_ballon_2026-05.md`](demonstrator_ballon_2026-05.md) | Ballon-Demonstrator der Linie B: falsifizierbare Hypothese einer phasenabhängigen vertikalen Netto-Drift eines austarierten Heliumballons, Mechanismus, Minimalaufbau, Steuerung, Messung und Auswertung, Abgrenzung | Mai 2026 | AP-28 (Linie B, Stufe S5) | Konzept der Linie B; keine Messdaten; Dichteaussage (Befund 3) durch die Linie-B-Kontrollrechnungen eingeschränkt, Kraftmodell bei kleiner KC-Zahl offen; der Tischtest-Sketch stellt nur die Phase der PWM-Hüllkurve ein, kein Sketch erzeugt das Egg-Profil (Vermerk) |
| [`demonstrator_begleitbericht_2026-05.md`](demonstrator_begleitbericht_2026-05.md) | Technischer Begleitbericht zum Ballon-Demonstrator: Bauteilliste, Schaltung, ESP32-Code für den Phasenzyklus zweier Vibrationsmotoren | Mai 2026 | AP-28 (Linie B, Stufe S5); Firmware-Muster bei AP-01 | Konzept; Code als [`pcmms_phasen_automatik.ino`](../../code/firmware/pcmms_phasen_automatik.ino) im Repository, nur Phase der PWM-Hüllkurve, kein Egg-Profil; Preise sind Schätzungen von Mai 2026 (Vermerk) |
| [`demonstrator_pendeltest_horizontal_2026-05.md`](demonstrator_pendeltest_horizontal_2026-05.md) | Protokollentwurf Pendeltest der horizontalen Drift („Strang b“): Messprinzip, Aufbauvarianten (bifilares Pendel, Torsionspendel, Luftkissenbahn), Kontrollen, Messablauf, Auswertung, Protokolltabellen | Mai 2026 | AP-28 (Linie B, Stufe S5) | Entwurf; Tabellen nicht ausgefüllt, keine Messung; Gesamtprojektanalyse: „parken“, Tracker zu grob; Ausgabe des Trackers in [`../../code/demonstrator/`](../../code/demonstrator/README.md) passt nicht zum Protokollformat (Vermerk) |
| [`ringstruktur_mehrkanal_inversion_2026.md`](ringstruktur_mehrkanal_inversion_2026.md) | Internes Arbeitspapier Ringstruktur und Mehrkanal-Inversion: Vorwärtsmodell F = Mg + S + C, Messkanäle als Projektionen, Inversionsstrategie und Trennung von S und C, Detektionsschwelle, numerischer Testplan T-A bis T-E | 2026 | AP-27 (mit AP-09) | internes lebendes Arbeitspapier; Tests nicht gerechnet; Zerlegung von C und Residuum gegen ein Vorwärtsmodell durch Formelverzeichnis v2.8 und Präregistrierung v2 eingeschränkt (Vermerk) |
| [`anwendungsstrang_lageregelung_2026-06.md`](anwendungsstrang_lageregelung_2026-06.md) | Anwendungsstrang Lageregelung (Reaktionsrad-Prinzip): Quaternion-Regelung mit Sättigung, Grenze der Drehimpulsumverteilung, Einordnung neben Fluid-Schub und Interface-Statistik, Andockpunkte | 14. Juni 2026 | AP-27 | Anwendungsdokument; keine Lageregelung mit PCMMS-Modulen ausgeführt; Simulationsskript nicht im Repository; Aussage zum Fluid-Schub durch die Linie-B-Kontrollrechnungen eingeschränkt (Vermerk) |
| [`anschlusspapier_robotik_2026.md`](anschlusspapier_robotik_2026.md) | Anschlusspapier Robotik: Kausalrichtung, Ebenen L0–L3, Beiträge eines robotischen Labors, Vorbehalt zum Momentenkanal, Untersuchungsfragen, Reihenfolge der Stufen | 2026 | AP-27 | Anschlussdokument ohne ausgeführte Regelung oder robotische Validierung; Bausteine 13 und 14 nicht im Repository, Abtastrate des Kraftkanals und Bezug auf Kernhypothese v3 überholt (Vermerk) |
| [`linie_c_energiebilanz_modellvergleich_2026-09-05.md`](linie_c_energiebilanz_modellvergleich_2026-09-05.md) | Ergänzende Notiz zur energetischen Erweiterung (Linie C): Energiebilanz ohne Doppelzählung, phasenabhängige Energie bei linearer Dynamik, Verteilung und Ertrag, Referenzfälle, zwei Federspeicher als Pilotvariante, nächste Aufgabe | 5. September 2026 | AP-29 | AP-29 geparkt; methodische Notiz ohne Simulation, Empfängerwahl oder Messung; Linie C im Formelverzeichnis v2.8 neu gefasst (Vermerk) |

Steuerungssoftware: Die vorhandenen Firmware-Muster (ESP32) der Demonstratoren und Tischtests liegen in
[`../../code/firmware/`](../../code/firmware/) mit eigener README. Die Tracking- und Auswerteskripte des
Demonstrators der Linie B (Video → Höhen-CSV → Drift) liegen, nicht getestet, in
[`../../code/demonstrator/`](../../code/demonstrator/README.md); mit ihnen wurden keine Messdaten erzeugt.

**Nicht vorhanden.** Ein eigenständiges Sicherheitskonzept (AP-05) liegt nicht vor; sicherheitsrelevante Bausteine
stehen in der Präregistrierung v2 (Gültigkeits- und Abbruchregeln, §9.1 und §9.2), in
[`../einzugsgebiete_v1_kandidat.md`](../einzugsgebiete_v1_kandidat.md) (Hüpfzustände, Stoßspitzen) und im Laborplan
V1, Abschnitt 10 (harter Stopp). Für die Werkzeuge 3 bis 7 der Präregistrierung v2 (Aufnahme, Anpassverfahren,
Pilotskript, Auswertung, Randomisierung und Monitor) gibt es keine Konzeptdokumente; ihr Pflichtenheft steht in
§12 der Präregistrierung v2 und im Arbeitsplan (AP-10 bis AP-12). Den Plan für Werkzeug 8 enthält
[`../plan_ap13_pipelinetest.md`](../plan_ap13_pipelinetest.md).

Bearbeitungsstand aller Arbeitspakete: [`../arbeitsplan_status.md`](../arbeitsplan_status.md).
