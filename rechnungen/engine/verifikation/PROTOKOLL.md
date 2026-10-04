# P2 · Prüfgruppe „engine“ · Gegenprüfung (Verifikation)

> **Vermerk zur Übernahme (04.10.2026).** Protokoll aus der Gesamtprojektanalyse 10/2026, Stand 02.10.2026, unverändert bis auf Pfade und Quellenangaben. Geprüft wurde der Repository-Stand `cd7be6a` (28.09.2026) mit der Präregistrierung v2 vom 25./28.09.2026; die späteren Änderungen aus PR #13 und PR #14 (unter anderem Präregistrierung v2 mit Arbeitsfestlegungen, `code/auslegung.py`, `code/ereignisloeser.py`) sind nicht eingearbeitet. Alle Zahlen sind Simulation oder Analytik, keine Messdaten. Verweise wie „L1a-019“, „P1 §3“ oder „B01–B14“ zeigen auf Arbeitsdokumente der Analyse, die nicht im Repository liegen. Quellen außerhalb des Repositorys sind als „(lokaler Bestand, nicht im Repository)“ gekennzeichnet. Startbefehle und Grenzen je Gruppe: [`rechnungen/README.md`](../../README.md).

Stand 02.10.2026. Rolle: unabhängiger Gegenprüfer. Ziel: die Befunde ENG-01 … ENG-10 der Gruppe „engine“ mit
eigenen, unabhängig geschriebenen Werkzeugen zu widerlegen oder zu bestätigen. Alle Zahlen in diesem Protokoll
stammen aus eigener Rechnung in diesem Ordner, außer wo „Quelle“ oder „Gruppe“ steht. Repo-Code wurde weder
geändert noch importiert; auch die Skripte der Gruppe wurden nur gelesen. Parameter wurden aus `code/pcmms_v3a_phasen_sweep.py` abgeschrieben
(M = 0,650 kg, g = 9,81, f = 10 Hz, THOLD = 0,65, RTOP = 5 mm, RBOT = RTOP·TFAST/THOLD, K = 1e4 N/m, C = 16 N·s/m).

**Vorspann für alle Befehle**

```
cd rechnungen/engine/verifikation
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../../../code
```

## 0 Eigene Werkzeuge (anderer Rechenweg als die Gruppe)

| Datei | Rechenweg | Unterschied zur Gruppe |
|---|---|---|
| `vk_model.py` | Profil a, e′, e geschlossen; τ = φ[°]/360·T (Grad direkt, ohne Radiant) | eigene Formeln; Integrationskonstanten aus Periodizität |
| `vk_sa.py` | **Halbanalytischer ereignisgenauer Löser (SA).** Freiflug: Schwerpunkt ballistisch (geschlossen). Kontakt: lineare ODE mit stückweise sinusförmiger Anregung, geschlossene Lösung je knickfreiem Stück. Ereignisse (N = 0 fallend; min(−z, N) > 0) auf 1-µs-Raster gesucht und mit brentq (xtol 1e-16) verfeinert. Momente ∫N^p dt mit Gauß-Legendre. Floquet per Newton und zentralen Differenzen. | kein Runge-Kutta, kein DOP853 (Gruppe: DOP853 mit Ereignissen) |
| `vk_rk4com.py` | **RK4 in Schwerpunktkoordinaten (RK4-S):** Zustand (Z, V), z = Z − ē(t), ż = V − ē′(t); ē, ē′ tabelliert. Frequenzrampe ohne ρ′-Term (z = Z − ē(θ), ż = V − ρ·ē′(θ)). | andere Diskretisierung als die Engine (Rahmenkoordinate mit expliziter Anregung −ā) |
| `vk_kontakt.py` | stationäre Kontaktlösung mit **analytischen** Fourier-Koeffizienten des Profils (k ≤ 20 000) | Gruppe/`linear_solver.py`: FFT des abgetasteten Profils |
| `vk_paare.py` | eigene Herleitung der Gruppe S₃ (Referenzwechsel + Reihenfolge) | unabhängig von `sym_count.py` |

Validierung: SA gegen Fourierlösung im Kontakt (F_min, F_max, γ1 identisch auf ≤ 2·10⁻⁵ N); SA gegen RK4-S im
Hüpfzustand der Insel (λ 75,8154 % gegen 75,8156 % bei Δt/2); Impulsbilanz im SA exakt (≤ 10⁻¹⁵ N·s);
⟨N⟩ − Mg − R im SA ≤ 10⁻¹³ N in allen Fenstern.

