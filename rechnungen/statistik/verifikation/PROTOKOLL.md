# P2 · Gegenprüfung der Prüfgruppe „statistik“ (Statistik und Identifizierbarkeit der Präregistrierung v2)

> **Vermerk zur Übernahme (04.10.2026).** Protokoll aus der Gesamtprojektanalyse 10/2026, Stand 02.10.2026, unverändert bis auf Pfade und Quellenangaben. Geprüft wurde der Repository-Stand `cd7be6a` (28.09.2026) mit der Präregistrierung v2 vom 25./28.09.2026; die späteren Änderungen aus PR #13 und PR #14 (unter anderem Präregistrierung v2 mit Arbeitsfestlegungen, `code/auslegung.py`, `code/ereignisloeser.py`) sind nicht eingearbeitet. Alle Zahlen sind Simulation oder Analytik, keine Messdaten. Verweise wie „L1a-019“, „P1 §3“ oder „B01–B14“ zeigen auf Arbeitsdokumente der Analyse, die nicht im Repository liegen. Quellen außerhalb des Repositorys sind als „(lokaler Bestand, nicht im Repository)“ gekennzeichnet. Startbefehle und Grenzen je Gruppe: [`rechnungen/README.md`](../../README.md).

Stand 02.10.2026 · ursprünglich lokal, jetzt unter `rechnungen/` · Rolle: unabhängiger Gegenprüfer, Ziel: Befunde widerlegen.
Kennzeichnung: **[R]** eigene Rechnung, **[Q]** Quellenangabe, **[A]** Annahme.

Alle eigenen Skripte sind neu geschrieben und importieren **keinen** Code der Gruppe und keinen Repo-Code (Profilformel
aus `code/finesweep.py` neu implementiert; gelesen wird nur `data/finesweep_2deg_120_240.csv`). Andere Rechenwege als die Gruppe:
analytische Fehlerfortpflanzung und Quadratur statt Bootstrap-Monte-Carlo (v1), eigene Zeitreihen- und Segmentierungskette (v2),
Ordnungsstatistik (v3), eigener Zeltfit über Projektionsmatrizen (v4), Störungsrechnung 2. Ordnung statt RK4 (v5), vereinfachtes
Kampagnenmodell mit unabhängigen Tests (v6). Geprüft auf Grad/Radiant (`np.radians` vor jedem `exp(−ikφ)`; Jitter
σ_t = 56 µs → 2πf·σ_t = 0,00352 rad = 0,20°), Phasenvorzeichen (Modul verzögert, a(t − τ_j), τ_j = φ_j/(2πf); Gegenprobe:
F_min(120°) = 5,6452 N und F_min(100°) = 5,1759 N wie A4), N_k-Konvention (2/N)·Σ x·e^{−ikθ} (|N_k| synchron 3,8909/1,2823/0,5533 N
→ max. Kammfaktor-Werte 0,4504/0,2924/0,5533 N wie s0), Bandbegrenzung durch Abschneiden der DFT.

Reproduktion (alle aus diesem Verzeichnis):

```
cd rechnungen/statistik/verifikation
PY="env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../../../code OMP_NUM_THREADS=2"
$PY timeout 540 python3 v1_pb1_bindung_analytisch.py          # < 1 min
$PY timeout 540 python3 v1b_fmin_allein_L4.py                # < 1 min (importiert v1)
$PY timeout 540 python3 v2_fmin_zeitreihe_mc.py 200           # ≈ 3 min
$PY timeout 540 python3 v3_triphasik_rauschbias.py            # ≈ 1 min
$PY timeout 540 python3 v4_h2_fenster_halbbreite.py 1500 1000 # ≈ 4 min
$PY timeout 540 python3 v5_hertz_stoerung_oc.py               # < 5 s
$PY timeout 540 python3 v6_praezisionsparadox_oc.py           # ≈ 10 s
```

Ausgaben: `*_ausgabe.txt` je Skript, dazu `v2_fmin_zeitreihe_mc.csv`, `v4_h2_fenster.csv`.

---

## STA-01 · PB1-Herleitung und „F_min bindet“ → **eingeschränkt**

**Frage.** Stimmen Δ(F_min) = 0,1173 N, u_c ≤ 0,0327/0,0269 N, die P = 0,8-Grenzen 17,4/14,1 mN und „F_min bindet“?

