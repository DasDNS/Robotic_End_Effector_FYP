#include <Arduino.h>
#include <Wire.h>

void setup() {
  Serial.begin(115200);
  delay(500);
  
  Serial.println("Starting I2C scan on PB9(SDA)/PB8(SCL)...");

  Wire.setSDA(PB9);
  Wire.setSCL(PB8);
  Wire.begin();

  for (byte addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("Found device at 0x");
      Serial.println(addr, HEX);
    }
  }
  
  Serial.println("Scan complete.");
}

void loop() {}
