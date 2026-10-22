# PCMMS – Ergänzende Notiz zur energetischen Erweiterung

**Projekt:** PCMMS · Matthias Früh  
**Stand:** 5. September 2026  
**Status:** Methodische Arbeitsnotiz; keine neue Simulation und kein experimenteller Nachweis.

> **Vermerk (22.10.2026).** Originaldatei `PCMMS_Notiz_Energiebilanz_und_Modellvergleich_2026-09-05.md`, Stand
> 05.09.2026; hier unverändert bis auf diesen Vermerk. Methodische Arbeitsnotiz ohne Simulation, Empfängerwahl oder
> Messung (Kopf und Abschnitt 8). Linie C, Arbeitspaket AP-29 (Linie C: Wiederaufnahmebedingungen; Stufe S5, Status
> „später (geparkt)“, [`../arbeitsplan_status.md`](../arbeitsplan_status.md)). Seit September 2026 überholt oder offen:
> - **Einordnung von Linie C:** Das [Formelverzeichnis v2.8](../formelverzeichnis/README.md) vom 16.10.2026 fasst
>   Linie C als mögliche Umlenkung oder Abspaltung außerhalb der Systemgrenze, nicht als Energieaufnahme und
>   -verteilung innerhalb des Körpers (Abschnitt „Anschluss an Linie B und C“). Die Notiz ist älter;
>   Kopplungsmechanismus, Empfänger und Messstrategie lässt sie offen (Abschnitt 1).
> - **Wiederaufnahme:** Festzulegen sind danach äußerer Träger (Medium oder Feld), Ziel der Umlenkung oder Abspaltung,
>   Mechanismus, äußere Messgröße sowie Energie- und Impulsbilanz über die Systemgrenze; mit einem Medium als Träger
>   setzt Linie C die Klärung von Linie B voraus. Weder ein erhöhter Kraft-RMS noch eine veränderte Schiefe ist für sich
>   ein Nachweis einer solchen Wirkung oder verbesserter Energieeffizienz (ebd.).
> - **Bezugsdokumente:** „PCMMS – Projektfortführung und phasenselektive Energieübertragung“ (Abschnitt 1) und
>   `PCMMS_Zusammenfassung_Energieerweiterung_2026-09-05.md` (Abschnitt 9) liegen außerhalb des Repositorys.
>
> Lizenz wie der Ordner: CC BY 4.0 ([`../../LICENSE-CC-BY-4.0`](../../LICENSE-CC-BY-4.0)).

## 1. Zweck und Einordnung

Diese Notiz ergänzt „PCMMS – Projektfortführung und phasenselektive Energieübertragung“ um die Präzisierungen aus der anschließenden Diskussion. Sie hält die korrekte Energiebilanz, die Bedeutung linearer Überlagerung, getrennte Zielgrößen und Anforderungen an einen aussagekräftigen Modellvergleich fest.

Die Erweiterung bleibt eine plausible, noch zu konkretisierende Forschungsrichtung. Ein Vorteil des Egg-Profils, der Mehrmassenanordnung oder eines besonderen Empfängermaterials ist nicht nachgewiesen. Kopplungsmechanismus, Empfänger und Messstrategie bleiben offen.

## 2. Energiebilanz ohne Doppelzählung

Für eine festgelegte Systemgrenze und ein gemeinsames Beobachtungsintervall gilt:

$$E_{zu}+E_{initial}=E_{ab}+E_{final}.$$

Dabei bezeichnen E_initial und E_final die gesamte gespeicherte Energie innerhalb dieser Grenze zu Beginn und Ende des Intervalls. Gleichwertig gilt:

$$E_{zu}-E_{ab}=\Delta E_{System},\qquad \Delta E_{System}=E_{final}-E_{initial}.$$

Initialenergie, Finalenergie und dieselbe Speicheränderung dürfen nicht zusätzlich nebeneinander bilanziert werden. Werden mehrere Speicher getrennt betrachtet, müssen ihre Beiträge eindeutig und überschneidungsfrei definiert sein.

| Bilanzbeitrag | Zuordnung |
|---|---|
| Antriebsarbeit, elektrische Einspeisung, aufgenommene Umgebungsenergie | Über die Systemgrenze zugeführte Energie |
| Nutzenergie an einer äußeren Last | Über die Systemgrenze abgegebene Energie |
| Wärme, die die Systemgrenze verlässt | Abgegebene Energie |
| Erwärmung innerhalb des Systems | Änderung gespeicherter innerer Energie |
| Laden eines innerhalb der Grenze liegenden Empfängers | Änderung gespeicherter Energie |
| Energieaufnahme eines außerhalb liegenden Empfängers | Energieabgabe über die Grenze |

Reibung und elektrische Widerstände wandeln Energie in Wärme um. Ob diese als Abgabe oder Speicheränderung erscheint, hängt von Systemgrenze und Beobachtungsdauer ab. „Verlust“ ist eine Nutzungsbewertung und darf nicht als unbestimmter Korrekturterm die Bilanz schließen.

