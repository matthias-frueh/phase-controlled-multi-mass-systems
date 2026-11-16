# Sinus-Sweep und Steifigkeitsreihe: Skripte vom 05.09.2026

Erzeugende Skripte zu Arbeitspapier v2.5, Abschnitt 9.7 mit Anhang A.2 (Sweep mit sinusförmigem Bahnprofil, Datensatz [`data/sweep_7x7_sinus.csv`](../../../data/sweep_7x7_sinus.csv)) und Abschnitt 9.8, Tabelle 9.8 (Kontaktsteifigkeit). Am 16.11.2026 nachgetragen. Nur Simulation, keine Messdaten.

## Herkunft

Die Skripte `a_sin.py`, `sinsweep.py` und `sens.py` stammen aus der Arbeit vom 05.09.2026 ([Offene Punkte](../PCMMS_Arbeitspapier_Offene_Punkte.md), Punkte 1 und 2). Sie waren bis zum 16.11.2026 nicht als Dateien abgelegt und sind aus dem Protokoll der Chat-Sitzung jenes Tages übernommen; das Protokoll liegt nicht im Repository. Gegenüber dem Protokoll ist je Skript eine Zeile angepasst (die Engine wird aus [`code/pcmms_v3a_phasen_sweep.py`](../../../code/pcmms_v3a_phasen_sweep.py) geladen statt aus einer Kopie `engine.py` im Arbeitsordner) und ein Kopfkommentar ergänzt. `a_sin.py` war im Protokoll eine Eingabe ohne Dateinamen; der Name ist am 16.11.2026 vergeben.

## Dateien

- `a_sin.py` – Sinusamplitude gleichen Hubs: integriert die Beschleunigung des Egg-Profils zweimal numerisch über einen Zyklus (Summen mit Δt = 50 µs) und schreibt den halben Hub Spitze-Spitze nach `A_sin.txt`.
- `A_sin.txt` – die Amplitude, A = 0,0038461573223484992 m. Das sind 3,48 nm mehr als der analytische halbe Hub (RTOP + RBOT)/2 (relativ 9,0·10⁻⁷).
- `sinsweep.py` – 7×7-Sweep mit Sinusprofil. Übernimmt die Parameter aus der Engine, rechnet mit eigener RK4-Schleife (Schritt, Start und Auswertefenster wie dort), liest die Amplitude aus `A_sin.txt` und schreibt `sweep_7x7_sinus.csv` in diesen Ordner.
- `sens.py` – 7×7-Sweep mit Egg-Profil für fünf Steifigkeiten bei festem Dämpfungsgrad ζ = 16/(2·√(10⁴·M)) = 0,0992, C = 2·ζ·√(k·M). Übernimmt Parameter und Profil aus der Engine; eigene RK4-Schleife mit k und C als Argumenten. Schreibt je Steifigkeit eine Datei `sens_k_*.csv`, danach vier Raster mit anderem Dämpfungsgrad bei k = 10⁴ N/m (`sens_z_*.csv`) und die Übersicht `sensitivitaet.csv`.
- `sens_k_1e+03_0.10.csv`, `sens_k_3e+03_0.10.csv`, `sens_k_1e+04_0.10.csv`, `sens_k_3e+04_0.10.csv`, `sens_k_1e+05_0.10.csv` – die fünf Raster zu Tabelle 9.8, je 49 Zeilen. **Am 16.11.2026 mit `sens.py` neu erzeugt; die Dateien vom 05.09.2026 liegen nicht vor.** Der Dateiname nennt die Steifigkeit in N/m und den gerundeten Dämpfungsgrad. Spalten wie in [`data/README.md`](../../../data/README.md) beschrieben (`phi2`, `phi3`, `F_mean`, `F_skew`, `liftoff`, `F_max`, `F_min`), dazu `dmin`: kleinster Phasenabstand zweier Module in Grad (0: ein Paar läuft gleichphasig).
- `pruefung_2026-11-16.py` – Prüfung vom 16.11.2026, Abschnitte A bis D. Neu geschrieben, nicht aus dem Protokoll. Lädt die drei Skripte unverändert und überschreibt keine Datei des Repositorys.
- `pruefung_2026-11-16_ausgabe.txt` – vollständige Ausgabe mit `--voll` in der Umgebung, in der die Raster erzeugt sind: Python 3.13.18, numpy 2.5.3, scipy 1.17.1, pandas 2.2.3 (Linux x86-64, glibc 2.39).
- `pruefung_2026-11-16_ausgabe_ci_versionen.txt` – dasselbe auf demselben Rechner mit den Paketversionen des automatischen Testlaufs ([`.github/constraints-ci.txt`](../../../.github/constraints-ci.txt)): numpy 2.5.4, scipy 1.18.1, pandas 3.1.1.

## Aufruf

`a_sin.py`, `sinsweep.py` und `sens.py` erwarten diesen Ordner als Arbeitsverzeichnis; die Prüfung läuft aus jedem Verzeichnis.

