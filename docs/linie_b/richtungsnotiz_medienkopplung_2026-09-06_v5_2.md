# PCMMS — Notiz: Richtung „Gleichrichtung und mögliche Einsatzschwellen phasenstrukturierter Medienkopplung"

**Datum:** 06.09.2026 · **Version:** v5 — ersetzt v1–v4 vom selben Tag · **Status:** Richtungsnotiz, redaktioneller Prüfzyklus abgeschlossen (vier externe Prüfungen) · offene Modellfrage §6 bleibt offen · ausdrücklich **nicht** der nächste Schritt
**Gilt für:** Linie B (H1_fluid), Forschungsrahmen v3.5 §1, §7, §9, Notiz Prüfarchitektur Linie B (01.09.2026)
**Autor:** Matthias Früh · ORCID 0009-0005-9984-4207

> **Vermerk (22.10.2026).** Originaldatei `PCMMS_Notiz_Richtung_Medienkopplung_2026-09-06_v5.2.md`, Stand 06.09.2026,
> Fassung v5.2 (die Kopfzeile nennt „v5“; v5.1 und v5.2 stehen im Änderungslog, §14); hier unverändert bis auf diesen
> Vermerk. Die Vorfassungen v1–v5.1 liegen nicht im Repository. Linie B, Arbeitspaket AP-28 (Stufe S5, Status
> „später“, [`../arbeitsplan_status.md`](../arbeitsplan_status.md)). Keine Messdaten. Seit dem 06.09.2026 nachgerechnet,
> berichtigt oder offen:
> - **Dateien (§7, §13, §14):** Skriptkorrekturen, Forschungsrahmen v3.5 und Prüfarchitektur liegen in diesem Ordner
>   ([`skriptkorrekturen_2026-09-06.md`](skriptkorrekturen_2026-09-06.md),
>   [`forschungsrahmen_v3_5_2026-05.md`](forschungsrahmen_v3_5_2026-05.md),
>   [`pruefarchitektur_2026-09-01.md`](pruefarchitektur_2026-09-01.md)). `pcmms_fluid_drift.py` und
>   `pcmms_medienkopplung_modell.py` liegen als v1 in [`quelle_v1/`](../../rechnungen/linie_b/review_2026-09-06/quelle_v1/),
>   als v2 in [`quelle_kopie/`](../../rechnungen/linie_b/quelle_kopie/); `sweep_13x13_drift.csv` ist
>   [`daten/sweep_13x13_drift_v1.csv`](../../rechnungen/linie_b/daten/sweep_13x13_drift_v1.csv) (nicht eingeschwungen).
> - **Kennzahlen (§6):** a = 0,134 mm (halbe Spitze-Spitze), KC = 2πa/D ≈ 0,0042 bzw. U_max·T/D ≈ 0,0060 statt 0,009,
>   β ≈ 2,67·10⁴ ([`PROTOKOLL.md`](../../rechnungen/linie_b/PROTOKOLL.md) LB-01, Abschnitt 3 Nr. 1–2); KC ≪ 1 gilt in
>   jeder Definition.
> - **Offene Modellfrage (§6):** präzisiert, nicht gelöst. Für einen glatten Träger (Ersatzkugel) ist das
>   quasistationäre Gesetz nicht gültig, die Kraft in führender Ordnung linear mit Periodenmittel null; bei
>   vorn-hinten-symmetrischer Hülle entsteht ein Mittelwert frühestens in dritter Ordnung, sein Betrag ist nicht
>   abgeschätzt; scharfe Kanten sind offen (LB-02). Das Kraftmodell bei kleiner KC-Zahl ist Gegenstand von AP-28.
> - **Modell B (§4.2):** Dichteunabhängigkeit bei c₁ = 0 und ∝ ρ unterhalb des Crossovers bei c₁ > 0 sind
>   nachgerechnet (LB-06; [Gegenprüfung](../../rechnungen/linie_b/verifikation/PROTOKOLL.md) LB-06). Bedingung (iii)
>   prüft nur den Widerstand; in Wasser beträgt die zugesetzte Masse ≈ 2,6·M_ges, die Rückstoßkinematik gilt dort nicht
>   (LB-03).
> - **Prüfprogramm (§7):** Punkte 2 und 3 sind erledigt (Vermerke im Text) und nachgerechnet (LB-05, LB-07). Die
>   Kennzahlen aus Punkt 1 sind für die Skriptparameter gerechnet; Trägergeometrie und Wahl des Kraftmodells sind offen
>   (LB-01, LB-02). Modell C (Punkt 4) ist in keiner Skriptfassung integriert (Skriptkorrekturen §6).
>
> Lizenz wie der Ordner: CC BY 4.0 ([`../../LICENSE-CC-BY-4.0`](../../LICENSE-CC-BY-4.0)).

