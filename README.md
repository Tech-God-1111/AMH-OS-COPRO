# AMH-OS COPRO

Native embedded operating-system groundwork for an ESP32-S3 N16R8 main processor paired with an original ESP32-WROOM coprocessor.

## Hardware
- Main processor: ESP32-S3 N16R8 (16 MB flash, 8 MB PSRAM)
- Coprocessor: ESP32-WROOM-32
- Display: not yet selected
- Inter-processor link: 3.3 V UART, 115200 baud, newline-delimited JSON

## Firmware options

### Arduino IDE (C++)
- Main controller: `firmware/arduino/main-esp32s3/AMH_OS_Main_S3/AMH_OS_Main_S3.ino`
- Coprocessor: `firmware/arduino/coprocessor-esp32/AMH_OS_Copro_WROOM/AMH_OS_Copro_WROOM.ino`
- Install **ArduinoJson 7.x** using Arduino IDE Library Manager.
- Follow [Arduino IDE setup](docs/arduino-ide-setup.md).

### MicroPython
The original MicroPython bring-up scripts remain in `firmware/main-esp32s3/` and `firmware/coprocessor-esp32/`.

## Status and safety

This is an early bring-up release. Firmware and wiring must be validated against the exact development-board revisions before powering or flashing. The two ESP32 boards are independent MCUs and communicate over UART; they do not share memory. The Arduino sketches have not yet been physically tested on the user's board revisions.

See `hardware/wiring.md`, `communication/protocol.md`, and `docs/arduino-ide-setup.md` before wiring or uploading.
