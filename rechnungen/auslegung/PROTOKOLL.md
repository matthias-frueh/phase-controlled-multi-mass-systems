# P2 · Prüfgruppe „auslegung“ – V1-Auslegungsraum und bewegter Massenanteil

> **Vermerk zur Übernahme (04.10.2026).** Protokoll aus der Gesamtprojektanalyse 10/2026, Stand 02.10.2026, unverändert bis auf Pfade und Quellenangaben. Geprüft wurde der Repository-Stand `cd7be6a` (28.09.2026) mit der Präregistrierung v2 vom 25./28.09.2026; die späteren Änderungen aus PR #13 und PR #14 (unter anderem Präregistrierung v2 mit Arbeitsfestlegungen, `code/auslegung.py`, `code/ereignisloeser.py`) sind nicht eingearbeitet. Alle Zahlen sind Simulation oder Analytik, keine Messdaten. Verweise wie „L1a-019“, „P1 §3“ oder „B01–B14“ zeigen auf Arbeitsdokumente der Analyse, die nicht im Repository liegen. Quellen außerhalb des Repositorys sind als „(lokaler Bestand, nicht im Repository)“ gekennzeichnet. Startbefehle und Grenzen je Gruppe: [`rechnungen/README.md`](../README.md).

Stand 02.10.2026 · ursprünglich lokal, jetzt unter `rechnungen/` · nur Simulation/Analytik, keine Messdaten.

**Umgebung für alle Befehle** (aus `rechnungen/auslegung/`):

```sh
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../../code:.
```

**Kennzeichnung:** [R] eigene Rechnung · [Q] Quellenangabe mit Fundstelle · [A] Annahme.

## Dateien

| Datei | Inhalt |
|---|---|
| `mu_modell.py` | eigene Bibliothek: analytische Fourierkoeffizienten des Egg-Profils, lineares μ-Modell (Kontaktast), RK4-μ-Engine (Schema wie Referenz-Engine), Lauftypen |
| `a1_p1_zahlen.py` → `a1_p1_zahlen_ausgabe.txt` | Aufgabe 1: f_n, 3f/f_n, F_min Triphasik, Sekanten, Einzelmodul linear + RK4, PB1, A4-Frequenzgrenzen |
| `a1b_zusatz.py` → `a1b_zusatz_ausgabe.txt` | H₂ := 1-Sekanten (L2-026), Massenszenarien Laborplan/Index |
| `a2_lineares_modell_abgleich.py` → `a2_…_ausgabe.txt` | Aufgabe 2: Abgleich mit `code/linear_solver.py`, Phasenfaktor, Ähnlichkeitsgesetz, Skalierung |
| `a3a_G_funktionen.py` → `a3a_G_funktionen.csv`, `a3a_…_ausgabe.txt` | Aufgabe 3A: dimensionslose Last-/Signalfunktionen G(ρ, ζ) je Lauftyp (1168 Zeilen) |
| `a3b_arbeitspunkte.py` → `a3b_bereich.csv`, `a3b_hubfenster.csv`, `a3b_vorschlaege.csv`, `a3b_robustheit.csv`, `a3b_…_ausgabe.txt` | Aufgabe 3B: zulässiger Bereich, Hubfenster, Vorschläge V1–V5, Robustheit K ± 30 % × ζ |
| `a4_rk4_stichprobe.py` → `a4_rk4_<Fall>.csv/_ausgabe.txt` | Aufgabe 4: nichtlineare Stichprobe (V1z05, V2z02, V4z02, V4z10, V5z05), Wurfstarts (`start`), E1-Spitzen (`E1`) |
| `a4b_bistabilitaet.py` → `a4b_bistabilitaet.csv/_ausgabe.txt` | Aufgabe 4: Wurfstarts über ζ, Referenz-Gegenprobe, Zeitschritt |
| `a4c_einzugsbereich.py` → `a4c_einzugsbereich.csv/_ausgabe.txt` | Aufgabe 4: Schwelle der Wurfgeschwindigkeit |
| `a4d_konvergenz.py` → `a4d_konvergenz_A/B/C_ausgabe.txt` | Aufgabe 4: Zeitschritt (T/4000, T/8000) und Laufzeit (40 s) der Hüpf- und E1-Befunde |
| `a5_qualitativ.py` → `a5_qualitativ.csv/_ausgabe.txt` | Aufgabe 5: normierte Kennzahlen Referenz / starr / Vorschläge |
| `a5b_kontaktanteil_mu.py` → `a5_kontaktanteil_mu_ausgabe.txt` | Aufgabe 5: Kontaktanteil bei K = 10⁴ N/m über μ (Gegenprobe Präreg A3) |

Validierung der eigenen Werkzeuge [R]: (i) RK4-μ-Engine bei μ = 1 gegen `code/finesweep.py` an (120°, 240°) und (113,684°, 227,368°): F_min, F_max, ⟨N⟩, Schiefe, λ auf 6 Nachkommastellen gleich; an (0°, 0°) (75,8 % Liftoff) F_max 41,1241 gegen 41,1226 N (Auswertungsreihenfolge, wie im finesweep-Docstring beschrieben). (ii) Lineares Modell gegen `linear_solver.solve` in 384 Fällen (μ, K, ζ, f, Zufallsphasen): F_max ≤ 2·10⁻⁶ N, Schiefe ≤ 1·10⁻⁶, z_max ≤ 7·10⁻¹¹ m; F_min_lin ≤ 1,5·10⁻⁴ N (nur in abhebenden, resonanznahen Fällen; Ursache: analytische statt FFT-Profilkoeffizienten). (iii) Einheiten: Phasen in Grad an allen Schnittstellen, intern `np.radians`; τ = φ/(2πf), Verzögerung (z_j(t) = z(t − τ_j)), Harmonische mit e^{−ikφ}; Kraftstichprobe aus der ersten RK4-Stufe wie in der Engine (Linksrechteck für ⟨N⟩, deshalb ⟨N⟩ − Mg ≈ 10⁻⁷ N statt exakt null); bei f ≠ 10 Hz Δt = T/2000 (ganze Perioden), bei 10 Hz genau 50 µs.

---

## AUS-01 · Kennzahlen des Simulationsreferenzsatzes (P1 §2, §3; L1b-062, L2-013, L2-026)

**Frage.** Stimmen f_n = 19,74 Hz, 2f/f_n = 1,013, 3f/f_n = 1,52, F_min = 5,330 N am Triphasik-Punkt und die Zeltsekanten 0,212/0,195 N/°?

**Methode.** [R] Formeln; eigenes lineares Modell; Abgleich mit `data/finesweep_2deg_120_240.csv` (Zeile 222) und `linear_solver`; H₂ := 1-Diagnose eigenständig.

