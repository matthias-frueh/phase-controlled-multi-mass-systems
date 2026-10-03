# Abnahme der Werkzeuge AP-02 und AP-03

**Phasenkontrollierte Mehrmassensysteme · Phase-Controlled Multi-Mass Systems**
Matthias Früh · Stand 3. Oktober 2026 · Branch `claude/unpack-project-dataset-8dzd9c`, Basis Tag
`stand-2026-09-28` (= `main` `cd7be6a`)

*Nur Simulation, keine Messdaten.*

Gegenstand sind zwei Werkzeuge, die vor dem Einfrieren von Teil A der [Präregistrierung v2](praeregistrierung_v2_entwurf.md)
im Repository liegen müssen bzw. die Sicherheit der Läufe betreffen:

- **AP-02** Auslegungswerkzeug [`code/auslegung.py`](../code/auslegung.py) (Präregistrierung v2 §12, Werkzeug 2):
  Arbeitspunkt, Summen- und Zellkräfte, Prüfungen §5.3, zugesetzte Luftmasse.
- **AP-03** ereignisgenauer Löser [`code/ereignisloeser.py`](../code/ereignisloeser.py) mit Einzugsprüfung und
  numerischer Konvergenzprüfung, dazu die Attraktorkarten [`code/einzugsgebiete.py`](../code/einzugsgebiete.py) und
  [`docs/einzugsgebiete_v1_kandidat.md`](einzugsgebiete_v1_kandidat.md).

Die Arbeitspaketnummern und Erfolgskriterien stammen aus dem Arbeitsplan der Gesamtprojektanalyse vom 02.10.2026.

## 1 · Testlauf

Umgebung: Python 3.11.15, numpy 2.4.6, scipy 1.17.1, pandas 3.0.6, pytest 9.1.1, 4 Kerne.

```bash
pip install -r code/requirements.txt
python3 -m pytest tests -q                                 # schnelle Tests
PCMMS_SLOW=1 python3 -m pytest tests -q --durations=10     # alle Tests einschließlich der langen
python3 code/ereignisloeser.py --konvergenz                # Konvergenzstudie mit Tabellen (Abschnitt 3, AP-03)
```

| Lauf | Ergebnis und Dauer |
|---|---|
| schnelle Tests | 133 bestanden, 6 übersprungen (die langen), 58,6 s |
| `PCMMS_SLOW=1` | 139 bestanden, 261,4 s |

Die langen Tests (`@slow`, nur mit `PCMMS_SLOW=1`):

| Test | prüft |
|---|---|
| `test_auslegung.py::test_rho_baender_raster` | zu meidende ρ-Bänder bei ζ = 0,02 über ρ = 0,010 … 0,166 liegen in den Resonanzlücken (ρ ≈ 0,054, 0,065, 0,080, 0,105, 0,139, d. h. um 1/18, 1/15, 1/12, 1/9, 1/7) |
| `test_ereignisloeser.py::test_hotspot_lang_und_1ulp` | Hot-Spot (0°, 208,421°) über 60 s und mit um 1 ULP verschobener Phase: Zeitmittel = M·g bis auf den Randterm, Attraktor unverändert |
| `test_ereignisloeser.py::test_v1_kritischer_wurf_ueber_wurfphase` | V1-Kandidat synchron, Start in der Ruhelage: erster Hüpfwurf 0,30 / 0,24 / 0,26 / 0,60 m/s für t₀/T = 0 / 0,25 / 0,5 / 0,75, alle kleineren Stützwürfe kehren zurück |
| `test_ereignisloeser.py::test_v1_hunt_crossley_rueckkehr` | Hunt-Crossley-Gegenstück am V1-Kandidaten: Rückkehr unterhalb des ersten Hüpfwurfs |
| `test_ereignisloeser.py::test_zweiter_integrationsweg_alle_huepforbits` | zweiter, unabhängig geschriebener Ereignisintegrator an H2, L1, Insel und Referenz-P2 (Kelvin-Voigt gegen die geschlossene Lösung ≤ 10⁻¹⁴ s, ≤ 10⁻¹² relativ) und am Hunt-Crossley-Dreifachstoß (≤ 10⁻¹¹ s, ≤ 10⁻⁹ relativ; gegen rtol 10⁻¹³ ≤ 3·10⁻¹² s) |
| `test_ereignisloeser.py::test_konvergenzstudie_voll` | volle Konvergenzstudie (`--konvergenz`): alle Kriteriengruppen erfüllt; Raster geschlossen ≤ 10⁻¹⁵ s und ≤ 10⁻¹³ relativ; RK4 im Kontaktast Ordnung 4 bzw. 2, im Kelvin-Voigt-Hüpfbereich nicht monoton und nicht periodisch; Endzustand an der Einzugsgrenze in allen Stufen gleich, RK4-Grenze bei Δt um > 10⁻⁴ m/s verschoben |

Dauer der langen Tests im Endlauf: `test_konvergenzstudie_voll` 136,9 s, `test_rho_baender_raster` 26,3 s,
`test_v1_kritischer_wurf_ueber_wurfphase` 19,3 s, `test_zweiter_integrationsweg_alle_huepforbits` 9,1 s,
`test_hotspot_lang_und_1ulp` 6,7 s, `test_v1_hunt_crossley_rueckkehr` 4,6 s; alle bestanden.

Die bestehende Validierung `python3 code/linear_solver.py --validate` besteht unverändert.

## 2 · Einzugsgebiete (Ergänzung zu AP-03)

Gerechnet für Einzelmodul-, Schnitt- und Pilotläufe sowie zum Vergleich synchron und (0°, 180°); Einzelheiten,
Intervalle je Wurfphase und Grenzen der Aussage in [`einzugsgebiete_v1_kandidat.md`](einzugsgebiete_v1_kandidat.md),
Daten in [`../data/`](../data/README.md).

**Modellkonfiguration.** 1-FG-Modell der Engine, Kelvin-Voigt-Kontakt (Ablösung bei N = 0); Restmasse 0,350 kg,
drei Module à 0,100 kg (M = 0,650 kg), Egg-Profil THOLD = 0,65, Hub 8 mm Spitze-Spitze, f = 10 Hz, K = 1,5·10⁶ N/m,
ζ = 0,05. Start auf dem Kontaktast, Wurf als Geschwindigkeitsstoß Δv = −1 … +1 m/s (Schritt 0,05) in 16 Wurfphasen,
Zustandswechsel per Bisektion auf ≤ 0,005 m/s; 17 712 Zellen. Zusätzlich ζ = 0,02 / 0,10 / 0,20, Hunt-Crossley und
eine Feinprüfung im 0,01-Raster.

**Darstellung.** Das Einzugsgebiet ist nicht monoton: In fast jeder Wurfphase wechseln sich Hüpfbänder und
Rückkehr-Inseln ab. Die Ergebnisse stehen deshalb als Attraktorkarte (Δv-Intervalle je Wurfphase und Attraktor).
Das kleinste |Δv| mit Hüpfen ist nur die untere Einhüllende, keine Schwelle.

| Laufart (ζ = 0,05, Kelvin-Voigt) | Zellen mit Hüpfen | Attraktoren | untere Einhüllende des Hüpfens + / − |
|---|---|---|---|
| Einzelmodul L1 (L2, L3 bis auf die Zeitverschiebung gleich) | 37 von 656 (5,6 %) | K, H1 (P1, 481,9 N) | +0,416 / −0,484 m/s |
| Schnitt, 21 Punkte | 0 von 13 776 | K | – |
| Piloten, 3 | 0 von 1 968 | K | – |
| synchron (0°, 0°) | 374 von 656 (57,0 %) | K, H1 (P1, 483,7 N), H2 (P2, 968,6 N) | +0,225 / −0,263 m/s |
| (0°, 180°) | 92 von 656 (14,0 %) | K, H1 (P1, 482,4 N) | +0,381 / −0,444 m/s |

