# PCMMS — Was es ist, was es nicht ist, und warum es das braucht

**Phasenkontrollierte Mehrmassensysteme · Phase-Controlled Multi-Mass Systems**
Matthias Früh · ORCID 0009-0005-9984-4207 · Stand September 2026

*Geschrieben für jemanden, der Mechanik kann und noch nie von PCMMS gehört hat.*

---

## 1 · In drei Sätzen

Ein geschlossener Körper enthält mehrere periodisch bewegte Innenmassen, deren relative Phasenlage
frei einstellbar ist. Untersucht wird, wie diese Phasenlage die **zeitliche Form** der Kontaktkraft am
Auflager bestimmt — während ihr **Zeitmittel** durch den Schwerpunktsatz auf M·g festgelegt bleibt und
nicht zur Disposition steht. Der Gegenstand ist damit ein Messproblem, kein Antriebsproblem.

---

## 2 · Der physikalische Kern

Für beschränkte periodische Innenbewegung gilt über eine Periode

```
⟨ Σₖ mₖ z̈ₖ ⟩ = 0     →     ⟨F_N⟩ = M·g
```

auch bei intermittierendem Kontakt mit Liftoff. Das ist kein Ergebnis, sondern eine Randbedingung.
Sie wird im Projekt als **Kontrollgröße** benutzt: Weicht ein gemessenes Zeitmittel dauerhaft ab, ist
die Messkette defekt, nicht die Physik.

Die Kontakt-Nichtlinearität — der Kontakt kann drücken, aber nicht ziehen — verlagert die gesamte
Information in die **Form** des Signals. Wo der Kontakt abhebt, ist die Kraft exakt null; die verlorene
Fläche muss anderswo durch höhere Spitzen kompensiert werden. Genau diese Umverteilung ist steuerbar.

**Die vier Observablen:**

| Größe | Definition | Was sie anzeigt |
|---|---|---|
| Schiefe | drittes zentrales Moment von F_N(t) | Asymmetrie der Kraftverteilung |
| Liftoff-Anteil | Zeitanteil je Zyklus mit F_N ≈ 0 | Kontaktverlust |
| Asymmetrieverhältnis | (F_max − M·g) / (M·g − F_min) | Verhältnis Überhöhung zu Entlastung |
| F_min | kleinste Kontaktkraft im Zyklus | Abstand zum Kontaktverlust |

---

## 3 · Zwei Linien, eine Klammer

Das Projekt führt **zwei getrennte Forschungslinien**. Die Präregistrierung vom Juni 2026 nennt beide
und ordnet sie:

### Linie A — Wellenformstatistik (primär)

Der Körper steht auf einer Unterlage und bewegt sich nicht. Gefragt ist ausschließlich, wie die
Phasenkonfiguration (φ₂, φ₃) die Wellenform von F_N(t) formt. Das Zeitmittel ist fixiert und wird
zur Kontrolle mitgemessen.

Hierzu gehören: das Exposé September 2026, der 19×19-Phasensweep, der 2°-Feinsweep, die
Simulationsengine, die Präsentationen.

### Linie B — Medium-gekoppelte Fortbewegung (optional, separater Aufbau)

Der Körper hängt frei oder an einer Torsionswaage. Gefragt ist, ob phasenkontrollierte Innenbewegung
über den **quadratischen Luftwiderstand** eine gerichtete Nettobewegung erzeugt — bilanziell
geschlossen, weil der Impuls messbar an die Luft geht. Im Vakuum verschwindet der Effekt exakt; das
ist Teil der Hypothese, nicht ihr Widerspruch.

Hierzu gehören: der Forschungsrahmen v3.5, der Drift-Sweep, die Medienkopplungsmodelle, der
Ballon-Demonstrator.

**Warum die Trennung wichtig ist:** Linie A ist erhaltungssicher im starken Sinne — der Effekt ist
ein Formeffekt bei festgelegtem Mittelwert, es gibt nichts zu bezweifeln außer der Messbarkeit.
Linie B ist ebenfalls erhaltungskonform, aber sie behauptet eine Nettobewegung und braucht deshalb
den expliziten Nachweis des Reaktionspartners. Wer die beiden vermischt, liest in Linie A eine
Antriebsbehauptung hinein, die dort nicht steht.

### Die beiden Linien im Vergleich

| | Linie A | Linie B |
|---|---|---|
| Körper | stationär auf Unterlage | frei bzw. aufgehängt |
| Hauptfrage | Form der Kontaktkraft | gerichtete Nettodrift |
| primäre Observable | F_N(t) und ihre Statistik | Position, Driftgeschwindigkeit |
| Rolle der Phase | experimentelle unabhängige Variable | Steuergröße für den Effekt |
| Reaktionspartner | Unterlage (Messinterface) | umgebende Luft (Effektträger) |
| Abstand zur Nachbarliteratur | größer | kleiner |
| Rolle im Projekt | wissenschaftlicher Kern | Nebenlinie, separater Aufbau |

