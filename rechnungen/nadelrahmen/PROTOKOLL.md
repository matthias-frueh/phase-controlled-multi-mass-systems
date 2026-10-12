# Prüfgruppe „nadelrahmen“ – Dreimassenkörper im Sechs-Nadel-Messrahmen (Vollmodell)

Stand 11.10.2026 · neue Rechengruppe, nicht Teil der Gesamtprojektanalyse vom 1./2. Oktober 2026 ·
Kennzeichnung: **[R]** eigene Rechnung, **[Q]** Quellenangabe, **[A]** Annahme, **[N]** neue Präzisierung vom 11.10.2026.
Alles ist Simulation oder Analytik, keine Messdaten, keine gebaute Apparatur; Konzept- und Modellarbeit zu AP-27.
Das Konzept dazu steht in
[`docs/konzepte/nadelrahmen_dreimassenkoerper_2026-10.md`](../../docs/konzepte/nadelrahmen_dreimassenkoerper_2026-10.md).

**Anlass [Q].** Festhaltung des Autors vom 11.10.2026: Der Dreimassenkörper (oder eine Modellvariante) wird in einen
Rahmen mit sechs Messpunkten eingebettet (Nord, Süd, Ost, West, oben, unten). Messnadeln halten den Körper an
Fixierstellen rundum fest; jede Nadel hat genau eine Kontaktfläche zu ihrer eigenen Messschnittstelle. Statt einer
Einzelauflage wird rundum gemessen (Vollmodellmessung). Kinematische Lagerung und Einspannung bleiben beide als
anwendungsabhängige Möglichkeiten offen; eine Bauentscheidung steht nicht an (Vorgabe des Autors vom 11.10.2026,
Quelle außerhalb des Repositorys).

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
| `n3_rahmendynamik.py` | Halterungsmoden, Übertragung T(k·f), Übersprechen durch Schwerpunkthöhe, Auslegungsregel | `n3_rahmendynamik_ausgabe.txt` | < 5 s |
| `n4_nebenschluss.py` | ungemessene Querkräfte der Nadeln (Nadelregel) | `n4_nebenschluss_ausgabe.txt` | < 5 s |
| `n5_kalibrierrang.py` | Rang tatsächlicher Kalibrierlasten (Eigengewicht, Gewichtsstücke, Rahmenlagen, Umlenkrollen) | `n5_kalibrierrang_ausgabe.txt` | < 1 s |
| `verifikation/v1_zeitbereich.py` | eigene Zeitbereichsintegration (DOP853) gegen die Frequenzbereichslösung | `verifikation/v1_zeitbereich_ausgabe.txt` | ≈ 70 s |
| `verifikation/v2_bilanz_rang.py` | Basislinie und Randterm aus Modulbahnen, Rang und Formschluss in rationaler Arithmetik | `verifikation/v2_bilanz_rang_ausgabe.txt` | < 10 s |

Beispiel: `cd rechnungen/nadelrahmen && eval $PY n2_vollmodell.py`; Gegenprüfung aus `verifikation/` mit
`PYTHONPATH=../../../code`. Getestet mit Python 3.13, numpy 2.5, scipy 1.18.

