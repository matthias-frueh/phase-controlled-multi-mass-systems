# Sechs-Nadel-Messrahmen · Dreimassenkörper in der Rundum-Messung (Vollmodell)

> **Vermerk (11.10.2026).** Konzept, ausgearbeitet am 11.10.2026 nach der Festhaltung des Autors vom selben Tag
> (Abschnitt 1). Nicht umgesetzt, nicht an Hardware geprüft; es gibt keine Messdaten. Alle Zahlen sind Simulation
> oder Analytik mit angenommenen Maßen, Steifigkeiten und Trägheiten (Rechenbeispiele, keine Bauvorgabe). Rechnungen,
> Gegenprüfung und Grenzen stehen in [`../../rechnungen/nadelrahmen/PROTOKOLL.md`](../../rechnungen/nadelrahmen/PROTOKOLL.md)
> (Befunde NR-01 bis NR-08). Das Konzept gehört zum Arbeitspaket AP-27 (räumliche Last) und ändert weder die
> [Präregistrierung v2](../praeregistrierung_v2_entwurf.md) noch die V1-Planung. Die Wahl zwischen Einspannen und
> kinematischer Lagerung bleibt offen (Festhaltung des Autors vom 11.10.2026); beide Ausführungen stehen hier
> nebeneinander.

*Matthias Früh · Oktober 2026 · prä-experimentell*

## 1 Festhaltung

Vom Autor am 11.10.2026 festgehalten:

- Der Dreimassenkörper – oder eine Modellvariante – wird in einen Rahmen mit sechs Messpunkten eingebettet:
  **Nord, Süd, Ost, West, oben, unten.**
- Am Körper liegen **Fixierstellen**. Nadelsysteme halten den Körper rundum; jede Nadel hat **genau eine
  Kontaktfläche** zu ihrer Messstelle.
- Jede der sechs Messnadeln hat ihren **eigenen Bezug** zu genau einer der sechs Messschnittstellen.
- Der jeweilige Prototyp arbeitet im Inneren.
- Keine Einzelauflagemessung mehr, sondern **Rundum-Messung: Vollmodellmessung.**

Die Idee eines Nadelrahmens ist älter. Eine Arbeitsfassung des Formelwerks vom Juni 2026 (§5–§6, Quelle außerhalb des
Repositorys) führt ein Nadel-Messmodell (jede Nadel misst eine Kraftkomponente längs ihrer Achse; Kraft und Moment
als Summen) und einen vorläufigen Aufbau mit Nadeln auf ±x, ±y, ±z, dort zusammen mit Ballons als Medienkontakt
(Linie B). Den Rahmen mit sechs Interfaces und die Ebenen L0–L3 beschreibt das Formelverzeichnis v2.7, Abschnitt
„Mehrpunkt-, Mehrinterface- und Mehrkanalmessung“ ([`../formelverzeichnis/`](../formelverzeichnis/README.md)). Neu
sind die Einbettung des Dreimassenkörpers, die Nadeln mit Fixierstelle und eigener Schnittstelle und die
Vollmodellmessung. Die Abschnitte 3 bis 9 sind am 11.10.2026 neu ausgearbeitet.

## 2 Bezeichnungen

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
- **Eigener Bezug je Nadel:** lokales Dreibein (n_j, t_j1, t_j2) mit t_j2 = n_j × t_j1, eigener Nullpunkt
  (Zustand R0), eigene Kalibrierkennung und Zeitverzögerung. Die Auswertung führt alle Nadeln über ihre Lage r_j in
  das gemeinsame System O.
- **Bilanzgrenze:** die Messebenen der sechs Schnittstellen. Zur bilanzierten Masse M gehören Träger (L1), Module
  (L2) und die Teile der Nadeln innerhalb dieser Ebenen; L0 ist der Rahmen mit den Schnittstellen, L3 die reale
  Kopplung, hier das elastische System aus Nadeln und Träger.
