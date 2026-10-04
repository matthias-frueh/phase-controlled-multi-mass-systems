# PCMMS — Präregistrierung v2, Technischer Anhang

**Matthias Früh · ORCID 0009-0005-9984-4207**
Stand: 28. September 2026, überarbeitet 2. Oktober 2026 (A3, A4: Einordnung der Vorzeichenregel; Entwurf 10/2026: Entscheidungsregeln, Identifizierbarkeit und Kontrollen, A0), 3. Oktober 2026 (A0, A4, Z: Verweise auf das Exposé; A0, A1, A2.1, A9.2, A9.7, Tabellen C und F, Z: Auftrieb und Bestimmung von M; A0, A1, A2.6, A8, A9.2, A9.5, A9.6, A9.8, A9.11–A9.13, Tabelle F, Z: offene Festlegungen gekennzeichnet, Klarstellungen; A0, A1, A4, A8, A9.2, A9.3, A9.6–A9.8, A9.11, Tabelle F, Z: Arbeitsfestlegungen des Autors zur Entscheidungslogik von H2 und H3, zum Niveau der H2-Intervalle, zur Laufzahlbedingung und zur Berichtsform) und 4. Oktober 2026 (A0, A1, A4, A8, A9.3, A9.9, A9.11, Tabellen C und F, Z: Arbeitsfestlegungen des Autors zu Äquivalenzgrenze, Signalmaß und Relevanzgrenze von H1, zur Reichweite und zu Werkzeug 8; A0, A1, A2.1, A8, A9.2, A9.3, A9.7, A9.8, A9.11, Tabellen C und F, Z: Bestimmung von M nach Konvention (b), die Festlegungen vom 3. und 4. Oktober 2026 als vorläufige Arbeitsfestlegungen, Werkzeug 2) · gleichrangiger Teil von Teil A, Entwurf — nicht eingefroren, nicht registriert

Dieser Anhang gehört zu `praeregistrierung_v2_entwurf.md` (Hauptdokument, Dateiname vorläufig, §12; Verweise
„§“ beziehen sich darauf) und wird mit ihm eingefroren und registriert. Er enthält den Änderungsvermerk
gegenüber v1 (A0), die vollständigen Definitionen, die Herleitungen, das Beispiel der starren Auflage, die
Fehlalarmraten, die Verfahren im Einzelnen, die Tabellen der Artefakte (C) und Festlegungen (F) sowie den
Zahlennachweis (Z) für beide Dateien. Es gibt keine Messdaten; alle Zahlen sind Simulationsergebnisse des
Repositorys oder daraus abgeleitet.

---

## A0 · Änderungsvermerk v1 → v2

| v1 | v2 | Grund |
|---|---|---|
| Arbeitsfassung, internes Grundlagendokument | zweistufig, extern registriert, an Commit-Hashes gebunden | Vorhersagen hängen von Größen ab, die erst Phase 0 misst |
| §1: Nachweis phasenabhängiger Strukturen | quantitative Fragestellung (§2) | Die Phasenabhängigkeit folgt aus dem Newtonschen Gesetz |
| §2 H0 im Fehlerbudget | H0 je Lauf, ε_ctrl = 3·σ̂_ref oder 3·σ̂_betr (§8.8) | Schwelle war offen |
| §2 H1: Wellenformstatistik hängt von der Phase ab | H1 Superposition, H2 Zeltspitze, H3 Kontaktmodell, H4 Vorzeichen der Schiefe | Das qualitative H1 ist praktisch garantiert |
| §2 H1_fluid | eigene Präregistrierung | anderer Aufbau |
| §3: Schiefe, Liftoff-Anteil, Peak-to-Mean | primär F_min − ⟨N⟩, N₁ … N₃; sekundär γ₁; A beschreibend; λ explorativ | im Kontaktast vorhersagbar; Peak-to-Mean wurde nie berechnet, die Codevariable `peak_ratio` ist A; auf dem Schnitt ist λ = 0 |
| §4: Zielauflösung 0,2–0,5 % | Äquivalenzbedingungen (§8.5), Laufzahl aus Planungssimulation; Lauf bleibt Einheit | Die Zielauflösung galt einer Mittelwertverschiebung |
| §5: Kontrollen ohne Phasensteuerung, mit starrer Kopplung, mit Dummy-Masse | Phase 0 mit Einzelmodulläufen, D1 (passiver Körper anstelle der Dummy-Masse) und D2; Kontrollläufe in randomisierten Blöcken; Blindung; die Kontrollen „ohne Phasensteuerung“ und „starre Kopplung“ entfallen | Für die Wellenform gibt es keinen Zustand ohne Effekt |
| §6: Artefakte, Verwerfungsregel | Regel beibehalten, Kontrolle je Quelle, neue Quellen (§7, Tabelle C) | geändertes Messprinzip |
| §7: Block-Averaging, Welch-Test Referenz gegen Modulation, Streuungsgate | phasensynchrone Mittelung je Lauf (Auswertung je Block nur als Sensitivitätsanalyse, A9.9); Superpositionsvorhersage, standardisierte Residuen, Bootstrap, Äquivalenzbedingung; Welch-Test nur für H0 | Einheit ist der Lauf; Referenz und Modulation haben dasselbe Mittel |
| §8: externe Validierung | bleibt Pflicht, konkretisiert (§10.1) | — |
| §9: Stop / Modify / Scale | Abbruchregeln (§9.2), Ergebnislogik (§9.4) mit „nicht entscheidbar“ | Das Stop-Kriterium konnte nicht greifen |
| §10: Abgrenzung | inhaltlich unverändert (§11) | — |

Neu sind Phase 0, die Driftkontrolle über ŷ¹, Profilphasen, Anlaufprotokoll, Einzelzellkräfte,
externe Registrierung, Datenmanagement und Abweichungsprotokoll. Die Bezeichnung H1 ist neu belegt.

**Entwurf 10/2026: Entscheidungsregeln.** Vor dem Einfrieren geändert, begründet mit Simulationen unter
angenommenen Rauschmodellen, nicht mit Messdaten. H1 wird als Äquivalenztest bestätigt (je 147 Intervalle
r ± t(0,95; ν)·u_c gegen ŷ⁰ und ŷ¹ in ±Δ_q, Intersection-Union-Prinzip, ohne „kein |z| > c“) und nur bei
relevanter Abweichung falsifiziert (|r| − c·u_c > Δ_rel); c ist das simulierte 95-%-Quantil von max|z⁰|, die
Ersatzregel entfällt (§3, §8.4, §8.5, §9.3, §9.4). Grund: Die bisherige Bestätigung wurde mit wachsender
Präzision unwahrscheinlicher, sobald eine kleine, irrelevante Abweichung nachweisbar war (A8). Die
Auslegungsgrenze von PB1 steht je Größe dabei, bandbegrenzt und für beide Vorhersagen gerechnet (A4, A8). Das
H2-Fitfenster hängt nicht mehr von u_c,erw ab, weil es bei hoher Präzision sonst keines gab; die Laufzahl ist
zusätzlich an das SNR gebunden, und der Intervalltyp von H2 folgt der simulierten Überdeckung mit einem
Rückfall (§5.4, §8.6, A9.6). F_min stammt nur aus der bandbegrenzten Mittelkurve; der Rauschbias wird für ŷ⁰
und ŷ¹ getrennt korrigiert und als Unsicherheit geführt, statt über f zu entscheiden (§5.4, A9.5).
Nichtlineare und zeitveränderliche Einflüsse werden auf die Nachweisgrenze bezogen (§5.2, G7). Die Reichweite
von H3 im steifen Aufbau ist benannt (§8.7). Offen sind die Regel für Δ_rel, D für Re und Im N_k, das
H2-Fenster, die Fassung von H3 und die Entscheidungslogik von H2 und H3 (§12).

**Entwurf 10/2026: Identifizierbarkeit und Kontrollen.** Vor dem Einfrieren ergänzt, begründet mit
Rechnungen am Modell und Abschätzungen mit angenommenen Maßen, nicht mit Messdaten. Bisher ordnete keine
registrierte Regel eine H1-Abweichung einer Ursache zu (§9.4), und mehrere Quellen fehlten in Tabelle C.
Neu sind: H0 mit ⟨N⟩ als statischer Last (§3); Tabelle C mit Luft am Körper, Auftrieb, Elektrostatik,
Kabelkräften, Aktorkopplung, lastabhängigem Phasenversatz und gemeinsamer Versorgung, je mit Größenordnung,
Signatur und Kontrolle; Identifizierbarkeitsläufe bei einer zweiten Einstellung an mindestens drei
Schnittpunkten mit eigener Vorhersage, D2 in Kombinationskonfiguration und P0.4 unter Betriebslast mit
Klirrkriterium (§5.2, §5.5, §6); eine registrierte Zuordnung nach der Skalierung mit der Amplitude (§8.10,
A2.6); die Superposition je Zelle als sekundäre Familie H1Z statt als Sensitivitätsanalyse (§3, §8.4, §8.5);
E3 als registrierte Kontrolle mit festen Schwellen statt explorativ (§3, §8.10, A2.7), mit Rückfall auf eine
nur beschreibende Auswertung, wenn die Präzision der Zellkanäle nicht reicht (A9.11); die Regel „kein frei
angepasster Residualterm“ (§8.1). Die Gegenkomponente (E3b) wird als Differenz gegen ihre Vorhersage aus der
zellweisen Superposition geprüft, nicht absolut: Eine feste Schwelle für |R₋₁|/|R₊₁| würde zulässige konstante
Modulunterschiede und Kalibrierfehler der Zellen bewerten; E3b ist deshalb von H1Z nicht unabhängig (§8.10).
Die Betriebslastprüfung von P0.4 läuft nach der Wahl von f, mit der Last je Zelle (§5.2). Kontakt- und
Messkettennichtlinearität sind ausdrücklich nicht trennbar.
Die Kampagne wird länger (§5.3 c, §6, A9.12), die Bonferroni-Schranke über die Familien steigt durch H1Z auf
0,25. Offen sind die Bestimmung von M (P0.2), Einstellung 2 und s, die Punkte I, Paarläufe, die Schwelle des
Klirrkriteriums, die
Grenzen von H1Z, die Schwellen von E3 und alle Teile, die vom Antrieb, vom Hardwarestand des Linearaktors,
von der Lage von Zellen und Modulen und von der Messkette abhängen (§12).

**Entwurf 10/2026: Auftrieb und Bestimmung von M (Nachtrag 3. Oktober 2026).** ⟨N⟩ heißt statische Last
statt scheinbares Gewicht. Der frühere Ausdruck M·g − ρ_L·g·V mit dem Körpervolumen V zog bei M aus der
statischen Zelllast den Auftrieb doppelt ab (0,021–0,047 N) und ließ bei M aus der Bauteilwägung das Gewicht der
Innenluft weg. Kein Hypothesentest war betroffen, weil H0 Δ⟨N⟩ prüft. Beide zulässigen Konventionen für M
stehen getrennt (§3, §4, P0.2, A1, A2.1, A9.2, Tabelle C, Tabelle F, Z), mit den Bezeichnungen aus
`code/auslegung.py`; die Wahl ist offen (§12). Kurzfassung, §2, §7 und §11 verwenden den Begriff statische Last.
Zugleich ordnet §12 die offenen Festlegungen nach dem Zeitpunkt,
zu dem sie getroffen werden können (unabhängig von der Hardware, abhängig vom Aufbau, erst nach Phase 0), und
nennt weitere offene Punkte mit Optionen, ohne eine zu wählen: Äquivalenzgrenze, Schätzer und Intervall von
H2, Driftbehandlung, Wiederaufnahme nach einem Eingriff, Wortlaut der Zusätze, Rückfall für H1, Nachweis und
Folge der Phase-0-Schwellen, Zuordnung, Läufe bei Einstellung 2, D2_K, Messzeit, Betriebslastprüfung, Art von
Einstellung 2 mit zweitem Nockensatz und Linearitätslauf, Rauschmodelle und kritischer Wert von H1,
Vollständigkeit bei H2, Mittelpunkt des H2-Fitfensters, Zielfunktion der Laufzahlplanung, Nullkontroll-Sammeltest
sowie das Gehäuse des Körpers (Hardware). Ergänzt sind weitere Optionen bei Einstellung 2 und s, Paarläufen,
Klirrschwelle, Grenzen von H1Z und E3 und bei der Entscheidungslogik von H2 und H3 sowie Angaben zu den Punkten I
und zu Fassung I von H3; die bisherigen Vorschläge sind unverändert. Die offenen Punkte sind zusätzlich an ihren
Regelstellen und in Tabelle F mit „offen, §12“ gekennzeichnet; vollständig führt sie §12. Berichtigt ist die
zirkuläre Mittelpunktregel des
H2-Fitfensters (der Schnittpunkt nächst φ̂₂*, das erst der Fit in W ergibt); ihre Fassung ist offen (§8.6, A9.6,
§12). Klargestellt sind die Bedeutung der Ausgänge (§9.3, §9.4), die Skalierung eines Kontaktresiduums bei
zweiter Frequenz über den Faktor 1 − H(kω) (§5.5, §8.10, A2.6), die träge Masse in H(ω) (§8.7, A2.1), der
Linearitätslauf mit einer Nocke und der Faktor der Justiergewichte bei Kalibrierung in Masseeinheiten (A9.2),
planmäßige Umschaltungen eines zweiten Nockensatzes (§5.5) und „reproduziert“ statt „bestätigt“ bei Alarmen
und Kontrollläufen (§9.2, A8, A9.12, Tabelle F, Z).

**Entwurf 10/2026: Arbeitsfestlegungen zu H2, H3, Laufzahl und Berichtsform (3. Oktober 2026).** Vorläufige
Arbeitsfestlegung des Autors (Status: Eintrag vom 4. Oktober 2026 zur Bestimmung von M), umgesetzt im Entwurf. (1)
H2 und H3 werden wie H1 nach Äquivalenzlogik entschieden (§3, §8.5, §8.6, §8.7, §9.3, §9.4): bestätigt, wenn jedes
Intervall in der Äquivalenzgrenze liegt (H2: [a⁰, b⁰] und [a¹, b¹] in ±δ_H2; H3:
r ± t(0,95; ν_eff)·u_c in ±δ_H3·|N̂_k⁽ʲ⁾|, ohne „kein |z| > c“), falsifiziert nur bei nachgewiesener Abweichung
über der Relevanzgrenze (H2:
beide Intervalle auf derselben Seite außerhalb von ±δ_H2; H3: an einem Test |r| − c·u_c über der Relevanzgrenze von
H3), sonst nicht entscheidbar. „0 ∈ Intervall und Halbbreite ≤ 1°“ entfällt als Bestätigungsregel. Grund: Die
Bestätigung darf mit wachsender Präzision nicht unwahrscheinlicher werden (A8). (2) Die H2-Intervalle bleiben auf
dem Niveau 95 % (§8.6, A9.6; Typ und Rückfallkette weiter offen, §12); die Option 90 % entfällt, weil die
Überdeckungsschwelle 0,936 und die Verbreiterungsstufen für 95 % gebaut sind und der Perzentil-Bootstrap bei kleinem
n eher zu eng ist. (3) Die Laufzahlplanung von §5.4 strebt gemeinsam P(H1 und H2 bestätigt | exakt) ≥ 0,8 an,
statt P(H1 bestätigt | exakt) ≥ 0,8 und eine erwartete H2-Halbbreite ≤ 1° zu verlangen; die Einhaltung prüft
Werkzeug 8 (A9.11). Zwei getrennte Bedingungen von je 0,8 ergäben bei Unabhängigkeit gemeinsam nur 0,8² = 0,64. Die
SNR-Faustregel von §5.4 bleibt als notwendige Bedingung, an δ_H2 gekoppelt: n_min ≥ (3·1°/(SNR·δ_H2))², bei der
Testvariante δ_H2 = 1° wie bisher n_min ≥ (3/SNR)² (A9.2). (4) Berichtsform (§8.8, §9.3, §9.4, A8, A9.8): Zusatz je
Ausgang (H1, H1Z, H2, H3) statt „Abweichung nachgewiesen, kleiner als Δ_rel“, „nicht entscheidbar“ stets mit Grund,
eine Wortregel für den Nullkontroll-Sammeltest, eine Zeile für gemischte Primärausgänge, „widersprechen“ nur
zwischen „bestätigt“ und „falsifiziert“ derselben Hypothese; die Oberbegriffe bleiben. Grund: Fehllesungen
vermeiden; an der Auslegungsgrenze erhielte auch eine wahre Abweichung von 1,25·Δ_rel den alten Zusatz „kleiner als
Δ_rel“ mit P = 0,986 (ein Test gegen eine Vorhersage, u_c = Δ_q/5,012, Δ_rel = Δ_q, c = c_B = 3,583, ν → ∞; Z).
Offen bleiben δ_H2 (Testvariante ±1°), δ_H3 (Testvariante ±10 %), die Relevanzgrenze von H3 und die Lesart von „H2
auch bei hoher Präzision entscheidbar“ (A9.11); Begründung und Prüfung mit Werkzeug 8 vor dem Einfrieren (§12). Bei
der Testvariante δ_H3 = 10 % wird eine Bestätigung von H3 nicht als Bestätigung des Kontaktgesetzes oder des
Kontaktmodells bezeichnet; im steifen Aufbau prüft H3 dann Masse, Profil und Kalibrierung (A4, §8.7). Soweit die
Einträge oben die hier festgelegten Punkte als offen führen, gilt dieser Eintrag.

**Entwurf 10/2026: Arbeitsfestlegungen zu H1 (4. Oktober 2026).** Vorläufige Arbeitsfestlegung des Autors (Status:
nächster Eintrag), umgesetzt im Entwurf. (1) Äquivalenzgrenze (§3, §4, §8.5, A1, A9.3, Tabelle F): Δ_q = 0,25·D_q je
Größe q, D_q als Punktwert aus ŷ⁰ [Teil B]. Grund: Eine Bestätigung muss die vorhergesagte Struktur auf ein Viertel
auflösen; ein kleinerer Faktor erhöhte die nötige Laufzahl etwa mit dem Kehrwert seines Quadrats (0,1 statt 0,25:
etwa 6-fach, Z). Der Punktwert ist dieselbe Größe, die die Auswertung verwendet; seinen Schätzfehler erfasst
Werkzeug 8, und die Prüfung auch gegen ŷ¹ begrenzt ihn. Nicht gewählt: die untere Vertrauensgrenze von D_q und D_q
aus dem Auslegungswerkzeug (dessen Vorhersage steht in Teil B nur zum Vergleich, A9.3). Als Sensitivitätsanalyse
wird H1 zusätzlich mit Δ_q = 0,1·D_q und ebenso Δ_rel,q = Δ_q ausgewertet; sie ändert keinen Ausgang (§8.9, A9.9).
(2) Signalmaß für Re und Im N_k (§8.5, A1, A8, Tabelle F): Fassung B, D = max_{i,i′} |N̂_k,i − N̂_k,i′|, der
Durchmesser der vorhergesagten Zeigermenge über den Schnitt, analog zur Spannweite bei F_min; Fassung A,
D = max_i |N̂_k,i|, wird als Sensitivitätsanalyse berichtet (A9.9). Grund: gleiche Bedeutung für alle 147 Größen;
Fassung A behandelt die Harmonischen ungleich (Beispiel A4: Toleranz 12,7 / 13,3 / 43,3 % der Änderung entlang des
Schnitts für N₁, N₂, N₃, Z) und lässt unter Lauf-zu-Lauf-Streuung je Modul Re und Im N₁ die Laufzahl stärker
treiben (etwa halbe Grenze). Preis:
Fassung B ist bei N₃ strenger (Beispiel A4: Δ_q = 0,0799 statt 0,1383 N). Sie bleibt auch, wenn die Grenze von N₃
bindet; dann werden Präzision und Laufzahl in der Planungssimulation geprüft (§5.4, A9.11), ein Wechsel zu Fassung A
ist nicht vorgesehen. Werkzeug 2 wird auf Fassung B nachgezogen (§12). (3) Relevanzgrenze (§3, §4, §8.5, §9.3, §9.4,
A8, Tabelle F): Δ_rel,q = Δ_q. Grund: kleinster Wert, mit dem sich „äquivalent“ und „relevant abweichend“
ausschließen, ohne weiteren freien Faktor; Δ_rel ändert die Bestätigung nicht. Nicht gewählt: κ·Δ_q mit κ > 1 und
max(Δ_q; Δ_phys,q). Einwand: Δ_q ist ein Auflösungs-, kein physikalisches Relevanzkriterium. Eine Falsifikation sagt
deshalb nur, dass die Superposition über die registrierte Toleranz hinaus verletzt ist. Ob Apparatur oder Physik,
klären Zuordnung und E3, soweit sie es können (§8.10); im steifen Aufbau überwiegt die Apparatur (§2).
(4) Reichweite (Kurzfassung, §2, §3, §9.3, §9.4): Eine Bestätigung von H1 ist eine grobe Modellübereinstimmung
innerhalb registrierter Toleranzen. Jede der 147 Abweichungen liegt dann nachweislich innerhalb eines Viertels der
vorhergesagten Struktur über den Schnitt; kleinere Verletzungen der Superposition, etwa schwache Kopplungen, bleiben
zulässig und erscheinen nur als Zusatz. Im Beispiel A4 erreicht das größte Residuum von F_min − ⟨N⟩ die Grenze erst
bei einer gemeinsamen Kopplung aller Module von etwa 10,6 % (A4, Z). Diese und alle anderen Kopplungszahlen sind
Rechenbeispiele (A4, Tabelle C) bzw. Simulationsannahmen (A9.11), keine Vorhersagen für die reale Apparatur V1.
(5) Werkzeug 8 (§12, A9.11) schätzt in jeder simulierten Kampagne D_q, Δ_q und Δ_rel,q wie die Auswertung als
Punktwert aus dem simulierten ŷ⁰, in Fassung B und in den Sensitivitätsvarianten, und prüft die Kriterien von A9.11
für das vollständige Verfahren in Fassung B mit Faktor 0,25 einschließlich dieser Schätzung (die Varianten werden nur
berichtet); Bezugswert der wahren Abweichung sind die Grenzen aus
der rauschfreien Vorhersage. Grund: Der Schätzfehler von D_q gehört zum Verfahren; ohne ihn gälten die Fehlerraten nur
für bekannte Grenzen. Offen bleiben Rückfall, Präzisionsstufen, Rauschmodelle, kritischer Wert und Laufzahl von H1
sowie die Grenzen von H1Z; deren Vorschläge Δ_q/3 und Δ_rel,q/3 fallen mit Δ_rel,q = Δ_q zusammen (§12). Soweit die
Einträge oben die hier festgelegten Punkte als offen führen, gilt dieser Eintrag.

**Entwurf 10/2026: Bestimmung von M und Status der Arbeitsfestlegungen (4. Oktober 2026).** (1) Bestimmung von M
(§3 H0, §4, P0.2, §8.7, §12, A1, A2.1, A9.2, A9.3, A9.7, Tabellen C und F): Konvention (b), M = Σ_c F_c,stat/g aus
der statischen Zelllast bei P0.2; die Zellen sind in N kalibriert, g ist örtlich bestimmt und gilt einheitlich für
Kalibrierung, M und alle Kräfte. Die statische Last ist das Gewicht M·g im Zustand bei P0.2; Auftrieb, Innenluft und
gleichbleibende äußere Kräfte sind enthalten, ein zusätzlicher Auftriebsabzug entfällt. Gewicht M·g und träge Masse
M + m_L (m_L = ρ_L·V_außen + m_hyd) bleiben getrennt. Eine Gesamtwägung des geschlossenen Körpers dient als
beschreibende Kontrolle, wenn eine geeignete Waage verfügbar ist; sonst nennt Teil B den Verzicht mit Grund. Grund:
M·g ist die statische Last selbst, mit denselben Zellen und derselben Kalibrierung wie ⟨N⟩ und ohne Annahme über
Volumina und Dichten; kein Test benutzt den Absolutwert M·g, und die H3-Vorhersage hängt nicht an M, weil P0.4 K und
C mit derselben trägen Masse anpasst (§8.7). Statische Nebenkräfte und der Luftzustand bei P0.2 gehen in M ein.
Nicht gewählt: (a) Summe der wahren Bauteilmassen; ihre Rechnungen bleiben als Begründung in Z. (2) Status: Die
Festlegungen vom 3. Oktober 2026 (Entscheidungslogik von H2 und H3, Niveau der H2-Intervalle, Laufzahlbedingung,
Berichtsform), vom 4. Oktober 2026 zu H1 (Äquivalenzgrenze, Signalmaß, Relevanzgrenze, Reichweite, Werkzeug 8) und
(1) sind vorläufige Arbeitsfestlegungen dieser Entwicklungsversion (§0, §12). Sie dürfen vor der endgültigen
Präregistrierung anhand von Konstruktion, Messsystem und Pilotprüfungen am Aufbau überarbeitet werden; jede
Überarbeitung kommt mit Grund in A0. Alle übrigen offenen Regeln und Hardwarewerte bleiben offen (§12). In Tabelle F
und an den Regelstellen heißen diese Punkte „Arbeitsfestlegung, §12“. (3) Werkzeug 2: `code/auslegung.py` gibt PB1
nach §8.5 aus (D für F_min aus der bandbegrenzten Kurve, für Re und Im N_k in Fassung B, notwendige Bedingung
u_c < Δ_q/t_eq, Auslegungsgrenze nach A8); Fassung A und Faktor 0,1 erscheinen dort nur als Sensitivitätsangaben
(§12). Soweit die Einträge oben die hier festgelegten Punkte als offen führen, gilt dieser Eintrag.

**Folgen für andere Dokumente** (§12; am 25.09.2026 nachgezogen, soweit „erledigt“ vermerkt):

- **README, `overview.md`:** Zielgrößen γ₁, λ, A, F_min; nach v2 sind F_min − ⟨N⟩ und N₁ … N₃ primär, γ₁
  sekundär, A beschreibend, λ explorativ; v2 verlinken. README, Bildunterschrift der Zeltkurve: „Die Lage
  der Spitze folgt aus der Phasengeometrie“ (aus der Geometrie folgt bei identischen Modulen nur der Knick
  bei 120°, A2.2; das Maximum kann kontaktabhängig wandern, A5). Erledigt.
- **README, `overview.md`, Grundsatz:** README „Es werden keine Kräfte gemessen“ und `overview.md` „Gemessen
  wird nie ein Absolutwert“ (H3 und G6 brauchen eine absolute Kalibrierung, §0); `overview.md` „⟨N⟩ … keine
  Messgröße“ (⟨N⟩ wird in jedem Lauf bestimmt, H0). Umformuliert zu „primär ausgewertet“ und „Kontrollgröße,
  nicht Zielgröße“ (erledigt).
- **Exposé:** „braucht keine Statistik“, „direkt am Kraftsignal ablesbar“ (v2 entscheidet mit Residuen und
  Bootstrap); Ziel „Nachweis oder Falsifikation der F_min-Zeltkurve“ (v2: nur Lage der Spitze); die
  Vorzeichenregel „werden in die vorgesehene v2 der Präregistrierung aufgenommen“ (v2 registriert
  stattdessen H4); „11 Kanäle“ bei neun aufgezählten; „noch nicht präregistriert“. Erledigt; „11 Kanäle“
  ist mit den Nachträgen vom 2. Oktober 2026 durch „Kanalzahl offen“ ersetzt (abhängig von Messkette und
  Wegkanal).
- **Werkstattbericht:** „präregistriert“ (v1 war eine nicht extern registrierte Arbeitsfassung); „Zwei
  Schwellenwerte des Auswerteverfahrens sind nicht festgelegt“; „Steigung, die man gegen ein Messrauschen
  halten kann“ (v2 registriert nur die Lage der Spitze). Erledigt.
- **Literaturabgleich (§4.2, T3):** ε_ctrl ist nach v2 festgelegt (§8.8), ε_phys für die Wellenformgrößen
  ersetzt (§1). Erledigt.
- **`einordnung.md` (§4, §6), `zehn_fragen.md` (Nr. 3, 7), `neuheitsgrad.md` (§5, §6):** „harten Stopp“ bei
  jeder Mittelwertabweichung (nach v2: Lauf ungültig, Stopp erst bei reproduzierbarem Verstoß, S1); „gilt H1
  … als falsifiziert“, wenn keine Struktur über dem Rauschen (nach v2: „nicht entscheidbar“); „ohne jede
  Statistik am Kraftsignal ablesbar“; Wellenformstatistik als „primäre Zielgröße“ (nach v2: γ₁ sekundär).
  Erledigt; „primäre Zielgröße“ für die zeitaufgelöste Kontaktkraft bleibt, das gilt auch nach v2.
- **`code/linear_solver.py`:** `--section`, `--phi3`, `--f` liegen seit Commit `069cb9b` im Repository
  (Werkzeug 1, erledigt).

---

## A1 · Definitionen

