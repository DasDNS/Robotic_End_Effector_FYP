# Vision-Guided Robotic Hand End Effector

A two-part robotic hand control system that combines:

- **STM32 MCU firmware** for servo actuation, tactile sensing, current sensing, and grasp-state control.
- **Laptop UI application** built with **PySide6 + ROS 2 Jazzy + serial communication** to receive finger activation patterns from a vision system and forward them to the MCU.

The project is designed for **adaptive grasping tasks** where a vision system selects the finger pattern for the target object, and the hand firmware closes, tightens, holds, settles, and recovers using **FSR feedback** and **motor current feedback**.  
fileciteturn6file0L1-L40 fileciteturn6file1L1-L35

---

## System Overview

### 1. MCU firmware
The MCU firmware runs on an STM32-based controller and handles:

- 5 servo outputs for finger actuation
- 9 FSR analog inputs for tactile sensing
- 5 INA226 current sensors through a PCA9548A I2C multiplexer
- A finite state machine (FSM) for grasp control
- A serial command interface for pattern selection, start, and reset  
fileciteturn6file0L10-L40 fileciteturn6file0L58-L88

### 2. Laptop UI
The laptop-side application provides:

- Serial connection to the MCU
- ROS 2 communication with the vision laptop
- Pattern request / receive / ACK workflow
- UI panels for FSM state, FSR data, current data, status, and debug logs
- Safe command gating so only valid MCU commands are sent  
fileciteturn6file1L15-L35 fileciteturn6file1L225-L330

---

## Architecture

```text
Vision Laptop (ROS 2)
    └── publishes 5-bit grasp pattern
            ↓
Laptop UI (PySide6 + ROS 2 + Serial)
    ├── requests pattern from vision node
    ├── receives pattern
    ├── sends ACK back over ROS 2
    └── forwards 5-bit pattern / start / reset to MCU over serial
            ↓
STM32 MCU Firmware
    ├── actuates enabled fingers
    ├── monitors FSR values
    ├── monitors motor current per finger
    └── transitions through grasp FSM states
```

The ROS-side workflow uses three topic names in this version:

- `finger_pattern_request`
- `finger_pattern`
- `finger_pattern_ack`  
fileciteturn6file1L21-L24

---

## Hardware / Signal Mapping

### Servo outputs
The firmware controls five servos mapped as:

- `PB13` → Pinky
- `PB14` → Ring
- `PB15` → Middle
- `PA8` → Index
- `PA11` → Thumb  
fileciteturn6file0L14-L19

### FSR inputs
Nine FSR channels are used:

- `PB0` → Little
- `PA7` → LittlePalm
- `PA6` → Ring
- `PA5` → RingPalm
- `PA4` → Middle
- `PA3` → Index
- `PA2` → IndexPalm
- `PA1` → Thumb
- `PA0` → ThumbPalm  
fileciteturn6file0L44-L57

### Current sensing
Five INA226 sensors are read through a PCA9548A I2C multiplexer on channels 0–4. The firmware explicitly initializes and checks each channel during startup.  
fileciteturn6file0L25-L31 fileciteturn6file0L179-L210 fileciteturn6file0L378-L410

---

## MCU Serial Protocol

The MCU accepts only three kinds of commands:

- **5-bit finger pattern**: `00000` to `11111`
- **`2`** → start grasp
- **`3`** → reset/open  
fileciteturn6file0L422-L469

### Serial workflow
1. Send a **5-bit pattern** while the hand is in `IDLE`
2. Send **`2`** to begin grasping
3. Send **`3`** at any time to reset and reopen the hand  
fileciteturn6file0L413-L420 fileciteturn6file0L422-L469

### Pattern meaning
Each bit in the 5-bit pattern enables one finger in this order:

`[Pinky, Ring, Middle, Index, Thumb]`  
fileciteturn6file0L357-L364

Example:

- `01110` → Ring, Middle, and Index enabled
- `11111` → all fingers enabled
- `00000` → no fingers selected

---

## ROS 2 Interface

The laptop UI runs a ROS 2 node named `ui_pattern_client` that:

- publishes pattern requests on `finger_pattern_request`
- subscribes to `finger_pattern`
- publishes confirmations on `finger_pattern_ack`  
fileciteturn6file1L142-L166

### UI-side ROS sequence
1. User clicks **Request Pattern (ROS)**
2. UI publishes `REQ`
3. Vision node publishes a 5-bit pattern
4. UI validates the pattern
5. UI sends `ACK:<pattern>` back
6. User clicks **Send Pattern to MCU**
7. User clicks **Start Grasping**  
fileciteturn6file1L206-L222 fileciteturn6file1L500-L531 fileciteturn6file1L654-L664

---

## Grasp FSM

The MCU firmware defines the following states:

- `IDLE`
- `CLOSING_FAST`
- `CLOSING_SLOW`
- `TIGHTEN`
- `HOLD`
- `SETTLE`
- `RECOVER`
- `RESETTING`  
fileciteturn6file0L64-L73

### State summary

#### `IDLE`
Hand is open and waiting for a valid pattern and start command.  
fileciteturn6file0L476-L500

#### `CLOSING_FAST`
Enabled fingers move toward `FAST_TARGET_US = 1600`. Ring finger uses a higher speed multiplier in this stage.  
fileciteturn6file0L32-L39 fileciteturn6file0L508-L524

#### `CLOSING_SLOW`
Enabled fingers continue moving toward `SLOW_TARGET_US = 1000` at reduced speed. The controller checks for:

- large FSR change
- high motor current
- completion of the slow closing ramp  
fileciteturn6file0L32-L39 fileciteturn6file0L526-L550

