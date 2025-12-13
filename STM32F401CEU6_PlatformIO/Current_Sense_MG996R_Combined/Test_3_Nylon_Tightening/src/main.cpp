#include <Arduino.h>
#include <Wire.h>
#include <Servo.h>
#include <INA226_WE.h>

#define I2C_ADDRESS 0x40

// ====== Objects ======
Servo myservo;
INA226_WE ina226 = INA226_WE(I2C_ADDRESS);

// ====== Pin Definitions ======
#define SERVO_PIN PB13    // PWM pin for servo

// ====== Functions ======
void checkForI2cErrors();
void printINA226Data();

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\n=== STM32 Black Pill: Servo (PB13) + INA226 Test ===");

  // ====== Initialize I2C ======
  Wire.setSDA(PB7);
  Wire.setSCL(PB6);
  Wire.begin();

  // ====== I2C Scan ======
  bool found = false;
  Serial.println("Scanning I2C bus...");
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("Found device at 0x");
      Serial.println(addr, HEX);
      if (addr == I2C_ADDRESS) found = true;
    }
  }

  if (!found) {
    Serial.println("INA226 NOT FOUND!");
  } else {
    Serial.println("INA226 found. Initializing...");
  }

  if (!ina226.init()) {
    Serial.println("INA226 init failed!");
    while (1) {}
  }

  ina226.waitUntilConversionCompleted();

  // ====== Attach Servo ======
  myservo.attach(SERVO_PIN);  
  Serial.println("Servo attached to PB13.\n");

  Serial.println("Enter 0, 1, or 2 to move the servo:");

}

void checkForI2cErrors() {
  byte errorCode = ina226.getI2cErrorCode();
  if (errorCode) {
    Serial.print("I2C error: ");
    Serial.println(errorCode);
    while (1) {}
  }
}

void printINA226Data() {
  float shuntVoltage_mV = ina226.getShuntVoltage_mV();
  float busVoltage_V = ina226.getBusVoltage_V();
  float current_mA = ina226.getCurrent_mA();
  float power_mW = ina226.getBusPower();
  float loadVoltage_V = busVoltage_V + (shuntVoltage_mV / 1000);

  checkForI2cErrors();

  Serial.print("Current[mA]: ");
  Serial.println(current_mA);

  Serial.println();
  delay(300);
}

void moveServoUS(int pulseWidth) {
  Serial.print("Moving servo (us): ");
  Serial.println(pulseWidth);

  myservo.writeMicroseconds(pulseWidth);

  // Print INA226 samples for 1 second
  unsigned long start = millis();
  while (millis() - start < 1000) {
    printINA226Data();
  }
}

void loop() {

  if (Serial.available()) {
    char cmd = Serial.read();

    switch (cmd) {
      case '0':
        Serial.println("Command 0 → Fully bent position");
        moveServoUS(500);      // same as ESP32
        break;

      case '1':
        Serial.println("Command 1 → Half bent (midpoint)");
        moveServoUS(1450);     // same as ESP32
        break;

      case '2':
        Serial.println("Command 2 → Fully straightened");
        moveServoUS(2400);     // same as ESP32
        break;

      default:
        Serial.println("Invalid. Use 0, 1, or 2.");
        break;
    }

    Serial.println("Enter next command:");
  }
}
