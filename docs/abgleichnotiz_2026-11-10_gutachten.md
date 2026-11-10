# PCMMS – Abgleichnotiz 2026-11-10: Gutachten und Gegenprüfung

Projekt: Phasenkontrollierte Mehrmassensysteme (PCMMS)
Autor: Matthias Früh, ORCID 0009-0005-9984-4207
Erstellt: 10.11.2026, Claude Code, nach Auftrag des Autors vom selben Tag
Status: Notiz, kein Arbeitsauftrag
Zuordnung: AP-16 (Literaturbestand); berührt die Offenen Punkte Nr. 21 und 42 des Arbeitspapiers
Lizenz: CC BY 4.0 (Ordner docs/, siehe LICENSE-CC-BY-4.0)

> **Vermerk (10.11.2026).** Abgleich am Repository-Stand `51f79a2` (`main`, 03.11.2026, PR #29). Zeilenangaben ohne
> Dateinamen („Z. …“) beziehen sich auf den Quelltext des Arbeitspapiers v2.5,
> [`arbeitspapier/PCMMS_Arbeitspapier_v2_5.tex`](arbeitspapier/PCMMS_Arbeitspapier_v2_5.tex), an diesem Stand. Auch die
> Zeilenangaben zu anderen Dateien gelten am Stand `51f79a2`. Der Pull Request, der diese Notiz anlegt, fügt Zeilen ein:
> in `README.md` nach Z. 62 eine, in [`overview.md`](overview.md) nach Z. 39 vier, in den Offenen Punkten des
> Arbeitspapiers nach Z. 92 eine und nach Z. 101 zwei; spätere Zeilen dieser Dateien stehen seither entsprechend tiefer.
> Die beiden abgeglichenen Texte und der Auftrag an Claude Code liegen nicht im Repository. Die Notiz ändert keine Zahl, keine
> Hypothese, keinen Code und keine Daten; Arbeitspapier (Quelltext und PDF) und Literaturverzeichnis bleiben
> unverändert (Variante A des Auftrags, kein Neusatz). Alle Zahlen des Repositorys sind Simulation; Messdaten
> existieren nicht.

## 0. Zweck und Quellenlage

Dem Autor lagen am 10.11.2026 zwei Texte vor: ein simuliertes Fachgutachten zu PCMMS (revidierte Fassung, Urteil
„Moderate Revision“) und eine Gegenprüfung dazu. Beide beziehen sich wechselseitig aufeinander; sie sind Hinweise, keine
unabhängige Begutachtung und kein Beleg. Diese Notiz hält fest, welche ihrer Aussagen den Repository-Stand treffen, und
ändert weder eine Regel noch einen Plan.

Die Texte selbst sind nicht abgelegt. Ihre Aussagen sind unter den Arbeitskennungen G-1 bis G-8 sinngemäß
wiedergegeben (Abschnitt 1). Grundlage der Wiedergabe ist der Auftrag des Autors vom 10.11.2026; die Texte selbst lagen
bei der Bearbeitung nicht vor. Die Kennungen E-1 bis E-4 in Abschnitt 7 bezeichnen offene Entscheidungen des Autors; sie
sind weder die Eingänge E-1 bis E-4 der [Abgleichnotiz vom 29.10.2026](abgleichnotiz_2026-10-29_v4.md) noch die
explorativen Fragen E1 bis E5 der [Präregistrierung v2 (Entwurf)](praeregistrierung_v2_entwurf.md).

## 1. Abgleich der Aussagen G-1 bis G-8 mit dem Repository

Jede Zeile ist am Stand `51f79a2` nachgeschlagen. Die Kernforderung beider Texte, einen Abschnitt zu Forschungsstand und
Beitrag in das Arbeitspapier einzufügen, trifft den Stand nicht: Kapitel, Abschnitt, Beitragsaussage in Kurzfassung und
Abstract und der Rechercheanhang sind vorhanden.

| Aussage | Befund | Fundstelle |
|---|---|---|
| **G-1** Im Arbeitspapier fehle ein Abschnitt zu Forschungsstand und Beitrag; der Literaturabgleich liege nur als eigenes Dokument vor. | **Trifft nicht zu.** Das Arbeitspapier v2.5 enthält das Kapitel „Stand der Forschung“ mit acht Abschnitten, darunter „Mehrkörperdynamik und phasengesteuerte Anregung“ und „Einordnung und mögliche Lücke“ mit vier Merkmalen der untersuchten Konstellation, und den Anhang „Dokumentation der Literaturrecherche“ (Anhang C). Richtig ist nur der engere Punkt, dass die Einträge des Literaturabgleichs vom 12.09.2026 nicht ins Arbeitspapier übernommen sind (unten, „Was zutrifft“). | `chap:stand` Z. 700–973, Abschnitte ab Z. 703, 721, 771, 825, 863, 885, 905, 920; „Mehrkörperdynamik …“ Z. 721–769; „Einordnung und mögliche Lücke“ Z. 920–973, Merkmale Z. 942–951; `app:recherche` Z. 5732–5895 |
| **G-2** Die Beitragsaussage fehle in Abstract und Einleitung oder sei unklar; sie sei zu „verdichten“. | **Trifft nicht zu.** Kurzfassung und Abstract schließen mit der Beitragsaussage (keine neue Physik; möglicher Beitrag methodisch und eng; Neuheit ohne systematische Recherche offen). Die Einleitung enthält den Abschnitt „Beitrag dieser Arbeit“ mit neun Punkten, das Fazit den Abschnitt „Methodischer Beitrag“. Ob die Aussagen untereinander widerspruchsfrei sind, ist eine andere Frage; sie ist in Abschnitt 4 geprüft. | Kurzfassung Z. 144–149; Abstract Z. 225–230; `sec:beitrag` Z. 590–696; Fazit „Methodischer Beitrag“ Z. 5175–5196 |
| **G-3** Abzugrenzen sei gegen „Olgac (2005)“, „Korendiy et al. (2026)“ und „Xiong & Xu (2015)“, mit einer Tabelle Zielgröße/Abgrenzung. | **Teilweise schon geführt, in dieser Form nicht übernommen.** „Korendiy et al. 2026“ führt Anhang C als nicht auffindbar; zitiert ist stattdessen Gurskyi, Korendiy et al. 2023. Arbeiten von Fang, Xu und Mitarbeitern stehen als bibliografisch ungeprüfte Kandidaten in Anhang C, in der Einordnung, im Neuheitsgrad-Dokument und in den Zehn Fragen. „Olgac“ kommt im Repository nicht vor. Die drei Angaben sind Gegenstand von Abschnitt 2; die Abgrenzungstabelle des Gutachtens wird nicht übernommen. | Verifikationstabelle Z. 5816; „Nicht aufgenommene Angaben“ Z. 5860–5862 und Z. 5863–5869; Zitat Gurskyi/Korendiy 2023 Z. 741–746, [`references.bib`](arbeitspapier/references.bib) Z. 214–223; [`einordnung.md`](einordnung.md) §5, Z. 165–174; [`neuheitsgrad.md`](neuheitsgrad.md) §10, Z. 236–240; [`zehn_fragen.md`](zehn_fragen.md) Z. 19–21; Suche nach „Olgac“ im ganzen Repository ohne Treffer |
| **G-4** Der Beitrag sei eine Rekombination bekannter Bausteine (Phasensteuerung, Mehrmassensystem, Kontaktkraft) unter methodischer Kontrolle (ruhender Körper, Nullkontrolle, Präregistrierung); Ziel sei die Charakterisierung der Wellenform, nicht die Entdeckung eines neuen Effekts. | **Nicht übernommen; am Repository gemessen.** Die Formel trifft den Verzicht auf einen Effektanspruch und die Selbstbeschreibung als Rekombination. Sie ändert den Anspruch beim Status der Präregistrierung, bei der Gewichtung der Nullgröße und beim Ziel; Zielgrößen nennt erst die Tabelle des Gutachtens. | Abschnitt 4.5 |
| **G-5** Die Messkampagne der Linie A sei zu konkretisieren (Hardware, Kanalplan, Schutzkonzept). | **Nicht Teil dieses Abgleichs.** | Abschnitt 6 |
| **G-6** Ein Benchmark sei zu prüfen (offene Daten, Nachrechnung durch Dritte). | **Bestandsaufnahme.** Festgehalten ist, was heute allein aus dem Repository nachrechenbar ist; eine Seite dazu entsteht nicht. | Abschnitt 5 |
| **G-7** Die Unabhängigkeit sei als Stärke darzustellen. | **Nicht Teil dieses Abgleichs.** | Abschnitt 6 |
| **G-8** Gesamturteil „Moderate Revision“. | **Nicht übernommen.** | Abschnitt 6; [`neuheitsgrad.md`](neuheitsgrad.md) §3 |

**Was zutrifft.** Zwei Lücken, die beide Texte berühren, benennt das Arbeitspapier selbst:

- Die 13 Einträge des [Literaturabgleichs vom 12.09.2026](literaturabgleich_2026-09-12.md) (zwölf in §1.1, ein
  Kurzvorläufer in §1.2) stehen weder im Literaturverzeichnis noch in Kapitel 2 des Arbeitspapiers (Z. 5844–5848;
  [Offene Punkte](arbeitspapier/PCMMS_Arbeitspapier_Offene_Punkte.md) Nr. 42, Z. 163–167). Nachgezählt: Keiner der
  13 Schlüssel steht in [`references.bib`](arbeitspapier/references.bib) (22 Einträge: 21 Literaturquellen und der
  Repository-Stand).
- Die Suchbegriffe der Recherche decken Haptik, vibrationsgetriebene Roboter und Kapselsysteme, Impact-Oszillatoren und
  Grazing, dynamisches Wägen und Metrologie nicht ab; eine Recherche in einer bibliografischen Fachdatenbank fehlt
  (Z. 5882–5895; Suchbegriffe Z. 5772–5788; Art der Recherche Z. 5741–5749).

**Dateiname.** Der in den Texten genannte Dateiname `06_neuheitsgrad.md` existiert im Repository nicht; gemeint ist
[`neuheitsgrad.md`](neuheitsgrad.md).

## 2. Literaturprüfung: die drei Angaben an den Primärquellen

Eng begrenzte Ausnahme von AP-16 („Recherche außerhalb des Bestands nicht begonnen“): Geprüft sind nur die drei in G-3
genannten Angaben. Es gab keine weitere Recherche; neue Kandidaten sind nicht aufgenommen.

**Prüfweg.** Alle Adressen wurden am 10.11.2026 zwischen 15:00 und 15:03 UTC in dieser Sitzung direkt abgerufen; gelesen
wurden die Rohantworten der Server (HTML, PDF, JSON, Kopfzeilen der Weiterleitung), kein Zusammenfassungswerkzeug. Die
Vorprüfung im Chat vom selben Tag ist nicht übernommen. Der Netzzugang der Sitzung war zunächst gesperrt und wurde vom
Autor für sieben Hosts freigegeben (`doi.org`, `api.crossref.org`, `www.extrica.com`, `journals.sagepub.com`,
`www.sciencedirect.com`, `linkinghub.elsevier.com`, `patents.google.com`). „Bibliografisch geprüft“ heißt wie in
Anhang C des Arbeitspapiers (Z. 5794–5797): Autoren, Titel, Erscheinungsort und Jahr auf der Seite des Verlags oder
Repositoriums bestätigt, DOI aufgelöst. Der Eintrag im DOI-Register Crossref enthält die vom Verlag hinterlegten
Angaben; er ist hier als Registereintrag geführt und zählt nicht als Verlagsseite. Aussagen über den Inhalt stammen nur
aus dem selbst gelesenen Text; der Lesestand steht dabei.

**Ergebnis.**

| Angabe der Texte | Gefundene Arbeit | Bibliografisch geprüft | Lesestand | DOI |
|---|---|---|---|---|
| a) „Korendiy et al. (2026)“ | Korendiy, Yaniv, Predko, Laushnyk, Dzyubyk, Hrevtsov 2026, Vibroengineering Procedia 62, S. 41–50 | **ja** (Verlagsseite, Verlags-PDF, DOI aufgelöst; Register stimmt überein) | Volltext | `10.21595/vp.2026.26165` |
| b) „Olgac (2005)“ | kein Aufsatz dieser Form; gefunden: Mikus, Olgac, Sipahi 2009, Control Engineering Practice 17 (1), S. 210–220 | **nein** – DOI aufgelöst und Registereintrag gelesen, die Verlagsseite verlangt eine Captcha-Eingabe und ist nicht gelesen | nur Katalogeintrag (Aufsatz); daneben der Abstract der Konferenzfassung | `10.1016/j.conengprac.2008.07.002` |
| c) „Xiong & Xu (2015)“ | Zhan, Xu 2015, Advances in Mechanical Engineering 7 (3), Artikel 1687814015573766; „Xiong“ ist der Vorname des Erstautors | **nein** – DOI aufgelöst und Registereintrag gelesen, die Verlagsseite verlangt eine Captcha-Eingabe und ist nicht gelesen | Abstract (im Registereintrag) | `10.1177/1687814015573766` |

