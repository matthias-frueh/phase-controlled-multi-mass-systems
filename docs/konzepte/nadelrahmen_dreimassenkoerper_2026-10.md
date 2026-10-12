# Sechs-Nadel-Messrahmen · Dreimassenkörper in der Rundum-Messung (Vollmodell)

> **Vermerk (11.10.2026, Nachtrag 12.10.2026).** Konzept- und Modellarbeit zu Linie A, Arbeitspaket AP-27
> (räumliche Last), ausgearbeitet am 11.10.2026 nach der Festhaltung des Autors vom selben Tag (Abschnitt 1).
> Nicht umgesetzt, nicht an Hardware geprüft;
> es gibt keine Messdaten. Alle Zahlen sind Simulation oder Analytik mit angenommenen Maßen, Steifigkeiten und
> Trägheiten (Rechenbeispiele, keine Bauvorgabe; Annahmen in Abschnitt 5). Rechnungen, Gegenprüfung und Grenzen
> stehen in [`../../rechnungen/nadelrahmen/PROTOKOLL.md`](../../rechnungen/nadelrahmen/PROTOKOLL.md) (Befunde NR-01
> bis NR-09). Kinematische Lagerung und Einspannung bleiben beide als anwendungsabhängige Möglichkeiten offen; das
> Konzept dokumentiert beide, eine Bauentscheidung steht nicht an. Es ändert weder die
> [Präregistrierung v2](../praeregistrierung_v2_entwurf.md) noch die V1-Planung.

*Matthias Früh · Oktober 2026 · prä-experimentell*

## 1 Festhaltung und Herkunft

Vom Autor am 11.10.2026 festgehalten:

- Der Dreimassenkörper – oder eine Modellvariante – wird in einen Rahmen mit sechs Messpunkten eingebettet:
  **Nord, Süd, Ost, West, oben, unten.**
- Am Körper liegen **Fixierstellen**. Nadelsysteme halten den Körper rundum; jede Nadel hat **genau eine
  Kontaktfläche** zu ihrer Messstelle.
- Jede der sechs Messnadeln hat ihren **eigenen Bezug** zu genau einer der sechs Messschnittstellen.
- Der jeweilige Prototyp arbeitet im Inneren.
- Keine Einzelauflagemessung mehr, sondern **Rundum-Messung: Vollmodellmessung.**
- Kinematische Lagerung und Einspannung bleiben beide als **anwendungsabhängige Möglichkeiten** offen; die
  Ausarbeitung dokumentiert sie, eine Bauentscheidung steht derzeit nicht an.

Die Idee eines Nadelrahmens ist älter. Eine Arbeitsfassung des Formelwerks vom Juni 2026 (§5–§6, Quelle außerhalb des
Repositorys) führt ein Nadel-Messmodell (jede Nadel misst eine Kraftkomponente längs ihrer Achse; Kraft und Moment
als Summen) und einen vorläufigen Aufbau mit Nadeln auf ±x, ±y, ±z, dort zusammen mit Ballons als Medienkontakt
(Linie B). Den Rahmen mit sechs Interfaces, den Lastvektor mit freien Kontaktmomenten und die Ebenen L0–L3 beschreibt
das Formelverzeichnis v2.7, Abschnitt „Mehrpunkt-, Mehrinterface- und Mehrkanalmessung“
([`../formelverzeichnis/`](../formelverzeichnis/README.md)). Neu sind die Einbettung des Dreimassenkörpers, die Nadeln
mit Fixierstelle und eigener Schnittstelle und die Vollmodellmessung.

| Herkunft | Inhalt | Ort |
|---|---|---|
| frühere Quellen | Festhaltung des Autors (11.10.2026); Arbeitsfassung des Formelwerks (Juni 2026, außerhalb des Repositorys); Formelverzeichnis v2.7 (Lastvektor, freie Kontaktmomente, L0–L3, H_cal); Prüfgruppe kippmoment (KM-03, KM-05, KM-10); V1-Kandidat aus `code/auslegung.py` | Abschnitt 1, Verweise im Text |
| neue Herleitungen (11.10.2026) | Begriffe und Lastbilanz, Nadelregel, Rang und Nullraum, Formschluss im Modell, Vollmodell, Rahmendynamik, Kalibrierrang | Abschnitte 2–9; Rechnungen NR-01 bis NR-09 |
| angenommene Parameter | Geometrie, Massen, Trägheit, Steifigkeiten, Dämpfung, Reibung, Bandbreite | Abschnitt 5, Tabelle der Annahmen |
| offene Punkte | Halterung, Bauteile, Kalibrierlasten, Rahmenstruktur; Modellgrenzen | Abschnitt 10 |

## 2 Bezeichnungen, Begriffe und Lastbilanz

Koordinaten rechtshändig: **x nach Ost, y nach Nord, z nach oben.** Bezugspunkt O ist die Rahmenmitte, ortsfest;
Schwerkraft g = −g·e_z.

| j | Nadel | Schnittstelle | Druckrichtung n_j auf den Körper | Querrichtungen t_j1, t_j2 |
|---|---|---|---|---|
| 1 | Nord | bei +y | −e_y | e_z, −e_x |
| 2 | Süd | bei −y | +e_y | e_z, +e_x |
| 3 | Ost | bei +x | −e_x | e_y, −e_z |
| 4 | West | bei −x | +e_x | e_y, +e_z |
| 5 | oben | bei +z | −e_z | e_x, −e_y |
| 6 | unten | bei −z | +e_z | e_x, +e_y |

