# P2 · Gegenprüfung der Prüfgruppe „kippmoment“

> **Vermerk zur Übernahme (04.10.2026).** Protokoll aus der Gesamtprojektanalyse 10/2026, Stand 02.10.2026, unverändert bis auf Pfade und Quellenangaben. Geprüft wurde der Repository-Stand `cd7be6a` (28.09.2026) mit der Präregistrierung v2 vom 25./28.09.2026; die späteren Änderungen aus PR #13 und PR #14 (unter anderem Präregistrierung v2 mit Arbeitsfestlegungen, `code/auslegung.py`, `code/ereignisloeser.py`) sind nicht eingearbeitet. Alle Zahlen sind Simulation oder Analytik, keine Messdaten. Verweise wie „L1a-019“, „P1 §3“ oder „B01–B14“ zeigen auf Arbeitsdokumente der Analyse, die nicht im Repository liegen. Quellen außerhalb des Repositorys sind als „(lokaler Bestand, nicht im Repository)“ gekennzeichnet. Startbefehle und Grenzen je Gruppe: [`rechnungen/README.md`](../../README.md).

Stand 02.10.2026 · ursprünglich lokal, jetzt unter `rechnungen/` · Rolle: unabhängiger Gegenprüfer (Ziel: Befunde widerlegen).
Kennzeichnung: **[R]** eigene Rechnung, **[Q]** Quellenangabe, **[A]** Annahme.

## Vorgehen und Unabhängigkeit

Geprüft wurden sieben Befunde: KM-01, KM-04, KM-05, KM-06, KM-07, KM-08 und KM-09. Ausgewählt nach V1-Bedeutung
„hoch“, Bewertung „neu“ und danach, ob Empfehlungen auf den Zahlen beruhen. KM-02, KM-03, KM-10, KM-11 und KM-12
wurden nicht eigens geprüft. Zu KM-10 und KM-11 gibt es nur Stichproben unter „Zusatzbefunde“.

Eigene Implementierung (`vf_modell.py`). Sie importiert nichts aus `km_modell.py` und nichts aus `code/finesweep.py`.
Der Rechenweg ist bewusst ein anderer:

- **Koordinaten:** die drei Zelleinfederungen w_j mit linearen Formfunktionen des Zelldreiecks,
  N_j = 1/3 + 2/(3R_c²)·(x·x_j + y·y_j). Die Gruppe rechnet mit Hub z und Neigungen a, b.
- **Massenmatrix in Zellkoordinaten:** M_w = M_f·[1/9 + 4ρ_f²/(9R_c²)·cos(ψ_j − ψ_k)] + Σ m_i N(X_i)N(X_i)ᵀ.
  Steifigkeit und Dämpfung sind diagonal (K/3, C/3).
- **Fourier-Koeffizienten des Egg-Profils:** analytisch als geschlossene Integrale der Sinusbögen, nicht per FFT.
  Abweichung gegen FFT: 5,8·10⁻¹⁰ m/s².
- **Quasistatischer Fall:** direkt im Zeitbereich mit 20 000 Stützstellen je Periode.
- **Nichtlinearer Fall:** eigenes RK4 in Zellkoordinaten. Die Anregung wird in jedem Teilschritt direkt aus dem
  Profil ausgewertet (keine Tabelle). Kontrolllauf mit Δt = 25 µs.

Übernommene Annahmen der Gruppe (für die Vergleichbarkeit, ausdrücklich **[A]**):
- Zellen auf R_c = 100 mm bei 0°/120°/240°.
- Geometrien G0, G60, G0h, G60h und Zc wie bei der Gruppe.
- Rahmen mit ρ_f = R_c/2, wo nicht anders angegeben.
- μ = 1 / 0,462 / 0,4.
- STEIF: K = 369 518 N/m, ζ = 0,02.

Prüfungen der eigenen Skripte:
- Phasenvorzeichen: Verzögerung τ = φ/(2πf), Fourier e^{−ikφ}.
- Grad/Radiant nur an den Schnittstellen umgerechnet.
- RK4-Teilschritte nachgeprüft (k2w = v + Δt/2·a1, k3w = v + Δt/2·a2, k4w = v + Δt·a3).
- Stichprobe der Zellkraft am Schrittanfang wie in der Engine.
- Kurztest gegen die Engine (unten).

