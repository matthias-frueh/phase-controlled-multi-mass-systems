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
