# P2 · Prüfgruppe „engine“ · Protokoll

> **Vermerk zur Übernahme (04.10.2026).** Protokoll aus der Gesamtprojektanalyse 10/2026, Stand 02.10.2026, unverändert bis auf Pfade und Quellenangaben. Geprüft wurde der Repository-Stand `cd7be6a` (28.09.2026) mit der Präregistrierung v2 vom 25./28.09.2026; die späteren Änderungen aus PR #13 und PR #14 (unter anderem Präregistrierung v2 mit Arbeitsfestlegungen, `code/auslegung.py`, `code/ereignisloeser.py`) sind nicht eingearbeitet. Alle Zahlen sind Simulation oder Analytik, keine Messdaten. Verweise wie „L1a-019“, „P1 §3“ oder „B01–B14“ zeigen auf Arbeitsdokumente der Analyse, die nicht im Repository liegen. Quellen außerhalb des Repositorys sind als „(lokaler Bestand, nicht im Repository)“ gekennzeichnet. Startbefehle und Grenzen je Gruppe: [`rechnungen/README.md`](../README.md).

Stand 02.10.2026. Thema: Startabhängigkeit, repräsentative Punkte, Symmetrieverletzungen der 19×19-Karte,
Inseln mit halbiertem Δt. Alle Zahlen stammen aus eigener Rechnung in diesem Ordner, sofern nicht als
„Quelle“ gekennzeichnet. Kein Repo-Code wurde verändert; `finesweep.py`, `linear_solver.py`,
`pcmms_v3a_phasen_sweep.py` und das Burn-in-Skript vom 13.09. wurden nur importiert.

**Reproduktion (Vorspann für alle Befehle):**

```
cd rechnungen/engine
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../../code
```

## 0 Werkzeuge

| Datei | Zweck |
|---|---|
| `eng.py` | Prüf-Engine, über Läufe vektorisiert. Die Arithmetik ist gleich wie bei `finesweep.run` (RK4, Kontaktkraft aus Stufe 1, t = t0 + i·Δt). Dazu kommen frei wählbarer Anfangszustand und Startzeit, eine Frequenzrampe, zyklusweise Akkumulatoren (Linksrechteck, RK4-gewichtet, Momente, min, max, λ) und ein Poincaré-Schnitt je Zyklus. |
| `validate_eng.py` | Abgleich mit `finesweep.run` und `data/sweep_19x19.csv`. Ergebnis: mit `finesweep` auf 6 Stellen identisch. Gegen die CSV identisch an Kontakt- und liftoffarmen Punkten. An Punkten mit Einschwingen oder Chaos weicht sie ab, weil die skalare Engine `math.sin`, die vektorisierte `np.sin` verwendet (z. B. (0°, 0°): F_mean 6,376417 gegen 6,376243 N). |
| `run_seg.py`, `make_specs.py`, `make_spec_transfer.py`, `make_spec_grid.py` | Läufe als JSON-Spezifikation, segmentweise Fortsetzung. Die Fortsetzung ist bitgenau geprüft. |
| `analyse_runs.py` | Fenster-Kenngrößen, Periodizität, Einschwingzeit, Blockstatistik |
| `orbit.py` | Newton auf die diskrete RK4-Periodenabbildung (Orbitstart) |
| `el_solver.py` | **Ereignislokalisierender Löser (EL).** Gleiches Modell wie die Engine. Kontakt gilt genau dann, wenn min(−Kz−Cż, −z) > 0. DOP853 mit rtol 1e-11 und atol 1e-14, stückweise zwischen den Knicken der Anregung. Die Momente ∫N^p dt laufen als Zusatzzustände mit. Ein Schutz gegen übersehene Vorzeichenwechsel prüft im 10-µs-Raster nach (`n_fix`; nur in den P45-Läufen > 0). Dazu kommen die Rampen-Variante `ELRamp` und Newton auf die EL-Periodenabbildung (Floquet-Multiplikatoren mit Stoßzeitpunkten). |
| `hotspot_scalar.py`, `burnin_repro.py` | Skalare Referenz-Engine (Arithmetik der CSV) und Reproduktion des adaptiven Burn-in vom 13.09. |

Startdefinitionen (Aufgabe 1):
- **std**: z = −Mg/K, ż = 0, t0 = 0 (Engine).
- **imp** (impulskonsistent): z = −Mg/K, ż(0) = −(1/3)·Σ e′(−τ_k). Damit ist v_S(0) = 0 im Laborsystem.
- **ramp2 / ramp10**: Frequenzhochlauf 0 → 10 Hz in 2 s bzw. 10 s bei festen Phasen, Start aus Ruhe. Die Module stehen, v_S(0) = 0 exakt. Das ist das Präreg-Anlaufprotokoll ohne Regelfehler.
- **orb**: Fixpunkt der Periodenabbildung (Newton) bei Dauerkontakt. Für Hüpfzustände: EL-Newton ab dem Endzustand des RK4-Laufs.
- **stdshift**: Standardzustand, aber t0 = −s bzw. +s. Damit ist der Partnerpunkt äquivalent gestartet.
- **vom Partner**: Endzustand des Partnerlaufs bei 100 s, zeitverschoben um s.