Python-Aufruf für alle Befehle (aus diesem Verzeichnis):

```
PY="env PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 PYTHONPATH=../../../code python3"
cd rechnungen/kippmoment/verifikation
```

| Skript | Inhalt | Ausgabe | Laufzeit |
|---|---|---|---|
| `vf_modell.py` | unabhängiges Modell | – | – |
| `v1_eigenfrequenzen.py` | KM-05 | `v1_eigenfrequenzen_ausgabe.txt` | < 2 s |
| `v2_linear_zellkraefte.py` | KM-06, KM-08, KM-04, KM-09 | `v2_linear_zellkraefte_ausgabe.txt` | ≈ 60 s |
| `v2b_rho_empfindlichkeit.py` | Empfindlichkeit gegen ρ_f (linear) | `v2b_rho_empfindlichkeit_ausgabe.txt` | ≈ 30 s |
| `v3_kurztest.py` | eigenes RK4 gegen Engine (0°,0°), 1 s | `v3_kurztest_ausgabe.txt` | ≈ 20 s |
| `v3_nichtlinear_zellen.py A 50` / `A 25` | KM-07, 3-FG REF, zwei Starts, Δt 50/25 µs | `v3_teilA_dt50_ausgabe.txt`, `v3_teilA_dt25_ausgabe.txt`, `.json` | 70 s / 145 s |
| `v3_nichtlinear_zellen.py B 50` | μ = 1, G0 entkoppelt; acht Startparitäten | `v3_teilB_dt50_ausgabe.txt` | 40 s |
| `v3_nichtlinear_zellen.py C 50` | STEIF μ = 1 (chaotisch) | `v3_teilC_dt50_ausgabe.txt` | 40 s |
| `v3_nichtlinear_zellen.py D 50` | REF μ = 0,462 G0 T, ρ_f variiert | `v3_teilD_dt50_ausgabe.txt` | 40 s |

**Kurztest [R]** (`v3_kurztest.py`): Bei μ = 1, G0 gilt in der eigenen Zellkoordinaten-Implementierung
3·F_Zelle1 gegen Engine `finesweep.run(0,0)`, beide ab t = 0:

| bis t | max. Abweichung |
|---|---|
| 0,1 s | 2,1·10⁻¹⁴ N |
| 0,5 s | 8,3·10⁻¹³ N |
| 1,0 s | 1,9·10⁻¹⁰ N |

Damit ist die Entkopplung unabhängig bestätigt. Das Fehlerwachstum (≈ 9–11 s⁻¹) entspricht dem Nebenbefund der Gruppe.

---

## KM-01 · Geometrieangaben im Bestand

**Frage.** Stimmen die Fundstellen, und fehlt die Geometrie wirklich?

**Methode.** Fundstellen geöffnet (grep/sed).

**Ergebnis [Q].**
- Präreg-Anhang A2.5, Z. 191–201: „jedes Modul über einer Zelle“, „die Lage ist offen (§12)“ – wörtlich vorhanden.
  Die lokale Überarbeitung vom 01.10. (Technischer Anhang, Z. 206–211) ist unverändert.
- Hauptdokument Z. 557: „Lage von Zellen und Modulen (bestimmt die Zellkräfte, A2.5, und E3)“ unter „Weitere Klärungen“.
- E3 steht in Z. 143–146 mit der Harmonischen-Aussage.
- Laborplan V1, §5: „Eine DMS-Wägezelle (… ~3–5 kg …)“, „≥ 2 kSPS“. Module ~50–150 g.
- Notiz Prüfarchitektur Linie B, Z. 148: „Trägheitsradius (5 mm zu etwa 50 mm)“.
- `pcmms_s2_dreieck(a).html.txt`, Z. 70: `triRad=0.15`.
- Schwellen_eps, Z. 36: „keine Standbreite und keine Schwerpunkthöhe“.
- Maße oder Trägheitsmomente für V1 wurden nicht gefunden.

