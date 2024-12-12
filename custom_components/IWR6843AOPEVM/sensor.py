from __future__ import annotations
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_NAME
from .const import DOMAIN
from .radar_reader import Core

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the radar sensor platform."""
    core = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([RadarSensor(core, config_entry.data[CONF_NAME])], True)

class RadarSensor(SensorEntity):
    """Representation of a radar sensor."""

    def __init__(self, core: Core, name: str) -> None:
        self.core = core
        self._attr_name = name
        self._attr_native_unit_of_measurement = "people"
        self._state = None

    @property
    def native_value(self):
        return self._state

    async def async_update(self):
        self._state = self.core.parseData()