Eigene Fehlerprüfung: Grad/Radiant (τ über Grad, Fourierphase über `np.radians`), Phasenvorzeichen (Modul k bei
e(t − τ_k), Koeffizient P_k·e^{−ikφ}), Linksrechteck gegen RK4-gewichtet getrennt ausgewiesen (`Q`), Startdefinition
imp: ż(0) = −ē′(0), Rampe: V(0) = 0. Ein Fehler wurde während der Arbeit gefunden und behoben: die erste
Fassung von `vk_kontakt.py` summierte die Fourier-Reihe direkt auf 10⁵ Punkten (zu langsam, nicht falsch);
ersetzt durch exakte irfft-Auswertung, Kontrolle direkte Summe gegen irfft: 9·10⁻¹⁶ N.

---

## ENG-01 Koordinaten und Anfangsimpuls des Standardstarts — **bestätigt**

**Frage.** Stimmen z als Rahmenlage, z_S = z + (1/3)Σe(t−τ_k), M·z̈_S = −Mg + N und v_S(0) = 0,2417 m/s bei (0°, 0°)?

**Methode.** Bewegungsgleichung aus `pcmms_v3a_phasen_sweep.py` (`rhs`: zdd = −G + Fc/M − zdd_egg) gelesen;
e′ analytisch, Kontrolle durch zweifache Trapezintegration der Engine-Beschleunigung (10⁶ Stützstellen) mit
Periodizitätsbedingung; Impulsbilanz im SA.

**Ergebnis.** e′(0) = 0,241661 m/s (analytisch = numerisch, Abweichung 2·10⁻¹²). v_S(0): (0°,0°) +0,2417;
(0°,208,421°) +0,1250; (120°,240°) −0,0023; (35°,116°) +0,0543; (113,684°,227,368°) −0,0130; (100°,240°) +0,0131 m/s.
M·v = 157,08 mN·s = 24,63 % von M·g·T; ½Mv² = 18,98 mJ gegen (Mg)²/2K = 2,033 mJ. 1°-Raster: max +0,2417,
min −0,0806, Median |v_S(0)| 0,0806 m/s (Hinweis: Mittel über das Raster = V0/3 = 0,0806). Impulsbilanz SA:
∫(N − Mg)dt − MΔV_S ≤ 10⁻¹⁵ N·s. Alle Zahlen der Gruppe reproduziert.

**Reproduktion.** `timeout 300 python3 vk_impuls.py` → `vk_impuls_ausgabe.txt`

**Einschränkung.** μ = 1 wie in der Engine.

---

## ENG-02 Kontaktast: startunabhängig, Floquet, stoßfest — **bestätigt**

**Methode.** (a) Harmonische Balance mit analytischen Fourier-Koeffizienten; (b) |µ| = exp(−CT/2M); (c) SA mit
Starts std/imp/Orbit; (d) SA-Stöße Δż = ±0,3, ±1, ±3 m/s an Zyklusphase 0 und 0,5, je 15 s, an (120°,240°),
(113,684°,227,368°), (100°,240°) und den Präreg-Piloten (110°,250°), (130°,230°), (110°,252°) — 72 Läufe.

**Ergebnis.**
| Punkt | γ1 | F_min (50-µs-Stichproben / kontinuierlich) | F_max |
|---|---|---|---|
| (120°,240°) | 0,066794 | 5,33039 / 5,33039 N | 7,49192 N |
| (113,684°,227,368°) | −0,272972 | 2,88213 / 2,88212 N | 9,46219 N |
| (100°,240°) | −0,344085 | 0,76769 / 0,76767 N | 10,9548 N |
| (110°,250°) | −0,229987 | 1,60156 / 1,60154 N | 10,634 N |
| (130°,230°) | −0,127528 | 1,86994 N | 10,128 N |
| (110°,252°) | −0,178137 | 1,31637 / 1,31635 N | 10,954 N |

|µ| = exp(−1,2308) = 0,2921 (analytisch). SA: alle Starts → derselbe Orbit, Einschwingen |Δż| < 10⁻⁶ nach
0,8–0,9 s, < 10⁻⁸ nach 1,0–1,3 s. Stöße: alle 72 Läufe enden im Kontakt (λ = 0 in den letzten 5 s, F_min
identisch mit dem Orbit), obwohl die Stöße zwischenzeitlich bis zu 100 % Liftoff je Zyklus erzeugen.

**Reproduktion.** `timeout 540 python3 vk_kontakt.py base`; `for r in "0 2" "2 4" "4 6"; do timeout 540 python3 vk_kontakt.py kicks $r; done`
→ `vk_kontakt_base_ausgabe.txt`, `vk_kontakt_kicks_*_ausgabe.txt`

**Einschränkung.** Stichprobe (zwei Phasen, sechs Beträge); kein Beweis globaler Monostabilität.

---

## ENG-06 Satelliteninsel (35°, 116°) — **bestätigt** (eine Präzisierung)

