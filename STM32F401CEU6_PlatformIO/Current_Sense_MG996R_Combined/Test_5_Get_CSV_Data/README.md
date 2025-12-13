# STM32 Black Pill – Servo Control with INA226 & CSV Logging

## 📌 Project Overview

This project implements **precise servo motor control** on an **STM32 Black Pill** while **measuring motor current in real time** using an **INA226 current sensor**.

It is specifically designed for **incremental grasp control experiments**, where servo position is gradually changed and motor current is logged to analyze **contact, soft grasp, hard grasp, and stall conditions**.

The firmware is developed using **PlatformIO (Arduino framework)** and outputs **CSV-formatted data over Serial** for offline analysis.

---

## ✅ Features Implemented (Core Emphasis)

| Command | Action |
|------|--------|
| **0** | Jump → **Fully bent** position (**500 µs**) |
| **1** | Jump → **Mid position** (**1450 µs**) |
| **2** | Jump → **Fully straight** position (**2400 µs**) |
| **3** | **Step −100 µs** (gradual bending) |
| **4** | **Step +100 µs** (gradual straightening) |

🔹 Commands **3** and **4** enable **fine, incremental control**, allowing smooth transition from fully straightened to fully bent positions.

🔹 After **every servo movement**, **INA226 current is sampled for 1 second** and logged.

---

## 2️⃣ Why CSV Logging Is Important for This Project

For **incremental grasp control**, CSV logging enables you to:

✔ Plot **motor current vs servo position**  
✔ Identify **initial contact**, **soft grasp**, and **hard grasp** regions  
✔ Detect **stall / saturation current**  
✔ Export data directly to **Excel, MATLAB, Python, GNU Octave**

➡️ This is **exactly how experimental data is collected and analyzed in research papers and Final Year Projects (FYPs).**

---

## 3️⃣ What Data Is Logged (Minimum Dataset)

The firmware logs the following **CSV columns**:

| Column | Meaning |
|------|--------|
| `time_ms` | Timestamp since boot (milliseconds) |
| `pulse_us` | Servo pulse width (grasp tightness) |
| `current_mA` | Motor current (grip force proxy) |

### Optional future extensions
- FSR sensor values
- Grasp state label (`soft`, `hard`, `stable`)

---

## 4️⃣ How CSV Logging Works on the Microcontroller

```
STM32 Black Pill
   ↓ (Serial CSV)
PlatformIO Serial Monitor
   ↓
Copy / Save to File
   ↓
Offline Plotting
```

✔ No SD card required  
✔ No runtime Python or AI  
✔ Fully deterministic and exam-safe

---

## 5️⃣ CSV Logging Implementation (Already in This Code)

### Step 1: CSV Header (Printed Once in `setup()`)

```cpp
Serial.println("time_ms,pulse_us,current_mA");
```

### Step 2: CSV Row Output (`printINA226Data()`)

```cpp
void printINA226Data() {
  float current_mA = ina226.getCurrent_mA();
  checkForI2cErrors();

  Serial.print(millis());
  Serial.print(",");
  Serial.print(currentPulseWidth);
  Serial.print(",");
  Serial.println(current_mA);

  delay(300);
}
```

⚠️ Important:
- No text labels
- No units
- Only numbers and commas

---

## 6️⃣ Example Serial Output (Realistic)

When pressing `2`, then `3` repeatedly:

```
time_ms,pulse_us,current_mA
1205,2400,82.1
1507,2400,83.0
1810,2400,84.5
2150,2300,91.8
2450,2300,93.2
2760,2200,101.4
```

➡️ This output is **directly plottable**.

---

## 7️⃣ Plotting Example (Python)

```python
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("grasp_log.csv")

plt.plot(data["pulse_us"], data["current_mA"], marker='o')
plt.xlabel("Servo Pulse Width (µs)")
plt.ylabel("Current (mA)")
plt.title("Grasp Tightness vs Motor Current")
plt.grid()
plt.show()
```

### Interpretation
- **Flat region** → No contact
- **Rising slope** → Soft grasp
- **Sharp rise** → Hard grasp / stall

---

## 🔌 Hardware Configuration

| Component | STM32 Pin |
|--------|-----------|
| Servo PWM | `PB13` |
| I2C SDA | `PB7` |
| I2C SCL | `PB6` |

**Note:** Servo must be powered from an external supply with a **common ground**.

---

## 📁 Project Structure

```
project-root/
├── src/
│   └── main.cpp
├── platformio.ini
└── README.md
```

---

