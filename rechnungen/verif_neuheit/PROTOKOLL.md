# P3 · Rolle „verif_neuheit“ – Prüfprotokoll (Gegenprüfung der Rolle „neuheit“)

> **Vermerk zur Übernahme (04.10.2026).** Protokoll aus der Gesamtprojektanalyse 10/2026, Stand 02.10.2026, unverändert bis auf Pfade und Quellenangaben. Geprüft wurde der Repository-Stand `cd7be6a` (28.09.2026) mit der Präregistrierung v2 vom 25./28.09.2026; die späteren Änderungen aus PR #13 und PR #14 (unter anderem Präregistrierung v2 mit Arbeitsfestlegungen, `code/auslegung.py`, `code/ereignisloeser.py`) sind nicht eingearbeitet. Alle Zahlen sind Simulation oder Analytik, keine Messdaten. Verweise wie „L1a-019“, „P1 §3“ oder „B01–B14“ zeigen auf Arbeitsdokumente der Analyse, die nicht im Repository liegen. Quellen, die nicht im Repository liegen, sind als „(Quelle außerhalb des Repositorys)“ gekennzeichnet. Startbefehle und Grenzen je Gruppe: [`rechnungen/README.md`](../README.md).

Stand 02.10.2026 · ursprünglich lokal, jetzt unter `rechnungen/` · keine Websuche, Literatur nur aus dem Bestand.

Ziel: Ergebnis der Rolle „neuheit“ (`rechnungen/neuheit/`) zu widerlegen; im Zweifel nicht bestätigt.

## 1 Gelesen

Ergebnis und Arbeitsunterlagen der geprüften Rolle
- `rechnungen/neuheit/PROTOKOLL.md`, `bibcheck_ausgabe.txt`, `sinus_zelt.py` mit Ausgabe (vollständig)
- Ergebnis-JSON der Rolle (im Auftrag)

Kontext
- (Quelle außerhalb des Repositorys) §7, §8, §12 (gezielt)
- (Quelle außerhalb des Repositorys) (gezielte Zeilen: L1a-007/047, L1b-037, L2-070, L3-067, L4-003/076/077, L5a-092, L5b-027/034, L6a-005/006/012/035/038/044/048/063/064/066, L6b-043/054/055/069, L7-085; alle Zeilen mit Quelle „Forschungslinie_Gegenstand“)
- (Quelle außerhalb des Repositorys) (AUS-02/06/07/08/10/11/12/13/14, ENG-01/03/05/09, KM-04/09/10/12, SYM-01/02/03, STA-06/09/11/12, RT-01/03, LB-11/13), `P2_zwischenbericht.md` Z. 94–153, `empfehlungen.md` Z. 40–61, `auslegung/PROTOKOLL.md` Z. 143–152, 238–248, `auslegung/a3b_arbeitspunkte.py` (Definition ΔF_Zelt), `auslegung/mu_modell.py` Z. 144
- (Quelle außerhalb des Repositorys) (alle Titel; Details B01 Nr. 38/70, B02 Nr. 1/5/8, B04 Nr. 3, B07 Nr. 9/41, B08 Nr. 37, B10 Nr. 42/47, B13 Nr. 14/71)
- Schwesterrollen zur Abgrenzung: `rechnungen/zusatz_p2/PROTOKOLL.md` (KM-10/11/12, SYM-01), `rechnungen/bewertung_a/b01_spiegelung_v1_ausgabe.txt` und PROTOKOLL Z. 42–50