**Methode.** SA (std, imp, Orbit; Newton/Floquet beider Zustände; Stöße ±0,03 … ±0,30 m/s an zwei Phasen),
RK4-S bei Δt = 50 µs und 25 µs (100 s, std/imp/Orbit), Rampen 2 s und 10 s (siehe ENG-10).

**Ergebnis.**
- Hüpfzustand (std und imp): SA λ 75,8154 %, γ1 1,69813, F_max 39,473 N, |µ| = 0,7426 (komplexes Paar, stabil).
  RK4-S Δt: 75,8165/75,8143 %, F_max 39,494/39,495 N; Δt/2: 75,8156/75,8143 %, F_max 39,488/39,487 N.
- Kontaktorbit: λ 0, F_min 0,3665 N, F_max 19,812 N, γ1 0,82305 (SA und RK4-S bei beiden Δt), |µ| = 0,2921 (SA).
- Stöße auf den Kontaktorbit (SA, Endzustand nach 15 s): Phase 0: ±0,03, ±0,05, ±0,07, +0,10, +0,20, +0,30 bleiben
  im Kontakt; −0,10, −0,20, −0,30 → Hüpfzustand. Phase 0,5: ±0,03, ±0,05, −0,07, −0,10 bleiben; +0,07, +0,10,
  ±0,20, ±0,30 → Hüpfzustand. Schwelle also 0,05–0,07 m/s (Phase 0,5, positiv) bzw. 0,07–0,10 m/s (Phase 0,
  negativ), M·Δż = 0,033–0,065 N·s = 5–10 % von M·g·T.
- Rampe 2 s und 10 s (RK4-S 50/25 µs + SA-Fortsetzung): Kontaktorbit.

**Präzisierung.** Die Zusammenfassung der Gruppe („ein Stoß von etwa 0,07 N·s schaltet“) nennt das obere Ende;
bei passender Phase genügt ≤ 0,046 N·s (0,07 m/s). Im Befundtext ist die Spanne 0,03–0,07 N·s richtig.

**Reproduktion.** `timeout 540 python3 vk_insel.py sa`; `timeout 540 python3 vk_insel.py rk4 5e-5`; `timeout 540 python3 vk_insel.py rk4 2.5e-5`

---

## ENG-03 Hot-Spot (0°, 208,421°) — **eingeschränkt**: das lange Einschwingen ist ein Δt-Artefakt

**Frage.** Ist das Einschwingen (AP §8.3: 18,8 s; CSV 5–15 s: −43,46 mN, λ 74,35 %, F_max 44,1 N) eine Eigenschaft
des Modells, und ist seine Dauer „keine Eigenschaft der Konfiguration“ (Gruppe: 7–19 s je nach 1-ULP-Rundung)?

**Methode.** SA (exakt) std-Start, 120 s, mit φ₃ = 208,421 und mit φ₃ = 208,42105263157893 (np.linspace);
RK4-S bei Δt = 50 µs und 25 µs, 120 s. Kriterium wie Gruppe: Wiederkehr |Δż| < 10⁻³ m/s, |Δz| < 10⁻⁴ m
(„locker“), streng 10⁻⁸/10⁻¹⁰.

**Ergebnis.**
| Löser | v_S(5 s) | ⟨N⟩−Mg, 5–15 s | Einschwingen locker / streng |
|---|---|---|---|
| SA, φ₃ = 208,421 | −0,3744 m/s | +0,021 mN (+3,2 ppm), λ 75,0847 %, F_max 38,49 N | 4,8 s / 9,1 s |
| SA, φ₃ = 208,42105263157893 | −0,3738 m/s | −0,024 mN (−3,7 ppm) | 5,0 s / 9,3 s |
| RK4-S Δt = 50 µs | +0,2859 m/s | −43,08 mN, λ 74,31 %, F_max 44,81 N | 7,3 s / – |
| RK4-S Δt = 25 µs | −0,3743 m/s | −0,036 mN, λ 75,086 % | 4,5 s / – |
| Gruppe, Engine Δt (Quelle: hotspot_scalar_ausgabe.txt) | ż(5 s) = +0,1618 → v_S +0,2868 | −43,46 mN | 7,1 s |
| Gruppe, Engine Δt/2 (dieselbe Datei) | ż(5 s) = −0,4993 → v_S −0,3743 | +0,049 mN | 4,5 s |

Attraktor (SA): stabiler P1, |µ| = 0,7359, λ 75,0847 %, γ1 1,65798, F_max 38,474 N, v_S zu Zyklusbeginn −0,3741 m/s.

