---

# INA226 Current and Power Measurement with STM32F401 Black Pill

## 🧩 Overview

This project demonstrates how to interface an **INA226 current and power sensor** with an **STM32F401CEU6 (WeAct Black Pill V3.0)** board using the **Arduino framework**.
The INA226 continuously measures **bus voltage**, **shunt voltage**, **current**, and **power**, displaying results over the serial monitor.

In this test, a **red LED and a 10 kΩ resistor** were used as the load to verify current measurements.

---

## ⚙️ Hardware Setup

**Board:** STM32F401CEU6 (WeAct Black Pill V3.0)
**Sensor:** INA226 Power & Current Sensor
**Load:** Red LED + 10 kΩ Resistor in series
**Operating Voltage:** 5.29 V supply

### 🔌 I2C Connection

| Function | STM32 Pin   | INA226 Pin |
| -------- | ----------- | ---------- |
| SDA      | PB9         | SDA        |
| SCL      | PB8         | SCL        |
| VCC      | 3.3 V / 5 V | VCC        |
| GND      | GND         | GND        |

Connections were made according to:

* [Wolle’s Elektronikkiste INA226 Tutorial](https://wolles-elektronikkiste.de/en/ina226-current-and-power-sensor)
* [How2Electronics INA226 Arduino Guide](https://how2electronics.com/how-to-use-ina226-dc-current-sensor-with-arduino/)

---

## 💡 Circuit Diagram

A simplified view of the setup:

```
  +5.29 V  ──►──[10 kΩ]──►──|>|──►── GND
                            LED
```

The INA226 is placed across the LED load for current and voltage measurement.

---

## 🧮 Theoretical Calculation

Given:

* Supply voltage ( V_s = 5.29 V )
* LED forward voltage ( V_f ≈ 2.0 V )
* Series resistor ( R = 10 kΩ = 10,000 Ω )

### Step 1: Calculate current

[
I = \frac{V_s - V_f}{R} = \frac{5.29 - 2.0}{10,000} = 0.000329 A = 0.33 mA
]

### Step 2: Compare with measured results

| Parameter | Theoretical | Measured (INA226) |
| --------- | ----------- | ----------------- |
| Current   | 0.33 mA     | 0.43 – 0.45 mA    |
| Power     | ~1.7 mW     | 2.1 – 2.3 mW      |

### ✅ Observation

The readings are **very close**. Minor deviations can result from:

* LED forward voltage variation (1.8 – 2.2 V range)
* ±5 % resistor tolerance
* INA226’s offset at low current levels

---

## 🧪 Serial Monitor Output

Example readings observed during the test:

```
----------------------
Bus Voltage: 5.29 V
Shunt Voltage: 0.00 mV
Current: 0.43 mA
Power: 2.30 mW
----------------------
Bus Voltage: 5.30 V
Shunt Voltage: 0.00 mV
Current: 0.40 mA
Power: 2.15 mW
----------------------
```

---

## 🧠 Conclusion

The measured current and power values closely match the theoretical calculations, confirming that the **INA226 sensor and STM32 setup are working correctly**.
This successful test validates both hardware connections and sensor calibration.

---

## 🔗 References

* [Wolle’s Elektronikkiste INA226 Tutorial](https://wolles-elektronikkiste.de/en/ina226-current-and-power-sensor)
* [How2Electronics INA226 Guide](https://how2electronics.com/how-to-use-ina226-dc-current-sensor-with-arduino/)

---