**Eine dritte Hypothese wurde verworfen.** Eine frühere Fassung postulierte eine persistente
Verschiebung des Zeitmittels (F̄ < M·g − ε). Sie ist durch den Schwerpunktsatz a priori ausgeschlossen,
nicht erst empirisch offen. Die zugehörigen Simulationsbefunde erwiesen sich als Artefakt eines
Kontaktmodells mit vorgeschriebener Eindrückung. Der Rückzug ist dokumentiert und die betroffenen
Dokumente sind mit Archivvermerk versehen.

---

## 4 · Aktueller Stand

**Vorhanden:** 361 Konfigurationen im Grobraster, 441 im 2°-Feinraster um den Triphasik-Punkt,
Präregistrierung mit Abbruchkriterien, Artefakt-Taxonomie, Auswerteplan, Schwellen als Formel
(3·σ̂_ref; die Zahlenwerte folgen erst aus der Referenzmessung).

**Nicht vorhanden:** jede Messung und damit auch der Auswertecode für Messdaten. Das Projekt ist prä-experimentell. Alle Zahlen sind numerisch.

**Die Kernbefunde aus der Simulation:**

| Größe | Wert |
|---|---|
| Streuung des Zeitmittels über 361 Konfigurationen | 0,072 % |
| Liftoff-Anteil | 0 … 76,2 % |
| Schiefe | −0,288 … +1,979 |
| Asymmetrieverhältnis | bis 6,93 |
| Spitzenkraft | bis 50,55 N bei ⟨F⟩ = 6,38 N |
| max \|⟨F⟩ − M·g\| im Feinfenster | 1,90 · 10⁻⁴ N |

**Die schärfste prüfbare Vorhersage:** Bei festem φ₃ = 240° und Variation von φ₂ durchläuft F_min
eine Zeltkurve mit scharfem Maximum von 5,330 N exakt bei φ₂ = 120°, abfallend auf 0,77 N bei 100°
und 1,62 N bei 140°. Steigung 0,21 N pro Grad bei K = 10⁴ N/m; das ist ein Resonanzwert, weil die zweite
Harmonische mit 2f/f_n = 1,013 auf der Kontaktresonanz liegt (bei festem ζ und K = 3·10⁴ … 10⁷ N/m:
0,09–0,12 N pro Grad). Das ist ohne jede Statistik am Kraftsignal ablesbar.

---

## 5 · Das Nachbarschaftsfeld

Die mechanischen Grundelemente von PCMMS sind alle besetzt. Das ist bekannt und wird nicht bestritten.

### Direkte Nachbarn

**Fudan-Gruppe (Fang, Xu, Diao) — Mehrmodul-Vibrationsroboter.** Die Gruppe um Fang und Xu untersucht
Dynamik und Phasenkoordination von Mehrmodul-Vibrationsrobotern mit linearen und nichtlinearen
Verbindungen und sucht Phasendifferenzen, die die mittlere Dauergeschwindigkeit maximieren.
Dieselbe Gruppe behandelt stückweise-glatte Mehrmodulsysteme mit Trockenreibung und
diskontinuitätsinduzierte Gleitbifurkationen (*Commun. Nonlinear Sci. Numer. Simul.* 114, 106704,
2022). Diao, Zhang & Fang optimieren die Lokomotionsleistung bi-objektiv (*Arch. Appl. Mech.* 91,
2073–2088, 2021).

**Das ist der engste Nachbar überhaupt** — gleicher mechanischer Unterbau, gleicher Phasenbegriff.

**Chernousko und Nachfolger — Optimierung vibrationsgetriebener Systeme.** Die klassische Linie:
optimale Innenmassenbewegung für maximale Dauergeschwindigkeit unter anisotroper Trockenreibung.

**M-Runners (DLR + TUM, Albu-Schäffer).** Intrinsische Dynamik elastischer Roboter — Bewegung
entsteht aus dem Zusammenspiel bewegter Massen und elastischer Elemente statt aus Servoregelung.
Der Roboter BERT nutzt Eigenschwingungen. Mechanische Bewegungserzeugung über Strukturdynamik statt
über Servoregelung ist damit etablierter, aktiv betriebener Forschungsstand — angrenzend, aber kein
Vorläufer von PCMMS: dort geht es um Energieeffizienz der Bewegung, nicht um die Kontaktkraft.

**Vibro-impact-Forschung.** Intermittierender Kontakt, Liftoff, Normalkraftdynamik bei starker
Vibrationsanregung — etabliert, mit aktuellen Arbeiten zu Crawl-/Flug-Regimen bei Bürstenrobotern.

### Was daraus folgt

