# Einzugsgebiete des V1-Kandidaten – Attraktorkarten für alle Laufarten

**Phasenkontrollierte Mehrmassensysteme · Phase-Controlled Multi-Mass Systems**
Matthias Früh · Stand Oktober 2026 · Kandidat v1, gerechnet mit [`code/einzugsgebiete.py`](../code/einzugsgebiete.py)

*Nur Simulation, keine Messdaten. Alle Parameter sind gerechnet oder angenommen, keiner ist gemessen.*

**Kurzfassung.** Am V1-Kandidaten (1-FG-Modell, Kelvin-Voigt, ζ = 0,05) ist für 27 Laufarten der
Endzustand nach einem Wurf auf den Kontaktast über 16 Wurfphasen und Δv = −1 … +1 m/s gerechnet (17 712
Zellen, Grenzen auf ≤ 0,005 m/s).

- **Schnitt- und Pilotläufe:** Im Raster (16 Wurfphasen, Schritt 0,05 m/s, |Δv| ≤ 1 m/s) hüpft keiner
  der 24 Läufe. Im 0,01-Raster ist das an S100, S120, S140 und P110-252 bestätigt (8 Wurfphasen); die
  übrigen 20 sind nur im 0,05-Raster gerechnet.
- **L1** (und damit L2, L3), **(0°, 180°)** und **synchron** können hüpfen: in stabile Zustände mit
  Stoßspitzen von 482–484 N, synchron auch 969 N (P2).
- Das Einzugsgebiet ist **nicht monoton**: Hüpfbänder und Rückkehr-Inseln wechseln sich ab, in fast jeder
  Wurfphase. Das kleinste |Δv| mit Hüpfen (L1 0,42 m/s, (0°, 180°) 0,38 m/s, synchron 0,225 m/s) ist nur
  die untere Einhüllende, keine Schwelle. Darüber hängt der Endzustand von Wurfphase und Δv ab. Bei L1
  findet das 0,01-Raster oberhalb von |Δv| ≈ 0,6 m/s weitere schmale Hüpfbänder, auch in Wurfphasen, die
  im 0,05-Raster nur Rückkehr zeigen (8/16).
- Jeder gerechnete Wurf mit |Δv| ≥ 0,02 m/s hebt zunächst ab und setzt wieder auf. Zurück in den Kontakt
  kommt er von selbst, solange er keinen Hüpfattraktor erreicht; ein erreichter Hüpfzustand bleibt.
- Auch zurückkehrende Würfe erzeugen ≈ 1 kN je m/s Wurfgeschwindigkeit.
- Das Ergebnis hängt stark von ζ und vom Kontaktgesetz ab: Bei ζ = 0,02 hüpfen auch die drei geprüften
  Schnittpunkte und der Pilot (110°, 252°), bei ζ = 0,20 keine der sechs geprüften Laufarten; mit
  Hunt-Crossley hüpft (120°, 240°) schon bei ζ = 0,05.

---

## 1 · Zweck

- **Abnahme AP-03.** Das Erfolgskriterium verlangt das Einzugsgebiet (kritische Wurfgeschwindigkeit bzw.
  Stoßimpuls) für alle Laufarten, auch für Einzelmodul-, Schnitt- und Pilotläufe. Bisher lag es nur für den
  synchronen Lauf vor (`ereignisloeser.py --candidate --einzug`).
- **Sicherheit für die Präregistrierung.** Präreg v2 §5.1 legt die Nennlast aus der größten erwarteten
  Zellkraft fest und verlangt einen Überlastanschlag. §6 schreibt für jeden Lauf eine Rampe mit aktiver
  Phasenregelung vor, nie durch die synchrone Phasung; L1–L3 laufen in jedem Kontrollsatz. Ein Hüpfzustand
  bringt im Modell Stoßspitzen von einigen 100 N bei M·g = 6,4 N. Die Karte zeigt, welche Laufart nach
  welcher Störung dort landet.
- **Karte statt Schwelle.** Das Einzugsgebiet des Kontaktasts ist nicht monoton. An der Satelliteninsel
  (35°, 116°) der Referenz kehren bei t₀ = 0 die Würfe +0,10 und +0,20 m/s zurück, +0,125 und +0,15 m/s
  hüpfen. Am Kandidaten gilt dasselbe (Abschnitt 4). Eine einzelne kritische Wurfgeschwindigkeit wäre
  deshalb falsch. Dieses Dokument gibt je Laufart die Attraktoren und je Wurfphase die Δv-Intervalle an.
  Das kleinste |Δv| mit Hüpfen steht nur als untere Einhüllende da, ausdrücklich nicht als Schwelle.

---

## 2 · Modellkonfiguration

Gerechnet ist das 1-FG-Modell der Referenz-Engine mit dem ereignisgenauen Löser
[`code/ereignisloeser.py`](../code/ereignisloeser.py) (Kelvin-Voigt geschlossen, Übergänge exakt lokalisiert).

| Größe | Wert |
|---|---|
| Freiheitsgrade | 1 (Hub des Körpers); keine Kippfreiheitsgrade, ideales Profil, ideal geführte Module |
| Kontakt | Kelvin-Voigt N = −K·x − C·ẋ, einseitig; Ablösung bei N = 0, Aufsetzen bei x = 0 |
| Restmasse m₀ | 0,350 kg |
| Module | drei je 0,100 kg; M = 0,650 kg, μ = 0,4615; geparkte Module bleiben mit ihrer Masse an Bord |
| Profil | Egg, Halteanteil THOLD = 0,65 |
| Hub | 8 mm Spitze-Spitze je bewegtem Modul |
| Frequenz | f = 10 Hz, T = 0,1 s |
| Steifigkeit | K = 1,5·10⁶ N/m, f_n = √(K/M)/2π = 241,8 Hz |
| Dämpfung | ζ = 0,05, C = 2ζ·√(K·M) = 98,74 N·s/m; Empfindlichkeit ζ = 0,02 / 0,10 / 0,20 (C = 39,50 / 197,5 / 395,0 N·s/m) |
| Schwerkraft | g = 9,81 m/s², M·g = 6,3765 N |
| Hunt-Crossley (Vergleich) | `hc_aequivalent(…, ζ = 0,05, n = 1,5, v_ref = 0,5 m/s)`: K_h = 3,960·10⁸ N/m^1,5, α = 0,3282 s/m; gleiche Tangentensteifigkeit in der Ruhelage, gleiche Stoßzahl bei 0,5 m/s (Zuordnung angenommen) |

**Laufarten** (Präreg v2 §5.3, §5.4, §6; Bezeichnungen wie in [`code/auslegung.py`](../code/auslegung.py)):

| Laufart | Phasen (φ₁, φ₂, φ₃) | Hub je Modul | Anzahl |
|---|---|---|---|
| Einzelmodul L1 | (0°, 0°, 0°) | (8, 0, 0) mm; Module 2 und 3 geparkt | 1 |
| Einzelmodul L2, L3 | – | wie L1, um τ_j verschoben (Abschnitt 3.6) | – |
| Schnitt | (0°, φ₂, 240°), φ₂ = 100°, 102°, …, 140° | 8 mm je Modul | 21 |
| Piloten | (0°, 110°, 250°), (0°, 130°, 230°), (0°, 110°, 252°) | 8 mm je Modul | 3 |
| Vergleich | synchron (0°, 0°, 0°), (0°, 0°, 180°) | 8 mm je Modul | 2 |

Alle 27 Laufarten haben bei allen vier ζ einen Kontaktast. Die kleinste Reserve F_min/(M·g) hat jeweils
synchron: 41,8 % (ζ = 0,02), 42,6 % (ζ = 0,05, wie `auslegung.py --candidate`), 42,8 % (ζ = 0,10 und 0,20);
bei ζ = 0,05 liegen alle übrigen Laufarten bei ≥ 73,8 %. Der Kontaktast ist also überall vorhanden und
linear weit vom Abheben entfernt. Die Konfiguration steht in jeder Zeile der CSV-Dateien (Spalten
`phi1_deg` … `g_m_s2`).

---

## 3 · Methode

### 3.1 Start, Wurf, Raster

- **Start** auf dem Kontaktast zur Wurfphase t₀: Fixpunkt der affinen Periodenabbildung im Dauerkontakt
  (`kontaktorbit`). Hunt-Crossley: Newton ab dem Kelvin-Voigt-Orbit, um die Differenz der statischen
  Einfederungen verschoben (`kontaktast()` im Skript). `startzustand(…, "orbit")` begann Newton zunächst in
  der Ruhelage und konvergierte am Kandidaten an 5 von 24 Wurfphasen nicht (L1 bei t₀/T = 7/8, synchron bei
  2/8, 3/8, 6/8, 7/8); seit der Korrektur in `ereignisloeser.py` startet es wie `kontaktast()` am
  Kelvin-Voigt-Orbit (Test `test_startzustand_hunt_crossley_am_kandidaten`). t₀ zählt ab dem Profilnullpunkt
  von Modul 1.
