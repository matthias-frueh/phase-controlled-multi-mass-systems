# P2 · Prüfgruppe „kippmoment“ – Einzelzellkräfte und Kippmoment bei drei Wägezellen im Dreieck

> **Vermerk zur Übernahme (04.10.2026).** Protokoll aus der Gesamtprojektanalyse 10/2026, Stand 02.10.2026, unverändert bis auf Pfade und Quellenangaben. Geprüft wurde der Repository-Stand `cd7be6a` (28.09.2026) mit der Präregistrierung v2 vom 25./28.09.2026; die späteren Änderungen aus PR #13 und PR #14 (unter anderem Präregistrierung v2 mit Arbeitsfestlegungen, `code/auslegung.py`, `code/ereignisloeser.py`) sind nicht eingearbeitet. Alle Zahlen sind Simulation oder Analytik, keine Messdaten. Verweise wie „L1a-019“, „P1 §3“ oder „B01–B14“ zeigen auf Arbeitsdokumente der Analyse, die nicht im Repository liegen. Quellen, die nicht im Repository liegen, sind als „(Quelle außerhalb des Repositorys)“ gekennzeichnet. Startbefehle und Grenzen je Gruppe: [`rechnungen/README.md`](../README.md).

Stand 02.10.2026 · ursprünglich lokal, jetzt unter `rechnungen/` · Kennzeichnung: **[R]** eigene Rechnung, **[Q]** Quellenangabe, **[A]** Annahme.

## Dateien und Reproduktion

Alle Befehle aus `rechnungen/kippmoment/` mit

```
PY="PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../../code python3"
```

| Skript | Inhalt | Ausgabe | Laufzeit |
|---|---|---|---|
| `km_modell.py` | gemeinsames Modell: 3-FG starrer Körper auf drei Zellen, linear (Frequenzbereich) und RK4 mit einseitigem Kontakt je Zelle | – | – |
| `k1_harmonische_auswahlregel.py` | Profilharmonische, Auswahlregel, Drehfeld quasistatisch | `k1_..._ausgabe.txt` | < 5 s |
| `k2_linear_3fg.py` | Eigenfrequenzen, Zellkräfte/Summe/Momente für T, Z, S, Fälle × Geometrien | `k2_..._ausgabe.txt`, `k2_linear_3fg.csv` | < 10 s |
| `k2b_umlaufsinn.py` | Umlaufsinn, Rundheit, H_t(kω) | `k2b_..._ausgabe.txt` | < 5 s |
| `k2c_phasen.py` | Phasen der umlaufenden Komponenten | `k2c_..._ausgabe.txt` | < 5 s |
| `k3_rk4_validierung.py` | 3-FG-RK4 gegen Engine und gegen linear, Δt-Konvergenz | `k3_..._ausgabe.txt` | ≈ 4 min |
| `k4_leckage_identifizierbarkeit.py` | 1 %/1°-Störungen, Leckage, Rückrechnung der Modulzeiger | `k4_..._ausgabe.txt` | < 10 s |
| `k5_rk4_einseitig.py REF` / `STEIF` | nichtlinear, einseitiger Kontakt je Zelle, zwei Starts | `k5_..._{REF,STEIF}_ausgabe.txt`, `.csv`, `_reihen.npz` | je ≈ 3 min |
| `k5b_entkopplung_mu1.py` | exakte Entkopplung bei μ = 1, G0; Vergleich mit Engine (0°,0°) | `k5b_..._ausgabe.txt` | ≈ 1,5 min |
| `k6_messbarkeit_auslegung.py` | Rauschmodell, Signale gegen u_c, Zellreserven aller Lauftypen | `k6_..._ausgabe.txt` | < 30 s |

Beispiel: `cd rechnungen/kippmoment && eval timeout 540 $PY k5_rk4_einseitig.py REF`

**Bezeichnungen.** T = (0°, 120°, 240°) Triphasik-Punkt; Z = (0°, 110°, 240°) Zeltschnittpunkt; S = (0°, 0°, 0°) mit Hubfaktor 0,15 (Dauerkontakt). Fälle: REF (K = 10⁴ N/m, C = 16 N·s/m, Engine), STEIF (K = 369 518 N/m, ζ = 0,02, f_n = 120 Hz, Beispiel aus Präreg A5), STARR (quasistatisch, H = 1). μ = 1 (Engine), μ = 0,462 (Laborplan-Mitte: 100 g je Modul bei M = 0,65 kg), μ = 0,4 (Präreg A4). Geometrien [A]: Zellen auf R_c = 100 mm bei 0°/120°/240°; G0 Module über den Zellen (Präreg A2.5), G60 Module um 60° gedreht auf R_c (außerhalb des Stützdreiecks), G0h/G60h Module auf R_c/2 (G60h = Kantenmitten), Z alle Module im Zentrum (≙ „Summe/3“). Rahmen: homogene Scheibe mit Radius R_c (ρ_f = R_c/2) [A], variiert 0,35…0,7·R_c. Moment-Zeiger: R+ = Radius der links (gegen den Uhrzeigersinn von oben) umlaufenden Komponente, R− rechts umlaufend. Amplituden = halbe Spitze-Spitze-Werte einer Harmonischen (2|c_k|).

---

## KM-01 · Geometrieangaben im Bestand

**Frage.** Gibt es Lage von Zellen und Modulen, Plattenmaße, Massen, Trägheitsmomente?