---

## ENG-01 Koordinaten der Engine und Impuls des Standardstarts

**Frage.** Was ist z, wie geht die Modulbeschleunigung ein, wie ist der Schwerpunkt definiert? Stimmt
v_CoM(0) = 0,24 m/s (P1, L2-004)?

**Methode.** Herleitung aus der Bewegungsgleichung (`pcmms_v3a_phasen_sweep.py`, Kopf und `rhs()`):
M z̈ = −Mg + N − (M/3)Σ ë(t−τ_k). Dazu analytische Profilgeschwindigkeit und eine numerische Impulsbilanz
über die Zyklen 2–12 (`impuls_start.py`).

**Ergebnis (eigene Rechnung).**
- z ist die Lage des masselosen Rahmens bzw. Auflagerpunkts; z < 0 heißt, die Feder ist eingedrückt. Die drei Module (je M/3) sitzen relativ zum Rahmen bei e(t−τ_k). Schwerpunkt: z_S = z + (1/3)Σ e(t−τ_k). Damit gilt M z̈_S = −Mg + N.
- e′(0) = RTOP·π/(THOLD·T) = 0,24166 m/s; das ist die Spitzengeschwindigkeit bei Profilphase 0. Standardstart: v_S(0) = (1/3)Σ e′(−τ_k).
  - (0°, 0°): +0,2417 m/s, Anfangsimpuls 157,1 mN·s = 24,6 % von M·g·T, ½Mv² = 18,98 mJ (statische Federenergie: 2,03 mJ)
  - (0°, 208,421°): +0,1250
  - (120°, 240°): −0,0023
  - (35°, 116°): +0,0543
  - (113,684°, 227,368°): −0,0130
  - (100°, 240°): +0,0131 m/s
  - 1°-Raster: Maximum +0,2417, Minimum −0,0806, Median von |v_S(0)| = 0,0806 m/s.
- Impulsbilanz: M Δv_S = ∫(N_RK4 − Mg)dt auf 3,4·10⁻¹³ N·s genau bei (0°, 0°), 1,8·10⁻⁷ beim Hot-Spot und 3,9·10⁻¹⁵ bei der Triphasik. Das Linksrechteck weicht bei (0°, 0°) um 2,6·10⁻⁴ N·s ab.
- Bewertung: L2-004 **bestätigt**. Die Tabelle „Numerik“ im AP v2.4 nennt den Start „statisches Gleichgewicht“; das trifft nur auf die Feder zu, nicht auf den Schwerpunkt.

**Reproduktion.** `timeout 300 python3 impuls_start.py` → `impuls_start_ausgabe.txt`

**Einschränkungen.** μ = 1 (masseloser Rahmen) wie in der Engine. Bei μ < 1 ändert sich die Aufteilung.

---

## ENG-02 Startvarianten und Orbitstart im Dauerkontakt

**Frage.** Hängen Dauerkontaktpunkte vom Start ab? Lässt sich direkt auf dem periodischen Orbit starten?

**Methode.**
- Newton auf die RK4-Periodenabbildung mit zentralen Differenzen (`orbit.py`) und Vergleich mit `linear_solver.orbit_state`.
- 100-s-Läufe für std, imp, ramp2, ramp10 und orb bei (120°, 240°), (113,684°, 227,368°) und (100°, 240°), bei Δt und Δt/2.
- EL-Läufe von 30 s.
- Stoßtests mit EL: Δż bis ±3 m/s bei zwei Zyklusphasen, dazu die drei Präreg-Pilotkonfigurationen (`el_kick.py`).

**Ergebnis.**
- Newton konvergiert in einem Schritt (die Abbildung ist affin), Residuum ≤ 3·10⁻¹⁶ m/s. Abstand zur linearen Lösung: ≤ 2,9·10⁻¹⁰ m und 2,8·10⁻⁸ m/s bei Δt, ≤ 3·10⁻¹¹ m und 4·10⁻⁹ m/s bei Δt/2.
- Floquet-Multiplikatoren |µ| = 0,2921 = exp(−C·T/2M) = exp(−1,2308); das ist auch analytisch so.
- Alle Starts enden auf demselben Orbit. Einschwingzeit (|Δż| < 10⁻⁶ m/s) nach std/imp 0,8–0,9 s (RK4), 1,2 s im EL bei Toleranz 10⁻⁸. Nach der Rampe ≤ 0,7 s nach Rampenende.
- Kenngrößen identisch über Starts, Δt, Δt/2 und EL:

| Punkt | γ1 | F_min | F_max |
|---|---|---|---|
| Triphasik | 0,066794 | 5,3304 N | 7,4919 N |
| (113,684°, 227,368°) | −0,27297 | 2,8821 N | 9,4622 N |
| (100°, 240°) | −0,34409 | 0,7677 N | 10,955 N |

