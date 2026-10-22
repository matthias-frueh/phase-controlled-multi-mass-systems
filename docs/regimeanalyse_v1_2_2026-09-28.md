# PCMMS – Regimeanalyse v1.2

**Projekt:** PCMMS – Phase-Controlled Multi-Mass Systems  
**Autor / Projektleitung:** Matthias Früh  
**Arbeitsstand:** 28. September 2026 (v1.1 vom 23. September 2026)  
**Dokumenttyp:** interne numerische Prüf- und Ergebnisnotiz  
**Status:** Simulation; keine experimentellen Messdaten  
**Schwerpunkt:** Linie A – Kontakt-/Regimedynamik im 19×19-Phasenraum  
**Ersetzt:** `PCMMS_Regimeanalyse_v1_1_2026-09-23.md`; neu ist der Nachtrag zur Bistabilität der Satelliteninseln (§7a), Änderungsvermerk am Ende

> **Vermerk (22.10.2026).** Originaldatei `PCMMS_Regimeanalyse_v1_2_2026-09-28.md`, Stand 28.09.2026 (v1.2; ersetzt
> v1.1 vom 23.09.2026, die nicht im Repository liegt); interne numerische Prüf- und Ergebnisnotiz, hier unverändert bis
> auf diesen Vermerk. Linie A, Modell der Referenz-Engine (v3a, Festschritt-RK4); nur Simulation, keine Messdaten,
> keine Chaos-Aussage; die Reihenfolge Ereignislöser → Basin-Scan → Lyapunov-Test steht in §0 und §13. Ausgewertet sind
> 2400-s-Läufe an 23 Punkten des 19×19-Rasters mit stroboskopischen Größen; die Tabelle in §3 gibt
> [`../data/regime_2400s.csv`](../data/regime_2400s.csv) und [`../data/regime_2400s_dt2.csv`](../data/regime_2400s_dt2.csv)
> gerundet wieder. Das Skript, das beide erzeugt hat, ist nicht überliefert ([`../data/README.md`](../data/README.md));
> die Zusatzläufe zu (12,17) und (9,9) (§1.2) liegen nicht im Repository. Seit dem 28.09.2026 erledigt oder offen:
> - **Ereignislöser (§0, §13 Schritt 1):** liegt vor ([`../code/ereignisloeser.py`](../code/ereignisloeser.py); AP-03
>   „vorhanden“, [`arbeitsplan_status.md`](arbeitsplan_status.md)) und bestätigt an der Insel (35°, 116°) beide
>   Zustände, den Hüpfzustand vom Standardstart (λ = 75,8154 %) und den Kontaktorbit (F_min = 0,3665 N)
>   ([`abnahme_ap02_ap03.md`](abnahme_ap02_ap03.md), Abschnitt AP-03). Nach dieser Abnahme ist eine Δt/2-Differenz im
>   Kelvin-Voigt-Hüpfbereich auch für die Engine keine Fehlerschätzung; das betrifft die Gruppen A–D (§2–§6).
> - **Offen (§13 Schritte 2–6):** Ereignisgenaue 2400-s-Läufe der 23 Punkte mit Konvergenzfolge, ein Basin-Scan und
>   ein Lyapunov-Test zu (9,9) liegen nicht vor; Nr. 34 und 41 der
>   [Offenen Punkte](arbeitspapier/PCMMS_Arbeitspapier_Offene_Punkte.md) sind offen. Die Engine-Prüfung der
>   Gesamtprojektanalyse (Stand 02.10.2026) hat das 19×19-Raster mit drei Starts über 40 s im Festschritt, in der
>   Gegenprüfung auch ereignisgenau über 20–30 s, und einzelne Paare ereignisgenau nachgerechnet; an (12,17) (§7)
>   koexistieren dort ein stabiler Hüpfzustand und ein aperiodischer Zustand um 35 %
>   ([`../rechnungen/engine/PROTOKOLL.md`](../rechnungen/engine/PROTOKOLL.md), ENG-08, ENG-09;
>   [Gegenprüfung](../rechnungen/engine/verifikation/PROTOKOLL.md)). Attraktorkarten gibt es nur für den V1-Kandidaten
>   mit anderen Parametern ([`einzugsgebiete_v1_kandidat.md`](einzugsgebiete_v1_kandidat.md)). Die Nacharbeit der
>   Numerik der Linie A (Karten als Attraktormengen) ist AP-25, Status „später“.
> - **Mehrstabilität (§7a, §14, §15):** Im Liftoff-Bereich koexistieren an mindestens 99 von 361 Rasterpunkten mehrere
>   stabile Zustände (drei Starts, Festschritt-RK4; Arbeitspapier v2.5, Anhang B.6; Offene Punkte Nr. 38, Nachtrag
>   03.10.2026).
> - **Literatur (§9):** Die Kandidaten zu Impact-Oszillatoren sind vor einer Aufnahme gegen die Primärquellen zu prüfen
>   (Offene Punkte Nr. 42; AP-16, „vorhanden, mit Prüfbedarf“).
>
> Lizenz wie der Ordner `docs/`: CC BY 4.0 ([`../LICENSE-CC-BY-4.0`](../LICENSE-CC-BY-4.0)).

