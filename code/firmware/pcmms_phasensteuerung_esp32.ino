/*  PCMMS Ballon-Demonstrator — Phasensteuerung zweier brushless (BLDC) Vibrationsmotoren
 *  ----------------------------------------------------------------------------------------
 *  Zwei exzentrisch belastete BLDC-Motoren drehen mit gemeinsamer Frequenz f und
 *  einstellbarem Phasenversatz phi. Eine CLOSED-LOOP WINKELREGELUNG haelt die Phase exakt
 *  (im Gegensatz zu reiner Drehzahlregelung, deren Phase langsam wegdriftet).
 *
 *  WICHTIG: Einfache "Handy-Vibrationsmotoren" (ERM, gebuerstet, Muenzform) lassen sich
 *           NICHT phasenstarr regeln — ihnen fehlt die Rotorlage-Rueckmeldung. Fuer echte
 *           Phasenkontrolle braucht man Rotorwinkel-Feedback (hier je ein AS5600 pro Motor).
 *
 *  Bibliothek:  "Simple FOC" (Arduino Library Manager -> SimpleFOC)
 *  Board:       ESP32 (zwei Hardware-I2C-Busse: Wire + Wire1)
 *
 *  Minimal-BOM:
 *    2x BLDC-Gimbalmotor (z.B. 2804/2208, ~20-30 g)        je 1 exzentrische Masse anbringen
 *    2x AS5600 Magnetencoder-Board + diametraler Magnet     fixer I2C-Adresse 0x36 -> getrennte Busse!
 *    2x BLDC-3-Phasen-Treiber (z.B. DRV8313 / SimpleFOC Mini)
 *    1x ESP32 Dev-Board
 *    Versorgung 2S-3S LiPo empfohlen (FOC-Drehmoment); 1S/3,7 V ist knapp.
 *
 *  Serielle Befehle (115200 Baud):
 *    f 5      -> Frequenz auf 5 Hz   (stetig, ohne Phasensprung)
 *    p 90     -> Phasenversatz B ggue. A auf 90 Grad
 *    on / off -> Vibration starten / stoppen
 *    s        -> Status ausgeben
 *    ?        -> diese Hilfe
 */

#include <SimpleFOC.h>

// ============================ KONFIGURATION (anpassen!) ============================
const int   POLE_PAIRS = 7;        // Polpaarzahl des Motors (Datenblatt; bei Gimbal oft 7 oder 11)
const float SUPPLY_V   = 8.0f;     // Versorgungsspannung in Volt (2S ~8V; 1S/3,7V = schwach)
const float VOLT_LIMIT = 4.0f;     // Spannungsgrenze an den Motor (Drehmoment / Erwaermung)

// 3 PWM-Pins + Enable je Treiber (ESP32-Ausgaenge; GPIO12/0/2/15 als Strapping-Pins gemieden):
const int A_PWM[3] = {25, 26, 27};  const int A_EN = 14;   // Motor A
const int B_PWM[3] = {16, 17,  4};  const int B_EN =  5;   // Motor B

// I2C-Pins fuer die beiden AS5600 (getrennte Busse -> gleiche Adresse 0x36 ist kein Problem):
const int A_SDA = 21, A_SCL = 22;   // Wire   (Encoder Motor A)
const int B_SDA = 32, B_SCL = 33;   // Wire1  (Encoder Motor B)
// ===================================================================================

BLDCMotor       motorA = BLDCMotor(POLE_PAIRS);
BLDCMotor       motorB = BLDCMotor(POLE_PAIRS);
BLDCDriver3PWM  drvA   = BLDCDriver3PWM(A_PWM[0], A_PWM[1], A_PWM[2], A_EN);
BLDCDriver3PWM  drvB   = BLDCDriver3PWM(B_PWM[0], B_PWM[1], B_PWM[2], B_EN);
MagneticSensorI2C encA = MagneticSensorI2C(AS5600_I2C);
MagneticSensorI2C encB = MagneticSensorI2C(AS5600_I2C);

// ---- Laufzeit-Parameter ----
float freq_hz   = 3.0f;     // gemeinsame Drehfrequenz
float phase_deg = 90.0f;    // Phasenversatz B gegenueber A (Grad)
bool  running   = false;

float offA = 0, offB = 0;   // absolute Winkel-Offsets; es gilt immer (offB - offA) == Phase
float omega = 0;            // rad/s
unsigned long t0_us = 0;

inline float phaseRad() { return phase_deg * PI / 180.0f; }
inline float thetaNow() { return omega * (micros() - t0_us) * 1e-6f; }

