# PCMMS – Arbeitspapier v2.3

**Wellenformstatistik der unilateralen Kontaktkraft in phasenkontrollierten Mehrmassensystemen** – Messrahmen, numerische Referenzfälle und Artefaktkontrolle. Prä-experimentelles Arbeitspapier, Stand 25.09.2026; eigene Messdaten liegen nicht vor.

- PDF: [`PCMMS_Arbeitspapier_v2_3.pdf`](PCMMS_Arbeitspapier_v2_3.pdf)
- Quelle: `PCMMS_Arbeitspapier_v2_3.tex`, `references.bib`, Abbildungen in `Plots/`
- Belege der Korrektur in v2.3: [`nachrechnung_2026-09-13/`](nachrechnung_2026-09-13/)
- Offene Punkte: [`PCMMS_Arbeitspapier_Offene_Punkte.md`](PCMMS_Arbeitspapier_Offene_Punkte.md)
- Bezeichnungen und Zuordnung zu den Symbolen des Forschungsrahmens: [`../formelverzeichnis/`](../formelverzeichnis/)

Gegenüber v2.2 (Zenodo, als Working Paper) ist nur die Deutung des Basislinienresiduums korrigiert: Randterm des Auswertefensters statt „langsamer Modulation“, Vorzeichen der Residuen gemischt statt „alle negativ“. Einzelheiten im Versionshinweis des Papiers.

## Bauen

```sh
xelatex PCMMS_Arbeitspapier_v2_3.tex
bibtex PCMMS_Arbeitspapier_v2_3
xelatex PCMMS_Arbeitspapier_v2_3.tex
xelatex PCMMS_Arbeitspapier_v2_3.tex
```

Benötigt eine TeX-Installation mit deutscher Babel-Unterstützung und Latin Modern (`lmodern`). Die beiliegende PDF wurde ohne `lmodern.sty` gebaut: Text in Latin Modern (OpenType), Formeln in Computer Modern. Die Abbildungen sind Rasterbilder aus der Vorschau von v2.1, keine Vektororiginale.