**Ergebnis.** f_n = 19,7407 Hz; 2f/f_n = 1,0131; 3f/f_n = 1,5197 (3f = 30 Hz gegenüber f_n/2 = 9,870 Hz: §5.3(b) um den Faktor 3 verletzt); |H(kω)| = 1,340 / 5,030 / 0,777 / 0,344 (k = 1 … 4). F_min(120°, 240°) = 5,330390 N (CSV, eigenes Modell, linear_solver identisch; zugleich Maximum der 441 Feinsweep-Punkte; 400/441 liftoff-frei). 2°-Sekanten 0,2124 / 0,1952 N/° (CSV und linear gleich), 20°-Sekanten 0,2281 / 0,1856 N/°. ΔF_Zelt (21 Punkte) = 4,5627 N. Mit H₂ := 1: 0,0458 / 0,0319 N/° (L2-026: 0,046/0,032). **Bestätigt.**

**Reproduktion.** `timeout 540 python3 a1_p1_zahlen.py` (≈ 4 min), `python3 a1b_zusatz.py`.

**Einschränkungen.** Gilt nur für den Simulationsreferenzsatz (μ = 1, K = 10⁴ N/m, C = 16 N·s/m).

## AUS-02 · Einzelmodul beim Referenzsatz: λ = 17,9 %, Dauerkontakt bis ≈ 75 % Hub (P1 §3.1)

**Frage.** Hebt ein Modul mit Referenzhub ab, und bis zu welchem Hubanteil besteht Dauerkontakt?

**Methode.** [R] Linear: F_min_lin eines Moduls (Gewichte w = (1, 0, 0)), Grenze aus F_min = 0 und aus x_max < 0 (Linearität in Hub). RK4-μ-Engine im Engine-Schema (Δt = 50 µs, 15 s, Auswertung 10 s), Hubanteil s = 0,70 … 1,00; Gegenprobe-Konvention (20 s, letzte 4 s) und Δt/2.

**Ergebnis.** Linear F_min = −2,0571 N, F_max = 15,47 N. Dauerkontaktgrenze linear bei **75,6 %** des Referenzhubs (aus x_max < 0: 76,7 %), **mit 25-%-Reserve nur 56,7 %**. RK4: s = 0,755 → λ = 0 (F_min 0,0091 N), s = 0,760 → λ = 1,90 %, 0,80 → 7,95 %, 0,90 → 13,95 %, **1,00 → λ = 17,90 %** (Engine-Konvention; 20 s/letzte 4 s: 17,90 %; Δt = 25 µs: 17,93 %). Der Übergang ist hier stetig (kein Sprung). **Bestätigt**, präzisiert (Grenze 75,5–75,6 %, Reserve-Grenze 56,7 %).

**Reproduktion.** `timeout 540 python3 a1_p1_zahlen.py`.

**Einschränkungen.** Standardstart; Einzelmodul = Modul 1 läuft, Module 2/3 geparkt (μ/3 der synchronen Anregung, Präreg A2.1).

## AUS-03 · PB1-Herleitung (L5a-065, Präreg A4/A8) und strengere Anforderung für N_k

**Frage.** ΔF_Zelt = 0,4693 N, Δ = 0,117 N, u_c ≤ 0,0327 N (ν → ∞) bzw. 0,0269 N (ν = 19)?

**Methode.** [R] Starre Auflage, μ = 0,4, 10 Hz, Referenzhub, 21 Schnittpunkte; c = t(1 − 0,05/(2·147); ν).

**Ergebnis.** F_min(120°) = 5,6452 N, F_min(100°) = 5,1759 N, F_min(140°) = 5,1760 N, **ΔF_Zelt = 0,4693 N**, Δ = 0,1173 N; c(∞) = 3,5826, c(19) = 4,3560 → **u_c ≤ 0,0327 N bzw. 0,0269 N (0,422 % von Mg)**. Sekanten 0,0469/0,0468 N/°. **Bestätigt.** Zusatz [R]: Für Re/Im N_k ist D_k = max_i |N̂_k,i| auf dem Schnitt im starren Fall 0,1483 / 0,0963 / 0,1822 · Mg·ε (k = 1, 2, 3), also für N₂ nur 62 % von ΔF_Zelt; im A4-Beispiel D₂ = 0,2924 N → u_c(N₂) ≤ 0,0204 N (ν → ∞) bzw. 0,0168 N (ν = 19). Das bestätigt die Vermutung in der Lückenspalte von L5a-065 (≈ 0,017 N): **die N₂-Anforderung ist strenger als die F_min-Anforderung** (Faktor 0,62); ob Harmonische entsprechend schwächer rauschen, ist Sache der Statistikgruppe.

**Reproduktion.** `a1_p1_zahlen.py` (PB1), `python3 a3a_G_funktionen.py` (D_k).

**Einschränkungen.** Ungebändert (volles Spektrum). Mit Bandbegrenzung k ≤ 3 wäre ΔG_Zelt 0,1887 statt 0,1545 (größer, also günstiger); das volle Spektrum ist für das Signal die vorsichtige Wahl.

## AUS-04 · Frequenzgrenzen und Zellzahlen des A4-Beispiels (Präreg A4)

**Frage.** Stimmen die A4-Angaben (25-%-Grenzen 19/21/18/12 Hz; Zelle 52,4 % bei 10 Hz; F_max-Werte)?

**Methode.** [R] Starr, μ = 0,4, Referenzhub, f = 10 … 26 Hz, kleinstes F_min/Mg je Lauftyp.

**Ergebnis.** Liftoff-Grenze / 25-%-Grenze (ganzzahlig): Schnitt 23/19 Hz, Einzelmodul 25/21 Hz, (0°, 180°) 21/18 Hz, synchron 14/12 Hz. Synchron 52,4 % (10 Hz), 31,4 % (12 Hz), 19,5 % (13 Hz). F_max bei 10 Hz: Schnitt 7,0752 N, synchron 12,0163 N, (0°, 180°) 9,1241 N, Einzelmodul 8,2564 N. **Alle A4-Zahlen bestätigt.**

**Reproduktion.** `a1_p1_zahlen.py`.

## AUS-05 · Massenkonflikt verifiziert (L1a-019, L5b-060, L4-017, L6b-073)

**Frage.** Welche Massenangaben stehen im Bestand?

**Methode.** [Q] grep in Evidenzmatrix und Quellen; [R] Umrechnung in ε.

**Ergebnis.** [Q] FV v2.7, Anh. B.4 (Z. 840 ff.): Restmasse m₀ = 0, kodiert M·z̈_f = −Mg + F_c − (M/3)Σq̈_k. [Q] Laborplan V1 (`(lokaler Bestand, nicht im Repository)`, Z. 58): „je eine Modulmasse (~50–150 g)“; AP v2.4 Tab. `aufbau` (Z. 2038–2041): M ≈ 0,65 kg, 50 bis 150 g je Modul. [Q] **„0,650 kg je Modul“ ist verifiziert**: `(lokaler Bestand, nicht im Repository)`, Z. 65: „M = 0,650 kg je Modul · 3 Module · f = 2,2 Hz · Egg-Profil mit T_f/T ≈ 0,80“ (L6b-073: ersetzt; FV v2.7 Anh. B „Getrennte Parameterstände“ nennt ihn ebenfalls). [R] μ = 3m_j/M: 0,231 (3 × 50 g) … 0,692 (3 × 150 g). Bei 10 Hz und Referenzhub: ε = 0,275 / 0,550 / 0,824 für 3 × 50/100/150 g; ΔF_Zelt (starr) 0,271 / 0,541 / 0,812 N; synchrone Reserve 72,5 / 45,0 / 17,6 %. 3 × 50 g verfehlt das Signalkriterium (Hub ≥ 13,3 mm nötig), 3 × 150 g verfehlt die 25-%-Reserve synchron. Index-Szenario (3 × 0,650 kg, m₀ = 0, 2,2 Hz, gerechnet mit dem TH = 0,65-Profil [A]): ε = 0,058, ΔF_Zelt = 0,170 N; Hub ≥ 21,2 mm nötig. **Bestätigt**; Konflikt ist real und quantitativ wesentlich.