> **Vorrang:** V1 und Linie A unverändert. Diese Notiz ersetzt keine bestehende Projektfassung und
> ändert die Präregistrierung nicht.
>
> **v5:** Begrenzte Korrekturen nach vierter externer Prüfung (06.09.2026): mittlere Medienkraft
> modellweise indiziert (F̄_A, F̄_B = 0, F̄_C = k⟨x⟩); Richtungsregel eingegrenzt; vollständige
> endliche Fensterbilanz; §4.1 und §6 eingegrenzt. Keine Zahl in dieser Fassung, die nicht aus einer
> angegebenen Gleichung folgt.

---

## 1 · Richtungsformulierung (korpustauglich)

Untersucht wird, unter welchen Bedingungen periodische, phasenstrukturierte Innenbewegungen mehrerer
Teilmassen über die Kopplung eines Trägers an ein Medium gerichtete Bewegung erzeugen. Dabei werden
drei Fälle unterschieden: stetige Gleichrichtungseffekte, Übergänge zwischen Widerstandsregimen und
mögliche dynamische Instabilitäten. Existenz, Richtung und Skalierung des Effekts werden als abhängig
von Bewegungsprofil, Phasenlage, Geometrie und Medienparametern geprüft. PCMMS realisiert die
Anordnung in ihrer einfachsten kontrollierbaren Form: drei Teilmassen mit vorgegebenem
Bewegungsprofil, ein Träger, ein Medium — bisher simuliert, nicht gemessen.

---

## 2 · Drei Begriffe, die getrennt bleiben

| Begriff | Bedeutung |
|---|---|
| **Crossover** | Ein Kraftbeitrag wird gegenüber einem anderen bedeutend; stetig, keine Bifurkation |
| **Dynamische Einsatzschwelle** | Ein Bewegungszustand entsteht oder verliert seine Stabilität. Hysterese, Bistabilität und Abhängigkeit von Anfangsbedingungen sind **mögliche** Signaturen, keine notwendigen |
| **Nachweisgrenze** | Ein vorhandener Effekt wird messtechnisch auflösbar (Forschungsrahmen §7) |

---

## 3 · Was die Klasse definiert — und was offen ist

**Definierend:**

1. **Mittelwertfreie Innen-Relativbewegung**: ⟨q̇_k⟩ = 0 pro Periode für jede Teilmasse. Aus der
   Innenbewegung allein folgt kein Nettoeffekt (Linie-B-Gegenstück zum Schwerpunktsatz).
2. **Nettoeffekt nur über nichtlineare Kopplung**: In einem linearen, gedächtnisfreien
   Widerstandsmodell ist die mittlere Medienkraft bei mittelwertfreier Trägerbewegung exakt null.

**Untersuchungsfragen, keine Definitionsmerkmale:**

3. Existenz einer dynamischen Einsatzschwelle.
4. Form der Dichteabhängigkeit.

**Klarstellung:** ⟨q̇_k⟩ = 0 sagt nichts über die Trägergeschwindigkeit V relativ zum Medium; deren
Periodenmittel ist die Drift (freies System) bzw. null (aufgehängtes System, §4.3).

---

## 4 · Drei Modelle — Ergebnisse werden nicht zwischen ihnen übertragen, ohne die Bedingung zu nennen

Gemeinsame Bausteine: Rückstoß der Innenmassen F_int(t) = −Σ_k m_k q̈_k mit ⟨F_int⟩ = 0 über ganze
Perioden; Widerstandsgesetz F_W(V), V = Trägergeschwindigkeit relativ zum ruhenden Medium. Im
bisherigen Ansatz F_W = −(c₁V + c₂ρV|V|), c₂ = ½·C_D·A. **Die Gültigkeit dieses Ansatzes ist selbst
offen (§6).** Wird stattdessen ein vollständiges C_D(Re)-Gesetz verwendet, entfällt der Term c₁V —
sonst ist der lineare Widerstand doppelt enthalten.

**Mittlere Medienkraft — modellweise, nicht übertragbar:**

| Größe | Bedeutung |
|---|---|
| F̄_A = ⟨F_W(v_osc)⟩ | Gleichrichtungskraft bei vorgegebener, mittelwertfreier Trägerbewegung |
| F̄_B = ⟨F_W(V_B)⟩ = 0 | Tatsächliche mittlere Medienkraft im freien eingeschwungenen Modell — null trotz Drift |
| F̄_C = ⟨F_W(V_C)⟩ = k⟨x⟩ | Tatsächliche mittlere Medienkraft im periodischen Pendelmodell |

