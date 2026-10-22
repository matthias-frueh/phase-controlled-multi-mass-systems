**PCMMS – Internes Arbeitspapier (lebendes Dokument)**

**Ringstruktur und Mehrkanal-Inversion**

*Vom Vorwärtsmodell F = Mg + S + C zur parameterbasierten Schätzung aus Messkanälen*

Matthias Früh · Gravidon Systemics Research · 2026 · ORCID 0009-0005-9984-4207

> **Vermerk (22.10.2026).** Originaldatei `PCMMS_Arbeitspapier_Ringstruktur_Mehrkanal_Inversion_Frueh_2026.md`,
> Fassung 2026 ohne Tagesdatum; Textfassung der Quelldatei (PDF) des Autors, hier unverändert bis auf diesen Vermerk
> (die Fußzeile „… · Seite“ stammt aus der Quelldatei). Nach eigener Angabe ein internes, lebendes Arbeitspapier, kein
> Preprint. Die gelben Markierungen des Originals sind im Klartext nicht mehr sichtbar; offene Punkte sind im Text mit
> „**offen:**“ eingeleitet (Abschnitte 4, 4.1 und 5). Konzept; die Tests T-A bis T-E (Abschnitt 6) sind im Repository
> nicht gerechnet, Messdaten gibt es nicht. Linie A (Randbedingung mean(F) = Mg, Gegenstand ist die Wellenform);
> Arbeitspaket AP-27 (Räumliche Last, N Module, Regelung, Robotik; Status „später; Konzept des Messrahmens vorgezogen
> (11.10.2026)“) mit Bezug zu AP-09 (Teil A: Identifizierbarkeit, Kontrollen, Tabelle C, E3; vorläufig),
> [`../arbeitsplan_status.md`](../arbeitsplan_status.md). Nach heutigem Repo-Stand eingeschränkt:
> - **Mehrkanal-Baustein (Abschnitte 2 und 5):** entspricht dem Konzeptbaustein
>   [`mehrkanal_messarchitektur_2026-05.md`](mehrkanal_messarchitektur_2026-05.md); nach dessen Vermerk gilt die
>   1/√N-Abschätzung nur für weißes, stationäres Rauschen.
> - **Zerlegung F = Mg + S + C:** Im [Formelverzeichnis v2.8](../formelverzeichnis/README.md) ist C der Sammelterm
>   relativ zum gewählten Vorwärtsmodell; ohne Kontrollen ist seine Zerlegung nicht eindeutig (Abschnitt „Zentrale
>   Messgleichung“). Ob phasenkorrelierte Anteile von C von S trennbar sind, hält Abschnitt 4.1 selbst als offen fest.
> - **Residuum:** Die primäre Prüfung der Präregistrierung v2 (H1) vergleicht die gemessene Kombination mit der
>   Superpositionsvorhersage aus gemessenen Einzelmodulantworten, nicht mit einem Vorwärtsmodell
>   ([Präregistrierung v2](../praeregistrierung_v2_entwurf.md), §3, §8.2).
> - **Messseite:** Rang und Nullraum der Nadelanordnung und den Rang des Kalibrier-Lastsatzes behandelt das Konzept zum
>   Sechs-Nadel-Messrahmen ([`nadelrahmen_dreimassenkoerper_2026-10.md`](nadelrahmen_dreimassenkoerper_2026-10.md);
>   NR-01 bis NR-09 in [`../../rechnungen/nadelrahmen/`](../../rechnungen/nadelrahmen/PROTOKOLL.md)); eine Schätzung
>   von (p, q) enthält es nicht.
> - **Baustein 13** (Abschnitte 1.3 und 7) liegt nicht im Repository.
>
> Lizenz wie der Ordner: CC BY 4.0 ([`../../LICENSE-CC-BY-4.0`](../../LICENSE-CC-BY-4.0)).

**Charakter dieses Dokuments. **Dies ist ein internes, lebendes Arbeitspapier — kein Preprint und keine Veröffentlichung. Es hält einen Arbeitsstand fest, markiert offene Punkte (gelb hinterlegt) und sammelt Testideen. Formulierungen sind bewusst vorläufig. Eine spätere, veröffentlichungsfähige Fassung wird erst nach numerischer Prüfung der hier skizzierten Ansätze erstellt.

*Geltende Randbedingung (durchgängig): mean(F) = Mg im eingeschwungenen Zustand. Alles Folgende betrifft die Form und Zerlegung der Welle, nicht ihren Mittelwert. Kein gerichteter Eigenantrieb.*

# 1. Ausgangspunkt: das Vorwärtsmodell

Die Ringstruktur-Skizze beschreibt die gemessene Kontaktkraft als Summe dreier klar getrennter Anteile:

*F(t) = Mg + S(t; p) + C(t; q)*

Die architektonische Trennung ist der eigentliche Wert: ein fester Gewichtsterm, ein intendierter Signalterm und ein Kopplungs-/Artefaktterm, der Spiel, Kontakte und Strukturkopplung ausdrücklich mitführt statt sie zu ignorieren.

