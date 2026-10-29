# PCMMS – Linie B: Abgrenzung für Forschungsrahmen v3.6

Entwurf 3 – 29.10.2026 – ersetzt Entwurf 2 und 1 vom selben Tag

Projekt: Phasenkontrollierte Mehrmassensysteme (PCMMS)
Autor: Matthias Früh, ORCID 0009-0005-9984-4207
Status: Entwurf zur Entscheidung (D-2 der Abgleichnotiz 29.10.; D-1 ist entschieden, siehe 1.7); bis dahin gilt Forschungsrahmen v3.5 unverändert; die Teilung B1/B2 ist ein Vorschlag und wird nicht stillschweigend angenommen
Zuordnung: AP-28 (Linie B), AP-29 (Linie C, geparkt), AP-14 (Präregistrierung, Dachstruktur); Arbeitsübersicht Technik 29.10., Punkte 66–73 (nachfolgend AÜT-Punkt)
Lizenz: CC BY 4.0 (Ordner docs/, siehe LICENSE-CC-BY-4.0)

> **Vermerk (29.10.2026).** Originaldatei `PCMMS_Linie_B_Abgrenzung_v3_6_Entwurf3_2026-10-29.md`, Entwurf 3 vom
> 29.10.2026; hier unverändert bis auf diesen Vermerk und die Lizenzzeile. Entwurf zur Entscheidung D-2 des Autors
> ([`../abgleichnotiz_2026-10-29_v4.md`](../abgleichnotiz_2026-10-29_v4.md), Abschnitt 5): Er stellt die
> Linie-B-Fassung des Forschungsrahmens v3.5 (Medienkopplung) der Abgrenzung des Autors vom 29.10.2026 (grenznahe
> Kontaktdynamik mit Auftriebshilfe und Armführung) gegenüber und benennt die Varianten V-1 bis V-3 mit einem
> Vorschlag (V-2, Teilung B1/B2). Der Forschungsrahmen v3.5 ([`forschungsrahmen_v3_5_2026-05.md`](forschungsrahmen_v3_5_2026-05.md))
> bleibt unverändert gültig; der Entwurf ersetzt keinen seiner Abschnitte und nimmt die geplante §9-Korrektur nicht
> vorweg. Die Teilung B1/B2 ist Vorschlag, nicht beschlossen. Entscheidung D-1 (29.10.2026) ist im Entwurf
> aufgenommen (Abschnitt 1.7, F-2). Linie B gehört im Arbeitsplan weiter zur Stufe S5, AP-28, Status „später“
> ([`../arbeitsplan_status.md`](../arbeitsplan_status.md)). Keine Messdaten; Zahlen sind Simulation, Analytik oder
> gekennzeichnete Überschläge.

## 0. Zweck

Seit dem 29.10.2026 stehen zwei Definitionen von Linie B nebeneinander. Dieser Entwurf stellt sie gegenüber, benennt drei Varianten für v3.6 und schlägt eine vor. Er ersetzt keinen Abschnitt von v3.5 und nimmt die ohnehin geplante §9-Korrektur (F̄_A statt F_drag,drift, β_h) nicht vorweg.

## 1. Ausgangslage

