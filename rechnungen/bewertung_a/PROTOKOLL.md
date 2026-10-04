# P3 · Rolle „bewertung_a“ · Bündel B01–B07 · Prüfprotokoll

> **Vermerk zur Übernahme (04.10.2026).** Protokoll aus der Gesamtprojektanalyse 10/2026, Stand 02.10.2026, unverändert bis auf Pfade und Quellenangaben. Geprüft wurde der Repository-Stand `cd7be6a` (28.09.2026) mit der Präregistrierung v2 vom 25./28.09.2026; die späteren Änderungen aus PR #13 und PR #14 (unter anderem Präregistrierung v2 mit Arbeitsfestlegungen, `code/auslegung.py`, `code/ereignisloeser.py`) sind nicht eingearbeitet. Alle Zahlen sind Simulation oder Analytik, keine Messdaten. Verweise wie „L1a-019“, „P1 §3“ oder „B01–B14“ zeigen auf Arbeitsdokumente der Analyse, die nicht im Repository liegen. Quellen außerhalb des Repositorys sind als „(lokaler Bestand, nicht im Repository)“ gekennzeichnet. Startbefehle und Grenzen je Gruppe: [`rechnungen/README.md`](../README.md).

Stand 02.10.2026 · ursprünglich lokal, jetzt unter `rechnungen/` · nichts committet, keine Repo-Datei verändert, kein `__pycache__` im Repo-Baum (geprüft), `git status` leer. Keine Websuche.
Kennzeichnung: **[Q]** Quelle mit Fundstelle · **[R]** eigene Rechnung (Skript hier) · **[E]** eigene Einschätzung · **[A]** Annahme.
Repo-Stand: `cd7be6a` (28.09.2026, `git log -1`).

## 1 Gelesen

Kontext
- `(Arbeitsdokument der Analyse, nicht im Repository)` vollständig (v. a. §5–§8, §10–§13).
- `(Arbeitsdokument der Analyse, nicht im Repository)` vollständig; `p1/gelesen.csv` (gezielt: ob Altdateien in P1 gelesen wurden).
- `(Arbeitsdokument der Analyse, nicht im Repository)`, `p2/empfehlungen.md` vollständig; `p2/befunde.csv` Zeilen AUS-06/07/08/12/13/14, ENG-03/05/06/09/10, KM-04/09/10/11/12, SYM-01…05, RT-03, STA-11/12, LB-10/11/13 (mit Gegenprüfung); `p2/korrekturen.csv` (alle 47 Zeilen überflogen); `p2/auslegung/PROTOKOLL.md` Z. 140–156, 238–268.
- `(Arbeitsdokument der Analyse, nicht im Repository)` (B01–B07 vollständig, B08–B14 Titel/Kandidaten zur Abgrenzung), `p3/zusatz_p2/PROTOKOLL.md` vollständig (Gegenprüfung KM-10/11/12, SYM-01, RT-04, STA-10), `p3/neuheit/PROTOKOLL.md` §1–§2 und `sinus_zelt.py`/Ausgabe.

Aktuelle Hauptquellen
- Präreg v2 Entwurf `docs/praeregistrierung_v2_entwurf.md` vollständig (u. a. §2 Reichweite Z. 102–107, §3 H0–H4/E1–E5 Z. 111–148, §5.1 Z. 177–190, §5.2 Tabelle Z. 191–221, §5.3 Z. 222–245, §6 Z. 272–315, §8 Z. 323–406, §9 Z. 407–501, §12 Z. 536–565).
- Präreg-Anhang `docs/praeregistrierung_v2_anhang.md`: A1 (Z. 66–120, A-Definition Z. 90), A2.1–A2.5 (Z. 121–203), A3–A7 (Z. 205–360), A9.1–A9.12 (Z. 421–645), Tabelle C (Z. 647–669), Tabelle F (Z. 673–740).
- AP v2.4 `docs/arbeitspapier/PCMMS_Arbeitspapier_v2_4.tex`: Z. 1805–1835 (Triaden), 2085–2110 (Antrieb/Profil), 2445–2460 (Hilfskanäle, 6.10), 3015–3045 (Pflichtläufe/Sinus), 3560–3575 (Randterm), 3655–3700 (Symmetrieprüfung, Wertebereich), 3895–3925 (Sinus-Folgerung), 4818–4835 (offene Punkte), 5005–5025 (Tab. liftoff-frei).
- FV v2.7 `docs/formelverzeichnis/PCMMS_Formelverzeichnis_v2_7.tex`: Z. 126–152 (Mehrinterface), 310–316 (Liftoff-Schätzer, Kontaktkanal), 505–545 (Residual, Gleichrichtung, Kontrollen), 798–806 (Anh. B.2).
- `docs/expose_2026-09.md` Z. 55–95 (Mechanismus c_down/c_up); `data/README.md` (Z. 33, 47, 65–70); `code/linear_solver.py` (Docstring, solve/transfer/section), `code/finesweep.py` (Profil, Parameter).
- SOT 01.10. (`(lokaler Bestand, nicht im Repository)`) per grep (nur Sinus-Sweep-Zeile Z. 50 einschlägig).

