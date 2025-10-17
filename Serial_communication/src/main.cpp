#include <Arduino.h>

void setup() {
  // Start the Serial communication
  Serial.begin(115200);

  // Wait for the serial port to connect (necessary for some boards)
  while (!Serial) {
    ; // Wait
  }
}

void loop() {
  // Print a message to the Serial Monitor
  Serial.println("Hello, Blue Pill!");

  // Wait for 1 second
  delay(1000);
}



