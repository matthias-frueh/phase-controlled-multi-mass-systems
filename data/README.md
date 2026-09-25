# Datensätze

**Simulationsausgabe, keine Messdaten.** Das gilt für alle Dateien in diesem Verzeichnis; gemessene Daten
existieren nicht. Beim Zitieren immer als Simulation kennzeichnen.

Lizenz dieses Ordners: CC BY 4.0, siehe [`../LICENSE-CC-BY-4.0`](../LICENSE-CC-BY-4.0). Namensnennung: „Matthias Früh, PCMMS“, https://github.com/matthias-frueh/phase-controlled-multi-mass-systems

Herkunft: erzeugt mit der Referenz-Engine [`../code/pcmms_v3a_phasen_sweep.py`](../code/pcmms_v3a_phasen_sweep.py)
(19×19-Sweep) und [`../code/finesweep.py`](../code/finesweep.py) (2°-Feinsweep). Engine-Stand im Repository:
Commit `1f75564` vom 20.09.2026, mit dem Engine und Datensätze gemeinsam abgelegt wurden. Ein Erzeugungsdatum
ist in den CSV-Dateien nicht hinterlegt.

Gemeinsamer Parametersatz (identisch mit dem Abschnitt „Simulationsstand“ der [README](../README.md);
Variablennamen aus [`../code/pcmms_v3a_phasen_sweep.py`](../code/pcmms_v3a_phasen_sweep.py), Block „Systemparameter“):
M = 0,650 kg Gesamtmasse (drei Module à M/3; der Rahmen ist masselos, die gesamte Masse bewegt sich
mit den Modulen) · g = 9,81 m/s², M·g = 6,3765 N · f = 10 Hz ·
Egg-Profil: Halteanteil pro Zyklus 0,65 (`THOLD`), Anteil der schnellen Phase 1 − THOLD = 0,35 (`TFAST`),
Hold-Radius oben 5 mm (`RTOP`), Radius unten (schnelle Phase) RTOP·TFAST/THOLD ≈ 2,69 mm (`RBOT`, C¹-stetig),
Hub (Spitze-Spitze) RTOP + RBOT ≈ 7,69 mm ·
Kontakt: linear-elastisch K = 10⁴ N/m, viskos C = 16 N·s/m (ζ ≈ 0,1), unilateral (nur Druck, keine Zugkraft) ·
RK4, Δt = 50 µs · 15 s je Konfiguration, davon 5 s Einschwingen; ausgewertet werden die letzten 10 s.

## Spalten

| Spalte | Bedeutung |
|---|---|
| `phi2_deg`, `phi3_deg` (bzw. `phi2`, `phi3`) | Phasenlage von Modul 2 und 3 gegen Modul 1, in Grad |
| `F_mean` | Zeitmittel der Kontaktkraft, in N; Erwartung M·g = 6,3765 N (Kontrollgröße, kein Ergebnis) |
| `F_skew` | Schiefe γ₁ der Kontaktkraft-Wellenform, dimensionslos |
| `liftoff` | Anteil der Auswertezeit ohne Kontakt, in Prozent |
| `F_max`, `F_min` | Maximum und Minimum der Kontaktkraft, in N |
| `peak_ratio` / `asym` | Asymmetrieverhältnis A = (F_max − M·g)/(M·g − F_min), dimensionslos. Die Spalte heißt im Code `peak_ratio`, berechnet aber A und nicht F_max/⟨F⟩ |
| `R` (nur Sinus-Sweep) | Resultierende der drei Phasenzeiger, R = \|1 + e^{iφ₂} + e^{iφ₃}\|, dimensionslos |

## Dateien

### `sweep_19x19.csv` — Grobraster, 361 Konfigurationen
Erzeugt mit [`../code/pcmms_v3a_phasen_sweep.py`](../code/pcmms_v3a_phasen_sweep.py) (N_GRID = 19). Raster über [0°, 360°)² mit Schrittweite
360°/19 = 18,947° ohne doppelten Randpunkt (`endpoint=False`). Die Punkte (120°, 240°) und (240°, 120°)
liegen deshalb nicht exakt auf dem Raster.
Kennzahlen: ⟨F⟩ Median 6,3765 N, Spannweite 6,3330–6,3832 N (Einschwing- und Endlich-Fenster-Effekte bei
hohem Liftoff) · Schiefe −0,288 … +1,979 · Liftoff 0–76,2 % · F_max bis 50,55 N · F_min bis 2,88 N ·
12 Rasterpunkte liftoff-frei.
Bekannte Eigenheiten: Das Minimum 6,3330 N bei (0°, 208,421°) stammt aus einem Einschwingvorgang, der nach 5 s
noch nicht abgeklungen ist; im stationären Zustand liegt ⟨F⟩ dort bei M·g − 0,5 mN und F_max bei 38,5 N statt
44,1 N. Im Liftoff-Bereich ist die Karte nicht eindeutig: Die Umbenennung der Module ändert die Physik nicht,
trotzdem landen gleichwertige Rasterpunkte teils in verschiedenen stationären Zuständen, etwa (0°, 113,684°)
mit 75,6 % und (246,316°, 246,316°) mit 18,2 % Liftoff. Die Werte einzelner Liftoff-Punkte hängen damit von der
Startbedingung ab (Start in statischer Ruhelage bei t = 0).

### `finesweep_2deg_120_240.csv` — 2°-Feinraster, 441 Konfigurationen
Erzeugt mit [`../code/finesweep.py`](../code/finesweep.py) (vektorisierte Reproduktion der Engine mit identischen Parametern,
gegen [`sweep_19x19.csv`](sweep_19x19.csv) geprüft mit `--validate`: liftoff-arme Punkte stimmen auf sechs
Nachkommastellen, am Punkt (0°, 0°) mit 75,8 % Liftoff weicht F_mean um 1,7·10⁻⁴ N ab —
Unterschied der Auswertungsreihenfolge zwischen skalarer und vektorisierter Fassung). Fenster φ₂ ∈ [100°, 140°],
φ₃ ∈ [220°, 260°], Schrittweite 2°.
Kennzahlen: F_min-Maximum 5,3304 N bei (120°, 240°), entlang φ₃ = 240° linear abfallend mit ≈ 0,23 N je Grad
zu kleineren φ₂ und ≈ 0,19 N je Grad zu größeren φ₂ (0,77 N bei φ₂ = 100°, 1,62 N bei 140°) · 90,7 % des Fensters liftoff-frei ·
|⟨F⟩ − M·g| ≤ 0,2 mN durchgehend.

### `sweep_7x7_sinus.csv` — Kontrollsweep mit Sinusprofil, 49 Konfigurationen
Gleiche Engine-Parameter, aber sinusförmiges statt Egg-Bewegungsprofil; Raster 7×7 über [0°, 360°),
Schrittweite 360°/7. Ergebnis: ohne Liftoff ist die Schiefe exakt null; die Phasenkarte kollabiert auf
die Zeigersumme R. Das erzeugende Skript (Sinus-Variante der Engine) ist noch nicht im Repository abgelegt.
Die Sinusamplitude ist nicht mit abgelegt; rekonstruiert aus den Daten beträgt sie (RTOP + RBOT)/2 ≈ 3,85 mm,
also derselbe Hub von 7,69 mm Spitze-Spitze wie beim Egg-Profil. Mit dieser Amplitude reproduziert die Engine
die liftoff-freien Punkte auf 10⁻⁵ N.
