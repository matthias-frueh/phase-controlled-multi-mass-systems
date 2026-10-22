# PCMMS · Laborfähigkeiten und Gate-Matrix

*Phase-Controlled Multi-Mass Systems — Matthias Früh · ORCID 0009-0005-9984-4207 · Stand September 2026*

Ersetzt die zonenbasierte Infrastrukturliste (`PCMMS_Labor_und_Infrastrukturplanung_2026-09.md`).

---

## 0 · Leseregel

Dieses Dokument ist **keine Beschaffungsliste**. Es beantwortet nur eine Frage:

> Welche experimentelle **Fähigkeit** ist an welchem **Forschungsgate** zwingend, und woraus folgt sie?

Aufbaurichtung durchgehend: **Observable → benötigter Kanal → Mindestspezifikation → Gate → Bezugsweg (intern/extern/vertagt) → räumliche Konsequenz.**

Was sich so nicht ableiten lässt, steht in §8 (Streichliste) — mit Begründung, nicht stillschweigend.

Grundsatz, der die halbe Liste entlastet: **Gemessen werden Kraftverschiebungen, keine Kräfte.** φ ist ein reiner Softwareparameter, der Aufbau bleibt zwischen den Punkten mechanisch identisch. Das Experiment ist ein Innerhalb-Aufbau-Vergleich. Umgebungseinflüsse gehen deshalb nur über die *Änderung innerhalb eines Sweepblocks* ein, nicht über ihren Absolutwert. Konsequenz: Kurzzeit-Wiederholpräzision und Kanalabgleich sind auslegungsbestimmend, absolute Genauigkeit und Umgebungsstabilisierung sind es nicht.

---

## 1 · Bezugsgrößen und offene Festlegungen

### 1.1 Klärung erforderlich, bevor Zahlen belastbar sind

In der Ablage stehen zwei unvereinbare Parametersätze:

| Quelle | M | f |
|---|---|---|
| Bindende Parameter (00_INDEX) | 0,650 kg **je Modul**, 3 Module → Mg ≈ 19,1 N | **2,2 Hz** |
| Laborplan V1/V2 (Mai 2026) | ≈ 0,65 kg **gesamt** → Mg ≈ 6,4 N | **10 Hz**, Hub „einige mm" |

Die Differenz ist auslegungsbestimmend, nicht kosmetisch:

- Gleiche Spitzenbeschleunigung skaliert mit A ∝ 1/f². (10 / 2,2)² ≈ **21**. Bei 2,2 Hz braucht dieselbe Liftoff-Bedingung rund zwanzigfachen Hub — aus „einige mm" wird ~10 cm. Das ändert Aktuatorklasse, Modulgeometrie, Gehäuse, Aufstandsfläche und Fertigungsbedarf.
- Mg legt Messbereich, Überlastgrenze und Auflösung fest.

Indiz: F_min erreicht im Feinsweep maximal ≈ 5,33 N. Das passt zu Mg ≈ 6,4 N, nicht zu 19,1 N. Der Verdacht richtet sich damit gegen die Zeile „0,650 kg je Modul", nicht gegen die Laborpläne. **Zu prüfen an `pcmms_v3a_phasen_sweep.py`, nicht an den Textdokumenten.**

Bis zur Klärung sind alle Spezifikationen unten **parametrisch in M und f** formuliert und bleiben dadurch in beiden Zweigen gültig.

### 1.2 Weiter offen

- **ε_⊥** (Querbilanzschwelle) — von Matthias zu setzen
- **ε_phys** (physikalische Nachweisschwelle) — von Matthias zu setzen
- **k** (Kontaktsteifigkeit) — empirisch, Messziel von Gate 1. Vorher sind Bandbreite und Abtastrate **nicht** zahlenmäßig festlegbar (§3, R3).

### 1.3 Mitgeführte Korrektur

Asymmetrieverhältnis = (F_max − Mg) / (Mg − F_min), so wie im Code implementiert. **Nicht** max(F)/⟨F⟩. Die abweichende Definition steht noch in Präregistrierung, Symbolverzeichnis, Laborplan und Messtechnik-Konzept und darf hier nicht weitergetragen werden.

---

## 2 · Zielobservablen (Ausgangspunkt der ganzen Ableitung)

**Linie A — stationärer Körper, unilateraler Kontakt:**

