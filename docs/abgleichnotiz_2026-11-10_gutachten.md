# PCMMS – Abgleichnotiz 2026-11-10: Gutachten und Gegenprüfung

Projekt: Phasenkontrollierte Mehrmassensysteme (PCMMS)
Autor: Matthias Früh, ORCID 0009-0005-9984-4207
Erstellt: 10.11.2026, Claude Code, nach Auftrag des Autors vom selben Tag
Status: Notiz, kein Arbeitsauftrag
Zuordnung: AP-16 (Literaturbestand); berührt die Offenen Punkte Nr. 21 und 42 des Arbeitspapiers
Lizenz: CC BY 4.0 (Ordner docs/, siehe LICENSE-CC-BY-4.0)

> **Vermerk (10.11.2026).** Abgleich am Repository-Stand `51f79a2` (`main`, 03.11.2026, PR #29). Zeilenangaben ohne
> Dateinamen („Z. …“) beziehen sich auf den Quelltext des Arbeitspapiers v2.5,
> [`arbeitspapier/PCMMS_Arbeitspapier_v2_5.tex`](arbeitspapier/PCMMS_Arbeitspapier_v2_5.tex), an diesem Stand. Die beiden
> abgeglichenen Texte und der Auftrag an Claude Code liegen nicht im Repository. Die Notiz ändert keine Zahl, keine
> Hypothese, keinen Code und keine Daten; Arbeitspapier (Quelltext und PDF) und Literaturverzeichnis bleiben
> unverändert (Variante A des Auftrags, kein Neusatz). Alle Zahlen des Repositorys sind Simulation; Messdaten
> existieren nicht.

## 0. Zweck und Quellenlage

Dem Autor lagen am 10.11.2026 zwei Texte vor: ein simuliertes Fachgutachten zu PCMMS (revidierte Fassung, Urteil
„Moderate Revision“) und eine Gegenprüfung dazu. Beide beziehen sich wechselseitig aufeinander; sie sind Hinweise, keine
unabhängige Begutachtung und kein Beleg. Diese Notiz hält fest, welche ihrer Aussagen den Repository-Stand treffen, und
ändert weder eine Regel noch einen Plan.

Die Texte selbst sind nicht abgelegt. Ihre Aussagen sind unter den Arbeitskennungen G-1 bis G-8 sinngemäß
wiedergegeben (Abschnitt 1). Die Kennungen E-1 bis E-4 in Abschnitt 7 bezeichnen offene Entscheidungen des Autors; sie
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
| **G-4** Beitragsformel: Rekombination bekannter Bausteine (Phasensteuerung, Mehrmassensystem, Kontaktkraft) unter methodischer Kontrolle (ruhender Körper, Nullkontrolle, Präregistrierung) mit dem Ziel der Wellenform-Charakterisierung, nicht der Entdeckung eines neuen Effekts. | **Nicht übernommen; am Repository gemessen.** Die Formel trifft den Verzicht auf einen Effektanspruch und die Selbstbeschreibung als Rekombination, weicht aber in Status der Präregistrierung, Zielgrößen, Gewichtung und Begriffen ab. | Abschnitt 4 |
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
| b) „Olgac (2005)“ | kein Aufsatz dieser Form; gefunden: Mikus, Olgac, Sipahi 2009, Control Engineering Practice 17 (1), S. 210–220 | **nein** – DOI aufgelöst und Registereintrag gelesen, die Verlagsseite verlangt eine Captcha-Eingabe und ist nicht gelesen | nur Katalogeintrag (Aufsatz); daneben Abstract der Konferenzfassung und Patentanmeldung | `10.1016/j.conengprac.2008.07.002` |
| c) „Xiong & Xu (2015)“ | Zhan, Xu 2015, Advances in Mechanical Engineering 7 (3), Artikel 1687814015573766; „Xiong“ ist der Vorname des Erstautors | **nein** – DOI aufgelöst und Registereintrag gelesen, die Verlagsseite verlangt eine Captcha-Eingabe und ist nicht gelesen | Abstract (im Registereintrag) | `10.1177/1687814015573766` |

