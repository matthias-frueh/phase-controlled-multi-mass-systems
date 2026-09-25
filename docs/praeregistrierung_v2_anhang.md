# PCMMS — Präregistrierung v2, Technischer Anhang

**Matthias Früh · ORCID 0009-0005-9984-4207**
Stand: 25. September 2026 · gleichrangiger Teil von Teil A, Entwurf — nicht eingefroren, nicht registriert

Dieser Anhang gehört zu `praeregistrierung_v2_entwurf.md` (Hauptdokument, Dateiname vorläufig, §12; Verweise
„§“ beziehen sich darauf) und wird mit ihm eingefroren und registriert. Er enthält den Änderungsvermerk
gegenüber v1 (A0), die vollständigen Definitionen, die Herleitungen, das Beispiel der starren Auflage, die
Fehlalarmraten, die Verfahren im Einzelnen, die Tabellen der Artefakte (C) und Festlegungen (F) sowie den
Zahlennachweis (Z) für beide Dateien. Es gibt keine Messdaten; alle Zahlen sind Simulationsergebnisse des
Repositorys oder daraus abgeleitet.

---

## A0 · Änderungsvermerk v1 → v2

| v1 | v2 | Grund |
|---|---|---|
| Arbeitsfassung, internes Grundlagendokument | zweistufig, extern registriert, an Commit-Hashes gebunden | Vorhersagen hängen von Größen ab, die erst Phase 0 misst |
| §1: Nachweis phasenabhängiger Strukturen | quantitative Fragestellung (§2) | Die Phasenabhängigkeit folgt aus dem Newtonschen Gesetz |
| §2 H0 im Fehlerbudget | H0 je Lauf, ε_ctrl = 3·σ̂_ref oder 3·σ̂_betr (§8.8) | Schwelle war offen |
| §2 H1: Wellenformstatistik hängt von der Phase ab | H1 Superposition, H2 Zeltspitze, H3 Kontaktmodell, H4 Vorzeichen der Schiefe | Das qualitative H1 ist praktisch garantiert |
| §2 H1_fluid | eigene Präregistrierung | anderer Aufbau |
| §3: Schiefe, Liftoff-Anteil, Peak-to-Mean | primär F_min − ⟨N⟩, N₁ … N₃; sekundär γ₁; A beschreibend; λ explorativ | im Kontaktast vorhersagbar; Peak-to-Mean wurde nie berechnet, die Codevariable `peak_ratio` ist A; auf dem Schnitt ist λ = 0 |
| §4: Zielauflösung 0,2–0,5 % | Äquivalenzbedingungen (§8.5), Laufzahl aus Planungssimulation; Lauf bleibt Einheit | Die Zielauflösung galt einer Mittelwertverschiebung |
| §5: Kontrollen ohne Phasensteuerung, mit starrer Kopplung, mit Dummy-Masse | Phase 0 mit Einzelmodulläufen, D1 (passiver Körper anstelle der Dummy-Masse) und D2; Kontrollläufe in randomisierten Blöcken; Blindung; die Kontrollen „ohne Phasensteuerung“ und „starre Kopplung“ entfallen | Für die Wellenform gibt es keinen Zustand ohne Effekt |
| §6: Artefakte, Verwerfungsregel | Regel beibehalten, Kontrolle je Quelle, neue Quellen (§7, Tabelle C) | geändertes Messprinzip |
| §7: Block-Averaging, Welch-Test Referenz gegen Modulation, Streuungsgate | phasensynchrone Mittelung je Lauf (Auswertung je Block nur als Sensitivitätsanalyse, A9.9); Superpositionsvorhersage, standardisierte Residuen, Bootstrap, Äquivalenzbedingung; Welch-Test nur für H0 | Einheit ist der Lauf; Referenz und Modulation haben dasselbe Mittel |
| §8: externe Validierung | bleibt Pflicht, konkretisiert (§10.1) | — |
| §9: Stop / Modify / Scale | Abbruchregeln (§9.2), Ergebnislogik (§9.4) mit „nicht entscheidbar“ | Das Stop-Kriterium konnte nicht greifen |
| §10: Abgrenzung | inhaltlich unverändert (§11) | — |

Neu sind Phase 0, die Driftkontrolle über ŷ¹, Profilphasen, Anlaufprotokoll, Einzelzellkräfte,
externe Registrierung, Datenmanagement und Abweichungsprotokoll. Die Bezeichnung H1 ist neu belegt.

**Folgen für andere Dokumente** (dort nicht geändert; §12):

- **README, `overview.md`:** Zielgrößen γ₁, λ, A, F_min; nach v2 sind F_min − ⟨N⟩ und N₁ … N₃ primär, γ₁
  sekundär, A beschreibend, λ explorativ; v2 verlinken. README, Bildunterschrift der Zeltkurve: „Die Lage
  der Spitze folgt aus der Phasengeometrie“ (aus der Geometrie folgt bei identischen Modulen nur der Knick
  bei 120°, A2.2; das Maximum kann kontaktabhängig wandern, A5). Erledigt.
- **README, `overview.md`, Grundsatz:** README „Es werden keine Kräfte gemessen“ und `overview.md` „Gemessen
  wird nie ein Absolutwert“ (H3 und G6 brauchen eine absolute Kalibrierung, §0); `overview.md` „⟨N⟩ … keine
  Messgröße“ (⟨N⟩ wird in jedem Lauf bestimmt, H0). Umformuliert zu „primär ausgewertet“ und „Kontrollgröße,
  nicht Zielgröße“ (erledigt).
- **Exposé:** „braucht keine Statistik“, „direkt am Kraftsignal ablesbar“ (v2 entscheidet mit Residuen und
  Bootstrap); Ziel „Nachweis oder Falsifikation der F_min-Zeltkurve“ (v2: nur Lage der Spitze); die
  Vorzeichenregel „werden in die vorgesehene v2 der Präregistrierung aufgenommen“ (v2 registriert
  stattdessen H4); „11 Kanäle“ bei neun aufgezählten; „noch nicht präregistriert“. Erledigt bis auf
  „11 Kanäle“; ob die Zahl oder die Aufzählung zu ändern ist, ist offen.
- **Werkstattbericht:** „präregistriert“ (v1 war eine nicht extern registrierte Arbeitsfassung); „Zwei
  Schwellenwerte des Auswerteverfahrens sind nicht festgelegt“; „Steigung, die man gegen ein Messrauschen
  halten kann“ (v2 registriert nur die Lage der Spitze). Erledigt.
- **Literaturabgleich (§4.2, T3):** ε_ctrl ist nach v2 festgelegt (§8.8), ε_phys für die Wellenformgrößen
  ersetzt (§1). Erledigt.
- **`einordnung.md` (§4, §6), `zehn_fragen.md` (Nr. 3, 7), `neuheitsgrad.md` (§5, §6):** „harten Stopp“ bei
  jeder Mittelwertabweichung (nach v2: Lauf ungültig, Stopp erst bei reproduzierbarem Verstoß, S1); „gilt H1
  … als falsifiziert“, wenn keine Struktur über dem Rauschen (nach v2: „nicht entscheidbar“); „ohne jede
  Statistik am Kraftsignal ablesbar“; Wellenformstatistik als „primäre Zielgröße“ (nach v2: γ₁ sekundär).
- **`code/linear_solver.py`:** `--section`, `--phi3`, `--f` liegen seit Commit `069cb9b` im Repository
  (Werkzeug 1, erledigt).

---

## A1 · Definitionen

| Größe | Definition |
|---|---|
| N_c(t), N(t) | Kraft der Wägezelle c = 1, 2, 3 nach Kalibrierung (P0.1); Gesamtkraft N = N₁ + N₂ + N₃ |
| Referenzlauf R | alle Module in Parkposition, Antriebe bestromt und haltend, gleiche Dauer wie ein Messlauf |
| Einzelmodullauf Lⱼ | nur Modul j läuft; die beiden anderen stehen in Parkposition, bestromt und haltend wie in R; ihre Masse bleibt an Bord |
| Kombinationslauf | alle drei Module laufen in einer Sollkonfiguration (Schnitt, Zusatz- oder Pilotkonfiguration) |
| Kontrollsatz | R, L₁, L₂, L₃ in zufälliger Reihenfolge |
| Parkposition | zeitgemittelte Lage der bewegten Masse über einen Zyklus (aus P0.5), Toleranz Δ_park [Teil B]; so sind die statischen Zelllasten in allen Laufarten gleich |
| D1, D2 | D1: passiver Körper gleicher Masse und Fußgeometrie ohne Antriebe. D2: Antriebe laufen, bewegte Massen abgekoppelt und am Rahmen fixiert |
| Kontaktast (Modell) | periodische Lösung ohne Abheben (N > 0 und Auflagerkoordinate z < 0; Docstring von `code/linear_solver.py`). Dass er existiert, heißt nicht, dass der reale Zustand darauf liegt (A3) |
| Kontaktast (Messung) | Die Vorhersage ŷ⁰ der Konfiguration erfüllt mit den gemessenen Zeigern ρⱼₖ Bedingung (a) aus §5.3, und kein Lauf der Konfiguration bei f zeigt Einzelzell-Liftoff; ausgenommen sind Läufe, die nach G5, G8 oder G10 ungültig sind. Eine Konfiguration außerhalb des Kontaktasts ist nicht auswertbar (§9.1) |
| θ | Zyklusphase 0 … 2π; θ = 0 am Indeximpuls von Modul 1 (Kombinationsläufe, D2) bzw. von Modul j (Lⱼ); Referenzläufe: virtueller Takt mit f |
| φⱼ,c | Indexphase von Modul j im Zyklus c: 2π·(t_idx,j − t_idx,1)/T_c mod 2π, mit t_idx,j dem ersten Indeximpuls von Modul j nach t_idx,1 und T_c der Dauer des Zyklus c von Modul 1 |
| Δδⱼ, φⱼ^P | Δδⱼ = arg x₁⁽¹⁾ − arg x₁⁽ʲ⁾ (mod 360°), mit x₁⁽ʲ⁾ der ersten Weg-Harmonischen von Modul j bezogen auf den eigenen Indeximpuls (P0.5). Profilphase φⱼ^P = φⱼ + Δδⱼ. Alle Sollphasen (Schnitt, Zusatz- und Pilotkonfigurationen, G2) sind Profilphasen; die Regelung stellt die Indexphase φⱼ,soll^P − Δδⱼ ein |
| φ̄ⱼ, σⱼ | zirkuläres Mittel arg⟨e^{iφⱼ,c}⟩ über die Zyklen eines Laufs; Jitter σⱼ = √(−2·ln Rⱼ) mit Rⱼ = \|⟨e^{iφⱼ,c}⟩\| |
| ρⱼₖ | mittlerer Phasenzeiger ⟨e^{−ikφⱼ,c}⟩ über alle Zyklen aller gültigen Läufe einer Konfiguration, Läufe gleich gewichtet; ρ₁ₖ = 1 |
| Mittelkurve N̄(θ) | phasensynchrones Mittel über alle vollständigen Zyklen des Auswertefensters eines Laufs, auf N_θ = 2000 Stützstellen, Harmonische über k_max null gesetzt |
| Konfigurationsmittelkurve | Mittel der Mittelkurven aller gültigen Läufe einer Konfiguration, jeder Lauf gleich gewichtet |
| N_k | komplexe Harmonische k ≥ 1: N_k = (2/N_θ)·Σₙ N̄(θₙ)·e^{−ikθₙ}; \|N_k\| ist die Amplitude wie in `linear_solver.py --section` |
| ⟨N⟩ | Zeitmittel über eine ganze Zahl vollständiger Zyklen im Auswertefenster (= Gleichanteil der Mittelkurve) |
| F_min, F_max | Minimum und Maximum der Konfigurationsmittelkurve; konfirmatorisch verglichen wird F_min − ⟨N⟩ |
| γ₁ | Schiefe m₃/m₂^{3/2} der Konfigurationsmittelkurve über ihre N_θ Stützstellen (wie `scipy.stats.skew` in `linear_solver.py`) |
| A | (F_max − ⟨N⟩)/(⟨N⟩ − F_min); unter H0 gleich (F_max − M·g)/(M·g − F_min); Codevariable `peak_ratio`; beschreibend |
| λ | Anteil der Rohwerte im Auswertefenster mit N < F_LO,Σ; explorativ |
| σ_c, σ_Σ, F_LO,c, F_LO,Σ | Standardabweichung der Rohwerte von Zelle c bzw. der Summe in Referenzläufen; Liftoff-Schwellen 5·σ_c bzw. 5·σ_Σ über dem Nullpunkt (P0.1) |
| Einzelzell-Liftoff | mindestens ein Rohwert N_c < F_LO,c im ganzen Lauf einschließlich Rampe und Einschwingzeit |
| N_s, N_s,int, β | Zeitmittel von N in Referenzläufen; N_s,int = (1 − β)·N_s,a + β·N_s,b, zeitlich linear interpoliert zwischen den beiden Referenzläufen a und b, die einen Lauf einschließen; β ∈ [0, 1] relative Lage des Laufs |
| Δ⟨N⟩, σ̂_ref, ε_ctrl | Δ⟨N⟩ = ⟨N⟩_Lauf − N_s,int. σ̂_ref ist die Standardabweichung derselben Statistik für Referenzläufe: Jeder Referenzlauf der Phase 0 wird gegen die Interpolation seiner beiden Nachbarn ausgewertet (leave-one-out), aus mindestens 42 Referenzläufen der Phase 0 (P0.7), also mindestens 40 Werten; σ̂_ref,c ebenso je Zelle. ε_ctrl = 3·σ̂_ref oder 3·σ̂_betr (§8.8) |
| σ̂_betr | Standardabweichung der auf mittige Lage normierten Werte Δ⟨N⟩·√(1,5/(1 + β² + (1 − β)²)) der nach G2–G10 gültigen Pilot- und Einzelmodulläufe der Phase 0 (§8.8, A9.8) |
| s_q, ν_p | s_q: gepoolte Standardabweichung über Läufe der Größe q, quadratisches Mittel der Standardabweichungen der Pilotkonfigurationen; ν_p = Σ(n_p,i − 1) mit den gültigen Läufen n_p,i |
| u_c, u_c,erw | u_c: kombinierte Unsicherheit einer Differenz Messung − Vorhersage (§8.3, A9.5). u_c,erw: vor Phase 1 erwarteter Wert, u_c,erw² = s_q²/n_min + u²(ŷ_q); für γ₁ mit u(γ̂₁) aus dem Bootstrap der Vorhersage |
| ν_eff | Welch–Satterthwaite, §8.3, A9.5 |
| ŷ⁰, ŷ¹; z⁰, z¹ | Vorhersage aus den Einzelmodulläufen der Phase 0 bzw. aus den Kontrollläufen der Phase 1; standardisierte Residuen dagegen |
| D_q, Δ_q | vorhergesagte Struktur und Äquivalenzgrenze Δ_q = 0,25·D_q (§8.5) |
| N̂_k⁽ʲ⁾, Δ (H3) | H3-Vorhersage: Mittel der Monte-Carlo-Ziehungen von G_F(kω)·m_j·H(kω)·a_k⁽ʲ⁾ (§8.7, A9.7); Δ = 0,10·\|N̂_k⁽ʲ⁾\| (PB3) |
| γ̂₁, γ̄₁,i, u(γ̄₁,i) | vorhergesagte bzw. gemessene Schiefe der Konfigurationsmittelkurve; u(γ̄₁,i) Standardabweichung von γ̄₁,i im Bootstrap A (A9.5) |
| φ̄₂^P | gemessene Profilphase von Modul 2 einer Konfiguration: −arg ρ₂₁ + Δδ₂; Abszisse des Zeltfits (§8.6) |
| auswertbar | Konfiguration im Kontaktast (Messung) mit mindestens n_min gültigen Läufen (§9.1) |
| Schnitt | 21 Punkte φ₂ = 100°, 102°, …, 140° bei φ₃ = 240° (Profilphasen) |
| gespiegelter Schnitt | φ₂ = 240°, φ₃ = 100°, 102°, …, 140° |
| Feinfenster | φ₂ ∈ [100°, 140°], φ₃ ∈ [220°, 260°] (Fenster des 2°-Feinsweeps, `data/README.md`) |
| zyklische Phasenabstände | Die Phasen {0, φ₂, φ₃} aufsteigend auf dem Kreis; die drei Differenzen benachbarter Phasen einschließlich des Übergangs über 360°, in zyklischer Reihenfolge (A7) |
| f₁, f_m, ζ_m | niedrigste in N oder einer Zellkraft sichtbare Mode aus P0.4; alle Moden mit Dämpfungsgraden |
| k_b, k_max | k_b = ⌊f₁/(2f)⌋; k_max nach §5.4 und A9.2 |
| f_u, f_zul | kleinste ganzzahlige Frequenz, die (d) erfüllt; größte Rasterfrequenz, die (a) nach dem Auslegungswerkzeug (Parameter aus P0.1–P0.4, Konstruktionsprofil, ohne Zusatzkonfigurationen), (b) und (d) erfüllt |
| T_warm, T_park, T_ramp, T_e, T_e,P, T_a, T_a,P, T_ab, T_Lauf, T_φ | Aufwärmzeit; Dauer Parkposition → Startstellung; Rampe; Einschwingzeit; Einschwingzeit der Phase-0-Läufe (A9.2); Auswertefenster; Aufnahmefenster der Phase-0-Läufe; Rampe ab und Parken; T_Lauf = T_park + T_ramp + T_e + T_a + T_ab; längste Einregelzeit der Phasen in den Pilotläufen |
| n₀ⱼ, n₀, n_min, r, n, n_max, p̂, N_K, d | Einzelmodulläufe je Modul in Phase 0 (n₀ geplant); Mindestzahl gültiger Läufe je Konfiguration; Reserve; geplante Läufe = Blöcke; Höchstzahl nach Zeitbudget (§5.3 c); Anteil ungültiger Pilotläufe; Zahl der Konfigurationen je Block (21 oder 23); Zahl der Messtage [Teil B] |
| δφ_tol, σ_tol, δf_tol, ΔT, T_P0 | Toleranzen der Phase (0,5°), des Jitters, der Frequenz und der Zelltemperatur (G2, G3, G7); T_P0 Temperaturmittel der Zelle während P0.8 bei f |
| W, w, φ₂*, φ̂₂* | Fitfenster, Halbbreite, Spitzenlage aus dem Fit an der Messung bzw. an der Vorhersage (§8.6) |
| V | Prüfmenge für H4 (§8.5) |

