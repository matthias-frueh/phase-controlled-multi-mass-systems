# P2 · Prüfgruppe „statistik“ – Statistik und Identifizierbarkeit der Präregistrierung v2

> **Vermerk zur Übernahme (04.10.2026).** Protokoll aus der Gesamtprojektanalyse 10/2026, Stand 02.10.2026, unverändert bis auf Pfade und Quellenangaben. Geprüft wurde der Repository-Stand `cd7be6a` (28.09.2026) mit der Präregistrierung v2 vom 25./28.09.2026; die späteren Änderungen aus PR #13 und PR #14 (unter anderem Präregistrierung v2 mit Arbeitsfestlegungen, `code/auslegung.py`, `code/ereignisloeser.py`) sind nicht eingearbeitet. Alle Zahlen sind Simulation oder Analytik, keine Messdaten. Verweise wie „L1a-019“, „P1 §3“ oder „B01–B14“ zeigen auf Arbeitsdokumente der Analyse, die nicht im Repository liegen. Quellen außerhalb des Repositorys sind als „(lokaler Bestand, nicht im Repository)“ gekennzeichnet. Startbefehle und Grenzen je Gruppe: [`rechnungen/README.md`](../README.md).

Stand 02.10.2026 · ursprünglich lokal, jetzt unter `rechnungen/` · Kennzeichnung: **[R]** eigene Rechnung, **[Q]** Quellenangabe, **[A]** Annahme.
Geprüfte Fassung: `docs/praeregistrierung_v2_entwurf.md` und `docs/praeregistrierung_v2_anhang.md` (Repo, Stand 25.09.2026),
Abgleich mit der lokalen Überarbeitung vom 01.10.2026 (`(lokaler Bestand, nicht im Repository)`).

## Dateien und Reproduktion

Alle Befehle aus `rechnungen/statistik/` mit

```
PY="PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../../code python3"
```

| Skript | Inhalt | Ausgabe | Laufzeit |
|---|---|---|---|
| `s0_pb1_grundlagen.py` | PB1-Nachrechnung, Δ_q aller 7 Größen, was PB1 wirklich verlangt, IUT-Vergleich | `s0_pb1_grundlagen_ausgabe.txt` | ≈ 1 min |
| `s1_fmin_rauschen_mc.py [0/1/2]` | Zeitreihen-MC eines Laufs: Sensorrauschen, f_s, N_z, Jitter, Bandbegrenzung, Schätzverfahren | `s1_fmin_rauschen_mc_cfg*_ausgabe.txt`, `s1_fmin_rauschen_mc.csv` | je ≈ 3–4 min |
| `s1b_rauschbias_triphasik.py` | Rauschbias-Bedingung (§5.4) und Bootstrap-z am Triphasik-Punkt | `s1b_rauschbias_triphasik_ausgabe.txt` | ≈ 4 min |
| `s2_h1_oc_kampagne.py L [600 20 20 9]` (über `run_s2.sh`) | Kampagnen-MC der H1-Entscheidungsregel (Bootstrap-u_c, ν_eff, c, PB1, ŷ⁰/ŷ¹), Rauschstufen L0–L5, 9 Szenarien | `s2_h1_oc_L*_ausgabe.txt`, `s2_h1_oc_L*_n20_n020_k9.csv` | je Stufe ≈ 5–8 min |
| `run_s2_zusatz.sh` | Zusatzszenarien 20 %/30 % Kopplung (Stufen L0, L2–L5, 300 Kampagnen) | `s2_h1_oc_L*_zusatz_ausgabe.txt`, `s2_h1_oc_L*_n20_n020_k9_s9-10.csv` | je ≈ 0,5 min |
| `s5_oc_tabelle.py` | Zusammenfassung der H1-OC-Läufe | `s5_oc_tabelle_ausgabe.txt`, `s5_oc_tabelle.csv` | < 5 s |
| `s3_h2_zeltfit_mc.py [1500]` | H2: Zeltfit-Bias, Halbbreite von Δφ*, Skalierung n(SNR), Fensterregel | `s3_h2_zeltfit_mc_ausgabe.txt`, `s3_h2_zeltfit_mc.csv`, `s3_h2_bias.csv` | ≈ 6 min |
| `s3b_h2_bootstrap_check.py [150 400]` | Stichprobe: Bootstrap-Halbbreite und Überdeckung des H2-Intervalls | `s3b_h2_bootstrap_check_ausgabe.txt` | ≈ 5 min |
| `s4_identifizierbarkeit.py b / a:40,60 / a:120,300` (über `run_s4.sh`) | Superpositionsresiduen von Alternativursachen (Hertz-Kontakt RK4, Zellkennlinie, Drift, Kopplung, Jitter, Phasenversatz) | `s4_identifizierbarkeit_*_ausgabe.txt`, `s4_identifizierbarkeit_*.csv` | Teil b < 10 s, Teile a je ≈ 4–6 min |

Gemeinsames Rechenbeispiel aller Skripte [A]: Präreg-Beispiel A4 (starre Auflage, μ = 0,4, f = 10 Hz, Egg-Profil der Engine,
identische Module, Modul j trägt (μM/3)·a(t − τ_j), τ_j = φ_j/(2πf)), Bandbegrenzung k_max = 9 (zulässig bei starrer Auflage),
Messgrößen wie §4/A9.4 (Mittelkurve je Lauf, Konfigurationsmittelkurve, N_k = (2/N_θ)·Σ N̄·e^{−ikθ}, F_min − ⟨N⟩).
Für H2 zusätzlich die Referenz-Engine im Kontaktast (K = 10⁴ N/m, C = 16 N·s/m, μ = 1). Eigene Skripte geprüft auf:
Grad/Radiant (überall `np.radians` vor `exp(−ikφ)`), Vorzeichen τ = φ/(2πf) (Modul verzögert, wie `linear_solver.waveform`),
N_k-Normierung (Gegenprobe: |N_k| synchron = 3,8909/1,2823/0,5533 N wie `linear_solver --section --rigid --mu 0.4`),
Kammfaktor-Maxima 0,116/0,228/1,0 (wie L5a-065), weißes Rauschen sd(Re N_k) = σ·√(2/(f_s·T_a)) (MC 0,112 mN gegen
Theorie 0,112 mN bei 20 mN, 6,4 kHz, 10 s), lineare Gegenprobe des Hertz-RK4 (Residuum ≤ 0,001 mN).

---

## STA-00 · Quellenstand: Repo-Fassung gegen lokale Überarbeitung vom 01.10.

**Frage.** Ändert die lokale Überarbeitung Entscheidungsregeln, Zahlen oder Statistik?

**Methode.** `diff` der beiden Dateien gegen die Repo-Fassung (nach Abzug des Konvertierungskopfs).

**Ergebnis [Q].** Geändert sind nur Hauptdokument §1 (Einordnung der Vorzeichenregel: „mit Arbeitspapier v2.4 als Aussage über
den Mechanismus zurückgezogen“) und Anhang A3/A4 (dieselbe Einordnung; A4-Schiefeabsatz „bestätigen keine allgemeine
Vorzeichenregel“). §0, §3, §5.3, §5.4, §8, §9, A1, A2, A5–A9, Tabelle C/F und Z sind unverändert; insbesondere PB1, A8 und die
Zahlen 0,0327/0,0269 N sind identisch. Alle folgenden Befunde gelten für beide Fassungen.

**Reproduktion.** Textvergleich der Repo-Fassung mit der lokalen Überarbeitung vom 01.10.2026 (lokaler Bestand, nicht im Repository).

---

## STA-01 · PB1-Herleitung (L5a-065, A4/A8) – Zahl bestätigt, Bedeutung nur „notwendig“

**Frage.** Stimmen Δ(F_min) = 0,117 N und u_c ≤ 0,0327 N (ν → ∞) bzw. 0,0269 N (ν = 19)? Was verlangt PB1 tatsächlich?

