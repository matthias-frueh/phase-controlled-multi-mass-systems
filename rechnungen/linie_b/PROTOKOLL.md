# P2 · Prüfgruppe linie_b · Protokoll (02.10.2026)

> **Vermerk zur Übernahme (04.10.2026).** Protokoll aus der Gesamtprojektanalyse 10/2026, Stand 02.10.2026, unverändert bis auf Pfade und Quellenangaben. Geprüft wurde der Repository-Stand `cd7be6a` (28.09.2026) mit der Präregistrierung v2 vom 25./28.09.2026; die späteren Änderungen aus PR #13 und PR #14 (unter anderem Präregistrierung v2 mit Arbeitsfestlegungen, `code/auslegung.py`, `code/ereignisloeser.py`) sind nicht eingearbeitet. Alle Zahlen sind Simulation oder Analytik, keine Messdaten. Verweise wie „L1a-019“, „P1 §3“ oder „B01–B14“ zeigen auf Arbeitsdokumente der Analyse, die nicht im Repository liegen. Quellen, die nicht im Repository liegen, sind als „(Quelle außerhalb des Repositorys)“ gekennzeichnet. Startbefehle und Grenzen je Gruppe: [`rechnungen/README.md`](../README.md).

Ablage: `rechnungen/linie_b/` (ursprünglich lokal, jetzt unter `rechnungen/`).
Quellen nur gelesen. Die Linie-B-Skripte wurden unverändert nach `quelle_kopie/` kopiert und dort importiert.
Kennzeichnung im Text: **[R]** eigene Rechnung, **[Q]** Quellenangabe mit Fundstelle, **[A]** Annahme.

Umgebung für alle Befehle:

```
cd rechnungen/linie_b
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../../code
```

## 0 Quellenstand

- `pcmms_fluid_drift_v2.py` und `pcmms_medienkopplung_modell_v2.py` an zwei Ablageorten außerhalb des Repositorys sind **byte-identisch** (MD5 15bef4cf… bzw. d32ec03b…). Die Kopien am zweiten Ablageort sind nur jünger datiert (26.09. gegenüber 06.09.). Verwendet wurde der gemeinsame Inhalt.
- Neu nachgerechnete Stellen: Notiz v5.2 §4.2, §4.3, §6, §7, §8; `PCMMS_Skriptkorrekturen_LinieB_2026-09-06.md` §1, §3; Werkstattbericht Z. 88; Präreg-Anhang A4, Tabelle C und Tabelle F.

## 1 Befunde

### LB-01 · Keulegan-Carpenter-Zahl und Kennzahlen des Trägers (Driftskript v2)

- **Frage:** Gilt KC ≈ 0,009 (Notiz v5.2 §6) oder ≈ 0,004 (P1, L3-054)? Wie groß sind Re, β, δ?
- **Methode [R]:** v_osc(t) = −RATIO·ṙ(t) aus `v_osc_profile()` des Skripts (Δt = 50 µs). Die Auslenkung folgt durch Integration. a ist die halbe Spitze-Spitze-Auslenkung. D wurde in drei Varianten gerechnet: 0,2 m (Notiz), √(4A/π) = 0,1954 m und √A = 0,1732 m, mit A = 0,03 m². Stoffwerte Luft: ρ = 1,2 kg/m³, μ = 1,8·10⁻⁵ Pa·s, wie in Notiz §8.
- **Ergebnis (synchron, 0°/0°):**
  - Kinematik: U_max = 12,000 mm/s, a = 0,1337 mm (Spitze-Spitze 0,2674 mm). U_max/ω = 0,191 mm ≠ a, denn das Profil ist kein Sinus.
  - KC_a = 2πa/D = **0,0042** (D = 0,2 m), 0,0043 bzw. 0,0049 für die anderen D.
  - KC_U = U_max·T/D = **0,0060**, 0,0061 bzw. 0,0069.
  - Mit a = 0,3 mm ergibt sich 0,0094, also der Notizwert. 0,3 mm entspricht ungefähr dem Spitze-Spitze-Weg, nicht der Amplitude.
  - Re = U_max·D/ν = 160 (D = 0,2 m) bzw. 156.
  - β = Re/KC_U = f·D²/ν = **2,67·10⁴** bzw. 2,55·10⁴ (Notiz: „≈ 3·10⁴“).
  - δ = √(2ν/ω) = **0,691 mm**, δ/D = 3,5·10⁻³, δ/a = 5,2. Die Stokes-Schicht ist also fünfmal dicker als der Trägerweg.
  - Streaming-Reynoldszahl Re_s = ωa²/ν = 0,075.
  - Triphasik (120°, 240°): a = 6,2 µm, KC_a = 1,9·10⁻⁴, δ/a = 111. Langsamster Rasterpunkt: KC_a = 5·10⁻⁴.
  - Medienkopplungsmodell v2 (`b1b`): Fall S KC_U = 0,063, Fall R 0,25 (D = 0,16 m). Auch diese Fälle liegen bei KC ≪ 1.