**Bezeichnungen.** Koordinaten rechtshändig: x nach Ost, y nach Nord, z nach oben; Bezugspunkt O = Rahmenmitte,
ortsfest. Nadeln in der Reihenfolge Nord, Süd, Ost, West, oben, unten; n_j = Druckrichtung auf den Körper,
λ > 0 Druck, λ < 0 Zug. Lastvektor (Dyname) w = (F; τ_O) = Σ_j [Σ_c G_jc·λ_jc + (0; τ^c_j)] mit Spalten
G_jc = (e_jc; r_j × e_jc) für jede übertragene Kraftkomponente und dem freien Kontaktmoment τ^c_j (Formelverzeichnis
v2.7 [Q]); im Modell ist τ^c_j = 0 [A]. Belegungen [A]: Angriffspunkte r_j im Abstand D = 0,15 m von O (bei A und B
die Fixierstellen auf der Wirkungslinie, bei C die Kugelgelenkmitten an der Schnittstelle), Versatz A = 0,04 m.
**A** zentral, eine axiale Komponente je Nadel; **B** versetzt, zyklisch gegensinnig (Ost/West ±A in y, Nord/Süd ±A
in z, oben/unten ±A in x), eine axiale Komponente; **B2** andere zyklische Zuordnung; **Bg** gleichseitig versetzt
(alle drei Paare); **C** zentral, drei Kraftkomponenten je Nadel (an der Fixierstelle fest, an der Schnittstelle
kugelgelenkig); **D7** sieben Druckspitzen mit eigenem Versatzmuster (50 mm; nicht die Lagen von B), **D12** zwölf
Druckspitzen (zwei je Fläche, ±A). Körper [A]: V1-Kandidat aus `code/auslegung.py` (3 × 100 g, Hub 8 mm, Träger
0,35 kg, 10 Hz, Egg-Profil) in Lage G0 (Module auf R_m = 100 mm bei 0°, 120°, 240°), Trägerträgheit isotrop mit
ρ₀ = 80 mm, Schwerpunkt in O, wo nicht anders angegeben. Nadelsteifigkeit axial k_a = 10⁶ N/m, quer k_t (C); Dämpfung
steifigkeitsproportional mit ζ = 0,02 an der tiefsten Mode. Rahmenstruktur und Fundament starr und ortsfest;
**Halterungsmoden** heißen die Eigenmoden des Körpers auf den elastischen Nadeln. Phasenlagen: T = (0°, 120°, 240°),
Z = (0°, 110°, 240°), S = (0°, 0°, 0°), E1 = nur Modul 1.

**Modell [R].** Kleine Bewegung x = (u; θ) des Körpers in der starren, ortsfesten Rahmenstruktur:
M6·ẍ + C·ẋ + K·x = w_g − w_mod(t), K = Σ k_jc G_jc G_jcᵀ, C = β·K, w_mod = Σ_i m_i s̈_i (e_z; R_i × e_z).
Übertragener Lastvektor G·λ = −w_g + w_mod + M6·ẍ, starrer Grenzfall −w_g + w_mod. Gemessen wird w_mess = G_m·λ_m
(nur gemessene Komponenten); w_mess = G·λ, solange keine Nadel ungemessene Komponenten überträgt (NR-07).
Je Harmonischer λ_k = k_jc(1 + iω_kβ) G_jcᵀ Z_k⁻¹ w_mod,k mit Z_k = K − ω_k² M6 + iω_kβK. Gültig, solange jede Nadel
in ihrem Kontaktzustand bleibt; geometrische Steifigkeit aus Vorspannung und Gewicht, die Nadelmassen und freie
Kontaktmomente sind vernachlässigt [A].

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

- Gegenüberliegende Nadeln bilden ein Paar. Bei rein axial übertragenden Nadeln (A, B) ist die **Differenz** die
  Kraft längs der Achse (F_x = q_West − q_Ost usw.); in C tragen die Querkomponenten der übrigen Nadeln mit (NR-06).
- Bei zentralen Wirkungslinien (A) ist die **Summe** frei: Sie ist die Vorspannung des Paars (Nullraum, drei
  Zustände). Momente sieht A nicht (blinde Richtungen M_x, M_y, M_z).
- Bei versetzten Wirkungslinien (B) ist die Summe ein **Moment**: M_x = A·(q_Nord + q_Süd),
  M_y = A·(q_oben + q_unten), M_z = A·(q_Ost + q_West). Ein Nullraum bleibt nicht.
- Gleichseitig versetzt (Bg) liegen beide Nadeln eines Paars auf einer Wirkungslinie: Rang 3 wie zentral.
  Teilweise gleichseitig (übrige Paare wie B): Jedes gleichseitige Paar kostet ein Moment, Rang 6 / 5 / 4 / 3 bei
  0 / 1 / 2 / 3 gleichseitigen Paaren, für jede Wahl der Paare.

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
Paar oben/unten zugleich M_y trägt. Mit dem Schwerpunkt auf der Wirkungslinie der unteren Nadel ist die obere
lastfrei. Die Schwerpunktlage bestimmt die statischen Nadellasten vollständig. Bei bekanntem G ist die Messung in R1
damit eine Wägung von M und der waagerechten Schwerpunktlage (x_cm, y_cm); z_cm geht in einer Rahmenlage nicht ein.
Als Prüfung von G (bei unabhängig bekanntem M und r_cm) deckt sie nur diese eine Lastrichtung ab (Rang 1, NR-09).