**Methode [R].** `s0_pb1_grundlagen.py`: Δ = 0,25·ΔF_Zelt aus `linear_solver.solve` (starr, μ = 0,4); c = t(1 − 0,05/294; ν).
Wahrscheinlichkeit, dass bei exakter Superposition (r ~ N(0, u²), û² ~ u²·χ²_ν/ν) „kein |z| > c“ und PB1 gelten, für 1, 21 und
147 unabhängige Tests; Bisektion auf P = 0,5 und 0,8.

**Ergebnis.**
- ΔF_Zelt = 0,4693 N, Δ = 0,1173 N; c(∞) = 3,583 → u_c ≤ 0,0327 N; c(19) = 4,356 → 0,0269 N (0,42 % von Mg). **Bestätigt.**
- Diese Grenze ist nur **notwendig**: Bei u_c = Δ/c ist PB1 nur für r = 0 exakt erfüllt, P(PB1) = 0. Für P(Bestätigung | exakte
  Superposition) ≥ 0,8 (Präreg §5.4) braucht es bei 147 unabhängigen Tests Δ/u ≥ 6,75 (ν → ∞) bzw. 8,31 (ν = 19), also für F_min
  **u_c ≤ 0,0174 N bzw. 0,0141 N** (21 Tests: 0,0191/0,0157 N; ein Test: 0,0241/0,0200 N). A8 nennt die Grenze korrekt
  „notwendig“; die Formulierung in A4 („PB1 verlangt dann“) ist als Auslegungszahl um etwa den Faktor 2 zu optimistisch.
- Bandbegrenzung: A6 verlangt Auslegungszahlen mit derselben Bandbegrenzung wie die Messung. Mit k_max = 9/6/3 ist ΔF_Zelt
  0,5173/0,5388/0,5730 N, Δ(F_min) = 0,1293/0,1347/0,1433 N (u_c-Grenze ν = 19: 0,0297/0,0309/0,0329 N). Die A4-Zahl gilt für
  das volle Spektrum.
- Δ_q der Harmonischen (A4-Beispiel, unabhängig von k_max ≥ 3): Δ₁ = 0,1126, Δ₂ = 0,0731, Δ₃ = 0,1383 N; notwendige u-Grenzen
  (ν = 19) 0,0259/0,0168/0,0318 N. N₂ hat die strengste absolute Grenze (bestätigt L5a-065 und AUS-03), rauscht aber schwächer:
  bei weißem Rauschen ist sd(Re N_k) = σ·√(2/(f_s T_a)), sd(F_min − ⟨N⟩) ≈ σ·√(2k_max/(f_s T_a)) (s1); im Kampagnen-MC (s2) ist
  u(N₂)/u(F_min) = 0,46–0,53, das Verhältnis Δ/u ist für N₂ gleich groß oder größer als für F_min (L0: 609 gegen 496; L2: 42 gegen
  40). **F_min bindet, N₂ nicht strenger** (Präzisierung zu L5a-065/AUS-03).

**Reproduktion.** `eval timeout 540 $PY s0_pb1_grundlagen.py`

**Einschränkungen.** Unabhängigkeit der 147 Tests ist die ungünstige Annahme (Korrelation erhöht P); die s2-Kampagnen
(korrelierte Tests) liefern P(Bestätigung | exakt) = 0,93 bei u_F = 0,26–3,3 mN (s. STA-08).

---

## STA-02 · Wie wird F_min geschätzt, und wie groß ist der Extremwert-Bias?

**Frage.** Ist F_min verzerrt (Extremwert-Bias ≈ −σ·√(2 ln n)), und wie hängt das vom Verfahren ab?

**Methode.** [Q] Präreg §4/A9.4: F_min ist das Minimum der **Konfigurationsmittelkurve** (je Lauf phasensynchrones Mittel der
Zyklen nach Resampling auf N_θ = 2000, DFT, Koeffizienten über k_max null; dann gleich gewichtetes Mittel der Läufe); also
Phasenmittelung vor der Minimumbildung, mit Bandbegrenzung. Zyklusweise Minima sind explorativ (E4, A2.4).
[R] `s1_fmin_rauschen_mc.py`: Zeitreihen je Lauf mit weißem Sensorrauschen σ ∈ {1, 5, 20} mN je Abtastwert des Summenkanals,
f_s ∈ {2000, 6400, 10000} Hz, N_z ∈ {10, 100} Zyklen, Jitter von Modul 2 und 3 je Zyklus σ_t ∈ {0, 56 µs} (= 0,2°), Punkte 100°,
116°, 120°; je Einstellung 300 Läufe. Verfahren A (registriert) mit k_max = 3/6/9/ohne, Verfahren B (Rohminimum je Zyklus,
gemittelt). Wahrheit: rauschfreie, jittergedämpfte Erwartungskurve (= Superpositionsvorhersage mit gemessenen ρ).
[A] Rauschbereich 1–20 mN begründet aus dem Bestand: Werkzeug_PCMMFM_PreValidation §6 (elektrisch 1–5 mN, mechanisch 5–30 mN,
Umgebung 3–20 mN, Beispiel σ_total ≈ 24 mN), Anforderungsprofil F1 (Auflösung ≤ 0,005·Mg ≈ 32 mN), Kurzdossier (σ_total ≈ 0,024 N).
Eine gemessene Rauschdichte gibt es nicht.

**Ergebnis [R]** (f_s = 6,4 kHz, N_z = 100, je Lauf; mN):

| Verfahren | 120° (Knick, drei gleiche Minima) | 116° | 100° |
|---|---|---|---|
| A, k_max = 9, σ = 1 / 5 / 20, ohne Jitter: Bias; sd | +0,08 / +0,03 / −0,18; 0,02 / 0,07 / 0,26 | +0,10 / +0,09 / +0,13; 0,02 / 0,09 / 0,34 | +0,08 / +0,08 / +0,10; 0,03 / 0,09 / 0,34 |
| A, k_max = 9, mit 56 µs Jitter | −0,73 … −0,77; 0,53 … 0,56 | +0,08 … +0,10; 0,90 … 1,01 | +0,07 … +0,09; 0,52 … 0,61 |
| A, ohne Bandbegrenzung, σ = 20, ohne/mit Jitter | −3,8 / −4,3; 0,9 / 1,1 | −1,3 / −1,2; 1,4 / 1,9 | −1,6 / −1,7; 1,2 / 1,3 |
| B (Rohminimum je Zyklus), σ = 1 / 5 / 20, ohne Jitter | −2,0 / −10,3 / −41,9 | −0,6 / −4,6 / −21,8 | −0,6 / −6,2 / −32,8 |
| B mit 56 µs Jitter | −12,3 / −18,5 / −46,3 | −1,7 / −5,3 / −22,2 | −0,6 / −6,2 / −32,8 |

- N_z = 10 (T_a = 1 s): sd etwa √10-fach, Bias von A ohne Bandbegrenzung −12,4 mN (σ = 20, 120°), A mit Jitter bei 120° −2,2 bis −2,8 mN.
- f_s = 2 kHz: systematisch +0,5 … +1,1 mN (A, k_max = 9) durch Interpolationsglättung der Knicke; mit 6,4 kHz (A6: f_s ≥ 6,3 kHz)
  ≤ +0,1 mN. Dieser Anteil ist linear und trifft Einzel- und Kombinationsläufe gleich.
- **Verfahren B ist unbrauchbar für konfirmatorische Zwecke:** Bias bis −46 mN = 36 % von Δ(F_min) (k_max = 9) und mittelt sich
  nicht mit N_z oder n weg. Faustformel: Bias ≈ −σ·√(2 ln n_eff) mit n_eff ≈ 4 (100°) bis 9 (120°) konkurrierenden Abtastwerten, nicht
  mit n = Abtastwerte je Zyklus (640; das ergäbe −72 mN bei 20 mN).
- **Verfahren A mit Bandbegrenzung** ist praktisch unverzerrt (|Bias| ≤ 0,2 mN ohne Jitter); der einzige nennenswerte Rest ist der
  Minimum-aus-drei-Effekt am Triphasik-Punkt unter Jitter (−0,75 mN je Lauf bei N_z = 100; s. STA-04).