| Größe | Definition |
|---|---|
| N_c(t), N(t) | Kraft der Wägezelle c = 1, 2, 3 nach Kalibrierung (P0.1); Gesamtkraft N = N₁ + N₂ + N₃ |
| Referenzlauf R | alle Module in Parkposition, Antriebe bestromt und haltend, gleiche Dauer wie ein Messlauf |
| Einzelmodullauf Lⱼ | nur Modul j läuft; die beiden anderen stehen in Parkposition, bestromt und haltend wie in R; ihre Masse bleibt an Bord |
| Kombinationslauf | alle drei Module laufen in einer Sollkonfiguration (Schnitt, Zusatz- oder Pilotkonfiguration) |
| Einstellung 2, Lⱼ′, Identifizierbarkeitslauf | zweite Amplitude oder zweite Frequenz (§5.5); Lⱼ′: Einzelmodullauf bei Einstellung 2; Identifizierbarkeitslauf: Kombinationslauf an einem Punkt von I bei Einstellung 2 |
| s, I, N_I, n₀′ | Kraftskala von Einstellung 2: s = (1/3)·Σⱼ \|N̄₁⁽ʲ⁾′\|/\|N̄₁⁽ʲ⁾\| aus den Einzelmodulläufen der Phase 0 (′: Einstellung 2) [Teil B]; Punkte der Identifizierbarkeitsläufe (mindestens drei Schnittpunkte); ihre Zahl je Block; Einzelmodulläufe je Modul bei Einstellung 2 in Phase 0 (≥ 20) |
| ŷ⁰′, ŷ¹′; r′ | Superpositionsvorhersagen bei Einstellung 2 aus den Lⱼ′ der Phase 0 bzw. der Phase 1; Residuen dagegen |
| Klasse p, χ²_p | Skalierung eines Residuums mit s: p = 0 (unabhängig), 1 (∝ s), 2 (∝ s²); Anpassungsmaß der Klasse p (§8.10, A9.13) |
| Kontrollsatz | R, L₁, L₂, L₃, L₁′, L₂′, L₃′ in zufälliger Reihenfolge |
| Parkposition | zeitgemittelte Lage der bewegten Masse über einen Zyklus (aus P0.5), Toleranz Δ_park [Teil B]; so sind die statischen Zelllasten in allen Laufarten gleich |
| D1, D2, D2ⱼ, D2_K | D1: passiver Körper gleicher Masse und Fußgeometrie ohne Antriebe. D2: Antriebe laufen, bewegte Massen abgekoppelt und am Rahmen fixiert; D2ⱼ: nur Antrieb j; D2_K: alle Antriebe in der Sollphasung einer Konfiguration (Punkte I) |
| Kontaktast (Modell) | periodische Lösung ohne Abheben (N > 0 und Auflagerkoordinate z < 0; Docstring von `code/linear_solver.py`). Dass er existiert, heißt nicht, dass der reale Zustand darauf liegt (A3) |
| Kontaktast (Messung) | Die Vorhersage ŷ⁰ der Konfiguration erfüllt mit den gemessenen Zeigern ρⱼₖ Bedingung (a) aus §5.3, und kein Lauf der Konfiguration bei f zeigt Einzelzell-Liftoff; ausgenommen sind Läufe, die nach G5, G8 oder G10 ungültig sind. Eine Konfiguration außerhalb des Kontaktasts ist nicht auswertbar (§9.1) |
| θ | Zyklusphase 0 … 2π; θ = 0 am Indeximpuls von Modul 1 (Kombinationsläufe, D2) bzw. von Modul j (Lⱼ); Referenzläufe: virtueller Takt mit f |
| φⱼ,c | Indexphase von Modul j im Zyklus c: 2π·(t_idx,j − t_idx,1)/T_c mod 2π, mit t_idx,j dem ersten Indeximpuls von Modul j nach t_idx,1 und T_c der Dauer des Zyklus c von Modul 1 |
| Δδⱼ, φⱼ^P | Δδⱼ = arg x₁⁽¹⁾ − arg x₁⁽ʲ⁾ (mod 360°), mit x₁⁽ʲ⁾ der ersten Weg-Harmonischen von Modul j bezogen auf den eigenen Indeximpuls (P0.5). Profilphase φⱼ^P = φⱼ + Δδⱼ. Alle Sollphasen (Schnitt, Zusatz- und Pilotkonfigurationen, G2) sind Profilphasen; die Regelung stellt die Indexphase φⱼ,soll^P − Δδⱼ ein |
| φ̄ⱼ, σⱼ | zirkuläres Mittel arg⟨e^{iφⱼ,c}⟩ über die Zyklen eines Laufs; Jitter σⱼ = √(−2·ln Rⱼ) mit Rⱼ = \|⟨e^{iφⱼ,c}⟩\| |
| ρⱼₖ | mittlerer Phasenzeiger ⟨e^{−ikφⱼ,c}⟩ über alle Zyklen aller gültigen Läufe einer Konfiguration, Läufe gleich gewichtet; ρ₁ₖ = 1 |
| Mittelkurve N̄(θ) | phasensynchrones Mittel über alle vollständigen Zyklen des Auswertefensters eines Laufs, auf N_θ = 2000 Stützstellen, Harmonische über k_max null gesetzt |
| Konfigurationsmittelkurve | Mittel der Mittelkurven aller gültigen Läufe einer Konfiguration, jeder Lauf gleich gewichtet |
| N_k | komplexe Harmonische k ≥ 1: N_k = (2/N_θ)·Σₙ N̄(θₙ)·e^{−ikθₙ}; \|N_k\| ist die Amplitude wie in `linear_solver.py --section` |
| ⟨N⟩ | Zeitmittel über eine ganze Zahl vollständiger Zyklen im Auswertefenster (= Gleichanteil der Mittelkurve) |
| statische Last, M, m_L | statische Last: Σ_c F_c,stat, Summe der Zellanzeigen bei ruhendem Körper mit geparkten Modulen gegen den Nullpunkt bei abgehobenem Körper (P0.1); physikalisch das Gewicht von Bauteilen und Innenluft abzüglich des Auftriebs ρ_L·g·V_außen in der Außenluft, zuzüglich gleichbleibender äußerer Kräfte (Kabel, Elektrostatik); unter H0 gleich ⟨N⟩ (§3). M = Σ_c F_c,stat/g aus P0.2 (Konvention b, Arbeitsfestlegung, §12; A9.2): Das Gewicht M·g ist die statische Last im Zustand von P0.2; Auftrieb, Innenluft und gleichbleibende äußere Kräfte sind enthalten und werden nicht noch einmal abgezogen. m_L = ρ_L·V_außen + m_hyd ist die träge Masse ohne Gewicht, die nicht in M enthalten ist; ρ_L·V_außen ersetzt den Auftrieb, um den M kleiner ist als die Masse von Bauteilen und Innenluft, die Innenluft steckt schon in M. Die träge Masse in H(ω) ist M + m_L. Nicht gewählt ist Konvention (a), M als Summe der wahren Bauteilmassen ohne Luft: statische Last ≈ M·g − ρ_L·g·V_Mat + (ρ_innen − ρ_L)·g·V_innen zuzüglich gleichbleibender äußerer Kräfte, m_L = ρ_L·V_innen + m_hyd. V_außen Außenvolumen, V_innen eingeschlossene Luft, V_Mat = V_außen − V_innen Materialvolumen, ρ_L und ρ_innen Dichte der Außen- bzw. Innenluft, m_hyd hydrodynamisch mitbewegte Luft (Tabelle C); Bezeichnungen wie in `code/auslegung.py` |
| N_c,k, F_min,c, Δ_c,q, Δ_c,rel,q | Harmonische und Minimum der bandbegrenzten Konfigurationsmittelkurve der Zelle c; Äquivalenz- und Relevanzgrenze von H1Z (§8.5) |
| T(kω), Ĉⱼ,ₖ | Übertragungsmatrix von den Modulkräften zu den Zellkräften bei der Harmonischen k: Statik der Dreipunktlagerung mit Zelllagen und relativen Zellverstärkungen aus P0.1, G_F je Zelle und Kippmoden aus P0.4 (A2.7); Ĉⱼ,ₖ = [T(kω)⁻¹·(N₁,ₖ, N₂,ₖ, N₃,ₖ)ᵀ]ⱼ, Zeiger von Modul j aus den Zellen |
| φⱼ^{P,Z}, Δφⱼ^Z | Profilphase von Modul j aus den Zellen, arg Ĉ₁,₁ − arg Ĉⱼ,₁; Abweichung Δφⱼ^Z = φⱼ^{P,Z} − φ̄ⱼ^P (E3a, §8.10) |
| R₊₁, R₋₁, q_Z, q_tol | gleich- und gegenläufige Komponente der ersten Harmonischen des Kippmoments aus den Zellkräften (A2.7); q_Z = \|R₋₁ − R̂₋₁\|/\|R̂₊₁\| am Triphasik-Punkt, R̂ aus der zellweisen Superposition (Differenz gegen die Vorhersage); q_tol = 5,8·10⁻⁴ (E3b, §8.10) |
| Schein-Oberwelle | Anteil der Kraft bei der 2- und 3-fachen Anregungsfrequenz in P0.4 über die vom Referenzaufnehmer gemessenen Oberwellen der Anregung hinaus (A9.2) |
| Betriebslast (P0.4) | je Zelle die größte vorhergesagte Harmonische der Zellkraft bei der Anregungsfrequenz in den Kombinations- und Einzelmodulläufen bei f (§5.2, A9.2) |
| F_min, F_max | Minimum und Maximum der bandbegrenzten Konfigurationsmittelkurve auf ihren N_θ Stützstellen; konfirmatorisch verglichen wird F_min − ⟨N⟩. Zyklusweise Minima und Minima ungefilterter Kurven sind nicht konfirmatorisch und werden nur beschreibend berichtet (E4) |
| γ₁ | Schiefe m₃/m₂^{3/2} der Konfigurationsmittelkurve über ihre N_θ Stützstellen (wie `scipy.stats.skew` in `linear_solver.py`) |
| A | (F_max − ⟨N⟩)/(⟨N⟩ − F_min), unter H0 mit ⟨N⟩ gleich der statischen Last; Codevariable `peak_ratio`; beschreibend |
| λ | Anteil der Rohwerte im Auswertefenster mit N < F_LO,Σ; explorativ |
| σ_c, σ_Σ, F_LO,c, F_LO,Σ | Standardabweichung der Rohwerte von Zelle c bzw. der Summe in Referenzläufen; Liftoff-Schwellen 5·σ_c bzw. 5·σ_Σ über dem Nullpunkt (P0.1) |
| Einzelzell-Liftoff | mindestens ein Rohwert N_c < F_LO,c im ganzen Lauf einschließlich Rampe und Einschwingzeit |
| N_s, N_s,int, β | Zeitmittel von N in Referenzläufen; N_s,int = (1 − β)·N_s,a + β·N_s,b, zeitlich linear interpoliert zwischen den beiden Referenzläufen a und b, die einen Lauf einschließen; β ∈ [0, 1] relative Lage des Laufs |
| Δ⟨N⟩, σ̂_ref, ε_ctrl | Δ⟨N⟩ = ⟨N⟩_Lauf − N_s,int. σ̂_ref ist die Standardabweichung derselben Statistik für Referenzläufe: Jeder Referenzlauf der Phase 0 wird gegen die Interpolation seiner beiden Nachbarn ausgewertet (leave-one-out), aus mindestens 42 Referenzläufen der Phase 0 (P0.7), also mindestens 40 Werten; σ̂_ref,c ebenso je Zelle. ε_ctrl = 3·σ̂_ref oder 3·σ̂_betr (§8.8) |
| σ̂_betr | Standardabweichung der auf mittige Lage normierten Werte Δ⟨N⟩·√(1,5/(1 + β² + (1 − β)²)) der nach G2–G10 gültigen Pilot- und Einzelmodulläufe der Phase 0 (§8.8, A9.8) |
| s_q, ν_p | s_q: gepoolte Standardabweichung über Läufe der Größe q, quadratisches Mittel der Standardabweichungen der Pilotkonfigurationen; ν_p = Σ(n_p,i − 1) mit den gültigen Läufen n_p,i |
| u_c, u_c,erw | u_c: kombinierte Unsicherheit einer Differenz Messung − Vorhersage (§8.3, A9.5). u_c,erw: vor Phase 1 erwarteter Wert, u_c,erw² = s_q²/n_min + u²(ŷ_q); für γ₁ mit u(γ̂₁) aus dem Bootstrap der Vorhersage |
| ν_eff | Welch–Satterthwaite, §8.3, A9.5 |
| ŷ⁰, ŷ¹; z⁰, z¹ | Vorhersage aus den Einzelmodulläufen der Phase 0 bzw. aus den Kontrollläufen der Phase 1; standardisierte Residuen dagegen |
| c, c_B, t_eq | c: kritischer Wert von H1, 95-%-Quantil von max_{i,q} \|z⁰_iq\| bei exakter Superposition aus der Kalibriersimulation (§8.4) [Teil B]; c_B = t(1 − 0,05/294; ν_eff): Bonferroni-Wert, für die Planung vor Teil B; t_eq = t(0,95; ν_eff): Quantil der Äquivalenztests von H1, H1Z und H3 (§8.5) |
| D_q, Δ_q, Δ_rel,q | vorhergesagte Struktur über den Schnitt als Punktwert aus ŷ⁰: für F_min − ⟨N⟩ die Spannweite max_i F̂_min,i − min_i F̂_min,i, für Re und Im N_k der Durchmesser max_{i,i′} \|N̂_k,i − N̂_k,i′\| der vorhergesagten Zeigermenge (Fassung B; Fassung A, max_i \|N̂_k,i\|, nur als Sensitivitätsanalyse, A9.9); Äquivalenzgrenze Δ_q = 0,25·D_q (Sensitivitätsvariante 0,1·D_q) und Relevanzgrenze Δ_rel,q = Δ_q des Mindesteffekttests (§8.5) [Teil B] (Arbeitsfestlegung, §12) |
| b̂_i⁰, b̂_i¹, u(b̂_i) | simulierter Rauschbias von F_min − ⟨N⟩ am Punkt i gegen ŷ⁰ (mit n₀ Einzelmodulläufen) bzw. ŷ¹ (mit n + d Kontrollläufen je Modul) und seine Unsicherheit (§5.4, A9.5) [Teil B] |
| SNR | s̄·1°/s_F: mittlere Flankensteigung des Zeltfits an der Vorhersage im Fitfenster mal 1°, geteilt durch die Pilotstreuung von F_min − ⟨N⟩ (§5.4) [Teil B] |
| N̂_k⁽ʲ⁾, δ_H3, Δ (H3) | H3-Vorhersage: Mittel der Monte-Carlo-Ziehungen von G_F(kω)·m_j·H(kω)·a_k⁽ʲ⁾ (§8.7, A9.7); Äquivalenzgrenze Δ = δ_H3·\|N̂_k⁽ʲ⁾\| (PB3) mit δ_H3 = 10 % (Testvariante, offen, §12); Relevanzgrenze von H3 gleich Δ oder größer (offen, §12) |
| γ̂₁, γ̄₁,i, u(γ̄₁,i) | vorhergesagte bzw. gemessene Schiefe der Konfigurationsmittelkurve; u(γ̄₁,i) Standardabweichung von γ̄₁,i im Bootstrap A (A9.5) |
| φ̄₂^P | gemessene Profilphase von Modul 2 einer Konfiguration: −arg ρ₂₁ + Δδ₂; Abszisse des Zeltfits (§8.6) |
| auswertbar | Konfiguration im Kontaktast (Messung) mit mindestens n_min gültigen Läufen (§9.1) |
| Schnitt | 21 Punkte φ₂ = 100°, 102°, …, 140° bei φ₃ = 240° (Profilphasen) |
| gespiegelter Schnitt | φ₂ = 240°, φ₃ = 100°, 102°, …, 140° |
| Feinfenster | φ₂ ∈ [100°, 140°], φ₃ ∈ [220°, 260°] (Fenster des 2°-Feinsweeps, `data/README.md`) |
| zyklische Phasenabstände | Die Phasen {0, φ₂, φ₃} aufsteigend auf dem Kreis; die drei Differenzen benachbarter Phasen einschließlich des Übergangs über 360°, in zyklischer Reihenfolge (A7) |
| f₁, f_m, ζ_m | niedrigste in N oder einer Zellkraft sichtbare Mode aus P0.4; alle Moden mit Dämpfungsgraden |
| k_b, k_max | k_b = ⌊f₁/(2f)⌋; k_max nach §5.4 und A9.2 |
| f_u, f_zul | kleinste ganzzahlige Frequenz, die (d) erfüllt; größte Rasterfrequenz, die (a) nach dem Auslegungswerkzeug (Parameter aus P0.1–P0.4, Konstruktionsprofil, ohne Zusatzkonfigurationen), (b) und (d) erfüllt |
| T_warm, T_park, T_ramp, T_e, T_e,P, T_a, T_a,P, T_ab, T_Lauf, T_φ | Aufwärmzeit; Dauer Parkposition → Startstellung; Rampe; Einschwingzeit; Einschwingzeit der Phase-0-Läufe (A9.2); Auswertefenster; Aufnahmefenster der Phase-0-Läufe; Rampe ab und Parken; T_Lauf = T_park + T_ramp + T_e + T_a + T_ab; längste Einregelzeit der Phasen in den Pilotläufen |
| n₀ⱼ, n₀, n_min, r, n, n_max, p̂, N_K, d | Einzelmodulläufe je Modul in Phase 0 (n₀ geplant); Mindestzahl gültiger Läufe je Konfiguration; Reserve; geplante Läufe = Blöcke; Höchstzahl nach Zeitbudget (§5.3 c); Anteil ungültiger Pilotläufe; Zahl der Konfigurationen je Block (21 oder 23); Zahl der Messtage [Teil B] |
| δφ_tol, σ_tol, δf_tol, ΔT, T_P0 | Toleranzen der Phase (0,5°), des Jitters, der Frequenz und der Zelltemperatur (G2, G3, G7); T_P0 Temperaturmittel der Zelle während P0.8 bei f |
| W, w, φ₂*, φ̂₂* | Fitfenster, Halbbreite (unabhängig von u_c,erw), Spitzenlage aus dem Fit an der Messung bzw. an der Vorhersage (§8.6, A9.6) |
| δ_H2; [a⁰, b⁰], [a¹, b¹] | Äquivalenz- und Relevanzgrenze von H2 für Δφ* = φ₂* − φ̂₂*, δ_H2 = 1° (Testvariante, offen, §12); Intervalle von Δφ* gegen ŷ⁰ bzw. ŷ¹ auf dem Niveau 95 % (Typ und Rückfall: §8.6, A9.6) |
| V | Prüfmenge für H4 (§8.5) |

---

## A2 · Herleitungen

### A2.1 Modell im Kontaktast und Superposition

Solange der Körper nicht abhebt, ist das Modell der Referenz-Engine linear (Docstring von
`code/linear_solver.py`):

    (M + m_L)·ẍ + C·ẋ + K·x = −μ·M·ā(t),     N(t) = M·g − K·x − C·ẋ

mit ā(t) dem Mittel der drei Modulbeschleunigungen und μ dem Anteil der Masse, der sich mit den Modulen
bewegt; μ·M = Σⱼ m_j. M·g ist die statische Last, das Gewicht im Zustand von P0.2 (M = Σ_c F_c,stat/g, A1);
M + m_L ist die träge Masse, mit der auch P0.4 angepasst wird (A1; in `linear_solver.py` ist m_L = 0). m_L
ist linear und zeitinvariant und lässt die Superposition unberührt. Für die k-te Harmonische der
Anregungsfrequenz f (ω = 2πf) gilt

    N_k = μ·M · H(kω) · P_k · (1 + e^{−ikφ₂} + e^{−ikφ₃}) / 3,     H(ω) = (K + iωC) / (K − (M + m_L)·ω² + iωC)

mit P_k den Fourier-Koeffizienten der Profilbeschleunigung. Die Phasenlage wirkt nur über den Kammfaktor
(1 + e^{−ikφ₂} + e^{−ikφ₃})/3. Am Triphasik-Punkt (120°, 240°) verschwindet er für alle k, die kein
Vielfaches von 3 sind; es bleiben k = 3, 6, 9 …

Für ein einzelnes Modul j mit bewegter Masse m_j und Profilharmonischen P_k⁽ʲ⁾ gilt N_k⁽ʲ⁾ = m_j·H(kω)·P_k⁽ʲ⁾,
bezogen auf seinen eigenen Takt, und jede Phasenkonfiguration ist die Summe

    N_k = Σⱼ N_k⁽ʲ⁾ · e^{−ikφⱼ},     φ₁ = 0.

Weil N_k⁽ʲ⁾ in den Einzelmodulläufen gemessen wird, gilt diese Superposition für jedes lineare,
zeitinvariante System, auch bei ungleichen Modulen und einer beliebigen Übertragung; K, C und μ werden
nicht gebraucht. Im Zeitbereich lautet sie N̂(t) = N_s + Σⱼ [N⁽ʲ⁾(t − τⱼ) − N_s] mit τⱼ = φⱼ/(2πf). Für
starre Auflage (H = 1) bleibt N(t) = M·g + Σⱼ m_j·a_j(t − τⱼ), das Newtonsche Gesetz für den ruhenden
Körper; dass die Wellenform von der Phasenlage abhängt, ist damit keine offene Frage. Bei identischen
Modulen entspricht ein Einzelmodullauf im Modell der synchronen Phasung mit μ/3; so wird er im
Zahlennachweis gerechnet.

### A2.2 Knick der Zeltspitze

Bei identischen Modulen hat N(t) am Triphasik-Punkt die Periode T/3 und drei gleich tiefe Minima θ_m.
Ändert sich φ₂ um δ, ändert sich jedes Minimum in erster Ordnung um δ·s_m mit s_m = ∂N/∂φ₂ an θ_m. Die
Harmonischen k = 3, 6, 9 … tragen zu s_m nichts bei: Ihr Beitrag zu ∂N/∂φ₂ ist bei φ₂ = 120° gleich
−(1/3)·dN/dθ, und die Minima sind stationäre Punkte von N. Die übrigen Harmonischen liefern an den drei um
T/3 versetzten Minima Beiträge mit der Summe null. F_min, das kleinste der drei Minima, steigt deshalb
links der Spitze mit max s_m > 0 und fällt rechts mit −min s_m > 0: ein Knick mit relativem Maximum bei
120°, für jeden linearen Kontakt mit glatter Wellenform, also auch für jede bandbegrenzte Kurve.

Referenzparameter: s_m = −0,196, +0,206, −0,011 N/° (Summe null bis auf 5·10⁻⁵). Die lokalen Steigungen mit
0,1° Abstand betragen 0,207 N/° links und 0,196 N/° rechts (F_min = 5,3097 / 5,3304 / 5,3108 N bei
119,9° / 120° / 120,1°). Die 2°-Sekanten 118° → 120° bzw. 122° → 120° betragen 0,212 bzw. 0,195 N/°; sie
weichen wegen der Krümmung der Flanken von den lokalen Steigungen ab. Die Flanken sind verschieden steil,
weil die drei s_m nicht symmetrisch liegen. Bei starrer Auflage liegen die Minima auf Knicken der
Profilbeschleunigung; der Knick bei 120° bleibt, und die 2°-Sekanten sind gleich (0,0469 und 0,0468 N/° bei
μ = 0,4), weil die Egg-Beschleunigung zeitumkehrsymmetrisch ist.

### A2.3 Schiefe am Triphasik-Punkt

Bei identischen Modulen enthält N − ⟨N⟩ am Triphasik-Punkt nur k = 3, 6, 9 …; mit
N − ⟨N⟩ = Σₖ a_k·cos(kθ + ϑ_k) gilt

    m₃ = (3/4)·a₃²·a₆·cos(2ϑ₃ − ϑ₆) + (3/2)·a₃·a₆·a₉·cos(ϑ₃ + ϑ₆ − ϑ₉) + …

Ohne Harmonische k ≥ 6 ist die Schiefe null (⟨cos³⟩ = 0). Ihr Vorzeichen hängt u. a. vom Term
a₃²·a₆·cos(2ϑ₃ − ϑ₆) ab, in den über ϑ₃ und ϑ₆ die Phasen von H(3ω) und H(6ω) eingehen. Mit k ≤ 6 ergibt
die Formel −0,3775 bei starrer Auflage (cos(2ϑ₃ − ϑ₆) = −1,000) und +0,0658 bei K = 10⁴ N/m
(cos(2ϑ₃ − ϑ₆) = +0,912), wie die bandbegrenzte Rechnung; mit vollem Spektrum −0,450 bzw. +0,067. Deshalb
hängt das Vorzeichen an diesem Punkt vom Kontakt ab, und H4 wird gegen die Superpositionsvorhersage
geprüft.

### A2.4 Jitterfaktor

Für normalverteilten Jitter mit Standardabweichung σⱼ (in rad) ist ρⱼₖ = e^{−ikφ̄ⱼ}·e^{−k²σⱼ²/2}. Jitter
dämpft die Harmonischen der Mittelkurve nur über den Faktor e^{−k²σ²/2}; bei σ = 1° beträgt er 0,99985,
0,99939 und 0,99863 für k = 1, 2, 3 sowie 0,99453 und 0,98774 für k = 6 und 9. Konfirmatorisch wird der
gemessene Zeiger ρⱼₖ verwendet, nicht die Normalverteilungsannahme. Die Minima einzelner Zyklen streuen
stärker; sie sind explorativ (E4).

### A2.5 Zellkräfte

Annahme für die Auslegung: starrer Körper auf drei Zellen, Schwerpunkt des Körpers über dem
Flächenschwerpunkt des Zelldreiecks, jedes Modul über einer Zelle. Eine senkrechte Kraft über einem
Auflagerpunkt geht bei Dreipunktlagerung ganz in dieses Auflager; deshalb trägt Zelle j bei jeder Phasung
M·g/3 + m_j·a_j(t − τⱼ). Ihr Minimum ist bei identischen Modulen ein Drittel des Minimums der synchronen
Phasung, unabhängig von φ₂ und φ₃. Je Zelle gilt dann die Grenze der synchronen Phasung, und die Zellkräfte
aller Konfigurationen sind bis auf eine Zeitverschiebung gleich. Bei anderer Lage von Zellen und Modulen
ändert sich das; die Lage ist offen (§12), und Bedingung (a) wird mit den gemessenen Zellkräften geprüft
(§8.2).

### A2.6 Skalierung der Residuen und Paaradditivität

Ein lineares, zeitinvariantes System erfüllt die Superposition exakt (A2.1). Ein Residuum entsteht nur
durch Nichtlinearität, Zeitvarianz zwischen Einzelmodul- und Kombinationsläufen oder Wechselwirkung der
Antriebe. Werden alle Modulkräfte um den Faktor s skaliert, bei gleicher Form, gilt:

- **Quadratische Nichtlinearität.** Mit einer Kennlinie N_mess = N + β·N² und den Modulanteilen yⱼ ist das
  Residuum der Mischterm β·[(Σⱼ yⱼ)² − Σⱼ yⱼ²] = 2β·Σ_{j<l} yⱼ·y_l; der statische Anteil fällt heraus. Er
  skaliert mit s². Das gilt für die Kennlinie einer Zelle, die Kräfte mehrerer Module trägt (bei Modulen
  über den Zellen nicht, A2.5), ebenso für einen Kontakt, dessen Kraft nichtlinear von der Einfederung
  abhängt. Beide skalieren bei zweiter Amplitude mit s² und sind dann nicht unterscheidbar. Beim Kontakt geht
  zusätzlich der Faktor 1 − H(kω) ein, mit dem ein Kontaktresiduum an die Zellen gelangt (im steifen Bereich
  ≈ −M·(kω)²/K); er verteilt das Residuum anders über die Harmonischen und wächst bei zweiter Frequenz mit
  festem Hub mit (kω)², also mit s. Ein Kontaktresiduum skaliert dann im steifen Bereich stärker als s² (etwa
  mit s³) und fällt aus den Klassen (als Skalierung; die Zuordnung nach A9.13 weist es erst bei großer
  Abweichung als „nicht zuordenbar“ aus, bei mittlerer kann sie es p = 2 zuordnen, A9.11), ein Kettenresiduum
  skaliert weiter mit s²; das nutzen die registrierten
  Läufe nicht konfirmatorisch.
- **Kopplung fester relativer Stärke.** Weicht die Antwort im Kombinationslauf um einen festen Bruchteil x
  von der im Einzelmodullauf ab, ist das Residuum x·ŷ; es skaliert mit s.
- **Von der Amplitude unabhängige Störung** (Drift, Einstreuung): Das Residuum skaliert nicht.
- **Kopplung, deren Stärke mit der Last wächst** (x ∝ s, etwa ein Spannungseinbruch der Versorgung unter
  Last): Das Residuum skaliert mit s² wie eine Nichtlinearität.

Die Klasse beschreibt also die Skalierung, nicht den Mechanismus. Bei einer zweiten Frequenz mit festem Hub
skaliert die Profilbeschleunigung mit f², und s wird aus den Einzelmodulläufen gemessen. Frequenzabhängige
Mechanismen (1 − H(kω) beim Kontakt, Lastmoment einer Nocke) verschieben dann die Exponenten; das prüft die
Kalibriersimulation (A9.11). Mit s = 0,5 verhalten sich die Residuen der drei Klassen wie 1 : 0,5 : 0,25.

**Paaradditivität.** Mischterme zweiter Ordnung addieren sich über die Modulpaare: Das Residuum einer
Konfiguration ist die Summe der Residuen der drei Paare in denselben Phasen. Paarläufe prüfen das und
ordnen eine Wechselwirkung einem Paar zu (§5.5).

**Gerade Harmonische.** Enthält das Profil nur ungerade Harmonische (Sinus oder ungerade-harmonisches
Profil), enthält die Antwort eines linearen Systems ebenfalls nur ungerade, auch bei linearer Kopplung.
Eine quadratische Kennlinie erzeugt gerade Harmonische, schon im Einzelmodullauf über den Eigenterm β·yⱼ²,
bei doppelter Amplitude mit vierfachem Betrag. Das nutzt der Linearitätslauf P0.12. Eine kubische
Nichtlinearität erzeugt nur ungerade Harmonische und bleibt dort unsichtbar.

### A2.7 Modulzeiger aus den Zellkräften (E3)

Im Kontaktast ist jede Zellkraft eine lineare Funktion der Modulkräfte: N_c,k = Σⱼ T_cj(kω)·Cⱼ,ₖ. Bei
starrem Körper und starrer Auflage folgt T aus der Statik der Dreipunktlagerung: Eine senkrechte Kraft
verteilt sich nach den baryzentrischen Koordinaten ihres Angriffspunkts im Zelldreieck auf die Zellen. Bei
endlicher Steifigkeit kommen die Kippmoden hinzu (P0.4 mit exzentrischer Anregung). Aus den drei
Zellzeigern folgen die drei Modulzeiger Ĉⱼ,ₖ = [T⁻¹·N_k]ⱼ; die Summe liefert nur eine Gleichung, die Zellen
liefern drei.

