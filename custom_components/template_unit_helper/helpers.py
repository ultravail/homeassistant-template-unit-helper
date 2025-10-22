import pint
from homeassistant.helpers.template import TemplateState

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity

def to_unit(value, target_unit: str):
    """Convert a value to a target unit."""

    q = quantity(value)
    if q is None:
        return None
    else:
        return q.to(target_unit).magnitude

def quantity(value):
    """Return a Pint Quantity object.
    Supports:
    - numeric or string values
    - TemplateState objects (states.sensor.xxx)
    - 2-element arrays [value, unit]    
    """

    # 2-element array
    if isinstance(value, (list, tuple)) and len(value) == 2:
        val, unit = value
        try:
            return Q_(float(val), unit)
        except Exception as e:
            raise ValueError(f"quantity failed with value={val!r}, unit={unit!r}: {e}")

    # TemplateState
    if isinstance(value, TemplateState):
        val = value.state
        unit = value.attributes.get("unit_of_measurement")
        if unit is None:
            # Overwrite value and fail over to the last (single value) resort
            value = val
        else:
            try:
                return Q_(float(val), unit)
            except Exception as e:
                raise ValueError(f"quantity failed with value={val!r}, unit={unit!r}: {e}")

    # Single value
    try:
        return Q_(float(value))
    except Exception:
        try:
            return Q_(value)
        except Exception as e:
            raise ValueError(f"Cannot parse value={value!r}: {e}")

def convert(value, from_unit: str, to_unit: str):
    """Convert numeric value between units."""
    try:
        q = Q_(float(value), from_unit)
        return q.to(to_unit).magnitude
    except Exception:
        return None
