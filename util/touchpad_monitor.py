#!/usr/bin/env python3

import sys
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

import paho.mqtt.publish as publish
import wiringpi
from time import sleep
from yaml import load
import os

script_file = os.path.realpath(__file__)
yaml_file = os.path.join(os.path.dirname(script_file), '../secrets.yaml')

data = None
logging.info('parse secrets.yaml')
with open(yaml_file, 'r') as f:
    data = load(f)

MQTT_AUTH = {
    'username': data['mqtt_username'],
    'password': data['mqtt_password']
}

if __name__ == "__main__":
    port = data['gpio_touchpad_port']
    logging.info('setup GPIO%02d as input port', port)
    wiringpi.wiringPiSetupSys()
    if not os.path.exists('/sys/class/gpio/gpio{:d}'.format(port)):
        logging.warning('setup GPIO with wiringpi failed')
        with open('/sys/class/gpio/export', 'w') as f:
            f.write('{:d}\n'.format(port))
    wiringpi.pinMode(port, wiringpi.INPUT)

    logging.info('enter polling')
    while True:
        if wiringpi.digitalRead(port) == wiringpi.HIGH:
            logging.info('detect rising edge')
            publish.single('hass/dorm/desk/lamp/toggle', 
                hostname=data['mqtt_broker'],
                port=data['mqtt_port'],
                auth=MQTT_AUTH)
            sleep(0.5)
            while wiringpi.digitalRead(port) == wiringpi.HIGH:
                sleep(0.1)
            logging.info('detect falling edge')
        sleep(0.1)