Fundstellen der Kandidaten (in `(lokaler Bestand, nicht im Repository)`, Endung .txt)
- B01: Regimeanalyse v1.2 §4–5, §10–13 (`(lokaler Bestand, nicht im Repository)`); Sweep_Karten_Periode_Randterm_2026-09-13 (Z. 79); Auswertung_v3a_Mehrmodul (Z. 51–62); Analyse_Neue_Unterlagen (Z. 75–131); Baustein8 Symmetrieerhaltende Numerik (vollständig); Kurzdossier (Z. 101, 174–176).
- B02: Korrekturblock AP v2.4 (K5/K7, Kopf); pcmms_3mass_v8_schnipp.py (Docstring, Parameter); b1_beispiel_ergebnis.png (OCR); pcmms_b1_zwei_zeitskalen.py (Docstring/Parameter); pcmms_eggmodul_v3.py (Docstring, Funktionsliste); pcmms_v3a_geglaettet.py (Docstring).
- B03: pcmms_v3a_kontaktmodell (über Exposé/Patent 2); Patent2 korrigiert §5.1–5.2; Patent1 korrigiert §6.2; Literaturanker faff8cf4 (Befund 2, Z. 51–53, 112–128); Dossier 2026-09-02 §5.1–5.2; pcmms_v16_stoss.py (Docstring); Werkzeuge_Statespace_Framework W5.
- B04: Werkzeug_Zustandsabhaengige_Kraftverschiebung §6–9; Werkzeug_MessOperator §2; Werkzeug_Phasen_Artefakt_Sensitivitaet §4–7; Werkzeuge_Messmethodik_Kleinstsignale W4/W5; Measurement Framework (grep Tabelle 1); Formelwerk 202606 §5–§7; pcmms_stand_v10_v15 (grep v12/v13); Schwellen_eps (über P1-Kandidat).
- B05: Ergebnisnotiz Randterm 13.09. (Kopf, §1); Anh. B.2 FV; AP §8.3.
- B07: Korrekturvorschlag A-Definition v3 (vollständig); Notiz_Bilanz_intern §3.5; Konzeptbaustein Mehrkanal-Messarchitektur (vollständig); Ringstruktur-Mehrkanal-Inversion (grep); Patent Y §5.1–5.2; GM2 §5.2–5.3.

Suche nach weiteren Ansätzen (§12 F): Dateilisten von 20_LINIE_A (Code/Dokumente dedupliziert), 30_EXPERIMENT_MESSTECHNIK, 60_REVIEW_QA, 95_HISTORISCHE_ENTWICKLUNG, 10_KERNRAHMEN (Bausteine); Stichwortsuche (Zell-/Modultausch, Rotation, elektrischer Kontakt, Klirr/THD, Überlast/Anschlag, Anlaufprotokoll, Impulshammer, inverse crime, Impulsbilanz, Nockenfolger); gezielt gelesen: Werkzeugbibliothek_extrahiert §1–2, §6; Baustein14 (grep, Z. 232); Baustein4 (grep); Laborplan Variante 1 (Gliederung, grep); Externe_Reviews_Todos (vollständig); pcmms_lageregelung_3achs, freqvergleich, drei_richtungen, pruefung_pr4, diagnose_phasenpartitionierung, signalform_diagnose, hoehen_logger (Docstrings); pcmms_s2_dreieck(afix).html (grep).

## 2 Vorgehen und Maßstab

Je Bündel: tragende Fundstellen gelesen → technischen Kern (Algorithmus/Diagnose/Messidee/Modell/Protokoll) und Voraussetzungen festgehalten → gegen P1/P2 (in der gegengeprüften Fassung, Spalte `verif_korrektur`) und gegen die Präreg v2 (was ist schon registriert?) geprüft → wo eine offene Zahl die Empfehlung entscheidet, kleine eigene Rechnung → Empfehlung. „jetzt_v1“ nur, wenn V1 konkret verbessert oder abgesichert wird; was die Präreg bereits enthält, gilt als Dublette.

