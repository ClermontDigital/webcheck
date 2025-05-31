"""The WebCheck integration."""

import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_URL, CONF_NAME
from homeassistant.helpers import config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.device_registry import DeviceEntry

from .const import (
    DOMAIN,
    CONF_UPDATE_INTERVAL,
    CONF_WEBSITES,
    CONF_VERIFY_SSL,
    LOGGER,
)

_WEBSITES_SCHEMA = vol.All(
    cv.ensure_list,
    [
        vol.Schema(
            {
                vol.Required(CONF_URL): vol.Url(),
                vol.Optional(CONF_NAME): cv.string,
                vol.Optional(CONF_UPDATE_INTERVAL): cv.positive_int,
                vol.Optional(CONF_VERIFY_SSL, default=True): cv.boolean,
            }
        )
    ],
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_WEBSITES): _WEBSITES_SCHEMA,
                vol.Optional(CONF_UPDATE_INTERVAL, default=10): cv.positive_int,
            },
        ),
    },
    extra=vol.ALLOW_EXTRA,
)

PLATFORMS = ["binary_sensor"]


async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the WebCheck integration from YAML."""
    if DOMAIN not in config:
        return True

    # Process YAML configuration
    for website in config[DOMAIN][CONF_WEBSITES]:
        # Add to config entries if not already there
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": "import"},
                data={
                    CONF_URL: website[CONF_URL],
                    CONF_NAME: website.get(CONF_NAME),
                    CONF_UPDATE_INTERVAL: website.get(
                        CONF_UPDATE_INTERVAL, config[DOMAIN][CONF_UPDATE_INTERVAL]
                    ),
                    CONF_VERIFY_SSL: website.get(CONF_VERIFY_SSL, True),
                },
            )
        )
    
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up WebCheck from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Store the config entry data
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    # Forward the setup to the binary sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    # Forward the unloading to the binary sensor platform
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    # Remove the config entry data
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
    return unload_ok


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Remove a config entry from a device."""
    # Allow devices to be removed from the integration
    return True
