# P2 · Gegenprüfung der Gruppe „symmetrie_randterm“ · Protokoll

> **Vermerk zur Übernahme (04.10.2026).** Protokoll aus der Gesamtprojektanalyse 10/2026, Stand 02.10.2026, unverändert bis auf Pfade und Quellenangaben. Geprüft wurde der Repository-Stand `cd7be6a` (28.09.2026) mit der Präregistrierung v2 vom 25./28.09.2026; die späteren Änderungen aus PR #13 und PR #14 (unter anderem Präregistrierung v2 mit Arbeitsfestlegungen, `code/auslegung.py`, `code/ereignisloeser.py`) sind nicht eingearbeitet. Alle Zahlen sind Simulation oder Analytik, keine Messdaten. Verweise wie „L1a-019“, „P1 §3“ oder „B01–B14“ zeigen auf Arbeitsdokumente der Analyse, die nicht im Repository liegen. Quellen außerhalb des Repositorys sind als „(lokaler Bestand, nicht im Repository)“ gekennzeichnet. Startbefehle und Grenzen je Gruppe: [`rechnungen/README.md`](../../README.md).

Stand 02.10.2026. Rolle: unabhängiger Gegenprüfer. Ziel war, die Befunde der Gruppe zu widerlegen.
Geprüft wurden SYM-02, SYM-03, SYM-04, RT-01, RT-02, RT-03 und RT-05. SYM-01, SYM-05 und RT-04 wurden nur
mitgeprüft, soweit sie in diese Rechnungen eingehen.

**Kennzeichnung.** Ohne Zusatz steht eine eigene Rechnung in diesem Ordner. „Quelle“ ist eine Fundstelle im
Bestand. „Annahme“ ist nicht geprüft.

**Vorspann für alle Reproduktionsbefehle:**

```
cd rechnungen/symmetrie_randterm/verifikation
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../../../code
```

## 0 Eigene Werkzeuge (unabhängig von `sr_engine.py`)

| Datei | Inhalt |
|---|---|
| `v_engine.py` | Eigene RK4-Engine, über Punkte vektorisiert. Das Profil wird analytisch als q, q̇, q̈ berechnet, die Phasen in Grad mit τ = (φ/360°)·T. Die Profiltabellen werden je Periode vorab berechnet, sodass die Rundung von der Referenz abweicht. Es gibt **zwei Formulierungen**: `frame` mit dem Zustand (z_f, v_f) wie das Modell, und `com`, bei der der Schwerpunkt (z_S, v_S) direkt integriert wird. In `com` schließt das RK4-gewichtete Mittel die Impulsbilanz algebraisch, dort ist also E ≡ 0. |
| `v_exakt.py` | Ereignisgesteuerte, halbanalytische Integration. Die Flugphase wird **analytisch** gelöst (z̈_f = −g − ā). Der Kontaktbeginn ergibt sich als Nullstelle von min(−z, F/K) mit brentq. Die Kontaktphase läuft mit DOP853 (rtol 1e-12) und dem Ereignis F = 0. Ein festes Zeitraster gibt es nicht. |
| `v1_symmetrie_analytik.py` | Äquivalenzklassen über die kanonische Abstandsfolge. Eigenes lineares Frequenzbereichsmodell: N_k = M·Ā_k·(K + ikωC)/(K − Mk²ω² + ikωC), Ā_k aus der FFT von q (2¹⁸ Stützstellen, 600 Harmonische). |

Validierung:
- Eigene q̈ gegen `finesweep.z_egg_zdd`: max. Abweichung 4,6·10⁻¹⁴ m/s².
- Lineares Modell gegen eigene RK4 an K1: γ₁ −0,18016 / −0,18016, F_min 3,98959 / 3,98960 N.
- Exakte Bahn an L1: ⟨N⟩ über eine Periode = Mg auf 7·10⁻⁷ ppm.
- Mit der eigenen RK4 ergeben sich an L1 bei 50 µs dieselben Q-Werte wie bei der Gruppe (−20,84 ppm).

---

## SYM-03 „120°-Verschiebung“ ist keine Invarianz → **bestätigt**

**Frage.** Ist (φ₂, φ₃) → (φ₂ + 120°, φ₃ + 120°) eine Invarianz? Wo gilt sie zufällig?

