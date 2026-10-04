# P3 · Rolle „zusatz_p2“ · Gegenprüfung der in P2 nicht verifizierten Befunde

> **Vermerk zur Übernahme (04.10.2026).** Protokoll aus der Gesamtprojektanalyse 10/2026, Stand 02.10.2026, unverändert bis auf Pfade und Quellenangaben. Geprüft wurde der Repository-Stand `cd7be6a` (28.09.2026) mit der Präregistrierung v2 vom 25./28.09.2026; die späteren Änderungen aus PR #13 und PR #14 (unter anderem Präregistrierung v2 mit Arbeitsfestlegungen, `code/auslegung.py`, `code/ereignisloeser.py`) sind nicht eingearbeitet. Alle Zahlen sind Simulation oder Analytik, keine Messdaten. Verweise wie „L1a-019“, „P1 §3“ oder „B01–B14“ zeigen auf Arbeitsdokumente der Analyse, die nicht im Repository liegen. Quellen, die nicht im Repository liegen, sind als „(Quelle außerhalb des Repositorys)“ gekennzeichnet. Startbefehle und Grenzen je Gruppe: [`rechnungen/README.md`](../README.md).

Stand 02.10.2026 · ursprünglich lokal, jetzt unter `rechnungen/` · nichts committet, keine Repo-Datei verändert.
Kennzeichnung: **[Q]** Quellenangabe mit Fundstelle, **[R]** eigene Rechnung in diesem Ordner, **[E]** eigene Einschätzung, **[A]** Annahme.

Geprüft: KM-02, KM-03, KM-10, KM-11, KM-12 (Gruppe kippmoment), RT-04, SYM-01 (symmetrie_randterm), STA-10 (statistik).

## 1 Gelesen

- Befundtexte: (Quelle außerhalb des Repositorys) (Zeilen KM-02, KM-03, KM-10, KM-11, KM-12, SYM-01, RT-04, STA-10).
- Protokolle: `rechnungen/kippmoment/PROTOKOLL.md` (KM-01…KM-12, Korrekturtabelle), `rechnungen/symmetrie_randterm/PROTOKOLL.md`
  (SYM-01…SYM-05, RT-01…RT-05), `rechnungen/statistik/PROTOKOLL.md` (STA-00…STA-10).
- Ausgaben der Gruppe (nur zum Vergleich der Zahlen): `k1_…`, `k3_…`, `k4_…`, `k6_…_ausgabe.txt`; `s9_archiv_zerlegung_ausgabe.txt`;
  `s5_oc_tabelle_ausgabe.txt`, `s2_h1_oc_L*_n20_n020_k9.csv`, `s4_identifizierbarkeit_rest_ausgabe.txt`.
- Skripte der Gruppe nur zur Fehlersuche: `k6_messbarkeit_auslegung.py` Z. 39–46 (Fehler gefunden, s. §4), `k4_…py` Z. 6/66 (Richtung der Zelllagestörung: radial).
- Quellen [Q]: `docs/praeregistrierung_v2_entwurf.md` §2 (Z. 82–109, „Reichweite“ Z. 102–107), §3 (E3 Z. 144–146), §8.2–8.5 (Z. 331–368),
  §9.1 G7 (Z. 423–424), §9.3 (Z. 468–479); `docs/praeregistrierung_v2_anhang.md` A2.5 (Z. 192–201), A4 (Z. 289), A6 (Z. 313–327),
  A9.2 P0.1/P0.4 (Z. 451–472); `docs/arbeitspapier/PCMMS_Arbeitspapier_v2_4.tex` Z. 86, 3491 (Tab. residual-strat), 5293–5295;
  `code/finesweep.py`, `code/linear_solver.py`, `code/pcmms_v3a_phasen_sweep.py` (Parameter, Gleichung); `data/sweep_19x19.csv`, `data/README.md`;
  `docs/arbeitspapier/nachrechnung_2026-09-13/sweep_19x19_burnin_2026-09-13.csv` (Kopf, Zeilen (0,0), (0; 18,947));
  (Quelle außerhalb des Repositorys) §6 (Z. 103–116);
  (Quelle außerhalb des Repositorys) (L1a-018, L1a-042/043/044, L2-001, L4-026, L4-034, L4-036, L5a-065, L5a-068, L5a-072/073, L5b-057, L6a-063, L6b-046).

