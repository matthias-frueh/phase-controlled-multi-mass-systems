# PCMMS – Symbol- und Formelverzeichnis v2.6

**Symbolverzeichnis und Formelzeichen im PCMMS-Forschungsrahmen** – Kontaktkraft, Wellenformstatistik und Messmodell. Arbeitsstand 26.09.2026.

- PDF: [`PCMMS_Formelverzeichnis_v2_6.pdf`](PCMMS_Formelverzeichnis_v2_6.pdf)
- Quelle: [`PCMMS_Formelverzeichnis_v2_6.tex`](PCMMS_Formelverzeichnis_v2_6.tex)

Gegenüber v2.5 neu: relativer Fensterrandterm δ_w, Quadraturanteil δ_Q und Schwerpunktschranke mit v_S,max (Abschnitt 3.2), Zuordnung der Bezeichnungen des [Arbeitspapiers v2.3](../arbeitspapier/) (Anhang A) und die Nachrechnung vom 13.09.2026 in der Codezuordnung (Anhang B.2). Die Definitionen der v2.5 bleiben unverändert.

## Bauen

```sh
pdflatex PCMMS_Formelverzeichnis_v2_6.tex
pdflatex PCMMS_Formelverzeichnis_v2_6.tex
```

Benötigt Latin Modern (`lmodern`) und die Pakete der Präambel. Die beiliegende PDF wurde ohne `lmodern.sty` mit XeLaTeX gebaut: Text in Latin Modern (OpenType), Formeln in Computer Modern.
