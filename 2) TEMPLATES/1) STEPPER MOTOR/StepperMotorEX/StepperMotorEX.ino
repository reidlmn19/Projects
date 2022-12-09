/*Example sketch to control a stepper motor with A4988 stepper motor driver and Arduino without a library. More info: https://www.makerguides.com */

// Define stepper motor connections and steps per revolution:
#define dirPin 4
#define stepPin 5

void setup() {
  Serial.begin(9600);
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
}

void loop() {
  while (Serial.available() > 0) {

    int d = Serial.parseInt();
    int s = Serial.parseInt();
    if (s < 350){
      s = 350;
    }
    int n = Serial.parseInt();

    if (Serial.read() == '\n') {
      stepperControl(d, s, n);
    }
  }
}

void stepperControl(int dir, int rate, int num_steps){
  digitalWrite(dirPin, dir);

  for (int i = 0; i < num_steps; i++) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(rate);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(rate);
  }
}

