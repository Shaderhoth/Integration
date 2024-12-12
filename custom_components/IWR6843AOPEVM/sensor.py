from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .radar_reader import RadarReader
from .const import DOMAIN, CONF_DEVICE_PATH

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    device_path = entry.data[CONF_DEVICE_PATH]
    radar_reader = RadarReader(device_path)
    async_add_entities([RadarOccupancySensor(radar_reader)], True)

class RadarOccupancySensor(SensorEntity):
    _attr_native_unit_of_measurement = "persons"
    _attr_icon = "mdi:account-group"
    _attr_name = "Room Occupancy"

    def __init__(self, radar_reader: RadarReader):
        self.radar_reader = radar_reader
        self._attr_native_value = None

    def update(self):
        data = self.radar_reader.read_data()
        if data is not None:
            self._attr_native_value = data
