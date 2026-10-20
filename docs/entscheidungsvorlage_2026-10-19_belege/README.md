# Belege zur Entscheidungsvorlage vom 19.10.2026

Stand der Zusammenstellung: 20.10.2026. Bezug: `docs/entscheidungsvorlage_2026-10-19.md` (im Folgenden „Vorlage“),
Abschnitte 1, 3, 4, 5, 6 und 8.

## Zweck

Die Vorlage stützt sich auf Rechnungen, deren Skripte und Ausgaben bisher nur im Scratch-Ordner der Sitzung lagen,
und auf Checkpoint-Befunde, die nur flüchtig unter `/tmp` liegen. Dieses Paket legt die Skripte mit ihren Ausgaben
im Repository ab, damit jede als „gerechnet“ oder „gerechnet in der Nachprüfung“ gekennzeichnete Zahl einem Skript,
einer Ausgabe und einer Herkunft zugeordnet werden kann. Es ändert keine Regel und keinen Code des Repositorys.

Alle Rechnungen sind Rechnungen auf Ebene der Teststatistik (analytisch, Quadratur oder Monte Carlo) oder Zählungen
in gespeicherten Dateien. Es wurde keine Kampagne mit der Codekette von Werkzeug 8 gerechnet (Abschnitt „Grenzen“).

## Aufbau

| Ordner | Inhalt | Vorlage |
|---|---|---|
| `eps_ctrl/` | ε_ctrl, G1-Fälle, R₁, X′ und Halte je Kampagne der 30 Ablaufkampagnen; Teststatistikmodell der S1-Halte | 1.1, 1.2, 3.1, 3.2, 3.5, 5.2, 5.4, 8 |
| `a8_wege/` | S1-Wege nach A8 einschließlich des reproduzierten Alarms am R₁ | 1.2, 3.1, 8 |
| `e3b/` | Randgültigkeit der E3-Grenzen, rekonstruierte Nachzählung | 4.1–4.3, 8 |
| `freiheitsgrade/` | effektive Freiheitsgrade von σ̂_ref, A8-Rate p1 marginal über σ̂_ref | 1.4, 3.1, 3.4, 5.2, 8 |
| `kosten/` | Kernstunden der Zähldiagnosen und der Neukalibrierung, Trennschärfe | 2.5, 3.5, 5.5, 6, 8 |
| `bezugsmengen/` | Halte gegen Auswertbarkeit, Prüf- und Überdeckungsschwelle, Reserve | 3.1, 3.3 |
| `laufphase/` | Laufphasenstreuung, D_F an S120, Faktoren d2 | 2.1, 2.2, 5.1, 5.2 |
| `g4_lj/` | G4 an Einzelmodul-Kontrollläufen (Option F) | 2.2, 3.1 |

Herkunftsangaben: „Nachprüfung 1 … 7“ sind die sieben Prüfer aus Vorlage Abschnitt 8 (1 ε_ctrl, 2 G4 an Lⱼ,
3 Halt an X′ und Wiederaufnahme, 4 Bezugsmengen, 5 E3b-Grenze und Nachzählung, 6 Laufphasenstreuung, 7 Reihenfolge
und Rechenbudget). „Gegenprobe“ sind die unabhängigen Nachrechnungen des Hauptbearbeiters (Abschnitt 8,
„Gegenproben des Hauptbearbeiters“). „Erste Fassung“ sind Skripte, die vor den Nachprüfungen im Scratch-Ordner
entstanden sind; ein Urheber ist dort nicht vermerkt. „Lesebericht c“ ist der Lesebericht zu E3 vom 18.10.2026, der
die Skripte als eigene Rechnungen zitiert; „Kritik“ ist die Kritik zur ersten Fassung.

Stand der Ausgabe: **neu** = für dieses Paket neu erzeugt (Laufzeit gemessen); **neu, =Quelle** = neu erzeugt und
bytegleich mit der Ausgabe im Scratch-Ordner; **übernommen** = aus dem Scratch-Ordner kopiert, nicht neu gerechnet;
**übernommen, geprüft** = kopiert und zur Kontrolle in einer Scratch-Kopie neu gerechnet, bytegleich.

## Übersicht: Beleg → Vorlage → Skript → Ausgabe → Herkunft

### eps_ctrl