**Ergänzung [Q].** Die Gruppe erwähnt nicht, dass der Laborplan V1 (Tabelle Richtwerte und §3) ausdrücklich einen
**weichen** Kontakt vorsieht: „weiches Elastomer/Feder, k und c bekannt“; „Die weiche Lagerung ist physikalisch
notwendig, um bei 10 Hz überhaupt in den Liftoff-Bereich zu kommen“. Präreg v2 setzt dagegen steife Zellen mit
kinematischer Lagerung voraus (A4 Z. 240–241, A9.1). Dieser Widerspruch entscheidet darüber, ob der REF- oder der
STEIF-Fall für V1 maßgeblich ist (siehe KM-07).

**Urteil: bestätigt.**

**Reproduktion.**
```
cd .
sed -n 185,205p docs/praeregistrierung_v2_anhang.md
sed -n 555,559p docs/praeregistrierung_v2_entwurf.md
grep -n Trägheitsradius (lokaler Bestand, nicht im Repository)
sed -n 40,62p (lokaler Bestand, nicht im Repository)
```

**Einschränkung.** Stichprobe, keine Vollsuche.

---

## KM-05 · Kipp-Eigenfrequenzen

**Frage.** Wo liegen die Kippmoden?

**Methode [R].** Eigenwerte von M_w⁻¹·(K/3)·I in Zellkoordinaten. Daneben die geschlossene Formel:
f_Kipp = √(K R_c²/2 / J)/2π mit J = (1−μ)Mρ_f² + μMR_m²/2.

**Ergebnis [R]** (numerisch = analytisch auf 3 Nachkommastellen):

| Fall | Geometrie | ρ_f/R_c | f_Kipp |
|---|---|---|---|
| REF μ = 1 | G0 | – | **19,741 Hz** (dreifach entartet), 2f/f_Kipp = 1,013 |
| REF μ = 1 | G60h | – | 39,481 Hz |
| REF μ = 0,462 | G0 | 0,35 / 0,5 / 0,7 | 25,618 / 23,089 / 19,848 Hz |
| STEIF μ = 0,462 | G0 | 0,35 / 0,5 / 0,7 | 155,725 / 140,353 / 120,651 Hz |
| STEIF μ = 0,462 | G60h | 0,35 / 0,5 / 0,7 | 241,3 / 193,5 / 149,7 Hz |

Weitere Werte:
- 3f/f_Kipp ≤ 0,249 im STEIF-Fall.
- Platte mit 1,5·R_c: f_Kipp/f_Hub = 0,968.
- ζ_Kipp = 0,1161 = ζ·f_Kipp/f_Hub (REF μ = 0,462).

**Urteil: bestätigt.** Kleine Wortkorrektur: 19,74 Hz liegt 1,3 % unter 2f. „Nahe 2f“ trifft es besser als „genau bei 2f“.

**Reproduktion.** `$PY v1_eigenfrequenzen.py`

**Einschränkung.** Gleiche Modellklasse wie die Gruppe: flacher starrer Körper, nur senkrechte Bewegungen.

---

## KM-06 · Einzelzellkräfte, Summe, Momente; Präzisierung von A2.5

**Frage.** Stimmen die Zahlen? Stimmt die Aussage „A2.5 gilt exakt nur bei H = 1 oder bei μ = 1 mit G0“?

**Methode [R].**
- Linear im Frequenzbereich, Zellkoordinaten, k ≤ 400.
- STARR direkt im Zeitbereich.
- Zusätzlich G0 mit ρ_f = R_c/√2 und eine ρ_f-Variation (`v2b`).

**Ergebnis [R].** Alle Tabellenwerte der Gruppe sind reproduziert:

| Fall | Zelle min | weitere Werte |
|---|---|---|
| REF μ = 1, G0, T | −6,3081 N | N_min 5,3304 N |
| REF μ = 1, G0h, T | 0,4487 N | – |
| REF μ = 0,462, G0, T | −0,2168 N | N_min 5,8932 N |
| STEIF μ = 0,462, G0, T | 0,8498 N (40,0 %) | – |
| STEIF μ = 0,462, G60, T | 0,0006 N | – |
| STARR μ = 0,462, G0, T | 0,9563 N (45,0 %) | N_min 5,5319 N (Summe/3 86,8 %); Zelle SS 3,340 N, N SS 1,396 N; R+₁ 0,2247 N·m, R−₂ 0,0741 N·m |
| Z (0°, 110°, 240°) | – | N₁ = 0,2611 N, R−₁/R+₁ = 0,0583 (δ/3 = 0,0582) |
| S | – | Moment 3·10⁻¹⁶ N·m |