---

## A2 · Herleitungen

### A2.1 Modell im Kontaktast und Superposition

Solange der Körper nicht abhebt, ist das Modell der Referenz-Engine linear (Docstring von
`code/linear_solver.py`):

    M·ẍ + C·ẋ + K·x = −μ·M·ā(t),     N(t) = M·g − K·x − C·ẋ

mit ā(t) dem Mittel der drei Modulbeschleunigungen und μ dem Anteil der Masse, der sich mit den Modulen
bewegt. Für die k-te Harmonische der Anregungsfrequenz f (ω = 2πf) gilt

    N_k = μ·M · H(kω) · P_k · (1 + e^{−ikφ₂} + e^{−ikφ₃}) / 3,     H(ω) = (K + iωC) / (K − M·ω² + iωC)

mit P_k den Fourier-Koeffizienten der Profilbeschleunigung. Die Phasenlage wirkt nur über den Kammfaktor
(1 + e^{−ikφ₂} + e^{−ikφ₃})/3. Am Triphasik-Punkt (120°, 240°) verschwindet er für alle k, die kein
Vielfaches von 3 sind; es bleiben k = 3, 6, 9 …

Für ein einzelnes Modul j mit bewegter Masse m_j und Profilharmonischen P_k⁽ʲ⁾ gilt N_k⁽ʲ⁾ = m_j·H(kω)·P_k⁽ʲ⁾,
bezogen auf seinen eigenen Takt, und jede Phasenkonfiguration ist die Summe

    N_k = Σⱼ N_k⁽ʲ⁾ · e^{−ikφⱼ},     φ₁ = 0.

Weil N_k⁽ʲ⁾ in den Einzelmodulläufen gemessen wird, gilt diese Superposition für jedes lineare,
zeitinvariante System, auch bei ungleichen Modulen und einer beliebigen Übertragung; K, C und μ werden
nicht gebraucht. Im Zeitbereich lautet sie N̂(t) = N_s + Σⱼ [N⁽ʲ⁾(t − τⱼ) − N_s] mit τⱼ = φⱼ/(2πf). Für
starre Auflage (H = 1) bleibt N(t) = M·g + Σⱼ m_j·a_j(t − τⱼ), das Newtonsche Gesetz für den ruhenden
Körper; dass die Wellenform von der Phasenlage abhängt, ist damit keine offene Frage. Bei identischen
Modulen entspricht ein Einzelmodullauf im Modell der synchronen Phasung mit μ/3; so wird er im
Zahlennachweis gerechnet.

### A2.2 Knick der Zeltspitze

Bei identischen Modulen hat N(t) am Triphasik-Punkt die Periode T/3 und drei gleich tiefe Minima θ_m.
Ändert sich φ₂ um δ, ändert sich jedes Minimum in erster Ordnung um δ·s_m mit s_m = ∂N/∂φ₂ an θ_m. Die
Harmonischen k = 3, 6, 9 … tragen zu s_m nichts bei: Ihr Beitrag zu ∂N/∂φ₂ ist bei φ₂ = 120° gleich
−(1/3)·dN/dθ, und die Minima sind stationäre Punkte von N. Die übrigen Harmonischen liefern an den drei um
T/3 versetzten Minima Beiträge mit der Summe null. F_min, das kleinste der drei Minima, steigt deshalb
links der Spitze mit max s_m > 0 und fällt rechts mit −min s_m > 0: ein Knick mit relativem Maximum bei
120°, für jeden linearen Kontakt mit glatter Wellenform, also auch für jede bandbegrenzte Kurve.

Referenzparameter: s_m = −0,196, +0,206, −0,011 N/° (Summe null bis auf 5·10⁻⁵). Die lokalen Steigungen mit
0,1° Abstand betragen 0,207 N/° links und 0,196 N/° rechts (F_min = 5,3097 / 5,3304 / 5,3108 N bei
119,9° / 120° / 120,1°). Die 2°-Sekanten 118° → 120° bzw. 122° → 120° betragen 0,212 bzw. 0,195 N/°; sie
weichen wegen der Krümmung der Flanken von den lokalen Steigungen ab. Die Flanken sind verschieden steil,
weil die drei s_m nicht symmetrisch liegen. Bei starrer Auflage liegen die Minima auf Knicken der
Profilbeschleunigung; der Knick bei 120° bleibt, und die 2°-Sekanten sind gleich (0,0469 und 0,0468 N/° bei
μ = 0,4), weil die Egg-Beschleunigung zeitumkehrsymmetrisch ist.

### A2.3 Schiefe am Triphasik-Punkt

Bei identischen Modulen enthält N − ⟨N⟩ am Triphasik-Punkt nur k = 3, 6, 9 …; mit
N − ⟨N⟩ = Σₖ a_k·cos(kθ + ϑ_k) gilt

    m₃ = (3/4)·a₃²·a₆·cos(2ϑ₃ − ϑ₆) + (3/2)·a₃·a₆·a₉·cos(ϑ₃ + ϑ₆ − ϑ₉) + …

Ohne Harmonische k ≥ 6 ist die Schiefe null (⟨cos³⟩ = 0). Ihr Vorzeichen hängt u. a. vom Term
a₃²·a₆·cos(2ϑ₃ − ϑ₆) ab, in den über ϑ₃ und ϑ₆ die Phasen von H(3ω) und H(6ω) eingehen. Mit k ≤ 6 ergibt
die Formel −0,3775 bei starrer Auflage (cos(2ϑ₃ − ϑ₆) = −1,000) und +0,0658 bei K = 10⁴ N/m
(cos(2ϑ₃ − ϑ₆) = +0,912), wie die bandbegrenzte Rechnung; mit vollem Spektrum −0,450 bzw. +0,067. Deshalb
hängt das Vorzeichen an diesem Punkt vom Kontakt ab, und H4 wird gegen die Superpositionsvorhersage
geprüft.

### A2.4 Jitterfaktor

Für normalverteilten Jitter mit Standardabweichung σⱼ (in rad) ist ρⱼₖ = e^{−ikφ̄ⱼ}·e^{−k²σⱼ²/2}. Jitter
dämpft die Harmonischen der Mittelkurve nur über den Faktor e^{−k²σ²/2}; bei σ = 1° beträgt er 0,99985,
0,99939 und 0,99863 für k = 1, 2, 3 sowie 0,99453 und 0,98774 für k = 6 und 9. Konfirmatorisch wird der
gemessene Zeiger ρⱼₖ verwendet, nicht die Normalverteilungsannahme. Die Minima einzelner Zyklen streuen
stärker; sie sind explorativ (E4).

### A2.5 Zellkräfte

Annahme für die Auslegung: starrer Körper auf drei Zellen, Schwerpunkt des Körpers über dem
Flächenschwerpunkt des Zelldreiecks, jedes Modul über einer Zelle. Eine senkrechte Kraft über einem
Auflagerpunkt geht bei Dreipunktlagerung ganz in dieses Auflager; deshalb trägt Zelle j bei jeder Phasung
M·g/3 + m_j·a_j(t − τⱼ). Ihr Minimum ist bei identischen Modulen ein Drittel des Minimums der synchronen
Phasung, unabhängig von φ₂ und φ₃. Je Zelle gilt dann die Grenze der synchronen Phasung, und die Zellkräfte
aller Konfigurationen sind bis auf eine Zeitverschiebung gleich. Bei anderer Lage von Zellen und Modulen
ändert sich das; die Lage ist offen (§12), und Bedingung (a) wird mit den gemessenen Zellkräften geprüft
(§8.2).

---

## A3 · Simulationsbefunde der Referenz

Parametersatz der Engine (README, „Simulationsstand“): M = 0,650 kg, μ = 1, f = 10 Hz, Hub 7,69 mm,
K = 10⁴ N/m, C = 16 N·s/m (ζ = 0,099228), f_n = 19,74 Hz, M·g = 6,3765 N.

- **Zeltkurve.** F_min = 5,3304 N bei (120°, 240°), 0,7677 N bei φ₂ = 100°, 1,6176 N bei 140°.
  2°-Sekanten 118° → 120° bzw. 122° → 120°: 0,212 bzw. 0,195 N/°; die Werte ≈ 0,23 und ≈ 0,19 N/° des
  Exposés sind die 20°-Sekanten 0,228 und 0,186 N/°. Die Referenz ist ein Resonanzfall: 2f/f_n = 1,013,
  |H₂| = 5,03. Bei festem ζ und K = 3·10⁴ … 10⁷ N/m betragen die 2°-Sekanten 0,09–0,12 N/°. Die
  Simulationswerte sind keine Vorhersage für einen realen Aufbau.