- **Bewertung:** P1 ist bestätigt, aber nur für die Definition 2πa/D. Mit der in der Aufgabe genannten Definition U_max·T/D ergibt sich 0,006. Die Gleichsetzung „U_max·T/D = 2πa/D“ gilt nur für Sinusbewegung. Der Notizwert 0,009 ist um den Faktor 1,5–2,2 zu groß. Die Folgerung KC ≪ 1 bleibt in jeder Definition bestehen.
- **Reproduktion:** `python3 b1_kc_kennzahlen.py`, `python3 b1b_kc_medienkopplung_fall_s.py`. Ausgaben: `b1_kc_kennzahlen.out`, `b1b_kc_medienkopplung_fall_s.out`.
- **Einschränkungen:** Die Trägergeometrie ist nicht spezifiziert. D wurde nur aus A abgeleitet.

### LB-02 · Gültigkeit des quasistationären Widerstandsmodells bei KC ≪ 1; dominierende Kraftanteile

- **Frage:** Ist Morison bzw. C_D(Re) bei KC ≪ 1 gültig? Welche Anteile dominieren?
- **Methode [R]:**
  - Träger als Kugel gleicher Stirnfläche [A], R = 0,0977 m.
  - Exakte lineare Lösung der oszillierenden Kugel (Stokes 1851): F = −6πμR(1+R/δ)·v − [(2/3)πR³ρ + 3πR²ρδ]·v̇, je Harmonische der tatsächlichen v_osc(t).
  - Dazu das quasistationäre Gesetz des Skripts −C₂ρ·v|v| und die formalen Stokes-Wang-Beiwerte für den Kreiszylinder (Wang 1968, Literaturliste der Notiz).
- **Ergebnis (Luft, synchron, Amplituden bei f):**

  | Anteil | Größe |
  |---|---|
  | Trägheit (zugesetzte Masse + Schicht) | 1,26·10⁻³ N |
  | viskose Stokes-Schicht (linear) | 3,9·10⁻⁵ N (Verhältnis 0,031 ≈ 9δ/2R) |
  | quasistationär-quadratisch (Skriptgesetz) | 9,7·10⁻⁷ N |
  | F̄_A (Gleichanteil des Skriptgesetzes) | +1,675·10⁻⁷ N |

  Stokes-Wang (Zylinder): C_M = 2,014, formales C_D = 26,9, F_D/F_I = C_D·KC/(π²C_M) = 0,008.
- **Folgerung:**
  - **Morison mit quasistationärem C_D(Re) ist nicht gültig.** Bei a ≪ δ ≪ D bleibt die Strömung an glatten Körpern anliegend und laminar (Sarpkaya 1986, laut Notiz §6). Die Kraft ist in führender Ordnung linear: zugesetzte Masse ≫ Stokes-Schicht. Ihr Periodenmittel ist null.
  - **Strukturaussage [R, Symmetrie]:** Für eine in Bewegungsrichtung vorn-hinten-symmetrische Hülle ist das Kraftfunktional ungerade, F[−U] = −F[U]. Im analytischen Bereich (anliegende Strömung, Re_s ≪ 1) verschwindet damit jeder Beitrag zweiter Ordnung, also jeder Mittelwert ∝ ρU², identisch. Ein gleichgerichteter Mittelwert entsteht frühestens in dritter Ordnung durch die Kopplung ω·ω·2ω. Das Gesetz v|v| erzeugt einen Mittelwert ∝ ρU² nur, weil es nicht analytisch ist; damit überträgt es Ablösephysik in ein Regime ohne Ablösung.
  - Streaming liegt wegen Re_s = 0,075 im langsamen, viskosen Bereich.
  - Der Betrag der mittleren Kraft wurde **nicht** abgeschätzt (Notiz §6: keine Ersatzabschätzung).
  - Scharfe Kanten (kastenförmiger Träger) können auch bei kleinem KC lokal ablösen. Das ist geometriespezifisch und offen.
