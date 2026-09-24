int leds[] = {3, 5, 6, 10, 11};

int brightness = 255;
int currentLEDs = 0;

void setup() {
  Serial.begin(9600);

  for (int i = 0; i < 5; i++) {
    pinMode(leds[i], OUTPUT);
    analogWrite(leds[i], 0);
  }
}

void setLEDs(int number) {
  currentLEDs = number;

  for (int i = 0; i < 5; i++) {
    if (i < number) {
      analogWrite(leds[i], brightness);
    } else {
      analogWrite(leds[i], 0);
    }
  }
}

void setBrightness(int value) {
  brightness = constrain(value, 0, 255);

  // Apply new brightness to currently ON LEDs
  setLEDs(currentLEDs);
}

void loop() {

  if (Serial.available() > 0) {

    String command = Serial.readStringUntil('\n');
    command.trim();

    // LED count command
    // L0, L1, L2, L3, L4, L5
    if (command.startsWith("L")) {

      int number = command.substring(1).toInt();

      if (number >= 0 && number <= 5) {
        setLEDs(number);
      }
    }

    // Brightness command
    // B0 to B255
    else if (command.startsWith("B")) {

      int value = command.substring(1).toInt();

      if (value >= 0 && value <= 255) {
        setBrightness(value);
      }
    }
  }
}