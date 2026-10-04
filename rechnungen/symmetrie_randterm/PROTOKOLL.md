# P2 · Prüfgruppe „symmetrie_randterm“ · Protokoll

> **Vermerk zur Übernahme (04.10.2026).** Protokoll aus der Gesamtprojektanalyse 10/2026, Stand 02.10.2026, unverändert bis auf Pfade und Quellenangaben. Geprüft wurde der Repository-Stand `cd7be6a` (28.09.2026) mit der Präregistrierung v2 vom 25./28.09.2026; die späteren Änderungen aus PR #13 und PR #14 (unter anderem Präregistrierung v2 mit Arbeitsfestlegungen, `code/auslegung.py`, `code/ereignisloeser.py`) sind nicht eingearbeitet. Alle Zahlen sind Simulation oder Analytik, keine Messdaten. Verweise wie „L1a-019“, „P1 §3“ oder „B01–B14“ zeigen auf Arbeitsdokumente der Analyse, die nicht im Repository liegen. Quellen außerhalb des Repositorys sind als „(lokaler Bestand, nicht im Repository)“ gekennzeichnet. Startbefehle und Grenzen je Gruppe: [`rechnungen/README.md`](../README.md).

Stand 02.10.2026. Teil A: Symmetrien der Phasenebene. Teil B: Randterm und Fensterbilanz.

**Kennzeichnung.**
- Ohne Zusatz: eigene Rechnung in diesem Ordner.
- „Quelle“: Angabe aus dem Bestand mit Fundstelle.
- „Annahme“: nicht geprüft.

Repo-Code wurde nicht verändert. `finesweep.py` und `pcmms_v3a_phasen_sweep.py` wurden nur importiert.

**Vorspann für alle Reproduktionsbefehle:**

```
cd rechnungen/symmetrie_randterm
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../../code
```

**Konventionen.**
- Modul j läuft mit q(t − τ_j), τ_j = φ_j/(360°·f).
- N_k = (2/T_w)∫N(t)e^{−ikωt}dt, mit absolutem Zeitbezug.
- Fenster W1 = 5–15 s (wie die Engine), W2 = 50–60 s.

## 0 Werkzeuge

| Datei | Zweck |
|---|---|
| `sr_engine.py` | Prüf-Engine, über Punkte vektorisiert. Arithmetik wie `finesweep.run`: RK4, Kontaktkraft aus Stufe 1, t = t0 + i·Δt. Frei wählbar sind Startzeit t0, Anfangszustand, Δt sowie K und C. Zyklusweise sammelt sie: Linksrechteck-, RK4-gewichtete und Trapezsummen, F², F³, min, max, λ, DFT k = 1…9, Zustand und v_S an jedem Zyklusbeginn. Optional protokolliert sie Aufsetzer (θ, w_RK4, Folgekraft). Ein zeitasymmetrisches Testprofil „skew“ dient nur Teil A. |
| `s0_validierung.py` | Abgleich mit `finesweep.run`: F_min, F_max und λ bitgleich, F_mean und Schiefe ≤ 1e-11. Abgleich mit `sweep_19x19.csv`: gleich an liftoffarmen Punkten. Bei (0,0) weicht die skalare Engine wie bekannt ab (6,376417 gegen 6,376243 N). |
| `s5_randterm_skalar.py`, `s9_archiv_zerlegung.py` | Skalare Referenz-Engine `pcmms_v3a_phasen_sweep.rhs`, unverändert. Mit ihr sind Tab. 9.3 und das Archiv gerechnet. |

---

## SYM-01 Exakte Äquivalenzen: Gruppe S₃ (Modulpermutation + Zeitverschiebung)

**Frage.** Welche Abbildungen von (φ₂, φ₃) lassen die stationären Observablen exakt unverändert, auch bei zeitasymmetrischem Profil? Gibt es Regeln für arg N_k?

**Herleitung (analytisch).**
- Die Anregung ist ā(t) = [q̈(t) + q̈(t−τ₂) + q̈(t−τ₃)]/3. Sie hängt nur von der Phasenmenge {0, φ₂, φ₃} ab.
- Eine Umbenennung, bei der Modul j zur Referenz wird, ergibt ā_B(t) = ā_A(t + τ_j).
- Das System ist zeitinvariant: K, C, M und g hängen nicht von t ab. Deshalb ist jeder stationäre Zustand von B die zeitverschobene Kopie eines Zustands von A. Das gilt für jedes Profil und auch mit Liftoff.
- Daraus folgen sechs Abbildungen mod 360°:

| Element | Abbildung | φ_ref (Zeitverschiebung τ_ref) |
|---|---|---|
| id | (φ₂, φ₃) | 0 |
| (23) | (φ₃, φ₂) | 0 |
| (12) | (−φ₂, φ₃−φ₂) | φ₂ |
| (123) | (φ₃−φ₂, −φ₂) | φ₂ |
| (13) | (φ₂−φ₃, −φ₃) | φ₃ |
| (132) | (−φ₃, φ₂−φ₃) | φ₃ |

- **Invariant:** ⟨N⟩, Schiefe γ₁, λ, F_min, F_max, A, |N_k|, alle Momente und das ganze Histogramm von N.
- **Gleichwertige Kennzeichnung:** die zyklische Folge der Phasenabstände bis auf Rotation (so in Präreg A7).
- **Bahngrößen:**
  - 1 nur für (0,0);
  - 2 für (120°,240°)/(240°,120°);
  - 3, wenn zwei Phasen zusammenfallen;
  - sonst 6.
- **Gleichschenklige Abstandsfolgen** wie (40,160,160) verkleinern die Bahn nicht. Sie sind aber spiegelinvariant (SYM-02).
- **Harmonischenphasen:** Unter einem Element mit neuer Referenz j gilt arg N_k(gA) = arg N_k(A) + k·φ_j (mod 360°); unter (23) bleibt arg N_k unverändert. Diese Regel ist exakt, auch nichtlinear, weil sie nur aus der Zeitverschiebung folgt. Invariant sind |N_k| und jede Kombination mit Gesamtordnung null, z. B. die Triadenphase arg(N₁²N₂*). Mit der umgekehrten DFT-Vorzeichenkonvention kehrt sich das Vorzeichen von k·φ_j um.