- **Schiefe und Vorzeichenregel.** Die Regel des Exposés (negative Schiefe nur bei echter Dephasierung;
  synchron und bei Zweiergruppen-Phasung positiv) ist bei K = 10⁴ N/m auf den geprüften Linien nicht
  widerlegt: Auf den Linien φ₂ = 0°, φ₃ = 0° und φ₂ = φ₃ des 19×19-Rasters (55 Punkte, darunter die
  synchrone Phasung) ist γ₁ ≥ +0,596; alle 36 negativen Werte liegen bei dephasierten Konfigurationen.
  Das Raster stammt aus der nichtlinearen Engine und enthält Liftoff-Punkte, deren Einzelwerte von der
  Startbedingung abhängen (README); der Befund ist deshalb ein Hinweis, kein Beweis. Das
  Vorzeichen an einem einzelnen dephasierten Punkt hängt aber vom Kontakt ab: Am Triphasik-Punkt ist
  γ₁ = +0,067 bei K = 10⁴ N/m und −0,450 bei starrer Auflage (A2.3). Die Regel sagt dafür kein Vorzeichen
  voraus; H4 prüft deshalb gegen die Superpositionsvorhersage.
- **Kontaktast.** Bei der Referenz besitzen 4,24 % des Phasenraums (1°-Raster) einen Kontaktast: zwei
  Hauptgebiete um (120°, 240°) und (240°, 120°) mit 2 × 2524 Punkten (3,90 %), in allen Proben monostabil,
  und sechs Satelliteninseln mit 6 × 74 Punkten (0,34 %), die bistabil sind: Bei (35°, 116°) ergibt der
  Standardstart der Engine λ = 75,82 %, der Start auf dem linearen Orbit λ = 0 %. Der Anteil hängt stark
  von Auflage und μ ab: 76,6 % bei starrer Auflage, 48,6 % bei K = 10⁴ N/m und μ = 0,5. Im
  Liftoff-Bereich ist die Phasenkarte nicht eindeutig; konfirmatorisch wird nur im Kontaktast geprüft.
- **Einzelmodul.** Bei den Referenzparametern hebt ein einzelnes Modul ab (lineares F_min = −2,057 N); die
  Superposition wäre dort nicht anwendbar. Der reale Arbeitspunkt muss auch die Einzelmodulläufe im Kontakt
  halten (§5.3).
- **Gespiegelter Schnitt.** (110°, 240°) und (240°, 110°) ergeben dasselbe F_min = 3,0846 N und dieselbe
  Schiefe −0,3846.

---

## A4 · Beispiel: starre Auflage, μ = 0,4

Ein realer Aufbau hat einen Rahmen mit eigener Masse (μ < 1) und mit steifen Wägezellen eine
Kontakteigenfrequenz weit über 3f. Als Beispiel dient die starre Auflage mit μ = 0,4; Masse, Hub und Profil
sind die der Simulationsreferenz, nicht die eines geplanten Aufbaus. Das Beispiel zeigt, wie die
Auslegungsregeln wirken; es ist keine Vorhersage.

| Fall | Kontaktast auf allen 21 Punkten | F_min bei 120° | F_min bei 100° und 140° | kleinstes F_min / M·g | 2°-Sekante 118° → 120° | ΔF_Zelt |
|---|---|---|---|---|---|---|
| starr, μ = 0,4, 10 Hz | ja | 5,6452 N | 5,1759 N | 81,2 % | 0,0469 N/° | 0,4693 N |
| starr, μ = 0,4, 14 Hz | ja | 4,9432 N | 4,0233 N | 63,1 % | 0,0918 N/° | 0,9199 N |
| starr, μ = 0,4, 19 Hz | ja | 3,7365 N | 2,0424 N | 32,0 % | 0,1691 N/° | 1,6941 N |
| starr, μ = 0,4, 20 Hz | ja | 3,4513 N | 1,5741 N | 24,7 % | 0,1874 N/° | 1,8772 N |
| Referenz: K = 10⁴ N/m, μ = 1, 10 Hz | ja | 5,3304 N | 0,7677 N / 1,6176 N | 12,0 % | 0,2124 N/° | 4,5627 N |

ΔF_Zelt ist die Spannweite von F_min über die 21 Punkte; die Zahlen gelten für das volle Spektrum.

- **Kein Liftoff auf dem Schnitt.** Bei 10 Hz beträgt das kleinste F_min 81,2 % von M·g. An den
  Schnitträndern hebt der Körper erst zwischen 23 und 24 Hz ab (lineares F_min bei 100°: 0,0254 N bzw.
  −0,5389 N).
- **Kleine Zeltsteigung.** Die 2°-Sekanten an der Spitze betragen bei 10 Hz 0,0469 und 0,0468 N/°. Die
  Flanke knickt bei etwa 114° und 126° ab (Schnitt der äußeren und inneren Geraden bei 114,01° und 125,98°);
  außerhalb (100°–112° und 128°–140°) beträgt die Steigung 0,0135 N/°. Das illustriert die Fensterregel für
  H2 (§8.6).
- **Frequenz als Stellgröße.** Bei starrer Auflage gilt N − M·g = μ·M·ā(t), und bei gleichem Hub ist
  ā ∝ f². Alle Kraftabweichungen von M·g und alle Steigungen skalieren mit f² (0,0469 → 0,0918 →
  0,1874 N/° bei 10, 14 und 20 Hz, Faktor 1,96 bzw. 4,0); γ₁ und A bleiben gleich (bei 120°: −0,4498 und
  0,6529). Bei endlicher Steifigkeit kommt die Frequenzabhängigkeit von H(kω) hinzu.
- **Grenzen durch die übrigen Läufe.** Ein Einzelmodullauf (F_min = 5,3642 N bei 10 Hz) hebt zwischen 25
  und 26 Hz ab, die Zweiergruppen-Phasung (0°, 180°) zwischen 21 und 22 Hz, die synchrone Phasung (0°, 0°)
  zwischen 14 und 15 Hz. Mit dem Sicherheitsabstand von 25 %, nach der Gesamtkraft beurteilt, erlauben auf
  dem 1-Hz-Raster der Schnitt höchstens 19 Hz, ein Einzelmodul 21 Hz, (0°, 180°) 18 Hz und die synchrone
  Phasung 12 Hz. Maßgeblich ist aber die Zellkraft: Im Zellmodell von A2.5 gilt je Zelle die Grenze der
  synchronen Phasung, höchstens 12 Hz (31,4 % bei 12 Hz, 19,5 % bei 13 Hz); bei 10 Hz bleibt jede Zelle mit
  52,4 % der statischen Zelllast im Kontakt. Nach der Gesamtkraft wären bei 10 Hz beide
  Zusatzkonfigurationen zulässig (kleinstes F_min 52,4 % bzw. 78,9 % von M·g).
- **Summenkraft und Nennlast.** Bei 10 Hz bleibt die Summenkraft auf dem Schnitt unter 7,08 N (größtes
  F_max 7,0752 N bei 100° und 140°). Das gilt nur für den Schnitt: Die synchrone Phasung erreicht
  12,0163 N, (0°, 180°) 9,1241 N, ein Einzelmodullauf 8,2564 N. Im Zellmodell trägt jede Zelle höchstens
  12,0163/3 = 4,0054 N bei einer statischen Zelllast von 2,1255 N. Im Liftoff-Bereich (E1) sind weit
  höhere Spitzen möglich; die Simulation mit μ = 1 und K = 10⁴ N/m erreicht 50,6 N. Die Nennlast wird nach
  §5.1 aus der größten erwarteten Zellkraft bestimmt; die „mindestens 10 kg“ des Exposés sind dort nicht
  hergeleitet.
- **Schiefe.** Auf dem Schnitt ist γ₁ überall negativ (−0,450 bei 120°, −0,793 bei 100° und 140°), bei
  synchroner Phasung +0,755, bei (0°, 180°) +0,986; das stimmt mit der Vorzeichenregel des Exposés überein,
  wie bei K = 10⁴ N/m auf den geprüften Linien (A3).
- **Endliche Steifigkeit.** Bei K = 10⁶ N/m (ζ fest) weichen die Beträge der ersten drei Harmonischen um
  0,3 %, 1,0 % und 2,4 % vom starren Wert ab (bei 19 Hz um 0,9 %, 3,8 % und 9,1 %), die der sechsten und
  neunten bei 10 Hz um 10 % und 26 % (|H| = 1,101 und 1,259; |H(3ω)| = 1,024). F_min bei 120° liegt deshalb
  0,083 N unter dem starren Wert (5,5620 gegen 5,6452 N, 18 % von ΔF_Zelt). H3 mit k ≤ 3 prüft den Kontakt
  in diesem Bereich kaum (§8.7); F_min und γ₁ enthalten ihn.
- **Größenordnung von PB1.** Mit ΔF_Zelt = 0,4693 N ist Δ(F_min) = 0,117 N; PB1 verlangt dann u_c ≤ 0,0327 N
  für ν → ∞ und u_c ≤ 0,0269 N (0,42 % von M·g) für ν = 19 (A8).

---

## A5 · Resonanzfall und Lage der Spitze

Bei identischen Modulen liegt bei 120° immer ein Knick mit relativem Maximum (A2.2). Ob er auch das Maximum
des Schnitts ist, hängt vom Kontakt ab. Werden Vielfache von 3 resonant überhöht, sinkt F_min(120°), und das
Maximum wandert: Bei μ = 0,4, 10 Hz, f_n = 120 Hz (K = 369 518 N/m) und ζ = 0,02 liegt es bei 106°
(5,2096 N gegenüber 5,1342 N bei 120°). Mit der Bandbegrenzung nach Bedingung (b) (hier k_max = 6) liegt
es im selben Fall bei 120° (2°-Sekante 0,0339 N/° gegenüber 0,0331 N/° bei starrer Auflage mit derselben
Bandbegrenzung). In allen gerechneten Fällen mit ζ ≈ 0,1 (K = 10⁴ N/m; K = 3·10⁴, 10⁵, 10⁶ und 10⁷ N/m mit
festem ζ) und bei starrer Auflage liegt das Maximum auf dem 2°-Raster bei 120°. Bei ungleichen Modulen ist
die Auslöschung unvollständig, und die Spitze verschiebt sich um einen Betrag, den die Superposition aus den
Einzelmodulläufen vorhersagt.

Bedingung (b) muss alle ausgewerteten Harmonischen erfassen, nicht nur k ≤ 3, weil am Triphasik-Punkt
k = 3, 6, 9 … die Wellenform bestimmen: An der Grenze 3f = f_n/2 liegt 6f auf f_n. Mit M = 0,650 kg,
μ = 1, 10 Hz und festem ζ (f_n = 60 Hz, K = 92 379 N/m) sinkt F_min(120°) dort auf 3,4258 N gegenüber
4,5483 N bei starrer Auflage.

---

## A6 · Bandbegrenzung und Resonanzabstand

**Resonanzabstand.** Mit r = k·f/f_m ist |H|² = (1 + 4ζ²r²)/((1 − r²)² + 4ζ²r²) ≤ 1/(1 − r²)². Für r ≤ 0,5
folgt |H| ≤ 1,33, und für ζ → 0 ist d ln|H| / d ln f = 2r²/(1 − r²) ≤ 0,67. Numerisch gelten beide Schranken
für jedes ζ ≤ 2 (Z). Die ausgewerteten Größen hängen dann nur schwach von K, ζ, f und Temperatur ab.

**Bandbegrenzung im Beispiel** (starr, μ = 0,4, 10 Hz). Bei k_max = 9 sinkt die 2°-Sekante an der Spitze auf
0,0343 N/°, F_min beträgt 5,6781 N bei 120° und 5,1608 N bei 100°, ΔF_Zelt 0,5173 N. γ₁ bei 120° beträgt
−0,4305 (k_max = 9), −0,3775 (k_max = 6) und null für 3 ≤ k_max ≤ 5, weil am Triphasik-Punkt unterhalb von k
= 6 nur die dritte Harmonische bleibt (A2.3); für k_max ≤ 2 ist die Kurve dort konstant. Alle
Auslegungszahlen in Teil B werden mit derselben Bandbegrenzung gerechnet wie die Messung.

**Abtastrate.** Lineare Interpolation eines Sinus der Frequenz k·f mit der Abtastrate f_s unterschätzt die
Amplitude höchstens um 1 − cos(π·k·f/f_s) ≈ (π·k·f/f_s)²/2. Die Bedingung (π·k_max·f/f_s)²/2 ≤ 10⁻³ verlangt
bei k_max = 9 und f = 10 Hz etwa f_s ≥ 6,3 kHz.

---

## A7 · Pilotkonfigurationen und Äquivalenz

Bei identischen Modulen ist eine Konfiguration bis auf Umbenennung der Module und Zeitverschiebung durch die
Folge ihrer drei zyklischen Phasenabstände bestimmt, bis auf zyklische Vertauschung (eine Spiegelung
entspräche einer Zeitumkehr und ist nur bei zeitumkehrsymmetrischem Profil und starrer Auflage eine
Symmetrie; sie erhält die Menge der Abstände). Jeder Punkt des Schnitts (φ₂, 240°) hat die Abstände
(φ₂, 240° − φ₂, 120°); der gespiegelte Schnitt hat dieselben Folgen (Vertauschen von Modul 2 und 3). Im
Feinfenster ist jede Konfiguration mit einem Abstand von 120° zu einem Punkt der Schnittgeraden
φ₂ ∈ [100°, 140°] äquivalent, auf dem 2°-Raster zu einem Schnittpunkt, und jede ohne einen solchen Abstand
zu keinem.

