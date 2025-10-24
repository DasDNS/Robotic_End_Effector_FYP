# INA226 I2C Current, Voltage, and Power Monitor for STM32

This project demonstrates how to interface an **INA226** sensor with an STM32 microcontroller using the **Wire (I2C) library** in Arduino. It scans the I2C bus, detects the INA226 sensor, and reads voltage, current, and power measurements.

---

## Features

- Automatically scans the I2C bus for devices
- Detects INA226 sensor at its default address (0x40)
- Reads and prints:
  - Bus voltage (V)
  - Shunt voltage (mV)
  - Current (mA)
  - Power (mW)
- Compatible with STM32 boards (tested with STM32F4 "Black Pill")
- Gracefully handles cases when INA226 is not connected

---

## Hardware Requirements

- STM32 development board (e.g., Black Pill F401)
- INA226 current/voltage sensor
- Connecting wires
- USB cable for programming and serial monitoring

### Connections (STM32 Black Pill)

| INA226 Pin | STM32 Pin |
|------------|-----------|
| SDA        | PB9       |
| SCL        | PB8       |
| VCC        | 3.3V or 5V |
| GND        | GND       |

---

## Software Requirements

- Arduino IDE or PlatformIO
- [INA226 library](https://github.com/robTillaart/INA226)
- STM32 board support installed in Arduino IDE

---

## Usage

1. Connect your STM32 board and INA226 sensor according to the table above.
2. Open the project in Arduino IDE or PlatformIO.
3. Upload the sketch to your STM32 board.
4. Open the Serial Monitor at **115200 baud**.
5. Observe the output:


---

## Notes

- If the INA226 is not found, check wiring and ensure it is powered correctly.
- The code uses dynamic allocation (`new INA226`) to prevent crashes if the sensor is not detected.
- You can modify the I2C pins according to your STM32 board configuration.

---

## License

This project is open-source and licensed under the MIT License.

---

## References

- [INA226 Datasheet](https://www.ti.com/lit/ds/symlink/ina226.pdf)
- [Rob Tillaart INA226 Arduino Library](https://github.com/robTillaart/INA226)
- [STM32 Arduino Core](https://github.com/stm32duino/Arduino_Core_STM32)