**Numerische Bestätigung.**
- max|ā_gA(t) − ā_A(t+τ_ref)| = 6,0·10⁻¹⁴ m/s². Geprüft an 20 Zufallspunkten × 6 Elementen, Beschleunigungsskala 11,7 m/s².
- Die Gruppe ist abgeschlossen (6 → 6 Bilder).
- Lineares Modell an (110°, 234°): Phasenregel auf ≤ 1,2·10⁻¹³°, |N_k| auf ≤ 4,4·10⁻¹⁵ N. Die Triadenphase ist in allen 6 Bildern +62,3723°.
- Engine-Prüfung: SYM-04.

**Reproduktion.** `timeout 540 python3 s3_analytik.py` → `s3_analytik_ausgabe.txt` (Abschnitte A und D)

**Einschränkungen.**
- Vorausgesetzt sind identische Module (Masse, Profil, Kopplungspfad) und ein masseloser starrer Rahmen.
- Bei Mehrstabilität gilt die Aussage je Attraktor. Der äquivalente Punkt muss äquivalent gestartet werden (SYM-04).

---

## SYM-02 Spiegelung φ → −φ

**Frage.** Ist (φ₂, φ₃) → (−φ₂, −φ₃) eine zusätzliche Symmetrie? Für welche Observablen gilt sie, und wie verhält sich das Egg-Profil mit THOLD = 0,65?