| Observable | Rolle |
|---|---|
| F_min(φ) | primär; Zeltkurve, ohne Statistik sichtbar |
| Liftoff-Anteil | primär |
| Schiefe von N(t) | primär; schlecht konditioniert bei bimodaler Verteilung → Bootstrap-CI |
| Asymmetrieverhältnis | primär |
| ⟨N⟩ | **Kontrollgröße**, keine Messgröße. Dauerhafte Abweichung von der statischen Last = defekte Messkette, nicht Befund. |
| ε_⊥ | Querbilanz, Artefaktausschluss |

**Linie B — separater Aufbau, medium-gekoppelte Fortbewegung:**

| Observable | Rolle |
|---|---|
| gerichtete Nettodrift | primär |
| Drift als Funktion der Mediendichte ρ | **die eigentliche Prüfgröße** — Steigung, nicht Einzelwert |

Linie B teilt mit Linie A weder Aufbau noch Messgröße. Fähigkeiten werden getrennt geführt (§6).

---

## 3 · Fähigkeitskatalog Linie A

Jede Fähigkeit mit Herkunft (aus welcher Observable) und Mindestspezifikation.

### F1 · Dreipunkt-Kraftinterface
**Aus:** F_min, Liftoff, ε_⊥
**Spezifikation:**
- ≥ 3 Kraftkanäle in Dreieckanordnung. **Mit einem einzelnen Kanal ist ε_⊥ nicht bestimmbar** — kein Druckmittelpunkt, keine Querbilanz. Harte Anforderung, keine Option.
- Nennbereich je Kanal ≥ 3·Mg (Asymmetrieverhältnis bis ≈ 6,9)
- Überlastgrenze ≥ 5·Mg (Wiederaufsetzstöße)
- DC-fähig (DMS, nicht ladungsgekoppelt ohne Langzeitkonstante)
- Auflösung ≤ 0,005·Mg je Kanal

**Bewusst nicht gefordert:** absolute Auflösung von F_min ≈ 0,006 N. Die Zeltkurve durchläuft nahezu den vollen Bereich 0…Mg. Gemessen wird die Verschiebung. F_min-Absolutwerte nahe null sind Simulationsartefakt der Kontaktmodellierung, kein Auslegungstreiber.

### F2 · Kontaktcharakterisierung (k, c)
**Aus:** allen Observablen — jede Spezifikation unten hängt an f_c = (1/2π)·√(k/M)
**Spezifikation:** Ausschwing-/Impulsversuch am aufgesetzten Körper, statische k-Kennlinie, Dämpfungsmaß. Austauschbare, charakterisierte Kontaktelemente (Feder oder Elastomer), damit k später als zweite Achse variierbar bleibt.
**Reihenfolgehinweis:** Dies ist die **erste** Fähigkeit, nicht die Phasensteuerung. Vor bekanntem k sind R3 und R4 nur symbolisch.

### F3 · Synchrone Mehrkanalerfassung
**Aus:** allen Observablen
**Spezifikation:**
- R3 Bandbreite (−3 dB) der **gesamten** Kette inkl. Sensoraufnahme: ≥ max(20·f, 5·f_c)
- R4 Abtastrate ≥ 10 × R3, **simultan** über alle Kraftkanäle (kein Multiplex); Kanalversatz ≤ 1/(100·R3)
- Hardware-Timestamping, eine Zeitbasis für Kraft, Position und Antriebsreferenz
- 11 Kanäle: 3 Kraft, 1 Dummy, 3 Phase/Position, 1 optischer Weg, 1 Beschleunigung, 1 Temperatur, 1 Reserve

### F4 · Dynamische Kalibrierung bei intermittierendem Kontakt
**Aus:** Liftoff, F_min, Asymmetrieverhältnis
**Dies ist die eigentliche messtechnische Schwierigkeit des Projekts** — nicht die absolute Kraftmessbarkeit. Statische Rückführung ist verfügbar und unkritisch. Die zonenbasierte Vorgängerliste deckte ausschließlich den statischen Fall ab.
**Spezifikation:**
- Übertragungsfunktion des Kraftpfads bis zur höchsten relevanten Harmonischen (Impulshammer oder Shaker mit Referenzaufnehmer)
- Nachweis, dass die Kette Kontaktabriss- und Wiederaufsetzflanken formtreu abbildet (nicht nur Amplituden)
- Rig-FRF vor jeder Kampagne, dokumentiert
- Gegenprobe Liftoff über den unabhängigen Beschleunigungskanal, nicht nur über den Kraftkanal

