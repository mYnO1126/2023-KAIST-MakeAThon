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
  int soil1 = analogRead(A1);
  int soil2 = analogRead(A2);


  digitalWrite(RELAY, HIGH);
  
  // temp humi light soil1 soil2
  Serial.print(DHT.temperature);
  Serial.print("  ");
  Serial.print(DHT.humidity);
  Serial.print("  ");
  Serial.print(light);
  Serial.print("  ");
  Serial.print(soil1);
  Serial.print("  ");
  Serial.println(soil2);

  
  delay(1000);
}
