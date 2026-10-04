# P2 · Gegenprüfung der Prüfgruppe „linie_b“ – Protokoll

> **Vermerk zur Übernahme (04.10.2026).** Protokoll aus der Gesamtprojektanalyse 10/2026, Stand 02.10.2026, unverändert bis auf Pfade und Quellenangaben. Geprüft wurde der Repository-Stand `cd7be6a` (28.09.2026) mit der Präregistrierung v2 vom 25./28.09.2026; die späteren Änderungen aus PR #13 und PR #14 (unter anderem Präregistrierung v2 mit Arbeitsfestlegungen, `code/auslegung.py`, `code/ereignisloeser.py`) sind nicht eingearbeitet. Alle Zahlen sind Simulation oder Analytik, keine Messdaten. Verweise wie „L1a-019“, „P1 §3“ oder „B01–B14“ zeigen auf Arbeitsdokumente der Analyse, die nicht im Repository liegen. Quellen außerhalb des Repositorys sind als „(lokaler Bestand, nicht im Repository)“ gekennzeichnet. Startbefehle und Grenzen je Gruppe: [`rechnungen/README.md`](../../README.md).

Stand: 02.10.2026. Rolle: unabhängiger Gegenprüfer. Ziel war es, die Befunde der Gruppe zu widerlegen.
Alle Skripte sind selbst geschrieben. Gruppen- und Repo-Code wird nicht importiert, nur `linear_solver`-Werte
als Zahl zitiert. Wo möglich, wurde ein anderer Rechenweg gewählt.

Gemeinsamer Aufruf (im Verzeichnis `rechnungen/linie_b/verifikation/`):

```
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../../../code timeout 540 python3 <skript>.py > <skript>.out
```

Laufzeiten: jeder Lauf unter 30 s. Geprüft wurden LB-01, LB-05, LB-06, LB-07, LB-09/LB-14, LB-10, LB-11 und LB-13.
LB-02, LB-03, LB-04, LB-08 und LB-12 wurden nicht eigenständig nachgerechnet; zu LB-12 gibt es nur einen Zahlenabgleich in vb6.

Kennzeichnung im Text: **[R]** eigene Rechnung, **[Q]** Quellenangabe, **[A]** Annahme.

---

## LB-01 · KC und Kennzahlen des Trägers (Linie B)

- **Frage:** KC ≈ 0,009 (Notiz v5.2) oder ≈ 0,004 (P1)? Stimmen Re, β, δ?
- **Methode:** Geschlossene Formeln statt numerischer Integration. Modulweg in der Schnellphase
  s = V_FAST·tf·T·2/π; Träger synchron mit Spitze-Spitze RATIO·s. Das Maximum über das 13×13-Raster wurde mit der
  Mittelpunktsregel (N = 20 000) bestimmt. Parameter wie im Skript, Z. 44–57 [Q].
- **Ergebnis [R]:** s = 1,33690 mm. Trägerhub Spitze-Spitze 0,26738 mm, also a = 0,13369 mm. U_max = 12,000 mm/s.
  - KC_a = 2πa/D: 0,00420 / 0,00430 / 0,00485 für D = 0,2 m / √(4A/π) / √A.
  - KC_U = U_max·T/D: 0,00600 / 0,00614 / 0,00693.
  - Mit a = 0,3 mm wäre KC = 0,00942.
  - Re = 160 / 156 / 139; β = 2,667·10⁴ / 2,546·10⁴ / 2,0·10⁴.
  - δ = 0,6910 mm, δ/a = 5,17, Re_s = 0,0749; in Wasser δ = 0,178 mm.
  - Die größte Trägeramplitude im Raster liegt bei synchroner Phasung (0°, 0°). Für die Triphasik ist a = 6,20 µm.
  - Fundstelle Notiz v5.2, Z. 210–214 [Q]: „a ≈ 0,3 mm … KC = 2πa/D ≈ 0,009 … β ≈ 3×10⁴“.
