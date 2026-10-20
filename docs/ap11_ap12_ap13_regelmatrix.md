# Regelmatrix der Softwarestufe AP-11 bis AP-13

> **Regelstand 2026-11 (Auftrag des Autors vom 20.10.2026).** Die Tabelle unten gilt für die Profile AF-2026-11 und
> ENTW-2026-11, die Vorgabe der Software. Die neuen Regeln (Präfixe `ablauf.`, `g4.`, `e3.`, `harness.`, `planung.`,
> `p0.`) sind methodische Arbeitsfestlegungen; sie sind statistisch nicht kalibriert und experimentell nicht geprüft.
> Der historische Regelstand 2026-10 (Profile AF-2026-10 und ENTW-2026-10, Stand bis PR #23) steht unverändert in
> [`ap11_ap12_ap13_regelmatrix_2026-10.md`](ap11_ap12_ap13_regelmatrix_2026-10.md); der Code rechnet unter diesen
> Profilen wie damals.

Stand 16.10.2026 · Grundlage: Präregistrierung v2, Entwicklungsversion ([Hauptdokument](praeregistrierung_v2_entwurf.md),
[Anhang](praeregistrierung_v2_anhang.md)) im Stand `a1c9953` · Lizenz CC BY 4.0. *Nur Software und Simulation, keine
Messdaten, keine Festlegung.* Die Matrix ändert keine Regel der Präregistrierung, nicht A0 und nicht Tabelle F.

Maßgeblich ist der Text der Präregistrierung; der Plan AP-13 ([`plan_ap13_pipelinetest.md`](plan_ap13_pipelinetest.md))
gilt nur, soweit sein Anhang „Abgleich mit `main`“ ihn nicht überholt. Die Matrix wird aus dem Code erzeugt
(`python3 code/pcmms_auswertung regeln --matrix`, Quelle `code/pcmms_auswertung/regeln.py`); ein Test prüft, dass die
Tabelle unten mit dem Code übereinstimmt.

## Statusbegriffe

| Status | Bedeutung | Wirkung in der Software |
|---|---|---|
| arbeitsfestlegung | vorläufige Festlegung des Autors, in §12 so gekennzeichnet (§0) | gilt in beiden Profilen |
| regeltext | Regel des Entwurfs ohne Kennzeichnung als offen | gilt in beiden Profilen |
| festlegung | Zahlenwert aus Tabelle F, nicht als offen gekennzeichnet | gilt in beiden Profilen |
| entwicklungsprüffall | offene Entscheidung; für die Entwicklung ausdrücklich gewählter Prüffall (Testvariante oder Vorschlag des Entwurfs) | nur im Profil ENTW-2026-10; Profil-ID und Wert stehen in jedem Ergebnis; keine Festlegung |
| offen | offene Entscheidung ohne Wert | abhängige Ausgänge „nicht entscheidbar (Grund: Regel offen …)“ oder nur numerische Prüfgrößen |
| nicht_implementiert | genannte Option, in dieser Stufe nicht umgesetzt | wird im Ergebnis als nicht umgesetzt genannt |
| technisch | Umsetzungsdetail der Software ohne eigene Regelwirkung | dokumentiert; Klärung am Präreg-Text (Rückmeldung an AP-08) |

Profile: **AF-2026-10** enthält nur Arbeitsfestlegungen, Regeltext und Tabelle F; alles Offene bleibt offen (H2 und H3
sind dann nicht entscheidbar, H1Z, E3 und Zuordnung nur numerisch). **ENTW-2026-10** fügt die Entwicklungsprüffälle
hinzu. Verringerte Replikat- oder Kampagnenzahlen erzeugen ein abgeleitetes Profil `…+red(…)`; die normativen Zahlen
(10 000 Replikate, 10 000 Monte-Carlo-Ziehungen, 1000 Kampagnen) stehen daneben.

## Übernommene Arbeitsfestlegungen (Auftrag, Abschnitt 2)

| Gegenstand | Fundstelle | Status | Umsetzung |
|---|---|---|---|
| H1-Größen F_min − ⟨N⟩ (zum Laufmittel) und Re/Im N₁ … N₃, Summe und Zellen getrennt | §3, §4, A1 | regeltext | `h1.py` (Summe), `h1.py` mit Zellen (H1Z) |
| Δ_q = 0,25·D_q, Δ_rel,q = Δ_q, D der Harmonischen in Fassung B | §8.5, A8, §12 (I) | arbeitsfestlegung | `teil_b.py`, `h1.py` |
| Grenzen je Kampagne aus dem verrauschten ŷ⁰; Bewertung gegen die Wahrheit mit den Grenzen der rauschfreien Vorhersage | §12 Nr. 8, A9.11 | arbeitsfestlegung | `harness/` |
| Sensitivität Faktor 0,1 und Fassung A getrennt, ohne Ausgangswirkung | §8.5, §8.9, A9.9 | arbeitsfestlegung | `h1.py` |
| Äquivalenzlogik von H2 und H3 (keine Signifikanzlogik als Hauptverfahren) | §3, §9.3, §12 (I) | arbeitsfestlegung | `h2.py`, `h3.py` |
| gemeinsame Laufzahlbedingung P(H1 und H2 bestätigt \| exakt) ≥ 0,8 an der oberen 80-%-Grenze der Streuungen | §5.4, A9.2, §12 (I) | arbeitsfestlegung | `pilot.py`, `harness/planung.py` |
| Rauschbias b̂⁰ und b̂¹ getrennt mit Unsicherheit, dieselbe Korrektur bei c | §5.4, §8.3, A9.5 | regeltext | `harness/`, `h1.py` |
| c aus Kalibriersimulation, getrennte Prüfsimulation, Prüfrate > 0,069 → Poolen (kein verfehltes Kriterium) | §8.4, A8, A9.11 | regeltext | `harness/kalibrierung.py` |
| H2-Überdeckung 0,936; Intervalltyp und Rückfallkette als Entwicklungsprofil | §8.6, A9.6, §12 | festlegung / offen → entwicklungsprüffall | `zeltfit.py`, `h2.py`, `harness/` |
| Berichtsform: Ausgänge, Zusätze, Gründe aus §9.3/§9.4 | §9.3, §9.4, §12 (I) | arbeitsfestlegung | `h1.py`, `bericht.py` |
| M nach Konvention (b): Gewicht M·g, träge Masse M + m_L getrennt; keine erfundenen Messwerte | §3, §4, P0.2, §12 (I) | arbeitsfestlegung | `anpassung.py`, `h3.py` |
| H3-Eingänge nur aus P0.1–P0.5, nicht aus Kraftdaten der Einzelmodulläufe | §3 H3, §5.2, A9.7 | regeltext | `h3.py` (liest nur die Kalibrierung) |

## Offene Entscheidungen und Entwicklungsprüffälle

Offen nach §12 und in ENTW-2026-10 als Prüffall gewählt: δ_H2 (1°), δ_H3 (10 %), Relevanzgrenze von H3 (= δ_H3·|N̂|),
H2-Fenster (w = 6°, Mittelpunkt i), Spitzenlagenschätzer (stetiges Zelt), Intervalltyp und Rückfallkette (Fassung a)
mit Bezugswert der Überdeckung, Vollständigkeit bei H2 (a), Drift-Zusatz und Driftlogik (a), Grenzen von H1Z (a,
Δ_q/3), Schwellen, Prüfzahl, Rückfall, Prüfmenge und Form von E3, Regel, Auslöser und Kriterium der Zuordnung, Punkte I,
Einstellung 2 und s, Temperaturfenster G7 (a), Rauschmodelle, Zielfunktion der Laufzahlplanung, Nachweisform der
Phase-0-Schwellen und Klirrschwelle. Die Testwerte 1° und 10 % sind keine Festlegungen.

In beiden Profilen offen (keine Entwicklungswahl): Rückfall für H1, Lesart „H2 auch bei hoher Präzision entscheidbar“
(die Software berichtet die Größen aller drei Lesarten), Drift-Zusatz bei H2 (nicht eigens definiert), G2–G4 bei
Einstellung 2, S1/S2/S4 für L₁′–L₃′, zusätzliche Power-Bedingung der Laufzahl.

Nicht implementiert: H3 Fassung I, H1′/H2′, Paarläufe, Wiederaufnahme nach Eingriff, frühere Signifikanzlogik und Regel
vom 25.09.2026, übrige Sensitivitätsanalysen von A9.9, Neuberechnung von b̂ und c nach dem Datenschluss, Auswertung von
D2_K und Kabelschlaufe, Einzelzell-Liftoff mit Stoßdynamik.

## Befunde am Regeltext

Befunde mit möglicher Ergebniswirkung stehen mit Auswirkung und betroffenem Pfad in
[`ap11_ap12_ap13_software.md`](ap11_ap12_ap13_software.md), Abschnitt „Befunde“.

## Vollständige Matrix

<!-- MATRIX-ANFANG (erzeugt mit: python3 code/pcmms_auswertung regeln --matrix) -->
| Regel | Gegenstand | Fundstelle | Status | Wert im Entwicklungsprofil ENTW-2026-11 | Umsetzung |
|---|---|---|---|---|---|
| `verarbeitung.n_theta` | Stützstellen je Zyklus | §4, A1, A9.4 (4), Tab. F | festlegung | 2000 | stufe1 |
| `verarbeitung.interpolation` | Resampling je Zyklus | A9.4 (4) | regeltext | "linear" | stufe1 |
| `verarbeitung.filter` | Softwarefilter | §5.1, §8.1, A9.1, A9.4 (2) | regeltext | "keine" | stufe1 |
| `verarbeitung.zyklen` | nur vollständige Zyklen im Auswertefenster | A9.4 (3) | regeltext | "vollstaendig" | stufe1 |
| `verarbeitung.k_voll` | Zahl gespeicherter Harmonischer je Lauf (≥ k_max; ungebändert für (a)) | §5.3 (a), Plan 2.6 b | technisch | 60 | stufe1 |
| `verarbeitung.t_phi` | Einregelzeit der Phasen je Lauf | §5.4, §6 (T_φ) | technisch | "erster Zyklus nach Rampenende, ab dem alle Indexphasen bis Fensterende innerhalb max(4σⱼ, 0,1°) um das Fenstermittel liegen" | stufe1 |
| `g2.delta_phi_tol_grad` | Phasentoleranz δφ_tol | §9.1 G2, Tab. F | festlegung | 0.5 | gueltigkeit |
| `g2.sigma_tol` | Jittertoleranz σ_tol | §9.1 G2, Tab. F | festlegung | 3.0 | gueltigkeit |
| `g4.faktor` | Fünftelkriterium (Faktor der Schwelle im historischen Modus je Laufart und für Lⱼ) | §9.1 G4, Tab. F | festlegung | 3.0 | gueltigkeit, g4, teil_b |
| `g6.faktor` | Liftoff-Schwelle F_LO,c | §4, A1, Tab. F | festlegung | 5.0 | gueltigkeit |
| `g7.form` | Form des Temperaturfensters G7 | §9.1 G7, §12 Driftbehandlung | offen → entwicklungsprüffall | "a" | gueltigkeit |
| `g.einstellung2` | G2–G4 für Läufe bei Einstellung 2 | §9.1, §12 Läufe bei Einstellung 2 | offen | – | gueltigkeit |
| `s.l_strich` | S1, S2, S4 für L₁′–L₃′ | §9.2, §12 Läufe bei Einstellung 2 | offen | – | gueltigkeit |
| `h0.eps_faktor` | ε_ctrl = 3·σ̂_ref bzw. 3·σ̂_betr | §8.8, A9.8, Tab. F | festlegung | 3.0 | gueltigkeit |
| `h0.alarm_faktor` | Nullpunktalarm 3·√(4/3)·σ̂_ref | §8.8, Tab. F | festlegung | 3.4641016151377544 | gueltigkeit |
| `h0.referenzlaeufe_min` | Referenzläufe der Phase 0 | P0.7, Tab. F | festlegung | 42 | gueltigkeit |
| `h0.sammeltest` | Nullkontroll-Sammeltest und Wortregel | §8.8, A9.8, §12 Wortlaut | arbeitsfestlegung | {"alpha": 0.05, "vermerk": "Einzellauftoleranz, keine Äquivalenzgrenze für das Mittel", "aussagen": ["Unterschied nachgewiesen", "kein Unterschied nachgewiesen, Gleichheit nicht nachgewiesen"]} | gueltigkeit |
| `s3.c_S` | S3-Schwelle c_S = t(1 − 0,05/42; n₀ⱼ − 1) | §9.2 S3, A8 | regeltext | 42 | gueltigkeit |
| `h1.alpha` | α je Familie | §3, §8.4, Tab. F | festlegung | 0.05 | h1, teil_b |
| `h1.groessen` | H1-Größen | §3 H1, §4 | regeltext | ["F_min − ⟨N⟩", "Re/Im N₁", "Re/Im N₂", "Re/Im N₃"] | h1, teil_b |
| `h1.faktor` | Äquivalenzgrenze Δ_q = Faktor·D_q | §8.5, §12 (I), Tab. F | arbeitsfestlegung | 0.25 | h1, teil_b |
| `h1.d_fassung` | D für Re/Im N_k | §8.5, A8, §12 (I) | arbeitsfestlegung | "B" | h1, teil_b |
| `h1.delta_rel` | Relevanzgrenze Δ_rel,q | §8.5, A8, §12 (I) | arbeitsfestlegung | "gleich_delta_q" | h1, teil_b |
| `h1.sensitivitaet` | Sensitivitätsvarianten (ohne Ausgangswirkung) | §8.5, §8.9, A9.9 | arbeitsfestlegung | {"faktor": 0.1, "fassung_A": true, "c_B": true} | h1, teil_b |
| `h1.grenzen_quelle` | D_q, Δ_q, Δ_rel als Punktwert aus ŷ⁰ | §8.5, A9.11, §12 (I) | arbeitsfestlegung | "yhat0_teil_b" | h1, teil_b |
| `h1.tost` | PB1: TOST mit t(0,95; ν_eff), IUT gegen ŷ⁰ und ŷ¹, ohne „kein |z| > c“ | §8.5, A8, Tab. F | arbeitsfestlegung | 0.95 | h1, teil_b |
| `h1.vollstaendigkeit` | Bestätigung nur bei 21 auswertbaren Punkten | §9.3 | regeltext | 21 | h1, teil_b |
| `h1.mindesteffekt` | |r⁰| − c·u⁰ > Δ_rel und |r¹| − c·u¹ > Δ_rel, gleiches Vorzeichen | §8.5, §9.3 | regeltext | "beide_gleiches_vorzeichen" | h1, teil_b |
| `h1.c_quelle` | kritischer Wert c von H1 | §8.4, A9.3 Nr. 10 | regeltext | "teil_b" | h1, teil_b |
| `h1.c_quantil` | Quantil von max|z⁰| | §8.4 | regeltext | 0.95 | h1, teil_b |
| `h1.c_pruefschwelle` | Prüfrate über 0,069 → gepooltes Quantil | §8.4, A8, Tab. F | festlegung | 0.069 | h1, teil_b |
| `h1.c_rauschmodelle` | Rauschmodelle und Wahl des Quantils für c | §8.4, §12 Rauschmodelle | arbeitsfestlegung | "a" | harness.kalibrierung |
| `h1.bias` | Rauschbias b̂⁰, b̂¹ getrennt mit u(b̂); dieselbe Korrektur in c | §5.4, §8.3, A9.5 | regeltext | "getrennt" | h1, teil_b |
| `h1.bias_u` | u(b̂): MC-Fehler und halbe Spannweite über die Rauschmodelle (Rechteck) | A9.5, Tab. F | festlegung | "rechteck" | h1, teil_b |
| `h1.rueckfall` | Rückfall für H1 bei verfehlten Raten | §12 Rückfall für H1 | offen | – | h1, teil_b |
| `h1.zusaetze` | Wortlaut der Zusätze | §9.3, §9.4, §12 Wortlaut | arbeitsfestlegung | {"bestaetigt": "Abweichung nachgewiesen, innerhalb der Äquivalenzgrenze", "nicht_entscheidbar": "Abweichung nachgewiesen, Relevanz offen", "drift": "Drift der Einzelmodulbasis"} | h1, teil_b |
| `h1.gruende` | Gründe für „nicht entscheidbar“ | §9.3, §9.4, §12 Wortlaut | arbeitsfestlegung | ["Präzision", "Graubereich", "Drift", "Datenlage", "Verfahren"] | h1, teil_b |
| `h1.grund_zuordnung` | Zuordnung des Grundes je Test und Rangfolge | §9.4 | technisch | "Datenlage > Verfahren > Drift > Graubereich > Präzision; Präzision: t_eq·u ≥ Δ_q, Graubereich sonst" | h1, teil_b |
| `h1.groesste_abweichung` | Auswahl der „größten Abweichung“ für die Vertrauensgrenzen | §9.3 | technisch | "größtes min(∣r⁰∣ − c·u⁰, ∣r¹∣ − c·u¹)/Δ_q unter den Tests mit nachgewiesener Abweichung" | h1, teil_b |
| `h1.grenzfall` | u_c = 0 (rauschfrei) | — | technisch | "u_c ≤ 1e-14·Skala gilt als null: Intervall entartet, z = 0 bei ∣r∣ ≤ 1e-14·Skala, sonst ±∞" | h1, teil_b |
| `drift.zusatz` | Definition des Drift-Zusatzes | §9.3, §12 Driftbehandlung | offen → entwicklungsprüffall | "a" | h1 |
| `drift.logik` | Wirkung nachgewiesener Drift auf den Ausgang | §9.3, §12 Driftbehandlung | offen → entwicklungsprüffall | "a" | h1 |
| `bootstrap.B` | Bootstrap-Replikate je Anteil | §8.3, A9.5, Tab. F | festlegung | 10000 | bootstrap |
| `bootstrap.varianz` | Varianz der Bootstrap-Replikate | §8.3, A9.5 | technisch | "Stichprobenvarianz mit ddof = 1" | bootstrap |
| `bootstrap.ziehung` | Indexmatrizen und Ziehreihenfolge | Plan AP-13 2.6 c | technisch | "SeedSequence(seed).spawn: A_i in Listenreihenfolge, B¹_1…B¹_3, H3, H4, danach E3, Einstellung 2" | bootstrap |
| `h1z.grenzen` | Grenzen Δ_c,q, Δ_c,rel,q von H1Z | §8.5, §12 Grenzen von H1Z | offen → entwicklungsprüffall | "a" | h1 |
| `h1z.c_quelle` | kritischer Wert von H1Z (441 Tests) | §8.4 | regeltext | "teil_b" | h1 |
| `h2.logik` | Entscheidungslogik von H2 | §3, §8.6, §9.3, §12 (I) | arbeitsfestlegung | "aequivalenz" | zeltfit, h2 |
| `h2.niveau` | Niveau der H2-Intervalle | §8.6, §12 (I), Tab. F | arbeitsfestlegung | 0.95 | zeltfit, h2 |
| `h2.ueberdeckung` | Überdeckungsschwelle | §8.6, A9.6, Tab. F | festlegung | 0.936 | zeltfit, h2 |
| `h2.replikate` | Bootstrap-Replikate H2 | §8.6, A9.6 | festlegung | 10000 | zeltfit, h2 |
| `h2.suchschritt_grad` | Suchschritt des Zeltfits | A9.6, Tab. F | festlegung | 0.001 | zeltfit, h2 |
| `h2.gleichstand` | Gleichstand im Zeltfit | A9.6 | regeltext | "kleinstes_phi" | zeltfit, h2 |
| `h2.rasterursprung` | Ursprung des 0,001°-Rasters | A9.6 „über [min W, max W]“ | technisch | "kleinste_abszisse" | zeltfit, h2 |
| `h2.delta_grad` | δ_H2 (Äquivalenz- und Relevanzgrenze) | §3, §8.6, §12 Grenzen von H2 und H3 | offen → entwicklungsprüffall | 1.0 | zeltfit, h2 |
| `h2.w_grad` | Halbbreite w des Fitfensters | §8.6, A9.6, §12 H2-Fitfenster | offen → entwicklungsprüffall | 6.0 | zeltfit, h2 |
| `h2.mittelpunkt` | Mittelpunkt des Fitfensters | A9.6, §12 H2-Fitfenster | offen → entwicklungsprüffall | "i" | zeltfit, h2 |
| `h2.schaetzer` | Schätzer der Spitzenlage | §8.6, §12 Schätzer | offen → entwicklungsprüffall | "zelt" | zeltfit, h2 |
| `h2.intervallkette` | Intervalltyp und Rückfallkette | §8.6, A9.6, §12 Intervall von H2 | offen → entwicklungsprüffall | "a" | zeltfit, h2 |
| `h2.ueberdeckung_bezug` | Bezugswert der simulierten Überdeckung | §8.6, §12 Intervall von H2 | offen → entwicklungsprüffall | "schaetzer_rauschfrei" | zeltfit, h2 |
| `h2.vollstaendigkeit` | Vollständigkeit bei H2 | §9.3, §12 Vollständigkeit | offen → entwicklungsprüffall | "a" | zeltfit, h2 |
| `h2.lesart_entscheidbar` | Lesart „H2 auch bei hoher Präzision entscheidbar“ | A9.11, §12 | offen | – | zeltfit, h2 |
| `h2.drift_zusatz` | Drift-Zusatz bei H2 | §9.3, §12 Driftbehandlung | offen | – | zeltfit, h2 |
| `h2.biaskorrektur` | Rauschbias im Zeltfit | §5.4, §8.6 | technisch | "keine" | zeltfit, h2 |
| `h2.gleichstand_toleranz` | Toleranz der Gleichstandsregel im Zeltfit | A9.6 (nennt keine Toleranz) | technisch | "RSS ≤ RSS_min·(1 + 10⁻⁹) + 10⁻¹²·SST + 10⁻²⁸·n·max F²" | zeltfit, h2 |
| `h2.quantil` | Quantildefinition der Bootstrap-Intervalle | §8.6, A9.6 | technisch | "numpy „linear“" | zeltfit, h2 |
| `h2.replikate_gemeinsam` | Replikate von H2 und E3 | A9.6, A9.13, Plan 2.6 c | technisch | "Zeilen der Bootstrap-Indexmatrizen (B_H2 = B_E3 = B)" | zeltfit, h2 |
| `h3.logik` | Entscheidungslogik von H3 | §3, §8.5, §9.3, §12 (I) | arbeitsfestlegung | "aequivalenz" | h3 |
| `h3.delta` | δ_H3 | §3, §8.5, §12 Grenzen von H2 und H3 | offen → entwicklungsprüffall | 0.1 | h3 |
| `h3.relevanz` | Relevanzgrenze von H3 | §3, §8.5, §12 | offen → entwicklungsprüffall | "gleich_delta" | h3 |
| `h3.fassung` | Fassung K oder I | §8.7, §12 (II) | offen → entwicklungsprüffall | "K" | h3 |
| `h3.eingaenge` | Eingänge nur aus P0.1–P0.5 | §3 H3, §5.2, A9.7 | regeltext | "kalibrierung" | h3 |
| `h3.mc` | Monte-Carlo-Ziehungen | A9.7, Tab. F | festlegung | 10000 | h3 |
| `h3.m` | Testzahl der Familie | §8.4, A8 | regeltext | 18 | h3 |
| `h4.m` | Testzahl (einseitig) | §8.4, A8 | regeltext | 23 | h4 |
| `h4.aufnahme` | Aufnahme in V: |γ̂₁| ≥ (c₄ + 1,645)·u_c,erw(γ₁) | §3 H4, §8.5 | regeltext | 1.645 | h4 |
| `e3.schwellen` | Schwellen von E3 (0,1°, q_tol) | §8.10, §12 Schwellen von E3 | arbeitsfestlegung | {"phase_grad": 0.1, "q_tol": 0.00058} | kontrollen, e3_grenzen |
| `e3.pruefzahl` | Zahl der E3-Prüfungen (Bonferroni) | A9.13, §12 | arbeitsfestlegung | 43 | kontrollen, e3_grenzen |
| `e3.rueckfall` | Rückfall von E3 | §8.10, A9.11, §12 | arbeitsfestlegung | "je_pruefgroesse" | kontrollen, e3_grenzen |
| `e3.pruefmenge` | Prüfmenge von E3 | §12 Schwellen von E3 | arbeitsfestlegung | "schnitt21_triphasik" | kontrollen, e3_grenzen |
| `e3.e3b_form` | E3b als Differenz oder absolut | §8.10, §12 | arbeitsfestlegung | "differenz" | kontrollen, e3_grenzen |
| `zuordnung.regel` | Regel der Zuordnung | §8.10, A9.13, §12 Zuordnung | offen → entwicklungsprüffall | "a" | kontrollen |
| `zuordnung.ausloeser` | Auslöser der Zuordnung | §8.10, §12 Zuordnung | offen → entwicklungsprüffall | "a" | kontrollen |
| `zuordnung.kriterium` | Kriterium der Zuordnung (A9.11) | A9.11, §12 Zuordnung | offen → entwicklungsprüffall | "a" | kontrollen |
| `zuordnung.s_formel` | Kraftskala s der Zuordnung | §8.10, A9.13 | technisch | "s = Σⱼ∣N̄′₁⁽ʲ⁾∣/Σⱼ∣N̄₁⁽ʲ⁾∣ aus den Einzelmodulläufen" | kontrollen |
| `zuordnung.m_fest` | m = 6·N_I fest bei Ausfällen | A9.13, §12 Läufe bei Einstellung 2 | offen → entwicklungsprüffall | "fest" | kontrollen |
| `punkte_I` | Punkte I | §5.5, §12 Punkte I | offen → entwicklungsprüffall | [116.0, 120.0, 124.0] | kontrollen, generator |
| `einstellung2.art` | Art von Einstellung 2 | §5.5, §12 (II) | offen → entwicklungsprüffall | "beide" | generator |
| `einstellung2.s` | Kraftskala s | §5.5, §12 Einstellung 2 | offen → entwicklungsprüffall | 0.5 | generator |
| `kontaktast.reserve` | Mindestabstand 25 % der statischen Zelllast | §5.3 (a), Tab. F | festlegung | 0.25 | teil_b, auswertung |
| `kontaktast.resonanz` | Resonanzabstand k·f ≤ f₁/2 | §5.3 (b), A6, Tab. F | festlegung | 0.5 | teil_b, auswertung |
| `a6.interpolation` | Abtastrate (π·k_max·f/f_s)²/2 ≤ 10⁻³ | §5.1, A6, Tab. F | festlegung | 0.001 | generator.ebene_z |
| `planung.bedingung` | P(H1 und H2 bestätigt | exakt) ≥ 0,8, Streuungen an der oberen 80-%-Grenze | §5.4, A9.2, §12 (I) | arbeitsfestlegung | 0.8 | pilot, harness.planung |
| `planung.faustregel` | n_min ≥ (3·1°/(SNR·δ_H2))², notwendig, nicht hinreichend | §5.4, A9.2 | regeltext | 3.0 | pilot, harness.planung |
| `planung.zielfunktion` | Zielfunktion der Laufzahlplanung | §5.4, §12 Messzeit | offen → entwicklungsprüffall | "a" | pilot, harness.planung |
| `planung.power` | zusätzliche Power-Bedingung (Laufzahl von H1) | §5.4, §12 Rauschmodelle … | offen | – | pilot, harness.planung |
| `planung.n0_min` | mindestens 20 Einzelmodulläufe je Modul | P0.8, §5.4, Tab. F | festlegung | 20 | pilot, harness.planung |
| `planung.reserve` | Reserve r = ⌈n_min·p̂/(1 − p̂)⌉ + 2 | §5.4, Tab. F | festlegung | 2 | harness.reserve, harness.planung |
| `planung.auslegungsgrenze` | Startwert Δ_q/5,01 (ν → ∞) bzw. Δ_q/5,21 (ν = 19) | §8.5, A8 | regeltext | [5.012, 5.208] | pilot, harness.planung |
| `p0.nachweisform` | Nachweisform der Phase-0-Schwellen | §5.2, A9.2, §12 Nachweis und Folge | offen → entwicklungsprüffall | "beide" | anpassung |
| `p0.klirr_faktor` | Klirrkriterium und P0.12 (Faktor auf u_c,erw) | §5.2, §12 Schwelle des Klirrkriteriums | offen → entwicklungsprüffall | 0.3 | anpassung |
| `p0.u_delta_delta_grad` | Anforderung u(Δδⱼ) ≤ 0,1° | P0.5, Tab. F | festlegung | 0.1 | anpassung |
| `p0.4.gewichtung` | Kohärenzgewichtung der 1-FG-Anpassung | §5.2 P0.4, A9.2, §12 Werkzeug 4 | technisch | "Gewicht 2·n_Mittel·γ²/((1 − γ²)·∣T∣²) je Real- und Imaginärteil" | anpassung |
| `p0.4.band` | Anpassungsband der 1-FG-Anpassung | §5.2 P0.4, A9.2 „festgelegtes Frequenzband“ | technisch | "Eingabe" | anpassung |
| `p0.4.kohaerenz_min` | Mindestkohärenz einer Frequenzlinie | §5.2 P0.4, Werkzeug 4 | technisch | 0.5 | anpassung |
| `p0.4.linearitaet` | Linearität zweier Amplituden | §5.2 P0.4, A9.2 „gleich innerhalb der Unsicherheit“ | technisch | "χ²-Test der Übertragungsdifferenz p ≥ 0,01 und ∣z∣ < 3 für f_n, ζ" | anpassung |
| `p0.4.modellordnung` | Zahl der Moden aus den Zellkanälen | §5.2 P0.4, A1 (f₁, f_m, ζ_m) | technisch | "gemeinsame Pole, zusätzliche Mode bei F-Test p ≤ 0,01; Moden außerhalb des Bands nicht bestimmt" | anpassung |
| `p0.gf_modell` | Modell der Kraftkette G_F aus dem Brückensimulator | §5.2 P0.1, A9.7, Werkzeug 4 | technisch | "g·e^{−i2πfτ}/(1 + if/f_tp); ohne nachweisbaren Tiefpass g·e^{−i2πfτ}" | anpassung |
| `verarbeitung.kennlinie` | Umrechnung der Rohwerte in Stufe 1 | A9.4 (1) „statische Kalibrierung je Zelle“ | technisch | "linear" | stufe1 |
| `M.konvention` | Bestimmung von M | §3, §4, P0.2, §12 (I) | arbeitsfestlegung | "b" | anpassung |
| `rauschmodelle` | Rauschmodelle (Liste in Teil A oder Teil B) | §12 Rauschmodelle …, A9.5 | arbeitsfestlegung | {"standard": "strukturmodell_phase0", "eingebettet": "familienanpassung", "sensitivitaet": "benannte_szenarien", "bootstrap": "optional"} | generator.rauschen, pilot |
| `harness.c_vollstaendig` | Kampagnen für das Quantil von c | §8.4 „über die 147 korrelierten Tests“ | arbeitsfestlegung | "menge_A" | harness |
| `harness.c_pool` | gepooltes Quantil bei Prüfrate > 0,069 | §8.4 | technisch | "95-%-Quantil der vereinigten max∣z⁰∣ beider Simulationen; Prüfsimulation danach neu ausgewertet" | harness |
| `harness.ueberdeckung_beide` | Überdeckung gegen ŷ⁰ und ŷ¹ | §8.6, A9.6 | technisch | "ein Intervalltyp gilt, wenn beide Überdeckungen die Schwelle erreichen" | harness |
| `harness.planung_rauschen` | Rauschmodell der Planungssimulation | §5.4, A9.2 | arbeitsfestlegung | "phase0_modell" | harness |
| `harness.seeds` | Seeds der Kampagnen | Plan 4.3 | technisch | "unterseed(Basis, Rolle, Szenario, Stufe, i)" | harness |
| `ni.fassung_I` | H3 Fassung I (Betriebsimpedanz) | §8.7, §12 (II) | nicht_implementiert | – | – |
| `ni.gespiegelt` | H1′/H2′ am gespiegelten Schnitt | §3, §6 | nicht_implementiert | – | – |
| `ni.paarlaeufe` | Paarläufe | §5.5, §12 Paarläufe | nicht_implementiert | – | – |
| `ni.wiederaufnahme` | Wiederaufnahme nach mechanischem Eingriff | §9.2, §12 | nicht_implementiert | – | – |
| `ni.signifikanzlogik` | frühere Signifikanzlogik von H2/H3 und Regel vom 25.09. | A0, §12 (I) | nicht_implementiert | – | – |
| `ni.sensitivitaet_rest` | übrige Sensitivitätsanalysen von A9.9 | A9.9 | nicht_implementiert | – | – |
| `ni.neuberechnung` | Neuberechnung von b̂ und c nach dem Datenschluss | §12 Rauschmodelle … | nicht_implementiert | – | – |
| `ni.d2k` | Auswertung von D2_K und Kabelschlaufe (P0.3) | §5.2 P0.3 | nicht_implementiert | – | – |
| `ni.einzelzell_dynamik` | Einzelzell-Liftoff mit Stoßdynamik (nichtlineares 3-FG-Modell) | Plan 2.2 (c) | nicht_implementiert | – | – |
| `ablauf.fassung` | Fassung des zustandsbehafteten Ablaufs | §6, §8.8, §9.2, A9.12 | arbeitsfestlegung | "ablauf-4" | ablauf, auswertung |
| `ablauf.reihenfolge` | Reihenfolge sofortiger Folgeläufe (A1 + Z1) | §9.2, A9.12 | arbeitsfestlegung | "R₁ zuerst; feststehender Verstoß → R₂, X′, R₃ geschlossen, auch bei ungültigem X′; danach übrige sofortige Wiederholungen, die zuletzt ausgelöste zuerst; ein sofortiger Halt hat Vorrang" | ablauf, auswertung |
| `ablauf.halt` | Ausstehende Folgeläufe und unvollständige Klammer bei Halt (H1 + K1) | §9.2, A9.12 | arbeitsfestlegung | "ausstehende sofortige Folgeläufe verworfen und protokolliert; G1-Fall ohne gemessenes X′ nach dem W-Satz als neue Folge R₂, X′, R₃; unvollständige Klammer: S1 nicht prüfbar, keine Sonderwiederholung, Platz fehlt" | ablauf, auswertung |
| `ablauf.wiederaufnahme_alarm` | Alarm im Kontrollsatz der Wiederaufnahme (N7) | §9.2, §8.8 | arbeitsfestlegung | "S1–S4; einzelne S3-Überschreitung und einzelner Nullpunktalarm werden wie sonst wiederholt, der reproduzierte Alarm hält an" | ablauf, auswertung |
| `ablauf.bezugseroeffnung` | Neuer Bezug nach einem Nullpunkthalt | §8.8, §9.2, A9.12 | arbeitsfestlegung | {"ausloeser": ["S1 reproduzierter Nullpunktalarm", "Nullpunktalarm (technische Grenze)"], "lauf": "gesonderter Referenzlauf vor dem W-Satz, ohne Alarmvergleich gegen das verworfene R₀", "grenze_wiederholungen": 2, "danach": "Halt „Bezugseröffnung“ (verbraucht eine Wiederaufnahme)", "ersatz": "letzter gültiger Aufwärmlauf bei Tageswechsel"} | ablauf, auswertung |
| `ablauf.aufwaermen` | Aufwärmen nach einer Wiederaufnahme | §6, §9.2 | arbeitsfestlegung | "nur_tageswechsel" | ablauf, auswertung |
| `ablauf.tageswechsel` | Tageswechsel bei der Wiederaufnahme in der Simulation | §6 | technisch | "Ereignisfeld tageswechsel; fehlt es, gilt Zeitpunkt − Halt ≥ tag_pause des Plans" | ablauf, auswertung |
| `p0.anordnung` | Anordnung der Referenzläufe in Phase 0 (P0.7) | P0.7, A9.2 | arbeitsfestlegung | {"min_referenz": 42, "max_abstand": 12, "verteilung": "gleichmaessig_mit_anfang_und_ende"} | generator.kampagne |
| `p0.laufgroessen` | Laufgrößenmodell aus Phase 0 (Schätzer d0) | §5.4, A9.2, A9.3 | arbeitsfestlegung | {"amplitude_phase": "kohärente Projektion der Lⱼ-Abweichungen (σ_a,j, σ_δ,j, ν = n₀ⱼ − 1)", "versatz": "Laufmittel der Indexphasen der gültigen Piloten (σ_off,j)", "boden": "Referenzläufe"} | laufgroessen, pilot, teil_b |
| `g4.verfahren` | Standardisierung der Fünftelschwelle für Konfigurationen | §9.1 G4, A9.2 | arbeitsfestlegung | "b_plus" | gueltigkeit, g4, teil_b |
| `g4.b_plus` | Bestandteile von B+ | §9.1 G4 | arbeitsfestlegung | {"mischung": "Laufversatz, Phasenrest, Modulamplitude", "piloten": "dieselbe Mischung für s̄_P", "knick": "Maximum über ±u(Δδⱼ)", "ziehungen": "normiert", "schwelle": "quantil", "untergrenze_faktor": 3.0} | gueltigkeit, g4, teil_b |
| `g4.zielrate` | Arbeitsziel der Fehlausschlüsse je Konfiguration und Lauf | A9.11 | arbeitsfestlegung | 0.015 | gueltigkeit, g4, teil_b |
| `g4.lj` | G4 an Einzelmodul-Kontrollläufen | §9.1 G4 | arbeitsfestlegung | {"schwelle": "n_abhaengig", "vergleich": "pooling"} | gueltigkeit, g4, teil_b |
| `e3.grenzen` | Konstruktion der E3-Grenzen (Option B) | §8.10, A9.13 | arbeitsfestlegung | {"e3a": "t_quantil_gefaltet", "e3b": "rice_kappa_lambda_max", "nu": "min_n_minus_1", "nu_min": 5, "unauffaellig": "t_0.95"} | kontrollen, e3_grenzen |
| `e3.zusatzszenarien` | Zusätzliche E3b-Prüffälle | A9.11 | arbeitsfestlegung | [0.005, 0.01] | kontrollen, e3_grenzen |
| `harness.wiederaufnahme` | Simulierte Wiederaufnahme fortsetzbarer Halte | §9.2, A9.11 | arbeitsfestlegung | {"W": 3, "T_UA": "Teil B", "T_UA_entwicklung_s": 1800.0, "ereignis": "Ursachenanalyse ohne Befund, kein Eingriff, kein Apparaturfehler"} | harness.kette, ablauf |
| `harness.mengen` | Bezugsmengen der Simulationen | §5.4, §8.4, §8.6, A9.11 | arbeitsfestlegung | {"G": "alle begonnenen Kampagnen der Rolle, einschließlich endgültig beendeter", "A": "abgeschlossen (auch nach Wiederaufnahme), ŷ¹ gültig, alle benötigten Prüfgrößen endlich"} | harness.mengen, harness.kalibrierung |
| `harness.nachziehen` | Sollzahl der Auswertungsmenge und Nachziehen | §8.4, §8.6 | arbeitsfestlegung | {"soll_A": 1000, "versuchslimit_faktor": 1.5} | harness.mengen |
| `planung.reserve_ziel` | Bedingung für die Reserve r | A9.2 (v) | arbeitsfestlegung | {"anteil": 0.95, "nenner": "nicht_endgueltig_beendet", "zusatz_max": 10} | harness.reserve, harness.planung |
| `planung.zeitformel` | Terme der Zeitformel | §5.3 (c), §12 Messzeit | arbeitsfestlegung | ["Läufe", "Wiederholungen", "Kontrollsatz der Wiederaufnahme", "Bezugseröffnung", "Ursachenanalyse T_UA", "Aufwärmen bei Tageswechsel"] | harness.reserve |
| `planung.obere_grenze` | Obere 80-%-Grenze eines mehrteiligen Rauschmodells | §5.4, A9.2 | arbeitsfestlegung | "je_komponente_gemeinsamer_boden" | pilot, harness.planung |
| `planung.teil_b_werte` | Teil-B-Werte aus Punktschätzern nach der Planung | §8.4, A9.2, A9.11 | arbeitsfestlegung | "punktschaetzer" | pilot, harness.planung |
| `p0.strukturmodell` | Regularisierung und Annahmen des Strukturmodells aus Phase 0 | §5.4, A9.2, A9.11 | technisch | {"punkt": "√max(0, s² − Boden), abgeschnitten bei null", "obere_grenze": "√max(0, s²·ν/χ²₀,₂(ν) − Boden) je Komponente; Boden von ⟨N⟩: ein Faktor für alle Laufarten", "nicht_identifizierbar": "0, ausdrücklich benannt, als benannte Sensitivität geführt", "rest": "orthogonaler Rest je Modul und Harmonischer als Vielfaches des Zellbodens, laufweise", "kombination": "Streuung der Kombinationsläufe wie in den Lⱼ-Läufen (Übertragungstest an den Piloten)", "boden": "weiß über die Zyklen (σ ∝ 1/√T_a)"} | generator.phase0_modell, harness.planung |
| `rauschmodelle.sensitivitaeten` | Benannte Sensitivitätsszenarien des Rauschmodells mit festen Stärken | §12 Rauschmodelle, A9.11 | technisch | {"version": "sensitivitaeten-0.1", "szenarien": {"jitter_farbig": "farbiger Jitter: AR(1) über die Zyklen mit Koeffizient 0,9", "jitter_korreliert": "Jitter der Module 2 und 3 je Zyklus korreliert (ρ = 0,5)", "jitter_lastabhaengig": "Jitter der Kombinationsläufe × (1 + 0,5·q₁(φ))", "phasendrift_lauf": "lineare Indexphasendrift 0,1° über den Kombinationslauf (Module 2, 3)", "kombination_doppelt": "Amplituden- und Phasenstreuung der Kombinationsläufe doppelt so groß wie in Lⱼ", "laufzeit_gemeinsam": "gemeinsame Laufzeitschwankung der Kette statt modulweisem δ in den Kombinationsläufen", "amplitude_doppelt": "Amplitudenstreuung je Modul doppelt so groß (alle Laufarten)", "nullpunkt_diffusion": "Zufallspfad des Nullpunkts mit D·13·T_Lauf = σ²_m,Σ (Leave-one-out-Varianz am Abstand von P0.7 etwa verdoppelt)", "drift_phase1": "Drift der Einzelmodulbasis zwischen Phase 0 und Phase 1: +0,1 % Amplitude aller Module in Phase 1"}} | generator.phase0_modell, harness.planung |
<!-- MATRIX-ENDE -->
