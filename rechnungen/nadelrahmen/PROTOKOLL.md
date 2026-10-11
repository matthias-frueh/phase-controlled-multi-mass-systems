# Prüfgruppe „nadelrahmen“ – Dreimassenkörper im Sechs-Nadel-Messrahmen (Vollmodell)

Stand 11.10.2026 · neue Rechengruppe, nicht Teil der Gesamtprojektanalyse vom 1./2. Oktober 2026 ·
Kennzeichnung: **[R]** eigene Rechnung, **[Q]** Quellenangabe, **[A]** Annahme, **[N]** neue Präzisierung vom 11.10.2026.
Alles ist Simulation oder Analytik, keine Messdaten, keine gebaute Apparatur. Das Konzept dazu steht in
[`docs/konzepte/nadelrahmen_dreimassenkoerper_2026-10.md`](../../docs/konzepte/nadelrahmen_dreimassenkoerper_2026-10.md).

**Anlass [Q].** Festhaltung des Autors vom 11.10.2026: Der Dreimassenkörper (oder eine Modellvariante) wird in einen
Rahmen mit sechs Messpunkten eingebettet (Nord, Süd, Ost, West, oben, unten). Messnadeln halten den Körper an
Fixierstellen rundum fest; jede Nadel hat genau eine Kontaktfläche zu ihrer eigenen Messschnittstelle. Statt einer
Einzelauflage wird rundum gemessen (Vollmodellmessung). Die Wahl zwischen Einspannen und kinematischer Lagerung
bleibt offen (Festhaltung vom 11.10.2026, Quelle außerhalb des Repositorys).

## Dateien und Reproduktion

Alle Befehle aus `rechnungen/nadelrahmen/` mit

```
PY="PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../../code python3"
```

| Skript | Inhalt | Ausgabe | Laufzeit |
|---|---|---|---|
| `nr_modell.py` | gemeinsames Modell: sechs Nadeln, Matrix G, Rang, Nullraum, Formschluss (lineares Programm), 6-FG-Körper mit drei Modulen, Lösung je Harmonischer | – | – |
| `n1_geometrie.py` | Rang, Paarstruktur, Statik der Belegung B, Formschluss | `n1_geometrie_ausgabe.txt` | ≈ 10 s |
| `n2_vollmodell.py` | Moduldyname und Auswahlregeln, Basislinie, Nadelkräfte B und C, Zeltkurve, Modulzeiger | `n2_vollmodell_ausgabe.txt` | < 5 s |
| `n3_rahmendynamik.py` | Eigenmoden, Übertragung T(k·f), Übersprechen durch Schwerpunkthöhe, Auslegungsregel | `n3_rahmendynamik_ausgabe.txt` | < 5 s |
| `n4_nebenschluss.py` | ungemessene Querkräfte der Nadeln (Nadelregel) | `n4_nebenschluss_ausgabe.txt` | < 5 s |
| `verifikation/v1_zeitbereich.py` | eigene Zeitbereichsintegration (DOP853) gegen die Frequenzbereichslösung | `verifikation/v1_zeitbereich_ausgabe.txt` | ≈ 70 s |
| `verifikation/v2_bilanz_rang.py` | Basislinie und Randterm aus Modulbahnen, Rang und Formschluss in rationaler Arithmetik | `verifikation/v2_bilanz_rang_ausgabe.txt` | < 10 s |

Beispiel: `cd rechnungen/nadelrahmen && eval $PY n2_vollmodell.py`; Gegenprüfung aus `verifikation/` mit
`PYTHONPATH=../../../code`. Getestet mit Python 3.13, numpy 2.5, scipy 1.18.

