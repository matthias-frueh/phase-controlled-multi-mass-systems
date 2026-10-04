/*  PCMMS Ballon — Hoehen-Logger (VL53L1X)
 *  --------------------------------------------------------------------------
 *  Loggt die Distanz des VL53L1X als CSV-Zeilen "t_s,h_m" ueber die serielle
 *  Schnittstelle. Im seriellen Monitor laeuft der Stream; mit einem Terminal-
 *  Programm (oder 'pio device monitor', PuTTY mit Logging, screen ... | tee ...)
 *  in eine Datei mitschneiden -> direkt in pcmms_drift_analyse.py einlesbar.
 *
 *  Montage: Sensor nach OBEN zeigend unter dem Ballon (misst Abstand zum Ballon)
 *           ODER am Ballon nach UNTEN zeigend (misst Hoehe ueber Boden). Die
 *           Auswertung nutzt nur die STEIGUNG, daher ist die Bezugsrichtung egal,
 *           solange sie pro Messreihe gleich bleibt.
 *
 *  Bibliothek: "VL53L1X" von Pololu (Arduino Library Manager).
 *  Verkabelung (I2C): VL53L1X  SDA->GPIO21  SCL->GPIO22  VIN->3V3  GND->GND
 *
 *  Befehle (115200 Baud):
 *    r   -> Zeit-Nullpunkt zuruecksetzen (Beginn eines neuen Runs)
 *    h   -> Kopfzeile erneut ausgeben
 */

#include <Wire.h>
#include <VL53L1X.h>

VL53L1X sensor;

const int SDA_PIN = 21, SCL_PIN = 22;
const uint16_t PERIOD_MS = 100;      // 10 Hz Lograte
unsigned long t0_ms = 0;
unsigned long lastLog_ms = 0;

void printHeader() { Serial.println("t_s,h_m"); }

void setup() {
  Serial.begin(115200);
  delay(300);
  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(400000);

  sensor.setTimeout(500);
  if (!sensor.init()) {
    Serial.println("# FEHLER: VL53L1X nicht gefunden (Verkabelung/Adresse pruefen).");
    while (1) { delay(1000); }
  }
  sensor.setDistanceMode(VL53L1X::Long);     // bis ~4 m
  sensor.setMeasurementTimingBudget(50000);  // 50 ms -> stabil
  sensor.startContinuous(PERIOD_MS);

  Serial.println("# PCMMS Hoehen-Logger bereit. 'r'=neuer Run, 'h'=Kopfzeile.");
  t0_ms = millis();
  printHeader();
}

void loop() {
  // Befehle
  while (Serial.available()) {
    char c = Serial.read();
    if (c == 'r') { t0_ms = millis(); Serial.println("# --- neuer Run ---"); printHeader(); }
    else if (c == 'h') printHeader();
  }

  // Loggen mit fester Rate
  unsigned long now = millis();
  if (now - lastLog_ms >= PERIOD_MS) {
    lastLog_ms = now;
    uint16_t mm = sensor.read();              // Distanz in mm
    if (sensor.timeoutOccurred()) return;     // Fehlmessung ueberspringen
    float t_s = (now - t0_ms) / 1000.0f;
    float h_m = mm / 1000.0f;
    Serial.print(t_s, 3); Serial.print(","); Serial.println(h_m, 4);
  }
}
