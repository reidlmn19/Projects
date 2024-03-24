#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>
#include <SPI.h>
#include <RF24.h>

#define LED_PIN     6
#define LED_COUNT   55
#define CE_PIN      9
#define CSN_PIN     10

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRBW + NEO_KHZ800);
RF24 radio(CE_PIN, CSN_PIN);

const byte address[6] = "00001";

void setup() { 
  Serial.begin(9600);
  
  strip.begin();
  strip.show();

  radio.begin();
  radio.openReadingPipe(0, address);
  radio.startListening();
}

void loop() {
  if (radio.available()){
    char text[48] = "";
    radio.read(text, sizeof(text));
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, text);
    int r = doc["red"];
    int g = doc["green"];
    int b = doc["blue"];
    Serial.println(text);
    write_color(r,g,b);
  }
  
}

void write_color(int r, int g, int b){
  for(int i=0; i<strip.numPixels(); i++) {
    strip.setPixelColor(i, r ,g ,b);
    strip.show();
  }
}
