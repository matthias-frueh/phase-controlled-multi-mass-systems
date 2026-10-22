# Laborplan · Variante 2 — mittelteuer

*PCMMS · Phase-Controlled Multi-Mass Systems  —  Matthias Früh  ·  ORCID 0009-0005-9984-4207  ·  Mai 2026*

## 1 · Zweck und Messprinzip

Variante 2 verfolgt dasselbe Ziel wie Variante 1 — der Nachweis, dass die relative Phasenlage die Form der Kontaktkraft N(t) eines Mehrmassensystems auf einseitigem Kontakt steuert —, hebt es aber von der *qualitativen* auf die *quantitative* Ebene. Statt nur die drei Regime sichtbar zu machen, wird die Karte φ → (Schiefe, Liftoff, Spitzenverhältnis) zahlenmäßig mit dem Simulationsmodell verglichen.

Die beiden entscheidenden Aufwertungen: (a) das echte, frei programmierbare Hold-Schnell-(Egg-)Profil wird per Voice-Coil-Aktuator aufgeprägt *und durch Positionsrückführung verifiziert*; (b) Kraft, Modulbewegung und Antriebsreferenz werden auf einem gemeinsamen Takt simultan abgetastet, sodass Phasenbeziehungen exakt und die Observablen quantitativ belastbar sind. Zusätzlich wird die Kontaktsteifigkeit k zu einer gezielt variierbaren zweiten Achse.

## 2 · Messgröße, Variablen und feste Parameter

- **Zielobservablen: **Schiefe, Liftoff-Anteil, Spitzen-zu-Mittel-Verhältnis von N(t) — quantitativ.

- **Kontrollgröße: **zeitlicher Mittelwert ⟨N⟩ (DC-Pfad, muss der statischen Last entsprechen).

- **Unabhängige Variablen: **relative Phase (φ₂, φ₃); optional die Kontaktsteifigkeit k als zweite Achse.

- **Verifiziert statt angenommen: **die tatsächlich aufgeprägte Innenbewegung (Soll-Ist-Vergleich des Egg-Profils).

*Richtwerte:*

| **Größe** | **Wert / Status** |
| --- | --- |
| Module | 3 (identisch), Voice-Coil mit Positionsrückführung |
| Gesamtmasse M | ≈ 0,65 kg  (Mg ≈ 6,4 N) |
| Antriebsfrequenz f | 10 Hz  (T = 0,1 s) |
| Innenbewegung | echtes Hold-Schnell-(Egg-)Profil, frei programmierbar + verifiziert |
| Hub | einige mm, definiert (Modellbezug RTOP ≈ 5 mm) |
| Kontakt | definierte, austauschbare Steifigkeit k; c charakterisiert |
| Steuergrößen | φ₂, φ₃  (+ optional k als zweite Achse) |

## 3 · Mechanischer Aufbau

Drei Module in einem steifen Gehäuse, das frei auf definierten Kontaktelementen auf einer kalibrierten Kraftmessdose ruht; die Dose steht auf einem passiven Schwingungsisolationstisch. Wie in Variante 1 entsteht der einseitige Kontakt durch freies Aufsetzen (kein Verschrauben, N → 0 bei Abheben). Neu ist die definierte Kontaktsteifigkeit: austauschbare, charakterisierte Federn oder Elastomere erlauben es, k gezielt auf den Modellwert zu setzen und systematisch zu variieren.

## 4 · Aktuatorik (10 Hz) — Voice-Coil, echtes Egg-Profil

Drei Voice-Coil-Linearaktuatoren (Moving-Coil) bewegen je eine Modulmasse mit einigen mm Hub und werden über eine programmierbare Sollkurve angesteuert. Damit lässt sich das asymmetrische Hold-Schnell-Profil *exakt* aufprägen — nicht nur per Kurbel approximieren — und die relative Phase φ₂, φ₃ in Software mit hoher Treue setzen. Eine Lageregelung mit Positionsrückführung (Encoder oder LVDT) je Modul hält und verifiziert die Trajektorie. Bei 10 Hz und einigen mm Hub liegt die Aufwärtsbeschleunigung sicher über g, sodass in einem Teil der Phasenlagen Liftoff auftritt.

