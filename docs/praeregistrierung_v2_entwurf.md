# PCMMS — Präregistrierung v2 (Entwurf)

**Matthias Früh · ORCID 0009-0005-9984-4207**
Stand: 25. September 2026, überarbeitet 2. Oktober 2026 (§1: Einordnung der Vorzeichenregel; Entwurf 10/2026: Entscheidungsregeln, Anhang A0) und 3. Oktober 2026 (§5.1, §12: Verweise auf das Exposé) · Teil A, Entwurf — nicht eingefroren, nicht registriert

Teil A besteht aus diesem Hauptdokument und dem gleichrangigen *Technischen Anhang*
(`praeregistrierung_v2_anhang.md`, im Folgenden „Anhang“). Es gibt keine Messdaten. Jede Zahl ist ein
Simulationsergebnis des Repositorys, eine daraus abgeleitete Größe oder eine Festlegung; die Befehle stehen
im Zahlennachweis (Anhang Z).

## Kurzfassung

v2 ersetzt für die Messkampagne die Präregistrierung vom Juni 2026 (v1 bleibt unverändert). Gegenstand
ist nur Linie A: die Kontaktkraft N(t) eines ruhenden Körpers mit drei phasengesteuerten Innenmassen,
solange er auf allen Auflagepunkten Kontakt hält. Primär geprüft werden an 21 Punkten des Schnitts
φ₂ = 100° … 140° bei φ₃ = 240° die Superposition der einzeln gemessenen Modulantworten (H1) und die Lage
der Spitze der Zeltkurve (H2), also des Maximums von F_min (Minimum von N über einen Zyklus) entlang des
Schnitts; bei identischen Modulen hat F_min am Triphasik-Punkt (120°, 240°) einen Knick mit relativem
Maximum. Sekundär geprüft werden ein Kontaktmodell mit einem Freiheitsgrad an den Einzelmodulläufen (H3)
und das Vorzeichen der Schiefe (H4). ⟨N⟩ = M·g ist Kontrollgröße (H0), kein Ergebnis. Die Vorhersagen
entstehen aus Messungen an der Apparatur selbst (Phase 0) und werden vor Phase 1 in Teil B registriert;
eine gleich gebildete zweite Vorhersage aus Kontrollläufen der Phase 1 dient als Driftkontrolle. H1 wird
mit einem Äquivalenztest und einem Mindesteffekttest entschieden; die Ausgänge „äquivalent“, „relevant
abweichend“ und „nicht entscheidbar“ schließen sich aus. Jeder Ausgang, auch „nicht entscheidbar“, wird
veröffentlicht. Vor dem Einfrieren fehlen vor allem die Werkzeuge und die offenen Festlegungen aus §12.

---

## 0 · Status und zweistufige Registrierung

v1 (`praeregistrierung_2026-06.md`, 14. Juni 2026) wird nicht verändert und bleibt als Dokument des Weges
gültig. H1_fluid (Linie B) erhält eine eigene Präregistrierung.

- **Teil A** (Hauptdokument und Anhang): Fragestellung, Hypothesen, Definitionen, Protokolle, Auswertung,
  Entscheidungs-, Ausschluss- und Abbruchregeln, Regeln für alle erst zu messenden Werte. Eingefroren und
  extern mit Zeitstempel registriert (OSF Registries oder Zenodo), mit den Commit-Hashes von Protokoll und
  Auswertecode, **bevor Phase 0 beginnt**.
- **Teil B** (Vorhersage-Addendum): Ergebnisse der Phase 0, Werte aller Platzhalter, numerische
  Vorhersagen mit Unsicherheiten, Laufzahl und Laufreihenfolge (Inhaltsliste: Anhang A9.3). Extern
  registriert, **bevor Phase 1 beginnt**.

Ablauf: Teil A einfrieren → Phase 0 → Teil B registrieren → Phase 1 → Datenschluss → konfirmatorische
Auswertung, einmalig, mit dem registrierten Code → Veröffentlichung jedes Ausgangs → externe Replikation.
Die Aufnahmesoftware schreibt die Kennung der gültigen Registrierung (Teil A in Phase 0, Teil B in Phase 1)
in den Kopf jeder Rohdatei und startet ohne sie nicht; das SHA-256-Manifest aller Rohdateien, auch
ungültiger und abgebrochener Läufe, wird ab dem ersten Lauf der Phase 0 mindestens täglich als Commit im
öffentlichen Repository hinterlegt. Zu jeder Phase 1 gibt es genau einen Teil B.

**Schreibweisen.** *[Teil B]*: nach einer hier festgelegten Regel in Phase 0 bestimmter Wert.
*Festlegung*: gewählter Zahlenwert ohne Messung (Anhang, Tabelle F). Nach dem Einfrieren sind Änderungen
nur über das Abweichungsprotokoll (§10.3) zulässig.

**Verschiebungen gegen eine Referenz.** Der Grundsatz aus README und `overview.md`, keine Absolutkräfte,
sondern Abweichungen gegen eine Referenz zu messen, gilt für H0, H1, H2 und H4: F_min − ⟨N⟩ ist eine
Differenz zum Zeitmittel des Laufs, die Harmonischen N_k (k ≥ 1) enthalten keinen Gleichanteil, und Messung
und Vorhersage stammen aus denselben Zellen mit derselben Kalibrierung. Eine absolute Kalibrierung brauchen
nur H3 und die Abstände zum Abheben (§5.3, G6).

---

## 1 · Verhältnis zu v1 und zum Exposé

v1 fragte qualitativ nach einer Phasenabhängigkeit der Wellenform, die aus dem Newtonschen Gesetz folgt
(§2). v2 prüft quantitative Vorhersagen und registriert zweistufig, weil die Vorhersagen von Größen
abhängen, die erst Phase 0 misst. Die Bezeichnung H1 ist neu belegt. Alle Änderungen mit Gründen: Anhang A0.

**Vorhersagen des Exposés.** Von der Zeltkurve wird die Lage der Spitze registriert (H2), vorhergesagt aus
Messungen an der Apparatur. Höhe und Steigungen der Simulation (5,3304 N; 2°-Sekanten 118° → 120° bzw.
122° → 120°: 0,212 bzw. 0,195 N/°) werden nicht registriert, weil sie für K = 10⁴ N/m gelten, einen
Resonanzfall (Anhang A3). Die frühere allgemeine Vorzeichenregel der Schiefe — negative Schiefe nur bei
Dephasierung ohne gleichphasiges Modulpaar — ist mit Arbeitspapier v2.4 als Aussage über den Mechanismus
zurückgezogen. Schon ein einzelnes Modul kann bei geänderter Kontaktübertragung im Dauerkontakt
linksschief werden. Die positiven Werte auf den geprüften Linien des Referenzrasters (A3) bleiben
beschränkte Simulationsbefunde und begründen keine allgemeine Regel. Auch das Vorzeichen an einem
einzelnen dephasierten Punkt hängt vom Kontakt ab (Triphasik-Punkt: γ₁ = +0,067 bei K = 10⁴ N/m,
−0,450 bei starrer Auflage). Statt der zurückgezogenen Regel sieht v2 weiterhin H4 vor: das Vorzeichen
wird gegen die Superpositionsvorhersage aus den gemessenen Einzelmodulantworten geprüft.

**Schwellen.** ε_ctrl wird hier mit einer Definition von σ̂_ref festgelegt (§4, §8.8). Die Einordnung (§4)
nannte die Form 3·σ̂_ref; der Literaturabgleich (§4.2, T3) ordnete 3·σ̂_ref je Funktional ε_phys zu und nannte
ε_ctrl ohne Formel; der Werkstattbericht führte beide als offen. ε_phys wird für die Wellenformgrößen durch
standardisierte Residuen, einen Äquivalenztest und einen Mindesteffekttest ersetzt (§8.4, §8.5).

---

## 2 · Fragestellung

Solange ein ruhender Körper mit drei phasengesteuerten Innenmassen auf allen Auflagepunkten in Kontakt
bleibt:

1. Folgt N(t) quantitativ der Superposition der einzeln gemessenen Modulantworten — in F_min und N₁ … N₃
   entlang des Schnitts φ₂ = 100° … 140° bei φ₃ = 240°? (H1)
2. Liegt die Spitze der F_min-Zeltkurve dort, wo die Superposition sie vorhersagt? (H2)
3. Sagt ein Modell mit einem Freiheitsgrad (1 FG) und linear-elastischem, viskosem, unilateralem Kontakt
   die Einzelmodulantwort aus unabhängig gemessenen Parametern voraus? (H3)
4. Hat die Schiefe dort, wo die Superposition ein deutliches Vorzeichen vorhersagt, dieses Vorzeichen? (H4)

Dabei bleibt ⟨N⟩ innerhalb der Kontrollschwelle gleich der statischen Last (H0).

**Grundlage.** Im Kontaktast ist das Modell linear; jede Harmonische ist die Summe der
Einzelmodulantworten, N_k = Σⱼ N_k⁽ʲ⁾·e^{−ikφⱼ} (φ₁ = 0), ohne K, C oder μ zu kennen (Anhang A2.1). Dass
die Wellenform von der Phasenlage abhängt, folgt aus dem Newtonschen Gesetz und ist keine Hypothese. Bei
identischen Modulen hat F_min bei 120° für jeden linearen Kontakt einen Knick mit relativem Maximum (A2.2);
ob er das Maximum des Schnitts ist, hängt vom Kontakt ab (A5).

