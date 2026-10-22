# Fluidisch gekoppelte Vertikaldrift eines auftriebskompensierten Körpers

**Ein falsifizierbares Proof-of-Concept aus dem PCMMS-Framework**

**Matthias Früh**  
ORCID: 0009-0005-9984-4207  
GitHub: [github.com/matthias-frueh/phase-controlled-multi-mass-systems](https://github.com/matthias-frueh/phase-controlled-multi-mass-systems)  
Zenodo: DOI 10.5281/zenodo.20080915  
**Stand: Mai 2026**

> **Vermerk (22.10.2026).** Originaldatei `PCMMS_Ballon_Demonstrator_2026.md`, Stand Mai 2026; hier unverändert bis auf
> diesen Vermerk. Konzept des Ballon-Demonstrators der Linie B ([`../einordnung.md`](../einordnung.md), Abschnitt
> „Linie B“). Linie B gehört im Arbeitsplan zur Stufe S5 (geparkt), ihr Arbeitspaket ist AP-28, Status „später“
> ([`../arbeitsplan_status.md`](../arbeitsplan_status.md)); ein eigenes Arbeitspaket für den Demonstrator gibt es
> nicht. Mit dem Demonstrator wurden keine Messdaten erzeugt. Seit Mai 2026 überholt oder offen:
> - **Befund 3 (Abschnitt 1):** „Nettodrift … skaliert mit Fluiddichte rho und ist im Vakuum exakt null“ ist nach den
>   Linie-B-Kontrollrechnungen eingeschränkt: „Kraft ∝ ρ; stationäre Drift nur im reinen Quadratmodell
>   dichteunabhängig; mit linearem Zusatzwiderstand unterhalb von ρ* ∝ ρ“
>   ([Gegenprüfung LB-06](../../rechnungen/linie_b/verifikation/PROTOKOLL.md);
>   [`../../rechnungen/linie_b/PROTOKOLL.md`](../../rechnungen/linie_b/PROTOKOLL.md) LB-06). „Wegen LB-02 ist bei
>   KC ≪ 1 aber auch F̄ ∝ ρ nicht belegt.“ (ebd., LB-06)
> - **Mechanismus (Abschnitte 3, 8):** Welches Kraftmodell bei der kleinen Keulegan-Carpenter-Zahl gilt, ist offen; ein
>   quasistationäres quadratisches Widerstandsgesetz ist dort nicht begründet (Einordnung, „Linie B“; LB-02; AP-28).
>   „Theorie, Elektronik und Auswertungstools fertig“ ist der Stand des Dokuments.
> - **Elektronik (Abschnitte 4, 5):** Die Firmware-Muster liegen in [`../../code/firmware/`](../../code/firmware/README.md);
>   keines erzeugt das Egg-Profil der Simulation, Phasengenauigkeiten sind nicht gemessen. Für die beschriebenen
>   Münzvibrationsmotoren gibt es nur den Tischtest-Sketch, der allein die Phase der PWM-Hüllkurve einstellt; die
>   Firmware-README ordnet dem Ballon-Demonstrator die BLDC- und LRA-Sketche zu.
> - **Anhänge:** Begleitbericht und Pendeltest-Protokoll liegen als
>   [`demonstrator_begleitbericht_2026-05.md`](demonstrator_begleitbericht_2026-05.md) und
>   [`demonstrator_pendeltest_horizontal_2026-05.md`](demonstrator_pendeltest_horizontal_2026-05.md) vor, die Tracking-
>   und Auswerteskripte, nicht getestet, in [`../../code/demonstrator/`](../../code/demonstrator/README.md).
> - **Zenodo-DOI (Kopf):** Frühere Zenodo-Stände (April–Mai 2026) dokumentieren den Weg, nicht den aktuellen Stand
>   ([`../../README.md`](../../README.md), „Zitieren“).
>
> Lizenz wie der Ordner: CC BY 4.0 ([`../../LICENSE-CC-BY-4.0`](../../LICENSE-CC-BY-4.0)).

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