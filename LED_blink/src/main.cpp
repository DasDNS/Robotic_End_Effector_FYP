#include <Arduino.h>

#define LED_PIN PC13

// put function declarations here:

void setup() {
  // put your setup code here, to run once:
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  digitalWrite(PC13, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(1000);              // wait for a second
  digitalWrite(PC13, LOW);    // turn the LED off by making the voltage low
  delay(1000);              // wait for a second
}

// put function definitions here:
int myFunction(int x, int y) {
  return x + y;
}