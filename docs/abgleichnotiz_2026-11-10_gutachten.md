# PCMMS – Abgleichnotiz 2026-11-10: simuliertes Fachgutachten und Gegenprüfung

Projekt: Phasenkontrollierte Mehrmassensysteme (PCMMS)
Autor: Matthias Früh, ORCID 0009-0005-9984-4207
Erstellt: 10.11.2026, Claude Code, nach Auftrag des Autors vom selben Tag; nach Gegenlesen berichtigt am 11.11.2026
Status: Notiz, kein Arbeitsauftrag
Zuordnung: AP-16 (Literaturbestand); berührt die Offenen Punkte Nr. 21 und 42 des Arbeitspapiers
Lizenz: CC BY 4.0 (Ordner docs/, siehe LICENSE-CC-BY-4.0)

> **Vermerk (10.11.2026).** Abgleich am Repository-Stand `51f79a2` (`main`, 03.11.2026, PR #29). Zeilenangaben ohne
> Dateinamen („Z. …“) beziehen sich auf den Quelltext des Arbeitspapiers v2.5,
> [`arbeitspapier/PCMMS_Arbeitspapier_v2_5.tex`](arbeitspapier/PCMMS_Arbeitspapier_v2_5.tex), an diesem Stand; steht
> „dort“ davor, gilt die Angabe für das zuletzt genannte andere Dokument. Auch die Zeilenangaben zu anderen Dateien
> gelten am Stand `51f79a2`. Der Pull Request, der diese Notiz anlegt, fügt vor hier zitierten Stellen Zeilen ein: in
> der [README](../README.md) des Repository-Stamms nach Z. 62 eine, in [`overview.md`](overview.md) nach Z. 39 fünf, in
> den Offenen Punkten des Arbeitspapiers nach Z. 92 eine und nach Z. 101 zwei; spätere Zeilen dieser Dateien stehen
> seither entsprechend tiefer. Seine übrigen Einfügungen liegen hinter den hier zitierten Zeilen und verschieben keine
> davon. Die beiden abgeglichenen Texte (ein simuliertes Fachgutachten und eine Gegenprüfung dazu, keine unabhängige
> Begutachtung) und der Auftrag an Claude Code liegen nicht im Repository. Die Notiz ändert keine Zahl, keine Hypothese,
> keinen Code und keine Daten; Arbeitspapier (Quelltext und PDF) und Literaturverzeichnis bleiben unverändert (Variante
> A des Auftrags, kein Neusatz). Alle Zahlen des Repositorys sind Simulation; Messdaten existieren nicht.

## 0. Zweck und Quellenlage

Dem Autor lagen am 10.11.2026 zwei Texte vor: ein simuliertes Fachgutachten zu PCMMS (revidierte Fassung, Urteil
„Moderate Revision“) und eine Gegenprüfung dazu. Beide beziehen sich wechselseitig aufeinander; sie sind Hinweise, keine
unabhängige Begutachtung und kein Beleg. Diese Notiz hält fest, welche ihrer Aussagen den Repository-Stand treffen, und
ändert weder eine Regel noch einen Plan.

Die Texte selbst sind nicht abgelegt. Ihre Aussagen sind unter den Arbeitskennungen G-1 bis G-8 sinngemäß wiedergegeben
(Abschnitt 1). Grundlage der Wiedergabe ist der Auftrag des Autors vom 10.11.2026; die Texte selbst lagen bei der
Bearbeitung nicht vor. Die Kennungen E-1 bis E-4 in Abschnitt 7 bezeichnen offene Entscheidungen des Autors; sie sind
weder die Eingänge E-1 bis E-4 der [Abgleichnotiz vom 29.10.2026](abgleichnotiz_2026-10-29_v4.md) noch die Kennungen E1
bis E5 der [Präregistrierung v2 (Entwurf)](praeregistrierung_v2_entwurf.md), also die explorativen Punkte E1, E2, E4 und
E5 und die registrierte Kontrolle E3. BA-1 bis BA-5 (Abschnitt 4.2) zählen die Abweichungen zwischen den
Beitragsaussagen, R-1 bis R-5 (Abschnitt 5.2) die vorgeschlagenen Referenzfälle; diese sind nicht die Rückmeldungen R-1
bis R-7 der Abgleichnotiz vom 29.10.2026.

## 1. Abgleich G-1 bis G-8

Jede Zeile ist am Stand `51f79a2` nachgeschlagen. Die Kernforderung beider Texte, einen Abschnitt zu Forschungsstand und
Beitrag in das Arbeitspapier einzufügen, trifft den Stand nicht: Kapitel, Abschnitt, Beitragsaussage in Kurzfassung und
Abstract und der Rechercheanhang sind vorhanden.

| Aussage | Befund | Fundstelle |
|---|---|---|
| **G-1** Im Arbeitspapier fehle ein Abschnitt zu Forschungsstand und Beitrag; der Literaturabgleich liege nur als eigenes Dokument vor. | **Trifft nicht zu.** Das Arbeitspapier v2.5 enthält das Kapitel „Stand der Forschung“ mit acht Abschnitten, darunter „Mehrkörperdynamik und phasengesteuerte Anregung“ und „Einordnung und mögliche Lücke“ mit vier Merkmalen der untersuchten Konstellation, und den Anhang „Dokumentation der Literaturrecherche“ (Anhang C). Richtig ist nur der engere Punkt, dass die Einträge des Literaturabgleichs vom 12.09.2026 nicht ins Arbeitspapier übernommen sind (unten, „Was zutrifft“). | `chap:stand` Z. 700–973, Abschnitte ab Z. 703, 721, 771, 825, 863, 885, 905, 920; „Mehrkörperdynamik …“ Z. 721–769; „Einordnung und mögliche Lücke“ Z. 920–973, Merkmale Z. 942–951; `app:recherche` Z. 5732–5895 |
| **G-2** Die Beitragsaussage fehle in Abstract und Einleitung oder sei unklar; sie sei zu „verdichten“. | **Trifft nicht zu.** Kurzfassung und Abstract schließen mit der Beitragsaussage (keine neue Physik; möglicher Beitrag methodisch und eng; Neuheit ohne systematische Recherche offen). Die Einleitung enthält den Abschnitt „Beitrag dieser Arbeit“ mit neun Punkten, das Fazit den Abschnitt „Methodischer Beitrag“. Ob die Aussagen untereinander widerspruchsfrei sind, ist eine andere Frage; sie ist in Abschnitt 4 geprüft. | Kurzfassung Z. 144–149; Abstract Z. 225–230; `sec:beitrag` Z. 590–696; Fazit „Methodischer Beitrag“ Z. 5175–5196 |
| **G-3** Abzugrenzen sei gegen „Olgac (2005)“, „Korendiy et al. (2026)“ und „Xiong & Xu (2015)“, mit einer Tabelle Zielgröße/Abgrenzung. | **Teilweise schon geführt, in dieser Form nicht übernommen.** „Korendiy et al. 2026“ führt Anhang C als nicht auffindbar; zitiert ist stattdessen Gurskyi, Korendiy et al. 2023. Arbeiten von Fang, Xu und Mitarbeitern stehen als bibliografisch ungeprüfte Kandidaten in Anhang C, in der Einordnung, im Neuheitsgrad-Dokument und in den Zehn Fragen. „Olgac“ kommt im Repository nicht vor. Die drei Angaben sind Gegenstand von Abschnitt 2; die Abgrenzungstabelle des Gutachtens wird nicht übernommen. | Verifikationstabelle Z. 5816; „Nicht aufgenommene Angaben“ Z. 5860–5862 und Z. 5863–5869; Zitat Gurskyi/Korendiy 2023 Z. 741–746, [`references.bib`](arbeitspapier/references.bib) Z. 214–223; [`einordnung.md`](einordnung.md) §5, Z. 165–174; [`neuheitsgrad.md`](neuheitsgrad.md) §10, Z. 236–240; [`zehn_fragen.md`](zehn_fragen.md) Z. 19–21; Suche nach „Olgac“ im ganzen Repository ohne Treffer |
| **G-4** Der Beitrag sei eine Rekombination bekannter Bausteine (Phasensteuerung, Mehrmassensystem, Kontaktkraft) unter methodischer Kontrolle (ruhender Körper, Nullkontrolle, Präregistrierung); Ziel sei die Charakterisierung der Wellenform, nicht die Entdeckung eines neuen Effekts. | **Nicht übernommen; am Repository gemessen.** Die Formel trifft den Verzicht auf einen Effektanspruch und die Selbstbeschreibung als Rekombination. Sie ändert den Anspruch beim Status (prä-experimentell, möglicher Beitrag; Präregistrierung im Entwurf), bei der Gewichtung der Nullgröße und beim Ziel. Zielgrößen nennt die Formel nicht; nach dem Auftrag nennt die Tabelle des Gutachtens Schiefe und Liftoff. | Abschnitt 4.5 |
| **G-5** Die Messkampagne der Linie A sei zu konkretisieren (Hardware, Kanalplan, Schutzkonzept). | **Nicht Teil dieses Abgleichs.** | Abschnitt 6 |
| **G-6** Ein Benchmark sei zu prüfen (offene Daten, Nachrechnung durch Dritte). | **Bestandsaufnahme.** Festgehalten ist, was heute allein aus dem Repository nachrechenbar ist; eine Seite dazu entsteht nicht. | Abschnitt 5 |
| **G-7** Die Unabhängigkeit sei als Stärke darzustellen. | **Nicht Teil dieses Abgleichs.** | Abschnitt 6 |
| **G-8** Gesamturteil „Moderate Revision“. | **Nicht übernommen.** | Abschnitt 6; [`neuheitsgrad.md`](neuheitsgrad.md) §3 |

**Was zutrifft.** Zwei Lücken im Umfeld von G-1 und G-3 benennt das Arbeitspapier selbst:

- Die 13 Einträge des [Literaturabgleichs vom 12.09.2026](literaturabgleich_2026-09-12.md) (zwölf in §1.1, ein
  Kurzvorläufer in §1.2) stehen weder im Literaturverzeichnis noch in Kapitel 2 des Arbeitspapiers (Z. 5844–5848;
  [Offene Punkte](arbeitspapier/PCMMS_Arbeitspapier_Offene_Punkte.md) Nr. 42, Z. 163–167). Nachgezählt: Keine der 13
  Arbeiten steht in [`references.bib`](arbeitspapier/references.bib) (verglichen nach Erstautor und Jahr; 22 Einträge:
  21 Literaturquellen und der Repository-Stand).
- Die Suchbegriffe der Recherche decken Haptik, vibrationsgetriebene Roboter und Kapselsysteme, Impact-Oszillatoren und
  Grazing, dynamisches Wägen und Metrologie nicht ab; eine Recherche in einer bibliografischen Fachdatenbank fehlt
  (Z. 5882–5895; Suchbegriffe Z. 5772–5788; Art der Recherche Z. 5741–5749).

**Dateiname.** Der in den Texten genannte Dateiname `06_neuheitsgrad.md` existiert im Repository nicht; gemeint ist
[`neuheitsgrad.md`](neuheitsgrad.md).

## 2. Literaturprüfung

Eng begrenzte Ausnahme von AP-16 („die Recherche außerhalb des Bestands ist nicht begonnen“): Geprüft sind nur die drei
in G-3 genannten Angaben. Es gab keine weitere Recherche; neue Kandidaten sind nicht aufgenommen. An der Primärquelle
bestätigt ist eine der drei Angaben, a); b) und c) sind nur am Registereintrag geprüft.

