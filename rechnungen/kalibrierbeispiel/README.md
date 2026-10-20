# Kalibrierbeispiel (Regelstand 2026-11)

Stand 20.10.2026 · Code [`code/pcmms_auswertung/harness/kalibrierbeispiel.py`](../../code/pcmms_auswertung/harness/kalibrierbeispiel.py)
· Lizenz: Code MIT, Text CC BY 4.0.

Dieses Verzeichnis enthält ein **ausführbares, startfreies Beispiel** der normativen Kalibrier- und Prüfsimulation von
Werkzeug 8 (Präregistrierung v2, §8.4, §8.6, A9.11) im Regelstand 2026-11. **Die große Kalibrierung ist im Auftrag vom
20.10.2026 ausdrücklich nicht ausgeführt worden** (Ressourcenentscheidung des Autors). Sie ist eine optionale
Nutzungsmöglichkeit außerhalb dieses Auftrags. Eine Kalibrierabnahme liegt nicht vor; sie wird auch nicht durch
niedrigere Sollzahlen oder durch den Demonstrationsmodus ersetzt.

Das Beispiel benutzt die echte API (`harness.kalibrierung.kalibrieren`) mit den Bezugsmengen G und A, dem Nachziehen
bis |A| = 1000 je Rolle mit technischem Versuchslimit (1,5·|A|), der Prüfrate und Pool-Regel (§8.4), der Auswahl des
H2-Intervalltyps (§8.6), den E3-Kriterien je Prüfgröße, der Reservebedingung 0,95 und der Zeitbilanz. Es gibt keinen
zweiten Kalibrieralgorithmus; das Beispiel ersetzt nur den Kampagnenlauf durch einen mit Checkpoints je Partie.

## Dateien

| Datei | Inhalt |
|---|---|
| `schema.json` | JSON-Schema der Konfiguration (`pcmms-kalibrierbeispiel-1`) |
| `konfig_gross_N01-A4.json` | Beispiel der großen Rechnung (N01-A4, ENTW-2026-11, 24 Blöcke, soll_A = 1000, vier Prozesse) – **nicht ausgeführt** |
| `konfig_demo.json` | sehr kleiner Funktionstest (3 Kampagnen je Rolle, 4 Blöcke, reduzierte Replikate) |
| `demo_ergebnis/` | Ergebnis des Demonstrationslaufs vom 20.10.2026 (ohne Checkpoints), dauerhaft gekennzeichnet „Demonstration, synthetisch, nicht kalibriert“ |

## Bedienung

Alle Befehle aus dem Verzeichnis `code/` (oder mit `PYTHONPATH=code`):

```
# Trockenlauf (Vorgabe): prüft die Konfiguration, nennt Auftragsliste, Seeds, Stände und Kosten; rechnet nichts
python3 -m pcmms_auswertung.cli harness kalibrierbeispiel --konfig ../rechnungen/kalibrierbeispiel/konfig_gross_N01-A4.json

# Demonstration (klein, gekennzeichnet; etwa 45 s mit einem Prozess)
python3 -m pcmms_auswertung.cli harness kalibrierbeispiel --konfig ../rechnungen/kalibrierbeispiel/konfig_demo.json \
    --ausfuehren --ausgabe /pfad/zu/einem/leeren/verzeichnis

# Große Rechnung (nicht Teil des Auftrags; nur mit dem ausdrücklichen Parameter)
python3 -m pcmms_auswertung.cli harness kalibrierbeispiel --konfig ../rechnungen/kalibrierbeispiel/konfig_gross_N01-A4.json \
    --ausfuehren --ausgabe /pfad/zu/einem/leeren/verzeichnis --bestaetigung "grosse Kalibrierung starten"
```

Der Trockenlauf gibt den vollständigen Ausführungsbefehl aus (mit `--ausgabe` und, bei der großen Rechnung,
`--bestaetigung`). Der Trockenlauf der großen Konfiguration schätzt 2000 bis 4500 Kampagnen (ohne bzw. mit Pool-Neuberechnung und
ausgeschöpftem Versuchslimit), bei 82 s je Kampagne mit den normativen Replikatzahlen (B = 10 000; Belegpaket der
Entscheidungsvorlage: A4 45,5 Kernstunden für 1000 + 1000 Kampagnen) etwa 46 bis 103 Kernstunden, mit vier Prozessen
etwa 11 bis 26 Stunden Wandzeit, für **ein** System (V1-G0 nach dem Belegpaket bis etwa das 1,8-Fache). Vor einer großen Rechnung die Sekunden je Kampagne mit einer kleinen
Laufzeitprobe ersetzen (Feld `sekunden_je_kampagne`).

## Sicherungen