**Methode.**
- Eigene Klassifikation über die Abstandsfolge bis auf Rotation, Brute Force auf dem 0,25°-Raster (2 073 600 Punkte).
- Handrechnung der sechs Gleichungssysteme.
- |Φ_k| vor und nach der Verschiebung.
- Eigene RK4 (frame und com), 60 s, Fenster 50–60 s.
- Exakte Bahn für das Bild (230°, 354°), 20 s.
- Kartenband aus `data/sweep_19x19.csv`.

**Ergebnis.**
- **Ausnahmepunkte:** genau 6, nämlich (40,200), (80,160), (160,80), (200,40), (280,320), (320,280). Die Handrechnung zeigt, dass nur die Elemente (123) und (132) Lösungen liefern.
- **|Φ_k|:**
  - (0,0): 3 → 1,7321 für k ≢ 0 mod 3.
  - (110,234): k = 1: 0,1483 → 1,6078 (×10,8); k = 2: 0,3173 → 1,9646 (×6,19); k = 3 und 6 unverändert.
- **Eigene RK4:**
  - K1: λ 0 → 75,504 % (frame) bzw. 75,502 % (com); |N₁| 0,6444 → 11,991 N.
  - L1: 12,400 → 75,907 bzw. 75,913 %.
  - L5: 75,61 → 0 %, F_min 1,0766 N.
- **Exakte Bahn (230,354):** λ 75,505 %, γ₁ +1,680, F_max 39,02 N.
- **Kartenband:** λ 74–77 % an 142 von 361 Punkten (39,3 %), γ₁ 1,658–1,720.
- **Quelle:** Forschungslinie S. 7 §4 (Z. 168–180) enthält die Behauptung wörtlich.

**Reproduktion.**
- `python3 v1_symmetrie_analytik.py`
- `timeout 540 python3 v2_symmetrie_laeufe.py std frame` (bzw. `com`), dann `python3 v2b_symmetrie_auswertung.py`
- `timeout 540 python3 v6_exakt_bilder.py K1+120`
- `python3 v7_kartenband.py`

**Einschränkung.** Nur Standardstart. Die Aussage ist trotzdem eindeutig, weil die Abweichungen 75 %-Punkte betragen.

---

## SYM-02 Spiegelung φ → −φ ist keine Symmetrie → **bestätigt**

**Methode.**
- Eigenes lineares Modell (Abschnitt B von `v1`).
- Eigene RK4 mit zwei Formulierungen, 60 s.
- Exakte Bahn für L1 und L1* (20 s, Auswertung 15–20 s auf einem 5-µs-Raster).

**Ergebnis.**
- **Egg-Profil:** Die Phasen von A_k relativ zu t₀ = 0,325 T sind 0° oder 180°. Das Profil ist also zeitumkehrsymmetrisch.
- **Lineares Modell, Werte A/A*:**

| Paar | Fall | γ₁ | F_min / N | F_max / N | max Δ\|N_k\| |
|---|---|---|---|---|---|
| (110,234)/(250,126) | Referenz | −0,1802 / −0,2620 | 3,9896 / 3,6896 | 8,5776 / 8,7759 | 2·10⁻¹⁶ N |
| (110,234)/(250,126) | C = 0 | −0,0197 / −0,0197 | gleich | gleich | 2·10⁻¹⁵ N |
| (110,234)/(250,126) | starr | −0,5994 / −0,5994 | 3,8621 / 3,8621 | gleich | 2·10⁻¹⁶ N |
| (100,240)/(260,120) | Referenz | −0,3441 / +0,0501 | 0,7677 / 1,6175 | 10,955 / 11,235 | 4·10⁻¹⁶ N |
| (100,240)/(260,120) | C = 0 / starr | gleich | gleich | gleich | ≤ 4·10⁻¹⁶ N |

- **Zeltschnitt φ₃ = 240°:**
  - Steigungen 0,2246 / 0,1916 N/°, max |F_min(120+d) − F_min(120−d)| = 0,850 N.
  - C = 0: 1,2·10⁻⁶ N. Starr: 1,8·10⁻⁵ N (20 000 Stützstellen je Periode).
