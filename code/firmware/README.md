# Firmware-Muster (ESP32) für Demonstratoren und Tischtests

Stand der Dateien: 2026; übernommen am 4. Oktober 2026, unverändert. Lizenz: MIT wie der übrige Code
([`../../LICENSE`](../../LICENSE)).

Die vier Sketche sind die vorhandene Steuerungs- und Logging-Software des Projekts. Sie gehören zu Demonstratoren und
Tischtests mit **zwei** Aktoren, nicht zur geplanten Apparatur V1 (drei Module, Encoder je Modul, Hardware-Zeitstempel,
Schutzpfad; Arbeitsplan AP-01 und AP-10, [`../../docs/arbeitsplan_status.md`](../../docs/arbeitsplan_status.md)).
Eine V1-Firmware liegt nicht vor. Mit keinem der Sketche wurden Messdaten des Projekts erzeugt.

| Datei | Zweck | Hardware | Phasenlage |
|---|---|---|---|
| [`pcmms_phasensteuerung_esp32.ino`](pcmms_phasensteuerung_esp32.ino) | Demonstrator mit zwei exzentrisch belasteten BLDC-Motoren: gemeinsame Frequenz, einstellbarer Phasenversatz, serielle Befehle | ESP32, zwei BLDC-Gimbalmotoren, zwei AS5600-Encoder, zwei Dreiphasentreiber (Bibliothek SimpleFOC) | geschlossene Winkelregelung je Motor über die Rotorlage |
| [`pcmms_lra_phasensteuerung_esp32.ino`](pcmms_lra_phasensteuerung_esp32.ino) | Demonstrator mit zwei linearen Resonanzaktoren (LRA): Sinus derselben Frequenz aus einem gemeinsamen Phasenzähler, Resonanzsuche | ESP32, DRV8833, zwei LRA | berechnet, zwischen den Kanälen phasenstarr; Betrieb nahe der LRA-Resonanz (typisch 175–205 Hz) |
| [`pcmms_phasen_automatik.ino`](pcmms_phasen_automatik.ino) | Tisch- und Pendeltest: fester Phasenzyklus (0°, 90°, 180°, 270°, aus) zweier Vibrationsmotoren über die PWM-Hüllkurve | ESP32, zwei Münzvibrationsmotoren (ERM) | nur die Phase der PWM-Hüllkurve; keine Regelung und keine Messung der mechanischen Phase |
| [`pcmms_hoehen_logger_vl53l1x.ino`](pcmms_hoehen_logger_vl53l1x.ino) | Abstands- und Höhenlogger als CSV über die serielle Schnittstelle | ESP32, VL53L1X (Bibliothek VL53L1X von Pololu) | – |

Einordnung: Die BLDC- und LRA-Sketche gehören zum Ballon-Demonstrator der Linie B (frei bewegter Körper im Medium),
der Tischtest-Sketch zur frühen Erprobung. Für Linie A (ruhender Körper auf Wägezellen) ist nur die Methode der
Phasenstellung übertragbar. Erreichte Phasengenauigkeiten sind nicht gemessen; die Firmware ist kein Beleg dafür.
Das Egg-Profil der Simulation erzeugt keiner der Sketche (Sinus- bzw. Rotationsbewegung).

Übersetzen: Arduino-IDE oder PlatformIO mit ESP32-Board-Paket und den genannten Bibliotheken. Die Sketche wurden bei
der Übernahme nicht übersetzt oder getestet.
