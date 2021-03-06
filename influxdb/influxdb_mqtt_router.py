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

class RouterDbLogger(object):
    '''
    Test class to log sensor data received via MQTT to a simple database
    '''

    def __init__(self, args):

	self.field_types = {
	    'sys_uptime': int,
	    'us_atten': float,
            'update_time': int,
            'ds_speed': int,
            'ds_atten': float,
            'wan_boot_time': int,
            'ds_margin': float,
            'us_margin': float,
            'wan_uptime': int,
            'sys_boot_time': int,
            'us_speed': int,
        }

        # Get the logger instance
        self.logger = logger.get_logger()
        self.logger.info("Router database logger starting up")

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
        client.subscribe('router/stats')

    def on_message(self, client, userdata, msg):
        '''
        Callback for when a PUBLISH message is received from the server.
        '''
        self.logger.debug('Got message: %s %s', msg.topic, msg.payload)

        router_stats = json.loads(msg.payload)

	data_points = [
            {
                'measurement': 'router',
                'fields': {}
            }
        ]

        for field, val in router_stats.iteritems():

	    if field in self.field_types:
		val = self.field_types[field](val)

            self.logger.debug("Router stats field {} value {} type {}".format(
                field, val, type(val)
            ))
            data_points[0]['fields'][field] = val

        self.logger.debug("Doing update: {}".format(data_points))
        self.influx_client.write_points(data_points)


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
    rdl = RouterDbLogger(args)
    rdl.run()

if __name__ == '__main__':

    main()
