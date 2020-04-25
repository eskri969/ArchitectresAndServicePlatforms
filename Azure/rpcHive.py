'''
HIVE LIGHT OFF      python rpcHive.py set_hive_indicator_light  {1,2,3} 0
HIVE LIGHT ON       python rpcHive.py set_hive_indicator_light  {1,2,3} 1
HIVE WEIGHT OFF     python rpcHive.py set_hive_indicator_weight {1,2,3} 0
HIVE WEIGHT ON      python rpcHive.py set_hive_indicator_weight {1,2,3} 1
HIVE PERIOD         python rpcHive.py set_hive_sampling_period  {1,2,3} {time}
GT   PERIOD         python rpcHive.py set_gt_sampling_period    {time}
'''

import sys
# pylint: disable=E0611

from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod, CloudToDeviceMethodResult

from builtins import input

# The service connection string to authenticate with your IoT hub.
# Using the Azure CLI:
# az iot hub show-connection-string --hub-name {your iot hub name} --policy-name service
CONNECTION_STRING = "HostName=IoTHubCloud.azure-devices.net;SharedAccessKeyName=service;SharedAccessKey=f5HUoOeEsgkZ5jmeSqJ6WDsobiMDXR+U5C3srerpYLI="
DEVICE_ID = "MyDevice3"

# Details of the direct method to call.
METHOD_NAME = sys.argv[1]
if METHOD_NAME == "set_gt_sampling_period":
    PARAM = sys.argv[2]
    METHOD_PAYLOAD = {"var":PARAM}
else:
    HIVE = sys.argv[2]
    PARAM = sys.argv[3]
    METHOD_PAYLOAD = {"hive":HIVE,"var":PARAM}

def iothub_devicemethod_sample_run():
    try:
        # Create IoTHubRegistryManager
        registry_manager = IoTHubRegistryManager(CONNECTION_STRING)

        # Call the direct method.
        deviceMethod = CloudToDeviceMethod(method_name=METHOD_NAME, payload=METHOD_PAYLOAD)
        response = registry_manager.invoke_device_method(DEVICE_ID, deviceMethod)

        print ( "" )
        print ( sys.argv )
        print ( "Device Method called" )
        print ( "Device Method name       : {0}".format(METHOD_NAME) )
        print ( "Device Method payload    : {0}".format(METHOD_PAYLOAD) )
        print ( "" )
        print ( "Response status          : {0}".format(response.status) )
        print ( "Response payload         : {0}".format(response.payload) )

        input("Press Enter to continue...\n")

    except Exception as ex:
        print ( "" )
        print ( "Unexpected error {0}".format(ex) )
        return
    except KeyboardInterrupt:
        print ( "" )
        print ( "IoTHubDeviceMethod sample stopped" )

if __name__ == '__main__':
    print ( "IoT Hub Python quickstart #2..." )
    print ( "    Connection string = {0}".format(CONNECTION_STRING) )
    print ( "    Device ID         = {0}".format(DEVICE_ID) )

    iothub_devicemethod_sample_run()
