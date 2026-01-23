# Template Unit Helper

A Home Assistant **HACS integration** that provides **unit conversion and quantity math** using the [Pint](https://github.com/hgrecco/pint) library.


## How to install
> [!NOTE]
> I tested this integration with Home Assistant 2025.10. I have no idea if it works with older versions.

> [!IMPORTANT]
> After installing via HACS or manually, restart Home Assistant. Then go to **Settings → Devices & Services → Add Integration** and search for "Template Unit Helper" to complete the setup. No configuration.yaml entry is required.

### Via HACS
This custom template is compatible with [HACS](https://hacs.xyz/), which means that you can easily download and manage updates for it. Custom templates are available for download in HACS 2.0 and up, and on earlier versions in case experimental features are enabled. When you are on HACS 2.0 or higher or experimental features are enabled you can click the button below to add it to your HACS installation:
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ultravail&repository=homeassistant-template-unit-helper&category=template)

### Via HACS with custom repository
For a manual install you need to add this repository as custom repository:

1. Go to **HACS → Press "⋮" on the upper right corner → Choose menu item "Custom repositories"**
2. Add Repository:
   ```   
   https://github.com/ultravail/homeassistant-template-unit-helper.git
   ```
   with Type: **Integration**
 
3. Install `Template Unit Helper` and restart Home Assistant.
4. Go to **Settings → Devices & Services → Add Integration** and search for "Template Unit Helper" to complete the setup.

### Manual install
1. Copy the `custom_components/template_unit_helper` of this repository to the `custom_components` directory of your HomeAssistant installation.
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration** and search for "Template Unit Helper" to complete the setup.

## Usage in Templates

Supports:
- **TemplateState objects** (`states.sensor.xxx`)
- **Pint Quantity objects** (created with the help of `with_unit` helper)
- **numeric or string values** (`12`, `"5 kg"`)
- **2-element arrays** `[value, unit]`

> [!CAUTION]
> The **`states(...)`** helper is NOT supported (without explicitly providing a hard-coded unit) because this helper only returns a number without any reference to the unit or its original state. Use `with_unit` instead.

> [!TIP]
> Instead of using `states('sensor.my_sensor')` use `with_unit('states.sensor.my_sensor')` - note that you need to add the prefix `states.` to the name `sensor.my_sensor`.

> [!NOTE]
> When providing a plain number to any of the helper functions `to_unit`, `from_unit` or `without_unit`, those helpers will return that same number without any conversion. When providing a plain number to the helper `with_unit`, the unit will be `dimensionless`
 
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
