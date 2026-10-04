# P3 · Rolle „verif_bewertung“ · Gegenprüfung der Bündelbewertung B01–B14

> **Vermerk zur Übernahme (04.10.2026).** Protokoll aus der Gesamtprojektanalyse 10/2026, Stand 02.10.2026, unverändert bis auf Pfade und Quellenangaben. Geprüft wurde der Repository-Stand `cd7be6a` (28.09.2026) mit der Präregistrierung v2 vom 25./28.09.2026; die späteren Änderungen aus PR #13 und PR #14 (unter anderem Präregistrierung v2 mit Arbeitsfestlegungen, `code/auslegung.py`, `code/ereignisloeser.py`) sind nicht eingearbeitet. Alle Zahlen sind Simulation oder Analytik, keine Messdaten. Verweise wie „L1a-019“, „P1 §3“ oder „B01–B14“ zeigen auf Arbeitsdokumente der Analyse, die nicht im Repository liegen. Quellen, die nicht im Repository liegen, sind als „(Quelle außerhalb des Repositorys)“ gekennzeichnet. Startbefehle und Grenzen je Gruppe: [`rechnungen/README.md`](../README.md).

Stand 02.10.2026 · ursprünglich lokal, jetzt unter `rechnungen/` · nichts committet, keine Repo-Datei verändert, kein `__pycache__` im Repo-Baum (geprüft mit `find`), `git status --short` leer. Keine Websuche.
Kennzeichnung: **[Q]** Quelle mit Fundstelle · **[R]** eigene Rechnung (Skript hier) · **[E]** eigene Einschätzung · **[A]** Annahme.

## 1 Gelesen

Kontext
- (Quelle außerhalb des Repositorys) §8–§13 (Z. 259–430).
- (Quelle außerhalb des Repositorys) vollständig; `p2/empfehlungen.md` vollständig; `p2/befunde.csv` AUS-08/12/13/14, ENG-05/10, STA-06/08/09/11/12, LB-10/11/13, KM-09/10/11/12, SYM-02 (mit Spalten verif_urteil/verif_korrektur).
- `rechnungen/auslegung/mu_modell.py` (Modell, `rk4_mu`), `a4b_bistabilitaet.py` + Ausgabe; `rechnungen/auslegung/verifikation/PROTOKOLL.md` Z. 150–151 und `v5_nichtlinear_D_ausgabe.txt` (Herkunft der Stoßabbildung).
- (Quelle außerhalb des Repositorys) (alle 14 Bündel, 88 Kandidaten, 8 P2-Stränge); `rechnungen/zusatz_p2/PROTOKOLL.md` vollständig.
- Ergebnisse der Rollen: `rechnungen/bewertung_a/PROTOKOLL.md` + alle `*_ausgabe.txt`; `rechnungen/bewertung_b/PROTOKOLL.md` + `b1`, `b3`, `b4`, `b5` Ausgaben.

Hauptquellen
- Präreg v2 Entwurf `docs/praeregistrierung_v2_entwurf.md` Z. 82–565 (§2–§12).
- Präreg-Anhang `docs/praeregistrierung_v2_anhang.md` A2.4–A2.5 (Z. 184–203), A4–A7 (Z. 238–360), A9.1–A9.2 (Z. 421–503), A9.7–A9.12 (Z. 565–645), Tabelle C (Z. 647–671).
- AP v2.4 Z. 660–678 (Perret-Liaudet), 2090–2112 (Bahnprofil/Antrieb), 2440–2462 (Hilfskanäle); FV v2.7 Z. 796–816; `code/linear_solver.py` Z. 70–100, `code/finesweep.py` Z. 35–45; `docs/arbeitspapier/references.bib` Z. 116–140; `docs/arbeitspapier/PCMMS_Arbeitspapier_Offene_Punkte.md` (grep Nocke).

