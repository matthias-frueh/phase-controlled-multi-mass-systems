# PCMMS — Notiz: spätere Prüfarchitektur für Linie B

**Datum:** 01.09.2026 · **Status:** Entwurf, ausdrücklich **nicht** der nächste Schritt
**Gilt für:** H1_fluid (Linie B, in der Präregistrierung als optional geführt)

> **Vermerk (22.10.2026).** Originaldatei `PCMMS_Notiz_Pruefarchitektur_LinieB.md`, Stand 01.09.2026, Entwurf; hier
> unverändert bis auf diesen Vermerk. Linie B, Arbeitspaket AP-28 (Stufe S5, Status „später“,
> [`../arbeitsplan_status.md`](../arbeitsplan_status.md)). Nicht umgesetzt; keine Messdaten. Seit dem 01.09.2026
> überholt oder offen:
> - **Drift (§1):** „maximal 0,00069 m/s“ stammt aus der nicht eingeschwungenen v1-Karte
>   ([`sweep_13x13_drift_v1.csv`](../../rechnungen/linie_b/daten/sweep_13x13_drift_v1.csv); LB-07 in
>   [`PROTOKOLL.md`](../../rechnungen/linie_b/PROTOKOLL.md)); stationär sind es 0,00105 m/s, das Verhältnis im
>   Freifallargument wird 7.300 : 1, der Schluss bleibt
>   ([`skriptkorrekturen_2026-09-06.md`](skriptkorrekturen_2026-09-06.md) §5 Nr. 3).
> - **Auflösung (§2):** mit F̄_A neu zu bewerten; für die Skriptparameter in Luft ist ⟨x⟩ ≈ 23 nm bei L = 1 m,
>   „Sub-Millimeter“ liegt vier Größenordnungen darüber (Skriptkorrekturen §5 Nr. 2). Bei der kleinen KC-Zahl des
>   Trägers ist ein quasistationäres Widerstandsgesetz nicht begründet (für einen glatten Träger nicht gültig); der
>   Betrag der mittleren Kraft ist offen (LB-01, LB-02).
> - **Druckreihe (§3):** Die [Richtungsnotiz v5.2](richtungsnotiz_medienkopplung_2026-09-06_v5_2.md) (§5) schlägt vor,
>   „Δv(p)“ als ΔF̄_C(p) bzw. Δ⟨x⟩(p) zu führen. Die Dichteabhängigkeit ist modellabhängig: die Kraft bei festem C_D ∝ ρ,
>   die stationäre Drift nur im rein quadratischen Modell dichteunabhängig (LB-06).
> - **Störmechanismen (§4):** Mechanismus 2 (dynamische Instabilität) ist nach Richtungsnotiz §12 zu ergänzen.
> - **H1_fluid:** erhält nach dem Entwurf der [Präregistrierung v2](../praeregistrierung_v2_entwurf.md) (§0) eine
>   eigene Präregistrierung.
> - **Geometrische Phase (§6):** laut Dokument eine unbelegte Vermutung; die erwogene „dritte Linie“ ist im Repository
>   nicht weitergeführt.
>
> Lizenz wie der Ordner: CC BY 4.0 ([`../../LICENSE-CC-BY-4.0`](../../LICENSE-CC-BY-4.0)).

> **Vorrang:** V1 und Linie A. Diese Notiz beschreibt eine Prüfarchitektur, die erst sinnvoll wird,
> wenn Linie A reale Messdaten geliefert hat. Der elegantere Versuch ist nicht der richtige erste
> Versuch — die Kammer kostet rund das Zehnfache von V1 und prüft die Nebenlinie.

---

## 1 · Verworfen: freier Fall

Der Gedanke war, PCMMS im freien Fall zu messen, um das Kontaktmodell loszuwerden. Er scheitert an
einer Größenordnung.

**In Luft eliminiert der Fall die falsche Variable.** Nach 0,78 s Fall beträgt die
Relativgeschwindigkeit zum Medium 7,65 m/s. Die vorhergesagte Drift liegt bei maximal 0,00069 m/s
(`sweep_13x13_drift.csv`). Verhältnis 11.000 : 1, und da der Widerstand quadratisch geht, ist der
Staudruck aus der Fallbewegung rund **10⁸ mal größer** als der aus der Driftbewegung. Gemessen wird
dann Aerodynamik, nicht Medienkopplung.

