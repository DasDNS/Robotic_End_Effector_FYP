# STM32 Black Pill – Servo Current Monitoring with INA226

## Overview

This project demonstrates **real-time current monitoring of a servo motor** using an **INA226 current sensor** and an **STM32 Black Pill (STM32F401)** board.

The system is designed for **robotic hand / grasp analysis**, where **servo motor current spikes** are used to infer:
- Initial contact
- Increasing load
- Stable grasp
- Load removal

The firmware allows:
- Manual servo positioning via serial commands
- Automatic, periodic current reporting every second
- High-rate current sampling immediately after servo movement

---

## Hardware Used

- STM32 Black Pill (STM32F401)
- MG996R Servo Motor
- INA226 Current Sensor
- External 5 V power supply for servo
- Shunt resistor (per INA226 configuration)

---

## Pin Configuration

| Signal | Pin |
|------|-----|
| Servo PWM | PB13 |
| I2C SDA | PB7 |
| I2C SCL | PB6 |
| INA226 I2C Address | `0x40` |

---

## Serial Commands

| Command | Action |
|-------|-------|
| `0` | Fully bent |
| `1` | Mid position |
| `2` | Fully straight |
| `3` | Step −100 µs |
| `4` | Step +100 µs |

---

## Serial Output Format

Current data is printed in **CSV format**:

```
<timestamp_ms>,<servo_pulse_width_us>,<current_mA>
```

Example:
```
148418,500,52.08
```

---

## Complete Serial Monitor Output (Captured)

```
Command 0 → Fully bent
Moving servo (us): 500
148418,500,52.08
148719,500,261.83
149020,500,470.40
149321,500,744.72
Enter next command:
149623,500,375.50
150623,500,327.38
151623,500,329.08
152623,500,329.08
153623,500,328.38
154623,500,328.73
155623,500,24.12
156623,500,54.63
157623,500,54.93
158623,500,54.78
159623,500,54.65
160623,500,54.85
161623,500,53.47
162623,500,53.43
163623,500,53.20
```

---

## Interpretation of the Current Profile

When the servo was **fully bent**:

- The fingertip was pressed against an external load.
- The current increased rapidly, reaching **744 mA** at peak contact.
- While the load was maintained, the current stabilized around **~300 mA**.
- Once the load was removed, the current dropped back to the idle level of **~53 mA**.

This clearly demonstrates how **motor current can be used to detect grasp contact, load holding, and release** without a force sensor.

---

## Key Features

- Continuous current monitoring (idle and active)
- High-resolution grasp event visibility
- CSV-style logging for plotting and analysis
- Suitable for multi-finger robotic hand expansion

---

## Intended Use

This firmware is intended for:
- Robotic hand grasp detection
- Embedded systems experimentation
- Research and academic projects

---

