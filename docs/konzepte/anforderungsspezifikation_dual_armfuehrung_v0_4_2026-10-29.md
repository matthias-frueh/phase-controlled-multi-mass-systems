# PCMMS – Anforderungsspezifikation Dual-Armführung der inneren Massen (Ebene L2)

Version 0.4 (Entwurf) – 29.10.2026 – ersetzt v0.3, v0.2 und v0.1 vom selben Tag

Projekt: Phasenkontrollierte Mehrmassensysteme (PCMMS)
Autor: Matthias Früh, ORCID 0009-0005-9984-4207
Status: Entwurf – inhaltlich angelegt, fachliche Absicherung läuft; keine Entwicklungs-, Bau- oder Beschaffungsentscheidung
Zuordnung: Antriebsoption „programmierbarer Aktor“ (AP-01; Arbeitsübersicht Technik 29.10., Punkt 03); Linie B nach Abgrenzung 29.10.; berührt AP-04, AP-05, AP-06, AP-07, AP-27, AP-28
Bezug: Formelverzeichnis v2.8 (§3 Gl. 3–6, §10.6 Egg-Profil und aktiv geführte Rückholung, §10.7 Referenzprofil, §11.1 Anschluss an Linie B und C); Arbeitspapier v2.5; Präregistrierung v2 (Entwurf); Anschlusspapier Robotik (Evidenzmatrix L4-027 bis L4-030); `PCMMS_Arbeitsuebersicht_Technik_2026-10-29.md` (nachfolgend AÜT-Punkt); Abgleichnotiz 2026-10-29 v4
Lizenz: CC BY 4.0 (Ordner docs/, siehe LICENSE-CC-BY-4.0)

> **Vermerk (29.10.2026).** Originaldatei `PCMMS_Anforderungsspezifikation_Dual-Armfuehrung_v0_4_2026-10-29.md`,
> Entwurf v0.4 vom 29.10.2026; hier unverändert bis auf diesen Vermerk und die Lizenzzeile. Anforderungsspezifikation für eine duale,
> armähnliche Führung der inneren Massen (Ebene L2), angelegt nach der Abgrenzung der Linien A/B/C durch den Autor vom
> 29.10.2026 ([`../abgleichnotiz_2026-10-29_v4.md`](../abgleichnotiz_2026-10-29_v4.md)). Zuordnung: Linie B nach
> dieser Abgrenzung, Stufe S5 / AP-28; zugleich eine Ausprägung der Antriebsoption „programmierbarer Aktor“ (AP-01,
> Entscheidung des Autors offen; [`../arbeitsplan_status.md`](../arbeitsplan_status.md)). Konzept: keine Messdaten,
> keine Bau-, Antriebs- oder Beschaffungsentscheidung. Entscheidung D-1 des Autors (29.10.2026): Die Stufenfolge des
> Arbeitsplans bleibt; B2 wird nur als langfristige Randbedingung für AP-01, AP-04 und AP-06 berücksichtigt
> (Erweiterbarkeit prüfen, Folgen dokumentieren), ohne Verpflichtung von V1 zur Armführung oder zu gemeinsamer
> Hardware. Die Teilung B1/B2 ist ein Vorschlag des Abgrenzungsentwurfs
> ([`../linie_b/abgrenzung_v3_6_entwurf3_2026-10-29.md`](../linie_b/abgrenzung_v3_6_entwurf3_2026-10-29.md)), nicht
> beschlossen (D-2). Das [Anschlusspapier Robotik](anschlusspapier_robotik_2026.md) führt Robotik als nachgelagerte
> Validierungsebene; dieses Dokument gibt ihr eine zweite, getrennte Rolle (Aktorik L2) – Ergänzung des
> Anschlusspapiers offen (D-4). Zahlenherkunft ist im Dokument gekennzeichnet; das Ergebnis der Prüfung der
> [AP]-Angaben gegen das Arbeitspapier v2.5 und des Abgleichs mit Anforderungsprofil, Anschlusspapier Robotik und
> Lageregelung steht in der Statusspalte von [`README.md`](README.md) und im Pull Request vom 29.10.2026.
>
> **Prüfvermerk (29.10.2026, Pull Request).** Ergebnis der Prüfung nach Abschnitt S3 des Auftrags, getrennt nach
> bestätigt, abweichend und ungeprüft; der Dokumenttext ist nicht verändert, die Kennzeichnung [AP] im Text gilt mit
> dieser Zuordnung als [AP✓], wo eine Fundstelle genannt ist.
> - *Bestätigt* (Arbeitspapier v2.5, Quelltext `../arbeitspapier/PCMMS_Arbeitspapier_v2_5.tex`): AF-11 Sinus-Kollaps
>   der Phasenkarte auf R, keine Schiefe im Dauerkontakt (Z. 113, Z. 5120–5126); AF-32 dynamische Liftoff-Schwelle
>   R_c = 1,45 aus R_c^qs = 1,94 und Transmissibilität 1,34, numerisch 1,44–1,48 (Z. 4168–4204, Gl. eq:Rc-dyn);
>   AF-32 Umschlag vom kurzzeitigen Abheben zum prellenden Betrieb zwischen R = 1,62 und 1,70 (Z. 4209–4212);
>   AF-23 Spitzenkraft näherungsweise ∝ √k (Z. 4337–4340) und 15,9·Mg bei ζ = 0,05 (Tabelle Z. 4402, Text Z. 4440);
>   AF-18 Zeltkurve ≈ 0,23 N je Grad zu kleineren und ≈ 0,19 N je Grad zu größeren φ₂ (Z. 4076–4077), Spannweite
>   4,56 N am Referenzsatz und 0,56 N am Kandidaten (Z. 2378–2379, 4094–4095); AF-26 Leerlauf mit bestromter, aber
>   blockierter Aktuierung als wichtigster Einzelversuch der Kampagne (Z. 3271–3274). Präregistrierung v2
>   (`../praeregistrierung_v2_entwurf.md`): H1 mit F_min − ⟨N⟩ und N₁, N₂, N₃ primär (Z. 161–162), H2 primär
>   (Z. 172), H3 und H4 (Schiefe) sekundär (Z. 186, 196), A und F_max beschreibend (Z. 220).
> - *Abweichend oder zu präzisieren*: AF-11 „Exzenter- oder Kurbeltriebe … scheiden als Zielantrieb aus“ – das
>   Arbeitspapier führt sie bei konstanter Drehzahl als Referenzlauf, der den Beitrag der Profilasymmetrie beziffert
>   (Z. 2278–2282); mit AF-11, AF-15 und AF-28 vereinbar, eine ausdrückliche Ergänzung um den Referenzlauf ist offen.
>   Abschnitt 2, „Liftoff-Anteil Λ explorativ“: in der Präregistrierung v2 nicht belegt (λ dort nur in §9 als nicht
>   ausschließender Wert, Z. 835); bleibt [AP] ohne Haken.
> - *Ungeprüft*: O-1, der vollständige Volltextabgleich mit Anforderungsprofil, Anschlusspapier Robotik und
>   Lageregelung; stichprobenartig stimmen die Ebenen L0–L3 (Anforderungsprofil Z. 107–110, Anschlusspapier Z. 46–49)
>   und die Begriffe Primär-/Sekundärkanal (Anschlusspapier Z. 57, 71) mit diesem Dokument überein. Die Bilanzen in
>   Abschnitt 2 und AF-30 wurden mit Formelverzeichnis v2.8 Gl. (3), (4), (6) nachvollzogen; die Fesselbilanz ist in
>   v0.4 nach Korrektur des Autors (K-1) berichtigt.

