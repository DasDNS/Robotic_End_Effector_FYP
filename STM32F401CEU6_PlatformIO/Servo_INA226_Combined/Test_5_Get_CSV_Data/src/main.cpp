#include <Arduino.h>
#include <Wire.h>
#include <Servo.h>
#include <INA226_WE.h>

// ===============================
// DEFINES & CONSTANTS
// ===============================
#define I2C_ADDRESS 0x40
#define SERVO_PIN   PB13

#define SERVO_MIN_US 500
#define SERVO_MAX_US 2400
#define SERVO_STEP   100

// ===============================
// OBJECTS
// ===============================
Servo myservo;
INA226_WE ina226 = INA226_WE(I2C_ADDRESS);

// ===============================
// GLOBAL VARIABLES
// ===============================
int currentPulseWidth = 1450;   // Track current servo position (µs)

// ===============================
// FUNCTION PROTOTYPES
// ===============================
void checkForI2cErrors();
void printINA226Data();
void moveServoUS(int pulseWidth);

// ===============================
// SETUP
// ===============================
void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("\n=== STM32 Black Pill: Servo + INA226 Control ===");

  // -------- I2C SETUP --------
  Wire.setSDA(PB7);
  Wire.setSCL(PB6);
  Wire.begin();

  // -------- I2C SCAN --------
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

  // -------- SERVO SETUP --------
  myservo.attach(SERVO_PIN);
  myservo.writeMicroseconds(currentPulseWidth);

  Serial.println("Servo attached to PB13.");
  Serial.println("\nCommands:");
  Serial.println("0 → Fully bent");
  Serial.println("1 → Mid position");
  Serial.println("2 → Fully straight");
  Serial.println("3 → Step -100 us");
  Serial.println("4 → Step +100 us");
  Serial.println("------------------------------");
}

// ===============================
// I2C ERROR CHECK
// ===============================
void checkForI2cErrors() {
  byte errorCode = ina226.getI2cErrorCode();
  if (errorCode) {
    Serial.print("I2C error: ");
    Serial.println(errorCode);
    while (1) {}
  }
}

// ===============================
// PRINT INA226 DATA
// ===============================
void printINA226Data() {
  float shuntVoltage_mV = ina226.getShuntVoltage_mV();
  float busVoltage_V   = ina226.getBusVoltage_V();
  float current_mA     = ina226.getCurrent_mA();
  float power_mW       = ina226.getBusPower();

  checkForI2cErrors();

  Serial.print(millis());
  Serial.print(",");
  Serial.print(currentPulseWidth);
  Serial.print(",");
  Serial.println(current_mA);

  delay(300);
}

// ===============================
// MOVE SERVO + SAMPLE CURRENT
// ===============================
void moveServoUS(int pulseWidth) {
  // Clamp pulse width
  if (pulseWidth < SERVO_MIN_US) pulseWidth = SERVO_MIN_US;
  if (pulseWidth > SERVO_MAX_US) pulseWidth = SERVO_MAX_US;

  currentPulseWidth = pulseWidth;

  Serial.print("Moving servo (us): ");
  Serial.println(currentPulseWidth);

  myservo.writeMicroseconds(currentPulseWidth);

  // Sample INA226 for 1 second AFTER movement
  unsigned long start = millis();
  while (millis() - start < 1000) {
    printINA226Data();
  }
}

// ===============================
// LOOP
// ===============================
void loop() {

  if (Serial.available()) {
    char cmd = Serial.read();

    switch (cmd) {

      case '0':
        Serial.println("Command 0 → Fully bent");
        moveServoUS(SERVO_MIN_US);
        break;

      case '1':
        Serial.println("Command 1 → Mid position");
        moveServoUS(1450);
        break;

      case '2':
        Serial.println("Command 2 → Fully straight");
        moveServoUS(SERVO_MAX_US);
        break;

      case '3':
        Serial.println("Command 3 → Step towards bent (-100 us)");
        moveServoUS(currentPulseWidth - SERVO_STEP);
        break;

      case '4':
        Serial.println("Command 4 → Step towards straight (+100 us)");
        moveServoUS(currentPulseWidth + SERVO_STEP);
        break;

      default:
        Serial.println("Invalid command. Use 0–4.");
        break;
    }

    Serial.println("Enter next command:");
  }
}
