#include <Adafruit_NeoPixel.h>

int blue_primary = 0;
int blue_secondary = 0;
int blue_tertiary = 30;

int green_primary = 0;
int green_secondary = 255;
int green_tertiary = 100;

int len_LED_strip = 200;
int len_LED_segments = 20;

int pin_LED_data = 3;

int red_primary = 255;
int red_secondary = 0;
int red_tertiary = 255;

int g_state;
int pix = 25;

Adafruit_NeoPixel pixels(len_LED_strip, pin_LED_data, NEO_GRB + NEO_KHZ800);

void setup() {
  Serial.begin(9600);
  pixels.begin();
  pixels.clear();
}

void loop() {
//  switch (g_state){
//      Serial.println("Loop Start");
//    case 0:
//      pixels.setPixelColor(pix, pixels.Color(0, 0, 0));
//      pixels.show();
//      Serial.println("State 0");
//      g_state = 1;
//    case 1:
//      pixels.setPixelColor(pix, pixels.Color(red_primary, green_primary, blue_primary));
//      pixels.show();
//      Serial.println("State 1");
//      g_state = 2;
//    case 2:
//      pixels.setPixelColor(pix, pixels.Color(red_secondary, green_secondary, blue_secondary));
//      pixels.show();
//      Serial.println("State 2");
//      g_state = 3;
//    case 3:
//      pixels.setPixelColor(pix, pixels.Color(red_tertiary, green_tertiary, blue_tertiary));
//      pixels.show();
//      Serial.println("State 3");
//      g_state = 0;
//  Serial.println("Loop End");
//  delay(1000);
//  }
   setWholeStrip(red_tertiary, green_tertiary, blue_tertiary);
   pixels.show();
   delay(1000);
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

typedef struct {
    double r;       // a fraction between 0 and 1
    double g;       // a fraction between 0 and 1
    double b;       // a fraction between 0 and 1
} rgb;

typedef struct {
    double h;       // angle in degrees
    double s;       // a fraction between 0 and 1
    double v;       // a fraction between 0 and 1
} hsv;

static hsv   rgb2hsv(rgb in);
static rgb   hsv2rgb(hsv in);

hsv rgb2hsv(rgb in)
{
    hsv         out;
    double      min, max, delta;

    min = in.r < in.g ? in.r : in.g;
    min = min  < in.b ? min  : in.b;

    max = in.r > in.g ? in.r : in.g;
    max = max  > in.b ? max  : in.b;

    out.v = max;                                // v
    delta = max - min;
    if (delta < 0.00001)
    {
        out.s = 0;
        out.h = 0; // undefined, maybe nan?
        return out;
    }
    if( max > 0.0 ) { // NOTE: if Max is == 0, this divide would cause a crash
        out.s = (delta / max);                  // s
    } else {
        // if max is 0, then r = g = b = 0              
        // s = 0, h is undefined
        out.s = 0.0;
        out.h = NAN;                            // its now undefined
        return out;
    }
    if( in.r >= max )                           // > is bogus, just keeps compilor happy
        out.h = ( in.g - in.b ) / delta;        // between yellow & magenta
    else
    if( in.g >= max )
        out.h = 2.0 + ( in.b - in.r ) / delta;  // between cyan & yellow
    else
        out.h = 4.0 + ( in.r - in.g ) / delta;  // between magenta & cyan

    out.h *= 60.0;                              // degrees

    if( out.h < 0.0 )
        out.h += 360.0;

    return out;
}


rgb hsv2rgb(hsv in)
{
    double      hh, p, q, t, ff;
    long        i;
    rgb         out;

    if(in.s <= 0.0) {       // < is bogus, just shuts up warnings
        out.r = in.v;
        out.g = in.v;
        out.b = in.v;
        return out;
    }
    hh = in.h;
    if(hh >= 360.0) hh = 0.0;
    hh /= 60.0;
    i = (long)hh;
    ff = hh - i;
    p = in.v * (1.0 - in.s);
    q = in.v * (1.0 - (in.s * ff));
    t = in.v * (1.0 - (in.s * (1.0 - ff)));

    switch(i) {
    case 0:
        out.r = in.v;
        out.g = t;
        out.b = p;
        break;
    case 1:
        out.r = q;
        out.g = in.v;
        out.b = p;
        break;
    case 2:
        out.r = p;
        out.g = in.v;
        out.b = t;
        break;

    case 3:
        out.r = p;
        out.g = q;
        out.b = in.v;
        break;
    case 4:
        out.r = t;
        out.g = p;
        out.b = in.v;
        break;
    case 5:
    default:
        out.r = in.v;
        out.g = p;
        out.b = q;
        break;
    }
    return out;     
}