- **Vorzeichen:** Nadelkraft λ > 0 heißt Druck auf den Körper, λ < 0 Zug.

| Begriff | Bedeutung |
|---|---|
| Fixierstelle | Stelle am Körper, an der eine Nadel befestigt ist. |
| Kraftpfad (Pfad) | Fixierstelle – Nadel – Kontaktfläche – Schnittstelle; jede Nadel ist genau ein Pfad (P01–P06). |
| Messfläche | die eine Kontaktfläche der Nadel an ihrer Schnittstelle; ihre Messebene gehört zur Bilanzgrenze. |
| Angriffspunkt r_j | Punkt, an dem die Pfadkraft in der Bilanz angreift: bei Zweigelenknadel und Druckspitze ein Punkt der Wirkungslinie (etwa die Fixierstelle), bei der dreikomponentigen Nadel die Kugelgelenkmitte an der Schnittstelle. |
| übertragene Komponenten | alles, was ein Pfad tatsächlich überträgt: axiale Kraft, Querkräfte, gegebenenfalls ein freies Kontaktmoment τ^c_j. |
| Sensorkanal | eine skalare Messgröße an einer Schnittstelle mit eigenem Nullpunkt, eigener Kalibrierkennung, Richtung und Zeitbasis; ein Pfad kann mehrere Kanäle haben (drei Kraftkomponenten; zwei Messketten am selben Pfad). |
| Resultierende | die sechs Komponenten F_x, F_y, F_z, M_x, M_y, M_z des Lastvektors um O, aus den Pfadkräften gebildet; sie sind keine Kanäle. |

- **Eigener Bezug je Nadel:** lokales Dreibein (n_j, t_j1, t_j2) mit t_j2 = n_j × t_j1. Nullpunkt (Zustand R0),
  Kalibrierkennung und Zeitverzögerung gehören zu jedem Sensorkanal des Pfads (Abschnitt 9). Die Auswertung führt alle
  Pfade über ihre Angriffspunkte r_j in das gemeinsame System O.
- **Bilanzgrenze:** die Messebenen der sechs Schnittstellen. Zur bilanzierten Masse M gehören Träger (L1), Module
  (L2) und die Teile der Nadeln innerhalb dieser Ebenen. L0 ist der passive Messrahmen mit den Schnittstellen; die
  Nadeln verbinden ihn mit dem Träger. L3 bleibt wie im Formelverzeichnis v2.7 die Kopplung zwischen Träger und
  Modulen. Nadeln, Gelenke und Kontakte heißen hier **Halterung**.
- **Lastbilanz** (Formelverzeichnis v2.7, mit Pfaden statt Interfaces):

      w_O = (F_Σ; τ_O) = Σ_j [ Σ_c G_jc·λ_jc + (0; τ^c_j) ],   G_jc = (e_jc; r_j × e_jc)

  Die Summe über c läuft über jede übertragene Kraftkomponente, e_jc aus {n_j, t_j1, t_j2}; τ^c_j ist das freie
  Kontaktmoment des Pfads j. Gemessen wird nur die Summe über die gemessenen Komponenten, w_mess. Sie ist gleich w_O,
  wenn jeder Pfad nur überträgt, was seine Schnittstelle misst (Nadelregel, Abschnitt 3), und keine weiteren Pfade
  die Bilanzgrenze kreuzen (Kabel, Zuleitungen). Die ausgearbeiteten Ausführungen setzen τ^c_j = 0 voraus (ideale
  Gelenke, Druckspitzen und Kugelgelenke); ungemessene Querkräfte sind in NR-07 bilanziert. Jeder Kanal geht mit
  seiner Richtung und seinem Vorzeichen ein; die Summe der Rohkanalwerte ist nicht automatisch eine Resultierende
  (in B ergibt sie (M_x + M_y + M_z)/A, während F_z = q_unten − q_oben, Abschnitt 4).

## 3 Die Nadelregel

Festgehalten ist: eine Nadel – ein Lastpfad – eine Kontaktfläche – eine Schnittstelle. Daraus folgt

> **Was eine Nadel überträgt, muss ihre Schnittstelle messen.**

Überträgt eine Nadel mehr Komponenten, als ihre Schnittstelle misst – Querkraft über Biegung, Gelenkreibung oder
Haftreibung an der Kontaktfläche, ein Moment über eine flächige Auflage –, entsteht innerhalb derselben Nadel ein
ungemessener Parallelpfad, und w_mess weicht von w_O ab. Gerechnet ist ein Beispiel (NR-07): sechs axial messende
Nadeln, eine je Fläche, versetzt wie Belegung B (Abschnitt 4), mit der ungemessenen Quersteifigkeit κ·k_a in beiden
Querrichtungen. Für kleine κ (bis etwa 10⁻³) fehlen der gemessenen Resultierenden etwa 2κ der Kraft und
κ·(1 + 2(D/A)²) des Kippmoments, mit den Beispielmaßen D = 150 mm und A = 40 mm also ≈ 29κ. Für 10⁻⁴ im Moment müsste
eine Nadel in diesem Beispiel quer rund 3·10⁵-mal weicher sein als axial. Differenztests zwischen Zuständen
(Abschnitt 5.2) zeigen diesen Fehlbetrag nicht, weil er in allen Zuständen derselbe Anteil ist. Sichtbar wird er nur
gegen ein unabhängig bestimmtes M·g (getrennte Wägung der bilanzierten Masse), für Momente und Einzelnadeln gegen eine
unabhängig bekannte Schwerpunktlage und ein zutreffendes G – jeweils bei vollständig erfasster Systemgrenze.

