# AP-11 bis AP-13: Anpassung, Auswertung und synthetischer Pipelinetest — erste Softwarestufe

Stand 16.10.2026, mit den Korrekturen A–E vom selben Tag (Abschnitt 1a), der k-Konsistenz mit dem Ablauf der Phase 1
vom 17.10.2026 (Abschnitt 1b), den Korrekturen vom 18.10.2026 (Abschnitt 1c) und dem Regelstand 2026-11 vom 20.10.2026
(Abschnitt 1d) · Basis `a1c9953` (`main` nach PR #19) · Paket [`code/pcmms_auswertung/`](../code/pcmms_auswertung/)
(Code MIT, dieses Dokument CC BY 4.0) · Umgebung der Prüfläufe: Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1, 4 Kerne.
*Nur Software und Simulation.* Es gibt keine Messdaten, keine Hardwarewahl, keine Festlegung offener Regeln und kein
ausgefülltes Teil B; synthetische Kennungen beginnen mit `SYNTH-` und behaupten keine Registrierung. Die
Präregistrierung, A0, Tabelle F, das Arbeitspapier v2.5 und das Formelverzeichnis v2.8 sind bis zum Stand vom
18.10.2026 unverändert; der Regelstand 2026-11 (Abschnitt 1d) ändert Normtext der Präregistrierung als
Arbeitsfestlegungen des Autors vom 20.10.2026 (A0).

Begleitdokumente: [Schnittstellen](ap11_ap12_ap13_schnittstellen.md) (Formate, Trennstelle, Zufallsströme,
Ausgabestruktur), [Regelmatrix](ap11_ap12_ap13_regelmatrix.md) (jede Regel mit Fundstelle, Status und Wert, aus dem
Code erzeugt), [Kriterienmatrix](ap11_ap12_ap13_kriterien.md) (K01–K21, Zuordnung, H1Z, E3 mit Status, aus dem
Prüfstand erzeugt), Plan [AP-13](plan_ap13_pipelinetest.md) mit Vermerk vom 16.10.2026.

## Kurzfassung

- **Regelstand 2026-11** (20.10.2026, Abschnitt 1d): Ablauf ablauf-4, P0.7-Anordnung, G4 mit B+ und k(n), simulierte
  Wiederaufnahme, Bezugsmengen G/A mit Nachziehen, Reservebedingung 0,95, E3 nach Option B, Laufgrößen- und
  Strukturmodell aus Phase 0 für Planung und Teil B; implementiert und softwaregetestet, an kleinen Beispielen
  untersucht, **nicht statistisch kalibriert**: Die große Kalibrierung ist nach Entscheidung des Autors nicht
  ausgeführt, ein ausführbares Beispiel liegt in [`rechnungen/kalibrierbeispiel/`](../rechnungen/kalibrierbeispiel/README.md).
- **Ausführbare Kette.** Generator (Ebene Z mit Rohzeitreihen, Ebene H mit Laufzusammenfassungen; Wahrheit getrennt) →
  AP-11 (Kalibrierung aus P0-Daten, Pilotanalyse, Teil B) → AP-12 (Stufe 1, Stufe 2) → Bewertung gegen die Wahrheit,
  aus einer frischen Ausgabestruktur ohne Handarbeit (`kette`) oder in Einzelschritten; dazu Harness-Befehle für
  Kampagnen, Kalibrier- und Prüfsimulation von c, Prüfstand, Kriterienmatrix und Prüfsatz (Abschnitt 2).
- **AP-11 und AP-12 an Synthetik geprüft.** Rückgewinnung und Unsicherheiten der Anpassverfahren über feste Seeds,
  Diagnosen bei Modellabweichungen; Stufe 1 gleich Ebene H; Entscheidungen und Grenzfälle wie nach dem Regeltext; H1 und
  Zeltfit gleich einer unabhängigen Referenz (4000 Zeltfits ohne Abweichung); eine Kampagne mit den normativen
  Replikatzahlen (B = 10 000) in 78 s.
- **AP-13 teilweise umgesetzt.** Kalibrierung von c mit getrennter Prüfsimulation (bei A4 griff die Pool-Regel:
  Prüfrate 18/193 > 0,069, gepooltes c = 3,71 gegen c_B = 4,20), H2-Überdeckung und gemeinsame Bestätigungswahrscheinlichkeit
  als getrennte Größen (A4: 0,965; V1-G0: 0,82; V1-G60h: 0,75 bei n = 24, n_min = 18), Planungshaken, Ebenenabgleich,
  Wahrheitstrennung, Reproduzierbarkeit und Prüfsatz geprüft; alle 36 Katalogszenarien durchlaufen (34 mit 30–200
  Kampagnen je Simulation, die beiden S₃-Fälle deterministisch).
- **Keine Kalibrierabnahme.** Alle Raten sind Entwicklungsdiagnostik (B = 1000, höchstens 200 Kampagnen je Simulation).
  Die Kriterienmatrix führt 1 Kriterium als geprüft (K16, deterministisch), 16 als nur probeweise gerechnet, 1 als
  fehlend, 5 als fachlich offen und 1 als in diesem Modell nicht prüfbar, ohne Gesamtampel. Die Matrix mit ≥ 1000
  Kampagnen je Szenario und Stufe (geschätzt ≈ 450 Kernstunden) ist vorbereitet, nicht gestartet.
- **Korrekturen A–E** (Abschnitt 1a): Planungshaken mit dem Plan des Kandidaten, Zeitmittel ⟨N⟩ aus den Rohzeiten,
  Phase von k = 2 in E3a, Nullkontrolle ohne definierten Test, Unsicherheit von T in E3. Der Prüfstand (Abschnitt 4.4)
  und die Kriterienmatrix stammen vom Stand `7a259ef` vor diesen Korrekturen. Die betroffenen Teile sind am 17.10.2026
  gezielt neu gerechnet ([Neulaufbericht](ap13_neulaeufe_2026-10-17/bericht.md)): Die K12-Suche findet weiterhin keinen
  zulässigen Arbeitspunkt, der verrauschte Ebenenabgleich (K19) ist bitgleich und innerhalb der 5-%-Schranke, die
  ausgewählten E3-Raten (11 Punkte, 570 Kampagnen) bleiben mit Unsicherheit von T unverändert. Die übrigen E3-Zahlen
  des Prüfstands sind historisch ohne T-Anteil.
- **Wichtigste Befunde** (Abschnitt 6): G4 mit σ_Δ aus den Piloten verliert konfigurationsabhängig Punkte und senkt die
  gemeinsame Bestätigungswahrscheinlichkeit; der Drift-Zusatz (a) erscheint auch ohne Drift; F_min ist unter S₃ nur bis
  auf die Rasterschranke invariant; C03 und A07 prüfen K11 und K21 mit dem Katalog nicht; die quadratische Kette I02
  kollidiert mit G1; E3 verfehlt „unauffällig ≥ 0,8“ auf L1, auch mit Unsicherheit von T (Neulauf vom 17.10.2026).
- **Diagnose E3b und G4** (17.10.2026, [Diagnosebericht](e3b_g4_diagnose_2026-10-17/bericht.md), Entscheidungsvorlage,
  keine Regel geändert): „unbestimmt“ von E3b folgt aus dem Betrag des komplexen Residuums (Rayleigh); G4 unterschätzt
  die Fünftel-Streuung an steilen Flanken (Jitter × Steigung), eine vorab aus Phase 0 bestimmte Standardisierung
  behebt das weitgehend; die Reserve „+2“ reicht mit den Wiederholungen nach A9.12, die der Generator nicht abbildet.
  Die Begründung der Pilotsuche nennt jetzt den tatsächlichen Abbruchgrund (`pilot-0.2`).
- **k-Konsistenz und Wiederholungsablauf** (17.10.2026, Abschnitt 1b,
  [Bericht](ap13_kmax_wiederholungen_2026-10-17/bericht.md), keine Regel geändert):
  - Die Phase-0-Größen (σ_Δ, Gültigkeitsmaske, σ̂_ref, ε_ctrl, p̂, Streuungen) entstehen als Satz bei k_max und N_z des
    verwendeten Plans; bis PR #22 galten sie bei A4 für k = 30 statt 9.
  - Phase 1 kann als zustandsbehafteter Ablauf mit den Wiederholungen nach A9.12 laufen, auf Ebene H und über
    Ebene Z/Stufe 1.
  - In der begrenzten Rechnung (105 Kampagnenausführungen) sind abgeschlossene Kampagnen mit Wiederholungen
    vollständig. 5 von 30 halten nach S1 oder S3 an.
  - Korrekturrunde vom 18.10.2026 (Abschnitt 1c): X′ gegen R₂/R₃, Suchtreffer ohne k-Wechsel, S2-Bilanz online wie
    offline; 39 weitere Kampagnenausführungen mit `ablauf-2` bestätigen die Befunde. Nachtrag (`ablauf-3`): R₃ folgt
    unmittelbar auf X′, auch wenn X′ eine S3-Wiederholung auslöst; keine gerechnete Kampagne ist davon betroffen.
  - Werkzeug 8, die Prüfstandsraten, K12 und die E3-Zähler sind für den neuen Ablauf nicht übertragbar.

## 1a Korrekturen vom 16.10.2026

Nach der ersten Prüfung wurden fünf Fehler behoben, je mit Regressionstest, der am alten Stand den Fehler zeigt (bei B,
C und D in den betroffenen Fällen; die Erhaltungstests des Standardfalls und die regulären Fälle bestanden dort schon). Die historischen Zahlen in
Abschnitt 4.4 und in der Kriterienmatrix bleiben der Lauf auf `7a259ef`; sie sind nicht mit neuen Einzelwerten
vermischt. Präregistrierung, Schwellen, offene Regeln, G4, δ_H2, δ_H3, die E3-Schwellen, die Bonferroni-Regel und der
Drift-Zusatz sind unverändert.

| | Fehler | Korrektur | Regression, Gegenprobe | betroffene historische Ergebnisse | verbleibender Neulauf |
|---|---|---|---|---|---|
| A | Planungshaken: N_z änderte nur den Seed; simuliert wurden die Vorgaben des Grundplans (100 Zyklen, T_Lauf = 17 s, 1 Messtag) | `5d52e6c`: Plan der Kampagnensimulation mit n_zyklen = N_z, T_Lauf und d aus dem Pilotskript, Abbruch bei widersprechendem f, T_a, N_K oder N_I, `plan_simuliert` je Kandidat | `test_planungshaken_simuliert_gewaehlte_fensterlaenge`: N_z = 20 und 80 im instrumentierten Aufruf; echte Läufe mit diesem Plan auf Ebene H (Zyklen, Laufdauer, Messtage, Budget von n_max) und je ein Rohlauf auf Ebene Z durch Stufe 1 (gezählte Zyklen, Fensterdauer); am alten Stand 100 statt 20 Zyklen | Planungsschritt des Prüfstands (K12): N_z = 100 stimmte zufällig, simuliert wurden aber T_Lauf = 17 s statt 16 s und 1 statt 2 Messtagen. Die Kandidatenraten (P ≤ 0,25) und „kein zulässiger Arbeitspunkt“ sind potenziell betroffen (Zeitlage der Drift, Tagesstruktur) | erledigt am 17.10.2026 (147 s): Suchergebnis unverändert, [Neulaufbericht](ap13_neulaeufe_2026-10-17/bericht.md) Abschnitt 2; eine Planung für Teil B bleibt eine eigene Rechnung mit ≥ 1000 Kampagnen je Kandidat |
| B | Stufe 1: ⟨N⟩ war das Mittel der auf N_θ resampelten Zyklen (Phasenmittel), bei ungleichen Perioden nicht das Zeitmittel nach A1 | `87c5888`: Zeitintegral über die akzeptierten Zyklusintervalle aus den Rohzeiten (`stufe1-0.2`); Bedeutung je Verarbeitungsstand, alte Zusammenfassungen werden gemeldet | vier Rohdatentests: 99/101 ms (4,010 N statt 4,000 N), Grenzen zwischen Abtastwerten mit ausgelassenem Zyklus, Fünftel (4,010 und 5,575 N), Standardfall gleicher Perioden; Meldung der alten Bedeutung; am alten Stand drei von vier fehlgeschlagen | nur Rohdatenketten (Ebene Z → Stufe 1): ⟨N⟩ in G1, G4 (D_N), σ̂_ref, ε_ctrl, Nullkontrolle, S-Regeln und N_s. Der Generator der Ebene Z hat gleiche Periodendauern; der rauschfreie Abgleich Z ↔ H bleibt bei 3·10⁻⁷ N. Potenziell betroffen: der verrauschte Ebenenabgleich (K19, je 4 Kampagnen) und die Ebene-Z-Läufe in Abschnitt 4.3. Ebene H (fast der ganze Prüfstand) und F_min − ⟨N⟩ (aus den Harmonischen) sind nicht betroffen | erledigt am 17.10.2026 (266 s): u_c-Mediane bitgleich, innerhalb 5 %, [Neulaufbericht](ap13_neulaeufe_2026-10-17/bericht.md) Abschnitt 3 |
| C | E3a aus k = 2 wurde erst nach der Halbierung gewickelt: Scheinfehler 180° bei exakt passender zweiter Harmonischer | `0397d48`: zuerst modulo 360° auf Ebene der Harmonischen, dann halbiert; Bezug und 180°-Mehrdeutigkeit im Ergebnis (`k2_hinweis`) | `tests/test_ap12_kontrollen.py`: T = I mit 0°/120°/240° (vorher 180° für Module 2 und 3), Phasen über den Argument-Sprung mit kleinen Fehlern (k = 2 gleich k = 1), Mehrdeutigkeit (δ = 100° erscheint als −80°) | nur berichtete k = 2-Werte; die Bewertung nutzt k = 1, die Raten sind nicht betroffen | keiner |
| D | Nullkontrolle mit beiden Stichprobenvarianzen null: Welch-Satterthwaite 0/0, NaN-Grenzen, trotzdem „prüfbar“ und „kein Unterschied nachgewiesen“ | `eddc156`: „nicht prüfbar“ mit Grund, Differenz und Stichprobenzahlen, ohne Testaussage und ohne Ersatzstreuung; nicht endliche Größen ebenso | 10 × 0,125 N gegen 10 × 0 N bei ε_ctrl = 0,01 N, gleiche Konstanten, eine konstante Stichprobe und zwei gewöhnliche gegen `scipy.stats.ttest_ind` (ν, Intervall), zu wenige und nicht endliche Werte, ohne Laufzeitwarnung | keine Raten des Prüfstands (alle Läufe verrauscht); betroffen wären rauschfreie Grenzfälle | keiner |
| E | E3: alle Replikate mit fester Inverse des nominellen T; die Ziehungen aus der Unsicherheit von T (A9.13) fehlten | `6e28cd5`: Unsicherheitsbeschreibung in Teil B `nr5`, Ziehungen je Replikat aus (g, x, y), Kette und f_n, ζ (Kette und 1 FG gemeinsam, ohne Doppelzählung), eigener Strom `E3/T`; ohne Beschreibung nur numerische Diagnostik | unabhängige T-Formulierung (Flächenverhältnisse); u(Δφ) gegen eine unabhängige lineare Sensitivitätsrechnung bei bekannter Kovarianz (Kettenlaufzeit, korrelierte Zelllage, Verstärkung; Verhältnis 0,99–1,00 bei B = 4000); Nullkovarianzen gleich festem T; gemeinsamer Faktor H ohne Wirkung; Zelllagen in E3b heben sich auf; Reproduzierbarkeit, gemeinsame Ziehungen, unzulässige Ziehungen, fehlende und unvollständige Beschreibung, Datei-Rundreise | alle E3-Raten des Prüfstands (z. B. „unauffällig“ 14/200 bei N01-A4, „auffällig“ 30/30 bei A06, H03 und E04, 36/40 bei E07) und die E3-Zeile der Kriterienmatrix sind ohne T-Anteil gerechnet. Die synthetischen Kalibrierungen sind sehr genau (Zelllagen 1–2 µm, Kettenlaufzeit ±14 ns); ob sich die Raten merklich ändern, war bei der Korrektur nicht nachgerechnet | erledigt am 17.10.2026 für 11 Punkte mit 570 Kampagnen (971 s): alle Zähler unverändert, [Neulaufbericht](ap13_neulaeufe_2026-10-17/bericht.md) Abschnitt 4; die übrigen E3-Zahlen bleiben historisch ohne T-Anteil. Eine Schwellenentscheidung folgt daraus nicht |

Grenzen der Korrekturen: Die Planung nutzt weiter das Szenariorauschmodell statt eines Generators aus gemessenen
Pilotkovarianzen. In E3 bleiben Modullagen (Konstruktion) und Kippmoden ohne Unsicherheit bzw. ohne Modell; getrennte
Kalibriermessungen ohne Kreuzkovarianz im Format werden als unabhängig gezogen; bei nicht identifizierbarem P0.4 (A4)
bleibt H(kω) nominal, weil es sich als gemeinsamer Faktor in E3a exakt aufhebt (die berichteten Amplituden |Ĉⱼ,₁|
tragen dann keine H-Unsicherheit). Jede E3-Auswertung nennt das unter `t_unsicherheit`. Ein Neulauf des ganzen
Prüfstands (91 min) ist für diese Korrekturen nicht nötig; die genannten Teilläufe sind am 17.10.2026 gerechnet
(23 min auf 4 Kernen, [Neulaufbericht](ap13_neulaeufe_2026-10-17/bericht.md)), mit den unveränderten
Werkzeug-8-Werten des Laufs auf `7a259ef`.

**Neuläufe vom 17.10.2026** (Rechnung auf `020e131`, Profil, Plan, n_min und Basis-Seed wie im Prüfstand, Ergebnisse
mit Herkunft in [`ap13_neulaeufe_2026-10-17/`](ap13_neulaeufe_2026-10-17/bericht.md)):

- **K12** (Korrektur A): Mit dem Plan des Kandidaten (N_z = 100, T_Lauf = 16 s, 2 Messtage) bleibt das Ergebnis „kein
  zulässiger Arbeitspunkt unter diesen Annahmen“; P(H1 und H2 bestätigt) der vier simulierten Kandidaten 0/4, 1/4, 0/4,
  0/4 (vorher 1/4, 0/4, 0/4, 0/4), n_max = 743 bindet nicht; 26 Aufrufe wegen der Entwicklungsgrenze nicht simuliert.
- **K19** (Korrektur B): Ebene Z mit `stufe1-0.2`; alle u_c-Mediane beider Ebenen bitgleich zum Altlauf, relative
  Differenzen −2,54 % bis +1,39 %, H1, H1Z, H2, H4 je 4/4 bestätigt. Bei gleichen Periodendauern des Generators wird die
  Korrektur in diesem Abgleich nicht sichtbar.
- **E3** (Korrektur E): N01-A4/L1 (200 Kampagnen der Prüfkohorte `pruefung_c`), A06, H03, E04, E07 (2), N03 (2) auf L1 und
  N01-A4 auf L0, L2, L4: alle Zähler unverändert (z. B. „unauffällig“ 14/200), keine Kampagne ohne dreiwertige
  Bewertung, keine unzulässige T-Ziehung; u der E3a-Phasen im Median 0,0–1,1 % größer (höchstens 3,5 %), u(q_Z)
  unverändert. „unbestimmt“ entsteht auf L1 allein an E3b, in dem T nicht vorkommt.

Gezielte Läufe nach den Korrekturen (Endstand, reduzierte Replikatzahlen B = 200, Entwicklungsdiagnostik; sie prüfen
Funktion und Korrekturen, keine Fehlerraten oder Power):

- **Dateiketten mit Stufe 1** aus frischer Ausgabestruktur auf Ebene Z (`kette --ebene Z`, je 811 Rohläufe): N01-A4
  (exakte Superposition) H1, H1Z, H2 und H4 bestätigt, H3 nicht entscheidbar (Verfahren), Nullkontrolle regulär, E3
  „unbestimmt“, 268 s; A04-R4 (Kopplung, Klasse R4) H1 und H1Z falsifiziert mit „Abweichung nachgewiesen“, H2 und H4
  bestätigt, 257 s. Alle Zusammenfassungen tragen `stufe1-0.2`.
- **Ebenen Z ↔ H rauschfrei** für N01-A4 und N01-V1G60h innerhalb der Schranken: Harmonische 1,4·10⁻⁵ bzw.
  0,9·10⁻⁵ N, ⟨N_c⟩ 3·10⁻⁷ N, Zeiger 2,5·10⁻³ bzw. 3,4·10⁻³.
- **Wahrheitstrennung** am Ebene-Z-Ergebnis von N01-A4: gleiche Prüfsumme bei unveränderter, geänderter (der Harness
  sieht Klasse R4) und entfernter Wahrheit.
- **E3-Gegenprobe** mit bewusst gewählter Unsicherheit (G60h, B = 4000, feste Seeds und Bootstrap-Indizes): u(Δφ) aus
  den T-Ziehungen zur unabhängigen linearen Referenz 0,996/0,996 (Kettenlaufzeit), 0,992/1,001 (korrelierte Zelllage),
  0,994/0,994 (Verstärkung) für Modul 2/3; wiederholt mit denselben Seeds bitgleich.
- **Endabnahme**: `python3 -m pytest tests -q` 328 bestanden, 8 übersprungen (382 s); `(cd data && python3 ../code/linear_solver.py --validate)` bestanden (2 s); `python3 rechnungen/neuheit/bibcheck.py` ohne Fehler; `harness pruefsatz --pruefen tests/fixtures/ap13_pruefsatz` gleich (25 s); zusammen 410 s auf 4 Kernen.

## 1b k-Konsistenz und Wiederholungsablauf vom 17.10.2026

Zwei technische Änderungen ohne Regeländerung (Auftrag vom 17.10.2026,
[Bericht](ap13_kmax_wiederholungen_2026-10-17/bericht.md) mit maschinenlesbaren Ergebnissen, Auftragsliste und
Laufprotokoll). Präregistrierung, Regelprofile, G4-Formel mit Faktor 3, Poolregel und normative Schwellen sind
unverändert.

- **Bindung der Phase-0-Größen an den Plan** (`pilot-0.3`, `teil_b-0.3`):
  - Bis PR #22 bildete das Pilotskript σ_Δ, die Gültigkeitsmaske der Phase 0 (damit n₀ⱼ für ŷ⁰ und den S3-Bezug),
    σ̂_ref, ε_ctrl, p̂, Rauschkovarianzen und gepoolte Streuungen bei k der Pilotgrößen (A4: k = 30). Teil B übernahm
    sie und prüfte Phase 1 mit k_max des Plans (A4: 9).
  - Jetzt entstehen alle diese Größen als ein Satz bei k_max und N_z des verwendeten Plans (`pilot.satz_fuer_plan`,
    `teil_b.phase0_satz`). Die Bindung nennt k, N_z, Fünftel, T_a, Herkunft und Prüfsumme der Phase-0-Daten sowie Seed
    und Datensatzzahl von ε_ctrl.
  - Unvereinbare Eingaben brechen ab. Der Arbeitspunkt wird ohne neue Suche erneut geprüft (`nr2.arbeitspunkt`:
    „abgesichert“, „nicht abgesichert“, „nicht geprüft“).
  - Ältere Pilot- und Teil-B-Dateien bleiben lesbar und gelten als historisch, nicht qualifiziert (`einordnen`).
  - A4 mit zehn Seeds: σ_Δ,F im Mittel 1,84 → 1,66 mN, ungültige Piloten 12/600 → 8/600, G4 in Phase 1
    166 → 221 von 5040 Läufen. V1-G0 und V1-G60h (k = k_max = 12) sind bitgleich.
- **Zustandsbehafteter Ablauf der Phase 1** (`ablauf.py`, `ablauf-1`, seit 18.10.2026 `ablauf-2`, nach dem Nachtrag
  `ablauf-3`; nur Simulation, keine DAQ):
  - Geplante und ausgeführte Reihenfolge sind getrennt. Jeder Versuch hat Kennung, Bezug, Zähler, Rolle, Anlass, Zeit
    und Gründe; verworfene Versuche bleiben erhalten.
  - Zusätzliche Versuche verbrauchen T_Lauf und verschieben spätere Läufe und die Drift.
  - Wiederholungsplätze zieht der Reihenfolgegenerator von §6 gleichverteilt (protokolliert).
  - Umgesetzt sind §6, §8.8, §9.1, §9.2 und A9.12: Konfigurationswiederholungen, R₀/R₁/R₂/X′/R₃, Nullpunktalarm,
    Kontrollwiederholungen mit L′-Ausnahme, S1–S4 und Aufwärmen.
  - Ein Halt gibt einen fortsetzbaren Ablaufstand zurück. Fortgesetzt wird nur mit einem ausdrücklich übergebenen
    externen Ereignis.
  - Dieselbe Steuerung läuft auf Ebene H und über Ebene Z/Stufe 1.
  - Stufe 2 prüft beim Ablauf, dass ihre Gültigkeit den Entscheidungen des Ablaufs gleicht, zählt je Konfiguration und
    Block höchstens einen Versuch und sperrt bei nicht abgeschlossenem Ablauf alle Ausgänge.
  - Einstellung 2: Die Lücken (G2–G4, S-Regeln für L′) werden gekennzeichnet; es gibt keine Qualifikationsaussage.
- **Verfahren** (`verfahren.py`, `verfahren-1`):
  - Bindung `plan`/`historisch` und Ablauf `statisch`/`zustand` mit Ablaufversion und Optionen. Sie gehören zu den
    Checkpoint-Schlüsseln von Kampagnen, Kalibrierung, Planung und Prüfstand (`--verfahren`).
  - Vorgabe ist `statisch` mit Bindung an den Plan; die Treiber von PR #21 und #22 rechnen ausdrücklich `historisch`
    nach.
  - Der Software-Prüfsatz (`tests/fixtures/ap13_pruefsatz`: Katalog, Profile, Generatorausgaben des statischen
    Laufplans) ist unverändert und weiter gleich. Der Ablauf hat einen eigenen Prüfsatz
    (`tests/fixtures/ap13_ablauf_pruefsatz`, fünf Prüfkampagnen mit inhaltlicher Gegenprobe).
  - Der Planungshaken trennt geplante und realisierte Messzeit; die normative Zeitformel ist unverändert.
- **Begrenzte Rechnung** (105 Kampagnenausführungen einschließlich Diagnose, Gegenproben und Abnahmelauf, 6 volle Ketten
  in der Rechnung, 0,20 Kernstunden; A4, V1-G0, V1-G60h mit je zehn Seeds von PR #22 in drei Varianten; Variante mit
  Wiederholungen in der Korrekturrunde mit `ablauf-2` neu gerechnet, Zahlen gleich):
  - Mit Wiederholungen kommen je Kampagne 11–78 Versuche hinzu, die Laufzeit abgeschlossener Kampagnen steigt um
    5–6 %.
  - Jede abgeschlossene Kampagne ist vollständig (mindestens 23 von 24 gültigen Läufen je Punkt).
  - 5 von 30 halten an: S1 nach reproduziertem Nullpunktalarm (2) oder G1-Verstoß von X′ gegen R₂/R₃ (2), S3 (1).
  - Gemeinsam vollständig: 25/30 historisch, 24/30 k-konsistent ohne und 25/30 mit Wiederholungen. Die Ursache
    wechselt von Punkten unter n_min zu Halten.
  - Volle Ketten (Nullfall N01-A4, Artefaktfall A04-R4, Ebene H und Z): Entscheidungen unverändert.
- **Nicht übertragbar** auf den neuen Ablauf und die Bindung an den Plan: Werkzeug 8 von PR #21 und #22 (c,
  Rauschbias, H2-Intervalltyp), die gemeinsame Bestätigungswahrscheinlichkeit und alle Raten des Prüfstands, K12, die
  E3-Zähler und die Reserveaussage von PR #22. Die Neuläufe sind im Bericht abgeschätzt (Kalibrierung je System grob
  18–81 Kernstunden), nicht gestartet.

