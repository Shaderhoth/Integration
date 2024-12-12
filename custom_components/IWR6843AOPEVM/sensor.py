from homeassistant.helpers.entity import Entity
from .radar_reader import RadarReader
from .const import DOMAIN, CONF_DEVICE_PATH

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    if discovery_info is None:
        return

    device_path = hass.data[DOMAIN][CONF_DEVICE_PATH]
    radar_reader = RadarReader(device_path)
    async_add_entities([RadarOccupancySensor(radar_reader)], True)

class RadarOccupancySensor(Entity):
    _attr_name = "Room Occupancy"
    _attr_icon = "mdi:account-group"

    def __init__(self, radar_reader):
        self.radar_reader = radar_reader
        self._state = None

    @property
    def state(self):
        return self._state

    def update(self):
        data = self.radar_reader.read_data()
        if data is not None:
            self._state = data
