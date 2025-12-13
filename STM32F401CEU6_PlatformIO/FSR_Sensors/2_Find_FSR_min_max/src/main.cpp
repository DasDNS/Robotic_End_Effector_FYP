#include <Arduino.h>

const int FSR_pin = A0;        // ADC pin
const int avg_size = 10;       // number of readings to average
const float R_0 = 10000.0;     // series resistor: 10kΩ
const float Vcc = 3.3;         // STM32 ADC reference voltage
const float Vout_min = 0.01;   // clamp voltage to avoid division by zero

// Set these experimentally
float R_FSR_max = 200000000.0; // no press (~200MΩ)
float R_FSR_min = 32000.0;     // maximum press (~32kΩ)

void setup() {
  Serial.begin(115200);
}

void loop() {
  float sum_val = 0.0;

  // Average multiple ADC readings
  for (int i = 0; i < avg_size; i++) {
    sum_val += analogRead(FSR_pin);
    delay(5);
  }
  float adc_avg = sum_val / avg_size;

  // Convert ADC to voltage
  float Vout = (adc_avg / 4095.0) * Vcc;

  // Clamp voltage
  if (Vout < Vout_min) Vout = Vout_min;

  // Calculate FSR resistance
  float R_FSR = R_0 * (Vcc / Vout - 1.0);

  // Map resistance to 0-100% force
  float force_percent = (R_FSR_max - R_FSR) / (R_FSR_max - R_FSR_min) * 100.0;

  // Clamp force between 0-100%
  if (force_percent < 0) force_percent = 0;
  if (force_percent > 100) force_percent = 100;

  // Print results
  Serial.print("R_FSR: ");
  Serial.print(R_FSR, 2);
  Serial.print(" Ω, Force: ");
  Serial.print(force_percent, 1);
  Serial.println(" %");

  delay(30000); 30 seconds
}

