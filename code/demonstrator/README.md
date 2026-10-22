# Auswerteskripte des Demonstrators (Linie B)

Stand der Skripte: 2026, zu den Demonstrator-Unterlagen vom Mai 2026; übernommen am 22. Oktober 2026, unverändert.
Lizenz: MIT wie der übrige Code ([`../../LICENSE`](../../LICENSE)).

Die drei Python-Skripte sind die Tracking- und Auswertewerkzeuge des Ballon-Demonstrators und des Pendeltests der
**Linie B** (frei bewegter Körper im Medium, Impuls an die Luft; [`../../docs/einordnung.md`](../../docs/einordnung.md),
Abschnitt 3, „Linie B“). Sie gehören nicht zu Linie A; die [Präregistrierung v2](../../docs/praeregistrierung_v2_entwurf.md)
behandelt Linie B nicht (§11). Im Arbeitsplan liegt Linie B in Stufe S5 (geparkt), AP-28, Status „später“
([`../../docs/arbeitsplan_status.md`](../../docs/arbeitsplan_status.md)). Gemessen wird eine Lage oder Höhe und daraus
eine Drift, keine Kraft. **Mit keinem der Skripte wurden Messdaten des Projekts erzeugt; Messdaten existieren nicht.**
Bei der Übernahme wurden die Skripte weder ausgeführt noch getestet; Tests in [`../../tests/`](../../tests/) gibt es
für sie nicht.

Zugehörige Unterlagen in [`../../docs/konzepte/`](../../docs/konzepte/README.md): Konzept des Ballon-Demonstrators
([`demonstrator_ballon_2026-05.md`](../../docs/konzepte/demonstrator_ballon_2026-05.md)), Technischer Begleitbericht
([`demonstrator_begleitbericht_2026-05.md`](../../docs/konzepte/demonstrator_begleitbericht_2026-05.md)) und
Pendeltest-Protokoll
([`demonstrator_pendeltest_horizontal_2026-05.md`](../../docs/konzepte/demonstrator_pendeltest_horizontal_2026-05.md)).
Steuerungs- und Logging-Firmware: [`../firmware/`](../firmware/README.md).

| Datei | Zweck | Eingabe und Aufruf | Ausgabe | Abhängigkeiten |
|---|---|---|---|---|
| [`pcmms_ballon_hoehen_tracker.py`](pcmms_ballon_hoehen_tracker.py) | Video → Höhen-CSV: größte Farbfläche je Bild (Ballon oder Marker; Farbvoreinstellung `--color` oder eigener HSV-Bereich), Ausreißerfilter, Median-Glättung, Höhe nach oben positiv in Metern | Videodatei und eine Kalibrierung: `--balloon-diam-m D`, `--ref-meters M --ref-pixels P` oder `--mpp X`; `--info` gibt Bildmaße und zwei Standbilder zum Kalibrieren aus | `<video>_hoehe.csv` (oder `--out`) mit `t_s,h_m`; optional `--debug-csv` (`frame,t_s,x_px,y_px,y_px_smooth,radius_px`) und `--preview` (annotiertes MP4) | numpy, OpenCV |
| [`pcmms_drift_analyse.py`](pcmms_drift_analyse.py) | Drift je Lauf als Steigung der Höhe (kleinste Quadrate, mit `--robust` Theil-Sen), Mittel und Streuung je Bedingung, Vergleich mit dem Pool der Kontrollen, Fallzahlabschätzung für `--target` (mm/s), Abbildung | `--data DIR`: je Bedingung ein Unterordner (Kontrollen nach `--controls`, Standard `off,random`; sonst z. B. `phase_090/`), darin je Lauf eine CSV `t_s,h_m` oder zwei Zahlenspalten; `--demo` erzeugt synthetische Daten in einem temporären Ordner | Bericht auf der Konsole (Drift in mm/s, Verdikt je Phase), PNG `--out` (Standard `drift_auswertung.png`) | numpy, matplotlib; scipy optional (sonst Ersatzrechnung für Theil-Sen, kein Welch-Test) |
| [`pcmms_pendel_tracker.py`](pcmms_pendel_tracker.py) | Marker-Tracking: roter Marker je Bild, gleitendes Mittel über die letzten 5 Detektionen | `python3 pcmms_pendel_tracker.py <video.mp4>` | `tracking_data.csv` im aktuellen Verzeichnis mit `frame,time_sec,x,y,x_smoothed,y_smoothed` (Pixel, ohne Maßstab) | numpy, OpenCV |

