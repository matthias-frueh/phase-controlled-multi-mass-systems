# Laborplan · Variante 3 — teuer (Metrologie-Klasse)

*PCMMS · Phase-Controlled Multi-Mass Systems  —  Matthias Früh  ·  ORCID 0009-0005-9984-4207  ·  Mai 2026*

> **Vermerk (22.10.2026).** Originaldatei `PCMMS_Laborplan_Variante3_teuer_Frueh_2026.md`, Stand Mai 2026; hier
> unverändert bis auf diesen Vermerk. **Nebeninformation; keine Entscheidung, keine Beschaffung.** Variante 3 des
> Laborplans neben [Variante 1](laborplan_v1_2026-05.md) und [Variante 2](laborplan_v2_2026-05.md); nicht umgesetzt,
> keine Messdaten. Bezug: AP-01, AP-04, AP-05 und AP-06, alle „noch nicht umgesetzt“; Experiment B gehört zu Linie B
> (Stufe S5, AP-28, Status „später“; [`../arbeitsplan_status.md`](../arbeitsplan_status.md)). Die Arbeitspakete AP1–AP5
> in Abschnitt 13 sind die des Plans, nicht die des Arbeitsplans. Seit Mai 2026 überholt oder eingeschränkt:
> - **Experiment A:** Es gelten die Punkte des Vermerks zu [Variante 2](laborplan_v2_2026-05.md): Richtwerte des
>   Simulations-Referenzsatzes, Auslegungskandidat abweichend (AP-04), Antrieb offen (AP-01), Zielgrößen und Regeln
>   durch die Präregistrierung v2 abgelöst, Messkette AP-06, Sicherheitskonzept AP-05.
> - **Experiment B, Dichtegesetz (Abschnitte 1, 7, 10, 11):** Die Vorhersage „Drift ∝ ρ“ ist nach den
>   Linie-B-Kontrollrechnungen eingeschränkt: Die Kraft ist ∝ ρ nur bei festem C_D und fester Bewegung, bei KC ≪ 1 ist
>   auch das nicht belegt; die stationäre freie Drift ist im rein quadratischen Modell dichteunabhängig, mit linearem
>   Zusatzwiderstand unterhalb von ρ* ∝ ρ (LB-06 in
>   [`../../rechnungen/linie_b/PROTOKOLL.md`](../../rechnungen/linie_b/PROTOKOLL.md);
>   [Gegenprüfung](../../rechnungen/linie_b/verifikation/PROTOKOLL.md);
>   [Richtungsnotiz v5.2](../linie_b/richtungsnotiz_medienkopplung_2026-09-06_v5_2.md), §4.2). Für einen glatten Träger
>   ist das quasistationäre Widerstandsgesetz bei KC ≪ 1 nicht gültig; scharfe Kanten sind offen (LB-01, LB-02;
>   Richtungsnotiz v5.2, §6). Dass der Effekt im
>   Vakuum ohne Reaktionspartner verschwindet, bleibt Teil der Hypothese ([`../einordnung.md`](../einordnung.md),
>   „Linie B“).
> - **Experiment B, Kammer (Abschnitte 7, 9):** Die [Prüfarchitektur](../linie_b/pruefarchitektur_2026-09-01.md) führt die
>   evakuierbare Kammer als späteren Versuch; Vorrang haben V1 und Linie A (Kopf und Abschnitt 7 dort). Sie nennt
>   Störmechanismen mit derselben Signatur am Vakuumende: radiometrisch (an beiden Enden gegen null) sowie akustisch
>   und Kammerwandreflexion (verschwindet im Vakuum, „formal wie H1_fluid“); „Wer nur Vorhandensein und Abwesenheit
>   misst, kann ihn nicht ausschließen“ (Abschnitt 4 dort). H1_fluid erhält nach dem Entwurf der
>   [Präregistrierung v2](../praeregistrierung_v2_entwurf.md) (§0) eine eigene Präregistrierung.
> - **Kosten:** Kostenrahmen (Abschnitt 14) und Stückliste sind Schätzungen vom Mai 2026.
>
> Lizenz wie der Ordner: CC BY 4.0 ([`../../LICENSE-CC-BY-4.0`](../../LICENSE-CC-BY-4.0)).

## 1 · Zweck und Messprinzip

