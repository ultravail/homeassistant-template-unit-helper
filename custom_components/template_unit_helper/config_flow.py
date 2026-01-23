"""Config flow for Template Unit Helper integration."""

from homeassistant import config_entries

from . import DOMAIN


class TemplateUnitHelperConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Template Unit Helper."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # Check if already configured
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        # No user input needed - create entry immediately
        return self.async_create_entry(title="Template Unit Helper", data={})

    async def async_step_import(self, user_input=None):
        """Handle import from configuration.yaml."""
        return await self.async_step_user(user_input)