## NR-03 · Formschluss: Sechs reibungsfreie Druckspitzen halten einen starren Körper nicht gegen beliebige Lasten

**Frage.** Kann ein starrer Körper mit sechs Nadeln gegen beliebige Lasten gehalten werden (vollständige räumliche
Halterung), wenn die Nadeln nur längs ihrer Achse drücken (Punktkontakt ohne Zug, ohne Reibung)?

**Ergebnis [R]** (`n1_…`, Abschnitt 4; `v2_…`, Teil C).
- Satz (Formschluss erster Ordnung): Die Kontaktrichtungen müssen den R⁶ positiv aufspannen. Das verlangt Rang 6 und
  einen Nullraumvektor mit lauter positiven Einträgen. Sechs Vektoren können das nicht: Wären sie aufspannend, wären
  sie eine Basis; aus −Σ G_j = Σ c_j G_j mit c_j ≥ 0 folgte Σ(1 + c_j) G_j = 0, also lineare Abhängigkeit.
  Mindestens sieben sind nötig.
- Zufallsstichprobe (2000 Lagen, eine Nadel je Fläche): Rang 6 in 2000/2000, Formschluss in 0/2000. Mit einer
  siebten Nadel auf zufälliger Fläche: Formschluss in 180/2000.
- Beispiel D7 (sechs Nadeln mit eigenem Versatzmuster – 50 mm, Nord/Süd in x und z, Ost/West und oben in y – und
  eine zweite Nadel unten, die beiden unteren bei ±50 mm in x; nicht die Lagen der Belegung B; Lagen in `n1_…`,
  Abschnitt 4): Rang 6, Nullraum 1, einziger Vorspannzustand (1, 1, 1, 1, 2, 1, 1) – alle positiv, Formschluss
  (LP-Reserve t* = 0,125; exakt bestätigt).
- D12 (zwei Nadeln je Fläche, ±A): Rang 6, Nullraum 6, (1, …, 1) im Nullraum, Formschluss.
- Belegung B mit einer siebten achsparallelen Nadel (Gitter 7 × 7 auf jeder Fläche): Formschluss in 0/294. Grund: In
  G_B⁻¹ hängt jedes Paar nur an einer Kraft und einem Moment (Abschnitt 2); eine achsparallele siebte Nadel erzeugt
  für mindestens ein Paar keines von beiden, und der einzige Vorspannzustand hat dort Nullen.

**Bewertung [N].** Im Modell – starrer Körper, reibungsfreie Punktkontakte nur längs der Nadelachse, erste Ordnung,
Halt gegen beliebige Lasten – sind mit reinen Druckspitzen mindestens sieben Nadeln in passender Lage nötig; eine
siebte achsparallele Nadel zu Belegung B genügt nicht. Sechs Nadeln, die den Körper rundum halten, brauchen im Modell
zugfeste Verbindungen oder Schnittstellen, die auch die Querkräfte übertragen und messen. Ausgearbeitet sind Belegung
B (zugfest, statisch bestimmt, kinematische Lagerung ohne Vorspannung) und Belegung C (drei Kraftkomponenten,
Einspannung mit Vorspannung); beide bleiben als anwendungsabhängige Möglichkeiten offen, andere oder gemischte
Belegungen sind damit nicht ausgeschlossen. Unter vorgegebener Last (NR-02: mit x_cm = −A trägt B das Gewicht allein
mit Druck), mit Haftreibung, flächigem Kontakt oder Krümmungseffekten (höhere Ordnung) gelten andere Bedingungen.
Haftreibung an Druckspitzen hält den Körper zwar, trägt dann aber ungemessene Querkräfte (NR-07).

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
**zeitlich identisch null** (max. 0 in allen Phasenlagen): dynamische Nullkomponenten der Resultierenden. Das gilt
ohne äußere Nebenpfade; ein Signal dort zeigt Querbewegung der Module, Führungsfehler, Kopplung über die Halterung
(NR-08) oder äußere Lasten über die Systemgrenze (Kabel, Zuleitungen).

