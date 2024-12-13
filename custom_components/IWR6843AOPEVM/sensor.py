from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from .const import DOMAIN, LOGGER

async def async_setup_entry(hass, config_entry, async_add_entities):
    core = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = RadarDataUpdateCoordinator(hass, core)
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([RadarSensor(coordinator, config_entry.data["name"])])

class RadarDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, core):
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name="Radar Sensor Data",
            update_interval=timedelta(seconds=1),
        )
        self.core = core

    async def _async_update_data(self):
        try:
            return self.core.parseData()
        except Exception as exception:
            LOGGER.error("Error updating radar data: %s", exception)
            return -1

class RadarSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, name):
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_native_unit_of_measurement = "people"
        self._last_valid_value = None

    @property
    def native_value(self):
        return self._last_valid_value

    async def async_update(self):
        new_value = await self.coordinator._async_update_data()
        if new_value > -1:
            self._last_valid_value = new_value