## 2 Vorgehen

Je Befund: Versuch der Widerlegung mit **eigenen, unabhängig geschriebenen** Skripten und anderem Rechenweg; Zahlen der Gruppe erst danach verglichen.

| Skript | Inhalt | Rechenweg (anders als P2) | Laufzeit |
|---|---|---|---|
| `zm.py` | eigenes 3-FG-Modell (Lagrange neu hergeleitet), Übertragungsmatrix T(kω), Momente, Drehzerlegung | Fourier-Koeffizienten des Egg-Profils **analytisch** (geschlossene Integrale), nicht per FFT | – |
| `z1_km02_modell.py` | KM-02 | lineare Lösung mit k_max = 8000 + FFT-Synthese; Zeitbereich mit **DOP853 (adaptiv)** statt RK4; Engine nur als Referenzdaten | 78 s |
| `z2_km03_auswahlregel.py` | KM-03 | analytische Geometriefaktoren; Drehsinn über Windungszahl der Zeitreihe | < 2 s |
| `z3_km10_identifizierbarkeit.py` | KM-10 | Konditionszahlen, Rückrechnung, **Jacobi-Rang-Analyse mit 15 Parametern** (Modulskala, -phase, Zellverstärkung, radiale/tangentiale Zelllage) für 5 Beobachtungsmengen; Rauschfortpflanzung | < 10 s |
| `z4_km11_messbarkeit.py` | KM-11 | Rauschmodell neu gerechnet, σ_A zusätzlich analytisch e_n/(S√T_a) | < 2 s |
| `z5_sym01_symmetrie.py` | SYM-01 | Brute-Force-Bahngrößen (360×360), lineares 1-FG-Modell, **eigene RK4-Engine** (neu geschrieben) mit äquivalentem und Standardstart | 163 s |
| `z6_rt04_archiv.py` | RT-04 | **diskrete RK4-Impulsbilanz**: E allein aus dem Profil, R aus ż(5 s), ż(15 s); Identität N_RK4 − Mg − R − E = 0 als Probe; rechte Seite der Referenz-Engine unverändert importiert (nötig für bitgleiche Einschwingbahnen) | 51 s |
| `z7_sta10_drift.py` | STA-10 | halbanalytisch: A4-Beispiel neu gerechnet, c = t(1 − 0,05/294; ν), Gauß/t-Näherung je Test, analytische Obergrenze | < 10 s |
| `z8_ergaenzung_km02_km12.py` | Entkopplung μ = 1 einseitig; \|M(t)\|, Umlaufzahl | eigene 3-FG-RK4 in q-Koordinaten gegen 1-FG-Schleife mit `finesweep.rhs` | 20 s |