```sh
cd docs/arbeitspapier/sinus_sensitivitaet_2026-09-05
python3 a_sin.py                        # etwa 1 s; schreibt A_sin.txt neu
python3 sinsweep.py                     # etwa 35 s; schreibt sweep_7x7_sinus.csv in diesen Ordner
python3 sens.py                         # etwa 9 min (neun Raster, je etwa 1 min)
python3 pruefung_2026-11-16.py          # etwa 1 min
python3 pruefung_2026-11-16.py --voll   # etwa 6 min
```

Benötigt numpy, scipy und pandas. `sens.py` überschreibt die fünf abgelegten Raster. `sweep_7x7_sinus.csv`, `sens_z_*.csv` und `sensitivitaet.csv` in diesem Ordner sind Laufartefakte (`.gitignore`); der Datensatz des Sinus-Sweeps liegt in `data/`.

## Ergebnis der Prüfung

Wortlaut in den beiden Ausgaben; beide enden mit „Ergebnis: bestanden“.

- **A, Amplitude.** `a_sin.py` liefert die Zeichenfolge in `A_sin.txt`.
- **B, Sinus-Sweep.** In der Umgebung der ersten Ausgabe entsteht `data/sweep_7x7_sinus.csv` bytegleich neu (SHA-256 `bd6b33af5547759cc2dfd32ad69cb5ca1a5ba3e704ed314e903ebe24294984ee`). Mit den Paketversionen des Testlaufs weicht `F_skew` in 33 der 49 Zeilen in der letzten Stelle ab (höchstens 2,2·10⁻¹⁶); alle anderen Spalten sind bitgleich. Mit (RTOP + RBOT)/2 statt `A_sin.txt` weichen F_max und F_min der 30 liftoff-freien Punkte um 2,2·10⁻⁶ bis 5,6·10⁻⁶ N ab.
- **C, Steifigkeitsreihe.** Die 40 Kennzahlen der Tabelle 9.8 (fünf Steifigkeiten, je acht Werte) folgen aus den fünf Rastern auf die gedruckten Stellen. Neu gerechnet kehren die Raster in der Umgebung der ersten Ausgabe bytegleich wieder; mit den Paketversionen des Testlaufs weicht `F_skew` in 27, 14, 12, 11 und 16 der je 49 Zeilen in der letzten Stelle ab (höchstens 4,4·10⁻¹⁶), alle anderen Spalten sind bitgleich. Mit C = 16 N·s/m liefert die Punktfunktion aus `sens.py` am Punkt (0°, 0°) die Zeile aus [`data/sweep_19x19.csv`](../../../data/sweep_19x19.csv) auf deren sechs Nachkommastellen.
- **D, 2400-s-Tabellen.** Gehört nicht zu den Skripten dieses Ordners: fünf Übereinstimmungen von `data/regime_2400s.csv` und `data/regime_2400s_dt2.csv` mit dem Burn-in-Sweep vom 13.09.2026 ([`../nachrechnung_2026-09-13/`](../nachrechnung_2026-09-13/)). Ein Indiz für die Herkunft dieser Tabellen, kein Nachweis; Wortlaut und Einordnung in [`data/README.md`](../../../data/README.md).

## Grenzen

- Die Raster sind neu erzeugt. Geprüft ist ihre Übereinstimmung mit den gedruckten Kennzahlen der Tabelle 9.8, nicht mit den Dateien vom 05.09.2026.
- Festschritt-RK4 über die Kontaktumschaltung, wie in [`data/README.md`](../../../data/README.md) zu `sweep_19x19.csv` beschrieben: Werte an Punkten mit Liftoff hängen von Startbedingung und Rundung ab. Beispiel: Bei k = 10⁴ N/m rechnet `sens.py` mit C = 2·ζ·√(k·M) = 15,999999999999998 N·s/m. Am gemeinsamen Rasterpunkt (0°, 0°) steht deshalb in `sens_k_1e+04_0.10.csv` F_max = 41,121298 N und λ = 75,7850 %, in `data/sweep_19x19.csv` 41,123260 N und 75,7885 %.
- Bytegleich kehren die Dateien nur in der genannten Umgebung wieder. Zwischen den beiden geprüften Umgebungen unterscheidet sich allein die Spalte `F_skew`, und nur in der letzten Stelle. Andere Rechner sind nicht geprüft.
- Nicht in diesem Ordner: das Skript zur Dämpfungstabelle des Abschnitts 9.8 (Tabelle 9.9, Rechnung an vier Regimepunkten; die vier Dämpfungsraster aus `sens.py` gehören nicht zum Arbeitspapier) und die Erzeuger der Abbildungen 9.5 und 9.6 (`Plots/sinus_kollaps.pdf`, `Plots/sens_k.pdf`).
- Die Prüfung gehört nicht zur Testsuite in `tests/`.

Lizenz wie im übrigen Repository: die Skripte unter MIT, Daten und Texte unter CC BY 4.0.

*Vermerk:* Erstellt am 16.11.2026, Chat-Sitzung (Claude), nach Auftrag des Autors. Fundstellen und Zahlen sind am Repository-Stand `4bcbb3c` geprüft.