**Methode.** Gezielte Suche (grep) in docs/ und in Quellen außerhalb des Repositorys (Messtechnik-Konzept `4c73fffc`, Präreg v2 + lokale Überarbeitung 01.10., Laborplan V1–V3, Exposé, Baustein 4, Schwellen_eps, Anforderungsprofil, S2-Visualisierungen, Formelverzeichnis v2.7).

**Ergebnis [Q].**
- Präreg v2 Anhang A2.5 (Z. 192–201): Auslegungsannahme „starrer Körper auf drei Zellen, Schwerpunkt … über dem Flächenschwerpunkt des Zelldreiecks, jedes Modul über einer Zelle“; „die Lage ist offen (§12)“. Hauptdokument Z. 557–558: „Lage von Zellen und Modulen (bestimmt die Zellkräfte, A2.5, und E3)“ als offene Klärung. Die lokale Überarbeitung vom 01.10. ist hier unverändert.
- A9.1 (Z. 425–432): drei Zellen im Dreieck, kinematische Lagerung (Kugel–Kegel/–Kerbe/–Ebene) – keine Maße.
- Messtechnik-Konzept `4c73fffc`: keine Geometrie („Wägezelle, einseitige Federlagerung, zwei bis drei phasengesteuerte Massen“).
- Laborplan V1 (Z. 45–66): M ≈ 0,65 kg, Modulmasse ~50–150 g (μ = 0,23–0,69), Hub „einige mm“, **eine** Wägezelle 3–5 kg, ADS1256 ≥ 2 kSPS.
- Baustein 4 §2.2: „Geometrie … noch nicht bindend“, Dreieck S2, Zielarchitektur „pyramidisch-rund“.
- Schwellen_eps (Z. 36, 130–135): „Es gibt keine Standbreite und keine Schwerpunkthöhe“; Kippbedingung F_⊥·h_S < M·g·b/2 offen.
- Einzige Zahlen: Notiz Prüfarchitektur Linie B §6, Z. 148: „Trägheitsradius (… etwa 50 mm)“ als grobe Schätzung (anderer Kontext); S2-Visualisierung `pcmms_s2_dreieck.html` Z. 70: `triRad=0.15` m (Darstellung, keine Konstruktion). Trägheitsmomente: keine.

**Folgerung.** Geometrie fehlt → parametrisiert (s. Bezeichnungen). Ergebnisse für Zellkräfte hängen nur von R_m/R_c, Δψ und ρ/R_c ab; Momente skalieren linear mit R_m (Zahlen für R_c = 100 mm).

**Einschränkung.** Flacher Körper angenommen (Schwerpunkthöhe, Horizontalbewegung, Reibung der kinematischen Lagerung nicht modelliert).

---

## KM-02 · Modell und Validierung

**Modell [R].** Koordinaten q = (z, a, b), w(x, y) = z + a·x + b·y. Zelle j: F_j = max(0, −(K/3)·w_j − (C/3)·ẇ_j) für w_j < 0 (einseitig je Zelle, wie Engine), Modul i mit m_i = μ·M/3 bei (X_i, Y_i), Lage w(X_i, Y_i) + h_i·z_egg(t − τ_i), τ_i = φ_i/(2πf). Lagrange: Mq·q̈ = −g·(M, Σm_iX_i, Σm_iY_i) + Σ_j F_j B_j − Σ_i m_i s̈_i b_i, Mq = diag(M_f, M_fρ_f², M_fρ_f²) + Σ m_i b_i b_iᵀ. Momente M_x = Σ F_j y_j, M_y = −Σ F_j x_j. Bei symmetrischer Anordnung entkoppeln Hub (M, K, C) und Kippen (J = M_fρ_f² + μMR_m²/2, K_t = K·R_c²/2, C_t = C·R_c²/2). Quasistatische Zellkraft eines Moduls: F_j = m_i s̈_i·[1/3 + (2R_m/3R_c)·cos(ψ_i − ψ_j)].

**Prüfung [R]** (`k3_rk4_validierung_ausgabe.txt`):
- Summe der Zellkräfte (bilateral, μ = 1, G0, T) gegen `finesweep.run(120, 240)`: max. Abweichung **3,1·10⁻¹³ N** über 10 s; F_min 5,330390 N, F_max 7,491922 N, ⟨N⟩ = 6,376500000 N wie Engine.
- RK4 bilateral gegen lineare Lösung, 12 Fälle (REF μ = 1/0,462, STEIF μ = 0,462; G0/G60h; T/Z): max|ΔF| ≤ **6,3·10⁻⁶ N**, R+₁, R−₂ auf 5 Stellen gleich.
- Δt-Konvergenz (50 → 25 µs): F_min ändert sich um 6,9·10⁻⁶ N.
- Bei μ = 1, G0 zerfällt das Modell exakt in drei unabhängige Einmassenschwinger (KM-07); Zelle 1 stimmt ab t = 0 punktweise mit der Engine bei (0°, 0°) überein (8,5·10⁻¹⁴ N nach 0,1 s, 7,8·10⁻¹⁰ N nach 1 s).

**Bewertung.** Modell und Implementierung konsistent mit der Engine; Phasenvorzeichen (Verzögerung, e^{−ikφ}) wie `linear_solver.py`; Stichproben am Schrittanfang wie Engine.

---

## KM-03 · Auswahlregel am Triphasik-Punkt

**Frage.** Welche Harmonischen heben sich in Summe bzw. Moment auf?

