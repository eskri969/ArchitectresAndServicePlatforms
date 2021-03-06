import logging
import time
import sys
import random
import json
import threading
from numbers import Number
import datetime
## Libraries for thingsboard communication management
#from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
## Libraries for hive sensors management as mqtt gateway
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import os

import random
import time

# Using the Python Device SDK for IoT Hub:
#   https://github.com/Azure/azure-iot-sdk-python
# The sample connects to a device-specific MQTT endpoint on your IoT Hub.
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse


# The device connection string to authenticate the device with your IoT hub.
# Using the Azure CLI:
# az iot hub device-identity show-connection-string --hub-name {YourIoTHubName} --device-id MyNodeDevice --output table
CONNECTION_STRING1 = "HostName=IoTHubCloud.azure-devices.net;DeviceId=MyDevice1;SharedAccessKey=FBPcxJdDzsncJpc4M6yXauqjhW4hMqECxsp4HdqG8WA="
CONNECTION_STRING2 = "HostName=IoTHubCloud.azure-devices.net;DeviceId=MyDevice2;SharedAccessKey=dpFEacEfBnIa2k7jHcXmWwHSHYoJY4IiyQ+n5ecYLRk="
CONNECTION_STRING3 = "HostName=IoTHubCloud.azure-devices.net;DeviceId=MyDevice3;SharedAccessKey=i8qV22VV8uPQwTfkEqiQgsIfpoxerrY92W6DYxwdDOs="
device1 = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING1)
device2 = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING2)
device3 = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING3)

## Old TB
values_TB_keys=["avtemperatureIn","avtemperatureOut","avhumidityIn","avhumidityOut","avweight0","avweight1","avweight2","avX","avY","avZ","avCO2"]
notif_TB_keys={"statusTempIn":"avtemperatureIn","statusTempOut":"avtemperatureOut","statusHumIn":"avhumidityIn","statusHumOut":"avhumidityOut","statusCO2":"avCO2"}
'''
msg_to_TB_hist = {
    1:{"values":{0:{"ts":0 ,"nsamples": 0,"avtemperatureIn": 0,"avtemperatureOut": 0,"avhumidityIn": 0,"avhumidityOut": 0,"avweight0": 0,"avweight1": 0,"avweight2": 0,"avX": 0,"avY": 0,"avZ": 0,"avCO2": 0,"lat": 0,"lng":0}},
            "notifications":{0:{"alertTempIn":0,"alertTempOut":0,"alertHumIn":0,"alertHumOut":0,"CO2_alert":0}}},
    2:{"values":{0:{"ts":0 ,"nsamples": 0,"avtemperatureIn": 0,"avtemperatureOut": 0,"avhumidityIn": 0,"avhumidityOut": 0,"avweight0": 0,"avweight1": 0,"avweight2": 0,"avX": 0,"avY": 0,"avZ": 0,"avCO2": 0,"lat": 0,"lng":0}},
            "notifications":{0:{"alertTempIn":0,"alertTempOut":0,"alertHumIn":0,"alertHumOut":0,"CO2_alert":0}}},
    3:{"values":{0:{"ts":0 ,"nsamples": 0,"avtemperatureIn": 0,"avtemperatureOut": 0,"avhumidityIn": 0,"avhumidityOut": 0,"avweight0": 0,"avweight1": 0,"avweight2": 0,"avX": 0,"avY": 0,"avZ": 0,"avCO2": 0,"lat": 0,"lng":0}},
            "notifications":{0:{"alertTempIn":0,"alertTempOut":0,"alertHumIn":0,"alertHumOut":0,"CO2_alert":0}}},
    }
'''
msg_to_TB_hist = {
    1:{"values":{0:{"timestamp": 0 ,"avtemperatureIn": 0,"avtemperatureOut": 0,"avhumidityIn": 0,"avhumidityOut": 0,"avweight0": 0,"avweight1": 0,"avweight2": 0,"avX": 0,"avY": 0,"avZ": 0,"avCO2": 0,"lat": 0,"lng":0}},
            "notifications":{0:{"alertTempIn":0,"alertTempOut":0,"alertHumIn":0,"alertHumOut":0,"CO2_alert":0}}},
    2:{"values":{0:{"timestamp": 0,"avtemperatureIn": 0,"avtemperatureOut": 0,"avhumidityIn": 0,"avhumidityOut": 0,"avweight0": 0,"avweight1": 0,"avweight2": 0,"avX": 0,"avY": 0,"avZ": 0,"avCO2": 0,"lat": 0,"lng":0}},
            "notifications":{0:{"alertTempIn":0,"alertTempOut":0,"alertHumIn":0,"alertHumOut":0,"CO2_alert":0}}},
    3:{"values":{0:{"timestamp": 0 ,"avtemperatureIn": 0,"avtemperatureOut": 0,"avhumidityIn": 0,"avhumidityOut": 0,"avweight0": 0,"avweight1": 0,"avweight2": 0,"avX": 0,"avY": 0,"avZ": 0,"avCO2": 0,"lat": 0,"lng":0}},
            "notifications":{0:{"alertTempIn":0,"alertTempOut":0,"alertHumIn":0,"alertHumOut":0,"CO2_alert":0}}},
    }