## Kette Video → Höhen-CSV → Drift

```bash
python3 pcmms_ballon_hoehen_tracker.py video.mp4 --info               # Bildmaße und Standbilder zum Kalibrieren
python3 pcmms_ballon_hoehen_tracker.py video.mp4 --balloon-diam-m D   # schreibt video_hoehe.csv (t_s,h_m)
# je Lauf eine CSV in den Ordner ihrer Bedingung legen, z. B. messdaten/off/, messdaten/random/, messdaten/phase_090/
python3 pcmms_drift_analyse.py --data messdaten                       # mit --robust: Theil-Sen
python3 pcmms_drift_analyse.py --demo                                 # nur synthetische Daten, kein Ergebnis
```

Die Aufrufe stammen aus den Kopfkommentaren der Skripte; bei der Übernahme wurden sie nicht ausgeführt. Dasselbe
Format `t_s,h_m` gibt der Höhenlogger
[`../firmware/pcmms_hoehen_logger_vl53l1x.ino`](../firmware/pcmms_hoehen_logger_vl53l1x.ino) über die serielle
Schnittstelle aus (Kopfkommentar des Sketches). Verdiktregel (Abstand zum Mittel der Kontrollen über 2·SD ihrer
Lauf-zu-Lauf-Streuung), Welch-Test und Fallzahlabschätzung (zweiseitig 5 %, Power 0,80) sind im Skript fest
eingestellt.

## Pendeltest

`pcmms_pendel_tracker.py` liefert Pixelkoordinaten ohne Maßstab und andere Spalten, als das Pendeltest-Protokoll
vorsieht (dort Abschnitt 5: `t_s, x_m, y_m`); sein Ausgang passt auch nicht zum Eingang von `pcmms_drift_analyse.py`
(`t_s,h_m`, sonst die ersten beiden Zahlenspalten als Zeit und Höhe). Die im Protokoll (Abschnitt 8) genannte
Umstellung der Drift-Auswertung von h(t) auf x(t) liegt nicht vor. Die Gesamtprojektanalyse (Stand 02.10.2026) hat
die Textfassungen `pcmms_drift_analyse.py.txt` (Kopf, Funktionsliste) unter Bündel B12 (Linie B) und
`pcmms_pendel_tracker.py.txt` (vollständig) unter B14 (Pendeltest) gelesen; Empfehlung für beide Bündel „parken“,
zum Pendeltest unter anderem „Tracker zu grob“
([`../../rechnungen/bewertung_b/PROTOKOLL.md`](../../rechnungen/bewertung_b/PROTOKOLL.md), Abschnitte 1 und 4).

## Abhängigkeiten

`pcmms_ballon_hoehen_tracker.py` und `pcmms_pendel_tracker.py` brauchen OpenCV (`import cv2`); der Ballon-Tracker
nennt bei fehlendem Modul `pip install opencv-python-headless`. OpenCV steht nicht in
[`../requirements.txt`](../requirements.txt) und wird dort nicht aufgenommen; kein anderes Skript und kein Test des
Repositorys braucht es. numpy, scipy und matplotlib stehen in `requirements.txt`.

## Herkunft

Die Skripte lagen außerhalb des Repositorys bei den Projektunterlagen des Demonstrators. `pcmms_pendel_tracker.py`
lag dort als `pcmms_pendel_tracker.py.txt` und ist mit berichtigter Endung übernommen, Inhalt unverändert. In die
Skripte ist kein Kopf eingefügt; ihre Einordnung steht nur hier.
