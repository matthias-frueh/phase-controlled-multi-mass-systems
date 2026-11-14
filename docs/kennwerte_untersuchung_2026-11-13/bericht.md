# Untersuchung: Kennwerte für den Wertevergleich mit Toleranz

**PCMMS — Phasenkontrollierte Mehrmassensysteme**\
Matthias Früh · Unabhängiger Forscher · ORCID [0009-0005-9984-4207](https://orcid.org/0009-0005-9984-4207)\
Stand: 14. November 2026 · Messreihe vom 13. und 14.11.2026 · Grundlage: `main` = `8429b3c` (nach Pull Request #40)
mit den Änderungen von PR C

**Status:** Softwareuntersuchung zu PR C (Entscheidung E-4 der
[Notiz vom 12.11.2026](../entscheidungsnotiz_herkunft_phase0_2026-11-12.md)). Alles im Repository ist Simulation
oder Analytik; Messdaten existieren nicht. Jede Zahl dieses Berichts steht in einer der Ergebnisdateien dieses
Verzeichnisses ([`streuung.json`](streuung.json), [`abdeckung.json`](abdeckung.json), [`zusatz.json`](zusatz.json))
oder ist dort genannt, wo sie steht.

## 1 Frage und Ergebnis

**Frage.** Prüfsummen über berechnete Gleitkommafelder gelten nur für einen Rechner. Reichen wenige Kennwerte je
Feld, verglichen mit einer Toleranz, um die Werte zu prüfen, oder braucht es die vollen Bezugsfelder?

**Ergebnis.**

1. Zwischen zehn Rechenumgebungen sind alle exakten Inhalte der drei Prüfsätze gleich (Katalog, Laufköpfe,
   Skelett der P0-Messung, Entscheidungen, Ziehungen, Schwellen, Gegenprobe). Die berechneten Felder unterscheiden
   sich im Rundungsrauschen: je Eintrag höchstens 6,5·10⁻¹⁴ des größten Betrags M seines Feldes.
2. Die Abweichung eines Eintrags richtet sich nach der Größe des Feldes, nicht nach der des Eintrags. Bezogen auf
   den Eintrag selbst reicht sie bis 100 % (Einträge nahe null). Eine Toleranz relativ zum einzelnen Eintrag wäre
   deshalb falsch; die Toleranz der Kennwerte bezieht sich auf M.
3. Kennwerte je Feld (Summe, Quadratsumme, zwei stellengewichtete Summen, Minimum, Maximum; exakte Felder als
   Prüfsumme) mit der Toleranz τ = 10⁻¹⁰·M + 10⁻¹² je Eintrag schlagen in keiner der Umgebungen an. Die Toleranz
   ist dabei höchstens zu 0,054 % ausgeschöpft (Abstand Faktor 1800).
4. Abdeckung: Die Kennwerte erkennen jede geprüfte systematische Änderung, Vertauschungen und Verschiebungen
   praktisch so gut wie ein Vergleich Eintrag für Eintrag. Die Änderung eines **einzelnen** Eintrags erkennen sie
   nur oberhalb von n·τ, in den vier großen Harmonischen-Feldern also deutlich schlechter (Abschnitt 5).
5. Die vollen Bezugsfelder der drei Prüfsätze wären 86,8 MB groß (komprimiert 66,0 MB), die Kennwerte 0,22 MB.
6. Umgesetzt sind deshalb Kennwerte je Feld. Die Grenze beim einzelnen Eintrag ist benannt und durch einen Test
   festgehalten; eine feinere Unterteilung der großen Felder ist möglich und Sache des Autors (Abschnitt 9).

## 2 Umgebungen

Ein Rechner (Intel Xeon mit AVX-512, zwei Kerne), Python 3.13.18, NumPy 2.5.4, SciPy 1.18.1, zlib 1.3. Verändert
wurden der Rechenkern von OpenBLAS (`OPENBLAS_CORETYPE`), die Zahl der BLAS-Threads und die Rechenwege von NumPy.

| Umgebung | Rechenkern (wirksam) | Threads | NumPy mit AVX-512 |
|---|---|---|---|
| SkylakeX_1 (Bezug) | SkylakeX | 1 | ja |
| SkylakeX_4 | SkylakeX | 4 | ja |
| Haswell_1, Haswell_2, Haswell_4 | Haswell | 1, 2, 4 | ja |
| Haswell_1_NumPy-AVX2, Haswell_4_NumPy-AVX2 | Haswell | 1, 4 | nein |
| Sandybridge_1 | Sandybridge | 1 | ja |
| Nehalem_1 | Nehalem | 1 | ja |
| Katmai_1 | Katmai | 1 | ja |

- **Wirksamer Rechenkern.** Die Tabelle nennt den Kern, den OpenBLAS tatsächlich lädt (ausgelesen mit
  `threadpoolctl`). In den OpenBLAS-Fassungen von NumPy 2.5.4 und SciPy 1.18.1 führt die Vorgabe `ZEN` zum Kern
  Haswell und die Vorgabe `PRESCOTT` zum Kern Katmai. Sechs Vorgaben (SkylakeX, HASWELL, ZEN, SANDYBRIDGE, NEHALEM,
  PRESCOTT) ergeben also fünf Rechenkerne.
- **Threads.** Vier Threads sind zur Laufzeit gesetzt (`threadpoolctl`); über die Umgebungsvariable begrenzt
  OpenBLAS auf die zwei Kerne des Rechners. Die Bedingung, unter der der Test der Prozesszahl auf GitHub fehlschlug
  (Kern Haswell, vier Threads im eigenen Prozess), ist damit nachgestellt.
- **NumPy ohne AVX-512.** `NPY_DISABLE_CPU_FEATURES=X86_V4,AVX512_ICL,AVX512_SPR` lässt NumPy die Rechenwege eines
  Prozessors ohne AVX-512 nehmen. Zusammen mit dem Kern Haswell und vier Threads ist das die nächste Nachstellung
  eines GitHub-Runners ohne AVX-512, die auf diesem Rechner möglich ist.
- **Nicht geprüft:** andere Betriebssysteme, ARM-Prozessoren, andere BLAS-Bibliotheken (MKL, Accelerate).

## 3 Streuung zwischen den Umgebungen

Gegenstand: die Felder der drei Prüfsätze (Laufzusammenfassungen und P0-Messung der sieben Prüfkampagnen, Tabellen
der zehn Ablauf-Prüfkampagnen; 24 Prüfsummen über berechnete Felder) und die Kurzbefunde dreier Kampagnen wie in
`test_kampagnen_unabhaengig_von_der_prozesszahl`. Alle Angaben gegen SkylakeX_1 (`streuung.json`).

| Umgebung | exakte Teile abweichend | Prüfsummen abweichend | Felder: größte δ/M | Kennwerte: Auslastung | Befunde: exakte Inhalte | Befunde: größte δ/M |
|---|---|---|---|---|---|---|
| SkylakeX_4 | 0 | 0 von 24 | 0 | 0 | gleich | 0 |
| Haswell_1, _2, _4 | 0 | 17 von 24 | 4,9·10⁻¹⁴ | 2,8·10⁻⁶ | gleich | 1,0·10⁻¹⁰ |
| Haswell_1 und _4 mit NumPy-AVX2 | 0 | 17 von 24 | 4,9·10⁻¹⁴ | 2,8·10⁻⁶ | gleich | 1,0·10⁻¹⁰ |
| Sandybridge_1 | 0 | 18 von 24 | 6,5·10⁻¹⁴ | 5,4·10⁻⁴ | gleich | 1,3·10⁻¹⁰ |
| Nehalem_1 | 0 | 18 von 24 | 6,5·10⁻¹⁴ | 5,4·10⁻⁴ | gleich | 1,5·10⁻¹⁰ |
| Katmai_1 | 0 | 18 von 24 | 6,5·10⁻¹⁴ | 5,4·10⁻⁴ | gleich | 5,6·10⁻¹¹ |

δ ist die Abweichung eines Eintrags, M der größte Betrag seines Feldes. „Auslastung“ ist die größte Abweichung eines
Kennwerts geteilt durch seine Toleranz; 1 wäre die Grenze.

- **Exakte Inhalte hängen nicht an der Umgebung.** Das gilt auch für Größen, die Gleitkommazahlen enthalten
  (Laufköpfe mit `f_mittel`, Skelett der P0-Messung, gerundete Schwellen).
- **Die hinterlegten Prüfsummen kehren nur mit dem Kern SkylakeX wieder.** Die Rundung auf 12 Nachkommastellen vor
  dem Hashen verhindert das nicht.
- **Die größte Abweichung der Felder** liegt in der Kohärenz der P0.4-Messung (Werte nahe 1); in den
  Laufzusammenfassungen und Ablauf-Tabellen bleibt δ/M unter 10⁻¹⁵ (`delta_M_ohne_p0`: bis 7,5·10⁻¹⁶).
- **Bezogen auf den Eintrag selbst** reicht die Abweichung bis 100 % (`delta_x` in `streuung.json`): Einträge nahe
  null tragen dasselbe absolute Rauschen wie große.
- **Auch die Rechenwege von NumPy ändern Werte.** Mit dem Kern Haswell unterscheiden sich die Felder mit und ohne
  AVX-512 in NumPy (andere Prüfsummen der Datenfelder, Abschnitt 7), aber in derselben Größenordnung.
- **Befunde der Auswertung streuen stärker als die Datenfelder:** zwischen Rechenkernen bis 1,5·10⁻¹⁰·M (größte
  Abweichung in den E3-Größen, `E3.e3a`). Mit der Toleranz der Datenfelder wäre ein Vergleich von Befunden zwischen
  Rechenkernen zu 41 % bis 109 % ausgeschöpft. Die Toleranz dieses Moduls ist für Datenfelder gewählt; ein Vergleich
  von Ergebnissen zwischen Rechnern braucht eine eigene, größere Toleranz (Abschnitt 9).

## 4 Kennwerte und Toleranz

Die Definition steht im Kopf von [`kennwerte.py`](../../code/pcmms_auswertung/kennwerte.py). Kurz:

- je Gleitkommafeld: Zahl der Einträge, Summe, Quadratsumme, zwei gewichtete Summen mit festen, von der Stelle
  abhängigen Gewichten, Minimum, Maximum, Zahl und Muster der nicht endlichen Einträge;
- Felder mit ganzen Zahlen oder Wahrheitswerten: SHA-256 ihrer Werte (exakt);
- die Summen sind exakt gerundet (`math.fsum`), die Gewichte entstehen aus ganzen Zahlen: Gleiche Felder ergeben
  auf jedem Rechner dieselben Kennwerte;
- Toleranz je Eintrag τ = rtol·M + atol mit rtol = 10⁻¹⁰ und atol = 10⁻¹²; daraus n·τ für die Summen,
  (2·M + τ)·n·τ für die Quadratsumme und τ für die Extremwerte.

Diese Toleranzen sind so gewählt, dass der Vergleich nie anschlägt, wenn jeder Eintrag innerhalb von τ liegt: Die
Gewichte liegen zwischen 0 und 1, also weicht jede der Summen höchstens um die Summe der Einzelabweichungen ab. Das
ist geprüft: 6800 Versuche mit Rauschen bis 0,5·τ und bis 0,99·τ je Eintrag, kein Alarm (`abdeckung.json`); dazu
`test_kein_alarm_solange_jeder_eintrag_innerhalb_der_toleranz_liegt` mit gleichgerichteten Abweichungen.

**Wahl von rtol.** Gemessen ist δ/M ≤ 6,5·10⁻¹⁴. rtol = 10⁻¹⁰ liegt um den Faktor 1500 darüber; die Kennwerte sind
zu höchstens 5,4·10⁻⁴ ausgeschöpft. Der Abstand ist bewusst groß, weil nur ein Rechner und nur OpenBLAS auf x86-64
gemessen sind. atol = 10⁻¹² (N, °, s) entspricht der bisherigen Rundung der Prüfsätze auf 12 Stellen und fängt
Felder ab, deren Werte nur Rundungsrauschen um null sind.

## 5 Abdeckung

Die Gleitkommafelder der Laufzusammenfassungen zweier Prüfkampagnen (A04-R4 und I01-amplitude, 34 Felder) wurden
gezielt verändert. Gezählt ist, wie oft der Vergleich der Kennwerte anschlägt und wie oft ein Vergleich Eintrag für
Eintrag mit derselben Toleranz je Eintrag (`abdeckung.json`; zufällige Stellen mit festem Seed, 100 je Feld).

| Veränderung | Versuche | Kennwerte | Eintrag für Eintrag |
|---|---|---|---|
| Rauschen bis 0,5·τ und bis 0,99·τ je Eintrag (darf nicht anschlagen) | 6800 | 0 | 0 |
| alle Einträge relativ um 10⁻⁹ größer | 34 | 34 | 34 |
| alle Einträge relativ um 10⁻¹⁰ größer (innerhalb der Toleranz) | 34 | 0 | 0 |
| alle Einträge um 2·τ verschoben | 34 | 34 | 34 |
| alle Läufe um einen Platz verschoben | 34 | 34 | 34 |
| Imaginärteil mit anderem Vorzeichen (komplexe Felder) | 10 | 10 | 10 |
| ein Eintrag fehlt (NaN) | 3400 | 3400 | 3400 |
| Werte eines Laufs durch die eines anderen ersetzt | 3400 | 3352 | 3352 |
| Werte zweier Läufe vertauscht | 3400 | 3349 | 3352 |
| zwei Einträge vertauscht | 3400 | 3245 | 3300 |
| ein Eintrag um 10⁻³·M verschoben | 3400 | 3400 | 3400 |
| ein Eintrag um 10⁻⁵·M verschoben | 3400 | 2743 | 3400 |
| ein Eintrag um 10⁻⁷·M verschoben | 3400 | 283 | 3400 |
| ein Eintrag relativ um 10⁻² geändert | 3400 | 2945 | 3400 |
| ein Eintrag relativ um 10⁻⁴ geändert | 3400 | 2777 | 3397 |
| ein Eintrag relativ um 10⁻⁶ geändert | 3400 | 2480 | 3236 |

- **Systematische Änderungen, Verschiebungen, fehlende Werte:** vollständig erkannt.
- **Vertauschte oder ersetzte Läufe:** so gut wie Eintrag für Eintrag (die übrigen Fälle sind Läufe mit gleichen
  Werten, die kein Vergleich unterscheidet). Bei zwei vertauschten Einträgen fehlen den Kennwerten 55 von 3300.
- **Ein einzelner Eintrag:** Die Kennwerte erkennen ihn sicher erst oberhalb von n·τ. In den 13 kleineren Feldern
  je Kampagne (n von 811 bis 8712) ist das kein Verlust: eine relative Änderung um 10⁻² wird dort in allen 2600
  Versuchen erkannt. In den vier großen Harmonischen-Feldern (`Nk_summe`, `Nk_zellen`, `fuenftel_Nk`, `zeiger`;
  n von 97 320 bis 361 080, n·τ bis 3,6·10⁻⁵·M) sind die meisten Einträge kleine Harmonische; dort werden von 800
  Versuchen mit 10⁻² relativ nur 345 erkannt (`je_feld` in `abdeckung.json`).

**Bewertung.** Die Prüfsätze sollen ungewollte Änderungen der Software erkennen. Eine Codeänderung wirkt auf ganze
Felder oder ganze Läufe (andere Formel, andere Reihenfolge, andere Ziehung, anderer Sonderfall) und fällt damit unter
die vollständig oder fast vollständig erkannten Fälle. Dass sich genau ein Eintrag eines großen Feldes um weniger
als n·τ ändert und sonst nichts, ist als Folge einer Codeänderung nicht zu erwarten, aber nicht ausgeschlossen. Der
Test `test_grenze_ein_einzelner_eintrag_unterhalb_von_n_tau_bleibt_unerkannt` hält diese Grenze fest.

**Volle Bezugsfelder.** Ein Vergleich Eintrag für Eintrag gegen einen hinterlegten Stand bräuchte die Felder der
drei Prüfsätze: 86,8 MB, als komprimierte NPZ-Dateien 66,0 MB (Laufzusammenfassungen 41,3 MB, P0-Messungen 12,7 MB,
Ablauf-Tabellen 12,0 MB; `groesse_bezugsfelder_byte` in `streuung.json`). Die Kennwerte-Dateien haben zusammen
0,22 MB. Für zwei Rechnungen im selben Lauf braucht es keine hinterlegten Felder; dort vergleicht
`kennwerte.vergleich_objekt` Eintrag für Eintrag.

## 6 Thread-Zahl

Dieselben drei Kampagnen im eigenen Prozess, bei gleichem Rechenkern mit verschiedener Thread-Zahl
(`befunde_gleicher_kern_andere_threadzahl` in `streuung.json`):

| Vergleich | Prüfsummen der Befunde | exakte Inhalte | größte δ/M | Auslastung |
|---|---|---|---|---|
| SkylakeX: 1 gegen 4 Threads | gleich | gleich | 0 | 0 |
| Haswell: 1 gegen 2 Threads | gleich | gleich | 0 | 0 |
| Haswell: 1 gegen 4 Threads | verschieden | gleich | 9,8·10⁻¹⁵ | 9,8·10⁻⁵ |
| Haswell mit NumPy-AVX2: 1 gegen 4 Threads | verschieden | gleich | 9,8·10⁻¹⁵ | 9,8·10⁻⁵ |

Mit dem Kern Haswell und vier Threads ändern sich Zahlenfelder der Befunde im Rundungsrauschen (größte Abweichung im
Feld `felder.nu0` des Kurzbefunds); Entscheidungen, Gründe und Zählgrößen bleiben gleich. Der bisherige Test verglich
Prüfsummen und schlug deshalb fehl. Abnahmekriterium seit dem 14.11.2026 (Kopf von
[`harness/kampagnen.py`](../../code/pcmms_auswertung/harness/kampagnen.py), Test
`test_kampagnen_unabhaengig_von_der_prozesszahl`): exakte Inhalte gleich, Zahlenfelder innerhalb der Toleranz. Die Rechnung selbst ist unverändert; bitgleich zwischen
den Prozesszahlen ist sie nur, wenn auch der eigene Prozess mit einem BLAS-Thread rechnet.

## 7 Zusatzmessungen: kleine Kampagne, Ebene Z, Strukturgenerator

Sechs Umgebungen mit je einem Thread (`zusatz.json`), gegen SkylakeX_1.

| Gegenstand | Herkunftsnachweis | Prüfsumme der Datenfelder | Kennwerte: Auslastung |
|---|---|---|---|
| Ebene H, N01-V1G0, Seed 7 (162 Phase-0-Läufe) | in allen sechs gleich (`d86333f3ed60`) | fünf verschiedene Werte | 2,2·10⁻⁶ |
| Ebene Z, N01-A4, Seed 13 (56 Rohdateien → Stufe 1) | in allen sechs verschieden | fünf verschiedene Werte | bis 7,0·10⁻⁶ |
| Strukturgenerator, Struktur aus P0.8 (N01-A4, Seed 5) | Modellprüfsumme: fünf verschiedene Werte | – | Struktur 2,1·10⁻⁶ |

- **Ebene H.** Der Nachweis hängt nicht an der Umgebung, die alte Bindung (Prüfsumme der Datenfelder) schon; die
  Kennwerte stimmen innerhalb der Toleranz überein. Sandybridge und Nehalem ergeben dieselbe Prüfsumme der
  Datenfelder.
- **Ebene Z.** Hier werden Rohdateien und Kalibrierung in jeder Umgebung neu erzeugt; `hash_rohdatei` und
  `kalibrier_hash` sind dann andere. Das ist die in der Notiz vom 12.11.2026 (Abschnitt 4) genannte Grenze: Der
  Nachweis gilt für gespeicherte Dateien. Die Werte nach Stufe 1 stimmen innerhalb der Toleranz überein.
- **Strukturgenerator (Prüfpunkt B vom 13.11.2026).** Das Modell stammt aus geschätzten Größen: Struktur aus P0.8
  und Rauschparameter aus den Laufgrößen. Seine Prüfsumme im Generatornachweis hängt deshalb am Rechenkern, und
  zwar nicht nur über die Prüfsumme der Strukturfelder, sondern auch über die Rauschparameter. Innerhalb eines
  Rechenlaufs ist sie stabil, auch über die Prozessgrenze zu den Arbeitsprozessen (`ueber_prozessgrenze_gleich`).
  Eine auf einem anderen Rechner neu erzeugte Tabelle weist Teil B zurück; angenommen wird nichts stillschweigend.
  Für die Planungssimulation, die in einem Rechenlauf erzeugt und auswertet, reicht das. Der Test
  `test_modellpruefsumme_des_strukturgenerators_gilt_innerhalb_eines_rechenlaufs` hält es fest.

## 8 Was daraus umgesetzt ist (PR C)

- [`kennwerte.py`](../../code/pcmms_auswertung/kennwerte.py): Kennwerte, Vergleich mit Toleranz, Vergleich
  vollständiger Objekte.
- **Phase 0 ↔ Teil B** (`pilot-0.6`, `teil_b-0.6`, nur Regelstand 2026-11): Die Pilotausgabe führt je Satz die
  Kennwerte der Phase-0-Datenfelder neben der Bindung; Teil B vergleicht sie mit denen der übergebenen Läufe und
  bricht bei einer Abweichung außerhalb der Toleranz ab. Die Bindung über den Herkunftsnachweis bleibt exakt.
- **Prüfsätze:** exakte Teile exakt, berechnete Felder über Kennwerte. Die Bezugswerte stehen in eigenen Dateien
  (`tests/fixtures/*_kennwerte.json`), erzeugt in einer Rechnung, die die hinterlegten Prüfsummen bitgleich
  wiedergab (Kern SkylakeX, zlib 1.3). Die Prüfsatz-Dateien sind unverändert. Mit `PCMMS_BITGLEICH=1` verlangen die
  Tests zusätzlich die bitgleiche Wiederkehr der Prüfsummen.
- **Kampagnen des Harness:** Abnahmekriterium der Unabhängigkeit von Prozess- und Thread-Zahl (Abschnitt 6).
- **CI:** keine Festlegung von Rechenkern und Thread-Zahl mehr, kein abgewählter Test.

## 9 Offen und Sache des Autors

1. **Feinere Kennwerte für die großen Felder.** Kennwerte je Harmonischer statt je Feld würden die Lücke beim
   einzelnen Eintrag weitgehend schließen, die Kennwerte-Dateien aber um ein Mehrfaches vergrößern. Nicht umgesetzt.
2. **Engere Toleranz.** Mit rtol = 10⁻¹² wäre die Toleranz in den gemessenen Umgebungen zu höchstens 2,8 %
   ausgeschöpft (`auslastung_rtol_1e_12` in `streuung.json`) und die Schwelle beim einzelnen Eintrag bis zu
   hundertmal kleiner. Der Abstand zu nicht gemessenen
   Rechnern (ARM, andere BLAS) wäre entsprechend geringer. Nicht umgesetzt.
3. **Toleranz für Ergebnisse.** Befunde der Auswertung streuen zwischen Rechenkernen bis 1,5·10⁻¹⁰·M. Für einen
   Vergleich von Ergebnissen zwischen Rechnern (Referenzstand, AP-14) ist eine eigene Toleranz festzulegen; die der
   Datenfelder reicht dafür nicht.
4. **Thread-Zahl im eigenen Prozess.** Bitgleichheit zwischen Prozesszahlen ließe sich erzwingen, indem der eigene
   Prozess die BLAS-Bibliothek auf einen Thread begrenzt. Das braucht eine neue Abhängigkeit (`threadpoolctl`) und
   beseitigt die Abhängigkeit vom Rechenkern nicht. Nicht umgesetzt.

## 10 Nachrechnen

Aus dem Wurzelverzeichnis des Repositorys; die Ablagen (je Umgebung rund 90 MB) liegen nicht im Repository.

```bash
# je Umgebung einmal; optional als zweites Argument die Thread-Zahl zur Laufzeit (braucht threadpoolctl)
OPENBLAS_CORETYPE=HASWELL OPENBLAS_NUM_THREADS=1 \
  python3 docs/kennwerte_untersuchung_2026-11-13/messen.py /tmp/kennwerte/Haswell_1.pkl
python3 docs/kennwerte_untersuchung_2026-11-13/auswerten.py /tmp/kennwerte SkylakeX_1      # → streuung.json
python3 docs/kennwerte_untersuchung_2026-11-13/abdeckung.py /tmp/kennwerte/SkylakeX_1.pkl  # → abdeckung.json
OPENBLAS_CORETYPE=HASWELL OPENBLAS_NUM_THREADS=1 \
  python3 docs/kennwerte_untersuchung_2026-11-13/zusatz.py messen /tmp/zusatz/Haswell_1.json
python3 docs/kennwerte_untersuchung_2026-11-13/zusatz.py vergleichen /tmp/zusatz SkylakeX_1 # → zusatz.json
```

Rechenkern und Thread-Zahl stehen nur dann in den Ergebnisdateien, wenn `threadpoolctl` installiert ist. Die Tests
brauchen das Paket nicht.

---

*Vermerk:* Erstellt am 14.11.2026, Chat-Sitzung (Claude), nach Auftrag des Autors (PR C). Lizenz: CC BY 4.0 wie
`docs/`; die Skripte MIT wie `code/`.
