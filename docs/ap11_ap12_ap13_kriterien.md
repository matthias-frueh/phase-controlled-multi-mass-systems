# Kriterienmatrix AP-13 – Entwicklungsstand der ersten Softwarestufe

Stand 16.10.2026 · Lizenz CC BY 4.0 · erzeugt mit `python3 code/pcmms_auswertung harness kriterien --pruefstand …
--ausgabe docs/ap11_ap12_ap13_kriterien.md --kompakt docs/ap11_ap12_ap13_pruefstand` aus dem Prüfstand auf Commit
`7a259ef` (Profil `ENTW-2026-10+red(bootstrap_B=1000, e3_mc=1000, eps_ctrl_datensaetze=1000, h2_replikate=1000,
h3_mc=1000)`, Entwicklungsplan n = 24, n_min = 18, Stufe L1, Präzisionsreihe L0/L2/L4). Kompakte Ergebnisse:
[`ap11_ap12_ap13_pruefstand.json`](ap11_ap12_ap13_pruefstand.json); Einordnung, Befunde und Grenzen:
[`ap11_ap12_ap13_software.md`](ap11_ap12_ap13_software.md). Kriterien nach Plan AP-13 Abschnitt 1.3 und Präreg A9.11.

*Synthetische Entwicklungsdiagnostik, keine Kalibrierabnahme.* Status: **geprüft** = mit normativer Kampagnenzahl
bewertet oder deterministisch vollständig geprüft; **nur probeweise gerechnet** = mit weniger Kampagnen oder Replikaten
bzw. mit Entwicklungsannahmen; **fehlt** = in dieser Stufe nicht umgesetzt oder nicht gerechnet; **fachlich offen** =
Kriterium oder Lesart offen (§12); **in diesem Modell nicht prüfbar** = der Katalog oder das Modell stellt den Fall nicht
dar. Zahlen: Rate ± Monte-Carlo-Fehler (Zähler/Nenner); ein Punktschätzer innerhalb des Solls ist bei dieser
Kampagnenzahl kein Nachweis.