**Prüfweg.** Alle Adressen wurden am 10.11.2026 zwischen 15:00 und 15:03 UTC in dieser Sitzung direkt abgerufen; gelesen
wurden die Rohantworten der Server (HTML, PDF, JSON, Kopfzeilen der Weiterleitung), nicht die Ausgabe eines
Zusammenfassungswerkzeugs. Aus der Vorprüfung im Chat vom selben Tag stammen nur die Suchschlüssel: Titel, Autoren und
Kennungen (die DOIs zu a) und c), zu b) die Artikelkennung PII; die DOI zu b) stammt aus der Registersuche). Ihre
Ergebnisse sind nicht übernommen, alle Angaben unten sind an den abgerufenen Quellen neu gelesen. Der Netzzugang der
Sitzung war zunächst gesperrt und wurde vom Autor für sieben Hosts freigegeben (`doi.org`, `api.crossref.org`,
`www.extrica.com`, `journals.sagepub.com`, `www.sciencedirect.com`, `linkinghub.elsevier.com`, `patents.google.com`).
„Bibliografisch geprüft“ heißt wie in Anhang C des Arbeitspapiers (Z. 5794–5797): Autoren, Titel, Erscheinungsort und
Jahr auf der Seite des Verlags oder Repositoriums bestätigt, DOI aufgelöst. Der Eintrag im DOI-Register Crossref enthält
die vom Verlag hinterlegten Angaben; er ist hier als Registereintrag geführt und zählt nicht als Verlagsseite. Aussagen
über den Inhalt stammen nur aus dem selbst gelesenen Text; der Lesestand steht dabei.

**Ergebnis.**

| Angabe der Texte | Gefundene Arbeit | Bibliografisch geprüft | Lesestand | DOI |
|---|---|---|---|---|
| a) „Korendiy et al. (2026)“ | Korendiy, Yaniv, Predko, Laushnyk, Dzyubyk, Hrevtsov 2026, Vibroengineering Procedia 62, S. 41–50 | **ja** (Verlagsseite, Verlags-PDF, DOI aufgelöst; Register stimmt überein) | Volltext | `10.21595/vp.2026.26165` |
| b) „Olgac (2005)“ | kein Aufsatz von 2005 zum Kraftgenerator gefunden (eine Registerabfrage nach Titel und Autoren, die ersten fünf Treffer); gefunden: Mikus, Olgac, Sipahi 2009, Control Engineering Practice 17 (1), S. 210–220 | **nein** – DOI aufgelöst und Registereintrag gelesen; die Weiterleitungsseite des Verlags nennt nur den Titel, die Artikelseite verlangt eine Captcha-Eingabe und ist nicht gelesen | nur Katalogeintrag (Aufsatz); daneben der Abstract eines Tagungsbeitrags gleichen Titels von 2003 | `10.1016/j.conengprac.2008.07.002` |
| c) „Xiong & Xu (2015)“ | Zhan, Xu 2015, Advances in Mechanical Engineering 7 (3), Artikel 1687814015573766 – mutmaßlich die gemeinte Arbeit; nach dem Registereintrag ist „Xiong“ der Vorname des Erstautors | **nein** – DOI aufgelöst und Registereintrag gelesen, die Verlagsseite antwortet mit 403 und einer Zugangsprüfung und ist nicht gelesen | Abstract (im Registereintrag) | `10.1177/1687814015573766` |

Die Angabe in Anhang C, zu „Korendiy et al. 2026“ sei keine Arbeit dieses Jahres auffindbar (Z. 5860–5862, Stichtag 4.
und 5. September 2026, Z. 5757), ist damit überholt: Eine Arbeit von Korendiy und Mitautoren ist am 08.06.2026
erschienen, die Suche hat sie nicht gefunden. Ob die Angabe vom September genau diese Arbeit meinte, lässt sich nicht
prüfen; das Repository überliefert zu ihr nur Autor und Jahr (Nr. 21 der
[Offenen Punkte](arbeitspapier/PCMMS_Arbeitspapier_Offene_Punkte.md)). Für b) und c) fehlt die Bestätigung auf der
Verlagsseite; sie war in dieser Sitzung nicht möglich und steht aus (Offene Punkte Nr. 46).

### 2.1 a) „Korendiy et al. (2026)“

| Feld | Inhalt |
|---|---|
| Bibliografie | Vitaliy Korendiy, Oleksandr Yaniv, Rostyslav Predko, Ihor Laushnyk, Andriy Dzyubyk, Serhii Hrevtsov: „Trajectory-based synthesis of a three-mass vibratory system excited by a dual phase-controlled crank-slider mechanism“. Vibroengineering Procedia, Band 62 (Juni 2026), S. 41–50; keine Heftnummer; ISSN 2345-0533 (Druck), 2538-8479 (online); Verlag Extrica (im Register: JVE International Ltd.). Eingegangen 22.02.2026, angenommen 30.03.2026, veröffentlicht 08.06.2026; Beitrag zur 76th International Conference on Vibroengineering, Taschkent, 28.–29.04.2026; Open Access, CC BY 4.0. DOI `10.21595/vp.2026.26165`. Alle Autoren: Lviv Polytechnic National University, Lwiw. |
| Prüfweg | <https://doi.org/10.21595/vp.2026.26165> leitet weiter (302) auf die Verlagsseite <https://www.extrica.com/article/26165> (200): Titel, sechs Autoren in dieser Reihenfolge, Zeitschrift, Band, Seiten, Datum und DOI stehen in den Metaangaben und im Seitentext. Verlags-PDF <https://www.extrica.com/article/26165/pdf>: 10 Seiten, Kolumnentitel „Vibroengineering Procedia. June 2026, Volume 62“, S. 41–50. Registereintrag <https://api.crossref.org/works/10.21595/vp.2026.26165>: übereinstimmend. Abruf 10.11.2026. **Bibliografisch geprüft: ja.** |
| Lesestand | Volltext: HTML-Volltext der Verlagsseite, Abschnitte 1 bis 4 mit Literaturliste; Verlags-PDF zum Abgleich, darin auch Fig. 1 (Schema) und Fig. 2 (Bahnen) angesehen. |
| System | Ebenes System mit drei bewegten Massen. Das Arbeitsorgan m₁ bewegt sich rein translatorisch in zwei Richtungen (Drehschwingungen vernachlässigt) und steht auf viskoelastischen Stützen (Feder-Dämpfer-Paare waagerecht und senkrecht). Zwei Hilfsmassen m₂, m₃ laufen auf zwei geneigten geraden Führungen und sind je über Feder und viskosen Dämpfer an den Schieber eines Schubkurbelkanals gekoppelt; die Schieber sind masselos angenommen. Nach Fig. 1 sitzt der Kurbeltrieb am Arbeitsorgan, und die Stützen verbinden das Arbeitsorgan mit einem festen Gestell. Modell mit vier Freiheitsgraden (x₁, y₁, u₂, u₃; u₂, u₃ relativ zum Arbeitsorgan). Rechenbeispiel: m₁ = 50 kg, m₂ = m₃ = 5 kg, 15 Hz (dort Abschnitte 2.1, 2.3, 3). |
| Bewegungsgesetz | Nicht harmonisch: Die Kurbel dreht mit konstanter Winkelgeschwindigkeit, der Schieberweg folgt der exakten Schubkurbelkinematik (dort Gl. 1). Bei r/l = 0,2 ist er nahe an einer Sinusbewegung mit kleiner zweiter Harmonischer (dort Abschnitt 3). Vorgegeben ist die Fußpunktbewegung der Koppelglieder; die Bewegung der Hilfsmassen und des Arbeitsorgans folgt aus der Dynamik (dort Abschnitte 2.2, 2.3). Kleine Abweichungen der berechneten Bahnen von idealen Ellipsen und Kreisen führt die Arbeit auf die höheren Harmonischen der Schubkurbelbewegung zurück, eine Folge der endlichen Pleuellänge (dort Highlights, Abschnitte 2.2 und 3). |
| Stellgröße | Phasenversatz γ zwischen den beiden Kurbelzapfen, also zwischen den beiden Erregerkanälen (φ₂ = φ + γ); wirksam ist δ = γ + (θ₃ − θ₂) mit den Führungswinkeln θ₂, θ₃. Im Modell ist γ je Konfiguration ein fester Einstellwert; eine Verstellung im Betrieb ist als Ausblick genannt. Daneben als Entwurfsgrößen die Führungswinkel und die Kurbelradien (Hübe) (dort Abschnitte 2.2, 3, 4). |
| Zielgröße | Stationäre Bahn des Arbeitsorgans in der Ebene: geradlinig (senkrecht, waagerecht, geneigt), elliptisch, nahezu kreisförmig (dort Abschnitt 2.4, Fig. 2). |
| Körper | Bewegt. Die Schwingbahn des Arbeitsorgans ist das Ziel. Die Lagerung ist beidseitig viskoelastisch; ein einseitiger Kontakt oder ein Abheben kommt im Modell nicht vor. |
| Kraft an Auflage oder Fundament | Nicht ausgewertet. Die Zweigkräfte F₂, F₃ und die resultierende Erregerkraft auf das Arbeitsorgan stehen in den Bewegungsgleichungen (dort Abschnitt 2.3). Die Rückstell- und Dämpfungskräfte der Stützen sind als Modellannahme genannt und stehen als Terme in den Bewegungsgleichungen (dort Abschnitt 2.1, Gl. 3); als Ergebnis berichtet sind sie nicht. Berichtet sind Bahnen (Fig. 2) und eine qualitative Tabelle der Parametereinflüsse (Table 1). Eine auf Gestell oder Fundament übertragene Kraft kommt im Volltext nicht vor. |
| Art der Arbeit | Analytik (Modell, stationäre Amplituden- und Phasenbeziehungen) und numerische Simulation (Wolfram Mathematica) an einem idealisierten Modell. Kein Experiment; die experimentelle Prüfung an einem Prototyp ist als künftige Arbeit genannt (dort Abschnitte 3, 4). |

**Abgrenzung zu PCMMS** (entlang der vier Merkmale, Z. 942–951). Gemeinsam sind ein Körper auf Stützen, der seinen
Antrieb mit bewegten Massen selbst trägt, drei Massen, die relative Phase als wichtigste Stellgröße, eine nicht
harmonische Bewegung (dort aus der Kurbelkinematik) und eine Studie ohne Experiment, gerechnet an einem idealisierten
Modell. Zielgröße ist dort die Bahn des Arbeitsorgans, nicht die Wellenform einer Kontaktkraft; gestellt wird die Phase
zwischen zwei Erregerkanälen mit je einer Hilfsmasse, und der Körper soll schwingen, auf beidseitig viskoelastischen
Stützen ohne einseitigen Kontakt. Eine Kraft an Auflage oder Fundament wird nicht ausgewertet, und eine durch einen
Erhaltungssatz festgelegte Kontrollgröße kommt im Volltext nicht vor.

Die Literaturliste der Arbeit enthält mehrere frühere Arbeiten mit Korendiy als Autor, darunter solche zur
Schubkurbel-Erregung (dort [18] bis [20]). Sie sind hier weder geprüft noch als Kandidaten aufgenommen; über die drei
Angaben hinaus ist nicht recherchiert (AP-16). In der Literaturliste steht auch die Arbeit von Osadchyy et al. 2023, die
im Literaturverzeichnis des Arbeitspapiers geführt ist.

### 2.2 b) „Olgac (2005)“

Einen Aufsatz von 2005 zum Kraftgenerator hat die Prüfung nicht ergeben. Dass die Angabe „Olgac (2005)“ den
Kraftgenerator-Aufsatz von Mikus, Olgac und Sipahi meint, ist ein Hinweis der Vorprüfung und nicht gesichert; die Texte
lagen nicht vor. Gesucht wurde mit einer einzigen Abfrage im DOI-Register nach Titel und Autoren dieses Aufsatzes, nicht
allgemein nach Arbeiten von Olgac aus dem Jahr 2005. Abgerufen sind die ersten fünf Treffer (`rows=5`; das Register
meldet 1 183 594). Unter ihnen sind ein Zeitschriftenaufsatz von 2009 und ein Tagungsbeitrag gleichen Titels von 2003.
Ein weiterer Treffer ist ein Tagungsbeitrag von Olgac und Sipahi von 2005, dem Titel nach zu einem anderen Gegenstand
(„Chatter Stability Mapping for Simultaneous Machining“, DOI `10.1115/imece2005-79116`); er ist nicht geprüft und kein
Kandidat. Zur Jahreszahl 2005 siehe den Prüfvermerk unten. Zitierfähig wäre der Aufsatz von 2009.

