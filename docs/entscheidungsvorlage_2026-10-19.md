# Entscheidungsvorlage vom 19.10.2026: Ablaufregeln, G4 und Vollständigkeit, E3, Generator aus Phase 0

Stand `main` 0f63187 (PR #23 gemergt); ergänzt am Abend des 19.10.2026 um die Ergebnisse der Nachprüfung
(Abschnitt 8). Vorlage zu den Punkten a) bis d) der Agenda des Autors vom 18.10.2026; Punkt e)
(realer V1-Pilot) ist zurückgestellt und hier nicht behandelt. Dieses Dokument ändert keine Regel. Es nennt je Punkt
den Ist-Stand mit Fundstellen, die Optionen, eine Empfehlung, die zu ändernden Textstellen, den Aufwand und die
Fragen, die beim Autor liegen. Alle Festlegungen gehören nach §12 zu den Gruppen (I) und (II) und sind als
Arbeitsfestlegung mit Eintrag und Grund in A0 vorgesehen (Entwurf Z. 997–1004).

**Stand 20.10.2026.** Mit dem Auftrag des Autors zur Gesamtumsetzung vom 20.10.2026 sind die Empfehlungen dieser
Vorlage für den Umfang der Umsetzung als Arbeitsvorgaben entschieden (Abschnitt 9). Die große Kalibrierung wird in
diesem Vorhabensteil nicht ausgeführt; das ist eine feste Entscheidung des Autors, weil die Rechenressourcen fehlen
und die vorhandenen Daten synthetisch sind. Sie wird nur als startfreies Beispiel vorbereitet, die
Kalibrierabnahme bleibt offen, und sie ist kein angekündigter nächster Schritt.

**Arbeitsweise und Kennzeichnung.** Grundlage sind der Präregistrierungsentwurf mit Anhang, der Code auf 0f63187, die
Berichte zu PR #21–#23 und deren gespeicherte Ergebnisdateien. Es wurde keine Kampagne mit der Codekette von
Werkzeug 8 gerechnet; die Nachprüfung hat Kampagnen nur auf Ebene der Teststatistik simuliert. Zahlen tragen eine
Herkunft: *gelesen* (steht so in Text, Code oder Ergebnisdatei), *gezählt* (aus gespeicherten Dateien ausgezählt),
*gerechnet* (eigene Rechnung auf Ebene einer Teststatistik, analytisch oder Monte Carlo, Sekunden bis Minuten; die
Skripte, kompakten Eingaben und Ausgaben liegen im Belegpaket `docs/entscheidungsvorlage_2026-10-19_belege/`;
für die E3b-Nachzählung tritt dort eine Rekonstruktion an die Stelle des verlorenen Originalskripts) oder
*Einschätzung*. Abschnitt 8 beschreibt die Nachprüfung dieser Vorlage durch sieben unabhängige Prüfer; Zahlen aus
ihr sind als „gerechnet in der Nachprüfung“ gekennzeichnet. Rechnungen auf Statistikebene sind Modellrechnungen mit
vereinfachten Annahmen; sie begründen Entscheidungen über Regeln, ersetzen aber keine Kalibrierung.

**Ergebnis in Kürze.**

- **a) Ablauf.** Der Präregistrierungstext verlangt an drei Stellen „sofort“ (R₁, S3-Wiederholung,
  Kontrollwiederholung), ohne Reihenfolge. Empfohlen: eine Vorrangregel „begonnene Referenzfolge zuerst“
  (R₁; bei feststehendem Verstoß R₂, X′, R₃; dann die übrigen sofortigen Wiederholungen), beim Halt entfallen
  ausstehende sofortige Folgeläufe, und eine durch einen Halt unvollständige Klammer wird so behandelt wie eine
  durch ungültiges R₂/R₃ unvollständige (S1 nicht prüfbar, keine weitere Wiederholung). Zwei Nachbarfragen gehören
  in denselben Beschluss: was im Kontrollsatz der Wiederaufnahme als „Alarm“ gilt, und ob nach einer Wiederaufnahme
  aufgewärmt wird. Nach einem Nullpunkthalt eröffnet ein gesonderter Referenzlauf vor dem Kontrollsatz der
  Wiederaufnahme einen neuen Bezug R₀; sonst verglichen der Kontrollsatz und jede Vorprüfung weiter mit dem
  wahrscheinlichen Ausreißer. Umsetzung ohne Kampagnenrechnung (`ablauf-4`).
- **b) G4.** Die heutige Schwelle je Laufart schließt an steilen Konfigurationen bis zu 14,7 % der Läufe aus
  (gezählt, PR #22), die Begründung „seltene Fehlausschlüsse“ (Tabelle F) trifft dort nicht zu, und p̂ der Piloten
  (1–2 %) bildet die Phase-1-Ausfälle (4,8–5,0 %) nicht ab. Eine konfigurationsabhängige Standardisierung aus
  Phase 0 ist als Gültigkeitsregel zulässig; empfohlen wird die Fassung v2 aus PR #22 mit vier Korrekturen, als
  Alternative eine phasenkorrigierte Fünftel-Differenz, falls G4 an steilen Punkten Trends unter 1 % erkennen soll.
- **b) Vollständigkeit und Halte.** Zählt ein Halt als verlorene Kampagne, begrenzt die Haltrate die 0,8-Bedingung:
  In PR #23 halten 5 von 30 Nullkampagnen an; A8 lässt bis etwa 0,3 je Kampagne zu, ohne das sauber herzuleiten, das
  Teststatistikmodell der Nachprüfung ergibt 0,09–0,12. Empfohlen:
  Werkzeug 8 nimmt Halte wie der Messbetrieb wieder auf (synthetische Ursachenanalyse ohne Befund), berichtet die
  Haltrate je Regel getrennt und verwendet für c, b̂, Prüfrate und H2-Überdeckung eine gemeinsame Auswertungsmenge,
  für P(H1 und H2) alle simulierten Kampagnen als Nenner. Die Reserveformel bleibt; das Ziel 0,95 aus PR #22 wird
  Bedingung für r über die nicht endgültig beendeten Kampagnen. Halte häufen sich in Kampagnen mit kleinem geschätztem
  ε_ctrl (Dispersionsindex 2,0–2,5 je nach Zahl der Referenzläufe in Phase 0), und nach einem Nullpunkthalt verkettet
  sich der W-Satz über dasselbe R₀; beides
  gehört in die Festlegung von a) und in die Wahl von W.
- **c) E3.** Die Intervallregel von A9.13 ist am Schwellenrand ungültig: Bei E3b beträgt die Fehlalarmrate je
  Prüfung das 2- bis 16-Fache von α/m, bei E3a das bis zu 3-Fache (gerechnet); die Bonferroni-Schranke steigt im
  ungünstigsten Fall von 5 % auf etwa 16 %. Empfohlen: am Rand gültige Grenzen (Rice-Konstruktion mit
  t-Korrektur für E3b, t-Quantile für E3a), Prüfzahl m = 43 fest, Rückfall je Prüfgröße. Die Nachprüfung hat über
  ein volles Raster bestätigt, dass die E3b-Grenze am Rand höchstens α/m und „unauffällig“ höchstens 0,05 hält;
  die freie Rice-Grenze mit eingesetzter Streuung hält dagegen nicht. Bei der Präzision von L1 ist das Ziel von
  mindestens 80 % unauffälligen Kampagnen für E3b mit einer gültigen Regel nicht erreichbar; einzelne unauffällige
  Ergebnisse sind damit nicht ausgeschlossen. Das ist eine Folge der Präzision, nicht der Regel.
- **d) Generator.** Die Pilotkovarianzen lassen sich nicht unverändert in einen Generator einsetzen: Sie sind
  singulär (Rang ≤ Freiheitsgrade), enthalten den über die Zeiger erfassten Phasenanteil und tragen die
  Konfigurationsabhängigkeit der Harmonischen und der Fünftel nicht. Empfohlen: ein Strukturmodell, dessen
  Komponenten aus Phase 0 geschätzt und über die gemessenen Zeiger auf jede Konfiguration fortgepflanzt werden.
  Das ist der größte Posten (geschätzt 6–9 Personentage). Er zerfällt in d0 (Schätzer der Laufphasenstreuung im
  Pilotskript), d1 (Generatoroptionen einschließlich Phase-0-Anordnung) und d2 (vollständiges Strukturmodell mit
  Planungshaken ohne Szenario).
- **Reihenfolge (wie Abschnitt 6).** a und c zuerst und parallel, dazu d0 und d1; dann der Code für b1 und b2 und
  die Zähldiagnose R1. R1 braucht d0 und den neuen Ablauf, aber nicht das ganze d2; R2 braucht nur d1; d2 läuft
  parallel. Ablaufversion und Zählweise gehören zum Checkpoint-Schlüssel und zur Bezugsmenge jeder späteren
  Kalibrierung. Nach dem Auftrag vom 20.10.2026 werden die Etappen als ein Gesamt-PR umgesetzt; R1, R2 und R1-d
  bis R3-d laufen dabei nur als kleine Proben, ihre vollen Umfänge und die große Kalibrierung sind startfreie
  Beispiele (Abschnitt 9).

Die Fragen an den Autor stehen je Punkt und gesammelt in Abschnitt 6.

## 1 Ablaufregeln (a)

### 1.1 Ist-Stand

Text (gelesen):

- §9.2 S1 (Entwurf Z. 803–809): „folgt sofort ein Referenzlauf R₁ … führt zu R₂, der Wiederholung X′ und R₃“.
  R₂/X′/R₃ stehen ohne „sofort“.
- §9.2 S3 (Z. 812–816): „… überschreitet die Schwelle in der sofortigen Wiederholung erneut“.
- §6 (Z. 488–493) und A9.12 (Anhang Z. 1184–1187): ein ungültiger Kontrolllauf „wird sofort wiederholt, höchstens
  zweimal; danach wird angehalten“.
- §9.2 (Z. 801): „Die Messung wird sofort angehalten bei“ S1–S4; (Z. 828–830): „Ursachenanalyse, Eintrag im
  Abweichungsprotokoll, Wiederaufnahme nach einem vollständigen Kontrollsatz ohne Alarm; der unterbrochene Block
  wird in der gezogenen Reihenfolge fortgesetzt, gültige Läufe bleiben gültig.“
- A8 (Anhang Z. 746–748) setzt für die S1-Schranke voraus, dass X′ „mittig zwischen den frischen Referenzläufen R₂
  und R₃“ liegt; A1 (Z. 253) interpoliert zwischen den beiden einschließenden Referenzläufen.
- §6 (Z. 498): „Kein Block über Nacht.“

Der Text lässt offen: die Reihenfolge mehrerer sofortiger Folgeläufe; was beim Halt mit noch ausstehenden
Folgeläufen geschieht; wie eine beim Halt offene G1-Prüfung geschlossen wird; was im Kontrollsatz der Wiederaufnahme
als „Alarm“ gilt; ob nach einer Wiederaufnahme aufgewärmt wird.

Code `ablauf-3` (gelesen):

- An einem gewöhnlichen Kontrolllauf Lⱼ, der zugleich die Vorprüfung auslöst und S3 überschreitet, kommt die
  S3-Wiederholung vor R₁ (`_lauf` fügt R₁ ein, danach fügt `_s3` die Wiederholung davor ein). Löst die
  S3-Wiederholung selbst eine Vorprüfung aus, schließt deren R₁ die G1-Prüfung des Lⱼ. Für X′ gilt seit `ablauf-3`
  die Ausnahme: seine S3-Wiederholung folgt nach R₃.
- Bei ungültigem Lⱼ-X′ steht die Kontrollwiederholung vor R₃.
- Beim Halt bleiben Warteschlange und offene G1-Prüfungen stehen. `fortsetzen` stellt den Kontrollsatz der
  Wiederaufnahme (W-Satz) vor alle ausstehenden Einschübe; danach laufen R₁, R₃, S3- und Kontrollwiederholungen
  weiter. Offene G1-Prüfungen schließt der erste gültige Referenzlauf nach der Wiederaufnahme, über die
  Unterbrechung interpoliert; daraus folgende R₂/X′/R₃ kommen sofort, also in den W-Satz hinein.
- Im W-Satz hält jede einzelne S3-Überschreitung und jeder einzelne Nullpunktalarm an (strenge Lesart von „ohne
  Alarm“). Eingeschobene R₁/R₂/R₃ tragen kein W-Kennzeichen; X′ eines W-Laufs erbt es.
- Ein Halt an einem nach G2–G10 gültigen X′ entsteht nur auf diesem Weg: X′ eines W-Lⱼ mit einer einzelnen
  S3-Überschreitung. S2, S4 und ein ausgeschöpfter Kontrolllauf setzen ein ungültiges X′ voraus; dafür gilt schon
  §9.2 Z. 808 („gilt §6“), eine S1-Frage stellt sich dort nicht.
- Der W-Satz übernimmt Messtag und Vorlage des ersten geplanten Kontrollsatzes; nach einer Wiederaufnahme gibt es
  kein Aufwärmen, Nullpunktalarm und Vorprüfung vergleichen mit dem R₀ von vor dem Halt.
- Stufe 2 prüft offline die Klammer von X′ und seit `ablauf-3` die Folge X′ → R₃; eine Prüfung der R₁-Folge gibt
  es nicht. In `regeln.py` fehlen die Ablaufregeln vollständig; sie stehen nur im Modulkopf und im Bericht zu
  PR #23 (Abschnitt 6) und damit nicht in der Regelmatrix.

Wie oft es darauf ankommt (gerechnet, A8-Annahmen, Unabhängigkeit): Vorprüfung und S3 treffen an einem Kontrolllauf
in etwa 0,6–1,6 % der Kampagnen zusammen; der Fall, in dem die Reihenfolge den G1-Bezug tatsächlich ändert (die
S3-Wiederholung löst ihrerseits eine Vorprüfung aus), liegt bei 10⁻⁴ je Kampagne. In den 37 Ablaufkampagnen der
Korrekturrunde von PR #23 lässt sich ein Zusammentreffen aus den gespeicherten Zählern weder nachweisen noch
ausschließen (notwendige Bedingung R₁ > 0 und S3-Wiederholung > 0 erfüllen 14 von 37). Die Wirkung auf Raten ist
klein; der Punkt muss trotzdem vor jeder Kalibrierung stehen, weil die Ablaufversion zum Checkpoint-Schlüssel
gehört.

