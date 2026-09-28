# Gegenprobe vom 26.09.2026 (Einzelmodul, Vorzeichen der Schiefe)

Belegdateien für die Korrektur in Arbeitspapier v2.4 (Abschnitte 4.8, 5.5, 9.7, 9.8, 12.2, 12.4, Anhänge A.5, B.3, B.6). Nur Simulation, keine Messdaten.

- `pcmms_gegenprobe_einzelmodul_2026-09-26.py` – Einzelmodul im Dauerkontakt über 3f/f_n mit den Nullstellen der Schiefe, Amplitudensweep eines Moduls durch den Liftoff-Bereich (Tabelle 4.1), Zweiergruppen-Linie bei k = 6 944 N/m mit halbiertem Zeitschritt, Triadenzerlegung (Gleichung 4.15) und Abgleich mit `data/sweep_19x19.csv`. Linearer Kontaktast im Frequenzbereich und RK4 mit denselben Parametern wie `code/pcmms_v3a_phasen_sweep.py`, eigene Nachbildung ohne Import.
- `pcmms_gegenprobe_einzelmodul_2026-09-26_ausgabe.txt` – vollständige Ausgabe, Abschnitte A–F.
- `pcmms_pruefung_pr4_linearloeser.py`, `pcmms_pruefung_pr4_linearloeser_ausgabe.txt` – unabhängige Prüfung zu PR #4 (`code/linear_solver.py`) vom 25.09.2026. Daraus stammen die übernommenen Werte zu Zeltsekanten, liftoff-freiem Anteil, Abheben des Triphasik-Punkts und den bistabilen Inseln.

Aufruf aus der Repo-Wurzel:

```sh
python3 docs/arbeitspapier/gegenprobe_2026-09-26/pcmms_gegenprobe_einzelmodul_2026-09-26.py
python3 docs/arbeitspapier/gegenprobe_2026-09-26/pcmms_pruefung_pr4_linearloeser.py
```

Laufzeit etwa 3 min bzw. unter 1 min. Benötigt numpy, dazu pandas (Abschnitt F der Gegenprobe) und scipy (Prüfung zu PR #4). Beide Ausgaben sind mit den beiliegenden Skripten reproduziert.

Lizenz wie im übrigen Repository: die Skripte unter MIT, Daten und Texte unter CC BY 4.0.