- **Geometrie.** Sitzen die Module über den Zellen (G0), ist T diagonal, und jede Zelle misst ein Modul.
  Eine relative Zellverstärkung ist dann von Masse und Hub des Moduls darüber nicht unterscheidbar; nur P0.1
  trennt sie. Sind die Module um 60° gedreht auf halbem Zellradius angeordnet (G60h), ist T voll besetzt
  (Kondition etwa 2). Mit k = 1 und 2 und bekannten Zelllagen ist eine Zellverstärkung dann von Modulfehlern
  trennbar, offen bleibt nur die gemeinsame Skala; bei unbekannten Zelllagen ist sie mit der radialen Lage
  der Zelle vermischt. Die Lage ist offen (§12).
- **Parameter.** Je Modul Skala und Phase, je Zelle Verstärkung und Lage in der Ebene: 15 Parameter. Aus
  den Läufen allein, auch mit Einzelmodulläufen und k = 1 … 5, sind nur 12 bestimmbar, mit Gewichtsstücken
  an mindestens fünf Laststellen bekannter Lage in P0.1 alle 15.
- **Lagefehler.** Beispiel: Zellradius 0,1 m, G0, Triphasik-Punkt. Liegt eine Zelle 1 mm weiter außen als
  angenommen, erscheint das als −0,66 % am Modul darüber und als −0,165 % mit ±0,165° Scheinphase an den
  Nachbarmodulen; 1 mm tangential als 0,29 % und 0,29° an den Nachbarn. Für die E3-Schwelle von 0,1°
  müssen die Zelllagen in diesem Beispiel auf etwa 0,1 mm bekannt sein; der Beitrag beträgt dann etwa
  0,017°. Bei G60h ist das mit der dortigen Statik neu zu rechnen.
- **Phase gegen Kalibrierung.** Ein Phasenversatz δ eines Moduls dreht dessen Zeiger bei der Harmonischen k
  um −k·δ. Die Scheinphase einer Zellverstärkung wechselt bei G60h von k = 1 zu k = 2 das Vorzeichen. Der
  Vergleich von k = 1 und k = 2 unterscheidet beides.
- **Gültigkeit.** Die Zuordnung zu einem Modul ist exakt nur bei starrem oder steifem Aufbau. Bei weichem
  Kontakt hängt T von den Modulmassen ab; eine Abweichung eines Moduls ändert dann T selbst. E3 setzt eine
  lineare Übertragung voraus: Ein nichtlinearer Mischterm von Kontakt oder Kette und ein Fehler von T
  jenseits seiner Unsicherheit erscheinen als Abweichung eines Modulzeigers.
- **Gegenkomponente.** Die erste Harmonische des Kippmoments zerfällt in eine gleich- und eine gegenläufige
  Komponente R₊₁ und R₋₁. Bei identischen Modulen ist R₋₁ am Triphasik-Punkt null. Weicht der Zeiger eines
  Moduls relativ um ε ab (Amplitude oder Phase), entsteht |R₋₁|/|R₊₁| ≈ |ε|/3: 1 % ergibt 3,3·10⁻³, 0,1°
  ergibt 5,8·10⁻⁴ (q_tol). Der Betrag des Moments ist beim Egg-Profil nicht konstant.

---

## A3 · Simulationsbefunde der Referenz

Parametersatz der Engine (README, „Simulationsstand“): M = 0,650 kg, μ = 1, f = 10 Hz, Hub 7,69 mm,
K = 10⁴ N/m, C = 16 N·s/m (ζ = 0,099228), f_n = 19,74 Hz, M·g = 6,3765 N.

- **Zeltkurve.** F_min = 5,3304 N bei (120°, 240°), 0,7677 N bei φ₂ = 100°, 1,6176 N bei 140°.
  2°-Sekanten 118° → 120° bzw. 122° → 120°: 0,212 bzw. 0,195 N/°; die Werte ≈ 0,23 und ≈ 0,19 N/° des
  Exposés sind die 20°-Sekanten 0,228 und 0,186 N/°. Die Referenz ist ein Resonanzfall: 2f/f_n = 1,013,
  |H₂| = 5,03. Bei festem ζ und K = 3·10⁴ … 10⁷ N/m betragen die 2°-Sekanten 0,09–0,12 N/°. Die
  Simulationswerte sind keine Vorhersage für einen realen Aufbau.
- **Schiefe: Referenzbefund und Geltungsbereich.** Auf den Linien φ₂ = 0°, φ₃ = 0° und φ₂ = φ₃ des
  19×19-Referenzrasters (55 Punkte, darunter die synchrone Phasung) ist γ₁ ≥ +0,596; alle 36 negativen
  Werte liegen bei dephasierten Konfigurationen. Diese Zahlen beschreiben ausschließlich das gespeicherte
  Raster beim oben genannten Parametersatz. Es stammt aus der nichtlinearen Engine und enthält
  Liftoff-Punkte, deren Einzelwerte von der Startbedingung abhängen (README).
  Die frühere allgemeine Vorzeichenregel ist mit Arbeitspapier v2.4 als Mechanismus-Aussage
  zurückgezogen: Bei geänderter Kontaktübertragung können schon einzelne Module und Zweiergruppen
  im Dauerkontakt negative Schiefe zeigen. Auch am Triphasik-Punkt hängt das Vorzeichen vom Kontakt ab:
  γ₁ = +0,067 bei K = 10⁴ N/m und −0,450 bei starrer Auflage (A2.3).
  H4 bleibt bestehen und prüft das Vorzeichen gegen die Superpositionsvorhersage aus gemessenen
  Einzelmodulantworten, nicht gegen eine allgemeine Zuordnung von Phasenklasse und Vorzeichen.
- **Kontaktast.** Bei der Referenz besitzen 4,24 % des Phasenraums (1°-Raster) einen Kontaktast: zwei
  Hauptgebiete um (120°, 240°) und (240°, 120°) mit 2 × 2524 Punkten (3,90 %), in allen Proben monostabil,
  und sechs Satelliteninseln mit 6 × 74 Punkten (0,34 %), die bistabil sind: Bei (35°, 116°) ergibt der
  Standardstart der Engine λ = 75,82 %, der Start auf dem linearen Orbit λ = 0 %. Der Anteil hängt stark
  von Auflage und μ ab: 76,6 % bei starrer Auflage, 48,6 % bei K = 10⁴ N/m und μ = 0,5. Im
  Liftoff-Bereich ist die Phasenkarte nicht eindeutig; konfirmatorisch wird nur im Kontaktast geprüft.
- **Einzelmodul.** Bei den Referenzparametern hebt ein einzelnes Modul ab (lineares F_min = −2,057 N); die
  Superposition wäre dort nicht anwendbar. Der reale Arbeitspunkt muss auch die Einzelmodulläufe im Kontakt
  halten (§5.3).
- **Gespiegelter Schnitt.** (110°, 240°) und (240°, 110°) ergeben dasselbe F_min = 3,0846 N und dieselbe
  Schiefe −0,3846.

---

## A4 · Beispiel: starre Auflage, μ = 0,4

Ein realer Aufbau hat einen Rahmen mit eigener Masse (μ < 1) und mit steifen Wägezellen eine
Kontakteigenfrequenz weit über 3f. Als Beispiel dient die starre Auflage mit μ = 0,4; Masse, Hub und Profil
sind die der Simulationsreferenz, nicht die eines geplanten Aufbaus. Das Beispiel zeigt, wie die
Auslegungsregeln wirken; seine Zahlen, auch die Kopplungszahlen unten und in Tabelle C, sind Rechenbeispiele,
keine Vorhersagen für die reale Apparatur V1 (§5.1).

| Fall | Kontaktast auf allen 21 Punkten | F_min bei 120° | F_min bei 100° und 140° | kleinstes F_min / M·g | 2°-Sekante 118° → 120° | ΔF_Zelt |
|---|---|---|---|---|---|---|
| starr, μ = 0,4, 10 Hz | ja | 5,6452 N | 5,1759 N | 81,2 % | 0,0469 N/° | 0,4693 N |
| starr, μ = 0,4, 14 Hz | ja | 4,9432 N | 4,0233 N | 63,1 % | 0,0918 N/° | 0,9199 N |
| starr, μ = 0,4, 19 Hz | ja | 3,7365 N | 2,0424 N | 32,0 % | 0,1691 N/° | 1,6941 N |
| starr, μ = 0,4, 20 Hz | ja | 3,4513 N | 1,5741 N | 24,7 % | 0,1874 N/° | 1,8772 N |
| Referenz: K = 10⁴ N/m, μ = 1, 10 Hz | ja | 5,3304 N | 0,7677 N / 1,6176 N | 12,0 % | 0,2124 N/° | 4,5627 N |

ΔF_Zelt ist die Spannweite von F_min über die 21 Punkte; die Zahlen gelten für das volle Spektrum.

- **Kein Liftoff auf dem Schnitt.** Bei 10 Hz beträgt das kleinste F_min 81,2 % von M·g. An den
  Schnitträndern hebt der Körper erst zwischen 23 und 24 Hz ab (lineares F_min bei 100°: 0,0254 N bzw.
  −0,5389 N).
- **Kleine Zeltsteigung.** Die 2°-Sekanten an der Spitze betragen bei 10 Hz 0,0469 und 0,0468 N/°. Die
  Flanke knickt bei etwa 114° und 126° ab (Schnitt der äußeren und inneren Geraden bei 114,01° und 125,98°);
  außerhalb (100°–112° und 128°–140°) beträgt die Steigung 0,0135 N/°. Das illustriert die Fensterregel für
  H2 (§8.6).
- **Frequenz als Stellgröße.** Bei starrer Auflage gilt N − M·g = μ·M·ā(t), und bei gleichem Hub ist
  ā ∝ f². Alle Kraftabweichungen von M·g und alle Steigungen skalieren mit f² (0,0469 → 0,0918 →
  0,1874 N/° bei 10, 14 und 20 Hz, Faktor 1,96 bzw. 4,0); γ₁ und A bleiben gleich (bei 120°: −0,4498 und
  0,6529). Bei endlicher Steifigkeit kommt die Frequenzabhängigkeit von H(kω) hinzu.
- **Grenzen durch die übrigen Läufe.** Ein Einzelmodullauf (F_min = 5,3642 N bei 10 Hz) hebt zwischen 25
  und 26 Hz ab, die Zweiergruppen-Phasung (0°, 180°) zwischen 21 und 22 Hz, die synchrone Phasung (0°, 0°)
  zwischen 14 und 15 Hz. Mit dem Sicherheitsabstand von 25 %, nach der Gesamtkraft beurteilt, erlauben auf
  dem 1-Hz-Raster der Schnitt höchstens 19 Hz, ein Einzelmodul 21 Hz, (0°, 180°) 18 Hz und die synchrone
  Phasung 12 Hz. Maßgeblich ist aber die Zellkraft: Im Zellmodell von A2.5 gilt je Zelle die Grenze der
  synchronen Phasung, höchstens 12 Hz (31,4 % bei 12 Hz, 19,5 % bei 13 Hz); bei 10 Hz bleibt jede Zelle mit
  52,4 % der statischen Zelllast im Kontakt. Nach der Gesamtkraft wären bei 10 Hz beide
  Zusatzkonfigurationen zulässig (kleinstes F_min 52,4 % bzw. 78,9 % von M·g).
- **Summenkraft und Nennlast.** Bei 10 Hz bleibt die Summenkraft auf dem Schnitt unter 7,08 N (größtes
  F_max 7,0752 N bei 100° und 140°). Das gilt nur für den Schnitt: Die synchrone Phasung erreicht
  12,0163 N, (0°, 180°) 9,1241 N, ein Einzelmodullauf 8,2564 N. Im Zellmodell trägt jede Zelle höchstens
  12,0163/3 = 4,0054 N bei einer statischen Zelllast von 2,1255 N. Im Liftoff-Bereich (E1) sind weit
  höhere Spitzen möglich; die Simulation mit μ = 1 und K = 10⁴ N/m erreicht 50,6 N. Die Nennlast wird nach
  §5.1 aus der größten erwarteten Zellkraft bestimmt und ist noch nicht hergeleitet. Das Exposé nennt seit
  den Nachträgen vom 2. Oktober 2026 keine Zahl mehr (zuvor „mindestens 10 kg“, dort nicht hergeleitet).
- **Schiefe.** Auf dem Schnitt ist γ₁ überall negativ (−0,450 bei 120°, −0,793 bei 100° und 140°), bei
  synchroner Phasung +0,755, bei (0°, 180°) +0,986. Diese Vorzeichen gelten für das hier berechnete
  Beispiel mit starrer Auflage und μ = 0,4. Sie bestätigen keine allgemeine Vorzeichenregel; diese
  ist mit Arbeitspapier v2.4 als Mechanismus-Aussage zurückgezogen (A3). H4 prüft weiterhin gegen die
  Superpositionsvorhersage aus gemessenen Einzelmodulantworten.
- **Endliche Steifigkeit.** Bei K = 10⁶ N/m (ζ fest) weichen die Beträge der ersten drei Harmonischen um
  0,3 %, 1,0 % und 2,4 % vom starren Wert ab (bei 19 Hz um 0,9 %, 3,8 % und 9,1 %), die der sechsten und
  neunten bei 10 Hz um 10 % und 26 % (|H| = 1,101 und 1,259; |H(3ω)| = 1,024). F_min bei 120° liegt deshalb
  0,083 N unter dem starren Wert (5,5620 gegen 5,6452 N, 18 % von ΔF_Zelt). H3 mit k ≤ 3 prüft den Kontakt
  in diesem Bereich kaum (§8.7); F_min und γ₁ enthalten ihn. Die Abweichungen der ersten drei Harmonischen
  liegen, auch bei 19 Hz, unter der Testvariante δ_H3 = 10 % (offen, §12). Der Kontaktanteil, auf den sich PB3
  bezieht, |H − 1|/|H| = |N̂_k⁽ʲ⁾ − G_F·m_j·a_k⁽ʲ⁾|/|N̂_k⁽ʲ⁾|, beträgt bei 10 Hz 0,3 %, 1,0 % und 2,3 % (A9.7, Z).
  Eine Bestätigung von H3 bei dieser Testvariante ist keine Bestätigung des Kontaktgesetzes oder des
  Kontaktmodells; H3 prüft dann Masse, Profil und Kalibrierung. Den Kontakt prüfte erst Fassung I (offen, §12)
  oder eine Grenze unter dem Kontaktanteil.
- **Einfederung.** Ein Einzelmodullauf federt bei K = 10⁶ N/m (ζ fest, μ = 0,4, 10 Hz) mit |x_k| = 1,30,
  0,43 und 0,19 µm für k = 1, 2, 3 ein. Eine Prüfung über die Betriebsimpedanz (§8.7, Fassung I) müsste das
  auf etwa 1 % auflösen, also auf etwa 13, 4,3 und 1,9 nm nach phasensynchroner Mittelung.
- **Größenordnung von PB1.** Gerechnet mit derselben Bandbegrenzung wie die Messung (k_max = 9, A6) ist
  ΔF_Zelt = 0,5173 N und Δ(F_min) = 0,1293 N. Notwendig für PB1 ist u_c < Δ/t_eq = 0,0786 N (ν → ∞) bzw.
  0,0748 N (ν = 19). Für eine Bestätigungswahrscheinlichkeit von 0,8 bei exakter Superposition und 294
  unabhängigen Intervallen (147 Tests gegen ŷ⁰ und ŷ¹) braucht es u_c ≤ Δ/5,01 = 0,0258 N (ν → ∞) bzw.
  Δ/5,21 = 0,0248 N (ν = 19), 0,39 % von M·g. Die Grenze gilt je Größe. Für Re und Im N₁, N₂, N₃ ist Δ_q in
  Fassung B 0,2218, 0,1374 und 0,0799 N, also u_c ≤ 0,0443, 0,0274 und 0,0159 N (ν → ∞; A8, Z); die Grenze für N₃
  ist enger als die für F_min − ⟨N⟩. In Fassung A (Sensitivitätsanalyse) wäre Δ_q für N₁ 0,1126 N, also
  u_c(N₁) ≤ 0,0225 N. Welche Größe bindet, hängt vom Rauschmodell ab (A8). Das gilt für H1 allein; die gemeinsame
  Bedingung mit H2 (§5.4) kann mehr verlangen (A8). An der Spitze entspricht Δ(F_min) bei der bandbegrenzten
  2°-Sekante 0,0343 N/° (A6) einer Verschiebung von etwa 3,8°; die Testvariante δ_H2 = 1° (offen, §12) ist dort
  strenger als die Äquivalenz von H1.
- **Größe einer Kopplung.** Weicht die Antwort aller Module in den Kombinationsläufen um 0,1 % (1 %) von den
  Einzelmodulläufen ab, beträgt das größte Residuum von F_min − ⟨N⟩ bandbegrenzt (k_max = 9) 1,22 mN
  (12,2 mN), also 0,9 % (9 %) von Δ(F_min) = 0,1293 N. Ein Phasenversatz von 0,05° an Modul 2 nur in den
  Kombinationsläufen ergibt 1,75 mN (bei 120°). Solche Abweichungen liegen weit innerhalb von Δ_q. Bei
  kleinem u_c sind sie nachweisbar und erscheinen dann neben „bestätigt“ als Zusatz „Abweichung nachgewiesen,
  innerhalb der Äquivalenzgrenze“ (§9.3); ihre Klasse ordnen die Identifizierbarkeitsläufe zu (§8.10).
  Das größte Residuum erreicht die Grenze Δ(F_min) erst bei einer gemeinsamen Kopplung aller Module von etwa
  10,6 % (linear, Z). Das veranschaulicht, dass eine Bestätigung von H1 eine grobe Modellübereinstimmung innerhalb
  registrierter Toleranzen ist (§2, §3). Diese und die übrigen Kopplungszahlen sind Rechenbeispiele, keine
  Vorhersagen für die reale Apparatur V1.

---

## A5 · Resonanzfall und Lage der Spitze

Bei identischen Modulen liegt bei 120° immer ein Knick mit relativem Maximum (A2.2). Ob er auch das Maximum
des Schnitts ist, hängt vom Kontakt ab. Werden Vielfache von 3 resonant überhöht, sinkt F_min(120°), und das
Maximum wandert: Bei μ = 0,4, 10 Hz, f_n = 120 Hz (K = 369 518 N/m) und ζ = 0,02 liegt es bei 106°
(5,2096 N gegenüber 5,1342 N bei 120°). Mit der Bandbegrenzung nach Bedingung (b) (hier k_max = 6) liegt
es im selben Fall bei 120° (2°-Sekante 0,0339 N/° gegenüber 0,0331 N/° bei starrer Auflage mit derselben
Bandbegrenzung). In allen gerechneten Fällen mit ζ ≈ 0,1 (K = 10⁴ N/m; K = 3·10⁴, 10⁵, 10⁶ und 10⁷ N/m mit
festem ζ) und bei starrer Auflage liegt das Maximum auf dem 2°-Raster bei 120°. Bei ungleichen Modulen ist
die Auslöschung unvollständig, und die Spitze verschiebt sich um einen Betrag, den die Superposition aus den
Einzelmodulläufen vorhersagt.

Bedingung (b) muss alle ausgewerteten Harmonischen erfassen, nicht nur k ≤ 3, weil am Triphasik-Punkt
k = 3, 6, 9 … die Wellenform bestimmen: An der Grenze 3f = f_n/2 liegt 6f auf f_n. Mit M = 0,650 kg,
μ = 1, 10 Hz und festem ζ (f_n = 60 Hz, K = 92 379 N/m) sinkt F_min(120°) dort auf 3,4258 N gegenüber
4,5483 N bei starrer Auflage.

---

## A6 · Bandbegrenzung und Resonanzabstand

**Resonanzabstand.** Mit r = k·f/f_m ist |H|² = (1 + 4ζ²r²)/((1 − r²)² + 4ζ²r²) ≤ 1/(1 − r²)². Für r ≤ 0,5
folgt |H| ≤ 1,33, und für ζ → 0 ist d ln|H| / d ln f = 2r²/(1 − r²) ≤ 0,67. Numerisch gelten beide Schranken
für jedes ζ ≤ 2 (Z). Die ausgewerteten Größen hängen dann nur schwach von K, ζ, f und Temperatur ab.

**Bandbegrenzung im Beispiel** (starr, μ = 0,4, 10 Hz). Bei k_max = 9 sinkt die 2°-Sekante an der Spitze auf
0,0343 N/°, F_min beträgt 5,6781 N bei 120° und 5,1608 N bei 100°, ΔF_Zelt 0,5173 N. γ₁ bei 120° beträgt
−0,4305 (k_max = 9), −0,3775 (k_max = 6) und null für 3 ≤ k_max ≤ 5, weil am Triphasik-Punkt unterhalb von k
= 6 nur die dritte Harmonische bleibt (A2.3); für k_max ≤ 2 ist die Kurve dort konstant. Alle
Auslegungszahlen in Teil B werden mit derselben Bandbegrenzung gerechnet wie die Messung.

**Abtastrate.** Lineare Interpolation eines Sinus der Frequenz k·f mit der Abtastrate f_s unterschätzt die
Amplitude höchstens um 1 − cos(π·k·f/f_s) ≈ (π·k·f/f_s)²/2. Die Bedingung (π·k_max·f/f_s)²/2 ≤ 10⁻³ verlangt
bei k_max = 9 und f = 10 Hz etwa f_s ≥ 6,3 kHz.

---

## A7 · Pilotkonfigurationen und Äquivalenz

Bei identischen Modulen ist eine Konfiguration bis auf Umbenennung der Module und Zeitverschiebung durch die
Folge ihrer drei zyklischen Phasenabstände bestimmt, bis auf zyklische Vertauschung (eine Spiegelung
entspräche einer Zeitumkehr und ist nur bei zeitumkehrsymmetrischem Profil und starrer Auflage eine
Symmetrie; sie erhält die Menge der Abstände). Jeder Punkt des Schnitts (φ₂, 240°) hat die Abstände
(φ₂, 240° − φ₂, 120°); der gespiegelte Schnitt hat dieselben Folgen (Vertauschen von Modul 2 und 3). Im
Feinfenster ist jede Konfiguration mit einem Abstand von 120° zu einem Punkt der Schnittgeraden
φ₂ ∈ [100°, 140°] äquivalent, auf dem 2°-Raster zu einem Schnittpunkt, und jede ohne einen solchen Abstand
zu keinem.

| Konfiguration | zyklische Abstände | äquivalent zu einem Schnittpunkt | F_min Referenz (K = 10⁴ N/m) | F_min starr, μ = 0,4, 10 Hz |
|---|---|---|---|---|
| (110°, 250°), Pilot | 110°, 140°, 110° | nein | 1,6016 N, Kontaktast | 5,1742 N (81,1 %) |
| (130°, 230°), Pilot | 130°, 100°, 130° | nein | 1,8699 N, Kontaktast | 5,3253 N (83,5 %) |
| (110°, 252°), Pilot | 110°, 142°, 108° | nein | 1,3164 N, Kontaktast | 5,1472 N (80,7 %) |
| (110°, 230°), Beispiel | 110°, 120°, 130° | ja, zu (130°, 240°) | 3,4139 N (wie (130°, 240°)) | — |
| (120°, 250°), Beispiel | 120°, 130°, 110° | ja, zu (130°, 240°) | 3,4139 N | — |

Die drei Pilotkonfigurationen liegen im Feinfenster, sind paarweise nicht äquivalent, und jeder ihrer
Abstände weicht um mindestens 10° von 120° ab (Festlegung, Tabelle F); ein Phasenfehler unterhalb von
δφ_tol kann sie deshalb nicht äquivalent machen. Der Abstand von 10° ist ein Phasenabstand, kein
physikalisches Maß: Einzelne Größen einer Pilotkonfiguration können denen eines Schnittpunkts nahekommen.
Die Nichtäquivalenz gilt für N; im Zellmodell von A2.5 sind die Zellkräfte aller Konfigurationen bis auf
eine Zeitverschiebung gleich. Im Beispiel erfüllen die Pilotkonfigurationen den Kontaktast mit Abstand:
Die Gesamtkraft bleibt über 80 % von M·g, jede Zelle im Zellmodell bei 52,4 % der statischen Zelllast.
Bei der Referenz liegen alle drei im Kontaktast.

---

## A8 · Kritische Werte und Fehlalarmraten

**Kritische Werte** c = t(1 − α/(s·m); ν), α = 0,05; für H1 und H1Z ist das der Bonferroni-Wert c_B,
Planungswert vor Teil B und Vergleichswert (konfirmatorisch gilt das simulierte Quantil, §8.4):

| Familie | m | Art | ν → ∞ | ν = 9 | ν = 19 | ν = 29 |
|---|---|---|---|---|---|---|
| H1 (und H1′): 21 Punkte × (F_min − ⟨N⟩, Re/Im N₁, N₂, N₃) | 147 | zweiseitig | 3,583 | 5,586 | 4,356 | 4,060 |
| H3: 3 Module × 3 Harmonische × (Re, Im) | 18 | zweiseitig | 2,991 | 4,075 | 3,435 | 3,269 |
| H4: höchstens 21 + 2 Konfigurationen | 23 | einseitig | 2,852 | 3,780 | 3,236 | 3,094 |
| H1Z: 3 Zellen × 21 Punkte × (F_min,c − ⟨N_c⟩, Re/Im N_c,1, N_c,2, N_c,3) | 441 | zweiseitig | 3,860 | 6,485 | 4,842 | 4,460 |

Bonferroni ist bei korrelierten Größen konservativ (für H1 und H1Z deshalb §8.4). Jede Hypothese wird mit
α = 0,05 entschieden; die Wahrscheinlichkeit, mindestens eine der beiden Primärhypothesen fälschlich zu
verwerfen, ist höchstens 0,10, über H1–H4 und H1Z höchstens 0,25 (Bonferroni-Schranke). Wegen der großen
t-Quantile bei wenigen Freiheitsgraden sind etwa 20 gültige Läufe je Konfiguration zweckmäßig; die Zahl
folgt aus §5.4. Die Spalten ν = 9, 19, 29 sind Beispiele (n_min = 10, 20, 30).

**Warum ein Äquivalenztest.** „Alle 147 Größen stimmen überein“ ist eine Schnittmenge von Einzelaussagen.
Nach dem Intersection-Union-Prinzip hält die Bestätigung das Niveau α, wenn jede Einzelaussage auf dem Niveau
α geprüft wird; eine Mehrfachkorrektur ist dafür nicht nötig. Je Test genügt deshalb ein TOST auf α = 0,05,
also das Intervall r ± t_eq·u_c in ±Δ_q (PB1, §8.5). Die Fassung vom 25.09.2026 verlangte Intervalle
r ± c·u_c mit dem Bonferroni-Wert und zusätzlich, dass kein |z| > c ist. Am Rand der Äquivalenzzone bestätigte
ein Test damit fälschlich mit Φ(−3,583) = 1,7·10⁻⁴ statt mit 0,05 (ν → ∞), also etwa 300-fach strenger als
nötig. Die Zusatzbedingung machte die Bestätigung zur Nicht-Ablehnung: Bei einer wahren Abweichung δ mit
0 < |δ| < Δ_q geht die Wahrscheinlichkeit für „kein |z| > c“ mit u_c → 0 gegen null; eine präzisere
Apparatur hätte seltener bestätigt. Mit dem Äquivalenztest geht die Bestätigungswahrscheinlichkeit in diesem
Fall gegen eins. Eine reine Power-Bedingung ((c + 1,645)·u_c ≤ Δ und kein |z| > c; 1,645 = z₀,₉₅) ersetzt den
Äquivalenztest nicht: Die Vertrauensgrenze der Abweichung könnte bei ν → ∞ bis 1,371·Δ reichen.
Aus demselben Grund werden H2 und H3 nach Äquivalenzlogik entschieden (Arbeitsfestlegung des Autors vom 3. Oktober
2026, §9.3). Ihre frühere Bestätigung bei 0 im Intervall (H2) bzw. ohne |z| > c (H3), zusammen mit einer
Präzisionsbedingung, war ebenfalls eine Nicht-Ablehnung: Bei hoher Präzision falsifizierte schon eine kleine,
irrelevante Abweichung. H3 prüft je Test das Intervall r ± t_eq·u_c gegen ±δ_H3·|N̂_k⁽ʲ⁾| (PB3) wie PB1. H2
behält die 95-%-Intervalle von §8.6 (je Seite 2,5 % statt 5 % wie im TOST), weil die Überdeckungsschwelle 0,936
und die Verbreiterungsstufen 0,96–0,99 für 95 % gebaut sind und der Perzentil-Bootstrap bei kleinem n eher zu eng
ist. δ_H2 und δ_H3 sind offen (Testvarianten 1° bzw. 10 %, §12).

**Auslegungsgrenze.** Notwendig für PB1 ist u_c < Δ_q/t_eq je Test. PB1 verlangt 147 Intervalle gegen ŷ⁰ und
147 gegen ŷ¹. Für eine Bestätigungswahrscheinlichkeit von 0,8 bei exakter Superposition und 294 unabhängigen
Intervallen muss jedes mit 0,8^(1/294) = 0,99924 bestehen. Das verlangt Δ_q/u_c ≥ 5,012 für ν → ∞
(geschlossen: t_eq + Φ⁻¹((1 + 0,8^(1/294))/2)) bzw. 5,208 für ν = 19 (numerisch, mit χ²-verteiltem Schätzer von
u_c). Gegen eine Vorhersage allein (147 Intervalle, 0,8^(1/147) = 0,99848) wären es 4,816 bzw. 5,004; mit
dieser Grenze bestätigt die Regel gegen beide Vorhersagen nur mit etwa 0,64 bei unabhängigen und 0,65 bei
mit 0,5 korrelierten Residuen r⁰, r¹ desselben Tests (ν → ∞). Die Korrelation, etwa über die gemeinsame
Messseite, senkt die Grenze kaum: bei 0,5 auf 5,007. Nach der Fassung vom 25.09.2026, ebenfalls für 147
Intervalle gerechnet, wären es 6,754 bzw. 8,320 gewesen. Korrelierte Tests bestehen gemeinsam leichter; die
Grenze ist eine Auslegungshilfe, maßgeblich ist die Planungssimulation (§5.4). Gerechnet wird mit derselben
Bandbegrenzung wie die Messung (Beispiel: A4). Die Grenze gilt für H1 allein; die Laufzahlplanung von §5.4 strebt
gemeinsam P(H1 und H2 bestätigt | exakt) ≥ 0,8 an (Prüfung mit Werkzeug 8, A9.11). Weil diese Wahrscheinlichkeit
höchstens P(H1 bestätigt | exakt) ist, kann die gemeinsame Bedingung ein kleineres u_c und damit mehr Läufe
verlangen als diese Grenze.