- **Messgleichung:** Lastvektor w_O = (F_Σ; τ_O) = Σ_j Σ_c G_jc·λ_jc mit G_jc = (e_jc; r_j × e_jc), e_jc aus
  {n_j, t_j1, t_j2}, je nachdem, welche Komponenten die Nadel überträgt.

## 3 Die Nadelregel

Festgehalten ist: eine Nadel – ein Lastpfad – eine Kontaktfläche – eine Schnittstelle. Daraus folgt

> **Was eine Nadel überträgt, muss ihre Schnittstelle messen.**

Überträgt eine Nadel mehr Komponenten, als ihre Schnittstelle misst – Querkraft über Biegung, Gelenkreibung oder
Haftreibung an der Kontaktfläche, ein Moment über eine flächige Auflage –, entsteht innerhalb derselben Nadel ein
ungemessener Parallelpfad. Bei axial messenden Nadeln mit der Quersteifigkeit κ·k_a fehlen der gemessenen
Resultierenden etwa 2κ der Kraft und κ·(1 + 2(D/A)²) ≈ 29κ des Kippmoments (Beispielmaße, NR-07). Für 10⁻⁴ im Moment
muss eine Nadel quer also rund 3·10⁵-mal weicher sein als axial. Der Nulltest ⟨F_z⟩ = M·g zeigt diesen Fehlbetrag
direkt an.

Zwei Bauweisen erfüllen die Regel:

- **Einkomponentige Nadel:** Sie überträgt nur die axiale Kraft (Gelenke an beiden Enden wie ein Zweigelenkstab, oder
  eine reibungsfreie Druckspitze); die Schnittstelle misst diese eine Komponente.
- **Dreikomponentige Nadel:** an der Fixierstelle fest, an der Schnittstelle kugelgelenkig (überträgt kein Moment);
  die Schnittstelle misst alle drei Kraftkomponenten.

Ein verklebter, verschraubter oder flächig aufliegender Kontakt überträgt bis zu sechs Komponenten; dann müsste die
Schnittstelle sechs messen.

## 4 Sechs Nadeln: was geometrisch geht

Die Zahl der übertragenen Komponenten ist Rang plus Nullraum. Rang 6 heißt: alle drei Kräfte und alle drei Momente
sind bestimmbar. Der Nullraum enthält die selbstgleichgewichtigen Nadelzustände – Vorspannung (Einspannen),
Lastumlagerung, Setz- und Temperaturdrift. Gegenüberliegende Nadeln bilden ein Paar. Ihre **Differenz** ist immer die
Kraft längs der Achse. Ihre **Summe** ist bei zentralen Wirkungslinien die Vorspannung des Paars, bei versetzten
Wirkungslinien ein Moment (NR-01). Für die versetzte Belegung B (Abschnitt 9):

    F_x = q_West − q_Ost      F_y = q_Süd − q_Nord      F_z = q_unten − q_oben
    M_z = A·(q_Ost + q_West)  M_x = A·(q_Nord + q_Süd)  M_y = A·(q_oben + q_unten)

| Ausführung mit sechs Nadeln | Komponenten | Rang | Nullraum | Vorspannung | Momente | Nulltest je Nadel | Nadel |
|---|---|---|---|---|---|---|---|
| A zentral, axial | 6 | 3 | 3 | ja | nein, Drehungen ungehalten | nein | Druckspitze |
| **B** versetzt, axial | 6 | 6 | 0 | nein | ja | ja | zug- und druckfest |
| **C** zentral, drei Kraftkomponenten | 18 | 6 | 12 | ja | ja | nein (sechs Resultierende) | fixiert, Kugelgelenk |

- **A** misst nur die drei Kräfte. Die Momente des Dreimassenkörpers (Kippmoment 0,23 N·m bei k = 1) fließen über
  ungemessene Pfade (Querkräfte, Reibung). Für die Vollmodellmessung ist A ungeeignet.
