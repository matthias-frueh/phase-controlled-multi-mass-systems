// PCMMS Automatischer Phasenzyklus für Tisch-/Pendeltest
#include <Arduino.h>

const int motor1_pin = 25;
const int motor2_pin = 26;
const int pwm_freq = 80;
const int pwm_res = 8;

float amplitude = 220.0;
float freq = 5.0;
const int phase_duration = 30000;  // ms pro Phase

int phases[] = {0, 90, 180, 270, 0};
String phase_names[] = {"Ausloeschung (0°)", "Uebergang (90°)", "Bouncing-aehnlich (180°)", "Uebergang (270°)", "Motoren AUS"};

int current_phase = 0;
unsigned long phase_start = 0;
bool running = false;

void setup() {
  Serial.begin(115200);
  ledcSetup(0, pwm_freq, pwm_res);
  ledcSetup(1, pwm_freq, pwm_res);
  ledcAttachPin(motor1_pin, 0);
  ledcAttachPin(motor2_pin, 1);
  
  Serial.println("PCMMS Automatik-Tischtest bereit.");
  Serial.println("Befehle: START | STOP");
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "START") {
      running = true;
      phase_start = millis();
      current_phase = 0;
      Serial.println("=== Testzyklus START ===");
    }
    if (cmd == "STOP") {
      running = false;
      setMotors(0, 0);
      Serial.println("=== Test STOPPED ===");
    }
  }

  if (!running) {
    setMotors(0, 0);
    return;
  }

  unsigned long now = millis();
  if (now - phase_start >= phase_duration) {
    current_phase = (current_phase + 1) % 5;
    phase_start = now;
    Serial.printf("Phase %d: %s\n", current_phase, phase_names[current_phase].c_str());
  }

  float t = millis() / 1000.0;
  float omega = 2.0 * PI * freq;
  float phi_base = omega * t;

  if (current_phase == 4) {
    setMotors(0, 0);
  } else {
    float phase_shift = phases[current_phase] * PI / 180.0;
    int duty1 = (int)(amplitude * (sin(phi_base) * 0.5 + 0.5));
    int duty2 = (int)(amplitude * (sin(phi_base + phase_shift) * 0.5 + 0.5));
    ledcWrite(0, duty1);
    ledcWrite(1, duty2);
  }

  delay(10);
}

void setMotors(int d1, int d2) {
  ledcWrite(0, d1);
  ledcWrite(1, d2);
}
