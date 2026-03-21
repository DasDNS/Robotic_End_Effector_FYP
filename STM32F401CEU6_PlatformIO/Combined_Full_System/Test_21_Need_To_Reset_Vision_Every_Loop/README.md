# Vision-Guided, Feedback-Enabled Robotic Hand End-Effector

This project combines an STM32-based robotic hand controller with a laptop-based control UI that communicates with a separate vision laptop. The overall system performs shape-guided grasp selection and adaptive grasp execution using tactile and motor-current feedback.

The repository, as provided here, contains two main software parts:

- **MCU firmware** for the robotic hand, written in Arduino-style C++ for STM32
- **Laptop UI application** written in Python with PySide6, ROS 2 Jazzy, and serial communication

## Project Overview

The system workflow is:

1. A **vision laptop** identifies or requests a finger activation pattern.
2. The **laptop UI** receives that pattern through ROS 2 topics.
3. The UI forwards the pattern to the **STM32 MCU** over serial.
4. The MCU executes grasping using:
   - **FSR tactile sensing**
   - **INA226 current sensing** for each servo channel
   - a finite-state control strategy to tighten, hold, settle, and recover the grasp

This makes the hand more adaptive than simple open-loop finger closing.

## Main Features

### MCU firmware

- Controls **5 servo-driven fingers**
- Reads **9 FSR sensors**
- Reads **5 INA226 current sensors** through a **PCA9548A I2C multiplexer**
- Uses a **finite state machine (FSM)** for grasp execution
- Supports per-finger enable/disable using a **5-bit grasp pattern**
- Supports runtime commands through serial:
  - `00000` to `11111` → finger activation pattern
  - `2` → start grasp
  - `3` → reset/open hand
- Periodically prints:
  - FSM state messages
  - live FSR values
  - servo current values

### Laptop UI

- Desktop interface built with **PySide6**
- Connects to STM32 over **serial**
- Connects to the vision laptop using **ROS 2 Jazzy**
- Supports **Manual Mode** and **Auto Mode**
- Displays:
  - active finger pattern
  - MCU FSM state
  - FSR live stream
  - current live stream
  - status and debug logs
- Auto-detects likely STM32 serial ports (`/dev/ttyUSB*`, `/dev/ttyACM*`)
- Sends ACK / status / state feedback back to the vision side

## System Architecture

```text
Vision Laptop
   │
   │ ROS 2
   ▼
Laptop UI (PySide6 + rclpy)
   │
   │ Serial (115200 baud)
   ▼
STM32 MCU
   ├── 5x MG996R / servo outputs
   ├── 9x FSR analog inputs
   ├── 5x INA226 current sensors
   └── PCA9548A I2C multiplexer
```

## MCU Firmware Details

### Hardware used by the firmware

- **STM32 MCU** running Arduino-compatible firmware
- **5 servos**
  - Pinky → `PB13`
  - Ring → `PB14`
  - Middle → `PB15`
  - Index → `PA8`
  - Thumb → `PA11`
- **9 FSR analog inputs**
  - `PB0, PA7, PA6, PA5, PA4, PA3, PA2, PA1, PA0`
- **5 INA226 current sensors**
- **PCA9548A** I2C multiplexer
- I2C pins:
  - `SDA = PB9`
  - `SCL = PB8`

### Motion and control logic

The firmware uses ramp-based servo motion and a grasp FSM with these states:

- `IDLE`
- `CLOSING_FAST`
- `CLOSING_SLOW`
- `TIGHTEN`
- `HOLD`
- `SETTLE`
- `RECOVER`
- `RESETTING`

### FSM summary

- **IDLE**: hand is open and waiting for a valid 5-bit pattern
- **CLOSING_FAST**: enabled fingers move toward an initial fast target
- **CLOSING_SLOW**: slower closing phase to detect contact more carefully
- **TIGHTEN**: fingers continue closing further for a secure grasp
- **HOLD**: grasp is maintained when tactile/current conditions indicate contact
- **SETTLE**: hand pauses after tightening to observe contact stability
- **RECOVER**: if contact appears to drop, fingers reopen slightly and retry tightening
- **RESETTING**: all fingers open/spread back to the reset position

### Grasp triggers used in firmware

The firmware transitions based on filtered sensor values, including:

- large FSR changes during slow closing
- high motor current during slow closing or tightening
- low FSR + low current for release from hold
- contact drop detection during settle

### Serial command protocol

The MCU accepts only three command types:

- **5-bit pattern** such as `10110`
- **`2`** → start grasp
- **`3`** → reset/open

Typical sequence:

```text
10110
2
```

Reset can be requested at any time:

```text
3
```

### MCU serial output examples

The MCU prints different message classes that the UI parses:

- FSM state lines:
  ```text
  1234,[STATE] CLOSING_FAST
  ```
- FSR stream:
  ```text
  1234,FSR Live: Little=12.00, Ring=25.00, ...
  ```
- Current stream:
  ```text
  1234,1800,Little=220 mA, Ring=310 mA, ...
  ```

## Laptop UI Details

### Technologies

- Python 3
- PySide6
- pyserial
- ROS 2 Jazzy
- `rclpy`
- `std_msgs`

### ROS 2 topics

The UI uses absolute ROS topic names for cross-machine consistency:

- `/finger_pattern_request` → UI requests a pattern from the vision laptop
- `/finger_pattern` → vision laptop sends a 5-bit finger pattern
- `/finger_pattern_ack` → UI publishes ACK / STATE / STATUS / AUTO messages
- `/finger_control_cmd` → vision laptop sends commands such as `Grab`, `Idle?`, `State?`

### Manual mode

Manual mode is intended for supervised operation:

1. Request pattern through ROS
2. Receive a valid 5-bit pattern
3. Send the pattern to the MCU
4. Start grasping
5. Reset/open when needed

### Auto mode

Auto mode is intended for tighter integration with the vision laptop:

1. Request pattern through ROS
2. Receive a valid 5-bit pattern
3. UI sends ACK and state feedback over ROS
4. UI can automatically forward the pattern to the MCU
5. When a `Grab` command is received and the MCU is idle, the UI starts grasping automatically

### Safety / guard behavior in the UI

The UI includes several checks:

- blocks invalid serial commands
- only accepts:
  - a 5-bit pattern
  - `2`
  - `3`
- prevents grasp start before pattern is sent in manual mode
- clears stored pattern on reset/open
- tracks MCU FSM state from `[STATE]` lines
- replies to the vision side with `STATE:Idle`, `STATE:Not Idle`, or `STATE:Unknown`

## File Structure

```text
.
├── mcu_code.ino / main firmware source
├── laptop_ui.py / PySide6 + ROS 2 + serial UI
└── README.md
```

Rename the source files to match your preferred project layout if needed.

## Setup

### 1. MCU firmware

Build the firmware in your Arduino-compatible STM32 environment.

You will need the required libraries used by the code, including:

- `Servo`
- `Wire`
- `INA226_WE`

Upload the firmware to the STM32 board.

### 2. Laptop UI environment

Install Python dependencies:

```bash
pip install PySide6 pyserial
```

For ROS 2 Jazzy, make sure your ROS environment is sourced before running the UI.

Example:

```bash
source /opt/ros/jazzy/setup.bash
```

If you are using a workspace overlay, source that as well.

### 3. Run the laptop UI

```bash
python3 laptop_ui.py
```

## Typical Usage

### Manual workflow

1. Connect the STM32 over serial
2. Enable **Manual Mode**
3. Click **Request Pattern (ROS)**
4. Wait for a valid 5-bit pattern from the vision laptop
5. Click **Send Pattern to MCU**
6. Click **Start Grasping**
7. Use **Reset/Open** to reopen the hand

### Auto workflow

1. Connect the STM32 over serial
2. Enable **Auto Mode**
3. Request a pattern or wait for the vision-side interaction
4. Let the UI exchange ACK / STATE / STATUS through ROS
5. When `Grab` is received and the MCU is in `IDLE`, the UI starts the grasp automatically
6. Use **Reset/Open (Auto)** when needed

## Accepted Commands and Messages

### Serial commands sent to MCU

- Pattern: `10110`
- Start: `2`
- Reset/Open: `3`

### ROS command examples received by the UI

- `Grab`
- `Idle?`
- `State?`

### ROS messages published by the UI

- `ACK:<pattern>`
- `STATE:Idle`
- `STATE:Not Idle`
- `STATE:Unknown`
- `STATUS:<text>`
- `AUTO:On`
- `AUTO:Off`

## Notes

- The UI currently looks for STM32 serial ports under `/dev/ttyUSB*` and `/dev/ttyACM*`.
- The MCU only allows pattern updates while in `IDLE`.
- Reset/open clears the currently stored pattern in the UI.
- The grasp control behavior depends on tactile thresholds, current thresholds, and filtered sensor readings defined in the firmware.

