# Servo Calibration Tool for Robotic Hand

This project uses an ESP32 and a servo motor to safely **position the nylon-thread-based tendon system** inside a robotic hand.  
The goal is to move the fingers into specific predefined positions so that the nylon threads can be tightened without getting tangled.

---

## 🛠️ Purpose

Nylon tendon systems in robotic hands can easily twist or tangle if the servo positions are not fixed during assembly.  
This tool lets you send simple commands (`0`, `1`, `2`) via the serial monitor to move the servo into:

| Command | Position Description | Mechanical Purpose |
|---------|----------------------|---------------------|
| `0` | Fully Bent | Tighten bending-side nylon thread |
| `1` | Half Bent | Mid‑point reference position |
| `2` | Fully Straightened | Tighten straightening nylon thread |

---

## 🔧 Hardware Used
- **ESP32 Development Board**
- **Servo Motor** (standard PWM controlled)
- **Nylon tendon mechanism** on robotic finger
- **USB cable** for serial communication

Servo pin used: **GPIO 18**

---

## 📦 PlatformIO Configuration

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino

lib_deps = 
    madhephaestus/ESP32Servo@^3.0.9

monitor_speed = 115200
```

---

## 📜 Code Used

```cpp
#include <Arduino.h>
#include <ESP32Servo.h>

/*
0 Completely bending
1 Half bending  ( Tighten the screw for bending up nylon thread )
2 Completely straightning up ( Tighten the screw for straightning up nylon thread )
*/

Servo myServo;
const int servoPin = 18;

void setup() {
  Serial.begin(115200);
  delay(500);

  myServo.setPeriodHertz(50);  // 50 Hz for analog servos
  myServo.attach(servoPin, 500, 2500);  // Calibrate min/max pulse width

  Serial.println("Enter 0, 1, or 2 to move the servo:");
}

void loop() {
  if (Serial.available()) {
    char command = Serial.read();

    switch (command) {
      case '0':
        myServo.writeMicroseconds(500);  // 0 degrees
        Serial.println("Moved to 0 degrees");
        break;

      case '1':
        myServo.writeMicroseconds(1450);  // ~165 degrees midpoint
        Serial.println("Moved to ~165 degrees");
        break;

      case '2':
        myServo.writeMicroseconds(2400);  // ~330 degrees
        Serial.println("Moved to ~330 degrees");
        break;

      default:
        Serial.println("Invalid command. Use 0, 1, or 2.");
        break;
    }
  }
}
```

---

## 🚀 How to Use

1. Upload the code to your ESP32 using PlatformIO.
2. Open **Serial Monitor** at **115200 baud**.
3. Type one of these commands:
   - `0` → Servo fully bends the finger
   - `1` → Servo moves to midpoint
   - `2` → Servo fully straightens the finger
4. Tighten the nylon tendons based on the position.

---

## 📝 Notes
- Adjust pulse widths (`500–2500 µs`) if your servo has a different range.
- Make sure the finger is not obstructed when testing extreme positions.

---

## 📄 License
MIT — Free to use and modify.