Reproduktion (aus diesem Ordner):
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../../code timeout 540 python3 <skript>` (z6 mit Argument `2` = Prozesse). Ausgaben: `<skript>_ausgabe.txt`.

Annahmen der Geometrie [A] wie in P2 (für die Vergleichbarkeit): Zellen auf R_c = 100 mm bei 0/120/240°, G0 Module über den Zellen,
G60h Module auf R_c/2 bei 60/180/300°, Rahmen als Scheibe mit Kipp-Trägheitsradius ρ_f = R_c/2 (Scheibe: J um Durchmesser = M R²/4, also korrekt),
STEIF: f_n = 120 Hz, ζ = 0,02 (K = 369 518 N/m, C = 19,60 N·s/m).

## 3 Ergebnisse je Befund

### KM-02 · 3-FG-Zellmodell, Validierung — **bestätigt**
- [R] Profil: A_k analytisch = FFT (14,9649/4,9321/2,1280/… m/s², arg c₁ = 63,00°) – `z1_…_ausgabe.txt` (0).
- [R] Summe der linearen Zellkräfte (eigenes Modell, μ = 1, G0, (0,120,240)) gegen `finesweep.run(120, 240)`: F_min 5,330390 / F_max 7,491922 / ⟨N⟩ 6,376500000 N identisch; max|ΔN| = **7,4·10⁻⁹ N** über 0,3 s (Unterschied lineare Lösung gegen Engine-RK4; P2 gibt 3,1·10⁻¹³ N für RK4 gegen RK4 an – beides belegt die Übereinstimmung).
- [R] Hub/Kippen entkoppelt: Nebendiagonale von Mq und Kq ≤ 1,3·10⁻¹⁷; bei μ = 1, G0 gilt Mq = (M/3)·B_c B_cᵀ exakt → drei unabhängige Einmassenschwinger (analytisch: Transformation w = B_cᵀq; einseitiger Kontakt je Zelle hängt nur von w_j ab).
- [R] Alle 12 Fälle aus `k3_…` (F_min Zelle, R+₁, R−₂) mit dem eigenen Modell auf alle 5 angegebenen Stellen reproduziert (z. B. REF μ = 1 G0 T: −6,30814 N, 0,65161, 0,80625 N·m; STEIF μ = 0,462 G60h Z: 1,14061 N).
- [R] DOP853 gegen eigene lineare Lösung: ≤ 2,0·10⁻⁸ N (3 Fälle). Einseitige Entkopplung (z8): Zelle 1 = Engine(0,0)/3 bis 0,1 s auf 2·10⁻¹⁴ N, bis 1 s auf 1,9·10⁻¹⁰ N (P2: 8,5·10⁻¹⁴ / 7,8·10⁻¹⁰ N).
- [E] Die Validierung prüft die Implementierung, nicht die Modellannahmen (starrer flacher Körper, ρ_f, keine Horizontal-FG) – diese Einschränkungen nennt P2 selbst.

### KM-03 · Auswahlregel — **bestätigt**
- [R] analytisch: Moment als komplexe Zahl m = M_x + iM_y ∝ Σ_i f_i(t)e^{iψ_i}; Koeffizient von e^{+ikωt} ist S_k = Σe^{iψ_i}e^{−ikφ_i}, von e^{−ikωt} S′_k = Σe^{iψ_i}e^{+ikφ_i}. Mit ψ_i = φ_i = 0/120/240°: S_k = 3 für k ≡ 1, S′_k = 3 für k ≡ 2, Summenfaktor 3 für k ≡ 0 (mod 3), sonst 0; bei umgekehrter Reihenfolge tauschen S und S′.
- [R] numerisch (STARR, STEIF, REF): 2|N_k| = 0 für k ≢ 0; R± wie behauptet; Windungszahl des k-Anteils +1, −2, +4, −5 je Periode (`z2_…`).
- [R] Einzelzelle enthält alle Ordnungen (G0 quasistatisch T = Einheitsmatrix; Formel 1/3 + 2R_m/(3R_c)cos Δψ gegen Gleichgewicht: 1,7·10⁻¹⁶).
- [E] Der Drehsinn hängt an drei Konventionen (Modulnummerierung gegen geometrische Reihenfolge, Verzögerung τ = φ/(2πf), Blick von oben); P2 nennt die erste ausdrücklich. Exakt für gleiche Module und symmetrische Anordnung; im steifen Fall ist die Einzelzelle nur näherungsweise „ein Modul“ (cond T = 1,002–1,056).

### KM-10 · Identifizierbarkeit — **eingeschränkt**
Bestätigt [R] (`z3_…`):
- Konditionszahlen exakt wie P2: G0 1,0; G60h 2,0; STEIF G0 1,002–1,056, G60h 2,009–2,259; REF μ = 1 G60h 2,509/7,595/3,886/3,461 (k = 1, 2, 4, 5). Zusätzlich REF μ = 0,462: G0 bis 1,58, G60h bis 6,29.
- Rückrechnung: Masse/Hub +1 % → +1,000 %, Phase +1° → −1,000°/−2,000° (k = 1/2) am richtigen Modul (STARR exakt, STEIF ≤ 0,013 % Abweichung); G0: Zellverstärkung +1 % ≡ Masse +1 % des Moduls darüber; G60h k = 1: +0,251/+0,251/+0,500 %, ∓0,247°; Zelllage 1 mm radial: −0,662 % am eigenen Modul, −0,165 %/∓0,165° an den Nachbarn.
- Rang (nur ε, δ, γ; Lagen bekannt): G0 Rang 6/9 bei jeder Beobachtungsmenge, Nullraum genau γ_j − ε_j (je Zelle/Modul-Paar) – auch mit allen Harmonischen und mit drei Einzelmodulläufen.
Eingeschränkt / korrigiert [R]:
1. **G60h ist nicht „konfundiert“ im Sinne von KM-10**: Das Muster einer Zellverstärkung kehrt bei k = 2 das Vorzeichen der Scheinphase um (k = 1: ∓0,247°, k = 2: ±0,247°); ein Modulphasenfehler dreht dagegen um −k·δ. Bei bekannten Zelllagen ist der Rang mit k = 1, 2 **8/9**; einziger Nullraum ist die globale Skala (alle γ = +c, alle ε = −c, Komponenten 1/√6). Anpassung des Musters „Z2 +1 %“ allein mit Modulfehlern lässt 65 % des Signals als Rest (1,5 mN je Zellzeigerkomponente bei σ_A ≈ 0,02–0,16 mN). Nur mit k = 1 allein trifft die P2-Aussage zu (Rang 6/9).
2. **Mit unbekannten Zelllagen** (15 Parameter, k = 1…5): Rang 12/15 bei G0 und G60h. Der Nullraum ist bei G0 γ_j − ε_j, bei G60h eine Mischung aus γ, ε und **radialer Zelllage**. Einzelmodulläufe beheben das nicht (Rang bleibt 12). Mit statischen Gewichtsstücken an den P0.1-Stellen (Mitte, über jeder Zelle, Modulachsen; Präreg A9.2 Z. 451–456) wird der Rang **15/15** (kleinster Singulärwert 3,9–5,2·10⁻³ N je 1 %/1°/1 mm). Die P2-Voraussetzung „P0.1 und Zelllage kalibriert“ ist damit quantitativ gestützt; Bedingung [A]: Laststellen und Gewichtsmassen genau bekannt.
3. „Exakt dem richtigen Modul zugeordnet“ gilt nur quasistatisch bzw. steif. Bei REF μ = 1 G0 ändert eine Massenstörung T selbst: Rückrechnung +1,344 %/−0,026° (k = 1), +0,213 %/−2,854° (k = 2) (P2-Ausgabe `k4_…` zeigt das, der Befundtext nicht).
4. Nicht behandelt in KM-10: tangentialer Zelllagefehler 1 mm → ∓0,29 % und ∓0,29° an den Nachbarmodulen, 0 am eigenen (G0, STARR).
5. Mit nur einer Harmonischen sind auch Phasenfehler bei G60h nicht trennbar (δ im Nullraum); die Aussage „Phasenfehler unterscheidbar“ braucht ≥ 2 Harmonische (implizit in P2).
- Rauschfortpflanzung [R, A wie KM-11]: je Lauf u(Amplitude) 0,024–0,27 mN, u(Phase) 0,001–0,03° je Modul – weit unter Präreg Tab. F u(Δδ) ≤ 0,1°; begrenzend sind Systematiken (bestätigt KM-11-Folgerung).

### KM-11 · Messbarkeit — **eingeschränkt** (Folgerung hält, Zahlen teils falsch)
- [R] σ_F je Stichprobe 2,41–21,31 mN: bestätigt. **σ_A je Lauf ist unabhängig von f_s** (σ_A = σ_F√(2/N_s) = e_n/(S√T_a), weil σ_F ∝ √f_s): **0,024–0,156 mN** statt „0,018–0,21 mN“; Moment **2,9–19,1 µN·m** statt „2–26 µN·m“. Ursache: Skriptfehler (§4).
- [R] Signale bestätigt: A₁ = 1,498 N (45,8·u_c), A₂ = 0,494 N (15,1·u_c), Zelle/Summe SS 2,392, R+₁ = 0,2247 N·m, R−₂ = 0,0741 N·m; 1 % Zellverstärkung → 0,0150 N in N₁; 1 mm Zelllage (radial, Momente mit nominaler Lage) → R−₁/R+₁ = 0,00332 = 1-%-Ellipse (0,00333).
- [R] A₁/σ_A = 9,6·10³ … 6,2·10⁴ (P2: „etwa 7·10³“). SNR der 1-%-Ellipse (R−₁ = 7,49·10⁻⁴ N·m): **39–254** mit dem P2-Schätzer, **56–359** mit dem optimalen Schätzer der gegenläufigen Komponente (Std |P̂−| = σ_M/√N) – statt „29–350“.
- [Q/R] A6 (Anhang Z. 325–327): f_s ≥ 702,5·k_max Hz bei 10 Hz → 2107 (k = 3), 3512 (k = 5) Hz bestätigt. [E] Kontext: Die Präreg verlangt für die H1-Auswertung mit k_max = 9 ohnehin ≥ 6,3 kHz (A6, Z. 327; §5.1 Z. 185); „2 kSPS reichen nicht“ betrifft den Laborplan V1, nicht die Präreg. Bei 12 Hz steigen die Werte um 20 %.
- [E] Unverändert gültig: Rauschen ist nicht begrenzend; Rauschmodell ist Annahme (keine Datenblattprüfung), mechanisches Rauschen/Drift nicht modelliert.

### KM-12 · Bewertung — **eingeschränkt**
Folgt aus den Zahlen [R/Q]:
- Superposition je Zelle im Kontaktast (T(kω) linear), zweite Hälfte (k ≢ 0) der linearen Antwort am Triphasik-Punkt (KM-03 bestätigt), H_t ≈ 1 im steifen Fall (cond T ≤ 1,056, |H| = 1,00–1,03 für k ≤ 2), großes Signal (45,8·u_c), Betrag nicht konstant (\|M\| max/min 2,24 STARR, 2,82 STEIF, 9,17 REF μ = 1 mit −2 Umläufen je Periode; z8), E3 bereits explorativ ohne Entscheidungsregel (Präreg §3 Z. 144–146).
Einschränkungen [Q/E]:
1. **Quelle falsch gelesen:** KM-12 begründet die Stärke mit „sieht genau die Störungen, für die H2 laut Präreg blind ist“. Präreg §2 „Reichweite“ (Hauptdokument Z. 104–105, lokal überarbeitete Fassung Z. 118, wortgleich) sagt das Gegenteil: „H2 **zeigt** Kopplungen, nicht konstante Phasenfehler oder nicht erfasste Modulunterschiede“; §9.4 deutet eine H2-Falsifikation genau so. Richtig wäre: H1/H2 sind gegen **konstante** Modulunterschiede unempfindlich (sie stecken in der Vorhersage ŷ, KM-09; §8.3 Z. 350–351: konstanter Skalenfehler fällt heraus), H2 zeigt nicht konstante nur summarisch; der Zellkanal misst beide **modulaufgelöst** und kann eine H2-Abweichung einem Modul zuordnen.
2. Das Argument „im steifen Aufbau prüft das Moment den Kontakt nicht“ trennt nicht zwischen Moment und N: Auch N ist dort quasistatisch (Präreg §2: H1 „in einem steifen Aufbau überwiegend ein Test der Apparatur“). Es spricht daher nicht spezifisch gegen das Moment als zweite Vorhersage.
3. Gegen „kein zusätzlicher Modellgehalt“: Eine Zell-Erweiterung von H1 prüft Superposition in den zwei Kipp-Freiheitsgraden und bei 1,35–2,39-fach größerer Wechselamplitude je Zelle (KM-06/z4); Abweichungen, die sich in der Summe aufheben (k ≢ 0 am Triphasik-Punkt), wären nur dort sichtbar. Gleiche Hypothesenklasse, aber zusätzliche Prüfkraft – P2 nennt das als „optionalen Ausbau“, die Gesamtwertung bleibt vertretbar.
4. Die Schwäche „konfundiert mit Zellverstärkung und Zelllage“ ist mit der bereits registrierten P0.1-Kalibrierung behebbar (z3: Rang 15/15), also kein grundsätzliches Hindernis für die empfohlene registrierte Kontrolle.
Gesamt [E]: Die Empfehlung (registrierte Kontrolle mit vorab festgelegter Auswertung, nicht zweite physikalische Hauptvorhersage) folgt aus den Zahlen; eine der drei Begründungen beruht auf einer falsch gelesenen Quelle, eine trennt nicht.

### SYM-01 · Äquivalenzgruppe S₃ und Phasenregel — **bestätigt**
- [R] Brute Force 360×360: Bahngröße 1 nur (0,0); 2 nur (120,240)/(240,120); 3 genau die 1077 = 3·359 Punkte mit zwei gleichen Phasen; sonst 6. Abgeschlossenheit an 50 Zufallspunkten × 36 Kompositionen.
- [R] ā_gA(t) = ā_A(t + τ_ref) auf 4,8·10⁻¹⁴ m/s² (20 Punkte × 6 Bilder).
- [R] lineares Modell (110°, 234°): Phasenregel arg N_k(gA) − arg N_k(A) − kφ_ref ≤ 1,2·10⁻¹³°, |N_k| ≤ 5,6·10⁻¹⁶ N, Triadenphase arg(N₁²N₂*) = **+62,3723°** in allen 6 Bildern.
- [R] nichtlinear, eigene RK4-Engine, L1 (157,3; 264) λ = 12,4 % und L2 (198,2; 267,4) λ = 18,2 %: äquivalenter Start → alle Observablen und Phasenregel auf ≤ 1,4·10⁻¹³ N bzw. 1,9·10⁻¹¹°; Standardstart → gleicher Attraktor (λ 18,15–18,20 %, Quantisierung 0,05 %-Pkt), Δ⟨N⟩ ≤ 4,1·10⁻⁴ N, Phasenregel ≤ 0,075° (Gitterphase/Q, wie SYM-04).
- [E] Die Einschränkung „masseloser Rahmen“ ist für das 1-FG-Modell unnötig streng: mit μ < 1 geht ebenfalls nur ā(t) ein (−μMā), die Gruppe gilt unverändert. Für Zellkräfte/Momente (3-FG) gilt sie nur mit gleichzeitiger Permutation der Modullagen.

### RT-04 · Archivresiduen — **bestätigt** (mit Textkorrekturen)
- [R] Stichprobe 38 Punkte: alle 19 mit |δ| > 200 ppm, 10 von 26 mit 50–200 ppm, 8 von 316 mit ≤ 50 ppm, dazu (246,316; 113,684). Archiv-F_mean reproduziert auf **≤ 4,85·10⁻⁷ N**; Identität N_RK4 − Mg − R − E ≤ 7·10⁻⁸ ppm (E unabhängig aus dem Profil).
- [R] |δ| > 200 ppm: R/δ = **0,963 … 1,019**, Median 1,002 → „96,3–100 % (Median 100,2 %)“ ist intern widersprüchlich (Median > Maximum); richtig **96,3–101,9 %**. |Q| max 77,8 ppm; Median |Q| in dieser Gruppe 5,9 ppm (die „32 ppm“ von P2 gelten für die 45 Punkte > 50 ppm). |E| ≤ 0,121 ppm.
- [R] Beispiele exakt: (0; 208,421) −6815 = −6738 − 78 ppm; (208,421; 0) −6773 = −6740 − 34; (284,2; 303,2) −6488 = −6520 + 31.
- [R] Kontaktast: E(246,316; 113,684) = −0,088 ppm, E(110, 234) = +0,029 ppm; 10⁻⁶ N = 0,157 ppm – bestätigt.
- [R/E] Zusatz: Für 50 < |δ| ≤ 200 ppm dominiert meist Q (Stichprobe: |R| > |Q| nur an 3 von 10; P2: 6 von 26). Die Überschrift „Archivresiduen sind zu 96–100 % Randterm“ gilt nur für |δ| > 200 ppm.
- [R] Das Archiv ist nur mit den **3-stellig gerundeten Phasen** reproduzierbar; mit exakten Rasterphasen k·360°/19: Hot-Spot +5,85·10⁻³ N (R = −5865 statt −6738 ppm), (0; 18,947) +9,6·10⁻⁵ N. Die Nachrechnung 13.09. verwendet exakte Phasen (CSV Zeile 2: 18,94736842105263) – Archiv- und Nachrechnungswerte gehören also zu leicht verschiedenen Konfigurationen.

### STA-10 · Drift-Logik — **bestätigt**
- [Q] Regeln §8.2 (Z. 336–338), §8.5 PB1 (nur r⁰, Z. 364–366), §9.3 (Z. 472), G7 (ΔT = 0,1 %/TK_C, Z. 423–424).
- [R] A4-Beispiel mit k_max = 9 neu gerechnet: F_min 5,6781/5,1608 N (wie A6), max|y_F| = 1,2157 N, Δ_F/Δ_N1/Δ_N2/Δ_N3 = 129,3/112,6/73,1/138,3 mN, 147 Tests, c(ν = 37) = 3,948.
- [R] Gauß/t-Näherung (Tests unabhängig, ρ(z⁰, z¹) = 0,5): Drift 1 %: P(falsifiziert) = 0,022/0,017/0,011 (L0/L1/L2), Drift 3 %: 0,023/0,023/0,014; P(bestätigt) = 0, P(PB1) = 1, P(ein |z⁰| > c) = 1. Analytische Obergrenze bei vollständig signifikantem z⁰: 147·α/294 = 0,025. P2-Simulation (korrelierte Tests) 0,010–0,018 liegt darunter – konsistent.
- [R] 0,1 % Verstärkungsdrift (G7) auf L0: z⁰(F_min) = 4,6 (P2: 4,7 mit gerundetem u_c); **stärkster Test ist Re N₃ mit z⁰ = 6,5**, 31 von 147 Tests mit E|z⁰| > c. Auf L1 nur noch max z⁰ = 2,4 → die Aussage gilt nur bei sensorbegrenzter Präzision (so von P2 eingeschränkt).
- [R] PB1-Bindung (P = 0,9, 21 Punkte, Δ/u ≥ c + 2,81 = 6,75): F_min bei u_c(F) ≈ 19 mN, N₁ bei u_c(F) ≈ 11 mN, N₂ ≈ 21 mN → „10–20 mN“ bestätigt.

## 4 Fehler in Skripten der P2-Gruppen

1. `rechnungen/kippmoment/k6_messbarkeit_auslegung.py` Z. 39–46: `sig_lo, sig_hi = min/max(s[3] for s in szen)` mischt die σ_F beider Abtastraten und multipliziert sie mit √(2/N_s) der jeweils anderen Rate. Folge: σ_A „0,0241…0,2130 mN“ (2 kHz) und „0,0176…0,1556 mN“ (3,75 kHz); richtig für beide 0,0241…0,1556 mN. Befund KM-11 (σ_A, Moment, SNR, „7·10³·σ_A“) übernimmt die falschen Grenzen. Die Folgerung bleibt.
2. Kein Fehler, aber Darstellungsmangel: `s9_archiv_zerlegung.py` gibt für R/δ nur min und Median aus; daraus entstand im Befundtext die falsche Obergrenze „100 %“.

## 5 Quellenstichprobe

Geprüft und korrekt: Präreg A2.5 Z. 192–201; A6 Z. 325–327; A9.2 P0.1 „mindestens fünf Stellen“ Z. 454; P0.4 ohne Anregungsort Z. 465–472; u_c ≤ 0,0327 N A4 Z. 289; E3 §3; §8.5 PB1 nur r⁰; G7; §9.3; AP v2.4 Z. 86/3491 („0,2 ppm“), Z. 5293–5295 („eindimensional … Kippen“); PCMMFM-Fehlerbudget §6 (elektrisch 0,001–0,005 N, σ_total ≈ 0,024 N); evidenzmatrix-Einträge wie in §1.
Falsch wiedergegeben: Präreg §2 „Reichweite“ in KM-12 (s. o.).

## 6 Bewertungsmaßstab

bestaetigt = Kernaussage und Zahlen mit eigenem Weg reproduziert, nur Randkorrekturen; eingeschraenkt = Kernaussage hält, aber eine Teilaussage, Zahl oder Begründung ist falsch bzw. gilt nur unter zusätzlichen Bedingungen; widerlegt = Kernaussage falsch. Keine Aussage dieser Prüfung beweist Neuheit; Literaturvergleiche wurden nicht angestellt.