Wichtige Einschränkungen: Dass Schnitt und Piloten nicht hüpfen, gilt nur bei ζ = 0,05 und Kelvin-Voigt. Bei ζ = 0,02
hüpfen alle geprüften Schnittpunkte und der Pilot (110°, 252°), mit Hunt-Crossley auch (120°, 240°) bei ζ = 0,05.
Bei ζ = 0,20 hüpft keine der sechs geprüften Laufarten. Auch zurückkehrende Würfe erzeugen Summenkräfte von ≈ 1 kN
je m/s. Ein erreichter Hüpfzustand ist stabil und klingt im Modell nicht ab.

**Gegenprüfung.** Ein unabhängig geschriebener Ereignisintegrator bestätigt 90 von 90 Stichproben (darunter 51
Grenzpunkte) im Endzustand, λ auf ≤ 6·10⁻¹⁰ Prozentpunkte, Kräfte auf ≤ 10⁻³ N; doppelte Laufzeit ändert an 39
geprüften Zellen keinen Endzustand; Teilaufrufe des Skripts reproduzieren die CSV-Zeilen zeichengleich.

**Abnahmebefund, behoben.** `startzustand(…, "orbit")` fand für Hunt-Crossley am steifen Kandidaten den Kontaktast an
5 von 24 Wurfphasen nicht (Newton divergierte ab der Ruhelage in den Flug). Newton startet jetzt am Kelvin-Voigt-Orbit
gleicher Tangentensteifigkeit; Test `test_startzustand_hunt_crossley_am_kandidaten` (schlug vorher fehl). Die Karten
waren davon nicht betroffen, weil `einzugsgebiete.py` diesen Start schon verwendete.

## 3 · Erfolgskriterien und Nachweise

### AP-02 Auslegungswerkzeug

| Kriterium bzw. geforderter Umfang | Nachweis | Stand |
|---|---|---|
| Summe gleich `linear_solver.py` auf ≤ 10⁻⁶ N | Referenzsatz an zehn Punkten auf ≈ 10⁻¹⁴ N, auch μ = 0,4, 12 Hz, Sinus, starr (`test_referenz_*`, `test_skalierung_*`) | erfüllt |
| ε-Fenster [0,476; 0,750], K ≥ 1,03·10⁶ N/m für ρ ≤ 0,05 bei 10 Hz, Hubfenster 6,67–10,50 mm bei 3 × 100 g | [0,4763; 0,7500], K ≥ 1,0264·10⁶ N/m, 6,667–10,499 mm (`test_fenster_starr`) | erfüllt |
| Zellmodellwerte der Nachrechnung (3-FG) | Zellreserven, kleinste Zellkräfte und Kippfrequenzen auf 5 Stellen (`test_zellreserven_starr`, `test_zellkraefte_dynamisch`, `test_kippfrequenzen`); Summe der Zellkräfte = Summenkraft | erfüllt |
| ungleiche Module, gemessene Übertragung, Zell- und Modullagen, k_max, ∂ŷ/∂f | Python-Schnittstelle mit Tests (`test_superposition_gemessener_einzelmodule`, `test_indexbezogene_messung_mit_delta_delta`, `test_ungleiche_zellen_zeitbereich`, `test_ableitung_f`) | erfüllt; gemessene Harmonische nur über Python, kein Dateiformat für die CLI |
| f₁ = min(f_Hub, f_Kipp), Hub als Spitze-Spitze | Ausgabe `kennzahlen()`; `test_hub_ist_spitze_spitze` | erfüllt |
| zu meidende ρ-Bänder für ζ < 0,1 um 1/7, 1/9, 1/12, 1/15, 1/18 | `rho_baender()` bei ζ = 0,02 (`test_rho_baender_punkte`, langer Test `test_rho_baender_raster`) | erfüllt für ζ = 0,02; weitere ζ nicht als eigene Ausgabe |
| zugesetzte Luftmasse des Körpers als Zusatzmasse im Kontaktmodell | `Aufbau(m_luft, J_luft, xy_luft)`, CLI `--m-luft` (g), `--J-luft` (kg·m²); nur träge: M + m_L in Massenmatrix, Übertragung, f_n, ζ und Moden, das Gewicht M·g unverändert in F₀ (Bezug der Reserven), ε und μ; Vorgabe 0 gleich dem bisherigen Stand (`test_luft_grenzfall_bitgleich`, einmalig bitgleich gegen `6a9a1cd`); Hubübertragung analytisch auf ≈ 10⁻¹⁶ relativ, Zeitbereich gegen `scipy.signal.lsim` und gegen die RK4-Rechnung der Nachrechnung 10/2026 (`test_luft_*`, unten) | erfüllt als konfigurierbare Modellgröße; Wert für V1 offen (Vorgabe 0) |

**Zugesetzte Luftmasse.** Die Luft um den Körper und ein Quetschfilm unter seinem Boden wirken auf die Körperbewegung
als zusätzliche Trägheit, nicht als Gewicht; hinzu kommt ein Luftanteil, der davon abhängt, wie M bestimmt wird
(Gehäuseluft bzw. Ausgleich des Auftriebs, Absatz „Bestimmung von M und Zuordnung der Luft“ unten). Der Impulssatz
wird zu (M + m_L)·ẍ + C·ẋ + K·x = −Σ m_j·ë_j mit
N = M·g + (M + m_L)·ẍ + Σ m_j·ë_j; ⟨N⟩ = M·g bleibt exakt. Im 3-FG-Modell greift m_L im Punkt `xy_luft` an (Vorgabe
Zellschwerpunkt); J_L ist die zugesetzte Flächenträgheit um diesen Punkt, als Skalar für beide Kippachsen oder als
symmetrische, positiv semidefinite 2 × 2-Matrix, M_L = m_L·b_L·b_Lᵀ + diag(0, J_L) mit b_L = (1, x_L, y_L). J_L wird
in kg·m² angegeben, nicht als Trägheitsradius, weil J/m von der Strömung bzw. der Gehäuseform abhängt
(Quetschfilm-Scheibe R²/12, freie Scheibe 2R²/15). Getrennt geführt werden:

| Größe | geht ein in |
|---|---|
| Gewicht M·g | statische Zelllasten F₀ (Bezug der Reserven), Einfederung M·g/K, ε, μ |
| träge Masse M + m_L, Flächenträgheit J + J_L | Massenmatrix M_q, Übertragung, f_n = √(K/(M + m_L))/2π, ζ, Moden, f₁, k_b, K_min, ρ-Raster in `rho_baender()` |

ζ ist der Dämpfungsgrad der Hubmode mit der trägen Masse, wie ihn eine Ausschwingmessung liefert: Bei Vorgabe von ζ
ist C = 2ζ·√(K·(M + m_L)); ausgegeben werden ζ und ζ_M = C/(2√(K·M)). Wer C als Kontakteigenschaft festhält, übergibt
C; ζ sinkt dann mit √(M/(M + m_L)). So bezogen bleibt N/(M·g) = 1 + ε·g̃(t; φ, ρ, ζ) dieselbe Funktion; ε bleibt auf das
Gewicht bezogen, weil m_L kein Gewicht hat und keine Vorlast trägt. Bei starrer Auflage wirkt m_L nicht.