**Reproduktion.** `python3 a1b_zusatz.py`.

## AUS-06 · Lineares Dauerkontaktmodell mit bewegtem Massenanteil μ (Herleitung und Abgleich)

**Herleitung** [R]. Körper (Gehäuse, Restmasse m₀) mit Vertikalkoordinate x (x < 0: Kontakt eingefedert), Module j = 1…3 mit Masse m_j und vorgegebener Relativlage z_j(t) = z(t − τ_j), τ_j = φ_j/(2πf); M = m₀ + Σm_j; einseitiger Kontakt N = max(0, −Kx − Cẋ) für x < 0. Impulssatz des Gesamtsystems (innere Antriebskräfte heben sich auf):

  M·ẍ + Σ_j m_j·z̈_j(t) = N − M·g.

Im Dauerkontakt mit y = x + Mg/K: **M·ÿ + C·ẏ + K·y = −Σ_j m_j·z̈_j(t)**, N = Mg − Ky − Cẏ. Für die Harmonische e^{ikωt} mit z̈_j ↔ P_k·e^{−ikφ_j}:

  N_k = H(kω)·Σ_j m_j·P_k·e^{−ikφ_j},  H(ω) = (K + iωC)/(K − Mω² + iωC),  Y_k = −Σ_j m_j P_k e^{−ikφ_j}/(K − Mk²ω² + ikωC).

Bei gleichen Modulen m_j = μM/3 und Laufgewichten w_j ∈ {0, 1} (w_j = 0: Modul geparkt): **N_k = μM·H(kω)·P_k·Φ_k/3**, Φ_k = Σ_j w_j e^{−ikφ_j}. Folgerungen: (1) **H enthält die Gesamtmasse M, nicht m₀ oder μM**: f_n = √(K/M)/2π hängt nicht von μ ab; μ skaliert nur die Anregung. Voraussetzung: Module kinematisch starr geführt (keine Antriebsnachgiebigkeit [A]). (2) Der Phasenfaktor ist auf ein Modul normiert: N_k = Φ_k·N_k⁽¹⁾ mit N_k⁽¹⁾ = m_j·H·P_k (FV v2.7 Gl. `phasenfaktor`, ohne 1/3); `linear_solver.py` schreibt dasselbe als μM·H·P_k·(Φ_k/3). Ein Fehler entstünde nur, wenn man m_j mit Φ_k/3 kombiniert (doppeltes 1/3). (3) Einzelmodul(μ) ≡ synchron(μ/3) (Präreg A2.1).

**Abgleich** [R]. 384 Vergleiche mit `linear_solver.solve` (Zahlen oben); N_k − Φ_k·N_k⁽¹⁾ ≤ 3·10⁻¹⁷ N an (120°,240°), (110°,250°), (0°,180°), (0°,0°); Einzelmodul(μ = 0,4) und synchron(μ/3) identisch (F_min 5,264385 N auch in linear_solver).

**Ähnlichkeitsgesetz** [R]. Mit ε = μ·a_h/g, a_h = π²·Hub·f²/TH (größte Abwärtsbeschleunigung der Haltephase; Hub = Spitze-Spitze = RTOP + RBOT, Referenz 7,6923 mm, a_h = 11,680 m/s² bei 10 Hz), ρ = f/f_n, ζ = C/(2√(KM)) gilt im Kontaktast exakt

  **N(t)/(Mg) = 1 + ε·g̃(t; φ, w, ρ, ζ)**.

Nachweis: Satz A (μ = 1, 10 Hz, K = 10⁴, Hub 7,69 mm) und Satz B (μ = 0,5, 5 Hz, K = 2500, Hub 61,54 mm), gleiches ε = 1,1906 und ρ = 0,5066: max|N_A − N_B| = 0 N; ebenso M = 0,65 → 1,3 kg bei gleichem (ε, ρ, ζ). Der vierdimensionale Raum (Hub, K, f, μ) reduziert sich damit auf (ε, ρ) bei gegebenem ζ; M setzt nur den Kraftmaßstab.

**Reproduktion.** `python3 a2_lineares_modell_abgleich.py`.

**Bewertung.** linear_solver bestätigt (Übertragungsfunktion, Normierung, μ-Behandlung). Einschränkung des Codes: M ist dort fest 0,65 kg, Einzelmodul- und Paarläufe sind nur über die μ/3-Äquivalenz bzw. gar nicht abbildbar (keine Gewichte w_j); `waveform` und `orbit_state` ignorieren `f_hz`.

## AUS-07 · Skalierung von F_min, F_max, Harmonischen, ΔF_Zelt und Sekanten

[R] Aus AUS-06: F_min = Mg·(1 − ε·G), F_max = Mg·(1 + ε·Ĝ), N_k = Mg·ε·n_k(φ; ρ, ζ), ΔF_Zelt = Mg·ε·ΔG(ρ, ζ), Sekanten = Mg·ε·S(ρ, ζ). Also **∝ M·μ·Hub·f²** bei festem ρ und ζ; K und f wirken zusätzlich über ρ = 2πf·√(M/K). Schiefe, A und Lage der Zeltspitze hängen nur von (φ, ρ, ζ) ab, nicht von ε.

Starre Grenzwerte (ρ → 0; je Mg·ε) [R]:

| Größe | Wert | 25-%-Grenze ε ≤ 0,75/G |
|---|---|---|
| G synchron | 1,00000 | 0,750 |
| G Paar (zwei Module, Δ = 0°) | 0,66667 | 1,125 |
| G (0°, 180°) | 0,44206 | 1,697 |
| G Piloten (max) | 0,40479 | 1,853 |
| G Schnitt (Ränder 100°/140°) | 0,39534 | 1,897 |
| G Einzelmodul | 0,33333 | 2,250 |
| Ĝ synchron (F_max) | 1,85714 = TH/TF | – |
| ΔG_Zelt | 0,15453 | – |
| 2°-Sekanten S_L / S_R | 0,015428 / 0,015426 1/° | – |
| D₁ / D₂ / D₃ | 0,1483 / 0,0963 / 0,1822 | – |

Zahlenbeispiele (ζ = 0,1, a2): starr μ = 0,4 → μ = 0,2 halbiert alle Abweichungen von Mg exakt; Hub ×2 und f ×√2 sind gleichwertig (beide ε = 0,9525). K = 10⁶ (ρ = 0,051): ΔF_Zelt 0,4680 statt 0,4693 N; K = 10⁵ (ρ = 0,160): 0,4367 N, Sekanten 0,0366/0,0378; K = 10⁴ (ρ = 0,507): 1,8148 N, Sekanten 0,0845/0,0776 (Resonanz der 2. Harmonischen).