**Am Rande — obere Kante der Mittelklasse: **Wer die Anregung als prescribed acceleration im laborüblichen Sinn will, kann statt Voice-Coils kleine elektrodynamische Mini-Shaker mit Leistungsverstärker einsetzen. Saubere, lehrbuchnahe Krafteinleitung, aber spürbar teurer — sinnvoll erst, wenn das Budget Richtung Variante 3 wandert.

## 5 · Kraftmessung: kalibrierte Messdose + dediziertes Mess-DAQ

Eine kalibrierte DMS-Kraftmessdose (rückführbare Kalibrierung über Referenzmassen oder Herstellerzertifikat) wird über ein simultan abtastendes Mehrkanal-Mess-DAQ ausgelesen (24-bit, ≥ 10 kSPS pro Kanal). „Simultan‘ ist hier der Kern: Kraft, Modulposition und Antriebsreferenz liegen auf einem gemeinsamen Takt, wodurch die Phasenbeziehungen exakt sind und Phasenmittelung, Lock-in und Kreuzkorrelation sauber funktionieren. Der DMS-Pfad ist DC-fähig und liefert damit zugleich die Kontrolle ⟨N⟩ = Mg.

**Am Rande — Piezo-Option und die DC-Falle: **Für höchste dynamische Treue ließe sich ein Piezo-Kraftsensor mit Ladungsverstärker nutzen. Piezo ist jedoch AC-gekoppelt und kann den echten Mittelwert nicht liefern — die ⟨N⟩-=-Mg-Kontrolle bräuchte dann einen separaten DC-Kanal (Präzisionswaage oder parallele DMS-Zelle). Die rückführbare DMS-Dose bleibt der saubere Mittelklasse-Weg.

**Am Rande — konkrete Teile (Beispiel): **kalibrierte Wägezelle/Kraftsensor mit Zertifikat (~€200–800), simultanes Mehrkanal-DAQ (z. B. MCC/NI-Klasse, 24-bit, ~€500–2000), IEPE-Beschleunigungssensor (~€100–300), Encoder/LVDT je Modul (~€150–600).

## 6 · Sekundär- und Referenzsensorik

- **Positionsrückführung je Modul: **Encoder oder LVDT → Soll-Ist-Vergleich des aufgeprägten Egg-Profils (Profilverifikation).

- **Beschleunigungssensor am Rahmen: **IEPE-Sensor, Liftoff über Freifall-Beschleunigung gegenprüfen.

- **Gemeinsame Synchronisation: **alle Kanäle auf einem DAQ-Takt → exakte Phase, Voraussetzung für quantitative Observablen.

## 7 · Kontakt und Schwingungsisolation

Definierte, austauschbare Kontaktelemente (kalibrierte Federn oder charakterisiertes Elastomer) mit gemessenem k und c — so wird der Kontakt zum kontrollierten Parameter statt zur Unbekannten. Als Basis dient ein passiver Schwingungsisolationstisch (pneumatische Isolatoren oder Tischplattform), der den Rauschboden gegenüber der Squash-Ball-Lösung der Billig-Variante deutlich senkt.

## 8 · Kontrollen (das wissenschaftliche Rückgrat)

- **Rückführbare Kraftkalibrierung **mit Referenzmassen → quantitative Kraftskala und Ruhebasis ⟨N⟩ = Mg.

- **Profilverifikation: **aufgeprägte Trajektorie messen und gegen das kommandierte Egg-Profil abgleichen (neu in V2, da das Profil programmierbar ist).

- **Referenzlauf **(φ = 0 bzw. Einzelmodul) → Bezugswellenform.

- **Dummy-/Null-Lauf: **Antrieb an, Amplitude null → schließt elektromagnetische Einkopplung und Rig-Resonanz aus.

- **Rig-FRF: **Strukturresonanzen vermessen, Antriebsfrequenz fernhalten.

- **Wiederholbarkeit: **Regime-Zentren und Übergang mehrfach → quantitativer Rauschboden je Observable.

- **Confounds: **Temperaturdrift, Montagewiederholbarkeit, Netzbrumm, Kabelmikrofonie, Isolationsgüte.

## 9 · Messablauf pro Phasenpunkt

- Phasenlage (φ₂, φ₃) und Kontaktsteifigkeit k einstellen, Einschwingen abwarten.

- Profilverifikation: Ist-Trajektorie der Module gegen Soll-Egg prüfen.

- ≥ 100 Zyklen simultan aufzeichnen: N(t), Modulpositionen, Antriebsreferenz, Beschleunigung.