**Methode [R].** v1 A: eigene Zeitbereichskurven (16 000 Punkte/Periode), Δ_q = 0,25·D_q. v1 B: P(PB1 ∧ kein |z| > c) je Test
geschlossen (ν = ∞: p₁ = 2Φ(min(R − c, c)) − 1) bzw. Quadratur über S² ~ χ²_ν/ν; Nullstellensuche für p₁^m = 0,8. v1 C: analytische
u_q aller 7 Größen an allen 21 Punkten (Hüllkurvensatz für F_min; Rauschmodell der Gruppe s2: σ_h = 0,11 mN, Modulamplitude σ_a,
nicht erfasste Modulphase σ_p; n = n₀ = 20, n₁ = 21).

**Ergebnis.**
- ΔF_Zelt = 0,4693 N, Δ = 0,1173 N; k_max = 9: 0,5173/0,1293 N; Δ₁/Δ₂/Δ₃ = 112,6/73,1/138,3 mN; c(∞) = 3,583 → 32,7 mN,
  c(19) = 4,356 → 26,9 mN. **Bestätigt.**
- P = 0,8 bei 147 Tests: R = c + Φ⁻¹((1 + 0,8^{1/147})/2) = 6,754 → u ≤ 17,4 mN (ν = ∞); Quadratur ν = 19: R = 8,320 → 14,1 mN;
  m = 21: 19,1/15,7 mN; m = 1: 24,1/20,0 mN. **Exakt wie die MC-Werte der Gruppe.**
- „Bei u = Δ/c ist P(PB1) = 0“ gilt nur für ν → ∞; bei ν = 19 ist p₁ = 0,217 je Test (147 Tests: 2,5·10⁻⁹⁸ ≈ 0). Kleinigkeit.
- **„F_min bindet“ ist für mechanische (modulproportionale) Streuung widerlegt.** Analytische u_q stimmen mit den Bootstrap-Medianen der
  Gruppe auf 2–5 % überein (L0: u_F 0,28 gegen 0,26 mN; L4: u_N1 30,6 gegen 29,5 mN), aber min Δ_q/u_q ist:
  L0 F 372 / N₁ 562 / N₂ 499 / N₃ 1194 (F bindet); L1 117 / **67** / 120 / 453; L2 35 / **20** / 36 / 138; L3 11,8 / **6,7** / 12,0 / 46;
  L4 5,9 / **3,3** / 6,0 / 23; L5 3,5 / **2,0** / 3,6 / 14. Ab L1 bindet Re/Im N₁: seine Struktur auf dem Schnitt ist klein
  (Kammfaktor ≤ 0,116, Δ₁ = 113 mN), sein Rauschen skaliert aber mit dem vollen Einzelmodul-|N₁| = 1,297 N. Reine Modulamplitude 1 %:
  F 39 gegen N₁ 20; reines weißes Rauschen: F 96 gegen N₂ 164 (F bindet); reine Phase 0,1°: F 82 gegen N₂ 106.
- Folge: P(bestätigt | exakt) = 0,8 wird (σ_p = 10°·σ_a wie s2) schon bei σ_a = 3,0 % erreicht, d. h. bei u_c(F_min) ≈ 10 mN (Median),
  nicht erst bei 14–17 mN; betrachtet man nur F_min, wären es σ_a = 5,5 % bzw. u_c(F_min) ≈ 18,7 mN. Die s2-Ausgabe der Gruppe zeigt
  dasselbe (L4: u_N1 = 29,5 mN gegen Δ₁ = 112,6 mN → Δ/u = 3,8 < c = 3,95 → P(PB1) = 0).

**Einschränkungen.** Tests unabhängig angenommen (P(bestätigt|exakt) L0–L2 analytisch 0,905 statt 0,93 der korrelierten s2-Kampagnen);
Rauschmodell der Gruppe übernommen [A].

## STA-02 · F_min-Schätzer → **eingeschränkt**

**Frage.** Ist das registrierte Verfahren (Phasenmittelung, Bandbegrenzung, Minimum) praktisch unverzerrt, Verfahren B stark verzerrt?