STEIF μ = 0,462, G0, ρ_f = R_c/2: Zellreserve 35,2–42,7 % (10 Hz) und 10,8–18,9 % (12 Hz).

**Widerspruch zur Präzisierung der Gruppe.** Die Zellen entkoppeln exakt, sobald M_w ∝ I gilt. Bei G0 ist das genau
dann der Fall, wenn J = M·R_c²/2 ist (⇔ f_Kipp = f_Hub). Dafür gibt es zwei Wege: μ = 1 **oder jedes μ mit
ρ_f = R_c/√2**.
- Die Nebendiagonale von M_w beträgt bei μ = 0,462 und bei μ = 0,2 mit ρ_f = R_c/√2 höchstens 8·10⁻¹⁷ kg, bei
  ρ_f = R_c/2 dagegen 1,9·10⁻² kg.
- STEIF μ = 0,462, G0, ρ_f = R_c/√2: Die Zellreserve ist für **alle** Lauftypen gleich, 36,3 % (10 Hz) bzw. 15,3 %
  (12 Hz). Das ist genau die synchrone Grenze. Zeitverschiebungsgleichheit und „je Zelle die Grenze der synchronen
  Phasung“ gelten dort also exakt, obwohl μ < 1 ist.

Abhängigkeit von ρ_f (STEIF μ = 0,462, G0):

| ρ_f/R_c | 10 Hz | 12 Hz |
|---|---|---|
| 0,35 | 32,8–42,6 % | 12,2–20,0 % |
| 0,6 | 34,1–43,2 % | **2,8**–16,3 % |

Die 2,8 % bei ρ_f = 0,6 und 12 Hz deuten auf eine hohe Harmonische nahe der Kippmode hin (Interpretation:
f_Kipp = 130,2 Hz, 11·12 Hz = 132 Hz).

**Urteil: eingeschränkt.**
- Die Zahlen stimmen.
- Die Ausschließlichkeit „nur μ = 1“ ist falsch. Richtig ist: G0 und f_Kipp = f_Hub.
- Die Spannweiten und die „ungünstigste Konfiguration“ hängen von der unbekannten Rahmenträgheit ab.

**Reproduktion.** `$PY v2_linear_zellkraefte.py` (Teile A, A2) und `$PY v2b_rho_empfindlichkeit.py`

**Einschränkung.** Linear und bilateral; Geometrie und ρ_f angenommen.

---

## KM-07 · Nichtlinear: Einzelzell-Liftoff

**Frage.** Stimmen λ_Zelle, λ_Summe, F_max, Schiefe und F_min? Trägt die Folgerung „Engine-Dauerkontakt am
Triphasik-Punkt gilt nicht für einen Körper auf drei Zellen“?

**Methode [R].**
- Eigenes RK4 in Zellkoordinaten, 15 s, Auswertung 10 s nach 5 s Burn-in, Liftoff F < 10⁻⁹ N.
- Zwei Starts: Ruhe im statischen Gleichgewicht, sowie Start auf der linearen periodischen Lösung bei t = 0
  (im Frequenzbereich berechnet; anderer Weg als der 5-s-Vorlauf der Gruppe).
- Δt = 50 und 25 µs.
- Teil B: entkoppelte Einmassenschwinger mit Startverzögerung 0 oder T → alle acht Paritätskombinationen.
- Teil D: ρ_f variiert.

**Ergebnis [R].** Δt = 25 µs ändert die nicht chaotischen Fälle nur in der 4. Stelle.