Annahmen: m_L ist frequenzunabhängig (einzusetzen ist der Wert bei der maßgeblichen Frequenz); die Luft ist
inkompressibel, ohne Schallabstrahlung und ohne eigene Dämpfung (eine Quetschfilmdämpfung, nach der Nachrechnung
0,5–0,6 N·s/m bei h = 3 mm, gehört gegebenenfalls in C); die Gegenfläche des Films liegt nicht im gemessenen
Kraftpfad. Gemessene Harmonische enthalten die Luft schon und werden zusammen mit m_luft > 0 oder J_luft ≠ 0
abgelehnt. Größenordnung der hydrodynamischen Zusatzmasse m_hyd (Mediumsreaktion) nach der Nachrechnung 10/2026
(Orientierung, keine Vorgabe): freie Scheibe (8/3)·ρ_L·R³ ≈ 2–5 g (Kasten 15–20 cm); mit Bodenspalt h Quetschfilm
m_hyd = π·ρ_L·R⁴/(8h) ≈ 8 g (h = 10 mm) bis 30 g (h = 3 mm, mit Zähigkeit) bei R = 0,113 m, Kippanteil
J_hyd = m_hyd·R²/12 (Teil von J_L).

**Bestimmung von M und Zuordnung der Luft.** Das Modell hat eine Masse M = m₀ + Σ m_j für das Gewicht M·g. Die
gesamte wirksame träge Masse (Bauteile, mitbewegte Innenluft, hydrodynamische Zusatzmasse) ist M + m_L; m_L ist also
diese träge Masse abzüglich M. Die hydrodynamische Zusatzmasse m_hyd (Reaktion der Außenluft, Quetschfilm) hat kein
Gewicht, erscheint weder in einer Wägung noch in der statischen Zelllast und gehört immer zu m_L. Volumina: V_Mat
Materialvolumen (Bauteile und Gehäusewände), V_innen freies Luftvolumen im geschlossenen Gehäuse, V_außen = V_Mat +
V_innen das von der Außenhaut umschlossene Volumen; ρ_L ≈ 1,2 kg/m³. Die Innenluft folgt der Hubbewegung bei
Wellenlängen ≫ Gehäuse wie ein starrer Körper (bei relativ zum Gehäuse ruhenden Einbauten ist ihr Impuls für jede
inkompressible Innenströmung ρ_L·V_innen·ẋ; zur Modulbewegung unten); ein leerer Kasten mit Innenmaß
20 × 20 × 10 cm enthält ≈ 4,8 g, 15 × 15 × 8 cm ≈ 2,2 g, abzüglich Bauteilvolumen etwas weniger. Wohin sie gehört,
hängt davon ab, wie M bestimmt wird:

| Bestimmung von M | M·g ist | m_L | Voraussetzungen und Näherungen |
|---|---|---|---|
| (a) aus den gewogenen Bauteilmassen: m₀ + Σ m_j = Summe der Massen aller Teile, die auf den Zellen ruhen und sich mit dem Körper bewegen, einschließlich der Module, ohne Luft | das Gewicht der Bauteile; die Innenluft fehlt in M | ρ_L·V_innen + m_hyd | gleiche Luftdichte innen und außen: Nur dann hebt der Auftrieb auf V_innen das Gewicht der Innenluft genau auf (belüftetes Gehäuse: 1 K Temperaturunterschied ändert die Dichte um ≈ 0,34 %, bei 4,8 g Innenluft weicht M·g dann um ≈ 0,016 g·g von der statischen Zelllast ab; dicht verschlossenes Gehäuse: Innendichte bleibt auf dem Wert beim Verschließen, maßgeblich ist die Änderung der Außendichte seither, 1 hPa ≈ 0,1 %, 1 K ≈ 0,34 %). Auftrieb auf das Materialvolumen vernachlässigt: M·g und ⟨N⟩ liegen um ρ_L·V_Mat·g über der realen statischen Zelllast, die träge Masse ist richtig |
| (b) aus der statischen Zelllast: M = Σ_c F_c,stat/g mit F_c,stat = Anzeige der Zelle c (als Kraft) bei aufgesetztem, ruhendem Körper minus Anzeige im Nullpunkt, in dem genau die in (a) gezählten Teile fehlen; m₀ = M − Σ m_j (ebenso, wenn der geschlossene Körper als Ganzes gewogen wird) | das wirksame Gewicht: Bauteile und Innenluft abzüglich des Auftriebs ρ_L·V_außen·g; die Innenluft steckt mit Gewicht und Hubträgheit in M | ρ_L·V_außen + m_hyd (Dichte der Außenluft); der Auftrieb mindert das Gewicht, nicht die Trägheit. Der Term zählt die Innenluft nicht doppelt, er ersetzt nur den Auftrieb, um den M kleiner ist als die bewegte Masse | keine Annahme über die Dichten (Zustand bei der Messung); die Zelllast enthält keine weiteren statischen Kräfte (Kabel, Elektrostatik), sonst gingen sie mit F/g in M und in die träge Masse ein. Zeigt die Zelle oder Waage Masseeinheiten nach Justierung mit Stahlgewichten, ist M um ≈ 1,5·10⁻⁴ relativ zu groß. Mit vereinfachtem m_L = ρ_L·V_innen + m_hyd fehlt der Trägheit ρ_L·V_Mat |

Der Auftrieb auf das Materialvolumen beträgt relativ ρ_L/ρ_Mat (1,5·10⁻⁴ Stahl, 4,4·10⁻⁴ Aluminium, ≈ 10⁻³
Kunststoff). Vernachlässigt man ihn, ergeben beide Wege dasselbe m_L = ρ_L·V_innen + m_hyd. In (a) sind wahre Massen
gemeint. Eine mit Stahlgewichten (8000 kg/m³) justierte Waage zeigt den konventionellen Wägewert
m·(1 − ρ_L/ρ_Mat + ρ_L/8000 kg/m³); er enthält den Materialauftrieb nur, soweit er den gleich schwerer Stahlgewichte
übersteigt (Stahl ≈ 0, Aluminium ≈ 2/3, Kunststoff ≈ 85 %). Soweit er enthalten ist, verschiebt sich die Abweichung
vom Gewicht in die Trägheit; M·g liegt dann für jeden Werkstoff um ≈ 1,5·10⁻⁴·M·g über der statischen Zelllast.

Im 3-FG-Modell greift jeder Anteil von m_L in seinem Schwerpunkt an; `xy_luft` ist ihr massengewichteter
Schwerpunkt, J_L ihre Kippträgheit um diesen Punkt einschließlich der Steiner-Anteile. In (a) sind die Anteile die
Innenluft (im Schwerpunkt von V_innen, mit ihrer verminderten Eigenträgheit, unten) und m_hyd (mit J_hyd). In (b)
sind es ρ_L·V_außen (im Auftriebsmittelpunkt, nur als Punktmasse) und m_hyd; (x₀, y₀) folgt aus der Verteilung der
F_c,stat, und die Kippträgheit der Innenluft gehört mit der Restmasse zu J₀ (die Vorgabe J₀ = m₀·ρ₀² zählt sie
starr). Beim Kippen dreht die nahezu reibungsfreie Innenluft nicht starr mit: Ihre Eigenträgheit liegt unter dem
Starrkörperwert, beim leeren Kasten 20 × 20 × 10 cm mit Kippachse parallel zu einer 20-cm-Kante (ideale Strömung) bei
≈ 0,45 des starren Drehträgheitsmoments m·(a² + c²)/12 (a = 20 cm, c = 10 cm), bei 4,8 g ≈ 9·10⁻⁶ kg·m²; exakt ist
nur der Steiner-Anteil ihres Schwerpunkts.

