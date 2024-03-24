#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>
#include <SPI.h>
#include <RF24.h>
#include <string>

#define LED_PIN     6
#define POT_PIN     0
#define BUT_PIN     3
#define LED_COUNT   1
#define CE_PIN      9
#define CSN_PIN     8

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRBW + NEO_KHZ800);
RF24 radio(CE_PIN, CSN_PIN);

const int reds[] = {0,255, 0, 0, 255};
const int greens[] = {0,0, 255, 0, 255};
const int blues[] = {0,0, 0, 255, 255};

volatile int color_select = 0;
const byte address[6] = "00001";

const bool TEST_MODE = true;

void setup() {
  pinMode(BUT_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(BUT_PIN), send_color, FALLING);

  radio.begin();
  radio.openWritingPipe(address);
  radio.stopListening();
  
  Serial.begin(9600);
  
  strip.begin();
  strip.show();
}


void loop() {
  if (color_changed()){
    write_color(color_select);
  }
  if (TEST_MODE){
    char nrf_buff[] = "TESTING";
    radio.write(nrf_buff, sizeof(nrf_buff));
    Serial.println(nrf_buff);
  }
  delay(1000);
}

bool color_changed(){
  int color_now = 5 * analogRead(POT_PIN)/1024;
  if (color_select != color_now){
    color_select = color_now;
    return 1;
  }
  return 0;
}

void write_color(int s){
  for(int i=0; i<strip.numPixels(); i++) {
    strip.setPixelColor(i, reds[s], greens[s], blues[s]);
    strip.show();
  }
}

void print_color(){
  Serial.print(reds[color_select]);
  Serial.print(greens[color_select]);
  Serial.println(blues[color_select]);
}

void send_color(){
  DynamicJsonDocument doc(1024);
  doc["red"] = reds[color_select];
  doc["green"] = greens[color_select];
  doc["blue"] = blues[color_select];
  char nrf_buff[64] = "";
  serializeJson(doc, nrf_buff);
  radio.write(nrf_buff, sizeof(nrf_buff));
  Serial.println(nrf_buff);  
}
