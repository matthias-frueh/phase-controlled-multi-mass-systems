# PCMMS · Wissenschaftliches Anforderungsprofil

**Projekt:** PCMMS — Phase-Controlled Multi-Mass Systems
**Verfasser:** Matthias Früh · ORCID 0009-0005-9984-4207
**Stand:** September 2026 · Forschungsstand präexperimentell
**Dokument 1 von 2.** Gegenstück: *PCMMS · Betriebs- und Infrastrukturplanung*

---

## 0 · Zweck, Geltung und Statuskennzeichnung

Dieses Dokument beantwortet ausschließlich:

> Welche experimentelle **Fähigkeit** mit welcher **Mindestspezifikation** ist an welchem **Forschungsgate** zwingend, und woraus folgt sie?

Ableitungsrichtung durchgehend: **Observable → Kanal → Spezifikation → Gate → Bezugsweg.**

Es ist keine Einkaufsliste und keine Raum-, Personal- oder Organisationsplanung. Diese Themen stehen vollständig in Dokument 2. Änderungslogik: Dieses Dokument wird durch **Messergebnisse** fortgeschrieben, insbesondere nach G1. Dokument 2 ändert sich nur bei Träger- oder Standortwechsel.

**Statusmarker** — jede Anforderung trägt genau einen:

| Marker | Bedeutung |
|---|---|
| **[B]** | bindend; gilt jetzt und ist nicht verhandelbar |
| **[O]** | offen; muss von Matthias gesetzt oder aus der Ablage aufgelöst werden |
| **[G1]** | folgt erst nach G1 aus Messdaten; vorher nur parametrisch formulierbar |

---

## 1 · Wissenschaftlicher Ausgangspunkt

### 1.1 Zwei Forschungslinien

Die beiden Linien teilen weder Aufbau noch Messgröße und dürfen nicht vermischt werden. Die Präregistrierung (Juni 2026) ist die gemeinsame Klammer und nennt beide.

| | **Linie A** | **Linie B** |
|---|---|---|
| Hypothese | H1 | H1_fluid |
| Status | primär | ausdrücklich optional, **separater Aufbau** |
| Gegenstand | Wellenformstatistik der unilateralen Kontaktkraft bei **stationärem** Körper | gerichtete Nettobewegung durch Impulsübertragung an das umgebende Medium |
| unabhängige Variable | relative Phase (φ₂, φ₃) | Mediendichte ρ |
| Erhaltungsbezug | ⟨N⟩ = M·g als Nullbasislinie | Impulsbilanz mit Medium |
| Prüfform | Zeltkurve F_min(φ₂) | ρ-Steigung der Drift |

Beide Linien sind erhaltungskonform. Keine ist widerlegt. Ein Nullergebnis in einer Linie berührt die andere nicht.

### 1.2 Systemebenen

| Ebene | Funktion | Status |
|---|---|---|
| **L0** | passiver Messrahmen / Referenzsystem | implementiert |
| **L1** | aktiver Träger mit eigenen Freiheitsgraden | Konzept |
| **L2** | Module, Bahnprofile, Phasenkontrolle | implementiert |
| **L3** | Kopplung L1 ↔ L2, Reaktionskräfte, Residualdynamik | offen |

**[B]** L0 ist Mess- und Referenzsystem, nicht Untersuchungsobjekt. Diese Trennung ist messtechnisch, räumlich und in der Datenführung durchzuhalten.

### 1.3 Was das Projekt nicht behauptet

Klassische Mehrkörpermechanik. Keine neue Physik, kein reaktionsloser Antrieb, keine Antigravitation, kein Perpetuum mobile. Der zeitliche Mittelwert der Kontaktkraft ist Bilanz- und Kontrollgröße, keine Effektgröße.

---

## 2 · Bezugsgrößen

### 2.1 [O] Parameterkonflikt — blockiert jede konkrete Zahl

In der Ablage stehen zwei unvereinbare Parametersätze:

| Quelle | Masse | Mg | Frequenz |
|---|---|---|---|
| Bindende Parameter (00_INDEX) | 0,650 kg **je Modul** × 3 Module = 1,95 kg | ≈ **19,1 N** | **2,2 Hz** |
| Laborplan V1/V2 (Mai 2026) | ≈ 0,65 kg **gesamt** | ≈ **6,4 N** | **10 Hz**, Hub „einige mm" |

**Warum das auslegungsbestimmend ist:**

1. Gleiche Spitzenbeschleunigung skaliert mit A ∝ 1/f².
   (10 / 2,2)² ≈ **20,7**.
   Bei 2,2 Hz braucht dieselbe Liftoff-Bedingung rund **zwanzigfachen Hub** — aus „einige mm" wird ~10 cm. Das ändert Aktuatorklasse, Modulgeometrie, Gehäuse, Aufstandsfläche und Fertigungsbedarf grundlegend.
2. Mg legt Nennbereich, Überlastgrenze und Auflösungsanforderung der gesamten Kraftmesskette fest (§5, F1).

**Indiz zur Auflösung:** F_min erreicht im Feinsweep maximal ≈ **5,33 N**. Das ist mit Mg ≈ 6,4 N verträglich und mit Mg ≈ 19,1 N nur schwer. Der Verdacht richtet sich damit gegen die Zeile „0,650 kg je Modul", nicht gegen die Laborpläne.

**Auflösung: gegen `pcmms_v3a_phasen_sweep.py` prüfen, nicht gegen Textdokumente.** Der Code ist die Quelle, aus der die Sweepdaten stammen; die Dokumente sind abgeleitet und können den Fehler tragen.

Solange dies offen ist, sind alle Spezifikationen unten **parametrisch in M und f** formuliert und damit in beiden Zweigen gültig. Nach Auflösung sind sie in einem Durchgang zahlenmäßig einsetzbar.

### 2.2 Weitere offene Größen

| Größe | Status | Anmerkung |
|---|---|---|
| **ε_⊥** | **[O]** | Querbilanzschwelle; an geometrische Referenz (Auflagerbreite) binden, nicht als absolute Kraft |
| **ε_phys** | **[O]** Verfahren / **[G1]** Wert | Verfahren jetzt festlegen, Zahl aus F7 |
| **k** (Kontaktsteifigkeit) | **[G1]** | Messziel von G1 |
| **c** (Dämpfung) | **[G1]** | Messziel von G1 |
| **f_c** = (1/2π)·√(k/M) | **[G1]** | folgt aus k; Eingang in F3 |

### 2.3 [B] Mitgeführte Korrektur

**Asymmetrieverhältnis = (F_max − Mg) / (Mg − F_min)**, so wie im Code implementiert. **Nicht** max(F)/⟨F⟩.

Die abweichende Definition steht noch in Präregistrierung, Symbolverzeichnis, Laborplan und Messtechnik-Konzept und ist dort nachzuziehen. Sie darf hier nicht weitergetragen werden.

### 2.4 [B] Weitere feste Größen

- Egg-Profil mit Hold-/Schnell-Asymmetrie, C¹-Stetigkeit am Nahtpunkt, Zyklusbilanzbedingung
- Triphasische Konfiguration (120°, 240°)
- Feinsweep-Raster 2° über ±20° um den Kompensationspunkt
- ⟨N⟩ = M·g als Erhaltungssatz und Kontrollgröße

---

## 3 · Zielobservablen

### 3.1 Linie A

| Observable | Rolle |
|---|---|
| **F_min(φ)** | **primär**; Zeltkurve, ohne Statistik sichtbar; schärfste verfügbare Testform |
| **Liftoff-Anteil** | primär |
| **Schiefe von N(t)** | primär; bei bimodaler Verteilung im hohen Liftoff-Regime schlecht konditioniert → Bootstrap-Konfidenzintervalle statt Punktschätzer |
| **Asymmetrieverhältnis** | primär, Definition nach §2.3 |
| **⟨N⟩** | **Kontrollgröße, keine Messgröße** |
| **ε_⊥** | Querbilanz, Artefaktausschluss |

**[B] Harter Stopp:** Weicht ⟨N⟩ dauerhaft von der statischen Last ab, jenseits der Kalibrierunsicherheit, ist das eine defekte Messkette — kein Befund. Apparatur prüfen und reparieren, nicht interpretieren.

