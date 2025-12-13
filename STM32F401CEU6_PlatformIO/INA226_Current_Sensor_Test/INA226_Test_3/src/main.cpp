#include <Arduino.h>
#include <Wire.h>
#include <INA226.h>

INA226* ina = nullptr;  // Pointer to INA226 object

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("Scanning I2C bus for devices...");

  // Set I2C pins for STM32
  Wire.setSDA(PB9);
  Wire.setSCL(PB8);
  Wire.begin();

  bool found = false;
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("Found device at 0x");
      Serial.println(addr, HEX);
      if (addr == 0x40) { // INA226 default address
        found = true;
      }
    }
  }

  if (found) {
    Serial.println("INA226 detected! Initializing...");
    ina = new INA226(0x40, &Wire);
    ina->setMaxCurrentShunt(0.02, 0.1);
    if (!ina->begin()) {
      Serial.println("Failed to initialize INA226!");
      while (1);
    }
    Serial.println("INA226 initialized successfully!");
  } else {
    Serial.println("INA226 not found on I2C bus.");
  }
}

void loop() {
  if (ina) {  // Only read if INA226 was initialized
    float busVoltage = ina->getBusVoltage();      // in Volts
    float shuntVoltage = ina->getShuntVoltage();  // in mV
    float current_mA = ina->getCurrent_mA();      // in mA
    float power_mW = ina->getPower_mW();          // in mW

    Serial.print("Bus Voltage: "); Serial.print(busVoltage); Serial.println(" V");
    Serial.print("Shunt Voltage: "); Serial.print(shuntVoltage); Serial.println(" mV");
    Serial.print("Current: "); Serial.print(current_mA); Serial.println(" mA");
    Serial.print("Power: "); Serial.print(power_mW); Serial.println(" mW");
    Serial.println("----------------------");
  } else {
    Serial.println("INA226 not initialized. Check connection.");
  }

  delay(1000);
}