- F_mean − Mg: Linksrechteck ≤ 0,06 ppm (Δt) und ≤ 0,01 ppm (Δt/2); RK4-gewichtet ≤ 6·10⁻¹⁰ ppm.
- Stöße bis ±3 m/s: Hauptgebiet, Rand (100°, 240°), Triphasik und die Piloten (110°, 250°), (130°, 230°), (110°, 252°) kehren immer in den Kontakt zurück. Das bestätigt AP B.6 bzw. Präreg A3 („Hauptgebiete monostabil“) für diese Stichproben.

**Reproduktion.**
- `timeout 540 python3 orbit.py`
- `timeout 300 python3 make_specs.py`, dann `for s in 0 1; do timeout 540 python3 run_seg.py spec_rep_dt.json run_rep_dt $s 500; done` und `for s in 0 1 2 3; do timeout 540 python3 run_seg.py spec_dt2.json run_dt2 $s 250; done`
- `python3 analyse_runs.py spec_rep_dt.json run_rep_dt tab_rep_dt.csv`, `python3 report_rep.py` → `rep_tabelle.csv`
- `timeout 540 python3 el_kick.py 0 2` (und `2 4`, `4 7`) → `el_kick_ausgabe.txt`

**Einschränkungen.** Nur Referenzparameter. Die Stoßtests sind stichprobenhaft (zwei Phasen, wenige Beträge).

---

## ENG-03 Hot-Spot (0°, 208,421°): Einschwingen ist real, seine Dauer ist nicht robust

**Frage.** Quelle AP v2.4 §8.3: Übergang 18,8 s, danach Periode 1, Randterm −2 ppm (L1a-043, L2-044); L1b-041.

**Methode.**
- Skalare Referenz-Engine (Arithmetik der CSV), 120 s bei Δt und Δt/2 (`hotspot_scalar.py`).
- Reproduktion des Burn-in-Skripts (`burnin_repro.py`).
- Numpy-Engine mit vier Starts.
- EL mit std, imp und Rampe, Floquet-Analyse.

**Ergebnis.**
- CSV 5–15 s exakt reproduziert: −43,4588 mN (−6815,5 ppm), λ 74,3490 %, γ1 1,6720, F_max 44,104 N. Zerlegung: R = −6737,7 ppm, Q = −77,8 ppm. Δż zwischen 5 s und Fensterende = −0,6610 m/s für Enden bei 15, 55 und 115 s (ż(5 s) = +0,1618, Ende −0,4991 m/s). Damit ist L1b-041 **bestätigt**.
- Einschwingende (Wiederkehr |Δż| < 10⁻³ m/s, |Δz| < 10⁻⁴ m, bis Laufende gültig):

| Variante | Einschwingende |
|---|---|
| skalar, φ₃ = 208,421 | 7,1 s |
| skalar, φ₃ = 208,42105263157896 | 9,7 s |
| Burn-in-Skript, φ₃ = 208,42105263157893 (np.linspace, 1 ULP kleiner) | Fensteröffnung 18,8 s (reproduziert; δ −64,7, R −2,0, Q −62,8 ppm) |
| numpy, φ₃ = 208,421 | 7,4 s |
| numpy, exakte Phase | 16,6 s |
| Δt/2 | 4,5 s |
| EL, streng periodisch | 9,1 s (std), 12,7 s (imp), 12,3 s (Rampe 2 s), 18,0 s (Rampe 10 s) |

- Der Attraktor ist in allen Varianten derselbe: λ 75,0847 % (EL) bzw. 75,08–75,09 % (RK4), γ1 1,65798, F_max 38,47–38,49 N. Er ist ein stabiler P1-Orbit, EL-Multiplikatoren |µ| = 0,7359.
- Bewertung:
  - L1a-043 **teilweise**: Einschwingen und P1 ja. Die „18,8 s“ sind aber keine Eigenschaft der Konfiguration; die Dauer ändert sich schon bei 1 ULP Phasenänderung (chaotischer Transient).
  - L2-044 bestätigt (gleiche Zahlen).

**Reproduktion.** `timeout 540 python3 hotspot_scalar.py 0 208.421 120`, `timeout 540 python3 hotspot_scalar.py 0 208.42105263157896 60`, `timeout 540 python3 burnin_repro.py`, `timeout 540 python3 el_check.py rep 300 0 16`

**Einschränkungen.** Das Kriterium „locker“ hat eine willkürliche Toleranz. Bei RK4 liegt die Festschritt-Streuung (ENG-05) nahe an dieser Toleranz.

---

## ENG-04 Fensterreihe am Hot-Spot (L4-038) und Quadraturrest

**Frage.** Quelle: Projektbeschreibung Aug. 2026, S. 5: „10 s −43,5 mN; 50 s −0,5 mN; 110 s −0,5 mN, stabil“.

**Methode.** Skalare Engine, Fenster ab 5 s mit 10, 50 und 110 s Länge, dazu Fenster nach dem Einschwingen. Zerlegung in R = M·Δv_S/T_w und Q = Linksrechteck − RK4-gewichtet.

**Ergebnis.**
- Fenster ab 5 s:

| Fensterlänge | ⟨N⟩ − Mg | δ | R |
|---|---|---|---|
| 10 s | −43,46 mN | −6815,5 ppm | −6737,7 ppm |
| 50 s | −9,08 mN | −1424,2 ppm | −1347,6 ppm |
| 110 s | −4,45 mN | −697,6 ppm | −612,6 ppm |

- R fällt exakt mit T_w⁻¹. Der Exponent −0,95 von δ entsteht durch Q ≈ −77…−85 ppm; das bestätigt die P1-These zum Randterm.
- Die Tabelle „Konvergenz“ im AP v2.4 (30/70/150 s: −2319/−1042/−530 ppm) passt zu R = −67 380 ppm·s/T_w + Q (−78 ppm). Daraus folgen −2324, −1041 und −527 ppm.
- Fenster nach dem Einschwingen (Δt): δ = −54…−100 ppm (−0,34…−0,64 mN), R = ±0,6 ppm. δ ist also der Quadraturrest Q des Linksrechtecks. Bei Δt/2 liegt Q zwischen −6,3 und +4,2 ppm. N_RK4 − Mg − R = 1,8·10⁻⁷ N (Δt) bzw. 4,8·10⁻⁸ N (Δt/2). Im EL ist ⟨N⟩ − Mg − R = 2·10⁻¹² N.
- Bewertung: L4-038 **widerlegt** für Fenster ab 5 s. Die −0,5 mN entsprechen nur Fenstern nach dem Einschwingen. Dort sind sie Δt-abhängige Quadratur und kein stabiles Plateau.

**Reproduktion.** `timeout 540 python3 hotspot_scalar.py 0 208.421 120` → `hotspot_scalar_ausgabe.txt`

**Einschränkungen.** Die Rechenweise der Projektbeschreibung ist nicht dokumentiert, vermutlich ältere Engine. Der Befund gilt für die Repo-Engine.

---

## ENG-05 Festschritt-Artefakte im Hüpfbereich: Periodenlabels und Stabilität

**Frage.** Sind die Perioden und Einschwingzeiten der RK4-Engine im Liftoff-Bereich numerisch belastbar?

**Methode.**
- Streuung des Poincaré-Schnitts über 50–100 s bei Δt und Δt/2 (`poincare_streuung.py`).
- Newton auf die RK4-Abbildung (`orbit_hopping.py`) gegen Newton auf die EL-Abbildung (`el_floquet*.py`).

**Ergebnis.**
- Hüpfzustände (λ ≈ 75–76 %): Streuung von ż zu Zyklusbeginn 2,6–5,8·10⁻⁴ m/s (Δt) gegen 1,8–2,8·10⁻⁴ m/s (Δt/2), also etwa proportional zu Δt. Im EL beträgt sie ≤ 10⁻¹¹ m/s, die Orbits sind exakt periodisch.
- (0°, 0°): RK4 „locker“ P2/P6/P4 je nach Start mit Einschwingzeit 47–79 s; bei Δt/2 P2 nach 2,2–3,7 s; im EL streng P2 nach 6,8 s, |µ| = 0,551.
- Die RK4-Abbildung hat Fixpunkte mit |µ| = 1,565 (Hot-Spot), 2,310 (Insel, Hüpfzustand) und 4,956 (synchron, P2). Diese scheinbare Instabilität ist ein Artefakt: Die Jacobi-Matrix enthält die Stoßzeitpunkte nicht. Im EL sind dieselben Zustände stabil: 0,7359, 0,7426, 0,5510.
- P45 (Bahn (12,17)/(14,2)): RK4 findet exakt P30 bzw. P3 (Streuung 10⁻¹²). Im EL existieren diese Orbits, sind aber instabil (|µ| = 29,5 bzw. 1,239). Der EL-Lauf ab dem RK4-Zustand bleibt aperiodisch bei λ ≈ 34,9–35,6 %, ein chaotischer Zustand.
- P33B ist im RK4 „P2“, im EL aber P1 (λ 76,1946 %).
- Bewertung (**neu**): Periodenlabels, „P3/P6/P30“ und Einschwingzeiten aus der Festschritt-RK4 sind im Liftoff-Bereich nicht belastbar. Das stützt Anweisung §5.6 (ereignislokalisierender Löser nötig). Die Kenngrößen λ, γ1 und F_max der Hüpfzustände stimmen dagegen zwischen RK4 und EL auf ≤ 0,01 %-Pkt bzw. 10⁻³ bzw. 0,03 N überein.

**Reproduktion.** `python3 poincare_streuung.py spec_rep_dt.json run_rep_dt`, `timeout 400 python3 orbit_hopping.py`, `timeout 540 python3 el_floquet.py`, `timeout 540 python3 el_floquet_p33.py`

**Einschränkungen.**
- Der EL ist nicht gegen einen zweiten unabhängigen Ereignislöser validiert. Er stimmt aber mit RK4 im Kontakt auf 10⁻⁵ überein und mit der linearen Lösung exakt.
- Bei P45 griff der Nachprüfschutz 3–6-mal (streifende Kontakte).

