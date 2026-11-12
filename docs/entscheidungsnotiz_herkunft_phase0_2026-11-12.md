# Entscheidungsnotiz: Herkunftsnachweis der Phase-0-Daten

**PCMMS — Phasenkontrollierte Mehrmassensysteme**\
Matthias Früh · Unabhängiger Forscher · ORCID [0009-0005-9984-4207](https://orcid.org/0009-0005-9984-4207)\
Stand: 12. November 2026 · Fassung 1 (entschieden und umgesetzt) · Entwurf 1 vom selben Tag war mit `main` =
`6261d16` abgeglichen (nach Pull Request #39)

**Status:** Vom Autor am 12.11.2026 entschieden (Abschnitt 8) und mit Pull Request #40 umgesetzt: Modul
[`herkunft.py`](../code/pcmms_auswertung/herkunft.py), Pilotausgabe `pilot-0.5`, Teil B `teil_b-0.5`. Abschnitt 9
nennt, wo die Umsetzung vom Entwurf abweicht. Alles im Repository ist Simulation oder Analytik; Messdaten existieren
nicht.

---

## 1 Anlass

Bis `pilot-0.4` und `teil_b-0.4` war die Bindung von Teil B an die Phase-0-Daten eine Prüfsumme über berechnete Werte
(Stand `6261d16`):

- `pilot.daten_sha256`: SHA-256 über die Lauf-IDs und die komprimierten NPZ-Bytes der Pflichtfelder der
  Phase-0-Zusammenfassungen.
- Sie stand als `phase0_sha256` in der Bindung des Satzes und in `teil_b.BINDUNG_IDENTITAET`. `teil_b.phase0_satz`
  rechnete sie neu und brach bei Abweichung ab („stammt aus anderen Phase-0-Daten“).
- Der Wert hängt am zlib des Systems (PR #36) und am Rechenkern von OpenBLAS (PR #37, #38). Dieselbe Kampagne
  ergibt mit dem Kern SkylakeX `c02f4e7e…`, mit HASWELL `a7130835…`.
- Anhang A9.3 Nr. 1 der Präregistrierung verlangt für Teil B „die SHA-256-Prüfsummen aller Rohdaten der Phase 0
  und der Pilotläufe“. Teil B führte keine Rohdaten-Prüfsummen.

## 2 Bestandsaufnahme

Die Entscheidung vom 12.11.2026 ordnet nach „Z – experimentell“ und „H – synthetisch“. Im Code sind das zwei
getrennte Merkmale. Die Notiz hält sie auseinander.

| Merkmal | Werte | Wo es steht |
|---|---|---|
| Ebene eines Laufs | Z: Lauf mit Rohdatei (Zeitreihe); H: Lauf ohne Rohdatei (Harmonische direkt aus dem Rauschmodell) | Laufkopf, Feld `ebene` |
| Datenart eines Objekts | `synthetisch` oder `messung` | Objektkopf, Feld `datenart` (`formate.DATENARTEN`) |

Ebene Z gibt es auch synthetisch: `generator/ebene_z.py` schreibt Rohdateien, Stufe 1 liest sie. Ebene H ist
immer synthetisch.

**Läufe mit Rohdatei (Ebene Z).**

- Je Lauf zwei Dateien: Kopf (JSON) und Daten (NPZ). Das Manifest nennt je Lauf `sha256_kopf` und `sha256_daten`
  und prüft beide beim Lesen gegen die Dateien (`rohdaten.py`).
- Stufe 1 schreibt in jeden Laufkopf `hash_rohdatei` (SHA-256 der Datendatei), `kalibrier_hash` (SHA-256 des
  Kalibrierobjekts) und `version_stufe1` (`stufe1.laufzusammenfassung`).
- Diese Werte sind Prüfsummen gespeicherter Bytes. Sie hängen nicht am Rechner, der sie prüft.

**Läufe ohne Rohdatei (Ebene H).**

- `hash_rohdatei` und `kalibrier_hash` sind leer; `version_stufe1` ist die Generatorversion `ebene_h-0.1`
  (`generator/ebene_h.py`).
- Was die Erzeugung bestimmt, stand weder im Laufkopf noch in der Tabelle: Modell, Laufliste, Zufallsstrom.

**Schon vorhandene Schranken.**

- Messdaten sind in dieser Stufe nicht zugelassen, und eine Auswertung mischt nie Mess- und synthetische Daten
  (`formate.pruefe_kopf`, `formate.gleiche_datenart`).
- Eine `LaufTabelle` verlangt eindeutige Lauf-IDs; `sortiert()` ordnet nach aufsteigender Position
  (`zusammenfassung.py`).

## 3 Lösung: Herkunftsnachweis statt Ergebnisprüfsumme

**Grundsatz.** Die Bindung besteht nur aus exakten Angaben: Lauf-IDs, Positionen, Prüfsummen gespeicherter
Dateien, Versionskennungen, Zustand eines Zufallsstroms. Eine Prüfsumme über berechnete Gleitkommafelder kommt in
der Bindung nicht mehr vor. Der Nachweis enthält keine Gleitkommazahl.

### 3.1 Nachweis je Lauf

| Klasse | Gilt für | Felder des Nachweises |
|---|---|---|
| `rohdatei` | Läufe der Ebene Z | `lauf_id`, `position`, `klasse`, `hash_rohdatei`, `kalibrier_hash`, `version_stufe1` |
| `generator` | Läufe der Ebene H | `lauf_id`, `position`, `klasse`, `version_stufe1` (Generatorversion) |

- Ein Lauf der Ebene H erhält keinen Rohdatei-Hash, auch keinen künstlichen. Ein gefülltes Feld `hash_rohdatei`
  oder `kalibrier_hash` wird dort zurückgewiesen.
- Bei einem Lauf der Ebene Z müssen beide Prüfsummen SHA-256-Hexzahlen sein; fehlende oder leere Felder werden
  zurückgewiesen.

### 3.2 Generatornachweis je Tabelle

Er ist Pflicht, sobald ein Lauf der Klasse `generator` vorkommt. Felder:

| Feld | Inhalt |
|---|---|
| `version` | Version des Generators (`ebene_h-0.1`; beim Strukturgenerator `phase0_modell-0.1`) |
| `modell_sha256` | SHA-256 der Modellbeschreibung mit dem wirksamen Rauschmodell: System, Rauschmodell, Plan, Effektstärke, Effekte, k_voll, Vollausschlag, Hertz-Modell (`szenarien.beschreibung`) |
| `laufplan_sha256` | SHA-256 der Laufliste, die der Generator erhalten hat. Auch die Läufe der Phase 1 gehen ein, weil sie bestimmen, welche Ziehungen ein Lauf erhält |
| `strom_sha256` | SHA-256 des Zustands des Zufallsstroms vor der ersten Ziehung |
| `zusatzstrom_sha256` | dasselbe für den Zusatzstrom des Strukturmodells, sonst leer |
| `aufruf` | leer oder die Angaben, mit denen `harness.kette` die Tabelle erzeugt hat: `szenario`, `stufe`, `seed`, `stroeme` |

- Den Nachweis legt der Generator selbst an (`ebene_h.generatornachweis`), bevor er die erste Zahl zieht. Er liest
  den Zustand des Stroms, den er tatsächlich erhält. Jede Tabelle der Ebene H trägt ihn damit von Anfang an, auch
  wenn sie nicht über `kette.kampagne_erzeugen` entsteht.
- `kette.kampagne_erzeugen` und `kette.kampagne_ablauf` ergänzen den Aufruf (der Ablauf nur, wenn das Modell aus
  dem Szenario folgt und nicht vorgegeben ist). Der Seed wird geprüft: `zufall.strom(seed, Name)` muss den Zustand
  `strom_sha256` ergeben. Plan, Stärke, Rauschmodell und k_max stehen nicht im Aufruf, sondern in `modell_sha256`.
- Der Nachweis reist in den Metadaten der Tabelle mit (`zusammenfassung.META_GENERATORNACHWEIS`), nicht im
  Laufkopf. `auswahl`, `sortiert`, `schreiben` und `lesen` erhalten ihn. Die Laufköpfe bleiben unverändert; ihre
  Prüfsummen in den Prüfsätzen ändern sich nicht.

### 3.3 Nachweis des Satzes und Bindung

Der Nachweis der Phase-0-Läufe ist ein Objekt mit:

- `version`: `herkunft-1`;
- `datenart`;
- `klassen`: Zahl der Läufe je Klasse;
- `optionale_felder`: Namen der vorhandenen optionalen Felder (nur Namen, keine Werte);
- `laeufe`: die Nachweise je Lauf in kanonischer Ordnung;
- `generator`: der Generatornachweis oder leer.

Die Bindung ist der SHA-256 dieses Objekts in kanonischer JSON-Form (`herkunft.sha256`).

| Ort | Feld |
|---|---|
| Pilotausgabe, je Satz | `phase0_herkunft` (der Nachweis) und `bindung.phase0_herkunft_sha256` |
| Teil B | `nr1.phase0_herkunft`, `nr1.phase0_herkunft_sha256`, `nr2.phase0_bindung.phase0_herkunft_sha256` |

Damit stehen die Rohdaten-Prüfsummen einzeln in Teil B, wie A9.3 Nr. 1 es verlangt. Weil der Nachweis eine Liste
ist, nennt die Fehlermeldung den ersten abweichenden Lauf und das abweichende Feld (`herkunft.unterschied`).

### 3.4 Reihenfolge und Mehrfachvorkommen

- Kanonische Ordnung: aufsteigende Position. Die Zeilenreihenfolge der Tabelle hat keinen Einfluss.
- Positionen und Lauf-IDs müssen im Satz eindeutig sein.
- Derselbe Rohdatei-Hash bei zwei Läufen ist ein Fehler.
- Ein fehlender, zusätzlicher oder umgestellter Lauf ändert den Nachweis.

### 3.5 Schranken gegen Daten anderer Herkunft

1. **Pilotausgabe und Läufe gehören zusammen.** Teil B bildet den Nachweis der übergebenen Phase-0-Läufe. Er muss
   einem Nachweis der Pilotausgabe gleichen: dem des Satzes auf oberster Ebene oder dem des Satzes der Suche. Die
   Prüfung gilt in beiden Bindungsarten (`plan` und `historisch`) und auch dann, wenn Teil B den Satz neu rechnet
   (`teil_b.pruefe_pilot_herkunft`). Für Läufe mit einem kürzeren Fenster als im Pilotskript heißt das: Bei
   Rohdateien bleibt der Nachweis derselbe; eine neu erzeugte Tabelle der Ebene H muss die sein, die das
   Pilotskript in seiner Suche verwendet hat.
2. **Zuordnung eines Satzes.** Ein Satz der Pilotausgabe mit gleichem k und N_z wird nur übernommen, wenn seine
   Bindung dieselbe Prüfsumme des Nachweises trägt.
3. **Klassenregeln.** Bei Datenart `messung` sind nur Läufe der Klasse `rohdatei` zulässig. Läufe der Klasse
   `generator` brauchen den Generatornachweis; fehlt er, wird der Satz zurückgewiesen, schon im Pilotskript.
4. **Mischung.** Kommen beide Klassen in einem Satz vor, steht das in `klassen`, und jeder Lauf trägt den
   Nachweis seiner Klasse. Bei Datenart `messung` ist Mischung ausgeschlossen.
5. **Datenart.** Wie bisher über `gleiche_datenart`; zusätzlich steht sie im Nachweis und geht in die Bindung ein.
   Eine Tabelle ohne Angabe gilt als synthetisch, weil diese Stufe nur synthetische Daten verarbeitet.

### 3.6 Versionierung und Altbestand

- Unter den aktuellen Profilen (AF-2026-11, ENTW-2026-11) gilt `pilot-0.5` und `teil_b-0.5`. `nr1.phase0_sha256`
  und `nr1.phase0_optionale_sha256` entfallen dort.
- Unter den historischen Profilen (AF-2026-10, ENTW-2026-10) bleiben `pilot-0.3` und `teil_b-0.3` mit
  `phase0_sha256` unverändert. Die Docstrings benennen die Bedeutung: Ergebnisprüfsumme, an zlib und Rechenkern
  gebunden. Ein Generatornachweis wird dort nicht verlangt und nicht ausgewertet. Der Generator legt ihn aber
  unabhängig vom Profil an; eine Datei `zusammenfassungen` der Ebene H hat deshalb auch dort einen zusätzlichen
  Schlüssel im Kopf.
- Eine Pilotausgabe ohne Herkunftsnachweis (bis `pilot-0.4` oder aus einem historischen Profil) gilt unter
  `teil_b-0.5` nicht als an die Läufe gebunden. Sie wird nicht umgedeutet: Teil B bricht ab und verlangt, das
  Pilotskript neu zu rechnen.
- Zwei Bindungen bezeichnen nur dann denselben Satz, wenn sie die Angabe zu den Läufen in derselben Fassung
  tragen (`teil_b.gleich_gebunden`).
- `tests/fixtures/historisch_main_referenz.json` bleibt gültig.

### 3.7 Messungen mit dem umgesetzten Stand

Drei Kampagnen der Ebene H (Stufe L1, Plan des Prüfsatzes; Intel Xeon mit AVX-512, Python 3.13.18, zlib 1.3, ein
BLAS-Thread). „Datenfelder“ ist die bisherige Prüfsumme `pilot.daten_sha256`.

| Kampagne | Phase-0-Läufe | Nachweis, SkylakeX | Nachweis, HASWELL | Datenfelder, SkylakeX | Datenfelder, HASWELL |
|---|---|---|---|---|---|
| A04-R4, Seed 7 | 181 | `9e3792702cbc` | `9e3792702cbc` | `c02f4e7ed562` | `a7130835ed39` |
| A04-R4, Seed 8 | 181 | `f473dd33effe` | `f473dd33effe` | `74c0e559d264` | `10227908534b` |
| I01-amplitude, Seed 7 | 226 | `26769ba95874` | `26769ba95874` | `494393675abb` | `fc2879d7640b` |

- Der Nachweis ist unter beiden Kernen gleich und unterscheidet die drei Kampagnen. Als JSON hat er 18,9 kB
  (181 Läufe) und 23,5 kB (226 Läufe).
- Eine vierte Kampagne (N01-V1G0, Seed 7, Plan mit zwei Blöcken wie in `tests/test_herkunft.py`, 162
  Phase-0-Läufe) ist unter sechs Kernen gerechnet: SkylakeX, HASWELL, ZEN, SANDYBRIDGE, NEHALEM, PRESCOTT. Der
  Nachweis ist sechsmal gleich (`d86333f3ed60`); die Prüfsumme der Datenfelder nimmt vier verschiedene Werte an.
- Die Modellprüfsumme ist für alle 36 Szenarien des Katalogs (Stufe L1, Plan des Prüfsatzes) unter SkylakeX und
  HASWELL gleich, auch für die sieben Szenarien mit Stärkesuche und den Hertz-Fall.

Die Skripte dieser Messungen liegen nicht im Repository. Der Test `test_p2_nachweis_gleich_unter_zwei_rechenkernen`
wiederholt den Vergleich für zwei Kerne bei jedem Testlauf.

## 4 Was der Nachweis nicht leistet

- **Er belegt Herkunft und Rechenvorschrift, nicht die Werte.** Geänderte Zusammenfassungen bei unverändertem
  Nachweis erkennt er nicht. Die bisherige Prüfsumme erkannte sie, schlug aber auch bei gleichen Daten auf einem
  anderen Rechner an. Der Abgleich der Werte mit Toleranz ist Sache von PR C; der Test
  `test_grenze_der_nachweis_belegt_die_herkunft_nicht_die_werte` hält den Stand fest.
- **Er garantiert keine bitgleichen Ergebnisse.** Dieselbe Generatoridentität ergibt auf verschiedenen
  Prozessoren Werte, die sich im Rundungsrauschen unterscheiden (gemessen bis 1,6·10⁻¹³ relativ).
- **Er hängt an der Versionspflege.** `ebene_h.VERSION` und `version_stufe1` müssen steigen, wenn sich die
  Ausgabe ändert. Der Git-Stand steht weiter in `code_version`, geht aber nicht in die Bindung ein; sonst bräche
  jeder Commit die Bindung.
- **Bei Ebene Z gilt er für die gespeicherten Dateien.** Neu erzeugte synthetische Rohdaten sind neue Dateien mit
  eigenen Prüfsummen. `kalibrier_hash` gilt für das Kalibrierobjekt, mit dem Stufe 1 gerechnet hat; eine neu
  gerechnete Kalibrierung kann sich in den letzten Bits unterscheiden und ergibt dann eine andere Prüfsumme.
- **Beim Strukturgenerator stammt das Modell aus berechneten Größen.** Die Prüfsumme der Struktur gilt für genau
  diese Felder. Die Tabellen dieses Generators dienen der Planungssimulation innerhalb eines Rechenlaufs.

## 5 Alternativen

| Nr. | Alternative | Bewertung |
|---|---|---|
| A1 | Ergebnisprüfsumme behalten, aber über unkomprimierte Feldbytes | Beseitigt zlib, nicht den Rechenkern. Für neu gerechnete Daten bleiben falsche Alarme. Verworfen (Entscheidung vom 12.11.). |
| A2 | Künstlicher Rohdatei-Hash für Ebene H | Täuscht Rohdaten vor. Verworfen (Entscheidung vom 12.11.). |
| A3 | Für Ebene H nur Kennung und Seed | Übersieht ein geändertes Modell oder einen geänderten Plan bei gleicher Kennung. Verworfen. |
| A4 | H-Tabellen immer als Datei ablegen und an die Dateiprüfsumme binden | Exakte Bytes, aber Kette und Tests rechnen im Speicher, und beim Neuerzeugen hängt die Datei wieder am Rechenkern. Nicht umgesetzt. |
| A5 | Neuer Regelstand statt `teil_b-0.5` | Sauberste Trennung, aber neue Profile und Dokumente. Die Bindung ist keine Entscheidungsregel. Nicht gewählt (E-2). |

## 6 Auswirkungen

**Präregistrierung.** Der Wortlaut von A9.3 Nr. 1 bleibt. Der Code erfüllt ihn jetzt für Läufe mit Rohdatei.
Entscheidungsregeln, Schwellen, Modelle und Daten ändern sich nicht. Ebene H kommt in Teil B einer Messkampagne
nicht vor; der Generatornachweis betrifft nur den Pipelinetest (A9.11).

**Geändert mit PR #40.**

- Code: `herkunft.py` (neu), `pilot.py`, `teil_b.py`, `zusammenfassung.py`, `generator/ebene_h.py`,
  `generator/phase0_modell.py`, `harness/kette.py`.
- Tests: `tests/test_herkunft.py` (neu), `tests/test_d_laufgroessen.py`, `tests/test_ap11_anpassung.py`.
  `tests/test_ap13_kmax.py` bleibt unverändert, weil es unter dem historischen Profil rechnet.
- Dokumente: [Schnittstellen](ap11_ap12_ap13_schnittstellen.md) (Abschnitte 4 und 5),
  [Software](ap11_ap12_ap13_software.md) (Abschnitt 1e), [Plan AP-13](plan_ap13_pipelinetest.md) (Nachtrag in 2.6).

**Nicht Teil von PR #40.** Weitere Prüfsummen über berechnete Felder bleiben für PR C:

- `auswertung.py`: `zusammenfassungen_sha256` in der Herkunft eines Ergebnisses;
- `generator/phase0_modell.py`: `daten_sha256` in der Herkunft der Struktur aus P0.8;
- `harness/pruefsatz.py`: `hash_felder`, Grundlage der drei in der CI abgewählten Tests;
- `harness/phase0_rechnungen.py`: Vergleich der Tabellen in `r2d_bekannt_gleich`.

`nr1.kalibrierung_sha256` und `nr1.pilot_sha256` in Teil B bleiben. Sie benennen die übergebenen Objekte und
dienen keiner Bindungsprüfung.

## 7 Negativtests

Jeder Test verändert eine Angabe und erwartet die Zurückweisung (`tests/test_herkunft.py`).

| Nr. | Veränderung | Erwartung | Test |
|---|---|---|---|
| N1 | anderer Seed; nur ein anderer Generatorstrom; Seed im Aufruf, der den Strom nicht ergibt | zurückgewiesen | `test_n1_anderer_seed` |
| N2 | anderes Szenario; geänderter Modellwert bei gleichem Laufplan und Strom | zurückgewiesen | `test_n2_…` |
| N3 | anderer Plan, anderes k_max, anderes Rauschmodell; Effektstärke | zurückgewiesen | `test_n3_…` (vier Fälle) |
| N4 | andere Generatorversion | zurückgewiesen | `test_n4_andere_generatorversion` |
| N5 | Tabelle der Ebene H ohne, mit unvollständigem oder mit erweitertem Generatornachweis; Lauf der Ebene H mit Rohdatei-Hash | zurückgewiesen | `test_n5_…` |
| N6 | ein Lauf entfernt oder hinzugefügt | zurückgewiesen | `test_n6_…` |
| N7 | Position eines Laufs geändert; zwei Positionen vertauscht | zurückgewiesen | `test_n7_position_geaendert` |
| N8 | doppelte Position | Fehler | `test_n8_doppelte_position` |
| N9 | `hash_rohdatei` eines Laufs geändert (Ebene Z) | zurückgewiesen | `test_n9_n10_…` |
| N10 | Rohdatei-Hashes zweier Läufe vertauscht | zurückgewiesen | `test_n9_n10_…` |
| N11 | derselbe Rohdatei-Hash bei zwei Läufen | Fehler | `test_n11_…` |
| N12 | `kalibrier_hash` oder `version_stufe1` geändert | zurückgewiesen | `test_n12_…` |
| N13 | Lauf der Ebene Z ohne, mit leerem oder mit ungültigem Hash | zurückgewiesen | `test_n13_…` |
| N14 | Lauf der Klasse `generator` bei Datenart `messung`; Mischung bei `messung` | zurückgewiesen | `test_n14_…` |
| N15 | Pilotausgabe ohne Nachweis unter `teil_b-0.5`; Nachweis, der nicht zu seiner Prüfsumme passt | zurückgewiesen | `test_n15_…` |

Dazu die Gegenproben, die angenommen werden müssen:

| Nr. | Veränderung | Erwartung | Test |
|---|---|---|---|
| P1 | dieselben Läufe in anderer Zeilenreihenfolge | angenommen, Satz übernommen | `test_p1_…` |
| P2 | dieselbe Kampagne mit einem anderen Rechenkern erzeugt | gleicher Nachweis | `test_p2_…` |

Die Tests N9 bis N13 rechnen mit Rohdateien einer kleinen Kampagne auf Ebene Z (56 Läufe). Der Test
`test_ebene_z_teil_b_fuehrt_die_rohdaten_pruefsummen` vergleicht jede Prüfsumme in Teil B mit der Datei auf der
Platte und mit dem Manifest. `test_satz_der_suche_mit_gekuerztem_fenster` prüft den Fall, dass die Suche des
Pilotskripts ein kürzeres Fenster festlegt: Teil B nimmt genau die Läufe an, die die Suche verwendet hat.

## 8 Entscheidungen des Autors vom 12.11.2026

| Nr. | Frage | Entscheidung |
|---|---|---|
| E-1 | Lösung nach Abschnitt 3 annehmen? | angenommen |
| E-2 | Version: `teil_b-0.5` unter den aktuellen Profilen oder neuer Regelstand? | `teil_b-0.5`; kein neuer Regelstand |
| E-3 | Soll der Nachweis bei Ebene Z auch `sha256_kopf` der Rohlauf-Kopfdatei führen? | später, zusammen mit dem Rohdatenformat von AP-10 |
| E-4 | Sollen Kennwerte der Pflichtfelder mit Toleranz zusätzlich in die Bindung? | mit PR C. Präzisierung: Numerische Kennwerte mit Toleranz gehören in eine zusätzliche Ergebnisprüfung, nicht in den exakten SHA-256-Herkunftsschlüssel |
| E-5 | Mischung beider Klassen bei synthetischen Daten? | zulassen, nur mit eindeutiger Kennzeichnung und vollständigen Nachweisen |
| E-6 | Reihenfolge B vor C beibehalten? | beibehalten; C zeitnah anschließen |

Zwei Absicherungen aus der Entscheidung:

1. Alte Datenbindungen werden nicht stillschweigend übernommen (Abschnitt 3.6).
2. PR B und PR C gehören zusammen. PR B nimmt die Kontrolle über berechnete Daten aus der Bindung; PR C stellt sie
   als Vergleich mit Toleranz wieder her. Dazwischen wird kein wissenschaftlicher Referenzstand eingefroren.

## 9 Umsetzung: Abweichungen vom Entwurf 1

| Nr. | Entwurf 1 | Umsetzung | Grund |
|---|---|---|---|
| U-1 | `harness/kette.py` legt den Generatornachweis an (Felder `version`, `szenario`, `stufe`, `seed`, `stroeme`, `modell_sha256`) | der Generator legt ihn an (`version`, `modell_sha256`, `laufplan_sha256`, `strom_sha256`, `zusatzstrom_sha256`); `kette` ergänzt den Aufruf (`szenario`, `stufe`, `seed`, `stroeme`) | Tests und Harness erzeugen Tabellen an vielen Stellen ohne `kette.kampagne_erzeugen`. Ein angegebener Seed ist nur so gut wie der Aufrufer; der Zustand des Stroms stammt vom Generator selbst |
| U-2 | Laufliste nicht im Generatornachweis | `laufplan_sha256` | Die Ziehungen eines Phase-0-Laufs hängen von allen Läufen ab, auch von denen der Phase 1 |
| U-3 | nur `teil_b-0.5` genannt | zusätzlich `pilot-0.5` | Die Bindung entsteht im Pilotskript; die Version der Pilotausgabe ist Teil der Bindung |
| U-4 | alter Satz: Neuberechnung „oder Fehler“ | Fehler | Die Pilotausgabe liefert auch Größen außerhalb des Satzes (σ_tol, σ_c, F_LO). Ohne Nachweis ist nicht prüfbar, dass sie zu den Läufen gehört |
| U-5 | Vergleich nur für einen Satz mit gleichem k und N_z | Pilotausgabe und Läufe werden immer verglichen | Rechnet Teil B den Satz neu, fand bisher kein Vergleich statt |
| U-6 | `nr1.phase0_herkunft` | zusätzlich `nr1.phase0_herkunft_sha256` | Die Prüfsumme steht neben dem Nachweis, auf den sie sich bezieht |

## 10 Offen für PR C

- Abgleich der Werte mit Toleranz (kompakte Referenzkennwerte; volle Felder nur, wenn die Abdeckung sonst nicht
  reicht), auch für die drei abgewählten Prüfsatz-Tests;
- Unabhängigkeit von der Thread-Zahl in den Kampagnen des Harness (Abnahmekriterium von C);
- konstruiertes Gleichstandsbeispiel für `code/auslegung.py`;
- danach: Festlegung von Rechenkern und Thread-Zahl in der CI aufheben.

---

*Vermerk:* Erstellt am 12.11.2026, Chat-Sitzung (Claude), nach Auftrag und Entscheidung des Autors. Die Zahlen in
Abschnitt 3.7 sind mit dem Stand von Pull Request #40 gerechnet. Lizenz: CC BY 4.0 wie `docs/`.
