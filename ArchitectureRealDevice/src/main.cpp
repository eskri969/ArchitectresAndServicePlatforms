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
const uint8_t scl = 5;
const uint8_t sda = 4;

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
const char* ssid = "Wall-e";
const char* wifi_password = "@gmail.com";

// MQTT
// Make sure to update this for your own MQTT Broker!
const char* mqtt_server = "192.168.43.89";
///GeneralTopics
const char* hive_telemetry = "hive/3/telemetry";
const char* hive_alert = "hive/3/alert";
const char* set_sampling_period = "hive/3/setSamplingPeriod";
const char* set_light_indicator = "hive/3/setIndicatorLight";
const char* set_weight_indicator = "hive/3/setweightIndicator";
const char* criticMaxTempIn = "hive/3/alert/tempIn/max";
const char* criticMinTempIn = "hive/3/alert/tempIn/mix";
const char* criticMaxHumIn = "hive/3/alert/humIn/max";
const char* criticMinHumIn = "hive/3/alert/humIn/mix";
const char* criticMaxCo2In = "hive/3/alert/co2/max";
const char* criticMinCo2In = "hive/3/alert/co2/mix";
const char* criticMaxTempOut = "hive/3/alert/tempOut/max";
const char* criticMinTempOut = "hive/3/alert/tempOut/mix";
const char* falltopic = "hive/3/alert/fall";
const char* thefttopic = "hive/3/alert/theft";




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
float lat=40.388875;
float lng=-3.628660;
//Timers
void sendTelemetry();
Ticker timer1(sendTelemetry,60000, 0, MILLIS);
//HW declarations
int lightIndicator = 14;
int weigthIndicator1 = 12;
int weigthIndicator2 = 13;
int weigthIndicator3 = 15;
int pinTheft = 16;

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

int read_acc(){
  Read_RawValue(MPU6050SlaveAddress, MPU6050_REGISTER_ACCEL_XOUT_H);
  X = (float)AccelX/AccelScaleFactor;
  Y = (float)AccelY/AccelScaleFactor;
  Z = (float)AccelZ/AccelScaleFactor;
  Serial.printf("X:%f Y:%f Z:%f\n",X,Y,Z);
  if( Z<0.6 || Y>0.3 || Y<-0.3 || X>0.3 || X<-0.3){
    return 1;
  }
  else{
    return 0;
  }
}

void read_dht(){
  sensors_event_t event;
  dht.temperature().getEvent(&event);
  temperatureIn=event.temperature;
  if(temperatureIn>40){
    sprintf(msg,"%f",temperatureIn);
    if (client.publish(criticMaxTempIn, msg)){
        Serial.println("temperatureIn alert");
    }
  }
  else if(temperatureIn<15){
    sprintf(msg,"%f",temperatureIn);
    if (client.publish(criticMinTempIn, msg)){
        Serial.println("temperatureIn alert");
    }
  }
  temperatureOut=temperatureIn+5;
  if(temperatureOut>45){
    sprintf(msg,"%f",temperatureOut);
    if (client.publish(criticMaxTempOut, msg)){
        Serial.println("temperatureOut alert");
    }
  }
  else if(temperatureOut<0){
    sprintf(msg,"%f",temperatureOut);
    if (client.publish(criticMinTempOut, msg)){
        Serial.println("temperatureOut alert");
    }
  }
  dht.humidity().getEvent(&event);
  humidityIn=event.relative_humidity;
  if(humidityIn>75){
    sprintf(msg,"%f",humidityIn);
    if (client.publish(criticMaxHumIn, msg)){
        Serial.println("humidityIn alert");
    }
  }
  else if(humidityIn<15){
    sprintf(msg,"%f",humidityIn);
    if (client.publish(criticMinHumIn, msg)){
        Serial.println("humidityIn alert");
    }
  }
  humidityOut=humidityIn-10;
}

void sendTelemetry(){
  Serial.printf("Sending %d\n",n);
  weigth0=random(0,5);
  weigth1=random(0,5);
  weigth2=random(0,5);
  co2=random(0,80);
  read_dht();
  if(!read_acc()){
    sprintf(msg,"{\"temperatureIn\":%f,\"temperatureOut\":%f,\"humidityIn\":%f,\"humidityOut\":%f,\"weight0\":%f,\"weight1\":%f,\"weight2\":%f,\"CO2\":%f}",
            temperatureIn,
            temperatureOut,
            humidityIn,
            humidityOut,
            weigth0,
            weigth1,
            weigth2,
            co2);
  }
  else{
    int theft = digitalRead(pinTheft);
    Serial.printf("Theft: %d\n",theft);
    if (theft == HIGH){
      if (client.publish(thefttopic, "")) {
          Serial.println("theft sent");
      }
      sprintf(msg,"{\"temperatureIn\":%f,\"temperatureOut\":%f,\"humidityIn\":%f,\"humidityOut\":%f,\"weight0\":%f,\"weight1\":%f,\"weight2\":%f,\"X\":%f,\"Y\":%f,\"Z\":%f,\"CO2\":%f,\"lat\":%f,\"lng\":%f}",
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
              co2,
              lat,
              lng);
    }
    else if (theft == LOW){
      if (client.publish(falltopic, "")) {
          Serial.println("fall sent");
      }
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
    }
  }
  n++;
  if (client.publish(hive_telemetry, msg)) {
      Serial.println("hive_telemetry sent");
  }
}

void ReceivedMessage(char* topic, byte* payload, unsigned int length) {
  // Output the first character of the message to serial (debug)
  //String msg_received = (char*)payload;
  char var[50];
  for (unsigned int i = 0; i < length; i++) {
    var[i]=((char)payload[i]);
    //Serial.printf("%d%c\n",i,((char)payload[i]));
  }
  Serial.printf("\n%s\t%s\t%d\n",topic,var,length);

  if(strcmp(topic, set_sampling_period)==0){
    Serial.printf("set_sampling_period %d\n",atoi(var));
    timer1.interval(atoi(var)*1000);
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
  if(strcmp(topic, set_weight_indicator)==0){
    Serial.printf("set_weight_indicator\n");
    Serial.printf("0:%c 1:%c 2:%c\n",var[14],var[30],var[46]);
    if(atoi(&var[14])==1){
      Serial.printf("weight0 ON\t");
      digitalWrite(weigthIndicator1,HIGH);
    }
    else if(atoi(&var[14])==0){
      Serial.printf("weight0 OFF\t");
      digitalWrite(weigthIndicator1,LOW);
    }
    if(atoi(&var[30])==1){
      Serial.printf("weight1 ON\t");
      digitalWrite(weigthIndicator2,HIGH);
    }
    else if(atoi(&var[30])==0){
      Serial.printf("weight1 OFF\t");
      digitalWrite(weigthIndicator2,LOW);
    }
    if(atoi(&var[46])==1){
      Serial.printf("weight2 ON\n");
      digitalWrite(weigthIndicator3,HIGH);
    }
    else if(atoi(&var[46])==0){
      Serial.printf("weight1 OFF\n");
      digitalWrite(weigthIndicator3,LOW);
    }
  }
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
  //Setup Button
  pinMode(pinTheft, INPUT);

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