Variante 3 ist die Metrologie-Klasse. Sie bringt die Wellenform-Messung auf rückführbare, quantitative Genauigkeit mit ausgewiesenem Unsicherheitsbudget und erschließt zugleich ein zweites, eigenständiges Experiment. Damit deckt V3 zwei Fragestellungen ab:

- **Experiment A (Hauptkern): **rückführbar-quantitative Karte φ → (Schiefe, Liftoff, Spitzenverhältnis) der Kontaktkraft N(t), mit Unsicherheitsbudget und k-Abhängigkeit.

- **Experiment B (Strang b, Medienkopplung): **das Drift-Gesetz eines oszillierenden Moduls gegen die Mediumdichte ρ — die falsifizierbare Vorhersage Drift ∝ ρ, im Vakuum exakt null.

**Schutzzaun — wofür die Vakuumfähigkeit da ist (und wofür nicht): **Die Kammer dient ausschließlich dem ρ-Strang. Sie liefert den Nullpunkt ρ → 0, an dem der medienbedingte Drift verschwinden MUSS. Sie ist kein Test auf einen geschlossenen Eigenantrieb: Dessen Netto-Schwerpunktswirkung ist nach dem Schwerpunktsatz null — unabhängig von der Apparatur. Verschwindet der Drift im Vakuum nicht, ist das ein Artefakt (mechanische Restkopplung, Neigung), kein Effekt.

## 2 · Messgrößen, Variablen und feste Parameter

- **Experiment A — Zielobservablen: **Schiefe, Liftoff-Anteil, Spitzen-zu-Mittel-Verhältnis von N(t), rückführbar quantifiziert.

- **Experiment B — Zielgröße: **Netto-Drift bzw. Selbstvortrieb des Moduls als Funktion von ρ (horizontal, nicht vertikal).

- **Kontrollgrößen: **⟨N⟩ = Mg (A, DC-Pfad); Drift(ρ → 0) = 0 (B, Vakuum-Nullkontrolle).

- **Unabhängige Variablen: **φ₂, φ₃ und k (A); Mediumdichte ρ (B).

*Richtwerte:*

| **Größe** | **Wert / Status** |
| --- | --- |
| Module | 3 (identisch), hochwertige Voice-Coil / Mini-Shaker, geschlossene Beschleunigungsregelung |
| Gesamtmasse M | ≈ 0,65 kg  (Mg ≈ 6,4 N) |
| Antriebsfrequenz f | 10 Hz  (T = 0,1 s) |
| Innenbewegung | prescribed acceleration (geregelt), berührungslos verifiziert (LDV) |
| Kontakt | definierte, variierbare k; c charakterisiert |
| Umgebung | ρ variabel (Vakuum → Gas), temperaturstabilisiert |
| Steuergrößen | φ₂, φ₃, k  (A);  ρ  (B) |

## 3 · Mechanischer Aufbau

Drei Module in einem steifen Gehäuse auf definierten Kontaktelementen auf einer rückführbar kalibrierten Kraftmessdose, das Ganze auf einem aktiven Schwingungsisolationstisch. Für Experiment B sitzt der Aufbau (bzw. ein dafür ausgelegtes Einzelmodul) in einer Vakuum-/Medienkammer mit einstellbarem Gasdruck. Einseitiger Kontakt wie zuvor durch freies Aufsetzen; für die Drift-Messung wird die Modulbewegung horizontal orientiert und reibungsarm geführt.

## 4 · Aktuatorik (10 Hz) — geregelte prescribed acceleration

Drei hochwertige Voice-Coil-Aktuatoren oder kleine elektrodynamische Mini-Shaker prägen die Innenbewegung über eine geschlossene Beschleunigungsregelung auf — die laborübliche prescribed acceleration. Ein Echtzeit-Controller fährt das Hold-Schnell-(Egg-)Profil und die relativen Phasen φ₂, φ₃ mit hoher Treue; die tatsächlich erreichte Trajektorie wird berührungslos per Laser-Vibrometer rückgemessen.

**Am Rande — Vibration Controller: **Eine geschlossene Regelung auf ein Soll-Beschleunigungsspektrum (closed-loop vibration control) garantiert, dass das aufgeprägte Profil unabhängig von Last- und Resonanzeffekten dem Soll entspricht — entscheidend, sobald Liftoff die effektive Last innerhalb des Zyklus ändert.

## 5 · Kraftmessung: rückführbare Metrologie