- **B** ist die kinematische, statisch bestimmte Lagerung: Lage und Länge der sechs Nadeln legen den Körper fest;
  Längentoleranzen und Temperatur erzeugen keine Zwangskräfte. Ohne Nullraum gibt es keine Vorspannung, die
  Nadelkräfte folgen allein aus Gewicht und Bewegung. Liegt der Schwerpunkt in O, trägt die Nadel oben die Hälfte des
  Gewichts als Zug (−3,19 N), die Nadel unten +3,19 N; am Triphasik-Punkt wechseln Nord, Süd und unten das Vorzeichen
  (NR-02, NR-06). Fixierstelle und Schnittstelle müssen deshalb Zug übertragen. Die Versatzrichtung zählt: Liegen
  beide Nadeln eines Paars auf derselben Wirkungslinie, fällt der Rang auf 3.
- **C** ist die Einspannung: Die Vorspannung liegt im Nullraum und ist in der Resultierenden unsichtbar. Mit
  Druckkontakt an der Schnittstelle braucht der Beispielkörper je nach Phasenlage und Quersteifigkeit 2,9–6,3 N
  Vorspannung im Paar oben/unten, mit reibschlüssiger Querkraft (μ_s = 0,2 angenommen) 5,5–6,3 N; mit gefangenem
  Kugelgelenk keine (NR-06). Nulltests gelten für die sechs Resultierenden; die zwölf Nullraumgrößen sind
  Beobachtungsgrößen.

**Formschluss (NR-03).** Sechs Nadeln, die nur drücken können, halten keinen Körper fest – gleich wie sie liegen.
Dazu müssten ihre Kraftwirkungen den sechsdimensionalen Lastraum positiv aufspannen, und das verlangt mindestens
sieben. Beispiel: die sechs versetzten Nadeln und eine zweite Nadel unten (Nullraum 1, einziger Vorspannzustand mit
lauter Druckkräften); üblich sind zwei Nadeln je Fläche (zwölf, Nullraum 6). Haftreibung an Druckspitzen hält den
Körper auch mit sechs Nadeln, verletzt dann aber die Nadelregel, wenn die Schnittstelle nur axial misst.

Für die Festhaltung „sechs Nadeln, je eine eigene Schnittstelle“ bleiben damit genau zwei Wege, und sie entsprechen
der offenen Variantenwahl: **B** (kinematische Lagerung) oder **C** (Einspannung). Wer mit einkomponentigen
Druckspitzen einspannen will, braucht eine siebte Nadel.

## 5 Was der Rahmen am Dreimassenkörper misst

Beispielkörper: der V1-Kandidat der Auslegung (3 × 100 g, Hub 8 mm, Träger 0,35 kg, 10 Hz, Egg-Profil), Module auf
100 mm Radius bei 0°, 120°, 240° (Lage G0), Fixierstellen 150 mm von O, Versatz 40 mm. Lage, Trägheit und Maße sind
Annahmen.

### 5.1 Messgleichung

Im starren Grenzfall – Rahmenmoden weit über den ausgewerteten Harmonischen – gilt für den gemessenen Lastvektor

    F_Σ(t) = M·g·e_z + Σ_i m_i·s̈_i(t)·e_z
    τ_O(t) = r_cm × M·g·e_z + Σ_i m_i·s̈_i(t)·(R_i × e_z)

mit s̈_i der Beschleunigung von Modul i relativ zum Träger und R_i seiner Lage. Die vertikale Komponente ist dieselbe
Funktion wie N(t) einer starren Auflage, solange diese nicht abhebt. Der V1-Kandidat hebt in keiner Phasenlage ab
(ε = 0,57; synchron F_z,min = 2,73 N): Der Rahmen misst dort dieselbe vertikale Wellenform wie eine Auflage und dazu
die übrigen fünf Komponenten. Wo eine Auflage abheben würde, setzt der Rahmen die lineare Lösung fort; F_z < 0 trägt
dann die Nadel oben. Mit endlicher Nadelsteifigkeit tritt die Rahmenübertragung T(k·f) hinzu (Abschnitt 6).

### 5.2 Basislinie: sechs Nulltests statt einem

