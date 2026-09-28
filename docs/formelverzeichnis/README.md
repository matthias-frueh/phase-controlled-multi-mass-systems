# PCMMS – Symbol- und Formelverzeichnis v2.7

**Symbolverzeichnis und Formelzeichen im PCMMS-Forschungsrahmen** – Kontaktkraft, Wellenformstatistik und Messmodell. Arbeitsstand 28.09.2026.

- PDF: [`PCMMS_Formelverzeichnis_v2_7.pdf`](PCMMS_Formelverzeichnis_v2_7.pdf)
- Quelle: [`PCMMS_Formelverzeichnis_v2_7.tex`](PCMMS_Formelverzeichnis_v2_7.tex)

Gegenüber v2.6 neu: die Größen aus [Arbeitspapier v2.4](../arbeitspapier/) – Ordnung m einer Harmonischen, komplexe Harmonische der Kontaktkraft, Phasenfaktor Φ_m, Kontaktübertragung H_c mit Frequenzverhältnis ϱ_m und Hubfaktor ξ_A. Dazu die Triadenzerlegung des dritten Moments im Dauerkontakt (Abschnitt 5.8), die Kontaktübertragung (Abschnitt 7.4), die Gegenprobe vom 26.09.2026 in der Codezuordnung (Anhang B.3) und die Zuordnung der neuen Zeichen des Arbeitspapiers (Anhang A). Die Definitionen der v2.6 bleiben unverändert.

v2.6 (26.09.2026): relativer Fensterrandterm δ_w, Quadraturanteil δ_Q und Schwerpunktschranke mit v_S,max (Abschnitt 3.2), Zuordnung der Bezeichnungen des Arbeitspapiers v2.3 (Anhang A), Nachrechnung vom 13.09.2026 in der Codezuordnung (Anhang B.2).

## Bauen

```sh
pdflatex PCMMS_Formelverzeichnis_v2_7.tex
pdflatex PCMMS_Formelverzeichnis_v2_7.tex
```

Benötigt Latin Modern (`lmodern`) und die Pakete der Präambel. Die beiliegende PDF wurde ohne `lmodern.sty` mit XeLaTeX gebaut: Text in Latin Modern (OpenType), Formeln in Computer Modern.