**Reichweite.** H1 kann an Kopplungen der Module, Nichtlinearitäten der Messkette und, soweit sich der
Körper auf der Auflage bewegt, an einem nichtlinearen Kontakt scheitern; in einem steifen Aufbau ist H1
überwiegend ein Test der Apparatur und wird so benannt. H2 zeigt Kopplungen, nicht konstante Phasenfehler
oder nicht erfasste Modulunterschiede. Über den Kontakt sagt H3 nur bei Harmonischen etwas aus, bei denen
sich Kontaktmodell und starre Auflage nachweisbar unterscheiden (§8.7). In einem steifen Aufbau ist das für
k ≤ 3 kaum der Fall (A4); H3 prüft dann Masse, Profil und Kalibrierung. Ob H3 dafür um eine Prüfung über
die Betriebsimpedanz des Kontakts ergänzt wird, ist offen (§8.7, §12). Der Liftoff-Bereich wird nicht
konfirmatorisch geprüft.

---

## 3 · Hypothesen

Alle konfirmatorischen Hypothesen beziehen sich auf den Arbeitspunkt f (§5.3) und auf auswertbare
Konfigurationen (§9.1); Sollphasen sind Profilphasen; α = 0,05 je Familie. Die Entscheidungsregeln stehen
vollständig in §9.3.

**H0 — Nullkontrolle.** Für jeden Lauf gilt |Δ⟨N⟩| ≤ ε_ctrl (§8.8). Ein Verstoß ist ein Apparaturfehler
oder eine Transiente, nie ein Effekt; er macht den Lauf ungültig (G1) und kann den Messbetrieb stoppen (S1).

**H1 — Superposition (primär).** An jedem der 21 Schnittpunkte stimmen F_min − ⟨N⟩ sowie Real- und
Imaginärteil von N₁, N₂, N₃ der Konfigurationsmittelkurve mit der Superpositionsvorhersage überein
(147 Tests). Bestätigt (äquivalent) ist H1 nur, wenn jede der 147 Abweichungen gegen beide Vorhersagen ŷ⁰
und ŷ¹ (§8.2) nachweislich innerhalb der Äquivalenzgrenze ±Δ_q liegt, einem Viertel der vorhergesagten
Struktur (Äquivalenztest, PB1, §8.5). Falsifiziert (relevant abweichend) ist H1 nur, wenn an einem Test die
Abweichung gegen beide Vorhersagen nachweislich größer als die Relevanzgrenze Δ_rel ist (Mindesteffekttest,
§8.5). Sonst ist H1 nicht entscheidbar. Die drei Ausgänge schließen sich aus.

**H2 — Zeltspitze (primär).** Die Lage φ₂* des F_min-Maximums aus einem Zeltfit mit zwei Geraden in einem
festen Fitfenster (§8.6) stimmt mit der Lage überein, die derselbe Fit an der Vorhersage ergibt; bestätigt
nur bei einer Halbbreite des Intervalls von höchstens 1°.

**H3 — Kontaktmodell (sekundär).** Das 1-FG-Modell sagt mit den in P0.1–P0.5 unabhängig gemessenen
Größen Real- und Imaginärteil von N_k⁽ʲ⁾, k = 1 … 3, der Einzelmodul-Kontrollläufe der Phase 1 voraus
(18 Tests, §8.7); bestätigt nur, wenn jedes Intervall in ±10 % der vorhergesagten Amplitude liegt (PB3).
In einem steifen Aufbau prüft H3 vor allem Masse, Profil und Kalibrierung (§8.7).

**H4 — Vorzeichen der Schiefe (sekundär).** An jeder Konfiguration der Prüfmenge V hat die gemessene
Schiefe das Vorzeichen der Vorhersage γ̂₁ (einseitig, höchstens 23 Tests). V enthält die Schnittpunkte
und, falls nach §5.3 zulässig, (0°, 0°) und (0°, 180°), jeweils nur bei
|γ̂₁| ≥ (c₄ + 1,645)·u_c,erw(γ₁) (§8.5); V steht in Teil B.

**Optional:** H1′, H2′ wie H1, H2 auf dem gespiegelten Schnitt (§6), sekundär, eigene Familien.

**Explorativ** (ohne Entscheidungsregel; zusätzliche Messungen erst nach dem Datenschluss): **E1**
Liftoff-Bereich (höheres f, Konfigurationen außerhalb des Kontaktasts; λ, A, F_max); **E2** Anlauf und
Hysterese (etwa synchroner Anlauf mit anschließender Phasenverschiebung, Stoßanregung), Suche nach
Bistabilität; **E3** Einzelzellkräfte und Kippmomente aus den drei Zellkräften der Phase-1-Läufe; in ihnen
heben sich am Triphasik-Punkt die Harmonischen, deren Ordnung kein Vielfaches von 3 ist, im Allgemeinen
nicht auf; **E4** zyklusweise Minima unter Phasenjitter; **E5** qualitativer Vergleich mit den
Simulationsdaten. A und F_max werden für alle Schnittpunkte mit ihrer Vorhersage beschreibend berichtet.

---

## 4 · Observablen und Definitionen

Entscheidungsrelevant; die vollständige Tabelle steht im Anhang A1.

| Größe | Definition |
|---|---|
| N_c, N | Kraft der Wägezelle c = 1, 2, 3 nach Kalibrierung; N = N₁ + N₂ + N₃ |
| Laufarten | Referenzlauf R: Module geparkt, Antriebe haltend. Einzelmodullauf Lⱼ: nur Modul j läuft. Kombinationslauf: alle Module in einer Sollkonfiguration. D1: passiver Körper ohne Antriebe; D2: Antriebe laufen, bewegte Massen abgekoppelt |
| θ, φ̄ⱼ, σⱼ, ρⱼₖ | θ: Zyklusphase ab dem Indeximpuls von Modul 1 (in Lⱼ von Modul j). φⱼ,c: Indexphase von Modul j im Zyklus c; φ̄ⱼ, σⱼ: ihr zirkuläres Mittel und Jitter in einem Lauf; ρⱼₖ = ⟨e^{−ikφⱼ,c}⟩ über alle Zyklen aller gültigen Läufe einer Konfiguration |
| Profilphase | φⱼ^P = φⱼ + Δδⱼ (Indexphase gegen Modul 1 plus Profilversatz aus P0.5); alle Sollphasen sind Profilphasen |
| Schnitt | φ₂ = 100°, 102°, …, 140° bei φ₃ = 240°; F_min entlang des Schnitts heißt Zeltkurve, (120°, 240°) Triphasik-Punkt |
| Mittelkurve | phasensynchrones Mittel der vollständigen Zyklen im Auswertefenster eines Laufs, N_θ = 2000 Stützstellen, Harmonische k ≤ k_max |
| Konfigurationsmittelkurve | Mittel der Mittelkurven aller gültigen Läufe einer Konfiguration, gleich gewichtet |
| N_k | (2/N_θ)·Σₙ N̄(θₙ)·e^{−ikθₙ}, k ≥ 1 |
| ⟨N⟩, N_s | Zeitmittel über die ganzen Zyklen des Auswertefensters; N_s: ⟨N⟩ in Referenzläufen |
| F_min, F_max, γ₁ | Minimum, Maximum, Schiefe m₃/m₂^{3/2} der bandbegrenzten Konfigurationsmittelkurve; verglichen wird F_min − ⟨N⟩; zyklusweise Minima und Minima ungefilterter Kurven sind nicht konfirmatorisch (E4) |
| Δ⟨N⟩, σ̂_ref | Δ⟨N⟩ = ⟨N⟩_Lauf − N_s,int, mit N_s,int linear interpoliert zwischen den beiden einschließenden Referenzläufen. σ̂_ref: Standardabweichung derselben Statistik für mindestens 42 Referenzläufe der Phase 0, jeder gegen seine Nachbarn (leave-one-out); σ̂_ref,c je Zelle. ε_ctrl: §8.8 |
| Einzelzell-Liftoff | ein Rohwert N_c < F_LO,c = Nullpunkt + 5·σ_c (σ_c: Rauschen der Zelle c in Referenzläufen) im ganzen Lauf einschließlich Rampe und Einschwingzeit |
| Kontaktast | Die Vorhersage ŷ⁰ erfüllt mit den gemessenen Zeigern ρⱼₖ Bedingung (a) aus §5.3, und kein Lauf der Konfiguration bei f zeigt Einzelzell-Liftoff; ausgenommen sind Läufe, die nach G5, G8 oder G10 ungültig sind |
| Δ_park, G_F, G_x | Toleranz der Parkposition [Teil B]; Übertragung der Kraftkette (P0.4) und des Wegkanals (P0.5) |
| u_c, u_c,erw | u_c: Unsicherheit einer Differenz Messung − Vorhersage (§8.3); erwartet: u_c,erw² = s_q²/n_min + u²(ŷ_q), s_q gepoolt aus den Pilotläufen [Teil B] |
| Δ_q, Δ_rel | Äquivalenzgrenze Δ_q = 0,25·D_q und Relevanzgrenze Δ_rel ≥ Δ_q der Falsifikation (§8.5) [Teil B] |