**Bewertung.** Bestätigt: Attraktor, P1, |µ|, 18,8 s nicht robust. Nicht bestätigt: „Einschwingen real“ im Sinne
einer Modelleigenschaft, die die CSV-Werte erklärt. Im exakten Modell ist der Körper bei 5 s auf dem Attraktor
(ΔV_S = 3·10⁻⁴ m/s), das 5–15-s-Fenster liefert ±4 ppm. Der lange Übergang mit v_S(5 s) ≈ +0,29 m/s tritt nur
bei Δt = 50 µs auf, in beiden Diskretisierungen (Engine und RK4-S), und verschwindet bei Δt/2. Die Streuung
7–19 s bei 1 ULP ist eine Eigenschaft der Festschritt-Trajektorie; im exakten Modell ändert 1 ULP die Dauer nur
von 4,8 auf 5,0 s (streng 9,1 → 9,3 s). Damit sind CSV-Wert −43,46 mN, λ 74,35 % und F_max 44,1 N am Hot-Spot
Diskretisierungsartefakte, nicht „Einschwingen nach 5 s“ des Modells (so auch data/README.md, Quelle).

**Reproduktion.** `timeout 540 python3 vk_hotspot.py sa`; `timeout 540 python3 vk_hotspot.py sa 208.42105263157893 _linspace`;
`timeout 540 python3 vk_hotspot.py rk4 50`; `timeout 540 python3 vk_hotspot.py rk4 25`

---

## ENG-04 Fensterreihe am Hot-Spot (L4-038) — **eingeschränkt** („widerlegt“ ist zu stark)

**Quelle geprüft.** Projektbeschreibung Aug. 2026, S. 5 (Tabelle Z. 157–160): „10 s −43,5 mN Fensterartefakt,
nicht konvergiert; 50 s −0,5 mN im Bereich der Restnumerik; 110 s −0,5 mN stabil; keine weitere Abnahme“.
Die Lage der Fenster ist dort nicht angegeben. AP v2.4 Tab. konvergenz (Z. 3535–3550): 10/30/70/150 s:
−6816/−2319/−1042/−530 ppm.

**Eigene Rechnung.**
- Zerlegung bestätigt: R = M·ΔV_S/T_w ist exakt (SA: ⟨N⟩ − Mg − R ≤ 10⁻¹³ N). Mit ΔV_S = −0,661 m/s und Q = −78 ppm
  folgt −67 380 ppm·s/T_w + Q = −6816/−2324/−1041/−527 ppm (AP-Tabelle) — Arithmetik der Gruppe richtig.
- RK4-S Δt = 50 µs, Fenster ab 5 s: −43,08 / −8,98 / −4,36 mN (Gruppe Engine: −43,46 / −9,08 / −4,45);
  nach dem Einschwingen Linksrechteck −65 … −79 ppm (−0,42 … −0,50 mN) bei R ≤ 0,3 ppm, also Q.
- RK4-S Δt = 25 µs: alle Fenster −0,02 … −0,08 mN, Q = −3 … −13 ppm.
- SA (exakt), Fenster ab 5 s: +0,021 / +0,004 / +0,002 mN.

**Bewertung.** Richtig ist: R ∝ 1/T_w, Exponent −0,95 durch konstanten Rest Q, −0,5 mN nach dem Einschwingen =
Linksrechteck-Rest bei Δt = 50 µs. Zu stark ist „L4-038 widerlegt“: (1) Die Quelle selbst nennt die −0,5 mN
„Restnumerik“ — dieselbe Deutung wie die Gruppe; bei festem Δt ist Q tatsächlich ein Plateau (keine weitere
Abnahme), nur eben ein numerisches. (2) Die Fensterlage der Quelle ist undokumentiert; Fenster nach dem
Einschwingen reproduzieren ≈ −0,5 mN. (3) Die von der Gruppe als Korrektur genannten Werte −9,08/−4,45 mN gelten
nur für die Festschritt-Trajektorie bei Δt = 50 µs; bei Δt/2 und im exakten Modell gibt es den −43,5-mN-Wert gar
nicht (ENG-03). Die Korrektur der Quelle sollte lauten: Alle Einträge der Tabelle sind Numerik (Transient der
50-µs-RK4 plus Linksrechteck-Rest), physikalisch gilt ⟨N⟩ = Mg + R mit |R| ≤ 4 ppm ab 5 s.

**Reproduktion.** wie ENG-03 → `vk_hotspot_*_ausgabe.txt`

---

## ENG-05 Festschritt-Artefakte im Hüpfbereich — **bestätigt**

**Methode.** SA-Floquet für Hot-Spot, Insel, (0°,0°) (P2), P33; Poincaré-Spanne RK4-S bei Δt und Δt/2;
Jacobi-Matrix der eigenen RK4-S-Periodenabbildung mit Differenzenschritten s·(1 mm, 0,1 m/s), s = 10⁻¹⁰ … 10⁻³.