- P1-Hypothese „Extremwert-Bias ~ −σ·√(2 ln n)“: **für das registrierte Verfahren widerlegt** (Bias um 2–3 Größenordnungen kleiner),
  **für zyklusweise Minima (E4) bestätigt** in der Größenordnung.

**Reproduktion.** `for i in 0 1 2; do eval timeout 540 $PY s1_fmin_rauschen_mc.py $i; done`, danach
`eval $PY -c "import pandas as pd,glob; pd.concat([pd.read_csv(f) for f in sorted(glob.glob('s1_fmin_rauschen_mc_cfg*.csv'))]).to_csv('s1_fmin_rauschen_mc.csv',index=False)"`.

**Einschränkungen.** Weißes Rauschen; Jitter als starre Verschiebung je Zyklus, unabhängig zwischen Zyklen; Modul 1 ohne Jitter
(definiert θ); Segmentierung exakt (f_s/f ganzzahlig, Sub-Sample-Versatz je Lauf zufällig). 1/f-Anteile und langsame Drift wirken
auf k ≥ 1 nur über den Sägezahn Drift·T je Zyklus (bei 1 mN/10 s: 0,01 mN) und sind nicht simuliert.

---

## STA-03 · Erreichbares u_c gegen PB1

**Frage.** Welches u_c ist mit Sensorrauschen, Abtastrate, Zyklenzahl und Jitter ≤ 56 µs erreichbar, gemessen an PB1?

**Methode [R].** Laufstreuung aus s1; Kampagnen-MC s2 mit Bootstrap-u_c (Var_A + Var_B, B = 200), n = n₀ = 20, n₁ = 21.

**Ergebnis.**
- Weißes Sensorrauschen allein: sd(F_min − ⟨N⟩) je Lauf = σ·√(2k_max/(f_s T_a)) ≈ 0,34 mN bei σ = 20 mN, 6,4 kHz, 10 s, k_max = 9
  (MC 0,26–0,34 mN); Jitter 56 µs addiert 0,5–1,0 mN je Lauf (N_z = 100) bzw. 1,5–3 mN (N_z = 10) und dominiert unterhalb σ ≈ 20 mN.
- Kampagne (s2, Stufe L0 „Sensor + Jitter“): **u_c(F_min) = 0,26 mN, u_c(N₂) = 0,12 mN**, ν_eff ≈ 37. Das ist das **≈ 100-Fache
  unter** der notwendigen PB1-Grenze (27–33 mN) und das ≈ 55-Fache unter der Grenze für P(Bestätigung) ≥ 0,8 (14–17 mN).
- Mechanische Lauf-zu-Lauf-Streuung je Modul [A] bestimmt u_c: 0,3 %/0,03° → 0,99 mN; 1 %/0,1° → 3,3 mN;
  3 %/0,3° → 9,8 mN (P(PB1) = 0,96); 6 %/0,6° → 19,6 mN (P(PB1) = 0); 10 %/1° → 32 mN (s. STA-08). PB1 wird also erst bei u_c(F_min) ≈ 10–20 mN
  bindend (Δ_F/u_c ≈ 7–13), in Übereinstimmung mit STA-01.
- Folgerung: **Sensorrauschen begrenzt PB1 nicht.** Bindend sind die mechanische Reproduzierbarkeit (unbekannt, keine Hardware) und
  vor allem systematische Abweichungen (STA-08, STA-11).

**Reproduktion.** s1 (oben); `sh run_s2.sh` bzw. `eval timeout 540 $PY s2_h1_oc_kampagne.py 0 600 20 20 9`.

**Einschränkungen.** u_c aus Bootstrap mit B = 200 statt 10 000 (Varianzschätzung ±10 %); Phase-1-Kontrollläufe n₁ = 21 je Modul
(20 Blöcke); Einzelmodulläufe mit gleichem Restrauschen wie Kombinationsläufe.

---

## STA-04 · Rauschbias-Bedingung (§5.4) am Triphasik-Punkt strukturell verletzbar; Bootstrap am Knick

**Frage.** Ist |b_i| ≤ 0,1·u_c,erw,i(F_min) erfüllbar, wenn F_min das Minimum dreier gleich tiefer Minima ist?

**Methode [R].** `s1b_rauschbias_triphasik.py`, A4-Beispiel, n = 20, n₀ ∈ {20, 40, 60}, R = 4000, drei Rauschmodelle [A]: 'weiss'
(gleiches Restrauschen in Einzel- und Kombinationsläufen), 'modul' (Amplitudenstreuung je bewegtem Modul), 'jitter' (Laufmittel der
Phasen, nur in Kombinationsläufen). Zusätzlich 2000 Kampagnen mit Bootstrap-u (B = 400) am Triphasik-Punkt.

**Ergebnis.**
- Bei 116°–119° ist |b|/u_c,erw ≤ 0,03 in allen Modellen: unkritisch.
- Bei 120°: 'weiss' |b|/u = 0,42 (n₀ = 20), 0,18 (40), 0,01 (60) → erfüllt nur bei n₀ ≈ 3n; 'modul' 0,02 (n₀ = 20), 0,33 (40),
  0,54 (60) → erfüllt nur bei n₀ ≈ n; 'jitter' 1,62 bei jedem n₀, weil die Vorhersage diesen Anteil nicht trägt.
- Weil b und u_c,erw beide ∝ 1/√n skalieren, **hilft mehr Laufzahl nicht**; maßgeblich ist das Verhältnis der Rauschpegel von
  Mess- und Vorhersageseite. Nach §5.4 macht eine verletzte Bedingung das Paar (k, T_a) unzulässig; im Jitter-dominierten Fall
  (σ ≲ 20 mN, s. STA-02) wäre bei identischen Modulen **kein** Paar zulässig → „f unzulässig“, im Extremfall „kein zulässiger
  Arbeitspunkt“, ohne dass ein Messproblem vorliegt. Bei realen Modulunterschieden, die die drei Minima um mehr als einige
  Standardabweichungen trennen, verschwindet der Effekt.
- Bootstrap-z am Triphasik-Punkt (n = n₀ = 20): 'weiss' Mittel +0,37, sd 0,90; 'modul' −0,00, sd 0,88; 'jitter' −1,32, sd 0,66,
  P(|z| > c = 3,95) = 0,0015. Der Bootstrap eines Minimums gleich tiefer Minima ist nicht konsistent (Knick); er überschätzt hier
  die Streuung (sd z < 1) und verschiebt z.

**Reproduktion.** `eval timeout 540 $PY s1b_rauschbias_triphasik.py`

**Einschränkungen.** Exakt identische Module; Rauschstärken so gewählt, dass sd(F_min) eines Laufs ≈ 1 mN (Ergebnis als Quotient
skalierungsfrei). Mischformen der Modelle liegen dazwischen.

---

## STA-05 · H2: Halbbreite von Δφ* und nötige Wiederholungen

**Frage.** Wie viele Läufe je Punkt braucht der Zwei-Geraden-Zeltfit für eine Halbbreite ≤ 1° (L5a-021, §5.4, L5a-044), für die
Simulationssekanten 0,212/0,195 N/° und skaliert (0,5; 0,25; 0,1)?

**Methode [R].** `s3_h2_zeltfit_mc.py`: Formen 'ref' (Referenz-Engine im Kontaktast, mit `data/finesweep_2deg_120_240.csv` auf
φ₃ = 240° bis 2·10⁻⁶ N identisch) × s ∈ {1; 0,5; 0,25; 0,1} und 'A4'; weißes Restrauschen je Lauf (σ_run = sd von F_min − ⟨N⟩ eines
Laufs), n Läufe je Punkt, n₀ = n Einzelmodulläufe je Modul (Vorhersage über alle Punkte korreliert); SNR := s̄·1°/σ_run mit s̄ =
Mittel der 2°-Sekanten (bandbegrenzt k ≤ 9: 0,2118/0,1951 N/° für 'ref', 0,0343 N/° für 'A4'). Fenster nach A9.6, Zeltfit
nach A9.6 (0,02°-Raster, dann 0,001°). Halbbreite = (q97,5 − q2,5)/2 der MC-Verteilung von Δφ* über 1500 Kampagnen.
Kontrolle mit dem registrierten Bootstrap (`s3b_h2_bootstrap_check.py`).