---

## 0. Kernaussage dieser Revision

Die 2400-s-Läufe zeigen eine reproduzierbare Struktur im stroboskopischen Zustandsraum.  
Sie rechtfertigen **noch keine** Aussage über Chaos, Grazing-Bifurkationen oder Multistabilität als gesicherte Eigenschaften des kontinuierlichen mechanischen Modells.

Unabhängig von diesen 23 Punkten ist Bistabilität an anderer Stelle der Phasenebene belegt: In sechs kleinen Satelliteninseln koexistieren ein Dauerkontaktorbit und ein springender Zustand (§7a). Der Dauerkontaktorbit ist eine exakte Lösung des linearen gedämpften Systems; der springende Zustand stammt aus dem Festschritt-RK4 und ist mit dem Ereignis-Solver zu bestätigen.

Der vorrangige offene Punkt ist der Integrator:

> Das bestehende v3a-Modell verwendet festschrittiges RK4 über die Umschaltbedingungen des unilateralen Kelvin-Voigt-Kontakts. Vor jeder dynamischen Interpretation der grenznahen Punkte ist ein ereignislokalisierender Solver mit Zeitschritt-Konvergenz erforderlich.

Die Reihenfolge lautet daher:

1. **Ereignis-Solver + dt-Konvergenz**, geprüft gegen den exakten linearen Dauerkontaktast (§7a)
2. danach Basin-Scan
3. danach formaler Lyapunov-Test

---

## 1. Datengrundlage

Diese Revision trennt strikt zwischen Daten, die durch die zwei 2400-s-CSVs gedeckt sind, und Zusatzläufen, die bislang nicht Bestandteil des kanonischen Projekt-Datensatzes sind.

### 1.1 Primär ausgewertete Dateien

- `regime_2400s.csv`
- `regime_2400s_dt2.csv`

Sie enthalten je 23 Punkte und unter anderem:

- `passk`
- `bestk`
- `bestjv`
- `bestjz`
- `meanv`
- `sdv`
- `recur_frac`
- `recur_switches`

Die zweite Datei verwendet den halbierten Schritt.

### 1.2 Nicht durch diese beiden CSVs gedeckt

Nicht aus den beiden 2400-s-Dateien prüfbar sind insbesondere:

- die behaupteten zwei Äste bei `(12,17)`,
- die Divergenz zweier minimal gestörter Trajektorien bei `(9,9)`,
- daraus abgeleitete Zahlen eines Lyapunov-artigen Fits.

Für diese Aussagen existierten während der Arbeitssitzung zusätzliche Ausgaben (`basin_12_17.txt`, `p99_*.csv`). Sie waren jedoch in der ersten Notiz nicht als kanonische Rohdaten beigefügt.

Daher gelten diese Resultate in dieser Fassung **nicht als Hauptbefund**.

Vor Verwendung im Arbeitspapier müssen die Rohserien reproduzierbar unter `data/` abgelegt und nach der Solverkorrektur erneut gerechnet werden.

---

## 2. Was die beiden 2400-s-CSVs tatsächlich tragen

Die 23 Punkte lassen sich anhand von `recur_frac`, `recur_switches`, `passk` und der Änderung bei Zeitschritthalbierung zunächst in vier rein numerische Gruppen einteilen.

### Gruppe A – dt-robust aperiodisch / irregulär

9 Punkte:

`(0,10), (10,0), (1,11), (11,1), (8,9), (9,8), (9,9), (10,18), (18,10)`

Kennzeichen:

- `recur_frac` bleibt bei beiden Zeitschritten niedrig, ungefähr 0,08–0,19,
- kein Punkt erfüllt das Periodenkriterium,
- Mittelwert und Streuung der stroboskopischen Geschwindigkeit bleiben vergleichsweise stabil.

**Zulässige Aussage vor Solverkorrektur:**  
Diese Punkte zeigen im verwendeten Festschritt-Solver robuste, langfristig irreguläre stroboskopische Folgen.

**Noch nicht zulässig:**  
„chaotisch“, „physikalisch aperiodisch“ oder „Attraktor“ als gesicherte Systemeigenschaft.

### Gruppe B – dt-robust intermittent

2 Punkte:

`(0,13), (13,0)`

Kennzeichen:

- `recur_frac ≈ 0,72–0,75` bei beiden Schritten,
- mehrere hundert Wechsel zwischen Wiederkehr und Nichtwiederkehr,
- die Wechselstatistik bleibt bei dt-Halbierung vergleichbar.

Diese beiden Punkte sind die stärksten Kandidaten für eine **dt-robuste intermittierende Struktur im verwendeten Modell**.

Auch hier ist die physikalische Interpretation bis zum Event-Solver zurückzustellen.

### Gruppe C – dt-abhängig, derzeit nicht klassifizierbar

9 Punkte:

`(1,16), (16,1), (15,16), (16,15), (2,13), (13,2), (6,8), (11,17), (17,11)`