**Ergebnis.**
- SA: Hot-Spot |µ| 0,7359; Insel-Hüpfzustand 0,7426; (0°,0°) P2 mit |µ| 0,5510 (Einschwingen 7,4 s, Tol 10⁻⁹;
  der P1-Orbit dort ist instabil, |µ| 1,355); P33-P1-Orbit |µ| 0,9187/0,6058 (reell, langsam → erklärt das RK4-Label
  „P2“), P33-P3-Orbit |µ| 0,3538, λ 71,8573 %, γ1 1,9758, F_max 50,53 N.
- RK4-S-Abbildung (andere Diskretisierung als die Engine): |µ| = 2,3098 (Insel) und 1,5645 (Hot-Spot), unabhängig
  von s zwischen 10⁻¹⁰ und 10⁻⁴; Gruppe (Engine): 2,310 und 1,565. Gleiche Werte in zwei Diskretisierungen stützen
  die Erklärung der Gruppe (Jacobi-Matrix eines glatten Stücks ohne Stoßzeit-Sensitivität).
- Poincaré-Spanne ż (50–100 s, Insel-Hüpfzustand): RK4-S 4,4–4,7·10⁻⁴ (Δt), 2,6–2,8·10⁻⁴ m/s (Δt/2); SA periodisch
  auf 10⁻⁹.
- P45-~35-%-Zustand im SA 100 s aperiodisch (λ je 10 s 35,1–35,8 %), kein Periodenlabel.

**Reproduktion.** `vk_insel.py`, `timeout 540 python3 vk_rk4map.py 50`, `timeout 300 python3 vk_sync.py`, `timeout 540 python3 vk_langlauf.py floquet33`, `timeout 540 python3 vk_langlauf.py lang`

**Einschränkung.** P30/P3-Orbits von P45 im EL (|µ| 29,5/1,24) nicht nachgerechnet.

---

## ENG-07 Symmetriegruppe und Zählung — **bestätigt**

**Methode.** Eigene Herleitung: Phasenmenge {0, φ₂, φ₃}, neue Referenz j, zwei Reihenfolgen ⇒ 6 Elemente mit
ā_B(t) = ā_A(t + τ_j). Numerisch über 200 Zufallskonfigurationen × 6 Elemente geprüft (max 3,1·10⁻¹³ m/s²).
Zählung „Punkt verletzt, wenn |Δ| > tol zu irgendeinem Bildpunkt“.

**Ergebnis.** 70 Bahnen (1×1, 18×3, 51×6). CSV, volle Gruppe: λ >0,01: 160/30, >0,1: 60/12, >0,5: 56/11,
>1: 48/9; γ1 >10⁻³: 72/14, >0,01: 60/12, >0,1: 42/8; F_min >10⁻⁴: 6/1, >10⁻³: 0; F_mean >10⁻⁴: 311/60, >10⁻³: 36/7;
F_max >0,01: 91/19, >0,1: 60/12, >1: 45/9 — identisch mit der Gruppe. Nur (12) [P1 nennt (−φ₂, φ₃−φ₂),
Quelle anweisung_pruefung.csv Z. 293]: λ >0,1: 42, >0,5: 36, >1: 32. (23)-Paare: 72 von 171 mit Δλ > 0, F_mean bei 83,
max |Δλ| 1,166 %-Pkt, max |ΔF_mean| 7,54 mN. Im SA (exakt) weichen (23)-Paare ebenfalls ab (135–144 von 171 mit
Δλ > 0, max 0,77–2,25 %-Pkt in chaotischen Zuständen): Rundungsverstärkung, kein Fehler — Deutung der Gruppe gestützt.

**Zusatz.** Mit voller Gruppe und Toleranz λ > 5 %-Pkt ergeben sich ebenfalls genau 30 Punkte (6 Bahnen); die
Aussage der Gruppe, 30 gelte „nur für Generator (12)“, ist daher nicht ausschließlich.

**Reproduktion.** `timeout 120 python3 vk_paare.py gruppe`; `timeout 120 python3 vk_grid_analyse.py` (CSV-Teil); `timeout 100 python3 vk_gridsa_analyse.py`

---

## ENG-08 Sechs verletzte Äquivalenzpaare — **eingeschränkt**

**Methode.** SA (exakt) je Mitglied std und imp, 60 s; SA mit äquivalentem Start des Partners (t0 = −s);
SA-Langläufe 100 s der aperiodischen Zustände; Floquet.

