from homeassistant.const import CONF_DEVICE_PATH
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN, DEFAULT_DEVICE_PATH

async def async_setup(hass: HomeAssistant, config: ConfigType):
    if DOMAIN not in config:
        return True

    device_path = config[DOMAIN].get(CONF_DEVICE_PATH, DEFAULT_DEVICE_PATH)
    hass.data[DOMAIN] = {
        CONF_DEVICE_PATH: device_path
    }

    hass.async_create_task(
        async_load_platform(hass, "sensor", DOMAIN, {}, config)
    )

    return True