Die angenäherte freie Drift (4.2) und die Auslenkung (4.3) folgen dem Vorzeichen von F̄_A; die
Indizes bleiben in allen Ableitungen erhalten.

**Richtungsregel (eingegrenzt):** Für einen einfachen mittelwertfreien Trägerhub über dieselbe
Strecke s mit konstanter positiver Geschwindigkeit während T₊ und negativer während T₋ gilt

    ⟨V|V|⟩ = s² / (T₊ + T₋) · (1/T₊ − 1/T₋)

Ist die positive Bewegung die schnellere (T₊ < T₋), ist der Ausdruck positiv und der quadratische
Widerstand ergibt eine negative mittlere Medienkraft. Das überträgt sich auf gleich geformte,
zeitlich unterschiedlich gestreckte Hin- und Rückhübe: Die Gleichrichtungskraft wirkt **entgegen der
schnelleren Trägerbewegung**. In der Rückstoßnäherung

    v_osc ≈ −(1/M_ges) · Σ_k m_k q̇_k

entspricht das der Richtung des schnellen **massengewichteten** Innenmassenhubs. Bei dephasierten
Modulen zählt die Summenbewegung, nicht die schnelle Phase eines einzelnen Moduls. Für allgemeine
Wellenformen und Phasenkonfigurationen reicht „positive Phase schneller" nicht aus; die Richtung wird
aus dem vollständigen Geschwindigkeitsprofil berechnet. Gilt im quasistationären Modell; vgl. §6.

### 4.1 Modell A — vorgegebene Trägerbewegung (Kraftmodell)

V(t) = v_osc(t) vorgegeben, mittelwertfrei. Allgemein, für jedes ungerade, gedächtnisfreie F_W:

    F̄_A = ⟨F_W(v_osc)⟩

samt den Symmetrieeigenschaften aus §5. Für den Zweiterm-Ansatz konkret:

    F̄_A = −c₂·ρ·⟨v_osc|v_osc|⟩

Der lineare Anteil trägt nichts bei. Entspricht der Bilanzrechnung in
`pcmms_medienkopplung_modell.py` (Angabe der Notiz; nicht extern geprüft).

### 4.2 Modell B — freie Bewegung (Driftmodell)

    M_ges·dV/dt = F_int(t) − c₁·V − c₂·ρ·V|V|

Eingeschwungen, über ganze Perioden: c₁⟨V⟩ + c₂ρ⟨V|V|⟩ = 0, also F̄_B = 0 — Drift bei
verschwindender mittlerer Gesamtkraft und verschwindender mittlerer Medienkraft. Näherung
V = v_d + v_osc mit v_osc ≈ Rückstoßbewegung, gültig wenn Widerstand ≪ Trägheitskraft:
c₂ρ·v_osc/(M·2πf) ≈ 4×10⁻⁶ (Luft), 3×10⁻³ (Wasser) mit Skriptparametern.

- Mit |v_d| ≪ |v_osc|:

      v_d ≈ − c₂·ρ·⟨v_osc|v_osc|⟩ / (c₁ + 2·c₂·ρ·⟨|v_osc|⟩) = F̄_A / (c₁ + 2·c₂·ρ·⟨|v_osc|⟩)

  Für c₁ = 0 kürzt sich ρ heraus: **Im gemittelten rein quadratischen Modell ist die stationäre
  Drift bei festem Oszillationsprofil dichteunabhängig.** Ob das integrierte Skript
  (`pcmms_fluid_drift.py`, c₁ = 0, ρ = 1000; Angabe der Notiz) diese Näherung erfüllt, zeigt erst der
  Konvergenz- und Dichtevergleich (§7).
- Mit c₁ > 0: ∝ ρ unterhalb des Crossovers c₂ρ⟨|v_osc|⟩ ≈ c₁, Sättigung darüber.
- Einschwingzeit aus der Linearisierung der Driftbilanz um v_d:

      τ ≈ M / (c₁ + 2·c₂·ρ·⟨|v_osc|⟩)

  Für c₁ = 0: τ ≈ M/(2c₂ρ⟨|v_osc|⟩) — Wasser ≈ 6 s, Luft ≈ 80 min (Skriptparameter). Im linear
  dominierten Bereich geht τ gegen M/c₁. Freie Drift in Luft ist keine praktikable Observable
  (bestätigt Forschungsrahmen §9.2).

### 4.3 Modell C — aufgehängte Bewegung (Konfiguration D)

    M_ges·dV/dt = F_int(t) + F_W(V) − k·x − c_p·V,   k = M·g/L