## 0. Zweck, Geltung, Zahlenherkunft

Diese Spezifikation legt fest, was eine armähnliche, duale Führung der inneren Massen leisten muss, damit sie (a) die Wellenform-Observablen der Linie A nicht verfälscht, (b) die grenznahen Versuche der Linie B trägt und (c) die Nulltests des Projekts besteht. Sie beschreibt Anforderungen, keine Lösung, und keinen Antriebstyp, Armtyp oder Hersteller. Zahlenwerte aus dem Referenzmodell sind als solche gekennzeichnet und keine V1-Vorgaben (AÜT-Punkt 25: Ergebnisse nach Parametersatz trennen).

Kurzbild (Autor, 29.10.2026): Je gehaltener Masse zwei Arme (dual, nach dem Vorbild des menschlichen Arms); bei N = 3 Massen sechs Arme; gezielte Führung der gehaltenen Masse bzw. des gemeinsamen Massezentrums; Bewegungsprofile werden ermittelt und optimiert; Maximallasten, Grenzwerte, Kontaktverlustbedingungen und Messungen im kleinsten Bereich.

Zahlenherkunft (Kennzeichnung hinter jeder Angabe):
- [FV] Formelverzeichnis v2.8, am 29.10. im Volltext geprüft.
- [AÜT] Arbeitsübersicht Technik 29.10., am 29.10. im Volltext gelesen.
- [PA] Projektablage-Dokument, am 29.10. als Auszug gelesen (Evidenzmatrix, `neuheitsgrad.md`, Vorarbeit-Dokument, `00_UEBERSICHT_Linie_B_C.md`).
- [AP] übernommene Projektangabe (Arbeitspapier v2.5 bzw. Projektstand), am 29.10. nicht neu geprüft – vor jedem Zitat gegen die Quelle prüfen.
- [Ü] modellabhängiger Überschlag dieser Spezifikation; Annahmen genannt; nur Größenordnung.
- [LB] Lehrbuchbeziehung (ideale Gasgleichung, Potentialtheorie).

