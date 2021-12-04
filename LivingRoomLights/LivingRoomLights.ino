#include <Adafruit_NeoPixel.h>

int blue_primary = 0;
int blue_secondary = 0;
int blue_tertiary = 0;
int green_primary = 0;
int green_secondary = 255;
int green_tertiary = 18;
int len_LED_strip = 200;
int len_LED_segments = 20;
int pin_LED_data = 3;
int red_primary = 255;
int red_secondary = 0;
int red_tertiary = 190;
int state = 0;

Adafruit_NeoPixel pixels(len_LED_strip, pin_LED_data, NEO_GRB + NEO_KHZ800);

void setup() {
  pixels.begin();
  pixels.clear();
  Serial.begin(9600);  
}

void loop() {
   outsideOnly(50);
//   middleOnly(100);
    pixels.show();
  
//  if (Serial.available() > 0) {
//    state = Serial.parseInt();
//    Serial.println(state);
//  }
//  if (state==0){
//    setWholeStrip(0, 0, 0);
//    pixels.show();
//  }
//  else if (state==1){
//    animateScrollingBars(20, 50);
//  }
//  else if (state==2){
//    setWholeStrip(red_tertiary, green_tertiary, blue_tertiary);
//    pixels.show();
//  }
//  else if (state==3){
//    setWholeStrip(200, 200, 200);
//    pixels.show();
//  }
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
  for(int i=0; i<2*w; i++){
    setZone(red_primary, green_primary, blue_primary, i-2*w, i-w);\
    setZone(red_secondary, green_secondary, blue_secondary, i-w, i);
    
    setZone(red_primary, green_primary, blue_primary, i, i+w);
    setZone(red_secondary, green_secondary, blue_secondary, i+w, i+2*w);

    setZone(red_primary, green_primary, blue_primary, i+2*w, i+3*w);
    setZone(red_secondary, green_secondary, blue_secondary, i+3*w, i+4*w);

    setZone(red_primary, green_primary, blue_primary, i+4*w, i+5*w);
    setZone(red_secondary, green_secondary, blue_secondary, i+5*w, i+6*w);

    setZone(red_primary, green_primary, blue_primary, i+6*w, i+7*w);
    setZone(red_secondary, green_secondary, blue_secondary, i+7*w, i+8*w);

    setZone(red_primary, green_primary, blue_primary, i+8*w, i+9*w);
    setZone(red_secondary, green_secondary, blue_secondary, i+9*w, len_LED_strip);
    
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
    else if (mod==1){
      pixels.setPixelColor(i, pixels.Color(red_secondary, green_secondary, blue_secondary));
    }
    else if (mod==2){
      pixels.setPixelColor(i, pixels.Color(red_tertiary, green_tertiary, blue_tertiary));
    }
  }
}

void middleOnly(int w){
  int lower_lim = (len_LED_strip-w)/2;
  int upper_lim = lower_lim + w;
  setZone(0, 0, 0, 0, lower_lim);
  setZone(red_tertiary, green_tertiary, blue_tertiary, lower_lim, upper_lim);
  setZone(0, 0, 0, upper_lim, len_LED_strip);
}

void outsideOnly(int w){
  int lower_lim = w;
  int upper_lim = len_LED_strip-w;
  setZone(red_tertiary, green_tertiary, blue_tertiary, 0, lower_lim);
  setZone(0, 0, 0, lower_lim, upper_lim);
  setZone(red_tertiary, green_tertiary, blue_tertiary, upper_lim, len_LED_strip);
}