| Konfiguration | zyklische Abstände | äquivalent zu einem Schnittpunkt | F_min Referenz (K = 10⁴ N/m) | F_min starr, μ = 0,4, 10 Hz |
|---|---|---|---|---|
| (110°, 250°), Pilot | 110°, 140°, 110° | nein | 1,6016 N, Kontaktast | 5,1742 N (81,1 %) |
| (130°, 230°), Pilot | 130°, 100°, 130° | nein | 1,8699 N, Kontaktast | 5,3253 N (83,5 %) |
| (110°, 252°), Pilot | 110°, 142°, 108° | nein | 1,3164 N, Kontaktast | 5,1472 N (80,7 %) |
| (110°, 230°), Beispiel | 110°, 120°, 130° | ja, zu (130°, 240°) | 3,4139 N (wie (130°, 240°)) | — |
| (120°, 250°), Beispiel | 120°, 130°, 110° | ja, zu (130°, 240°) | 3,4139 N | — |

Die drei Pilotkonfigurationen liegen im Feinfenster, sind paarweise nicht äquivalent, und jeder ihrer
Abstände weicht um mindestens 10° von 120° ab (Festlegung, Tabelle F); ein Phasenfehler unterhalb von
δφ_tol kann sie deshalb nicht äquivalent machen. Der Abstand von 10° ist ein Phasenabstand, kein
physikalisches Maß: Einzelne Größen einer Pilotkonfiguration können denen eines Schnittpunkts nahekommen.
Die Nichtäquivalenz gilt für N; im Zellmodell von A2.5 sind die Zellkräfte aller Konfigurationen bis auf
eine Zeitverschiebung gleich. Im Beispiel erfüllen die Pilotkonfigurationen den Kontaktast mit Abstand:
Die Gesamtkraft bleibt über 80 % von M·g, jede Zelle im Zellmodell bei 52,4 % der statischen Zelllast.
Bei der Referenz liegen alle drei im Kontaktast.

---

## A8 · Kritische Werte und Fehlalarmraten

**Kritische Werte** c = t(1 − α/(s·m); ν), α = 0,05:

| Familie | m | Art | ν → ∞ | ν = 9 | ν = 19 | ν = 29 |
|---|---|---|---|---|---|---|
| H1 (und H1′): 21 Punkte × (F_min − ⟨N⟩, Re/Im N₁, N₂, N₃) | 147 | zweiseitig | 3,583 | 5,586 | 4,356 | 4,060 |
| H3: 3 Module × 3 Harmonische × (Re, Im) | 18 | zweiseitig | 2,991 | 4,075 | 3,435 | 3,269 |
| H4: höchstens 21 + 2 Konfigurationen | 23 | einseitig | 2,852 | 3,780 | 3,236 | 3,094 |

Bonferroni ist bei korrelierten Größen konservativ. Jede Hypothese wird mit α = 0,05 entschieden; die
Wahrscheinlichkeit, mindestens eine der beiden Primärhypothesen fälschlich zu verwerfen, ist höchstens
0,10, über H1–H4 höchstens 0,20 (Bonferroni-Schranke). Wegen der großen t-Quantile bei wenigen
Freiheitsgraden sind etwa 20 gültige Läufe je Konfiguration zweckmäßig; die Zahl folgt aus §5.4. Die
Spalten ν = 9, 19, 29 sind Beispiele (n_min = 10, 20, 30).

**Warum PB1.** Mit einer reinen Power-Bedingung ((c + 1,645)·u_c ≤ Δ und kein |z| > c; 1,645 = z₀,₉₅)
könnte die Vertrauensgrenze der Abweichung bei ν → ∞ bis 1,371·Δ reichen. PB1 verlangt, dass jedes
Intervall in ±Δ liegt; notwendig ist u_c ≤ Δ/c. Beispiel in A4: Δ(F_min) = 0,117 N, u_c ≤ 0,0327 N (ν → ∞)
bzw. 0,0269 N (ν = 19).

**Aufnahmeschwelle für V.** Bei n_min = 20 ist (c₄ + 1,645)·u_c,erw = 4,881·u_c,erw, für ν → ∞
4,497·u_c,erw. Liegt der wahre Wert an der Schwelle, bestätigt ein Punkt ein zutreffendes Vorzeichen mit
etwa 93 % (n_min = 20, nichtzentrale t-Verteilung) bzw. 95 % (ν → ∞); 23 unabhängige Punkte an der Schwelle
bestätigen es zusammen nur mit etwa 0,20. Die Bestätigungswahrscheinlichkeit von H4 wird deshalb in der
Planungssimulation bestimmt und in Teil B berichtet; sie ist keine Bedingung.

**Ersatzregel für c.** Der Monte-Carlo-Standardfehler einer Rate 0,05 aus 1000 Kampagnen ist 0,0069; die
Schwelle 0,05 plus zwei Standardfehler beträgt 0,064. Das ersetzte c gilt in z⁰, z¹ und PB1; das Quantil
von max |z⁰| ist konservativ gegenüber der gemeinsamen Bedingung für z⁰ und z¹.

**Fehlalarme bei korrekter Funktion.** Annahmen: ⟨N⟩ aller Laufarten normalverteilt mit derselben
Streuung, keine Drift, σ̂_ref aus 42 gleich getakteten Referenzläufen (leave-one-out). Die Angaben zu S1
und S3 sind obere Schranken, keine Raten des Verfahrens.

- **G1:** je Lauf höchstens 1,5 % (ungünstigste Lage: Interpolation ganz auf einen Referenzlauf), 0,61 %
  mittig zwischen zwei Referenzläufen (Monte Carlo über die Streuung von σ̂_ref).
- **S1 über G1:** Der erste Lauf wird mit der ungünstigsten Lage angesetzt, die Wiederholung liegt mittig
  zwischen den frischen Referenzläufen R₂ und R₃; beide Prüfungen sind bei gegebenem σ̂_ref unabhängig. Die
  Vorprüfung wird nicht berücksichtigt; sie senkt die Rate nur. Schranke je Lauf: 2,5·10⁻⁴.
- **S1 über Nullpunktalarme:** Alarm und Bestätigung teilen den vorangehenden Referenzlauf und sind
  deshalb korreliert. Schranke je Referenzlauf und Kanal: 7,3·10⁻⁴ (Monte Carlo); vier Kanäle (Summe und
  drei Zellen).
- **S1 über eine Kampagne:** Bei 20 Blöcken mit 23 Konfigurationen an einem Messtag sind es ohne Aufwärm-
  und Wiederholungsläufe 565 Läufe: 460 Kombinations-, 63 Einzelmodul- und 42 Referenzläufe (21 in den
  Kontrollsätzen, 20 in der Blockmitte, ein Schlussreferenzlauf), 21 Kontrollsätze. Bonferroni-Schranke:
  523·2,5·10⁻⁴ + 42·4·7,3·10⁻⁴ ≈ 0,25. Allgemein sind es (N_K + 5)·n + 5·d Läufe; jeder weitere Messtag
  bringt einen Kontrollsatz und einen Schlussreferenzlauf und erhöht die Schranke um
  3·2,5·10⁻⁴ + 2·4·7,3·10⁻⁴ ≈ 0,0066. Aufwärmläufe tragen nichts bei (A9.12); Wiederholungen erhöhen die
  Schranke je Lauf wie oben.
- **S3:** Die Statistik (x − x̄₀)/(s·√(1 + 1/n₀ⱼ)) ist t-verteilt mit n₀ⱼ − 1 Freiheitsgraden; mit
  c_S = t(1 − 0,05/42; n₀ⱼ − 1) (bei n₀ⱼ = 20: 3,503) löst ein Kontrollsatz über die 21 Größen mit höchstens
  5 % aus (Bonferroni-Schranke, exakt je Größe). Bestätigung durch die sofortige Wiederholung: höchstens
  9,5·10⁻⁴ je Kontrollsatz (Bonferroni über 21 Größen; der Summand je Größe per Monte Carlo, weil erste
  Messung und Wiederholung dasselbe Phase-0-Mittel teilen). Über die 21 Kontrollsätze einer solchen Kampagne
  höchstens 0,020.
- **Aufwärmen:** Ohne Drift bleibt das Kriterium (§6) nach zehn Referenzläufen mit etwa 6·10⁻⁴ unerfüllt.

---

## A9 · Verfahren im Einzelnen

### A9.1 Aufbau

- **Kanäle.** Drei Wägezellen im Dreieck, optischer Wegkanal (Phase 0: Weg der bewegten Masse relativ zum
  Rahmen; Phase 1: Einfederung des Körpers), drei Phasenencoder mit Indeximpuls, Beschleunigungssensor am
  Rahmen, Blindkanal (Brücke aus Festwiderständen am gleichen Verstärkertyp, gleicher Kabelweg; zeigt die
  Einstreuung unter echter Motorlast), Temperaturfühler an jeder Zelle und jedem Antrieb. Ein Sinusprofil
  liefert ohne Liftoff keine Schiefe; das Profil braucht eine Nocke oder einen programmierbaren Aktuator.
- **Lagerung und Kabel.** Füße lateral entkoppelt auf den Zellen (kinematische Lagerung, etwa
  Kugel–Kegel, Kugel–Kerbe, Kugel–Ebene). Alle Kabel laufen vom Körper in einer weichen, festgelegten
  Schlaufe mit Zugentlastung zum Unterbau; die Führung wird fotografisch dokumentiert und bleibt bis zum
  Ende von Phase 1 unverändert.
- **Messkette.** Feste Verstärkung; keine Softwarefilter, automatische Nullpunktnachführung,
  Stillstandserkennung, adaptive Filter oder Bereichsumschaltung; analoge Anti-Aliasing-Filter gleicher
  Bauart in allen Kraftkanälen. Die Einstellungen stehen in Teil B und in den Metadaten jedes Laufs.
- **Zeitbasis.** Gemeinsame Zeitbasis aller Kanäle; Kraftkanäle gleichzeitig abgetastet oder mit bekanntem,
  korrigiertem Kanalversatz. Die Indeximpulse stempelt ein Zeitgeber derselben Zeitbasis; die Quantisierung
  360°·f/f_clk beträgt höchstens 0,01° (bei 10 Hz f_clk ≥ 360 kHz).

### A9.2 Phase 0

- **P0.1** Jede Zelle einzeln und eingebaut mit rückgeführten Gewichtsstücken, auf- und absteigend;
  Orientierung: DKD-R 3-3 „Kalibrierung von Kraftmessgeräten“, Revision 1 (DOI 10.7795/550.20250130);
  DKD-R sind Richtlinien, keine Normen. Nullpunkt je Zelle bei abgehobenem Körper (Hubvorrichtung,
  reproduzierbare Wiederauflage). Gewichtsstück an mindestens fünf Stellen (Mitte, über jeder Zelle, über den
  Modulachsen); bekannte Horizontalkraft in zwei Richtungen. Elektronik mit Brückensimulator: zwei Signale
  mit verschiedenen Harmonischen einzeln und als Summe. Ergebnis: Kennlinie, Linearitäts- und
  Umkehrspanne, Kriechen, Kalibrierunsicherheit, Nullpunkt je Zelle; Einfluss von Laststelle, Querkraft und
  Superpositionsfehler der Elektronik je ≤ 0,1·Δ_q (Nachweis in Teil B).
- **P0.3** D1; D2 bei jeder Frequenz des 1-Hz-Rasters im Bereich (d); statische Summe und Umkehrspanne mit
  der Kabelschlaufe in Soll- und in einer zweiten Lage; Nebenschlusseinfluss ≤ 0,1·Δ_q.
- **Endmontage.** Zeitpunkt protokolliert, Fotos. Danach bis zum Datenschluss kein Abheben des Körpers,
  kein Lösen von Massen, Kabeln oder Encodern. Nicht als Veränderung zählen das Ausrichten des
  berührungslosen Wegkanals zwischen P0.5 und Phase 1, das Ankoppeln und Lösen der Anregung in P0.4 und
  für P0.5 angebrachte Messmarken, die bis zum Datenschluss bleiben.
- **P0.4** Komplexe Übertragungsfunktion je Zelle und der Summe mit Impulshammer oder Shaker, Module
  geparkt, auf der gemeinsamen Zeitbasis bis zur Grenzfrequenz der Anti-Aliasing-Filter; Wiederholung mit
  doppelter Anregungsamplitude (Linearität: beide gleich innerhalb der Unsicherheit). Orientierung: DKD-R
  3-10 Blatt 1 „Dynamische Kalibrierung von einachsig beanspruchten Kraftmessgeräten und Prüfmaschinen
  (Grundlagen)“ (DOI 10.7795/550.20240404) und Blatt 2 (Sinusverfahren, Ausgabe 2019). Ergebnis: K, C, f_n,
  ζ aus der Anpassung des 1-FG-Modells an die komplexe Übertragungsfunktion in einem festgelegten
  Frequenzband, gewichtet mit der Kohärenz (Verfahren im eingefrorenen Code), alle in N oder N_c sichtbaren
  Moden f_m, ζ_m, Übertragung der Kraftkette G_F(ω) je Zelle und Summe.
- **P0.5** Wegkanal auf die bewegte Masse jedes Moduls, Encoderwinkel, bei f über [Teil B] Zyklen:
  x_k⁽ʲ⁾ und a_k⁽ʲ⁾ = −(kω)²·x_k⁽ʲ⁾ bezogen auf den eigenen Indeximpuls; Δδⱼ mit u(Δδⱼ) ≤ 0,1°; Übertragung
  des Wegkanals G_x(ω); Parkposition.
- **P0.6** Sollphasen aller Konfigurationen; Wiederholbarkeit des Indeximpulses je Encoder; statischer
  Versatz, Jitter σⱼ.
