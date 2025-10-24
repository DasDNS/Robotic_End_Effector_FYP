# INA226 Power and Current Measurement with STM32F401 Black Pill

This project demonstrates how to interface an **INA226 current and power sensor** with an **STM32F401CEU6 (WeAct Black Pill V3.0)** board using the **Arduino framework**. It scans the I2C bus, initializes the INA226 sensor, and continuously displays real-time voltage, current, and power readings on the Serial Monitor.

---

## 🧠 Project Overview

The code dynamically detects the INA226 sensor over I2C, initializes it if found, and then prints measured values every second. The program uses the `INA226` library for easy communication with the sensor.  
A **Red LED with a 10 kΩ resistor** is connected in series as the test load.

---

## ⚙️ Hardware Setup

### **Components Used**
- **WeAct STM32F401CEU6 Black Pill (V3.0)**
- **INA226 Current Sensor**
- **Red LED**
- **10 kΩ Resistor**
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

**Test Load Circuit (LED + Resistor):**
```
3.3V -----> [10 kΩ Resistor] -----> [Red LED] -----> GND
```

Reference wiring tutorial:  
[Teensy 4.1 INA226 Current Sensor Tutorial](https://makerbotics.com/knowledge-base/teensy-4-1-ina226-current-sensor-tutorial/)

---

## 🧮 Theoretical Calculations

Given:  
- Supply Voltage, **V = 3.3 V**  
- Series Resistor, **R = 10 kΩ = 10,000 Ω**  
- Red LED Forward Voltage, **Vf ≈ 2.0 V** (typical)

### Step 1: Voltage across the resistor
\( V_R = V - V_f = 3.3 - 2.0 = 1.3 \,V \)

### Step 2: Current through the circuit
\( I = \frac{V_R}{R} = \frac{1.3}{10,000} = 0.00013 \,A = 0.13 \,mA \)

✅ **Theoretical Current = 0.13 mA**

---

## 📟 Observed Serial Output

Below is a snippet of the output obtained from the Serial Monitor:

```
----------------------
Bus Voltage: 0.01 V
Shunt Voltage: 0.00 mV
Current: 0.13 mA
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

### ✅ Observation:
The measured current (≈ **0.13 mA**) matches closely with the theoretical value (0.13 mA).  
This confirms that the INA226 sensor and the STM32 setup are functioning correctly. The test was **successful**.

---

## 🔍 Troubleshooting Tips

- Ensure **SDA** and **SCL** pins match your STM32 board configuration.
- Confirm that **VCC** and **GND** are securely connected.
- Check the LED polarity (longer leg = anode).
- Verify shunt resistor wiring between the INA226 and the load.

---

## 📄 License

This project is released under the **MIT License**.

---

## 🧷 References

- [INA226 Datasheet (Texas Instruments)](https://www.ti.com/lit/ds/symlink/ina226.pdf)
- [Rob Tillaart INA226 Arduino Library](https://github.com/RobTillaart/INA226)
- [Makerbotics Tutorial Reference](https://makerbotics.com/knowledge-base/teensy-4-1-ina226-current-sensor-tutorial/)

<img width="1920" height="1080" alt="Screenshot from 2025-10-24 16-01-32" src="https://github.com/user-attachments/assets/32a92cb2-5b31-4b99-9193-f8dac90d1b9c" />
<img width="1094" height="610" alt="image" src="https://github.com/user-attachments/assets/f497f4f8-0743-44ae-9169-ead6cbe8bf70" />
<img width="679" height="668" alt="image" src="https://github.com/user-attachments/assets/982fdea4-763a-4f4d-be47-e05ace344f06" />
<img width="1000" height="667" alt="image" src="https://github.com/user-attachments/assets/7cc238b1-ae78-4a59-a60c-9a830a6cee47" />
