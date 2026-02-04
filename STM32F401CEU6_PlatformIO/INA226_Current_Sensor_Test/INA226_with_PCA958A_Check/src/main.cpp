#include <Arduino.h>
#include <Wire.h>
#include <INA226_WE.h>

#define PCA9548A_ADDRESS 0x70
#define INA226_ADDRESS   0x40

// --- Create ONE INA226 object (we will reuse it on each mux channel)
INA226_WE ina226 = INA226_WE(INA226_ADDRESS);

// Select a PCA9548A channel (0–7)
void selectPCAChannel(uint8_t channel) {
  Wire.beginTransmission(PCA9548A_ADDRESS);
  Wire.write(1 << channel);
  Wire.endTransmission();
}

// Scan current I2C bus and print found devices
void scanI2CBus(const char* label) {
  Serial.println(label);

  bool foundAny = false;

  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("  Found I2C device at 0x");
      if (addr < 16) Serial.print("0");
      Serial.println(addr, HEX);
      foundAny = true;
    }
  }

  if (!foundAny) {
    Serial.println("  (no devices found)");
  }

  Serial.println();
}

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("\n=== STM32 PB8/PB9 I2C + PCA9548A Scanner + INA226 Init Test ===");

  // I2C pins for STM32 Black Pill
  Wire.setSDA(PB9);
  Wire.setSCL(PB8);
  Wire.begin();

  // ---- Scan MAIN bus (before selecting any PCA channel) ----
  scanI2CBus("[SCAN] Main I2C bus (expect PCA9548A at 0x70)");

  // ---- Scan each PCA channel ----
  for (uint8_t ch = 0; ch < 8; ch++) {
    Serial.print("[SCAN] PCA9548A channel ");
    Serial.println(ch);

    selectPCAChannel(ch);
    delay(10);

    scanI2CBus("  Devices behind this channel:");

    // ---- INA226 init attempt on THIS channel (same style as your working code) ----
    // We check if INA226 exists at 0x40, then try init().
    bool foundINA = false;
    Wire.beginTransmission(INA226_ADDRESS);
    if (Wire.endTransmission() == 0) {
      foundINA = true;
    }

    if (!foundINA) {
      Serial.println("  INA226 NOT FOUND on this channel.");
    } else {
      Serial.println("  INA226 found on this channel. Initializing...");

      if (!ina226.init()) {
        Serial.println("  INA226 init failed on this channel!");
        // Do NOT stop the whole program here (scanner continues to next channels)
      } else {
        Serial.println("  INA226 init OK on this channel!");
        ina226.waitUntilConversionCompleted();

        // Optional: take one reading to confirm it works
        float current_mA = ina226.getCurrent_mA();
        Serial.print("  INA226 current (mA): ");
        Serial.println(current_mA);
      }
    }

    Serial.println("----------------------------------");
  }

  Serial.println("=== Scan + INA226 init test complete ===");
}

void loop() {
  // nothing here
}
