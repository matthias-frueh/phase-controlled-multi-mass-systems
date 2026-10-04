# Konzeptbaustein · Mehrkanal-Messarchitektur

> **Vermerk zur Übernahme (04.10.2026).** Konzeptnotiz des Autors vom Mai 2026; Textfassung aus der Quelldatei des
> Autors, Inhalt unverändert, Tabellen und Listen in Markdown gesetzt. Konzept; nicht umgesetzt. Die Notiz entstand im
> Rahmen der Reformulierungs-Notiz v3b und der Kernhypothese v3 (Mittelwertverschiebung), die seit dem Archiv-Vermerk
> ([`../archiv_vermerk_kernhypothese_v3.md`](../archiv_vermerk_kernhypothese_v3.md)) zurückgezogen ist. Die
> Messarchitektur selbst (mehrere synchronisierte Kanäle, Referenzkanal, Residuum gegen ein Modell) ist davon
> unabhängig und Grundlage des Messkettenpakets AP-06. Seit Mai 2026 überholt oder abweichend von den heutigen Regeln:
> - **Bezüge auf v3b/v3:** „nichtlinearer Kontakt aus der v3-Hypothese“, „Observablen aus §3.1 der v3b-Notiz“,
>   „10⁻⁵⁰-Linien“ und die Abschätzung ε_phys ≈ 3·10⁻⁸ N (Abschnitt 7) gehören zur zurückgezogenen Frage nach einem
>   kleinen Mittelwerteffekt. Die heutige Zielgröße ist die Wellenform (F_min − ⟨N⟩, Harmonische 1–3) im Newton- bis
>   Millinewtonbereich; ⟨N⟩ = M·g ist Kontrollgröße. Die 1/√N-Abschätzung gilt nur für weißes, stationäres Rauschen;
>   Drift, 1/f-Rauschen, Nichtlinearität und Übersprechen mitteln sich nicht so heraus.
> - **Driftabzug und Filter:** Stufe 3 der Verarbeitungskette („gleitendes Mittel“) widerspricht der Präregistrierung v2
>   (§5.1, §8.1: keine Softwarefilter; Driftkontrolle über Referenzläufe, Auswertung über ganze Zyklen).
> - **Residuum gegen Modell (6.4):** Die Präregistrierung v2 vergleicht die gemessene Kombination mit der
>   Superpositionsvorhersage aus gemessenen Einzelmodulantworten (H1), nicht mit einem Kontaktmodell; das Kontaktmodell
>   wird in Phase 0 unabhängig charakterisiert (P0.4). Ohne diese Charakterisierung ist ein Residuum kein
>   Mechanismusnachweis.
> - **Kraftkanal:** Der heutige Entwurf sieht drei DC-fähige Wägezellen (Einzelzellkräfte, Kippmoment) mit Abtastung nach
>   Präregistrierung v2, A6, dazu Wegkanal, inertialen Rahmenkanal und Referenzzelle unter Totlast vor (Arbeitsplan AP-06);
>   „Piezo“ und „einzelne Präzisionswaage“ sind Optionen des Konzepts.
> - **Status (Abschnitt 9):** Schritt 2 (Simulation v3a) ist mit anderem Ziel erfolgt (Wellenform statt Mittelwert);
>   Schritte 3–6 sind offen oder durch den Arbeitsplan ersetzt.

*Matthias Früh · Mai 2026 · prä-experimentell · Grundlagenforschung*

## Vorbemerkung

Dieser Baustein präzisiert die in der Reformulierungs-Notiz v3b (§4) angerissene Idee einer Mehrkanal-Messarchitektur. Er beschreibt eine Detektionsstruktur, die Wellenform-Asymmetrien in der Kontaktdynamik eines PCMMS sichtbar machen kann – nicht durch Verlassen auf einen einzelnen Messkanal, sondern durch Kombination unabhängiger Beobachter mit synchronisierter Zeitbasis und gemeinsamer Residualanalyse.

Status: konzeptuell · nicht hardwarespezifisch · keine Bauanleitung. Die Notiz definiert die logische Struktur des Messsystems – konkrete Geräteklassen werden benannt, konkrete Modelle bewusst nicht. Eine spätere institutionelle Fortführung kann auf dieser Struktur aufsetzen.

## 1 · Grundprinzip: Warum mehrere Kanäle

Eine einzelne Präzisionswaage misst F_c(t), aber ihr Signal ist überlagert von Drift, Temperatur, Untergrundvibration, Eigenresonanzen der Lagerung und thermischem Rauschen. Bei einer Zielobservablen, die in der Wellenformstatistik sitzt – nicht im Mittelwert – ist die einzelne Waage nicht ausreichend.

