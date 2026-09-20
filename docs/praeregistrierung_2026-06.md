# PCMMS — Präregistrierung (Arbeitsfassung)

**Matthias Früh · Gravidon Systemics Research · ORCID 0009-0005-9984-4207**
Stand: 14. Juni 2026

Diese Präregistrierung legt Fragestellung, Observablen, Entscheidungsregeln und Abbruchkriterien **vor** der Messung fest. Sie basiert auf dem internen Dokument *Nullhypothese / Effektgröße / Messartefakte / externe Validierung / Abbruchkriterien* und der korrigierten Methodik: **⟨F⟩ = Mg ist eine Erhaltungs-Nullbasislinie** (Schwerpunktsatz), die **Wellenform-Statistik** ist die primäre, erhaltungssichere Observable.

---

## 1. Fragestellung

Unter welchen kontrollierten Bedingungen lassen sich in phasensynchronen mechanischen Mehrmassensystemen reproduzierbare, **phasenabhängige Strukturen in der Kontaktkraft** nachweisen — und bleibt der **Mittelwert** dabei innerhalb des Fehlerbudgets gleich `Mg`?

## 2. Hypothesen

- **H0 (Erhaltungs-Nullbasislinie):** `⟨F_contact⟩ = Mg` innerhalb des Fehlerbudgets, unabhängig von der Phasenlage. Wird erwartet zu halten — Bestätigung = saubere Messkette + bestätigte Impulserhaltung, **kein** physikalischer Effekt.
- **H1 (primär, erhaltungssicher):** Die Wellenform-Statistik der Kontaktkraft — **Schiefe, Liftoff-Anteil, Spitzen-zu-Mittel-Verhältnis** — hängt reproduzierbar von der Phasenkonfiguration ab.
- **H1_fluid (optional, separater Aufbau):** Bei weichem Reaktionspartner (Fluid/Medium) tritt eine **Netto-Schwerpunktdrift** auf, die mit der Mediendichte ρ skaliert und im Vakuum (ρ = 0) exakt verschwindet. Kein Erhaltungsverstoß — der Impuls geht messbar ins Medium.

## 3. Observablen

- **Primär:** Schiefe, Liftoff-Anteil, Peak-to-Mean der Kraftzeitreihe `F(t)`.
- **Null-/Kontroll-Observable:** Zeitmittel `⟨F⟩`, getestet gegen `Mg`.
- **Fluid-Variante:** Netto-Drift des Schwerpunkts und ihre ρ-Abhängigkeit.

## 4. Effektgröße & Stichprobe

- Zielauflösung: **0,2–0,5 %** relative Abweichung (Sub-Promille-Kraftsensorik).
- **N** so dimensioniert, dass **0,3 %** bei gegebenem σ_F mit vorab gewählter Power und Konfidenz detektierbar ist.
- **Statistische Einheit = der Run**, nicht der Einzel-Sample. Pseudo-N aus autokorrelierten Samples ist ungültig.

## 5. Messprotokoll

- **Referenz / Negativkontrolle:** gleiche Mechanik, aber ohne Phasensteuerung / mit starrer Kopplung / mit Dummy-Masse — der Zustand, in dem kein Effekt erwartet wird.
- **Repeats** vorab geplant, nicht improvisiert.
- **Blind / Randomisierung**, wo möglich.
- **Vollständige Metadaten:** Temperatur, Versorgung, Timestamps, Checksums.

## 6. Hauptquellen möglicher Artefakte (vorab benannt)

Thermische Drift · mechanische Kopplung · Vibrationen · EM-Rückwirkungen · Software-Filter · Sensor-Nichtlinearität · Phasenfehler · Erwartungseffekte.

**Regel:** Alles, was nicht durch Referenz, Dummy und Wiederholung überlebt, wird verworfen.

## 7. Analyseplan (vorab fixiert)

- Block-Averaging mit `T_b ≫ Korrelationszeit`.
- Welch-Satterthwaite-Zweistichproben-t (Referenz vs. Modulation).
- **Zusätzliches Gate:** Run-zu-Run-Streuungskriterium — der p-Wert allein reicht nicht.
- Jede scheinbare Abweichung von `⟨F⟩ = Mg` gilt als Indikator für Artefakt / Transiente / Modellfehler, **nicht** als Effekt.

## 8. Externe Validierung (Pflicht, nicht Kür)

Ohne unabhängige Messung zählt es nicht: gleiche Messung, andere Personen, andere Umgebung, idealerweise andere Hardware. Filter gegen Selbsttäuschung — Eintrittskarte, nicht Marketing-Schritt.

## 9. Abbruchkriterien (vorab, datengetrieben)

- **Stop:** kein reproduzierbarer phasenabhängiger Effekt → Projektende oder Themenwechsel.
- **Modify:** Effekt inkonsistent → Architektur, Parameter, Methodik anpassen.
- **Scale:** Effekt stabil **und** extern bestätigt → systematisch erweitern.

Die Entscheidung fällt nach Datenlage, nicht nach Bauchgefühl.

## 10. Abgrenzung (was *nicht* behauptet wird)

Kein reactionless drive, keine Gewichtsreduktion, keine neue Physik. `⟨F⟩ = Mg` ist Erhaltungssatz, nicht Forschungsziel. Abgrenzung zu EM-Drive / Woodward-Effekt: dort werden (umstrittene) neue Mechanismen postuliert — hier bleibt alles in der klassischen Mechanik, mit dokumentierter Null-Basislinie.