Unabhängig von der Bestimmung von M vernachlässigt das Modell die Verdrängung der Innenluft durch die bewegten
Module: Bei inkompressibler Luft im starren Gehäuse ist die Anregung (in Bewegungsgleichung und N)
Σ_j (m_j − ρ_L·V_j)·ë_j statt Σ_j m_j·ë_j, mit der Dichte der Innenluft und dem Volumen V_j des bewegten Teils von
Modul j; relativ ρ_L/ρ_j mit ρ_j = m_j/V_j.

Wirkung am V1-Kandidaten (G0, 3 × 100 g, 8 mm, M = 0,65 kg, 10 Hz, K = 1,5·10⁶ N/m, ζ = 0,05 fest, wo nicht anders
angegeben), mit dem Werkzeug gerechnet; in allen Zeilen sind (a), (b), robust, ρ-Band und Signal erfüllt:

| m_L | f_n [Hz] | k_b | kleinste Zellreserve (Schnitt φ₂ = 100°) | ΔF_Zelt ungebändert (maßgeblich) [N] | F_min(120°, 240°) der Summe [N] |
|---|---|---|---|---|---|
| 0 (bisheriger Stand) | 241,77 | 12 | 41,136 % | 0,5603 | 5,4088 |
| 4,8 g (nur Gehäuseluft, leerer Kasten 20 × 20 × 10 cm) | 240,89 | 12 | 41,124 % | 0,5617 | 5,4093 |
| 9,7 g | 239,99 | 11 | 41,111 % | 0,5632 | 5,4100 |
| 30 g (Quetschfilm, h = 3 mm) | 236,38 | 11 | 41,040 % | 0,5697 | 5,4127 |
| 30 g, C fest (ζ = 0,0489) | 236,38 | 11 | 41,030 % | 0,5701 | 5,4127 |
| 30 g, J_L = J_hyd = m_hyd·R²/12 = 3,2·10⁻⁵ kg·m² | 236,38 (f_Kipp 280,94 statt 282,83) | 11 | 41,075 % | 0,5697 | 5,4127 |

Ab m_L = K/(2π·240 Hz)² − M = 9,64 g sinkt k_b von 12 auf 11, weil f₁ unter 12·2f fällt; die bandbegrenzten Größen
springen dann (ΔF_Zelt für k ≤ k_max 0,587 → 0,637 N), maßgeblich bleibt der ungebänderte Wert. Nahe einer Resonanz
ist die Wirkung größer: Am Simulationsreferenzsatz (μ = 1, K = 10⁴ N/m, 2f ≈ f_n) verschieben 4,6 g F_min(140°, 240°)
um 64 mN.

Nachweise (`tests/test_auslegung.py`): Ohne Luft, auch mit expliziten Nullen und an verschobenem Angriffspunkt, sind
`bewerte`, `pruefung` und `kennzahlen` bitgleich, M_q, H, f_n, ζ und C entsprechen den Formeln ohne Luft
(`test_luft_grenzfall_bitgleich`). Die Hubübertragung H_a = (K + iωC)/(K − (M + m_L)ω² + iωC) gilt für k = 1 … 40 auf
≈ 10⁻¹⁶ relativ (Testschranke 10⁻¹², `test_luft_hub_analytisch`). Bei unsymmetrischem Aufbau mit Luft außerhalb des
Zellschwerpunkts bleibt F₀ bitgleich, ⟨N⟩ = M·g und ⟨F_c⟩ = F₀ gelten (`test_luft_statik_und_mittelwert`); Hub- und
Kippfrequenzen folgen aus M + m_L bzw. J + J_L (`test_luft_kippfrequenzen`). Ungleiche Zellsteifigkeiten mit 30 g
bei (20, −15) mm und anisotropem J_L stimmen mit `scipy.signal.lsim` auf 2,8·10⁻⁶ N überein, bei einer Luftwirkung von
0,033 N (`test_luft_ungleiche_zellen_zeitbereich`). Die F_min-Verschiebungen treffen die unabhängige
RK4-Zeitbereichsrechnung der Nachrechnung 10/2026 an vier Fällen (μ = 1 / 0,4, K = 10⁴ … 10⁶ N/m, 1,94 und 4,60 g) auf
die angegebenen vier Stellen (`test_luft_gegen_zeitbereich_nachrechnung`). Bei gleichem ρ und ζ ist N unverändert und `rho_baender()`
liefert dieselbe Fensterbreite (`test_luft_normierte_antwort_unveraendert`). CLI und Fehleingaben (negativ, nan, inf:
Rückgabewert 2; unsymmetrisches oder indefinites J, falsche Formen, gemessene Harmonische mit Luft: `ValueError`) in
`test_luft_cli`, `test_luft_cli_fehler`, `test_luft_ungueltige_eingaben`. Der dauerhafte Grenzfalltest vergleicht mit
den geschlossenen Formeln, nicht mit der alten Fassung; die Bitgleichheit gegen `6a9a1cd` ist einmalig geprüft (in der
Abnahme an 19 Aufbauten und 7 CLI-Aufrufen, nach der Nachbesserung erneut an 9 Aufbauten und den JSON-Ausgaben von
`--candidate`, `--reference --point 120 240` und `--runs --geometry G60h`). Die Textausgabe nennt zusätzlich m_luft und
J_luft, JSON und `kennzahlen()` enthalten zusätzlich m_luft, J_luft, xy_luft, M_traege und zeta_M.

**Abnahmebefund, behoben.** Ein skalares J0 wurde bisher auf alle vier Einträge des Kippblocks addiert, also auch auf
die Nebendiagonale ([[J, J], [J, J]]). Jetzt wirkt es als J0·I für beide Kippachsen. J0 und J_luft werden auf
Symmetrie (Toleranz 10⁻⁹·max|J|, danach symmetrisiert) und positive Semidefinitheit geprüft. Kein Aufrufer, Test oder
Dokument im Repository nutzte ein skalares J0; Matrix-J0 und die Vorgabe bleiben bitgleich
(`test_flaechentraegheit_skalar_und_rundung`).

Weitere Lücken: Das Kriterium (a) prüft je Zelle die Kraft, die Auflagerkoordinate je Zelle folgt daraus (im
Kelvin-Voigt-Modell zwingend). Die Geometrien G0, G60h und „zentral“ beruhen auf angenommenen Werten (Zellradius
100 mm, Restmasse als Scheibe); die reale Lage von Zellen und Modulen ist nach Präregistrierung §12 offen.
Neuer Befund des Werkzeugs: Am Kandidaten mit Modulen über den Zellen bindet im 3-FG-Modell der Schnittpunkt
φ₂ = 100° (Zellreserve 41,1 %), nicht der synchrone Lauf (42,6 %); (a) bleibt erfüllt. Zur Luftmasse: Ihr Wert für V1
hängt von Bodenspalt und Gehäuse ab und ist bis zu einer Messung oder Festlegung offen. Nicht modelliert sind die
Frequenzabhängigkeit der Quetschfilmmasse (h = 3 mm: 30,0 g bei 10 Hz, 27,8 g bei 60 Hz) und seine Dämpfung (nur über
C nachzubilden). Die CLI kennt nur ein isotropes J_luft um den Zellschwerpunkt; ein anisotropes J_luft und ein anderer
Angriffspunkt gehen nur über Python. Der ereignisgenaue Löser und die Attraktorkarten rechnen ohne zugesetzte
Luftmasse; im Zeitbereich wirkt sie auch während des Flugs.

### AP-03 Ereignisgenauer Löser und Einzugsprüfung