#### `TIGHTEN`
The fingers tighten further toward `SERVO_MIN_US = 500` using a slower ramp. The state exits to `HOLD` on contact/current events or to `SETTLE` when the target is reached.  
fileciteturn6file0L552-L577

#### `HOLD`
All ramps stop. If both tactile and current signals fall below release thresholds for a debounce period, the controller returns to `TIGHTEN`.  
fileciteturn6file0L126-L133 fileciteturn6file0L579-L596

#### `SETTLE`
No movement occurs. The firmware watches for a contact-drop condition: contact was previously strong, then all FSRs fall below the low threshold.  
fileciteturn6file0L136-L145 fileciteturn6file0L598-L619

#### `RECOVER`
The hand spreads partially to `RECOVER_SPREAD_US = 900`, then retries `TIGHTEN`.  
fileciteturn6file0L32-L39 fileciteturn6file0L621-L641

#### `RESETTING`
All fingers are reopened to `SERVO_MAX_US = 2400`, then the controller returns to `IDLE`.  
fileciteturn6file0L291-L309 fileciteturn6file0L501-L507

---

## Sensing and Control Logic

### FSR processing
The firmware reads nine analog FSR channels and filters them using a low-pass filter with:

- `ALPHA_FSR = 0.20`  
fileciteturn6file0L114-L123 fileciteturn6file0L240-L264

### Current processing
The firmware reads current from five INA226 channels and filters them using:

- `ALPHA_I = 0.20`  
fileciteturn6file0L114-L123 fileciteturn6file0L240-L264

### Key thresholds
Some important thresholds in this version are:

- `I_TIGHTEN_HIGH_MA = 800.0`
- `HOLD_RELEASE_FSR_FRAC = 0.20`
- `HOLD_RELEASE_I_MA = 100.0`
- `HOLD_RELEASE_DEBOUNCE_MS = 350`
- `SETTLE_RECOVER_HIGH_FRAC = 0.30`
- `SETTLE_RECOVER_LOW_ABS = 30.0`
- `SETTLE_RECOVER_DEBOUNCE_MS = 120`  
fileciteturn6file0L126-L145

---

## Laptop UI Features

The PySide6 UI includes:

- serial port discovery for `ttyUSB` / `ttyACM`
- MCU connection and disconnection
- ROS pattern request button
- pattern-to-MCU transfer button
- start and reset buttons
- manual debug send box
- active finger display
- FSM state display
- separate text panels for FSR data, current data, status, and debug logs  
fileciteturn6file1L38-L57 fileciteturn6file1L225-L394

The UI also blocks invalid commands and only allows:

- 5-bit patterns
- `2`
- `3`  
fileciteturn6file1L29-L35 fileciteturn6file1L623-L647

---

## Software Requirements

### MCU side
- Arduino-compatible STM32 environment
- Libraries used in firmware:
  - `Arduino.h`
  - `Wire.h`
  - `Servo.h`
  - `INA226_WE.h`
  - `math.h`  
fileciteturn6file0L1-L5

### Laptop side
- Python 3
- PySide6
- pyserial
- ROS 2 Jazzy
- `rclpy`
- `std_msgs`  
fileciteturn6file1L1-L19

Install the Python dependencies with your preferred environment manager. For example:

```bash
pip install PySide6 pyserial
```

ROS 2 Jazzy packages should be available from your sourced ROS environment.

---

## How to Run

### 1. Upload MCU firmware
Flash the STM32 with the firmware in the MCU code file.

### 2. Source ROS 2 Jazzy
Make sure the laptop terminal has ROS 2 Jazzy sourced before starting the UI.

Example:

```bash
source /opt/ros/jazzy/setup.bash
```

### 3. Run the laptop UI

```bash
python3 your_ui_script.py
```

### 4. Connect to the MCU
In the UI:

- click **Refresh Ports** or **Auto-Detect**
- connect to the STM32 serial port

### 5. Request a vision pattern
- click **Request Pattern (ROS)**
- wait for the 5-bit pattern
- click **Send Pattern to MCU**

### 6. Start grasping
- click **Start Grasping**

### 7. Reset/open the hand
- click **Reset/Open**
- or send `3`  
fileciteturn6file1L585-L603 fileciteturn6file1L654-L664 fileciteturn6file0L422-L469

---

## Expected Serial Output

The MCU periodically prints:

- current data lines in the form `millis,pulse,...mA`
- FSR lines beginning with `FSR Live:`
- state lines such as `[STATE] HOLD`
- UI/status messages such as pattern storage, busy warnings, and reset messages  
fileciteturn6file0L59-L62 fileciteturn6file0L213-L238 fileciteturn6file0L275-L289 fileciteturn6file0L422-L469

The laptop UI classifies incoming lines into:

- FSM
- FSR
- current
- status  
fileciteturn6file1L38-L57

---

## Notes

- New grasp patterns are only accepted when the MCU is in `IDLE`.  
  fileciteturn6file0L436-L453
- Reset works from any state.  
  fileciteturn6file0L479-L487
- The UI enforces the workflow: request pattern → send pattern to MCU → start grasping.  
  fileciteturn6file1L654-L664
- This version uses **relative ROS topic names**, not absolute slash-prefixed names.  
  fileciteturn6file1L21-L24

---

## Project Purpose

This project is suitable for research and development work involving:

- vision-guided robotic grasping
- adaptive end-effector control
- tactile feedback integration
- motor current-based load/contact detection
- FSM-based embedded manipulation control  
fileciteturn6file0L126-L145 fileciteturn6file1L500-L531
