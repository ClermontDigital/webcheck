"""Config flow for WebCheck integration."""
import logging
import voluptuous as vol
from urllib.parse import urlparse

from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_URL
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_UPDATE_INTERVAL,
    CONF_VERIFY_SSL,
)

_LOGGER = logging.getLogger(__name__)

class WebCheckConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WebCheck."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate URL
            try:
                result = urlparse(user_input[CONF_URL])
                if all([result.scheme, result.netloc]):
                    # Check if this URL is already configured
                    await self.async_set_unique_id(user_input[CONF_URL])
                    self._abort_if_unique_id_configured()
                    
                    # URL is valid, create entry
                    return self.async_create_entry(
                        title=user_input.get(CONF_NAME, result.netloc),
                        data=user_input,
                    )
                else:
                    errors["base"] = "invalid_url"
            except ValueError:
                errors["base"] = "invalid_url"

        # Show form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_URL): str,
                vol.Optional(CONF_NAME): str,
                vol.Optional(CONF_UPDATE_INTERVAL, default=10): cv.positive_int,
                vol.Optional(CONF_VERIFY_SSL, default=True): bool,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
        
    async def async_step_import(self, user_input=None):
        """Handle import from YAML."""
        if user_input is not None:
            # Check if this URL is already configured
            await self.async_set_unique_id(user_input[CONF_URL])
            self._abort_if_unique_id_configured()
            
            # Import the entry
            return self.async_create_entry(
                title=user_input.get(CONF_NAME, urlparse(user_input[CONF_URL]).netloc),
                data=user_input,
            )
        
        return self.async_abort(reason="unknown") 