## 1. Einordnung

- Ebenen [FV, PA]: L0 passiver Messrahmen (Messapparatur, nicht Untersuchungsgegenstand), L1 Träger/Rahmen, L2 bewegte Module, L3 Kopplung Träger–Module. Die Armführung ist L2; die Reaktionskräfte der Arme auf den Träger sind L3. Für keine Ebene existiert ein gebauter Aufbau.
- Rolle der Robotik [PA, AÜT]: Das Anschlusspapier Robotik führt Robotik als nachgelagerte Vergleichs- und Validierungsebene (nach V1, AÜT-Punkt 65). Diese Spezifikation gibt der Robotik eine zweite, davon getrennte Rolle: Aktorik der Ebene L2. Primärkanal bleibt die direkte Kraftmessung; Gelenkmomente und Motorströme sind Sekundärkanäle mit dokumentierter Modellabhängigkeit (L4-029).
- Neuheit [PA]: Mehr als zwei innere Massen, Phasendifferenz als Steuerparameter und asymmetrische Bahnform sind laut `neuheitsgrad.md` §7.1 besetzt. Diese Spezifikation beansprucht keine Prinzipneuheit; sie beschreibt eine Konstruktions- und Führungsform im Dienst der Zielgröße Wellenformstatistik (§7.2).
- Stufenfolge und Fernziel (Entscheidung D-1, Autor, 29.10.): Die Stufenfolge des Arbeitsplans bleibt. B2 wird als langfristige Randbedingung für AP-01, AP-04 und AP-06 berücksichtigt – das heißt zunächst: Erweiterbarkeit prüfen und Folgen dokumentieren. Es verpflichtet V1 weder zur Armführung noch zu gemeinsamer Hardware für A und B.
- Linien: Die Teilung in B1 (Medienkopplung) und B2 (grenznahe Kontaktdynamik) ist ein Vorschlag des Abgrenzungsentwurfs (D-2 offen). Wo diese Spezifikation „B2“ schreibt, ist die Abgrenzung 29.10. gemeint, nicht eine beschlossene Linienstruktur.

## 2. Notation und Bilanz

Formelverzeichnis v2.8 [FV], z nach oben, konstante Massen, definierte Systemgrenze:

- F_c(t): Kontaktkraft (in Arbeitspapier und Präregistrierung N(t)); einseitig, F_c ≥ 0.
- Gl. (3): M·z̈_S = F_c + F_ext,z − M·g. Gl. (4): F_c = M·g + S_true − F_ext,z mit S_true = Σ_k m_k·z̈_k (k = 0 … n, Rahmen eingeschlossen).
- Gl. (6): ⟨F_c⟩ = M·g − ⟨F_ext,z⟩ + b_w, b_w = M·Δv_S/T_w (Endlich-Fenster-Term).
- F_ext,z wird hier zerlegt: F_ext,z = F_auf + F_med,z + F_par. F_auf Auftrieb der Hülle (Symbol neu, nicht im Formelverzeichnis; F̄_A ist belegt für Modell A der Richtungsnotiz v5.2 – O-11), F_med,z vertikale Medienkraft (Linie B), F_par parasitäre Kraftpfade (Kabel, Schläuche, Fessel).
- Restlast: W_R := M·g − F_auf; Restlastanteil w_R := W_R/(M·g). In Linie A ist w_R = 1 (bis auf den kleinen Auftrieb des Körpers selbst).
- Kontaktverlust (Liftoff): F_c → 0, d. h. S_true ≤ −(M·g − F_ext,z) = −W_R + F_med,z + F_par. Die Armführung bestimmt S_true(t); die Restlast bestimmt, wie viel innere Beschleunigung bis zum Kontaktverlust bleibt.
- Profil: T = T_f + T_r, β = T_f/T (Vorwärtsanteil, Entwurfswert ≈ 0,8, keine Festlegung; §10.6); Referenzprofil der Engine mit Hold-Anteil β_h (§10.7); Hubangaben stets Spitze-Spitze; Phasenraster 360°/G mit endpoint=False.
- Observablen: F_min − ⟨N⟩ und Harmonische F_c,m (m = 1–3) primär, γ₁ sekundär, Asymmetrieverhältnis beschreibend, Liftoff-Anteil Λ explorativ (Präreg v2, Entwurf [AP]); Π_N = F_N,max/µ_N [FV].

## 3. Anforderungen

Kennung AF-xx. Prüfart: R = Rechnung/Simulation, I = Inspektion/Dokument, P = Prüfstand (erst nach Anbindung, AP-18). Bezug nennt die Projektstelle, aus der die Anforderung folgt.

