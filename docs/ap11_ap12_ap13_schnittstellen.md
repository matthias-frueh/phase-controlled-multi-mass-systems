# Schnittstellen der Softwarestufe AP-11, AP-12 und AP-13

Stand 16.10.2026 · Paket [`code/pcmms_auswertung/`](../code/pcmms_auswertung/) · Lizenz dieses Dokuments CC BY 4.0, Code MIT.
*Entwicklungsschnittstelle für synthetische Daten, keine Messdaten.* Das Format legt das Rohdatenformat der
Aufnahmesoftware (AP-10) nicht fest; Teil B wird hier nur synthetisch gefüllt und behauptet keine Registrierung.

Regelgrundlage: [Präregistrierung v2](praeregistrierung_v2_entwurf.md) mit [Anhang](praeregistrierung_v2_anhang.md);
Feldliste und Trennstelle nach [Plan AP-13](plan_ap13_pipelinetest.md), Abschnitt 2.6, soweit sein Anhang „Abgleich mit
`main`“ ihn nicht überholt. Regeln mit Status: [`ap11_ap12_ap13_regelmatrix.md`](ap11_ap12_ap13_regelmatrix.md).
Umfang und Prüfergebnisse: [`ap11_ap12_ap13_software.md`](ap11_ap12_ap13_software.md).

> **Vermerk vom 16.10.2026 (Korrekturen A–E).** Geänderte Felder und Bedeutungen: Zeitmittel ⟨N⟩ der
> Laufzusammenfassung ab `stufe1-0.2` (Abschnitt 4), Kettenrichtungen in P0.4 und Unsicherheitsbeschreibung von T in
> Teil B `nr5` (Abschnitt 5), Strom `E3/T` (Abschnitt 7), Nullkontrolle ohne definierten Test, E3 mit T-Ziehungen und
> Verarbeitungsstand im Ergebnis (Abschnitt 8), Planungshaken mit dem Plan des Kandidaten (Abschnitt 5). Ältere
> Dateien bleiben lesbar und werden nicht als neu berechnet behandelt.

## 1 Trennstelle

```python
from pcmms_auswertung import auswertung
laufzusammenfassung(laufdatei, kalibrierung, teil_b) -> Laufzusammenfassung        # Stufe 1, A9.4 Schritte 1–6
auswerten(zusammenfassungen, kalibrierung, teil_b, regeln,
          seed=None, bootstrap_indizes=None) -> Ergebnis                            # Stufe 2, A9.4 Schritt 7, §8, §9
auswerten_manifest(manifest, kalibrierung, teil_b, regeln, seed=None) -> Ergebnis  # Stufe 1 + 2
```

Stufe 1 verarbeitet Rohdaten; Stufe 2 braucht keine Zeitreihen, weil die Konfigurationsmittelkurve bandbegrenzt und
durch ⟨N⟩ und N_k (k ≤ k_max) bestimmt ist (A9.4 Schritt 5). AP-13 erzeugt auf **Ebene Z** Rohdateien (Weg über
Stufe 1) und auf **Ebene H** dieselben Laufzusammenfassungen direkt. `kalibrierung` ist das Ergebnis von AP-11
(Werkzeug 4) und die einzige Quelle der H3-Eingänge; `teil_b` liefert die registrierten Werte (A9.3); `regeln` ist ein
Regelprofil (Abschnitt 6).

## 2 Konventionen

