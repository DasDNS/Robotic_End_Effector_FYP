# Vision-Guided Robotic Hand End Effector Control System

This project implements a vision-guided robotic hand end-effector with tactile and current-feedback-assisted grasp control.

The system is split into two main parts:

- **MCU firmware** running on an STM32-based controller for finger actuation, FSR sensing, current sensing, and finite-state grasp control.
- **Laptop UI application** running on a laptop to communicate with the MCU over serial and receive grasp patterns from a vision laptop over **ROS 2 Jazzy**.

## System Overview

The workflow is:

1. The **vision laptop** determines the grasp pattern as a 5-bit finger activation string.
2. The **laptop UI** requests that pattern through ROS 2.
3. The UI sends the received pattern to the **STM32 MCU** over serial.
4. The MCU starts grasping when commanded.
5. The MCU monitors:
   - **FSR sensor values** for tactile/contact feedback
   - **INA226 current readings** for motor load feedback
6. Based on those signals, the MCU transitions through grasp-control FSM states such as fast closing, slow closing, tighten, hold, settle, and recover.

## Project Structure

```text
.
├── mcu_firmware.ino        # STM32/Arduino-style firmware for robotic hand control
├── laptop_ui.py            # PySide6 + ROS 2 + serial UI application
└── README.md
```

## Main Features

### MCU firmware

- Controls **5 servo-driven fingers**
- Reads **9 FSR sensors**
- Reads **5 INA226 current sensors** through a **PCA9548A I2C multiplexer**
- Uses a **finite state machine (FSM)** for adaptive grasping
- Supports:
  - pattern storage
  - start grasp command
  - reset/open command
- Prints live **FSR**, **current**, and **state** messages over serial for monitoring

### Laptop UI

- Built with **PySide6**
- Connects to STM32 through **serial**
- Communicates with the vision side using **ROS 2 Jazzy**
- Requests finger patterns from the vision laptop
- Displays:
  - active finger pattern
  - FSM state
  - FSR log stream
  - current log stream
  - status/debug messages
- Sends ACK messages back over ROS after receiving a pattern

## Hardware Components

The MCU firmware is designed around the following hardware:

- **STM32 MCU** running Arduino-style firmware
- **5 servo motors**
  - Pinky
  - Ring
  - Middle
  - Index
  - Thumb
- **9 FSR sensors**
  - Little
  - LittlePalm
  - Ring
  - RingPalm
  - Middle
  - Index
  - IndexPalm
  - Thumb
  - ThumbPalm
- **5 INA226 current sensors**
- **PCA9548A I2C multiplexer**

## Pin Mapping

### Servo pins

| Finger | Pin |
|---|---|
| Pinky | `PB13` |
| Ring | `PB14` |
| Middle | `PB15` |
| Index | `PA8` |
| Thumb | `PA11` |

### FSR pins

| Sensor | Pin |
|---|---|
| Little | `PB0` |
| LittlePalm | `PA7` |
| Ring | `PA6` |
| RingPalm | `PA5` |
| Middle | `PA4` |
| Index | `PA3` |
| IndexPalm | `PA2` |
| Thumb | `PA1` |
| ThumbPalm | `PA0` |

### I2C

- SDA: `PB9`
- SCL: `PB8`
- INA226 address: `0x40`
- PCA9548A address: `0x70`

## Software Stack

### MCU side

- Arduino framework
- `Wire`
- `Servo`
- `INA226_WE`

### Laptop side

- Python 3
- PySide6
- pyserial
- ROS 2 Jazzy
- `rclpy`
- `std_msgs`

## ROS 2 Interface

The laptop UI uses the following ROS topics:

| Topic | Direction | Purpose |
|---|---|---|
| `finger_pattern_request` | UI → vision laptop | Request a grasp pattern |
| `finger_pattern` | vision laptop → UI | Return a 5-bit grasp pattern |
| `finger_pattern_ack` | UI → vision laptop | Send acknowledgment after receiving a pattern |

### Pattern format

Patterns are sent as a **5-bit binary string**:

```text
00000 to 11111
```

Finger order:

```text
Pinky Ring Middle Index Thumb
```

A value of:

- `1` = finger enabled for grasp
- `0` = finger disabled/open

Example:

```text
01110
```

This enables Ring, Middle, and Index while leaving Pinky and Thumb disabled.

## Serial Protocol (UI ↔ MCU)

The MCU accepts only the following line-based commands:

- **5-bit pattern**: stores the finger selection pattern
- **`2`**: start grasp
- **`3`**: reset/open hand

### Allowed examples

```text
10111
2
3
```

### Serial behavior

- Serial baud rate: **115200**
- Commands are sent as **LF-terminated lines**
- The firmware rejects unsupported commands

## MCU Finite State Machine

The MCU firmware uses the following states:

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
Hand is open and waiting for a valid 5-bit pattern and start command.

#### `CLOSING_FAST`
Enabled fingers move quickly toward the initial closing target.