Die Angabe in Anhang C, zu „Korendiy et al. 2026“ sei keine Arbeit dieses Jahres auffindbar (Z. 5860–5862, Stichtag
4. und 5. September 2026, Z. 5757), ist damit überholt: Die Arbeit ist am 08.06.2026 erschienen, die Suche hat sie nicht
gefunden. Für b) und c) fehlt die Bestätigung auf der Verlagsseite; sie gehört zur Sichtprüfung des Autors (E-1).

### 2.1 a) „Korendiy et al. (2026)“

| Feld | Inhalt |
|---|---|
| Bibliografie | Vitaliy Korendiy, Oleksandr Yaniv, Rostyslav Predko, Ihor Laushnyk, Andriy Dzyubyk, Serhii Hrevtsov: „Trajectory-based synthesis of a three-mass vibratory system excited by a dual phase-controlled crank-slider mechanism“. Vibroengineering Procedia, Band 62 (Juni 2026), S. 41–50; keine Heftnummer; ISSN 2345-0533 (Druck), 2538-8479 (online); Verlag Extrica (im Register: JVE International Ltd.). Eingegangen 22.02.2026, angenommen 30.03.2026, veröffentlicht 08.06.2026; Beitrag zur 76th International Conference on Vibroengineering, Taschkent, 28.–29.04.2026; Open Access, CC BY 4.0. DOI `10.21595/vp.2026.26165`. Alle Autoren: Lviv Polytechnic National University, Lwiw. |
| Prüfweg | <https://doi.org/10.21595/vp.2026.26165> leitet weiter (302) auf die Verlagsseite <https://www.extrica.com/article/26165> (200): Titel, sechs Autoren in dieser Reihenfolge, Zeitschrift, Band, Seiten, Datum und DOI stehen in den Metaangaben und im Seitentext. Verlags-PDF <https://www.extrica.com/article/26165/pdf>: 10 Seiten, Kolumnentitel „Vibroengineering Procedia. June 2026, Volume 62“, S. 41–50. Registereintrag <https://api.crossref.org/works/10.21595/vp.2026.26165>: übereinstimmend. Abruf 10.11.2026. **Bibliografisch geprüft: ja.** |
| Lesestand | Volltext: HTML-Volltext der Verlagsseite, Abschnitte 1 bis 4 mit Literaturliste; Verlags-PDF zum Abgleich, darin auch Fig. 1 (Schema) und Fig. 2 (Bahnen) angesehen. |
| System | Ebenes System mit drei bewegten Massen. Das Arbeitsorgan m₁ bewegt sich rein translatorisch in zwei Richtungen (Drehschwingungen vernachlässigt) und steht auf viskoelastischen Stützen (Feder-Dämpfer-Paare waagerecht und senkrecht). Zwei Hilfsmassen m₂, m₃ laufen auf zwei geneigten geraden Führungen und sind je über Feder und viskosen Dämpfer an den Schieber eines Schubkurbelkanals gekoppelt; die Schieber sind masselos angenommen. Nach Fig. 1 sitzt der Kurbeltrieb am Arbeitsorgan, und die Stützen verbinden das Arbeitsorgan mit einem festen Gestell. Modell mit vier Freiheitsgraden (x₁, y₁, u₂, u₃; u₂, u₃ relativ zum Arbeitsorgan). Rechenbeispiel: m₁ = 50 kg, m₂ = m₃ = 5 kg, 15 Hz (dort Abschnitte 2.1, 2.3, 3). |
| Bewegungsgesetz | Nicht harmonisch: Die Kurbel dreht mit konstanter Winkelgeschwindigkeit, der Schieberweg folgt der exakten Schubkurbelkinematik (dort Gl. 1). Bei r/l = 0,2 ist er nahe an einer Sinusbewegung mit kleiner zweiter Harmonischer. Vorgegeben ist die Fußpunktbewegung der Koppelglieder; die Bewegung der Hilfsmassen und des Arbeitsorgans folgt aus der Dynamik (dort Abschnitte 2.2, 3). |
| Stellgröße | Phasenversatz γ zwischen den beiden Kurbelzapfen, also zwischen den beiden Erregerkanälen (φ₂ = φ + γ); wirksam ist δ = γ + (θ₃ − θ₂) mit den Führungswinkeln θ₂, θ₃. Im Modell ist γ je Konfiguration ein fester Einstellwert; eine Verstellung im Betrieb ist als Ausblick genannt. Daneben als Entwurfsgrößen die Führungswinkel und die Kurbelradien (Hübe) (dort Abschnitte 2.2, 3, 4). |
| Zielgröße | Stationäre Bahn des Arbeitsorgans in der Ebene: geradlinig (senkrecht, waagerecht, geneigt), elliptisch, nahezu kreisförmig (dort Abschnitt 2.4, Fig. 2). |
| Körper | Bewegt. Die Schwingbahn des Arbeitsorgans ist das Ziel. Die Lagerung ist beidseitig viskoelastisch; ein einseitiger Kontakt oder ein Abheben kommt im Modell nicht vor. |
| Kraft an Auflage oder Fundament | Nicht ausgewertet. Die Zweigkräfte F₂, F₃ und die resultierende Erregerkraft auf das Arbeitsorgan stehen in den Bewegungsgleichungen (dort Abschnitt 2.3). Als Ergebnisse berichtet sind Bahnen (Fig. 2) und eine qualitative Tabelle der Parametereinflüsse (Table 1). Stützkräfte oder eine auf das Fundament übertragene Kraft kommen im Volltext nicht vor. |
| Art der Arbeit | Analytik (Modell, stationäre Amplituden- und Phasenbeziehungen) und numerische Simulation (Wolfram Mathematica) an einem idealisierten Modell. Kein Experiment; die experimentelle Prüfung an einem Prototyp ist als künftige Arbeit genannt (dort Abschnitte 3, 4). |