- **Eigene RK4:**
  - K1: γ₁ −0,18016 → −0,26197, F_min 3,98960 → 3,68956 N, |N_k| gleich.
  - L1: λ 12,40 → 8,95 %, γ₁ −0,1686 → +0,0832, |N₂| 4,567 → 4,763 N.
- **Exakte Bahn:** L1 hat λ 12,390 %, γ₁ −0,1685, F_max 12,983 N. L1* hat λ 8,975 %, γ₁ +0,0830, F_max 13,389 N.

**Reproduktion.** `python3 v1_symmetrie_analytik.py`; `v2_*` wie oben; `timeout 540 python3 v6_exakt_bilder.py L1 'L1*'`

**Einschränkung.** Die Triadenregel (82,2°) wurde nicht nachgerechnet.

---

## SYM-04 Numerische Verifikation der S₃-Äquivalenzen, Startabhängigkeit → **bestätigt** (mit Präzisierung)

**Methode.**
- Eigene RK4, 600 Perioden.
- Basispunkte K1, L1, L4, L5 und L6 mit ihren 6 S₃-Bildern. Die Bilder habe ich selbst hergeleitet: Referenzmodul r, neue Phasen = alte − r.
- Startmodi „std“ (t0 = 0) und „shift“ (t0 = −τ_r).
- Zusätzlich exakte Bahn für L4.

**Ergebnis (eigene Zahlen, Fenster 50–60 s).**
- **Shift, K1 und L1:**
  - |ΔN1| ≤ 1,8·10⁻¹⁵ N, |Δγ₁| ≤ 1,4·10⁻¹³, |ΔF_max| ≤ 7·10⁻¹⁵ N.
  - Phasenregel arg N_k(B) = arg N_k(A) + kφ_r erfüllt auf 8·10⁻¹⁴°.
- **Shift, L4:** alle 6 Bilder bei λ ≈ 43,84 %, |ΔN1| 8,9·10⁻⁵ N, Δλ 0,004 %-Pkt, Phasenregel 0,036°.
- **Std, K1:** |ΔN1| 1,85·10⁻⁷ N (frame) bzw. 4·10⁻¹⁰ N (com), |ΔF_max| 6·10⁻⁶ N.
- **Std, L1:**
  - |ΔN1| 2,67·10⁻⁴ N (42 ppm). Das RK4-Mittel weicht nur um 1,85·10⁻⁷ N (frame) bzw. 2,7·10⁻¹⁵ N (com) ab.
  - Damit ist die Erklärung der Gruppe bestätigt: Die Abweichung ist Q, und in frame kommt E hinzu.
- **Std, Mehrstabilität:** in beiden Formulierungen identisch zur Gruppe (W40 = W50).
  - L4: 4 Bilder bei 43,84 %, 2 bei 75,80 %.
  - L5: 4 bei 75,61 %, 2 bei 23,50 %.
  - L6: 2 bei 71,58 %, 4 bei 76,18 %.
- **Präzisierung, die über die Gruppe hinausgeht:**
  - Der 43,84-%-Zustand von L4 existiert auch in der exakten Dynamik: Ab dem RK4-Zustand bei 30 s bleibt die exakte Bahn 30 s lang bei λ 43,82–43,87 %. In der eigenen RK4 hält er 200 s (λ je 10 s: 43,83–43,85 %).
  - Ab dem Standardstart landet die exakte Bahn für L4 jedoch auf **75,805 %**, die RK4 auf 43,84 %. Dasselbe gilt für das Bild g4 bei std- und shift-Start.
  - Die Mehrstabilität ist also physikalisch. **Welchen** Attraktor der Standardstart erreicht, hängt aber auch von der Numerik ab (Δt bzw. Integrator), nicht nur von der Startphase. Das konkrete 4/2-Muster ist ein Engine-Befund, keine Modelleigenschaft.

**Reproduktion.**
- `timeout 540 python3 v2_symmetrie_laeufe.py std frame`, `… std com`, `… shift frame`; dann `python3 v2b_symmetrie_auswertung.py`
- `timeout 540 python3 v10_exakt_mehrstabil.py std` und `… shift`
- `timeout 540 python3 v12_L4_attraktor.py rk4` (≈ 7 min) und `… exakt` (≈ 3 min)

