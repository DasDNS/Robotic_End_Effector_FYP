# 🧠 STM32 Black Pill Servo Motor Control

This project demonstrates how to control a **servo motor** using an **STM32 Black Pill (WeAct V3.0)** board with the **Arduino framework**.  
The servo is rotated between **0°, 90°, and 180°** positions in sequence.

---

## ⚙️ Hardware Setup

### **Components Used**
- STM32 Black Pill (WeAct V3.0)
- Servo motor (e.g., SG90 or MG996R)
- Jumper wires
- External 5V power supply (recommended for servo)
- Common ground between servo and STM32

### **Pin Connections**

| STM32 Pin | Servo Wire | Description |
|------------|-------------|-------------|
| **PA8** | Control (Orange/Yellow) | PWM signal pin |
| **5V (external)** | VCC (Red) | Servo power |
| **GND** | GND (Brown/Black) | Common ground |

> ⚠️ Note: The servo should **not** draw power from the STM32 5V pin if it’s powered over USB — use an external 5V supply to prevent overcurrent issues.

---

## 🧩 Code Overview

### **Source Code**
```cpp
#include <Arduino.h>
#include <Servo.h>

Servo myservo;

void setup() {
  myservo.attach(PA8);  // PWM-capable pin
}

void loop() {
  myservo.write(0);     // move to 0°
  delay(1000);
  myservo.write(90);    // move to 90°
  delay(1000);
  myservo.write(180);   // move to 180°
  delay(1000);
  myservo.write(90);    // return to 90°
  delay(1000);
}
```

---

## 🧠 Working Principle

1. The **Servo library** generates PWM signals on pin **PA8**.
2. The servo interprets pulse widths (typically 1–2 ms) to move to target angles.
3. The loop cycles through angles: 0°, 90°, 180°, and back to 90°, pausing 1 second between each movement.

---

## ⚡ Power & Theoretical Analysis

### Servo Specifications (Example: SG90)
- Operating voltage: 4.8V – 6.0V
- Operating current: ~200–250 mA (idle to moving)
- Stall current: ~650–800 mA
- PWM frequency: 50 Hz (20 ms period)

### Power Estimation
At 5V, if servo draws an average of 250 mA while moving:
\[ P = V \times I = 5V \times 0.25A = 1.25W \]

If using USB (max 500 mA), **use external 5V supply** to avoid brownouts.

---

## 🧪 Testing Notes

- The servo smoothly transitions between the set angles.
- The STM32 Black Pill’s **hardware PWM** provides accurate timing, ensuring stable servo positioning.
- Verified to work with **Arduino Core STM32** installed via the **Boards Manager**.

---

## 🔌 Power and Safety

- Servo motors may draw up to **1A during movement** — use a dedicated 5V supply.
- Always connect **GND of STM32 and external power supply** together to maintain reference.

---

## 🎥 Demonstration

[▶️ Watch demo video]([./demo.mp4](https://www.youtube.com/watch?v=YOUR_VIDEO_ID](https://github.com/user-attachments/assets/b047719a-9d5a-4905-b462-e08ca6b3eb56)
---

## 🧰 References

- [STM32 Black Pill (WeAct V3.0) Pinout](https://stm32-base.org/boards/STM32F401CEU6-WeAct-Black-Pill-V3.0.html)
- [Arduino Servo Library Documentation](https://docs.arduino.cc/libraries/servo/)
- [STM32 BluePill Servo Test 1](https://circuitdigest.com/microcontroller-projects/servo-motor-interfacing-with-stm32f103c8-stm32-development-board)
- [STM32 BluePill Servo Test 2](https://www.mathaelectronics.com/how-to-control-a-servo-motor-with-stm32f103c8t6-blue-pill/)

---

**✅ Result:**  
The servo moves accurately between specified angles, confirming successful PWM signal generation and proper wiring.