Ausgearbeitet sind zwei Bauweisen, die die Regel erfüllen:

- **Einkomponentige Nadel:** Sie überträgt nur die axiale Kraft (Gelenke an beiden Enden wie ein Zweigelenkstab, oder
  eine reibungsfreie Druckspitze); die Schnittstelle misst diese eine Komponente.
- **Dreikomponentige Nadel:** an der Fixierstelle fest, an der Schnittstelle kugelgelenkig (überträgt kein Moment);
  die Schnittstelle misst alle drei Kraftkomponenten. Angriffspunkt ist die Kugelgelenkmitte.

Ein verklebter, verschraubter oder flächig aufliegender Kontakt überträgt bis zu sechs Komponenten, drei Kräfte und
das Kontaktmoment τ^c_j; dann müsste die Schnittstelle alle sechs messen. Diese Bauweise ist denkbar, hier aber nicht
ausgearbeitet.

## 4 Sechs Nadeln: was geometrisch geht

Die Zahl der übertragenen Komponenten ist Rang plus Nullraum. Rang 6 heißt: alle drei Kräfte und alle drei Momente
sind bestimmbar. Der Nullraum enthält die selbstgleichgewichtigen Nadelzustände – Vorspannung (Einspannen),
Lastumlagerung, Setz- und Temperaturdrift. Gegenüberliegende Nadeln bilden ein Paar. Übertragen die Nadeln nur axial
(A, B), ist die **Differenz** eines Paars die Kraft längs der Achse; in C tragen die Querkomponenten der übrigen Nadeln
mit (NR-06). Die **Summe** ist bei zentralen Wirkungslinien die Vorspannung des Paars, bei versetzten Wirkungslinien
ein Moment (NR-01). Für die versetzte Belegung B (Abschnitt 9):

    F_x = q_West − q_Ost      F_y = q_Süd − q_Nord      F_z = q_unten − q_oben
    M_z = A·(q_Ost + q_West)  M_x = A·(q_Nord + q_Süd)  M_y = A·(q_oben + q_unten)

| Ausgearbeitete Ausführung (sechs Nadeln) | Komponenten | Rang | Nullraum | Vorspannung | Momente | Nulltest je Nadel | Nadel |
|---|---|---|---|---|---|---|---|
| A zentral, axial | 6 | 3 | 3 | ja | nein, Drehungen ungehalten | nein | Druckspitze |
| **B** versetzt, axial | 6 | 6 | 0 | nein | ja | ja (Abschnitt 5.2) | zug- und druckfest |
| **C** zentral, drei Kraftkomponenten | 18 | 6 | 12 | ja | ja | nein (sechs Resultierende) | fixiert, Kugelgelenk |

- **A** misst nur die axialen Anteile der drei Kräfte. Die Momente des Dreimassenkörpers (im Beispiel am
  Triphasik-Punkt 0,23 N·m Kippmoment bei k = 1) fließen über ungemessene Pfade (Querkräfte, Reibung), die auch einen
  Teil der Kräfte tragen (etwa 2κ, NR-07). Für die Vollmodellmessung ist A ungeeignet.
- **B** ist die kinematische, statisch bestimmte Lagerung: Lage und Länge der sechs Nadeln legen den Körper fest;
  Längentoleranzen und Temperatur erzeugen keine Zwangskräfte. Ohne Nullraum gibt es keine Vorspannung, die
  Nadelkräfte folgen allein aus Gewicht und Bewegung. Liegt der Schwerpunkt in O, trägt die Nadel oben die Hälfte des
  Gewichts als Zug und die Nadel unten ebenso viel Druck (Beispielkörper: ∓3,19 N). Beim Beispielkörper wechseln am
  Triphasik-Punkt Nord, Süd und unten das Vorzeichen (NR-02, NR-06); Fixierstelle und Schnittstelle müssen dort Zug
  übertragen. Die Versatzrichtung zählt: Jedes Paar, dessen Nadeln auf derselben Wirkungslinie liegen, kostet ein
  Moment; liegen alle drei Paare so (gleichseitig, Bg), fällt der Rang auf 3 (NR-01).
- **C** ist die Einspannung: Die Vorspannung liegt im Nullraum und ist in der Resultierenden unsichtbar. Mit
  Druckkontakt an der Schnittstelle braucht der Beispielkörper bei k_t/k_a = 0,02 und 0,1 (Phasenlagen T, Z, S,
  starrer Grenzfall) 2,9–6,3 N Vorspannung im Paar oben/unten, mit reibschlüssiger Querkraft (μ_s = 0,2 angenommen)
  5,5–6,3 N. Weichere Querrichtungen verlangen mehr, weil dann ein größerer Anteil des Gewichts axial über oben/unten
  läuft. Mit gefangenem Kugelgelenk ist keine Vorspannung nötig (NR-06). Nulltests gelten für die sechs
  Resultierenden; die zwölf Nullraumgrößen sind Beobachtungsgrößen.

