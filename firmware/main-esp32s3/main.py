"""AMH-OS main-controller bring-up firmware for ESP32-S3 N16R8.

MicroPython target. UART1: GPIO17 TX -> WROOM GPIO16 RX;
GPIO18 RX <- WROOM GPIO17 TX. USB serial remains for REPL/logging.
"""
import time
import ujson
from machine import UART, Pin

UART_ID = 1
UART_BAUD = 115200
UART_TX = 17
UART_RX = 18
MAX_LINE = 512
REQUEST_TIMEOUT_MS = 1200

uart = UART(
    UART_ID,
    baudrate=UART_BAUD,
    bits=8,
    parity=None,
    stop=1,
    tx=Pin(UART_TX),
    rx=Pin(UART_RX),
    timeout=20,
)

rx_buffer = bytearray()
next_request_id = 1


def send_message(payload):
    try:
        uart.write(ujson.dumps(payload).encode("utf-8") + b"\n")
    except Exception as exc:
        print("UART TX error:", exc)


def read_message():
    global rx_buffer
    waiting = uart.any()
    if not waiting:
        return None

    chunk = uart.read(min(waiting, 128))
    if not chunk:
        return None

    for byte in chunk:
        if byte == 10:
            line = bytes(rx_buffer).strip()
            rx_buffer = bytearray()
            if not line:
                continue
            try:
                value = ujson.loads(line.decode("utf-8"))
                if isinstance(value, dict):
                    return value
            except Exception as exc:
                print("Ignored malformed UART frame:", exc)
        elif byte != 13:
            if len(rx_buffer) < MAX_LINE:
                rx_buffer.append(byte)
            else:
                print("UART frame too long; discarding")
                rx_buffer = bytearray()
    return None


def request(command):
    global next_request_id
    request_id = next_request_id
    next_request_id += 1
    send_message({"cmd": command, "id": request_id})

    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < REQUEST_TIMEOUT_MS:
        response = read_message()
        if response is not None and response.get("id") == request_id:
            return response
        time.sleep_ms(5)
    return None


print("AMH-OS main controller starting")
time.sleep_ms(300)

identity = request("identify")
if identity:
    print("Coprocessor:", identity)
else:
    print("Coprocessor not detected; check UART wiring and common GND")

while True:
    result = request("ping")
    if result:
        print("Coprocessor link: OK")
    else:
        print("Coprocessor link: TIMEOUT")
    time.sleep_ms(3000)
