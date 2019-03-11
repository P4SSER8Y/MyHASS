import logging
_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = []
REQUIREMENTS = ['requests']
DOMAIN = 'bark'

from requests import get

def setup(hass, config):
    cfg = config.get(DOMAIN)
    url = cfg.get("url", None)
    hass.services.register(DOMAIN, 'bark', main_wrapper(url))
    return True
    
def main_wrapper(default_url):
    def main(call):
        if call.data.get("url", None):
            url = call.data.get("url")
        else:
            url = default_url
        if not url:
            _LOGGER.error("No URL found")
            return
        if not call.data.get("message", None):
            _LOGGER.error("No message found")
            return
        if call.data.get("title", None):
            ret = get('/'.join([url, call.data.get("title"), call.data.get("message")]))
        else:
            ret = get('/'.join([url, call.data.get("message")]))
    return main