**Methode [R].** Geometrischer Faktor S_k = Σ_i e^{iψ_i}e^{−ikφ_i} (links), S′_k = Σ_i e^{iψ_i}e^{+ikφ_i} (rechts), Summenfaktor Σ_i e^{−ikφ_i}; numerisch für k = 1…9 (`k1_…`).

**Ergebnis.** Bei φ = (0°, 120°, 240°) und Modulen in Linksreihenfolge (ψ = 0°, 120°, 240°):
- Summe: |Σe^{−ikφ}| = 3 für k ≡ 0 (mod 3), sonst 0.
- Moment: k ≡ 1 (mod 3) → nur links umlaufend (|S_k| = 3), k ≡ 2 → nur rechts umlaufend (|S′_k| = 3), k ≡ 0 → **kein** Moment.
- Bei umgekehrter Zuordnung (ψ = 0°, −120°, −240°) tauschen die Drehrichtungen.
- Einzelzellkraft (G0, quasistatisch): Zelle j = Modul j, alle Harmonischen voll vorhanden.
- Summe und Moment sind komplementär: Was in N fehlt, steht vollständig im Moment und umgekehrt.

**Bewertung.** Präreg v2 §3 E3 (L5a-073: „heben sich … im Allgemeinen nicht auf“) **bestätigt** und präzisiert: In den Zellkräften fehlt keine Ordnung. Im Moment fehlen genau die Vielfachen von 3.

---

## KM-04 · Drehfeld-These: konstanter Betrag?

**Frage (P1 §3 Nr. 5, L4-026).** Umlaufendes Kippmoment „konstanten Betrags (3/2)·m·a₁·r“?

**Methode [R].** Lineare Lösung über einen Zyklus (2000 Stichproben), |M(t)|, Spektrum von |M|, Netto-Umläufe, Mittelwerte; quasistatisch und mit Kippdynamik; Egg (volles Spektrum, k ≤ 6, k ≤ 2) gegen Sinus (`k1_…`, `k2b_…`, `k2c_…`).

**Ergebnis.**
- Egg-Profil, Harmonische der Beschleunigung (Hubfaktor 1): A₁ = 14,965, A₂ = 4,932, A₃ = 2,128, A₄ = 0,322, A₅ = 0,442, A₆ = 0,399 m/s².
- Die Formel (3/2)·m·A₁·R_m ist **exakt der Radius der k = 1-Komponente**: 0,48636 N·m bei μ = 1, R_m = 100 mm; 0,22470 N·m bei μ = 0,462.
- Der Gesamtbetrag ist **nicht konstant**. Quasistatisch, volles Spektrum: |M| = 0,288 … 0,645 N·m (μ = 1), also max/min = **2,24**. Mit k ≤ 2 sind es 1,98, mit k ≤ 6 2,13. Nur das Sinusprofil gibt einen konstanten Betrag (0,49348 N·m, max/min = 1,000).
- |M(t)| enthält nur die Harmonischen 3, 6, 9, 12 (Periode T/3), weil alle Drehraten ≡ 1 (mod 3) sind.
- Die Bahn ist eine dreizählige Rosette: links mit R+₁, rechts mit R−₂ = (A₂/A₁)·R+₁ = 0,33·R+₁.
- Mittelwert des Momentvektors: ⟨M_x⟩, ⟨M_y⟩ ≤ 2·10⁻⁷ N·m linear (Rest Aliasing). Auch in allen nichtlinearen Liftoff-Läufen ist er 0, außer in den chaotischen STEIF-μ = 1-Läufen (≤ 0,004 N·m bei endlichem Fenster). Die Zellmittel sind gleich der statischen Zelllast (≤ 10⁻⁴ N).
- Mit Kippdynamik:
  - STEIF, μ = 0,462: |H_t(ω)| = 1,004–1,007, |H_t(2ω)| = 1,017–1,028; max/min 2,3–2,8 (hohe Harmonische nahe der Kippresonanz).
  - REF, μ = 1, G0: |H_t(2ω)| = 5,03, R−₂ = 0,806 > R+₁ = 0,652 N·m. Der Vektor läuft dann **netto zweimal rechts herum je Zyklus**, max/min = 9,2.
  - REF, μ = 0,462, ρ_f = 0,7·R_c: ebenfalls −2 Umläufe; bei ρ_f = 0,5·R_c +1 Umlauf, aber max/min = 12,5.
- Phasen (G0, quasistatisch): arg P+₁ = arg c₁ − 90° = −27,0°, arg P−₂ = −arg c₂ − 90° = 144,0°.

**Bewertung: teilweise bestätigt.** Für die Grundharmonische ist das Drehfeld real und hat den angegebenen Radius. Für das Egg-Profil schwankt der Betrag aber um den Faktor 2,2–2,8 (Periode T/3). Der Umlaufsinn ist nicht robust: Nahe einer Kippresonanz bei 2f kehrt er sich um. Der zeitliche Mittelwert ist null.

---

## KM-05 · Kipp-Eigenfrequenzen

**Methode [R].** Eigenwerte von Mq⁻¹Kq (`k2_…`); analytisch f_t = f_n·R_c/(√2·ρ), J = M·ρ².

**Ergebnis.**