| Gegenstand | Festlegung |
|---|---|
| Einheiten | SI: N, m, s, kg, Hz; Temperaturen in °C; Rohwerte der Kraftkanäle in ADC-Einheiten |
| Harmonische | N_k = (2/N_θ)·Σₙ N̄(θₙ)·e^{−ikθₙ}, k ≥ 1, θₙ = 2πn/N_θ, N_θ = 2000; N̄(θ) = ⟨N⟩ + Σ_k Re(N_k·e^{ikθ}); \|N_k\| wie `linear_solver.py --section` |
| Komplexe Zahlen | NPZ: complex128; JSON: Paare [Re, Im] |
| Vorzeichen | Kräfte positiv nach oben auf die Zellen (Druck); Phasenverzögerung φ eines Moduls ergibt den Faktor e^{−ikφ} |
| Phasenbezug | θ = 0 am Indeximpuls von Modul 1 (Kombinationsläufe, D2), von Modul j (Lⱼ, Lⱼ′), virtueller Takt mit f (Referenzläufe); Indexphase φⱼ,c = 2π·(t_idx,j − t_idx,1)/T_c mod 2π (A1); Profilphase φⱼ^P = φⱼ + Δδⱼ |
| Grad/Radiant | Dateien und Schnittstellen in Grad, Rechnung intern in Radiant |
| Indizes | Zellen c = 1, 2, 3 und Module j = 1, 2, 3 stehen in Feldern an den Stellen 0, 1, 2; Harmonische k = 1 … k_voll an den Stellen 0 … k_voll − 1 |
| H1-Größen | Reihenfolge F_min − ⟨N⟩, Re N₁, Im N₁, Re N₂, Im N₂, Re N₃, Im N₃; Punkte nach φ₂ aufsteigend |
| Konfigurationen | Kennungen R, L1 … L3, S100 … S140 (Schnitt), Z0_0, Z0_180, P110_250 …, I116 …; Einstellung 2 mit „′“ (L1′, I116′) |
| Reihenfolge gültiger Läufe | aufsteigende Position in der Laufreihenfolge (Grundlage der Bootstrap-Indizes) |
| Fehlende Werte | nan in Feldern, null in JSON, mit Nennung in `fehlende_kanaele`; nie durch Nullen ergänzt |
| Bandbegrenzung | Laufzusammenfassungen tragen k = 1 … k_voll (k_voll ≥ k_max); Stufe 2 schneidet bei k_max aus Teil B ab; Bedingung (a) von §5.3 nutzt die ungebänderten Zellharmonischen |

## 3 Pflichtmetadaten, Datenarten, Versionen

Jede Datei ist ein JSON-Objekt `{"kopf": …, "inhalt": …}` und gegebenenfalls eine NPZ-Datei gleichen Namens. Der Kopf
enthält `schema` (`pcmms.<art>`), `schema_version`, `datenart`, `kennung`, `registrierung`, `erzeugt_von`,
`code_version` (Paketversion, Git-Stand) und bei NPZ `daten` (Datei, SHA-256, Datentyp und Form jedes Felds).
Fehlende oder unbekannte Schemata und Versionen werden zurückgewiesen (`FormatFehler`), ebenso eine abweichende
Prüfsumme oder Feldform. Synthetische Daten tragen `datenart = "synthetisch"`, eine Kennung mit `SYNTH-` und
`registrierung = "keine (synthetisch)"`. Messdaten (`datenart = "messung"`) weist diese Stufe zurück; eine Auswertung
mischt nie beide Arten. NPZ-Dateien werden deterministisch geschrieben (feste ZIP-Zeitstempel, sortierte Schlüssel):
Gleiche Eingaben und Seeds ergeben bitgleiche Dateien.