- **Wurf** als idealer Geschwindigkeitsstoß auf den Körper: ẋ → ẋ + Δv, Stoßimpuls M·Δv (Δv = 1 m/s
  entspricht 0,65 N·s ≈ M·g·T). Δv > 0 wirft nach oben, vom Auflager weg; Δv < 0 drückt ins Auflager.
- **Raster:** t₀/T ∈ {0, 1/16, …, 15/16}, Δv ∈ {−1,00; −0,95; …; +1,00} m/s, also 16 × 41 = 656 Zellen je
  Laufart und 17 712 Zellen für die 27 Laufarten. Δv = 0 ist die Kontrolle: Der Start muss auf dem
  Kontaktast bleiben (in allen 432 Wurfphasen erfüllt).

### 3.2 Laufdauer und Klassifikation

Jeder Wurf läuft zunächst 80 Perioden (8 s). Klassifiziert wird über die letzten 20 Perioden:

| Endzustand | Kriterium | Begründung der Laufdauer |
|---|---|---|
| Kontaktast (K) | λ = 0 im Fenster und Poincaré-Schnitt gleich dem Orbit (\|Δx\| < 10⁻⁹ m, \|Δẋ\| < 10⁻⁶ m/s) | Im Dauerkontakt zieht die Periodenabbildung mit \|μ\| = e^{−ζω_n·T} zusammen: 5,0·10⁻⁴ je Periode (ζ = 0,05), 0,048 (ζ = 0,02). 20 Perioden ohne Abheben schließen ein späteres Abheben aus. |
| Hüpfen (H) | λ > 0 und Periode p: Poincaré-Schnitt kehrt über 10 Perioden auf 10⁻⁵ m/s und 10⁻⁷ m wieder | Der Hüpforbit zieht nur mit \|μ\| ≈ e zusammen (Stoßzahl des Kontakts: 0,86 bei ζ = 0,05, 0,94 bei ζ = 0,02). Von 0,3 m/s auf 10⁻⁵ m/s braucht das ≈ 70 bzw. ≈ 170 Perioden. Ohne Wiederkehr wird um je 80 Perioden verlängert, höchstens auf 800 (80 s); P2-Orbits brauchen bei ζ = 0,02 bis zu 480 Perioden. |
| irregulär (X) | keine Wiederkehr bis 800 Perioden | Status „nicht eingeschwungen“; λ und F_max aus den letzten 20 Perioden |

Hunt-Crossley: 60 Perioden, höchstens 120; Kontaktast bei |Δx| < 10⁻⁶ m und |Δẋ| < 10⁻³ m/s, weil die
Dämpfung um die Ruhelage klein ist (|μ| = 0,79 je Periode).

Je Zelle werden λ (Liftoff-Anteil), Periode p, Aufsetzer je Periode, F_max und die größte Stoßspitze im
Fenster gespeichert, dazu F_max und die größte Stoßspitze über den ganzen Lauf einschließlich des
Einschwingens (`F_max_lauf_N`, `stossspitze_lauf_N`). F_max über den ganzen Lauf enthält auch den
Dämpferkraftsprung C·|Δv| eines Wurfs ins Auflager.

### 3.3 Attraktoren

Signatur eines Hüpfzustands: (p, Aufsetzer je p Perioden, λ, F_max). Zellen mit gleicher Signatur (λ auf
0,05 Prozentpunkte, F_max auf 0,5 N bzw. 0,1 %) bilden je Laufart einen Attraktor. Nummeriert wird nach der
Zahl der Rasterzellen: K Kontaktast, H1, H2, … Hüpfzustände, X irregulär. Für jeden Hüpfattraktor rechnet
ein Newton-Schießverfahren auf den p-fachen Poincaré-Schnitt den Orbit genau nach; die Attraktortabelle
nennt diese Werte und den größten Floquet-Multiplikator |μ|_max. Zwei phasenverschobene Kopien desselben
P2-Orbits (Aufsetzen in geraden bzw. ungeraden Perioden) haben dieselbe Signatur und zählen als ein
Attraktor.

### 3.4 Grenzen

Zwischen zwei in Δv benachbarten Rasterzellen mit verschiedenem Endzustand wird rekursiv halbiert, bis die
Klammer ≤ 0,005 m/s breit ist (vier Schritte, Breite 0,003125 m/s). Liegt in der Mitte ein dritter
Zustand, werden beide Teilgrenzen verfolgt. Die Intervalltabellen in Abschnitt 4 nennen als Rand den
äußersten gerechneten Punkt jedes Intervalls; die wahre Grenze liegt höchstens 0,003125 m/s weiter außen.
Inseln, die schmaler als das Raster sind und zwischen zwei gleichen Nachbarn liegen, findet das Verfahren
nicht. Grenzen in t₀-Richtung werden nicht verfeinert.

### 3.5 Vorabprüfung

Bekannte Werte (Nachrechnung 10/2026, `tests/test_ereignisloeser.py`): V1 synchron, t₀ = 0, Start in der
statischen Ruhelage. Derselbe Ablauf (`--pruefung`) liefert:

| Start | Δv | Endzustand | λ | Stoßspitze im Hüpfzustand | F_max im Lauf | Perioden |
|---|---|---|---|---|---|---|
| Ruhelage | 0,25 m/s | Kontaktast | 0 | – | 331,2 N | 80 |
| Ruhelage | 0,30 m/s | Hüpfen, P1 | 97,9872 % | 483,66 N | 606,1 N | 160 |
| Kontaktast | 0,25 m/s | Kontaktast | 0 | – | 332,4 N | 80 |
| Kontaktast | 0,30 m/s | Hüpfen, P1 | 97,9872 % | 483,66 N | 607,8 N | 160 |

Die Referenz (0,25 m/s kehrt zurück; 0,30 m/s hüpft mit λ ≈ 97,99 % und Stoßspitze ≈ 483,7 N) wird
getroffen. Unterschied der Starts: Die Ruhelage (x = −M·g/K, ẋ = 0) liegt nicht auf dem Kontaktast. Beim
Start dort fällt der Wurf mit dem Einschalten der Anregung zusammen. Der Orbit weicht je nach Wurfphase um
bis zu 4,5 µm Einfederung (≈ 6,8 N Federkraft) und 0,4 mm/s von der Ruhelage ab. Die Karte startet auf
dem Orbit, wie ein Störstoß im laufenden Betrieb. Am Kandidaten ist die Klassifikation gleich, die
Stoßspitze im Hüpfzustand auch. Die Grenzen verschieben sich um höchstens eine Bisektionsklammer
(0,003125 m/s); Grundlage ist die Bisektion von beiden Starts an zwölf Wurfphasen (Abschnitt 4.2). Auch
der zurückkehrende Wurf von 0,25 m/s hebt ab und erzeugt beim ersten Aufsetzen 331 N.

### 3.6 L2 und L3

Im 1-FG-Modell wirkt Modul j nur über m_j·ë_j(t − τ_j), τ_j = φ_j/(360°·f). Bei gleicher Modulmasse und
gleichem Hub ist der Einzelmodullauf L_j daher L1 mit der Zeit t − τ_j: Seine Karte ist die von L1, in t₀
um τ_j verschoben. Die Lage des Moduls auf der Platte wirkt erst über Kippmoden, die das Modell nicht hat.
Stichprobe (`--pruefung`): L1 bei t₀, L2 (φ₂ = 120°) bei t₀ + T/3 und L3 (φ₃ = 240°) bei t₀ + 2T/3, je
für t₀/T ∈ {0, 2/16, 12/16} und Δv ∈ {−0,55; −0,30; +0,45; +0,60} m/s (36 Läufe, darunter fünf Hüpfzustände
und zwei Rückkehr-Inseln). Alle zwölf Tripel haben denselben Endzustand; F_max und λ stimmen auf 2·10⁻¹¹ N
bzw. 2·10⁻¹³ Prozentpunkte überein (Rundung). Die L1-Karte gilt damit für L2 und L3 mit t₀ → t₀ − τ_j.

---

## 4 · Ergebnisse

Alle Angaben in 4.1 bis 4.5 gelten für ζ = 0,05 und Kelvin-Voigt. Alle 17 712 Zellen sind eingeschwungen
(17 270 nach 80, 391 nach 160, 51 nach 240 Perioden); keine ist irregulär. Δv = 0 bleibt in allen 432
Wurfphasen auf dem Kontaktast.

### 4.1 Überblick

