# 🟦 ESP32 INA226 Current Sensor Example

This example demonstrates how to read **current, voltage, and power** using the **INA226 Current Sensor** with an **ESP32** board. The project is built using **Arduino framework** in **PlatformIO**.

The INA226 sensor used is available here: [INA226 Current & Voltage Sensor Module (20A)](https://tronic.lk/product/ina226-current-voltage-sensor-module-20a?srsltid=AfmBOorYbTJVue1AYEPZS_M6-riRqkakVSS6Vdv143IfBXLlgl2sJXNO).

The **shunt resistor** on the module is labeled **R100**.

---

## 🔧 Hardware Connections

| ESP32 Pin | INA226 Pin | Notes |
|-----------|------------|-------|
| 21        | SDA        | I2C data line |
| 22        | SCL        | I2C clock line |
| 3.3V      | VCC        | Power |
| GND       | GND        | Common ground |

> ⚠️ Make sure VCC and GND are properly connected, and the ESP32 and INA226 share a common ground.

---

## 💻 Code

```cpp
#include <Arduino.h>
#include <Wire.h>
#include <INA226.h>

// Create INA226 object with default I2C address (0x40)
INA226 ina226(0x40);

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Initialize I2C (ESP32 default pins: SDA=21, SCL=22)
  Wire.begin(21, 22);

  Serial.println("Initializing INA226...");

  if (!ina226.begin()) {
    Serial.println("❌ Could not connect to INA226. Check wiring and address.");
    while (1) delay(1000);
  }

  // Configure shunt resistor and maximum expected current
  // Example: shunt = 0.1 ohm, expect up to 0.02 A (20 mA)
  ina226.setMaxCurrentShunt(0.02, 0.1);

  Serial.println("✅ INA226 Initialized Successfully!");
}

void loop() {
  float busVoltage = ina226.getBusVoltage();
  float shuntVoltage = ina226.getShuntVoltage_mV();
  float current_mA = ina226.getCurrent_mA();
  float power_mW = ina226.getPower_mW();

  Serial.print(">BusV:");
  Serial.print(busVoltage, 3);
  Serial.print(",ShuntV_mV:");
  Serial.print(shuntVoltage, 3);
  Serial.print(",Current_mA:");
  Serial.print(current_mA, 3);
  Serial.print(",Power_mW:");
  Serial.println(power_mW, 3);

  delay(2000);
}
```

---

## 🧠 What the Code Does

1. **Initializes Serial Communication**  
   Starts communication at **115200 baud** for serial monitor output.

2. **Initializes I2C**  
   Uses default ESP32 pins (`SDA=21`, `SCL=22`) to communicate with INA226.

3. **Checks INA226 Connection**  
   If the sensor is not detected at I2C address `0x40`, it prints an error and stops execution.

4. **Configures the Shunt Resistor**  
   Sets the expected max current and the shunt resistor value (`0.1Ω` corresponding to **R100**).

5. **Reads Measurements Continuously**  
   - **Bus Voltage** (`V`)  
   - **Shunt Voltage** (`mV`)  
   - **Current** (`mA`)  
   - **Power** (`mW`)

6. **Prints Data for Serial Monitor / Plotter**  
   Each reading is prefixed for easy parsing:

```
>BusV:12.345,ShuntV_mV:1.234,Current_mA:10.123,Power_mW:123.456
```

---

## 🖥️ Using Serial Monitor

1. Connect your ESP32 via USB to your computer.  
2. Open the **PlatformIO Serial Monitor** or VS Code Serial Monitor.  
3. Select the **correct COM port**.  
4. Set **baud rate** to `115200`.  
5. You should see output similar to:

```
>BusV:12.345,ShuntV_mV:1.234,Current_mA:10.123,Power_mW:123.456
>BusV:12.346,ShuntV_mV:1.235,Current_mA:10.125,Power_mW:123.460
```

---

## ✅ Summary

| Parameter | Description |
|-----------|-------------|
| **Board** | ESP32 Dev Module |
| **Sensor** | INA226 Current & Voltage Sensor Module (20A) |
| **I2C Pins** | SDA=21, SCL=22 |
| **Shunt Resistor** | R100 (0.1Ω) |
| **Baud Rate** | 115200 |
| **Output** | Bus voltage (V), Shunt voltage (mV), Current (mA), Power (mW) |
| **Library** | INA226 by [Rob Tillaart](https://registry.platformio.org/libraries/robtillaart/INA226) |

---

✨ _Monitor voltage, current, and power from your ESP32 in real-time using the INA226 sensor!_