| Element | Neu? |
|---|---|
| Interne bewegte Massen | nein |
| Mehrmodulsysteme | nein |
| Phasendifferenz als Stellgröße | nein |
| Liftoff, intermittierender Kontakt | nein |
| Zeitaufgelöste Normalkraftmessung | nein |
| 2D-Parameterkarten | nein |

**Nichts an den Bausteinen ist neu.** Das ist die ehrliche Antwort, und sie ist stärker als jede
Neuheitsbehauptung, weil sie überprüfbar ist.

---

## 6 · Die harten Fragen

### „Gibt es das nicht schon dreimal?"

Die Bausteine ja, die Fragestellung nein — aber die Abgrenzung braucht zwei Schritte, nicht einen.

**Schritt 1: Wer die Kontaktkraft als Zielgröße nimmt, hat keine Mehrmassen-Phasensteuerung.**
Perret-Liaudet & Rigaud untersuchen die Normalkraft eines stoßenden Hertz-Kontakts unter
Zufallsanregung als primäre Observable und zeigen, dass Schiefe und Kontaktverlust die
Zustandsinformation tragen. Umbanhowar & van Hecke messen Kraftdynamik bei sub-nm-Relativbewegung.
Beide behandeln die Kraft selbst — aber an einem Einzelkontakt beziehungsweise einer granularen
Packung, ohne mehrere individuell phasengesteuerte Innenmassen als Stellgröße.

**Schritt 2: Wer Mehrmassen-Phasensteuerung betreibt, optimiert Geschwindigkeit.**
In den für PCMMS direkt relevanten Mehrmodul-Vibrationsrobotik-Arbeiten wird die Kraftdynamik
überwiegend als *Mechanismus* der Lokomotion behandelt; zentrale Zielgrößen sind Lokomotionsleistung,
mittlere Dauergeschwindigkeit und Bewegungsregime. Wenn die Gruppe um Fang und Xu Phasendifferenzen zwischen
Modulen optimiert, dann für maximale Geschwindigkeit. Diao et al. optimieren die Lokomotionsleistung
bi-objektiv. Dieselbe Gruppe analysiert Gleitbifurkationen unter Trockenreibung — auch dort ist die
mittlere Geschwindigkeit die zentrale Größe.

**PCMMS Linie A sitzt im Schnitt beider Mengen:** mehrere individuell phasengesteuerte Innenmassen
*und* die zeitaufgelöste Kontaktkraft als primäre Zielgröße, bei absichtlich stationärem Körper.
Der Aufbau ähnelt Schritt 2, die Fragestellung ähnelt Schritt 1 — die Kombination habe ich nicht
gefunden.

Das ist eine schwächere und damit haltbarere Behauptung als „niemand untersucht Kontaktkräfte".

### „Was ist dann konkret der Beitrag?"

Die Kombination, nicht das Einzelteil:

> vorgegebenes individuelles Bahnprofil · kontrollierte relative Phase · gemeinsamer Rahmen ·
> unilaterale Stützfläche · zeitaufgelöste Kraftmessung · analytisch festgelegte ⟨F_N⟩ = M·g-Nullbasis ·
> vollständige Präregistrierung mit Abbruchkriterien vor der Messung

Diese Zusammenstellung als **Messproblem** habe ich in der Literatur nicht gefunden. Das ist eine
Nischenbehauptung, keine Entdeckungsbehauptung — und sie ist widerlegbar, indem jemand die Arbeit
zeigt, die es schon gibt.

### „Ist das nicht ein verkapptes Perpetuum mobile?"

Nein, und die Struktur des Projekts ist genau darauf ausgelegt, das prüfbar zu machen. Linie A
behauptet ausdrücklich, dass das Zeitmittel **nicht** verschiebbar ist, und benutzt diese Unmöglichkeit
als Kontrollgröße: Jede beobachtete Mittelwertabweichung gilt per Protokoll als Apparaturfehler und
löst einen harten Stopp aus, keine Interpretation.

Linie B behauptet eine Nettobewegung, benennt aber den Reaktionspartner explizit — die umgebende
Luft — und sagt vorher, dass der Effekt im Vakuum exakt verschwindet und mit der Mediendichte
skaliert. Das ist genau die Vorhersage, die ein reaktionsloser Antrieb nicht machen könnte.

Eine frühere Fassung des Projekts behauptete tatsächlich eine Mittelwertverschiebung. Sie wurde
zurückgezogen, der Rückzug ist dokumentiert und die betroffenen Dokumente sind entsprechend
gekennzeichnet.

### „Warum schwankt die Kraft, wenn der Mittelwert fest ist?"

Weil der Mittelwert eine Aussage über das Integral macht, nicht über den Verlauf. Beim Liftoff ist
die Kraft phasenweise exakt null; die fehlende Fläche muss durch Spitzen kompensiert werden. In der
Simulation erreicht die Spitzenkraft 50,6 N bei einem Zeitmittel von 6,38 N — Faktor acht, bei einer
Streuung des Mittelwerts von 0,07 %.

