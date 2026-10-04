# Konzepte zu Laboraufbau, Messtechnik und Steuerung

Stand: 4. Oktober 2026. Lizenz dieses Ordners: CC BY 4.0, siehe [`../../LICENSE-CC-BY-4.0`](../../LICENSE-CC-BY-4.0). Namensnennung: „Matthias Früh, PCMMS“, https://github.com/matthias-frueh/phase-controlled-multi-mass-systems

Dieser Ordner enthält die vorhandenen Konzeptdokumente des Projekts zu Laboraufbau, Messtechnik und Steuerung.
Alle Dokumente sind **Konzepte**: Entwürfe aus dem Jahr 2026, nicht umgesetzt, nicht an Hardware geprüft; es gibt
keine Messdaten. Maßgeblich für Hypothesen, Entscheidungsregeln und Auslegung sind die
[Präregistrierung v2](../praeregistrierung_v2_entwurf.md) (Entwicklungsversion) und die Werkzeuge in
[`../../code/`](../../code/); wo ein Konzept davon abweicht oder überholt ist, steht das im Vermerk am Kopf des
Dokuments. Die Texte selbst sind bis auf Querverweise und die Kontaktzeile unverändert.

| Datei | Inhalt | Stand | Arbeitspaket | Status |
|---|---|---|---|---|
| [`laborplan_v1_2026-05.md`](laborplan_v1_2026-05.md) | Laborplan Variante 1 (kostengünstig): Messprinzip, mechanischer Aufbau, Aktuatorik, Kraftmessung, Kontrollen, Messablauf, Stückliste | Mai 2026 | AP-01, AP-04, AP-05, AP-06 | Konzept; Parameter, Antrieb, Messgrößen und Sicherheit durch Auslegungswerkzeug, Präregistrierung v2 und Arbeitsplan in Teilen überholt (Vermerk) |
| [`messtechnik_anschluss_v2_2026-09.md`](messtechnik_anschluss_v2_2026-09.md) | Mess- und Prüfrahmen: Status, zentrale Aussagen, geplanter Prüfstand, gesuchte Anbindung | 1. September 2026 | AP-06, AP-18 | Konzept; eine Aussage zurückgezogen, eine Zahl als Artefakt erkannt (Vermerk) |
| [`mehrkanal_messarchitektur_2026-05.md`](mehrkanal_messarchitektur_2026-05.md) | Konzeptbaustein Mehrkanal-Messarchitektur: Kraft-, Weg-, Referenz- und Rahmenkanal, Synchronisation, Verarbeitungskette, Detektionsstrategien | Mai 2026 | AP-06, AP-10 | Konzept; im Rahmen der zurückgezogenen Kernhypothese v3 entstanden, Architektur davon unabhängig; Driftabzug und Residuumslogik abweichend von der Präregistrierung v2 (Vermerk) |

Steuerungssoftware: Die vorhandenen Firmware-Muster (ESP32) der Demonstratoren und Tischtests liegen in
[`../../code/firmware/`](../../code/firmware/) mit eigener README.

**Nicht vorhanden.** Ein eigenständiges Sicherheitskonzept (AP-05) liegt nicht vor; sicherheitsrelevante Bausteine
stehen in der Präregistrierung v2 (Gültigkeits- und Abbruchregeln, §9.1 und §9.2), in
[`../einzugsgebiete_v1_kandidat.md`](../einzugsgebiete_v1_kandidat.md) (Hüpfzustände, Stoßspitzen) und im Laborplan
V1, Abschnitt 10 (harter Stopp). Für die Werkzeuge 3 bis 7 der Präregistrierung v2 (Aufnahme, Anpassverfahren,
Pilotskript, Auswertung, Randomisierung und Monitor) gibt es keine Konzeptdokumente; ihr Pflichtenheft steht in
§12 der Präregistrierung v2 und im Arbeitsplan (AP-10 bis AP-12). Den Plan für Werkzeug 8 enthält
[`../plan_ap13_pipelinetest.md`](../plan_ap13_pipelinetest.md).

Bearbeitungsstand aller Arbeitspakete: [`../arbeitsplan_status.md`](../arbeitsplan_status.md).