| Feld | Inhalt |
|---|---|
| Bibliografie | Oldrich Mikus, Nejat Olgac, Rifat Sipahi: „An actively controlled harmonic force generator“. Control Engineering Practice, Band 17, Heft 1 (Januar 2009), S. 210–220; ISSN 0967-0661; Elsevier. DOI `10.1016/j.conengprac.2008.07.002`. Angaben nach dem Registereintrag. |
| Prüfweg | Registersuche `https://api.crossref.org/works?query.bibliographic=An+actively+controlled+harmonic+force+generator+Mikus+Olgac+Sipahi&rows=5` (dazu eine Feldauswahl mit `select=`; abgerufen sind die ersten fünf von 1 183 594 gemeldeten Treffern). Registereintrag <https://api.crossref.org/works/10.1016/j.conengprac.2008.07.002>: Autoren, Titel, Zeitschrift, Band, Heft, Seiten, Jahr. <https://doi.org/10.1016/j.conengprac.2008.07.002> leitet weiter (302) auf <https://linkinghub.elsevier.com/retrieve/pii/S0967066108001238> (200), eine Weiterleitungsseite des Verlags, die nur den Titel und die Kennung (PII) des Artikels nennt. Die Artikelseite <https://www.sciencedirect.com/science/article/pii/S0967066108001238> antwortet mit 403 und einer Captcha-Abfrage; sie ist nicht gelesen. Registereintrag des Tagungsbeitrags von 2003: <https://api.crossref.org/works/10.1115/imece2003-41410>. Abruf 10.11.2026. **Bibliografisch geprüft: nein** – Registereintrag und DOI-Auflösung liegen vor, die Bestätigung auf der Verlagsseite fehlt. |
| Lesestand | Zeitschriftenaufsatz: nur Katalogeintrag, hier der Registereintrag bei Crossref (ohne Abstract). Nebenquelle, kein Ersatz für den Aufsatz: der Abstract des Tagungsbeitrags gleichen Titels von 2003 im Registereintrag (zur Zuordnung siehe den Prüfvermerk). |
| System | Aus dem Registereintrag nicht zu entnehmen. Abstract des Tagungsbeitrags: Geräte mit umlaufenden Exzentermassen; Zahl und Anordnung der Massen sind im Abstract nicht genannt. |
| Bewegungsgesetz | Aus dem Registereintrag nicht zu entnehmen. Abstract des Tagungsbeitrags: Erzeugt wird eine harmonische Kraft; ob die Bewegung der Massen vorgegeben ist, ist im Abstract nicht genannt. |
| Stellgröße | Aus dem Registereintrag nicht zu entnehmen. Abstract des Tagungsbeitrags: Verstellt werden Amplitude, Frequenz und Phasenwinkel der harmonischen Kraft. Die „relative phase“ ist dort die Phase der Kraft gegen ein gegebenes harmonisches Signal; eine Phase zwischen den Massen nennt der Abstract nicht. |
| Zielgröße | Aus dem Registereintrag nicht zu entnehmen. Abstract des Tagungsbeitrags: eine harmonische Kraft mit einstellbarer Amplitude (null bis F_max), Frequenz (rund ±10 % um die Nennfrequenz) und Phase (0 bis 2π gegen ein gegebenes harmonisches Signal), zur Krafterregung oder zur Tilgung harmonisch erregter Schwingungen; dazu ein günstiges Verhältnis von Spitzenkraft zu Gewicht. |
| Körper | Aus dem Registereintrag nicht zu entnehmen; im Abstract des Tagungsbeitrags nicht genannt. |
| Kraft an Auflage oder Fundament | Aus dem Registereintrag nicht zu entnehmen. Im Abstract des Tagungsbeitrags ist die erzeugte Kraft selbst die Zielgröße; eine Kraft an Auflage oder Fundament ist dort nicht genannt. |
| Art der Arbeit | Aus dem Registereintrag nicht zu entnehmen. Abstract des Tagungsbeitrags: Entwurf und Steuerung eines Geräts, Erprobung an einem Prototyp. |

**Prüfvermerk zur Herkunft der Angabe.** Tagungsbeitrag nach dem Registereintrag
<https://api.crossref.org/works/10.1115/imece2003-41410> (Abruf 10.11.2026): O. Mikus, N. Olgac, R. Sipahi, „An Actively
Controlled Harmonic Force Generator“, in „Dynamic Systems and Control, Volumes 1 and 2“ (ASME 2003 International
Mechanical Engineering Congress and Exposition, Washington, DC, 15.–21.11.2003), S. 31–40, DOI
`10.1115/imece2003-41410`. Dass er die Konferenzfassung des Aufsatzes ist, ist aus dem gleichen Titel und denselben drei
Autoren geschlossen; eine Beziehung zwischen beiden Einträgen ist im Register nicht hinterlegt. Als Zieladresse der DOI
nennt der Registereintrag eine Seite unter `asmedigitalcollection.asme.org`; die DOI ist in dieser Sitzung nicht
aufgelöst, die Seite nicht abgerufen. Patentanmeldung (Nummer aus der Vorprüfung): US 2005/0077845 A1, „Actively
controlled harmonic force generator“, Erfinder Nejat Olgac, Oldrich Mikus, Rifat Sipahi, angemeldet 20.08.2004,
veröffentlicht 14.04.2005, gelesen unter <https://patents.google.com/patent/US20050077845A1/en>. Der Titel ist bis auf
den einleitenden Artikel der des Aufsatzes, die drei Personen sind dieselben; die Anmeldung ist die mutmaßliche Herkunft
der Jahreszahl 2005. Sie ist kein Literatureintrag, und ihr Inhalt ist in dieser Notiz nicht verwendet.

**Abgrenzung zu PCMMS** (nur nach dem Abstract des Tagungsbeitrags von 2003; der Aufsatz selbst ist nicht gelesen).
Gemeinsam sind nach diesem Abstract bewegte Massen, mit denen eine Kraft geformt wird; er nennt dafür Geräte mit
umlaufenden Exzentermassen. Zielgröße ist dort eine harmonische Kraft mit einstellbarer Amplitude, Frequenz und Phase
gegen ein Bezugssignal, nicht die Wellenform einer einseitigen Kontaktkraft. Eine Phasenlage zwischen den Massen als
Stellgröße, ein ruhender Körper, ein Kontaktverlust und eine Kontrollgröße sind im Abstract nicht genannt.

### 2.3 c) „Xiong & Xu (2015)“

**Namensprüfung.** Der Registereintrag führt die Autoren als Xiong Zhan (Vorname Xiong, Nachname Zhan) und Jian Xu.
„Xiong & Xu“ nennt danach einen Vornamen als Nachnamen; nach dem Registereintrag ist Zhan und Xu richtig, die
Bestätigung auf der Verlagsseite fehlt.

| Feld | Inhalt |
|---|---|
| Bibliografie | Xiong Zhan, Jian Xu: „Locomotion analysis of a vibration-driven system with three acceleration-controlled internal masses“. Advances in Mechanical Engineering, Band 7, Heft 3 (2015), Artikelnummer 1687814015573766; ISSN 1687-8132, 1687-8140; SAGE Publications. DOI `10.1177/1687814015573766`. Im Register: Druckdatum 01.03.2015, Online-Datum 06.04.2015. Angaben nach dem Registereintrag. |
| Prüfweg | Registereintrag <https://api.crossref.org/works/10.1177/1687814015573766>: Autoren, Titel, Zeitschrift, Band, Heft, Artikelnummer, Jahr, Abstract. <https://doi.org/10.1177/1687814015573766> leitet weiter (302) auf <https://journals.sagepub.com/doi/10.1177/1687814015573766>; die Seite antwortet mit 403 und einer automatischen Zugangsprüfung (Seitentitel „Just a moment...“, Kopfzeile `cf-mitigated: challenge`) und ist nicht gelesen. Abruf 10.11.2026. **Bibliografisch geprüft: nein** – Registereintrag und DOI-Auflösung liegen vor, die Bestätigung auf der Verlagsseite fehlt. |
| Lesestand | Abstract, wie ihn der Verlag im Register hinterlegt hat. |
| System | Ein starrer Körper auf einer waagerechten Ebene mit drei inneren, beschleunigungsgesteuerten Massen als Antrieb; zwischen System und Ebene wirkt isotrope Trockenreibung. |
| Bewegungsgesetz | Die Beschleunigung der inneren Massen ist gesteuert („acceleration-controlled“). Ob das Gesetz harmonisch ist, ist im Abstract nicht genannt. |
| Stellgröße | Im Abstract „drive parameters“ (Antriebsparameter), nicht näher bezeichnet. Eine relative Phase ist im Abstract nicht genannt. |
| Zielgröße | Fortbewegung des Körpers in der Ebene: geradlinige und drehende Grundbewegung, daraus zusammengesetzte Bahnen (schräge Geraden und Kurven, durch Streckenzüge angenähert); Steigung und Krümmung über die Antriebsparameter einstellbar; Optimierung der Antriebsparameter auf maximale mittlere Geschwindigkeit. |
| Körper | Bewegt. |
| Kraft an Auflage oder Fundament | Im Abstract nicht genannt; genannt ist nur die Reibung zwischen System und Ebene. |
| Art der Arbeit | Im Abstract nicht ausdrücklich genannt (die Dynamik wird „studied“, die ebene Fortbewegung „constructed“, Bahnen werden „proposed“, Parameter „optimized“); ein Experiment ist im Abstract nicht genannt. |

**Ist das eine der Arbeiten, die das Projekt als „Fang, Xu und Mitarbeiter“ führt?** Aus den gelesenen Quellen nicht zu
entscheiden. Das Repository nennt keine Vornamen und zwei Fundstellen ([`einordnung.md`](einordnung.md) Z. 169–171:
Commun. Nonlinear Sci. Numer. Simul. 114, 106704, 2022, und Diao, Zhang & Fang, Arch. Appl. Mech. 91, 2073–2088, 2021);
keine davon ist diese Arbeit. Die abweichenden Arbeitsangaben in Projektunterlagen außerhalb des Repositorys, auf die
Anhang C (Z. 5865–5867) und `einordnung.md` (dort Z. 172–173) verweisen, lagen nicht vor; gegen sie ist nicht geprüft.
Der Registereintrag nennt für beide Autoren die Tongji-Universität, Shanghai; die Fudan-Universität kommt in ihm nicht
vor. Gegenstand ist nach dem Abstract ein einzelner Körper mit drei inneren Massen, kein Mehrmodul-Roboter.

**Abgrenzung zu PCMMS.** Gemeinsam ist nach dem Abstract ein Körper mit drei inneren, gesteuert bewegten Massen.
Zielgröße ist dort die Fortbewegung des Körpers auf einer Ebene mit Trockenreibung (Bahn und mittlere Geschwindigkeit),
der Körper bewegt sich also; eine relative Phase als Stellgröße, eine Kontaktkraft als Zielgröße und eine Kontrollgröße
sind im Abstract nicht genannt. Die im Auftrag wiedergegebene Inhaltsangabe der Texte (Bewegungsarten über
Phasenbeziehungen) ist am Abstract nicht bestätigt.

### 2.4 BibTeX-Arbeitsblock

Nach dem Muster von [`literaturabgleich_2026-09-12.md`](literaturabgleich_2026-09-12.md) §1.1. Der Block steht nur in
dieser Notiz, nicht in `references.bib` (Variante A). Die Titel folgen der Schreibweise der Verlagsseite (a) bzw. des
Registers (b, c).

```bibtex
@article{KorendiyEtAl2026,
  author  = {Korendiy, Vitaliy and Yaniv, Oleksandr and Predko, Rostyslav and Laushnyk, Ihor and Dzyubyk, Andriy and Hrevtsov, Serhii},
  title   = {Trajectory-based synthesis of a three-mass vibratory system excited by a dual phase-controlled crank-slider mechanism},
  journal = {Vibroengineering Procedia},
  year    = {2026},
  volume  = {62},
  pages   = {41--50},
  note    = {Beitrag zur 76th International Conference on Vibroengineering, Taschkent, 28.--29.04.2026; online 08.06.2026; Open Access},
  doi     = {10.21595/vp.2026.26165}
}

@article{MikusOlgacSipahi2009,
  author  = {Mikus, Oldrich and Olgac, Nejat and Sipahi, Rifat},
  title   = {An actively controlled harmonic force generator},
  journal = {Control Engineering Practice},
  year    = {2009},
  volume  = {17},
  number  = {1},
  pages   = {210--220},
  note    = {Angaben nach dem Crossref-Eintrag; Verlagsseite am 10.11.2026 nicht gelesen},
  doi     = {10.1016/j.conengprac.2008.07.002}
}

@article{ZhanXu2015,
  author  = {Zhan, Xiong and Xu, Jian},
  title   = {Locomotion analysis of a vibration-driven system with three acceleration-controlled internal masses},
  journal = {Advances in Mechanical Engineering},
  year    = {2015},
  volume  = {7},
  number  = {3},
  pages   = {1687814015573766},
  note    = {Artikelnummer 1687814015573766; Angaben nach dem Crossref-Eintrag; Verlagsseite am 10.11.2026 nicht gelesen},
  doi     = {10.1177/1687814015573766}
}
```