- **Urteil:** bestätigt, alle Zahlen stimmen auf 3–4 Stellen.
- **Einschränkung:** Liest man „Trägeramplitude“ in der Notiz als Spitze-Spitze-Wert (0,267 mm ≈ 0,3 mm), ist die Abweichung nur
  eine Definitionsfrage. KC ≪ 1 gilt in jedem Fall.
- **Reproduktion:** `python3 vb1_kc_analytisch.py` → `vb1_kc_analytisch.out`

## LB-05 · Periodische Lösung des integrierten Modells gegen die gemittelte Bilanz

- **Frage:** Stimmt das integrierte Modell mit der Bilanz überein, auch bei ρ = 1,2?
- **Methode:** Eigene Implementierung mit solve_ivp (DOP853, rtol 1e-12, max_step T/400) statt festschrittigem RK4.
  Schießverfahren mit brentq auf V(T) − V₀. Die Bilanz wurde mit Mittelpunktsregel bei N = 2·10³, 2·10⁴ und 2·10⁵ gerechnet.
- **Ergebnis [R]:**
  - Relative Abweichung periodisch gegen Bilanz: −5,2·10⁻⁶ … +5,0·10⁻⁶. Die Gruppe nannte −4,6·10⁻⁶ … +9,3·10⁻⁶.
  - ρ = 1,2 gegen ρ = 1000: +5,2·10⁻⁶ (0,0), +5,1·10⁻⁶ (120,240), +3,9·10⁻⁶ (221,54/110,77).
  - Diskretisierung: N = 2000 Linksrechteck (Skript) gegen N = 2·10⁵ Mittelpunkt ergibt einen Unterschied von 6·10⁻¹⁰ m/s (relativ 6·10⁻⁷).
- **Urteil:** bestätigt (≤ 1·10⁻⁵).
- **Einschränkung:** Bei ρ = 1,2 ist τ/T ≈ 5·10⁴. Das Schießproblem ist dort schlecht konditioniert, die Abweichungen von
  ~5·10⁻⁶ sind numerisches Rauschen. Die Übereinstimmung folgt dort schon aus der Mittelungstheorie, Fehler O(T/τ); der Test bei
  ρ = 1,2 trägt deshalb wenig zusätzlich bei. Alles gilt nur im Zweiterm-Ansatz (LB-02).
- **Reproduktion:** `python3 vb2_dichte_bilanz_periodisch.py` → `vb2_dichte_bilanz_periodisch.out`, Teile (a) und (b)

## LB-06 · „ρ geht nicht in v_d ein“ – Urteil „widerlegt“ für „Drift ∝ Dichte“

- **Frage:** Trägt die Rechnung das Urteil „widerlegt“ für die Aussagen „Drift ∝ Mediendichte, null im Vakuum“
  (Archiv-Vermerk 28.09., Z. 91 [Q]) und „Der Effekt skaliert mit der Dichte des Mediums und verschwindet im Vakuum“
  (Werkstattbericht, Z. 88 [Q])?
- **Methode:** Unabhängige Bilanz wie bei LB-05. Modell B mit linearem Zusatzterm c₁: c₁v_d + c₂ρ⟨(v_d+v)|v_d+v|⟩ = 0.
  c₁ = 6πμR [A] und zusätzlich der Faktor 0,1 bzw. 10 darauf. Lokaler Exponent d ln v_d / d ln ρ bei ρ = 1,2.
- **Ergebnis [R]:**
  - Mit c₁ = 0 enthält die Bilanz ρ nicht: v_d = +1,05490 bzw. −0,081024 mm/s. Dagegen F̄_A ∝ ρ (1,396·10⁻⁴ N in Wasser,
    1,675·10⁻⁷ N in Luft) und τ ∝ 1/ρ (5,84 s bzw. 4870 s). Das stimmt mit der Gruppe überein.
  - Mit c₁ = 6πμR = 3,3·10⁻⁵ N·s/m: ρ* = 0,26 bzw. 1,86 kg/m³; v_d/v_d(c₁=0) bei ρ = 1,2 beträgt 0,83 bzw. 0,40. Auch das
    stimmt mit der Gruppe überein. Der lokale Exponent bei ρ = 1,2 liegt bei 0,17 (0,0) bzw. 0,61 (120,240).
  - Mit 10·c₁ (z. B. zusätzliche Lager- oder Aufhängungsdämpfung) steigt er auf 0,68 bzw. 0,94, die Drift ist dann nahezu
    ∝ ρ. Für ρ → 0 gilt bei jedem c₁ > 0 v_d ∝ ρ → 0, also „null im Vakuum“.
