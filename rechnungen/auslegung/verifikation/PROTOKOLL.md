# P2 · Gegenprüfung der Prüfgruppe „auslegung“ (Rolle: unabhängiger Gegenprüfer)

> **Vermerk zur Übernahme (04.10.2026).** Protokoll aus der Gesamtprojektanalyse 10/2026, Stand 02.10.2026, unverändert bis auf Pfade und Quellenangaben. Geprüft wurde der Repository-Stand `cd7be6a` (28.09.2026) mit der Präregistrierung v2 vom 25./28.09.2026; die späteren Änderungen aus PR #13 und PR #14 (unter anderem Präregistrierung v2 mit Arbeitsfestlegungen, `code/auslegung.py`, `code/ereignisloeser.py`) sind nicht eingearbeitet. Alle Zahlen sind Simulation oder Analytik, keine Messdaten. Verweise wie „L1a-019“, „P1 §3“ oder „B01–B14“ zeigen auf Arbeitsdokumente der Analyse, die nicht im Repository liegen. Quellen, die nicht im Repository liegen, sind als „(Quelle außerhalb des Repositorys)“ gekennzeichnet. Startbefehle und Grenzen je Gruppe: [`rechnungen/README.md`](../../README.md).

Stand 02.10.2026 · ursprünglich lokal, jetzt unter `rechnungen/` · nur Simulation/Analytik.

**Umgebung** (alle Befehle aus diesem Verzeichnis):

```sh
cd rechnungen/auslegung/verifikation
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../../../code:.
```

**Kennzeichnung:** [R] eigene Rechnung · [Q] Quellenangabe mit Fundstelle · [A] Annahme.

## Unabhängiger Rechenweg (`vk_lib.py`)

Bewusst anders als die Gruppe (`mu_modell.py`: analytische Fourierkoeffizienten + irfft; RK4 mit festem Schritt)
und als `code/linear_solver.py` (FFT des abgetasteten Profils):

1. **Linearer Kontaktast exakt im Zeitbereich.** Zwischen den Knickstellen des Profils (Beginn Halte-/Rückholphase
   je Modul) ist die Last Q(t) = Σ m_j a_j(t) eine Summe von Sinusfunktionen. Partikulärlösung geschlossen
   (komplexe Amplitude / (K − MΩ² + iCΩ)), homogene Lösung geschlossen, periodische Lösung aus der
   Ein-Perioden-Abbildung s(T) = Φ s(0) + p (Schießverfahren). Keine FFT, kein Zeitschritt.
2. **Nichtlinear (einseitiger Kelvin-Voigt-Kontakt wie Engine)** ereignisgesteuert und abschnittsweise exakt:
   Kontaktphase wie (1), Flugphase ẍ = −g − Q/M geschlossen integriert, Moduswechsel per Abtastung (h = 5 µs)
   + brentq auf der geschlossenen Form. λ = exakte Flugzeit / Fensterlänge.
3. **Eigener FFT-Löser** (`fft_linear`, nur für Sweeps), gegen (1) geprüft: max|ΔN| = 5·10⁻⁷ N.
4. Eigene Herleitung: Impulssatz m₀ẍ + Σ m_j(ẍ + a_j) = N − Mg ⇒ Mẍ = N − Mg − Σ m_j a_j(t); in der
   Übertragung steht die Gesamtmasse M (deckt sich mit FV v2.7 Gl. (rahmen) S_true = M z̈₀ + Σ m_k q̈_k, Z. 176) [Q].

Selbsttest (`v0_selbsttest.py` → `v0_selbsttest_ausgabe.txt`) [R]: lineare Lösung = `linear_solver` an 6 Punkten auf
6 Nachkommastellen (u. a. F_min(120°,240°) = 5,330390 N, Periodizitätsfehler < 4·10⁻¹⁸); nichtlinear bei (0°,0°):
λ = 75,787 % / F_max = 41,107 N gegen Engine-Datensatz `data/sweep_19x19.csv` Z. 2: 75,7885 % / 41,1233 N
(Unterschied = Stichprobenkonvention der RK4-Engine).