(F_W enthält den linearen und den quadratischen Medienwiderstand.) Bedingungen für nahezu freie
Rückstoßbewegung bei f: (i) k ≪ M(2πf)² — mit L = 1 m, f = 10 Hz: ≈ 7 N/m gegen ≈ 3×10³ N/m;
(ii) Aufhängungsdämpfung klein gegen die dynamische Trägheit, c_p/(M·2πf) ≪ 1; (iii) Widerstand ≪
Trägheit wie in 4.2.

**Vollständige Bilanz über ein endliches Fenster T** (Δ = Endwert minus Anfangswert):

    k·⟨x⟩_T = ⟨F_W⟩_T − M_ges·ΔV/T − Σ_k m_k·Δq̇_k/T − c_p·Δx/T

mit ⟨V⟩_T = Δx/T exakt — dieselbe Randtermlogik wie die Fensterkorrektur in Linie A. Der
Ortsrandterm allein korrigiert die Kraft-Auslenkungs-Beziehung nicht; erst bei ganzen Perioden der
eingeschwungenen Gesamtbewegung verschwinden alle Randterme, und es gilt

    k·⟨x⟩ = F̄_C,   ⟨x⟩ = F̄_C · L/(M·g)

Unter (i)–(iii) ist F̄_C ≈ F̄_A: Die Erwartungskurve für Konfiguration D folgt aus **Modell A**, nicht
aus Modell B. Ein vollständig festgehaltener Träger hätte V = 0 und keine Medienkraft.
Aufhängungssteifigkeit und -dämpfung gehören ins Modell; c_p trägt zum Periodenmittel nichts bei.

**Bedingte Modellabschätzung** (Skriptparameter: v_osc-Amplitude ≈ 0,012 m/s, Egg 0,65/0,35, Module
in Phase, quasistationäres C_D = 0,8, 1000 mbar): |F̄_A| ≈ 1,7×10⁻⁷ N, |⟨x⟩| ≈ 23 nm bei L = 1 m.
Rechnerisch konsistent mit der angesetzten Kraft; keine abgesicherte Auflösungsanforderung, solange
§6 offen ist. Unter dieser Bedingung läge die in der Prüfarchitektur genannte Sub-Millimeter-Auflösung
vier Größenordnungen über dem Signal.

### 4.4 Übertragungsregeln

| Von → nach | Überträgt sich | Bedingung |
|---|---|---|
| A → C | F̄_A ≈ F̄_C, damit ⟨x⟩ | (i)–(iii) aus 4.3, v_osc = Rückstoßbewegung, ganze Perioden |
| A → B | ⟨v_osc|v_osc|⟩ als Eingang der Driftbilanz; Driftvorzeichen = Vorzeichen von F̄_A | Widerstand ≪ Trägheit |
| B → C | **nichts** — ⟨V⟩ ≠ 0 dort, ⟨V⟩ = 0 hier; F̄_B = 0, F̄_C ≠ 0 | — |

---

## 5 · Dichteabhängigkeit und Kontrollen — modellweise

**Dichte (Modell C):** F̄_C ∝ ρ·C_D(Re) bei unverändertem Bewegungsverlauf; nur bei konstantem C_D
eine Gerade. Über die Druckreihe fällt Re_D von ≈ 320 auf ≈ 0,02 (§8); C_D ist dort nicht konstant.
Im Stokes-Grenzfall (C_D = 24/Re) wird der „quadratische" Term selbst linear und richtet nichts
gleich. Die Erwartungskurve ist aus einem regimeabhängigen Kraftmodell zu **berechnen**. In der
Prüfarchitektur ist „Δv(p)" als **ΔF̄_C(p) bzw. Δ⟨x⟩(p)** zu führen — Vorschlag, noch keine
abgesicherte Korrektur, solange §6 offen ist.

**Symmetriekontrollen — Nullvorhersagen sind Periodenmittel, nicht Geschwindigkeiten:**

| Operation | Modell A: F̄_A | Modell B: ⟨V⟩ | Modell C: ⟨x⟩ | Bedingung |
|---|---|---|---|---|
| Sinus (zeitsymmetrisches Profil) | 0 | 0 | 0 | ungerades, gedächtnisfreies F_W; symmetrische Geometrie |
| Räumliche Spiegelung q_k(t) → −q_k(t) | −F̄_A | −⟨V⟩ | −⟨x⟩ | Parität; exakt bei symmetrischer Geometrie, auch mit Gedächtnistermen |
| Zeitumkehr des Profils, v_rev(t) = −v(−t) | −F̄_A exakt | nur unter den Näherungen aus 4.2 | nur unter den Näherungen aus 4.3 | ungerades, gedächtnisfreies F_W bei vorgegebener Bahn |

