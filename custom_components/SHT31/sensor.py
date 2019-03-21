#!/usr/bin/env python3
import logging
LOGGER = logging.getLogger(__name__)

from homeassistant.helpers.entity import Entity
from homeassistant.const import DEVICE_CLASS_HUMIDITY, DEVICE_CLASS_TEMPERATURE, TEMP_CELSIUS
import smbus
import math
from time import sleep, time
from datetime import timedelta

REQUIREMENTS = ['smbus']
SCAN_INTERVAL = timedelta(seconds=60)

bus = smbus.SMBus(1)
base_addr = 0x44

def setup_platform(hass, config, add_devices, discovery_info=None):
    addr0 = config.get('addr0', 0)
    SCAN_INTERVAL = config.get('scan_interval', timedelta(seconds=60))
    LOGGER.info("hello world")
    sensor = SHT31_Client(base_addr | addr0, SCAN_INTERVAL)
    sensor_list = []
    if config.get('sensors', None):
        if config.get('sensors').get('temperature'):
            sensor_list.append(SHT31_Temperature(sensor, config.get('sensors').get('temperature').get('name', None)))
        if config.get('sensors').get('humidity'):
            sensor_list.append(SHT31_Humidity(sensor, config.get('sensors').get('humidity').get('name', None)))
    else:
        sensor_list = [SHT31_Temperature(sensor), SHT31_Humidity(sensor)]
    add_devices(sensor_list)


class SHT31_Client():
    def __init__(self, addr, update_interval=timedelta(seconds=60)):
        self._addr = addr
        self._temperature = None
        self._humidity = None
        self._interval = update_interval.total_seconds()
        self._last_update_time = 0
        self.update()

    @property
    def temperature(self):
        return self._temperature

    @property
    def humidity(self):
        return self._humidity

    def reset(self):
        bus.write_byte(0x00, 0x06)

    def update(self):
        if self._last_update_time + self._interval > time():
            return
        self._last_update_time = time()
        LOGGER.info("querying")
        bus.write_i2c_block_data(self._addr, 0x2C, [0x06])
        sleep(0.5)
        LOGGER.info("retrieving data")
        data = bus.read_i2c_block_data(self._addr, 0x00, 6)
        raw_temperature = (data[0] << 8) | data[1]
        raw_humidity = (data[3] << 8) | data[4]
        self._temperature = -45.0 + 175.0 * raw_temperature / 65535.0
        self._humidity = 100.0 * raw_humidity / 65535.0
        

class SHT31_Temperature(Entity):
    def __init__(self, sensor, name=None):
        self._sensor = sensor
        self._state = None
        if name:
            self._name = name
        else:
            self._name = 'SHT31_Temperature_0x{:02X}'.format(self._sensor._addr)
        self.update()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return TEMP_CELSIUS

    @property
    def device_class(self):
        return DEVICE_CLASS_TEMPERATURE

    def update(self):
        self._sensor.update()
        self._state = "{:0.1f}".format(self._sensor.temperature)


class SHT31_Humidity(Entity):
    def __init__(self, sensor, name=None):
        self._sensor = sensor
        self._state = None
        if name:
            self._name = name
        else:
            self._name = 'SHT31_Humidity_0x{:02X}'.format(self._sensor._addr)
        self.update()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return '%'

    @property
    def device_class(self):
        return DEVICE_CLASS_HUMIDITY

    def update(self):
        self._sensor.update()
        self._state = "{:0.0f}".format(self._sensor.humidity)


if __name__ == "__main__":
    LOGGER.setLevel(logging.INFO)
    sensor = SHT31_Client(base_addr)
    print("Temperature: {:0.2f}\nHumidity: {:0.2f}%".format(sensor.temperature, sensor.humidity))


