# Laborplan · Variante 1 — kostengünstig

*PCMMS · Phase-Controlled Multi-Mass Systems  —  Matthias Früh  ·  ORCID 0009-0005-9984-4207  ·  Mai 2026*

> **Vermerk zur Übernahme (04.10.2026).** Konzept des Autors vom Mai 2026, hier unverändert bis auf den Querverweis
> in Abschnitt 6. Nicht umgesetzt; keine Messdaten. Der Plan ist der Hardware- und Laborentwurf für die erste
> Apparatur (V1) in der kostengünstigen Variante. Die Arbeitspakete AP1–AP5 in Abschnitt 12 sind die des Plans, nicht
> die des Arbeitsplans der Gesamtprojektanalyse (AP-01 bis AP-30, [`../arbeitsplan_status.md`](../arbeitsplan_status.md)).
> Seit Mai 2026 überholt oder offen:
> - **Parameter:** Die Richtwerte (M ≈ 0,65 kg, Mg ≈ 6,4 N, weicher Kontakt) sind die des Simulations-Referenzsatzes.
>   Der Auslegungskandidat des Werkzeugs [`../../code/auslegung.py`](../../code/auslegung.py) rechnet mit steifem
>   Kontakt, drei Modulen à 100 g und 8 mm Hub; Arbeitspunkt, Geometrie und Zellen sind nicht festgelegt (AP-04). Die
>   Zellreserve folgt aus den Einzelzellkräften, nicht aus der Summe ([`../../rechnungen/kippmoment/`](../../rechnungen/kippmoment/)).
> - **Antrieb:** Kurbel, Nocke oder programmierbarer Aktor sind offen (AP-01, Entscheidung des Autors). Die
>   „vorhandene ESP32-Steuerung“ ist die Firmware der Demonstratoren und Tischtests ([`../../code/firmware/`](../../code/firmware/));
>   eine Firmware für drei Module mit Encoder und Zeitstempel liegt nicht vor.
> - **Messgrößen und Regeln:** Primär sind nach der Präregistrierung v2 F_min − ⟨N⟩ und die Harmonischen 1–3;
>   „Spitzen-zu-Mittel-Verhältnis“ und Asymmetrieverhältnis sind verschiedene Größen ([`../overview.md`](../overview.md)).
>   Die Erfolgs- und Falsifikationsregel in Abschnitt 10 ist durch die Entscheidungsregeln der Präregistrierung v2
>   (§8, §9) ersetzt; der „harte Stopp“ bei ⟨N⟩ ≠ Mg entspricht ihrer Kontrollgröße H0.
> - **Sicherheit:** Hüpfzustände mit Stoßspitzen von einigen 100 N sind im Modell des steifen Aufbaus möglich
>   ([`../einzugsgebiete_v1_kandidat.md`](../einzugsgebiete_v1_kandidat.md)); der Plan behandelt sie nicht. Ein
>   Sicherheitskonzept (AP-05) steht aus.
> - **Messkette:** Kanalzahl, Abtastrate (≥ 6,3 kHz für k_max = 9 nach Präregistrierung v2, A6) und Kalibrierplan
>   sind Gegenstand von AP-06; die Angaben zu ADC und Abtastrate (≥ 2 kSPS) sind der Stand des Plans.

## 1 · Zweck und Messprinzip

Ziel der Kampagne ist der experimentelle Nachweis, dass die *relative Phasenlage* mehrerer periodisch bewegter Module die Form der Kontaktkraft N(t) eines Mehrmassensystems auf einseitigem Kontakt deterministisch steuert — bei konstantem mittlerem Lastfall. Gemessen werden die Wellenform-Observablen Schiefe, Liftoff-Anteil und Spitzen-zu-Mittel-Verhältnis, kontrolliert wird die Bindung des Mittelwerts an das Gewicht (⟨N⟩ = Mg).