### 3.2 Linie B

| Observable | Rolle |
|---|---|
| gerichtete Nettodrift | primär |
| **Drift als Funktion von ρ** | **die eigentliche Prüfgröße** — die Steigung, nicht der Einzelwert |

### 3.3 [B] Messprinzip: differenziell

**Gemessen werden Kraftverschiebungen, keine Kräfte.**

φ ist ein reiner Softwareparameter. Der Aufbau bleibt zwischen den Sweeppunkten mechanisch identisch. Das Experiment ist ein Innerhalb-Aufbau-Vergleich. Umgebungseinflüsse gehen deshalb nur über ihre **Änderung innerhalb eines Sweepblocks** ein, nicht über ihren Absolutwert.

Konsequenz für die gesamte Auslegung:

- auslegungsbestimmend: **Kurzzeit-Wiederholpräzision, Kanalabgleich, Bandbreite**
- *nicht* auslegungsbestimmend: absolute Genauigkeit, Rückführbarkeit, Umgebungsstabilisierung

Dies ist der Grund, warum ein erheblicher Teil klassischer Laborinfrastruktur hier methodisch ersetzbar ist (F6).

---

## 4 · Fähigkeitskatalog Linie A

### F1 · Dreipunkt-Kraftinterface

| Anforderung | Wert | Status |
|---|---|---|
| Kanalzahl | ≥ 3, Dreieckanordnung | **[B]** |
| Nennbereich je Kanal | ≥ 3·Mg | **[B]** |
| Überlastgrenze | ≥ 5·Mg | **[B]** |
| Auflösung je Kanal | ≤ 0,005·Mg | **[B]** |
| Kopplung | DC-fähig (DMS; nicht ladungsgekoppelt ohne Langzeitkonstante) | **[B]** |
| mechanische Aufnahme | definiert, reproduzierbar demontierbar | **[B]** |

**Begründung Kanalzahl:** ε_⊥ ist der Druckmittelpunkt der Auflagerkräfte. **Mit einem einzelnen Kanal existiert die Größe nicht.** Harte Anforderung, keine Ausbauoption.

**Begründung Bereich:** Asymmetrieverhältnis bis ≈ 6,9 in der Simulation ⇒ F_max deutlich über Mg. Überlastreserve wegen Wiederaufsetzstößen bei intermittierendem Kontakt.

**Ausdrücklich nicht gefordert:** absolute Auflösung von F_min ≈ 0,006 N. Die Zeltkurve durchläuft nahezu den vollen Bereich 0…Mg; F_min-Werte nahe null sind ein Artefakt der Kontaktmodellierung in der Simulation und kein Auslegungstreiber. Wer hier µN-Metrologie ansetzt, dimensioniert am Signal vorbei.

### F2 · Kontaktcharakterisierung (k, c)

**[B]** Erste Fähigkeit in der Reihenfolge — **nicht** die Phasensteuerung.

| Anforderung | Inhalt |
|---|---|
| statische Kennlinie | k über den gesamten genutzten Federweg, Linearitätsabweichung dokumentiert |
| Ausschwing-/Impulsversuch | Dämpfungsmaß c, Kontaktresonanz f_c |
| Kontaktelemente | charakterisiert und austauschbar, damit k später zweite Sweepachse wird |
| Ergebnis | **f_c = (1/2π)·√(k/M)** — Eingangsgröße für F3 |

**Vor bekanntem k sind Bandbreite und Abtastrate nur symbolisch formulierbar.** Jede Beschaffungsentscheidung zur DAQ vor G1 ist eine Wette.

### F3 · Synchrone Mehrkanalerfassung

| Anforderung | Wert | Status |
|---|---|---|
| Bandbreite (−3 dB) der **gesamten** Kette inkl. Sensoraufnahme | ≥ max(20·f, 5·f_c) | **[B]** parametrisch / **[G1]** numerisch |
| Abtastrate | ≥ 10 × Bandbreite | **[B]** |
| Gleichzeitigkeit | **simultan**, kein Multiplex über die Kraftkanäle | **[B]** |
| Kanalversatz | ≤ 1/(100 · Bandbreite) | **[B]** |
| Zeitbasis | eine gemeinsame für Kraft, Position, Antriebsreferenz; Hardware-Timestamping | **[B]** |

