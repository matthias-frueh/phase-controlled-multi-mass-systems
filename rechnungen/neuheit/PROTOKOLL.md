# P3 · Rolle „neuheit“ – Prüfprotokoll

> **Vermerk zur Übernahme (04.10.2026).** Protokoll aus der Gesamtprojektanalyse 10/2026, Stand 02.10.2026, unverändert bis auf Pfade und Quellenangaben. Geprüft wurde der Repository-Stand `cd7be6a` (28.09.2026) mit der Präregistrierung v2 vom 25./28.09.2026; die späteren Änderungen aus PR #13 und PR #14 (unter anderem Präregistrierung v2 mit Arbeitsfestlegungen, `code/auslegung.py`, `code/ereignisloeser.py`) sind nicht eingearbeitet. Alle Zahlen sind Simulation oder Analytik, keine Messdaten. Verweise wie „L1a-019“, „P1 §3“ oder „B01–B14“ zeigen auf Arbeitsdokumente der Analyse, die nicht im Repository liegen. Quellen außerhalb des Repositorys sind als „(lokaler Bestand, nicht im Repository)“ gekennzeichnet. Startbefehle und Grenzen je Gruppe: [`rechnungen/README.md`](../README.md).

Stand 02.10.2026 · ursprünglich lokal, jetzt unter `rechnungen/` · keine Websuche, Literatur nur aus dem Bestand

## 1 Gelesen (vollständig bzw. gezielt)

Kontext und Vorbefunde
- `(Arbeitsdokument der Analyse, nicht im Repository)` (vollständig; §2, §5–§8, §11, §12 F–H, §13)
- `(Arbeitsdokument der Analyse, nicht im Repository)` (vollständig; §3 Nachtrag: gültig 4c73fffc / faff8cf4)
- `(Arbeitsdokument der Analyse, nicht im Repository)` (vollständig); `p1/evidenzmatrix.csv` (gefiltert: Literatur, Neuheit, Beitrag, IP, Außenmaterial; u. a. L1a-079/080, L1b-037, L4-001…008, L4-073…079, L5a-090/092, L5b-024…036, L6a-002…067, L6b-026/043/055/063/069, L7-086)
- `(Arbeitsdokument der Analyse, nicht im Repository)`, `p2/empfehlungen.md` (vollständig); `p2/befunde.csv` (Befunde zu P2-1…P2-8 und Nachbarn: KM-01…04, KM-09…12, AUS-01/02/06/07/08/12/13/14, ENG-01/02/03/05/06/09/10, RT-01/02/03, STA-06…12, SYM-01…04, LB-10/11/13); `p2/auslegung/PROTOKOLL.md` (gezielt: Profilspektrum Z. 145–152, 240–266)
- `(Arbeitsdokument der Analyse, nicht im Repository)` (alle 14 Bündel, 88 Kandidaten, P2-1…P2-8)

Literaturbestand
- `docs/neuheitsgrad.md`, `docs/literaturabgleich_2026-09-12.md`, `docs/einordnung.md`, `docs/arbeitspapier/references.bib` (alle vollständig)
- AP v2.4 `docs/arbeitspapier/PCMMS_Arbeitspapier_v2_4.tex`: Kurzfassung Z. 56–117, §1.6 „Beitrag“ Z. 474–578, Kap. 2 „Stand der Forschung“ Z. 581–833, §4.8 Z. 1778–1860, Fazit Z. 4760–4780, Anhang C Z. 5319–5455; alle \cite-Stellen per Skript
- FV v2.7 `docs/formelverzeichnis/PCMMS_Formelverzeichnis_v2_7.tex` (Kopf Z. 39, Anhang Literatur Z. 886–895, gezielt Gleichrichtung)
- Literaturanker `(lokaler Bestand, nicht im Repository)` (vollständig) und Diff gegen 50010487
- Dissertation v2.1: `references.bib.txt` (Diff gegen AP-bib: identisch), Zitatschlüssel per Skript, Kap. 2 per grep
- Regimeanalyse v1.2 `(lokaler Bestand, nicht im Repository)` §9 (Impact-Oszillator-Literatur)
- Linie B: Notiz v5.2 `(lokaler Bestand, nicht im Repository)` §6, §9, §13; Forschungsrahmen v3.5 (Zusammenfassung, §1, §2, §17, Änderungslog)
- Messtechnik-Konzept `(lokaler Bestand, nicht im Repository)` (vollständig)
- Präreg v2 Entwurf (Z. 1–110 vollständig, Rest gezielt) und Anhang (gezielt: A2 Z. 147, DKD-R Z. 452–468, Zahlennachweis Z. 795–803)

