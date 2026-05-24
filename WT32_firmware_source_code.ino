#include <WiFi.h>
#include <HTTPClient.h>
#include <PZEM004Tv30.h>
#include <ArduinoJson.h>


const char* ssid = "realme C51";
const char* password = "40042026";


const char* serverUrl = "http://10.100.162.120:5000/data";  

const String deviceID = "node01";   

PZEM004Tv30 pzem(Serial2, 16, 17);  



void setup() {
  Serial.begin(9600);
  
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected! IP Address: " + WiFi.localIP().toString());
}

void loop() {
  static unsigned long lastSend = 0;

  if (millis() - lastSend > 2000) {        
    lastSend = millis();

    // Read data from PZEM
    float v = pzem.voltage();
    float c = pzem.current();
    float p = pzem.power();
    float e = pzem.energy();
    float f = pzem.frequency();
    float pf = pzem.pf();

    
    if (isnan(v) || isnan(c) || isnan(p)) {
      Serial.println("Error reading from PZEM - Skipping this reading");
      return;  
    }

    // Create JSON payload
    StaticJsonDocument<300> doc;
    doc["device_id"] = deviceID;
    doc["voltage"] = v;
    doc["current"] = c;
    doc["power"] = p;
    doc["energy"] = e;
    doc["frequency"] = f;
    doc["pf"] = pf;
    doc["timestamp"] = millis();

    String jsonPayload;
    serializeJson(doc, jsonPayload);

    // Send via HTTP POST
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(serverUrl);
      http.addHeader("Content-Type", "application/json");

      int httpResponseCode = http.POST(jsonPayload);

      if (httpResponseCode > 0) {
        Serial.printf("Data sent successfully! Response: %d\n", httpResponseCode);
      } else {
        Serial.printf("Failed to send data. Error: %s\n", http.errorToString(httpResponseCode).c_str());
      }
      
      http.end();
    } else {
      Serial.println("WiFi disconnected. Reconnecting...");
      WiFi.reconnect();
    }

    
    Serial.println("\n--- PZEM-004T Measurement Sent ---");
    Serial.print("Voltage: "); Serial.print(v); Serial.println(" V");
    Serial.print("Current: "); Serial.print(c); Serial.println(" A");
    Serial.print("Power: "); Serial.print(p); Serial.println(" W");
    Serial.print("Energy: "); Serial.print(e); Serial.println(" kWh");
    Serial.println("--------------------------------");
  }

  delay(10);
}