| Laufart | Rasterzellen | Kontaktast | Hüpfen | irregulär | Attraktoren | kleinstes Δv > 0 ohne Rückkehr (t₀/T) | kleinstes Δv < 0 ohne Rückkehr (t₀/T) | Wurfphasen mit Rückkehr-Inseln + / − (0,05-Raster) | F_max im Lauf, max |
|---|---|---|---|---|---|---|---|---|---|
| L1 | 656 | 619 (94,4 %) | 37 (5,6 %) | 0 | K, H1 (P1, 481,9 N) | +0,416 (2/16) | −0,484 (2/16) | 13 / 12 | 987 N |
| Schnitt, 21 Punkte | 13 776 | 13 776 (100,0 %) | 0 (0,0 %) | 0 | K | – | – | 0 / 0 | 934–957 N |
| Piloten, 3 | 1 968 | 1 968 (100,0 %) | 0 (0,0 %) | 0 | K | – | – | 0 / 0 | 949–952 N |
| synchron (0°, 0°) | 656 | 282 (43,0 %) | 374 (57,0 %) | 0 | K, H1 (P1, 483,7 N), H2 (P2, 968,6 N) | +0,225 (4/16) | −0,263 (4/16) | 15 / 16 | 1072 N |
| (0°, 180°) | 656 | 564 (86,0 %) | 92 (14,0 %) | 0 | K, H1 (P1, 482,4 N) | +0,381 (2/16) | −0,444 (2/16) | 16 / 15 | 996 N |

- **Schnitt und Piloten:** Alle 15 744 Zellen (24 Laufarten × 656) kehren in den Kontaktast zurück. Im
  Raster tritt kein Hüpfzustand auf, auch nicht bei |Δv| = 1 m/s. Die Feinprüfung in 4.8 sucht schmalere
  Hüpfbänder, aber nur an vier dieser 24 Läufe (S100, S120, S140, P110-252).
- **Einzelmodul L1:** 37 Zellen (5,6 %) enden im Hüpfzustand H1. Hüpfen tritt nur in schmalen Bändern auf:
  Die inneren Bänder sind 0,003–0,094 m/s breit (Median 0,028 m/s, gemessen zwischen den äußersten
  gerechneten Punkten).
- **(0°, 180°):** 92 Zellen (14,0 %) enden in H1.
- **Synchron:** 374 Zellen (57,0 %) enden in H1 oder H2. H2 ist ein P2-Orbit mit einem Aufsetzer je
  Doppelperiode und der doppelten Stoßspitze (968,6 N).

### 4.2 Attraktoren

| Laufart | Attraktor | p | Aufsetzer je Periode | λ [%] | Stoßspitze = F_max [N] | Stoßspitze / (M·g) | \|μ\|max | Aufsetzphase t/T | Rasterzellen |
|---|---|---|---|---|---|---|---|---|---|
| L1 | H1 | 1 | 1,00 | 97,979 | 481,9 | 76 | 0,8577 | 0,0609 | 37 |
| synchron (0°,0°) | H1 | 1 | 1,00 | 97,987 | 483,7 | 76 | 0,8582 | 0,2485 | 319 |
| synchron (0°,0°) | H2 | 2 | 0,50 | 98,995 | 968,6 | 152 | 0,8584 | 0,1721 | 55 |
| (0°,180°) | H1 | 1 | 1,00 | 97,981 | 482,4 | 76 | 0,8578 | 0,0633 | 92 |

Der Kontaktast (K) ist in jeder Laufart derselbe Orbit wie im Start, mit |μ| = 5,0·10⁻⁴ und F_max = 6,97 N
(Schnitt (120°, 240°)) bis 13,17 N (synchron). Alle Hüpfattraktoren sind stabil; ihr größter
Floquet-Multiplikator liegt bei 0,858, nahe der Stoßzahl e = 0,8588 des Kontakts. Ein Hüpfzustand klingt
im Modell also nicht von selbst ab. Die drei P1-Attraktoren von L1, (0°, 180°) und synchron unterscheiden
sich in der Stoßspitze nur um 2 N (481,9 / 482,4 / 483,7 N ≈ 76·M·g), wohl aber in der Aufsetzphase.

**Startzustand Ruhelage gegen Kontaktast.** Bekannte Werte (Start in der Ruhelage, 0,02-m/s-Raster):
erster Hüpfwurf synchron bei 0,30 / 0,24 / 0,26 / 0,60 m/s für t₀/T = 0 / 0,25 / 0,5 / 0,75. Vom Kontaktast
liegt er bei +0,297 / +0,225 / +0,259 / +0,603 m/s. Für den Abgleich sind an zwölf Wurfphasen (synchron
t₀/T = 0, 1/4, 1/2, 3/4; L1 t₀/T = 0, 1/8, …, 7/8) alle Grenzen von beiden Starts per Bisektion gerechnet
(`--start ruhe`, Raster 0,05 m/s, Klammer 0,003125 m/s; Befehle in Abschnitt 7):

| Vergleich | Anzahl |
|---|---|
| Grenzen vom Kontaktast | 63 |
| davon in derselben Klammer | 59 |
| davon um eine Klammer verschoben (0,003125 m/s) | 4 (L1 1/8 bei −0,48; synchron 3/4 bei −0,96, +0,60, +0,88) |
| zusätzliche Grenzen nur aus der Ruhelage | 1: synchron t₀ = 0, ein einzelner K-Punkt bei +0,8125 m/s zwischen H1 und H2 (vom Kontaktast dort H1 → H2) |

Der Startzustand verschiebt die Grenzen also um höchstens eine Klammer. Schmale Inseln können je nach
Start auftreten oder fehlen.

### 4.3 Attraktorkarten je Laufart

Lesart: In jeder Zeile folgen die Endzustände von Δv = −1,00 bis +1,00 m/s aufeinander; angegeben ist der
erste und letzte gerechnete Punkt jedes Intervalls (Raster- und Bisektionspunkte). Die Grenze liegt
zwischen zwei benachbarten Angaben, also in einer Lücke von höchstens 0,003125 m/s. Ein einzelner Wert
ist ein Intervall, das nur ein Bisektionspunkt trifft.

**Schnitt (21 Punkte) und Piloten (3):** im 0,05-Raster in allen 16 Wurfphasen K von −1,000 bis +1,000 m/s.

**L1** (gilt für L2 und L3 mit t₀ → t₀ − τ_j):

| t₀/T | Endzustand über Δv [m/s] |
|---|---|
| 0/16 | K −1,000 … −0,594 · H1 −0,591 … −0,500 · K −0,497 … +0,431 · H1 +0,434 … +0,509 · K +0,512 … +0,734 · H1 +0,738 … +0,750 · K +0,753 … +0,991 · H1 +0,994 … +1,000 |
| 1/16 | K −1,000 … −0,856 · H1 −0,853 … −0,841 · K −0,838 … −0,584 · H1 −0,581 … −0,487 · K −0,484 … +0,416 · H1 +0,419 … +0,500 · K +0,503 … +0,844 · H1 +0,847 … +0,850 · K +0,853 … +1,000 |
| 2/16 | K −1,000 … −0,572 · H1 −0,569 … −0,484 · K −0,481 … +0,412 · H1 +0,416 … +0,494 · K +0,497 … +1,000 |
| 3/16 | K −1,000 … −0,550 · H1 −0,547 … −0,494 · K −0,491 … +0,416 · H1 +0,419 … +0,478 · K +0,481 … +1,000 |
| 4/16 | K −1,000 … −0,956 · H1 −0,953 … −0,947 · K −0,944 … +0,691 · H1 +0,694 … +0,703 · K +0,706 … +1,000 |
| 5/16 | K −1,000 … −0,959 · H1 −0,956 … −0,944 · K −0,941 … −0,809 · H1 −0,806 … −0,794 · K −0,791 … +1,000 |
| 6/16 | K −1,000 … −0,966 · H1 −0,963 … −0,950 · K −0,947 … +0,944 · H1 +0,947 … +0,972 · K +0,975 … +1,000 |
| 7/16 | K −1,000 … +0,988 · H1 +0,991 … +1,000 |
| 8/16 | K −1,000 … +1,000 |
| 9/16 | K −1,000 … −0,762 · H1 −0,759 … −0,741 · K −0,738 … +0,637 · H1 +0,641 … +0,656 · K +0,659 … +1,000 |
| 10/16 | K −1,000 … +0,834 · H1 +0,838 … +0,850 · K +0,853 … +1,000 |
| 11/16 | K −1,000 … −0,725 · H1 −0,722 … −0,694 · K −0,691 … +0,838 · H1 +0,841 … +0,853 · K +0,856 … +1,000 |
| 12/16 | K −1,000 … +0,572 · H1 +0,575 … +0,600 · K +0,603 … +1,000 |
| 13/16 | K −1,000 … −0,656 · H1 −0,653 … −0,609 · K −0,606 … +0,531 · H1 +0,534 … +0,569 · K +0,572 … +1,000 |
| 14/16 | K −1,000 … −0,625 · H1 −0,622 … −0,562 · K −0,559 … +0,491 · H1 +0,494 … +0,541 · K +0,544 … +1,000 |
| 15/16 | K −1,000 … −0,606 · H1 −0,603 … −0,525 · K −0,522 … +0,456 · H1 +0,459 … +0,522 · K +0,525 … +1,000 |

Die L1-Tabelle ist das 0,05-Raster. Oberhalb von |Δv| ≈ 0,6 m/s findet das 0,01-Raster weitere schmale
Hüpfbänder, auch in Zeilen, die hier nur K zeigen (etwa 8/16; Abschnitte 4.4 und 4.8).

