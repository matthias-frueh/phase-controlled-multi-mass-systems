# Phasengekoppelte Mehrmassen-Oszillatoren — ein unabhängig entwickelter Mess- und Prüfrahmen

*Zeitaufgelöste Charakterisierung dynamischer Auflagekräfte: Simulationsrahmen, Präregistrierung und geplanter Prüfstand. Status: prä-experimentell — Kooperationsgesuch.*

> **Vermerk zur Übernahme (04.10.2026).** Konzept des Autors vom 1. September 2026 (Fassung v2), geschrieben als
> Kurzdarstellung des Mess- und Prüfrahmens für die gesuchte wissenschaftliche Anbindung. Hier unverändert bis auf die
> Kontaktzeile am Ende (nur ORCID). Nicht umgesetzt; es liegt keine eigene Messung vor. Seit dem 1. September 2026
> überholt:
> - **Zurückgezogen:** Die Aussage, negative Schiefe trete nur bei echter Mehrmodul-Dephasierung auf (allgemeine
>   Vorzeichenregel der Schiefe), ist mit dem Arbeitspapier v2.4 (Abschnitt 4.8) und der Präregistrierung v2 (§1)
>   zurückgezogen; positive Referenzfälle behalten ihren begrenzten Geltungsbereich (Simulation, weicher Referenzkontakt).
> - **Artefakt:** Der „Konvergenztest −43,5 mN bei 10 s → −0,5 mN bei 110 s“ betrifft den Punkt (0°, 208,4°); der
>   Wert ist ein Artefakt der Festschritt-Integration, ereignisgenau beträgt die Abweichung +0,02 mN
>   ([`../../data/README.md`](../../data/README.md), [`../../code/ereignisloeser.py`](../../code/ereignisloeser.py)).
> - **Literaturangaben:** Die 15-%-Angabe zu Perret-Liaudet & Rigaud ist ungeprüft (Arbeitspapier, Offene Punkte
>   Nr. 42); Wakou, Ochiai & Isobe 2008 ist im Literaturverzeichnis des Arbeitspapiers geführt (`wakou2008`).
> - **Prüfstand und Kosten:** „AP1, Sachkosten ≈ 10.000 €“ ist die Planung dieses Konzepts. Antrieb, Geometrie,
>   Kontakt, Nennlast und Messkette sind offen (Arbeitsplan AP-01, AP-04 bis AP-06,
>   [`../arbeitsplan_status.md`](../arbeitsplan_status.md)); Kosten sind dort nicht geschätzt.
> - **Messgrößen und Regeln:** Primäre Größen, Entscheidungsregeln und Kontrollen stehen in der Präregistrierung v2
>   (Entwicklungsversion), nicht mehr in der Präregistrierung vom Juni 2026 („Stop / Modify / Scale“, Block-Averaging).
>   „Spitzen-zu-Mittel-Verhältnis“ und Asymmetrieverhältnis sind verschiedene Größen ([`../overview.md`](../overview.md)).
> - **Vorhandenes:** „Steuerungs- und Logging-Elektronik … (ESP32)“ sind die Firmware-Muster der Demonstratoren
>   ([`../../code/firmware/`](../../code/firmware/)); die „neun offen zugänglichen Arbeiten (Zenodo)“ sind frühere
>   Stände (April–Mai 2026), die den Weg dokumentieren, nicht den aktuellen Stand (README, „Zitieren“). Das „SOP- und
>   Zonenkonzept“ liegt nicht im Repository.

---

## Worum es geht

Untersucht werden soll, wie sich die Auflage- bzw. Kontaktkraft eines Systems aus mehreren gekoppelten, phasengesteuert angeregten Schwingmassen zeitlich verhält. Im Fokus steht **nicht** eine neue Kraftwirkung, sondern die messtechnische Charakterisierung der Kraft-**Wellenform** (Schiefe, Liftoff-Anteil, Spitzen-zu-Mittel-Verhältnis), ihrer Phasenabhängigkeit und der dabei auftretenden Artefakte (Spiel, Kontakte, Strukturkopplung).

## Status: prä-experimentell

**Vorhanden:**