**Nicht geprüft.** Die Kartenzählungen (72 Punkte |Δγ₁| > 10⁻³, 662 Feinsweep-Paare) sowie K2, K3, L2, L3, Z1 und Z2.

---

## RT-01 Fensterbilanz am Hot-Spot, Tab. 9.3 → **bestätigt**

**Methode.**
- Schleife über die **unveränderte** skalare Referenz-Engine (`rk4_step`), (0°; 208,421°), 155 s.
- v_S = ż + q̄̇(t) mit **eigener** Profilgeschwindigkeit.
- Zusätzlich eigene RK4 in zwei Formulierungen.

**Ergebnis.**
- **Skalar, Fenster ab 5 s:**

| T_w | N1 / N | δ / ppm | R / ppm | Q+E / ppm | Δv_S / (m/s) |
|---|---|---|---|---|---|
| 10 s | 6,333041 | −6815,5 | −6737,7 | −77,7 | −0,66097 |
| 30 s | 6,361711 | −2319,3 | −2246,0 | −73,3 | −0,66100 |
| 70 s | 6,369854 | −1042,3 | −962,5 | −79,8 | −0,66097 |
| 150 s | 6,373122 | −529,8 | −449,1 | −80,7 | −0,66089 |

- Die N1-Werte sind **gleich Tab. 9.3** (Quelle: AP v2.4 Z. 3540–3548).
- R·T = −67 377 ppm·s mit 0,017 % Spannweite.
- Potenzfit an R: −1,00004. Potenzfit an δ: −0,9451. Aus den Tabellenwerten: A = −67 356 ppm·s, Q = −78,7 ppm, Residuum ≤ 4,6 ppm.
- Synthetisch ergeben Q = 0 / −40 / −78 / +78 ppm die Exponenten −1,000 / −0,972 / −0,947 / −1,063.
- **Nach dem Einschwingen** (10-s-Fenster): Q+E = −58,5 / −58,5 / −92,0 / −58,5 ppm, |R| ≤ 1,9 ppm.

**Präzisierung.** In der exakten Dynamik ist der Hot-Spot ein **streng periodischer P1-Orbit** (σ_v = 2·10⁻¹¹ m/s an den Periodenbeginnen 10–25 s, `v9`). Die Begründung der Gruppe, Q schwanke, weil „der Zustand nicht streng periodisch“ sei, trifft nur auf die RK4-Bahn mit 50 µs zu (σ_v 7–9·10⁻⁵ m/s). Die Schwankung ist ein Artefakt der Numerik und keine Eigenschaft des Modells.

**Reproduktion.** `timeout 540 python3 v8_skalar_tab93.py` (≈ 20 s); `python3 v3_randterm.py fit` (Tab.-9.3-Fit)

---

## RT-02 Realisierungsabhängigkeit des Exponenten; Punkt (0,0) → **eingeschränkt**

**Methode.** Eigene RK4 in den Formulierungen frame und com, 155 s, Hot-Spot mit φ₃ = 208,421° und 11·360°/19, dazu (0,0). Exakte Bahn für (0,0), 25 s.

**Ergebnis.**
- **Exponent je nach Realisierung:**

| Engine | HS 208,421°: Exponent (Δv_S) | HSx 11·360/19: Exponent (Δv_S) |
|---|---|---|
| eigene, frame | −0,9363 (−0,542 m/s) | −0,9479 (−0,569 m/s) |
| eigene, com | −0,9363 (−0,5505 m/s) | −0,9455 (−0,518 m/s) |
| skalar | −0,9451 (−0,661 m/s) | – |

