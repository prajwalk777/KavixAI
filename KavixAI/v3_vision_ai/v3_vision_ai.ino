// v3_vision_ai.ino

void setup() {
  Serial.begin(115200);
}

void loop() {
  if (Serial.available()) {
    String object = Serial.readString();

    Serial.print("Detected: ");
    Serial.println(object);
  }
}