value_TB={1:0,2:0,3:0}
notif_TB={1:0,2:0,3:0}

###### PERIOD ######
gatewaySamplingPeriod=10

###Hive MQTTv311
## Hive gateway def
hivegt = mqtt.Client(protocol=mqtt.MQTTv311, transport="tcp")
mosquitto_broker = "127.0.0.1"
clear_hive_att={"criticTempIn":0,"criticTempOut":0,"criticHumIn":0,"criticHumOut":0,"criticCo2":0}
values_hive_keys=["temperatureIn","temperatureOut","humidityIn","humidityOut","weight0","weight1","weight2","X","Y","Z","CO2"]
msg_from_hive_hist = {
    1:{"values":{0:{"ts": 0,"temperatureIn": 0,"temperatureOut": 0,"humidityIn": 0,"humidityOut": 0,"weight0": 0,"weight1": 0,"weight2": 0,"X": 0,"Y": 0,"Z": 0,"CO2": 0,"lat": 0,"lng":0}},
            "notifications":{0:{"ts": 0,"alert_temp": 0,"alert_hum": 0,"weight0": 0,"weight1": 0,"weight2": 0,"accel_alert":0,"CO2_alert":0}}},
    2:{"values":{0:{"ts": 0,"temperatureIn": 0,"temperatureOut": 0,"humidityIn": 0,"humidityOut": 0,"weight0": 0,"weight1": 0,"weight2": 0,"X": 0,"Y": 0,"Z": 0,"CO2": 0,"lat": 0,"lng":0}},
            "notifications":{0:{"ts": 0,"alert_temp": 0,"alert_hum": 0,"weight0": 0,"weight1": 0,"weight2": 0,"accel_alert":0,"CO2_alert":0}}},
    3:{"values":{0:{"ts": 0,"temperatureIn": 0,"temperatureOut": 0,"humidityIn": 0,"humidityOut": 0,"weight0": 0,"weight1": 0,"weight2": 0,"X": 0,"Y": 0,"Z": 0,"CO2": 0,"lat": 0,"lng":0}},
            "notifications":{0:{"ts": 0,"alert_temp": 0,"alert_hum": 0,"weight0": 0,"weight1": 0,"weight2": 0,"accel_alert":0,"CO2_alert":0}}},
    }
value_hive={1:0,2:0,3:0}
notif_hive={1:0,2:0,3:0}
sampling_period_hive={1:60,2:60,3:60}
light_indicator_hive={1:0,2:0,3:0}
weight_indicator_hive={1:0,2:0,3:0}
weight_th=2

## Hivegt functions
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
    hivegt.subscribe("hive/+/alert/#")
    hivegt.subscribe("hive/+/telemetry")