**Bezeichnungen.** Koordinaten rechtshändig: x nach Ost, y nach Nord, z nach oben; Bezugspunkt O = Rahmenmitte,
ortsfest. Nadeln in der Reihenfolge Nord, Süd, Ost, West, oben, unten; n_j = Druckrichtung auf den Körper,
λ > 0 Druck, λ < 0 Zug. Lastvektor (Dyname) w = (F; τ_O) = G·λ mit Spalten G_jc = (e_jc; r_j × e_jc).
Belegungen [A]: Fixierstellen im Abstand D = 0,15 m von O, Versatz A = 0,04 m. **A** zentral, eine axiale Komponente
je Nadel; **B** versetzt, zyklisch gegensinnig (Ost/West ±A in y, Nord/Süd ±A in z, oben/unten ±A in x), eine
axiale Komponente; **B2** andere zyklische Zuordnung; **Bg** gleichseitig versetzt; **C** zentral, drei
Kraftkomponenten je Nadel (an der Fixierstelle fest, an der Schnittstelle kugelgelenkig); **D7**, **D12** sieben bzw.
zwölf Druckspitzen. Körper [A]: V1-Kandidat aus `code/auslegung.py` (3 × 100 g, Hub 8 mm, Träger 0,35 kg, 10 Hz,
Egg-Profil) in Lage G0 (Module auf R_m = 100 mm bei 0°, 120°, 240°), Trägerträgheit isotrop mit ρ₀ = 80 mm,
Schwerpunkt in O, wo nicht anders angegeben. Nadelsteifigkeit axial k_a = 10⁶ N/m, quer k_t (C); Dämpfung
steifigkeitsproportional mit ζ = 0,02 an der tiefsten Mode. Phasenlagen: T = (0°, 120°, 240°), Z = (0°, 110°, 240°),
S = (0°, 0°, 0°), E1 = nur Modul 1.

**Modell [R].** Kleine Bewegung x = (u; θ) des Körpers im starren, ortsfesten Rahmen:
M6·ẍ + C·ẋ + K·x = w_g − w_mod(t), K = Σ k_jc G_jc G_jcᵀ, C = β·K, w_mod = Σ_i m_i s̈_i (e_z; R_i × e_z).
Gemessener Lastvektor w_mess = G·λ = −w_g + w_mod + M6·ẍ; starrer Grenzfall w_mess = −w_g + w_mod.
Je Harmonischer λ_k = k_jc(1 + iω_kβ) G_jcᵀ Z_k⁻¹ w_mod,k mit Z_k = K − ω_k² M6 + iω_kβK. Gültig, solange jede Nadel
in ihrem Kontaktzustand bleibt; geometrische Steifigkeit aus Vorspannung und Gewicht sowie die Nadelmassen sind
vernachlässigt [A].

---

## NR-01 · Rang und Paarstruktur der sechs Nadeln

**Frage.** Welche Lastkomponenten erfassen sechs Nadeln (eine je Fläche), und wo bleibt eine Vorspannung?

**Ergebnis [R]** (`n1_…`, Abschnitte 1–2; exakt bestätigt in `v2_…`, Teil B).

| Belegung | gemessene Komponenten | Rang | Nullraum | Kondition l_ref = A / D |
|---|---|---|---|---|
| A zentral, axial | 6 | 3 | 3 | ∞ |
| B versetzt (zyklisch) | 6 | 6 | 0 | 1,000 / 3,750 |
| B2 versetzt (andere Zuordnung) | 6 | 6 | 0 | 1,000 / 3,750 |
| Bg gleichseitig versetzt | 6 | 3 | 3 | ∞ |
| C zentral, drei Kraftkomponenten | 18 | 6 | 12 | 3,062 / 1,225 |

- Gegenüberliegende Nadeln bilden ein Paar. Die **Differenz** ist immer die Kraft längs der Achse
  (F_x = q_West − q_Ost usw.).
- Bei zentralen Wirkungslinien (A) ist die **Summe** frei: Sie ist die Vorspannung des Paars (Nullraum, drei
  Zustände). Momente sieht A nicht (blinde Richtungen M_x, M_y, M_z).
- Bei versetzten Wirkungslinien (B) ist die Summe ein **Moment**: M_x = A·(q_Nord + q_Süd),
  M_y = A·(q_oben + q_unten), M_z = A·(q_Ost + q_West). Ein Nullraum bleibt nicht.
- Gleichseitig versetzt (Bg) liegen beide Nadeln eines Paars auf einer Wirkungslinie: Rang 3 wie zentral.

**Bewertung [N].** Mit sechs einkomponentigen Nadeln gilt Rang + Nullraum = 6: alle sechs Komponenten (Rang 6)
und Vorspannung (Nullraum > 0) schließen sich aus. Das bestätigt den Nachtrag vom 11.10.2026, §3, für die konkrete
Sechs-Nadel-Anordnung.

## NR-02 · Statische Nadellasten der statisch bestimmten Belegung B

**Ergebnis [R]** (`n1_…`, Abschnitt 3). Unter dem Gewicht (M g = 6,3765 N):