Hier verschiebt die Zeitschritthalbierung die Wiederkehrstatistik stark.

Besonders auffällig:

- `(6,8)`: `recur_frac` etwa 0,19 → 0,59
- `(11,17)`: etwa 0,33 → 0,80
- `(17,11)`: etwa 0,27 → 0,78
- `(2,13)/(13,2)`: bei ursprünglichem dt formell P6 und `recur_frac=1`; bei dt/2 nur noch etwa 0,73–0,75 und kein `passk`

Diese Punkte dürfen derzeit **weder als intermittierend noch als stabil periodisch** klassifiziert werden.

### Gruppe D – bei dt/2 vollständig wiederkehrend / Toleranzgrenze bei dt

3 Punkte:

`(14,13), (14,14), (17,16)`

Bei ursprünglichem dt:

- `recur_frac ≈ 0,98–0,99`
- 19 / 24 / 36 Wiederkehr-Schalter

Bei dt/2:

- `recur_frac = 1`
- `recur_switches = 0`

Damit liegt die einfachste Interpretation derzeit nahe:

> Diese Punkte sitzen am numerischen Toleranzboden des alten Klassifikators und dürfen nicht als belastbare Intermittenzbeispiele verwendet werden.

---

## 3. Vollständige numerische Tabelle

**Wichtig:** `meanv` ist hier der Mittelwert der **stroboskopischen Proben** `ż(nT)`, nicht das kontinuierliche Zeitmittel der Translationsgeschwindigkeit.

| Punkt | Klasse | recur dt | switches dt | passk dt | recur dt/2 | switches dt/2 | passk dt/2 | meanv dt | meanv dt/2 | sdv dt | sdv dt/2 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| (0,10) | A — dt-robust aperiodisch / irregulär | 0.122 | 110 | – | 0.150 | 108 | – | +0.064037 | +0.064500 | 0.042079 | 0.042285 |
| (0,13) | B — dt-robust intermittent | 0.723 | 482 | – | 0.728 | 452 | – | +0.049108 | +0.049120 | 0.016086 | 0.016091 |
| (1,11) | A — dt-robust aperiodisch / irregulär | 0.151 | 136 | – | 0.127 | 132 | – | +0.031966 | +0.033446 | 0.056300 | 0.056414 |
| (1,16) | C — dt-abhängig, derzeit nicht klassifizierbar | 0.819 | 326 | – | 0.902 | 176 | – | -0.323858 | -0.323849 | 0.154008 | 0.153984 |
| (2,13) | C — dt-abhängig, derzeit nicht klassifizierbar | 1.000 | 0 | 6 | 0.746 | 246 | – | +0.029850 | +0.029729 | 0.066612 | 0.066626 |
| (6,8) | C — dt-abhängig, derzeit nicht klassifizierbar | 0.194 | 142 | – | 0.594 | 296 | – | -0.071083 | -0.079435 | 0.090848 | 0.106768 |
| (8,9) | A — dt-robust aperiodisch / irregulär | 0.156 | 166 | – | 0.130 | 154 | – | -0.084465 | -0.084614 | 0.073347 | 0.072728 |
| (9,8) | A — dt-robust aperiodisch / irregulär | 0.155 | 172 | – | 0.075 | 122 | – | -0.084079 | -0.084980 | 0.073356 | 0.072533 |
| (9,9) | A — dt-robust aperiodisch / irregulär | 0.075 | 118 | – | 0.112 | 124 | – | -0.084102 | -0.084836 | 0.060821 | 0.060857 |
| (10,0) | A — dt-robust aperiodisch / irregulär | 0.131 | 132 | – | 0.095 | 126 | – | +0.063380 | +0.063939 | 0.042511 | 0.042276 |
| (10,18) | A — dt-robust aperiodisch / irregulär | 0.129 | 130 | – | 0.151 | 144 | – | +0.078681 | +0.077535 | 0.033105 | 0.033174 |
| (11,1) | A — dt-robust aperiodisch / irregulär | 0.134 | 160 | – | 0.125 | 107 | – | +0.031574 | +0.031535 | 0.056250 | 0.056434 |
| (11,17) | C — dt-abhängig, derzeit nicht klassifizierbar | 0.332 | 230 | – | 0.796 | 368 | – | +0.055966 | +0.061094 | 0.025375 | 0.024182 |
| (13,0) | B — dt-robust intermittent | 0.741 | 410 | – | 0.751 | 412 | – | +0.048924 | +0.049152 | 0.015894 | 0.016129 |
| (13,2) | C — dt-abhängig, derzeit nicht klassifizierbar | 1.000 | 0 | 6 | 0.726 | 264 | – | +0.029851 | +0.029707 | 0.066613 | 0.066634 |
| (14,13) | D — bei dt/2 vollständig wiederkehrend / Toleranzgrenze bei dt | 0.988 | 19 | – | 1.000 | 0 | – | -0.320397 | -0.320401 | 0.001024 | 0.000537 |
| (14,14) | D — bei dt/2 vollständig wiederkehrend / Toleranzgrenze bei dt | 0.983 | 24 | – | 1.000 | 0 | 2 | -0.428041 | -0.428040 | 0.001046 | 0.000466 |
| (15,16) | C — dt-abhängig, derzeit nicht klassifizierbar | 0.771 | 388 | – | 0.858 | 256 | – | -0.042646 | -0.042656 | 0.288734 | 0.288722 |
| (16,1) | C — dt-abhängig, derzeit nicht klassifizierbar | 0.802 | 356 | – | 0.892 | 194 | – | -0.323870 | -0.323845 | 0.154005 | 0.153977 |
| (16,15) | C — dt-abhängig, derzeit nicht klassifizierbar | 0.764 | 396 | – | 0.862 | 248 | – | -0.042679 | -0.042665 | 0.288704 | 0.288713 |
| (17,11) | C — dt-abhängig, derzeit nicht klassifizierbar | 0.269 | 187 | – | 0.781 | 394 | – | +0.055161 | +0.061089 | 0.025474 | 0.024182 |
| (17,16) | D — bei dt/2 vollständig wiederkehrend / Toleranzgrenze bei dt | 0.980 | 36 | – | 1.000 | 0 | – | -0.497024 | -0.497063 | 0.024883 | 0.024835 |
| (18,10) | A — dt-robust aperiodisch / irregulär | 0.186 | 139 | – | 0.138 | 128 | – | +0.080271 | +0.079349 | 0.032600 | 0.032613 |

