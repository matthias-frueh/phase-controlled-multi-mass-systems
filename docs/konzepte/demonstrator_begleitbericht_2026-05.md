# PCMMS – Technischer Begleitbericht

**Phasenstarre Steuerung für zwei Vibrationsmodule**  
**Technischer Begleitbericht zum PCMMS-Demonstrator (fluidische Vertikaldrift)**

**Matthias Früh**  
ORCID: 0009-0005-9984-4207  
GitHub: github.com/matthias-frueh/phase-controlled-multi-mass-systems  
Zenodo DOI: 10.5281/zenodo.20080915  
Stand: Mai 2026

> **Vermerk (22.10.2026).** Originaldatei `PCMMS_Technischer_Begleitbericht_2026.md`, Stand Mai 2026; hier unverändert
> bis auf diesen Vermerk. Bauteilliste, Schaltung und ESP32-Code zum Ballon-Demonstrator
> ([`demonstrator_ballon_2026-05.md`](demonstrator_ballon_2026-05.md)) der Linie B; im Arbeitsplan Stufe S5 (geparkt),
> AP-28, Status „später“ ([`../arbeitsplan_status.md`](../arbeitsplan_status.md)). Mit dem Aufbau wurden keine
> Messdaten erzeugt. Seit Mai 2026 eingeordnet oder eingeschränkt:
> - **Code (Abschnitt 3):** liegt als [`pcmms_phasen_automatik.ino`](../../code/firmware/pcmms_phasen_automatik.ino) im
>   Repository; dort weichen nur Kommentare, Schreibweise und Textausgaben ab (u. a. „Bouncing-aehnlich (180°)“ statt
>   „Bouncing (180°)“). Die [Firmware-README](../../code/firmware/README.md) ordnet den Sketch dem Tisch- und
>   Pendeltest zu. Er stellt nur die Phase der PWM-Hüllkurve ein (keine Regelung, keine Messung der mechanischen
>   Phase), erzeugt nicht das Egg-Profil der Simulation und wurde bei der Übernahme ins Repository weder übersetzt noch
>   getestet (ebd.).
> - **Bauteilliste (Abschnitt 1):** Die Preise sind Schätzungen vom Mai 2026.
> - **Zenodo-DOI (Kopf):** siehe den Vermerk in [`demonstrator_ballon_2026-05.md`](demonstrator_ballon_2026-05.md).
>
> Lizenz wie der Ordner: CC BY 4.0 ([`../../LICENSE-CC-BY-4.0`](../../LICENSE-CC-BY-4.0)); der Sketch unter
> `code/firmware/` steht unter MIT.

## 1. Bauteilliste

| Komponente              | Vorschlag                          | ca. Preis |
|-------------------------|------------------------------------|-----------|
| Mikrocontroller        | ESP32 Dev Board (DOIT DEVKIT V1)  | 8,00 €   |
| Motortreiber           | 2x IRLZ44N N-Kanal MOSFET         | 1,00 €   |
| Vibrationsmotoren      | 2x Münzvibrationsmotor (10mm, 3V) | 2,00 €/St. |
| Freilaufdioden         | 2x 1N4007                         | 0,10 €   |
| Akku                   | LiPo 1S 500 mAh + JST             | 6,00 €   |
| Kleinkram              | Breadboard, Kabel, Widerstände    | 5,00 €   |

## 2. Schaltplan

- MOSFET Gate an GPIO25 (Motor 1) bzw. GPIO26 (Motor 2) mit 10 kΩ Pull-down nach GND.
- Drain an Motor-Masse, Source an GND.
- Freilaufdiode parallel zum Motor (Kathode an VCC, Anode an Drain).
- Motoren direkt am 3.7–4.2 V Akku.

## 3. ESP32 Automatik-Code (pcmms_phasen_automatik.ino)

```cpp
#include <Arduino.h>

const int motor1_pin = 25;
const int motor2_pin = 26;
const int pwm_freq = 80;
const int pwm_res = 8;

float amplitude = 220;
float freq = 5.0;
const int phase_duration = 30000;  // 30 Sekunden pro Phase

int phases[] = {0, 90, 180, 270, 0};
String phase_names[] = {"Ausloeschung (0°)", "Uebergang (90°)", "Bouncing (180°)", "Uebergang (270°)", "Motoren AUS"};

int current_phase = 0;
unsigned long phase_start = 0;
bool running = false;

void setup() {
  Serial.begin(115200);
  ledcSetup(0, pwm_freq, pwm_res);
  ledcSetup(1, pwm_freq, pwm_res);
  ledcAttachPin(motor1_pin, 0);
  ledcAttachPin(motor2_pin, 1);
  Serial.println("PCMMS Automatik-Tischtest bereit. Befehle: START | STOP");
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "START") { running = true; phase_start = millis(); current_phase = 0; Serial.println("=== Testzyklus START ==="); }
    if (cmd == "STOP")  { running = false; setMotors(0, 0); Serial.println("=== Test STOPPED ==="); }
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
```

## 4. Hinweise
- Münzmotoren haben Trägheit → Phasen nicht perfekt scharf.
- Für Tisch-/Pendeltest ideal.
- Serieller Monitor (115200 Baud) für Steuerung und Logging.

---

**Konzentriert:** Dies ist der vollständige Technische Begleitbericht.