Eigene Fehlerprüfung: Phasenvorzeichen τ = φ/(360°·f), Modul j wirkt mit a(t − τ_j) wie die Engine (bestätigt durch die
asymmetrischen Sekanten 0,2124/0,1952 N/° und den Punkt (113,684°, 227,368°)); Grad→rad nur in `fft_linear`
(`np.radians`); RTOP = TH·Hub, Hub = Spitze-Spitze; C = 2ζ√(KM); Fensterlängen in Perioden geprüft.
**Prozessfehler (eigener):** Ein Hintergrundlauf wurde einmal im falschen Arbeitsverzeichnis gestartet und legte
`v5A_log.txt` (Fehlermeldung) und eine Kopie von `v5e_einzugsschwelle.py` im Repo-Wurzelverzeichnis an; beide sofort
entfernt bzw. hierher verschoben, `git status` danach leer. Kein `__pycache__` im Repo-Baum.

## Dateien

| Skript | Ausgabe | Inhalt |
|---|---|---|
| `vk_lib.py` | – | Bibliothek (exakter linearer Löser, exakter Ereignis-Integrator, FFT-Löser, Lauftypen) |
| `v0_selbsttest.py` | `v0_selbsttest_ausgabe.txt` | Abgleich mit Repo-Engine/linear_solver |
| `v1_referenz_einzelmodul.py` | `v1_referenz_einzelmodul_ausgabe.txt` | AUS-01, AUS-02 |
| `v2_starr_G_PB1.py` | `v2_starr_G_PB1_ausgabe.txt` | AUS-03, AUS-05 (Zahlen), AUS-07 (starr), AUS-08 (Fenster), AUS-09 |
| `v2b_A4_frequenzgrenzen.py` | `v2b_A4_frequenzgrenzen_ausgabe.txt` | AUS-04 |
| `v3_arbeitspunkte.py` | `v3_arbeitspunkte_ausgabe.txt`, `.csv`, `v3_robustheit_fein.csv` | AUS-10, Robustheit fein, AUS-14 (Kennzahlen) |
| `v3c_phasenebene.py` | `v3c_phasenebene_ausgabe.txt` | AUS-15 |
| `v4_resonanz_G.py` | `v4_resonanz_G_ausgabe.txt`, `.csv` | AUS-17, AUS-07 (Ähnlichkeit), Präreg A5 |
| `v5_nichtlinear.py A/B/C/D` | `v5_nichtlinear_{A,B,C,D}_ausgabe.txt` | AUS-11, AUS-12, AUS-13, Stoßabbildung |
| `v5e_einzugsschwelle.py` | `v5e_einzugsschwelle_ausgabe.txt` | AUS-12 Schwelle ż₀ über ζ und Wurfphase |
| `v6_mu_abgleich_kontaktanteil.py` | `v6_mu_abgleich_kontaktanteil_ausgabe.txt` | AUS-06 (μ ≠ 1), AUS-14 (Kontaktanteil) |
| `v7_triphasik_zulaessig.py` | `v7_triphasik_zulaessig_ausgabe.txt` | Zuordnung 5,33 N/Schiefe zu H(kω); AUS-08 zulässiger ρ-Anteil |
| `v8_geringe_daempfung.py` | `v8_geringe_daempfung_ausgabe.txt` | Robustheit V1–V3 bei ζ = 0,005/0,01 |

Laufzeiten: v3 ≈ 270 s, v5e ≈ 140 s, v3c ≈ 75 s, alle übrigen < 30 s.

---

## AUS-01 · Kennzahlen Referenzsatz — **bestätigt**

Frage: f_n, 2f/f_n, 3f/f_n, F_min(120°,240°), Sekanten. Methode [R]: Formeln; exakte Zeitbereichslösung.
Ergebnis: f_n = 19,7407 Hz; 2f/f_n = 1,0131; 3f/f_n = 1,5197 (f_n/2 = 9,870 Hz, Faktor 3,04); |H| = 1,340/5,030/0,777/0,344;
F_min(120°) = 5,330390 N (2000/Periode und 200 000/Periode gleich); 2°-Sekanten 0,2124/0,1952 N/°; 20°-Sekanten 0,2281/0,1856;
ΔF_Zelt = 4,5627 N. Reproduktion: `timeout 540 python3 v1_referenz_einzelmodul.py`.

## AUS-02 · Einzelmodul Referenzsatz — **bestätigt**