---

## 5 · Aufbau und Phase 0

### 5.1 Aufbau

Teil A geht für V1 von drei Wägezellen im Dreieck, optischem Wegkanal, drei Phasenencodern mit Indeximpuls,
Beschleunigungssensor und Temperatur aus (Kanäle: A9.1), mit Nocke oder programmierbarem Aktuator für das
Profil; festgelegt ist dieser Kanalsatz damit nicht. Das Exposé nennt die drei Wägezellen im Dreieck;
Wegkanal, Phasenencoder, Beschleunigungssensor und Temperaturfühler stehen dort als erwogen, die Kanalzahl
als offen.
Zusätzlich verlangt Teil A: kinematische Lagerung der Füße und eine festgelegte, dokumentierte
Kabelschlaufe; feste Verstärkung ohne Softwarefilter, automatische Nullpunktnachführung,
Stillstandserkennung, adaptive Filter oder Bereichsumschaltung; gleiche analoge Anti-Aliasing-Filter in
allen Kraftkanälen; eine gemeinsame Zeitbasis mit Zeitstempeln der Indeximpulse (Quantisierung ≤ 0,01°);
eine Abtastrate mit (π·k_max·f/f_s)²/2 ≤ 10⁻³ (A6); einen Blindkanal und Temperaturfühler an jeder Zelle und
jedem Antrieb. Die Nennlast folgt aus der größten erwarteten Zellkraft einschließlich E1 mit
Sicherheitsfaktor, mit Überlastanschlag; Teil B weist mit den Datenblattwerten nach, dass PB1 und PB3 bei
der Arbeitslast erreichbar sind (Größenordnungen: A4). Einzelheiten: A9.1; Kanalliste und Einstellungen:
[Teil B].

### 5.2 Ablauf der Phase 0

Mechanisch verändernde Schritte liegen vor der **Endmontage**; danach wird der Aufbau bis zum
Datenschluss mechanisch nicht verändert: kein Abheben, kein Lösen von Massen, Kabeln oder Encodern. Nicht
als Veränderung zählen das Ausrichten des berührungslosen Wegkanals, das Ankoppeln und Lösen der Anregung
in P0.4 und Messmarken für P0.5, die bis zum Datenschluss bleiben. D1, D2 und der Zellnullpunkt werden nach
dem Datenschluss wiederholt. Verfahren im Einzelnen: A9.2.

| Nr. | Schritt | Ergebnis (→ Teil B) |
|---|---|---|
| P0.1 | statische Kalibrierung (Orientierung DKD-R 3-3), Nullpunkt, Laststellen, Querkraft, Elektronik | Kennlinien, Unsicherheiten; Laststelle, Querkraft je ≤ 0,1·Δ_q; Superpositionsfehler der Elektronik ≤ 0,3·u_c,erw |
| P0.2 | Wägung | M, m_j, μ |
| P0.3 | D1; D2 auf dem 1-Hz-Raster; Kabelschlaufe in zwei Lagen | Störsignaturen; statischer Nebenschluss ≤ 0,1·Δ_q; Umkehrspanne ≤ 0,3·u_c,erw |
| — | **Endmontage** | — |
| P0.4 | Übertragungsfunktion je Zelle und Summe, zwei Amplituden (Orientierung DKD-R 3-10 Blatt 1 und 2) | K, C, f_n, ζ; Moden f_m, ζ_m; G_F(ω); Linearität |
| P0.5 | Profilmessung bei f | x_k⁽ʲ⁾, a_k⁽ʲ⁾, Δδⱼ mit u ≤ 0,1°, G_x(ω), Parkposition |
| P0.6 | Phasensteuerung | Versatz, Jitter σⱼ, Wiederholbarkeit der Indeximpulse |
| P0.7 | ≥ 42 Referenzläufe, verschachtelt mit P0.8–P0.10, je einer nach zwölf anderen Läufen | σ̂_ref, σ̂_ref,c, σ_c, F_LO |
| P0.8 | Einzelmodulläufe, je Modul ≥ 20, auf n₀ ergänzt | N̄⁽ʲ⁾(θ) gesamt und je Zelle; ε_ctrl (§8.8) |
| P0.9 | Arbeitspunkt (§5.3) | f, k_max |
| P0.10 | Pilotläufe (§5.4) | s_q, σ_Δ, σ_tol, T_φ, Rauschkovarianzen, p̂, T_a, T_ramp, n₀, n_min, n |
| P0.11 | Vorhersagen (§8) | Vorhersagen mit Unsicherheiten |

K, C, M, m_j, x_k⁽ʲ⁾, G_F und G_x stammen nur aus P0.1–P0.5, nie aus Kraftdaten der Einzelmodulläufe. Die
Ergebnisse von P0.1–P0.4 werden mit SHA-256 und Zeitstempel hinterlegt, bevor Kraftdaten aus P0.8
ausgewertet werden, die P0.5-Ergebnisse einer Frequenz, bevor P0.8-Kraftdaten bei dieser Frequenz
ausgewertet werden; die Verfahren von P0.4 und P0.5 sind eingefrorener Code (§12, Werkzeug 4).
**D2-Kriterium:** Für die Harmonischen D2_k der D2-Signatur, k = 1 … 3, gilt |D2_k| ≤ 0,01·min_j |N̂_k⁽ʲ⁾|
(N̂_k⁽ʲ⁾: H3-Vorhersage, §8.7); sonst geht die D2-Signatur als Unsicherheit in H3 ein und wird in Teil B
berichtet. Für H1 ist ein D2-Signal eines einzelnen Antriebs unschädlich, weil es in den Einzelmodulläufen
mitgemessen wird. H1 betreffen kann nur eine Wechselwirkung der Antriebe; sie zeigt erst D2 in
Kombinationskonfiguration. Ob D2 auch so gemessen wird und mit welcher Schwelle, ist offen (§12).

**Schwellen und Nachweisgrenze.** Einflüsse, die eine H1-Signatur erzeugen können, weil sie nichtlinear sind
oder sich zwischen Einzelmodul- und Kombinationsläufen ändern, werden auf die Nachweisgrenze bezogen:
≤ 0,3·u_c,erw,q mit dem kleinsten u_c,erw,q über die Schnittpunkte (Superpositionsfehler der Elektronik in
P0.1, Umkehrspanne in P0.3, G7). Lineare, zeitinvariante Einflüsse (Laststelle, Querkraft,
statischer Nebenschluss) erzeugen keine H1-Signatur (A2.1); für sie bleibt ≤ 0,1·Δ_q, und sie gehen in H3 als
Unsicherheit ein. Der Nachweis steht in Teil B; eine verfehlte Schwelle wird dort berichtet und geht als
Szenario in die Kalibriersimulation ein (A9.11).

### 5.3 Wahl des Arbeitspunkts

- **(a) Kontaktast mit Abstand:** Für jeden Schnittpunkt, jede Pilotkonfiguration und jeden
  Einzelmodullauf liegt das vorhergesagte Minimum jeder Zellkraft bei mindestens 25 % der statischen
  Zelllast, vorhergesagt mit der Superposition je Zelle ohne Bandbegrenzung (vor den Messungen bei einer
  Frequenz mit dem Auslegungswerkzeug), und kein Einzelmodul- oder Pilotlauf bei f zeigt
  Einzelzell-Liftoff. Je Zelle, weil Kippmomente eine Zelle entlasten können, während N groß bleibt.
- **(b) Resonanzabstand:** 3f ≤ f₁/2, f₁ die niedrigste in N oder einer Zellkraft sichtbare Mode; nur
  Harmonische mit k·f ≤ f₁/2 werden ausgewertet. Dann ist |H| ≤ 1,33 und d ln|H| / d ln f ≤ 0,67 für jedes
  ζ ≤ 2 (A6).
- **(c) Präzision und Zeit:** Nach §5.4 gibt es k_max ≥ 3 und n = n_min + r ≤ n_max, n_max das größte n mit
  ((N_K + 5)·n + 15·d)·T_Lauf/(1 − p̂) ≤ T_verfügbar; d Messtage und T_verfügbar [Teil B], N_K = 21 oder 23,
  T_Lauf = T_park + T_ramp + T_e + T_a + T_ab (Startstellung anfahren, Rampe, Einschwingen, Fenster,
  Abfahren und Parken; Zählung: A9.12).
- **(d) Grenzen der Apparatur:** Antrieb, Nennlast, Abtastrate.

**Regel.** f_u ist die kleinste ganzzahlige Frequenz, die (d) erfüllt, f_zul die größte, die (a) nach dem
Auslegungswerkzeug, (b) und (d) erfüllt [beide Teil B]. Zuerst wird bei f_zul gemessen (P0.5–P0.8,
P0.10). Kandidaten sind die ganzzahligen Frequenzen f_u … f_zul, die (d) und (c) mit der auf sie
skalierten Struktur und den Streuungen bei f_zul erfüllen; sie werden aufsteigend gemessen (f_zul nicht
erneut). f ist der erste Kandidat, der (a)–(d) mit eigenen Daten erfüllt (A9.2). Gibt es keinen, endet
Phase 0 mit dem veröffentlichten Befund „kein zulässiger Arbeitspunkt“. (0°, 0°) und (0°, 180°) werden nur
gemessen, wenn sie bei f (a) erfüllen; sonst ist H4 auf den Schnitt beschränkt.