**Formschluss (NR-03).** Untersucht ist das Modell eines starren Körpers mit reibungsfreien Punktkontakten, die nur
längs der Nadelachse drücken (Betrachtung erster Ordnung), und gefragt ist nach vollständiger räumlicher Halterung,
also nach Halt gegen beliebige Lasten. In diesem Modell halten sechs Nadeln den Körper nicht, gleich wie sie liegen:
Dazu müssten ihre Kraftwirkungen den sechsdimensionalen Lastraum positiv aufspannen, und das verlangt mindestens
sieben solcher Nadeln in passender Lage. Rechenbeispiele sind D7 – sieben Druckspitzen in eigener Anordnung (50 mm
Versatz, eine je Fläche und eine zweite unten; nicht die Lagen der Belegung B), Nullraum 1 mit einem einzigen
Vorspannzustand aus lauter Druckkräften – und D12 mit zwei Nadeln je Fläche (zwölf, Nullraum 6). Belegung B mit
einer siebten achsparallelen Nadel schließt nie formschlüssig, weil in G_B⁻¹ jedes Paar nur an einer Kraft und einem
Moment hängt; in einer Stichprobe zufälliger Lagen gelingt der Formschluss mit einer siebten Nadel in 180 von 2000
Fällen. Unter einer vorgegebenen Last (etwa nur dem Gewicht), mit Haftreibung, mit flächigem Kontakt oder mit
Krümmungseffekten (Formschluss höherer Ordnung) gelten andere Bedingungen; sie sind nicht gerechnet. Haftreibung an
Druckspitzen hält den Körper auch mit sechs Nadeln, verletzt aber die Nadelregel, wenn die Schnittstelle nur axial
misst.

**Ausgearbeitete Varianten.** Für die Festhaltung „sechs Nadeln, je eine eigene Schnittstelle“ sind zwei Varianten
ausgearbeitet: **B** (kinematische Lagerung mit zugfesten, einkomponentigen Nadeln) und **C** (Einspannung mit
dreikomponentigen Nadeln und Vorspannung). Beide bleiben als anwendungsabhängige Möglichkeiten offen; eine
Bauentscheidung steht nicht an. Weitere Belegungen sind denkbar, hier aber nicht ausgearbeitet: andere Versatzmuster
(etwa B2, NR-01), geneigte Nadeln, Schnittstellen mit bis zu sechs Komponenten, gemischte Belegungen oder mindestens
sieben Druckspitzen in passender Lage.

## 5 Was der Rahmen am Dreimassenkörper misst

Beispielkörper und Rahmen sind Rechenbeispiele. Alle Werte in diesem und dem nächsten Abschnitt gelten für die
folgenden Annahmen:

| Größe | Annahme | Herkunft |
|---|---|---|
| Körper | V1-Kandidat: 3 × 100 g, Hub 8 mm, Träger 0,35 kg (M = 0,65 kg), 10 Hz, Egg-Profil | `code/auslegung.py` |
| Modullage | G0: 100 mm Radius bei 0°, 120°, 240° in der Höhe von O; senkrecht geführt, Bewegung vorgeschrieben | Annahme |
| Träger | Trägheit isotrop mit ρ₀ = 80 mm; Schwerpunkt des Körpers in O, wo nicht anders angegeben | Annahme |
| Geometrie | Angriffspunkte D = 150 mm von O, Versatz A = 40 mm (B) | Annahme |
| Nadeln | axial k_a = 10⁶ N/m (Vergleich 10⁷ N/m); quer k_t = 2·10⁴ bzw. 10⁵ N/m (C); Nadelmassen vernachlässigt | Annahme |
| Kontakte | Gelenke, Spitzen und Kugelgelenke ideal: reibungsfrei, ohne freie Kontaktmomente (τ^c_j = 0); μ_s = 0,2 nur für den Reibkontakt in C | Annahme |
| Dämpfung | steifigkeitsproportional, ζ = 0,02 an der tiefsten Halterungsmode | Annahme |
| Rahmen | Rahmenstruktur und Fundament starr und ortsfest; keine Kabel oder Zuleitungen über die Bilanzgrenze | Annahme |
| Auswertung | Harmonische bis k = 6 (60 Hz), ganze Perioden | Annahme |

### 5.1 Lastvektor im starren Grenzfall

Im starren Grenzfall – Halterungsmoden weit über den ausgewerteten Harmonischen –, bei erfüllter Nadelregel und ohne
weitere Pfade über die Bilanzgrenze gilt für den gemessenen Lastvektor

    F_Σ(t) = M·g·e_z + Σ_i m_i·s̈_i(t)·e_z
    τ_O(t) = r_cm × M·g·e_z + Σ_i m_i·s̈_i(t)·(R_i × e_z)

mit s̈_i der Beschleunigung von Modul i relativ zum Träger und R_i seiner Lage. Die vertikale Komponente ist dieselbe
Funktion wie N(t) einer starren Auflage, solange diese nicht abhebt. Die Übereinstimmung mit der V1-Auflage gilt nur
für den verglichenen Fall: gleiche vorgeschriebene Modulbewegung, geschlossener Kontakt und passende Dynamik
(starrer Grenzfall beider Aufbauten oder jeweils bekannte Übertragung). Der V1-Kandidat hebt im Modell in keiner
Phasenlage ab (ε = 0,57; synchron F_z,min = 2,73 N); unter diesen Bedingungen liefert der Rahmen dieselbe vertikale
Wellenform wie eine starre Auflage und dazu die übrigen fünf Komponenten. Mit endlicher Steifigkeit treten die
Rahmenübertragung T(k·f) der Halterung (Abschnitt 6) bzw. die Kontaktübertragung H(k·f) der Auflage hinzu; beide sind
eigene Modellbestandteile, ebenso die nicht gerechnete Elastizität von Rahmenstruktur und Fundament. Wo eine Auflage
abheben würde, setzt der Rahmen die lineare Lösung fort, solange jede Nadel in ihrem Kontaktzustand bleibt (B
zugfest, C mit ausreichender Vorspannung oder gefangenem Kugelgelenk); F_z < 0 trägt dann die Nadel oben.

