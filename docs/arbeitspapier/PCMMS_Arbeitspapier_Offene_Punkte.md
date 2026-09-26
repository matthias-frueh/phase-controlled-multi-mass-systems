# PCMMS-Arbeitspapier — Offene Punkte

Historischer Ausgangsstand: 05.09.2026 · Quelle: PCMMS_Dissertation_v2.tex, **97 Seiten**

## Erledigt (05.09.2026)

- [x] 1 Sinus-Profil-Sweep → Kap. 11, Phasenkarte kollabiert auf R; Nocke zwingend
- [x] 2 Sensitivität k (5 Steifigkeiten, 7×7) und ζ (5 Werte, 4 Regimepunkte)
      → Auslegungsfenster 1 ≲ 3f/f_n ≲ 3, ζ ≲ 0,1; Vorzeichenregel hat Gültigkeitsbereich
- [x] 3 Symbolverzeichnis: 23 Einträge ergänzt
- [x] 4 Fazit: sechs Befunde, sieben konkrete weiterführende Arbeiten
- [x] 5 Protokoll angeglichen: ≥100 Zyklen, Konvergenznachweis, drei Pflichtläufe
- [x] 6 Unnummerierte Formeln: Zählfehler, nur 4 reine Notationsdefinitionen, korrekt so
- [x] 7 Kurzfassung (deutsch) und Abstract (englisch) im Vorspann

## Offen — Projektentscheidungen, keine Schreibarbeit

8. ~~Recherche dokumentieren~~ **erledigt 05.09.** — Anhang C: Art, Zeitraum,
   Quellen, Suchbegriffe, Verifikationstabelle aller 21 Einträge, nicht
   aufgenommene Angaben. Keine TODO-Marke mehr im Quelltext.
9. Parameterabgleich: Forschungsrahmen v3_5 (2,2 Hz / 0,80) gegen Simulation
   und Laborplan (10 Hz / 0,65). Nur noch: Forschungsrahmen nachziehen?
10. „Yoshimura et al. 2008" im Messtechnik-Konzept v2 streichen —
    wahrscheinlich Fehlzuschreibung von Wakou/Ochiai/Isobe 2008.
11. ~~Sechs Lehrbucheinträge prüfen~~ **erledigt 05.09.** — alle sechs halten.
    Beckwith: 6. Aufl. Aug. 2006 (Schlüssel → beckwith2006). DOIs ergänzt:
    Bendat 10.1002/9781118032428, Featherstone 10.1007/978-1-4899-7560-7,
    NIST 10.6028/NIST.tn.1297. ISBNs: Kay, Lanczos, Beckwith.

## Neu durch die Arbeit vom 05.09. entstanden — Auslegung, nicht Text

12. Laborplan V1: Antrieb mit **asymmetrischem Profil** (Nocke oder programmierbarer Aktor); Exzenter/Kurbel bei konstanter Drehzahl ausgeschlossen (Punkt 18).
13. Laborplan V1: Wägezelle von 3–5 kg auf **20 kg** bei ungemessener Dämpfung; 10 kg erst nach nachgewiesenem ζ ≥ 0,1 (Punkt 20).
14. Kontaktelement: k und ζ vor der Kampagne messen; Fenster 1 ≲ 3f/f_n ≲ 3, ζ ≲ 0,1.

## Stand des Dokuments

101 Seiten · 21 Literatureinträge, alle verifiziert · 9 Abbildungen · 48 Gleichungen
· 3 Datensätze (sweep_19x19.csv, sweep_7x7_sinus.csv, sens_k_*.csv)
· kompiliert mit pdflatex/bibtex ohne Warnung · keine unaufgelöste Referenz

## D · Aus externer Prüfung, 05.09.2026 — alle sechs Punkte angenommen

Vorrang: Präzisierung, kein zusätzlicher Umfang.

15. **Äquivalenzlogik statt Nichtsignifikanz.** Spur 1: qualifiziert nur, wenn das
    KI von µ_Δ vollständig innerhalb ±ε_ctrl liegt; außerhalb null → Fehler; breiter
    als Toleranz → unbestimmt. Spur 2 Nullergebnis: KI jeder Differenz innerhalb
    ±ε_phys. Vierter Ausgang „unbestimmt" wieder einführen. Kap. 10, Kap. 6, Fazit,
    Kurzfassung.
16. **Weicher Kontakt falsch erklärt.** k=10³ ist Isolationsbereich (f > f_n,
    Transmissibilität ≈ 0,66), nicht quasistatisch. Formel N ≈ Mg − (M/3)Σz̈ gehört
    zum steifen Grenzfall. Korrektur in §sens-k, Anhang B, Fazit, Kurzfassung.