**Im Vakuum sagt H1_fluid selbst Null voraus.** Ein Vakuumfallturm liefert die Kontrollmessung, nicht
die Effektmessung.

**Für Linie A entfällt mit dem Kontakt die Observable.** Ohne Kontaktkraft gibt es keine Schiefe von
N(t), keinen Liftoff-Anteil, kein F_min, kein Asymmetrieverhältnis. Was bliebe, wäre determiniert:
Schwerpunktbahn aus Impulserhaltung, Orientierung aus Drehimpulserhaltung, Rahmenbewegung aus beidem.

**Fazit:** Die Vakuumkammer wird gebraucht, der freie Fall nicht.

---

## 2 · Der Aufbau

Evakuierbare Kammer mit Torsionswaage. Identische Aufhängung, identische Geometrie, variiert wird
allein der Kammerdruck. Das System ruht relativ zum Medium — nur dann ist die Driftgeschwindigkeit
die einzige Relativgeschwindigkeit und der quadratische Widerstand arbeitet mit dem Signal statt
dagegen.

**Bedarf:** Kammer mit Drehdurchführung · Vorpumpe · Druckmessung über mindestens vier Dekaden ·
Durchführungen für Strom und Signale · Torsionswaage mit Auflösung im Sub-Millimeter-Bereich ·
Temperaturerfassung am Aufbau.

---

## 3 · Druckreihe statt 2×2

Eine Zweipunktmessung (Luft / Vakuum) sagt nur *Effekt da / Effekt weg*. H1_fluid macht aber eine
Aussage über die **Skalierung mit der Mediendichte**. Deshalb eine Reihe:

| Druck | PCMMS AUS | PCMMS EIN |
|---|---|---|
| 2000 mbar | Referenz | Messung |
| 1000 mbar | Referenz | Messung |
| 500 mbar | Referenz | Messung |
| 100 mbar | Referenz | Messung |
| 10 mbar | Referenz | Messung |
| 1 mbar | Referenz | Messung |
| 0,1 mbar | Referenz | Messung |

Ausgewertet wird **Δv(p) = v_ein(p) − v_aus(p)**. Die AUS-Messung läuft über die gesamte Reihe mit,
nicht als einzelner Kontrollpunkt — das macht die Auswertung robust gegen langsame Drift der
Torsionswaage und gegen thermische Trends.

### Drei Punkte, die das Design tragen

**Randomisierte Reihenfolge.** Eine monoton fallende Sequenz läuft parallel zur Erwärmung: Mit
sinkendem Druck fällt die Konvektion aus, der Aufbau wird wärmer. Jeder thermische Trend erzeugt
dann eine scheinbare Druckabhängigkeit. Randomisierte Reihenfolge mit wiederholten Stufen trennt
beides und kostet nichts außer Ventilstellungen. Entspricht dem Randomisierungsgrundsatz, der in der
Präregistrierung für die Phasenkonfigurationen bereits steht.

**Ankerpunkt im Überdruck.** Ohne Punkt oberhalb Umgebungsdruck liegen alle Messungen auf einer
fallenden Flanke. Bei 2000 mbar muss die Medienkopplung *stärker* werden — radiometrische und
akustische Effekte tun das nicht in gleicher Weise. Ein Überdruckpunkt ist diagnostisch vermutlich
wertvoller als drei zusätzliche im Feinvakuum. Setzt eine entsprechend ausgelegte Kammer voraus.

**Erwartungskurve aus dem Modell, nicht aus der Intuition.** Die vorhergesagte Form von v_drift(p)
muss aus `pcmms_medienkopplung_modell.py` abgeleitet und **vor** der Messkampagne festgeschrieben
werden. „Monoton mit der Dichte" ist eine Vermutung, keine Modellaussage.

---

## 4 · Druckabhängige Störmechanismen

Diese Kandidaten füllen genau die Zelle, die positiv sein soll. Sie sind vorab zu benennen und
messtechnisch zu trennen.

| Mechanismus | Signatur über p | Trennung durch |
|---|---|---|
| **H1_fluid** | gemäß Modellkurve, steigend mit Dichte | Überdruckpunkt, Richtungscharakteristik |
| **Radiometrisch** | nichtmonoton, Maximum im Zwischenvakuum, an beiden Enden gegen null | Temperaturerfassung, Form der Kurve |
| **Thermisch / konvektiv** | Sprung dort, wo die Konvektion aussetzt, danach flach | Temperaturerfassung, Aufwärmphasen |
| **Akustisch, Kammerwandreflexion** | verschwindet im Vakuum — **formal wie H1_fluid** | Frequenzvariation, Geometrieänderung, Wandabstand |

