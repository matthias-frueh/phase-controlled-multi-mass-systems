# Entscheidungsvorlage vom 19.10.2026: Ablaufregeln, G4 und Vollständigkeit, E3, Generator aus Phase 0

Stand `main` 0f63187 (PR #23 gemergt). Vorlage zu den Punkten a) bis d) der Agenda des Autors vom 18.10.2026; Punkt e)
(realer V1-Pilot) ist zurückgestellt und hier nicht behandelt. Dieses Dokument ändert keine Regel. Es nennt je Punkt
den Ist-Stand mit Fundstellen, die Optionen, eine Empfehlung, die zu ändernden Textstellen, den Aufwand und die
Fragen, die beim Autor liegen. Alle Festlegungen gehören nach §12 zu den Gruppen (I) und (II) und sind als
Arbeitsfestlegung mit Eintrag und Grund in A0 vorgesehen (Entwurf Z. 997–1004).

**Arbeitsweise und Kennzeichnung.** Grundlage sind der Präregistrierungsentwurf mit Anhang, der Code auf 0f63187, die
Berichte zu PR #21–#23 und deren gespeicherte Ergebnisdateien. Es wurde keine Kampagne gerechnet. Zahlen tragen eine
Herkunft: *gelesen* (steht so in Text, Code oder Ergebnisdatei), *gezählt* (aus gespeicherten Dateien ausgezählt),
*gerechnet* (eigene Rechnung auf Ebene einer Teststatistik, analytisch oder Monte Carlo, Sekunden bis Minuten; die
Skripte liegen noch außerhalb des Repositorys und werden mit dem jeweiligen Umsetzungs-PR als geprüfte Rechnungen
nachgereicht) oder *Einschätzung*. Rechnungen auf Statistikebene sind Modellrechnungen mit vereinfachten Annahmen; sie
begründen Entscheidungen über Regeln, ersetzen aber keine Kalibrierung.

**Ergebnis in Kürze.**

- **a) Ablauf.** Der Präregistrierungstext verlangt an drei Stellen „sofort“ (R₁, S3-Wiederholung,
  Kontrollwiederholung), ohne Reihenfolge. Empfohlen: eine Vorrangregel „begonnene Referenzfolge zuerst“
  (R₁; bei feststehendem Verstoß R₂, X′, R₃; dann die übrigen sofortigen Wiederholungen), beim Halt entfallen
  ausstehende sofortige Folgeläufe, und eine durch einen Halt unvollständige Klammer wird so behandelt wie eine
  durch ungültiges R₂/R₃ unvollständige (S1 nicht prüfbar, keine weitere Wiederholung). Zwei Nachbarfragen gehören
  in denselben Beschluss: was im Kontrollsatz der Wiederaufnahme als „Alarm“ gilt, und ob nach einer Wiederaufnahme
  aufgewärmt wird. Umsetzung ohne Kampagnenrechnung (`ablauf-4`).
- **b) G4.** Die heutige Schwelle je Laufart schließt an steilen Konfigurationen bis zu 14,7 % der Läufe aus
  (gezählt, PR #22), die Begründung „seltene Fehlausschlüsse“ (Tabelle F) trifft dort nicht zu, und p̂ der Piloten
  (1–2 %) bildet die Phase-1-Ausfälle (4,8–5,0 %) nicht ab. Eine konfigurationsabhängige Standardisierung aus
  Phase 0 ist als Gültigkeitsregel zulässig; empfohlen wird die Fassung v2 aus PR #22 mit drei Korrekturen, als
  Alternative eine phasenkorrigierte Fünftel-Differenz, falls G4 an steilen Punkten Trends unter 1 % erkennen soll.
- **b) Vollständigkeit und Halte.** Zählt ein Halt als verlorene Kampagne, begrenzt die Haltrate die 0,8-Bedingung:
  In PR #23 halten 5 von 30 Nullkampagnen an, die A8-Schranken lassen bis etwa 0,3 je Kampagne zu. Empfohlen:
  Werkzeug 8 nimmt Halte wie der Messbetrieb wieder auf (synthetische Ursachenanalyse ohne Befund), berichtet die
  Haltrate je Regel getrennt und verwendet eine Bezugsmenge für c, Prüfrate und P(H1 und H2). Die Reserveformel
  bleibt; ein eigenes Vollständigkeitsziel ist dann nicht nötig.
- **c) E3.** Die Intervallregel von A9.13 ist am Schwellenrand ungültig: Bei E3b beträgt die Fehlalarmrate je
  Prüfung das 2- bis 16-Fache von α/m, bei E3a das bis zu 3-Fache (gerechnet); die Bonferroni-Schranke steigt im
  ungünstigsten Fall von 5 % auf etwa 16 %. Empfohlen: am Rand gültige Grenzen (Rice-Konstruktion mit
  t-Korrektur für E3b, t-Quantile für E3a), Prüfzahl m = 43 fest, Rückfall je Prüfgröße. Bei der Präzision von L1
  kann E3b mit keiner gültigen Regel „unauffällig“ werden; das ist eine Folge der Präzision, nicht der Regel.
- **d) Generator.** Die Pilotkovarianzen lassen sich nicht unverändert in einen Generator einsetzen: Sie sind
  singulär (Rang ≤ Freiheitsgrade), enthalten den über die Zeiger erfassten Phasenanteil und tragen die
  Konfigurationsabhängigkeit der Harmonischen und der Fünftel nicht. Empfohlen: ein Strukturmodell, dessen
  Komponenten aus Phase 0 geschätzt und über die gemessenen Zeiger auf jede Konfiguration fortgepflanzt werden.
  Das ist der größte Posten (geschätzt 6–9 Personentage) und muss vor der Neukalibrierung von Werkzeug 8 stehen.
- **Reihenfolge.** a und c zuerst und parallel (kleine, voneinander unabhängige Codepfade), dann d, dann b1 (G4) und
  b2 (Halte) mit Zähldiagnosen, dann die Neukalibrierung. Jede Festlegung als eigener PR mit Normtext, `regeln.py`,
  Code, Tests, Regelmatrix und Prüfsätzen. Ohne Festlegung von a und b2 lässt sich nicht kalibrieren, weil
  Ablaufversion und Zählweise zum Checkpoint-Schlüssel und zur Bezugsmenge gehören.

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

