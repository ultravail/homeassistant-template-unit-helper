from homeassistant.core import HomeAssistant
from homeassistant.helpers import template
from . import helpers

async def async_setup(hass: HomeAssistant, config):
    """Set up Template Unit Helper."""

    # Register as global functions
    template.global_functions["to_unit"] = lambda value, target: helpers.to_unit(value, target)
    template.global_functions["convert"] = lambda value, from_u, to_u: helpers.convert(value, from_u, to_u)
    template.global_functions["quantity"] = lambda value: helpers.quantity(value)

    # Register as filters (pipe support)
    template.Template.environment.filters["to_unit"] = lambda value, target: helpers.to_unit(value, target)
    template.Template.environment.filters["convert"] = lambda value, from_u, to_u: helpers.convert(value, from_u, to_u)
    template.Template.environment.filters["quantity"] = lambda value: helpers.quantity(value)

    return True