Methode [R]: lineare exakte Lösung (w = (1,0,0)); nichtlinear mit exaktem Ereignis-Integrator, 15 s, Fenster 5–15 s.
Ergebnis: linear F_min = −2,0571 N, F_max = 15,473 N; Grenzen s = 0,7561 (F_min = 0), 0,5671 (25 %), 0,7672 (x_max = 0).
Nichtlinear: s = 0,755 → λ = 0 (F_min 0,0091 N); 0,76 → 1,931 %; 0,80 → 7,920 %; 0,90 → 13,988 %; 1,00 → **17,925 %**
(20 s/letzte 4 s und h/2 gleich). Die 17,90 % der Gruppe/Gegenprobe sind die RK4-Stichprobenkonvention; Unterschied 0,03 Pp.
Kontrolle Einzelmodul(μ = 0,6) = synchron(μ = 0,2): max|ΔN| = 1,8·10⁻¹⁵ N.

## AUS-03 · PB1 — **bestätigt**

Methode [R]: starr, N = Mg + Σ m_j a_j(t) direkt; Harmonische per Quadratur (400 000 Stützstellen).
Ergebnis: F_min(120°) = 5,6452 N, F_min(100°) = 5,1759 N, ΔF_Zelt = 0,4693 N, Δ = 0,1173 N; c(∞) = 3,5826, c(19) = 4,3560;
u_c ≤ 0,0327/0,0269 N (0,422 % Mg). D_k/(Mg·ε) = 0,148324/0,096283/0,182188; D₂ = 0,2924 N ⇒ u_c(N₂) ≤ 0,0204/0,0168 N;
Verhältnis 0,623. Reproduktion: `python3 v2_starr_G_PB1.py`.

## AUS-04 · A4-Frequenzgrenzen — **bestätigt**

Methode [R]: F_min/Mg = 1 − ε(f)·G mit ε ∝ f². Ergebnis: Liftoff/25 %: Schnitt 23,05/19,96 Hz, Einzelmodul 25,10/21,74 Hz,
(0°,180°) 21,79/18,87 Hz, synchron 14,49/12,55 Hz → ganzzahlig 23/19, 25/21, 21/18, 14/12 Hz. Synchrone Reserve 52,4/31,4/19,5 %
bei 10/12/13 Hz; F_max(10 Hz) 7,0752/8,2564/9,1241/12,0163 N. Reproduktion: `python3 v2b_A4_frequenzgrenzen.py`.

## AUS-05 · Massenkonflikt — **bestätigt**

[Q] geöffnet: FV v2.7 Z. 840 („Restmasse $m_0=0$ … für $m_k=M/3$“); Laborplan V1 Z. 58 („je eine Modulmasse (~50–150 g) mit
einigen mm Hub“); AP v2.4 Z. 2038–2041; (Quelle außerhalb des Repositorys) Z. 65 („M = 0,650 kg je Modul · 3 Module · f = 2,2 Hz“).
[R]: ε = 0,275/0,550/0,824 (3×50/100/150 g, Referenzhub, 10 Hz), ΔF_Zelt 0,271/0,541/0,812 N, synchrone Reserve 72,5/45,0/17,6 %;
3×50 g braucht Hub ≥ 13,33 mm; Index-Szenario (M = 1,95 kg, μ = 1, 2,2 Hz, TH-0,65-Profil [A]): ε = 0,0576, ΔF_Zelt = 0,170 N.

## AUS-06 · Lineares μ-Modell und linear_solver — **bestätigt**

Methode [R]: eigene Herleitung (s. o.) und Zeitbereichslösung gegen `linear_solver.solve` in 40 Zufallsfällen
(μ ∈ [0,2; 1], K ∈ [10⁴; 3·10⁶], ζ ∈ {0,02…0,2}, f ∈ {8…14} Hz): max|ΔF_min| = 2,5·10⁻⁶ N, max|ΔF_max| = 1,0·10⁻⁶ N.
H mit Gesamtmasse M, μ skaliert nur die Anregung; Normierung μM·Φ/3 äquivalent. Reproduktion: `python3 v6_mu_abgleich_kontaktanteil.py`.

## AUS-07 · Ähnlichkeitsgesetz — **bestätigt**

