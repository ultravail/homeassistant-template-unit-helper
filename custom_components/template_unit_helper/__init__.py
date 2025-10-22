"""Helpers and custom filters for template unit conversions in Home Assistant."""

from homeassistant.components.light import PLATFORM_SCHEMA as LIGHT_PLATFORM_SCHEMA
from homeassistant.core import HomeAssistant
from homeassistant.helpers import template
from homeassistant.helpers.typing import ConfigType

from . import helpers

# Initialization inspired by https://github.com/zvldz/ha_custom_filters

_TemplateEnvironment = template.TemplateEnvironment

# Validation of the user's configuration
PLATFORM_SCHEMA = LIGHT_PLATFORM_SCHEMA.extend({})

custom_filters = [helpers.from_unit, helpers.to_unit, helpers.with_unit]

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
    for env in environments:
        env.globals[name] = env.filters[name] = function


def init(*args):
    """Initialize filters."""
    env = _TemplateEnvironment(*args)

    for f in custom_filters:
        add_custom_filter_function(f, env)

    return env


async def async_setup(hass: HomeAssistant, hass_config: ConfigType) -> bool:
    """Initialize filters."""
    config = hass_config["custom_filters"]  # noqa: F841
    tpl = template.Template("", hass)

    for f in custom_filters:
        add_custom_filter_function(f, tpl._env)  # noqa: SLF001

    # in configuration.yaml
    # custom_filters:
    #   custom_date_format: "%b %-d %Y, %-I:%M:%S %p"
    # if config["custom_date_format"]:
    #    add_custom_filter_function(get_format_date_function(config["custom_date_format"]), tpl._env, template._NO_HASS_ENV)
    return True


def main():
    """Executed during loading of integration."""
    template.TemplateEnvironment = init
    for f in custom_filters:
        add_custom_filter_function(f, template._NO_HASS_ENV)  # noqa: SLF001


main()