**Ergebnis (λ in %, SA 40–60 s).**
| Paar | A std / imp | B std / imp | äquivalent gestartet (B mit t0 = −s) |
|---|---|---|---|
| P6 (0,6)/(13,13) | 75,589 / 75,589 | **18,224** / 75,589 | B = A (Δż ≤ 5·10⁻¹⁴) |
| P13 (6,6)/(13,0) | 75,697 / 75,697 | **43,60 aperiodisch (100 s)** / 75,697 | B = A |
| P49 (3,7)/(16,4) | 75,632 / 75,632 | **19,025** / 75,632 | B = A |
| P45 (12,17)/(14,2) | 75,629 / 75,629 | 75,629 / 75,629 | B = A |
| P11 (0,11)/(8,8) | 75,085 (5–15 s schon 75,085) / 75,085 | 75,085 / 75,085 | B = A |
| P33 (1,16)/(3,4) | **71,93 (P3)** / 76,195 | 76,195 / **71,86 (P3)** | B = A |

Floquet SA (alle stabil): P6A-Hüpfzustand |µ| 0,7405, P6B-Tiefzustand 0,3655, P49A 0,7409, P49B-Tiefzustand 0,3691,
P45A-Hüpfzustand 0,7409, P13B imp 0,7415, P33 P3 0,3538, P33 P1 0,9187/0,6058 — gleich den EL-Werten der Gruppe.
Der ~35-%-Zustand von P45 hält sich im SA 100 s (aus RK4-S-Endzustand), ebenso P13B 43,6 % über 100 s.

**Bewertung.** Bestätigt für P6, P13, P49, P33: koexistierende Zustände, Auswahl durch die (nicht äquivalente)
Startphase; äquivalenter Start reproduziert den Partner exakt. Nicht bestätigt in der Ursachenzuordnung:
- **P11** ist kein „langsamer Transient“ des Modells: Im SA ist A schon im Fenster 5–15 s auf dem Attraktor
  (75,085 %); die CSV-Abweichung (74,35 %) stammt aus dem Δt-Artefakt der 50-µs-RK4 (ENG-03) → Ursache Numerik.
- **P45**: Im exakten Modell landen mit Standardstart beide Mitglieder im Hüpfzustand; die CSV-Verletzung ist eine
  numerische Zustandsauswahl. Multistabilität existiert (35-%-Zustand persistent), erklärt aber diese Verletzung
  nicht allein. Bilanz damit: 4 × Multistabilität mit Startauswahl, 1 × Multistabilität mit numerischer Auswahl,
  1 × Numerik.

**Reproduktion.** `for r in "0 4" "4 8" "8 12"; do timeout 540 python3 vk_paare.py lauf $r; done`; `timeout 540 python3 vk_paare.py shift`;
`timeout 400 python3 vk_paare.py floquet P45A_std:1 P6A_std:1 P6B_std:1 P49B_std:1 P49A_std:1`;
`timeout 540 python3 vk_langlauf.py lang`; `timeout 540 python3 vk_langlauf.py floquet33`

---

## ENG-09 19×19 mit drei Starts — **bestätigt** (Untergrenze im exakten Modell gestützt)

**Methode.** Eigenes RK4-S-Raster (361 Punkte, exakte Phasen) mit std, imp, ramp2, 40 s; Fenster 5–15/30–40 s.
Für jede per λ-Lücke markierte Bahn: Läufe mit kleinstem und größtem λ ab RK4-S-Endzustand 20 s mit SA fortgesetzt.
Zusätzlich das ganze Raster mit SA (std, CSV-Phasen, 20 s) und mit SA (imp, 30 s).

**Ergebnis.**
- RK4-S: λ-Spannweite über drei Starts > 1 %-Pkt an 76, > 5 an 70 Punkten; Bahnen mit Lücke > 3 %-Pkt: 18 Bahnen / 99
  Punkte; > 5: 17/93; λ > 74 % erreichbar in 40 von 70 Bahnen; Mediane std 32,27 / imp 44,86 / ramp2 27,95 %;
  Punkte λ > 74 %: 140 / 165 / 119; verletzte Punkte/Bahnen (λ > 0,5, 30–40 s): std 54/11, imp 51/9, ramp2 20/4
  (Gruppe: 54/10, 57/10, 18/3). Alle Kernzahlen der Gruppe mit anderer Diskretisierung reproduziert.
- SA-Fortsetzung: in **allen 18** markierten Bahnen bleiben zwei Zustände über 20 s getrennt (z. B. Bahn 37: 7,87 % P1
  gegen 75,86 %; Bahn 38: 24,57 % gegen 75,52 %; Bahn 5: 28,40 % P2 gegen 75,92 %). Die 99 Punkte sind damit auch im
  exakten Modell eine Untergrenze.