| Fall | Geometrie | ρ_f/R_c | f_Hub | f_Kipp (2×) | 2f/f_Kipp | 3f/f_Kipp |
|---|---|---|---|---|---|---|
| REF μ = 1 | G0 | – | 19,74 | **19,74** | 1,013 | 1,52 |
| REF μ = 1 | G60h | – | 19,74 | 39,48 | 0,507 | 0,76 |
| REF μ = 0,462 | G0 | 0,35/0,5/0,7 | 19,74 | 25,6/23,1/19,8 | 0,78/0,87/1,01 | 1,17/1,30/1,51 |
| STEIF μ = 0,462 | G0 | 0,35/0,5/0,7 | 120,0 | 155,7/140,4/120,7 | ≤ 0,17 | ≤ 0,25 |
| STEIF μ = 0,462 | G60h | 0,35/0,5/0,7 | 120,0 | 241/194/150 | ≤ 0,13 | ≤ 0,20 |
| STEIF μ = 1 | G0 | – | 120,0 | 120,0 | 0,167 | 0,25 |

- Bei μ = 1 und Modulen über den Zellen ist f_Kipp = f_Hub exakt (Entartung).
- Liegt die Masse außerhalb von R_c/√2 (schwere große Platte, Module außerhalb der Zellen, hoher Schwerpunkt), gilt f_Kipp < f_Hub.
- Beispiel: Platte mit 1,5·R_c, μ = 0,462 → f_Kipp = 0,97·f_Hub.

**Bewertung.**
- Beim Simulationsreferenzsatz liegt die Kippmode bei 2f. Gerade die k = 2-Komponente, die in N am Triphasik-Punkt ausgelöscht ist, wird im Kippkanal resonant überhöht (Faktor bis 5,03).
- Im steifen Aufbau ist (b) mit Abstand erfüllt, wenn die Kippmode berücksichtigt wird. Die Präreg definiert f₁ bereits als „niedrigste in N oder einer Zellkraft sichtbare Mode“ (§5.3 b).
- Die Beispiele A4/A5 und das 1-FG-Auslegungswerkzeug enthalten nur die Hubmode.
- P0.4 legt den Anregungsort nicht fest (A9.2, Z. 465–472). Eine Anregung in der Mitte regt die Kippmoden nicht an.

---

## KM-06 · Einzelzellkräfte, Summe, Momente (linear)

**Methode [R].** `k2_linear_3fg.py`, Tabellen in `k2_…_ausgabe.txt` und `k2_linear_3fg.csv` (alle k = 1…6).

**Ergebnis (Auswahl; Zelle = kleinste Zellkraft, Reserve = Zelle/(Mg/3), Mg/3 = 2,1255 N):**

| Fall | Geo | Cfg | N_min | N SS | Zelle min | Reserve | Summe/3 | Zelle SS | R+₁ | R−₂ | \|M\| min…max |
|---|---|---|---|---|---|---|---|---|---|---|---|
| REF μ = 1 | G0 | T | 5,3304 | 2,16 | **−6,308** | −297 % | 83,6 % | 17,53 | 0,652 | 0,806 | 0,159…1,457 |
| REF μ = 1 | G0h | T | 5,3304 | 2,16 | 0,449 | 21,1 % | 83,6 % | 3,94 | 0,260 | 0,106 | 0,148…0,374 |
| REF μ = 0,462 | G0 | T | 5,8932 | 1,00 | −0,217 | −10,2 % | 92,4 % | 5,65 | 0,276 | 0,236 | 0,041…0,511 |
| STEIF μ = 0,462 | G0 | T | 4,9416 | 2,60 | 0,850 | 40,0 % | 77,5 % | 3,51 | 0,226 | 0,076 | 0,114…0,320 |
| STEIF μ = 0,462 | G60 | T | 4,9416 | 2,60 | 0,0006 | 0,0 % | 77,5 % | 3,61 | 0,226 | 0,076 | 0,114…0,320 |
| STARR μ = 0,462 | G0 | T | 5,5319 | 1,40 | 0,956 | 45,0 % | 86,8 % | 3,34 | 0,225 | 0,074 | 0,133…0,298 |
| STARR μ = 0,4 | G0 | T | 5,6452 | 1,21 | 1,113 | 52,4 % | 88,5 % | 2,89 | 0,195 | 0,064 | 0,115…0,258 |
| STARR μ = 0,462 | G0 | Z | 5,1455 | 1,90 | 0,956 | 45,0 % | 80,7 % | 3,34 | 0,224 | 0,073 (R−₁ 0,013) | 0,113…0,304 |
| alle | alle | S (h = 0,15) | – | – | = Summe/3 | – | – | – | 0 | 0 | 0 |

**Weitere Ergebnisse.**
- Am Triphasik-Punkt ist die Zell-Wechselamplitude größer als die der Summe. Spitze-Spitze Zelle/Summe: 2,39 (STARR, G0), 1,35 (STEIF, G0), 8,1 (REF μ = 1, G0).
- Am Zeltschnittpunkt Z liefert die Summe N₁ = 0,261 N. Im Moment entsteht dazu eine schwache Gegenkomponente: R−₁/R+₁ = 0,058 = δ/3 mit δ = 10° in rad.
- Bei synchroner Phasung (S) verschwindet das Moment bei gleichen Modulen.
- G0 und G60 haben gleiche Momentbeträge (der Vektor ist nur gedreht), aber verschiedene Zellkräfte.

**Präzisierung von A2.5.** „Zellkräfte aller Konfigurationen bis auf eine Zeitverschiebung gleich“ und „je Zelle die Grenze der synchronen Phasung“ gelten exakt nur quasistatisch (H = 1) oder bei μ = 1 mit G0 (Entkopplung, KM-07). Bei μ < 1 und endlicher Steifigkeit trennen sich Hub- und Kippübertragung:

    F_j = (1/3)·H_z{S} + H_t{m·a_j} − (1/3)·H_t{S},   S = Σ m_i a_i.

