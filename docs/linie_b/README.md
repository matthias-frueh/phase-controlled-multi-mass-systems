# Linie B: Forschungsrahmen und Notizen zur Medienkopplung

Stand: 22. Oktober 2026. Lizenz dieses Ordners: CC BY 4.0, siehe [`../../LICENSE-CC-BY-4.0`](../../LICENSE-CC-BY-4.0). Namensnennung: „Matthias Früh, PCMMS“, https://github.com/matthias-frueh/phase-controlled-multi-mass-systems

Dieser Ordner enthält die Dokumente der Linie B, der optionalen zweiten Forschungslinie des Projekts: gerichtete
Nettobewegung durch Impulsübertrag an ein umgebendes Medium, mit separater Apparatur
([`../../README.md`](../../README.md), „Zwei Forschungslinien“; [`../einordnung.md`](../einordnung.md), Abschnitt 3).
Die Dokumente lagen bis Oktober 2026 nur außerhalb des Repositorys. Es gibt keine Messdaten; alle Zahlen sind
Simulation oder Analytik, die Effektgrößen gelten nur im Zweiterm-Ansatz mit stationärem C_D. Linie B gehört im
Arbeitsplan zur Stufe S5 (geparkt), Arbeitspaket AP-28, Status „später“. Die Prüfung der Modelle steht in
[`../../rechnungen/linie_b/PROTOKOLL.md`](../../rechnungen/linie_b/PROTOKOLL.md) (Befunde LB-01 bis LB-08 und LB-14;
LB-09 bis LB-13 betreffen Luftkräfte am Linie-A-Aufbau V1), teilweise gegengeprüft in
[`../../rechnungen/linie_b/verifikation/PROTOKOLL.md`](../../rechnungen/linie_b/verifikation/PROTOKOLL.md); wo ein
Dokument davon abweicht oder überholt ist, steht das im Vermerk am Kopf. Die Texte selbst sind bis auf den Vermerk
unverändert.

| Datei | Inhalt | Stand | Arbeitspaket | Status |
|---|---|---|---|---|
| [`forschungsrahmen_v3_5_2026-05.md`](forschungsrahmen_v3_5_2026-05.md) | Forschungsrahmen v3.5: positive Hypothese H1 (medium-gekoppelte Fortbewegung), Grenzfälle Vakuum und Medium, Zerlegung des Residualterms in Medien- und Artefaktanteil, Messkonfigurationen A bis D, Medienkopplungsmodell mit Effektgrößen, Reibung und Schub-Pendel, Falsifikationskriterium, Kontrollen | Mai 2026 (v3.5) | AP-28 | später; korrekturbedürftig, Nachfolger v3.6 vorgesehen; Effektzahlen (§9) auf der Driftwiderstandskraft statt F̄_A, Kraftmodell bei kleiner KC-Zahl offen (Vermerk) |
| [`pruefarchitektur_2026-09-01.md`](pruefarchitektur_2026-09-01.md) | Notiz zur späteren Prüfarchitektur: freier Fall verworfen, evakuierbare Kammer mit Torsionswaage, randomisierte Druckreihe mit Überdruckpunkt, druckabhängige Störmechanismen, Nebenbefund geometrische Phase, Reihenfolge | 1. September 2026 | AP-28 | später; Entwurf, ausdrücklich nicht der nächste Schritt; Driftwert (§1) überholt, Auflösungsanforderung (§2) neu zu bewerten, Auswertegröße der Druckreihe (§3) zur Änderung vorgeschlagen (Vermerk) |
| [`richtungsnotiz_medienkopplung_2026-09-06_v5_2.md`](richtungsnotiz_medienkopplung_2026-09-06_v5_2.md) | Richtungsnotiz „Gleichrichtung und mögliche Einsatzschwellen phasenstrukturierter Medienkopplung“: Modelle A, B und C mit Übertragungsregeln, Dichteabhängigkeit und Symmetriekontrollen, offene Modellfrage zum quasistationären Widerstandsgesetz, rechnerisches Prüfprogramm, Regime der Druckreihe, Mechanismus 2 | 6. September 2026 (v5.2) | AP-28 | später; Prüfprogramm Punkte 2 und 3 erledigt, offene Modellfrage (§6) präzisiert, nicht gelöst; Kennzahlen in §6 berichtigt (LB-01) (Vermerk) |
| [`review_leitfaden_skripte_2026-09-06.md`](review_leitfaden_skripte_2026-09-06.md) | Leitfaden der externen Skriptprüfung: Dateien mit MD5, Zuordnung von Notiz und Code, Reproduktionsergebnisse, zehn Prüffragen | 6. September 2026 | AP-28 | später; Prüfanleitung; Fragen laut Skriptkorrekturen beantwortet (Befunde dort §1); Prüfgegenstand (v1-Skripte) und Reproduktion in [`review_2026-09-06/`](../../rechnungen/linie_b/review_2026-09-06/) (Vermerk) |
| [`skriptkorrekturen_2026-09-06.md`](skriptkorrekturen_2026-09-06.md) | Korrekturbeleg v1 → v2 nach der Skriptprüfung: stationäre Driftkarte, Trennung von Driftwiderstandskraft und Pendelkraft F̄_A, Kennzahlen, Folgen für den Korpus | 6. September 2026 | AP-28 | später; Korrekturbeleg; v2-Skripte in [`quelle_kopie/`](../../rechnungen/linie_b/quelle_kopie/), nachgerechnet in LB-04 bis LB-08; Folgen für den Korpus nicht eingearbeitet (Vermerk) |

Skripte und Daten: die korrigierten Modelle v2 in
[`../../rechnungen/linie_b/quelle_kopie/`](../../rechnungen/linie_b/quelle_kopie/), die stationäre Driftkarte
[`sweep_13x13_drift_v2.csv`](../../rechnungen/linie_b/sweep_13x13_drift_v2.csv) und die historische, nicht
eingeschwungene v1-Karte [`sweep_13x13_drift_v1.csv`](../../rechnungen/linie_b/daten/sweep_13x13_drift_v1.csv); die
v1-Originale als Prüfgegenstand der Skriptprüfung und deren Reproduktion in
[`../../rechnungen/linie_b/review_2026-09-06/`](../../rechnungen/linie_b/review_2026-09-06/) (Aufruf in
[`../../rechnungen/README.md`](../../rechnungen/README.md), Abschnitt `linie_b/`). Das „Egg“-Profil der Linie B ist
nicht das der Linie A (LB-14). Demonstrator-Unterlagen der Linie B (Ballon, Begleitbericht, Pendeltest) liegen in
[`../konzepte/`](../konzepte/README.md), ihre Auswerteskripte in
[`../../code/demonstrator/`](../../code/demonstrator/README.md).

**Nicht vorhanden.** Der Forschungsrahmen v3.6 ist vorgesehen (AP-28); Abgleichpunkte gegen v3.5 stehen im
[Literaturabgleich](../literaturabgleich_2026-09-12.md). Ein Kraftmodell bei kleiner Keulegan-Carpenter-Zahl (AP-28)
und eine integrierte Pendelsimulation (Modell C, Skriptkorrekturen §6) liegen nicht vor. H1_fluid erhält nach dem
Entwurf der [Präregistrierung v2](../praeregistrierung_v2_entwurf.md) (§0) eine eigene Präregistrierung; sie liegt
nicht vor. Die Vorfassungen v1–v5.1 der Richtungsnotiz und die Antworten der externen Skriptprüfung liegen nicht im
Repository.

Bearbeitungsstand aller Arbeitspakete: [`../arbeitsplan_status.md`](../arbeitsplan_status.md).
