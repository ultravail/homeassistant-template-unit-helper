"""Helpers for unit conversion and quantity handling using Pint.

This module provides functions to convert values between units and to
create Pint Quantity objects, supporting Home Assistant TemplateState,
numeric values, and [value, unit] arrays.
"""

import pint

from homeassistant.helpers.template import TemplateState

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity


def from_unit(expr, source_unit: str | None = None, target_unit: str | None = None):
    """Convert numeric value between units."""
    return to_unit(expr, target_unit, source_unit)


def to_unit(expr, target_unit: str | None = None, source_unit: str | None = None):
    """Convert a value to a target unit."""

    if source_unit is None or source_unit == "":
        source_unit = target_unit
    if target_unit is None or target_unit == "":
        target_unit = source_unit

    q = with_unit(expr, source_unit)
    try:
        return q.to(target_unit).magnitude
    except Exception as e:
        raise ValueError(
            f"Conversion failed with expr={q:~#P}, target_unit={target_unit!r}: {e}"
        ) from e


def with_unit(expr, default_unit: str | None = None):
    """Return a Pint Quantity object.

    Supports:
    - numeric or string values
    - TemplateState objects (states.sensor.xxx)
    - 2-element arrays [value, unit]
    """
    value = None
    unit = None

    # Check for 2-element array - [value, unit]
    if isinstance(expr, (list, tuple)) and len(expr) == 2:
        value, unit = expr
        expr = value

    # Check for TemplateState
    if isinstance(expr, TemplateState):
        value = expr.state
        if unit is None:
            unit = expr.attributes.get("unit_of_measurement")
    else:
        value = expr

    if unit is not None:
        try:
            return Q_(float(str(value)), unit)
        except Exception:  # noqa: BLE001
            # value is not a string - ignore
            pass
    if default_unit is not None:
        try:
            return Q_(float(str(value)), default_unit)
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
