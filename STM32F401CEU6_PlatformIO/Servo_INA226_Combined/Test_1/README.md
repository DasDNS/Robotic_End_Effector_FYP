# MG996R Servo + INA226 Current Sensor Test (STM32 Black Pill)
This file contains the test sketch, wiring notes, the raw serial output, and an analysis of the measured currents.

---

## Hardware & Wiring

- Microcontroller: STM32F401CEU6 (WeAct Black Pill V3.0)
- Servo: MG996R (external 5V supply)
- INA226: I2C current sensor (followed how2electronics tutorial)
- I2C pins: SDA=PB9, SCL=PB8; Servo pin PB13

Important: INA226 must measure across a shunt resistor in series with the load (VIN+/VIN-). Ensure the servo current flows through the shunt.

---

## Sketch (main.ino)

```
#include <Arduino.h>
#include <Wire.h>
#include <Servo.h>
#include <INA226.h>

// ====== Objects ======
Servo myservo;
INA226 *ina = nullptr;

// ====== Pin Definitions ======
#define SERVO_PIN PB13
#define SDA_PIN PB9
#define SCL_PIN PB8

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\n=== MG996R Servo + INA226 Current Sensor Test ===");

  // Initialize I2C
  Wire.setSDA(SDA_PIN);
  Wire.setSCL(SCL_PIN);
  Wire.begin();

  // ====== Scan for I2C Devices ======
  Serial.println("Scanning I2C bus...");
  bool found = false;
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("Found I2C device at 0x");
      Serial.println(addr, HEX);
      if (addr == 0x40) found = true; // INA226 default address
    }
  }

  // ====== Initialize INA226 ======
  if (found) {
    Serial.println("INA226 detected! Initializing...");
    ina = new INA226(0x40, &Wire);
    ina->setMaxCurrentShunt(0.02, 0.1); // 0.02Ω shunt, 0.1A max (adjust if needed)
    if (!ina->begin()) {
      Serial.println("INA226 initialization failed!");
      while (1);
    }
    Serial.println("INA226 initialized successfully!");
  } else {
    Serial.println("INA226 not found on I2C bus.");
  }

  // ====== Attach Servo ======
  myservo.attach(SERVO_PIN);
  Serial.println("Servo attached to PB13.");
  delay(1000);
}

void printINA226Data() {
  if (!ina) return;
  
  float busVoltage = ina->getBusVoltage();      // in V
  float shuntVoltage = ina->getShuntVoltage();  // in mV
  float current_mA = ina->getCurrent_mA();      // in mA
  float power_mW = ina->getPower_mW();          // in mW

  Serial.print("Bus Voltage: "); Serial.print(busVoltage); Serial.println(" V");
  Serial.print("Shunt Voltage: "); Serial.print(shuntVoltage); Serial.println(" mV");
  Serial.print("Current: "); Serial.print(current_mA); Serial.println(" mA");
  Serial.print("Power: "); Serial.print(power_mW); Serial.println(" mW");
  Serial.println("----------------------------");
}

void moveServoAndMeasure(int angle, int waitMs) {
  Serial.print("Moving servo to "); Serial.print(angle); Serial.println("°");
  myservo.write(angle);
  unsigned long start = millis();
  while (millis() - start < waitMs) {
    printINA226Data();
    delay(500); // read every 0.5s
  }
}

void loop() {
  if (!ina) {
    Serial.println("INA226 not initialized. Check wiring.");
    delay(2000);
    return;
  }

  moveServoAndMeasure(0, 3000);
  moveServoAndMeasure(180, 3000);
  moveServoAndMeasure(90, 3000);
}

```

---

## Raw Serial Output (verbatim)