- SA std-Raster: Symmetrieverletzungen λ > 0,5: 57/11 (5–15 s), 52/11 (10–20 s) gegen CSV 56/11; 9 der 11 CSV-Bahnen
  sind auch im SA verletzt; nur in der CSV: Bahn 11 (Hot-Spot, Δt-Artefakt) und Bahn 45 (P45); nur im SA: 10, 16.
- SA imp-Raster (exakt, V_S(0) = 0, Fenster 20–30 s): verletzte Punkte/Bahnen λ > 0,5: **57/10** gegen SA std 52/11 (10–20 s);
  Median λ 44,86 %, Punkte λ > 74 %: 165 (Gruppe RK4: 57/10, 44,87 %, 165). Der imp-Start beseitigt Verletzungen in
  6 Bahnen (6, 13, 16, 31, 49, 57) und erzeugt neue in 5 (24, 35, 38, 56, 58).

**Bewertung.** Die P1-These „Ursache = nicht impulskonsistenter Start“ ist widerlegt (Bewertung der Gruppe
bestätigt): Die Verletzungen bestehen im exakten Modell mit Standardstart; äquivalent gestartete Partner stimmen
exakt überein; ein impulskonsistenter Start ist ebenfalls nicht äquivariant (er setzt äquivalente Punkte bei
verschiedener Anregungsphase auf V_S = 0). Ursache: Multistabilität plus nicht äquivariante Startvorschrift.

**Reproduktion.** `for st in std imp ramp2; do timeout 540 python3 vk_grid.py $st; done`; `timeout 120 python3 vk_grid_analyse.py`;
`timeout 540 python3 vk_grid_sa.py 0 9`; `timeout 540 python3 vk_grid_sa.py 9 18`;
`for c in 0 1 2 3 4 5 6 7; do timeout 540 python3 vk_grid_sa_full.py $c 8 csv; done`; `timeout 100 python3 vk_gridsa_analyse.py`;
`for c in 0 1 2 3 4 5 6 7 8 9; do timeout 540 python3 vk_grid_sa_full.py $c 10 csv imp 300; done`; `python3 vk_gridsa_imp_analyse.py`

**Einschränkung.** Zustände über 20 s (bzw. 100 s für drei) geprüft, aperiodische Tiefzustände (Bahnen 13, 44, 45, 48)
ohne Floquet; sehr lange Transienten nicht ausgeschlossen.

---

## ENG-10 Hochlauf wählt den Zustand — **eingeschränkt** (P45 numerisch fragil)

**Quelle geprüft.** Präreg-v2-Entwurf Z. 294–298: „Startstellung der Sollphasen → Rampe auf f in T_ramp mit aktiver
Phasenregelung (nie durch die synchrone Phasung) → Einschwingzeit T_e = max(T_φ, 10·max τ_m) …, τ_m = 1/(2π ζ_m f_m)“;
E2 (Z. 142–144) „Anlauf und Hysterese … Suche nach Bistabilität“ explorativ.

**Methode.** Rampe 0 → 10 Hz, (1 − cos)/2, bei festen Phasen, Start aus Ruhe; eigene Umsetzung in
Schwerpunktkoordinaten (ohne ρ′-Term), RK4-S Δt = 50 und 25 µs, 40 s; Endzustand mit SA 10 s fortgesetzt.
13 Läufe: Insel, Hot-Spot, (0°,0°), P6A/B, P13A/B, P49A/B, P45A/B, P33A/B.

**Ergebnis (SA-Fortsetzung, λ in %).**
| Lauf | 2 s/50 µs | 2 s/25 µs | 10 s/50 µs | 10 s/25 µs | Gruppe EL 2 s / 10 s |
|---|---|---|---|---|---|
| Insel | 0 | 0 | 0 | 0 | 0 / 0 |
| Hot-Spot | 75,085 | 75,085 | 75,085 | 75,085 | 75,085 / 75,085 |
| (0°,0°) | 75,787 (P2) | 75,787 | 75,787 | 75,787 | 75,787 / 75,787 |
| P6A, P6B | 18,224 | 18,224 | 18,224 | 18,224 | 18,22 / 18,22 |
| P13A, P13B | 75,697 | 75,697 | 75,697 | 75,697 | 75,70 / 75,70 |
| P49A, P49B | 19,025 | 19,025 | 19,025 | 19,025 | 19,03 / 19,03 |
| P33A, P33B | 76,195 | 76,195 | 76,195 | 76,195 | 76,19 / 76,19 |
| **P45A** | 35,2 | 34,7 | **75,63** | 35,1 | 35,3 / 75,63 |
| **P45B** | 34,7 | **75,63** | 35,6 | 34,8 | 35,2 / 35,66 |