- **Urteil:** eingeschränkt. Der Code-Befund ist richtig: Im Skriptmodell mit c₁ = 0 ist die stationäre Drift dichteunabhängig.
  „Widerlegt“ für die Quellaussagen geht aber zu weit:
  - Das Modell mit c₁ = 0 ist bei ρ → 0 singulär (τ → ∞).
  - Jeder zusätzliche lineare Widerstand macht v_d bei Luftdichte merklich bis nahezu proportional zu ρ.
  - Die Kraft und die nicht eingeschwungenen Fensterwerte (LB-07) skalieren ohnehin mit ρ.
  - Richtig ist: „Kraft ∝ ρ; stationäre Drift nur im reinen Quadratmodell dichteunabhängig; mit linearem Zusatzwiderstand
    unterhalb von ρ* ∝ ρ.“
  - Die Werkstattbericht-Aussage ist missverständlich, aber nicht widerlegt.
- **Reproduktion:** `python3 vb2_dichte_bilanz_periodisch.py`, Teile (a) und (c)

## LB-07 · v1-Fensterkarte (Werkstattbericht-Spanne)

- **Methode:** Vektorisiertes RK4 über alle 169 Punkte, v1-Verfahren laut Quelltext `pcmms_fluid_drift.py`, Z. 35–39 und 65–82 [Q].
  Dazu DT = 25 µs. Für ρ = 1,2 halbanalytische Störungsrechnung 1. Ordnung, V ≈ c·∫(−v_osc|v_osc|).
- **Ergebnis [R]:**
  - Archiv-CSV (10 Kopien, MD5-gleich) reproduziert: max |Diff| = 4,9·10⁻¹¹ m/s. Spanne −0,104101 … +0,691635 mm/s;
    der Werkstattbericht, Z. 88 [Q], nennt dieselbe Spanne.
  - DT = 25 µs ändert um ≤ 8·10⁻¹⁰ m/s.
  - ρ = 1,2: −0,000155 … +0,001359 mm/s. Die Störungsrechnung stimmt auf 6·10⁻⁴ (relativ).
  - Verhältnis der Fensterwerte ρ = 1000 / ρ = 1,2: 508,8 … 769,3; ρ = 1,2 / 0,12: 9,994 … 9,999.
- **Urteil:** bestätigt.
- **Reproduktion:** `python3 vb3_v1_fensterkarte_vektor.py` → `.out`, `.csv`

## LB-09 / LB-14 · Luftkräfte an den Modulen; Linie-A-Egg und Gleichrichtung

- **Methode:** Modulharmonische analytisch über geschlossene Fourierintegrale der Halbsinus-Lagebögen, kein FFT.
  - Zeitumkehrsymmetrie und Raum-Zeit-Antisymmetrie numerisch geprüft.
  - ⟨V|V|⟩ für Kombinationen und deren Spiegelbilder berechnet.
  - Impulsbilanz der Innenluft im geschlossenen Gehäuse.
