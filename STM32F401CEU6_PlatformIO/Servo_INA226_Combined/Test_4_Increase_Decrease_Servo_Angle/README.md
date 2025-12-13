# STM32 Black Pill – Servo Control with INA226 Current Monitoring

## 📌 Project Overview

This project demonstrates **precise servo motor control** using an **STM32 Black Pill** while **monitoring motor current in real time** via an **INA226 current sensor**.

It is designed for **grasp control, force analysis, and experimental robotics applications**, where servo position and motor current are tightly coupled.

The firmware is developed using **PlatformIO (Arduino framework)**.

---

## ✅ Features Implemented (IMPORTANT)

The following command-based servo control features are implemented and emphasized:

| Command | Action |
|-------|--------|
| **0** | Jump → **Fully bent** position (**500 µs**) |
| **1** | Jump → **Mid position** (**1450 µs**) |
| **2** | Jump → **Fully straight** position (**2400 µs**) |
| **3** | **Step −100 µs** (bend gradually, fine control) |
| **4** | **Step +100 µs** (straighten gradually, fine control) |

🔹 Commands **3** and **4** allow **incremental motion**, enabling smooth, controlled transitions from fully straightened to fully bent positions.

🔹 After **every servo movement**, the **INA226 current is sampled for 1 second**, ensuring accurate post-movement current measurement.

---

## 🧠 Why This Matters

- Enables **soft → hard → stable grasp analysis**
- Motor current acts as a **proxy for grip force**
- Ideal for **FYPs, robotics labs, and prosthetic hand research**
- Fully **non-AI**, deterministic, and exam-safe

---

## 🧰 Hardware Requirements

- STM32 Black Pill (STM32F103C8 / STM32F411)
- Standard RC Servo Motor
- INA226 Current & Voltage Sensor Module
- External power supply for servo
- Common GND between STM32, INA226, and servo
- I2C Pull-up resistors (usually on INA226 module)

---

## 🔌 Pin Configuration

| Function | STM32 Pin |
|-------|----------|
| Servo PWM | `PB13` |
| I2C SDA | `PB7` |
| I2C SCL | `PB6` |

---

## ⚙️ Software Requirements

- PlatformIO
- Arduino framework for STM32
- Required libraries:
  - `Servo`
  - `Wire`
  - `INA226_WE`

---

## ▶️ How to Use

1. Build and upload the firmware using PlatformIO
2. Open the **Serial Monitor** at **115200 baud**
3. Enter commands `0` to `4`
4. Observe:
   - Servo movement
   - Motor current readings printed after each movement

---

## 📊 Example Serial Output

```
Moving servo (us): 2400
Current [mA]: 82.1
Current [mA]: 83.4
Current [mA]: 85.0
```

---

## 📁 File Structure

```
project-root/
├── src/
│   └── main.cpp
├── platformio.ini
└── README.md
```

---