---

## ENG-06 Satelliteninsel (35°, 116°) mit Δt/2 (Aufgabe 4) und Stoßfestigkeit

**Frage.** P1 fand den Δt/2-Beleg nur im Docstring von `linear_solver.py`. Bestehen beide Zustände bei Δt/2 und ohne Festschritt-Artefakt?

**Methode.** 100 s RK4 bei Δt und Δt/2 mit std, imp, ramp2, ramp10 und orb; EL mit std, imp, orb und Rampe; Floquet-Multiplikatoren; Stöße (EL).

**Ergebnis.**
- Hüpfzustand (std, imp):

| Löser | λ | F_max | γ1 |
|---|---|---|---|
| Δt | 75,815 % | 39,495 N | 1,6981 |
| Δt/2 | 75,814 % | 39,487 N | 1,6981 |
| EL | 75,8154 % | 39,473 N | 1,69813 |

  Im EL ist der Zustand stabil mit |µ| = 0,7426.
- Kontaktorbit (orb, ramp2, ramp10, EL-Rampe 2 s und 10 s): λ 0, F_min 0,3665 N, F_max 19,81 N, γ1 0,82305, |µ| = 0,2921.
- Docstring (200 s): 75,82/75,81 %, 39,49/39,48 N, Orbit 19,81 N. **Bestätigt.**
- Stöße auf den Kontaktorbit: Bei |Δż| ≤ 0,05 m/s bleibt er bestehen. Ab 0,10 m/s hängt das Ergebnis von Phase und Vorzeichen ab: Bei t0 = 0 führt −0,10 in den Hüpfzustand, +0,10 und +0,30 nicht. Bei t0 = 0,05 s führen +0,10 und +0,30 in den Hüpfzustand, −0,10 nicht. Die Grenze des Einzugsgebiets ist also phasenabhängig und nicht monoton. Das Einzugsgebiet ist klein: M·Δż ≈ 0,03–0,07 N·s, also 5–10 % von M·g·T.
- Neu: Der Frequenzhochlauf wählt an der Insel den Kontaktorbit, der Standardstart den Hüpfzustand.

**Reproduktion.** `tab_rep_dt.csv`, `tab_dt2.csv`, `el_check.py rep`, `el_floquet.py`, `timeout 540 python3 el_ramp_check.py 0 7`, `el_kick.py 0 2`

**Einschränkungen.** Nur ein Inselpunkt; die Lage der übrigen fünf Inseln wurde nicht nachgeprüft.

---

## ENG-07 Symmetrie der Phasenebene: exakte Äquivalenzen und Zählung in der CSV

**Herleitung.** Bei identischen Modulen ist eine Konfiguration bis auf Umbenennung und Zeitverschiebung bestimmt.
Wird Modul j die neue Referenz, gilt ā_B(t) = ā_A(t + τ_j). Die Gruppe S₃ wirkt auf (φ₂, φ₃) mod 360° so:

| Element | Abbildung | Zeitverschiebung s |
|---|---|---|
| (23) | (φ₃, φ₂) | keine |
| (12) | (−φ₂, φ₃−φ₂) | τ₂ |
| (13) | (φ₂−φ₃, −φ₃) | τ₃ |
| (123) | (φ₃−φ₂, −φ₂) | τ₂ |
| (132) | (−φ₃, φ₂−φ₃) | τ₃ |

Numerisch geprüft: Gruppe geschlossen; ā_B(t) − ā_A(t+s) ≤ 5·10⁻¹⁴ m/s².

- Nur die Vertauschung (23) lässt ODE **und** Standardstart unverändert. Alle anderen Elemente starten die äquivalenten Punkte bei verschiedener Anregungsphase.
- Eine Spiegelung (φ → −φ) ist wegen der Dämpfung keine Symmetrie (Präreg A7 korrekt).
- 19er-Raster: 70 Bahnen, davon 1 der Größe 1, 18 der Größe 3 und 51 der Größe 6.

**Ergebnis (CSV).**
- (23) allein: 84 von 171 Paaren weichen bei CSV-Auflösung ab, maximal |ΔF_mean| 7,5 mN, |Δλ| 1,17 %-Pkt, |Δγ1| 0,035, alle bei λ ≥ 27,4 %. Da ODE und Start bis auf die Summationsreihenfolge gleich sind, ist das verstärkte Rundung (AP §8.4: „numerischer Ursprung“ – korrekt).
- Volle Gruppe, verletzte Punkte/Bahnen:

| Observable | Toleranz → Punkte/Bahnen |
|---|---|
| λ | >0,01 %-Pkt: 160/30; >0,1: 60/12; >0,5: 56/11; >1: 48/9 |
| γ1 | >10⁻⁴: 150/29; >10⁻³: 72/14; >0,01: 60/12; >0,1: 42/8 |
| F_min | >10⁻⁴ N: 6/1; >10⁻³ N: 0 |
| F_mean | >10⁻⁵ N: 321/62; >10⁻⁴: 311/60; >10⁻³: 36/7 |
| F_max | >10⁻³ N: 272/54; >0,01: 91/19; >0,1: 60/12; >1: 45/9 |