- **Bewertung:** L3-055 ist bestätigt und präzisiert.
- **Reproduktion:** `python3 b1_kc_kennzahlen.py` (Abschnitte „Kraftanteile“ und „Stokes-Wang“).
- **Einschränkungen:** Kugel- bzw. Zylinderformeln sind Stellvertreter. Die Symmetrieaussage setzt eine symmetrische Umgebung voraus; Aufhängung und Wände brechen sie schwach.

### LB-03 · Wasser-Voreinstellung: zugesetzte Masse verletzt die Rückstoßkinematik (neu)

- **Methode [R]:** wie LB-02, ρ = 1000 kg/m³.
- **Ergebnis:** Die zugesetzte Masse der Ersatzkugel beträgt ½ρV = 1,95 kg, das sind **2,6·M_ges** (M_ges = 0,75 kg). In Luft sind es 3,1·10⁻³·M_ges. Die Notizbedingung (iii) „Widerstand ≪ Trägheit“ (c₂ρv/(Mω) ≈ 3·10⁻³, nachgerechnet 3,06·10⁻³) prüft nur den quadratischen Term. Mit zugesetzter Masse sinkt die Trägerbewegung um etwa M/(M + m_a) ≈ 0,28. v_osc = −RATIO·ṙ gilt in Wasser also nicht.
- **Bewertung:** neu. Die Wasserkarte (RHO = 1000 im Skript) ist nur formal. Wegen der ρ-Unabhängigkeit der Bilanz sind ihre v_d-Werte dieselben wie für Luft. τ und F̄_A für Wasser sind physikalisch nicht belastbar.
- **Reproduktion:** `python3 b1_kc_kennzahlen.py`, Zeile „zugesetzte Masse/M_ges“.
- **Einschränkungen:** geometrieabhängig. Eine Platte, die längs angeströmt wird, hätte eine viel kleinere zugesetzte Masse.

### LB-04 · „Integrierte Kontrolle ausgeschaltet“ in fluid_drift_v2

- **Stelle [Q]:** `pcmms_fluid_drift_v2.py` Z. 40 `INTEGRATED_CHECK = False`, Kontrollpunkte Z. 41 `[(0,0), (120,240)]`, Ausführung `main()` Z. 189–195, Integrator `integrate_drift()` Z. 110–137 (RK4, Δt = 50 µs, Abbruch, wenn sich das Periodenmittel über 10 Perioden relativ um weniger als tol = 10⁻⁵ ändert).
- **Methode [R]:** Kopie `b2_fluid_drift_v2_kontrolle_an.py`. Einzige Änderung ist Z. 40 = True (per diff belegt). Laufzeit 29 s.
- **Ergebnis:**
  - Karte und CSV sind unverändert. `sweep_13x13_drift_v2.csv` stimmt mit der archivierten Datei in v_d, F̄_A und τ exakt überein (max. |Diff| = 0).
  - Kennzahlen: max 1,0549, min −0,294477 mm/s, Mittel 0,1813 mm/s, 54/169 negativ, τ = 5,84–37,99 s.
  - Die Kontrolle liefert nur Konsolenzeilen:
    - (0,0): Bilanz +1,0549, integriert +1,0548 mm/s nach 546 Perioden (55 s)
    - (120,240): −0,0810 bzw. −0,0810 nach 3232 Perioden (323 s)
- **Bewertung:** P1 ist bestätigt. Das Einschalten ändert keine Kartenwerte; es bestätigt die Bilanz auf ≤ 10⁻⁴ relativ.
- **Reproduktion:** `timeout 540 python3 b2_fluid_drift_v2_kontrolle_an.py` → `b2_fluid_drift_v2_kontrolle_an.out`, `sweep_13x13_drift_v2.csv`.
- **Einschränkung:** Das Abbruchkriterium ist τ-abhängig. Der Restfehler beträgt ≈ tol·τ/(10T), siehe LB-05.

