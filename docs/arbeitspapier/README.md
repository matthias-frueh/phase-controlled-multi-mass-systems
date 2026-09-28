# PCMMS – Arbeitspapier v2.4

**Wellenformstatistik der unilateralen Kontaktkraft in phasenkontrollierten Mehrmassensystemen** – Messrahmen, numerische Referenzfälle und Artefaktkontrolle. Prä-experimentelles Arbeitspapier, Stand 26.09.2026; eigene Messdaten liegen nicht vor.

- PDF: [`PCMMS_Arbeitspapier_v2_4.pdf`](PCMMS_Arbeitspapier_v2_4.pdf)
- Quelle: `PCMMS_Arbeitspapier_v2_4.tex`, `references.bib`, Abbildungen in `Plots/`
- Belege der Korrektur in v2.4: [`gegenprobe_2026-09-26/`](gegenprobe_2026-09-26/)
- Belege der Korrektur in v2.3: [`nachrechnung_2026-09-13/`](nachrechnung_2026-09-13/)
- Offene Punkte: [`PCMMS_Arbeitspapier_Offene_Punkte.md`](PCMMS_Arbeitspapier_Offene_Punkte.md)
- Bezeichnungen und Zuordnung zu den Symbolen des Forschungsrahmens: [`../formelverzeichnis/`](../formelverzeichnis/). Die mit v2.4 neuen Symbole stehen vorerst nur im Symbolverzeichnis des Papiers.

## Änderungen

**v2.4 (26.09.2026).** Die Vorzeichenregel der Schiefe – negative Schiefe nur, wenn kein Modulpaar gleichphasig läuft – ist als Aussage über den Mechanismus zurückgezogen. Eine Gegenprobe mit einem einzelnen Modul zeigt, dass das Vorzeichen von der Kontaktübertragung abhängt: Beim Referenzparametersatz liegt die zweite Harmonische auf der Kontaktresonanz (2f/f_n = 1,013), und schon bei gut 5 % geringerer Kontaktsteifigkeit ist ein einzelnes Modul im Dauerkontakt linksschief; bei k = 6 944 N/m wird auch die Zweiergruppe (0°, 180°) bei vollem Hub negativ. Außerdem korrigiert: zweite statt dritte Harmonische auf der Resonanz; das frühere Auslegungsfenster 1 ≲ 3f/f_n ≲ 3 ist durch die Resonanzlinien 3f/f_n = 3/j ersetzt; die Näherung für steifen Kontakt lautet N ≈ Mg + (M/3)·Σz̈ (Vorzeichen). Neu sind die Triadenzerlegung der Schiefe im Dauerkontakt und ein Hinweis auf kleine bistabile Inseln der Phasenebene, in denen kein Punkt des 19×19-Rasters liegt. Die Zahlen des Rasters bleiben unverändert. Einzelheiten im Versionshinweis des Papiers.

**v2.3 (25.09.2026).** Deutung des Basislinienresiduums korrigiert: Randterm des Auswertefensters statt „langsamer Modulation“, Vorzeichen der Residuen gemischt statt „alle negativ“.

## Bauen

```sh
xelatex PCMMS_Arbeitspapier_v2_4.tex
bibtex PCMMS_Arbeitspapier_v2_4
xelatex PCMMS_Arbeitspapier_v2_4.tex
xelatex PCMMS_Arbeitspapier_v2_4.tex
```

Benötigt eine TeX-Installation mit deutscher Babel-Unterstützung und Latin Modern (`lmodern`). Die beiliegende PDF wurde ohne `lmodern.sty` gebaut: Text in Latin Modern (OpenType), Formeln in Computer Modern. Die Abbildungen sind Rasterbilder, keine Vektororiginale.