**(0°, 180°):**

| t₀/T | Endzustand über Δv [m/s] |
|---|---|
| 0/16 | K −1,000 … −0,894 · H1 −0,891 … −0,847 · K −0,844 … −0,634 · H1 −0,631 … −0,459 · K −0,456 … +0,397 · H1 +0,400 … +0,544 · K +0,547 … +0,722 · H1 +0,725 … +0,766 · K +0,769 … +0,841 · H1 +0,844 … +0,856 · K +0,859 … +0,950 · H1 +0,953 … +1,000 |
| 1/16 | K −1,000 … −0,881 · H1 −0,878 … −0,850 · K −0,847 … −0,625 · H1 −0,622 … −0,447 · K −0,444 … +0,384 · H1 +0,388 … +0,534 · K +0,537 … +0,725 · H1 +0,728 … +0,756 · K +0,759 … +0,894 · H1 +0,897 … +0,906 · K +0,909 … +1,000 |
| 2/16 | K −1,000 … −0,875 · H1 −0,872 … −0,847 · K −0,844 … −0,619 · H1 −0,616 … −0,444 · K −0,441 … +0,378 · H1 +0,381 … +0,531 · K +0,534 … +0,725 · H1 +0,728 … +0,750 · K +0,753 … +0,897 · H1 +0,900 … +0,916 · K +0,919 … +1,000 |
| 3/16 | K −1,000 … −0,978 · H1 −0,975 … −0,944 · K −0,941 … −0,863 · H1 −0,859 … −0,841 · K −0,838 … −0,600 · H1 −0,597 … −0,453 · K −0,450 … +0,384 · H1 +0,388 … +0,519 · K +0,522 … +1,000 |
| 4/16 | K −1,000 … −0,972 · H1 −0,969 … −0,931 · K −0,928 … −0,566 · H1 −0,562 … −0,475 · K −0,472 … +0,397 · H1 +0,400 … +0,491 · K +0,494 … +0,925 · H1 +0,928 … +0,963 · K +0,966 … +1,000 |
| 5/16 | K −1,000 … −0,978 · H1 −0,975 … −0,919 · K −0,916 … −0,825 · H1 −0,822 … −0,797 · K −0,794 … +0,688 · H1 +0,691 … +0,709 · K +0,713 … +0,787 · H1 +0,791 … +0,834 · K +0,838 … +0,928 · H1 +0,931 … +0,972 · K +0,975 … +1,000 |
| 6/16 | K −1,000 … −0,991 · H1 −0,988 … −0,934 · K −0,931 … −0,803 · H1 −0,800 … −0,775 · K −0,772 … +0,787 · H1 +0,791 … +0,841 · K +0,844 … +0,925 · H1 +0,928 … +1,000 |
| 7/16 | H1 −1,000 … −0,972 · K −0,969 … +0,822 · H1 +0,825 … +0,856 · K +0,859 … +0,925 · H1 +0,928 … +1,000 |
| 8/16 | H1 −1,000 … −0,994 · K −0,991 … −0,784 · H1 −0,781 … −0,747 · K −0,744 … +0,641 · H1 +0,644 … +0,669 · K +0,672 … +0,844 · H1 +0,847 … +0,866 · K +0,869 … +1,000 |
| 9/16 | H1 −1,000 · K −0,997 … −0,781 · H1 −0,778 … −0,738 · K −0,734 … +0,631 · H1 +0,634 … +0,669 · K +0,672 … +1,000 |
| 10/16 | K −1,000 … −0,775 · H1 −0,772 … −0,725 · K −0,722 … +0,622 · H1 +0,625 … +0,662 · K +0,666 … +1,000 |
| 11/16 | H1 −1,000 … −0,991 · K −0,988 … −0,759 · H1 −0,756 … −0,700 · K −0,697 … +0,606 · H1 +0,609 … +0,653 · K +0,656 … +1,000 |
| 12/16 | K −1,000 … −0,725 · H1 −0,722 … −0,653 · K −0,650 … +0,572 · H1 +0,575 … +0,628 · K +0,631 … +1,000 |
| 13/16 | K −1,000 … −0,694 · H1 −0,691 … −0,594 · K −0,591 … +0,522 · H1 +0,525 … +0,600 · K +0,603 … +0,791 · H1 +0,794 … +0,812 · K +0,816 … +1,000 |
| 14/16 | K −1,000 … −0,922 · H1 −0,919 … −0,866 · K −0,863 … −0,672 · H1 −0,669 … −0,531 · K −0,528 … +0,469 · H1 +0,472 … +0,578 · K +0,581 … +1,000 |
| 15/16 | K −1,000 … −0,903 · H1 −0,900 … −0,850 · K −0,847 … −0,650 · H1 −0,647 … −0,484 · K −0,481 … +0,425 · H1 +0,428 … +0,559 · K +0,562 … +0,728 · H1 +0,731 … +0,778 · K +0,781 … +1,000 |

**Synchron (0°, 0°):**

| t₀/T | Endzustand über Δv [m/s] |
|---|---|
| 0/16 | H2 −1,000 … −0,941 · H1 −0,938 … −0,825 · K −0,822 … −0,784 · H1 −0,781 … −0,331 · K −0,328 … +0,294 · H1 +0,297 … +0,678 · K +0,681 … +0,713 · H1 +0,716 … +0,812 · H2 +0,816 … +1,000 |
| 1/16 | H2 −1,000 … −0,916 · K −0,912 … −0,906 · H1 −0,903 … −0,300 · K −0,297 … +0,263 · H1 +0,266 … +0,787 · H2 +0,791 … +1,000 |
| 2/16 | H2 −1,000 … −0,906 · K −0,903 · H1 −0,900 … −0,784 · K −0,781 … −0,741 · H1 −0,738 … −0,278 · K −0,275 … +0,241 · H1 +0,244 … +0,637 · K +0,641 … +0,675 · H1 +0,678 … +0,744 · K +0,747 … +0,750 · H1 +0,753 … +0,775 · H2 +0,778 … +1,000 |
| 3/16 | H2 −1,000 … −0,906 · H1 −0,903 … −0,781 · K −0,778 … −0,734 · H1 −0,731 … −0,266 · K −0,263 … +0,228 · H1 +0,231 … +0,628 · K +0,631 … +0,669 · H1 +0,672 … +0,772 · H2 +0,775 … +1,000 |
| 4/16 | H2 −1,000 … −0,916 · H1 −0,912 … −0,784 · K −0,781 … −0,738 · H1 −0,734 … −0,263 · K −0,259 … +0,222 · H1 +0,225 … +0,628 · K +0,631 … +0,669 · H1 +0,672 … +0,741 · K +0,744 … +0,750 · H1 +0,753 … +0,778 · H2 +0,781 … +1,000 |
| 5/16 | H2 −1,000 … −0,934 · H1 −0,931 … −0,794 · K −0,791 … −0,744 · H1 −0,741 … −0,269 · K −0,266 … +0,225 · H1 +0,228 … +0,634 · K +0,637 … +0,675 · H1 +0,678 … +0,747 · K +0,750 … +0,756 · H1 +0,759 … +0,794 · H2 +0,797 … +1,000 |
| 6/16 | H2 −1,000 … −0,966 · H1 −0,963 … −0,903 · K −0,900 … −0,891 · H1 −0,887 … −0,803 · K −0,800 … −0,753 · H1 −0,750 … −0,278 · K −0,275 … +0,231 · H1 +0,234 … +0,641 · K +0,644 … +0,684 · H1 +0,688 … +0,797 · K +0,800 … +0,812 · H1 +0,816 · H2 +0,819 … +1,000 |
| 7/16 | K −1,000 · H1 −0,997 … −0,809 · K −0,806 … −0,756 · H1 −0,753 … −0,291 · K −0,287 … +0,241 · H1 +0,244 … +0,647 · K +0,650 … +0,691 · H1 +0,694 … +0,847 · H2 +0,850 … +0,969 · H1 +0,972 … +1,000 |
| 8/16 | K −1,000 … −0,994 · H1 −0,991 … −0,812 · K −0,809 … −0,753 · H1 −0,750 … −0,309 · K −0,306 … +0,256 · H1 +0,259 … +0,647 · K +0,650 … +0,694 · H1 +0,697 … +0,841 · K +0,844 … +0,850 · H1 +0,853 … +0,984 · K +0,988 … +1,000 |
| 9/16 | H1 −1,000 … −0,806 · K −0,803 … −0,728 · H1 −0,725 … −0,338 · K −0,334 … +0,275 · H1 +0,278 … +0,631 · K +0,634 … +0,691 · H1 +0,694 … +0,778 · K +0,781 … +0,800 · H1 +0,803 … +0,887 · K +0,891 … +0,925 · H1 +0,928 … +1,000 |
| 10/16 | H1 −1,000 … −0,791 · K −0,787 … −0,669 · H1 −0,666 … −0,394 · K −0,391 … +0,316 · H1 +0,319 … +0,591 · K +0,594 … +0,681 · H1 +0,684 … +0,778 · K +0,781 … +0,809 · H1 +0,812 … +1,000 |
| 11/16 | K −1,000 … −0,897 · H1 −0,894 … −0,750 · K −0,747 … +0,378 · H1 +0,381 … +0,469 · K +0,472 … +0,656 · H1 +0,659 … +0,772 · K +0,775 … +0,819 · H1 +0,822 … +0,909 · K +0,912 … +1,000 |
| 12/16 | H1 −1,000 … −0,963 · K −0,959 … −0,859 · H1 −0,856 … −0,672 · K −0,669 … +0,600 · H1 +0,603 … +0,744 · K +0,747 … +0,881 · H1 +0,884 … +0,938 · K +0,941 … +0,994 · H1 +0,997 … +1,000 |
| 13/16 | K −1,000 … −0,994 · H1 −0,991 … −0,572 · K −0,569 … +0,516 · H1 +0,519 … +0,878 · K +0,881 … +0,919 · H1 +0,922 … +0,997 · K +1,000 |
| 14/16 | H1 −1,000 … −0,947 · K −0,944 … −0,900 · H1 −0,897 … −0,466 · K −0,463 … +0,425 · H1 +0,428 … +0,794 · K +0,797 … +0,834 · H1 +0,838 … +0,928 · K +0,931 · H1 +0,934 · H2 +0,938 … +1,000 |
| 15/16 | H2 −1,000 … −0,981 · H1 −0,978 … −0,956 · K −0,953 … −0,947 · H1 −0,944 … −0,869 · K −0,866 … −0,825 · H1 −0,822 … −0,381 · K −0,378 … +0,347 · H1 +0,350 … +0,722 · K +0,725 … +0,759 · H1 +0,762 … +0,859 · H2 +0,863 … +1,000 |