17. **R_c = 1,94 ist die quasistatische Schwelle.** Dynamisch ≈ 1,94/1,34 ≈ 1,45.
    Feine R-Abtastung 1,3–1,6 (8 Punkte), Transmissibilitätskorrektur in den Text.
18. **„Nocke zwingend" → „asymmetrisches Profil zwingend".** Nocke oder
    programmierbarer Aktor; Exzenter/Kurbel bei konstanter Drehzahl ausgeschlossen.
19. **„Auslegungsfenster" / „gesichert für ζ ≲ 0,1" auf „nach Stichproben"
    zurücknehmen.** Kap. 11, Fazit, Kurzfassung.
20. **Lastreserve abschließen:** ≥16·Mg (20-kg-Dose) bei ungemessener Dämpfung;
    ≥10 kg nur nach nachgewiesenem ζ ≥ 0,1. Kap. 7 und Punkt 13 oben.
21. Literaturkandidaten aus der Prüfung, VOR Aufnahme einzeln verifizieren:
    Osadchyy et al. 2023, Korendiy et al. 2026, Chatzinikolaidis et al.

### Stand Block D (05.09.2026, abends)
- [x] 15 Äquivalenzlogik, vier Ausgänge, ε_ctrl eingeführt — Kap. 6, 9, 10, 13, Fazit, Kurzfassung, Abstract, §1.5, Symbolverzeichnis
- [x] 16 Weicher Kontakt: Isolationsbereich statt quasistatisch — §sens-k, Anhang B, Kap. 6, Fazit
- [x] 17 R_c: quasistatisch 1,94 → dynamisch 1,45 über Transmissibilität; feine Abtastung bestätigt 1,44–1,48
- [x] 18 „asymmetrisches Profil zwingend" statt „Nocke zwingend" — sechs Stellen
- [x] 19 „nach Stichproben" statt „gesichert"/„Fenster" — Kap. 11, Fazit, Kurzfassung, Abstract
- [x] 20 Lastreserve zweistufig abgeschlossen — Kap. 7, Kap. 8, Fazit
- [x] 21 Literaturkandidaten geprüft und aufgenommen: Osadchyy 2023 (Sensors, DOI 10.3390/s23042170), Gurskyi/Korendiy 2023 (Machines, DOI 10.3390/machines11010097 — „Korendiy 2026" nicht auffindbar, ersetzt), Chatzinikolaidis 2020 + 2021 (IEEE RA-L). 21 Einträge.

## Stand 20.09.2026 (v2.1) — Abgleich mit Repository-Stand 2026-09 und Symbolverzeichnis v2.5

- [x] 22 Symbol Θ → β_h (Hold-Zeitanteil), 12 Stellen: Symbolverzeichnis, Tab. 9.1, Anhang Egg-Profil. Symbolverzeichnis v2.5 führt Θ (Dissertation v2) → β_h in der Migrationstabelle.
- [x] 23 „Halteanteil von 0,80" (Status der Parameter) → Vorwärtsanteil β ≈ 0,80 als andere Profilfestlegung; „Verhältnis nicht geklärt" ersetzt durch Verweis auf Symbolverzeichnis v2.5 (10.6, 10.7, B.2). Satz „Abgleich steht aus" bleibt, betrifft die Übertragung auf die Apparatur. Schließt Punkt 9 zur Hälfte; offen bleibt nur: Forschungsrahmen v3_5 nachziehen.
- [x] 24 „kein hinterlegter Datensatz" (§ Wertebereich, nach Abb. schnitt_nmin) ersetzt durch Feinsweep-Absatz: 2°-Raster, 441 Konfigurationen, N_min-Spitze 5,3304 N bei (120°, 240°), Abfall ≈ 0,23 / 0,19 N je Grad, 90,7 % liftoff-frei, |⟨N⟩ − Mg| ≤ 0,2 mN. Datensatz finesweep_2deg_120_240.csv, zitiert als frueh2026repo (Zenodo 10.5281/zenodo.22864178, GitHub-Tag 2026-09). Anhang A „Datensatz" ergänzt.
- [x] 25 In Arbeitspapier v2.2 umgesetzt: Titelblatt und Vorspann umgestellt; Hochschul-, Grad- und Betreuungsplatzhalter sowie Prüfungserklärung entfernt; Status- und Versionshinweis ergänzt.

Stand des Dokuments: 101 Seiten · 22 Literatureinträge · 9 Abbildungen · Datensätze sweep_19x19.csv, finesweep_2deg_120_240.csv, sweep_7x7_sinus.csv, sens_k_*.csv · Vorschau-PDF vom 20.09. mit XeLaTeX/Latin Modern gesetzt (Abbildungen aus den JPEG-Exporten).


## Stand 20.09.2026 — Arbeitspapier v2.2

- Redaktionelle Überführung aus `PCMMS_Dissertation_v2_1.tex`; neuer Titelzusatz: „Messrahmen, numerische Referenzfälle und Artefaktkontrolle“.
- Englische Selbstbezeichnung `This working paper`; PDF-Metadaten als Arbeitspapier.
- Fachlicher Haupttext, Anhänge und Literaturbasis aus v2.1 unverändert übernommen; keine neue wissenschaftliche Gesamtprüfung.
- Formelverzeichnis v2.5 unverändert.
- Die neun Abbildungsdateien wurden aus den eingebetteten Bildern der gelieferten Vorschau rekonstruiert und als echte PDF-Dateien beigefügt; keine neuen Plotberechnungen.
- Der Repository-DOI bezeichnet weiterhin das Repository-Paket. Ein DOI für dieses Arbeitspapier wird erst durch dessen eigene Veröffentlichung festgelegt.
- Veröffentlichung auf Zenodo noch nicht vorgenommen. Die übrigen offenen Projektentscheidungen bleiben bestehen.

Aktuelle Ausgabe: 101 Seiten · 22 Literatureinträge · 9 Abbildungen · XeLaTeX/BibTeX; keine unaufgelösten Verweise. Die interne Symboltabelle ist seitenübergreifend gesetzt, überbreite Tabellen wurden angepasst.


## Stand 25.09.2026 — Arbeitspapier v2.3

- [x] 26 Deutung des Basislinienresiduums korrigiert (Kurzfassung, Abstract, 7.8, 9.4, 11.2, 12.2, A.1, A.4, B.4). „Langsame Modulation“ ersetzt durch den Randterm des Auswertefensters, δ = δ_w + δ_Q mit δ_w = Δv_S/(g·T_w), Schranke |δ_w| ≤ 2·v_S,max/(g·T_w) (Gl. 9.3). Neue Tabelle 9.4 mit der Zerlegung aus der Nachrechnung vom 13.09.2026: 315/24/22 Konfigurationen stationär/grenzwertig/nicht stationär, max |δ_w| = 3714 ppm, δ_Q Median 0, max 93 ppm.
- [x] 27 Faktenfehler behoben: „Sämtliche 361 Residuen negativ“ → gemischt, 178 negativ, 167 positiv, 16 null (sweep_19x19.csv). „Mittleres absolutes Residuum 29 ppm“ → Median 29 ppm, Mittelwert 133 ppm. Anzahl λ > 50 % in Tab. 9.2 und A.4 nachgetragen (146).
- [x] 28 Archiv-Höchstwert −6816 ppm als Einschwingen ausgewiesen: Übergang 18,8 s, danach Periode 1, δ_w = −2 ppm. Hinweis zur Einschwingkontamination des Archivs im Datensatz-Anhang (λ > 0,5 %-Pkt an 11 Punkten, γ₁ > 0,02 an 7, N_max > 0,2 N an 9, A > 0,05 an 6).
- [x] 29 Symbolverzeichnis des Papiers um δ_w, δ_Q, Δv_S, v_S,max, T_w ergänzt; Bezeichnungen an das Formelverzeichnis angeglichen.
- [x] 30 Belegordner `nachrechnung_2026-09-13` im Quellpaket: Datensatz, 100-s-Klassifikation, Skripte (nur Pfade angepasst), Engine, Ergebnisnotiz.

Offen:
- 31 Karten (λ, γ₁, A, N_min) aus der Nachrechnung neu zeichnen und die 22 nicht stationären Punkte markieren; Periodenkarte mit Randtermklassen als neue Abbildung.
- [x] 32 Formelverzeichnis v2.6 (26.09.2026): δ, δ_w, δ_Q und v_S,max in Abschnitt 3.2 ergänzt, Nachrechnung in die Codezuordnung aufgenommen.
- 33 Rasterabbildungen durch Vektororiginale ersetzen.
- 34 Befunde der Regimeanalyse (Zeitschrittabhängigkeit an Regimegrenzen, Bistabilität der Satelliteninseln) erst nach Abschluss mit exaktem Ereignislöser aufnehmen.

Aktuelle Ausgabe: 103 Seiten · XeLaTeX/BibTeX · keine unaufgelösten Verweise.