- P1 („30 von 361“, nur Generator (12)) ist reproduzierbar mit Toleranz γ1 0,05 (30), A 0,1 (30) oder F_max 0,5–1 N (30). Bei λ > 0,1 %-Pkt sind es 42. Die Zahl hängt von Generator und Toleranz ab: **teilweise**.

**Reproduktion.** `timeout 540 python3 sym_count.py` → `sym_count_19x19_ausgabe.txt`, `sym_bahnen_19x19.csv`

**Einschränkungen.** Die CSV rundet die Phasen auf 3 Stellen; Äquivalenzen gelten dadurch nur bis 0,001°.

---

## ENG-08 Sechs verletzte Äquivalenzpaare nachgerechnet

**Methode.** Je Paar (A, B = gA) wurden folgende Läufe gerechnet:
- 100 s RK4 mit stdR (CSV-Phasen), std (exakte Phasen i·360/19), imp und ramp2;
- stdshift und Start vom Partnerorbit;
- stdR bei Δt/2;
- EL mit std, imp, Rampe 2 s und 10 s, Floquet-Analyse.

Kennzahl: λ im Fenster 50–100 s (RK4) bzw. in den letzten 10–13 s (EL). Tabelle: `paare_tabelle.csv`.

**Ergebnis (λ in %).**

| Paar | CSV A/B | Lauf 50–100 s | stdshift / vom Partner | EL | Ursache |
|---|---|---|---|---|---|
| P6 (0,6)/(13,13) | 75,59 / 18,20 | A: std 75,59, ramp 18,25; B: std 18,20, imp 75,59; bei Δt/2 gleich | reproduzieren den Partner, halten dessen Zustand | P1 75,59 (|µ| 0,741) und P1 18,22 (|µ| 0,366), beide stabil; Rampe → 18,22 | **Multistabilität** |
| P13 (6,6)/(13,0) | 75,70 / 43,60 | A: alle Starts 75,70; B: std 43,7 (aperiodisch, Blöcke 43,6–43,9), imp/ramp 75,70 | A vom Partner hält 43,69 | B std 43,73 aperiodisch; Hüpfen stabil (|µ| 0,742) | **Multistabilität** |
| P49 (3,7)/(16,4) | 75,63 / 19,00 | wie P6 (ramp → 19,05/19,00) | wie P6 | 75,63 (|µ| 0,741) und 19,03 (|µ| 0,369); Rampe → 19,03 | **Multistabilität** |
| P45 (12,17)/(14,2) | 75,63 / 35,42 | A: stdR 75,63 (100 s), std 35,19 („P30“), imp 75,63, ramp 35,09; B: std 34,77 („P3“), imp 75,63 | vom Partner gehalten; bei Δt/2 wählt stdR für **beide** 75,63 | Hüpfen stabil (|µ| 0,741); ~35-%-Zustand aperiodisch, P3/P30 instabil; Rampe 2 s → 35,3/35,2, Rampe 10 s → A 75,63, B 35,66 | **Multistabilität**; Auswahl numerisch fragil |
| P11 (0,11)/(8,8) | 74,35 / 75,09 | alle Starts 75,09 | – | alle Starts 75,085, P1 | **langsamer Transient** |
| P33 (1,16)/(3,4) | 71,94 / 76,20 | A: std 71,85, imp/ramp 76,19; B: std 76,20, imp 71,85 | – | P3 71,857 % (γ1 1,976, F_max 50,53, |µ| 0,354) und P1 76,195 % (F_max 39,99), beide stabil | **Multistabilität** |

Zu P11: Mit 5–15 s ist das Fenster bei A noch im Einschwingen (std exakt: Einschwingen 16,6 s, stdshift 14,4 s).

Zu P33: Der A_max-Zustand des AP ist der P3-Orbit.

- **stdshift** (äquivalent gestartet) reproduziert in allen sechs Paaren den Zustand des Partners, z. B. P45B_stdshift: λ 35,19 %, P30 ab 22,4 s, gleich wie P45A_std. Die Verletzungen entstehen also allein durch die unterschiedliche Startphase. Ein längerer Burn-in ändert nichts: λ bei 5–15 s gleich λ bei 50–100 s, außer bei P11 und P45A_std.
- Ursachen: Multistabilität in 5 Paaren (P6, P13, P49, P45, P33), langsamer Transient in 1 (P11). Numerik: Die Zustandsauswahl bei P45 kippt mit Δt und Arithmetik (CSV 75,6, exakt 35,2, Δt/2 75,6, EL 75,6). Die Zustände selbst sind im EL bestätigt.

**Reproduktion.**
- `for s in 0 1; do timeout 540 python3 run_seg.py spec_pairs_dt.json run_pairs_dt $s 500; done`
- `python3 make_spec_transfer.py`, `for s in 0 1; do timeout 540 python3 run_seg.py spec_transfer_dt.json run_transfer_dt $s 500; done`
- `python3 analyse_runs.py …`, `timeout 540 python3 el_check.py pairs 400 0 12` (und `12 24`), `el_check.py rk4 400 0 14`
- `python3 report_pairs.py`

