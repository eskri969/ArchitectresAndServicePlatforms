#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <ESP8266WiFi.h> // Enables the ESP8266 to connect to the local network (via WiFi)
#include <PubSubClient.h> // Allows us to connect to, and publish to the MQTT broker
#include <Wire.h>
#include "Ticker.h"

////////////DHT
#define DHTPIN 2     // Digital pin connected to the DHT sensor
// Feather HUZZAH ESP8266 note: use pins 3, 4, 5, 12, 13 or 14 --
// Pin 15 can work but DHT must be disconnected during program upload.

// Uncomment the type of sensor in use:
#define DHTTYPE    DHT11     // DHT 11
DHT_Unified dht(DHTPIN, DHTTYPE);

//////////ACC
// MPU6050 Slave Device Address
const uint8_t MPU6050SlaveAddress = 0x68;

// Select SDA and SCL pins for I2C communication
const uint8_t scl = 4;
const uint8_t sda = 5;

// sensitivity scale factor respective to full scale setting provided in datasheet
const uint16_t AccelScaleFactor = 16384;
const uint16_t GyroScaleFactor = 131;

// MPU6050 few configuration register addresses
const uint8_t MPU6050_REGISTER_SMPLRT_DIV   =  0x19;
const uint8_t MPU6050_REGISTER_USER_CTRL    =  0x6A;
const uint8_t MPU6050_REGISTER_PWR_MGMT_1   =  0x6B;
const uint8_t MPU6050_REGISTER_PWR_MGMT_2   =  0x6C;
const uint8_t MPU6050_REGISTER_CONFIG       =  0x1A;
const uint8_t MPU6050_REGISTER_GYRO_CONFIG  =  0x1B;
const uint8_t MPU6050_REGISTER_ACCEL_CONFIG =  0x1C;
const uint8_t MPU6050_REGISTER_FIFO_EN      =  0x23;
const uint8_t MPU6050_REGISTER_INT_ENABLE   =  0x38;
const uint8_t MPU6050_REGISTER_ACCEL_XOUT_H =  0x3B;
const uint8_t MPU6050_REGISTER_SIGNAL_PATH_RESET  = 0x68;

int16_t AccelX, AccelY, AccelZ, Temperature, GyroX, GyroY, GyroZ;

// WiFi
// Make sure to update this for your own WiFi network!
const char* ssid = "CentralPerk";
const char* wifi_password = "@gmail.com";

// MQTT
// Make sure to update this for your own MQTT Broker!
const char* mqtt_server = "192.168.0.128";
///GeneralTopics
const char* hive_telemetry = "hive/3/telemetry";
const char* hive_alert = "hive/3/alert";
const char* set_sampling_period = "hive/3/setSamplingPeriod";
const char* set_light_indicator = "hive/3/setIndicatorLight";
const char* set_weight_indicator = "hive/3/setweightIndicator";



// The client id identifies the ESP8266 device. Think of it a bit like a hostname (Or just a name, like Greg).
const char* clientID = "hive3";
//boolean connect (clientID, willTopic, willQoS, willRetain, willMessage)
const char* willTopic = "node_disconnected";
const int willQoS = 1;
const boolean willRetain = true;
const char* willMessage = clientID;
// Initialise the WiFi and MQTT Client objects
WiFiClient wifiClient;
PubSubClient client(mqtt_server, 1883, wifiClient); // 1883 is the listener port for the Broker
char msg[300];
//System vatibales
float temperatureIn=0;
float temperatureOut=0;
float humidityIn=0;
float humidityOut=0;
float weigth0=0;
float weigth1=0;
float weigth2=0;
float X=0;
float Y=0;
float Z=0;
float co2=0;
float sampling_delay=5000;
//Timers
void sendTelemetry();
Ticker timer1(sendTelemetry,10000, 0, MILLIS);
//HW declarations
int lightIndicator = 14;
int weigthIndicator1 = 12;
int weigthIndicator2 = 13;
int weigthIndicator3 = 15;

int n=0;

void I2C_Write(uint8_t deviceAddress, uint8_t regAddress, uint8_t data){
  Wire.beginTransmission(deviceAddress);
  Wire.write(regAddress);
  Wire.write(data);
  Wire.endTransmission();
}

// read all 14 register
void Read_RawValue(uint8_t deviceAddress, uint8_t regAddress){
  Wire.beginTransmission(deviceAddress);
  Wire.write(regAddress);
  Wire.endTransmission();
  Wire.requestFrom(deviceAddress, (uint8_t)14);
  AccelX = (((int16_t)Wire.read()<<8) | Wire.read());
  AccelY = (((int16_t)Wire.read()<<8) | Wire.read());
  AccelZ = (((int16_t)Wire.read()<<8) | Wire.read());
  Temperature = (((int16_t)Wire.read()<<8) | Wire.read());
  GyroX = (((int16_t)Wire.read()<<8) | Wire.read());
  GyroY = (((int16_t)Wire.read()<<8) | Wire.read());
  GyroZ = (((int16_t)Wire.read()<<8) | Wire.read());
}

