# AMH-OS Desktop v6.0

Adds Hardware Center with JSON identify/ping/status requests over serial for a compatible ESP32-S3 bridge firmware.

## Install
Requires Windows 10/11 and Python 3.10+.

```powershell
python -m pip install -r requirements.txt
python main.py
```

## Runtime notes
- Runs as a desktop shell application on Windows; it is not a bootable OS.
- Use F11 to toggle fullscreen and Ctrl+Shift+Q to exit.
- Logs and persistent Notes are stored under %APPDATA%\\AMH-OS.
- Quick Settings and Appearance entries are previews, not actual Windows system-control APIs.
- Hardware Center sends JSON lines for identify/ping/status. It requires compatible firmware on the selected serial port; the current earlier S3 firmware may need a matching USB-to-UART command bridge before this can work end-to-end.

## Troubleshooting
Run with `python -u main.py`. Startup and runtime logs are written to `%APPDATA%\\AMH-OS\\amh-os.log`.