> **Vermerk vom 16.10.2026 (nachträglich, nicht aus dem Prüfstand erzeugt).** Die Tabelle ist der Stand `7a259ef` vor
> den Korrekturen A–E ([Softwaredokument, Abschnitt 1a](ap11_ap12_ap13_software.md#1a-korrekturen-vom-16102026)) und
> nicht neu gerechnet. **K12**: Der Planungshaken simulierte T_Lauf = 17 s statt 16 s und einen statt zwei Messtagen
> (Korrektur A; N_z stimmte); die Kandidatenraten sind potenziell betroffen. **K19**: Der verrauschte Ebenenabgleich lief
> mit ⟨N⟩ als Phasenmittel in Stufe 1 (Korrektur B); der rauschfreie Abgleich ist nicht betroffen. **E3**: Alle Raten
> sind ohne Unsicherheit von T gerechnet (Korrektur E; C betrifft nur berichtete k = 2-Werte); daraus folgt keine
> Schwellenentscheidung. Die übrigen Zeilen beruhen auf Ebene H und sind von den Korrekturen nicht berührt.

| Nr. | Kriterium | Status | Befund (Rate ± MC-Fehler (Zähler/Nenner)) | Einschränkung |
|---|---|---|---|---|
| K01 | P(H1 falsifiziert \| exakte Superposition) ≤ 0,05 je Stufe, beide Betriebsarten | nur probeweise gerechnet | N01-A4 (Prüfsimulation mit kalibriertem c): 0.000 ± 0.000 (0/200); N03-ungleich: 0.000 ± 0.000 (0/40); N03-N3bindet: 0.000 ± 0.000 (0/40); N04-laufart: 0.000 ± 0.000 (0/40) | nur Stufe L1 und Betriebsart „Raster“ mit Entwicklungsplan; V1-Systeme siehe Kalibrierung V1 |
| K02 | P(H1 falsifiziert \| LTI-Artefakt oder Drift der Einzelmodulbasis) ≤ 0,05 | nur probeweise gerechnet | E04-kette: 0.000 ± 0.000 (0/30); E07-verstaerkung: 0.000 ± 0.000 (0/40); E07-basisdrift: 0.000 ± 0.000 (0/40); I04-drift: 0.000 ± 0.000 (0/30) | E04-kette mit Testvorgabe für c (eigenes System) |
| K03 | P(H1 falsifiziert \| größte wahre Abweichung < Δ_rel) ≤ 0,05 | nur probeweise gerechnet | A04-R1: 0.000 ± 0.000 (0/40); A06-phase: 0.000 ± 0.000 (0/30) | — |
| K04 | P(H1 bestätigt \| eine Größe genau an ±Δ_q) ≤ 0,05 | nur probeweise gerechnet | N05-F: 0.000 ± 0.000 (0/40); N05-N2: 0.000 ± 0.000 (0/40); N05-N3: 0.000 ± 0.000 (0/40); A04-R2: 0.000 ± 0.000 (0/40) | N05-N1 (Kopplung an N₁ genau an Δ_q) ist nicht konstruierbar (Befund Etappe 2) |
| K05 | P(H1 bestätigt \| exakt) ≥ 0,8 bei geplanter Laufzahl | nur probeweise gerechnet | P(H1 bestätigt \| exakt) = 0.965 ± 0.013 (193/200) bei n = 24, n_min = 18 | Laufzahl nicht nach §5.4 geplant (Entwicklungsplan) |
| K06 | P(H1 bestätigt \| exakt) nicht fallend mit der Präzision (L5 → L0) | nur probeweise gerechnet | L0: 0.925 ± 0.042 (37/40); L2: 0.950 ± 0.034 (38/40); L4: 1.000 ± 0.000 (40/40) | Stufen L0, L2, L4 mit Testvorgabe (b̂ = 0, c_B); nicht alle Stufen L0–L5 |
| K07 | P(H1 falsifiziert \| Kopplung mit Residuum ≥ 2·Δ_rel) ≥ 0,8 | nur probeweise gerechnet | A04-R4: 1.000 ± 0.000 (40/40) | — |
| K08 | – entfallen (Prüfrate von c nur berichtet, K15) | fachlich offen | entfallen; Prüfrate von c steht unter K15 | Plan 1.3 (K08 entfallen) |
| K09 | H2 entscheidbar bei u_c,erw 0,3–1 mN (Lesart offen) | fachlich offen | N01-A4 (Prüfsimulation): P(H2 bestätigt \| exakt) = 0.970 ± 0.012 (194/200) | Lesart „entscheidbar“ offen (Regel h2.lesart_entscheidbar) |
| K10 | Überdeckung des gewählten H2-Intervalls ≥ 0,936, auch beim symmetrischen Zelt | nur probeweise gerechnet | N01-A4: perzentil_0.95: ŷ⁰ 1.000 ± 0.000 (194/194), ŷ¹ 1.000 ± 0.000 (194/194); bca_0.95: ŷ⁰ 0.974 ± 0.011 (189/194), ŷ¹ 0.969 ± 0.012 (188/194) → gewählt perzentil_0.95; H01-zelt (symmetrisches Zelt): perzentil_0.95: ŷ⁰ 1.000 ± 0.000 (40/40), ŷ¹ 1.000 ± 0.000 (40/40); bca_0.95: ŷ⁰ 1.000 ± 0.000 (40/40), ŷ¹ 0.950 ± 0.034 (38/40) → gewählt perzentil_0.95 | Bezugswert der Überdeckung offen (§12); Entwicklungsprüffall „Schätzer an den rauschfreien Kurven“; Fenstervarianten w = 8° nicht gerechnet |
| K11 | P(H3 bestätigt \| Mismatch über PB3) ≤ 0,05 | nur probeweise gerechnet | C03-GF5: 0.900 ± 0.055 (27/30); C03-GF1: 0.967 ± 0.033 (29/30); C04-steif: 0.967 ± 0.033 (29/30) | H3 Fassung K, δ_H3 = 10 % (Entwicklungsprüffall); C03 mit Testvorgabe für c |
| K12 | Planung nach §5.4 (n_min, n₀) mit Startwert und dokumentiertem Rechenweg | nur probeweise gerechnet | Suche: kein zulässiger Arbeitspunkt unter diesen Annahmen; 28 Aufrufe der Planung, Kandidaten n_min [18, 24] | Planungssimulation mit wenigen Kampagnen je Kandidat; Rauschmodell des Szenarios auf die obere 80-%-Grenze skaliert; Startwert aus der Auslegungsgrenze nicht automatisch gesetzt |
| K13 | Rauschbias: nach Korrektur \|E[r(F_min)] − b̂\| ≤ 0,1·u_c,erw für ŷ⁰ und ŷ¹ | nur probeweise gerechnet | yhat0: max \|E[r] − b̂\|/u_c = 0.264 (MC-Fehler 0.085, Soll ≤ 0,1); yhat1: max \|E[r] − b̂\|/u_c = 0.246 (MC-Fehler 0.078, Soll ≤ 0,1) | u(b̂) nur aus dem MC-Fehler (eine Rauschvariante); Rauschmodellvarianten N04 nicht kombiniert |
| K14 | Quantil für ε_ctrl aus 10 000 simulierten Datensätzen (A9.8) | nur probeweise gerechnet | A9.8-Simulation im Pilotskript; im Prüfstand mit 1000 Datensätzen; ein Lauf mit 10 000 Datensätzen im normativen Einzellauf | Quantil je Kampagne, keine Ratenprüfung |
| K15 | Berichtsgrößen ohne Bedingung (Rate „nicht entscheidbar“ je Grund, Zusätze, H4, Prüfrate von c, Sensitivitäten) | nur probeweise gerechnet | Raten „nicht entscheidbar“ je Grund, Zusätze, H4, Sensitivitäten und Prüfrate von c je Szenario in der Prüfstandsausgabe | — |
| K16 | S₃: gleiche Bilder (10⁻⁹ N, 10⁻⁶°), ungleiche Module: Vorhersage exakt, Bildvergleich weicht ab | geprüft | F01: \|N_k\| 7.8e-16 N, γ₁ 7.8e-16, Phase 2.6e-13°, F_min − ⟨N⟩ 1.2e-05 N (Rasterschranke 1.8e-05 N); F03: Bildvergleich \|N_k\| 0.023 N, Vorhersage 7.1e-16 N | rauschfrei auf Ebene H; F_min nur bis auf die N_θ-Rasterschranke (Befund: 10⁻⁹ N für F_min nicht erreichbar, A1); Ebene Z und F02 (mit Rauschen) nicht gerechnet |
| K17 | Vorzeichen-Inversionstest S = N₊ + N₋ − 2Mg | fehlt | — | Gruppe G (Vorzeichen-Inversionstest) nicht im Katalog; Antrieb offen (Plan 5.4) |
| K18 | Zuordnung: Trefferquote ≥ 0,8 (0,1 % Kopplung p = 1; Kette ≥ 1 mN p = 2) | nur probeweise gerechnet | I01-amplitude: Klasse p = 1 0.667 ± 0.086 (20/30), nicht durchgeführt 0.033 ± 0.033 (1/30), nicht zuordenbar 0.300 ± 0.084 (9/30); I01-frequenz: Klasse p = 1 0.733 ± 0.081 (22/30), nicht durchgeführt 0.100 ± 0.055 (3/30), nicht zuordenbar 0.167 ± 0.068 (5/30); I02-amplitude: Klasse p = 2 0.033 ± 0.033 (1/30), keine Abweichung an den Punkten I nachgewiesen 0.100 ± 0.055 (3/30), nicht durchgeführt 0.700 ± 0.084 (21/30), nicht zuordenbar 0.167 ± 0.068 (5/30); I02-frequenz: Klasse p = 2 0.033 ± 0.033 (1/30), keine Abweichung an den Punkten I nachgewiesen 0.333 ± 0.086 (10/30), nicht durchgeführt 0.333 ± 0.086 (10/30), nicht zuordenbar 0.300 ± 0.084 (9/30) | Zuordnungsregel und Kriterium offen (§12); Entwicklungsprüffall (a); I03 und I06 fehlen |
| K19 | Ebenen Z und H konsistent (u_c-Mediane 5 %, Raten 2 MC-SE) | nur probeweise gerechnet | rauschfrei gleich: True (max \|ΔN_k\| 1.4e-05 N); verrauscht 4 Kampagnen je Ebene: max \|Δu_c\|/u_c = 0.025 | nur N01-A4 auf einer Stufe; L0, L2, L4 nach Plan nicht gerechnet |
| K20 | Einfrieren von Katalog, Kriterien, Seeds und Prüfdatensatz vor Teil A | fachlich offen | Software-Prüfsatz gehasht (tests/fixtures/ap13_pruefsatz.json) | Einfrieren von Teil A ist nicht Gegenstand dieser Stufe; kein Einfrieren, keine Registrierung |
| K21 | P(H1 falsifiziert \| Hertz-Kontakt mit Residuum ≥ 2·Δ_rel) ≥ 0,8 | in diesem Modell nicht prüfbar | A07-hertz50: Klasse R1, r_max/Δ_rel = 0.50; P(falsifiziert) = 0.000 ± 0.000 (0/30) | kein Punkt ≥ 2·Δ_rel im Kontaktast mit diesem Szenario; berichtet nach K15 |
| H1Z | H1Z: P(falsifiziert \| exakt oder LTI) ≤ 0,05; Bestätigung und Prüfrate von c berichtet | nur probeweise gerechnet | N01-A4: P(H1Z falsifiziert) = 0.000 ± 0.000 (0/200), bestätigt 0.965 ± 0.013 (193/200); E04-kette: 0.000 ± 0.000 (0/30) | Grenzen von H1Z: Entwicklungsprüffall Δ_q/3; Prüfrate von c_H1Z nicht gesondert simuliert |
| E3 | E3: P(auffällig \| exakt) ≤ 0,05 und P(unauffällig \| exakt) ≥ 0,8; Raten bei 0,1°/0,3° Phasenversatz | fachlich offen | N03-ungleich: unauffällig 0.075 ± 0.042 (3/40), unbestimmt 0.925 ± 0.042 (37/40); A06-phase: auffällig 1.000 ± 0.000 (30/30); N01-A4: unauffällig 0.070 ± 0.018 (14/200), unbestimmt 0.930 ± 0.018 (186/200) | Schwellen, Prüfmenge und Rückfall von E3 offen (§12); Phasenversatzszenarien 0,1°/0,3° fehlen |
| Zuordnung | Zuordnung (A9.11): Raten falscher Klasse und „nicht zuordenbar“, auch Hertz und lastabhängige Kopplung | fachlich offen | I05-misch: Klasse p = 1 0.200 ± 0.073 (6/30), nicht durchgeführt 0.633 ± 0.088 (19/30), nicht zuordenbar 0.167 ± 0.068 (5/30); I02-amplitude: Klasse p = 2 0.033 ± 0.033 (1/30), keine Abweichung an den Punkten I nachgewiesen 0.100 ± 0.055 (3/30), nicht durchgeführt 0.700 ± 0.084 (21/30), nicht zuordenbar 0.167 ± 0.068 (5/30) | Kriterium der Zuordnung offen (§12: feste Anker oder Zuordnungsgrenze); Hertz und lastabhängige Kopplung als Zuordnungsszenarien fehlen |

Zählung der Status: geprüft: 1, nur probeweise gerechnet: 16, fehlt: 1, fachlich offen: 5, in diesem Modell nicht prüfbar: 1.

Keine Gesamtampel: Die Prüffälle sind unvollständig und die Kampagnenzahlen reduziert; kein Kriterium gilt damit als abgenommen.
