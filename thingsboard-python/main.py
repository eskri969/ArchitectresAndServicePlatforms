import logging
import time
import sys
import random
import json
import threading
## Libraries for thingsboard communication management
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
## Libraries for hive sensors management as mqtt gateway
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.INFO)


## Thinsgboard vad def
server_address = "srv-iot.diatel.upm.es"

msg_to_TB_hist = {
    "ts": 0,
    "hive1":{"values":{0:{"nsamples": 0,"avtemperatureIn": 0,"avtemperatureOut": 0,"avhumidityIn": 0,"avhumidityOut": 0,"avweigth0": 0,"avweigth1": 0,"avweigth2": 0,"avweigth3": 0,"avweigth4": 0,"avweigth4": 0,"avX": 0,"avY": 0,"avZ": 0,"avC02": 0}},
            "notifications":{0:{"ts": 0,"alert_temp":"","alert_hum":"","weigth0": "ok","weigth1": "ok","weigth2": "ok","accel_alert":"","C02_alert":""}}},
    "hive2":{"values":{0:{"nsamples": 0,"avtemperatureIn": 0,"avtemperatureOut": 0,"avhumidityIn": 0,"avhumidityOut": 0,"avweigth0": 0,"avweigth1": 0,"avweigth2": 0,"avweigth3": 0,"avweigth4": 0,"avweigth4": 0,"avX": 0,"avY": 0,"avZ": 0,"avC02": 0}},
            "notifications":{0:{"ts": 0,"alert_temp":"","alert_hum":"","weigth0": "ok","weigth1": "ok","weigth2": "ok","accel_alert":"","C02_alert":""}}},
    "hive3":{"values":{0:{"nsamples": 0,"avtemperatureIn": 0,"avtemperatureOut": 0,"avhumidityIn": 0,"avhumidityOut": 0,"avweigth0": 0,"avweigth1": 0,"avweigth2": 0,"avweigth3": 0,"avweigth4": 0,"avweigth4": 0,"avX": 0,"avY": 0,"avZ": 0,"avC02": 0}},
            "notifications":{0:{"ts": 0,"alert_temp":"","alert_hum":"","weigth0": "ok","weigth1": "ok","weigth2": "ok","accel_alert":"","C02_alert":""}}}
    }
value_TB_1=0
value_TB_2=0
value_TB_3=0
last_value_sent_ts=0
notif_TB_1=0
notif_TB_2=0
notif_TB_3=0


## Thinsgboard devices def
device1 = TBDeviceMqttClient(server_address, "IU8rjHe8MCyu0A0oqk7S")
device2 = TBDeviceMqttClient(server_address, "QCDjqx2llqZp3Wr6NAvY")
device3 = TBDeviceMqttClient(server_address, "PN9ZCENmB0jvEc8WHMyX")

# Thingsboard device functions
def TB_connect_all():
    device1.connect()
    device2.connect()
    device3.connect()

## Hive gateway def
hivegt = mqtt.Client(protocol=mqtt.MQTTv311, transport="tcp")
mosquitto_broker = "127.0.0.1"
msg_from_hive_hist = {
    "hive1":{"values":{0:{"ts": 0,"temperatureIn": 0,"temperatureOut": 0,"humidityIn": 0,"humidityOut": 0,"weigth0": 0,"weigth1": 0,"weigth2": 0,"X": 0,"Y": 0,"Z": 0,"C02": 0}},
            "notifications":{0:{"ts": 0,"alert_temp":"","alert_hum":"","weigth0": "ok","weigth1": "ok","weigth2": "ok","accel_alert":"","C02_alert":""}}},
    "hive2":{"values":{0:{"ts": 0,"temperatureIn": 0,"temperatureOut": 0,"humidityIn": 0,"humidityOut": 0,"weigth0": 0,"weigth1": 0,"weigth2": 0,"X": 0,"Y": 0,"Z": 0,"C02": 0}},
            "notifications":{0:{"ts": 0,"alert_temp":"","alert_hum":"","weigth0": "ok","weigth1": "ok","weigth2": "ok","accel_alert":"","C02_alert":""}}},
    "hive3":{"values":{0:{"ts": 0,"temperatureIn": 0,"temperatureOut": 0,"humidityIn": 0,"humidityOut": 0,"weigth0": 0,"weigth1": 0,"weigth2": 0,"X": 0,"Y": 0,"Z": 0,"C02": 0}},
            "notifications":{0:{"ts": 0,"alert_temp":"","alert_hum":"","weigth0": "ok","weigth1": "ok","weigth2": "ok","accel_alert":"","C02_alert":""}}}
    }
