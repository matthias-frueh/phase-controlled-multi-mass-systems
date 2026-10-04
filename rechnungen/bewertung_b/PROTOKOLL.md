# P3 · Rolle „bewertung_b“ · Bewertung der Bündel B08–B14

> **Vermerk zur Übernahme (04.10.2026).** Protokoll aus der Gesamtprojektanalyse 10/2026, Stand 02.10.2026, unverändert bis auf Pfade und Quellenangaben. Geprüft wurde der Repository-Stand `cd7be6a` (28.09.2026) mit der Präregistrierung v2 vom 25./28.09.2026; die späteren Änderungen aus PR #13 und PR #14 (unter anderem Präregistrierung v2 mit Arbeitsfestlegungen, `code/auslegung.py`, `code/ereignisloeser.py`) sind nicht eingearbeitet. Alle Zahlen sind Simulation oder Analytik, keine Messdaten. Verweise wie „L1a-019“, „P1 §3“ oder „B01–B14“ zeigen auf Arbeitsdokumente der Analyse, die nicht im Repository liegen. Quellen außerhalb des Repositorys sind als „(lokaler Bestand, nicht im Repository)“ gekennzeichnet. Startbefehle und Grenzen je Gruppe: [`rechnungen/README.md`](../README.md).

Stand 02.10.2026 · ursprünglich lokal, jetzt unter `rechnungen/` · nichts committet, keine Repo-Datei verändert, keine Websuche.
Kennzeichnung im Text: **[Q]** Quelle mit Fundstelle, **[R]** eigene Rechnung (Skript in diesem Ordner), **[E]** eigene Einschätzung, **[A]** Annahme.

## 1 Gelesen

Kontext
- `(Arbeitsdokument der Analyse, nicht im Repository)` vollständig (v. a. §5–§8, §10–§13).
- `(Arbeitsdokument der Analyse, nicht im Repository)` vollständig; `p1/evidenzmatrix.csv` gefiltert (ESP32/Firmware/Encoder/Pendel/Ballon/Ring/Regelung/Bootstrap/Rast/Gasaustausch/geometrische Phase; u. a. L1a-063, L2-074, L3-064…070, L4-054/060/072, L5b-041/061/063/064, L7-063/072/077–080); `p1/gelesen.csv` (Lesestatus je Datei, für die Suche nach nicht erfassten Ansätzen).
- `(Arbeitsdokument der Analyse, nicht im Repository)`, `p2/empfehlungen.md` vollständig; `p2/befunde.csv` STA-01…STA-12 (Volltext STA-05…12); `p2/statistik/PROTOKOLL.md` (Gliederung, Änderungsvorschläge Z. 431–499).
- `(Arbeitsdokument der Analyse, nicht im Repository)` (B08–B14 vollständig, P2-Stränge); Nachbarrollen nur zur Abgrenzung: `p3/zusatz_p2/PROTOKOLL.md` (KM-10, KM-12), `p3/neuheit/PROTOKOLL.md`, `bibcheck_ausgabe.txt` (Perret-Liaudet-Einträge).

Hauptquellen
- `docs/praeregistrierung_v2_entwurf.md`: §2 (Z. 102), §3 (E1–E3, Z. 141–146), §5.1, §6 (Z. 294–298), §8 (Z. 323–405), §9 (Z. 407–500), §12 (Z. 536–565).
- `docs/praeregistrierung_v2_anhang.md`: A9.1 (Z. 423–447), A9.2 (Z. 449–503), A9.4–A9.11 (Z. 530–620), Tab. C (Z. 647–671), Tab. F/Z (Auszüge).
- `docs/arbeitspapier/PCMMS_Arbeitspapier_v2_4.tex` Z. 660–676 (Perret-Liaudet), Z. 2096–2108 (Antrieb), Z. 4820–4830; `…/PCMMS_Arbeitspapier_Offene_Punkte.md` Z. 32, 54–60; `references.bib` Z. 110–180.
- `docs/literaturabgleich_2026-09-12.md` §2.3, §3, §4; `docs/einordnung.md` Z. 170–182, 228–262; `docs/expose_2026-09.md` Z. 160–170.
- SOT 01.10. (`(lokaler Bestand, nicht im Repository)`) vollständig.

