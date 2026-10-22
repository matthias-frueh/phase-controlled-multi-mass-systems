# PCMMS — Skriptkorrekturen Linie B (06.09.2026)

**Anlass:** externe Skriptprüfung vom 06.09.2026 (Review-Leitfaden, alle zehn Fragen beantwortet).
Zwei Korrekturaufgaben belegt: stationäre Driftkarte neu bestimmen; F_eff von der Pendelkraft trennen.
**Originale unverändert.** Neue Dateien liegen daneben.

> **Vermerk (22.10.2026).** Originaldatei `PCMMS_Skriptkorrekturen_LinieB_2026-09-06.md`, Stand 06.09.2026; hier
> unverändert bis auf diesen Vermerk. Korrekturbeleg der Linie B zur externen Skriptprüfung
> ([`review_leitfaden_skripte_2026-09-06.md`](review_leitfaden_skripte_2026-09-06.md)), Arbeitspaket AP-28 (Stufe S5,
> Status „später“, [`../arbeitsplan_status.md`](../arbeitsplan_status.md)). Simulation, keine Messdaten. Seit dem
> 06.09.2026:
> - **Dateien (§2):** Die v2-Skripte liegen unverändert in [`quelle_kopie/`](../../rechnungen/linie_b/quelle_kopie/),
>   die Karte als [`sweep_13x13_drift_v2.csv`](../../rechnungen/linie_b/sweep_13x13_drift_v2.csv) (LB-04); die
>   v1-Originale in [`quelle_v1/`](../../rechnungen/linie_b/review_2026-09-06/quelle_v1/), die v1-Karte
>   `sweep_13x13_drift.csv` als historische
>   [`daten/sweep_13x13_drift_v1.csv`](../../rechnungen/linie_b/daten/sweep_13x13_drift_v1.csv).
> - **Nachgerechnet:** Karte, integrierte Kontrolle und Dichteunabhängigkeit (§1, §3) in
>   [`PROTOKOLL.md`](../../rechnungen/linie_b/PROTOKOLL.md) LB-04, LB-05 und LB-07, F_drag_drift gegen F̄_A (§4) in
>   LB-08. Die Dichteunabhängigkeit gilt nur für c₁ = 0 (LB-06;
>   [Gegenprüfung](../../rechnungen/linie_b/verifikation/PROTOKOLL.md) LB-06); τ und F̄_A für Wasser sind wegen der
>   zugesetzten Masse nicht belastbar (LB-03).
> - **Offen (§6):** Die KC-Zahl des Trägers beträgt 0,004–0,006 statt ≈ 10⁻² (LB-01); dort ist ein quasistationäres
>   Widerstandsgesetz nicht begründet, für einen glatten Träger nicht gültig (LB-02). Die Zahlen bleiben Modellgrößen
>   des Zweiterm-Ansatzes; eine integrierte Pendelsimulation (Modell C) liegt weiterhin nicht vor.
> - **Folgen für den Korpus (§5):** nicht in die Dokumente eingearbeitet; Forschungsrahmen v3.5 und Prüfarchitektur
>   liegen hier in ihren Fassungen vom Mai bzw. 01.09.2026 (Vermerke dort), v3.6 ist vorgesehen (AP-28). Das
>   [Formelverzeichnis v2.8](../formelverzeichnis/README.md) übernimmt die Trennung von Driftwiderstandskraft und
>   Pendelkraft (Abschnitt „Anschluss an Linie B und C“), nicht die Zahlen.
>
> Lizenz wie der Ordner: CC BY 4.0 ([`../../LICENSE-CC-BY-4.0`](../../LICENSE-CC-BY-4.0)).

## 1 · Was die Prüfung bestätigt hat (und ich übernehme)

- Trägerkinematik `Vcm - RATIO*r_dot` exakt (Impulskinematik); Näherung erst beim Ersetzen der
  Schwerpunktgeschwindigkeit durch einen konstanten Driftwert.
- Konvergenzfehler der v1-Karte **konfigurationsabhängig**: CSV-Beträge 15–66 % des stationären
  Werts; alle 54 negativen Punkte bleiben negativ (kein Phasenfehler); lokale Relaxationszeiten
  5,5–36,6 s in Wasser (linearisiert). Ein festes Fenster oder feste 60 s sind kein Kriterium.
- Dichteunabhängigkeit der stationären Drift auf sechs Stellen (periodische Lösung); die 0,2 % im
  Reproduktionslauf waren Resteinschwingen.