Der Träger schwingt in allen drei Fällen weiter; null sind die Periodenmittel. Abweichungen im
Aufbau: bei Spiegelung → richtungsabhängiger Widerstand oder Geometrieasymmetrie; bei Zeitumkehr →
Beiträge jenseits der Profilgleichrichtung, **nicht** automatisch Bias; bei Sinus → Geometrie- oder
Strömungsbias, weitere Kopplungen. Das Profilquartett Egg / gespiegelt / zeitumgekehrt /
gespiegelt-zeitumgekehrt trennt Profilgleichrichtung von Richtungsbias. „Zeitasymmetrisch" garantiert
für sich nicht ⟨V|V|⟩ ≠ 0; die Größe ist aus der tatsächlichen Trägerbewegung zu berechnen. Die
Phase formt das massengewichtete Summenprofil und kann Harmonische auslöschen — keine allgemeine
Monotonie in „Phasenkohärenz".

---

## 6 · Offene Modellfrage Nr. 1 — quasistationäre Verwendung eines stationären Widerstandsgesetzes

Offen ist die **quasistationäre Verwendung eines stationären Widerstandsgesetzes** — gleich welcher
Form, auch C_D = 24/Re — für die vorliegende Oszillation. Kennzahlen mit Skriptparametern
(Trägeramplitude a ≈ 0,3 mm, Trägermaß D ≈ 0,2 m, f = 10 Hz, Luft):

- Keulegan-Carpenter-Zahl KC = 2πa/D ≈ 0,009
- Stokes-Schichtdicke δ = √(2ν/ω) ≈ 0,7 mm
- Stokes-Parameter β = fD²/ν ≈ 3×10⁴

Referenzbefund für **Kreiszylinder**: Für planare Oszillationen kleiner Amplitude stimmen die
gemessenen Kraftbeiwerte mit der Stokes–Wang-Analyse überein — zweidimensionale, anliegende, laminare
Strömung —, und erst oberhalb einer kritischen Keulegan-Carpenter-Zahl weicht C_D davon ab
(Sarpkaya 1986). Dieser Befund gilt für die dort untersuchte Geometrie; er ist nicht unmittelbar auf
die noch unzureichend spezifizierte Trägergeometrie übertragbar.

**Was daraus folgt — und nur das:** Die kleine KC-Zahl ist ein hinreichender Grund, das
quasistationäre Widerstandsmodell für die Trägerkonfiguration in Frage zu stellen. Die
quasistationären Effektgrößen (Forschungsrahmen §9: 10⁻⁷–10⁻⁴ N) sind für die vorliegende
Oszillation **nicht abgesichert**. Ein geometriespezifisches instationäres Modell muss klären, welche
mittlere Kraft entsteht; eine stationäre Sekundärströmung kann vorhanden sein, ohne eine gerichtete
resultierende Kraft zu erzeugen, und welche Beiträge sich aufheben, hängt von Geometrie,
Bewegungsprofil und Randbedingungen ab. **Betrag und führende Ordnung bleiben offen.** Größere
Trägeramplitude oder Anhänge mit größerer relativer Amplitude sind Auslegungsoptionen, deren Wirkung
ebenfalls erst das instationäre Modell zeigt.

**Vorrang:** Diese Frage ist **vor** Dichte- und Symmetrierechnungen zu klären, weil alle Kurven in
§5 vom Widerstandsgesetz erben. Sie wird nicht durch eine weitere Abschätzung ersetzt. Für den Status
dieser Notiz muss sie nicht gelöst sein.

---

## 7 · Prüfprogramm — rechnerisch, ohne Hardware, in dieser Reihenfolge

1. **Kennzahlen festschreiben** (KC, β, δ, Re_D) für den tatsächlichen Parametersatz und die
   tatsächliche Trägergeometrie; entscheiden, welches Kraftmodell zulässig ist (quasistationär /
   Zweiterm / vollständiges C_D(Re) / instationär). Entweder Zweiterm-Ansatz oder vollständiges
   C_D(Re), nie beides.
2. **Konvergenz.** `pcmms_fluid_drift.py` mit T_SIM ≥ 60 s (≥ 10 τ in Wasser); Vergleich mit
   `sweep_13x13_drift.csv`. Burn-in 4 s liegt unter τ ≈ 6 s; der Maximalwert 0,691635 mm/s ist
   vermutlich transientenbehaftet.
   **Erledigt 06.09.:** bestätigt, konfigurationsabhängig — CSV-Beträge 15–66 % des stationären
   Werts, Vorzeichen unverändert; Referenz stationär 1,0549 mm/s. Ein festes Fenster ist kein
   Kriterium; v2-Skript mit Bilanz und Abbruchkriterium, siehe
   `PCMMS_Skriptkorrekturen_LinieB_2026-09-06.md`.
