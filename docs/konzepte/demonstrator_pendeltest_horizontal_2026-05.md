# Pendeltest-Protokoll — horizontale Drift (Strang b)

*PCMMS · Phase-Controlled Multi-Mass Systems  —  Matthias Früh  ·  ORCID 0009-0005-9984-4207  ·  Mai 2026*

## 1 · Zweck und Messprinzip

Geprüft wird, ob phasengesteuerte interne Oszillation eine reproduzierbare, phasenabhängige **horizontale** Netto-Verschiebung in ruhiger Luft erzeugt — oberhalb der Eigendrift und der Run-zu-Run-Streuung. Der Mechanismus ist ehrlich benannt: Der Impuls geht an die Luft (Vibrationsschwimmer; nichtlinearer Widerstand, mitbewegte Luftmasse). Die Luft ist der Reaktionspartner; es ist kein reactionless drive.

**Warum horizontal (und nicht vertikal): **In der Horizontalen gibt es keine statische Grundkraft — Schwerkraft und Auftrieb wirken vertikal. Eine Netto-Horizontalbewegung kann deshalb nur aus der Luftkopplung stammen. Das vermeidet den Auftriebs- und Antigravitations-Confound der Vertikalmessung und hält den Strang sauber. Ein Null-Ergebnis ist ein vollwertiges, dokumentiertes Resultat.

## 2 · Messgröße und Variablen

- **Primärgröße: **horizontale Netto-Verschiebung x(t) gegenüber der Ruhelage. Beim Pendel der mittlere Versatz Δx̄ nach Einschwingen; auf der Luftkissenbahn die Driftgeschwindigkeit (Steigung von x(t)).

- **Querachse y: **mitgetrackt als Kontrolle (ein echter Effekt liegt entlang der Asymmetrieachse, nicht beliebig).

- **Steuergröße: **relative Phase φ der Module (0°, 90°, 180°, 270°) sowie das gespiegelte Phasenmuster (Vorzeichenumkehr-Test).

- **Kontrollen: **Motoren AUS, Zufallsphase, balancierte (Dummy-)Masse.

## 3 · Aufbau

**Primär (günstig) — langes bifilares Pendel.  **Die Plattform hängt an langen Fäden; ein roter Marker wird per Video verfolgt. Lange Fäden bedeuten schwache Rückstellkraft, also hohe Empfindlichkeit für kleine Horizontalkräfte. Eine kleine Netto-Horizontalkraft F erzeugt einen messbaren Gleichgewichtsversatz Δx ≈ L·F/(Mg).

**Empfindlicher — Torsionspendel.  **Plattform an einem Torsionsdraht; eine tangentiale Schubkraft erzeugt eine Winkelauslenkung. Das ist die Standardapparatur für kleine Schübe (z. B. Triebwerks-Prüfstände) und deutlich empfindlicher als das Fadenpendel.

**Sauberste Steigung — Luftkissenbahn.  **Nahezu reibungsfreie 1D-Translation, im Laborrahmen referenziert; hier ergibt ein Netto-Schub eine echte, ablesbare Driftgeschwindigkeit.

**Allen gemeinsam:  **ruhige Luft (geschlossene Box / Windschutz), thermisches Einschwingen vor der Messung, schwere und entkoppelte Aufhängung; die Antriebsfrequenz darf keine Pendel- oder Torsionsresonanz treffen.

## 4 · Aktuatorik und Phasen

Zwei bis drei Vibrationsmodule (Exzentermassen) werden über die ESP32-Steuerung phasenstarr betrieben; die relative Phase φ wird auf 0°, 90°, 180°, 270° gesetzt. Antriebsfrequenz konstant (Bezug: 10 Hz), Amplitude konstant.

**Vorzeichenumkehr-Test (starke Signatur): **Das gespiegelte Phasenmuster (umgekehrte Phasenreihenfolge der Module) sollte laut Modell eine entgegengesetzt gerichtete Drift erzeugen. Kehrt die gemessene Drift unter Spiegelung das Vorzeichen um, ist das ein starkes Indiz für einen realen, steuerbaren Effekt — analog zur v3c↔v3d-Symmetrie. Bleibt das Vorzeichen gleich, ist es ein Artefakt.

## 5 · Sensorik und Tracking

- **Kamera fest montiert **(Stativ), Bildebene parallel zur Bewegungsebene, Maßstab im Bild.

- **OpenCV-Tracking **des roten Markers → x(t) und y(t), ≥ 30 fps; Kalibrierung mm/Pixel über den Maßstab; gemeinsame Zeitbasis.

- **Ausgabe **als CSV „t_s, x_m, y_m‘ — direkt in die Auswertepipeline einlesbar.

## 6 · Kontrollen (das wissenschaftliche Rückgrat)

- **Motoren AUS: **Eigendrift und Streuung → Nullband / Rauschboden.

- **Zufallsphase: **Motoren an, aber ohne kohärente Phase → trennt einen kohärenten Phaseneffekt von bloßer Vibration.

