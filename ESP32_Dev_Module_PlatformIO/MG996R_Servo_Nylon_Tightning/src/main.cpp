#include <Arduino.h>
#include <ESP32Servo.h>

/*
0 Completely bending
1 Half bending  ( Tighten the screw for bending up nylon thread )
2 Completely straightning up ( Tighten the screw for straightning up nylon thread )
*/


Servo myServo;
const int servoPin = 18;

void setup() {
  Serial.begin(115200);
  delay(500);

  myServo.setPeriodHertz(50);  // 50 Hz for analog servos
  myServo.attach(servoPin, 500, 2500);  // Calibrate min/max pulse width

  Serial.println("Enter 0, 1, or 2 to move the servo:");
}

void loop() {
  if (Serial.available()) {
    char command = Serial.read();

    switch (command) {
      case '0':
        myServo.writeMicroseconds(500);  // 0 degrees
        Serial.println("Moved to 0 degrees");
        break;

      case '1':
        myServo.writeMicroseconds(1450);  // ~165 degrees midpoint
        Serial.println("Moved to ~165 degrees");
        break;

      case '2':
        myServo.writeMicroseconds(2400);  // ~330 degrees
        Serial.println("Moved to ~330 degrees");
        break;

      default:
        Serial.println("Invalid command. Use 0, 1, or 2.");
        break;
    }
  }
}