Über ganze Perioden im eingeschwungenen Zustand ist ⟨F_Σ⟩ = M·g·e_z und ⟨τ_O⟩ = r_cm × M·g·e_z = M·g·(y_cm, −x_cm, 0).
Bei senkrecht bewegten Modulen hängt beides nicht von der Phasenlage ab. Zwischen zwei Zuständen gilt daher
Δ⟨w_O⟩ = 0 in allen sechs Komponenten, in Belegung B zusätzlich Δ⟨q_j⟩ = 0 für jede Nadel (NR-05). Das ist Spur 1 der
Linie A, sechsfach. Über Teilfenster weicht das Mittel genau um den Randterm (P(t₁) − P(t₀))/T_W bzw.
(H_O(t₁) − H_O(t₀))/T_W ab, bei 3,37 Perioden synchroner Phasung um 0,27 N in F_z. Ausgewertet werden deshalb ganze
Perioden.

### 5.3 Auswahlregeln am Triphasik-Punkt

| Komponente | Harmonische bei (0°, 120°, 240°) | Amplituden im Beispiel |
|---|---|---|
| F_z | nur k ≡ 0 (mod 3) | k = 3: 0,664 N; k = 6: 0,124 N |
| M_x, M_y | nur k ≢ 0 (mod 3), umlaufendes Kippmoment | k = 1: 0,234 N·m links umlaufend; k = 2: 0,077 N·m rechts; k = 4, 5: 0,005 / 0,007 N·m |
| F_x, F_y, M_z | keine | zeitlich null (dynamische Nullkanäle) |

Kraft und Moment ergänzen sich: Was in F_z ausgelöscht ist, steht vollständig im Kippmoment (vgl. KM-03 in
[`../../rechnungen/kippmoment/PROTOKOLL.md`](../../rechnungen/kippmoment/PROTOKOLL.md)). Abseits des
Triphasik-Punkts erscheinen in F_z die Ordnungen 1 und 2 und im Moment eine gegenläufige Komponente (bei φ₂ = 110°:
F_z,1 = 0,27 N, R−₁ = 0,014 N·m). F_x, F_y und M_z sind bei senkrecht geführten Modulen im starren Grenzfall in jeder
Phasenlage null. Ein Signal dort zeigt Querbewegung der Module, Führungsfehler oder Rahmenkopplung.

### 5.4 Welche Nadel was sieht (Belegung B)

| Nadel | trägt | am Triphasik-Punkt (starr) |
|---|---|---|
| Ost, West | ∓F_x/2 + M_z/(2A) | lastfrei: Nullkanäle |
| Nord, Süd | ∓F_y/2 + M_x/(2A) | nur k ≢ 0 (mod 3), ±3,40 N |
| oben | −F_z/2 + M_y/(2A) | beide Klassen, −7,35 … −1,01 N (immer Zug) |
| unten | +F_z/2 + M_y/(2A) | beide Klassen, −0,40 … +5,57 N |

### 5.5 Zeltkurve und Modulzeiger

F_z,min entlang φ₃ = 240° bildet auch im Rahmen das Zelt mit Spitze bei 120° (5,499 N starr, Spannweite 0,563 N über
100°–140°). Es ist hier reine Phasengeometrie der linearen Überlagerung; die Höhe hängt nur von Modulkinematik und
Rahmenübertragung ab (Belegung B mit k_a = 10⁶ N/m: 5,421 N und 0,560 N; der Kandidat auf seiner Auflage: 0,560 N).
Aus (F_z, M_x, M_y) folgen je Harmonischer die drei Modulzeiger (Kondition 1,41): Amplitude und Phase jedes Moduls in
jedem Lauf. Eine Abweichung von +1 % Masse und +1° Phase an Modul 2 wird exakt zurückgerechnet (NR-06).

## 6 Rahmendynamik

Die Nadeln sind der Kontakt des Rahmens. Sie halten den Körper mit sechs Eigenmoden, und deren Lage bestimmt, wie
getreu der Rahmen die Moduldynamik überträgt (NR-08):