| Art | Inhalt | Schreibt | Liest |
|---|---|---|---|
| `rohlauf` | Rohdatei eines Laufs der Ebene Z (Abschnitt 4) | Generator Ebene Z | Stufe 1 |
| `manifest` | eine Zeile je Lauf: Dateien, SHA-256, Laufart, Konfiguration, Block, Reihenfolge, Online-Gültigkeit | Generator | Stufe 1 |
| `p0_messung` | synthetische Messdaten von P0.1 (Kennlinien, Laststellen, Querkraft, Brückensimulator), P0.2 (Zelllasten, Bauteilwägung), P0.4 (Übertragungsfunktionen mit Kohärenz, zwei Amplituden, exzentrisch, Betriebslast), P0.5 (Weg, Indeximpulse) | Generator | AP-11 |
| `kalibrierung` | Ergebnis von Werkzeug 4 mit Unsicherheiten und Kovarianzen, Diagnosen, Eingangshashes | AP-11 | Stufe 1 (Umrechnung), Stufe 2 (H3, E3) |
| `pilot` | Ergebnis von Werkzeug 5: Streuungen, s_q, T_φ, Rauschkovarianzen, p̂, Rampen- und Einschwinginformation, Planungsstand; keine Residuen, keine Entscheidungen | AP-11 | Teil B, Planung |
| `teil_b` | synthetisches Teil B nach A9.3 (Abschnitt 5) | `teil_b.py` (Befehl `ap11 teil-b`) aus Phase-0-Zusammenfassungen, Kalibrierung, Pilot und Werkzeug-8-Werten | Stufe 2 |
| `laufzusammenfassung`, `zusammenfassungen` | ein Lauf bzw. Bündel vieler Läufe (Abschnitt 4) | Stufe 1, Ebene H | Stufe 2 |
| `regelprofil` | Profil-ID, alle Regeln mit Fundstelle, Status, Wert und Herkunft, Reduktionen | `regeln.py` | Stufe 2, Harness |
| `bootstrap_indizes` | Indexmatrizen je Quelle (Abschnitt 7) | Stufe 2, Harness | Stufe 2 |
| `ergebnis` | Ausgänge, Zusätze, Gründe, Intervalle, Grenzen, Prüfgrößen und Herkunft (Abschnitt 8) | Stufe 2 | Harness, Bericht |
| `wahrheit` | rauschfreie Erwartungswerte, wahre Residuen, Klasse der erwarteten Antwort | Generator | nur Harness |
| `werkzeug8` | Werte für Teil B nr4/nr10: c von H1 und H1Z, Rauschbias b̂⁰, b̂¹ mit u(b̂) (Summe und je Zelle), Intervalltyp von H2 mit Überdeckung, Prüfrate, jeweils mit Herkunft und Kennzeichnung „reduziert“ | Harness (`harness kalibrierung`) | `ap11 teil-b` |
| `planangaben` | Laufplan der synthetischen Kampagne (f, k_max, n_min, n₀, n, d, Einstellung 2) und Seeds von Pilot, Teil B, Bootstrap und Reihenfolge; Platzhalter für Teil B nr2 | Generator | `ap11 teil-b` |
| `bewertung`, `katalog`, `pruefsatz` | Vergleich mit der Wahrheit, Raten mit MC-Fehler, Prüfstand; Szenarienkatalog; Hashes des Software-Prüfsatzes | Harness | – |

## 4 Rohdatei und Laufzusammenfassung

**Rohdatei** (`rohdaten.py`): Inhalt `lauf` (lauf_id, laufart R/L/K/D1/D2, modul, einstellung, konfiguration mit
Profil-Sollphasen, phase, block, messtag, position, kontrollsatz, t_start), `erfassung` (f_soll, f_s, t0, ADC-Bits und
Vollausschlag, f_takt der Indexzeitstempel, Kanalliste), `protokoll` (t_rampe_ende, t_e, n_zyklen_fenster, Störung,
Aufzeichnung, Parkposition, Bediener, Notizen), `umgebung` und `einstellungen` (A9.10), bei Synthetik `generator`
(Version, Szenario, Seed; nie die Wahrheit). Daten: `kraft_adc` (3 × n), `index_modul1 … 3` (Zeitstempel; Länge 0
bei geparktem Modul, fehlender Schlüssel = fehlender Kanal), `temperatur_zellen` mit `t_temperatur`, `uebersteuerung`.
Die Abtastrate folgt aus A6 für f und k_max des Prüffalls ((π·k_max·f/f_s)²/2 ≤ 10⁻³), nicht aus einem Pauschalwert.

