# AMH-OS COPRO

Native embedded operating-system groundwork for an ESP32-S3 N16R8 main processor paired with an original ESP32-WROOM coprocessor.

## Hardware
- Main processor: ESP32-S3 N16R8 (16 MB flash, 8 MB PSRAM)
- Coprocessor: ESP32-WROOM-32
- Display: not yet selected
- Inter-processor link: 3.3 V UART, 115200 baud, newline-delimited JSON

## Status
This is an early bring-up release. Firmware and wiring must be validated against the exact development-board revisions before powering or flashing. The two ESP32 boards are independent MCUs and communicate over UART; they do not share memory.

See `hardware/wiring.md`, `communication/protocol.md`, and the firmware directories for the initial bring-up implementation.
