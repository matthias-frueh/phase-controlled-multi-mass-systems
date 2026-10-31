# PCMMS – Massenkonzentration auf die bewegten Hauptmassen

Version 0.1 · 31.10.2026 · Konzeptentwurf zur begleitenden Konstruktionsauslegung · ergänzt um Zielkonflikte und gezielte Messvarianten

Projekt: Phase-Controlled Multi-Mass Systems (PCMMS), Matthias Früh

Status: Konzeptentwurf zur Auslegungsbegleitung und zum gezielten Variantenvergleich; keine Messdaten oder nachgewiesene Apparaturauslegung.
Lizenz: CC BY 4.0, siehe [`../../LICENSE-CC-BY-4.0`](../../LICENSE-CC-BY-4.0). Namensnennung: „Matthias Früh, PCMMS“.

> **Einpflegevermerk (31.10.2026).** Grundlage ist der am 31.10.2026 um Zielkonflikte und Messvarianten erweiterte Quelldraft `PCMMS_Konzept_Massenkonzentration_v0_1_2026-10-31.md`. Redaktionell angepasst sind: relativer Verweis auf die Dual-Arm-Spezifikation, Status- und Lizenzangaben, Formelblöcke als `$$`-Blöcke für die Darstellung auf GitHub, ein Satz zur Lage des Trägers L1 innerhalb der Systemgrenze nach AF-01 (Abschnitt 2), „übrige Masse“ statt „übrige Apparatur“ für die 40 kg (Abschnitt 3.3), neutrale Herkunftsangaben (Abschnitt 7, Schritt 1, und „Quellen und Herkunft“) sowie der Schlusssatz des Änderungsvermerks. Beim gemeinsamen Abgleich mit der Messoption (31.10.2026) zusätzlich: Zuordnung rotierender Motorteile in Abschnitt 3.2 an Abschnitt 2 angeglichen; Körperindex in Abschnitt 5 von i und z_{G_i} auf k und z_k in Erweiterung des Formelverzeichnisses umgestellt (i ist dort der Abtastindex); η_H und η_H,bew als konzepteigene Kennzahlen gekennzeichnet; Querverweis auf die Messoption in Abschnitt 8. Auf Vorgabe des Autors (31.10.2026): M als materielle Gesamtmasse eindeutig zugeordnet und von der aus der statischen Zelllast abgeleiteten Größe nach Konvention (b) der Präregistrierung v2 abgegrenzt (Abschnitt 2); Systemgrenze als Angabe je Variante (Abschnitte 6.2 und 7). Die vorhandenen Anforderungen werden durch dieses Begleitkonzept nicht neu festgelegt.

Grundlage: Konstruktionsziel und ergänzende Vorgaben des Autors vom 31.10.2026; Abgleich mit der Anforderungsspezifikation Dual-Armführung v0.4 vom 29.10.2026 einschließlich AF-21-Nachtrag. Die nachfolgenden Kennzahlen und Budgetgleichungen sind Vorschläge dieses Konzeptentwurfs. Zahlenbeispiele sind Rechenbeispiele, keine Apparaturparameter oder nachgewiesenen Auslegungen. Die bestehende Spezifikation wird durch diesen Entwurf nicht geändert.

## 1. Konstruktionsziel

**Ein möglichst großer, mit der jeweiligen Modell- und Messaufgabe vereinbarer Anteil der gesamten bilanzierten Apparaturmasse soll in den gezielt bewegten Hauptmassen liegen. Gesucht wird das geeignete Verhältnis zwischen Hauptmassen, Bewegungsapparat und übriger Apparatur unter Berücksichtigung von Stabilität, erreichbarer Geschwindigkeit, Profiltreue und Messbarkeit. Die Eigenbewegung der Konstruktion wird vollständig in der Dynamik berücksichtigt.**

Die Hauptmassen sind die für das PCMMS-Bewegungsprofil vorgesehenen Massenelemente. Ihre Geometrie, Masse und Schwerpunktbahn werden ausdrücklich festgelegt. Die Konstruktion hält, führt und beschleunigt diese Elemente und soll diese Aufgabe bei möglichst geringer eigener Masse erfüllen.

„Massenkonzentration“ bezeichnet hier die Verteilung der Masse auf diese Funktionen. Die räumliche Lage des gemeinsamen Schwerpunkts und die zulässige Schwerpunktwanderung sind zusätzliche Auslegungsgrößen.

