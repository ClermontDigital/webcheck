"""Config flow for WebCheck integration."""
from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN

class WebCheckConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WebCheck."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title="WebCheck",
                data=user_input,
            )

        data_schema = vol.Schema({
            vol.Required("url"): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
        ) 