### 5.2 Basislinie: sechs Nulltests statt einem

Voraussetzungen: Bilanzgrenze und M sind festgelegt; außer dem Gewicht laufen alle Lasten auf die bilanzierte Masse
über die sechs Schnittstellen (keine Kabel, Zuleitungen oder sonstigen äußeren Lasten); der Rahmen ist ortsfest;
ausgewertet wird über ganze Perioden der eingeschwungenen Systemantwort (ganze Anregungsperioden genügen nur bei
passender Antwort; Formelverzeichnis v2.7). Dann ist ⟨F_Σ⟩ = M·g·e_z und
⟨τ_O⟩ = r_cm × M·g·e_z = M·g·(y_cm, −x_cm, 0). Bei senkrecht bewegten Modulen ändert sich die waagerechte
Schwerpunktlage nicht, und beides hängt nicht von der Phasenlage ab. Zwischen zwei Zuständen mit gleichen äußeren
Lasten gilt daher Δ⟨w_O⟩ = 0 in allen sechs Komponenten (NR-05). Das ist Spur 1 der Linie A, sechsfach.

Einzelne Kanalmittelwerte brauchen zusätzlich Geometrie- und Lagerungsannahmen. Die Gesamtbilanz allein legt sie im
Allgemeinen nicht fest; eine allgemeine Vorhersage einer phasenabhängigen mittleren Lastumverteilung folgt daraus aber
nicht. In der statisch bestimmten Belegung B legen Impuls- und Drallbilanz über G die Nadelmittel fest: Ohne
Nebenpfade, mit unveränderter Geometrie G, gleichen äußeren Lasten und unverändertem Kontaktzustand gilt
Δ⟨q_j⟩ = 0 für jede Nadel, im linearen Modell für T, Z und S numerisch bestätigt (NR-05); der Absolutwert
⟨q⟩ = G⁻¹·(M·g·e_z; r_cm × M·g·e_z) verlangt bekanntes G, M und r_cm. In C hängen die Nadelmittel zusätzlich vom
inneren Lastzustand im Nullraum ab (Vorspannung und ihre Drift); dort sind nur die sechs Resultierenden Nulltests. Im
Modell ist die Vorspannung vorgegeben; eine Änderung durch Phasensteuerung ist bislang nicht nachgewiesen. Eine
mögliche mittlere Lastumverteilung bleibt eine Modellfrage (Kontaktzustände, Geometrie, Nachgiebigkeit,
Vorspannung), die gegenüber Messketteneffekten zu prüfen wäre.

Differenztests zeigen gleichbleibende Fehlbeträge nicht, etwa den Nebenschluss aus Abschnitt 3; dafür braucht es eine
unabhängige Referenz (M·g aus getrennter Wägung, bekannte Schwerpunktlage). Über Teilfenster weicht das Mittel genau
um den Randterm (P(t₁) − P(t₀))/T_W (b_w im Formelverzeichnis) bzw. (H_O(t₁) − H_O(t₀))/T_W ab, bei 3,37 Perioden
synchroner Phasung um 0,27 N in F_z. Ausgewertet werden deshalb ganze Perioden.

### 5.3 Auswahlregeln am Triphasik-Punkt

| Komponente der Resultierenden | Harmonische bei (0°, 120°, 240°) | Amplituden im Beispiel |
|---|---|---|
| F_z | nur k ≡ 0 (mod 3) | k = 3: 0,664 N; k = 6: 0,124 N |
| M_x, M_y | nur k ≢ 0 (mod 3), umlaufendes Kippmoment | k = 1: 0,233 N·m links umlaufend; k = 2: 0,077 N·m rechts; k = 4, 5: 0,005 / 0,007 N·m |
| F_x, F_y, M_z | keine | zeitlich null (dynamische Nullkomponenten) |

Kraft und Moment ergänzen sich: Was in F_z ausgelöscht ist, steht vollständig im Kippmoment (vgl. KM-03 in
[`../../rechnungen/kippmoment/PROTOKOLL.md`](../../rechnungen/kippmoment/PROTOKOLL.md)). Abseits des
Triphasik-Punkts erscheinen in F_z die Ordnungen 1 und 2 und im Moment eine gegenläufige Komponente (bei φ₂ = 110°:
F_z,1 = 0,27 N, R−₁ = 0,014 N·m). F_x, F_y und M_z sind bei senkrecht geführten Modulen im starren Grenzfall ohne
äußere Nebenpfade in jeder Phasenlage null; das ist eine Modellvorhersage unter diesen Annahmen, kein festgelegter
Nulltest. Ein Signal dort zeigt Querbewegung der Module, Führungsfehler, Kopplung
über die Halterung (Schwerpunkt über O, Abschnitt 6) oder äußere Lasten über die Systemgrenze (Kabel, Zuleitungen).
Welche Sensorkanäle dabei ohne dynamische Last bleiben, hängt von der Belegung ab: im Beispiel in B die Kanäle Ost und
West, in C die axialen Kanäle der vier Seitennadeln (bis auf eine Vorspannung).