## 1c Korrekturen vom 18.10.2026 (PR #23)

Drei bestätigte Fehler aus der unabhängigen Prüfung von PR #23, je mit Regressionen, die am Stand 9a1cd2f den Fehler
zeigen und jetzt bestehen ([Bericht](ap13_kmax_wiederholungen_2026-10-17/bericht.md), Abschnitt „Korrekturrunde vom
18.10.2026“). Präregistrierung, Regelprofile, normative Schwellen, G1-Grenze und Wiederholungsgrenze sind unverändert.

| | Fehler | Korrektur | Regression, Gegenprobe | betroffene Ergebnisse | Neurechnung |
|---|---|---|---|---|---|
| 1 | Die Vorprüfung gegen R₀ lief auch für X′; in R₂, X′, R₃ kam ein R₁, X′ wurde gegen R₂/R₁ geprüft, S1 konnte vor R₃ anhalten | `ablauf-2` (0008dd8): X′ ohne Vorprüfung, Klammer an R₂/R₃ desselben G1-Falls gebunden und protokolliert; S1 nur mit dieser gültigen Klammer, sonst „S1 nicht prüfbar“; Stufe 2 prüft die Klammer offline; Platzstatus aus strukturierten Angaben | Gegenprobe der Anweisung (0,0095 N gegen R₂/R₃, am alten Stand R₁ und S1 bei 0,0105 N), verletzendes X′ nach R₃, spät erkannter Verstoß, X′ jenseits der Grenze, unvollständige Klammer, Fortsetzung, Übergabe an Stufe 2 | Ablauf-Prüfsatz (Prüfsummen, Inhalt gleich); in 39 Kampagnen keine Entscheidung, nur Texte und drei Platzbenennungen | 30 Vergleichskampagnen, 4 volle Ketten, 3 Regelpfade: Befunde gleich, kein X′ mit R₁ unter `ablauf-1` |
| 2 | Suchtreffer beim ursprünglichen k (k = 12 → 12, N_z = 100): `phase0_satz` übernahm den vorläufigen Satz, `arbeitspunkt` lehnte allein wegen dessen Quelle ab | 4266bc3: Satz der Suche geht bei festgelegtem Paar vor; Herkunft über Quelle und Bindung (`gleich_gebunden`) | Testhaken beim ersten Paar (reiner Softwareprüffall): am alten Stand „nicht abgesichert“, jetzt „abgesichert“; fremde Daten, abweichender Plan, zu kleine Reserve, andere Bindung weiter zurückgewiesen bzw. nicht abgesichert | keine gerechnete Kampagne (ohne Planungshaken ist die Suche „offen“) | – |
| 3 | Online zählte ein S2 mit bestätigtem Apparaturfehler nicht, offline galt `len(s2) >= 2`: ein abgeschlossener Ablauf konnte in `datenlage` global gesperrt werden | 305c7b7: `gueltigkeit.s2_bilanz` online und offline, Übergabe im Ablaufstand, Abgleich in `datenlage`; Ausschlüsse bleiben; fehlende oder widersprüchliche Angaben geben nichts frei; S2 während eines anderen Halts gezählt | Gegenprobe der Anweisung, zwei S2 ohne Apparaturfehler, widersprüchliche Angaben, S2 im dritten Versuch eines Kontrolllaufs, Übergabe auf Ebene H (mit Fortsetzung aus dem gespeicherten Halt) und über Ebene Z/Stufe 1 | keine gerechnete Kampagne (keine Wiederaufnahme in den Katalogkampagnen) | Regelpfad S02 neu gerechnet: Halt wie bisher |
| 4 | Nachtrag (verschachtelte Wiederholungen): Die S3-Wiederholung eines X′ (Kontrolllauf) stand vor dessen R₃. Löste sie selbst die Vorprüfung aus, schloss deren R₁ die Klammer: X′ gegen R₂/R₁, S1 „nicht prüfbar“, ein erforderlicher Halt blieb aus (reproduziert am Stand 836f2c4) | `ablauf-3` (377fc26): Was X′ auslöst, folgt erst nach seinem R₃ (§9.2: R₂, X′, R₃; A8: X′ mittig); Stufe 2 prüft offline, dass auf ein nach G2–G10 gültiges X′ unmittelbar sein R₃ folgt (ausgenommen ein Halt an X′ vor R₃); Ablaufstände von `ablauf-2` werden nicht fortgesetzt | fünf Regressionen, am Stand 836f2c4 alle fehlgeschlagen: S1 nach R₃ trotz S3-Wiederholung mit eigener Vorprüfung (0,015 N gegen R₂/R₃), bestehendes X′ mit reproduziertem S3 nach R₃, Offline-Zurückweisung der alten Folge, Fortsetzung aus dem Ablaufstand, Halt an X′ im Kontrollsatz einer Wiederaufnahme | keine gerechnete Kampagne: In den 37 Ablaufkampagnen folgt auf jedes der 33 X′ mit G1-Prüfung unmittelbar sein R₃ (eines ist ein Kontrolllauf, ohne S3-Wiederholung); Ablauf-Prüfsatz nur in Version und Verfahrenskennung neu | keine (nicht nötig; Zusatzbudget ausgeschöpft) |