**Kanalbelegung (11):** 3 × Kraft · 1 × Dummy · 3 × Phase/Position · 1 × optischer Weg · 1 × Beschleunigung · 1 × Temperatur · 1 × Reserve

Der Faktor 20·f sichert die Oberwellen der Kontaktflanken, der Faktor 5·f_c die Kontaktresonanz selbst. Maßgeblich ist der größere der beiden.

### F4 · Dynamische Kalibrierung bei intermittierendem Kontakt

**[B]** Dies ist die eigentliche messtechnische Schwierigkeit des Projekts — nicht die absolute Kraftmessbarkeit. Statische Rückführung (DKD-R 3-10) ist verfügbar und unkritisch.

| Anforderung | Inhalt |
|---|---|
| Übertragungsfunktion des Kraftpfads | Impulshammer oder Shaker mit Referenzaufnehmer, bis zur höchsten relevanten Harmonischen |
| Formtreue | Nachweis, dass Kontaktabriss- und Wiederaufsetzflanken formtreu abgebildet werden, nicht nur Amplituden |
| Rig-FRF | vor jeder Kampagne, dokumentiert und versioniert |
| Liftoff-Gegenprobe | über den **unabhängigen** Beschleunigungskanal, nicht über den Kraftkanal |

### F5 · Phasenstellung und Profilverifikation

| Anforderung | Wert | Status |
|---|---|---|
| Sweepraster | 2° | **[B]** |
| zulässiger Phasenjitter | ≤ 0,2° (10 % des Rasters) | **[B]** |
| daraus Zeitbudget | Δt ≤ (0,2/360) · 1/f | **[B]** |
| — bei f = 2,2 Hz | ≤ **253 µs** | |
| — bei f = 10 Hz | ≤ **56 µs** | |
| Profilverifikation | Soll-Ist des gefahrenen Egg-Profils, Positionsauflösung ≤ 1 % des Hubs | **[B]** |
| Profilgenerator | C¹-Bedingung am Nahtpunkt und Zyklusbilanz **geprüft**, nicht angenommen | **[B]** |

**Befund: Synchronität ist nicht der Engpass.** Beide Budgets sind mit Hardware-Timestamping trivial erreichbar. Jitterüberwachung, Phasendriftmessung und Synchronisationsdiagnostik als eigenständige Ausbaustufe sind überdimensioniert.

### F6 · Differenzielle Kampagnenführung

| Anforderung | Wert | Status |
|---|---|---|
| φ-Reihenfolge | randomisiert innerhalb jedes Sweepblocks | **[B]** |
| Referenzphase | in festem Intervall eingestreut, Rückkehr auf denselben Punkt | **[B]** |
| Nullpunktdrift je Block | ≤ 0,002·Mg, **über die Referenzphasenwiederholung nachgewiesen** | **[B]** |
| Dummy-Kanal | über die gesamte Kampagne mitlaufend | **[B]** |
| Auswertung | blockweise; Welch–Satterthwaite bei α = 0,05 | **[B]** |

**Diese Fähigkeit kostet nichts und ersetzt einen erheblichen Teil der klassischen Umgebungsinfrastruktur** — Messfundament, Klimatisierung, EMV-Umgebung. Sie ist methodisch außerdem stärker, weil sie Drift **nachweist** statt sie zu unterstellen. Eine randomisierte Reihenfolge mit Referenzrückkehr trennt Driftartefakte von φ-Abhängigkeit; ein ruhiger Raum tut das nicht.

Sie ist deshalb **nicht** eine Fähigkeit unter zehn, sondern der methodische Hebel, der die Infrastrukturfrage entschärft.

### F7 · Rauschboden und Nachweisschwelle