**Laufzusammenfassung** (`zusammenfassung.py`, Plan 2.6 b): Kopf lauf_id, laufart, modul, einstellung, konfiguration,
phase, block, messtag, position, kontrollsatz, t_start, t_ende, f_soll, f_mittel, n_zyklen, n_fuenftel, k_voll, n_theta,
stoerung, aufzeichnung_ok, park_ok, fehlende_kanaele, hash_rohdatei, version_stufe1, kalibrier_hash, ebene. Daten:
`Nk_summe` (k), `Nk_zellen` (3, k), `N_mittel`, `N_mittel_zellen` (3), `zeiger` (3, k) = Σ_c e^{−ikφⱼ,c},
`phi_mittel_grad`, `sigma_grad`, `index_fehler` (3), `fuenftel_N_mittel` (2), `fuenftel_Nk` (2, k), `min_roh_zellen`,
`max_roh_zellen` (3; ganzer Lauf einschließlich Rampe), `sigma_roh_zellen` (3) und `sigma_roh_summe` (Standardabweichung
der Rohwerte im Auswertefenster, für σ_c, σ_Σ und F_LO aus den Referenzläufen), `uebersteuert_zellen` (3),
`temperatur_min_zellen`,
`temperatur_max_zellen` (3), `t_phi` (3). Abweichend vom Plan stehen Zeiger und Harmonische für alle Läufe bis k_voll
(nicht nur bis k_max), damit Bedingung (a) ungebändert geprüft und k_max in der Pilotanalyse gewählt werden kann; die
Fünftel stehen als Harmonische, F_min − ⟨N⟩ der Fünftel bildet Stufe 2 mit k_max.

`N_mittel`, `N_mittel_zellen` und `fuenftel_N_mittel` sind ab `stufe1-0.2` Zeitmittel nach A1: Integral des linear
interpolierten Verlaufs der kalibrierten Rohwerte über die akzeptierten vollständigen Zyklusintervalle, geteilt durch
deren Gesamtdauer (Grenzen zwischen Abtastwerten interpoliert; verworfene Zyklen und Lücken weder in Zähler noch
Nenner; Fünftel nach der bisherigen Auswahl). Bis `stufe1-0.1` waren sie das Phasenmittel der resampelten Zyklen.
Die Bedeutung je `version_stufe1` steht in `zusammenfassung.MITTEL_BEDEUTUNG`; Teil B (`nr1.phase0_verarbeitung`) und
Ergebnis (`herkunft.verarbeitung`) nennen den Verarbeitungsstand, Zusammenfassungen der alten Bedeutung werden als
solche gemeldet. Ebene H liefert den Gleichanteil des Modells (gleiche Periodendauern).

## 5 Synthetisches Teil B

`teil_b.json` gliedert nach A9.3: `nr1` Herkunft (Kalibrier-, Phase-0- und Code-Hashes), `nr2` Platzhalterwerte (f,
k_max, k_voll, Δδⱼ, σ_tol, δf_tol, σ̂_ref und σ̂_ref,c, ε_ctrl mit Prüfgröße und kritischem Wert, σ_c, F_LO,c, σ_Δ je
Laufart, T_P0 und ΔT, n_min, n₀, r, n, n_max, d, p̂, Einstellung 2 mit s und I), `nr3` Einzelmodul-Harmonische der
Phase 0 je Lauf (Summe, Zellen, ungebändert) mit den Indexmatrizen B⁰ⱼ als feste Eingabe von Bootstrap B und H2
(die Replikate folgen daraus), `nr4` Vorhersage an den Sollphasen, D_q, Δ_q, Δ_rel,q (Fassung B; Faktor 0,1 und
Fassung A als Sensitivität), b̂⁰, b̂¹ mit u(b̂), u_c,erw, H1Z-Größen je Zelle, `nr5` T(kω) für E3, `nr6` H2
(Fenstermittelpunkt, w, W, φ̂₂*, SNR, Intervalltyp mit Niveau und simulierter Überdeckung), `nr7` H3-Vorhersage (nur
zum Vergleich; Stufe 2 rechnet sie aus der Kalibrierung), `nr8` Prüfmenge V, `nr9` Laufreihenfolge (Seed),
`nr10` Ergebnisse von Werkzeug 8 (c von H1 und H1Z mit Prüfrate und Herkunft, Intervalltyp von H2, kritischer Wert
für ε_ctrl, Raten). Die Werkzeug-8-Werte kommen aus `harness kalibrierung` (Datei `werkzeug8`) oder ausdrücklich als
`testvorgabe` (c = c_B, b̂ = 0, Perzentilintervall; jede Herkunftsangabe trägt dann „TESTVORGABE“).
Fehlt ein benötigter Wert, meldet Stufe 2 den betroffenen Ausgang als nicht entscheidbar mit Grund.

