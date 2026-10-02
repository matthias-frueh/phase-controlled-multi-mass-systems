# Abnahme der Werkzeuge AP-02 und AP-03

**Phasenkontrollierte Mehrmassensysteme · Phase-Controlled Multi-Mass Systems**
Matthias Früh · Stand 2. Oktober 2026 · Branch `claude/unpack-project-dataset-8dzd9c`, Basis Tag
`stand-2026-09-28` (= `main` `cd7be6a`)

*Nur Simulation, keine Messdaten.*

Gegenstand sind zwei Werkzeuge, die vor dem Einfrieren von Teil A der [Präregistrierung v2](praeregistrierung_v2_entwurf.md)
im Repository liegen müssen bzw. die Sicherheit der Läufe betreffen:

- **AP-02** Auslegungswerkzeug [`code/auslegung.py`](../code/auslegung.py) (Präregistrierung v2 §12, Werkzeug 2):
  Arbeitspunkt, Summen- und Zellkräfte, Prüfungen §5.3.
- **AP-03** ereignisgenauer Löser [`code/ereignisloeser.py`](../code/ereignisloeser.py) mit Einzugsprüfung, dazu die
  Attraktorkarten [`code/einzugsgebiete.py`](../code/einzugsgebiete.py) und
  [`docs/einzugsgebiete_v1_kandidat.md`](einzugsgebiete_v1_kandidat.md).

Die Arbeitspaketnummern und Erfolgskriterien stammen aus dem Arbeitsplan der Gesamtprojektanalyse vom 02.10.2026.

## 1 · Testlauf

Umgebung: Python 3.11.15, numpy 2.4.6, scipy 1.17.1, pandas 3.0.6, pytest 9.1.1, 4 Kerne.

```bash
pip install -r code/requirements.txt
python3 -m pytest tests -q                      # schnelle Tests
PCMMS_SLOW=1 python3 -m pytest tests -q --durations=6   # alle Tests einschließlich der vier langen
```

| Lauf | Ergebnis | Dauer |
|---|---|---|
| schnelle Tests | 98 bestanden, 4 übersprungen (lang) | 42 s |
| `PCMMS_SLOW=1` | 102 bestanden, keiner übersprungen | 106 s |

Die vier langen Tests:

| Test | prüft | Dauer |
|---|---|---|
| `test_auslegung.py::test_rho_baender_raster` | zu meidende ρ-Bänder bei ζ = 0,02 über ρ = 0,010 … 0,166 liegen in den Resonanzlücken (ρ ≈ 0,054, 0,065, 0,080, 0,105, 0,139, d. h. um 1/18, 1/15, 1/12, 1/9, 1/7) | 28,8 s |
| `test_ereignisloeser.py::test_v1_kritischer_wurf_ueber_wurfphase` | V1-Kandidat synchron, Start in der Ruhelage: erster Hüpfwurf 0,30 / 0,24 / 0,26 / 0,60 m/s für t₀/T = 0 / 0,25 / 0,5 / 0,75, alle kleineren Stützwürfe kehren zurück | 22,6 s |
| `test_ereignisloeser.py::test_hotspot_lang_und_1ulp` | Hot-Spot (0°, 208,421°) über 60 s und mit um 1 ULP verschobener Phase: Zeitmittel = M·g bis auf den Randterm, Attraktor unverändert | 7,1 s |
| `test_ereignisloeser.py::test_v1_hunt_crossley_rueckkehr` | Hunt-Crossley-Gegenstück am V1-Kandidaten: Rückkehr unterhalb des ersten Hüpfwurfs | 4,9 s |

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
| zugesetzte Luftmasse des Körpers als Zusatzmasse im Kontaktmodell | – | **offen** |

Weitere Lücken: Das Kriterium (a) prüft je Zelle die Kraft, die Auflagerkoordinate je Zelle folgt daraus (im
Kelvin-Voigt-Modell zwingend). Die Geometrien G0, G60h und „zentral“ beruhen auf angenommenen Werten (Zellradius
100 mm, Restmasse als Scheibe); die reale Lage von Zellen und Modulen ist nach Präregistrierung §12 offen.
Neuer Befund des Werkzeugs: Am Kandidaten mit Modulen über den Zellen bindet im 3-FG-Modell der Schnittpunkt
φ₂ = 100° (Zellreserve 41,1 %), nicht der synchrone Lauf (42,6 %); (a) bleibt erfüllt.