- Observablen quantitativ berechnen (Schiefe, Liftoff, Spitzen-zu-Mittel) + ⟨N⟩-Kontrolle.

- Feines Raster über (φ₂, φ₃), optional zusätzliche k-Werte; Abbildung auf das 19×19-Modellgitter → quantitativer Abgleich.

## 10 · Erfolgs- und Abbruchkriterium

**Erfolg.  **Die gemessene Karte φ → Wellenform stimmt quantitativ (innerhalb der kombinierten Unsicherheit) mit dem Modell überein; die Lage der drei Regime und ihre Übergänge werden zahlenmäßig reproduziert, einschließlich der k-Abhängigkeit.

**Falsifikation (für den getesteten Bereich).  **Die vorhergesagte Regime-Struktur ist nach allen Kontrollen nicht oberhalb des Rauschbodens nachweisbar, oder die quantitative Abweichung übersteigt systematisch die Unsicherheit ohne benennbare Ursache.

**Harter Stopp (Schutz gegen die alte Falle).  **Weicht ⟨N⟩ dauerhaft von der statischen Last ab, jenseits der Kalibrierunsicherheit, ist das eine defekte Messkette — keine Entdeckung. Apparatur prüfen und reparieren, nicht interpretieren.

## 11 · Leistungsgrenzen von Variante 2

**Kann:  **das echte Egg-Profil verifiziert aufprägen; die Wellenform quantitativ vermessen; k gezielt variieren; saubere Phasenmittelung; zahlenmäßiger Modellabgleich statt nur Strukturnachweis.

**Kann nicht:  **Vakuum- oder Medienkontrolle, µN-Metrologie, Klima-/Temperaturkammer, eichfähige Rückführung auf nationale Normale — das bleibt Variante 3.

## 12 · Arbeitspakete

| **AP** | **Inhalt** | **Ergebnis** |
| --- | --- | --- |
| AP1 | Aufbau, Isolationstisch, Kontaktcharakterisierung (k, c), rückführbare Kraftkalibrierung | kalibrierte Skala, ⟨N⟩-Basis, bekanntes k |
| AP2 | Voice-Coil-Aktuatorik, Lageregelung, Profilverifikation (Soll-Ist Egg) | verifiziertes Egg-Profil, exakte φ |
| AP3 | Mess-DAQ + Synchronisation, Kontroll-/Dummy-Messungen, Rauschboden | synchrone Kanäle, Nachweisschwelle |
| AP4 | Sweep-Kampagne (fein, φ und k), Datennahme | quantitative φ → Wellenform-Karte |
| AP5 | Quantitative Auswertung, Modellabgleich, Artefaktanalyse, Doku | Bericht, Rohdaten, Reproduzierbarkeit |

## 13 · Kostenrahmen

Grob €3.000–8.000, je nach Aktuator- und DAQ-Wahl. Wesentliche Posten: drei Voice-Coil-Aktuatoren mit Treibern und Positionsrückführung, kalibrierte Kraftmessdose, simultanes Mehrkanal-Mess-DAQ, passiver Isolationstisch, charakterisierte Kontaktelemente.

## Anhang · Beispiel-Stückliste (Orientierung)

| **Komponente** | **Beispielteil** | **Richtpreis** | **Funktion** |
| --- | --- | --- | --- |
| Aktuator ×3 | Voice-Coil-Linearaktuator + Treiber | ~€300–1500 | echtes Egg-Profil, exakte Phase |
| Positionsrückf. ×3 | optischer Encoder / LVDT | ~€150–600 | Profilverifikation, Lageregelung |
| Kraftsensor | kalibrierte DMS-Dose (Zertifikat) | ~€200–800 | N(t) DC+dynamisch, rückführbar |
| Mess-DAQ | simultanes Mehrkanal, 24-bit | ~€500–2000 | alle Kanäle synchron, exakte φ |
| Beschl.-Sensor | IEPE-Beschleunigungssensor | ~€100–300 | Liftoff-Gegenprobe |
| Kontakt | kalibrierte Federn / Elastomer-Set | ~€100 | definierte, variierbare k |
| Isolation | passiver Isolationstisch | ~€300–1500 | niedriger Rauschboden |

*Teileangaben sind Orientierung. Entscheidend sind die Eigenschaften: verifiziert aufgeprägtes Egg-Profil, simultan abgetasteter DC-fähiger Kraftkanal, definierte Kontaktsteifigkeit, niedriger Rauschboden.*