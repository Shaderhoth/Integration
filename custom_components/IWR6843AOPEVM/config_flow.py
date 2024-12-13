from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from .const import DOMAIN, DEFAULT_DATA_DEVICE_PATH, DEFAULT_CLI_DEVICE_PATH

class RadarFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Radar Integration."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data={
                    "cli": user_input["cli"],
                    "port": user_input["port"],
                    CONF_NAME: user_input[CONF_NAME],
                },
            )

        data_schema = vol.Schema(
            {
                vol.Required("cli", default=DEFAULT_CLI_DEVICE_PATH): str,
                vol.Required("port", default=DEFAULT_DATA_DEVICE_PATH): str,
                vol.Required(CONF_NAME, default="Radar Sensor"): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