**Reproduktion.** `python3 a2_lineares_modell_abgleich.py`, `python3 a3a_G_funktionen.py`.

## AUS-08 · Zulässiger Bereich in (ε, ρ, ζ) bzw. (Hub, K, f, μ)

**Frage.** Wo gelten gleichzeitig (i) 25-%-Reserve für alle Läufe, (ii) 3f ≤ f₁/2, (iii) PB1-Signal?

**Kriterien.** (i) F_min ≥ 0,25·Mg; Zelle = Summe/3 [A: Modulkräfte wirken im Flächenschwerpunkt des Zelldreiecks]; Laufmengen PFLICHT = 21 Schnittpunkte + 3 Piloten + Einzelmodule (Präreg §5.3(a)), ZUSATZ = PFLICHT + (0°,180°) + synchron (H4-Zusatzkonfigurationen, „falls zulässig“), ALLE = ZUSATZ + Zweierkombinationen (zwei Module laufen, im Präreg nicht geplant, Δ = 0…355°). Ungünstigster Paarlauf ist immer Δ = 0. (ii) ρ ≤ 1/6, f₁ = f_n des 1-FG-Modells [A: Kippmoden nicht modelliert]. (iii) ΔF_Zelt ≥ 0,4693 N ⇔ PB1-Anforderung nicht strenger als u_c ≤ 0,0327 N (ν → ∞); allgemein u_c,req = 0,25·ΔF_Zelt/c. Dämpfung: **ζ fest** (nicht C), weil ζ allein die Resonanzüberhöhung bestimmt und wie in AP v2.4 (Sensitivität „ζ fest“) übertragbar ist; gerechnet mit ζ = 0,02 / 0,05 / 0,1 / 0,2, da ζ des realen Aufbaus unbekannt ist (P0.4).

**Ergebnis** [R].
- **Starrer Grenzfall:** ε_sig = 0,4763 (Signal), ε_max = 0,750 (ZUSATZ/ALLE, synchron bindend), 1,853 (PFLICHT, Piloten bindend; ohne Piloten Schnittränder 1,897). Das ZUSATZ-Fenster ist schmal: **ε ∈ [0,476; 0,750]**, d. h. ΔF_Zelt ∈ [0,469; 0,739] N bei M = 0,65 kg.
- **(ii) genügt nicht für (i) bei schwacher Dämpfung.** (a) wird „ohne Bandbegrenzung“ vorhergesagt; dann regen hohe Profilharmonische (k ≈ 1/ρ) die Kontaktresonanz an. ζ = 0,02: G_syn bis 1,79 bei ρ → 1/6 (ε_max 0,419), Spitze verschoben auf 100°–104° bei ρ ≈ 1/12, 1/9, 1/6; ζ = 0,05: G_syn bis 1,28; ζ = 0,1: ≤ 1,10; ζ = 0,2: ≤ 1,03.
- Anteil zulässiger ρ ∈ (0, 1/6] (Raster 0,001) für ZUSATZ: 89,2 % (ζ = 0,02), 94,3 % (0,05), 100 % (0,1 und 0,2). **Resonanzlücken** (ε-Fenster < 0,15 bei mindestens einem ζ ≥ 0,02): ρ ≈ 0,053–0,055, 0,062–0,067, 0,077–0,084, 0,100–0,112, 0,138–0,141 (k = 18, 15/16, 12/13, 9/10, 7). **Robust für alle ζ ≥ 0,02: ρ ≤ 0,052**, d. h. f_n ≥ 19·f.
- Abweichung der normierten Kennzahlen vom starren Wert für ρ ≤ 0,04: ζ = 0,02: G_syn 3,4 %, ΔG 6,5 %, Sekanten bis 20 %; ζ = 0,05: G_syn 0,7 %, ΔG 1,3 %, Sekanten 3,7 %; ζ ≥ 0,1: ≤ 0,6 % (G_Schnitt bis 5 %, weil F_min am Schnittrand von hohen Harmonischen abhängt).
- **Physikalische Umrechnung:** K ≥ M·(12πf)² = 924·f² N/m für (ii) (10 Hz: 92,4 kN/m; 12 Hz: 133 kN/m; 14 Hz: 181 kN/m); robust ρ ≤ 0,05: K ≥ 1,03·10⁶ N/m (10 Hz), 1,48·10⁶ (12 Hz), 2,01·10⁶ (14 Hz). Hubfenster (starr, ZUSATZ) Hub ∈ [0,3077; 0,4846] m·Hz²/(μ·f²), z. B. 10 Hz, μ = 0,4615 (3 × 100 g): **6,67–10,50 mm**; 12 Hz, μ = 0,4: 5,34–8,41 mm; 14 Hz, μ = 0,231 (3 × 50 g): 6,80–10,71 mm (vollständige Tabelle `a3b_hubfenster.csv`).

**Reproduktion.** `python3 a3a_G_funktionen.py && python3 a3b_arbeitspunkte.py`.

**Einschränkungen.** Lineares Modell mit idealem Egg-Profil (Beschleunigung C⁰, |P_k| ~ k⁻²); reale Profile haben ein anderes Hochfrequenzspektrum (P0.5 misst es). Zellmodell Summe/3 ist eine Annahme (AUS-09).

## AUS-09 · Zellmodell: Summe/3 gegen Präreg A2.5

[Q] Präreg A2.5: „jedes Modul über einer Zelle … deshalb trägt Zelle j bei jeder Phasung M·g/3 + m_j·a_j(t − τⱼ). Ihr Minimum ist … ein Drittel des Minimums der synchronen Phasung, unabhängig von φ₂ und φ₃.“ [R] Folge: In diesem Zellmodell (quasistatisch) gilt für **jede** Konfiguration je Zelle die Reserve der synchronen Phasung, 1 − ε (starr). Die Laufmenge spielt dann keine Rolle; ε ≤ 0,75 ist bindend, also genau der Fall „synchron als ungünstigster Fall“. Mit dem Aufgaben-Zellmodell Summe/3 ist synchron nur bindend, wenn es gemessen wird; ohne synchron (PFLICHT) wäre ε bis ≈ 1,1 zulässig (Paare Δ = 0, falls gemessen) bzw. bis 1,85. **Die Lage von Modulen und Zellen ist damit ein Auslegungshebel**: Wirken die Modulkräfte nahe dem Zellschwerpunkt (z. B. Module auf der Mittelachse), steigt das zulässige ε und damit ΔF_Zelt um bis zu ≈ 50 % (V5). Kippdynamik bei endlicher Zellsteifigkeit kann Einzelzellen stärker entlasten; das rechnet eine andere Gruppe und ist hier nicht enthalten.

## AUS-10 · Arbeitspunktvorschläge (lineares Modell, M = 0,65 kg)