Das messtechnische Residuum lautet:

$$r_E=E_{zu}-E_{ab}-\Delta E_{System}.$$

Es ist gegen die kombinierte Messunsicherheit zu prüfen. Unbekannte Beiträge dürfen nicht als passender Rest bestimmt und anschließend als unabhängige Bestätigung der Bilanz verwendet werden.

## 3. Phasenabhängige Energie ist auch bei linearer Dynamik möglich

Eine Energieverteilungsänderung beweist für sich weder Nichtlinearität noch eine zusätzliche Mehrmodul-Wechselwirkung. Bereits eine lineare Überlagerung von Bewegungen kann phasenabhängige Energiegrößen erzeugen, weil Leistung und Energie häufig quadratisch von den Zustandsgrößen abhängen.

Als einfaches Beispiel dient ein gemeinsamer linearer Dämpfer mit Dämpfungskonstante c und relativer Geschwindigkeit v = v_1 + v_2. Seine dissipierte Leistung ist:

$$P=c(v_1+v_2)^2=c v_1^2+c v_2^2+2c v_1v_2.$$

Für v_1 = a cos(ωt) und v_2 = b cos(ωt + φ), gemittelt über ganze Perioden, folgt:

$$\langle P\rangle=\frac{c}{2}(a^2+b^2)+cab\cos\varphi.$$

Der Kreuzterm hängt von der relativen Phase ab, obwohl der Dämpfer linear ist. Das Beispiel betrifft Dissipation, nicht Speicherung. Es zeigt die Auswertelogik, nicht bereits ein PCMMS-Empfängermodell.

**Konsequenz:** Im linearen Referenzmodell sind zunächst die Bewegungen beziehungsweise Felder zu überlagern. Erst daraus werden Leistung und Energie berechnet. Die bloße Addition isolierter Einzelmodulenergien kann relevante Kreuzterme auslassen.

Eine solche Überlagerung setzt dasselbe lineare System mit gleichen Randbedingungen voraus. Wird beim Einzelmodulversuch die mechanische Struktur, Last oder Kopplung verändert, können seine Ergebnisse nicht ohne Weiteres als Beiträge desselben Mehrmodulsystems verwendet werden.

Auch eine Abweichung von einem korrekt formulierten Referenzmodell ist zunächst ein Modellresiduum. Ihre Ursache kann etwa in unberücksichtigter Kopplung, Parameterfehlern, Nichtlinearitäten oder Messartefakten liegen; sie ist gesondert zu identifizieren.

## 4. Energieverteilung und Ertrag getrennt messen

Für zwei Empfänger sind zwei Fragen zu unterscheiden:

$$s_1=\frac{E_1}{E_1+E_2}$$

beschreibt den Anteil des ersten Empfängers an der insgesamt betrachteten Empfängerenergie. Dagegen beschreibt

$$y_1=\frac{E_1}{E_{zu}}$$

den auf den Energieeinsatz bezogenen Ertrag dieses Empfängers.

Ein größerer Verteilungsanteil s_1 kann auch dadurch entstehen, dass E_2 sinkt. Er belegt weder einen Anstieg von E_1 noch einen besseren Gesamtwirkungsgrad. Deshalb sind E_1, E_2 und E_zu zusätzlich absolut auszuweisen.

Voraussetzungen für diese Kennzahlen sind ein gemeinsames Zeitintervall, definierte Anfangszustände, eindeutig definierte Energiegrößen und positive, ausreichend von null entfernte Nenner. Bei bidirektionaler Übertragung oder Nettoentladung ist eine einfache Anteilsinterpretation möglicherweise ungeeignet.

Für einen Bilanzport mit positiver Leistung in Richtung Empfänger können Aufnahme und Rückgabe getrennt erfasst werden:

$$E_{auf}=\int_W\max(P(t),0)\,dt,\qquad E_{rueck}=\int_W\max(-P(t),0)\,dt.$$

Die Nettoübertragung ist E_auf − E_rueck. Sie entspricht nur dann unmittelbar dem Speicherzuwachs, wenn keine weiteren Energiepfade oder Umwandlungsverluste innerhalb des Empfängers zu berücksichtigen sind.

Ein Leistungsintegral über einen Teil des Zyklus zeigt die zeitliche Verteilung. Für Speicherfähigkeit ist zusätzlich der Energiezustand nach einem definierten Halteintervall relevant.

## 5. Forschungswert und Referenzfälle

Eine gemeinsame Zeitverschiebung aller Anregungen kann in einem zeitinvarianten System lediglich dieselbe Antwort zeitlich verschieben. Das ist als Funktionstest nützlich. Eine Änderung relativer Phasen kann dagegen die Überlagerung und die Energieverteilung verändern.

Eine phasenabhängige Verteilungsänderung innerhalb eines linearen Modells kann technisch und wissenschaftlich relevant sein. Nichtlinearität ist kein notwendiges Qualitätskriterium. Eigenständiger Forschungswert hängt von der konkreten Fragestellung, quantitativen Erklärung, Robustheit, Vergleichbarkeit und Abgrenzung zur Literatur ab.