**Welche Größe bindet; D für N_k.** Für F_min − ⟨N⟩ ist D die Spannweite über den Schnitt. Für N_k begrenzt
der Kammfaktor |1 + e^{−ikφ₂} + e^{−ik·240°}|/3 den Betrag |N̂_k| auf dem Schnitt: höchstens 0,116 für k = 1 und
0,228 für k = 2; für k = 3 liegt er zwischen 0,882 und 1. Lauf-zu-Lauf-Streuung, die je Modul proportional zu
dessen Antwort ist, streut N_k dagegen mit der vollen Einzelmodulamplitude. Unter solcher Streuung können
deshalb Re und Im N₁ die Bestätigung binden, bei rein additivem Sensorrauschen eher F_min − ⟨N⟩. Für Re und Im
N_k gilt Fassung B von D (§8.5; Arbeitsfestlegung, §12): der Durchmesser der vorhergesagten Zeigermenge über den
Schnitt, analog zur Spannweite bei F_min. Im Beispiel A4 (starr, μ = 0,4, 10 Hz) ist Δ_q für N₁, N₂, N₃ in Fassung B
0,2218, 0,1374 und 0,0799 N, in Fassung A (D = max_i |N̂_k,i|, Sensitivitätsanalyse, A9.9) 0,1126, 0,0731 und
0,1383 N. Grund der Wahl: Fassung B gibt allen 147 Größen dieselbe Bedeutung, ein Viertel der Änderung entlang des
Schnitts. Fassung A behandelt die Harmonischen ungleich (Toleranz im Beispiel 12,7, 13,3 und 43,3 % der Änderung für
N₁, N₂, N₃, Z) und lässt unter Lauf-zu-Lauf-Streuung je Modul Re und Im N₁ die Laufzahl stärker treiben (im Beispiel
etwa halbe Grenze). Preis: Fassung B ist bei N₃ strenger, dessen Betrag auf dem Schnitt überwiegend nicht von der
Phase abhängt. Die Auslegungsgrenze u_c ≤ Δ_q/5,012 ergibt im Beispiel für N₁, N₂, N₃ 0,0443, 0,0274 und 0,0159 N,
gegen 0,0258 N für F_min − ⟨N⟩ (ν → ∞, Z); welche Größe bindet, hängt vom Rauschmodell ab. Fassung B bleibt auch,
wenn die Grenze von N₃ bindet; dann werden die nötige Präzision und Laufzahl in der Planungssimulation geprüft
(§5.4, A9.11). Ein Wechsel zu Fassung A ist nicht vorgesehen.

**Mindesteffekt und Disjunktheit.** „Relevant abweichend“ verlangt an einem Test |r| > Δ_rel + c·u_c,
„äquivalent“ an jedem Test |r| ≤ Δ_q − t_eq·u_c, jeweils gegen beide Vorhersagen. Mit Δ_rel = Δ_q (Regel unten)
schließen sich beide aus. |r| − c·u_c ist eine untere simultane Vertrauensgrenze von |δ|. Liegt jede wahre Abweichung
höchstens bei Δ_rel, ist die Rate falscher Falsifikation deshalb näherungsweise höchstens die Rate von
„mindestens ein |z⁰| > c“ bei exakter Superposition, also 0,05; die Kalibriersimulation prüft das (A9.11).
Nachgewiesene, aber nicht nachweislich relevante Abweichungen werden als Zusatz berichtet (§9.3): neben
„bestätigt“ „Abweichung nachgewiesen, innerhalb der Äquivalenzgrenze“, neben „nicht entscheidbar“ „Abweichung
nachgewiesen, Relevanz offen“, je mit den Vertrauensgrenzen der größten Abweichung. Neben „nicht entscheidbar“
ist die Abweichung nur nicht nachweislich größer als Δ_rel und kann darüber liegen. Bei H2 ist δ_H2 Äquivalenz-
und Relevanzgrenze zugleich, bei H3 ist die Relevanzgrenze mindestens δ_H3·|N̂_k⁽ʲ⁾| (offen, §12); auch dort
schließen sich „bestätigt“ und „falsifiziert“ aus.

**Regel für Δ_rel (Arbeitsfestlegung, §12).** Δ_rel,q = Δ_q für jede Größe q (Arbeitsfestlegung des Autors vom 4.
Oktober 2026, A0). Das ist der kleinste Wert, mit dem sich „äquivalent“ und „relevant abweichend“ ausschließen, ohne
weiteren freien Faktor; Δ_rel ändert die Bestätigung nicht. „Relevant“ bedeutet dasselbe wie die Äquivalenzgrenze,
ein Viertel der vorhergesagten Struktur. Abweichungen zwischen Δ_q − t_eq·u_c und Δ_q + c·u_c bleiben nicht
entscheidbar. Nicht gewählt: κ·Δ_q mit κ > 1 (mehr „nicht entscheidbar“ auch bei genau gemessenen Abweichungen) und
max(Δ_q; Δ_phys,q) (verlangt eine vorab benannte Alternative mit Modell; im steifen Aufbau gleich Δ_q). Einwand: Δ_q
ist ein Auflösungs-, kein physikalisches Relevanzkriterium. Antwort: Eine Falsifikation sagt nur, dass die
Superposition über die registrierte Toleranz hinaus verletzt ist. Ob Apparatur oder Physik, klären Zuordnung und E3
(§8.10), soweit sie es können; im steifen Aufbau überwiegt die Apparatur (§2). In den Sensitivitätsanalysen (Faktor
0,1; Fassung A) gilt ebenso Δ_rel,q = Δ_q (A9.9).

**Aufnahmeschwelle für V.** Bei n_min = 20 ist (c₄ + 1,645)·u_c,erw = 4,881·u_c,erw, für ν → ∞
4,497·u_c,erw. Liegt der wahre Wert an der Schwelle, bestätigt ein Punkt ein zutreffendes Vorzeichen mit
etwa 93 % (n_min = 20, nichtzentrale t-Verteilung) bzw. 95 % (ν → ∞); 23 unabhängige Punkte an der Schwelle
bestätigen es zusammen nur mit etwa 0,20. Die Bestätigungswahrscheinlichkeit von H4 wird deshalb in der
Planungssimulation bestimmt und in Teil B berichtet; sie ist keine Bedingung.

**Kritischer Wert aus der gemeinsamen Nullverteilung.** Die 147 Größen sind korreliert; Bonferroni ist dann
konservativ. Das 95-%-Quantil von max|z⁰| aus der Kalibriersimulation hält die Rate „mindestens ein |z⁰| > c“
bei exakter Superposition bei 0,05 und gilt in beide Richtungen, auch wenn es unter c_B liegt. Die
UND-Verknüpfung mit z¹ senkt die Rate weiter. Der Monte-Carlo-Standardfehler einer Rate 0,05 aus 1000
Kampagnen ist 0,0069. Die Rate der Prüfsimulation streut zusätzlich, weil c selbst aus 1000 Kampagnen
geschätzt ist; beide Fehler zusammen ergeben 0,0097. Die Prüfschwelle 0,05 plus zwei Standardfehler beträgt
deshalb 0,069 (§8.4). Eine Schwelle mit nur dem Fehler der Prüfung (0,064) würde bei korrektem Verfahren in
etwa 8 % der Fälle überschritten.

**Fehlalarme bei korrekter Funktion.** Annahmen: ⟨N⟩ aller Laufarten normalverteilt mit derselben
Streuung, keine Drift, σ̂_ref aus 42 gleich getakteten Referenzläufen (leave-one-out). Die Angaben zu S1
und S3 sind obere Schranken, keine Raten des Verfahrens.

- **G1:** je Lauf höchstens 1,5 % (ungünstigste Lage: Interpolation ganz auf einen Referenzlauf), 0,61 %
  mittig zwischen zwei Referenzläufen (Monte Carlo über die Streuung von σ̂_ref).
- **S1 über G1:** Der erste Lauf wird mit der ungünstigsten Lage angesetzt, die Wiederholung liegt mittig
  zwischen den frischen Referenzläufen R₂ und R₃; beide Prüfungen sind bei gegebenem σ̂_ref unabhängig. Die
  Vorprüfung wird nicht berücksichtigt; sie senkt die Rate nur. Schranke je Lauf: 2,5·10⁻⁴.
- **S1 über Nullpunktalarme:** Alarm und Wiederholung teilen den vorangehenden Referenzlauf und sind
  deshalb korreliert. Schranke je Referenzlauf und Kanal: 7,3·10⁻⁴ (Monte Carlo); vier Kanäle (Summe und
  drei Zellen).
- **S1 über eine Kampagne:** Bei 20 Blöcken mit 23 Konfigurationen und drei
  Identifizierbarkeitskonfigurationen an einem Messtag sind es ohne Aufwärm- und Wiederholungsläufe 688
  Läufe: 520 Kombinations-, 126 Einzelmodul- und 42 Referenzläufe (21 in den Kontrollsätzen, 20 in der
  Blockmitte, ein Schlussreferenzlauf), 21 Kontrollsätze aus je sieben Läufen. Bonferroni-Schranke:
  646·2,5·10⁻⁴ + 42·4·7,3·10⁻⁴ ≈ 0,28. Ohne Identifizierbarkeitsläufe (Kontrollsätze aus vier Läufen) wären
  es 565 Läufe (460, 63, 42) und 523·2,5·10⁻⁴ + 42·4·7,3·10⁻⁴ ≈ 0,25. Allgemein sind es (N_K + N_I + 8)·n +
  8·d Läufe; jeder weitere Messtag bringt einen Kontrollsatz und einen Schlussreferenzlauf und erhöht die
  Schranke um 6·2,5·10⁻⁴ + 2·4·7,3·10⁻⁴ ≈ 0,007. Aufwärmläufe tragen nichts bei (A9.12); Wiederholungen
  erhöhen die Schranke je Lauf wie oben.
- **S3:** Die Statistik (x − x̄₀)/(s·√(1 + 1/n₀ⱼ)) ist t-verteilt mit n₀ⱼ − 1 Freiheitsgraden; mit
  c_S = t(1 − 0,05/42; n₀ⱼ − 1) (bei n₀ⱼ = 20: 3,503) löst ein Kontrollsatz über die 21 Größen mit höchstens
  5 % aus (Bonferroni-Schranke, exakt je Größe). Reproduktion durch die sofortige Wiederholung: höchstens
  9,5·10⁻⁴ je Kontrollsatz (Bonferroni über 21 Größen; der Summand je Größe per Monte Carlo, weil erste
  Messung und Wiederholung dasselbe Phase-0-Mittel teilen). Über die 21 Kontrollsätze einer solchen Kampagne
  höchstens 0,020.
- **Aufwärmen:** Ohne Drift bleibt das Kriterium (§6) nach zehn Referenzläufen mit etwa 6·10⁻⁴ unerfüllt.

---

## A9 · Verfahren im Einzelnen

### A9.1 Aufbau

- **Kanäle.** Drei Wägezellen im Dreieck, optischer Wegkanal (Phase 0: Weg der bewegten Masse relativ zum
  Rahmen; Phase 1: Einfederung des Körpers), drei Phasenencoder mit Indeximpuls, Beschleunigungssensor am
  Rahmen, Blindkanal (Brücke aus Festwiderständen am gleichen Verstärkertyp, gleicher Kabelweg; zeigt die
  Einstreuung unter echter Motorlast), Temperaturfühler an jeder Zelle und jedem Antrieb. Ein Sinusprofil
  liefert ohne Liftoff keine Schiefe; das Profil braucht eine Nocke oder einen programmierbaren Aktuator.
- **Lagerung und Kabel.** Füße lateral entkoppelt auf den Zellen (kinematische Lagerung, etwa
  Kugel–Kegel, Kugel–Kerbe, Kugel–Ebene). Alle Kabel laufen vom Körper in einer weichen, festgelegten
  Schlaufe mit Zugentlastung zum Unterbau; die Führung wird fotografisch dokumentiert und bleibt bis zum
  Ende von Phase 1 unverändert.
- **Messkette.** Feste Verstärkung; keine Softwarefilter, automatische Nullpunktnachführung,
  Stillstandserkennung, adaptive Filter oder Bereichsumschaltung; analoge Anti-Aliasing-Filter gleicher
  Bauart in allen Kraftkanälen. Die Einstellungen stehen in Teil B und in den Metadaten jedes Laufs.
  *Begründung:* Median- und Stillstandsfilter liefern einen formabhängigen Lagewert, kein Zeitmittel.
  Für den Median gilt Median(N) − ⟨N⟩ = s_N·med(u) mit u = (N − ⟨N⟩)/s_N und s_N der
  Standardabweichung von N über einen Zyklus. Beim Egg-Profil (Einzelmodul, starre Auflage) ist
  med(u) = −0,368 bei γ₁ = +0,755. Ein solcher Anzeigewert weicht damit schon bei s_N = 0,54–1,36 %
  von M·g um 0,2–0,5 % vom Mittel ab, in der Größe der Zielauflösung von v1. Beim Sinus verschwindet
  der Versatz, bei umgekehrtem Vorzeichen der Kraftabweichung kehrt er sich um; er erzeugt damit die
  Signatur eines phasenabhängigen Mittelwerteffekts, obwohl ⟨N⟩ = M·g gilt. Nachträglich korrigieren
  lässt er sich nicht: Die Momentennäherung −γ₁·s_N/6 unterschätzt ihn um den Faktor 2,9.
- **Zeitbasis.** Gemeinsame Zeitbasis aller Kanäle; Kraftkanäle gleichzeitig abgetastet oder mit bekanntem,
  korrigiertem Kanalversatz. Die Indeximpulse stempelt ein Zeitgeber derselben Zeitbasis; die Quantisierung
  360°·f/f_clk beträgt höchstens 0,01° (bei 10 Hz f_clk ≥ 360 kHz).

### A9.2 Phase 0

- **P0.1** Jede Zelle einzeln und eingebaut mit rückgeführten Gewichtsstücken, auf- und absteigend;
  Orientierung: DKD-R 3-3 „Kalibrierung von Kraftmessgeräten“, Revision 1 (DOI 10.7795/550.20250130);
  DKD-R sind Richtlinien, keine Normen. Nullpunkt je Zelle bei abgehobenem Körper (Hubvorrichtung,
  reproduzierbare Wiederauflage). Gewichtsstück an mindestens fünf Stellen bekannter Lage (Lehre; Mitte,
  über jeder Zelle, über den Modulachsen); bekannte Horizontalkraft in zwei Richtungen. Elektronik mit
  Brückensimulator: zwei Signale mit verschiedenen Harmonischen einzeln und als Summe. Ergebnis: Kennlinie,
  Linearitäts- und Umkehrspanne, Kriechen, Kalibrierunsicherheit, Nullpunkt je Zelle; Zelllagen in der
  Ebene und relative Zellverstärkungen mit Unsicherheit (Ziel ≤ 0,1 mm bzw. ≤ 0,1 %), Eingang von T(kω) für
  E3 (A2.7); Einfluss von Laststelle und Querkraft je ≤ 0,1·Δ_q, Superpositionsfehler der Elektronik
  ≤ 0,3·u_c,erw (Nachweis in Teil B; §5.2; Nachweisform, Folge und lineare Schwelle offen, §12).
- **P0.2** Wägung vor der Endmontage. m_j: bewegte Masse jedes Moduls einschließlich mitbewegter Kabel und
  Messmarken, durch Bauteilwägung; der konventionelle Wägewert genügt (Abweichung von der wahren Masse
  höchstens etwa 10⁻³ relativ, klein gegen PB3). M = Σ_c F_c,stat/g (Konvention b, Arbeitsfestlegung, §12) mit
  F_c,stat der Anzeige der Zelle c bei aufgesetztem, ruhendem Körper mit geparkten Modulen gegen den Nullpunkt bei
  abgehobenem Körper (P0.1), dazu Luftdruck, Lufttemperatur und Feuchte. Die Zellen sind in N kalibriert (P0.1); g
  ist der örtlich bestimmte Wert [Teil B], derselbe für die Gewichtskräfte der Kalibrierung, für M und für alle
  Kräfte. Das Gewicht M·g ist die statische Last im Zustand bei P0.2; Auftrieb, Innenluft und gleichbleibende äußere
  Kräfte sind darin enthalten, von M = Σ_c F_c,stat/g wird kein Auftrieb abgezogen. Die träge Masse ist M + m_L mit
  m_L = ρ_L·V_außen + m_hyd (A1); statische Nebenkräfte (Kabel, Ladung) gehen mit F/g in M und damit in die träge
  Masse ein. Ist eine geeignete Waage verfügbar, wird der geschlossene Körper bei P0.2 und gleichem Luftzustand auf
  ihr gewogen und beschreibend mit M verglichen. Zeigt die Waage nach Justierung mit Stahlgewichten Masseeinheiten
  an, wird ihre Anzeige mit (1 − ρ_L/(8000 kg/m³)) multipliziert, einem Skalenfaktor der Kalibrierung, keinem Auftrieb
  des Körpers (Z); die Differenz zeigt die Summe aus statischen Nebenkräften und Kalibrierunterschied. Sonst nennt
  Teil B den Verzicht mit Grund. M gilt für den Zustand bei P0.2; Endmontage, Kabelführung und Messmarken ändern die
  statische Last danach noch, die Wiederholung des Zellnullpunkts nach dem Datenschluss (§5.2) ergibt eine zweite
  Bestimmung, die nur beschreibend berichtet wird. Nicht gewählt ist Konvention (a), M als Summe der wahren Massen
  aller Teile ohne Luft; sie verlangte, die konventionellen Wägewerte m·(1 − ρ_L/ρ_Mat + ρ_L/(8000 kg/m³)) einer mit
  Stahlgewichten justierten Waage mit der Werkstoffdichte jedes Teils auf wahre Massen umzurechnen, sonst würde der
  Materialauftrieb zum Teil doppelt abgezogen (Z).
- **P0.3** D1; D2ⱼ für jeden Antrieb bei jeder Frequenz des 1-Hz-Rasters im Bereich (d); D2_K an den Punkten
  I in deren Sollphasung bei denselben Frequenzen. Wechselwirkung der Antriebe: D2_K − Σⱼ D2ⱼ·e^{−ikφⱼ} je
  Harmonischer, ausgewertet bei f mit k_max, in N und je Zelle, ≤ 0,3·u_c,erw (§5.2; Fassung von D2_K offen,
  §12). Statische Summe und
  Umkehrspanne mit der Kabelschlaufe in Soll- und in einer zweiten Lage; statischer Nebenschlusseinfluss
  ≤ 0,1·Δ_q, Umkehrspanne ≤ 0,3·u_c,erw (§5.2; Nachweisform, Folge und lineare Schwelle offen, §12). Spalt
  zwischen Körperboden und Unterlage dokumentiert. Ist er
  kleiner als 10 mm und die Grundplatte geschlossen (§5.1), zusätzlich Einzelmodulläufe je Modul bei der
  Sollhöhe und einer zweiten Spalthöhe (Spaltvariation); die Änderung von N_k ist linear und muss
  ≤ 0,1·Δ_q sein, die von ⟨N⟩ wird berichtet.
- **Endmontage.** Zeitpunkt protokolliert, Fotos. Danach bis zum Datenschluss kein Abheben des Körpers,
  kein Lösen von Massen, Kabeln oder Encodern. Nicht als Veränderung zählen das Ausrichten des
  berührungslosen Wegkanals zwischen P0.5 und Phase 1, das Ankoppeln und Lösen der Anregung in P0.4, auch
  für die Betriebslastprüfung nach P0.9 (Zeitpunkt offen, §12), und für P0.5 angebrachte Messmarken, die bis zum
  Datenschluss
  bleiben; falls vorgesehen (offen, §12), auch die Umschaltung auf einen vor der Endmontage eingebauten
  zweiten Nockensatz ohne Lösen von Massen, Kabeln oder Encodern. Bei Randomisierung nach §6 wäre sie in
  Phase 1 im Mittel etwa neunmal je Block nötig (N_K = 23, N_I = 3), bei n = 20 etwa 190-mal; ihre
  Wiederholbarkeit weist P0.5′ nach.
- **P0.4** Komplexe Übertragungsfunktion je Zelle und der Summe mit Impulshammer oder Shaker, Module
  geparkt, auf der gemeinsamen Zeitbasis bis zur Grenzfrequenz der Anti-Aliasing-Filter; Anregung in der
  Mitte und an mindestens zwei exzentrischen Orten über Modulpositionen, damit Kippmoden und T(kω) sichtbar
  werden; Wiederholung mit doppelter Anregungsamplitude (Linearität: beide gleich innerhalb der
  Unsicherheit). Orientierung: DKD-R 3-10 Blatt 1 „Dynamische Kalibrierung von einachsig beanspruchten
  Kraftmessgeräten und Prüfmaschinen (Grundlagen)“ (DOI 10.7795/550.20240404) und Blatt 2 (Sinusverfahren,
  Ausgabe 2019). Ergebnis: K, C, f_n, ζ aus der Anpassung des 1-FG-Modells an die komplexe
  Übertragungsfunktion in einem festgelegten Frequenzband, gewichtet mit der Kohärenz (Verfahren im
  eingefrorenen Code), alle in N oder N_c sichtbaren Moden f_m, ζ_m, Übertragung der Kraftkette G_F(ω) je
  Zelle und Summe. **Betriebslastprüfung (unter Betriebslast).** Zeitpunkt: nach P0.9, weil die Last von f
  abhängt (offen, §12: Zeile „Schwelle des Klirrkriteriums und von P0.12“); bei zweiter Frequenz auch bei
  Einstellung 2. Das Ergebnis wird vor P0.11 hinterlegt wie das von
  P0.12; es ist keine Eingangsgröße der Vorhersagen. Sinusanregung bei f, 2f und 3f, je einzeln, Module
  geparkt, nacheinander über jeder der drei Modulpositionen. Die Kraftamplitude ist die Betriebslast je
  Zelle: die größte vorhergesagte Harmonische der Zellkraft bei der Anregungsfrequenz in den Kombinations-
  und Einzelmodulläufen bei f, aus den Einzelmodulläufen der Phase 0 mit der Superposition je Zelle; jede
  Zelle erreicht sie bei mindestens einer Anregungsposition. Eine mittige Anregung in Höhe der Harmonischen
  der Summe genügt nicht: Bei Harmonischen, deren Ordnung kein Vielfaches von 3 ist, ist die Summe auf dem
  Schnitt klein gegen die Zellkräfte. Im Beispiel A4 mit Modulen über den Zellen trägt jede Zelle bei f die
  Einzelmodul-Harmonische 1,30 N (bei 2f 0,43 N, bei 3f 0,18 N), während |N₁| auf dem Schnitt höchstens
  0,45 N beträgt; mittig angeregt bekäme jede Zelle etwa 0,15 N, ein Neuntel ihrer Last. Klirrkriterium:
  Schein-Oberwellen bei der 2- und 3-fachen Anregungsfrequenz, soweit ≤ k_max·f, in N und je Zelle
  ≤ 0,3·u_c,erw (Schwelle offen, §12). Die Anregung ist klirrarm, ihre Oberwellen liegen also nachweislich
  unter der Schwelle, oder ein Referenzaufnehmer im Kraftpfad misst sie; es zählen nur Oberwellen über die
  der Anregung hinaus. P0.4 prüft Kontakt und Kette zusammen und kann beide nicht trennen.
- **P0.5** Wegkanal auf die bewegte Masse jedes Moduls, Encoderwinkel, bei f über [Teil B] Zyklen:
  x_k⁽ʲ⁾ und a_k⁽ʲ⁾ = −(kω)²·x_k⁽ʲ⁾ bezogen auf den eigenen Indeximpuls; Δδⱼ mit u(Δδⱼ) ≤ 0,1°; Übertragung
  des Wegkanals G_x(ω); Parkposition. Dieselben Größen bei Einstellung 2 (P0.5′); bei einem
  programmierbaren Aktor wird dabei die Profiltreue bei beiden Amplituden nachgewiesen. Bei einem zweiten
  Nockensatz (offen, §12) wird in P0.5′ mindestens fünfmal in jede Richtung umgeschaltet; Kriterium (offen, §12): Δδⱼ
  streut über die Umschaltungen höchstens um u(Δδⱼ), x_k⁽ʲ⁾ höchstens um seine Unsicherheit aus P0.5. Wird
  das verfehlt, ist die Option nicht zulässig, und Einstellung 2 ist eine zweite Frequenz.
- **P0.6** Sollphasen aller Konfigurationen; Wiederholbarkeit des Indeximpulses je Encoder; statischer
  Versatz, Jitter σⱼ.
- **Laufdauer in Phase 0.** Alle Läufe bei einer Frequenz haben dieselbe Dauer, mit Einschwingzeit T_e,P
  und Fenster T_a,P [Teil B]. Ausgewertet werden die ersten ganzen Zyklen der Länge T_a, die T_e nach Ende
  der Rampe beginnen (Kürzen auf die ersten Zyklen); dazu muss T_e + T_a ≤ T_e,P + T_a,P sein.
- **P0.7** Mindestens 42 Referenzläufe, verschachtelt mit P0.8–P0.10 bei jeder gemessenen Frequenz, je einer
  nach zwölf anderen Läufen; σ̂_ref und σ̂_ref,c aus den Läufen bei f.
- **Einstellung 2 (§5.5).** Nach der Wahl von f: P0.5′, dann je Modul n₀′ ≥ 20 Einzelmodulläufe Lⱼ′ (Umfang
  offen, §12),
  verschachtelt mit Referenzläufen wie P0.7. Die P0.5′-Ergebnisse werden hinterlegt, bevor Kraftdaten der
  Lⱼ′ ausgewertet werden. Ergebnis: ŷ⁰′ an den Punkten I, s mit Unsicherheit, die Streuungen für die Planung
  der Zuordnung; Bedingung (a) bei Einstellung 2 mit den eigenen Daten (Folge bei Verfehlen offen, §12).
- **P0.12 Linearitätslauf** (antriebsabhängig, offen, §5.5, §12). Einzelmodulläufe jedes Moduls mit Sinus-
  oder ungerade-harmonischem Profil bei zwei Amplituden im Verhältnis 2 (bei einer Nocke mit nur einem
  Sinussatz über ein Frequenzverhältnis √2; dann wächst eine Kettennichtlinearität vierfach, eine
  Kontaktnichtlinearität stärker), Profil in P0.5 mitgemessen.
  Kriterium: Die geraden Harmonischen k = 2, 4, … ≤ k_max in N und je Zelle, abzüglich G_F·m_j·H·a_k⁽ʲ⁾ aus
  der Profilmessung, betragen höchstens 0,3·u_c,erw (Schwelle offen, §12). Bei Überschreitung wird ihre
  Skalierung mit der
  Amplitude (vierfach bei quadratischer Kennlinie, A2.6) in Teil B berichtet, und das Ergebnis geht als
  Szenario in die Kalibriersimulation ein (Nachweisform und Folge offen, §12).
- **Reihenfolge der Schwellen.** (1) G2–G10 auf die Phase-0-Läufe anwenden, mit σ_tol und σ_Δ aus allen
  Läufen der jeweiligen Art (Median bzw. MAD, G2, G4). (2) ε_ctrl nach §8.8 und A9.8 aus den danach
  gültigen Läufen. (3) G1 anwenden. p̂ ist der Anteil der danach ungültigen Pilotläufe; alle Streuungen
  stammen aus den gültigen Läufen.
- **Frequenzsuche.** (1) f_u und f_zul bestimmen (§5.3; (a) mit dem Auslegungswerkzeug, den Parametern aus
  P0.1–P0.4 und dem Konstruktionsprofil, ohne Zusatzkonfigurationen). (2) Bei f_zul P0.5–P0.8 und P0.10
  ausführen; (a) mit der Superposition je Zelle ohne Bandbegrenzung prüfen; k_max nach §5.4 bestimmen.
  (3) Kandidaten sind die Rasterfrequenzen f_u … f_zul, die (d) und (c) mit der nach dem
  Auslegungswerkzeug auf diese Frequenz skalierten Struktur und den Pilotstreuungen bei f_zul erfüllen.
  (4) Den kleinsten noch nicht geprüften Kandidaten messen (bei f_zul die vorhandenen Daten) und mit diesen
  Daten (a)–(d) prüfen; der erste, der besteht, ist f. (5) Besteht keiner: Befund „kein zulässiger
  Arbeitspunkt“, veröffentlicht; der Aufbau wird überarbeitet. In Teil B gehen nur Werte bei f ein.
- **k_max, T_a und Laufzahl** (§5.4), in dieser Reihenfolge: Für k = k_b, k_b − 1, …, 3 und je k für T_a =
  N_z/f mit N_z = 1, 2, …, solange T_e + T_a ≤ T_e,P + T_a,P: (i) s_q(T_a) aus den Pilotläufen, gekürzt auf
  die ersten N_z Zyklen; (ii) T_e und T_Lauf mit den Moden bis k·f; (iii) Planungssimulation: n₀ ≥ 20 und
  n_min minimieren N_K·n_min + 3·n₀ (Zielfunktion und Laufzahl von H1 offen, §12) unter den
  Bedingungen von §5.4 (gemeinsame Bestätigung von H1 und H2 nach §8.5, §8.6 und §9.3 bei exakter
  Superposition mit Wahrscheinlichkeit ≥ 0,8, Arbeitsfestlegung, §12; n_min ≥ (3·1°/(SNR·δ_H2))², δ_H2 offen,
  §12), bei Gleichstand das kleinere n_min; (iv) Rauschbias b̂_i⁰ mit diesen
  n_min und n₀, b̂_i¹ mit n_min und n + d Kontrollläufen je Modul, jeweils mit Unsicherheit; (v) n = n_min + r
  ≤ n_max (§5.3 c) prüfen. Das erste Paar (k, T_a), das (v) erfüllt, legt k_max, T_a, n_min und n₀ fest.
  Obere 80-%-Vertrauensgrenze einer Streuung s mit ν Freiheitsgraden: s·√(ν/χ²₀,₂(ν)); t-Quantile mit dem
  erwarteten ν_eff; c als c_B. Der Rauschbias berücksichtigt, dass Messkurve und vorhergesagte Summe dreier
  Einzelmodulkurven verschiedene Rauschpegel haben; die Simulation verwendet getrennte Rauschmodelle für
  Einzelmodul- und Kombinationsläufe. Die Faustregel n ≥ (3·1°/(SNR·δ_H2))² gibt die Laufzahl,
  bei der die H2-Halbbreite etwa δ_H2 erreicht (Halbbreite ≈ 3/(SNR·√n) für n₀ = n; Faktor 3: Tabelle F; bei
  der Testvariante δ_H2 = 1° die bisherige Regel n ≥ (3/SNR)²; δ_H2 offen, §12). Für die Bestätigung von H2
  ist das notwendig, nicht hinreichend; maßgeblich bleibt die Planungssimulation.