def on_message(client, userdata, msg):
    print("NEW MSG -> "+msg.topic+" "+str(msg.payload.decode('UTF-8'))+"\n")
    msg_dict=json.loads(msg.payload.decode('UTF-8'))
    global value_hive
    if "hive/1" in msg.topic:
        '''
        if "/alert" in msg.topic:
            print("alert1 "+msg.topic)
            if "/tempIn" in msg.topic:
                if "/max" in msg.topic:
                    attributes = {"criticTempIn": 2}
                    device1.send_message(Message(json.dumps(attributes)))
                elif "/min" in msg.topic:
                    attributes = {"criticTempIn": 1}
                    device1.send_message(Message(json.dumps(attributes)))
            elif "/humIn" in msg.topic:
                if "/max" in msg.topic:
                    attributes = {"criticHumIn": 2}
                    device1.send_message(Message(json.dumps(attributes)))
                elif "/min" in msg.topic:
                    attributes = {"criticHumIn": 1}
                    device1.send_message(Message(json.dumps(attributes)))
            elif "/co2" in msg.topic:
                if "/max" in msg.topic:
                    attributes = {"criticCo2": 2}
                    device1.send_message(Message(json.dumps(attributes)))
                elif "/min" in msg.topic:
                    attributes = {"criticCo2": 1}
                    device1.send_message(Message(json.dumps(attributes)))
            elif "/tempOut" in msg.topic:
                if "/max" in msg.topic:
                    attributes = {"criticTempOut": 2}
                    device1.send_message(Message(json.dumps(attributes)))
                elif "/min" in msg.topic:
                    attributes = {"criticTempOut": 1}
                    device1.send_message(Message(json.dumps(attributes)))
            elif "/fall" in msg.topic:
                attributes = {"statusFall": 1}
                device1.send_message(Message(json.dumps(attributes)))
            elif "/move" in msg.topic:
                attributes = {"statusMove": 1}
                device1.send_message(Message(json.dumps(attributes)))
            msg_from_hive_hist[1]["notifications"][value_hive[1]]={}
            msg_from_hive_hist[1]["notifications"][value_hive[1]]["ts"]=time.time()
            msg_from_hive_hist[1]["notifications"][value_hive[1]].update(msg_dict)
            notif_hive[1] +=1
        elif "/telemetry" in msg.topic:
        '''
        if "/telemetry" in msg.topic:
            #print("telemetry from hive1 -> "+str(value_hive[1]))
            msg_from_hive_hist[1]["values"][value_hive[1]]={}
            msg_from_hive_hist[1]["values"][value_hive[1]]["ts"]=time.time()
            msg_from_hive_hist[1]["values"][value_hive[1]].update(msg_dict)
            #print(json.dumps(msg_from_hive_hist[1])+"\n")
            value_hive[1] +=1
    if "hive/2" in msg.topic:
        #print("hive2")
        '''
        if "/alert" in msg.topic:
            print("alert2 "+msg.topic)
            if "/tempIn" in msg.topic:
                if "/max" in msg.topic:
                    attributes = {"criticTempIn": 2}
                    device2.send_message(Message(json.dumps(attributes)))
                elif "/min" in msg.topic:
                    attributes = {"criticTempIn": 1}
                    device2.send_message(Message(json.dumps(attributes)))
            elif "/humIn" in msg.topic:
                if "/max" in msg.topic:
                    attributes = {"criticHumIn": 2}
                    device2.send_message(Message(json.dumps(attributes)))
                elif "/min" in msg.topic:
                    attributes = {"criticHumIn": 1}
                    device2.send_message(Message(json.dumps(attributes)))
            elif "/co2" in msg.topic:
                if "/max" in msg.topic:
                    attributes = {"criticCo2": 2}
                    device2.send_message(Message(json.dumps(attributes)))
                elif "/min" in msg.topic:
                    attributes = {"criticCo2": 1}
                    device2.send_message(Message(json.dumps(attributes)))
            elif "/tempOut" in msg.topic:
                if "/max" in msg.topic:
                    attributes = {"criticTempOut": 2}
                    device2.send_message(Message(json.dumps(attributes)))
                elif "/min" in msg.topic:
                    attributes = {"criticTempOut": 1}
                    device2.send_message(Message(json.dumps(attributes)))
            elif "/fall" in msg.topic:
                attributes = {"statusFall": 1}
                device2.send_message(Message(json.dumps(attributes)))
            elif "/move" in msg.topic:
                attributes = {"statusMove": 1}
                device2.send_message(Message(json.dumps(attributes)))
            msg_from_hive_hist[2]["notifications"][value_hive[2]]={}
            msg_from_hive_hist[2]["notifications"][value_hive[2]]["ts"]=time.time()
            msg_from_hive_hist[2]["notifications"][value_hive[2]].update(msg_dict)
            notif_hive[2] +=1
        elif "/telemetry" in msg.topic:
        '''
        if "/telemetry" in msg.topic:
            #print("telemetry from hive2 -> "+str(value_hive[2]))
            msg_from_hive_hist[2]["values"][value_hive[2]]={}
            msg_from_hive_hist[2]["values"][value_hive[2]]["ts"]=time.time()
            msg_from_hive_hist[2]["values"][value_hive[2]].update(msg_dict)
            #print(json.dumps(msg_from_hive_hist["hive2"])+"\n")
            value_hive[2] +=1
    if "hive/3" in msg.topic:
        '''
        if "/alert" in msg.topic:
            print("alert3 "+msg.topic)
            if "/tempIn" in msg.topic:
                if "/max" in msg.topic:
                    attributes = {"criticTempIn": 2}
                    device3.send_message(Message(json.dumps(attributes)))
                elif "/min" in msg.topic:
                    attributes = {"criticTempIn": 1}
                    device3.send_message(Message(json.dumps(attributes)))
            elif "/humIn" in msg.topic:
                if "/max" in msg.topic:
                    attributes = {"criticHumIn": 2}
                    device3.send_message(Message(json.dumps(attributes)))
                elif "/min" in msg.topic:
                    attributes = {"criticHumIn": 1}
                    device3.send_message(Message(json.dumps(attributes)))
            elif "/co2" in msg.topic:
                if "/max" in msg.topic:
                    attributes = {"criticCo2": 2}
                    device3.send_message(Message(json.dumps(attributes)))
                elif "/min" in msg.topic:
                    attributes = {"criticCo2": 1}
                    device3.send_message(Message(json.dumps(attributes)))
            elif "/tempOut" in msg.topic:
                if "/max" in msg.topic:
                    attributes = {"criticTempOut": 2}
                    device3.send_message(Message(json.dumps(attributes)))
                elif "/min" in msg.topic:
                    attributes = {"criticTempOut": 1}
                    device3.send_message(Message(json.dumps(attributes)))
            elif "/fall" in msg.topic:
                attributes = {"statusFall": 1}
                device3.send_message(Message(json.dumps(attributes)))
            elif "/move" in msg.topic:
                attributes = {"statusMove": 1}
                device3.send_message(Message(json.dumps(attributes)))
            msg_from_hive_hist[3]["notifications"][value_hive[3]]={}
            msg_from_hive_hist[3]["notifications"][value_hive[3]]["ts"]=time.time()
            msg_from_hive_hist[3]["notifications"][value_hive[3]].update(msg_dict)
            notif_hive[3] +=1
        elif "/telemetry" in msg.topic:
        '''
        if "/telemetry" in msg.topic:
            #print("telemetry from hive3 -> "+str(value_hive[3]))
            msg_from_hive_hist[3]["values"][value_hive[3]]={}
            msg_from_hive_hist[3]["values"][value_hive[3]]["ts"]=time.time()
            msg_from_hive_hist[3]["values"][value_hive[3]].update(msg_dict)
            #print(json.dumps(msg_from_hive_hist["hive3"])+"\n")
            value_hive[3] +=1

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print ("Unexpected MQTT disconnection. Will auto-reconnect")

