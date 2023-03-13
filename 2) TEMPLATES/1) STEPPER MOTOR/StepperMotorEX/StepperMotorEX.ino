#include <math.h>

const int PIN_ENABLE = 6; 
const int PIN_DIRECTION = 4; 
const int PIN_STEP = 5;

int state = 0;

int SPEED = 500; // ms per step
char msg[] = "0100FF";

 
void setup() {
  pinMode(PIN_ENABLE,OUTPUT); 
  pinMode(PIN_DIRECTION,OUTPUT);
  pinMode(PIN_STEP,OUTPUT); 
  Serial.begin(9600);
  Serial.println("Begin");
  MOVE(500, true);
}
void loop() {

}



void MOVE(int steps, bool dir){
  digitalWrite(PIN_ENABLE, HIGH);
  for (int i = 0; i < steps; i++){
    digitalWrite(PIN_DIRECTION,dir);
    digitalWrite(PIN_STEP,HIGH); 
    delayMicroseconds(SPEED); 
    digitalWrite(PIN_STEP,LOW); 
    delayMicroseconds(SPEED);
  }
  digitalWrite(PIN_ENABLE, LOW);
}
