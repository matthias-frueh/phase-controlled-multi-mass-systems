# Wegweiser durch die Dokumente

Stand: 25. September 2026, Nachträge 2., 4., 11., 16., 22., 29. und 31. Oktober 2026. Diese Datei ersetzt die Übersicht vom April 2026.

Lizenz dieses Ordners: CC BY 4.0, siehe [`../LICENSE-CC-BY-4.0`](../LICENSE-CC-BY-4.0). Namensnennung: „Matthias Früh, PCMMS“, https://github.com/matthias-frueh/phase-controlled-multi-mass-systems

## Lesereihenfolge

1. `was_ist_pcmms.md` — worum es geht, ohne Vorwissen.
2. `werkstattbericht.md` — der fachliche Stand: warum die Wellenform und nicht der Mittelwert untersucht wird.
3. `expose_2026-09.md` — Kernfrage, Stand der Simulation, das messbare Signal, nächster Schritt.
4. `praeregistrierung_2026-06.md` — Hypothesen, Falsifikationskriterien, Abbruchregeln (Juni 2026).
5. `literaturabgleich_2026-09-12.md` — wo PCMMS in der Ratchet-, Tribologie- und Kontaktdynamik-Literatur steht.
6. `neuheitsgrad.md`, `einordnung.md`, `zehn_fragen.md` — Abgrenzung und Antworten auf die üblichen Einwände.
7. `archiv_vermerk_kernhypothese_v3.md` — der dokumentierte Rückzug der früheren Hypothese.
8. [`../rechnungen/README.md`](../rechnungen/README.md) — Rechen- und Prüfskripte der Gesamtprojektanalyse
   10/2026 mit Ergebnissen und Protokollen (Simulation und Analytik, Stand 02.10.2026).
9. [`konzepte/README.md`](konzepte/README.md) — Konzepte zu Laboraufbau, Messtechnik und Steuerung (Mai bis
   Oktober 2026, darunter der Sechs-Nadel-Messrahmen mit eingebettetem Dreimassenkörper), als Konzepte
   gekennzeichnet; dazu die Demonstrator-Unterlagen der Linie B, Anwendungs- und Anschlusspapiere (Lageregelung,
   Robotik), eine Notiz zu Linie C und seit 29.10.2026 die Anforderungsspezifikation einer dualen Armführung der
   inneren Massen (Entwurf v0.4, Konzept ohne Bau- oder Antriebsentscheidung), seit 31.10.2026 außerdem die
   Konzeptentwürfe zur Massenkonzentration auf die bewegten Hauptmassen (Auslegungsbegleitung für verschiedene
   Konstruktionsmodelle, Zielanteile offen) und zur schwerkraftbezogenen Messung mit lageadaptiver Bewegungsführung
   (Mess- und Führungsoption, nicht ausgeführt). Firmware-Muster in
   [`../code/firmware/`](../code/firmware/), Auswerteskripte des Demonstrators in
   [`../code/demonstrator/`](../code/demonstrator/README.md).
10. [`plan_ap13_pipelinetest.md`](plan_ap13_pipelinetest.md) — Plan des Pipelinetests (Werkzeug 8 der Präregistrierung v2);
    Plan, nicht umgesetzt.
11. [`arbeitsplan_status.md`](arbeitsplan_status.md) — Bearbeitungsstand der Arbeitspakete AP-01 bis AP-30 und offene
    Entscheidungen des Autors.
12. [`linie_b/README.md`](linie_b/README.md) — Unterlagen der optionalen Linie B (Forschungsrahmen v3.5,
    Richtungsnotiz v5.2, Skriptkorrekturen, Leitfaden der Skriptprüfung, Prüfarchitektur), je mit Vermerk zum
    heutigen Stand; Stufe S5, später. Seit 29.10.2026 dazu der Abgrenzungsentwurf für den Forschungsrahmen v3.6
    (Entwurf 3): zwei B-Fassungen gegenübergestellt, Teilung B1/B2 als Vorschlag, Entscheidung D-2 des Autors offen.
13. [`abgleichnotiz_2026-10-29_v4.md`](abgleichnotiz_2026-10-29_v4.md) — Sitzungs- und Entscheidungsnotiz vom
    29.10.2026: Abgrenzung der Linien A/B/C durch den Autor, Abgleich mit dem Projektstand, Entscheidung D-1
    (Stufenfolge bleibt, B2 nur als Randbedingung für AP-01, AP-04, AP-06), offene Entscheidungen D-2 bis D-6,
    Prüfvermerke und Korrekturen.

**Zurückgezogen** sind frühere Aussagen zu einer Mittelwertverschiebung (Ursache: Kontaktmodell mit
vorgeschriebener Eindrückung; Archiv-Vermerk), zu einer gerichteten Netto-Impulsübertragung ohne äußeren
Partner (vgl. Archiv-Vermerk, Abschnitt „Gültiger Nachfolger“) und zu einer allgemeinen Vorzeichenregel der
Schiefe (Arbeitspapier v2.4, Abschnitt 4.8).

## Verbindliche Begriffe

- **⟨N⟩ = M·g** ist Erhaltungssatz; ⟨N⟩ wird in jedem Lauf bestimmt, aber als Kontrollgröße, nicht als
  Zielgröße und nicht als Ergebnis.
