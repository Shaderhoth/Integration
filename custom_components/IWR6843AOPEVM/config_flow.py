import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_DEVICE_PATH

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_DEVICE_PATH, default="/dev/ttyUSB0"): str
})

class ConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="IWR6843AOPEVM Radar", data=user_input)
        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)
