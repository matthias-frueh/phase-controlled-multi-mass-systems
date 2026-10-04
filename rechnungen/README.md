# Rechnungen der Gesamtprojektanalyse 10/2026

Rechen- und Prüfskripte mit ihren gespeicherten Ergebnissen aus der Gesamtprojektanalyse vom 1. bis 2. Oktober 2026.
**Alles ist Simulation oder Analytik, keine Messdaten.** Jede Gruppe liegt in einem eigenen Ordner mit den Skripten,
den Ausgaben des ursprünglichen Laufs (`<skript>_ausgabe.txt` bzw. `.out`, dazu CSV, JSON, NPZ) und dem
Protokoll `PROTOKOLL.md`, das die Befunde mit den Rechnungen verknüpft. Die Unterordner `verifikation/` enthalten
die unabhängige Gegenprüfung derselben Fragen mit eigenem Code; wo eine Gegenprüfung ein Ergebnis einschränkt,
steht das in ihrem Protokoll, die Erstrechnung bleibt unverändert.

Lizenz: Skripte MIT ([`../LICENSE`](../LICENSE)); Protokolle, Ausgaben und Daten CC BY 4.0
([`../LICENSE-CC-BY-4.0`](../LICENSE-CC-BY-4.0)), Namensnennung „Matthias Früh, PCMMS“.

## Stand und Kennzeichnung

- **Code-Stand der Rechnungen:** Repository `cd7be6a` (28.09.2026). Die importierten Module `code/finesweep.py`,
  `code/linear_solver.py` und `code/pcmms_v3a_phasen_sweep.py` sind seit diesem Stand unverändert; die Daten
  `data/sweep_19x19.csv` und `data/finesweep_2deg_120_240.csv` ebenso. Die später hinzugekommenen Werkzeuge
  `code/auslegung.py`, `code/ereignisloeser.py` und `code/einzugsgebiete.py` wurden hier nicht benutzt; sie setzen
  Befunde dieser Rechnungen um (3-FG-Zellmodell, ereignisgenauer Löser, Attraktorkarten).
- **Dokumentstand der Rechnungen:** Präregistrierung v2 vom 25./28.09.2026, Arbeitspapier v2.4, Formelverzeichnis
  v2.7. Die Präregistrierung ist seither überarbeitet (PR #14: Entscheidungsregeln als Arbeitsfestlegungen, M nach
  Konvention (b)); die Vorschläge in `statistik/PROTOKOLL.md` sind dort teilweise eingegangen. Maßgeblich ist der
  Text in `docs/`, nicht das Protokoll.
- **Historische Rechnungen:** Die Protokolle tragen einen Vermerk zur Übernahme. Sie sind nicht nachgeführt.
  Verweise wie „L1a-019“, „P1 §3“ oder „B01–B14“ zeigen auf Arbeitsdokumente der Analyse (Evidenzmatrix,
  Zwischenberichte, Bündelliste), die nicht im Repository liegen; „(lokaler Bestand, nicht im Repository)“ steht
  für Quellen außerhalb des Repositorys.
- **Übernommen wurden** nur Pfade (relativ zum Skript, Repo-Code über `PYTHONPATH`), die Startskripte in
  `statistik/` und die Kopie der v1-Karte für Linie B. Die Ausgabedateien sind die unveränderten Originale; eine
  Ausgabe enthält noch den damaligen absoluten Pfad in einer Warnzeile (`symmetrie_randterm/s6b_…_ausgabe.txt`).
- **Prüfstand bei der Übernahme (04.10.2026):** alle 173 Skripte kompilieren (`py_compile`). 36 kurze Skripte
  wurden aus einer Kopie des Ordners gestartet: 29 geben Zeile für Zeile die gespeicherte Ausgabe wieder, zwei bis
  auf Laufzeit- und Warnzeilen (`linie_b/b2b_…`, `symmetrie_randterm/s6b_…`), eines mit erwarteter Abweichung
  (`neuheit/bibcheck.py`, siehe dort), eines ohne gespeicherte Vergleichsdatei (`engine/verifikation/vk_paare.py
  gruppe`), eines bricht ohne die nicht enthaltenen Rohsegmente ab (`engine/grid_wertebereich.py`), eines wurde
  nach 150 s abgebrochen (`verif_bewertung/vb4_…`). Lange Rechnungen wurden nicht wiederholt; ihre Ausgaben sind
  die Originale.