3. **Dichtevergleich.** Gleiches Skript mit ρ = 1000 und ρ = 1,2 bei ausreichender T_SIM: prüft die
   Näherung aus 4.2 direkt.
   **Erledigt 06.09.:** stationäre Drift bei ρ = 1000 / 100 / 1,2 auf sechs Stellen gleich
   (periodische Lösung, externe Prüfung); Näherung aus 4.2 für die Skriptparameter erfüllt.
4. **Modell C implementieren** (k, c_p; Bedingungen (i)–(iii) protokollieren) und ⟨x⟩ gegen F̄_A/k
   vergleichen; Periodenmittel über ganze Perioden bilden; Randterme der endlichen Fensterbilanz
   ausweisen.
5. **Kraftmodell nach Punkt 1**, ρ(p) für Luft über die Druckreihe; Ausgabe F̄_A(p), ⟨x⟩(p), v_d(p) —
   modellweise getrennt.
6. **Profilquartett und Sinus** (§5); Auf-/Abwärtsfahrten, verschiedene Anfangsbedingungen — im
   Widerstandsmodell ein eindeutiger Fixpunkt, also keine Hysterese: Nullvorhersage für Mechanismus 2.
7. **Kennzahlen je Druckstufe protokollieren.**

**Ergebnisklassen:** (a) Kontrollen erfüllt, Kurven konsistent → Erwartungskurve für die
Prüfarchitektur modellweise festgeschrieben; (b) Kurven weichen ab, Kontrollen erfüllt → Kraftmodell
nachziehen; (c) Kontrollen verletzt → Implementierungsfehler, zuerst beheben.

---

## 8 · Regime-Einordnung der Druckreihe

Annahmen: D ≈ 0,2 m, v_osc-Amplitude ≈ 0,012 m/s, Luft 20 °C, μ = 1,8×10⁻⁵ Pa·s,
mittlere freie Weglänge λ ≈ 68 µm bei 1 mbar (λ ∝ 1/p).

| p [mbar] | ρ [kg/m³] | Re_D | Kn (D = 0,2 m) | Regime (stationär gedacht) |
|---|---|---|---|---|
| 2000 | 2,4 | ≈ 320 | 1,7×10⁻⁷ | Übergangsbereich, C_D nicht konstant |
| 1000 | 1,2 | ≈ 160 | 3,4×10⁻⁷ | Übergangsbereich |
| 500 | 0,6 | ≈ 80 | 6,8×10⁻⁷ | Übergangsbereich |
| 100 | 0,12 | ≈ 16 | 3,4×10⁻⁶ | nahe Crossover (Re_D ≈ 24/C_D ≈ 30 → p* ≈ 200 mbar) |
| 10 | 0,012 | ≈ 1,6 | 3,4×10⁻⁵ | linear dominiert |
| 1 | 0,0012 | ≈ 0,16 | 3,4×10⁻⁴ | Stokes-Bereich |
| 0,1 | 0,00012 | ≈ 0,016 | 3,4×10⁻³ | Stokes-Bereich, Kontinuum für den Träger |

Kn < 10⁻² über die gesamte Reihe: Kontinuum für den Träger; kleinere lokale Geometrieskalen
gesondert prüfen. Die Re_D-Spalte beschreibt eine gedachte stationäre Anströmung; für die
tatsächliche Oszillation sind KC und β maßgeblich (§6).

---

## 9 · Mechanismus 2 — dynamische Instabilität (Alternativhypothese)

Für geflappte Körper ist ein Schwellenübergang publiziert (Vandenberghe, Zhang, Childress 2004;
Vandenberghe, Childress, Zhang 2006: starrer symmetrischer Flügel, vertikal geflappt, horizontal
frei; oberhalb einer kritischen Flappfrequenz entsteht Vorwärtsflug bis zu konstanter
Endgeschwindigkeit). Numerisch wird oberhalb einer hinreichend großen Frequenz-Reynolds-Zahl
gerichtete Fortbewegung zum Attraktor eines anfangs ruhenden Körpers; das Strömungsfeld verliert
erst durch eine von-Kármán-artige Instabilität seine Symmetrie, dann stoßen Wechselwirkungen mit
abgelösten Wirbeln den Körper in Bewegung (Alben, Shelley 2005). Hysterese und Bistabilität wurden
dort berichtet — als mögliche Signaturen, nicht als notwendige Merkmale jeder Einsatzschwelle.