**Prüfstand 10.11.2026:** `KorendiyEtAl2026` gegen die Verlagsseite, das Verlags-PDF und den Registereintrag geprüft
(Autoren, Titel, Zeitschrift, Band, Seiten, Datum, DOI); DOI aufgelöst; Volltext gelesen. `MikusOlgacSipahi2009` und
`ZhanXu2015` nur gegen den Registereintrag geprüft, DOI aufgelöst, Verlagsseite offen. Kein Eintrag geht ohne die
Sichtprüfung des Autors ins Literaturverzeichnis ([`neuheitsgrad.md`](neuheitsgrad.md) §9; E-1). In `references.bib`
wären die Schlüssel nach der dortigen Schreibweise klein zu führen, etwa `korendiy2026`.

## 3. Berichtigung und Textvorschläge

Nur für die Arbeit, die Abschnitt 2 bibliografisch bestätigt hat: a) Korendiy et al. 2026. Für b) und c) entsteht kein
Vorschlag, weil sie nicht bestätigt sind. Alles in diesem Abschnitt ist Vorschlag. Quelltext, PDF und
Literaturverzeichnis des Arbeitspapiers v2.5 bleiben unverändert (Variante A); der Berichtigungshinweis steht in
[`arbeitspapier/README.md`](arbeitspapier/README.md) und in den
[Offenen Punkten](arbeitspapier/PCMMS_Arbeitspapier_Offene_Punkte.md) (Nr. 45 und 46).

### 3.1 Berichtigung zu Anhang C

**Sachverhalt.** Anhang C führt „Korendiy et al. 2026“ an zwei Stellen als nicht auffindbar. Eine Arbeit von Korendiy
und Mitautoren aus dem Jahr 2026 besteht und ist am 08.06.2026 erschienen, vor dem Stichtag der Recherche (4. und 5.
September 2026, Z. 5757). Die Suche hat sie nicht gefunden.

**Reichweite des Wortlauts.** Der folgende Wortlaut gilt für den Fall, dass die Arbeit nach der Sichtprüfung des Autors
aufgenommen wird (E-1). Ohne Aufnahme entfallen die neue Zeile der Verifikationstabelle und der Zusatz „(nächste
Zeile)“, und der letzte Satz des Punkts lautet dann: „Sie ist auf der Verlagsseite geprüft und im Volltext gelesen
(Vibroengineering Procedia 62, S. 41–50, DOI 10.21595/vp.2026.26165); über ihre Aufnahme ist nicht entschieden.“ Der
Einleitungssatz gilt in beiden Fällen.

**Verifikationstabelle (`tab:verifikation`), Z. 5816.** Bisher:

```latex
    Gurskyi/Korendiy et al.\ 2023 & MDPI & DOI & Ersatz für nicht auffindbares „Korendiy 2026“ \\
```

Vorschlag, mit einer neuen Zeile für die geprüfte Arbeit:

```latex
    Gurskyi/Korendiy et al.\ 2023 & MDPI & DOI & am 5.~September 2026 anstelle der damals nicht verifizierten Angabe „Korendiy 2026“ aufgenommen; eine Arbeit von 2026 ist inzwischen bestätigt (nächste Zeile) \\
    Korendiy et al.\ 2026 & Extrica & DOI & geprüft am 10.~November 2026, Volltext gelesen; erschienen am 8.~Juni 2026, bei der Suche vom 4.\ und 5.\ September 2026 nicht gefunden \\
```

**„Nicht aufgenommene Angaben“, Einleitungssatz (Z. 5852–5854).** Bisher:

```latex
Drei Angaben aus früheren Projektdokumenten oder aus externen
Prüfungen wurden \emph{nicht} aufgenommen, weil sie sich nicht
verifizieren ließen:
```

Vorschlag:

```latex
Drei Angaben aus früheren Projektdokumenten oder aus externen
Prüfungen wurden bei der Recherche vom 4.\ und 5.\ September 2026
\emph{nicht} aufgenommen, weil sie sich damals nicht verifizieren
ließen; die zweite ist am 10.\ November 2026 berichtigt:
```

**„Nicht aufgenommene Angaben“, Punkt „Korendiy et al. 2026“ (Z. 5860–5862).** Bisher:

```latex
\item \emph{„Korendiy et al.\ 2026“} --- keine Arbeit dieses Jahres
      auffindbar; die Arbeitsgruppe ist real, die verifizierte Arbeit
      von 2023 wurde stattdessen aufgenommen.
```

Vorschlag:

```latex
\item \emph{„Korendiy et al.\ 2026“} --- bei der Suche am 4.\ und
      5.\ September 2026 nicht gefunden; aufgenommen wurde damals
      stattdessen die verifizierte Arbeit von 2023 \cite{gurskyi2023}.
      Berichtigung vom 10.\ November 2026: Eine Arbeit von Korendiy
      et al.\ aus dem Jahr 2026 besteht; sie ist am 8.\ Juni 2026
      erschienen, also vor dem Stichtag. Sie ist auf der Verlagsseite
      geprüft, im Volltext gelesen und nachträglich aufgenommen
      \cite{korendiy2026}.
```

**Punkt zur Fudan-Zuschreibung (Z. 5863–5869).** Kein Vorschlag, weil c) nicht im Sinn von Anhang C bestätigt ist. Als
Hinweis: Mit „Xiong & Xu (2015)“ ist mutmaßlich Zhan und Xu 2015 gemeint (Abschnitt 2.3); der Registereintrag dieser
Arbeit nennt die Tongji-Universität, nicht die Fudan-Universität, und die Arbeit ist keine der beiden Fundstellen in
[`einordnung.md`](einordnung.md) §5.

### 3.2 Textvorschlag für „Mehrkörperdynamik und phasengesteuerte Anregung“

Ein Absatz für a), im Ton der vorhandenen Absätze. Einzufügen nach dem Satz zu Gurskyi, Korendiy et al., der in Z. 746
mit `\cite{gurskyi2023}` endet; die beiden Sätze zur Haptik (Z. 746–750) beginnen dann einen neuen Absatz.

```latex
Korendiy et al.\ untersuchen ein ebenes Dreimassensystem mit
Schubkurbelantrieb: Zwei Hilfsmassen laufen auf geneigten Führungen und
regen das viskoelastisch gelagerte Arbeitsorgan über
Feder-Dämpfer-Glieder an \cite{korendiy2026}. Steuergröße ist vor allem
der Phasenversatz zwischen den beiden Kurbelkanälen, daneben
Führungswinkel und Kurbelradien; Zielgröße ist die stationäre Bahn des
Arbeitsorgans --- geradlinig, elliptisch oder nahezu kreisförmig. Der
Schieberweg ist nur näherungsweise sinusförmig, und kleine Abweichungen
der Bahnen von der idealen Ellipse oder dem Kreis führen die Autoren
auf dessen höhere Harmonische zurück. Gerechnet wird an einem
idealisierten Modell mit vier Freiheitsgraden, analytisch und in
numerischer Simulation; ein Experiment steht aus, und eine Kraft an
Auflage oder Fundament wird nicht ausgewertet.
```

Der Vorschlag hält die Grenze von fünf Sätzen ein (vier Satzschlüsse, im ersten Satz ein Ganzsatz nach dem Doppelpunkt)
und folgt der Wortwahl des Arbeitspapiers („Steuergröße“, Z. 804; für die Schubkurbel „näherungsweise sinusförmig“,
Z. 2270–2271 und Z. 4125–4126). Jede Aussage steht in Abschnitt 2.1.

**Gilt der Absatz „Der Zweck ist in diesen Anwendungen …“ (Z. 764–769) unverändert?** Mit a) ja. Zweck der neuen Arbeit
ist die Bahn des Arbeitsorgans, und die steht in der Aufzählung des Absatzes (Z. 766). Die Kraft an der Auflage ist dort
nicht Zielgröße; sie wird nicht einmal ausgewertet, „Begleiterscheinung“ (Z. 769) trifft also nur im weiteren Sinn. Für
b) und c) ist die Frage nicht geprüft; sie stellt sich erst, wenn die Arbeiten bestätigt und im Volltext gelesen sind.

Unabhängig von den neuen Arbeiten steht der Absatz schon am Stand `51f79a2` in Spannung zum Absatz davor: Dort heißt es
für die Robotik, Bewegung und Kontaktkraft würden „gemeinsam als Entwurfsgrößen behandelt“ (Z. 753–754), hier dagegen,
der Zweck sei „durchweg ein anderer als hier“ und die Kraft an der Auflagefläche „nicht die Zielgröße, sondern eine
Begleiterscheinung“ (Z. 764–769). Das ist nicht geändert und in der Beschreibung des Pull Requests gemeldet.

### 3.3 Folgeänderungen

Nr. 1 bis 3 und die neue Zeile aus Nr. 4 gelten bei einer Aufnahme von a); die geänderte Anmerkung aus Nr. 4 (ohne den
Zusatz „(nächste Zeile)“) sowie Nr. 5 und 6 gelten schon mit der Berichtigung; Nr. 7 betrifft den Neusatz, Nr. 8 nennt,
was bleibt, und Nr. 9 die Dateien außerhalb des Arbeitspapiers.

1. [`references.bib`](arbeitspapier/references.bib): neuer Eintrag `korendiy2026` mit den Feldern aus Abschnitt 2.4,
   nach `gurskyi2023` (Z. 214–223 der Datei) und mit eigener Kommentarzeile zum Prüfstand 10.11.2026, weil der Block
   davor den Vermerk zur Prüfung vom 05.09.2026 trägt (Z. 201 der Datei). Den deutschen Vermerk im Feld `note` wie in
   der Datei üblich mit `\foreignlanguage{ngerman}{…}` auszeichnen (Z. 84, 95 und 254 der Datei); Kopfkommentar um den
   Prüfstand ergänzen.
2. „Einordnung und mögliche Lücke“, Z. 925–927: Der Sammelverweis `\cite{chen2019, osadchyy2023, gurskyi2023}` belegt
   dort den Satz, die Phasensteuerung mehrerer Massen werde „technisch eingesetzt“. a) ist eine Modellstudie ohne
   Experiment (Abschnitt 2.1) und belegt einen technischen Einsatz nicht. Näher liegt ein eigener Halbsatz, etwa „… und
   für die Bahnform eines Dreimassensystems am Modell untersucht `\cite{korendiy2026}`“.
3. Z. 5792: „Jede der 21 Literaturquellen“ wird zu 22; dazu der Hinweis, dass ein Eintrag am 10.11.2026 geprüft ist
   (der Stichtag der Rahmendaten, Z. 5757, bleibt 4. und 5. September 2026).
4. Verifikationstabelle: geänderte Anmerkung wie in 3.1; die neue Zeile nur bei Aufnahme. In den Rahmendaten
   (Z. 5759–5760, „Verifikationsquellen“) fehlt dann Extrica; dort fehlen schon am Stand `51f79a2` Hindawi, PMC, CRC und
   McGraw-Hill, die die Tabelle nennt (Z. 5814, 5815, 5822, 5823; in der Beschreibung des Pull Requests gemeldet).
5. „Nicht aufgenommene Angaben“, Einleitungssatz Z. 5852–5854: neu fassen (Wortlaut in 3.1); der Punkt bleibt in der
   Liste.
6. Möglich, vom Auftrag nicht verlangt: in „Folgerung für die Aussagen zum Forschungsstand“ (Z. 5882–5895) ein Satz,
   dass die Suche vom 4. und 5. September 2026 die knapp drei Monate vorher erschienene Arbeit nicht gefunden hat. Ob er
   aufgenommen wird, entscheidet der Autor.