| Beleg | Vorlage | Skript | Ausgabe | Herkunft | Stand |
|---|---|---|---|---|---|
| Tabelle ε_ctrl, u, G1-Fälle, R₁, R₂, X′, R₃, Halt je Kampagne (30 Kampagnen), Spearman ε~G1 −0,81, ε~X′ −0,65 | 3.1 „Halte nach ε_ctrl“, 3.5 | `tabelle_eps_halte.py` | `eps_ctrl_halte_je_kampagne.csv`, `tabelle_eps_halte.out` | erste Fassung | CSV neu, =Quelle; .out neu |
| unabhängige Nachzählung mit SHA-Prüfung, Abgleich mit `kampagnen.csv`, Ränge der Halte (1, 4, 12, 13, 17), G1 nur Konfigurationsläufe −0,75 | 3.1 | `tabelle.py` | `eps_tabelle.csv`, `tabelle.out` | Nachprüfung 1 | CSV neu, =Quelle; .out neu |
| Phase-0- und Phase-1-Modell der Teststatistik | 3.1, 7 | `phase0.py`, `phase1.py`, `phase1b.py` | (Module) | Nachprüfung 1 | – |
| Zählererwartung auf einem u-Gitter | 3.1 | `gitter.py` | `gitter.json` | Nachprüfung 1 | übernommen |
| Halte je Kampagne, Dispersion, P(≥ k), Mischung, homogene Rate; Varianten gen_F, A8, A8_F, chi41, fest | 3.1 (Tabelle „Halte je Kampagne“, P(kein S1-Halt) 0,91/0,88), 5.4 | `s1_verteilung.py` | `s1_verteilung_<variante>_streng_<seed>.json` (5 Dateien), `s1_verteilung_gen_F_A8.json` (milde Lesart, ältere Fassung, siehe Lücken) | Nachprüfung 1 | übernommen |
| Detailsimulation je Kampagne (npz, nicht im Paket); Mittelwerte aller Zähler, darunter R₁ je Kampagne 4,26 / 4,58 gegen 3,64 bei bekanntem σ (`s1_verteilung_fest_streng_104.json`), also Vorprüfung 17–26 % häufiger | 1.1, 1.2, 3.1 | `detail.py` | `log_det_genF.txt`, `log_det_A8F.txt` | Nachprüfung 1 | übernommen |
| D 2,0–2,1 / 2,5; P(≥ 2) 0,023 / 0,040; P(≥ 4) 0,0036 / 0,0076; homogen 1,0·10⁻⁵ / 5,2·10⁻⁵; Halt an R₂ 1,1–1,7·10⁻², an R₃ 3–5·10⁻³; 36–52 % bei u < 0,85; Kette 0,28/0,33 je Alarmhalt, Kettenfaktor 1,25–1,30; Option (iii) 6–16 % zu niedrig; W = 1, 2, 3 nicht fortgesetzt; 4/30 mit P = 0,26–0,50 (σ bekannt 0,012); X′-Weg 0,35 erwartet, P = 0,05; Halt an gültigem X′ 0,6–1·10⁻⁴; S1 je Lauf 2,5·10⁻³ (u = 0,7) bis 6·10⁻⁷ (u = 1,2) | 1.1, 1.2, 3.1, 3.2 | `auswertung_detail.py` | `auswertung_detail.out` | Nachprüfung 1 | neu |
| erwartete S1-Halte der 30 Kampagnen bei ihrem ε, κ(ν), ν_eff analytisch 20,6 / 30,3 | 3.1 | `erwartung30.py` | `eps_tabelle_mit_erwartung.csv`, `erwartung30.out` | Nachprüfung 1 | CSV neu, =Quelle; .out neu |
| Verteilung von u, ν_eff 20,9 (Momente), q(1,5) 0,61 %, q(2) 1,5 %, p1 2,5·10⁻⁴ als Mittel über σ̂_ref | 1.2, 3.1 | `p0_vert.py` | `p0_vert.json` | Nachprüfung 1 | übernommen, geprüft |
| 72 % der Schranke aus 9 % der Kampagnen mit u < 0,8; F-Test 9,1 % statt 5,0 % bei getrennt skaliertem Boden | 3.1, 5.2 | `rest.py` | `rest.out` | Nachprüfung 1 | neu |
| Spearman(ε, G1) im Modell Median −0,71, P(≤ −0,81) = 0,14; KS-Test p = 0,36 | 3.1 | `vergleich.py` | `vergleich.out` | Nachprüfung 1 | neu |

### a8_wege

| Beleg | Vorlage | Skript | Ausgabe | Herkunft | Stand |
|---|---|---|---|---|---|
| S1-Wege je Lauf marginal über σ̂_ref: Alarm am R₁ 2,9–3,0·10⁻⁴, über X′ 0,9–2,0·10⁻⁴, Alarm an R₂ 0,6–2,6·10⁻⁴, an R₃ 1–2·10⁻⁵ | 3.1 (Tabelle S1-Wege), 8 | `a_halt_s1_wege.py` | `a_halt_s1_wege.out` | Nachprüfung 3 | neu |
| P(Vorprüfung) 1,54 %, P(S1 an R₁ / Vorprüfung) 1,9 %, P(S1 an R₂ / G1-Fall) 2,9·10⁻³ | 1.2, 3.1 | `a_halt_alarm_r1r2.py` | `a_halt_alarm_r1r2.out` | Nachprüfung 3 | neu |
| dieselben Wege bei bekanntem σ: R₁ 5–6·10⁻⁵, X′ 0,5–1,5·10⁻⁵, R₂ 0,6–4,4·10⁻⁵, R₃ < 2·10⁻⁶ | 3.1 (Spalte „σ bekannt“), 8 | `wege_sigma_bekannt.py` | `wege_sigma_bekannt.out` | Gegenprobe | neu |

### e3b

| Beleg | Vorlage | Skript | Ausgabe | Herkunft | Stand |
|---|---|---|---|---|---|
| Größe von Regel B am Rand über das volle Raster: höchstens 0,908·α/m; „unauffällig“ höchstens 0,0499; Gegenregeln (c-2 bis 6,4·α/m, √(Spur/2) bis 27·α/m) | 4.2 | `groesse_regel_b.py` | `groesse_regel_b.out`, `groesse_regel_b.json` (Schlüssel `zusammenfassung`, `kontrollen`, `ergebnisse`) | Nachprüfung 5 | übernommen |
| Grenzwert, kleine ν, zusammengesetzte Kovarianz (≤ 0,59·α/m), B = 1000 (relativ +1 bis +3 %), schwere Ränder (0,07–0,63·α/m, „unauffällig“ ≤ 0,049), Macht, c-2-Obergrenze am Rand (bis 0,154 bei ν = 19, 0,160 bei ν = 10), E3a, Satterthwaite (bis 1,085·α/m) | 4.2, 4.3, 4.5 (F-c4) | `zusatz_b.py` (importiert `groesse_regel_b.py`) | `zusatz_z1_z6.out/.json`, `zusatz_z4.out/.json`, `zusatz_z7.json` | Nachprüfung 5 | übernommen |
| erste Konstruktion gültiger Grenzen (R0–R3), Macht | 4.1, 4.2 | `e3b_vorschlag.py` | `e3b_vorschlag.out` | Lesebericht c | übernommen |
| R2 bei kleinen ν, O1, MP-Vergleich, E3a mit t | 4.1, 4.2 | `e3b_robust.py` (importiert `e3b_vorschlag.py`) | `e3b_robust.out` | Lesebericht c | übernommen |
| heutige Regel am Rand 2,1–11,5·α/m (s bekannt), Bonferroni-Summe, MP-Grenze t* | 4.1 | `e3b_rand.py` | `e3b_rand.out` | Lesebericht c | übernommen |
| E3a am Rand: heute 3,1·α/m (n_A = 22), t-Regel ≤ α/m, obere Grenze 6,2 % | 4.1, 4.3 | `e3a_nu.py` | `e3a_nu.out` | Lesebericht c | übernommen, geprüft |
| Gegenprobe der Größe von B per Monte Carlo: 0,908·α/m bei ν = 10, ρ = 0,1, t = 10 | 4.2, 8 | `b_rand.py` | `b_rand.out` | Gegenprobe | neu |
| Gegenprobe isotrop ν = 19, t = 1,5: 0,146·α/m | 4.2, 8 | `b_iso.py` | `b_iso.out` | Gegenprobe | neu |
| Nachzählung der 570 gespeicherten Prüfgrößen (H03 30/30, E07-basisdrift 31/40 bzw. 33/40, A06 0, L4 0, „unauffällig“ L1 0/200) | 4.2 | `nachzaehlung_rekonstruktion.py` | `nachzaehlung_rekonstruktion.out`; Original zum Vergleich `e3b_nachzaehlung.out` | Nachprüfung 5 (Rekonstruktion); Original: Lesebericht c | .out neu, =Quelle; Original unverändert |
| Kurtosis 1,95 [1,76; 2,15], ρ ≥ 0,67, ŝ kalibriert 1,07, T-Anteil < 10⁻⁴ | 4.2 | `indirekt_aniso_nu.py` | `indirekt_aniso_nu.out` | Nachprüfung 5 | neu, =Quelle |
| Referenzwerte CV²(ŝ²) gegen ν (ν_eff ≈ 50, 42–63) | 4.2 | `cv_nu_abbildung.py` | `cv_nu_abbildung.out` | Nachprüfung 5 | neu, =Quelle |
| E3a-Faltungsfaktor ≤ 1,03, L4 Kampagne 31 (u = 0,120°), κ | 4.2, 4.3 | `kleinrechnungen.py` | `kleinrechnungen.out` | Nachprüfung 5 | neu, =Quelle |

