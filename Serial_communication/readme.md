# 🟦 STM32 "Hello, Blue Pill!" — UART Serial Communication Example

This simple example demonstrates how to print a message ("Hello, Blue Pill!") from an **STM32 Black Pill (STM32F401CE)** board using the **UART (Serial)** interface.  
The project is built using **PlatformIO** and verified using a **USB-to-TTL converter** for serial communication and an **ST-Link debugger** for uploading the code.

---

## 🔧 Hardware Connections

### UART–TTL Converter Connections

| STM32 Pin | UART–TTL Pin | Notes          |
|------------|---------------|----------------|
| PA9        | RX            | TX1 output     |
| PA10       | TX            | RX1 input      |
| GND        | GND           | Common ground  |

> ⚠️ Ensure that the **GND** of the STM32 and the UART–TTL module are connected.

---

### ST-Link Debugger Connections

| ST-Link Pin | STM32 Pin | Notes                   |
|--------------|------------|--------------------------|
| 3.3V         | 3.3V       | Power (optional, if not powered externally) |
| GND          | GND        | Common ground           |
| SWCLK        | PA14 (SWCLK) | Clock line             |
| SWDIO        | PA13 (SWDIO) | Data line              |
| RST (optional) | NRST     | Optional reset control  |

---

## 💻 Code

```cpp
#include <Arduino.h>

void setup() {
  // Start the Serial communication
  Serial.begin(115200);

  // Wait for the serial port to connect (necessary for some boards)
  while (!Serial) {
    ; // Wait
  }
}

void loop() {
  // Print a message to the Serial Monitor
  Serial.println("Hello, Blue Pill!");

  // Wait for 1 second
  delay(1000);
}
```

---

## 🧠 What the Code Does

1. **Initializes Serial Communication**  
`Serial.begin(115200);` starts UART communication at a baud rate of 115200.

2. **Waits for Serial Connection**  
The `while (!Serial)` loop ensures the program waits until the serial connection is established.

3. **Prints a Message**  
Inside `loop()`, the code continuously prints "Hello, Blue Pill!" every second.

4. **Delay**  
`delay(1000);` introduces a 1-second pause between messages.

---

## ⚙️ PlatformIO Setup

1. Open the project folder in **PlatformIO**.
2. Connect the **ST-Link debugger** to your STM32 board.
3. Upload the code using:  
   `PlatformIO: Upload`
4. Once uploaded, open the **Serial Monitor** from the PlatformIO toolbar or using:  
   `PlatformIO: Monitor`

---

## 🖥️ Viewing the Output

After uploading, open the **Serial Monitor** (or the Serial Monitor extension) and:

1. Select the correct **COM port** (usually the **last option** — corresponding to your **USB-to-TTL converter**).  
2. Set the **baud rate** to **115200**.  
3. You should see continuous messages like:

```
Hello, Blue Pill!
Hello, Blue Pill!
Hello, Blue Pill!
...
```

---

## ✅ Summary

| Parameter | Description |
|-----------|-------------|
| **Board** | STM32F401CE (Black Pill) |
| **IDE** | PlatformIO |
| **Debugger** | ST-Link |
| **Serial Communication** | USB-to-TTL converter (PA9 → RX, PA10 → TX) |
| **Baud Rate** | 115200 |
| **Output** | Prints "Hello, Blue Pill!" every second |

---
<img width="749" height="580" alt="Screenshot from 2025-10-17 11-22-26" src="https://github.com/user-attachments/assets/1a52a56b-6db4-491d-82f5-dd00f8d3c419" />

<img width="1920" height="1080" alt="Screenshot from 2025-10-17 11-51-40" src="https://github.com/user-attachments/assets/23d441d2-7cf7-4d12-b785-70a04a5d53e5" />
<img width="1920" height="1080" alt="Screenshot from 2025-10-17 11-51-40" src="https://github.com/user-attachments/assets/03f498d4-695a-4c93-882c-ea2ef402fa6e" />