**Herleitung.**
- Die Spiegelung kehrt die zyklische Abstandsfolge um, die Menge der Abstände bleibt.
- Für ein Profil, das um t₀ zeitumkehrsymmetrisch ist, gilt ā_{A*}(t) = ā_A(2t₀' − t). Die gespiegelte Konfiguration erhält also die zeitumgekehrte Anregung.
- Daraus folgt eine Symmetrie der Antwort nur, wenn auch die Dynamik zeitumkehrbar ist: starre Auflage ohne Abheben (N = Mg + Mā) oder eine lineare Auflage ohne Dämpfung (C = 0, H_k reell).
- Mit Dämpfung oder Liftoff gibt es keine Zeitumkehrsymmetrie, denn Attraktoren sind dissipativ.
- Im Kontaktast gilt für jedes Profil und jede lineare Auflage N_k(A*) = (M/3)H_kP_kΦ_k*. Damit sind |N_k|, ⟨N⟩ und die Varianz spiegelinvariant.
- Für die Phasen gilt arg N_k(A*) = 2arg(H_kP_k) − arg N_k(A). Die Triadenphase wird an 2θ_H gespiegelt, mit θ_H = arg(H₁²H₂*) = +82,2° bei der Referenz. Am Punkt (110°,234°) wird so aus +62,37° der Wert +102,03°.

**Ergebnis.**
- **Egg-Profil:** zeitumkehrsymmetrisch um t₀ = 0,325 T, max|a(t₀+s) − a(t₀−s)| = 3,3·10⁻¹⁴ m/s². Die Phasen der P_k relativ zur Achse sind 0° oder 180°, die Profiltriade 0°. Das bestätigt AP v2.4 Z. 1818 und FV v2.7 Abschn. refprofil. Die „Asymmetrie“ des Egg ist eine Halbwellen-/Amplitudenasymmetrie, keine Zeitasymmetrie.
- **Lineares Modell im Kontaktast, Spiegelpaare:**

| Fall | Egg, Referenz K=10⁴, C=16 | Egg, C = 0 | Egg, starr | Testprofil „skew“ (Triade 55,6°), starr |
|---|---|---|---|---|
| (110,234): γ₁ A/A* | −0,180/−0,262 | −0,0197/−0,0197 | −0,599/−0,599 | +0,178/+0,055 |
| (100,240): γ₁ A/A* | −0,344/+0,050 | gleich | gleich | −0,207/+0,207 |
| (100,240): F_min A/A* [N] | 0,768/1,618 | gleich | 3,375/3,375 | 2,542/3,207 |
| max Δ\|N_k\| | ≤ 3,6·10⁻¹⁵ N | ≤ 2,5·10⁻¹⁴ | ≤ 1,6·10⁻¹⁵ | ≤ 2,7·10⁻¹⁵ |

- **Engine, 60-s-Läufe, Fenster 50–60 s:**
  - K1 (110,234): γ₁ −0,1802 gegen −0,2620, F_min 3,990 gegen 3,690 N; |N₁…N₆| gleich auf 4 Stellen.
  - L1 (157,3; 264): λ 12,40 gegen 8,95 %, γ₁ −0,169 gegen +0,083.
  - L2: λ 18,20 gegen 24,40 %.
  - L3: λ 28,85 gegen 21,25 %.
  - Mit Liftoff unterscheiden sich auch die |N_k| (L3: |N₂| 7,23 gegen 1,02 N).
- **Zeltkurve:** Auf dem Schnitt φ₃ = 240° bildet die Spiegelung (φ₂, 240°) auf (240°−φ₂, 240°) ab, also auf die Spiegelung um φ₂ = 120°.
  - Referenz: Steigung 0,2246 N/° (120°→110°) gegen 0,1916 N/° (120°→130°); max|F_min(120+d) − F_min(120−d)| = 0,85 N für d ≤ 20°.
  - C = 0: 1,8·10⁻⁶ N bei 16 000 Stützstellen je Periode.
  - Starr: 2,7·10⁻⁴ N; der Rest ist Abtastung am Knick und fällt mit feinerer Abtastung (5·10⁻³ → 2,7·10⁻⁴ N).
  - Die Asymmetrie der Zeltkurve (Quelle FV v2.7 Z. 842: 0,23/0,19 N/°; P1: 0,228/0,186) ist damit genau die Brechung der Spiegelung durch die komplexe Kontaktübertragung.
- **Bewertung:**
  - Die Spiegelung ist keine Symmetrie der Referenz.
  - Exakt gilt sie nur für ⟨N⟩ und, im Kontaktast, für |N_k| und die Varianz.
  - Für γ₁, F_min, F_max, λ und arg N_k gilt sie nur, wenn ein zeitumkehrsymmetrisches Profil und eine verlustfreie bzw. starre Auflage ohne Abheben zusammenkommen.

**Reproduktion.**
- `timeout 540 python3 s3_analytik.py` (Abschnitte C, D, E)
- Engine: `timeout 540 python3 s2_symmetrie_laeufe.py std` und `python3 s4_symmetrie_auswertung.py`, letzter Tabellenblock

**Einschränkungen.**
- Lineares Modell nur im Kontaktast. Die C=0-Fälle verlassen ihn (F_min < 0); dort dienen sie nur als algebraische Probe.
- Das Testprofil „skew“ ist synthetisch: q = 3,6 mm·sin ωt + 1,2 mm·sin(2ωt + 0,6).

---

## SYM-03 „Zyklische Vertauschung (φ₂ + 120°, φ₃ + 120°)“

**Frage.** Quellen L4-036 (Forschungslinie S. 7 §4), L7-019 (Auswertung v3a S. 2 §3) und L6a-063 (Patent X §5.2): Ist das eine Invarianz bzw. ein Selbsttest? Wann gilt sie zufällig?

**Analytisch.**
- Die Abbildung ändert die Phasenmenge: {0, φ₂, φ₃} → {0, φ₂+120°, φ₃+120°}. Das ist in der Regel keine Umbenennung.
- Im Kontaktast gilt |Φ_k(φ+120°)| = |Φ_k(φ)| nur für k ≡ 0 mod 3, weil e^{−ik·120°} = 1. Beispiel (0,0)→(120,120): |Φ₁| = 3 → √3 = 1,732, Verhältnis 0,577 für k = 1, 2, 4, 5, 7, 8. Bei (110,234) liegen die Verhältnisse für k = 1 und 2 bei 10,8 und 6,2.
- Eine Äquivalenz liegt nur vor, wenn die Abbildung an einem Punkt mit einem S₃-Element zusammenfällt. Die Lösung der sechs Gleichungssysteme ergibt genau sechs Punkte, Brute-Force-Kontrolle auf dem 0,5°-Raster: 6 Treffer:
  - (40°,200°) und (200°,40°), Abstände {40,160,160};
  - (80°,160°) und (160°,80°), Abstände {80,80,200};
  - (280°,320°) und (320°,280°), Abstände {40,40,280}.
- Diese Punkte werden durch (123) bzw. (132) realisiert.
- Der Fehler der Quellen verwechselt die zyklische Umbenennung 1→2→3→1 mit einer Phasenverschiebung. Richtig ist (φ₂, φ₃) → (φ₃−φ₂, −φ₂): eine Drehung der Ordnung 3 um die Fixpunkte (0,0), (120,240) und (240,120), keine Translation.
- Auf dem 19er-Raster (Schritt 18,947°) war die behauptete 120°-Verschiebung gar nicht prüfbar, denn 120°/18,947° = 6,33 ist kein Rastervielfaches.

**Numerisch (Engine, Standardstart, 60 s, Fenster 50–60 s).**
- K1: λ 0 → 75,50 %, |N₁| 0,644 → 11,99 N, F_min 3,990 → 0 N.
- K2: λ 0 → 75,68 %.
- K3: λ 0 → 75,42 %.
- L1: λ 12,40 → 75,91 %.
- L5: λ 75,61 → 0 %.
- Z1 (40,200) gegen (160,320): λ 27,023 gegen 26,975 %, γ₁ 0,32124 gegen 0,32132. Das liegt in der Abweichung äquivalenter Punkte bei Standardstart (SYM-04).
- Z2 (80,160) gegen (200,280): λ 20,800 gegen 20,800 %, γ₁ 0,61971 gegen 0,61969.

**Scheinbare Gültigkeit in Heatmaps.**
- 142 von 361 Punkten (39,3 %) der 19×19-Karte liegen im gesättigten Hüpfband λ = 74–77 % mit γ₁ = 1,658…1,720.
- Wo Bild und Urbild beide in diesem Band liegen, sieht die Karte invariant aus. Das trifft die meisten Bilder aus SYM-04: λ 75,4–76,2 %, γ₁ 1,68–1,72.

**Bewertung.** L4-036, L7-019 und L6a-063 sind **bestätigt**: Die 120°-Verschiebung ist keine Symmetrie und taugt nicht als Selbsttest. Sie gilt
- exakt an sechs Ausnahmepunkten,
- im Kontaktast für |N_{3j}|,
- näherungsweise im gesättigten Hüpfbereich.

**Reproduktion.**
- `timeout 540 python3 s3_analytik.py` (Abschnitt B)
- `timeout 540 python3 s2_symmetrie_laeufe.py std`, dann `python3 s4_symmetrie_auswertung.py`

**Einschränkungen.** Die Brute-Force-Kontrolle ist rasterbasiert. Die analytische Lösung schließt weitere Punkte aus.

---

## SYM-04 Numerische Verifikation der Äquivalenzen und Startabhängigkeit (11 Basispunkte × 6 Bilder)

**Methode.**
- Basispunkte:
  - liftoff-frei: K1 (110,234), K2 (128,246), K3 (114,252);
  - mit Liftoff, generisch, aus `s1_kandidaten.py`: L1 (157,3; 264,0) λ 12 %, L2 (198,2; 267,4) 18 %, L3 (204,4; 250,8) 29 %, L4 (330,6; 242,9) 44 %, L5 (98,1; 333,7) 76 %, L6 (307,5; 279,9) 72 %;
  - Ausnahmepunkte Z1 (40,200), Z2 (80,160).
- Je Basispunkt laufen die 6 S₃-Bilder über 600 Perioden (60 s).
- Modus **shift**: äquivalenter Start mit Standardzustand bei t0 = −τ_ref, sodass Bild B die exakte Zeitkopie von A ist.
- Modus **std**: alle Läufe mit Standardstart t0 = 0, wie Engine und Archiv.

**Ergebnis.** Angegeben ist die größte Abweichung der 6 Bilder vom Basispunkt. Ein zweiter Lauf mit der endgültigen `sr_engine.py` (mit Aufsetzer-Protokoll) ergab eine bitgleiche Ausgabe.

| Gruppe | Modus | \|ΔF_mean\| | \|ΔN_RK4\| | \|Δγ₁\| | \|Δλ\| | \|ΔF_max\| | Phasenregel |
|---|---|---|---|---|---|---|---|
| K1–K3, L1–L3, Z1–Z2 | shift (W1 und W2) | ≤ 3·10⁻¹⁴ N | ≤ 2·10⁻¹⁴ N | ≤ 1,3·10⁻¹² | 0 | ≤ 5·10⁻¹² N | ≤ 2,4·10⁻¹⁰ ° |
| L4, L5, L6 (aperiodisch/P3) | shift | ≤ 3,9·10⁻⁴ N | ≤ 2,1·10⁻⁴ N | ≤ 1,5·10⁻⁴ | ≤ 0,006 %-Pkt | ≤ 0,014 N | ≤ 0,16 ° |
| K1–K3 (Kontaktast) | std (W1 = W2) | ≤ 5,6·10⁻⁷ N | ≤ 5,6·10⁻⁷ N | ≤ 8·10⁻⁷ | 0 | ≤ 2·10⁻⁵ N | ≤ 6·10⁻⁴ ° |
| L1–L3, Z1, Z2 (periodisch) | std (W1 = W2) | ≤ 6,5·10⁻⁴ N (102 ppm) | ≤ 5,6·10⁻⁷ N | ≤ 3,6·10⁻⁴ | ≤ 0,05 %-Pkt | ≤ 1,2·10⁻³ N | ≤ 0,22 ° |
| L4, L5, L6 | std | bis 0,038 N | bis 0,038 N | bis 0,99 | bis 52 %-Pkt | bis 17,6 N | – |

**Deutung.**
- **Äquivalenzen:** Bei äquivalentem Start sind sie auf Maschinengenauigkeit erfüllt. Ausnahme sind aperiodische Zustände; dort verstärkt sich die Rundung, der Attraktor bleibt aber derselbe.
- **Standardstart:** Er ist nicht zeitverschiebungsinvariant. Daraus entstehen drei verschiedene Abweichungen:
  1. **Gitterphase.** τ_ref ist kein Vielfaches von Δt. Die Abtastung trifft die Wellenform an anderer Stelle (F_min/F_max ≤ 2·10⁻⁵ N), und der Simpson-Defekt E verschiebt sich (≤ 5,6·10⁻⁷ N).
  2. **Quadraturrest Q.** Er hängt von der Lage der Aufsetzer im Zeitschritt ab. Äquivalente Punkte unterscheiden sich deshalb in F_mean um bis zu 102 ppm. Das RK4-gewichtete Mittel stimmt dagegen auf 5,6·10⁻⁷ N überein. Das ist ein direkter Beleg, dass Q ein Auswerteartefakt ist (RT-03).
  3. **Mehrstabilität.**
     - L4: 4 Bilder bei λ 43,84 %, 2 Bilder bei 75,80 %.
     - L5: 4 bei 75,61 %, 2 bei 23,50 %.
     - L6: 2 im Quasi-P3-Zustand bei 71,58 %, 4 bei 76,18 %.
     - Das Muster ist in W1 und W2 gleich, also kein Einschwingrest.
     - Bei äquivalentem Start erreichen alle Bilder denselben Zustand.
- Das bestätigt den P1-Hinweis (L7-019) und den Befund ENG-08 der Gruppe engine: Verletzungen der Umbenennungssymmetrie in der Karte entstehen durch die Startphase in Verbindung mit Mehrstabilität, nicht durch einen Modellfehler.
- Datenprüfung der Karten (`s3_analytik.py`, Abschnitt F):
  - 19×19, volle S₃-Gruppe: 72 Punkte mit |Δγ₁| > 10⁻³, 60 mit |Δλ| > 0,1 %-Pkt, 91 mit |ΔF_max| > 0,01 N, 0 mit |ΔF_min| > 10⁻³ N.
  - Die 12 liftoff-freien Punkte bilden 2 S₃-Bahnen zu je 6, mit Spannweite F_min ≤ 2,7·10⁻⁴ N. Damit erklären sich die „zwei Wertepaare“ in AP Tab. liftoff-frei.
  - Feinsweep: 662 Paare (Punkt, S₃-Bild) im Fenster, max |Δγ₁| 2·10⁻⁶, |ΔF_min| 3,1·10⁻⁵ N.
- Die P1-Zahl „30 von 361“ hängt von Generator und Toleranz ab; Nachweis bei der Gruppe engine (ENG-07).

**Reproduktion.**
- `timeout 540 python3 s1_kandidaten.py`
- `timeout 540 python3 s2_symmetrie_laeufe.py std`, `timeout 540 python3 s2_symmetrie_laeufe.py shift` (je 2,5–6 min, je nach Last)
- `python3 s4_symmetrie_auswertung.py` → `s4_symmetrie_auswertung_ausgabe.txt`

**Einschränkungen.**
- Fester Schritt Δt = 50 µs.
- Für L4–L6 ist nicht geklärt, ob sie chaotisch sind oder sehr lang einschwingen; Floquet-Analyse siehe Gruppe engine.
- λ ist auf 0,05 %-Pkt quantisiert (1 Abtastwert je Periode).

---

## SYM-05 Symmetrieaussagen in den Quellen (Präreg A7, AP v2.4, FV v2.7)

- **Präreg-v2-Anhang A7 (L5a-095; repo und lokale Überarbeitung vom 01.10. wortgleich):**
  - „Konfiguration bis auf Umbenennung und Zeitverschiebung durch die Folge ihrer zyklischen Abstände bestimmt, bis auf zyklische Vertauschung“: **korrekt** (SYM-01).
  - „Spiegelung = Zeitumkehr, nur bei zeitumkehrsymmetrischem Profil und starrer Auflage eine Symmetrie; erhält die Menge der Abstände“: **korrekt**, mit zwei Präzisierungen. Erstens muss die starre Auflage ohne Abheben sein (oder die Auflage verlustfrei linear). Zweitens sind |N_k| und ⟨N⟩ im Kontaktast für jedes Profil spiegelinvariant (SYM-02).
  - „Jede Konfiguration des Feinfensters mit einem 120°-Abstand ist zu einem Schnittpunkt φ₂ ∈ [100°,140°] äquivalent“: analytisch geprüft, **korrekt**. Fall φ₂ = 120°: äquivalent zu (φ₃−120°, 240°). Fall φ₃ − φ₂ = 120°: äquivalent zu (360°−φ₃, 240°). Beide liegen in [100°, 140°].
  - Der „gespiegelte Schnitt“ (Hauptdokument §6: φ₂ = 240°, φ₃ = 100…140°) ist die Vertauschung (23), also exakt äquivalent.
- **AP v2.4 §8.4 und Anhang „Vertauschungssymmetrie“:**
  - Genannt wird nur (φ₂, φ₃) → (φ₃, φ₂). Das ist **korrekt, aber unvollständig**: Es fehlen die übrigen vier Elemente von S₃ und die Regel für arg N_k.
  - „Mittlere Differenz exakt null“: Über die 171 Paare i < j beträgt sie +5,3·10⁻⁶ N. Exakt null ist sie nur über alle 342 geordneten Paare, und dort trivial. Das Maximum 7,5 mN ist bestätigt.
  - „Numerischer Ursprung“ trifft für (23) zu: ODE und Start sind gleich bis auf die Summationsreihenfolge. Für die volle Gruppe ist die Ursache die Startphase zusammen mit Mehrstabilität (SYM-04).
- **AP Z. 1818 und FV refprofil („Egg zeitumkehrsymmetrisch, Triadenphasen 0 oder π“):** **korrekt**.
- **FV Z. 541** („Spiegelung/Zeitumkehr muss bei Dämpfung und Kontakt keine identischen Kennzahlen liefern“): **korrekt**.
- **Weder AP noch FV** nennen die volle Äquivalenzgruppe. Die Zeltasymmetrie wird in AP und FV als Befund geführt, ohne Bezug zur Spiegelung.
- **Patent X §5.2:** Die 120°-Invarianz ist **falsch** (SYM-03). Die Paarvertauschung ist richtig.
- **Forschungslinie §4 und Auswertung v3a §3:** gleicher Fehler. In der Auswertung wird er zusätzlich als Zuverlässigkeitsbeleg verwendet.

**Reproduktion.** Fundstellen per `grep -n` (siehe SYM-03, SYM-05). Zahlen aus `s3_analytik.py` (F).

---

## RT-01 Fensterbilanz und Reproduktion von Tab. 9.3 (Hot-Spot)

**Frage.** Gilt δ(T_w) = R(T_w) + Q, mit R = MΔv_S/T_w exakt ∝ 1/T_w und Q konstant? Reproduziert ein Potenzfit über die Fensterlängen 10/30/70/150 s den Exponenten −0,945?

**Formel (Prüfung).**
- ⟨F_c⟩_{T_w} = Mg + MΔv_S/T_w − ⟨F_ext,z⟩, mit F_ext,z als äußerer Kraft, positiv nach oben.
- Das ist FV v2.7 Gl. fenster (b_w = MΔv_S/T_w) und AP §8.3 Gl. randterm (δ_w = Δv_S/(gT_w)), identisch auch mit dem Code (R = M(v_e − v_s)/T_WIN).
- Das Vorzeichen ist numerisch bestätigt: Δv_S < 0 ergibt δ < 0.

**Methode.**
- Skalare Referenz-Engine, Standardstart, Δt = 50 µs, φ₃ = 208,421° (wie im Archiv auf 3 Stellen gerundet), ein Lauf bis 155 s.
- Zerlegung N1 − Mg = R + Q + E mit Q = N1 − N_RK4 und E = N_RK4 − Mg − R.

**Ergebnis.**
- **Reproduktion:** N1 stimmt mit Tab. 9.3 und dem Hot-Spot-JSON (Quelle L2-045) in allen Stellen überein:

| T_w | N1 / N | δ / ppm | R / ppm | Q / ppm | Δv_S / (m/s) | R·T_w / (ppm·s) |
|---|---|---|---|---|---|---|
| 10 | 6,333041 | −6815,5 | −6737,7 | −77,8 | −0,66097 | −67 377 |
| 30 | 6,361711 | −2319,3 | −2246,0 | −73,3 | −0,66100 | −67 380 |
| 70 | 6,369854 | −1042,3 | −962,5 | −79,8 | −0,66097 | −67 377 |
| 150 | 6,373122 | −529,8 | −449,1 | −80,7 | −0,66089 | −67 369 |

- **R ∝ 1/T_w:** R·T_w = −67 376 ppm·s mit 0,017 % Spannweite. Ein Potenzfit an R allein ergibt den Exponenten −1,00004.
- **Q:** −73,3 … −80,7 ppm. Es ist nur näherungsweise konstant (±4 ppm), denn Q ist ein Fenstermittel aufsetzphasenabhängiger Beiträge (RT-03), und der Zustand ist nicht streng periodisch (σ_v = 9,4·10⁻⁵ m/s je Zyklus im Vektorlauf, RT-05).
- **E:** 1,80·10⁻⁷ N (0,028 ppm).
- **Potenzfit über δ:**
  - Tab. 9.3, gerundete Werte: Exponent −0,9450.
  - Eigene Reproduktion: −0,9451.
  - Fit δ = A/T + Q: A = −67 355 ppm·s, Q = −78,7 ppm, Residuen ≤ 4,6 ppm.
  - Lokale Steigung −0,988 (10 s) bis −0,851 (150 s).
  - Bei A = −67 377 ppm·s ergäben Q = 0 / −40 / −78 / +78 ppm die Exponenten −1,000 / −0,972 / −0,947 / −1,063.
- **Fenster nach dem Einschwingen** (je 10 s ab 25, 45, 95, 145 s): R = −0,4 / −1,9 / +1,4 / −0,6 ppm, Q = −58,5 / −58,5 / −92,0 / −58,5 ppm.

**Bewertung.** L1b-042, L2-045 und P1 §3.4 sind **bestätigt**:
- −0,945 ist kein eigenes Gesetz, sondern die Mischung aus einem exakten 1/T_w-Randterm und einem Quadraturrest von etwa −78 ppm.
- Präzisierung: Q ist nicht streng konstant. Es schwankt zwischen −58 und −92 ppm, je nach Fenster.

**Reproduktion.**
- `timeout 540 python3 s5_randterm_skalar.py 0 208.421 155` (21 s) → `s5_randterm_skalar_0_208.421.json`
- `python3 s7_randterm_fit.py` (ohne Argument: nur Fits) → `s7_randterm_fit_ausgabe.txt`

**Einschränkungen.** Die Zahlen gelten für diese eine Einschwingrealisierung (RT-02).

---

## RT-02 Realisierungsabhängigkeit des Exponenten; Kontrollpunkt (0°, 0°)

**Methode.**
- Vektor-Engine (`sr_engine`, Arithmetik `finesweep`), 155 s, am Hot-Spot mit φ₃ = 208,421° und mit dem exakten Rasterwert 11·360°/19.
- Dazu (0,0), mit beiden Engines.

**Ergebnis.**
- **HS 208,421°, Vektor-Engine:** Δv_S = −0,6635 m/s statt −0,6610 m/s. R·T konstant, Q = −74…−81 ppm, Exponent −0,949.
- **HS mit exaktem Rasterwert:** Δv_S = −0,5751 m/s. Q = +27 … −76 ppm, weil das Fenster ab 5 s die Aufsetzer des Einschwingens enthält. Exponent −0,936.
- **Attraktor:** bei allen drei Varianten gleich, λ 75,094 %, γ₁ 1,658, F_max 38,49 N.
- **(0,0):**
  - In allen Fenstern ist |R| ≤ 3 ppm, und es gilt δ ≈ Q.
  - Skalar: −40,2 / +22,8 / −27,5 / +26,0 / +21,7 ppm, je nach Fenster.
  - Vektor: −14,1 ppm (5–15 s), −49,3 ppm (145–155 s).
  - Der Hüpfzustand ist aperiodisch: σ_v = 0,030 m/s an den Zyklusbeginnen.
  - Die „−40 ppm (Δt) gegen +27 ppm (Δt/2)“ der RK4-Diagnose (Quelle L1b-047) sind deshalb Einzelwerte eines schwankenden Q.

**Bewertung.** Der Exponent hängt an der Einschwingrealisierung (−0,936 … −0,949) und ist keine Systemgröße. Die Zerlegung δ = R + Q gilt in allen Fällen.

**Reproduktion.**
- `timeout 540 python3 s7_randterm_fit.py vektor` (ca. 3 min)
- `timeout 540 python3 s5_randterm_skalar.py 0 0 155`

---

## RT-03 Quadraturrest Q gegen Δt und Quadraturregel; Mechanismus

**Frage.** Wie hängt Q von Δt (Δt, Δt/2, Δt/4, zusätzlich Δt/8) und der Quadratur (Linksrechteck, Trapez, RK4-gewichtet) ab? Welche Ordnung hat Q? Verschwindet Q bei RK4-gewichteter Mittelung?

**Methode.**
- Punkte: HS (0; 208,421), S0 (0,0), L1 (157,3; 264,0), K1 (110,234).
- Neustart bei t = 30 s aus dem Attraktor des 50-µs-Laufs, dann 50 Perioden Vorlauf und Fenster 35–45 s (100 Perioden) je Δt.
- Aufsetzer werden protokolliert: Sprung der Dämpferkraft J = C·|ż| bei z = 0, θ = Lage im Schritt.
- Zwei Modelle für Q:
  - (i) exakte Abtastung einer springenden Funktion (Euler-Maclaurin): Q_J = (1/N)ΣJ(θ − ½);
  - (ii) RK4-Stufenmodell: Q_RK = (1/N)Σ(F_folge/2 − w_RK4). Im Sprungschritt verteilt RK4 den Impuls als w ≈ 5J/6 (θ < ½) bzw. J/6 (θ > ½). Je Aufsetzer ist Q daher ±J/3·(Δt/T_w)·(…), mit der Schranke |Q| ≤ n_td·J/(3N).

**Ergebnis.** Werte in ppm von Mg.

| Punkt | Größe | 50 µs | 25 µs | 12,5 µs | 6,25 µs |
|---|---|---|---|---|---|
| HS | Q Linksrechteck = Q Trapez | −54,31 | −6,28 | −18,89 | −2,10 |
| HS | Modell RK4-Stufen | −53,01 | −5,83 | −18,80 | −2,07 |
| HS | Rest Q − Modell | −1,31 | −0,45 | −0,087 | −0,027 |
| HS | Modell exakte Abtastung | −30,99 | −4,06 | −12,75 | −0,03 |
| HS | Schranke J/3 je Aufsetzer | 209,9 | 105,0 | 52,5 | 26,2 |
| S0 | Q | −13,49 | +6,82 | −7,76 | −2,82 |
| S0 | Rest Q − Modell | −1,75 | −0,42 | −0,11 | −0,026 |
| L1 | Q | −20,84 | −10,44 | +5,22 | +2,61 |
| L1 | Q / Schranke | −0,998 | −1,000 | +1,001 | +1,001 |
| K1 | Q | 7,7·10⁻⁷ | 4·10⁻⁸ | −1·10⁻⁹ | 1·10⁻⁸ |
| alle | E = N_RK4 − Mg − R [N] (HS) | 1,80·10⁻⁷ | 4,83·10⁻⁸ | −1,76·10⁻⁸ | 3,2·10⁻⁹ |
| alle | E [N] (K1, L1) | 1,85·10⁻⁷ | 4,62·10⁻⁸ | −2,31·10⁻⁸ | 2,9·10⁻⁹ |

**Befunde.**
- **Trapez = Linksrechteck.** Bei Fenstern aus ganzen Perioden mit F(Anfang) = F(Ende) sind beide identisch. Das Trapez hilft daher nicht.
- **Q ist O(Δt) mit aufsetzphasenabhängigem Vorzeichen.**
  - Die Schranke halbiert sich exakt (Ordnung 1,00).
  - Am streng periodischen L1 (ein θ je Lauf) ist |Q| = Schranke. Q halbiert sich exakt und wechselt das Vorzeichen, wenn θ die Schrittmitte überquert (θ < ½ bei 50 und 25 µs, θ > ½ bei 12,5 und 6,25 µs).
  - An HS und S0 schwankt θ von Zyklus zu Zyklus, und Q/Schranke liegt zwischen −0,36 und +0,06. Daher kommt die „nicht monotone“ Δt-Abhängigkeit (L1b-047).
- **Das RK4-Stufenmodell erklärt Q** bis auf einen Rest der Ordnung ≈ 2: HS 1,31 → 0,027 ppm, S0 1,75 → 0,026 ppm.
- **Das Modell „exakte Abtastung“ erklärt Q nicht** (HS −31 gegen −54 ppm). Q ist damit kein reiner Abtastfehler exakter Werte. Q ist der Unterschied zwischen dem Linksrechteck der diskreten Bahn und ihrer RK4-konsistenten Impulsbilanz am Dämpfersprung.
- **Mit RK4-gewichteter Mittelung verschwindet Q.**
  - Es bleibt E = M·mean_Simpson(ā), also der Simpson-Defekt der vorgegebenen Modulbeschleunigung mit ihren Knicken. Die Gleichheit ist in `s6c` auf 3 Stellen bestätigt.
  - E ist ≤ 1,85·10⁻⁷ N (0,03 ppm) bei 50 µs und von der Größenordnung O(Δt²) (Ordnung 1,9–2,0 im ersten Schritt), mit Vorzeichenwechseln je nach Lage der Knicke zum Raster.
  - Liegen alle Knicke auf dem Raster ((0,0)) oder heben sie sich auf ((120,240)), gilt E ≈ 10⁻¹³…10⁻¹⁵ N.
  - Die „~10⁻¹³ N“ aus L1b-047 gelten deshalb nur an solchen Punkten.
- **K1 (Kontaktast):** Q ≈ 0 (≤ 8·10⁻⁷ ppm), δ = E.
- **Observablen gegen Δt (HS, 50 → 6,25 µs):** λ 75,0885 → 75,0851 %, γ₁ 1,65801 → 1,65798, F_max 38,493 → 38,477 N, also O(Δt) durch die Abtastung der Stoßspitze.

**Bewertung.** P1 §3.4 und L1b-047 sind **bestätigt und präzisiert**:
- Q ist ein Auswerteartefakt der Ordnung O(Δt): Linksrechteck an der unstetigen Dämpferkraft, verbunden mit der RK4-Impulsverteilung im Sprungschritt.
- Es ist durch ±J/(3N) je Aufsetzer beschränkt und verschwindet bei RK4-gewichtetem Mittel bis auf E ≤ 0,03 ppm.

**Reproduktion.**
- `timeout 540 python3 s6_quadratur_dt.py p1`
- dann je Δt: `timeout 540 python3 s6_quadratur_dt.py 5e-5` (24 s), `2.5e-5` (60 s), `1.25e-5` (101 s), `6.25e-6` (186 s)
- `python3 s6b_quadratur_tabelle.py` → `s6b_quadratur_tabelle_ausgabe.txt`
- `python3 s6c_simpson_defekt.py`

**Einschränkungen.**
- θ wird linear interpoliert; der Fehler ist gegenüber J vernachlässigbar.
- HS und S0 sind nicht streng periodisch, daher ist Q dort ein Fenstermittel.

---

## RT-04 Archivresiduen (bis 6816 ppm; L1a-042/043/044)

**Methode.**
- Skalare Engine. Phasen wie im Archiv (3 Stellen).
- Alle 45 Archivpunkte mit |δ| > 50 ppm und eine Zufallsstichprobe von 25 der übrigen 316 Punkte.
- Fenster 5–15 s; Zerlegung in R, Q und E.

**Ergebnis.**
- Die Archiv-F_mean werden an allen 70 Punkten auf ≤ 4,9·10⁻⁷ N reproduziert.
- 19 Punkte mit |δ| > 200 ppm: R erklärt 96,3–100 % (Median 100,2 %) von δ.
- Max |Q| = 77,8 ppm (Median 32 ppm in der Gruppe |δ| > 50 ppm); |E| ≤ 0,12 ppm.
- Größte Werte: (0; 208,421) δ = −6815 = R −6738 + Q −78 ppm; (208,421; 0) −6773 = −6740 − 34; (284,2; 303,2) −6488 = −6520 + 31.
- In der Stichprobe (|δ| ≤ 50 ppm): |R| ≤ 36, |Q| ≤ 46 ppm.
- **Boden im Kontaktast:** Die „0,2 ppm numerischer Boden“ (AP Tab. residual-strat) entsprechen der 6-stelligen Rundung der CSV (10⁻⁶ N = 0,157 ppm). Der tatsächliche Rest im Kontaktast ist E. An (246,3; 113,7) ist er −0,088 ppm, an K1 +0,029 ppm.

**Bewertung.**
- Die Archivresiduen sind Randterm von Einschwingen oder unvollständigen Orbitperioden, dazu ein O(Δt)-Quadraturrest (|Q| ≲ 10² ppm, Vorzeichen zufällig) und E < 0,2 ppm.
- Sie sind kein Bilanzverstoß. Das bestätigt AP §8.3 und L1a-043/044.

**Reproduktion.** `timeout 540 python3 s9_archiv_zerlegung.py` (2 min) → `s9_archiv_zerlegung.csv`, `…_ausgabe.txt`

**Einschränkungen.** 70 von 361 Punkten wurden geprüft. Unter den nicht geprüften Punkten (alle mit |δ| ≤ 50 ppm) kann der Anteil von Q größer sein.

---

## RT-05 Folgerung für ⟨N⟩ = Mg als Nullkontrolle im Experiment

**Frage.** Welche Fensterlänge und -lage hält |δ_w| < ε = 10⁻⁴ (0,638 mN bei Mg = 6,3765 N)?

**Methode.** Referenzmodell (Engine) an vier Zuständen. Formeln:
- |δ_w| = |Δv_S|/(gT_w).
- (a) Fenster beliebig gelegt: |Δv_S| ≤ 2v_S,max, typisch √2·v_S,rms.
- (b) Phasenstarr über ganze Perioden: Es bleibt die Zyklusstreuung σ_v. Hinzu kommt ein Zeitfehler δt_b der Fenstergrenzen mit Δv_S = a_S·δt_b und a_S = (N − Mg)/M.
- (c) Fenster im Einschwingen.
- (d) Abtastbias bei Sprüngen (synthetisch).

**Ergebnis.**

| Zustand | v_S,max | (a) T_w worst | (a) T_w rms 1σ | σ_v je Zyklus | (b-i) T_w | max\|a_S\| | (b-ii) T_w bei δt_b = 100 µs |
|---|---|---|---|---|---|---|---|
| HS (λ 75 %) | 0,379 m/s | 773 s | 329 s | 9,4·10⁻⁵ m/s | 0,14 s | 49 m/s² | 5,0 s |
| S0 (λ 76 %, aperiodisch) | 0,528 | 1077 s | 338 s | 3,0·10⁻² | 43 s | 53 | 5,5 s |
| L1 (λ 12 %) | 0,127 | 259 s | 88 s | ~10⁻¹⁴ | – | 10 | 1,0 s |
| K1 (Kontaktast) | 0,031 | 63 s | 28 s | ~10⁻¹⁵ | – | 3,7 | 0,37 s |

- Liegt die Fenstergrenze im Flug (N = 0), gilt a_S = −g exakt und damit T_w ≥ δt_b/ε (1 s bei 100 µs).
- (c) Ein Fenster, das im Einschwingen geöffnet wird (Hot-Spot, Standardstart), hat Δv_S = −0,661 m/s und braucht T_w ≥ 674 s. Im Kontaktast klingt das Einschwingen mit 2M/C = 0,081 s ab.
- (d) Abtastmittel eines Signals mit Sprung J = 8 N, T = 0,1 s, 100 Perioden:
  - Kommensurabel abgetastet (f_s = 10 kHz, θ fest): Bias bis ±561 ppm (Schranke J/(2f_sT) = 4 mN = 627 ppm).
  - Inkommensurabel (f_s = 10 134 Hz): ≤ 37 ppm.
  - Rational nah (9973 Hz, Phasenmuster mit Periode 10): ≤ 62 ppm.

**Folgerungen (Empfehlung).**
1. Fenster erst nach nachgewiesenem Einschwingen öffnen, z. B. |v_S(t+T) − v_S(t)| bzw. Wiederholung des Kraftverlaufs je Periode.
2. Fenster phasenstarr über ganze Systemperioden legen, bei P-k-Orbits über k·T. Dann reichen im Kontaktast T_w ≥ 1 s, bei periodischen Hüpfzuständen wenige Sekunden. Bei aperiodischen Zuständen (S0) sind ≥ 43 s nötig (1σ).
3. Ohne phasenstarre Grenzen braucht man T_w ≥ 2v_S,max/(εg): 63 s (Kontaktast K1) bis über 1000 s (Hüpfen).
4. Das Kraftsignal vor der Abtastung bandbegrenzen (Antialiasing) oder f_s inkommensurabel zu f wählen. Sonst wirkt ein Q-artiger Bias bis J/(2f_sT) je Stoß und Periode.
5. Die Kennzahl je Lauf mit Δv_S-Abschätzung angeben.

**Einschränkungen.**
- Die v_S-Werte beziehen sich auf den Simulationsreferenzsatz: bewegte Masse = Gesamtmasse, Hub 5 mm, 10 Hz. Für V1 (μ < 1, anderer Hub und anderes f) skalieren sie mit dem bewegten Massenanteil und der Modulgeschwindigkeit (Annahme).
- Die Messkettendynamik (h*F) ist nicht enthalten.

**Reproduktion.** `python3 s8_fensterbedarf.py` → `s8_fensterbedarf_ausgabe.txt` (benötigt `s6_p1.npz`)

---

## TXT-01 F_min − ⟨N⟩ und Normierung des Phasenfaktors (nur Text)

- **„F_min − ⟨N⟩“** ist in AP v2.4 und FV v2.7 **nicht definiert**: grep über beide .tex-Dateien. Vorkommen gibt es nur in der Präreg v2, Hauptdokument Z. 53, 120, 166, 300 und 365. AP und FV kennen nur Mg − N_min bzw. Mg − F_c,min als Nenner von A bzw. A_pk (AP Z. 281/1701, FV Z. 321/792), bezogen auf Mg, nicht auf das Fenstermittel. Der P1-Befund ist **bestätigt**.
- **Phasenfaktor:**
  - AP v2.4 Z. 292/1827: Φ_j = 1 + e^{−ijφ₂} + e^{−ijφ₃}, N̂_j = Φ_jN̂_j^{(1)}.
  - FV v2.7 Z. 364/690: Φ_m = Σ_k e^{−imφ_k}, synchron Φ_m = n.
  - Beide normieren je Modul, ohne /3. **Bestätigt.**
  - `linear_solver.py` verwendet (1+…)/3 zusammen mit M·H·P_k. Das ist gleichwertig, weil N̂^{(1)} = (M/3)H·P_k (ein Modul der Masse M/3).
  - Patent X normiert mit /3 (Quelle L6a-063).

---

## Korrekturen an Quellen (Kurzfassung)

1. **Forschungslinie §4 S. 7, Auswertung v3a §3 S. 2, Patent X §5.2 und Anspruch 3:** Die 120°-Verschiebung ist keine Invarianz. Die richtige Gruppe ist S₃ (SYM-01). Die 120°-Verschiebung gilt nur an 6 Ausnahmepunkten und im Kontaktast für |N_{3j}|.
2. **AP v2.4 §8.4 und Anhang:** Nur (23) wird genannt; die volle S₃-Gruppe und die Phasenregel fehlen. „Mittlere Differenz exakt null“ ist bei Paaren i < j nicht exakt (+5,3·10⁻⁶ N). Die Verletzungen der vollen Gruppe entstehen durch die Startphase zusammen mit Mehrstabilität.
3. **AP §8.3:** Das „0,2 ppm numerischer Boden“ ist CSV-Rundung (0,157 ppm je 10⁻⁶ N). Der Rest im Kontaktast ist der Simpson-Defekt E ≤ 0,09 ppm.
4. **AP §8.3 und Tab. konvergenz:** Der Exponent −0,945 ist realisierungsabhängig (−0,936…−0,949). Q ist nicht streng konstant.
5. **RK4-Diagnose (L1b-047):** Die Bilanz schließt „bis 10⁻¹³ N“ nur an Punkten mit Knicken auf dem Raster. Allgemein bleibt E ≈ 1,8·10⁻⁷ N. Auch „nicht monoton in Δt“ hat eine Ursache: Die Lage der Aufsetzer im Schritt bestimmt das Vorzeichen von Q.
6. **Präreg A7:** korrekt. Präzisierung: Die Spiegelinvarianz von |N_k| im Kontaktast gilt für jedes Profil, und „starre Auflage“ ist als „ohne Abheben“ zu lesen.

## Offene Punkte

- Ein vollständiger S₃-Test auf einer Karte mit äquivalent gestarteten Bildern steht aus; es wurden nur 11 Basispunkte gerechnet.
- Für L4–L6 ist nicht geklärt, ob die Zustände chaotisch sind oder sehr lang einschwingen.
- Die Spiegelungsbrechung ist für V1-Parameter zu beziffern: ζ, Resonanzabstand von 2f und 3f, μ < 1.
- Ein Messplan für die Zeltasymmetrie als Prüfgröße der komplexen Kontaktübertragung fehlt.