- Neurechnung: 39 zusätzliche Kampagnenausführungen (Zusatzbudget 40), davon 4 volle Bootstrap-Auswertungen
  (Zusatzgrenze 4), 0,20 Kernstunden; bisher 105 Ausführungen, zusammen 144, davon 11 volle. Statische Varianten sind
  nach Codeanalyse, Stichprobe und Software-Prüfsatz unberührt und mit Herkunft 13f2a20 übernommen.
- Die vier S1-Halte der Rechnung bleiben; die zwei nach X′ sind gegen die vorgesehene Klammer R₂/R₃ belegt.
- Der Ablauf-Prüfsatz ist nach einer Gegenprüfung neu geschrieben (Inhalt gleich, Prüfsummen von Köpfen und
  Entscheidungen neu). Der Software-Prüfsatz und die Ergebnisse von PR #21/#22 sind unverändert.
- Nachtrag (`ablauf-3`): Der Ablauf-Prüfsatz wich vor dem Neuschreiben nur in Ablaufversion und Verfahrenskennung ab;
  Inhalt und alle Prüfsummen der fünf Prüfkampagnen sind gleich. Die Ergebnisse der Korrekturrunde sind mit
  `ablauf-2` gerechnet und gelten unverändert für `ablauf-3`; ihre Checkpoints passen nicht mehr zum heutigen
  Rechencode, neu gerechnet ist nichts.

## 1d Regelstand 2026-11 vom 20.10.2026 (Gesamtumsetzung a–d, ohne große Kalibrierung)

Auftrag des Autors vom 20.10.2026 auf Grundlage der [Entscheidungsvorlage vom 19.10.2026](entscheidungsvorlage_2026-10-19.md)
(Abschnitt 9) und ihres [Belegpakets](entscheidungsvorlage_2026-10-19_belege/README.md). Neue Profile `AF-2026-11` und
`ENTW-2026-11` (Standard `ENTW-2026-11`); `AF/ENTW-2026-10` bleiben bitgleich und historisch (`regeln.ist_historisch`).
**Die große Kalibrierung ist nach Entscheidung des Autors nicht ausgeführt**; es gibt keine Kalibrierabnahme, und eine
bestandene Softwareprüfung ersetzt sie nicht. Normtext: Präregistrierung §5.2, §5.4, §6, §8.8, §8.10, §9.1, §9.2, §12,
A0, A8, A9.2, A9.3, A9.5, A9.11–A9.13 als Arbeitsfestlegungen vom 20.10.2026.

