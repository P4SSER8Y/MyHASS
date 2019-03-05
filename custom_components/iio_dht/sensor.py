from homeassistant.const import DEVICE_CLASS_HUMIDITY, DEVICE_CLASS_TEMPERATURE , TEMP_CELSIUS
from homeassistant.helpers.entity import Entity

from time import sleep

def setup_platform(hass, config, add_devices, discovery_info=None):
    add_devices([DHTHumidity(), DHTTemperature()])

class DHTHumidity(Entity):
    def __init__(self):
        self._state = None
        self.update()

    @property
    def name(self):
        return 'IIO DHT Humidity'

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
        flag = False
        while not flag:
            try:
                with open("/sys/devices/platform/dht11@0/iio:device0/in_humidityrelative_input", "r") as f:
                    self._state = float(f.readline()) / 1000.0
                flag = True
            except:
                sleep(1)

class DHTTemperature(Entity):
    def __init__(self):
        self._state = None
        self.update()

    @property
    def name(self):
        return 'IIO DHT Temperature'

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
        flag = False
        while not flag:
            try:
                with open("/sys/devices/platform/dht11@0/iio:device0/in_temp_input", "r") as f:
                    self._state = float(f.readline()) / 1000.0
                flag = True
            except:
                sleep(1)