Das Ziel gilt unter den Anforderungen an Bahn- und Phasentreue, Steifigkeit, Festigkeit, Gelenkspiel, Antriebsbelastung und Messbarkeit. Ein höherer Hauptmassenanteil allein belegt weder eine bessere Wellenform noch einen geringeren Energiebedarf.

Ein höherer Hauptmassenanteil kann die Anforderungen an Führung, Stabilität und Antrieb verschärfen, insbesondere wenn dafür die Hauptmassen vergrößert oder tragende Strukturen verkleinert werden. Wie stark dieser Zielkonflikt ausfällt, hängt vom Modell und vom Weg der Massenänderung ab. Der Ansatz dient dazu, einen geeigneten Arbeitsbereich zu finden; zugunsten von Stabilität, erreichbarer Geschwindigkeit oder Messqualität kann ein geringerer Hauptmassenanteil zweckmäßig sein.

In der späteren Gesamtbetrachtung dürfen Hauptmassen sowie andere Baugruppen gezielt verändert werden: Masse kann für eine bestimmte Messung entfernt, ergänzt oder räumlich umverteilt werden. Materialwechsel, das Entfallen für diese Messaufgabe nicht benötigter Funktionen und Messmittel sowie Varianten von Halterungen, Bewegungsapparaten und Kopplungen werden als dokumentierte Konstruktions- oder Messvarianten geführt.

## 2. Drei Massengruppen innerhalb derselben Systemgrenze

| Gruppe | Symbol | Zuordnung |
| --- | --- | --- |
| Hauptmassen | M_H | Summe der gezielt geführten Massenelemente: M_H = Σ m_H,k |
| Bewegte Nebenmassen | M_B | Bewegte Arme, Gelenkteile, Massenträger, Klemmen, mitbewegte Antriebsteile und bewegte Leitungsanteile |
| Trägerfeste Masse | M_T | Träger, feste Halter, trägerfeste Antriebsteile, Versorgung, Steuerung und übrige trägerfeste Bauteile |

Es gilt:

$$
M = M_H + M_B + M_T.
$$

„Bewegt“ und „trägerfest“ beziehen sich auf den Träger L1. Auch eine trägerfeste Baugruppe kann sich gegenüber dem Labor bewegen, etwa beim Nachgeben der Auflage oder beim Kontaktverlust. Rotierende Teile zählen zu M_B, auch wenn ihr Schwerpunkt ortsfest bleibt. Antriebe sind deshalb bei Bedarf in Stator, Rotor, Gehäuse und Übertragung aufzuteilen. Flexible Leitungen werden nach nachvollziehbarer Zuordnung oder als verteilte Masse geführt.

Jede reale Masse wird genau einmal gezählt. Halterungen bleiben in der Funktionsbilanz als Halterungen erkennbar, auch wenn sie unmittelbar an der Hauptmasse sitzen. Eine funktionale Integration ist möglich; die Bezugsgrenze des Hauptmassenkörpers wird dann vor dem Variantenvergleich festgelegt. Ein bloßes Umbenennen eines schweren Halters verbessert die Konstruktion nicht.

Die Systemgrenze folgt AF-01: Alle zum untersuchten Körper gehörenden Teile einschließlich Versorgung sind einzubeziehen. Ob der Träger L1 innerhalb von M liegt, wird nach AF-01 je Versuch festgelegt; M_T enthält trägerfeste Teile nur, soweit sie innerhalb dieser Systemgrenze liegen. Der externe passive Messrahmen L0 gehört nach der bisherigen Ebenenzuordnung nicht zur Apparaturmasse. Getragene Sensoraufsätze sind entsprechend ihrer tatsächlichen Zugehörigkeit zu erfassen. Bei Linie B gehören auch Hülle und Füllgas zur materiellen Massenbilanz; Auftrieb und zugesetzte Luftmasse werden zusätzlich im passenden Kraft- bzw. Dynamikmodell geführt. Auftrieb vermindert die materielle Masse nicht. M ist in diesem Konzept stets die materielle Gesamtmasse innerhalb der angegebenen Systemgrenze; sie wird für Massenanteile, Schwerpunktbildung und tatsächliche Gewichtskraft verwendet. Eine aus der statischen Zelllast abgeleitete Größe, etwa M nach Konvention (b) der Präregistrierung v2, wird davon getrennt geführt und ersetzt M hier nicht ungeprüft; Zuordnung und operative Referenzlast beschreibt die [Messoption](messoption_schwerkraftbezug_lageadaptive_fuehrung_v0_1_2026-10-31.md), Abschnitt 4.

## 3. Zwei Kennzahlen für unterschiedliche Fragen

### 3.1 Hauptmassenanteil der gesamten Apparatur