Mehrkanalmessung adressiert dieses Problem durch drei Mechanismen:

- Redundanz: Mehrere physikalisch unabhängige Beobachter messen dieselbe Dynamik. Ein echter Effekt erscheint konsistent in allen Kanälen, ein Artefakt typischerweise nur in einem.
- Modelltrennung: Jeder Kanal misst eine andere Projektion derselben Bewegung. Aus dem Verhältnis lassen sich Effekt und Artefakt trennen – ein Kraftsignal ohne korrespondierende Wegbewegung ist verdächtig.
- Untergrundsubtraktion: Ein dedizierter Referenzkanal liefert das Rauschen des Aufbaus ohne aktive Anregung. Dieser Untergrund wird vom Messsignal abgezogen.

Die Architektur folgt damit derselben Logik wie moderne Präzisionsmessungen in Gravimetrie, LIGO-Klasse-Interferometrie oder Kalorimetrie: nicht ein präziser Sensor, sondern eine Sensor-Kette mit definierter Datenfusion.

## 2 · Die Messkanäle

### 2.1 · Kraftkanal

| Eigenschaft | Beschreibung |
|---|---|
| Zweck | Direkte Messung der Kontaktkraft F_c(t) am Interface zwischen System und Reaktionspartner. |
| Sensorklasse | Präzisions-Wägezelle (Dehnungsmessstreifen) oder piezoelektrischer Kraftsensor. DMS für Mittelwert und niedrige Frequenzen, Piezo für Wellenformdetails und schnelle Liftoff-Übergänge. |
| Erwartete Auflösung | Wägezelle: 10⁻³ – 10⁻⁵ N bei 1 s Mittelung. Piezo: höhere Bandbreite, aber AC-gekoppelt. |
| Bandbreite | DC bis mehrere kHz, abhängig von Sensorklasse. Für Wellenformanalyse mindestens 10× die Anregungsfrequenz. |
| Hauptlimitierungen | Eigenresonanz der Lagerung, Temperaturdrift, mechanische Hysterese, Kreuzeinkopplung von Lateralkräften. |

### 2.2 · Optischer Wegkanal

| Eigenschaft | Beschreibung |
|---|---|
| Zweck | Direkte, mechanisch entkoppelte Messung des vertikalen Versatzes z(t) des Rahmens oder eines definierten Referenzpunkts am System. |
| Sensorklasse | Laser-Interferometer (sub-nm-Auflösung) oder konfokale/triangulierende Laser-Wegsensoren (sub-µm). Wahl nach Bandbreite und Bewegungsamplitude. |
| Erwartete Auflösung | Interferometer: 10⁻⁹ – 10⁻¹² m je nach Aufbau. Triangulation/Konfokal: 10⁻⁶ – 10⁻⁸ m bei höherer Bandbreite. |
| Bandbreite | Bis in den kHz-Bereich, oberhalb der mechanischen Eigenfrequenzen relevant. |
| Hauptlimitierungen | Luftbrechungsindex-Schwankungen, Streulicht, Targetreflektivität, Wahl des Referenzkörpers (was ist „in Ruhe“?). |

### 2.3 · Referenz-/Untergrundkanal

| Eigenschaft | Beschreibung |
|---|---|
| Zweck | Erfassung des Umgebungsrauschens, der Drift und der Eigenvibration des Aufbaus ohne aktive Anregung des PCMMS. Liefert die Subtraktionsbasis für die anderen Kanäle. |
| Sensorklasse | Identische Kraft- und Wegsensoren wie 2.1/2.2, montiert an einem identisch konstruierten, aber inaktiven Referenz-Aufbau in unmittelbarer Nähe – oder zweite Messung am selben Aufbau bei abgeschalteter Anregung („off-state“). |
| Verwendung | Subtraktion oder gleitende Drift-Korrektur. Erkennt Tagesgang, Temperaturzyklus, Gebäudeschwingungen. |
| Hauptlimitierungen | Annahme, dass Referenz und Messung identische Umgebungseinflüsse sehen, ist nur näherungsweise gültig. Räumliche Korrelation muss verifiziert werden. |

### 2.4 · Optional: Inertialer Rahmenkanal

