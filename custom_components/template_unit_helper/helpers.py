"""Helpers for unit conversion and quantity handling using Pint.

This module provides functions to convert values between units and to
create Pint Quantity objects, supporting Home Assistant TemplateState,
numeric values, and [value, unit] arrays.
"""

import pint

from homeassistant.core import HomeAssistant
from homeassistant.helpers.template import TemplateState, TemplateEnvironment
from homeassistant.helpers.template.extensions.base import (
    BaseTemplateExtension,
    TemplateFunction,
)

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity
NO_DIMENSION = ureg.Unit('dimensionless')

class UnitHelperTemplateExtension(BaseTemplateExtension):

    def __init__(self, environment: TemplateEnvironment) -> None:
        """Initialize the area extension."""
        super().__init__(
            environment,
            functions=[
                TemplateFunction(
                    "from_unit",
                    self.from_unit,
                    as_global=True,
                    as_filter=True,
                    requires_hass=True,
                ),
                TemplateFunction(
                    "to_unit",
                    self.to_unit,
                    as_global=True,
                    as_filter=True,
                    requires_hass=True,
                ),
                TemplateFunction(
                    "with_unit",
                    self.with_unit,
                    as_global=True,
                    as_filter=True,
                    requires_hass=True,
                ),
                TemplateFunction(
                    "without_unit",
                    self.without_unit,
                    as_global=True,
                    as_filter=True,
                    requires_hass=True,
                ),
            ],
        )


    def from_unit(
        self,
        expr,
        source_unit: str | None = None,
        target_unit: str | None = None,
    ):
        """Convert numeric value between units."""
        return self.to_unit(expr, target_unit, source_unit)


    def to_unit(
        self,
        expr,
        target_unit: str | None = None,
        source_unit: str | None = None,
    ):
        """Convert a value to a target unit."""

        q = self.with_unit(expr, source_unit)
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
                        (q + self.with_unit(0, str(q.u)[6:]))
                        .to(target_unit)
                        .magnitude
                    )
                except Exception:  # noqa: BLE001
                    pass
        raise ValueError(
            f"Conversion failed with expr={q:~#P}, target_unit={target_unit!r}: {ex}"
        ) from ex


    def without_unit(self, expr):
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

    def try_float(self, s):
        try:
            return float(s)
        except:
            return s

    def with_unit(self, expr, target_unit: str | None = None):
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
                entity = Q_(self.try_float(value), value_unit)
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
                    state = self.hass.states.get(expr[7:])
                    if state is None:
                        raise ValueError(f"State {expr} not found")
                    expr = TemplateState(self.hass, state)
                else:
                    # Assume the string is a state name
                    state = self.hass.states.get(expr)
                    if state is None:
                        raise ValueError(f"State states.{expr} not found")
                    expr = TemplateState(self.hass, state)

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
                    entity = Q_(self.try_float(value))
                else:
                    entity = Q_(self.try_float(value), value_unit)
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
            return Q_(self.try_float(value), value_unit)
        except (
            ValueError,
            TypeError,
            pint.UndefinedUnitError,
            pint.DimensionalityError,
        ) as err:
            raise ValueError(
                f"Cannot convert expression '{value!r}' and unit '{value_unit!r}' to quantity: : {err}"
            ) from err
