#include <Adafruit_NeoPixel.h>

int blue_primary = 0;
int blue_secondary = 0;
int green_primary = 0;
int green_secondary = 255;
int len_LED_strip = 200;
int len_LED_segments = 20;
int pin_LED_data = 3;
int red_primary = 255;
int red_secondary = 0;

Adafruit_NeoPixel pixels(len_LED_strip, pin_LED_data, NEO_GRB + NEO_KHZ800);

void setup() {
  pixels.begin();
  pixels.clear();
}

void loop() {
  animateScrollingBars(20, 500);
}

void setWholeStrip(int r, int g, int b){
  for(int i=0; i<len_LED_strip; i++){
      pixels.setPixelColor(i, pixels.Color(r, g, b));
  }
}

void setZone(int r, int g, int b, int l, int u){
  for(int i=l; i<u; i++){
      pixels.setPixelColor(i, pixels.Color(r, g, b));
  }
}

void animateScrollingBars(int w, int s){
  for(int i=0; i<w; i++){
      setZone(red_primary, green_primary, blue_primary, i, i+w);
      setZone(red_secondary, green_secondary, blue_secondary, i+w, i+(2*w));
      pixels.show();
      delay(s);
  }
}