| Eigenschaft | Beschreibung |
|---|---|
| Zweck | Beschleunigungssensor am Rahmen des PCMMS – misst direkt z̈(t) als unabhängige Bestätigung der modellierten Dynamik. |
| Sensorklasse | MEMS-Beschleunigungssensor (µg-Klasse) oder seismische Beschleunigungsmesser für tiefe Frequenzen. |
| Verwendung | Konsistenzprüfung: aus z̈(t) und Modell folgt F_c-Vorhersage, die mit der direkten Kraftmessung verglichen wird. Diskrepanzen sind diagnostisch. |

## 3 · Mechanischer Aufbau: Einseitige Federlagerung

Das PCMMS wird auf einer einseitig wirkenden Federlagerung mit definierter Steifigkeit k und Dämpfung c platziert. Diese Lagerung bildet den nichtlinearen Kontakt aus der v3-Hypothese physisch nach:

- Bei Andruck: F_c = k·x + c·ẋ – Feder und Dämpfer wirken
- Bei Abheben: F_c = 0 – Kontakt unterbrochen, das System fliegt frei
- Liftoff-Übergänge sind das diagnostisch entscheidende Ereignis – sie definieren die Wellenformasymmetrie

Die Lagerung wird so gewählt, dass die Liftoff-Schwelle bei realistischen Anregungsamplituden tatsächlich erreicht wird. k und c werden vor der Messung statisch und dynamisch kalibriert. Eine Variation von k über mehrere Größenordnungen (weicher Schaum bis steifer Stahl) erlaubt Sweep über die Kontaktcharakteristik – das spiegelt den simulativen (k, c)-Sweep aus v3a.

## 4 · Synchronisation und Zeitbasis

Wellenformanalyse erfordert eine gemeinsame Zeitbasis aller Kanäle. Die Synchronisationsanforderung ist strenger als bei reiner Mittelwertmessung:

- Gemeinsamer Sampling-Trigger für alle Kanäle (Hardware-Trigger, kein Software-Polling)
- Phasenstarre Kopplung an die PCMMS-Anregungsfrequenz – ermöglicht Lock-in-Auswertung und kohärente Mittelung über tausende Zyklen
- Zeitstempel-Auflösung ≪ Wellenform-Strukturzeit – typisch mindestens 100× kleiner als die kürzeste relevante Phase im Egg-Zyklus
- Drift-Synchronisation der Sensorelektronik (Temperatur-stabilisierte Oszillatoren oder GPS-Disziplinierung)

Ohne synchronisierte Zeitbasis ist Kreuzkorrelation zwischen Kraft- und Wegkanal nicht möglich – damit verfällt der wichtigste Detektionsmechanismus der Architektur.

## 5 · Datenfluss und Verarbeitungskette

Die Verarbeitung verläuft kanalweise und dann kanalübergreifend:

| Stufe | Operation | Zweck |
|---|---|---|
| 1 | Rohdaten-Erfassung | Alle Kanäle synchron, hohe Bandbreite, kein Vorfiltern |
| 2 | Kalibrierung | Anwendung der statisch/dynamisch ermittelten Sensorkennlinien |
| 3 | Driftabzug | Subtraktion des Referenzkanals oder gleitenden Mittels |
| 4 | Modellresiduum | Vergleich Mess-F_c mit Modellvorhersage aus z(t) bzw. z̈(t); Residuum r(t) = F_meas − F_model |
| 5 | Wellenform-Statistik | Berechnung der Observablen aus §3.1 der v3b-Notiz (Schiefe, Liftoff-Anteil, Spitzenkraftverhältnis, Spektrum) pro Zyklus |
| 6 | Ensemble-Mittelung | Kohärente Mittelung über N Zyklen reduziert Rauschen mit √N |
| 7 | Anomaliedetektion | Vergleich Anregung an vs. Anregung aus; Test auf signifikante Differenz |

## 6 · Detektionsstrategien

### 6.1 · Differenzielle Messung

Anregung an / Anregung aus im Wechsel über lange Zeiträume. Die Differenz der Observablen zwischen beiden Zuständen ist robuster gegen langsame Drift als der Absolutwert. Typische Sequenz: 5 min an, 5 min aus, über mehrere Stunden.

### 6.2 · Lock-in auf Anregungsfrequenz

Das PCMMS wird mit präzise bekannter Frequenz angeregt. Phasenstarre Demodulation aller Kanäle bei dieser Frequenz und ihren Harmonischen extrahiert nur den Signalanteil, der zur Anregung kohärent ist. Untergrund bei anderen Frequenzen wird durch die Demodulation unterdrückt.

### 6.3 · Kreuzkorrelation Kraft × Weg

