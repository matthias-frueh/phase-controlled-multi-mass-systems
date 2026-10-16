# PCMMS – Symbol- und Formelverzeichnis v2.8

**Symbolverzeichnis und Formelzeichen im PCMMS-Forschungsrahmen** – Kontaktkraft, Wellenformstatistik und Messmodell. Arbeitsstand 16.10.2026.

- PDF: [`PCMMS_Formelverzeichnis_v2_8.pdf`](PCMMS_Formelverzeichnis_v2_8.pdf) – Stand 16.10.2026, Lesefassung mit den
  Nachträgen vom Oktober 2026 (u. a. Rückzugsvermerk, Linie C, Status der Architekturebenen, Literaturhinweise). PDF
  und Quelltext stimmen überein.
- Quelle: [`PCMMS_Formelverzeichnis_v2_8.tex`](PCMMS_Formelverzeichnis_v2_8.tex)

## Änderungen

v2.8 (16.10.2026): Lesefassung der Nachträge vom Oktober 2026 – Statusvermerk zu den Architekturebenen, Minimalkraft relativ zum Laufmittel F_min − ⟨N⟩ und Trennung von Π_N und A_pk in den Phasenkarten, Rückzugsvermerk im Glossar, Anschluss an Linie B und C, Parameterstand des V1-Kandidaten und Hubangaben als Spitze-Spitze (Anhang B), Literaturhinweise. Die Definitionen der Größen der v2.7 bleiben unverändert; neu sind F_min − ⟨N⟩ und die Regel für Hubangaben, Linie C ist neu umschrieben.

v2.7 (28.09.2026). Gegenüber v2.6 neu: die Größen aus [Arbeitspapier v2.4](../arbeitspapier/) – Ordnung m einer Harmonischen, komplexe Harmonische der Kontaktkraft, Phasenfaktor Φ_m, Kontaktübertragung H_c mit Frequenzverhältnis ϱ_m und Hubfaktor ξ_A. Dazu die Triadenzerlegung des dritten Moments im Dauerkontakt (Abschnitt 5.8), die Kontaktübertragung (Abschnitt 7.4), die Gegenprobe vom 26.09.2026 in der Codezuordnung (Anhang B.3) und die Zuordnung der neuen Zeichen des Arbeitspapiers (Anhang A). Die Definitionen der v2.6 bleiben unverändert.

v2.6 (26.09.2026): relativer Fensterrandterm δ_w, Quadraturanteil δ_Q und Schwerpunktschranke mit v_S,max (Abschnitt 3.2), Zuordnung der Bezeichnungen des Arbeitspapiers v2.3 (Anhang A), Nachrechnung vom 13.09.2026 in der Codezuordnung (Anhang B.2).

## Bauen

Vom Repository-Stamm aus:

```sh
(cd docs/formelverzeichnis \
  && for i in 1 2 3; do xelatex -interaction=nonstopmode -halt-on-error PCMMS_Formelverzeichnis_v2_8.tex || exit 1; done)
```

Benötigt XeLaTeX mit deutschen Trennmustern, Latin Modern OpenType und die Pakete der Präambel (Debian/Ubuntu: `texlive-xetex texlive-latex-extra texlive-lang-german fonts-lmodern`); `lmodern.sty` ist dafür nicht nötig. Unter pdfLaTeX gilt weiter der Weg mit `inputenc`, `fontenc` und `lmodern`. Die beiliegende PDF: Text in Latin Modern (OpenType), Formeln in Computer Modern.