Die Angabe in Anhang C, zu „Korendiy et al. 2026“ sei keine Arbeit dieses Jahres auffindbar (Z. 5860–5862, Stichtag
4. und 5. September 2026, Z. 5757), ist damit überholt: Die Arbeit ist am 08.06.2026 erschienen, die Suche hat sie nicht
gefunden. Für b) und c) steht die Bestätigung auf der Verlagsseite aus; im Browser ist sie eine Sache von Minuten
(E-1).

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
Antrieb mit bewegten Massen selbst trägt, drei bewegte Massen, die relative Phase als wichtigste Stellgröße, eine nicht
harmonische Bewegung aus der Kurbelkinematik und eine reine Simulationsstudie an einem idealisierten Modell. Zielgröße
ist dort die Bahn des Arbeitsorgans, nicht die Wellenform einer Kontaktkraft; gestellt wird die Phase zwischen zwei
Erregerkanälen mit je einer Hilfsmasse, und der Körper soll schwingen, auf beidseitig viskoelastischen Stützen ohne
einseitigen Kontakt. Eine Kraft an Auflage oder Fundament wird nicht ausgewertet, und eine durch einen Erhaltungssatz
festgelegte Kontrollgröße kommt im Volltext nicht vor.

Die Arbeit nennt in Einleitung und Literaturliste eigene Vorarbeiten der Gruppe zur Schubkurbel-Erregung. Sie sind hier
weder geprüft noch als Kandidaten aufgenommen (E-4). In der Literaturliste steht auch Osadchyy et al. 2023, das im
Literaturverzeichnis des Arbeitspapiers geführt ist.

### 2.2 b) „Olgac (2005)“

Einen Aufsatz „Olgac (2005)“ hat die Prüfung nicht ergeben. Die Registersuche nach Titel und Autoren liefert einen
Zeitschriftenaufsatz von 2009 und eine Konferenzfassung von 2003; aus dem Jahr 2005 stammt die Veröffentlichung einer
Patentanmeldung derselben drei Personen, die mutmaßliche Herkunft der Angabe. Zitierfähig wäre der Aufsatz.

