# PCMMS — Phasenkontrollierte Mehrmassensysteme

**Phase-Controlled Multi-Mass Systems**
Matthias Früh · Gravidon Systemics Research · ORCID [0009-0005-9984-4207](https://orcid.org/0009-0005-9984-4207)
Stand: 20. September 2026 · Status: prä-experimentell (Simulation; keine Messdaten)

---

## Worum es geht

Ein ruhender Körper steht auf einer Unterlage. In seinem Inneren bewegen sich drei Massen periodisch
mit demselben Profil, aber mit einstellbarer relativer Phasenlage (φ₂, φ₃). Untersucht wird, wie diese
Phasenkonfiguration die **zeitliche Form** der Kontaktkraft N(t) zwischen Körper und Unterlage bestimmt —
gemessen an Schiefe γ₁, Liftoff-Anteil λ, Asymmetrieverhältnis A = (F_max − M·g)/(M·g − F_min) und
Minimalkraft F_min.

Der Grundsatz des Projekts: **Es werden keine Kräfte gemessen, sondern Verschiebungen gegen eine
Referenz.** Die Referenz ist das Zeitmittel ⟨N⟩ = M·g, das aus dem Schwerpunktsatz folgt. Es ist kein
Ergebnis und kein Forschungsziel, sondern Randbedingung und Kontrollgröße: Jede beobachtete Abweichung
des Zeitmittels gilt als Apparaturfehler. Der Untersuchungsgegenstand ist die Wellenform, nicht das Mittel.

Ausdrücklich **nicht** behauptet werden: reaktionsloser Antrieb, Gravitationsmodifikation,
Gewichtsreduktion, Verschiebung des Zeitmittels. Ein früherer Simulationszyklus (v3a–v3d) berichtete eine
solche Verschiebung; sie wurde als Kontaktmodell-Artefakt erkannt, zurückgezogen und archiviert
(`docs/archiv_vermerk_kernhypothese_v3.md`). Die alten Gleichungen bleiben als Nulllinie dokumentiert.

## Zwei Forschungslinien

- **Linie A (primär):** Wellenformstatistik der einseitigen Kontaktkraft eines *ruhenden* Körpers.
  Kein Effektanspruch; ⟨N⟩ = M·g als Erhaltungs-Nullgröße. Alles in diesem Repository gehört zu Linie A.
- **Linie B (optional, separate Apparatur):** gerichtete Nettobewegung durch Impulsübertrag an ein
  umgebendes Medium (Luft); das Medium ist der Reaktionspartner, das Vakuum der Nullfall. Linie B ist
  hier noch nicht abgelegt.

## Inhalt des Repositories

| Pfad | Inhalt |
|---|---|
| `docs/overview.md` | Wegweiser durch die Dokumente, Lesereihenfolge |
| `docs/was_ist_pcmms.md` | Einstieg ohne Vorwissen |
| `docs/werkstattbericht.md` | „Wellenform statt Mittelwert“ — der Stand für fachliche Leser |
| `docs/expose_2026-09.md` | Projekt-Exposé (Kernfrage, Stand, messbares Signal, nächster Schritt) |
| `docs/praeregistrierung_2026-06.md` | Präregistrierung mit Falsifikationskriterien (Juni 2026, unverändert) |
| `docs/einordnung.md`, `docs/zehn_fragen.md` | Einordnung, Abgrenzung, Antworten auf die üblichen Einwände |
| `docs/neuheitsgrad.md` | Was daran nicht neu ist — und was übrig bleibt |
| `docs/literaturabgleich_2026-09-12.md` | Abgleich mit der Ratchet-, Tribologie- und Kontaktdynamik-Literatur, 12 verifizierte Referenzen, davon 10 mit DOI |
| `docs/archiv_vermerk_kernhypothese_v3.md` | Dokumentierter Rückzug der früheren Hypothese |
| `code/` | Simulations-Engine (`pcmms_v3a_phasen_sweep.py`) und 2°-Feinsweep (`finesweep.py`) |
| `data/` | Simulationsausgaben: 19×19-Phasensweep und 2°-Feinsweep (`data/README.md`) |

## Simulationsstand

Parametersatz der Engine (Simulationsreferenz für alle Zahlen in diesem Repository):
M = 0,650 kg (drei Module à M/3) · f = 10 Hz · Egg-Profil mit Halteanteil 0,65, C¹-stetig ·
Kontakt: linear-elastisch K = 10⁴ N/m, viskos C = 16 N·s/m (ζ ≈ 0,1), unilateral · RK4, Δt = 50 µs,
15 s je Punkt (5 s Einschwingen). Alle Datensätze sind Simulationsausgaben; **gemessene Daten existieren nicht.**

- **19×19-Phasensweep** (361 Konfigurationen, `data/sweep_19x19.csv`): ⟨F⟩ im Median 6,3765 N = M·g
  (Spannweite 6,333–6,383 N, Endlich-Fenster-Effekt bei hohem Liftoff) · Schiefe −0,29 … +1,98 ·
  Liftoff 0–76,2 % · F_max bis 50,6 N. Nur 12 Rasterpunkte um (120°, 240°) und (240°, 120°) sind liftoff-frei.
- **2°-Feinsweep** um (120°, 240°) (441 Konfigurationen, `data/finesweep_2deg_120_240.csv`):
  F_min bildet eine Zeltkurve mit Spitze 5,3304 N genau am Triphasik-Punkt, beidseitig ≈ 0,21 N je Grad
  abfallend · 90,7 % des Fensters liftoff-frei · |⟨F⟩ − M·g| ≤ 0,2 mN durchgehend.
- Ein Sinusprofil liefert ohne Liftoff keine Schiefe; das asymmetrische Bewegungsprofil ist für das
  Zielsignal zwingend.

Die Auslegung eines physischen Aufbaus (Bewegungsprofil, Wägezellen, Kalibrierung bei intermittierendem
Kontakt) ist davon getrennt und offen; siehe `docs/expose_2026-09.md`, Abschnitt „Nächster Schritt“.

## Nachrechnen

```bash
pip install -r code/requirements.txt
cd data
python3 ../code/finesweep.py --validate      # prüft die Feinsweep-Engine gegen sweep_19x19.csv
python3 ../code/pcmms_v3a_phasen_sweep.py    # voller 19×19-Sweep, schreibt nach ~/pcmms_outputs_v3a_sweep
```

Der vollständige 19×19-Sweep braucht je nach Rechner 30–60 Minuten; das Skript ist checkpoint-fest.

## Zitieren

Siehe `CITATION.cff`. Frühere Stände (April–Mai 2026) liegen auf Zenodo unter *Früh, Matthias*; sie
dokumentieren den Weg, nicht den aktuellen Stand.

## Lizenz

MIT, siehe `LICENSE`.

---

*Summary (EN):* Pre-experimental study in classical mechanics. A body at rest carries three internally
oscillating masses with adjustable relative phases (φ₂, φ₃). The object of study is the waveform of the
unilateral contact force — skewness, liftoff fraction, asymmetry ratio, minimum force — not its time
average, which is fixed at M·g by the centre-of-mass theorem and serves as the null control. No claim of
reactionless propulsion, gravity modification or mean-force shift is made; an earlier mean-shift result
was identified as a contact-model artefact and retracted. All data here are simulation output.