### 3.1 Systemgrenze und Bilanz

- AF-01 Rahmen, Arme, Antriebe, Steuerung, Energieversorgung, gehaltene Massen und – in Linie B – die Auftriebshülle liegen innerhalb der bilanzierten Masse M. Für jeden Versuch wird festgelegt, ob L1 und welche Sensoraufsätze innerhalb von M liegen (Formelverzeichnis §3 [FV]; AÜT-Punkt 22). [I]
- AF-02 Jeder Kraftpfad nach außen außer Gewicht und Kontakt wird benannt und gehört entweder zu F_par (Störgröße, gemessen, unter ε_ctrl) oder zu einem Versuchsparameter (F_auf, F_med,z) – nie unbemerkt zu beidem (AÜT-Punkt 23). [I, P]
- AF-03 Kein Massenaustausch mit der Umgebung während eines Laufs und keine erzwungene Luftströmung (Lüfter, Abluft, Ausgleichsventile): Ein Luftstrom ist ein Impulsübertrag ans Medium – in Linie A eine Störung, in Linie B eine unkontrollierte Versuchsgröße. Kühlung passiv oder thermisch gepuffert (O-7). [I]
- AF-04 Energieversorgung an Bord oder über einen dokumentierten, kraftarmen Pfad; die parasitäre Kraft des Pfads wird gemessen (O-3). [P]

### 3.2 Kinematik und Freiheitsgrade

- AF-05 Je gehaltener Masse mindestens ein geführter Freiheitsgrad in z, weil nur S_true die Kontaktkraft moduliert (Gl. 4 [FV]). [R]
- AF-06 (bedingt) Halten beide Arme gleichzeitig dieselbe Masse und sind sie am gemeinsamen Träger befestigt, entsteht eine geschlossene kinematische Schleife Träger–Arm 1–Masse–Arm 2–Träger. Das ist eine Konsequenz des Konzepts „zwei Arme je Masse“, keine Konstruktionswahl. Eine geschlossene Schleife ist nicht dasselbe wie statische Überbestimmung: Freiheitsgrade, Gelenke, Nachgiebigkeit und Lastaufteilung bleiben auszulegen. Gefordert ist, dass die Lastaufteilung zwischen den Armen definiert ist und im Modell geführt wird; innere Verspannungskräfte heben sich in der Bilanz auf, beeinflussen aber Reibung, Spiel und Wärme (O-6). [R, I]
- AF-07 Unerwünschte Querkräfte und Kippmomente der Massenführung auf die Auflage bleiben innerhalb festgelegter, messtechnisch überprüfter Grenzen; die Grenzwerte folgen aus Arbeitspunkt und Auflage (AP-04, AP-27), die Prüfung aus Zellkräften oder Rahmenkanälen. Ob und welche horizontalen Freiheitsgrade die Führung erhält, ist Teil der Kinematikauslegung (O-6); die Medienkopplung der Linie B kann sie erfordern, das ist dort zu begründen. Wie das konstruktiv erreicht wird – eigene Hardware mit einem Freiheitsgrad, gesperrte Achsen, Führung – bleibt offen (O-2, O-6; AÜT-Punkt 09). [I, P]
- AF-08 Die Bahn des Massenmittelpunkts jeder gehaltenen Masse folgt eindeutig aus der Armkinematik (direkte Kinematik), damit z̈_k(t) und S_true(t) rekonstruierbar sind. Bei Vektortrajektorien gelten die Nahtbedingungen je Komponente (§10.6, Gl. 48–49 [FV]). [R]
- AF-09 Die Lage des gemeinsamen Massezentrums ist im Betrieb berechenbar; ein Sollwert für das Massezentrum ist als übergeordnete Vorgabe zulässig (Autor, 29.10.). Horizontale Verlagerungen des Massezentrums erzeugen Kippmomente auf die Auflage; sie werden im Lastmodell der Auflage bzw. des Messrahmens geführt (AP-27) und unterliegen AF-07. [R]

### 3.3 Bewegungsprofil

