
#https://pypi.org/project/paho-mqtt/
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time
import sys
import random


# Don't forget to change the variables for the MQTT broker!
topic_pub='v1/devices/me/telemetry'
mqtt_broker_ip = "srv-iot.diatel.upm.es"
client = mqtt.Client(protocol=mqtt.MQTTv311, transport="tcp")

client2 = mqtt.Client(protocol=mqtt.MQTTv311, transport="tcp")
forward=False

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(topic_pub)
    client.subscribe('v1/devices/me/attributes')
    client.subscribe('v1/devices/me/attributes/response/+')
    client.subscribe('v1/devices/me/rpc/request/+')

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("NEW MSG -> "+msg.topic+" "+str(msg.payload.decode('UTF-8')))
    global forward
    forward=True

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print ("Unexpected MQTT disconnection. Will auto-reconnect")

if __name__ == "__main__":
    try:
        client.username_pw_set("IU8rjHe8MCyu0A0oqk7S", password=None)
        client.connect(mqtt_broker_ip, 1883, 60)
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        client.loop_start()

        client2.connect("127.0.0.1", 1883, 60)
        client2.subscribe("server", 0)
        client2.on_message = on_message
        client2.loop_start()
        for i in range(4):
            x = 0
            print(x)
            msg = "{\"temperature\":"+str(x)+"}"
            client.publish(topic_pub, msg)
            time.sleep(1)
        while True:
            for i in range(5):
                x = random.randrange(0, 50)
                print(x)
                msg = "{\"temperature\":"+str(x)+"}"
                client.publish(topic_pub, msg)
                if forward:
                    time.sleep(5)
                    x = 200
                    print(x)
                    msg = "{\"temperature\":"+str(x)+"}"
                    client.publish(topic_pub, msg)
                    forward=False
                time.sleep(5)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    finally:
        client.loop_stop(force=False)
        sys.exit(0)
'''
from __future__ import division
import paho.mqtt.client as mqtt
import random
import time
import threading

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc, *extra_params):
   print('Connected with result code ' + str(rc))
   # Subscribing in on_connect() means that if we lose the connection and
   # reconnect then subscriptions will be renewed
   client.subscribe('tb/mqtt-integration-tutorial/sensors/+/rx/twoway')
   client.subscribe('tb/mqtt-integration-tutorial/sensors/+/rx')


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
  print ('Incoming message\nTopic: ' + msg.topic + '\nMessage: ' + str(msg.payload))
  if msg.topic.startswith('tb/mqtt-integration-tutorial/sensors/SN-001/rx/twoway'):
       print ('This is a Two-way RPC call. Going to reply now!')
       responseMsg = "{\"rpcReceived\":\"OK\"}"
       print ('Sending a response message: ' + responseMsg)
       client.publish('tb/mqtt-integration-tutorial/sensors/SN-001/rx/response', responseMsg)
       print ('Sent a response message: ' + responseMsg)
       return
  if msg.topic.startswith( 'tb/mqtt-integration-tutorial/sensors/+/rx'):
       print ('This is a One-way RPC call. RequestID: ')
       return

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect('srv-iot.diatel.upm.es', 1883)

client.loop_forever()
'''
