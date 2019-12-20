#https://pypi.org/project/paho-mqtt/
import paho.mqtt.client as mqtt

# Don't forget to change the variables for the MQTT broker!
mqtt_topic = "test"
mqtt_broker_ip = "192.168.0.128"
client = mqtt.Client()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("$SYS/#")
    client.subscribe(mqtt_topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("NEW MSG"+msg.topic+" "+str(msg.payload.decode('UTF-8')))
    if(str(msg.payload.decode('UTF-8'))=="Button pressed!"):
        pass
        #client.publish("test", "python_received", qos=0, retain=False)


if __name__ == "__main__":
    try:
        client.connect(mqtt_broker_ip, 1883, 60)
        client.on_connect = on_connect
        client.on_message = on_message
        mqttc.loop_start()
        while True:
            pass
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    finally:
        loop_stop(force=False)
        sys.exit(0)