| Kriterium bzw. geforderter Umfang | Nachweis | Stand |
|---|---|---|
| Kontaktast gleich `linear_solver.py` auf ≤ 10⁻⁶ N | Wellenform 1,3·10⁻⁷ N, F_min(120°, 240°) = 5,330390 N (`test_kontaktast_gleich_linear_solver`) | erfüllt |
| Satelliteninsel (35°, 116°): λ 75,815 %, F_max 39,47 N, Kontaktorbit F_min 0,3665 N (≤ 0,1 %) | 75,8154 %, 39,473 N, 0,366516 N (`test_satelliteninsel_bistabil`) | erfüllt |
| V1-Kandidat synchron, ζ = 0,05: Hüpfschwelle 0,30 m/s bei t₀ = 0 (0,24–0,60 m/s über die Wurfphase), Stoßspitze ≈ 483,7 N | 0,25 m/s kehrt zurück, 0,30 m/s hüpft mit 483,66 N; über die Wurfphase 0,30 / 0,24 / 0,26 / 0,60 m/s (`test_v1_huepfschwelle`, langer Test `test_v1_kritischer_wurf_ueber_wurfphase`) | erfüllt, Start in der Ruhelage; wegen Nichtmonotonie als erster Hüpfwurf zu lesen, nicht als Schwelle |
| Einzugsgebiet für alle Laufarten, auch Einzelmodul-, Schnitt- und Pilotläufe | Attraktorkarten für L1 (L2, L3), 21 Schnittpunkte, 3 Piloten, synchron, (0°, 180°) mit ζ- und Kontaktgesetzvergleich; unabhängig gegengeprüft (Abschnitt 2) | erfüllt im Modell mit Auslegungswerten; Neuberechnung mit gemessenen K, ζ und Kontaktgesetz nach Phase 0 nötig |
| Stoßspitzen mit mindestens zwei Kontaktgesetzen | Kelvin-Voigt und Hunt-Crossley (`test_v1_kontaktgesetze_vergleich`, `test_stoss_*`); Hunt-Crossley ≈ 1 050 N statt 484 N; numerisch konvergiert (Einzelstoß gegen geschlossene Formeln ≤ 6·10⁻¹¹ relativ, Stoßspitzen der Hüpforbits unter Verfeinerung ≤ 2·10⁻¹⁰ relativ, unten) | erfüllt; Zuordnung des Hunt-Crossley-Gesetzes ist eine Annahme |
| Standardausgaben Randterm, RK4-gewichtetes Mittel | Randterm R = M·Δv_S/T_w; Zeitmittel und Schiefe über Gauß-Legendre-Quadratur der Periodenintegrale statt RK4-gewichtet, ohne Abtastfehler; ⟨N⟩ = M·g + R: Kelvin-Voigt geschlossen ≤ 10⁻¹² N, über solve_ivp ≤ 10⁻¹⁰ N, Hunt-Crossley durch die Quadratur am Kontaktrand begrenzt (≈ 5·10⁻⁷ N mit 8 Gauß-Knoten, 2·10⁻⁸ N mit 16; für die Kenngrößen ohne Belang) | erfüllt (exaktes statt RK4-gewichtetes Mittel) |
| Standardausgabe Δt/2-Kontrolle | ersetzt durch die Konvergenzprüfung des Lösers (`konvergenz()`, `--konvergenz`, langer Test `test_konvergenzstudie_voll`): 53 von 53 Kriteriengruppen an zwölf Fällen beider Kontaktgesetze; Festschritt-RK4-Gegenprobe; zweiter, unabhängig geschriebener Integrationsweg in den Tests (Begründung und Ergebnisse im folgenden Abschnitt) | erfüllt durch Ersatz; ohne festen Zeitschritt ist Δt/2 nicht anwendbar, im Kelvin-Voigt-Hüpfbereich auch für die Engine keine Fehlerschätzung |

Lücken: 1 Freiheitsgrad, keine Kippmoden, keine zugesetzte Luftmasse; im 0,05-Raster fehlen bei L1 oberhalb
|Δv| ≈ 0,6 m/s schmale Hüpfbänder (die Feinprüfung zeigt sie); die Feinprüfung umfasst nur 5 von 26 Laufarten; der
Anlauf über eine Frequenzrampe ist nicht Teil der Karten; Hunt-Crossley ist nur für positive Würfe ohne Bisektion
gerechnet.

### AP-03: Numerische Konvergenzprüfung (Ersatz der Δt/2-Kontrolle)

**Begründung.** Die Δt/2-Kontrolle ist für Festschritt-Integratoren gedacht: Die Differenz zweier Läufe mit Δt und
Δt/2 schätzt den Fehler, wenn die Ordnung des Verfahrens bekannt ist und sich nicht ändert. Der ereignisgenaue Löser
hat keinen Zeitschritt. Kelvin-Voigt (unterkritisch) löst er je knickfreiem Stück geschlossen, Hunt-Crossley mit
solve_ivp; Kontaktwechsel werden als Nullstellen lokalisiert. Seine Genauigkeit bestimmen vier Parameter:

| Parameter | Standard | bestimmt |
|---|---|---|
| Abtastraster h der Schaltfunktion | min(T/10 000, 2π/(300·ω_n)) | nur die Erkennung eines Wechsels; die Zeitpunkte setzt brentq (xtol 10⁻¹⁵ s) auf der geschlossenen bzw. dichten Lösung, bei solve_ivp schon dessen Ereignissuche |
| rtol von solve_ivp (DOP853) | 10⁻¹¹ | Hunt-Crossley, überkritische Dämpfung, Frequenzrampe und die Gegenprobe zur geschlossenen Lösung |
| Gauß-Legendre-Quadratur der Periodenintegrale | 8 Knoten je ≤ 100 µs | Zeitmittel, Rest der Identität ⟨N⟩ = M·g + R, Schiefe |
| Differenzenschritt der Floquet-Matrix | 10⁻⁹ m, 10⁻⁷ m/s | Newton-Fixpunkt z* und Floquet-Multiplikatoren μ |

Die Studie verfeinert jeden Parameter einzeln (h × 2 … 1/8, rtol 10⁻⁸ … 10⁻¹², 8 / 16 / 32 Knoten, Differenzenschritt
× 10 / 1 / 0,1), jeweils ab demselben Orbitzustand, und misst Aufsetz- und Ablösezeiten, λ, Zahl der Aufsetzer,
Stoßspitzen und F_min / F_max, den Rest der Identität, die Schiefe, z* (ein Newton-Schritt je Stufe) und |μ|. Die
Absicht der Δt/2-Kontrolle, nämlich zu zeigen, dass das Ergebnis nicht von der Diskretisierung abhängt, prüft
zusätzlich eine Festschritt-RK4 im Schema der Engine (`rk4_festschritt()`, Δt = T/2000 … T/16 000) an denselben
Fällen. Sie zeigt, dass eine Δt/2-Differenz im Kelvin-Voigt-Hüpfbereich auch für die Engine keine Fehlerschätzung ist
(siehe Gegenprobe unten). Die Standardergebnisse des Lösers sind durch die Studie nicht verändert: `simulate()` ist
unverändert, 15 Vergleiche gegen `6a9a1cd` (Einzelstoß beider Gesetze bei vier ζ, `simulate` an drei Punkten,
Hunt-Crossley-`simulate`, `newton`, `wurf`, `startzustand`) sind bitgleich, und die Testdatei des alten Stands
besteht gegen den neuen Code.

**Fälle.** Hüpforbits: V1 synchron H1 (Kelvin-Voigt und Hunt-Crossley), V1 synchron H2 (P2), V1 L1 H1,
Hunt-Crossley-Dreifachstoß bei (120°, 240°), Satelliteninsel (35°, 116°) im Hüpfzustand, Referenz (0°, 0°) P2.
Kontaktorbits: Insel (Kelvin-Voigt), V1 synchron (beide Gesetze). Einzelstoß 0,5 m/s beider Gesetze gegen
geschlossene Formeln (`stoss_geschlossen()`). Wurf an der Einzugsgrenze K | H1 (V1 synchron, t₀ = 0).

