// v4_smart_ai.ino

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

void showHappy() {
  display.clearDisplay();
  display.setCursor(20, 20);
  display.println(":)");
  display.display();
}

void showSad() {
  display.clearDisplay();
  display.setCursor(20, 20);
  display.println(":(");
  display.display();
}

void showNeutral() {
  display.clearDisplay();
  display.setCursor(20, 20);
  display.println(":|");
  display.display();
}

void setup() {
  Serial.begin(115200);

  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
}

void loop() {
  if (Serial.available()) {
    String emotion = Serial.readString();

    if (emotion == "happy") showHappy();
    if (emotion == "sad") showSad();
    if (emotion == "neutral") showNeutral();
  }
}