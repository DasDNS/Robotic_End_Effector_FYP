# STM32 LED Control + PySide6 Serial Control UI

## 📌 Project Overview
This project demonstrates a **PC ↔ STM32 serial control system** with:

- LED control firmware running on STM32 (Arduino framework)
- Desktop GUI control panel built with PySide6 (Qt for Python)
- Real‑time serial communication
- Command-based LED control (ON / OFF / BLINK)

---

# 🧠 System Architecture

PC GUI (PySide6)  →  Serial UART  →  STM32 MCU  →  LED Control

The GUI sends numeric commands via serial, and the STM32 executes LED actions.

---

# 🔧 STM32 Firmware

## Features
- Serial command parsing
- LED ON / OFF / BLINK modes
- Non‑blocking blink using `millis()`
- Active‑LOW LED handling (common on STM32 boards)

## Command Mapping

| Command | Action |
|--------|--------|
| `1` | LED ON |
| `0` | LED OFF |
| `2` | LED BLINK |

---

## Firmware Code Behavior (Step‑by‑Step)

### 1️⃣ Pin Configuration
```cpp
#define LED_PIN PC13
```
Uses onboard LED pin (change if needed).

---

### 2️⃣ State Variables
```cpp
bool blinkMode = false;
uint32_t lastBlinkMs = 0;
bool ledState = false;
```
Tracks blink state and timing.

---

### 3️⃣ LED Control Functions
```cpp
void ledOn()  { digitalWrite(LED_PIN, LOW); }
void ledOff() { digitalWrite(LED_PIN, HIGH); }
```
Active‑LOW logic.

---

### 4️⃣ Setup()
- Configures LED pin as output
- Starts serial at 115200 baud
- Prints usage instructions

---

### 5️⃣ Serial Command Reading
Reads single‑byte commands:

```cpp
if (c == '1') → LED ON
if (c == '0') → LED OFF
if (c == '2') → BLINK MODE
```

---

### 6️⃣ Blink Logic
Non‑blocking timing:

```cpp
if (now - lastBlinkMs >= 500)
```
Toggles LED every 500 ms → 1 Hz blink.

---

# 🖥️ PySide6 Serial Control UI

## Features
- Auto serial port detection
- Manual port selection
- Quick control buttons
- Serial monitor style command sender
- Debug log + MCU status console
- Line ending selection
- Threaded serial reader

---

## UI Sections

### 🔌 Connection Panel
- Refresh ports
- Auto-detect STM32
- Connect / Disconnect
- Status display

---

### ⚡ Quick Controls
Buttons send instant commands:

| Button | Command Sent |
|--------|---------------|
| Light ON | `1` |
| OFF | `0` |
| BLINK | `2` |
| Ping | `PING` |

---

### ⌨️ Command Sender
Manual serial transmission:

- Custom command input
- Line ending selection:
  - NONE
  - LF
  - CR
  - CRLF

---

### 📡 MCU Status Monitor
Displays all incoming serial messages.

---

### 🧾 Debug Log
Shows:

- TX messages
- RX messages
- Errors
- Connection logs

---

# 🔄 Serial Communication Flow

1. User clicks button or sends command
2. GUI writes serial bytes
3. STM32 receives command
4. LED state changes
5. STM32 prints response
6. GUI displays response

---

# 🛠️ Requirements

## Firmware
- STM32 board
- Arduino STM32 Core
- USB‑Serial connection

## PC Software
```bash
pip install PySide6 pyserial
```

---

# ▶️ How to Run

## 1️⃣ Flash STM32
Upload firmware via Arduino IDE / PlatformIO.

---

## 2️⃣ Run GUI
```bash
python3 control_ui.py
```

---

## 3️⃣ Connect
- Select port
- Click Connect
- Use quick controls

---

# 📷 Use Cases

- Embedded testing
- UART debugging
- Robotics subsystems
- LED signaling demos
- Firmware validation

---

# 🚀 Future Improvements

- Multi‑LED control
- PWM brightness
- Sensor feedback
- ROS2 bridge
- Wireless serial (BLE/WiFi)

---

# 👨‍💻 Author
**Dasuni Saparamadu**  
Embedded Software / Firmware Engineer  
Sri Lanka 🇱🇰
