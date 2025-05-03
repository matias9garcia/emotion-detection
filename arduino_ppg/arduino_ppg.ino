#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
const char* ssid = "Galaxy A54 5G 3857";
const char* password = "cwvfhxtg75bv5hr";
const char* serverUrl = "http://192.168.78.114:5100/data";
const int sensorPin = A0; // Pin analógico donde está conectado el sensor

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Conectando a WiFi...");
  }
  Serial.println("Conectado a la red WiFi");
}
void loop() {
  int sensorValue = analogRead(sensorPin);
  sendData(sensorValue);

  delay(10); // Pequeña demora para no saturar el servidor
}
void sendData(int value) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    WiFiClient client;
    http.begin(client,serverUrl + String("?value=") + String(value));
    int httpCode = http.GET();
    if (httpCode > 0) {
      Serial.printf("Enviado: %s\n", http.getString().c_str());
    } else {
      Serial.printf("Error al enviar: %s\n", http.errorToString(httpCode).c_str());
    }
    http.end();
  }
}