### LB-05 · Integriertes Modell: periodische Lösung und Dichtevergleich (schließt die Lücke in L3-036)

- **Methode [R]:** Schießverfahren über eine Periode mit demselben RK4/Δt wie `integrate_drift()`; Bedingung V(T; V₀) = V₀ (brentq). Damit ist der stationäre Wert des integrierten Modells ohne Einschwingen auch für ρ = 1,2 erreichbar (τ = 81 min). Dazu kommt `integrate_drift()` am langsamsten Rasterpunkt.
- **Ergebnis:**

  | Punkt | rel. Abw. periodisch vs. Bilanz | ρ = 1,2 vs. ρ = 1000 (periodisch) |
  |---|---|---|
  | (0,0) | −4,6·10⁻⁶ (ρ = 1000) / +5,7·10⁻⁷ (ρ = 1,2) | +5,2·10⁻⁶ |
  | (120,240) | +8,5·10⁻⁶ | −7,6·10⁻⁹ |
  | (221,54°, 110,77°) | +9,3·10⁻⁶ / +9,1·10⁻⁶ | −1,8·10⁻⁷ |

  Am langsamsten Punkt liefert `integrate_drift()` (tol = 10⁻⁵) −0,166274 mm/s nach 2911 Perioden; periodisch −0,166334. Der Abbruchfehler von 3,6·10⁻⁴ passt zu tol·τ/(10T) = 3,8·10⁻⁴.
- **Bewertung:** bestätigt Notiz v5.2 §7.3 und Skriptkorrekturen §1 („sechs Stellen“; nachgerechnet ≤ 5,2·10⁻⁶ relativ). Der Mittelungsfehler der Bilanz liegt bei ≤ 10⁻⁵.
- **Reproduktion:** `timeout 540 python3 b2b_periodische_loesung.py` → `b2b_periodische_loesung.out` (23 s).
- **Einschränkung:** Alles gilt innerhalb des Zweiterm-Ansatzes (LB-02).

### LB-06 · Wo ρ eingeht: Kraft- und Geschwindigkeitsaussage getrennt (L3-036, L3-068, L1b-064, L3-020)

- **Methode [R]:** Quelltext von `drift_balance()` ausgegeben; Auswertung bei ρ = 1000 … 0,0012; Modell B mit linearem Term c₁ (Notiz §4.2), illustrativ c₁ = 6πμR = 3,3·10⁻⁵ N·s/m [A, nicht validiert].
- **Ergebnis:**
  - Die Nullstellenfunktion für v_d, `np.mean((x+v)*np.abs(x+v))`, enthält ρ nicht.
  - v_d = +1,0549001614 mm/s (0,0) bzw. −0,0810241947 mm/s (120,240), identisch für alle ρ.
  - F̄_A ∝ ρ: 1,396·10⁻⁴ N (Wasser), 1,675·10⁻⁷ N (Luft).
  - τ ∝ 1/ρ: 5,84 s (Wasser), 4870 s (Luft).
  - Mit c₁ > 0 wird v_d dichteabhängig, Crossover ρ* = c₁/(2c₂⟨|v_osc|⟩) = 0,26 kg/m³ (0,0) bzw. 1,9 kg/m³ (120,240). Bei ρ = 1,2 ist v_d/v_d(c₁ = 0) = 0,83 bzw. 0,40. Für ρ ≪ ρ* gilt v_d ∝ ρ.
- **Bewertung:**
  - L3-036 ist bestätigt (konstruktionsbedingt).
  - „Drift ∝ Dichte, null im Vakuum“ (Archiv-Vermerk 28.09. §2.3, Werkstattbericht Z. 88) ist als Aussage über die stationäre Drift im Skriptmodell **widerlegt**.
  - ∝ ρ gilt für die **Kraft** F̄_A (Modell A/C, bei festem C_D und fester Bewegung), für die Anfangsbeschleunigung bzw. Fensterwerte mit t ≪ τ (LB-07) und mit c₁ > 0 unterhalb des Crossovers.
  - Wegen LB-02 ist bei KC ≪ 1 aber auch F̄ ∝ ρ nicht belegt.
- **Reproduktion:** `python3 b3_dichte_drift_c1.py` → `b3_dichte_drift_c1.out`.

### LB-07 · v1-Fensterkarte reproduziert; Fensterwert skaliert mit ρ (neu)