Geeignete Prüfungen sind:

1. **Zeitverschiebungskontrolle:** Bleibt nach gemeinsamer zeitlicher Ausrichtung lediglich dieselbe Antwort bestehen?
2. **Relative Phasenvariation:** Ändern sich Energieanteile bei unveränderter Empfängeranordnung?
3. **Profilvergleich:** Erzeugt das Egg-Profil gegenüber einer geeigneten Sinusreferenz eine zusätzliche, quantitativ erklärte Wirkung?
4. **Lineares Referenzmodell:** Erklärt die Überlagerung der Zustandsgrößen einschließlich der energetischen Kreuzterme das Ergebnis?
5. **Robustheit und Aufwand:** Bleibt der Befund unter Parameterabweichungen bestehen, und welcher Energie- und Materialeinsatz ist erforderlich?

Ein beobachteter Effekt ist nicht automatisch neu oder nützlich. Umgekehrt ist eine vollständig durch bekannte lineare Physik erklärbare Wirkung nicht automatisch wissenschaftlich wertlos.

## 6. Zwei Federspeicher als mögliche Pilotvariante

Zwei Federspeicher sind eine mögliche mechanische Modellvariante, keine bereits getroffene Projektentscheidung. Zu definieren wären die Kopplung zu den Modulen, Federkennwerte, Dämpfung, Anfangsauslenkungen sowie die Bedingungen für Aufnahme, Rückgabe und gegebenenfalls Entkopplung.

Die Zuordnung der Empfänger zu unterschiedlichen Phasen darf die gesuchte Verteilungsänderung nicht bereits erzwingen. Beim Phasensweep sollen Empfängergeometrie und Kopplungsregel unverändert bleiben. Entscheidend ist, welche Wirkung die relative Modulphase unter diesen Bedingungen hat.

Bei idealen linearen Federn gilt E_j = k_j x_j²/2. Im periodischen stationären Betrieb kann der Speicherzustand nach einem vollständigen Zyklus wieder derselbe sein. Deshalb sind temporäre Speicherung, Energieumsatz und bleibender Speicherzuwachs getrennte Zielgrößen.

Für einen fairen Einzelmodulvergleich sind Masse, Kopplungsfläche, Last, Hub, Frequenz und Energieeinsatz ausdrücklich zu dokumentieren. Nicht alle Bedingungen lassen sich gleichzeitig identisch halten; die gewählte Vergleichsnormierung muss zur Forschungsfrage passen.

## 7. Simulation und Messkonzept gemeinsam entwickeln

Ein vollständig ausgearbeitetes Messsystem ist keine Voraussetzung für eine erste idealisierte Simulation. Systemgrenze, Energieflüsse und Annahmen müssen jedoch von Anfang an benannt sein. Messbarkeit und Unsicherheit werden anschließend konkretisiert.

Ebenso muss ein besonderer Vorteil nicht bereits simuliert sein, bevor ein kleiner Charakterisierungsversuch sinnvoll ist. Ein solcher Versuch kann benötigt werden, um Kopplungskennwerte, Dämpfung oder Leckverluste für das Modell zu bestimmen.

Für eine bestätigende Messkampagne sind Messstrategie, Auswertefenster, Kontrollen und Entscheidungskriterien vorab festzulegen. Wiederholpräzision ist dabei ein Unsicherheitsbeitrag; eine praktisch relevante Äquivalenzgrenze braucht eine zusätzliche inhaltliche Begründung.

## 8. Präzisierte nächste Aufgabe

> Ein Minimalmodell mit festgelegter Quelle, unveränderter Empfängeranordnung und einer definierten Kopplung soll prüfen, ob relative Phasenlage und Bewegungsprofil die Energieanteile zwischen zwei Empfängern verändern. Die Auswertung soll gemeinsame Zeitverschiebung, lineare Überlagerung einschließlich energetischer Kreuzterme und mögliche zusätzliche Effekte unterscheiden.

Als erste Ergebnisse wären ausreichend:

- eine geschlossene Modellbilanz ohne Doppelzählung;
- getrennte Angaben zu Empfängerenergien, Energieeinsatz und Verteilungsanteilen;
- ein nachvollziehbares Referenzmodell;
- eine Abschätzung, welche Größen experimentell zu charakterisieren sind.

Eine Empfängerwahl, eine Simulation oder eine Messung wurde durch diese Notiz noch nicht vorgenommen.

## 9. Herkunft und Geltungsbereich

Diese Notiz konsolidiert die Diskussion im Anschluss an `PCMMS_Zusammenfassung_Energieerweiterung_2026-09-05.md`. Sie dokumentiert Bilanz- und Modellierungspräzisierungen sowie offene Entwicklungsentscheidungen. Die Formeln dienen der begrifflichen Klärung und einfachen Herleitung; sie sind keine Auswertung neuer PCMMS-Daten. Eine erneute Prüfung der Dissertation oder eine zusätzliche Literaturrecherche ist nicht Bestandteil dieser Notiz.
