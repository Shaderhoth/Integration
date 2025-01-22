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
        self.last_data = None
        self.zerocount = 0
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name="Radar Sensor Data",
            update_interval=timedelta(seconds=1),
        )
        self.core = core

    async def _async_update_data(self):
        try:
            data = self.core.parseData()            
            if data > -1 and data < 100:
                self.zerocount = 0
                self.last_data = data
                return self.last_data
            else:
                self.zerocount += 1
                if self.zerocount > 2:
                    self.last_data = 0
                return self.last_data
        except Exception as exception:
            LOGGER.error("Error updating radar data: %s", exception)
            return self.last_data

class RadarSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, name):
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_native_unit_of_measurement = "people"

    @property
    def native_value(self):
        return self.coordinator.last_data
