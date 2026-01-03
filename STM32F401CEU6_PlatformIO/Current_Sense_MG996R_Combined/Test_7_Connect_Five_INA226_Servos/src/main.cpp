#include <Arduino.h>
#include <Wire.h>
#include <Servo.h>
#include <INA226_WE.h>

// ===============================
// DEFINES & CONSTANTS
// ===============================
#define INA226_ADDRESS   0x40
#define PCA9548A_ADDRESS 0x70

#define SERVO1_PIN PB13
#define SERVO2_PIN PB14
#define SERVO3_PIN PB15
#define SERVO4_PIN PA8
#define SERVO5_PIN PA11

#define SERVO_MIN_US 500
#define SERVO_MAX_US 2400
#define SERVO_STEP   300

// ===============================
// OBJECTS
// ===============================
Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;
Servo servo5;

INA226_WE ina226_1 = INA226_WE(INA226_ADDRESS);
INA226_WE ina226_2 = INA226_WE(INA226_ADDRESS);
INA226_WE ina226_3 = INA226_WE(INA226_ADDRESS);
INA226_WE ina226_4 = INA226_WE(INA226_ADDRESS);
INA226_WE ina226_5 = INA226_WE(INA226_ADDRESS);

// ===============================
// GLOBAL VARIABLES
// ===============================
int currentPulseWidth = 1450;
unsigned long lastPeriodicPrint = 0;

// ===============================
// FUNCTION PROTOTYPES
// ===============================
void selectPCAChannel(uint8_t channel);
void checkForI2cErrors(INA226_WE &sensor);
void printINA226Data();
void moveServoUS(int pulseWidth);

// ===============================
// PCA9548A CHANNEL SELECT
// ===============================
void selectPCAChannel(uint8_t channel) {
  Wire.beginTransmission(PCA9548A_ADDRESS);
  Wire.write(1 << channel);
  Wire.endTransmission();
}

// ===============================
// SETUP
// ===============================
void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("\n=== STM32 Black Pill: 5 Servo + 5 INA226 ===");

  // -------- I2C SETUP (UNCHANGED STYLE) --------
  Wire.setSDA(PB9);
  Wire.setSCL(PB8);
  Wire.begin();

  // -------- INIT INA226 SENSORS --------
  selectPCAChannel(0);
  if (!ina226_1.init()) while (1) {}

  selectPCAChannel(1);
  if (!ina226_2.init()) while (1) {}

  selectPCAChannel(2);
  if (!ina226_3.init()) while (1) {}

  selectPCAChannel(3);
  if (!ina226_4.init()) while (1) {}

  selectPCAChannel(4);
  if (!ina226_5.init()) while (1) {}

  // -------- SERVO SETUP --------
  servo1.attach(SERVO1_PIN);
  servo2.attach(SERVO2_PIN);
  servo3.attach(SERVO3_PIN);
  servo4.attach(SERVO4_PIN);
  servo5.attach(SERVO5_PIN);

  Serial.println("Servos attached to PB13, PB14, PB15, PA8 and PA11.");

  Serial.println("\nCommands:");
  Serial.println("0 → Fully bent");
  Serial.println("1 → Mid position");
  Serial.println("2 → Fully straight");
  Serial.println("3 → Step -300 us");
  Serial.println("4 → Step +300 us");
  Serial.println("------------------------------");
}

// ===============================
// I2C ERROR CHECK
// ===============================
void checkForI2cErrors(INA226_WE &sensor) {
  byte errorCode = sensor.getI2cErrorCode();
  if (errorCode) {
    Serial.print("I2C error: ");
    Serial.println(errorCode);
    while (1) {}
  }
}

// ===============================
// PRINT ALL CURRENTS
// ===============================
void printINA226Data() {
  float c1, c2, c3, c4, c5;

  selectPCAChannel(0);
  c1 = ina226_1.getCurrent_mA();
  checkForI2cErrors(ina226_1);

  selectPCAChannel(1);
  c2 = ina226_2.getCurrent_mA();
  checkForI2cErrors(ina226_2);

  selectPCAChannel(2);
  c3 = ina226_3.getCurrent_mA();
  checkForI2cErrors(ina226_3);

  selectPCAChannel(3);
  c4 = ina226_4.getCurrent_mA();
  checkForI2cErrors(ina226_4);

  selectPCAChannel(4);
  c5 = ina226_5.getCurrent_mA();
  checkForI2cErrors(ina226_5);

  Serial.print(millis());
  Serial.print(",");
  Serial.print(currentPulseWidth);
  Serial.print(",");
  Serial.print("S1=");
  Serial.print(c1);
  Serial.print(" mA, ");
  Serial.print("S2=");
  Serial.print(c2);
  Serial.print(" mA, ");
  Serial.print("S3=");
  Serial.print(c3);
  Serial.print(" mA, ");
  Serial.print("S4=");
  Serial.print(c4);
  Serial.print(" mA, ");
  Serial.print("S5=");
  Serial.print(c5);
  Serial.println(" mA");

  delay(300);
}

// ===============================
// MOVE ALL SERVOS
// ===============================
void moveServoUS(int pulseWidth) {
  if (pulseWidth < SERVO_MIN_US) pulseWidth = SERVO_MIN_US;
  if (pulseWidth > SERVO_MAX_US) pulseWidth = SERVO_MAX_US;

  currentPulseWidth = pulseWidth;

  Serial.print("Moving servos (us): ");
  Serial.println(currentPulseWidth);

  servo1.writeMicroseconds(currentPulseWidth);
  servo2.writeMicroseconds(currentPulseWidth);
  servo3.writeMicroseconds(currentPulseWidth);
  servo4.writeMicroseconds(currentPulseWidth);
  servo5.writeMicroseconds(currentPulseWidth);

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
      case '0': moveServoUS(SERVO_MIN_US); break;
      case '1': moveServoUS(1450); break;
      case '2': moveServoUS(SERVO_MAX_US); break;
      case '3': moveServoUS(currentPulseWidth - SERVO_STEP); break;
      case '4': moveServoUS(currentPulseWidth + SERVO_STEP); break;
      default: Serial.println("Invalid command. Use 0–4."); break;
    }

    Serial.println("Enter next command:");
  }

  if (millis() - lastPeriodicPrint >= 1000) {
    lastPeriodicPrint = millis();
    printINA226Data();
  }
}
