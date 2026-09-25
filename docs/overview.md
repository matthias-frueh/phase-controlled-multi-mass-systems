# Wegweiser durch die Dokumente

Stand: 25. September 2026. Diese Datei ersetzt die Übersicht vom April 2026.

Lizenz dieses Ordners: CC BY 4.0, siehe [`../LICENSE-CC-BY-4.0`](../LICENSE-CC-BY-4.0). Namensnennung: „Matthias Früh, PCMMS“, https://github.com/matthias-frueh/phase-controlled-multi-mass-systems

## Lesereihenfolge

1. `was_ist_pcmms.md` — worum es geht, ohne Vorwissen.
2. `werkstattbericht.md` — der fachliche Stand: warum die Wellenform und nicht der Mittelwert untersucht wird.
3. `expose_2026-09.md` — Kernfrage, Stand der Simulation, das messbare Signal, nächster Schritt.
4. `praeregistrierung_2026-06.md` — Hypothesen, Falsifikationskriterien, Abbruchregeln (Juni 2026).
5. `literaturabgleich_2026-09-12.md` — wo PCMMS in der Ratchet-, Tribologie- und Kontaktdynamik-Literatur steht.
6. `neuheitsgrad.md`, `einordnung.md`, `zehn_fragen.md` — Abgrenzung und Antworten auf die üblichen Einwände.
7. `archiv_vermerk_kernhypothese_v3.md` — der dokumentierte Rückzug der früheren Hypothese.

## Verbindliche Begriffe

- **⟨N⟩ = M·g** ist Erhaltungssatz; ⟨N⟩ wird in jedem Lauf bestimmt, aber als Kontrollgröße, nicht als
  Zielgröße und nicht als Ergebnis.
- **Kraftverschiebung statt Kraft:** Ausgewertet wird primär die Abweichung gegen die Referenz M·g
  (Erwartungswert null), nicht der Absolutwert.
- **Zielgrößen** sind Wellenform-Observablen: in der Simulation Schiefe γ₁, Liftoff-Anteil λ,
  Asymmetrieverhältnis A = (F_max − M·g)/(M·g − F_min), Minimalkraft F_min. Für die Messkampagne sind
  nach dem [Entwurf der Präregistrierung v2](praeregistrierung_v2_entwurf.md) F_min − ⟨N⟩ und die
  Harmonischen N₁ … N₃ primär, γ₁ sekundär, A beschreibend und λ explorativ.
- **Linie A** (ruhender Körper, Wellenformstatistik) ist die primäre Linie; **Linie B** (Bewegung durch
  Mediumkopplung) ist optional und hier nicht abgelegt.

## Hinweise zu einzelnen Dateien

- Die **Präregistrierung** ist unverändert vom Juni 2026 und wird nicht nachträglich editiert. Sie
  nennt als dritte Observable das „Spitzen-zu-Mittel-Verhältnis“; in Engine, Daten und allen
  September-Dokumenten ist diese Größe als Asymmetrieverhältnis A definiert (Codevariable `peak_ratio`).
  Eine v2 mit Änderungsvermerk liegt als [Entwurf](praeregistrierung_v2_entwurf.md) vor (nicht eingefroren,
  nicht registriert).
- Der **Literaturabgleich** ist ein Arbeitsdokument für die nächste Fassung des Forschungsrahmens (v3.6);
  die dort genannte Fassung v3.5 ist noch nicht im Repository abgelegt, weil sie vor der Umstellung auf
  Linie A als primäre Linie entstand.
- Das **Exposé** und die Kurznotizen beziehen alle Zahlen auf den Parametersatz der Engine
  (`../data/README.md`). Die Auslegung eines physischen Aufbaus ist davon getrennt und offen.
- Alle Zahlen in den Dokumenten sind Simulationsergebnisse. Messdaten existieren nicht.

## Was nicht im Repository liegt

Arbeitsstände in Bearbeitung (Forschungsrahmen v3.6, Symbolverzeichnis, Arbeitspapier), Linie-B-Skripte
und -Notizen, Labor- und Messtechnikplanung. Sie folgen, sobald sie den Stand der abgelegten Dokumente
erreicht haben.
