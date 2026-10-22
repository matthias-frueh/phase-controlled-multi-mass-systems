**PCMMS — Anschlusspapier Robotik**

Nachgelagerte Vergleichs- und Validierungsebene

Matthias Früh · Unabhängige Forschung · ORCID 0009-0005-9984-4207 · Fassung 2026 · Anschlussdokument zu Baustein 14

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