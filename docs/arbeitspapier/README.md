# PCMMS – Arbeitspapier v2.5

**Wellenformstatistik der unilateralen Kontaktkraft in phasenkontrollierten Mehrmassensystemen** – Messrahmen, numerische Referenzfälle und Artefaktkontrolle. Prä-experimentelles Arbeitspapier, Stand 16.10.2026; eigene Messdaten liegen nicht vor.

- PDF: [`PCMMS_Arbeitspapier_v2_5.pdf`](PCMMS_Arbeitspapier_v2_5.pdf) – Stand 16.10.2026, Lesefassung mit den Nachträgen
  vom 2. und 3. Oktober 2026 (begrenzte Aussagen, Literatur- und Rückzugsvermerke, offene Hardwareentscheidungen,
  Profilasymmetrie und Harmonische). PDF und Quelltext stimmen überein.
- Quelle: `PCMMS_Arbeitspapier_v2_5.tex`, `references.bib`, Abbildungen in `Plots/`
- Belege der Korrektur in v2.4: [`gegenprobe_2026-09-26/`](gegenprobe_2026-09-26/)
- Belege der Korrektur in v2.3: [`nachrechnung_2026-09-13/`](nachrechnung_2026-09-13/)
- Offene Punkte: [`PCMMS_Arbeitspapier_Offene_Punkte.md`](PCMMS_Arbeitspapier_Offene_Punkte.md)
- Bezeichnungen und Zuordnung zu den Symbolen des Forschungsrahmens: [`../formelverzeichnis/`](../formelverzeichnis/). Die mit v2.4 neuen Symbole führt das Formelverzeichnis ab v2.7.

## Änderungen

**v2.5 (16.10.2026).** Lesefassung der Nachträge vom 2. und 3. Oktober 2026, die bisher nur im Quelltext von v2.4 standen: Reichweite der Kontrollgröße begrenzt, Definition von F_min − ⟨N⟩, Antrieb, Kontakt und Nennlast als offene Entscheidungen, der Wert am Punkt (0°, 208,4°) als Folge eines von der Festschritt-Integration verlängerten Einschwingens, Profilasymmetrie und Harmonische, Lücken- und Beitragsaussagen auf Suchbefunde zurückgenommen. Gegenüber diesem Quelltext ändern sich nur Titelblatt, Versionshinweis und Präambel. Einzelheiten im Versionshinweis des Papiers.

**v2.4 (26.09.2026).** Die Vorzeichenregel der Schiefe – negative Schiefe nur, wenn kein Modulpaar gleichphasig läuft – ist als Aussage über den Mechanismus zurückgezogen. Eine Gegenprobe mit einem einzelnen Modul zeigt, dass das Vorzeichen von der Kontaktübertragung abhängt: Beim Referenzparametersatz liegt die zweite Harmonische auf der Kontaktresonanz (2f/f_n = 1,013), und schon bei gut 5 % geringerer Kontaktsteifigkeit ist ein einzelnes Modul im Dauerkontakt linksschief; bei k = 6 944 N/m wird auch die Zweiergruppe (0°, 180°) bei vollem Hub negativ. Außerdem korrigiert: zweite statt dritte Harmonische auf der Resonanz; das frühere Auslegungsfenster 1 ≲ 3f/f_n ≲ 3 ist durch die Resonanzlinien 3f/f_n = 3/j ersetzt; die Näherung für steifen Kontakt lautet N ≈ Mg + (M/3)·Σz̈ (Vorzeichen). Neu sind die Triadenzerlegung der Schiefe im Dauerkontakt und ein Hinweis auf kleine bistabile Inseln der Phasenebene, in denen kein Punkt des 19×19-Rasters liegt. Die Zahlen des Rasters bleiben unverändert. Einzelheiten im Versionshinweis des Papiers.

**v2.3 (25.09.2026).** Deutung des Basislinienresiduums korrigiert: Randterm des Auswertefensters statt „langsamer Modulation“, Vorzeichen der Residuen gemischt statt „alle negativ“.

## Bauen

Vom Repository-Stamm aus:

```sh
(cd docs/arbeitspapier \
  && xelatex -interaction=nonstopmode -halt-on-error PCMMS_Arbeitspapier_v2_5.tex \
  && bibtex PCMMS_Arbeitspapier_v2_5 \
  && xelatex -interaction=nonstopmode -halt-on-error PCMMS_Arbeitspapier_v2_5.tex \
  && xelatex -interaction=nonstopmode -halt-on-error PCMMS_Arbeitspapier_v2_5.tex)
```

Benötigt XeLaTeX mit deutschen Trennmustern und Latin Modern OpenType (Debian/Ubuntu: `texlive-xetex texlive-latex-extra texlive-lang-german fonts-lmodern`); `lmodern.sty` ist dafür nicht nötig. Unter pdfLaTeX gilt weiter der Weg mit `fontenc` und `lmodern`. Die beiliegende PDF: Text in Latin Modern (OpenType), Formeln in Computer Modern. Die Abbildungen sind Rasterbilder, keine Vektororiginale.
