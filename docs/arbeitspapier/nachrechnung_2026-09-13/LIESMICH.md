# Nachrechnung vom 13.09.2026 (adaptiver Burn-in)

Belegdateien für die Korrektur in Arbeitspapier v2.3 (Abschnitt 9.4, Tabelle 9.4, Anhänge A.1, A.4, B.4). Spaltenbedeutung im Formelverzeichnis v2.6, Anhang B.2.

- `sweep_19x19_burnin_2026-09-13.csv` – 361 Konfigurationen mit Randterm (`R_ppm` = 10⁶·δ_w), Quadratur (`Q_ppm` = 10⁶·δ_Q), Residuum (`delta_ppm` = 10⁶·δ), Burn-in-Zeit, erkannter Periode und den Archivwerten (`arch_*`) zum Vergleich.
- `PCMMS_Klassifikation_100s_2026-09-13.csv` – 100-s-Folgeläufe an 26 Punkten (Periode, Stationarität).
- `pcmms_sweep_burnin_2026-09-13.py`, `pcmms_folgelaeufe_2026-09-13.py` – erzeugende Skripte. Gegenüber dem Original sind nur die Pfade angepasst: Die Engine wird aus `code/pcmms_v3a_phasen_sweep.py` dieses Repositorys geladen, Ausgaben landen in diesem Ordner.
- `PCMMS_Ergebnisnotiz_Sweep_Burnin_2026-09-13_v2.txt` – Ergebnisnotiz mit Verfahren, Kernzahlen und Deutung. Sie verwendet noch R und Q für δ_w und δ_Q.

Rechenzeit des Sweeps etwa 9 min auf einem Kern (laut Ergebnisnotiz).

Lizenz wie im übrigen Repository: die beiden Skripte unter MIT, Daten und Texte unter CC BY 4.0.