- AF-10 Profile je Masse sind programmierbar, periodisch mit gemeinsamer Periode T und frei parametrierbar in Phase φ_k, Hub (Spitze-Spitze) und Form; Vorwärts- und Rückholphase nach §10.6 [FV], die Rückholung ist aktiv geführt. [I]
- AF-11 Asymmetrische Profile müssen darstellbar sein. Referenzmodell [AP]: Bei reinen Sinusprofilen kollabiert die Phasenkarte auf R = |1 + e^{iφ₂} + e^{iφ₃}| mit γ₁ = 0 ohne Kontaktverlust; Exzenter- oder Kurbeltriebe mit konstanter Drehzahl scheiden als Zielantrieb aus. [R]
- AF-12 Teilprofile sind mindestens stückweise zweimal differenzierbar mit beschränkter Beschleunigung; Nähte mindestens C¹, für stetige Beschleunigung C²; Beschleunigungs- und Ruckgrenzen passend zu Aktorik und Messbandbreite (§10.6 [FV]). Harte Sprünge im Positionssollwert sind keine realisierbaren Trajektorien (§10.8 [FV]). [I, R]
- AF-13 Für jeden Versuch werden Profilfunktion oder versionierte Profildatei, Normierung, Raumorientierung, Nahtbedingungen und Parameter hinterlegt (§10.6 [FV]). Der Hold-Anteil β_h des Referenzprofils wird nicht ungeprüft mit dem Vorwärtsanteil β gleichgesetzt (§10.7 [FV]; O-4). [I]
- AF-14 Lage- und Geschwindigkeitsprofil werden unterschieden: Linie A Lageprofil (Hub), Linie B bisher Geschwindigkeitsprofil (Egg der Richtungsnotiz, V_FAST [PA]); ein Profilvergleich nennt die Normierung – gleicher Hub, gleiche RMS-Amplitude oder gleicher Energieeinsatz (AÜT-Punkt 36). [I]
- AF-15 Zur Gegenprobe muss die Armführung die Profilform eines Nockenantriebs nachfahren können, damit die beiden AP-01-Optionen vergleichbar bleiben (Profiltreue, AÜT-Punkt 04). [R, P]
- AF-16 Anlauf, Parkposition und Wiederanlauf nach Eingriff sind definierte Zustände (Frequenzrampe T_ramp, Amplitudenhülle; AÜT-Punkt 13). Adaptive Änderungen von Frequenz, Phase oder Amplitude werden mitprotokolliert (§10.8 [FV]). [I]

### 3.4 Phasenkopplung und Zeitbasis

- AF-17 Alle N Massen laufen auf einer gemeinsamen Zeitbasis; die mechanische Phase jeder Masse wird gemessen, nicht nur kommandiert – eine PWM- oder Hüllkurvenphase ist keine gemessene mechanische Phase (AÜT-Punkt 24). [I, P]
- AF-18 Phasenjitter und Phasendrift werden spezifiziert und protokolliert. Orientierung aus dem 2°-Feinsweep (`data/finesweep_2deg_120_240.csv`): Abfall der Zeltkurve ≈ 0,19–0,23 N/° am weichen Referenzkontakt [AP]; am V1-Kandidaten Spannweite 0,56 N statt 4,56 N [FV] – Referenzzahlen, keine V1-Vorhersage. Grenzwert offen (O-5). [R]
- AF-19 Kraftkanal, Kinematikkanäle und Phasenkanal teilen eine Zeitbasis; Kanalverzögerungen sind bestimmt und passen zur höchsten ausgewerteten Harmonischen (AÜT-Punkt 19). [I, P]

### 3.5 Kinematikmessung (AP-07)

- AF-20 Die Position jeder gehaltenen Masse wird zeitsynchron mit dem Kraftkanal erfasst; Auflösung, Abtastrate und Übertragungsfunktion erlauben die Rekonstruktion von z̈_k(t) mindestens bis zur dritten Harmonischen der Grundfrequenz mit Reserve. Zahlenwerte gehören zu AP-06/AP-10 (AÜT-Punkte 17–18). [I]
- AF-21 Aus Gl. 4 [FV] folgt F_c − ⟨F_c⟩ = (S_true − ⟨S_true⟩) − (F_ext,z − ⟨F_ext,z⟩). Der Vergleich der rekonstruierten Größe S_true(t) mit F_c(t) − ⟨F_c⟩ ist nur dann ein Nulltest der Messkette (zweiter Pfad neben ΔF̄_Zustand), wenn der zeitveränderliche Anteil von F_ext,z vernachlässigbar ist oder getrennt gemessen wird; diese Bedingung wird je Versuch benannt und belegt. In Linie A ist sie für F_par und Luftkräfte nachzuweisen (AÜT-Punkt 23); in Linie B mit Medienkraft ist sie nicht erfüllt – dort ist das Residuum −(F_med,z − ⟨F_med,z⟩) ein Messsignal, kein Nulltest. Bei Liftoff oder elastischer Aufstellung geht die Rahmenbewegung m₀·z̈₀ ein (Gl. 5 [FV]). [R, P]
- AF-22 Kontaktverlust und Wiederanlage werden unabhängig vom Kraftsignal erkannt (Kontakt-, Weg- oder Kinematikkanal; AÜT-Punkt 17), kompatibel mit dem Ereignislöser (AP-03). [I, P]

### 3.6 Lasten, Steifigkeit, Spiel