| Messung | Zweck |
|---|---|
| Leermessung | Grundrauschen der Kette |
| Dummy-Messung | Kanalgleichlauf, Übersprechen |
| Aktuatorlauf mit unterdrückter Innenbewegung | Anteil von Antriebsgeräusch und Strukturkopplung |
| Wiederholstreuung über Blöcke | praktische Wiederholpräzision |

**[B]** Ergebnis ist die empirische Schwelle, gegen die **ε_phys** gesetzt wird. **ε_phys darf nicht vor dieser Messung numerisch festgeschrieben werden.** Eine vorab gesetzte Schwelle ist entweder unerreichbar oder trivial erfüllbar; beides entwertet die Präregistrierung.

**Hinweis zur Streuung:** σ_F = 4,58 mN aus der Simulation ist eine **Sweep-zu-Sweep-Schätzervarianz**, keine Run-zu-Run-Messvarianz. Sie darf nicht als erwarteter experimenteller Rauschboden verwendet werden.

### F8 · Umgebungsdiagnostik (nicht Umgebungskontrolle)

**[B]** Ein Beschleunigungsaufnehmer an der Basis plus Temperaturkanal, beide auf derselben Zeitbasis mitgeschrieben.

Zweck ist **Korrelationsprüfung im Nachhinein**, nicht Unterdrückung im Vorfeld. Erst wenn F7 zeigt, dass der Rauschboden die Zeltkurve verdeckt, wird Isolation zum Thema — dann als gemessene Notwendigkeit, nicht als Vorabinvestition.

### F9 · Datenführung

**[B]** Run-ID-System · Rohdaten unverändert archiviert · Messkonfiguration versioniert · Auswertung skriptgebunden und wiederholbar · Nullresultate dokumentiert wie Positivresultate.

Zielkette: `u(t) → x(t) → y_meas(t) → Auswertefenster → Kennzahl → statistischer Test`

**[B]** Nullergebnisse sind ein gültiges publizierbares Ergebnis. Das ist ein Entwurfsprinzip, kein Rückfallplan.

### F10 · Fertigung und Montage

**[B]** intern: Feinmontage, Bohren, Gewinde, Spanntechnik, Messschieber/Mikrometer/Richtplatte, 3D-Druck für Vorrichtungen und Sensorhalter.
**[B]** extern: Dreh-, Fräs- und hochpräzise Sonderteile grundsätzlich als externe Leistung.

---

## 5 · ε-Schwellen

### 5.1 ε_phys

**[O]** Verfahren jetzt festzulegen, **[G1]** Wert aus F7.

Empfohlene Bindung: ε_phys als Vielfaches der empirischen Wiederholstreuung des jeweiligen Observablen über Blöcke, nicht als absolute Kraftgröße. Damit ist die Schwelle apparaturbezogen und bleibt bei Aufbauänderung nachvollziehbar anpassbar.

### 5.2 ε_⊥

**[O]** Von Matthias zu setzen.

Lateralbilanz: `| Σ_k (d²r_k/dt²)_⊥ | ≤ ε_⊥`

Empfohlene Bindung: an eine geometrische Referenz — Verschiebung des Druckmittelpunkts als Bruchteil der Auflagerbreite des Dreipunkt-Interfaces. **Nicht** als absolute Kraft- oder Beschleunigungsgröße, weil die Größe sonst nicht zwischen Aufbauvarianten übertragbar ist.

---

## 6 · Gates