**Ergebnis.**
- Gesetz: **Halbbreite ≈ κ/(SNR·√n) mit κ = 3,0 (Spannweite 2,5–4,5)**, für alle Skalen gleich (das Problem ist skaleninvariant).
  Nötig für ≤ 1°: **n ≈ (3/SNR)²**: SNR 0,5 → 37; 1 → 10; 2 → 3; ≥ 3 → 1–2. Gleichwertig: Punktunsicherheit der
  Konfigurationsmittelkurve σ_run/√n ≤ s̄/3 (0,068 N für 'ref', 0,011 N für 'A4' bandbegrenzt).
- Nur Messseite (wie L5a-021) wäre die Halbbreite etwa halb so groß; L5a-021 (0,34° bei 0,01 N, 0,74° bei 0,027 N, A4 ungefiltert)
  ist damit **bestätigt** in der Größenordnung, mit der Vorhersageseite verdoppelt sie sich.
- Realistisch (σ_run ≈ 0,3–1 mN aus STA-02/03): SNR ≈ 34–700 → H2 ist nicht präzisionsbegrenzt, auch nicht bei Skala 0,1
  (SNR ≈ 20–70). Begrenzend ist die Fensterregel (STA-06).
- Bootstrap-Kontrolle (s3b, 150 Kampagnen, B = 400, SNR = 1, n = n₀ = 20): 'ref' (w = 16) MC-Halbbreite 0,645°, mittlere
  Bootstrap-Halbbreite 0,624°, Überdeckung 0,947; 'A4' (w = 6) 0,735° gegen 0,696°, Überdeckung 0,927 (Standardfehler 0,018).
  Das registrierte Perzentil-Bootstrap trifft die Halbbreite auf 3–5 % und ist leicht zu schmal.

**Reproduktion.** `eval timeout 540 $PY s3_h2_zeltfit_mc.py 1500`; `eval timeout 540 $PY s3b_h2_bootstrap_check.py 150 400`

**Einschränkungen.** Weißes Restrauschen; mechanisches Rauschen verändert κ wenig (Vorhersage- und Messseite gleich aufgebaut),
nicht eigens gerechnet. Abszisse = Sollphase (die gemessene Profilphase streut um ≤ 0,02° je Konfiguration).

---

## STA-06 · H2-Fensterregel macht H2 bei hoher Präzision unentscheidbar (neu)

**Frage.** Ist ein Fitfenster W nach §8.6/A9.6 („F̂_min weicht höchstens 0,25·min_i u_c,erw,i von der eigenen Zeltanpassung ab“)
bei realistischer Präzision überhaupt zulässig?

**Methode [R].** s3, Teil 1: größte Abweichung der rauschfreien (bandbegrenzten) Vorhersage von ihrer Zeltanpassung je w.

**Ergebnis.** Kleinste Abweichung (w = 4°, 5 Punkte, 1 Freiheitsgrad): 'ref' 1,0 mN, 'A4' 1,1 mN (Abrundung der Spitze durch die
Bandbegrenzung), skaliert mit s. Ein Fenster existiert nur, wenn u_c,erw ≥ 4 × diese Abweichung ist, also **u_c,erw ≥ 4,0 mN
('ref') bzw. 4,4 mN ('A4')**. Mit n = n₀ und weißem Rauschen heißt das σ_run ≥ 2·m₄·√n, für 'A4' und n = 20 **σ_run ≥ 9,8 mN**,
d. h. SNR ≤ 3,5. Im MC fehlt das Fenster entsprechend bei 'A4' für SNR = 4 (n = 20, 40) und SNR = 8 (alle n). Bei der in STA-03
erreichbaren Präzision (u_c,erw ≈ 0,3–1 mN) ist **H2 nach der registrierten Regel „nicht entscheidbar“**, obwohl die Halbbreite
weit unter 1° läge. Die Regel bindet das Fenster an die Messunsicherheit statt an den Fehler der Spitzenlage; der Formfehler des
Zelts hebt sich aber in Δφ* auf, weil derselbe Fit auf Messung und Vorhersage angewandt wird (STA-07).

**Reproduktion.** wie STA-05 (Abschnitt 1 der Ausgabe und Zeilen ohne w in `s3_h2_zeltfit_mc.csv`).

**Einschränkungen.** Rauschfreie Vorhersage zur Fensterwahl (Teil B nutzt die verrauschte Phase-0-Vorhersage; das ändert die
Schwelle nicht grundsätzlich).

---

## STA-07 · Bias des Zwei-Geraden-Fits bei gekrümmtem Zelt

**Frage.** Wie stark verschiebt die Krümmung der Flanken die geschätzte Spitze?

**Methode [R].** s3, Teil 1 (rauschfrei) und Teil 2 (E[Δφ*] unter Rauschen).

**Ergebnis.**
- Absolut: Referenzzelt (Sekanten 0,229 → 0,212 links, 0,195 → 0,174 N/° rechts) ergibt φ* − 120° = −0,044° (w = 4) bis −0,219° (w = 20);
  die CSV der nichtlinearen Engine gibt dasselbe (−0,044° … −0,212°). A4-Zelt (symmetrisch): 0,000°.
- In Δφ* hebt sich der Formfehler auf: |E[Δφ*]| ≤ 0,05° in allen 100 MC-Fällen (Median |E| ≈ 0,01°), auch bei Skala 0,1 und
  ungleichen Rauschpegeln von Mess- und Vorhersageseite (n₀ = n). Mess- und Vorhersagebias einzeln je −0,05° … −0,3° (Fenster).
- **Folgerung:** Der Fit-Bias ist für H2 unschädlich, solange Messung und Vorhersage dieselbe Form haben; die Fensterregel (STA-06)
  schützt gegen ein Problem, das der Differenzvergleich schon löst.

**Reproduktion.** wie STA-05; `s3_h2_bias.csv`.

---

## STA-08 · Mehrfachtests H1: kontrollierte Fehlerrate und Operating Characteristic

**Frage.** Welche Fehlerrate kontrollieren die 147 Tests mit Bonferroni-c und die Regel „|z⁰| > c und |z¹| > c, gleiches Vorzeichen“
(L5a-018, L5a-068)? Wie verhalten sich P(falsifiziert) und P(bestätigt) bei exakter Superposition und bei Abweichungen?

**Methode.** [Q/analytisch] §8.4, §9.3, A8. [R] `s2_h1_oc_kampagne.py`: je Rauschstufe 600 Kampagnen je Szenario; registrierte
Regel (Bootstrap-u_c, Welch–Satterthwaite-ν, c = t(1 − 0,05/294; ν), Δ_q aus ŷ⁰, PB1 nur mit r⁰) und zwei Vorschläge
(IUT-TOST-Bestätigung; Mindesteffekt-Falsifikation |r| − c·u > Δ_q gegen ŷ⁰ und ŷ¹).

**Ergebnis analytisch.**
- Falsifikationsseite: je Vorhersage Bonferroni über 147 zweiseitige Tests → **FWER ≤ 0,05** je Familie (stark, auch bei
  Abhängigkeit). Die UND-Verknüpfung mit z¹ ist eine Intersection-Union-Verknüpfung; sie senkt die Rate weiter. Holm würde die
  globale Entscheidung „mindestens ein Test verwirft“ nicht ändern (erster Holm-Schritt = Bonferroni), nur die Zuordnung, welche
  Größen abweichen.
