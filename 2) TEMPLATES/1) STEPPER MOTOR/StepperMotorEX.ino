#include <math.h>

const int stepPin = 5; 
const int dirPin = 4; 
const int potPin = 0;

int state = 0;

float position_current = 0;
float position_target = 0;
float velocity_current = 0;
float velocity_max = 100; // counts per second
float acceleration_max = 10; // counts per second squared

 
void setup() {
  pinMode(stepPin,OUTPUT); 
  pinMode(dirPin,OUTPUT);
  Serial.begin(9600);
  
}
void loop() {
  Serial.println(position_current);
  
  if (Serial.available()>0);
    position_target = Serial.parseFloat();
  
  switch(state){
    case 0: //Idle
      Serial.println("Target Reached.");
      if (position_current<position_target):
        state = 1;
   
    case 1: //Accelerating forward
        
    case 2: //Accelerating reverse

    case 3: //deaccelerating forward

    case 4: //deaccelerating reverse

    case 5: //Constant velocity != 0

  }
  delay(1000);
}

void steppp_baby(float vel, bool dir){
  digitalWrite(dirPin,dir);
  digitalWrite(stepPin,HIGH); 
  delayMicroseconds(500); 
  digitalWrite(stepPin,LOW); 
  delayMicroseconds(500);
  position_current = position_current + 1;
  delay(vel);
}
