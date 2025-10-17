# 🟦 STM32 FSR Sensor Reading — Thin Film Pressure Sensor Example

This example demonstrates how to read a **Force Sensitive Resistor (FSR)** using the **WeAct Black Pill V3.0 (STM32F401CEU6)** board with **PlatformIO** and Arduino framework.

The chosen sensor is the [RFP602 500g Thin Film Pressure Sensor](https://tronic.lk/product/rfp602-500g-thin-film-pressure-sensor).

---

## 🔧 Hardware Connections

| STM32 Pin | Sensor Connection | Notes |
|------------|-----------------|-------|
| A0         | FSR signal       | Analog input to read voltage |
| GND        | GND              | Common ground |
| 3.3V       | VCC              | Power to FSR (if required) |

**Resistor Value:** 10 kΩ (used in voltage divider with FSR)

---

## 💻 Code

```cpp
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
```

---

## 🧠 What the Code Does

1. **Initializes Serial Communication**  
   Starts UART communication at **115200 baud**.

2. **Reads Analog Values**  
   Samples the FSR voltage **10 times** and averages the readings.

3. **Calculates FSR Resistance**  
   Uses the voltage divider formula to compute the FSR resistance:  
   `R_FSR = R_0 * (Vcc / Vout - 1.0)`

4. **Prints Resistance**  
   Sends the resistance in **ohms** to the Serial Monitor.

5. **Delay Between Measurements**  
   Waits **30 seconds** before the next measurement.

---

## ⚙️ PlatformIO Setup

1. Open the project folder in **PlatformIO**.
2. Connect your **WeAct Black Pill V3.0** to the PC via ST-Link or USB.
3. Upload the code using:  
   `PlatformIO: Upload`
4. Open the **Serial Monitor** using:  
   `PlatformIO: Monitor`
5. Set the baud rate to **115200**.

You should see the resistance values of the FSR printed every **30 seconds**.

---

## ✅ Summary

| Parameter | Description |
|-----------|-------------|
| **Board** | WeAct Black Pill V3.0 (STM32F401CEU6) |
| **Sensor** | RFP602 500g Thin Film Pressure Sensor |
| **ADC Pin** | A0 |
| **Reference Voltage** | 3.3 V |
| **Voltage Divider Resistor** | 10 kΩ |
| **Baud Rate** | 115200 |
| **Measurement Interval** | 30 seconds |
| **Output** | FSR resistance in ohms |

---

✨ _This setup allows you to monitor pressure changes via FSR on the STM32 using PlatformIO!_

<img width="1920" height="1080" alt="Screenshot from 2025-10-17 15-06-35" src="https://github.com/user-attachments/assets/fd3f7853-1f88-436f-a2e4-5dd918f5fcff" />
<img width="1920" height="1080" alt="Screenshot from 2025-10-17 15-08-50" src="https://github.com/user-attachments/assets/07e204ba-de20-4a54-98cd-287dbeed2a58" />
<img width="1920" height="1080" alt="Screenshot from 2025-10-17 15-08-50" src="https://github.com/user-attachments/assets/0b83a96c-c81b-4e2c-b6c0-b8ff99e23944" />
<img width="1920" height="1080" alt="Screenshot from 2025-10-17 15-08-50" src="https://github.com/user-attachments/assets/923c1815-61be-4e77-b624-87b78bbf2bb6" />
