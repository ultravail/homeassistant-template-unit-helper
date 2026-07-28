"""Helpers and custom filters for template unit conversions in Home Assistant."""

import logging

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

logger = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Template Unit Helper from a config entry."""
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Filters are registered globally, so we can't really unload them
    # But we return True to indicate the entry can be removed
    return True


async def async_setup(hass: HomeAssistant, hass_config: ConfigType) -> bool:
    """Set up Template Unit Helper (legacy support)."""
    # Depending on load order, a TemplateEnvironment may be created & cached before the hook below
    # is executed, thus missing our extension.  Nuke the cache just in case.
    for key in (template._ENVIRONMENT, template._ENVIRONMENT_LIMITED, template._ENVIRONMENT_STRICT):
        if (env := hass.data.pop(key, None)) is not None:
            logger.warning(f"removed cached TemplateEnvironment for {key}")
            # Ensure any templates holding onto the cached env get the extension.
            env.add_extension(helpers.UnitHelperTemplateExtension)
    return True


_TE = template.TemplateEnvironment

class UnitHelperTemplateEnvironment(_TE):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_extension(helpers.UnitHelperTemplateExtension)

# This needs to happen before async_setup() etc, so that the environment is hooked before
# instances are cached in core. But also see cache management above.
template.TemplateEnvironment = UnitHelperTemplateEnvironment