$$
\eta_H = \frac{M_H}{M_H+M_B+M_T}.
$$

Diese Kennzahl beschreibt, wie viel der Gesamtmasse tatsächlich in den vorgesehenen Hauptmassen liegt. Sie unterstützt die Auslegung zusammen mit den erreichbaren Bewegungs- und Messeigenschaften der jeweiligen Variante. η_H und η_H,bew sind Kennzahlen dieses Konzepts und nicht im Formelverzeichnis v2.8 geführt; dort bezeichnet η ohne diesen Index das Rauschen.

### 3.2 Hauptmassenanteil innerhalb der bewegten Baugruppen

$$
\eta_{H,\mathrm{bew}} = \frac{M_H}{M_H+M_B}.
$$

Diese Kennzahl zeigt, wie groß der Anteil der Hauptmassen gegenüber der mitbewegten Mechanik ist. Sie beschreibt ein Massenverhältnis; unterschiedliche Bahnen, Beschleunigungen und Rotationsträgheiten sind damit noch nicht bewertet.

Ein Motor am Träger kann den bewegten Anteil gegenüber einer Anordnung am Arm verringern. Stator und Gehäuse zählen dann zu M_T, der Rotor als rotierendes Teil nach Abschnitt 2 weiterhin zu M_B; die gesamte Motormasse bleibt in der Gesamtmasse M. Beide Kennzahlen werden deshalb gemeinsam geführt.

### 3.3 Beispiel des Autors

| Bestandteil | Masse |
| --- | ---: |
| Drei Hauptmassen zu je 2 kg | 6 kg |
| Halterungen und Bewegungsapparat | 30 kg |
| Übrige Apparatur | 10 kg |
| Gesamt | 46 kg |

$$
\eta_H = \frac{6}{46} \approx 13{,}0\,\%.
$$

40 kg übrige Masse stehen 6 kg Hauptmassen gegenüber, entsprechend etwa 6,67 kg übriger Masse je Kilogramm Hauptmasse. Hinsichtlich der angestrebten Massenkonzentration ist dieses Verhältnis ungünstig. Die Eignung für eine konkrete Messaufgabe hängt zusätzlich von den damit erreichten Eigenschaften ab.

Die 30 kg sind noch in bewegte und trägerfeste Anteile zu zerlegen. Ohne diese Aufteilung lässt sich η_H,bew nicht bestimmen. Falls die gesamten 30 kg relativ zum Träger bewegt würden und die 10 kg trägerfest wären, ergäbe sich η_H,bew = 6/36 ≈ 16,7 %; das ist lediglich ein bedingter Rechenfall.

Bereits die 10 kg Restmasse würden selbst bei verschwindender Masse des Bewegungsapparats den Hauptmassenanteil auf 6/16 = 37,5 % begrenzen. Auch Träger, Versorgung und sonstige Ausstattung benötigen daher ein Budget.

## 4. Vom gewünschten Anteil zum Massenbudget

Für eine gewählte Zielgröße η_H,Ziel folgt:

$$
M_B+M_T \leq M_H\left(\frac{1}{\eta_{H,\mathrm{Ziel}}}-1\right).
$$

| Beispielhafter Hauptmassenanteil | Höchstens zulässige übrige Masse bei M_H = 6 kg | Höchstens zulässige Gesamtmasse |
| --- | ---: | ---: |
| 50 % | 6 kg | 12 kg |
| 60 % | 4 kg | 10 kg |
| 75 % | 2 kg | 8 kg |

Diese Prozentwerte illustrieren ausschließlich die Budgetrechnung. Sie sind keine Norm, keine physikalische Wirksamkeitsschwelle und keine zugesagte technische Erreichbarkeit. Ein Anteil über 50 % würde bedeuten, dass die Hauptmassen die Mehrheit der Gesamtmasse stellen. Ob dies für eine konkrete Variante erreichbar und zweckmäßig ist, muss die Auslegung zeigen.

Die Budgetrechnung wird iteriert: Für jeden Kandidaten werden die verbleibenden Reserven für Stabilität, Geschwindigkeit, Belastung und Messqualität bestimmt. Ein rechnerisch günstiger Massenanteil wird nur zusammen mit diesen Eigenschaften bewertet. Unterschiedliche Modelle und Messaufgaben können unterschiedliche geeignete Verhältnisse ergeben.

Für die bewegten Nebenmassen lässt sich zusätzlich ein eigenes Budget aus η_H,bew,Ziel ableiten:

$$
M_B \leq M_H\left(\frac{1}{\eta_{H,\mathrm{bew,Ziel}}}-1\right).
$$

