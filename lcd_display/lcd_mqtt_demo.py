import paho.mqtt.client as mqtt
import json
import usblcd
from datetime import datetime

display = usblcd.UsbLcd('/dev/cu.usbmodem26231', 57600)

display.clear()


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("demo/devices/arduino")
    display.clear()
    display.write("Connected to MQTT OK")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    sensor_data = json.loads(msg.payload)
    #print sensor_data['bme280']
    print sensor_data

    # sensor_temperature_c = float(sensor_data['bme280']['temperature'])
    # sensor_pressure_mb   = float(sensor_data['bme280']['pressure']) / 100.0
    # sensor_humidity_pc   = float(sensor_data['bme280']['humidity'])
    sensor_temperature_c = float(sensor_data['temperature'])
    sensor_pressure_mb   = float(sensor_data['pressure'])
    sensor_humidity_pc   = float(sensor_data['humidity'])

    display_str = '{:<8} {:2.1f}C  {:4.1f}mb {:.1f}%RH'.format(
        datetime.now().strftime('%H:%M:%S'), sensor_temperature_c, sensor_pressure_mb, sensor_humidity_pc)
    print display_str, len(display_str)
    display.clear()
    display.write(display_str)

display.write("Connecting...")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.0.101", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