```

Bus Voltage: 0.00 V
Shunt Voltage: -0.00 mV
Current: -0.02 mA
Power: 0.00 mW
----------------------------
Bus Voltage: 5.21 V
Shunt Voltage: -0.00 mV
Current: 0.00 mA
Power: 0.15 mW
----------------------------
Bus Voltage: 5.23 V
Shunt Voltage: 0.00 mV
Current: 0.03 mA
Power: 0.15 mW
----------------------------
Bus Voltage: 5.23 V
Shunt Voltage: 0.00 mV
Current: 0.00 mA
Power: 0.00 mW
----------------------------
Bus Voltage: 5.23 V
Shunt Voltage: 0.00 mV
Current: 0.03 mA
Power: 0.15 mW
----------------------------
Moving servo to 180°
Bus Voltage: 5.23 V
Shunt Voltage: 0.00 mV
Current: 0.00 mA
Power: 0.00 mW
----------------------------
Bus Voltage: 5.26 V
Shunt Voltage: 0.00 mV
Current: 0.00 mA
Power: 0.00 mW
----------------------------
Bus Voltage: 5.32 V
Shunt Voltage: 0.00 mV
Current: 0.03 mA
Power: 0.15 mW
----------------------------
Bus Voltage: 5.22 V
Shunt Voltage: 0.00 mV
Current: 0.00 mA
Power: 0.00 mW
----------------------------
Bus Voltage: 5.31 V
Shunt Voltage: 0.00 mV
Current: 0.03 mA
Power: 0.15 mW
----------------------------
Bus Voltage: 5.20 V
Shunt Voltage: 0.00 mV
Current: -0.02 mA
Power: 0.15 mW
----------------------------
Moving servo to 90°
Bus Voltage: 5.31 V
Shunt Voltage: 0.00 mV
Current: 0.00 mA
Power: 0.00 mW
----------------------------
Bus Voltage: 5.19 V
Shunt Voltage: 0.00 mV
Current: 0.03 mA
Power: 0.15 mW
----------------------------
Bus Voltage: 5.30 V
Shunt Voltage: 0.03 mV
Current: 0.03 mA
Power: 0.15 mW
----------------------------
Bus Voltage: 4.18 V
Shunt Voltage: -0.00 mV
Current: -0.02 mA
Power: 0.10 mW
----------------------------
Bus Voltage: 5.29 V
Shunt Voltage: 0.00 mV
Current: 0.00 mA
Power: 0.00 mW
----------------------------
Bus Voltage: 5.32 V
Shunt Voltage: 0.00 mV
Current: 0.03 mA
Power: 0.15 mW
----------------------------
Moving servo to 0°
Bus Voltage: 5.27 V
Shunt Voltage: -0.00 mV
Current: 0.00 mA
Power: 0.15 mW
----------------------------
Bus Voltage: 5.23 V
Shunt Voltage: 0.00 mV
Current: 0.03 mA
Power: 0.15 mW
----------------------------
Bus Voltage: 5.23 V
Shunt Voltage: 0.00 mV
Current: 0.03 mA
Power: 0.00 mW
----------------------------
Bus Voltage: 5.23 V
Shunt Voltage: 0.00 mV
Current: 0.00 mA
Power: 0.00 mW
----------------------------
Bus Voltage: 5.23 V
Shunt Voltage: 0.00 mV
Current: 0.00 mA
Power: 0.00 mW
----------------------------
Bus Voltage: 5.23 V
Shunt Voltage: 0.00 mV
Current: 0.03 mA
Power: 0.15 mW
----------------------------
Moving servo to 180°
Bus Voltage: 5.23 V
Shunt Voltage: 0.00 mV
Current: 0.03 mA
Power: 0.15 mW
----------------------------
Bus Voltage: 5.32 V
Shunt Voltage: 0.00 mV
Current: 0.00 mA
Power: 0.00 mW
----------------------------
Bus Voltage: 5.26 V
Shunt Voltage: 0.00 mV
Current: -0.02 mA
Power: 0.00 mW
----------------------------
Bus Voltage: 5.32 V
Shunt Voltage: 0.00 mV
Current: 0.03 mA
Power: 0.15 mW
----------------------------
Bus Voltage: 5.23 V
Shunt Voltage: 0.00 mV
Current: 0.03 mA
Power: 0.15 mW
----------------------------
Bus Voltage: 5.31 V
Shunt Voltage: 0.00 mV
Current: 0.03 mA
Power: 0.15 mW
----------------------------
Moving servo to 90°
Bus Voltage: 5.20 V
Shunt Voltage: 0.00 mV
Current: 0.00 mA
Power: 0.00 mW
----------------------------

```

---

## Measured Statistics (extracted from the output)

- Number of samples: **30**
- Current (mA): mean = **0.0113 mA**, median = **0.0000 mA**, stdev = **0.0189 mA**, min = **-0.0200 mA**, max = **0.0300 mA**
- Bus Voltage (V): mean = **5.044 V**, min = **0.00 V**, max = **5.32 V**
- Shunt Voltage (mV): mean = **0.0010 mV**, min = **-0.0000 mV**, max = **0.0300 mV**
- Power (mW): mean = **0.0833 mW**, min = **0.0000 mW**, max = **0.1500 mW**

---

## Analysis & Calculations

The INA226 reported currents on the order of ±0.03 mA (tens of microamps) and power readings around 0–0.15 mW. Bus voltage readings are typically ~5.2–5.3 V.

**Expected MG996R currents:**

- Idle/holding: ~100–250 mA
- Moving (light load): ~200–700 mA
- Stall peaks: >1 A (short bursts)

Therefore the reported readings are orders of magnitude smaller than expected. If the servo were drawing 200 mA at 5 V, expected power would be 1000 mW; the INA226 reported mean power is far lower.

### Likely causes & fixes

1. Shunt wiring incorrect — ensure current flows through VIN+ -> VIN- (or external shunt) on the INA226 module.

2. Library calibration — verify you used the correct functions to set shunt resistor and calibration (not only setMaxCurrentShunt).

3. Shunt value vs resolution — for debugging, try a larger shunt (e.g., 0.05–0.1 Ω) temporarily and/or a known resistor load to confirm readings.

4. Ground/reference issues — common ground between servo supply, INA226, and STM32 is required.

5. Noise & averaging — use INA226 averaging or sample many times and average.

### Quick diagnostic test:

Place a known resistor (e.g., 10 Ω) between 5 V and GND instead of the servo (draws 0.5 A). If INA226 still reads ~0 mA, wiring or module is wrong. If it reads ~500 mA, the INA226 and library are OK and the original servo wiring was bypassing the shunt.

---

## Recommended next steps

1. Re-check VIN+/VIN- wiring and that servo V+ is routed through the shunt.
2. Ensure common ground.
3. Use explicit calibration API in library.
4. Test with known resistive load.
5. Optionally increase shunt for easier debugging.

---

**Conclusion:** The measured mean current (~0.0113 mA) is not accurate for an MG996R. Most likely fix: rewire shunt/current path and verify calibration.