### A9.3 Inhalt von Teil B

1. alle Ergebnisse von P0.1–P0.10 und gegebenenfalls P0.12 mit Unsicherheiten, die SHA-256-Prüfsummen
   aller Rohdaten der Phase 0 und der Pilotläufe und die Commit-Hashes des verwendeten Codes;
2. die Werte aller Platzhalter: Parkposition und Δ_park; Kanalliste, Abtastrate, Auflösung, Verstärker-
   und Filtereinstellungen; Zyklenzahl der Profilmessung; Δδⱼ; f_u, f_zul, f, k_max; T_warm, T_park,
   T_ramp, T_e, T_e,P, T_a, T_a,P, T_ab, T_Lauf; σ_tol, δf_tol; T_P0, TK_C, ΔT; σ̂_ref, σ̂_ref,c, ε_ctrl
   (mit Prüfgröße, kritischem Wert und gegebenenfalls σ̂_betr), σ_c, σ_Σ, F_LO; σ_Δ; n₀, n_min, r, n, n_max,
   d; T_verfügbar; Einstellung 2 (Amplitude oder Frequenz), s, I, N_I, n₀′; Spalt; g (örtlich bestimmt), V_außen
   und m_hyd (für m_L), Ergebnis der Gesamtwägung oder begründeter Verzicht (A9.2);
3. die Einzelmodul-Mittelkurven N̄⁽ʲ⁾(θ), gesamt und je Zelle, mit ihren Bootstrap-Replikaten als Datei;
   zusammen mit dem registrierten Code legen sie die Vorhersage für jede gemessene Phasenlage fest;
4. die Vorhersage bei den Sollphasen und dem Jitter aus P0.6: F̂_min − N_s, N̂_k (k = 1 … 3), γ̂₁, Â, F̂_max
   je Konfiguration mit Unsicherheit; D_q als Punktwert aus ŷ⁰ (für Re und Im N_k Fassung B, für die
   Sensitivitätsanalyse auch Fassung A), Δ_q = 0,25·D_q (Sensitivitätsvariante 0,1·D_q) und Δ_rel,q = Δ_q; der
   Rauschbias b̂_i⁰ und b̂_i¹ mit Unsicherheit; u_c,erw je Größe und die daraus folgenden Schwellen (§5.2, G7); zum
   Vergleich die Vorhersage des Auslegungswerkzeugs mit den Parametern aus P0.1–P0.5; für H1Z je Zelle die
   Vorhersage, Δ_c,q, Δ_c,rel,q und den Rauschbias; ŷ⁰′ an den Punkten I;
5. für E3 die Übertragungsmatrix T(kω) mit Zelllagen und Zellverstärkungen aus P0.1 und ihrer
   Unsicherheit; die Ergebnisse von D2_K, des Klirrkriteriums, gegebenenfalls von P0.12 und der
   Spaltvariation;
6. die vorhergesagte Spitzenlage φ̂₂*, das Fitfenster W, die erwartete Halbbreite und das SNR;
7. die H3-Vorhersage und je Harmonischer die Angabe, ob sie den Kontakt prüft; ein Vergleich mit gemessenen
   Einzelmodul-Harmonischen wird vor dem Datenschluss nicht berechnet;
8. die Prüfmenge V und die Entscheidung über Zusatzkonfigurationen und gespiegelten Schnitt;
9. die Laufreihenfolge;
10. die Ergebnisse der Planungs- und Kalibriersimulation, auch die gemeinsame Bestätigungswahrscheinlichkeit
    von H1 und H2 bei exakter Superposition (§5.4), die Bestätigungswahrscheinlichkeit von H4 und H1Z, den
    kritischen Wert für ε_ctrl, die kritischen Werte c von H1 und H1Z mit der Prüfrate (§8.4), den
    Intervalltyp von H2 mit simulierter Überdeckung, gegebenenfalls mit Nominalniveau (§8.6), die
    Trefferquote der Zuordnung, die Fehlalarmrate und die Raten „unauffällig“ und „unbestimmt“ von E3 und
    die daraus folgende Fassung von E3 (dreiwertig oder nur beschreibend, A9.11);
11. eine Erklärung, welche Daten und Auswertungen bei der Registrierung vorlagen und wer welche Ausgaben
    gesehen hat;
12. die Einträge des Abweichungsprotokolls bis zu diesem Zeitpunkt.

### A9.4 Verarbeitungskette

Für alle Laufarten (Kombination, Identifizierbarkeitslauf, Lⱼ, Lⱼ′, R, D2) identisch: (1) Rohdaten
schreibgeschützt; Umrechnung mit der statischen Kalibrierung je Zelle; N = N₁ + N₂ + N₃. (2) Keine
Softwarefilter. (3) Segmentierung am Indeximpuls (θ, A1); nur Zyklen, die vollständig im Auswertefenster
liegen. (4) Resampling jedes Zyklus auf N_θ = 2000 äquidistante Stützstellen durch lineare Interpolation.
(5) Mittelkurve je Lauf; DFT; Koeffizienten oberhalb k_max null. (6) Je Lauf N_k, ⟨N⟩, γ₁, φ̄ⱼ, σⱼ,
zyklusweise Phasenzeiger; dieselben Größen je Zelle. (7) Je Konfiguration Konfigurationsmittelkurve und
daraus F_min − ⟨N⟩, N_k, γ₁, F_max, A, dieselben Größen je Zelle. (8) Für E3 je Konfiguration die
Modulzeiger Ĉⱼ,ₖ (k = 1, 2) aus den gemittelten Zellzeigern (A9.13). Die Schritte 3–5 und die Mittelung
über Läufe sind linear und vertauschen mit der Summe über Module; die Superposition bleibt deshalb
erhalten, wenn Einzelmodul- und Kombinationsläufe identisch verarbeitet werden.

### A9.5 Bootstrap und Freiheitsgrade

B = 10 000 Replikate je Anteil. **A (Messung):** Läufe der Konfiguration mit Zurücklegen ziehen, mit ihren
Phasenzeigern; ȳ, ρⱼₖ und ŷ neu berechnen, r bilden. **B (Vorhersage):** Einzelmodulläufe jedes Moduls mit
Zurücklegen ziehen (Phase 0 für ŷ⁰, Phase-1-Kontrollläufe für ŷ¹), ρⱼₖ fest; r bilden. u_c² = Var_A +
Var_B, für lineare und nichtlineare Größen gleich. Ein eigener Phasenterm entfällt, weil die Vorhersage mit
den gemessenen Zeigern derselben Läufe gebildet wird. Für F_min − ⟨N⟩ wird r⁰ um b̂_i⁰ und r¹ um b̂_i¹
korrigiert, und u_c² = Var_A + Var_B + u²(b̂_i) mit dem jeweiligen b̂_i. u(b̂_i) kombiniert quadratisch den
Monte-Carlo-Fehler und die halbe Spannweite von b̂_i über die in Teil B festgelegten Rauschmodelle (Festlegung
in Teil B oder als Liste in Teil A offen, §12), diese als
Rechteckverteilung (geteilt durch √3). ν_eff nach §8.3: n_A = gültige Läufe der Konfiguration (H3: gültige
Phase-1-Kontrollläufe des Moduls), n_B = min_j der gültigen Einzelmodulläufe der jeweiligen Basis, Monte Carlo
mit ν = ∞, also ν_eff = (n_A − 1)·u_c⁴/Var_A² in H3. H1Z, die Zuordnung und E3 verwenden dieselben
Replikate; bei Einstellung 2 treten Lⱼ′ an die Stelle der Lⱼ.

### A9.6 Zeltfit

Schätzer wie §8.6 (offen, §12): φ* wird in Schritten von 0,001° über [min W, max W] gesucht; für jedes φ* werden
F*, s_L, s_R ungewichtet
nach der Methode der kleinsten Quadrate bestimmt; gewählt wird φ* mit der kleinsten Residuenquadratsumme,
bei Gleichstand das kleinste. Fitfenster: Der Mittelpunkt folgt allein aus der Vorhersage in Teil B, nicht aus
φ̂₂*, das erst der Fit in W ergibt. Offen (§12): (i) der Schnittpunkt mit dem größten vorhergesagten
F̂_min − N_s oder (ii) der Schnittpunkt, der dem auf einem Raster von 0,01° über den ganzen Schnitt bestimmten
Maximum von F̂_min − N_s am nächsten liegt; jeweils bei Gleichstand der kleinere. W sind die Schnittpunkte in
[Mittelpunkt − w, Mittelpunkt + w], am
Schnittrand abgeschnitten. w hängt nicht von u_c,erw ab. Vorschlag (offen, §12): w = 6° fest. Alternativen:
w = 8° fest; oder w ist der größte Wert aus {4°, 6°, …, 20°}, für den der Zeltfit an der Vorhersage bei den
Sollphasen die Spitzenlage um höchstens 0,1° gegen das Maximum von F̂_min − N_s verschiebt, das der
registrierte Code auf einem Raster von 0,01° in φ₂ (φ₃ = 240°) innerhalb von W bestimmt. Hat W auf einer
Seite des Mittelpunkts weniger als zwei Punkte, ist H2 nicht entscheidbar (Grund: Datenlage; zu ausgefallenen
Punkten in W: §9.3; offen, §12). Bleibt φ* bei einem nahezu
symmetrischen Zelt auf einem Schnittpunkt hängen, hat Δφ* eine Punktmasse; die Kalibriersimulation prüft
die Überdeckung auch in diesem Fall (A9.11). Abszisse ist die gemessene Profilphase
φ̄₂^P = −arg ρ₂₁ + Δδ₂ (A1). Intervall: In jedem von 10 000 Replikaten werden die Läufe jeder Konfiguration
und die Einzelmodulläufe jedes Moduls mit Zurücklegen gezogen, Abszissen und ρⱼₖ neu gebildet, beide Fits
wiederholt und Δφ* = φ₂*,Messung − φ̂₂* gebildet; [a, b] sind das 2,5- und das 97,5-%-Quantil
(Perzentilintervall), getrennt für ŷ⁰ ([a⁰, b⁰]) und ŷ¹ ([a¹, b¹]). Erreicht die simulierte Überdeckung des
Perzentilintervalls 0,936 nicht, gilt das BCa-Intervall, wenn es 0,936 erreicht; sonst das Perzentilintervall
mit dem kleinsten Nominalniveau aus 0,96, 0,97, 0,98 und 0,99, das 0,936 erreicht (Quantile (1 − Niveau)/2 und
(1 + Niveau)/2). Reicht keines, ist H2 nicht entscheidbar (Grund: Verfahren; §8.6, Teil B; Rückfallkette und
Bezugswert der Überdeckung offen, §12).

### A9.7 Monte-Carlo-Fortpflanzung (H3)

a_k⁽ʲ⁾ = −(kω)²·x_k⁽ʲ⁾ aus P0.5, korrigiert um G_x; G_F ist die komplexe Übertragung der Kraftkette relativ
zur Zeitbasis der Indeximpulse (P0.4); alles bezogen auf den eigenen Indeximpuls und bei der gemessenen
Frequenz. 10 000 Ziehungen aus den Unsicherheiten von K und C (Kovarianz der Anpassung), M + m_L und m_j, x_k⁽ʲ⁾,
G_F, G_x, f und gegebenenfalls der D2-Signatur; K und C folgen je Ziehung aus der Anpassung von P0.4 mit der
gezogenen trägen Masse M + m_L, H(kω) hängt dann nur von f_n und ζ ab, nicht von M (§12). Vorhersage und u(ŷ)
sind Mittelwert und
Standardabweichung von Real- und Imaginärteil. Konfirmatorisch ist H3, weil kein Modellparameter aus
Kraftdaten der Einzelmodulläufe bestimmt wird und die Parameter vor jeder Auswertung dieser Daten
hinterlegt sind (§5.2, je Frequenz). Vor dem Datenschluss wird die Vorhersage nicht mit gemessenen
Einzelmodul-Harmonischen (Phase 0 oder 1) verglichen; der Vergleich mit Phase 0 wird danach berechnet und
berichtet. Eine Bestätigung nach PB3 schließt die starre Auflage nur für eine Harmonische aus, deren
Abstand |N̂_k⁽ʲ⁾ − G_F·m_j·a_k⁽ʲ⁾| größer als Δ = δ_H3·|N̂_k⁽ʲ⁾| ist, deren Kontaktanteil |H(kω) − 1|/|H(kω)|
also δ_H3 übersteigt (Testvariante δ_H3 = 10 %, offen, §12). Im steifen Aufbau trifft das bei 10 % für k ≤ 3
meist auf keine Harmonische zu (Beispiel A4, K = 10⁶ N/m, 10 Hz: Kontaktanteil 0,3 / 1,0 / 2,3 %, Z; der
Betrag weicht um 0,3 / 1,0 / 2,4 % vom starren Wert ab); dann prüft H3 bei ±10 % Masse, Profil und
Kalibrierung. Unabhängig vom Aufbau wird eine Bestätigung bei der Testvariante ±10 % nicht als Bestätigung des
Kontaktgesetzes oder des Kontaktmodells bezeichnet (§8.5, §8.7). Den Kontakt prüfte erst Fassung I oder eine
Grenze unter dem Kontaktanteil (§8.7; Fassung K oder I, offen).

### A9.8 Nullkontrolle

Zusammenfassender Test: Welch-Satterthwaite-t-Test von Δ⟨N⟩ aller Kombinationsläufe gegen Δ⟨N⟩ der
Referenzläufe von Phase 1 (leave-one-out), zweiseitig, α = 0,05; einbezogen sind alle Läufe, die nicht aus
anderen Gründen als G1 ungültig sind. Berichtet werden Differenz, 95-%-Intervall [L, U] und dessen Lage zu
±ε_ctrl mit dem Vermerk „Einzellauftoleranz, keine Äquivalenzgrenze für das Mittel“, dazu genau eine von zwei
Aussagen (Arbeitsfestlegung, §12: Nullkontroll-Sammeltest): bei 0 ∉ [L, U] „Unterschied nachgewiesen“, sonst „kein
Unterschied nachgewiesen, Gleichheit nicht nachgewiesen“. Eine Gleichheitsaussage gibt es nicht; sie bräuchte
eine eigene, vorab begründete Grenze. Die Differenz zweier Referenzläufe streut
√(4/3)-mal so stark wie die Leave-one-out-Statistik
(Varianz 2σ² gegen 1,5σ²); daher die Schwelle 3·√(4/3)·σ̂_ref des Nullpunktalarms. Ein Zellalarm weist auch
auf einen verrutschten Fuß hin. Der Randterm aus der Impulsänderung des Schwerpunkts über das Fenster
(Literaturabgleich §4.2, T3) ist bei ganzen Zyklen im stationären Zustand null; er wird aus Weg- und
Beschleunigungskanal abgeschätzt und berichtet.

**ε_ctrl in Phase 0** (§8.8), nach G2–G10 und vor G1: Jeder gültige Pilot- und Einzelmodullauf an der
relativen Lage β zwischen seinen Referenzläufen ergibt d = Δ⟨N⟩·√(1,5/(1 + β² + (1 − β)²)); bei gleicher
Streuung σ aller Läufe hat d die Varianz 1,5σ² wie die Leave-one-out-Statistik. Prüfgröße ist
F = s_d²/σ̂_ref², s_d die Standardabweichung der d. Kritischer Wert ist das 95-%-Quantil von F in 10 000
simulierten Datensätzen mit derselben Laufanordnung (Lagen β, gemeinsame Referenzläufe) und normalverteiltem
⟨N⟩ gleicher Streuung in allen Laufarten. Liegt F darüber, gilt ε_ctrl = 3·σ̂_betr mit σ̂_betr = s_d. Ein
F-Test mit nominellen Freiheitsgraden wäre zu liberal, weil die Leave-one-out-Werte korreliert sind und
benachbarte Läufe dieselben Referenzläufe teilen.

### A9.9 Sensitivitätsanalysen

Vorhersage aus Phase-0- und Phase-1-Einzelmodulläufen zusammen; blockweise Vorhersage aus den
Kontrollläufen desselben Blocks; Vorhersage ohne Jitterzeiger (ρⱼₖ = e^{−ikφ̄ⱼ}); k_max − 2 (nicht unter 3)
und, soweit (b) es zulässt, k_max + 2; Auswertung je Block; H2 mit w ± 2°; Auswertung einschließlich der
nach G1 ungültigen Läufe; Ausschlussraten je Konfiguration; H1 mit c_B statt des simulierten c; H1 mit D für
Re und Im N_k in Fassung A, D = max_i |N̂_k,i| (§8.5); H1 mit Δ_q = 0,1·D_q und Δ_rel,q = Δ_q (§8.5); F_min − ⟨N⟩ ohne
Korrektur des Rauschbias; am Triphasik-Punkt zusätzlich der Wert der gemessenen Kurve an den Minimumsstellen der
Vorhersage und das Mittel der drei lokalen Minima; Zuordnung nur gegen ŷ⁰, ŷ⁰′ bzw. nur gegen ŷ¹, ŷ¹′; E3 mit
nominaler statt kalibrierter Geometrie. Die bisherige Sensitivitätsanalyse „Superposition je Zelle“
ist jetzt H1Z (§3).

### A9.10 Metadaten je Lauf

Lauf-ID, Registrierungskennung, Block, Konfiguration (Sollphasen), Laufart, Einstellung (Haupteinstellung
oder Einstellung 2), Start- und Endzeit, Frequenz, Temperaturen, Luftdruck, Lufttemperatur, Feuchte,
Versorgungsspannung, Verstärker- und Filtereinstellungen, Firmware- und Softwarestände, Kalibrier-IDs,
Bediener, Ergebnis der Gültigkeitsprüfung mit Grund, Protokollnotizen.

### A9.11 Pipelinetest und Simulationen

Einzelmodul- und Kombinationsläufe aus `linear_solver.py` mit Rauschen, Jitter und Drift müssen H1
bestätigen; Daten mit bekannter Nichtlinearität (etwa ein Hertzscher Kontakt nach Testebene T0 des
Literaturabgleichs) oder mit eingebauter Modulkopplung müssen H1 falsifizieren, wenn ihr größtes Residuum
mindestens 2·Δ_rel beträgt (Power-Kriterium unten); knapp über Δ_rel ist „nicht entscheidbar“ zu erwarten.
Vor Teil B zusätzlich je Szenario 1000 synthetische Kampagnen mit den geplanten n, n₀ und den
Pilotstreuungen, mit getrennten Rauschmodellen für Einzelmodul- und Kombinationsläufe; dieselbe Simulation
liefert n_min, n₀, den Rauschbias b̂⁰ und b̂¹ und c (§8.4; ob sie nach dem Datenschluss mit den tatsächlichen
Laufzahlen neu berechnet werden, ist offen, §12). Den kritischen Wert für ε_ctrl liefert eine eigene
Simulation nach A9.8.

**Schätzung der Grenzen.** In jeder simulierten Kampagne werden D_q, Δ_q und Δ_rel,q wie in der Auswertung als
Punktwert aus dem simulierten ŷ⁰ geschätzt, also aus den simulierten Einzelmodulläufen der Phase 0 dieser Kampagne,
in Fassung B und in den Sensitivitätsvarianten (Faktor 0,1; Fassung A). Die Kriterien unten gelten für das
vollständige Verfahren einschließlich dieser Schätzung (Arbeitsfestlegung, §12): Die simulierte Auswertung verwendet
die geschätzten Grenzen; Bezugswerte der wahren Abweichung in den Kriterien (etwa „eine Größe genau an der Grenze
±Δ_q“, „größte wahre Abweichung < Δ_rel“, „größtes Residuum mindestens 2·Δ_rel“) sind Δ_q und Δ_rel aus der
rauschfreien Vorhersage des Szenarios. Zu den Szenarien gehören solche mit ungleichen Modulen, in denen N₃ unter
Fassung B bindet; berichtet werden dann die nötige Präzision und Laufzahl.

Kriterien vor dem Einfrieren (Kalibrierung mit angenommenen Rauschmodellen über mehrere Präzisionsstufen
(Umfang der Stufen und Laufzahl je Stufe offen, §12), von reinem Sensorrauschen bis zu mehreren Prozent
Lauf-zu-Lauf-Streuung je Modul) und in Teil B (mit den
Pilotkovarianzen):

- P(falsifiziert | exakte Superposition oder lineares, zeitinvariantes Artefakt) ≤ 0,05;
- P(falsifiziert | größte wahre Abweichung < Δ_rel) ≤ 0,05;
- P(bestätigt | eine Größe genau an der Grenze ±Δ_q) ≤ 0,05;
- P(H1 und H2 bestätigt | exakt) ≥ 0,8 bei der nach §5.4 geplanten Laufzahl (gemeinsame Bedingung, Arbeitsfestlegung,
  §12) und nicht fallend mit wachsender Präzision;
- P(falsifiziert | Kopplung, deren größtes Residuum mindestens 2·Δ_rel beträgt) ≥ 0,8 bei der geplanten
  Laufzahl;
- H2 auch bei hoher Präzision entscheidbar (Lesart offen, §12; mit der gemeinsamen Bedingung oben ist
  P(H2 bestätigt | exakt) ≥ 0,8 bei der geplanten Laufzahl von selbst erfüllt); das nach §8.6 gewählte
  Intervall erreicht die simulierte Überdeckung 0,936 (dieselbe Schwelle wie §8.6; Bezugswert der Überdeckung
  offen, §12), notfalls mit kalibrierter Verbreiterung; auch bei symmetrischem Zelt geprüft;
- berichtet, ohne Bedingung: Rate „nicht entscheidbar“ je Grund, Power gegen Kopplung und Hertz-Kontakt,
  Raten der Ausgänge von H1 in den Sensitivitätsvarianten (Faktor 0,1; Fassung A), Raten der Ausgänge von H2
  und H3 mit den Testvarianten δ_H2 = 1°, δ_H3 = 10 % und den Alternativen von §12
  (Zeile „Grenzen von H2 und H3“) sowie der Relevanzgrenze von H3 gleich Δ (offen, §12), auch bei wahren
  Abweichungen an diesen Grenzen; Bestätigungswahrscheinlichkeit von H4;
  der Anteil der Kampagnen mit mindestens einem |z⁰| > c bei exakter Superposition in der Prüfsimulation (§8.4).
  Liegt er über 0,069, gilt das gepoolte Quantil nach §8.4; das ist kein verfehltes Kriterium.

**Zuordnung, H1Z und E3.** Zusätzliche Szenarien, jeweils für beide Arten von Einstellung 2 (zweite Amplitude,
zweite Frequenz mit festem Hub): Aktorkopplung fester relativer Stärke (0,1 % und 1 %; Simulationsannahmen, keine
Vorhersagen für die reale Apparatur V1); Kopplung, deren Stärke mit der Last wächst; quadratische Kettenkennlinie;
Hertzscher Kontakt in Reihe zur Zelle; lastabhängiger Phasenversatz eines Moduls; Wechselwirkung der Antriebe;
Zelllage- und Zellverstärkungsfehler innerhalb und außerhalb der Unsicherheit aus P0.1. Kriterien:

- Zuordnung (Kriterium offen, §12: feste Anker oder Zuordnungsgrenze): Trefferquote ≥ 0,8 bei der geplanten
  Laufzahl für 0,1 % Aktorkopplung (Klasse p = 1) und für
  eine Kettennichtlinearität mit mindestens 1 mN größtem H1-Residuum (Klasse p = 2); berichtet: Rate einer
  falschen Klasse und von „nicht zuordenbar“, auch für Hertz-Kontakt und lastabhängige Kopplung;
- H1Z: P(falsifiziert | exakte Superposition oder lineares, zeitinvariantes Artefakt) ≤ 0,05; berichtet:
  Bestätigungswahrscheinlichkeit und Prüfrate von c wie bei H1;
- E3: P(auffällig | exakte Superposition, Kalibrierung innerhalb ihrer Unsicherheit) ≤ 0,05 und
  P(unauffällig | exakte Superposition, Kalibrierung innerhalb ihrer Unsicherheit) ≥ 0,8; berichtet: Rate
  „unbestimmt“ und Rate „auffällig“ bei 0,1° und 0,3° Phasenversatz eines Moduls. Die Laufzahl richtet sich
  nicht nach E3. Verfehlt E3 eines der beiden Kriterien in Teil B mit den Pilotkovarianzen, werden die
  E3-Prüfgrößen nur beschreibend mit Unsicherheit berichtet, ohne dreiwertige Aussage (§8.10; Rückfall je
  Prüfgröße oder für E3 als Ganzes offen, §12). Vor dem
  Einfrieren zeigt die Kalibrierung über die Präzisionsstufen, ab welcher Unsicherheit der Zellharmonischen
  das Kriterium erreichbar ist.

Erfüllt die Kalibrierung vor dem Einfrieren ein Kriterium nicht, werden die Regeln von §8.4–§8.6 bzw. §5.5 und
§8.10 überarbeitet und die Änderung in A0 vermerkt. Erreicht die Zuordnung die Trefferquote auch mit
geänderter Einstellung 2 oder geänderten Punkten I nicht, wird sie nur beschreibend berichtet. Für das
E3-Kriterium „unauffällig“, das von der erst in Phase 0 bekannten Präzision abhängt, gilt stattdessen der
Rückfall oben. In Teil B werden die Ergebnisse berichtet; die Regeln bleiben, wie in Teil A festgelegt,
einschließlich der Regeln für c (§8.4) und den Intervalltyp mit Rückfall (§8.6); offen sind ein Rückfall für H1 und
die Fassung dieser Regeln (§12).

### A9.12 Phase 1 im Ablauf

- **Messtag.** Aufwärm-Referenzläufe (§6), höchstens zehn; sie lösen keinen Nullpunktalarm aus, und der
  letzte gilt als gültiger Referenzlauf für N_s,int und als Vergleich für den ersten Nullpunktalarm. Nach
  dem letzten Kontrollsatz des Tages folgt der Schlussreferenzlauf, damit jeder Lauf zwischen zwei
  Referenzläufe liegt. Läufe je Kampagne: (N_K + N_I + 8)·n + 8·d, dazu Aufwärm- und Wiederholungsläufe;
  je Block N_K + N_I Konfigurationen, der Referenzlauf der Blockmitte und ein Kontrollsatz aus sieben
  Läufen, je Messtag ein weiterer Kontrollsatz und der Schlussreferenzlauf. In §5.3 (c) steht dafür 18·d
  (acht Läufe und höchstens zehn Aufwärmläufe je Tag) und der Faktor 1/(1 − p̂) (Zeitformel offen, §12: Messzeit
  der Identifizierbarkeitsläufe). Ohne
  Identifizierbarkeitsläufe wären es (N_K + 5)·n + 5·d.
- **Phase 0 bei Einstellung 2.** P0.5′, 3·n₀′ Einzelmodulläufe und nach je zwölf Läufen ein Referenzlauf,
  dazu D2_K in P0.3, die Betriebslastprüfung von P0.4 nach P0.9 (Zeitpunkt offen, §12) und gegebenenfalls P0.12
  und die Prüfung
  der Umschaltung eines zweiten Nockensatzes in P0.5′ (A9.2).
- **Wiederholungsplatz.** Ein vor Beginn des Schlusskontrollsatzes als ungültig erkannter Lauf einer
  Konfiguration wird an einem Platz wiederholt, den der Generator von §6 gleichverteilt unter den offenen
  Konfigurationsplätzen des Blocks und dem Platz vor dem Schlusskontrollsatz zieht; höchstens zwei
  Wiederholungen je Konfiguration und Block. Was danach fehlt, deckt die Reserve r.
- **G1 und S1.** Die Vorprüfung gegen R₀ erkennt grobe Verstöße sofort. Steht ein G1-Verstoß erst mit dem
  nächsten planmäßigen Referenzlauf fest, folgen ebenfalls R₂, X′ und R₃, sofern der Schlusskontrollsatz
  noch nicht begonnen hat; danach festgestellte Verstöße werden weder wiederholt noch nach S1 geprüft. X′
  wird auch jenseits der Wiederholungsgrenze gemessen und zählt als Wiederholung. S1 greift nur bei einem
  G1-Verstoß von X′.
- **Kontrollläufe.** Ein aus anderem Grund als G1 ungültiger Kontrolllauf (bei R auch ein nicht reproduzierter
  Nullpunktalarm, §8.8) wird sofort wiederholt, höchstens zweimal; ist auch die zweite Wiederholung
  ungültig, wird angehalten und nach §9.2 verfahren. Für L₁′, L₂′, L₃′ gilt das nicht: Nach zwei ungültigen
  Wiederholungen fehlt der Lauf, und der Block wird fortgesetzt (Mindestzahl gültiger L′ je Modul offen, §12).
- **Nach S2.** Die Konfiguration bleibt in den Blöcken und wird weiter gemessen, geht aber in keinen Test
  ein (§9.1); betrifft S2 ein Lⱼ, ist ŷ¹ ungültig (§8.2), betrifft es ein Lⱼ′, ist ŷ¹′ ungültig (ob S2 für L′
  gilt und welche Folge das für die Zuordnung hat,
  ist offen, §12). Ein zweites
  S2 ohne festgestellten Apparaturfehler beendet Phase 1 (§9.2).