Beispiele (STEIF μ = 0,462, G0):
- 10 Hz: Zellreserve je nach Konfiguration 35,2–42,7 %. Synchron 36,3 %, (0°,180°) 35,2 %.
- 12 Hz: 10,8–18,9 %. Synchron 15,3 %, Pilot 110/250 10,8 % (`k6_…`, Teil B).

---

## KM-07 · Nichtlinear: Einzelzell-Liftoff und Rückwirkung auf die Summenkraft

**Frage.** Was passiert, wo die lineare Zellkraft negativ wird? Gilt die Engine-Aussage „Kontaktast am Triphasik-Punkt“ für einen Körper auf drei Zellen?

**Methode [R].** RK4, einseitiger Kontakt je Zelle, Δt = 50 µs, 15 s, Auswertung 10 s nach 5 s. Zwei Starts: Standardstart und linearer Orbit (5 s bilateral, dann einseitig). Dazu exakte Entkopplungsprüfung (`k5_…`, `k5b_…`).

**Ergebnis.**
- **μ = 1, G0 (Engine-Massenverteilung, Module über Zellen).**
  - Das System zerfällt exakt in drei unabhängige Schwinger (M/3, K/3, C/3, je ein Modul). Jede Zellkraft ist dann ein Drittel der Engine-Kraft bei **synchroner** Phasung, verschoben um τ_j.
  - Zellen: λ = 75,79 % je Zelle (Engine (0°,0°): 75,7885 %), F_max·3 = 41,12 N (Engine 41,1226 N), Schiefe 1,7055 (1,7054).
  - Summe am Triphasik-Punkt: λ_Summe = **37,06 %** (linearer Orbit) bzw. **56,44 %** (Standardstart), F_max = 24,96 N, Schiefe +0,83 bzw. +1,03.
  - Zum Vergleich die 1-FG-Engine am selben Punkt: F_min = 5,3304 N, λ = 0, F_max = 7,49 N, Schiefe +0,067.
  - Die Bahn ist nicht T-periodisch (max|F(t) − F(t − T)| = 13,7 N).
- **REF μ = 0,462, G0.**
  - T: λ_Zelle = 11,95 %. Die Summe bleibt im Kontakt, aber F_min = 5,964 statt 5,893 N und die Schiefe ist 0,022 statt 0,067.
  - Z: λ_Zelle bis 17,25 %. Summen-Schiefe −0,998 statt −0,385 (linear).
  - Beide Starts geben dasselbe Ergebnis.
- **REF μ = 1, G60h, T:** λ_Zelle = 22,35 %, Summen-Schiefe 0,098 statt 0,067, F_min 5,407 statt 5,330 N.
- **STEIF μ = 1, G0, T/Z:** λ_Zelle ≈ 98 %, λ_Summe ≈ 93 %, F_max 350–420 N. Das ist chaotisches Springen mit starker Startabhängigkeit.
- **Alle Fälle mit positiver linearer Zellkraft** (STEIF μ = 0,462 G0 T/Z/S, G60 T mit 0,0006 N; REF S; REF μ = 1 G0h T; REF μ = 0,462 G60h T): λ = 0, Ergebnis wie linear.

**Bewertung.**
- Die Engine-Aussagen zum Triphasik-Punkt setzen stillschweigend voraus, dass der Körper nicht kippt bzw. alle Zellen tragen. Mit Modulen über drei Zellen und μ = 1 ist der Triphasik-Punkt beim Referenzsatz **kein** Kontaktpunkt.
- Schon wenig Einzelzell-Liftoff (12–17 %) verfälscht die Summen-Observablen deutlich, während N > 0 bleibt.
- Damit sind §5.3(a) „je Zelle“, G6 und S2 der Präreg quantitativ begründet.
- Das ist eine Präzisierung der bekannten Einschränkung „Modell eindimensional … Kippen“ (Arbeitspapier v2.4, Z. 5293), keine Widerlegung von Engine-Zahlen für den 1-FG-Fall.

**Nebenbefund (KM-13).**
- Die Engine-Bahn bei (0°, 0°) ist rundungsempfindlich: Die Differenz zweier mathematisch identischer Rechnungen wächst von 8,5·10⁻¹⁴ N (0,1 s) auf 1,4·10⁻² N (3 s). Das entspricht einer Wachstumsrate von ≈ 9 s⁻¹, ein Hinweis auf chaotische Dynamik.
- Die Bahn ist weder T- noch 2T-periodisch (8,7 N bei 2T).
- Die Statistik (λ, F_max, Schiefe) ist auf 4 Stellen robust; punktweise Werte sind nur statistisch definiert.

---

## KM-08 · Auslegung: Einzelzell-Minimum gegen Summe/3 (§5.3 a)

**Methode [R].** Lineare Zellreserve min_j F_j/(Mg/3) für alle Präreg-Lauftypen (Einzelmodul, Paare Δ = 0/120/180°, synchron, (0°,180°), drei Piloten, 21 Schnittpunkte), f = 10/12/14 Hz bei gleichem Hub (`k6_…`, Teil B).

**Ergebnis (STARR μ = 0,462, 10 Hz; Zelle | Summe/3):**