`nr5.unsicherheit` (ab `teil_b-0.2`, Format `e3_T_unsicherheit-0.1`, Modell `e3_T-0.2`, Herkunft mit
Kalibrierungs-Hash; A9.3 Nr. 5): Nennwerte und gemeinsame Kovarianz von (g₁…g₃, x₁…x₃, y₁…y₃) aus P0.1, Parameter
und Kovarianz der Kette je Zelle, (f_n, ζ) mit statistischem Anteil, Kennzeichen „gezogen“ und den Verschiebungen je
Störrichtung der Kette aus P0.4 (`kette_richtungen`, ab `anpassung-0.2`; Reihenfolge Zelle, Spalte wie
`anpassung.kette_cholesky`), Modullagen, nicht gezogene Eingänge, unvollständige Teile und Näherungen. Teil B ohne
diese Beschreibung (älterer Stand) ergibt in E3 nur numerische Diagnostik, keine Unsicherheit null.

Planungshaken (`harness.planung.haken`, Aufruf durch das Pilotskript): Eingang k, N_z, T_a, T_e, T_Lauf, die
Zeitangaben (d, N_K, N_I), Pilotstreuungen, p̂ und n_max; der simulierte Plan erhält n_zyklen = N_z, T_lauf und
tage = d des Kandidaten (Widerspruch bei f, T_a, N_K oder N_I: Abbruch); jeder Kandidat nennt `plan_simuliert`, die
Ausgabe das `fenster`.

## 6 Regelprofil

Jede Regel trägt Fundstelle, Status (Abschnitt „Statusbegriffe“ der Regelmatrix), Wert und Herkunft. Offene Regeln
haben keinen Wert; wer sie braucht, erhält `RegelOffen`. Ergebnisse nennen Profil-ID, SHA-256 des Profils, alle
wirksamen Werte mit Status sowie die offenen und nicht implementierten Regeln. Reduzierte Replikat- oder
Kampagnenzahlen ändern die Profil-ID (`…+red(bootstrap_B=200)`).

## 7 Zufallsströme und Bootstrap-Indizes

`zufall.py`: jeder Strom aus `SeedSequence(basis, spawn_key=(Schlüssel …))`; getrennte Schlüssel für Generator,
Kalibriersimulation von c, Prüfsimulation, Bootstrap, H3-, E3-Monte-Carlo und Teil B; Kampagne i eines Szenarios
erhält den Seed `zufall.unterseed(Basis, Rolle, Szenario, Stufe, i)` (Rolle: `kalibrierung_c`, `pruefung_c`,
`pruefung`, `planung` …; `zufall.katalog_seed` leitet eine Basis aus dem Katalog-Hash ab). Parallele Ausführung ändert
keine Zahl (Test `test_kampagnen_unabhaengig_von_der_prozesszahl`); es gibt keine Seed-Suche. Bootstrap-Indizes nach Plan 2.6 c: `SeedSequence(seed).spawn` in fester Reihenfolge A_i für alle
Konfigurationen in der Listenreihenfolge von Teil B, B¹₁ … B¹₃, H3, H4, danach in dieser Stufe angehängt E3 und die
Quellen bei Einstellung 2, zuletzt der Strom `E3/T` der Ziehungen von T (keine Indexmatrix; die übrigen Ströme ändern
sich dadurch nicht); je Kind `Generator(PCG64(kind)).integers(0, n, size=(B, n))` über die gültigen Läufe der
Quelle in aufsteigender Position. B⁰ⱼ stehen fest in Teil B. Übergebene `bootstrap_indizes` ersetzen die Ziehung
vollständig, mit denselben Schlüsseln (`A/<konfig>`, `B0/modul<j>`, `B1/modul<j>`, …; in NPZ mit `__` statt `/`).