### A9.13 Zuordnung und E3 im Einzelnen

- **Kraftskala.** s aus den Einzelmodulläufen der Phase 0 (A1) mit Bootstrap-Unsicherheit; für die Zuordnung
  gegen ŷ¹ und ŷ¹′ ebenso s¹ aus den Kontrollläufen der Phase 1.
- **Residuen.** Für i ∈ I und q ∈ {Re N_k, Im N_k; k = 1, 2, 3}: r_iq und r′_iq gegen ŷ⁰ und ŷ⁰′ bzw. gegen ŷ¹
  und ŷ¹′, Unsicherheiten nach §8.3. F_min − ⟨N⟩ geht nicht ein, weil das Minimum nicht linear von der Kurve
  abhängt.
- **Anpassungsmaß.** χ²_p = Σ_{i,q} (r′_iq − s^p·r_iq)²/(u′²_iq + s^{2p}·u²_iq) für p = 0, 1, 2, mit
  m = 6·N_I Termen (ob m fest bleibt, wenn ein Punkt von I nicht auswertbar ist, ist offen, §12), verglichen mit
  dem 95-%-Quantil von χ²(m). Die Terme sind korreliert; ob das Quantil die
  Rate falscher Zuordnungen begrenzt, prüft die Kalibriersimulation (A9.11).
- **Regel** (Regel und Auslöser offen, §12). Zugeordnet ist Klasse p, wenn χ²_p unter dem Quantil liegt und
  χ²_{p′} für beide anderen p′
  darüber, gegen ŷ⁰, ŷ⁰′ und gegen ŷ¹, ŷ¹′ dieselbe Klasse; sonst „nicht zuordenbar“. Voraussetzung ist an
  einem Punkt von I ein |z⁰| > c mit gleichsinnigem |z¹| > c (§8.10).
- **Modulzeiger.** Je Konfiguration Ĉₖ = T(kω)⁻¹·(N₁,ₖ, N₂,ₖ, N₃,ₖ)ᵀ für k = 1, 2 aus den Zellzeigern der
  Konfigurationsmittelkurven, mit T aus P0.1 (Statik, Zelllagen, relative Verstärkungen) und P0.4 (G_F je
  Zelle, Kippmoden).
- **E3a.** Δφⱼ^Z = (arg Ĉ₁,₁ − arg Ĉⱼ,₁) − φ̄ⱼ^P, j = 2, 3, an jeder auswertbaren Konfiguration. Daneben
  berichtet: derselbe Wert aus k = 2 (Differenz der Argumente geteilt durch 2; ein echter Phasenversatz
  ergibt beide Male denselben Wert, A2.7) und die Amplitudenverhältnisse |Ĉⱼ,₁| der Kombinationsläufe zu
  denen der Einzelmodulläufe.
- **E3b.** R±₁ aus den Zellzeigern N_c,1 und den Zelllagen, R̂±₁ ebenso aus der zellweisen Superposition;
  q_Z am Triphasik-Punkt. Weil Messung und Vorhersage aus denselben Zellen stammen, fallen konstante
  Modulunterschiede, Zellverstärkungen und Zelllagen heraus; q_Z ist eine Funktion der H1Z-Residuen von
  Re und Im N_c,1 am Triphasik-Punkt (§8.10). Daneben berichtet, ohne Schwelle: |R₋₁|/|R₊₁| der Messung und
  der Vorhersage.
- **Vertrauensgrenzen.** Bootstrap wie A9.5, zusätzlich mit Ziehungen aus der Unsicherheit von T, bei E3a
  auch aus u(Δδⱼ) (normalverteilt, je Modul eine Ziehung für alle Konfigurationen) und aus der Quantisierung
  der Zeitstempel (Rechteckverteilung). Auffällig:
  |x̂| − z_B·u(x̂) > Schwelle, z_B das einseitige Bonferroni-Quantil zu α = 0,05 über alle E3-Prüfungen
  (zwei je auswertbarer Konfiguration und E3b; Zahl der Prüfungen offen, §12). Unauffällig: |x̂| + 1,645·u(x̂) ≤
  Schwelle für alle Prüfungen.
  Sonst unbestimmt.

---

## Tabelle C · Artefakte und Kontrollen

| Quelle | Wirkung | Kontrolle |
|---|---|---|
| Thermische Drift (v1) | Nullpunkt- und Empfindlichkeitsdrift | Temperatur an Zellen und Antrieben, Aufwärmen, G7; Referenzläufe in jedem Block; nullpunktfreie Größen; ŷ¹, S3 |
| Mechanische Kopplung (v1) | Module beeinflussen einander | Gegenstand von H1; D2_K; Identifizierbarkeitsläufe und E3 (§8.10) |
| Vibrationen (v1) | nicht synchrone Kraftanteile | Referenzläufe, Beschleunigungssensor, phasensynchrone Mittelung |
| EM-Rückwirkungen (v1) | Einstreuung der Antriebe | D2ⱼ, D2_K; Blindkanal in jedem Lauf |
| Software-Filter (v1) | Formänderung der Kurve | nur die Bandbegrenzung auf k_max, für alle Läufe identisch, Code eingefroren |
| Anzeige- und Stillstandsstatistik (neu) | formabhängiger Lagewert statt Zeitmittel; Versatz s_N·med(u), Signatur eines phasenabhängigen Mittelwerteffekts | Verbot in A9.1; Rohdaten, ganze Zyklen (A9.4) |
| Sensor-, Ketten- und Kontaktnichtlinearität (v1, erweitert) | verzerrte Wellenform, verletzte Superposition; Kontakt und Kette nicht trennbar (A2.6) | P0.1 (Brückensimulator), P0.4 (zwei Amplituden, unter Betriebslast mit Klirrkriterium), P0.12 (antriebsabhängig), feste Einstellungen; G5; Identifizierbarkeitsläufe (Klasse p = 2); H1Z |
| Phasenfehler (v1) | falscher Konfigurationspunkt | gemessene Phasenzeiger ρⱼₖ; Profilphasen mit Δδⱼ; G2; E3a |
| Erwartungseffekte (v1) | Auswahl, nachträgliches Justieren | Randomisierung, eingefrorene Regeln, automatische Gültigkeitsprüfung, Blindung, Abweichungsprotokoll |
| Einzelzellen, Kippmomente (neu) | eine Zelle hebt ab, obwohl N > 0 | Sicherheitsabstand je Zelle, G6, S2; E3 |
| Kraftnebenschluss, Querkräfte, Übersprechen (neu) | Nebenpfad oder Hysterese; Summe hängt von der Laststelle ab | kinematische Lagerung, Kabelschlaufe; P0.1, P0.3; Kabelkräfte: Ergänzung unten |
| Resonanzen der Auflage, weitere Moden (neu) | Überhöhung, Empfindlichkeit gegen K, ζ, f | P0.4; Bedingung (b), k_max-Regel |
| Drift der Einzelmodulantwort (neu) | Vorhersage aus Phase 0 veraltet | ŷ¹; S3; keine mechanischen Eingriffe |
| Zeitbasis, Kanalversatz, Indexauflösung (neu) | Phasenfehler in ρⱼₖ und H3 | gemeinsame Zeitbasis, Zeitstempel; G_F, G_x |
| Frequenzabweichung (neu) | Profilbeschleunigung ∝ f², H(kω) | G3 |
| Parkfehler (neu) | geparktes Modul bewegt sich oder steht falsch | Encoder der geparkten Module; G9 |
| Segmentierung, Resampling (neu) | Verschmierung der Mittelkurve | identische Verarbeitung; Abtastrate; Pipelinetest |
| Rauschbias des Minimums (neu) | F_min systematisch zu klein | nur bandbegrenzte Konfigurationsmittelkurve; Bias simuliert, korrigiert und als Unsicherheit geführt (§5.4, A9.5) |
| Einschwingvorgänge (neu; Erfahrung v3) | scheinbare Mittelwertabweichung, verzerrte Form | T_e, G4, H0 |

**Ergänzung (Entwurf 10/2026).** Signatur: *H0* wirkt auf ⟨N⟩ und fällt, soweit gleichbleibend, in Δ⟨N⟩
heraus; *linear* heißt linear und zeitinvariant, also keine H1-Signatur (A2.1), wohl aber eine Wirkung auf H3
und absolute Größen; *H1* kann die Superposition verletzen (nichtlinear, zeitveränderlich oder
Wechselwirkung). Die Größenordnungen sind Modellabschätzungen mit angenommenen Maßen (Grundfläche des
Körpers 0,04 m², Außenvolumen V_außen 1,8–4 l, M = 0,650 kg) oder Rechnungen im Beispiel A4, keine Messwerte (Z);
die Kopplungszahlen sind Rechenbeispiele, keine Vorhersagen für die reale Apparatur V1.

| Quelle | Wirkung | Signatur | Größenordnung (Modellabschätzung) | Kontrolle |
|---|---|---|---|---|
| Luft am Körper: zugesetzte Masse, Quetschfilm im Bodenspalt | zusätzliche mitbewegte Masse und Dämpfung, verschiebt f_n; kleiner Gleichanteil aus der Trägheit der Spaltströmung | linear; der quadratische Anteil gibt einen Gleichanteil (H0) und Mischterme gleicher Größe (H1), beide vernachlässigbar | hydrodynamische Zusatzmasse m_hyd ≈ 4,6 g (0,7 % von M); mit Bodenspalt 8 g (10 mm) bis 30 g (3 mm), Dämpfung 0,04 bzw. 0,6 N·s/m; dazu der Luftanteil ρ_L·V_außen ≈ 2,2–4,8 g von m_L (A1); Gleichanteil (Skala, obere Abschätzung, Spalt 3 mm, Beispiel A4): bei K = 10⁵ N/m etwa 4·10⁻⁶ N im Einzelmodullauf und 3·10⁻⁵ N bei synchroner Phasung, bei K = 10⁶ N/m unter 10⁻⁶ N | Spalt ≥ 10 mm oder offene Grundplatte, sonst Spaltvariation in P0.3 (§5.1, A9.2); in P0.4 und den Einzelmodulläufen enthalten; als Zusatzmasse m_L = ρ_L·V_außen + m_hyd im Auslegungswerkzeug (`--m-luft`) |
| Auftrieb, Luftdichte | Der Auftrieb ist Teil der statischen Last und damit von ⟨N⟩; er ändert sich mit Luftdruck, Temperatur und Feuchte. Mit M aus der statischen Zelllast (Konvention b, §12) ist er in M·g enthalten und wird nicht abgezogen (A1) | H0 | auf das Außenvolumen ρ_L·g·V_außen ≈ 0,021–0,047 N, auf das Materialvolumen ρ_L·g·V_Mat ≈ 1–6 mN (Unterschied zur nicht gewählten Bauteilwägung, A1); Änderung bei 1 % Dichteänderung ≈ 0,2–0,5 mN (dicht verschlossenes Gehäuse) bzw. ≈ 0,01–0,06 mN (offenes oder belüftetes Gehäuse) | M aus der statischen Zelllast (§12, P0.2); Referenzläufe mit Interpolation; Luftdruck, Lufttemperatur, Feuchte je Lauf (A9.10) und bei P0.2 |
| Elektrostatische Aufladung | Gleich- und Driftanteil; Modulation durch bewegte Teile gegenüber Gegenflächen | H0; Modulation etwa linear | Plattennäherung σ²A/(2ε₀) = 2·10⁻⁵ … 0,2 N für σ = 10⁻⁷ … 10⁻⁵ C/m², über vier Dekaden offen; Modulation ≈ 0,04 mN (10 cm², 100 V, 1 mm) | leitfähige, geerdete Oberflächen (§5.1); Feuchte je Lauf; ein Ionisator nur, wenn vor Phase 0 festgelegt; D1, Referenzläufe, G1, Nullpunktalarm, S1 |
| Kabelkräfte | Steifigkeit der Schlaufe; Reibung und Hysterese; Kabel an bewegten Modulen (etwa für Sensoren) | linear (Steifigkeit); H1 (Hysterese, Reibung) | Schlaufe mit 100 N/m bei der Einfederung eines Einzelmodullaufs im Beispiel A4: 0,13 mN bei K = 10⁶ N/m (1,30 µm) bis 1,3 mN bei K = 10⁵ N/m (13,3 µm) | festgelegte Schlaufe mit Fotodokumentation (A9.1); P0.3: zwei Lagen, statischer Nebenschluss ≤ 0,1·Δ_q, Umkehrspanne ≤ 0,3·u_c,erw; Kabel an Modulen: Masse in m_j (P0.2), Führung wie die Schlaufe, in den Einzelmodulläufen enthalten |
| Aktorkopplung | Amplitude oder Profil eines Moduls ändern sich unter der Last der anderen | H1 | 0,1 % Abweichung in den Kombinationsläufen ergibt 1,22 mN in F_min − ⟨N⟩, 1 % ergibt 12,2 mN (Rechenbeispiel A4, k_max = 9) | Gegenstand von H1; Identifizierbarkeitsläufe (Klasse p = 1, bei lastabhängiger Stärke p = 2); E3 (Amplitudenverhältnisse, E3b); Modulkinematik in Phase 1, falls vorgesehen (offen, §12) |
| Lastabhängiger Phasenversatz zwischen Encoder und Masse | Nachgiebigkeit der Übertragung, Lastmoment einer Nocke mit 2f-Anteil; der Encoder misst den Antrieb, nicht die Masse | H1 | 0,05° an Modul 2 nur in den Kombinationsläufen ergibt 1,75 mN in F_min − ⟨N⟩ (Rechenbeispiel A4) | E3a (Modulphase aus den Zellen gegen Encoder, 0,1°); Identifizierbarkeitsläufe; P0.5 und P0.6 messen ohne die Last der anderen Module |
| Gemeinsame Versorgung der Antriebe | Spannungseinbruch, Sättigung von Reglern, Erdschleifen; wirkt nur, wenn mehrere Antriebe laufen | H1 (Wechselwirkung) | parametrisch: Ein Spannungseinbruch wirkt wie eine Aktorkopplung; 0,1 % Amplitudeneinbruch eines Moduls nur in den Kombinationsläufen ergibt ≈ 1,0 mN in F_min − ⟨N⟩, aller Module 1,22 mN (Rechenbeispiel A4, k_max = 9). Ob und wie stark die Amplitude einbricht, hängt vom Antrieb ab (offen) | D2_K, ohne Last (§5.2); Versorgungsspannung je Lauf (A9.10); Identifizierbarkeitsläufe (lastabhängig: p = 2); Blindkanal; getrennte Versorgung als Teil des Antriebsentscheids (§12) |
| Luftkräfte auf die Module, Schall | Widerstand der bewegten Massen | je Modul, ohne Mischterm (∝ v² der eigenen Masse), daher keine H1-Signatur; Wechselwirkung vernachlässigbar | ≈ 0,035 mN je Modul (10 cm², c_w = 1, Spitzengeschwindigkeit des Profils 0,24 m/s) | keine eigene; in den Einzelmodulläufen enthalten |

---

## Tabelle F · Festlegungen

Gewählte Zahlenwerte ohne Messung, je mit einer Zeile Begründung.

| Festlegung | Stelle | Begründung |
|---|---|---|
| α = 0,05 je Familie | §3, §8.4 | übliche Irrtumswahrscheinlichkeit; jede Hypothese wird für sich berichtet |
| 25 % der statischen Zelllast als Mindestabstand | §5.3 (a) | Nahe am Abheben wird ein realer Kontakt nichtlinear, und im Liftoff-Bereich ist der Zustand nicht eindeutig |
| Bestimmung von M: Konvention (b), M = Σ_c F_c,stat/g aus P0.2, Zellen in N kalibriert, g örtlich bestimmt; Gesamtwägung als beschreibende Kontrolle, wenn eine geeignete Waage verfügbar ist (Arbeitsfestlegung, §12) | §3, §4, §5.2 P0.2; A1, A9.2 | misst die statische Last mit denselben Zellen und derselben Kalibrierung wie ⟨N⟩, ohne Annahme über Volumina und Dichten; kein zusätzlicher Auftriebsabzug; Gewicht M·g und träge Masse M + m_L (m_L = ρ_L·V_außen + m_hyd) getrennt. Statische Nebenkräfte (Kabel, Ladung) und der Luftzustand bei P0.2 gehen in M ein, M gilt für den Zustand vor der Endmontage. Nicht gewählt: (a) Bauteilwägung, sie braucht wahre Massen, V_Mat und V_innen |
| Faktor 2 Resonanzabstand (k·f ≤ f₁/2) | §5.3 (b) | begrenzt \|H\| auf 1,33 und die Frequenzempfindlichkeit auf 0,67 (A6) |
| Δ_q = 0,25·D_q, D_q als Punktwert aus ŷ⁰ (Arbeitsfestlegung, §12); Sensitivitätsvariante 0,1·D_q | §8.5 PB1, A9.9 | Eine Bestätigung muss die vorhergesagte Struktur auf ein Viertel auflösen, nicht nur ihr Vorhandensein zeigen; ein kleinerer Faktor erhöhte die nötige Laufzahl etwa mit dem Kehrwert seines Quadrats (0,1: etwa 6-fach, Z). Punktwert: dieselbe Größe, die die Auswertung verwendet; ihren Schätzfehler erfasst Werkzeug 8 (A9.11), die Prüfung auch gegen ŷ¹ begrenzt ihn. Die Bestätigung ist damit eine grobe Modellübereinstimmung innerhalb registrierter Toleranzen: Im Beispiel A4 erreicht erst eine gemeinsame Kopplung aller Module von etwa 10,6 % die Grenze von F_min − ⟨N⟩ (Rechenbeispiel, keine Vorhersage für die reale Apparatur V1; A4, Z) |
| t_eq = t(0,95; ν_eff), ohne Mehrfachkorrektur; ebenso für die H3-Intervalle r ± t_eq·u_c (Arbeitsfestlegung, §12) | §8.5 PB1, PB3 | TOST je Test auf α = 0,05; das Intersection-Union-Prinzip hält α für die gemeinsame Bestätigung (A8) |
| Δ_rel,q = Δ_q (Arbeitsfestlegung, §12) | §8.5 | kleinster Wert, mit dem „äquivalent“ und „relevant abweichend“ disjunkt sind, ohne weiteren freien Faktor; ändert die Bestätigung nicht. Δ_q ist ein Auflösungs-, kein physikalisches Relevanzkriterium: Eine Falsifikation zeigt eine Verletzung der Superposition über die registrierte Toleranz hinaus (A8) |
| D für Re und Im N_k: Fassung B, Durchmesser max_{i,i′} \|N̂_k,i − N̂_k,i′\| der Zeigermenge (Arbeitsfestlegung, §12); Fassung A, max_i \|N̂_k,i\|, als Sensitivitätsanalyse | §8.5, A9.9 | analog zur Spannweite bei F_min, gleiche Bedeutung für alle 147 Größen; Fassung A behandelt die Harmonischen ungleich (Beispiel A4: Toleranz 12,7 / 13,3 / 43,3 % der Änderung entlang des Schnitts für N₁ / N₂ / N₃, Z) und lässt unter Lauf-zu-Lauf-Streuung Re und Im N₁ die Laufzahl stärker treiben (etwa halbe Grenze); B ist bei N₃ strenger und bleibt auch, wenn N₃ bindet (A8) |
| c von H1 als 95-%-Quantil von max\|z⁰\|, in beide Richtungen (Rauschmodelle für c offen, §12) | §8.4 | hält die Rate „mindestens ein \|z⁰\| > c“ bei 0,05 trotz korrelierter Tests (A8) |
| Faktor 3 in n_min ≥ (3·1°/(SNR·δ_H2))², bei der Testvariante δ_H2 = 1°: n_min ≥ (3/SNR)² (δ_H2 offen, §12) | §5.4 | H2-Halbbreite etwa 3/(SNR·√n) für n₀ = n in einer Vorabsimulation des Zeltfits mit weißem Restrauschen außerhalb des Repositorys; Werkzeug 8 wiederholt sie; notwendig, nicht hinreichend für die Bestätigung von H2 |
| δ_H3 = 10 %, Δ = δ_H3·\|N̂_k⁽ʲ⁾\| als Äquivalenzgrenze von H3 (Testvariante, offen, §12; Relevanzgrenze von H3 offen, §12) | §8.5 PB3 | Ein Modelltest mit gröberer Auflösung unterscheidet nichts. Bei 10 % ist eine Bestätigung von H3 keine Bestätigung des Kontaktgesetzes oder des Kontaktmodells: Im steifen Aufbau liegt der Kontaktanteil \|H − 1\|/\|H\| = \|N̂_k⁽ʲ⁾ − G_F·m_j·a_k⁽ʲ⁾\|/\|N̂_k⁽ʲ⁾\| bei k ≤ 3 darunter (Beispiel A4, K = 10⁶ N/m, 10 Hz: 0,3 / 1,0 / 2,3 %, Z; Betrag gegen den starren Wert 0,3 / 1,0 / 2,4 %; §8.7, A9.7) |
| δ_H2 = 1° als Äquivalenz- und Relevanzgrenze von H2 (Testvariante, offen, §12; Alternative 0,5° oder ein anderer begründeter Wert) | §3 H2, §8.6, §9.3 | halbe Schrittweite des Schnitts (bisher die Halbbreitengrenze); an der Spitze strenger als H1, dessen Äquivalenzgrenze im Beispiel A4 etwa 3,8° Spitzenverschiebung entspräche (Z); Begründung und Prüfung in Werkzeug 8 vor dem Einfrieren (A9.11) |
| (c₄ + 1,645)·u_c,erw für V | §8.5 | bestätigt ein zutreffendes Vorzeichen an der Schwelle mit etwa 93 % je Punkt (n_min = 20, A8) |
| k_max ≥ 3 | §5.4 | H1 prüft N₃ |
| 0,1·u_c,erw für die Frequenztoleranz | G3 | systematischer Beitrag klein gegen die Unsicherheit |
| Rauschbias: halbe Spannweite über die Rauschmodelle als Rechteckverteilung (Rauschmodelle offen, §12) | §5.4, A9.5 | Modellunsicherheit des Bias ohne Annahme über das wahre Rauschmodell |
| 0,1·Δ_q für Laststelle, Querkraft, statischen Nebenschluss (offen, §12) | §5.2 | lineare, zeitinvariante Einflüsse erzeugen keine H1-Signatur (A2.1); klein gegen die Äquivalenzgrenze |
| 0,3·u_c,erw für Superpositionsfehler der Elektronik, Umkehrspanne, Wechselwirkung der Antriebe in D2_K, Schein-Oberwellen in P0.4, gerade Harmonische in P0.12, Empfindlichkeitsänderung (G7) (Nachweisform und Folge offen, §12; Fassung von D2_K offen, §12) | §5.2, G7 | nichtlineare oder zeitveränderliche Einflüsse können eine H1-Signatur erzeugen; 0,3·u_c,erw ist klein gegen die Nachweisgrenze c·u_c (Schwelle für P0.4 und P0.12 offen, §12) |
| \|D2_k\| ≤ 0,01·min_j \|N̂_k⁽ʲ⁾\| für D2ⱼ | §5.2 | ein Zehntel der H3-Grenze bei der Testvariante δ_H3 = 10 % (offen, §12); ein D2-Signal eines einzelnen Antriebs betrifft H1 nicht, weil es in den Einzelmodulläufen mitgemessen wird |
| ε_ctrl = 3·σ̂_ref bzw. 3·σ̂_betr | §8.8 | Form aus Einordnung §4; seltene Fehlausschlüsse (A8) |
| Nullpunktalarm 3·√(4/3)·σ̂_ref | §8.8 | dieselbe Schwelle in Standardabweichungen wie G1 für die Differenz zweier Referenzläufe |
| mindestens 42 Referenzläufe | §4, P0.7 | mindestens 40 Leave-one-out-Werte für σ̂_ref |
| Referenzlauf nach je zwölf anderen Läufen in Phase 0 | P0.7 | etwa der Abstand in Phase 1 (Blockmitte, Kontrollsätze) |
| 5·σ für F_LO | §4 | Rauschen löst praktisch keinen Liftoff-Befund aus |
| c_S mit höchstens 5 % Fehlalarm je Kontrollsatz | §9.2 S3 | ein Kontrollsatz je Block; Reproduktion durch Wiederholung senkt die Rate weiter |
| σ_tol = dreifacher Median von σⱼ der Pilotläufe | G2 | robust gegen einzelne Ausreißer der Pilotläufe |
| σ_Δ = 1,4826·MAD | G4 | robuste Standardabweichung aus allen Läufen einer Art, vor jeder Ausschlussentscheidung bestimmbar |
| ΔT aus höchstens 0,1 % Empfindlichkeitsänderung und höchstens 0,3·u_c,erw in jeder Größe (Form des Temperaturfensters offen, §12) | G7 | klein gegen Δ_q und gegen die Nachweisgrenze; Antriebstemperaturen wirken über die Phase und werden von G2 erfasst |
| δφ_tol = 0,5° | G2 | ein Viertel der Schrittweite des Schnitts; die Vorhersage verwendet ohnehin die gemessenen Zeiger |
| u(Δδⱼ) ≤ 0,1° | P0.5 | klein gegen δφ_tol und gegen δ_H2 (Testvariante 1°, offen, §12) |
| Zeitstempel-Quantisierung ≤ 0,01° | §5.1 | vernachlässigbar gegen u(Δδⱼ) |
| Interpolationsfehler ≤ 10⁻³ | §5.1 | Amplitudenfehler klein gegen Δ |
| N_θ = 2000 | §4 | so viele Stützstellen je Periode wie in der Engine |
| zehn Zeitkonstanten für T_e | §6 | Restamplitude e⁻¹⁰ ≈ 4,5·10⁻⁵ |
| T_e auf ganze Sekunden aufgerundet | §6 | einfache Steuerung; verlängert nur |
| Fünftel und 3·σ_Δ für G4 | G4 | Anfang und Ende mit gleich vielen Zyklen; seltene Fehlausschlüsse |
| drei Pilotkonfigurationen mit je mindestens 20 gültigen Läufen | §5.4 | gepoolt mindestens 57 Freiheitsgrade für die Streuungen |
| jeder Pilotabstand mindestens 10° von 120° | §5.4, A7 | keine Pilotkonfiguration ist zu einem Schnittpunkt äquivalent, auch nicht bei Phasenfehlern weit über δφ_tol; kein physikalisches Abstandsmaß |
| Verdopplung von T_ramp bei Liftoff in der Rampe | §5.4 | endliche, eindeutige Anpassung |
| mindestens 20 Einzelmodulläufe je Modul vor der Planung | P0.8 | Streuungen für die Planungssimulation |
| gemeinsame Bestätigungswahrscheinlichkeit P(H1 und H2 bestätigt \| exakt) ≥ 0,8 bei oberer 80-%-Grenze der Streuungen (Arbeitsfestlegung, §12; Laufzahl von H1 offen, §12) | §5.3 (c), §5.4, A9.11 | übliche Power, abgesichert gegen zu kleine Pilotstreuungen; gemeinsam, weil zwei getrennte 0,8-Bedingungen bei Unabhängigkeit zusammen nur etwa 0,64 ergäben (Z) |
| Reserve r = ⌈n_min·p̂/(1 − p̂)⌉ + 2 | §5.4 | erwartete Ausfälle plus zwei |
| höchstens zwei Wiederholungen je Konfiguration und Block, je Kontrolllauf | §6 | begrenzt die Blocklänge |
| Ausnahme G5, G8, G10 bei Liftoff (Kontaktast, S2) | §4, §9.2 | Übersteuerung, äußere Störung und defekte Aufzeichnung sagen nichts über den Kontakt |
| Referenzlauf nach der zwölften Konfiguration | §6 | etwa Blockmitte bei 21 bis 26 Konfigurationen (mit Identifizierbarkeitskonfigurationen) |
| mindestens n_min gültige Phase-1-Kontrollläufe je Modul | §3 H3 | gleiche Präzision wie für die Konfigurationen |
| Seed aus den ersten 16 Hexziffern (64 Bit) des SHA-256 des Hauptdokuments | §6 | vor Phase 0 festgelegt; 64 Bit sind der übliche Seed-Umfang |
| Reihenfolge der Konfigurationsliste | §6 | vor Phase 0 festgelegt, damit die Ziehung nicht von Teil B abhängt |
| B = 10 000 Bootstrap-Replikate | §8.3, §8.6 | Quantile von 2,5 % und 97,5 % stabil |
| 10 000 Monte-Carlo-Ziehungen (H3) | A9.7 | Mittel und Streuung stabil |
| 1000 synthetische Kampagnen je Szenario | §12, A9.11 | Standardfehler 0,0069 bei einer Rate von 0,05 |
| 10 000 simulierte Datensätze für den kritischen Wert von ε_ctrl | A9.8 | 95-%-Quantil stabil |
| Prüfschwelle 0,069 für das simulierte c | §8.4 | 0,05 plus zwei Standardfehler, die den Monte-Carlo-Fehler der Prüfung und den Schätzfehler von c (je 1000 Kampagnen) zusammenfassen (A8) |
| Überdeckungsschwelle 0,936 für die Wahl des H2-Intervalls und als Kriterium (Bezugswert der Überdeckung offen, §12) | §8.6, A9.6, A9.11 | 0,95 minus zwei Monte-Carlo-Standardfehler bei 1000 Kampagnen |
| Niveau 95 % der H2-Intervalle, nicht 90 % wie der TOST von PB1 (Arbeitsfestlegung, §12) | §8.6, A9.6 | Überdeckungsschwelle 0,936 und Nominalniveaus 0,96–0,99 sind für 95 % gebaut; je Seite 2,5 % statt 5 % gleicht die Enge des Perzentil-Bootstraps bei kleinem n teilweise aus |
| Nominalniveaus 0,96, 0,97, 0,98, 0,99 für die kalibrierte Verbreiterung des H2-Intervalls (Rückfallkette offen, §12) | §8.6, A9.6 | endliche Liste in Schritten von 0,01; erreicht auch 0,99 die Überdeckung nicht, trägt das Intervall nicht, und H2 ist nicht entscheidbar (Grund: Verfahren) |
| Welch-Test mit α = 0,05; Aussage „Unterschied nachgewiesen“ oder „kein Unterschied nachgewiesen, Gleichheit nicht nachgewiesen“ (Arbeitsfestlegung, §12: Nullkontroll-Sammeltest) | §8.8, A9.8 | berichtet, ohne Einfluss auf H1–H4; ±ε_ctrl ist eine Einzellauftoleranz, keine Äquivalenzgrenze für das Mittel; eine Gleichheitsaussage bräuchte eine eigene, vorab begründete Grenze |
| Streuungsvergleich für ε_ctrl mit α = 0,05 | §8.8, A9.8 | übliche Irrtumswahrscheinlichkeit; setzt ε_ctrl und damit G1 für alle Läufe |
| Fitfenster: Vorschlag w = 6° fest (offen, §12); mindestens zwei Punkte je Seite (Vollständigkeit bei Ausfällen offen, §12) | §8.6, A9.6 | unabhängig von u_c,erw, damit H2 bei hoher Präzision entscheidbar bleibt; drei Punkte je Flanke; ein Zelt braucht zwei Punkte je Flanke |
| Spitzenfehler 0,1° und Raster 0,01° (Alternative zum festen Fenster) | A9.6 | Formfehler des Zelts klein gegen δ_H2 (Testvariante 1°, offen, §12) |
| Suchschritt 0,001° | A9.6 | klein gegen die Halbbreite |
| 1-Hz-Raster für f | §5.3 | endliche Suche; Kraft skaliert mit f² |
| Aufwärmkriterium: zwei Referenzläufe um weniger als σ̂_ref verschieden, höchstens zehn | §6 | Drift kleiner als die Streuung eines Laufs; ohne Drift bleibt es mit etwa 6·10⁻⁴ unerfüllt (A8) |
| Schlussreferenzlauf je Messtag | §6 | jeder Lauf liegt zwischen zwei Referenzläufen |
| mindestens täglich hinterlegtes Manifest | §0 | Verlust oder Änderung höchstens eines Tages unentdeckt |
| zwei räumlich getrennte Kopien | §10.2 | übersteht den Verlust eines Standorts |
| mindestens fünf Laststellen, zwei Kraftrichtungen, zwei Signale | P0.1 | Mitte, drei Zellen, Modulachsen; beide Querrichtungen; kleinste Summe für einen Superpositionstest; mit bekannter Lage bestimmen die Laststellen alle 15 Modul- und Zellparameter (A2.7) |
| doppelte Anregungsamplitude | P0.4 | Linearitätsprüfung mit deutlichem Amplitudenunterschied |
| k_max ± 2 und w ± 2° | A9.9 | ein Rasterschritt der Sensitivitätsvariation je Richtung (w in 2°-Schritten) |
| Beispielspalten ν = 9, 19, 29 | A8 | n_min = 10, 20, 30 |
| Einstellung 2 mit s ≈ 0,5 (Vorschlag, offen, §12) | §5.5 | kleinere Last: Bedingung (a) und G6 bleiben bei linearer Skalierung gewahrt; Residuenverhältnis der drei Klassen 1 : 0,5 : 0,25 (A2.6) |
| mindestens drei Punkte I, Vorschlag 116°, 120°, 124° (offen, §12) | §5.5 | kleinste Zahl, mit der die Skalierung an mehreren Punkten geprüft wird; um den Triphasik-Punkt, wo F_min auf dem Schnitt am größten ist |
| n₀′ ≥ 20 Einzelmodulläufe je Modul bei Einstellung 2; L₁′, L₂′, L₃′ in jedem Kontrollsatz (Umfang offen, §12) | §5.5, §6 | eigene Vorhersage ŷ⁰′ wie in P0.8; ŷ¹′ folgt einer Drift wie ŷ¹ |
| Paarläufe: Verzicht (Vorschlag, offen, §12) | §5.5 | trennen die Skalierungsklassen nicht; Zuordnung zu einem Modul über E3 ohne Zusatzläufe; aufgegeben werden Paaradditivität und Zuordnung zu einem Paar |
| α = 0,05 für das χ²-Quantil der Zuordnung; Trefferquote ≥ 0,8 (Anker oder Zuordnungsgrenze offen, §12) | §8.10, A9.11, A9.13 | übliche Irrtumswahrscheinlichkeit und Power; die Raten prüft die Kalibriersimulation |
| Δ_c,q = Δ_q/3, Δ_c,rel,q = Δ_rel,q/3 für H1Z (Vorschlag, offen, §12) | §8.5 | drei Zellen innerhalb ihrer Grenzen weichen zusammen höchstens um Δ_q ab; unabhängig von der Geometrie |
| E3a-Schwelle 0,1° (Vorschlag, offen, §12) | §8.10 | gleich der Anforderung an die Profilphase in P0.5, klein gegen δφ_tol = 0,5° und gegen δ_H2 (Testvariante 1°, offen, §12); u(Δδⱼ) geht in die Unsicherheit ein, „unauffällig“ verlangt deshalb u(Δδⱼ) deutlich unter 0,1° |
| q_tol = 5,8·10⁻⁴ (Vorschlag, offen, §12) | §8.10 | Wirkung von 0,1° an einem Modul auf die Gegenkomponente (A2.7), passend zur E3a-Schwelle; Differenz gegen die Vorhersage, weil eine absolute Schwelle zulässige konstante Modulunterschiede bewerten würde |
| P(unauffällig \| exakt) ≥ 0,8 für E3, sonst nur beschreibend (Schwellen und Rückfall von E3 offen, §12) | A9.11 | dieselbe Schwelle 0,8 wie die gemeinsame Bedingung von H1 und H2 (§5.4) und die Zuordnung; ohne sie wäre „unbestimmt“ der erwartete Ausgang |
| Bonferroni über die E3-Prüfungen, einseitig α = 0,05 (Zahl der Prüfungen offen, §12) | §8.10, A9.13 | „auffällig“ soll bei korrekter Funktion selten sein, obwohl viele Konfigurationen geprüft werden |
| Zelllage ≤ 0,1 mm, relative Zellverstärkung ≤ 0,1 % (Ziel) | P0.1 | Beitrag zur E3a-Prüfgröße etwa 0,017° je Zelllagefehler (A2.7, Beispiel G0, Zellradius 0,1 m), klein gegen 0,1° |
| Spalt ≥ 10 mm oder offene Grundplatte | §5.1 | Quetschfilm-Trägheit (Teil von m_hyd) dann höchstens etwa 8 g, Gleichanteil vernachlässigbar (Tabelle C) |
| Sinusanregung bei f, 2f, 3f in Höhe der Betriebslast je Zelle, über den Modulpositionen, nach P0.9 (Zeitpunkt offen, §12); Linearitätslauf mit Amplitudenverhältnis 2 (Zeitpunkt und Bezugsamplitude offen, §12) | §5.2, P0.4, P0.12 | prüft die Linearität jeder Zelle bei ihrer Last im Betrieb, die erst mit f feststeht; Verhältnis 2 wie in P0.4, gerade Harmonische dann vierfach bei quadratischer Kennlinie |
| mindestens fünf Umschaltungen je Richtung bei zweitem Nockensatz; Streuung von Δδⱼ ≤ u(Δδⱼ) (Kriterium offen, §12) | P0.5′ | die Umschaltung wird in Phase 1 etwa neunmal je Block nötig; ihre Streuung soll nicht größer sein als die zugelassene Unsicherheit der Profilphase |

