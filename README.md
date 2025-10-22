# Template Unit Helper v2

A Home Assistant **HACS integration** that provides **unit conversion and quantity math** using the [Pint](https://github.com/hgrecco/pint) library.

## 🧩 Installation (via HACS)
1. Go to **HACS → Integrations → ⋮ → Custom repositories**
2. Add:
   ```
   https://github.com/ultravail/template-unit-helper
   ```
   Type: **Integration**
3. Install and restart Home Assistant.

## ⚙️ Usage in Templates

Supports:
- **TemplateState objects** (`states.sensor.xxx`)
- **numeric or string values** (`12`, `"5 kg"`)
- **2-element arrays** `[value, unit]`

### Examples

```jinja2
# Convert a sensor directly
{{ to_unit(states.sensor.temperature, 'K') }}

# Convert numeric or string values manually
{{ to_unit(12, 'cm') }}
{{ to_unit('5 m', 'cm') }}

# Convert using 2-element array [value, unit]
{{ to_unit([12, 'm'], 'cm') }}
{{ to_unit([states.sensor.temperature.state, '°C'], 'K') }}

# Create quantity objects
{{ quantity(states.sensor.temperature) }}
{{ quantity([5, 'kg']) }}
{{ quantity('12 m') }}

# Using convert helper
{{ convert(3, 'hour', 'minutes') }}

# Using pipe syntax
{{ states.sensor.temperature | to_unit('K') }}
{{ 12 | to_unit('cm') }}
```

---

**Author:** @ultravail  
**License:** MIT