| Gate | Inhalt | Zwingende Fähigkeiten | Eintrittskriterium ins nächste Gate |
|---|---|---|---|
| **G0** | Papierlage: Parameterkonflikt, ε-Verfahren, Präregistrierung geschärft | — | §2.1 aufgelöst; Verfahren für ε_phys und ε_⊥ festgelegt |
| **G1** | Kontaktcharakterisierung, Rauschboden, Rig-FRF | F1, F2, F3, F4, F7, F9, F10 | k, c, f_c bekannt; F3 zahlenmäßig gesetzt; Rauschboden < erwartete F_min-Spanne |
| **G2** | Strukturnachweis Linie A: Zeltkurve F_min(φ₂) bei festem φ₃ = 240° | + F5, F6, F8 | Zeltkurve reproduzierbar über getrennte Blöcke und randomisierte Reihenfolge — oder belastbarer Null-/Inconclusive-Befund |
| **G3** | Quantitative Phasenkarte, 2D-Sweep, Unsicherheitsbudget | + externe Kalibrierung, Bootstrap, k als zweite Achse | Karte gegen Simulation abgeglichen, Abweichungen zugeordnet |
| **G4a** | Linie B, separater Aufbau (§7) | B1–B4 | ρ-Steigung bestimmt oder Nullergebnis dokumentiert |
| **G4b** | Rückführbare Kalibrierung, unabhängige Replikation | externe Messkette, Partneraufbau | unabhängige Bestätigung oder Widerlegung |
| **G5** | L3, mehrere Stände, Vergleichssysteme | projektspezifisch | erst nach G3 wissenschaftlich spezifizierbar |

### 6.1 [B] Gate-Regel

Keine Fähigkeit wird beschafft, deren Gate nicht das nächste ist. Ein größerer Aufbau muss aus dem **nächsten** Gate begründet werden, nicht aus einem denkbaren späteren.

### 6.2 Verzweigung, keine Treppe

Bis G3 ist die Abfolge linear. **Danach verzweigt sie.** Quantitative Phasenkarte, L3-Kopplungsdynamik, metrologische Verifikation, Linie B und spätere Vergleichssysteme sind unabhängige Pfade mit unterschiedlichem Fähigkeitsbedarf. Kein Pfad zieht die anderen automatisch nach sich.

---

## 7 · Linie B — getrennter Fähigkeitssatz

**[B]** Eigener Aufbau, eigene Sicherheitsbetrachtung, eigene Auswertung. Keine gemeinsame Nutzung der Linie-A-Messzone während laufender A-Kampagnen.

### B1 · Mediendichtevariation

**Gasaustausch in geschlossenem Behälter statt Vakuum.**

| Medium | ρ bei 20 °C, 1 bar |
|---|---|
| Helium | ≈ 0,17 kg/m³ |
| Luft | ≈ 1,20 kg/m³ |
| Argon | ≈ 1,66 kg/m³ |
| Kohlendioxid | ≈ 1,84 kg/m³ |

Mit moderater Druckvariation ergibt sich ein Bereich von ≈ **0,17 bis ≈ 5 kg/m³**, also **Faktor ~30**.

**[B] Methodischer Kernpunkt:** Der Gasaustausch liefert eine **ρ-Steigung**, ein Vakuumversuch nur ein Ja/Nein. Die Steigung prüft die vorhergesagte Proportionalität; das binäre Ergebnis prüft nur ihre Existenz. Die Steigung ist damit der **stärkere** Test — und sie ist um Größenordnungen billiger als eine Vakuumkammer.

**[B] Ausschluss:** SF₆ wird nicht verwendet, obwohl es mit ≈ 6,2 kg/m³ die größte Dichte böte. F-Gas-reguliert, Rückhalte- und Dokumentationspflicht, sehr hohes Treibhauspotenzial. In einem Kleinlabor unverhältnismäßig.

### B2 · Driftstrecke

Reibungsarme Lagerung mit definiertem Weg — bifilare Pendelaufhängung oder Luftlager. Die vorhandenen Pendeltest-Protokolle sind der Ausgangspunkt.

### B3 · Wegmessung

Driftweg und -richtung, optisch, auf derselben Zeitbasis wie die Phasenreferenz.

### B4 · Gassicherheit

**[B]** O₂-Warner, Zwangslüftung, Betriebsanweisung, Behältermanagement. Erstickungsgefahr bei He/Ar/CO₂ in geschlossenen Räumen ist real und nicht optional. Details in Dokument 2, §8.

### B5 · Querbezug zu Linie A

Wenn die Medienkopplung real ist, ist der Linie-A-Aufbau in Luft **nicht mediumsfrei**. B1 dient Linie A dann als Artefaktkontrolle. Die Dichtevariation ist damit eine gemeinsam nutzbare Fähigkeit — allerdings erst ab G3, nicht ab G1.

---

## 8 · Was an welchem Gate *nicht* nötig ist

