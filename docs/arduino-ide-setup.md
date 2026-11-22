# Arduino IDE setup

Native Arduino C++ sketches are provided below. The original MicroPython files remain available.

## 1. Install Arduino IDE and ESP32 support

1. Install Arduino IDE 2.x.
2. In Boards Manager, install **esp32 by Espressif Systems**.
3. In Library Manager, search for and install **ArduinoJson** (version 7.x).

## 2. Upload the coprocessor first

1. Open `firmware/arduino/coprocessor-esp32/AMH_OS_Copro_WROOM/AMH_OS_Copro_WROOM.ino`.
2. Select **ESP32 Dev Module** (or the exact WROOM-32 board profile).
3. Select the coprocessor USB/serial port and upload.
4. Open Serial Monitor at 115200 baud.

## 3. Upload the main controller

1. Open `firmware/arduino/main-esp32s3/AMH_OS_Main_S3/AMH_OS_Main_S3.ino`.
2. Select **ESP32S3 Dev Module** or the exact S3 board profile.
3. If available, select 16 MB flash and 8 MB OPI PSRAM to match the N16R8. Menu options vary by board/core version.
4. Select the S3 port and upload. Open Serial Monitor at 115200 baud.
5. With both boards connected, expect the coprocessor identity and periodic Coprocessor link: OK messages.

## 4. UART wiring

| ESP32-S3 main | ESP32-WROOM-32 coprocessor |
|---|---|
| GPIO17 TX | GPIO16 RX |
| GPIO18 RX | GPIO17 TX |
| GND | GND |

UART is 115200 baud, 8N1, newline-delimited JSON. The sketches use UART1 on the S3 and UART2 on the WROOM.

## Important hardware checks

- Verify exact board pinouts. GPIO availability and board menu options vary.
- Confirm the coprocessor is an original ESP32-WROOM-32, not a WROVER variant that may use GPIO16/17 for PSRAM.
- Initially power each board from its own USB connection and connect GND. Do not connect their 3V3 or 5V/VIN rails together.
- UART GPIO is 3.3 V logic; never apply 5 V to an ESP32 GPIO.
- Some S3 boards require USB CDC or upload-mode Tools settings; follow the board maker's guidance.

## Troubleshooting

- No identity/ping response: check crossed TX/RX, common GND, power, selected serial ports, and GPIO pin conflicts.
- ArduinoJson.h missing: install ArduinoJson 7.x through Library Manager.
- Upload failure: verify board profile and port; some boards require holding BOOT while upload begins.
- This is initial bring-up firmware and has not been physically tested on your specific board revisions.
