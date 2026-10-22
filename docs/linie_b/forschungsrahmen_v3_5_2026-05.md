# Phasenkontrollierte Mehrmassensysteme

### Wellenform-gesteuerte, medium-gekoppelte Fortbewegung aus interner Massendynamik — messzentrierter Rahmen mit dokumentierter Falsifikation der Leerraum-Hypothese

**Matthias Früh** · Unabhängiger Forscher · Gravidon Systemics Research
ORCID: 0009-0005-9984-4207
Mai 2026 · Version 3.5

> **Vermerk (22.10.2026).** Originaldatei `PCMMS_Forschungsrahmen_v3_5_Frueh_2026.md`, Stand Mai 2026, Version 3.5;
> hier unverändert bis auf diesen Vermerk. Linie B, Arbeitspaket AP-28 (Stufe S5, Status „später“,
> [`../arbeitsplan_status.md`](../arbeitsplan_status.md)); nach [`../einordnung.md`](../einordnung.md)
> korrekturbedürftig, Nachfolger v3.6 vorgesehen; Abgleichpunkte sowie Streich- und Ersatzliste im
> [Literaturabgleich](../literaturabgleich_2026-09-12.md), §2 und §3. Keine Messdaten. Seit Mai 2026 überholt oder
> eingeschränkt:
> - **Einordnung:** „Fortbewegung“ im Titel betrifft Linie B, nicht Linie A. Primär ist Linie A, die Wellenform der
>   Kontaktkraft eines ruhenden Körpers ohne Effektanspruch ([`../../README.md`](../../README.md), „Zwei
>   Forschungslinien“); v3.5 entstand vor dieser Umstellung ([`../overview.md`](../overview.md)). Der Literaturabgleich
>   (§2.2) schlägt vor, die Wellenformgrößen (§6) als Gegenstand von Linie A festzuschreiben. Die Rückzugsliste der
>   README („Worum es geht“), darunter die gerichtete Netto-Impulsübertragung ohne äußeren Partner, gilt unverändert;
>   der Rahmen nennt das Medium als äußeren Reaktionspartner (§1–§3).
> - **Effektzahlen (§9, §9.2, §17):** „10⁻⁷ bis 10⁻⁴ N“ und die Auslenkung von rund 35 nm beruhen auf der
>   Driftwiderstandskraft (v1 „F_eff“); für Konfiguration D maßgeblich ist F̄_A, im Fall S (hier M1) 6,67·10⁻⁶ N und
>   680 nm ([`skriptkorrekturen_2026-09-06.md`](skriptkorrekturen_2026-09-06.md) §4, §5 Nr. 1;
>   [`../../rechnungen/linie_b/PROTOKOLL.md`](../../rechnungen/linie_b/PROTOKOLL.md) LB-08). Beide Zahlenreihen gelten
>   nur im Zweiterm-Ansatz. Der 80/20-Nullbefund gilt für das reduzierte Skript, nicht als allgemeiner Satz
>   (Literaturabgleich §2.3).
> - **Kraftmodell und Dichte:** Die Fälle des Begleitskripts liegen bei KC ≪ 1 (Fall S 0,063, Fall R 0,25; LB-01), die
>   Effektspanne ist dort nicht abgesichert (LB-08). Für einen glatten Träger ist das quasistationäre
>   Widerstandsgesetz bei KC ≪ 1 nicht gültig, die Kraft in führender Ordnung linear mit Periodenmittel null; scharfe
>   Kanten sind offen (LB-02, für den Träger des Driftskripts). C_medium ∝ ρ (§5, §10, §11) ist nicht begründet
>   (PROTOKOLL, Abschnitt 3); dichteunabhängig ist die stationäre freie Drift nur im rein quadratischen Modell (LB-06).
> - **Begleitskript und Parameter:** `pcmms_medienkopplung_modell.py` liegt als v1 (§9.1, §9.2 nur in `-1.py`) in
>   [`quelle_v1/`](../../rechnungen/linie_b/review_2026-09-06/quelle_v1/), korrigiert als v2 in
>   [`quelle_kopie/`](../../rechnungen/linie_b/quelle_kopie/). T_f/T ≈ 0,8 (Gl. 4) ist ein Vorwärtsanteil, eine andere
>   Profilfestlegung als der Halteanteil 0,65 des Simulationssatzes; offen ist nur, den Rahmen nachzuziehen (Nr. 9 und
>   23 der [Offenen Punkte](../arbeitspapier/PCMMS_Arbeitspapier_Offene_Punkte.md)).
> - **Zenodo (§15):** Frühere Zenodo-Stände (April–Mai 2026) dokumentieren den Weg, nicht den aktuellen Stand
>   ([`../../README.md`](../../README.md), „Zitieren“).
>
> Lizenz wie der Ordner: CC BY 4.0 ([`../../LICENSE-CC-BY-4.0`](../../LICENSE-CC-BY-4.0)).

---

## Zusammenfassung

Dieses Dokument formuliert eine **positive, falsifizierbare und erhaltungssatz-konforme** Forschungsfrage: Kann ein System ausschließlich durch interne, phasenkontrollierte Massenbewegung — ohne Flügel, Propeller oder ausgestoßene Masse — eine reproduzierbare, gerichtete **Nettobewegung** erzeugen, indem es das umgebende **Medium (Luft) als expliziten Reaktionspartner** nutzt?

Die Antwort ist durch zwei Grenzfälle gerahmt. Im **Vakuum** ist eine Nettoverschiebung des Schwerpunkts durch beschränkte interne Bewegung physikalisch ausgeschlossen (Schwerpunktsatz); die entsprechende frühere „Leerraum-Hypothese" ist damit **durch den Schwerpunktsatz ausgeschlossen (theoretische Falsifikation, Abschnitt 8)** — kein experimentelles Null-Ergebnis. Im **Medium** ist gerichtete Bewegung dagegen erlaubt und alltäglich — der an die Luft übertragene Impuls schließt die Bilanz. Der Rahmen behauptet **keinen** reaktionslosen Antrieb, keine Gewichtsreduktion und keine Antigravitation.

