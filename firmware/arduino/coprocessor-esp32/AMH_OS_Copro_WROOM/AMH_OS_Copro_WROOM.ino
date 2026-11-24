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

static constexpr int LINK_RX_PIN = 16;
static constexpr int LINK_TX_PIN = 17;
static constexpr uint32_t UART_BAUD = 115200;
static constexpr size_t MAX_LINE = 512;
static constexpr uint32_t WIFI_RETRY_INTERVAL_MS = 15000;

HardwareSerial LinkSerial(2);
String rxLine;
uint32_t lastWifiRetryAt = 0;
bool lastWifiConnected = false;

void sendResponse(JsonDocument &response) {
  serializeJson(response, LinkSerial);
  LinkSerial.write('\n');
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
    response["firmware"] = "amh-copro-0.2.0";
  } else if (strcmp(command, "status") == 0) {
    response["ok"] = true;
    response["board"] = "ESP32-WROOM-32";
    response["role"] = "coprocessor";
    response["uptime_ms"] = millis();
    response["free_heap"] = ESP.getFreeHeap();
    response["wifi_connected"] = WiFi.status() == WL_CONNECTED;
    response["wifi_ssid"] = WiFi.status() == WL_CONNECTED ? WiFi.SSID() : "";
    response["wifi_ip"] = WiFi.status() == WL_CONNECTED ? WiFi.localIP().toString() : "";
    response["wifi_rssi"] = WiFi.status() == WL_CONNECTED ? WiFi.RSSI() : 0;
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
  startWifi();
}

void loop() {
  serviceWifi();

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