## 1.1 Signalterm S(t; p)

Der intendierte Anteil aus N Modulen, mit glatter asymmetrischer Profilfunktion und Fensterung:

*S(t; p) = Summe über k von m_k · A_k · E( psi_k(t) )*

mit der glatten, asymmetrischen Profilfunktion *E(·)* (z. B. exponentielles An-/Abklingen, C¹-stetig), Amplituden *A_k*, Massen *m_k* und den Phasen *psi_k(t)*. Der Parametervektor p sammelt Amplituden, Phasenlagen und Profilform.

## 1.2 Kopplungs- und Artefaktterm C(t; q)

Der Anteil, der die reale Unvollkommenheit des Aufbaus trägt:

*C(t; q) = Summe über k von ( alpha_k·F_(r,k)(t) + beta_k·F_(t,k)(t) + gamma·I_k(t) )*

mit radialen und tangentialen Kopplungsbeiträgen sowie kurzen, nicht-idealen Pulsen *I_k(t)* (gaußförmig, kein Dirac). Der Parametervektor q sammelt die Kopplungskoeffizienten und Pulsparameter. Wichtig: C ist nicht Störung im Sinne von „wegmitteln“, sondern Teil des Modells — nur so lässt sich später Echtes von Artefakt unterscheiden.

## 1.3 Phasen

*psi_k(t) = ( t − phi_k − lambda·(Theta(t) + theta_k(t)) ) mod T*

Die Phasenkonstruktion erlaubt eine langsame, übergeordnete Modulation über *Theta(t)* — das ist der direkte Anschluss an die Zwei-Zeitskalen-Architektur aus Baustein 13. Parameterbereiche: T, dt_eff, A_k, m_k, lambda, sowie die Kopplungs- und Dämpfungskoeffizienten radial und tangential.

# 2. Die Lücke: das inverse Problem

Der bestehende Mehrkanal-Baustein beschreibt, wie F(t) gemessen wird. Die Ringstruktur beschreibt, wie F(t) modelliert wird. Was beide verbindet, ist bisher nicht ausgearbeitet:

*Kernfrage dieses Papiers: Wie schätzt man die Modellparameter (p, q) aus den gemessenen Kanälen — und wie trennt man dabei den intendierten Signalterm S vom Artefaktterm C?*

Das ist ein klassisches Inversions- bzw. Parameterschätzproblem. Formal: gegeben die Messkanäle, finde die Parameter, die das Vorwärtsmodell am besten erklären, mit sauberer Unsicherheitsangabe.

# 3. Die Messseite: Kanäle als Projektionen

Jeder Kanal misst eine andere Projektion derselben Dynamik. Das ist der Hebel: dasselbe (p, q) muss alle Kanäle gleichzeitig erklären.

| **Kanal** | **Misst** | **Rolle in der Inversion** |
| --- | --- | --- |
| Kraft (F_c) | Kontaktkraft am Interface | Primärbeobachter für S und C gemeinsam |
| Weg (z) | Verschiebung, mechanisch entkoppelt | liefert F_model aus Kinematik ergibt Trennung Kraft/Bewegung |
| Referenz | Untergrund ohne Anregung | kalibriert C-Anteil aus Drift/Vibration |
| Inertial (opt.) | Trägerbeschleunigung | unabhängige Konsistenzprüfung der Dynamik |

Der entscheidende Trick steckt im Wegkanal: aus der gemessenen Kinematik lässt sich ein Kraft-Erwartungswert *F_model* berechnen. Das Residuum

*r(t) = F_gemessen(t) − F_model( z(t), dz/dt, d²z/dt² )*

ist der Schlüssel: Ein Kraftbeitrag ohne korrespondierende Bewegung ist verdächtig — entweder Artefakt (C) oder ein Hinweis auf etwas Unmodelliertes. Genau hier sitzt die Detektionskraft der Architektur.

# 4. Inversionsstrategie (Arbeitsskizze)

Vorgeschlagenes Vorgehen, stufenweise von einfach nach anspruchsvoll. Bewusst noch nicht festgelegt — zum Durchspielen.

- **Vorwärtssimulation kalibrieren. **Synthetische Kanäle aus bekanntem (p, q) erzeugen, Rauschen aufprägen, Verarbeitungskette anwenden. Ground Truth ist bekannt — ideal zum Testen des Schätzers.

- **Wellenform-Kennzahlen als reduzierte Beobachter. **Statt der vollen Zeitreihe zunächst nur Schiefe, Liftoff-Anteil, Spitzen-zu-Mittel-Verhältnis und Ungerade/Gerade-Spektralverhältnis als Zielgrößen. Sie sind robust und niedrigdimensional.

- **Parameterschätzung. **Least-Squares oder Bayessche Schätzung von (p, q), die alle Kanäle gleichzeitig erklärt. Kostenfunktion gewichtet Kanal-Residuen mit ihrem jeweiligen Rauschen.