---

## 4. Zwillingstest durch Modulvertauschung

Für identische Module ist das Modell unter

`(i2,i3) ↔ (i3,i2)`

symmetrisch.

Im Rechenweg unterscheiden sich die vertauschten Fälle im Wesentlichen nur durch die Reihenfolge von Gleitkommaoperationen. Die entstehenden Unterschiede liegen zunächst in der Größenordnung numerischer Rundung.

Trotzdem können langfristige Trajektorien und diskrete Wiederkehrlabels auseinanderlaufen.

Die stroboskopischen Langzeitstatistiken `meanv` und `sdv` der Spiegelpaare bleiben dagegen eng beieinander:

| Spiegelpaar | rel. Differenz meanv | rel. Differenz sdv | recur_frac | bestk |
|---|---:|---:|---:|---:|
| (0, 10) ↔ (10, 0) | 1.027% | 1.018% | 0.122 / 0.131 | 50 / 25 |
| (0, 13) ↔ (13, 0) | 0.376% | 1.195% | 0.723 / 0.741 | 100 / 6 |
| (1, 11) ↔ (11, 1) | 1.225% | 0.088% | 0.151 / 0.134 | 8 / 10 |
| (1, 16) ↔ (16, 1) | 0.004% | 0.002% | 0.819 / 0.802 | 3 / 6 |
| (2, 13) ↔ (13, 2) | 0.002% | 0.001% | 1.000 / 1.000 | 6 / 6 |
| (8, 9) ↔ (9, 8) | 0.458% | 0.013% | 0.156 / 0.155 | 50 / 50 |
| (10, 18) ↔ (18, 10) | 1.981% | 1.528% | 0.129 / 0.186 | 7 / 4 |
| (11, 17) ↔ (17, 11) | 1.440% | 0.390% | 0.332 / 0.269 | 6 / 6 |
| (15, 16) ↔ (16, 15) | 0.078% | 0.010% | 0.771 / 0.764 | 6 / 6 |

Für die vorhandenen Paare liegen die relativen Abweichungen von `meanv` und `sdv` bei höchstens rund 2 %.

Das ist ein nützlicher interner **Zwillingstest**:

- Trajektorien-/Periodenlabels können stark auseinanderlaufen,
- grobe Zustandsstatistik bleibt nahezu symmetrisch.

Das stützt die Aussage, dass die neun Punkte der Gruppe A im vorhandenen Rechenmodell eine sensitive irreguläre Langzeitstruktur besitzen.

Es beweist jedoch noch nicht, dass diese Struktur nach korrekter Ereignisbehandlung erhalten bleibt.

### 4.1 Asymmetrische 40-s-Klassifikation

Die Punkte

- `(6,8)`,
- `(14,13)`,
- `(17,16)`

stehen ohne ihr jeweiliges Spiegelbild in der ursprünglichen 40-s-Liste.

Das zeigt unmittelbar, dass der alte Periodenklassifikator an diesen Stellen auf einer numerisch zu feinen Grenze gearbeitet hat. Eine harte Karte `P1/P2/P6/.../.` ist dort nicht belastbar.

---

## 5. Hauptproblem: Festschritt-RK4 über Umschaltflächen

Der verwendete Kontakt lautet sinngemäß:

`F_trial = -K z - C ż`

und wird auf null gesetzt, wenn

- `z >= 0`, oder
- `F_trial <= 0`.

Damit existieren zwei relevante Umschaltflächen:

1. Kontaktbeginn bei `z = 0`
2. Ablösung bei `F_trial = 0`

Der bisherige RK4-Schritt lokalisiert diese Ereignisse nicht. Seine Zwischenstufen können verschiedene Kontaktmodi mischen.