Methodisch zentral ist die Erkenntnis, dass der Residualterm `C(x,t)` der Messgleichung **nicht reines Artefakt** ist: sein medienkopplungsbedingter Anteil ist das eigentliche **Signal** der Fortbewegung. Der entwickelte Mess- und Auswertebaukasten dient daher zwei dualen Zwecken — Artefakte *abziehen* (Messpräzision) bzw. die Medienkopplung *charakterisieren und ausnutzen* (Fortbewegung). Beide Anwendungen sind domänenübergreifend nutzbar (Vibrationstechnik, drag-basierte Mikroaktorik, adaptive Lager, Structural Health Monitoring).

*Alle Arbeiten auf Zenodo — DOI-Verzeichnis siehe Abschnitt 15.*

---

## 1. Forschungsziel und positive Hypothese

**Ziel:** Maximale gerichtete Nettobewegung unter strengen Randbedingungen — *Handicaps*:
- keine Flügel, Propeller, Düsen oder ausgestoßene Reaktionsmasse,
- ausschließlich interne, phasenkontrollierte Bewegung von `N` Massen innerhalb eines gemeinsamen Rahmens,
- als Reaktionspartner ausdrücklich zugelassen: das **umgebende Medium** (Luft), dessen Trägheits- und Widerstandsreaktion bewusst ausgenutzt wird.

**Positive Hypothese (H1).** Phasenkontrollierte interne Massenbewegung erzeugt über den quadratischen Luftwiderstand eine **gleichgerichtete** Netto-Impulsübertragung an das Medium und damit eine messbare Nettobewegung des Systems — bilanziell geschlossen, ohne Verletzung von Impuls- oder Schwerpunktsatz. Der Mechanismus ist explizit modelliert (Abschnitt 9): Drift entsteht **nicht** durch bloße zeitliche Asymmetrie, sondern nur, wenn die Geschwindigkeit der Hülle eine **von null verschiedene Schiefe** besitzt (oder der Widerstand richtungsabhängig ist). Damit ist die Wellenform-Schiefe (Abschnitt 6) zugleich der physikalische Stellhebel des Effekts.

Diese Hypothese ist **erhaltungskonform** (der Impuls geht an die Luft), **falsifizierbar** (Abschnitt 10) und besitzt einen klaren Anwendungskontext (widerstandsgetriebene Fortbewegung — ein etabliertes Feld, hier mit phasenkontrollierter Mehrmassen-Aktuierung).

## 2. Abgrenzung

- **Kein reaktionsloser Antrieb.** Der Reaktionspartner ist explizit das Medium; ohne Medium keine Bewegung (siehe Null-Ergebnis, Abschnitt 8). Genau diese Mediumsabhängigkeit unterscheidet H1 von reaktionslosen Behauptungen.
- **Keine Gewichtsreduktion, keine Antigravitation.** Das Zeitmittel der Kontaktnormalkraft auf einer Unterlage bleibt durch `mean(F_N) = M·g` festgelegt (Abschnitt 3).
- **Abgrenzung zu EM-Drive / Woodward:** deren Kernproblem ist die fehlende Trennung kleiner Signale von thermischen/messtechnischen Artefakten (vgl. Tajmar et al., 2018). H1 macht das Medium zum *kontrollierten, variierbaren* Reaktionspartner und erlaubt damit gerade die saubere Trennung (Abschnitt 11).

## 3. Erhaltungssatz als Randbedingung — die zwei Grenzfälle

Für beschränkte periodische Innenbewegung mittelt sich der dynamische Term über die Periode zu null:
```
⟨ Σ_k m_k z̈_k ⟩ = 0
```

**Grenzfall Vakuum (geschlossenes System):** Der Schwerpunkt kann sich nicht netto verschieben. Eine gerichtete Nettobewegung durch interne Bewegung allein ist ausgeschlossen. → Null-Ergebnis erwartet und bestätigt (Abschnitt 8).

**Grenzfall Medium (offenes System):** Das System tauscht Impuls mit der umgebenden Luft. Die Bilanz lautet
```
Δp_System = − Δp_Medium ,
```
d.h. eine Vorwärtsbewegung des Systems ist exakt durch den rückwärts an die Luft übertragenen Impuls gedeckt. Nettobewegung ist erlaubt — sie ist möglich, **weil** der an die Luft übertragene Impuls letztlich von den Raumwänden aufgenommen wird; die Gesamtimpulsbilanz System + Luft + Wände bleibt geschlossen. Auf einer Unterlage gemessen bleibt zugleich `⟨F_N⟩ = mg + ⟨C⟩`; die Mediumsreaktion erscheint im Residualterm `C` (Abschnitt 5).

Diese Randbedingung ist nicht verhandelbar. Sie trennt sauber das physikalisch Verbotene (Leerraum-Netto-Effekt) vom physikalisch Erlaubten (medium-gekoppelte Bewegung).

## 4. Systemdefinition und messzentrische Formulierung

`N` Einzelmassen, koordiniert bewegt über zwei getrennte Steuerebenen: **Phasenkontrolle** (*wann* relativ zueinander) und **Hüllkurven-/Egg-Modulation** (*wie* die Trajektorie geformt ist).

Gemessene Normalkraft am Interface (Konfiguration A, auf Unterlage):
```
F_N(t) = mg + Σ_{k=1}^N m_k z̈_k(t) + C(x,t)        (1)
```
Anregung:
```
u_k(t) = A_k · p_k(t − φ_k),    u_sys(t) = Σ_k A_k · p_k(t − φ_k)     (2,3)
```
Zeitliche Asymmetrie (Vorwärts-/Rückholphase) als zentrales Gestaltungsmerkmal:
```
T = T_f + T_r,   T_f/T ≈ 0.8,   T_r/T ≈ 0.2          (4)
z̈_k(t) = z̈_k,∥(t) + z̈_k,⊥(t)                       (5)
```
Die Asymmetrie formt die **Wellenform** der Kraft und — im Medium — die **Asymmetrie der Medienreaktion**. Sie verändert nicht das Zeitmittel der Innendynamik (`∫z̈ dt = 0`/Periode).

