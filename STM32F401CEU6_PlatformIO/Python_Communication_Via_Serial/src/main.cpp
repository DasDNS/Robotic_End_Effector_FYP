#include <Arduino.h>

unsigned long previousMillis = 0;
const long interval = 500; // 500 ms

void setup() {
    Serial.begin(115200); // Make sure this matches Python
    while (!Serial); // Wait for serial port to connect (optional for Blackpill)
}

void loop() {
    unsigned long currentMillis = millis();

    // Every 500 ms, print something to Serial Monitor
    if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;
        Serial.println("STM32 says hi!");
    }

    // Check if data is available from Python
    if (Serial.available()) {
        String received = Serial.readStringUntil('\n'); // Read until newline
        Serial.print("Received from Python: ");
        Serial.println(received);
    }
}