**Methode [R].** v2: eigene Zeitreihen (f_s = 6,4 kHz, N_z = 100, zufälliger Sub-Sample-Versatz), Jitter zyklusweise je eigenem Zyklus
von Modul 2/3, Segmentierung am Index von Modul 1, lineare Interpolation auf 2000 Stützstellen, DFT-Abschneiden; 200 Läufe je Zelle.
Wahrheit zweifach: Soll-Kurve mit Jitterdämpfung (wie Gruppe) und Kurve mit den im Lauf **gemessenen** Zeigern ρ_jk (§8.2, A9.5).

**Ergebnis (mN, Bias ± MC-SE, sd je Lauf).**
- A, k_max = 9, ohne Jitter: +0,03 … +0,11 (σ = 5) bzw. +0,05 … +0,09 und −0,18 bei 120° (σ = 20); sd 0,07–0,36. Davon rauschfrei
  +0,08 … +0,10 Interpolationsanteil (linear, trifft Einzel- und Kombinationsläufe gleich). **Bestätigt** (Gruppe: +0,03 … +0,13; −0,18).
- A ohne Bandbegrenzung, σ = 20: −1,4 … −3,7 (ohne Jitter), −4,4 bei 120° mit Jitter. **Bestätigt** (−1,2 … −4,3).
- B (Rohminimum je Zyklus): −4,7 … −42,0 ohne, −18,6/−46,3 mit Jitter bei 120°; 46,3/129,3 = 36 % von Δ. **Bestätigt.**
- Jitter 56 µs, 120°: gegen Soll −0,76/−0,78, sd 0,52–0,55 (= Gruppe −0,73 … −0,77); **gegen die gemessenen ρ (registrierter Vergleich)
  +0,10/+0,05, sd 0,13/0,32** – also nur der Interpolationsanteil. Die „sd 0,5–1,0 mN mit Jitter“ und der „Bias −0,75 mN am
  Triphasik-Punkt“ sind echte Streuung der realisierten Konfiguration, die die Vorhersage über ρ mitführt; für H1 sind sie kein Bias.
  Die Aussage der Gruppe „einziger nennenswerter Rest ist der Minimum-aus-drei-Effekt unter Jitter“ ist daher für das registrierte
  Verfahren überdehnt.

**Einschränkungen.** Weißes Rauschen; Jitter normal und unabhängig je Zyklus [A]; Konfigurationsmittel über n Läufe nicht simuliert
(verkleinert alle Rauschanteile weiter).

## STA-03 · Erreichbares u_c → **eingeschränkt**

**Ergebnis [R].** σ = 20 mN, 6,4 kHz, 10 s → σ_h = 0,1118 mN, sd(F_min − ⟨N⟩) je Lauf 0,335 mN (Gruppe 0,34). Analytisch L0
u_F = 0,28 mN (Median, Spanne 0,22–0,35), u_N2 = 0,13 mN; Verhältnis zu 26,9–32,7 mN ≈ 96–117 („≈ 100-fach“ bestätigt) und zu
14,1–17,4 mN ≈ 50–62. Die Zahl ist aber eine reine Annahmenfolge [A]: σ = 20 mN, T_a = 10 s, n = n₀ = 20 und ein nicht erfasster
Phasenrest von 0,02° (= 0,2°/√100), der im Modell der Gruppe den Jitter vertritt; ohne diesen Rest (Jitter voll über ρ erfasst) wären
es ≈ 0,15 mN. Fehlzuschreibung: „6 %/0,6° → P(PB1) = 0“ und „PB1 bindet ab Δ_F/u_c ≈ 7–13“ liegen an Re/Im N₁ (Δ₁/u ≈ 3,3), nicht an
F_min (Δ_F/u ≈ 5,9). v1b: nur die 21 F_min-Tests ergäben bei L4 P = 0,48, nur die 42 N₁-Tests P = 0,000; bei L3 F_min allein 0,99,
N₁ allein 0,87.

## STA-04 · Rauschbias am Triphasik-Punkt → **eingeschränkt** (Jitterteil widerlegt)

