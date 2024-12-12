from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from .radar_reader import RadarReader
from .const import DOMAIN, CONF_DEVICE_PATH

import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass: HomeAssistant, config: ConfigType, async_add_entities, discovery_info: DiscoveryInfoType = None):
    if discovery_info is None:
        return

    device_path = hass.data[DOMAIN][CONF_DEVICE_PATH]
    radar_reader = RadarReader(device_path)
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
        data = self.radar_reader.read_data()
        if data is not None:
            self._state = data
