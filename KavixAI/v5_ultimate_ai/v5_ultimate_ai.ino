// v5_ultimate_ai.ino

#include <WiFi.h>
#include <WebServer.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASS";

WebServer server(80);

Adafruit_SSD1306 display(128, 64, &Wire, -1);

void showFace(String emotion) {
  display.clearDisplay();
  display.setTextSize(2);
  display.setCursor(20, 20);

  if (emotion == "happy") display.println(":)");
  else if (emotion == "sad") display.println(":(");
  else display.println(":|");

  display.display();
}

void handleEmotion() {
  String emotion = server.arg("e");
  showFace(emotion);
  server.send(200, "text/plain", "OK");
}

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(500);

  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);

  server.on("/emotion", handleEmotion);
  server.begin();
}

void loop() {
  server.handleClient();
}