- AF-23 Arme, Gelenke und Antriebe werden gegen die Spitzenlasten des Auslegungswerkzeugs (AP-02, `auslegung.py`) für den gewählten Parametersatz ausgelegt – nicht gegen Referenzzahlen und nicht gegen die früheren 20-/10-kg-Angaben (AÜT-Punkt 10). Zur Orientierung aus dem Referenzmodell: N_max ∝ √k, bis 15,9·M·g bei ζ = 0,05 [AP]. Statische Last, dynamische Spitzen und Stoßlasten bei Wiederanlage werden getrennt betrachtet. [R]
- AF-24 Die Eigenfrequenzen der Armstruktur liegen deutlich über der höchsten ausgewerteten Harmonischen. Das Gesamtsystem ist nicht quasistatisch (Referenzparametersatz: zweite Harmonische auf der Kontaktresonanz, ϱ₂ = 1,013; Formelverzeichnis §7.4 [FV]); unmodellierte Armnachgiebigkeit verfälscht die Wellenform. Nachweis durch Modalrechnung oder Messung. [R, P]
- AF-25 Spiel in Gelenken und Getrieben ist begrenzt und wird gemessen; Umkehrspiel erzeugt Kraftspitzen, die als höhere Harmonische erscheinen. [I, P]

### 3.7 Nulltest-Tauglichkeit

- AF-26 Leerlauf-Modus: Antriebe bestromt, mechanisch blockiert, Profil kommandiert – das wichtigste Gegenexperiment gegen phasenkorrelierte Einstreuung in die Messkette [AP]. [I, P]
- AF-27 Reproduzierbare Ruhelage (Home) aller Arme; die Ruhelage ist der Zustand der Referenzmessungen. [I]
- AF-28 Kontrollfälle sind mit der Armführung fahrbar: Sinus, Modulvertauschung, Spiegelung, Synchronzustand, Zeitumkehr (AÜT-Punkt 33; Richtungsnotiz v5.2 Symmetriekontrollen [PA]). [R, I]

### 3.8 Grenznähe und Auftriebshilfe (Linie B, Abgrenzung 29.10.)

- AF-29 Die Restlast W_R = M·g − F_auf ist Versuchsparameter und wird während des Laufs mitgemessen: Referenzwägung vor und nach dem Lauf, Temperatur von Füllgas und Umgebungsluft, Luftdruck, Feuchte, Permeationsrate der Hülle über die Laufdauer. Der Driftmechanismus hängt vom Hüllentyp ab [LB]: Bei volumenfester (gespannter) Hülle folgt F_auf der Umgebungsluftdichte (ideale Gasgleichung: ≈ 0,35 %/K bei 293 K, ≈ 1 %/10 hPa bei 1013 hPa). Bei freier, nicht gespannter Hülle gleicht sich der Innendruck an; die verdrängte Luftmasse bleibt in erster Näherung n_He·M_Luft, Druck- und Temperaturänderungen der Umgebung heben sich auf, und maßgeblich sind die Temperaturdifferenz zwischen Füllgas und Umgebungsluft (≈ 0,34 % der verdrängten Luftlast je Kelvin Differenz), die Luftfeuchte und die Permeation. Eigenwärme der Antriebe in oder an der Hülle erzeugt so eine betriebskorrelierte Auftriebsdrift. Der Leerlauf-Modus (AF-26) ist dafür eine Gegenprobe, keine Abdeckung: Ein blockierter, bestromter Antrieb hat nicht denselben Wärmeverlauf wie ein bewegter; die thermische Vergleichbarkeit (Leistungsaufnahme, Wärmepfad, Zeitverlauf) ist nachzuweisen, und die Temperatur des Füllgases wird als eigener Kanal geführt. Der Hüllentyp ist festzulegen (O-14). Überschlag [Ü] mit den Annahmen M ≈ 0,65 kg (V1-Kandidat [FV]), ρ_Luft ≈ 1,20 kg/m³, ρ_He ≈ 0,17 kg/m³ bei 20 °C: Hüllenvolumen ≈ 0,6–0,7 m³ ohne Hüllenmasse, verdrängte Luft ≈ 7–8 N, Drift von F_auf ≈ 0,03 N je Kelvin (Umgebungsdichte bei gespannter, Gas–Luft-Differenz bei freier Hülle); bei 5 % Restlast knapp 10 % je Kelvin. [I, P]
- AF-30 Drei Versuchskonfigurationen werden getrennt geführt, und je Lauf ist die Konfiguration eindeutig festgelegt: Kontaktaufstellung (w_R > 0, Messgröße F_c), Schwebe (w_R ≈ 0, freie Drift – Modell B der Richtungsnotiz, F̄_B = 0 [PA]), Fesselung (w_R < 0, gehalten – Modell C [PA], Messgröße Fesselkraft F_F; mit F_med,z nach oben positiv und nach unten ziehender Fessel gilt ohne weitere Kräfte M·z̈_S = F_auf + F_med,z − M·g − F_F, im stationären Mittel ⟨F_F⟩ = F_auf − M·g + ⟨F_med,z⟩ – Vorzeichen vom Autor am 29.10. korrigiert). Innerhalb eines Laufs auftretende Wechsel des Kontaktzustands (Kontaktverlust, Wiederanlage, Hüpfen) sind Untersuchungsgegenstand: sie werden erkannt (AF-22) und getrennt ausgewertet. Der statische Restlastanteil w_R bestimmt den momentanen Kontaktzustand nicht. Der Begriff F_c gilt nur bei Kontakt (O-10). [I]
- AF-31 Die Hülle ist nur am Körper befestigt (kein Bodenkontakt, keine Durchführung als Kraftpfad). Ihre zugesetzte Luftmasse wird für die reale Geometrie bestimmt und in M-Konvention und Modell aufgenommen (AÜT-Punkte 22, 32). Orientierung [Ü]: für eine Kugel ½·ρ_Luft·V [LB], beim Überschlag aus AF-29 ≈ 0,4 kg – Größenordnung M; andere Hüllenformen liegen anders, die Aussage ist die Größenordnung, nicht der Wert. Raumluftbewegung wird protokolliert. [R, I]
- AF-32 Abschaltregel bei erkanntem Hüpfen und Einschluss der gehaltenen Massen bei Armversagen (AP-05, AÜT-Punkt 12); Referenzmodell [AP]: Übergang zum Bouncing zwischen R = 1,62 und 1,70, dynamische Liftoff-Schwelle R_c ≈ 1,45 bei w_R = 1. Die Skalierung der Schwelle mit w_R ist eine Herleitung dieser Spezifikation [Ü] und mit der Engine zu prüfen (O-9). [R, I]