| Ausführung (Beispiel) | Eigenfrequenzen [Hz] |
|---|---|
| B, k_a = 10⁶ N/m | 124 (Drehen um z), 147 (Kippen, 2×), 279 (Verschieben, 3×) |
| B, k_a = 10⁷ N/m | 393, 466 (2×), 883 (3×) |
| C, k_a = 10⁶ N/m, k_t = 2·10⁴ N/m | 93, 110 (2×), 285 (3×) |
| C, k_a = 10⁶ N/m, k_t = 10⁵ N/m | 209, 247 (2×), 306 (3×) |

- Die Dreh- und Kippmoden liegen am tiefsten. In B hängen sie am Versatz A (Drehsteifigkeit 2·k_a·A², Frequenz
  proportional zu A), in C an der Quersteifigkeit der Nadeln.
- Übertragung in B mit k_a = 10⁶ N/m: Kippkanäle +0,5 % bei k = 1, +1,9 % bei k = 2, +20 % bei k = 6; Kraftkanäle
  +0,1 %, +0,5 %, +4,8 %. Mit 10⁷ N/m im Kippkanal +0,05 %, +0,18 %, +1,7 %.
- Ohne Korrektur verlangt eine Abweichung von höchstens 1 % bis zur sechsten Harmonischen bei 10 Hz eine tiefste Mode
  ab 600 Hz (0,1 %: ab 1,9 kHz). Sonst wird die Übertragung des Gesamtaufbaus dynamisch kalibriert (H_cal(f), mit
  Anregung an mehreren Orten, damit die Kippmoden sichtbar werden).
- Liegt der Schwerpunkt nicht in O, koppelt das Kippen an waagerechte Beschleunigungen: Bei 16 mm Schwerpunkthöhe
  entstehen in F_x und F_y 3–4 mN (k_a = 10⁶ N/m) bzw. 0,3–0,4 mN (10⁷ N/m). Diese Kanäle sind dann Rahmenkanäle (L3).

## 7 Was sich gegenüber der Einzelauflage ändert

| Größe | Einzelauflage (V1, einseitiger Kontakt) | Nadelrahmen (Rundum-Messung) |
|---|---|---|
| Kontakt | einseitig, kann öffnen | gehalten; öffnet eine Nadel, verlässt der Rahmen seinen Gültigkeitsbereich |
| vertikale Wellenform | N(t) über die Kontaktübertragung H(k·f), bei Abheben nichtlinear | F_z(t) linear über die Rahmenübertragung; starr M·g + Σ m_i s̈_i |
| F_min − Mittel, Zeltkurve | kontaktabhängig | aus Modulkinematik und Rahmenübertragung; beim V1-Kandidaten starr dieselbe Wellenform |
| Liftoff-Anteil λ | explorativ | entfällt (null per Konstruktion) |
| Superposition der Einzelmodule (H1) | prüft die Linearität der Kette einschließlich Kontakt | prüft die Linearität von Nadeln, Gelenken und Antrieb |
| Momente | mit drei Zellen M_x, M_y (E3) | alle drei, direkt |
| Nulltests (Spur 1) | ⟨N⟩ = M·g | sechs Resultierende; in B zusätzlich sechs Nadelmittel |
| dynamische Nullkanäle | – | F_x, F_y, M_z |
| Gegenstand | Kontaktdynamik der einseitigen Auflage | vollständige Moduldyname, Träger- und Rahmenkopplung (L3) |

Die Rundum-Messung erfasst die Anregung vollständig und ohne Kontaktmodell. Die einseitige Kontaktphysik – Abheben,
Hüpfzustände, Kontaktresonanz – schließt sie konstruktiv aus. Soll diese weiter untersucht werden, wäre das eine
Modellvariante im Rahmen, zum Beispiel eine einseitig nachgiebige Nadel unten mit den übrigen Nadeln als Führung;
messtechnisch ist das wieder eine Auflagemessung mit seitlicher Führung. Ob und wie die V1-Planung davon berührt wird,
entscheidet der Autor; dieses Konzept ändert sie nicht.