- 1.1 Forschungsrahmen v3.5 (Mai 2026, einzig gültige Rahmenfassung; v3.1–v3.4 und Reframe überholt): H1 Drift über quadratischen Luftwiderstand, nur bei Geschwindigkeits-Schiefe (M1) oder richtungsabhängigem Widerstand (M2); primäre Messkonfiguration D (Schub-Pendel/Torsionswaage); §9-Effektgrößen 10⁻⁷–10⁻⁴ N, durch die Skriptkorrekturen vom 06.09. relativiert; Kontrollen Dichtevariation und Vakuum-zu-Vakuum.
- 1.2 Richtungsnotiz Medienkopplung v5.2 (06.09.2026, gültig): drei Modelle – A vorgegebene Trägerbewegung (F̄_A), B freie Drift (F̄_B = 0), C aufgehängt (F̄_C = k⟨x⟩); Richtungsregel; Symmetriekontrollen (Sinus, Spiegelung, Zeitumkehr) als Periodenmittel; Dichteabhängigkeit ist Untersuchungsfrage, keine garantierte Monotonie (v1-Aussage gestrichen). Formelverzeichnis §11.1: Relativgeschwindigkeit, Widerstandsgesetz, stationäre Drift und gebundene mittlere Reaktionskraft getrennt definieren; bei kleiner Keulegan-Carpenter-Zahl ist das Kraftmodell offen.
- 1.3 Prüfarchitektur (01.09.2026, Entwurf): evakuierbare Kammer mit Torsionswaage, Druckreihe 2000 … 0,1 mbar mit mitlaufender AUS-Referenz; Auflösungsanforderung liegt vier Größenordnungen über dem Modellsignal.
- 1.4 Ballon-Demonstrator (Mai 2026): austarierter Heliumballon mit 2–3 Vibrationsmodulen, Video-Tracking, vertikale Netto-Drift; Konzept mit Firmware, keine Messdaten; Firmware erzeugt kein Egg-Profil (AÜT-Punkt 73).
- 1.5 Abgrenzung 29.10.2026 (Autor): B = grenznahe Bewegung mit Auftriebshilfe – Prototyp in speziell konstruierter Heliumhülle, dual-robotische Armführung der inneren Massen (z. B. zwei Arme je Masse, sechs bei N = 3), optimierte Profile, Restlast variabel unter, nahe oder über dem Abhebepunkt; Zielgrößen Maximallast, Grenzwerte, Kontaktverlustbedingungen. Im Extrakt: „eigentlicher konstruktiver und experimenteller Kern“.
- 1.6 Linie C (geparkt, AP-29; C-Notiz zuletzt v4): natürliche Trennungsbedingungen, vorzugsweise in der Atmosphäre, betrachtet aus den Testfeldern A/B; Formelverzeichnis §11.1: Umlenkung oder Abspaltung außerhalb der Systemgrenze; bei Medium als Träger setzt C die Klärung von B voraus. „Trennung“ in C (Abspaltung) ist nicht „Trennung“ im Sinne von Kontaktverlust (AÜT-Punkt 75).
- 1.7 Arbeitsplan: B und C liegen in Stufe S5 („später“); eine eigene Präregistrierung für Linie B fehlt (AÜT-Punkt 72). Entscheidung D-1 (Autor, 29.10.2026): Die Stufenfolge bleibt; B2 wird als langfristige Randbedingung für AP-01, AP-04 und AP-06 berücksichtigt – Erweiterbarkeit prüfen, Folgen dokumentieren; keine Verpflichtung von V1 zur Armführung oder zu gemeinsamer Hardware.

## 2. Gemeinsamkeiten beider B-Fassungen

- G-1 Plattform: Helium als Auftriebshilfe; derselbe Körper mit inneren Massen; beide arbeiten nahe am Abhebepunkt – der austarierte Ballon (1.4) ist der Grenzfall w_R ≈ 0 der Restlast aus 1.5.
- G-2 Medienabhängigkeit: Auftrieb und Medienkopplung verschwinden beide im Vakuum.
- G-3 Bilanz: ⟨F_c⟩ = M·g − ⟨F_ext,z⟩ + b_w (Formelverzeichnis Gl. 6) mit F_ext,z = F_auf + F_med,z; beide erhaltungskonform.
- G-4 Antrieb: beide brauchen programmierbare, asymmetrische Profile (Sinus-Kollaps im Referenzmodell; Egg mit aktiv geführter Rückholung, §10.6).

## 3. Unterschiede

