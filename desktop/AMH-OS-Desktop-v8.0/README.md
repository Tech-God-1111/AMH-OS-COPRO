# AMH-OS Desktop v8.0

Release-candidate foundation for the AMH-OS Windows-hosted desktop shell.

## Features
- Full-screen desktop, Start menu, app shortcuts and taskbar app switching.
- File Explorer, PowerShell terminal, live system monitor, persistent Notes and safe arithmetic Calculator.
- USB Serial Monitor with COM discovery, send/receive and connect/disconnect.
- Hardware Center for JSON identify/ping/status requests to compatible ESP32 bridge firmware.
- Appearance preview and Diagnostics report with persistent log access.
- Startup exception reporting and logs under %APPDATA%\\AMH-OS.

## Install and run
Requires Windows 10/11 and Python 3.10+.

```powershell
python -m pip install -r requirements.txt
python -u main.py
```

## Important limitations
This is a Windows-hosted desktop-shell application, not a standalone bootable OS. Quick Settings and Appearance are preview controls. Hardware Center needs firmware that accepts newline-delimited JSON over the selected USB serial port. The current coprocessor link firmware uses UART between the ESP32-S3 and ESP32-WROOM; the PC-facing USB command bridge still needs to be implemented and tested. Test this release before treating it as stable.