[R] Reserven = kleinstes F_min/Mg je Lauftyp (Zelle = Summe/3; „synchron“ ist zugleich die Zellreserve im Modell A2.5). Zahlen bei ζ = 0,05 (in Klammern ζ = 0,02 / 0,1). Robustheit: schlechtester Wert über K ∈ [0,7; 1,3]·K_nenn und ζ ∈ {0,02; 0,05; 0,1; 0,2}.

| | V1 | V2 | V3 | V4 | V5 |
|---|---|---|---|---|---|
| Kurzname | Laborplan-Mitte, steif | Referenzhub 12 Hz, steif | leichte Module 14 Hz | weicher Kontakt (Pad) | nur PFLICHT, Wirkung im Zentrum |
| Hub [mm] | 8,00 | 7,69 | 8,00 | 8,00 | 7,69 |
| f [Hz] | 10 | 12 | 14 | 10 | 12 |
| μ (m_j) | 0,462 (100 g) | 0,400 (87 g) | 0,231 (50 g) | 0,462 (100 g) | 0,600 (130 g) |
| K [kN/m] | 1500 | 2500 | 3000 | 320 | 2500 |
| f_n [Hz]; 3f/f_n | 241,8; 0,124 | 312,1; 0,115 | 341,9; 0,123 | 111,7; 0,269 | 312,1; 0,115 |
| ε | 0,571 | 0,686 | 0,560 | 0,571 | 1,029 |
| Reserve Einzelmodul | 81 % | 77 % | 81 % | 80 % (77/81) | 66 % |
| Reserve Paar Δ = 0° | 62 % | 54 % | 62 % | 59 % (55/61) | 31 % |
| Reserve synchron (= Zelle A2.5) | 43 % (42/43) | 31 % (29/31) | 44 % (43/44) | 39 % (32/42) | **−3 % (hebt ab)** |
| Reserve (0°, 180°) | 74 % | 68 % | 74 % | 71 % | 53 % |
| Reserve Piloten | 76 % | 71 % | 76 % | 74 % | 56 % |
| Reserve Schnitt | 76 % | 71 % | 77 % | 72 % (68/74) | 57 % |
| ΔF_Zelt voll / bandbegr. [N] | 0,560 / 0,588 | 0,678 / 0,711 | 0,546 / 0,576 | 0,791 / 0,724 (1,127 bei ζ = 0,02) | 1,016 / 1,066 |
| 2°-Sekanten s_L / s_R [N/°] | 0,0545 / 0,0571 | 0,0704 / 0,0669 | 0,0527 / 0,0551 | 0,0608 / 0,0632 | 0,1056 / 0,1003 |
| Zeltspitze | 120° | 120° | 120° | 120° (106° möglich) | 120° |
| PB1: u_c,req F_min / N_k (ν → ∞) [N] | 0,039 / 0,025 | 0,047 / 0,030 | 0,038 / 0,024 | 0,055 / 0,025 | 0,071 / 0,044 |
| größte Zellkraft [N] (statisch 2,126) | 4,39 | 4,86 | 4,34 | 4,51 | 3,49 (PFLICHT) / 6,23 (A2.5) |
| Robust: Reserve ≥ / ΔF_Zelt ≥ | 39,6 % / 0,513 N | 28,5 % / 0,639 N | 41,3 % / 0,516 N | 31,9 % / **0,273 N** | 53,2 % / 0,958 N |
| Bewertung | zulässig, robust | zulässig, robust, Reserve knapp | zulässig, robust | nur bei gemessenem ζ ≥ 0,1 und genau bekanntem K | nur ohne synchronen Lauf und mit Modulwirkung im Zellschwerpunkt; verletzt A2.5 |

Nennlast: [R] größte erwartete Zellkraft im Kontaktast 4,3–4,9 N (≈ 0,45–0,5 kg) bei V1–V4; [Q] Präreg §5.1 verlangt die Nennlast „einschließlich E1 mit Sicherheitsfaktor“; E1-Spitzen siehe AUS-13. Die Steifigkeiten 1,5–3·10⁶ N/m sind Zielwerte; ob drei Wägezellen dieser Nennlast samt Gehäuse sie erreichen, ist im Bestand nicht belegt (keine Datenblattwerte gefunden) und wird in P0.4 gemessen.

**Reproduktion.** `python3 a3b_arbeitspunkte.py` (≈ 1 min).

## AUS-11 · Nichtlineare Stichprobe: gilt die lineare Vorhersage?

**Methode.** [R] RK4-μ-Engine (einseitiger Kontakt, Standardstart, 8 s, Auswertung der letzten 5 s), je 30 Läufe (Einzelmodul, Paare Δ = 0/120/180°, synchron, (0°,180°), 3 Piloten, 21 Schnittpunkte) an V1 (ζ = 0,05), V2 (ζ = 0,02), V4 (ζ = 0,02 und 0,1), V5 (ζ = 0,05).

**Ergebnis.** In allen Läufen mit linearem Kontaktast **λ = 0**; max|F_min,RK4 − F_min,lin| = 1,1·10⁻⁵ N (V1), 2,3·10⁻⁵ (V2), 1,0·10⁻⁵ (V4 ζ = 0,02), 5,7·10⁻⁶ (V4 ζ = 0,1), 2,6·10⁻⁵ (V5); |ΔN_k| ≤ 6,5·10⁻⁷ N; |⟨N⟩ − Mg| ≤ 3,2·10⁻⁷ N; ΔF_Zelt RK4/linear 0,56023/0,56023 (V1), 0,72417/0,72414 (V2), 1,12668/1,12667 (V4 ζ = 0,02), 0,62889/0,62888 (V4 ζ = 0,1), 1,01649/1,01649 (V5); Sekanten auf 10⁻⁵ N/° gleich, Spitze überall 120°. Die Restabweichungen ~10⁻⁵ N entstehen, wenn τ_j kein ganzzahliges Vielfaches von Δt ist (Abtastung). V5 synchron (lineares F_min = −0,222 N = −3,5 % Mg): RK4 λ = 25,15 %, F_max 19,22 N (linear 18,68) – **schon eine kleine negative lineare Reserve führt bei steifem Kontakt zu 25 % Liftoff (harter Übergang)**, anders als beim weichen Referenzkontakt (AUS-02, stetiger Anstieg ab 1,9 %). **Bestätigt** für Läufe vom Standardstart; Einschränkung siehe AUS-12.

**Reproduktion.** `timeout 540 python3 a4_rk4_stichprobe.py V1z05` (analog V2z02, V4z02, V4z10, V5z05; je 25–40 s).

## AUS-12 · Kontaktast bei steifem Kontakt nicht global anziehend (Hüpfzustände)

**Frage.** Erreicht der Körper den Kontaktast auch nach einer Störung? (`linear_solver.py` meldet für die Referenz die Hauptgebiete „in allen Proben“ monostabil.)

**Methode.** [R] RK4-μ-Engine, Wurfstart ż₀ aus der statischen Ruhelage bei t = 0, 16 s, Auswertung der letzten 4 s. Referenz-Gegenprobe (K = 10⁴, ż₀ = 3 m/s, 15 s/10 s); V1 über ζ = 0,02/0,05/0,1/0,2 an (120°,240°) und synchron, ż₀ = 0,05/0,1/0,2/0,5 m/s; V2 (ζ = 0,02); Zeitschritt T/2000, T/4000, T/8000 und 40 s Laufzeit (a4d); Schwelle von ż₀ (a4c). Restitutionskoeffizient des Kelvin-Voigt-Stoßes e = exp(−πζ/√(1−ζ²)): 0,939/0,854/0,729/0,527.