### AP-03 Ereignisgenauer Löser und Einzugsprüfung

| Kriterium bzw. geforderter Umfang | Nachweis | Stand |
|---|---|---|
| Kontaktast gleich `linear_solver.py` auf ≤ 10⁻⁶ N | Wellenform 1,3·10⁻⁷ N, F_min(120°, 240°) = 5,330390 N (`test_kontaktast_gleich_linear_solver`) | erfüllt |
| Satelliteninsel (35°, 116°): λ 75,815 %, F_max 39,47 N, Kontaktorbit F_min 0,3665 N (≤ 0,1 %) | 75,8154 %, 39,473 N, 0,366516 N (`test_satelliteninsel_bistabil`) | erfüllt |
| V1-Kandidat synchron, ζ = 0,05: Hüpfschwelle 0,30 m/s bei t₀ = 0 (0,24–0,60 m/s über die Wurfphase), Stoßspitze ≈ 483,7 N | 0,25 m/s kehrt zurück, 0,30 m/s hüpft mit 483,66 N; über die Wurfphase 0,30 / 0,24 / 0,26 / 0,60 m/s (`test_v1_huepfschwelle`, langer Test `test_v1_kritischer_wurf_ueber_wurfphase`) | erfüllt, Start in der Ruhelage; wegen Nichtmonotonie als erster Hüpfwurf zu lesen, nicht als Schwelle |
| Einzugsgebiet für alle Laufarten, auch Einzelmodul-, Schnitt- und Pilotläufe | Attraktorkarten für L1 (L2, L3), 21 Schnittpunkte, 3 Piloten, synchron, (0°, 180°) mit ζ- und Kontaktgesetzvergleich; unabhängig gegengeprüft (Abschnitt 2) | erfüllt im Modell mit Auslegungswerten; Neuberechnung mit gemessenen K, ζ und Kontaktgesetz nach Phase 0 nötig |
| Stoßspitzen mit mindestens zwei Kontaktgesetzen | Kelvin-Voigt und Hunt-Crossley (`test_v1_kontaktgesetze_vergleich`, `test_stoss_*`); Hunt-Crossley ≈ 1 050 N statt 484 N | erfüllt; Zuordnung des Hunt-Crossley-Gesetzes ist eine Annahme |
| Standardausgaben Randterm, RK4-gewichtetes Mittel, Δt/2-Kontrolle | Randterm R = M·Δv_S/T_w und exaktes Zeitmittel (⟨N⟩ = M·g + R auf ≤ 10⁻¹² N); statt Δt/2: Gegenprobe geschlossen gegen solve_ivp (≤ 10⁻¹⁰ m) und Stichproben im Engine-Raster | sinngemäß erfüllt (ohne festen Zeitschritt entfällt Δt/2) |

Lücken: 1 Freiheitsgrad, keine Kippmoden; im 0,05-Raster fehlen bei L1 oberhalb |Δv| ≈ 0,6 m/s schmale Hüpfbänder
(die Feinprüfung zeigt sie); die Feinprüfung umfasst nur 5 von 26 Laufarten; der Anlauf über eine Frequenzrampe ist
nicht Teil der Karten; Hunt-Crossley ist nur für positive Würfe ohne Bisektion gerechnet.

## 4 · Was aus der Abnahme für die nächsten Schritte folgt

- Die Karten sind mit gemessenen K, ζ und Kontaktgesetz (Phase 0, P0.4) neu zu rechnen, bevor Teil B registriert wird.
- Nennlast und Überlastanschlag müssen Summenkräfte von einigen 100 N bis ≈ 1 kN aufnehmen oder Stöße konstruktiv
  begrenzen; die Verteilung auf die Zellen braucht ein Modell mit Kippfreiheitsgraden.
- Ein erreichter Hüpfzustand bleibt bestehen; die Präregistrierung (§9.1 G6, §9.2 S2) erfasst schon kurzes Abheben,
  ein Anhalten des Antriebs bei erkanntem Hüpfen ist zusätzlich festzulegen.
- Offen in AP-02: zugesetzte Luftmasse; Dateiformat für gemessene Harmonische.