| Schwerpunkt r_cm | Nord | Süd | Ost | West | oben | unten |
|---|---|---|---|---|---|---|
| in O | 0 | 0 | 0 | 0 | −3,188 (Zug) | +3,188 |
| x_cm = −A = −40 mm | 0 | 0 | 0 | 0 | 0 | +6,377 |
| y_cm = +10 mm | +0,797 | +0,797 | 0 | 0 | −3,188 | +3,188 |

**Bewertung.** Liegt der Schwerpunkt in O, muss die obere Nadel die Hälfte des Gewichts als Zug tragen, weil das
Paar oben/unten zugleich M_y trägt. Mit dem Schwerpunkt auf der Wirkungslinie der unteren Nadel ist sie lastfrei.
Die Schwerpunktlage bestimmt die statischen Nadellasten vollständig; die Messung in R1 ist damit eine Wägung von M
und r_cm (Prüfung von G).

## NR-03 · Formschluss: Sechs Druckspitzen halten keinen Körper

**Frage.** Kann ein Körper mit sechs Nadeln gehalten werden, die nur drücken (Kontaktfläche ohne Zug, ohne Reibung)?

**Ergebnis [R]** (`n1_…`, Abschnitt 4; `v2_…`, Teil C).
- Satz: Die Kontaktrichtungen müssen den R⁶ positiv aufspannen. Das verlangt Rang 6 und einen Nullraumvektor mit
  lauter positiven Einträgen. Sechs Vektoren können das nicht: Wären sie aufspannend, wären sie eine Basis; aus
  −Σ G_j = Σ c_j G_j mit c_j ≥ 0 folgte Σ(1 + c_j) G_j = 0, also lineare Abhängigkeit. Mindestens sieben sind nötig.
- Zufallsstichprobe (2000 Lagen, eine Nadel je Fläche): Rang 6 in 2000/2000, Formschluss in 0/2000. Mit einer
  siebten Nadel auf zufälliger Fläche: Formschluss in 180/2000.
- Beispiel D7 (die sechs Nadeln, versetzt, und eine zweite Nadel unten): Rang 6, Nullraum 1, einziger
  Vorspannzustand (1, 1, 1, 1, 2, 1, 1) – alle positiv, Formschluss (LP-Reserve t* = 0,125; exakt bestätigt).
- D12 (zwei Nadeln je Fläche, ±A): Rang 6, Nullraum 6, (1, …, 1) im Nullraum, Formschluss.

**Bewertung [N].** Sechs Nadeln, die den Körper rundum **einspannen**, brauchen entweder zugfeste Verbindungen
(Belegung B, statisch bestimmt) oder Schnittstellen, die auch die Querkräfte übertragen und messen (Belegung C).
Mit reinen Druckspitzen sind mindestens sieben nötig. Haftreibung an Druckspitzen hält den Körper zwar, trägt dann
aber ungemessene Querkräfte (NR-07).

## NR-04 · Moduldyname: Auswahlregeln aller sechs Komponenten

**Ergebnis [R]** (`n2_…`, Abschnitt 2). Amplituden 2|w_k| im starren Grenzfall (= gemessener Lastvektor minus
Basislinie), V1-Kandidat. Profilharmonische je Modul A_k = 15,564 / 5,129 / 2,213 / 0,335 / 0,460 / 0,415 m/s²
(k = 1 … 6).

| Phasenlage | F_z [N] | M_x = M_y [N·m] | F_x, F_y, M_z |
|---|---|---|---|
| T | k = 3: 0,664; k = 6: 0,124; sonst 0 | k = 1: 0,2335 (links umlaufend); k = 2: 0,0769 (rechts); k = 4: 0,0050 (links); k = 5: 0,0069 (rechts); k ≡ 0 (mod 3): 0 | 0 |
| Z | k = 1: 0,271; k = 2: 0,178; k = 3: 0,644 | R+₁ = 0,2327, Gegenkomponente R−₁ = 0,0136 | 0 |
| S | k = 1: 4,669; k = 2: 1,539; k = 3: 0,664 | 0 | 0 |
| E1 | k = 1: 1,556 | nur M_y, k = 1: 0,156 (R+ = R−: linear) | 0 |