- Bestätigungsseite: „alle 147 äquivalent“ ist ein Intersection-Union-Problem; dafür genügt je Test ein TOST auf Niveau α
  (90-%-Intervall, c_eq = t(0,95; ν) = 1,65–1,73). PB1 verlangt (1 − α/147)-Intervalle; die Rate fälschlicher Bestätigung am Rand
  der Äquivalenzzone ist damit je Test **1,7·10⁻⁴ statt 0,05** (s0), also etwa 300-fach konservativer als nötig. Für die gleiche
  Bestätigungswahrscheinlichkeit erlaubt IUT ein ≈ 2,2–2,5-fach größeres u_c.
- „Bestätigt“ verlangt zusätzlich, dass **kein** Test signifikant ist. Das ist eine Nicht-Ablehnung; PB1 liefert zwar eine
  Äquivalenzmarge Δ_q, aber eine signifikante, beliebig kleine Abweichung verhindert die Bestätigung und führt (bei Vorliegen gegen
  ŷ⁰ und ŷ¹) zu „falsifiziert“. Eine Mindestrelevanz der Falsifikation fehlt.

**Ergebnis Simulation (A4-Beispiel, n = n₀ = 20, n₁ = 21, k_max = 9; 600 Kampagnen je Zelle, Zusatzszenarien 20/30 % mit 300).**
Einträge: P(falsifiziert) / P(bestätigt); Rest = „nicht entscheidbar“. Größte Residuen der Szenarien (rauschfrei, s4):
Kopplung 1 % → F_min 12,2 mN, N₃ 5,5 mN; N₂ 1 % → ≤ 2,9 mN in Re/Im N₂; 10 % Kopplung → F_min 120 mN (≈ 0,93·Δ_F).

| Szenario | L0 | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|---|
| Lauf-zu-Lauf-Streuung [A] | Sensor+Jitter | 0,3 %/0,03° | 1 %/0,1° | 3 %/0,3° | 6 %/0,6° | 10 %/1° |
| u_c(F_min) / u_c(N₂) [mN] | 0,26 / 0,12 | 0,99 / 0,51 | 3,3 / 1,7 | 9,8 / 5,1 | 19,6 / 10,1 | 32,3 / 16,9 |
| exakte Superposition | 0,000 / 0,935 | 0,000 / 0,933 | 0,005 / 0,928 | 0,003 / 0,883 | 0,000 / 0,000 | 0,002 / 0,000 |
| Kopplung 1 % | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 0,097 / 0,513 | 0,005 / 0 | 0,000 / 0 |
| Kopplung 3 % | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 0,443 / 0 | 0,057 / 0 |
| Kopplung 10 % | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 0,998 / 0 |
| N₂ 1 % | 1,000 / 0 | 0,997 / 0 | 0,012 / 0,780 | 0,000 / 0,877 | 0,000 / 0 | 0,002 / 0 |
| N₂ 3 % | 1,000 / 0 | 1,000 / 0 | 0,975 / 0 | 0,013 / 0,708 | 0,005 / 0 | 0,000 / 0 |
| N₂ 10 % | 1,000 / 0 | 1,000 / 0 | 1,000 / 0 | 0,998 / 0 | 0,178 / 0 | 0,013 / 0 |
| Drift Phase 0 1 % | 0,017 / 0 | 0,018 / 0 | 0,010 / 0 | 0,005 / 0,682 | 0,002 / 0 | 0,000 / 0 |
| Drift Phase 0 3 % | 0,012 / 0 | 0,015 / 0 | 0,012 / 0 | 0,008 / 0 | 0,005 / 0 | 0,002 / 0 |
| **Vorschlag IUT-TOST:** P(bestätigt) exakt / Kopplung 1 % / Kopplung 10 % | 1 / 1 / 1 | 1 / 1 / 1 | 1 / 1 / 0,39 | 1 / 1 / 0 | 0,24 / 0,24 / 0 | 0 / 0 / 0 |
| **Vorschlag Mindesteffekt:** P(falsifiziert) bei ≤ 10 % / 20 % / 30 % Kopplung | 0 / 1 / 1 | 0 / – / – | 0 / 1 / 1 | 0 / 1 / 1 | 0 / 1 / 1 | 0 / 0,78 / 1 |

- **Typ-I-Fehler:** P(falsifiziert | exakt) = 0–0,005 (0–3 von 600) auf allen Stufen, also eine Größenordnung unter dem Nominalwert
  0,05. Ursachen: Bonferroni bei korrelierten Größen (q95 von max|z⁰| = 3,76–3,95 gegen c = 3,95; P(mindestens ein |z⁰| > c) =
  0,030–0,050) und die UND-Verknüpfung mit z¹ (Korrelation z⁰/z¹ = 0,50–0,58). Die Ersatzregel (§8.4) greift deshalb nie.
- **Bestätigung bei exakter Superposition:** 0,93 auf L0–L2, 0,88 auf L3 (PB1 0,96), **0 ab L4** (u_c(F_min) ≈ 20 mN, Δ_F/u_c ≈ 7):
  PB1 wird zwischen u_c ≈ 10 und 20 mN bindend (vgl. STA-01: 14–17 mN). „Nicht entscheidbar“ bei exakter Superposition auf L0–L2
  ≈ 0,065 (ein einzelnes |z⁰| oder |z¹| > c).

**Reproduktion.** `sh run_s2.sh` (Stufen L0–L5; einzelne Stufe: `eval timeout 540 $PY s2_h1_oc_kampagne.py L 600 20 20 9`),
`sh run_s2_zusatz.sh` (20/30 % Kopplung), Tabelle: `eval $PY s5_oc_tabelle.py` → `s5_oc_tabelle_ausgabe.txt`, `s5_oc_tabelle.csv`.

**Einschränkungen.** Rauschmodell aus weißem Rest plus Modulamplitude/-phase [A]; Abweichungen als multiplikative Faktoren
(gleichmäßige Kopplung bzw. nur k = 2); alle 21 Punkte auswertbar; B = 200; 600 Kampagnen (Standardfehler einer Rate 0,05: 0,009).

---

## STA-09 · Präzisionsparadox der H1-Regel (neu)

**Frage.** Ist „Bestätigung“ eine Nicht-Ablehnung ohne Äquivalenzgrenze? Wie wirkt sie bei realen, kleinen Abweichungen?

**Methode.** [R] s2-Tabelle (STA-08) und s0; [analytisch] Bedingungen von §9.3.

**Ergebnis.**
- „Bestätigt“ verlangt für jeden Test |r| ≤ c·u_c (Nicht-Ablehnung) **und** |r| + c·u_c ≤ Δ_q (PB1). Für eine reale Abweichung δ ist
  Bestätigung nur im Fenster δ ≲ c·u_c ≲ Δ_q − δ möglich. Folge: P(bestätigt) hängt **nicht monoton** von der Präzision ab – bei
  1 % Kopplung 0 / 0 / 0 / **0,51** / 0 / 0 (L0 … L5), bei 1 % N₂-Abweichung 0 / 0 / **0,78** / **0,88** / 0 / 0, bei 1 % Drift
  0 / 0 / 0 / **0,68** / 0 / 0. Eine **präzisere Apparatur kann H1 seltener bestätigen** als eine ungenauere.
- Bei Sensor-limitierter Präzision (L0, u_c(F_min) = 0,26 mN) wird H1 durch jede Abweichung ab etwa 1 mN „falsifiziert“, auch wenn
  alle Intervalle weit innerhalb ±Δ_q liegen (1 % Kopplung: |r| ≤ 12 mN ≪ Δ_F = 129 mN; P(falsifiziert) = 1, P(IUT-äquivalent) = 1).
  §9.4 kennt dafür den Zusatz „Abweichung nachgewiesen, kleiner als ein Viertel der Struktur“, das Label bleibt aber „falsifiziert“.
- Damit ist die Bewertung der P1-Frage: Eine Äquivalenzmarge existiert (PB1, Δ_q = 0,25·D_q) und ist formal ein TOST (auf dem
  Niveau α/294 je Test); die Bestätigung koppelt sie aber an die Nicht-Ablehnung. Es fehlen ein Äquivalenztest **ohne**
  Nicht-Signifikanzbedingung und eine Relevanzgrenze für die Falsifikation. **Teilweise bestätigt** (P1 §7.6).