Literaturbestand und Beitragsbehauptungen (an der Fundstelle geprüft)
- `docs/arbeitspapier/references.bib` (vollständig); Diss-v2.1-bib (Diff: identisch bis auf Kopf)
- AP v2.4: Kurzfassung Z. 56–117, §1.6 Z. 474–578, Kap. 2 Z. 581–833 (inkl. Haptik Z. 626–628, Robotik Z. 630–647), §4.8 Z. 1778–1862, Anhang C Z. 5319–5455; grep nach Popov/Ratchet/Feng/Flach/Haptik
- FV v2.7: Z. 39, 505–535, 880–895
- `docs/neuheitsgrad.md`, `einordnung.md`, `zehn_fragen.md`, `expose_2026-09.md` (vollständig); `literaturabgleich_2026-09-12.md` Z. 1–406; `werkstattbericht.md` Z. 25–90; `was_ist_pcmms.md` Z. 110–156; `README.md` Z. 15–55, 76–122; Präreg v2 Entwurf Z. 60–112, 536–565; Anhang Z. 140–150, 448–470
- `docs/arbeitspapier/PCMMS_Arbeitspapier_Offene_Punkte.md` Z. 18–40
- Literaturanker faff8cf4 (grep: Z. 20, 23, 37, 48, 55, 61, 90, 122, 128); Messtechnik-Konzept 4c73fffc Z. 30–55
- Regimeanalyse v1.2 §9 und §14
- Projektbeschreibung August: Z. 422–492 (§12–13), 728–740 (§22.2), 262–275 (§7), 820–851 (§26.2)
- Änderungslog Rework 20.09. Z. 40–72
- Präsentationen vom 28.09.2026 (Quelle außerhalb des Repositorys): erste Folien 1–5, zweite Folien 4, 6, 9, 11, Z. 504, 604
- Weitere Quellen außerhalb des Repositorys (gezielte Zeilen)
- Forschungsrahmen v3.5 Z. 28–58, 235–239, 340–346; Notiz Linie B v5.2 (Gliederung, §13)
- SOT 01.10. (grep); Linie-A-Bericht 01.10. Z. 1–40 (Quelle außerhalb des Repositorys)
- Dissertation v2.1 (Quelle außerhalb des Repositorys) Z. 1930–1940, 2850–2860, 4525–4550 (grep Beitrag/Haptik)
- Frühe Zenodo-Arbeiten (April 2026): (Quelle außerhalb des Repositorys) (Kopf, §3.11), Preliminary Proposal Z. 30–40, „Measurement Framework …“ Z. 84–90; Zuordnung zu DOI über Exposé Juli (Quelle außerhalb des Repositorys) Z. 264–276
- Forschungslinie korrigiert (Quelle außerhalb des Repositorys) Z. 222–345
- `code/linear_solver.py` Docstring Z. 1–40

## 2 Eigene Rechnung

| Aufruf | Zweck | Ergebnis |
|---|---|---|
| `linear_solver.py --section --rigid --mu 0.462` und `… --sinus` (Repo-Werkzeug, Referenzhub, 10 Hz) → `v1_egg_sinus_schnitt_ausgabe.txt` | Gegenprobe zu `neuheit/sinus_zelt.py`: Zelt Egg gegen Sinus bei gleichem Hub, starr | Spannweite 100°→120°: Egg 0,542 N, Sinus 0,528 N (bestätigt „vergleichbar“). **Knicksteigung Egg 0,0541 N/°, Sinus 0,0265 N/° (Faktor 2,04)**. Referenz K = 1e4, μ = 1: Sinus 1,53 N Spannweite, 0,077 N/°; Egg 4,56 N, 0,212/0,195 N/°. |
| Handrechnung | ε-Identität | Mit C¹-Bedingung RTOP/THOLD = RBOT/TFAST = Hub folgt RTOP = Hub·THOLD und a_hold,max = RTOP·π²f²/THOLD² = π²·Hub·f²/THOLD, also ε = μ·a_hold,max/g; V1: 0,462·π²·0,008·100/(0,65·9,81) = 0,572 (P2: 0,571). Synchron hebt bei ε > 1 ab (P2 AUS-08/AUS-11: V5 ε = 1,029 hebt ab). |

