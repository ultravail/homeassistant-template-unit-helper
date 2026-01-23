"""Helpers and custom filters for template unit conversions in Home Assistant."""

from homeassistant.components.light import PLATFORM_SCHEMA as LIGHT_PLATFORM_SCHEMA
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import template
from homeassistant.helpers.typing import ConfigType

from . import helpers

DOMAIN = "template_unit_helper"

# Initialization inspired by https://github.com/zvldz/ha_custom_filters

_TemplateEnvironment = template.TemplateEnvironment

# Validation of the user's configuration
PLATFORM_SCHEMA = LIGHT_PLATFORM_SCHEMA.extend({})

custom_filters = [
    helpers.from_unit,
    helpers.to_unit,
    helpers.with_unit,
    helpers.without_unit,
]

"""
async def async_setup(hass: HomeAssistant, config):
    # Register as global functions
    # template.global_functions["to_unit"] = lambda value, target: helpers.to_unit(value, target)
    # template.global_functions["convert"] = lambda value, from_u, to_u: helpers.convert(value, from_u, to_u)
    # template.global_functions["quantity"] = lambda value: helpers.quantity(value)
    template.global_functions["to_unit"] = helpers.to_unit
    template.global_functions["convert"] = helpers.convert
    template.global_functions["quantity"] = helpers.quantity

    # Register as filters (pipe support)
    template.Template.environment.filters["to_unit"] = helpers.to_unit
    template.Template.environment.filters["convert"] = helpers.convert
    template.Template.environment.filters["quantity"] = helpers.quantity

    template.TemplateEnvironment.hass_filter("reverse", my_reverse_filter)
    template.TemplateEnvironment.
    return True
"""


def add_custom_filter_function(custom_filter, *environments):
    """Add a function as global function and filter."""
    name = (
        custom_filter["name"]
        if isinstance(custom_filter, dict)
        else custom_filter.__name__
    )
    function = (
        custom_filter["function"] if isinstance(custom_filter, dict) else custom_filter
    )

    def _make_wrapper(func, env):
        def _wrapper(*args, **kwargs):
            return func(env.hass, *args, **kwargs)

        return _wrapper

    for env in environments:
        env.globals[name] = env.filters[name] = _make_wrapper(function, env)


def init(*args):
    """Initialize filters."""
    env = _TemplateEnvironment(*args)

    for f in custom_filters:
        add_custom_filter_function(f, env)

    return env


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Template Unit Helper from a config entry."""
    # Get a template instance to access the template environment
    tpl = template.Template("", hass)

    # Register all custom filters
    for f in custom_filters:
        add_custom_filter_function(f, tpl._env)  # noqa: SLF001

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Filters are registered globally, so we can't really unload them
    # But we return True to indicate the entry can be removed
    return True


async def async_setup(hass: HomeAssistant, hass_config: ConfigType) -> bool:
    """Set up Template Unit Helper (legacy support)."""
    # This is kept for backward compatibility but should not be needed
    # when using config flow
    return True


def main():
    """Executed during loading of integration."""
    template.TemplateEnvironment = init
    for f in custom_filters:
        add_custom_filter_function(f, template._NO_HASS_ENV)  # noqa: SLF001


main()