Bei drei gleichen Hauptmassen und sechs Armen kann das Gesamtbudget beispielsweise geschrieben werden als:

$$
M = 3m_H + 6m_{\mathrm{Arm}} + 3m_{\mathrm{Halter}} + M_{\mathrm{gemeinsam}}.
$$

Dabei bezeichnet m_Arm die vollständig abgegrenzte Masse eines Arms, m_Halter die zusätzliche gemeinsame Aufnahme je Hauptmasse und M_gemeinsam alle verbleibenden Teile. Antriebe oder Gelenke, die bereits in m_Arm enthalten sind, werden nicht erneut gezählt. Unterschiedliche Arme werden einzeln summiert. Die Aufteilung nach M_B und M_T erfolgt zusätzlich nach ihrer tatsächlichen Bewegung.

Für 3 × 2 kg und das Rechenziel η_H ≥ 50 % müssten sämtliche sechs Arme, drei Aufnahmen und gemeinsamen Teile zusammen höchstens 6 kg wiegen. Diese Gleichung dient als frühe Prüfung der Architektur.

## 5. Die mitbewegte Konstruktion bleibt dynamisch wirksam

Für die gesamte Vertikalkraftbilanz werden die Schwerpunkte aller Körper erfasst, mit z nach oben und Beschleunigungen im Laborbezugssystem:

$$
S_{\mathrm{true}}(t)
= \sum_{k=0}^{n}m_k\ddot z_k(t)
= S_H(t)+S_B(t)+S_T(t),
$$

$$
F_c(t)=Mg+S_{\mathrm{true}}(t)-F_{\mathrm{ext},z}(t).
$$

Der Index k = 0 … n läuft in Erweiterung des Formelverzeichnisses v2.8 (dort k = 1 … n Module) über alle Teilkörper innerhalb der Systemgrenze: k = 0 ist wie dort der übrige Körper bzw. Rahmen, bei L1 innerhalb von M der Träger mit seinen trägerfesten Teilen; k = 1 … n sind Hauptmassen, Arme, Antriebsteile und weitere bewegte Teile, n ist hier deren Anzahl und nicht zwingend die Modulzahl. z_k ist die absolute vertikale Schwerpunktkoordinate des Teilkörpers k; für einen Teilkörper der Gruppe M_H gilt m_k = m_H,k (Abschnitt 2). S_H, S_B und S_T sind die Teilsummen über die Teilkörper der Gruppen M_H, M_B und M_T. Dies ist die Aufgliederung der bestehenden Bilanz aus §2 der Dual-Arm-Spezifikation, keine zusätzliche Kraftquelle. Bei einem räumlich ruhenden, starren Träger ist S_T = 0. Bei Trägerbewegung oder Verformung wird der entsprechende Beitrag mitgeführt. Die Schwerpunktbildung aus allen Teilkörpern entspricht der üblichen Mehrkörperdynamik [1].

Für jeden bewegten starren Körper gehören Masse, Schwerpunktlage und Trägheitstensor ins Modell [2]. Die vertikale Summenkraft hängt von den Schwerpunktbeschleunigungen ab; Rotationsträgheiten bestimmen zusätzlich Antriebsmomente, Lagerlasten und Momentenreaktionen. Ein Rotor mit ortsfestem Schwerpunkt kann deshalb trotz verschwindendem eigenem Vertikalkraftbeitrag relevant sein.

Für Variantenvergleiche sind mindestens zu prüfen:

- Kraftbeiträge der Hauptmassen und der bewegten Nebenmassen über die vorgesehenen Bahnen und Phasenzustände.
- Resultierende Wellenform, ausgewertete Harmonische und die jeweiligen PCMMS-Observablen.
- Spitzenmomente, Kräfte und Lastaufteilung der Arme sowie Reaktionen am Träger.
- Bahn- und Phasentreue unter Last, Eigenfrequenzen und Spiel.

Die phasenabhängige Aufhebung von Kraftbeiträgen kann einen kleinen Summenwert ergeben, während einzelne Arme hoch belastet bleiben. Eine allgemeine Dominanzkennzahl aus dem Quotienten der resultierenden Nebenmassenkraft und der resultierenden Hauptmassenkraft wäre nahe solchen Auslöschungen ungeeignet. Beiträge und Bauteillasten werden deshalb zusätzlich getrennt betrachtet.