- **Methode [R]:** wie v1 (`pcmms_fluid_drift.py`: Start aus der Ruhe, Mittel 4–8 s, RK4, Δt = 50 µs), alle 169 Punkte, ρ = 1000 und 1,2. Abgleich mit der archivierten `sweep_13x13_drift.csv` (Stand 01.09.2026; Kopie unter `daten/sweep_13x13_drift_v1.csv`).
- **Ergebnis:**
  - Die archivierte v1-Karte ist reproduziert, max. |Diff| = 4,9·10⁻¹¹ m/s.
  - Spanne **−0,104101 … +0,691635 mm/s**, genau die Zahlen des Werkstattberichts. Das entspricht 14,7–65,6 % des stationären Werts; die Vorzeichen sind überall gleich.
  - Bei ρ = 1,2 liefert dieselbe Auswertung −0,000155 … +0,001359 mm/s, also 0,019–0,129 % des stationären Werts. Das Verhältnis der Fensterwerte ρ = 1000 / ρ = 1,2 beträgt 509–769 (Dichteverhältnis 833).
- **Bewertung:** Die Werkstattbericht-Zahlen sind nicht eingeschwungene Wasserwerte. Eine Fensterauswertung mit t ≪ τ skaliert nahezu ∝ ρ (V ≈ F̄_A·t/M), die stationäre Drift nicht. Ob das die Herkunft der Dichteaussage ist, ist im Bestand nicht belegt.
- **Reproduktion:** `timeout 540 python3 b3b_v1_fenster_karte.py` → `b3b_v1_fenster_karte.out`, `.csv` (34 s).

### LB-08 · Effektspanne 10⁻⁷–10⁻⁴ N (L3-015)

- **Methode [R]:** unveränderte Kopie `pcmms_medienkopplung_modell_v2.py` ausgeführt.
- **Ergebnis:** Fall S: F_drag_drift = 3,39·10⁻⁷ N, F̄_A = 6,67·10⁻⁶ N, Verhältnis 19,7; Pendel 680 nm (v1: 34,5 nm). Fall R: −3,15·10⁻⁵ bzw. −3,20·10⁻⁴ N. Die KC-Zahlen der Fälle liegen bei 0,05–0,25 (LB-01).
- **Bewertung:** L3-015 ist bestätigt. Die Spanne beruht auf F_drag_drift und ist bei KC ≪ 1 nicht abgesichert.
- **Reproduktion:** `python3 quelle_kopie/pcmms_medienkopplung_modell_v2.py` → `b0_medienkopplung_modell_v2_lauf.out`.

### LB-09 · V1: Luftkräfte auf die bewegten Module

- **Methode [R]:**
  - Egg-Lageprofil der Engine (`finesweep.z_egg_zdd`), Hub 7,692 mm, v_max = 0,2417 m/s, a = −11,68 … +21,69 m/s².
  - Modul als Kugel R = 1,45 cm (100 g Stahl) bzw. 2,5 cm, oder als breitseitig angeströmte Scheibe R = 4 cm [A].
  - Stokes-Kugel exakt; quadratischer Widerstand mit C_D = 2 als **obere Schranke**; Schallabstrahlung R_rad = (π/3)ρc·a²(ka)⁴.
- **Ergebnis:**
  - Kennzahlen: KC = 0,30–0,83, β = 560–4300, δ/a = 0,18, Re_s = 62. Die Module selbst liegen also nicht im Bereich KC ≪ 1.
  - Amplituden bei f / 2f / 3f für die Scheibe R = 4 cm (größter Fall):
    - zugesetzte Masse 3,3·10⁻³ / 1,1·10⁻³ / 4,5·10⁻⁴ N
    - viskos 1,9·10⁻⁴ / 4,4·10⁻⁵ / 1,6·10⁻⁵ N
    - quadratische Schranke 2,9·10⁻⁴ / 7,9·10⁻⁵ / 3,1·10⁻⁵ N
    - Schall ≤ 2·10⁻⁹ N
  - Für die Kugel R = 1,45 cm liegen alle Anteile bei ≤ 1,4·10⁻⁴ N.
  - **Gleichanteil:** ⟨v|v|⟩ = 0 exakt je Modul, weil v in jeder Halbsinus-Lagephase symmetrisch ist. Ein quasistationärer Gleichrichtungsanteil entfällt beim Linie-A-Egg.
  - Zugesetzte Masse 0,008–0,20 g, also 7,7·10⁻⁵ bis 2·10⁻³ von m_j = 0,1 kg. In dieser Höhe liegt auch der Massenfehler der H3-Vorhersage G_F·m_j·a_k.
