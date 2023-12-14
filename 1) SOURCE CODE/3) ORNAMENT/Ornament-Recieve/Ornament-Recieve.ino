#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>
#include <SPI.h>
#include <RF24.h>

#define LED_PIN     6
#define LED_COUNT   1
#define CE_PIN      9
#define CSN_PIN     8

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRBW + NEO_KHZ800);
RF24 radio(CE_PIN, CSN_PIN);

const byte address[6] = "00001";

void setup() {
  radio.begin();
  radio.openReadingPipe(0, address);
  radio.startListening();
  
  Serial.begin(9600);
  
  strip.begin();
  strip.show();
}

void loop() {
  if (radio.available()){
    char text[48] = {0};
    radio.read(text, sizeof(text));
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, text);
    long color = doc["color"];
    write_color(color);
  }
}

void write_color(int color){
  for(int i=0; i<strip.numPixels(); i++) {
    strip.setPixelColor(i, color);
    strip.show();
  }
}