### 5.4 Pilotläufe, Bandbreite und Laufzahl

**Pilotläufe:** (110°, 250°), (130°, 230°) und (110°, 252°), je mindestens 20 gültige Läufe, aufgenommen
mit dem Fenster T_a,P [Teil B]. Ihre zyklischen Phasenabstände (110°/140°/110°, 130°/100°/130°,
110°/142°/108°) enthalten keinen Abstand von 120°; damit ist keine, auch nach Modulvertauschung und
Zeitverschiebung, zu einem Punkt eines Schnitts äquivalent (A7). T_ramp [Teil B] wird vor den Pilotläufen
gewählt; zeigt ein Pilotlauf in der Rampe Einzelzell-Liftoff, wird T_ramp verdoppelt, und die Pilotläufe
werden wiederholt. Ein registriertes Skript gibt nur Streuungen, T_φ, Rauschkovarianzen und den Anteil p̂
ungültiger Läufe aus; Superpositionsresiduen der Piloten werden vor Teil B nicht berechnet. Die Pilotdaten
werden bei der Aufnahme gehasht, nach der Auswertung veröffentlicht (§10.2) und nicht konfirmatorisch
verwendet. s_q ist je Größe das quadratische Mittel der Streuungen über die Pilotkonfigurationen
(gepoolt), auch für s(γ₁) der Zusatzkonfigurationen.

**k_max, T_a und Laufzahl** (Reihenfolge fest, A9.2): Für k = k_b, k_b − 1, …, 3 (k_b = ⌊f₁/(2f)⌋) und je k
für T_a aus ganzen Zyklen aufsteigend, soweit die Aufnahme reicht, wird s_q(T_a) aus den auf die ersten
Zyklen gekürzten Pilotläufen gebildet. n_min und n₀ ≥ 20 minimieren N_K·n_min + 3·n₀ (bei Gleichstand das
kleinere n_min) unter der Bedingung, dass die Planungssimulation (§12, Punkt 8) H1 bei exakter Superposition
nach den Regeln von §8.5 und §9.3 mit Wahrscheinlichkeit ≥ 0,8 bestätigt und die erwartete H2-Halbbreite
≤ 1° ist, mit Streuungen an ihrer oberen 80-%-Vertrauensgrenze. Zusätzlich gilt n_min ≥ (3/SNR)² mit
SNR = s̄·1°/s_F, s̄ dem Mittel der beiden Flankensteigungen des Zeltfits an der Vorhersage im Fitfenster und
s_F der Pilotstreuung von F_min − ⟨N⟩ (Faustregel für die H2-Halbbreite, A9.2); SNR steht in Teil B. Das
erste Paar (k, T_a), das damit n ≤ n_max erfüllt, legt k_max = k, T_a, n_min und n₀ fest; alle k ≤ k_max
werden verwendet. Gibt es keines, ist f unzulässig. **Rauschbias:** Für jeden Schnittpunkt wird
b_i = E[min N̄_Messung] − E[min N̂] aus den Rauschkovarianzen simuliert, mit getrennten Rauschmodellen für
Einzelmodul- und Kombinationsläufe. Der Bias hängt vom Verhältnis der Rauschpegel von Mess- und
Vorhersageseite ab; er wird deshalb für beide Vorhersagen getrennt bestimmt: b_i⁰ mit n_min Läufen und n₀
Einzelmodulläufen je Modul, b_i¹ mit n_min Läufen und den geplanten n + d Kontrollläufen je Modul der Phase 1
(A9.12). Die Schätzwerte b̂_i⁰ und b̂_i¹ stehen in Teil B. Sie werden vom Residuum r_i⁰(F_min) bzw. r_i¹(F_min)
abgezogen, und ihre Unsicherheiten u(b̂_i⁰) bzw. u(b̂_i¹) gehen in u_c ein (§8.3, A9.5). Die Simulation von c
verwendet dieselbe Korrektur (§8.4). Über die Zulässigkeit von f entscheidet der Rauschbias nicht. Geplant
werden n = n_min + r Läufe je Konfiguration (n Blöcke), r = ⌈n_min·p̂/(1 − p̂)⌉ + 2.

---

## 6 · Phase 1 — Messprotokoll

**Konfigurationen:** die 21 Schnittpunkte; falls zulässig (0°, 0°) und (0°, 180°); Kontrollläufe R, L₁,
L₂, L₃.

**Blöcke:** Ein Block enthält jede Konfiguration genau einmal in zufälliger Reihenfolge, beginnt mit einem
Kontrollsatz (R, L₁, L₂, L₃ in zufälliger Reihenfolge), hat nach der zwölften Konfiguration einen
Referenzlauf und endet mit einem Kontrollsatz; zwei unmittelbar aufeinanderfolgende Blöcke teilen sich
diesen, wenn sie am selben Messtag liegen. Jeder Messtag endet mit einem Schlussreferenzlauf. Die
Reihenfolge erzeugt das Randomisierungsskript (§12, Werkzeug 7) mit `numpy.random.default_rng(seed)`,
seed = int(sha256(Dateibytes des registrierten Hauptdokuments).hexdigest()[:16], 16), aus der Liste:
Schnittpunkte aufsteigend nach φ₂, dann (0°, 0°) und (0°, 180°), falls zulässig; Kontrollsatz R, L₁, L₂, L₃.

**Wiederholungen:** Ein Konfigurationslauf, der vor Beginn des Schlusskontrollsatzes als ungültig erkannt
wird, wird wiederholt, höchstens zweimal je Konfiguration und Block, an einem Platz, den derselbe Generator
gleichverteilt unter den offenen Konfigurationsplätzen und dem Platz vor dem Schlusskontrollsatz zieht.
G1-Verstöße behandelt S1 (§9.2). Ein ungültiger Kontrolllauf wird sofort wiederholt, höchstens zweimal;
danach wird angehalten (§9.2). Später erkannte ungültige Läufe werden nicht wiederholt. Einzelheiten: A9.12.

**Messtag und Lauf:** Die Messelektronik ist mindestens T_warm eingeschaltet. Es folgen Aufwärm-
Referenzläufe, bis zwei aufeinanderfolgende um weniger als σ̂_ref differieren, höchstens zehn (sonst
Ursachenanalyse nach §9.2); der letzte gilt als gültiger Referenzlauf für N_s,int und den Nullpunktalarm.
Kein Block über Nacht. Jeder Lauf mit bewegten Modulen: Startstellung der Sollphasen → Rampe auf f in
T_ramp mit aktiver Phasenregelung (nie durch die synchrone Phasung) → Einschwingzeit
T_e = max(T_φ, 10·max_m τ_m), aufgerundet auf ganze Sekunden, mit τ_m = 1/(2π·ζ_m·f_m) für alle Moden bis
k_max·f und T_φ der längsten Einregelzeit der Phasen in den Pilotläufen → Auswertefenster T_a aus ganzen
Zyklen → Rampe auf 0 → Parkposition. Referenzläufe dauern gleich lang.

**Blindung:** Die Software berechnet nur, was §9.1 und §9.2 brauchen (intern auch F_min − ⟨N⟩ je Fünftel
für G4 und die S3-Größen), und zeigt nur „gültig“ oder „ungültig“ mit Kriterium, die Alarme S1–S4 und eine
Übersteuerungsanzeige, keine Zahlen und keine Wellenformen von Kombinationsläufen; Zwischenwerte sind erst
nach dem Datenschluss zugänglich. Die Konfiguration ist dem Bediener bekannt (berichtete Einschränkung).

**Datenschluss:** alle Blöcke gemessen, Manifest hinterlegt; bei vorzeitigem Ende (Zeit, Hardwareausfall)
nach dem letzten vollständigen Block, mit Eintrag im Abweichungsprotokoll. Dann läuft die konfirmatorische
Auswertung einmal. Als **Codefehler** gilt nur ein Fehler, der an den synthetischen Daten des
Pipelinetests nachweisbar ist; dann zählt das korrigierte Ergebnis, mit Eintrag im Abweichungsprotokoll,
und das des registrierten Codes wird daneben berichtet. Sonst bleibt der registrierte Code maßgeblich.

**Gespiegelter Schnitt (optional):** φ₂ = 240°, φ₃ = 100° … 140° ist bei identischen Modulen gleichwertig
(A7); falls in Teil B vorgesehen, nach den Blöcken des Hauptschnitts gemessen und als H1′/H2′ ausgewertet.

---

## 7 · Artefakte und Kontrollen

Die Regel aus v1 §6 gilt weiter: Was nicht durch Referenz, Dummy und Wiederholung überlebt, wird
verworfen. Alle Quellen mit ihrer Kontrolle: Anhang, Tabelle C.

---

## 8 · Auswertung

### 8.1 Verarbeitung