**Ergebnis.** Referenz: (98°/120°/148°, 240°) mit ż₀ = 3 m/s → λ = 0 (bestätigt die Angabe von linear_solver). **V1 synchron, ż₀ = 0,5 m/s (Fallhöhe 12,7 mm): dauerhafter Hüpfzustand mit λ ≈ 98 % und Stoßspitzen 484–490 N (≈ 76·Mg) für ζ = 0,02, 0,05 und 0,1**; für ζ = 0,2 Rückkehr in den Kontaktast. ż₀ ≤ 0,2 m/s (h ≤ 2 mm): überall Rückkehr. V1 (120°,240°): bis 0,5 m/s Rückkehr für alle ζ. **V2 (ζ = 0,02), (120°,240°), ż₀ = 0,5 m/s: λ = 94,18 % bei Δt = T/2000, aber λ = 0 bei Δt = T/4000** – ebenso λ = 0 bei Δt = T/8000 (a4d C): **der Hüpfbefund an diesem Punkt ist ein Zeitschritt-Artefakt der groben Schrittweite und wird verworfen**; die übrigen V2-Wurfproben (Einzelmodul und synchron bei 0,5 m/s ≈ 98 %, Schnittränder bei 1,5 m/s λ 30–41 %, alle Δt = T/2000) sind nicht zeitschrittgeprüft. Schwelle (a4c): V1 synchron (ζ = 0,05) kehrt bis ż₀ = 0,25 m/s (h = 3,2 mm) zurück, ab 0,30 m/s (h = 4,6 mm) Hüpfzustand (λ ≈ 98 %, F_max ≈ 485 N); V2 Triphasik (ζ = 0,02) bis 0,40 m/s (8,2 mm) zurück (0,50 m/s siehe oben: Artefakt). **Zeitschritt- und Laufzeitprüfung (a4d):** V1 synchron, ζ = 0,05, ż₀ = 0,30/0,50 m/s: Δt = 25 µs (16 s) λ = 97,990/97,988 %, F_max 484,99/484,66 N; Δt = 50 µs über 40 s λ = 97,985/97,993 %, F_max 485,39/485,52 N; je ein Stoß pro Anregungsperiode (Abstände 1,000 ± 0,004 T), Kontaktdauer ≈ 2 % der Periode ≈ π/ω_n. **Der synchrone Hüpfzustand ist ein zeitschrittfester, dauerhafter Endzustand.** **Neu**: Bei steifem, schwach bis mäßig gedämpftem Kontakt (ζ ≤ 0,1) koexistieren der Kontaktast und Hüpfzustände (Prallkugel-Dynamik); der Standardstart (Module setzen aus der Ruhe ein) landet auf dem Kontaktast, eine Störung von wenigen mm Fallhöhe (synchron V1: ≥ 4,6 mm) nicht. ζ = 0,2 beseitigte den Hüpfzustand in der Probe.

**Reproduktion.** `timeout 540 python3 a4b_bistabilitaet.py` (≈ 5–7 min), `timeout 540 python3 a4c_einzugsbereich.py`, `python3 a4_rk4_stichprobe.py start`, `timeout 540 python3 a4d_konvergenz.py A` (analog `B`, `C`; Teil `D` mit Δt = T/8000 nicht ausgeführt).

**Einschränkungen.** Kelvin-Voigt-Kontakt mit geschwindigkeitsunabhängigem ζ; reale Füße/Wägezellen haben nichtlineare Kontaktsteifigkeit, Seitenführung und Kippfreiheitsgrade; Einzugsbereich nur stichprobenartig. Fälle nahe der Einzugsgrenze sind zeitschrittempfindlich (V2 Triphasik: Artefakt); belastbar ist der zeitschritt- und laufzeitgeprüfte synchrone V1-Fall (Schwelle zwischen 0,25 und 0,30 m/s; 0,30 m/s auch bei Δt/2 bestätigt).

## AUS-13 · E1 und Nennlast bei steifem Kontakt

**Frage.** Welche Spitzenkräfte entstehen, wenn ein steifer Aufbau abhebt (E1: höheres f, Präreg §3)?

**Methode.** [R] RK4-μ-Engine, V1-Parameter (K = 1,5·10⁶ N/m, ζ = 0,05), synchron, f = 12/13/14/16 Hz, Standardstart, 8 s/letzte 5 s.

**Ergebnis.** 12 Hz (ε = 0,823, linear F_min +1,06 N): λ = 0, F_max 16,29 N. 13 Hz (ε = 0,966, +0,14 N): λ = 0, 17,88 N. **14 Hz (ε = 1,120, linear F_min −0,92 N): λ = 96,96 %, F_max = 589,7 N (92·Mg)**; 16 Hz: λ = 98,20 %, F_max = 991,4 N (155·Mg). Zeitschrittprüfung (a4d C): 14 Hz mit Δt = 17,9 µs statt 35,7 µs: λ = 97,19 %, F_max = 360,0 N, Stoßfolge mit Periode 2 (Abstände 0,70/1,30 T) – **Größenordnung (einige 10²·N, 56–92·Mg) robust, Einzelwert nicht zeitschrittfest**. Zum Vergleich Referenz (K = 10⁴): Spitzen ≈ 41–51 N (finesweep (0°,0°): 41,12 N; AP v2.4 Kap. 5: „7,9-fache … rund 51 N“). Die Stoßspitze wächst etwa mit v_Stoß·√(K·M) [A, Kelvin-Voigt-Abschätzung]; √(KM) ist bei K = 1,5·10⁶ N/m √150 ≈ 12-mal größer als bei 10⁴ N/m. **Neu**: Im steifen V1-Regime bestimmen nicht die Kontaktast-Kräfte (≤ 4,9 N je Zelle), sondern E1- und Hüpfzustände die Nennlast; sie liegen zwei Größenordnungen höher. Eine Nennlastwahl „einschließlich E1“ (Präreg §5.1) ist mit kleinen Wägezellen und steifem Kontakt nicht erfüllbar; E1 braucht Überlastanschlag oder eine eigene, weichere Kontaktstufe.

**Reproduktion.** `timeout 540 python3 a4_rk4_stichprobe.py E1` (≈ 2,5 min).

**Einschränkungen.** Wie AUS-12; Spitzen im Hüpfzustand hängen stark von der Kontaktnichtlinearität ab; die Größenordnung ist belastbar, der Einzelwert nicht.

## AUS-14 · Was skaliert nur, was ändert sich qualitativ (Aufgabe 5)

**Methode.** [R] Normierte, ε-unabhängige Kennzahlen (a5) für Referenz, starren Grenzfall, A4-Beispiel und V1–V4; Kontaktanteil im Phasenraster; Abweichung vom starren Wert über ρ (a3a); Gegenprobe Präreg A3 (Kontaktanteil bei μ = 0,5).

