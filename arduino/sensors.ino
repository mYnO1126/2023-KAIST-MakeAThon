#include <DFRobot_DHT11.h>


DFRobot_DHT11 DHT;
#define DHT11_PIN 2
#define RELAY 8


void setup(){
  Serial.begin(115200);
  pinMode(RELAY, OUTPUT);
}

void loop(){
  DHT.read(DHT11_PIN);
  int light = analogRead(A0);
  int soil = analogRead(A1);

  digitalWrite(RELAY, HIGH);
  
  // temp humi light soil
  Serial.print(DHT.temperature);
  Serial.print("  ");
  Serial.print(DHT.humidity);
  Serial.print("  ");
  Serial.print(light);
  Serial.print("  ");
  Serial.println(soil);

  
  delay(1000);
;
}