**Schranken** (`KONV_SCHRANKE`, `KONV_REST`): Zeitpunkte 10⁻⁹ s; Kräfte und Stoßspitzen 10⁻⁶ relativ zur größten Kraft
des Falls; λ 10⁻⁶ Prozentpunkte; gleiche Zahl der Aufsetzer; z* 10⁻⁹ m bzw. 10⁻⁷ m/s; |μ| und √|det J| 10⁻⁶;
Stoßzahl 10⁻⁹; Schiefe 10⁻⁶ relativ; Rest der Identität 10⁻¹² N (geschlossen), 10⁻¹⁰ N (solve_ivp), 10⁻⁶ N
(Hunt-Crossley); gleicher Endzustand. Bei rtol gelten sie auf den Stufen ≤ 10⁻¹¹ (Standard und feiner), die Stufen
10⁻⁸ … 10⁻¹⁰ dienen der Ordnungsschätzung; bei Raster, Quadratur und Differenzenschritt auf allen Stufen. Referenz ist
für Kelvin-Voigt die geschlossene Lösung, für Hunt-Crossley rtol 10⁻¹³ (keine geschlossene Lösung; DOP853 konvergiert
in rtol nicht monoton, die Änderung ist deshalb keine Fehlerschätzung), für √|det J| der Liouville-Wert, wo er bekannt
ist (exp(−C·p·T/M) im Kelvin-Voigt-Dauerkontakt, exp(−1,5·α·g·p·T) für jeden Hunt-Crossley-Orbit).

**Ergebnis: 53 von 53 Kriteriengruppen erfüllt** (20 Rastergruppen als Kontrolle der Erkennung, davon 12 mit
solve_ivp, wo h die Zeitpunkte nicht beeinflusst; 12 rtol, 10 Quadratur, 10 Differenzenschritt, 1 Endzustand an der
Einzugsgrenze). Größte Änderung je Größe:

*Kelvin-Voigt.* Raster: geschlossen, h × 2 … 1/8 gegen die Standardeinstellung. rtol: solve_ivp mit rtol 10⁻¹¹ und
10⁻¹² gegen die geschlossene Lösung. |μ|: größte Änderung über alle Stufen. Die Zahl der Aufsetzer ist in allen Stufen
gleich.

| Fall | Kontaktwechsel [s] Raster / rtol | Kräfte, Stoßspitzen [rel.] Raster / rtol | λ [%-P.] Raster / rtol | \|μ\| |
|---|---|---|---|---|
| V1 synchron H1 | 3,5·10⁻¹⁸ / 6,7·10⁻¹³ | 5,9·10⁻¹⁶ / 1,0·10⁻¹¹ | 0 / 1,3·10⁻¹² | 1,1·10⁻⁸ |
| V1 synchron H2 (P2) | 5,2·10⁻¹⁷ / 3,1·10⁻¹³ | 8,1·10⁻¹⁵ / 3,9·10⁻¹² | 5,7·10⁻¹⁴ / 9,1·10⁻¹³ | 6,6·10⁻⁸ |
| V1 L1 H1 | 6,8·10⁻¹⁷ / 1,3·10⁻¹⁴ | 1,0·10⁻¹⁴ / 1,6·10⁻¹¹ | 5,7·10⁻¹⁴ / 1,0·10⁻¹² | 3,0·10⁻⁸ |
| Insel (35°, 116°) Hüpfzustand | 3,6·10⁻¹⁶ / 1,1·10⁻¹³ | 8,6·10⁻¹⁵ / 1,1·10⁻¹¹ | 3,6·10⁻¹³ / 1,1·10⁻¹⁰ | 1,3·10⁻⁸ |
| Referenz (0°, 0°) P2 | 1,4·10⁻¹⁷ / 6,4·10⁻¹³ | 3,5·10⁻¹⁶ / 3,8·10⁻¹² | 1,4·10⁻¹⁴ / 1,2·10⁻¹⁰ | 6,4·10⁻⁸ |
| Insel Kontaktorbit | – (kein Wechsel) | 1,8·10⁻¹⁶ / 3,2·10⁻¹³ | 0 / 0 | 1,2·10⁻⁹ |
| V1 synchron Kontaktast | – (kein Wechsel) | 1,3·10⁻¹⁶ / 1,3·10⁻¹⁰ | 0 / 0 | 1,2·10⁻¹⁰ |

solve_ivp konvergiert gegen die geschlossene Lösung etwa mit Ordnung 1 in rtol (Steigungen der Ausgleichsgeraden für
Zeitpunkte, Kräfte, Rest und z* überwiegend 0,6 bis 1,3). Der Rest der Identität liegt geschlossen mit 8 bis 32 Knoten
auf Rundungsniveau (≤ 3·10⁻¹⁵ N), über solve_ivp bei rtol ≤ 10⁻¹¹ bei ≤ 5·10⁻¹¹ N. Am steifen V1-Kontaktast bleibt
die Kraftabweichung über solve_ivp bei ≈ 10⁻¹⁰ relativ stehen; dort begrenzt atol (K·10⁻¹⁵ m ≈ 1,5·10⁻⁹ N), nicht rtol.
An beiden Kontaktorbits trifft √|det J| den Wert exp(−C·p·T/(2M)) auf ≤ 1,2·10⁻⁹.

*Hunt-Crossley* (nur solve_ivp). rtol: Stufen 10⁻¹¹ und 10⁻¹² gegen rtol 10⁻¹³ (Änderung, kein Fehler). Zweiter Weg:
Abweichung der Standardeinstellung (rtol 10⁻¹¹) vom unabhängigen Integrator der Tests, also eine Fehlerschätzung. Das
Raster h ändert nichts außer Rundung (Zeitpunkte und λ 0, Kräfte ≤ 3·10⁻¹⁶). Die Zahl der Aufsetzer ist in allen
Stufen gleich.

| Fall | Kontaktwechsel [s] rtol / zweiter Weg | Kräfte, Stoßspitzen [rel.] rtol / zweiter Weg | λ [%-P.] rtol | √\|det J\| − Liouville | Rest [N] 8 / 16 / 32 Knoten |
|---|---|---|---|---|---|
| V1 synchron H1 | 6,8·10⁻¹³ / 6,8·10⁻¹³ | 4,3·10⁻¹¹ / 5,2·10⁻¹¹ | 7,9·10⁻¹² | 3,4·10⁻⁸ (Differenzenschritt × 10: 8,7·10⁻⁷) | 4,8·10⁻⁷ / 1,7·10⁻⁸ / 7,8·10⁻¹⁰ |
| V1 (120°, 240°) Dreifachstoß | 7,8·10⁻¹² / 5,8·10⁻¹² | 1,7·10⁻¹⁰ / 2,0·10⁻¹⁰ | 8,5·10⁻¹¹ | 1,3·10⁻⁷ (alle Differenzenschritte: 1,8·10⁻⁷) | 2,6·10⁻⁷ / 9,4·10⁻⁹ / 5,2·10⁻¹⁰ |
| V1 synchron Kontaktast | – (kein Wechsel) | 1,1·10⁻¹⁰ / – | 0 | 4,1·10⁻⁸ (alle Differenzenschritte: 1,4·10⁻⁷) | 1,9·10⁻¹² in allen Stufen |