Nachprüfung mit geschätztem σ̂_ref (gerechnet, Teststatistikmodell, Plan von PR #23): Für den Mittelwert trägt die
Unabhängigkeit von Vorprüfung und S3. Die Vorprüfung ist je Lauf aber 17–26 % häufiger als bei bekanntem σ und
häuft sich in Kampagnen mit kleinem ε_ctrl. Ein Halt an einem nach G2–G10 gültigen X′ kommt mit dem heutigen Code in
etwa 0,6–1·10⁻⁴ der Kampagnen vor, 2,4- bis 3,2-mal so oft wie unter Unabhängigkeit; mit N7 entfällt er.

### 1.2 Optionen

Reihenfolge am Kontrolllauf:

- **A1 (empfohlen): Referenzfolge zuerst.** R₁ folgt unmittelbar auf den Lauf mit Verstoß in der Vorprüfung. Steht
  mit R₁ ein G1-Verstoß fest, folgen unmittelbar R₂, X′, R₃. Danach die übrigen sofortigen Wiederholungen, die
  zuletzt ausgelöste zuerst. Folgen: X, R₁, S3w bzw. X, R₁, R₂, X′, R₃, S3w(X); überschreitet X′ selbst S3:
  …, R₃, S3w(X′), S3w(X). Jede Klammer bleibt geschlossen, die Mittellage von X′ zwischen R₂ und R₃, die A8
  voraussetzt, bleibt erhalten, der Codeeingriff beschränkt sich
  auf `_s3` und die Einfügestelle der Kontrollwiederholung.
- **A2: S3-Wiederholung vor der G1-Folge** (X, R₁, S3w, R₂, X′, R₃). Braucht eine zusätzliche Regel, weil R₂ sonst
  die G1-Prüfung der S3-Wiederholung schließt und bei deren Verstoß R₂′/X″/R₃′ vor X′ setzt; das ist der Fehlertyp
  von vor `ablauf-3`.
- **A3: X′ übernimmt die S3-Wiederholung des Lⱼ.** Spart einen Lauf, vermischt aber zwei Prüfungen mit
  verschiedenen Bezügen. Nicht empfohlen.
- **Z1 (empfohlen, Ergänzung):** R₃ folgt ausnahmslos unmittelbar auf X′, auch wenn X′ aus anderem Grund ungültig
  ist; die Kontrollwiederholung eines ungültigen Lⱼ-X′ kommt nach R₃.

Halt und Wiederaufnahme:

- **H0: heutiges Verhalten festschreiben.** Ausstehende Folgeläufe überdauern den Halt und folgen nach dem W-Satz,
  R₂/X′/R₃ aus beim Halt offenen Prüfungen kommen in den W-Satz hinein. Widerspricht „Wiederaufnahme nach einem
  vollständigen Kontrollsatz“ und lässt ein Konfigurations-X′ mitten im W-Satz messen.
- **H1 (empfohlen): ausstehende sofortige Folgeläufe entfallen.** Bei der Wiederaufnahme entfallen alle noch nicht
  gemessenen sofortigen Folgeläufe (R₁, R₃, S3-, Kontroll- und Alarmwiederholungen, der Rest eines unterbrochenen
  W-Satzes) und werden protokolliert. Ein G1-Fall, dessen X′ beim Halt noch nicht gemessen ist (Halt an R₂ durch
  reproduzierten Nullpunktalarm), wird nach dem W-Satz vollständig gemessen (R₂ neu, X′, R₃), damit S1 prüfbar
  bleibt. Beim Halt offene G1-Prüfungen schließt der erste gültige Referenzlauf nach der Wiederaufnahme (A1, über
  die Unterbrechung interpoliert; offline schon so); daraus folgende R₂/X′/R₃ kommen nach dem W-Satz.
- **Unvollständige Klammer durch Halt** (Halt an X′ selbst oder an R₃): **K1 (empfohlen)**: wie bei ungültigem
  R₂/R₃: G1 von X′ gegen die einschließenden gültigen Referenzläufe, S1 „nicht prüfbar“, keine weitere
  Wiederholung, der Platz fehlt (Reserve r). Das ist die heutige Lesart, als Text. **K2**: X′ wird über die
  Unterbrechung geprüft; ist es G1-ungültig und nach G2–G10 gültig, folgt nach dem W-Satz einmalig eine frische
  Klammer R₂′, X″, R₃′ (auch über die Wiederholungsgrenze), S1 an X″. K2 hält S1 dort prüfbar, wo es greifen
  würde, kostet aber Mechanik für einen seltenen Fall: Ein Halt an R₃ kommt in 3–5·10⁻³ der Kampagnen vor
  (gerechnet in der Nachprüfung, Teststatistikmodell mit geschätztem σ̂_ref; die erste Fassung nannte hier
  pauschal 10⁻²). Unter K1 geht der Platz dann bedingt mit etwa 42 % verloren. Viermal häufiger ist der Halt an
  R₂ (1,1–1,7·10⁻² der Kampagnen), den H1 abdeckt: Der G1-Fall wird oft von einem abweichenden R₀ oder R₁
  ausgelöst, gegen den R₂ dann alarmiert. 36–52 % dieser Halte liegen in Kampagnen mit kleinem ε_ctrl
  (u = σ̂/σ < 0,85). **K3**: R₃ noch vor dem Halt messen. Widerspricht „sofort angehalten“ für S1–S4; nur beim
  Halt über die W-Regel textlich möglich. Nicht empfohlen.
- **S1 über den Halt hinweg prüfen:** nicht empfohlen. X′ läge dann fast auf R₂ (β → 0); die G1-Rate stiege von
  0,61 % (mittig) auf etwa 1,5 % (Randlage, gelesen A8), die S1-Schranke von 2,5·10⁻⁴ je Lauf wäre nicht mehr
  belegt (gerechnet 5,3·10⁻⁴). Alle diese Werte sind Mittel über die Streuung von σ̂_ref (nachgerechnet am
  Befehl in Tab. F, Anhang Z. 1437). In einer gegebenen Kampagne reicht die S1-Rate je Lauf von 2,5·10⁻³
  (u = 0,7) bis 6·10⁻⁷ (u = 1,2); bei bekanntem σ wären es 2,5·10⁻⁵.

Nachbarfragen, die in denselben Beschluss gehören:

- **N7, „ohne Alarm“ im W-Satz.** Empfohlen: Als Alarm gelten S1–S4 und der Nullpunktalarm (§6 Z. 506 nennt „die
  Alarme S1–S4“, §8.8 den Nullpunktalarm). Eine einzelne S3-Überschreitung ist nach §9.2 noch kein S3; im W-Satz
  folgt dann die S3-Wiederholung wie sonst, bei X′ nach R₃. Folge: Einen Halt an einem gültigen X′ gibt es nicht
  mehr; K1 bleibt für den Halt an R₃ nötig. Den Nullpunktalarm eines W-Mitglieds entscheidet der Autor: Halt (wie
  heute) oder Wiederholung nach §8.8.
- **N5:** Eingeschobene R₁/R₂/R₃ gehören nicht zum W-Satz (wie heute); ihr Alarm folgt §8.8.
- **N6, Aufwärmen und Messtag.** Heute fehlt nach einer Wiederaufnahme das Aufwärmen, der W-Satz vergleicht mit dem
  R₀ von vor dem Halt, und das Kopffeld „messtag“ bleibt der geplante Tag. Zur Wahl: (a) Aufwärmen nach §6 nach
  jeder Wiederaufnahme, der letzte Aufwärmlauf wird R₀ und schließt die offenen G1-Prüfungen; (b) Aufwärmen nur bei
  Tageswechsel, am selben Tag bleibt R₀ bestehen. „Kein Block über Nacht“ (§6 Z. 498) braucht in beiden Fällen die
  Ausnahme „außer nach einem Halt (§9.2)“, oder die Fortsetzung am Folgetag wird ausgeschlossen. Empfohlen: (b),
  mit tatsächlichem Messtag im Kopf und mit einer Ausnahme nach einem Nullpunkthalt (nächster Punkt); die
  Zeitkosten gehören zu b2.
- **Kette über dasselbe R₀ (Befund der Nachprüfung, gerechnet und vom Hauptbearbeiter nachgerechnet).** Nach S1
  über einen reproduzierten Nullpunktalarm ist meist R₀ selbst der Ausreißer. Der W-Satz vergleicht aber weiter mit
  diesem R₀ (`ablauf.py` Z. 398–414). Sein Referenzlauf alarmiert dann im selben Kanal mit etwa 0,19 bis 0,2 bei
  u = 1 und 0,27 bei u = 0,8. Hält jeder einzelne Nullpunktalarm im W-Satz an, entstehen 0,28–0,33 weitere Halte
  je Alarmhalt; 98 % aller Alarme im W-Satz folgen auf einen Alarmhalt. Wird der Alarm im W-Satz nach §8.8
  wiederholt, reproduziert er sich nur mit 0,057–0,107. N6 (b) erhält diese Kette, N6 (a) bricht sie. Empfohlen
  wird deshalb (b) mit einer Bezugseröffnung nach jedem Nullpunkthalt. Nullpunkthalt heißt: S1 über einen
  reproduzierten Nullpunktalarm; im W-Satz wird ein einzelner Nullpunktalarm nach §8.8 wiederholt, erst der
  reproduzierte hält an (F-a4, entschieden am 20.10.2026). Reihenfolge der Bezugseröffnung (Präzisierung vom
  20.10.2026):
  1. Nach dem protokollierten Ereignis „Ursachenanalyse ohne Befund“ wird vor den zufällig geordneten Läufen des
     W-Satzes ein gesonderter Referenzlauf gemessen, der Bezugslauf.
  2. Er wird nicht gegen das verworfene R₀ auf Nullpunktalarm geprüft; alle übrigen Gültigkeitsprüfungen bleiben
     wirksam. Ist er gültig, wird er R₀.
  3. Erst danach beginnt der vollständige W-Satz in seiner gezogenen Reihenfolge; der Bezugslauf zählt gesondert und
     ist kein Mitglied des W-Satzes.
  4. Bis ein gültiger neuer Bezug vorliegt, gibt es keine Vorprüfung und keinen Nullpunktalarm gegen den
     verworfenen Bezug, und die Wiederaufnahme gilt nicht als erfolgreich.
  5. Ein ungültiger Bezugslauf wird sofort wiederholt, höchstens zweimal wie ein ungültiger Kontrolllauf (§6);
     ist auch die zweite Wiederholung ungültig, folgt ein Halt „Bezugseröffnung gescheitert“, der eine weitere
     Wiederaufnahme verbraucht. Mit W ist die Zahl der Versuche begrenzt; eine Endlosschleife gibt es nicht.
  6. Altes und neues R₀ und ihre Differenz bleiben im Protokoll; eine reale Nullpunktänderung wird durch den
     neuen Bezug weder widerlegt noch aus dem Protokoll entfernt.
  Ohne diese Reihenfolge könnte ein zufällig zuerst gezogener L-Lauf des W-Satzes noch eine Vorprüfung gegen den
  verworfenen Bezug auslösen. Bei Tageswechsel kann der letzte gültige Aufwärmlauf den Bezugslauf ersetzen. Offene
  G1-Prüfungen von Läufen vor dem Halt schließt wie bisher die festgelegte Interpolation zwischen dem Referenzlauf,
  der bei ihrer Messung galt, und dem ersten gültigen Referenzlauf nach dem Halt; das kann der Bezugslauf sein.
  Für Läufe nach dem Halt ist der verworfene Bezug kein Stützpunkt mehr.

### 1.3 Empfehlung

A1 + Z1 + H1 + K1 + N7 (S1–S4; einzelner Nullpunktalarm im W-Satz nach §8.8) + N5 + N6 (b) mit Bezugseröffnung nach
einem Nullpunkthalt,
als Arbeitsfestlegung mit A0-Eintrag und als `ablauf-4`. Gründe: wörtlichste Lesart von §9.2 (Halt beendet die
Messung mit dem auslösenden Lauf, Wiederaufnahme nach einem vollständigen Kontrollsatz), die Mittellage von X′, die
A8 voraussetzt, bleibt erhalten, keine neue Verschachtelungslücke, der Code bleibt klein.
K2 ist die bessere Regel für S1, wenn der Autor den seltenen Fall „Halt an R₃“ nicht der Reserve überlassen will.

Mit demselben Beschluss sollten die übrigen Lesarten aus dem Modulkopf von `ablauf.py` Regeltext werden, damit vor
der Kalibrierung keine Lesarten bleiben: Schlusskontrollsatz bei geteiltem Satz; ein G1-Verstoß, der erst mit dem
ersten Referenzlauf des Schlusskontrollsatzes feststeht, gilt als spät erkannt; G1, S1 und Vorprüfung nur für
G2–G10-gültige Läufe; ein ungültiger Referenzlauf außerhalb eines Kontrollsatzes wird nicht wiederholt; technische
Grenze der Alarmkette; S4 zählt Läufe mit bewegten Modulen; W-Satz in gezogener Reihenfolge; keine Wiederaufnahme
nach mechanischem Eingriff (§12).

### 1.4 Änderungen

Normtext (Vorschläge, Wortlaut zur Entscheidung):

- §9.2 S1, Satz 1: „… folgt als nächster Lauf ein Referenzlauf R₁, vor jeder anderen Wiederholung (A9.12), und
  G1(X) wird mit R₀ und R₁ geprüft.“
- §9.2 S3: „… in der sofortigen Wiederholung erneut; sie folgt nach den Referenzläufen der G1-Prüfung desselben
  Laufs (A9.12).“
- §9.2 „Nach einem Abbruch“: „…; beim Halt noch ausstehende sofortige Folgeläufe entfallen (A9.12); der
  unterbrochene Block wird in der gezogenen Reihenfolge fortgesetzt, gültige Läufe bleiben gültig. Als Alarm im
  Kontrollsatz der Wiederaufnahme gelten S1–S4 und der nach §8.8 reproduzierte Nullpunktalarm.“ Der Entwurf nennt den Halt mit Wiederaufnahme „Abbruch“; diese Vorlage sagt dafür
  „Halt“ und meint mit „endgültig beendet“ nur das Ende nach zweitem S2, erschöpftem W oder Eingriff.
- A9.12, neuer Punkt „Reihenfolge sofortiger Folgeläufe“ (Definition der sofortigen Folgeläufe; (1) begonnene
  Referenzfolge wird nicht unterbrochen; (2) feststehender Verstoß → unmittelbar R₂, X′, R₃; (3) danach die übrigen
  Wiederholungen, die zuletzt ausgelöste zuerst; „sofort“ in §6, §8.8, §9.2 bedeutet diese Reihenfolge).
- A9.12 „G1 und S1“, Zusatz zur Klammer: R₂/R₃ desselben Falls, Alarmwiederholung ersetzt, X′ ohne Vorprüfung;
  unvollständige Klammer (R₂/R₃ ungültig, kein Referenzlauf danach, Halt an X′ oder R₃): G1 gegen die
  einschließenden gültigen Referenzläufe, S1 nicht prüfbar, keine weitere Wiederholung, Platz fehlt.
- A9.12, neuer Punkt „Halt und Wiederaufnahme“ (ausstehende Folgeläufe entfallen und werden protokolliert; G1-Fall
  ohne gemessenes X′ nach dem W-Satz vollständig; offene G1-Prüfungen schließt der erste gültige Referenzlauf nach
  der Wiederaufnahme; eingeschobene Referenzläufe gehören nicht zum W-Satz; Aufwärmen bei Tageswechsel; nach einem
  Nullpunkthalt eröffnet ein gesonderter Bezugslauf vor dem W-Satz den neuen Bezug, Reihenfolge und Grenzen wie in
  1.2; Messtag;
  „Kein Block über Nacht“ mit Ausnahme).
- A8 (Anhang Z. 740–757): S1-Weg über einen reproduzierten Nullpunktalarm am R₁ der Vorprüfung ergänzen; die Raten
  je Lauf als Mittel über die Streuung von σ̂_ref kennzeichnen, σ̂_ref mit effektiv etwa 21 Freiheitsgraden;
  Kampagnenschranke neu herleiten oder durch die simulierte Rate ersetzen (Abschnitt 3.1).
- P0.7 (Anhang Z. 886–887), Arbeitsfestlegung vom 20.10.2026: mindestens 42 Referenzläufe über Phase 0 verteilt,
  höchstens zwölf andere Läufe zwischen zwei Referenzläufen („nach zwölf“ als größter Abstand). Bei 120 anderen
  Läufen werden 42 Referenzläufe einschließlich Anfang und Ende möglichst gleichmäßig verteilt; die tatsächlich
  gültige Zahl und Anordnung wird ausgewiesen. Die alte Generatoranordnung bleibt als historischer Prüfmodus.
- §12 (I): neue Zeile „Ablauf der Phase 1 (A9.12)“ mit der Arbeitsfestlegung; A0-Eintrag.

Code und Tests:

- `ablauf.py` (`ablauf-4`): `_klammer_offen` → allgemeiner Vorrang (R₁ des eigenen Laufs oder R₃ des eigenen Falls an
  der Spitze), `_s3` und `_kontrolle_ungueltig` fügen dahinter ein; `fortsetzen` verwirft ausstehende Einschübe mit
  Protokoll, misst einen G1-Fall ohne X′ nach dem W-Satz vollständig und ordnet daraus folgende Einschübe hinter
  den W-Satz; N7-Fassung in `_s3`/`_referenz`; Bezugseröffnung nach einem Nullpunkthalt; Aufwärmen und Messtag bei
  Tageswechsel. Das Verwerfen gehört in
  `fortsetzen`, nicht in `_halt`, sonst ändern sich die Prüfsummen des Prüffalls S02 ohne fachlichen Grund.
- `auswertung.py`: Offline-Gegenprobe der Folgen (R₁ unmittelbar nach seinem Lauf; nach einem Halt beginnt der
  W-Satz; kein R₁/R₃ bezieht sich auf einen Lauf, an dem angehalten wurde), optional mit nachgerechneter
  Vorprüfung aus ⟨N⟩.
- `regeln.py`: Präfix `ablauf.` mit allen Ablaufregeln (Status Arbeitsfestlegung), Aufnahme in die Regelmatrix.
- Tests: Zusammentreffen Vorprüfung/S3 am gewöhnlichen Lⱼ (heute ungetestet), verschachtelte Vorprüfung der
  S3-Wiederholung, ungültiges Lⱼ-X′ (Z1), Halt an R₂ und an R₃, W-Satz mit S3-Überschreitung und mit
  Nullpunktalarm, Wiederaufnahme nach Nullpunkthalt mit Bezugslauf (kein Alarm gegen das alte R₀, keine Vorprüfung
  eines zufällig zuerst gezogenen L-Laufs gegen den verworfenen Bezug, ungültiger Bezugslauf), Fortsetzung aus
  dem Ablaufstand, Tageswechsel. Ablauf-Prüfsatz neu (Version); Software-Prüfsatz
  unverändert.
- Ergebnisse: Die Zahlen von PR #23 bleiben `ablauf-3`-Werte und werden so gekennzeichnet; eine Neurechnung ist
  nicht nötig und erst mit der Kalibrierung sinnvoll.

Aufwand (Einschätzung): 1–2 Personentage, keine Kampagnenrechnung.

### 1.5 Fragen an den Autor

- F-a1: Reihenfolge A1 (Referenzfolge zuerst, S3-Wiederholung danach) und Z1?
- F-a2: Halt: H1 (ausstehende Folgeläufe entfallen; G1-Fall ohne X′ wird nach dem W-Satz vollständig gemessen)?
- F-a3: Unvollständige Klammer durch Halt: K1 (S1 nicht prüfbar, Platz fehlt) oder K2 (einmalige frische Klammer)?
- F-a4: N7: gilt eine einzelne S3-Überschreitung im W-Satz als Alarm? Hält ein einzelner Nullpunktalarm im W-Satz
  an, oder wird er nach §8.8 wiederholt? (Halt verkettet mit 0,19–0,27, Wiederholung reproduziert nur mit
  0,057–0,107; gerechnet, siehe „Kette über dasselbe R₀“.)
- F-a5: Aufwärmen nach jeder Wiederaufnahme oder nur bei Tageswechsel; Ausnahme von „Kein Block über Nacht“; neuer
  Bezug R₀ nach einem Nullpunkthalt (Abschnitt 1.2)?
- F-a6: Sollen die übrigen Lesarten (Abschnitt 1.3, letzter Absatz) im selben PR Regeltext werden?

## 2 G4 (b, erster Teil)

### 2.1 Ist-Stand

- §9.1 G4 (Entwurf Z. 779–781): Schwelle 3·σ_Δ,X je Laufart, σ_Δ als 1,4826·MAD über alle Phase-0-Läufe der Art
  (Piloten gepoolt, P0.8 je Modul, P0.7). Tabelle F (Anhang Z. 1316) begründet mit „seltene Fehlausschlüsse“, ohne
  Zielrate. Die Reserve ist r = ⌈n_min·p̂/(1 − p̂)⌉ + 2 (Z. 402), p̂ geht auch in die Zeitformel ein (Z. 348–349).
- Code: `gueltigkeit.py` prüft D_N und D_F mit Faktor 3 je Gruppe R, L1–L3, K; seit PR #23 bei k_max des Plans.
  Die Standardisierung v2 aus PR #22 existiert nur im Diagnosecode, nicht in Teil B, `gueltigkeit` oder `regeln`.
- PR #22 (gelesen): G4 schließt 2,84 / 4,31 / 4,47 % der Läufe aus (A4 / V1-G0 / V1-G60h), unter v2 1,47 / 0,87 /
  0,85 %. Ursache ist der Jitter der Indexphasen mal der Flankensteigung von F_min − ⟨N⟩; nach A7 zulässige Piloten
  erreichen die steilen Punkte nicht.
- Gezählt aus `g4_konfigurationen.csv` (960 Läufe je Punkt): Rate je Konfiguration unter der heutigen Regel
  0,83–10,83 % (A4), 0,62–14,06 % (V1-G0), 0,42–14,69 % (V1-G60h); unter v2 0,73–3,12 / 0,42–2,29 / 0,42–2,29 %,
  ohne den Knickpunkt S120 höchstens 2,08 / 1,35 / 1,15 % und homogen (χ², p = 0,27–0,71). An S120 unterschätzt v2
  die Streuung um den Faktor 0,84–0,90 (von der Nachprüfung erneut gezählt). Ursache: s_i wird an der Sollphase und
  mit nominalen Modulamplituden ausgewertet, der Knick wandert aber von Lauf zu Lauf mit dem Indexversatz, dem nicht
  erfassten Phasenrest δ und der Amplitudenstreuung der Module. Die Nachprüfung hat D_F an S120 mit der
  Generatorstruktur und den Parametern der Stufe L1 nachgebildet (gerechnet, 200 000 Läufe):

  | MAD(D_F) an S120 [mN] | A4 | V1 |
  |---|---|---|
  | nur Sollphase | 1,64 | 2,06 |
  | Laufphase (Versatz und δ) | 2,12 | 2,64 |
  | alle Laufgrößen | 2,25 | 2,81 |
  | beobachtet (PR #22) | 2,29 | 2,88 / 2,87 |

  δ allein gibt den Faktor 1,15, die Laufphase 1,28, die Amplitudenstreuung allein ebenfalls 1,28, alle drei
  zusammen 1,36–1,39. Erst alle drei treffen die Beobachtung auf etwa 2 % und die G4-Rate unter v2 auf 0,1–0,25
  Prozentpunkte. An den übrigen 20 Punkten liegt beobachtet gegen nachgebildet bei 0,93–1,08.
- Am Knick hat D_F schwere Ränder (gerechnet in der Nachprüfung): Das 99,9-%-Quantil von |D_F| liegt beim
  3,8–3,9-Fachen der MAD statt beim 3,29-Fachen. Selbst mit exaktem σ ergibt die 3σ-Regel dort 0,75–0,77 % statt
  0,27 % Ausschlüsse.
- p̂ der Piloten (1,0–2,0 %) gegen den Anteil ungültiger Schnittläufe: heute 4,80–4,96 %, v2 1,35–2,12 %. Erst v2
  bildet mit p̂ die Phase 1 ab, wie Reserve und Zeitformel es voraussetzen (gezählt).
- Die 3σ-Regel mit MAD-Schätzer ist nicht nominal (gerechnet, Normalmodell): je Prüfgröße 0,65 % bei n = 60 und
  1,84 % bei n = 20 statt 0,27 %; mit D_N und D_F zusammen 1,31 % bzw. 3,65 %.
- Mit dem Wiederholungsablauf ist G4 für die Vollständigkeit nicht mehr maßgeblich (PR #23: jeder Punkt
  abgeschlossener Kampagnen hat mindestens 23 von 24 gültigen Läufen). G4 wirkt über die Messzeit (heute 5,2–5,4 %
  zusätzliche Schnittläufe, v2 1,4–2,2 %, gezählt) und über Halte an Kontrollläufen (Option F in 2.2, in 3.1 als
  Haltquelle geführt).
- Erster Ordnung ist die Fünftel-Differenz unkorreliert mit dem Laufmittel; G4 wählt also nicht nach der
  konfirmatorischen Größe aus, weder heute noch unter v2 (Einschätzung mit Herleitung).

### 2.2 Optionen

- **A: unverändert** (eine Schwelle je Laufart). Kein Code. Verfehlt die eigene Begründung, macht p̂ unbrauchbar und
  kostet rund 5 % Messzeit; eine größere Reserve wäre der falsche Hebel, weil die Wiederholungen die Punktausfälle
  schon decken.
- **B: Standardisierung v2** (PR #22): σ²_Δ,F,i = σ²_Δ,F + max(0, s_i² − s̄_P²), s_i aus ŷ⁰, Δδⱼ und σⱼ der Piloten,
  Untergrenze 3·σ_Δ,F.
- **B+ (empfohlen):** v2 mit vier Korrekturen (nach der Nachprüfung präzisiert):
  (1) s_i als Mischung über die Laufgrößen, s_i² = E_{τ,A}[2·Var_e F(φ_i + τ + e; A)], mit den Relativphasen
  τⱼ = offⱼ + δⱼ − δ₁ (j = 2, 3) und den Modulamplituden A. σ_off,j kommt aus den Laufmitteln φ̄ⱼ und σⱼ der
  gültigen Piloten (σ²_off,j = max(0, Var φ̄ⱼ − σⱼ²/N_z), ν ≈ 57). σ_δ,j und σ_a,j kommen aus der Quadratur- bzw.
  Gleichphasenkomponente der Lⱼ-Läufe (P0.8), kohärent über k und Zellen projiziert, ν = 19 je Modul. Der Boden
  kommt aus den R-Läufen. Derselbe Satz parametriert den Generator (Abschnitt 5). τ darf nicht einfach zu e addiert
  werden: Das zählte Var_τ E_e F mit, das sich in D_F aufhebt, und überschätzte die steilen Punkte stark. P0.5
  liefert nur das statische Δδⱼ und P0.6 nur Encodergrößen; beide geben keine Streuung von Lauf zu Lauf her (die
  erste Fassung nannte sie hier als Quelle).
  (2) An Punkten, deren vorhergesagter Knick innerhalb ±u(Δδⱼ) liegt, das Maximum von s über diesen Bereich.
  (3) Ziehungen auf Einheitskovarianz normiert oder Delta-Methode (die 512 festen Ziehungen von PR #22 verzerren s_i
  um den Faktor 0,94–1,04).
  (4) Die Zielrate wird am vorhergesagten Rand geprüft und die Schwelle dort über ein Quantil festgelegt statt über
  die Streuung, wegen der schweren Ränder am Knick.
  Dazu: Piloten behalten das gepoolte σ_Δ,F (p̂ unverändert definiert), aber s_p der Piloten wird mit derselben
  Mischung gebildet, weil P2 = (130°, 230°) nahe einem Knick liegt (A4: Sollphase 1,49, mit Mischung 1,78,
  beobachtet 1,71 mN MAD); sonst ist s̄_P² verzerrt. Fehlt s_i, ist G4 „nicht prüfbar“; eine registrierte Zielrate
  je Konfiguration in A9.11. Die Lⱼ-Schätzer sind im Generatormodell identifizierbar: Mit ν = 19 liegt σ̂_δ/σ_δ zu
  90 % zwischen 0,73 und 1,26, der Rauschboden trägt nur 0,4–1,6 % bei; an S120 ändert das MAD(D_F) um höchstens
  −4/+2,4 % (gerechnet in der Nachprüfung).
- **D: phasenkorrigierte Fünftel-Differenz.** Von D_F wird die aus den gemessenen Fünftelzeigern und ŷ⁰
  vorhergesagte Änderung abgezogen; eine Schwelle aus den ebenso korrigierten Piloten gilt für alle
  Konfigurationen. Misst den Jitter statt ihn zu modellieren und erhielte nach Gaußabschätzung die
  Trendempfindlichkeit an steilen Punkten (unter B+ wird ein Amplitudentrend von 0,5 % dort nur in 5–7 % der Läufe
  erkannt, gelesen PR #22). Braucht die Fünftelzeiger in der Laufzusammenfassung (Formatänderung) und 3–5
  Personentage.
- **F (Nebenpunkt, unabhängig): G4 an Einzelmodul-Kontrollläufen.** σ_Δ je Modul aus n₀ = 20 Läufen schließt nach
  dem an PR #22 kalibrierten Normalmodell 3,6 % [2,8; 4,4] je L-Lauf aus, also 3,0 [2,3; 3,7] Kontrollwiederholungen
  und 3,8 % [2,6; 5,2] G4-Halte je Kampagne bei V1 (gerechnet; A4 etwa die Hälfte). Beobachtet in PR #23: 55
  Kontrollwiederholungen nach G4 in 30 Kampagnen, 0 Halte (mit 30 Kampagnen nicht unterscheidbar). Pooling über die
  Module (n = 60) senkt das auf 1,0 Wiederholungen und 0,11 % Halte; ein Faktor k(n) statt 3 auf 0,4 und 0,2 %. Das
  ist eine Haltquelle für Abschnitt 3 und gehört in R1.

Zulässigkeit einer konfigurationsabhängigen Schwelle (Einschätzung): gegeben, wenn sie vollständig aus Phase-0-Größen
in Teil B festgelegt ist, keine Phase-1-Daten und nur Vorhersagegrößen (ŷ⁰, σⱼ) verwendet, erster Ordnung nicht nach
der Prüfgröße auswählt, eine registrierte Zielrate hat und vollständig spezifiziert ist (Konfigurationen, Piloten,
fehlendes s_i, Einstellung 2). Präzedenz sind G3 und G7, die ebenfalls aus Vorhersagegrößen gebildet werden.

### 2.3 Empfehlung

Die heutige Regel nicht einfrieren. B+ als Regeltext mit Zielrate je Konfiguration in A9.11 (Vorschlag ≤ 1,5 % je
Lauf, weil die 3σ-MAD-Regel mit 60 Piloten schon 1,3 % je Lauf erwartet; ≤ 1 % verlangt k(n) ≈ 3,4–3,6 statt 3). D
in dieselbe Rechenrunde aufnehmen; die Wahl zwischen B+ und D hängt an einer Frage des Autors: Muss G4 an steilen
Punkten Amplitudentrends unter 1 % erkennen? Wenn nein, B+; wenn ja, D, sofern R2 die Robustheit bestätigt. F mit R1
prüfen und mit b2 zusammen entscheiden. Die k_max-Klarstellung aus PR #22 (G1) in A9.2 nachziehen; der Code tut es
seit `pilot-0.3`.

### 2.4 Änderungen

- Normtext: §9.1 G4 (Zusatz für Kombinationsläufe, Wortlaut nach PR #22 Z. 610 mit den Korrekturen von B+); A9.2
  Reihenfolge der Schwellen (neuer Schritt s_i, k_max-Klarstellung); A9.3 Nr. 2 (s_i und σ_Δ,F,i in Teil B);
  Tabelle F (Zeile mit Zielrate); A9.11 (G4-Kriterium je Konfiguration, Trendempfindlichkeit als Berichtsgröße oder
  Kriterium); A0.
- Code: s_i-Funktionen aus `harness/diagnose_e3b_g4.py` in ein Produktivmodul; `pilot`/`teil_b` (s_i, Bindung an
  k_max und N_z); `gueltigkeit.Schwellen` je Konfiguration; `regeln.py` (g4.standardisierung, Zielrate);
  `auswertung._schwellen`. Für D zusätzlich Fünftelzeiger in `zusammenfassung`/`stufe1`/`generator`.
- Tests: s_i-Rundreise, Untergrenze, fehlendes s_i, Knickregel, Gleichheit mit dem Diagnosecode auf gespeicherten
  D_F, Offline-Gleichheit.
- Aufwand: B+ 1,5–2,5 Personentage, D 3–5 Personentage.

### 2.5 Rechnungen

- **R1 (vor der Entscheidung B+/D):** G4-Zähldiagnose mit Verfahren `zustand` für heutige Regel, B+ und D auf A4,
  V1-G0, V1-G60h, je 1000 Kampagnen und Variante, gepaarte Seeds, ohne Stufe 2; gemessen werden Rate je
  Konfiguration (Standardfehler etwa ±0,15 Prozentpunkte), Wiederholungen, fehlende Plätze, Halte nach Ursache
  (auch F), Messzeit, p̂ gegen die Phase-1-Ausfälle. Kosten etwa 6–9 Kernstunden (0,7 Kernstunden je 1000
  schlanke Kampagnen, mit den langsameren Laufzeiten der Korrekturrunde bis 1,0).
- **R2 (Robustheit, Kernfrage B+ gegen D):** farbiger Jitter, zwischen Modulen korrelierter Jitter, lastabhängiger
  Jitter, konfigurationsabhängiges Rauschen, größere Laufversätze, Phasendrift im Lauf. Dazu die drei Annahmen, die
  der Lⱼ-Schätzer selbst nicht trägt: größere Amplitudenstreuung je Modul, Streuung in Kombinationsläufen anders als
  in Einzelmodulläufen (wie N04, K = 2·L), und eine gemeinsame Laufzeitschwankung der Kette statt eines modulweisen
  δ (in Lⱼ nicht von δ trennbar, der Lⱼ-Wert ist für die Relativphase dann eine obere Schranke). Zusammen
  9 Szenarien × 3 Systeme × 300 statische Kampagnen, Auswertung aller Varianten auf denselben Läufen; 4,5–7,0
  Kernstunden (gerechnet aus 2,0–3,1 s je statischer Kampagne) plus Generatoroptionen (Teil d1 von d, nicht das
  Strukturmodell).
- **R3:** Trendempfindlichkeit je Variante für registrierte Trendklassen, nachträglich auf R1/R2-Daten; Minuten.

### 2.6 Fragen an den Autor

- F-b1: Muss G4 an steilen Punkten Amplitudentrends unter etwa 1 % erkennen (dann D), oder genügt die Erkennung an
  flachen Punkten (dann B+)?
- F-b2: Zielrate je Konfiguration als Kriterium in A9.11: ≤ 1,5 % je Lauf, oder ≤ 1 % mit Faktor k(n)?
- F-b3: Ist eine Formatänderung der Laufzusammenfassung (Fünftelzeiger) vor dem Einfrieren annehmbar
  (Voraussetzung für D)? Für B+ ist sie nicht nötig: φ̄ⱼ, σⱼ, Zeiger und Zellharmonische stehen schon in der
  Laufzusammenfassung (`zusammenfassung.py` Z. 45–47).
- F-b4: Piloten beim gepoolten σ_Δ,F belassen (p̂ unverändert) oder ebenfalls standardisieren?
- F-b5: G4 an Lⱼ: σ_Δ über die Module poolen, Faktor k(n), größeres n₀, oder erst R1 abwarten?
- F-b6: R1 und R2 vor der Neukalibrierung beauftragen? Zusammen etwa 13–19 Kernstunden plus Code: R1 mit Halten
  und zweiter Phase-0-Anordnung 8,6–11,8, R2 mit neun Szenarien 4,5–7,0 (Abschnitt 6).

## 3 Vollständigkeit und Halte (b, zweiter Teil)

### 3.1 Ist-Stand

- Text: „auswertbar“ ist punktweise definiert (§9.1 Z. 796–797); Planungsziel P(H1 und H2 bestätigt | exakt) ≥ 0,8
  (§5.4 Z. 382–386, A9.11); keine Bezugsmenge der Kampagnen genannt. Ein Halt führt zu Ursachenanalyse und
  Wiederaufnahme, „Ein Fehlalarm kostet eine Ursachenanalyse, keine Daten“ (Z. 825–826); Phase 1 endet nur nach
  einem zweiten S2 ohne Apparaturfehler oder nach einem Eingriff mit Differenz (Z. 830–836); bei vorzeitigem Ende
  gilt der Datenschluss nach dem letzten vollständigen Block (§6 Z. 510–512). Die Zeitformel (§5.3 c) kennt weder
  Halte noch Wiederholungen; sie ist nach §12 offen.
- Code: Eine angehaltene Kampagne wird in `datenlage` global gesperrt, alle Ausgänge sind „nicht entscheidbar“.
  Für c und die Prüfrate filtert `kalibrierung.py` nur auf „alle z endlich“; z wird für auswertbare Punkte trotz der
  Sperre berechnet. Spät angehaltene Kampagnen (PR #23: V1-G0 Nr. 2 mit 21/21 auswertbaren Punkten) gehen damit in
  c und die Prüfrate ein, zählen in P(H1 und H2) aber als nicht bestätigt. Das ist eine Inkonsistenz der
  Bezugsmengen, unabhängig von der gewählten Option.
- Bezugsmengen im Einzelnen (gelesen, Nachprüfung vom 19.10., vom Hauptbearbeiter am Code bestätigt): Heute gibt es
  vier, und keine filtert auf den Ablaufstatus. c und Prüfrate laufen über Kampagnen mit allen z endlich
  (`c_bestimmen`, Z. 63–79 und 199–206). b̂ (`rauschbias`, Z. 38–60) und der Restbias (`_restbias`, Z. 244–260)
  mitteln punktweise über alle endlichen Werte, also über mehr Kampagnen als c; `_restbias` weist n am Punkt mit
  den meisten Werten aus. Die H2-Überdeckung (`h2_ueberdeckung`, Z. 98–140) zählt Kampagnen mit vollständigem W
  und gültigem ŷ¹ und verwendet nur die erste Rauschvariante (Z. 189), c und b̂ dagegen alle. P(H1 und H2) hat
  alle Kampagnen im Nenner (`kampagnen.py` Z. 204, 221–222); dort steht zusätzlich eine zweite Rate „mindestens
  ein |z⁰| > c“ mit allen Kampagnen im Nenner (Z. 223–225), die nicht die Prüfrate ist.
- Wie viele Halte das heute betrifft (gezählt in den Checkpoint-Befunden der 30 Kampagnen von PR #23): Von den
  fünf angehaltenen Kampagnen hätte genau eine an allen Punkten endliche z⁰ (V1-G0 Nr. 2); die vier übrigen haben
  0/21 auswertbare Punkte und gehen in keine Schätzung ein, stehen aber im Nenner von P. Die Inkonsistenz betrifft
  also nur späte Halte.
- Text gegen Code bei b̂ (gelesen): §5.4 Z. 396–398 und A9.2 (iv) Z. 920–921 definieren b̂ „mit n_min Läufen“
  bzw. mit n + d Kontrollläufen, also über feste Laufzahlen. Der Code mittelt über die realisierten gültigen Läufe
  der Kampagnen (`auswertung.py` Z. 257–266); V1-G0 Nr. 2 hat mindestens 22 gültige Läufe je Punkt bei
  n_min = 18. Eine Festlegung der Bezugsmenge muss diese Abweichung mit auflösen.
- PR #23 (gezählt, 30 Nullkampagnen mit Ablauf, Entwicklungsplan n = 24, n_min = 18, 630 geplante Läufe): 5 halten
  an (S1 nach reproduziertem Nullpunktalarm 2, S1 nach G1-Verstoß von X′ 2, S3 1); dazu halten die Regelpfade S02
  (S2) und S06 (S3). Gemeinsam vollständig 25/30; jede abgeschlossene Kampagne ist vollständig. Wilson-Intervall
  für die Haltrate 5/30: [0,07; 0,34].
- Schranken aus A8 (gelesen und nachgerechnet): S1 je Kampagne bis 0,25–0,29 je nach Laufzahl, S3 reproduziert bis
  0,020–0,024; zusammen bis etwa 0,3. Das sind die Bonferroni-Summen von A8 bei exakter Superposition. Weil der
  S1-Weg über einen reproduzierten Alarm am R₁ fehlt (nächster Punkt), sind sie keine hergeleiteten oberen
  Schranken.
- Lücke in der Herleitung von A8 (Befund der Nachprüfung zu a; vom Hauptbearbeiter mit dem Skript der Nachprüfung
  und einer Variante bei bekanntem σ nachgerechnet, Summenkanal, 4·10⁶ Läufe): Ein reproduzierter Nullpunktalarm am
  R₁ der Vorprüfung führt zu S1, weil Alarm und Wiederholung gegen dasselbe R₀ prüfen, das schon die Vorprüfung
  ausgelöst hat. Diesen Weg enthält die Bonferroni-Summe von A8 nicht (Anhang Z. 747–757: „Die Vorprüfung … senkt
  die Rate nur“). Er ist der größte einzelne S1-Weg. Die Tabelle rechnet wie A8: Mittel über σ̂_ref ohne F-Test,
  ungünstige Interpolationslagen, ein eigenes R₀ je Lauf, nur Summenkanal. Es sind Bonferroni-Größen je Lauf,
  keine Raten des Verfahrens:

  | S1-Weg je Konfigurationslauf (Annahmen von A8) | marginal über σ̂_ref | σ bekannt |
  |---|---|---|
  | reproduzierter Alarm am R₁ | 2,9–3,0·10⁻⁴ | 5–6·10⁻⁵ |
  | über X′ | 0,9–2,0·10⁻⁴ | 0,5–1,5·10⁻⁵ |
  | reproduzierter Alarm an R₂ bzw. R₃ | 0,6–2,6·10⁻⁴ bzw. 1–2·10⁻⁵ | 0,6–4,4·10⁻⁵ bzw. < 2·10⁻⁶ |

  Mit diesem Weg ergäbe die Bonferroni-Summe für 646 Läufe etwa 0,47 statt 0,28. Das vollständige
  Teststatistikmodell der Nachprüfung zu ε_ctrl enthält den Weg, rechnet aber mit F-Test, wirklichen Lagen und
  gemeinsamem R₀ und kommt auf P(mindestens ein Halt) von 0,09 (Generator) bis 0,12 (42 R) je Kampagne. Auch ohne
  F-Test, wie A8 rechnet, liegt die mittlere Haltzahl dort bei 0,24, also P(mindestens ein Halt) ≤ 0,24. Die
  Kampagnenschranken 0,25–0,29 werden also eingehalten, sind aber nicht hergeleitet. Der Text von A8 ist im PR zu a
  zu berichtigen (Abschnitt 1.4).
- Halte nach ε_ctrl (gezählt aus den Befunden der 30 Kampagnen von PR #23): Die beiden S1-Halte über X′ liegen auf
  Rang 1 und 4 der 30 Kampagnen nach aufsteigendem ε_ctrl (V1-G0 Nr. 2 mit 0,222 mN und 13 X′, Nr. 7 mit
  0,265 mN). Die drei übrigen Halte liegen auf Rang 12, 13 und 17. Die Zahl der G1-Fälle und der X′ fällt mit
  ε_ctrl (Spearman −0,81 bzw. −0,65; die Nachprüfung hat Ränge und Werte unabhängig bestätigt). „G1-Fälle“ zählt
  dabei auch Referenzläufe mit Nullpunktalarm mit (`ablauf.py` Z. 407); nur mit Konfigurationsläufen sind es −0,75.
- Ursache und Größe (gerechnet in der Nachprüfung, Teststatistikmodell: ⟨N⟩ normal, ohne S3, G2–G10, Drift und
  Aufwärmen, ein Messtag, je Variante 20 000 Kampagnen): Die Korrelation ist die erwartete Folge des Schätzfehlers
  von σ̂_ref. Im Modell liegt Spearman(ε, G1) im Median bei −0,71, P(≤ −0,81) = 0,14; die Streuung von ε über die
  30 Kampagnen passt zum Modell (KS-Test p = 0,36). Die Schranke 2,5·10⁻⁴ je Lauf aus A8 ist ein Mittel über die
  Streuung von σ̂_ref; 72 % davon stammen aus den 9 % der Kampagnen mit u < 0,8. σ̂_ref aus 42 Referenzläufen hat
  wegen der korrelierten Leave-one-out-Werte effektiv ν ≈ 21, nicht 41 (vom Hauptbearbeiter analytisch und per
  Monte Carlo nachgerechnet). Die Halte je Kampagne sind deshalb überdispers:

  | Phase-0-Anordnung | Halte je Kampagne | Dispersionsindex | P(≥ 2) | P(≥ 4) | P(≥ 4) bei homogener Rate |
  |---|---|---|---|---|---|
  | σ bekannt | 0,037 | 1,5 | 0,005 | 0,0004 | – |
  | Generator (61 R), mit F-Test | 0,13 | 2,0–2,1 | 0,023 | 0,0034–0,0036 | 1,0·10⁻⁵ |
  | 42 R (Mindestzahl nach P0.7, Abstand 2), mit F-Test | 0,20 | 2,5 | 0,040 | 0,0076 | 5,2·10⁻⁵ |

  Gezählt sind S1-Halte und Halte im W-Satz, mit unbegrenzter Wiederaufnahme und der strengen Lesart des heutigen
  Codes. Die 30 Kampagnen von PR #23 sind damit verträglich: 4/30 S1-Halte haben im Modell P = 0,26–0,50, bei
  bekanntem σ nur 0,012. Der X′-Weg liegt am Rand (2 beobachtet, 0,35 erwartet, P = 0,05).
- Folgen, wenn ein Halt als verloren zählt (erste Fassung, gerechnet aus der homogenen Rate 5 Halte auf 18 215
  Versuche):
  P(kein Halt) ≈ 0,82–0,83 für 630–688 Läufe (Bereich 0,63–0,94), 0,74 für n = 30 bei N_K = 23 und N_I = 3. Dann
  gilt P(H1 und H2) ≤ P(kein Halt), und für 0,8 müsste P(bestätigt | ohne Halt) ≥ 0,96 sein. Die Grenze fällt mit
  der Laufzahl; Reserve und Laufzahl helfen nicht. Im Modell der Nachprüfung ist P(kein S1-Halt) für die
  Nullkampagne von PR #23 0,91 (Generator) bzw. 0,88 (42 R), dazu S3 reproduziert ≤ 0,024 (A8); beobachtet 25/30.
  Bei gleichem Mittel liegt P(kein Halt) wegen der Mischung über ε etwas über exp(−Mittel). Mit diesen Werten ist
  P(kein Halt) ≈ 0,86–0,89, und für 0,8 müsste P(bestätigt | ohne Halt) ≥ 0,90–0,93 sein statt ≥ 0,96.
- Reserve unter dem Wiederholungsablauf (gerechnet, Binomial, unabhängige Versuche): Ein Platz fehlt erst nach drei
  ungültigen Versuchen; selbst mit 30 % ungültigen Versuchen ist P(Punkt < n_min) ≈ 2,2·10⁻³ bei n = 21, r = 3, und
  gemeinsam über 21 unabhängige Punkte sind 0,955 der Kampagnen vollständig. Bei r = 2 wären es 1,6·10⁻² je Punkt
  und gemeinsam 0,71; bei höchstens 10 % ungültigen Versuchen ist die Vollständigkeit praktisch 1. Die Formel reicht
  gegen punktweise Ausfälle; über die gemeinsame Vollständigkeit entscheiden die Halte.
- Ziel 0,95 aus PR #22 (gelesen, `docs/e3b_g4_diagnose_2026-10-17/bericht.md` Z. 611 und 616): Der vorgeschlagene
  Zusatz zu A9.2 (v) lautet „r = ⌈n_min·p̂/(1 − p̂)⌉ + 2 gilt, wenn alle Punkte in mindestens 95 % der simulierten
  Kampagnen n_min gültige Läufe erreichen; sonst wird r erhöht, bis das erreicht ist.“ Dort ist 0,95 also eine
  Bedingung für r, keine Berichtsgröße; der Zahlenwert ist ausdrücklich offen. Der Kontext stützt die gemeinsame
  Lesart (in 95 % der Kampagnen alle Punkte), nicht die punktweise. PR #22 simulierte noch keine Halte. Teil A,
  Anhang und Code enthalten das Ziel nicht (`planung.py` Z. 103 bildet r nur aus der Formel).
- Simulierte Wiederaufnahme (gerechnet): Der W-Satz hätte zu etwa 4,7 % selbst einen Alarm (etwa 1 % je
  Referenzlauf, 3,7 % S3-Einzelüberschreitung je Satz). Den daraus abgeleiteten Kettenfaktor von etwa 1,05 hat die
  Nachprüfung widerlegt: Mit dem heutigen Code ist er 1,25–1,30, weil der W-Satz nach einem Nullpunkthalt mit
  demselben R₀ vergleicht (Abschnitt 1.2, „Kette über dasselbe R₀“). Mit neuem Bezug nach einem Nullpunkthalt fällt
  er nach Einschätzung der Nachprüfung auf etwa 1,02–1,05. Eine bedingte Zählung ohne S3-Halte verzerrt c im
  Nullmodell vernachlässigbar (3,4775 gegen 3,4783 in einer vereinfachten Rechnung). Unter (iii) fallen aber
  bevorzugt Kampagnen mit kleinem ε heraus; X′, G1 und R₁ würden um 6–16 % zu niedrig berichtet. Für c gilt das
  nur, solange der Generator das Rauschen von ⟨N⟩ und der Harmonischen getrennt zieht (`ebene_h.py` Z. 156–158);
  mit dem Strukturgenerator aus Abschnitt 5 ist es neu zu prüfen.
- Erschöpfung der Wiederaufnahmen (gerechnet in der Nachprüfung): Bei höchstens W = 3 Wiederaufnahmen wird eine
  Nullkampagne in 0,34–0,76 % der Fälle nicht fortgesetzt (strenge Lesart), bei W = 2 in 0,8–1,5 %, bei W = 1 in
  2,3–4,0 %. Die erste Fassung nahm mit homogener Rate 5–7·10⁻⁵ an. Kampagnen mit u < 0,85 stellen 18–39 % der
  erschöpften.
- G4-Halte an Einzelmodul-Kontrollläufen (Option F in 2.2, gerechnet mit dem an PR #22 kalibrierten Normalmodell):
  3,8 % [2,6; 5,2] je vollständiger Kampagne bei V1, etwa 1,5 % bei A4; in PR #23 0 von 30 (mit 30 Kampagnen nicht
  unterscheidbar). Sie fehlen in der Tabelle oben. Nach der Nachprüfung zu G4 an Lⱼ treten sie gehäuft in denselben
  Kampagnen auf wie die S1-Halte; R1 simuliert beide gemeinsam, statt sie zu addieren.
- Die Prüfschwelle 0,069 setzt 1000 verwertbare Kampagnen voraus (A8, Z. 734–738; nachgerechnet 0,0695); bei 833
  (Beispiel aus P(kein Halt) ≈ 0,83 der ersten Fassung) wären es 0,0714. Dasselbe gilt für die Überdeckungsschwelle
  0,936 (§8.6 Z. 643, „bei 1000 Kampagnen“), die bei
  833 Kampagnen 0,935 wäre. Beide Werte stehen fest im Profil (`regeln.py` Z. 114, 149) und hängen nicht vom
  tatsächlichen Nenner ab.

### 3.2 Optionen

- **(i) Halt = nicht vollständig** (heute). Konsequent wäre, auch c nur aus abgeschlossenen Kampagnen zu bilden.
  Begrenzt die 0,8-Bedingung durch die Haltrate; die Planung kann scheitern, ohne dass die Präzision der Grund ist.
- **(ii) simulierte Wiederaufnahme (empfohlen).** Werkzeug 8 setzt jeden fortsetzbaren Halt fort wie der
  Messbetrieb: protokolliertes synthetisches Ereignis „Ursachenanalyse ohne Befund, kein Eingriff, kein
  Apparaturfehler“, Kontrollsatz nach `ablauf-4`, Fortsetzung des Blocks; Parameter: höchstens W Wiederaufnahmen je
  Kampagne (Vorschlag 3), Analysezeit T_UA, Aufwärmen bei Tageswechsel. Als verloren zählt nur ein Abbruch (zweites
  S2, W erschöpft, mechanischer Eingriff nötig). Nur (ii) erzeugt dieselbe Menge von Kampagnen wie der reale
  Versuch. W = 3 bleibt nach der Nachprüfung vertretbar, aber nur zusammen mit dem neuen Bezug nach einem
  Nullpunkthalt; sonst ist die Kette über dasselbe R₀ der häufigste Weg zur Erschöpfung.
- **(iii) bedingte Zählung** nur über Kampagnen ohne Halt. Nachziehen bis zur Sollzahl; im Nullmodell nahe an (ii),
  in Szenarien mit echter Ursache verzerrt.
- **(iv) getrennte Zielgrößen:** P(H1 und H2 | ohne Halt) als Planungsbedingung, Haltrate je Regel als zweite
  Größe gegen die A8-Schranken, (1 − h)·P als Sensitivität.

### 3.3 Empfehlung

(ii) als maßgebliche Zählung in Planung, Kalibrierung, Prüfsimulation und Kriterien, ergänzt um die
Berichtsgrößen aus (iv): Anteil mit mindestens einem Halt je Regel neben der A8-Schranke für die tatsächliche
Laufzahl, Wiederaufnahmen (Mittel, Maximum), Anteil nicht fortgesetzt, zusätzliche Messzeit, P(H1 und H2 | ohne
Halt) und (1 − h)·P als Sensitivität. Für Szenarien mit echter Ursache (S04, E07, E09, I02) (ii) und (i)
nebeneinander berichten.

Bezugsmenge in zwei Stufen, gleich in Kalibrier-, Prüf- und Planungssimulation (nach der Nachprüfung geändert; die
erste Fassung nannte hier nur eine Menge und widersprach damit 3.4 und F-b7):

- Grundmenge G: alle simulierten Kampagnen der Rolle, mit Halten wie im Messbetrieb und über alle Rauschvarianten.
- Auswertungsmenge A ⊂ G: abgeschlossen nach Wiederaufnahme, ŷ¹ gültig, alle 147 z⁰ endlich (für H1Z alle 441).
  Über A laufen c, Prüfrate, b̂ mit u(b̂), Restbias und H2-Überdeckung.
- P(H1 und H2 bestätigt | exakt) hat den Zähler aus A und den Nenner G, also P = P(A)·P(H1 und H2 | A). Jede
  bestätigte Kampagne liegt ohnehin in A (`h1.py` Z. 64). Nur mit G im Nenner ist die Vollständigkeit in P
  enthalten.
- Die Ausschlüsse G \ A werden nach Grund gezählt: Abbruch (zweites S2, W erschöpft, Eingriff), ŷ¹ ungültig,
  Punkt < n_min, Konfiguration nach S2.
- Die Sollzahl 1000 gilt für |A| je Simulation: Kampagnen werden nachgezogen, bis |A| = 1000; dann gelten 0,069 und
  0,936 unverändert. Das Nachziehen wählt nicht nach c oder b̂ aus, weil Ablauf und Gültigkeit nur die Schwellen
  aus Teil B verwenden (`kette.py` Z. 193–203). Die Alternative ist, beide Schwellen aus |A| zu berechnen.
- „Alle z endlich“ statt nur „abgeschlossen“, weil H1 auch in unvollständigen, nicht gesperrten Kampagnen
  falsifizieren kann; ein c aus vollständigen Kampagnen ist für sie konservativ.

Reserveformel „+2“ beibehalten. Zum Ziel 0,95 (nach der Nachprüfung geändert): P ≥ 0,8 erzwingt die Vollständigkeit
nur bis 0,8, und r steht nicht in der Zielfunktion von §5.4; ohne eigene Bedingung passt nichts r an. Empfohlen wird
deshalb, 0,95 wie in PR #22 als Bedingung für r zu führen, in der gemeinsamen Lesart und mit dem Nenner „nicht
endgültig beendete Kampagnen“ (endgültig beendet heißt: zweites S2, W erschöpft oder Eingriff; ein Halt mit
Wiederaufnahme zählt nicht dazu): P(alle 21 Punkte ≥ n_min | nicht endgültig beendet) ≥ 0,95, direkt gezählt in der
Planungssimulation. Endgültig beendete Kampagnen gehören nicht in diesen Nenner, weil r sie nicht verringert; sonst
könnte die Regel
„r erhöhen, bis erreicht“ nie enden. Nach der Binomialrechnung in 3.1 greift die Bedingung nur bei extremen
punktweisen Ausfällen. Die Zeitformel erhält Terme für Wiederholungen (gemessen +5,4 %, höchstens +9,5 %) und
Wiederaufnahmen (W-Satz, T_UA, Aufwärmen).

Voraussetzungen: Abschnitt 1 ist festgelegt (die Wiederaufnahme muss `ablauf-4` simulieren, nicht `ablauf-3`), und
die Halt- und Wiederaufnahmeraten sind mit R1 (Abschnitt 3.5) gemessen, bevor Werkzeug 8 kalibriert wird.

### 3.4 Änderungen

- Normtext: §5.4 nach „(A9.11)“ (Bezugsmenge alle simulierten Kampagnen; Halte wie im Messbetrieb behandelt; nicht
  fortgesetzte oder abgebrochene Kampagne zählt als nicht bestätigt); §9.2 nach Z. 826 (Alarm im W-Satz → weitere
  Ursachenanalyse; Simulation rechnet Halte als Unterbrechung); A9.11 neuer Absatz „Halte in der Simulation“ (W,
  T_UA, Aufwärmen, Bezugsmenge, Berichtsgrößen); §5.3 (c) Zeitformel; §12 Zeile „Messzeit“ ergänzen; Tabelle F; A0.
  Dazu: §5.4 Z. 394–400 und A9.2 (iv) definieren b̂ „mit n_min Läufen“, der Code mit den realisierten Laufzahlen;
  entweder wird der Text auf die Menge A mit realisierten Laufzahlen umgestellt, oder der Code kürzt auf n_min.
  In §8.4 Z. 583–584 und §8.6 Z. 643 „1000 Kampagnen“ als „1000 gewertete Kampagnen (Menge A)“ präzisieren.
  A9.2 (v) erhält die Bedingung 0,95 für r. A8 (Z. 740–757): S1-Weg über einen reproduzierten Alarm am R₁ der
  Vorprüfung ergänzen; kennzeichnen, dass die Raten je Lauf Mittel über die Streuung von σ̂_ref sind und σ̂_ref
  effektiv etwa 21 Freiheitsgrade hat; Kampagnenschranke neu herleiten oder durch die simulierte Rate ersetzen.
- Code: Harness-Automatik der Wiederaufnahme in `kampagnen`, `planung`, `kalibrierung` und Prüfstand (synthetisches
  Ereignis, W, T_UA); Zähler je Regel; Bezugsmengen G und A in `kalibrierung` (Status und alle z endlich) und
  `kampagnen`, und zwar in `c_bestimmen`, `rauschbias`, `_restbias`, `_verh`, `h2_ueberdeckung` (alle
  Rauschvarianten statt nur der ersten) und in der zweiten Rate von `kampagnen.raten` (Z. 223–225); Zähler G \ A
  nach Grund; Nachziehen bis |A| = 1000; Statusvorrang „fehlt: Halt“ in `ablauf.bericht` nach erfolgreicher
  Wiederaufnahme korrigieren; Zeitformel und Bedingung 0,95 im Planungshaken. Die Befunde speichern je Kampagne
  σ̂_ref, σ̂_ref,c, F, den kritischen Wert und die Quelle von ε (heute nur ε_ctrl).
- Tests: Wiederaufnahme mit synthetischem Ereignis bis W, Abbruchfälle, Bezugsmenge, Zeitkosten, Berichtsgrößen.
- Aufwand: etwa 1–1,5 Personentage.

### 3.5 Rechnungen

- **R1-Halte:** Halt- und Wiederaufnahmeraten je Regel mit `ablauf-4`, gepaart für (i) und (ii) mit denselben
  Seeds, A4, V1-G0, V1-G60h je 1000 Kampagnen, Zähldiagnose ohne Stufe 2; dazu die Tabelle ε_ctrl × G1-Fälle ×
  Halte je Kampagne und die A8-Schranken für die tatsächliche Laufzahl. Die Tabelle für die 30 Kampagnen aus PR #23
  steht mit Skript im Belegpaket (`eps_ctrl/eps_ctrl_halte_je_kampagne.csv`); die Checkpoints selbst waren flüchtig
  und sind nicht aufgenommen (Stand 20.10.2026). R1 prüft die Teststatistikrechnung aus 3.1 als Gegenprobe: P(≥ 2), P(≥ 4),
  Kettenfaktor und Halt an R₂, R₃ und X′ nach ε-Klassen, einmal mit der Phase-0-Anordnung des Generators und einmal
  mit der von P0.7 (ein Referenzlauf nach zwölf Läufen). Mit denselben Seeds zählt R1 ohne Mehraufwand |A|,
  |G \ A| nach Grund, die H2-Teilmenge außerhalb von A und die gemeinsame Vollständigkeit über die nicht
  endgültig beendeten Kampagnen; die G4-Halte an Lⱼ laufen mit, damit sie zusammen mit den S1-Halten statt
  addiert bewertet werden. Etwa 4–6 Kernstunden, wenn (i) aus (ii) abgeleitet wird (mit denselben Seeds bis zum
  ersten Halt gleich) und die 6000 Kampagnen die zwei Anordnungen zu je 3000 sind; paarig simuliert 8,6–11,8.
  Monte-Carlo-Fehler der Haltrate etwa 0,012. Lässt sich mit R1 aus Abschnitt 2 in einem Lauf verbinden
  (Abschnitt 6).
- **R2-Halte:** ob (iii) unter Null eine gute Näherung von (ii) ist, und die Variante „Datenschluss nach §6“ für
  nicht fortsetzbare Kampagnen; mit fester Testvorgabe für c; nachträglich auf R1-Daten, Minuten.

### 3.6 Fragen an den Autor

- F-b7: Zählung (ii) als maßgeblich, mit der 0,8-Bedingung über alle simulierten Kampagnen (Nenner G) und den
  Schätzungen über die Auswertungsmenge A?
- F-b8: Parameter der Wiederaufnahme: höchstens W = 3 je Kampagne (nur zusammen mit dem neuen Bezug nach einem
  Nullpunkthalt, F-a5; sonst kleiner wählen oder neu rechnen), Analysezeit T_UA (Vorschlag: Teil-B-Wert, in der
  Entwicklung 1800 s), Aufwärmen bei Tageswechsel?
- F-b9: Nicht fortsetzbare Kampagne: Sperre aller Ausgänge (konservativ) oder Datenschluss nach §6 mit Auswertung?
  Gilt dasselbe für den realen Versuch?
- F-b10: Haltrate je Regel nur Berichtsgröße oder eigenes Kriterium (S1 und S3 reproduziert je höchstens ihre
  Schranke bei tatsächlicher Laufzahl, S3 0,020–0,024; die S1-Schranke erst nach der Neuherleitung von A8)?
- F-b11: Zeitformel um Wiederholungen und Wiederaufnahmen erweitern (§12 „Messzeit“)?
- F-b12: Ziel 0,95 als Bedingung für r mit dem Nenner „nicht endgültig beendete Kampagnen“, direkt gezählt in der
  Planungssimulation (empfohlen), oder nur als Berichtsgröße?
- F-b13: Sollzahl 1000 für die Auswertungsmenge A durch Nachziehen (empfohlen) oder Schwellen 0,069 und 0,936 aus
  |A| berechnen? b̂ über realisierte Laufzahlen (Text anpassen) oder auf n_min gekürzt (Code anpassen)?

## 4 E3 (c)

### 4.1 Ist-Stand

- Text: E3a |Δφⱼ^Z| mit Schwelle 0,1° an 21 Schnittpunkten für j = 2, 3 (42 Prüfungen); E3b q_Z am
  Triphasik-Punkt mit q_tol = 5,8·10⁻⁴ (eine Prüfung); dreiwertige Bewertung nach A9.13 (Z. 1221–1227): auffällig
  bei |x̂| − z_B·u > Schwelle (einseitiges Bonferroni-Normalquantil), unauffällig bei |x̂| + 1,645·u ≤ Schwelle für
  alle Prüfungen, sonst unbestimmt. Prüfzahl heute datenabhängig („zwei je auswertbarer Konfiguration und E3b“),
  Rückfall nach §8.10 und A9.11 für E3 als Ganzes oder je Prüfgröße offen (§12). E3 ändert keinen Ausgang und
  bestimmt die Laufzahl nicht.
- Code (`kontrollen.py`): u für E3b ist die Streuung von |d_b| über die Bootstrap-Replikate; keine 2×2-Kovarianz;
  m = 2·(Zahl der ausgewerteten Punkte) + 1; z-Quantile; ein Gesamturteil. Die Profilwerte `e3.pruefzahl`,
  `e3.pruefmenge`, `e3.rueckfall` und `e3.e3b_form` werden gelesen, aber nicht angewandt bzw. nirgends gelesen.
- Datenlage (gelesen, PR #21/#22, 570 Kampagnen, statischer Laufplan, historisch): N01-A4/L1 E3 unauffällig 14/200,
  sonst unbestimmt, allein wegen E3b; E3a 200/200 unauffällig.

Warum die Intervallregel am Rand versagt (gerechnet; reproduziert PR #22 exakt):

- Die Aussage „auffällig“ ist ein Test von H0: wahrer Wert ≤ Schwelle; ihre Fehlerrate muss am Rand gelten (wahrer
  Wert genau auf der Schwelle), nicht nur bei exakter Superposition, wie A9.11 es prüft.
- Rice-Geometrie: Für einen komplexen Schätzer gilt |D + ε| ≈ |D| + ε_∥ + ε_⊥²/(2|D|); Rauschen quer zum Residuum
  vergrößert den Betrag nur, der rechte Rand ist schwerer als normal.
- Die Bootstrap-Streuung des Betrags ist nicht die Streuung je Komponente; nahe null wird sie zu klein.
- u stammt aus etwa 20–24 Läufen, wird aber am Quantil 1 − α/m ≈ 99,88 % mit einem Normalquantil behandelt.
- Ergebnis je E3b-Prüfung am Rand, Vielfache von α/m = 0,116 %: mit bekanntem s 2,1 (t = q_tol/s = 1,5, Lage von
  L1) bis 11,5 (t → 0); mit Bootstrap-u aus ν = 21 Freiheitsgraden 6,3 bei t = 1,5, über alle t bis 15,8.
  Auch E3a ist betroffen: bei n_A = 22 und ohne bekannten Varianzanteil 3,1·α/m, die obere Grenze gibt 6,2 % statt
  5 %. Die Bonferroni-Schranke über 43 Prüfungen liegt im ungünstigsten Fall bei etwa 16 % (ν = 21) bzw. 7,8 % bei
  halb bekannter Varianz statt 5 %.
- Ein Nachweis der Randgültigkeit bei α/m ≈ 0,12 % ist mit 1000 Kampagnen nicht möglich (erwartet 1,2 Ereignisse);
  die Gültigkeit muss auf Ebene der Teststatistik gezeigt werden, die Kampagnen prüfen nur die Modellannahmen.

### 4.2 Optionen

- **A: E3b vorerst beschreibend**, E3a dreiwertig mit t-Quantilen, m = 43 fest, Rückfall je Prüfgröße. E3b berichtet
  q_Z, ŝ, Anisotropie und die Grenzen ohne Aussage. Nach dem Einfrieren wäre „beschreibend“ endgültig (A9.11
  Z. 1156–1158).
- **B (empfohlen): am Rand gültige Grenzen für E3b** (nach der Nachprüfung präzisiert). Replikate
  d_b = (R₋₁,b − R̂₋₁,b)/|R̂₊₁,b| komplex wie in `kontrollen.py` Z. 352, aber ohne Betrag; ungültige Replikate
  werden ausgelassen. n* = min(n_A, n₀,₁, n₀,₂, n₀,₃) gültige Läufe, Σ̂ = n*/(n* − 1)·Cov_b(Re d_b, Im d_b),
  ν = n* − 1, ŝ² = λ_max(Σ̂); bei B < 10 000 Replikaten ν_eff = (1/ν + 1/(B − 1))⁻¹ in κ und in t(0,95).
  Auffällig, wenn q_Z > κ·ŝ·Rice⁻¹(1 − α/m; q_tol/(κ·ŝ)) mit κ = t(1 − α/m; ν)/z(1 − α/m); unauffällig, wenn
  q_Z + t(0,95; ν)·ŝ ≤ q_tol; „nicht prüfbar“ zusätzlich bei ν < 5. Berichtet werden ŝ, ρ̂ = √(λ_min/λ_max), ν,
  n_A und n₀ⱼ.
  Größe am Rand (gerechnet in der Nachprüfung mit bedingt exakter Quadratur über das volle Raster ν ∈ {10, 19, 21,
  40, 80}, Anisotropie ρ ∈ {1; 0,5; 0,25; 0,1}, t ∈ [0,05; 10], Richtung in 15°-Schritten): „auffällig“ höchstens
  0,91·α/m, Grenzwert α/m für ρ → 0 und t → ∞, wo B zum einseitigen t-Test wird; vom Hauptbearbeiter an zwei
  Punkten unabhängig nachgerechnet (0,908 und 0,146·α/m). „Unauffällig“ höchstens 0,05; das folgt unter Gauß- und
  Wishart-Annahme aus einer Projektionsungleichung und ist damit bewiesen. Bei einem wahren Wert 2 % bzw. 10 % über
  q_tol höchstens 0,044 bzw. 0,027. Die erste Fassung nannte 0,96·α/m und 0,0505 aus einem Raster, das kein volles
  Produkt war und ν = 19 nicht enthielt; beide Werte waren Monte-Carlo-Rauschen.
  Gegenproben: Mit eingesetztem ŝ ohne n/(n − 1) und ohne κ hielte die Regel nur bis 3,1·α/m bei ν = 19 und
  6,4·α/m bei ν = 10; das ist die Regel „c-2“ des Querschnittsberichts, deren obere Rice-Grenze am Rand außerdem bis
  0,154 (ν = 19) bzw. 0,160 (ν = 10) statt 0,05 ergibt (Belegpaket, `e3b/zusatz_z1_z6.out`). Mit √(Spur/2) statt λ_max wären es bei geschätztem ŝ bis 20–27·α/m, mit κ, aber
  √(Spur/2), bis 11·α/m, bei bekanntem s bis 9,9·α/m. κ und λ_max sind also beide nötig; eine „Rice-exakte“ Grenze
  ist nur bei bekanntem s und isotropem Σ exakt.
  Annahmen: d̂ näherungsweise zweidimensional normal (Nenner nahezu fest); Läufe je Quelle unabhängig ohne Drift,
  Σ̂ ≈ Wishart mit mindestens ν Freiheitsgraden und unabhängig von d̂; Rauschbias klein gegen q_tol. Robustheit
  (gerechnet): zusammengesetzte Kovarianz mit ν = min − 1 höchstens 0,59·α/m; schwere Ränder der Einzelläufe
  0,07–0,63·α/m, „unauffällig“ ≤ 0,049; B = 1000 statt 10 000 erhöht die Größe relativ um etwa 2 %. Nicht geprüft:
  Drift und serielle Korrelation, Schiefe, Rauschen im Nenner.
- **C: Vertrauensscheibe** (Mahalanobis-Radius nach Hotelling √(2ν/(ν − 1)·F⁻¹(1 − α/m; 2, ν − 1)), etwa 4,61
  bei ν = 19); gültig, aber deutlich schwächer (Macht 0,12 statt 0,26 bei 0,3° auf L1, ν = 40).
- **D: kritische Werte je Richtung aus der vollen Σ̂**, numerisch je Kampagne; mächtiger, aufwendiger, später
  möglich.
- **E: Rückfall für E3 als Ganzes** (heutiges Profil ENTW „ganz“): nicht empfohlen, weil E3a auf L1 beide Kriterien
  erfüllt und dann mitfiele.

Macht von B (gerechnet, isotrop; ν = 19 ist der Wert der Regel bei n₀ = 20, PR-#21-Bericht Z. 51): bei 0,3° an
einem Modul auf L1 0,16 bei ν = 19 und 0,26 bei ν = 40 (heutige, ungültige Regel 0,56; Scheibe 0,12), bei 1 %
Amplitudenänderung 0,995 bzw. 0,999, bei t = 3 und 0,3° 0,955 bzw. 0,99. Phasenversätze erkennt E3a auf L1 ohnehin
sicher; E3b ergänzt vor allem Amplituden- und Kombinationsänderungen. „Unauffällig“ bei exakter Superposition: mit B
bei t = 1,5 praktisch 0 (heute 7 %), über 0,8 erst ab t ≈ 3,8 (ν = 19) bzw. 3,6 (ν = 40); die bestmögliche gültige
Regel (Neyman-Pearson, s bekannt) erreicht 0,8 ab t ≈ 3,2–3,4. Das Kriterium „unauffällig ≥ 0,8“ ist für E3b bei der
Präzision von L1 mit keiner gültigen Regel erreichbar; der Rückfall je Prüfgröße macht daraus eine einseitige
Auswertung, E3a bleibt dreiwertig.

Modellnachzählung der 570 Kampagnen (gerechnet, m = 43; ŝ aus der isotropen Umkehrung von u, weil Σ̂ nicht
gespeichert ist): H03 30/30 → 30/30; E07-basisdrift 36/40 → 31/40 mit ν = 19 (33/40 mit ν = 40); A06 3/30 → 0;
N01-A4/L4 (exakte Superposition) 2/40 → 0. „Unauffällig“ mit B: N01-A4/L1 0/200 (heute 14/200), N01-A4/L0 und
N03-N3bindet je 40/40, sonst 0. Das erzeugende Skript der ersten Nachzählung war überschrieben; die Nachprüfung hat
es rekonstruiert, und die Rekonstruktion reproduziert die gespeicherte Ausgabe bytegleich. E3a auf L4: Der eine
Fehlalarm bei exakter Superposition (1/40) entfällt mit dem t-Quantil, wenn u dieser Prüfung mindestens 0,08–0,10°
ist; bei der Prüfung mit dem größten |Δφ| ist u = 0,120°, dann entfällt er. u je Prüfung ist nicht gespeichert.

Anisotropie und ν lassen sich aus den gespeicherten Daten nicht direkt bestimmen: Es gibt keine Replikate, keine
2×2-Kovarianz und kein n_A oder n₀ⱼ je Kampagne. Indirekt (N01-A4/L1, 200 Nullkampagnen, synthetischer Generator,
gerechnet): Kurtosis von q 1,95 [1,76; 2,15], also ρ ≥ 0,67; ŝ im Mittel kalibriert (1,07 [0,93; 1,21]);
ν_eff ≈ 50 (42–63); der T-Anteil an u_q_Z liegt unter 10⁻⁴. Das stützt ν = 19 als konservativ und zeigt dort
keine starke Anisotropie; für reale Daten ist damit nichts gezeigt.

### 4.3 Empfehlung

Option B mit den Festlegungen: Prüfmenge 21 Schnittpunkte (E3a) und Triphasik-Punkt (E3b), ohne
Identifizierbarkeits- und Zusatzkonfigurationen; m = 43 fest, auch bei nicht auswertbaren Punkten, Rückfall einer
Prüfgröße oder N_K = 23; Bonferroni für die Gesamtaussage; E3a mit t-Quantilen (ν = n_A − 1, n/(n − 1) auf das
ganze u² einschließlich T, Δδ und Quantisierung, weil das einfach und konservativ ist; gerechnet: bei w = 0 genau
α/m, sonst weniger, obere Grenze ≤ 0,05). Ist 0,1°/u klein, kommt die Gegenseite hinzu (Faktor ≤ 1,03 für
0,1°/u ≥ 0,5, bis 2 für 0,1°/u → 0); dann gilt die gefaltete kritische Schranke. L1 ist davon nicht betroffen, L4
höchstens mit 1,02; „E3 unauffällig“ nur, wenn beide Prüfgrößen dreiwertig ausgewertet werden und alle Prüfungen
unauffällig sind, sonst E3a und E3b getrennt; „nicht prüfbar (Grund)“ bei nicht auswertbarem Triphasik-Punkt, bei
nicht endlicher oder singulärer Σ̂ oder bei ν < 5, m bleibt 43. A9.11 erhält ein Gültigkeitskriterium am Rand (auf
Statistikebene) und die Modellprüfung in den Kalibrierkampagnen: Kalibrierung von ŝ (E q²/(2·E ŝ²) in
Nullkampagnen), Isotropie über ρ̂, Prüfung von ν über die Streuung von ŝ² und PIT von q_Z. Verfehlt E3b die
Modellprüfung, ist es nur beschreibend (Rückfall je Prüfgröße). Wenn vor realen Daten kein neuer E3b-Code gewünscht
ist: Option A mit
denselben Festlegungen; B lässt sich vor dem Einfrieren nachziehen, ohne m zu ändern. Die Laufzahl hängt in keiner
Variante von E3 ab.

### 4.4 Änderungen

- Normtext: A9.13 (Grenzen für E3a und E3b, m = 43, Prüfmenge, Bonferroni, nicht prüfbar); §8.10 und A9.11 (Rückfall
  je Prüfgröße, Gültigkeit am Rand als Kriterium, Modellprüfung); §12 Zeile „Schwellen von E3“ (Option (a) mit
  Rückfall je Prüfgröße festgelegt); A0.
- Code: `kontrollen.py` (2×2-Kovarianz, κ, Rice-Grenze, t-Quantile, m fest, Urteil je Prüfgröße; je Kampagne Σ̂
  mit drei Zahlen, ρ̂, ν, n_A und n₀ⱼ in den Befund und in die CSV, sonst ist die Modellprüfung aus 4.3 nicht
  möglich), `auswertung.py` (Prüfmenge, Profilwerte wirklich binden), `regeln.py` (e3.* festlegen),
  Kriterienmatrix.
- Tests auf Statistikebene (Sekunden bis Minuten): Größe am Rand als bedingt exakte Quadratur statt Monte Carlo
  über ν, Anisotropie, t und Richtung, einschließlich Grenzfall ρ → 0, t → ∞, zusammengesetzter Kovarianz und
  endlichem B (ein Monte Carlo mit 2·10⁵ Fällen trennt 0,96 nicht von 1); Gleichheit zu PR #22 bei bekanntem s;
  E3a-Grenzen; Nachzählung der gespeicherten 570 Prüfgrößen als Regression mit der rekonstruierten Nachzählung.
- Aufwand: etwa 1 Personentag; keine zusätzlichen Kampagnen (die Modellprüfung läuft in den ohnehin geplanten
  Kalibrierkampagnen mit).

### 4.5 Fragen an den Autor

- F-c1: E3b jetzt mit gültiger Grenze (B) oder vorerst beschreibend (A), in beiden Fällen m = 43 fest?
- F-c2: Rückfall je Prüfgröße; „E3 unauffällig“ nur bei beiden dreiwertigen Prüfgrößen?
- F-c3: E3a auf t-Quantile mit ν = n_A − 1 umstellen (ändert den Wortlaut von A9.13 auch für E3a)?
- F-c4: Freiheitsgrade konservativ ν = min(n_A, n₀,₁, n₀,₂, n₀,₃) − 1 (empfohlen) oder Welch-Satterthwaite
  (mächtiger, mit geschätzten Gewichten aber bis 1,085·α/m, also leicht antikonservativ; gerechnet)?
- F-c5: Zusätzliches E3b-Szenario mit Amplitudenänderung 0,5 % und 1 % in A9.11, weil E3b dort über E3a hinaus
  etwas zeigt?

## 5 Generator aus Phase 0 (d)

### 5.1 Ist-Stand

- Text: Die Planung bildet s_q aus den gekürzten Pilotläufen und sucht (n_min, n₀) mit „Streuungen an ihrer oberen
  80-%-Vertrauensgrenze“ (§5.4 Z. 383–386; A9.2 Z. 914–926, Grenze s·√(ν/χ²₀,₂(ν)) nur für eine skalare Streuung
  definiert; „c als c_B“). Rauschbias, c, Intervalltyp von H2, E3-Raten und alle Kriterien von A9.11 stammen in
  Teil B aus der Simulation „mit den Pilotkovarianzen“, „mit getrennten Rauschmodellen für Einzelmodul- und
  Kombinationsläufe“ (Z. 394–401; Anhang Z. 1092–1095, 1107–1110). Nicht festgelegt sind Form und Dimension der
  Rauschkovarianzen, die Trennung von erfasstem Phasenanteil und Restrauschen, die Übertragung auf die
  Schnittpunkte, Drift und Fünftel, die 80-%-Grenze für mehrere Komponenten. Die Rauschmodellfrage ist offen (§12
  Z. 1026: Liste in Teil A oder Festlegung in Teil B; c als Quantil eines Modells oder Maximum über die Liste).
- Code: Der Planungshaken rechnet mit dem Rauschmodell des Katalogszenarios und skaliert es mit einem gemeinsamen
  Faktor κ(ν_p) = 1,091 bei ν = 57 (gerechnet). Die übergebenen Pilotkovarianzen werden nicht verwendet. Für Teil B
  gibt es kein Szenario; die Planung braucht ein aus Phase 0 gebautes Modell. Die Schnittstelle Pilotskript → Haken
  enthält schon Phase-0-Tabelle, Maske, Kalibrierung und Kovarianzen.
- Warum die Pilotkovarianz nicht direkt einsetzbar ist (gerechnet mit Szenarioparametern, Annahmen gekennzeichnet):
  (1) Dimension 3 + 6·k (57 bei k = 9, 75 bei k = 12) bei Freiheitsgraden 57 (Piloten), 41 (R), 19 (Lⱼ): die
  Kovarianzen von Lⱼ und R sind immer singulär, die Pilotkovarianz ab k = 10; ein Gauß-Generator zöge in
  Unterräumen. (2) Bei L0 entfallen rund 80 % der Lauf-zu-Lauf-Varianz der Harmonischen auf den über die gemessenen
  Zeiger ρ erfassten Phasenanteil, der im Residuum herausfällt; eingesetzt als Laufrauschen würde er die
  Residuenstreuung um bis zum Faktor 2,2–2,4 überschätzen (bei L1 1,03–1,21). Die Nachprüfung hat das mit den
  tatsächlichen Summenharmonischen von A4 bestätigt (1,297 / 0,427 / 0,184 N; bei A4 gleich den Zellharmonischen,
  weil die Zelle unter dem Modul die ganze Modulkraft trägt; für V1-G60h träfe die Gleichsetzung nicht zu). Das gilt
  für k = 1–3; für k = 4–9 liegt der Faktor bei L0 bei 1,03–1,69, bei L1 bis 1,38. Für F_min des Laufmittels ist er
  punktabhängig: bei L0 1,96–2,76 mit dem Maximum an S118, bei L1 1,05–1,27. Er ist im Wesentlichen ein Verhältnis
  von erfasster zu nicht erfasster Phasenstreuung und folgt in Teil B aus dem Laufgrößenmodell. (3)
  Konfigurationsabhängigkeit: Das
  Verhältnis der Varianz von Re bzw. Im N_k an einem Schnittpunkt zum gepoolten Pilotwert liegt bei
  modulproportionaler Streuung zwischen 0,52 und 1,65 (k = 2) und 0 und 1,63 (k = 3); am Triphasik-Punkt ist bei
  k = 3 alles gleichphasig. (4) Fünftel und F_min stehen in der Pilotkovarianz nicht; die Flankenabhängigkeit von
  G4 ist eine zweite Konfigurationsabhängigkeit. (5) Im Katalog hat kein Szenario eine Nullpunktdrift; σ̂_ref ist im
  Generator rein weiß, A9.11 verlangt „Rauschen, Jitter und Drift“.
- Zwei Textstellen widersprechen sich: A9.2 sagt für die Suche „c als c_B“, der Haken simuliert c (ohne Wirkung auf
  die Bedingung, weil die Bestätigung von c nicht abhängt); A9.11 nennt „dieselbe Simulation“ für n_min, b̂ und c,
  die Planungsbedingung verlangt aber die obere Grenze, b̂ und c skalieren mit dem Rauschpegel. Nach der Nachprüfung
  zu Reihenfolge und Budget ist A9.11 Z. 1093–1095 die einzige abweichende Stelle und zudem zirkulär: Dieselbe
  Simulation läuft „mit den geplanten n, n₀“ und soll n_min und n₀ erst liefern. §8.4 Z. 577–584 und A9.2 (iii)/(iv)
  sehen schon zwei Simulationen vor, die Planung mit c_B an der oberen Grenze und danach die Kalibrierung mit den
  Laufzahlen von Teil B.
- Zusicherung der Planungsregel (gerechnet, vereinfachtes unabhängiges Modell 7 × 42): Mit Punktschätzern liegt
  P(wahres P ≥ 0,8) bei 0,48–0,56, mit κ(ν) bei 0,81–0,88. Der Schätzfehler der Kovarianz wirkt auf c mit SD 0,010
  gegen den Monte-Carlo-Fehler 0,039 bei 1000 Kampagnen; eine Wishart-Fortpflanzung für c ist nicht nötig.
- §5.4 (Z. 373–374) verbietet dem Pilotskript die Ausgabe von Superpositionsresiduen der Piloten. Den ρ-Anteil
  herauszurechnen und die Pilotkovarianz aus den Lⱼ-Kovarianzen vorherzusagen braucht die Einzelmodul-Mittelkurven
  N̄⁽ʲ⁾ (zweite Momente, keine Residuen) zusammen mit den Pilotläufen; ob das zulässig ist, entscheidet der Text
  nicht. Der Lⱼ-Schätzer der Laufgrößen aus 5.2 braucht N̄⁽ʲ⁾ nur aus demselben Schritt P0.8 und ist davon nicht
  betroffen.

### 5.2 Optionen

- **A: Szenariofamilie mit aus Phase 0 geschätzten Parametern** (Amplituden- und Phasenstreuung je Modul und
  Laufart, weißes Rauschen je Zelle, Indexversatz, Zyklusjitter, T_φ, neu Nullpunktprozess und laufinterner Anteil)
  per Momentenschätzung. 2–3 Personentage. Geht als Sonderfall in C auf.
- **B: empirische Kovarianz je Laufart direkt (Gauß)** mit den gepoolten Pilotkovarianzen. Wörtliche Lesart, aber
  an den Schnittpunkten systematisch falsch (oben); nur als Diagnose- oder Sensitivitätsvariante. 1–2 Personentage.
- **C (empfohlen): Strukturmodell aus Phase 0.** Schätzung im Pilotskript (nur zweite Momente, gebunden an k und
  N_z): Sensorboden aus den R-Läufen (ν ≥ 41 für die Kovarianz der Harmonischen; σ̂_ref aus den
  Leave-one-out-Werten hat dagegen effektiv nur ν ≈ 21 bei 42 R) und σ_c; Laufgrößen je Modul (nach der
  Nachprüfung präzisiert): σ_a,j und σ_δ,j aus der kohärenten Projektion der Lⱼ-Abweichungen über k und Zellen auf
  skalare Laufwerte âⱼ,r und δ̂ⱼ,r (ν = n₀ⱼ − 1), σ_off,j aus den Laufmitteln φ̄ⱼ der Piloten, mit Parametern je
  Modul statt je Laufart (heute `rauschen.py` Z. 23–24); der orthogonale Rest je Harmonischer aus den Lⱼ-Läufen
  als eigene Komponente; erfasster Phasenanteil aus den Zeigern; Nullpunktprozess aus der Referenzfolge; Fünftel
  aus dem laufinternen Anteil. Fortpflanzung auf jede Konfiguration über die gemessenen
  Zeiger und ŷ⁰ (Struktur aus Phase 0 am Arbeitspunkt, aus Werkzeug 2 für Kandidatenfrequenzen). Obere 80-%-Grenze
  je Komponente mit eigenem ν nur für die Planungsbedingung; Teil-B-Werte (c, b̂, H2-Typ, E3-Raten) mit
  Punktschätzern aus der Kalibrierung nach der Planung, wie §8.4 und A9.2 es schon vorsehen. Für b̂ und c ist der
  Unterschied numerisch klein (höchstens 0,02–0,06 z-Einheiten, unter dem Monte-Carlo-Fehler von c; gerechnet in
  der Nachprüfung aus den gespeicherten Werkzeug-8-Werten); er zählt für die pegelabhängigen Raten (E3, Kriterien,
  H2-Überdeckung und -Typ, Halte). Das ε_ctrl-Quantil hat eine eigene Simulation nach A9.8, die nicht vom Pegel,
  wohl aber von der Phase-0-Anordnung abhängt. Für den weißen Boden von ⟨N⟩ gilt ein gemeinsamer Faktor für alle
  Laufarten: Werden R-Läufe mit κ(21) und K/L-Läufe mit κ(57) skaliert, schlägt der F-Test nach A9.8 künstlich in
  9,1 % statt 5,0 % der Fälle an (gerechnet in der Nachprüfung), und ε_ctrl, G1 und Halte verschieben sich.
  6–9 Personentage einschließlich A als Sonderfall.
- **D: Residuen-Bootstrap** der Lⱼ-Abweichungen als nichtparametrische Zusatzvariante (Mehrfachzählung des
  Sensorbodens beachten). 2–3 Personentage auf C.
- **E: prädiktive Planung** (Inverse-Wishart je Kampagne) statt oberer 80-%-Grenze; höchstens als berichtete
  Zusicherung, nicht als Regel.

### 5.3 Empfehlung

C mit A als eingebettetem Sonderfall (Modus, der den Szenariogenerator bitgleich reproduziert, als Prüfung). Als
Liste der Rauschmodelle nach §12 Fassung (b) {Strukturmodell aus Phase 0, Familienanpassung}, optional D; u(b̂) aus
der halben Spannweite darüber (so schon `kalibrierung.rauschbias`). Für c Fassung (a) (Quantil des
Strukturmodells) mit der Liste als Sensitivität, oder (b) (Maximum), wenn der Autor die Modellunsicherheit über die
Power stellt. Was Pilotdaten nicht hergeben (Drift zwischen Phase 0 und Phase 1 und zwischen Messtagen, farbiger
Jitter, lastabhängige Zusatzstreuung an Spitze und Flanken), wird nicht geschätzt, sondern als benannte
Sensitivitätsszenarien mit festen Stärken in Teil A geführt und in Teil B mitgerechnet und berichtet. Reihenfolge:
(1) Regeltexte (Komponentenzerlegung, κ je Komponente mit gemeinsamem Faktor für den ⟨N⟩-Boden, Punktschätzer
für Teil-B-Werte, Liste der Rauschmodelle,
Zulässigkeit von N̄⁽ʲ⁾), (2) Schätzer im Pilotskript und Modus A bitgleich zum Szenariogenerator, (3) Gauß-Modus,
Rundreise, (4) Planungshaken mit Pilotmodell und Modellquelle in den Kampagnen; das Szenario-Hakenpaar bleibt für
den Prüfstand als Orakel, (5) Rechnungen, (6) Abgleich mit b (s_i aus demselben Jitterpfad, Wiederholungen über
`zustand`) und c (E3-Kriterien mit dem Zellrauschen aus C).

### 5.4 Änderungen

- Normtext: §5.4 und A9.2 (Planungssimulation mit dem Phase-0-Modell; obere Grenze je Komponente; „c als c_B“
  streichen oder begründen); A9.3 (Komponenten in Teil B); A9.5 (Rauschmodell); A9.11 („dieselbe Simulation“
  präzisieren: Planungsbedingung an der oberen Grenze, Teil-B-Werte mit Punktschätzern; Sensitivitätsszenarien);
  §12 Zeile „Rauschmodelle, kritischer Wert und Laufzahl von H1“ festlegen; §5.4 Ausgabeverbot präzisieren; A0.
- Code: `pilot.py` (Komponentenschätzer, Format der Kovarianzen), neues Generatormodul (Ebene H aus Phase 0,
  Modi A/C/D), `harness/planung.py` (Haken ohne Szenario-ID, κ je Komponente mit gemeinsamem Faktor für den
  ⟨N⟩-Boden), `kampagnen`/`kalibrierung`
  (Modellquelle), `teil_b.py` (Felder), `regeln.py`.
- Tests: Rundreise Pilot → Generator → Pilot (Wiedergewinnung von s_q, σ_Δ, σ̂_ref, p̂, Komponenten); Modus A
  bitgleich zum Szenariogenerator; Gleichheit der Entscheidungen bei eingesetzter Szenariokovarianz; Singularität
  und Regularisierung; Wahrheitstrennung (kein Zugriff auf Szenario-Wahrheit im Pilotmodus); Verteilung von
  u = ε_ctrl/(3·√1,5·σ) und Anteil der Kampagnen mit ε aus σ̂_betr gegen die Nullsimulation; Rundreise
  Lⱼ → σ̂_δ, σ̂_a mit Kohärenzprüfung über k.
- Teil B: Felder σ_a,j, σ_δ,j und σ_off,j mit ν in A9.3 Nr. 2. Heute führt P0.8 keine Streuung als Ergebnis
  (Entwurf Z. 297), und das Pilotskript gibt nur Pilotgrößen aus (Z. 373–374). Der Lⱼ-Schätzer braucht nur N̄⁽ʲ⁾
  aus demselben Schritt und keine Superpositionsresiduen der Piloten; F-d3 betrifft nur die Verwendung zusammen mit
  den Pilotläufen (ρ-Anteil, Übertragungstest L → K).
- Phase-0-Anordnung: P0.7 verlangt mindestens 42 Referenzläufe, je einen nach zwölf anderen Läufen (Anhang
  Z. 886–887). Das ist mit den 120 anderen Phase-0-Läufen bei n₀ = 20 und 20 Piloten nicht erfüllbar; es bräuchte
  mindestens 492 (gerechnet). Der Generator verkürzt deshalb den Abstand auf zwei Läufe und kommt auf 61 R
  (`generator/kampagne.py` Z. 33–34 und 92, gelesen); Abstand 12 gäbe 11 R, Abstand 3 gäbe 41 R. Die Variante
  „42 R“ der Nachprüfung verwendet ebenfalls Abstand 2. Haltraten hängen nicht vom Rauschpegel ab, wohl aber von
  der Zahl der Referenzläufe: Mit 42 R sind es im Mittel 0,20 statt 0,13 Halte je Kampagne (gerechnet in der
  Nachprüfung). Die Lesart von P0.7 ist eine Regel der Gruppe (I) und gehört mit einer Anordnungsoption im
  Generator vor R1 (Abschnitt 1.4, PR 0), nicht erst in das Strukturmodell.
- Aufwand: 6–9 Personentage für C mit A, dazu 2–3 für D.

### 5.5 Rechnungen

- **R1-d:** Rundreise auf etwa 1000 synthetischen Phase-0-Sätzen je Szenario (N01-A4, N04-laufart, N03-ungleich,
  L0/L2/L4), ohne Stufe 2; 0,5–2,0 Kernstunden je nach Zahl der Sätze (Einschätzung der Nachprüfung; die erste
  Fassung nannte ≤ 0,5).
- **R2-d:** Gleichheit mit dem Szenariomodell auf Ebene der Entscheidungen (2 Szenariopunkte × 2 Generatoren × 400
  Kampagnen mit Stufe 2, B = 1000): 2,3–3,5 Kernstunden (gerechnet aus 5,1–7,9 s je Kampagne; die erste Fassung
  nannte 1,5–2).
- **R3-d:** Planung mit dem Pilotmodell gegen das Szenario-Orakel für K12-ähnliche Suche in Entwicklungsgröße;
  1,25–1,75 Kernstunden je Kandidat bei 2 × (200 + 200) Kampagnen und B = 1000 (gerechnet in der Nachprüfung).
- Die Rechnungen für Teil B selbst (Kalibrierung je System 18–81 Kernstunden, Planungssimulation je Kandidat ebenso;
  gelesen PR #23) sind davon getrennt und AP-21.

### 5.6 Fragen an den Autor

- F-d1: Lesart von „Streuungen an ihrer oberen 80-%-Vertrauensgrenze“ für ein mehrteiliges Modell: ein Faktor für
  alles (heute), jede Komponente mit eigenem ν (empfohlen, mit einem gemeinsamen Faktor für den ⟨N⟩-Boden aller
  Laufarten), oder ein Faktor mit dem kleinsten ν?
- F-d2: A9.11 Z. 1093–1095 an §8.4 und A9.2 angleichen (empfohlen): Planung an der oberen Grenze mit c_B,
  Teil-B-Werte und Kriterien mit Punktschätzern aus den Pilotkovarianzen? Oder alles an der oberen Grenze
  („dieselbe Simulation“)? Gegenüber dem Text kostet die Angleichung nichts, gegenüber dem heutigen Haken eine
  Einheit (1000 + 1000 Kampagnen, 18,4–81,1 Kernstunden für ein System); rechnet die Planung je Kandidat nur
  Prüfkampagnen mit c_B, gleicht sich das ab zwei Kandidaten aus.
- F-d3: Darf das Pilotskript die Einzelmodul-Mittelkurven N̄⁽ʲ⁾ zusammen mit den Pilotläufen verwenden
  (Herausrechnen des ρ-Anteils, Übertragungstest L → K), ohne gegen §5.4 zu verstoßen? Der Lⱼ-Schätzer allein ist
  davon nicht betroffen.
- F-d4: §12 Rauschmodelle: Fassung (b) mit der Liste {Strukturmodell, Familienanpassung, optional Bootstrap}; c nach
  (a) oder (b)?
- F-d5: Struktur in der Planung am Arbeitspunkt aus P0.8 oder aus Werkzeug 2 mit den Parametern aus P0.1–P0.5?
- F-d6: Nicht schätzbare Komponenten als benannte Sensitivitätsszenarien in Teil A, nur berichtet?
- F-d7: Soll Stufe 1 die Zeiger der Fünftel speichern? Nötig für Option D von G4; für B+ genügt σⱼ/√n_f. Farbiger
  Jitter bleibt nach 5.3 ein Sensitivitätsszenario.
- F-d8: Soll der Prüfstand künftig mit dem Pilotmodell planen und das Szenario nur als Orakel dienen?

## 6 Reihenfolge, Abhängigkeiten, Paketierung, Entscheidungsliste

Abhängigkeiten (nach der Nachprüfung zu Reihenfolge und Budget geschärft):

- d zerfällt in drei Teile. d0 ist der Schätzer der Laufphasenstreuung im Pilotskript (σ_a,j und σ_δ,j aus den
  Lⱼ-Läufen, σ_off,j aus den Piloten). d1 sind Generatoroptionen: farbiger, korrelierter und lastabhängiger Jitter,
  Laufversätze, Phasendrift, Nullpunktdrift, Parameter je Modul und die Phase-0-Anordnung. d2 ist das Strukturmodell
  mit Pilotschätzern und einem Planungshaken ohne Szenario.
- b2 (Halte) setzt a voraus: Die simulierte Wiederaufnahme muss `ablauf-4` abbilden; Ablaufversion und Zählweise
  gehören zum Checkpoint-Schlüssel und zur Bezugsmenge jeder Kalibrierung.
- R1 braucht a, den Code für b1 und b2, d0 und die Lesart von P0.7, aber nicht d2: Haltraten hängen nicht vom
  Rauschpegel ab. R2 braucht nur d1. b1 lässt sich als Regel ohne d2 festlegen; ihre Zahlen für Teil B hängen an d0
  und d2.
- c ist von a, b und d unabhängig (eigener Codepfad, keine Wirkung auf die Laufzahl); die Modellprüfung von E3 nutzt
  später das Zellrauschen aus d2.
- Vor die Neukalibrierung gehören d0 und d1. d2 braucht es für Teil B, oder wenn die Kalibrierung den Planungshaken
  mit dem Pilotmodell mitprüfen soll; die Gleichheit mit dem Szenariomodell deckt R2-d.
- Werkzeug 8 wird erst nach a, b1, b2, d0 und d1 neu kalibriert; c ist nur eine weiche Voraussetzung, weil
  E3-Varianten auf denselben Kampagnen ausgewertet werden können. Das weicht von §12 Z. 999–1001 („gestützt auf
  Werkzeug 8“) und von Plan Z. 652 ab (nach M4 die offenen Fassungen wählen, „H1-Kern einmal neu“). Begründung für
  A0: Regeln, die die Laufabfolge ändern (a, G4 über Gültigkeit und Wiederholungen, b2), brauchen je Variante eigene
  Kampagnen. Drei G4-Varianten mit voller Kalibrierung kosteten 165–730 Kernstunden, R1 dagegen 6,5–8,9 (gerechnet).
  R1 läuft im Harness von Werkzeug 8 mit angenommenen Rauschmodellen, nur ohne Stufe 2; b1 und b2 stützen sich damit
  im Sinn von §12 zum Teil schon auf Werkzeug 8.
- F-d2 fügt keine Simulation hinzu, sondern gleicht A9.11 an §8.4 und A9.2 an (Abschnitt 5.1).

Gemeinsame Reihenfolge (sie verträgt sich mit allen Reihenfolgen der Leseberichte, weil R2 nur d1 braucht):

1. PR 0 mit der Lesart von P0.7.
2. Parallel: a (PR 1), c (PR 2), d0 und d1 (PR 3a).
3. Code für b1 und b2 (PR 4 und 5), dann R1 mit dem Szenariogenerator in beiden Phase-0-Anordnungen.
4. R2, danach die Entscheidungen zu b1 und b2; parallel d2 mit R1-d bis R3-d (PR 3b).
5. Neukalibrierung von Werkzeug 8, danach Planungssimulation, Prüfstandsauswahl und E3-Punkte. Nach der
   Entscheidung vom 20.10.2026 nicht Teil dieses Vorhabensteils; nur als startfreies Beispiel vorbereitet.
6. Teil B (AP-21): Planung an der oberen Grenze, Teil-B-Werte und Kriterien mit den Pilotkovarianzen.

Vorgeschlagene Paketierung, je PR mit Normtext (§12-Zeile, A0, Regelstelle), `regeln.py`, Code, Tests,
Regelmatrix und Prüfsätzen:

| PR | Inhalt | Rechnung | Aufwand (Einschätzung) |
|---|---|---|---|
| 0 (Vorbereitung, kann in PR 1) | Präfix `ablauf.` in `regeln.py` und Regelmatrix; Profilwerte `e3.*` und `planung.zielfunktion` an den Code binden; „\|“ auch in der Gegenstandsspalte der Regelmatrix maskieren; Profilkennungen versionieren (AF-/ENTW-2026-11), damit gespeicherte Profile lesbar bleiben; Lesart von P0.7 | keine | 0,5–1 Personentag |
| 1 | a: `ablauf-4` mit neuem Bezug nach Nullpunkthalt, Offline-Gegenproben, Prüfsatz, Berichtigung von A8 | keine | 1–2 Personentage |
| 2 (parallel zu 1) | c: E3-Grenzen, m = 43, Rückfall je Prüfgröße, Kriterienmatrix | Statistikebene (Sekunden bis Minuten) | 1 Personentag |
| 3a (parallel zu 1) | d0 und d1: Laufphasenschätzer im Pilotskript, Generatoroptionen einschließlich Phase-0-Anordnung | kleine Rundreise, unter 1 Kernstunde (Einschätzung) | Teil der 6–9 Personentage von d |
| 4 | b1: G4 B+ (oder D), Zielrate | R1 gemeinsam mit PR 5; R2 4,5–7,0 Kernstunden; R3 Minuten | 1,5–5 Personentage |
| 5 | b2: Wiederaufnahme in Werkzeug 8, Bezugsmengen G und A, Berichtsgrößen, Zeitformel, Ziel 0,95 | R1 gemeinsam mit PR 4: 8,6–11,8 Kernstunden | 1–1,5 Personentage |
| 3b | d2: Strukturmodell, Pilotschätzer, Planungshaken | R1-d 0,5–2,0, R2-d 2,3–3,5, R3-d 1,25–1,75 je Kandidat; zusammen mindestens 3–6 Kernstunden | übriger Teil der 6–9 Personentage |
| nicht beauftragt, nur Beispiel | Neukalibrierung von Werkzeug 8, drei Systeme × (1000 + 1000) Kampagnen, normativ | 55–243 Kernstunden; mit den Laufzeiten der Korrekturrunde 78–243; oben 166, wenn je System die gemessene Laufzeit statt der von V1-G0 gilt; Nachziehen bis \|A\| = 1000 unter (ii) +0,2–2,5 | AP-13 |
| nicht beauftragt, nur Beispiel | Planungssimulation je Kandidat, Paar (k, T_a) und System | 18,4–81,1 Kernstunden je Einheit | AP-13 |
| nicht beauftragt | Prüfstandsauswahl, E3-Punkte | nicht beziffert | AP-13 |
| nicht enthalten | volle M4-Matrix (Katalog × L0–L5) | Plan 200–235 Kernstunden, Softwaredoku etwa 450 bei B = 1000 | eigener Auftrag |

Rechenbudget der Zähldiagnosen (gerechnet aus gelesenen 2,6–3,5 s je schlanker und 2,0–3,1 s je statischer
Kampagne, PR #23 und Softwaredoku):

| Rechnung | Kampagnen | Kernstunden |
|---|---|---|
| R1 gemeinsam: G4 heute, B+ und D × Halte unter (ii), (i) daraus abgeleitet | 9000 | 6,5–8,9 |
| dazu zweite Phase-0-Anordnung für eine G4-Variante | 3000 | 2,2–3,0 |
| R2 mit neun Szenarien | 8100 | 4,5–7,0 |
| zusammen | 20 100 | 13–19 |

Eine G4-Variante genügt für die zweite Anordnung: Die Haltzahl je Kampagne trennt sich gepoolt über drei Systeme mit
etwa 4,4 Standardfehlern (gerechnet in der Nachprüfung); voll faktoriell wären es 18 000 Kampagnen und 13,0–17,7
Kernstunden allein für R1. In R1 ist kein Nachziehen nötig, weil R1 |A| und G \ A bei |G| = 1000 zählt. Die
Obergrenze 243 Kernstunden der Neukalibrierung setzt die 139 s von V1-G0 für alle drei Systeme; die Messungen gelten
für n = 20, und ob es Kern- oder Wandsekunden sind, sagt die Softwaredoku an dieser Stelle nicht. Das Budget liegt
weit über den bisherigen Zusatzbudgets. Nach dem Auftrag vom 20.10.2026 werden die vollen Umfänge von R1, R2 und
R1-d bis R3-d nur als Auftragslisten mit Seeds und Checkpoints vorbereitet; innerhalb des Auftrags laufen kleine,
gepaarte Proben mit zusammen höchstens zwei Kernstunden neben der Testsuite. Solche Proben zeigen, dass ein
Verfahren durchläuft oder einen Fehler erkennt; sie belegen keine seltene Fehlalarmrate, keine Power von 0,8 und
keine Vollständigkeitsrate von 0,95.

Entscheidungsliste (Kurzform; Empfehlung in Klammern). Mit dem Auftrag vom 20.10.2026 sind alle Punkte für den
Umfang der Umsetzung als Arbeitsvorgaben entschieden; Abschnitt 9 nennt sie, einschließlich F-a4:

1. F-a1 Reihenfolge A1 + Z1 (ja). F-a2 Halt H1 (ja). F-a3 K1 oder K2 (K1). F-a4 N7-Fassung (S1–S4 als Alarm; ob
   ein einzelner Nullpunktalarm im W-Satz anhält oder nach §8.8 wiederholt wird: Autor, die Wiederholung verkettet
   weniger). F-a5 Aufwärmen bei Tageswechsel, neuer Bezug nach Nullpunkthalt (ja). F-a6 übrige Lesarten im selben
   PR (ja).
2. F-b1 B+ oder D (B+, wenn keine Trendempfindlichkeit an steilen Punkten verlangt ist). F-b2 Zielrate (≤ 1,5 %,
   am Knick über ein Quantil geprüft). F-b3 Fünftelzeiger im Format (ja, damit D in R1 mitgerechnet werden kann;
   für B+ nicht nötig). F-b4 Piloten gepoolt (ja, s_p mit derselben Mischung). F-b5 G4 an Lⱼ (R1 abwarten, Pooling
   bevorzugt). F-b6 R1 und R2 beauftragen (ja, 13–19 Kernstunden).
3. F-b7 Zählung (ii) mit Nenner G und Schätzungen über A (ja). F-b8 W = 3 nur mit neuem Bezug nach Nullpunkthalt,
   T_UA, Aufwärmen bei Tageswechsel. F-b9 nicht fortsetzbar: Sperre (ja). F-b10 Haltrate als Berichtsgröße (ja).
   F-b11 Zeitformel erweitern (ja). F-b12 Ziel 0,95 als Bedingung für r über die nicht endgültig beendeten
   Kampagnen (ja). F-b13 Nachziehen bis |A| = 1000 (ja); b̂ über realisierte Laufzahlen (Autor).
4. F-c1 E3b Option B (ja). F-c2 Rückfall je Prüfgröße (ja). F-c3 E3a mit t (ja). F-c4 ν konservativ (ja). F-c5
   Amplitudenszenario (ja).
5. F-d1 κ je Komponente mit gemeinsamem Faktor für den ⟨N⟩-Boden (ja). F-d2 A9.11 an §8.4 und A9.2 angleichen
   (ja). F-d3 N̄⁽ʲ⁾ zusammen mit den Pilotläufen (ja). F-d4 Liste (b), c nach (a) mit Sensitivität. F-d5 Struktur
   (P0.8 am Arbeitspunkt, Werkzeug 2 für Kandidaten). F-d6 Sensitivitätsszenarien (ja). F-d7 Fünftelzeiger (ja,
   wenn D gerechnet wird). F-d8 Prüfstand mit Pilotmodell, Szenario als Orakel (ja).
6. Paketierung und Abweichung von §12 Z. 999–1001 und Plan Z. 652 mit A0-Begründung (ja); Lesart von P0.7 (Autor).

## 7 Grenzen dieser Vorlage

- Alle Rechnungen sind Rechnungen auf Statistikebene mit vereinfachten Annahmen (Normalmodelle, Unabhängigkeit,
  Isotropie; die homogene Haltrate der ersten Fassung ist durch die Nachprüfung widerlegt); sie sind gekennzeichnet
  und ersetzen keine Kalibrierung. Skripte, kompakte Eingaben und Ausgaben liegen seit dem 20.10.2026 im
  Belegpaket `docs/entscheidungsvorlage_2026-10-19_belege/` (mit Herkunft, Seeds, Softwareständen und
  Ausführungsanweisung); die dort benannten Lücken (unter anderem das verlorene Originalskript der E3b-Nachzählung,
  die nicht aufgenommenen npz-Dateien und einzelne Gegenproben ohne gespeichertes Skript) bleiben bestehen.
- Die Zahlen aus PR #22 und #23 stammen aus Entwicklungsläufen (reduzierte Replikatzahlen, zehn bis vierzig
  Kampagnen je System) und aus Kampagnen mit statischem Laufplan oder `ablauf-2`/`ablauf-3`; sie zeigen Richtungen,
  keine Raten.
- Die Teststatistikrechnung der Nachprüfung zu ε_ctrl und Halten (3.1) bildet S3, G2–G10, Drift und Aufwärmen nicht
  ab und rechnet mit einem Messtag; die Rechnung zu Vorprüfung und S3 in 1.1 enthält S3, setzt aber Unabhängigkeit
  innerhalb einer Kampagne voraus. Die E3b-Rechnungen (Abschnitt 4) prüfen Drift, serielle Korrelation, Schiefe und
  Nennerrauschen nicht. Die Rechnungen zur
  Laufphasenstreuung gelten für die Generatorstruktur mit den Parametern der Stufe L1, nicht für eine Apparatur.
  Offen bleiben dort die Übertragung der Lⱼ-Streuung auf Kombinationsläufe, die Trennung einer gemeinsamen
  Laufzeitschwankung der Kette von modulweisem δ und die Registrierung der Laufgrößen in Teil B; R2 prüft diese
  Annahmen.
- Nicht behandelt: Punkt e) (realer Pilot), die Hardwareentscheidungen von §12 (II) und die Fassung der
  Zeitformel im Einzelnen.

## 8 Nachprüfung dieser Vorlage

Die erste Fassung beruht auf sechs Leseberichten und einer Kritik, die sieben Nachprüfaufträge formuliert hat. Am
Morgen des 19.10. sind fünf davon an Nutzungslimits abgebrochen; die erste Fassung hat sie behelfsweise durch eigenes
Nachlesen ersetzt. Am Abend wurden die abgebrochenen Prüfer mit ihrem gespeicherten Verlauf fortgesetzt, höchstens
zwei gleichzeitig. Alle Prüfer haben nur gelesen und auf Ebene der Teststatistik gerechnet; es wurde keine Kampagne
gerechnet und keine Regel geändert.

| Nr. | Gegenstand | Stand | Wichtigste Folge für diese Vorlage |
|---|---|---|---|
| 1 | Schätzfehler von ε_ctrl als Treiber von G1-, X′- und S1-Halten | am Abend fortgesetzt und abgeschlossen | Halte überdispers, Kette über dasselbe R₀, σ̂_ref mit ν ≈ 21; Abschnitte 1.2, 3.1, 3.2, 5 |
| 2 | G4 an Einzelmodul-Kontrollläufen | am Morgen abgeschlossen | Option F mit kalibriertem Normalmodell; Abschnitt 2.2 |
| 3 | Halt an X′, Falltabelle, Wiederaufnahme | am Morgen abgeschlossen | Messtag und Aufwärmen nach der Wiederaufnahme (1.1, N6); fehlender S1-Weg in A8 (jetzt 3.1) |
| 4 | Bezugsmengen für c, b̂, H2 und P; Ziel 0,95 | am Abend fortgesetzt und abgeschlossen | vier Bezugsmengen ohne Statusfilter, zweistufige Menge G/A, 0,95 als Bedingung für r; Abschnitt 3 |
| 5 | Konstruktion der E3b-Grenze, Nachzählung | am Abend fortgesetzt und abgeschlossen | Größe von B über ein volles Raster, Beweis für „unauffällig“, Nachzählung rekonstruiert; Abschnitt 4 |
| 6 | Herkunft der Laufphasenstreuung | am Abend fortgesetzt und abgeschlossen | Lⱼ-Läufe und Piloten statt P0.5/P0.6, Mischung für s_i, S120 erklärt; Abschnitte 2, 5 |
| 7 | Reihenfolge, Abhängigkeiten, Rechenbudget | am Abend fortgesetzt und abgeschlossen | d in d0, d1, d2 aufgeteilt, gemeinsame Reihenfolge, Kosten nachgerechnet und ergänzt, F-d2 als Angleichung von A9.11; Abschnitte 5 und 6 |

Nach den sieben Prüfern hat eine weitere unabhängige Prüfung die überarbeitete Vorlage auf innere Widersprüche
durchgesehen; ihre Befunde (unter anderem die Annahmen der A8-Wegetabelle in 3.1, der Geltungsbereich des neuen
Bezugs, die zwei Bedeutungen von „Abbruch“ und die G4-Halte an Lⱼ in 3.1) sind eingearbeitet.

Gegenproben des Hauptbearbeiters, unabhängig von den Prüfern gerechnet:

- effektive Freiheitsgrade von σ̂_ref aus 42 Referenzläufen: analytisch 20,6, Monte Carlo 19,8;
- A8-Schranke 2,5·10⁻⁴ je Lauf als Mittel über σ̂_ref (2,50·10⁻⁴), bei bekanntem σ 2,53·10⁻⁵;
- Kette über dasselbe R₀ bei u = 1: Reproduktion 0,058, Alarm des nächsten Referenzlaufs 0,20;
- S1-Weg über das R₁ der Vorprüfung: 2,9–3,0·10⁻⁴ je Lauf marginal, 5–6·10⁻⁵ bei bekanntem σ;
- Größe von Option B am Rand: 0,908·α/m bei ν = 10, ρ = 0,1, t = 10 und 0,146·α/m isotrop bei ν = 19, t = 1,5;
- Kostenrechnung aus den gelesenen Sekunden je Kampagne: R1 mit 9000 bzw. 12 000 Kampagnen 6,5–8,9 bzw.
  8,6–11,8 Kernstunden, R2 mit 8100 Kampagnen 4,5–7,0, Neukalibrierung mit den je System gemessenen Laufzeiten
  oben 166;
- Codeaussagen zu den Bezugsmengen, zu den Feldern der Laufzusammenfassung und zum Generator, die zitierten Stellen
  aus A9.11, §8.4, A9.2 und Plan Z. 652 sowie die Zählungen an S120 und in den Checkpoint-Befunden.

Gegenüber der ersten Fassung geänderte Empfehlungen:

- N6: Aufwärmen nur bei Tageswechsel, aber mit neuem Bezug R₀ nach einem Nullpunkthalt (Abschnitt 1.2).
- Bezugsmenge: Grundmenge G für den Nenner von P, Auswertungsmenge A für alle Schätzungen, Nachziehen bis
  |A| = 1000 (Abschnitt 3.3).
- Ziel 0,95: Bedingung für r über die nicht endgültig beendeten Kampagnen statt Berichtsgröße (Abschnitt 3.3, F-b12).
- B+: s_i als Mischung über die Laufgrößen aus Lⱼ-Läufen und Piloten, neue Korrektur (4) mit Quantil am Rand
  (Abschnitt 2.2).
- E3b: Definition mit n*, ν_eff bei endlichem B und „nicht prüfbar“ bei ν < 5 (Abschnitt 4.2).
- F-d2: keine zweite Simulation, sondern Angleichung von A9.11 an §8.4 und A9.2 (Abschnitte 5.1 und 5.6).
- Reihenfolge: R1 vor dem Strukturmodell; Lesart von P0.7 in PR 0; Budget für R1 und R2 13–19 statt 11–14
  Kernstunden (Abschnitt 6).

Unverändert geblieben sind die Grundrichtungen: A1 + Z1 + H1 + K1 + N7 für den Ablauf, B+ gegen D für G4, Zählung
(ii) für Halte, Option B für E3b und das Strukturmodell C für den Generator.

Die Skripte und Ergebnisse der Prüfer und der Gegenproben sind am 20.10.2026 in das Belegpaket
`docs/entscheidungsvorlage_2026-10-19_belege/` übernommen worden, darunter die Tabelle ε_ctrl je Kampagne, die
A8-Wege einschließlich des Alarms am R₁, die rekonstruierte E3b-Nachzählung mit Vergleichsausgabe (die Rekonstruktion
gibt die erhaltene Originalausgabe bytegleich wieder; das Originalskript ist verloren), die Randgültigkeit der
E3-Grenzen, die effektiven Freiheitsgrade von σ̂_ref und die Kostenrechnung. Die README des Pakets ordnet jede Zahl
Skript, Ausgabe und Herkunft zu und benennt die Lücken. Für das Paket wurden 46 kleine Rechnungen mit zusammen etwa
6,4 Kernminuten neu ausgeführt.

## 9 Auftrag vom 20.10.2026: Ressourcenentscheidung und Arbeitsvorgaben

**Ressourcenentscheidung des Autors.** Die normative Kalibrier- und Prüfsimulation mit 1000 + 1000 verwertbaren
Kampagnen je System, die volle M4-Matrix und große Planungssimulationen je Kandidat werden in diesem Vorhabensteil
nicht ausgeführt. Das ist eine feste Entscheidung, weil die Rechenressourcen fehlen und die vorhandenen Daten
synthetisch sind. Diese Rechnungen werden als startfreie Beispiele vorbereitet. Ihre Nichtausführung ist kein Fehler
der Umsetzung; die Kalibrierabnahme bleibt offen und wird weder durch niedrigere Sollzahlen noch durch gelockerte
Kriterien ersetzt. Für die Umsetzung gelten höchstens vier Prozesse mit je einem BLAS-Thread und neben der
Testsuite höchstens zwei Kernstunden für neue Diagnose- und Demonstrationsrechnungen.

**Arbeitsvorgaben.** Sie ersetzen die Auswahlfragen dieser Vorlage für den Umfang der Umsetzung. Weitergehende
Fachfragen, etwa δ_H2 und δ_H3, sind damit nicht mitentschieden. Alle Vorgaben sind methodische
Arbeitsfestlegungen; sie sind statistisch nicht kalibriert und experimentell nicht geprüft.

| Fragen | Arbeitsvorgabe |
|---|---|
| F-a1 bis F-a3 | A1 + Z1: R₁ zuerst, bei feststehendem Verstoß R₂, X′, R₃ als geschlossene Folge, auch bei ungültigem X′; H1 mit neuer vollständiger Folge für einen G1-Fall ohne gemessenes X′; K1 bei unvollständiger Klammer |
| F-a4 | Im Kontrollsatz der Wiederaufnahme gelten S1–S4 als Alarm; eine einzelne S3-Überschreitung und ein einzelner Nullpunktalarm werden wie sonst wiederholt, erst der reproduzierte Alarm hält an |
| F-a5 | Aufwärmen nur bei Tageswechsel; Bezugseröffnung nach einem Nullpunkthalt in der Reihenfolge von 1.2; Ausnahme für einen durch Halt unterbrochenen Block über Nacht im Normtext |
| F-a6, A8, P0.7 | übrige Lesarten im selben Regelstand; A8 um den S1-Weg über das R₁ ergänzen; P0.7 mit höchstens zwölf anderen Läufen zwischen zwei Referenzläufen, 42 Referenzläufe gleichmäßig verteilt, alte Anordnung als historischer Prüfmodus |
| F-b1 bis F-b5 | B+ als Standard, D als wählbarer Diagnose- und Entwicklungsmodus, bisherige Regel als historische Vergleichsvariante; Arbeitsziel höchstens 1,5 % Fehlausschlüsse je Konfiguration und Lauf unter dem benannten Nullmodell als Zielvorgabe; Fünftelzeiger im Format für D; s̄_P der Piloten mit derselben Mischung; für Lⱼ eine von n abhängige Schwelle, Pooling als Vergleich |
| F-b6 | R1 und R2 funktional implementiert, kleine Proben; volle Umfänge als Auftragslisten |
| F-b7 bis F-b13 | Zählung (ii) mit W = 3 und T_UA aus Teil B (Entwicklung 1800 s); Mengen G und A; endgültig beendete Kampagne sperrt ihre Ausgänge; Haltraten berichtet; Zeitformel erweitert; Ziel 0,95 als Bedingung für r über die nicht endgültig beendeten Kampagnen mit technischer Grenze; |A| = 1000 mit Nachziehen und Versuchslimit nur im Kalibrierbeispiel; b̂ über die realisierten Laufzahlen |
| F-c1 bis F-c5 | Option B mit beschreibendem Rückfall je Prüfgröße; m = 43 fest; E3a mit t-Quantilen und Berücksichtigung der Gegenseite; ν konservativ; Amplitudenänderungen 0,5 % und 1 % als kleine Zusatzprüffälle |
| F-d1 bis F-d8 | Strukturmodell als Standard, Familienanpassung eingebettet; κ je identifizierbarer Komponente mit gemeinsamem Faktor für den ⟨N⟩-Boden, marginale Grenzen ohne gemeinsame Garantie; Planung und nachgelagerte Parameterschätzung im Normtext getrennt; N̄⁽ʲ⁾ für Schätzung und Übertragungstest zulässig, keine Superpositionsresiduen der Piloten; c aus dem Standardmodell, Modellliste als Sensitivität; P0.8 am Arbeitspunkt, Werkzeug 2 für Kandidaten; nicht identifizierbare Komponenten als benannte Sensitivitäten; Planungshaken ohne Szenario, Szenariomodell als unabhängige Referenz; Residuen-Bootstrap optional |

Die Umsetzung erfolgt als ein Gesamt-PR mit den Etappen von Abschnitt 6 als Commits. Ergebnisse alter
Ablaufversionen bleiben historische Ergebnisse und werden nicht umetikettiert.
