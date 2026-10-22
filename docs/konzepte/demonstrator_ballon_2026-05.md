# Fluidisch gekoppelte Vertikaldrift eines auftriebskompensierten Körpers

**Ein falsifizierbares Proof-of-Concept aus dem PCMMS-Framework**

**Matthias Früh**  
ORCID: 0009-0005-9984-4207  
GitHub: [github.com/matthias-frueh/phase-controlled-multi-mass-systems](https://github.com/matthias-frueh/phase-controlled-multi-mass-systems)  
Zenodo: DOI 10.5281/zenodo.20080915  
**Stand: Mai 2026**

## Leitlinie
Der Demonstrator basiert ausschließlich auf dem mediumsabhängigen Rückstoß — dem einen PCMMS-Befund, der für einen frei beweglichen Körper gilt. Zielgröße ist die vertikale **Netto-Drift**. Ein Null-Ergebnis ist ein vollwertiges, dokumentiertes Resultat.

## 1. Ausgangslage
Das PCMMS-Framework liefert drei belastbare Befunde:

1. **Steady-State-Null**: Im periodischen Gleichgewicht gilt ⟨N⟩ = Mg (Impulserhaltung).
2. **Wellenform-Signatur**: Stark phasenabhängige Kontaktkraft N(t) mit drei Regimen (Bouncing, Auslöschung, Übergang) bei gelagerten Systemen.
3. **Mediumsabhängiger Rückstoß**: Nettodrift des Schwerpunkts durch interne Oszillation skaliert mit Fluiddichte rho und ist im Vakuum exakt null.

Für einen frei schwebenden Körper (Heliumballon) ist vor allem Befund 3 relevant. Phasengesteuerte interne Massenbewegung kann über asymmetrische fluidische Kopplung eine Netto-Drift erzeugen.

## 2. Hypothese (falsifizierbar)
Durch phasenstarre Ansteuerung von 2–3 internen Vibrationsmodulen erfährt ein nahezu neutral austarierter Heliumballon eine **messbare, reproduzierbare und phasenabhängige vertikale Netto-Drift**, die sich signifikant von umgebungsbedingter Drift unterscheidet.

**Kontrollexperiment**: Zufällige Phase oder Motoren aus → keine systematische Drift erwartet.

## 3. Mechanismus (ehrlich benannt)
Interne Kräfte erzeugen keine Nettokraft auf den Schwerpunkt. Die Drift entsteht durch **asymmetrische Wechselwirkung mit der Luft** (nichtlinearer Widerstand, mitbewegte Luftmasse, ggf. Hüllverformung) über einen Zyklus. Prinzip des Vibrationsschwimmers in dünnem Medium.  
**Kein reactionless drive, keine neue Physik.**

## 4. Aufbau (Minimalversion < 150 g)
- Heliumballon (ca. 60 cm Durchmesser), knapp austariert (leicht negativer Auftrieb).
- Leichte Trägerplattform (Balsa/3D-Druck-Gitter).
- 2–3 Vibrationsmodule (Münzvibrationsmotoren mit exzentrischen Massen).
- ESP32 + MOSFET-Steuerung (IRLZ44N), 1S-LiPo-Akku.
- Messung: Hochkant-Video mit Maßstab + OpenCV-Tracking.

## 5. Elektronik & Steuerung
Phasenstarre PWM-Steuerung mit einstellbarem/zyklischem Phasenversatz (0 Grad, 90 Grad, 180 Grad, 270 Grad). Vollständiger Code und Schaltplan im Technischen Begleitbericht.

## 6. Messung & Auswertung
**Phase 1 – Pendel-/Tischtest** (obligatorisch):  
Freie Plattform oder Pendel mit rotem Marker → Video → automatisches Tracking → Driftkurven pro Phase.

**Phase 2 – Ballontest**:  
30 s Intervalle pro Konfiguration. Quantitative Auswertung via Tracking.

**Erfolgskriterium**: Phasenabhängige Drift oberhalb von Umgebungs- und Streurauschen, reproduzierbar.

## 7. Abgrenzung
- Kein „reactionless drive“ — Impuls an das Fluid.
- Keine Gravitationsmodifikation, kein Perpetuum mobile.
- Wellenform-Regime nicht direkt übertragbar.
- Neue, ungeprüfte Hypothese.

## 8. Status & Nächste Schritte
- Theorie, Elektronik und Auswertungstools fertig.
- Nächster Schritt: Pendeltest mit automatischer Phasensteuerung + Tracking.
- Dokumentation: Vollständig offen auf GitHub und Zenodo (Rohdaten, Videos, Skripte).

**Anhänge**  
- Technischer Begleitbericht (Bauteilliste, Schaltplan, ESP32-Code)  
- Python OpenCV Tracking-Skript  
- Automatischer Phasenzyklus-Code  
- Detailliertes Testprotokoll

---

*Dieses Dokument ist bewusst ehrlich, falsifizierbar und reproduzierbar formuliert.*