**Bewertung.** Am Triphasik-Punkt trägt F_z nur die Vielfachen von 3, das Kippmoment genau die übrigen Ordnungen
(KM-03 [Q], hier im gehaltenen Körper). Bei senkrecht geführten Modulen sind F_x, F_y und M_z im starren Grenzfall
**zeitlich identisch null** (max. 0 in allen Phasenlagen): dynamische Nullkanäle. Ein Signal dort zeigt Querbewegung
der Module, Führungsfehler oder Rahmenkopplung (NR-08).

## NR-05 · Basislinie, Randterm und Einzelnadel-Nulltest

**Ergebnis [R]** (`n2_…`, Abschnitt 3; `v2_…`, Teil A).
- Zeitmittel über ganze Perioden: ⟨w_mess⟩ = (M g e_z; r_cm × M g e_z). Mit r_cm = (5, −3, 20) mm:
  M_x = −0,01913 N·m, M_y = −0,03188 N·m, F_z = 6,3765 N. Gegenprüfung mit anderer Modullage (G60h, 20 mm über O)
  und Schwerpunktversatz aus den Modulbahnen: Abweichung ≤ 1,8·10⁻¹⁰.
- Teilfenster (3,37 Perioden): Das Mittel weicht genau um den Randterm (P(t₁) − P(t₀))/T_W bzw.
  (H_O(t₁) − H_O(t₀))/T_W ab (Differenz ≤ 3·10⁻¹⁴); bei S sind das −0,272 N in F_z, bei T −6,7 mN in F_z und
  +11,2 mN·m in M_y.
- Einzelnadel-Mittel der Belegung B: in T, Z und S gleich (Differenz ≤ 1,0·10⁻¹⁰ N) und gleich G⁻¹·Basislinie.

**Bewertung [N].** Die Erhaltungsgröße „Zeitmittel = Mg“ wird im Rahmen zu sechs Nulltests (Kräfte und Momente;
für Momente mit der Basislinie r_cm × M g e_z, Nachtrag §4). Bei senkrechter Modulbewegung hängt die Basislinie
nicht von der Phasenlage ab. In der statisch bestimmten Belegung B ist zusätzlich jede Nadel ein eigener Nulltest
(Δ⟨q_j⟩ = 0 zwischen Zuständen). Ausgewertet werden ganze Perioden; sonst gehört der Randterm zur Basislinie.

## NR-06 · Nadelkräfte, Vorspannbedarf, Zeltkurve und Modulzeiger

**Belegung B, starr [R]** (`n2_…`, Abschnitt 4):

| Nadel | T: min … max [N] | S: min … max [N] | Inhalt am Triphasik-Punkt |
|---|---|---|---|
| Nord, Süd | −3,401 … +3,401 | 0 | ∓F_y/2 + M_x/(2A): nur k ≢ 0 (mod 3) (2,918 / 0,962 N bei k = 1/2) |
| Ost, West | 0 | 0 | ∓F_x/2 + M_z/(2A): Nullkanäle |
| oben | −7,346 … −1,005 | −6,572 … −1,366 | −F_z/2 + M_y/(2A): beide Klassen |
| unten | −0,397 … +5,570 | +1,366 … +6,572 | +F_z/2 + M_y/(2A) |

Nord, Süd und unten wechseln am Triphasik-Punkt das Vorzeichen, oben ist immer auf Zug: B braucht zugfeste Nadeln.

**Belegung C, starr [R]** (`n2_…`, Abschnitt 5): Bei k_t/k_a = 0,02 trägt das Paar oben/unten 96,15 % des
Gewichts axial, 3,85 % gehen über die Querkomponenten der Seitennadeln (bei 0,1: 83,3 % / 16,7 %). Nötige
Vorspannung, damit kein axialer Kontakt auf Zug geht: 3,34 N (T), 6,32 N (S) bei k_t/k_a = 0,02. Mit reibschlüssiger
Querkraft (μ_s = 0,2 angenommen [A]): 5,9 N (T) bzw. 6,3 N (S). Mit gefangenem Kugelgelenk entfällt beides; die
Vorspannung ist dann frei wählbar (Nullraum).

**Zeltkurve im Rahmen [R]** (`n2_…`, Abschnitt 6): F_z,min entlang φ₃ = 240°: Spitze 5,4989 N bei 120°, Spannweite
über 100°–140° 0,5632 N (starr); mit Rahmendynamik B (k_a = 10⁶ N/m) 5,4206 N und 0,5601 N. Synchron
F_z,min = 2,7323 N (ε = 0,5715): Der V1-Kandidat bleibt überall im Kontaktast. Die Gegenkomponente R−₁ des
Kippmoments wächst linear vom Triphasik-Punkt weg (0,0027 N·m je 2°).

