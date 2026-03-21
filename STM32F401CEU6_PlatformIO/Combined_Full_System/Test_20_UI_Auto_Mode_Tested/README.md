# Vision-Guided Robotic Hand End Effector Control System

This project implements a **vision-assisted robotic hand end effector** with a feedback-driven grasp controller on the MCU side and a **laptop UI bridge** that connects the hand to a vision laptop through **ROS 2 Jazzy**.

The system is split into two parts:

- **MCU firmware** for the robotic hand, sensor reading, and grasp state machine
- **Laptop control UI** for serial communication with the MCU and ROS communication with the vision laptop

## Project Overview

The overall workflow is:

1. The vision side determines a **5-bit finger activation pattern**.
2. The laptop UI requests and receives that pattern over ROS.
3. The UI forwards the pattern to the MCU over serial.
4. The MCU performs a grasp using:
   - **FSR tactile sensing**
   - **servo current sensing through INA226 sensors**
   - a multi-state **finite state machine (FSM)**
5. The hand adjusts grasping based on feedback until the grasp is held, settled, or recovered.

This design supports both:

- **Manual mode**: operator requests a pattern, sends it to the MCU, and starts grasping manually
- **Auto mode**: the UI automatically acknowledges patterns, sends them to the MCU, reacts to vision commands, and publishes state/status back over ROS

---

## Repository Components

### 1. MCU Firmware
The firmware is written for an STM32/Arduino-style environment and controls the robotic hand.

Main responsibilities:

- Drive **5 servo motors** for the fingers
- Read **9 FSR sensors**
- Read **5 INA226 current sensors** through a **PCA9548A I2C multiplexer**
- Run the grasp **FSM**
- Accept simple serial commands from the laptop UI
- Continuously print sensor and state data for monitoring

### 2. Laptop UI Application
The laptop-side application is written in **Python** using **PySide6**, **pyserial**, and **ROS 2 Jazzy**.

Main responsibilities:

- Connect to the MCU over serial
- Provide a desktop control panel
- Communicate with the vision laptop using ROS topics
- Display:
  - active finger pattern
  - FSM state
  - live FSR values
  - live current values
  - status/debug logs
- Support both manual and automatic grasp workflows

---

## Hardware/Signal Architecture

### MCU-side hardware
- **5 servo outputs**
  - Pinky: `PB13`
  - Ring: `PB14`
  - Middle: `PB15`
  - Index: `PA8`
  - Thumb: `PA11`
- **9 FSR analog inputs**
  - `PB0, PA7, PA6, PA5, PA4, PA3, PA2, PA1, PA0`
- **5 INA226 current sensors**
  - all on address `0x40`
  - selected through **PCA9548A** at `0x70`
- **I2C pins**
  - SDA: `PB9`
  - SCL: `PB8`

### Laptop-side links
- **Serial link** between laptop UI and MCU
- **ROS 2 link** between laptop UI and vision laptop

---

## Serial Protocol (Laptop UI <-> MCU)

The MCU accepts only three command types:

- `00000` to `11111` → 5-bit finger activation pattern
- `2` → start grasp
- `3` → reset/open hand

### Meaning of the 5-bit pattern
Each bit enables or disables one finger:

- bit 0: Little / Pinky
- bit 1: Ring
- bit 2: Middle
- bit 3: Index
- bit 4: Thumb

Example:

```text
11111   -> all fingers active
01110   -> ring, middle, index active
00001   -> thumb only
```

### Basic serial workflow

```text
1. Send 5-bit pattern
2. Send "2" to start grasp
3. Send "3" anytime to reset/open
```

The MCU blocks invalid commands and also blocks new patterns while the hand is not in `IDLE`.

---

## ROS 2 Interface (Laptop UI <-> Vision Laptop)

The laptop UI uses these ROS topic names:

- `finger_pattern_request`
  - UI -> vision laptop
  - requests a new 5-bit pattern
- `finger_pattern`
  - vision laptop -> UI
  - returns the 5-bit pattern
- `finger_pattern_ack`
  - UI -> vision laptop
  - carries messages such as:
    - `ACK:<pattern>`
    - `STATE:Idle`
    - `STATE:Not Idle`
    - `STATE:Unknown`
    - `STATUS:<text>`
    - `AUTO:On`
    - `AUTO:Off`
- `finger_control_cmd`
  - vision laptop -> UI
  - control commands such as:
    - `Grab`
    - `Idle?`
    - `State?`

### Auto mode behavior
When Auto Mode is enabled, the UI can:

- request a pattern over ROS
- publish `ACK:<pattern>` after receiving it
- publish state replies such as `STATE:Idle`
- publish status messages such as `STATUS:GrabStarted`
- publish `AUTO:On` / `AUTO:Off`
- send the stored pattern to the MCU automatically
- start grasping automatically when a `Grab` command is received and the MCU is in `IDLE`

---

## MCU Finite State Machine

The hand controller uses the following states:

- `IDLE`
- `CLOSING_FAST`
- `CLOSING_SLOW`
- `TIGHTEN`
- `HOLD`
- `SETTLE`
- `RECOVER`
- `RESETTING`

### State summary

#### `IDLE`
Hand is open and waiting for a valid 5-bit pattern.

#### `CLOSING_FAST`
Initial fast closing motion toward `FAST_TARGET_US = 1600`.

#### `CLOSING_SLOW`
Slower closing motion toward `SLOW_TARGET_US = 1000`.
During this phase the controller looks for:

- large FSR changes
- high motor current

If either is detected, the hand transitions to `HOLD`.

#### `TIGHTEN`
Further closes enabled fingers toward `SERVO_MIN_US = 500` at a reduced speed.
Used when the hand needs to increase grip force.