- **Laufdauer in Phase 0.** Alle Läufe bei einer Frequenz haben dieselbe Dauer, mit Einschwingzeit T_e,P
  und Fenster T_a,P [Teil B]. Ausgewertet werden die ersten ganzen Zyklen der Länge T_a, die T_e nach Ende
  der Rampe beginnen (Kürzen auf die ersten Zyklen); dazu muss T_e + T_a ≤ T_e,P + T_a,P sein.
- **P0.7** Mindestens 42 Referenzläufe, verschachtelt mit P0.8–P0.10 bei jeder gemessenen Frequenz, je einer
  nach zwölf anderen Läufen; σ̂_ref und σ̂_ref,c aus den Läufen bei f.
- **Reihenfolge der Schwellen.** (1) G2–G10 auf die Phase-0-Läufe anwenden, mit σ_tol und σ_Δ aus allen
  Läufen der jeweiligen Art (Median bzw. MAD, G2, G4). (2) ε_ctrl nach §8.8 und A9.8 aus den danach
  gültigen Läufen. (3) G1 anwenden. p̂ ist der Anteil der danach ungültigen Pilotläufe; alle Streuungen
  stammen aus den gültigen Läufen.
- **Frequenzsuche.** (1) f_u und f_zul bestimmen (§5.3; (a) mit dem Auslegungswerkzeug, den Parametern aus
  P0.1–P0.4 und dem Konstruktionsprofil, ohne Zusatzkonfigurationen). (2) Bei f_zul P0.5–P0.8 und P0.10
  ausführen; (a) mit der Superposition je Zelle ohne Bandbegrenzung prüfen; k_max nach §5.4 bestimmen.
  (3) Kandidaten sind die Rasterfrequenzen f_u … f_zul, die (d) und (c) mit der nach dem
  Auslegungswerkzeug auf diese Frequenz skalierten Struktur und den Pilotstreuungen bei f_zul erfüllen.
  (4) Den kleinsten noch nicht geprüften Kandidaten messen (bei f_zul die vorhandenen Daten) und mit diesen
  Daten (a)–(d) prüfen; der erste, der besteht, ist f. (5) Besteht keiner: Befund „kein zulässiger
  Arbeitspunkt“, veröffentlicht; der Aufbau wird überarbeitet. In Teil B gehen nur Werte bei f ein.
- **k_max, T_a und Laufzahl** (§5.4), in dieser Reihenfolge: Für k = k_b, k_b − 1, …, 3 und je k für T_a =
  N_z/f mit N_z = 1, 2, …, solange T_e + T_a ≤ T_e,P + T_a,P: (i) s_q(T_a) aus den Pilotläufen, gekürzt auf
  die ersten N_z Zyklen; (ii) T_e und T_Lauf mit den Moden bis k·f; (iii) Planungssimulation: n₀ ≥ 20 und
  n_min minimieren N_K·n_min + 3·n₀ unter den Bedingungen von §5.4, bei Gleichstand das kleinere n_min; (iv)
  Rauschbias b_i mit diesen n_min und n₀; (v) Rauschbias-Bedingung und n = n_min + r ≤ n_max (§5.3 c)
  prüfen. Das erste Paar (k, T_a), das (v) erfüllt, legt k_max, T_a, n_min und n₀ fest. Obere
  80-%-Vertrauensgrenze einer Streuung s mit ν Freiheitsgraden: s·√(ν/χ²₀,₂(ν)); t-Quantile mit dem
  erwarteten ν_eff. Der Rauschbias berücksichtigt, dass Messkurve und vorhergesagte Summe dreier
  Einzelmodulkurven verschiedene Rauschpegel haben.

### A9.3 Inhalt von Teil B

1. alle Ergebnisse von P0.1–P0.10 mit Unsicherheiten, die SHA-256-Prüfsummen aller Rohdaten der Phase 0
   und der Pilotläufe und die Commit-Hashes des verwendeten Codes;
2. die Werte aller Platzhalter: Parkposition und Δ_park; Kanalliste, Abtastrate, Auflösung, Verstärker-
   und Filtereinstellungen; Zyklenzahl der Profilmessung; Δδⱼ; f_u, f_zul, f, k_max; T_warm, T_park,
   T_ramp, T_e, T_e,P, T_a, T_a,P, T_ab, T_Lauf; σ_tol, δf_tol; T_P0, TK_C, ΔT; σ̂_ref, σ̂_ref,c, ε_ctrl
   (mit Prüfgröße, kritischem Wert und gegebenenfalls σ̂_betr), σ_c, σ_Σ, F_LO; σ_Δ; n₀, n_min, r, n, n_max,
   d; T_verfügbar;
3. die Einzelmodul-Mittelkurven N̄⁽ʲ⁾(θ), gesamt und je Zelle, mit ihren Bootstrap-Replikaten als Datei;
   zusammen mit dem registrierten Code legen sie die Vorhersage für jede gemessene Phasenlage fest;
4. die Vorhersage bei den Sollphasen und dem Jitter aus P0.6: F̂_min − N_s, N̂_k (k = 1 … 3), γ̂₁, Â, F̂_max
   je Konfiguration mit Unsicherheit; D_q und Δ_q; zum Vergleich die Vorhersage des Auslegungswerkzeugs mit
   den Parametern aus P0.1–P0.5;
5. die vorhergesagte Spitzenlage φ̂₂*, das Fitfenster W und die erwartete Halbbreite;
6. die H3-Vorhersage und je Harmonischer die Angabe, ob sie den Kontakt prüft; ein Vergleich mit gemessenen
   Einzelmodul-Harmonischen wird vor dem Datenschluss nicht berechnet;
7. die Prüfmenge V und die Entscheidung über Zusatzkonfigurationen und gespiegelten Schnitt;
8. die Laufreihenfolge;
9. die Ergebnisse der Planungs- und Kalibriersimulation, auch die Bestätigungswahrscheinlichkeit von H4
   und den kritischen Wert für ε_ctrl, gegebenenfalls das ersetzte c;
10. eine Erklärung, welche Daten und Auswertungen bei der Registrierung vorlagen und wer welche Ausgaben
    gesehen hat;
11. die Einträge des Abweichungsprotokolls bis zu diesem Zeitpunkt.

### A9.4 Verarbeitungskette

Für alle Laufarten (Kombination, Lⱼ, R, D2) identisch: (1) Rohdaten schreibgeschützt; Umrechnung mit der
statischen Kalibrierung je Zelle; N = N₁ + N₂ + N₃. (2) Keine Softwarefilter. (3) Segmentierung am
Indeximpuls (θ, A1); nur Zyklen, die vollständig im Auswertefenster liegen. (4) Resampling jedes Zyklus auf
N_θ = 2000 äquidistante Stützstellen durch lineare Interpolation. (5) Mittelkurve je Lauf; DFT;
Koeffizienten oberhalb k_max null. (6) Je Lauf N_k, ⟨N⟩, γ₁, φ̄ⱼ, σⱼ, zyklusweise Phasenzeiger; dieselben
Größen je Zelle. (7) Je Konfiguration Konfigurationsmittelkurve und daraus F_min − ⟨N⟩, N_k, γ₁, F_max, A.
Die Schritte 3–5 und die Mittelung über Läufe sind linear und vertauschen mit der Summe über Module; die
Superposition bleibt deshalb erhalten, wenn Einzelmodul- und Kombinationsläufe identisch verarbeitet werden.

### A9.5 Bootstrap und Freiheitsgrade

B = 10 000 Replikate je Anteil. **A (Messung):** Läufe der Konfiguration mit Zurücklegen ziehen, mit ihren
Phasenzeigern; ȳ, ρⱼₖ und ŷ neu berechnen, r bilden. **B (Vorhersage):** Einzelmodulläufe jedes Moduls mit
Zurücklegen ziehen (Phase 0 für ŷ⁰, Phase-1-Kontrollläufe für ŷ¹), ρⱼₖ fest; r bilden. u_c² = Var_A +
Var_B, für lineare und nichtlineare Größen gleich. Ein eigener Phasenterm entfällt, weil die Vorhersage mit
den gemessenen Zeigern derselben Läufe gebildet wird. ν_eff nach §8.3: n_A = gültige Läufe der
Konfiguration (H3: gültige Phase-1-Kontrollläufe des Moduls), n_B = min_j der gültigen Einzelmodulläufe der
jeweiligen Basis, Monte Carlo mit ν = ∞, also ν_eff = (n_A − 1)·u_c⁴/Var_A² in H3.

### A9.6 Zeltfit

φ* wird in Schritten von 0,001° über [min W, max W] gesucht; für jedes φ* werden F*, s_L, s_R ungewichtet
nach der Methode der kleinsten Quadrate bestimmt; gewählt wird φ* mit der kleinsten Residuenquadratsumme,
bei Gleichstand das kleinste. Fitfenster: Mittelpunkt ist der Schnittpunkt, der φ̂₂* aus Teil B am nächsten
liegt, bei Gleichstand der kleinere; W sind die Schnittpunkte in [Mittelpunkt − w, Mittelpunkt + w]; w ist
der größte Wert aus {4°, 6°, …, 20°}, für den W auf jeder Seite des Mittelpunkts mindestens zwei Punkte hat
und F̂_min an keinem Punkt in W um mehr als 0,25·min_i u_c,erw,i(F_min) von der eigenen Zeltanpassung
abweicht; ohne solches w ist H2 nicht entscheidbar. Abszisse ist die gemessene Profilphase
φ̄₂^P = −arg ρ₂₁ + Δδ₂ (A1). Intervall: In jedem von 10 000 Replikaten werden die Läufe jeder Konfiguration
und die Einzelmodulläufe jedes Moduls mit Zurücklegen gezogen, Abszissen und ρⱼₖ neu gebildet, beide Fits
wiederholt und Δφ* = φ₂*,Messung − φ̂₂* gebildet; [a, b] sind das 2,5- und das 97,5-%-Quantil, getrennt
für ŷ⁰ ([a⁰, b⁰]) und ŷ¹ ([a¹, b¹]).

### A9.7 Monte-Carlo-Fortpflanzung (H3)

a_k⁽ʲ⁾ = −(kω)²·x_k⁽ʲ⁾ aus P0.5, korrigiert um G_x; G_F ist die komplexe Übertragung der Kraftkette relativ
zur Zeitbasis der Indeximpulse (P0.4); alles bezogen auf den eigenen Indeximpuls und bei der gemessenen
Frequenz. 10 000 Ziehungen aus den Unsicherheiten von K und C (Kovarianz der Anpassung), M und m_j, x_k⁽ʲ⁾,
G_F, G_x, f und gegebenenfalls der D2-Signatur; Vorhersage und u(ŷ) sind Mittelwert und
Standardabweichung von Real- und Imaginärteil. Konfirmatorisch ist H3, weil kein Modellparameter aus
Kraftdaten der Einzelmodulläufe bestimmt wird und die Parameter vor jeder Auswertung dieser Daten
hinterlegt sind (§5.2, je Frequenz). Vor dem Datenschluss wird die Vorhersage nicht mit gemessenen
Einzelmodul-Harmonischen (Phase 0 oder 1) verglichen; der Vergleich mit Phase 0 wird danach berechnet und
berichtet. Eine Bestätigung nach PB3 schließt die starre Auflage für eine Harmonische aus, deren
Abstand |N̂_k⁽ʲ⁾ − G_F·m_j·a_k⁽ʲ⁾| größer als Δ ist.

### A9.8 Nullkontrolle

Zusammenfassender Test: Welch-Satterthwaite-t-Test von Δ⟨N⟩ aller Kombinationsläufe gegen Δ⟨N⟩ der
Referenzläufe von Phase 1 (leave-one-out), zweiseitig, α = 0,05; einbezogen sind alle Läufe, die nicht aus
anderen Gründen als G1 ungültig sind. Berichtet werden Differenz, 95-%-Intervall und dessen Lage zu
±ε_ctrl. Die Differenz zweier Referenzläufe streut √(4/3)-mal so stark wie die Leave-one-out-Statistik
(Varianz 2σ² gegen 1,5σ²); daher die Schwelle 3·√(4/3)·σ̂_ref des Nullpunktalarms. Ein Zellalarm weist auch
auf einen verrutschten Fuß hin. Der Randterm aus der Impulsänderung des Schwerpunkts über das Fenster
(Literaturabgleich §4.2, T3) ist bei ganzen Zyklen im stationären Zustand null; er wird aus Weg- und
Beschleunigungskanal abgeschätzt und berichtet.

**ε_ctrl in Phase 0** (§8.8), nach G2–G10 und vor G1: Jeder gültige Pilot- und Einzelmodullauf an der
relativen Lage β zwischen seinen Referenzläufen ergibt d = Δ⟨N⟩·√(1,5/(1 + β² + (1 − β)²)); bei gleicher
Streuung σ aller Läufe hat d die Varianz 1,5σ² wie die Leave-one-out-Statistik. Prüfgröße ist
F = s_d²/σ̂_ref², s_d die Standardabweichung der d. Kritischer Wert ist das 95-%-Quantil von F in 10 000
simulierten Datensätzen mit derselben Laufanordnung (Lagen β, gemeinsame Referenzläufe) und normalverteiltem
⟨N⟩ gleicher Streuung in allen Laufarten. Liegt F darüber, gilt ε_ctrl = 3·σ̂_betr mit σ̂_betr = s_d. Ein
F-Test mit nominellen Freiheitsgraden wäre zu liberal, weil die Leave-one-out-Werte korreliert sind und
benachbarte Läufe dieselben Referenzläufe teilen.

### A9.9 Sensitivitätsanalysen

