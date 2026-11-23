# AMH-OS Desktop v2.0

A full-screen desktop-shell prototype built with Python and PySide6. This version adds a desktop canvas, clickable shortcuts, a Start menu with app search, a taskbar with running-app buttons and clock, plus working prototype apps.

## Features

- Full-screen AMH-OS desktop with a custom, locally drawn abstract wallpaper
- Clickable desktop shortcuts
- Start menu with live app filtering
- Taskbar with running application buttons and clock
- File Explorer for browsing folders and opening files
- PowerShell terminal (runs commands on the Windows host)
- Live CPU, memory and system-drive monitor
- Settings and About windows
- F11 toggles full-screen; Esc closes the Start menu; Ctrl+Shift+Q exits

## Important

AMH-OS v2.0 is still a desktop environment prototype running on top of Windows. It is not a standalone bootable operating system, and its Terminal executes commands on the Windows host. Save your work before experimenting with terminal commands.

## Run on Windows

From this folder in PowerShell:

    py -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    .\.venv\Scripts\python.exe main.py

If you already have a virtual environment, activate it and install the requirements:

    python -m pip install -r requirements.txt
    python main.py

## Exit

Press Ctrl+Shift+Q or use Start > Power > Exit AMH-OS.
