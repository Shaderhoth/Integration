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
    core = Core()
    port = entry.data.get("port")
    
    config_file = "AOP_6m_default.cfg"
    core.selectCfg(config_file)
    core.connectCom(port)
    core.sendCfg()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = core

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    core = hass.data[DOMAIN].pop(entry.entry_id, None)
    if core:
        core.parser.dataCom.close()

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
