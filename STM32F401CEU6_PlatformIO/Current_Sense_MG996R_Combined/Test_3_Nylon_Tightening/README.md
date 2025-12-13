# STM32 Black Pill – Servo Control + INA226 Current Monitoring

This project demonstrates how to control a servo motor using **PWM on pin PB13** of the STM32 Black Pill, while simultaneously measuring current consumption using the **INA226 current/voltage sensor** over I2C.

The user can send commands (`0`, `1`, or `2`) through the Serial Monitor to move the servo to preset positions. For each movement, real-time current readings from the INA226 are printed for one second.

---

## 📌 Features

* Control a servo using **PB13 PWM**
* Read current, voltage, and power using **INA226**
* Full **I2C scanning**
* Real-time current monitoring while servo is moving
* Serial commands for easy debugging
* Designed for **STM32 Black Pill + PlatformIO**

---

## 📦 Hardware Requirements

* STM32F103C8T6 **Black Pill**
* Servo motor (SG90/MG996R/etc.)
* INA226 Current/Voltage Sensor
* External power supply for the servo (recommended)
* Common ground between STM32 and servo supply

---

## 📡 Pin Connections

| Component    | STM32 Pin | Notes                   |
| :----------- | :-------- | :---------------------- |
| Servo Signal | **PB13** | PWM output              |
| I2C SDA      | **PB7** | Connected to INA226 SDA |
| I2C SCL      | **PB6** | Connected to INA226 SCL |
| INA226 VCC   | 3.3V      | Power                   |
| INA226 GND   | GND       | Common ground           |

> **⚠️ WARNING:** Do NOT power the servo from the STM32 3.3V pin. Use an external 5V supply.

---

## 📁 Required Libraries (PlatformIO)

Add these to your `platformio.ini`:

```ini
lib_deps =
    madhephaestus/ESP32Servo@^3.0.9
    wenjuno/INA226_WE
    
> **Note:** The Servo library is used because STM32 supports the generic Servo class through Arduino Core.

---
```

## ▶️ How the Code Works

### 1. Startup
* Initialize serial at 115200
* Configure I2C pins PB7 (SDA) and PB6 (SCL)
* Scan I2C bus for devices
* Initialize INA226
* Attach servo to PB13
* Wait for user input

### 2. Servo Control
The user enters:
* `0` → 500 µs → Fully bent
* `1` → 1450 µs → Half bent
* `2` → 2400 µs → Fully straight

### 3. Current Monitoring
For 1 second after each movement:
* Print `Current[mA]` readings from INA226

---

## 📜 Full Serial Monitor Output
```

=== STM32 Black Pill: Servo (PB13) + INA226 Test ===
Scanning I2C bus...
Found device at 0x40
INA226 found. Initializing...
Servo attached to PB13.

Enter 0, 1, or 2 to move the servo:
---- Sent utf8 encoded message: "0" ----
Command 0 → Fully bent position
Moving servo (us): 500
Current[mA]: 0.10

Current[mA]: 0.12

Current[mA]: 0.10

Current[mA]: 0.10

Enter next command:
---- Sent utf8 encoded message: "1" ----
Command 1 → Half bent (midpoint)
Moving servo (us): 1450
Current[mA]: 0.10

Current[mA]: 0.08

Current[mA]: 0.10

Current[mA]: 0.10

Enter next command:
---- Sent utf8 encoded message: "2" ----
Command 2 → Fully straightened
Moving servo (us): 2400
Current[mA]: 0.10

Current[mA]: 0.10

Current[mA]: 0.10

Current[mA]: 0.10

Enter next command:
---- Closed serial port /dev/ttyUSB0 due to disconnection from the machine ----
```