7. Titelblatt (Z. 61), PDF-Metadaten der Präambel (Z. 33) und Versionshinweis (neuer Absatz nach Z. 376), Neusatz nach
   [`arbeitspapier/README.md`](arbeitspapier/README.md) und die Verweise auf „v2.5“ in anderen Dateien: nur in
   Variante B (E-2).
8. Die Zählungen der Literatureinträge in den Offenen Punkten (Z. 21, 64, 101, 110 und 123 der Datei) und die abgelegte
   Ausgabe der formalen Literaturprüfung
   ([`rechnungen/neuheit/bibcheck_ausgabe.txt`](../rechnungen/neuheit/bibcheck_ausgabe.txt), Z. 2–4 und Z. 52) sind
   datierte Stände und bleiben.
9. Außerhalb des Arbeitspapiers wären die Sätze nachzuführen, die den Stand vom 10.11.2026 festhalten:
   [`neuheitsgrad.md`](neuheitsgrad.md) §10 (Nachtrag), [`arbeitsplan_status.md`](arbeitsplan_status.md) (AP-16, E-1,
   E-2), [`arbeitspapier/README.md`](arbeitspapier/README.md) (Absatz „Berichtigung 10.11.2026“) und die Offenen Punkte
   Nr. 45 und 46.

## 4. Beitragsaussagen

Verglichen sind sieben Stellen: (1) der Schlussabsatz der Kurzfassung (Z. 144–149), (2) der Schlussabsatz des Abstracts
(Z. 225–230), (3) „Beitrag dieser Arbeit“ (Z. 590–696), (4) „Einordnung und mögliche Lücke“ (Z. 920–973), (5) das Fazit
„Methodischer Beitrag“ (Z. 5175–5196), (6) [`neuheitsgrad.md`](neuheitsgrad.md) §7 und §8 (dort Z. 163–196) und (7) der
Abschnitt „Worum es geht“ der [README](../README.md) (dort Z. 9–36). Maßstab sind die „Verbindlichen Begriffe“ in
[`overview.md`](overview.md) (dort Z. 46–57) und der [Entwurf der Präregistrierung v2](praeregistrierung_v2_entwurf.md).
Weitere Beitragsaussagen des Repositorys sind nicht verglichen, etwa in [`einordnung.md`](einordnung.md) („Was ist dann
konkret der Beitrag?“), [`zehn_fragen.md`](zehn_fragen.md) (Frage 2) und [`was_ist_pcmms.md`](was_ist_pcmms.md). Als
Beleg sind unten weitere Stellen herangezogen, vor allem aus dem Hauptteil des Arbeitspapiers; als eigene Abweichung
geführt sind davon Z. 860–861, Z. 5089–5091 und `CITATION.cff`. Eine vollständige Durchsicht ist das nicht. Ergebnis ist
die Liste in 4.2; 4.3 und 4.4 halten fest, was geprüft und nicht als Anspruchsänderung gewertet ist. Es wird nichts
umformuliert, und es gibt keinen neuen Wortlaut für Kurzfassung, Abstract oder Einleitung. Die Liste ist in getrennten
Lesedurchgängen derselben Sitzung (Claude Code, ohne Beteiligung des Autors) an den Fundstellen gegengelesen; die
Einordnung unter 4.2, 4.3 oder 4.4 folgt diesen Durchgängen.

### 4.1 Worin die Stellen übereinstimmen

- Keine neue Physik, kein Effektanspruch (Z. 144, Z. 225; README Z. 30–31; `neuheitsgrad.md` Z. 195).
- Das Zeitmittel ist durch den Schwerpunktsatz festgelegt und dient der Kontrolle; es ist nicht Zielgröße und kein
  Ergebnis (Z. 145–146, Z. 606–616, Z. 949–950, Z. 5181–5183; `neuheitsgrad.md` Z. 173; README Z. 20–21; ausführlicher
  außerhalb der sieben Stellen: Z. 88–90 und `neuheitsgrad.md` Z. 110–114). Welche Größe als Kontrollgröße ausgewertet
  wird, ist uneinheitlich (4.3).
- Der mögliche Beitrag ist methodisch und eng; die Bausteine sind bekannt (Z. 144–145, Z. 595–596, Z. 922–935;
  `neuheitsgrad.md` Z. 176 und Z. 186; außerhalb der sieben Stellen: `neuheitsgrad.md` Z. 48–49).
- Ob eine Lücke besteht, ist offen; „nicht gefunden“ ist ein Suchbefund (Z. 148–149, Z. 597, Z. 937–940, Z. 5192–5194;
  `neuheitsgrad.md` Z. 192–193).
- An keiner der sieben Stellen heißt die Präregistrierung registriert oder eingefroren; wo sie genannt ist, steht
  „Entwurf“.

### 4.2 Abweichungen, die den Anspruch ändern

**BA-1 Die Neuheit der Nullgröße als Prüfmittel steht einmal als Tatsache da, sonst als offen.** In Kapitel 2 heißt es:
„neu ist hier allein die Verwendung dieser Basislinie als Prüfmittel gegen die Messkette“ (Z. 860–861). Der Satz steht
im Abschnitt „Kraftverläufe an der Auflage schwingungsangeregter Systeme“, außerhalb der sieben Stellen, trifft aber
dieselbe Aussage. Dagegen stehen „ist nicht recherchiert; er ist deshalb als methodischer Baustein mit ungeklärter
Neuheit zu lesen“ (Z. 5193–5194), „ohne systematische Recherche offen“ (Z. 148–149) und die Einordnung, die für die
nicht ausgewertete Metrologie- und Wägetechnikliteratur festhält: „dort liegt die Verwendung einer bekannten Last als
Kontrolle nahe“ (Z. 957–961). Der Versionshinweis führt die Lücken- und Beitragsaussagen in Kapitel 2 als auf
Suchbefunde zurückgenommen (Z. 355–358); Z. 860–861 ist davon nicht erfasst. Die Stelle ist nicht geändert und in der
Beschreibung des Pull Requests gemeldet.

**BA-2 Zielgrößen, Rangfolge und Kontaktregime.** Das Arbeitspapier führt vier Funktionale – Schiefe, Liftoff-Anteil,
Asymmetrieverhältnis, minimale Kontaktkraft – ohne Abstufung als Zielgrößen des Messrahmens, in „Beitrag dieser Arbeit“
als „primäre Zielgrößen“ (Z. 622–624; Kurzfassung Z. 91–96; Abstract Z. 172–176), und prüft sie nach seinem
Hypothesenteil einzeln (Z. 1929–1941). Der Gegenstand ist über die Auflage bestimmt, die „einseitig ist, also innerhalb
eines Zyklus abheben kann“ (Z. 79–80). README (Z. 14–17) und `overview.md` (Z. 52–55) ordnen die vier Funktionale der
Simulation zu; `neuheitsgrad.md` nennt die vier nicht zusammen, gibt aber die Rangfolge des Entwurfs v2 wieder
(`neuheitsgrad.md` Z. 157–159). Für die Messkampagne sind nach dem Entwurf der Präregistrierung v2 F_min − ⟨N⟩ und die
Harmonischen 1 bis 3 primär (H1, dort Z. 161), ebenso die Lage der Zeltspitze (H2, dort Z. 172); das Vorzeichen der
Schiefe ist sekundär (H4, dort Z. 196), das Asymmetrieverhältnis A beschreibend, der Liftoff-Bereich explorativ (E1,
dort Z. 215). Gegenstand ist dort der Körper, „solange er auf allen Auflagepunkten Kontakt hält“ (dort Z. 13–15); der
Arbeitspunkt hält Abstand zum Abheben (§5.3 (a), dort Z. 340–344), und der Liftoff-Bereich wird nicht konfirmatorisch
geprüft (dort Z. 139–140). Das Arbeitspapier nennt F_min − ⟨N⟩ und die Beschränkung auf den Dauerkontakt im Hauptteil
selbst (Z. 1855–1868, Z. 2299–2313), in den Beitragsaussagen nicht; die Harmonischen 1 bis 3 nennt es nirgends als
Zielgröße. Dass F_min − ⟨N⟩ nicht die minimale Kontaktkraft N_min der Beitragsaussagen ist (Bandbegrenzung, Mittelung
über Läufe, Bezug auf das Laufmittel statt auf M·g), erklärt nur das Arbeitspapier (Z. 1855–1870); die README nennt
beide Größen ohne Erklärung (dort Z. 14–17).

**BA-3 Was die Messung entscheidet.** Die Beitragsaussagen des Arbeitspapiers beschreiben einen Rahmen, in dem eine
Phasenabhängigkeit der Wellenform „nachgewiesen, begrenzt oder ausgeschlossen“ werden kann (Z. 693–695; Z. 966–968 mit
„beziffert“). Gemeint ist der Nachweis oberhalb der Auflösungsschwelle (Z. 518–521; Frage F2, Z. 1899–1902; Hypothesen
Z. 1929–1941), nicht die Abhängigkeit im Modell, die das Papier selbst nennt (Z. 130–131). Davon unabhängig weichen zwei
Punkte ab. Erstens geht „ausgeschlossen“ über den Endzustand „nachgewiesenes Nullergebnis mit oberer Schranke“ hinaus
(Z. 99–101, Z. 3565–3569); das Papier verlangt an anderer Stelle selbst, eine schwache Schranke (weite Schwelle bei
großem σ̂_ref) als solche zu berichten, „statt als Ausschluss“ (Z. 4957–4961). Zweitens weicht die Fassung als
Nachweisentscheidung von README und Entwurf v2 ab: Die README fragt, „wie“ die Phasenkonfiguration die zeitliche Form
der Kontaktkraft bestimmt (dort Z. 12–13), nicht ob. Im Entwurf der Präregistrierung v2, auf den README und
`neuheitsgrad.md` für die Messkampagne verweisen, ist die Abhängigkeit „keine Hypothese“ (Entwurf v2, Z. 118–119),
geprüft werden quantitative Vorhersagen aus Messungen an der Apparatur (H1, H2), und ε_phys ist für die Wellenformgrößen
ersetzt (Entwurf v2, Z. 97–98).

**BA-4 Festgelegte Kriterien gegenüber einer Präregistrierung im Entwurf.** Das Kapitel „Fazit“ sagt im Abschnitt
„Zusammenfassung der Arbeit“ über die Arbeit: „Sie legt die Kriterien fest, bevor Daten vorliegen, und macht sie damit
der nachträglichen Anpassung unzugänglich“ (Z. 5089–5091, außerhalb der sieben Stellen). „Beitrag dieser Arbeit“ führt
eine Schwelle ε_phys und vier Endzustände „mit vorab festgelegten Kriterien“ (Z. 654–668), ohne die Präregistrierung
oder ihren Status zu nennen. Dagegen stehen `neuheitsgrad.md` §7 mit einer „Präregistrierung im Entwurf (v2, nicht
eingefroren; v1 als nicht extern registrierte Arbeitsfassung)“ (dort Z. 174), der Entwurf v2 als Entwicklungsversion mit
vorläufigen Arbeitsfestlegungen (dort Z. 4 und Z. 62–66), der ε_phys für die Wellenformgrößen ersetzt (dort Z. 97–98),
und das Arbeitspapier selbst, nach dem die Schwellen nicht beziffert sind (Z. 5007–5010, Z. 2140–2141). Innerhalb der
sieben Stellen ist das ein Unterschied im Status – im Papier definierte Regeln gegenüber einer noch nicht eingefrorenen
Festlegung –, kein Widerspruch im Wortlaut. Die Aussage in Z. 5089–5091 geht darüber hinaus; sie ist nicht geändert und
in der Beschreibung des Pull Requests gemeldet.

