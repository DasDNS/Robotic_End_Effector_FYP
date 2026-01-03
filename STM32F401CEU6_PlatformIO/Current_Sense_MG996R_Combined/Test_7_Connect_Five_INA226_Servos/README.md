# STM32 Black Pill – 5 Servo Motors with INA226 Current Monitoring

This project demonstrates how to control **five servo motors** using an **STM32 Black Pill** while **monitoring the current consumption of each servo motor** using **five INA226 current sensors** connected via a **PCA9548A I2C multiplexer**.

This setup is intended for **robotic hand / adaptive grasping experiments**, where motor current is used as a proxy for contact and load detection.

---

## Hardware Used

- **MCU**: STM32 Black Pill (STM32F401 / STM32F411)
- **Servo Motors**: 5 × RC servos (e.g., MG996R)
- **Current Sensors**: 5 × INA226
- **I2C Multiplexer**: PCA9548A
- **Power Supply**: External 5V high-current SMPS
- **Logic Level**: 3.3V (STM32)

> ⚠️ Servos must NOT be powered from the STM32 board.

---

## Pin Mapping

### Servo PWM Pins

| Servo | STM32 Pin |
|------|----------|
| Servo 1 | PB13 |
| Servo 2 | PB14 |
| Servo 3 | PB15 |
| Servo 4 | PA8 |
| Servo 5 | PA11 |

### I2C Pins

| Signal | STM32 Pin |
|-------|-----------|
| SDA | PB9 |
| SCL | PB8 |

---

## System Overview

- All INA226 sensors share the same I2C address (`0x40`)
- A **PCA9548A** I2C multiplexer is used to isolate each INA226 on a separate channel
- Each servo’s **power line passes through its own INA226**, enabling:
  - Per-servo current monitoring
  - Contact detection
  - Stall / overload detection
- Servo motion and current sensing run together for synchronized control and feedback

---

## Required Libraries

Install the following Arduino libraries:

- `Servo`
- `Wire`
- `INA226_WE` by Wolfgang Ewald

Compatible with **Arduino Core for STM32**.

---

## Serial Commands

| Command | Action |
|-------|--------|
| `0` | Move all servos to minimum position (500 µs) |
| `1` | Move all servos to mid position (1450 µs) |
| `2` | Move all servos to maximum position (2400 µs) |
| `3` | Decrease pulse width by 300 µs |
| `4` | Increase pulse width by 300 µs |

---


---

## Power & Decoupling Recommendations

- Use a **common ground** between SMPS, INA226 sensors, and STM32
- Recommended capacitors:
  - **1000 µF + 0.1 µF** near the 5V SMPS
  - **470 µF + 0.1 µF** near the servo power distribution / INA226 inputs
- Use **wide traces or multiple ground pins** for high-current paths

---

## Application Notes

This architecture is suitable for:

- Robotic hand grasp detection
- Current-based contact sensing
- Stable grasp detection
- Feedforward + feedback control experiments

---

## Known Limitations

- Uses blocking `delay()` and `while()` loops
- Not yet real-time or RTOS-safe
- Intended for bench testing and experimentation

---

## Future Improvements

- Replace blocking delays with `millis()`
- Add per-servo current thresholds
- Implement grasp-state machine
- Integrate tactile (FSR) sensing
- Closed-loop grip force control

---