- F_eff (kd·v_d²) ≠ Pendelkraft F̄_A: Faktor 19,7 im Fall S; kein allgemeiner Korrekturfaktor.
- Zeitschritt unkritisch; Brent-Klammer geeignet; Profilamplitude im Fall R 400 mm/s (meine
  Angabe „100 mm/s" war falsch).
- Namenskonflikt „M2": im Skript richtungsabhängiger Widerstand, in der Notiz dynamische
  Instabilität → getrennt.

## 2 · Neue Dateien

| Datei | Inhalt |
|---|---|
| `pcmms_fluid_drift_v2.py` | Stationäre Drift primär über die gemittelte Bilanz (ganze Karte in < 2 s); integriertes RK4-Modell nur als Kontrolle mit Abbruchkriterium über Periodenmittel; rho als Parameter; je Punkt F̄_A und τ; CSV im Schreibmodus |
| `sweep_13x13_drift_v2.csv` | Stationäre Karte, rho = 1000: v_d, F̄_A, τ je Rasterpunkt |
| `pcmms_medienkopplung_modell_v2.py` | Basis 112-Zeilen-Fassung; Rückgabe von F_drag_drift (v1: „F_eff") **und** F̄_A; Pendelauslenkung aus F̄_A; Fälle Z / S / R statt „M1/M2"; Konsolentexte berichtigt |

## 3 · Kennzahlen der stationären Karte (rho = 1000, Skriptparameter)

- Referenz (0°, 0°): **1,0549 mm/s** (v1-CSV: 0,6916). Minimum −0,2945 mm/s, Mittel 0,181 mm/s,
  54/169 negativ. Symmetrisch unter φ₂ ↔ φ₃.
- Triphasik (120°, 240°), Zusatzpunkt außerhalb des Rasters: −0,0810 mm/s, F̄_A = −1,46×10⁻⁶ N
  (Wasser), τ ≈ 42 s.
- Integrierte Kontrolle mit Abbruchkriterium (Δ Periodenmittel < 10⁻⁴ über 10 Perioden):
  (0,0) 1,0544 nach 42 s; langsamster Punkt (221,5°, 110,8°) −0,1657 nach 207 s; Triphasik −0,0807
  nach 228 s — Abweichungen ≤ 0,4 %, Kriterium bei langsamen Punkten noch zu locker (tol 10⁻⁵ in v2).
- F̄_A über die Karte, Wasser: −1,6×10⁻⁵ … +1,4×10⁻⁴ N; Luft (×1,2/1000): −1,9×10⁻⁸ … +1,7×10⁻⁷ N.

## 4 · Ausgaben des Medienkopplungsmodells v2 (M = 1 kg, A = 0,02 m², rho = 1,2)

| Fall | v_d | F_drag_drift (v1 „F_eff") | F̄_A | ⟨x⟩ aus F̄_A (1 kg, 1 m) |
|---|---|---|---|---|
| Z zweistufig 80/20 | 0 | 0 | 0 | 0 |
| S schiefe v | 5,31 mm/s | 3,39×10⁻⁷ N | 6,67×10⁻⁶ N | 680 nm (v1: 34,5 nm) |
| R richtungsabh. 1,5/0,5 | −72,4 mm/s | −3,15×10⁻⁵ N | −3,20×10⁻⁴ N | −32,6 µm (v1: −3,2 µm) |

## 5 · Folgen für den Korpus (aufgelistet, nicht eingearbeitet)

1. Forschungsrahmen v3.5 §9: „effektiver Schub 10⁻⁷–10⁻⁴ N" und „34,7 nm" beruhen auf
   F_drag_drift. Für Konfiguration D ist F̄_A maßgeblich (Faktor ≈ 2⟨|v_osc|⟩/|v_d|, fallabhängig
   10–20). Beide Zahlenreihen gelten nur im Zweiterm-Ansatz (Notiz §6 offen).
2. Prüfarchitektur Linie B §2: Auflösungsanforderung mit F̄_A neu bewerten — Skriptparameter in
   Luft: ⟨x⟩ = F̄_A·L/(Mg) ≈ 1,7×10⁻⁷ N × 1 m / 7,36 N ≈ 23 nm bei (0°, 0°); Sub-Millimeter bleibt
   vier Größenordnungen darüber.
3. Prüfarchitektur §1: „vorhergesagte Drift maximal 0,00069 m/s" → stationär 0,00105 m/s (Wasser-
   und Luft-Wert gleich); das Verhältnis 11.000 : 1 im Freifallargument wird 7.300 : 1 — Schluss
   unverändert.
4. Jede Zitierung von `sweep_13x13_drift.csv` (v1) ist durch `sweep_13x13_drift_v2.csv` zu ersetzen
   oder als „nicht eingeschwungen" zu kennzeichnen.
5. Bezeichnung „Mechanismus 2" bleibt der Notiz (dynamische Instabilität) vorbehalten; im Skript
   heißt der richtungsabhängige Widerstand Fall R.

## 6 · Offen

- Physikalische Gültigkeit des quasistationären Widerstandsgesetzes bei KC ≈ 10⁻² (Notiz §6).
  Keine der Zahlen oben ist davon unabhängig.
- Dynamische Pendelsimulation (Modell C integriert) ist in keiner Skriptfassung enthalten; die
  Beziehung k⟨x⟩ = F̄_C ≈ F̄_A steht bisher nur als Herleitung.
