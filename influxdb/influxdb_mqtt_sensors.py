import paho.mqtt.client
import json
from influxdb import InfluxDBClient
from datetime import datetime
import argparse
import time

import logger

MQTT_IP='127.0.0.1'
MQTT_PORT=1883
MQTT_TIMEOUT=60
INFLUX_IP='127.0.0.1'
INFLUX_PORT=8086
INFLUX_DB='mydb'
DOWNSAMPLE_RATIO=12

LOCAL_ALTITUDE = 83.9

def sea_level_pressure(atm_pressure, altitude):
    return atm_pressure / pow(1.0 - (altitude / 44330.0), 5.255)

class SensorSamples(object):

    def __init__(self, id):
        self.id = id
        self.samples = {}

    def add_sample(self, field, value):

        if field not in self.samples:
            self.samples[field] = []

        self.samples[field].append(value)

    def max_samples(self):
        return max((len(samples) for samples in self.samples.values()))

    def clear(self):
        for field in self.samples:
            self.samples[field][:] = []

    def sample_means(self):
        for field in self.samples:
            if len(self.samples[field]):
                yield field, sum(self.samples[field]) / len(self.samples[field])

class SensorDbLogger(object):
    '''
    Test class to log sensor data received via MQTT to a simple database
    '''

    def __init__(self, args):

        # Initialise sample arrays and update time
        self.sensor_samples = {}
        self.downsample = args.downsample

        # Get the logger instance
        self.logger = logger.get_logger()

        self.logger.info("Sensor database logger starting up")

        # Connect to the database
        self.logger.info("Connecting to influxDB database %s at host %s port %d",
            args.influx_db, args.influx_ip, args.influx_port)
        self.influx_client = InfluxDBClient(host=args.influx_ip, port=args.influx_port,
            database=args.influx_db)

        # Create an MQTT client instance, register connect and message callbacks and connect
        self.mqtt_client = paho.mqtt.client.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        self.logger.info('Connecting to MQTT server at address %s:%d', args.mqtt_ip, args.mqtt_port)
        self.mqtt_client.connect(args.mqtt_ip, args.mqtt_port, args.mqtt_timeout)

    def run(self):

        # Run the MQTT client event loop
        self.mqtt_client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        '''
        Callback for when the client receives a CONNACK response from the server.
        '''
        self.logger.info('MQTT client connected with result code %d', rc)

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe('demo/devices/+')

    def on_message(self, client, userdata, msg):
        '''
        Callback for when a PUBLISH message is received from the server.
        '''
        self.logger.debug('Got message: %s %s', msg.topic, msg.payload)

        sensor_id = msg.topic.split('/')[-1]
        sensor_data = json.loads(msg.payload)

        if sensor_id not in self.sensor_samples:
            self.sensor_samples[sensor_id] = SensorSamples(sensor_id)

        for field, value in sensor_data.iteritems():

	    if field == 'pressure':
		value = sea_level_pressure(float(value), LOCAL_ALTITUDE)

            self.sensor_samples[sensor_id].add_sample(field, float(value))

        if self.sensor_samples[sensor_id].max_samples() >= self.downsample:

            data_points = [
                {
                    'measurement': sensor_id,
                    'fields': {}
                }
            ]

            for field, mean_val in self.sensor_samples[sensor_id].sample_means():
                self.logger.debug("Sensor id {} field {} mean {}".format(
                    sensor_id, field, mean_val
                ))
                data_points[0]['fields'][field] = mean_val

            self.logger.debug("Doing update: {}".format(data_points))
            self.influx_client.write_points(data_points)
            self.sensor_samples[sensor_id].clear()


def parse_args():
    '''
    Parses command line arguments to pass to main application class.

    The parsed arguments are returned in a Namespace object which can be accessed by the application class as atributes
    '''

    parser = argparse.ArgumentParser(description='MQTT sensor database logger demo')

    parser.add_argument('--mqtt_ip', action='store', dest='mqtt_ip', default=MQTT_IP,
                        help='Set the IP address of the MQTT server to connect to (default={})'.format(MQTT_IP))
    parser.add_argument('--mqtt_port', action='store', dest='mqtt_port', type=int, default=MQTT_PORT,
                        help='Set the IP address of the MQTT server to connect to (default={})'.format(MQTT_PORT))
    parser.add_argument('-mqtt_timeout', action='store', dest='mqtt_timeout', type=int, default=MQTT_TIMEOUT,
                        help='Set the timeout (in secs) for connecting to the MQTT server (default={})'.format(MQTT_TIMEOUT))
    parser.add_argument('--influx_ip', action='store', dest='influx_ip', default=INFLUX_IP,
                        help='Set the IP address of the influxDB database to connect to (default={})'.format(INFLUX_IP))
    parser.add_argument('--influx_port', action='store', dest='influx_port', type=int, default=INFLUX_PORT,
                        help='Set the IP address of the influxDB server to connect to (default={})'.format(INFLUX_PORT))
    parser.add_argument('--influx_db', action='store', dest='influx_db', default=INFLUX_DB,
                        help='Set the name of the influxDB database to use (default={})'.format(INFLUX_DB))
    parser.add_argument(
        '--downsample', action='store', dest='downsample', type=int,
        default=DOWNSAMPLE_RATIO,
        help='Sets the downsample ratio for updates to the database (default={})'.format(DOWNSAMPLE_RATIO)
    )
    parser.add_argument('--logging', action='store', default='info',
                        choices=['debug', 'info', 'warning', 'error', 'none'],
                        help='Set the logger level')

    args = parser.parse_args()

    return args

def main():

    # Parse the ocmmand line arguments
    args = parse_args()

    # Set up the message logger
    logger.setup_logger('db_mqtt_demo', args.logging)

    # Instantiate the logger and run
    sdl = SensorDbLogger(args)
    sdl.run()

if __name__ == '__main__':

    main()
