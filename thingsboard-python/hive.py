
#https://pypi.org/project/paho-mqtt/
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time
import sys
import random


# Don't forget to change the variables for the MQTT broker!
topic_pub1="hive/1/telemetry"
topic_pub2="hive/2/telemetry"
topic_pub3="hive/3/telemetry"

mqtt_broker_ip = "127.0.0.1"
client = mqtt.Client(protocol=mqtt.MQTTv311, transport="tcp")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe(topic_pub)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("NEW MSG -> "+msg.topic+" "+str(msg.payload.decode('UTF-8')))

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print ("Unexpected MQTT disconnection. Will auto-reconnect")

if __name__ == "__main__":
    try:
        client.connect(mqtt_broker_ip, 1883, 60)
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        client.loop_start()
        i=0
        temperatureIn=0
        temperatureOut=0
        humidityIn=0
        humidityOut=0
        weigth0=0
        weigth1=0
        weigth2=0
        X=0
        Y=0
        Z=0
        C02=0
        print("init")
        while True:
            i+=1
            temperatureIn+=1
            temperatureOut+=1
            humidityIn+=1
            humidityOut+=1
            weigth0+=1
            weigth1+=1
            weigth2+=1
            X+=1
            Y+=1
            Z+=1
            C02+=1
            msg="{\"temperatureIn\":"+str(temperatureIn)+",\"temperatureOut\":"+str(temperatureIn)+",\"humidityIn\":"+str(temperatureIn)+",\"humidityOut\":"+str(temperatureIn)+",\"weigth0\":"+str(temperatureIn)+",\"weigth1\":"+str(temperatureIn)+",\"weigth2\":"+str(temperatureIn)+",\"X\":"+str(temperatureIn)+",\"Y\":"+str(temperatureIn)+",\"Z\":"+str(temperatureIn)+",\"C02\":"+str(temperatureIn)+"}"
            print("send"+str(i))
            client.publish(topic_pub1, msg)
            client.publish(topic_pub2, msg)
            client.publish(topic_pub3, msg)
            time.sleep(15)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    finally:
        client.loop_stop(force=False)
        sys.exit(0)