**Abgrenzung zu PCMMS** (entlang der vier Merkmale, Z. 942–951). Gemeinsam sind ein Körper auf Stützen, der seinen
Antrieb mit bewegten Massen selbst trägt, drei Massen, die relative Phase als wichtigste Stellgröße, eine nicht
harmonische Bewegung (dort aus der Kurbelkinematik) und eine reine Simulationsstudie an einem idealisierten Modell. Zielgröße
ist dort die Bahn des Arbeitsorgans, nicht die Wellenform einer Kontaktkraft; gestellt wird die Phase zwischen zwei
Erregerkanälen mit je einer Hilfsmasse, und der Körper soll schwingen, auf beidseitig viskoelastischen Stützen ohne
einseitigen Kontakt. Eine Kraft an Auflage oder Fundament wird nicht ausgewertet, und eine durch einen Erhaltungssatz
festgelegte Kontrollgröße kommt im Volltext nicht vor.

Die Literaturliste der Arbeit enthält mehrere frühere Arbeiten mit Korendiy als Autor, darunter solche zur
Schubkurbel-Erregung (dort [18] bis [20]). Sie sind hier weder geprüft noch als Kandidaten aufgenommen (E-4). In der
Literaturliste steht auch Osadchyy et al. 2023, das im Literaturverzeichnis des Arbeitspapiers geführt ist.

### 2.2 b) „Olgac (2005)“

Einen Aufsatz „Olgac (2005)“ hat die Prüfung nicht ergeben. Die Registersuche nach Titel und Autoren liefert einen
Zeitschriftenaufsatz von 2009 und eine Konferenzfassung von 2003; aus dem Jahr 2005 stammt die Veröffentlichung einer
Patentanmeldung derselben drei Personen, die mutmaßliche Herkunft der Angabe. Zitierfähig wäre der Aufsatz.

| Feld | Inhalt |
|---|---|
| Bibliografie | Oldrich Mikus, Nejat Olgac, Rifat Sipahi: „An actively controlled harmonic force generator“. Control Engineering Practice, Band 17, Heft 1 (Januar 2009), S. 210–220; ISSN 0967-0661; Elsevier. DOI `10.1016/j.conengprac.2008.07.002`. Angaben nach dem Registereintrag. |
| Prüfweg | Registereintrag <https://api.crossref.org/works/10.1016/j.conengprac.2008.07.002>: Autoren, Titel, Zeitschrift, Band, Heft, Seiten, Jahr. <https://doi.org/10.1016/j.conengprac.2008.07.002> leitet weiter (302) auf <https://linkinghub.elsevier.com/retrieve/pii/S0967066108001238> (200), eine Weiterleitungsseite des Verlags, die nur den Titel und die Kennung (PII) des Artikels nennt. Die Artikelseite <https://www.sciencedirect.com/science/article/pii/S0967066108001238> antwortet mit 403 und einer Captcha-Abfrage; sie ist nicht gelesen. Abruf 10.11.2026. **Bibliografisch geprüft: nein** – Registereintrag und DOI-Auflösung liegen vor, die Bestätigung auf der Verlagsseite fehlt. |
| Lesestand | Zeitschriftenaufsatz: nur Katalogeintrag (der Registereintrag enthält keinen Abstract). Nebenquelle, kein Ersatz für den Aufsatz: der Abstract der Konferenzfassung im Registereintrag. |
| System | Aus dem Katalogeintrag nicht zu entnehmen. Abstract der Konferenzfassung: Geräte mit umlaufenden Exzentermassen; Zahl und Anordnung der Massen sind im Abstract nicht genannt. |
| Bewegungsgesetz | Aus dem Katalogeintrag nicht zu entnehmen. Abstract der Konferenzfassung: Erzeugt wird eine harmonische Kraft; ob die Bewegung der Massen vorgegeben ist, ist im Abstract nicht genannt. |
| Stellgröße | Aus dem Katalogeintrag nicht zu entnehmen. Abstract der Konferenzfassung: Verstellt werden Amplitude, Frequenz und Phasenwinkel der harmonischen Kraft. Die „relative phase“ ist dort die Phase der Kraft gegen ein gegebenes harmonisches Signal; eine Phase zwischen den Massen nennt der Abstract nicht. |
| Zielgröße | Aus dem Katalogeintrag nicht zu entnehmen. Abstract der Konferenzfassung: eine harmonische Kraft mit einstellbarer Amplitude (null bis F_max), Frequenz (rund ±10 % um die Nennfrequenz) und Phase (0 bis 2π gegen ein gegebenes harmonisches Signal), zur Krafterregung oder zur Tilgung harmonisch erregter Schwingungen; dazu ein günstiges Verhältnis von Spitzenkraft zu Gewicht. |
| Körper | Aus dem Katalogeintrag nicht zu entnehmen; im Abstract der Konferenzfassung nicht genannt. |
| Kraft an Auflage oder Fundament | Aus dem Katalogeintrag nicht zu entnehmen. Im Abstract der Konferenzfassung ist die erzeugte Kraft selbst die Zielgröße; eine Kraft an Auflage oder Fundament ist dort nicht genannt. |
| Art der Arbeit | Aus dem Katalogeintrag nicht zu entnehmen. Abstract der Konferenzfassung: Entwurf und Steuerung eines Geräts, Erprobung an einem Prototyp. |

**Prüfvermerk zur Herkunft der Angabe.** Konferenzfassung nach dem Registereintrag: O. Mikus, N. Olgac, R. Sipahi,
„An Actively Controlled Harmonic Force Generator“, in „Dynamic Systems and Control, Volumes 1 and 2“ (ASME 2003
International Mechanical Engineering Congress and Exposition, Washington, DC, 15.–21.11.2003), S. 31–40,
DOI `10.1115/imece2003-41410`; die DOI leitet auf `asmedigitalcollection.asme.org` weiter, die Seite ist nicht
abgerufen. Patentanmeldung: US 2005/0077845 A1, „Actively controlled harmonic force generator“, Erfinder Nejat Olgac,
Oldrich Mikus, Rifat Sipahi, angemeldet 20.08.2004, veröffentlicht 14.04.2005, gelesen unter
<https://patents.google.com/patent/US20050077845A1/en>. Sie beschreibt einen Kraftgenerator mit vier gleichen umlaufenden
Exzentermassen, paarweise gegenläufig, dessen Kraftamplitude über die Winkellage zweier Massengruppen gestellt wird. Die
Anmeldung ist die mutmaßliche Herkunft der Jahreszahl 2005. Sie ist kein Literatureintrag, und ihr Inhalt ist in der
Tabelle oben nicht verwendet.

**Abgrenzung zu PCMMS.** Der Aufsatz selbst ist nicht gelesen; die folgende Einordnung stützt sich nur auf den Abstract
der Konferenzfassung. Gemeinsam sind bewegte, hier umlaufende Massen, mit denen eine Kraft geformt wird. Zielgröße ist
dort eine harmonische Kraft mit einstellbarer Amplitude, Frequenz und Phase, nicht die Wellenform einer einseitigen
Kontaktkraft; zu ruhendem Körper, Kontaktverlust und einer Kontrollgröße sagt der Abstract nichts.

### 2.3 c) „Xiong & Xu (2015)“

**Namensprüfung.** Der Registereintrag führt die Autoren als Xiong Zhan (Vorname Xiong, Nachname Zhan) und Jian Xu.
„Xiong & Xu“ nennt also einen Vornamen als Nachnamen; richtig ist Zhan und Xu.