**Einschränkungen.**
- Für P13 wurde die Stabilität des 43,7-%-Zustands im EL nur als Fortbestand über 40 s geprüft (aperiodisch, kein Floquet).
- Für P45 ist ein sehr langer Transient des ~35-%-Zustands nicht ausgeschlossen.

---

## ENG-09 19×19 mit drei Starts: Ausmaß der Startabhängigkeit

**Methode.** 361 Punkte mit exakten Phasen × {std, imp, ramp2}, je 40 s, Fenster 5–15 s und 30–40 s (`analyse_grid.py`, `grid_wertebereich.py`). Je Bahn liefern Mitglieder × Starts bis zu 18 Anfangsbedingungen derselben Konfiguration.

**Ergebnis.**
- std (exakte Phasen, numpy) 5–15 s gegen CSV: 24 Punkte weichen in λ um mehr als 0,01 %-Pkt ab, 5 um mehr als 1 %-Pkt, z. B. (12,17) mit 75,63 → 35,71 %.
- Längerer Burn-in (std, 5–15 → 30–40 s): |Δλ| > 0,5 %-Pkt an nur 6 Punkten. Die Symmetrieverletzungen bleiben (λ > 0,5 %-Pkt: 55 → 54 Punkte; Bahnen 11 → 10). Mit imp: 57 Punkte/10 Bahnen. Mit ramp2: 18 Punkte/3 Bahnen (Bahnen 28, 35, 44).
- λ-Spannweite über die drei Starts > 1 %-Pkt an 76 von 361 Punkten (21,1 %), > 5 %-Pkt an 70.
- Bahnen mit mindestens zwei Zustandsgruppen (λ-Lücke > 3 %-Pkt): **18 von 70 Bahnen = 99 von 361 Rasterpunkten (27,4 %)**. Mit Lücke > 5 %-Pkt: 17 Bahnen bzw. 93 Punkte. Das ist eine Untergrenze bei 3 Starts. In 40 von 70 Bahnen wird der Hüpfzustand (λ > 74 %) erreicht.
- Kartenstatistik je Start (30–40 s; CSV 32,27 / 0,866 / 2,445 / 142):

| Start | λ-Median | γ1-Median | A-Median | Punkte mit λ > 74 % |
|---|---|---|---|---|
| std | 32,27 % | 0,866 | 2,445 | 140 |
| imp | 44,87 % | 1,012 | 2,696 | 165 |
| ramp2 | 27,95 % | 0,785 | 2,377 | 119 |

  Die Maxima sind robust: λ 76,2 %, A 6,90–6,93, F_max 50,4–50,6 N. Die 36 Punkte mit negativer Schiefe bleiben in allen Varianten gleich.
- Bewertung: P1 §3.3 („Ursache: nicht impulskonsistenter Start“) **widerlegt** als Ursache. Der impulskonsistente Start beseitigt weder Startabhängigkeit noch Verletzungen. Die Ursache ist Multistabilität, und die Startphase wählt den Zustand aus.

**Reproduktion.** `python3 make_spec_grid.py`; `for st in std imp ramp2; do for s in 0 1; do timeout 540 python3 run_seg.py spec_grid_$st.json run_grid_$st $s 200; done; done`; `timeout 300 python3 analyse_grid.py`; `timeout 200 python3 grid_wertebereich.py`

**Einschränkungen.**
- Festschritt-RK4 bei Δt; einzelne Zustände können Artefakte sein (vgl. P45). Die Trennung Hüpfzustand gegen niedriger Zustand ist an 5 Paaren mit EL bestätigt.
- Chaotische Zustände schwanken über 10 s um bis zu ~2,5 %-Pkt; deshalb das Lückenkriterium.

---

## ENG-10 Hochlauf (Präreg-Anlaufprotokoll) und Folgerungen

**Ergebnis.** Die Frequenzrampe (RK4 und EL) wählt folgende Zustände:
- Insel → Kontakt;
- P6 und P49 → niedrige Zustände (18,2 bzw. 19,0 %);
- P13 und P33 → Hüpfzustand;
- P45: abhängig von Rampenzeit und Mitglied (2 s → ~35 %, 10 s → A 75,6 %, B 35,7 %);
- Hot-Spot und (0°, 0°) → Hüpfzustand.

Einschwingzeiten ab Rampenbeginn im Liftoff-Bereich (EL): 3–11 s für die niedrigen Zustände, 8–23 s für die Hüpfzustände. Im Kontaktast genügt die Präreg-Regel T_e = max(T_φ, 10τ) mit 10τ = 0,81 s → 1 s; gemessen wurden ≤ 1,2 s. Für den Liftoff-Bereich ist sie um eine Größenordnung zu kurz.

---

## Gesamtbewertung

