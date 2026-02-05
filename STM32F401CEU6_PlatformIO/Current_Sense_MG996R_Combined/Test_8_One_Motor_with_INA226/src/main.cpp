#include <Arduino.h>
#include <Wire.h>
#include <Servo.h>
#include <INA226_WE.h>

#define PCA9548A_ADDRESS 0x70
#define INA226_ADDRESS   0x40

// ---- Servo (ONE motor)
#define SERVO_PIN     PA8
#define SERVO_MIN_US  500
#define SERVO_MAX_US  2400
#define SERVO_STEP    300

// ---- INA is fixed behind PCA channel 3
#define INA_PCA_CHANNEL 3

INA226_WE ina226(INA226_ADDRESS);
Servo servoMotor;

int currentPulseWidth = 1450;
unsigned long lastPeriodicPrint = 0;

// ===============================
// PCA9548A channel select
// ===============================
void selectPCAChannel(uint8_t channel) {
  Wire.beginTransmission(PCA9548A_ADDRESS);
  Wire.write(1 << channel);
  Wire.endTransmission();
}

// ===============================
// Scan I2C bus (optional, for debug)
// ===============================
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
  if (!foundAny) Serial.println("  (no devices found)");
  Serial.println();
}

// ===============================
// INA presence check at 0x40
// ===============================
bool inaPresentOnCurrentBus() {
  Wire.beginTransmission(INA226_ADDRESS);
  return (Wire.endTransmission() == 0);
}

// ===============================
// I2C error check (same style as your ref code)
// ===============================
void checkForI2cErrors() {
  byte errorCode = ina226.getI2cErrorCode();
  if (errorCode) {
    Serial.print("I2C error: ");
    Serial.println(errorCode);
    while (1) {} // halt
  }
}

// ===============================
// Print INA226 current (ONE sensor, fixed channel 3)
// Format: millis,pulseWidth,current_mA
// ===============================
void printINA226Data() {
  selectPCAChannel(INA_PCA_CHANNEL);

  float current_mA = ina226.getCurrent_mA();
  checkForI2cErrors();

  Serial.print(millis());
  Serial.print(",");
  Serial.print(currentPulseWidth);
  Serial.print(",");
  Serial.print(current_mA);
  Serial.println(" mA");
}

// ===============================
// Move ONE servo and sample current for 1 second
// ===============================
void moveServoUS(int pulseWidth) {
  if (pulseWidth < SERVO_MIN_US) pulseWidth = SERVO_MIN_US;
  if (pulseWidth > SERVO_MAX_US) pulseWidth = SERVO_MAX_US;

  currentPulseWidth = pulseWidth;

  Serial.print("Moving servo PA8 (us): ");
  Serial.println(currentPulseWidth);

  servoMotor.writeMicroseconds(currentPulseWidth);

  unsigned long start = millis();
  while (millis() - start < 1000) {
    printINA226Data();
    delay(300);
  }
}

// ===============================
// Setup
// ===============================
void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("\n=== ONE Servo (PA8) + INA226 on PCA9548A Channel 3 ===");

  // I2C pins for STM32 Black Pill
  Wire.setSDA(PB9);
  Wire.setSCL(PB8);
  Wire.begin();

  // Optional debug scans
  scanI2CBus("[SCAN] Main I2C bus (expect PCA9548A at 0x70)");

  Serial.println("[SCAN] PCA9548A Channel 3");
  selectPCAChannel(INA_PCA_CHANNEL);
  delay(10);
  scanI2CBus("  Devices behind channel 3:");

  // Init INA226 on channel 3 (fixed)
  if (!inaPresentOnCurrentBus()) {
    Serial.println("INA226 NOT FOUND on channel 3. Check wiring / address. Halting.");
    while (1) {}
  }

  Serial.println("INA226 found on channel 3. Initializing...");
  if (!ina226.init()) {
    Serial.println("INA226 init FAILED on channel 3. Halting.");
    while (1) {}
  }
  Serial.println("INA226 init OK on channel 3!");
  ina226.waitUntilConversionCompleted();

  // Servo setup (ONE motor)
  servoMotor.attach(SERVO_PIN);
  servoMotor.writeMicroseconds(currentPulseWidth);
  Serial.println("Servo attached on PA8.");

  Serial.println("\nCommands:");
  Serial.println("0 → Fully bent");
  Serial.println("1 → Mid position");
  Serial.println("2 → Fully straight");
  Serial.println("3 → Step -300 us");
  Serial.println("4 → Step +300 us");
  Serial.println("------------------------------");
  Serial.println("Enter command:");
}

// ===============================
// Loop
// ===============================
void loop() {
  if (Serial.available()) {
    char cmd = Serial.read();

    switch (cmd) {
      case '0': moveServoUS(SERVO_MIN_US); break;
      case '1': moveServoUS(1450); break;
      case '2': moveServoUS(SERVO_MAX_US); break;
      case '3': moveServoUS(currentPulseWidth - SERVO_STEP); break;
      case '4': moveServoUS(currentPulseWidth + SERVO_STEP); break;
      case '\n':
      case '\r':
        break;
      default:
        Serial.println("Invalid command. Use 0–4.");
        break;
    }

    Serial.println("Enter next command:");
  }

  if (millis() - lastPeriodicPrint >= 1000) {
    lastPeriodicPrint = millis();
    printINA226Data();
  }
}

