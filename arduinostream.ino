#include <WiFiNINA.h>
#include <PubSubClient.h>

// Replace with your network credentials
const char* ssid = "yourSSID";
const char* password = "yourPASSWORD";

// MQTT broker settings
const char* mqtt_server = "broker.hivemq.com"; // Replace with the address of your MQTT broker
const int mqtt_port = 1883; // Replace with your MQTT broker port

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

int sensorPin = A0;
int sensorValue = 0;

void setup() {
    Serial.begin(9600);
    Serial.println("Connecting to WiFi...");

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConnected to WiFi");

  // Print IP address
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    // Delay before attempting MQTT connection
    delay(1000);

    mqttClient.setServer(mqtt_server, mqtt_port);
    reconnect();
}

void loop() {
    if (!mqttClient.connected()) {
        reconnect();
    }
    mqttClient.loop();

    sensorValue = readAverage(sensorPin, 10);
    Serial.print("Sensor value: ");
    Serial.println(sensorValue);

    String payload = String(sensorValue);
    if (mqttClient.publish("toaster/current", payload.c_str())) {
        Serial.println("Publish successful");
    } else {
        Serial.println("Publish failed");
    }

    delay(1000);
}

int readAverage(int pin, int numberOfReadings) {
    long sum = 0;
    for (int i = 0; i < numberOfReadings; i++) {
        sum += analogRead(pin);
        delay(10);
    }
    return sum / numberOfReadings;
}

void reconnect() {
    while (!mqttClient.connected()) {
        Serial.println("Attempting MQTT connection...");
        if (mqttClient.connect("ArduinoClient")) {
            Serial.println("Connected to MQTT Broker!");
        } else {
            Serial.print("Failed to connect, state: ");
            Serial.println(mqttClient.state());
            delay(5000);
        }
    }
}