### F5 · Phasenstellung und Profilverifikation
**Aus:** φ als unabhängige Variable
**Spezifikation:**
- Sweepraster 2° ⇒ zulässiger Phasenjitter ≤ 0,2° ⇒ Δt ≤ 0,2/360 · 1/f
  - bei f = 2,2 Hz: ≤ 250 µs
  - bei f = 10 Hz: ≤ 56 µs
- **Befund: Synchronität ist nicht der Engpass.** Beides ist mit Hardware-Timestamping trivial erreichbar. Die Vorgängerliste behandelt Jitter-, Phasendrift- und Synchronisationsüberwachung als eigenständige Ausbaustufe — das ist überdimensioniert.
- Soll-Ist-Vergleich des gefahrenen Egg-Profils, Positionsauflösung ≤ 1 % des Hubs, gleiche Zeitbasis wie F3
- C¹-Bedingung am Nahtpunkt und Zyklusbilanz im Profilgenerator geprüft, nicht angenommen

### F6 · Differenzielle Kampagnenführung
**Aus:** dem Charakter der Messung (Verschiebung, nicht Absolutwert)
**Spezifikation:**
- randomisierte φ-Reihenfolge innerhalb jedes Sweepblocks
- eingestreute Referenzphase in festem Intervall, Rückkehr auf denselben Punkt
- R7 Nullpunktdrift innerhalb eines Blocks ≤ 0,002·Mg, **über die Referenzphasenwiederholung nachgewiesen**, nicht über Umgebungsstabilisierung erzwungen
- Blockweise Auswertung, Welch–Satterthwaite bei α = 0,05
- Dummy-Kanal mitlaufend über die gesamte Kampagne

**Diese Fähigkeit kostet nichts und ersetzt einen erheblichen Teil der Umgebungsinfrastruktur** (Messfundament, Klimatisierung, EMV-Umgebung). Sie ist methodisch außerdem stärker, weil sie Drift *nachweist* statt sie zu unterstellen.

### F7 · Rauschboden und Nachweisschwelle
**Aus:** ε_phys
**Spezifikation:** Leermessung, Dummy-Messung, Messung mit laufenden Aktuatoren bei unterdrückter Innenbewegung. Ergebnis ist die empirische Schwelle, gegen die ε_phys gesetzt wird. **ε_phys darf nicht vor dieser Messung numerisch festgeschrieben werden.**

### F8 · Umgebungsdiagnostik (nicht Umgebungskontrolle)
**Aus:** Artefaktausschluss
**Spezifikation:** ein Beschleunigungsaufnehmer an der Basis plus Temperaturkanal, beide auf derselben Zeitbasis mitgeschrieben. Zweck ist **Korrelationsprüfung im Nachhinein**, nicht Unterdrückung im Vorfeld.
Erst wenn F7 zeigt, dass der Rauschboden die Zeltkurve verdeckt, wird Isolation zum Thema — dann als gemessene Notwendigkeit, nicht als Vorabinvestition.

### F9 · Datenführung
**Aus:** Präregistrierung, Nullergebnis-Pipeline
**Spezifikation:** Run-ID-System, Rohdaten unverändert archiviert, Messkonfiguration versioniert, Auswertung skriptgebunden und wiederholbar, Nullresultate dokumentiert wie Positivresultate.

### F10 · Fertigung und Montage
**Aus:** Aufbau
**Spezifikation:** Feinmontage, Bohren, Gewinde, Spanntechnik, Messschieber/Mikrometer/Richtplatte, 3D-Druck für Vorrichtungen und Sensorhalter. Dreh-/Frästeile und Präzisionsteile extern (§7).

---

## 4 · Gates

| Gate | Inhalt | Zwingende Fähigkeiten | Eintrittskriterium ins nächste Gate |
|---|---|---|---|
| **G0** | Papierlage, Parameterklärung, Präregistrierung geschärft | — | §1.1 gelöst; ε_⊥, ε_phys-Verfahren festgelegt |
| **G1** | Kontaktcharakterisierung, Rauschboden, Rig-FRF | F1, F2, F3, F4, F7, F9, F10 | k und c bekannt; f_c bekannt; R3/R4 zahlenmäßig gesetzt; Rauschboden < erwartete F_min-Spanne |
| **G2** | Strukturnachweis Linie A: Zeltkurve F_min(φ₂) bei festem φ₃ | + F5, F6, F8 | Zeltkurve reproduzierbar über getrennte Blöcke und randomisierte Reihenfolge |
| **G3** | Quantitative Phasenkarte, volle 2D-Sweep, Unsicherheitsbudget | + externe Kalibrierung, Bootstrap-Auswertung, k als zweite Achse | Karte gegen Simulation abgeglichen; Abweichungen zugeordnet |
| **G4a** | Linie B, separater Aufbau (§6) | eigener Fähigkeitssatz | ρ-Steigung bestimmt oder Nullergebnis dokumentiert |
| **G4b** | Rückführbare Kalibrierung, unabhängige Replikation extern | externe Messkette, Partneraufbau | unabhängige Bestätigung oder Widerlegung |
| **G5** | Erweiterung: L3, mehrere Stände, Vergleichssysteme | — | erst nach G3 sinnvoll zu spezifizieren |