| Feld | Inhalt |
|---|---|
| Bibliografie | Xiong Zhan, Jian Xu: „Locomotion analysis of a vibration-driven system with three acceleration-controlled internal masses“. Advances in Mechanical Engineering, Band 7, Heft 3 (2015), Artikelnummer 1687814015573766; ISSN 1687-8132, 1687-8140; SAGE Publications. DOI `10.1177/1687814015573766`. Im Register: Druckdatum 01.03.2015, Online-Datum 06.04.2015. Angaben nach dem Registereintrag. |
| Prüfweg | Registereintrag <https://api.crossref.org/works/10.1177/1687814015573766>: Autoren, Titel, Zeitschrift, Band, Heft, Artikelnummer, Jahr, Abstract. <https://doi.org/10.1177/1687814015573766> leitet weiter (302) auf <https://journals.sagepub.com/doi/10.1177/1687814015573766>; die Seite antwortet mit 403 und einer Captcha-Abfrage und ist nicht gelesen. Abruf 10.11.2026. **Bibliografisch geprüft: nein** – Registereintrag und DOI-Auflösung liegen vor, die Bestätigung auf der Verlagsseite fehlt. |
| Lesestand | Abstract, wie ihn der Verlag im Register hinterlegt hat. |
| System | Ein starrer Körper auf einer waagerechten Ebene mit drei inneren, beschleunigungsgesteuerten Massen als Antrieb; zwischen System und Ebene wirkt isotrope Trockenreibung. |
| Bewegungsgesetz | Die Beschleunigung der inneren Massen ist gesteuert („acceleration-controlled“). Ob das Gesetz harmonisch ist, ist im Abstract nicht genannt. |
| Stellgröße | „Drive parameters“. Eine relative Phase ist im Abstract nicht genannt. |
| Zielgröße | Fortbewegung des Körpers in der Ebene: geradlinige und drehende Grundbewegung, daraus zusammengesetzte Bahnen (schräge Geraden und Kurven, durch Streckenzüge angenähert); Steigung und Krümmung über die Antriebsparameter einstellbar; Optimierung der Antriebsparameter auf maximale mittlere Geschwindigkeit. |
| Körper | Bewegt. |
| Kraft an Auflage oder Fundament | Im Abstract nicht genannt; genannt ist nur die Reibung zwischen System und Ebene. |
| Art der Arbeit | Im Abstract nicht ausdrücklich genannt (die Dynamik wird „studied“, Bahnen werden „constructed“, Parameter „optimized“); ein Experiment ist im Abstract nicht genannt. |

**Ist das eine der Arbeiten, die das Projekt als „Fang, Xu und Mitarbeiter“ führt?** Aus den gelesenen Quellen nicht zu
entscheiden. Das Repository nennt keine Vornamen und zwei Fundstellen ([`einordnung.md`](einordnung.md) Z. 169–171:
Commun. Nonlinear Sci. Numer. Simul. 114, 106704, 2022, und Diao, Zhang & Fang, Arch. Appl. Mech. 91, 2073–2088, 2021);
keine davon ist diese Arbeit. Der Registereintrag nennt für beide Autoren die Tongji-Universität, Shanghai; die
Fudan-Universität kommt in ihm nicht vor. Gegenstand ist nach dem Abstract ein einzelner Körper mit drei inneren Massen,
kein Mehrmodul-Roboter.

**Abgrenzung zu PCMMS.** Gemeinsam ist nach dem Abstract ein Körper mit drei inneren, gesteuert bewegten Massen.
Zielgröße ist dort die Fortbewegung des Körpers auf einer Ebene mit Trockenreibung (Bahn und mittlere Geschwindigkeit),
der Körper bewegt sich also; eine relative Phase als Stellgröße, eine Kontaktkraft als Zielgröße und eine Kontrollgröße
sind im Abstract nicht genannt. Die Inhaltsangabe der beiden Texte (Bewegungsarten über Phasenbeziehungen) ist am
Abstract nicht bestätigt.

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
Textvorschlag, solange die Verlagsseiten nicht gelesen sind (E-1). Alles in diesem Abschnitt ist Vorschlag. Quelltext,
PDF und Literaturverzeichnis des Arbeitspapiers v2.5 bleiben unverändert (Variante A); der Berichtigungshinweis steht in
[`arbeitspapier/README.md`](arbeitspapier/README.md) und in den
[Offenen Punkten](arbeitspapier/PCMMS_Arbeitspapier_Offene_Punkte.md) (Nr. 45 und 46).

### 3.1 Berichtigung zu Anhang C

**Sachverhalt.** Anhang C führt „Korendiy et al. 2026“ an zwei Stellen als nicht auffindbar. Die Arbeit besteht und ist
am 08.06.2026 erschienen, vor dem Stichtag der Recherche (4. und 5. September 2026, Z. 5757). Die Suche hat sie nicht
gefunden.

**Verifikationstabelle (`tab:verifikation`), Zeile Z. 5816.** Bisher:

```latex
    Gurskyi/Korendiy et al.\ 2023 & MDPI & DOI & Ersatz für nicht auffindbares „Korendiy 2026“ \\
```

Vorschlag, mit einer neuen Zeile für die geprüfte Arbeit:

```latex
    Gurskyi/Korendiy et al.\ 2023 & MDPI & DOI & am 5.9.2026 anstelle der damals nicht gefundenen Angabe „Korendiy 2026“ aufgenommen; diese ist inzwischen bestätigt (nächste Zeile) \\
    Korendiy et al.\ 2026 & Extrica, Crossref & DOI & geprüft am 10.11.2026, Volltext gelesen; erschienen am 8.6.2026, bei der Suche vom 4./5.9.2026 nicht gefunden \\
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
      Berichtigung vom 10.\ November 2026: Die Arbeit besteht. Sie ist
      am 8.\ Juni 2026 erschienen, also vor dem Stichtag; die Suche hat
      sie nicht gefunden. Sie ist auf der Verlagsseite geprüft, im
      Volltext gelesen und aufgenommen \cite{korendiy2026}.
```

**Punkt zur Fudan-Zuschreibung (Z. 5863–5869).** Kein Vorschlag, weil c) nicht im Sinn von Anhang C bestätigt ist. Als
Hinweis für die Sichtprüfung: Die von den Texten als „Xiong & Xu (2015)“ genannte Arbeit ist nach dem Registereintrag
Zhan und Xu 2015; der Eintrag nennt die Tongji-Universität, nicht die Fudan-Universität, und die Arbeit ist keine der
beiden Fundstellen in [`einordnung.md`](einordnung.md) §5 (Abschnitt 2.3).

### 3.2 Textvorschlag für „Mehrkörperdynamik und phasengesteuerte Anregung“

Ein Absatz für a), im Ton der vorhandenen Absätze. Einzufügen nach dem Satz zu Gurskyi, Korendiy et al., der in Z. 746
mit `\cite{gurskyi2023}` endet; die beiden Sätze zur Haptik (Z. 746–750) beginnen dann einen neuen Absatz.

```latex
Korendiy et al.\ untersuchen ein ebenes Dreimassensystem mit
Schubkurbelantrieb: Zwei Hilfsmassen laufen auf geneigten Führungen und
regen das viskoelastisch gelagerte Arbeitsorgan über
Feder-Dämpfer-Glieder an \cite{korendiy2026}. Stellgröße ist der
Phasenversatz zwischen den beiden Kurbelkanälen, Zielgröße die
stationäre Bahn des Arbeitsorgans --- geradlinig, elliptisch oder
nahezu kreisförmig. Die nicht harmonische Kurbelkinematik erscheint
dort als kleine Störung der idealen Bahn. Die Arbeit ist eine
Simulationsstudie an einem Modell mit vier Freiheitsgraden; ein
Experiment steht aus, und eine Kraft an Auflage oder Fundament wird
nicht ausgewertet.
```

**Gilt der Absatz „Der Zweck ist in diesen Anwendungen …“ (Z. 764–769) unverändert?** Mit a) ja. Zweck der neuen Arbeit
ist die Bahn des Arbeitsorgans, und die steht in der Aufzählung des Absatzes (Z. 766). Die Kraft an der Auflage ist dort
nicht Zielgröße; sie wird nicht einmal ausgewertet, „Begleiterscheinung“ (Z. 769) trifft also nur im weiteren Sinn. Für
b) und c) ist die Frage vor einer Aufnahme am Volltext zu klären. Nach den gelesenen Abstracts fielen sie unter „Betrag
der resultierenden Kraft“ und „Fortbewegung eines Körpers“; bei b) wäre die erzeugte Kraft allerdings selbst die
Zielgröße.

Unabhängig von den neuen Arbeiten steht der Absatz schon am Stand `51f79a2` in Spannung zum Absatz davor: Dort heißt es
für die Robotik, Bewegung und Kontaktkraft würden „gemeinsam als Entwurfsgrößen behandelt“ (Z. 753–754), hier dagegen,
die Kraft an der Auflagefläche sei „durchweg“ nicht Zielgröße, sondern Begleiterscheinung (Z. 764–769). Das ist im Pull
Request gemeldet und nicht geändert.

