# Vision-Guided Robotic Hand End-Effector Control System

This project combines an **STM32-based robotic hand controller** with a **laptop-side PySide6 + ROS 2 user interface** for adaptive grasping experiments.

The system is designed to:
- receive a **5-bit finger activation pattern** from a vision laptop over ROS 2,
- forward that pattern from the UI laptop to the STM32 over serial,
- actuate selected fingers using **servo motors**,
- monitor **motor current** using INA226 sensors,
- monitor **contact feedback** using FSR sensors,
- and manage grasping through a finite-state control strategy.

This README is based on the uploaded MCU firmware and laptop UI code. fileciteturn7file0 fileciteturn7file1

---

## 1. System Overview

The project has two main parts:

### A. STM32 MCU firmware
The MCU:
- controls **5 servo-driven fingers**,
- reads **5 INA226 current sensors** through a **PCA9548A I2C multiplexer**,
- reads **9 FSR sensors**,
- accepts serial commands,
- and runs the grasping **FSM**.

### B. Laptop UI application
The laptop application:
- provides a **PySide6 desktop interface**,
- communicates with the STM32 over **serial**,
- communicates with the vision laptop over **ROS 2 Jazzy**,
- requests a grasp pattern,
- displays the received pattern,
- sends the pattern to the MCU,
- and allows the operator to start or reset the grasp. fileciteturn7file0 fileciteturn7file1

---

## 2. Main Features

### MCU side
- 5-servo finger control using `Servo.h`
- 5 INA226 current monitors on PCA9548A channels 0-4
- 9 analog FSR inputs
- per-finger ramped motion control
- state-based grasp controller with hold, settle, and recovery logic
- continuous serial printing of:
  - FSM state
  - FSR live values
  - motor current values

### Laptop side
- serial connection manager for STM32
- ROS 2 request / response / ACK messaging
- live display of:
  - selected grasp pattern
  - current MCU FSM state
  - FSR stream
  - current stream
  - debug log
- operator buttons for:
  - requesting pattern from ROS
  - sending pattern to MCU
  - starting grasp
  - reset/open
  - manual debug send

---

## 3. Hardware Mapping

### Servo outputs
The firmware controls five servo outputs:
- `SERVO0_PIN PB13` → Pinky
- `SERVO1_PIN PB14` → Ring
- `SERVO2_PIN PB15` → Middle
- `SERVO3_PIN PA8`  → Index
- `SERVO4_PIN PA11` → Thumb fileciteturn7file0

### FSR inputs
Nine FSR channels are defined:
- `PB0` → Little
- `PA7` → LittlePalm
- `PA6` → Ring
- `PA5` → RingPalm
- `PA4` → Middle
- `PA3` → Index
- `PA2` → IndexPalm
- `PA1` → Thumb
- `PA0` → ThumbPalm fileciteturn7file0

### Current sensing
The system uses:
- `INA226_ADDRESS = 0x40`
- `PCA9548A_ADDRESS = 0x70`
- one INA226 per finger, accessed by selecting mux channels 0 to 4. fileciteturn7file0

### I2C pins
The MCU firmware sets:
- `SDA = PB9`
- `SCL = PB8` fileciteturn7file0

---

## 4. Software Stack

### MCU firmware
Libraries used:
- Arduino core
- `Wire.h`
- `Servo.h`
- `INA226_WE.h`
- `math.h` fileciteturn7file0

### Laptop UI
Python dependencies include:
- Python 3
- PySide6
- pyserial
- ROS 2 Jazzy
- `rclpy`
- `std_msgs` fileciteturn7file1

Install Python packages as needed:

```bash
pip install PySide6 pyserial
```

ROS 2 Jazzy packages should already be available in your ROS environment.

---

## 5. ROS 2 Communication

The UI uses these ROS topic names:
- `finger_pattern_request` → UI publishes pattern requests
- `finger_pattern` → UI subscribes to pattern responses from the vision system
- `finger_pattern_ack` → UI publishes confirmation / ACK back to the vision system fileciteturn7file1

### ROS message flow
1. Operator clicks **Request Pattern (ROS)**.
2. UI publishes `REQ` on `finger_pattern_request`.
3. Vision laptop responds with a **5-bit pattern** on `finger_pattern`.
4. UI validates the pattern.
5. UI sends `ACK:<pattern>` on `finger_pattern_ack`.
6. Operator clicks **Send Pattern to MCU**.
7. UI sends the same 5-bit pattern over serial to the STM32.
8. Operator clicks **Start Grasping** to send command `2`. fileciteturn7file1

---

## 6. Serial Protocol (UI ↔ MCU)

The MCU accepts only three command types:
- **5-bit pattern** such as `10110`
- `2` → start grasp
- `3` → reset / open hand

The firmware explicitly blocks any other command format. Pattern commands are only accepted in the `IDLE` state. Reset works from any state. fileciteturn7file0

### Serial workflow
1. Send a valid 5-bit finger pattern.
2. MCU stores the pattern and waits.
3. Send `2` to begin grasping.
4. Send `3` at any time to reset/open the hand. fileciteturn7file0

### Example commands
```text
10110
2
3
```

---

## 7. Finger Pattern Meaning

The pattern is a 5-character binary string. Each bit enables or disables one finger.

Order used by the software:
- bit 0 → Pinky / Little
- bit 1 → Ring
- bit 2 → Middle
- bit 3 → Index
- bit 4 → Thumb fileciteturn7file0turn7file1