**Zwei Messkonfigurationen:**
- **Konfiguration A — gebunden (auf Kraftsensor):** Reaktionspartner = Unterlage. `⟨F_N⟩` durch Schwerpunktsatz fixiert; messbar ist die *Wellenform* und die Medienreaktion im Residuum. Dient der Pipeline-Validierung und der C-Charakterisierung.
- **Konfiguration B/C — frei bzw. reibungsarm rollend:** Reaktionspartner = Luft. **Achtung:** reibungslimitiert — der erwartete Schub (Abschnitt 9: 10⁻⁷–10⁻⁴ N) liegt *unter* typischer Roll-/Gleitreibung (~10⁻² N) und sogar unter Luftlager-Reibung (~10⁻⁴ N). Freie Drift setzt sich für diese Schubwerte **nicht** in Bewegung. Nur als Negativ-/Kontrollkonfiguration sinnvoll.
- **Konfiguration D — Schub-Pendel / Torsionswaage (primäre Messkonfiguration):** Das System hängt an einer reibungsfreien Aufhängung. Der stetige, gleichgerichtete Schub deflektiert die Aufhängung statisch (`x = F_eff·L/(M·g)`); keine Haftreibungsschwelle. Dies ist die etablierte Methode für µN–nN-Schub (vgl. Schubwaagen bei EM-Drive-Tests, Tajmar 2018) und die einzige für die erwartete Effektgröße taugliche Konfiguration (Abschnitt 9).

**Wichtige Einschränkung (A↔B/D):** Die Medienreaktion hängt von der Relativgeschwindigkeit System↔Luft ab, die in A (fixiert, v≈0) und B/D (frei schwingend) verschieden ist. Dass die in A gemessene Kraft-Schiefe den Vortrieb in B/D treibt, ist eine **nicht-triviale, noch zu validierende Annahme** und nur ein qualitatives Indiz, kein quantitativer Prädiktor (siehe §6, §17). Konfiguration D liefert die eigentliche Effektmessung.

## 5. C(x,t): vom Artefakt zum Signal (Dualität)

Der Residualterm aggregiert Strukturkopplung, Dissipation, Sensorartefakte, Umgebungseinflüsse **und die Reaktion des umgebenden Mediums**. Entscheidend:

> Für das Messpräzisions-Ziel ist `C` Störung und wird abgezogen.
> Für das Fortbewegungs-Ziel ist der **medienkopplungsbedingte Anteil von `C` das Signal**.

`C` ist daher zu zerlegen, nicht nur zu konstatieren:
```
C(x,t) = C_medium(x,t)  +  C_artefakt(x,t)
```
- `C_medium` — reproduzierbare, mediumsdichte-abhängige Reaktion (das gesuchte Signal),
- `C_artefakt` — Sensordrift, Strukturkopplung an die Halterung, EMV, Filterbias (zu eliminieren).

Die Trennung erfolgt **nicht per Definition, sondern per Evidenz** durch unabhängige Kontrollen (Abschnitt 11), insbesondere die **Variation der Mediumsdichte** (Luft ↔ Teilvakuum): `C_medium` skaliert mit der Dichte, `C_artefakt` nicht. Damit ist die im früheren Rahmen zirkuläre Aussage „jede Verschiebung ist Artefakt" durch ein **messbares Unterscheidungskriterium** ersetzt.

## 6. Observablen

**Wellenform-Statistik** der Kontaktkraft (Konfiguration A) als Steuer- und Charakterisierungsgrößen:
- Schiefe `E[(F−µ)³]/σ³` — Asymmetrie des Kraftverlaufs,
- Liftoff-Anteil — Zeitbruchteil mit `F_N ≈ 0`,
- Peak-to-Mean `max(F_N)/⟨F_N⟩`.

Diese Größen sind die **Stellhebel** der Medienkopplung. **Einschränkung (quantitativ vs. qualitativ):** Die in Konfiguration A (fixiert, v≈0) gemessene *Kraft*-Schiefe ist nicht identisch mit der *Geschwindigkeits*-Schiefe der freien Hülle (die DGL in §9 koppelt beide nichtlinear). Die Kraft-Schiefe in A dient als **qualitatives Indiz**, dass die innere Bewegung ausreichende zeitliche Asymmetrie aufweist; eine **quantitative** Vorhersage der Drift erfordert die Lösung der vollen Dynamik (§9) inkl. Reibung. Die quantitative Beziehung zwischen Kraft-Schiefe (A) und Schub (D) wird daher **experimentell bestimmt** (empirische Korrelation, keine theoretische Vorhersage — wegen der nichtlinearen Dynamik und unbekannten Reibung): Konfiguration D liefert die Kalibrierung.

**Fortbewegungs-/Schub-Observable** (Konfiguration D): statische Auslenkung `x` der Schub-Pendel-/Torsionsaufhängung, woraus der gleichgerichtete Schub `F_eff = x·M·g/L` folgt. Dies ist die **primäre Observable für den H1-Nachweis** (nicht die Kontaktkraft in A, die nur den Stellhebel charakterisiert).

Die zustandsabhängige Mittelwertdifferenz `ΔF̄` wird **nur als Null-Test-Größe** geführt (erwartungsgemäß ≈ 0 in Konfiguration A; jede Abweichung primär `⟨C⟩`).

## 7. Wellenform- und Fortbewegungs-Detektionsschwellen