## NR-05 · Basislinie, Randterm und Einzelnadel-Nulltest

**Ergebnis [R]** (`n2_…`, Abschnitt 3; `v2_…`, Teil A).
- Zeitmittel über ganze Perioden: ⟨w_mess⟩ = (M g e_z; r_cm × M g e_z). Mit r_cm = (5, −3, 20) mm:
  M_x = −0,01913 N·m, M_y = −0,03188 N·m, F_z = 6,3765 N. Gegenprüfung mit anderer Modullage (G60h, 20 mm über O)
  und Schwerpunktversatz aus den Modulbahnen: Abweichung ≤ 1,8·10⁻¹⁰.
- Teilfenster (3,37 Perioden): Das Mittel weicht genau um den Randterm (P(t₁) − P(t₀))/T_W bzw.
  (H_O(t₁) − H_O(t₀))/T_W ab (Differenz ≤ 3·10⁻¹⁴); bei S sind das −0,272 N in F_z, bei T −6,7 mN in F_z und, in der
  Modullage G60h der Gegenprüfung (`v2_…`), +11,2 mN·m in M_y. Der Kraftanteil hängt nicht von der Modullage ab, der
  Momentenanteil schon.
- Einzelnadel-Mittel der Belegung B: in T, Z und S gleich (Differenz ≤ 1,0·10⁻¹⁰ N) und gleich G⁻¹·Basislinie.

**Bewertung [N].** Die Erhaltungsgröße „Zeitmittel = Mg“ wird im Rahmen zu sechs Nulltests (Kräfte und Momente;
für Momente mit der Basislinie r_cm × M g e_z, Nachtrag §4). Voraussetzungen: festgelegte Bilanzgrenze, alle Lasten
außer dem Gewicht über die sechs Schnittstellen (keine Kabel oder Zuleitungen), Rahmen ortsfest, ganze Perioden im
eingeschwungenen Zustand; für die Differenzform gleiche äußere Lasten in beiden Zuständen. Bei senkrechter
Modulbewegung hängt die Basislinie nicht von der Phasenlage ab. In der statisch bestimmten Belegung B ohne Nebenpfade
und mit unveränderter Geometrie G ist zusätzlich jede Nadel ein eigener Nulltest (Δ⟨q_j⟩ = 0 zwischen Zuständen); der
Absolutwert G⁻¹·Basislinie verlangt bekanntes G, M und r_cm. Differenztests zeigen gleichbleibende Fehlbeträge nicht
(NR-07). Ausgewertet werden ganze Perioden; sonst gehört der Randterm zur Basislinie.

## NR-06 · Nadelkräfte, Vorspannbedarf, Zeltkurve und Modulzeiger

**Belegung B, starr [R]** (`n2_…`, Abschnitt 4):

| Nadel | T: min … max [N] | S: min … max [N] | Inhalt am Triphasik-Punkt |
|---|---|---|---|
| Nord, Süd | −3,401 … +3,401 | 0 | ∓F_y/2 + M_x/(2A): nur k ≢ 0 (mod 3) (2,918 / 0,962 N bei k = 1/2) |
| Ost, West | 0 | 0 | ∓F_x/2 + M_z/(2A): lastfrei |
| oben | −7,346 … −1,005 | −6,572 … −1,366 | −F_z/2 + M_y/(2A): beide Klassen |
| unten | −0,397 … +5,570 | +1,366 … +6,572 | +F_z/2 + M_y/(2A) |

Nord, Süd und unten wechseln am Triphasik-Punkt das Vorzeichen, oben ist immer auf Zug: B braucht im Beispiel
zugfeste Nadeln.

