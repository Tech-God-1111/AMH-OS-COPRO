# AMH-OS Desktop v10.2

Connectivity and browser integration update for the AMH-OS Windows desktop-shell prototype. This is a Windows-hosted desktop environment, not a standalone bootable operating system.

## Desktop applications

- **Internet** — opens a web page in the PC's registered default browser using Windows URL handling.
- **Connectivity Hub** — opens native Windows Wi-Fi, Bluetooth and Network Status settings.
- **Workload Monitor** — processor and worker telemetry interface.
- **Task Scheduler** — task queue and priority planning interface.
- **Resource Manager** — processor capacity and resource admission interface.
- **Task Dispatcher** — job routing and dispatch interface.
- **Result Manager** — task output and verification interface.
- **Recovery Manager** — timeout, retry and worker recovery policy interfaces.
- Existing shell apps: File Explorer, Terminal, System Monitor, Notes, Calculator, Serial Monitor, Hardware Center, Appearance and Diagnostics.

## v10.2 connectivity features

- Added an Internet desktop icon and Start-menu entry. Clicking it opens https://www.google.com through Windows, which launches the system's default browser.
- Added Connectivity Hub with direct links to Windows Wi-Fi settings, Bluetooth settings and Network Status.
- Wi-Fi discovery, connection, adapter power and Bluetooth pairing remain managed by Windows and the installed device drivers. AMH-OS does not yet implement its own radio controls or device-pairing stack.

## v10.1 stability foundations

- Hardware Center uses bounded LF frame assembly, handling fragmented/coalesced serial reads, CRLF and oversized-frame recovery.
- Hardware Center tracks one outstanding request, matches response IDs, uses monotonic timeout measurement and closes serial ports cleanly.
- Serial Monitor polling is non-blocking and closes the port after read failures.
- PowerShell execution is asynchronous, asks for confirmation and clearly states that commands run with the Windows user's permissions.
- Calculator arithmetic is evaluated without eval() and limits expression size, exponent magnitude and numeric result size.
- Diagnostics renders each report field on its own line.
- Added hardware-independent task/result/retry contracts and tests, including protocol version 1, bounded task timeout and a conservative 256-byte Uno JSON payload budget.
- Extracted the six processing-suite windows into a separate apps module.
- Added packaging metadata, dependency bounds, .gitignore and GitHub Actions CI.

## Install and run (Windows 10/11)

Python 3.10 or newer is required.

```powershell
python -m pip install -r requirements.txt
python -u main.py
```

To install the test extra and run the hardware-independent tests:

```powershell
python -m pip install -e ".[test]"
python -m pytest -q
```

## Hardware and feature status

The six processing-suite applications remain interface-first. Their task contracts are software foundations only: they do not measure live hardware load, schedule or dispatch real work, or run firmware on the ESP32/Uno boards. The Arduino Uno workers still have no firmware or validated wiring/protocol.

The Hardware Center requires a compatible PC-to-ESP32-S3 USB JSON bridge. The existing S3 sketch still performs the S3-to-WROOM UART link check and does not yet implement the PC-facing USB bridge. Therefore desktop-to-board commands are not end-to-end ready until that bridge is implemented, flashed and physically tested.

Wi-Fi and Bluetooth are controlled through Windows Settings, using the PC's existing adapters and drivers. Availability depends on the hardware and drivers installed on the PC.
