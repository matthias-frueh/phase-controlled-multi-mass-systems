# Arbeitspakete AP-01 bis AP-30: Bearbeitungsstand

Stand: 4. Oktober 2026. Lizenz dieses Ordners: CC BY 4.0, siehe [`../LICENSE-CC-BY-4.0`](../LICENSE-CC-BY-4.0).
Namensnennung: „Matthias Früh, PCMMS“, https://github.com/matthias-frueh/phase-controlled-multi-mass-systems

Die Arbeitspakete folgen dem Arbeitsplan der Gesamtprojektanalyse vom Oktober 2026: 30 Pakete in fünf Stufen, S1 vor
dem Einfrieren von Teil A der Präregistrierung v2, S2 Phase 0 und Teil B, S3 Phase 1 und Auswertung, S4 nach V1, S5
geparkt (Linie B und C). Diese Übersicht dokumentiert den Bearbeitungsstand; sie ist kein neuer Auftrag. Alles im
Repository ist Simulation oder Analytik; Messdaten existieren nicht.

**Statusbegriffe.** *vorhanden*: Ergebnis liegt im Repository und ist abgenommen oder geprüft. *vorläufig*: Ergebnis liegt
vor, gilt aber als Arbeitsfestlegung oder Entwicklungsversion und kann vor dem Einfrieren überarbeitet werden.
*in Bearbeitung*: Teilschritte erledigt, Paket nicht abgeschlossen. *noch nicht umgesetzt*: Paket der Stufe S1, noch
nicht begonnen; vorhandene Grundlagen sind genannt. *später*: Stufen S2 bis S5, erst nach Entscheidungen oder nach V1.
Konzepte sind Konzepte, keine Umsetzung ([`konzepte/README.md`](konzepte/README.md)).

## Stufe S1 – vor dem Einfrieren von Teil A

