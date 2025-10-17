# 🟦 STM32 FSR Force Measurement — RFP602 Thin Film Pressure Sensor

This example demonstrates how to measure **force in percentage** using a **Force Sensitive Resistor (FSR)** connected to a **WeAct Black Pill V3.0 (STM32F401CEU6)**. The output prints both the FSR resistance and the corresponding force in percentage.

The sensor used is the [RFP602 500g Thin Film Pressure Sensor](https://tronic.lk/product/rfp602-500g-thin-film-pressure-sensor).

---

## 🔧 Hardware Connections

| STM32 Pin | Sensor Connection | Notes |
|------------|-----------------|-------|
| A0         | FSR signal       | Analog input to read voltage |
| GND        | GND              | Common ground |
| 3.3V       | VCC              | Power to FSR (if required) |

**Series Resistor:** 10 kΩ used in voltage divider with FSR.

---

## 💻 Code

```cpp
#include <Arduino.h>

const int FSR_pin = A0;        // ADC pin
const int avg_size = 10;       // number of readings to average
const float R_0 = 10000.0;     // series resistor: 10kΩ
const float Vcc = 3.3;         // STM32 ADC reference voltage
const float Vout_min = 0.01;   // clamp voltage to avoid division by zero

// Set experimentally based on observed max/min readings
float R_FSR_max = 3290000.0;   // no press (~3.29 MΩ)
float R_FSR_min = 32000.0;     // maximum press (~32 kΩ)

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

  delay(30000); // 30 seconds
}
```

---

## 🧠 What the Code Does

1. **Initializes Serial Communication**  
   Starts UART communication at **115200 baud**.

2. **Reads Analog Values**  
   Samples the FSR voltage **10 times** and averages the readings.

3. **Calculates FSR Resistance**  
   Uses a voltage divider formula:  
   `R_FSR = R_0 * (Vcc / Vout - 1.0)`

4. **Maps Resistance to Force (%)**  
   Converts resistance into a percentage of applied force using the observed `R_FSR_max` and `R_FSR_min`.

5. **Clamps Values**  
   Ensures voltage and force percentage stay within safe bounds.

6. **Prints Results**  
   Outputs resistance in ohms and force percentage to the Serial Monitor every **30 seconds**.

---

## ⚙️ PlatformIO Setup

1. Open the project folder in **PlatformIO**.
2. Connect your **WeAct Black Pill V3.0** to the PC via ST-Link or USB.
3. Upload the code using:  
   `PlatformIO: Upload`
4. Open the **Serial Monitor** using:  
   `PlatformIO: Monitor`
5. Set the baud rate to **115200**.

You should see output similar to:

```
--- Opened the serial port /dev/ttyUSB0 ----
R_FSR: 3290000.00 Ω, Force: 98.4 %
R_FSR: 35188.70 Ω, Force: 100.0 %
R_FSR: 3290000.00 Ω, Force: 98.4 %
--- Closed the serial port /dev/ttyUSB0 ----
```

> ✅ Note: The maximum FSR resistance observed experimentally is **3.29 MΩ**, so `R_FSR_max` is set to 3290000.0 Ω.

---

## ✅ Summary

| Parameter | Description |
|-----------|-------------|
| **Board** | WeAct Black Pill V3.0 (STM32F401CEU6) |
| **Sensor** | RFP602 500g Thin Film Pressure Sensor |
| **ADC Pin** | A0 |
| **Reference Voltage** | 3.3 V |
| **Series Resistor** | 10 kΩ |
| **Baud Rate** | 115200 |
| **Measurement Interval** | 30 seconds |
| **Output** | FSR resistance (Ω) and force (%) |

---

✨ _This setup allows monitoring of applied force via FSR on STM32 using PlatformIO._