## 8 Ergebnis

`ergebnis.json` enthält je Hypothese den Ausgang (`bestätigt`, `falsifiziert`, `nicht entscheidbar`) mit Gründen und
Zusätzen nach §9.3/§9.4, die verwendeten Grenzen und kritischen Werte mit Herkunft, alle Einzeltests (r⁰, r¹, u⁰, u¹,
ν⁰, ν¹, z⁰, z¹, Δ_q, Δ_rel, Bias), Sensitivitätsvarianten getrennt, H2-Intervalle mit Typ und Niveau, H3 mit
Kennzeichnung „prüft Masse, Profil, Kalibrierung“ (Fassung K), H4, Nullkontrolle mit Wortregel, Gültigkeit G1–G10 und
Abbrüche S1–S4 (offline, keine Echtzeitfunktion) mit betroffenen Läufen, numerische Prüfgrößen von H1Z, E3 und
Zuordnung mit Status, die offenen und nicht implementierten Regeln und die Herkunft (Eingangshashes, Profil, Seed,
Replikatzahlen, Codestand, Verarbeitungsstand der Laufzusammenfassungen). Dazu eine kurze Textfassung.
Ergebnisdateien enthalten keine Zeitstempel. Ist der Welch-Test der Nullkontrolle nicht definiert (beide Varianzen
null) oder eine Rechengröße nicht endlich, steht dort `pruefbar = false` mit Grund, Differenz und Stichprobenzahlen,
ohne Testaussage. E3 trägt `t_unsicherheit` (gezogen, Anteil unzulässiger Ziehungen mit Gründen, nicht gezogene
Eingänge, Näherungen) und `k2_hinweis` (k = 2 lokal, nur bis auf 180° bestimmt). Je Prüfgröße steht als Diagnose
zusätzlich u ohne T-Anteil (`u_ohne_T_grad` in E3a, `u_q_Z_ohne_T` in E3b: dieselben Replikate, T und Zelllagen fest);
die Bewertung nutzt sie nicht. Der Kurzbefund des Harness (`kampagnen.kurzbefund`) behält davon Bewertung, Status,
z_B, m, die Prüfgrößen (|Δφ_Z|, u, u ohne T-Anteil bzw. q_Z, u, u ohne T-Anteil) und die T-Diagnose; fehlt E3 ganz,
nennt `E3_grund` den Grund.

## 9 Wahrheit getrennt

Generatorausgaben liegen in `eingang/` (alles, was AP-11 und AP-12 sehen) und `wahrheit/` (nur Harness). AP-11 und
AP-12 importieren weder Generator- noch Harnessmodule, lesen keine `wahrheit`-Dateien (Schema `pcmms.wahrheit` wird von
ihren Lesefunktionen abgewiesen) und übernehmen keine wahren Parameter oder erwarteten Entscheidungen. Der Negativtest
`test_wahrheit_aendern_oder_entfernen_aendert_ap12_nicht` ändert die Wahrheit, entfernt sie und prüft, dass das Ergebnis
von AP-12 gleich bleibt (Prüfsumme ohne Laufzeit und Codestand) und eine Wahrheitsdatei als Eingang zurückgewiesen
wird.