- **Bewertung:** neu. Alle Anteile liegen ≤ 0,1·u_c (u_c = 0,0327 N). Sie sind linear bzw. je Modul eigenständig und überlagern sich daher; H1 ist nicht betroffen. Im geschlossenen Gehäuse sind diese Kräfte intern.
- **Reproduktion:** `python3 b4_v1_luftkraefte.py`, Abschnitt (1) in `b4_v1_luftkraefte.out`.

### LB-10 · V1: zugesetzte Luftmasse am Körper und Resonanzempfindlichkeit

- **Methode [R]:**
  - Lineare Dauerkontaktlösung mit (M + m_a) auf der Auflagerkoordinate. Abgleich mit `linear_solver.solve`: F_min(120,240) = 5,330390 N in beiden Rechnungen.
  - Gehäuse 20×20×10 cm bzw. 15×15×8 cm [A], m_a = (8/3)ρR³ (Scheibe gleicher Fläche) = 4,60 bzw. 1,94 g, also 0,71 bzw. 0,30 % von M.
  - K = 10⁴/10⁵/10⁶ N/m bei ζ = 0,0992.
- **Ergebnis (4,6 g):**
  - Die Kontaktresonanz verschiebt sich um f_n −0,35 %.
  - K = 10⁴ (2f/f_n = 1,013):
    - Triphasik: dF_min = +1,24·10⁻² N (0,38·u_c; 2,6 % von ΔF_Zelt = 0,4693 N), |ΔN₃| = 1,3·10⁻² N
    - (100°, 240°): |ΔN₂| = 0,131 N bei |N₂| = 3,68 N (im Wesentlichen eine Phasendrehung), dF_min = −9,5·10⁻³ N
  - K = 10⁵ (6f nahe f_n = 62,4 Hz): dF_min bis −1,2·10⁻² N, |ΔN_k| ≤ 3,8·10⁻³ N.
  - K = 10⁶: ≤ 1,3·10⁻³ N.
  - Viskose Stokes-Schicht am Gehäuse: 5–8·10⁻³ N·s/m (≤ 0,05 % von C). Schallabstrahlung ≤ 4·10⁻⁵ N·s/m.
- **Bewertung:** neu.
  - Der Effekt ist linear und damit in der gemessenen Übertragung bzw. den Phase-0-Läufen enthalten. Für H1–H3 ist er kein Artefakt.
  - Für Vergleiche Simulation ↔ Messung (A3, Engine ohne m_a) ist er beim resonanten Referenzsatz in der Größe von u_c und darüber relevant.
- **Reproduktion:** `python3 b4_v1_luftkraefte.py`, Abschnitt (2).
- **Einschränkungen:**
  - m_a für einen Kasten ist nur genähert; Bodennähe erhöht den Wert.
  - Einzelmodul mit Referenzhub: linear ungültig wegen Liftoff (F_min,lin = −2,06 N), passend zu P1 §3.1.

### LB-11 · V1: Luftpolster bzw. Quetschfilm unter dem Körper (neu)

- **Methode [R]:**
  - Viskos: c_sq = 3πμR⁴/(2h³).
  - Trägheitsanteil: Skala des Gleichanteils |F̄| ~ πρR⁴⟨ż²⟩/(16h²), reibungsfreie Kleinamplitudennäherung.
  - Zum Vorzeichen: Die reine Austrittsrandbedingung liefert eine abstoßende Kraft; ein Eintrittsverlust kann sie aufheben oder umkehren. **Das Vorzeichen ist offen.**
- **Ergebnis (R = 0,113 m):**
  - c_sq = 13,8 / 0,51 / 0,014 N·s/m bei h = 1 / 3 / 10 mm, also 86 / 3,2 / 0,09 % von C = 16 N·s/m.
  - Der viskose Gleichanteil ist exakt null, weil F = −dΦ(h)/dt.
  - Skala des Trägheits-Gleichanteils bei K = 10⁴, h = 3 mm: (100°, 240°) 5,2·10⁻³ N (0,16·u_c), Triphasik 8·10⁻⁴ N. Bei h = 10 mm ≤ 5·10⁻⁴ N; bei K ≥ 10⁵ ≤ 7·10⁻⁵ N (h = 3 mm).
  - ωh²/ν = 8 / 75 / 838: bei 1 mm überwiegt die Viskosität.
