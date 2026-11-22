"""AMH-OS coprocessor firmware for original ESP32-WROOM-32.

MicroPython target. UART2 uses GPIO16 (RX) and GPIO17 (TX).
Keep USB serial available for flashing/logging.
"""
import time
import ujson
from machine import UART, Pin

UART_ID = 2
UART_BAUD = 115200
UART_RX = 16
UART_TX = 17
MAX_LINE = 512

uart = UART(
    UART_ID,
    baudrate=UART_BAUD,
    bits=8,
    parity=None,
    stop=1,
    rx=Pin(UART_RX),
    tx=Pin(UART_TX),
    timeout=20,
)

rx_buffer = bytearray()


def send_message(payload):
    """Send one compact JSON object followed by a newline."""
    try:
        encoded = ujson.dumps(payload).encode("utf-8") + b"\n"
        uart.write(encoded)
    except Exception as exc:
        print("UART TX error:", exc)


def handle_message(message):
    command = message.get("cmd")
    request_id = message.get("id")

    if command == "ping":
        return {"ok": True, "id": request_id, "reply": "pong"}
    if command == "identify":
        return {
            "ok": True,
            "id": request_id,
            "board": "ESP32-WROOM-32",
            "role": "coprocessor",
            "firmware": "amh-copro-0.1.0",
        }
    if command == "status":
        return {
            "ok": True,
            "id": request_id,
            "board": "ESP32-WROOM-32",
            "role": "coprocessor",
            "uptime_ms": time.ticks_ms(),
            "free_heap": __import__("gc").mem_free(),
        }
    return {
        "ok": False,
        "id": request_id,
        "error": "unknown_command",
    }


def process_line(raw_line):
    if not raw_line:
        return
    try:
        message = ujson.loads(raw_line.decode("utf-8"))
        if not isinstance(message, dict):
            raise ValueError("JSON message must be an object")
        response = handle_message(message)
    except Exception as exc:
        response = {"ok": False, "error": "invalid_message", "detail": str(exc)}
    send_message(response)


print("AMH-OS coprocessor ready; UART2 at", UART_BAUD)


while True:
    waiting = uart.any()
    if waiting:
        chunk = uart.read(min(waiting, 128))
        if chunk:
            for byte in chunk:
                if byte == 10:  # newline framing
                    process_line(bytes(rx_buffer).strip())
                    rx_buffer = bytearray()
                elif byte != 13:
                    if len(rx_buffer) < MAX_LINE:
                        rx_buffer.append(byte)
                    else:
                        # Drop an oversized frame and resynchronise at newline.
                        rx_buffer = bytearray()
    time.sleep_ms(5)