Aufruf mit `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../../code timeout 540`, Arbeitsverzeichnis Scratchpad. Kein `__pycache__` im Repo-Baum (geprüft), `git status` ohne Änderungen.

## 3 Bewertungsregeln

- Urteil je Gegenstand: bestaetigt (Kernaussage und Fundstelle halten), eingeschraenkt (Kernaussage hält, Teilaussage/Kategorie/Fundstelle/Zahl falsch oder unvollständig), widerlegt (Kernaussage falsch), nicht_pruefbar (ohne Websuche nicht entscheidbar).
- Kategorienprüfung am eigenen Maßstab der Rolle: Wo die Rolle selbst „Standard“, „naheliegend“ oder „nicht recherchiert“ schreibt, trägt die Kategorie „methodischer_beitrag“ nicht (Anweisung §12 G: fehlende Fundstelle beweist keine Neuheit).
- Literatur nur aus dem Bestand; Prüfvermerke des Bestands sind Behauptungen des Bestands.
- Ergebnisse der Schwesterrollen (`zusatz_p2`, `bewertung_a`) nur als ergänzende Analyseergebnisse, nicht als Bestand.

## 4 Hauptbefunde (Kurz)

1. Kern der Rolle hält: keine empirischen Ergebnisse; Mechanik bekannt (1-FG = Fußpunkterregung, linear_solver.py Z. 4–8); Beitrag = enge Kombination als Messfrage plus kleine methodische Bausteine; Literaturbestand dünn; viele überzogene Aussagen bestätigt.
2. Kategorien uneinheitlich: Standardanwendungen werden mal „methodischer_beitrag“ (⟨N⟩-Kontrolle, Gleichrichtung, Superposition, Präreg, Spiegelpaare), mal „bekannte_mechanik“ (Triaden, Äquivalenzlogik, Ähnlichkeitsgesetz) genannt.
3. Übersehene Vorarbeiten im Bestand: AP Z. 626–628 (Haptik, unzitiert), AP Z. 637–640 (Robotik: Kontaktkraft inkl. Kontaktverlust als Entwurfsgröße), Projektbeschreibung §26.2 Z. 842–843 (Zimmermann/Zeidis/Pivovarov 2013, resistives Medium – Linie B), Literaturabgleich WangEtAl2026Capsule.
4. Übersehene, öffentlich kursierende Beitragsbehauptungen: Zenodo-Arbeiten April 2026 (u. a. DOI 10.5281/ZENODO.19876111, „methodological and contextual novelty“ für die zurückgezogene Mittelwertlinie); Forschungslinie korr. §7.2/§8.
5. Sinusvergleich: Spannweite gleich, aber Egg verdoppelt die Knicksteigung (H2-Lokalisierung).
6. Spiegelpaare für V1 praktisch ohne Signal (≤ 0,05 mN bandbegrenzt, bewertung_a) und mit Profil-Zeitumkehrasymmetrie konfundiert (P2 SYM-02, Testprofil „skew“).
7. Literaturkritik teils überzogen: „vier unvereinbare“ Fudan-Angaben sind verschiedene Arbeiten (widersprüchlich ist der Prüfstatus); bib-Kopf „DOI oder ISBN“ beschreibt den Prüfweg, nicht Feldvollständigkeit.
8. P2-Stand teils veraltet: SYM-01 und KM-10/11/12 inzwischen gegengeprüft (zusatz_p2); Zellverstärkungs-Konfundierung mit P0.1 behebbar (Rang 15/15).
9. Kleinere Fundstellenfehler: zehn_fragen #5 ist Z. 47–53 (nicht 28–35); 0,228/0,186 N/° sind die 20°-Sekanten aus Präreg A3 Z. 212 (P2 SYM-02 nennt 0,2246/0,1916); Exposé Z. 134–136 ist korrekt formuliert („Sinusprofil liefert keine Schiefe ohne Liftoff“); einordnung §8 ist Selbstkritik, keine Lückenbehauptung.
