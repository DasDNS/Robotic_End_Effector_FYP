# FSR Auto-Save System (STM32 Blackpill)

This project implements an **automatic stability detection and data capture system** for **Force Sensitive Resistors (FSRs)** using an **STM32F401 Blackpill** board and the **Arduino framework**.

The system continuously reads multiple FSR sensors, computes averaged values, detects when the readings become stable, and automatically saves a snapshot of the sensor data.

---

## ✨ Features

- Supports **9 FSR sensors**
- Uses **oversampling + averaging** for noise reduction
- Automatic **stability detection**
- **Auto-save** when readings remain stable for a defined duration
- Prints **live sensor values** with corresponding **MCU pin names**
- Serial output suitable for **logging, plotting, or CSV parsing**

---

## 🧠 How It Works

1. Each FSR is sampled multiple times (`samples`).
2. The average value is calculated for each sensor.
3. The current averages are compared with the previous cycle.
4. If all sensors stay within a defined `threshold` for a number of cycles:
   - The system automatically **saves the data**
5. Live data is continuously printed over Serial.

---

## 🔌 Hardware Setup

### Microcontroller
- **STM32F401 Blackpill**
- Arduino Core for STM32

### FSR Connections

| FSR | MCU Pin |
|----|--------|
| FSR 1 | PB0 |
| FSR 2 | PA7 |
| FSR 3 | PA6 |
| FSR 4 | PA5 |
| FSR 5 | PA4 |
| FSR 6 | PA3 |
| FSR 7 | PA2 |
| FSR 8 | PA1 |
| FSR 9 | PA0 |

Each FSR is typically used in a **voltage divider** configuration with a fixed resistor (e.g., 10 kΩ).

---

## ⚙️ Configuration Parameters

You can tune the system behavior using these constants:

```cpp
#define NUM_SENSORS 9

const int samples = 80;            // Samples per sensor per cycle
const int delay_ms = 3;            // Delay between samples
const float threshold = 15.0;      // Stability threshold
const int stableCyclesNeeded = 5;  // Cycles required to trigger save
```

---

## 🖥 Serial Output Example

```
FSR Live: PB0=812.34, PA7=799.12, PA6=805.44, PA5=810.01, PA4=808.77, PA3=820.55, PA2=815.32, PA1=802.91, PA0=798.40
```

When stable:

```
=====================================
STABLE → DATA SAVED
FSR Snapshot: PB0=812.30, PA7=799.10, PA6=805.40, PA5=810.00, PA4=808.70, PA3=820.50, PA2=815.30, PA1=802.90, PA0=798.40
=====================================
```

---

## 🛠 Requirements

- STM32 Arduino Core
- PlatformIO or Arduino IDE
- No external libraries required

---


## 📄 License

This project is open-source and free to use for educational and personal projects.