**Leitgedanke der Auslegung: **Das gesuchte Signal ist eine Order-1-Größe (Liftoff 0 → ≈75 %, Schiefe 0 → ≈+1,7), keine mN- oder µN-Jagd. Die Apparatur braucht deshalb nicht Präzision, sondern Bandbreite. Genau das macht eine kostengünstige Realisierung wissenschaftlich tragfähig.

## 2 · Messgröße, Variablen und feste Parameter

- **Zielobservablen: **Schiefe, Liftoff-Anteil und Spitzen-zu-Mittel-Verhältnis von N(t).

- **Kontrollgröße: **zeitlicher Mittelwert ⟨N⟩ (muss der statischen Last entsprechen).

- **Unabhängige Variable: **relative Phase (φ₂, φ₃) ∈ [0°, 360°)².

- **Konstant gehalten: **Masse, Antriebsfrequenz, Hub, Kontaktsteifigkeit, Geometrie.

*Richtwerte (an das Simulationsmodell angelehnt):*

| **Größe** | **Wert / Status** |
| --- | --- |
| Module | 3 (identisch), gemeinsames steifes Gehäuse |
| Gesamtmasse M | ≈ 0,65 kg  (Mg ≈ 6,4 N) |
| Antriebsfrequenz f | 10 Hz  (T = 0,1 s) |
| Innenbewegung | Hold-Schnell-Profil, näherungsweise per Kurbel/Nocke |
| Hub | einige mm (Modellbezug RTOP ≈ 5 mm) |
| Kontakt | weiches Elastomer/Feder, k und c bekannt |
| Steuergröße | φ₂, φ₃ (relative Phasen der Module) |

## 3 · Mechanischer Aufbau

Drei Module sitzen in einem möglichst steifen Gehäuse, das *frei* auf einem nachgiebigen, einseitigen Kontakt (Elastomerpad oder kalibrierte Feder mit bekanntem k, c) auf einer Kraftmessdose ruht; die Dose steht auf einer schweren, schwingungsisolierten Basis. Der einseitige Kontakt entsteht von selbst: Das System ist nur unter Schwerkraft aufgesetzt, nicht verschraubt, und hebt ab, sobald die Aufwärtsbeschleunigung g übersteigt (N → 0). Die weiche Lagerung ist physikalisch notwendig, um bei 10 Hz überhaupt in den Liftoff-Bereich zu kommen, und hält zugleich die Spitzenkräfte im Messbereich der Dose.

## 4 · Aktuatorik (10 Hz)

Drei kleine getriebene DC-Motoren mit Exzenter bzw. Kurbel/Nocke bewegen je eine Modulmasse (~50–150 g) mit einigen mm Hub. 600 U/min ergeben 10 Hz; eine Kurbel approximiert die sinusförmige, eine Nocke die asymmetrische (Egg-)Bewegung. Die relative Phasenlage φ₂, φ₃ wird über die vorhandene ESP32-Steuerung per Timing bzw. Encoder gesetzt. Damit trifft die Apparatur direkt den 10-Hz-Bereich der Simulation und nutzt die bestehende Phasen-Firmware.

**Design-Bedingung: **Frequenz, Masse und Kontaktsteifigkeit so abstimmen, dass in einem Teil der Phasenlagen tatsächlich Liftoff auftritt — wo dieser Bereich liegt, gibt die Simulation vorab an.

**Am Rande — LRA-Option: **Vorhandene LRAs laufen physikalisch nicht bei 10 Hz, sondern resonieren bei ~150–235 Hz mit µm-Hub. Nutzbar nur, wenn man bei LRA-Resonanz fährt und die Kontaktsteifigkeit k (und die Masse) so skaliert, dass die dimensionslosen Verhältnisse, die Liftoff und Schiefe bestimmen, dem 10-Hz-Modell entsprechen. Bei ~175 Hz ist ω² so groß, dass Liftoff (a > g) schon bei wenigen µm entsteht — das funktioniert, ist aber eine Mikro-Version bei verschobener Frequenz. Für ‚voll und sicher‘ bleibt es bei 10 Hz (Motor + Kurbel); LRA-Resonanz nur als Notnagel.

