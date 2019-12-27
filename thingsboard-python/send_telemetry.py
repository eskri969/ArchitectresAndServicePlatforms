import logging
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
import time
logging.basicConfig(level=logging.DEBUG)

telemetry = {"luminosity": 1.0}
attributes = {"latitude": 30.0, "location": "indoor"}

client = TBDeviceMqttClient("srv-iot.diatel.upm.es", "pu0fhys82xIHTxsbqalR")
client.connect()
# Sending data in async way
client.send_attributes(attributes)
client.send_telemetry(telemetry)

# Waiting for data to be delivered
result = client.send_attributes(attributes)
result.get()
print("Attribute update sent: " + str(result.rc() == TBPublishInfo.TB_ERR_SUCCESS))
result = client.send_attributes(attributes)
result.get()
print("Telemetry update sent: " + str(result.rc() == TBPublishInfo.TB_ERR_SUCCESS))
client.disconnect()
