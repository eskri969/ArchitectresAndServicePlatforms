
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
        temperatureIn=1
        temperatureOut=10
        humidityIn=20
        humidityOut=30
        weight01=0
        weight11=1
        weight21=2
        weight02=0
        weight12=1
        weight22=2
        X=70
        Y=80
        Z=90
        CO2=100
        print("init")
        while True:
            i+=1
            temperatureIn = random.uniform(22, 25)
            temperatureOut = random.uniform(25, 28)
            humidityIn=random.uniform(48, 53)
            humidityOut = random.uniform(38, 43)
            weight0 = random.uniform(0, 5)
            weight1 = random.uniform(0, 5)
            weight2 = random.uniform(0, 5)
            X = random.uniform(-0.2, 0.2)
            Y = random.uniform(-0.2, 0.2)
            Z = random.uniform(0.8, 0.92)
            CO2 = random.uniform(60, 80)
            msg="{\"temperatureIn\":"+str(temperatureIn)+",\"temperatureOut\":"+str(temperatureOut)+",\"humidityIn\":"+str(humidityIn)+",\"humidityOut\":"+str(humidityOut)+",\"weight0\":"+str(weight01)+",\"weight1\":"+str(weight11)+",\"weight2\":"+str(weight21)+",\"X\":"+str(X)+",\"Y\":"+str(Y)+",\"Z\":"+str(Z)+",\"CO2\":"+str(CO2)+"}"
            print("1send"+str(i))
            client.publish(topic_pub1, msg)
            temperatureIn = random.uniform(22, 25)
            temperatureOut = random.uniform(25, 28)
            humidityIn=random.uniform(48, 53)
            humidityOut = random.uniform(38, 43)
            weight01 += random.uniform(0, 0.5)
            weight11 += random.uniform(0, 0.5)
            weight21 += random.uniform(0, 0.5)
            X = random.uniform(-0.2, 0.2)
            Y = random.uniform(-0.2, 0.2)
            Z = random.uniform(0.8, 0.92)
            CO2 = random.uniform(60, 80)
            msg="{\"temperatureIn\":"+str(temperatureIn)+",\"temperatureOut\":"+str(temperatureOut)+",\"humidityIn\":"+str(humidityIn)+",\"humidityOut\":"+str(humidityOut)+",\"weight0\":"+str(weight02)+",\"weight1\":"+str(weight12)+",\"weight2\":"+str(weight22)+",\"X\":"+str(X)+",\"Y\":"+str(Y)+",\"Z\":"+str(Z)+",\"CO2\":"+str(CO2)+"}"
            print("2send"+str(i))
            client.publish(topic_pub2, msg)
            temperatureIn = random.uniform(22, 25)
            temperatureOut = random.uniform(25, 28)
            humidityIn=random.uniform(48, 53)
            humidityOut = random.uniform(38, 43)
            weight02 += random.uniform(0, 0.5)
            weight12 += random.uniform(0, 0.5)
            weight22 += random.uniform(0, 0.5)
            X = random.uniform(-0.2, 0.2)
            Y = random.uniform(-0.2, 0.2)
            Z = random.uniform(0.8, 0.92)
            CO2 = random.uniform(60, 80)
            msg="{\"temperatureIn\":"+str(temperatureIn)+",\"temperatureOut\":"+str(temperatureOut)+",\"humidityIn\":"+str(humidityIn)+",\"humidityOut\":"+str(humidityOut)+",\"weight0\":"+str(weight02)+",\"weight1\":"+str(weight12)+",\"weight2\":"+str(weight22)+",\"X\":"+str(X)+",\"Y\":"+str(Y)+",\"Z\":"+str(Z)+",\"CO2\":"+str(CO2)+"}"
            print("2send"+str(i))
            #client.publish(topic_pub3, msg)
            if weight01 > 4.5:
                weight01 = 0
            if weight11 > 4.5:
                weight11 = 0
            if weight21 > 4.5:
                weight21 = 0
            if weight02 > 4.5:
                weight02 = 0
            if weight12 > 4.5:
                weight12 = 0
            if weight22 > 4.5:
                weight22 = 0
            time.sleep(5)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    finally:
        client.loop_stop(force=False)
        sys.exit(0)
