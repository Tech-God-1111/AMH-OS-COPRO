# AMH-OS Desktop v5.0

Adds USB Serial Monitor: COM-port discovery, baud selection, connect/disconnect, send and receive.

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
- Hardware Center is not included in this release; the JSON command interface first appears in v6.0 and requires a compatible PC-to-S3 bridge.

## Troubleshooting
Run with `python -u main.py`. Startup and runtime logs are written to `%APPDATA%\\AMH-OS\\amh-os.log`.
