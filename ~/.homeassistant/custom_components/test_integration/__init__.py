"""Test integration."""

DOMAIN = "test_integration"

async def async_setup(hass, config):
    """Set up the Test integration."""
    return True

async def async_setup_entry(hass, entry):
    """Set up Test integration from a config entry."""
    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    return True 