| Geo | Einzelmodul | synchron | (0°,180°) | Piloten | Schnitt (min) |
|---|---|---|---|---|---|
| G0 | 45,0 \| 81,7 % | 45,0 \| 45,0 % | 45,0 \| 75,7 % | 45,0 \| ≥ 77,7 % | 45,0 \| 78,3 % |
| G60 | 63,3 \| 81,7 % | 45,0 \| 45,0 % | **−7,4** \| 75,7 % | 8,5–12,5 % | **8,9** \| 78,3 % |
| G0h | 63,3 % | 45,0 % | 69,5 % | 61,4–63,4 % | 61,6 % |
| G60h | 72,5 % | 45,0 % | 45,0 % | 56,9–59,3 % | 56,9 % |
| Z (Zentrum) | 81,7 % | 45,0 % | 75,7 % | 77,7–81,0 % | 78,3 % |

**Weitere Ergebnisse.**
- Bei 12 Hz fällt G0 auf 20,8 % für alle Läufe (verletzt 25 %), und G60 wird negativ.
- STEIF μ = 0,462, G0, 10 Hz: 35,2–42,7 %.
- STARR μ = 0,4, G0: 52,4 % bei 10 Hz und 31,4 % bei 12 Hz, wie A4.

**Bewertung.**
- Die Summe/3 überschätzt die Zellreserve am Schnitt um bis zu Faktor 1,7 (G0) bzw. 9 (G60).
- Die Lage der Module ist ein starker Auslegungshebel. Module außerhalb des Stützdreiecks (G60) sind auszuschließen.
- Module auf R_c/2 (G0h, G60h) halbieren das Moment, heben aber die Reserve am Schnitt auf 57–62 %.
- Die synchrone Phasung ist geometrieunabhängig (Moment null) und bindet bei G0, G0h und G60h.
- Bestätigt L5a-040: Das Kriterium muss je Zelle gelten.

---

## KM-09 · Leckage am Triphasik-Punkt durch Modulungleichheit

**Methode [R].** Lineare Lösung mit je einer Störung an Modul 2 bzw. Zelle 2 (`k4_…`).

**Ergebnis (STARR μ = 0,462, G0; Amplituden 2|δN_k|):**

| Störung | δN₁ | δN₂ | δF_min(Σ) | R−₁/R+₁ (Ellipse) | Achse k = 1 |
|---|---|---|---|---|---|
| Masse M2 +1 % | 0,0150 N | 0,0049 N | −0,0019 N | 0,00332 (= ε/3) | 30° |
| Hub M2 +1 % | 0,0150 N | 0,0049 N | −0,0117 N | 0,00332 | 30° |
| Phase M2 +1° | 0,0261 N | 0,0172 N | −0,054 N | 0,00582 (= δ/3); R+₂/R−₂ = 0,0116 (= 2δ/3) | 75° |
| Phase M3 +1° | 0,0261 N | 0,0172 N | −0,054 N | 0,00582 | 15° |
| Zellverstärkung Z2 +1 % | 0,0150 N | 0,0049 N | +0,0096 N | 0,00332 | 30° |
| Zelllage Z2 +1 mm (Auswertung nominal) | 0 | 0 | 0 | 0,00332 | 120° |

**Weitere Ergebnisse.**
- Die Differenz der δF_min zwischen Masse und Hub (0,0098 N) ist die geänderte statische Last.
- STEIF ist praktisch gleich.
- REF μ = 1 ist resonant überhöht: Masse +1 % gibt δN₂ = 0,268 N, weil die drei Moden bei μ = 1, G0 entartet sind und die Kopplung über die verschobene Massenverteilung nahe 2f/f_n = 1,013 wirkt.
- Vergleich u_c ≤ 0,0327 N: 1 % Ungleichheit leckt 0,46·u_c in N₁, 1° Phase 0,80·u_c.

**Bewertung.**
- 1 % bzw. 1° erzeugen in N am Triphasik-Punkt Signale in der Größe von u_c.
- Im Kippkanal erscheinen dieselben Fehler als Ellipse (Gegenkomponente ε/3 bzw. δ/3 relativ). Ihre Achse zeigt auf das abweichende Modul (Modulwinkel − 90°).
- Für H1 heben sich konstante Ungleichheiten heraus, weil die Einzelmodulläufe sie mitmessen. Kritisch sind nur Änderungen zwischen Einzel- und Kombinationslauf.

---

## KM-10 · Identifizierbarkeit von Modulungleichheit

**Methode [R].** Rückrechnung der drei komplexen Modulzeiger g_i,k aus den drei Zellzeigern über die nominale Übertragungsmatrix T(kω) für k = 1, 2 (`k4_…`).

**Ergebnis.**
- Die Summe allein liefert eine komplexe Gleichung je Harmonischer (Σ δg_i): Welches Modul abweicht, bleibt unbestimmt.
- Die drei Zellen liefern drei Gleichungen. Kondition von T: 1,0 (G0), 2,0 (G60h), bis 7,6 (REF G60h, k = 2).
- Die Rückrechnung findet Masse/Hub +1 % und Phase +1° exakt beim richtigen Modul. Die Phase dreht um −k·δ: −1° bei k = 1, −2° bei k = 2.
- Nicht unterscheidbar aus Kräften allein:
  - Masse, Hub und Zellverstärkung sind reine Skalenfaktoren, für alle k gleich. Bei G0 ist ein Zellverstärkungsfehler identisch mit einem Massenfehler des Moduls darüber. Bei G60h verteilt er sich auf alle drei Module (+0,25/+0,25/+0,50 %, ±0,25°).
  - Ein Zelllagefehler von 1 mm erscheint als −0,66 % am Modul und ±0,165° Scheinphase an den Nachbarmodulen.