---

## Z · Zahlennachweis

Alle Befehle aus dem Wurzelverzeichnis des Repositorys. `--section`, `--phi3` und `--f` liegen seit Commit
`069cb9b` in `code/linear_solver.py` (§12, Werkzeug 1); mit diesem Stand sind die Zahlen nachgerechnet. Ein Einzelmodullauf wird als synchrone Phasung mit μ/3 gerechnet. ζ fest
heißt C = 2ζ√(KM) mit ζ = 0,099228. „Repo“: Zahl aus einem Repository-Dokument, hier nachgerechnet. „Zitat“:
Zahl aus einem Dokument oder einer Quelle, die nicht gerechnet wird. Festlegungen (Tabelle F) sind gewählt,
nicht gerechnet. „BL(KM; ARGS)“ heißt bandbegrenzt auf k ≤ KM:
`python3 -c "import sys;sys.path.insert(0,'code');import linear_solver as L;P,n=L.profile_spectrum();km=KM;P[km+1:]=0;L.profile_spectrum=lambda *a,**k:(P.copy(),n);L.section(ARGS)"`
mit ARGS = `None,0,0.4` (starr, μ = 0,4), `K,L.c_for(K,Z),0.4` oder `1e4,16,1.0` (Referenz). Stelle: „§“
Hauptdokument; A0–A9, Tab. C, Tab. F und Z Anhang.