value_hive_1=0
value_hive_2=0
value_hive_3=0
notif_hive_1=0
notif_hive_2=0
notif_hive_3=0

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
    if "hive/1" in msg.topic:
        global value_hive_1
        print("hive1")
        if msg.topic == "hive/1/alert":
            pass
        elif msg.topic == "hive/1/telemetry":
            print("telemetry from hive1 -> "+str(value_hive_1))
            msg_from_hive_hist["hive1"]["values"][value_hive_1]={}
            msg_from_hive_hist["hive1"]["values"][value_hive_1]["ts"]=time.time()
            msg_from_hive_hist["hive1"]["values"][value_hive_1].update(msg_dict)
            print(json.dumps(msg_from_hive_hist["hive1"])+"\n")
            value_hive_1 +=1
    if "hive/2" in msg.topic:
        global value_hive_2
        print("hive2")
        if msg.topic == "hive/2/alert":
            pass
        elif msg.topic == "hive/2/telemetry":
            print("telemetry from hive2 -> "+str(value_hive_2))
            msg_from_hive_hist["hive2"]["values"][value_hive_2]={}
            msg_from_hive_hist["hive2"]["values"][value_hive_2]["ts"]=time.time()
            msg_from_hive_hist["hive2"]["values"][value_hive_2].update(msg_dict)
            print(json.dumps(msg_from_hive_hist["hive2"])+"\n")
            value_hive_2 +=1
    if "hive/3" in msg.topic:
        global value_hive_3
        print("hive3")
        if msg.topic == "hive/3/alert":
            pass
        elif msg.topic == "hive/3/telemetry":
            print("telemetry from hive3 -> "+str(value_hive_3))
            msg_from_hive_hist["hive3"]["values"][value_hive_3]={}
            msg_from_hive_hist["hive3"]["values"][value_hive_3]["ts"]=time.time()
            msg_from_hive_hist["hive3"]["values"][value_hive_3].update(msg_dict)
            print(json.dumps(msg_from_hive_hist["hive3"])+"\n")
            value_hive_3 +=1
            print("sent")


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print ("Unexpected MQTT disconnection. Will auto-reconnect")

## Device intelligence functions
def calculate_avg(key,time_frame):
    print(value_hive_1)
    ns=0
    ts=time.time()
    print(ts)
    result=0
    for i in range(value_hive_1-1,-1,-1):
        if(msg_from_hive_hist["hive1"]["values"][i]["ts"])<(ts-time_frame):
            break
        result+=msg_from_hive_hist["hive1"]["values"][i][key]
        print("i="+str(i)+" "+json.dumps(msg_from_hive_hist["hive1"]["values"][i]["ts"]))
        ns+=1
    print("r"+str(result))
    print(ns)
    if(ns>0):
        return result/ns
    else:
        return 0

def publish_avg(time_frame):
    print("calculate")
    print(calculate_avg("temperatureIn",time_frame))

def periodic_avg(time_frame):
    publish_avg(time_frame)
    timer = threading.Timer(time_frame, periodic_avg, args=(time_frame,))
    timer.start()

## Main initialization and thread
if __name__ == "__main__":
    try:
        start_hive_gt()
        TB_connect_all()
        periodic_avg(20)
        while True:
            x = random.randrange(0, 50)
            telemetry = {"temperature": x,"humidity": x+5}
            #device1.send_telemetry(telemetry)
            #device2.send_telemetry(telemetry)
            #device3.send_telemetry(telemetry)
            time.sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        hivegt.loop_stop(force=False)
        sys.exit(0)