### 5.1 Kraftsprung beim Aufsetzen

Beim Eintritt aus der freien Bewegung mit `ż < 0` gilt unmittelbar hinter `z=0`:

`F_c ≈ C |ż|`

Bei beispielsweise

`C = 16 N·s/m`, `|ż| ≈ 0,5 m/s`

ergibt sich:

`F_c ≈ 8 N`.

Das liegt bereits über der statischen Gewichtskraft `Mg ≈ 6,38 N`.

Der Zustandsvektor bleibt kontinuierlich, die Beschleunigung bzw. rechte Seite der Differentialgleichung springt.

Ein klassischer RK4-Schritt über dieses Ereignis verliert damit seine nominelle glatte Fehlerordnung; die konkrete Kontaktzeit wird nur auf O(dt) getroffen und die Stufen können beide Seiten der Umschaltfläche vermischen.

### 5.2 Empirisches Warnsignal aus den Daten

Die starken Verschiebungen von `recur_frac` unter dt-Halbierung passen genau zu einem solchen Problem.

Besonders:

- `(6,8)`: +0,40
- `(11,17)`: +0,46
- `(17,11)`: +0,51
- `(2,13)/(13,2)`: ungefähr −0,25 bis −0,27

Dagegen bleiben die neun Punkte aus Gruppe A sowie `(0,13)/(13,0)` qualitativ wesentlich stabiler.

Diese Beobachtung rechtfertigt **nicht** die Behauptung, dass die instabilen Klassen reine Solverartefakte sind.

Sie rechtfertigt aber die strengere Aussage:

> Für Gruppe C und D ist die dynamische Klassifikation mit dem derzeitigen Integrator nicht konvergiert.

---

## 6. Falsifikations- und Konvergenzkriterium

Der nächste Solver muss die Bewegung zwischen Ereignissen glatt integrieren und die Umschaltzeitpunkte separat lokalisieren.

### 6.1 Minimalanforderung

- getrennte Modi „frei“ und „Kontakt“,
- Ereignisfunktion `z=0` für Kontaktbeginn,
- Ereignisfunktion `F_trial=0` für Ablösung,
- Bisektion oder ein vergleichbar robuster Root-Finder innerhalb eines Schritts,
- Integration exakt bis zum Ereignis,
- Neustart des Integrators im neuen Modus,
- kein RK4-Stufenmittel über die Umschaltfläche.

### 6.2 Konvergenzfolge

Mindestens:

- `dt`
- `dt/2`
- `dt/4`

bzw. entsprechende Toleranzfolgen bei adaptivem event-driven Solver.

### 6.3 Entscheidungsregel

Für die derzeit dt-abhängige Gruppe:

**Wenn**

`recur_frac → 1`

und

`recur_switches → 0`

mit Verfeinerung,

dann war die bisherige „Intermittenz“ bzw. Nichtperiodizität numerisch erzeugt oder numerisch verstärkt.

**Wenn dagegen**

`recur_frac < 1`

auf einen stabilen Wert konvergiert und die Schalterstatistik ebenfalls konvergiert,

dann gibt es Evidenz für eine reale intermittierende/aperiodische Struktur des definierten kontinuierlichen Modells.

Erst dann wird eine dynamische Klassifikation vergeben.

---

## 7. `(12,17)` – vorerst zurückstufen

Zusatzläufe aus der Arbeitssitzung zeigten zwei deutlich getrennte stroboskopische Zustandsgruppen.

Diese Daten waren jedoch nicht Teil der zwei 2400-s-CSVs und lagen in der ersten Notiz nicht als reproduzierbare Rohserie im Projektbestand vor.

Außerdem muss eine ältere Ergebnisnotiz zum Verhalten von `(12,17)` mit den neuen Zusatzläufen vollständig abgeglichen werden. Solange diese Quellenlage nicht vereinheitlicht ist, gilt:

> **Für `(12,17)` kein nachgewiesener Multistabilitätsbefund im kanonischen PCMMS-Datensatz.**

Die vorhandenen Zusatzläufe sind als Hypothesengenerator zu behandeln.

Das gilt nur für `(12,17)`. Bistabilität in den Satelliteninseln ist unabhängig davon belegt (§7a); kein Punkt des 19×19-Rasters liegt in einer dieser Inseln.

Nach dem Event-Solver folgt ein neuer Basin-Scan über `(z_0, ż_0)`.

### Begriffskorrektur

Werte wie

`meanv = -0,496 m/s`

bezeichnen in diesen Analysen den Mittelwert der stroboskopischen Probe `ż(nT)`.

Sie sind **kein** kontinuierlicher Geschwindigkeitsmittelwert und dürfen nicht als Netto-Drift des Körpers beschrieben werden.

---

## 7a. Bistabilität der Satelliteninseln (Nachtrag 28.09.2026)