**Ergebnis.**

| Kennzahl | Referenz (ρ = 0,507) | starr | V1 / V2 / V3 (ζ = 0,05, ρ ≈ 0,04) | Art der Änderung |
|---|---|---|---|---|
| (Mg − F_min(120°))/(Mg·ε) | 0,138 | 0,241 | 0,266 / 0,263 / 0,266 | qualitativ (Referenz: k = 3 über der Resonanz gedämpft, |H₃| = 0,78) |
| ΔG_Zelt | 0,601 | 0,1545 | 0,154 / 0,155 / 0,153 | qualitativ (Faktor 3,9 durch 2f ≈ f_n) |
| Sekanten S_L / S_R [1/°] | 0,0280 / 0,0257 | 0,0154 / 0,0154 | 0,0149/0,0157; 0,0161/0,0153; 0,0148/0,0154 | qualitativ (Überhöhung 1,8 entfällt) |
| s_L/s_R (Zeltasymmetrie) | 1,088 | 1,000 | 0,955 / 1,053 / 0,956 | qualitativ (Vorzeichen der Asymmetrie hängt von ρ ab; starr symmetrisch) |
| Lage der Zeltspitze | 120° | 120° | 120° | bleibt, außer bei ζ ≲ 0,05 nahe ρ ≈ 1/6, 1/9, 1/12 (bis 100°–106°) |
| γ₁ am Triphasik-Punkt | +0,067 | −0,450 | −0,492 / −0,485 / −0,492 | Vorzeichenwechsel |
| γ₁ auf dem Schnitt | −0,385 … +0,067 | −0,793 … −0,450 | −0,80 … −0,49 | qualitativ |
| γ₁ synchron / (0°,180°) / Einzelmodul (linear) | +0,14 / +0,04 / +0,14 (heben ab) | +0,755 / +0,986 / +0,755 | +0,76 / +0,98 / +0,76 | qualitativ (Referenzläufe haben keinen Kontaktast) |
| A bei 120° | 1,066 | 0,653 | 0,612 / 0,598 / 0,608 | qualitativ |
| Kontaktanteil Phasenraster (2°) | 4,19 % | 76,6 % (μ = 1) | 100 % | qualitativ: kein Liftoff mehr in der Phasenebene |
| |H₂| | 5,03 | 1 | 1,007 / 1,006 / 1,007 | Resonanznähe der 2. Harmonischen entfällt |
| größtes |H(kω)| | 5,03 (k = 2) | 1 | ≈ 10 bei k = 24/26/24 | neue Empfindlichkeit: hohe Profilharmonische |

- **Nur Skalierung (gleiches ρ, ζ):** Ändert man bei K = 10⁴ N/m nur μ (1 → 0,4), bleiben alle normierten Kennzahlen gleich (G120 = 0,1378, ΔG = 0,601, γ₁ = +0,067, s_L/s_R = 1,088); F_min(120°) = Mg − 1,0461 N·μ (5,958 N bei μ = 0,4). Nicht linear ist dagegen der Kontaktanteil (Schwellengröße): 4,24 % (μ = 1), 48,59 % (μ = 0,5; Präreg A3: 48,6 % – bestätigt), 71,84 % (μ = 0,4), 1°-Raster.
- **Innerhalb des neuen Bereichs (ρ ≤ 0,05, ζ ≥ 0,05)** skaliert alles in guter Näherung mit ε: Abweichungen vom starren Wert ≤ 1,5 % (G_syn), ≤ 3,3 % (ΔG), ≤ 8,2 % (Sekanten), ≤ 7,8 % (G_Schnitt). Das A4-Beispiel der Präregistrierung (starr, μ = 0,4) ist deshalb auf V1–V3 übertragbar, die Referenzzahlen (5,33 N, 0,212/0,195 N/°, 0,228/0,186 N/°, ΔF_Zelt 4,56 N, 4,24 % Kontaktanteil, γ₁ = +0,067, Liftoff-Tabellen) nicht.
- **Neu und qualitativ:** (1) Die Resonanznähe der 2. Harmonischen entfällt; dafür werden hohe Profilharmonische (k ≈ f_n/f ≈ 20–30) bis |H| ≈ 10 überhöht und verschieben das ungebänderte F_min am Triphasik-Punkt um ≈ 10 % von G (≈ 0,1 N bei ε ≈ 0,57); Bedingung (a) hängt damit vom Hochfrequenzspektrum des realen Profils ab. (2) Der Übergang zum Liftoff ist hart (AUS-11, V5), es gibt Hüpfzustände (AUS-12). (3) Spitzenkräfte außerhalb des Kontaktasts steigen um zwei Größenordnungen (AUS-13).

**Reproduktion.** `python3 a5_qualitativ.py`, `python3 a5b_kontaktanteil_mu.py`.

## AUS-15 · Widerspruch AP v2.4 „Auslegungsbedingung“ ↔ Präreg §5.3(a)/A2.5

[Q] AP v2.4, Kap. 5 (Z. 2110–2117): „Frequenz, Masse und Kontaktsteifigkeit sind so abzustimmen, dass in einem Teil der Phasenlagen tatsächlich Liftoff auftritt.“ [R] Im quasistatischen Bereich ist die synchrone Phasung der globale ungünstigste Fall (N − Mg = μM·ā(t) ≥ μM·min a). Erfüllt der Arbeitspunkt (a) für die ZUSATZ-Menge oder im Zellmodell A2.5, hat **kein** Punkt der Phasenebene Liftoff (V1–V3: Kontaktanteil 100 %). Beide Forderungen sind bei einer Frequenz unvereinbar; Liftoff ist dann nur über E1 (höheres f) erreichbar – mit den Spitzen aus AUS-13. Nur die PFLICHT-Menge mit Modulwirkung im Zellschwerpunkt (V5) lässt Liftoff nahe der synchronen Phasung zu.

## AUS-16 · Folgerung aus P1 §3.1 für Einzelmodulläufe

[Q] P1 §3.1: „Einzelmodulläufe brauchen reduzierten Hub mit Linearitätsnachweis.“ [R] Das gilt für den Simulationsreferenzsatz (Grenze 56,7 % Hub mit Reserve, AUS-02). In jedem Arbeitspunkt, der die synchrone 25-%-Reserve erfüllt, hat ein Einzelmodul im quasistatischen Bereich die Reserve 1 − ε/3 ≥ 75 % (V1–V4: 77–81 %); ein reduzierter Hub ist dann nicht nötig. Bindend sind synchron (bzw. Zellmodell A2.5) und Paare mit Δ = 0, nicht die Einzelmodule. **Teilweise widerlegt** (Folgerung gilt nur für den Referenzsatz).

## AUS-17 · §5.3(b) schützt Bedingung (a) nicht vor resonanten hohen Harmonischen

