#include <Arduino.h>
#include <Servo.h>

Servo myservo;

void setup() {
  myservo.attach(PA8);  // use a PWM-capable pin (example)
}

void loop() {
  myservo.write(0);   // move to 0°
  delay(1000);
  myservo.write(90);  // move to 90°
  delay(1000);
  myservo.write(180);   // move to 180°
  delay(1000);
  myservo.write(90);  // move to 90°
  delay(1000);
}