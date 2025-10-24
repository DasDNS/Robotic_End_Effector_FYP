---

# ESP32 Servo Motor Control Example

## 🧩 Overview

This project demonstrates how to control a **servo motor** using an **ESP32** microcontroller and the **ESP32Servo** library.
The servo motor smoothly rotates between **0° and 180°**, then back again in an endless loop.

---

## ⚙️ Hardware Setup

**Microcontroller:** ESP32
**Servo Motor:** MG90S / SG90 / MG996R (or any standard 3-pin hobby servo)
**Power Supply:** 5V DC (separate supply recommended for stable operation)

### 🔌 Pin Configuration

| ESP32 Pin | Servo Pin | Description                           |
| --------- | --------- | ------------------------------------- |
| GPIO 26   | Signal    | PWM control signal                    |
| 5V        | VCC       | Power for servo motor                 |
| GND       | GND       | Common ground between ESP32 and servo |

> ⚠️ Note: Servo motors can draw significant current. If the ESP32 resets or behaves erratically, power the servo from an external 5V source and connect the grounds together.

---

## 💻 Code Explanation

```cpp
#include <ESP32Servo.h>

#define SERVO_PIN 26 // ESP32 pin GPIO26 connected to servo motor

Servo servoMotor;

void setup() {
  servoMotor.attach(SERVO_PIN);  // Attach the servo to pin 26
}

void loop() {
  // Sweep from 0° to 180°
  for (int pos = 0; pos <= 180; pos++) {
    servoMotor.write(pos);
    delay(5);
  }

  // Sweep from 180° back to 0°
  for (int pos = 180; pos >= 0; pos--) {
    servoMotor.write(pos);
    delay(5);
  }
}
```

### 🧠 How It Works

1. The servo motor is attached to GPIO 26.
2. The loop gradually increases the angle from **0° to 180°**, then decreases it back.
3. Each movement is delayed by 5 milliseconds for smooth motion.

---

## 📦 Library Installation

You must install the **ESP32Servo** library before uploading the code.

### Steps (Arduino IDE):

1. Open **Sketch → Include Library → Manage Libraries...**
2. Search for **ESP32Servo**
3. Click **Install**

Or, if using PlatformIO, add this line to your `platformio.ini`:

```
lib_deps = ESP32Servo
```

---

## 🧪 Expected Output

* The servo should rotate **slowly and smoothly** from 0° → 180°, then back 180° → 0°.
* This motion repeats indefinitely.

---

## 🔋 Power Considerations

* The servo can draw **up to 500 mA or more** under load.
* Avoid powering the servo directly from the ESP32’s 3.3V pin.
* Always use a **separate 5V power source** with common ground.

---

## 📸 Example Circuit Diagram

```
       +5V (External or USB)
          |
          |        Servo Motor
          |      +-----------+
          +------| VCC       |
                 | Signal ---|<---- GPIO26 (ESP32)
          +------| GND       |
          |      +-----------+
          |
         GND
          |
       +--+---------------------+
       |        ESP32           |
       |    (GND & GPIO26)      |
       +-------------------------+
```

---

## 🧠 Summary

This example shows how easily an ESP32 can control servo motors using PWM signals with the `ESP32Servo` library.
You can adapt this example for robotic arms, pan-tilt cameras, or other motion-control projects. </br>
Refer: [esp32-servo-motor](https://esp32io.com/tutorials/esp32-servo-motor)

---
<img width="912" height="445" alt="image" src="https://github.com/user-attachments/assets/ebfa07ec-179f-48b0-84bf-45b81644871a" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/2f0d326d-d8b7-462b-b0a5-34c98a2799b1" />

<iframe width="560" height="315" src="" 
title="YouTube video player" frameborder="0" allowfullscreen></iframe>
<video width="640" controls>
  <source src="https://github.com/user-attachments/assets/8201881d-a845-44b4-9b8e-72ce573bcf3e" type="video/mp4">
  Your browser does not support the video tag.
</video>
