# Template Unit Helper v2

A Home Assistant **HACS integration** that provides **unit conversion and quantity math** using the [Pint](https://github.com/hgrecco/pint) library.

## 🧩 Installation (via HACS)
1. Go to **HACS → Press "⋮" on the upper right corner → Choose menu item "Custom repositories"**
2. Add Repository:
   ```   
   https://github.com/ultravail/homeassistant-template-unit-helper.git
   ```
   with Type: **Integration**
3. Install and restart Home Assistant.

## ⚙️ Usage in Templates

Supports:
- **TemplateState objects** (`states.sensor.xxx`)
- **numeric or string values** (`12`, `"5 kg"`)
- **2-element arrays** `[value, unit]`

The `with_unit` helper returns a [Pint Quantity](https://pint.readthedocs.io/en/stable/api/base.html#pint.Quantity). The helpers `to_unit` and `from_unit` return plain numbers. The helper `without_unit` returns the value in the current unit.

### Examples

```jinja2
# Convert a sensor directly
{{ to_unit(states.sensor.temperature, 'K') }}

# Calculations with sensors
{{ (with_unit(states.sensor.temperature) - with_unit('7 K')) }}
{{ (with_unit('states.sensor.temperature') - with_unit('7 K')) }}
{{ with_unit('states.sensor.temperature') == with_unit(states.sensor.temperature) == with_unit(states('sensor.temperature'), state_attr('sensor.temperature', 'unit_of_measurement')) }}

# Convert numeric or string values manually
# to_unit(expr, target_unit, default_unit = None)
{{ to_unit('5 m', 'cm') == 500 }}
{{ to_unit(5, 'cm', 'm') == 500 }}
{{ to_unit('5m', 'cm', 'cm') == 500 }}
{{ to_unit('5', 'cm', 'm') == 500 }}

# Convert using 2-element array [value, default_unit]
{{ to_unit([12, 'm'], 'cm') == 1200 }}
{{ to_unit([states.sensor.temperature.state, '°C'], 'K') }}

# Create quantity objects
# with_unit(expr, target_unit=None)
{{ with_unit(states.sensor.temperature) }}
{{ with_unit([5, 'kg']) | to_unit('g') == 5000 }}
{{ with_unit('12 m') == '12 m' }}

# Using from_unit helper
# from_unit(expr, source_unit, target_unit)
# 3 hours to minutes -> 180
{{ from_unit(3, 'hour', 'minutes') == 180 }}

# Using pipe syntax
{{ states.sensor.temperature | to_unit('K') }}
{{ (12 | from_unit('m', 'cm')) == (12 | to_unit('cm', 'm')) == (1200) }}

# Removing units
{{ (with_unit(100, '°C') - with_unit(7, '°C')) | without_unit == 93 }}

# Temperature arithmetic
{{ (with_unit(100, '°C') - with_unit(7, 'Δ°C')) | to_unit('°C') == 93 }}

# Variants and conversions
{{ from_unit(4, 'm', 'cm') == with_unit(4, 'm') | to_unit('cm') }}
{{ to_unit('5 m', 'cm') == to_unit(5, 'cm', 'm') == from_unit(5, 'm', 'cm') == to_unit(5, 'm') }}
# 3 hours - 30 minuts = 9000 seconds
{{ (with_unit(3, 'hours') - with_unit(30, 'minutes')) | to_unit('seconds') == to_unit(9000, 'seconds') == 9000 }}

```

---

**Author:** @ultravail  
**License:** MIT