**Belegung C, starr [R]** (`n2_…`, Abschnitt 5): Bei k_t/k_a = 0,02 trägt das Paar oben/unten 96,15 % des
Gewichts axial, 3,85 % gehen über die Querkomponenten der Seitennadeln (bei 0,1: 83,3 % / 16,7 %). Die axialen
Komponenten der Seitennadeln bleiben in T, Z und S ohne Last (ohne Vorspannung); die Querkomponenten tragen die
Momente. Nötige Vorspannung, damit kein axialer Kontakt auf Zug geht: 3,34 N (T), 6,32 N (S) bei k_t/k_a = 0,02;
über T, Z, S und beide Quersteifigkeiten 2,90–6,32 N. Mit reibschlüssiger Querkraft (μ_s = 0,2 angenommen [A]):
5,9 N (T) bzw. 6,3 N (S) bei 0,02, über beide Quersteifigkeiten 5,48–6,32 N. Gerechnet sind nur k_t/k_a = 0,02 und
0,1; weichere Querrichtungen verlangen mehr, weil ein größerer Anteil axial über oben/unten läuft. Mit gefangenem
Kugelgelenk entfällt beides; die Vorspannung ist dann frei wählbar (Nullraum).

**Zeltkurve im Rahmen [R]** (`n2_…`, Abschnitt 6): F_z,min entlang φ₃ = 240°: Spitze 5,4989 N bei 120°, Spannweite
über 100°–140° 0,5632 N (starr); mit Rahmendynamik B (k_a = 10⁶ N/m) 5,4206 N und 0,5601 N. Synchron
F_z,min = 2,7323 N (ε = 0,5715): Der V1-Kandidat bleibt im Modell überall im Kontaktast. Die Gegenkomponente R−₁ des
Kippmoments wächst linear vom Triphasik-Punkt weg (0,0027 N·m je 2°).

**Modulzeiger [R]** (`n2_…`, Abschnitt 7): Aus (F_z, M_x, M_y) folgen je Harmonischer die drei Modulzeiger
g_i,k = m_i·a_i,k (Kondition 1,414 in G0). Eine Störung von +1 % Masse und +1° Phase an Modul 2 wird exakt
zurückgerechnet (Betrag 1,01000, Phase −k·1,000°). Das ist eine Konsistenzprüfung des Modells: Die Rückrechnung
invertiert dieselbe Geometrie auf die rauschfreie Moduldyname des starren Grenzfalls bei exakt bekannter Modullage.
Rahmenübertragung (NR-08), Rauschen, Kalibrier- und Lagefehler sind nicht enthalten, Masse und Amplitude werden nicht
getrennt; ein experimenteller Nachweis ist das nicht.

**Bewertung.** Im starren Grenzfall ist F_z(t) = M g + Σ m_i s̈_i(t) dieselbe Funktion wie N(t) einer starren
Auflage, solange diese nicht abhebt (`linear_solver.py`, starre Auflage [Q]). Das gilt für den verglichenen Fall:
gleiche vorgeschriebene Modulbewegung, geschlossener Kontakt, starrer Grenzfall beider Aufbauten. Mit endlicher
Steifigkeit sind Rahmenübertragung (NR-08) und Kontaktübertragung der Auflage eigene Modellbestandteile: Die
Spannweite des Zelts ist starr 0,5632 N, für den Kandidaten auf seiner Auflage mit K = 1,5·10⁶ N/m 0,5603 N
(`code/auslegung.py --candidate` [Q]) und im Rahmen B mit k_a = 10⁶ N/m 0,5601 N. Die Unterschiede sind die jeweilige
Übertragung; die Nähe der beiden letzten Werte folgt aus den angenommenen Steifigkeiten. Der Rahmen setzt die lineare
Lösung dort fort, wo eine Auflage abheben würde, solange jede Nadel in ihrem Kontaktzustand bleibt (F_z < 0 trägt
dann die Nadel oben). Zusätzlich liefert er, bei bekannter Modullage und kalibrierter Übertragung, Moment und
Modulzeiger in jedem Lauf (vgl. KM-10 [Q]).

## NR-07 · Nadelregel: ungemessene Querkräfte

**Frage.** Was geschieht, wenn eine Nadel mehr Komponenten überträgt, als ihre Schnittstelle misst?