| Fall | Ergebnis |
|---|---|
| μ = 1, G0, T, Standardstart | λ_Zelle 75,79 % (Engine (0°,0°) laut `data/sweep_19x19.csv`: 75,7885 %), 3·F_max 41,12 N; λ_Summe **56,44 %**, N_max 24,97 N, Schiefe 1,031, max\|F(t) − F(t−T)\| = 13,7 N |
| μ = 1, G0, T, Start auf linearem Orbit | λ_Summe **37,05 %**, Schiefe 0,834 |
| Teil B, acht Paritäten | Nur zwei Werte: 56,45 % (alle drei Zellen gleiche Parität) und 37,06 % (eine abweichend). Die Spanne „37–56 %“ der Gruppe ist damit vollständig. |
| μ = 0,462, G0, T (ρ_f = R_c/2) | λ_Zelle 11,95 %, N_min 5,9641 N, Schiefe 0,0219 (linear 0,0668) |
| μ = 0,462, G0, Z (ρ_f = R_c/2) | λ_Zelle 17,25 %, Schiefe −0,9976 |
| μ = 1, G60h, T | λ_Zelle 22,35 %, N_min 5,4067 N, Schiefe 0,0984 |
| STEIF μ = 1, G0, T/Z | λ_Zelle 95,9–98,8 %, λ_Summe 92,8 / 91,8 %, N_max 350 / 361 N |

**Empfindlichkeit gegen die Annahme ρ_f (REF μ = 0,462, G0, T) [R]:**

| ρ_f/R_c | lin. Zelle min | λ_Zelle | N_min | Schiefe N |
|---|---|---|---|---|
| 0,35 | +0,316 N | 0 % | 5,8932 N | 0,0668 (= Engine) |
| 0,5 (Gruppe) | −0,217 N | 11,95 % | 5,9641 N | 0,0219 |
| 0,6 | −0,968 N | 29,3 % | **3,819 N** | −0,201 |
| 0,7071 (exakt entkoppelt) | −1,771 N | 26,9 % | **3,404 N** | −0,250 (nicht T-periodisch) |

**Urteil: eingeschränkt.**
1. Alle Zahlen der Gruppe sind mit unabhängigem Code reproduziert.
2. Die Aussagen für μ = 0,462 („12–17 % Liftoff verfälschen die Schiefe um Faktor 2,6–3“, „F_min 5,964 statt
   5,893 N“) sind ein einzelner Punkt einer stark annahmeabhängigen Kurve:
   - Je nach ρ_f reicht die Wirkung auf N_min von 0 bis −2,5 N.
   - Die Schiefe am Triphasik-Punkt wechselt sogar das Vorzeichen.
   - Die qualitative Aussage (Zell-Liftoff verfälscht die Summen-Observablen bei N > 0) wird dadurch gestärkt.
   - Die Zahlen sind nicht belastbar.
3. Der Titel verallgemeinert. Nur bei Modulen über den Zellen (G0) mit f_Kipp ≈ 2f fällt der Kontaktast weg. Bei
   G0h (μ = 1) gibt es keinen Liftoff, bei ρ_f = 0,35·R_c auch nicht.
4. REF (K = 10⁴ N/m) ist laut Präreg A4/A9.1 nicht die V1-Auslegung (steife Zellen). Im STEIF-Fall μ = 0,462 tritt
   kein Liftoff auf. V1-relevant wird der Befund nur bei weichem Kontakt wie im Laborplan V1.

**Reproduktion.**
```
for t in A B C D; do timeout 540 $PY v3_nichtlinear_zellen.py $t 50; done
timeout 540 $PY v3_nichtlinear_zellen.py A 25
timeout 540 $PY v3_kurztest.py
```

**Einschränkung.**
- Chaotische Fälle (μ = 1) sind nur statistisch definiert.
- Kelvin-Voigt-Kontakt, flacher Körper; Geometrie angenommen.

---

## KM-08 · Zellreserve je Zelle gegen Summe/3

**Frage.** Stimmen die Reserven für alle Lauftypen und Geometrien?

**Methode [R].** Wie KM-06. Lauftypen: Einzelmodul, drei Paare, synchron, (0°,0°,180°), drei Piloten, 21 Schnittpunkte
(Präreg §5.3/§5.4: Schnitt φ₂ = 100…140° bei φ₃ = 240°, Piloten (110,250), (130,230), (110,252)).

**Ergebnis [R].** Alle Werte stimmen auf 0,1 Prozentpunkte.

STARR μ = 0,462, 10 Hz (Zelle | Summe/3 am Schnitt):

| Geometrie | Schnitt | weitere Werte |
|---|---|---|
| G0 | 45,0 \| 78,3 % | – |
| G60 | 8,9 % | (0°,0°,180°): −7,4 %; Piloten 8,5–12,5 % |
| G0h | 61,6 % | – |
| G60h | 56,9 % | – |
| Zc | 78,3 % | – |