## Send telemetry to Azure
## Device intelligence functions
def calculate_ns(time_frame,ts,hive):
    ns=0
    for i in range(value_hive[hive]-1,-1,-1):
        if(msg_from_hive_hist[hive]["values"][i]["ts"])<(ts-time_frame):
            break
        ns+=1
    return ns


def calculate_avg(key,time_frame,ts,hive):
    ns=0
    result=0
    for i in range(value_hive[hive]-1,-1,-1):
        if(msg_from_hive_hist[hive]["values"][i]["ts"])<(ts-time_frame):
            break
        if key in msg_from_hive_hist[hive]["values"][i].keys():
            result+=msg_from_hive_hist[hive]["values"][i][key]
            ns+=1
            #print("i="+str(i)+" "+json.dumps(msg_from_hive_hist[hive]["values"][i]["ts"])+" "+json.dumps(msg_from_hive_hist[1]["values"][i][key]))
    #print("key "+key+" ns "+str(ns)+" r "+str(result))
    if(ns>0):
        return round(result/ns,2)
    else:
        return


def check_avgs(hive):
    '''
    avg_alerts={}
    if hive==1:
        device=device1
    elif hive==2:
        device=device2
    elif hive==3:
        device=device3
    else:
        print("wrong hive number")
        return
    if(value_TB[hive]>0):
        for notif_key in notif_TB_keys.keys():
            avg_tot=0
            navg=0
            for i in range(1,4):
                #print("+++++hive"+str(i)+" value_TB"+str(value_TB[i])+" avkey "+notif_key+" key "+notif_TB_keys[notif_key]+"+++++")
                #print(json.dumps(msg_to_TB_hist[i]["values"][1][notif_TB_keys[notif_key]]))
                #print(value_TB[i] in msg_to_TB_hist[i]["values"]and notif_TB_keys[notif_key] in msg_to_TB_hist[i]["values"][value_TB[i]].keys())
                if value_TB[i] in msg_to_TB_hist[i]["values"] and notif_TB_keys[notif_key] in msg_to_TB_hist[i]["values"][value_TB[i]].keys():
                    #print(json.dumps(msg_to_TB_hist[i]["values"][value_TB[i]]))
                    if isinstance(msg_to_TB_hist[i]["values"][value_TB[i]][notif_TB_keys[notif_key]],Number):
                        navg += 1
                        avg_tot += msg_to_TB_hist[i]["values"][value_TB[i]][notif_TB_keys[notif_key]]
            if navg != 0:
                avg_tot /= navg
            #print("+++ avg"+notif_key+str(avg_tot)+" +++")
            if notif_TB_keys[notif_key] in msg_to_TB_hist[hive]["values"][value_TB[hive]].keys():
                if not isinstance(msg_to_TB_hist[hive]["values"][value_TB[hive]][notif_TB_keys[notif_key]],Number):
                    #avg_alerts.update({notif_key:-1})
                    attributes = {notif_key: -1}
                    #device.send_attributes(attributes)
                    print("anomaly for "+notif_key+" in deviec "+str(i)+" val= -1")
                elif msg_to_TB_hist[hive]["values"][value_TB[hive]] and avg_tot*1.2 < msg_to_TB_hist[hive]["values"][value_TB[hive]][notif_TB_keys[notif_key]]:
                    #avg_alerts.update({notif_key:2})
                    attributes = {notif_key: 2}
                    #device.send_attributes(attributes)
                    print("anomaly for "+notif_key+" in deviec "+str(i)+" val= 2")
                elif msg_to_TB_hist[hive]["values"][value_TB[hive]] and avg_tot*0.8 > msg_to_TB_hist[hive]["values"][value_TB[hive]][notif_TB_keys[notif_key]]:
                    #avg_alerts.update({notif_key:1})
                    attributes = {notif_key: 1}
                    #device.send_attributes(attributes)
                    print("anomaly for "+notif_key+" in deviec "+str(i)+" val= 1")
                else:
                    attributes = {notif_key: 0}
                avg_alerts.update(attributes)
        print("Sending for hive"+str(i)+" "+json.dumps(avg_alerts))
        device.send_message(Message(json.dumps(avg_alerts)))
        '''
    pass