### 5.4 Welche Nadel was sieht (Belegung B, Beispielkörper)

| Nadel | trägt | am Triphasik-Punkt (starr, Schwerpunkt in O) |
|---|---|---|
| Ost, West | ∓F_x/2 + M_z/(2A) | lastfrei |
| Nord, Süd | ∓F_y/2 + M_x/(2A) | nur k ≢ 0 (mod 3), ±3,40 N |
| oben | −F_z/2 + M_y/(2A) | beide Klassen, −7,35 … −1,01 N (immer Zug) |
| unten | +F_z/2 + M_y/(2A) | beide Klassen, −0,40 … +5,57 N |

### 5.5 Zeltkurve und Modulzeiger

F_z,min entlang φ₃ = 240° bildet auch im Rahmen das Zelt mit Spitze bei 120° (5,499 N starr, Spannweite 0,563 N über
100°–140°). Es ist hier reine Phasengeometrie der linearen Überlagerung; die Höhe hängt im Modell nur von
Modulkinematik und Rahmenübertragung ab (Belegung B mit k_a = 10⁶ N/m: 5,421 N und 0,5601 N). Zum Vergleich: Der
Kandidat auf seiner Auflage mit K = 1,5·10⁶ N/m ergibt 0,5603 N – ein anderes Modell mit eigener Kontaktübertragung.
Die Nähe der Werte folgt aus den angenommenen Steifigkeiten und zeigt keine Gleichwertigkeit von Rahmen und Auflage.

Aus (F_z, M_x, M_y) folgen je Harmonischer die drei Modulzeiger g_i,k = m_i·a_i,k (Kondition 1,41 in Lage G0),
sofern die Modullagen bekannt sind und die Rahmenübertragung korrigiert ist; Masse und Amplitude eines Moduls trennt
das nicht. Die synthetische Rückrechnung in NR-06 – +1 % Masse und +1° Phase an Modul 2 werden exakt zurückgerechnet –
ist eine Konsistenzprüfung des Modells: starrer Grenzfall, rauschfrei, Geometrie exakt bekannt, dieselbe Geometrie
erzeugt und invertiert die Daten. Rahmenübertragung (Abschnitt 6, B mit 10⁶ N/m: im Moment +0,5 % bei k = 1, +1,9 %
bei k = 2), Rauschen, Kalibrier- und Lagefehler sind nicht enthalten; ein experimenteller Nachweis ist das nicht.

## 6 Rahmendynamik

Rahmendynamik heißt hier: der Körper auf den elastischen Nadeln, Rahmenstruktur und Fundament starr und ortsfest. Die
Nadeln sind die Halterung des Körpers. Er hat darauf sechs Eigenmoden (Halterungsmoden), und deren Lage bestimmt, wie
getreu die Messung die Moduldynamik überträgt (NR-08). Die Elastizität von Rahmenstruktur und Fundament ist nicht
gerechnet und bleibt ein eigener Modellbestandteil (Abschnitt 10). Alle Werte gelten für die Annahmen aus Abschnitt 5.

| Ausführung (Beispielparameter) | Eigenfrequenzen [Hz] |
|---|---|
| B, k_a = 10⁶ N/m | 124 (Drehen um z), 147 (Kippen, 2×), 279 (Verschieben, 3×) |
| B, k_a = 10⁷ N/m | 393, 466 (2×), 883 (3×) |
| C, k_a = 10⁶ N/m, k_t = 2·10⁴ N/m | 93, 110 (2×), 285 (3×) |
| C, k_a = 10⁶ N/m, k_t = 10⁵ N/m | 209, 247 (2×), 306 (3×) |

- Im Beispiel (A = 40 mm) liegen die Dreh- und Kippmoden am tiefsten; bei A = 80 mm liegen die Kippmoden, bei
  A = 120 mm alle drei Drehmoden über den Verschiebungsmoden (NR-08). In B hängen die Drehmoden am Versatz A
  (Drehsteifigkeit 2·k_a·A², Frequenz proportional zu A), in C an der Quersteifigkeit der Nadeln und dem Hebel D; in
  beiden zudem an der angenommenen Trägheit.
- Übertragung in B mit k_a = 10⁶ N/m: Kippkomponenten M_x, M_y +0,5 % bei k = 1, +1,9 % bei k = 2, +20 % bei k = 6;
  Kraftkomponenten +0,1 %, +0,5 %, +4,8 %; M_z bei k = 6 +30 % (bei senkrechter Modulführung nicht angeregt). Mit
  10⁷ N/m im Kippen +0,05 %, +0,18 %, +1,7 %.
- Ohne Korrektur verlangt eine Abweichung von höchstens 1 % bis zur sechsten Harmonischen bei 10 Hz nach der
  Einmassenschwinger-Näherung |T − 1| ≈ (k·f/f₁)² eine tiefste Mode ab etwa 600 Hz (0,1 %: ab etwa 1,9 kHz). Die
  Werte folgen aus der gewählten Toleranz, der ausgewerteten Bandbreite (k_max = 6 bei 10 Hz) und der Näherung; sie
  sind keine Bauvorgabe. Sonst wird die Übertragung des Gesamtaufbaus dynamisch kalibriert (H_cal(f) mit einem
  Anregungssatz vom Rang 6, Abschnitt 8).