**Zahlenwerte nur mit Definition:** Eine Sekundärquelle (Preprint 2025/JFM 2026) nennt Re_f* ≈ 20–55
mit eigener Nondimensionalisierung; laut externer Prüfung nennt die Originalarbeit mit
Re_f = ρ·f·a·c/μ einen Einsatz um 500 und ein Abstoppen um 390. Volltext prüfen; keine Zahl ohne
Definition übernehmen.

**Einordnung für PCMMS:** Trägeramplitude ≈ 0,3 mm bei ≈ 0,2 m (a/ℓ ≈ 10⁻³, KC ≈ 10⁻²) gegen
Amplituden von der Größenordnung des Flügelmaßes in den zitierten Arbeiten. Eine direkte
Übertragung der Flügelbefunde auf den Träger ist nicht gegeben; andere Strömungsinstabilitäten sind
damit nicht ausgeschlossen. Welche für die tatsächliche Trägergeometrie maßgeblich ist, gehört zu §6.
Für Anhänge mit großer relativer Amplitude bleibt Mechanismus 2 offen.

Umkehranordnung — Medium oszilliert, Körper passiv — publiziert: passiver Körper mit flexiblen
Flügeln (Childress, Vandenberghe, Zhang 2006), starre Pyramide (Weathers et al. 2010), Stabilität
(Liu et al. 2012). Vergleichsfälle, keine äquivalente Spiegelform.

---

## 10 · Gestrichen gegenüber v1–v4

- v1: „unterhalb exakt null"; harte Schwelle beim Übergang linear → quadratisch; „einfachster belegter
  Fall"; garantierte Monotonie in Dichte und Phasenkohärenz; Einsatzschwelle als Klassenbedingung.
- v2: „Träger gehalten" für Konfiguration D; „Gerade durch den Ursprung"; Zeitumkehr als exakte
  allgemeine Nullkontrolle; Knudsen-Werte um Faktor zehn; Re_f* ≈ 20–55 ohne Definition.
- v3: Vorzeichen in Drift- und Pendelformel; „Sinus → v = 0" statt Periodenmittel; Fehlerordnung
  O(Widerstand/Trägheit) für die volle Dynamik; in §6 effektive Fläche D·δ, Faktor δ/D, Überschlag
  10⁻¹⁰ N, Honji als maßgebliche Instabilität, KC ≳ 2 als Ausweg; Hysterese als notwendige Signatur.