## Start

```bash
pip install -r code/requirements.txt          # numpy, scipy, pandas
cd rechnungen/<gruppe>
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../../code python3 <skript>.py [Argumente]
cd verifikation && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../../../code python3 <skript>.py
```

Die Skripte schreiben in ihren eigenen Ordner und überschreiben dabei die gespeicherten Ergebnisse. Für eine
Gegenprobe den Ordner kopieren. Argumente, Laufzeiten und Reihenfolgen stehen je Gruppe im Protokoll (Abschnitt
„Dateien“ bzw. „Werkzeuge“). Getestet mit Python 3.11, numpy 2.4, scipy 1.17, pandas 3.0.

## Gruppen

### `auslegung/` – V1-Auslegungsraum, bewegter Massenanteil μ

| | |
|---|---|
| Zweck | Kennzahlen des Simulationsreferenzsatzes; lineares Dauerkontaktmodell mit Massenanteil μ und RK4-μ-Engine (`mu_modell.py`); dimensionslose Last- und Signalfunktionen G(ρ, ζ); zulässiger Bereich in (ε, ρ, ζ); Arbeitspunktvorschläge V1–V5; nichtlineare Stichprobe (Hüpfzustände, E1-Spitzen, Einzugsbereich, Konvergenz); PB1-Herleitung |
| Start | `a1_p1_zahlen.py`, `a1b_zusatz.py`, `a2_lineares_modell_abgleich.py`, `a3a_G_funktionen.py`, `a3b_arbeitspunkte.py`, `a4_rk4_stichprobe.py <Fall>` (Fall `V1z05`, `V2z02`, `V4z02`, `V4z10`, `V5z05`, `start`, `E1`), `a4b_bistabilitaet.py`, `a4c_einzugsbereich.py`, `a4d_konvergenz.py`, `a5_qualitativ.py`, `a5b_kontaktanteil_mu.py` |
| Abhängigkeiten | `code/finesweep.py`, `code/linear_solver.py` (Abgleich) |
| Parameter | Referenzsatz M = 0,650 kg, K = 10⁴ N/m, C = 16 N·s/m, f = 10 Hz, Egg-Profil THOLD = 0,65; V1-Vorschläge (3 × 100 g, Hub 8 mm, K ≥ 1,5·10⁶ N/m, ζ = 0,05) sind Annahmen |
| Grenzen | 1 Freiheitsgrad, keine Kippmoden, keine Zellsteifigkeit, keine Antriebsnachgiebigkeit; Einzugsbereich und Hysterese nicht systematisch; Rauschen in `statistik/`. Die RK4-Stichproben (a4) laufen je mehrere Minuten |

### `engine/` – Startabhängigkeit, Symmetriepaare, ereignislokalisierender Löser

