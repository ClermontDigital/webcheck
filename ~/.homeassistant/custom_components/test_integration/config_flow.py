"""Config flow for Test integration."""
from homeassistant import config_entries

class TestIntegrationConfigFlow(config_entries.ConfigFlow, domain="test_integration"):
    """Handle a config flow for Test integration."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title="Test Integration",
                data={},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=None,
        ) 