- **Ergebnis [R]:**
  - Harmonische identisch mit der Gruppe: |v_k| = 0,23817 / 0,039248 / 0,011289 m/s, |a_k| = 14,965 / 4,9321 / 2,1280 m/s².
  - Zeitumkehr z(0,65T − t) = z(t) gilt bis 4·10⁻¹⁸ m. Daher ist ⟨f(v)⟩ = 0 für jede ungerade Momentanfunktion f
    (⟨v|v|⟩, ⟨v³⟩, ⟨v⁵⟩ = 0).
  - Eine Antisymmetrie z(t+D) = −z(t) gibt es nicht (Restfehler ≥ 3,5 mm). Ein Mittelwert höherer Ordnung aus
    gedächtnisbehafteten, dissipativen Kräften ist durch Symmetrie also nicht ausgeschlossen.
  - ⟨V|V|⟩: (0,0) = 0, (120,240) = 4·10⁻²⁰, (100,240) = +7,667·10⁻⁵, (260,120) = −7,667·10⁻⁵ m²/s². Die Ungeradheit unter
    φ → −φ ist bestätigt (LB-14).
  - Offene Luft: Scheibe R = 4 cm bei f 3,252·10⁻³ N = 0,0994·u_c; Kugel 1,393·10⁻⁴ N.
  - Im geschlossenen Gehäuse wirkt die Innenluft auf das Gesamtsystem nur mit ρ_L·V_mod·a_mod; das ist das 1,5·10⁻⁴-Fache der
    Modulträgheit, beim 100-g-Stahlmodul 2,3·10⁻⁴ N. Der Gleichanteil ist exakt 0, weil er die Zeitableitung eines periodischen
    Impulses ist.
- **Urteil:** bestätigt.
- **Einschränkungen:**
  - „≤ 0,1·u_c“ ist für die angenommene Scheibe knapp (0,0994).
  - „Kein Gleichanteil“ in offener Luft ist nur für quasistationäre bzw. lineare Kraftgesetze belegt.
  - Im geschlossenen Gehäuse gilt beides unabhängig vom Strömungsmodell, durch Impulserhaltung.
- **Reproduktion:** `python3 vb6_module_symmetrie_ueberschlaege.py` → `.out`

## LB-10 · Zugesetzte Luftmasse am Körper

- **Frage:** Stimmen dF_min und ΔN_k, und trägt die Einordnung „0,38·u_c; 2,6 % von ΔF_Zelt; bis zu 1,2·10⁻² N“?
- **Methode:**
  - (a) Nichtlineares Kontaktmodell im Zeitbereich mit eigenem vektorisiertem RK4, Kontaktregel wie die Engine, DT = 50 µs,
    3 s Einschwingen und 1 s Auswertung.
  - (b) Lineare Lösung im Frequenzbereich mit analytischen Fourierkoeffizienten. Abgleich: F_min(120,240) = 5,330390 N wie
    linear_solver [Q].
  - Szenarien: wie die Gruppe (K = 1e4, μ = 1) und A4-konsistent (μ = 0,4, K = 1e5 / 1e6, ζ fest) [Q: Anhang A4, §5.3(b)].
- **Ergebnis [R]:**
  - Gruppenwerte reproduziert, (a) und (b) identisch:
    - Triphasik: dF_min = +1,242·10⁻² N, |ΔN₃| = 1,29·10⁻² N.
    - (100,240): dF_min = −9,54·10⁻³ N, |ΔN₂| = 0,131 N.
  - **Nicht berichtet:** Bei (140,240) ist dF_min = +6,39·10⁻² N (4,60 g) bzw. +2,64·10⁻² N (1,94 g). Das ist das Fünffache der
    angegebenen Obergrenze „bis zu 1,2·10⁻² N“. Die Zeltdifferenz F_min(120) − F_min(140) ändert sich um −5,15·10⁻² N.
  - **Skalen vermischt:** u_c = 0,0327 N und ΔF_Zelt = 0,4693 N gehören zum Beispiel „starr, μ = 0,4“ [Q: A4]. Für die
    Referenz K = 1e4, μ = 1 gilt ΔF_Zelt = 4,5627 N, daraus u_c ≤ 0,318 N [R, vb7].
    - Konsistent gerechnet sind 1,24·10⁻² N dort 0,04·u_c (0,27 % von ΔF_Zelt).
    - Selbst der Maximalwert 6,4·10⁻² N entspricht nur 0,20·u_c.
  - Die Referenz K = 1e4 (f_n = 19,7 Hz) verletzt außerdem Präreg §5.3(b), 3f ≤ f₁/2; dafür wäre K ≥ 9,2·10⁴ N/m nötig.
  - A4-konsistent (μ = 0,4), freie Scheibe 4,60 g:
    - K = 1e5: |dF_min| ≤ 6,1·10⁻³ N (0,19·u_c).
    - K = 1e6: ≤ 5,1·10⁻⁴ N (0,016·u_c).
  - **2–5 g sind keine Obergrenze.** Steht der Gehäuseboden mit Spalt h über einer Grundplatte, ist die Quetschfilm-Trägheit
    πρR⁴/(8h) maßgeblich (vb5): bei 10 Hz 8,2 g (h = 10 mm), 30,0 g (h = 3 mm), 91,5 g (h = 1 mm, zäh, Faktor 1,2).
    Das verschiebt f_n um −0,6 bis −2,2 % (h = 10 bzw. 3 mm).
    - Mit exakter Impedanz bei K = 1e5, μ = 0,4: |dF_min| ≤ 9,7·10⁻³ N (h = 10 mm), ≤ 2,45·10⁻² N (h = 3 mm, 0,75·u_c).
    - Bei K = 1e6, μ = 0,4: ≤ 3,2·10⁻³ N (h = 3 mm), ≤ 8,7·10⁻³ N (h = 1 mm).
