# UART communication smoke test

## Before testing
- Confirm exact board variants and pinouts.
- Verify TX/RX are crossed and GND is common.
- Keep the boards independently USB-powered for initial testing.
- Confirm both firmware images use 115200 baud, 8N1.

## Expected result
1. Start the WROOM firmware first. Its USB console prints that the coprocessor is ready.
2. Start the S3 firmware.
3. S3 console prints a coprocessor identity response.
4. S3 prints `Coprocessor link: OK` approximately every three seconds.

## Failure checks
- No identify response: check common ground, crossed TX/RX and pin mapping.
- Garbled data: check baud rate and wiring quality.
- Intermittent response: shorten wires, verify stable USB supplies and confirm no GPIO conflicts.
- S3 REPL unavailable: use the board's USB programming/serial interface and confirm the correct MicroPython build.

This is a manual smoke test, not automated hardware validation. No physical boards are attached to this development environment.