### freiheitsgrade

| Beleg | Vorlage | Skript | Ausgabe | Herkunft | Stand |
|---|---|---|---|---|---|
| ν_eff von σ̂_ref: analytisch 20,6 (42 R) bzw. 30,3 (61 R), exakt 20,8 bzw. 30,6, Monte Carlo 20,8 bzw. 30,6 (gegen E[σ̂²]) und 19,8 bzw. 29,6 (gegen die nominale LOO-Varianz 1,5·σ²); p1 marginal 2,50·10⁻⁴ (42 R) bzw. 1,45·10⁻⁴ (61 R) gegen 2,53·10⁻⁵ bei bekanntem σ | 1.4, 3.1, 3.4, 5.2, 8 | `nu_eff_sigma_ref.py` | `nu_eff_sigma_ref.out`, `nu_eff_sigma_ref.json` | neu (dieses Paket), rechnet die Gegenprobe nach | neu |

### kosten

| Beleg | Vorlage | Skript | Ausgabe | Herkunft | Stand |
|---|---|---|---|---|---|
| R1 6,5–8,9 bzw. 8,6–11,8 Kernstunden, R2 4,5–7,0, Neukalibrierung 55–243 (oben 166 je System gemessen), Phase-0-Läufe, Nachziehen, κ, Größe von b̂ | 2.5, 3.5, 5.5, 6, 8 | `rechnung.py` | `rechnung.json` | Nachprüfung 7 | neu, =Quelle |
| zweite Phase-0-Anordnung: Differenz etwa 4,4 Standardfehler bei 3000 Kampagnen | 6 | `trennschaerfe.py` | `trennschaerfe.out` | Nachprüfung 7 | neu |

### bezugsmengen

| Beleg | Vorlage | Skript | Ausgabe | Herkunft | Stand |
|---|---|---|---|---|---|
| 5 von 30 halten an; nur V1-G0 Nr. 2 mit 21/21 auswertbaren Punkten; 25/25 abgeschlossene vollständig | 3.1 | `zaehle_halte.py` | `zaehle_halte.out` | Nachprüfung 4 | neu |
| Prüfschwelle 0,0695 (1000) bzw. 0,0714 (833), Überdeckung 0,936 bzw. 0,935; Reserve: 2,2·10⁻³ je Punkt, 0,955 gemeinsam (r = 3), 1,6·10⁻² und 0,71 (r = 2) | 3.1 | `schwellen.py` | `schwellen.out` | Nachprüfung 4 | neu |

### laufphase

| Beleg | Vorlage | Skript | Ausgabe | Herkunft | Stand |
|---|---|---|---|---|---|
| Summenharmonische der Einzelmodule (A4: 1,297 / 0,427 / 0,184 N) | 5.1 | `a4_struktur.py` | `struktur.json`, `a4_struktur.out` | Nachprüfung 6 | JSON neu, =Quelle; .out neu |
| Lⱼ-Schätzer identifizierbar: σ̂_δ/σ_δ zu 90 % in [0,73; 1,26], Rauschboden 0,4–1,6 % | 2.2 | `ident.py` | `ident.out` | Nachprüfung 6 | neu |
| Faktor d2: L0 2,2–2,4 (k = 1–3), 1,03–1,69 (k = 4–9), L1 1,03–1,21 | 5.1 | `d2_nach.py` | `d2_nach.out` | Nachprüfung 6 | neu |
| F_min-Faktor L0 1,96–2,76 (Maximum S118), L1 1,05–1,27 | 5.1 | `d2_fmin.py` | `d2_fmin.out` | Nachprüfung 6 | neu |
| Zählung an S120 (G4 unter v2, σ_F,v2 je Kampagne) | 2.1 | `csv_s120.py` | `csv_s120.json`, `csv_s120.out` | Nachprüfung 6 | JSON neu, =Quelle; .out neu |
| D_F-Nachbildung je Laufgröße, alle Punkte | 2.1 | `df_mc.py` | `df_mc_A4.json`, `df_mc_V1-G0.json`, `df_mc_A4.out`, `df_mc_V1G0.out` | Nachprüfung 6 | übernommen |
| MAD(D_F) an S120: 1,64 / 2,12 / 2,25 mN (A4), G4-Rate unter v2 | 2.1 | `s120_rate.py` | `s120_rate_A4.out`, `s120_rate_V1G0.out` | Nachprüfung 6 | übernommen |
| beobachtet gegen nachgebildet (S120, übrige 20 Punkte 0,93–1,08), Faktoren 1,15 / 1,28 / 1,36–1,39, Quantil 99,9 % beim 3,8–3,9-Fachen der MAD | 2.1 | `df_vergleich.py` | `df_vergleich.out` | Nachprüfung 6 | neu |
| Empfindlichkeit an S120 −4 / +2,4 % | 2.2 | `s120_empf.py` | `s120_empf.out` | Nachprüfung 6 | neu |

### g4_lj