- **Urteil:** eingeschränkt. Die Zahlen sind richtig gerechnet, aber unvollständig (140°). Die Relevanzangaben vergleichen
  Größen aus verschiedenen Szenarien. Der Massenbereich der Gruppe unterschätzt den Effekt, wenn ein Bodenspalt besteht.
- **Bestätigt bleibt:** Der Effekt ist linear, ⟨N⟩ ändert sich nicht (d⟨N⟩ ≤ 10⁻¹² N bei Dauerkontakt). Er steckt in den
  gemessenen Einzelmodulantworten (Phase 0) und ist für H1–H3 kein Artefakt; relevant ist er für Simulation ↔ Messung.
- **Reproduktion:** `python3 vb4_gehaeuse_zusatzmasse_zeitbereich.py`, `python3 vb5_quetschfilm_impedanz.py`, `python3 vb7_skalen_uc.py`

## LB-11 · Quetschfilm unter dem Körper: Dämpfung und Gleichanteil

- **Methode:**
  - Exakte lineare Impedanz Z(ω) = iωπρR⁴/(8hΦ), Φ = 1 − tanh(kh/2)/(kh/2), k = √(iω/ν) (eigene Herleitung).
    Grenzfälle: Trägheit πρR⁴/(8h), zäh 3πμR⁴/(2h³).
  - Gleichanteil reibungsfrei und nichtlinear über F = −πρR⁴ḧ/(8h) + 3πρR⁴ḣ²/(16h²), gemittelt entlang h(t) = h₀ + z(t)
    ohne Kleinamplitudennäherung.
  - Randbedingung A: p(R) = p₀. Randbedingung B: Eintrittsverlust beim Einströmen.
- **Ergebnis [R]:**
  - c_sq im zähen Grenzfall: 13,73 / 0,509 / 0,0137 N·s/m, wie die Gruppe. Exakt bei 10 Hz: 13,76 / 0,581 / 0,038 N·s/m.
  - Gleichanteil-Skala der Gruppe bestätigt: K = 1e4, μ = 1, (100,240), h = 3 mm ergibt 5,14·10⁻³ N (nichtlinear, A) gegen
    5,16·10⁻³ N (Skala).
  - Mit B sinkt er auf 2,5·10⁻⁴ N; bei der Triphasik kehrt sich das Vorzeichen um (−1,6·10⁻⁵ N). Die Skala ist also eine obere
    Abschätzung.
  - A4-konsistent (K = 1e5, μ = 0,4, h = 3 mm): ≤ 1,2·10⁻⁵ N (4·10⁻⁴·u_c).
  - Die Herleitung der Gruppe nutzt dieselbe reibungsfreie Theorie, lässt aber deren Term 1. Ordnung (Trägheit πρR⁴/(8h),
    5- bis 6-mal größer als 4,6 g bei h = 3 mm) in LB-10 weg.
