import voluptuous as vol
from .const import (
    DOMAIN,
    CONF_CLI_DEVICE_PATH,
    CONF_DATA_DEVICE_PATH,
    DEFAULT_CLI_DEVICE_PATH,
    DEFAULT_DATA_DEVICE_PATH
)
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
import logging
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType):
    if DOMAIN not in config:
        return True

    cli_device_path = config[DOMAIN].get(CONF_CLI_DEVICE_PATH, DEFAULT_CLI_DEVICE_PATH)
    data_device_path = config[DOMAIN].get(CONF_DATA_DEVICE_PATH, DEFAULT_DATA_DEVICE_PATH)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][CONF_CLI_DEVICE_PATH] = cli_device_path
    hass.data[DOMAIN][CONF_DATA_DEVICE_PATH] = data_device_path

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

    from .radar_reader import RadarReader

    radar_reader = RadarReader(cli_device_path, data_device_path)
    hass.data[DOMAIN]['radar_reader'] = radar_reader

    hass.async_create_task(
        async_load_platform(hass, "sensor", DOMAIN, {}, config)
    )

    return True