- Mit den Vorschlägen (IUT-TOST für Bestätigung, Mindesteffekt Δ_q für Falsifikation) wird die OC monoton und interpretierbar:
  Bestätigung 1,00 auf L0–L3 für exakt, 1 % und 3 % Abweichung; Falsifikation 0 für alle Abweichungen < Δ_q und 1,00 (L0–L4) für
  20–30 % Kopplung (|r| ≈ 1,9–2,8·Δ_F).

**Reproduktion.** `sh run_s2.sh`, `sh run_s2_zusatz.sh`, `eval $PY s5_oc_tabelle.py` → `s5_oc_tabelle_ausgabe.txt`.

**Einschränkungen.** Die Vorschläge sind hier nur gegen ŷ⁰ und ŷ¹ mit den Bootstrap-u_c der Simulation gerechnet; eine eigene
Kalibrierung ihrer Fehlerraten (insbesondere der IUT-Bestätigung am Rand der Äquivalenzzone, s0: 0,050) gehört in Werkzeug 8.

---

## STA-10 · Drift der Einzelmodulbasis und Kopplung an PB1

**Frage.** Wie wirkt die Regel „gegen ŷ⁰ und ŷ¹“ bei einer Drift, und wie ist PB1 an die übrigen Bedingungen gekoppelt?

**Methode.** [R] s2-Szenario „drift“ (Phase-0-Einzelmodulantwort um 1 bzw. 3 % größer, Superposition sonst exakt); s4 c).

**Ergebnis.**
- Bei Drift ist z⁰ überall signifikant, die Falsifikation hängt allein an z¹: P(falsifiziert) = 0,010–0,018 (L0–L2), also unter α;
  P(nicht entscheidbar, Zusatz „Drift“) = 0,98–0,99. Die ŷ¹-Logik **funktioniert** wie beabsichtigt.
- PB1 wird nur mit r⁰ gebildet (§8.5). Bei Drift bleibt PB1 erfüllt (P = 1,00 auf L0–L2), die Bestätigung scheitert an |z⁰| > c. Ein
  Drift von 0,1 % (G7-Grenze, 1,2 mN Residuum gegen ŷ⁰) reicht auf L0 schon für z⁰ ≈ 4,7 und damit für „nicht entscheidbar“.
- PB1 teilt den kritischen Wert c (Bonferroni, ggf. Ersatzregel) mit der Signifikanzbedingung: Ein größeres c (kleines ν) erleichtert
  die Nicht-Signifikanz und erschwert PB1. PB1 bindet erst ab u_c(F_min) ≈ 10–20 mN (STA-08); darunter entscheidet allein die
  Signifikanz (STA-09).

**Reproduktion.** wie STA-08; `s4_identifizierbarkeit_rest_ausgabe.txt` Zeilen c).

---

## STA-11 · Identifizierbarkeit: welche Ursachen erzeugen eine H1-Signatur?

**Frage.** Welche Alternativursachen erzeugen dieselbe Signatur wie eine H1-Falsifikation, wie groß, und welche Kontrolle der
Präreg trennt sie?

**Methode.** [analytisch] A2.1 sagt selbst: Für jedes lineare, zeitinvariante (LTI) System gilt die Superposition der gemessenen
Einzelantworten exakt. LTI-Artefakte erzeugen deshalb **keine** H1-Signatur, gleich wie groß sie sind; sie verfälschen nur H3
(Modell) und absolute Größen. Eine H1-Signatur entsteht nur durch (i) Nichtlinearität, (ii) Zeitvarianz zwischen Einzel- und
Kombinationsläufen, (iii) Wechselwirkung der Antriebe, die in Einzelläufen fehlt. [R] `s4_identifizierbarkeit.py` beziffert
Beispiele im A4-Beispiel (k_max = 9, sofern nicht anders angegeben). Nachweisgrenze zum Vergleich (s2; die z-Angaben der Tabelle sind grob: größtes Residuum geteilt durch den Median von u_c): c·u_c ≈ 3,95 × 0,26 =
1,0 mN (F_min) bzw. 0,5 mN (N_k) bei Sensor+Jitter (L0); 13 mN bzw. 6,7 mN bei 1 %/0,1° mechanischer Streuung (L2).
Δ_F = 129 mN, Δ_N2 = 73 mN.

**Ergebnis.**

| Ursache (Annahme) | Art | max \|r\| F_min / N_k [mN] | erkannt bei L0 / L2? | trennende Kontrolle der Präreg |
|---|---|---|---|---|
| Profilabweichung, Modulungleichheit (stationär, in Einzel- und Kombinationslauf gleich) | linear | 0 (exakt) | – | keine nötig; verschiebt nur die H2-Vorhersage (wird vorhergesagt) |
| Übersprechen, Querkraftempfindlichkeit, lineare Kipp-Leckage, Strukturresonanzen, lineare Kabelsteifigkeit | LTI | 0 | – | keine nötig für H1; relevant für H3 (P0.1, P0.3, P0.4) |
| EM-Einstreuung je Antrieb (additiv) | LTI je Antrieb | 0 | – | D2, Blindkanal; Wechselwirkung der Antriebe (gemeinsame Versorgung) wird **nicht** geprüft (D2 nur je Frequenz, nicht in Kombinationskonfiguration) |
| Luftwiderstand je Modul (10 cm², c_w = 1, v ≈ 0,24 m/s) | nichtlinear, aber je Modul | 0,035 je Modul, Wechselwirkungsanteil ≪ 0,04 | nein | keine (fehlt in Tabelle C) |
| Elektrostatik (10 cm², 100 V, 1 mm) / Kabelschlaufe (100 N/m, ≤ 1 µm) | ≈ linear | 0,044 / 0,10 (Gesamtkraft, nicht Residuum) | nein | Kabelschlaufe P0.3; Elektrostatik fehlt in Tabelle C |
| Phasenjitter (über gemessene ρ berücksichtigt) | linear | 0 | – | ρⱼₖ (A2.4) |
| nicht erfasster Jitter Encoder ↔ Masse, σ_u = 0,2° | linear (Dämpfung) | 0,07 / 0,02 | nein | P0.5 (Δδⱼ), sonst keine |
| Zellkennlinie quadratisch, ε_lin = 0,02–0,05 % FS, FS = 10–49 N, Module über den Zellen (A2.5) | nichtlinear | **0 (exakt)** | – | Geometrie wirkt als Kontrolle |
| dieselbe, Module zentral (je 1/3 auf alle Zellen) | nichtlinear | 0,04–0,20 / 0,005–0,12 | knapp nein (z ≈ 0,2–1,0) | P0.1 (Brückensimulator prüft nur Elektronik), Schwelle 0,1·Δ_q ≈ 13 mN |
| Hertz-Kontakt statt linear, f_n0 = 300 Hz, ζ = 0,05 (k_max = 9 zulässig) | nichtlinear | 1,07 (k ≤ 9; 0,51 mit k ≤ 3) / 0,41 (N₃) | knapp ja (z ≈ 4,1 bei c = 3,95) / nein | P0.4 (zwei Amplituden), H3 nur bei Kontaktempfindlichkeit |
| Hertz, f_n0 = 120 Hz (k_max = 6 nach (b)) | nichtlinear | 6,3 (k ≤ 6; 12,3 mit k ≤ 9) / 2,84 (N₃) | ja (z ≈ 24) / nein (F_min z ≈ 1,9, N₃ z ≈ 1,7) | wie oben |
| Hertz, f_n0 = 60 Hz (k_max = 3 nach (b)) | nichtlinear | 19,0 (k ≤ 3; 196 mit k ≤ 6, Resonanz 6f = f_n) / 16,1 (N₃) | ja / ja | wie oben |
| lastabhängige Aktoramplitude (Kopplung), 0,1 % / 1 % | Wechselwirkung | 1,2 / 12,2 (F); 0,55 / 5,5 (N₃) | L0: ja (z ≈ 4,7 bzw. 47); L2: 0,1 % nein, 1 % ja (s2: P(falsifiziert) = 1,00) | **keine**: Modulhub wird in Phase 1 nicht gemessen (Wegkanal misst dann die Einfederung, A9.1) |
| konfigurationsabhängiger Phasenversatz Modul 2 (0,05°, z. B. lastabhängige Übertragungsnachgiebigkeit) | Wechselwirkung | 1,75 / 1,10 (N₁) | ja (z ≈ 9) / nein | Encoder messen den Antrieb, nicht die Masse; P0.5 nur stationär |
| Verstärkungsdrift Phase 0 → Phase 1, 0,1 % (= G7-Grenze) / 0,01 % | Zeitvarianz | 1,2 / 0,12 (nur gegen ŷ⁰) | z⁰ ≈ 4,7 / 0,5 | ŷ¹ fängt sie ab → „nicht entscheidbar, Drift“ statt „falsifiziert“ (s2: P(fals) = 0,010–0,018 bei 1–3 % Drift) |
| Einzelzell-Abheben, Reibung/Gleiten in der kinematischen Lagerung | stark nichtlinear | groß | ja | G6/S2 bzw. keine (Gleiten nur bei Querkraft > μ_R·N_c) |