## 5 · Kraftmessung: schnelle Messdose + DAQ

Eine DMS-Wägezelle (Biegebalken, ~3–5 kg Bereich — Headroom über Mg ≈ 6,4 N) wird über einen schnellen 24-bit-ADC mit programmierbarem Vorverstärker (PGA) ausgelesen. Die Abtastrate liegt bei ≥ 2 kSPS (rund 200× die Grundfrequenz), damit die scharfen Liftoff-Flanken und Kraftspitzen zeitlich aufgelöst werden. Der DC-fähige Pfad liefert gleichzeitig die statische Kontrolle ⟨N⟩ = Mg.

**Wichtig: **Ein HX711 (80 SPS) ist zu langsam für Liftoff und Spitzen und scheidet aus. Als Host genügt ein Raspberry Pi (SPI) oder — am günstigsten — der ESP32 als SPI-Master, der die Rohdaten an einen Laptop streamt.

**Am Rande — konkrete Teile (Beispiel, ~€50): **Wägezelle 5 kg (~€8), ADS1256-Breakout (24-bit, bis 30 kSPS, PGA bis 64×, ~€20), Pi oder vorhandener ESP32 als Logger; Beschleunigungssensor MPU-6050 oder ADXL345 (~€3) am Rahmen zur Liftoff-Gegenprobe.

## 6 · Sekundär- und Referenzsensorik

- **Beschleunigungssensor am Rahmen: **Liftoff über die Freifall-Beschleunigung (≈ 0 g) gegenprüfen und die Innenbewegung verifizieren.

- **Referenz-/Sync-Kanal: **das Phasen-/Antriebssignal des ESP32 mitschneiden → ermöglicht Phasenmittelung, Lock-in und Kreuzkorrelation (die Mehrkanal-Messarchitektur, [`mehrkanal_messarchitektur_2026-05.md`](mehrkanal_messarchitektur_2026-05.md), hier am richtigen Ort).

## 7 · Kontakt und Schwingungsisolation

Weiches Elastomerpad oder Feder mit bekanntem k, c als einseitiger Kontakt. Das gesamte System wird frei aufgesetzt (nicht verschraubt), damit Liftoff physikalisch entstehen kann. Als Basis dient eine schwere Platte (Granit- oder Gehwegplattenrest) auf Squash-Bällen oder Sorbothane-Füßen, um Boden- und Tischschwingungen zu entkoppeln.

## 8 · Kontrollen (das wissenschaftliche Rückgrat)

- **Statische Kalibrierung **mit Referenzmassen → Kraftskala und Ruhebasis ⟨N⟩ = Mg.

- **Referenzlauf **(φ = 0 bzw. Einzelmodul) → Bezugswellenform.

- **Dummy-/Null-Lauf: **Aktuatoren an, Amplitude null (oder inerte Ersatzmasse) → schließt elektromagnetische Einkopplung des Antriebs und Rig-Resonanz als Scheinsignal aus.

- **Rig-FRF: **Strukturresonanzen einmal vermessen und die Antriebsfrequenz davon fernhalten.

- **Wiederholbarkeit: **drei Regime-Zentren und der Übergang je 3–5× → empirischer Rauschboden (Power-Analyse-Logik auf die reale Streuung angewandt).

- **Confounds prüfen: **Temperaturdrift, Sitz-/Montagewiederholbarkeit, 50-Hz-Netzbrumm, Kabelmikrofonie, Isolationsgüte.

## 9 · Messablauf pro Phasenpunkt

- Phasenlage (φ₂, φ₃) einstellen, Einschwingen abwarten.

- ≥ 100 Zyklen von N(t) (und Beschleunigung, Sync) aufzeichnen.

- Observablen berechnen: Schiefe, Liftoff-Anteil, Spitzen-zu-Mittel, sowie ⟨N⟩ als Kontrolle.