## 4. Nicht-Anforderungen (Abgrenzung)

- Keine Bauentscheidung; V1 wird nicht gebaut (Projektentscheidung, Vorbereitungsphase bis zur Anbindung).
- Keine Vorentscheidung über gemeinsame Hardware für A und B und keine Verpflichtung von V1 zur Armführung (D-1).
- Keine Festlegung auf Antriebsprinzip, Armtyp, Hersteller oder Steuerungsplattform; keine Festlegung der Kinematik (Freiheitsgrade, Gelenke, Nachgiebigkeit).
- Keine Aussage über Energieeffizienz oder Energieübertragung (Linie C geparkt; Formelverzeichnis §11.1 [FV]: erhöhter Kraft-RMS oder veränderte Schiefe sind kein Nachweis).
- Keine robotische Validierung im Sinne des Anschlusspapiers (nach V1, AÜT-Punkt 65).
- Keine Annahme der B1/B2-Teilung; sie bleibt Vorschlag (D-2).

## 5. Offene Fragen

- O-1 Abgleich mit docs/konzepte/ (Anforderungsprofil, Robotik-Anschlussdokument, Lageregelung): Inhalte hier nur über Evidenzmatrix und Recheck-Register eingesehen, nicht im Volltext.
- O-2 Armführung in Linie A: nach D-1 keine Verpflichtung; zu prüfen ist die Erweiterbarkeit der S1-Festlegungen (AP-01, AP-04, AP-06) in Richtung B2, mit dokumentierten Folgen.
- O-3 Energieversorgung: Akku an Bord oder Kabel; Kraftpfad quantifizieren (AF-04).
- O-4 Abbildung β ↔ β_h ↔ THOLD/TFAST der Engine; die Engine kennt kein β [FV].
- O-5 Grenzwert für Phasenjitter aus der Zeltkurvenbreite am gewählten Parametersatz (AF-18).
- O-6 Kinematik der dualen Führung: Freiheitsgrade je Masse, Gelenke, Nachgiebigkeit, Auflösung der Schleife und Lastaufteilung (AF-06, AF-07).
- O-7 Kühlkonzept ohne Luftstrom (AF-03).
- O-8 Arme innerhalb oder außerhalb der Hülle; Durchführungen (AF-31).
- O-9 Skalierung der Liftoff-Schwelle mit w_R mit der Engine prüfen (AF-32); dabei zugesetzte Luftmasse berücksichtigen.
- O-10 Fesselungsregime: Fessel als Kraftpfad, Messgröße F_F statt F_c – gehört das zu B oder zu C? (AF-30)
- O-11 Symbol für den Auftrieb im Formelverzeichnis anlegen (F_auf vorgeschlagen); Symbolkonflikte M, A, R, β beachten (AÜT, Pflegepunkte).
- O-12 Literaturprüfung dualer/bimanualer Manipulation vor externer Verwendung des Begriffs „Neuheit“ (AÜT-Punkt 57).
- O-13 Grenzwerte für Querkräfte und Kippmomente (AF-07) aus AP-04/AP-27 ableiten; Messweg (Zellkräfte, Rahmenkanäle) festlegen.
- O-14 Hüllentyp festlegen (volumenfest/gespannt oder frei); Temperaturmessung Füllgas und Umgebung; Dichte- bzw. Temperaturkompensation je Hüllentyp (AF-29).