- **Bewertung:** neu, mit niedriger bis mittlerer Sicherheit. Der Anteil ist konfigurationsabhängig, skaliert mit ⟨ż²⟩ und hätte damit die Signatur eines phasenabhängigen Mittelwerteffekts. Relevant nur bei weichem Kontakt und engem Spalt.
- **Reproduktion:** `python3 b4_v1_luftkraefte.py`, Zeilen „Quetschfilm“.
- **Einschränkungen:** Die V1-Geometrie (Spalt, Bodenform) ist unbekannt. Die Formel ist nur eine Skala.

### LB-12 · V1: Auftrieb, Luftdichte, Thermik

- **Ergebnis [R, A: V = 1,8–4 l]:**
  - Statischer Auftrieb ρgV = 0,021–0,047 N (0,65–1,44·u_c). Er hebt sich in Δ⟨N⟩ gegen die Referenzläufe auf (Präreg-Entwurf `docs/praeregistrierung_v2_entwurf.md` Z. 158 und 167: Referenzlauf = Module geparkt; Δ⟨N⟩ = ⟨N⟩_Lauf − N_s,int [Q]). Nur ein Vergleich von ⟨N⟩ mit M·g aus der Masse wäre betroffen.
  - ±10 hPa: 2–5·10⁻⁴ N.
  - Belüftetes Gehäuse +10 K: 0,7–1,6·10⁻³ N, langsam.
  - Konvektion an der Wand bei +5 K: ~5·10⁻⁵ N (Überschlag).
- **Bewertung:** neu. Drift ≤ 0,05·u_c; die Interpolation zwischen Referenzläufen und D2 decken das ab. Die Formel „⟨N⟩ = M·g“ meint das scheinbare Gewicht M·g − ρ_L·g·V.
- **Reproduktion:** `python3 b4_v1_luftkraefte.py`, Abschnitte (2) und (3).

### LB-13 · V1: Elektrostatik; Tabelle C der Präreg

- **Quelle [Q]:** In Tabelle C (`docs/praeregistrierung_v2_anhang.md`, ab Z. 647, und lokale Überarbeitung vom 01.10., ab Z. 662) kommen weder Luft-, Auftriebs- oder akustische Kräfte noch Elektrostatik vor (grep ohne Treffer in Hauptdokument und Anhang, Repo und lokal).
- **Ergebnis [R, A]:** Plattennäherung σ²A/(2ε₀) auf 0,04 m² ergibt 2·10⁻⁵ / 2·10⁻³ / 0,23 N für σ = 10⁻⁷ / 10⁻⁶ / 10⁻⁵ C/m². Das ist der potenziell größte Gleich- und Driftterm, aber stark unsicher. Durch Bewegung relativ zu Gegenflächen kommt eine Modulation hinzu.
- **Bewertung:** P1 ist bestätigt. Tabelle C braucht Zeilen für Elektrostatik und für Luftpolster/zugesetzte Luftmasse; Auftrieb gehört in die Definition von H0.
- **Reproduktion:** `python3 b4_v1_luftkraefte.py`, Abschnitt (3). Für die Tabelle: `grep -n -i "luft\|elektrostat\|auftrieb\|akust" docs/praeregistrierung_v2_*.md`.

### LB-14 · „Egg“ in Linie B ≠ „Egg“ in Linie A (neu)

- **Ergebnis [R]:**
  - Linie B (`egg_vel`) gibt Halbsinusbögen der **Geschwindigkeit** vor: V_FAST = 0,06 m/s, Modulhub 1,337 mm, Trägerhub 0,267 mm. Die Geschwindigkeit ist dabei schief.
  - Die Linie-A-Engine gibt Halbsinusbögen der **Lage** vor: Hub 7,69 mm, v_max = 0,2417 m/s in beiden Phasen, ⟨v|v|⟩ = 0 je Modul.
  - Mit Linie-A-Kinematik wäre F̄_A für ein einzelnes Modul exakt null. Im Zweiterm-Modell gibt es dann bei synchroner und bei triphasischer Lage keine Gleichrichtung, denn dort ist F̄_A ungerade unter φ → −φ.