Bei einem Vergleich mit einem vereinfachten Modell, das nur die dynamischen Beiträge der Hauptmassen enthält, bleibt die reale Gesamtmasse als Grundlast erhalten. Andernfalls würden zwei verschiedene Änderungen gleichzeitig verglichen. Die Grenzen eines vereinfachten Modells sind anhand der vollständigen Kinematik und Dynamik zu bestimmen; die Massenteilung allein liefert diese Grenzen nicht [1, 3].

## 6. Material, Volumen und konstruktive Entscheidungen

Für ein homogenes Massenelement gilt m = ρV. Höhere Dichte kann das erforderliche Volumen einer vorgegebenen Hauptmasse verringern. Ob dadurch die ganze Apparatur leichter wird, hängt davon ab, ob Aufnahmen, Abstände und Tragstruktur tatsächlich verkleinert werden können. Die zu beschleunigende Masse und ihre Trägheitskräfte bleiben bei gleichem Bewegungsprofil erhalten.

Für jede Variante werden daher folgende Entscheidungen zusammen bewertet:

| Entscheidung | Zu untersuchende Wirkung |
| --- | --- |
| Geometrie und Material der Hauptmasse | Bauraum, Schwerpunktlage, Rotationsträgheit und Befestigung |
| Geometrie und Material der Arme | Eigenmasse, Steifigkeit, Festigkeit und Eigenfrequenzen |
| Position von Motoren und Übertragung | Bewegte Nebenmasse, reflektierte Trägheit, Spiel, Nachgiebigkeit und Gesamtmasse |
| Aufnahme der Hauptmasse | Haltermasse, Krafteinleitung, Austauschbarkeit und Reproduzierbarkeit |
| Mechanische Kopplungen | Masse, Steifigkeit, Dämpfung, Spiel, Vorspannung und Übertragung der Kräfte und Momente |
| Anzahl der Freiheitsgrade | Erforderliche Profilfähigkeit und daraus folgende Gelenk-, Antriebs- und Strukturmasse |
| Versorgung und Träger | Verbleibendes Gesamtbudget, Wärmeabfuhr und Kraftpfade |
| Funktionsumfang und Messausstattung | Für die jeweilige Aufgabe erforderliche Funktionen, Messkanäle, Messqualität und zusätzliche Masse |

Schwere Teile möglichst trägernah anzuordnen ist als Variante zu prüfen, wenn dadurch ihre Bewegung oder der wirksame Hebelarm verringert wird. Zusätzliche Übertragungsteile sind mit ihrer Masse und Nachgiebigkeit gegenzurechnen. Das Auslagern von Antrieben auf einen externen Rahmen verändert Systemgrenze und Kraftpfade und ist kein bloßer Budgetgewinn innerhalb derselben Apparatur.

Eine Erhöhung der Hauptmassen verbessert rechnerisch η_H, erhöht bei gleicher Beschleunigung aber auch die erforderlichen Kräfte und kann größere Antriebe und Strukturen nach sich ziehen. Hauptmassen, Bewegungsprofil und Bewegungsapparat werden deshalb gemeinsam iteriert.

### 6.1 Zielkonflikte zwischen Massenanteil und erreichbarer Bewegung

Der Weg zu einem höheren Hauptmassenanteil wird ausdrücklich benannt:

| Änderung | Modellabhängig zu prüfende Folgen |
| --- | --- |
| Größere Hauptmassen bei gleichem Bewegungsprofil | Größere Trägheitskräfte und Gelenkbelastungen; erreichbare Geschwindigkeit, Beschleunigung und Profiltreue mit dem vorhandenen Antrieb neu bestimmen |
| Weniger Masse in tragenden Armen oder Halterungen | Veränderte Steifigkeit, Eigenfrequenzen, Verformung und Belastungsreserven; zugleich geringere bewegte Eigenmasse möglich |
| Weniger trägerfeste Masse | Veränderte Gesamtlast, Schwerpunktlage, Trägheit und Kontaktbedingungen; Standsicherheit und Bewegung des Trägers neu bewerten |
| Entfall entbehrlicher Ausstattung | Geringere Masse bei möglicherweise unveränderter Tragstruktur; mehrere Auslegungsziele können sich gleichzeitig verbessern |
| Andere Material- oder Kopplungsvariante | Geänderte Masse und gegebenenfalls geänderte Steifigkeit, Dämpfung und Lastpfade; Gesamtwirkung berechnen |

Damit ist eine durchgehend monotone Verschlechterung bei steigendem η_H nicht vorausgesetzt. Die Aussage des Autors wird als zu prüfender Zielkonflikt geführt: Je weiter die Hauptmassenkonzentration in einer konkreten Architektur getrieben wird, desto stärker können andere Anforderungen die weitere Steigerung begrenzen.