Der akustische Kandidat ist der unangenehmste: Impulsübertragung ans Medium, verschwindend im
Vakuum — das ist die Vorhersage von H1_fluid, erzeugt durch einen anderen Mechanismus. Unterschieden
werden kann er nur über Skalierung, Frequenzabhängigkeit und Richtungscharakteristik. Wer nur
Vorhandensein und Abwesenheit misst, kann ihn nicht ausschließen.

**Mitzuerfassen sind daher:** Kammerdruck, Temperatur am Aufbau, Richtung der Drift, Anregungsfrequenz.

---

## 5 · Formulierungen, die halten

Zwei Sätze, die in einer früheren Fassung zu weit gingen und in dieser Form verwendet werden sollten:

> **Nicht:** „Kein anderer Mechanismus würde dieses Muster erzeugen."
> **Sondern:** Ein reproduzierbarer Unterschied zwischen PCMMS EIN und AUS, der mit dem Kammerdruck
> verschwindet und mit der vorhergesagten Druckabhängigkeit skaliert, wäre ein spezifischer Test von
> H1_fluid und würde nicht durch die betrachteten druckunabhängigen Störmechanismen erklärt.

> **Nicht:** „Die Aktuatorik validiert sich über beide Linien hinweg."
> **Sondern:** Die Aktuatorik bildet die gemeinsame experimentelle Basis beider Linien und kann in
> Linie B unabhängig hinsichtlich ihrer kinematischen und zeitlichen Reproduzierbarkeit
> charakterisiert werden — Frequenz, Phasenlage, Amplitude, Wiederholbarkeit, Leistungsaufnahme,
> thermisches Verhalten. Die für Linie A relevante Kontaktkraftdynamik wird dadurch **nicht**
> mitvalidiert; dafür bleibt der Kontaktversuch notwendig.

---

## 6 · Nebenbefund: geometrische Phase

Beim Durchdenken der Freifallvariante aufgetaucht, gehört **nicht** zu Linie A oder B.

Bei verschwindendem Drehimpuls ist die Orientierung punktweise determiniert — aber nicht zyklisch.
Rotationen um verschiedene Achsen kommutieren nicht, deshalb kann nach einem geschlossenen Zyklus
der Innenkonfiguration eine **Netto-Orientierungsänderung** zurückbleiben, obwohl L = 0 durchgehend
gilt. Derselbe Mechanismus wie beim Katzendreh.

Für drei Module im Dreieck mit vertikal schwingenden Massen entstehen Kippmomente um zwei
nicht-parallele horizontale Achsen. Der Netto-Drehwinkel pro Zyklus hinge von der eingeschlossenen
Fläche im Konfigurationsraum ab — und die ist eine direkte Funktion der Phasendifferenzen: null bei
φ₂ = φ₃ = 0, maximal bei (120°, 240°).

**Status: unbelegte Vermutung.** Grobe Abschätzung über das Quadrat des Verhältnisses von Massenhub
zu Trägheitsradius (5 mm zu etwa 50 mm) ergibt rund 1 % pro Zyklus, also Milliradiant-Bereich. Die
1D-Engine kann das grundsätzlich nicht abbilden. Vor jeder Verwendung müsste die eingeschlossene
Fläche für die konkrete Modulgeometrie berechnet werden.

Falls es trägt, wäre es eine **dritte** Linie mit eigener Observable (Netto-Drehwinkel), eigenem
Aufbau und eigener Literatur — geometrische Phasen in Mehrkörpersystemen sind seit Shapere und
Wilczek ein eigenes, gut besetztes Feld. Nicht mit der Kontaktkraftlinie vermischen.

---

## 7 · Reihenfolge

```
V1  →  Linie A  →  reale Messdaten  →  institutionelle Anbindung
                                              ↓
                          erst wenn Ergebnisse und Mittel es rechtfertigen
                                              ↓
        Linie B  →  evakuierbare Kammer  →  randomisierte Druckreihe  →  H1_fluid
```

Linie B wird dadurch nicht kleingeredet. Das Experiment ist wissenschaftlich attraktiv — es ist für
den gegenwärtigen Projektstand nur nicht der optimale nächste Versuch.