| Häufig gefordert | Frühestens nötig ab | Begründung |
|---|---|---|
| separates Messfundament, schwimmende Entkopplung | nach G1, **nur falls F7 es erzwingt** | Signal ist O(1) gegenüber Mg; Messung ist differenziell |
| EMV-reduzierte Umgebung, Abschirmung | G4b, wenn überhaupt | Signalpegel und Bandbreite geben das nicht her |
| Klimatisierung, Feuchteregelung | G4b | F6 deckt Drift über Referenzphasen ab |
| optische / berührungslose Messtechnik | G3 | vor bekanntem k ohne Bezugsgröße |
| Hochgeschwindigkeitskamera, Laser-Vibrometer | G3, extern oder Leihe | Einmalbedarf, kein Bestand |
| Maschinenwerkstatt (Drehen, Fräsen, Schweißen) | nie intern | externe Fertigung |
| µN-Metrologie, rückführbare Absolutgenauigkeit | G4b, extern | Messung ist differenziell |

**[B]** „Nicht jetzt erforderlich" heißt nicht „wissenschaftlich nie relevant".

---

## 9 · Bezugsweg je Fähigkeit

| Fähigkeit | intern | extern | vertagt |
|---|---|---|---|
| F1 Kraftinterface | ✔ | Kalibrierung | |
| F2 Kontaktcharakterisierung | ✔ | | |
| F3 DAQ | ✔ | | |
| F4 dynamische Kalibrierung | Rig-FRF selbst | Referenzshaker / akkreditiertes Labor | |
| F5 Phasenstellung | ✔ (vorhandene Firmwarebasis) | | |
| F6 Kampagnenführung | ✔ | | |
| F7 Rauschboden | ✔ | | |
| F8 Umgebungsdiagnostik | ✔ (2 Kanäle) | | |
| F9 Datenführung | ✔ | | |
| F10 Fertigung | Montage, Bohren, Gewinde, 3D-Druck | CNC, Präzisionsteile | |
| Rückführbare Kalibrierung | — | akkreditiertes Kalibrierlabor | ab G3 |
| Optische Messtechnik | — | Partnerlabor / Leihe | ab G3 |
| Unabhängige Replikation | — | Partneraufbau | ab G4b |
| B1–B4 Linie B | Behälter, Wegmessung | Gasbezug, Sicherheitstechnik | ab G4a |

**[B] Grundsatz:** Rückführbarkeit wird nicht im Haus aufgebaut. Fertigungstiefe bleibt auf Montageniveau. Was nur einmal gebraucht wird, wird geliehen oder vergeben.

---

## 10 · Deckungsmatrix

Vergleichsinstrument für Infrastrukturvarianten. Nicht „Was kostet ein Labor?", sondern:

> Welche der Fähigkeiten F1–F10 deckt die Variante ab, und welche bleiben offen?

Bewertung je Zelle: **voll / teilweise / nicht / extern beziehbar**

| Fähigkeit | Partnerlabor | eigener kleiner Aufbau | institutionelle Einbettung | Mischmodell |
|---|---|---|---|---|
| F1 Dreipunkt-Kraftinterface | | | | |
| F2 Kontaktcharakterisierung | | | | |
| F3 Synchrone Erfassung | | | | |
| F4 Dynamische Kalibrierung | | | | |
| F5 Phasenstellung | | | | |
| F6 Kampagnenführung | | | | |
| F7 Rauschboden | | | | |
| F8 Umgebungsdiagnostik | | | | |
| F9 Datenführung | | | | |
| F10 Fertigung / Montage | | | | |
| B1–B4 Linie B | | | | |
| Rückführbare Kalibrierung | | | | |
| Unabhängige Replikation | | | | |
| **Verfügbarkeit / Messzeit** | | | | |
| **Kontrolle über Rohdaten** | | | | |

Die beiden letzten Zeilen sind keine Fähigkeiten, entscheiden aber praktisch mit: Eine Variante, die F1–F10 abdeckt, aber nur vier Messtage im Quartal bietet, trägt eine 21-Punkt-Sweepkampagne nicht.