Ein echter Wellenform-Effekt zeigt eine spezifische Phasenbeziehung zwischen F_c(t) und z(t), die das lineare Modell nicht reproduziert. Die Kreuzkorrelation als Funktion der Phasenverschiebung ist der diagnostische Test: ein Effekt erzeugt eine charakteristische Signatur, ein Artefakt typischerweise nicht.

### 6.4 · Residualstatistik gegen Modell

Aus dem nichtlinearen Kontaktmodell und z(t) wird F_c-Vorhersage berechnet. Das Residuum r(t) = F_meas − F_model wird statistisch ausgewertet. Erwartung unter H₀: r(t) ist weißes Rauschen mit bekannter Verteilung. Abweichungen sind das eigentliche Signal.

## 7 · Was die Architektur für ε_phys bedeutet

Die physikalisch relevante Schwelle ε_phys ist keine feste Zahl, sondern eine Funktion der Architektur. Sie ergibt sich aus dem Rauschen jedes Kanals, der Mittelungstiefe und der Detektionsstrategie:

**ε_phys  ≈  σ_kanal / √N  ·  η_strategie**

- σ_kanal: Eigenrauschen des limitierenden Kanals
- N: Anzahl kohärent gemittelter Zyklen – wächst linear mit der Messzeit
- η_strategie: Effizienzfaktor der Auswertung (Lock-in, Kreuzkorrelation, Residualanalyse) – typisch 0.1 bis 1.0

Mit konservativen Annahmen (σ ≈ 10⁻⁴ N, N = 10⁶ Zyklen bei 1 Hz über zwei Wochen, η ≈ 0.3) ergibt sich rechnerisch ε_phys ≈ 3·10⁻⁸ N. Das ist drei bis vier Größenordnungen unterhalb dessen, was eine einzelne Präzisionswaage liefert.

Tiefere Detektionsklassen erfordern entweder bessere Sensoren (kryogene Lagerung, atomare Interferometrie) oder längere Mittelungszeiten – beides ist Frage institutioneller Ressourcen, nicht des konzeptuellen Aufbaus.

## 8 · Grenzen und was nicht beansprucht wird

- Die Architektur erzeugt keine Effekte. Sie macht sie sichtbar – falls vorhanden.
- Mehrkanalmessung ersetzt keine physikalische Hypothese. Ohne klare Vorhersage, was die Observable in welchem Kanal tun sollte, ist die Architektur ein Datensammler ohne Falsifikationskraft.
- Detektionsklassen unterhalb 10⁻²⁰ N sind mit klassischen mechanischen Methoden konzeptionell ausgeschlossen (thermisches Rauschen, Quantenlimit). Die in v3b §5 genannten 10⁻⁵⁰-Linien sind Ferndruckpunkte, keine Architekturparameter.
- Synchronisation, Kalibrierung und Datenfusion sind anspruchsvoll. Die Architektur ist konzeptuell einfach, aber praktisch experimentintensiv.

## 9 · Status und nächste Schritte

| # | Schritt | Status |
|---|---|---|
| 1 | Konzeptbaustein Mehrkanal-Messarchitektur (diese Notiz) | Vorliegend |
| 2 | Simulation v3a – ein Modul, Egg, nichtlinearer Kontakt – als Wellenform-Charakterisierung | Folgt |
| 3 | Definition von ε_phys auf Basis konkreter Sensor-/Messzeit-Annahmen | Folgt |
| 4 | Modell der Datenverarbeitungskette als simulativer Verarbeitungs-Stack (Stufe 1–7 aus §5) | Mittelfristig |
| 5 | Spezifikation eines minimalen Demonstrator-Aufbaus (Einzelmodul + zwei Kanäle) | Mittelfristig |
| 6 | Institutionell unterstützte Realisierung | Langfristig |

## Schlussbemerkung

Eine Hypothese ist nur so prüfbar wie die Architektur, mit der sie gemessen wird. v3b reformuliert die Frage – dieser Baustein beschreibt das Werkzeug, das die Frage beantworten könnte. Beide Notizen sind unabhängig vom Existenznachweis des Effekts wertvoll: sie definieren die methodische Infrastruktur einer ehrlichen Untersuchung.

Die hier skizzierte Struktur ist nicht neu – sie folgt etablierter Praxis in der Präzisionsmesstechnik. Ihr Wert liegt darin, dass sie auf das spezifische PCMMS-Setting zugeschnitten ist und an die übrigen Bausteine direkt anschließt.

*PCMMS · Konzeptbaustein · Mehrkanal-Messarchitektur · Matthias Früh · Mai 2026*

*ORCID: 0009-0005-9984-4207 · prä-experimentell · Grundlagenforschung*