**Modulzeiger [R]** (`n2_…`, Abschnitt 7): Aus (F_z, M_x, M_y) folgen je Harmonischer die drei Modulzeiger
(Kondition 1,414 in G0). Eine Störung von +1 % Masse und +1° Phase an Modul 2 wird exakt zurückgerechnet (Betrag
1,01000, Phase −k·1,000°).

**Bewertung.** Im starren Grenzfall ist F_z(t) = M g + Σ m_i s̈_i(t) dieselbe Funktion wie N(t) einer starren
Auflage, solange diese nicht abhebt (`linear_solver.py`, starre Auflage [Q]). Die Spannweite des Zelts ist starr
0,5632 N, für den Kandidaten auf seiner Auflage mit K = 1,5·10⁶ N/m 0,5603 N (`code/auslegung.py --candidate` [Q])
und im Rahmen B mit k_a = 10⁶ N/m 0,5601 N; die Unterschiede sind die jeweilige Übertragung. Der Rahmen setzt die
lineare Lösung dort fort, wo eine Auflage abheben würde (F_z < 0 trägt die Nadel oben). Zusätzlich liefert er
Moment und Modulzeiger in jedem Lauf (vgl. KM-10 [Q]).

## NR-07 · Nadelregel: ungemessene Querkräfte

**Frage.** Was geschieht, wenn eine Nadel mehr Komponenten überträgt, als ihre Schnittstelle misst?

**Ergebnis [R]** (`n4_…`). Belegung B mit ungemessener Quersteifigkeit k_q = κ·k_a je Nadel:

| κ | ΔF_z/(M g) statisch | ΔM_y/M_y statisch | Fehler F_z,3 (T) | Fehler R+₁ (T) |
|---|---|---|---|---|
| 10⁻⁶ | −2,0·10⁻⁶ | −2,9·10⁻⁵ | 2,0·10⁻⁶ | 2,9·10⁻⁵ |
| 10⁻⁴ | −2,0·10⁻⁴ | −2,9·10⁻³ | 2,0·10⁻⁴ | 2,9·10⁻³ |
| 10⁻² | −1,96·10⁻² | −0,224 | 1,96·10⁻² | 0,224 |

Faustformel: Kraftfehler ≈ 2κ, Momentenfehler ≈ κ·(1 + 2(D/A)²) = 29,1·κ, weil zwei Nadelpaare quer mit dem Hebel D,
axial aber nur ein Paar mit dem Hebel A trägt. In der zentralen Belegung A gehen die Momente vollständig in
ungemessene Pfade (gemessener Anteil 0).

**Bewertung [N].** Jede Nadel ist genau ein Lastpfad; was sie überträgt, muss ihre Schnittstelle messen. Sonst
entsteht innerhalb der Nadel ein ungemessener Parallelpfad, den der Nulltest ⟨F_z⟩ = Mg (und in B jede Nadel)
direkt anzeigt. Für Momente ist die Anforderung an die Querweichheit um (D/A)² schärfer als für Kräfte.

## NR-08 · Rahmendynamik

**Ergebnis [R]** (`n3_…`; Zeitbereich in `v1_…`).

| Fall | Eigenfrequenzen [Hz] |
|---|---|
| B, k_a = 10⁶ N/m | 124,4 (θ_z), 147,2 (θ_x, θ_y), 279,2 (dreifach, Verschiebungen) |
| B, k_a = 10⁷ N/m | 393,3, 465,5 (2×), 882,8 (3×) |
| C, k_a = 10⁶, k_t = 2·10⁴ N/m | 93,3, 110,4 (2×), 284,7 (3×) |
| C, k_a = 10⁶, k_t = 10⁵ N/m | 208,6, 246,9 (2×), 305,8 (3×) |

- Die Drehmoden der Belegung B hängen nur am Hebel A (Drehsteifigkeit 2·k_a·A²): A = 0,02 / 0,04 / 0,08 m gibt
  62 / 124 / 249 Hz (tiefste Mode, k_a = 10⁶ N/m).