**Ergebnis [R]** (`n4_…`). Belegung B mit ungemessener Quersteifigkeit k_q = κ·k_a je Nadel in beiden
Querrichtungen:

| κ | ΔF_z/(M g) statisch | ΔM_y/M_y statisch | Fehler F_z,3 (T) | Fehler R+₁ (T) |
|---|---|---|---|---|
| 10⁻⁶ | −2,0·10⁻⁶ | −2,9·10⁻⁵ | 2,0·10⁻⁶ | 2,9·10⁻⁵ |
| 10⁻⁴ | −2,0·10⁻⁴ | −2,9·10⁻³ | 2,0·10⁻⁴ | 2,9·10⁻³ |
| 10⁻² | −1,96·10⁻² | −0,224 | 1,96·10⁻² | 0,224 |

Faustformel für kleine κ (Belegung B, gleiche Quersteifigkeit in beiden Querrichtungen): Kraftfehler ≈ 2κ,
Momentenfehler ≈ κ·(1 + 2(D/A)²) = 29,1·κ bei D/A = 3,75, weil zwei Nadelpaare quer mit dem Hebel D, axial aber nur
ein Paar mit dem Hebel A trägt. In der zentralen Belegung A gehen die Momente vollständig in ungemessene Pfade
(gemessener Anteil 0); auch dort fehlen in F_z etwa 2κ.

**Bewertung [N].** Jede Nadel ist genau ein Lastpfad; was sie überträgt, muss ihre Schnittstelle messen. Sonst
entsteht innerhalb der Nadel ein ungemessener Parallelpfad. Der Fehlbetrag ist ein fester Anteil und im linearen
Modell in allen Zuständen gleich: Differenztests zwischen Zuständen (Δ⟨w⟩ = 0, in B Δ⟨q_j⟩ = 0) zeigen ihn nicht. Ihn
zeigt nur der Vergleich mit unabhängig bekanntem M·g bzw. – für Momente und die Einzelnadeln in B – mit unabhängig
bekannter Schwerpunktlage und zutreffendem G, wie in `n4_…` gerechnet. Für Momente ist die Anforderung an die
Querweichheit um (D/A)² schärfer als für Kräfte.

## NR-08 · Rahmendynamik

**Ergebnis [R]** (`n3_…`; Zeitbereich in `v1_…`). Halterungsmoden des Körpers auf den Nadeln, Rahmenstruktur starr:

| Fall | Eigenfrequenzen [Hz] |
|---|---|
| B, k_a = 10⁶ N/m | 124,4 (θ_z), 147,2 (θ_x, θ_y), 279,2 (dreifach, Verschiebungen) |
| B, k_a = 10⁷ N/m | 393,3, 465,5 (2×), 882,8 (3×) |
| C, k_a = 10⁶, k_t = 2·10⁴ N/m | 93,3, 110,4 (2×), 284,7 (3×) |
| C, k_a = 10⁶, k_t = 10⁵ N/m | 208,6, 246,9 (2×), 305,8 (3×) |

- Die Drehmoden der Belegung B hängen bei gegebener Trägheit am Hebel A (Drehsteifigkeit 2·k_a·A²):
  A = 0,02 / 0,04 / 0,08 m gibt 62 / 124 / 249 Hz (tiefste Mode, k_a = 10⁶ N/m). Bei A ≤ 40 mm liegen Dreh- und
  Kippmoden unter den Verschiebungsmoden (279 Hz), bei A = 80 mm die Kippmoden (294 Hz) und bei A = 120 mm alle
  Drehmoden (373 / 442 Hz) darüber.
- Übertragung |T_ii(k·f)| (B, k_a = 10⁶): k = 1: 1,0013 (Kräfte), 1,0046 (M_x, M_y); k = 2: 1,0052 / 1,0188;
  k = 6: 1,048 / 1,199 (M_z 1,303). Bei k_a = 10⁷: k = 2: 1,0005 / 1,0018; k = 6: 1,0046 / 1,0169.