- Die Spanne −0,936 … −0,948 liegt in der Gruppenspanne −0,936 … −0,949.
- R·T ist je Lauf auf 0,006–0,053 % konstant. Der Attraktor ist immer derselbe (λ 75,09 %).
- **Q in Fenstern auf dem Attraktor** über alle eigenen HS-Läufe: −33,4 … −108,7 ppm. Die Spanne ist breiter als die der Gruppe (−58,5 … −92,0).
- **(0,0), eigene Läufe:** |R| ≤ 2,1 ppm in allen 10-s-Fenstern; δ ≈ Q liegt zwischen −44,9 und +17,6 ppm. Das ist bestätigt.
- **Widerlegt ist der Teil „σ_v = 0,030 m/s (aperiodisch)“:**
  - Exakte Dynamik: (0,0) ist ein **streng periodischer P2-Orbit**. v_S an den Periodenbeginnen wechselt zwischen −0,218646 und −0,278439 m/s, die Streuung der Teilfolgen beträgt 1,0·10⁻¹¹ bzw. 2,2·10⁻¹¹ m/s.
  - σ_v = 0,0299 m/s ist genau die halbe P2-Alternation. In der RK4 (50 µs) streuen die Teilfolgen numerisch um 1,1·10⁻⁴ bzw. 2,5·10⁻⁴ m/s.

**Reproduktion.**
- `timeout 540 python3 v3_randterm.py frame`, `… com` (je ≈ 3,5 min); `python3 v3_randterm.py fit` → `v3_randterm_ausgabe.txt`
- `timeout 540 python3 v9_exakt_periodik.py S0` bzw. `HS`

---

## RT-03 Quadraturrest Q gegen Δt, Mechanismus → **bestätigt**

**Methode.**
- Eigene RK4 (frame) ab dem Zustand bei 30 s, Δt = 50 / 25 / 12,5 / 6,25 µs, Fenster 32–42 s.
- Für L1 zusätzlich die **exakte Bahn** auf demselben Raster:
  - Abtastfehler exakter Werte Q_abtast = (1/L)ΣN_exakt(t_i) − ⟨N⟩_exakt;
  - J und θ des Aufsetzens aus der exakten Bahn.

**Ergebnis.**

| Δt | Q_RK4 (L1) | Stufenmodell ∓J/(3L) | Q_abtast exakt | J(θ−½)/L | θ |
|---|---|---|---|---|---|
| 50 µs | −20,840 | −20,928 | −16,151 | −16,239 | 0,241 |
| 25 µs | −10,435 | −10,464 | −0,524 | −0,543 | 0,483 |
| 12,5 µs | +5,223 | +5,232 | +7,298 | +7,306 | 0,965 |
| 6,25 µs | +2,615 | +2,616 | +3,380 | +3,382 | 0,931 |

(Alle Q in ppm; J = 0,8007 N.)

- Q_RK4 folgt dem RK4-Stufenmodell auf 0,04–0,4 %. Der Abtastfehler exakter Werte ist eine andere Größe.
- Damit ist die These der Gruppe bestätigt: Q ist keine reine Abtastung exakter Werte, sondern enthält die O(Δt)-Fehlverteilung des Aufsetzimpulses durch RK4. Beide Anteile sind O(Δt).
- **E (frame):** 1,849·10⁻⁷ / 4,62·10⁻⁸ / −2,31·10⁻⁸ / 2,89·10⁻⁹ N, gleich den Gruppenwerten. In der Formulierung com ist E ≈ 3·10⁻¹⁴ N. E ist also der Simpson-Defekt der vorgegebenen Beschleunigung und hängt an der Formulierung.
- **K1:** Q < 10⁻⁶ ppm.
- **HS:** Q = −96,2 / −14,7 / −19,9 / −3,7 ppm, nicht monoton fallend. Observablen: λ 75,0915 → 75,0853 %, F_max 38,495 → 38,477 N.

**Reproduktion.** `timeout 540 python3 v4_quadratur.py lauf` (≈ 4 min); `timeout 540 python3 v4_quadratur.py exakt` → `v4_quadratur_ausgabe.txt`

**Einschränkung.** Die exakte Gegenprobe gilt nur für den periodischen Punkt L1. HS und S0 sind in der exakten Dynamik ebenfalls periodisch (P1/P2). Ihr „schwankendes θ“ ist eine Eigenschaft der RK4-Bahn.

---

## RT-05 Fensterbedarf für die Nullkontrolle (ε = 10⁻⁴) → **eingeschränkt**