Alle Laufarten werden identisch verarbeitet (A9.4): Kalibrierung je Zelle, keine Softwarefilter,
Segmentierung am Indeximpuls, Mittelkurve, DFT mit Harmonischen bis k_max. Minimum und Schiefe werden auf
gemessene und vorhergesagte Kurven gleich angewandt, jeweils nach der Summation.

### 8.2 Superpositionsvorhersage

    N̂(θ) = N_s + Σⱼ Σₖ Re[ N̄_k⁽ʲ⁾ · ρⱼₖ · e^{ikθ} ]  (k ≤ k_max),     N̂_k = Σⱼ N̄_k⁽ʲ⁾ · ρⱼₖ

N̄_k⁽ʲ⁾: Harmonische der gemittelten Einzelmodul-Mittelkurve, bezogen auf den eigenen Indeximpuls; ρⱼₖ
aus den gültigen Läufen der Konfiguration. Zellkräfte ebenso, für (a) ohne Bandbegrenzung. **ŷ⁰** aus den
Einzelmodulläufen der Phase 0 ist die registrierte Vorhersage; **ŷ¹** entsteht ebenso aus den gültigen
Kontrollläufen der Phase 1 und folgt einer Drift. Eine Abweichung zählt nur, wenn sie gegen beide besteht.
Die Differenz Phase 1 − Phase 0 der 21 Einzelmodulgrößen wird mit Welch-t-Test, zweiseitig, Bonferroni
über 21, α = 0,05, berichtet. Zeigt ein Kontrolllauf der Phase 1 Einzelzell-Liftoff (ausgenommen Läufe, die
nach G5, G8 oder G10 ungültig sind), ist ŷ¹ ungültig, und H1 und H2 sind nicht entscheidbar. Für ŷ⁰ schließt
§5.3 (a) Liftoff aus.

### 8.3 Unsicherheiten

r_iq = ȳ_iq − ŷ_iq; u_c² = Var_A + Var_B aus zwei Bootstraps mit je 10 000 Replikaten über die Läufe der
Konfiguration (A) und die Einzelmodulläufe (B) (A9.5). **ν_eff:** für jeden Vergleich Welch–Satterthwaite,
ν_eff = u_c⁴ / (Var_A²/(n_A − 1) + Var_B²/(n_B − 1)), mit den Zahlen gültiger Läufe der Messseite (n_A)
und des kleinsten Moduls der Vorhersageseite (n_B); Monte-Carlo-Vorhersagen zählen mit ν = ∞. Das gilt
für z⁰, z¹ und H3; bei H4 gibt es nur die Messseite (ν = n_i − 1). In H1, H2 und H4 fällt ein konstanter
Skalenfehler heraus; in H3 geht die Kalibrierunsicherheit voll ein. Für F_min − ⟨N⟩ ist r_i⁰ um den
Rauschbias b̂_i⁰ und r_i¹ um b̂_i¹ korrigiert; u_c² enthält zusätzlich u²(b̂_i⁰) bzw. u²(b̂_i¹) (§5.4, A9.5).

### 8.4 Kritische Werte

z_iq = r_iq / u_c,iq. **H3, H4:** c = t(1 − α/(s·m); ν_eff) mit s = 2 (zweiseitig) bzw. 1; m fest: H3 18
(zweiseitig), H4 23 (einseitig); Werte in A8. m gilt auch, wenn weniger Tests auswertbar sind.
**H1:** c ist das 95-%-Quantil der gemeinsamen Nullverteilung von max_{i,q} |z⁰_iq| über die 147 korrelierten
Tests, bestimmt in der Kalibriersimulation bei exakter Superposition mit den Rauschkovarianzen, Laufzahlen und
dem Code von Teil B einschließlich der Biaskorrektur (§5.4, A9.11) [Teil B]. Es gilt in beide Richtungen, also
auch dann, wenn es unter dem Bonferroni-Wert c_B = t(1 − α/294; ν_eff) liegt, und ebenso für z¹ und im
Mindesteffekttest (§8.5). Bis zu Teil B rechnet die Planung mit c_B (A8). Eine zweite, unabhängige Simulation
mit 1000 Kampagnen prüft den Anteil der Kampagnen mit mindestens einem |z⁰| > c bei exakter Superposition.
Liegt er über 0,069, gilt das 95-%-Quantil aus beiden Simulationen zusammen. Die Schwelle ist 0,05 plus zwei
Standardfehler; diese fassen den Monte-Carlo-Fehler der Prüfung und den Schätzfehler von c zusammen (A8). Eine
Überschreitung löst nur dieses Poolen aus; sie ist kein verfehltes Kriterium (A9.11). Die
Wahrscheinlichkeit, mindestens eine der beiden Primärhypothesen fälschlich zu verwerfen, ist höchstens 0,10,
für H1–H4 höchstens 0,20 (Bonferroni-Schranke über die Familien).

### 8.5 Äquivalenz, Mindesteffekt und Präzision

- **PB1 (H1, Äquivalenztest):** Für alle 147 Tests und beide Vorhersagen liegt [r − t_eq·u_c, r + t_eq·u_c]
  in [−Δ_q, +Δ_q], mit t_eq = t(0,95; ν_eff): je Test zwei einseitige Tests auf α = 0,05 (TOST), verknüpft
  nach dem Intersection-Union-Prinzip, ohne Mehrfachkorrektur und ohne die Bedingung „kein |z| > c“ (A8).
  Δ_q = 0,25·D_q aus ŷ⁰ [Teil B], mit D = max_i F̂_min,i − min_i F̂_min,i für F_min − ⟨N⟩. Für Re und Im N_k
  ist D offen (§12): Fassung A (bisher) D = max_i |N̂_k,i|; Fassung B D = max_{i,i′} |N̂_k,i − N̂_k,i′|, der
  Durchmesser der vorhergesagten Zeigermenge über den Schnitt, analog zur Spannweite bei F_min (A8).
- **Präzision:** Notwendig für PB1 ist u_c < Δ_q/t_eq je Test. Als Auslegungsgrenze für eine
  Bestätigungswahrscheinlichkeit von 0,8 bei exakter Superposition gilt je Größe q u_c,q ≤ Δ_q/5,01 (ν → ∞)
  bzw. Δ_q/5,21 (ν = 19). Sie gilt für 294 als unabhängig angenommene Intervalle: 147 Tests gegen ŷ⁰
  und ŷ¹. Gegen eine Vorhersage allein wären es Δ_q/4,82 bzw. Δ_q/5,00; die zweite Vorhersage senkt die
  Bestätigungswahrscheinlichkeit (A8). Gerechnet wird mit derselben Bandbegrenzung wie die Messung (A4, A8).
  Welche Größe bindet, hängt vom Rauschmodell ab (A8); maßgeblich ist die Planungssimulation (§5.4).
- **Mindesteffekt (H1):** Ein Test ist relevant abweichend, wenn |r⁰| − c·u_c⁰ > Δ_rel,q und
  |r¹| − c·u_c¹ > Δ_rel,q mit gleichem Vorzeichen von r⁰ und r¹ (c nach §8.4). Δ_rel,q [Teil B] folgt einer in
  Teil A festgelegten Regel; Vorschlag: Δ_rel,q = Δ_q (Optionen: A8, offen, §12). Jede zulässige Regel
  erfüllt Δ_rel,q ≥ Δ_q; dann schließen sich „äquivalent“ und „relevant abweichend“ aus (A8).
- **PB3 (H3):** Intervall in ±0,10·|N̂_k⁽ʲ⁾|.
- **H4:** Aufnahme in V bei |γ̂₁| ≥ (c₄ + 1,645)·u_c,erw(γ₁), c₄ = t(1 − 0,05/23; n_min − 1).

### 8.6 Zeltfit (H2)

Stetiges Zelt F(φ) = F* − s_L·(φ* − φ) für φ ≤ φ*, F* − s_R·(φ − φ*) sonst, ungewichtet an F_min − ⟨N⟩
über der gemessenen Profilphase φ̄₂^P = −arg ρ₂₁ + Δδ₂ im Fitfenster W; derselbe Fit an der Vorhersage
ergibt φ̂₂*. W ist um den Schnittpunkt zentriert, der der in Teil B vorhergesagten Spitze am nächsten liegt
(bei Gleichstand der kleinere), und am Schnittrand abgeschnitten. Die Halbbreite w hängt nicht von u_c,erw
ab; Vorschlag: w = 6° fest (Alternativen: w = 8° fest oder ein Kriterium über den Spitzenfehler, A9.6;
offen, §12). Liegen auf einer Seite weniger als zwei Punkte, ist H2 nicht entscheidbar. Das 95-%-Intervall
der Differenz entsteht aus 10 000 Bootstrap-Replikaten über alle Läufe, getrennt gegen ŷ⁰ und ŷ¹, als
Perzentilintervall. Über den Intervalltyp entscheidet die Überdeckung in der Kalibriersimulation mit der
Schwelle 0,936 (0,95 minus zwei Monte-Carlo-Standardfehler bei 1000 Kampagnen) [Teil B]: Erreicht das
Perzentilintervall sie, gilt es. Sonst gilt das BCa-Intervall, wenn es sie erreicht. Erreicht keines sie, gilt
das Perzentilintervall mit dem kleinsten Nominalniveau aus 0,96, 0,97, 0,98 und 0,99, dessen simulierte
Überdeckung 0,936 erreicht (kalibrierte Verbreiterung). Reicht auch 0,99 nicht, ist H2 nicht entscheidbar.
Suchschritt, Gleichstand, Replikate: A9.6.