Kandidatenquellen (alle unter `(lokaler Bestand, nicht im Repository)`, sofern nicht anders angegeben)
- B08: `20_LINIE_A/CODE/Arbeitsstaende/sensitivity_sweep.py.txt` (voll), `20_LINIE_A/CODE/Frueher_Bestand_Pruefen/pcmm_sim.py.txt` (voll), `(lokaler Bestand, nicht im Repository)` (voll), `(lokaler Bestand, nicht im Repository)` §4–5 (Z. 230–433), `(lokaler Bestand, nicht im Repository)` Z. 100–145, `(lokaler Bestand, nicht im Repository)` (voll), `(lokaler Bestand, nicht im Repository)` §8–9.
- B09: `20_LINIE_A/CODE/Arbeitsstaende/pcmms_phasensteuerung_esp32.ino.txt` (voll), `…/pcmms_lra_phasensteuerung_esp32.ino.txt` (Kopf), `(lokaler Bestand, nicht im Repository)` (voll), `…/PCMMS_Baustein3c…docx.txt`, `…/PCMMS_Baustein3e…docx.txt`, `…/PCMMS_Baustein3_Autonome_Rahmensteuerung…docx.txt`, `…/PCMMS_Baustein3d…docx.txt`, `…/PCMMS_Baustein13…-1.docx.txt` (alle voll), `70_IP_SCHUTZRECHTE/Bestand_Pruefen/Patent_X_Schutzansprueche…pdf.txt` (voll), `(lokaler Bestand, nicht im Repository)` (voll), `(lokaler Bestand, nicht im Repository)` (voll), `(lokaler Bestand, nicht im Repository)` (voll; privates Denkpapier #17 nur über den Vermerk, nicht zitiert).
- B10: `pcmm_sim.py.txt`, `(lokaler Bestand, nicht im Repository)` §3.4–3.6, §6–7, `20_LINIE_A/CODE/Arbeitsstaende/pcmms_v10_egg_traj.py.txt` (voll), `(lokaler Bestand, nicht im Repository)` §5.1–5.5, §5.9, `20_LINIE_A/CODE/Frueher_Bestand_Pruefen/pcmms_s2_quat_basislinie.py.txt` (Kopf, Parameter, Orientierungssets), `(lokaler Bestand, nicht im Repository)` (gezielt), `(lokaler Bestand, nicht im Repository)` §3–4, `(lokaler Bestand, nicht im Repository)` §3–6.
- B11: `21_LINIE_B/CODE/Arbeitsstaende/pcmms_c1_vorwaertsmodell.py.txt` (voll), `(lokaler Bestand, nicht im Repository)` (voll); #30 (PNG-Text) nur als Dublette vermerkt.
- B12: `(lokaler Bestand, nicht im Repository)` §6–7, `(lokaler Bestand, nicht im Repository)` (Kopf, §5–§7), `(lokaler Bestand, nicht im Repository)` §6, `21_LINIE_B/CODE/Arbeitsstaende/pcmms_drift_analyse.py.txt` (Kopf, Funktionsliste), `80_…/PCMMS – Studienleitfaden….PDF.txt` (Antwort 9), `Einzeldateien_Upload_2026-10-01/pcmms_signaturcheck_altbestand.py.txt` (Teil 3).
- B13: `(lokaler Bestand, nicht im Repository)` §9, §12, `(lokaler Bestand, nicht im Repository)` (gezielt).
- B14: `30_…/Bestand_Pruefen/PCMMS_Pendeltest_Protokoll_horizontal_Frueh_2026.docx.txt` §1–9, `10_KERNRAHMEN/Bestand_Pruefen/pcmms_pendel_tracker.py.txt` (voll).

Suche nach nicht erfassten Ansätzen (§12 F)
- Lesestatus aus `p1/gelesen.csv` gegen Verzeichnislisten von 20_LINIE_A, 21_LINIE_B, 22_LINIE_C, 30_, 31_, 50_, 60_, 95_ abgeglichen; zusätzlich gelesen: `(lokaler Bestand, nicht im Repository)`, `20_LINIE_A/CODE/Arbeitsstaende/pcmms_lageregelung_3achs.py.txt` (Kopf), `10_KERNRAHMEN/Bestand_Pruefen/PCMMS_Baustein14_Grunddynamik_Spezifikationsblatt_Frueh_2026.docx.txt` (voll), `(lokaler Bestand, nicht im Repository)` §6, `(lokaler Bestand, nicht im Repository)` W7/W8, `(lokaler Bestand, nicht im Repository)` §2–3, Gliederungen von `Werkzeug_NullErgebnis…`, `Werkzeug_Simulation_Based…`, `Werkzeug_MessOperator…`, `20_LINIE_A/CODE/Frueher_Bestand_Pruefen/pcmms_diagnose_phasenpartitionierung.py.txt` und `pcmms_signalform_diagnose.py.txt` (Kopf), `20_LINIE_A/CODE/Aktuell_Kandidat/pcmms_pruefung_pr4_linearloeser.py.txt` (Kopf), `(lokaler Bestand, nicht im Repository)` §3–4, `(lokaler Bestand, nicht im Repository)` (gezielt), Gliederungen weiterer 60_-Dateien; Volltextsuche nach Nocke/Linearaktor/Allan im Bestand.
- Bewusst nicht gelesen: `95_HISTORISCHE_ENTWICKLUNG/CORE_UEBERGREIFEND/GSR_Denkdokument_*` (laut Archiv-Vermerk §1/§7 privat bzw. Mittelwertlinie).

## 2 Rechnungen (Reproduktion aus diesem Ordner)

`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../../code timeout 540 python3 <skript>`; Ausgaben `<skript>_ausgabe.txt`. Kein Repo-Code importiert.

| Skript | Frage | Ergebnis |
|---|---|---|
| `b1_median_versatz.py` | #37: stimmen med(u) = −0,368, γ₁ = +0,755, Faktor 2,9 (Präreg A9.1, Tab. F)? | bestätigt: −0,3680 (= geschlossene Form), +0,7550, 2,92; 0,54/1,36 % für 0,2/0,5 % Versatz; Sinus 0 |
| `b2_rast_linie_b.py` | #15/#86: Zahlen 0,462/0,364/0,222/0 (Archiv-Vermerk §2.4) | bestätigt; geschlossen 1 − (c_r/c_h)·t_h/t_r → im gedächtnisfreien Modell streng monoton fallend |
| `b3_ungerade_harmonische.py` | Übertragung #19 auf Linie A: ungerade-harmonisches Profil im linearen Kontaktast (V1-Kandidat aus P2: μ = 0,46, 8 mm, 10 Hz, K = 1,5·10⁶ N/m, ζ = 0,05 [A]) | γ₁ ≤ 2·10⁻¹⁵, gerade/ungerade ≤ 2·10⁻¹⁴, A = 1 für alle geprüften Phasen, auch mit 1 % linearer Kopplung; quadratische Kennlinie erzeugt gerade Harmonische (|N₂| ×4 bei doppeltem Hub). Egg-Profil zur Kontrolle: Triphasik γ₁ = −0,49 (deckt sich mit P2 AUS) |
| `b4_auswahlregel_N.py` | #42 und Verallgemeinerung | Summe nur k ≡ 0 mod N; paarweise Gegenphase löscht ungerade k; azimutale Mode m trägt k ≡ ±m mod N (N = 3: Moment nur k ≢ 0, wie KM-03) |
| `b5_landestoss_waechter.py` | neuer Kandidat Liftoff-Wächter: Landestoß und Abklingen | F_peak ≈ v√(KM): 1 mm Fall → 127–140 N, 12 mm → 427–471 N (P2: 483–487 N); nach Antriebsstopp 8–37 Stöße, 0,35–1,5 s (ζ 0,1–0,02) |
| `b6_gasreihe.py` | #75: Dichteverhältnis und Mitänderung von ν | CO₂/He 11,07; ν(He)/ν(CO₂) 14,8; δ(10 Hz) 1,94 gegen 0,50 mm; Luft δ = 0,69 mm (passt zu v5 §6: 0,7 mm). Stoffwerte [A] |

## 3 Bewertungsmaßstab

Je Kandidat: (1) technischer Kern und Voraussetzungen aus der Fundstelle; (2) Gültigkeit nach P1/P2 (zurückgezogene Deutungen: Mittelwertverschiebung, Vorzeichenregel, 120°-„Symmetrie“, Drift ∝ Dichte; korrigierte Zahlen: Referenzsatz, Startabhängigkeit, Hot-Spot, Kippmoment-Betrag, Zellreserve); (3) Abgleich mit dem, was Präreg v2/P2 bereits enthalten (Dubletten zum aktuellen Stand gelten nicht als neuer Ansatz); (4) Nutzen für V1 streng: „jetzt_v1“ nur bei konkreter Verbesserung/Absicherung von V1 vor dem Einfrieren von Teil A.

## 4 Ergebnis in Kürze

| Bündel | Empfehlung | tragend |
|---|---|---|
| B08 Statistik | jetzt_v1 | nur P2-4 (IUT-TOST, Mindesteffekt, H2-Fensterregel, F_min-Schätzer, Intervalltyp); Altkandidaten bereits umgesetzt oder verworfen |
| B09 Phasensteuerung/Regelung | vor_v1_pruefen | Antriebs-/Encoderkonzept (#34) für Nockenvariante, Profilphase in Phase 1 (#79 mit P2-6); Regelungsideen nach V1 |
| B10 Modellerweiterungen | nach_v1 | #47 schon in Präreg; #42 + Raum-Zeit-Regel für §8.4; Rest verwerfen/parken |
| B11 Synthetik | jetzt_v1 (eng) | Zirkularitätsregel als Spezifikation für Werkzeug 8, v. a. Mismatch-Generatoren für H3 |
| B12 Linie B | parken | Nullkontrollen (#19, #20), Rastprobe nur mit instationärem Modell |
| B13 Literatur/Anwendung | nach_v1 | #14 als begleitende Literaturaufgabe (Mechanismusunterschied beachten), #71 Vergleichsgrößen |
| B14 Pendeltest | parken | Kontrollset ja, Vorzeichenkriterium auf geometrische Spiegelung umstellen; Tracker zu grob |

Korrektur am Bestand (neu, [Q]+[E]): AP v2.4 Z. 2103–2105 („programmierbarer Linearaktor, wie er im Projekt für die Phasensteuerung bereits vorliegt“) ist im Bestand nicht belegt: vorhanden sind nur ESP32-Firmware für zwei BLDC-Exzenter (konstante Drehzahl, Sinuskraft) und für Münz-LRAs bei ≈ 175 Hz (Firmware-Köpfe; P1 L5b-061). P1 führte die Aussage als „ungeprüft“ (L1a-063).

## 5 Hygiene

Kein `__pycache__` im Repo-Baum; `git status --short` leer (geprüft am Ende).