- Liegt der Schwerpunkt über O, koppelt das Kippen an waagerechte Beschleunigungen. Gerechnet ist eine
  Schwerpunkthöhe von 16,2 mm (Trägerschwerpunkt 30 mm über O): Am Triphasik-Punkt entstehen in F_x und F_y 3–4 mN
  (k = 1, 2; k_a = 10⁶ N/m) bzw. 0,3–0,4 mN (10⁷ N/m). F_x und F_y sind dann keine Nullkomponenten mehr; die Kopplung
  läuft über die Halterung, nicht über L3.

## 7 Was sich gegenüber der Einzelauflage ändert

| Größe | Einzelauflage (V1, einseitiger Kontakt) | Nadelrahmen (Rundum-Messung, Modell) |
|---|---|---|
| Kontakt | einseitig, kann öffnen | gehalten; öffnet eine Nadel, verlässt der Rahmen seinen Gültigkeitsbereich |
| vertikale Wellenform | N(t) über die Kontaktübertragung H(k·f), bei Abheben nichtlinear | F_z(t) linear über die Rahmenübertragung T(k·f), solange jede Nadel ihren Kontaktzustand hält; starr M·g + Σ m_i s̈_i |
| F_min − Mittel, Zeltkurve | kontaktabhängig | aus Modulkinematik und Rahmenübertragung; beim V1-Kandidaten im verglichenen Fall (Abschnitt 5.1) dieselbe Wellenform |
| Liftoff-Anteil λ | explorativ | entfällt, solange jede Nadel ihren Kontaktzustand hält |
| Superposition der Einzelmodule (H1) | prüft die Linearität der Kette einschließlich Kontakt | prüft die Linearität von Nadeln, Gelenken und Antrieb |
| Momente | mit drei Zellen M_x, M_y (E3) | alle drei, aus den Pfadkräften über G |
| Nulltests (Spur 1) | ⟨N⟩ = M·g | sechs Resultierende; in B zusätzlich sechs Nadelmittel (Voraussetzungen Abschnitt 5.2) |
| dynamische Nullkomponenten | – | F_x, F_y, M_z der Resultierenden; lastfreie Kanäle je nach Belegung (B: Ost, West) |
| Gegenstand | Kontaktdynamik der einseitigen Auflage | Moduldyname in allen sechs Komponenten, übertragen über die Halterung |

Im starren Grenzfall oder mit kalibrierter Rahmenübertragung und ohne ungemessene Nebenpfade (Abschnitt 3) erfasst
die Rundum-Messung alle sechs Komponenten der Anregung. An die Stelle des einseitigen Kontaktmodells tritt das Modell
der Halterung (Nadeln, Gelenke, Kontaktzustand, Rahmenübertragung T(k·f), Abschnitt 6). Die einseitige
Kontaktphysik – Abheben, Hüpfzustände – schließt sie aus, solange jede Nadel in ihrem Kontaktzustand bleibt; an die
Stelle der Kontaktresonanz treten die Halterungsmoden. Soll die einseitige Kontaktphysik weiter untersucht werden,
wäre das eine Modellvariante im Rahmen, zum Beispiel eine einseitig nachgiebige Nadel unten mit den übrigen Nadeln
als Führung; messtechnisch ist das wieder eine Auflagemessung mit seitlicher Führung. Ob und wie die V1-Planung davon
berührt wird, entscheidet der Autor; dieses Konzept ändert sie nicht.

## 8 Zustände, Tara und Kalibrierung

| Zustand | Inhalt | Prüfung |
|---|---|---|
| R0 | Rahmen und Nadeln ohne Prüfling | Nullpunkt jedes Sensorkanals (eigener Bezug) |
| R1 | Prüfling eingesetzt, in Ruhe | B: q = G⁻¹·(M·g·e_z; r_cm × M·g·e_z), bei bekanntem G eine Wägung von M und der waagerechten Schwerpunktlage (x_cm, y_cm); z_cm geht in einer Rahmenlage nicht ein. C: dazu die Vorspannung, sichtbar nur in den Nadelwerten |
| R2a, R2b | Betrieb in zwei Phasenlagen | Δ⟨w_O⟩ = 0 in sechs Komponenten; in B Δ⟨q_j⟩ = 0 je Nadel (Voraussetzungen Abschnitt 5.2) |

Den Übergang R0 → R1 aufzeichnen, nicht nullen. Kalibriert wird G (bzw. H_cal) mit bekannten Lasten; jede statische
Last ist eine Kraft F mit Angriffspunkt r und hat den Lastvektor (F; r × F) um O. Maßgeblich ist der Rang des
tatsächlichen Lastsatzes, nicht die Zahl der Rahmenlagen (NR-09, Rechenbeispiele):

- Gewichtsstücke in einer Rahmenlage regen nur F_z, M_x und M_y an (höchstens Rang 3).
- Weitere Rahmenlagen ergänzen F_x, F_y und M_z nur bei linear unabhängigen Schwerkraftrichtungen und mindestens drei
  Lastpunkten, die nicht auf einer Geraden liegen. Drei Lagen durch Drehen um eine waagerechte Achse (koplanare
  Schwerkraftrichtungen) oder Lastpunkte auf einer Geraden ergeben höchstens Rang 5. Drei beliebige Rahmenlagen
  garantieren also keine vollständige Kalibrierung.
- Waagerechte Lasten über Umlenkrollen: Je ein Zug in x und y lässt M_z mit F_x, F_y gekoppelt (höchstens Rang 5);
  erst ein zweiter Zug mit anderer Wirkungslinie gibt im Beispiel Rang 6.