Fundstellen (Stichprobe an der Originalstelle; Dateinamen ohne Pfad sind Quellen außerhalb des Repositorys)
- Archiv-Vermerk vom 28.09.2026 (Quelle außerhalb des Repositorys) §2.1 (Z. 61–70), §9.1 (Z. 237–242) – formelalt, Adaptionsgesetz.
- Kurzdossier (Quelle außerhalb des Repositorys) Z. 99–101, 166–176 (Pendeltest, Aktorwahl A7, Spiegelung A9).
- (Quelle außerhalb des Repositorys) Z. 155–167 (Abbruchkriterium).
- `PCMMS_Baustein14_…docx.txt` Z. 88–149 (Ring, Messkette), Z. 225–236 (§14.11 Selbsttäuschungskatalog).
- (Quelle außerhalb des Repositorys) §6.2 (Z. 355–361).
- (Quelle außerhalb des Repositorys) Z. 80–87; (Quelle außerhalb des Repositorys) Z. 116.
- `pcmms_v3a_geglaettet.py.txt` (Docstring).
- (Quelle außerhalb des Repositorys) Z. 66–92; (Quelle außerhalb des Repositorys) (Gliederung, §4–§5).
- (Quelle außerhalb des Repositorys) (Gliederung).
- (Quelle außerhalb des Repositorys) (Gliederung), `pcmms_lageregelung_3achs.py.txt` (Docstring).
- SOT 01.10. Z. 53 (Linie B → Forschungsrahmen v3_5).
- Volltextsuche im Bestand: Linearaktor/Voice-Coil (nur Planungen V2/Forschungsrahmen), Nocke/Vorspannung/formschlüssig (keine Nockenfolger-Auslegung).
- (Quelle außerhalb des Repositorys) (Lesestatus für Dateien des Bestands).

## 2 Vorgehen

