# AMH-OS UART schematic (logical)

```text
       ESP32-S3 N16R8                         ESP32-WROOM-32
     MAIN CONTROLLER                         COPROCESSOR
  +---------------------+                 +---------------------+
  |                     |                 |                     |
  | GPIO17 / UART1_TX ---+-----------------> GPIO16 / UART2_RX   |
  |                     |                 |                     |
  | GPIO18 / UART1_RX <--+-----------------+ GPIO17 / UART2_TX   |
  |                     |                 |                     |
  | GND ----------------+-----------------+ GND                 |
  |                     |                 |                     |
  | USB (power/logging) |                 | USB (power/logging) |
  +---------------------+                 +---------------------+
           |                                         |
       USB supply                               USB supply

          UART: 115200 baud, 8N1, 3.3 V logic
          Do not tie the 3V3 or 5V/VIN power rails together.
```

This is a logical connection diagram, not a board-layout schematic. Confirm the exact development-board pinouts before connecting.