- Das Eigengewicht des Prüflings ist eine einzige Last am Schwerpunkt: In beliebig vielen Rahmenlagen hat es höchstens
  Rang 3. Als Prüflast taugt es nur bei unabhängig bekanntem M und r_cm, denn R1 setzt G voraus. Für Rang 6 braucht es
  Lasten an mindestens zwei weiteren Punkten, die mit dem Schwerpunkt nicht auf einer Geraden liegen, in Lagen mit
  linear unabhängigen Schwerkraftrichtungen.

Vor einer Kalibrierung ist der Rang des geplanten Lastsatzes nachzurechnen (Vorgehen wie in `n5_kalibrierrang.py`).
Für die dynamische Kalibrierung H_cal(f) gilt dieselbe Bedingung: ein Anregungssatz vom Rang 6, also mehrere Orte, die
nicht auf einer Geraden liegen, und mehrere Richtungen. Anregung nur in der Mitte lässt die Kippmoden unangeregt
(KM-05).

## 9 Kanalplan (Vorlage mit Beispielgeometrie)

Pfade der Belegung B (Beispielmaße D = 150 mm, A = 40 mm, zyklisch gegensinnig versetzt; die Fixierstelle liegt auf
der Wirkungslinie und dient als Angriffspunkt):

| Pfad | Nadel | Fixierstelle r [mm] | Druckrichtung n | Zug/Druck | übertragen / gemessen |
|---|---|---|---|---|---|
| P01 | Nord | (0, 150, 40) | −e_y | beides | 1 / 1 |
| P02 | Süd | (0, −150, −40) | +e_y | beides | 1 / 1 |
| P03 | Ost | (150, 40, 0) | −e_x | beides | 1 / 1 |
| P04 | West | (−150, −40, 0) | +e_x | beides | 1 / 1 |
| P05 | oben | (40, 0, 150) | −e_z | beides | 1 / 1 |
| P06 | unten | (−40, 0, −150) | +e_z | beides | 1 / 1 |

Belegung C: Kugelgelenkmitten (Angriffspunkte r_j) in den Flächenmitten, 150 mm von O in Achsrichtung; die
Fixierstelle am Körper liegt um die Nadellänge weiter innen. Je Pfad drei Kraftkomponenten (n_j, t_j1, t_j2),
zusammen 18 Größen. Offen bleiben die Kanäle (Bauart, Band, Rolle, Tara, Kalibrierkennung, Verzögerung). Zwei
Messketten am selben Pfad, etwa DMS und Piezo, sind zwei Beobachter derselben Kraft und werden nicht addiert; die
Resultierende wird nur über Pfade gebildet. Die Rechnungen in
[`../../rechnungen/nadelrahmen/`](../../rechnungen/nadelrahmen/PROTOKOLL.md) nehmen eigene Geometrien und
Modellvarianten über die Parameter von `nr_modell.py` auf.

## 10 Offene Punkte und Modellgrenzen

Keine der folgenden Fragen steht derzeit zur Entscheidung an; die Liste hält fest, was eine Anwendung festlegen müsste.

- Halterung: Kinematische Lagerung (ausgearbeitet als B) und Einspannung (ausgearbeitet als C) bleiben als
  anwendungsabhängige Möglichkeiten offen; eine Bauentscheidung steht nicht an. Weitere Belegungen, etwa mit
  mindestens sieben Druckspitzen in passender Lage (NR-03), sind denkbar.
- Fixierstellen am Körper: Lage, Versatz A (Hebel für Momente und Drehmoden in B), Zuordnung der Versatzrichtungen.
- Nadel: Gelenkart, Quersteifigkeit (Ziel für κ nach Abschnitt 3), Kontaktmomente, Zugfestigkeit, Masse,
  Kontaktfläche zur Schnittstelle.
- Schnittstellen: Komponentenzahl (ausgearbeitet: eine oder drei; bei festem oder flächigem Kontakt bis zu sechs,
  Abschnitt 3), Sensorprinzip, Band, Nennlast (Gewicht, Vorspannung, Dynamik).
- Rahmenstruktur und Fundament: Steifigkeit und Eigenmoden (nicht gerechnet); Kabel und Zuleitungen des Prototyps als
  Parallelpfade (über eine Nadel führen oder gesondert charakterisieren).
- Kalibrierung: statischer Lastsatz und dynamischer Anregungssatz mit nachgerechnetem Rang 6 (Abschnitt 8);
  unabhängige Referenz für M·g und r_cm.
- Prototyp: Modellvariante, Lage im Rahmen (r_cm), Modulgeometrie.
- Auswertegrößen im Rahmen; die Präregistrierung v2 und die V1-Planung sind davon nicht berührt.

**Modellgrenzen** (Einzelheiten im Rechenprotokoll unter „Grenzen“): starrer Körper, kleine Bewegung, linear;
Kontaktöffnen, Mikroschlupf und Hysterese nicht modelliert; ideale Kontakte ohne freie Kontaktmomente; Nadelmassen,
Nadel-Eigenmoden und geometrische Steifigkeit vernachlässigt; Rahmenstruktur und Fundament starr; Module senkrecht
geführt, Bewegung vorgeschrieben (keine Antriebsrückwirkung); keine Kabel oder Zuleitungen; nur der V1-Kandidat als
Prototyp; Kalibrierlasten nur als Rechenbeispiele. Die Gegenprüfung bestätigt die Rechnung innerhalb dieses Modells;
Messdaten gibt es nicht.