def getLatLng(time_frame,ts,hive):
    lat=0
    nlat=0
    resultlat=0
    lng=0
    nlng=0
    resultlng=0
    for i in range(value_hive[hive]-1,-1,-1):
        if(msg_from_hive_hist[hive]["values"][i]["ts"])<(ts-time_frame):
            break
        if "lat" in msg_from_hive_hist[hive]["values"][i].keys():
            resultlat+=msg_from_hive_hist[hive]["values"][i]["lat"]
            nlat+=1
        if "lng" in msg_from_hive_hist[hive]["values"][i].keys():
            resultlng+=msg_from_hive_hist[hive]["values"][i]["lng"]
            nlng+=1
    if nlat != 0 and nlng != 0:
        return {"lat":resultlat/nlat,"lng":resultlng/nlng}
    else:
        return

def publish_avg(time_frame):
    ts=time.time()
    print(ts)
    global value_TB
    '''
    for i in range (1,4):
    '''
    for i in range (1,4):
        print("\n***** Hive "+str(i)+" *****")
        msg_to_TB_hist[i]["values"][value_TB[i]]={}
        key_ind=0
        msg_to_TB_hist[i]["values"][value_TB[i]]["timestamp"]=str(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"))

        #msg_to_TB_hist[i]["values"][value_TB[i]]["nsamples"]=calculate_ns(time_frame,ts,i)
        calculate_ns(time_frame,ts,i)

        while key_ind < len(values_TB_keys):
            avg=calculate_avg(values_hive_keys[key_ind],time_frame,ts,i)
            if avg != None:
                msg_to_TB_hist[i]["values"][value_TB[i]][values_TB_keys[key_ind]]=avg
                #print("hive"+str(i)+" valuesTB "+str(value_TB[i])+" values_TB_key "+values_TB_keys[key_ind]+" value "+json.dumps(msg_to_TB_hist[i]["values"][value_TB[i]][values_TB_keys[key_ind]]))
            else:
                msg_to_TB_hist[i]["values"][value_TB[i]][values_TB_keys[key_ind]]=""
            key_ind += 1
        if value_TB[i] != 0:
            if i == 1:
                location = getLatLng(time_frame,ts,i)
                check_avgs(i)
                if location != None:
                    msg_to_TB_hist[i]["values"][value_TB[i]].update(location)
                msg_send=msg_to_TB_hist[i]["values"][value_TB[i]]
                #msg_send.update(getHiveNotif(time_frame,ts,i))
                print("DEVICE1 SENDING\n"+json.dumps(msg_send))

                #device1.send_message(Message(json.dumps(clear_hive_att)))

                device1.send_message(Message(json.dumps(msg_send)))
            elif i== 2:
                location = getLatLng(time_frame,ts,i)
                check_avgs(i)
                if location != None:
                    msg_to_TB_hist[i]["values"][value_TB[i]].update(location)
                msg_send=msg_to_TB_hist[i]["values"][value_TB[i]]
                #msg_send.update(getHiveNotif(time_frame,ts,i))
                print("DEVICE2 SENDING\n"+json.dumps(msg_send))

                #device2.send_message(Message(json.dumps(clear_hive_att)))

                device2.send_message(Message(json.dumps(msg_send)))
            elif i== 3:
                location = getLatLng(time_frame,ts,i)
                check_avgs(i)
                if location != None:
                    msg_to_TB_hist[i]["values"][value_TB[i]].update(location)

                msg_to_TB_hist[i]["values"][value_TB[i]]["avX"]=round(random.uniform(-0.2, 0.2),2)
                msg_to_TB_hist[i]["values"][value_TB[i]]["avY"]=round(random.uniform(-0.2, 0.2),2)
                msg_to_TB_hist[i]["values"][value_TB[i]]["avZ"]=round(random.uniform(0.8, 0.92),2)
                msg_send=msg_to_TB_hist[i]["values"][value_TB[i]]
                #msg_send.update(getHiveNotif(time_frame,ts,i))
                print("DEVICE3 SENDING\n"+json.dumps(msg_send))

                #device3.send_message(Message(json.dumps(clear_hive_att)))

                device3.send_message(Message(json.dumps(msg_send)))
        #print()
    #print(json.dumps(msg_to_TB_hist[1]["values"][value_TB[1]]))
    #device1.send_telemetry(msg_to_TB_hist[1]["values"][value_TB[1]])
    print()
    for i in range(1,4):
        value_TB[i]+=1

## RPC
def set_hive_indicator_light(hive,light):
    if light == True:
        light=1
    elif light == False:
        light=0
    print("hive"+str(hive)+" lightIndicator "+str(light))
    hivegt.publish("hive/"+str(hive)+"/setIndicatorLight",light)
    if light == True:
        light_indicator_hive[hive]=1
    elif light == False:
        light_indicator_hive[hive]=0

def set_hive_indicator_weight(hive,weight):
    print("hive"+str(hive)+" weightIndicator "+str(weight))
    payload={"avweight0":0,"avweight1":0,"avweight2":0}
    if weight == "1":
        weight_indicator_hive[int(hive)]=1
        print(payload.keys())
        for key in payload.keys():
            print(key)
            print(json.dumps(msg_to_TB_hist[int(hive)]["values"][value_TB[int(hive)]-1][key]))
            if msg_to_TB_hist[int(hive)]["values"][value_TB[int(hive)]-1][key] !="" and  msg_to_TB_hist[int(hive)]["values"][value_TB[int(hive)]-1][key] > weight_th:
                payload[key]=1
                print("light on")
        hivegt.publish("hive/"+str(hive)+"/setweightIndicator",json.dumps(payload))
        print("hive"+str(hive)+" weightIndicator "+json.dumps(payload))
    elif weight == "0":
        weight_indicator_hive[int(hive)]=0
        hivegt.publish("hive/"+str(hive)+"/setweightIndicator",json.dumps(payload))

def set_hive_sampling_period(hive,period):
    sampling_period_hive[hive]=int(period)
    print("Sampling Period for Hive"+str(hive)+" = "+str(period))
    hivegt.publish("hive/"+str(hive)+"/setSamplingPeriod",period)

def set_gt_sampling_period(period):
    global gatewaySamplingPeriod
    gatewaySamplingPeriod=float(period)
    print("GtPeriod "+str(gatewaySamplingPeriod))

def device_method_listener(device_client):
    while True:
        method_request = device_client.receive_method_request()
        print (
            "\nMethod callback called with:\nmethodName = {method_name}\npayload = {payload}".format(
                method_name=method_request.name,
                payload=method_request.payload
            )
        )
        ##
        if method_request.name == "set_hive_indicator_light":
            try:
                set_hive_indicator_light(method_request.payload["hive"], method_request.payload["var"])
                pass
            except ValueError:
                response_payload = {"Response": "Invalid parameter"}
                response_status = 400
            else:
                response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                response_status = 200
        ##
        elif method_request.name == "set_hive_indicator_weight":
            try:
                set_hive_indicator_weight(method_request.payload["hive"], method_request.payload["var"])
                pass
            except ValueError:
                response_payload = {"Response": "Invalid parameter"}
                response_status = 400
            else:
                response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                response_status = 200
        ##
        elif method_request.name == "set_hive_sampling_period":
            try:
                set_hive_sampling_period(method_request.payload["hive"], method_request.payload["var"])
                pass
            except ValueError:
                response_payload = {"Response": "Invalid parameter"}
                response_status = 400
            else:
                response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                response_status = 200
        ##
        elif method_request.name == "set_gt_sampling_period":
            try:
                set_gt_sampling_period(method_request.payload["var"])
                pass
            except ValueError:
                response_payload = {"Response": "Invalid parameter"}
                response_status = 400
            else:
                response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                response_status = 200

        else:
            response_payload = {"Response": "Direct method {} not defined".format(method_request.name)}
            response_status = 404

        method_response = MethodResponse(method_request.request_id, response_status, payload=response_payload)
        device_client.send_method_response(method_response)
####

## Main initialization and thread
if __name__ == "__main__":
    try:
        # Start a thread to listen
        device_method_thread = threading.Thread(target=device_method_listener, args=(device3,))
        device_method_thread.daemon = True
        device_method_thread.start()
        start_hive_gt()
        #Azure connect
        print("all Connected")
        while True:
            print("\n************************************************************************************************************")
            print("PERIOD DONE -> "+str(datetime.datetime.now()))
            publish_avg(gatewaySamplingPeriod)
            print("NEXT IN -> "+str(gatewaySamplingPeriod))
            print("************************************************************************************************************\n")
            time.sleep(gatewaySamplingPeriod)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    finally:
        hivegt.loop_stop(force=False)
        sys.exit(0)