**BA-5 Wo der mögliche Beitrag liegt.** Kurzfassung und Abstract nennen zwei Elemente: die Nullgröße als Prüfmittel
gegen die eigene Messkette und die Wellenform der Kontaktkraft als entworfene Zielgröße einer Phasensteuerung innerer
Massen (Z. 144–148, Z. 225–228). Das Fazit verweist auf alle Elemente von „Beitrag dieser Arbeit“ und hebt die Nullgröße
als Prüfmittel hervor; sie ist dort „der konstruktive Kern“ (Z. 5177–5185; ebenso, außerhalb der sieben Stellen, „Der
zentrale methodische Zug“, Z. 4837–4838). `neuheitsgrad.md` §8 nennt dagegen die konkrete experimentelle Fragestellung,
die „Attribution über die Phasensteuerung“ und die methodisch kontrollierte Messung der Kraftwellenform (dort
Z. 188–190). Die Nullbasis ist dort eines von acht Gliedern der Zusammenstellung (dort Z. 173) und in §8 nicht genannt;
ihre Funktion als Kontrollkanal beschreibt §5 (dort Z. 110–114, außerhalb der sieben Stellen), und als „methodische
Behauptung“ gilt dort die Wellenformstatistik der unilateralen Kontaktkraft als Zielgröße (dort Z. 157, außerhalb der
sieben Stellen). Ein so benanntes Element führt das Arbeitspapier nicht: Sein Rahmen endet beim Endzustand
„nachgewiesene Abhängigkeit ohne Mechanismusbehauptung“ (Z. 100–101), eine kausale Auslegung nimmt es nur vor, wenn
unabhängige Belege artefaktbasierte Erklärungen ausschließen (Z. 4947–4951), und die Sache steht dort unter den neun
Beiträgen als Trennung von Artefakten durch das Versuchsdesign (Z. 676–681); `neuheitsgrad.md` schränkt selbst ein: „die
Zuordnung selbst ist damit noch nicht gezeigt“ (dort Z. 104). Die Stellen setzen den Kern des möglichen Beitrags
verschieden an; das ändert, was als Beitrag vorgetragen wird.

### 4.3 Verkürzungen, uneinheitliche Gewichtung und uneinheitliche Einzelaussagen

Die Punkte unten ändern nach der Lesart dieser Notiz den Anspruch nicht: Entweder steht die vollständige oder die
einschränkende Aussage auch im Arbeitspapier selbst, oder die Stellen zählen dieselben Elemente verschieden. Wo der
Wortlaut einer Stelle trotzdem weiter reicht oder einer anderen widerspricht, ist es beim Punkt vermerkt.

- **Ruhender Körper.** Die Einordnung führt ihn als eines von vier Merkmalen der Konstellation des Suchbefunds (Z. 948),
  `neuheitsgrad.md` nennt ihn den entscheidenden Unterschied (dort Z. 83–85) und führt ihn in der Zusammenstellung (dort
  Z. 173), die README beginnt mit ihm (dort Z. 11). Die Beitragsaussagen von Kurzfassung, Abstract, „Beitrag dieser
  Arbeit“ und Fazit grenzen ohne ihn ab (Z. 146–148, Z. 625–629). Sie verkürzen; der Sache nach enthält das Papier das
  Merkmal (Z. 948, Z. 1403–1405, Z. 2192–2194; ohne äußere Aktuierung Z. 2244–2246). Dem Wortlaut nach ist die
  Kurzformel aber um dieses Merkmal weiter als die Konstellation, für die das Papier einen Suchbefund angibt. „Ruhend“
  ist an den sieben Stellen nicht definiert und steht neben einer Auflage, die abheben kann (Z. 79–80); am nächsten
  kommen die Voraussetzung der Basislinie (Z. 1403–1405) und [`einordnung.md`](einordnung.md) (dort Z. 69–70:
  „stationärer Betrieb mit begrenzter Bewegung des Körpers, ohne gerichtete Nettodrift“).
- **Zahl der Elemente.** Zwei in Kurzfassung und Abstract, neun Punkte unter „Die wesentlichen Beiträge“ in „Beitrag
  dieser Arbeit“ (Z. 602–691), vier Merkmale in der Einordnung, acht in `neuheitsgrad.md` §7 (dort Z. 171–174).
  Bahnprofil und Präregistrierung im Entwurf zählen unter den sieben Stellen nur dort zur Zusammenstellung.
- **Reichweite der Kontrolle.** „Beitrag dieser Arbeit“ schließt mit dem Satz, die Apparatur werde „fortlaufend gegen
  eine Größe qualifiziert …, deren Wert bekannt ist“ (Z. 695–696); die Einordnung hat ihn gegen Ende (Z. 968–969). Die
  README sagt: „Umgekehrt qualifiziert ein unauffälliges Zeitmittel die dynamische Messkette nicht“ (dort Z. 25–26). Die
  Grenze steht im Arbeitspapier in Kurzfassung (Z. 138–140), Abstract (Z. 219–221), „Beitrag dieser Arbeit“ (Z. 614–616)
  und Fazit (Z. 5187–5190); ohne Einschränkung bleibt nur „Einordnung und mögliche Lücke“. Uneinheitlich ist außerdem,
  was geprüft wird: „Auswertekette“ (Z. 90, Z. 614, Z. 950, Z. 5183), „Messkette“ (Z. 146, Z. 959) oder „Apparatur“
  (Z. 94, Z. 695, Z. 968). Uneinheitlich ist auch die Kontrollgröße selbst: in „Beitrag dieser Arbeit“ die Differenz der
  Zeitmittel zweier Zustände (Z. 610–612), in README und `overview.md` das Zeitmittel ⟨N⟩ gegen M·g (README Z. 20–25;
  `overview.md` Z. 48–51). Ein Fehler, der beide Zustände gleich trifft, besteht die Differenzkontrolle; das sagen das
  Arbeitspapier (Z. 4866–4869) und die README (dort Z. 27) selbst.
- **Drift.** Kurzfassung (Z. 88–90), „Beitrag dieser Arbeit“ (Z. 612–614) und `neuheitsgrad.md` (dort Z. 112–113) nennen
  Drift unter dem, worauf die Kontrolle prüft; das Papier sagt, Drift werde „von der Kontrollgröße erfasst“
  (Z. 2672–2673), trennt die Kontrollgröße aber zugleich durch Verschachtelung und Randomisierung von Drift
  (Z. 1490–1493). Die README zählt Drift zu dem, was trotz unauffälligem Zeitmittel gesondert zu charakterisieren ist
  (dort Z. 26–27).

### 4.4 Geprüft und nicht als Abweichung gewertet

- „nachgewiesen, begrenzt oder ausgeschlossen“ (Z. 694–695) gegenüber „nachgewiesen, beziffert oder ausgeschlossen“
  (Z. 967–968).
- „möglicher Beitrag“ (Z. 144, Z. 5177) gegenüber „Der Beitrag der Arbeit ist“ (Z. 965) und „Die wesentlichen Beiträge
  sind“ (Z. 602); der Vorbehalt steht jeweils im Text davor.
- „ohne systematische Recherche offen“ (Z. 149, Z. 597, Z. 710–711, Z. 940) gegenüber „ist nicht recherchiert“
  (Z. 5193); nach Anhang C wurde in Metrologie und Wägetechnik nicht gesucht (Z. 5888–5890).
- „Primär“ steht vor vier verschiedenen Dingen: der zeitaufgelösten Kontaktkraft im Gegensatz zur Körperbewegung
  (`neuheitsgrad.md` Z. 171–172), den vier Funktionalen im Gegensatz zum Zeitmittel (Z. 622–624), dem Rang nach dem
  Entwurf v2 (README Z. 16–17) und der Abweichung gegen die Referenz im Gegensatz zur Absolutkraft (README Z. 19–20;
  `overview.md` Z. 50–51). Der Zusammenhang klärt jede Verwendung; verwechselbar bleibt Z. 623 neben der README.
- Der Satz „nur die minimale Kontaktkraft trägt eigenständige Information“ (Z. 120–121) ist ein Modellbefund, „F_min ist
  … nicht der Neuheitskern“ (`neuheitsgrad.md` Z. 155–156) eine Aussage zur Neuheit; ein Widerspruch ist das nicht.

### 4.5 Die Formel G-4, gemessen am Repository

Gemessen ist die Formel in der Wiedergabe des Auftrags (Abschnitt 0); der Text des Gutachtens lag nicht vor.

**Was sie trifft.** Als Rekombination bekannter Bausteine beschreibt sich das Projekt selbst (`neuheitsgrad.md`
Z. 48–49; sinngleich im Arbeitspapier, Z. 922 und Z. 934–935). Der Verzicht auf einen Effektanspruch steht mit keiner
der sieben Stellen im Widerspruch (Z. 144, Z. 225, Z. 597–598; README Z. 30–31). „Ruhender Körper“ und „Nullkontrolle“
sind Begriffe des Repositorys. In grober Form deckt die Formel die vier Merkmale der Einordnung: die Wellenform als
Ziel, die Phasensteuerung eines Mehrmassensystems, den ruhenden Körper und die Nullkontrolle.

**Wo sie den Anspruch ändert.**

- **Status.** Die Formel trägt weder den Stand „prä-experimentell“ (Z. 80–81) noch den Vorbehalt des „möglichen“
  Beitrags bei offener Recherche (Z. 144–149, Z. 5192–5194). Sie beschreibt eine methodische Kontrolle als gegeben, die
  im Repository Auslegung, Entwurf und Simulation ist. Wo der Vorbehalt im Arbeitspapier im Satz fehlt (Z. 602, Z. 965),
  steht er im Text davor (4.4); die Formel steht allein.
- **Präregistrierung als methodische Kontrolle.** Die Formel nennt sie ohne Zusatz. Im Repository ist v1 eine nicht
  extern registrierte Arbeitsfassung und v2 ein Entwurf, „nicht eingefroren, nicht registriert“ (`neuheitsgrad.md`
  Z. 174; Entwurf v2, Z. 4 und Z. 62–66); Einfrieren und Registrierung sind in AP-14 offen
  ([`arbeitsplan_status.md`](arbeitsplan_status.md)). Die Beitragsstellen des Arbeitspapiers nennen die Präregistrierung
  nicht.
- **Gewichtung der Nullgröße.** Das Arbeitspapier führt sie als erstes von zwei Beitragselementen (Z. 144–148), als
  konstruktiven Kern (Z. 5177–5185) und als zentralen methodischen Zug (Z. 4837–4838, Kapitel „Diskussion“), mit
  ausdrücklich ungeklärter Neuheit (Z. 5192–5194). In der Formel ist die „Nullkontrolle“ eines von drei Gliedern der
  methodischen Kontrolle; ihre Funktion als Prüfmittel der eigenen Auswertekette und der Neuheitsvorbehalt fehlen. Diese
  Gewichtung entspricht der von `neuheitsgrad.md` (BA-5).
- **Ziel.** Eine Charakterisierung als Ziel ist beschreibend und mit README und `neuheitsgrad.md` §8 vereinbar. Die
  Beitragsstellen des Arbeitspapiers nennen dagegen einen Messrahmen mit Entscheidungsstruktur, Äquivalenzlogik und
  Nullausgang (Z. 597–598, Z. 654–674); nichts davon nennt die Formel.

**Was ihr fehlt, ohne den Anspruch zu ändern.**

- **Zielgrößen.** Die Formel, wie der Auftrag sie wiedergibt, nennt keine; die Charakterisierung der Wellenform deckt
  auch F_min − ⟨N⟩ und die Harmonischen. Schiefe und Liftoff nennt nach dem Auftrag die Tabelle des Gutachtens (am Text
  nicht geprüft); für sie gilt BA-2: Nach dem Entwurf v2 sind F_min − ⟨N⟩, die Harmonischen 1 bis 3 und die Lage der
  Zeltspitze primär, das Vorzeichen der Schiefe sekundär, der Liftoff-Bereich explorativ, und der Versuch V1 verlangt
  Dauerkontakt.
- **Phasensteuerung.** Die Formel nennt sie als Baustein; eine Tatsachenaussage, die Phasenlage steuere die Wellenform,
  enthält sie in der Wiedergabe des Auftrags nicht. Als Modellaussage ist gedeckt, dass die Phasenlage die Wellenform
  formt (Entwurf v2, Z. 118–119; Arbeitspapier Z. 5096–5098 und Z. 5117–5119); die Zahlen dazu sind Simulation. Nicht
  gezeigt ist die Zuordnung beobachteter Änderungen zur Phasenvariation allein (`neuheitsgrad.md` Z. 100–104).
- **Bausteine.** Es fehlen die Einseitigkeit des Kontakts, die inneren Massen eines geschlossenen Körpers (Z. 943–947)
  und das Bahnprofil, das unter den sieben Stellen nur `neuheitsgrad.md` als Merkmal führt (dort Z. 171). Die Formel
  verliert Abgrenzungsschärfe, erhebt aber keinen weiteren Anspruch.
