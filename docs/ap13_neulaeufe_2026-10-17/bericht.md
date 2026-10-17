# AP-13-Neuläufe K12, K19 und E3 nach den Korrekturen A–E

Stand 17.10.2026 · Lizenz CC BY 4.0 · Ergänzungsbericht zu
[`ap11_ap12_ap13_software.md`](../ap11_ap12_ap13_software.md) (Abschnitte 1a und 4.4) und
[`ap11_ap12_ap13_kriterien.md`](../ap11_ap12_ap13_kriterien.md). Synthetische Entwicklungsdiagnostik: keine
Kalibrierabnahme, keine Schwellenentscheidung, keine Änderung von Teil A, keine AP-13-Gesamtabnahme.

Gezielt neu gerechnet wurden die von den Korrekturen A (Planungshaken), B (Zeitmittel in Stufe 1) und E (Unsicherheit von
T in E3) betroffenen Entwicklungsläufe des Prüfstands vom 16.10.2026 (Stand `7a259ef`). Der historische kompakte
Prüfstand [`ap11_ap12_ap13_pruefstand.json`](../ap11_ap12_ap13_pruefstand.json) bleibt unverändert (Git-Blob
`c0a6afb4…`); alle übrigen Zahlen dort gelten weiter als historische Ergebnisse.

## Kurzantworten

1. **K12 – ändert sich die reduzierte Suche mit dem richtigen Plan?** Nein im Ergebnis: weiterhin „kein zulässiger
   Arbeitspunkt unter diesen Annahmen“. Simuliert wird jetzt der Plan des Kandidaten (N_z = 100, T_a = 10 s,
   T_e = 1 s, T_Lauf = 16 s statt 17 s, 2 statt 1 Messtag). Kein simulierter Kandidat erreicht
   P(H1 und H2 bestätigt | exakt) ≥ 0,8: bei k = 30 0/4 (n_min = 18) und 1/4 (n_min = 24), bei k = 29 je 0/4; vorher
   1/4, 0/4, 0/4, 0/4. Das Budget bindet nicht (n = 20 bzw. 26 bei n_max = 743, p̂ = 0). 26 weitere Aufrufe mit
   zusammen 52 Kandidaten sind wegen der Entwicklungsgrenze von 2 Aufrufen nicht gerechnet. Mit 4 + 4 Kampagnen je
   Kandidat (MC-Fehler bis 0,22) folgt daraus keine Power-Aussage.
2. **K19 – bleiben die Vergleiche nach der Zeitmittelkorrektur innerhalb der Schranken?** Ja. Alle sieben u_c-Mediane
   beider Ebenen sind bitgleich zum Altlauf, obwohl Ebene Z jetzt mit `stufe1-0.2` (Zeitmittel nach A1) ausgewertet ist;
   die relativen Differenzen Z/H liegen zwischen −2,54 % und +1,39 % (Schranke 5 %), H1, H1Z, H2 und H4 sind auf beiden
   Ebenen 4/4 bestätigt (innerhalb zweier MC-Standardfehler). u_c folgt aus den Harmonischen, nicht aus ⟨N⟩, und der
   Generator der Ebene Z hat gleiche Periodendauern; die Korrektur B wird in diesem Abgleich deshalb nicht sichtbar.
3. **E3 – wie ändern sich Raten und Unsicherheiten?** Die Raten der 11 Punkte (570 Kampagnen) bleiben in jeder Kategorie
   gleich; keine Kampagne ist ohne dreiwertige Bewertung, keine der 570 000 T-Ziehungen ist unzulässig. Die
   Unsicherheit der E3a-Phasen steigt durch T im Median um 0,0–1,1 % (höchstens 3,5 %), u(q_Z) in E3b praktisch nicht
   (dort kommt T nicht vor, die Zelllagen heben sich auf). Dieselben Kampagnen mit u ohne T-Anteil bewertet ergeben an
   allen Punkten die historischen Zähler: Die (ausbleibende) Änderung folgt allein aus dem kleinen T-Anteil der sehr
   genauen synthetischen Kalibrierung. „unbestimmt“ entsteht auf L1 ausschließlich an E3b (q_Z + 1,645·u(q_Z) > q_tol =
   0,00058; z. B. 186 von 186 bei N01-A4), nicht an den Phasen.
4. **Grenzen:** Abschnitt 5 – Entwicklungsannahmen (Zeitangaben, Profil, Plan, Kampagnenzahlen), Planung ohne
   Generator aus gemessenen Pilotkovarianzen, T-Modell ohne Kippmoden und Modullagenunsicherheit, nicht modellierte
   Kreuzkovarianzen getrennter Kalibriermessungen, offene Fachregeln (E3, Planung, G4, Drift-Zusatz).

## 1 Ausgangsstand, Herkunft und Umfang