**Gate-Regel:** Keine Fähigkeit wird beschafft, deren Gate nicht das nächste ist. Die vier Infrastrukturklassen der Vorgängerliste (I–IV) sind hier durch G1–G5 ersetzt, weil Klassen nach Ausstattung sortieren und Gates nach Erkenntnisstand.

---

## 5 · Was an welchem Gate *nicht* nötig ist

| Vorgängerliste fordert | Frühestens nötig ab | Begründung |
|---|---|---|
| separates Messfundament, schwimmende Entkopplung | nach G1, nur falls F7 es erzwingt | Signal ist O(1) gegenüber Mg; Messung ist differenziell |
| EMV-reduzierte Umgebung, Abschirmung | G4b, wenn überhaupt | Signalpegel und Bandbreite geben das nicht her |
| Klimatisierung, Feuchteregelung | G4b | F6 deckt Drift über Referenzphasen ab |
| optische/berührungslose Messtechnik | G3 | vor bekanntem k ohne Bezugsgröße |
| Hochgeschwindigkeitskamera, Vibrometer | G3/extern | Leihe oder Partnerlabor, kein Bestand |
| Maschinenwerkstatt (Drehen, Fräsen, Schweißen) | nie intern | externe Fertigung (§7) |
| Personalstruktur | G5 | vor G3 keine ableitbare Stellenbeschreibung |
| Gebäude-, Umbau-, Neubezugsplanung | G5 | Konsequenz, nicht Prämisse |

---

## 6 · Linie B — getrennter Fähigkeitssatz

Die Vorgängerliste enthält Linie B **überhaupt nicht**. Luftströmung erscheint dort ausschließlich als Störgröße (Abschnitte 2 und 12). Für H1_fluid ist die Mediendichte die *unabhängige Variable*.

| Fähigkeit | Spezifikation |
|---|---|
| **B1 · Mediendichtevariation** | Gasaustausch in geschlossenem Behälter statt Vakuum. He ≈ 0,17 · Ar ≈ 1,66 · Luft ≈ 1,20 · CO₂ ≈ 1,84 kg/m³ (20 °C, 1 bar). Mit moderater Druckvariation ergibt sich ein ρ-Bereich von ≈ 0,17 bis ≈ 5 kg/m³, also Faktor ~30. |
| **B2 · Driftstrecke** | reibungsarme Lagerung mit definiertem Weg — Pendelaufhängung (bifilar) oder Luftlager; die vorhandenen Pendeltest-Protokolle sind der Ausgangspunkt |
| **B3 · Wegmessung** | Driftweg und -richtung, optisch, mit derselben Zeitbasis wie Phasenreferenz |
| **B4 · Gassicherheit** | O₂-Warner, Zwangslüftung, Betriebsanweisung. Erstickungsgefahr bei He/Ar/CO₂ in geschlossenen Räumen ist real und nicht optional. |

**Methodischer Kernpunkt:** Der Gasaustausch liefert eine **ρ-Steigung**, ein Vakuumversuch nur ein Ja/Nein. Die Steigung ist die stärkere Prüfung, weil sie die vorhergesagte Proportionalität testet statt nur ihre Existenz — und sie ist um Größenordnungen billiger als eine Vakuumkammer.

**Nicht verwenden:** SF₆, obwohl es mit ≈ 6,2 kg/m³ die größte Dichte böte. F-Gas-reguliert, Rückhaltepflicht, sehr hohes Treibhauspotenzial. In einem Kleinlabor unverhältnismäßig.

