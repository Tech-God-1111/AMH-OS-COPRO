# AMH-OS Desktop v10.1

Stability and architecture update for the AMH-OS Windows desktop-shell prototype. This is the maintained desktop development line; earlier version branches remain available as historical snapshots.

## Desktop applications

- **Workload Monitor** — processor and worker telemetry interface.
- **Task Scheduler** — task queue and priority planning interface.
- **Resource Manager** — processor capacity and resource admission interface.
- **Task Dispatcher** — job routing and dispatch interface.
- **Result Manager** — task output and verification interface.
- **Recovery Manager** — timeout, retry and worker recovery policy interface.
- Existing shell apps: File Explorer, Terminal, System Monitor, Notes, Calculator, Serial Monitor, Hardware Center, Appearance and Diagnostics.

## v10.1 fixes

- Hardware Center now uses a bounded LF frame assembler that handles fragmented and coalesced serial reads, CRLF, and oversized-frame recovery.
- Hardware Center tracks one outstanding request, matches response IDs, uses monotonic timeout measurement, and closes the serial port cleanly.
- Serial Monitor polling is non-blocking and closes the port after read failures.
- The PowerShell terminal runs asynchronously so long-running commands do not freeze the desktop; each command requires confirmation and the UI states that commands execute with the Windows user's permissions.
- Calculator arithmetic is evaluated without eval() and now limits expression size, exponent magnitude and numeric result size.
- Diagnostics renders each report field on its own line.
- Added hardware-independent task/result/retry data contracts and tests, including protocol version 1 and a bounded per-task timeout. Uno task payloads are limited to a conservative 256-byte JSON budget.
- Extracted the six processing-suite windows into a separate apps module and kept protocol, calculator and task contracts in core modules.
- Added packaging metadata, repository ignores and a GitHub Actions test workflow.

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

The six processing-suite applications remain interface-first. The new task contracts are software foundations only: they do not measure live hardware load, schedule or dispatch real work, or run firmware on the ESP32/Uno boards. The Arduino Uno workers still have no firmware or validated wiring/protocol.

The Hardware Center requires a compatible PC-to-ESP32-S3 USB JSON bridge. The existing S3 firmware in this repository still performs its S3-to-WROOM UART link check and does not yet implement the PC-facing USB bridge. Therefore, desktop-to-board Hardware Center commands are not end-to-end functional until that bridge is implemented, flashed and physically tested. The v10.1 desktop parser fix does not claim otherwise.

This remains a Windows-hosted desktop application, not a standalone bootable operating system. Appearance and Quick Settings remain previews and do not change Windows settings.