Alle Hunt-Crossley-Orbits der Studie haben ein komplex konjugiertes Paar von Multiplikatoren, also |μ| = √|det J|.
Den Rest der Identität begrenzt bei Hunt-Crossley die Quadratur, nicht der Integrator: Der Verlauf δ^1,5 ist am
Kontaktrand nicht glatt; am Kontaktast ohne Kontaktrand bleibt der Rest bei 1,9·10⁻¹² N, und eine adaptive Quadratur
über die dichte Lösung ergab in der Nachrechnung der Abnahme ≈ 2·10⁻¹⁰ N. Die Schiefe ändert sich mit der Knotenzahl
um ≤ 4·10⁻¹⁰ relativ.

*Einzelstoß 0,5 m/s gegen die geschlossenen Formeln* (`stoss_geschlossen()`; Kelvin-Voigt: Stoßspitze und Ablösung
bei N = 0 aus der gedämpften Schwingung; Hunt-Crossley: geschlossene Phasenbahn δ(u), Spitze als Maximum über u per
Brent, Stoßzahl aus `e_hc`):

| Gesetz | Größe | geschlossen | Raster h × 2 … 1/8 | solve_ivp rtol ≤ 10⁻¹¹ |
|---|---|---|---|---|
| Kelvin-Voigt | Stoßzahl e | 0,8587581018 | 1,1·10⁻¹⁶ | 6,6·10⁻¹³ |
| Kelvin-Voigt | Stoßspitze | 459,8146824 N | 1,2·10⁻¹⁶ relativ | 4,7·10⁻¹² relativ |
| Kelvin-Voigt | Kontaktdauer | 2,004701388 ms | 8,7·10⁻¹⁹ s | 1,8·10⁻¹⁵ s |
| Hunt-Crossley | Stoßzahl e | 0,8587581018 | wie rtol 10⁻¹¹ (h ohne Einfluss) | 3,0·10⁻¹¹ |
| Hunt-Crossley | Stoßspitze | 986,2141009 N | wie rtol 10⁻¹¹ (h ohne Einfluss) | 5,9·10⁻¹¹ relativ |

*Endzustand an der Einzugsgrenze* (Kelvin-Voigt, V1 synchron, t₀ = 0, Start auf dem Kontaktast; Läufe wie die Karte,
80 Perioden, Klassifikation über die letzten 20). Die Grenze K | H1 liegt bei Standardeinstellung bei
v_g = 0,2944898 m/s (Bisektion aus der Kartenklammer [0,29375; 0,296875] m/s auf 9,5·10⁻⁸ m/s). Würfe bei
v_g − 10⁻⁶ m/s enden in allen acht Stufen (geschlossen h × 2 … 1/8; solve_ivp rtol 10⁻⁸, 10⁻¹⁰, 10⁻¹²) im Kontaktast,
Würfe bei v_g + 10⁻⁶ m/s im Hüpfen.

**Festschritt-RK4-Gegenprobe.** `rk4_festschritt()` rechnet im Schema der Engine (kraftbasierte Kontaktregel in jeder
Stufe, Kraftstichprobe zu Schrittbeginn) ab dem exakten Orbitzustand; Referenz ist der Ereignislöser, für
Hunt-Crossley mit rtol 10⁻¹³. Δt = T/2000 = 50 µs wie die Engine. Ordnung: Steigung der Ausgleichsgeraden über
Δt … Δt/8. Perioden 40·p … 100·p: größte Abweichung je Periode vom exakten Orbit; eine Spanne von ẋ im
Poincaré-Schnitt ≈ 0 heißt, der RK4-Orbit ist periodisch. Stoßspitzen sind Stichproben im Raster Δt und enthalten
den Abtastfehler, so wie die Engine sie ausgibt.

| Fall | Gesetz | Größe | Δt | Δt/2 | Δt/4 | Δt/8 | Ordnung, Befund |
|---|---|---|---|---|---|---|---|
| V1 synchron Kontaktast | Kelvin-Voigt | max \|N_k − N(t_k)\| [N] | 5,8·10⁻⁷ | 3,6·10⁻⁸ | 2,3·10⁻⁹ | 1,4·10⁻¹⁰ | 4,0 (Knickstellen des Profils auf dem Raster) |
| Insel Kontaktorbit | Kelvin-Voigt | max \|N_k − N(t_k)\| [N] | 2,5·10⁻⁶ | 3,1·10⁻⁷ | 7,7·10⁻⁸ | 3,9·10⁻⁸ | 2,0 (Knick im Schritt, lageabhängig) |
| V1 synchron Kontaktast | Hunt-Crossley | max \|N_k − N(t_k)\| [N] | 5,3·10⁻⁶ | 3,2·10⁻⁷ | 1,6·10⁻⁸ | 1,5·10⁻⁸ | 3,0 (bei Δt/8 Grenze der Referenz) |
| V1 synchron H1 | Kelvin-Voigt | Stoßspitze nach einer Periode [rel.] | 1,1·10⁻³ | 4,1·10⁻⁴ | 9,2·10⁻⁵ | 2,6·10⁻⁴ | 0,8, nicht monoton |
| V1 synchron H1 | Kelvin-Voigt | ẋ nach einer Periode [m/s] | 3,7·10⁻⁴ | 1,2·10⁻⁴ | 4,4·10⁻⁵ | 1,1·10⁻⁴ | 0,6, nicht monoton |
| V1 synchron H1 | Kelvin-Voigt | Stoßspitze, Perioden 40–100 [rel.] | 6,1·10⁻³ | 2,2·10⁻³ | 1,0·10⁻³ | 6,1·10⁻⁴ | gestreut |
| V1 synchron H1 | Kelvin-Voigt | Aufsetzzeit, Perioden 40–100 [s] | 5,5·10⁻⁴ | 1,9·10⁻⁴ | 8,5·10⁻⁵ | 5,2·10⁻⁵ | gestreut |
| V1 synchron H1 | Kelvin-Voigt | Spanne ẋ im Poincaré-Schnitt, Perioden 40–100 [m/s] | 6,1·10⁻³ | 2,4·10⁻³ | 7,9·10⁻⁴ | 6,3·10⁻⁴ | nicht periodisch |
| V1 synchron H1 | Hunt-Crossley | ẋ nach einer Periode [m/s] | 7,1·10⁻⁵ | 1,1·10⁻⁵ | 3,4·10⁻⁸ | 1,8·10⁻⁸ | 4,4, monoton |
| V1 synchron H1 | Hunt-Crossley | Spanne ẋ im Poincaré-Schnitt, Perioden 40–100 [m/s] | 2,1·10⁻⁴ | 8,8·10⁻¹⁰ | 2,5·10⁻¹² | 1,5·10⁻¹² | periodisch ab Δt/2 |
| V1 (120°, 240°) Dreifachstoß | Hunt-Crossley | Stoßspitze nach einer Periode [rel.] | 1,4·10⁻³ | 4,4·10⁻⁴ | 1,5·10⁻⁴ | 2,1·10⁻⁵ | 2,0, monoton |
| V1 synchron, Wurf t₀ = 0 | Kelvin-Voigt | Einzugsgrenze per Bisektion − v_g [m/s] | +1,6·10⁻⁴ | +2,4·10⁻⁵ | −1,1·10⁻⁵ | +6,8·10⁻⁶ | nicht monoton (Bisektion auf 2·10⁻⁶); bei Δt und Δt/2 keine scharfe Grenze |