Vorhersage aus Phase-0- und Phase-1-Einzelmodulläufen zusammen; blockweise Vorhersage aus den
Kontrollläufen desselben Blocks; Vorhersage ohne Jitterzeiger (ρⱼₖ = e^{−ikφ̄ⱼ}); k_max − 2 (nicht unter 3)
und, soweit (b) es zulässt, k_max + 2; Auswertung je Block; Superposition je Zelle; H2 mit w ± 2°;
Auswertung einschließlich der nach G1 ungültigen Läufe; Ausschlussraten je Konfiguration.

### A9.10 Metadaten je Lauf

Lauf-ID, Registrierungskennung, Block, Konfiguration (Sollphasen), Laufart, Start- und Endzeit, Frequenz,
Temperaturen, Versorgungsspannung, Verstärker- und Filtereinstellungen, Firmware- und Softwarestände,
Kalibrier-IDs, Bediener, Ergebnis der Gültigkeitsprüfung mit Grund, Protokollnotizen.

### A9.11 Pipelinetest und Simulationen

Einzelmodul- und Kombinationsläufe aus `linear_solver.py` mit Rauschen, Jitter und Drift müssen H1
bestätigen; Daten mit bekannter Nichtlinearität (etwa ein Hertzscher Kontakt nach Testebene T0 des
Literaturabgleichs) oder mit eingebauter Modulkopplung müssen H1 falsifizieren, wenn die Abweichung Δ
übersteigt. Vor Teil B zusätzlich je Szenario 1000 synthetische Kampagnen mit den geplanten n, n₀ und den
Pilotstreuungen: Rate falscher Falsifikation von H1 (Soll ≤ 0,05), Überdeckung des H2-Intervalls
(Soll ≥ 0,95), Rate „nicht entscheidbar“, Power gegen Kopplung und Hertz-Kontakt, Bestätigungswahrscheinlichkeit
von H4 (berichtet, keine Bedingung); dieselbe Simulation liefert n_min, n₀ und den Rauschbias. Den kritischen
Wert für ε_ctrl liefert eine eigene Simulation nach A9.8.

### A9.12 Phase 1 im Ablauf

- **Messtag.** Aufwärm-Referenzläufe (§6), höchstens zehn; sie lösen keinen Nullpunktalarm aus, und der
  letzte gilt als gültiger Referenzlauf für N_s,int und als Vergleich für den ersten Nullpunktalarm. Nach
  dem letzten Kontrollsatz des Tages folgt der Schlussreferenzlauf, damit jeder Lauf zwischen zwei
  Referenzläufen liegt. Läufe je Kampagne: (N_K + 5)·n + 5·d, dazu Aufwärm- und Wiederholungsläufe; in
  §5.3 (c) als 15·d (fünf Läufe und höchstens zehn Aufwärmläufe je Tag) und Faktor 1/(1 − p̂).
- **Wiederholungsplatz.** Ein vor Beginn des Schlusskontrollsatzes als ungültig erkannter Lauf einer
  Konfiguration wird an einem Platz wiederholt, den der Generator von §6 gleichverteilt unter den offenen
  Konfigurationsplätzen des Blocks und dem Platz vor dem Schlusskontrollsatz zieht; höchstens zwei
  Wiederholungen je Konfiguration und Block. Was danach fehlt, deckt die Reserve r.
- **G1 und S1.** Die Vorprüfung gegen R₀ erkennt grobe Verstöße sofort. Steht ein G1-Verstoß erst mit dem
  nächsten planmäßigen Referenzlauf fest, folgen ebenfalls R₂, X′ und R₃, sofern der Schlusskontrollsatz
  noch nicht begonnen hat; danach festgestellte Verstöße werden weder wiederholt noch nach S1 geprüft. X′
  wird auch jenseits der Wiederholungsgrenze gemessen und zählt als Wiederholung. S1 greift nur bei einem
  G1-Verstoß von X′.
- **Kontrollläufe.** Ein aus anderem Grund als G1 ungültiger Kontrolllauf (bei R auch ein unbestätigter
  Nullpunktalarm, §8.8) wird sofort wiederholt, höchstens zweimal; ist auch die zweite Wiederholung
  ungültig, wird angehalten und nach §9.2 verfahren.
- **Nach S2.** Die Konfiguration bleibt in den Blöcken und wird weiter gemessen, geht aber in keinen Test
  ein (§9.1); betrifft S2 ein Lⱼ, ist ŷ¹ ungültig (§8.2). Ein zweites S2 ohne festgestellten Apparaturfehler
  beendet Phase 1 (§9.2).

---

## Tabelle C · Artefakte und Kontrollen

| Quelle | Wirkung | Kontrolle |
|---|---|---|
| Thermische Drift (v1) | Nullpunkt- und Empfindlichkeitsdrift | Temperatur an Zellen und Antrieben, Aufwärmen, G7; Referenzläufe in jedem Block; nullpunktfreie Größen; ŷ¹, S3 |
| Mechanische Kopplung (v1) | Module beeinflussen einander | Gegenstand von H1; D2 |
| Vibrationen (v1) | nicht synchrone Kraftanteile | Referenzläufe, Beschleunigungssensor, phasensynchrone Mittelung |
| EM-Rückwirkungen (v1) | Einstreuung der Antriebe | D2; Blindkanal in jedem Lauf |
| Software-Filter (v1) | Formänderung der Kurve | nur die Bandbegrenzung auf k_max, für alle Läufe identisch, Code eingefroren |
| Sensor- und Kettennichtlinearität (v1, erweitert) | verzerrte Wellenform, verletzte Superposition | P0.1 (Brückensimulator), P0.4 (zwei Amplituden), feste Einstellungen; G5 |
| Phasenfehler (v1) | falscher Konfigurationspunkt | gemessene Phasenzeiger ρⱼₖ; Profilphasen mit Δδⱼ; G2 |
| Erwartungseffekte (v1) | Auswahl, nachträgliches Justieren | Randomisierung, eingefrorene Regeln, automatische Gültigkeitsprüfung, Blindung, Abweichungsprotokoll |
| Einzelzellen, Kippmomente (neu) | eine Zelle hebt ab, obwohl N > 0 | Sicherheitsabstand je Zelle, G6, S2 |
| Kraftnebenschluss, Querkräfte, Übersprechen (neu) | Nebenpfad oder Hysterese; Summe hängt von der Laststelle ab | kinematische Lagerung, Kabelschlaufe; P0.1, P0.3 |
| Resonanzen der Auflage, weitere Moden (neu) | Überhöhung, Empfindlichkeit gegen K, ζ, f | P0.4; Bedingung (b), k_max-Regel |
| Drift der Einzelmodulantwort (neu) | Vorhersage aus Phase 0 veraltet | ŷ¹; S3; keine mechanischen Eingriffe |
| Zeitbasis, Kanalversatz, Indexauflösung (neu) | Phasenfehler in ρⱼₖ und H3 | gemeinsame Zeitbasis, Zeitstempel; G_F, G_x |
| Frequenzabweichung (neu) | Profilbeschleunigung ∝ f², H(kω) | G3 |
| Parkfehler (neu) | geparktes Modul bewegt sich oder steht falsch | Encoder der geparkten Module; G9 |
| Segmentierung, Resampling (neu) | Verschmierung der Mittelkurve | identische Verarbeitung; Abtastrate; Pipelinetest |
| Rauschbias des Minimums (neu) | F_min systematisch zu klein | Rauschbias-Bedingung |
| Einschwingvorgänge (neu; Erfahrung v3) | scheinbare Mittelwertabweichung, verzerrte Form | T_e, G4, H0 |

---

## Tabelle F · Festlegungen

Gewählte Zahlenwerte ohne Messung, je mit einer Zeile Begründung.

| Festlegung | Stelle | Begründung |
|---|---|---|
| α = 0,05 je Familie | §3, §8.4 | übliche Irrtumswahrscheinlichkeit; jede Hypothese wird für sich berichtet |
| 25 % der statischen Zelllast als Mindestabstand | §5.3 (a) | Nahe am Abheben wird ein realer Kontakt nichtlinear, und im Liftoff-Bereich ist der Zustand nicht eindeutig |
| Faktor 2 Resonanzabstand (k·f ≤ f₁/2) | §5.3 (b) | begrenzt \|H\| auf 1,33 und die Frequenzempfindlichkeit auf 0,67 (A6) |
| Δ_q = 0,25·D_q | §8.5 PB1 | Eine Bestätigung muss die vorhergesagte Struktur auf ein Viertel auflösen, nicht nur ihr Vorhandensein zeigen |
| Δ = 0,10·\|N̂_k⁽ʲ⁾\| | §8.5 PB3 | Ein Modelltest mit gröberer Auflösung unterscheidet nichts |
| Halbbreite ≤ 1° | §3 H2 | halbe Schrittweite des Schnitts |
| (c₄ + 1,645)·u_c,erw für V | §8.5 | bestätigt ein zutreffendes Vorzeichen an der Schwelle mit etwa 93 % je Punkt (n_min = 20, A8) |
| k_max ≥ 3 | §5.4 | H1 prüft N₃ |
| 0,1·u_c,erw für Rauschbias und Frequenztoleranz | §5.4, G3 | systematischer Beitrag klein gegen die Unsicherheit |
| 0,1·Δ_q für Laststelle, Querkraft, Elektronik, Nebenschluss | §5.2 | Messkettenfehler klein gegen die Äquivalenzgrenze |
| \|D2_k\| ≤ 0,01·min_j \|N̂_k⁽ʲ⁾\| | §5.2 | ein Zehntel der H3-Grenze |
| ε_ctrl = 3·σ̂_ref bzw. 3·σ̂_betr | §8.8 | Form aus Einordnung §4; seltene Fehlausschlüsse (A8) |
| Nullpunktalarm 3·√(4/3)·σ̂_ref | §8.8 | dieselbe Schwelle in Standardabweichungen wie G1 für die Differenz zweier Referenzläufe |
| mindestens 42 Referenzläufe | §4, P0.7 | mindestens 40 Leave-one-out-Werte für σ̂_ref |
| Referenzlauf nach je zwölf anderen Läufen in Phase 0 | P0.7 | etwa der Abstand in Phase 1 (Blockmitte, Kontrollsätze) |
| 5·σ für F_LO | §4 | Rauschen löst praktisch keinen Liftoff-Befund aus |
| c_S mit höchstens 5 % Fehlalarm je Kontrollsatz | §9.2 S3 | ein Kontrollsatz je Block; Bestätigung durch Wiederholung senkt die Rate weiter |
| σ_tol = dreifacher Median von σⱼ der Pilotläufe | G2 | robust gegen einzelne Ausreißer der Pilotläufe |
| σ_Δ = 1,4826·MAD | G4 | robuste Standardabweichung aus allen Läufen einer Art, vor jeder Ausschlussentscheidung bestimmbar |
| ΔT aus höchstens 0,1 % Empfindlichkeitsänderung | G7 | klein gegen Δ_q; Antriebstemperaturen wirken über die Phase und werden von G2 erfasst |
| δφ_tol = 0,5° | G2 | ein Viertel der Schrittweite des Schnitts; die Vorhersage verwendet ohnehin die gemessenen Zeiger |
| u(Δδⱼ) ≤ 0,1° | P0.5 | klein gegen δφ_tol und die H2-Halbbreite |
| Zeitstempel-Quantisierung ≤ 0,01° | §5.1 | vernachlässigbar gegen u(Δδⱼ) |
| Interpolationsfehler ≤ 10⁻³ | §5.1 | Amplitudenfehler klein gegen Δ |
| N_θ = 2000 | §4 | so viele Stützstellen je Periode wie in der Engine |
| zehn Zeitkonstanten für T_e | §6 | Restamplitude e⁻¹⁰ ≈ 4,5·10⁻⁵ |
| T_e auf ganze Sekunden aufgerundet | §6 | einfache Steuerung; verlängert nur |
| Fünftel und 3·σ_Δ für G4 | G4 | Anfang und Ende mit gleich vielen Zyklen; seltene Fehlausschlüsse |
| drei Pilotkonfigurationen mit je mindestens 20 gültigen Läufen | §5.4 | gepoolt mindestens 57 Freiheitsgrade für die Streuungen |
| jeder Pilotabstand mindestens 10° von 120° | §5.4, A7 | keine Pilotkonfiguration ist zu einem Schnittpunkt äquivalent, auch nicht bei Phasenfehlern weit über δφ_tol; kein physikalisches Abstandsmaß |
| Verdopplung von T_ramp bei Liftoff in der Rampe | §5.4 | endliche, eindeutige Anpassung |
| mindestens 20 Einzelmodulläufe je Modul vor der Planung | P0.8 | Streuungen für die Planungssimulation |
| Bestätigungswahrscheinlichkeit 0,8 bei oberer 80-%-Grenze der Streuungen | §5.3 (c), §5.4 | übliche Power, abgesichert gegen zu kleine Pilotstreuungen |
| Reserve r = ⌈n_min·p̂/(1 − p̂)⌉ + 2 | §5.4 | erwartete Ausfälle plus zwei |
| höchstens zwei Wiederholungen je Konfiguration und Block, je Kontrolllauf | §6 | begrenzt die Blocklänge |
| Ausnahme G5, G8, G10 bei Liftoff (Kontaktast, S2) | §4, §9.2 | Übersteuerung, äußere Störung und defekte Aufzeichnung sagen nichts über den Kontakt |
| Referenzlauf nach der zwölften Konfiguration | §6 | etwa Blockmitte bei 21 oder 23 Konfigurationen |
| mindestens n_min gültige Phase-1-Kontrollläufe je Modul | §3 H3 | gleiche Präzision wie für die Konfigurationen |
| Seed aus den ersten 16 Hexziffern (64 Bit) des SHA-256 des Hauptdokuments | §6 | vor Phase 0 festgelegt; 64 Bit sind der übliche Seed-Umfang |
| Reihenfolge der Konfigurationsliste | §6 | vor Phase 0 festgelegt, damit die Ziehung nicht von Teil B abhängt |
| B = 10 000 Bootstrap-Replikate | §8.3, §8.6 | Quantile von 2,5 % und 97,5 % stabil |
| 10 000 Monte-Carlo-Ziehungen (H3) | A9.7 | Mittel und Streuung stabil |
| 1000 synthetische Kampagnen je Szenario | §12, A9.11 | Standardfehler 0,0069 bei einer Rate von 0,05 |
| 10 000 simulierte Datensätze für den kritischen Wert von ε_ctrl | A9.8 | 95-%-Quantil stabil |
| Schwelle 0,064 der Ersatzregel für c | §8.4 | 0,05 plus zwei Monte-Carlo-Standardfehler |
| Welch-Test mit α = 0,05 | §8.8 | berichtet, ohne Einfluss auf H1–H4 |
| Streuungsvergleich für ε_ctrl mit α = 0,05 | §8.8, A9.8 | übliche Irrtumswahrscheinlichkeit; setzt ε_ctrl und damit G1 für alle Läufe |
| Fitfenster 4° … 20° in 2°-Schritten, mindestens zwei Punkte je Seite | §8.6 | Rasterweite des Schnitts; ein Zelt braucht zwei Punkte je Flanke |
| Fensterkriterium 0,25·min_i u_c,erw,i | §8.6 | Modellfehler des Zelts klein gegen die Messunsicherheit |
| Suchschritt 0,001° | A9.6 | klein gegen die Halbbreite |
| 1-Hz-Raster für f | §5.3 | endliche Suche; Kraft skaliert mit f² |
| Aufwärmkriterium: zwei Referenzläufe um weniger als σ̂_ref verschieden, höchstens zehn | §6 | Drift kleiner als die Streuung eines Laufs; ohne Drift bleibt es mit etwa 6·10⁻⁴ unerfüllt (A8) |
| Schlussreferenzlauf je Messtag | §6 | jeder Lauf liegt zwischen zwei Referenzläufen |
| mindestens täglich hinterlegtes Manifest | §0 | Verlust oder Änderung höchstens eines Tages unentdeckt |
| zwei räumlich getrennte Kopien | §10.2 | übersteht den Verlust eines Standorts |
| mindestens fünf Laststellen, zwei Kraftrichtungen, zwei Signale | P0.1 | Mitte, drei Zellen, Modulachsen; beide Querrichtungen; kleinste Summe für einen Superpositionstest |
| doppelte Anregungsamplitude | P0.4 | Linearitätsprüfung mit deutlichem Amplitudenunterschied |
| k_max ± 2 und w ± 2° | A9.9 | ein Rasterschritt der Sensitivitätsvariation je Richtung (w in 2°-Schritten) |
| Beispielspalten ν = 9, 19, 29 | A8 | n_min = 10, 20, 30 |

