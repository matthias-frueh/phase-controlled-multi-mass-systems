# PCMMS — Anwendungsstrang: Lageregelung (Reaktionsrad-Prinzip)

**Matthias Früh · Gravidon Systemics Research · ORCID 0009-0005-9984-4207**
Stand: 14. Juni 2026

> **Vermerk (22.10.2026).** Originaldatei `PCMMS_Anwendungsstrang_Lageregelung_Frueh_2026.md`, Stand 14.06.2026; hier
> unverändert bis auf diesen Vermerk. Anwendungsdokument; eine Lageregelung mit PCMMS-Modulen ist nicht ausgeführt: Im
> Repository gibt es dazu weder Code noch Rechnung, Messdaten ebenso wenig. Arbeitspaket AP-27 (Räumliche Last,
> N Module, Regelung, Robotik; Stufe S4, Status „später; Konzept des Messrahmens vorgezogen (11.10.2026)“,
> [`../arbeitsplan_status.md`](../arbeitsplan_status.md)). Das Dokument nennt keine Forschungslinie; von den drei
> Strängen der Tabelle in Abschnitt 4 entspricht der Fluid-Schub (1) Linie B, die Interface-Statistik (3) Linie A
> ([`../../README.md`](../../README.md), „Zwei Forschungslinien“). Seit Juni 2026 überholt oder offen:
> - **Simulation (Abschnitt 7):** `pcmms_lageregelung_3achs.py` liegt nicht im Repository; die Gesamtprojektanalyse hat
>   nur ihren Kopf als Quelle außerhalb des Repositorys gelesen
>   ([`../../rechnungen/bewertung_b/PROTOKOLL.md`](../../rechnungen/bewertung_b/PROTOKOLL.md), Abschnitt 1). Sie rechnet
>   nach Abschnitt 7 mit idealem Rad; ein PCMMS-Modul als Stellglied ist dort erst vorgeschlagen.
> - **Strang (1), Vakuum „= 0 (skaliert mit ρ)“:** Mit ρ skaliert im Modell die Kraft (bei festem C_D
>   und fester Bewegung); die stationäre Drift ist nur im quadratischen Widerstandsmodell ohne linearen Anteil
>   dichteunabhängig, mit linearem Zusatzwiderstand unterhalb von ρ* ∝ ρ; bei kleiner Keulegan-Carpenter-Zahl ist auch
>   die Kraftaussage nicht belegt ([`../../rechnungen/linie_b/PROTOKOLL.md`](../../rechnungen/linie_b/PROTOKOLL.md),
>   LB-02, LB-06; [Gegenprüfung LB-06](../../rechnungen/linie_b/verifikation/PROTOKOLL.md)).
> - **Strang (3), Zielgrößen:** Für die Messkampagne sind nach dem Entwurf der Präregistrierung v2 F_min − ⟨N⟩
>   und die Harmonischen 1–3 primär, γ₁ sekundär, A beschreibend und λ explorativ; Spitzen-zu-Mittel-Verhältnis und Asymmetrieverhältnis sind verschiedene
>   Größen ([`../overview.md`](../overview.md)).
>
> Lizenz wie der Ordner: CC BY 4.0 ([`../../LICENSE-CC-BY-4.0`](../../LICENSE-CC-BY-4.0)).

---

## Kurzfassung

Die phasengekoppelte Mehrmassen-Hardware lässt sich als **Drehimpuls-Stellglied** nutzen: die Orientierung eines Starrkörpers steuern, **ohne Außenwirkung** — das Reaktionsrad-Prinzip der Satelliten-Lageregelung. Voll innerhalb der klassischen Mechanik, vakuumgültig, schwerpunkterhaltend. Das ist der defensivste „Wofür ist das gut?"-Strang des Projekts.

## 1. Was es ist

3-Achs-Starrkörper + 3 Reaktionsräder, **Quaternion-Regelung** (`q = (w,x,y,z)`, `|q| = 1`, Neutrallage `(1,0,0,0)`), mit Sättigung. Kommandiert wird die **Orientierung `q(t)`** — eine physikalisch offene, etablierte Größe (Stand der Technik), **nicht** `ΔF̄`.

## 2. Was gilt — und wo die Grenze ist

- **Szenario A (Slew):** Der Körper dreht auf das Zielquaternion und hält. Die Räder geben Drehimpuls ab und kehren zu ~0 zurück. Der Gesamtdrehimpuls `|H|` bleibt erhalten (Start 0), die Schwerpunkt-Translation ist 0.
- **Szenario B (Halten gegen Störmoment):** Die Lage wird gehalten, aber die Räder müssen Drehimpuls *aufladen* → die Radrate rampt linear bis zur **Sättigung**. Danach geht nichts mehr ohne externes Moment.
- **Ehrliche Grenze:** Inneres Tauschen verteilt Drehimpuls nur **um**. Das *Ändern* des Gesamt-`H` braucht ein Außen (Desaturation per externem Moment — Magnetorquer, Düsen o. Ä.). Genau hier ist die Trennlinie zwischen „legitim" und „unmöglich".

## 3. Bezug zur PCMMS-Hardware

Es ist **dasselbe Werkzeug** — phasengekoppelte Oszillation, Egg-Modulation, adaptive Steuerung —, nur auf eine physikalisch offene Frage gerichtet: Orientierung statt Netto-Kraft. Die Module liefern die Stell-Drehmomente; das Sättigungsverhalten und die nichtlineare Stellglied-Dynamik sind der eigentliche technische Inhalt.

## 4. Einordnung in die drei legitimen Stränge

| Strang | Zielgröße | Reaktionspartner | Vakuum |
|--------|-----------|------------------|--------|
| (1) Fluid-Schub | Netto-Drift des Schwerpunkts | verdrängtes Medium | = 0 (skaliert mit ρ) |
| **(2) Lageregelung** | **Orientierung `q(t)`** | **keiner nötig (intern)** | **gültig** |
| (3) Interface-Statistik | Schiefe / Liftoff / Peak-to-Mean | Auflager | gültig (`⟨N⟩ = Mg` fixiert) |

Die Lageregelung ist der einzige Strang ohne Mediumannahme: vakuumgültig, und der Schwerpunkt bewegt sich nie.

## 5. Abgrenzung

Kein reactionless drive, keine Translation des Schwerpunkts, keine Gewichtsänderung. Reine Umverteilung von Drehimpuls im geschlossenen System — lehrbuchkonform (Satelliten-ADCS).

## 6. Andockpunkte

- **Woschke / Mehrkörperdynamik:** Reaktionsrad + Sättigung + nichtlineare Stellglied-Dynamik ist MKS-Territorium.
- **Aerospace / Kleinsatelliten (CubeSat-ADCS):** direkter Anwendungskontext für die Methodik.

## 7. Status & nächste Schritte

- **Vorhanden:** laufende Simulation `pcmms_lageregelung_3achs.py` (Szenario A + B, `|H|`-Erhaltung, Sättigung).
- **Vorschlag nächste Schritte:**
  1. Desaturations-Strategie ergänzen (externes Moment, Modellierung).
  2. PCMMS-Modul als *reales* Stellglied modellieren statt idealem Rad.
  3. Regelgüte und Sättigungsgrenzen quantifizieren (Slew-Zeit, Haltedauer vs. Störmoment).