- Übersprechen: mit Schwerpunkt in O null (≤ 10⁻¹⁶); mit Schwerpunkt 16,2 mm über O (Trägerschwerpunkt 30 mm über O)
  entstehen am Triphasik-Punkt F_x, F_y von 3,0 / 4,1 mN (k = 1 / 2, k_a = 10⁶) bzw. 0,30 / 0,40 mN (10⁷). Andere
  Schwerpunktlagen sind nicht gerechnet.
- Nadelkräfte mit Dynamik gegen starr (T): bis 0,21 N (10⁶) bzw. 0,069 N (10⁷).
- Ohne Korrektur verlangt |T − 1| ≤ ε bis k_max = 6 bei 10 Hz nach der Einmassenschwinger-Näherung
  |T − 1| ≈ (k·f/f₁)² eine tiefste Mode f₁ ≥ 600 Hz (ε = 1 %) bzw. 1,9 kHz (ε = 0,1 %); die Zahlen folgen aus der
  gewählten Toleranz, der Bandbreite und der Näherung.

**Bewertung.** Die Nadeln sind die Halterung des Körpers: Ihre Steifigkeit, ihr Hebel (A in B, D in C) und die
Trägheit des Körpers setzen die Halterungsmoden, die Übertragung je Harmonischer und damit die Kalibrieranforderung.
Im Beispiel liegen die Momentenkomponenten den tiefsten Moden am nächsten (M_z dem Drehen um z, M_x und M_y dem
Kippen). Die Rahmenübertragung gehört wie die Kontaktübertragung der Auflage zur Versuchskonfiguration (H_cal(f),
dynamische Kalibrierung mit einem Anregungssatz vom Rang 6 wie in NR-09; eine Anregung in der Mitte regt die
Kippmoden nicht an, KM-05 [Q]). Elastizität und Eigenmoden von Rahmenstruktur und Fundament sind nicht gerechnet.

## NR-09 · Rang tatsächlicher Kalibrierlasten

**Frage.** Reichen die Kalibrierlasten, die die erste Fassung des Konzepts nannte – drei Rahmenlagen, eine
Umlenkrolle, das Eigengewicht des Prüflings –, für alle sechs Komponenten?

**Ergebnis [R]** (`n5_…`; Lastsätze, Lastpunkte und Beträge [A]; Rang mit [F; M/l_ref], l_ref = D). Eine statische
Last ist eine Kraft F mit Angriffspunkt r und hat den Lastvektor (F; r × F).

| Lastsatz | Lasten | Rang | Kondition | nicht angeregt |
|---|---|---|---|---|
| Eigengewicht (0,65 kg am Schwerpunkt), 1 / 2 / 3 unabhängige / 24 zufällige Rahmenlagen | 1 / 2 / 3 / 24 | 1 / 2 / 3 / 3 | – | 5 / 4 / 3 / 3 Richtungen |
| Eigengewicht in drei Lagen + Stück an einem zweiten Punkt | 6 | 5 | – | Moment um die Verbindungsgerade |
| Eigengewicht in drei Lagen + Stücke an zwei weiteren Punkten (nicht auf einer Geraden) | 9 | 6 | 5,07 | – |
| zwölf Gewichtsstücke, eine Lage / zwei Lagen | 12 / 24 | 3 / 5 | – | 3 Richtungen / F_x |
| zwölf Gewichtsstücke, drei Lagen mit unabhängigen Schwerkraftrichtungen | 36 | 6 | 2,55 | – |
| zwölf Gewichtsstücke, drei koplanare Lagen (um x gedreht: 0°, 90°, 180°) | 36 | 5 | – | F_x |
| Lastpunkte auf der Hochachse, drei unabhängige Lagen | 12 | 5 | – | M_z |
| eine Lage, zwölf Gewichtsstücke + je ein waagerechter Zug in x und y | 14 | 5 | – | M_z mit F_x, F_y gekoppelt |
| dazu ein zweiter Zug in x mit anderer Wirkungslinie | 15 | 6 | 13,74 | – |