- Grob-Sweep (7×7) zur Lokalisierung der Regime, danach feines Raster an den Regime-Grenzen.

- Raster auf das 19×19-Simulationsgitter abbilden → direkter Vergleich Messung ↔ Modell.

## 10 · Erfolgs- und Abbruchkriterium

**Erfolg.  **Die drei Regime erscheinen an den vorhergesagten Phasenlagen oberhalb des Rauschbodens; die Struktur (nicht die exakten Zahlenwerte) reproduziert die Simulation.

**Falsifikation (für den getesteten Bereich).  **Die Regime-Struktur ist nach allen Kontrollen nicht über dem Rauschboden nachweisbar.

**Harter Stopp (Schutz gegen die alte Falle).  **Weicht ⟨N⟩ dauerhaft von der statischen Last ab, jenseits der Kalibrierunsicherheit, ist das eine defekte Messkette — keine Entdeckung. Dann wird die Apparatur geprüft und repariert, nicht interpretiert.

## 11 · Leistungsgrenzen von Variante 1

**Kann:  **die drei Regime und die gesamte φ → Wellenform-Karte sichtbar machen, Modell und Messung vergleichen, ⟨N⟩ = Mg kontrollieren.

**Kann nicht:  **ein sauberes Egg-Profil (die Kurbel ist nur näherungsweise) und eine feine Quantifizierung der Spitzenkraft (Pad-Nichtlinearität, ADC-Rauschen). Für den Nachweis der Struktur reicht es — und die Struktur ist die Aussage.

## 12 · Arbeitspakete

| **AP** | **Inhalt** | **Ergebnis** |
| --- | --- | --- |
| AP1 | Aufbau, Gehäuse, weicher Kontakt, statische Kalibrierung | kalibrierte Kraftskala, ⟨N⟩-Ruhebasis |
| AP2 | Aktuatorik (Motor + Kurbel), ESP32-Phasensteuerung | einstellbare (φ₂, φ₃) bei 10 Hz |
| AP3 | Kontroll- und Dummy-Messungen, Rig-FRF, Rauschboden | Artefaktausschluss, Nachweisschwelle |
| AP4 | Sweep-Kampagne (grob → fein), Datennahme | φ → Wellenform-Karte, Sim-Vergleich |
| AP5 | Auswertung, Artefaktanalyse, Dokumentation | Bericht, Rohdaten, Reproduzierbarkeit |

## 13 · Kostenrahmen

Grob €150–400, je nachdem, wie viel bereits vorhanden ist (ESP32, Laptop, ggf. LRAs). Wesentliche Posten: Wägezelle und schneller ADC, drei Kleinmotoren mit Exzenter, Elastomer/Feder, Isolationsbasis, Kleinmaterial.

## Anhang · Beispiel-Stückliste (Orientierung)

| **Komponente** | **Beispielteil** | **Richtpreis** | **Funktion** |
| --- | --- | --- | --- |
| Kraftsensor | DMS-Wägezelle 5 kg | ~€8 | N(t), statisch + dynamisch |
| ADC/DAQ | ADS1256-Breakout, 24-bit | ~€20 | schnelle Abtastung ≥ 2 kSPS |
| Beschl.-Sensor | MPU-6050 / ADXL345 | ~€3 | Liftoff-Gegenprobe |
| Aktuator ×3 | DC-Getriebemotor + Exzenter | ~€10–30 | Innenbewegung 10 Hz |
| Steuerung | ESP32 (vorhanden) | — | Phasenlage φ₂, φ₃ + Sync |
| Kontakt | Elastomerpad / Feder | ~€5 | einseitiger Kontakt, k, c |
| Isolation | Granitplatte + Sorbothane | ~€20 | Schwingungsentkopplung |

*Teileangaben sind Orientierung, keine Festlegung — entscheidend sind die Eigenschaften: schneller DC-fähiger Kraftkanal (≥ 2 kSPS), 10-Hz-Antrieb mit einstellbarer Phase, weicher einseitiger Kontakt.*