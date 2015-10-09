#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

const char* ssid = "test";
const char* password = "";

IPAddress mqttServer(192, 168, 2, 1);
int       mqttPort = 1883;

WiFiClient wClient;
PubSubClient mqttClient(wClient);

#define SEALEVELPRESSURE_HPA (1013.25)

Adafruit_BME280 bme; // I2C, assumes SDA connected to GPIO4 (D2), SCL to GPIO5 (D1)
bool bmeOK = false;

unsigned long lastPubTime = 0;
const unsigned long pubInterval = 5L * 1000l;
char pubMsgBuf[100]; 

void setup() {

  // Set up the serial port
  Serial.begin(115200);
  Serial.println(F("BME280 Sensor MQTT client starting up..."));
  
  delay(10);

  // Initialize the BUILTIN_LED pin as an output
  pinMode(BUILTIN_LED, OUTPUT);  
     
  // Initialise the BME280 sensor and set flag accordingly
  if (bme.begin()) {
    bmeOK = true;
    Serial.println("Valid BME280 sensor detected");
  } 
  else
  {
    Serial.println("Could not detect a valid BME280 sensor, check I2C configuration!");
    bmeOK = false;
  }
  
  // Configure the MQTT client
  mqttClient.setServer(mqttServer, mqttPort);
  mqttClient.setCallback(mqttCallback);

  // Start ESP8266 WiFi in station mode, join the network
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid);

  // Wait for WiFI to connect then print status info
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi connected: ");
  printWifiStatus();
 
}

void loop()
{
  if (!mqttClient.connected()) {
    mqttReconnect();
  }
  mqttClient.loop();

  unsigned long now = millis();
  if (now - lastPubTime > pubInterval) {
    mqttPublishBmeData();
    lastPubTime = now;
  }
}

void printWifiStatus() {

  // print the SSID of the network 
  Serial.print("SSID: ");
  Serial.print(WiFi.SSID());

  // print your IP info
  Serial.print(" ip: ");
  Serial.print(WiFi.localIP());
  Serial.print(" mask: ");
  Serial.print(WiFi.subnetMask());
  Serial.print(" gw: ");
  Serial.print(WiFi.gatewayIP());

  // print the received signal strength:
  Serial.print(" rssi:");
  Serial.print(WiFi.RSSI());
  Serial.println(" dBm");
}

void mqttPublishBmeData()
{
  float bmeTemperature = -1.0;
  float bmePressure    = -1.0;
  float bmeHumidity    = -1.0;
  if (bmeOK) 
  {
    bmeTemperature = bme.readTemperature();
    bmePressure    = bme.readPressure();
    bmeHumidity    = bme.readHumidity();
  }

  String bmePubString = "{\"bme280\" : {\"temperature\": \"" + String(bmeTemperature) + "\", \"pressure\" : \""
    + String(bmePressure) + "\", \"humidity\" : \"" + String(bmeHumidity) + "\"} }";
  
  bmePubString.toCharArray(pubMsgBuf, bmePubString.length()+1);
  Serial.println(bmePubString);
  mqttClient.publish("demo/devices/arduino", pubMsgBuf);  
  
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i=0;i<length;i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();

  // Switch on the LED if an 1 was received as first character
  if ((char)payload[0] == '1') {
    digitalWrite(BUILTIN_LED, LOW);   // Turn the LED on (Note that LOW is the voltage level
    // but actually the LED is on; this is because
    // it is acive low on the ESP-01)
  } else {
    digitalWrite(BUILTIN_LED, HIGH);  // Turn the LED off by making the voltage HIGH
  }
}


void mqttReconnect() {
  // Loop until we're reconnected
  while (!mqttClient.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (mqttClient.connect("arduinoClient")) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      mqttClient.publish("outTopic","hello world");
      // ... and resubscribe
      mqttClient.subscribe("inTopic");
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