1. Alle jetzt_v1/vor_v1_pruefen-Bündel (B03–B09, B11) und neuen Kandidaten mit jetzt_v1/vor_v1_pruefen gegen Präreg v2 (was ist schon registriert?), P2 (gegengeprüfte Fassung) und die Originalfundstelle geprüft.
2. verwerfen/parken stichprobenhaft auf übersehene Algorithmen geprüft (#83, #24, #69, #5, #45, B12, B14).
3. Zahlenangaben der Rollen gegen deren Skriptausgaben abgeglichen.
4. Die sicherheitsrelevante Aussage B06 („Hüpfzustand bei V1 synchron, ζ_krit ≈ 0,152“) mit dem P2-Modell eigenständig nachgerechnet (Widerlegungsversuch).

## 3 Eigene Rechnungen

Alle: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../../code timeout 540 python3 <skript>`; Modell: `rechnungen/auslegung/mu_modell.rk4_mu` (P2, einseitiger Kelvin-Voigt mit kraftbasierter Ablösung N = max(0, −Kz − Cż)), V1-Vorschlag μ = 0,4615, Hub 8 mm, 10 Hz, K = 1,5·10⁶ N/m [A wie P2]; Wurfstart v0 aus statischer Ruhelage, Wurfphase über globale Phasenverschiebung; Auswertung 12–16 s.

| Skript | Frage | Ergebnis [R] |
|---|---|---|
| `vb1_einzelmodul_huepfen.py` | Hüpfen auch im Einzelmodullauf L_j? | Stoßabbildung: ζ_krit(synchron) = 0,152, ζ_krit(Einzelmodul) = 0,050. Numerik T/2000 und T/4000 identisch: ζ = 0,02 → 9 von 30 Würfen (0,5/0,8 m/s) dauerhaftes Hüpfen, λ 97,9 %, F_max 482 N; ζ = 0,05 → 1 von 30 (0,5 m/s), 483 N; ζ = 0,1 → keiner. |
| `vb2_schnitt_piloten_huepfen.py` | Schnitt, Triphasik, Piloten, (0°,180°) | ζ = 0,02: Hüpfzustände an (100°,240°) 482 N, (110°,240°) 162 N, (120°,240°) 158 N, (130°,230°) 165 N, (110°,252°) 163/482 N, (0°,180°) 482–969 N; ζ = 0,05: nur (0°,180°) 484 N. |
| `vb3_konvergenz.py` | Zeitschritt T/2000 → T/4000 | 5 von 6 Treffern bleiben (Triphasik 158 N, Pilot (110°,252°) 481 N, (0°,180°) 483 N, Einzelmodul ζ = 0,05 und 0,02); (130°,230°) v0 = 0,5 ist Zeitschrittartefakt. T/8000 nach 540 s abgebrochen. |
| `vb4_zeta_schwelle.py` | Gilt ζ_krit ≈ 0,152 auch bei großen Würfen? | synchron: Hüpfen bei ζ = 0,10, 0,14 **und 0,17** (500 N); bei 0,20 keines; (0°,180°) ab ζ = 0,1 keines. |
| `vb5_zeta017_kontrolle.py` | Feinabtastung ζ, T/4000 | synchron, v0 = 0,5 m/s: Hüpfen bei ζ = 0,15/0,16/0,17 (495–498 N), keines ab 0,18. → numerische Schwelle 0,17 < ζ_krit < 0,18 (nur diese Würfe/Wurfphase). |

Folgerung [E]: Die Stoßabbildung mit e = exp(−πζ/√(1−ζ²)) unterschätzt die Schwelle, weil der geklippte Kelvin-Voigt-Kontakt bei N = 0 ablöst (vor der Rückkehr der Einfederung auf null) und damit stoßelastischer ist als angenommen. Die Empfehlung ζ ≥ 0,2 hält im Modell, aber mit nur ≈ 0,02–0,03 Abstand statt 0,05; die Hüpfgefahr betrifft bei kleinem ζ auch Einzelmodul-, Schnitt- und Pilotläufe.

## 4 Wichtigste Befunde der Gegenprüfung

1. B06/B05: Schwelle ζ_krit falsch (0,152 → numerisch 0,17–0,18), Geltungsbereich zu eng (nicht nur synchron) [R].
2. B04: Erfolgskriterium innerlich widersprüchlich (Hertz-Kontakt und quadratische Kettennichtlinearität skalieren beide ∝ A²; „konstant“ ist Drift); Aufwand der zweiten Amplitude/Frequenz unterschätzt (eigene Einzelmodulläufe, Nocke hat festen Hub); P2-Teile „Paarläufe“ und „P0.4 unter Betriebslast“ nicht aufgenommen.
3. B11: Schwerpunkt „3-FG-Mismatch für H3“ bei steifem V1 schwach begründet: nach Präreg §8.7/A4 prüft H3 dort den Kontakt bei k ≤ 3 nicht; lineare Kippmoden erzeugen keine H1-Signatur (STA-11). Relevanter Mismatch: Auslegungswerkzeug (Zellreserve) und nichtlineare Szenarien.
4. Doppelte bzw. widersprüchliche Bewertungen zwischen den Rollen: Echtzeit-Abschaltung (a: jetzt_v1; b: vor_v1_pruefen), Sinus-/ungerade-harmonischer Referenzlauf (a: B02 nach_v1; b: vor_v1_pruefen); Modulkinematik in Phase 1 dreifach (B04 P2-6, B07 kinematischer Kanal, B09 #79); Werkzeug-8-Spezifikation vierfach (B01, B04, B08, B11).
5. bewertung_a nennt 62 statt 52 Kandidaten für B01–B07.
6. Bestätigt: AP-6.10-Kriterium „0 g im freien Fall“ ist bei μ < 1 falsch; Nockenfolger braucht Vorspannung/Formschluss (a_Halt = π²·Hub·f²/TH = 12,15 m/s² > g); AP v2.4 Z. 2103–2105 („Linearaktor liegt bereits vor“) im Bestand nicht belegt – zusätzlich gestützt durch Kurzdossier A7 (Z. 168).
7. Übersehen: Nennlast-/Auflösungs-/Steifigkeitskonflikt (Zellbereich 10² N gegen u_c ≲ 10 mN und K ≥ 1,03·10⁶ N/m); Mechanismusmodell der Modulkopplung fehlt für Werkzeug 8; kinematische Lagerung ist selbst ein Hertz-Kontakt in Reihe zur Zelle.

## 5 Grenzen

- Alle eigenen Rechnungen: 1-FG-Modell der P2 mit Festschritt-RK4 (T/2000, T/4000), ideales Egg-Profil, angenommene V1-Parameter; keine Kippmoden, kein Hertz-Fußkontakt; Wurfphase nur in 60°/90°-Schritten; ereignisgenauer Löser nicht verwendet. Die numerische Schwelle ist eine Stichprobe, keine Einzugsgebietskarte.
- Literaturangaben (Perret-Liaudet, Regimeanalyse-DOIs) nicht prüfbar ohne externe Quellen.
- Datenblattwerte für Zellsteifigkeit und -rauschen fehlen im Bestand; Aussagen zum Nennlastkonflikt sind [E]/[A].