- **Code.** Branch `ap13-neulaeufe-2026-10-17` von `main` = `dd7676e` (Merge von PR #20). Treiber und benötigte
  Berichtslogik `0982df9`, Auftragsliste und Werkzeug-8-Dateien `020e131`; gerechnet auf **`020e131`** aus sauberem
  Arbeitsbaum (vom Treiber vor und nach jedem Auftrag geprüft), Rechencode-Hash in jedem Checkpoint. Treiber:
  [`harness/neulauf.py`](../../code/pcmms_auswertung/harness/neulauf.py) über den Produktionsfunktionen
  (`pruefstand.ausfuehren` mit Schritt `planung`, `ebenen.vergleich_verrauscht`, `kampagnen.ausfuehren`); Vergleich und
  Tabellen: [`harness/neulauf_vergleich.py`](../../code/pcmms_auswertung/harness/neulauf_vergleich.py); dessen
  Ergänzungen nach der Rechnung (`23ebb15`, `fbedadc`, `beeeee3`: bestimmende Prüfgrößen, Tabellen, Kampagnenübersicht)
  liegen außerhalb des Rechencode-Hashes, die Checkpoints wurden ohne neue Rechnung übernommen. Bericht und kompakte
  Ergebnisse erzeugt auf `fb23ba4`.
- **Gemeinsame Einstellungen wie im Altlauf**, vom Treiber gegen `pruefstand.STANDARD` geprüft: Profil
  `ENTW-2026-10` mit `bootstrap_B=1000, h3_mc=1000, eps_ctrl_datensaetze=1000` (H2- und E3-Replikate folgen B),
  Profil-Hash `49dc74ab…14352` gleich dem Altlauf; Plan n₀ = 20, n_pilot = 20, n = 24 Blöcke, übrige Planwerte Vorgabe;
  n_min = 18; Basis-Seed 20261016; Hauptstufe L1. Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1 wie im Altlauf.
- **Werkzeug 8: wiederverwendet, nicht rekonstruiert.** Die vollständige Ausgabe des Altlaufs (`pruefstand.json` und
  `.npz` vom 16.10.2026, SHA-256 `fdfe9229…d468` und `d1a57008…5449`, Kennung `SYNTH-PRUEFSTAND-20261016`, Code
  `7a259ef`) war im Arbeitsbereich erhalten; ihre kompakte Fassung ist feldgleich mit der versionierten Datei. Daraus
  stammen die vollständigen Werte A4 (c_H1 = 3,7093 nach Pool-Regel, Prüfrate 18/193; c_H1Z = 3,8065; Bias und
  Unsicherheiten der Summe und Zellen; Perzentilintervall 0,95) und V1-G0 (c_H1 = 3,6589, nicht gepoolt; c_H1Z = 3,6704),
  je mit Kalibrierung N01-A4/L1 200 + 200 bzw. N01-V1G0/L1 60 + 60 Kampagnen, Rollen `kalibrierung_c`/`pruefung_c`,
  Seed 20261016. Die Codeänderungen `7a259ef` → `dd7676e` betreffen E3 (mit Teil B `nr5.unsicherheit` und den
  Kettenrichtungen von P0.4), die Nullkontrolle, Stufe 1, den Planungshaken und Metadaten; der neue Zufallsstrom `E3/T`
  steht am Ende der Reihenfolge, die übrigen Ströme bleiben gleich. c, Rauschbias, H1 und H2 rechnen unverändert.
  Bestätigt wird die Wiederverwendung durch gleiche H1/H2- und Gültigkeitszähler an allen Punkten und bitgleiches
  max|z⁰| aller 200 Prüfkampagnen von N01-A4/L1. Gespeichert:
  [`werkzeug8_A4`](werkzeug8_A4.json) und [`werkzeug8_V1G0`](werkzeug8_V1G0.json) mit NPZ-Begleiter und Herkunft im
  Kopf. Eine Kalibrierrekonstruktion war nicht nötig; Kalibrierkampagnen wurden keine gerechnet.
- **Testvorgabe nur wie im Altversuch**: E04-kette/L1 sowie N01-A4/L0, L2 und L4 (Aufruf mit `werkzeug8=None`; die
  erzeugten Werte stehen in [`werkzeug8_testvorgabe`](werkzeug8_testvorgabe.json)). Für alle anderen Aufträge bricht
  der Treiber ohne vollständige Werkzeug-8-Datei ab.
- **Seeds.** Bestehende Ableitung `unterseed(20261016, Rolle, Szenario, Stufe, i)`; die Auftragsliste nennt alle Seeds.
  N01-A4/L1 verwendet die Prüfkohorte der Kalibrierung (Rolle `pruefung_c`, dieselbe wie bei den alten 14/200); die
  übrigen zehn Punkte haben dieselben Seedlisten wie der Altlauf; K19 `unterseed(20261016, 'ebenen', 'N01-A4', 'L1', i)`.
- **Umfang.** K12: Planungsschritt wie im Altlauf (2 simulierte Aufrufe × 2 Kandidaten × (4 Kalibrier- + 4
  Prüfkampagnen), bei k = 30, n_min = 24 nach Pool-Regel dieselben 4 Prüfseeds erneut ausgewertet, dazu die
  Pilotkampagne). K19: 4 Kampagnen je Ebene (Ebene Z je 811 Rohläufe durch Stufe 1). E3: 570 Prüfkampagnen an 11
  Punkten. Keine weiteren Szenarien, Stufen oder Kalibrierungen.
- **Laufzeiten** (4 Arbeitsprozesse mit je einem BLAS-Thread, 4 Kerne): 06:51:28–07:14:32 UTC, zusammen 1384 s
  (23 min). K12 146,9 s (Altlauf 140,3 s), K19 265,5 s, E3 N01-A4/L1 277,3 s (200 Kampagnen), die übrigen E3-Punkte
  55–100 s je Punkt (Einzelwerte in [`ergebnisse.json`](ergebnisse.json)). Jede Rechnung hat einen Checkpoint mit
  Schlüssel; ein zweiter Aufruf übernimmt alle 13 ohne neue Rechnung.

## 2 K12: Planungshaken mit dem Plan des Kandidaten

Ausgeführt über `pruefstand.ausfuehren(…, schritte=['planung'], prozesse=4)`, gleichwertig mit
`python3 code/pcmms_auswertung harness pruefstand --schritte planung --prozesse 4 --ausgabe
/tmp/pcmms-ap13-neulaeufe-20261017/planung`. Wirksame Vorgaben, vorher und nachher gegen die Auftragsliste geprüft:
n_planung = (4, 4), Kandidaten n_min ∈ {18, 24}, n₀ = 20, planung_max_aufrufe = 2; Zeitangaben T_park = 2 s,
T_ramp = 2 s, T_ab = 1 s, T_e,P = 4 s, T_a,P = 10 s, T_verfügbar = 4 Tage, d = 2, N_K = 21, N_I = 0
(Entwicklungsannahmen, keine Teil-B-Werte). Raster, Kandidaten und Aufrufzahl sind nicht erweitert.

<!-- tabelle:k12 -->
| Zählung | alt | neu |
|---|---:|---:|
| Aufrufe des Haken (Paare k, N_z) | 28 | 28 |
| davon simuliert | 2 | 2 |
| Kandidaten simuliert | 4 | 4 |
| Kandidaten übersprungen (n > n_max) | 0 | 0 |
| Aufrufe nicht gerechnet (Aufrufgrenze 2) | 26 | 26 |
| Kandidaten nicht gerechnet (Aufrufgrenze) | 52 | 52 |
| Aufrufe ohne Kandidaten aus anderem Grund | 0 | 0 |

| Kandidat | Stand | N_z | T_a [s] | T_e [s] | T_Lauf [s] | Messtage | n = n_min + r | n_max | c_H1 | H2-Intervall | P(H1 ∧ H2) | erfüllt |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|---|---|---|
| k = 30, n_min = 18, n₀ = 20 | alt | 100 | – | – | 17 | 1 | 18 + 2 | – | 3.782 | perzentil_0.95 | 1/4 (0.25 ± 0.22) | nein |
| k = 30, n_min = 18, n₀ = 20 | neu | 100 | 10.0 | 1.0 | 16.0 | 2 | 18 + 2 (n_Blöcke 20) | 743 | 2.241 | perzentil_0.95 | 0/4 (0.00 ± 0.00) | nein |
| k = 30, n_min = 24, n₀ = 20 | alt | 100 | – | – | 17 | 1 | 24 + 2 | – | – | perzentil_0.95 | 0/4 (0.00 ± 0.00) | nein |
| k = 30, n_min = 24, n₀ = 20 | neu | 100 | 10.0 | 1.0 | 16.0 | 2 | 24 + 2 (n_Blöcke 26) | 743 | 2.803 | perzentil_0.95 | 1/4 (0.25 ± 0.22) | nein |
| k = 29, n_min = 18, n₀ = 20 | alt | 100 | – | – | 17 | 1 | 18 + 2 | – | – | – | 0/4 (0.00 ± 0.00) | nein |
| k = 29, n_min = 18, n₀ = 20 | neu | 100 | 10.0 | 1.0 | 16.0 | 2 | 18 + 2 (n_Blöcke 20) | 743 | – | perzentil_0.95 | 0/4 (0.00 ± 0.00) | nein |
| k = 29, n_min = 24, n₀ = 20 | alt | 100 | – | – | 17 | 1 | 24 + 2 | – | – | – | 0/4 (0.00 ± 0.00) | nein |
| k = 29, n_min = 24, n₀ = 20 | neu | 100 | 10.0 | 1.0 | 16.0 | 2 | 24 + 2 (n_Blöcke 26) | 743 | – | perzentil_0.95 | 0/4 (0.00 ± 0.00) | nein |

Suchergebnis alt: kein zulässiger Arbeitspunkt unter diesen Annahmen (kein Paar (k, T_a) erfüllt n = n_min + r ≤ n_max); neu: kein zulässiger Arbeitspunkt unter diesen Annahmen (kein Paar (k, T_a) erfüllt n = n_min + r ≤ n_max).
<!-- /tabelle -->

Lesart: Die Pilotsuche ruft den Haken für k = 30 bis 3 bei N_z = 100 auf (κ = 1,0911); nur die ersten beiden Aufrufe
werden simuliert. „Alt“ simulierte für jeden Kandidaten den Grundplan (N_z = 100, T_Lauf = 17 s, 1 Messtag), „neu“ den
Plan des Kandidaten. Die Werte c_H1 und das H2-Intervall stammen aus je 4 + 4 Kampagnen und sind nur Funktionsnachweis;
c_H1 fehlt (–), wenn keine Kalibrierkampagne alle Tests vollständig hatte. Der Begründungstext der Suche („kein Paar
… erfüllt n = n_min + r ≤ n_max“) nennt die Budgetbedingung; tatsächlich scheitert die Suche daran, dass kein simulierter
Kandidat P ≥ 0,8 erreicht (n = 20 bzw. 26 ≤ n_max = 743), und an der Aufrufgrenze für die übrigen Paare. n_max und T_e
der Paare stehen erst seit diesem Lauf in der Ausgabe (`paare`); für den Altlauf sind sie nicht gespeichert, der
Pilotteil der Suche ist von Korrektur A aber nicht berührt.

## 3 K19: verrauschter Ebenenvergleich Z ↔ H

`ebenen.vergleich_verrauscht('N01-A4', 'L1', …, 4 Kampagnen, Basis-Seed 20261016, …, werkzeug8=A4)`; Ebene Z
vollständig durch die Dateikette und Stufe 1 (Verarbeitungsstand `stufe1-0.2` in allen 4 × 811 Zusammenfassungen, ⟨N⟩
als Zeitmittel nach A1), Ebene H mit getrennten Zufallsströmen. Die Rohzeitreihen wurden nach der Auswertung gelöscht.

<!-- tabelle:k19 -->
| Größe | Z alt | H alt | rel. alt | Z neu | H neu | rel. neu |
|---|---:|---:|---:|---:|---:|---:|
| F_min | 0.000995082 | 0.000981409 | +1.39 % | 0.000995082 | 0.000981409 | +1.39 % |
| Re N1 | 0.00146124 | 0.00148343 | -1.50 % | 0.00146124 | 0.00148343 | -1.50 % |
| Im N1 | 0.00142811 | 0.00141345 | +1.04 % | 0.00142811 | 0.00141345 | +1.04 % |
| Re N2 | 0.000512548 | 0.000512252 | +0.06 % | 0.000512548 | 0.000512252 | +0.06 % |
| Im N2 | 0.000497377 | 0.000499443 | -0.41 % | 0.000497377 | 0.000499443 | -0.41 % |
| Re N3 | 0.00027617 | 0.000276103 | +0.02 % | 0.00027617 | 0.000276103 | +0.02 % |
| Im N3 | 0.000171313 | 0.000175775 | -2.54 % | 0.000171313 | 0.000175775 | -2.54 % |

Alle |rel.| ≤ 5 %: alt ja, neu ja. u_c-Mediane neu bitgleich alt: Ebene Z ja, Ebene H ja.

| Ausgang | Z alt | H alt | Z neu | H neu | innerhalb 2 SE alt / neu |
|---|---|---|---|---|---|
| H1: bestätigt | 4/4 | 4/4 | 4/4 (1.00 ± 0.00) | 4/4 (1.00 ± 0.00) | ja / ja |
| H1: falsifiziert | 0/4 | 0/4 | 0/4 (0.00 ± 0.00) | 0/4 (0.00 ± 0.00) | ja / ja |
| H1: nicht entscheidbar | 0/4 | 0/4 | 0/4 (0.00 ± 0.00) | 0/4 (0.00 ± 0.00) | ja / ja |
| H1Z: bestätigt | 4/4 | 4/4 | 4/4 (1.00 ± 0.00) | 4/4 (1.00 ± 0.00) | ja / ja |
| H1Z: falsifiziert | 0/4 | 0/4 | 0/4 (0.00 ± 0.00) | 0/4 (0.00 ± 0.00) | ja / ja |
| H1Z: nicht entscheidbar | 0/4 | 0/4 | 0/4 (0.00 ± 0.00) | 0/4 (0.00 ± 0.00) | ja / ja |
| H2: bestätigt | 4/4 | 4/4 | 4/4 (1.00 ± 0.00) | 4/4 (1.00 ± 0.00) | ja / ja |
| H2: falsifiziert | 0/4 | 0/4 | 0/4 (0.00 ± 0.00) | 0/4 (0.00 ± 0.00) | ja / ja |
| H2: nicht entscheidbar | 0/4 | 0/4 | 0/4 (0.00 ± 0.00) | 0/4 (0.00 ± 0.00) | ja / ja |
| H4: bestätigt | 4/4 | 4/4 | 4/4 (1.00 ± 0.00) | 4/4 (1.00 ± 0.00) | ja / ja |
| H4: falsifiziert | 0/4 | 0/4 | 0/4 (0.00 ± 0.00) | 0/4 (0.00 ± 0.00) | ja / ja |
| H4: nicht entscheidbar | 0/4 | 0/4 | 0/4 (0.00 ± 0.00) | 0/4 (0.00 ± 0.00) | ja / ja |
<!-- /tabelle -->

Die Gleichheit bis aufs Bit auf beiden Ebenen zeigt, dass in diesen vier Kampagnen keine für u_c wirksame Entscheidung
(Gültigkeit, Auswahl der Läufe) durch das Zeitmittel gekippt ist: u_c folgt aus den Harmonischen, und bei gleichen
Periodendauern stimmen Zeit- und Phasenmittel bis auf Rundung überein. Der 5-%-Vergleich ist unverändert eingehalten.
Mit vier Kampagnen bleibt K19 Entwicklungsdiagnostik; der rauschfreie Abgleich ist nicht wiederholt (vorhandene Prüfung
und Tests).

## 4 E3 mit fortgepflanzter Unsicherheit von T

Je Punkt `kampagnen.ausfuehren` mit Rolle, Seeds und Werkzeug 8 der Auftragsliste; E3 in AP-12 mit T-Ziehungen aus
Teil B `nr5.unsicherheit` (Modell `e3_T-0.2`, Format `e3_T_unsicherheit-0.1`, B = 1000 Ziehungen je Kampagne, eigener
Strom `E3/T`). Nenner sind alle Kampagnen eines Punktes; Kampagnen ohne dreiwertige Bewertung stünden getrennt mit Grund
(hier keine). Die MC-Fehler sind √(p(1 − p)/n) je Rate; alte und neue Rate beruhen auf denselben Kampagnen (gleiche
Seeds), Δ ist also eine Methodenänderung an denselben Kampagnen.

### 4.1 Raten alt und neu

<!-- tabelle:e3 -->
| Punkt | Rolle, n | Werkzeug 8 | auffällig alt → neu | unauffällig alt → neu | unbestimmt alt → neu | ohne dreiwertige Bewertung neu |
|---|---|---|---|---|---|---|
| N01-A4/L1 | pruefung_c, 200 | A4 | 0/200 (0.000 ± 0.000) → 0/200 (0.000 ± 0.000); Δ +0.000 | 14/200 (0.070 ± 0.018) → 14/200 (0.070 ± 0.018); Δ +0.000 | 186/200 (0.930 ± 0.018) → 186/200 (0.930 ± 0.018); Δ +0.000 | 0/200 |
| A06-phase/L1 | pruefung, 30 | V1-G0 | 30/30 (1.000 ± 0.000) → 30/30 (1.000 ± 0.000); Δ +0.000 | 0/30 (0.000 ± 0.000) → 0/30 (0.000 ± 0.000); Δ +0.000 | 0/30 (0.000 ± 0.000) → 0/30 (0.000 ± 0.000); Δ +0.000 | 0/30 |
| H03-phase/L1 | pruefung, 30 | V1-G0 | 30/30 (1.000 ± 0.000) → 30/30 (1.000 ± 0.000); Δ +0.000 | 0/30 (0.000 ± 0.000) → 0/30 (0.000 ± 0.000); Δ +0.000 | 0/30 (0.000 ± 0.000) → 0/30 (0.000 ± 0.000); Δ +0.000 | 0/30 |
| E04-kette/L1 | pruefung, 30 | testvorgabe | 30/30 (1.000 ± 0.000) → 30/30 (1.000 ± 0.000); Δ +0.000 | 0/30 (0.000 ± 0.000) → 0/30 (0.000 ± 0.000); Δ +0.000 | 0/30 (0.000 ± 0.000) → 0/30 (0.000 ± 0.000); Δ +0.000 | 0/30 |
| E07-verstaerkung/L1 | pruefung, 40 | A4 | 0/40 (0.000 ± 0.000) → 0/40 (0.000 ± 0.000); Δ +0.000 | 6/40 (0.150 ± 0.056) → 6/40 (0.150 ± 0.056); Δ +0.000 | 34/40 (0.850 ± 0.056) → 34/40 (0.850 ± 0.056); Δ +0.000 | 0/40 |
| E07-basisdrift/L1 | pruefung, 40 | A4 | 36/40 (0.900 ± 0.047) → 36/40 (0.900 ± 0.047); Δ +0.000 | 0/40 (0.000 ± 0.000) → 0/40 (0.000 ± 0.000); Δ +0.000 | 4/40 (0.100 ± 0.047) → 4/40 (0.100 ± 0.047); Δ +0.000 | 0/40 |
| N03-ungleich/L1 | pruefung, 40 | A4 | 0/40 (0.000 ± 0.000) → 0/40 (0.000 ± 0.000); Δ +0.000 | 3/40 (0.075 ± 0.042) → 3/40 (0.075 ± 0.042); Δ +0.000 | 37/40 (0.925 ± 0.042) → 37/40 (0.925 ± 0.042); Δ +0.000 | 0/40 |
| N03-N3bindet/L1 | pruefung, 40 | A4 | 0/40 (0.000 ± 0.000) → 0/40 (0.000 ± 0.000); Δ +0.000 | 40/40 (1.000 ± 0.000) → 40/40 (1.000 ± 0.000); Δ +0.000 | 0/40 (0.000 ± 0.000) → 0/40 (0.000 ± 0.000); Δ +0.000 | 0/40 |
| N01-A4/L0 | pruefung, 40 | testvorgabe | 0/40 (0.000 ± 0.000) → 0/40 (0.000 ± 0.000); Δ +0.000 | 40/40 (1.000 ± 0.000) → 40/40 (1.000 ± 0.000); Δ +0.000 | 0/40 (0.000 ± 0.000) → 0/40 (0.000 ± 0.000); Δ +0.000 | 0/40 |
| N01-A4/L2 | pruefung, 40 | testvorgabe | 0/40 (0.000 ± 0.000) → 0/40 (0.000 ± 0.000); Δ +0.000 | 0/40 (0.000 ± 0.000) → 0/40 (0.000 ± 0.000); Δ +0.000 | 40/40 (1.000 ± 0.000) → 40/40 (1.000 ± 0.000); Δ +0.000 | 0/40 |
| N01-A4/L4 | pruefung, 40 | testvorgabe | 3/40 (0.075 ± 0.042) → 3/40 (0.075 ± 0.042); Δ +0.000 | 0/40 (0.000 ± 0.000) → 0/40 (0.000 ± 0.000); Δ +0.000 | 37/40 (0.925 ± 0.042) → 37/40 (0.925 ± 0.042); Δ +0.000 | 0/40 |
<!-- /tabelle -->

### 4.2 Kampagnen ohne dreiwertige Bewertung

<!-- tabelle:e3_gruende -->
| Punkt | ohne dreiwertige Bewertung | Grund (Klasse) | Anzahl |
|---|---|---|---:|
| N01-A4/L1 | 0/200 | – | 0 |
| A06-phase/L1 | 0/30 | – | 0 |
| H03-phase/L1 | 0/30 | – | 0 |
| E04-kette/L1 | 0/30 | – | 0 |
| E07-verstaerkung/L1 | 0/40 | – | 0 |
| E07-basisdrift/L1 | 0/40 | – | 0 |
| N03-ungleich/L1 | 0/40 | – | 0 |
| N03-N3bindet/L1 | 0/40 | – | 0 |
| N01-A4/L0 | 0/40 | – | 0 |
| N01-A4/L2 | 0/40 | – | 0 |
| N01-A4/L4 | 0/40 | – | 0 |
<!-- /tabelle -->

### 4.3 Unsicherheiten und T-Ziehungen

<!-- tabelle:e3_diagnose -->
| Punkt | Kampagnen mit T-Ziehungen | unzulässige Ziehungen | Median u E3a mit / ohne T-Anteil [°] | u/u ohne T (E3a): Median, Max. | Median u(q_Z) mit / ohne T-Anteil |
|---|---|---|---|---|---|
| N01-A4/L1 | 200/200 | 0/200000 | 0.0093 / 0.0092 | 1.0057, 1.024 | 0.000296 / 0.000296 |
| A06-phase/L1 | 30/30 | 0/30000 | 0.0094 / 0.0093 | 1.0059, 1.019 | 0.000361 / 0.000361 |
| H03-phase/L1 | 30/30 | 0/30000 | 0.0093 / 0.0092 | 1.0057, 1.020 | 0.000382 / 0.000382 |
| E04-kette/L1 | 30/30 | 0/30000 | 0.0094 / 0.0093 | 1.0074, 1.035 | 0.000303 / 0.000303 |
| E07-verstaerkung/L1 | 40/40 | 0/40000 | 0.0093 / 0.0093 | 1.0055, 1.022 | 0.000300 / 0.000300 |
| E07-basisdrift/L1 | 40/40 | 0/40000 | 0.0173 / 0.0173 | 1.0017, 1.010 | 0.000589 / 0.000589 |
| N03-ungleich/L1 | 40/40 | 0/40000 | 0.0094 / 0.0093 | 1.0057, 1.026 | 0.000315 / 0.000315 |
| N03-N3bindet/L1 | 40/40 | 0/40000 | 0.0088 / 0.0087 | 1.0062, 1.024 | 0.000079 / 0.000079 |
| N01-A4/L0 | 40/40 | 0/40000 | 0.0068 / 0.0067 | 1.0110, 1.031 | 0.000036 / 0.000036 |
| N01-A4/L2 | 40/40 | 0/40000 | 0.0285 / 0.0285 | 1.0006, 1.008 | 0.001003 / 0.001003 |
| N01-A4/L4 | 40/40 | 0/40000 | 0.1691 / 0.1691 | 1.0000, 1.001 | 0.006136 / 0.006136 |
<!-- /tabelle -->

„ohne T-Anteil“: dieselben Bootstrap-Replikate mit festem T(kω) und festen Zelllagen (Diagnose aus
`kontrollen.e3_auswerten`, nicht Teil der Bewertung). Nicht gezogen und so in jeder Kampagne vermerkt: Modullagen
(Konstruktion, wie in A2.7), Kippmoden (nicht im T-Modell) und an den Punkten mit nicht identifizierbarem P0.4
(A4-System außer N03-ungleich) f_n und ζ; H(kω) ist dort ein gemeinsamer Faktor und hebt sich in E3a auf. Unvollständige
Beschreibungen: keine; betragsgespiegelte Tiefpassparameter w: Anteil 0.

### 4.4 Alte Lesart und bestimmende Prüfgrößen

<!-- tabelle:e3_lesart -->
| Punkt | historisch auff. / unauff. / unbest. | alte Lesart nachgerechnet (u ohne T-Anteil) | gleich | bestimmend bei „auffällig“ | bestimmend bei „unbestimmt“ |
|---|---|---|---|---|---|
| N01-A4/L1 | 0 / 14 / 186 | 0 / 14 / 186 | ja | – | E3b 186 |
| A06-phase/L1 | 30 / 0 / 0 | 30 / 0 / 0 | ja | E3a 27, beide 3 | – |
| H03-phase/L1 | 30 / 0 / 0 | 30 / 0 / 0 | ja | beide 30 | – |
| E04-kette/L1 | 30 / 0 / 0 | 30 / 0 / 0 | ja | E3a 30 | – |
| E07-verstaerkung/L1 | 0 / 6 / 34 | 0 / 6 / 34 | ja | – | E3b 34 |
| E07-basisdrift/L1 | 36 / 0 / 4 | 36 / 0 / 4 | ja | E3b 36 | E3b 4 |
| N03-ungleich/L1 | 0 / 3 / 37 | 0 / 3 / 37 | ja | – | E3b 37 |
| N03-N3bindet/L1 | 0 / 40 / 0 | 0 / 40 / 0 | ja | – | – |
| N01-A4/L0 | 0 / 40 / 0 | 0 / 40 / 0 | ja | – | – |
| N01-A4/L2 | 0 / 0 / 40 | 0 / 0 / 40 | ja | – | E3b 2, beide 38 |
| N01-A4/L4 | 3 / 0 / 37 | 3 / 0 / 37 | ja | E3a 1, E3b 2 | beide 37 |
<!-- /tabelle -->

„bestimmend“: bei „auffällig“ die Prüfgrößen über der Schwelle (x − z_B·u > s), bei „unbestimmt“ die, die
„unauffällig“ verfehlen (x + 1,645·u > s); Schwellen des Entwicklungsprofils 0,1° (E3a) und q_tol = 0,00058 (E3b). Die
Nachrechnung ist eine Gegenprobe der Zuordnung, keine alten Einzelbefunde: Der Altlauf hat E3 je Kampagne nicht
gespeichert, Übergänge je Kampagne werden deshalb nicht berichtet.

### 4.5 Kontrollgrößen H1, H2 und Gültigkeit

<!-- tabelle:e3_kontrollen -->
| Punkt | H1 bestätigt alt / neu | H2 bestätigt alt / neu | H1 ∧ H2 alt / neu | ungültig G1, G4 alt / neu | Kontrollen gleich | Seeds bzw. Kohorte |
|---|---|---|---|---|---|---|
| N01-A4/L1 | 193/200 / 193/200 | 194/200 / 194/200 | 193/200 / 193/200 | 759/126000 / 759/126000; 2938/126000 / 2938/126000 | ja | max|z⁰| bitgleich 200/200 |
| A06-phase/L1 | 23/30 / 23/30 | 23/30 / 23/30 | 23/30 / 23/30 | 113/18900 / 113/18900; 778/18900 / 778/18900 | ja | Seeds gleich |
| H03-phase/L1 | 24/30 / 24/30 | 25/30 / 25/30 | 24/30 / 24/30 | 100/18900 / 100/18900; 663/18900 / 663/18900 | ja | Seeds gleich |
| E04-kette/L1 | 22/30 / 22/30 | 22/30 / 22/30 | 22/30 / 22/30 | 109/18900 / 109/18900; 836/18900 / 836/18900 | ja | Seeds gleich |
| E07-verstaerkung/L1 | 37/40 / 37/40 | 38/40 / 38/40 | 37/40 / 37/40 | 188/25200 / 188/25200; 644/25200 / 644/25200 | ja | Seeds gleich |
| E07-basisdrift/L1 | 39/40 / 39/40 | 39/40 / 39/40 | 39/40 / 39/40 | 184/25200 / 184/25200; 455/25200 / 455/25200 | ja | Seeds gleich |
| N03-ungleich/L1 | 34/40 / 34/40 | 34/40 / 34/40 | 34/40 / 34/40 | 166/25200 / 166/25200; 934/25200 / 934/25200 | ja | Seeds gleich |
| N03-N3bindet/L1 | 40/40 / 40/40 | 40/40 / 40/40 | 40/40 / 40/40 | 136/25200 / 136/25200; 254/25200 / 254/25200 | ja | Seeds gleich |
| N01-A4/L0 | 37/40 / 37/40 | 37/40 / 37/40 | 37/40 / 37/40 | 213/25200 / 213/25200; 554/25200 / 554/25200 | ja | Seeds gleich |
| N01-A4/L2 | 38/40 / 38/40 | 38/40 / 38/40 | 38/40 / 38/40 | 158/25200 / 158/25200; 533/25200 / 533/25200 | ja | Seeds gleich |
| N01-A4/L4 | 40/40 / 40/40 | 0/40 / 0/40 | 0/40 / 0/40 | 133/25200 / 133/25200; 316/25200 / 316/25200 | ja | Seeds gleich |
<!-- /tabelle -->

Alle Kontrollgrößen sind gleich; Änderungen außerhalb von E3 gibt es nicht. Die Wahrheit (Klasse) je Punkt ist
unverändert.

**Nicht neu gerechnete E3-Zahlen** bleiben historische Ergebnisse ohne T-Unsicherheit: die übrigen Szenarien von A4
(A04-R1 bis R4, H01-zelt, H-fehlend, N04-laufart, N05-F/N2/N3, S02-kontrolllauf, S06-saettigung, S-indexfehler), V1
(I01, I02, I04, I05), die eigenen Systeme C03, C04, A07 sowie die Prüfsimulationen von V1-G0 und V1-G60h.

## 5 Grenzen

- **Entwicklungsannahmen.** Zeitangaben der Planung, Entwicklungsprofil mit gewählten, nicht festgelegten Optionen,
  Entwicklungsplan (n = 24, n_min = 18, nicht nach §5.4 geplant), B = 1000 statt 10 000 Replikate, 4–200 statt ≥ 1000
  Kampagnen je Szenario und Stufe. K12 mit 4 + 4 Kampagnen je Kandidat und K19 mit 4 Kampagnen je Ebene sind
  Funktions- und Konsistenzprüfungen.
- **Planung ohne Pilotkovarianz-Anbindung.** Die Planungssimulation nutzt das Rauschmodell des Szenarios, skaliert auf
  die obere 80-%-Grenze; ein aus gemessenen Pilotkovarianzen gespeister Generator fehlt (für Teil B nötig). Die
  Power-Bedingung (Regel `planung.power`) ist offen und nicht geprüft.
- **T-Modell.** Ohne Kippmoden; Modullagen ohne Unsicherheit; bei nicht identifizierbarem P0.4 bleibt H(kω) nominal.
- **Kreuzkovarianzen.** Getrennte Kalibriermessungen ohne Kreuzkovarianz im Format werden als unabhängig gezogen; ein
  kanalweise verschiedener gemeinsamer Fehler ist nicht abgebildet.
- **Kleiner T-Anteil als Eigenschaft der Synthetik.** Die synthetischen Kalibrierungen sind sehr genau; dass T die Raten
  hier nicht verschiebt, sagt nichts über reale Kalibrierungen.
- **Offene Fachregeln.** E3-Schwellen, Prüfmenge und Rückfall (§12), G4 und Pilotreserve, die Lesart des
  Drift-Zusatzes und die Planungsregeln bleiben offen; aus diesen Läufen folgt keine Entscheidung dazu.
- **Ebenenabgleich.** Der Generator der Ebene Z hat gleiche Periodendauern; ungleiche Perioden, an denen sich Zeit- und
  Phasenmittel unterscheiden, prüft K19 in dieser Form nicht.

## 6 Dateien und Wiederholung

| Datei | Inhalt |
|---|---|
| [`auftrag.json`](auftrag.json) | Auftragsliste: 13 Aufträge mit Szenario, Stufe, Rolle, allen Seeds, Werkzeug-8-Quelle, Kampagnenzahl; gemeinsame Einstellungen und Profil-Hash |
| [`werkzeug8_A4.json`](werkzeug8_A4.json), [`werkzeug8_V1G0.json`](werkzeug8_V1G0.json) (+ `.npz`) | vollständige, unveränderte Werkzeug-8-Werte des Altlaufs mit Herkunft im Kopf |
| [`werkzeug8_testvorgabe.json`](werkzeug8_testvorgabe.json) (+ `.npz`) | die vom Harness erzeugte Testvorgabe (nur Dokumentation) |
| [`altstand_auszug.json`](altstand_auszug.json) | Vergleichswerte des Altlaufs mit MC-Fehlern, Seedlisten, u_c-Mediane von K19, Planungsaufrufe, max|z⁰| der Prüfkohorte; Prüfsummen der Quelle |
| [`ergebnisse.json`](ergebnisse.json) | kompakte Ergebnisse mit Herkunft (Rechen-Commit, Rechencode-Hash, Auftrag, Profil, Werkzeug 8, Bibliotheken, Laufzeiten) |
| [`kampagnen_e3.csv`](kampagnen_e3.csv) | eine Zeile je E3-Kampagne (570): Bewertung, Grund, alte Lesart, Prüfgrößen, T-Diagnose, H1/H2, Gültigkeit |
| [`laufprotokoll.txt`](laufprotokoll.txt) | Protokoll des Laufs mit Start- und Endzeiten je Auftrag |

```bash
python3 code/pcmms_auswertung harness neulauf             # Rechnung; Checkpoints unter /tmp/pcmms-ap13-neulaeufe-20261017
python3 code/pcmms_auswertung harness neulauf --bericht   # ergebnisse.json, kampagnen_e3.csv und Tabellen dieses Berichts
```

Die Checkpoints (Kampagnenbefunde mit Feldern, Planungs- und Ebenenausgabe) liegen nicht im Repository. Ein Aufruf
übernimmt einen Checkpoint nur bei gleichem Rechencode, Auftrag, Profil, Werkzeug 8, gleichen Seeds und Bibliotheken
und rechnet sonst neu. Die Auftragsliste und die Werkzeug-8-Dateien entstanden einmalig mit
`harness neulauf --vorbereiten <vollständige Altausgabe>`; die Altausgabe selbst ist nicht versioniert.