Ergänzend zur Mittelkraft-Sensitivität (`ΔF ∼ 10⁻³ N`, `ΔF/F_0 ∼ 5–15 ppm`) werden **formspezifische** Schwellen definiert:
- Schiefe: minimale auflösbare Änderung `Δγ_min`, abgeleitet aus der Block-Statistik der Kraftzeitreihe (`Δγ_min ≈ k · σ_γ`, `σ_γ` aus Bootstrap über Blöcke).
- Liftoff-Anteil: minimale auflösbare Fraktionsänderung, gekoppelt an Sensor-Nulldurchgangs-Auflösung.
- Fortbewegung: minimale detektierbare Nettoverschiebung aus Positions-/Tracking-Auflösung (z.B. Video-Höhentracker) und Mittelung über Zyklen.

Ohne diese Schwellen wäre die Wellenform-Analyse nicht falsifizierbar; sie sind daher Pflichtbestandteil jeder Kampagne.

**Standardverfahren (GUM-konform, ISO/IEC Guide 98-3).** Die Schwellen werden vor jeder Kampagne aus den Gerätedaten berechnet; das Verfahren ist fixiert:
1. Zeitreihe in `K` nicht-überlappende Blöcke (Blocklänge `T_b ≥ 10×` Korrelationszeit) segmentieren.
2. Zielgröße (z.B. Schiefe `γ`) je Block berechnen → Stichprobe `{γ_k}`.
3. `σ_γ` per Bootstrap (≥ 1000 Resamples) schätzen; `Δγ_min = k · σ_γ`, `k = 2` (95 %).

**Rechenbeispiel (illustrativ):** `K = 50` Blöcke, daraus `σ_γ ≈ 0.04` → `Δγ_min ≈ 0.08`. Eine Schiefeänderung unter 0.08 gilt dann als nicht auflösbar. (Konkrete Zahlen pro Aufbau einsetzen — `K`, `T_b`, `σ_γ` aus den realen Daten.) Analog für Liftoff-Anteil (Fraktion, gekoppelt an die Nulldurchgangs-Auflösung des Sensors) und Nettoverschiebung (Tracking-Auflösung × Mittelung über Zyklen).

## 8. Status der Leerraum-Hypothese: a-priori-Ausschluss + Pipeline-Validierung

**Historische Hypothese (H0_alt, zurückgezogen):** Frühere Versionen dieses Rahmens vermuteten einen gerichteten Netto-Effekt aus interner Bewegung *im nahezu leeren Raum*.

**Status — präzise getrennt nach Evidenzart:**

1. **A-priori-Ausschluss (theoretisch, beleglos weil Theorem):** H0_alt ist durch den Schwerpunktsatz ausgeschlossen — für ein geschlossenes System mit beschränkter Innenbewegung kann der Schwerpunkt sich im Vakuum nicht netto verschieben (Abschnitt 3). Dies ist die stärkste Aussage und braucht keinen Datensatz.

2. **Pipeline-Validierung (in Vorbereitung):** Die Simulationspipeline **wird erwartungsgemäß** diesen Ausschluss reproduzieren — als korrekt implementierte Newton'sche Integration *muss* sie den Schwerpunktsatz erfüllen; das wäre keine eigenständige „Bestätigung", sondern eine **Validierung der Auswerteverfahren gegen einen bekannten Referenzfall** (Erkenntniswert allein: keine Falsch-Positiven bei ppm-Niveau). Diese Validierung ist **in Vorbereitung** (begleitende Arbeiten *„Simulation-Based Evaluation…"*, *„Null-Ergebnis Einzelmasse…"*; DOIs siehe §15). Der A-priori-Ausschluss (1) steht unabhängig davon. Das beiliegende Skript `pcmms_medienkopplung_modell.py` deckt die Dynamik aus §9 ab, nicht die ppm-Mittelkraft-Simulationen.

3. **Experimentelle Falsifikation (steht aus):** Eine dedizierte *physikalische* Falsifikation von H0_alt liegt **noch nicht** vor; sie ist nicht erforderlich, da (1) den Ausschluss bereits liefert, wird aber als Vollständigkeit im Ausblick geführt.

Es wird also **kein** unbelegter experimenteller Befund behauptet: der Ausschluss ist theoretisch, die Pipeline numerisch validiert, das Experiment offen.

Empirische Teilbefunde der Simulationen:
1. Keine Verschiebung unter balancierter Anregung.
2. Strukturelle Asymmetrie allein → keine Verschiebung.
3. RMS ≠ Mittelwert (große Dynamik ⇏ DC-Verschiebung).
4. Biasierte Anregung (z.B. 65/35) → Verschiebung, aber inputinduziert (`ū≠0`), nicht systemisch.
5. Modell-Mismatch → systematische Residualverzerrung `R_korr ≈ F_real − F_modell ≠ 0`.

Die Pivot-Logik: Was im Vakuum verboten ist (1–2), wird im Medium über `C_medium` erlaubt — Übergang von H0_alt (ausgeschlossen) zu H1 (offen, Abschnitt 1).

## 9. Mechanismus der Medienkopplung und erwartete Effektgröße

Frühere Versionen ließen offen, *wie* die innere Bewegung an die Luft koppelt. Hier wird der Mechanismus explizit modelliert und numerisch gerechnet (Skript `pcmms_medienkopplung_modell.py`, reproduzierbar).

**Modell (starre, frei bewegliche Hülle, Masse `M`):**
```
M · v'(t) = F_int(t) − ½ · ρ · c_w · A · v(t)|v(t)|
```
mit `F_int(t)` der **mittelwertfreien** (impulserhaltenden) Kraft der inneren Massen auf die Hülle (`⟨F_int⟩ = 0` über die Periode), `ρ` Luftdichte, `c_w` Widerstandsbeiwert, `A` wirksame Fläche. Drag-Vorzeichen über `v|v|` (quadratisch, richtungsrichtig).