- **Urteil:** eingeschränkt. Formel und Zahlen stimmen. „Skala ≤ 0,16·u_c“ gilt aber nur für den resonanten, nach §5.3(b)
  unzulässigen Referenzfall und für Randbedingung A, und u_c stammt aus einem anderen Szenario. Im zulässigen steifen Bereich
  ist der Gleichanteil vernachlässigbar. Relevant ist dann der lineare Teil (Trägheit, Dämpfung, siehe LB-10).
- **Einschränkung:** Bei h = 1 mm und K = 1e4 ist z_pp ≈ h, die Linearisierung gilt dort nicht. Die Geometrie (R, h) ist
  angenommen [A]. Dass die Luftkraft die Wägezellen umgeht, ist ebenfalls eine Annahme [A]; für Füße auf Wägezellen über einer
  Grundplatte ist sie plausibel (Präreg §5.1 [Q]).
- **Reproduktion:** `python3 vb5_quetschfilm_impedanz.py` → `.out`

## LB-13 · Tabelle C: Luft- und elektrostatische Kräfte fehlen

- **Methode:** grep nach luft, elektrostat, auftrieb, akust, aufladung, strömung, konvektion, ladung, esd, luftdruck, medium,
  schall in Präreg-Entwurf und -Anhang (Repo) sowie in der lokalen Überarbeitung vom 01.10. Dazu Tabelle C (Anhang
  Z. 647–669) gelesen. Elektrostatik und Auftrieb in vb6 nachgerechnet.
- **Ergebnis:**
  - [Q] Keine Treffer; die einzigen Treffer sind „verschwindet“. Tabelle C nennt keine Luft- oder elektrostatischen Kräfte.
    Am nächsten kommt „Kraftnebenschluss“ (Nebenpfad); das trifft den Quetschfilm physikalisch, ist aber auf Kabel bzw.
    Lagerung gemünzt.
  - [R] σ²A/(2ε₀) = 2,26·10⁻⁵ / 2,26·10⁻³ / 0,226 N bei Feldstärken von 0,4 / 4 / 38 % der Durchschlagfeldstärke.
    Auftrieb 0,0212 / 0,0471 N.
- **Urteil:** bestätigt.
- **Einschränkung:** Die Formulierung „Elektrostatik möglicherweise größter Gleichterm“ ist überdehnt. Ein konstanter Anteil
  fällt wie der Auftrieb in Δ⟨N⟩ heraus. Relevant sind nur zeitliche Änderungen gegenüber den Referenzläufen. Die
  Ladungsdichten sind reine Annahmen.

---

## Zusatzbefunde

1. LB-10 (140,240): dF_min = +6,4·10⁻² N wurde nicht berichtet; „bis zu 1,2·10⁻² N“ ist falsch.
2. Skalenvermischung in LB-10 und LB-11: u_c = 0,0327 N und ΔF_Zelt = 0,4693 N stammen aus dem Fall starr/μ = 0,4. Die
   resonante Referenz ist nach Präreg §5.3(b) kein zulässiger Arbeitspunkt.
3. Die Quetschfilm-Trägheit unter dem Gehäuseboden (8–30 g bei h = 10–3 mm) übersteigt die Freiraum-Zusatzmasse deutlich.
   Für Tabelle C ist sie als linearer Nebenpfad (Kategorie Kraftnebenschluss) einzuordnen und bei der Bestimmung von f₁
   bzw. bei Simulationsvergleichen zu berücksichtigen.
4. Der Quetschfilm-Gleichanteil hängt stark von der Randbedingung ab: Mit Eintrittsverlust sinkt er auf 1/20 bis 1/10, und
   das Vorzeichen kann sich umkehren.

## Hygiene

Keine Datei außerhalb von `verifikation/` angelegt; Repo-Code nicht verändert. Prüfung auf `__pycache__` am Ende siehe Rückgabe.