### 3.3 Folgeänderungen bei einer Aufnahme von a)

1. [`references.bib`](arbeitspapier/references.bib): neuer Eintrag `korendiy2026` mit den Feldern aus Abschnitt 2.4,
   nach `gurskyi2023` (Z. 214–223 der Datei); Kopfkommentar um den Prüfstand 10.11.2026 ergänzen.
2. „Einordnung und mögliche Lücke“, Z. 925–927: den Verweis `\cite{chen2019, osadchyy2023, gurskyi2023}` um
   `korendiy2026` ergänzen.
3. Z. 5792: „Jede der 21 Literaturquellen“ wird zu 22; dazu der Hinweis, dass ein Eintrag am 10.11.2026 geprüft ist
   (der Stichtag der Rahmendaten, Z. 5757, bleibt 4. und 5. September 2026).
4. Verifikationstabelle: neue Zeile und geänderte Anmerkung wie in 3.1; in den Rahmendaten (Z. 5759–5760,
   „Verifikationsquellen“) fehlt Extrica.
5. „Nicht aufgenommene Angaben“, Einleitungssatz Z. 5852–5854: „Drei Angaben … wurden nicht aufgenommen, weil sie sich
   nicht verifizieren ließen“ gilt nach der Berichtigung nur noch für zwei.
6. „Folgerung für die Aussagen zum Forschungsstand“ (Z. 5882–5895): Dass die gezielte Suche eine einschlägige, drei
   Monate vorher erschienene Arbeit nicht gefunden hat, gehört als Beleg für ihre begrenzte Reichweite dorthin (ein
   Satz).
7. Versionshinweis und Titelblatt, Neusatz nach [`arbeitspapier/README.md`](arbeitspapier/README.md) und die Verweise
   auf „v2.5“ in anderen Dateien: nur in Variante B (E-2).
8. Die Zählungen unter „Stand des Dokuments“ in den Offenen Punkten (Z. 64, 110, 123 der Datei) sind historisch und
   bleiben.

## 4. Beitragsaussagen: Prüfung auf Widerspruchsfreiheit

Verglichen sind sieben Stellen: (1) der Schlussabsatz der Kurzfassung (Z. 144–149), (2) der Schlussabsatz des Abstracts
(Z. 225–230), (3) „Beitrag dieser Arbeit“ (Z. 590–696), (4) „Einordnung und mögliche Lücke“ (Z. 920–973), (5) das Fazit
„Methodischer Beitrag“ (Z. 5175–5196), (6) [`neuheitsgrad.md`](neuheitsgrad.md) §7 und §8 (Z. 163–196) und (7) der
Abschnitt „Worum es geht“ der [README](../README.md) (Z. 9–36). Maßstab sind die „Verbindlichen Begriffe“ in
[`overview.md`](overview.md) (Z. 46–57) und der [Entwurf der Präregistrierung v2](praeregistrierung_v2_entwurf.md).
Ergebnis ist diese Liste. Es wird nichts umformuliert, und es gibt keinen neuen Wortlaut für Kurzfassung, Abstract oder
Einleitung. Jede Abweichung ist von einem zweiten Leser an den Fundstellen gegengeprüft; was dabei nicht standhielt,
steht unter 4.3 oder 4.4 und nicht unter 4.2.

### 4.1 Worin die Stellen übereinstimmen

- Keine neue Physik, kein Effektanspruch (Z. 144, Z. 225; README Z. 30–31; `neuheitsgrad.md` Z. 195).
- Das Zeitmittel ist Kontrollgröße, nicht Zielgröße und kein Ergebnis (Z. 88–90, Z. 606–616, Z. 949–950, Z. 5181–5183;
  `neuheitsgrad.md` Z. 110–114; README Z. 20–21).
- Der mögliche Beitrag ist methodisch und eng; die Bausteine sind bekannt (Z. 144–145, Z. 595–596, Z. 922–935;
  `neuheitsgrad.md` Z. 48–49, Z. 176).
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
Suchbefunde zurückgenommen (Z. 355–358); Z. 860–861 ist davon nicht erfasst.

**BA-2 Zielgrößen, Rangfolge und Kontaktregime.** Das Arbeitspapier führt vier Funktionale – Schiefe, Liftoff-Anteil,
Asymmetrieverhältnis, minimale Kontaktkraft – ohne Abstufung als „primäre Zielgrößen“ des Messrahmens (Z. 622–624;
Kurzfassung Z. 91–96; Abstract Z. 172–176) und prüft sie nach seinem Hypothesenteil einzeln (Z. 1929–1941). Der
Gegenstand ist über die Auflage bestimmt, die „einseitig ist, also innerhalb eines Zyklus abheben kann“ (Z. 79–80).
README (Z. 14–17), `neuheitsgrad.md` (Z. 157–159) und `overview.md` (Z. 52–55) ordnen die vier Funktionale der
Simulation zu. Für die Messkampagne sind nach dem Entwurf der Präregistrierung v2 F_min − ⟨N⟩ und die Harmonischen 1 bis
3 primär (H1, dort Z. 161), ebenso die Lage der Zeltspitze (H2, Z. 172); das Vorzeichen der Schiefe ist sekundär (H4,
Z. 196), A beschreibend, der Liftoff-Bereich explorativ (E1, Z. 215). Gegenstand ist dort der Körper, „solange er auf
allen Auflagepunkten Kontakt hält“ (Z. 13–15); der Arbeitspunkt hält Abstand zum Abheben (§5.3 (a), Z. 340–344), und
der Liftoff-Bereich wird nicht konfirmatorisch geprüft (Z. 139–140). Das Arbeitspapier nennt beides im Hauptteil selbst
(Z. 1855–1868, Z. 2299–2313), in den Beitragsaussagen nicht; die Harmonischen kommen dort als Zielgröße nicht vor.

**BA-3 Was die Messung entscheidet.** Die Beitragsaussagen des Arbeitspapiers beschreiben einen Rahmen, in dem eine
Phasenabhängigkeit der Wellenform „nachgewiesen, begrenzt oder ausgeschlossen“ werden kann (Z. 693–695; Z. 966–968 mit
„beziffert“). Gemeint ist der Nachweis oberhalb der Auflösungsschwelle (Z. 518–521; Frage F2, Z. 1899–1902; Hypothesen
Z. 1929–1941), nicht die Abhängigkeit im Modell, die das Papier selbst nennt (Z. 130–131). Zwei Punkte bleiben. Erstens
geht „ausgeschlossen“ über den Endzustand „nachgewiesenes Nullergebnis mit oberer Schranke“ hinaus (Z. 99–101,
Z. 3565–3569); das Papier sagt an anderer Stelle selbst: „Das Ausbleiben eines Befunds beweist nicht die Abwesenheit
einer Abhängigkeit“ (Z. 4953–4954). Zweitens weicht die Fassung als Nachweisentscheidung vom Entwurf der
Präregistrierung v2 ab, auf den README und `neuheitsgrad.md` für die Messkampagne verweisen: Dort ist die Abhängigkeit
„keine Hypothese“ (Z. 118–119), geprüft werden quantitative Vorhersagen aus Messungen an der Apparatur (H1, H2), und
ε_phys ist für die Wellenformgrößen ersetzt (Z. 97–98).

**BA-4 Festgelegte Kriterien gegenüber einer Präregistrierung im Entwurf.** Das Fazit sagt über die Arbeit: „Sie legt
die Kriterien fest, bevor Daten vorliegen, und macht sie damit der nachträglichen Anpassung unzugänglich“
(Z. 5089–5091, Abschnitt „Zusammenfassung der Arbeit“, außerhalb der sieben Stellen). „Beitrag dieser Arbeit“ führt
eine Schwelle ε_phys und vier Endzustände „mit vorab festgelegten Kriterien“ (Z. 654–668), ohne die Präregistrierung
oder ihren Status zu nennen. Dagegen stehen `neuheitsgrad.md` §7 mit „einer Präregistrierung im Entwurf (v2, nicht
eingefroren; v1 als nicht extern registrierte Arbeitsfassung)“ (Z. 174), der Entwurf v2 als Entwicklungsversion mit
vorläufigen Arbeitsfestlegungen (dort Z. 4, Z. 62–66), der ε_phys für die Wellenformgrößen ersetzt (Z. 97–98), und das
Arbeitspapier selbst, nach dem die Schwellen nicht beziffert sind (Z. 5007–5010, Z. 2140–2141). Innerhalb der sieben
Stellen ist das ein Unterschied im Status – im Papier definierte Regeln gegenüber einer noch nicht eingefrorenen
Festlegung –, kein Widerspruch im Wortlaut. Die Aussage in Z. 5089–5091 geht darüber hinaus.

### 4.3 Verkürzungen und uneinheitliche Gewichtung bei gleichem Umfang