[R] G_syn(μ = 1, Hub_ref, 10 Hz, M = 0,65 kg) = G_syn(μ = 0,5, 4·Hub_ref, 5 Hz, M = 1,3 kg) = 1,054606 bei ρ = 0,1, ζ = 0,05;
max|Δg̃| = 8,9·10⁻¹⁶. Starre Grenzwerte (Zeitbereich): G_Einzel 1/3, G_Paar(0) 2/3 (Maximum über Δ = 0…359°), G_syn 1,
G_(0,180) 0,44208 (Gruppe 0,44206), G_Pilot 0,40479, G_Schnitt 0,39535, Ĝ_syn = TH/TF = 1,8571, ΔG 0,15454, Sekanten 0,015427/0,015428 1/°.

## AUS-08 · Zulässiger Bereich — **eingeschränkt**

[R] ε_sig = 0,4763 (identisch mit ε_A4 = 0,47625: das Signalkriterium heißt „Signal mindestens wie im A4-Beispiel“, also eine
Festlegung, kein Ergebnis); ε_max = 0,750 (synchron) bzw. 1,853 (PFLICHT); Hub 6,67–10,50 mm (3×100 g, 10 Hz); K ≥ 923,8·f² N/m
für (ii), K ≥ 10 264·f² N/m für ρ ≤ 0,05. Zulässiger ρ-Anteil (ZUSATZ): 89,2/94,3/100/100 % für ζ = 0,02/0,05/0,1/0,2 – identisch.
Einschränkung: Die Robustheitsaussagen gelten nur für ζ ≥ 0,02; darunter (`v8`, ζ = 0,005/0,01) verletzt V2 die 25-%-Reserve
(nominal 20,0 % bzw. 25,9 %, über K ± 30 % bis 16,2 %), und V1/V3 verfehlen das Signalkriterium auf 5–17 % des K-Bereichs.
Reproduktion: `python3 v2_starr_G_PB1.py; python3 v7_triphasik_zulaessig.py; python3 v8_geringe_daempfung.py`.

## AUS-09 · Zellmodell A2.5 — **bestätigt** (nicht neu)

[R] Mit V1-Masse/Hub, starr: kleinste Zellkraft/statische Zelllast = 0,4285 = 1 − ε für Einzelmodul, synchron, Triphasik, (0°,180°).
ε_max = 1,125 (Paar Δ = 0, Summe/3) und 1,853 (PFLICHT, Summe/3) bestätigt. [Q] Die Kernaussage steht bereits in Präreg-Anhang
A2.5 (Z. 192–203: „Je Zelle gilt dann die Grenze der synchronen Phasung“) und A4; „neu“ trifft nicht zu. „Bis zu etwa 50 %“ ist nur
das Verhältnis V5/V2 (1,016/0,678), keine Schranke. Modulwirkung „im Zellschwerpunkt“ ist für drei getrennte Module nur bei
koaxialer Anordnung möglich [A].

## AUS-10 · Arbeitspunkte V1–V5 — **eingeschränkt**

[R] Exakte Lösung aller 99 Läufe je Fall (15 Fälle): größte Abweichung zur Gruppen-CSV 4,9·10⁻⁷ (Reserven) bzw. 4,8·10⁻⁶ N
(ΔF_Zelt, Zellkraft). Nennwerte damit bestätigt (V1 ζ = 0,05: Reserven 80,9/61,8/42,6/73,8/75,7/76,0 %, ΔF_Zelt 0,560 N,
Sekanten 0,0545/0,0571 N/°, Zellkraft 4,390 N). Robustheit mit feinem K-Raster (Schritt 0,0025 statt 0,05): V1 ΔF_Zelt ≥ 0,501 N
(Gruppe 0,513), V2 Reserve ≥ 28,1 % (28,5) und ΔF ≥ 0,633 N (0,639), V3 ΔF ≥ 0,491 N (0,516), V4 Spitze ∈ {102, 104, 106, 120°}
(Gruppe {106, 120}), V5 ≥ 52,2 % (53,2). Bei ζ < 0,02 (Annahme schwach gedämpfter Zellen) siehe AUS-08. Hub ist Spitze-Spitze;
das AP nennt als „Modellbezug“ r_top ≈ 5 mm (Z. 2043) – Verwechslung würde ε um den Faktor 1/TH = 1,54 erhöhen (V1: ε 0,879,
Reserve ≈ 12 %). Reproduktion: `timeout 540 python3 v3_arbeitspunkte.py`.

