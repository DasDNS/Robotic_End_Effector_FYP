# 🟦 STM32 FSR Sensor — Force Measurement with Serial Plotter

This example demonstrates reading a **Force Sensitive Resistor (FSR)** using a **WeAct Black Pill V3.0 (STM32F401CEU6)** and plotting the FSR resistance and force percentage in real-time using the **PlatformIO Serial Plotter extension**.

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
float R_FSR_min = 32000.0;     // max press (~32 kΩ)

void setup() {
  Serial.begin(115200); // Match VS Code Serial Plotter
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

  // Send data for Serial Plotter
  Serial.print(">R_FSR:");
  Serial.print(R_FSR, 2);          // plot raw resistance
  Serial.print(",Force:");
  Serial.println(force_percent, 2); // plot normalized force
}
```

---

## 🧠 What the Code Does

1. **Initializes Serial Communication**  
   Starts UART communication at **115200 baud**.

2. **Averages ADC Readings**  
   Reads the analog FSR voltage **10 times** and averages to reduce noise.

3. **Calculates FSR Resistance**  
   Uses voltage divider formula:  
   `R_FSR = R_0 * (Vcc / Vout - 1.0)`

4. **Converts Resistance to Force (%)**  
   Maps the measured resistance to a **0-100% scale** based on `R_FSR_max` and `R_FSR_min`.

5. **Clamps Values**  
   Ensures voltage and force percentage stay within safe bounds.

6. **Sends Data for Serial Plotter**  
   Prefix `>` allows the **Serial Plotter extension** to read and plot data continuously.

---

## 🖥️ PlatformIO Serial Plotter Setup

1. Install the **Serial Plotter** extension by Mario Zechner:  
   - **Marketplace:** serial-plotter  
   - [Link](https://marketplace.visualstudio.com/items?itemName=mariozechner.serial-plotter)

2. Open the **Serial Plotter** from the PlatformIO toolbar.
3. Select the correct **COM port** (usually the last connected USB-to-STM32 device).
4. Set baud rate to **115200**.
5. The plotter will display **R_FSR** and **Force** in real-time.

---

## 📈 Example Serial Output

```
--- Opened the serial port /dev/ttyUSB0 ----
R_FSR: 3290000.00 Ω, Force: 0.0 %
R_FSR: 41477.06 Ω, Force: 99.7 %
R_FSR: 3290000.00 Ω, Force: 0.0 %
R_FSR: 105710.66 Ω, Force: 97.7 %
R_FSR: 83750.00 Ω, Force: 98.4 %
R_FSR: 32700.73 Ω, Force: 100.0 %
---- Closed the serial port /dev/ttyUSB0 ----
```

> ✅ Note: The maximum FSR resistance observed experimentally is **3.29 MΩ**, so `R_FSR_max` is set to 3290000.0 Ω.

---

## ✅ Summary

| Parameter | Description |
|-----------|-------------|
| **Board** | WeAct Black Pill V3.0 (STM32F401CEU6) |
| **Sensor** | RFP602 500g Thin Film Pressure Sensor |
| **ADC Pin** | A0 |
| **Series Resistor** | 10 kΩ |
| **Baud Rate** | 115200 |
| **Measurement Interval** | Continuous (every ~50 ms for averaging) |
| **Plotting Tool** | PlatformIO Serial Plotter by Mario Zechner |
| **Output** | Resistance (Ω) and Force (%) plotted in real-time |

---

✨ _Monitor real-time force readings from your FSR sensor on STM32 using PlatformIO Serial Plotter!_

<img width="1920" height="1080" alt="Screenshot from 2025-10-17 16-10-38" src="https://github.com/user-attachments/assets/5ddf4bdf-8960-40c7-a452-207e76a0a6a8" />

<video width="1920" height="1080" controls>
    <source src="https://github.com/user-attachments/assets/0d75ed40-793a-45ee-a326-0e650b0f6932" type="video/mp4">
    Your browser does not support the video tag.
  </video>
  
https://github.com/user-attachments/assets/0d75ed40-793a-45ee-a326-0e650b0f6932