- Phasenfehler sind unterscheidbar (∝ k).

**Bewertung.**
- Der Zell- bzw. Kippkanal macht Modulungleichheit und Phasenlage **je Modul** identifizierbar, auch in jedem Kombinationslauf. Die Summenkraft kann das nicht.
- Voraussetzung: Zellverstärkungen relativ auf ≲ 0,1 % (P0.1 mit Gewichtsstücken an fünf Stellen, A9.2) und Zelllage auf ≲ 0,1 mm bzw. kalibriert.
- Masse und Hub trennt nur P0.2 (Wägung) bzw. P0.5 (Wegkanal).

---

## KM-11 · Messbarkeit

**Methode.**
- [A] Rauschmodell, im Bestand keine Rauschdichte:
  - 5-kg-DMS-Zelle, 1 bzw. 2 mV/V, Speisung 5 V
  - Brücke 1 kΩ (Rauschen 4,0 nV/√Hz [R])
  - ADC eingangsbezogen 15 bzw. 50 nV/√Hz, Rauschbandbreite f_s/2
- [Q] Bestand: PCMMFM-Fehlerbudget elektrisch 0,001–0,005 N, Beispiel σ_total ≈ 0,024 N (`Werkzeug_PCMMFM_PreValidation`, §6); Laborplan V1 ADS1256 ≥ 2 kSPS.
- [R] Harmonische eines Laufs: σ_A = σ_F·√(2/N_s) (`k6_…`, Teil A).

**Ergebnis.**
- σ_F je Stichprobe 2,4–21 mN. Je Lauf (10 s): σ_A = 0,018–0,21 mN, Moment 2–26 µN·m (R_c = 100 mm).
- Signale am Triphasik-Punkt (STARR μ = 0,462, G0):
  - Zellamplituden A₁ = 1,498 N und A₂ = 0,494 N, also 46·u_c bzw. 15·u_c, rund 7·10³·σ_A (pessimistisch).
  - Moment R+₁ = 0,225 N·m, R−₂ = 0,074 N·m.
  - Ellipse aus 1 % Ungleichheit: R−₁ = 7,5·10⁻⁴ N·m, Signal-Rausch-Verhältnis je Lauf 29–350.
- Systematiken sind größer als das Rauschen:
  - 1 mm Zelllage ≙ 1 % Scheinungleichheit
  - 1 % Zellverstärkung ≙ 0,015 N Leckage in N₁
- Abtastrate nach Präreg A6: k_max = 3 verlangt f_s ≥ 2107 Hz (2 kSPS reicht knapp nicht), k_max = 5 (Momentharmonische bis 5) verlangt ≥ 3512 Hz.

**Bewertung.** Das Kippmoment ist mit großem Abstand messbar. Begrenzend sind Kalibrierung, Zelllage, Übersprechen und Rahmenmoden (nicht modelliert), nicht das Zellrauschen.

---

## KM-12 · Bewertung: neue konfirmatorische Observable oder Kontrolle?

**Ergebnis [R + Q].**
1. **Physikalischer Gehalt.**
   - Im Kontaktast sind Zellkräfte und Momente lineare Superpositionen der Einzelmodulantworten, genau wie N (gleiche Grundlage wie H1).
   - Am Triphasik-Punkt trägt das Moment die in N ausgelöschten Ordnungen k ≢ 0 (mod 3). Es ist damit die zweite Hälfte derselben linearen Antwort, keine neue Physik.
   - Im steifen V1-Aufbau gilt H_t ≈ 1. Das Moment folgt dann aus Modulmasse, Hub, Profil und Geometrie und prüft den Kontakt nicht. Es prüft Modulgleichheit, Phasen, Zellkalibrierung und Geometrie.
2. **Eigenschaften.**
   - Großes Signal (≈ 46·u_c).
   - Modulaufgelöste Phasen- und Amplitudenmessung in jedem Lauf (KM-10).
   - Empfindlich auf genau die Störungen, gegen die H2 laut Präreg blind ist („nicht konstante Phasenfehler oder nicht erfasste Modulunterschiede“, Präreg §2 Reichweite).
3. **Grenzen.**
   - Konfundiert mit Zellverstärkung und Zelllage.
   - Der Umlaufsinn hängt bei Kippresonanz von der Dynamik ab.
   - Ein „Drehfeld konstanten Betrags“ gibt es beim Egg-Profil nicht.
4. **Abgleich mit E3.** Präreg v2 führt Kippmomente bereits als E3 (explorativ, ohne Entscheidungsregel) mit der korrekten Harmonischen-Aussage. P1 („bisher nur als Kippkontrolle geführt“) ist insoweit zu korrigieren.

**Bewertung.**
- Als **zweite physikalische Vorhersage neben F_min nicht geeignet**: kein zusätzlicher Modellgehalt, gleiche Hypothesenklasse wie H1, zusätzliche Tests.
- Wertvoll als **registrierte Kontrolle mit Entscheidungsregel**: Modulzeiger aus den Zellen als Phasen-/Gleichheitsmonitor gegen die Encoder, Gegenkomponente R−₁/R+₁ als Ungleichheitsmaß, Zellreserve (S2/G6).
- Ein optionaler Ausbau wäre eine Zell-Erweiterung von H1 (Superposition je Zelle, k = 1, 2), dann als eigene sekundäre Familie.
- E3 sollte die Auswertung vorab festlegen: Größen, Bandbegrenzung, Geometrie.

