#include <Arduino.h>
#include <ArduinoJson.h>

static constexpr int COPRO_RX_PIN = 18;
static constexpr int COPRO_TX_PIN = 17;
static constexpr uint32_t UART_BAUD = 115200;
static constexpr size_t MAX_LINE = 512;
static constexpr uint32_t REQUEST_TIMEOUT_MS = 1200;
static constexpr uint32_t PING_INTERVAL_MS = 3000;

HardwareSerial CoproSerial(1);
String rxLine;
uint32_t nextRequestId = 1;
uint32_t lastPingAt = 0;

void sendJson(JsonDocument &doc) {
  serializeJson(doc, CoproSerial);
  CoproSerial.write('\n');
}

bool readResponse(JsonDocument &response, uint32_t timeoutMs) {
  const uint32_t started = millis();
  while (millis() - started < timeoutMs) {
    while (CoproSerial.available()) {
      char c = static_cast<char>(CoproSerial.read());
      if (c == '\r') continue;
      if (c == '\n') {
        if (rxLine.isEmpty()) continue;
        DeserializationError err = deserializeJson(response, rxLine);
        rxLine = "";
        if (!err) return true;
        Serial.printf("Ignored malformed UART JSON: %s\n", err.c_str());
      } else if (rxLine.length() < MAX_LINE) rxLine += c;
      else { rxLine = ""; Serial.println("UART frame too long; discarding"); }
    }
    delay(2);
  }
  return false;
}

bool requestCoprocessor(const char *command, JsonDocument &response) {
  uint32_t requestId = nextRequestId++;
  JsonDocument request;
  request["cmd"] = command;
  request["id"] = requestId;
  sendJson(request);
  uint32_t started = millis();
  while (millis() - started < REQUEST_TIMEOUT_MS) {
    JsonDocument candidate;
    if (readResponse(candidate, 20) && candidate["id"].is<uint32_t>() &&
        candidate["id"].as<uint32_t>() == requestId) {
      response.set(candidate);
      return true;
    }
  }
  return false;
}

void setup() {
  Serial.begin(115200);
  delay(500);
  CoproSerial.begin(UART_BAUD, SERIAL_8N1, COPRO_RX_PIN, COPRO_TX_PIN);
  Serial.println("\nAMH-OS main controller starting (ESP32-S3)");
  JsonDocument response;
  if (requestCoprocessor("identify", response)) {
    Serial.print("Coprocessor identity: ");
    serializeJson(response, Serial);
    Serial.println();
  } else Serial.println("Coprocessor not detected; check UART wiring and common GND.");
  lastPingAt = millis();
}

void loop() {
  if (millis() - lastPingAt >= PING_INTERVAL_MS) {
    lastPingAt = millis();
    JsonDocument response;
    if (requestCoprocessor("ping", response) &&
        response["reply"] == "pong" && response["ok"] == true)
      Serial.println("Coprocessor link: OK");
    else Serial.println("Coprocessor link: TIMEOUT / unexpected response");
  }
  delay(5);
}