- Ohne `--ausfuehren` wird nie gerechnet; die große Rechnung verlangt zusätzlich genau
  `--bestaetigung "grosse Kalibrierung starten"` und eine Konfiguration mit `"modus": "gross"`, soll_A = 1000 und
  ohne Reduktion. Der Demonstrationsmodus ist begrenzt (`DEMO_GRENZEN`, `DEMO_UNTERGRENZEN`): soll_A ≤ 5; Plan mit
  n₀ ≤ 20, n_Pilot ≤ 20, Mindestzahl der Phase-0-Referenzläufe `ref_min_p0` ≤ 42, Referenzabstand ≥ 12, höchstens
  4 Blöcke, n_Zyklen ≤ 100 und höchstens 2 Messtagen, ohne Zusatz-, Prüf- und Einstellung-2-Konfigurationen; B,
  H2-Replikate, H3- und E3-MC ≤ 200, ε_ctrl-Datensätze ≤ 300; 1 ≤ n_min ≤ n. Unbekannte Planfelder werden abgelehnt.
- Ein Ausgabeverzeichnis mit Ergebnissen einer anderen Konfiguration wird nicht überschrieben
  (`konfiguration.json` mit Prüfsumme); Checkpoints mit anderem Schlüssel (Profil, Plan, Verfahren, Szenario, Seeds,
  Codestand) werden abgelehnt, nicht vermischt. Die Pool-Neuberechnung der Prüfung (gleiche Seeds, andere
  Werkzeug-8-Werte) steht daneben.
- Demonstrationswerte tragen in Ergebnis und Werkzeug-8-Werten die Kennzeichnung „Demonstration, synthetisch, nicht
  kalibriert“; `teil_b.erstellen` lehnt sie für jede nicht synthetische Kennung ab.
- Es werden keine weiteren Systeme, Diagnosen oder Matrizen automatisch gestartet.

## Ergebnisstruktur (`ergebnis.json/.npz`)

| Feld | Bedeutung |
|---|---|
| `kennzeichnung`, `betriebsart`, `status`, `abgeschlossen` | Demonstration oder große Rechnung; Status „nicht abgeschlossen“, wenn \|A\| je Rolle nicht erreicht wurde; `abgeschlossen` ist nur bei der großen Rechnung mit erreichtem \|A\| wahr |
| `werkzeug8` | Werte für Teil B (c_H1, c_H1Z, Rauschbias mit u, H2-Intervall, Prüfrate, `e3_kriterien`) mit Kennzeichnung |
| `c_H1`, `c_H1Z`, `pruefung`, `gepoolt`, `h2` | kritische Werte mit Bootstrap-Fehler, Prüfrate, Pool-Regel, gewählter H2-Typ |
| `gemeinsame_bestaetigung` | P(H1 und H2 bestätigt) mit Nenner G |
| `mengen` | G, A und Ausschlüsse je Grund für Kalibrierung und Prüfung; Nachziehprotokoll je Rolle |
| `e3` | Raten „auffällig“/„unauffällig“ je Prüfgröße und Kriterienbefund (nur bei der normativen Zahl ausgewiesen) |
| `reserve_ziel`, `zeitbilanz` | Bedingung 0,95 mit Zähler/Nenner; Zeit je Kampagne nach Termen |
| `checkpoints`, `platzhalter` | geladene/gerechnete Partien; Hinweis, wenn Werte aus nicht abgeschlossenen Mengen stammen |

Tatsächlich berechnete Werte stehen nur in Ergebnissen mit `"gerechnet": true`. Der Trockenlauf enthält keine
Rechenwerte, nur Konfiguration, Auftragsliste und Schätzungen. Im Demonstrationsergebnis sind alle Zahlen Ergebnisse
von drei Kampagnen je Rolle: Funktionsnachweis, keine Kalibrierung (Kriterien deshalb `None`).

## Demonstrationslauf vom 20.10.2026

`konfig_demo.json`, ein Prozess, 9 Kampagnen (3 Kalibrierung, 3 Prüfung, 3 Pool-Neuberechnung), 43 s; Fortsetzung aus
den Checkpoints in 1 s (6 Partien geladen, keine neu gerechnet). In der Endabnahme auf dem Endstand des Branches in ein
leeres Verzeichnis wiederholt (43 s); `demo_ergebnis/` enthält dieses Ergebnis. Gegenüber dem ersten Lauf gleich sind c,
Prüfrate, b̂, H2 und alle Raten; neu bzw. geändert sind nur Codestand, Profilprüfsumme (Regeln des Regelstands 2026-11
ergänzt), die realisierten Kampagnenzahlen G je Rolle und die Zuordnung der Aufwärmläufe am Tagesbeginn zum Zeitterm
„Aufwärmen bei Tageswechsel“. |A| = |G| = 3 je Rolle; eine Prüfkampagne mit
simulierter Wiederaufnahme (Bezugslauf, Kontrollsatz, T_UA = 1800 s); Pool-Regel gegriffen (bei drei Kampagnen ohne
Aussage). Die Zahlen in `demo_ergebnis/` sind keine Werte für Teil B.