## 3 Eigene Rechnungen (alle: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../../code timeout 540 python3 <skript>`)

| Skript | Frage | Ergebnis [R] |
|---|---|---|
| `b03_daempfungsasymmetrie.py` (+ Arg. `0.2`) | Verletzt richtungsabhängige Kontaktdämpfung (c_load = C(1+a), c_unload = C(1−a)) die Superposition? Eigenes 1-FG-RK4 (Δt = T/4000, 1 s Einschwingen, Konvergenz ≤ 1e-13 N), drei Einzelmodulläufe + 21 Schnittpunkte + synchron, Superposition im Zeitbereich, Residuen bandbegrenzt wie Präreg A9.4 | Kontrolle a = 0: ≤ 0,0006 mN. **V1 (K = 1,5e6 N/m, ζ = 0,05):** a = 0,1/0,3/0,5 → max |r(F_min−⟨N⟩)| bei k_max = 9: 0,03/0,10/0,17 mN (k_max = 12: 0,07/0,21/0,36 mN); Re/Im N₁…N₃ ≤ 0,03 mN; ⟨N⟩ = Mg auf 0,1 µN; Δ⟨δ⟩ −0,3…−4,9 nm. **ζ = 0,2:** k_max = 9: 0,14/0,41/0,66 mN, k_max = 12: 0,31/0,89/1,39 mN; N₃ ≤ 0,10 mN. **Weich K = 1e5 (ρ = 0,16):** k_max ≥ 6: 4–23 mN, N₃ 0,35–1,65 mN, Δ⟨δ⟩ 26–400 nm. Ohne Bandbegrenzung bei V1: 2–11 mN (hohe Harmonische). |
| `b01_spiegelung_v1.py` | Spiegelungsbrechung φ → −φ (P2-8, SYM-02) am V1-Punkt | Referenz (K = 1e4): 850 mN, wie P2. **V1 bandbegrenzt (k ≤ 12): ≤ 0,05 mN**, Δγ₁ < 1e-4 (ζ = 0,02: ≤ 0,03 mN); starr ≤ 0,02 mN (Abtastung). Ohne Bandbegrenzung 17–44 mN, stammt aus Profilharmonischen nahe der Kontaktresonanz (k ≈ 24). |
| `b07_impulsbilanz_kanal.py` | Größe des Rahmenterms M·a_R = (H − 1)·Σm_j a_j im kinematischen Kraftkanal am V1-Punkt | |M a_R| je Harmonischer 0,9–10,6 mN (k = 3 am Schnitt 9,2–10,4 mN), Spitze bis 12. Harmonische 18–53 mN. Absolutschluss von N₁ auf 1 mN verlangt 0,02–0,19 % Genauigkeit der Modulbeschleunigung → nur relativ (Einzelmodul- gegen Kombinationslauf) praktikabel. |
| `b02_profilglaette.py` | Anteil hoher Profilharmonischer am ungebänderten F_min (Präreg §5.3(a)) und Wirkung einer Glättung (Tiefpass auf P_k als Ersatz) | V1, ζ = 0,05/0,02: F_min(120°) 5,409/5,384 N gegen 5,499 N starr (16–21 % von ΔF_Zelt); synchrone Reserve 42,6/41,8 % statt 42,9 % (Bedingung (a) kaum berührt). Tiefpass k₀ = 15: Abweichung 0,03–0,04 N. |
| (Kommandozeile, im Protokoll) | Dämpfungsschwelle für den 1-periodischen Hüpforbit nach P2-Stoßabbildung μπ·Hub·f ≥ gT(1−e)/(2(1+e)), e = exp(−πζ/√(1−ζ²)), μπ·Hub·f = 0,116 m/s (P2 AUS-12 verif) | Orbit existiert für ζ < 0,152; ab ζ ≈ 0,15 kein 1-periodischer Hüpforbit bei V1 synchron (Näherung; nur dieser Orbittyp). |

## 4 Kurzbefunde je Bündel (Details im Schema-Ergebnis)