### 1.2 Optionen

Reihenfolge am Kontrolllauf:

- **A1 (empfohlen): Referenzfolge zuerst.** R₁ folgt unmittelbar auf den Lauf mit Verstoß in der Vorprüfung. Steht
  mit R₁ ein G1-Verstoß fest, folgen unmittelbar R₂, X′, R₃. Danach die übrigen sofortigen Wiederholungen, die
  zuletzt ausgelöste zuerst. Folgen: X, R₁, S3w bzw. X, R₁, R₂, X′, R₃, S3w(X); überschreitet X′ selbst S3:
  …, R₃, S3w(X′), S3w(X). Jede Klammer bleibt geschlossen, A8 gilt unverändert, der Codeeingriff beschränkt sich
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
  würde, kostet aber Mechanik für einen Fall von etwa 10⁻² je Kampagne (Halt an R₃, gerechnet), in dem unter K1
  der Platz bedingt mit etwa 42 % verloren geht. **K3**: R₃ noch vor dem Halt messen. Widerspricht „sofort
  angehalten“ für S1–S4; nur beim Halt über die W-Regel textlich möglich. Nicht empfohlen.
- **S1 über den Halt hinweg prüfen:** nicht empfohlen. X′ läge dann fast auf R₂ (β → 0); die G1-Rate stiege von
  0,61 % (mittig) auf etwa 1,5 % (Randlage, gelesen A8), die S1-Schranke von 2,5·10⁻⁴ je Lauf wäre nicht mehr
  belegt (gerechnet 5,3·10⁻⁴).

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
  mit tatsächlichem Messtag im Kopf; die Zeitkosten gehören zu b2.

### 1.3 Empfehlung

A1 + Z1 + H1 + K1 + N7 (S1–S4 und Nullpunktalarm) + N5 + N6 (b), als Arbeitsfestlegung mit A0-Eintrag und als
`ablauf-4`. Gründe: wörtlichste Lesart von §9.2 (Halt beendet die Messung mit dem auslösenden Lauf, Wiederaufnahme
nach einem vollständigen Kontrollsatz), A8 bleibt gültig, keine neue Verschachtelungslücke, der Code bleibt klein.
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
- §9.2 „Nach einem Abbruch“: „…; beim Abbruch noch ausstehende sofortige Folgeläufe entfallen (A9.12); der
  unterbrochene Block wird in der gezogenen Reihenfolge fortgesetzt, gültige Läufe bleiben gültig. Als Alarm im
  Kontrollsatz der Wiederaufnahme gelten S1–S4 und der Nullpunktalarm.“
- A9.12, neuer Punkt „Reihenfolge sofortiger Folgeläufe“ (Definition der sofortigen Folgeläufe; (1) begonnene
  Referenzfolge wird nicht unterbrochen; (2) feststehender Verstoß → unmittelbar R₂, X′, R₃; (3) danach die übrigen
  Wiederholungen, die zuletzt ausgelöste zuerst; „sofort“ in §6, §8.8, §9.2 bedeutet diese Reihenfolge).
- A9.12 „G1 und S1“, Zusatz zur Klammer: R₂/R₃ desselben Falls, Alarmwiederholung ersetzt, X′ ohne Vorprüfung;
  unvollständige Klammer (R₂/R₃ ungültig, kein Referenzlauf danach, Halt an X′ oder R₃): G1 gegen die
  einschließenden gültigen Referenzläufe, S1 nicht prüfbar, keine weitere Wiederholung, Platz fehlt.
- A9.12, neuer Punkt „Halt und Wiederaufnahme“ (ausstehende Folgeläufe entfallen und werden protokolliert; G1-Fall
  ohne gemessenes X′ nach dem W-Satz vollständig; offene G1-Prüfungen schließt der erste gültige Referenzlauf nach
  der Wiederaufnahme; eingeschobene Referenzläufe gehören nicht zum W-Satz; Aufwärmen bei Tageswechsel; Messtag;
  „Kein Block über Nacht“ mit Ausnahme).
- §12 (I): neue Zeile „Ablauf der Phase 1 (A9.12)“ mit der Arbeitsfestlegung; A0-Eintrag.

Code und Tests:

- `ablauf.py` (`ablauf-4`): `_klammer_offen` → allgemeiner Vorrang (R₁ des eigenen Laufs oder R₃ des eigenen Falls an
  der Spitze), `_s3` und `_kontrolle_ungueltig` fügen dahinter ein; `fortsetzen` verwirft ausstehende Einschübe mit
  Protokoll, misst einen G1-Fall ohne X′ nach dem W-Satz vollständig und ordnet daraus folgende Einschübe hinter
  den W-Satz; N7-Fassung in `_s3`/`_referenz`; Aufwärmen und Messtag bei Tageswechsel. Das Verwerfen gehört in
  `fortsetzen`, nicht in `_halt`, sonst ändern sich die Prüfsummen des Prüffalls S02 ohne fachlichen Grund.
- `auswertung.py`: Offline-Gegenprobe der Folgen (R₁ unmittelbar nach seinem Lauf; nach einem Halt beginnt der
  W-Satz; kein R₁/R₃ bezieht sich auf einen Lauf, an dem angehalten wurde), optional mit nachgerechneter
  Vorprüfung aus ⟨N⟩.
- `regeln.py`: Präfix `ablauf.` mit allen Ablaufregeln (Status Arbeitsfestlegung), Aufnahme in die Regelmatrix.
- Tests: Zusammentreffen Vorprüfung/S3 am gewöhnlichen Lⱼ (heute ungetestet), verschachtelte Vorprüfung der
  S3-Wiederholung, ungültiges Lⱼ-X′ (Z1), Halt an R₂ und an R₃, W-Satz mit S3-Überschreitung und mit
  Nullpunktalarm, Fortsetzung aus dem Ablaufstand, Tageswechsel. Ablauf-Prüfsatz neu (Version); Software-Prüfsatz
  unverändert.