**[B]** Diese Deckungsanalyse entscheidet, nicht der Kostenrahmen. Betriebliche und organisatorische Bewertung der Varianten: Dokument 2, §14.

---

## 11 · Wissenschaftliches Risikoregister

Nur messtechnisch-methodische Risiken. Betriebliche Risiken in Dokument 2, §18.

| Risiko | mögliche Folge | Gegenmaßnahme |
|---|---|---|
| externe Vibration | Signalüberlagerung | messen und korrelieren (F8), erst danach isolieren |
| Sensordrift | scheinbare φ-Abhängigkeit | Referenzphase, Dummy, F6 |
| Phasenjitter | verschmierte Phasenkarte | gemeinsame Zeitbasis (F5) |
| Strukturkopplung | falsche Attribution | Rig-FRF, mechanische Charakterisierung (F4) |
| Reibung / Spiel | Modellabweichung | Konstruktion und Charakterisierung (F2) |
| Kontaktartefakte | falsche Wellenform | unabhängiger Beschleunigungskanal (F4) |
| unzureichende Bandbreite | verschliffene Flanken, falsches F_min | F3 gegen f_c auslegen |
| schlechte Auflösung | Inconclusive | ε_phys empirisch bestimmen (F7) |
| fehlende Querdiagnostik | unerkannte laterale Effekte | ε_⊥, Dreipunkt-Interface (F1) |
| Schiefe bei hohem Liftoff | instabiler Punktschätzer | Bootstrap-CI, F_min als primäre Größe |
| fehlende Unabhängigkeit | schwacher positiver Befund | zweite Messkette / Partneraufbau (G4b) |
| zu frühe Skalierung | mehr Confounder | Gate-Regel §6.1 |
| Verwechslung Linie A / B | Attributionsfehler | getrennte Aufbauten, getrennte Auswertung |

**[B] Zu positiven Befunden:** Ein einzelner Kanal oder ein einzelner Aufbau kann einen interessanten Befund erzeugen, beweist aber nicht dessen Robustheit. Vorgesehene Stufung: (1) interne Reproduzierbarkeit, (2) unabhängige Messkette, (3) unabhängige externe Replikation.

---

## 12 · Statusübersicht

### [B] Bindend — gilt jetzt

Linientrennung A/B · L0-Rolle · ⟨N⟩ als Kontrollgröße mit hartem Stopp · Asymmetrieverhältnis-Definition · Egg-Profil mit C¹-Bedingung · Triphasik (120°, 240°) · 2°-Raster · differenzielles Messprinzip · F1 Kanalzahl und Bereichsfaktoren · F3 Struktur und Gleichzeitigkeit · F5 Jitterbudget · F6 vollständig · F7 als Voraussetzung für ε_phys · Gate-Regel · SF₆-Ausschluss · Grundsatz externe Rückführbarkeit

### [O] Offen — von Matthias zu setzen

1. **Parameterkonflikt §2.1** — gegen den Simulationscode auflösen. Blockiert alle numerischen Werte.
2. **ε_⊥** — als Bruchteil der Auflagerbreite definieren
3. **Verfahren für ε_phys** — Bindung an Wiederholstreuung festlegen
4. **Asymmetrieverhältnis** — Definition in Präregistrierung, Symbolverzeichnis, Laborplan, Messtechnik-Konzept nachziehen

### [G1] Folgt aus Messdaten

k · c · f_c · numerische Bandbreite und Abtastrate (F3) · Zahlenwert ε_phys · Notwendigkeit von Schwingungsisolation · Notwendigkeit von Klimatisierung

---

## 13 · Nächste Schritte in Reihenfolge

1. §2.1 gegen `pcmms_v3a_phasen_sweep.py` auflösen.
2. Alle parametrischen Werte in §4 numerisch einsetzen.
3. ε_⊥ definieren, ε_phys-Verfahren festlegen.
4. Asymmetrieverhältnis-Definition in den vier Folgedokumenten nachziehen.
5. Deckungsmatrix §10 gegen real erreichbare Varianten ausfüllen.
6. Erst danach: betriebliche und organisatorische Bewertung nach Dokument 2.
