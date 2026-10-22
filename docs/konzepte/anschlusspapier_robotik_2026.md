**PCMMS — Anschlusspapier Robotik**

Nachgelagerte Vergleichs- und Validierungsebene

Matthias Früh · Unabhängige Forschung · ORCID 0009-0005-9984-4207 · Fassung 2026 · Anschlussdokument zu Baustein 14

> **Vermerk (22.10.2026).** Originaldatei `PCMMS_Anschlusspapier_Robotik_Frueh_2026-3.md`, Fassung 2026 ohne
> Tagesdatum; Textfassung der Quelldatei (DOCX) des Autors, hier unverändert bis auf diesen Vermerk (die Fußzeile
> „… · Seite“ am Ende stammt aus der Quelldatei). Anschlussdokument ohne ausgeführte Regelung oder robotische
> Validierung; Messdaten gibt es nicht. Arbeitspaket AP-27 (Räumliche Last, N Module, Regelung, Robotik; Stufe S4,
> Status „später; Konzept des Messrahmens vorgezogen (11.10.2026)“, [`../arbeitsplan_status.md`](../arbeitsplan_status.md)).
> Robotik als nachgelagerte Validierungsebene, nicht als Voraussetzung, führen auch [`../einordnung.md`](../einordnung.md)
> und [`../zehn_fragen.md`](../zehn_fragen.md) (Frage 8). Seit der Fassung überholt oder offen:
> - **Baustein 14:** ist historisch und liegt wie Baustein 13 und „Systemarchitektur und Modulhierarchie“ nicht im
>   Repository. „… ist in Baustein 14 als generativer Mechanismus vollständig spezifiziert“ (Abschnitt 1) ist die
>   Aussage des damaligen Dokuments. Hypothesen, Kontrollen und Entscheidungsregeln stehen heute in der
>   [Präregistrierung v2](../praeregistrierung_v2_entwurf.md) (Entwicklungsversion); Messkette und Kalibrierplan sind
>   offen (AP-06, „noch nicht umgesetzt“).
> - **Kraftkanal (Abschnitt 3):** „Abtastrate ≥ 100 Hz“ ist der Stand von Baustein 14; für die Wellenform verlangt die
>   Präregistrierung v2 bei k_max = 9 und f = 10 Hz etwa f_s ≥ 6,3 kHz ([Anhang A6](../praeregistrierung_v2_anhang.md)).
> - **Ebenen L0–L3 (Abschnitt 2):** Die Rollen beschreibt das [Formelverzeichnis v2.8](../formelverzeichnis/README.md)
>   (Abschnitt „Mehrpunkt-, Mehrinterface- und Mehrkanalmessung“); für keine Ebene existiert ein gebauter Aufbau. Ein
>   Messrahmen mit sechs Messschnittstellen liegt als Konzept vor
>   ([`nadelrahmen_dreimassenkoerper_2026-10.md`](nadelrahmen_dreimassenkoerper_2026-10.md), AP-27).
> - **Kernhypothese v3** (Anschlussdokumente am Ende) ist zurückgezogen; neue Texte zitieren sie nicht mehr
>   ([`../archiv_vermerk_kernhypothese_v3.md`](../archiv_vermerk_kernhypothese_v3.md)).
>
> Lizenz wie der Ordner: CC BY 4.0 ([`../../LICENSE-CC-BY-4.0`](../../LICENSE-CC-BY-4.0)).

# **1  Ausgangslage**

Die PCMMS-Grunddynamik ist in Baustein 14 als generativer Mechanismus vollständig spezifiziert: Zyklusaufbau, Wellenformbibliothek, Phasenkontrolle, Nebenbedingungen, Messkette, Auswertung und Falsifikationskriterium liegen mit Zahlenwerten vor. Dieses Papier regelt ausschließlich, in welchem Verhältnis robotische Systeme dazu stehen.

Die Kausalrichtung ist festgelegt:

PCMMS-Grunddynamik → L2 → L3 → komplexe gekoppelte Dynamik

Robotik → nachgelagerte Vergleichs- und Validierungsebene

Robotische Systeme sind damit weder Quelle noch Vorbild der Modulcharakteristik. Der umgekehrte Weg — Dynamik aus einem bestehenden Manipulator extrahieren und daraus ein PCMMS-Modul ableiten — wird ausdrücklich nicht verfolgt.

# **2  Ebenenzuordnung (Kurzfassung)**

| **Ebene** | **Inhalt** | **Rolle gegenüber der Robotik** |
| --- | --- | --- |
| L0 | passiver Messrahmen, 6-Interface, 12 Sensoren | Referenzsystem; nicht Messobjekt, nicht erstes Modul |
| L1 | aktiver Träger mit eigenen Freiheitsgraden | Analogon zur aktiv geführten Basis; Vergleichspunkt |
| L2 | Module, Egg-Bewegung, Phasenkontrolle | das generative System — Gegenstand jedes Vergleichs |
| L3 | Kopplung L1 ↔ L2, Reaktionskräfte, C(x,t) | offene Ebene; hier entsteht die eigentlich vergleichbare Systemdynamik |