- **Ruhender Körper.** Die Einordnung führt ihn als eines von vier Merkmalen der Konstellation des Suchbefunds
  (Z. 948), `neuheitsgrad.md` nennt ihn den entscheidenden Unterschied (Z. 83–85) und führt ihn in der Zusammenstellung
  (Z. 173), die README beginnt mit ihm (Z. 11). Die Beitragsaussagen von Kurzfassung, Abstract, „Beitrag dieser
  Arbeit“ und Fazit grenzen ohne ihn ab (Z. 146–148, Z. 625–629). Sie verkürzen; der Sache nach enthält das Papier das
  Merkmal (Z. 948, Z. 2250–2254). Dem Wortlaut nach ist die Kurzformel aber um dieses Merkmal weiter als die
  Konstellation, für die das Papier einen Suchbefund angibt. „Ruhend“ ist nirgends definiert und steht neben einer
  Auflage, die abheben kann (Z. 79–80).
- **Kern des Beitrags.** Das Arbeitspapier nennt die Nullgröße als Prüfmittel den „konstruktiven Kern“ (Z. 5178–5183;
  „Der zentrale methodische Zug“, Z. 4837–4838) und verweist dabei auf alle Elemente von „Beitrag dieser Arbeit“
  (Z. 5177–5178). `neuheitsgrad.md` nennt die Wellenformstatistik der unilateralen Kontaktkraft als Zielgröße „die
  methodische Behauptung“ (Z. 157), führt die Nullbasis als Zusatz („Dazu die Nullbasislinie“, Z. 108) und nennt sie in
  §8 nicht (Z. 188–190). Kurzfassung und Abstract nennen beide Elemente gleichrangig (Z. 145–148).
- **Zahl der Elemente.** Zwei in Kurzfassung und Abstract, neun „wesentliche Beiträge“ in „Beitrag dieser Arbeit“
  (Z. 602–691), vier Merkmale in der Einordnung, acht in `neuheitsgrad.md` §7 (Z. 171–174). Bahnprofil und
  Präregistrierung im Entwurf zählen nur dort zur Zusammenstellung.
- **Attribution.** `neuheitsgrad.md` §8 nennt die „Attribution über die Phasensteuerung“ als einen Ort des möglichen
  Beitrags (Z. 188–190) und schränkt selbst ein: „die Zuordnung selbst ist damit noch nicht gezeigt“ (Z. 104). Im
  Arbeitspapier fehlt ein so benanntes Element; die Sache steht dort als Trennung von Artefakten durch das
  Versuchsdesign (Z. 676–681), und der Rahmen endet bei einer „nachgewiesenen Abhängigkeit ohne Mechanismusbehauptung“
  (Z. 100–101).
- **Reichweite der Kontrolle.** „Beitrag dieser Arbeit“ und die Einordnung schließen mit dem Satz, die Apparatur werde
  „fortlaufend gegen eine Größe qualifiziert …, deren Wert bekannt ist“ (Z. 695–696, Z. 968–969). Die README sagt:
  „Umgekehrt qualifiziert ein unauffälliges Zeitmittel die dynamische Messkette nicht“ (Z. 25–26). Die Grenze steht im
  Arbeitspapier in Kurzfassung (Z. 138–140), Abstract (Z. 219–221), „Beitrag dieser Arbeit“ (Z. 614–616) und Fazit
  (Z. 5187–5190); ohne Einschränkung bleibt nur „Einordnung und mögliche Lücke“. Uneinheitlich ist außerdem, was
  geprüft wird: „Auswertekette“ (Z. 90, Z. 614, Z. 950, Z. 5183), „Messkette“ (Z. 146, Z. 959) oder „Apparatur“
  (Z. 94, Z. 695, Z. 968).
- **Drift.** Kurzfassung (Z. 88–90), „Beitrag dieser Arbeit“ (Z. 612–614) und `neuheitsgrad.md` (Z. 112–113) nennen
  Drift unter dem, worauf die Kontrolle prüft; das Papier sagt, Drift werde „von der Kontrollgröße erfasst“
  (Z. 2672–2673), trennt die Kontrollgröße aber zugleich durch Verschachtelung und Randomisierung von Drift
  (Z. 1490–1493). Die README zählt Drift zu dem, was trotz unauffälligem Zeitmittel gesondert zu charakterisieren ist
  (Z. 26–27).

### 4.4 Unterschiede der Wortwahl

- „nachgewiesen, begrenzt oder ausgeschlossen“ (Z. 694–695) gegenüber „nachgewiesen, beziffert oder ausgeschlossen“
  (Z. 967–968).
- „möglicher Beitrag“ (Z. 144, Z. 5177) gegenüber „Der Beitrag der Arbeit ist“ (Z. 965) und „Die wesentlichen Beiträge
  sind“ (Z. 602); der Vorbehalt steht jeweils im Text davor.
- „ohne systematische Recherche offen“ (Z. 149, Z. 597, Z. 711, Z. 940) gegenüber „ist nicht recherchiert“ (Z. 5193);
  nach Anhang C wurde in Metrologie und Wägetechnik nicht gesucht (Z. 5888–5890).
- Minimale Kontaktkraft N_min gegenüber F_min − ⟨N⟩: ein sachlicher Unterschied (Bandbegrenzung, Mittelung über Läufe,
  Bezug auf das Laufmittel), den das Arbeitspapier (Z. 1855–1868) und die README selbst erklären.
- „Primär“ steht vor drei verschiedenen Dingen: der zeitaufgelösten Kontaktkraft im Gegensatz zur Körperbewegung
  (`neuheitsgrad.md` Z. 171–172), den vier Funktionalen im Gegensatz zum Zeitmittel (Z. 622–624) und dem Rang nach dem
  Entwurf v2 (README Z. 16–17). Der Zusammenhang klärt jede Verwendung; verwechselbar bleibt Z. 623 neben der README.
- „Nur die minimale Kontaktkraft trägt eigenständige Information“ (Z. 119–121) ist ein Modellbefund, „F_min ist … nicht
  der Neuheitskern“ (`neuheitsgrad.md` Z. 155–156) eine Aussage zur Neuheit; ein Widerspruch ist das nicht.

### 4.5 Die Formel G-4, gemessen am Repository

**Was sie trifft.** „Rekombination bekannter Bausteine“ ist die Selbstbeschreibung des Projekts (`neuheitsgrad.md`
Z. 48–49; sinngleich Z. 922 und Z. 934–935). „Nicht der Entdeckung eines neuen Effekts“ steht mit keiner der sieben
Stellen im Widerspruch (Z. 144, Z. 225, Z. 597–598; README Z. 30–31). „Ruhender Körper“ und „Nullkontrolle“ sind
Begriffe des Repositorys. In grober Form deckt die Formel die vier Merkmale der Einordnung: die Wellenform als Ziel, die
Phasensteuerung eines Mehrmassensystems, den ruhenden Körper und die Nullkontrolle.

**Wo sie den Anspruch ändert.**

- **Präregistrierung als methodische Kontrolle.** Die Formel nennt sie ohne Zusatz. Im Repository ist v1 eine nicht
  extern registrierte Arbeitsfassung und v2 ein Entwurf, „nicht eingefroren, nicht registriert“
  (`neuheitsgrad.md` Z. 174; Entwurf v2, Z. 4 und Z. 62–66); Einfrieren und Registrierung sind in AP-14 offen
  ([`arbeitsplan_status.md`](arbeitsplan_status.md)). Die Beitragsstellen des Arbeitspapiers nennen die Präregistrierung
  nicht.
- **Gewichtung der Nullgröße.** Das Arbeitspapier führt sie als erstes von zwei Beitragselementen (Z. 144–148), als
  „konstruktiven Kern“ (Z. 5178–5185) und als „zentralen methodischen Zug“ (Z. 4837–4838), mit ausdrücklich ungeklärter
  Neuheit (Z. 5192–5194). In der Formel ist die „Nullkontrolle“ eines von drei Gliedern der methodischen Kontrolle; ihre
  Funktion als Prüfmittel der eigenen Auswertekette und der Neuheitsvorbehalt fehlen. Diese Gewichtung entspricht der
  von `neuheitsgrad.md` (4.3, „Kern des Beitrags“).
- **Ziel.** „Charakterisierung“ ist beschreibend und mit README und `neuheitsgrad.md` §8 vereinbar. Die Beitragsstellen
  des Arbeitspapiers nennen dagegen einen Messrahmen mit Entscheidungsstruktur, Äquivalenzlogik und Nullausgang
  (Z. 597–598, Z. 654–674); beides nennt die Formel nicht.

**Was ihr fehlt, ohne den Anspruch zu ändern.**