## AUS-11 · Nichtlineare Stichprobe — **bestätigt**

[R] Exakter Ereignis-Integrator, Standardstart, 8 s, letzte 5 s: V1 (ζ = 0,05, 13 Läufe), V2 (ζ = 0,02, 4 Läufe), V5: alle Läufe
mit Kontaktast λ = 0, |ΔF_min| ≤ 5,9·10⁻⁷ (V1), 3,4·10⁻⁷ (V2), 1,0·10⁻⁶ N (V5). V5 synchron (linear −0,2221 N): λ = 25,174 %
(Gruppe 25,15 %), F_max 19,22 N. Reproduktion: `python3 v5_nichtlinear.py A`.

## AUS-12 · Hüpfzustände — **eingeschränkt** (Kern bestätigt)

[R] Exakt: V1 synchron, Wurf bei t₀ = 0: ζ = 0,02/0,05: Hüpfen ab ż₀ = 0,30 m/s (λ = 97,95/97,99 %, F_max 483,0/483,7 N, ein Stoß je
Periode, Phase fest); ζ = 0,1: Hüpfen erst ab **0,32 m/s** (bei 0,30 m/s Rückkehr; Gruppe hatte bei ζ = 0,1 nur 0,5 m/s gerechnet),
F_max 486,8 N; ζ = 0,2: Rückkehr bis 0,60 m/s. Schwelle hängt von der Wurfphase ab (ζ = 0,05): t₀/T = 0/0,25/0,5/0,75 →
0,30/**0,24**/0,26/0,60 m/s (Fallhöhe 2,9–18 mm). Zeitschrittfest: h/2 und 40 s unverändert (97,987 %, 483,66 N). Triphasik V1
(ζ = 0,02/0,1) und V2 (ζ = 0,02) mit 0,5 m/s: Rückkehr (bestätigt den Artefaktbefund der Gruppe). Unabhängige Stoßabbildung
(momentaner Stoß, e = exp(−πζ/√(1−ζ²))): 1-periodischer Orbit existiert genau dann, wenn μπ·Hub·f = 0,116 m/s ≥ gT(1−e)/(2(1+e))
= 0,015/0,039/0,077/0,152 m/s (ζ = 0,02/0,05/0,1/0,2) – also für ζ ≤ 0,1, nicht für 0,2; Stoßspitze 485/486/493 N.
Reproduktion: `python3 v5_nichtlinear.py B; python3 v5_nichtlinear.py D; timeout 540 python3 v5e_einzugsschwelle.py`.

## AUS-13 · E1-Spitzen — **eingeschränkt**

[R] Exakt, V1-Parameter synchron, ζ = 0,05: 12/13 Hz λ = 0 (F_max 16,3/17,9 N); **14 Hz: λ = 98,596 %, F_max = 700,5 N (110·Mg),
ein Stoß je zwei Perioden** (h/2: 703,0 N; 30 s: 698,1 N); 16 Hz: λ = 98,23 %, F_max = 1120,8 N (176·Mg). Die Gruppe hatte
589,7 N (T/2000) und 360,0 N (T/4000, Stoßfolge 0,70/1,30 Perioden) bzw. 991 N – andere Attraktoren des Festschritt-RK4.
Größenordnung „einige 10² N“ bestätigt; der Bereich 360–990 N ist zu eng (exakt bis ≈ 1120 N). Reproduktion: `python3 v5_nichtlinear.py C`.

## AUS-14 · Skalierung vs. qualitative Änderung — **eingeschränkt**

