# AMH-OS Desktop v3.0

A Windows-hosted desktop-shell prototype built with Python and PySide6.

## New in v3.0
- Desktop right-click menu: refresh, New note, Settings and About.
- Quick Settings preview panel (the toggles do not change Windows settings).
- Start menu app search and taskbar app switching.
- Notes app with session-only save.
- Calculator with a restricted AST arithmetic evaluator; it does not use eval().
- File Explorer, PowerShell command runner and live CPU/RAM/disk monitor.
- F11 toggles fullscreen; Esc closes desktop panels; Ctrl+Shift+Q exits.

## Install and run
Requires Windows 10/11, Python 3.10+, PySide6 and psutil.

```powershell
python -m pip install -r requirements.txt
python main.py
```

## Important
AMH-OS v3.0 runs as an application on Windows. It is not independently bootable. Quick Settings are visual previews, Notes are stored only for the current session, and Terminal commands execute in Windows PowerShell. Only run commands you understand.