| AP | Inhalt | Status | Im Repository | Bearbeitungsstand, offen |
|---|---|---|---|---|
| AP-01 | Hardwarestand klären, Antrieb festlegen (Nocke oder programmierbarer Aktor), Anforderungsblatt | noch nicht umgesetzt | Firmware-Muster der Demonstratoren ([`../code/firmware/`](../code/firmware/)); Laborplan V1 als Konzept ([`konzepte/laborplan_v1_2026-05.md`](konzepte/laborplan_v1_2026-05.md)) | Entscheidung des Autors; Hardwarestand eines Linearaktors nicht belegt; Inventar nach Simulation, Firmware, Mechanik und erprobter Hardware fehlt |
| AP-02 | Auslegungswerkzeug (Werkzeug 2): 3-FG-Zellmodell, Laufarten, Prüfungen §5.3, PB1, Luftmasse | vorhanden | [`../code/auslegung.py`](../code/auslegung.py), Tests, [`abnahme_ap02_ap03.md`](abnahme_ap02_ap03.md) | PB1 nach §8.5 (PR #14); zugrunde liegende Regeln sind Arbeitsfestlegungen (AP-08); m_L wird vorgegeben; Dateiformat für gemessene Harmonische offen |
| AP-03 | Ereignisgenauer Löser und Einzugsprüfung (Hüpfzustände, Stoßspitzen, Konvergenz) | vorhanden | [`../code/ereignisloeser.py`](../code/ereignisloeser.py), [`../code/einzugsgebiete.py`](../code/einzugsgebiete.py), [`einzugsgebiete_v1_kandidat.md`](einzugsgebiete_v1_kandidat.md), Abnahmebericht | ein Freiheitsgrad, ohne Kippmoden und zugesetzte Luftmasse (Abnahme, Abschnitt 3); Neurechnung mit gemessenen K, ζ nach Phase 0 nötig |
| AP-04 | Arbeitspunkt, Geometrie (G0 oder G60h), Zellen, Konstruktionsentwurf | noch nicht umgesetzt | Auslegungskandidat (`auslegung.py --candidate`); Einzelzellkräfte und Kippmoment ([`../rechnungen/kippmoment/`](../rechnungen/kippmoment/PROTOKOLL.md)); Auslegungsraum ([`../rechnungen/auslegung/`](../rechnungen/auslegung/PROTOKOLL.md)) | hängt an AP-01; Geometrie, Zellwahl und Dämpfungsziel sind Entscheidungen des Autors; kein Konstruktionsstand |
| AP-05 | Sicherheitskonzept: Anlaufprotokoll, Überlastanschlag, Echtzeit-Abschaltung, ζ-Ziel, Nennlast | noch nicht umgesetzt | Bausteine: Gültigkeits- und Abbruchregeln der Präregistrierung v2 (§9.1, §9.2), Einzugsgebiete und Stoßspitzen (AP-03), Laborplan V1 Abschnitt 10 | kein eigenständiges Dokument; ζ-Ziel, Nennlast und Umfang von E1 offen (Entscheidung des Autors) |
| AP-06 | Messkette und Kalibrierplan: drei DC-fähige Zellkanäle, Abtastrate nach A6, Wegkanal, Referenzzelle, dynamische Kalibrierung, P0.1-Plan | noch nicht umgesetzt | Konzepte ([`konzepte/mehrkanal_messarchitektur_2026-05.md`](konzepte/mehrkanal_messarchitektur_2026-05.md), [`konzepte/messtechnik_anschluss_v2_2026-09.md`](konzepte/messtechnik_anschluss_v2_2026-09.md), Laborplan V1 Abschnitte 5 und 6); Anforderungen in der Präregistrierung v2 (A6, A9.2) | Spezifikation und Datenblattnachweis fehlen; Kanalzahl und Wegkanal offen; Nachweis des Ziel-u_c über Werkzeug 8 (AP-13) |
| AP-07 | Modulkinematik in Phase 1: Sensorentscheid, Kontaktindikator, Zusatzmasse, Kabelkräfte | noch nicht umgesetzt | Anforderungen in der Präregistrierung v2 (E3, Tabelle C) | Sensorentscheid offen; hängt an AP-01 und AP-06 |
| AP-08 | Teil A: Statistik, Entscheidungsregeln, Reichweite von H3 | vorläufig | Präregistrierung v2 §3, §5.4, §8, §9, §12, A8, A9 (PR #14); Kontrollrechnung zur Entwurfsfassung ([`../rechnungen/ap08_kontrolle/`](../rechnungen/ap08_kontrolle/README.md)); Statistikprüfung ([`../rechnungen/statistik/`](../rechnungen/statistik/PROTOKOLL.md)) | Arbeitsfestlegungen vom 3. und 4. Oktober 2026 (§0, §12, A0); offen nach §12: δ_H2, δ_H3, Relevanzgrenze von H3, Grenzen von H1Z, Lesart von A9.11, Gruppen (I) und (II); Kalibrierung der Fehlerraten durch Werkzeug 8 steht aus |
| AP-09 | Teil A: Identifizierbarkeit, Kontrollen, Tabelle C, E3 | vorläufig | Präregistrierung v2 (PR #14); Identifizierbarkeitsrechnung ([`../rechnungen/statistik/s4_identifizierbarkeit.py`](../rechnungen/statistik/s4_identifizierbarkeit.py)) | Schwellen von E3, Punkte I und Paarläufe offen (§12); Konvention (b) für M als Arbeitsfestlegung |
| AP-10 | Werkzeuge 3 und 7: Aufnahme mit Registrierungskennung, Manifest, Randomisierung, Monitor, Schutzpfad | noch nicht umgesetzt | Pflichtenheft in Präregistrierung v2 §12 Nr. 3 und 7; Entwurf des Rohdatenformats in [`plan_ap13_pipelinetest.md`](plan_ap13_pipelinetest.md), Abschnitt 2.6 | hängt an AP-01, AP-05, AP-06 (DAQ und Antriebssteuerung) |
| AP-11 | Werkzeuge 4 und 5: Anpassverfahren P0.4/P0.5, Pilotskript | noch nicht umgesetzt | Pflichtenheft §12 Nr. 4 und 5 | Erfolgskriterium wird an synthetischen Daten aus AP-13 geprüft |
| AP-12 | Werkzeug 6: Auswerteskript §8.1–§8.7, Zeltfit, H3-Fortpflanzung, E3 | noch nicht umgesetzt | Pflichtenheft §12 Nr. 6; Schnittstelle Stufe 1/2 im Plan AP-13 (2.6); Grundstock in [`../rechnungen/statistik/`](../rechnungen/statistik/PROTOKOLL.md); S₃-Prüffall in [`../rechnungen/symmetrie_randterm/`](../rechnungen/symmetrie_randterm/PROTOKOLL.md) | wird aus dem Text der Präregistrierung geschrieben; Abgleich mit der Referenzimplementierung von Werkzeug 8 vorgesehen |
| AP-13 | Werkzeug 8: Pipelinetest, Planungs- und Kalibriersimulation | noch nicht umgesetzt (Plan vorhanden) | [`plan_ap13_pipelinetest.md`](plan_ap13_pipelinetest.md) (Architektur, Szenarienkatalog, Budget, Meilensteine); Kurzmessungen ([`../rechnungen/ap13_kurzmessung/`](../rechnungen/ap13_kurzmessung/README.md)) | Regelgrundlage seit PR #14 in `main`; der Plan ist nicht überarbeitet (Anhang „Abgleich mit `main`“); Entwicklungsaufgabe nicht angestoßen; Endabnahme braucht AP-12 |
| AP-14 | Präregistrierung bereinigen, Teil A einfrieren und registrieren | in Bearbeitung | Präregistrierung v2 als Entwicklungsversion ([`praeregistrierung_v2_entwurf.md`](praeregistrierung_v2_entwurf.md), [Anhang](praeregistrierung_v2_anhang.md)) | erledigte Teilschritte: Vorzeichenregel aus §1, A3, A4 (PR #12), Verweise auf Kanalzahl und Nennlast (PR #13), Entscheidungsregeln und Kontrollen (PR #14); offen: Werkzeuge 3–8 mit Commit-Hashes, Plattform und Dateinamen der Registrierung, Status der Präregistrierung v1, Einfrieren und Registrierung (nicht Teil des laufenden Auftrags) |
| AP-15 | Aktive Dokumente bereinigen | vorhanden | README, `docs/*.md`, Arbeitspapier v2.4 und Formelverzeichnis v2.7 im Quelltext (PR #13) | **PDF- und Quelltextstand:** Die PDFs geben den Stand vom 26.09. bzw. 28.09.2026 wieder, die Nachträge vom 2. Oktober 2026 stehen nur im Quelltext (Offene Punkte Nr. 43); Neusatz und Versionsnummern entscheidet der Autor. Dokumente außerhalb des Repositorys (Arbeitsmanuskript, Forschungsrahmen der Linie B) sind nicht nachgeführt |
| AP-16 | Literaturbestand bereinigen | vorhanden, mit Prüfbedarf | [`../docs/arbeitspapier/references.bib`](arbeitspapier/references.bib), Anhang C des Arbeitspapiers, [`literaturabgleich_2026-09-12.md`](literaturabgleich_2026-09-12.md); formale Prüfung in [`../rechnungen/neuheit/`](../rechnungen/neuheit/PROTOKOLL.md) | **Literatur-Prüfbedarf:** Primärquellenprüfung der als „zu prüfen“ markierten Angaben (Offene Punkte Nr. 42); die Recherche außerhalb des Bestands ist nicht begonnen und nicht Teil des laufenden Auftrags |
| AP-17 | Status- und Rückzugsvermerke | vorhanden, teils offen | einheitliche Rückzugsvermerke in README, Wegweiser, Arbeitspapier, Formelverzeichnis (PR #13); Konzepte mit Vermerk ([`konzepte/`](konzepte/README.md)) | offen: Umgang mit den öffentlichen Altständen (Zenodo-Einträge April bis Mai 2026; Hinweis, neue Version oder kein Schritt) und ein Vermerk zur Ergebnisnotiz vom 13.09.2026 in [`arbeitspapier/nachrechnung_2026-09-13/`](arbeitspapier/nachrechnung_2026-09-13/) – beides Entscheidung des Autors, nicht beschlossen |
| AP-18 | Institutionelle Anbindung (Messplatz, Kalibrierung, Review, Replikation) | noch nicht umgesetzt | Konzept der gesuchten Anbindung ([`konzepte/messtechnik_anschluss_v2_2026-09.md`](konzepte/messtechnik_anschluss_v2_2026-09.md)) | Entscheidung des Autors: Anbindung als Tor zu Phase 0 beibehalten oder eigenen Messplatz mit externer Kalibrierung und Review; Anfrageunterlage mit Mindestumfang fehlt |

## Stufen S2 bis S5 – später

| AP | Inhalt | Stufe | Status | Vorhandene Grundlagen im Repository |
|---|---|---|---|---|
| AP-19 | Aufbau, Endmontage, Inbetriebnahme | S2 | später | – (setzt AP-01, AP-04 bis AP-07, AP-10, AP-14, AP-18 voraus) |
| AP-20 | Phase 0: Apparaturcharakterisierung (P0.1–P0.10, Referenz- und Pilotläufe) | S2 | später | Ablauf und Schwellen in der Präregistrierung v2 (A9.2) |
| AP-21 | Arbeitspunkt endgültig wählen, Teil B registrieren (Vorhersagen aus gemessenen Zeigern, Neukalibrierung) | S2 | später | Werkzeuge 2 und 3 (AP-02, AP-03); Planungsmodus von Werkzeug 8 im Plan AP-13 |
| AP-22 | Phase 1 und Datenschluss | S3 | später | Laufplan und Blockregel in der Präregistrierung v2 (§6, A9.12) |
| AP-23 | Auswertung und Veröffentlichung (drei Ausgänge je Hypothese, Nullergebnisse eingeschlossen) | S3 | später | Entscheidungsregeln §8, §9 |
| AP-24 | Unabhängige Replikation an einer zweiten Apparatur | S4 | später | Präregistrierung v2 §10.1 |
| AP-25 | Numerik der Linie A nacharbeiten (Karten als Attraktormengen, S₃-Prüfung, Liftoff-Kennzahlen als Spannen) | S4 | später | ereignisgenauer Löser (AP-03); Prüfrechnungen zu Engine, Symmetrie und Randterm ([`../rechnungen/engine/`](../rechnungen/engine/PROTOKOLL.md), [`../rechnungen/symmetrie_randterm/`](../rechnungen/symmetrie_randterm/PROTOKOLL.md)) |
| AP-26 | Explorative Folgestudien an der Apparatur (Liftoff, Hysterese, Profilvarianten) | S4 | später | nur mit Schutzkonzept (AP-05) |
| AP-27 | Räumliche Last, N Module, Regelung, Robotik | S4 | später | linearer Löser als Referenz für N = 3 |
| AP-28 | Linie B: Kraftmodell bei kleiner Keulegan-Carpenter-Zahl, Forschungsrahmen v3.6 | S5 | später | Kontrollrechnungen und Modelle v2 ([`../rechnungen/linie_b/`](../rechnungen/linie_b/PROTOKOLL.md), als Linie B gekennzeichnet); der Forschungsrahmen liegt nicht im Repository |
| AP-29 | Linie C: Wiederaufnahmebedingungen | S5 | später (geparkt) | – |

## Repository und Veröffentlichung

| AP | Inhalt | Status | Bearbeitungsstand |
|---|---|---|---|
| AP-30 | Repository sichern, thematische Pull Requests, Release | in Bearbeitung | Tag `stand-2026-09-28` vor der ersten Änderung; thematische Pull Requests #12 (Werkzeuge AP-02, AP-03), #13 (AP-15 bis AP-17), #14 (AP-08, AP-09), #15 (Rechnungen der Analyse) und dieses Dokumentpaket; Release, Zenodo und Einfrieren sind nicht Teil des laufenden Auftrags |

## Offene Entscheidungen des Autors

Sie werden hier nur geführt; aus ihnen entsteht kein Entwicklungsauftrag.

- Antrieb (Nocke mit Folger oder programmierbarer Aktor) und tatsächlicher Hardwarestand (AP-01).
- Geometrie G0 oder G60h, Zellwahl, Kontakt und Dämpfungsziel, Umfang von E1 und Nennlast (AP-04, AP-05).
- Messkette: Kanalzahl, Wegkanal, Abtastrate (AP-06); Sensor der Modulkinematik (AP-07).
- Institutionelle Anbindung als Tor zu Phase 0 oder eigener Messplatz (AP-18).
- Registrierungsplattform und Dateinamen; Status der Präregistrierung v1 nach Registrierung von Teil A (AP-14).
- Umgang mit den öffentlichen Altständen und Vermerk zur Ergebnisnotiz 13.09. (AP-17); Release und Zenodo (AP-30).
- Neusatz der PDFs und Versionsnummern von Arbeitspapier v2.4 und Formelverzeichnis v2.7 (Offene Punkte Nr. 43);
  Primärquellenprüfung der Literatur (Nr. 42).