**Quelle:** Prüfung zu PR #4 vom 25.09.2026 (`pcmms_pruefung_pr4_linearloeser.py` mit Ausgabe) und Gegenprobe vom 26.09.2026, Abschnitt F (`pcmms_gegenprobe_einzelmodul_2026-09-26.py`); beide im Repo unter `docs/arbeitspapier/gegenprobe_2026-09-26/`. Eingearbeitet in Arbeitspapier v2.4, Anhang B.6.

**Befund**

- Die liftoff-freie Menge des linearen Kontaktasts besteht im 1°-Raster aus zwei Hauptgebieten um (120°, 240°) und (240°, 120°) mit je 2524 Punkten (F_min bis 5,330 N) und aus sechs Satelliteninseln mit je 74 Punkten um (35°, 116°), (116°, 35°), (81°, 325°), (325°, 81°), (244°, 279°) und (279°, 244°), zusammen 0,34 % der Phasenebene (F_min bis 0,477 N).
- In den Inseln existiert ein Dauerkontaktorbit. Er ist exakte Lösung des gedämpften linearen Systems und damit lokal stabil.
- Der Start aus dem statischen Gleichgewicht erreicht ihn nicht: Bei (35°, 116°) liefert der Standardstart λ = 75,82 %, der Start auf dem Kontaktorbit λ = 0,00 %; bei (28°, 115°) sind es 75,80 % bzw. 0,00 % (Festschritt-RK4).
- In den Hauptgebieten kehrten Stichproben mit Anfangsgeschwindigkeit 3 m/s bei (98°, 240°) und (148°, 240°) in den Dauerkontakt zurück (λ = 0,00 %).
- Kein Punkt des 19×19-Rasters liegt in einer Insel: Die zwölf Rasterpunkte mit Kontaktorbit sind genau die zwölf liftoff-freien Punkte der CSV.

**Einordnung**

- Bistabilität zwischen Dauerkontakt und Springen ist damit numerisch belegt, als zustandsabhängige Astwahl an festen Phasen. Eine Aussage über Grazing-Bifurkationen oder Chaos folgt daraus nicht.
- Der Dauerkontaktast ist exakt, der springende Zustand beruht auf dem Festschritt-RK4. Seine Existenz ist mit dem Ereignis-Solver zu bestätigen (§13, Schritt 1). Fände der Ereignis-Solver vom Standardstart in den Dauerkontakt, wäre der springende Zustand ein Integrationsartefakt.
- Der Befund betrifft weder die grenznahen Punkte der 2400-s-Läufe noch `(12,17)` (§7).
- Das Anfahrprotokoll ist damit eine Kontrollvariable (§12).

---

## 8. `(9,9)` – Lyapunov-Aussage vorerst zurückstufen

Zusätzliche Sitzungsdaten zeigten eine rasche Trennung zweier minimal gestörter Trajektorien.

Der frühere Fit von ungefähr

- 0,53 pro Zyklus bei dt
- 0,46 pro Zyklus bei dt/2

ist jedoch:

1. nicht Bestandteil der beiden primären CSVs,
2. nicht vollständig zeitschrittkonvergiert,
3. kein Benettin-Test,
4. bei einem nichtglatten System ohne korrekte Übergangslinearisation ohnehin nur eingeschränkt interpretierbar.

Daher ist die zulässige Formulierung vorerst:

> `(9,9)` gehört zur dt-robusten irregulären Gruppe und ist ein sinnvoller Kandidat für eine spätere Chaosdiagnostik.

Nicht zulässig ist derzeit:

> „starker Chaos-Kandidat aufgrund eines Lyapunov-Werts von 0,5 pro Zyklus“.

Ein formaler Test folgt erst nach Solvervalidierung.

---

## 9. Literaturrahmen: Impact Oscillator / Grazing

Die beobachtete Problemklasse ist in der nichtlinearen Dynamik gut etabliert.

Ein periodisch erregter Freiheitsgrad mit unilateralem Kontakt gehört in die Familie der **piecewise-smooth / vibro-impact / impact oscillator**-Systeme.

Dort sind unter anderem bekannt:

- harmonische und subharmonische Zustände,
- koexistierende Attraktoren,
- sensitive Dynamik,
- Periodenübergänge,
- Grazing-Bifurkationen,
- aperiodische und chaotische Bewegungen.

Das ist kein Neuheitsargument für PCMMS. Es ist der notwendige theoretische Anschluss für die numerische Phasenkarte.

### 9.1 Verifizierte Primär- und Grundlagenliteratur

1. **P. J. Holmes (1982)**  
   *The dynamics of repeated impacts with a sinusoidally vibrating table.*  
   Journal of Sound and Vibration 84(2), 173–189.  
   DOI: `10.1016/S0022-460X(82)80002-3`

2. **S. W. Shaw, P. J. Holmes (1983)**  
   *A periodically forced piecewise linear oscillator.*  
   Journal of Sound and Vibration 90(1), 129–155.  
   DOI: `10.1016/0022-460X(83)90407-8`

3. **A. B. Nordmark (1991)**  
   *Non-periodic motion caused by grazing incidence in an impact oscillator.*  
   Journal of Sound and Vibration 145(2), 279–297.  
   DOI: `10.1016/0022-460X(91)90592-8`

