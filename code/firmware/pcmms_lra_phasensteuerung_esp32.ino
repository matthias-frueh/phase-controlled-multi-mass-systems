/*  PCMMS Ballon-Demonstrator — LRA-Variante (leicht & echt phasenstarr)
 *  --------------------------------------------------------------------------------------
 *  Zwei LRAs (lineare Resonanz-Aktoren) werden mit je einem Sinus DERSELBEN Frequenz und
 *  einstellbarem PHASENVERSATZ getrieben. Den Sinus erzeugt der ESP32 selbst als fein
 *  aufgeloestes PWM (SPWM) und schickt ihn ueber eine Dual-H-Bruecke (DRV8833) an die Spulen.
 *
 *  WARUM PHASE HIER ECHT IST: Beide Kanaele werden aus EINEM gemeinsamen Phasenzaehler
 *  berechnet. Kanal B ist um 'phase_deg' versetzt -> der Phasenversatz ist exakt und
 *  bleibt verriegelt, egal wie lange es laeuft. (Anders als bei freilaufenden Muenz-ERM-
 *  Motoren, deren Drehphase ohne Rueckmeldung wegdriftet.)
 *
 *  ZWEI PRAXIS-HINWEISE:
 *   1) LRAs bewegen sich nur NAHE ihrer Resonanz spuerbar. F_RES unten auf den Wert deines
 *      LRA setzen (Datenblatt; oft 175 oder 205 Hz). Mit 'sweep' kannst du die Resonanz
 *      durch Hoeren/Fuehlen finden.
 *   2) Damit der Phasenversatz die Bewegung FORMT (nicht nur die Amplitude aendert), die
 *      beiden LRAs nicht parallel/kollinear montieren, sondern ueber Eck / im Winkel.
 *
 *  --------------------------------------------------------------------------------------
 *  BAUTEILLISTE (leicht, billig):
 *    1x ESP32 Dev-Board                                             ~8 €
 *    1x DRV8833 Dual-H-Bruecken-Modul                               ~2-3 €
 *    2x LRA (z.B. 10 mm Coin-LRA, ~175 Hz, ~2 V)                    ~1-3 €/St.
 *    1x LiPo 1S (3,7-4,2 V)                                         ~6 €
 *    Kleinkram: Kondensatoren 0,1 µF + 10 µF (an VM), Kabel
 *
 *  VERKABELUNG (DRV8833):
 *    LiPo + ──┬── ESP32 5V/VIN     (Board macht 3,3 V selbst)
 *             └── DRV8833 VM (Motorspannung)
 *    GND gemeinsam:  LiPo − ── ESP32 GND ── DRV8833 GND
 *    ESP32 -> DRV8833:   GPIO25->AIN1  GPIO26->AIN2   (LRA A an AOUT1/AOUT2)
 *                        GPIO27->BIN1  GPIO14->BIN2   (LRA B an BOUT1/BOUT2)
 *    DRV8833 nSLEEP/EEP -> 3,3 V (aktiv schalten).  Cs (0,1µF+10µF) an VM/GND nahe am IC.
 *    HINWEIS: GPIO25/26 sind zwar DAC-Pins, werden hier aber als digitale PWM-Eingaenge
 *             der H-Bruecke genutzt (SPWM), nicht als Analog-DAC.
 *
 *  SPANNUNG/SCHUTZ: LRAs sind oft nur ~2 V (RMS) ausgelegt. AMP unten konservativ lassen;
 *                   wird ein LRA warm -> AMP verringern.
 *
 *  Serielle Befehle (115200 Baud):
 *    f 175            -> Frequenz auf 175 Hz
 *    p 90             -> Phasenversatz B ggue. A auf 90 Grad
 *    a 150            -> Amplitude (0-255)
 *    on / off         -> Ausgabe an / aus
 *    sweep 150 220 8  -> Frequenz in 8 s von 150 auf 220 Hz fahren (Resonanz suchen)
 *    s                -> Status   |   ?  -> Hilfe
 */

#include <Arduino.h>
#include <math.h>

// ============================ KONFIGURATION ============================
const int   AIN1 = 25, AIN2 = 26;      // H-Bruecke Kanal A  -> LRA A
const int   BIN1 = 27, BIN2 = 14;      // H-Bruecke Kanal B  -> LRA B

const int   PWM_FREQ  = 20000;         // PWM-Traegerfrequenz (Hz), > hoerbar, < Schaltverluste
const int   PWM_RES   = 8;             // PWM-Aufloesung (Bit) -> Duty 0..255
const int   SAMPLE_HZ = 8000;          // Sinus-Abtastrate (Stuetzstellen/s)

float F_RES_DEFAULT   = 175.0f;        // <-- Resonanzfrequenz deines LRA hier eintragen!
const int   AMP_MAX   = 255;
// =======================================================================

// LEDC-Kanaele (Arduino-ESP32 Core 2.x). Bei Core 3.x: ledcAttach(pin,freq,res)+ledcWrite(pin,duty).
const int CH_A1 = 0, CH_A2 = 1, CH_B1 = 2, CH_B2 = 3;

// ---- Laufzeit-Parameter ----
volatile float freq_hz   = 175.0f;
volatile float phase_deg = 90.0f;
volatile int   amp       = 150;        // 0..AMP_MAX
volatile bool  running   = false;

// ---- interner Zustand ----
float phase = 0.0f;                    // gemeinsamer Phasenzaehler (rad), in [0, 2*PI)
unsigned long lastSample_us = 0;
const unsigned long sampleInterval_us = 1000000UL / SAMPLE_HZ;