//configure MPU6050
void MPU6050_Init(){
  delay(150);
  I2C_Write(MPU6050SlaveAddress, MPU6050_REGISTER_SMPLRT_DIV, 0x07);
  I2C_Write(MPU6050SlaveAddress, MPU6050_REGISTER_PWR_MGMT_1, 0x01);
  I2C_Write(MPU6050SlaveAddress, MPU6050_REGISTER_PWR_MGMT_2, 0x00);
  I2C_Write(MPU6050SlaveAddress, MPU6050_REGISTER_CONFIG, 0x00);
  I2C_Write(MPU6050SlaveAddress, MPU6050_REGISTER_GYRO_CONFIG, 0x00);//set +/-250 degree/second full scale
  I2C_Write(MPU6050SlaveAddress, MPU6050_REGISTER_ACCEL_CONFIG, 0x00);// set +/- 2g full scale
  I2C_Write(MPU6050SlaveAddress, MPU6050_REGISTER_FIFO_EN, 0x00);
  I2C_Write(MPU6050SlaveAddress, MPU6050_REGISTER_INT_ENABLE, 0x01);
  I2C_Write(MPU6050SlaveAddress, MPU6050_REGISTER_SIGNAL_PATH_RESET, 0x00);
  I2C_Write(MPU6050SlaveAddress, MPU6050_REGISTER_USER_CTRL, 0x00);
}

void read_acc(){
  Read_RawValue(MPU6050SlaveAddress, MPU6050_REGISTER_ACCEL_XOUT_H);
  X = (float)AccelX/AccelScaleFactor;
  Y = (float)AccelY/AccelScaleFactor;
  Z = (float)AccelZ/AccelScaleFactor;
  //Serial.printf("X:%f Y:%f Z:%f",X,Y,Z);
}

void read_dht(){
  sensors_event_t event;
  dht.temperature().getEvent(&event);
  temperatureIn=event.temperature;
  temperatureOut=temperatureIn+5;
  dht.humidity().getEvent(&event);
  humidityIn=event.relative_humidity;
  humidityOut=humidityIn-10;
}

void sendTelemetry(){
  Serial.printf("Sending %d\n",n);
  read_dht();
  read_acc();
  weigth0=random(0,5);
  weigth1=random(0,5);
  weigth2=random(0,5);
  co2=random(0,80);
  sprintf(msg,"{\"temperatureIn\":%f,\"temperatureOut\":%f,\"humidityIn\":%f,\"humidityOut\":%f,\"weight0\":%f,\"weight1\":%f,\"weight2\":%f,\"X\":%f,\"Y\":%f,\"Z\":%f,\"CO2\":%f}",
          temperatureIn,
          temperatureOut,
          humidityIn,
          humidityOut,
          weigth0,
          weigth1,
          weigth2,
          X,
          Y,
          Z,
          co2);
  if (client.publish(hive_telemetry, msg)) {
      Serial.println("hive_telemetry sent");
  }
  n+=1;
}

void ReceivedMessage(char* topic, byte* payload, unsigned int length) {
  // Output the first character of the message to serial (debug)
  //String msg_received = (char*)payload;
  char var[50];
  for (unsigned int i = 0; i < length; i++) {
    var[i]=((char)payload[i]);
  }
  Serial.printf("\n%s\t%s\t%d\n",topic,var,length);
  if(strcmp(topic, set_sampling_period)==0){
    Serial.printf("set_sampling_period %d\n",atoi(var));
    timer1.interval(atoi(var));
  }
  if(strcmp(topic, set_light_indicator)==0){
    if(atoi(var)==1){
      Serial.printf("set_light_indicator ON\n");
      digitalWrite(lightIndicator,HIGH);
    }
    else if(atoi(var)==0){
      Serial.printf("set_light_indicator OFF\n");
      digitalWrite(lightIndicator,LOW);
    }
  }
  /*
  if(strcmp(topic, set_weight_indicator)==0){
    Serial.printf("set_weight_indicator %d\n",atoi(var));
    if(atoi(var)==1){
    }
    else if(atoi(var)==0){

    }
  }
  */

}

void setup()
{
  Serial.begin(115200);
  //////Setup sensor
  dht.begin();
  Wire.begin(sda, scl);
  MPU6050_Init();
  sensor_t sensor;
  dht.temperature().getSensor(&sensor);
  ///////Setup Lights
  pinMode(lightIndicator, OUTPUT);
  digitalWrite(lightIndicator,LOW);
  pinMode(weigthIndicator1, OUTPUT);
  digitalWrite(weigthIndicator1,LOW);
  pinMode(weigthIndicator2, OUTPUT);
  digitalWrite(weigthIndicator2,LOW);
  pinMode(weigthIndicator3, OUTPUT);
  digitalWrite(weigthIndicator3,LOW);

  ///////Setup MQTT
  // Switch the on-board LED off to start with
  Serial.print("Connecting to ");
  Serial.println(ssid);

  // Connect to the WiFi
  WiFi.begin(ssid, wifi_password);

  // Wait until the connection has been confirmed before continuing
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // Debugging - Output the IP Address of the ESP8266
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  client.setCallback(ReceivedMessage);
  // Connect to MQTT Broker
  // client.connect returns a boolean value to let us know if the connection was successful.
  if (client.connect(clientID, willTopic, willQoS, willRetain, willMessage)) {
    Serial.println("Connected to MQTT Broker!");
  }
  else {
    Serial.println("Connection to MQTT Broker failed...");
  }
  client.subscribe(set_sampling_period);
  client.subscribe(set_light_indicator);
  client.subscribe(set_weight_indicator);
  timer1.start();
}

void loop()
{
  timer1.update();
  client.loop();
}