- Ergebnisse: Die Zahlen von PR #23 bleiben `ablauf-3`-Werte und werden so gekennzeichnet; eine Neurechnung ist
  nicht nötig und erst mit der Kalibrierung sinnvoll.

Aufwand (Einschätzung): 1–2 Personentage, keine Kampagnenrechnung.

### 1.5 Fragen an den Autor

- F-a1: Reihenfolge A1 (Referenzfolge zuerst, S3-Wiederholung danach) und Z1?
- F-a2: Halt: H1 (ausstehende Folgeläufe entfallen; G1-Fall ohne X′ wird nach dem W-Satz vollständig gemessen)?
- F-a3: Unvollständige Klammer durch Halt: K1 (S1 nicht prüfbar, Platz fehlt) oder K2 (einmalige frische Klammer)?
- F-a4: N7: gilt eine einzelne S3-Überschreitung im W-Satz als Alarm? Hält ein einzelner Nullpunktalarm im W-Satz
  an, oder wird er nach §8.8 wiederholt?
- F-a5: Aufwärmen nach jeder Wiederaufnahme oder nur bei Tageswechsel; Ausnahme von „Kein Block über Nacht“?
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
  die Streuung um den Faktor 0,84–0,90, weil die Jitterstreuung an der Sollphase ausgewertet wird und die Läufe in
  der Laufphase streuen.
- p̂ der Piloten (1,0–2,0 %) gegen den Anteil ungültiger Schnittläufe: heute 4,80–4,96 %, v2 1,35–2,12 %. Erst v2
  bildet mit p̂ die Phase 1 ab, wie Reserve und Zeitformel es voraussetzen (gezählt).
- Die 3σ-Regel mit MAD-Schätzer ist nicht nominal (gerechnet, Normalmodell): je Prüfgröße 0,65 % bei n = 60 und
  1,84 % bei n = 20 statt 0,27 %; mit D_N und D_F zusammen 1,31 % bzw. 3,65 %.
- Mit dem Wiederholungsablauf ist G4 für die Vollständigkeit nicht mehr maßgeblich (PR #23: jeder Punkt
  abgeschlossener Kampagnen hat mindestens 23 von 24 gültigen Läufen). G4 wirkt über die Messzeit (heute 5,2–5,4 %
  zusätzliche Schnittläufe, v2 1,4–2,2 %, gezählt) und über Halte an Kontrollläufen (Abschnitt 3).
- Erster Ordnung ist die Fünftel-Differenz unkorreliert mit dem Laufmittel; G4 wählt also nicht nach der
  konfirmatorischen Größe aus, weder heute noch unter v2 (Einschätzung mit Herleitung).

### 2.2 Optionen

- **A: unverändert** (eine Schwelle je Laufart). Kein Code. Verfehlt die eigene Begründung, macht p̂ unbrauchbar und
  kostet rund 5 % Messzeit; eine größere Reserve wäre der falsche Hebel, weil die Wiederholungen die Punktausfälle
  schon decken.
