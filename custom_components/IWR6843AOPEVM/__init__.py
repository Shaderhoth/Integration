
import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers import config_validation as cv
from .const import (
    DOMAIN,
    CONF_DATA_DEVICE_PATH,
    DEFAULT_DATA_DEVICE_PATH
)
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config):
    if DOMAIN not in config:
        return True

    data_device_path = config[DOMAIN].get(CONF_DATA_DEVICE_PATH, DEFAULT_DATA_DEVICE_PATH)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][CONF_DATA_DEVICE_PATH] = data_device_path

    from .radar_reader import RadarReader

    radar_reader = RadarReader(data_device_path)
    hass.data[DOMAIN]['radar_reader'] = radar_reader

    async def handle_send_command(call):
        command = call.data.get('command')
        radar_reader = hass.data[DOMAIN].get('radar_reader')
        if radar_reader:
            radar_reader.send_command(command)
            _LOGGER.info(f"Sent command: {command}")
        else:
            _LOGGER.error("RadarReader not initialized")

    hass.services.async_register(
        DOMAIN,
        'send_command',
        handle_send_command,
        schema=vol.Schema({
            vol.Required('command'): cv.string
        })
    )

    # Load the sensor platform
    hass.async_create_task(
        async_load_platform(hass, "sensor", DOMAIN, {}, config)
    )

    return True