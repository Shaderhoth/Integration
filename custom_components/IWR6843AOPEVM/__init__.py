"""Custom integration to integrate radar_reader with Home Assistant."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN
from .radar_reader import Core

PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the radar integration from a config entry."""
    # Create a Core instance and connect to the radar device
    core = Core()
    port = entry.data.get("port")  # Retrieve the COM port from configuration
    core.connectCom(port)

    # Store the Core instance in Home Assistant's data storage
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = core

    # Set up the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Retrieve the Core instance and close the connection
    core = hass.data[DOMAIN].pop(entry.entry_id, None)
    if core:
        core.parser.dataCom.close()

    # Unload the sensor platform
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
