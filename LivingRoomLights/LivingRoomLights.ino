#include <Adafruit_NeoPixel.h>

int blue_primary = 0;
int blue_secondary = 0;
int blue_tertiary = 255;
int green_primary = 0;
int green_secondary = 255;
int green_tertiary = 0;
int len_LED_strip = 200;
int len_LED_segments = 20;
int pin_LED_data = 3;
int red_primary = 255;
int red_secondary = 0;
int red_tertiary = 0;

Adafruit_NeoPixel pixels(len_LED_strip, pin_LED_data, NEO_GRB + NEO_KHZ800);

void setup() {
  pixels.begin();
  pixels.clear();
}

void loop() {
  for (int i; i<5; i++){
    animateScrollingBars(20, 500);
  }
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
  int num_segments = len_LED_strip/(2*w);
  for(int i=0; i<w; i++){
    for(int j=0; j<=num_segments; j++){
      setZone(red_primary, green_primary, blue_primary, i+(j*w), i+((j+1)*w));
      setZone(red_secondary, green_secondary, blue_secondary, i+((j+1)*w), i+((j+2)*w));
    }
    pixels.show();
    delay(s);
  }
}

void animateTwinkle(int s, int n, int p){
  for(int i=0; i<len_LED_strip; i++){
    int mod = (i+p)%n;
    if (mod==0){
      pixels.setPixelColor(i, pixels.Color(red_primary, green_primary, blue_primary));
    }
    else if (mod==0){
      pixels.setPixelColor(i, pixels.Color(red_secondary, green_secondary, blue_secondary));
    }
    else if (mod==0){
      pixels.setPixelColor(i, pixels.Color(red_tertiary, green_tertiary, blue_tertiary));
    }
  }
}

