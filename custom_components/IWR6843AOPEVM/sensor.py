from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_NAME
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from datetime import timedelta
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the radar sensor platform."""
    core = hass.data[DOMAIN][config_entry.entry_id]

    # Set up a data update coordinator for periodic updates
    coordinator = RadarDataUpdateCoordinator(hass, core)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([RadarSensor(coordinator, config_entry.data[CONF_NAME])])

class RadarDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching radar data periodically."""

    def __init__(self, hass, core):
        super().__init__(
            hass,
            logger=hass.helpers.logger,
            name="Radar Sensor Data",
            update_interval=timedelta(seconds=0.2),
        )
        self.core = core

    async def _async_update_data(self):
        return self.core.parseData()

class RadarSensor(CoordinatorEntity, SensorEntity):
    """Representation of a radar sensor."""

    def __init__(self, coordinator, name):
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_native_unit_of_measurement = "people"

    @property
    def native_value(self):
        return self.coordinator.data