- **Zielgrößen.** Die Formel nennt keine; „Wellenform-Charakterisierung“ deckt auch F_min − ⟨N⟩ und die Harmonischen.
  Schiefe und Liftoff nennt die Tabelle des Gutachtens, und für sie gilt BA-2: Nach dem Entwurf v2 sind F_min − ⟨N⟩, die
  Harmonischen 1 bis 3 und die Lage der Zeltspitze primär, das Vorzeichen der Schiefe sekundär, der Liftoff-Bereich
  explorativ, und V1 verlangt Dauerkontakt.
- **Phasensteuerung.** Die Formel nennt sie als Baustein. Als Modellaussage ist gedeckt, dass die Phasenlage die
  Wellenform formt (Entwurf v2, Z. 118–119; Arbeitspapier Z. 945–947); die Zahlen dazu sind Simulation. Nicht gezeigt
  ist die Zuordnung beobachteter Änderungen zur Phasenvariation allein (`neuheitsgrad.md` Z. 100–104).
- **Status und Vorbehalt.** Die Formel trägt weder den Stand „prä-experimentell“ (Z. 80–81) noch den Vorbehalt des
  „möglichen“ Beitrags bei offener Recherche (Z. 144–149, Z. 5192–5194). „Unter klarer methodischer Kontrolle“
  beschreibt als gegeben, was im Repository Auslegung, Entwurf und Simulation ist. Das wiegt nur, wenn die Formel allein
  als Beitragsaussage steht; auch das Arbeitspapier setzt den Vorbehalt nicht an jeder Stelle (Z. 602, Z. 965).
- **Bausteine.** Es fehlen „unilateral“ und „innere Massen eines geschlossenen Körpers“ (Z. 943–947) und das
  Bahnprofil, das nur `neuheitsgrad.md` als Merkmal führt (Z. 171). Die Formel verliert Abgrenzungsschärfe, erhebt aber
  keinen weiteren Anspruch.
- **Begriff.** „Kontaktkraft“ steht ohne Bezug auf die Kraftverschiebung gegen die Referenz (`overview.md` Z. 50–51;
  README Z. 19–20). In der Formel bezeichnet das Wort einen Baustein, nicht die ausgewertete Größe; die Kurzaussagen
  des Repositorys halten es ebenso (Z. 146–148; `neuheitsgrad.md` Z. 172).

**Dieselbe Lesart im Repository.** [`CITATION.cff`](../CITATION.cff) führt „preregistration“ als Schlagwort ohne Status
(Z. 19), nennt als Zielgrößen „Schiefe, Liftoff-Anteil, Asymmetrieverhältnis und Minimalkraft“ und zählt zum Enthaltenen
die „Präregistrierung“ (Z. 27–29). Die Datei liegt außerhalb der sieben Stellen und ist nicht geändert.

Die Formel wird nicht übernommen, und diese Notiz setzt keine andere an ihre Stelle.

### 4.6 Offen, nicht entschieden

- D-3, die Neuheitsformulierung der Konstruktionsform, bleibt Entscheidung des Autors
  ([`arbeitsplan_status.md`](arbeitsplan_status.md)).
- Ob Linie A künftig von der einzelnen einseitigen Auflage her beschrieben wird (README Z. 11; Kurzfassung Z. 77–80)
  oder vom Messrahmen mit Rundum-Kontaktkette (AP-27, Konzept;
  [`konzepte/nadelrahmen_dreimassenkoerper_2026-10.md`](konzepte/nadelrahmen_dreimassenkoerper_2026-10.md)), ist offen.
  [`einordnung.md`](einordnung.md) nennt schon beides (Z. 69). Die Frage berührt BA-2 und den Punkt „Ruhender Körper“
  in 4.3 und ist hier nur vermerkt.

## 5. Nachrechenbare Referenzfälle (zu G-6): Bestandsaufnahme

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
- **Sollwerte:** die Datensätze in `data/` (361, 441 und 49 Punkte) und Tests mit festgehaltenen Zahlen
  (`tests/test_ereignisloeser.py`, `tests/test_auslegung.py`). Am Punkt (120°, 240°) binden drei Tests denselben Wert
  F_min = 5,330390 N an zwei weitere Rechenwege: den ereignisgenauen Löser auf 1·10⁻⁶ N (`tests/test_ereignisloeser.py`,
  Z. 51) und das Auslegungswerkzeug auf 5·10⁻⁷ N (`tests/test_auslegung.py`, Z. 66 und Z. 498).
- **Nachweisarchiv:** [`rechnungen/`](../rechnungen/README.md) mit Prüfskripten und abgelegten Ausgaben, etwa
  `rechnungen/engine/validate_eng_ausgabe.txt`, und die Gegenprobe zum linearen Löser in
  `docs/arbeitspapier/gegenprobe_2026-09-26/`. Die README nennt das Archiv „für den Einstieg nicht nötig“ (Z. 76).
- **Anleitung:** der Block „Nachrechnen“ der README (Z. 199–214) mit Aufrufen und einigen Laufzeiten.

### 5.2 Vorschlag: fünf Referenzfälle

Aufrufe vom Repository-Stamm, nach `pip install -r code/requirements.txt`. R-1 ist in dieser Sitzung nachgerechnet, die
übrigen Fälle sind aus Code, Tests und Dokumenten gelesen und nicht ausgeführt.

**R-1 Dauerkontakt am Triphasik-Punkt (120°, 240°), Referenz-Engine**

- Konfiguration: Referenzsatz, Standardstart (z₀ = −M·g/K), Δt = 50 µs, Fenster 5–15 s.
- Größen und Sollwerte: `F_mean` 6,376500 N (Kontrollgröße), `F_skew` 0,066794, `liftoff` 0, `F_max` 7,491922 N,
  `F_min` 5,330390 N, `peak_ratio` (Asymmetrieverhältnis A) 1,066257.
- Quelle: [`data/finesweep_2deg_120_240.csv`](../data/finesweep_2deg_120_240.csv), Zeile 222 (Spaltennamen in Zeile 1).
  Die Zeile stammt aus `finesweep.py`; der Punkt liegt nicht auf dem 19×19-Raster der Engine.
- Aufruf: `python3 -c "import sys; sys.path.insert(0, 'code'); import pcmms_v3a_phasen_sweep as e; print(e.simulate_point(120.0, 240.0))"`.
  Eine Kommandozeilenoption für einen Einzelpunkt hat die Engine nicht; der Import allein startet keine Rechnung und
  schreibt keine Ergebnisdatei.
- Laufzeit: „Engine: ca. 2 s“ je Punkt (`code/linear_solver.py`, Z. 42); in dieser Sitzung rund 1 s.
- Zulässige Abweichung: Gleichheit auf die sechs Nachkommastellen der CSV, also ±5·10⁻⁷. Herkunft ist die Rundung der
  Datei (`float_format='%.6f'`); eine Toleranz für die Nachrechnung legt das Repository nicht fest. Zeitschritt, Fenster
  und Start sind fest; ohne Liftoff ist der Zustand eindeutig. Dass an diesem Punkt alle Starts, der halbe Zeitschritt
  und der ereignisgenaue Löser dieselben Kenngrößen geben, hält `rechnungen/engine/PROTOKOLL.md` fest (Z. 73–86).
- **Nachgerechnet am 10.11.2026:** alle sechs Spalten auf sechs Nachkommastellen gleich; größte Abweichung vor der
  Rundung 1,8·10⁻⁷ (`F_min`); `F_mean` − M·g = 6·10⁻¹³ N. Rechenzeit von `simulate_point` 0,9 bis 1,0 s ohne
  Programmstart (Python 3.13.18, numpy 2.5.4, scipy 1.18.1, 4 Kerne). Das ist der eine Einzelpunkt, den der Auftrag
  zulässt; es gab keinen Sweep.

**R-2 Analytische Lösung gegen die drei Datensätze**

- Konfiguration: Referenzsatz; alle 851 Punkte der drei CSV-Dateien, verglichen werden die 442 liftoff-freien
  (12 von 361, 400 von 441, 30 von 49).
- Größen und Sollwerte: Einteilung liftoff-frei oder abhebend ohne Abweichung; größte Abweichung von F_min, F_max,
  Schiefe und A höchstens 6·10⁻⁶; Schlusszeile „Ergebnis: bestanden“.
- Quelle: `code/linear_solver.py`, Z. 45–46; [`README.md`](../README.md), Z. 137.
- Aufruf: `python3 code/linear_solver.py --validate`
- Laufzeit: ca. 5 s (README, Z. 204).
- Zulässige Abweichung: Der Code lässt 1·10⁻⁴ zu (N bzw. dimensionslos; 1·10⁻⁵ N für |`F_mean` − M·g|, Z. 266); die
  engere Angabe 6·10⁻⁶ steht nur im Text. Herkunft: gleiche Stichproben wie in der Engine (Δt = 50 µs) und die Rundung
  der Dateien.
- Hinweis: Die 409 Liftoff-Punkte gehen nur als Einteilung ein. Geprüft wird gegen die abgelegten Werte; im
  Liftoff-Bereich hängen sie von der Startbedingung ab (R-4).