### 4.4 Nicht monotone Bereiche

Das Einzugsgebiet des Kontaktasts ist in allen Laufarten mit Hüpfzuständen nicht monoton. Oberhalb des
ersten Hüpfwurfs einer Wurfphase folgen wieder Würfe, die zurückkehren (**Rückkehr-Inseln**). Die Zahlen
der Wurfphasen mit Rückkehr-Inseln gelten für das 0,05-Raster mit Bisektion (4.1):

- **L1:** im 0,05-Raster in 13 von 16 Wurfphasen für Δv > 0 und in 12 für Δv < 0. Beispiel t₀ = 0:
  Rückkehr bis +0,431, Hüpfen +0,434 … +0,509, Rückkehr +0,512 … +0,734, Hüpfen +0,738 … +0,750, Rückkehr
  +0,753 … +0,991, Hüpfen +0,994 … +1,000 m/s. In Wurfphase 8/16 kehrt im 0,05-Raster jeder Wurf bis
  ±1 m/s zurück. Das 0,01-Raster findet dort aber Hüpfpunkte (H1) bei −0,97, −0,77, −0,76, +0,66 und
  +0,83 m/s; +0,65 und +0,67 m/s kehren zurück (4.8). Im 0,01-Raster haben alle acht geprüften
  Wurfphasen Rückkehr-Inseln, je Vorzeichen.
- **(0°, 180°):** im 0,05-Raster in 16 bzw. 15 Wurfphasen; bis zu vier Hüpfbänder je Vorzeichen (t₀ = 0,
  Δv > 0).
- **Synchron:** im 0,05-Raster in 15 bzw. 16 Wurfphasen. Zwischen die Hüpfbänder schieben sich
  Rückkehr-Inseln von einem einzelnen Bisektionspunkt (schmaler als 0,007 m/s, etwa −0,903 bei
  t₀/T = 2/16) bis 0,18 m/s Breite (+0,472 … +0,656 bei t₀/T = 11/16). Auch bei t₀ = 0 liegt eine Insel
  oberhalb des ersten Hüpfwurfs: +0,681 … +0,713 m/s kehrt zurück, die Rasterzelle +0,70 m/s eingeschlossen.

Der Anteil der Würfe ohne Rückkehr wächst nicht monoton mit |Δv| (Anteil der Rasterzellen je Band):

| Laufart | Vorzeichen | \|Δv\| = 0,05–0,20 | \|Δv\| = 0,25–0,40 | \|Δv\| = 0,45–0,60 | \|Δv\| = 0,65–0,80 | \|Δv\| = 0,85–1,00 |
|---|---|---|---|---|---|---|
| L1 | Δv > 0 | 0 % | 0 % | 16 % | 5 % | 9 % |
| L1 | Δv < 0 | 0 % | 0 % | 16 % | 6 % | 6 % |
| synchron | Δv > 0 | 0 % | 64 % | 84 % | 66 % | 86 % |
| synchron | Δv < 0 | 0 % | 45 % | 81 % | 77 % | 81 % |
| (0°, 180°) | Δv > 0 | 0 % | 8 % | 27 % | 19 % | 19 % |
| (0°, 180°) | Δv < 0 | 0 % | 0 % | 33 % | 16 % | 23 % |

**Untere Einhüllende, keine Schwelle.** Das kleinste |Δv| mit Hüpfen über alle 16 Wurfphasen ist:

| Laufart | Δv > 0 | Δv < 0 | Stoßimpuls M·\|Δv\| | Fallhöhe \|Δv\|²/(2g) |
|---|---|---|---|---|
| L1 | +0,416 m/s (t₀/T = 2/16) | −0,484 m/s (2/16) | 0,270 / 0,315 N·s | 8,8 / 11,9 mm |
| (0°, 180°) | +0,381 m/s (2/16) | −0,444 m/s (2/16) | 0,248 / 0,289 N·s | 7,4 / 10,0 mm |
| synchron | +0,225 m/s (4/16) | −0,263 m/s (4/16) | 0,146 / 0,171 N·s | 2,6 / 3,5 mm |
| Schnitt, Piloten | – | – | – | – |

Unterhalb dieser Werte kehrt im Raster jeder Wurf zurück, in jeder Wurfphase. Oberhalb wechseln Rückkehr
und Hüpfen je nach Wurfphase und Δv. Ein Wurf über der Einhüllenden führt also nicht sicher ins Hüpfen,
und ein Wurf, der in einer Wurfphase zurückkehrt, kann in der Nachbarphase hüpfen. Die Werte gelten auf
±0,003 m/s; schmalere Hüpfbänder unterhalb können zwischen den Rasterpunkten liegen (4.8).

### 4.5 Kräfte im Einschwingen

Auch ein Wurf, der zurückkehrt, erzeugt beim ersten Aufsetzen bzw. beim Stoß ins Auflager hohe Kräfte.
Größte Kontaktkraft im ganzen Lauf über alle Wurfphasen:

| Laufart | \|Δv\| = 0,05 | \|Δv\| = 0,10 | \|Δv\| = 0,20 | \|Δv\| = 0,30 | \|Δv\| = 0,50 | \|Δv\| = 1,00 |
|---|---|---|---|---|---|---|
| L1 | 57 N | 112 N | 231 N | 351 N | 527 N | 987 N |
| Schnitt (21) | 56 N | 113 N | 211 N | 312 N | 497 N | 957 N |
| Piloten (3) | 57 N | 112 N | 208 N | 313 N | 492 N | 952 N |
| synchron | 66 N | 145 N | 370 N | 608 N | 611 N | 1072 N |
| (0°, 180°) | 62 N | 126 N | 257 N | 352 N | 537 N | 996 N |

Für Schnitt und Piloten liegt F_max im Lauf bei 0,83–1,13 kN je m/s Wurfgeschwindigkeit (|Δv| ≥ 0,1).
Das entspricht dem Stoß einer Masse M mit v auf eine Feder K, F ≈ v·√(K·M) = 0,99 kN·s/m · v. Synchron
liegen die Werte bei kleinen Würfen höher (370 N bei 0,2 m/s, Endzustand Kontaktast), weil dort schon
der Orbit die größte Wechselkraft hat. Bei 0,3 m/s stammt der Höchstwert (608 N) aus einem Lauf, der in
H1 endet (t₀ = 0); der größte Wert eines zurückkehrenden Wurfs ist dort 436 N. Die größte Kraft im ganzen
Raster ist 1 072 N (synchron, |Δv| = 1 m/s, ≈ 168·M·g).

### 4.6 Dämpfung ζ

Gröberes Raster: 8 Wurfphasen (t₀/T = 0, 1/8, …, 7/8), Δv = −1,0 … +1,0 m/s in Schritten von 0,1 m/s,
Grenzen per Bisektion auf ≤ 0,005 m/s; sechs Laufarten, ζ = 0,02 / 0,10 / 0,20 (3 024 Zellen, alle
eingeschwungen, längster Lauf 480 Perioden). Die Zeile ζ = 0,05 ist die Teilmenge des Hauptrasters auf
denselben Rasterpunkten.

