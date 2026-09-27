"""Helpers and custom filters for template unit conversions in Home Assistant."""

import logging
logger = logging.getLogger(__name__)
logger.info(f"Template Unit Helper integration startup")

from homeassistant.components.template import DOMAIN as TEMPLATE_DOMAIN
from homeassistant.components.template import SERVICE_RELOAD as TEMPLATE_SERVICE_RELOAD

from homeassistant.exceptions import ServiceNotFound
from homeassistant.components.light import PLATFORM_SCHEMA as LIGHT_PLATFORM_SCHEMA
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import template
from homeassistant.helpers.template.extensions.base import (
    BaseTemplateExtension,
    TemplateFunction,
)
from homeassistant.helpers.typing import ConfigType

from . import helpers

DOMAIN = "template_unit_helper"

# Validation of the user's configuration
PLATFORM_SCHEMA = LIGHT_PLATFORM_SCHEMA.extend({})

# Keep a global flag to prevent registering the extension multiple times on reload
_EXTENSION_LOADED = False

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Template Unit Helper from a config entry."""
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Filters are registered globally, so we can't really unload them
    # But we return True to indicate the entry can be removed
    return True


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the template extension at the absolute earliest core stage."""
    global _EXTENSION_LOADED

    if not _EXTENSION_LOADED:
        logger.info("Injecting UnitHelperTemplateExtension into Home Assistant template engine...")

        for key in (template._ENVIRONMENT, template._ENVIRONMENT_LIMITED, template._ENVIRONMENT_STRICT):
            if (env := hass.data.pop(key, None)) is not None:
                # Ensure any templates holding onto the cached env get the extension.
                env.add_extension(helpers.UnitHelperTemplateExtension)
                logger.info(f"removed cached TemplateEnvironment for {key}")
        
        _EXTENSION_LOADED = True

        # 3. Force template entities to reload.
        # Now that the environment possesses your 'from_unit', 'to_unit' etc.,
        # this reload will instantly restore the "Not provided" UI helpers to operational status.
        if hass.services.has_service(TEMPLATE_DOMAIN, TEMPLATE_SERVICE_RELOAD):
            logger.info(f"Requesting {TEMPLATE_DOMAIN}.{TEMPLATE_SERVICE_RELOAD} ...")
            await hass.services.async_call(
                TEMPLATE_DOMAIN,
                TEMPLATE_SERVICE_RELOAD,
                blocking=False
            )
        template_entries = hass.config_entries.async_entries("template")
        for entry in template_entries:
            logger.info(f"Reloading Template Config Entry: {entry.entry_id}")
            await hass.config_entries.async_reload(entry.entry_id)

    """
    The worst-case scenario would be to reload the template component.
    As of now I think this is not necessary. Besides that, I think the async_call
    to TEMPLATE_SERVICE_RELOAD does exactly the same as below code.

    #template_component = hass.data.get(TEMPLATE_DOMAIN)
    #if template_component:
    #    # This triggers a reload of the underlying entity definitions
    #    await template_component.async_reload()
    """

    return True    


_TE = template.TemplateEnvironment

class UnitHelperTemplateEnvironment(_TE):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_extension(helpers.UnitHelperTemplateExtension)

logger.info(f"Injecting early Template environment for Template Unit Helper")

# This needs to happen before async_setup() etc, so that the environment is hooked before
# instances are cached in core. But also see cache management above.
template.TemplateEnvironment = UnitHelperTemplateEnvironment

# Home Assistant uses a set of extensions internally
# We add our extension
if hasattr(template, "_ALL_EXTENSIONS"): 
    template._ALL_EXTENSIONS.append(helpers.UnitHelperTemplateExtension)