Example:
```text
01111
```
This means the pinky is disabled and the other four fingers are enabled.

---

## 8. MCU Finite State Machine

The firmware defines these states:
- `STATE_IDLE`
- `STATE_CLOSING_FAST`
- `STATE_CLOSING_SLOW`
- `STATE_TIGHTEN`
- `STATE_HOLD`
- `STATE_SETTLE`
- `STATE_RECOVER`
- `STATE_RESETTING` fileciteturn7file0

### State summary

#### `IDLE`
Hand remains open and waits for a valid 5-bit pattern and start command.

#### `RESETTING`
All fingers are opened/spread to the maximum pulse width using a reset ramp.

#### `CLOSING_FAST`
Enabled fingers move quickly toward `FAST_TARGET_US = 1600`.

#### `CLOSING_SLOW`
Enabled fingers continue closing more slowly toward `SLOW_TARGET_US = 1000`.
During this state, the controller looks for:
- a large FSR change,
- or high current,
which can trigger transition to `HOLD`. fileciteturn7file0

#### `TIGHTEN`
Enabled fingers ramp toward `SERVO_MIN_US = 500` at reduced speed for a firmer grasp.
Again, high current or major FSR change can trigger `HOLD`. fileciteturn7file0

#### `HOLD`
Finger motion is stopped. If both contact and current become low for the debounce period, the controller returns to `TIGHTEN`. fileciteturn7file0

#### `SETTLE`
After tightening reaches minimum pulse width, motion stops and the controller watches whether contact disappears.

#### `RECOVER`
If contact was present and then drops significantly, the hand partially reopens to `RECOVER_SPREAD_US = 900`, then attempts `TIGHTEN` again. fileciteturn7file0

---

## 9. Key Control Parameters

Important firmware constants include:
- `FULL_SWEEP_TIME_SEC = 12.0`
- `RESET_SWEEP_TIME_SEC = 6.0`
- `FAST_TARGET_US = 1600`
- `SLOW_TARGET_US = 1000`
- `RECOVER_SPREAD_US = 900`
- `I_TIGHTEN_HIGH_MA = 800.0`
- `HOLD_RELEASE_FSR_FRAC = 0.20`
- `HOLD_RELEASE_I_MA = 100.0`
- `SETTLE_RECOVER_HIGH_FRAC = 0.30`
- `SETTLE_RECOVER_LOW_ABS = 30.0` fileciteturn7file0

The ring finger is intentionally given a larger speed multiplier than the others in several motion states. fileciteturn7file0

---

## 10. UI Panels

The laptop UI contains the following sections:
- **Connection (MCU Serial)**
- **Vision Pattern (ROS 2 Jazzy)**
- **Controls (MCU)**
- **Manual Send (Debug)**
- **Grasp Selection + FSM State**
- **FSR Values**
- **Current Values**
- **MCU Status / Other Messages**
- **Debug Log** fileciteturn7file1

The UI also color-codes the active finger pattern and highlights the current FSM state. fileciteturn7file1

---

## 11. Running the Project

### A. MCU side
Flash the MCU firmware to your STM32 board using your Arduino-compatible STM32 setup.

Make sure the following are connected correctly:
- 5 servo motors
- 5 INA226 modules through PCA9548A
- 9 FSR inputs
- serial USB connection to the laptop

### B. Laptop side
Before running the UI, source your ROS 2 Jazzy environment.

Example:
```bash
source /opt/ros/jazzy/setup.bash
python3 your_ui_script.py
```

### C. Typical operation
1. Connect the STM32 over USB.
2. Open the UI.
3. Click **Refresh Ports** or **Auto-Detect**.
4. Click **Connect**.
5. Click **Request Pattern (ROS)**.
6. Wait for the vision laptop to publish a valid 5-bit pattern.
7. Click **Send Pattern to MCU**.
8. Click **Start Grasping**.
9. Use **Reset/Open** whenever needed. fileciteturn7file1

---

## 12. Serial Output Streams

The firmware periodically prints:

### FSM messages
Example:
```text
12345,[STATE] CLOSING_FAST
```

### FSR live messages
Example:
```text
12345,FSR Live: Little=0.00, LittlePalm=0.00, Ring=12.00, ...
```

### Current messages
Example:
```text
12345,1800,Little=120.0 mA, Ring=340.0 mA, Middle=...
```

The laptop UI classifies these incoming serial lines into separate display panels. fileciteturn7file0turn7file1

---

## 13. Safety / Behavior Notes

- The firmware halts during setup if any INA226 device is not detected or fails to initialize. fileciteturn7file0
- Disabled fingers are forced to the open/spread pulse width. fileciteturn7file0
- The UI prevents starting a grasp until a ROS pattern has been sent to the MCU. fileciteturn7file1
- The UI restricts manual commands to only valid patterns, `2`, or `3`. fileciteturn7file1

---

## 14. Suggested Project Structure

If you are organizing this into a repository, a practical layout would be:

```text
project/
├── mcu/
│   └── main_firmware.ino
├── laptop_ui/
│   └── control_ui.py
├── README.md
└── docs/
```

---

## 15. Future Improvements

Possible extensions for this project:
- integrate automatic serial reconnection
- log FSR/current data to CSV
- add a ROS topic for MCU state publishing
- add threshold tuning from the UI
- add plots for live FSR and current trends
- support multiple grasp taxonomies from the vision system

---

## 16. License

Add your preferred license here if this project will be published.