| | |
|---|---|
| Zweck | Prüf-Engine `eng.py` (Arithmetik der Referenz-Engine, freier Start, Frequenzrampe, zyklusweise Akkumulatoren); Startvarianten std/imp/ramp/orb; Hot-Spot-Einschwingen und Fensterreihe; Festschritt-Artefakte im Hüpfbereich; Satelliteninsel mit Δt/2; S₃-Äquivalenzpaare der 19×19-Karte; drei Starts auf dem Raster; ereignislokalisierender Löser `el_solver.py` (DOP853) mit Floquet-Analyse |
| Start | Spezifikationen: `make_specs.py`, `make_spec_transfer.py`, `make_spec_grid.py`; Läufe: `run_seg.py SPEC.json OUTDIR SEG N_CYC` (segmentweise, je Segment ≤ 540 s); Auswertung: `analyse_runs.py`, `analyse_grid.py`, `grid_wertebereich.py`, `report_pairs.py`, `report_rep.py`, `poincare_streuung.py`, `sym_count.py`; EL: `el_check.py`, `el_floquet.py`, `el_floquet_p33.py`, `el_kick.py`, `el_ramp_check.py`, `orbit.py`, `orbit_hopping.py`; `hotspot_scalar.py`, `impuls_start.py`, `burnin_repro.py`, `validate_eng.py` |
| Abhängigkeiten | `code/finesweep.py`, `code/linear_solver.py`, `code/pcmms_v3a_phasen_sweep.py`, `data/sweep_19x19.csv`, `docs/arbeitspapier/nachrechnung_2026-09-13/` (Burn-in-Reproduktion) |
| Parameter | Referenzsatz; Δt = 50 µs und 25 µs; Fenster 5–15 s |
| Nicht enthalten | die Rohsegmente `run_*/seg_*.npz` (134 MB). `analyse_runs.py`, `analyse_grid.py`, `grid_wertebereich.py` und `poincare_streuung.py` brauchen sie und brechen ohne sie ab (geprüft); Erzeugung mit den `for`-Schleifen im Protokoll (ENG-02, ENG-08, ENG-09), je Segment bis 9 min. Die Endzustände `run_*/state_*.npz`, die Spezifikationen und alle abgeleiteten Tabellen (`rep_tabelle.csv`, `paare_tabelle.csv`, `grid_auswertung.json`, `*_ausgabe.txt`, `el_*.jsonl`) liegen bei |
| Grenzen | Rasterzählung mit Festschritt-RK4; EL nur an 6 Paaren und 6 Punkten; EL hier nicht gegen einen zweiten Ereignislöser validiert (später: `code/ereignisloeser.py`); Einzugsgebiete nicht bestimmt (später: `code/einzugsgebiete.py`) |

### `kippmoment/` – Einzelzellkräfte und Kippmoment bei drei Wägezellen

| | |
|---|---|
| Zweck | starrer Körper auf drei Zellen im Dreieck (`km_modell.py`, 3 Freiheitsgrade): Profilharmonische und Auswahlregel, Kipp-Eigenfrequenzen, Zellkräfte und Momente linear, nichtlinear mit einseitigem Kontakt je Zelle (REF, STEIF), Leckage durch Modulungleichheit, Identifizierbarkeit, Messbarkeit |
| Start | `k1_harmonische_auswahlregel.py`, `k2_linear_3fg.py`, `k2b_umlaufsinn.py`, `k2c_phasen.py`, `k3_rk4_validierung.py` (≈ 4 min), `k4_leckage_identifizierbarkeit.py`, `k5_rk4_einseitig.py REF` bzw. `STEIF` (je ≈ 3 min), `k5b_entkopplung_mu1.py`, `k6_messbarkeit_auslegung.py` |
| Abhängigkeiten | `code/finesweep.py` (Konstanten, Profil) |
| Parameter | Zellen auf R_c = 100 mm bei 0/120/240°, Geometrien G0 (Module über den Zellen), G0h/G60h (R_c/2), G60; Rahmen als Scheibe mit ρ_f = R_c/2; REF K = 10⁴ N/m, STEIF f_n = 120 Hz, ζ = 0,02; alles Annahmen, keine CAD-Daten |
| Grenzen | Geometrie, Massen, Trägheiten, Schwerpunkthöhe angenommen; Rahmen- und Plattenmoden, Übersprechen der Zellen, Aktorrückwirkung nicht modelliert; Liftoff-Fälle chaotisch. **Bekannter Fehler:** `k6_messbarkeit_auslegung.py` Z. 39–46 mischt σ_F beider Abtastraten (Gegenprüfung `zusatz_p2/z4_km11_messbarkeit.py`, Befund KM-11 „eingeschränkt“); Skript und Ausgabe sind unverändert belassen, die Folgerung hält laut Gegenprüfung |
| Nicht enthalten | Zeitreihen der Gegenprüfung `verifikation/v3_teil*_reihen3s.npy` (53 MB; Erzeugung `v3_nichtlinear_zellen.py A 50`, `A 25`, `B 50`, `C 50`, `D 50`, 40–145 s je Lauf) |

### `statistik/` – Statistik und Identifizierbarkeit der Präregistrierung v2