- **Identifizierbarkeit prüfen. **Welche Parameter sind aus welchen Kanälen überhaupt eindeutig bestimmbar? Sensitivitätsanalyse / Fisher-Information. Entartete Richtungen markieren.

**offen: **Punkt 3: Entscheiden, ob Least-Squares reicht oder ob die Artefakt-Korrelation eine volle Bayessche Behandlung mit Priors auf q erzwingt. Hängt von der Identifizierbarkeit aus Punkt 4 ab, also evtl. iterativ.

## 4.1 Trennung S von C — der Kern

Die eigentliche Schwierigkeit: S (intendiert) und C (Artefakt) können ähnliche Kraftsignaturen erzeugen. Drei Unterscheidungshebel:

- Phasenstarrheit: S ist starr an die Anregungsphase gekoppelt; ein Großteil von C (Drift, Temperatur) ist es nicht. Phasenselektive Mittelung trennt beide.

- Bewegungskorrelation: S korrespondiert mit der gemessenen Kinematik (Wegkanal); reine Aktor-Artefakte oft nicht.

- Off-State-Referenz: Der Referenzkanal liefert C ohne S — direkte Subtraktionsbasis.

**offen: **Prüfen, ob die Phasenstarrheit als Trennkriterium ausreicht, wenn ein Teil von C (tangentiale Strukturkopplung) selbst phasenkorreliert ist. Verdacht: das ist der harte Fall. Gegentest mit gezielt phasenkorreliertem C in der Simulation.

# 5. Anschluss an die Detektionsschwelle

Aus dem Mehrkanal-Baustein übernommen, hier als Designgröße der Inversion:

*eps_phys ungefähr sigma_kanal / Wurzel(N) · eta_strategie*

mit Eigenrauschen des limitierenden Kanals *sigma_kanal*, Zahl kohärent gemittelter Zyklen N und Strategie-Effizienz *eta_strategie* (typisch 0,1 bis 1,0). Die Inversionsstrategie bestimmt eta direkt: ein gut konditionierter Schätzer mit sauberer Identifizierbarkeit hebt eta, eine entartete Parametrierung senkt es. Das verknüpft Abschnitt 4 quantitativ mit der erreichbaren Schwelle.

**offen: **eta_strategie ist derzeit ein Platzhalter. Ziel: eta aus der Fisher-Information des Schätzers (Punkt 4.4) ableiten statt zu raten. Das wäre ein eigenständiger, publikationsfähiger Beitrag.

# 6. Testplan (numerisch, vor jeder Hardware)

Konkrete nächste Rechenschritte, alle rein simulativ und vollständig im Wellenform-Rahmen:

| **Test** | **Frage** | **Erwartung** |
| --- | --- | --- |
| T-A Closed Loop | Wird (p, q) aus synthetischen Kanälen wiedergefunden? | Recovery im Rauschlimit |
| T-B S/C-Trennung | Trennt Phasen- + Bewegungskriterium S von C? | saubere Trennung außer bei phasenkorr. C |
| T-C Identifizierbarkeit | Welche Parameter sind entartet? | Liste entarteter Richtungen |
| T-D eta-Ableitung | Folgt eta aus Fisher-Information? | eta als Funktion von N, Kanalsatz |
| T-E Robustheit | Wie empfindlich gegen Modellfehler in E(·)? | Bias-Quantifizierung |

Reihenfolge: T-A zuerst (validiert die ganze Kette), dann T-B (der wissenschaftlich interessanteste Teil), Rest nach Bedarf.

# 7. Offene Fragen / Parkplatz

Sammelstelle für Gedanken, die noch keinen Platz haben — wird laufend ergänzt.

- Reicht ein gemeinsames (p, q) für alle Module, oder braucht jedes Modul eigene Artefaktparameter? (Vermutlich modulindividuell für q, gemeinsam für Profilform.)

- Wie viele Module N sind für die Inversion günstig — mehr Module = mehr Mittelung, aber auch mehr Parameter. Optimum?

- Verbindung zu Baustein 13: Die langsame Schicht Theta(t) ist ein weiterer zu schätzender Freiheitsgrad. Erst später einbauen, sonst zu hochdimensional.

- Lässt sich die Lateralbilanz (Baustein 13, Abschnitt 4) als zusätzliche Constraint in die Schätzung einbringen? Könnte Identifizierbarkeit verbessern.

**Arbeitsstand. **Das Vorwärtsmodell (Abschnitt 1) und die Messseite (Abschnitt 3) stehen. Das inverse Problem (Abschnitt 2, 4) ist die eigentliche neue Arbeit und noch unerprobt. Nächster Schritt ist Test T-A: die geschlossene Schleife aus synthetischen Kanälen, um den Schätzer überhaupt zu validieren. Erst danach lohnt sich T-B, der den wissenschaftlichen Kern (Trennung S von C) prüft.

PCMMS · Arbeitspapier Ringstruktur/Inversion · intern · Gravidon Systemics Research · 2026 · Seite