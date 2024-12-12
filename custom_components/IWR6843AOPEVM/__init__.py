from homeassistant.helpers.discovery import load_platform
from homeassistant.const import CONF_DEVICE_PATH
from .const import DOMAIN, DEFAULT_DEVICE_PATH

async def async_setup(hass, config):
    if DOMAIN not in config:
        return True

    device_path = config[DOMAIN].get(CONF_DEVICE_PATH, DEFAULT_DEVICE_PATH)

    hass.data[DOMAIN] = {
        CONF_DEVICE_PATH: device_path
    }

    # Load the sensor platform
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform("sensor", DOMAIN, {}, config)
    )

    return True
