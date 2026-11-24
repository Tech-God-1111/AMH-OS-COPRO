# AMH-OS COPRO

AMH-OS COPRO is an embedded ESP32 communication bring-up project plus a Windows-hosted desktop-shell prototype. The desktop app is not a bootable replacement for Windows or a standalone embedded operating system.

## Project layers

1. **Embedded firmware** — ESP32-S3 N16R8 main controller and ESP32-WROOM-32 coprocessor.
2. **Communication** — 3.3 V UART, 115200 baud, 8N1, newline-delimited JSON.
3. **Desktop environment** — Python/PySide6 Windows application with a Start menu, desktop shortcuts, taskbar, utility apps and serial tools.

## Current desktop development branch

The maintained desktop development line is **v10.2**:

- Branch: https://github.com/Tech-God-1111/AMH-OS-COPRO/tree/v10.2
- Desktop source directory: desktop/AMH-OS-Desktop-v10.0/
- Release notes and setup: https://github.com/Tech-God-1111/AMH-OS-COPRO/blob/v10.2/desktop/AMH-OS-Desktop-v10.0/README.md

Earlier branches (v2.0 through v8.0 and v10.0) are retained as historical snapshots. The original main branch contains the v0.1 desktop and embedded bring-up files.

### Download and run v10.1 on Windows

Run these commands in PowerShell:

    git clone --branch v10.2 --single-branch https://github.com/Tech-God-1111/AMH-OS-COPRO.git
    cd AMH-OS-COPRO\desktop\AMH-OS-Desktop-v10.0
    python -m pip install -r requirements.txt
    python -u main.py

Python 3.10+ and Windows 10/11 are required.

The v10.2 desktop adds a Connectivity Hub that opens Windows Wi-Fi and Bluetooth settings, plus an Internet desktop icon that opens the system's default browser.

## Hardware

- Main processor: ESP32-S3 N16R8 (16 MB flash, 8 MB PSRAM)
- Coprocessor: ESP32-WROOM-32
- Display: not yet selected
- Inter-processor link: 3.3 V UART, 115200 baud, newline-delimited JSON

## Firmware options

### Arduino IDE (C++)

- Main controller: firmware/arduino/main-esp32s3/AMH_OS_Main_S3/AMH_OS_Main_S3.ino
- Coprocessor: firmware/arduino/coprocessor-esp32/AMH_OS_Copro_WROOM/AMH_OS_Copro_WROOM.ino
- Install **ArduinoJson 7.x** using Arduino IDE Library Manager.
- Follow the Arduino IDE setup guide at docs/arduino-ide-setup.md.

### MicroPython

The original MicroPython bring-up scripts remain in firmware/main-esp32s3/ and firmware/coprocessor-esp32/.

## Hardware and safety status

The ESP32 boards are independent MCUs and communicate over UART; they do not share memory. Firmware and wiring must be validated against the exact development-board revisions before powering or flashing. The Arduino sketches have not been physically validated on every supported board revision.

The desktop Hardware Center needs a PC-to-ESP32-S3 USB JSON bridge. The current main-controller sketch does not yet implement that PC-facing bridge, so the desktop-to-hardware command path is not end-to-end ready. The v10.1 serial parser fix does not replace that missing firmware component.

The six v10 processing-suite applications are still interface-first. Task contracts and tests are groundwork only; live workload monitoring, autonomous dispatch, Uno worker firmware and recovery actions are not implemented.

Read hardware/wiring.md, communication/protocol.md, and docs/arduino-ide-setup.md before wiring or uploading.