| Zahl | Stelle | Befehl |
|---|---|---|
| F_min 5,3304 N (120°), 0,7677 N (100°), 1,6176 N (140°); 2°-Sekanten 0,2124 und 0,1952 N/° (0,212 und 0,195); ΔF_Zelt 4,5627 N | §1; A2.2, A3, A4 | `python3 code/linear_solver.py --section` |
| 20°-Sekanten 0,228 und 0,186 N/° (Exposé ≈ 0,23 / ≈ 0,19, Repo) | A3 | `python3 -c "print(round((5.3304-0.7677)/20,3), round((5.3304-1.6176)/20,3))"` |
| f_n = 19,74 Hz; 2f/f_n = 1,013; \|H₂\| = 5,03; 2°-Sekanten 0,09–0,12 N/° bei ζ fest, K = 3·10⁴ … 10⁷ N/m (Repo) | A3 | `python3 code/linear_solver.py --harmonics` |
| 4,24 %; 2 × 2524 Punkte (3,90 %); 6 × 74 Punkte (0,34 %); λ = 75,82 % bzw. 0 % bei (35°, 116°); 76,6 % starr; 48,6 % bei μ = 0,5 (Repo) | A3 | `python3 code/linear_solver.py --contact`; `python3 -c "print(round(100*5048/360**2,2), round(100*444/360**2,2))"`; Monostabilität: `python3 code/linear_solver.py --contact --grid` (ca. 6–8 min) |
| ζ = 0,099228; M·g = 6,3765 N | A3, Z | `python3 -c "print(round(16/(2*(1e4*0.65)**0.5),6), round(0.65*9.81,4))"` |
| γ₁ = +0,067 (K = 10⁴ N/m) und −0,450 (starr) am Triphasik-Punkt; A 0,6529 starr μ = 0,4 | §1; A2.3, A3, A4 | `python3 code/linear_solver.py --point 120 240`; `python3 code/linear_solver.py --point 120 240 --rigid` (ebenso mit `--mu 0.4`) |
| Schiefe des Referenzrasters: 55 Punkte auf φ₂ = 0°, φ₃ = 0°, φ₂ = φ₃, γ₁ ≥ +0,596, davon 0 negativ; 36 negative Werte insgesamt | §1; A3 | `python3 -c "import pandas as pd,numpy as np;d=pd.read_csv('data/sweep_19x19.csv');a,b=d.phi2_deg,d.phi3_deg;m=np.isclose(a,0)+np.isclose(b,0)+np.isclose(a,b);print(m.sum(),round(d.F_skew[m].min(),3),int((d.F_skew[m]<0).sum()),int((d.F_skew<0).sum()))"` |
| s_m = −0,196, +0,206, −0,011 N/°, Summe −5·10⁻⁵ | A2.2 | `python3 -c "import sys; sys.path.insert(0,'code'); import linear_solver as L; t,N=L.waveform(120,240); d=(L.waveform(120.0001,240)[1]-L.waveform(119.9999,240)[1])/0.0002; i=[j for j in range(len(N)) if N[j]<=N[j-1] and N[j]<=N[(j+1)%len(N)]]; i=sorted(sorted(i,key=lambda j:N[j])[:3]); print([round(float(d[j]),3) for j in i], round(float(sum(d[j] for j in i)),5))"` |
| lokale Steigungen 0,207 und 0,196 N/°; F_min 5,3097 / 5,3304 / 5,3108 N bei 119,9° / 120° / 120,1° | A2.2 | `python3 code/linear_solver.py --point 119.9 240`, ebenso `120 240`, `120.1 240`; `python3 -c "print(round((5.330390-5.309711)/0.1,3), round((5.330390-5.310811)/0.1,3))"` |
| Schiefeformel: cos(2ϑ₃ − ϑ₆) = −1,000 bzw. +0,912; γ₁(k ≤ 6) = −0,3775 bzw. +0,0658 | A2.3 | `python3 -c "import sys;sys.path.insert(0,'code');import linear_solver as L,numpy as np;P,n=L.profile_spectrum();[print(K,[round(float(v),4) for v in (np.cos(2*np.angle(X[3])-np.angle(X[6])),0.75*abs(X[3])**2*abs(X[6])*np.cos(2*np.angle(X[3])-np.angle(X[6]))/((abs(X[3])**2+abs(X[6])**2)/2)**1.5)]) for K,C in ((None,0.0),(1e4,16.0)) for X in [P*L.transfer(K,C,P.size)[0]]]"`; Gegenprobe BL(6; `None,0,0.4`) und BL(6; `1e4,16,1.0`), Zeile 120° |
| Jitterfaktoren 0,99985 / 0,99939 / 0,99863 / 0,99453 / 0,98774 | A2.4 | `python3 -c "import numpy as np; s=np.radians(1.0); print([round(float(np.exp(-k*k*s*s/2)),5) for k in (1,2,3,6,9)])"` |
| Einzelmodul bei den Referenzparametern: lineares F_min = −2,057 N | A3 | `python3 code/linear_solver.py --point 0 0 --mu 0.3333333333333333` |
| gespiegelter Schnitt: F_min 3,0846 N, γ₁ −0,3846 | A3 | `python3 code/linear_solver.py --point 110 240`; `python3 code/linear_solver.py --point 240 110` |
| starr, μ = 0,4, 10 Hz: Kontaktast auf allen 21 Punkten; F_min 5,6452 / 5,1759 / 5,4581 / 5,3379 N (120° / 100°, 140° / 116° / 112°, 128°); 2°-Sekanten 0,0469 / 0,0468 N/°; γ₁ −0,4498 (120°), −0,7932 (100°, 140°); F_max 7,0752 N (7,08 N) | A2.2, A4 | `python3 code/linear_solver.py --section --rigid --mu 0.4` |
| starr, μ = 0,4, 14 / 19 / 20 Hz: F_min 4,9432 / 4,0233 N, 3,7365 / 2,0424 N, 3,4513 / 1,5741 N; 2°-Sekanten 0,0918, 0,1691, 0,1874 N/°; γ₁ und A unverändert; Kontaktast auf allen Punkten | A4 | `python3 code/linear_solver.py --section --rigid --mu 0.4 --f 14` (ebenso `--f 19`, `--f 20`) |
| Liftoff am Schnittrand zwischen 23 und 24 Hz: F_min(100°) 0,0254 bzw. −0,5389 N | A4 | `python3 code/linear_solver.py --section --rigid --mu 0.4 --f 23` bzw. `--f 24` |
| Einzelmodul (starr, μ = 0,4): F_min 5,3642 N, F_max 8,2564 N, γ₁ +0,755 (10 Hz); F_min 1,9124 (21 Hz), 1,4771 (22 Hz), 0,0498 (25 Hz), −0,4664 N (26 Hz) | A4 | `python3 code/linear_solver.py --point 0 0 --rigid --mu 0.13333333333333333 --f F` mit F = 10, 21, 22, 25, 26 |
| synchron (starr, μ = 0,4): F_min 3,3397 N, F_max 12,0163 N, γ₁ +0,755 (10 Hz); F_min 2,0035 (12 Hz), 1,2443 (13 Hz), 0,4244 (14 Hz), −0,4563 N (15 Hz) | A4 | `python3 code/linear_solver.py --point 0 0 --rigid --mu 0.4 --f F` mit F = 10, 12, 13, 14, 15 |
| (0°, 180°) (starr, μ = 0,4): F_min 5,0340 N, F_max 9,1241 N, γ₁ +0,986 (10 Hz); F_min 2,0268 (18 Hz), 1,5300 (19 Hz), 0,4560 (21 Hz), −0,1213 N (22 Hz) | A4 | `python3 code/linear_solver.py --point 0 180 --rigid --mu 0.4 --f F` mit F = 10, 18, 19, 21, 22 |
| Anteile an M·g: 81,2; 63,1; 32,0; 24,7; 12,0 %; 52,4 / 31,4 / 19,5 % (synchron bzw. je Zelle 10 / 12 / 13 Hz); 78,9 / 31,8 / 24,0 % ((0°, 180°) 10 / 18 / 19 Hz); 30,0 / 23,2 % (Einzelmodul 21 / 22 Hz) | A4 | `python3 -c "Mg=6.3765; print([round(100*x/Mg,1) for x in (5.1759,4.0233,2.0424,1.5741,0.7677,3.3397,2.0035,1.2443,5.0340,2.0268,1.5300,1.9124,1.4771)])"` |
| Zellkraft: statisch 2,1255 N, höchstens 4,0054 N | A4 | `python3 -c "print(round(6.3765/3,4), round(12.0163/3,4))"` |
| ΔF_Zelt 0,4693 / 0,9199 / 1,6941 / 1,8772 / 4,5627 N; äußere Steigung 0,0135 N/°; innere 0,0468 N/°; Faktoren 1,96 und 4,0 | A4 | `python3 -c "print([round(a-b,4) for a,b in ((5.6452,5.1759),(4.9432,4.0233),(3.7365,2.0424),(3.4513,1.5741),(5.3304,0.7677))], round((5.3379-5.1759)/12,4), round((5.6452-5.4581)/4,4), round(0.0918/0.0469,2), round(0.1874/0.0469,2))"` |
| Knicke bei etwa 114° und 126° (114,01° und 125,98°) | §12; A4 | `python3 -c "a=(5.3379-5.1759)/12; b=(5.6452-5.4581)/4; c=(5.6452-5.4580)/4; print(round((5.6452-120*b-5.1759+100*a)/(a-b),2), round((5.1759+140*a-5.6452-120*c)/(a-c),2))"` |
| K = 10⁶ N/m (ζ fest) gegen starr, μ = 1: \|N_k\| +0,3 / 1,0 / 2,4 % (10 Hz: 9,7522 / 3,2391 / 1,4158 gegen 9,7272 / 3,2059 / 1,3832 N), +0,9 / 3,8 / 9,1 % (19 Hz: 35,4435 / 12,0178 / 5,4457 gegen 35,1153 / 11,5732 / 4,9932 N) | §8.7; A4, A9.7, Tab. F | `python3 code/linear_solver.py --section --K 1e6 --zeta 0.099228` und `python3 code/linear_solver.py --section --rigid` (Kopfzeile), ebenso mit `--f 19`; `python3 -c "print([round(100*(a/b-1),1) for a,b in ((9.7522,9.7272),(3.2391,3.2059),(1.4158,1.3832),(35.4435,35.1153),(12.0178,11.5732),(5.4457,4.9932))])"` |
| Kontaktanteil \|N̂_k⁽ʲ⁾ − G_F·m_j·a_k⁽ʲ⁾\|/\|N̂_k⁽ʲ⁾\| = \|H − 1\|/\|H\| für k = 1, 2, 3 (K = 10⁶ N/m, ζ fest, 10 Hz): 0,3 / 1,0 / 2,3 %; nicht zu verwechseln mit der Abweichung des Betrags vom starren Wert, \|H\| − 1 = 0,3 / 1,0 / 2,4 % (Zeile davor) | §8.7; A4, A9.7, Tab. F | `python3 -c "import sys;sys.path.insert(0,'code');import linear_solver as L;H,Y=L.transfer(1e6,L.c_for(1e6,0.099228),4);print([round(float(100*abs(H[k]-1)/abs(H[k])),1) for k in (1,2,3)])"` |
| \|H(kω)\| = 1,024 / 1,101 / 1,259 für k = 3, 6, 9 (K = 10⁶ N/m, ζ fest, 10 Hz); 10 % und 26 % | A4 | `python3 -c "import numpy as np; M=0.65; K=1e6; C=2*0.099228*(K*M)**0.5; print([round(abs((K+1j*w*C)/(K-M*w*w+1j*w*C)),3) for w in 2*np.pi*10*np.array([3,6,9])])"` |
| F_min(120°) 5,5620 N (K = 10⁶ N/m, ζ fest, μ = 0,4) gegen 5,6452 N: 0,083 N, 18 % von 0,4693 N | A4 | `python3 code/linear_solver.py --section --K 1e6 --zeta 0.099228 --mu 0.4`; `python3 -c "print(round(5.6452-5.5620,4), round(100*(5.6452-5.5620)/0.4693,1))"` |
| Δ(F_min) = 0,1293 N bei k_max = 9 (ΔF_Zelt 0,5173 N); notwendig u_c < 0,0786 N (ν → ∞) bzw. 0,0748 N (ν = 19); Auslegung (294 Intervalle) u_c ≤ 0,0258 N (ν → ∞) bzw. 0,0248 N (ν = 19), 0,39 % von M·g; Re/Im N₁ in Fassung A: Δ = 0,1126 N, u_c ≤ 0,0225 N | §8.10; A4, A8 | `python3 -c "from scipy.stats import norm,t; D=0.25*0.5173; print(round(D,4), round(D/norm.ppf(0.95),4), round(D/t.ppf(0.95,19),4), round(D/5.012,4), round(D/5.208,4), round(100*D/5.208/6.3765,2), round(0.25*0.4504,4), round(0.25*0.4504/5.012,4))"`; 0,5173 N aus BL(9; `None,0,0.4`), 0,4504 N aus `python3 code/linear_solver.py --section --rigid --mu 0.4` (\|N_1\| bei 100°) |
| Auslegungsgrenze Δ_q/u_c ≥ 5,012 (ν → ∞) bzw. 5,208 (ν = 19) für 294 Intervalle, 0,8^(1/294) = 0,99924; gegen eine Vorhersage (147 Intervalle) 4,816 bzw. 5,004, 0,8^(1/147) = 0,99848; Fassung vom 25.09.2026 (147 Intervalle) 6,754 bzw. 8,320; t_eq = 1,645 (ν → ∞) bzw. 1,729 (ν = 19); Φ(−3,583) = 1,7·10⁻⁴ | §8.5; A4, A8 | `python3 -c "import numpy as np; from scipy import integrate, optimize; from scipy.stats import norm,t,chi2; c=norm.ppf(1-0.05/294); d=lambda s,nu: chi2.pdf(nu*s*s,nu)*2*nu*s; te=lambda nu: t.ppf(0.95,nu); cb=lambda nu: t.ppf(1-0.05/294,nu); fn=lambda R,nu,p: integrate.quad(lambda s:(2*norm.cdf(R-te(nu)*s)-1)*(R>te(nu)*s)*d(s,nu),0,5,limit=400,points=[R/te(nu)])[0]-p; fo=lambda R,nu,p: integrate.quad(lambda s:(2*norm.cdf(min(R-cb(nu)*s,cb(nu)*s))-1)*(min(R-cb(nu)*s,cb(nu)*s)>0)*d(s,nu),0,5,limit=400,points=[R/(2*cb(nu))])[0]-p; [print(m, round(p,5), round(norm.ppf(0.95)+norm.ppf((1+p)/2),3), round(optimize.brentq(fn,2,20,args=(19,p)),3)) for m in (294,147) for p in [0.8**(1/m)]]; p=0.8**(1/147); print(round(c+norm.ppf((1+p)/2),3), round(optimize.brentq(fo,2,20,args=(19,p)),3), round(norm.ppf(0.95),3), round(te(19),3), float('%.2g'%norm.sf(c)))"` |
| Grenze 4,816 gegen beide Vorhersagen: Bestätigung etwa 0,64 (unabhängig, 0,8²) bzw. 0,65 (Korrelation 0,5 von r⁰ und r¹, ν → ∞); nötig bei Korrelation 0,5: 5,007; ebenso 0,8² = 0,64 für zwei getrennte 0,8-Bedingungen von H1 und H2 bei Unabhängigkeit | A0, A8, Tab. F | `python3 -c "from scipy import integrate, optimize; from scipy.stats import norm; te=norm.ppf(0.95); P=lambda a,r: integrate.quad(lambda x: norm.pdf(x)*(norm.cdf((a-r*x)/(1-r*r)**0.5)-norm.cdf((-a-r*x)/(1-r*r)**0.5)),-a,a,epsabs=1e-13,epsrel=1e-13)[0]; print(round(0.8**2,2), round(P(4.816-te,0.5)**147,2), round(optimize.brentq(lambda R: P(R-te,0.5)**147-0.8,4,7),3))"` |
| Bisheriger Zusatz „Abweichung nachgewiesen, kleiner als Δ_rel“ neben „nicht entscheidbar“ an der Auslegungsgrenze (ein Test, eine Vorhersage, Δ_rel = Δ_q, Δ_q/u_c = 5,012, ν → ∞, c = c_B = 3,583): P = 0,986 bei wahrer Abweichung 1,25·Δ_rel (mit c = 3,9 statt c_B: 0,987) | A0 | `python3 -c "from scipy.stats import norm; u=1/5.012; d=1.25; p=lambda a,c: norm.sf((a+c*u-d)/u)+norm.cdf((-a-c*u-d)/u); print([round(float(p(0,c)-p(1,c)),3) for c in (3.9,3.583)])"` |
| Kammfaktor auf dem Schnitt höchstens 0,116 (k = 1) und 0,228 (k = 2), 0,882 … 1 (k = 3) | A8 | `python3 -c "import numpy as np; p=np.radians(np.arange(100,141,2)); [print(k, round(float(abs((1+np.exp(-1j*k*p)+np.exp(-1j*k*np.radians(240)))/3).min()),3), round(float(abs((1+np.exp(-1j*k*p)+np.exp(-1j*k*np.radians(240)))/3).max()),3)) for k in (1,2,3)]"` |
| Δ_q für N₁, N₂, N₃ (starr, μ = 0,4, 10 Hz): Fassung A 0,1126 / 0,0731 / 0,1383 N, Fassung B (Durchmesser) 0,2218 / 0,1374 / 0,0799 N | §12; A0, A4, A8 | `python3 -c "import sys;sys.path.insert(0,'code');import linear_solver as L,numpy as np;P,n=L.profile_spectrum();p=np.radians(np.arange(100,141,2));[print(k, round(0.25*abs(z).max(),4), round(0.25*abs(z[:,None]-z[None,:]).max(),4)) for k in (1,2,3) for z in [2*0.4*L.M*P[k]*(1+np.exp(-1j*k*p)+np.exp(-1j*k*np.radians(240)))/3/n]]"` |
| Einfederung eines Einzelmodullaufs bei K = 10⁶ N/m (ζ fest, μ = 0,4, 10 Hz): \|x_k\| = 1,30 / 0,43 / 0,19 µm, 1 % davon 13 / 4,3 / 1,9 nm | A4 | `python3 -c "import sys;sys.path.insert(0,'code');import linear_solver as L;P,n=L.profile_spectrum();K=1e6;H,Y=L.transfer(K,L.c_for(K,0.099228),4);x=[float(1e9*abs(2*0.4*L.M/3*P[k]*Y[k])/n) for k in (1,2,3)];print([round(v/1e3,2) for v in x],[round(v/100,1) for v in x])"` |
| Überdeckungsschwelle 0,936 (0,95 minus zwei Standardfehler bei 1000 Kampagnen) | §8.6, §12; A0, A9.6, A9.11, Tab. F | `python3 -c "print(round(0.95-2*(0.95*0.05/1000)**0.5,3))"` |
| Maximum bei 106° (5,2096 N; 5,1342 N bei 120°) für μ = 0,4, f_n = 120 Hz, ζ = 0,02; K = 369 518 N/m | A5 | `python3 code/linear_solver.py --section --K 369518 --zeta 0.02 --mu 0.4`; `python3 -c "import math; print(round(0.65*(2*math.pi*120)**2))"` |
| bandbegrenzt k_max = 6: Spitze 120°, 2°-Sekante 0,0339 N/° (f_n = 120 Hz, ζ = 0,02) bzw. 0,0331 N/° (starr); k_max = 6 = ⌊120/(2·10)⌋ | A5 | BL(6; `369518,L.c_for(369518,0.02),0.4`) bzw. BL(6; `None,0,0.4`), letzte Zeile |
| Spitze bei 120° für K = 3·10⁴, 10⁵, 10⁶, 10⁷ N/m (ζ fest) und starr | A5 | `python3 code/linear_solver.py --section --K 3e4 --zeta 0.099228` (ebenso `1e5`, `1e6`, `1e7`); `python3 code/linear_solver.py --section --rigid`; letzte Zeile |
| 3f = f_n/2 (f_n = 60 Hz, K = 92 379 N/m, ζ fest, μ = 1): F_min(120°) 3,4258 N gegen 4,5483 N starr | A5 | `python3 code/linear_solver.py --section --K 92379 --zeta 0.099228`; `python3 code/linear_solver.py --section --rigid`; `python3 -c "import math; print(round(0.65*(2*math.pi*60)**2))"` |
| \|H\| ≤ 1,33 und d ln\|H\|/d ln f ≤ 0,67 bei k·f/f_m = 0,5, ζ → 0; numerisch für r ≤ 0,5 und jedes ζ ≤ 2 (Maxima 1,3333 und 0,6667) | §5.3; A6, Tab. F | `python3 -c "r=0.5; print(round(1/(1-r*r),3), round(2*r*r/(1-r*r),3))"`; `python3 -c "import numpy as np; r=np.linspace(1e-4,0.5,5001); z=np.linspace(0,2,2001)[:,None]; lh=lambda r:0.5*np.log((1+4*z*z*r*r)/((1-r*r)**2+4*z*z*r*r)); h=1e-6; d=(lh(r+h)-lh(r-h))/(2*h)*r; print(round(float(np.exp(lh(r)).max()),4), round(float(d.max()),4))"` |
| bandbegrenzt, starr, μ = 0,4: k_max = 9: 2°-Sekante 0,0343 N/°, F_min 5,6781 N (120°) und 5,1608 N (100°), ΔF_Zelt 0,5173 N, γ₁(120°) −0,4305; k_max = 6: γ₁ −0,3775; k_max = 3, 4, 5: γ₁ 0 | A6 | BL(9; `None,0,0.4`), BL(6; …), BL(5; …), BL(4; …), BL(3; …): Zeilen 100°, 120° und letzte Zeile |
| H1-äquivalente Spitzenverschiebung im Beispiel A4 (starr, μ = 0,4, 10 Hz, k_max = 9): Δ_q(F_min)/2°-Sekante = 0,1293 N/(0,0343 N/°) = 3,77° (≈ 3,8°) | §9.4; A4, Tab. F | `python3 -c "print(round(0.1293/0.0343,2))"`; 0,1293 N und 0,0343 N/° aus BL(9; `None,0,0.4`) wie oben |
| Auslegungsgrenze u_c ≤ Δ_q/5,012 für Re und Im N₁ / N₂ / N₃ in Fassung B (starr, μ = 0,4, 10 Hz, ν → ∞): 0,0443 / 0,0274 / 0,0159 N | A4, A8 | `python3 -c "print([round(x/5.012,4) for x in (0.2218,0.1374,0.0799)])"`; Δ_q aus der Zeile „Δ_q für N₁, N₂, N₃“ |
| Toleranz von Fassung A in % der Änderung entlang des Schnitts (Durchmesser aus Fassung B) für N₁ / N₂ / N₃ (starr, μ = 0,4, 10 Hz): 12,7 / 13,3 / 43,3 % (Fassung B: 25 %) | §12; A0, A8, Tab. F | `python3 -c "print([round(100*a/(b/0.25),1) for a,b in ((0.1126,0.2218),(0.0731,0.1374),(0.1383,0.0799))])"`; Δ_q aus der Zeile „Δ_q für N₁, N₂, N₃“ |
| Laufzahlfaktor bei Faktor 0,1 statt 0,25 in Δ_q (nötige Laufzahl etwa mit dem Kehrwert des Quadrats): (0,25/0,1)² = 6,25, etwa 6-fach | §12; A0, Tab. F | `python3 -c "print(round((0.25/0.1)**2,2))"` |
| Rechenbeispiel Reichweite (starr, μ = 0,4, 10 Hz, k_max = 9): Das größte Residuum von F_min − ⟨N⟩ erreicht Δ(F_min) = 0,1293 N bei einer gemeinsamen Kopplung aller Module von 0,1293/1,2157 = 10,64 % (≈ 10,6 %; linear) | §2; A0, A4, Tab. F | `python3 -c "print(round(100*0.1293/1.2157,2))"`; 0,1293 N aus BL(9; `None,0,0.4`), 1,2157 N aus der Zeile „Kopplung im Beispiel A4“ |
| Abtastrate f_s ≥ 6,3 kHz bei k_max = 9, f = 10 Hz; f_clk ≥ 360 kHz für 0,01° bei 10 Hz | A6, A9.1 | `python3 -c "import math; print(round(math.pi*9*10/(2e-3)**0.5), 360*10/0.01)"` |
| Median-Versatz, Egg-Profil (Einzelmodul, starr): med(u) = −0,368 (numerisch und geschlossen), γ₁ +0,755; 0,2–0,5 % bei s_N = 0,54–1,36 % von M·g; Faktor 2,9 gegenüber −γ₁/6; umgekehrtes Vorzeichen +0,368; Sinus 0 | A9.1, Tab. C | `python3 -c "import numpy as np;p=np.arange(2*10**6)/2e6;w=lambda h:(lambda a:a-a.mean())(np.where(p<h,-np.sin(np.pi*p/h)/h**2,np.sin(np.pi*(p-h)/(1-h))/(h*(1-h))));x=w(0.65);s=x.std();m=float(np.median(x)/s);g=float(np.mean(x**3)/s**3);print(round(m,3),round(-np.sqrt(2*0.35/0.65)*np.sin(np.pi*(1-1/1.3)/2),3),round(g,3),round(0.2/-m,2),round(0.5/-m,2),round(m/(-g/6),1),round(float(np.median(-x)/s),3),round(abs(float(np.median(w(0.5)))),6))"` |
| Pilotkonfigurationen: zyklische Abstände 110/140/110, 130/100/130, 110/142/108 (nicht äquivalent, paarweise verschieden); Beispiele 110/120/130 und 120/130/110 (äquivalent) | §5.4; A7 | `python3 -c "g=lambda a,b:(lambda s:[s[1]-s[0],s[2]-s[1],360-s[2]])(sorted([0,a,b]));c=lambda x:min(tuple(x[i:]+x[:i]) for i in range(3));S={c(g(*q)) for p in range(100,141,2) for q in ((p,240),(240,p))};[print((a,b),g(a,b),c(g(a,b)) in S) for a,b in ((110,250),(130,230),(110,252),(110,230),(120,250))];print(len({c(g(a,b)) for a,b in ((110,250),(130,230),(110,252))}))"` |
| Pilotkonfigurationen im Modell: Referenz F_min 1,6016 / 1,8699 / 1,3164 N (Kontaktast); starr, μ = 0,4: 5,1742 / 5,3253 / 5,1472 N; Beispiele: 3,4139 N wie (130°, 240°) | A7 | `python3 code/linear_solver.py --point 110 250` (ebenso `130 230`, `110 252`, `110 230`, `120 250`), jeweils auch mit `--rigid --mu 0.4`; `python3 code/linear_solver.py --section` (Zeile 130°) |
| 81,1 / 83,5 / 80,7 % von M·g | A7 | `python3 -c "print(round(100*5.1742/6.3765,1), round(100*5.3253/6.3765,1), round(100*5.1472/6.3765,1))"` |
| kritische Werte 3,583 / 5,586 / 4,356 / 4,060 (H1), 2,991 / 4,075 / 3,435 / 3,269 (H3), 2,852 / 3,780 / 3,236 / 3,094 (H4), 3,860 / 6,485 / 4,842 / 4,460 (H1Z); 1,645 | §3, §8.4, §8.5; A8 | `python3 -c "from scipy.stats import norm,t; [print(m,s,round(norm.ppf(1-0.05/(s*m)),3),[round(float(t.ppf(1-0.05/(s*m),v)),3) for v in (9,19,29)]) for m,s in ((147,2),(18,2),(23,1),(441,2))]; print(round(norm.ppf(0.95),3))"` |
| Zählungen: 147 = 21·7, 18 = 3·3·2, 23 = 21 + 2, 42 = 2·21; 565 = (23 + 5)·20 + 5·1 Läufe, davon 460 Kombinations-, 63 Einzelmodul- und 42 Referenzläufe, 523 mit G1, 21 Kontrollsätze; 15 = 5 + 10 je Messtag; familienübergreifend 0,10 und 0,20, mit H1Z 0,25; mit Identifizierbarkeitsläufen 688 = (23 + 3 + 8)·20 + 8·1 Läufe, davon 520 Kombinations-, 126 Einzelmodul- und 42 Referenzläufe, 646 mit G1; 18 = 8 + 10 je Messtag; H1Z 441 = 3·21·7 Tests, 882 = 2·441 | §3, §5.3, §8.4, §9.2; A8, A9.12 | `python3 -c "print(21*(1+2*3), 3*3*2, 21+2, 2*21, (23+5)*20+5*1, 20*23, 3*(1+20), (1+20)+20+1, (23+5)*20+5-((1+20)+20+1), 1+20, 5+10, 2*0.05, 4*0.05, 5*0.05, (23+3+8)*20+8*1, 20*26, 6*(1+20), (23+3+8)*20+8-((1+20)+20+1), 8+10, 3*21*7, 2*3*21*7)"` |
| 1,371·Δ (reine Power-Bedingung, ν → ∞) | A8 | `python3 -c "from scipy.stats import norm; c=norm.ppf(1-0.05/294); print(round(2*c/(c+norm.ppf(0.95)),3))"` |
| Aufnahmeschwelle für V: 4,881 (n_min = 20), 4,497 (ν → ∞); Bestätigung an der Schwelle etwa 93 % je Punkt (0,932), 95 % für ν → ∞, 23 unabhängige Punkte etwa 0,20 | A8, Tab. F | `python3 -c "from scipy.stats import norm,t,nct; c=t.ppf(1-0.05/23,19); c0=norm.ppf(1-0.05/23); p=nct.sf(c,19,c+1.645); print(round(c+1.645,3), round(c0+1.645,3), round(p,3), round(norm.sf(-1.645),3), round(p**23,2))"` |
| Standardfehler 0,0069 (eine Rate aus 1000 Kampagnen), 0,0097 (Prüfrate mit aus 1000 Kampagnen geschätztem c); Schwelle 0,069; mit 0,05 plus zwei Standardfehlern nur der Prüfung überschritten in etwa 8 % (0,079) | §8.4; A8, Tab. F | `python3 -c "from scipy.stats import norm; print(round((0.05*0.95/1000)**0.5,4), round((0.05*0.95*2/1000)**0.5,4), round(0.05+2*(0.05*0.95*2/1000)**0.5,3), round(norm.sf(2*(0.05*0.95/1000)**0.5/(0.05*0.95*2/1000)**0.5),3))"` |
| G1 0,61 % bis 1,5 % je Lauf; S1 über G1 2,5·10⁻⁴ je Lauf; Nullpunktalarm 7,3·10⁻⁴ je Referenzlauf und Kanal; Kampagne ≈ 0,25 (523 G1-Läufe, 42·4 Referenzkanäle), je weiterer Messtag ≈ 0,0066; mit Identifizierbarkeitsläufen ≈ 0,28 (646 G1-Läufe), je weiterer Messtag ≈ 0,007 | §9.2; A8 | `python3 -c "import numpy as np; from scipy.stats import norm; g=np.random.default_rng(1); R=g.standard_normal((400000,42)); s=(R[:,1:-1]-(R[:,:-2]+R[:,2:])/2).std(1,ddof=1); q=lambda v: 2*norm.sf(3*s/v**0.5); p1=(q(2)*q(1.5)).mean(); x,y,z=g.standard_normal((3,s.size)); t=3*(4/3)**0.5*s; p2=((abs(x-z)>t)&(abs(y-z)>t)).mean(); print(float('%.2g'%q(1.5).mean()), float('%.2g'%q(2).mean()), float('%.2g'%p1), float('%.2g'%p2), round(523*p1+168*p2,2), round(3*p1+8*p2,4), round(646*p1+168*p2,2), round(6*p1+8*p2,3))"` |
| S3: c_S = 3,503 (n₀ⱼ = 20); höchstens 5 % je Kontrollsatz (exakt 0,05); Reproduktion höchstens 9,5·10⁻⁴; 21 Kontrollsätze höchstens 0,020 | §9.2; A8 | `python3 -c "import numpy as np; from scipy.stats import t; g=np.random.default_rng(2); n=2000000; c=t.ppf(1-0.05/42,19); Z=g.standard_normal((n,20)); m=Z.mean(1); u=Z.std(1,ddof=1)*(1+1/20)**0.5; x,y=g.standard_normal((2,n)); a=abs(x-m)>c*u; b=abs(y-m)>c*u; print(round(c,3), round(42*t.sf(c,19),4), round(21*a.mean(),4), float('%.2g'%(21*(a&b).mean())), round(21*21*(a&b).mean(),3))"` |
| Varianzverhältnis 4/3 (2σ² gegen 1,5σ²) | §8.8; A9.8 | `python3 -c "print(2/(1+0.25+0.25))"` |
| e⁻¹⁰ ≈ 4,5·10⁻⁵; 57 gepoolte Freiheitsgrade; MAD-Faktor 1,4826 | Tab. F | `python3 -c "import math; from scipy.stats import norm; print(round(math.exp(-10),7), 3*(20-1), round(1/norm.ppf(0.75),4))"` |
| Aufwärmen: ohne Drift nach zehn Referenzläufen etwa 6·10⁻⁴ ohne zwei aufeinanderfolgende mit Differenz < σ̂_ref (σ̂_ref = √1,5·σ) | A8, Tab. F | `python3 -c "import numpy as np; g=np.random.default_rng(3); R=g.standard_normal((10**6,10)); print(float('%.1g'%(1-(abs(np.diff(R,axis=1))<1.5**0.5).any(1).mean())))"` |
| Normierung für ε_ctrl: Var(Δ⟨N⟩) = σ²(1 + β² + (1 − β)²), 1,5σ² bei β = 0,5 | §8.8; A1, A9.8 | `python3 -c "b=0.5; print(1+b*b+(1-b)**2)"` |
| Kopplung im Beispiel A4 (starr, μ = 0,4, 10 Hz, k_max = 9): größtes \|F_min − ⟨N⟩\| 1,2157 N; 0,1 % / 1 % Abweichung der Kombinationsläufe → 1,22 / 12,2 mN, 0,9 / 9,4 % von 0,1293 N; Phasenversatz 0,05° an Modul 2 → 1,75 mN bei 120° | §8.10; A4, Tab. C | `python3 -c "import sys;sys.path.insert(0,'code');import linear_solver as L,numpy as np;P,n=L.profile_spectrum();k=np.arange(1,10);N=2*0.4*L.M*P[1:10]/3/n;t=2*np.pi*np.arange(2000)/2000;c=lambda X:(X.real@np.cos(np.outer(k,t))-X.imag@np.sin(np.outer(k,t))).min();f=lambda p,d=0:c(N+N*np.exp(-1j*k*np.radians(p+d))+N*np.exp(-1j*k*np.radians(240)));p=np.arange(100,141,2.);F=np.array([f(x) for x in p]);D=np.array([f(x,0.05) for x in p])-F;m=abs(F).max();print(round(m,4),round(m,2),round(10*m,1),round(100*m*1e-3/0.1293,1),round(100*m*1e-2/0.1293,1),round(1e3*abs(D).max(),2),p[abs(D).argmax()])"` |
| Luft am Körper (Grundfläche 0,04 m², R = 0,113 m, ρ_L = 1,2 kg/m³, μ_L = 1,8·10⁻⁵ Pa·s, 10 Hz): zugesetzte Masse (8/3)·ρ_L·R³ = 4,6 g (0,71 % von 0,650 kg); Quetschfilm mit exakter Impedanz iωπρ_LR⁴/(8hΦ), Φ = 1 − tanh(x)/x, x = h·√(iω/ν)/2: Trägheit 8,2 / 30,1 g, Dämpfung 0,038 / 0,58 N·s/m (h = 10 / 3 mm); Luftanteil von m_L bei Konvention (b) ρ_L·V_außen = 2,2 / 4,8 g (V_außen = 1,8 / 4 l), bei (a) Innenluft höchstens so groß | Tab. C, Tab. F; A1 | `python3 -c "import numpy as np; r,m,w=1.2,1.8e-5,2*np.pi*10; R=(0.04/np.pi)**0.5; print(round(R,4), round(1e3*8/3*r*R**3,1), round(100*8/3*r*R**3/0.65,2)); [print(h, round(1e3*Z.imag/w,1), round(Z.real,3)) for h in (0.01,0.003) for x in [np.sqrt(1j*w*r/m)*h/2] for Z in [1j*w*np.pi*r*R**4/(8*h*(1-np.tanh(x)/x))]]"`; `python3 -c "print([round(1.2*V*1e3,1) for V in (1.8e-3,4e-3)])"` |
| Gleichanteil des Quetschfilms, Skala πρ_LR⁴⟨ż²⟩/(16h²) mit h = 3 mm (ζ fest, μ = 0,4, 10 Hz): K = 10⁶ N/m Einzelmodullauf 2,7·10⁻⁸ N (\|x₁\| = 1,30 µm), synchron 2,4·10⁻⁷ N, beide unter 10⁻⁶ N; K = 10⁵ N/m Einzelmodullauf 3,8·10⁻⁶ N (\|x₁\| = 13,3 µm), synchron 3,4·10⁻⁵ N; Kabelschlaufe 100 N/m · 13,3 µm = 1,33 mN | Tab. C | `python3 -c "import sys;sys.path.insert(0,'code');import linear_solver as L,numpy as np;P,n=L.profile_spectrum();R=(0.04/np.pi)**0.5;w=2*np.pi*10*np.arange(P.size);[print(K,round(1e6*abs(x[1]),2),'%.1e'%(np.pi*1.2*R**4*0.5*np.sum(abs(w*x)**2)/(16*0.003**2)),round(1e3*100*abs(x[1]),2)) for K in (1e6,1e5) for Y in [L.transfer(K,L.c_for(K,0.099228),P.size)[1]] for f in (1/3,1) for x in [2*0.4*L.M*f*P*Y/n]]"` |
| Auftrieb auf das Außenvolumen ρ_L·g·V_außen = 0,021 / 0,047 N (V_außen = 1,8 / 4 l), 1 % Dichteänderung 0,21 / 0,47 mN (dicht verschlossenes Gehäuse); Elektrostatik σ²A/(2ε₀) = 2,3·10⁻⁵ / 2,3·10⁻³ / 0,23 N (σ = 10⁻⁷ / 10⁻⁶ / 10⁻⁵ C/m², A = 0,04 m²), Modulation ε₀AU²/(2d²) = 0,044 mN (10 cm², 100 V, 1 mm); Kabelschlaufe 100 N/m · 1,30 µm = 0,13 mN; Spitzengeschwindigkeit des Profils 0,24 m/s (Hub 7,69 mm, 10 Hz), Luftwiderstand je Modul 0,035 mN (10 cm², c_w = 1) | §12; A0, Tab. C | `python3 -c "import sys;sys.path.insert(0,'code');import numpy as np;from finesweep import z_egg_zdd;g=9.81;print([round(1.2*g*V,4) for V in (1.8e-3,4e-3)],[round(1e3*0.012*g*V,2) for V in (1.8e-3,4e-3)],['%.2g'%(s*s*0.04/(2*8.854e-12)) for s in (1e-7,1e-6,1e-5)],round(1e3*8.854e-12*1e-3*1e4/2e-6,3),round(1e3*100*1.30e-6,2));t=np.arange(200000)*(0.1/200000);v=np.cumsum(z_egg_zdd(t))*(0.1/200000);v-=v.mean();u=abs(v).max();print(round(u,2),round(1e3*0.5*1.2*1e-3*u*u,3))"` |
| Auftrieb auf das Materialvolumen und konventioneller Wägewert (Konvention a; M = 0,650 kg, einheitlich Stahl 8000 / Aluminium 2700 / Kunststoff 1200 kg/m³): V_Mat = 0,081 / 0,241 / 0,542 l, ρ_L·g·V_Mat = 0,96 / 2,83 / 6,38 mN, bei 1 % Dichteänderung 0,01 / 0,028 / 0,064 mN (offenes oder belüftetes Gehäuse); konventioneller minus wahrer Wägewert 0 / −0,19 / −0,55 g | §12; A0, A1, A9.2, Tab. C | `python3 -c "g=9.81;M=0.65;[print(r,round(1e3*M/r,3),round(1e3*1.2*g*M/r,2),round(1e3*0.012*g*M/r,3),round(1e3*M*(1.2/8000-1.2/r),2)) for r in (8000,2700,1200)]"` |
| Justierung mit Stahlgewichten (Anzeige in Masseeinheiten, etwa bei der Gesamtwägung): F/g = angezeigte Masse·(1 − ρ_L/(8000 kg/m³)), F Kraft auf die Waage, vergleichbar mit M = Σ_c F_c,stat/g, keine wahre Masse; Faktor 1,5·10⁻⁴, bei M = 0,650 kg 0,96 mN | A9.2 | `python3 -c "print(1.2/8000, round(1e3*0.65*9.81*1.2/8000,2))"` |
| Belüftetes Gehäuse, Temperaturunterschied ΔT innen–außen bei gleichem Druck: ρ_innen − ρ_L ≈ −ρ_L·ΔT/T; Änderung der statischen Last höchstens ρ_L·g·V_innen/T = 0,072 / 0,161 mN je K (obere Schranke mit V_innen ≤ V_außen = 1,8 / 4 l, T = 293 K) | §12 | `python3 -c "print([round(1e3*1.2*9.81*V/293.15,3) for V in (1.8e-3,4e-3)])"` |
| Zelllagefehler (Statik der Dreipunktlagerung, Zellradius 0,1 m, G0, Triphasik-Punkt, Rekonstruktion mit nominaler Lage): 1 mm radial −0,662 % am eigenen Modul, −0,165 % und ±0,165° an den Nachbarn; 1 mm tangential 0,29 % und 0,29° an den Nachbarn; 0,1 mm radial 0,0165° (linear) | A2.7, Tab. F | `python3 -c "import numpy as np;a=np.radians([90,210,330]);C=0.1*np.c_[np.cos(a),np.sin(a)];S=lambda p,Q:np.linalg.solve(np.vstack([np.ones(3),Q.T]),np.r_[1,p]);e=np.exp(-1j*np.radians([0,120,240]));[print(np.round(100*(abs(r)-1),3),np.round(-np.degrees(np.angle(r)),3)) for d in (np.r_[np.cos(a[1]),np.sin(a[1])],np.r_[-np.sin(a[1]),np.cos(a[1])]) for Q in [C+np.outer([0,1,0],1e-3*d)] for r in [np.c_[[S(C[j],Q) for j in range(3)]].T@e/e]];print(round(0.165*0.1,4))"` |
| Gegenkomponente am Triphasik-Punkt: \|R₋₁\|/\|R₊₁\| = 3,3·10⁻³ bei 1 % Amplitude, 5,8·10⁻⁴ bei 0,1° Phase eines Moduls, gleich \|ε\|/3 | §8.10; A2.7, Tab. F | `python3 -c "import numpy as np;th=np.radians([90,210,330]);q=lambda F:(lambda a,b:min(a,b)/max(a,b))(abs((F*np.exp(-1j*th)).sum()),abs((F*np.exp(1j*th)).sum()));e=np.exp(-1j*np.radians([0,120,240]));print('%.1e'%q(e*[1.01,1,1]),'%.1e'%q(e*[np.exp(-1j*np.radians(0.1)),1,1]),'%.1e'%(0.01/3),'%.1e'%(np.radians(0.1)/3))"` |
| Aufwand der Identifizierbarkeitsläufe: (N_K + N_I + 8)/(N_K + 5) = 1,231 / 1,308 (N_K = 21; N_I = 3 / 5) und 1,214 / 1,286 (N_K = 23); Paarläufe zusätzlich 1,094 bzw. 1,088; Residuenverhältnis bei s = 0,5: 1 : 0,5 : 0,25; Abstand der Klassen p = 1 und 2: s·(1 − s) = 0,25 (s = 0,5), s·(s − 1) = 0,56 (s = 1,4) | §5.5, §6, §12; A2.6, Tab. F | `python3 -c "print([round((k+i+8)/(k+5),3) for k in (21,23) for i in (3,5)], round((21+3+3+8)/(21+3+8),3), round((23+3+3+8)/(23+3+8),3), [0.5**p for p in (0,1,2)], 0.5*(1-0.5), round(1.4*(1.4-1),2))"` |
| Betrag \|1 + e^{−ikφ₂} + e^{−ik·240°}\| auf dem Schnitt (Residuum einer Kopplung fester relativer Stärke in N_k bei gleichen Modulen proportional dazu), k = 1 / 2 / 3: 100° und 140° 0,347 / 0,684 / 2,646; 116° und 124° 0,070 / 0,140 / 2,985; 120° 0 / 0 / 3 | §12 | `python3 -c "import numpy as np; [print(p,[float(round(abs(1+np.exp(-1j*k*np.radians(p))+np.exp(-1j*k*np.radians(240))),3)) for k in (1,2,3)]) for p in (100,116,120,124,140)]"` |
| Betriebslast je Zelle (starr, μ = 0,4, 10 Hz, Module über den Zellen): Einzelmodul-Harmonische 1,30 / 0,43 / 0,18 N für k = 1, 2, 3; \|N₁\| auf dem Schnitt höchstens 0,45 N, mittig angeregt je Zelle 0,15 N, Verhältnis 8,6 (etwa ein Neuntel) | §5.2, §12; A9.2 | `python3 -c "import sys;sys.path.insert(0,'code');import linear_solver as L,numpy as np;P,n=L.profile_spectrum();p=np.radians(np.arange(100,141,2));N=[abs(2*0.4*L.M*P[k]/3/n) for k in (1,2,3)];S=abs(2*0.4*L.M*P[1]*(1+np.exp(-1j*p)+np.exp(-1j*np.radians(240)))/3/n).max();print([round(float(x),2) for x in N],round(float(S),2),round(float(S)/3,2),round(float(3*N[0]/S),1))"` |
| Umschaltungen eines zweiten Nockensatzes bei Randomisierung nach §6 (R ohne Einstellung, n = 20, ein Messtag, 5000 Kampagnen): im Mittel 189 bzw. 188 je Kampagne (N_K = 23 bzw. 21, N_I = 3), 9,5 bzw. 9,4 je Block; N_I = 5: 12,4 je Block; Läufe bei Einstellung 2 je Block und Kontrollsatz zusammenhängend: 4,0 je Block | §5.2, §5.5, §6, §12; A9.2, Tab. F | `python3 -c "import numpy as np;g=np.random.default_rng(7);c=lambda q:int((np.diff(np.concatenate(q))!=0).sum());F=lambda NK,NI:c([g.permutation([1]*3+[2]*3)]+[a for _ in range(20) for a in (g.permutation([1]*NK+[2]*NI),g.permutation([1]*3+[2]*3))]);G=lambda m,r:(lambda i:[1]*i+[2]*m+[1]*(r-i))(int(g.integers(0,r+1)));B=lambda NK,NI:c([G(3,3)]+[a for _ in range(20) for a in (G(NI,NK),G(3,3))]);z=[float(np.mean([F(k,i) for _ in range(5000)])) for k,i in ((23,3),(21,3),(23,5))];b=float(np.mean([B(23,3) for _ in range(5000)]));print([round(v) for v in z],[round(v/20,1) for v in z],round(b/20,1))"` |
| Gemeinsame Versorgung als Aktorkopplung (Beispiel A4, k_max = 9): 0,1 % Amplitude von Modul 1 / 2 / 3 nur in den Kombinationsläufen → 1,02 / 1,01 / 1,02 mN größtes \|ΔF_min\| auf dem Schnitt; aller Module 1,22 mN | Tab. C | `python3 -c "import sys;sys.path.insert(0,'code');import linear_solver as L,numpy as np;P,n=L.profile_spectrum();k=np.arange(1,10);N=2*0.4*L.M*P[1:10]/3/n;t=2*np.pi*np.arange(2000)/2000;c=lambda X:(X.real@np.cos(np.outer(k,t))-X.imag@np.sin(np.outer(k,t))).min();f=lambda p,a:c(a[0]*N+a[1]*N*np.exp(-1j*k*np.radians(p))+a[2]*N*np.exp(-1j*k*np.radians(240)));p=np.arange(100,141,2.);F=np.array([f(x,(1,1,1)) for x in p]);print([round(1e3*float(abs(np.array([f(x,a) for x in p])-F).max()),2) for a in ((1.001,1,1),(1,1.001,1),(1,1,1.001),(1.001,)*3)])"` |
| Erreichbarkeit der E3-Schwellen (Beispiel A4, Module über den Zellen, \|N₁⁽ʲ⁾\| = 1,30 N): E3a „unauffällig“ möglich erst bei u ≈ 0,97 mN je Komponente einer Zellharmonischen (1,645·√2·u/1,30 N = 0,1°); q_Z bei exakter Superposition und 1 mN in Messung und Vorhersage im quadratischen Mittel √12·u/(3·1,30 N) = 8,9·10⁻⁴; u(Δδⱼ) ≈ 0,03° für 1,645·u(Δδⱼ) = 0,05° | §8.10, §12 | `python3 -c "import sys;sys.path.insert(0,'code');import linear_solver as L,numpy as np;P,n=L.profile_spectrum();C=float(abs(2*0.4*L.M*P[1]/3/n));u=np.radians(0.1)*C/(1.645*2**0.5);print(round(C,2),round(1e3*u,2),'%.1e'%(12**0.5/3*1e-3/C),round(0.05/1.645,3))"` |
| Zitate: drei Wägezellen im Dreieck genannt; Wegkanal, Encoder und Hilfskanäle erwogen, Kanalzahl offen, Nennlast nicht hergeleitet (Exposé, Nachträge vom 2. Oktober 2026); historisch 10 kg und „11 Kanäle“ bei neun aufgezählten (drei Zellen, Weg, drei Encoder, Beschleunigung, Temperatur; Exposé im Stand des Tags `stand-2026-09-28`); 50,6 N, 7,69 mm, 0,650 kg, 16 N·s/m (README); 2,2 Hz (zehn_fragen); 0,2–0,5 % (v1); Ausgabe 2019 (DKD-R 3-10 Blatt 2; PTB-OAR, Websuche, kein Befehl); vorhandener programmierbarer Linearaktor (historisch: Arbeitspapier v2.4 im Stand des Tags `stand-2026-09-28`, Z. 2104; heutiger Quelltext: Hardwarestand offen, Abschnitt „Hardwarestand Linearaktor“) | §5.1, §12; A0, A3, A4 | `grep -n -e "Erwogen" -e "Kanalzahl" -e "Nennlast der" -e "nicht hergeleitet" docs/expose_2026-09.md`; historisch (Git-Klon mit Tags): `git grep -n -e "10 kg" -e "11 Kanäle" stand-2026-09-28 -- docs/expose_2026-09.md`; `git grep -n -A1 "11 Kanäle:" stand-2026-09-28 -- docs/expose_2026-09.md`; `grep -n -e "50,6 N" -e "7,69 mm" -e "0,650 kg" -e "16 N·s/m" README.md`; `grep -n "2,2 Hz" docs/zehn_fragen.md`; `grep -n "0,2–0,5" docs/praeregistrierung_2026-06.md`; historisch: `git grep -n "bereits vorliegt" stand-2026-09-28 -- docs/arbeitspapier/PCMMS_Arbeitspapier_v2_4.tex`; `grep -n -A1 "Hardwarestand Linearaktor" docs/arbeitspapier/PCMMS_Arbeitspapier_v2_4.tex` |