## 10 Beispieldatensatz

```sh
python3 code/pcmms_auswertung beispiel --ausgabe /tmp/pcmms_beispiel
```

erzeugt bitgleich den eingecheckten Datensatz [`tests/fixtures/ap1x_beispiel/`](../tests/fixtures/ap1x_beispiel/):
einen Referenzlauf und einen Einzelmodullauf L₁ (je 6 Zyklen bei 10 Hz, f_s = 2110 Hz nach A6 für k_max = 3, analytisch
vorgegebene Zellharmonische k = 1 … 3, ADC 24 Bit, Indexzeitstempel auf 1 µs), Manifest (JSON und CSV), statische
Kalibrierung, das Regelprofil ENTW-2026-10, ein Beispiel für Bootstrap-Indizes und die Wahrheit unter `wahrheit/`.
SHA-256 der Datendateien:

| Datei | SHA-256 |
|---|---|
| `eingang/laeufe/B-R-001.npz` | `326d60ddf792b2dfd8fa0ac1ed2de795615465b2ff629f8a3d4fc09079125c84` |
| `eingang/laeufe/B-L1-001.npz` | `dc06ead11196e29fa453c02c39663f6a8326fb97cebbc47996f818f344313720` |
| `eingang/bootstrap_indizes.npz` | `c794b13d0b0817bfe3a1b3b230c102001a0f439292b1cb2c18ef9ba149607f68` |
| `wahrheit/wahrheit.npz` | `7435ea9ea5c5546741a4ca728fbfa58e9bf75823ce3de9182b49e89aec7ba626` |

Die JSON-Köpfe tragen den Codestand und ändern sich deshalb mit jedem Commit; ihr übriger Inhalt ist fest
(`tests/test_pcmms_formate.py`). Stufe 1 rechnet aus Rohdateien Laufzusammenfassungen, die Ebene H bis auf den
Interpolationsfehler nach A6 und die Quantisierung der Zeitstempel treffen (`tests/test_ap12_auswertung.py`,
`test_stufe1_rauschfrei_gleich_ebene_h`; `harness.ebenen.vergleich_rauschfrei`).

## 11 Ausgabestruktur der Kette

`python3 code/pcmms_auswertung kette …` bzw. die Einzelbefehle schreiben in ein frisches Zielverzeichnis:

| Pfad | Inhalt | Schreibt |
|---|---|---|
| `eingang/p0_messung`, `eingang/planangaben` | P0-Messdaten, Laufplan und Seeds | `generator` |
| `eingang/laeufe/` (Ebene Z) | Rohläufe und Manifest | `generator` |
| `eingang/zusammenfassungen` | Laufzusammenfassungen (Ebene H direkt, Ebene Z aus Stufe 1) | `generator` bzw. `ap12 stufe1` |
| `eingang/kalibrierung` | Werkzeug 4 aus den P0-Daten | `ap11 kalibrierung` |
| `eingang/pilot`, `eingang/teil_b` | Werkzeug 5 und Teil B | `ap11 teil-b` |
| `eingang/regelprofil`, `eingang/werkzeug8` | verwendetes Profil, gegebenenfalls Werkzeug-8-Werte | `kette` |
| `ergebnis/ergebnis`, `ergebnis/bewertung` | Ergebnis von AP-12; Vergleich mit der Wahrheit | `ap12 auswerten`, `harness bewerten` |
| `wahrheit/wahrheit`, `wahrheit/p0_wahrheit` | Generatorwahrheit (H1-Größen, Klasse, P0-Parameter) | `generator`; liest nur der Harness |

Der Generator schreibt nur Generatorausgaben; Kalibrierung, Pilot und Teil B entstehen aus diesen Dateien in AP-11
(auf Ebene Z aus den Stufe-1-Zusammenfassungen der Phase-0-Läufe). Ein nicht leeres `eingang/` wird zurückgewiesen.
