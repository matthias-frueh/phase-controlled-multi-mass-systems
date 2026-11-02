# PCMMS – Symbol- und Formelverzeichnis v2.8

**Symbolverzeichnis und Formelzeichen im PCMMS-Forschungsrahmen** – Kontaktkraft, Wellenformstatistik und Messmodell. Arbeitsstand 16.10.2026.

- PDF: [`PCMMS_Formelverzeichnis_v2_8.pdf`](PCMMS_Formelverzeichnis_v2_8.pdf) – Stand 16.10.2026, Lesefassung mit den
  Nachträgen vom Oktober 2026 (u. a. Rückzugsvermerk, Linie C, Status der Architekturebenen, Literaturhinweise). PDF
  und Quelltext stimmen überein.
- Quelle: [`PCMMS_Formelverzeichnis_v2_8.tex`](PCMMS_Formelverzeichnis_v2_8.tex)

**Redaktioneller Neusatz (02.11.2026).** Die PDF wird wie das Arbeitspapier mit pdfLaTeX und eingebetteten
Type-1-Schriften neu erzeugt, damit die Schriftwiedergabe auf Android zuverlässiger ist.
Unicode-Zuordnungen der Schriften unterstützen Kopieren und Suchen. Fachstand und Version bleiben v2.8.
Die Silbentrennung folgt den deutschen Trennmustern (ngerman) mit Ausnahmen für Zusammensetzungen wie
Kontakt-übertragung; der Zenodo-DOI im Änderungsvermerk wird nicht mehr getrennt.

## Änderungen

v2.8 (16.10.2026): Lesefassung der Nachträge vom Oktober 2026 – Statusvermerk zu den Architekturebenen, Minimalkraft relativ zum Laufmittel F_min − ⟨N⟩ und Trennung von Π_N und A_pk in den Phasenkarten, Rückzugsvermerk im Glossar, Anschluss an Linie B und C, Parameterstand des V1-Kandidaten und Hubangaben als Spitze-Spitze (Anhang B), Literaturhinweise. Die Definitionen der Größen der v2.7 bleiben unverändert; neu sind F_min − ⟨N⟩ und die Regel für Hubangaben, Linie C ist neu umschrieben.

v2.7 (28.09.2026). Gegenüber v2.6 neu: die Größen aus [Arbeitspapier v2.4](../arbeitspapier/) – Ordnung m einer Harmonischen, komplexe Harmonische der Kontaktkraft, Phasenfaktor Φ_m, Kontaktübertragung H_c mit Frequenzverhältnis ϱ_m und Hubfaktor ξ_A. Dazu die Triadenzerlegung des dritten Moments im Dauerkontakt (Abschnitt 5.8), die Kontaktübertragung (Abschnitt 7.4), die Gegenprobe vom 26.09.2026 in der Codezuordnung (Anhang B.3) und die Zuordnung der neuen Zeichen des Arbeitspapiers (Anhang A). Die Definitionen der v2.6 bleiben unverändert.

v2.6 (26.09.2026): relativer Fensterrandterm δ_w, Quadraturanteil δ_Q und Schwerpunktschranke mit v_S,max (Abschnitt 3.2), Zuordnung der Bezeichnungen des Arbeitspapiers v2.3 (Anhang A), Nachrechnung vom 13.09.2026 in der Codezuordnung (Anhang B.2).

## Bauen

Vom Repository-Stamm aus:

```sh
(cd docs/formelverzeichnis \
  && latexmk -pdf -interaction=nonstopmode -halt-on-error \
       -outdir=../_build/formelverzeichnis PCMMS_Formelverzeichnis_v2_8.tex \
  && cp ../_build/formelverzeichnis/PCMMS_Formelverzeichnis_v2_8.pdf .)
```

Benötigt pdfLaTeX mit deutschen Trennmustern, `latexmk`, Latin Modern und die Pakete der Präambel
(Debian/Ubuntu: `texlive-latex-extra texlive-lang-german lmodern latexmk`).
Für die veröffentlichte PDF ist dieser pdfLaTeX-Bauweg maßgeblich; die Quelldatei unterstützt weiterhin XeLaTeX/LuaLaTeX.
Die beiliegende PDF verwendet eingebettete Type-1-Schriften mit Unicode-Zuordnung:
Latin Modern für Text und Formeln, ergänzt durch AMS-Symbole.