---

## Z · Zahlennachweis

Alle Befehle aus dem Wurzelverzeichnis des Repositorys. `--section`, `--phi3` und `--f` liegen seit Commit
`069cb9b` in `code/linear_solver.py` (§12, Werkzeug 1); mit diesem Stand sind die Zahlen nachgerechnet. Ein Einzelmodullauf wird als synchrone Phasung mit μ/3 gerechnet. ζ fest
heißt C = 2ζ√(KM) mit ζ = 0,099228. „Repo“: Zahl aus einem Repository-Dokument, hier nachgerechnet. „Zitat“:
Zahl aus einem Dokument oder einer Quelle, die nicht gerechnet wird. Festlegungen (Tabelle F) sind gewählt,
nicht gerechnet. „BL(KM; ARGS)“ heißt bandbegrenzt auf k ≤ KM:
`python3 -c "import sys;sys.path.insert(0,'code');import linear_solver as L;P,n=L.profile_spectrum();km=KM;P[km+1:]=0;L.profile_spectrum=lambda *a,**k:(P.copy(),n);L.section(ARGS)"`
mit ARGS = `None,0,0.4` (starr, μ = 0,4), `K,L.c_for(K,Z),0.4` oder `1e4,16,1.0` (Referenz). Stelle: „§“
Hauptdokument; A0–A9, Tab. C, Tab. F und Z Anhang.

