import logging
import time
import sys
import random
import json
## Libraries for thingsboard communication management
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
## Libraries for hive sensors management as mqtt gateway
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)


## Thinsgboard address
server_address = "srv-iot.diatel.upm.es"

## Thinsgboard devices def
device1 = TBDeviceMqttClient(server_address, "IU8rjHe8MCyu0A0oqk7S")
device2 = TBDeviceMqttClient(server_address, "QCDjqx2llqZp3Wr6NAvY")
device3 = TBDeviceMqttClient(server_address, "PN9ZCENmB0jvEc8WHMyX")
#device4 = TBDeviceMqttClient(server_address, "")

# Thingsboard device functions
def TB_connect_all():
    device1.connect()
    device2.connect()
    device3.connect()

## Hive gateway def
hivegt = mqtt.Client(protocol=mqtt.MQTTv311, transport="tcp")
mosquitto_broker = "127.0.0.1"
messages_hist = {"hive1":{0:{"ts": 0,"temperatureIn": 0,"temperatureOut": 0,"humidityIn": 0,"humidityOut": 0,"weigth0": 0,"weigth1": 0,"weigth2": 0,"weigth3": 0,"weigth4": 0,"weigth4": 0,"X": 0,"Y": 0,"Z": 0,"C02": 0}},
                "hive2":{0:{"ts": 0,"temperatureIn": 0,"temperatureOut": 0,"humidityIn": 0,"humidityOut": 0,"weigth0": 0,"weigth1": 0,"weigth2": 0,"weigth3": 0,"weigth4": 0,"weigth4": 0,"X": 0,"Y": 0,"Z": 0,"C02": 0}},
                "hive3":{0:{"ts": 0,"temperatureIn": 0,"temperatureOut": 0,"humidityIn": 0,"humidityOut": 0,"weigth0": 0,"weigth1": 0,"weigth2": 0,"weigth3": 0,"weigth4": 0,"weigth4": 0,"X": 0,"Y": 0,"Z": 0,"C02": 0}},
                "hive4":{0:{"ts": 0,"temperatureIn": 0,"temperatureOut": 0,"humidityIn": 0,"humidityOut": 0,"weigth0": 0,"weigth1": 0,"weigth2": 0,"weigth3": 0,"weigth4": 0,"weigth4": 0,"X": 0,"Y": 0,"Z": 0,"C02": 0}},
                }
#TODO define topics for a proper message receptions

# Hivegt functions
def stop_hivegt():
    hivegt.loop_stop()

def start_hive_gt():
    hivegt.on_connect = on_connect
    hivegt.on_disconnect = on_disconnect
    hivegt.on_message = on_message
    hivegt.connect(mosquitto_broker, 1883, 60)
    hivegt.loop_start()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    hivegt.subscribe("hive/#")

def on_message(client, userdata, msg):
    print("NEW MSG -> "+msg.topic+" "+str(msg.payload.decode('UTF-8')))
    msg_dict=json.loads(msg.payload.decode('UTF-8'))
    print(msg_dict)
    if "hive/1" in msg.topic:
        print("hive1")
        if msg.topic == "hive/1/alert":
            pass
        elif msg.topic == "hive/1/telemetry":
            print("telemetry")
            messages_hist["hive1"][1]={"temperatureIn": 0}
            messages_hist["hive1"][1]["temperatureIn"]=15
            messages_hist["hive1"][0]["temperatureIn"]=15
            print("telemetry")
            print(json.dumps(messages_hist["hive1"]))
    if msg.topic == "hive/2":
        pass
    if msg.topic == "hive/3":
        pass
    if msg.topic == "hive/4":
        pass

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print ("Unexpected MQTT disconnection. Will auto-reconnect")

## Main initialization and thread
if __name__ == "__main__":
    try:
        start_hive_gt()
        TB_connect_all()
        while True:
            x = random.randrange(0, 50)
            telemetry = {"temperature": x,"humidity": x+5}
            device1.send_telemetry(telemetry)
            device2.send_telemetry(telemetry)
            device3.send_telemetry(telemetry)
            time.sleep(5)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    finally:
        hivegt.loop_stop(force=False)
        sys.exit(0)