---

## Korrekturen und Präzisierungen an Quellen

| Quelle | Fundstelle | Aussage | Korrektur |
|---|---|---|---|
| P1-Zwischenbericht | §3 Nr. 5; L4-026 (Voraussetzungen); übersehene_ansaetze Z. 43 | „umlaufendes Kippmoment konstanten Betrags (3/2)·m·a₁·r“ | Die Formel gibt nur den Radius der k = 1-Komponente. Beim Egg-Profil schwankt der Betrag um Faktor 2,24 (quasistatisch), Periode T/3, Mittel 0. Die k = 2-Komponente läuft gegensinnig (33 % quasistatisch, bei Kippresonanz dominant). |
| P1-Zwischenbericht | §3 Nr. 5 | „Bisher ist es nur als ‚Kippkontrolle‘ geführt“ | Präreg v2 §3 E3 (Z. 144–146) führt Einzelzellkräfte und Kippmomente bereits als explorative Observable mit der Harmonischen-Aussage. |
| Präreg v2 Anhang | A2.5, Z. 192–201 | „Zellkräfte aller Konfigurationen bis auf eine Zeitverschiebung gleich; je Zelle Grenze der synchronen Phasung“ | Exakt nur quasistatisch oder bei μ = 1 mit G0. Bei μ < 1 und endlichem K (f_n = 120 Hz) weichen die Zellreserven um bis zu 7,5 Prozentpunkte (10 Hz) bzw. 8 Punkte (12 Hz) ab. Dort ist nicht die synchrone Phasung die ungünstigste. |
| Präreg v2 Anhang | A2.5 | „Eine senkrechte Kraft über einem Auflagerpunkt geht … ganz in dieses Auflager“ | Statisch richtig. Dynamisch gilt F_j = (1/3)H_z{S} + H_t{m a_j} − (1/3)H_t{S}. Mit Kippmode bei 2f (Referenzsatz) ist die Zellkraft resonant überhöht. |
| Präreg v2 Anhang | A9.2 P0.4 | Übertragungsfunktion je Zelle mit Impulshammer/Shaker, 1-FG-Anpassung | Präzisierung: Die Anregung muss exzentrisch erfolgen (mindestens zwei Orte), sonst bleiben die Kippmoden unsichtbar. Die Anpassung braucht ein 3-FG-Modell (Hub + 2 Kippmoden). |
| Arbeitspapier v2.4 / Engine | Anhang B.1; Z. 5293 | Kontaktast mit F_min = 5,33 N am Triphasik-Punkt (1-FG) | Präzisierung: Für einen Körper auf drei Zellen mit Modulen über den Zellen und μ = 1 gilt am Triphasik-Punkt Einzelzell-Liftoff 75,8 % und λ_Summe 37–56 %. Das Ergebnis setzt einen nicht kippenden Körper voraus. |
| Laborplan V1 | §5 (Z. 66) | ≥ 2 kSPS genügt | Nach Präreg A6 reicht das nicht ganz für k_max = 3 (≥ 2107 Hz). Für Momentharmonische bis k = 5 sind ≥ 3,5 kHz nötig. |

## Empfehlungen für V1

1. **Lage festlegen und begründen.**
   - Module über den Zellen (G0): maximales Moment, Zelle = Modulkanal, Kondition 1, Zellreserve = synchrone Grenze.
   - Module auf R_c/2 (G0h/G60h): halbes Moment, Reserve am Schnitt 57–62 %.
   - Module außerhalb des Stützdreiecks (G60) ausschließen.
2. **Auslegungswerkzeug auf das 3-FG-Zellmodell erweitern** (Hub + 2 Kippmoden, J aus CAD inklusive Schwerpunkthöhe). f_Kipp = f_n·R_c/(√2ρ) prüfen; f₁ = min(f_Hub, f_Kipp) in §5.3(b).
3. **P0.4 mit exzentrischer Anregung** (über jeder Modulposition) und 3-FG-Anpassung. Zelllage auf ≤ 0,1 mm messen; relative Zellverstärkungen auf ≤ 0,1 %.
4. **E3 präzisieren**: Modulzeiger aus Zellen (k = 1, 2) je Lauf, R−₁/R+₁, Umlaufsinn, Vergleich mit Encoderphasen. Als Kontrollkriterium mit vorab festgelegter Schwelle nutzen, nicht als physikalische Hypothese.
5. **Abtastrate ≥ 3,75 kSPS**, wenn Momentharmonische bis k = 5 ausgewertet werden.
6. **S2/G6 beibehalten**: 12–17 % Zell-Liftoff verändern die Summen-Schiefe um Faktor 3 bzw. 2,6, bei N > 0.

## Offene Punkte

- Reale Geometrie, Massen, Trägheitsmomente und Schwerpunkthöhe fehlen. Ebenso Horizontal-Freiheitsgrade und Reibung der kinematischen Lagerung.
- Rahmen- und Plattenmoden sind nicht modelliert. Sie können unter f_Kipp liegen.
- Querkraft- und Momentübersprechen der Zellen sind nicht modelliert (Formelverzeichnis §„Übersprechen und Momente“).
- Die Rauschdichte der Messkette ist angenommen; P0.1/P0.7 liefern reale Werte.
- Die Aktorrückwirkung (Profil unter Kippbewegung) ist nicht modelliert.
- Die nichtlinearen Liftoff-Fälle (μ = 1) sind chaotisch und startabhängig; Summenwerte sind dort nur statistisch definiert.