| Laufart | ζ | Hüpfen [%] | irregulär [%] | Attraktoren (Stoßspitze) | kleinstes Δv > 0 / < 0 ohne Rückkehr | F_max im Lauf, max |
|---|---|---|---|---|---|---|
| L1 | 0,02 | 33,9 | 0,0 | H1 (P1, 1 Stoß je Periode, 481,5 N), H2 (P2, 1 Stoß je 2 Perioden, 965,7 N) | +0,344 / −0,366 | 1028 N |
| L1 | 0,05 | 4,8 | 0,0 | H1 (P1, 1 Stoß je Periode, 481,9 N) | +0,416 / −0,484 | 987 N |
| L1 | 0,10 | 0,0 | 0,0 | – | – / – | 933 N |
| L1 | 0,20 | 0,0 | 0,0 | – | – / – | 869 N |
| Schnitt (120°,240°) | 0,02 | 6,0 | 0,0 | H1 (P1, 3 Stöße je Periode, 157,9 N) | +0,200 / −0,200 | 973 N |
| Schnitt (120°,240°) | 0,05 | 0,0 | 0,0 | – | – / – | 934 N |
| Schnitt (120°,240°) | 0,10 | 0,0 | 0,0 | – | – / – | 882 N |
| Schnitt (120°,240°) | 0,20 | 0,0 | 0,0 | – | – / – | 822 N |
| Schnitt (100°,240°) | 0,02 | 8,3 | 0,0 | H1 (P1, 1 Stoß je Periode, 481,3 N), H2 (P1, 3 Stöße je Periode, 163,9 N) | +0,150 / −0,466 | 997 N |
| Schnitt (100°,240°) | 0,05 | 0,0 | 0,0 | – | – / – | 957 N |
| Schnitt (100°,240°) | 0,10 | 0,0 | 0,0 | – | – / – | 904 N |
| Schnitt (100°,240°) | 0,20 | 0,0 | 0,0 | – | – / – | 842 N |
| Schnitt (140°,240°) | 0,02 | 3,6 | 0,0 | H1 (P1, 3 Stöße je Periode, 165,0 N) | +0,600 / −0,500 | 983 N |
| Schnitt (140°,240°) | 0,05 | 0,0 | 0,0 | – | – / – | 944 N |
| Schnitt (140°,240°) | 0,10 | 0,0 | 0,0 | – | – / – | 892 N |
| Schnitt (140°,240°) | 0,20 | 0,0 | 0,0 | – | – / – | 831 N |
| Pilot (110°,252°) | 0,02 | 5,4 | 0,0 | H1 (P1, 3 Stöße je Periode, 162,8 N), H2 (P1, 1 Stoß je Periode, 481,0 N) | +0,500 / −0,200 | 990 N |
| Pilot (110°,252°) | 0,05 | 0,0 | 0,0 | – | – / – | 950 N |
| Pilot (110°,252°) | 0,10 | 0,0 | 0,0 | – | – / – | 897 N |
| Pilot (110°,252°) | 0,20 | 0,0 | 0,0 | – | – / – | 836 N |
| synchron (0°,0°) | 0,02 | 61,9 | 0,0 | H1 (P1, 1 Stoß je Periode, 482,9 N), H2 (P2, 1 Stoß je 2 Perioden, 967,3 N) | +0,212 / −0,225 | 1117 N |
| synchron (0°,0°) | 0,05 | 57,7 | 0,0 | H1 (P1, 1 Stoß je Periode, 483,7 N), H2 (P2, 1 Stoß je 2 Perioden, 968,6 N) | +0,225 / −0,263 | 1068 N |
| synchron (0°,0°) | 0,10 | 41,7 | 0,0 | H1 (P1, 1 Stoß je Periode, 486,8 N) | +0,250 / −0,338 | 1009 N |
| synchron (0°,0°) | 0,20 | 0,0 | 0,0 | – | – / – | 940 N |

- **ζ = 0,20:** In keiner der sechs Laufarten hüpft ein Wurf bis ±1 m/s.
- **ζ = 0,10:** Nur synchron hüpft (41,7 %, P1 mit 486,8 N).
- **ζ = 0,05:** L1 und synchron hüpfen; Schnitt und Pilot kehren zurück (4.1).
- **ζ = 0,02:** Alle sechs Laufarten hüpfen, auch Schnitt und Pilot. Dort tritt ein neuer Attraktor auf:
  P1 mit drei Aufsetzern je Periode, λ = 93,7 %, Stoßspitze 158–165 N. Bei (100°, 240°) und beim Piloten
  (110°, 252°) gibt es zusätzlich den P1-Attraktor mit einem Stoß von 481 N. Die untere Einhüllende sinkt
  bis auf +0,150 m/s (Schnitt (100°, 240°)) bzw. −0,200 m/s (Schnitt (120°, 240°), Pilot).
- F_max im Lauf hängt kaum von ζ ab (0,82–1,12 kN bei |Δv| = 1 m/s).

Die Karte hängt stark von ζ ab: Bei synchron reicht der Hüpfanteil über ζ von 0 bis 61,9 %. Die Laufart
wirkt ähnlich stark (bei ζ = 0,05 von 0 bis 57,7 %). ζ des Aufbaus ist nicht gemessen.

### 4.7 Kontaktgesetz

Hunt-Crossley-Gegenstück (n = 1,5; gleiche Tangentensteifigkeit in der Ruhelage, gleiche Stoßzahl wie
Kelvin-Voigt bei 0,5 m/s) für L1, Schnitt (120°, 240°) und synchron bei ζ = 0,05: 8 Wurfphasen,
Δv = +0,1 … +1,0 m/s in Schritten von 0,1 m/s, ohne Bisektion (240 Zellen). Wegen der Rechenzeit
(solve_ivp, ≈ 0,15 s je Periode im Dauerkontakt) entfallen negative Würfe und Bisektion; die Läufe dauern
60 Perioden, verlängert bis 120 (198 Zellen nach 60, 42 nach 120 Perioden eingeschwungen). Kelvin-Voigt:
Teilmenge des Hauptrasters auf denselben Punkten.

| Laufart | Kontaktgesetz | Hüpfen | Attraktoren (Stoßspitze) | erster Hüpfwurf je Wurfphase t₀/T = 0, 1/8, …, 7/8 [m/s] | F_max im Lauf, max |
|---|---|---|---|---|---|
| L1 | Kelvin-Voigt | 5 von 80 (6,2 %) | H1 (P1, 1 Stoß je Periode, 481,9 N) | 0,5 / – / 0,7 / – / – / – / 0,6 / 0,5 | 987 N |
| L1 | Hunt-Crossley | 0 von 80 (0,0 %) | – | – / – / – / – / – / – / – / – | 2388 N |
| Schnitt (120°,240°) | Kelvin-Voigt | 0 von 80 (0,0 %) | – | – / – / – / – / – / – / – / – | 934 N |
| Schnitt (120°,240°) | Hunt-Crossley | 13 von 80 (16,2 %) | H1 (P1, 3 Stöße je Periode, 272,5 N) | 0,3 / 1,0 / 0,4 / – / 0,3 / 0,3 / 0,2 / 0,4 | 2235 N |
| synchron (0°,0°) | Kelvin-Voigt | 50 von 80 (62,5 %) | H1 (P1, 1 Stoß je Periode, 483,7 N), H2 (P2, 1 Stoß je 2 Perioden, 968,6 N) | 0,3 / 0,3 / 0,3 / 0,3 / 0,3 / 0,4 / 0,7 / 0,5 | 1068 N |
| synchron (0°,0°) | Hunt-Crossley | 53 von 80 (66,2 %) | H1 (P1, 1 Stoß je Periode, 1052,2 N) | 0,3 / 0,3 / 0,3 / 0,3 / 0,3 / 0,4 / 0,7 / 0,5 | 2619 N |

- **Synchron:** gleiche erste Hüpfwürfe in allen acht Wurfphasen, aber Stoßspitze 1 052 N statt 484 N.
  Oberhalb des ersten Hüpfwurfs unterscheiden sich die Karten in 9 von 80 Zellen (6 × K → H1, 3 × H1 → K).
  Auch unter Hunt-Crossley ist die Karte nicht monoton: Bei t₀/T = 4/8 kehren +0,7 und +1,0 m/s zurück,
  bei 5/8 +0,9 m/s, bei 6/8 +1,0 m/s, jeweils über dem ersten Hüpfwurf.
- **L1:** Unter Hunt-Crossley hüpft keine der 80 Zellen (Kelvin-Voigt: 5).
- **Schnitt (120°, 240°):** Unter Hunt-Crossley hüpfen 13 von 80 Zellen in einen P1-Zustand mit drei
  Aufsetzern je Periode (Aufprall mit 0,161 m/s, Stoßspitze 272,5 N); unter Kelvin-Voigt keine. Der
  kleinste Hüpfwurf ist +0,2 m/s (t₀/T = 6/8, untere Einhüllende). Die Hüpfzellen liegen verstreut,
  etwa bei t₀/T = 6/8: +0,2 hüpft, +0,3 … +0,6 kehren zurück, +0,7 hüpft, +0,8 … +1,0 kehren zurück.
  Grund: Die Hunt-Crossley-Stoßzahl fällt mit der Aufprallgeschwindigkeit (e ≈ 1 − α·v): 0,95 bei 0,16 m/s,
  0,86 bei 0,5 m/s. Kleine Stöße sind also elastischer als im Kelvin-Voigt-Kontakt (e = 0,86 für jedes v)
  und gleichen Kelvin-Voigt mit ζ = 0,02 (e = 0,94). Dort tritt derselbe Attraktortyp auf (4.6).