Das ist kein Sonderfall: Perret-Liaudet & Rigaud zeigen für den stoßenden Hertz-Kontakt experimentell,
dass das Zeitmittel bei bis zu 15 % Kontaktverlust an der statischen Last bleibt.

### „Warum keine Messdaten?"

Weil das Projekt prä-experimentell ist und das so benannt wird. Die Reihenfolge ist bewusst:
Präregistrierung, Artefaktkatalog, Entscheidungsregeln und Abbruchkriterien stehen **vor** der ersten
Messung. In der experimentellen Mechanik ist das unüblich — und genau deshalb ist es der Teil der
Arbeit, der auch dann Bestand hat, wenn die Physik nichts hergibt.

### „Was ist, wenn nichts herauskommt?"

Dann ist das ein Ergebnis. Die Falsifikationsbedingung steht vorab fest: Ist die Regime-Struktur nach
allen Kontrollen nicht über dem Rauschboden nachweisbar, gilt H1 für den getesteten Bereich als
falsifiziert. Ein Null-Ergebnis ist eingeplant, nicht abgefedert.

### „Warum kein Roboter? Das wäre doch die Anwendung."

Weil ein Roboter die Frage unbeantwortbar macht. Sobald sich das System fortbewegt, mischen sich
Reibungsmodell, Untergrundeigenschaften und Kontaktgeometrie in das Signal. Die Wellenform der
Kontaktkraft ist dann nicht mehr isolierbar. Der stationäre Aufbau ist eine Vereinfachung mit
Absicht — Robotik ist eine mögliche nachgelagerte Validierungsebene, keine Voraussetzung.

### „Was ist die praktische Relevanz?"

Liftoff-Anteil und Spitzenkraft sind bei Vibrationsförderern, Siebmaschinen und Bodenverdichtung
unmittelbar Durchsatz- und Verschleißgrößen. Wenn sich beide über die Phasenlage einstellen lassen,
ohne den mittleren Lastfall zu ändern, ist das ein Stellhebel. Ob er praktisch trägt, ist offen —
das Projekt behauptet es nicht, es untersucht die Grundlage.

### „Warum sollte ich das ernst nehmen — ohne Institut, ohne Labor?"

Die faire Antwort: Die Physik ist unstrittig; Simulationscode und Simulationsdaten liegen in diesem
Repository (`code/`, `data/`) und sind nachrechenbar. Was fehlt, ist die Messung, und das steht in jedem Dokument. Was das Projekt anbietet, ist
keine Entdeckung, sondern eine vollständig vorbereitete, falsifizierbare Messfrage mitsamt
Auswerteplan — und die Bereitschaft, ein Null-Ergebnis zu veröffentlichen.

---

## 7 · Was ausdrücklich nicht behauptet wird

- kein reaktionsloser Antrieb
- keine Gravitationsmodifikation oder -abschirmung
- keine Gewichtsreduktion
- keine Verschiebung des Zeitmittels der Kontaktkraft
- keine Verletzung von Impuls- oder Schwerpunktsatz
- keine neue Physik

Alles bewegt sich innerhalb der klassischen Mechanik.

---

## 8 · Wo die Argumentation dünn ist

Zur Vollständigkeit, weil ein guter Gutachter es ohnehin findet:

**Linie B liegt näher an der Nachbarliteratur als Linie A.** Gerichtete Fortbewegung durch interne
Massenbewegung mit Medienkopplung überschneidet sich mit drag-basierter Mikroaktorik und mit der
Vibrationsroboter-Literatur deutlich stärker. Die Abgrenzung ist dort schwieriger und sollte nicht
mit der von Linie A vermischt werden.

**Die Schiefe ist bei hohem Liftoff schlecht konditioniert.** Die Kraftverteilung wird dann bimodal
(Nullphasen plus Kontaktphasen), und das dritte Moment reagiert empfindlich auf die Fensterwahl.
Für die Auswertung sind Bootstrap-Konfidenzintervalle vorgesehen.

**Die dynamische Kalibrierung bei intermittierendem Kontakt ist ungelöst.** Nicht die absolute
Kraftmessbarkeit ist das Problem — statische Rückführbarkeit ist über DKD-R 3-3 verfügbar, Verfahren
zur dynamischen Kalibrierung einachsig belasteter Kraftaufnehmer beschreibt DKD-R 3-10 — sondern
die Übertragung auf einen Kontakt, der zyklisch abhebt.

**Simulationsresiduen lassen sich beliebig klein rechnen.** Der numerische Boden von 2·10⁻⁴ N sagt
nichts über die erreichbare Messauflösung. Physikalisch zählt erst die gemessene Größe.
