#!/usr/bin/env python3
import logging
_LOGGER = logging.getLogger(__name__)

from homeassistant.helpers.entity import Entity
from homeassistant.const import DEVICE_CLASS_ILLUMINANCE 
import smbus
import math

REQUIREMENTS = ['smbus']

bus = smbus.SMBus(1)
base_addr = 0x4a

def setup_platform(hass, config, add_devices, discovery_info=None):
    add_devices([MAX44009()])

def read_light_value(addr0=0):
    addr = base_addr | addr0
    high = bus.read_byte_data(addr, 0x03)
    low = bus.read_byte_data(addr, 0x04)
    exponent = high >> 4
    mantissa = (high << 4) + (low & 0x0F)
    value = (2 ** exponent) * mantissa * 0.045
    return value

class MAX44009(Entity):
    def __init__(self, addr0=0):
        self._addr = base_addr | addr0
        self._state = None

    @property
    def name(self):
        return 'MAX44009_0x{:02X}'.format(self._addr)

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return 'lx'

    @property
    def device_class(self):
        return DEVICE_CLASS_ILLUMINANCE

    def update(self):
	# ceil to 0.05n lx
        self._state = "{:0.2f}".format(math.ceil((read_light_value(self._addr) + 0.001) * 20) / 20)

if __name__ == "__main__":
    print(read_light_value())

