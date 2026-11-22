# Hardware wiring — initial UART bring-up

## Boards
- Main: ESP32-S3 N16R8 development board.
- Coprocessor: original ESP32-WROOM-32 development board.
- Display: not selected / not connected.

## UART connection
| ESP32-S3 main | ESP32-WROOM-32 coprocessor |
|---|---|
| GPIO17 (UART1 TX) | GPIO16 (UART2 RX) |
| GPIO18 (UART1 RX) | GPIO17 (UART2 TX) |
| GND | GND |

UART signals are crossed: TX connects to the other board's RX.

## Power and safety
1. Initially power/program each development board from its own USB connection.
2. Connect the grounds so UART has a common reference.
3. Do **not** connect the boards' 3V3 rails or 5V/VIN rails together.
4. Both UART pins use 3.3 V logic. Do not apply 5 V to GPIO.
5. Disconnect power before changing wiring.

## Important board-revision check
GPIO availability varies by development-board design. Before wiring, verify the exact board pinout and ensure GPIO16/17 on the WROOM board and GPIO17/18 on the S3 board are exposed and not reserved by onboard peripherals, flash/PSRAM, USB, or other circuitry. In particular, some ESP32 module variants use GPIO16/17 internally; confirm the module is the original WROOM-32, not WROVER or another variant.

## Bring-up
1. Flash `firmware/coprocessor-esp32/main.py` to the WROOM board as `main.py`.
2. Flash `firmware/main-esp32s3/main.py` to the S3 board as `main.py`.
3. Open each USB serial console at 115200 baud.
4. Power both boards and observe the S3 identify response followed by periodic ping success.
5. If there is no response, re-check crossed TX/RX, common GND, pin mux conflicts and matching UART settings.