- **Bewertung:** neu. Linie-B-Zahlen sind nicht auf die V1-Kinematik übertragbar.
- **Reproduktion:** `python3 b4_v1_luftkraefte.py`, Kopfzeilen; Quelltextvergleich `egg_vel()` gegen `z_egg_zdd()`.

## 2 Zusammenfassung für V1 (Größenordnungen, Luft)

| Beitrag | Gleichanteil | Wechselanteile f/2f/3f | relativ zu u_c = 0,0327 N |
|---|---|---|---|
| Module: zugesetzte Masse, Widerstand, Schall | 0 (Egg), Schranke ≪ 10⁻⁴ N | ≤ 3,3·10⁻³ N (Platte R = 4 cm), ≤ 1,4·10⁻⁴ N (kompakt) | ≤ 0,1 |
| Gehäuse: zugesetzte Masse 2–5 g | 0 | dF_min ≤ 1,2·10⁻² N, ΔN₂ bis 0,13 N nahe Resonanz (K = 10⁴); ≤ 1,3·10⁻³ N bei K = 10⁶ | linear, in gemessener Übertragung |
| Quetschfilm, viskos | 0 exakt | Dämpfung 0,1–86 % von C (h = 10…1 mm) | linear |
| Quetschfilm, Trägheit | Skala ≤ 5·10⁻³ N (K = 10⁴, h = 3 mm), Vorzeichen offen | – | ≤ 0,16, phasenabhängig |
| statischer Auftrieb | 0,02–0,05 N, konstant | – | hebt sich in Δ⟨N⟩ auf |
| Dichte-/Temperaturdrift | ≤ 1,6·10⁻³ N, langsam | – | ≤ 0,05 |
| Konvektion | ~5·10⁻⁵ N | – | ≪ 0,1 |
| Elektrostatik [A] | 2·10⁻⁵ … 0,2 N | Modulation durch Bewegung | unbekannt, bis ≫ 1 |

Vergleichsgrößen [Q]: u_c ≤ 0,0327 N, Δ(F_min) = 0,117 N, ΔF_Zelt = 0,4693 N (Anhang A4); 0,1·u_c als Schwelle „systematisch klein“ (Tabelle F); M·g = 6,3765 N.

## 3 Korrekturen an Quellen

1. Notiz v5.2 §6: „Trägeramplitude a ≈ 0,3 mm, KC ≈ 0,009“. Richtig ist a = 0,134 mm (halbe Spitze-Spitze), KC = 2πa/D = 0,0042 bzw. U_max·T/D = 0,0060.
2. Notiz v5.2 §6: „β ≈ 3·10⁴“. Richtig sind 2,67·10⁴ (D = 0,2 m) bzw. 2,55·10⁴.
3. Notiz v5.2 §4.2 (iii): Die Bedingung prüft nur den Widerstand. In Wasser beträgt die zugesetzte Masse ≈ 2,6·M_ges; dort gilt die Rückstoßkinematik nicht.
4. Archiv-Vermerk 28.09. §2.3 und Werkstattbericht Z. 88: „Drift ∝ Dichte“ gilt für die stationäre Drift nicht. Die Werte −0,104…+0,692 mm/s sind nicht eingeschwungene v1-Fensterwerte (ρ = 1000); stationär sind es −0,294…+1,055 mm/s.
5. Forschungsrahmen v3.5 §5/§11: Die Skalierung C_medium ∝ ρ ist nicht begründet (L3-020; bei KC ≪ 1 sind Kraftgesetz und ρ-Abhängigkeit offen).
6. Präreg v2, Tabelle C: Elektrostatik und Luftpolster/zugesetzte Luftmasse fehlen; „⟨N⟩ = M·g“ meint das scheinbare Gewicht.
7. Aufgabentext: „KC = U_max·T/D = 2πa/D“ gilt nur für Sinusbewegung.

## 4 Kontrolle der Regeln

- Keine Repo-Datei geändert. Ausgaben liegen nur unter `rechnungen/linie_b/`.
- `find code docs -name __pycache__` lieferte am Ende keinen Treffer (Prüfung siehe Abschluss).