- **Kraftverschiebung statt Kraft:** Ausgewertet wird primär die Abweichung gegen die Referenz M·g
  (Erwartungswert null), nicht der Absolutwert.
- **Zielgrößen** sind Wellenform-Observablen: in der Simulation Schiefe γ₁, Liftoff-Anteil λ,
  Asymmetrieverhältnis A = (F_max − M·g)/(M·g − F_min), Minimalkraft F_min. Für die Messkampagne sind
  nach dem [Entwurf der Präregistrierung v2](praeregistrierung_v2_entwurf.md) F_min − ⟨N⟩ und die
  Harmonischen 1–3 der Kontaktkraft N(t) primär, γ₁ sekundär, A beschreibend und λ explorativ.
- **Linie A** (ruhender Körper, Wellenformstatistik) ist die primäre Linie; **Linie B** (Bewegung durch
  Mediumkopplung) ist optional; ihre Unterlagen liegen gekennzeichnet in [`linie_b/`](linie_b/README.md).

## Hinweise zu einzelnen Dateien

- Die **Präregistrierung** ist unverändert vom Juni 2026 und wird nicht nachträglich editiert. Sie
  nennt als dritte Observable das „Spitzen-zu-Mittel-Verhältnis“ (Peak-to-Mean, im Formelverzeichnis
  Π_N = F_max/⟨F⟩). Engine, Daten und die September-Dokumente verwenden stattdessen das
  Asymmetrieverhältnis A = (F_max − M·g)/(M·g − F_min); die Codevariable `peak_ratio` berechnet A, nicht Π_N.
  Spitzen-zu-Mittel-Verhältnis (Π_N) einerseits und Asymmetrieverhältnis A (`peak_ratio`) andererseits
  sind also zwei verschiedene Größen.
  Eine v2 mit Änderungsvermerk liegt als [Entwurf](praeregistrierung_v2_entwurf.md) vor (nicht eingefroren,
  nicht registriert).
- Das **Arbeitspapier** v2.5 liegt in [`arbeitspapier/`](arbeitspapier/) (die Skripte der Nachrechnung und der Gegenprobe dort
  unter MIT), das **Symbol- und Formelverzeichnis** in der Fassung v2.8 in
  [`formelverzeichnis/`](formelverzeichnis/). Die PDFs vom 16.10.2026 enthalten die Nachträge vom Oktober 2026; PDF
  und Quelltext stimmen überein (Bauanleitung in den README-Dateien beider Ordner).
- Der **Literaturabgleich** ist ein Arbeitsdokument für die nächste Fassung des Forschungsrahmens (v3.6);
  die dort genannte Fassung v3.5 liegt seit 22.10.2026 mit Vermerk in
  [`linie_b/forschungsrahmen_v3_5_2026-05.md`](linie_b/forschungsrahmen_v3_5_2026-05.md); sie entstand vor der
  Umstellung auf Linie A als primäre Linie.
- Die **Regimeanalyse** v1.2 ([`regimeanalyse_v1_2_2026-09-28.md`](regimeanalyse_v1_2_2026-09-28.md)) ist eine interne
  numerische Prüfnotiz vom 28.09.2026 zu Langläufen der Engine; ihr Vermerk nennt, was seither erledigt und was offen
  ist.
- Das **Exposé** und die Kurznotizen beziehen alle Zahlen auf den Parametersatz der Engine
  (`../data/README.md`). Dieser Referenzsatz hat einen weichen Kontakt (K = 10⁴ N/m); Leitzahlen wie
  5,33 N, Zeltsteilheit und positive Schiefe am Triphasik-Punkt sind dessen Effekte und keine Vorhersagen für
  einen Aufbau. Die Auslegung eines physischen Aufbaus ist davon getrennt und offen; die offenen
  Entscheidungen des Autors stehen im Exposé, Abschnitt „Nächster Schritt“.
- Alle Zahlen in den Dokumenten sind Simulationsergebnisse. Messdaten existieren nicht.

## Was nicht im Repository liegt

Der Forschungsrahmen v3.6 ist vorgesehen (AP-28, Status „später“) und liegt nicht vor; ein Abgrenzungsentwurf dazu (29.10.2026) liegt in [`linie_b/`](linie_b/README.md). Die Notiz „Trennungsbedingungen“ des Autors zur Linie C (v4, 28./29.10.2026) liegt nicht im Repository. Die Linie-B-Notizen liegen seit 22.10.2026 in
[`linie_b/`](linie_b/README.md), die Linie-B-Modelle v2 und ihre Kontrollrechnungen in
[`../rechnungen/linie_b/`](../rechnungen/linie_b/). Die Labor- und Messtechnikplanung liegt
als Konzeptsammlung in [`konzepte/`](konzepte/) (Stand Mai bis Oktober 2026); die Planung von Räumen, Personal und
Kosten ist nicht Gegenstand des Repositorys.

Außerhalb des Repositorys kursierende ältere Fassungen sind überholt: das Arbeitsmanuskript v2.1 (früher
als Dissertation geführt), die Exposés vom Mai und Juli 2026, ältere Präsentationen, FAQ und Kurzpapiere.
Sie enthalten teils zurückgezogene Aussagen. Maßgeblich sind die Fassungen in diesem Repository.
