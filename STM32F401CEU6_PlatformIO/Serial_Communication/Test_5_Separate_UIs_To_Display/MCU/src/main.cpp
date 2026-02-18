#include <Arduino.h>

#define LED_PIN PC13   // if this doesn't work, try PB12 or change later

bool blinkMode = false;
uint32_t lastBlinkMs = 0;
bool ledState = false;

// periodic message timing
uint32_t lastFsrMs = 0;
uint32_t lastCurMs = 0;

void ledOn()  { digitalWrite(LED_PIN, LOW); }   // active LOW on many boards
void ledOff() { digitalWrite(LED_PIN, HIGH); }

void setup() {
  pinMode(LED_PIN, OUTPUT);
  ledOff();

  Serial.begin(115200);
  delay(300);

  Serial.println("Send: 1=ON, 0=OFF, 2=BLINK");
}

void loop() {
  // ---- read a single byte command ----
  while (Serial.available() > 0) {
    char c = (char)Serial.read();

    if (c == '1') {
      blinkMode = false;
      ledOn();
      Serial.println("LED ON");
    }
    else if (c == '0') {
      blinkMode = false;
      ledOff();
      Serial.println("LED OFF");
    }
    else if (c == '2') {
      blinkMode = true;
      Serial.println("LED BLINK");
    }
  }

  // ---- blink mode ----
  if (blinkMode) {
    uint32_t now = millis();
    if (now - lastBlinkMs >= 500) {   // 500ms toggle = 1Hz blink
      lastBlinkMs = now;
      ledState = !ledState;
      digitalWrite(LED_PIN, ledState ? LOW : HIGH);
    }
  }

  // ---- periodic prints (rate-limited) ----
  uint32_t now = millis();

  // every 2 seconds
  if (now - lastFsrMs >= 2000) {
    lastFsrMs = now;
    // replace this dummy text with your real readings later
    Serial.println("FSR Readings = e73264836r138419");
  }

  // every 3 seconds
  if (now - lastCurMs >= 3000) {
    lastCurMs = now;
    // replace this dummy text with your real readings later
    Serial.println("Current readings = 82392y93y`293");
  }
}