- **Balancierte (Dummy-)Masse: **Motoren laufen, Exzenter entfernt/ausgewuchtet → trennt die echte asymmetrische Luftkopplung von Motor-EM-, Struktur- und Aufhängungskopplung. Der entscheidende Confound-Check.

- **Vorzeichenumkehr: **gespiegeltes Phasenmuster muss die Driftrichtung umkehren.

- **Stillluft und Thermik: **geschlossene Box, Einschwingzeit, Wiederholung zu verschiedenen Zeitpunkten.

- **Reihenfolge randomisieren, **Kontrollen zwischen die Phasenläufe schalten (gegen langsame Drift über die Session).

## 7 · Messablauf

- Aufbau in der Box thermisch einschwingen lassen; Tracking und Kalibrierung prüfen.

- Pro Bedingung: Box schließen, einschwingen lassen, 30–60 s x(t), y(t) aufzeichnen.

- Je Bedingung 3–5 Wiederholungen; Bedingungsreihenfolge randomisiert, Kontrollen interleaved.

- Pflicht-Set pro Sitzung: AUS, Zufallsphase, balancierte Masse, 0°/90°/180°/270°, sowie ein gespiegeltes Muster.

- Tracking-CSV und Video je Lauf sichern (offen auf Zenodo/GitHub).

## 8 · Auswertung

Je Lauf wird aus x(t) eine robuste Steigung (Theil-Sen) bzw. der mittlere Versatz Δx̄ mit Standardfehler bestimmt; y dient als Kontrolle. Der Kontroll-Pool (AUS + Zufallsphase) liefert den Rauschboden; eine Bedingung gilt als Signal, wenn ihr Mittel außerhalb des Bandes ±k·SD (k = 2) liegt *und* sich das Vorzeichen unter Spiegelung umkehrt. Die vorhandene Pipeline pcmms_drift_analyse.py wird wiederverwendet — Eingang von h(t) auf x(t) umgestellt.

## 9 · Erfolgs- und Abbruchkriterium

**Erfolg.  **Phasenabhängige horizontale Drift oberhalb des Kontrollbandes, reproduzierbar, mit Vorzeichenumkehr unter gespiegeltem Phasenmuster.

**Falsifikation (für den getesteten Bereich).  **Keine phasenabhängige Horizontaldrift über dem Kontrollband, nachdem alle Kontrollen bestanden sind.

**Artefakt-Flags (kein Effekt, sondern Messfehler).  **(1) Die balancierte Masse zeigt dieselbe Drift wie die asymmetrische Konfiguration → Motor-/Struktur-/Aufhängungskopplung, kein Lufteffekt. (2) Die Drift kehrt unter Spiegelung das Vorzeichen nicht um → Artefakt. (3) Die Drift korreliert mit Zugluft oder Temperatur → Umgebung. In allen Fällen wird die Ursache behoben, nicht interpretiert.

## 10 · Protokoll (auszufüllen)

| **Datum / Ort** |  |
| --- | --- |
| **Setup** | Aufbau (Pendel/Torsion/Luftbahn), Fadenlänge L, Kamera-Abstand, mm/Pixel, Stillluft-Box, Frequenz, Modulanzahl: |
| **Tracking-CSV** | tracking_data.csv |
| **Video** | pendeltest_[datum].mp4 |

*Messungen (x-Drift = Primärgröße, y = Kontrolle):*

| **Bedingung** | **Lauf** | **Dauer** | **x-Drift** | **y (Kontr.)** | **>****Schw.?** | **Beob.** |
| --- | --- | --- | --- | --- | --- | --- |
| Motoren AUS (Ref.) |  |  |  |  |  |  |
| Zufallsphase |  |  |  |  |  |  |
| Balancierte Masse |  |  |  |  |  |  |
| 0° (Auslöschung) |  |  |  |  |  |  |
| 90° |  |  |  |  |  |  |
| 180° |  |  |  |  |  |  |
| 270° |  |  |  |  |  |  |
| Gespiegelt (Umkehr) |  |  |  |  |  |  |

## 11 · Zusammenfassung (auszufüllen)

- **Kontroll-Pool: **Mittel ____ mm/s, Streuung SD ____ mm/s, Schwelle 2·SD = ____ mm/s.

- **Phasenabhängige Horizontaldrift über Schwelle? **Ja / Nein

- **Vorzeichenumkehr unter Spiegelung bestätigt? **Ja / Nein

- **Confound-Checks bestanden (balancierte Masse, y-Kontrolle, Stillluft)? **Ja / Nein

- **Probleme: **(Resonanzen, ungleiche Motoren, Zugluft, Tracking-Aussetzer)

- **Bewertung: **Effekt / Null-Ergebnis / nicht eindeutig — mit Begründung.

*Dokumentation offen auf Zenodo / GitHub (Rohdaten, Videos, Skripte). Ein sauberes Null-Ergebnis wird vollständig dokumentiert.*