T_e: 10τ = 10·2M/C = 0,8125 s (= 1/(2π ζ f_n) mit ζ = 0,09923, f_n = 19,741 Hz), aufgerundet 1 s (falls T_φ ≤ 1 s).
Kontaktast: Einschwingen ≤ 1,3 s (ENG-02). Liftoff-Zustände im SA nach std/imp: 1,7–1,8 s (Tiefzustände P6B, P49B)
bis 23,1 s (P33A imp) bzw. 21,2 s (P33B std); übrige Hüpfzustände 6–10 s (Toleranz 10⁻⁸ m/s).

**Bewertung.** Zustandsauswahl durch die Rampe für 11 von 13 Läufen robust über zwei Rampenzeiten, zwei Schrittweiten
und zwei Formulierungen bestätigt. Für P45 ist die Aussage der Gruppe („2 s → ~35 %, 10 s → A 75,63 %, B 35,66 %“) nicht
robust: Das Ergebnis kippt mit Δt (bei 25 µs/2 s geht B in den Hüpfzustand, bei 25 µs/10 s A in den 35-%-Zustand).
Die Schlussfolgerung „T_e reicht nur im Kontaktast“ ist gestützt. Die Einschwingspannen nach Rampe (3–11 s / 8–23 s)
wurden nicht eigenständig nachgemessen.

**Reproduktion.** `for tr in 2 10; do for dt in 50 25; do timeout 540 python3 vk_rampe.py $tr $dt; done; done` → `vk_rampe_*_ausgabe.txt`

**Einschränkung.** Idealer Hochlauf (keine Phasenregelfehler, μ = 1); nur zwei Rampenzeiten.

---

## Zusatzbefunde

1. **Hot-Spot-Werte der CSV sind Diskretisierungsartefakte** (ENG-03): ⟨N⟩−Mg −43,46 mN, λ 74,35 %, F_max 44,10 N
   (CSV) gegen +0,02 mN, 75,0847 %, 38,49 N im exakten Modell im selben Fenster 5–15 s. Gilt ebenso für den
   (23)-Partner (208,421°, 0°) mit −43,19 mN.
2. **Exaktes 19×19-Raster (SA, Standardstart):** Kontaktpunkte der CSV exakt (12 Punkte, |ΔF_min| ≤ 1,9·10⁻⁵ N,
   |Δγ1| ≤ 3,3·10⁻⁷). Im Liftoff-Bereich weichen 8 Punkte um > 1 %-Pkt und 3 um > 5 %-Pkt in λ ab ((2,14), (14,2):
   CSV 35,4 → SA 75,6 %; (3,3): 76,2 → 70,0 %), 6 Punkte um > 10 mN in ⟨N⟩, 9 um > 1 N in F_max. Größter Randterm
   im exakten Modell bei 5–15 s: (16,15)/(15,16) mit −41,6 mN (P3-Orbit, Fenster ohne ganze Periode; CSV −41,4 mN).
3. **Rampenauswahl bei P45 numerisch fragil** (ENG-10).
4. **Wertebereich nicht robust:** Im exakten Modell (SA, Standardstart) landet (3,3) = (56,842°, 56,842°) in einem
   aperiodischen Zustand mit λ 70,7 %, γ1 1,999, F_max 51,6 N (30–40 s); CSV und alle RK4-Raster zeigen dort 76,2 %.
   Damit liegen γ1 und F_max über den von der Gruppe als „robust“ bezeichneten Maxima (γ1 ≤ 1,979, F_max 50,4–50,6 N,
   A 6,90–6,93; SA 10–20 s: A 7,07).
5. Die RK4-Abbildungsmultiplikatoren der Gruppe (2,310/1,565) sind diskretisierungsunabhängig reproduzierbar (RK4-S
   2,3098/1,5645): systematische Eigenschaft der Festschritt-Abbildung, nicht der Engine-Arithmetik.

## Nachtrag imp-Raster (exaktes Modell)

`timeout 100 python3 vk_gridsa_imp_analyse.py` → `vk_gridsa_imp_analyse_ausgabe.txt`:
SA std (10–20 s) 52 Punkte/11 Bahnen, SA imp (20–30 s) 57/10 verletzt (λ > 0,5 %-Pkt); gemeinsam verletzt: Bahnen 10, 21,
28, 33, 44. |λ_std − λ_imp| > 1 %-Pkt an 44, > 5 an 38 Punkten; Bahnen mit ≥ 2 Zustandsgruppen allein aus SA std + SA imp:
14 Bahnen / 75 Punkte (mit RK4-S und drei Starts: 18/99, alle 18 im SA bestätigt).

## Abschlusskontrolle

`find ../../../code docs -name __pycache__` → leer
(PYTHONDONTWRITEBYTECODE=1 in allen Läufen). Keine Datei außerhalb dieses Ordners angelegt oder geändert.