- v4: eine modellübergreifende Kraftgröße F̄ („Auslenkung und Drift folgen dem Vorzeichen von F̄");
  Richtungsregel ohne Einschränkung auf gleich geformte Hübe und massengewichtete Summenbewegung;
  endliche Fensterbilanz nur mit Ortsrandterm; „stationäres C_D setzt abgelöste Strömung voraus";
  Zweiterm-Formel als allgemeine Aussage in §4.1.

---

## 11 · Abgrenzung

Diese Notiz macht keine Aussage über ein bestimmtes Phänomen außerhalb des PCMMS-Aufbaus. Sie
definiert eine Anordnungsklasse über zwei Bedingungen, trennt drei Modelle und drei
Schwellenbegriffe, benennt eine offene Modellfrage und ein Rechenprogramm. Eine Übertragung auf
andere Systeme ist eine eigene empirische Frage, die PCMMS nicht beantworten kann. Motivation
außerhalb dieses Rahmens ist nicht Bestandteil des Korpus.

---

## 12 · Einordnung im Korpus

- Forschungsrahmen v3.5 §1: Klassenformulierung als Ergänzung.
- Forschungsrahmen v3.5 §9: Effektgrößenschätzung unter Vorbehalt von §6 dieser Notiz; Hinweis auf
  Modelltrennung A/B/C, indizierte Kraftgrößen F̄_A/F̄_B/F̄_C und τ ∝ 1/ρ.
- Prüfarchitektur Linie B: §3 dort — Erwartungskurve modellweise berechnen, „Δv(p)" als
  ΔF̄_C(p)/Δ⟨x⟩(p); §2 dort — Auflösungsanforderung der Aufhängung nach Klärung von §6 neu bewerten;
  §4 dort — Mechanismus 2 mit möglicher Signatur Hysterese/Bistabilität ergänzen.
- Präregistrierung: unverändert. H1_fluid bleibt optional.

---

## 13 · Literatur

DOI geprüft:

- Vandenberghe N., Zhang J., Childress S. (2004): Symmetry breaking leads to forward flapping flight.
  *J. Fluid Mech.* 506, 147–155. doi:10.1017/S0022112004008468
- Vandenberghe N., Childress S., Zhang J. (2006): On unidirectional flight of a free flapping wing.
  *Phys. Fluids* 18, 014102. doi:10.1063/1.2148989
- Alben S., Shelley M. (2005): Coherent locomotion as an attracting state for a free flapping body.
  *Proc. Natl. Acad. Sci. USA* 102(32), 11163–11166. doi:10.1073/pnas.0505064102
- Childress S., Vandenberghe N., Zhang J. (2006): Hovering of a passive body in an oscillating airflow.
  *Phys. Fluids* 18, 117103. doi:10.1063/1.2371123
- Sarpkaya T. (1986): Force on a circular cylinder in viscous oscillatory flow at low Keulegan–Carpenter
  numbers. *J. Fluid Mech.* 165, 61–71. doi:10.1017/S0022112086002999

Aus Referenzlisten, nicht direkt geprüft:

- Bearman P. W., Downie M. J., Graham J. M. R., Obasaju E. D. (1985): Forces on cylinders in viscous
  oscillatory flow at low Keulegan–Carpenter numbers. *J. Fluid Mech.* 154, 337–356.
- Wang C.-Y. (1968): On high-frequency oscillating viscous flows. *J. Fluid Mech.* 32, 55–68.
- Weathers A., Folie B., Liu B., Childress S., Zhang J. (2010): Hovering of a rigid pyramid in an
  oscillatory airflow. *J. Fluid Mech.* 650, 415–425.
- Liu B., Ristroph L., Weathers A., Childress S., Zhang J. (2012): Intrinsic stability of a body
  hovering in an oscillating airflow. *Phys. Rev. Lett.* 108, 068103.
- Childress S., Dudley R. (2004): Transition from ciliary to flapping mode in a swimming mollusc:
  flapping flight as a bifurcation in Re_ω. *J. Fluid Mech.* 498, 257–288.

Intern:

- PCMMS_Forschungsrahmen_v3_5_Frueh_2026.md, §1, §7, §9
- PCMMS_Notiz_Pruefarchitektur_LinieB.md (01.09.2026)
- pcmms_fluid_drift.py · pcmms_medienkopplung_modell.py · sweep_13x13_drift.csv (Angaben der Notiz)
- Externe Prüfungen der v1–v4 (06.09.2026), Punkte übernommen wie in §10 vermerkt

---

## 14 · Änderungslog

- 2026-09-06 · v1 · Erstfassung.
- 2026-09-06 · v2 · Schwellenbehauptung zurückgenommen; Begriffe getrennt; Trägerdynamik von
  Innenbewegung getrennt; Regimetabelle; Profiltripel; Konvergenzprüfung.
- 2026-09-06 · v3 · Modelle A/B/C mit Übertragungsregeln; Konfiguration D als aufgehängte Bewegung;
  Dichteunabhängigkeit als Näherung; Spiegelung als exakte Kontrolle; Kn-Tabelle berichtigt;
  Vandenberghe-Werte nur mit Definition; offene Modellfrage Nr. 1.
- 2026-09-06 · v4 · Vorzeichen berichtigt; Symmetrietabelle als Periodenmittel; Randterm; Bedingung
  c_p/(Mω) ≪ 1; keine Doppelzählung; §6 auf die offene Frage reduziert.
- 2026-09-06 · v5 · Kraftgrößen modellweise indiziert (F̄_A, F̄_B = 0, F̄_C = k⟨x⟩); Richtungsregel
  eingegrenzt (gleich geformte Hübe, massengewichtete Summenbewegung, Rechteckhub-Formel);
  vollständige endliche Fensterbilanz; §4.1 auf Zweiterm-Ansatz eingegrenzt; §6 erster Satz
  eingegrenzt. Redaktioneller Prüfzyklus abgeschlossen.
- 2026-09-06 · v5.1 · Fünfte externe Prüfung bestätigt v5 (Kraftgrößen, Richtungsregel,
  Fensterbilanz, §6, Statustrennung). Ergänzt: Einschwingzeit mit c₁,
  τ ≈ M/(c₁ + 2c₂ρ⟨|v_osc|⟩). Die Bestätigung betrifft die innere Konsistenz der Ableitungen, nicht
  die Skriptergebnisse oder die physikalische Effektgröße. Sachlich offen: §6 und die Konvergenz der
  Driftkarte. Vorrang V1/Linie A.
- 2026-09-06 · v5.2 · Skriptprüfung (extern, reproduziert): Prüfprogramm Punkte 2 und 3 erledigt;
  Definitionslücke F_eff (kd·v_d²) gegen F̄_A im Medienkopplungsmodell belegt (Faktor ≈ 20 im
  Fall S); Folgen für Forschungsrahmen §9 und Prüfarchitektur aufgelistet in
  `PCMMS_Skriptkorrekturen_LinieB_2026-09-06.md`, nicht eingearbeitet. §6 unverändert offen.
