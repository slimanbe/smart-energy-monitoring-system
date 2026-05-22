#include <WiFi.h>
#include <WebServer.h>
#include <WebSocketsServer.h>
#include <PZEM004Tv30.h>
#include <ArduinoJson.h>


const char* ssid = "realme C51";
const char* password = "40042020";


PZEM004Tv30 pzem(Serial2, 16, 17);

WebServer server(80);
WebSocketsServer webSocket = WebSocketsServer(81);


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
  webSocket.begin();
}

void loop() {
  server.handleClient();
  webSocket.loop();

  static unsigned long lastUpdate = 0;
  if (millis() - lastUpdate > 500) { 
    lastUpdate = millis();
    
    
    String dataPayload = getSensorData(); 
    webSocket.broadcastTXT(dataPayload);
    
    
    Serial.println(dataPayload);
  }
}