#include <WiFi.h>
#include <WebServer.h>
#include <PZEM004Tv30.h>
#include <ArduinoJson.h>


const char* ssid = "realme C51";
const char* password = "40042026";


PZEM004Tv30 pzem(Serial2, 16, 17); 

WebServer server(80);

String getSensorData() {
  StaticJsonDocument<200> doc;
  
  float v = pzem.voltage();
  float c = pzem.current();
  float p = pzem.power();
  float e = pzem.energy();
  float f = pzem.frequency();
  float pf = pzem.pf();

  doc["voltage"] = isnan(v) ? 0 : v;
  doc["current"] = isnan(c) ? 0 : c;
  doc["power"] = isnan(p) ? 0 : p;
  doc["energy"] = isnan(e) ? 0 : e;
  doc["frequency"] = isnan(f) ? 0 : f;
  doc["pf"] = isnan(pf) ? 0 : pf;

  String json;
  serializeJson(doc, json);
  return json;
}

void setup() {
  
  Serial.begin(9600);
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { 
    delay(500); 
    Serial.print("."); 
  }
  
  Serial.println("\nConnected! IP Address: " + WiFi.localIP().toString());

  server.on("/data", []() {
    server.send(200, "application/json", getSensorData());
  });

  server.begin();
}

void loop() {
  server.handleClient();

  static unsigned long lastPrint = 0;
  if (millis() - lastPrint > 2000) {
    lastPrint = millis();

    float v = pzem.voltage();
    float c = pzem.current();
    float p = pzem.power();
    float e = pzem.energy();
    float f = pzem.frequency();
    float pf = pzem.pf();

    Serial.println("\n--- PZEM-004T Measurements ---");
    if (isnan(v)) {
      Serial.println("Error reading from PZEM module!");
    } else {
      Serial.print("Voltage: "); Serial.print(v); Serial.println(" V");
      Serial.print("Current: "); Serial.print(c); Serial.println(" A");
      Serial.print("Power:   "); Serial.print(p); Serial.println(" W");
      Serial.print("Energy:  "); Serial.print(e); Serial.println(" kWh");
      Serial.print("Freq:    "); Serial.print(f); Serial.println(" Hz");
      Serial.print("PF:      "); Serial.println(pf);
    }
    Serial.println("--------------------------------");
  }
  
  delay(10); 
}