- Übertragung |T_ii(k·f)| (B, k_a = 10⁶): k = 1: 1,0013 (Kräfte), 1,0046 (M_x, M_y); k = 2: 1,0052 / 1,0188;
  k = 6: 1,048 / 1,199 (M_z 1,303). Bei k_a = 10⁷: k = 2: 1,0005 / 1,0018; k = 6: 1,0046 / 1,0169.
- Übersprechen: mit Schwerpunkt in O null (≤ 10⁻¹⁶); mit Schwerpunkt 16,2 mm über O entstehen F_x, F_y von
  3,0 / 4,1 mN (k = 1 / 2, k_a = 10⁶) bzw. 0,30 / 0,40 mN (10⁷).
- Nadelkräfte mit Dynamik gegen starr (T): bis 0,21 N (10⁶) bzw. 0,069 N (10⁷).
- Ohne Korrektur verlangt |T − 1| ≤ ε bis k_max = 6 bei 10 Hz f₁ ≥ 600 Hz (ε = 1 %) bzw. 1,9 kHz (ε = 0,1 %).

**Bewertung.** Die Nadeln sind der Kontakt des Rahmens: Ihre Steifigkeit und der Hebel A setzen die Moden, die
Übertragung je Harmonischer und damit die Kalibrieranforderung. Die Kippkanäle liegen der tiefsten Mode am nächsten.
Die Rahmenübertragung gehört wie die Kontaktübertragung der Auflage zur Versuchskonfiguration (H_cal(f), dynamische
Kalibrierung mit Anregung an mehreren Orten, KM-05 [Q]).

---

## Gegenprüfung

- `v1_zeitbereich.py`: eigene Geometrietabelle, eigene Massenmatrix (Summe räumlicher Trägheiten), Egg-Beschleunigung
  direkt aus der Formel, Integration mit DOP853 (rtol 10⁻¹¹) über 30 Perioden. Abweichung zur Frequenzbereichslösung
  bei n = 4000 / 16 000 / 64 000 Stützstellen je Periode: dynamisch 1,8·10⁻⁵ / 1,1·10⁻⁶ / 7,1·10⁻⁸ N, starr
  9,2·10⁻⁵ / 5,4·10⁻⁶ / 5,6·10⁻⁷ N. Die Restabweichung ist der Abbruch der Profilreihe (fällt etwa wie 1/n²);
  `nr_modell.py` rechnet mit n = 16 000 (wie `N_FEIN` in `code/auslegung.py`). **Bestätigt.**
- `v2_bilanz_rang.py`: Basislinie und Randterm aus Impuls- und Drallbilanz im Zeitbereich (NR-05), Rang und
  Nullraum in rationaler Arithmetik für A, B, B2, Bg, C, D7, D12 (gleich `nr_modell`), Formschluss von D7 und D12
  exakt, Vorspannung der Belegung C exakt im Nullraum. **Bestätigt.**
- Die Faustformeln von NR-07 stimmen mit der Rechnung überein (2,000·κ und 29,12·κ bei κ ≤ 10⁻⁵).

## Grenzen

- Geometrie, Massen, Trägheiten, Nadelsteifigkeiten, Dämpfung und μ_s sind Annahmen [A]; keine CAD-Daten.
- Rahmen starr und ortsfest; Rahmenmoden und Fundament nicht modelliert. Nadelmassen, Nadel-Eigenmoden und
  geometrische Steifigkeit aus Vorspannung und Gewicht nicht modelliert.
- Linear: Kontaktöffnen an einer Nadel, Mikroschlupf und Hysterese an Reibkontakten sind nicht modelliert; NR-06
  gibt nur die Grenzen an, ab denen sie auftreten.
- Module senkrecht geführt; Querbewegung der Module, Antriebsrückwirkung, Kabel und Zuleitungen als Parallelpfade
  nicht modelliert.
- Nur der V1-Kandidat als Modellvariante gerechnet; andere Prototypen über die Parameter von `Koerper`.

## Offene Punkte

- Ausführung B oder C (oder ≥ 7 Druckspitzen) – bewusst offen (Festhaltung 11.10.2026).
- Reale Fixierstellen, Versatz A, Nadelbauart (Gelenke, Quersteifigkeit κ, Zugfestigkeit), Schnittstellen
  (Komponentenzahl, Band, Nennlast) und Rahmensteifigkeit.
- Ob und wie die einseitige Kontaktphysik der Linie A im Rahmen weiter untersucht wird (Modellvariante „einseitige
  Nadel unten“) – Entscheidung des Autors.
