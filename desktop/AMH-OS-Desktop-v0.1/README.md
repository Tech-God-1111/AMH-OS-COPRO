# AMH-OS Desktop v0.1

A Windows-style desktop application prototype built with Python and PySide6.

## Requirements
- Windows 10/11
- Python 3.10 or newer

## Install
Open a terminal in this folder:

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run

```powershell
python main.py
```

## Current features
- Dashboard with host CPU, RAM and disk usage (via psutil)
- Navigation sidebar
- COM-port discovery (via pyserial)
- Basic folder browser
- Launches Windows Command Prompt
- Settings / project information

## Hardware integration status
The ESP32-S3 and ESP32-WROOM-32 UART link has been tested independently. This desktop prototype only discovers serial ports; it does not yet send commands to the boards. We will add a safe desktop-to-S3 serial protocol in a later milestone.

This is a desktop application running on Windows, not a bootable replacement operating system.