// ---- Frequenz-Sweep (nicht blockierend) ----
bool  sweeping = false;
float sw_f0 = 0, sw_f1 = 0;
unsigned long sw_t0 = 0, sw_dur_ms = 0;

inline float phaseOffsetRad() { return phase_deg * (float)M_PI / 180.0f; }

// Einen Sinuswert s in [-1,1] als VORZEICHEN-BETRAG auf eine H-Bruecke geben:
// positive Halbwelle -> in1 = |s|*amp, in2 = 0 ; negative Halbwelle -> umgekehrt.
inline void driveBridge(int ch1, int ch2, float s) {
  int duty = (int)(fabsf(s) * (float)amp);
  if (duty > AMP_MAX) duty = AMP_MAX;
  if (s >= 0.0f) { ledcWrite(ch1, duty); ledcWrite(ch2, 0); }
  else           { ledcWrite(ch1, 0);    ledcWrite(ch2, duty); }
}

inline void outputsOff() {
  ledcWrite(CH_A1, 0); ledcWrite(CH_A2, 0);
  ledcWrite(CH_B1, 0); ledcWrite(CH_B2, 0);
}

void printStatus() {
  Serial.print("status | f="); Serial.print(freq_hz, 1);
  Serial.print(" Hz  phi=");   Serial.print(phase_deg, 1);
  Serial.print(" deg  amp=");  Serial.print(amp);
  Serial.print("  ");          Serial.print(running ? "[an]" : "[aus]");
  Serial.println(sweeping ? "  (sweep laeuft)" : "");
}

void printHelp() {
  Serial.println(F("\nBefehle: 'f <Hz>'  'p <Grad>'  'a <0-255>'  'on'  'off'"
                   "  'sweep <f1> <f2> <s>'  's'(Status)  '?'(Hilfe)"));
}

void handleSerial() {
  static char buf[40];
  static uint8_t n = 0;
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (n == 0) continue;
      buf[n] = 0; n = 0;
      if (buf[0] == 'f')                       freq_hz   = atof(buf + 1);
      else if (buf[0] == 'p')                  phase_deg = atof(buf + 1);
      else if (buf[0] == 'a') { amp = atoi(buf + 1); if (amp < 0) amp = 0; if (amp > AMP_MAX) amp = AMP_MAX; }
      else if (!strcmp(buf, "on"))  { running = true;  Serial.println("-> AN"); }
      else if (!strcmp(buf, "off")) { running = false; outputsOff(); Serial.println("-> AUS"); }
      else if (!strncmp(buf, "sweep", 5)) {
        float a1, a2; int secs;
        if (sscanf(buf + 5, "%f %f %d", &a1, &a2, &secs) == 3 && secs > 0) {
          sw_f0 = a1; sw_f1 = a2; sw_dur_ms = (unsigned long)secs * 1000UL;
          sw_t0 = millis(); sweeping = true; running = true;
          Serial.printf("-> Sweep %.0f..%.0f Hz in %d s\n", a1, a2, secs);
        } else Serial.println("?? sweep <f1> <f2> <sekunden>");
      }
      else if (buf[0] == 's')  printStatus();
      else if (buf[0] == '?')  printHelp();
      else Serial.println("?? unbekannt — '?' fuer Hilfe");
      if (buf[0] == 'f' || buf[0] == 'p' || buf[0] == 'a') printStatus();
    } else if (n < sizeof(buf) - 1) {
      buf[n++] = c;
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(300);

  ledcSetup(CH_A1, PWM_FREQ, PWM_RES);  ledcAttachPin(AIN1, CH_A1);
  ledcSetup(CH_A2, PWM_FREQ, PWM_RES);  ledcAttachPin(AIN2, CH_A2);
  ledcSetup(CH_B1, PWM_FREQ, PWM_RES);  ledcAttachPin(BIN1, CH_B1);
  ledcSetup(CH_B2, PWM_FREQ, PWM_RES);  ledcAttachPin(BIN2, CH_B2);
  outputsOff();

  freq_hz = F_RES_DEFAULT;
  lastSample_us = micros();

  Serial.println(F("\nPCMMS LRA-Steuerung bereit. Ausgabe ist AUS ('on' zum Start)."));
  Serial.println(F("Tipp: erst 'sweep 150 220 8' und auf das staerkste Brummen hoeren."));
  printHelp();
  printStatus();
}

void loop() {
  // Sweep (falls aktiv) nicht blockierend nachfuehren:
  if (sweeping) {
    unsigned long el = millis() - sw_t0;
    if (el >= sw_dur_ms) { sweeping = false; freq_hz = sw_f1; }
    else freq_hz = sw_f0 + (sw_f1 - sw_f0) * ((float)el / (float)sw_dur_ms);
  }

  // Sinus mit fester Abtastrate erzeugen (gemeinsamer Phasenzaehler -> Phase exakt):
  unsigned long now = micros();
  if ((unsigned long)(now - lastSample_us) >= sampleInterval_us) {
    lastSample_us += sampleInterval_us;     // driftfreie Taktung

    if (running) {
      float s1 = sinf(phase);
      float s2 = sinf(phase + phaseOffsetRad());
      driveBridge(CH_A1, CH_A2, s1);
      driveBridge(CH_B1, CH_B2, s2);
    }

    phase += 2.0f * (float)M_PI * freq_hz / (float)SAMPLE_HZ;
    if (phase >= 2.0f * (float)M_PI) phase -= 2.0f * (float)M_PI;   // beschraenkt halten
  }

  handleSerial();
}