## 8 Zustände, Tara und Kalibrierung

| Zustand | Inhalt | Prüfung |
|---|---|---|
| R0 | Rahmen und Nadeln ohne Prüfling | Nullpunkt jeder Nadel (eigener Bezug) |
| R1 | Prüfling eingesetzt, in Ruhe | B: q = G⁻¹·(M·g·e_z; r_cm × M·g·e_z) ist eine Wägung von M und r_cm. C: dazu die Vorspannung, sichtbar nur in den Nadelwerten |
| R2a, R2b | Betrieb in zwei Phasenlagen | Δ⟨w_O⟩ = 0 in sechs Komponenten; in B Δ⟨q_j⟩ = 0 je Nadel |

Den Übergang R0 → R1 aufzeichnen, nicht nullen. Gewichtsstücke in einer Rahmenlage regen nur F_z, M_x und M_y an
(Rang 3); drei Lagen des ganzen Rahmens oder waagerechte Lasten über eine Umlenkrolle ergänzen F_x, F_y und M_z. Das
Eigengewicht des Prüflings in drei Rahmenlagen ist ein bekannter Lastsatz (M, r_cm) und prüft G. Die dynamische
Kalibrierung braucht Anregung an mehreren Orten, sonst bleiben die Kippmoden unsichtbar.

## 9 Kanalplan (Vorlage mit Beispielgeometrie)

Pfade der Belegung B (Beispielmaße D = 150 mm, A = 40 mm, zyklisch gegensinnig versetzt):

| Pfad | Nadel | Fixierstelle r [mm] | Druckrichtung n | Zug/Druck | übertragen / gemessen |
|---|---|---|---|---|---|
| P01 | Nord | (0, 150, 40) | −e_y | beides | 1 / 1 |
| P02 | Süd | (0, −150, −40) | +e_y | beides | 1 / 1 |
| P03 | Ost | (150, 40, 0) | −e_x | beides | 1 / 1 |
| P04 | West | (−150, −40, 0) | +e_x | beides | 1 / 1 |
| P05 | oben | (40, 0, 150) | −e_z | beides | 1 / 1 |
| P06 | unten | (−40, 0, −150) | +e_z | beides | 1 / 1 |

Belegung C: Fixierstellen in den Flächenmitten (r = 150 mm in Achsrichtung), je Pfad drei Komponenten
(n_j, t_j1, t_j2), zusammen 18 Größen. Offen bleiben die Kanäle (Bauart, Band, Rolle, Tara, Kalibrierkennung,
Verzögerung). Zwei Messketten am selben Pfad, etwa DMS und Piezo, sind zwei Beobachter derselben Kraft und werden
nicht addiert; die Resultierende wird nur über Pfade gebildet. Die Rechnungen in
[`../../rechnungen/nadelrahmen/`](../../rechnungen/nadelrahmen/PROTOKOLL.md) nehmen eigene Geometrien und
Modellvarianten über die Parameter von `nr_modell.py` auf.

## 10 Offene Entscheidungen

- Ausführung B (kinematisch) oder C (eingespannt), oder sieben bis zwölf Druckspitzen – bewusst offen.
- Fixierstellen am Körper: Lage, Versatz A (Hebel für Momente und Kippmoden), Zuordnung der Versatzrichtungen.
- Nadel: Gelenkart, Quersteifigkeit (Ziel für κ nach Abschnitt 3), Zugfestigkeit, Masse, Kontaktfläche zur
  Schnittstelle.
- Schnittstellen: Komponentenzahl (eine oder drei), Sensorprinzip, Band, Nennlast (Gewicht, Vorspannung, Dynamik).
- Rahmen: Steifigkeit und Eigenmoden; Kabel und Zuleitungen des Prototyps als Parallelpfade (über eine Nadel führen
  oder gesondert charakterisieren).
- Prototyp: Modellvariante, Lage im Rahmen (r_cm), Modulgeometrie.
- Auswertegrößen im Rahmen; die Präregistrierung v2 ist davon nicht berührt.
