import logging
import os

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.switch import SwitchDevice, PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME

REQUIREMENTS = []
DEFAULT_NAME = 'gpio_switch'
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required('port'): int,
    vol.Optional('inverted', default=False): cv.boolean,
})
    
_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    name = config.get(CONF_NAME)
    port = config.get('port')
    inverted = config.get('inverted')
    add_entities([Switch(name, port, inverted)])


class Switch(SwitchDevice):
    def __init__(self, name, port, is_inverted):
        self._state = False
        self._name = name
        self._port = port
        if is_inverted:
            self._on = '0'
            self._off = '1'
        else:
            self._on = '1'
            self._off = '0'
        self.open_port()
        self.turn_off()

    def open_port(self):
        if not os.path.exists('/sys/class/gpio/gpio{}'.format(self._port)):
            with open('/sys/class/gpio/export', 'w') as f:
                f.write('{}'.format(self._port))
        with open('/sys/class/gpio/gpio{}/direction'.format(self._port), 'w') as f:
            f.write('out')

    def check_port(self):
        value = None
        if os.path.exists('/sys/class/gpio/gpio{}/value'.format(self._port)):
            try:
                with open('/sys/class/gpio/gpio{}/value'.format(self._port), 'r') as f:
                    value = f.read()
                    value = value[0] == self._on
            except:
                pass
        return value 
    
    def turn_on(self, **kwargs):
        value = self.check_port()
        if value is None:
            self.open_port()
        if value:
            return 
        with open('/sys/class/gpio/gpio{}/value'.format(self._port), 'w') as f:
            f.write(self._on)
        self._state = True
    
    def turn_off(self, **kwargs):
        value = self.check_port()
        if value is None:
            self.open_port()
        if not value:
            return
        with open('/sys/class/gpio/gpio{}/value'.format(self._port), 'w') as f:
            f.write(self._off)
        self._state = False

    @property
    def is_on(self):
        return self.check_port() == True

    @property
    def assumed_state(self):
        return self._state

    @property
    def unique_id(self):
        return 'troy_switch_direct_gpio_{}'.format(self._port)

    @property
    def name(self):
        return self._name