**Kernresultat (Notwendige Bedingung für Drift):**
- **Linearer Widerstand** → Drift exakt null (lineares System, mittelwertfreie Anregung → mittelwertfreie Antwort).
- **Quadratischer Widerstand + zweistufige (rein zeitlich asymmetrische) Kraft** → Drift **ebenfalls null**: eine stückweise konstante Kraft erzeugt eine stückweise lineare (Dreieck-)Geschwindigkeit, deren Werteverteilung **gleichverteilt und symmetrisch** ist (`⟨v|v|⟩ = 0`). **Bloße Timing-Asymmetrie genügt nicht.**
- Drift entsteht nur, wenn (M1) die **Geschwindigkeit eine Schiefe ≠ 0** besitzt — erzeugt über Wellenform-Oberwellen — oder (M2) der **Widerstand richtungsabhängig** ist (`c_w,vor ≠ c_w,zurück`, d.h. Körperform-Asymmetrie).

Damit ist die **Schiefe** (Abschnitt 6) nicht nur eine Observable, sondern der **physikalische Treiber** des Effekts.

**Gerechnete Größenordnungen** (`M = 1 kg`, `A = 0.02 m²`, `T = 0.1 s`):

| Fall | Drift `v_drift` | effektiver Schub `F_eff` |
|------|-----------------|--------------------------|
| Zweistufig 80/20 (nur Timing) | ≈ 0 | ≈ 0 (Null-Befund) |
| M1 schiefe v (2-harmonisch, b=3, φ=π/4) | ≈ 5.3 mm/s | ≈ 3.4 × 10⁻⁷ N |
| M2 richtungsabh. Widerstand (1.5/0.5, Fa=10 N) | ≈ 72 mm/s | ≈ 6.3 × 10⁻⁵ N |

**Ehrliche Schlussfolgerung — und Korrektur der Messstrategie:** Der effektive Netto-Schub liegt bei **10⁻⁷ bis 10⁻⁴ N**, also **1–4 Größenordnungen unter** der Kraft-Detektionsschwelle (`ΔF ∼ 10⁻³ N`). In Luft ist **Kraft die falsche Observable** — der µN-Schub liegt unter jeder Wägezelle. Die **Driftgeschwindigkeit (mm/s) bzw. die Nettoverschiebung** ist dagegen per Positions-Tracking (z.B. Video-Höhentracker) gut auflösbar. Daher wird in Konfiguration B/C **die Drift-Kinematik gemessen, nicht die Kontaktkraft**. Die Kontaktkraft-Wellenform (Konfig. A) dient der Charakterisierung des Stellhebels (Schiefe), nicht dem direkten Effektnachweis.

(Modell ist ein Überschlag für eine starre symmetrische Hülle; M2 setzt Körperform-Asymmetrie voraus.)

**M1 vs. M2 — was PCMMS auszeichnet:** M2 (richtungsabhängiger Widerstand) ist ein **trivialer** Effekt, der mit jeder oszillierenden Bewegung an einer aerodynamisch asymmetrischen Form funktioniert — er streift das „keine Flügel"-Handicap (eine asymmetrische Form ist zwar kein Flügel, aber eine passive aerodynamische Maßnahme) und ist *nicht* das Spezifische an PCMMS. Der **nicht-triviale, eigentliche PCMMS-Fall ist M1**: gerichtete Bewegung an einer symmetrischen Hülle allein durch phasenkontrolliert erzeugte Geschwindigkeits-Schiefe. M1 ist schwächer (~mm/s, ~10⁻⁷ N), aber konzeptionell der Kern.

### 9.1 Konkrete Mehrmassen-Realisierung (Brücke PCMMS → F_int)

Das obige `F_int(t)` ist kein willkürliches Signal, sondern aus zwei phasenkontrollierten Massen ableitbar. Mit `F_int = −(m₁z̈₁ + m₂z̈₂)`, Masse 1 auf der Grundfrequenz, Masse 2 auf der zweiten Harmonischen:
```
z₁ = A₁ sin(ωt),  z₂ = A₂ sin(2ωt + φ)
F_int = m₁A₁ω² sin(ωt) + m₂A₂(2ω)² sin(2ωt+φ)
```
Das ist exakt die zwei-harmonische Kraft des M1-Falls (a, b). Konkret (`m₁=m₂=0.1 kg`, `T=0.1 s`, a=5 N, b=3 N):

| Masse | Frequenz | Amplitude | Beschleunigung | Spitzenkraft |
|-------|----------|-----------|----------------|--------------|
| 1 (Grundton) | 10 Hz | 1.27 cm | 50 m/s² ≈ 5.1 g | 5 N |
| 2 (2. Harmon.) | 20 Hz | 0.19 cm | 30 m/s² ≈ 3.1 g | 3 N |

Realisierbar mit Voice-Coil-Aktuatoren / Linearmotoren (wenige g, cm-Hub). Die **Phase φ steuert die Geschwindigkeits-Schiefe** und damit Vorzeichen/Größe des Drifts. Damit ist die Verbindung „Mehrmassen-Phasenkontrolle → F_int → Drift" konkret, nicht behauptet.

### 9.2 Reibung und Messkonfiguration: Schub-Pendel statt freier Drift

Entscheidend für die Machbarkeit: schlägt der Schub die Reibung? Reibungsboden `F_fric = µ·M·g` (M=1 kg):

| Lagerung | µ | F_fric | M1 (3·10⁻⁷ N) | M2 (6·10⁻⁵ N) |
|----------|-----|--------|----------------|----------------|
| Präzisions-Rollen | 10⁻³ | ~10⁻² N | tot | tot |
| Luftlager | 10⁻⁵ | ~10⁻⁴ N | tot | tot |
| Luftlager (top) | 10⁻⁶ | ~10⁻⁵ N | tot | grenzwertig |

**Freie Drift ist damit die falsche Konfiguration** — der Schub liegt 1–4 Größenordnungen unter der Reibung; das System setzt sich nicht in Bewegung. Lösung: **reibungsfreie Aufhängung** (Schub-Pendel / Torsionswaage, Konfig. D). Da die Antriebsfrequenz (≥10 Hz) weit über der Pendel-Eigenfrequenz (~0.5 Hz) liegt, schwingt die Hülle am Antrieb effektiv frei → die Drag-Gleichrichtung bleibt erhalten → der **DC-gleichgerichtete Schub deflektiert die Aufhängung quasi-statisch** (keine Haftreibungsschwelle):
```
x = F_eff · L / (M·g)
```

