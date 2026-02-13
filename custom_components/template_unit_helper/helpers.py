"""Helpers for unit conversion and quantity handling using Pint.

This module provides functions to convert values between units and to
create Pint Quantity objects, supporting Home Assistant TemplateState,
numeric values, and [value, unit] arrays.
"""

import pint

from homeassistant.core import HomeAssistant
from homeassistant.helpers.template import TemplateState

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity
NO_DIMENSION = ureg.Unit('dimensionless')

def from_unit(
    hass: HomeAssistant,
    expr,
    source_unit: str | None = None,
    target_unit: str | None = None,
):
    """Convert numeric value between units."""
    return to_unit(hass, expr, target_unit, source_unit)


def to_unit(
    hass: HomeAssistant,
    expr,
    target_unit: str | None = None,
    source_unit: str | None = None,
):
    """Convert a value to a target unit."""

    q = with_unit(hass, expr, source_unit)
    if target_unit is None or target_unit == source_unit:
        return q
    
    ex = None
    try:
        return q.to(target_unit).magnitude
    except Exception as e:  # noqa: BLE001
        ex = e
        if str(q.u).startswith("delta_"):
            try:
                # Try to add zero delta value to transform to "normal" unit
                return (
                    (q + with_unit(hass, 0, str(q.u)[6:]))
                    .to(target_unit)
                    .magnitude
                )
            except Exception:  # noqa: BLE001
                pass
    raise ValueError(
        f"Conversion failed with expr={q:~#P}, target_unit={target_unit!r}: {ex}"
    ) from ex


def without_unit(hass: HomeAssistant, expr):
    """Return the raw number without any conversion."""
    if isinstance(expr, (list, tuple)) and len(expr) == 2:
        value, _ = expr
    else:
        value = expr
    if isinstance(value, Q_):
        return value.magnitude
    if isinstance(value, TemplateState):
        return value.state
    try:
        return float(str(value))
    except Exception:  # noqa: BLE001
        pass
    return value

def with_unit(hass: HomeAssistant, expr, target_unit: str | None = None):
    """Return a Pint Quantity object.

    Supports:
    - numeric or string values
    - TemplateState objects (states.sensor.xxx)
    - 2-element arrays [value, unit]
    """
    value = None
    value_unit = None
    entity = None

    # if expression is a quantity object itself
    # then simply return it
    if isinstance(expr, Q_):
        entity = expr
        value = entity.magnitude
        value_unit = str(entity.u)
    # Check for 2-element array - [value, unit]
    elif isinstance(expr, (list, tuple)) and len(expr) == 2:
        value, value_unit = expr
        try:
            entity = Q_(value, value_unit)
            if entity.u == NO_DIMENSION:
                entity = None
        except err as Exception:
            raise ValueError(
                f"Cannot convert expression '{value!r}' and unit '{value_unit!r}' to quantity: : {err}"
            ) from err

    else:
        # If expression is text, then check
        # if the text is a state name
        if isinstance(expr, str):
            if expr.startswith("states."):
                state = hass.states.get(expr[7:])
                if state is None:
                    raise ValueError(f"State {expr} not found")
                expr = TemplateState(hass, state)
        # Check for TemplateState
        if isinstance(expr, TemplateState):
            value_unit = expr.attributes.get("unit_of_measurement")
            value = expr.state
        else:
            value = expr

    # End of parsing `expr` - from here onwards we
    # deal with `value`, optional `value_unit` and optional `entity`

    if entity is None:
        # try to convert to quantity
        try:
            if value_unit is None:
                entity = Q_(value)
            else:
                entity = Q_(value, value_unit)
            if entity.u == NO_DIMENSION:
                entity = None
        except:
            entity = None            
        if entity is not None:
            value_unit = str(entity.u)
            value = entity.magnitude
        elif target_unit is None:
            raise ValueError(
                f"Cannot convert '{expr!r}' without a unit"
            )
        else:
            value_unit = target_unit

    if value_unit is not None and target_unit is not None:
        try:
            u1 = pint.Unit(value_unit)
        except:
            raise ValueError(f"Unknown unit {value_unit!r}")
        try:        
            u2 = pint.Unit(target_unit)
        except:
            raise ValueError(f"Unknown unit {target_unit!r}")

        if u1 != u2:
            raise ValueError(
                f"Unit '{value_unit!r}' of expression does not match expected unit '{target_unit!r}'"
            )

    if entity is not None:
        return entity

    # once this point is reached we can safely assume that
    # we have to deal with `value` being a number and `target_unit`
    # being the unit
    try:
        return Q_(value, value_unit)
    except (
        ValueError,
        TypeError,
        pint.UndefinedUnitError,
        pint.DimensionalityError,
    ) as err:
        raise ValueError(
            f"Cannot convert expression '{value!r}' and unit '{value_unit!r}' to quantity: : {err}"
        ) from err