| Beleg | Vorlage | Skript | Ausgabe | Herkunft | Stand |
|---|---|---|---|---|---|
| Auszug der Checkpoint-Befunde von PR #22 (120) und PR #23 (30), SHA-geprüft | 2.2, 3.1 | `g4L_daten.py` | `g4L_daten.json` (510 kB), `g4L_daten.out` | erste Fassung, von Nachprüfung 2 übernommen | JSON übernommen, geprüft; .out neu |
| Anlasszähler je Kampagne: 55 Kontrollwiederholungen nach G4 in 30 Kampagnen, kein Halt durch G4 | 2.2, 3.1 | `g4L_zaehlung.py`, `g4L_nichtK.py` | `g4L_zaehlung.out`, `g4L_nichtK.out` | erste Fassung, von Nachprüfung 2 übernommen | neu |
| σ̂_Δ je Gruppe gegen Normal-MAD-Theorie, Homogenität L1–L3 | 2.2 | `g4L_sigma.py`, `g4L_module.py` | `g4L_sigma.out`, `g4L_module.out` | erste Fassung bzw. Nachprüfung 2 | neu |
| Modelltest b-g4 gegen PR #22/#23 | 2.2 | `g4L_modelltest.py` | `g4L_modelltest.out` | erste Fassung, von Nachprüfung 2 übernommen | neu |
| D_N und D_F unkorreliert; Phase 0 von PR #22 und #23 gleich | 2.2 | `g4L_korr.py` | `g4L_korr.out` | erste Fassung, von Nachprüfung 2 übernommen | neu |
| Option F: 3,6 % [2,8; 4,4] je L-Lauf, 3,0 [2,3; 3,7] Wiederholungen, 3,8 % [2,6; 5,2] G4-Halte bei V1; Pooling 1,0 / 0,11 %; k(n) 0,4 / 0,2 % | 2.2, 3.1 | `g4L_kalib.py`, `g4L_kalib2.py` | `g4L_kalib.out`, `g4L_kalib2.out` | Nachprüfung 2 | übernommen, geprüft |
| Normalmodell gegen 41 Wiederholungen der 25 abgeschlossenen Kampagnen: Mittel 74,9, P(≤ 41) = 0,007 | 2.2 | `pruef_g4_kontroll_vs_pr23.py` | `pruef_g4_kontroll_vs_pr23.out` | Kritik | neu |

## Eingaben

Aus dem Repository (Stand main 0f63187, unverändert auf diesem Zweig):
`docs/ap13_kmax_wiederholungen_2026-10-17/` (`ergebnisse.json`, `kampagnen.csv`),
`docs/e3b_g4_diagnose_2026-10-17/` (`e3_pruefgroessen.csv`, `ergebnisse.json`, `g4_konfigurationen.csv`,
`werkzeug8_V1G60h.*`), `docs/ap13_neulaeufe_2026-10-17/werkzeug8_*` und der Code `code/pcmms_auswertung`
(`generator/systeme`, `vorhersage`, `konventionen`).

Flüchtige Checkpoints (nur lesen; Pfad als Kommandozeilenargument):

- Korrekturrunde von PR #23, 30 Ablaufkampagnen, am 18.10.2026 unter `/tmp/pcmms-ablauf-vergleich-20261018/`
  (Code c8c0a36, laut Metadaten `ablauf-2`). SHA-256 nach `docs/ap13_kmax_wiederholungen_2026-10-17/ergebnisse.json`,
  Schlüssel `checkpoints`; am 20.10.2026 nachgeprüft und gleich:
  - `korr-N01-A4-wiederholungen/ablauf_korr-N01-A4-wiederholungen.json`
    daca921e6ac715424b90fc392fedcdd4a47e78c319cd867ff183702a66f5e124
  - `korr-N01-V1G0-wiederholungen/ablauf_korr-N01-V1G0-wiederholungen.json`
    b4d3da73fe4d54307dc345cebcf10684874660c1c3df082bcbd16a27de8fbdbf
  - `korr-N01-V1G60h-wiederholungen/ablauf_korr-N01-V1G60h-wiederholungen.json`
    f9cd4300b987ba0bd969a1b6dfce1eb1aaceda5e0c9537ba6fe7a286ed4c61ba
- G4-Diagnose von PR #22, am 17.10.2026 unter `/tmp/pcmms-diagnose-e3b-g4-20261017/` (Ordner `G4-N01-*-start` und
  `-rest`); SHA-256 in `docs/e3b_g4_diagnose_2026-10-17/ergebnisse.json`. `g4L_daten.py` prüft jede Datei.

