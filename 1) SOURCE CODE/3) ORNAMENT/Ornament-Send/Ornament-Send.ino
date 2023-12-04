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

const uint32_t colors[] = {0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF000, 0x00FFFF, 0x0080FF, 0x7F00FF, 0xFF007F0};
volatile int color_select = 0;
const byte address[6] = "00001";

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

void loop(){
  for (int i=0; i<8; i++){
    radio.write(&colors[i], sizeof(colors[i]));
    delay(1000);
  }
}

//void loop() {
//  if (color_changed()){
//    write_color(colors[color_select]);
//  }
//  delay(200);
//}

bool color_changed(){
  int color_now = 8 * analogRead(POT_PIN)/1024;
  if (color_select != color_now){
    color_select = color_now;
    return 1;
  }
  return 0;
}

void write_color(int color){
  for(int i=0; i<strip.numPixels(); i++) {
    strip.setPixelColor(i, color);
    strip.show();
  }
}

void print_color(){
  Serial.println(colors[color_select]);
}

void send_color(){
  DynamicJsonDocument doc(1024);
  doc["color"] = colors[color_select];
  char nrf_buff[1024];
  serializeJson(doc, nrf_buff);
  radio.write(&nrf_buff, sizeof(nrf_buff));
}
