# ARCHIV-Vermerk — Kernhypothese v3 ist überholt

**Stand: 30.07.2026 · Matthias Früh · ORCID 0009-0005-9984-4207**

**Betrifft:** `PCMMS_Kernhypothese_v3_Frueh_2026` und `PCMMS_Kernhypothese_v3_konsolidiert_Frueh_2026` (Mai 2026); sinngemäß auch die Ergebnis-Bausteine 9–12 (v3a–v3d) sowie den laut Code-INVENTAR quarantänisierten Code (`pcmms_v3a_kontaktmodell.py` u. a.).

## Kernfehler

Die Dokumente erklären ΔF̄ ≠ 0 bei unterbrechbarem (unilateralem) Kontakt für „physikalisch offen". Das ist falsch. Für **beschränkte periodische Bewegung** gilt ⟨F_Kontakt⟩ = M·g **auch mit Liftoff**: Der Schwerpunktsatz mittelt Σ mₖ·z̈ₖ über die Periode zu null; die Kontakt-Nichtlinearität verlagert Information ausschließlich in die **Form** der Kraft (höhere Spitzen kompensieren die Nullphasen), nicht in ihr Zeitmittel.

## Belege

1. **Fremdliteratur:** Perret-Liaudet & Rigaud 2003 (*J. Sound Vib.* 265; arXiv:physics/0701033) — ⟨N⟩ = mg experimentell bestätigt bei bis zu 15 % Kontaktverlust; Wakou, Ochiai & Isobe 2008, arXiv:0801.4428 (Schwerpunktsatz am Vielkontakt). Vgl. `Werkzeug_Literaturanker_Wellenformstatistik`.
2. **Eigene saubere Engine** (`pcmms_v3a_phasen_sweep.py`, unilateraler Kontakt, T1-konform): 19×19-Sweep, Median der ⟨F⟩-Schätzer = M·g = 6,3765 N. **Konvergenztest 30.07.2026:** schlechteste Konfiguration (φ₂ = 0°, φ₃ = 208,4°, Liftoff 74 %) zeigt bei 10 s Auswertefenster −43,5 mN scheinbare Abweichung, bei 50 s noch −0,5 mN, bei 110 s −0,5 mN; zweites Extrem (φ₂ = 246,3°, φ₃ = 37,9°): +6,7 mN → −1,4 mN. **Endlich-Fenster-Effekt, kein physikalischer Shift.** Die Wellenform-Observablen (Schiefe 1,672 → 1,658) bleiben dabei stabil.
3. Die früheren ΔF̄-Werte (−0,037 N u. ä.) stammen aus vorgeschriebenem δ = −m·a/K — Kontaktmodell-Artefakt (INVENTAR: Quarantäne, Test T1 ✗).

## Gültiger Nachfolger

`PCMMS_Forschungsrahmen_v3_5` + `PCMMS_Praeregistrierung`: Wellenform-Statistik (Schiefe, Liftoff-Anteil, Peak-to-Mean) als primäre, erhaltungssichere Observable; gerichtete Nettobewegung nur mit **externem Reaktionspartner** (Medium, Strang b).

## Maßnahme

- Beide Kernhypothese-Dateien mit Präfix `ARCHIV_` versehen bzw. diesen Vermerk als Deckblatt voranstellen; in neuen Texten **nicht mehr zitieren**.
- Hinweis Dateihygiene: Beide Dateien (und weitere „.docx" im Projekt, u. a. Playbooks und Warnung) sind Klartext mit falscher Endung — bei Gelegenheit in `.md` umbenennen, sonst scheitert das Öffnen in Word.