„Stabilität“ wird dabei konkretisiert: mechanische Standsicherheit und Kippreserve, ausreichende Struktursteifigkeit sowie Regelstabilität und Schwingungsneigung der Führung. „Geschwindigkeit“ wird zusammen mit Hub, Bahnform, Frequenz und zulässiger Beschleunigung angegeben. Bei einer sinusförmigen Translation und gleichem Hub wächst die Spitzenbeschleunigung beispielsweise mit dem Quadrat der Frequenz; die Trägheitskraft einer Hauptmasse wächst bei gleicher Beschleunigung proportional zu ihrer Masse. Diese Beziehungen erklären einzelne Zielkonflikte, ersetzen aber die vollständige Mehrkörperauslegung nicht.

Ergebnis des Vergleichs ist ein für Modell und Messaufgabe geeigneter Bereich von Massenverhältnissen mit den jeweils erreichbaren Bewegungs- und Messeigenschaften. Eine eindeutige beste Variante setzt zusätzlich voraus, dass die Prioritäten zwischen diesen Eigenschaften festgelegt sind.

### 6.2 Gezieltes Entfernen, Ergänzen und Umverteilen von Masse

Die Hauptmassen sind veränderbare Auslegungs- und Versuchsparameter. Für eine Variante kann gelten:

$$
m'_{H,k}=m_{H,k}+\Delta m_{H,k}.
$$

Δm_H,k ist bei Ergänzung positiv und bei Entnahme negativ; das verbleibende Massenelement behält eine positive Masse und eine definierte Funktion. Sind alle übrigen Bauteile unverändert, gilt M′ = M + Σ_k Δm_H,k. Änderungen weiterer Baugruppen gehen zusätzlich in die Gesamtbilanz ein.

Mögliche Varianten sind:

- Entnehmbare oder ergänzbare Masseneinsätze zur Untersuchung der Massenabhängigkeit einer Messgröße.
- Materialwechsel bei möglichst gleicher Außenkontur, um die Masse bei vergleichbarer äußerer Geometrie zu variieren. Geänderte Steifigkeit und Trägheitseigenschaften werden mitgeführt.
- Gezielte Materialentnahme aus einem Hauptmassenelement, sofern die geänderte Geometrie, Befestigung und Schwerpunktlage im Modell erfasst sind.
- Räumliche Umverteilung bei gleicher Masse zur Untersuchung von Schwerpunktlage und Rotationsträgheit.
- Entfall für den jeweiligen Versuch entbehrlicher integrierter Funktionen, Messmittel und zugehöriger Halter oder Leitungen.

Jede Änderung wird ihrer Funktionsgruppe M_H, M_B oder M_T zugeordnet. Das Entfernen eines mitbewegten Sensors verringert beispielsweise die bewegte Nebenmasse; es wird nicht allein wegen seiner Position am Hauptmassenelement als Änderung von M_H verbucht. Die festgelegte Abgrenzung des Hauptmassenkörpers bleibt nachvollziehbar.

Für die Messplanung werden zwei Vergleichsfälle unterschieden:

| Vergleichsfall | Behandlung der Masse und der Auswertung |
| --- | --- |
| Gesamtmasse darf sich ändern | Neue Gesamtmasse und Grundlast bestimmen; Masse, Schwerpunkt, Trägheit sowie Kontakt- und Bewegungsmodell aktualisieren |
| Gesamtmasse soll gleich bleiben | Entnommene Hauptmasse kann beispielsweise an einer definierten trägerfesten Position ergänzt werden; die geänderte räumliche Massenverteilung und die daraus folgenden Dynamikänderungen werden mitgeführt |

Für jede Messvariante werden Ausgangszustand, Änderung, Messziel, Systemgrenze (Lage von L1 und Sensoraufsätzen nach AF-01), M_H/M_B/M_T, Schwerpunkt- und Trägheitseigenschaften, Bewegungsprofil, Phasen und Kopplungsparameter festgehalten. Bei einer vergleichenden Messung wird benannt, welche Größen gleich gehalten und welche bewusst variiert werden. Mehrere gleichzeitige Änderungen gelten als kombinierte Variante; eine beobachtete Änderung lässt sich dann ohne weitere Gegenproben nicht eindeutig einem einzelnen Parameter zuordnen.

Die Gesamtbetrachtung kann somit auch zu kleineren Hauptmassen oder zu bewusst ergänzter Masse führen, wenn dadurch eine Messung aussagekräftiger oder der betreffende Arbeitsbereich besser erreichbar wird.