Ein rückführbar kalibrierter Kraftsensor (Kalibrierkette auf nationale Normale) wird über einen Präzisions-Brücken- bzw. Ladungsverstärker und ein Metrologie-DAQ (simultan, hochauflösend) ausgelesen. Der DC-fähige Pfad liefert die Kontrolle ⟨N⟩ = Mg mit ausgewiesener Unsicherheit. Alle Kanäle — Kraft, LDV, Antriebsreferenz — laufen synchron auf einem Takt.

**Am Rande — konkrete Teile (Beispiel): **rückführbar kalibrierter Kraftsensor + Präzisionsverstärker (~€1.000–5.000), Metrologie-DAQ / Echtzeit-Controller (~€2.000–10.000). Die kostentreibenden Posten sind LDV und Kammer (Abschnitte 6 und 7).

## 6 · Berührungslose Messung: Laser-Doppler-Vibrometer

Ein Laser-Doppler-Vibrometer (LDV) misst Geschwindigkeit und Auslenkung von Rahmen und Modulen berührungslos — ohne Massebelastung durch montierte Sensoren und mit sehr hoher Bandbreite und Auflösung. Damit werden das aufgeprägte Egg-Profil und der Liftoff direkt und ohne Rückwirkung verifiziert; ein scannendes oder mehrstrahliges LDV erfasst mehrere Punkte. Das LDV ist die hochwertigste Form der Profil- und Liftoff-Kontrolle.

## 7 · Umgebungs- und Medienkontrolle

Eine Vakuum-/Medienkammer erlaubt es, die Gasdichte ρ über mehrere Größenordnungen zu variieren (Vakuum bis erhöhter Druck) und damit Experiment B durchzuführen: das Drift-Gesetz Drift(ρ). Eine Temperaturstabilisierung (Kammer oder stabilisiertes Labor) eliminiert thermische Drift als Confound. Der Aufstieg eines Ballons — als Alternative — durchfährt ρ ebenfalls, jedoch mit erheblichen Stör- und Pendel-Confounds; die Kammer ist die kontrollierte Laborentsprechung.

**Verbindung zum ρ-Strang: **Experiment B ist die saubere, falsifizierbare Form der Medienkopplung: Der medienbedingte Drift skaliert mit ρ und ist im Vakuum exakt null. Genau dieser Nullpunkt ist die strengste Kontrolle — er trennt einen realen Medieneffekt von mechanischen Artefakten.

## 8 · Schwingungsisolation

Aktiver Schwingungsisolationstisch (rückgekoppelte Isolation) für den niedrigsten Rauschboden. In Kombination mit LDV und Metrologie-DAQ ergibt sich die kleinste nachweisbare Wellenform-Änderung und die feinste ρ-Auflösung in Experiment B.

## 9 · Kontrollen (das wissenschaftliche Rückgrat)

- **Rückführbare Kalibrierung **der Kraftkette → quantitative Skala mit Unsicherheitsbudget, Ruhebasis ⟨N⟩ = Mg.

- **LDV-Profilverifikation: **aufgeprägte Trajektorie berührungslos gegen das Soll-Egg-Profil abgleichen.

- **Vakuum-Nullkontrolle (B): **Drift muss bei ρ → 0 verschwinden; Resttrend = Neigungs-/Restkopplungsartefakt.

- **Neigungs- und Restkopplungs-Check (B): **Libelle/Neigungssensor, Kammeraufhängung, um Scheindrift durch minimale Schräglage auszuschließen.

- **Dummy-/Null-Lauf, Rig-FRF, Wiederholbarkeit, Confounds **wie in den Varianten 1 und 2.

## 10 · Messablauf

**Experiment A.  **Pro Punkt: prescribed acceleration einregeln, LDV-Profil verifizieren, ≥ 100 Zyklen N(t) + LDV + Referenz synchron aufzeichnen, Observablen mit Unsicherheit berechnen, ⟨N⟩ kontrollieren; feines (φ₂, φ₃)- und k-Raster, Abgleich mit dem Modell.

**Experiment B.  **Druck ρ schrittweise von Vakuum zu Gas erhöhen; je ρ den stationären Drift messen (Vakuum zuerst und zuletzt als Nullkontrolle); Drift(ρ) gegen die Vorhersage Drift ∝ ρ prüfen.

## 11 · Erfolgs- und Abbruchkriterium

**Erfolg A.  **Die rückführbar gemessene Karte φ → Wellenform stimmt innerhalb des Unsicherheitsbudgets mit dem Modell überein, inklusive k-Abhängigkeit.

