# 🔍 I2C Scanner — STM32 WeAct Black Pill V3.0

This project scans all possible I2C device addresses using an **STM32F401CEU6 (WeAct Black Pill V3.0)** board. </br>

The chosen sensor is the [INA226 Current sensor](https://tronic.lk/product/ina226-current-voltage-sensor-module-20a?srsltid=AfmBOoowLnBBUcmrwyMpIubV5cGhBE0F4dRJ7hqiSbTkmW4U-PZrlO-c).

---

## ⚙️ Hardware Connections

| Signal | STM32 Pin | Description |
|---------|------------|--------------|
| SDA | PB9 | I2C Data line |
| SCL | PB8 | I2C Clock line |
| VCC | 3.3V | Power for the I2C device |
| GND | GND | Common ground |

> ⚠️ Make sure the I2C device is powered at **3.3V** and shares a common ground with the STM32.

---

## 💻 Code

```cpp
#include <Arduino.h>
#include <Wire.h>

void setup() {
  Serial.begin(115200);
  delay(500);
  
  Serial.println("Starting I2C scan on PB9(SDA)/PB8(SCL)...");

  Wire.setSDA(PB9);
  Wire.setSCL(PB8);
  Wire.begin();

  for (byte addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("Found device at 0x");
      Serial.println(addr, HEX);
    }
  }
  
  Serial.println("Scan complete.");
}

void loop() {}
```

---

## 🧠 Explanation

- The code initializes **I2C communication** on pins **PB9 (SDA)** and **PB8 (SCL)**.
- It scans all valid I2C addresses (`0x01` to `0x7E`).
- When a device responds, its address is printed on the **Serial Monitor**.

---

## 🖥️ Output Example

```
Starting I2C scan on PB9(SDA)/PB8(SCL)...
Found device at 0x40
Scan complete.
```

This indicates that an I2C device was successfully detected at address **0x40**.

---

## ✅ Summary

| Parameter | Description |
|------------|-------------|
| **Board** | STM32F401CEU6 (WeAct Black Pill V3.0) |
| **I2C Pins** | SDA = PB9, SCL = PB8 |
| **Baud Rate** | 115200 bps |
| **Power** | 3.3V |
| **Detected Device Address** | 0x40 |

---

📘 **Notes:**  
- The scan output confirms the presence of a device at **I2C address 0x40**.  
- Always double-check pull-up resistors on the SDA and SCL lines if no devices are found.  
- Suitable for quick I2C hardware verification using **PlatformIO** or **Arduino IDE**.

<img width="1920" height="1080" alt="Screenshot from 2025-10-24 12-38-14" src="https://github.com/user-attachments/assets/c5a421d0-93c4-4df7-b19a-83453e4a7449" /> </br>
<img width="1920" height="1080" alt="Screenshot from 2025-10-24 12-38-14" src="https://github.com/user-attachments/assets/a903e6eb-3f84-4281-b2d9-ad1049c4430d" /></br>
<img width="1920" height="1080" alt="Screenshot from 2025-10-24 12-38-14" src="https://github.com/user-attachments/assets/c095b8a1-237f-4ff0-9bc2-777dcdc8b034" />
