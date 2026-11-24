# Changelog

## 10.1.0
- Replaced fragile Hardware Center receive parsing with bounded newline framing, response ID matching and monotonic timeout tracking.
- Made Serial Monitor polling non-blocking and close its port on read errors.
- Made PowerShell execution asynchronous and added per-command confirmation plus an explicit host-permissions warning.
- Added a bounded arithmetic evaluator to prevent oversized exponent calculations and complex expressions.
- Corrected Diagnostics report line breaks.
- Added reusable serial framing, versioned task/result contracts, bounded task timeouts, Uno payload budget and automated unit tests.
- Extracted the six processing-suite windows into an apps module; kept serial, calculator and task contracts in core.
- Added package metadata, dependency bounds, .gitignore and GitHub Actions CI.
- Kept all six processing-suite apps interface-first; hardware dispatch and telemetry remain intentionally unimplemented pending desktop validation.

## 10.0.0
- Created the AMH-OS Desktop v10.0 application directory.
- Added six interface-first processing suite applications: Workload Monitor, Task Scheduler, Resource Manager, Task Dispatcher, Result Manager and Recovery Manager.
- Added overview cards, processor/task tables and clear hardware-not-connected prototype states.
- Preserved the v8.0 desktop shell and existing applications.
- Hardware telemetry, autonomous scheduling, task dispatch, result verification and recovery are not implemented in this interface-only stage.
