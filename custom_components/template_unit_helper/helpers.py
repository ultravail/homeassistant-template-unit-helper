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

    if source_unit is None or source_unit == "":
        source_unit = target_unit
    if target_unit is None or target_unit == "":
        target_unit = source_unit

    q = with_unit(hass, expr, source_unit)
    ex = None
    try:
        return q.to(target_unit).magnitude
    except Exception as e:  # noqa: BLE001
        ex = e
        if str(q.u).startswith("delta_"):
            try:
                # Try to add zero delta value to transform to "normal" unit
                return (
                    with_unit(hass, q + with_unit(hass, 0, str(q.u)[6:]))
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


def with_unit(hass: HomeAssistant, expr, unit: str | None = None):
    """Return a Pint Quantity object.

    Supports:
    - numeric or string values
    - TemplateState objects (states.sensor.xxx)
    - 2-element arrays [value, unit]
    """
    value = None
    value_unit = None

    # Check for 2-element array - [value, unit]
    if isinstance(expr, (list, tuple)) and len(expr) == 2:
        value, value_unit = expr
        expr = value

    if isinstance(expr, Q_):
        value = expr.magnitude
        value_unit = str(expr.u)

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

    if unit is None:
        unit = value_unit

    if unit is not None and value_unit is not None and unit != value_unit:
        value = to_unit(hass, value, unit, value_unit)

    if unit is not None:
        try:
            return Q_(float(str(value)), unit)
        except Exception:  # noqa: BLE001
            # value is not a string - ignore
            pass
    try:
        return Q_(str(value))
    except (
        ValueError,
        TypeError,
        pint.UndefinedUnitError,
        pint.DimensionalityError,
    ) as err:
        raise ValueError(
            f"with_unit failed with value={value!r}, unit={unit!r}, default_unit={default_unit!r}: {err}"
        ) from err