- **B: Standardisierung v2** (PR #22): σ²_Δ,F,i = σ²_Δ,F + max(0, s_i² − s̄_P²), s_i aus ŷ⁰, Δδⱼ und σⱼ der Piloten,
  Untergrenze 3·σ_Δ,F.
- **B+ (empfohlen):** v2 mit drei Korrekturen: (1) s_i einschließlich der Streuung der Laufphase von Lauf zu Lauf,
  geschätzt aus Phase 0 (Wiederholbarkeit der Indeximpulse, P0.6, oder aus den Lⱼ-Läufen; derselbe Schätzer wie im
  Generator von Abschnitt 5); (2) an Punkten, deren vorhergesagter Knick innerhalb ±u(Δδⱼ) liegt, das Maximum von s
  über diesen Bereich; (3) Ziehungen auf Einheitskovarianz normiert oder Delta-Methode (die 512 festen Ziehungen
  von PR #22 verzerren s_i um den Faktor 0,94–1,04). Dazu: Piloten behalten das gepoolte σ_Δ,F (p̂ unverändert
  definiert); fehlt s_i, ist G4 „nicht prüfbar“; eine registrierte Zielrate je Konfiguration in A9.11.
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
  Jitter, konfigurationsabhängiges Rauschen, größere Laufversätze, Phasendrift im Lauf; 6 Szenarien × 3 Systeme ×
  300 statische Kampagnen, Auswertung aller Varianten auf denselben Läufen; etwa 4,5 Kernstunden plus
  Generatoroptionen (gehört zu d).
- **R3:** Trendempfindlichkeit je Variante für registrierte Trendklassen, nachträglich auf R1/R2-Daten; Minuten.

### 2.6 Fragen an den Autor

- F-b1: Muss G4 an steilen Punkten Amplitudentrends unter etwa 1 % erkennen (dann D), oder genügt die Erkennung an
  flachen Punkten (dann B+)?
- F-b2: Zielrate je Konfiguration als Kriterium in A9.11: ≤ 1,5 % je Lauf, oder ≤ 1 % mit Faktor k(n)?
- F-b3: Ist eine Formatänderung der Laufzusammenfassung (Fünftelzeiger) vor dem Einfrieren annehmbar
  (Voraussetzung für D und für die Schätzung der Laufphasenstreuung aus Pilotdaten)?
- F-b4: Piloten beim gepoolten σ_Δ,F belassen (p̂ unverändert) oder ebenfalls standardisieren?
- F-b5: G4 an Lⱼ: σ_Δ über die Module poolen, Faktor k(n), größeres n₀, oder erst R1 abwarten?
- F-b6: R1 und R2 (zusammen etwa 11–14 Kernstunden plus Code) vor der Neukalibrierung beauftragen?

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
- PR #23 (gezählt, 30 Nullkampagnen mit Ablauf, Entwicklungsplan n = 24, n_min = 18, 630 geplante Läufe): 5 halten
  an (S1 nach reproduziertem Nullpunktalarm 2, S1 nach G1-Verstoß von X′ 2, S3 1); dazu halten die Regelpfade S02
  (S2) und S06 (S3). Gemeinsam vollständig 25/30; jede abgeschlossene Kampagne ist vollständig. Wilson-Intervall
  für die Haltrate 5/30: [0,07; 0,34].
- Schranken aus A8 (gelesen und nachgerechnet): S1 je Kampagne bis 0,25–0,29 je nach Laufzahl, S3 reproduziert bis
  0,020–0,024; zusammen bis etwa 0,3. Das sind obere Schranken bei exakter Superposition.
- Halte nach ε_ctrl (gezählt aus den Befunden der 30 Kampagnen von PR #23): Die beiden S1-Halte über X′ liegen auf
  Rang 1 und 4 der 30 Kampagnen nach aufsteigendem ε_ctrl (V1-G0 Nr. 2 mit 0,222 mN und 13 X′, Nr. 7 mit
  0,265 mN). Die drei übrigen Halte liegen auf Rang 12, 13 und 17. Die Zahl der G1-Fälle und der X′ fällt mit
  ε_ctrl (Spearman −0,81 bzw. −0,65). Eine über Kampagnen homogene Haltrate ist deshalb nur eine Näherung; für die
  Planung zählt die Verteilung von ε_ctrl. Bei 30 Kampagnen ist das ein Hinweis, keine Rate.
- Folgen, wenn ein Halt als verloren zählt (gerechnet aus der empirischen Rate 5 Halte auf 18 215 Versuche):
  P(kein Halt) ≈ 0,82–0,83 für 630–688 Läufe (Bereich 0,63–0,94), 0,74 für n = 30 bei N_K = 23 und N_I = 3. Dann
  gilt P(H1 und H2) ≤ P(kein Halt), und für 0,8 müsste P(bestätigt | ohne Halt) ≥ 0,96 sein. Die Grenze fällt mit
  der Laufzahl; Reserve und Laufzahl helfen nicht.
- Reserve unter dem Wiederholungsablauf (gerechnet, Binomial): Ein Platz fehlt erst nach drei ungültigen Versuchen;
  selbst mit 30 % ungültigen Versuchen ist P(Punkt < n_min) ≤ 2·10⁻³ bei n = 21, r = 3. Die Formel reicht gegen
  punktweise Ausfälle; über die gemeinsame Vollständigkeit entscheiden die Halte.
- Simulierte Wiederaufnahme (gerechnet): Der W-Satz hätte zu etwa 4,7 % selbst einen Alarm (etwa 1 % je
  Referenzlauf, 3,7 % S3-Einzelüberschreitung je Satz), Kettenfaktor etwa 1,05; mit der Fassung N7 aus Abschnitt 1
  weniger. Eine bedingte Zählung ohne S3-Halte verzerrt c im Nullmodell vernachlässigbar (3,4775 gegen 3,4783 in
  einer vereinfachten Rechnung).
- Die Prüfschwelle 0,069 setzt 1000 verwertbare Kampagnen voraus (A8); bei 833 wären es 0,0714.

### 3.2 Optionen

- **(i) Halt = nicht vollständig** (heute). Konsequent wäre, auch c nur aus abgeschlossenen Kampagnen zu bilden.
  Begrenzt die 0,8-Bedingung durch die Haltrate; die Planung kann scheitern, ohne dass die Präzision der Grund ist.
- **(ii) simulierte Wiederaufnahme (empfohlen).** Werkzeug 8 setzt jeden fortsetzbaren Halt fort wie der
  Messbetrieb: protokolliertes synthetisches Ereignis „Ursachenanalyse ohne Befund, kein Eingriff, kein
  Apparaturfehler“, Kontrollsatz nach `ablauf-4`, Fortsetzung des Blocks; Parameter: höchstens W Wiederaufnahmen je
  Kampagne (Vorschlag 3), Analysezeit T_UA, Aufwärmen bei Tageswechsel. Als verloren zählt nur ein Abbruch (zweites
  S2, W erschöpft, mechanischer Eingriff nötig). Nur (ii) erzeugt dieselbe Menge von Kampagnen wie der reale
  Versuch.
- **(iii) bedingte Zählung** nur über Kampagnen ohne Halt. Nachziehen bis zur Sollzahl; im Nullmodell nahe an (ii),
  in Szenarien mit echter Ursache verzerrt.
- **(iv) getrennte Zielgrößen:** P(H1 und H2 | ohne Halt) als Planungsbedingung, Haltrate je Regel als zweite
  Größe gegen die A8-Schranken, (1 − h)·P als Sensitivität.

### 3.3 Empfehlung

(ii) als maßgebliche Zählung in Planung, Kalibrierung, Prüfsimulation und Kriterien, ergänzt um die
Berichtsgrößen aus (iv): Anteil mit mindestens einem Halt je Regel neben der A8-Schranke für die tatsächliche
Laufzahl, Wiederaufnahmen (Mittel, Maximum), Anteil nicht fortgesetzt, zusätzliche Messzeit, P(H1 und H2 | ohne
Halt) und (1 − h)·P als Sensitivität. Für Szenarien mit echter Ursache (S04, E07, E09, I02) (ii) und (i)
nebeneinander berichten. Eine Bezugsmenge für c, b̂, H2-Überdeckung, Prüfrate und P(H1 und H2): abgeschlossene
Kampagnen nach Wiederaufnahme mit allen z endlich, Ausschlüsse nach Grund gezählt; damit stimmt auch die Herleitung
der Prüfschwelle wieder. Reserveformel „+2“ beibehalten; kein eigenes Vollständigkeitsziel, weil H1 alle 21 Punkte
verlangt und die Vollständigkeit damit in P(H1 und H2) enthalten ist (ein Ziel, das Halte einschließt, wäre
faktisch Option (i); das Ziel 0,95 aus PR #22 G3 wird als Berichtsgröße „alle Punkte ≥ n_min“ geführt). Die
Zeitformel erhält Terme für Wiederholungen (gemessen +5,4 %, höchstens +9,5 %) und Wiederaufnahmen (W-Satz, T_UA,
Aufwärmen).

Voraussetzungen: Abschnitt 1 ist festgelegt (die Wiederaufnahme muss `ablauf-4` simulieren, nicht `ablauf-3`), und
die Halt- und Wiederaufnahmeraten sind mit R1 (Abschnitt 3.5) gemessen, bevor Werkzeug 8 kalibriert wird.

### 3.4 Änderungen

- Normtext: §5.4 nach „(A9.11)“ (Bezugsmenge alle simulierten Kampagnen; Halte wie im Messbetrieb behandelt; nicht
  fortgesetzte oder abgebrochene Kampagne zählt als nicht bestätigt); §9.2 nach Z. 826 (Alarm im W-Satz → weitere
  Ursachenanalyse; Simulation rechnet Halte als Unterbrechung); A9.11 neuer Absatz „Halte in der Simulation“ (W,
  T_UA, Aufwärmen, Bezugsmenge, Berichtsgrößen); §5.3 (c) Zeitformel; §12 Zeile „Messzeit“ ergänzen; Tabelle F; A0.
- Code: Harness-Automatik der Wiederaufnahme in `kampagnen`, `planung`, `kalibrierung` und Prüfstand (synthetisches
  Ereignis, W, T_UA); Zähler je Regel; Bezugsmenge in `kalibrierung` (Status statt „z endlich“) und `kampagnen`;
  Statusvorrang „fehlt: Halt“ in `ablauf.bericht` nach erfolgreicher Wiederaufnahme korrigieren; Zeitformel im
  Planungshaken.
- Tests: Wiederaufnahme mit synthetischem Ereignis bis W, Abbruchfälle, Bezugsmenge, Zeitkosten, Berichtsgrößen.
- Aufwand: etwa 1–1,5 Personentage.

### 3.5 Rechnungen

- **R1-Halte:** Halt- und Wiederaufnahmeraten je Regel mit `ablauf-4`, gepaart für (i) und (ii) mit denselben
  Seeds, A4, V1-G0, V1-G60h je 1000 Kampagnen, Zähldiagnose ohne Stufe 2; dazu die Tabelle ε_ctrl × G1-Fälle ×
  Halte je Kampagne (Prüfung der Homogenitätsannahme; für die 30 Kampagnen aus PR #23 in 3.1 bereits gezählt) und
  die A8-Schranken für die tatsächliche Laufzahl. Etwa
  4–6 Kernstunden; Monte-Carlo-Fehler der Haltrate etwa 0,012. Lässt sich mit R1 aus Abschnitt 2 in einem Lauf
  verbinden.
- **R2-Halte:** ob (iii) unter Null eine gute Näherung von (ii) ist, und die Variante „Datenschluss nach §6“ für
  nicht fortsetzbare Kampagnen; mit fester Testvorgabe für c; nachträglich auf R1-Daten, Minuten.

### 3.6 Fragen an den Autor

- F-b7: Zählung (ii) als maßgeblich, mit der 0,8-Bedingung über alle simulierten Kampagnen?
- F-b8: Parameter der Wiederaufnahme: höchstens W = 3 je Kampagne, Analysezeit T_UA (Vorschlag: Teil-B-Wert, in der
  Entwicklung 1800 s), Aufwärmen bei Tageswechsel?
- F-b9: Nicht fortsetzbare Kampagne: Sperre aller Ausgänge (konservativ) oder Datenschluss nach §6 mit Auswertung?
  Gilt dasselbe für den realen Versuch?
- F-b10: Haltrate je Regel nur Berichtsgröße oder eigenes Kriterium (S1 ≤ A8-Schranke bei tatsächlicher Laufzahl,
  S3 reproduziert ≤ 0,020)?
- F-b11: Zeitformel um Wiederholungen und Wiederaufnahmen erweitern (§12 „Messzeit“)?

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
- **B (empfohlen): am Rand gültige Grenzen für E3b.** Aus den Bootstrap-Replikaten der komplexen Differenz die
  2×2-Kovarianz Σ̂ (korrigiert mit n/(n − 1)), ŝ² = λ_max(Σ̂), ν = min(n_A, n_B) − 1. Auffällig, wenn
  q_Z > κ·ŝ·Rice⁻¹(1 − α/m; q_tol/(κ·ŝ)) mit κ = t(1 − α/m; ν)/z(1 − α/m); unauffällig, wenn
  q_Z + t(0,95; ν)·ŝ ≤ q_tol. Größe am Rand ≤ 0,96·α/m bzw. ≤ 0,0505 in allen geprüften Fällen (ν ∈ {10, 21, 40,
  80}, Anisotropie 1 bis 0,1, t ∈ [0,25; 10], drei Richtungen). Ohne κ und mit eingesetztem ŝ bliebe die Regel
  bei bis zu 2,8·α/m, mit √(Spur/2) statt λ_max bei bis zu 9,9·α/m; eine „Rice-exakte“ Grenze ist nur bei bekanntem
  s exakt.
- **C: Vertrauensscheibe** (Mahalanobis-Radius √(2·F⁻¹)); gültig, aber deutlich schwächer (Macht 0,12 statt 0,26 bei
  0,3° auf L1).
- **D: kritische Werte je Richtung aus der vollen Σ̂**, numerisch je Kampagne; mächtiger, aufwendiger, später
  möglich.
- **E: Rückfall für E3 als Ganzes** (heutiges Profil ENTW „ganz“): nicht empfohlen, weil E3a auf L1 beide Kriterien
  erfüllt und dann mitfiele.

Macht von B (gerechnet, ν = 40, isotrop): bei 0,3° an einem Modul auf L1 0,26 (heutige, ungültige Regel 0,56;
Scheibe 0,12), bei 1 % Amplitudenänderung ≥ 0,999, bei t = 3 und 0,3° 0,99. Phasenversätze erkennt E3a auf L1
ohnehin sicher; E3b ergänzt vor allem Amplituden- und Kombinationsänderungen. „Unauffällig“ bei exakter Superposition:
mit B bei t = 1,5 praktisch 0 (heute 7 %), erst ab t ≈ 3,4 über 0,8; die bestmögliche gültige Regel (Neyman-Pearson,
s bekannt) erreicht 0,8 ab t ≈ 3,2. Das Kriterium „unauffällig ≥ 0,8“ ist für E3b bei der Präzision von L1 mit
keiner gültigen Regel erreichbar; der Rückfall je Prüfgröße macht daraus eine einseitige Auswertung, E3a bleibt
dreiwertig. Modellnachzählung der 570 Kampagnen (gerechnet, isotrope Näherung, m = 43): H03 30/30 → 30/30;
E07-basisdrift 36/40 → 33/40 (ν = 40) bzw. 32/40 (ν = 21); A06 3/30 → 0; N01-A4/L4 (exakte Superposition) 2/40 → 0;
E3a auf L4: der eine Fehlalarm bei exakter Superposition (1/40) entfällt mit t-Quantil.

### 4.3 Empfehlung

Option B mit den Festlegungen: Prüfmenge 21 Schnittpunkte (E3a) und Triphasik-Punkt (E3b), ohne
Identifizierbarkeits- und Zusatzkonfigurationen; m = 43 fest, auch bei nicht auswertbaren Punkten, Rückfall einer
Prüfgröße oder N_K = 23; Bonferroni für die Gesamtaussage; E3a mit t-Quantilen (ν = n_A − 1, Varianz mit n/(n − 1));
„E3 unauffällig“ nur, wenn beide Prüfgrößen dreiwertig ausgewertet werden und alle Prüfungen unauffällig sind, sonst
E3a und E3b getrennt; „nicht prüfbar (Grund)“ bei nicht auswertbarem Triphasik-Punkt oder singulärer Σ̂, m bleibt 43.
A9.11 erhält ein Gültigkeitskriterium am Rand (auf Statistikebene) und die Modellprüfung in den Kalibrierkampagnen
(Kalibrierung von ŝ, Isotropie, PIT). Wenn vor realen Daten kein neuer E3b-Code gewünscht ist: Option A mit
denselben Festlegungen; B lässt sich vor dem Einfrieren nachziehen, ohne m zu ändern. Die Laufzahl hängt in keiner
Variante von E3 ab.

### 4.4 Änderungen

- Normtext: A9.13 (Grenzen für E3a und E3b, m = 43, Prüfmenge, Bonferroni, nicht prüfbar); §8.10 und A9.11 (Rückfall
  je Prüfgröße, Gültigkeit am Rand als Kriterium, Modellprüfung); §12 Zeile „Schwellen von E3“ (Option (a) mit
  Rückfall je Prüfgröße festgelegt); A0.
- Code: `kontrollen.py` (2×2-Kovarianz, κ, Rice-Grenze, t-Quantile, m fest, Urteil je Prüfgröße), `auswertung.py`
  (Prüfmenge, Profilwerte wirklich binden), `regeln.py` (e3.* festlegen), Kriterienmatrix.
- Tests auf Statistikebene (Sekunden): Größe am Rand über ν, Anisotropie und t; Gleichheit zu PR #22 bei bekanntem
  s; E3a-Grenzen; Nachzählung der gespeicherten 570 Prüfgrößen als Regression.
- Aufwand: etwa 1 Personentag; keine zusätzlichen Kampagnen (die Modellprüfung läuft in den ohnehin geplanten
  Kalibrierkampagnen mit).

### 4.5 Fragen an den Autor

- F-c1: E3b jetzt mit gültiger Grenze (B) oder vorerst beschreibend (A), in beiden Fällen m = 43 fest?
- F-c2: Rückfall je Prüfgröße; „E3 unauffällig“ nur bei beiden dreiwertigen Prüfgrößen?
- F-c3: E3a auf t-Quantile mit ν = n_A − 1 umstellen (ändert den Wortlaut von A9.13 auch für E3a)?
- F-c4: Freiheitsgrade konservativ ν = min(n_A, n_B) − 1 (empfohlen) oder Welch-Satterthwaite (mächtiger, leicht
  antikonservativ)?
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
  Residuenstreuung um bis zum Faktor 2,2–2,4 überschätzen (bei L1 1,03–1,21). (3) Konfigurationsabhängigkeit: Das
  Verhältnis der Varianz von Re bzw. Im N_k an einem Schnittpunkt zum gepoolten Pilotwert liegt bei
  modulproportionaler Streuung zwischen 0,52 und 1,65 (k = 2) und 0 und 1,63 (k = 3); am Triphasik-Punkt ist bei
  k = 3 alles gleichphasig. (4) Fünftel und F_min stehen in der Pilotkovarianz nicht; die Flankenabhängigkeit von
  G4 ist eine zweite Konfigurationsabhängigkeit. (5) Im Katalog hat kein Szenario eine Nullpunktdrift; σ̂_ref ist im
  Generator rein weiß, A9.11 verlangt „Rauschen, Jitter und Drift“.
- Zwei Textstellen widersprechen sich: A9.2 sagt für die Suche „c als c_B“, der Haken simuliert c (ohne Wirkung auf
  die Bedingung, weil die Bestätigung von c nicht abhängt); A9.11 nennt „dieselbe Simulation“ für n_min, b̂ und c,
  die Planungsbedingung verlangt aber die obere Grenze, b̂ und c skalieren mit dem Rauschpegel.
- Zusicherung der Planungsregel (gerechnet, vereinfachtes unabhängiges Modell 7 × 42): Mit Punktschätzern liegt
  P(wahres P ≥ 0,8) bei 0,48–0,56, mit κ(ν) bei 0,81–0,88. Der Schätzfehler der Kovarianz wirkt auf c mit SD 0,010
  gegen den Monte-Carlo-Fehler 0,039 bei 1000 Kampagnen; eine Wishart-Fortpflanzung für c ist nicht nötig.
- §5.4 (Z. 373–374) verbietet dem Pilotskript die Ausgabe von Superpositionsresiduen der Piloten. Den ρ-Anteil
  herauszurechnen und die Pilotkovarianz aus den Lⱼ-Kovarianzen vorherzusagen braucht die Einzelmodul-Mittelkurven
  N̄⁽ʲ⁾ (zweite Momente, keine Residuen); ob das zulässig ist, entscheidet der Text nicht.

### 5.2 Optionen

- **A: Szenariofamilie mit aus Phase 0 geschätzten Parametern** (Amplituden- und Phasenstreuung je Modul und
  Laufart, weißes Rauschen je Zelle, Indexversatz, Zyklusjitter, T_φ, neu Nullpunktprozess und laufinterner Anteil)
  per Momentenschätzung. 2–3 Personentage. Geht als Sonderfall in C auf.
- **B: empirische Kovarianz je Laufart direkt (Gauß)** mit den gepoolten Pilotkovarianzen. Wörtliche Lesart, aber
  an den Schnittpunkten systematisch falsch (oben); nur als Diagnose- oder Sensitivitätsvariante. 1–2 Personentage.
- **C (empfohlen): Strukturmodell aus Phase 0.** Schätzung im Pilotskript (nur zweite Momente, gebunden an k und
  N_z): Sensorboden aus den R-Läufen (ν ≥ 41) und σ_c; Modulanteil je Modul aus den Lⱼ-Läufen (ν = n₀ⱼ − 1) in
  Gleichphase, Quadratur und Rest je Harmonischer; erfasster Phasenanteil aus den Zeigern; Nullpunktprozess aus
  der Referenzfolge; Fünftel aus dem laufinternen Anteil. Fortpflanzung auf jede Konfiguration über die gemessenen
  Zeiger und ŷ⁰ (Struktur aus Phase 0 am Arbeitspunkt, aus Werkzeug 2 für Kandidatenfrequenzen). Obere 80-%-Grenze
  je Komponente mit eigenem ν nur für die Planungsbedingung; Teil-B-Werte (c, b̂, H2-Typ, E3-Raten, ε_ctrl-Quantil)
  mit Punktschätzern (zweite Simulation). 6–9 Personentage einschließlich A als Sonderfall.
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
(1) Regeltexte (Komponentenzerlegung, κ je Komponente, Punktschätzer für Teil-B-Werte, Liste der Rauschmodelle,
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
  Modi A/C/D), `harness/planung.py` (Haken ohne Szenario-ID, κ je Komponente), `kampagnen`/`kalibrierung`
  (Modellquelle), `teil_b.py` (Felder), `regeln.py`.
- Tests: Rundreise Pilot → Generator → Pilot (Wiedergewinnung von s_q, σ_Δ, σ̂_ref, p̂, Komponenten); Modus A
  bitgleich zum Szenariogenerator; Gleichheit der Entscheidungen bei eingesetzter Szenariokovarianz; Singularität
  und Regularisierung; Wahrheitstrennung (kein Zugriff auf Szenario-Wahrheit im Pilotmodus).
- Aufwand: 6–9 Personentage für C mit A, dazu 2–3 für D.

### 5.5 Rechnungen

- **R1-d:** Rundreise auf etwa 1000 synthetischen Phase-0-Sätzen je Szenario (N01-A4, N04-laufart, N03-ungleich,
  L0/L2/L4), ohne Stufe 2; ≤ 0,5 Kernstunden.
- **R2-d:** Gleichheit mit dem Szenariomodell auf Ebene der Entscheidungen (2 Szenariopunkte × 2 Generatoren × 400
  Kampagnen, B = 1000): etwa 1,5–2 Kernstunden.
- **R3-d:** Planung mit dem Pilotmodell gegen das Szenario-Orakel für K12-ähnliche Suche in Entwicklungsgröße;
  Kosten wie eine Planungssimulation je Kandidat in Entwicklungsgröße (Stunden).
- Die Rechnungen für Teil B selbst (Kalibrierung je System 18–81 Kernstunden, Planungssimulation je Kandidat ebenso;
  gelesen PR #23) sind davon getrennt und AP-21.

### 5.6 Fragen an den Autor

- F-d1: Lesart von „Streuungen an ihrer oberen 80-%-Vertrauensgrenze“ für ein mehrteiliges Modell: ein Faktor für
  alles (heute), jede Komponente mit eigenem ν (empfohlen), oder ein Faktor mit dem kleinsten ν?
- F-d2: Teil-B-Werte (c, b̂, H2-Typ, E3-Raten, ε_ctrl-Quantil) mit Punktschätzern aus einer zweiten Simulation
  (empfohlen) oder alles an der oberen Grenze („dieselbe Simulation“, A9.11)?
- F-d3: Darf das Pilotskript die Einzelmodul-Mittelkurven N̄⁽ʲ⁾ für zweite Momente verwenden, ohne gegen §5.4 zu
  verstoßen?
- F-d4: §12 Rauschmodelle: Fassung (b) mit der Liste {Strukturmodell, Familienanpassung, optional Bootstrap}; c nach
  (a) oder (b)?
- F-d5: Struktur in der Planung am Arbeitspunkt aus P0.8 oder aus Werkzeug 2 mit den Parametern aus P0.1–P0.5?
- F-d6: Nicht schätzbare Komponenten als benannte Sensitivitätsszenarien in Teil A, nur berichtet?
- F-d7: Soll Stufe 1 die Zeiger der Fünftel speichern (farbiger Jitter, Jitterstreuung der Fünftel für G4)?
- F-d8: Soll der Prüfstand künftig mit dem Pilotmodell planen und das Szenario nur als Orakel dienen?

## 6 Reihenfolge, Abhängigkeiten, Paketierung, Entscheidungsliste

Abhängigkeiten:

- b2 (Halte) setzt a voraus: Die simulierte Wiederaufnahme muss `ablauf-4` abbilden; Ablaufversion und Zählweise
  gehören zum Checkpoint-Schlüssel und zur Bezugsmenge jeder Kalibrierung.
- b1 (G4) lässt sich als Regel ohne d festlegen; ihre Zahlen für Teil B, die Robustheitsrechnung R2 und der
  Schätzer der Laufphasenstreuung hängen an d. R1 läuft schon mit dem Szenariogenerator.
- c ist von a, b und d unabhängig (eigener Codepfad, keine Wirkung auf die Laufzahl); die Modellprüfung von E3 nutzt
  später das Zellrauschen aus d.
- d steht vor jeder Neukalibrierung, weil Teil B kein Szenario hat.
- Werkzeug 8 neu (55–243 Kernstunden für drei Systeme, gelesen PR #23) erst nach a, b1, b2, c, d; sonst wird
  zweimal kalibriert. Das weicht von §12 Z. 999–1001 ab (Festlegungen „gestützt auf Werkzeug 8“); Begründung für A0:
  Die Kalibrierung setzt Ablauf, Zählweise und Rauschmodell voraus.

Vorgeschlagene Paketierung, je PR mit Normtext (§12-Zeile, A0, Regelstelle), `regeln.py`, Code, Tests,
Regelmatrix und Prüfsätzen:

| PR | Inhalt | Rechnung | Aufwand (Einschätzung) |
|---|---|---|---|
| 0 (Vorbereitung, kann in PR 1) | Präfix `ablauf.` in `regeln.py` und Regelmatrix; Profilwerte `e3.*` und `planung.zielfunktion` an den Code binden; „\|“ auch in der Gegenstandsspalte der Regelmatrix maskieren; Profilkennungen versionieren (AF-/ENTW-2026-11), damit gespeicherte Profile lesbar bleiben | keine | 0,5 Personentag |
| 1 | a: `ablauf-4`, Offline-Gegenproben, Prüfsatz | keine | 1–2 Personentage |
| 2 (parallel zu 1) | c: E3-Grenzen, m = 43, Rückfall je Prüfgröße, Kriterienmatrix | Statistikebene (Sekunden) | 1 Personentag |
| 3 | d: Strukturmodell, Pilotschätzer, Planungshaken | R1-d, R2-d, R3-d (≈ 2–5 Kernstunden) | 6–9 Personentage |
| 4 | b1: G4 B+ (oder D), Zielrate | R1 (≈ 6–9 Kernstunden), R2 (≈ 4,5), R3 | 1,5–5 Personentage |
| 5 | b2: Wiederaufnahme in Werkzeug 8, Bezugsmenge, Berichtsgrößen, Zeitformel | R1-Halte (≈ 4–6 Kernstunden, mit R1 verbindbar) | 1–1,5 Personentage |
| danach | Neukalibrierung Werkzeug 8, Planungssimulation, Prüfstandsauswahl, E3-Punkte | 55–243 Kernstunden | AP-13/AP-21 |

Rechenbudget: Die Zähldiagnosen R1 (G4 und Halte zusammen, 3 Systeme × 1000 Kampagnen × 3 Varianten, ohne
Bootstrap) kosten etwa 7–10 Kernstunden, R2 etwa 4,5 Kernstunden. Das liegt weit über den bisherigen Zusatzbudgets
(40 Ausführungen) und braucht einen eigenen Auftrag mit Auftragsliste, Seeds und Checkpoints wie in PR #22/#23.

Entscheidungsliste (Kurzform; Empfehlung in Klammern):

1. F-a1 Reihenfolge A1 + Z1 (ja). 2. F-a2 Halt H1 (ja). 3. F-a3 K1 oder K2 (K1). 4. F-a4 N7-Fassung (S1–S4 und
   Nullpunktalarm; Nullpunktalarm im W-Satz: Autor). 5. F-a5 Aufwärmen bei Tageswechsel (ja). 6. F-a6 übrige
   Lesarten im selben PR (ja).
2. F-b1 B+ oder D (B+, wenn keine Trendempfindlichkeit an steilen Punkten verlangt ist). F-b2 Zielrate (≤ 1,5 %).
   F-b3 Fünftelzeiger im Format (ja, auch für d). F-b4 Piloten gepoolt (ja). F-b5 G4 an Lⱼ (R1 abwarten, Pooling
   bevorzugt). F-b6 R1/R2 beauftragen (ja).
3. F-b7 Zählung (ii) (ja). F-b8 W = 3, T_UA, Aufwärmen bei Tageswechsel. F-b9 nicht fortsetzbar: Sperre (ja).
   F-b10 Haltrate als Berichtsgröße (ja). F-b11 Zeitformel erweitern (ja).
4. F-c1 E3b Option B (ja). F-c2 Rückfall je Prüfgröße (ja). F-c3 E3a mit t (ja). F-c4 ν konservativ (ja). F-c5
   Amplitudenszenario (ja).
5. F-d1 κ je Komponente (ja). F-d2 Punktschätzer für Teil-B-Werte (ja). F-d3 N̄⁽ʲ⁾ für zweite Momente (ja). F-d4
   Liste (b), c nach (a) mit Sensitivität. F-d5 Struktur (P0.8 am Arbeitspunkt, Werkzeug 2 für Kandidaten). F-d6
   Sensitivitätsszenarien (ja). F-d7 Fünftelzeiger (ja). F-d8 Prüfstand mit Pilotmodell, Szenario als Orakel (ja).
6. Paketierung und Abweichung von §12 Z. 999–1001 mit A0-Begründung (ja).

## 7 Grenzen dieser Vorlage

- Alle Rechnungen sind Rechnungen auf Statistikebene mit vereinfachten Annahmen (Normalmodelle, Unabhängigkeit,
  Isotropie, homogene Haltrate); sie sind gekennzeichnet und ersetzen keine Kalibrierung. Die Skripte liegen noch
  außerhalb des Repositorys und werden mit den jeweiligen PRs als geprüfte Rechnungen nachgereicht.
- Die Zahlen aus PR #22 und #23 stammen aus Entwicklungsläufen (reduzierte Replikatzahlen, zehn bis vierzig
  Kampagnen je System) und aus Kampagnen mit statischem Laufplan oder `ablauf-2`/`ablauf-3`; sie zeigen Richtungen,
  keine Raten.
- Nachprüfungen mit eingeschränkter Tiefe: Fünf geplante unabhängige Nachprüfungen konnten nicht laufen. Sie sind
  so ersetzt: Bezugsmenge für c durch eigenes Nachlesen von `kalibrierung.py` (3.1); E3b-Konstruktion durch die
  gezählten und gerechneten Varianten in Abschnitt 4; Reihenfolge und Aufwand durch Abschnitt 6; ε_ctrl als Treiber
  der Halte durch die Zählung in 3.1 an 30 Kampagnen. Offen bleibt die Herkunft der Laufphasenstreuung von Lauf zu
  Lauf; B+ stützt sich dafür nur auf P0.6 und den Lⱼ-Schätzer. R2 aus Abschnitt 2 prüft sie mit größeren
  Laufversätzen.
- Nicht behandelt: Punkt e) (realer Pilot), die Hardwareentscheidungen von §12 (II) und die Fassung der
  Zeitformel im Einzelnen.