Synchron in allen Geometrien 45,0 %.

Weitere Fälle:

| Fall | Zellreserve |
|---|---|
| STARR μ = 0,462, 12 Hz, G0 | 20,8 % für alle Läufe |
| STEIF μ = 0,462, 10 Hz, G0 | 35,2–42,7 % |
| STARR μ = 0,4, G0 | 52,4 % (10 Hz) und 31,4 % (12 Hz), wie Präreg A4 |

Verhältnis Summe/3 zu Zelle am Schnitt: 78,3/45,0 = 1,74 (G0) und 78,3/8,9 = 8,8 (G60).

**Urteil: bestätigt.** Dabei ist die Neuheit zu relativieren: Die G0-Aussage (Zelle = synchrone Grenze, Summe/3
überschätzt) steht schon in Präreg A2.5/A4 („Maßgeblich ist aber die Zellkraft … 52,4 %“) und in §5.3(a). Neu sind
die Geometrievarianten und die dynamische STEIF-Korrektur. Letztere hängt von ρ_f ab (siehe KM-06).

**Reproduktion.** `$PY v2_linear_zellkraefte.py` (Teil B)

**Einschränkung.** Linear, volles Spektrum, gleicher Hub über f; Geometrie angenommen.

---

## KM-04 · Drehfeld-These

**Frage.** Ist (3/2)·m·A₁·R der Radius der Grundharmonischen? Ist |M| konstant? Welcher Umlaufsinn, welcher Mittelwert?

**Methode [R].**
- |M(t)| quasistatisch direkt aus dem Profil im Zeitbereich (ohne Fourier), 20 000 Stützstellen.
- Spektrum von |M|.
- Windungszahl über arg(M_x + iM_y).
- Dynamisch in Zellkoordinaten.

**Ergebnis [R].**
- A₁…A₆ = 14,9649 / 4,9321 / 2,128 / 0,322 / 0,4419 / 0,3989 m/s² (analytisch).
- (3/2)·m·A₁·R = 0,48636 N·m (μ = 1) bzw. 0,22470 N·m (μ = 0,462). Das ist gleich R+₁.
- |M| = 0,2882…0,6453 N·m, max/min = 2,239. |M| enthält nur die Harmonischen 3, 6, 9, 12.
- Sinusprofil: |M| = 0,49348 N·m konstant.
- R−₂/R+₁ = 0,3296.
- Phasen: arg P+₁ = −27,0°, arg P−₂ = 144,0°.
- Bei gespiegelter Modulzuordnung tauschen die Drehrichtungen.
- Mittelwert des Moments ≈ 10⁻⁹ N·m. Analytisch gilt im zeitlichen Mittel jeder beschränkten Bewegung ⟨F_j⟩ = F0_j,
  also ist der Mittelwert des Moments null, auch bei Liftoff.
- REF μ = 1, G0: R+₁ = 0,6516, R−₂ = 0,8062 N·m, |H_t(ω)| = 1,340, |H_t(2ω)| = 5,030, max/min 9,17, netto −2 Umläufe
  je Zyklus.
- REF μ = 0,462: ρ_f = 0,7 gibt −2 Umläufe; ρ_f = 0,5 gibt +1 Umlauf, max/min 12,45.

**Urteil: bestätigt.**

**Reproduktion.** `$PY v2_linear_zellkraefte.py` (Teil C)

**Einschränkung.** Linear (Dauerkontakt). Bei REF μ = 1 ist der Umlaufsinn nur formal, weil dort Liftoff auftritt.

---

## KM-09 · Leckage am Triphasik-Punkt

**Frage.** Stimmen δN₁, δN₂ und δF_min für 1 % bzw. 1°?

**Methode [R].** STARR im Zeitbereich mit gestörtem Modul bzw. gestörter Zelle; REF im Frequenzbereich.

**Ergebnis [R].** STARR μ = 0,462, G0:

| Störung | δN₁ | δN₂ | δF_min | R−₁/R+₁ |
|---|---|---|---|---|
| Masse M2 +1 % | 0,0150 N | 0,0049 N | −0,0019 N | 0,00332 |
| Hub M2 +1 % | 0,0150 N | 0,0049 N | −0,0117 N | 0,00332 |
| Phase M2 bzw. M3 +1° | 0,0261 N | 0,0172 N | −0,0541 N | 0,00582 |
| Zellverstärkung Z2 +1 % | 0,0150 N | 0,0049 N | +0,0096 N | 0,00332 |

- Im Verhältnis zu u_c: δN₁/u_c = 0,46 bzw. 0,80.
- REF μ = 1, G0, Masse +1 %: δN₂ = 0,2682 N (Gruppe 0,268 N). Davon stammen nur 0,0537 N aus der um 1 % größeren
  Anregung. Der Rest kommt aus der Verstimmung der Zellresonanz durch die Zusatzmasse. Die Erklärung der Gruppe
  trifft im Kern zu.

**Urteil: bestätigt.**

**Reproduktion.** `$PY v2_linear_zellkraefte.py` (Teil D)

**Einschränkung.** Linear; konstante Ungleichheiten fallen in H1 heraus (wie die Gruppe schreibt).

---

## Zusatzbefunde

1. **Entkopplungsbedingung allgemeiner als angegeben:** G0 und J = M·R_c²/2 (f_Kipp = f_Hub), für jedes μ. Das
   betrifft die Korrektur der Gruppe an A2.5 (KM-06) und den Satz „exakt nur bei μ = 1“ in KM-07.
2. **Rahmenträgheit als dominierende unbekannte Größe für REF:** N_min am Triphasik-Punkt 3,40–5,96 N; λ_Zelle 0–29 %
   für ρ_f = 0,35…0,71·R_c (μ = 0,462).
3. **Laborplan V1 gegen Präreg v2:** weicher Elastomer-Kontakt gegen steife Zellen. Erst diese Wahl entscheidet, ob
   KM-07 für V1 gilt.
4. **KM-11, Stichprobe [R]:** Präreg A6 (Anhang Z. 325–327): f_s ≥ π·k·f/√(2·10⁻³) ergibt 2107 Hz (k = 3) und
   3512 Hz (k = 5). σ_F aus den Annahmen der Gruppe nachgerechnet: 2,4 mN (2 mV/V, 15 nV/√Hz, 2 kSPS) bis 21,3 mN
   (1 mV/V, 50 nV/√Hz, 3,75 kSPS). A₁ = m·A₁ = 1,498 N = 45,8·u_c. Bestätigt.
5. **KM-10, Stichprobe analytisch [R]:** Zelle 2 radial um +1 mm (R_c = 100 mm). Baryzentrische Anteile von Modul 2:
   0,99338 auf Zelle 2, je 0,00331 auf Zellen 1 und 3. Daraus folgen:
   - −0,66 % am Modul;
   - Scheinanteile der Nachbarmodule 0,0033·sin 120° rad = 0,165° und 0,0033·cos 120° = −0,165 % in der Amplitude;
   - Momentkanal mit nominalen Hebeln −0,99 %, also R−₁/R+₁ ≈ 0,0033.

   Stimmt mit der Gruppe überein.
6. **Fehlerwachstum der Engine-Bahn (0°,0°):** mit eigener Implementierung nachvollzogen, ≈ 9 s⁻¹ (0,1 → 0,5 s)
   bzw. ≈ 11 s⁻¹ (0,5 → 1 s).

## Hinweise zu den Skripten der Gruppe

- `k5b_entkopplung_mu1.py`: Der Vergleich „3·F_j(t) − N_Engine(t − τ_j)“ für die Zellen 2 und 3 rundet τ_j auf ganze
  Stichproben (667 statt 666,67). Er vergleicht außerdem Bahnen mit verschiedener Startlage relativ zum Profil. Die
  ausgegebenen 41 N und 9 N sind daher kein Test. Die Gruppe stützt sich nicht darauf.
- Sonst keine Einheiten-, Vorzeichen- oder Parameterfehler gefunden. Phasenkonvention, Δt, Burn-in, Stichprobe am
  Schrittanfang und STEIF-Dämpfung C = 2·0,02·√(KM) = 19,60 N·s/m (f_n = 120,000 Hz) sind konsistent.