**Bewertung [N].** Eine einzelne Last am Schwerpunkt hat Lastvektoren mit Wirkungslinie durch r_cm: Rang höchstens 3,
gleich in wie vielen Lagen. Begründung allgemein: Ein Vektor (a; b), der zu allen Lastvektoren eines Punkts p mit
linear unabhängigen Kraftrichtungen senkrecht steht, erfüllt a = p × b. Für zwei Punkte folgt b ∥ (p₁ − p₂) – es
fehlt das Moment um die Verbindungsgerade (Rang 5); für drei Punkte, die nicht auf einer Geraden liegen, folgt
b = 0 und a = 0 (Rang 6). Koplanare Schwerkraftrichtungen lassen die Kraft senkrecht zu ihrer Ebene aus. Maßgeblich
ist deshalb der Rang des tatsächlichen Lastsatzes, nicht die Zahl der Lagen; vor einer Kalibrierung ist er
nachzurechnen. Für die dynamische Kalibrierung H_cal(f) gilt dieselbe Bedingung an den Anregungssatz. Das Eigengewicht
prüft G nur in seinem Unterraum und nur bei unabhängig bekanntem M und r_cm (R1 setzt G voraus, NR-02).

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
- NR-09: Ränge numerisch (Singulärwerte, relative Schwelle 10⁻⁹) und durch die Begründung in NR-09 analytisch gestützt.
- Die Gegenprüfung rechnet dasselbe Modell unabhängig nach. Sie bestätigt Numerik und Modellkonsistenz; eine Messung
  ersetzt sie nicht.

## Grenzen

- Geometrie, Massen, Trägheiten, Nadelsteifigkeiten, Dämpfung und μ_s sind Annahmen [A]; keine CAD-Daten. Alle
  Frequenzen, Übertragungswerte und Faustzahlen (2κ, 29κ, 600 Hz) gelten für diese Beispielparameter.
- Rahmenstruktur und Fundament starr und ortsfest; ihre Elastizität und Eigenmoden sind nicht modelliert (eigener
  Modellbestandteil). Nadelmassen, Nadel-Eigenmoden und geometrische Steifigkeit aus Vorspannung und Gewicht nicht
  modelliert.
- Ideale Kontakte: Gelenke, Spitzen und Kugelgelenke reibungsfrei, freie Kontaktmomente τ^c_j = 0; ungemessene
  Querkräfte nur als Nebenschluss in NR-07.
- Linear: Kontaktöffnen an einer Nadel, Mikroschlupf und Hysterese an Reibkontakten sind nicht modelliert; NR-06
  gibt nur die Grenzen an, ab denen sie auftreten. Formschluss nur erster Ordnung (NR-03).
- Module senkrecht geführt, Bewegung vorgeschrieben; Querbewegung der Module, Antriebsrückwirkung, Kabel und
  Zuleitungen als Parallelpfade nicht modelliert. Übersprechen nur für einen Schwerpunkt über O gerechnet.
- Nur der V1-Kandidat als Modellvariante gerechnet; andere Prototypen über die Parameter von `Koerper`.
- Modulzeiger-Rückrechnung (NR-06) und Gegenprüfung sind Konsistenzprüfungen des Modells; Kalibrierlastsätze
  (NR-09) sind Rechenbeispiele.

## Offene Punkte

- Kinematische Lagerung (ausgearbeitet als B) und Einspannung (ausgearbeitet als C) bleiben als anwendungsabhängige
  Möglichkeiten offen; eine Bauentscheidung steht nicht an (Vorgabe vom 11.10.2026). Weitere Belegungen (≥ 7
  Druckspitzen in passender Lage, andere Versatzmuster, Schnittstellen mit bis zu sechs Komponenten) sind denkbar.
- Reale Fixierstellen, Versatz A, Nadelbauart (Gelenke, Quersteifigkeit κ, Kontaktmomente, Zugfestigkeit),
  Schnittstellen (Komponentenzahl, Band, Nennlast), Rahmenstruktur und Fundament.
- Kalibrierlastsatz und Anregungssatz mit nachgerechnetem Rang 6; unabhängige Referenz für M·g und r_cm.
- Ob und wie die einseitige Kontaktphysik der Linie A im Rahmen weiter untersucht wird (Modellvariante „einseitige
  Nadel unten“) – Entscheidung des Autors.