- **B01** (nach_v1): S₃ exakt (P2 SYM-01, zusatz_p2 bestätigt). Experimentell durch H1 mit gemessenen Einzelmodulen und den Zellkanal (P2-1) dominiert; Spiegelung bei V1 ≤ 0,05 mN [R] → P2-8 für V1 unbrauchbar. Bleibt: S₃-Prüfungen mit bekannter Antwort im Pipelinetest und bei Kartenneuberechnung; „120°-Symmetrie“ und Baustein-8-Numerik verworfen.
- **B02** (nach_v1): Sinus-Zelt existiert (Kegel |Φ₁|, neuheit), bringt für V1 aber nichts über P0.5/P0.6/E3 hinaus; R_c-Schwelle und Frequenzhochlauf brauchen Liftoff → bei steifem Kontakt Hüpfstöße. Triadenphase am steifen Punkt irrelevant (γ₁(120°) = −0,49, P2 AUS-14). Schnipp verworfen.
- **B03** (jetzt_v1, eingeschränkt): P2-5 Ähnlichkeitsgesetz als Auslegungswerkzeug; Dämpfungsasymmetrie bei V1 unter der H1-Nachweisgrenze [R], erst bei ζ ≈ 0,2 mit starker Asymmetrie an der Grenze; AP-6.10-Kriterium „0 g im freien Fall“ gilt bei bewegten Modulen nicht [E]; H3 im steifen Aufbau über Einfederung/Rahmenbeschleunigung (Betriebsimpedanz) statt Kraftresiduen prüfen [E, neuer Kandidat].
- **B04** (jetzt_v1, eingeschränkt): P2-6 Identifizierbarkeitsläufe und P2-7 Tabelle-C-Zeilen; P0.4-Klirrkriterium (Kand. 58); nichtlinearer Nebenschluss als Pipeline-Szenario (Kand. 78). Taxonomien und Gleichrichtungsregression überwiegend Dubletten oder zirkulär.
- **B05** (jetzt_v1, eingeschränkt): ereignisgenauer Löser (P2-3) als Repo-Werkzeug für Monostabilitäts- und Nennlastprüfung bei gemessenen Parametern; Fensterregeln der Präreg genügen experimentell; Randterm bei V1 ≲ 10⁻⁵ N [E].
- **B06** (jetzt_v1, eingeschränkt): P2-2 Hüpfzustand → Anlaufprotokoll, Überlastschutz, ζ-Ziel (≥ 0,15…0,2 [R]), Echtzeit-Abschaltung (neuer Kandidat); Hysteresefahrt E2 erst nach V1 mit Schutz.
- **B07** (jetzt_v1, eingeschränkt): Zell-/Modullage vor Teil A festlegen (Kand. 35); E3 als registrierte Kontrolle (P2-1, mit zusatz_p2-Korrekturen); kinematischer Impulsbilanz-Kanal (Kand. 62/76/50) als Zerlegung einer H1-Abweichung prüfen; 6-Interface/DMS+Piezo parken.

## 5 Neue Kandidaten (nicht in P1 erfasst)

1. Echtzeit-Lastabschaltung bei Überlast/Einzelzell-Liftoff (Werkzeugbibliothek_extrahiert §6) → B06, jetzt_v1.
2. Antriebsstrom je Modul als Sekundärkanal (Baustein 14 Z. 232) → B04, vor_v1_pruefen.
3. Betriebsimpedanz des Kontakts N_k/x_k bzw. M·a_R,k für H3 im steifen Aufbau (Präreg A9.1 Z. 425–426, Patent 1 §6.2, Mehrkanal-Konzept §2.4) → B03, vor_v1_pruefen.
4. Körperdrehung um 120° / Zelltausch als Identifizierbarkeits-Rückfallebene (Phasen-Artefakt-Werkzeug §4–5; Messmethodik W5 Nr. 5) → B07, parken.
5. Profilglätte (C¹ → C²) als Auslegungsgröße bei steifem Kontakt (pcmms_v3a_geglaettet.py; Anweisung §8.3) → B02, parken.

## 6 Grenzen

- Alle Rechnungen sind Modellrechnungen im linearen bzw. stückweise linearen 1-FG-Modell mit idealem Egg-Profil; V1-Parameter sind P2-Vorschläge [A], nicht gemessen. Rauschen, Kippmoden und reale Profilspektren sind nicht enthalten.
- Die Nockenfolger-/Spielfrage (B03) ist eigene Einschätzung ohne Fundstelle im Bestand.
- Keine Literatur- oder Neuheitsaussage; fehlende Fundstellen beweisen keine Neuheit.