| Merkmal | v3.5 / v5.2 (Medienkopplung) | 29.10. (Grenznähe) |
|---|---|---|
| Fragestellung | Wirkung innerer Bewegung auf das Medium: Drift oder gebundene mittlere Reaktionskraft | Verhalten der Kontaktdynamik bei künstlich kleiner Restlast |
| Mechanismus | dynamisch: Impulsübertrag ans Medium, Asymmetrie der Medienkraft | statisch: Auftrieb senkt W_R; Dynamik innen (S_true) |
| Zielgröße | stationäre Drift bzw. F̄_C = k⟨x⟩ als Referenzdifferenz (AÜT-Punkt 69) | F_min − ⟨N⟩, Harmonische, Liftoff-Anteil Λ, Zeitpunkte von Kontaktverlust und Wiederanlage, Maximallast |
| Regime (Modelle v5.2) | B frei (w_R ≈ 0), C aufgehängt (w_R < 0 oder Pendel), A vorgegebene Trägerbewegung | Kontakt (w_R > 0, F_c messbar); Übergang nach Schwebe/Fesselung |
| Signalgröße | 10⁻⁷–10⁻⁴ N (v3.5 §9, relativiert) | Wellenform im N-Bereich; Störung durch F_auf-Drift ≈ 0,03 N je Kelvin (Überschlag V1-Kandidat, Mechanismus je Hüllentyp, M-2) |
| Rolle des Auftriebs | Austarierung, Bedingung der freien Drift | Versuchsparameter und größte Störquelle zugleich |
| Datenbasis heute | Driftkarte 13×13, Fluid-/Medienkopplungsmodelle v2, Regimeanalyse v1.2 | keine – Abgrenzungsnotiz, Anforderungsspezifikation v0.4 |

Folge: Die beiden Fassungen sind nicht dieselbe Frage mit zwei Namen. Ein Lauf kann nicht zugleich Drift im Sub-Millinewton-Bereich und Kontaktverlust unter Newton-Lasten als Zielgröße haben.

## 4. Varianten für v3.6

- V-1 Umwidmung: B := Grenznähe (1.5). Medienkopplung wird Teilaspekt oder entfällt. Folge: docs/linie_b/ (v3.5, Richtungsnotiz v5.2, Prüfarchitektur, Driftkarte) verliert sein Zuhause; Untertitel, H1 und §9 werden ersetzt; die Dachstruktur der Präregistrierung ist umzuschreiben.
- V-2 Ergänzung: B behält den v3.5-Kern als B1 (Medienkopplung) und erhält B2 (grenznahe Kontaktdynamik mit Auftriebshilfe und Armführung). Gleiche Plattform, getrennte Zielgrößen, Regime und Läufe. Folge: v3.5-Material bleibt gültig; v3.6 ergänzt ein Kapitel B2 und die Messung von F_auf; AP-28 wächst; die Reihenfolge-Regel aus §11.1 (C setzt B voraus) bleibt erfüllt.
- V-3 Übergabe: B bleibt v3.5; der Grenznähe-Inhalt wird Testfeld von C (deckungsgleich mit dem C-Zielbereich: Grenzwerte, Maximallast, Trägerkopplung). Folge: C müsste teilweise entparkt werden – gegen den fixierten Fokus A/B – und „Trennung“ würde zwei Bedeutungen in einer Linie tragen (AÜT-Punkt 75).