**Methode [R].** v3: Ordnungsstatistik der drei gleich tiefen Minima (Kovarianz exakt aus den Harmonischen; weißes Rauschen ist
zwischen den Minima unkorreliert, Korrelation 0,0000) und Monte-Carlo-Gegenprobe (20 000 Kampagnen). Zwei Lesarten von u_c,erw:
(i) Präreg §4 (u_c,erw² = s_q²/n_min + u²(ŷ), s_q aus Pilotläufen mit **einem** Minimum), (ii) Gruppe (sd des Minimums aus drei).

**Ergebnis (n = 20; |b|/u in (i) / (ii)).**
- weiß: n₀ = 20: 0,31 / 0,41; n₀ = 40: 0,12 / 0,16; n₀ = 60: 0,00 / 0,00 (Gruppe 0,42/0,18/0,01). Verletzung bei n₀ ≲ 2n bestätigt,
  in Präreg-Lesart etwa 25 % kleiner.
- modul: 0,00 / 0,00; 0,23 / 0,35; 0,35 / 0,53 (Gruppe 0,02/0,33/0,54). Bestätigt.
- **Jitter:** Das Modell der Gruppe (s1b) lässt die Vorhersage mit Sollphasen rechnen und die Einzelläufe ohne Phasenrauschen; das
  widerspricht §8.2/A9.5 und dem eigenen s2-Modell. Reproduziert ergibt es 1,67 (ii) bzw. 0,83 (i). Registriert (Jitter über gemessene ρ):
  **b = 0** (v3) bzw. +0,05/+0,10 mN Interpolationsanteil (v2). Physikalisch konsistent nicht erfasster Phasenversatz in Einzel- UND
  Kombinationsläufen: 0 (n₀ = n), 0,25/0,43 (n₀ = 2n), 0,38/0,65 (n₀ = 3n) – verhält sich wie „modul“, nicht „für jedes n₀“.
- Der Effekt setzt Module voraus, die auf ≲ 0,01–0,03 % gleich sind: 0,1 % Amplitudenunterschied trennt die Minima um 1 und 2 mN
  (≫ σ ≈ 0,07–0,2 mN), 1 % um 12 und 23 mN. Bei ungleichen Modulen liegt die Spitze zwischen zwei Rasterpunkten; P(Abstand der
  konkurrierenden Minima < 0,6 mN) ≈ 0,009.

## STA-05 · H2-Halbbreite → **bestätigt**

**Methode [R].** v4 Teil 3: eigener Zeltfit (0,01°-Kandidaten über Projektionsmatrizen, Verfeinerung 0,001°), weißes Rauschen,
n₀ = n, 1000 Kampagnen.

**Ergebnis.** HB = 0,698° (A4, SNR 1, n = 20, w = 6; Gruppe 0,735°), 0,642° (ref, SNR 1, n = 20, w = 16; Gruppe 0,645°), 1,197° (ref,
SNR 0,5, w = 20; Gruppe 1,234°); κ = HB·SNR·√n = 3,12 / 2,87 / 2,68 / 2,72 / 2,38 (A4 w = 4, SNR 4) – Faustregel n ≈ (3/SNR)² ist
leicht konservativ. Messseite allein: Faktor 1,7–2,9 kleiner („etwa Verdopplung“ bestätigt). Zusatz: Beim symmetrischen A4-Zelt
bleibt φ* oft exakt auf dem Rasterpunkt 120° hängen (P(φ*_Mess = 120°) = 0,17 bei w = 6, 0,41 bei w = 4/SNR 4, 0,91–0,98 bei w = 20);
Δφ* = 0 exakt in 2–62 % der Kampagnen; κ sinkt dann auf 1,9–2,4. Beim asymmetrischen Referenzzelt tritt das nicht auf.

## STA-06 · Fensterregel → **bestätigt** (mit Erweiterung)

**Methode [R].** v4 Teil 1 (rauschfrei) und Teil 2 (NEU: Fensterwahl mit der **verrauschten** Phase-0-Vorhersage, wie in Teil B,
1500 Ziehungen, n = n₀ = 20).

