/*
 * Emulates a nRF8001 temperature beacon; 
 * reads temperature from a DHT11 and sends it via BTLE.
 * Compatible with Nordic Semiconductor apps such as
 * nRF Master Control Panel or nRF Temp 2.0.
 */

#include <BTLE.h>

#include <SPI.h>
#include <RF24.h>

RF24 radio(7,8);
BTLE btle(&radio);

void setup() {
  Serial.begin(57600);
  while (!Serial) { }
  Serial.println("BTLE temperature sender");
  Serial.end();

  // 8 chars max
  btle.begin("SimoTemp");
}

void loop() {
  nrf_service_data buf;
  buf.service_uuid = NRF_TEMPERATURE_SERVICE_UUID;
  buf.value = BTLE::to_nRF_Float(float(6969696));
  
  if(!btle.advertise(0x16, &buf, sizeof(buf))) {
    Serial.begin(57600);
    Serial.println("BTLE advertisement failure");
    Serial.end();
  }
  btle.hopChannel();
  
  delay(1000);

}