### 8.7 H3

N̂_k⁽ʲ⁾ = G_F(kω)·m_j·H(kω)·a_k⁽ʲ⁾ mit H(ω) = (K + iωC)/(K − M·ω² + iωC), als Mittel einer Monte-Carlo-
Fortpflanzung mit Unsicherheit (A9.7); Messwerte sind die Mittel der gültigen Phase-1-Kontrollläufe. Eine
Harmonische prüft den Kontakt nur, wenn |N̂_k⁽ʲ⁾ − G_F·m_j·a_k⁽ʲ⁾| > Δ (PB3); sonst prüft H3 Masse, Profil und
Kalibrierung. Teil B nennt den Fall je k. Vor dem Datenschluss wird die H3-Vorhersage nicht mit gemessenen
Einzelmodul-Harmonischen verglichen; der Vergleich mit Phase 0 wird danach berichtet.

**Reichweite im steifen Aufbau (offen – Entscheidung des Autors, §12).** Bei K = 10⁶ N/m weichen |N₁|, |N₂|,
|N₃| nur um 0,3 %, 1,0 % und 2,4 % vom starren Wert ab (A4), weit unter PB3. H3 prüft dann für k ≤ 3 nicht den
Kontakt. Zwei Fassungen stehen zur Wahl:

- **Fassung K (Kennzeichnung):** H3 bleibt wie oben und wird ausdrücklich als Prüfung von Masse, Profil und
  Kalibrierung berichtet; eine Bestätigung sagt dann nichts über das Kontaktmodell. Kein zusätzlicher Kanal.
- **Fassung I (Betriebsimpedanz):** H3 wird um eine Prüfung ergänzt, die die Abweichung von der
  starren Auflage direkt misst. In den Einzelmodul-Kontrollläufen der Phase 1 werden je Harmonischer die
  Einfederung x_k (Wegkanal, A9.1, Bezugspunkt unterhalb der Zellen) oder, über x_k = −a_R,k/(kω)², die
  Rahmenbeschleunigung aufgenommen; aus N_k/x_k = −(K + i·kω·C) folgen K und C unter Betriebslast, verglichen
  mit P0.4 (Module geparkt). Voraussetzung ist ein Wegkanal, der |x_k| auf etwa 1 % auflöst (im Beispiel A4
  Nanometer). Die Fassung hängt am offenen Entscheid über Messkette und Wegkanal; ihre Entscheidungsregel wird
  vor dem Einfrieren ergänzt, wenn sie gewählt wird.

### 8.8 Nullkontrolle

**ε_ctrl** = 3·σ̂_ref, bestimmt in Phase 0 nach G2–G10 und vor G1. Streuen die danach gültigen Pilot- und
Einzelmodulläufe stärker als die Referenzläufe (Test in A9.8: auf mittige Lage normierte Δ⟨N⟩, kritischer
Wert aus einer Simulation ohne Zusatzstreuung, α = 0,05), gilt ε_ctrl = 3·σ̂_betr (A1).

**Nullpunktalarm**, wenn ein Referenzlauf um mehr als 3·√(4/3)·σ̂_ref (Summe) bzw. 3·√(4/3)·σ̂_ref,c
(Zelle) vom vorangehenden gültigen Referenzlauf abweicht. Er wird sofort wiederholt;
überschreitet die Wiederholung im selben Kanal wieder die Schwelle, greift S1, sonst ist der alarmierte
Lauf ungültig und die Wiederholung ersetzt ihn. Berichtet wird ein Welch-t-Test von Δ⟨N⟩ der
Kombinationsläufe gegen die Referenzläufe (A9.8), ohne Einfluss auf H1–H4.

### 8.9 Sensitivitätsanalysen

Sie werden berichtet und entscheiden nichts (Liste: A9.9).

---

## 9 · Entscheidungs-, Ausschluss- und Abbruchregeln

### 9.1 Gültigkeit eines Laufs

Ein Lauf ist ungültig bei:

- **G1** |Δ⟨N⟩| > ε_ctrl.
- **G2** |φ̄ⱼ^P − φⱼ,soll^P| > δφ_tol = 0,5° (j = 2, 3), σⱼ > σ_tol (dreifacher Median von σⱼ aller
  Pilotläufe) oder fehlendem bzw. überzähligem Indeximpuls.
- **G3** |f̄ − f| > δf_tol = min_q min_i 0,1·u_c,erw,q,i/|∂ŷ_q,i/∂f| über die konfirmatorischen Größen q und
  Punkte i (∂ŷ/∂f aus dem Auslegungswerkzeug einschließlich H(kω)).
- **G4** |X(erstes Fünftel) − X(letztes Fünftel)| > 3·σ_Δ,X für X = ⟨N⟩ oder F_min − ⟨N⟩, jeweils aus der
  bandbegrenzten Mittelkurve der ersten bzw. letzten ⌊N_z/5⌋ der N_z Zyklen; σ_Δ,X = 1,4826·MAD dieser
  Differenz über alle Phase-0-Läufe derselben Laufart (Pilotläufe gepoolt, P0.8 je Modul, P0.7).
- **G5** einem Rohwert eines Kraftkanals am ADC-Endwert oder einem Übersteuerungssignal.
- **G6** Einzelzell-Liftoff.
- **G7** einer Zelltemperatur außerhalb T_P0 ± ΔT (T_P0: Mittel während P0.8 bei f;
  ΔT = min(10⁻³; 0,3·min_{q,i} u_c,erw,q,i/|ŷ_q,i|)/TK_C, also eine Empfindlichkeitsänderung von höchstens
  0,1 % und höchstens 0,3·u_c,erw in jeder Größe; TK_C Temperaturkoeffizient der Empfindlichkeit laut
  Datenblatt); Antriebstemperaturen werden protokolliert.
- **G8** äußerer Störung, protokolliert vor jeder Auswertung.
- **G9** Bewegung eines geparkten Moduls oder Abweichung von der Parkposition über Δ_park.
- **G10** defekter oder unvollständiger Aufzeichnung.

Referenzläufe: Nullpunktalarm statt G1, ohne G2 und G3, G4 nur mit ⟨N⟩. Einzelmodulläufe: G2 nur für
Indeximpulse. Nie ausgeschlossen wird wegen des Werts von F_min, N_k, γ₁, A oder λ; G4 prüft nur die
Änderung innerhalb eines Laufs. Ungültige Läufe bleiben mit Grund im Datensatz und werden gezählt
berichtet. **Auswertbar** ist eine Konfiguration im Kontaktast (§4) mit mindestens n_min gültigen Läufen;
eine nicht auswertbare Konfiguration geht in keinen Test ein, auch nicht in W oder V.

### 9.2 Abbruch im Messbetrieb

Die Messung wird sofort angehalten bei:

- **S1 — reproduzierbarer H0-Verstoß.** Weicht ⟨N⟩ eines Kombinations- oder Einzelmodullaufs X um mehr
  als ε_ctrl vom vorangehenden gültigen Referenzlauf R₀ ab, folgt sofort ein Referenzlauf R₁, und G1(X)
  wird mit R₀ und R₁ geprüft. Jeder G1-Verstoß, der vor Beginn des Schlusskontrollsatzes feststeht, auch
  erst mit einem planmäßigen Referenzlauf, führt zu R₂, der Wiederholung X′ und R₃, auch über die
  Wiederholungsgrenze hinaus; S1 greift, wenn X′ G1 verletzt (mit R₂ und R₃). Ein gültiges X′ ersetzt X
  und zählt als Wiederholung; ist X′ aus anderem Grund ungültig, gilt §6. S1 greift auch bei einem
  bestätigten Nullpunktalarm.
- **S2 — Einzelzell-Liftoff** in einem Lauf mit bewegten Modulen (ausgenommen Läufe, die nach G5, G8 oder
  G10 ungültig sind).
- **S3 — Drift der Einzelmodulreferenz:** In einem Kontrolllauf weicht eine der 21 Größen F_min⁽ʲ⁾ −
  ⟨N⁽ʲ⁾⟩, Re N_k⁽ʲ⁾, Im N_k⁽ʲ⁾ (k, j = 1 … 3) um mehr als c_S·s·√(1 + 1/n₀ⱼ) vom Phase-0-Mittel ab (s:
  Streuung der Phase-0-Läufe, c_S = t(1 − 0,05/42; n₀ⱼ − 1)), und dieselbe Größe überschreitet die
  Schwelle in der sofortigen Wiederholung erneut. S3 erkennt nur grobe Drift; kleine fängt ŷ¹ ab.
- **S4 — Phasenregelung außerhalb der Toleranz:** G2 in zwei aufeinanderfolgenden Läufen.