- **Kräfte:** F_max im Lauf 2,2–2,6 kN statt ≈ 1 kN. Der Hunt-Crossley-Kontakt wird mit der Eindrückung
  steifer (Tangentensteifigkeit 1,5·K_h·δ^0,5).
- **Gegenprobe:** Unter Hunt-Crossley haben Kontaktast und Hüpforbits denselben Betrag der
  Floquet-Multiplikatoren, |μ| = 0,7855. Das ist erwartet: Nach Liouville ist det J = exp(−1,5·α·∫N_el dt/M),
  und ∫N_el dt = M·g·T je Periode für jeden periodischen Orbit; also |μ| = exp(−0,75·α·g·T) = 0,7855.

Ob Schnittpunkte hüpfen können, hängt damit vom Kontaktgesetz ab. Robust gegen das Kontaktgesetz ist im
groben Raster nur der erste Hüpfwurf des synchronen Laufs: In allen acht Wurfphasen liegt er in beiden
Gesetzen auf demselben Rasterpunkt, bei t₀ = 0 bei 0,3 m/s. Darüber unterscheiden sich die Karten.

F_max_N der Hunt-Crossley-Zellen im Kontaktast ist ein Fensterwert des abklingenden Einschwingens, nicht
der Orbit: Im Dauerkontakt zieht die Abbildung nur mit |μ| = 0,79 je Periode zusammen, und die Läufe
dauern 60 bis 120 Perioden. Beispiel L1, t₀ = 0, Δv = 0,5 m/s: 13,8 N im Fenster nach 60 Perioden
(Wert in der CSV), 8,74 N nach 120 Perioden, gleich dem Orbit. Die Klassifikation K ist davon nicht
berührt. Die Orbitwerte stehen in `einzugsgebiete_v1_kandidat_hc_attraktoren.csv`: L1 8,75 N,
Schnitt (120°, 240°) 7,13 N, synchron 13,20 N.

### 4.8 Feinprüfung im 0,01-Raster

Das Hauptraster (Δv-Schritt 0,05 m/s) kann Hüpfbänder verfehlen, die zwischen zwei Rasterpunkten liegen.
Nachgerechnet sind L1, Schnitt (100°, 240°), (120°, 240°), (140°, 240°) und Pilot (110°, 252°) in acht
Wurfphasen (t₀/T = 0, 1/8, …, 7/8) mit Δv = −1,00 … +1,00 m/s in Schritten von 0,01 m/s, ohne Bisektion
(8 040 Zellen, ζ = 0,05, Kelvin-Voigt).

| Laufart | Zellen | Hüpfen | kleinstes Δv > 0 / < 0 mit Hüpfen | Hüpfbänder (davon im Hauptraster) |
|---|---|---|---|---|
| L1 | 1 608 | 95 (5,9 %; Hauptraster in denselben Phasen 5,2 %) | +0,42 / −0,49 m/s (Hauptraster +0,416 / −0,484) | 39 (14) |
| Schnitt (100°, 120°, 140°), Pilot (110°, 252°) | je 1 608 | 0 | – | 0 |

- Die vier geprüften Schnitt- und Pilotläufe kehren auch im feinen Raster aus jedem Wurf zurück. Die
  übrigen 18 Schnittpunkte und die Piloten (110°, 250°), (130°, 230°) sind nur im 0,05-Raster gerechnet.
- Bei L1 findet das feine Raster 25 zusätzliche Hüpfbänder. Sie sind schmal (höchstens 0,03 m/s zwischen
  den äußersten Punkten) und liegen alle bei |Δv| ≥ 0,63 m/s. Unterhalb der unteren Einhüllenden liegt
  keines. An den 328 gemeinsamen Punkten stimmen beide Raster überein.
- Auch bei t₀/T = 8/16, wo das 0,05-Raster für L1 nur Rückkehr zeigt, hüpfen im 0,01-Raster Würfe von
  −0,97, −0,77, −0,76, +0,66 und +0,83 m/s (H1); ihre Nachbarn im 0,01-Raster kehren zurück. Im
  0,01-Raster haben alle acht Wurfphasen Rückkehr-Inseln, je Vorzeichen (0,05-Raster: 13 bzw. 12 von 16).
- Die L1-Karte ist also oberhalb von ≈ 0,6 m/s in Zahl und Lage der Hüpfbänder unvollständig; auch das
  0,01-Raster kann schmalere Bänder verfehlen. Die untere Einhüllende von L1 und die Rückkehr der vier
  geprüften Schnitt- und Pilotläufe bestätigt die Feinprüfung.

---

## 5 · Grenzen der Aussage

- **1 FG.** Nur der Hub des Körpers. Kippmoden, Seitenführung, Rahmen- und Fußelastizität fehlen. Die
  Zellkräfte einzelner Wägezellen und die Lage der Module (L1 gegen L2, L3) wirken erst über Kippmoden.
- **Kontaktgesetz.** Kelvin-Voigt mit Ablösung bei N = 0 wie die Engine. Der Hunt-Crossley-Vergleich
  hängt an der angenommenen Zuordnung (gleiche Tangentensteifigkeit, gleiche Stoßzahl bei 0,5 m/s). Für
  den realen Fußkontakt ist keines der Gesetze gemessen.
- **Parameter.** K, ζ, Massen, Hub und Profil sind Auslegungswerte, nicht gemessen (P0.4 und P0.5 stehen
  aus). ζ ist die größte Unbekannte; Abschnitt 4.6 zeigt, wie stark die Karte davon abhängt.
- **Wurf.** Idealer Geschwindigkeitsstoß auf den Körper zu einem Zeitpunkt. Reale Störungen (Anstoßen,
  Kabelzug, Phasensprung, Rampe) haben Dauer und Form; die Karte ordnet sie nur über ihren Impuls ein.
- **Startzustand.** Immer der Kontaktast. Ein Wurf auf einen schon hüpfenden Körper ist nicht gerechnet.
  Der Anlauf über eine Frequenzrampe ist kein Wurf und nicht Teil der Karte.
- **Raster.** 16 Wurfphasen, Δv-Schritt 0,05 m/s, Grenzen nur in Δv verfeinert. Bänder und Inseln
  schmaler als das Raster können fehlen; bei L1 oberhalb 0,6 m/s fehlen nachweislich welche (4.8). Die
  Feinprüfung im 0,01-Raster umfasst nur L1, S100, S120, S140 und P110-252 in 8 Wurfphasen. |Δv| > 1 m/s
  ist nicht gerechnet. ζ- und Hunt-Crossley-Vergleich nutzen gröbere Raster.
- **Klassifikation.** Endzustand nach höchstens 80 s. Sehr lange Transienten, Attraktoren mit Periode > 30
  oder Zustände, die erst später wechseln, sind als irregulär ausgewiesen oder nicht erfasst.
- **Stoßspitzen** sind Modellwerte des starren Körpers auf einer Feder. Sie hängen vom Kontaktgesetz ab
  (Abschnitt 4.7) und sind nur in der Größenordnung belastbar.

---

## 6 · Folgerungen

Nur soweit die Daten sie tragen (Modell, gerechnete Parameter):

1. **Konfirmatorische Läufe und Piloten.** Bei ζ = 0,05 und Kelvin-Voigt hüpft im Raster (16 Wurfphasen,
   Schritt 0,05 m/s, |Δv| ≤ 1 m/s) kein Schnitt- und kein Pilotlauf. Im 0,01-Raster ist das an S100, S120,
   S140 und P110-252 bestätigt (8 Wurfphasen), für die übrigen 20 nicht gerechnet. Die Aussage hängt aber
   an ζ und am Kontaktgesetz: Bei ζ = 0,02 hüpfen alle geprüften Schnittpunkte und der Pilot (110°, 252°),
   mit Hunt-Crossley auch (120°, 240°) bei ζ = 0,05. Monostabilität der konfirmatorischen Konfigurationen
   ist damit nicht modellunabhängig belegt.
2. **Einzelmodulläufe.** L1–L3 laufen in jedem Kontrollsatz (Präreg §6). Mit Kelvin-Voigt und ζ = 0,05
   können sie hüpfen, in einen stabilen Zustand mit 482 N Stoßspitze. Der kleinste Hüpfwurf ist +0,416 m/s
   (untere Einhüllende, keine Schwelle; 0,27 N·s, 8,8 mm Fallhöhe), bei ζ = 0,02 +0,344 m/s. Darüber hüpft
   L1 nur in schmalen Bändern; die meisten größeren Würfe kehren zurück (Hüpfanteil 5,6 %). Unter
   Hunt-Crossley hüpft L1 im groben Raster nicht.
