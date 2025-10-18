# 🤖 Final Year Project: Vision-Guided, Feedback-Enabled Robotic Hand End-Effector

This repository contains code and resources for the **Final Year Project** on developing a **vision-guided, feedback-enabled robotic hand end-effector** for adaptive grasping tasks.

The project focuses on integrating embedded microcontrollers, sensors, and control logic to enable precise and adaptive manipulation of objects.

---

## 📂 Repository Structure

- **ESP32 Tests**  
  Contains code for testing and verifying ESP32 functionalities, including sensor interfacing, communication protocols, and actuator control.

- **STM32 Black Pill (WeAct V3.0 STM32F401CEU6)**  
  Contains firmware for the STM32 microcontroller handling low-level control, sensor readings, and communication with the main control system.

---

## 🔧 Supported Hardware

| Component | Description |
|-----------|-------------|
| STM32F401CEU6 | WeAct Black Pill V3.0 microcontroller board |
| ESP32 | Microcontroller for high-level logic and testing |
| Robotic Hand End-Effector | Custom-designed hand with actuators and sensors |
| Sensors | Includes force, touch, or other feedback sensors for adaptive grasping |
| Camera / Vision Module | For vision-guided object detection and grasp planning |

---

## 💻 Usage

1. Clone the repository to your local machine:

```bash
git clone git@github.com:DasDNS/Robotic_End_Effector_FYP.git
cd Robotic_End_Effector_FYP
```

2. Open the relevant folder in **PlatformIO** or your preferred IDE.

3. Select the target microcontroller:
   - STM32: WeAct Black Pill V3.0 (STM32F401CEU6)
   - ESP32: ESP32 Dev Module

4. Upload the corresponding firmware to the board.

5. Monitor serial output using **PlatformIO Serial Monitor** or VS Code Serial Monitor.

6. Run the ESP32 tests to validate sensors and communication.

---

## 🧠 Project Overview

The robotic hand end-effector system is designed to:

- Perform **adaptive grasping** using real-time feedback from sensors.
- Utilize **vision guidance** to detect object shapes, size, and orientation.
- Integrate **ESP32 and STM32 microcontrollers** for distributed control.
- Provide a framework for **testing different grasp strategies** and analyzing sensor data.

---

## ✅ Summary

| Parameter | Description |
|-----------|-------------|
| Project | Vision-Guided, Feedback-Enabled Robotic Hand End-Effector |
| Microcontrollers | STM32F401CEU6 (Black Pill), ESP32 |
| IDE / Platform | PlatformIO (VS Code) |
| Purpose | Adaptive grasping, sensor feedback, vision guidance |
| Contents | ESP32 tests, STM32 firmware, sensor interfacing, actuator control |

---

✨ _This repository serves as the software foundation for the FYP robotic hand end-effector system, enabling vision-guided and feedback-driven adaptive grasping tasks._