#include <Arduino.h>
#include <Wire.h>
#include <Servo.h>
#include <INA226.h>

// ====== Objects ======
Servo myservo;
INA226 *ina = nullptr;

// ====== Pin Definitions ======
#define SERVO_PIN PB13
#define SDA_PIN PB9
#define SCL_PIN PB8

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\n=== MG996R Servo + INA226 Current Sensor Test ===");

  // Initialize I2C
  Wire.setSDA(SDA_PIN);
  Wire.setSCL(SCL_PIN);
  Wire.begin();

  // ====== Scan for I2C Devices ======
  Serial.println("Scanning I2C bus...");
  bool found = false;
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("Found I2C device at 0x");
      Serial.println(addr, HEX);
      if (addr == 0x40) found = true; // INA226 default address
    }
  }

  // ====== Initialize INA226 ======
  if (found) {
    Serial.println("INA226 detected! Initializing...");
    ina = new INA226(0x40, &Wire);
    ina->setMaxCurrentShunt(0.02, 0.1); // 0.02Ω shunt, 0.1A max (adjust if needed)
    if (!ina->begin()) {
      Serial.println("INA226 initialization failed!");
      while (1);
    }
    Serial.println("INA226 initialized successfully!");
  } else {
    Serial.println("INA226 not found on I2C bus.");
  }

  // ====== Attach Servo ======
  myservo.attach(SERVO_PIN);
  Serial.println("Servo attached to PB13.");
  delay(1000);
}

void printINA226Data() {
  if (!ina) return;
  
  float busVoltage = ina->getBusVoltage();      // in V
  float shuntVoltage = ina->getShuntVoltage();  // in mV
  float current_mA = ina->getCurrent_mA();      // in mA
  float power_mW = ina->getPower_mW();          // in mW

  Serial.print("Bus Voltage: "); Serial.print(busVoltage); Serial.println(" V");
  Serial.print("Shunt Voltage: "); Serial.print(shuntVoltage); Serial.println(" mV");
  Serial.print("Current: "); Serial.print(current_mA); Serial.println(" mA");
  Serial.print("Power: "); Serial.print(power_mW); Serial.println(" mW");
  Serial.println("----------------------------");
}

void moveServoAndMeasure(int angle, int waitMs) {
  Serial.print("Moving servo to "); Serial.print(angle); Serial.println("°");
  myservo.write(angle);
  unsigned long start = millis();
  while (millis() - start < waitMs) {
    printINA226Data();
    delay(500); // read every 0.5s
  }
}

void loop() {
  if (!ina) {
    Serial.println("INA226 not initialized. Check wiring.");
    delay(2000);
    return;
  }

  moveServoAndMeasure(0, 3000);
  moveServoAndMeasure(180, 3000);
  moveServoAndMeasure(90, 3000);
}