Beitragsbehauptungen in aktiven Dokumenten
- `README.md`, `docs/expose_2026-09.md`, `docs/zehn_fragen.md`, `docs/werkstattbericht.md` (vollständig); `docs/was_ist_pcmms.md` Z. 100–207; `docs/archiv_vermerk_kernhypothese_v3.md` Z. 8–20; `docs/arbeitspapier/PCMMS_Arbeitspapier_Offene_Punkte.md` (gezielt)
- SOT 01.10. `(lokaler Bestand, nicht im Repository)` (vollständig); SOT 28.09. `(lokaler Bestand, nicht im Repository)` (gezielt)
- Linie-A-Projektbericht 01.10. `(lokaler Bestand, nicht im Repository)` (vollständig)
- Pitch 28.09. (vollständig), Master 28.09. Folien 1–28 (Text vollständig, Diagrammdaten übersprungen)
- Projektbeschreibung August `(lokaler Bestand, nicht im Repository)` (§7 Z. 262–275, §12 Z. 425–458, §13 Z. 470–490, §22 Z. 715–740, §26 Z. 799–870)
- IP: Patent Z korr. (§2, §6), Patent 1 korr. (§2), GM korr. (§2.4), Patent X (§2–§3), Patent Y (§2), GM2 (§2.5); Businessplan korr. (Z. 74–79, 318–322, 390–396, 575–590)
- `code/linear_solver.py` Docstring Z. 1–30 (Bewegungsgleichung mit wirksamer Anregung −μMā, Hinweis Dreizylinder-Massenausgleich)
- `(lokaler Bestand, nicht im Repository)` Z. 45–70 (Fudan-Angaben)

## 2 Eigene Skripte und Rechnungen

| Skript | Zweck | Ergebnis (Kurz) |
|---|---|---|
| `bibcheck.py` → `bibcheck_ausgabe.txt` | \cite gegen bib (AP, Diss), Feldvollständigkeit, AP-Anhang-C-Tabelle, Literaturabgleich-BibTeX gegen bib/AP, FV-Bibliografie | Alle 22 AP-Schlüssel im bib, keine verwaist. 4 Bücher ohne ISBN/DOI; 6 Artikel ohne DOI; perretliaudet2003 ohne Seiten (FV v2.7 hat Seiten 309–327 und DOI). Anhang C nennt für Shabana „ISBN“, bib hat keine. Keine der 13 Literaturabgleich-Referenzen steht im bib oder im AP („Flach“ im AP nur als „Flachstößel“). |
| `sinus_zelt.py` → `sinus_zelt_ausgabe.txt` | Plausibilität: Zelt mit Knick auch beim Sinusprofil? (starr, linear, Präreg A2 Z. 147) | Ja. Bei V1-ähnlichen Werten (3×0,1 kg, 8 mm Spitze-Spitze, 10 Hz): F_min(100°) − F_min(120°) = −0,548 N, symmetrische Steigung 0,028 N/° am Knick; vergleichbar mit der Egg-Zeltspannweite 0,56 N (P2 V1). „Asymmetrisches Profil zwingend“ gilt deshalb nur für Schiefe im Dauerkontakt und für N₂/N₃. |

Aufruf jeweils: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../../code timeout 540 python3 <skript>`. Kein `__pycache__` im Repo-Baum (geprüft), `git status` leer.

Analytische Eigenleistung (ohne Skript): Die 1-FG-Bewegungsgleichung (P2 ENG-01; `code/linear_solver.py` Z. 4–8: M·ẍ + C·ẋ + K·x = −μ·M·ā(t)) ist formgleich mit einem einseitig gestützten Einmassenschwinger unter Fußpunkterregung mit der Beschleunigung μ·ā(t) = (μ/3)·Σ aₖ(t − τₖ). Im Liftoff-Bereich ist das Modell daher ein Impact-Oszillator bzw. „Bouncing Ball“ mit nicht-sinusförmiger Fußpunktbeschleunigung; die Phasenlage formt nur die Wellenform dieser wirksamen Anregung (Φₖ). Der Ähnlichkeitsparameter ε = μ·π²·Hub·f²/(THOLD·g) (P2 AUS-07) ist μ·a_hold,max/g (Spitzenbeschleunigung der Haltephase 11,68 m/s² bei RTOP = 5 mm, P1 L6a-035), also das Gegenstück der dimensionslosen Beschleunigung Γ der Bouncing-Ball-Literatur.

## 3 Bewertungsregeln

- Kategorien nach Auftrag: bekannte_mechanik (hier auch: etablierte Standardmethodik in Numerik und Statistik, weil das Schema dafür keine eigene Kategorie hat) / konkrete_kombination / methodischer_beitrag / empirisches_ergebnis (nicht vergeben: keine Messdaten) / ungeklaert.
- Primärquelle „prüfbar“ heißt: vollständiger bib-Eintrag mit DOI/ISBN oder eindeutiger Fundstelle im Bestand. Ob die Angaben stimmen, ist ohne Websuche nicht prüfbar. Verifikationsvermerke im Bestand („gegen Verlagsseite geprüft“) werden als Behauptung des Bestands übernommen, nicht als eigene Prüfung.
- Eine fehlende Fundstelle beweist keine Neuheit. Offene Vergleiche werden als Recherchefragen formuliert.
- Aussagen aus P2 gelten in der gegengeprüften Fassung (Spalte verif_korrektur). Nicht gegengeprüfte P2-Befunde (z. B. KM-10/11/12, SYM-01) sind so gekennzeichnet.
- Keine Rechtsberatung: Zum Schutzrechtsstand wird nur wiedergegeben, was interne Dokumente sagen (P1 L6a-002/005/006).

## 4 Grenzen

- Ohne Websuche bleibt jede Neuheitsaussage offen; die dokumentierte Recherche des AP (Anhang C) war eine gezielte Websuche ohne Datenbankabfrage.
- IP-Texte nur auf Beitrags- und Neuheitsaussagen gelesen; die technische Verwertbarkeit bewertet die Rolle „IP“.
- Das Master-Deck wurde über den Text gelesen; Diagrammdaten wurden nicht nachgerechnet.