**Methode.**
- Eigene RK4 (com), 400 Perioden. v_S(t) innerhalb der Periode wird exakt aus der diskreten Impulsbilanz rekonstruiert (Kontrolle 1,5·10⁻¹² m/s).
- Direkte Fensterung mit Zufallsstart, (i) über ganze Perioden und (ii) mit der Länge T_w + U·T, U gleichverteilt.
- Periodenanalyse der v_S-Werte an den Periodenbeginnen, mit eigener RK4 (155 s) und exakter Bahn.

**Ergebnis.**

| Zustand | v_S,max | (a) T_w worst | (a) rms | max\|a_S\| | (b-ii) bei 100 µs |
|---|---|---|---|---|---|
| HS | 0,3786 m/s | 772 s | 329 s | 49,4 m/s² | 5,0 s |
| S0 | 0,5281 m/s | 1077 s | 338 s | 53,4 m/s² | 5,4 s |
| L1 | 0,1268 m/s | 259 s | 88 s | 10,2 m/s² | 1,04 s |
| K1 | 0,0310 m/s | 63 s | 28 s | 3,67 m/s² | 0,37 s |

- **(a) und (b-ii)** sind bestätigt.
- **Freie Fenster** erreichen in der direkten Fensterung 96 % der Schranke 2v_max/(gT): HS bei 1 s 73 997 ppm gegen 77 255 ppm.
- **(b-i) S0 ist widerlegt:**
  - σ_v = 0,0299 m/s ist die P2-Alternation und keine Zyklusstreuung.
  - Phasenstarr über eine **gerade** Periodenzahl: in der exakten Dynamik |Δv_S| < 10⁻¹⁰ m/s, also kein Randterm. In der RK4 max 1,0·10⁻³ m/s, also T_w ≈ 1 s.
  - Über eine **ungerade** Zahl: |Δv_S| = 0,0598 m/s, also T_w ≈ 61–62 s.
  - Die „43 s für aperiodische Zustände“ aus der Zusammenfassung sind damit nicht belegt.
- **(b-i) HS:** Exakt P1, also 0. In der RK4 mit Zufallsstartphase und 1 s Fensterlänge max 216 ppm, bei 5 s 35 ppm. Der Periodenbeginn-σ_v unterschätzt die Streuung an anderen Phasen (Aufsetzjitter der RK4).
- **(c)** 674 s gelten nur für die Archivrealisierung. Eigene Realisierungen haben Δv_S = −0,52 … −0,57 m/s, also 528–580 s.
- **Ergänzung:** L6 (Quasi-P3) im Fenster 50–60 s über 100 Perioden ergibt δ = −5978 ppm, davon R = −5977 ppm. Über 150 Perioden (durch 3 teilbar) sind es −0,9 ppm. Das stützt die Empfehlung „k·T bei P-k-Orbits“ der Gruppe; bei S0 hat die Gruppe sie aber nicht angewandt.

**Reproduktion.**
- `timeout 540 python3 v5_fensterbedarf.py lauf`, dann `python3 v5_fensterbedarf.py` (benötigt `v3_randterm_frame.npz`)
- `timeout 540 python3 v9_exakt_periodik.py S0`
- `python3 v11_L6_fenster.py` → `v11_L6_fenster_ausgabe.txt` (L6)

**Einschränkungen.** Wie bei der Gruppe gilt der Simulationsreferenzsatz: bewegte Masse = M, Messkette ideal. (d) habe ich nicht nachgerechnet. Der Mechanismus J(θ−½)/f_s wurde aber an L1 mit exakten Werten bestätigt (RT-03).

---

## Zusatzprüfungen

- **SYM-05:** Datenprüfung (23) über 171 Paare i<j: mittlere Differenz +5,30·10⁻⁶ N, max 7,54 mN (`v7_kartenband.py`). Die Fundstellen AP §8.4 (Z. 3663–3675) und A7 (Z. 330–340) sind wörtlich vorhanden.
- **Skriptfehler der Gruppe:** `s8_fensterbedarf.py` setzt `sig = np.std(vc[300:400, j])` ohne Rücksicht auf die Orbitperiode. Für S0 misst das die P2-Alternation, daraus folgt die falsche Angabe „43 s“. Dieselbe Fehldeutung „aperiodisch“ steht in RT-02.

## Kontrolle

Nach Abschluss wurde der Repo-Baum auf `__pycache__` geprüft (`find code docs -name __pycache__`): nichts gefunden.