| Zahl | Stelle | Befehl |
|---|---|---|
| F_min 5,3304 N (120°), 0,7677 N (100°), 1,6176 N (140°); 2°-Sekanten 0,2124 und 0,1952 N/° (0,212 und 0,195); ΔF_Zelt 4,5627 N | §1; A2.2, A3, A4 | `python3 code/linear_solver.py --section` |
| 20°-Sekanten 0,228 und 0,186 N/° (Exposé ≈ 0,23 / ≈ 0,19, Repo) | A3 | `python3 -c "print(round((5.3304-0.7677)/20,3), round((5.3304-1.6176)/20,3))"` |
| f_n = 19,74 Hz; 2f/f_n = 1,013; \|H₂\| = 5,03; 2°-Sekanten 0,09–0,12 N/° bei ζ fest, K = 3·10⁴ … 10⁷ N/m (Repo) | A3 | `python3 code/linear_solver.py --harmonics` |
| 4,24 %; 2 × 2524 Punkte (3,90 %); 6 × 74 Punkte (0,34 %); λ = 75,82 % bzw. 0 % bei (35°, 116°); 76,6 % starr; 48,6 % bei μ = 0,5 (Repo) | A3 | `python3 code/linear_solver.py --contact`; `python3 -c "print(round(100*5048/360**2,2), round(100*444/360**2,2))"`; Monostabilität: `python3 code/linear_solver.py --contact --grid` (ca. 6–8 min) |
| ζ = 0,099228; M·g = 6,3765 N | A3, Z | `python3 -c "print(round(16/(2*(1e4*0.65)**0.5),6), round(0.65*9.81,4))"` |
| γ₁ = +0,067 (K = 10⁴ N/m) und −0,450 (starr) am Triphasik-Punkt; A 0,6529 starr μ = 0,4 | §1; A2.3, A3, A4 | `python3 code/linear_solver.py --point 120 240`; `python3 code/linear_solver.py --point 120 240 --rigid` (ebenso mit `--mu 0.4`) |
| Vorzeichenregel: 55 Punkte auf φ₂ = 0°, φ₃ = 0°, φ₂ = φ₃, γ₁ ≥ +0,596, davon 0 negativ; 36 negative Werte insgesamt | §1; A3 | `python3 -c "import pandas as pd,numpy as np;d=pd.read_csv('data/sweep_19x19.csv');a,b=d.phi2_deg,d.phi3_deg;m=np.isclose(a,0)+np.isclose(b,0)+np.isclose(a,b);print(m.sum(),round(d.F_skew[m].min(),3),int((d.F_skew[m]<0).sum()),int((d.F_skew<0).sum()))"` |
| s_m = −0,196, +0,206, −0,011 N/°, Summe −5·10⁻⁵ | A2.2 | `python3 -c "import sys; sys.path.insert(0,'code'); import linear_solver as L; t,N=L.waveform(120,240); d=(L.waveform(120.0001,240)[1]-L.waveform(119.9999,240)[1])/0.0002; i=[j for j in range(len(N)) if N[j]<=N[j-1] and N[j]<=N[(j+1)%len(N)]]; i=sorted(sorted(i,key=lambda j:N[j])[:3]); print([round(float(d[j]),3) for j in i], round(float(sum(d[j] for j in i)),5))"` |
| lokale Steigungen 0,207 und 0,196 N/°; F_min 5,3097 / 5,3304 / 5,3108 N bei 119,9° / 120° / 120,1° | A2.2 | `python3 code/linear_solver.py --point 119.9 240`, ebenso `120 240`, `120.1 240`; `python3 -c "print(round((5.330390-5.309711)/0.1,3), round((5.330390-5.310811)/0.1,3))"` |
| Schiefeformel: cos(2ϑ₃ − ϑ₆) = −1,000 bzw. +0,912; γ₁(k ≤ 6) = −0,3775 bzw. +0,0658 | A2.3 | `python3 -c "import sys;sys.path.insert(0,'code');import linear_solver as L,numpy as np;P,n=L.profile_spectrum();[print(K,[round(float(v),4) for v in (np.cos(2*np.angle(X[3])-np.angle(X[6])),0.75*abs(X[3])**2*abs(X[6])*np.cos(2*np.angle(X[3])-np.angle(X[6]))/((abs(X[3])**2+abs(X[6])**2)/2)**1.5)]) for K,C in ((None,0.0),(1e4,16.0)) for X in [P*L.transfer(K,C,P.size)[0]]]"`; Gegenprobe BL(6; `None,0,0.4`) und BL(6; `1e4,16,1.0`), Zeile 120° |
| Jitterfaktoren 0,99985 / 0,99939 / 0,99863 / 0,99453 / 0,98774 | A2.4 | `python3 -c "import numpy as np; s=np.radians(1.0); print([round(float(np.exp(-k*k*s*s/2)),5) for k in (1,2,3,6,9)])"` |
| Einzelmodul bei den Referenzparametern: lineares F_min = −2,057 N | A3 | `python3 code/linear_solver.py --point 0 0 --mu 0.3333333333333333` |
| gespiegelter Schnitt: F_min 3,0846 N, γ₁ −0,3846 | A3 | `python3 code/linear_solver.py --point 110 240`; `python3 code/linear_solver.py --point 240 110` |
| starr, μ = 0,4, 10 Hz: Kontaktast auf allen 21 Punkten; F_min 5,6452 / 5,1759 / 5,4581 / 5,3379 N (120° / 100°, 140° / 116° / 112°, 128°); 2°-Sekanten 0,0469 / 0,0468 N/°; γ₁ −0,4498 (120°), −0,7932 (100°, 140°); F_max 7,0752 N (7,08 N) | A2.2, A4 | `python3 code/linear_solver.py --section --rigid --mu 0.4` |
| starr, μ = 0,4, 14 / 19 / 20 Hz: F_min 4,9432 / 4,0233 N, 3,7365 / 2,0424 N, 3,4513 / 1,5741 N; 2°-Sekanten 0,0918, 0,1691, 0,1874 N/°; γ₁ und A unverändert; Kontaktast auf allen Punkten | A4 | `python3 code/linear_solver.py --section --rigid --mu 0.4 --f 14` (ebenso `--f 19`, `--f 20`) |
| Liftoff am Schnittrand zwischen 23 und 24 Hz: F_min(100°) 0,0254 bzw. −0,5389 N | A4 | `python3 code/linear_solver.py --section --rigid --mu 0.4 --f 23` bzw. `--f 24` |
| Einzelmodul (starr, μ = 0,4): F_min 5,3642 N, F_max 8,2564 N, γ₁ +0,755 (10 Hz); F_min 1,9124 (21 Hz), 1,4771 (22 Hz), 0,0498 (25 Hz), −0,4664 N (26 Hz) | A4 | `python3 code/linear_solver.py --point 0 0 --rigid --mu 0.13333333333333333 --f F` mit F = 10, 21, 22, 25, 26 |
| synchron (starr, μ = 0,4): F_min 3,3397 N, F_max 12,0163 N, γ₁ +0,755 (10 Hz); F_min 2,0035 (12 Hz), 1,2443 (13 Hz), 0,4244 (14 Hz), −0,4563 N (15 Hz) | A4 | `python3 code/linear_solver.py --point 0 0 --rigid --mu 0.4 --f F` mit F = 10, 12, 13, 14, 15 |
| (0°, 180°) (starr, μ = 0,4): F_min 5,0340 N, F_max 9,1241 N, γ₁ +0,986 (10 Hz); F_min 2,0268 (18 Hz), 1,5300 (19 Hz), 0,4560 (21 Hz), −0,1213 N (22 Hz) | A4 | `python3 code/linear_solver.py --point 0 180 --rigid --mu 0.4 --f F` mit F = 10, 18, 19, 21, 22 |
| Anteile an M·g: 81,2; 63,1; 32,0; 24,7; 12,0 %; 52,4 / 31,4 / 19,5 % (synchron bzw. je Zelle 10 / 12 / 13 Hz); 78,9 / 31,8 / 24,0 % ((0°, 180°) 10 / 18 / 19 Hz); 30,0 / 23,2 % (Einzelmodul 21 / 22 Hz) | A4 | `python3 -c "Mg=6.3765; print([round(100*x/Mg,1) for x in (5.1759,4.0233,2.0424,1.5741,0.7677,3.3397,2.0035,1.2443,5.0340,2.0268,1.5300,1.9124,1.4771)])"` |
| Zellkraft: statisch 2,1255 N, höchstens 4,0054 N | A4 | `python3 -c "print(round(6.3765/3,4), round(12.0163/3,4))"` |
| ΔF_Zelt 0,4693 / 0,9199 / 1,6941 / 1,8772 / 4,5627 N; äußere Steigung 0,0135 N/°; innere 0,0468 N/°; Faktoren 1,96 und 4,0 | A4 | `python3 -c "print([round(a-b,4) for a,b in ((5.6452,5.1759),(4.9432,4.0233),(3.7365,2.0424),(3.4513,1.5741),(5.3304,0.7677))], round((5.3379-5.1759)/12,4), round((5.6452-5.4581)/4,4), round(0.0918/0.0469,2), round(0.1874/0.0469,2))"` |
| Knicke bei etwa 114° und 126° (114,01° und 125,98°) | A4 | `python3 -c "a=(5.3379-5.1759)/12; b=(5.6452-5.4581)/4; c=(5.6452-5.4580)/4; print(round((5.6452-120*b-5.1759+100*a)/(a-b),2), round((5.1759+140*a-5.6452-120*c)/(a-c),2))"` |
| K = 10⁶ N/m (ζ fest) gegen starr, μ = 1: \|N_k\| +0,3 / 1,0 / 2,4 % (10 Hz: 9,7522 / 3,2391 / 1,4158 gegen 9,7272 / 3,2059 / 1,3832 N), +0,9 / 3,8 / 9,1 % (19 Hz: 35,4435 / 12,0178 / 5,4457 gegen 35,1153 / 11,5732 / 4,9932 N) | A4 | `python3 code/linear_solver.py --section --K 1e6 --zeta 0.099228` und `python3 code/linear_solver.py --section --rigid` (Kopfzeile), ebenso mit `--f 19`; `python3 -c "print([round(100*(a/b-1),1) for a,b in ((9.7522,9.7272),(3.2391,3.2059),(1.4158,1.3832),(35.4435,35.1153),(12.0178,11.5732),(5.4457,4.9932))])"` |
| \|H(kω)\| = 1,024 / 1,101 / 1,259 für k = 3, 6, 9 (K = 10⁶ N/m, ζ fest, 10 Hz); 10 % und 26 % | A4 | `python3 -c "import numpy as np; M=0.65; K=1e6; C=2*0.099228*(K*M)**0.5; print([round(abs((K+1j*w*C)/(K-M*w*w+1j*w*C)),3) for w in 2*np.pi*10*np.array([3,6,9])])"` |
| F_min(120°) 5,5620 N (K = 10⁶ N/m, ζ fest, μ = 0,4) gegen 5,6452 N: 0,083 N, 18 % von 0,4693 N | A4 | `python3 code/linear_solver.py --section --K 1e6 --zeta 0.099228 --mu 0.4`; `python3 -c "print(round(5.6452-5.5620,4), round(100*(5.6452-5.5620)/0.4693,1))"` |
| Δ(F_min) = 0,117 N; u_c ≤ 0,0327 N (ν → ∞), 0,0269 N (ν = 19), 0,42 % von M·g | A4, A8 | `python3 -c "from scipy.stats import norm,t; D=0.25*0.4693; print(round(D,4), round(D/norm.ppf(1-0.05/294),4), round(D/t.ppf(1-0.05/294,19),4), round(100*D/t.ppf(1-0.05/294,19)/6.3765,2))"` |
| Maximum bei 106° (5,2096 N; 5,1342 N bei 120°) für μ = 0,4, f_n = 120 Hz, ζ = 0,02; K = 369 518 N/m | A5 | `python3 code/linear_solver.py --section --K 369518 --zeta 0.02 --mu 0.4`; `python3 -c "import math; print(round(0.65*(2*math.pi*120)**2))"` |
| bandbegrenzt k_max = 6: Spitze 120°, 2°-Sekante 0,0339 N/° (f_n = 120 Hz, ζ = 0,02) bzw. 0,0331 N/° (starr); k_max = 6 = ⌊120/(2·10)⌋ | A5 | BL(6; `369518,L.c_for(369518,0.02),0.4`) bzw. BL(6; `None,0,0.4`), letzte Zeile |
| Spitze bei 120° für K = 3·10⁴, 10⁵, 10⁶, 10⁷ N/m (ζ fest) und starr | A5 | `python3 code/linear_solver.py --section --K 3e4 --zeta 0.099228` (ebenso `1e5`, `1e6`, `1e7`); `python3 code/linear_solver.py --section --rigid`; letzte Zeile |
| 3f = f_n/2 (f_n = 60 Hz, K = 92 379 N/m, ζ fest, μ = 1): F_min(120°) 3,4258 N gegen 4,5483 N starr | A5 | `python3 code/linear_solver.py --section --K 92379 --zeta 0.099228`; `python3 code/linear_solver.py --section --rigid`; `python3 -c "import math; print(round(0.65*(2*math.pi*60)**2))"` |
| \|H\| ≤ 1,33 und d ln\|H\|/d ln f ≤ 0,67 bei k·f/f_m = 0,5, ζ → 0; numerisch für r ≤ 0,5 und jedes ζ ≤ 2 (Maxima 1,3333 und 0,6667) | §5.3; A6, Tab. F | `python3 -c "r=0.5; print(round(1/(1-r*r),3), round(2*r*r/(1-r*r),3))"`; `python3 -c "import numpy as np; r=np.linspace(1e-4,0.5,5001); z=np.linspace(0,2,2001)[:,None]; lh=lambda r:0.5*np.log((1+4*z*z*r*r)/((1-r*r)**2+4*z*z*r*r)); h=1e-6; d=(lh(r+h)-lh(r-h))/(2*h)*r; print(round(float(np.exp(lh(r)).max()),4), round(float(d.max()),4))"` |
| bandbegrenzt, starr, μ = 0,4: k_max = 9: 2°-Sekante 0,0343 N/°, F_min 5,6781 N (120°) und 5,1608 N (100°), ΔF_Zelt 0,5173 N, γ₁(120°) −0,4305; k_max = 6: γ₁ −0,3775; k_max = 3, 4, 5: γ₁ 0 | A6 | BL(9; `None,0,0.4`), BL(6; …), BL(5; …), BL(4; …), BL(3; …): Zeilen 100°, 120° und letzte Zeile |
| Abtastrate f_s ≥ 6,3 kHz bei k_max = 9, f = 10 Hz; f_clk ≥ 360 kHz für 0,01° bei 10 Hz | A6, A9.1 | `python3 -c "import math; print(round(math.pi*9*10/(2e-3)**0.5), 360*10/0.01)"` |
| Pilotkonfigurationen: zyklische Abstände 110/140/110, 130/100/130, 110/142/108 (nicht äquivalent, paarweise verschieden); Beispiele 110/120/130 und 120/130/110 (äquivalent) | §5.4; A7 | `python3 -c "g=lambda a,b:(lambda s:[s[1]-s[0],s[2]-s[1],360-s[2]])(sorted([0,a,b]));c=lambda x:min(tuple(x[i:]+x[:i]) for i in range(3));S={c(g(*q)) for p in range(100,141,2) for q in ((p,240),(240,p))};[print((a,b),g(a,b),c(g(a,b)) in S) for a,b in ((110,250),(130,230),(110,252),(110,230),(120,250))];print(len({c(g(a,b)) for a,b in ((110,250),(130,230),(110,252))}))"` |
| Pilotkonfigurationen im Modell: Referenz F_min 1,6016 / 1,8699 / 1,3164 N (Kontaktast); starr, μ = 0,4: 5,1742 / 5,3253 / 5,1472 N; Beispiele: 3,4139 N wie (130°, 240°) | A7 | `python3 code/linear_solver.py --point 110 250` (ebenso `130 230`, `110 252`, `110 230`, `120 250`), jeweils auch mit `--rigid --mu 0.4`; `python3 code/linear_solver.py --section` (Zeile 130°) |
| 81,1 / 83,5 / 80,7 % von M·g | A7 | `python3 -c "print(round(100*5.1742/6.3765,1), round(100*5.3253/6.3765,1), round(100*5.1472/6.3765,1))"` |
| kritische Werte 3,583 / 5,586 / 4,356 / 4,060 (H1), 2,991 / 4,075 / 3,435 / 3,269 (H3), 2,852 / 3,780 / 3,236 / 3,094 (H4); 1,645 | §3, §8.5; A8 | `python3 -c "from scipy.stats import norm,t; [print(m,s,round(norm.ppf(1-0.05/(s*m)),3),[round(float(t.ppf(1-0.05/(s*m),v)),3) for v in (9,19,29)]) for m,s in ((147,2),(18,2),(23,1))]; print(round(norm.ppf(0.95),3))"` |
| Zählungen: 147 = 21·7, 18 = 3·3·2, 23 = 21 + 2, 42 = 2·21; 565 = (23 + 5)·20 + 5·1 Läufe, davon 460 Kombinations-, 63 Einzelmodul- und 42 Referenzläufe, 523 mit G1, 21 Kontrollsätze; 15 = 5 + 10 je Messtag; familienübergreifend 0,10 und 0,20 | §3, §5.3, §8.4, §9.2; A8, A9.12 | `python3 -c "print(21*(1+2*3), 3*3*2, 21+2, 2*21, (23+5)*20+5*1, 20*23, 3*(1+20), (1+20)+20+1, (23+5)*20+5-((1+20)+20+1), 1+20, 5+10, 2*0.05, 4*0.05)"` |
| 1,371·Δ (reine Power-Bedingung, ν → ∞) | A8 | `python3 -c "from scipy.stats import norm; c=norm.ppf(1-0.05/294); print(round(2*c/(c+norm.ppf(0.95)),3))"` |
| Aufnahmeschwelle für V: 4,881 (n_min = 20), 4,497 (ν → ∞); Bestätigung an der Schwelle etwa 93 % je Punkt (0,932), 95 % für ν → ∞, 23 unabhängige Punkte etwa 0,20 | A8, Tab. F | `python3 -c "from scipy.stats import norm,t,nct; c=t.ppf(1-0.05/23,19); c0=norm.ppf(1-0.05/23); p=nct.sf(c,19,c+1.645); print(round(c+1.645,3), round(c0+1.645,3), round(p,3), round(norm.sf(-1.645),3), round(p**23,2))"` |
| Standardfehler 0,0069 (0,0138 für zwei); Schwelle 0,064 | §8.4; A8, Tab. F | `python3 -c "print(round((0.05*0.95/1000)**0.5,4), round(2*(0.05*0.95/1000)**0.5,4), round(0.05+2*(0.05*0.95/1000)**0.5,3))"` |
| G1 0,61 % bis 1,5 % je Lauf; S1 über G1 2,5·10⁻⁴ je Lauf; Nullpunktalarm 7,3·10⁻⁴ je Referenzlauf und Kanal; Kampagne ≈ 0,25 (523 G1-Läufe, 42·4 Referenzkanäle); je weiterer Messtag ≈ 0,0066 | §9.2; A8 | `python3 -c "import numpy as np; from scipy.stats import norm; g=np.random.default_rng(1); R=g.standard_normal((400000,42)); s=(R[:,1:-1]-(R[:,:-2]+R[:,2:])/2).std(1,ddof=1); q=lambda v: 2*norm.sf(3*s/v**0.5); p1=(q(2)*q(1.5)).mean(); x,y,z=g.standard_normal((3,s.size)); t=3*(4/3)**0.5*s; p2=((abs(x-z)>t)&(abs(y-z)>t)).mean(); print(float('%.2g'%q(1.5).mean()), float('%.2g'%q(2).mean()), float('%.2g'%p1), float('%.2g'%p2), round(523*p1+168*p2,2), round(3*p1+8*p2,4))"` |
| S3: c_S = 3,503 (n₀ⱼ = 20); höchstens 5 % je Kontrollsatz (exakt 0,05); Bestätigung höchstens 9,5·10⁻⁴; 21 Kontrollsätze höchstens 0,020 | §9.2; A8 | `python3 -c "import numpy as np; from scipy.stats import t; g=np.random.default_rng(2); n=2000000; c=t.ppf(1-0.05/42,19); Z=g.standard_normal((n,20)); m=Z.mean(1); u=Z.std(1,ddof=1)*(1+1/20)**0.5; x,y=g.standard_normal((2,n)); a=abs(x-m)>c*u; b=abs(y-m)>c*u; print(round(c,3), round(42*t.sf(c,19),4), round(21*a.mean(),4), float('%.2g'%(21*(a&b).mean())), round(21*21*(a&b).mean(),3))"` |
| Varianzverhältnis 4/3 (2σ² gegen 1,5σ²) | §8.8; A9.8 | `python3 -c "print(2/(1+0.25+0.25))"` |
| e⁻¹⁰ ≈ 4,5·10⁻⁵; 57 gepoolte Freiheitsgrade; MAD-Faktor 1,4826 | Tab. F | `python3 -c "import math; from scipy.stats import norm; print(round(math.exp(-10),7), 3*(20-1), round(1/norm.ppf(0.75),4))"` |
| Aufwärmen: ohne Drift nach zehn Referenzläufen etwa 6·10⁻⁴ ohne zwei aufeinanderfolgende mit Differenz < σ̂_ref (σ̂_ref = √1,5·σ) | A8, Tab. F | `python3 -c "import numpy as np; g=np.random.default_rng(3); R=g.standard_normal((10**6,10)); print(float('%.1g'%(1-(abs(np.diff(R,axis=1))<1.5**0.5).any(1).mean())))"` |
| Normierung für ε_ctrl: Var(Δ⟨N⟩) = σ²(1 + β² + (1 − β)²), 1,5σ² bei β = 0,5 | §8.8; A1, A9.8 | `python3 -c "b=0.5; print(1+b*b+(1-b)**2)"` |
| Zitate: 10 kg und „11 Kanäle“ bei neun aufgezählten (drei Zellen, Weg, drei Encoder, Beschleunigung, Temperatur; Exposé); 50,6 N, 7,69 mm, 0,650 kg, 16 N·s/m (README); 2,2 Hz (zehn_fragen); 0,2–0,5 % (v1); Ausgabe 2019 (DKD-R 3-10 Blatt 2; PTB-OAR, Websuche, kein Befehl) | §12; A0, A3, A4 | `grep -n -e "10 kg" -e "11 Kanäle" docs/expose_2026-09.md`; `grep -n -A1 "11 Kanäle:" docs/expose_2026-09.md`; `grep -n -e "50,6 N" -e "7,69 mm" -e "0,650 kg" -e "16 N·s/m" README.md`; `grep -n "2,2 Hz" docs/zehn_fragen.md`; `grep -n "0,2–0,5" docs/praeregistrierung_2026-06.md` |