- **Begriff.** „Kontaktkraft“ steht ohne Bezug auf die Kraftverschiebung gegen die Referenz (`overview.md` Z. 50–51;
  README Z. 19–20). In der Formel bezeichnet das Wort einen Baustein, nicht die ausgewertete Größe. Auch die
  Kurzaussagen des Repositorys nennen die Kontaktkraft ohne diesen Bezug, dort sogar als Zielgröße (Z. 146–148;
  `neuheitsgrad.md` Z. 172).

**Dieselbe Lesart im Repository.** [`CITATION.cff`](../CITATION.cff) führt „preregistration“ als Schlagwort ohne Status
(dort Z. 19), nennt als Zielgrößen „Schiefe, Liftoff-Anteil, Asymmetrieverhältnis und Minimalkraft“ und zählt zum
Enthaltenen die „Präregistrierung“ (dort Z. 27–29). Die Datei liegt außerhalb der sieben Stellen und ist nicht geändert;
die Stelle ist in der Beschreibung des Pull Requests gemeldet.

Die Formel wird nicht übernommen, und diese Notiz setzt keine andere an ihre Stelle.

### 4.6 Offen, nicht entschieden

- D-3, die Neuheitsformulierung der Armführung (Ingenieurbeitrag ohne Prinzipneuheit oder Ergänzung von
  `neuheitsgrad.md` um die Konstruktionsform), bleibt Entscheidung des Autors
  ([`arbeitsplan_status.md`](arbeitsplan_status.md)).
- Ob Linie A künftig von der einzelnen einseitigen Auflage her beschrieben wird (README Z. 11; Kurzfassung Z. 77–80)
  oder vom Messrahmen mit Rundum-Kontaktkette (AP-27, Konzept;
  [`konzepte/nadelrahmen_dreimassenkoerper_2026-10.md`](konzepte/nadelrahmen_dreimassenkoerper_2026-10.md)), ist offen
  und bleibt Entscheidung des Autors. [`einordnung.md`](einordnung.md) nennt schon beides (dort Z. 69). Die Frage
  berührt BA-2 und den Punkt „Ruhender Körper“ in 4.3 und ist hier nur vermerkt.

## 5. Referenzfälle

Die Frage ist, was ein Dritter heute allein aus dem Repository nachrechnen kann. Es entsteht keine neue Seite, es gibt
keine neuen Daten und keinen Aufruf an Dritte; ob aus der Liste eine Seite zum Nachrechnen wird, entscheidet der Autor
(E-3). Alle Zahlen sind Simulation. Das Zeitmittel (`F_mean`, ⟨N⟩) ist in jedem Fall Kontrollgröße mit dem Sollwert
M·g = 6,3765 N, kein Ergebnis.

### 5.1 Was vorliegt

- **Parametersatz:** [`data/README.md`](../data/README.md) (Z. 15–23), gleichlautend im Abschnitt „Simulationsstand“
  der [README](../README.md): M = 0,650 kg, f = 10 Hz, Egg-Profil, K = 10⁴ N/m, C = 16 N·s/m, RK4 mit Δt = 50 µs,
  15 s je Konfiguration, ausgewertet die letzten 10 s.
- **Rechenwege:** die Referenz-Engine (`code/pcmms_v3a_phasen_sweep.py`, skalar, RK4 mit festem Schritt), ihre
  vektorisierte Fassung für den Feinsweep (`code/finesweep.py`), die analytische Lösung des Kontaktasts
  (`code/linear_solver.py`), der ereignisgenaue Löser (`code/ereignisloeser.py`) und das Auslegungswerkzeug
  (`code/auslegung.py`).
- **Sollwerte:** die drei Engine-Datensätze in `data/` (`sweep_19x19.csv` mit 361 und `finesweep_2deg_120_240.csv` mit
  441 Punkten am Referenzsatz, `sweep_7x7_sinus.csv` mit 49 Punkten und Sinusprofil; daneben liegen dort die
  Regime-Langläufe und die Attraktorkarten des V1-Kandidaten, siehe 5.4) und Tests mit festgehaltenen Zahlen
  (`tests/test_ereignisloeser.py`, `tests/test_auslegung.py`). Am Punkt (120°, 240°) binden drei Tests denselben Wert
  F_min = 5,330390 N an zwei weitere Rechenwege: den ereignisgenauen Löser auf 1·10⁻⁶ N (`tests/test_ereignisloeser.py`,
  Z. 51) und das Auslegungswerkzeug auf 5·10⁻⁷ N (`tests/test_auslegung.py`, Z. 66 und Z. 498).