#### `HOLD`
Stops motion and monitors whether contact is still present.
If both tactile and current feedback drop sufficiently for a debounce period, the system returns to `TIGHTEN`.

#### `SETTLE`
No further motion. The hand watches for loss of contact after previously having strong contact.

#### `RECOVER`
Recovery action after contact drop in `SETTLE`.
The hand spreads slightly to `RECOVER_SPREAD_US = 900` and then re-enters `TIGHTEN`.

#### `RESETTING`
Opens/spreads the hand back to the reset position and returns to `IDLE`.

---

## Feedback Logic Used by the MCU

### 1. Tactile sensing
The firmware reads **9 FSR channels** and applies low-pass filtering.
These are used to detect:

- contact onset
- large contact changes during closing
- contact loss during hold/settle

### 2. Current sensing
The firmware reads **5 INA226 current sensors**, one per finger motor path.
Current is used to detect conditions such as:

- motor loading during object contact
- high current suggesting grasp completion / hold condition
- low current during release/contact loss

### 3. Per-finger ramp control
Each finger has:

- its own servo pulse value
- target pulse
- ramp activation flag
- speed multiplier

This allows selective and non-uniform finger motion depending on the active pattern and grasp phase.

---

## Important MCU Parameters

Some key values from the firmware:

- `SERVO_MIN_US = 500`
- `SERVO_MAX_US = 2400`
- `FULL_SWEEP_TIME_SEC = 12.0`
- `RESET_SWEEP_TIME_SEC = 6.0`
- `FAST_TARGET_US = 1600`
- `SLOW_TARGET_US = 1000`
- `RECOVER_SPREAD_US = 900`
- `CONTROL_PERIOD_MS = 10`
- `CURRENT_PRINT_PERIOD_MS = 200`
- `FSR_PRINT_PERIOD_MS = 200`
- `I_TIGHTEN_HIGH_MA = 800.0`
- `HOLD_RELEASE_DEBOUNCE_MS = 350`
- `SETTLE_RECOVER_DEBOUNCE_MS = 120`

---

## Laptop UI Features

The desktop application provides:

- **Manual Mode**
  - request pattern from ROS
  - send pattern to MCU manually
  - start grasp manually
  - reset/open manually
- **Auto Mode**
  - request pattern from ROS
  - auto-acknowledge pattern
  - auto-send pattern to MCU
  - react to `Grab`, `Idle?`, and `State?`
  - publish status/state messages back to the vision side
- **Serial port tools**
  - refresh ports
  - auto-detect STM32 port
  - connect/disconnect at `115200`
- **Live monitoring**
  - current text stream
  - FSR text stream
  - FSM state box
  - debug log box

---

## Expected MCU Output Format

The UI classifies incoming serial lines into three main types.

### FSM lines
```text
12345,[STATE] HOLD
```

### FSR lines
```text
12345,FSR Live: Little=..., Ring=..., Middle=..., ...
```

### Current lines
```text
12345,1400,Little=... mA, Ring=... mA, Middle=... mA, Index=... mA, Thumb=... mA
```

Any other incoming lines are shown as general status/debug messages.

---

## Software Requirements

### MCU side
- Arduino-compatible STM32 environment
- Required libraries:
  - `Arduino.h`
  - `Wire.h`
  - `Servo.h`
  - `INA226_WE.h`
  - `math.h`

### Laptop side
- Python 3
- ROS 2 Jazzy
- Python packages/libraries:
  - `PySide6`
  - `pyserial`
  - `rclpy`
  - `std_msgs`

Example Python install for desktop dependencies:

```bash
pip install PySide6 pyserial
```

ROS 2 Jazzy must also be installed and sourced in the terminal before launching the UI.

---

## How to Run

### 1. Flash the MCU firmware
Build and upload the firmware to the STM32 board using your Arduino/STM32 toolchain.

### 2. Start ROS 2 environment
On the laptop running the UI:

```bash
source /opt/ros/jazzy/setup.bash
```

If you are also using a workspace:

```bash
source /opt/ros/jazzy/setup.bash
source ~/your_ws/install/setup.bash
```

### 3. Run the laptop UI

```bash
python3 your_ui_script.py
```

### 4. Connect to the MCU
- Use **Refresh Ports** or **Auto-Detect**
- Connect to the STM32 serial port

### 5. Operate the system

#### Manual mode
1. Enable **Manual Mode**
2. Request pattern from ROS
3. Send pattern to MCU
4. Press **Start Grasping**
5. Use **Reset/Open** when needed

#### Auto mode
1. Enable **Auto Mode**
2. Request pattern from ROS
3. Let the UI receive and acknowledge the pattern
4. Let the vision side send `Grab`
5. The UI starts grasping automatically when the MCU is ready

---

## Safety / Operational Notes

- The MCU only accepts a new pattern while in `IDLE`.
- Reset (`3`) works from any state.
- In auto mode, grasp start is blocked if:
  - no valid pattern is stored
  - MCU state is unknown
  - MCU is not in `IDLE`
  - serial is not connected
- The firmware halts during setup if any INA226 sensor is missing or fails initialization.
- Disabled fingers are forced open/spread at `SERVO_MAX_US`.

---

## Suggested Folder Structure

```text
project/
├── mcu_firmware/
│   └── hand_controller.ino
├── laptop_ui/
│   └── control_ui.py
└── README.md
```

---

## Typical Use Case

A vision module identifies the object or grasp class and generates a 5-bit finger activation pattern. The laptop UI requests that pattern, forwards it to the MCU, and then supervises execution. The MCU closes the enabled fingers in stages while monitoring tactile and current feedback. If contact is detected early, the hand holds. If contact is lost after settling, the controller performs a small recovery spread and retries tightening.

---

## Notes

This README was written from the provided codebase, so it reflects the current implementation and message flow in the shared MCU firmware and Python UI.