**R-3 Zeltkurve im Kontaktast (Schnitt φ₂ = 100° … 140° bei φ₃ = 240°)**

- Konfiguration: Referenzsatz, 21 Punkte, analytische Lösung.
- Größen und Sollwerte: F_min 5,3304 N bei 120°, 0,7677 N bei 100°, 1,6176 N bei 140°; 2°-Sekanten an der Spitze
  0,2124 und 0,1952 N je Grad; Spannweite 4,5627 N.
- Quelle: [`praeregistrierung_v2_anhang.md`](praeregistrierung_v2_anhang.md), Zahlennachweis, Z. 1547; die Spannweite
  hält außerdem `tests/test_auslegung.py`, Z. 164, über das Auslegungswerkzeug fest (±6·10⁻⁵ N).
- Aufruf: `python3 code/linear_solver.py --section`
- Laufzeit: nicht angegeben; der Löser braucht „ca. 1 ms je Punkt“ (`code/linear_solver.py`, Z. 42).
- Zulässige Abweichung: die letzte gedruckte Stelle (±5·10⁻⁵); das folgt aus dem Ausgabeformat und ist im Repository
  nicht festgelegt. Die README nennt für dieselbe Kurve ≈ 0,23 und ≈ 0,19 N
  je Grad; das sind die Sekanten über 20°, nicht die über 2°.

**R-4 Satelliteninsel (35°, 116°), ereignisgenau – Fall im Liftoff-Bereich**

- Konfiguration: Referenzsatz; zwei Zustände am selben Punkt: Kontaktorbit (Start auf dem linearen Orbit) und
  Hüpfzustand (vom Standardstart aus).
- Größen und Sollwerte: Kontaktorbit mit Liftoff 0, F_min 0,3665 N, F_max 19,812 N, Schiefe 0,82305; Hüpfzustand mit
  Liftoff-Anteil 75,8154 %, F_max 39,473 N, Schiefe 1,69813.
- Quelle: `tests/test_ereignisloeser.py`, `test_satelliteninsel_bistabil`, Z. 101–120.
- Aufruf: `python3 -m pytest tests/test_ereignisloeser.py::test_satelliteninsel_bistabil -q` oder
  `python3 code/ereignisloeser.py --point 35 116 --orbit`
- Laufzeit: Kommandozeile ca. 5 s (README, Z. 207); für den einzelnen Test nicht angegeben.
- Zulässige Abweichung: die Toleranzen des Tests (F_min ±1·10⁻⁴ N, F_max ±1·10⁻³ N, Schiefe ±1·10⁻⁵, Liftoff-Anteil
  ±1·10⁻⁴ Prozentpunkte). Herkunft: „letzte angegebene Stelle der Referenz, höchstens 0,1 %“ (Kopf der Testdatei, Z. 5).
- **Hinweis.** Der Punkt liegt im Liftoff-Bereich. Dort ist die Karte nicht eindeutig: Es gibt mehrere stabile
  Zustände, und welcher erreicht wird, hängt von der Startbedingung ab ([`data/README.md`](../data/README.md),
  Z. 54–58; README, Z. 148–153). Als Referenzfall taugt der Punkt deshalb nur mit beiden Zuständen und ihren Starts.

**R-5 V1-Kandidat der Auslegung – andere Parameter als der Referenzsatz**

- Konfiguration: Restmasse 0,350 kg, drei Module zu je 0,100 kg, Hub 8 mm, 10 Hz, K = 1,5·10⁶ N/m, ζ = 0,05
  (`code/auslegung.py`, Z. 193).
- Größen und Sollwerte: Spannweite der Zeltkurve 0,560 N; kleinste Zellreserve 0,41137; Kontakteigenfrequenz 241,8 Hz.
- Quelle: `tests/test_auslegung.py`, Z. 242 (Spannweite über die Python-Schnittstelle, ±5·10⁻⁴ N) und Z. 494–495
  (Zellreserve und Eigenfrequenz über die Kommandozeile, ±1·10⁻⁵ und ±0,05 Hz).
- Aufruf: `python3 code/auslegung.py --candidate`, mit `--json` maschinenlesbar.
- Laufzeit: ca. 2 s (README, Z. 206).
- Zulässige Abweichung: die Toleranzen der Tests.
- Hinweis: Auslegungswert eines angenommenen Aufbaus, keine Vorhersage für V1 (README, Z. 122–123).

### 5.3 Was einem Dritten heute fehlt

- Die Engine hat keinen dokumentierten Weg zu einem Einzelpunkt (die README nennt nur den vollen Sweep mit 30 bis
  60 Minuten), und kein Test ruft sie auf.
- Für die Nachrechnung der Engine gegen ihre eigenen Datensätze legen die README-Dateien und `code/` keine Toleranz
  fest. `finesweep.py --validate` druckt Rechenwert und CSV-Wert nebeneinander, ohne Urteil und mit Exit-Code 0.
- `linear_solver.py --validate` gehört nicht zur Testsuite; der Lauf druckt die erreichten Höchstabweichungen, abgelegt
  ist davon nur das Urteil „bestanden“.
- Abgelegte Soll-Ausgaben gibt es, aber im Nachweisarchiv und nicht dort, wo ein Dritter beginnt.
- [`code/requirements.txt`](../code/requirements.txt) nennt fünf Pakete ohne Versionen; eine CI-Konfiguration gibt es
  nicht. Die dokumentierten Prüfumgebungen sind verschieden (Python 3.11 mit numpy 2.4 in
  [`abnahme_ap02_ap03.md`](abnahme_ap02_ap03.md), Python 3.13 mit NumPy 2.5 in
  [`ap11_ap12_ap13_software.md`](ap11_ap12_ap13_software.md)).
- Laufzeiten sind nur für einen Teil der Aufrufe angegeben.

### 5.4 Was sich nicht als Referenzfall eignet

- Einzelne Liftoff-Punkte der Engine-Datensätze: Ihr Wert hängt von Start, Zeitschritt und Auswertungsreihenfolge ab.
  Am Punkt (0°, 0°) mit 75,8 % Liftoff weichen skalare und vektorisierte Fassung in `F_mean` um 1,7·10⁻⁴ N voneinander
  ab (`code/finesweep.py`, Z. 4–5).
- `data/regime_2400s.csv` und `data/regime_2400s_dt2.csv`: Das Erzeugungsskript ist nicht überliefert.
- `data/sweep_7x7_sinus.csv`: Das erzeugende Skript liegt nicht im Repository; die Amplitude ist aus den Daten
  rekonstruiert.

## 6. Nicht bearbeitet

- **G-5, Messkampagne der Linie A konkretisieren.** Hardware, Messkette und Schutzkonzept sind die Arbeitspakete AP-01,
  AP-06 und AP-05 und hängen an Entscheidungen des Autors, aus denen kein Entwicklungsauftrag entsteht
  ([`arbeitsplan_status.md`](arbeitsplan_status.md), „Offene Entscheidungen des Autors“); diese Notiz plant dazu nichts.
- **G-7, Unabhängigkeit als Stärke darstellen.** Die Außendarstellung des Projekts ist nicht Gegenstand des Repositorys.
- **G-8, Gesamturteil.** Eine Gesamtnote ohne Bezugsklasse wird nicht geführt ([`neuheitsgrad.md`](neuheitsgrad.md) §3).

## 7. Offene Entscheidungen des Autors

Sie werden nur geführt; aus ihnen entsteht kein Entwicklungsauftrag. Sie stehen auch in
[`arbeitsplan_status.md`](arbeitsplan_status.md).

- **E-1** Sichtprüfung der geprüften Arbeiten durch den Autor. Sie ist Voraussetzung für jede Aufnahme ins
  Literaturverzeichnis ([`neuheitsgrad.md`](neuheitsgrad.md) §9). Für a) liegen Verlagsseite und Volltext vor
  (Abschnitt 2.1); für b) und c) fehlt die Bestätigung auf der Verlagsseite, für b) auch die Lektüre des Aufsatzes.
- **E-2** Arbeitspapier v2.6 mit eingearbeiteter Berichtigung (Variante B des Auftrags) jetzt, gebündelt mit der
  Primärquellenprüfung nach Nr. 42 der Offenen Punkte, oder vorerst nicht. Was dann zu ändern wäre, steht in
  Abschnitt 3.3.
- **E-3** Eine Seite mit Referenzfällen zum Nachrechnen anlegen oder nicht (Abschnitt 5).
- **E-4** Die Recherche im Strang vibrationsgetriebener Systeme mit inneren Massen beginnen oder weiter zurückstellen
  (AP-16).

Unberührt bleiben die offenen Entscheidungen D-2 bis D-6 der
[Abgleichnotiz vom 29.10.2026](abgleichnotiz_2026-10-29_v4.md), AP-01, AP-04 bis AP-07 und AP-18 sowie Nr. 42 der
Offenen Punkte.