- **Nachweisarchiv:** [`rechnungen/`](../rechnungen/README.md) mit Prüfskripten und abgelegten Ausgaben, etwa
  `rechnungen/engine/validate_eng_ausgabe.txt`, und die unabhängige Prüfung des linearen Lösers (PR #4) in
  `docs/arbeitspapier/gegenprobe_2026-09-26/`, dort neben der Gegenprobe zum Einzelmodul. Die README des
  Repository-Stamms nennt das Archiv „für den Einstieg nicht nötig“ (dort Z. 76).
- **Anleitung:** der Block „Nachrechnen“ der README (dort Z. 199–214) mit Aufrufen und einigen Laufzeiten; der
  Zahlennachweis der Präregistrierung v2 ([`praeregistrierung_v2_anhang.md`](praeregistrierung_v2_anhang.md), Abschnitt
  Z, ab Z. 1534) mit einem Befehl je Zahl; für die Attraktorkarten der Abschnitt „Reproduktion und Dateien“ in
  [`einzugsgebiete_v1_kandidat.md`](einzugsgebiete_v1_kandidat.md) (ab Z. 560, Laufzeiten 25 s bis 63 min).

### 5.2 Vorschlag: fünf Referenzfälle

Aufrufe vom Repository-Stamm, nach `pip install -r code/requirements.txt`. R-1 ist in dieser Sitzung nachgerechnet, die
übrigen Fälle sind aus Code, Tests und Dokumenten gelesen und nicht ausgeführt.

**R-1 Dauerkontakt am Triphasik-Punkt (120°, 240°), Referenz-Engine**

- Konfiguration: Referenzsatz, Standardstart (z₀ = −M·g/K), Δt = 50 µs, Fenster 5–15 s.
- Größen und Sollwerte: `F_mean` 6,376500 N (Kontrollgröße), `F_skew` 0,066794, `liftoff` 0, `F_max` 7,491922 N,
  `F_min` 5,330390 N, `peak_ratio` (Asymmetrieverhältnis A) 1,066257.
- Quelle: [`data/finesweep_2deg_120_240.csv`](../data/finesweep_2deg_120_240.csv), Zeile 222 (Spaltennamen in Zeile 1).
  Die Zeile stammt aus `finesweep.py`; der Punkt liegt nicht auf dem 19×19-Raster der Engine.
- Aufruf vom Repository-Stamm:

  ```bash
  python3 -c "import sys; sys.path.insert(0, 'code'); import pcmms_v3a_phasen_sweep as e; print(e.simulate_point(120.0, 240.0))"
  ```

  Eine Kommandozeilenoption für einen Einzelpunkt hat die Engine nicht; der Import allein startet keine Rechnung und
  schreibt keine Ergebnisdatei.
- Laufzeit: „Engine: ca. 2 s“ je Punkt (`code/linear_solver.py`, Z. 42); der Kopf der Engine
  (`code/pcmms_v3a_phasen_sweep.py`, Z. 36) und die README (dort Z. 214) nennen für die 361 Punkte dagegen 30 bis 60
  Minuten, also rund 5 bis 10 s je Punkt. In dieser Sitzung rund 1 s.
- Zulässige Abweichung: Gleichheit auf die sechs Nachkommastellen der CSV, also ±5·10⁻⁷. Herkunft ist die Rundung der
  Datei (`float_format='%.6f'`); eine Toleranz für die Nachrechnung legen die README-Dateien und `code/` nicht fest
  (5.3). Zeitschritt, Fenster und Start sind fest. Der Punkt liegt im Hauptgebiet des Kontaktasts, in dem die Engine in
  allen Proben auf dem Kontaktast landet (`code/linear_solver.py`, Z. 21–25; README, Z. 143–148); allgemein folgt aus
  einem liftoff-freien Orbit keine Eindeutigkeit (R-4). Für diesen Punkt hält `rechnungen/engine/PROTOKOLL.md`
  (Z. 73–86) fest, dass die fünf dort geprüften Starts, der halbe Zeitschritt und der ereignislokalisierende Löser des
  Nachweisarchivs (`rechnungen/engine/el_solver.py`, nicht `code/ereignisloeser.py`) dieselben Kenngrößen geben, auf die
  dort angegebenen Stellen (Schiefe 0,066794; F_min 5,3304 N; F_max 7,4919 N).
- **Nachgerechnet am 10.11.2026:** alle sechs Spalten auf sechs Nachkommastellen gleich; größte Abweichung vor der
  Rundung 1,8·10⁻⁷ (`F_min`); `F_mean` − M·g = 6·10⁻¹³ N. Der Punkt ist dreimal gerechnet worden: zweimal mit einem
  Prüfskript, das die sechs Spalten mit der CSV vergleicht und die Rechenzeit um den Funktionsaufruf misst (1,0 s und
  0,9 s, ohne Programmstart), einmal mit dem oben angegebenen Aufruf (Python 3.13.18, numpy 2.5.4, scipy 1.18.1,
  4 Kerne). Mehr als diesen einen Punkt lässt der Auftrag nicht zu; es gab keinen Sweep.

**R-2 Analytische Lösung gegen die drei Datensätze**

- Konfiguration: Referenzsatz für die 802 Punkte der beiden Egg-Dateien; die 49 Punkte von `sweep_7x7_sinus.csv` rechnet
  der Löser mit dem Sinusprofil und der aus diesen Daten rekonstruierten Amplitude (RTOP + RBOT)/2
  (`code/linear_solver.py`, Z. 66 und Z. 254; [`data/README.md`](../data/README.md), Z. 79–84), insoweit kein
  unabhängiger Sollwert (5.4). Verglichen werden die 442 liftoff-freien Punkte (12 von 361, 400 von 441, 30 von 49).
- Größen und Sollwerte: Einteilung liftoff-frei oder abhebend ohne Abweichung; größte Abweichung von F_min, F_max,
  Schiefe und A höchstens 6·10⁻⁶; Schlusszeile „Ergebnis: bestanden“.
- Quelle: `code/linear_solver.py`, Z. 45–46; [`README.md`](../README.md), Z. 137.
- Aufruf: `python3 code/linear_solver.py --validate`
- Laufzeit: ca. 5 s (README, Z. 204).
- Zulässige Abweichung: Der Code lässt 1·10⁻⁴ zu (N bzw. dimensionslos; 1·10⁻⁵ N für |`F_mean` − M·g|;
  `code/linear_solver.py`, Z. 266); die engere Angabe 6·10⁻⁶ steht nur im Text. Herkunft: Die analytische Lösung wird an
  denselben Stichproben gebildet wie in der Engine (Δt = 50 µs, 2000 je Periode; `code/linear_solver.py`, Z. 42–43), die
  Werte sind deshalb direkt vergleichbar. Übrig bleiben der RK4-Fehler der Engine bei diesem Zeitschritt („einige 1e-6“,
  `tests/test_ereignisloeser.py`, Z. 73–74) und bei den beiden Egg-Dateien die Rundung auf sechs Nachkommastellen;
  `sweep_7x7_sinus.csv` ist ungerundet abgelegt.
- Hinweis: Die 409 Liftoff-Punkte gehen nur als Einteilung ein. Geprüft wird gegen die abgelegten Werte; im
  Liftoff-Bereich hängen sie von der Startbedingung ab (R-4).

**R-3 Zeltkurve im Kontaktast (Schnitt φ₂ = 100° … 140° bei φ₃ = 240°)**

- Konfiguration: Referenzsatz, 21 Punkte, analytische Lösung.
- Größen und Sollwerte: F_min 5,3304 N bei 120°, 0,7677 N bei 100°, 1,6176 N bei 140°; 2°-Sekanten an der Spitze 0,2124
  und 0,1952 N je Grad; Spannweite 4,5627 N (von `--section` nicht gedruckt: Differenz der Werte bei 120° und 100°).
- Quelle: [`praeregistrierung_v2_anhang.md`](praeregistrierung_v2_anhang.md), Zahlennachweis, Z. 1547; die Spannweite
  hält außerdem `tests/test_auslegung.py`, Z. 164, über das Auslegungswerkzeug fest (±6·10⁻⁵ N).
- Aufruf: `python3 code/linear_solver.py --section`
- Laufzeit: nicht angegeben; der Löser braucht „ca. 1 ms je Punkt“ (`code/linear_solver.py`, Z. 42).
- Zulässige Abweichung: die letzte gedruckte Stelle (±5·10⁻⁵), für die Spannweite als Differenz zweier gedruckter Werte
  ±1·10⁻⁴. Das folgt aus dem Ausgabeformat; festgelegt ist im Repository nur die Toleranz der Spannweite im Test
  (±6·10⁻⁵ N). Die README nennt für dieselbe Kurve ≈ 0,23 und ≈ 0,19 N je Grad; das sind die Sekanten über 20°, nicht
  die über 2°.

**R-4 Satelliteninsel (35°, 116°), ereignisgenau – Fall im Liftoff-Bereich**

- Konfiguration: Referenzsatz; zwei Zustände am selben Punkt: Kontaktorbit (Start auf dem linearen Orbit) und
  Hüpfzustand (vom Standardstart aus).
- Größen und Sollwerte: Kontaktorbit mit Liftoff 0, F_min 0,3665 N, F_max 19,812 N, Schiefe 0,82305; Hüpfzustand mit
  Liftoff-Anteil 75,8154 %, F_max 39,473 N, Schiefe 1,69813.
- Quelle: `tests/test_ereignisloeser.py`, `test_satelliteninsel_bistabil`, Z. 101–122.
- Aufruf: `python3 -m pytest tests/test_ereignisloeser.py::test_satelliteninsel_bistabil -q` oder
  `python3 code/ereignisloeser.py --point 35 116 --orbit`
- Laufzeit: Kommandozeile ca. 5 s (README, Z. 207); für den einzelnen Test nicht angegeben.
- Zulässige Abweichung: die Toleranzen des Tests (F_min ±1·10⁻⁴ N, F_max ±1·10⁻³ N, Schiefe ±1·10⁻⁵, Liftoff-Anteil
  ±1·10⁻⁴ Prozentpunkte). Herkunft: „letzte angegebene Stelle der Referenz, höchstens 0,1 %“ (Kopf von
  `tests/test_ereignisloeser.py`, Z. 5).
- **Hinweis.** Der Punkt liegt im Liftoff-Bereich. Dort ist die Karte nicht eindeutig: Es gibt mehrere stabile
  Zustände, und welcher erreicht wird, hängt von der Startbedingung ab ([`data/README.md`](../data/README.md),
  Z. 54–58; README, Z. 148–153). Als Referenzfall taugt der Punkt deshalb nur mit beiden Zuständen und ihren Starts.

**R-5 V1-Kandidat der Auslegung – andere Parameter als der Referenzsatz**

- Konfiguration: Restmasse 0,350 kg, drei Module zu je 0,100 kg, Hub 8 mm, 10 Hz, K = 1,5·10⁶ N/m, ζ = 0,05
  (`code/auslegung.py`, Z. 193), Geometrie G0 mit R_c = 100 mm und ρ₀ = R_c/2 (Vorgabe des Werkzeugs, dort Z. 140–141);
  die Zellreserve gilt nur für diese Geometrie.
- Größen und Sollwerte: Spannweite der Zeltkurve ohne Bandbegrenzung 0,560 N (bandbegrenzt auf k ≤ 12: 0,588 N);
  kleinste Zellreserve 0,41137, am Schnittpunkt (100°, 240°); Kontakteigenfrequenz 241,8 Hz.
- Quelle: `tests/test_auslegung.py`, Z. 242–243 (Spannweite über die Python-Schnittstelle, ±5·10⁻⁴ N, dort an der
  Geometrie „zentral“ gerechnet, Z. 231; bei symmetrischer Lage ist die Summenkraft nach dem Kopf des Werkzeugs
  dieselbe, `code/auslegung.py`, Z. 19–20) und Z. 494–495 (Zellreserve und Eigenfrequenz über die Kommandozeile, ±1·10⁻⁵
  und ±0,05 Hz).
- Aufruf: `python3 code/auslegung.py --candidate --json`; ohne `--json` zeigt die Textausgabe Reserven nur in Prozent
  mit einer Nachkommastelle (`code/auslegung.py`, Z. 701–702).
- Laufzeit: ca. 2 s (README, Z. 206).
- Zulässige Abweichung: die Toleranzen der Tests (Spannweite ±5·10⁻⁴ N, Zellreserve ±1·10⁻⁵, Eigenfrequenz ±0,05 Hz).
  Herkunft: die letzte angegebene Stelle der Referenzzahlen aus der Nachrechnung 10/2026 (Kopf von
  `tests/test_auslegung.py`, Z. 3–7; eine halbe Einheit bei Spannweite und Eigenfrequenz, eine ganze bei der
  Zellreserve). Zeitschritt, Fenster und Startbedingung gehen nicht ein, weil das Werkzeug die stationäre Lösung des
  linearen Modells im Dauerkontakt berechnet (`code/auslegung.py`, Z. 2–3).
- Hinweis: Auslegungswert eines angenommenen Aufbaus, keine Vorhersage für V1 (README, Z. 122–123).

### 5.3 Was einem Dritten heute fehlt

Die Liste hält fest, was auffiel; ein Auftrag folgt daraus nicht (E-3).

- Die Engine hat keinen dokumentierten Weg zu einem Einzelpunkt (die README nennt nur den vollen Sweep mit 30 bis
  60 Minuten), und kein Test ruft sie auf.
- Für die Nachrechnung der Engine gegen ihre eigenen Datensätze legen die README-Dateien und `code/` keine Toleranz
  fest. `finesweep.py --validate` druckt Rechenwert und CSV-Wert nebeneinander, ohne Urteil und mit Exit-Code 0. Im
  Nachweisarchiv ist eine solche Nachrechnung mit der skalaren Engine abgelegt: 70 Punkte des 19×19-Rasters, darunter
  alle 45 mit |δ| > 50 ppm, `F_mean` auf ≤ 4,9·10⁻⁷ N reproduziert (`rechnungen/symmetrie_randterm/PROTOKOLL.md`,
  Z. 376–381).
- `linear_solver.py --validate` gehört nicht zur Testsuite; der Lauf druckt die erreichten Höchstabweichungen, abgelegt
  ist davon nur das Urteil „bestanden“.
- Abgelegte Soll-Ausgaben gibt es, aber im Nachweisarchiv und nicht dort, wo ein Dritter beginnt.
- [`code/requirements.txt`](../code/requirements.txt) nennt fünf Pakete ohne Versionen; eine CI-Konfiguration gibt es
  nicht. Die dokumentierten Prüfumgebungen sind verschieden (Python 3.11 mit numpy 2.4 in
  [`abnahme_ap02_ap03.md`](abnahme_ap02_ap03.md), Python 3.13 mit NumPy 2.5 in
  [`ap11_ap12_ap13_software.md`](ap11_ap12_ap13_software.md)).
- Laufzeiten sind nur für einen Teil der Aufrufe angegeben.

### 5.4 Was sich nicht als Referenzfall eignet

- Einzelne Liftoff-Punkte der Engine-Datensätze: Ihr Wert hängt von Start, Zeitschritt und Rechenweg ab. Am Punkt (0°,
  0°) mit 75,8 % Liftoff weichen skalare und vektorisierte Fassung in `F_mean` um 1,7·10⁻⁴ N voneinander ab
  (`code/finesweep.py`, Z. 4–5); am Punkt (0°, 208,421°) hängt das Einschwingen schon von der letzten Stelle der
  Phasenangabe ab ([`data/README.md`](../data/README.md), Z. 46–48). Mit der skalaren Engine und den Phasen der CSV sind
  im Nachweisarchiv dagegen abgelegte Werte reproduziert: `F_mean` an 70 Punkten des 19×19-Rasters, darunter alle 45 mit
  |δ| > 50 ppm (`rechnungen/symmetrie_randterm/PROTOKOLL.md`, Z. 376–381), und am Punkt (0°, 208,421°) Zeitmittel,
  Liftoff-Anteil, Schiefe und F_max (`rechnungen/engine/PROTOKOLL.md`, Z. 113).
- `data/regime_2400s.csv` und `data/regime_2400s_dt2.csv`: Das Erzeugungsskript ist nicht überliefert.
- `data/sweep_7x7_sinus.csv`: Das erzeugende Skript liegt nicht im Repository; die Amplitude ist aus den Daten
  rekonstruiert. Als eigener Referenzfall eignet sich die Datei deshalb nicht; in R-2 geht sie nur mit diesem Vorbehalt
  ein.
- Die Attraktorkarten `data/einzugsgebiete_v1_kandidat*.csv` mit `code/einzugsgebiete.py` sind hier nicht betrachtet:
  Der Auftrag nennt sie nicht als Grundlage, und ihre Rechenzeiten reichen bis 63 Minuten
  ([`einzugsgebiete_v1_kandidat.md`](einzugsgebiete_v1_kandidat.md), Abschnitt 7).

## 6. Nicht bearbeitet

- **G-5, Messkampagne der Linie A konkretisieren.** Hardware (AP-01), Messkette (AP-06) und Schutzkonzept (AP-05, dort
  „Sicherheitskonzept“) hängen an Entscheidungen des Autors, aus denen kein Entwicklungsauftrag entsteht
  ([`arbeitsplan_status.md`](arbeitsplan_status.md), „Offene Entscheidungen des Autors“); diese Notiz plant dazu nichts.
- **G-7, Unabhängigkeit als Stärke darstellen.** Die Außendarstellung des Projekts ist nicht Gegenstand des Repositorys.
- **G-8, Gesamturteil.** Eine Gesamtnote ohne Bezugsklasse wird nicht geführt ([`neuheitsgrad.md`](neuheitsgrad.md) §3).

## 7. Offene Entscheidungen des Autors

Sie werden nur geführt; aus ihnen entsteht kein Entwicklungsauftrag. Sie stehen auch in
[`arbeitsplan_status.md`](arbeitsplan_status.md).

- **E-1** Sichtprüfung der bestätigten Arbeiten durch den Autor. Sie ist Voraussetzung für jede Aufnahme ins
  Literaturverzeichnis ([`neuheitsgrad.md`](neuheitsgrad.md) §9). Bestätigt ist bisher nur a): auf der Verlagsseite
  geprüft und im Volltext gelesen (Abschnitt 2.1). b) und c) sind nur am Registereintrag geprüft: Gelesen ist von c) der
  Abstract, vom Aufsatz b) nichts (nur der Abstract des Tagungsbeitrags von 2003). Unter die Sichtprüfung fallen sie
  erst, wenn die Verlagsseite bestätigt und der Text gelesen ist; ob und wann das nachgeholt wird, ist offen.
- **E-2** Arbeitspapier v2.6 mit eingearbeiteter Berichtigung (Variante B des Auftrags) jetzt, gebündelt mit der
  Primärquellenprüfung nach Nr. 42 der Offenen Punkte, oder vorerst nicht. Was dann zu ändern wäre, steht in Abschnitt 3
  (Berichtigung 3.1, Textvorschlag 3.2, Folgeänderungen 3.3).
- **E-3** Eine Seite mit Referenzfällen zum Nachrechnen anlegen oder nicht (Abschnitt 5).
- **E-4** Die Recherche im Strang vibrationsgetriebener Systeme mit inneren Massen beginnen oder weiter zurückstellen
  (AP-16).

Nicht vorweggenommen sind die offenen Entscheidungen D-2 bis D-6 der
[Abgleichnotiz vom 29.10.2026](abgleichnotiz_2026-10-29_v4.md), die Entscheidungen des Autors zu AP-01, AP-04 bis AP-07
und AP-18 und die Primärquellenprüfung nach Nr. 42 der Offenen Punkte.