Bei korrekter Funktion löst S3 je Kontrollsatz mit höchstens 5 % aus und bestätigt sich mit höchstens
9,5·10⁻⁴; S1 greift in einer Kampagne mit 20 Blöcken zu 23 Konfigurationen an einem Messtag (565 Läufe
ohne Aufwärm- und Wiederholungsläufe) mit höchstens etwa 25 % (Bonferroni-Schranken, A8); die Schranke
wächst mit der Zahl der Läufe. Ein Fehlalarm kostet eine Ursachenanalyse, keine Daten.

**Nach einem Abbruch:** Ursachenanalyse, Eintrag im Abweichungsprotokoll, Wiederaufnahme nach einem
vollständigen Kontrollsatz ohne Alarm; der unterbrochene Block wird in der gezogenen Reihenfolge
fortgesetzt, gültige Läufe bleiben gültig. Nach einem mechanischen Eingriff werden vorher je Modul
mindestens n₀ Einzelmodulläufe mit Phase 0 verglichen (Welch-t, zweiseitig, Bonferroni über 21,
α = 0,05); ist eine Differenz signifikant, endet Phase 1, und ein neuer Teil B ist nötig. Nach S2 ist die
betroffene Konfiguration nicht auswertbar (bei einem Lⱼ ist ŷ¹ ungültig, §8.2), wird aber weiter gemessen.
Ein zweites S2 ohne festgestellten Apparaturfehler in derselben Phase 1, gleich bei welcher Konfiguration,
beendet Phase 1 als abgebrochene Kampagne.

### 9.3 Entscheidung je Hypothese

| Hypothese | falsifiziert, wenn | bestätigt, wenn | sonst |
|---|---|---|---|
| H1 | relevant abweichend: an einem Test \|r⁰\| − c·u_c⁰ > Δ_rel und \|r¹\| − c·u_c¹ > Δ_rel, gleiches Vorzeichen | äquivalent: alle 21 Punkte auswertbar, PB1 gegen ŷ⁰ und ŷ¹ (§8.5) | nicht entscheidbar |
| H2 | 0 ∉ [a⁰, b⁰] und 0 ∉ [a¹, b¹], auf derselben Seite | 0 ∈ [a⁰, b⁰] und 0 ∈ [a¹, b¹], (b⁰ − a⁰)/2 ≤ 1° | nicht entscheidbar; Zusatz „Drift der Einzelmodulbasis“ wie bei H1 |
| H3 | ein \|z\| > c | kein \|z\| > c, PB3, je Modul ≥ n_min gültige Kontrollläufe | nicht entscheidbar |
| H4 | an einem i ∈ V: sgn(γ̂₁,i)·γ̄₁,i < −c·u(γ̄₁,i) | V nicht leer, an jedem i ∈ V: sgn(γ̂₁,i)·γ̄₁,i > c·u(γ̄₁,i) | nicht entscheidbar |

z⁰, z¹: standardisierte Residuen gegen ŷ⁰, ŷ¹ (§8.4); [a⁰, b⁰], [a¹, b¹]: Intervalle von §8.6. **Zusätze
bei H1** (beschreibend, sie ändern den Ausgang nicht): „Abweichung nachgewiesen, kleiner als Δ_rel“, wenn an
einem Test |z⁰| > c und |z¹| > c mit gleichem Vorzeichen auftreten, ohne dass er relevant abweicht; „Drift der
Einzelmodulbasis“, wenn ein |z⁰| > c ohne gleichsinniges |z¹| > c auftritt oder umgekehrt. H2 ist
nur entscheidbar, wenn alle Punkte von W auswertbar sind. γ̄₁,i: gemessene Schiefe der
Konfigurationsmittelkurve, u(γ̄₁,i) ihre Bootstrap-Unsicherheit (Anteil A, §8.3); bei H4 ist
c = t(1 − 0,05/23; n_i − 1), V enthält nur auswertbare Konfigurationen. H1′, H2′ wie H1, H2 mit eigenen
Familien. H0 wird nicht im Sinn eines Effekts entschieden.

### 9.4 Ergebnislogik

| Ausgang | Deutung | nächster Schritt |
|---|---|---|
| S1 | Apparaturfehler oder Transiente | Fehlersuche |
| H1 falsifiziert (relevant abweichend) | Abweichung über Δ_rel: Kontakt nichtlinear, Module gekoppelt, Messkette oder Phasenmessung fehlerhaft; im steifen Aufbau überwiegend Apparatur (§2) | veröffentlichen; Ursachenanalyse; Einordnung mit T2 des Literaturabgleichs, T0/T1 bei Zellminima nahe F_LO |
| Zusatz „Abweichung nachgewiesen, kleiner als Δ_rel“ | kleine, nachweisbare Verletzung der Superposition; Apparatur und Physik nicht getrennt | berichten; Ursachenanalyse; der Ausgang von H1 bleibt |
| H2 falsifiziert | Kopplung, Phasenfehler oder nicht erfasste Modulunterschiede | veröffentlichen; Ursachenanalyse |
| H1, H2 bestätigt, H3 falsifiziert | Superposition trägt, 1-FG-Modell nicht; im steifen Aufbau in Fassung K: Masse, Profil oder Kalibrierung (§8.7) | Modellrevision bzw. Prüfung von Masse, Profil und Kalibrierung; K-Tabelle des Werkstattberichts nicht übertragen |
| H3 falsifiziert, H1 nicht bestätigt | Befunde nicht trennbar | berichten |
| H1 bestätigt, H4 falsifiziert | Harmonische über k = 3 weichen ab | explorativ untersuchen |
| H1, H2, H3 bestätigt | Kontaktast in diesem Aufbau verstanden; im steifen Aufbau in Fassung K ohne Aussage über das Kontaktmodell (§8.7) | E1, E2; externe Replikation |
| nicht entscheidbar | Präzision reicht nicht, Basis gedriftet oder Abweichung zwischen Äquivalenz- und Relevanzgrenze | veröffentlichen; neuer Teil B und neue Phase 1 |
| Abbruch nach S2 | Kontaktannahme verletzt | veröffentlichen; neuer Teil B |
| H1′/H2′ widersprechen H1/H2 | nicht erfasster Modulunterschied oder Drift | Primärentscheidung bleibt; berichten |

Jedes Null-Ergebnis wird veröffentlicht. Kein Ausgang wird als Verschiebung von ⟨N⟩ gedeutet.

---

## 10 · Externe Validierung, Datenmanagement, Abweichungsprotokoll

### 10.1 Externe Validierung

v1 §8 bleibt Pflicht: gleiche Messung, andere Personen, andere Umgebung, möglichst andere Hardware. Das
Replikationspaket enthält Teil A und B, Protokolle, Code mit Commit-Hash, Anleitungen, Teileliste,
Zeichnungen und synthetische Beispieldaten; die replizierende Gruppe misst eine eigene Phase 0 und
registriert einen eigenen Teil B. Erfolgreich ist eine Replikation mit demselben Ausgang für H1 und H2,
der nicht „nicht entscheidbar“ ist; erst danach wird erweitert („Scale“, v1 §9).

### 10.2 Datenmanagement

Rohdaten je Lauf in einer schreibgeschützten Datei mit SHA-256, zwei räumlich getrennte Kopien, Metadaten
je Lauf (A9.10). Veröffentlicht werden nach der Auswertung, unabhängig vom Ausgang, Roh-, verarbeitete,
Phase-0- und Pilotdaten (CC BY 4.0), der Code (MIT) und das Abweichungsprotokoll.

### 10.3 Abweichungsprotokoll

Jede Abweichung von Teil A oder B wird mit Datum, Beschreibung, Grund, betroffenen Läufen und Auswertungen
und der Angabe protokolliert, ob Ergebnisdaten bekannt waren. Abweichungen nach dem Datenschluss machen die
betroffenen Auswertungen explorativ (Ausnahme: Codefehler); die registrierte Fassung wird daneben
berichtet. Das Protokoll wird vollständig mit den Ergebnissen veröffentlicht.

---

## 11 · Abgrenzung

Kein reaktionsloser Antrieb, keine Gewichtsreduktion, keine Gravitationsmodifikation, keine Verschiebung
des Zeitmittels, keine neue Physik; ⟨N⟩ = M·g ist Erhaltungssatz, jede Abweichung ein Apparaturfehler. Kein
Bezug zu postulierten neuen Antriebsmechanismen (v1: EM-Drive, Woodward-Effekt). Simulationszahlen sind
keine Vorhersage für den Aufbau. Linie B ist nicht Gegenstand.

---

## 12 · Offene Punkte vor dem Einfrieren

**Werkzeuge**, die vor dem Einfrieren im Repository liegen müssen (Commit-Hashes mit Teil A):

1. die Optionen `--section`, `--phi3` und `--f` von `code/linear_solver.py` (erledigt: seit Commit
   `069cb9b` im Repository; mit ihnen ist der Zahlennachweis gerechnet);
2. ein Auslegungswerkzeug für ungleiche Module, gemessene Übertragungsfunktion, k_max, Zell- und Modullage,
   mit N_k, F_min, γ₁, A, Zellkräften für beliebige (φ₂, φ₃) und ∂ŷ/∂f, abgeglichen mit `linear_solver.py`
   bei M = 0,650 kg und identischen Egg-Profilen (Bewegungsprofil der Simulation). `code/auslegung.py` und
   seine Tests geben PB1 noch nach der Fassung vom 25.09.2026 aus (u_c ≤ 0,25·D/c_B); nach der Entscheidung
   über die Regeln (unten) werden die notwendige Bedingung Δ/t_eq, die Auslegungsgrenze (A8) und die
   D-Fassung nachgezogen;