**Ergebnis.** Rauschfrei kleinste Abweichung (w = 4°): A4 1,08 mN, Referenz 1,05 mN, Engine-CSV 1,02 mN → Fenster nur bei
u_c,erw ≥ 4,31/4,19 mN bzw. σ_run ≥ 9,6/9,4 mN (Gruppe 4,4/4,0 mN, 9,8 mN). Mit verrauschter Vorhersage ist die Existenz zufällig:
A4 P(Fenster) = 0,98/0,89/0,91/0,94/0,86 (SNR 0,25/0,5/1/2/3), 0,26 (SNR 4, u_c,erw 3,8 mN), 0,06 (SNR 8), 0,001 (SNR 16), 0 (SNR ≥ 32,
u_c,erw ≤ 0,48 mN); Referenz 0,69–0,98 bis SNR 16, 0,46 bei SNR 32 (u_c,erw 2,8 mN), 0,027 bei SNR 100 (0,91 mN). Kernaussage
(bei u_c,erw ≲ 1 mN ist H2 „nicht entscheidbar“) bestätigt; zusätzlich fehlt das Fenster auch bei geringer Präzision in 2–31 % der
Fälle, und w streut bei niedrigem SNR über 4–20°.

## STA-07 · Bias des Zwei-Geraden-Fits → **bestätigt**

v4 Teil 1: φ* − 120° = −0,044° … −0,219° (Referenz), −0,044° … −0,212° (CSV), 0,000° (A4) – identisch mit der Gruppe; v4 Teil 3:
|E[Δφ*]| ≤ 0,017° in allen Fällen.

## STA-08 · Mehrfachtests H1 → **bestätigt**

**Methode [R].** v5 Teil 2: Bonferroni-Schranke Σ_Tests 2·P(Z⁰ < −c, Z¹ < −c) (bivariat normal); v6: vereinfachtes Kampagnenmodell
(unabhängige Tests, χ²₃₇-Unsicherheit), 10 000 Kampagnen je Zelle.

**Ergebnis.** Typ-I-Schranke über 147 Tests (c = 3,948, ν = 37): 1,6·10⁻⁵ (ρ(z⁰,z¹) = 0,25), 1,9·10⁻⁴ (0,5), 1,9·10⁻³ (0,8) – verträglich
mit 0–0,005 der Gruppe; nur z⁰: 0,05. OC (v6) P(falsifiziert)/P(bestätigt): exakt 0,000–0,001 / 0,903, 0,904, 0,902, 0,792, 0, 0
(Gruppe 0,93/0,93/0,93/0,88/0/0); Kopplung 1 %: 1/1/1/0,084/0,004/0,002 (Gruppe 1/1/1/0,097/0,005/0,000); N₂ 1 %: 1/1/0,009/0,001
(Gruppe 1/0,997/0,012/0). PB1-Fehlbestätigung am Rand: Φ(−3,583) = 1,7·10⁻⁴ (geschlossen).

## STA-09 · Präzisionsparadox → **bestätigt**

v6: P(bestätigt) bei 1 % Kopplung 0/0/0/0,22/0/0, bei N₂ 1 % 0/0/0,73/0,79/0/0, bei N₂ 3 % 0/0/0/0,63/0/0 (L0–L5): nicht monoton.
Niveaus bei L3 kleiner als bei der Gruppe (0,51/0,88), weil unabhängige Tests mehr Gelegenheiten für ein einzelnes |z| > c bieten.
IUT-Vorschlag: 1,00 auf L0–L3 (exakt, 1 %, 3 %), bei L4 nur 0,02 (Gruppe 0,24) – ebenfalls wegen N₁.

## STA-11 · Identifizierbarkeit / Hertz-Kontakt → **bestätigt** (Zahlen), z-Angabe zu niedrig

**Methode [R].** v5 Teil 1: Störungsrechnung 2. Ordnung im Frequenzbereich, M·ÿ + c·ẏ + K₀y + q·y² = μMā, q = K₀/(4δ₀);
Superpositionsresiduum R_k = (1 − H(kω))·q·FT[(Σ_j y_j)² − Σ_j y_j²]_k. Unabhängig vom RK4 der Gruppe.