Wer die Checkpoints nicht mehr hat, kann die Skripte, die sie lesen (`tabelle_eps_halte.py`, `tabelle.py`,
`erwartung30.py`, `vergleich.py`, `auswertung_detail.py`, `zaehle_halte.py`, `g4L_daten.py`, `g4L_korr.py`), nicht
neu ausführen; ihre Ausgaben liegen hier. `g4_lj/g4L_daten.json` enthält die Befunde beider Checkpoint-Sätze im
JSON-Teil (ohne die npz-Felder von PR #22) und macht die übrigen `g4L_*`-Skripte ohne Checkpoints lauffähig.

## Modellannahmen je Rechnung

- **eps_ctrl.** ⟨N⟩ aller Laufarten normal mit gleicher Streuung σ = 1 (Summe), Zellen σ/√3 unabhängig, keine
  Drift. Phase 0: Referenzläufe im Abstand von drei Läufen (je zwei andere dazwischen), 61 R (Anordnung des
  Generators) oder 42 R (Mindestzahl nach P0.7, ebenfalls Abstand zwei, nicht zwölf); σ̂_ref aus Leave-one-out;
  F-Test nach A9.8 mit kritischem Wert aus 200 000 Nulldatensätzen; ε_ctrl = 3·σ̂_ref oder 3·σ̂_betr. Phase 1 nach
  dem Plan von PR #23 (N_K = 21, n = 24, ein Messtag, 630 geplante Läufe) mit Vorprüfung, G1, R₂/X′/R₃, S1 und
  Nullpunktalarm in Summe und drei Zellen; Wiederaufnahme ohne Befund, unbegrenzt; strenge Lesart (jeder
  Nullpunktalarm im W-Satz hält an, wie der Code `ablauf-3`) oder milde Lesart. Nicht modelliert: S3, G2–G10,
  Aufwärmen, Drift, Messtagwechsel. Tabellen: σ von ⟨N⟩ je Lauf 0,02/√(6400·10) N, u = ε_ctrl/(3·√1,5·σ).
- **a8_wege.** Annahmen von A8: exakte Superposition, gleiche Streuung, keine Drift, nur Summenkanal, ein eigenes R₀
  je Lauf, σ̂_ref aus 42 gleich getakteten Referenzläufen, kein F-Test, ungünstige Lagen (k, m) = (1, 1), (6, 6),
  (12, 1). Es sind Bonferroni-Größen je Lauf, keine Raten des Verfahrens.
- **e3b.** D̂ zweidimensional normal (Nenner nahezu fest), Σ̂ = W/ν mit W ~ Wishart(ν, Σ) unabhängig von D̂, Läufe
  je Quelle unabhängig ohne Drift, Rauschbias klein gegen q_tol; Größe am Rand |D| = q_tol. Nicht geprüft: Drift,
  serielle Korrelation, Schiefe, Rauschen im Nenner. Nachzählung: ŝ aus der isotropen Umkehrung von u (Σ̂ ist nicht
  gespeichert), m = 43.
- **freiheitsgrade.** Referenzläufe unabhängig normal mit gleicher Streuung, keine Drift; LOO-Wert wie
  `gueltigkeit.sigma_ref` mit zeitlicher Interpolation zwischen den Nachbarn. **ν_eff hängt von Zahl und Anordnung
  der Referenzläufe ab; „etwa 21“ gilt für 42 gleich getaktete Referenzläufe.** Gleich getaktet sind benachbarte
  LOO-Werte mit −2/3 und 1/6 korreliert, ν_eff = (n − 2)/(1 + 2·((2/3)² + (1/6)²)): 4,6 (11 R, Abstand 12 nach
  P0.7), 20,1 (41 R), 20,6 (42 R), 30,3 (61 R, Generator). Ein ungleicher Takt ändert die Gewichte und damit
  Korrelation und Skala; im gerechneten Beispiel (Abstände abwechselnd 1 und 3, eine Annahme zur Veranschaulichung)
  bleibt ν fast gleich (20,7), die LOO-Varianz steigt aber von 1,5 auf 1,625·σ² und p1 fällt von 2,50 auf
  1,79·10⁻⁴. p1 nach Anhang Tab. F Z. 1437: erster Lauf in ungünstigster Lage, Wiederholung mittig, beide bei
  gegebenem σ̂_ref unabhängig.
- **kosten.** Gelesene Sekunden je Kampagne aus `docs/ap13_kmax_wiederholungen_2026-10-17/ergebnisse.json`
  (schlank 2,59 bzw. 3,54 s, statisch 2,02 bzw. 3,13 s, voll gemessen 68–139 s), lineare Hochrechnung; Trennschärfe in
  Normalnäherung mit den Dispersionsindizes der Tabelle in 3.1.
- **bezugsmengen.** Zählung in den Checkpoint-Befunden; Schwellen aus Binomial-Standardfehlern; Reserve mit
  unabhängigen Versuchen (ein Platz fehlt nach drei ungültigen Versuchen).
- **laufphase.** Generatorstruktur (Ebene H nach `generator/ebene_h.py`) mit den Parametern der Stufe L1
  (Amplitude 0,3 %, δ 0,03°, Indexversatz 0,05°, Zyklusjitter 0,2°, weißes Rauschen je Zelle und Abtastwert
  0,02/√3 N), N01 mit
  identischen Modulen; gilt für das Modell, nicht für eine Apparatur.
- **g4_lj.** Normalmodell b-g4: σ̂_Δ je Modul aus n₀ = 20 (Referenz n = 61) über die Normal-MAD, D_N und D_F
  unabhängig; Skalenfaktor κ an PR #22 kalibriert; Wiederholungen bis zum Halt nach drei ungültigen Versuchen.

## Seeds

| Skript | Seed |
|---|---|
| `eps_ctrl/s1_verteilung.py` | Argument 5; Ausgaben: 101 gen_F, 102 A8, 103 chi41, 104 fest, 105 A8_F (je N = 20 000, „streng“); `s1_verteilung_gen_F_A8.json` (N = 40 000, mild) ohne vermerkten Seed |
| `eps_ctrl/detail.py` | Argument 4; Vorlage: gen_F 201, A8_F 202 (je 20 000) |
| `eps_ctrl/gitter.py` | `random.Random(20261019)` |
| `eps_ctrl/p0_vert.py` | `default_rng(20261019)` |
| `eps_ctrl/rest.py` | `default_rng(1)` (wie Tab. F Z. 1437), `default_rng(4)` |
| `eps_ctrl/vergleich.py` | `default_rng(3)` |
| `a8_wege/a_halt_s1_wege.py`, `wege_sigma_bekannt.py` | `default_rng(11)` |
| `a8_wege/a_halt_alarm_r1r2.py` | `default_rng(7)` |
| `e3b/groesse_regel_b.py` | 20261019 + 100·i + j je Zelle (ν_i, ρ_j); Kontrollen 5–8 |
| `e3b/zusatz_b.py` | ein Generator `default_rng(20261024)` für die Teile in Aufrufreihenfolge; z7: `default_rng(77)` |
| `e3b/e3b_vorschlag.py`, `e3b_robust.py`, `e3b_rand.py`, `e3a_nu.py` | 20261019, 20261020, 20261018, 20261021 |
| `e3b/b_rand.py`, `b_iso.py` | 2024, 99 |
| `e3b/indirekt_aniso_nu.py`, `cv_nu_abbildung.py` | 55, 91 |
| `freiheitsgrade/nu_eff_sigma_ref.py` | 1 (42 R, wie Tab. F), 2 (61 R), 3 (ungleicher Takt) |
| `laufphase/ident.py`, `df_mc.py` | 20261019 |
| `laufphase/s120_rate.py`, `s120_empf.py`, `d2_fmin.py` | 20261020, 11, 5 |
| `g4_lj/g4L_kalib.py`, `g4L_modelltest.py`, `pruef_g4_kontroll_vs_pr23.py` | 20261019 |
| `g4_lj/g4L_kalib2.py`, `g4L_sigma.py` | 42, 1 |
| alle übrigen | keiner (Zählung, Analytik, Quadratur) |

## Softwarestand

- Repository: main 0f63187 (PR #23). Die Skripte, die Repository-Code importieren (`laufphase/a4_struktur.py`,
  `d2_fmin.py`, `df_mc.py`, `s120_rate.py`, `s120_empf.py`), wurden gegen einen Auszug
  `git archive 0f63187 code docs` gerechnet, weil im Arbeitsbaum dieses Zweigs parallel am Code gearbeitet wird.
  Die gelesenen Dateien unter `docs/` sind auf diesem Zweig gegenüber 0f63187 unverändert.
- Python 3.13.16, numpy 2.5.3, scipy 1.18.1 (Umgebung der Zusammenstellung). Die übernommenen Ausgaben stammen aus
  derselben Sitzungsumgebung vom 18. und 19.10.2026; die zur Kontrolle wiederholten Rechnungen sind bytegleich.
- Rechenrahmen: ein Prozess, `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1`.

## Ausführung

Vorbereitung (Bash, Repository-Wurzel):

```
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
B=docs/entscheidungsvorlage_2026-10-19_belege
CP23=<Verzeichnis der Checkpoints von PR #23>      # früher /tmp/pcmms-ablauf-vergleich-20261018
CP22=<Verzeichnis der Checkpoints von PR #22>      # früher /tmp/pcmms-diagnose-e3b-g4-20261017
# optional für Skripte mit Repository-Code: export PCMMS_REPO=<auszug von 0f63187>
```

`-I` (isoliert) steht bei Skripten ohne lokale Importe, `-B` überall (keine `__pycache__`). Die Skripte, die einen
Ordner als Argument „.“ erwarten oder neben sich schreiben, werden im jeweiligen Ordner aufgerufen. Repository-Pfade
bestimmen die Skripte relativ zu ihrem Ort (drei Ebenen höher) oder über `PCMMS_REPO`. Laufzeiten: Wandzeit, ein
Prozess, gemessen am 20.10.2026; „geschätzt“ bei nicht neu gerechneten Ausgaben.

| Ordner | Befehl (im Ordner, sofern nicht anders angegeben) | Laufzeit |
|---|---|---|
| eps_ctrl | `python3 -I -B tabelle_eps_halte.py $CP23 eps_ctrl_halte_je_kampagne.csv > tabelle_eps_halte.out` | < 1 s |
| eps_ctrl | `python3 -I -B tabelle.py $CP23 eps_tabelle.csv > tabelle.out 2>&1` | < 1 s |
| eps_ctrl | `python3 -B gitter.py . gitter.json` | geschätzt 4–5 min |
| eps_ctrl | `python3 -B s1_verteilung.py . 20000 gen_F streng 101` (ebenso A8 102, chi41 103, fest 104, A8_F 105) | je etwa 2 min (Feld `sekunden` 107–111 s plus F-Test-Nullsimulation) |
| eps_ctrl | `python3 -B detail.py . gen_F 20000 201 > log_det_genF.txt`; `python3 -B detail.py . A8_F 20000 202 > log_det_A8F.txt` | geschätzt je 2 min; schreibt `detail_gen_F_201.npz` bzw. `detail_A8_F_202.npz` (je 2,7 MB) in den Ordner |
| eps_ctrl | `python3 -I -B auswertung_detail.py . $CP23 > auswertung_detail.out` (nach `detail.py`) | 1 s |
| eps_ctrl | `python3 -I -B erwartung30.py . $CP23 > erwartung30.out` | < 1 s |
| eps_ctrl | `python3 -B p0_vert.py . > p0_vert.json` | 30 s |
| eps_ctrl | `python3 -B rest.py . > rest.out` | 7 s |
| eps_ctrl | `python3 -B vergleich.py . $CP23 > vergleich.out` | 8 s |
| a8_wege | `python3 -I -B a_halt_s1_wege.py > a_halt_s1_wege.out` | 10 s |
| a8_wege | `python3 -I -B a_halt_alarm_r1r2.py > a_halt_alarm_r1r2.out` | 1 s |
| a8_wege | `python3 -I -B wege_sigma_bekannt.py > wege_sigma_bekannt.out` | 6 s |
| e3b | `python3 -B groesse_regel_b.py groesse_regel_b.json > groesse_regel_b.out` | 287 s mit vier Prozessen (`Pool(4)` im Skript, etwa 19 Kernminuten) |
| e3b | `python3 -B zusatz_b.py zusatz_z1_z6.json z1 z2 z3 z5 z6 > zusatz_z1_z6.out`; `python3 -B zusatz_b.py zusatz_z4.json z4 > zusatz_z4.out`; `python3 -B zusatz_b.py zusatz_z7.json z7` | geschätzt einige Minuten je Aufruf |
| e3b | `python3 -I -B e3b_vorschlag.py > e3b_vorschlag.out`; `python3 -B e3b_robust.py > e3b_robust.out`; `python3 -I -B e3b_rand.py > e3b_rand.out` | geschätzt mehrere Minuten bzw. je 1–2 min |
| e3b | `python3 -I -B e3a_nu.py > e3a_nu.out` | 2 s |
| e3b | `python3 -I -B b_rand.py > b_rand.out`; `python3 -I -B b_iso.py > b_iso.out` | 30 s; 19 s |
| e3b (Repository-Wurzel) | `python3 -I -B $B/e3b/nachzaehlung_rekonstruktion.py docs/e3b_g4_diagnose_2026-10-17/e3_pruefgroessen.csv > $B/e3b/nachzaehlung_rekonstruktion.out` | 1 s |
| e3b (Repository-Wurzel) | `python3 -I -B $B/e3b/indirekt_aniso_nu.py docs/e3b_g4_diagnose_2026-10-17/e3_pruefgroessen.csv > $B/e3b/indirekt_aniso_nu.out` | 2 s |
| e3b | `python3 -I -B cv_nu_abbildung.py > cv_nu_abbildung.out`; `python3 -I -B kleinrechnungen.py > kleinrechnungen.out` | 10 s; < 1 s |
| freiheitsgrade | `python3 -I -B nu_eff_sigma_ref.py nu_eff_sigma_ref.json > nu_eff_sigma_ref.out` | 6 s |
| kosten | `python3 -I -B rechnung.py rechnung.json > /dev/null`; `python3 -I -B trennschaerfe.py > trennschaerfe.out` | < 1 s |
| bezugsmengen | `python3 -I -B zaehle_halte.py $CP23 > zaehle_halte.out`; `python3 -I -B schwellen.py > schwellen.out` | < 1 s |
| laufphase | `python3 -B a4_struktur.py struktur.json > a4_struktur.out` | 1 s |
| laufphase | `python3 -I -B csv_s120.py csv_s120.json > csv_s120.out` | < 1 s |
| laufphase | `python3 -I -B ident.py > ident.out`; `python3 -I -B d2_nach.py > d2_nach.out`; `python3 -B d2_fmin.py > d2_fmin.out` | 14 s; < 1 s; 10 s |
| laufphase | `python3 -B df_mc.py A4 30000 > df_mc_A4.out`; `python3 -B df_mc.py V1-G0 30000 > df_mc_V1G0.out` | 276 s bzw. 294 s (übernommene Angabe) |
| laufphase | `python3 -B s120_rate.py A4 > s120_rate_A4.out`; `python3 -B s120_rate.py V1-G0 > s120_rate_V1G0.out` | geschätzt je 1–2 min |
| laufphase | `python3 -I -B df_vergleich.py > df_vergleich.out`; `python3 -B s120_empf.py > s120_empf.out` | < 1 s; 14 s |
| g4_lj | `python3 -I -B g4L_daten.py $CP22 $CP23 g4L_daten.json > g4L_daten.out` | 2 s |
| g4_lj | `python3 -I -B <skript>.py > <skript>.out` für `g4L_zaehlung`, `g4L_nichtK`, `g4L_module`, `g4L_sigma`, `g4L_modelltest`, `g4L_kalib`, `g4L_kalib2`, `pruef_g4_kontroll_vs_pr23` | < 1 s bis 66 s (`g4L_kalib`), 41 s (`g4L_modelltest`) |
| g4_lj | `python3 -I -B g4L_korr.py $CP22 > g4L_korr.out` | 1 s |

Neu gerechnet wurden für dieses Paket etwa 6,5 CPU-Minuten (einschließlich der Kontrollrechnungen); die Langläufer
`s1_verteilung.py`, `groesse_regel_b.py`, `df_mc.py` und `zusatz_b.py` sowie `gitter.py`, `s120_rate.py`,
`e3b_vorschlag.py`, `e3b_robust.py` und `e3b_rand.py` wurden nicht vollständig neu gerechnet. Ihre Aufrufbarkeit
wurde in einer Kopie außerhalb des Pakets mit kleinen Parametern in einem Prozess geprüft (s1_verteilung und detail
mit 40 Kampagnen; die Zellfunktion von groesse_regel_b mit N_W = 2000; zusatz_b Teile z1–z6 mit N = 2000; df_mc
mit N = 200; s120_rate mit N = 2000, gitter mit 3 Kampagnen je Punkt, e3b_vorschlag/robust/rand mit N = 2000–4000,
die drei letzten über einen Aufruf, der nur die Stichprobengröße im Speicher verkleinert). Alle liefen fehlerfrei.

## E3b-Nachzählung: Original und Rekonstruktion

- Das Originalskript der Nachzählung ist überschrieben und verloren. Die Datei gleichen Namens im Scratch-Ordner
  (SHA-256 34e86c679397ec90ae4f0abfacd3b9370aa042a44ca2b691a83cc7b6b5071167) ist eine spätere, andere Rechnung; sie
  erzeugt nicht die Tabelle der Originalausgabe und liegt nicht im Paket.
- `e3b/e3b_nachzaehlung.out` ist die unveränderte Originalausgabe vom 18.10.2026, SHA-256
  **7bba3400fb0ba636988a124236a6593cd609c3e8049ac95563c553aac9b44d98**.
- `e3b/nachzaehlung_rekonstruktion.py` (Nachprüfung 5, nach der Kopfzeile der Originalausgabe neu geschrieben)
  reproduziert die Zeilen 1–12 der Originalausgabe bytegleich: `head -12 nachzaehlung_rekonstruktion.out | sha256sum`
  ergibt am 20.10.2026 ebenfalls 7bba3400fb0ba636988a124236a6593cd609c3e8049ac95563c553aac9b44d98. Die Zeilen 13–26
  sind neue Zusätze (Regel B mit ν = 19, O1 „unauffällig“). Die Rekonstruktion ist eine gleichwertige Neufassung, nicht
  das Original. Eingabe: `docs/e3b_g4_diagnose_2026-10-17/e3_pruefgroessen.csv` (SHA-256
  09646e1fe34b347df5369c0f7c02178384a1ecccaa59d460d1273bb7e32a1083).

## Prüfungen bei der Zusammenstellung

- Neu erzeugt und bytegleich mit der Ausgabe im Scratch-Ordner: `eps_ctrl_halte_je_kampagne.csv`, `eps_tabelle.csv`,
  `eps_tabelle_mit_erwartung.csv`, `nachzaehlung_rekonstruktion.out`, `indirekt_aniso_nu.out`,
  `cv_nu_abbildung.out`, `kleinrechnungen.out`, `rechnung.json`, `struktur.json`, `csv_s120.json`.
- Übernommen und in einer Kopie neu gerechnet, bytegleich: `p0_vert.json`, `e3a_nu.out`, `g4L_daten.json`
  (SHA-256 35aa4ae9d2e4fb5217a1e9c11726b32535bcc58911a0bb174d0da284ebd6c2fd), `g4L_kalib.out`, `g4L_kalib2.out`.
- Die neu erzeugten Ausgaben ohne Gegenstück (a8_wege, `b_rand.out`, `b_iso.out`, `auswertung_detail.out` usw.)
  geben die in der Vorlage genannten Werte wieder (Tabelle oben). `b_rand.py` ist reines Monte Carlo; an
  (ν = 19, ρ = 1, t = 1,5) liegt es mit 0,121 ± 0,010·α/m etwa 2,5 Standardfehler unter dem bedingt exakten Wert
  0,146 aus `b_iso.py` und dem Raster von `groesse_regel_b.out` (0,14); die Vorlage zitiert die bedingt exakten Werte.
- Bereinigung: keine Sitzungspfade, keine Kontaktdaten, keine Prüferantworten oder Agentenprotokolle, keine
  `__pycache__`.

## Lücken und Abweichungen

- **E3b-Nachzählung:** Originalskript verloren (oben); belegt ist die Rekonstruktion.
- **npz der Detailsimulation:** `detail_gen_F_201.npz` und `detail_A8_F_202.npz` (je 2,7 MB) liegen nicht im Paket.
  Sie entstehen mit `detail.py` (Befehle oben, Seeds 201 und 202, je 20 000 Kampagnen); `auswertung_detail.out`
  wurde am 20.10.2026 aus den npz im Scratch-Ordner erzeugt.
- **`s1_verteilung_gen_F_A8.json`** (milde Lesart, 40 000 Kampagnen) stammt aus einer früheren Fassung von
  `s1_verteilung.py`: ohne die Felder `halte_mit_WA` und `P_zweiter_halt_gegeben_erster` und mit anderem
  Dateinamensschema; der Seed ist nicht vermerkt. Die heutige Fassung schreibt bei „mild“
  `s1_verteilung_<varianten>_mild_<seed>.json`. Die frühere Fassung ist nicht erhalten.
- **Bildschirmausgabe von `zusatz_b.py z7`** wurde nicht gespeichert; `zusatz_z7.json` enthält dieselben Werte
  (das Skript druckt `OUT['Z7']` als JSON).
- **Bildschirmausgaben von `s1_verteilung.py`** (`log_*.txt` im Scratch-Ordner) sind nicht aufgenommen; sie enthalten
  je eine Zeile mit demselben Inhalt wie die JSON-Dateien.
- **Monte-Carlo-Wert 19,8 der Gegenprobe (Abschnitt 8):** Das Skript der Gegenprobe liegt nicht im Scratch-Ordner.
  `nu_eff_sigma_ref.py` erhält 19,82 mit der Momentenanpassung gegen die nominale LOO-Varianz 1,5·σ²
  (ν = 2·(1,5)²/Var σ̂²) und 20,83 gegen den Erwartungswert von σ̂² (ν = 2·(E σ̂²)²/Var σ̂², wie `p0_vert.py`: 20,9).
  Dass die Gegenprobe die erste Definition verwendet hat, ist eine Einschätzung. Die analytische Formel ist eine
  asymptotische Näherung (20,57 gegen exakt 20,83 bei 42 R).
- **Kette über dasselbe R₀ (Abschnitt 1.2):** Die analytischen Werte 0,185 / 0,225 / 0,271 und 0,057–0,107 der
  Nachprüfung 1 sowie die Gegenprobe „Reproduktion 0,058, Alarm des nächsten Referenzlaufs 0,20“ (Abschnitt 8) haben
  kein gespeichertes Skript. Aus dem Paket belegt sind 0,28 / 0,33 Halte je Alarmhalt, der Kettenfaktor 1,25–1,30
  (`auswertung_detail.out`) und der Anteil 98 % der W-Satz-Alarme nach einem Alarmhalt (Verhältnis der letzten beiden
  Mittelwerte in `log_det_*.txt`).
- **Nicht aufgenommen, weil nicht beauftragt:** weitere Skripte des Scratch-Ordners zur ersten Fassung, darunter die
  Rechnungen zum Halt an R₃ (bedingter Platzverlust etwa 42 %) und zur S1-Prüfung über einen Halt hinweg
  (5,3·10⁻⁴) aus Nachprüfung 3, das Modellskript zu G4 an Lⱼ, auf das sich `pruef_g4_kontroll_vs_pr23.py` bezieht,
  und die übrigen Lesebericht-Skripte.
- **Langläufer:** nicht neu gerechnet (oben); ihre Laufzeitangaben stammen aus den übernommenen Ausgaben oder sind
  Schätzungen. `groesse_regel_b.py` verwendet vier Prozesse; ein Neulauf im Rahmen „ein Prozess“ bräuchte etwa
  20 Minuten.

## Änderungen an den Skripten gegenüber der Quelle

Rechenlogik unverändert. Jedes übernommene Skript trägt einen Belegkopf (Zweck, Eingaben, Annahmen, Seed, Laufzeit,
Aufruf, Herkunft), danach die Zeile „Ende des Belegkopfs“ und den Text der Quelle. Geändert wurden nur feste Pfade:
Checkpoint-Verzeichnisse als Kommandozeilenargumente (`tabelle.py`: Argument 1, die Ausgabe ist jetzt Argument 2;
`erwartung30.py`, `vergleich.py`, `auswertung_detail.py`: Argument 2; `g4L_daten.py`: Argumente 1 und 2; `g4L_korr.py`:
Argument 1), Repository-Pfade relativ zur Repository-Wurzel (`tabelle.py`, `rechnung.py`, `csv_s120.py`,
`df_vergleich.py`, `g4L_daten.py`, `g4L_korr.py`, Code-Pfad in `a4_struktur.py`, `d2_fmin.py`, `df_mc.py`),
Scratch-Pfade durch den eigenen Ordner bzw. ein optionales Argument (`ident.py`, `d2_nach.py`, `a4_struktur.py`,
`csv_s120.py`, `df_mc.py` mit optionalem Argument 3 für die Ausgabe, `s120_rate.py`, `s120_empf.py`, `df_vergleich.py`,
`g4L_*.py`). `e3b_robust.py` und `zusatz_b.py` importieren ihre Partner wie bisher aus dem eigenen Ordner;
`s120_rate.py` und `s120_empf.py` führen den Kopf von `df_mc.py` aus dem eigenen Ordner aus.

## Grenzen

- Alle Rechnungen sind Rechnungen auf Ebene der Teststatistik oder Zählungen; sie sind synthetisch, ersetzen keine
  Kalibrierung von Werkzeug 8 und enthalten keine Messdaten.
- Die Checkpoint-Befunde stammen aus Entwicklungsläufen (30 Nullkampagnen, `ablauf-2`, reduzierte Replikatzahlen);
  sie zeigen Richtungen, keine Raten.
- Das Teststatistikmodell der Halte bildet S3, G2–G10, Drift, Aufwärmen und Messtagwechsel nicht ab; die A8-Wege
  rechnen mit den vereinfachten Annahmen von A8; die E3b-Rechnungen prüfen Drift, serielle Korrelation, Schiefe und
  Nennerrauschen nicht; die Rechnungen zur Laufphasenstreuung gelten für die Generatorstruktur mit L1-Parametern.
- Zahlen, die die Vorlage aus anderen Quellen (gelesen, gezählt in PR #21–#23, Einschätzung) führt, sind hier nicht
  belegt.