## 6. Bezüge

- Formelverzeichnis v2.8: §3 (Gl. 3–6, Ebenen L0–L3), §7.4, §10.6–10.8, §11.1.
- Arbeitspapier v2.5: Sinus-Kollaps, Liftoff-Schwelle, Bouncing, Sensitivität, Feinsweep, Leerlauf-Gegenexperiment (alle [AP], vor Zitat prüfen).
- Präregistrierung v2 (Entwurf): Zielgrößen und Ausgänge.
- Richtungsnotiz Medienkopplung v5.2: Modelle A/B/C, Symmetriekontrollen.
- Anschlusspapier Robotik (über Evidenzmatrix L4-027 bis L4-030).
- `PCMMS_Arbeitsuebersicht_Technik_2026-10-29.md`: Punkte 03, 04, 09, 10, 12, 13, 17–19, 22–25, 32, 33, 36, 57, 65.
- Abgleichnotiz 2026-10-29 v4 (Entscheidungen D-1 bis D-6, Rückmeldungen R-1 bis R-7, Reststellenprüfung und Korrekturen K-1 bis K-4).

## Änderungslog

- v0.4 (29.10.2026, im Dokumentations-PR): vier Korrekturen nach Prüfung des Autors (K-1 bis K-4, Abgleichnotiz v4 Abschnitt 7): K-1 AF-30 – Vorzeichen der Fesselbilanz berichtigt, ⟨F_F⟩ = F_auf − M·g + ⟨F_med,z⟩ (v0.3 hatte ein Minus vor der Medienkraft); K-2 AF-21 – Nulltest vollständig formuliert, Bedingung an den zeitveränderlichen Anteil von F_ext,z benannt, in Linie B kein Nulltest; K-3 AF-30 – „ein Lauf, ein Regime“ ersetzt durch eindeutige Versuchskonfiguration je Lauf mit Erkennung und getrennter Auswertung von Kontaktzustandswechseln; K-4 AF-29 – Leerlauf-Modus als Gegenprobe statt Abdeckung, thermische Vergleichbarkeit nachzuweisen, Füllgastemperatur als Kanal. Keine inhaltliche Festlegung darüber hinaus geändert.
- v0.3 (29.10.2026): Reststellenprüfung vor dem Dokumentations-PR (dritte Rückmeldung R-6): AF-07 – verbliebener Satz „Für Linie B sind horizontale Freiheitsgrade vorzusehen“ entfernt, Freiheitsgrade bleiben Teil der Kinematikauslegung (O-6); AF-29 – Driftmechanismus nach Hüllentyp unterschieden (gespannt: Umgebungsdichte; frei: Gas–Luft-Temperaturdifferenz, Feuchte, Permeation), betriebskorrelierte Drift durch Eigenwärme ergänzt, Leerlauf-Modus als Gegenprobe benannt, Überschlag auf 0,6–0,7 m³ und 7–8 N präzisiert (O-14 neu); AF-30 – Vorzeichenkonvention der Fesselbilanz ergänzt, Gl. 3 und 6 nachgerechnet; Abschnitt 2 (Liftoff-Bedingung) gegen Gl. 4 nachgerechnet, unverändert. Keine inhaltliche Festlegung geändert.
- v0.2 (29.10.2026): zweite externe Rückmeldung vom 29.10. eingearbeitet, Präzisierungen des Autors: R-1 D-1 übernommen (Abschnitt 1, Abschnitt 4, O-2); R-2 AF-06 bedingt gefasst – geschlossene Schleife als Konsequenz, nicht als Wahl; Schleife ≠ statische Überbestimmung; Auslegung offen (O-6); R-3 AF-07 als Grenzwertanforderung für Querkräfte und Kippmomente statt „keine Horizontalbewegung“; Konstruktionsweg offen (O-13 neu); R-4 Zahlenherkunft [FV]/[AÜT]/[PA]/[AP]/[Ü]/[LB] durchgehend; R-5 B1/B2 ausdrücklich als Vorschlag gekennzeichnet (Abschnitt 1, Abschnitt 4). Keine neue Bau- oder Linienentscheidung.
- v0.1 (29.10.2026): erstellt aus der Abgrenzung 29.10. und dem Projektstand; nicht gegen docs/konzepte/ im Volltext abgeglichen (O-1).