4. **J. M. Luck, A. Mehta (1993)**  
   *Bouncing ball with a finite restitution: Chattering, locking, and chaos.*  
   Physical Review E 48, 3988–3997.  
   DOI: `10.1103/PhysRevE.48.3988`

5. **P. C. Müller (1995)**  
   *Calculation of Lyapunov exponents for dynamic systems with discontinuities.*  
   Chaos, Solitons & Fractals 5(9), 1671–1681.  
   DOI: `10.1016/0960-0779(94)00170-U`

6. **K. H. Hunt, F. R. E. Crossley (1975)**  
   *Coefficient of Restitution Interpreted as Damping in Vibroimpact.*  
   Journal of Applied Mechanics 42(2), 440–445.  
   DOI: `10.1115/1.3423596`

### 9.2 Besonders passende Ergänzungen für weichen Kontakt

7. **J. de Weger, W. van de Water, J. Molenaar (2000)**  
   *Grazing impact oscillations.*  
   Physical Review E 62, 2030.  
   DOI: `10.1103/PhysRevE.62.2030`

   Relevant, weil dort Grazing-Mappings sowohl für instantane Stöße als auch für weiche Kollisionen mit nachgiebiger Wand betrachtet werden.

8. **Grazing-induced bifurcations in impact oscillators with elastic and rigid constraints (2017)**  
   International Journal of Mechanical Sciences 127, 204–214.  
   DOI: `10.1016/j.ijmecsci.2017.02.001`

   Relevant für die Unterscheidung zwischen starrem Anschlag und elastischem einseitigem Kontakt.

### 9.3 Vorsicht bei der PCMMS-Zuordnung

Die Liftoff-/Kontaktgrenze des PCMMS-Modells ist **grazing-verwandt** und sollte gegen diese Literatur analysiert werden.

Aber:

> `R_c` ist noch nicht formal als Nordmark-Grazing-Bifurkation des PCMMS-Modells nachgewiesen.

Dafür braucht es eine lokale Fortsetzungs-/Poincaré-Analyse der PCMMS-Grenze.

---

## 10. Kontaktgesetz als eigener Modellunsicherheitsfaktor

Das aktuelle Modell verwendet einen einseitig beschnittenen Kelvin-Voigt-Term.

Hunt & Crossley zeigen bereits grundsätzlich, warum ein einfaches linear-viskoses Kelvin-Voigt-Gesetz für Stoßkontakt problematisch sein kann; ihr Kraftgesetz lässt die Kontaktkraft mit der Eindringtiefe gegen null gehen und vermeidet damit insbesondere den unmittelbaren Dämpfungskraftsprung bei `x=0`.

Für PCMMS folgt daraus nicht, dass Hunt-Crossley automatisch das richtige Gesetz ist.

Es folgt:

> Die Regimestruktur muss nach Solvervalidierung auch gegen mindestens ein alternatives kontinuierliches Kontaktgesetz geprüft werden.

Damit können Solverartefakt und Kontaktmodellabhängigkeit getrennt werden.

---

## 11. Korrektur des Randterm-Themas im Arbeitspapier v2.2

Die Größenordnung `T^-0,945` sollte nicht einfach gelöscht werden.

Zu korrigieren ist ihre frühere **Deutung**.

Für den untersuchten Hotspot gilt die Bilanz:

`δ(T) = M·Δż / (Mg·T) + Q`

also:

- ein Randterm, der ungefähr wie `1/T` fällt,
- plus ein nahezu konstanter Quadraturbeitrag `Q`.

Zu entfernen oder umzuschreiben sind daher:

- „langsame Modulation“ als Erklärung,
- „sämtliche 361 Residuen negativ“,
- `0,68 %` als allgemeiner Genauigkeitswert der eingeschwungenen Auswertung,
- eine Darstellung von `T^-0,945` als eigenständiges dynamisches Skalengesetz.

Der Zahlenverlauf bleibt als historischer/numerischer Befund dokumentierbar, aber seine Ursache ist neu zu beschreiben.

**Stand 28.09.2026:** umgesetzt in Arbeitspapier v2.3 (25.09.2026) und in v2.4 übernommen.

---

## 12. Konsequenzen für Labor und Kennzahlen

In den Satelliteninseln ist Bistabilität numerisch belegt (§7a). Das **Anfahrprotokoll** ist damit eine experimentelle Kontrollvariable: An derselben Phasenkonfiguration entscheidet der Anfangszustand zwischen Dauerkontakt und rund 76 % Liftoff.

Es reicht deshalb nicht, nur `(φ2,φ3)` anzugeben.

Zu protokollieren wären zusätzlich:

- Startzustand,
- Rampe bzw. Phasenpfad zum Zielzustand,
- Einschwingdauer,
- Richtung einer Parameterfahrt.

### 12.1 Billiger experimenteller Test

Ein sinnvoller späterer Test wäre eine Hysteresefahrt:

1. Phase schrittweise in eine Richtung rampen,
2. Zielgrößen erfassen,
3. denselben Bereich rückwärts durchfahren,
4. Wellenformstatistiken vergleichen.