Vorschlag des Entwurfs: V-2. Begründung: bewahrt die Linie-B-Unterlagen (PR #25), hält C geparkt, gibt der Armführung einen Ort, trennt Zielgrößen und Regime sauber und entspricht dem Vermerk vom 28.09.2026, Trennungsbedingungen als Vorarbeit zu C über die Dynamik in A bzw. B zu ergründen. Die Entscheidung liegt beim Autor (D-2); V-1 ist die kostspieligste, V-3 die am wenigsten verträgliche mit dem Arbeitsplan.

## 5. Vorschlag Kurzformel v3.6 (bei V-2)

- A = ruhend, ohne Auftriebshilfe, w_R = 1; Messqualität und Wellenform der Kontaktkraft.
- B1 = Medienkopplung: Drift oder gebundene Reaktionskraft; Regime Schwebe/aufgehängt (Modelle B, C) oder vorgegebene Trägerbewegung (Modell A); Kontrollen Dichte und Vakuum.
- B2 = grenznahe Kontaktdynamik: Kontaktregime mit 0 < w_R < 1, Auftriebshilfe als Versuchsparameter, Armführung nach Anforderungsspezifikation v0.4; Zielgrößen wie Linie A plus Kontaktverlust- und Wiederanlagezeitpunkte; Vorarbeit zu C.
- C = geparkt; Umlenkung oder Abspaltung außerhalb der Systemgrenze, energetische Wechselbedingungen (C-Notiz v4, §11.1).

Die Linien A und B2 teilen Observablen und Auswertepaket; B1 nicht. Das ist der Grund, B2 nicht in A aufgehen zu lassen (Auftriebshilfe ändert M-Konvention, Luftmasse und Störbild) und nicht in B1 (andere Zielgröße, andere Signalgröße).

## 6. Messtechnische Folgen für B2

- M-1 Restlastanteil w_R := (M·g − F_auf)/(M·g) als Versuchsparameter; Stufenleiter festzulegen (abfallend bis w_R → 0; Werte offen, F-3).
- M-2 F_auf mitmessen: Referenzwägung vor und nach dem Lauf, Temperatur von Füllgas und Umgebungsluft, Druck, Feuchte, Permeationsrate der Hülle über die Laufdauer. Der Driftmechanismus hängt vom Hüllentyp ab: gespannte, volumenfeste Hülle – F_auf folgt der Umgebungsluftdichte (≈ 0,35 %/K, ≈ 1 %/10 hPa); freie Hülle – Umgebungsdruck und -temperatur heben sich in erster Näherung auf, Treiber sind die Temperaturdifferenz Füllgas–Umgebung (≈ 0,34 % der verdrängten Luftlast je Kelvin), Feuchte und Permeation; Eigenwärme der Antriebe erzeugt dann eine betriebskorrelierte Drift; der Leerlauf-Modus ist dafür eine Gegenprobe, deren thermische Vergleichbarkeit nachzuweisen ist, und die Füllgastemperatur ein eigener Kanal. Überschlag V1-Kandidat (M ≈ 0,65 kg, ρ_Luft ≈ 1,20 kg/m³, ρ_He ≈ 0,17 kg/m³): Hülle ≈ 0,6–0,7 m³, verdrängte Luft ≈ 7–8 N, Drift ≈ 0,03 N je Kelvin – bei 5 % Restlast knapp 10 % je Kelvin. Hüllentyp festlegen (F-8).
- M-3 Zugesetzte Luftmasse der Hülle (Kugel: ½·ρ_Luft·V ≈ 0,4 kg beim Überschlag) ist von der Größenordnung M: M-Konvention (AÜT-Punkt 22), Engine-Parameter und Liftoff-Schwelle müssen sie enthalten (AÜT-Punkt 32). Das Linie-A-Modell überträgt sich nicht unverändert.
- M-4 Versuchskonfiguration je Lauf eindeutig festlegen – Kontaktaufstellung (F_c), Schwebe (Modell B), Fesselung (Modell C, Messgröße Fesselkraft; ⟨F_F⟩ = F_auf − M·g + ⟨F_med,z⟩ bei nach oben positiver Medienkraft) – und eine Zielgröße je Lauf. Wechsel des Kontaktzustands innerhalb eines Laufs (Kontaktverlust, Wiederanlage, Hüpfen) sind in B2 Untersuchungsgegenstand: erkennen und getrennt auswerten. Der statische Restlastanteil bestimmt den momentanen Kontaktzustand nicht.
- M-5 Hülle nur am Körper befestigt; keine Durchführung als Kraftpfad; Raumluftbewegung protokollieren – die Hülle ist zugleich die Kopplungsfläche von B1.
- M-6 Liftoff-Schwelle skaliert mit w_R (Herleitung Anforderungsspezifikation AF-32; mit der Engine zu prüfen, O-9).
- M-7 Störgrößentabelle der Präregistrierung (Tabelle C) um Auftriebsdrift, Permeation, zugesetzte Luftmasse und Hüllenströmung erweitern; Elektrostatik bleibt der potenziell größte Gleichterm (00_UEBERSICHT_Linie_B_C §2.6).

## 7. Änderungen gegenüber v3.5 (bei V-2)

- Ä-1 Untertitel ergänzen: Medienkopplung (B1) und grenznahe Kontaktdynamik (B2).
- Ä-2 Abgrenzungsabschnitt: Kurzformel aus Abschnitt 5; Abgrenzung zu A und C.
- Ä-3 Observablenliste um B2-Größen erweitern; Signalgrößen je Teillinie nennen.
- Ä-4 §9: F̄_A statt F_drag,drift, β_h (bereits geplant); zusätzlich F_auf als Versuchsparameter in B2 mit eigenem Symbol (Formelverzeichnis, O-11).
- Ä-5 Verweis auf Anforderungsspezifikation Dual-Armführung v0.4.
- Ä-6 Positionierung aus dem Literaturabgleich v3 übernehmen: Eigenständigkeit von B in der expliziten Mediumkopplung; keine Neuheit bei phasenbasierter Gleichrichtung.
- Ä-7 Präregistrierung: prüfen, ob die Dachstruktur B2 abdeckt; eigene B-Präregistrierung (AÜT-Punkt 72) um B2 erweitern.
- Ä-8 Demonstrator: Zuordnung zu B1 (vertikale Drift des austarierten Ballons) ausdrücklich festhalten; kein B2-Demonstrator vorhanden.

## 8. Offene Fragen

- F-1 Entscheidung V-1 / V-2 / V-3 (D-2).
- F-2 beantwortet durch D-1 (29.10.): B bleibt in S5; B2 nur als Randbedingung für AP-01/04/06 (siehe 1.7). Offen bleibt daraus allein, was „Erweiterbarkeit prüfen“ für AP-01, AP-04 und AP-06 konkret heißt – gehört in arbeitsplan_status.
- F-3 Stufenleiter der Restlast w_R.
- F-4 Fesselungsregime: B2 oder C?
- F-5 Übertragbarkeit der Linie-A-Engine auf B2 (zugesetzte Luftmasse, Hüllenelastizität, Kippmomente); AÜT-Punkt 67 (instationäres Kraftmodell, kleine KC) gilt für B1 und für die Hüllenströmung in B2.
- F-6 Abschnittsnummern von v3.5 für Ä-1 bis Ä-8 (v3.5 hier nicht im Volltext eingesehen).
- F-7 Literaturstand zu vibrationsgetriebener Bewegung auftriebskompensierter Körper – vor externer Verwendung prüfen (AÜT-Punkt 57).
- F-8 Hüllentyp für B2 (volumenfest/gespannt oder frei) und die dazu passende Kompensation (M-2); gilt sinngemäß auch für den austarierten Ballon in B1.

## Änderungslog

- Entwurf 3 (29.10.2026, im Dokumentations-PR): Korrekturen des Autors K-3 und K-4 (Abgleichnotiz v4 Abschnitt 7) – M-4 lässt Kontaktzustandswechsel innerhalb eines Laufs zu (Konfiguration je Lauf eindeutig, Wechsel erkennen und getrennt auswerten) und trägt die berichtigte Fesselbilanz (K-1); M-2 Leerlauf als Gegenprobe statt Abdeckung; Verweise auf v0.4.
- Entwurf 2 (29.10.2026): D-1 in 1.7 und Status aufgenommen, F-2 als beantwortet geführt; M-2 Driftmechanismus nach Hüllentyp präzisiert (Reststellenprüfung vor dem PR), F-8 neu; Verweise auf Anforderungsspezifikation v0.3; Vorbehalt B1/B2 im Kopf.
- Entwurf 1 (29.10.2026): erstellt.
