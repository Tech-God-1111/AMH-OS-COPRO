#include <Arduino.h>
#include <ArduinoJson.h>

static constexpr int LINK_RX_PIN = 16;
static constexpr int LINK_TX_PIN = 17;
static constexpr uint32_t UART_BAUD = 115200;
static constexpr size_t MAX_LINE = 512;

HardwareSerial LinkSerial(2);
String rxLine;

void sendResponse(JsonDocument &response) {
  serializeJson(response, LinkSerial);
  LinkSerial.write('\n');
}

void handleLine(const String &line) {
  JsonDocument request;
  DeserializationError err = deserializeJson(request, line);
  JsonDocument response;
  if (err || !request.is<JsonObject>()) {
    response["ok"] = false;
    response["error"] = "invalid_message";
    sendResponse(response);
    return;
  }
  if (request["id"].is<uint32_t>()) response["id"] = request["id"].as<uint32_t>();
  const char *command = request["cmd"] | "";
  if (strcmp(command, "ping") == 0) {
    response["ok"] = true;
    response["reply"] = "pong";
  } else if (strcmp(command, "identify") == 0) {
    response["ok"] = true;
    response["board"] = "ESP32-WROOM-32";
    response["role"] = "coprocessor";
    response["firmware"] = "amh-copro-0.1.0";
  } else if (strcmp(command, "status") == 0) {
    response["ok"] = true;
    response["board"] = "ESP32-WROOM-32";
    response["role"] = "coprocessor";
    response["uptime_ms"] = millis();
    response["free_heap"] = ESP.getFreeHeap();
  } else {
    response["ok"] = false;
    response["error"] = "unknown_command";
  }
  sendResponse(response);
}

void setup() {
  Serial.begin(115200);
  delay(300);
  LinkSerial.begin(UART_BAUD, SERIAL_8N1, LINK_RX_PIN, LINK_TX_PIN);
  Serial.println("\nAMH-OS coprocessor ready (ESP32-WROOM-32, UART2)");
}

void loop() {
  while (LinkSerial.available()) {
    char c = static_cast<char>(LinkSerial.read());
    if (c == '\r') continue;
    if (c == '\n') {
      if (!rxLine.isEmpty()) handleLine(rxLine);
      rxLine = "";
    } else if (rxLine.length() < MAX_LINE) rxLine += c;
    else { rxLine = ""; Serial.println("Oversized UART frame discarded"); }
  }
  delay(2);
}