**Querbezug zu Linie A:** Wenn die Medienkopplung real ist, ist der Linie-A-Aufbau in Luft nicht mediumsfrei. B1 dient Linie A dann als Artefaktkontrolle. Das macht die Dichtevariation zu einer *gemeinsam genutzten* Fähigkeit, nicht zu einem Linie-B-Sonderposten — allerdings erst ab G3, nicht ab G1.

---

## 7 · Bezugsweg je Fähigkeit

| Fähigkeit | intern | extern | vertagt |
|---|---|---|---|
| F1 Kraftinterface | ✔ | Kalibrierung | |
| F2 Kontaktcharakterisierung | ✔ | | |
| F3 DAQ | ✔ | | |
| F4 dynamische Kalibrierung | Rig-FRF selbst | Referenzshaker / akkreditiertes Labor | |
| F5 Phasenstellung | ✔ (ESP32-Firmware vorhanden) | | |
| F6 Kampagnenführung | ✔ | | |
| F7 Rauschboden | ✔ | | |
| F8 Umgebungsdiagnostik | ✔ (2 Kanäle) | | |
| F9 Datenführung | ✔ | | |
| F10 Fertigung | Montage, Bohren, Gewinde, 3D-Druck | Dreh-/Frästeile, Präzisionsteile, CNC | |
| Rückführbare Kalibrierung | | akkreditiertes Kalibrierlabor | ab G3 |
| Optische Messtechnik | | Partnerlabor / Leihe | ab G3 |
| Unabhängige Replikation | | Partneraufbau | ab G4b |
| B1–B4 Linie B | Behälter, Wegmessung | Gasbezug, Sicherheitstechnik | ab G4a |

**Grundsatz:** Rückführbarkeit wird nie im Haus aufgebaut. Fertigungstiefe bleibt auf Montageniveau. Was nur einmal gebraucht wird, wird geliehen oder vergeben.

---

## 8 · Räumliche Konsequenz (Ergebnis, nicht Ausgangspunkt)

| Gate | Flächenbedarf | Anforderung |
|---|---|---|
| G1–G2 | ein stabiler Tisch, ~6 m² plus Ablage | schwere Basis, keine Sonderbaumaßnahme; abschließbar; konstante Aufstellung über Kampagnendauer |
| G3 | separater ruhiger Raum, ~15–20 m² | getrennt von Montagetätigkeit; Temperatur protokolliert, nicht geregelt |
| G4a | zusätzlicher Raum mit Zwangslüftung | Gasbehälter, Driftstrecke, O₂-Überwachung |
| G4b/G5 | dann erst Gebäudefrage | vorher nicht spezifizierbar |

Die Vorgängerliste beginnt mit Standortwahl, Baugrund und Fundament. Das ist die Reihenfolge umgekehrt.

---

## 9 · Organisatorische Festlegungen

Unabhängig von der gewählten Variante zu regeln:

- Eigentum am Aufbau und an den Geräten
- Rohdatenrechte und Archivierungsort
- Verantwortung für Messprotokoll und Kalibrierstand
- Veröffentlichungsrechte und Autorenschaft
- Wartungs- und Sicherheitsverantwortung
- Zugriff externer Gutachter auf Rohdaten, nicht nur auf Auswertungen

**Varianten** (Entscheidung gehört nach G1, nicht davor):

- **A · Partnerlabor** — minimale eigene Infrastruktur, externe Nutzung hochwertiger Messtechnik
- **B · eigener kleiner Aufbau** — Aufbau, Steuerung und Messung unter eigener Kontrolle, Kalibrierung und Review extern
- **C · institutionelle Einbettung** — Labor, Messtechnik und unabhängige Verifikation innerhalb einer Forschungseinrichtung

Die Fähigkeitsmatrix macht die Varianten vergleichbar: Für jede Variante wird geprüft, welche der Fähigkeiten F1–F10 sie abdeckt und welche offen bleiben. Erst diese Deckungsanalyse — nicht der Kostenrahmen — entscheidet.

---

## 10 · Nächste Festlegungen

1. Parameterkonflikt §1.1 gegen den Code auflösen. Blockiert jede Zahl in §3.
2. Verfahren zur Bestimmung von ε_phys festlegen (Ergebnis von F7, nicht Vorgabe).
3. ε_⊥ als Bruchteil der Auflagerbreite definieren, nicht als absolute Kraft.
4. Asymmetrieverhältnis-Definition in Präregistrierung, Symbolverzeichnis, Laborplan und Messtechnik-Konzept nachziehen.
5. Deckungsanalyse A/B/C gegen F1–F10 durchführen, sobald 1.–3. stehen.