- Im steifen Aufbau (f_n ≥ 300 Hz) ist der physikalische Kontaktbeitrag mit ≈ 1 mN von derselben Größe wie Kettenartefakte und
  kleine Kopplungen; **H1 ist dort ein Apparaturtest** (bestätigt P1 §3.7). Erst bei f_n ≲ 120 Hz übersteigt der Kontakt die
  übrigen Ursachen deutlich.
- Trennende Kontrollen der Präreg: Drift ← ŷ¹/S3 (konfirmatorisch über den Zusatz „Drift der Einzelmodulbasis“, funktioniert in s2);
  Elektronik-Nichtlinearität ← P0.1 (nur mit Schwelle 0,1·Δ_q); Kontakt-Linearität ← P0.4 (Impuls, Module geparkt); additive
  Antriebsstörungen ← D2/Blindkanal. Es fehlen: Antriebswechselwirkung (D2 in Kombination), Amplitudenmessung der Module in Phase 1,
  Superposition je Zelle als registrierte Prüfung, Skalierung mit Amplitude/Frequenz.
- **Unidentifizierbar** mit dem registrierten Plan bleiben: (1) Kontakt- gegen Ketten-/Zellnichtlinearität unter dynamischer Last
  (beide hängen von der Gesamtkraft ab); (2) Amplitudenkopplung der Antriebe gegen jede Nichtlinearität (Modulhub in Phase 1
  unbeobachtet); (3) lastabhängiger Phasenversatz Encoder ↔ Masse gegen echte Kopplung; (4) Kopplung, die die Phase verschiebt,
  wird von ρ teilweise absorbiert und ist dann gar nicht sichtbar.

**Reproduktion.** `sh run_s4.sh` (Teile `b`, `a:40,60`, `a:120,300`).

**Einschränkungen.** Reiner Hertz-Kontakt ist der ungünstigste Fall (in Reihe mit einer linearen Wägezelle wird die
Nichtlinearität mit dem Nachgiebigkeitsanteil verdünnt; nicht gerechnet). Kopplung und Phasenversatz sind parametrische Annahmen
ohne Mechanismusmodell. Luft-, Kabel- und Elektrostatikwerte sind Abschätzungen mit angenommenen Maßen.

---

## STA-12 · Trennung von Modellabweichung und Messartefakt (L5a-070, P1 §3.7)

**Frage.** Ist die im Exposé genannte Trennung („ob sich diese Steuerung an realer Hardware reproduzierbar von Messartefakten trennen
lässt“, `docs/expose_2026-09.md` Z. 18–19) konfirmatorisch umgesetzt?

**Methode.** [Q] §9.3, §9.4, §5.2, Tabelle C, A9.11; [R] Schwellen gegen Nachweisgrenze aus s2/s4.

**Ergebnis.**
- §9.4 nennt als Deutung einer H1-Falsifikation „Kontakt nichtlinear, Module gekoppelt, Messkette oder Phasenmessung fehlerhaft“ und
  verweist auf eine Ursachenanalyse; es gibt **keine vorregistrierte Zuordnungsregel** von Signaturen zu Ursachen. **Bestätigt (L5a-070).**
- Die Phase-0-Schranken für Messkettenfehler (P0.1 Laststelle/Querkraft/Elektronik, P0.3 Nebenschluss: je ≤ 0,1·Δ_q ≈ 13 mN; G7:
  0,1 % Empfindlichkeit ≈ 1,2 mN Residuum; D2: 1 % der H3-Grenze) liegen bei Sensor-limitierter Präzision **10- bis 50-fach über der
  H1-Nachweisgrenze** c·u_c ≈ 1 mN. Ein Artefakt, das alle Phase-0-Prüfungen besteht, kann H1 also signifikant „falsifizieren“. Die
  Ausschlussschranken sind auf die Äquivalenzgrenze bezogen, die Falsifikation auf die Präzision – diese Asymmetrie verhindert die
  Trennung (neu, quantitativ).
- Konfirmatorisch getrennt wird nur **Drift** (ŷ⁰ gegen ŷ¹): bei 1–3 % Drift der Phase-0-Basis s2 P(falsifiziert) = 0,010–0,018,
  P(nicht entscheidbar) ≈ 0,99.

**Reproduktion.** s2, s4 wie oben.

---

## Änderungsvorschläge für die Präregistrierung v2 (nur Vorschläge, nichts geändert)

1. **A4/A8, PB1-Größenordnung:** als notwendige Bedingung kennzeichnen und die Auslegungsgrenze für P(Bestätigung | exakt) ≥ 0,8
   ergänzen: u_c ≤ Δ/6,75 (ν → ∞) bzw. Δ/8,31 (ν = 19), im Beispiel 17,4 bzw. 14,1 mN statt 32,7 bzw. 26,9 mN; Zahlen mit derselben
   Bandbegrenzung wie die Messung (k_max = 9: Δ(F_min) = 0,1293 N). *Grund:* STA-01.
2. **Bestätigung von H1 als Äquivalenztest nach dem Intersection-Union-Prinzip:** „bestätigt“, wenn alle 147 Intervalle
   r ± t(0,95; ν_eff)·u_c gegen ŷ⁰ **und** ŷ¹ in ±Δ_q liegen (TOST je Test auf α = 0,05, ohne Bonferroni), **ohne** die Bedingung
   „kein |z| > c“. *Grund:* PB1 ist je Test ≈ 300-fach konservativer als nötig (Fehlbestätigung 1,7·10⁻⁴ statt 0,05, s0); die
   Nicht-Signifikanzbedingung macht die Bestätigung bei hoher Präzision unmöglich, sobald irgendeine reale, irrelevante Abweichung
   größer als ≈ c·u_c ist (STA-09: 1 % Kopplung → P(bestätigt) = 0 für u_c(F_min) ≤ 3,3 mN, IUT-Bestätigung = 1,00).
3. **Falsifikation nur bei relevanter Abweichung** (Mindesteffekttest): „falsifiziert“, wenn an einem Test |r| − c·u_c > Δ_rel gegen
   ŷ⁰ und ŷ¹ mit gleichem Vorzeichen, Δ_rel = Δ_q (oder eigene, physikalisch begründete Relevanzgrenze). Signifikante Abweichungen
   unter Δ_rel als eigener, beschreibender Ausgang „Abweichung nachgewiesen, < Δ_rel“ (bisher als Zusatz in §9.4, aber unter dem
   Label „falsifiziert“). *Grund:* STA-08/09/11: bei u_c(F_min) = 0,26 mN „falsifizieren“ 0,1 % Aktorkopplung (1,2 mN), 0,05°
   lastabhängiger Phasenversatz (1,7 mN) oder Hertz-Kontakt bei f_n = 300 Hz (1,1 mN) H1 – Ursachen, die die Präreg selbst als
   Apparaturfehler einordnet. Zusammen mit Vorschlag 2 schließen sich „äquivalent“ (|r| + t₀,₉₅·u ≤ Δ_q) und „relevant abweichend“
   (|r| − c·u > Δ_q) gegenseitig aus; alles dazwischen ist „nicht entscheidbar“.
