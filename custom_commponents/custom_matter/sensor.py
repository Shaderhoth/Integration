"""Platform for Custom Matter sensor integration."""

from __future__ import annotations
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from .const import DOMAIN, LOGGER

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    matter_client = hass.data[DOMAIN].get("matter_client")
    nodes = matter_client.list_nodes()
    sensors = []

    for node in nodes:
        # Assuming the Matter node contains a temperature measurement cluster
        if "temperature" in node.clusters:
            sensors.append(CustomMatterSensor(matter_client, node))

    add_entities(sensors, True)

class CustomMatterSensor(SensorEntity):
    """Representation of a Matter sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, matter_client, node):
        """Initialize the sensor."""
        self._matter_client = matter_client
        self._node = node
        self._attr_name = f"Matter {node.name} Temperature"
        self._attr_unique_id = f"matter_sensor_{node.id}"

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            data = self._matter_client.get_node_data(self._node.id)
            self._attr_native_value = data.get("temperature")
        except Exception as err:
            LOGGER.error("Failed to fetch data from Matter server: %s", err)
