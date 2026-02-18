# STM32 LED + Sensor Serial UI Test

## 📌 Project Description
This project is a **PC ↔ STM32 serial communication test system** featuring:

- LED control firmware on STM32 (Arduino framework)
- Periodic sensor message transmission (FSR + Current)
- PySide6 desktop UI for monitoring and control
- Message filtering into dedicated UI panels
- Serial Monitor–style command sender
- Debug logging + monitor clearing

---

# 🧠 System Architecture

STM32 MCU  ⇄  UART Serial  ⇄  Python PySide6 UI

The MCU sends structured text messages, and the UI filters and displays them in separate components.

---

# 🔧 STM32 Firmware Features

## LED Control Commands

| Command | Function |
|--------|-----------|
| `1` | LED ON |
| `0` | LED OFF |
| `2` | LED BLINK |

Active‑LOW LED logic is used (common for STM32 onboard LEDs).

---

## Periodic Sensor Messages

The MCU transmits two independent message streams:

| Message | Period |
|---------|--------|
| `FSR Readings = ...` | Every 2 seconds |
| `Current readings = ...` | Every 3 seconds |

Example output:

```
FSR Readings = e73264836r138419
Current readings = 82392y93y`293
LED ON
LED OFF
```

Timing is implemented using **millis() (non‑blocking)** to prevent UART flooding.

---

# 🖥️ Python PySide6 UI Features

## 🔌 Serial Connection Panel
- Port refresh
- Auto‑detect STM32
- Connect / Disconnect
- Live connection status

---

## ⚡ Quick Controls

| Button | Command Sent |
|--------|---------------|
| Light ON | `1` |
| OFF | `0` |
| BLINK | `2` |
| PING | `PING` |

---

## ⌨️ Serial Monitor Sender
- Manual command entry
- Selectable line endings:
  - NONE
  - LF
  - CR
  - CRLF

Works exactly like Arduino Serial Monitor.

---

# 📊 Filtered Data Panels

## FSR Readings Panel
Displays only lines starting with:

```
FSR Readings =
```

---

## Current Readings Panel
Displays only lines starting with:

```
Current readings =
```

---

## MCU Status / Other Messages
Displays:

- LED ON
- LED OFF
- LED BLINK
- Any non‑sensor MCU messages

---

## 🧾 Debug Log Panel
Shows:

- TX messages
- RX messages
- Connection logs
- Errors

---

# 🧹 Clear Monitor Function

A **Clear Monitors** button clears:

- FSR panel
- Current panel
- Status panel
- Debug log

Useful during long test sessions.

---

# 🔍 Message Filtering Logic

Implemented in Python serial reader thread:

```python
if s.startswith("FSR"):
    → FSR panel
elif s.startswith("Current"):
    → Current panel
else:
    → Status panel
```

This enables structured UI routing.

---

# 🛠️ Requirements

## Firmware
- STM32 board
- Arduino STM32 Core
- USB‑UART connection

## PC Software
```bash
pip install PySide6 pyserial
```

---

# ▶️ How to Run

## 1️⃣ Flash Firmware
Upload STM32 code via Arduino IDE / PlatformIO.

## 2️⃣ Run UI
```bash
python3 control_ui.py
```

## 3️⃣ Connect
- Select serial port
- Click Connect
- Use quick controls or monitor panels

---

# ⚠️ UART Stability Notes

If USB‑TTL disconnects or crashes:

- Avoid printing every loop
- Use timed intervals (millis)
- Keep messages short
- Use ≥115200 baud
- Ensure common GND

Current test rates (2s / 3s) are safe.

---

# 🚀 Future Improvements

- Real sensor integration
- Graph plotting
- CSV logging
- ROS2 bridge
- Multi‑MCU routing
- Wireless telemetry

---

# 👨‍💻 Author
**Dasuni Saparamadu**  
Embedded Software / Firmware Engineer  
Sri Lanka 🇱🇰
