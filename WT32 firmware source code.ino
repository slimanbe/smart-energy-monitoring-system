#include <WiFi.h>
#include <WebServer.h>
#include <WebSocketsServer.h>
#include <PZEM004Tv30.h>
#include <ArduinoJson.h>

// WiFi Configuration
const char* ssid = "realme C51";
const char* password = "40042020";

// PZEM-004T Connection: RX=16 (Connect to TX of PZEM), TX=17 (Connect to RX of PZEM)
PZEM004Tv30 pzem(Serial2, 5, 17);

WebServer server(80);
WebSocketsServer webSocket = WebSocketsServer(81);

// This function creates the JSON string
String getSensorData() {
  StaticJsonDocument<200> doc;
  float v = pzem.voltage();
  float c = pzem.current();
  float p = pzem.power();
  float e = pzem.energy();
  float f = pzem.frequency();
  float pf = pzem.pf();

  // Handle cases where the PZEM is not connected to AC power
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
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { 
    delay(500); 
    Serial.print("."); 
  }
  
  Serial.println("\nConnected! IP Address: " + WiFi.localIP().toString());

  // API for the Python "requests" method
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
  if (millis() - lastUpdate > 1000) { // Send data every 1 second
    lastUpdate = millis();
    
    // FIX: Store the string in a variable first to satisfy the library requirement
    String dataPayload = getSensorData(); 
    webSocket.broadcastTXT(dataPayload);
    
    // Optional: Print to serial so you can see it working
    Serial.println(dataPayload);
  }
}