| Feld | Inhalt |
|---|---|
| Bibliografie | Oldrich Mikus, Nejat Olgac, Rifat Sipahi: „An actively controlled harmonic force generator“. Control Engineering Practice, Band 17, Heft 1 (Januar 2009), S. 210–220; ISSN 0967-0661; Elsevier. DOI `10.1016/j.conengprac.2008.07.002`. Angaben nach dem Registereintrag. |
| Prüfweg | Registereintrag <https://api.crossref.org/works/10.1016/j.conengprac.2008.07.002>: Autoren, Titel, Zeitschrift, Band, Heft, Seiten, Jahr. <https://doi.org/10.1016/j.conengprac.2008.07.002> leitet weiter (302) auf <https://linkinghub.elsevier.com/retrieve/pii/S0967066108001238> (200), eine Weiterleitungsseite des Verlags, die nur den Titel und die Kennung (PII) des Artikels nennt. Die Artikelseite <https://www.sciencedirect.com/science/article/pii/S0967066108001238> antwortet mit 403 und einer Captcha-Abfrage; sie ist nicht gelesen. Abruf 10.11.2026. **Bibliografisch geprüft: nein** – Registereintrag und DOI-Auflösung liegen vor, die Bestätigung auf der Verlagsseite fehlt. |
| Lesestand | Zeitschriftenaufsatz: nur Katalogeintrag (der Registereintrag enthält keinen Abstract). Nebenquellen, kein Ersatz für den Aufsatz: Abstract der Konferenzfassung im Registereintrag; Patentanmeldung im Volltext. |
| System | Aus dem Katalogeintrag nicht zu entnehmen. Konferenz-Abstract: Geräte mit umlaufenden Exzentermassen. Patentanmeldung: vier gleiche umlaufende Exzentermassen, paarweise gegenläufig; die Kraftanteile quer zur Wirklinie heben sich auf. |
| Bewegungsgesetz | Aus dem Katalogeintrag nicht zu entnehmen. Patentanmeldung: Umlauf mit im Idealfall konstanter Winkelgeschwindigkeit, also harmonische Kraft; die Drehzahl wird nur in Übergängen verändert. |
| Stellgröße | Aus dem Katalogeintrag nicht zu entnehmen. Konferenz-Abstract: Amplitude, Frequenz und Phasenwinkel der harmonischen Kraft. Patentanmeldung: die relative Winkellage φ („relative angular position“) zwischen zwei Gruppen der vier Massen stellt die Kraftamplitude (Spitzenwert 4·m·ω²·r·cos(φ/2), von null bei φ = π bis 4·m·ω²·r bei φ = 0); die Drehzahl stellt die Frequenz; die Phase der Kraft gegen ein Bezugssignal wird über vorübergehende Drehzahländerungen gestellt. |
| Zielgröße | Aus dem Katalogeintrag nicht zu entnehmen. Konferenz-Abstract und Patentanmeldung: eine harmonische Kraft (nach der Patentanmeldung längs einer festen Achse) mit einstellbarer Amplitude (null bis F_max), Frequenz (rund ±10 % um die Nennfrequenz) und Phase (0 bis 2π gegen ein gegebenes harmonisches Signal), zur Erregung oder zur Tilgung harmonischer Schwingungen einer Struktur. |
| Körper | Aus dem Katalogeintrag nicht zu entnehmen; in den Nebenquellen kein ruhender Körper auf einer einseitigen Auflage genannt. |
| Kraft an Auflage oder Fundament | Aus dem Katalogeintrag nicht zu entnehmen. In den Nebenquellen ist die erzeugte resultierende Kraft selbst die Zielgröße; nach der Patentanmeldung wird sie am Prototyp mit einem Kraftaufnehmer gemessen. Eine Auflagekraft ist nicht genannt. |
| Art der Arbeit | Aus dem Katalogeintrag nicht zu entnehmen. Konferenz-Abstract: Entwurf und Steuerung, Erprobung an einem Prototyp. Patentanmeldung: Analytik und Versuche an einem gebauten Prototyp. |

**Prüfvermerk zur Herkunft der Angabe.** Konferenzfassung nach dem Registereintrag: O. Mikus, N. Olgac, R. Sipahi,
„An Actively Controlled Harmonic Force Generator“, in „Dynamic Systems and Control, Volumes 1 and 2“ (ASME 2003
International Mechanical Engineering Congress and Exposition, Washington, DC, 15.–21.11.2003), S. 31–40,
DOI `10.1115/imece2003-41410`; die DOI leitet auf `asmedigitalcollection.asme.org` weiter, die Seite ist nicht
abgerufen. Patentanmeldung: US 2005/0077845 A1, „Actively controlled harmonic force generator“, Erfinder Nejat Olgac,
Oldrich Mikus, Rifat Sipahi, angemeldet 20.08.2004, veröffentlicht 14.04.2005, gelesen unter
<https://patents.google.com/patent/US20050077845A1/en>. Die Patentanmeldung ist kein Literatureintrag.

**Abgrenzung zu PCMMS.** Der Aufsatz selbst ist nicht gelesen; die folgende Einordnung stützt sich nur auf den Abstract
der Konferenzfassung und die Patentanmeldung. Gemeinsam sind mehrere bewegte Massen, deren gegenseitige Winkellage eine
resultierende Kraft formt. Zielgröße ist dort eine harmonische Kraft mit einstellbarer Amplitude, Frequenz und Phase,
nicht die Wellenform einer einseitigen Kontaktkraft; zu ruhendem Körper, Kontaktverlust und einer Kontrollgröße sagen
die gelesenen Quellen nichts.

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