**Karten im AP v2.4.**
- Im Kontaktast eindeutig und startunabhängig (12 Rasterpunkte; Feinsweep-Fenster).
- Im Liftoff-Bereich sind die Werte vom Standardstart ausgewählte Zustände: mindestens 27 % der Rasterpunkte gehören zu mehrdeutigen Konfigurationen.
- Mediane von λ, γ1 und A hängen vom Startprotokoll ab (λ 28–45 %). Der A_max-Zustand ist einer von zwei stabilen Zuständen.
- Perioden und Einschwingzeiten aus der RK4 sind dort nicht belastbar.
- „Statisches Gleichgewicht“ als Anfangsbedingung ist irreführend.

**Präreg v2.**
- Die konfirmatorischen Vorhersagen im Kontaktast (Pilotkonfigurationen, Schnitt) sind im Modell nicht startabhängig.
- Explorative Liftoff-Vorhersagen (E1/E2) sind als Zustandsmengen mit Auswahlprotokoll anzugeben.
- T_e ist für den Liftoff-Bereich unzureichend.
- Inseln mit kleinem F_min (0,37 N) und kleinem Einzugsgebiet sind für konfirmatorische Konfigurationen zu meiden.

**Experiment.**
- Rampenzeit und -form bestimmen im Liftoff-Bereich und an Inseln den Zustand.
- Hysterese/E2 ist im Modell konkret vorhergesagt: Hüpfzustand λ ≈ 75,6 % und F_max ≈ 39 N gegenüber niedrigen Zuständen; an der Insel schaltet ein Stoß von ≈ 0,07 N·s.

## Korrekturen an Quellen (Kurzfassung)

1. **Projektbeschreibung Aug. 2026, S. 5 (L4-038):** Die Werte „50 s −0,5 mN; 110 s −0,5 mN, stabil“ sind für Fenster ab 5 s nicht reproduzierbar. Richtig sind −9,08 bzw. −4,45 mN (Randterm ∝ 1/T_w plus Q). Die −0,5 mN gelten nur nach dem Einschwingen und sind dort Δt-abhängige Quadratur (Δt/2: ≈ ±0,03 mN).
2. **AP v2.4 §8.3:** „Übergang 18,8 s“ ist keine Eigenschaft der Konfiguration. Je nach Phasenrundung um 1 ULP bzw. Arithmetik liegt der Wert bei 7–19 s, im EL bei 9,1 s. Phase und Arithmetik sind anzugeben oder eine Spanne zu nennen.
3. **AP v2.4, Tabelle „Numerik“:** „z₀ = −Mg/k, statisches Gleichgewicht“ ist kein Gleichgewicht. Der Schwerpunkt startet mit v_S(0) = Mittel der Modulgeschwindigkeiten (bis 0,2417 m/s).
4. **AP v2.4 Anh. B.6 und Präreg-v2-Anhang A3:** Die Aussage, Mehrdeutigkeit gebe es nur in den sechs Satelliteninseln bzw. die Rasterwerte seien nur für den Standardstart gültig, ist unvollständig. Im Liftoff-Bereich gehören mindestens 99 von 361 Rasterpunkten (18 von 70 Bahnen) zu Konfigurationen mit koexistierenden Zuständen. An 5 Paaren sind sie im EL als stabile Orbits bzw. persistente Zustände bestätigt.
5. **Ergebnisnotiz Burn-in 13.09., §2b/§3:** „(12,17)/(17,12): Transient, ab 21 s P30, keine Bistabilität nachgewiesen.“ Tatsächlich ist der Hüpfzustand dort stabil (EL |µ| = 0,741) und koexistiert mit einem aperiodischen Zustand um 35 %. P30/P3 sind instabile Orbits, die die Festschritt-RK4 künstlich stabilisiert.
6. **Ergebnisnotiz Burn-in, §2 Periodenzählung:** Die Periodenlabels (P1 211, P2 104, …) stammen aus der Festschritt-RK4 mit 10⁻³-Toleranz. Hüpfzustände streuen dort Δt-proportional um 3–6·10⁻⁴ m/s; die Labels sind nicht robust.
7. **P1-Zwischenbericht §3 Nr. 3:** „Ursache der Startabhängigkeit = nicht impulskonsistenter Start“ trifft nicht zu (ENG-09). „30 von 361“ hängt von Generator und Toleranz ab (ENG-07).

## Offene Punkte

- Einzugsgebiete bzw. Häufigkeiten der koexistierenden Zustände sind nicht bestimmt (nur 3 Starts je Mitglied plus Stöße).
- Die Rasterzählung beruht auf Festschritt-RK4. Eine EL-Rasterrechnung fehlt; nur 6 Paare und 6 repräsentative Punkte sind mit EL geprüft.
- Übrige fünf Satelliteninseln, Parameterabhängigkeit (K, C, μ < 1, f) und realistischer Hochlauf (Phasenregelfehler, Motordynamik) sind nicht untersucht.
- Der ~35-%-Zustand von P45 und der 43,7-%-Zustand von P13 sind im EL nur über 40 s geprüft; ein sehr langer Transient ist nicht ausgeschlossen.
- Der EL ist nicht gegen einen zweiten Ereignislöser validiert.
