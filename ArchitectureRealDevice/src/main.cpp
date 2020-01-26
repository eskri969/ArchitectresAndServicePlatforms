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
int lightIndicator = A0;
int weigthIndicator1 = A0;
int weigthIndicator2 = A0;
int weigthIndicator3 = A0;

int n=0;
void sendTelemetry(){
  Serial.printf("Sending %d\n",n);
  /*
  Serial.print(F("Temp:"));
  Serial.print(event.temperature);
  dht.humidity().getEvent(&event);
  Serial.print(F("\tHum:"));
  Serial.println(event.relative_humidity);
  */
  temperatureOut=0;
  humidityOut=0;
  weigth0=0;
  weigth1=0;
  weigth2=0;
  X=0;
  Y=0;
  Z=0;
  co2=0;
  //msg="{\"temperatureIn\":"+str(temperatureIn)+",\"temperatureOut\":"+str(temperatureOut)+",\"humidityIn\":"+str(humidityIn)+",\"humidityOut\":"+str(humidityOut)+",\"weigth0\":"+str(weigth0)+",\"weigth1\":"+str(weigth1)+",\"weigth2\":"+str(weigth2)+",\"X\":"+str(X)+",\"Y\":"+str(Y)+",\"Z\":"+str(Z)+",\"CO2\":"+str(CO2)+"}"
  sprintf(msg,"{\"temperatureIn\":%f,\"temperatureOut\":%f,\"humidityIn\":%f,\"humidityOut\":%f,\"weigth0\":%f,\"weigth1\":%f,\"weigth2\":%f,\"X\":%f,\"Y\":%f,\"Z\":%f,\"CO2\":%f}",
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
  /*
  sprintf(msg,"{\"temperatureIn\":%f,\"temperatureOut\":%f,\"humidityIn\":%f,\"humidityOut\":%f,\"weigth0\":%f,\"weigth1\":%f,\"weigth2\":%f}",
    temperatureIn,
    temperatureOut,
    humidityIn,
    humidityOut,
    weigth0,
    weigth1,
    weigth2);
  */
  if (client.publish(hive_telemetry, msg)) {
      Serial.println("hive_telemetry sent");
  }
  n+=1;
}

void setup()
{
  Serial.begin(115200);
  //////Setup sensor
  dht.begin();
  Wire.begin(sda, scl);
  MPU6050_Init();
  // Print temperature sensor details.
  sensor_t sensor;
  dht.temperature().getSensor(&sensor);
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
  sensors_event_t event;
  dht.temperature().getEvent(&event);
  Serial.print(F("Temp:"));
  Serial.print(event.temperature);
  temperatureIn=event.temperature;
  dht.humidity().getEvent(&event);
  Serial.print(F("\tHum:"));
  Serial.println(event.relative_humidity);
  humidityIn=event.relative_humidity;
  //Serial.printf("hum: %f, temp: %f\n",humidityIn,temperatureIn);

  double Ax, Ay, Az, T, Gx, Gy, Gz;

  Read_RawValue(MPU6050SlaveAddress, MPU6050_REGISTER_ACCEL_XOUT_H);

  //divide each with their sensitivity scale factor
  Ax = (double)AccelX/AccelScaleFactor;
  Ay = (double)AccelY/AccelScaleFactor;
  Az = (double)AccelZ/AccelScaleFactor;
  T = (double)Temperature/340+36.53; //temperature formula
  Gx = (double)GyroX/GyroScaleFactor;
  Gy = (double)GyroY/GyroScaleFactor;
  Gz = (double)GyroZ/GyroScaleFactor;

  Serial.print("Ax: "); Serial.print(Ax);
  Serial.print(" Ay: "); Serial.print(Ay);
  Serial.print(" Az: "); Serial.print(Az);
  Serial.print(" T: "); Serial.print(T);
  Serial.print(" Gx: "); Serial.print(Gx);
  Serial.print(" Gy: "); Serial.print(Gy);
  Serial.print(" Gz: "); Serial.println(Gz);
  delay(2000);
}