### 6.3 Variation von Funktionsumfang, Halterungen und Kopplungen

Für die jeweilige Messaufgabe wird festgelegt, welche Funktionen und Messmittel benötigt werden. Eine reduzierte Ausstattung kann entbehrliche Sensoren, Zusatzfunktionen, Befestigungen oder Leitungen einsparen. Die für diese Aufgabe erforderliche Messqualität, Zeitzuordnung und Bilanzprüfung werden für den reduzierten Aufbau erneut bestimmt; die Vergleichbarkeit mit dem Ausgangszustand wird dokumentiert.

Halterungen, Bewegungsapparate und Kopplungen sind gleichberechtigte Variationsgrößen. Neben ihrer Masse werden insbesondere Kinematik, Steifigkeit, Dämpfung, Spiel, Vorspannung und Lastaufteilung erfasst. Eine geänderte Kopplung kann den Kraftverlauf auch bei unveränderten Hauptmassen verändern. Solche Varianten werden mit dem jeweils passenden Dynamikmodell ausgewertet und in derselben Variantenliste geführt.

## 7. Arbeitsablauf für den Variantenvergleich

1. Modell- und Messaufgabe sowie die dafür benötigten Funktionen und Messmittel festlegen. Hauptmassen, Schwerpunktbahnen, Hub, Frequenz, Phasenbereich und Beschleunigungs-/Ruckgrenzen für die betreffende Variante bestimmen. Die 3 × 2 kg aus dem Beispiel des Autors (Abschnitt 3.3) bleiben bis zu einer solchen Festlegung ein Beispiel.
2. Systemgrenze nach AF-01 angeben (Lage von L1, getragene Sensoraufsätze). Alle Baugruppen mit Masse, Funktionszuordnung und Bewegungsart erfassen. Bei bewegten Körpern Schwerpunktlage und Trägheit ergänzen; Unsicherheiten der Schätzwerte angeben.
3. η_H und η_H,bew berechnen und daraus vorläufige Budgets für Arme, Aufnahmen, Antrieb, Träger und Versorgung ableiten. Gemeinsame Bauteile nur einmal zählen. Den Weg der Massenänderung und die erwarteten Zielkonflikte benennen.
4. Bei reinen Konstruktionsvergleichen die Kandidaten auf dieselben geforderten Hauptmassenbahnen auslegen. Bei gezielten Messvarianten bewusst geänderte Massen, Materialien, Profile, Funktionen oder Kopplungen sowie die gleich gehaltenen Größen festlegen. Tatsächlich erreichbare Geschwindigkeit, Bahn- und Phasentreue sowie Spitzenlasten mitprüfen.
5. Vollständige Kraft- und Momentenverläufe berechnen und mit dem vereinfachten Hauptmassenmodell vergleichen. Bei der Dual-Armführung Schleifenbedingungen und Lastaufteilung berücksichtigen.
6. Varianten anhand von Massenanteilen, Stabilität, erreichbarer Geschwindigkeit, Profiltreue, Steifigkeit, Belastung und Messqualität gemeinsam bewerten. Einen geeigneten Arbeitsbereich und die Prioritäten der Messaufgabe festlegen; Zielanteile erst danach als Anforderungen übernehmen.
7. Nach jeder Massen-, Material-, Funktions- oder Kopplungsänderung die betroffene Massenbilanz, Schwerpunkt- und Trägheitsdaten, Dynamikparameter und messtechnischen Eigenschaften aktualisieren. Ergebnisse dem jeweiligen Aufbauzustand zuordnen.

Eine einzige Variantenliste genügt als Arbeitsblatt:

| Variante und Messziel | Systemgrenze (L1, Sensoraufsätze) | M_H / M_B / M_T | η_H / η_H,bew | Profil und erreichbare Geschwindigkeit | Stabilität, Lasten und Messqualität | Geeigneter Arbeitsbereich |
| --- | --- | --- | --- | --- | --- | --- |
| Noch festzulegen | – | – | – | – | – | – |

Zu jeder Zeile gehören der dokumentierte Änderungsumfang sowie die Festlegung, ob Gesamtmasse, Geometrie, Hauptmassenbahn oder andere Vergleichsgrößen konstant gehalten werden. Die Angaben bleiben im selben Konzept beziehungsweise im zugehörigen Parametersatz zusammengeführt.

## 8. Anschluss an die bestehende Spezifikation

