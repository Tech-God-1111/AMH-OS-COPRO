# AMH-OS Desktop v10.0

Interface-first development release for the AMH-OS autonomous processing suite.

## New applications
- **Workload Monitor** — processor and worker telemetry dashboard.
- **Task Scheduler** — task queue and priority planning interface.
- **Resource Manager** — processor capacity and resource admission dashboard.
- **Task Dispatcher** — job routing and dispatch console.
- **Result Manager** — task output and verification dashboard.
- **Recovery Manager** — timeout, retry and worker recovery policy dashboard.

## Existing desktop features
- Windows-hosted desktop shell, Start menu, desktop shortcuts and taskbar.
- File Explorer, PowerShell terminal, System Monitor, Notes and Calculator.
- USB Serial Monitor, Hardware Center, Appearance and Diagnostics.

## Install and run
Requires Windows 10/11 and Python 3.10+.

```powershell
python -m pip install -r requirements.txt
python -u main.py
```

## v10.0 development status
The six processing-suite applications are currently interface prototypes. They display planned processor and task information but do not yet communicate with the ESP32 or Arduino boards, dispatch hardware jobs, measure their workload, or perform recovery actions. Those functions will be implemented after the desktop interfaces are tested.

This remains a Windows-hosted desktop application, not a standalone bootable operating system.