**Geändertes Verhalten unter den Profilen 2026-11** (historische Profile, Prüfsätze und Ergebnisse bis PR #23 unverändert):

| Bereich | bisher (2026-10) | jetzt (2026-11) | Code |
|---|---|---|---|
| Ablauf der Phase 1 | `ablauf-3` | `ablauf-4`: R₁ zuerst, R₂/X′/R₃ geschlossen (A1 + Z1); beim Halt entfallen ausstehende Folgeläufe, ein G1-Fall ohne gemessenes X′ erhält nach dem W-Satz eine neue Folge (H1); unvollständige Klammer: S1 nicht prüfbar, keine Sonderwiederholung (K1); Kontrollsatz mit S1–S4 (N5 + N7); Bezugseröffnung nach einem Nullpunkthalt (Rolle `bezugslauf`, `bezugswechsel`); Aufwärmen nur bei Tageswechsel; Offline-Gegenprobe in Stufe 2 | `ablauf.py`, `auswertung._folgen_gegenprobe` |
| P0.7 | historische Anordnung | höchstens zwölf andere Läufe zwischen zwei Referenzläufen (`Plan.p0_anordnung = 'p07'`) | `generator/kampagne.py` |
| G4 | Schwelle je Laufart | B+ für Kombinationsläufe (Mischung über die Laufgrößen, Verschiebung ±u(Δδ), Untergrenze 3σ_P), Lⱼ mit k(n₀ⱼ) und gepoolter Varianz; D als Diagnosemodus (`Regelprofil.mit_diagnose`); Fünftelzeiger als optionales Feld der Laufzusammenfassung | `g4.py`, `gueltigkeit.py`, `teil_b.py`, `stufe1.py`, `zusammenfassung.py` |
| Halte in der Simulation | ein Halt beendet die Kampagne | simulierte Wiederaufnahme fortsetzbarer Halte (W = 3, T_UA aus Teil B, Entwicklungsbeispiel 1800 s); zweites S2 oder erschöpftes W beendet endgültig | `harness/kette.py` |
| Bezugsmengen | alle Kampagnen | G (alle begonnenen) und A (abgeschlossen, alle Prüfgrößen endlich); c, Prüfrate, b̂, u(b̂), Restbias, H2-Überdeckung über A, P(H1 und H2 bestätigt) mit Nenner G; Nachziehen bis \|A\| = soll_A mit Versuchslimit 1,5·\|A\| | `harness/mengen.py`, `harness/kalibrierung.py` |
| c bei mehreren Rauschmodellen | gepoolt | Fassung (a): Quantil des Standardmodells, die übrigen als Sensitivität (`c_varianten`, `c_sensitivitaet`) | `harness/kalibrierung.py` |
| Planung | Reserve r = ⌈n_min·p̂/(1 − p̂)⌉ + 2 | zusätzlich Reservebedingung 0,95 mit r += 1 bis zehnmal, sonst „Reservegrenze“; Zielfunktion aus der Regel; Zeitbilanz nach Termen; Ablauf ablauf-4 als Vorgabe beim Szenariopfad | `harness/planung.py`, `harness/reserve.py` |
| Planung, Rauschquelle | Szenariomodell × κ(ν_p) | Phase-0-Modell aus dem Aufruf (Strukturmodell an den oberen 80-%-Grenzen je Komponente, gemeinsamer Bodenfaktor, c_B); Szenario nur als ausdrückliches Orakel | `harness/planung.py`, `generator/phase0_modell.py` |
| Laufgrößen | Pilotstreuungen | Laufgrößenmodell aus Phase 0 (d0) im Pilotskript und in Teil B (`pilot-0.4`, `teil_b-0.4`) | `laufgroessen.py`, `pilot.py`, `teil_b.py` |
| E3 | Intervallregel (am Schwellenrand nicht gültig) | Option B: m = 43, E3a mit gefaltetem t-Quantil, E3b nach Rice mit κ·λ_max und ν_eff, Rückfall „beschreibend“ je Prüfgröße; Kriterien aus der Prüfsimulation nur bei der normativen Zahl | `e3_grenzen.py`, `auswertung.py`, `teil_b.py` (nr10) |

**Status nach Kategorien.**

| Kategorie | Inhalt |
|---|---|
| implementiert und softwaregetestet | Profile und Regeln 2026-11 mit historischer Bitgleichheit (`test_regelstand_2026_11`, Software- und Ablauf-Prüfsatz ablauf-3); ablauf-4 (`test_ablauf4`, 14 Tests, neuer Ablauf-Prüfsatz `tests/fixtures/ap13_ablauf_pruefsatz_ablauf4.json`); G4-Modi, k(n), Pooling, Fünftelzeiger (`test_g4_2026_11`, 10); Wiederaufnahme, Mengen, Nachziehen, Reserve, Zeitbilanz (`test_harness_mengen`, 9; `test_planung_reserve`, 4); E3 Option B (`test_e3_grenzen`, 8; `test_e3_auswertung`, 13); d0–d2 (`test_d_laufgroessen`, 9; `test_d_phase0_modell`, 13; `test_d_planung_phase0`, 9); Kalibrierbeispiel (`test_kalibrierbeispiel`, 5) |
| an kleinen synthetischen Beispielen untersucht | G4 gepaart an 3 × 3 Kampagnen, End-to-End mit ablauf-4 an 5 Fällen und über Ebene Z ([`rechnungen/regelstand_2026-11/`](../rechnungen/regelstand_2026-11/README.md)); R1-d mit 45 Sätzen, R2-d mit 2 × 2 × (3 + 3), R3-d mit 2 + 2 Kampagnen (unten) |
| nur als ausführbares Beispiel vorbereitet | normative Kalibrier- und Prüfsimulation mit \|A\| = 1000 je Rolle ([`rechnungen/kalibrierbeispiel/`](../rechnungen/kalibrierbeispiel/README.md): Trockenlauf als Vorgabe, Demonstration „Demonstration, synthetisch, nicht kalibriert“); Auftragslisten R1-d (9 × 1000 Sätze), R2-d, R3-d (`harness/phase0_rechnungen.py`) |
| nicht statistisch kalibriert | alle Raten und kritischen Werte: Fehlausschlussrate von G4 (Arbeitsziel ≤ 1,5 %), Reservebedingung 0,95, c von H1/H1Z, H2-Überdeckung, E3-Kriterien, Planung mit dem Phase-0-Modell |
| nicht experimentell geprüft | alles: keine Messdaten, kein Teil B, keine Hardware |

**Teil d in Kleinstgröße** (Endstand der Teilbearbeitung, process_time): R1-d (45 Sätze an N01-A4, N04-laufart,
N03-ungleich × L0/L2/L4; 19 s): Verhältnis Schätzung/Wahrheit für σ_δ,j, σ_off,j, Jitter und Boden 0,82–1,15 (bei L0
ist die wahre Amplitudenstreuung 0), Ablehnung der Kohärenzprüfung 0–0,17. R2-d (91 s): Kette läuft, mit 3 Kampagnen
ohne Aussage. R3-d (27 s; im Gesamtstand für den Phase-0-Haken nachgerechnet, 18 s): Das Szenario-Orakel legt n_min = 18
fest (P = 1,0); der Phase-0-Haken ergibt P = 0, beide Prüfkampagnen mit H1 „nicht entscheidbar“ (im Gesamtstand Grund
Graubereich; in der Teilbearbeitung vor B+ Datenlage). Der Rauschbias stammt dabei aus einer einzigen verwertbaren
Kalibrierkampagne (Restbias 2,1 ± 1,2 bzw. 3,2 ± 0,9 u_c); bei dieser Größe ist die Ursache nicht von der
Monte-Carlo-Streuung zu trennen. Es ist keine Aussage über die Planung mit dem Phase-0-Modell.

**Grenzen dieses Stands.**

- Kampagnen aus der Phase-0-Modellquelle haben nur den statischen Laufplan (kein Vorrat des Strukturgenerators für
  den Ablauf). Die Reservebedingung 0,95 ist dort nicht prüfbar; der Planungshaken legt im Regelstand 2026-11 mit dem
  Phase-0-Modell deshalb keinen Kandidaten fest und berichtet den Kandidaten nach P allein (`kandidat_nur_P`).
- Nicht umgesetzt: Residuen-Bootstrap (Regel: optional), Einstellung 2 im Phase-0-Modell, Gauß-Modus als Generator,
  Modellprüfung der E3-Kriterien, Fassung (b) der Zielfunktion.
- Die Kalibrierung P0.4 ist in den letzten Bits nicht bitreproduzierbar (χ² der Linearität hängt vom
  `PYTHONHASHSEED` ab, Befund der Teilbearbeitung d); der Bitgleichheitstest von Teil d schließt deshalb die
  Prüfsummen von Kalibrierung und Pilotausgabe aus. Die Prüfsätze runden auf 12 Stellen und haben in der Endabnahme
  bestanden; eine Prüfung über verschiedene `PYTHONHASHSEED` ist nicht gemacht.
- Werkzeug-8-Werte, Prüfstandsraten, K12 und E3-Zähler früherer Stände sind auf den Regelstand 2026-11 nicht
  übertragbar.
- Die Stärken der benannten Sensitivitäten und die Regularisierung des Strukturmodells sind technische Regeln mit
  Vorschlagscharakter (`rauschmodelle.sensitivitaeten`, `p0.strukturmodell`), Festlegung beim Autor.
- Rechenaufwand neben der Testsuite: etwa 0,4 Kernstunden ([Protokoll](../rechnungen/regelstand_2026-11/README.md)).
  Die große Kalibrierung, die volle Matrix und große Planungsläufe wurden nicht ausgeführt.

## 1 Erreichter Umfang

| Paket | umgesetzt | geprüft an | offen |
|---|---|---|---|
| AP-11, Werkzeug 4 (`anpassung.py`) | P0.1 Kennlinie je Zelle, Laststellen mit Rang- und Identifizierbarkeitsprüfung, Kraftkette aus dem Brückensimulator mit Modellwahl; P0.2 nach Konvention (b); P0.4 1-FG-Anpassung mit Kohärenzgewichtung, Kovarianz, χ², Band- und Identifizierbarkeitsdiagnose, K und C mit M + m_L, Linearität zweier Amplituden, Moden aus den Zellkanälen, exzentrische Anregung; P0.5 Harmonische, G_x, Δδⱼ mit u(Δδⱼ) als prüfbare Anforderung; gehashte Kalibrierung, H3-Eingänge nur daraus | unabhängig erzeugten P0-Daten mit bekannten Parametern, Überdeckung der Unsicherheiten über 25–40 feste Seeds, Modellabweichungen (Kette zweiter Ordnung, falscher Brückensimulator, amplitudenabhängige Steifigkeit, exzentrische Restmasse, falsches G_x), Fehlfälle (kollineare Laststellen, f_n außerhalb des Bands, starre Auflage, zu wenige Indeximpulse) | Kennlinienform der Umrechnung (linear, quadratischer Anteil nur berichtet), reale P0-Daten, P0.3, P0.6 |
| AP-11, Werkzeug 5 (`pilot.py`, `gueltigkeit.py`) | §5.4/A9.2: σ_c, F_LO, σ_tol, σ_Δ, σ̂_ref, ε_ctrl mit simuliertem kritischem Wert (A9.8), Reihenfolge G2–G10 → ε_ctrl → G1, p̂, gepoolte s_q mit ν_p und oberer 80-%-Grenze, Rauschkovarianzen je Laufart, T_φ, Rampe; Suche nach k_max, T_a, n_min, n₀ in der Reihenfolge von A9.2 mit Haken der AP-13-Planung | Phase-0-Daten der Generatoren; Ausgabeprüfung gegen Residuen-, Vorhersage- und Entscheidungsfelder; Suche bis „kein zulässiger Arbeitspunkt“ | Planung aus gemessenen Pilotkovarianzen; Zeitangaben für n_max sind Eingaben |
| AP-12, Stufe 1 (`stufe1.py`) | A9.4 Schritte 1–6 für alle Laufarten gleich: statische Kalibrierung je Zelle, Summe, Segmentierung an den Indeximpulsen (fehlende und überzählige Impulse), vollständige Zyklen, lineares Resampling auf N_θ = 2000, Mittelkurve, DFT; Rohextrema über den ganzen Lauf, Fünftel, Zeiger, Jitter, T_φ; fehlende Kanäle gemeldet | Ebene Z gegen Ebene H rauschfrei; Sättigung und Indexfehler aus dem Rohkanal; fehlender Kanal | AP-10-Rohdatenformat |
| AP-12, Stufe 2 (`auswertung.py`, `h1.py` … `h4.py`, `zeltfit.py`, `bootstrap.py`, `kontrollen.py`, `teil_b.py`) | G1–G10, S1–S4 offline; ŷ⁰ (feste B⁰-Replikate aus Teil B) und ŷ¹; Bootstrap A/B nach A9.5; H1 mit IUT-TOST und Mindesteffekt gegen beide Vorhersagen, Rauschbias, Sensitivitäten getrennt; H1Z; H2 mit exaktem Kandidaten-Zeltfit, drei Fits je Replikat, Rückfallkette; H3 Fassung K mit MC; H4; Nullkontrolle; Zuordnung und E3 (dreiwertig nur im Entwicklungsprofil); Gründe, Zusätze, Herkunft maschinenlesbar und als Kurztext | Entscheidungen und Grenzfälle an Szenarien mit bekannter Wahrheit; unabhängige Referenz für H1 und Zeltfit (`referenz/`) mit denselben Indizes; Vergleichssatz mit 4000 Zeltfits; ein Lauf mit den normativen Replikatzahlen | Optionen nach §12 im Entwicklungsprofil gewählt, nicht festgelegt; H3 Fassung I, H1′/H2′, Paarläufe, übrige Sensitivitäten von A9.9 |
| AP-13, Generator (`generator/`) | Ebene H und Ebene Z aus denselben Laufziehungen, synthetische P0-Daten, Phase 0/1 nach §6 und A9.12, Rauschmodelle L0–L5 getrennt nach Laufart, lineare 3-FG-Zellkräfte, Hertz-Kontakt über den ereignisgenauen Löser, Wahrheit getrennt, Katalog der Mindestfälle | analytische Gegenproben, Abgleich mit `linear_solver.py`, Ebene Z ↔ H | Gruppen B, D, G; Einzelzell-Liftoff mit Stoßdynamik |
| AP-13, Harness (`harness/`) | Kette im Speicher und aus Dateien; Kampagnen mit festen Seeds; Kalibrier- und Prüfsimulation von c mit Pool-Regel; Rauschbias; H2-Überdeckung und Typwahl; gemeinsame Bestätigungswahrscheinlichkeit; Planungshaken; Ebenenabgleich; S₃-Prüfung; Wahrheitstrennung; Software-Prüfsatz; Kriterienmatrix; Prüfstand; Kommandozeile | Abschnitt 4 | Matrix mit ≥ 1000 Kampagnen je Szenario und Stufe; Generator aus gemessenen Pilotkovarianzen |

## 2 Aufrufe

Alle Befehle vom Repository-Stamm; Hilfe mit `python3 code/pcmms_auswertung <befehl> -h`. Profil, Reduktion,
Kampagnenzahl, Seeds, Plan und Ausgabeziel sind ausdrückliche Argumente; ohne Profil bricht ein Befehl ab.

Abnahme:

```sh
python3 -m pytest tests -q
(cd data && python3 ../code/linear_solver.py --validate)
python3 rechnungen/neuheit/bibcheck.py
```

Kette aus einer frischen Ausgabestruktur in einem Schritt (Ebene H ca. 5 s, Ebene Z ca. 4,5 min):

```sh
python3 code/pcmms_auswertung kette --szenario A04-R4 --stufe L1 --seed 7 --ebene H --band 20 600 \
  --profil ENTW-2026-10 --red bootstrap_B=200,h3_mc=1000,eps_ctrl_datensaetze=300 --n-min 18 --ausgabe /tmp/pcmms_k
```

Dieselbe Kette in Einzelschritten (`R="--profil ENTW-2026-10 --red bootstrap_B=200,h3_mc=1000,eps_ctrl_datensaetze=300"`,
`D=/tmp/pcmms_e`):

```sh
python3 code/pcmms_auswertung generator --szenario A04-R4 --stufe L1 --seed 7 --ebene Z --n-min 18 --ausgabe $D
python3 code/pcmms_auswertung ap11 kalibrierung --p0 $D/eingang/p0_messung --band 20 600 --ausgabe $D/eingang/kalibrierung
python3 code/pcmms_auswertung ap12 stufe1 --manifest $D/eingang/laeufe --kalibrierung $D/eingang/kalibrierung \
  --ausgabe $D/eingang/zusammenfassungen                                      # nur Ebene Z
python3 code/pcmms_auswertung ap11 teil-b --zusammenfassungen $D/eingang/zusammenfassungen \
  --kalibrierung $D/eingang/kalibrierung --planangaben $D/eingang/planangaben --werkzeug8 testvorgabe \
  --ausgabe $D/eingang/teil_b --pilot $D/eingang/pilot $R
python3 code/pcmms_auswertung ap12 auswerten --zusammenfassungen $D/eingang/zusammenfassungen \
  --kalibrierung $D/eingang/kalibrierung --teil-b $D/eingang/teil_b --ausgabe $D/ergebnis/ergebnis $R
python3 code/pcmms_auswertung harness bewerten --ergebnis $D/ergebnis/ergebnis --wahrheit $D/wahrheit/wahrheit
```

Harness:

```sh
# c, Rauschbias, H2-Intervalltyp aus Kalibrier- und Prüfsimulation → Werkzeug-8-Datei für ap11 teil-b
python3 code/pcmms_auswertung harness kalibrierung --szenario N01-A4 --stufe L1 --kampagnen-kal 200 \
  --kampagnen-pruef 200 --seed 20261016 --prozesse 4 --n-min 18 --ausgabe /tmp/pcmms_w8 $R
python3 code/pcmms_auswertung harness kampagnen --szenario A04-R4 --stufe L1 --kampagnen 40 --seed 20261016 \
  --werkzeug8 /tmp/pcmms_w8/werkzeug8 --prozesse 4 --n-min 18 --ausgabe /tmp/pcmms_kamp $R
python3 code/pcmms_auswertung harness pruefstand --ausgabe /tmp/pcmms_ps --prozesse 4   # gezielte Läufe, Abschnitt 4.4
python3 code/pcmms_auswertung harness kriterien --pruefstand /tmp/pcmms_ps/pruefstand --ausgabe docs/ap11_ap12_ap13_kriterien.md
python3 code/pcmms_auswertung harness pruefsatz --pruefen tests/fixtures/ap13_pruefsatz
python3 code/pcmms_auswertung harness matrix --kampagnen 1000 --seed 1 --ausgabe /tmp/pcmms_matrix   # nur Auftragsliste
python3 code/pcmms_auswertung harness neulauf             # Neuläufe K12/K19/E3 nach Auftragsliste, mit Checkpoints
python3 code/pcmms_auswertung harness neulauf --bericht   # Alt-Neu-Vergleich (docs/ap13_neulaeufe_2026-10-17/)
python3 code/pcmms_auswertung harness diagnose-e3b-g4 [--startsatz]   # G4-Ergänzungsläufe der Diagnose, mit Checkpoints
python3 code/pcmms_auswertung harness diagnose-e3b-g4 --bericht       # Diagnose E3b/G4 (docs/e3b_g4_diagnose_2026-10-17/)
python3 code/pcmms_auswertung harness kampagnen ... --verfahren zustand   # Phase 1 als Ablauf mit Wiederholungen (A9.12)
python3 code/pcmms_auswertung harness ablauf-pruefsatz --pruefen tests/fixtures/ap13_ablauf_pruefsatz   # Prüfsatz des Ablaufs
python3 code/pcmms_auswertung harness ablauf-vergleich [--startsatz]   # begrenzte Rechnung k-Konsistenz/Ablauf, mit Checkpoints
python3 code/pcmms_auswertung harness ablauf-vergleich --bericht       # Bericht (docs/ap13_kmax_wiederholungen_2026-10-17/)
PCMMS_SLOW=1 python3 -m pytest tests/test_ap12_auswertung.py -k vollraster_4000 -s   # 4000 Zeltfits gegen Vollraster
```

Parallele Läufe (`--prozesse`) verwenden Arbeitsprozesse mit je einem BLAS-Thread; die Ergebnisse hängen nicht von der
Prozesszahl ab. Weniger Replikate oder Kampagnen als normativ stehen in der Profilkennung (`…+red(…)`), in jedem Ergebnis
(„REDUZIERT (Entwicklungsdiagnostik)“) und an jeder Rate („reduziert“). `harness matrix` schreibt nur die Auftragsliste
der großen Matrix (≥ 1000 Kampagnen je Szenario und Stufe) und startet sie nicht.

`--verfahren` (bei `kampagnen` und `kalibrierung`) wählt Bindung und Ablauf:

- `statisch` (Vorgabe): Bindung an k_max und N_z des Plans, Laufplan ohne Ablaufentscheidungen.
- `zustand`: Bindung an den Plan, Phase 1 als Ablauf mit Wiederholungen.
- `historisch`: Bindung an k der Pilotgrößen wie bis PR #22, nur zur Nachrechnung.

Das Verfahren steht in jedem Ergebnis und in den Checkpoint-Schlüsseln. Ein angeforderter Ablauf fällt nie still auf
den statischen Laufplan zurück.

## 3 Regelgrundlage

Maßgeblich sind die Präregistrierung v2 mit Anhang im Stand `a1c9953` und deren Arbeitsfestlegungen; der Plan AP-13 nur,
soweit sein Anhang „Abgleich mit `main`“ ihn nicht überholt. Die [Regelmatrix](ap11_ap12_ap13_regelmatrix.md) führt
125 Regeln mit Fundstelle, Status und Umsetzung: im Profil AF-2026-10 14 Arbeitsfestlegungen, 18 Regeln des Regeltexts, 22 Zahlenwerte aus Tabelle F, 25 technische Umsetzungsdetails, 37 offene Entscheidungen und 9 nicht implementierte Optionen; im Profil ENTW-2026-10
sind 31 offene Regeln als Entwicklungsprüffälle gewählt (z. B. δ_H2 = 1°, δ_H3 = 10 %, w = 6°, Rückfallkette (a),
Bezugswert der Überdeckung, Grenzen von H1Z, E3-Schwellen, Zuordnungsregel (a), Rauschmodellfamilie), 6 (Rückfall für H1, Lesart „H2 entscheidbar“, Drift-Zusatz bei H2, G2–G4 bei Einstellung 2, S-Regeln für L′, zusätzliche Power-Bedingung)
bleiben auch dort offen. Offene Regeln haben keinen Vorgabewert: Wer sie braucht, erhält „nicht entscheidbar (Grund:
Regel offen …)“ oder nur numerische Prüfgrößen. Technische Umsetzungsdetails ohne eigene Regelwirkung stehen als
„technisch“ in der Matrix, darunter in dieser Etappe: Replikate von H2 und E3 als Zeilen der Bootstrap-Indexmatrizen,
Wertung nur vollständiger Kampagnen beim Quantil von c, Pooling, Überdeckung gegen beide Vorhersagen, Rauschmodell der
Planungssimulation und Seeds der Kampagnen.

## 4 Prüfergebnisse

### 4.1 Tests

Basis `a1c9953`: 135 bestanden, 6 übersprungen (Stand PR #19). Vor den Korrekturen A–E: 294 bestanden, 8 übersprungen
(376 s). Endstand nach den Korrekturen: `python3 -m pytest tests -q` → 328 bestanden, 8 übersprungen (382 s). Übersprungen sind die langsamen Prüfungen (`PCMMS_SLOW=1`), darunter der
Vergleichssatz mit 4000 Zeltfits; er wurde gesondert ausgeführt (Abschnitt 4.3). Die Tests des Stands `a1c9953` sind
unverändert; die Testdateien unten sind neu. In `tests/test_pcmms_formate.py` (Etappe 1) wurde die Erwartung zur
Reduktion in Etappe 5 verschärft (h2_replikate und e3_mc folgen bootstrap_B).

| Testdatei | Tests | Gegenstand |
|---|---|---|
| `tests/test_pcmms_formate.py` | 21 | Pflichtköpfe, Schemata, Datenarten, deterministische NPZ, Regelprofile und Reduktion, Regelmatrix gleich Code, Beispieldatensatz bitgleich, Wahrheit getrennt, Zufallsströme |
| `tests/test_ap13_generator.py` | 29 Funktionen (mit Parametern mehr) | analytische Gegenproben (starre G0, Egg-Harmonische), Abgleich mit `linear_solver.py` und `auslegung.py`, Ebene H (Superposition, Streuungen je Laufart, Reproduzierbarkeit, Ereignisse), Abtastrate nach A6, Ebene Z ↔ H, P0-Daten, Szenarienklassen, Hertz über den ereignisgenauen Löser, Wahrheit getrennt |
| `tests/test_ap11_anpassung.py` | 23 Funktionen | Überdeckung der Unsicherheiten über feste Seeds, Modellabweichungen, Fehlfälle, Pilotskript ohne Residuen und Entscheidungen, Suchreihenfolge, ε_ctrl, Gültigkeit aus dem Rohkanal, Importtrennung |
| `tests/test_ap12_auswertung.py` | 26 Funktionen | Stufe 1 gegen Ebene H, Regeln aus dem Rohkanal, Zeitmittel ⟨N⟩ bei ungleichen Perioden, Grenzen zwischen Abtastwerten, ausgelassenem Zyklus und in den Fünfteln (Korrektur B), Meldung der alten Bedeutung, Entscheidungen und Grenzfälle, Reproduzierbarkeit, fehlende Teil-B-Werte, E3 ohne Unsicherheit von T (Korrektur E), Profil AF, N₃ bindet, H3 bei falscher Kette, Zuordnung, Importtrennung, H1 gegen Referenz, Zeltfit gegen Vollraster, Regressionen (Intervalltyp „keiner“, Stressszenario) |
| `tests/test_ap12_kontrollen.py` | 16 Funktionen (27 Fälle) | E3a aus k = 2 (Korrektur C), Nullkontrolle bei verschwindenden Varianzen gegen SciPy (Korrektur D), Unsicherheit von T in E3 gegen unabhängige Formulierung und lineare Referenz (Korrektur E) |
| `tests/test_referenz_selbst.py` | 15 Funktionen | Selbstprüfung der unabhängigen Referenz (H1-Formeln, Grenzfall, Vollraster) |
| `tests/test_ap13_harness.py` | 16 | Raten, Seeds und Prozesse, c mit Pool-Regel, Überdeckung und gemeinsame Bestätigung, Rückfallkette, Planungshaken mit dem simulierten Plan des Kandidaten (Korrektur A), Wahrheitstrennung, Dateikette mit Rundreise der neuen Metadaten, Ebenen, S₃, Prüfsatz, Kriterienmatrix, CLI |

### 4.2 AP-11

Geprüft an unabhängig erzeugten synthetischen P0-Daten mit bekannten Parametern (`tests/test_ap11_anpassung.py`):
z-Werte (Schätzwert − Wahrheit)/u über 25–40 feste Seeds mit Streuung im Band 0,6–1,5 und Mittel nahe 0 für Nullpunkt
und Empfindlichkeit je Zelle, Laststellen (1/g, x/g, y/g), Zellverstärkungen, Kraftkette, f_n und ζ der 1-FG-Anpassung
(χ²/ν 0,7–1,4) sowie Δδⱼ. Modellabweichungen werden diagnostiziert statt verdeckt: Kette zweiter Ordnung,
falscher Brückensimulator (Widerspruch zur Statik), amplitudenabhängige Steifigkeit (Linearitätsprüfung), exzentrische
Restmasse (1-FG-Prüfung), falsches G_x-Datenblatt. Fehlfälle mit verständlicher Diagnose: kollineare Laststellen (nicht
bestimmbar, kein Optimiererwert), f_n außerhalb des Bands, nicht identifizierbare Anpassung, zu wenige Indeximpulse,
starre Auflage ohne Mode. u(Δδⱼ) ≤ 0,1° ist eine prüfbare Anforderung: bei großem Jitter wird sie als nicht erfüllt
gemeldet. Das Pilotskript gibt keine Residuen, Vorhersagen oder Entscheidungen aus (Feldprüfung `pruefe_ausgabe`), auch
nicht mit angebundener Planung; ohne Planung meldet es die Planung als offen, ohne zulässiges k „kein zulässiger
Arbeitspunkt“. In der Kette verwenden Teil B und AP-12 nachweislich die AP-11-Kalibrierung aus der Datei
(`kalibrierung_sha256` im Ergebnis).

### 4.3 AP-12

- **Rohdatenweg gegen Zusammenfassungsweg.** Rauschfrei trifft Stufe 1 die Ebene H für alle Laufarten: Harmonische
  ≤ 3·10⁻⁵ N (Interpolation nach A6), Mittel ≤ 2·10⁻⁶ N, Zeiger ≤ 10⁻² (1-µs-Zeitstempel), Rohminima ≤ 2·10⁻⁴ N.
  Sättigung einer Zelle (G5) und ein fehlender Indeximpuls (G2/G10) werden aus dem Rohkanal erkannt, obwohl die Summe
  unauffällig ist; ein fehlender Kanal wird gemeldet. Eine volle Kampagne auf Ebene Z (N01-A4, L1, n = 24, rund 810
  Rohläufe) liefert dieselben Ausgänge wie Ebene H.
- **Entscheidungen.** Exakte Superposition: H1, H1Z, H2, H4 bestätigt, H3 bei starrer Auflage nicht entscheidbar
  (Verfahren). Kopplung unter Δ_rel (A04-R1) bestätigt, über 2·Δ_rel (A04-R4) falsifiziert, an Δ_q (A04-R2, L0) nicht
  bestätigt. ŷ¹ ungültig (Liftoff in einem Kontrolllauf) oder fehlende Punkte: nicht entscheidbar (Datenlage). Fehlende
  Teil-B-Werte und Profil AF-2026-10: nicht entscheidbar mit Grund „Regel offen …“ bzw. „Verfahren“. Rauschfreie
  Grenzfälle (u_c = 0) nach der Regel `h1.grenzfall` ohne erfundene Unsicherheit. H3 mit falscher Kraftkette: kein
  Verdecken durch Anpassung an Einzelmodul-Kraftdaten. N₃ bindet unter Fassung B (N03-N3bindet). Zuordnung bei
  Kopplung (I01): Klasse p = 1. Die Nullkontrolle sagt nie „Gleichheit nachgewiesen“.
- **Unabhängige Referenz.** H1 (r, u, z, ν, TOST, Relevanz, Ausgang, Zusätze) gegen `referenz/h1_referenz.py` mit
  denselben Bootstrap-Indizes an N01-A4 (L2), A04-R2 und A04-R4 (L1): gleich innerhalb der Toleranzen von Plan 2.6 e
  (Kräfte 10⁻⁹ N + 10⁻⁹·|Wert|, u 10⁻¹² N + 10⁻⁹·u, z 10⁻⁷ + 10⁻⁹·|z|, ν relativ 10⁻⁹).
- **Zeltfit.** Kandidatenverfahren gegen das unabhängig geschriebene Vollraster (`referenz/zeltfit_referenz.py`) auf
  4000 Fits (asymmetrisches und symmetrisches Zelt, verrauschte Kurven, reines Rauschen, Gerade; 7, 9, 21 Punkte):
  3997 gleich, 3 Gleichstände innerhalb der Toleranzregel, 0 abweichend.
- **Normative Replikatzahlen.** Eine Kampagne mit unreduziertem Profil ENTW-2026-10 (B = 10 000, H2 mit denselben
  10 000 Zeilen, H3-MC 10 000, ε_ctrl-Simulation 10 000 Datensätze), Plan n = 20, n_min = 18: N01-A4 (L1) H1, H1Z, H2,
  H4 bestätigt, H3 nicht entscheidbar (Verfahren), Nullkontrolle ohne Unterschied; N01-V1G0 (L1) H1 nicht entscheidbar
  (Datenlage: G4 macht an S116/S118 3 bzw. 4 von 20 Läufen ungültig, Befund 1), H3 bestätigt mit Kennzeichnung „keine
  Harmonische k ≤ 3 prüft den Kontakt“, H4 bestätigt.
- **Abgleich mit Bestandswerten unter ihren Annahmen.** A4: D(F_min) = 0,5173 N, Δ_q(F_min) = 0,1293 N (Plan,
  STA-01); Kopplung 1 % → 12,16 mN (Plan 12,2 mN), Kopplung 10,638 % → genau Δ_rel (Plan N05). V1-G0: D_q in Fassung B
  0,5877 / 1,0664 / 0,6640 / 0,3893 N für F_min, N₁, N₂, N₃, gleich `auslegung.py --candidate` (bandbegrenzt k ≤ 12; der
  Planwert 0,560 N ist der ungebänderte Wert). Historische Raten der AP-08-Kontrolle und der P2-Statistik (Fassung A,
  B = 200, Regel vom 25.09., n = 20) sind unter anderen Regeln entstanden und wurden nicht als Sollwerte verwendet.

### 4.4 AP-13: gezielte Entwicklungsläufe (Prüfstand)

> **Vermerk (Korrekturen A–E, Abschnitt 1a).** Dieser Abschnitt ist der Lauf auf `7a259ef` vor den Korrekturen.
> Potenziell betroffen waren der Planungshaken (Korrektur A: T_Lauf und Messtage), der verrauschte Ebenenabgleich (B)
> und alle E3-Raten (E: ohne Unsicherheit von T; C betrifft nur berichtete k = 2-Werte). Planungsschritt,
> verrauschter Ebenenabgleich und die E3-Raten von N01-A4 (Prüfsimulation, L0, L2, L4), A06, H03, E04, E07 und N03
> sind am 17.10.2026 neu gerechnet ([Neulaufbericht](ap13_neulaeufe_2026-10-17/bericht.md), Abschnitt 1a): Ergebnis
> und Zähler unverändert. Die übrigen E3-Raten dieses Abschnitts sind historisch ohne T-Anteil; die anderen Zahlen
> beruhen auf Ebene H und sind nach Abschnitt 1a von den Korrekturen nicht berührt.

Ausgeführt mit `python3 code/pcmms_auswertung harness pruefstand --prozesse 4` auf Commit `7a259ef` (sauberer Worktree),
Profil `ENTW-2026-10+red(bootstrap_B=1000, e3_mc=1000, eps_ctrl_datensaetze=1000, h2_replikate=1000, h3_mc=1000)`,
Entwicklungsplan n₀ = 20 je Modul, 20 Läufe je Pilotkonfiguration, n = 24 Blöcke, n_min = 18 (nicht nach §5.4 geplant),
Präzisionsstufe L1, Basis-Seed 20261016. Kompakte Zusammenfassung:
[`ap11_ap12_ap13_pruefstand.json`](ap11_ap12_ap13_pruefstand.json) (Raten als Zähler/Nenner). Alle Raten sind
Entwicklungsdiagnostik: Die normative Kampagnenzahl ist 1000, die normative Replikatzahl 10 000.

**Kalibrier- und Prüfsimulation (exakte Superposition).** c, Rauschbias und Intervalltyp wurden je System aus einer
Kalibriersimulation bestimmt und in einer unabhängigen Prüfsimulation (eigene Seeds) über Teil B verwendet.

| System (Stufe) | c von H1 (q95 ± Bootstrap-SE) | c_B | c von H1Z | Prüfrate | gepoolt | Überdeckung Perzentil 0,95 ŷ⁰ / ŷ¹ | P(H1 und H2 bestätigt) | Restbias max \|E[r] − b̂\|/u_c |
|---|---|---|---|---|---|---|---|---|
| A4 (L1) | 3.709 ± 0.096 (n = 387, ohne 6) | 4.202 | 3.806 (c_B 4.643) | 0.093 ± 0.021 (18/193) | ja | 1.000 / 1.000 (n = 194); BCa 0.974 / 0.969 (n = 194) → perzentil_0.95 | 0.96 ± 0.01 (193/200) | yhat0: 0.26 (± 0.09), yhat1: 0.25 (± 0.08) |
| V1-G0 (L1) | 3.659 ± 0.091 (n = 40, ohne 20) | 4.202 | 3.670 (c_B 4.643) | 0.020 ± 0.020 (1/49) | nein | 1.000 / 1.000 (n = 42); BCa 0.976 / 0.976 (n = 42) → perzentil_0.95 | 0.82 ± 0.05 (49/60) | yhat0: 0.28 (± 0.14), yhat1: 0.29 (± 0.16) |
| V1-G60h (L1) | 3.596 ± 0.289 (n = 45, ohne 15) | 4.202 | 4.278 (c_B 4.643) | 0.022 ± 0.022 (1/45) | nein | 1.000 / 1.000 (n = 46); BCa 0.935 / 0.978 (n = 46) → perzentil_0.95 | 0.75 ± 0.06 (45/60) | yhat0: 0.30 (± 0.18), yhat1: 0.43 (± 0.16) |

Für A4 lag die Prüfrate mit 18/193 über 0,069; nach §8.4 gilt dann das 95-%-Quantil aus beiden Simulationen
(387 vollständige Kampagnen), und die Prüfsimulation wurde mit diesem c neu ausgewertet. Kampagnen, in denen ein
Schnittpunkt unter n_min fiel, zählen für das Quantil nicht (Regel `harness.c_vollstaendig`); an den V1-Systemen sind
das 20 bzw. 15 von 60 (Befund 1). Die Überdeckung des Perzentilintervalls ist bei exakter Superposition 1 (konservativ),
BCa liegt bei 0,94–0,98; gewählt ist nach der Rückfallkette das Perzentilintervall. Die gemeinsame
Bestätigungswahrscheinlichkeit ist eine eigene Größe: A4 0,965, V1-G0 0,82, V1-G60h 0,75 bei diesem Plan; die
Verluste sind durchweg „Datenlage“ durch G4. Der Restbias nach Korrektur (K13, Soll ≤ 0,1·u_c) ist mit 60–200
Kampagnen nicht prüfbar: Das Maximum über 21 Punkte liegt bei 0,25–0,43 bei einem MC-Fehler von 0,08–0,18 je Punkt.
Weitere Raten der Prüfsimulation A4: H1 nie falsifiziert (0/200), H1Z bestätigt 193/200, H2 bestätigt 194/200, H4
bestätigt 200/200, H3 nicht entscheidbar (Verfahren, starre Auflage), E3 „unauffällig“ 14/200, Zusatz „Drift der
Einzelmodulbasis“ ohne Drift 21/200 (Befund 3), ungültige Läufe 2,3 % (G4) und 0,6 % (G1).

**Szenariopunkte.** 40 Kampagnen je A4-Punkt, 30 je V1-Punkt und je Punkt mit eigenem System; „c, b̂“ nennt die
Herkunft der Werkzeug-8-Werte (A4 bzw. V1: Kalibrierung oben; Testvorgabe: c_B, b̂ = 0). Wahrheit: Klasse und größtes
wahres Residuum relativ zu Δ_rel aus der rauschfreien Vorhersage. „n. e.“ = nicht entscheidbar.

| Szenario/Stufe | Wahrheit (r_max/Δ_rel) | c, b̂ | H1 bestätigt | H1 falsifiziert | H1 n. e. (Gründe) | H1-Zusätze | H2 bestätigt | H3 best./fals. | H4 bestätigt | ungültig (Anteil Läufe) | Zuordnung | E3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A04-R1/L1 | R1 (0.50) | A4 | 39/40 | 0/40 | 1/40 Datenlage 1 | Abweichung nachgewiesen, Relevanz offen 1; Abweichung nachgewiesen, innerhalb der Äquivalenzgrenze 39; Drift der Einzelmodulbasis 40 | 39/40 | 0/40 / 0/40 | 40/40 | G4 0.021, G1 0.006 | — | unauffällig 3, unbestimmt 37 |
| A04-R2/L1 | R2 (1.00) | A4 | 0/40 | 0/40 | 40/40 Graubereich 39, Datenlage 1 | Abweichung nachgewiesen, Relevanz offen 40; Drift der Einzelmodulbasis 33 | 39/40 | 0/40 / 0/40 | 40/40 | G4 0.016, G1 0.006 | — | unauffällig 5, unbestimmt 35 |
| A04-R3/L1 | R3 (1.50) | A4 | 0/40 | 40/40 | 0/40  | Abweichung nachgewiesen 40; Drift der Einzelmodulbasis 34 | 40/40 | 0/40 / 0/40 | 40/40 | G4 0.017, G1 0.006 | — | unauffällig 9, unbestimmt 31 |
| A04-R4/L1 | R4 (2.50) | A4 | 0/40 | 40/40 | 0/40  | Abweichung nachgewiesen 40; Drift der Einzelmodulbasis 11 | 40/40 | 0/40 / 0/40 | 40/40 | G4 0.014, G1 0.006 | — | unauffällig 6, unbestimmt 34 |
| E07-basisdrift/L1 | R0 (0.00) | A4 | 39/40 | 0/40 | 1/40 Datenlage 1 | Abweichung nachgewiesen, innerhalb der Äquivalenzgrenze 2; Drift der Einzelmodulbasis 40 | 39/40 | 0/40 / 0/40 | 40/40 | G4 0.018, G1 0.007 | — | auffällig 36, unbestimmt 4 |
| E07-verstaerkung/L1 | R0 (0.00) | A4 | 37/40 | 0/40 | 3/40 Datenlage 3 | Drift der Einzelmodulbasis 40 | 38/40 | 0/40 / 0/40 | 40/40 | G4 0.026, G1 0.007 | — | unauffällig 6, unbestimmt 34 |
| H-fehlend/L1 | R0 (0.00) | A4 | 0/40 | 0/40 | 40/40 Datenlage 40 | Drift der Einzelmodulbasis 5 | 0/40 | 0/40 / 0/40 | 40/40 | G8 0.076, G4 0.021 | — | unauffällig 5, unbestimmt 35 |
| H01-zelt/L1 | R0 (0.00) | A4 | 40/40 | 0/40 | 0/40  | Drift der Einzelmodulbasis 3 | 40/40 | 0/40 / 0/40 | 40/40 | G4 0.020, G1 0.006 | — | unauffällig 4, unbestimmt 36 |
| N03-N3bindet/L1 | R0 (0.00) | A4 | 40/40 | 0/40 | 0/40  | Drift der Einzelmodulbasis 7 | 40/40 | 0/40 / 0/40 | 40/40 | G4 0.010, G1 0.005 | — | unauffällig 40 |
| N03-ungleich/L1 | R0 (0.00) | A4 | 34/40 | 0/40 | 6/40 Datenlage 6 | Drift der Einzelmodulbasis 5 | 34/40 | 40/40 / 0/40 | 40/40 | G4 0.037, G1 0.007 | — | unauffällig 3, unbestimmt 37 |
| N04-laufart/L1 | R0 (0.00) | A4 | 39/40 | 0/40 | 1/40 Datenlage 1 | Abweichung nachgewiesen, innerhalb der Äquivalenzgrenze 2; Drift der Einzelmodulbasis 8 | 40/40 | 0/40 / 0/40 | 40/40 | G4 0.022, G1 0.008 | — | unbestimmt 40 |
| N05-F/L1 | R2 (1.00) | A4 | 0/40 | 0/40 | 40/40 Graubereich 37, Datenlage 3 | Abweichung nachgewiesen, Relevanz offen 40; Drift der Einzelmodulbasis 33 | 37/40 | 0/40 / 0/40 | 40/40 | G4 0.019, G1 0.007 | — | unauffällig 3, unbestimmt 37 |
| N05-N2/L1 | R2 (1.00) | A4 | 0/40 | 0/40 | 40/40 Graubereich 38, Datenlage 2 | Abweichung nachgewiesen, Relevanz offen 40; Drift der Einzelmodulbasis 3 | 38/40 | 0/40 / 0/40 | 40/40 | G4 0.016, G1 0.006 | — | unauffällig 6, unbestimmt 34 |
| N05-N3/L1 | R2 (1.00) | A4 | 0/40 | 0/40 | 40/40 Graubereich 39, Datenlage 1 | Abweichung nachgewiesen, Relevanz offen 40; Drift der Einzelmodulbasis 3 | 39/40 | 0/40 / 0/40 | 40/40 | G4 0.022, G1 0.006 | — | unauffällig 7, unbestimmt 33 |
| S-indexfehler/L1 | R0 (0.00) | A4 | 39/40 | 0/40 | 1/40 Datenlage 1 | Drift der Einzelmodulbasis 4 | 39/40 | 0/40 / 0/40 | 40/40 | G4 0.024, G1 0.006 | — | unauffällig 5, unbestimmt 35 |
| S02-kontrolllauf/L1 | R0 (0.00) | A4 | 0/40 | 0/40 | 40/40 Datenlage 40 | — | 0/40 | 0/40 / 0/40 | 40/40 | G4 0.017, G1 0.007 | — | unauffällig 6, unbestimmt 34 |
| S06-saettigung/L1 | R0 (0.00) | A4 | 40/40 | 0/40 | 0/40  | Drift der Einzelmodulbasis 5 | 40/40 | 0/40 / 0/40 | 40/40 | G4 0.018, G1 0.007 | — | unauffällig 2, unbestimmt 38 |
| A06-phase/L1 | R1 (0.06) | V1 | 23/30 | 0/30 | 7/30 Datenlage 7 | Abweichung nachgewiesen, Relevanz offen 7; Abweichung nachgewiesen, innerhalb der Äquivalenzgrenze 23; Drift der Einzelmodulbasis 30 | 23/30 | 28/30 / 0/30 | 30/30 | G4 0.041, G1 0.006 | — | auffällig 30 |
| H03-phase/L1 | R1 (0.15) | V1 | 24/30 | 0/30 | 6/30 Datenlage 6 | Abweichung nachgewiesen, Relevanz offen 6; Abweichung nachgewiesen, innerhalb der Äquivalenzgrenze 24; Drift der Einzelmodulbasis 30 | 25/30 | 30/30 / 0/30 | 30/30 | G4 0.035, G1 0.005 | — | auffällig 30 |
| I01-amplitude/L1 | R1 (0.10) | V1 | 23/30 | 0/30 | 7/30 Datenlage 7 | Abweichung nachgewiesen, Relevanz offen 7; Abweichung nachgewiesen, innerhalb der Äquivalenzgrenze 23; Drift der Einzelmodulbasis 30 | 25/30 | 29/30 / 0/30 | 30/30 | G4 0.033, G1 0.007 | Klasse p = 1 20, nicht durchgeführt 1, nicht zuordenbar 9 | unauffällig 2, unbestimmt 28 |
| I01-frequenz/L1 | R1 (0.10) | V1 | 24/30 | 0/30 | 6/30 Datenlage 6 | Abweichung nachgewiesen, Relevanz offen 6; Abweichung nachgewiesen, innerhalb der Äquivalenzgrenze 24; Drift der Einzelmodulbasis 30 | 24/30 | 29/30 / 0/30 | 30/30 | G4 0.034, G1 0.006 | Klasse p = 1 22, nicht durchgeführt 3, nicht zuordenbar 5 | unauffällig 3, unbestimmt 27 |
| I02-amplitude/L1 | R1 (0.02) | V1 | 1/30 | 0/30 | 29/30 Datenlage 29 | Abweichung nachgewiesen, Relevanz offen 24; Drift der Einzelmodulbasis 28 | 2/30 | 30/30 / 0/30 | 30/30 | G1 0.158, G4 0.036 | Klasse p = 2 1, keine Abweichung an den Punkten I nachgewiesen 3, nicht durchgeführt 21, nicht zuordenbar 5 | unauffällig 12, unbestimmt 18 |
| I02-frequenz/L1 | R1 (0.02) | V1 | 2/30 | 0/30 | 28/30 Datenlage 28 | Abweichung nachgewiesen, Relevanz offen 25; Abweichung nachgewiesen, innerhalb der Äquivalenzgrenze 2; Drift der Einzelmodulbasis 29 | 10/30 | 29/30 / 0/30 | 30/30 | G1 0.112, G4 0.034 | Klasse p = 2 1, keine Abweichung an den Punkten I nachgewiesen 10, nicht durchgeführt 10, nicht zuordenbar 9 | unauffällig 4, unbestimmt 26 |
| I04-drift/L1 | R0 (0.00) | V1 | 20/30 | 0/30 | 10/30 Datenlage 10 | Drift der Einzelmodulbasis 15 | 20/30 | 29/30 / 0/30 | 30/30 | G4 0.038, G1 0.006 | keine Abweichung an den Punkten I nachgewiesen 24, nicht durchgeführt 6 | unauffällig 2, unbestimmt 28 |
| I05-misch/L1 | R1 (0.12) | V1 | 0/30 | 0/30 | 30/30 Datenlage 30 | Abweichung nachgewiesen, Relevanz offen 30; Drift der Einzelmodulbasis 22 | 6/30 | 29/30 / 0/30 | 30/30 | G1 0.150, G4 0.040 | Klasse p = 1 6, nicht durchgeführt 19, nicht zuordenbar 5 | unauffällig 6, unbestimmt 24 |
| S01a-liftoff/L1 | R0 (0.00) | V1 | 0/30 | 0/30 | 30/30 Datenlage 30 | — | 0/30 | 0/30 / 0/30 | 0/30 | G6 0.217, G4 0.059 | — | — |
| A07-hertz50/L1 | R1 (0.50) | Testvorgabe | 8/30 | 0/30 | 22/30 Datenlage 22 | Abweichung nachgewiesen, Relevanz offen 22; Abweichung nachgewiesen, innerhalb der Äquivalenzgrenze 8; Drift der Einzelmodulbasis 30 | 9/30 | 24/30 / 0/30 | 0/30 | G4 0.109, G1 0.007 | — | nicht auswertbar 30 |
| C03-GF1/L1 | R0 (0.00) | Testvorgabe | 24/30 | 0/30 | 6/30 Datenlage 6 | Drift der Einzelmodulbasis 1 | 24/30 | 29/30 / 0/30 | 30/30 | G4 0.037, G1 0.007 | — | unauffällig 3, unbestimmt 27 |
| C03-GF5/L1 | R0 (0.00) | Testvorgabe | 26/30 | 0/30 | 4/30 Datenlage 4 | — | 26/30 | 27/30 / 0/30 | 30/30 | G4 0.041, G1 0.006 | — | unauffällig 2, unbestimmt 28 |
| C04-steif/L1 | R0 (0.00) | Testvorgabe | 27/30 | 0/30 | 3/30 Datenlage 3 | — | 28/30 | 29/30 / 0/30 | 30/30 | G4 0.039, G1 0.008 | — | unauffällig 2, unbestimmt 28 |
| E04-kette/L1 | R0 (0.00) | Testvorgabe | 22/30 | 0/30 | 8/30 Datenlage 8 | — | 22/30 | 28/30 / 0/30 | 30/30 | G4 0.044, G1 0.006 | — | auffällig 30 |
| N01-A4/L0 | R0 (0.00) | Testvorgabe | 37/40 | 0/40 | 3/40 Datenlage 3 | — | 37/40 | 0/40 / 0/40 | 40/40 | G4 0.022, G1 0.008 | — | unauffällig 40 |
| N01-A4/L2 | R0 (0.00) | Testvorgabe | 38/40 | 0/40 | 2/40 Datenlage 2 | — | 38/40 | 0/40 / 0/40 | 40/40 | G4 0.021, G1 0.006 | — | unbestimmt 40 |
| N01-A4/L4 | R0 (0.00) | Testvorgabe | 40/40 | 0/40 | 0/40  | Drift der Einzelmodulbasis 1 | 0/40 | 0/40 / 0/40 | 40/40 | G4 0.013, G1 0.005 | — | auffällig 3, unbestimmt 37 |

Lesart der Szenariopunkte (Punktschätzer mit MC-Fehler, keine Abnahme):

- **Exakte Superposition und LTI** (N03, N04, E04, E07, C04, H01, S-Pfade): H1 nie falsifiziert; die Bestätigung fehlt
  nur, wo Punkte durch G4 unter n_min fallen („Datenlage“, bis 10 von 30 bei V1/I04). N₃ bindet unter Fassung B ohne
  Bestätigungsverlust auf L1. Der Messketteneinfluss E04 erhält die Superposition (0/30 falsifiziert); E3 meldet ihn als
  „auffällig“ (30/30). Drift der Einzelmodulbasis (E07) und Verstärkungsdrift: bestätigt mit Zusatz „Drift“ in 40/40.
- **Grenzen** (A04, N05): unter Δ_rel (A04-R1) bestätigt 39/40 mit Zusatz „Abweichung nachgewiesen, innerhalb der
  Äquivalenzgrenze“; genau an Δ_q (A04-R2, N05-F/N2/N3) nie bestätigt (0/40, Graubereich); bei 1,5·Δ_rel und 2,5·Δ_rel
  falsifiziert 40/40 (A04-R3 ist nach Plan nur zu berichten; bei L1 ist c·u klein gegen 0,5·Δ_rel).
- **Phasenversatz und Kopplung an V1** (A06, H03, I01): H1 nie falsifiziert; E3 „auffällig“ 30/30 bei A06 und H03.
  H03 verschiebt die Spitze um 0,5°; mit δ_H2 = 1° (Testvariante) ist das innerhalb der Äquivalenzgrenze, H2 bestätigt
  25/30. Zuordnung bei 1 % Kopplung: Klasse p = 1 in 20/30 (zweite Amplitude) bzw. 22/30 (zweite Frequenz).
- **Quadratische Kette** (I02, I05): G1 macht 11–16 % der Läufe ungültig (Befund 8), H1 ist fast immer
  „Datenlage“; Zuordnung p = 2 nur 1/30, meist „nicht durchgeführt“ (Punkte von I nicht auswertbar).
- **H3** (Testvorgabe für c): richtige Eingänge bestätigt (C04 29/30, mit Kennzeichnung „keine Harmonische k ≤ 3 prüft
  den Kontakt“); Kettenfehler 1 % und 5 % ebenfalls bestätigt (29/30, 27/30), meist mit „Abweichung nachgewiesen,
  innerhalb der Äquivalenzgrenze“; ein Fehler über 10 % ist nicht im Katalog (Befund 5).
- **Hertz-Kontakt** (A07, ereignisgenauer Löser, Testvorgabe): Klasse R1 (0,50·Δ_rel); H1 nie falsifiziert, aber 22/30
  „Datenlage“ (G4 11 % der Läufe); H4 falsifiziert 30/30 (für H4 berechnet der Generator keine Wahrheit); E3 nicht
  auswertbar (T(kω) singulär). In der Prüfstandsdatei steht diese Zählung noch unter dem Schlüssel „E3: None“; die
  Zählbezeichnung ist seit Etappe 5 (Teil 2) korrigiert (Befund 7).
- **Regelpfade**: Kontrolllauf mit Liftoff (S02) → ŷ¹ ungültig, H1/H2 „Datenlage“ 40/40; fehlende Schnittpunkte
  (H-fehlend) → „Datenlage“ 40/40; Einzelzell-Liftoff (S01a) → G6 aus dem Zellkanal in 22 % der Läufe, alle Ausgänge
  „Datenlage“; Sättigung und Indexfehler machen nur den betroffenen Lauf ungültig.
- **Präzisionsreihe** (N01-A4, Testvorgabe, je 40): P(H1 bestätigt) 37/40 (L0), 193/200 (L1, kalibriert), 38/40 (L2),
  40/40 (L4); die Verluste sind „Datenlage“ (G4), nicht Präzision oder Graubereich. H2 ist auf L4 nie bestätigt
  (Präzision 27, Graubereich 13), die gemeinsame Bedingung fällt dort aus.

**Gegenproben.**

- **Ebenen Z ↔ H** (K19). Rauschfrei, 13 Läufe aller Laufarten: Harmonische ≤ 1,4·10⁻⁵ N, Mittel ≤ 3·10⁻⁷ N, Zeiger
  ≤ 2,5·10⁻³, Rohminima ≤ 3,8·10⁻⁷ N (physikalisch-numerisch gleich). Mit Rauschen, je 4 Kampagnen N01-A4 auf Ebene Z
  (Dateikette mit Stufe 1) und Ebene H mit getrennten Zufallsströmen: u_c-Mediane aller sieben Größen innerhalb 2,5 %
  (Vorschlag K19: 5 %), H1, H1Z, H2 und H4 auf beiden Ebenen 4/4 bestätigt (statistisch, nur probeweise).
- **Reproduzierbarkeit.** Vier Kampagnen seriell und mit vier Prozessen bitgleich, andere Seeds verschieden; Dateikette
  und Kette im Speicher gleich (Test); der normative Lauf über `kette` wiederholt den früheren Lauf im Speicher exakt
  (max|z⁰| = 2,6914200635266576). Toleranz: bitgleich auf derselben Maschine und Bibliotheksversion; zwischen Umgebungen
  gelten die Toleranzen von Plan 2.6 e, der Prüfsatz rundet vor dem Hashen auf 12 Stellen.
- **Wahrheitstrennung.** Dateikette A04-R4: Wahrheit geändert (Klasse und Felder) und danach entfernt → das Ergebnis von
  AP-12 bleibt gleich (Prüfsumme ohne Laufzeit und Codestand); eine Wahrheitsdatei als Teil-B-Eingang wird abgewiesen.
- **H1 gegen die Referenz** (N01-A4 L2, A04-R2 und A04-R4 L1, dieselben Indizes): alle Größen innerhalb der Toleranzen;
  größte Abweichungen r 1,7·10⁻¹⁵ N, u 8·10⁻¹⁷ N, z 4·10⁻¹¹, ν 3·10⁻¹²; Ausgang, TOST, Relevanz, Zusätze gleich.
- **Zeltfit** (4000 Fits gegen das Vollraster): 3997 gleich, 3 Gleichstände (reines Rauschen), 0 abweichend; Kandidat
  9,5 s, Vollraster 461 s.
- **S₃** (K16): Bilder bei identischen Modulen gleich (|N_k| und γ₁ 8·10⁻¹⁶, Phasenregel 3·10⁻¹³°; F_min − ⟨N⟩
  1,2·10⁻⁵ N innerhalb der Rasterschranke, Befund 2); bei 1 % Massenungleichheit weicht der Bildvergleich um 0,023 N ab,
  die Superpositionsvorhersage um 7·10⁻¹⁶ N.
- **Planungshaken** (K12): Pilotskript an N01-A4 mit Haken der Planung, Kandidaten n_min ∈ {18, 24}, je 4 + 4 Kampagnen,
  κ = 1,091 (obere 80-%-Grenze). Die starre Auflage hat kein f₁ im Band, die Suche beginnt bei k_b = 30; dort und bei
  k = 29 bleibt P(H1 und H2 bestätigt) ≤ 0,25, weil G4 bei 30 Harmonischen mehr Punkte unter n_min drückt; danach greift
  die Entwicklungsgrenze von zwei Aufrufen, und die Suche endet regulär mit „kein zulässiger Arbeitspunkt unter diesen
  Annahmen“. Geprüft ist die Mechanik, nicht eine Planung für Teil B.
- **Prüfsatz.** Neuberechnung von Katalog-, Profil-, Seed- und Testdaten-Hashes gleich dem eingecheckten Prüfsatz.

### 4.5 Kriterienmatrix

Aus dem Prüfstand auf `7a259ef` erzeugt (nicht neu erzeugt; betroffen waren K12 durch Korrektur A, K19 durch
Korrektur B und die E3-Zeile durch Korrektur E, Abschnitt 1a; diese sind am 17.10.2026 gezielt neu gerechnet, siehe
[Neulaufbericht](ap13_neulaeufe_2026-10-17/bericht.md) und Vermerk der Matrix): [`ap11_ap12_ap13_kriterien.md`](ap11_ap12_ap13_kriterien.md). Zählung: 1 geprüft
(K16, deterministisch), 16 nur probeweise gerechnet, 1 fehlt (K17), 5 fachlich offen (K08 entfallen, K09 Lesart
offen, K20 Einfrieren nicht Gegenstand, E3 und Zuordnung mit offenen Schwellen bzw. Kriterium), 1 in diesem Modell
nicht prüfbar (K21: kein Hertz-Punkt ≥ 2·Δ_rel im Katalog). Es gibt keine Gesamtampel. Die Punktschätzer liegen bei
K01–K05, K07, H1Z innerhalb der Sollwerte; K11 ist mit dem Katalog nicht prüfbar formuliert (Befund 5), K13 ist mit
200 Kampagnen nicht auflösbar, K18 bleibt mit 20–22 von 30 unter 0,8 (Kopplung 1 % statt 0,1 %), die
E3-Bedingung „unauffällig ≥ 0,8“ wird auf L1 verfehlt (14/200).

## 5 Laufzeiten

| Vorgang | Umfang | Laufzeit (4 Kerne) |
|---|---|---|
| Testsuite (Endstand nach den Korrekturen) | 328 bestanden, 8 übersprungen | 382 s |
| eine Kampagne Ebene H, Kette im Speicher | N01-A4, L1, n = 24; B = 200, ε_ctrl 300, H3-MC 1000 | 3,9 s (Generator 0,2; AP-11-Kalibrierung 1,7; Pilot und Teil B 0,7; Stufe 2 1,2) |
| dieselbe im Prüfstand | B = 1000, ε_ctrl 1000, H3-MC 1000 | 7,1–7,6 s je Kampagne und Kern (A4), 10–11 s (V1) |
| normative Replikatzahlen, `kette` | N01-A4, L1, n = 20; B = 10 000, H3-MC 10 000, ε_ctrl 10 000 | 78 s (Stufe 2: 72 s) |
| normative Replikatzahlen, Speicherkette | N01-V1G0, L1, n = 20 | 139 s (Stufe 2: 131 s) |
| normative Replikatzahlen mit T-Ziehungen (Korrektur E) | N01-V1G60h, L1, n = 20; B = 10 000 | 68 s (Stufe 2: 65 s) |
| T-Ziehungen von E3 (Korrektur E) | V1-G60h, B = 1000 bzw. 10 000 | 0,12 s bzw. 1,3 s |
| Ebene Z, Einzelschritte | A04-R4, L1, n = 24, 811 Rohläufe (522 MB, danach gelöscht) | Generator 237 s, AP-11 3 s, Stufe 1 34 s, Teil B 2 s, AP-12 3 s |
| Zeltfit-Vergleichssatz | 4000 Fits | Kandidat 9,5–10,5 s, Vollraster 461–544 s (Faktor ≈ 50) |
| Prüfstand | 14 Schritte, rund 2100 Kampagnen (einschließlich der Wiederholung der A4-Prüfsimulation mit gepooltem c) | 91 min (Kalibrierung A4 18 min, Szenarien A4 22 min, Kalibrierung V1 11 min, Szenarien V1 13 min, eigene Systeme 7 min, Präzisionsreihe 4 min, Ebenen 5 min, Zeltfit 8 min, Planung 2 min) |
| große Matrix (nur Schätzung) | 36 Szenarien × 6 Stufen × 1000 Kampagnen, B = 1000 | ≈ 450 Kernstunden ohne die Simulationen von c je Stufe; mit B = 10 000 rund das Zehnfache |
| Kampagne Ebene H ohne Stufe 2 (17.10.2026, Abschnitt 1b) | A4/V1, L1, n = 24, ε_ctrl 1000; statisch bzw. mit Ablauf | 2,0 s bzw. 2,6 s je Kampagne und Kern |
| dieselbe mit Stufe 2 | B = 1000, H3-MC 1000 | 5,1 s (statisch), 5,6 s (Ablauf) |
| Ebene Z/Stufe 1 mit Ablauf und Stufe 2 | N01-A4, A04-R4, L1, n = 24; rund 850 Rohläufe je Kampagne (danach gelöscht) | 234 s je Kampagne und Kern |
| begrenzte Rechnung k-Konsistenz/Ablauf | 105 Kampagnenausführungen, davon 7 mit Stufe 2 (6 in der Rechnung, 1 im Abnahmelauf) | 0,20 Kernstunden, Wandzeit rund 10 min |
| Korrekturrunde vom 18.10.2026 (Abschnitt 1c) | 39 Kampagnenausführungen, davon 4 mit Stufe 2 | 0,20 Kernstunden, Wandzeit 10 min 51 s (Rechner rund 35 % langsamer als am 17.10.) |

Die Kurzmessung des Plans (Abschnitt 4.1: 0,30 s je Kampagne bei n = 20, B = 1000, nur Bootstrap von H1) misst einen
kleineren Rechenweg und ist keine Abnahmeschwelle; sie wurde nicht als Vergleich verwendet.

## 6 Befunde

Befunde am Regeltext, am Plan oder an der eigenen Integration; keine Regel wurde geändert. „Rückmeldung“ heißt: zu
klären am Präreg-Text bzw. im Plan (AP-08, AP-13), nicht in der Software.

1. **G4 mit σ_Δ aus den Pilotläufen streut je Konfiguration verschieden** (§9.1 G4, A9.2). Die Fünftel-Differenz von
   F_min − ⟨N⟩ streut an Schnittpunkten mit steiler Zeltflanke stärker als in den Pilotkonfigurationen (Jitter der
   Indexphase wirkt über dF_min/dφ₂). Am V1-G0 (L1, normativer Lauf) sind an S116/S118 15–20 % der Läufe ungültig
   gegenüber 1,7 % in den Piloten; bei der weichen Auflage A07 22 % (S110–S118, S134). Mit n = n_min + r fallen
   einzelne Punkte unter n_min, und H1 wird bei exakter Superposition „nicht entscheidbar (Datenlage)“. Die Reserve
   r = ⌈n_min·p̂/(1 − p̂)⌉ + 2 aus p̂ der Piloten deckt diese punktweisen Ausfälle nicht. Im Prüfstand (n = 24,
   n_min = 18, L1) macht G4 2,3 % (A4), 4,4 % (V1-G0) und 5,0 % (V1-G60h) der Läufe ungültig; H1 ist bei exakter
   Superposition in 7/200, 11/60 und 15/60 Kampagnen „Datenlage“, und P(H1 und H2 bestätigt | exakt) sinkt auf 0,965,
   0,82 und 0,75. Mit 30 Harmonischen (Planungssuche bei A4) wird der Anteil noch größer. Wirkung: K05 und die gemeinsame
   Bestätigungswahrscheinlichkeit sinken, für c zählen weniger Kampagnen; Pfad `gueltigkeit.py` (G4), `pilot.py`
   (Reserve). Rückmeldung (σ_Δ je Konfiguration oder Lage der Piloten, Reserve je Punkt). Diagnose vom 17.10.2026
   ([Diagnosebericht](e3b_g4_diagnose_2026-10-17/bericht.md), Abschnitt 3, 120 Ergänzungskampagnen): Ursache ist der
   Jitter der Indexphasen mal der Flankensteigung; nach A7 zulässige Piloten erreichen die steilen Punkte nicht; eine
   konfigurationsabhängige Standardisierung aus Phase 0 senkt G4 auf 0,9–1,5 %; mit den Wiederholungen nach A9.12
   sind alle 120 Kampagnen vollständig; bei A4 bildet die Pilotanalyse σ_Δ,F mit k = 30 statt k_max = 9.
   Nachtrag vom 17.10.2026 (Abschnitt 1b, [Bericht](ap13_kmax_wiederholungen_2026-10-17/bericht.md)):
   - Die k-Inkonsistenz ist behoben. Bei A4 macht G4 mit Phase-0-Größen bei k = 9 mehr Läufe ungültig (3,3 % → 4,4 %
     in zehn Kampagnen).
   - Die Diagnose von PR #22 setzte Ersatzläufe am ursprünglichen Zeitplatz ein; ihr 120/120 ist kein Nachweis.
   - Mit dem zustandsbehafteten Ablauf ist jede abgeschlossene Kampagne vollständig, dafür halten Kampagnen nach S1
     oder S3 an (Befund 14).
2. **S₃-Gleichheit von F_min nur bis auf die N_θ-Rasterschranke** (Plan K16 gegen A1). F_min ist nach A1 das Minimum
   auf den 2000 Stützstellen; unter Zeitverschiebungen, die kein Vielfaches von 0,18° sind, ist F_min − ⟨N⟩ nur bis
   auf Σ_k k²|N_k|·(2π/N_θ)²/8 invariant (F01: 1,2·10⁻⁵ N bei Schranke 1,5–1,8·10⁻⁵ N). |N_k|, γ₁ und die Phasenregel
   erfüllen 10⁻⁹ N bzw. 10⁻⁶°. Rückmeldung an den Plan (Toleranz von K16 für F_min).
3. **Drift-Zusatz in Fassung (a) erscheint ohne Drift** (§9.3, §12 Driftbehandlung). „|z⁰| > c ohne gleichsinniges
   |z¹| > c oder umgekehrt“ tritt bei jeder echten Abweichung nahe der Nachweisgrenze auf, weil u⁰ (n₀
   Einzelmodulläufe) und u¹ (Kontrollläufe) verschieden sind; beobachtet bei Kopplung (A04) und Hertz-Kontakt (A07).
   Im Prüfstand: bei exakter Superposition (Prüfsimulation N01-A4) 21/200 = 0,105 ± 0,022, unter Δ_rel (A04-R1) 40/40, bei 2,5·Δ_rel (A04-R4) 11/40. Rückmeldung (Fassung des Drift-Zusatzes).
4. **Gewichtung von ρⱼₖ und Mittelkurve verschieden** (§4, A1). ρⱼₖ mittelt nach dem Text über alle Zyklen aller
   gültigen Läufe, die Konfigurationsmittelkurve gewichtet die Läufe gleich. Bei Läufen mit fehlenden Zyklen
   (Indexfehler) weichen beide Gewichte ab; umgesetzt wie im Text, Wirkung klein.
5. **C03 mit 5 % Kettenfehler prüft K11 unter δ_H3 = 10 % nicht** (Plan C03/K11). K11 verlangt einen Mismatch über PB3;
   5 % liegt innerhalb von ±10 %, H3 wird erwartungsgemäß bestätigt, mit Zusatz, wenn die Abweichung nachweisbar ist.
   AP-11 meldet zugleich den Widerspruch zwischen Statik und Brückensimulator. Im Prüfstand: H3 bestätigt bei 1 % 29/30 und bei 5 % 27/30, meist mit „Abweichung nachgewiesen, innerhalb der Äquivalenzgrenze“. Rückmeldung an den Plan
   (Stärke von C03 über der Testgrenze).
6. **Starre Auflage A4: H3 nicht prüfbar** (P0.4). Ohne Mode im Anpassungsband ist die 1-FG-Anpassung nicht
   identifizierbar; H3 ist „nicht entscheidbar (Verfahren)“, und das Pilotskript nimmt das Bandende als untere Schranke
   für f₁ (k_b = 30). Die A4-Szenarien prüfen H1, H2 und H4, nicht H3.
7. **A07 (Hertz-Kontakt, f₁ = 50 Hz) liegt außerhalb der Auslegungsregel (b) und liefert keinen R4-Punkt** (Plan A07,
   K21). Das Pilotskript meldet regulär „kein zulässiger Arbeitspunkt“ (k_b = 2 < 3); für die Stressprüfung entsteht
   Teil B mit den Planwerten, und das Ergebnis nennt den Pilotbefund. Das wahre F_min-Residuum 0,135 N entspricht dem
   Planwert 1,04·Δ bezogen auf Δ(F_min) des starren A4 (0,129 N); nach A9.11 gelten aber Δ_q und Δ_rel aus der
   rauschfreien Vorhersage des Szenarios selbst, und damit liegt A07-hertz50 bei 0,50·Δ_rel (Klasse R1).
   K21 bleibt ohne Hubskalierung (Plan: 0,5–3·Δ_rel) nicht prüfbar. Integration: Teil B und E3 brachen in diesem Fall
   zunächst ab (fehlende Pilotgrößen, singuläres T(kω)); korrigiert, Regressionstest
   `test_stressszenario_ohne_zulaessigen_arbeitspunkt`. Die Ratenzählung führte E3 ohne Bewertung danach unter
   „None“; sie zählt Kontrollen ohne Bewertung jetzt unter ihrem Status (Regressionsprüfung in
   `test_kampagnen_unabhaengig_von_der_prozesszahl`).
8. **Quadratische Kettenkennlinie I02 verletzt H0** (Plan I02, §8.8). β = 2·10⁻³/N verschiebt ⟨N⟩ der
   Kombinationsläufe um β·Var(F) gegenüber den Referenzläufen; G1 macht deshalb einen Teil der Läufe ungültig, und die
   Zuordnung ist häufig „nicht zuordenbar“. Im Prüfstand: G1 macht 15,8 % (zweite Amplitude) bzw. 11,2 % (zweite Frequenz) der Läufe ungültig, H1 ist in 29/30 bzw. 28/30 Kampagnen „nicht entscheidbar (Datenlage)“, die Zuordnung p = 2 gelingt in 1/30. Die Stärke des Plans (≥ 1 mN H1-Wirkung) und G1 stehen hier
   gegeneinander. Rückmeldung an den Plan.
9. **N05-N1 nicht konstruierbar** (Plan N05). Mit einer Kopplung nur der ersten Harmonischen erreicht F_min − ⟨N⟩ die
   Grenze vor Re/Im N₁; ein Szenario mit genau einem Test an Δ_q für N₁ entsteht so nicht. N05-F, N05-N2 und N05-N3
   sind vorhanden.
10. **Intervalltyp „keiner“** (Integration). Erreichte in der Planungssimulation kein Intervalltyp die Überdeckung,
    brach H2 beim Lesen des Niveaus ab; jetzt „nicht entscheidbar (Verfahren)“ mit Grund, Regressionstest
    `test_h2_intervalltyp_keiner_nicht_entscheidbar`.
11. **E3 verfehlt „unauffällig ≥ 0,8“ auf L1** (A9.11, §8.10; Prüfstand vor Korrektur E ohne Unsicherheit von T, am
    17.10.2026 mit Unsicherheit von T neu gerechnet: Zähler unverändert, „unbestimmt“ allein durch E3b,
    [Neulaufbericht](ap13_neulaeufe_2026-10-17/bericht.md); eine Schwellenentscheidung folgt daraus nicht). Mit den Entwicklungsschwellen (0,1°, q_tol = 5,8·10⁻⁴)
    ist E3 bei exakter Superposition in 14/200 Kampagnen „unauffällig“, sonst „unbestimmt“; nach A9.11 würde E3 dann
    nur beschreibend berichtet. Phasenversatz eines Moduls (A06, H03) und der lineare Messketteneinfluss E04 erscheinen
    als „auffällig“ (30/30), die Basisdrift E07 in 36/40. Bei A07 ist E3 nicht auswertbar (T(kω) singulär). Diagnose vom
    17.10.2026 ([Diagnosebericht](e3b_g4_diagnose_2026-10-17/bericht.md), Abschnitt 2): 27/200 scheitern an der reinen
    Unsicherheitsgrenze u(q_Z) > q_tol/1,645, 159/200 am positiven Punktschätzer; ein komplexes Nullresiduum sagt
    P(unauffällig) = 0,07 voraus (beobachtet 14/200), für 0,8 müsste die Streuung 2,2-mal kleiner sein. Am
    Schwellenrand ist die untere Grenze von E3b im selben Modell nicht gültig (0,24 % statt 0,116 % je Prüfung bei
    L1-Präzision). Vorschlag: feste Schwellen mit Rückfall je Prüfgröße und fester Prüfzahl, vorausgesetzt am Rand
    gültige einseitige Grenzen und gemeinsame Fehlerkontrolle über alle E3-Prüfungen; Entscheidung beim Autor.
12. **Überdeckung der H2-Intervalle konservativ** (§8.6, A9.6). Bei exakter Superposition überdeckt das
    Perzentilintervall den Bezugswert in allen Kampagnen (194/194, symmetrisches Zelt 40/40), BCa in 0,94–0,98; die
    Rückfallkette wählt damit stets das Perzentilintervall. Der Bezugswert der Überdeckung ist offen (§12); gewählt ist
    der Wert des Schätzers an den rauschfreien Kurven.
13. **Replikate von H2 und E3** (A9.6, A9.13). Beide nutzen die Zeilen der Bootstrap-Indexmatrizen; eine getrennte
    Reduktion von `h2_replikate` oder `e3_mc` gegenüber `bootstrap_B` wäre irreführend und wird abgewiesen.
14. **S1 und S3 halten Kampagnen bei exakter Superposition an** (§8.8, §9.2; Ablauf vom 17.10.2026). In 30 Kampagnen
    mit Wiederholungsablauf (A4, V1-G0, V1-G60h, je zehn) halten 5 an, ohne dass ein Effekt vorliegt:
    - S1 nach reproduziertem Nullpunktalarm: 2 Kampagnen;
    - S1 nach G1-Verstoß von X′: 2 Kampagnen, beide V1-G0 mit 22 feststehenden G1-Verstößen in zehn Kampagnen; mit
      `ablauf-2` (X′ gegen R₂/R₃, Korrektur vom 18.10.2026) bestätigt, unter `ablauf-3` unverändert;
    - S3: 1 Kampagne, dazu der Regelpfad S06.
    Das liegt innerhalb der Schranken der Präregistrierung (S1 bis etwa 25–28 % je Kampagne). Für die gemeinsame
    Vollständigkeit wiegen die Halte aber mehr als die punktweisen Ausfälle, die der Ablauf beseitigt; ob eine
    Kampagne nach der Ursachenanalyse fortgesetzt würde, simuliert die Software nicht. Wirkung: Die Planung braucht ein
    Ziel der gemeinsamen Vollständigkeit, das Halte einschließt. Rückmeldung (Vollständigkeitsziel, Umgang mit Halten
    in Planung und Kalibrierung).

Kleinere Befunde aus Etappe 1 und 2 sind am Ort dokumentiert: Rasterursprung und Gleichstandstoleranz des Zeltfits,
die A9.6 nicht festlegt (Regeln `h2.rasterursprung`, `h2.gleichstand_toleranz`), Harmonische bis k_voll in den
Zusammenfassungen (`verarbeitung.k_voll`, Schnittstellen Abschnitt 4), Lage der Referenzläufe bei wenigen anderen
Läufen nach P0.7 (`generator/kampagne.py`), Rampe als Amplitudenhülle auf Ebene Z (`generator/ebene_z.py`), halber
Zeitgebertakt als Toleranz am Fensterbeginn (`stufe1.py`) und die quadratische Kennlinie auf dem Ausgang der linearen
Kette (`generator/ebene_h.py`).

## 7 Grenzen und verbleibende Arbeit

- **Keine vollständige Kalibrierung.** Gerechnet sind gezielte Entwicklungsläufe mit 30–200 Kampagnen je Punkt und
  B = 1000; die Matrix mit ≥ 1000 Kampagnen je Szenariopunkt und Präzisionsstufe L0–L5 in beiden Betriebsarten ist
  vorbereitet (`harness matrix`, Auftragsliste), aber nicht gestartet. Kein Kriterium K01–K21 gilt als abgenommen; die
  Kriterienmatrix nennt je Kriterium den Status, ohne Gesamtampel.
- **Planung.** Der Haken der AP-13-Planung ist angebunden und mechanisch geprüft; mit wenigen Kampagnen je Kandidat
  ist er Entwicklungsdiagnostik. Es fehlen ein Generator, der unmittelbar aus gemessenen Pilotkovarianzen speist (für
  Teil B nötig), der automatische Startwert aus der Auslegungsgrenze Δ_q/5,01 bzw. Δ_q/5,21 und die offene zusätzliche
  Power-Bedingung (Regel `planung.power`).
- **Katalog.** Umgesetzt sind die Mindestfälle des Auftrags; aus dem Plan fehlen die Gruppen B (3-FG gegen 1-FG),
  D (Nebenschluss) und G (Vorzeichen-Inversionstest, K17), A01–A03, A05, C01, C02, N02 (als Prüfsimulation umgesetzt),
  N06–N08, E01–E03, E05, E06, E08, E09, H02, H04, H05, I03, I06, S01b, S01c, S03–S05, S07 (A9.8 im Pilotskript) sowie
  die E3-Szenarien mit 0,1° und 0,3° Phasenversatz und die Zuordnungsszenarien mit Hertz-Kontakt und lastabhängiger
  Kopplung. Einzelzell-Liftoff prüft nur den Beginn (lineares 3-FG-Modell); Stoßdynamik einer abhebenden Zelle ist
  nicht modelliert.
- **Ebenen.** Der Abgleich Z ↔ H ist rauschfrei vollständig, mit Rauschen nur an N01-A4 auf L1 mit wenigen Kampagnen
  gerechnet (K19 verlangt L0, L2, L4).
- **Optionen.** H3 Fassung I, H1′/H2′, Paarläufe, Wiederaufnahme nach Eingriff, frühere Signifikanzlogik, übrige
  Sensitivitäten von A9.9, Fenstervarianten von H2 (w = 8°, Spitzenfehlerkriterium) und die Neuberechnung von b̂ und c
  nach dem Datenschluss sind nicht umgesetzt; offene Regeln bleiben im Profil AF-2026-10 offen.
- **Daten.** Nur synthetische Daten; das Format weist Messdaten in dieser Stufe zurück. Das Rohdatenformat legt AP-10
  fest; keine DAQ-Anbindung, keine Echtzeitfunktion (G1–G10, S1–S4 nur offline).
- **Hardware.** Antrieb, Messkette, Wegkanal, Geometrie, Kontakt, Dämpfungsziel und institutionelle Anbindung bleiben
  offen; A4, V1-G0 und V1-G60h sind Rechenannahmen der Kalibrierung, keine beschlossene V1-Topologie.
- **Teil B.** Teil B wird nur synthetisch gefüllt; die Neukalibrierung mit gemessenen Kovarianzen gehört zu AP-21.
- **Ablauf der Phase 1** (Abschnitt 1b). Nur in der Simulation; Lesarten, wo der Regeltext nicht ausdrücklich ist,
  stehen im Kopf von `ablauf.py` und im [Bericht](ap13_kmax_wiederholungen_2026-10-17/bericht.md), Abschnitt 6.
  - Angehaltene Kampagnen werden nicht automatisch fortgesetzt; eine Wiederaufnahme nach mechanischem Eingriff ist
    nicht umgesetzt.
  - Die Dateikette (`dateien.kette_dateien`, Befehl `kette`) kennt nur den statischen Laufplan und bricht mit
    „zustand“ ab; den Ablauf über Ebene Z rechnet `kette.kampagne_ablauf`.
  - Katalogereignisse betreffen die geplanten Läufe, nicht zusätzliche Versuche.
  - Für Einstellung 2 gibt es keine Qualifikationsaussage (G2–G4 und S-Regeln für L′ offen).
  - Werkzeug 8, die Prüfstandsraten, die Planung (K12) und die E3-Zähler sind mit dem neuen Ablauf und der Bindung an
    den Plan neu zu rechnen (Abschätzung im Bericht, nicht gestartet).
