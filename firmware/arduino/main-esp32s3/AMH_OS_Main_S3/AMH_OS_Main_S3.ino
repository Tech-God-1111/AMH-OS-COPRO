#include <Arduino.h>
#include <ArduinoJson.h>
#include <WiFi.h>

// Create amh_wifi_secrets.h beside this sketch using the example file.
// The real credentials file is ignored by Git and must never be committed.
#if __has_include("amh_wifi_secrets.h")
  #include "amh_wifi_secrets.h"
#else
  #define AMH_WIFI_SSID ""
  #define AMH_WIFI_PASSWORD ""
#endif

static constexpr int COPRO_RX_PIN = 18;
static constexpr int COPRO_TX_PIN = 17;
static constexpr uint32_t UART_BAUD = 115200;
static constexpr size_t MAX_LINE = 512;
static constexpr uint32_t REQUEST_TIMEOUT_MS = 1200;
static constexpr uint32_t PING_INTERVAL_MS = 3000;
static constexpr uint32_t WIFI_RETRY_INTERVAL_MS = 15000;

HardwareSerial CoproSerial(1);
String rxLine;
uint32_t nextRequestId = 1;
uint32_t lastPingAt = 0;
uint32_t lastWifiRetryAt = 0;
bool lastWifiConnected = false;

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

void startWifi() {
  if (strlen(AMH_WIFI_SSID) == 0) {
    Serial.println("Wi-Fi not configured: create amh_wifi_secrets.h from the example file.");
    return;
  }

  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(AMH_WIFI_SSID, AMH_WIFI_PASSWORD);
  lastWifiRetryAt = millis();
  Serial.printf("Connecting to Wi-Fi SSID: %s\n", AMH_WIFI_SSID);
}

void serviceWifi() {
  const bool connected = WiFi.status() == WL_CONNECTED;
  if (connected != lastWifiConnected) {
    lastWifiConnected = connected;
    if (connected) {
      Serial.printf("Wi-Fi connected; IP: %s; RSSI: %d dBm\n",
                    WiFi.localIP().toString().c_str(), WiFi.RSSI());
    } else {
      Serial.println("Wi-Fi disconnected.");
    }
  }

  if (!connected && strlen(AMH_WIFI_SSID) > 0 &&
      millis() - lastWifiRetryAt >= WIFI_RETRY_INTERVAL_MS) {
    lastWifiRetryAt = millis();
    Serial.println("Retrying Wi-Fi connection...");
    WiFi.reconnect();
  }
}

void setup() {
  Serial.begin(115200);
  delay(500);
  CoproSerial.begin(UART_BAUD, SERIAL_8N1, COPRO_RX_PIN, COPRO_TX_PIN);
  Serial.println("\nAMH-OS main controller starting (ESP32-S3)");
  startWifi();

  JsonDocument response;
  if (requestCoprocessor("identify", response)) {
    Serial.print("Coprocessor identity: ");
    serializeJson(response, Serial);
    Serial.println();
  } else Serial.println("Coprocessor not detected; check UART wiring and common GND.");
  lastPingAt = millis();
}

void loop() {
  serviceWifi();

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