| Schub | Auslenkung bei L=1 m |
|-------|----------------------|
| M2 (6.3·10⁻⁵ N) | 6.4 µm (optisch/interferometrisch leicht) |
| M1 (3.4·10⁻⁷ N) | 35 nm (Interferometrie/Torsionswaage; anspruchsvoll, aber Stand der Technik) |

Torsionswaagen erreichen nN-Schub routinemäßig (eben jene Technik, mit der EM-Drive-Schübe gemessen/widerlegt wurden, Tajmar 2018). M2 ist damit klar messbar, M1 grenzwertig-aber-erreichbar. **Die experimentelle Strategie ist Schubwaage, nicht Fahrschlitten.**

**Messpraktische Grenzen (Aufhängung):** Die stationäre M1-Auslenkung (35 nm) ist mit kommerziellen Interferometern auflösbar, erfordert aber typischerweise Mittelung über viele Minuten und aktive Schwingungsisolierung (Luftfedertisch). Die Relaxationszeit des luftgedämpften Pendels ist vorab zu bestimmen, damit im eingeschwungenen Zustand gemessen wird (sonst alternativ Frequenzgang-/Lock-in-Auswertung). Das thermische (Brownsche) Rauschen ist bei steifer Aufhängung unkritisch (für `M=1 kg`, `k≈Mg/L≈10 N/m`: RMS-Auslenkung `√(k_BT/k) ≈ 2·10⁻¹¹ m`, weit unter 35 nm), wächst aber bei weicherer Aufhängung — Steifigkeit also gegen Auslesegewinn abwägen.

## 10. Falsifikationskriterium (messgeräte-gekoppelt)

Ersetzt die frühere, nicht erfüllbare Schwelle `10⁻¹⁵`. Zweistufig:

**Simulationsebene (numerische Auflösung):** Effekte bis zur numerischen Rauschgrenze des Integrators prüfbar; dient nur der Modell-Konsistenz, nicht als physikalischer Nachweis.

**Experimentebene (physikalische Falsifikation):** Da der erwartete Schub (10⁻⁷–10⁻⁴ N) *unter* der Kraftschwelle (~10⁻³ N) liegt, ist eine direkte Kraftmessung **nicht** geeignet. Die Falsifikation von H1 erfolgt **ausschließlich** über die in Konfiguration D gemessene **statische Auslenkung** der Schub-Pendel-/Torsionsaufhängung (bzw. den daraus folgenden Schub `F_eff = x·M·g/L`). Die Kraft-/Wellenformmessung in Konfiguration A dient nur der Charakterisierung des Stellhebels (Schiefe) und ist für den Effektnachweis ungeeignet.

H1 gilt für einen Parameterbereich `p*` als **falsifiziert**, wenn der aus der Auslenkung abgeleitete Schub **innerhalb der kombinierten Standardmessunsicherheit `u_c` der Schubwaage** bleibt:
```
|F_eff(p*)| ≤ k · u_c        (k = 2, ~95 %)
```
mit `u_c` aus Auslesepräzision (Interferometer/optisches Tracking), Aufhängungs-Drift und Wiederholpräzision (GUM-konform). Begleitend die Mediumsdichte-Kontrolle (Abschnitt 11): echter `C_medium`-Schub skaliert mit der Dichte und verschwindet im Teilvakuum.

**Präzisierung (notwendig vs. hinreichend, ohne Zirkularität):** Dass `C_medium` bei Reduktion der Mediumsdichte verschwindet, ist eine *notwendige*, aber **keine hinreichende** Bedingung — ein Artefakt könnte ebenfalls mit der Dichte skalieren (z.B. thermisch über veränderte Luftkühlung; daher die Vakuum-zu-Vakuum-Kontrolle, Abschnitt 11.3). Um nicht das zu testende Modell zur Definition der Schwelle zu benutzen, wird ein **fester Dichteschwellwert** vorgegeben: `ρ < 10⁻² · ρ₀` (Teilvakuum). Zusätzlich gilt eine vom Modell *unabhängige*, konservative Schranke: der unter den gegebenen Anregungsbedingungen *maximal plausible* Effekt (obere Abschätzung aus Anregungsenergie, nicht aus H1) muss bei dieser Dichte kleiner als `u_c` sein. Bleibt das gemessene Signal dann innerhalb `u_c` um null, ist H1 für `p*` falsifiziert.

Lokales Kriterium (pro `p*`); globale Aussage erst nach systematischem Parameter-Scanning.

## 11. Kontrollexperimente zur C-Charakterisierung

Zur evidenzbasierten Zerlegung `C = C_medium + C_artefakt`:
1. **Leermessung** (`u_k=0`, Langzeit) → Drift- und Rauschboden, `C_artefakt`-Basis.
2. **Mediumsdichte-Variation** (Luft ↔ Teilvakuum / verschiedene Drücke) → isoliert `C_medium` (skaliert mit Dichte) von `C_artefakt` (dichteunabhängig). **Schlüsselkontrolle.**
3. **Vakuum-zu-Vakuum-Kontrolle (gegen dichteabhängige Artefakte):** Wiederholung *ohne* Dichteänderung über die gleiche Zeitdauer und bei stabilisierter Temperatur (überwacht per Thermoelement/PT100 am Aufbau), um zu prüfen, dass `C_artefakt` tatsächlich dichteunabhängig ist (Kontrolle gegen thermische Kopplung über Pumpenlaufzeit, Feuchte, Konvektion). Pflicht-Begleitkontrolle zu (2).
4. **Reaktionspartner-Variation** (Halterungssteifigkeit, Auflagergeometrie) → trennt Strukturkopplung von Medienreaktion.
5. **Orientierungstest** (Rotation/Inversion) → gravitations-/montagebedingter Bias.
6. **Phasen-Randomisierung** → bricht Kohärenz bei gleicher Anregungsenergie (Kontrolle gegen kohärente Artefakte).