#### `CLOSING_SLOW`
Fingers continue closing more carefully while monitoring for large FSR change or high motor current.

#### `TIGHTEN`
Fingers continue tightening toward the minimum pulse width at a reduced speed.

#### `HOLD`
The hand stops closing and holds the grasp when contact/load is detected.

#### `SETTLE`
The hand stays still after tightening. If contact is later lost, recovery logic can trigger.

#### `RECOVER`
The hand partially reopens and then retries tightening to re-establish grasp.

#### `RESETTING`
The hand opens/spreads back to the reset position.

## Control Logic Highlights

The firmware combines tactile and motor-current feedback.

### Tactile-based transitions

- A **large FSR change** during slow closing can trigger `HOLD`
- In `SETTLE`, if strong contact existed earlier and later all sensors drop low, the system can enter `RECOVER`

### Current-based transitions

- High filtered current on enabled fingers can trigger `HOLD`
- Low contact and low current for a debounce period can move `HOLD` back to `TIGHTEN`

### Per-finger speed scaling

The firmware supports per-finger speed multipliers. In this version, the ring finger is intentionally given larger multipliers during several closing phases.

## Important Firmware Parameters

Some key parameters from the firmware:

- Servo range:
  - `SERVO_MIN_US = 500`
  - `SERVO_MAX_US = 2400`
- Full sweep time:
  - `FULL_SWEEP_TIME_SEC = 12.0`
- Reset sweep time:
  - `RESET_SWEEP_TIME_SEC = 6.0`
- Fast target:
  - `FAST_TARGET_US = 1600`
- Slow target:
  - `SLOW_TARGET_US = 1000`
- Recover spread target:
  - `RECOVER_SPREAD_US = 900`

## UI Workflow

Recommended workflow in the laptop UI:

1. Connect to the STM32 serial port
2. Click **Request Pattern (ROS)**
3. Wait for the 5-bit pattern from the vision laptop
4. Click **Send Pattern to MCU**
5. Click **Start Grasping**
6. Use **Reset/Open** to reopen the hand when needed

The UI guards against starting a grasp before a pattern is sent to the MCU.

## Serial Output Categories

The laptop UI classifies incoming MCU lines into:

- **FSM state lines**
- **FSR lines**
- **Current lines**
- **Other status messages**

### Example output types

#### FSM state

```text
12345,[STATE] CLOSING_SLOW
```

#### FSR output

```text
12345,FSR Live: Little=0.00, LittlePalm=0.00, ...
```

#### Current output

```text
12345,1400,Little=120.0 mA, Ring=130.0 mA, ...
```

## Setup Instructions

### 1. MCU firmware

- Open the firmware in your Arduino-compatible STM32 environment
- Install required libraries:
  - `INA226_WE`
  - Servo library support for your STM32 environment
- Flash the firmware to the MCU
- Ensure the hardware is wired according to the pin map above

### 2. Laptop UI dependencies

Install Python dependencies:

```bash
pip install PySide6 pyserial
```

Install ROS 2 Jazzy Python support in your ROS environment.

### 3. Source ROS 2

Before running the UI, source your ROS 2 Jazzy environment.

Example:

```bash
source /opt/ros/jazzy/setup.bash
```

If you also have a workspace for the vision node, source that as well.

### 4. Run the UI

```bash
python3 laptop_ui.py
```

## ROS / Network Notes

For the UI and vision laptop to communicate correctly:

- both machines must be on the same ROS 2 network setup
- `ROS_DOMAIN_ID` must match
- DDS/network discovery must work between the devices
- the vision side must publish on `finger_pattern` and subscribe to `finger_pattern_request`

## Safety / Usage Notes

- Always verify the correct serial port before connecting
- Test with low-risk objects first
- Make sure servo power and grounding are stable
- Use reset/open before sending a new pattern if the hand is busy
- The firmware only accepts a new pattern when in `IDLE`

## Troubleshooting

### UI says no serial port found

- Check USB connection
- Confirm the STM32 appears as `/dev/ttyUSB*` or `/dev/ttyACM*`
- Refresh or auto-detect ports from the UI

### ROS pattern is not received

- Check that ROS 2 Jazzy is sourced
- Confirm the vision laptop node is running
- Verify topic names match exactly
- Check `ROS_DOMAIN_ID` and network connectivity

### MCU does not start grasping

- Ensure a valid 5-bit pattern was sent first
- Then send command `2`
- Check that the MCU is in `IDLE`

### MCU rejects commands

Only these are accepted:

- a 5-bit binary pattern
- `2`
- `3`

## Future Extensions

Possible improvements for future versions:

- richer grasp-pattern metadata from the vision side
- logging to CSV files from the UI
- more advanced grasp adaptation using sensor fusion
- configurable thresholds from the UI
- ROS-based publishing of MCU sensor feedback

## License

Add your preferred license here.

## Author

Add your name and affiliation here.