// Bisher aufgelaufene Phase in die Offsets falten und Zeitbasis zuruecksetzen.
// So lassen sich Frequenz/Phase im Lauf STETIG (ohne Winkelsprung) aendern,
// und die Float-Werte bleiben langfristig beschraenkt.
void reanchor() {
  float th = thetaNow();
  offA += th;
  offB += th;
  t0_us = micros();
}

void setFreq(float f) {
  if (f < 0) f = 0;
  if (running) reanchor();   // stetig umschalten
  freq_hz = f;
  omega   = TWO_PI * f;
}

void setPhase(float deg) {
  phase_deg = deg;
  offB = offA + phaseRad();  // B sofort auf neue Phase relativ zu A
}

void startMotion() {
  offA  = motorA.shaft_angle;     // A startet, wo er steht (kein Drehmoment-Schlag)
  offB  = offA + phaseRad();      // B auf korrekte Phase relativ zu A
  omega = TWO_PI * freq_hz;
  t0_us = micros();
  motorA.enable();
  motorB.enable();
  running = true;
  Serial.println("-> Vibration AN");
}

void stopMotion() {
  running = false;
  motorA.disable();               // Drehmoment weg; exzentrische Masse haengt nach unten aus
  motorB.disable();
  Serial.println("-> Vibration AUS");
}

void printStatus() {
  Serial.print("status | f="); Serial.print(freq_hz, 2); Serial.print(" Hz  phi=");
  Serial.print(phase_deg, 1);  Serial.print(" deg  ");
  Serial.println(running ? "[laeuft]" : "[gestoppt]");
}

void printHelp() {
  Serial.println(F("\nBefehle: 'f <Hz>'  'p <Grad>'  'on'  'off'  's'(Status)  '?'(Hilfe)"));
}

void setupMotor(BLDCMotor &m, BLDCDriver3PWM &d, MagneticSensorI2C &enc, TwoWire &bus) {
  enc.init(&bus);
  m.linkSensor(&enc);

  d.voltage_power_supply = SUPPLY_V;
  d.init();
  m.linkDriver(&d);

  m.voltage_limit = VOLT_LIMIT;
  m.controller    = MotionControlType::angle;   // Winkelregelung -> Phase bleibt verriegelt

  // Regler-Startwerte (bei Bedarf nachstellen):
  m.PID_velocity.P = 0.2f;
  m.PID_velocity.I = 2.0f;
  m.PID_velocity.D = 0.0f;
  m.LPF_velocity.Tf = 0.01f;
  m.P_angle.P      = 20.0f;
  m.velocity_limit = 200.0f;                     // rad/s Obergrenze

  m.init();
  m.initFOC();                                   // kalibriert Sensor-Nullpunkt & Drehrichtung
}

void handleSerial() {
  static char buf[24];
  static uint8_t n = 0;
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (n == 0) continue;
      buf[n] = 0; n = 0;
      // parsen
      if (buf[0] == 'f')       setFreq(atof(buf + 1));
      else if (buf[0] == 'p')  setPhase(atof(buf + 1));
      else if (!strcmp(buf, "on"))  startMotion();
      else if (!strcmp(buf, "off")) stopMotion();
      else if (buf[0] == 's')  printStatus();
      else if (buf[0] == '?')  printHelp();
      else Serial.println("?? unbekannt — '?' fuer Hilfe");
      if (buf[0] == 'f' || buf[0] == 'p') printStatus();
    } else if (n < sizeof(buf) - 1) {
      buf[n++] = c;
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(300);
  Wire.begin(A_SDA, A_SCL, 400000UL);
  Wire1.begin(B_SDA, B_SCL, 400000UL);

  Serial.println(F("\nPCMMS Phasensteuerung — Initialisierung (FOC-Kalibrierung) ..."));
  setupMotor(motorA, drvA, encA, Wire);
  setupMotor(motorB, drvB, encB, Wire1);
  omega = TWO_PI * freq_hz;

  Serial.println(F("Bereit. Motoren stehen still (off). 'on' zum Start."));
  printHelp();
  printStatus();
}

void loop() {
  // FOC-Schleife so schnell wie moeglich laufen lassen:
  motorA.loopFOC();
  motorB.loopFOC();

  if (running) {
    // Float langfristig beschraenkt halten:
    if ((micros() - t0_us) > 60UL * 1000000UL) reanchor();
    float th = thetaNow();
    motorA.move(offA + th);
    motorB.move(offB + th);     // (offB + th) - (offA + th) == Phasenversatz, exakt
  } else {
    motorA.move(motorA.shaft_angle);   // Position halten (bzw. disabled)
    motorB.move(motorB.shaft_angle);
  }

  handleSerial();
}
