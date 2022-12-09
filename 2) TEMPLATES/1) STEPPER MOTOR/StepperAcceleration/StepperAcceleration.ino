/*Example sketch to control a stepper motor with A4988 stepper motor driver and Arduino without a library. More info: https://www.makerguides.com */

#define dirPin 4
#define stepPin 5
#define enaPin 6
#define min_rate 1000
#define max_rate 200
#define rate_interval 1

void setup() {
  Serial.begin(9600);
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  pinMode(enaPin, OUTPUT);
}

void loop() {
  while (Serial.available() > 0) {

    int d = Serial.parseInt();
    
    int s = Serial.parseInt();
    if (s < max_rate){
      s = max_rate;
    }
    int n = Serial.parseInt();

    if (Serial.read() == '\n') {
      stepperAdvControl(d, s, n);
    }
  }
}


void stepperAdvControl(int dir, int rate_target, int num_steps){
  digitalWrite(dirPin, dir);
  digitalWrite(enaPin, HIGH);
  delay(5);
  int rate_current = min_rate;
  
  for (int i = 0; i < num_steps; i++){
    if (rate_current > rate_target){
      rate_current = rate_current - rate_interval;
    }
    else {
      rate_current = rate_target;
    }
    
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(rate_current);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(rate_current);
  }
  delay(100);
  digitalWrite(enaPin, LOW);
}