4. **Kritischer Wert aus der gemeinsamen Nullverteilung** (Studentisiertes max|z| über die 147 korrelierten Tests aus der
   Kalibriersimulation oder einem Bootstrap unter H0) und in beide Richtungen anwenden; die Ersatzregel (§8.4) greift bisher nur,
   wenn Bonferroni zu liberal ist. *Grund:* s2: q95(max|z⁰|) = 3,76–3,95 ≤ c = 3,95; tatsächliche Rate falscher Falsifikation
   ≤ 0,005 statt nominal 0,05 (UND-Verknüpfung mit z¹). Kleiner Gewinn, gegenüber 2./3. nachrangig.
5. **PB1 (bzw. Vorschlag 2) auch gegen ŷ¹**, nicht nur gegen ŷ⁰. *Grund:* Eine Drift der Phase-0-Basis, die ŷ¹ abfängt, soll nicht
   über die Präzisionsbedingung entscheiden; die Logik „gegen beide“ der Falsifikation gilt dann symmetrisch.
6. **F_min-Schätzer festschreiben und am Triphasik-Punkt entschärfen:** zyklusweise Minima (E4) ausdrücklich nicht konfirmatorisch
   (Bias bis −46 mN = 36 % von Δ); Bandbegrenzung verpflichtend (ohne: −4 mN bei 20 mN Rauschen); am Triphasik-Punkt, wo drei gleich
   tiefe Minima konkurrieren, F_min durch eine glatte Größe ersetzen oder ergänzen (Wert der gemessenen Kurve an den
   Minimumsstellen der Vorhersage, Mittel der drei lokalen Minima oder Soft-Min) oder den Bias per parametrischem Bootstrap
   korrigieren. *Grund:* STA-02, STA-04 (Bootstrap am Knick inkonsistent; z-Verschiebung bis −1,3).
7. **Rauschbias-Bedingung (§5.4) umformulieren:** b und u_c,erw skalieren beide mit 1/√n, das Verhältnis hängt nur vom Verhältnis
   der Rauschpegel ab (weiß: n₀ ≈ 3n nötig; modulproportional: n₀ ≈ n; Jitteranteil: für kein n₀ erfüllbar, |b|/u = 1,6). Statt
   eines harten Zulässigkeitskriteriums: Bias simulieren, korrigieren und als Unsicherheitsbeitrag führen; Planungssimulation mit
   getrennten Rauschmodellen für Einzel- und Kombinationsläufe. *Grund:* STA-04; sonst „f unzulässig“ ohne Messproblem.
8. **H2-Fensterregel entkoppeln:** Kriterium nicht „Abweichung ≤ 0,25·u_c,erw“, sondern Spitzenfehler (z. B. |φ*-Verschiebung durch
   den Formfehler, an der Vorhersage gerechnet| ≤ 0,1°) oder festes Fenster ±6° … ±8°. *Grund:* STA-06: mit der registrierten Regel
   gibt es kein Fenster, sobald u_c,erw < 4,0–4,4 mN; im A4-Beispiel schon bei σ_run < 9,8 mN (n = 20) → H2 nicht entscheidbar,
   obwohl die Halbbreite ≪ 1° wäre; der Formfehler hebt sich in Δφ* auf (|E[Δφ*]| ≤ 0,05°, STA-07).
9. **H2-Laufzahl explizit:** Halbbreite ≈ 3/(SNR·√n), SNR = s̄·1°/σ_run (n₀ = n) → n ≥ (3/SNR)²; SNR in Teil B berichten.
   Bootstrap-Perzentilintervall ist bei n = 20 leicht zu schmal (Überdeckung 0,927–0,947, s3b); Überdeckung in der
   Kalibriersimulation prüfen (A9.11 sieht das vor) und ggf. studentisiertes oder BCa-Intervall. *Grund:* STA-05.
10. **Phase-0- und Gültigkeitsschwellen an die Nachweisgrenze koppeln:** P0.1/P0.3 (≤ 0,1·Δ_q ≈ 13 mN), G7 (0,1 %
    Empfindlichkeit ≈ 1,2 mN Residuum) und das D2-Kriterium auf ≤ 0,3·u_c,erw (bzw. ≤ 0,1·c·u_c,erw) beziehen. *Grund:* STA-12;
    sonst kann ein Artefakt unterhalb aller Phase-0-Schranken H1 signifikant „falsifizieren“.
11. **Identifizierbarkeit konfirmatorisch machen** (vorregistrierte Zuordnungsregeln, mindestens als sekundäre Hypothesen):
    (a) Schnitt bei einer zweiten Frequenz oder Amplitude: Residuum ∝ Amplitude² bei quadratischer Nichtlinearität, ∝ Amplitude bei
    lastproportionaler Kopplung, unabhängig bei Drift; (b) Superposition je Zelle (bei Modulen über den Zellen ist die
    Zellkennlinie exakt wirkungslos, s4); (c) Modulhub in Phase 1 mitmessen (zweiter Wegkanal oder Hubsensor je Modul), damit
    Amplitudenkopplung von Kontakt- und Kettennichtlinearität trennbar ist; (d) D2 auch in Kombinationskonfigurationen
    (Antriebe gemeinsam, Massen abgekoppelt) gegen Antriebswechselwirkung (gemeinsame Versorgung); (e) Paarläufe (zwei Module) zur
    Lokalisierung einer Kopplung; (f) P0.4 zusätzlich unter Betriebslast (Module laufend). *Grund:* STA-11, STA-12.
12. **Tabelle C ergänzen:** Luftkräfte, Elektrostatik, Kabelkräfte mit Größenordnung (≤ 0,04–0,1 mN) und dem Hinweis, dass
    LTI-Anteile keine H1-Signatur erzeugen (A2.1); eigene Zeilen für lastabhängige Amplituden-/Phasenkopplung der Antriebe und
    gemeinsame Versorgung. *Grund:* STA-11.

## Offene Punkte

- Alle Zahlen zu u_c, OC und Laufzahl sind bedingt auf angenommene Rauschmodelle [A]; es gibt weder Hardware noch gemessene
  Rauschdichten oder Lauf-zu-Lauf-Streuungen. Erst die Pilotläufe (P0.10) liefern die Eingangsgrößen; Werkzeug 8 muss die hier
  gezeigten Effekte (Präzisionsparadox, Rauschbias am Knick, Fensterregel) mit den echten Kovarianzen wiederholen.
- Bootstrap mit B = 200 (s2) bzw. 400 (s1b, s3b) statt 10 000; 600 bzw. 300 Kampagnen je Szenario (Standardfehler 0,009 bei 0,05).
- Ungleiche Module wurden für H1 nicht simuliert; sie entschärfen den Minimum-aus-drei-Effekt am Triphasik-Punkt, verschieben aber
  die H2-Spitze (wird vorhergesagt).
- Hertz-Kontakt nur rein (ungünstigster Fall); Reihe mit linearer Wägezelle (Verdünnung) und andere Kontaktgesetze nicht gerechnet.
- Aktorkopplung und lastabhängiger Phasenversatz nur parametrisch; ein Mechanismusmodell (gemeinsame Versorgung, Servo-Steifigkeit,
  Nockenelastizität) fehlt, bis der Antrieb festgelegt ist.
- H3 (PB3) und H4 wurden statistisch nicht nachgerechnet (nicht Teil des Auftrags); A8 gibt für H4 an der Schwelle 0,93 je Punkt und
  0,20 für 23 Punkte an.
- 1/f-Rauschen, Drift innerhalb eines Laufs und Kanalversatz sind nur analytisch abgeschätzt.
- Die Fehlerrate der vorgeschlagenen IUT-Bestätigung am Rand der Äquivalenzzone ist für einen Test geprüft (0,050), nicht für die
  korrelierten 147 Tests mit geschätzten Δ_q.