3. die Aufnahmesoftware mit Registrierungskennung, Zeitstempeln und Hash-Kette;
4. die Anpassverfahren von P0.4 (1-FG-Modell an die komplexe Übertragungsfunktion, Frequenzband, Gewichtung
   mit der Kohärenz) und die Profilauswertung von P0.5 einschließlich Δδⱼ;
5. das Pilotskript;
6. das Auswerteskript für §8.1–§8.5, den Zeltfit (§8.6) und die H3-Fortpflanzung (§8.7);
7. Randomisierungsskript, Monitor der Regeln ohne Anzeige von Zwischenwerten, Blocksteuerung ohne
   Bedienereingriff;
8. Pipelinetest und Planungs-/Kalibriersimulation (A9.11): Synthetische Daten mit exakter Superposition
   müssen H1 bestätigen. Daten mit Hertz-Kontakt oder Modulkopplung, deren größtes Residuum mindestens
   2·Δ_rel beträgt, müssen es mit Wahrscheinlichkeit ≥ 0,8 falsifizieren; knapp über Δ_rel ist „nicht
   entscheidbar“ der erwartete Ausgang (§8.5). Je Szenario 1000 Kampagnen über mehrere Präzisionsstufen für
   Fehlerraten, den kritischen Wert c von H1, Überdeckung, Power, n_min, n₀, Rauschbias und das Quantil für
   ε_ctrl. Erfüllt die Simulation die Kriterien von A9.11 nicht, werden die Regeln von §8.4–§8.6 vor dem
   Einfrieren überarbeitet (Eintrag in A0).

**Offene Festlegungen der Entscheidungsregeln (Entwurf 10/2026).** Vor dem Einfrieren zu wählen, gestützt
auf die Planungs- und Kalibriersimulation mit angenommenen Rauschmodellen (Werkzeug 8); die gewählte Fassung
und ihr Grund kommen in A0.

| Festlegung | Optionen und Folgen |
|---|---|
| Regel für Δ_rel (§8.5) | (a) Δ_rel,q = Δ_q (Vorschlag): kleinster Wert, der die Ausgänge disjunkt hält; jede nachgewiesene Abweichung über ein Viertel der Struktur falsifiziert. (b) Δ_rel,q = κ·Δ_q mit festem κ > 1: Falsifikation erst bei größerer Abweichung, mehr „nicht entscheidbar“. (c) Δ_rel,q = max(Δ_q; Δ_phys,q), Δ_phys,q die Abweichung einer vorab benannten kleinsten relevanten Alternative (etwa einer Aktorkopplung bestimmter Größe), mit dem Auslegungswerkzeug berechnet: physikalisch begründet, verlangt aber eine vorab festgelegte Alternative und ihr Modell |
| D für Re und Im N_k (§8.5) | Fassung A (bisher): D = max_i \|N̂_k,i\|. Unter Lauf-zu-Lauf-Streuung der Module kann dann Re/Im N₁ die Bestätigung binden, weil die Struktur von N₁ auf dem Schnitt klein ist, seine Streuung aber mit der Einzelmodulamplitude wächst (A8); Folge: mehr Läufe. Fassung B: Durchmesser der Zeigermenge; im Beispiel A4 etwa doppelte Grenze für N₁ und N₂, kleinere für N₃ (A8) |
| H2-Fitfenster (§8.6, A9.6) | (a) w = 6° fest (Vorschlag): drei Punkte je Seite; im Beispiel A4 knicken die Flanken bei etwa ±6° (A4). (b) w = 8° fest: mehr Punkte und kleinere Halbbreite, aber ein größerer Formfehler des Zelts, der Messung und Vorhersage gleich trifft. (c) das größte w ∈ {4°, 6°, …, 20°}, bei dem der Zeltfit an der Vorhersage die Spitze um höchstens 0,1° gegen das Maximum der fein gerechneten Vorhersage verschiebt: passt sich der Form an, braucht die Vorhersage auf einem feinen Phasenraster |
| Fassung von H3 (§8.7) | Fassung K (Kennzeichnung) oder Fassung I (Betriebsimpedanz); hängt am Entscheid über Messkette und Wegkanal (unten) |
| Entscheidungslogik von H2 und H3 (§9.3) | (a) Signifikanzlogik wie bisher: bestätigt bei 0 ∈ Intervall (H2) bzw. kein \|z\| > c (H3), zusammen mit der Präzisionsbedingung (Halbbreite ≤ 1° bzw. PB3). Das ist eine Nicht-Ablehnung, wie sie A8 für H1 verwirft: Bei hoher Präzision falsifiziert schon eine kleine, irrelevante Abweichung. Die H2-Halbbreite beträgt etwa 3/(SNR·√n) (A9.2); bei großem SNR ist sie weit kleiner als 1°, und dann falsifiziert schon eine Spitzenverschiebung dieser Größe H2. (b) Äquivalenzlogik wie bei H1: H2 bestätigt, wenn [a⁰, b⁰] und [a¹, b¹] in ±δ_H2 liegen (etwa δ_H2 = 1°, die bisherige Halbbreitengrenze), falsifiziert, wenn beide auf derselben Seite außerhalb von ±δ_H2 liegen; H3 bestätigt, wenn jedes Intervall r ± t(0,95; ν_eff)·u_c in ±0,10·\|N̂_k⁽ʲ⁾\| liegt (PB3 als Äquivalenzgrenze), ohne „kein \|z\| > c“. Folge: Bestätigung wird mit wachsender Präzision nicht unwahrscheinlicher; δ_H2 und eine Relevanzgrenze für H3 brauchen eine Begründung vor dem Einfrieren, und die Kalibriersimulation muss sie prüfen. Dieser Entwurf führt (a) |

**Offene Hardwareentscheidungen (offen – Entscheidung des Autors).** Dieser Entwurf legt sie nicht fest.
Ihre Folgen für die Entscheidungsregeln:

| Entscheidung | Optionen | Folge für die Entscheidungsregeln |
|---|---|---|
| Messkette und Wegkanal | Wegkanal mit Nanometerauflösung und Bezugspunkt unterhalb der Zellen; oder Wegkanal ohne diese Auflösung (P0.5, Einfederung nur beschreibend) | Fassung I von H3 nur mit dem ersten; Auflösung und Rauschen der Kraftkanäle bestimmen u_c,erw und damit n_min |
| Kontakt und Dämpfungsziel | steif mit hoher Dämpfung; steif mit geringer Dämpfung; weicher Kontakt | bestimmt f₁ und k_max (§5.3 b) und die Größe nichtlinearer Kontaktanteile gegen die Nachweisgrenze |
| Umfang von E1 und Nennlast | E1 streichen; eigene weiche Kontaktstufe; Zellen für hohe Spitzenlast | Nennlast und Auflösung stehen im Zielkonflikt; höhere Nennlast heißt größeres u_c,erw und mehr Läufe |
| Antrieb | Nocke oder programmierbarer Aktor; ob ein programmierbarer Linearaktor vorhanden ist, ist offen | bestimmt Profilspektrum, Phasenjitter und Lauf-zu-Lauf-Streuung, damit u_c,erw und die Bindung von N₁ |
| Lage von Zellen und Modulen | Module über den Zellen (G0) oder um 60° gedreht auf halbem Zellradius (G60h) | bestimmt Zellkräfte (§5.3 a) und Superposition je Zelle; die Regeln für H1 an der Summe bleiben gleich |
| Ort von Phase 0 (institutionelle Anbindung) | Messplatz und Kalibrierung bei einer Einrichtung; oder eigener Messplatz mit externer Kalibrierung | bestimmt T_verfügbar und damit n_max (§5.3 c) |

**Weitere Klärungen:** Ausführung von D2 (auch in Kombinationskonfiguration, mit Schwelle und Folge für H1,
§5.2) und der Parkposition; Lage von Zellen und Modulen (bestimmt die Zellkräfte, A2.5, und E3); genauer
Titel von DKD-R 3-10 Blatt 2 (Sinusverfahren, Ausgabe 2019); Wahl der Registrierungsplattform; endgültige
Dateinamen von Hauptdokument und Anhang; eigene Präregistrierung für Linie B. Die Diskrepanz bei Frequenz
(10 Hz im Code gegen 2,2 Hz in älterer Dokumentation) und Profilasymmetrie berührt v2 nicht, weil f nach §5.3
gewählt und das Profil gemessen wird.

**Folgen für andere Dokumente:** Liste im Anhang A0. Die dort genannten Stellen in README, `overview.md`,
Exposé, Werkstattbericht, Literaturabgleich, `einordnung.md`, `zehn_fragen.md` und `neuheitsgrad.md` sind
nachgezogen. Die Kanalzahl führt das Exposé seit den Nachträgen vom 2. Oktober 2026 als offen, abhängig
von Messkette und Wegkanal (zuvor „11 Kanäle“ bei neun aufgezählten).
