from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from .radar_reader import RadarReader
from .const import DOMAIN, CONF_CLI_DEVICE_PATH, CONF_DATA_DEVICE_PATH
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities,
    discovery_info: DiscoveryInfoType = None
):
    if discovery_info is None:
        return

    cli_device_path = hass.data[DOMAIN][CONF_CLI_DEVICE_PATH]
    data_device_path = hass.data[DOMAIN][CONF_DATA_DEVICE_PATH]

    radar_reader = RadarReader(cli_device_path, data_device_path)
    hass.data[DOMAIN]['radar_reader'] = radar_reader
    async_add_entities([RadarOccupancySensor(radar_reader)], update_before_add=True)

class RadarOccupancySensor(Entity):
    _attr_name = "Room Occupancy"
    _attr_icon = "mdi:account-group"
    _attr_unit_of_measurement = "persons"
    _attr_unique_id = "radar_room_occupancy"

    def __init__(self, radar_reader: RadarReader):
        self.radar_reader = radar_reader
        self._state = None

    @property
    def state(self):
        return self._state

    def update(self):
        self._state = self.radar_reader.get_people_count()