**Ergebnis.** max|r_F| k ≤ 3/6/9: 300 Hz 0,55/0,77/1,02 mN (RK4 0,51/0,79/1,07); 120 Hz 3,75/6,02/11,1 (3,44/6,29/12,3);
60 Hz 20,9/158/203 (19,0/196/207; Abweichung bei k ≤ 6 wegen Resonanz 6f = f_n, wo die Störungsrechnung ungenau ist). N₃-Residuum
300 Hz 0,47 mN (RK4 0,41). Kopplung 0,1 %/1 %: 1,22/12,2 mN (= x·1,216 N). Luftwiderstand 0,5·1,2·1·10⁻³·0,24² = 0,035 mN [A: A = 10 cm²].
**P(falsifiziert) auf L0 = 1,000** für Hertz 300 Hz und 0,1 % Kopplung (v5 Teil 3, 20 000 Kampagnen); größtes |r|/u = 9,1 bzw. 10,7, und
zwar bei Re N₃ (124°), nicht bei F_min. Die Angabe der Gruppe „z ≈ 4 bei L0“ (größtes F_min-Residuum / Median-u) unterschätzt die
Empfindlichkeit; die Aussage „H1 wird bei hoher Präzision schon dadurch falsifiziert“ ist damit eher stärker.

## STA-12 · Trennung Modellabweichung/Messartefakt → **eingeschränkt**

[Q] §9.4 Z. 488 nennt Ursachen ohne Zuordnungsregel (L5a-070 bestätigt); A9.2 P0.1: „Einfluss von Laststelle, Querkraft und
Superpositionsfehler der Elektronik je ≤ 0,1·Δ_q“, P0.3: „Nebenschlusseinfluss ≤ 0,1·Δ_q“, Tabelle F G7 „0,1 % Empfindlichkeitsänderung“.
[R] 0,1·Δ_F = 12,9 mN gegen c·u_F(L0) = 3,95·0,26–0,28 = 1,0–1,1 mN (≈ 12-fach); N₃: 13,8 mN gegen 0,19–0,36 mN (38–72-fach).
Einschränkung: Laststelle, Querkraft und Nebenschluss sind lineare Einflüsse, die nach der eigenen Analyse der Gruppe (STA-11, A2.1)
keine H1-Signatur erzeugen; der Vergleich mit der H1-Nachweisgrenze trifft nur den Superpositionsfehler der Elektronik, die
Linearitätsprüfung P0.4 („innerhalb der Unsicherheit“) und Kontakt-/Kettennichtlinearität. Eine G7-Änderung zwischen den Phasen
führt nach STA-10 zu „nicht entscheidbar (Drift)“, nicht zu „falsifiziert“. Die Folgerung „ein Artefakt, das alle Phase-0-Prüfungen
besteht, kann H1 signifikant falsifizieren“ gilt daher für nichtlineare Artefakte, nicht für die genannten Schranken insgesamt.

## STA-00 · Lokale Überarbeitung → **bestätigt** (Stichprobe)

md5 der Abschnitte A8, A9.6, Tabelle F in Repo- und lokaler Fassung identisch; A4 verschieden; die PB1-Zeilen (0,0327/0,0269 N)
kommen im diff nicht vor.

## Nicht geprüft

STA-10 (Driftlogik) – nicht nachgerechnet.

## Fehler und Schwächen in den Skripten der Gruppe

1. `s1b_rauschbias_triphasik.py`, Modell 'jitter': Vorhersage mit Sollphasen (`E_of(p2)`), Einzelläufe ohne Phasenrauschen → b/u = 1,62
   ist ein Modellartefakt (widerspricht §8.2/A9.5 und `s2_h1_oc_kampagne.py`, wo ρ = Sollphase plus erfasster Jitter).
2. `s1b`: u_c,erw als sd des Minimums aus drei statt nach Präreg §4 (Pilot-s_q, ein Minimum) → Quotienten um Faktor ≈ 1,34 zu groß.
3. `s4_identifizierbarkeit.py`, `summarize`: ein gemeinsames u_N = 0,12 mN für alle Harmonischen → z für N₃ unterschätzt (≈ 4 statt ≈ 9).
4. Deutung von s2: „F_min bindet“ aus dem Vergleich F_min gegen N₂ abgeleitet, obwohl die eigene Ausgabe u_N1 zeigt, dass N₁ ab L1 bindet.

## Annahmen dieser Gegenprüfung

Rauschmodell und Rauschstufen L0–L5 der Gruppe [A]; weißes Rauschen; identische Module (außer v3 Teil 4); A4-Beispiel (starr, μ = 0,4,
10 Hz, k_max = 9) bzw. Referenzform; Normalverteilung der Residuen (v5/v6); unabhängige Tests in v6.
