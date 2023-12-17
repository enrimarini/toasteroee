#include <WiFiNINA.h>
#include <PubSubClient.h>

// Replace with your network credentials
const char* ssid = "yourSSID";
const char* password = "yourPASSWORD";

// MQTT Broker settings
const char* mqtt_server = "broker.hivemq.com";
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

// Constants for analog reading
const int maxADCReading = 1023;
const int maxCurrent = 12.5;  // Assumed maximum current in amperes

void setup() {
  Serial.begin(115200);

  // Connect to WiFi
  connectToWiFi();

  // Setup MQTT connection
  mqttClient.setServer(mqtt_server, 1883);
  connectToMQTT();
}

void loop() {
  // Maintain WiFi and MQTT connections
  checkWiFiConnection();
  if (!mqttClient.connected()) {
    connectToMQTT();
  }
  mqttClient.loop();

  // Read and process the analog input
  readAnalogInput();

  // Additional delay to control loop execution frequency
  delay(1000);
}

void connectToWiFi() {
  Serial.print("Connecting to ");
  Serial.print(ssid);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nConnected to WiFi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void checkWiFiConnection() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi connection lost. Reconnecting...");
    connectToWiFi();
  }
}

void connectToMQTT() {
  while (!mqttClient.connected()) {
    Serial.println("Connecting to MQTT...");
    if (mqttClient.connect("arduinoClient")) {
      Serial.println("Connected to MQTT");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

const char* mqtt_topic = "home/arduino/current"; // MQTT topic

void readAnalogInput() {
  // Read the analog value
  int adcValue = analogRead(A0);

  // Convert the ADC reading to current
  float current = (float)adcValue / maxADCReading * maxCurrent;

  // Print the calculated current to the serial monitor
  Serial.print("Current: ");
  Serial.print(current);
  Serial.println(" A");

  // For troubleshooting, publish the current reading as a plain number
  char currentStr[16];
  dtostrf(current, 6, 2, currentStr); // Convert float to string

  // Publish the current reading to the MQTT topic
  if (!mqttClient.publish(mqtt_topic, currentStr)) {
    Serial.println("Publish failed");
  } else {
    Serial.println("Publish succeeded");
  }
}