**Erfolg B.  **Der Drift skaliert messbar mit ρ und verschwindet im Vakuum innerhalb der Nachweisschwelle — das bestätigt den Medienmechanismus.

**Falsifikation.  **A: Regime-Struktur nicht über dem Rauschboden bzw. quantitative Abweichung ohne benennbare Ursache. B: kein ρ-Trend oberhalb des Rauschbodens.

**Harte Stopps (Schutz gegen die alte Falle).  **(1) Weicht ⟨N⟩ dauerhaft von der statischen Last ab → defekte Messkette, keine Entdeckung. (2) Verschwindet der Drift im Vakuum nicht → mechanische Restkopplung oder Neigung, kein geschlossener Eigenantrieb. In beiden Fällen wird die Apparatur geprüft und repariert, nicht interpretiert.

## 12 · Leistungsgrenzen von Variante 3

Auch die Metrologie-Klasse ändert die Physik nicht. Die fundamentale Grenze — keine Netto-Schwerpunktsverschiebung und keine Mittelkraft über Mg in einem geschlossenen System — ist von der Apparaturqualität unabhängig. V3 kauft nicht den Weg zu einem Schub, sondern: niedrigsten Rauschboden, rückführbare Genauigkeit, berührungslose Verifikation und das ρ-Gesetz. Der größte Wert von V3 ist, das Erlaubte präzise zu vermessen und das Verbotene dort, wo es null sein muss, sauber als null zu bestätigen.

## 13 · Arbeitspakete

| **AP** | **Inhalt** | **Ergebnis** |
| --- | --- | --- |
| AP1 | Aufbau, aktive Isolation, Kammer, rückführbare Kalibrierung, Kontaktcharakterisierung | metrologische Basis, bekanntes k, ρ-fähig |
| AP2 | Geregelte Aktuatorik (prescribed acceleration), LDV-Profilverifikation | verifiziertes Egg-Profil, exakte φ |
| AP3 | Metrologie-DAQ + Synchronisation, Kontrollen, Rauschboden, Vakuum-Nullkontrolle | Unsicherheitsbudget, Nachweisschwellen |
| AP4a | Experiment A: φ/k-Sweep, rückführbarer Modellabgleich | quantitative φ → Wellenform-Karte |
| AP4b | Experiment B: ρ-Sweep (Vakuum → Gas), Drift-Gesetz | Drift(ρ), Vakuum-Null bestätigt |
| AP5 | Auswertung mit Unsicherheitsbudget, Artefaktanalyse, Veröffentlichung | Bericht, Rohdaten, Publikation |

## 14 · Kostenrahmen

Grob €30.000–150.000+, dominiert von Laser-Vibrometer und Vakuum-/Medienkammer, gefolgt von Mini-Shakern mit Vibration-Controller, Metrologie-DAQ und aktiver Isolation. Skalierbar: Experiment A ist ohne Kammer realisierbar (unteres Ende), Experiment B erfordert die Kammer (oberes Ende).

## Anhang · Beispiel-Stückliste (Orientierung)

| **Komponente** | **Beispielteil** | **Richtpreis** | **Funktion** |
| --- | --- | --- | --- |
| Berührungslos | Laser-Doppler-Vibrometer (ggf. scanning) | ~€20k–80k | Profil/Liftoff ohne Massebelastung |
| Umgebung | Vakuum-/Medienkammer + Pumpe + Druckmessung | ~€5k–30k | ρ-Sweep, Vakuum-Nullpunkt |
| Aktuator ×3 | Mini-Shaker / High-End Voice-Coil + Controller | ~€5k–30k | geregelte prescribed acceleration |
| Isolation | aktiver Isolationstisch | ~€5k–20k | niedrigster Rauschboden |
| Klimakontrolle | Temperaturstabilisierung / Kammer | ~€2k–15k | Driftkontrolle |
| Kraftmetrologie | rückführbarer Sensor + Präzisionsverstärker | ~€1k–5k | N(t) rückführbar, ⟨N⟩-Kontrolle |
| Metrologie-DAQ | simultanes High-Res-DAQ / Echtzeit | ~€2k–10k | exakte Phase, Regelung |

*Teileangaben sind Orientierung. Entscheidend sind die Eigenschaften: geregelte prescribed acceleration, berührungslose Verifikation, rückführbare Kraftmetrologie, kontrollierte ρ-Umgebung mit Vakuum-Nullpunkt, niedrigster Rauschboden.*