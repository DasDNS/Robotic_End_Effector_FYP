#include <Arduino.h>

const int FSR_pin = A0;    // ADC pin
const int avg_size = 10;   // number of readings to average
const float R_0 = 10000.0; // 10k resistor
const float Vcc = 3.3;     // STM32 ADC reference

void setup() {
  Serial.begin(115200); // STM32: 115200 is more reliable
}

void loop() {
  float sum_val = 0.0;
  for (int i = 0; i < avg_size; i++) {
    sum_val += (analogRead(FSR_pin) / 4095.0) * Vcc;
    delay(10);
  }
  float Vout = sum_val / avg_size;
  float R_FSR = R_0 * (Vcc / Vout - 1.0);

  Serial.println(R_FSR); // resistance in ohms
  delay(30000); //30 seconds = 0.5 min
}