## 12. Simulations-Methodik (Reproduzierbarkeit)

Zur Behebung früherer Intransparenz wird je Kampagne dokumentiert:
- **Code:** Eigenentwicklung (Python), öffentlich freigegeben **mit Veröffentlichung der jeweiligen Ergebnisse** (kein „auf Anfrage"). Das dynamische Medienkopplungs-Modell (`pcmms_medienkopplung_modell.py`, Abschnitt 9) liegt dem Dokument bei. Pro publiziertem Ergebnis konkrete Skript-/Commit-Referenz.
- **Modellannahmen:** Dämpfungsmodell, Kontakt-/Mediumsreaktionsmodell, Linearität/Nichtlinearität explizit.
- **Numerik:** Integrator (RK4/adaptiv), Zeitschritt `Δt`, Burn-in, Auswertefenster.
- **Balance-Nachweis:** wie `ū(t)=0` numerisch sichergestellt und verifiziert wird (Integral-Check pro Periode unter Toleranz).
- **Parameterräume:** abgedeckte `N`, Amplituden, Phasenkombinationen, Asymmetriegrade (Sweep-Tabellen als CSV beigelegt).

## 13. Detektion vs. Interpretation

Statistische Signifikanz (`p<α`) zeigt *Vorhandensein* einer Abweichung, nicht ihre Ursache. Detektion = statistisches Problem; Interpretation = Modellierungsproblem. Physikalische Attribution (insb. „ist es `C_medium`?") ist stets nachgelagert und an die Kontrollen aus Abschnitt 11 gebunden.

## 14. Pipeline und Entwicklungsstufen (operationalisiert)

**Sieben Achsen:** (1) Anregung/Modulation, (2) Zeitstruktur/Fenster, (3) Richtungsdekomposition `F∥/F⊥`, (4) Messung/Rekonstruktion, (5) Statistik (`F̄`, `σ²`, t-Test, CI, Wellenform-Statistik), (6) Parameterraum, (7) Entwicklungsstufen.

**Gen-Stufen mit operationalen Kriterien:**

| Stufe | Trennkriterium (operational) |
|-------|------------------------------|
| Gen0 | Aktuierung & Kraftmessung funktionsfähig; Sensor kalibriert; `u_c` bestimmt. |
| Gen1 | Systembewegung reproduzierbar erzeugbar, aber Trajektorienstreuung über Zyklen > X % (unkontrolliert). |
| Gen2 | Trajektorienstreuung ≤ X %; Phasen-/Profilvorgabe wird eingehalten; einzelne Achse stabil. |
| Gen3 | Globale Stabilität: alle Module phasenkohärent über ≥ M Zyklen; Wellenform-Zielgrößen innerhalb Toleranz reproduzierbar. |

**Bestimmung von X und M:** Standardwerte `X = 5 %`, `M = 10⁴ Zyklen`, mit der Option begründeter Anpassung (im Methodenteil dokumentiert). Konkret: `X` = relative Trajektorienstreuung der Gehäuse-Spitzenposition (3σ über die ersten 100 Zyklen, normiert auf die Hubamplitude) — anwendbar in Konfig. B/C/D (frei/aufgehängt), **nicht** in A (fixiert, keine Gehäusebewegung; dort gilt Gen-Reife über Wellenform-Reproduzierbarkeit). `M` = Maximum aus 10⁴ Zyklen und dem konvergenzbasierten Kriterium (kumulierte Wellenform-/Auslenkungs-Statistik innerhalb `u_c` stationär).

## 15. Publikationsverzeichnis

Alle Arbeiten auf Zenodo unter ORCID 0009-0005-9984-4207. Als Belege zu Abschnitt 8 (Pipeline-Validierung), Status **in Vorbereitung** — DOIs vor Veröffentlichung dieses Rahmens inline einsetzen:
- *Simulation-Based Evaluation of Mean Force Signals in Phase-Controlled Multi-Mass Systems* — DOI: [in Vorbereitung].
- *Null-Ergebnis Einzelmasse (PCMMS)* — DOI: [in Vorbereitung].

(Solange die DOIs nicht vergeben sind, wird in §8 kein öffentlich-verfügbarer Beleg behauptet; der A-priori-Ausschluss via Schwerpunktsatz steht unabhängig davon.)

## 16. Symbolverzeichnis

| Symbol | Bedeutung | Einheit |
|--------|-----------|---------|
| `N` | Anzahl Module | – |
| `m_k`, `m`/`M` | Modul- / Gesamtmasse | kg |
| `g` | Erdbeschleunigung | m/s² |
| `F_N(t)`, `F̄_N` | gemessene / gemittelte Normalkraft | N |
| `z̈_k`, `z̈_k,∥`, `z̈_k,⊥` | Beschleunigung gesamt / parallel / lateral | m/s² |
| `u_k`, `u_sys`, `ū` | Anregung Modul / gesamt / mittel (`ū=0`=balanciert) | – |
| `A_k`, `p_k`, `φ_k` | Amplitude, Profil, Phase | –, –, rad |
| `T`, `T_f`, `T_r` | Periode, Vorwärts-, Rückholphase | s |
| `C`, `C_medium`, `C_artefakt` | Residual gesamt / Medienanteil / Artefaktanteil | N |
| `c_w` | Widerstandsbeiwert (drag); `c_w,vor`/`c_w,zurück` richtungsabh. | – |
| `ρ`, `ρ₀` | Mediumsdichte / Referenzdichte (Luft) | kg/m³ |
| `F_int(t)` | mittelwertfreie innere Kraft auf die Hülle | N |
| `v_drift`, `v_osc` | mittlere Drift- / Oszillationsgeschwindigkeit der Hülle; `v_drift` = mittlere Geschwindigkeit, bei der im stationären Zustand das Periodenmittel der Drag-Kraft verschwindet | m/s |
| `F_eff` | effektiver Netto-Schub `= ½ρc_wA·v_drift|v_drift| = x·M·g/L` (Pendel) | N |
| `x`, `L` | statische Auslenkung / Länge der Schubaufhängung | m |
| `Skew(v)` | Schiefe der Geschwindigkeit (Drift-Treiber) | – |
| `Δp_System`, `Δp_Medium` | Impulsänderung System / Medium | kg·m/s |
| `Δs` | gerichtete Nettoverschiebung | m |
| `ΔF`, `F_0` | Mittelkraftverschiebung (≡⟨C⟩) / Referenz mg | N |
| `u_c` | kombinierte Standardmessunsicherheit (GUM) | (je Größe) |
| `σ`, `σ²`, `σ_γ` | Streuung / Varianz / Schiefe-Streuung | N, N², – |
| `k` | Konfidenz-/Detektionsfaktor (≈2) | – |

## 17. Grenzen, offene Fragen, Schluss

**Offen (empirisch):** Ob die im Medium erreichbare Driftgeschwindigkeit über der Tracking-Auflösung liegt und technisch nutzbar ist. Das dynamische Modell (Abschnitt 9) liefert `v_drift ∼ mm/s … cm/s` und effektiven Schub `∼ 10⁻⁷–10⁻⁴ N` — der Schub liegt unter der Kraftschwelle, die Drift-Kinematik ist aber messbar. Die erreichbare Effektgröße bleibt eine offene, *quantitative* Frage; beide Ausgänge (Nachweis oder belastbares Null-Ergebnis für H1) sind gleichwertig informativ.

**Offen (A↔B/D-Brücke):** Es ist **nicht validiert**, dass die in Konfiguration A (fixiert) gemessene Kraft-Schiefe den Schub in Konfiguration D (frei aufgehängt) quantitativ vorhersagt — die Medienreaktion hängt von der Relativgeschwindigkeit ab, die im fixierten Fall ≈0 ist (der Drift-Mechanismus aus §9 greift dort gar nicht). Die Kraft-Schiefe ist ein qualitatives Indiz, kein quantitativer Prädiktor; Konfiguration D liefert die empirische Kalibrierung zwischen Schiefe und Schub.

**Grenzen:** M2-Drift setzt Körperform-Asymmetrie voraus und streift das „keine Flügel"-Handicap (gesondert zu deklarieren). Für eine streng symmetrische Hülle bleibt nur der schwächere M1-Pfad (Geschwindigkeits-Schiefe, ~mm/s). Die Zerlegung `C = C_medium + C_artefakt` ist nur so gut wie die Kontrollen (Abschnitt 11); ohne Dichtevariation *und* Vakuum-zu-Vakuum-Kontrolle nicht belastbar.

**Schluss:** Der Rahmen besitzt eine **positive, erhaltungskonforme, falsifizierbare Hypothese** (H1, medium-gekoppelte Fortbewegung), trennt sauber den theoretischen A-priori-Ausschluss der Leerraum-Hypothese von dessen numerischer Bestätigung und der offenen experimentellen Prüfung, und stellt ein **messgeräte-gekoppeltes** Kriterium sowie unabhängige Kontrollen bereit. Es werden keine neuen physikalischen Prinzipien behauptet und keine Erhaltungssätze in Frage gestellt.

---

## Änderungs-Log v3.4 → v3.5 (fünftes Review — redaktioneller Feinschliff, publikationsreif)

- **Pkt 1 (Sim-Validierung Tempus):** §8 von „reproduziert" auf „wird erwartungsgemäß reproduzieren (in Vorbereitung)" — keine bereits erfolgte Validierung behauptet; A-priori-Ausschluss steht unabhängig.
- **Pkt 2 (Aufhängung):** §9.2 um Relaxationszeit, Schwingungsisolierung und thermisches Rauschen (Brownsche Grenze ~2·10⁻¹¹ m ≪ 35 nm) ergänzt.
- **Pkt 3 (A↔D-Kalibrierung):** §6 explizit als *empirische* Korrelation (keine theoretische Vorhersage) formuliert.
- **Pkt 4 (Zusammenfassung):** „falsifiziert dokumentiert" → „durch Schwerpunktsatz ausgeschlossen (theoretische Falsifikation)" — empirische Konnotation entfernt.
- **Pkt 5 (Redaktion):** `v_drift`-Definition in Klartext; µ-Tabelle unverändert (Aussage „tot" bleibt korrekt).

**Status:** Das fünfte Review erklärt den Rahmen nach diesen Korrekturen für **publikationsfähig** (Preprint / technischer Bericht). Verbleibende offene Punkte sind keine Mängel mehr, sondern reguläre Zukunftsarbeit:

**Vor/bei Veröffentlichung:** Sim-DOIs vergeben und in §8/§15 einsetzen (nachreichbar); Skript mitveröffentlichen; Schubwaagen-`u_c` und Pendel-Relaxationszeit für den konkreten Aufbau bestimmen.

---

*Begleitskript: `pcmms_medienkopplung_modell.py` — reproduziert Dynamik (§9), Mehrmassen-Realisierung (§9.1), Reibungsanalyse und Pendel-Auslenkung (§9.2).*

---

### Versionshistorie (Kurz)
v3 Reframe → weg von „gravitationsähnlichem Antrieb". v3.1 → positive Hypothese H1 (medium-gekoppelte Fortbewegung). v3.2 → realistisches Falsifikationskriterium, Größenordnung. v3.3 → explizites dynamisches Kopplungsmodell, Messstrategie-Korrektur. v3.4 → Mehrmassen-Brücke, Reibungsanalyse, Schub-Pendel. v3.5 → redaktioneller Feinschliff, publikationsreif.