Ein reproduzierbarer pfadabhängiger Unterschied wäre ein direkter Hinweis auf mehrere stabile Regime oder Hysterese.

### 12.2 Kennzahlen in komplexen Bereichen

Falls mehrere Äste oder nichtstationäre Fenster bestätigt werden, dürfen

- `γ1`,
- `λ`,
- `N_min`,
- `N_max`,
- `A`

nicht als ein einziger Wert pro Phasenpunkt behandelt werden.

Dann sind sie entweder:

- **je Attraktionsast**, oder
- als **Fensterverteilung / Ensemble**

anzugeben.

---

## 13. Verbindliche Reihenfolge ab diesem Stand

### Schritt 1 — Ereignis-Solver

Implementieren und gegen den bisherigen Solver testen. Exakte Referenz ist der lineare Dauerkontaktast (`code/linear_solver.py`): An Punkten mit Dauerkontakt muss der Ereignis-Solver die lineare Lösung reproduzieren. In der Insel bei (35°, 116°) ist zu prüfen, ob beide Zustände je nach Start erhalten bleiben.

### Schritt 2 — Konvergenz der 23 Punkte

Mindestens Event-Solver mit äquivalenten Auflösungen `dt`, `dt/2`, `dt/4` bzw. Toleranzfolge.

Ausgabe:

- `recur_frac`
- `recur_switches`
- bestes `k`
- Wiederkehrfehler
- `meanv`, `sdv`
- Kontaktzahl / Ereigniszahl
- Bilanzfehler

### Schritt 3 — Klassifikation erst danach

Die vier Gruppen werden neu bestimmt.

### Schritt 4 — Basin-Scan `(12,17)`

Erst wenn das Regime solverkonvergiert. Zusätzlich ein Basin-Scan in der Insel bei (35°, 116°) als Fall mit bekanntem Dauerkontaktorbit.

### Schritt 5 — Lyapunov/Poincaré `(9,9)`

Benettin-artige Renormalisierung auf der stroboskopischen Abbildung; bei nichtglatten Übergängen muss die linearisierte Ereignisbehandlung bzw. Saltation/Transition berücksichtigt werden.

### Schritt 6 — Kontaktgesetz-Robustheit

Mindestens Vergleich des aktuellen clipped Kelvin-Voigt-Modells mit einem glatter ansetzenden Kontaktgesetz.

---

## 14. Aktuell zulässige Gesamtaussage

Der belastbare Befund lautet vorerst:

> Der bestehende PCMMS-Festschritt-Solver erzeugt im 19×19-Phasenraum unterschiedliche langfristige Wiederkehrregime. Neun der 23 ursprünglich auffälligen Punkte bleiben bei Zeitschritthalbierung robust stark irregulär, zwei weitere zeigen eine robuste intermittierende Wiederkehrstatistik. Zwölf Punkte reagieren dagegen so stark auf die Zeitschrittänderung bzw. auf die Periodentoleranz, dass ihre dynamische Klassifikation derzeit nicht belastbar ist. Vor einer physikalischen Interpretation dieser Regimestruktur muss die unilaterale Kontaktumschaltung ereignislokalisiert und numerisch konvergiert werden.

Hinzu kommt (§7a): In sechs Satelliteninseln der Phasenebene koexistieren Dauerkontakt und Springen; welcher Zustand sich einstellt, hängt vom Anfangszustand ab. Kein Punkt des 19×19-Rasters liegt in einer Insel.

Das ist weniger spektakulär als die v1-Formulierung, aber wissenschaftlich deutlich stärker.

---

## 15. Status

**Stand:** 28.09.2026  
**Nächster Prüfstein:** Ereignislokalisierter Kontakt-Solver.  
**Keine Messdaten. Kein Chaosnachweis. Bistabilität in den Satelliteninseln numerisch belegt (§7a); für die grenznahen Punkte der 2400-s-Läufe kein gesicherter Multistabilitätsnachweis.**

---

## Änderungsvermerk v1.1 → v1.2 (28.09.2026)

1. Kopf: Version, Stand, Ersetzt-Vermerk.
2. §0: Absatz zur Bistabilität der Satelliteninseln; Reihenfolge, Punkt 1, um die lineare Referenz ergänzt.
3. §7: „Kein nachgewiesener Multistabilitätsbefund“ auf `(12,17)` beschränkt, Verweis auf §7a.
4. §7a neu: Bistabilität der Satelliteninseln mit Quelle, Befund und Einordnung.
5. §11: Umsetzungsvermerk (Arbeitspapier v2.3, übernommen in v2.4).
6. §12: Anfahrprotokoll als Kontrollvariable, nicht mehr bedingt formuliert.
7. §13: Schritt 1 mit exakter Referenz und Inseltest, Schritt 4 um Basin-Scan in der Insel ergänzt.
8. §14 und §15: Gesamtaussage und Status angepasst.

Unverändert: Datengrundlage, Gruppen A–D, Tabellen, §4–6, §8–10.