| | |
|---|---|
| Zweck | PB1-Nachrechnung; Extremwert-Bias von F_min (Zeitreihen-Monte-Carlo); Rauschbias-Bedingung am Triphasik-Punkt; Operating Characteristic der H1-Entscheidungsregel über Rauschstufen L0–L5 und neun Szenarien; H2-Zeltfit (Bias, Halbbreite, Fensterregel) und Bootstrap-Überdeckung; Superpositionsresiduen von Alternativursachen (Hertz-Kontakt, Zellkennlinie, Drift, Kopplung, Jitter, Phasenversatz) |
| Start | `s0_pb1_grundlagen.py` (≈ 1 min), `s1_fmin_rauschen_mc.py 0|1|2` (je 3–4 min), `s1b_rauschbias_triphasik.py` (≈ 4 min), `sh run_s2.sh` (sechs Läufe à 5–8 min), `sh run_s2_zusatz.sh`, `s5_oc_tabelle.py`, `s3_h2_zeltfit_mc.py` (≈ 6 min), `s3b_h2_bootstrap_check.py` (≈ 5 min), `sh run_s4.sh` |
| Abhängigkeiten | `code/finesweep.py`, `code/linear_solver.py`, `data/finesweep_2deg_120_240.csv` |
| Parameter | Beispiel A4 der Präregistrierung (starre Auflage, μ = 0,4, f = 10 Hz, k_max = 9), Rauschmodelle als Annahmen (Sensorrauschen 20 mN bei 6,4 kHz, Jitter, Lauf-zu-Lauf-Streuung je Stufe) |
| Grenzen | alle u_c-, OC- und Laufzahlwerte sind bedingt auf angenommene Rauschmodelle; Bootstrap mit B = 200/400; ungleiche Module nicht simuliert; Hertz-Kontakt nur rein; H3 und H4 nicht nachgerechnet. Die Regeln der Präregistrierung sind seither geändert (PR #14); die hier geprüfte Fassung ist die vom 25./28.09.2026 |

### `symmetrie_randterm/` – Symmetrien der Phasenebene, Randterm und Fensterbilanz

| | |
|---|---|
| Zweck | Teil A: exakte Äquivalenzen (Gruppe S₃), Spiegelung φ → −φ, 120°-Verschiebung, numerische Prüfung an 11 Basispunkten × 6 Bildern; Teil B: Fensterbilanz und Reproduktion von Tab. 9.3 (Hot-Spot), Realisierungsabhängigkeit des Exponenten, Quadraturrest gegen Δt und Quadraturregel, Archivresiduen, Folgerung für ⟨N⟩ = Mg als Nullkontrolle. Prüf-Engine `sr_engine.py` |
| Start | `s0_validierung.py`, `s1_kandidaten.py`, `s2_symmetrie_laeufe.py std|shift` (je 2,5–6 min), `s3_analytik.py`, `s4_symmetrie_auswertung.py` (braucht `s2_laeufe_*.npz`), `s5_randterm_skalar.py`, `s6_quadratur_dt.py`, `s6b_quadratur_tabelle.py`, `s6c_simpson_defekt.py`, `s7_randterm_fit.py`, `s8_fensterbedarf.py` (braucht `s6_p1.npz`), `s9_archiv_zerlegung.py` |
| Abhängigkeiten | `code/finesweep.py`, `code/pcmms_v3a_phasen_sweep.py`, `data/sweep_19x19.csv`, `data/finesweep_2deg_120_240.csv` |
| Parameter | Referenzsatz; Fenster W1 = 5–15 s, W2 = 50–60 s; Δt 6,25–50 µs |
| Nicht enthalten | `s2_laeufe_std.npz`, `s2_laeufe_shift.npz` (22 MB; `s2_symmetrie_laeufe.py std` und `shift`); in `verifikation/` die Läufe `v2_laeufe_std_*.npz` und `v5_fensterbedarf.npz` (20 MB; `v2_symmetrie_laeufe.py`, `v5_fensterbedarf.py lauf`) |
| Grenzen | S₃-Test nur an 11 Basispunkten; für die Rauschstufen L4–L6 ist Chaos gegen langes Einschwingen nicht geklärt; Spiegelungsbrechung für V1-Parameter nicht beziffert. `s6b_quadratur_tabelle_ausgabe.txt` enthält eine Warnzeile des Originallaufs (log2 einer Null), die beim Neustart auf stderr erscheint |

### `linie_b/` – Linie B: Medienkopplung und Fluid-Drift (Kontrollrechnungen)

Linie B ist die optionale zweite Forschungslinie des Projekts (gerichtete Bewegung durch Impulsübertrag an ein
umgebendes Medium, separate Apparatur). Dieser Ordner enthält keine Ergebnisse einer Apparatur, sondern die
Prüfung der vorhandenen Modelle. Das „Egg“-Profil von Linie B ist nicht das der Linie A (Befund LB-14).

| | |
|---|---|
| Zweck | Kennzahlen des Trägers (Keulegan-Carpenter-Zahl, β), Gültigkeit des quasistationären Widerstandsmodells, periodische Lösung des integrierten Modells und Dichtevergleich, Reproduktion der v1-Fensterkarte und ihre Skalierung mit ρ, Luftkräfte auf Module und Körper des Linie-A-Aufbaus V1 (zugesetzte Masse, Quetschfilm, Auftrieb, Thermik, Elektrostatik) |
| Modelle | `quelle_kopie/pcmms_fluid_drift_v2.py` und `quelle_kopie/pcmms_medienkopplung_modell_v2.py`: die korrigierten Fassungen vom 06.09.2026, byte-gleich mit dem Bestand, hier unverändert; Lauf des Modells in `b0_medienkopplung_modell_v2_lauf.out` |
| Daten | `sweep_13x13_drift_v2.csv`: stationäre Driftkarte des v2-Modells (ρ = 1000 kg/m³, 169 Punkte, Simulation); `daten/sweep_13x13_drift_v1.csv`: **historische** v1-Karte aus dem Kernpaket vom 01.09.2026 (Fenstermittel 4–8 s, nicht eingeschwungen; nur als Vergleich für `b3b_…` und `verifikation/vb3_…`) |
| Start | `b1_kc_kennzahlen.py`, `b1b_kc_medienkopplung_fall_s.py`, `b2_fluid_drift_v2_kontrolle_an.py`, `b2b_periodische_loesung.py`, `b3_dichte_drift_c1.py`, `b3b_v1_fenster_karte.py`, `b4_v1_luftkraefte.py`; Ausgaben `.out` |
| Abhängigkeiten | nur `quelle_kopie/`; `b4_v1_luftkraefte.py` zusätzlich `code/linear_solver.py` |
| Parameter | Driftskript v2: M = 0,75 kg, RATIO = 0,2, C_D-Ansatz mit stationärem C_D, 13×13-Raster; V1-Luftkräfte mit angenommenen Maßen (Platte R = 4 cm, Gehäuse 15–20 cm, Spalt 1–10 mm) |
| Grenzen | Zweiterm-Ansatz mit stationärem C_D; bei KC ≪ 1 sind Kraftgesetz und ρ-Abhängigkeit offen; Größenordnungen für V1 aus angenommener Geometrie; keine Aussage zu einer Apparatur. `b2b_periodische_loesung.out` weicht beim Neustart in Laufzeitangaben und letzten Stellen ab (iterative Lösung) |

### `bewertung_a/`, `bewertung_b/`, `verif_bewertung/` – Bewertung übersehener Ansätze

| | |
|---|---|
| Zweck | Modellrechnungen zu Kandidaten aus der Analyse (Bündel B01–B14): Spiegelungsbrechung am V1-Punkt, Anteil hoher Profilharmonischer am ungebänderten F_min, richtungsabhängige Kontaktdämpfung, Rahmenterm im kinematischen Kraftkanal (`bewertung_a/`); Median-Versatz, Rast-Modell der Linie B, ungerade Harmonische, Auswahlregel für N Module, Landestoß nach Liftoff, Gasreihe (`bewertung_b/`); Gegenprüfung der Hüpfzustände mit `../auslegung/mu_modell.py`: Einzelmodullauf, Schnitt und Piloten, Zeitschritt, ζ-Schwelle (`verif_bewertung/`) |
| Start | `bewertung_a`: `b01_spiegelung_v1.py`, `b02_profilglaette.py`, `b03_daempfungsasymmetrie.py [0.2]`, `b07_impulsbilanz_kanal.py`; `bewertung_b`: `b1_…` bis `b6_…`; `verif_bewertung`: `vb1_…` bis `vb5_…` (vb1, vb2, vb4 mehrere Minuten) |
| Abhängigkeiten | `bewertung_a`: `code/linear_solver.py`, `code/finesweep.py`; `bewertung_b`: keine; `verif_bewertung`: `../auslegung/mu_modell.py` |
| Parameter | V1-Vorschlag aus `auslegung/` (M = 0,65 kg, μ ≈ 0,46, Hub 8 mm, 10 Hz, K = 1,5·10⁶ N/m, ζ = 0,05 bzw. 0,02); Stoffwerte der Gasreihe als Annahmen |
| Grenzen | 1-FG-Modelle mit idealem Egg-Profil; Wurfphasen nur in 60°/90°-Schritten; kein ereignisgenauer Löser (die Schwelle 0,17 < ζ_krit < 0,18 gilt für diese Würfe); Literaturangaben nicht geprüft |

### `zusatz_p2/` – Gegenprüfung nicht verifizierter Befunde

| | |
|---|---|
| Zweck | eigenes 3-FG-Modell (`zm.py`, Lagrange-Herleitung, analytische Fourier-Koeffizienten) und unabhängige Rechenwege zu KM-02, KM-03, KM-10, KM-11, KM-12, SYM-01, RT-04 und STA-10; Ergebnis: KM-02, KM-03, SYM-01, RT-04, STA-10 bestätigt, KM-10, KM-11, KM-12 eingeschränkt (Protokoll Abschnitt 3 und 4) |
| Start | `z1_km02_modell.py` (78 s), `z2_km03_auswahlregel.py`, `z3_km10_identifizierbarkeit.py`, `z4_km11_messbarkeit.py`, `z5_sym01_symmetrie.py` (163 s), `z6_rt04_archiv.py`, `z7_sta10_drift.py`, `z8_ergaenzung_km02_km12.py` (20 s) |
| Abhängigkeiten | `code/finesweep.py` (z1, z8), `code/pcmms_v3a_phasen_sweep.py` und `data/sweep_19x19.csv` (z6) |
| Parameter | wie `kippmoment/` (Vergleichbarkeit) |
| Grenzen | wie `kippmoment/`; Geometrie angenommen |

### `neuheit/`, `verif_neuheit/` – formale Literaturprüfung und Zeltform beim Sinusprofil

| | |
|---|---|
| Zweck | `bibcheck.py`: Zitierschlüssel, Feldvollständigkeit und Konsistenz von `docs/arbeitspapier/references.bib` gegen Arbeitspapier, Literaturabgleich und Formelverzeichnis; `sinus_zelt.py`: Zelt mit Knick auch beim Sinusprofil (starr, linear); Gegenprobe mit `code/linear_solver.py --section --rigid --mu 0.462` und `--sinus` (`verif_neuheit/v1_egg_sinus_schnitt_ausgabe.txt`) |
| Start | `bibcheck.py` (schreibt auf stdout), `sinus_zelt.py` |
| Abhängigkeiten | `docs/arbeitspapier/`, `docs/formelverzeichnis/`, `docs/literaturabgleich_2026-09-12.md`; die Dissertation v2.1 liegt nicht im Repository, der Vergleich wird übersprungen und gemeldet. Die gespeicherte Ausgabe stammt vom vollständigen Lauf gegen den Stand `cd7be6a`; `references.bib` ist seither bereinigt (PR #13), ein Neustart meldet deshalb weniger fehlende Felder |
| Grenzen | keine Websuche, keine Neuheitsaussage; nur formale Prüfung des Bestands |

## Nicht übernommen

- Lesekorpus, Evidenzmatrix und Zwischenberichte der Analyse (Phasen P1, P4; Arbeitsdokumente, kein Rechenmaterial).
  Hardwarekonzepte, der Plan des Pipelinetests und die Übersicht der Arbeitspakete folgen in einem eigenen
  Dokumentpaket.
- Rechnungen zu Schutzrechtstexten (Rollen `ip_a`, `ip_b`, `verif_ip`): Ihre Quellen liegen nicht im Repository;
  Übernahme ist Entscheidung des Autors.
- Rohdaten über 2 MB (oben je Gruppe genannt, zusammen 232 MB) und drei leere Fehlprotokolle eines Fehlaufrufs.
- Prüfung der Aussagen gegen Dokumente außerhalb des Repositorys (lokaler Bestand): in den Protokollen nur noch als
  Verweis gekennzeichnet.
