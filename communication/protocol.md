# AMH-OS inter-processor protocol (v0.1)

## Transport
- Physical link: 3.3 V UART, 8 data bits, no parity, 1 stop bit (8N1).
- Default baud rate: 115200.
- Framing: one UTF-8 JSON object per line, terminated by LF (0x0A).
- CR (0x0D) is ignored.
- Maximum accepted frame: 512 bytes.
- No shared memory: the S3 and WROOM are independent microcontrollers.

## Request format
```json
{"cmd":"ping","id":1}
```

Every request should include an integer `id`. The receiver echoes it in its response.

## Supported commands
| Command | Purpose |
|---|---|
| `ping` | Link check; returns `reply: "pong"` |
| `identify` | Returns board identity, role and firmware version |
| `status` | Returns uptime and free heap where supported |

Unknown commands return `ok: false` and `error: "unknown_command"`.

## Response examples
```json
{"ok":true,"id":1,"reply":"pong"}
{"ok":true,"id":2,"board":"ESP32-WROOM-32","role":"coprocessor","firmware":"amh-copro-0.1.0"}
```

## Reliability notes
- Requests use monotonically increasing IDs on the main controller.
- Main-controller timeout: 1200 ms.
- A timeout is not proof of hardware failure; check baud rate, crossed TX/RX, common ground, power and pin availability.
- Future protocol revisions should add explicit version negotiation, checksum/CRC, retry policy and command authorization before controlling actuators.