L3 ist die offene Stelle. Ein robotischer Vergleich ist erst sinnvoll, wenn L0 und L2 charakterisiert und die L3-Wechselwirkung formalisiert ist. Vorher vergleicht man ein unvollständig beschriebenes System mit einem vollständig beschriebenen — das erzeugt Scheinbefunde.

# **3  Was ein robotisches Labor beitragen kann**

| **Beitrag** | **Inhalt** |
| --- | --- |
| Primärkanal Kraft | direkte Kraftmessung nach der Spezifikation aus Baustein 14 (Bereich ca. 0–500 N, Auflösung ≤ 0,01 N, Abtastrate ≥ 100 Hz) |
| Sekundärkanal Moment | Gelenkmomente ausschließlich als Sekundärkanal mit dokumentierter Modellabhängigkeit — siehe §4 |
| Positions- und Geschwindigkeitsmessung | hochauflösend, zyklussynchron; Grundlage für Phasenstabilitätsnachweis |
| Bewegungsreferenz | kontrollierter Manipulator als Referenzbewegung mit bekannter Dynamik |
| Phasen- und Zyklusanalyse | Nachweis, dass φ_k über die Laufzeit synchronisiert bleibt |
| Systemidentifikation | nicht um PCMMS zu erzeugen, sondern um zu bestimmen, was PCMMS tatsächlich erzeugt |
| Mehrkörper- und nichtlineare Dynamik | mathematische Beschreibung der gekoppelten Module, insbesondere L3 |

# **4  Vorbehalt zum Momentenkanal**

Ein aus dem Robotercontroller stammendes τ_k(t) ist kein direkt gemessener Kraftkanal. Es wird typischerweise rekonstruiert aus:

τ_geschätzt = f( I, q̇, q̈, Getriebemodell, Reibungsmodell, … )

Die Aussagekraft hängt damit an den Modellannahmen der Rekonstruktion. Für die PCMMS-Primärcharakterisierung ist das nicht ausreichend, weil die gesuchten Größen in derselben Größenordnung liegen können wie der Modellfehler. Regel für alle Anschlussarbeiten: Primärkanal ist die direkte Kraftmessung; Gelenkmomente werden nur als Sekundärkanal geführt und ihre Modellabhängigkeit wird im Protokoll ausgewiesen.

*Dieselbe Regel gilt für Motorstrom als Kraftindikator.*

# **5  Untersuchungsfragen der Anschlussebene**

*Nicht gefragt wird: Wie muss PCMMS konstruiert werden, damit es einen Roboterarm nachbildet?*

Gefragt wird:

- Welche Eigenschaften der durch PCMMS erzeugten Dynamik eignen sich zur technischen Abbildung komplexer Bewegungsstrukturen?

- Wie verhält sich die PCMMS-Dynamik gegenüber einer aktiv geführten Basis (L1)?

- Wie verändern sich Phasenstabilität, Kopplungsverhalten und Wellenformkennzahlen beim Übergang N = 4 → 8 → 20–32?

- Ab welcher Kopplungsstärke randomisieren mechanische Wechselwirkungen die Phasenbeziehungen?

- Lässt sich eine gegebene Zielbewegung mit einer PCMMS-Topologie darstellen, die nicht der eines klassischen seriellen Manipulators entspricht?

Die letzte Frage ist die eigentliche Anschlussfrage. Sie setzt voraus, dass L3 geklärt ist, und ist damit nicht Gegenstand der Erstcharakterisierung.

# **6  Abgrenzung und Reihenfolge**

| **Stufe** | **Inhalt** |
| --- | --- |
| 1 — Baustein 14 | Charakterisierung von L0 und L2 nach spezifizierter Messkette; Baseline, Artefaktkontrollen, Entscheidungsregel |
| 2 — L3 | Formalisierung und Vermessung der Kopplung L1 ↔ L2 einschließlich C(x,t) |
| 3 — dieses Papier | Vergleich der erzeugten Bewegungs- und Kraftstrukturen mit etablierten robotischen Systemen |
| 4 — offen | Abbildung komplexer Bewegungsstrukturen durch modulare PCMMS-Topologien |

Die Stufen sind nicht vertauschbar. Ein Einstieg auf Stufe 3 ohne Stufe 1 würde die Modulcharakteristik nachträglich aus dem Vergleichssystem heraus definieren und damit genau die Kausalrichtung umkehren, die dieses Papier festhält.

Anschlussdokumente: Baustein 14 (Grunddynamik, Spezifikationsblatt) · Systemarchitektur und Modulhierarchie · Baustein 13 (hierarchische Steuerungsarchitektur) · Kernhypothese v3

PCMMS · Anschlusspapier Robotik · M. Früh 2026 · Seite