Das Konzept ergänzt AF-01 (Systemgrenze), AF-08/09 (Schwerpunktbahnen), AF-21 (Kinematik- und Kraftbilanz) sowie AF-23 bis AF-25 (Lasten, Steifigkeit, Spiel). Für die Dual-Armführung gelten zusätzlich AF-06/07 zur kinematischen Schleife, Lastaufteilung und Begrenzung unerwünschter Reaktionen.

Als späterer Anforderungstext bietet sich an:

> Für jede Konstruktions- und Messvariante sind der Anteil der gezielt geführten Hauptmassen an der Gesamtmasse und ihr Anteil innerhalb der bewegten Baugruppen auszuweisen. Arme, Aufnahmen, Antriebe und übrige Apparatur werden mit getrennten Massenbudgets geführt. Das geeignete Verhältnis wird für das jeweilige Modell und die Messaufgabe unter Berücksichtigung von Stabilität, erreichbarer Geschwindigkeit, Profiltreue, Belastbarkeit und Messqualität bestimmt. Die Beiträge aller bewegten Körper zur Kraft- und Momentendynamik werden berücksichtigt. Gezielte Massenentnahme, Massenergänzung, Umverteilung, Materialwechsel, Änderungen des benötigten Funktions- und Messumfangs sowie Varianten von Halterungen, Bewegungsapparaten und Kopplungen sind mit ihren Auswirkungen auf Bilanz, Dynamik und Messvergleich zu dokumentieren.

Wie Gewichtskraftbezug, Lastabweichung, Lage und Position für solche Varianten gemessen und für eine lageabhängige Führung genutzt werden können, beschreibt der Konzeptentwurf [Schwerkraftbezogene Messung und lageadaptive Bewegungsführung](messoption_schwerkraftbezug_lageadaptive_fuehrung_v0_1_2026-10-31.md).

Offen bleiben die konkreten Zielanteile, der Apparaturparametersatz, Materialien und Geometrien, die erreichbaren Budgets und Arbeitsbereiche sowie die Prioritäten der einzelnen Modell- und Messaufgaben. Die geltende Stufenfolge und die offene Wahl der Antriebsarchitektur werden durch dieses Begleitkonzept nicht neu entschieden.

## Änderungsvermerk

Ergänzung vom 31.10.2026 auf Vorgabe des Autors: Zielkonflikte zwischen Hauptmassenanteil, Stabilität und erreichbarer Geschwindigkeit; modell- und messaufgabenabhängige Verhältniswahl; gezielte Entnahme, Ergänzung und Umverteilung von Masse; Material- und Funktionsänderungen einschließlich entbehrlicher Messmittel; Variation von Halterungen, Bewegungsapparaten und Kopplungen. Konstruktionsziel, Arbeitsablauf und Anforderungsvorschlag entsprechend erweitert. Der Quelldraft wurde unter seiner ursprünglichen Dateibezeichnung weitergeführt; für das Repository gilt die dortige Ordner- und Dateikonvention.

## Quellen und Herkunft

- Projektquelle: [PCMMS_Anforderungsspezifikation_Dual-Armfuehrung_v0_4_2026-10-29.md](anforderungsspezifikation_dual_armfuehrung_v0_4_2026-10-29.md), einschließlich AF-21-Nachtrag; am 31.10.2026 vollständig gelesen.
- [1] Russ Tedrake, MIT: [Underactuated Robotics – Highly-articulated Legged Robots, Generalization to multibody / Centroidal dynamics](https://underactuated.mit.edu/humanoids.html). Grundlage für Schwerpunkt- und Gesamtimpulsbeschreibung; abgerufen am 31.10.2026.
- [2] Drake, MIT: [Spatial Mass Matrix (Spatial Inertia)](https://drake.mit.edu/doxygen_cxx/group__multibody__spatial__inertia.html). Masse, Schwerpunktlage und Rotationsträgheit eines starren Körpers; abgerufen am 31.10.2026.
- [3] Russ Tedrake, MIT: [Underactuated Robotics – Multi-Body Dynamics](https://underactuated.mit.edu/multibody.html). Mehrkörperdynamik und kinematische Zwangsbedingungen; abgerufen am 31.10.2026.

Das Konstruktionsziel und die ergänzten Variationsmöglichkeiten stammen aus den Vorgaben des Autors vom 31.10.2026. Kennzahlen, Budgetbeispiele, Einordnung der Zielkonflikte und der vorgeschlagene Arbeitsablauf sind projektspezifische Ableitungen. Die Quellen begründen die mechanische Modellierung; sie belegen keine technische Erreichbarkeit der beispielhaften Massenbudgets und keine allgemeine monotone Beziehung zwischen Hauptmassenanteil, Stabilität und Geschwindigkeit.