Die übrigen Kelvin-Voigt-Hüpforbits verhalten sich gleich: Über die Perioden 40·p … 100·p ist der RK4-Orbit in keiner
Stufe periodisch (Spanne von ẋ bei Δt/8: H2 1,3·10⁻³, L1 2,0·10⁻³, Insel 5,2·10⁻⁵, Referenz-P2 6,0·10⁻⁵ m/s; Stoßspitze
bei Δt bis 4,6·10⁻³ relativ), die Stoßzahl je Periode bleibt aber gleich. Folgerung: Im Kontaktast konvergiert die RK4
mit Ordnung 2 bis 4; bei Δt liegen die Kraftstichproben um ≤ 3·10⁻⁵ N (Kelvin-Voigt) bzw. ≤ 8·10⁻⁵ N (Hunt-Crossley)
neben dem exakten Wert. Im Hüpfbereich springt die Kelvin-Voigt-Kraft beim Aufsetzen um C·|ẋ| (≈ 52 N bei V1 H1); ein
Schritt mit dem Sprung ist nur von erster Ordnung, die beobachteten Steigungen nach einer Periode liegen zwischen 0,3
und 3,3 und sind nicht monoton (V1 H1: ẋ-Fehler von Δt/4 nach Δt/8 von 4,4·10⁻⁵ auf 1,1·10⁻⁴ m/s). Über viele
Perioden misst eine Δt/2-Differenz dort die Streuung eines unregelmäßigen RK4-Attraktors, nicht den Fehler. Mit
Hunt-Crossley (Kraft beim Aufsetzen stetig) konvergiert die RK4 glatter, der Orbit ist ab Δt/2 periodisch. An der
Einzugsgrenze hat die RK4 bei Δt und Δt/2 keine scharfe Grenze: In Schritten von 2·10⁻⁵ m/s wechselt ihr Endzustand
im Bereich v_g − 1,0·10⁻⁴ … v_g + 1,6·10⁻⁴ m/s (Δt) bzw. v_g − 4·10⁻⁵ … v_g + 2·10⁻⁵ m/s (Δt/2) mehrfach, die
Bisektion der Tabelle findet einen dieser Wechsel; ab Δt/4 gibt es in diesem Raster nur einen Wechsel (ergänzende
Abtastung der Abnahme, nicht Teil der Studie). Bei Δt = 50 µs hüpft also schon ein Wurf 10⁻⁴ m/s unter der wahren
Grenze (`test_wurf_an_der_einzugsgrenze`), während einzelne Würfe darüber zurückkehren.

**Unabhängige Gegenwege.** Kelvin-Voigt: zwei Integrationswege im Modul (geschlossen gegen solve_ivp); sie teilen
Modellfunktionen, Ereignissuche und Auswertung, prüfen also die Integration, nicht den Modellaufbau. Beide Gesetze:
ein unabhängig geschriebener Ereignisintegrator in den Tests (`_zweiter_weg` in `tests/test_ereignisloeser.py`:
Engine-Profil `finesweep.z_egg_zdd`, eigene Kraftgesetze, Kontaktregeln und Knickstellen, Radau mit rtol 10⁻¹²). Er
trifft die geschlossene Kelvin-Voigt-Lösung an fünf Hüpforbits auf ≤ 4·10⁻¹⁶ s und ≤ 1,4·10⁻¹³ relativ, was ihn selbst
validiert; die Hunt-Crossley-Abweichungen stehen in der Tabelle oben, gegen rtol 10⁻¹³ sind es ≤ 10⁻¹² s
(`test_zweiter_integrationsweg`, langer Test `test_zweiter_integrationsweg_alle_huepforbits`). Hunt-Crossley
zusätzlich über exakte Invarianten: Liouville-Determinante und Einzelstoß. Die unabhängige Nachrechnung der Abnahme
(eigener Ereignisintegrator mit Gauß-Legendre-Kollokation, nicht im Repository) fand dieselben Abweichungen:
Kelvin-Voigt Ereigniszeiten ≤ 6·10⁻¹⁵ s, Spitzen ≤ 1,3·10⁻¹³ relativ, |μ| auf 8 Stellen; Hunt-Crossley bei rtol 10⁻¹¹
≤ 5,8·10⁻¹² s und ≤ 2,1·10⁻¹⁰ relativ; v_g bestätigt.

**Reproduktion.**

```bash
python3 code/ereignisloeser.py --konvergenz                  # alle zwölf Fälle, Tabellen A–F
python3 code/ereignisloeser.py --konvergenz stoss insel-k    # Teilstudie (Fälle siehe unten)
PCMMS_SLOW=1 python3 -m pytest tests/test_ereignisloeser.py -q \
    -k "konvergenz or zweiter or rk4 or einzugsgrenze or gauss or abtastraster"
```

Fälle: `v1-h1`, `v1-h1-hc`, `v1-h2`, `l1-h1`, `hc-dreifach`, `insel`, `ref-p2`, `insel-k`, `v1-k`, `v1-k-hc`,
`stoss`, `wurf`. In Python liefert `ereignisloeser.konvergenz()` die Kriteriengruppen mit allen Stufenwerten,
`konv_zaehlung()` die Zählung nach Art der Gruppe.

**Grenzen.** Die Studie prüft die Numerik des 1-FG-Modells, nicht das Modell selbst (Kontaktgesetz, Parameter,
fehlende Kippmoden, keine zugesetzte Luftmasse im Zeitbereich). Der Endzustand an einer Einzugsgrenze ist nur an
einer Stelle geprüft (Kelvin-Voigt, V1 synchron, t₀ = 0), ebenso die RK4-Grenzverschiebung; für Hunt-Crossley gibt es
keine Grenzprüfung. Für Hunt-Crossley-Orbits fehlt eine geschlossene Lösung; den Fehler belegen der zweite Weg und die
Invarianten, die rtol-Änderung allein nicht. Nicht variiert sind die Teilintervallbreite der Quadratur (≤ 100 µs), die
brentq-Toleranz (10⁻¹⁵ s, an der Grenze der Gleitkommagenauigkeit für t) und atol von solve_ivp (10⁻¹⁵ m,
10⁻¹² m/s). z* und |μ| je Stufe stammen aus einem Newton-Schritt ab dem gemeinsamen Orbitzustand. Die Startwerte der
Orbits stehen als gerundete Konstanten im Code und werden bei Standardeinstellung mit Newton verfeinert.

## 4 · Was aus der Abnahme für die nächsten Schritte folgt

- Die Karten sind mit gemessenen K, ζ und Kontaktgesetz (Phase 0, P0.4) neu zu rechnen, bevor Teil B registriert wird.
- Nennlast und Überlastanschlag müssen Summenkräfte von einigen 100 N bis ≈ 1 kN aufnehmen oder Stöße konstruktiv
  begrenzen; die Verteilung auf die Zellen braucht ein Modell mit Kippfreiheitsgraden.
- Ein erreichter Hüpfzustand bleibt bestehen; die Präregistrierung (§9.1 G6, §9.2 S2) erfasst schon kurzes Abheben,
  ein Anhalten des Antriebs bei erkanntem Hüpfen ist zusätzlich festzulegen.
- Ergebnisse der Festschritt-RK4 der Engine im Kelvin-Voigt-Hüpfbereich (Stoßspitzen, Aufsetzzeiten, Lage von
  Einzugsgrenzen) sind mit dem ereignisgenauen Löser zu rechnen; eine Δt/2-Differenz der Engine ist dort keine
  Fehlerschätzung.
- Die zugesetzte Luftmasse ist als Modellgröße umgesetzt. Offen bleiben ihr Wert für V1 (Bodenspalt, Gehäuse; bis zur
  Festlegung oder Messung Vorgabe 0) und, falls er nicht vernachlässigbar ist, ihre Ergänzung im ereignisgenauen Löser.
- Offen in AP-02: Dateiformat für gemessene Harmonische (bisher nur über die Python-Schnittstelle).