- Vollständig dokumentierter Simulations- und Auswerterahmen: parametrisierte Phasenanregung je Modul, unilaterales Kontaktmodell (RK4, steife Kontaktfeder), Wellenform-Statistik, Residual- und Artefaktanalyse; neun offen zugängliche Arbeiten (Zenodo, ORCID 0009-0005-9984-4207).
- Präregistrierung mit H0/H1, vorab fixiertem Analyseplan (Block-Averaging, Run als statistische Einheit), Referenz-/Dummy-Kontrollen und Abbruchkriterien (Stop / Modify / Scale).
- SOP- und Zonenkonzept (Bau und Messung getrennt, Parameter-Freeze, Rohdaten-Schreibschutz) als ausgearbeitete Dokumentation.
- Steuerungs- und Logging-Elektronik als dokumentiertes Design mit Code (ESP32; phasenstarre LRA-Ansteuerung über gemeinsamen Phasenzähler; Weg-/Höhen-Logging).

**Noch nicht vorhanden:** ein eigener Kraftmessaufbau. **Es liegt keine eigene Messung vor** — genau dafür wird die Anbindung gesucht.

## Zentrale Aussagen (Theorie und Simulation, fremdverankert)

- **⟨F_N⟩ = M·g** ist für beschränkte periodische Innenbewegung eine Erhaltungs-Randbedingung (Schwerpunktsatz) — kein Forschungsziel. Die Simulationspipeline reproduziert diese Null-Basislinie: Im 19×19-Phasensweep liegt der Median der ⟨F⟩-Schätzer exakt bei M·g; Restabweichungen einzelner Bouncing-Konfigurationen sind nachweislich Endlich-Fenster-Effekte (Konvergenztest: −43,5 mN bei 10 s Auswertefenster → −0,5 mN bei 110 s). Unabhängig belegt in der Kontaktdynamik-Literatur (Perret-Liaudet & Rigaud 2007: ⟨N⟩ = mg bei bis zu 15 % Kontaktverlust; Wakou, Ochiai & Isobe 2008, arXiv:0801.4428).
- Primäre, erhaltungssichere Observable ist die **Wellenform**: Der Sweep zeigt drei Regime (Schiefe −0,3 bis +2,0; Liftoff-Anteil 0–76 %). Schärfste prüfbare Vorhersage: **negative Schiefe** tritt nur bei echter Mehrmodul-Dephasierung auf — im synchronen (effektiven Einzelmodul-)Fall und bei Zweiergruppen-Phasung bleibt die Schiefe positiv.

## Geplanter Prüfstand (AP1, Sachkosten ≈ 10.000 €)

Wägezelle, einseitige Federlagerung, zwei bis drei phasengesteuerte Massen, optionaler optischer Referenzkanal. Durchführung strikt nach Präregistrierung: statische Referenz und Dummy-Masse, Blindung/Randomisierung wo möglich, Run als statistische Einheit, vollständige Metadaten, Rohdaten-Schreibschutz.

## Wissenschaftlich anschlussfähig

Der Wert der geplanten Arbeit liegt in reproduzierbarer Differenz-Kraftmessung im mN-Bereich unter kontrollierten Bedingungen, der Charakterisierung periodischer Kraftsignaturen und einer auditierbaren Messkette einschließlich Artefakt- und Driftbehandlung — anschlussfähig an Kraftmesstechnik (statische und dynamische Kräfte), Wäge-/EMK-Technik und Messunsicherheits-Methodik.

## Was ich anbiete und suche

Ich bringe Simulationscode und Auswertungspipeline, Präregistrierung, SOP-Dokumentation, das Elektronik-Design sowie Eigenleistung in Aufbau und Betrieb mit. Gesucht wird **wissenschaftliche Anbindung**: fachliche Begleitung, Zugang zu rückgeführter Referenz-Messtechnik, gemeinsame Messung und Veröffentlichung — ausdrücklich auch des erwarteten Mittelwert-Null-Ergebnisses und einer möglichen Falsifikation der Wellenform-Vorhersagen.

---

**Matthias Früh** — unabhängiger technischer Forscher (Messtechnik, Systemdynamik) · ORCID 0009-0005-9984-4207
