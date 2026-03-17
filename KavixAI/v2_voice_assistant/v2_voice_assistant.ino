// v2_voice_assistant.ino

#include <WiFi.h>

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASS";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting...");
  }

  Serial.println("Connected!");
}

void loop() {
  // Listen for serial commands
  if (Serial.available()) {
    String cmd = Serial.readString();

    if (cmd == "listen") {
      Serial.println("Listening mode...");
    }
    if (cmd == "speak") {
      Serial.println("Speaking mode...");
    }
  }
}