[Q] Präreg §5.3(b): „3f ≤ f₁/2 … nur Harmonische mit k·f ≤ f₁/2 werden ausgewertet. Dann ist |H| ≤ 1,33 …“; §5.3(a): Vorhersage „ohne Bandbegrenzung“. [R] (a3a/a3b) Für ρ ≤ 1/6 bleiben die ausgewerteten |H(kω)|, k ≤ 3, ≤ 1,125; das ungebänderte F_min hängt aber von Harmonischen k ≈ 1/ρ ab. Bei ζ = 0,02 steigt G_syn bis 1,79 (ρ → 1/6), G_Schnitt bis 1,09 statt 0,40, die Zeltspitze wandert bei ρ ≈ 1/12, 1/9, 1/6 auf 100°–104°, und ΔG fällt in Bändern bei ρ ≈ 1/18, 1/15, 1/12, 1/9, 1/7 unter 90 % des starren Werts; bei ζ = 0,05 G_syn bis 1,28, bei ζ = 0,1 bis 1,10. Präreg A5 nennt nur den Fall 6f = f_n. **Teilweise**: Die Aussage zu |H| gilt für die ausgewerteten Harmonischen, sichert aber weder (a) noch die Lage der Spitze gegen K- und ζ-Unsicherheit. Marge: ρ ≤ 0,05 (alle ζ ≥ 0,02) oder gemessenes ζ ≥ 0,1.

**Reproduktion.** `python3 a3a_G_funktionen.py && python3 a3b_arbeitspunkte.py`.

---

## Korrekturen und Präzisierungen an Quellen

1. **Präreg v2 §5.3(b) / A6** („Dann ist |H| ≤ 1,33 … für jedes ζ ≤ 2“): gilt für die ausgewerteten Harmonischen; Bedingung (a) wird „ohne Bandbegrenzung“ vorhergesagt und hängt trotz (b) von resonanten hohen Harmonischen ab (ζ = 0,02: G_syn bis +79 % bei ρ → 1/6; Lücken bei ρ ≈ 1/7, 1/9, 1/12, 1/15, 1/18). A5 nennt den Fall 6f = f_n nur für einen Punkt. Empfehlung: ρ ≤ 0,05 oder gemessenes ζ ≥ 0,1.
2. **AP v2.4 Kap. 5 „Auslegungsbedingung“** (Liftoff in einem Teil der Phasenlagen): unvereinbar mit Präreg §5.3(a) in der ZUSATZ-Menge bzw. mit Zellmodell A2.5 (AUS-15).
3. **AP v2.4 Kap. 5 „Kraftbereich“ / Präreg A4 „Summenkraft und Nennlast“** (51 N, 101 N, 50,6 N): gelten für K = 10⁴ N/m. Bei steifem Kontakt erreichen E1- und Hüpfzustände 360–990 N (K = 1,5·10⁶ N/m), AUS-13.
4. **`code/linear_solver.py`, Docstring** („Hauptgebiete … in allen Proben“ nicht bistabil): für die Referenz bestätigt, aber nicht auf steife Kontakte übertragbar (AUS-12).
5. **P1 §3.1** „Dauerkontakt nur bis etwa 75 % Hub“: genauer 75,6 % (linear), RK4 zwischen 75,5 und 76 %; mit 25-%-Reserve 56,7 %. Folgerung „Einzelmodulläufe brauchen reduzierten Hub“ gilt nur für den Referenzsatz (AUS-16).
6. **L5a-065, Lückenspalte** (N₂ womöglich strenger): bestätigt, u_c(N₂) ≤ 0,0204 N (ν → ∞) bzw. 0,0168 N (ν = 19) im A4-Beispiel.
7. **P1 §3.2** („Massenkonflikt … Das ändert Anregung und Kontaktresonanz“): Bei fester Gesamtmasse M ≈ 0,65 kg (Laborplan) ändert μ < 1 nur die Anregung; die Kontaktresonanz f_n = √(K/M)/2π enthält die Gesamtmasse und ist von μ unabhängig (AUS-06). Die Resonanz ändert sich nur mit M (Index-Szenario 3 × 0,650 kg: M = 1,95 kg) oder K.

## Empfehlungen für V1

1. Auslegung dimensionslos führen: ε = μ·π²·Hub·f²/(TH·g), ρ = f/f_n, ζ; Ziel ε ≈ 0,55–0,70 (ZUSATZ/A2.5), ρ ≤ 0,05 (f_n ≥ 20·f) solange ζ nicht gemessen ist.
2. Konkrete Startpunkte: V1 (3 × 100 g, 8 mm, 10 Hz, K ≥ 1,5·10⁶ N/m) oder V3 (3 × 50 g, 8 mm, 14 Hz, K ≥ 3·10⁶ N/m); V2 nur mit Reserve-Kontrolle (29–31 %).
3. K und ζ in P0.4 messen, bevor f festgelegt wird; ρ-Bänder um 1/7, 1/9, 1/12, 1/15, 1/18 meiden, wenn ζ < 0,1.
4. Zell- und Modulgeometrie bewusst wählen: Modulwirkung nahe dem Zellschwerpunkt erlaubt ε bis ≈ 1,1 (ΔF_Zelt bis ≈ 1,1 N); jedes Modul über einer Zelle (A2.5) begrenzt ε auf 0,75. Abstimmen mit der Kipp-Gruppe.
5. Kontaktdämpfung erhöhen (ζ ≥ 0,2 beseitigt im Test den Hüpfzustand nach 0,5 m/s Wurf) und Startprozedur festlegen (Module aus der Ruhe mit Rampe, kein Aufsetzen unter Bewegung); Einzelzell-Liftoff-Erkennung über den ganzen Lauf beibehalten.
6. Nennlast und Überlastschutz nach E1/Hüpfzuständen auslegen (Größenordnung 10²·Mg bei steifem Kontakt) oder E1 mit eigener, weicherer Kontaktstufe fahren.
7. PB1 für Re/Im N₂ ist etwa 0,6-mal strenger als für F_min; mit der Statistikgruppe klären, welche Anforderung bindet.
8. Hochfrequenzspektrum des realen Profils in P0.5 bestimmen; es geht in das ungebänderte F_min der Bedingung (a) ein.
9. Die Simulationsreferenzzahlen (5,33 N, Sekanten, Kontaktanteil, γ₁-Vorzeichen) nicht als V1-Erwartung führen; das A4-Beispiel (starr) ist die passende Vorlage und skaliert mit ε.

## Offene Punkte

- Einzelzellkräfte und Kippmoden bei endlicher Zellsteifigkeit (andere Gruppe); erst damit ist die Zellreserve zwischen „Summe/3“ und „A2.5“ festgelegt.
- Reale Steifigkeit von drei Wägezellen der benötigten Nennlast samt Gehäuse und Füßen: im Bestand keine Datenblattwerte; ob 1,5–3·10⁶ N/m erreichbar sind, ist offen.
- Antriebsnachgiebigkeit (Module nicht ideal kinematisch geführt) fügt Freiheitsgrade hinzu, die das μ-Modell nicht enthält.
- Einzugsbereich des Kontaktasts systematisch (über Phasen, ζ, ε) und Hysterese beim Frequenz-Rücklauf aus E1 (E2) nicht gerechnet.
- Erreichbares u_c (Sensorrauschen, Laufzahl) – Statistikgruppe.

