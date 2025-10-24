# INA226 Power and Current Measurement with STM32F401 Black Pill

This project demonstrates how to interface an **INA226 current and power sensor** with an **STM32F401CEU6 (WeAct Black Pill V3.0)** board using the **Arduino framework**. It scans the I2C bus, initializes the INA226 sensor, and continuously displays real-time voltage, current, and power readings on the Serial Monitor.

---

## 🧠 Project Overview

The code dynamically detects the INA226 sensor over I2C, initializes it if found, and then prints measured values every second. The program uses the `INA226` library for easy communication with the sensor.

---

## ⚙️ Hardware Setup

### **Components Used**
- **WeAct STM32F401CEU6 Black Pill (V3.0)**
- **INA226 Current Sensor**
- **Connecting Wires**
- **USB Cable for Serial Monitoring**

### **Wiring**

| INA226 Pin | STM32 Pin | Description |
|-------------|------------|--------------|
| **VCC** | 3.3V | Power supply |
| **GND** | GND | Common ground |
| **SDA** | PB9 | I2C Data |
| **SCL** | PB8 | I2C Clock |

> **Note:** PB8 and PB9 are the dedicated I2C pins on the STM32F401CEU6 (I2C1).

Reference tutorial for wiring:  
[Teensy 4.1 INA226 Current Sensor Tutorial](https://makerbotics.com/knowledge-base/teensy-4-1-ina226-current-sensor-tutorial/)

---

## 🧰 Software Requirements

- **PlatformIO** or **Arduino IDE**
- **INA226 Library by Rob Tillaart**  
  *(Available via Library Manager or from [GitHub](https://github.com/RobTillaart/INA226))*
- **STM32duino Core** installed

---

## 🧾 Code Description

The sketch first scans all possible I2C addresses (1–127) and looks for the INA226 device at address `0x40`. Once detected, it initializes the sensor and starts printing:

- Bus Voltage (V)
- Shunt Voltage (mV)
- Current (mA)
- Power (mW)

### **Main Code Snippet**

```cpp
ina = new INA226(0x40, &Wire);
ina->setMaxCurrentShunt(0.02, 0.1);  // 0.02Ω shunt, 0.1A max current
if (!ina->begin()) {
  Serial.println("Failed to initialize INA226!");
  while (1);
}
```

---

## 📟 Sample Output

Below is a snippet of the serial output observed during operation:

```
----------------------
Bus Voltage: 0.01 V
Shunt Voltage: 0.00 mV
Current: 0.10 mA
Power: 0.00 mW
----------------------
Bus Voltage: 0.01 V
Shunt Voltage: 0.00 mV
Current: 0.15 mA
Power: 0.00 mW
----------------------
Bus Voltage: 0.01 V
Shunt Voltage: 0.00 mV
Current: 0.13 mA
Power: 0.00 mW
----------------------
```

The INA226 successfully responds on the I2C bus and provides consistent but very low readings (near zero). This typically indicates that:

- The shunt resistor or measurement load is not drawing significant current, **or**
- The wiring to the shunt resistor is reversed or not connected properly.

---

## 🔍 Troubleshooting Tips

- Ensure **SDA** and **SCL** pins match your STM32 board configuration.
- Confirm that **VCC** and **GND** are securely connected.
- Check the shunt resistor connections and polarity.
- Use a known load (e.g., LED or resistor) across the measurement side of INA226.
- Verify the **I2C address** using the scanner output (`0x40` default).

---

## 🧪 Future Improvements

- Calibrate readings based on your exact shunt resistor value.
- Add data averaging and filtering.
- Display results on an OLED or LCD display.
- Publish readings to MQTT or an IoT dashboard.

---

## 📄 License

This project is released under the **MIT License**.

---

## 🧷 References

- [INA226 Datasheet (Texas Instruments)](https://www.ti.com/lit/ds/symlink/ina226.pdf)
- [Rob Tillaart INA226 Arduino Library](https://github.com/RobTillaart/INA226)
- [Makerbotics Tutorial Reference](https://makerbotics.com/knowledge-base/teensy-4-1-ina226-current-sensor-tutorial/)

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/20d667ee-0461-4e88-aadd-4e708ff6fd31" />

