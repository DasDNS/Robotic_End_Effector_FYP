#include <Arduino.h>
#include <Wire.h>
#include <INA226.h>

// Create INA226 object with default I2C address (0x40)
INA226 ina226(0x40);

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Initialize I2C (ESP32 default pins: SDA=21, SCL=22)
  Wire.begin(21, 22);

  Serial.println("Initializing INA226...");

  if (!ina226.begin()) {
    Serial.println("❌ Could not connect to INA226. Check wiring and address.");
    while (1) delay(1000);
  }

  // Configure shunt resistor and maximum expected current
  // Example: shunt = 0.1 ohm, expect up to 0.02 A (20 mA)
ina226.setMaxCurrentShunt(0.02, 0.1);

  Serial.println("✅ INA226 Initialized Successfully!");
}

void loop() {
  float busVoltage = ina226.getBusVoltage();
  float shuntVoltage = ina226.getShuntVoltage_mV();
  float current_mA = ina226.getCurrent_mA();
  float power_mW = ina226.getPower_mW();

  Serial.print(">BusV:");
  Serial.print(busVoltage, 3);
  Serial.print(",ShuntV_mV:");
  Serial.print(shuntVoltage, 3);
  Serial.print(",Current_mA:");
  Serial.print(current_mA, 3);
  Serial.print(",Power_mW:");
  Serial.println(power_mW, 3);

  delay(2000);
}