[R] Kontaktanteil 1°-Raster (F_min > 0, x_max < 0) aus exakter Einzelmodulantwort: 4,24/48,59/71,84 % für μ = 1/0,5/0,4 – bestätigt.
G120 = 0,138 (Referenz) → 0,2656/0,2628/0,2657 (V1–V3, ζ = 0,05; 0,272 bei ζ = 0,02); γ₁(120°) −0,492/−0,485/−0,492; |H₂| = 1,007/1,006;
für ρ ≤ 0,05, ζ = 0,05: |ΔG_syn| ≤ 1,5 %, |ΔΔG| ≤ 3,3 % – bestätigt. **Fehlzuordnung in der Zusammenfassung der Gruppe:** 5,33 N und die
positive Triphasik-Schiefe sind keine Effekte von 2f ≈ f_n. Am Triphasik-Punkt ist |Φ_k| ≤ 2·10⁻¹⁵ für k ≠ 3m; mit H(2ω) := 1 bleiben
F_min(120°) = 5,330390 N und γ₁ = +0,0668 unverändert (nur die Sekanten fallen auf 0,0458/0,0319 N/°). Verantwortlich sind H(3ω)
(:= 1 → 5,0284 N) und H(6ω) (:= 1 → γ₁ = −0,244), also der weiche Kontakt oberhalb der Resonanz. Reproduktion:
`python3 v6_mu_abgleich_kontaktanteil.py; python3 v7_triphasik_zulaessig.py`.

## AUS-15 · AP-Auslegungsbedingung vs. Präreg — **bestätigt**

[R] Ganze Phasenebene (3°-Raster) bei ζ = 0,05: kleinstes F_min = synchron: V1 2,7184 N (42,6 % Mg), V2 1,9775 N (31,0 %),
V3 2,7879 N (43,7 %); 100 % der Ebene mit F_min ≥ 0,25·Mg. [Q] AP v2.4 Z. 2110–2117 und Laborplan Z. 60 fordern Liftoff in einem
Teil der Phasenlagen; die Präreg verlegt Liftoff bereits nach E1 (höheres f). Reproduktion: `python3 v3c_phasenebene.py`.

## AUS-16 · „Einzelmodulläufe brauchen reduzierten Hub“ — **eingeschränkt**

[R] Summe/3: Einzelmodul-Reserve = 1 − (1 − R_syn)/3 exakt (Einzel(μ) = synchron(μ/3)), V1–V4 77–81 % – bestätigt. Im Zellmodell
A2.5, das §5.3(a) „je Zelle“ verlangt, hat die Zelle unter dem laufenden Modul aber dieselbe Reserve wie synchron (V1 starr 42,85 %).
Dort sind Einzelmodulläufe genauso bindend; die Folgerung „kein reduzierter Hub nötig“ gilt trotzdem, sobald ε ≤ 0,75.

## AUS-17 · §5.3(b) schützt (a) nicht — **bestätigt**

[R] FFT-Sweep ρ = 0,010…1/6, exakt nachgeprüft: max G_syn = 1,811 (ζ = 0,02, ρ = 1/6), 1,284 (0,05), 1,101 (0,1); max G_Schnitt
1,087; Spitze ≠ 120° bei ρ = 0,082–0,084 (102–106°), 0,109–0,114 (100–106°), 0,162–1/6 (100°); ΔG < 90 % in 0,053–0,055,
0,063–0,066, 0,077–0,083, 0,101–0,109, 0,138–0,140, 0,153–0,163 (ζ = 0,02). Präreg A5 nachgerechnet (106°, 5,2096 / 5,1342 N).
Kleinkorrektur: A5 nennt außer 6f = f_n auch 12f = f_n (f_n = 120 Hz, Spitze 106°). Reproduktion: `python3 v4_resonanz_G.py`.

---

## Zusatzbefunde

1. Geringe Dämpfung (ζ ≤ 0,01, [A] nicht gemessen): V2 unzulässig (synchrone Reserve 20,0 % bei ζ = 0,005); V1/V3: ΔF_Zelt < 0,4693 N
   auf 14–17 % des K-Bereichs ± 30 %, Zeltspitze teils bei 110–112° (`v8_geringe_daempfung_ausgabe.txt`). Eine untere Schranke für ζ
   gehört in die Auslegungsregel.
2. „Hub“ ist im Bestand mehrdeutig: Präreg A3 „Hub 7,69 mm“ (Spitze-Spitze), AP Tab. aufbau „Modellbezug r_top ≈ 5 mm“.
3. Die Hüpf-Schwelle ist wurfphasenabhängig (0,24–0,60 m/s bei ζ = 0,05); 0,24 m/s entsprechen 2,9 mm Fallhöhe.
4. E1-Zustände sind bei steifem Kontakt multistabil; Einzelwerte hängen vom Integrator ab, exakt 700 N (14 Hz), 1121 N (16 Hz).