3. **Synchron und (0°, 180°).** Sie haben die größten Hüpfanteile (57 % bzw. 14 % der Zellen) und die
   kleinste untere Einhüllende (synchron 0,225 m/s, 2,6 mm Fallhöhe); synchron gibt es zusätzlich einen
   P2-Zustand mit 969 N. Synchron hüpft noch bei ζ = 0,10 und unter Hunt-Crossley. Das stützt die Regel in
   Präreg §6, die Rampe nie durch die synchrone Phasung zu führen. Werden die Zusatzkonfigurationen
   gemessen, sind sie die Läufe mit dem größten Risiko.
4. **Ein erreichter Hüpfzustand bleibt.** Jeder gerechnete Wurf mit |Δv| ≥ 0,02 m/s hebt zunächst ab
   und setzt wieder auf: Im Hauptraster haben alle 16 777 Kontaktast-Zellen mit Δv ≠ 0 einen Aufsetzer im
   Lauf; im 0,01-Raster bleiben nur zwei Würfe von −0,01 m/s (L1) im Kontakt. Ohne Hüpfattraktor
   kehrt der Wurf von selbst in den Kontakt zurück. Ein Lauf, der einen Hüpfattraktor erreicht hat, kehrt
   im Modell dagegen nicht von selbst zurück; alle Hüpfattraktoren sind stabil (|μ| = 0,74–0,94).
   Präreg §9.1 G6 macht einen Lauf mit Einzelzell-Liftoff ungültig, §9.2 S2 hält die Messung an
   (ausgenommen Läufe, die nach G5, G8 oder G10 ungültig sind, etwa nach einer äußeren Störung). Beide
   Regeln erfassen schon das kurze Abheben eines zurückkehrenden Wurfs.
   Zusätzlich folgt aus der Karte nur: Sobald Hüpfen erkannt ist, Antrieb anhalten bzw. neu anlaufen,
   weil der Hüpfzustand sonst bis zum Laufende bestehen bleibt, auch in einem nach G8 ausgenommenen Lauf.
   Hüpfen ist eindeutig zu erkennen: λ = 94–99 % und Stoßspitzen von 158–1 052 N, gegen ≤ 13,3 N auf
   dem Kontaktast-Orbit (alle ζ, beide Kontaktgesetze).
5. **Anlauf.** Die Karte beschreibt Störstöße auf den laufenden Kontaktast, nicht den Anlauf selbst. Ob
   eine Rampe den Körper aus dem Kontaktast wirft, zeigt sie nicht. Dafür ist je Laufart eine eigene
   Rechnung nötig (`ereignisloeser.py --rampe`).
6. **Überlastschutz.** Schon Würfe, die zurückkehren, erzeugen Kräfte von ≈ 1 kN je m/s (Kelvin-Voigt;
   0,83–1,13 kN je m/s bei Schnitt und Piloten), unter Hunt-Crossley bis 2,6 kN bei 1 m/s. Hüpfattraktoren
   tragen Stoßspitzen von 158–969 N (Kelvin-Voigt) bzw. 273–1 052 N (Hunt-Crossley). Das sind
   Summenkräfte des starren Körpers im 1-FG-Modell; die Verteilung auf die drei Zellen ist nicht gerechnet.
   Nennlast und Überlastanschlag nach Präreg §5.1 müssen Summenkräfte dieser Größenordnung aufnehmen,
   oder Stöße sind konstruktiv zu begrenzen. Welche Störgeschwindigkeiten real auftreten, sagt das Modell
   nicht.
7. **Dämpfung.** ζ = 0,20 unterdrückt im Modell jedes Hüpfen bis ±1 m/s in den sechs geprüften
   Laufarten; ζ = 0,10 lässt nur synchron hüpfen. ζ ist nicht gemessen (P0.4). Vor dem Einfrieren der
   Präregistrierung ist die Karte mit gemessenen K, ζ und Kontaktgesetz neu zu rechnen.

---

## 7 · Reproduktion und Dateien

Aus dem Repository-Wurzelverzeichnis; benötigt numpy und scipy, für `--zusammenfassung` pandas. Die
Rechnung ist deterministisch. Rechenzeiten mit drei Prozessen:

```sh
python3 code/einzugsgebiete.py --pruefung                                    # Abschnitte 3.5, 3.6; 25 s
python3 code/einzugsgebiete.py --raster voll --laufart alle \
        --out data/einzugsgebiete_v1_kandidat.csv                            # 4.1–4.5; 63 min
python3 code/einzugsgebiete.py --raster grob --laufart empfindlichkeit --zeta 0.02 0.1 0.2 \
        --out data/einzugsgebiete_v1_kandidat_zeta.csv                       # 4.6; 15 min
python3 code/einzugsgebiete.py --raster grob --laufart hc --law hc --dv-min 0.1 --keine-grenzen \
        --out data/einzugsgebiete_v1_kandidat_hc.csv                         # 4.7; 9 min
python3 code/einzugsgebiete.py --raster grob --dv-schritt 0.01 --keine-grenzen \
        --laufart L1 S100 S120 S140 P110-252 \
        --out data/einzugsgebiete_v1_kandidat_fein.csv                       # 4.8; 24 min
python3 code/einzugsgebiete.py --zusammenfassung data/einzugsgebiete_v1_kandidat.csv   # Tabellen (Markdown)
python3 code/einzugsgebiete.py --raster voll --wurfphasen 4 --laufart synchron --start ruhe \
        --out vergleich_ruhe_synchron.csv                                    # 4.2, Start Ruhelage; 2 min
python3 code/einzugsgebiete.py --raster voll --wurfphasen 8 --laufart L1 --start ruhe \
        --out vergleich_ruhe_L1.csv                                          # 4.2, Start Ruhelage; 2 min
```

Die beiden letzten Läufe schreiben Vergleichsdateien in das aktuelle Verzeichnis; sie gehören nicht ins
Repository. Verglichen werden ihre `_grenzen.csv` mit `data/einzugsgebiete_v1_kandidat_grenzen.csv`.

| Datei | Inhalt |
|---|---|
| [`data/einzugsgebiete_v1_kandidat.csv`](../data/einzugsgebiete_v1_kandidat.csv) | Hauptraster, 17 712 Zeilen: eine je Rasterzelle mit allen Konfigurationsparametern, t0_T, dv_m_s, impuls_Ns, attraktor, zustand, periode, aufsetzer_je_periode, lambda_pct, F_max_N, stossspitze_N, F_max_lauf_N, stossspitze_lauf_N, perioden, status |
| [`data/einzugsgebiete_v1_kandidat_grenzen.csv`](../data/einzugsgebiete_v1_kandidat_grenzen.csv) | 315 Bisektionsklammern (dv_links, dv_rechts ≤ 0,005 m/s auseinander, Attraktor links und rechts) |
| [`data/einzugsgebiete_v1_kandidat_attraktoren.csv`](../data/einzugsgebiete_v1_kandidat_attraktoren.csv) | Signatur je Attraktor und Laufart (Newton-Werte, \|μ\|max, Aufsetzphase, Zellenzahl) |
| [`data/einzugsgebiete_v1_kandidat_intervalle.csv`](../data/einzugsgebiete_v1_kandidat_intervalle.csv) | je Laufart und Wurfphase die Δv-Intervalle gleichen Endzustands |
| [`data/einzugsgebiete_v1_kandidat_kennwerte.csv`](../data/einzugsgebiete_v1_kandidat_kennwerte.csv) | je Laufart Anteile, untere Einhüllende je Vorzeichen, Wurfphasen mit Rückkehr-Inseln, Kräfte |
| `data/einzugsgebiete_v1_kandidat_zeta*.csv` | dasselbe für ζ = 0,02 / 0,10 / 0,20 (grobes Raster, 3 024 Zeilen) |
| `data/einzugsgebiete_v1_kandidat_hc*.csv` | dasselbe für Hunt-Crossley (240 Zeilen, ohne Grenzen) |
| `data/einzugsgebiete_v1_kandidat_fein*.csv` | Feinprüfung im 0,01-Raster (8 040 Zeilen, ohne Grenzen) |

Spaltenbedeutung: `attraktor` K Kontaktast, H1, H2, … Hüpfzustände je Laufart (Nummern gelten nur
innerhalb einer Laufart und eines ζ), X irregulär; `lambda_pct` Liftoff-Anteil im Auswertefenster;
`F_max_N` größte Kontaktkraft im Fenster (bei Hunt-Crossley-Zellen im Kontaktast ein Wert des noch
abklingenden Einschwingens, nicht der Orbit; Orbitwerte in der Attraktortabelle, Abschnitt 4.7);
`stossspitze_N` größte Stoßspitze im Fenster; `*_lauf_*` über den ganzen Lauf; `K_N_m`
Kelvin-Voigt-Steifigkeit bzw. bei Hunt-Crossley die Tangentensteifigkeit in der Ruhelage, `hc_Kh_N_m_n` =
K_h in N/m^1,5. Alle Werte sind Simulation, keine Messdaten.
