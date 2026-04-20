---
applyTo: "**/templates/**"
description: "Home Assistant Jinja2 template patterns for this project"
---

# Home Assistant Jinja2 Template Patterns

## HA-Specific Functions

```jinja2
states('sensor.foo')                    # state string, or 'unavailable'/'unknown'
state_attr('sensor.foo', 'attr')        # attribute value or none
is_state('sensor.foo', 'on')            # boolean
device_id('sensor.foo')                 # device UUID or none
device_entities('device-uuid')          # list of entity_ids for device
area_id('sensor.foo')                   # area UUID or none
area_entities('area-uuid')              # list of entity_ids in area
as_datetime('2024-01-15T10:00:00')      # datetime object or none
now()                                   # current datetime (TZ-aware)
has_value('sensor.foo')                 # true if not unavailable/unknown
```

## Safe Coercion — ALWAYS provide defaults

```jinja2
{{ s.state | float(100) }}              # ✅ default inline
{{ s.state | int(default=0) }}          # ✅ keyword form
{{ val | default(none) }}               # ✅ use when value may be missing
```

**Filter order rule:** `| int(default=0)` — NEVER `| int | default(0)` (wrong order)

## Namespace Pattern — required for loop variable mutation

```jinja2
{%- set ns = namespace(total=0, crit=0, low=0) -%}
{% for s in states.sensor %}
  {%- set ns.total = ns.total + 1 -%}
{% endfor %}
{{ ns.total }}
```

## Nested Namespace — for inner-loop mutation

```jinja2
{%- set outer_ns = namespace(result=[]) -%}
{% for item in items %}
  {%- set inner_ns = namespace(val='default') -%}
  {% for sub in item.subs %}
    {%- set inner_ns.val = sub -%}
  {% endfor %}
{%- endfor -%}
```

## Dict Building — dicts are immutable, use `dict()` merge

```jinja2
{%- set ns = namespace(lifespan={}) -%}
{# First entry for a key: #}
{%- set ns.lifespan = dict(ns.lifespan, **{key: {'count': 0, 'ages': []}}) -%}
{# Update existing entry: #}
{%- set current = ns.lifespan[key] -%}
{%- set ns.lifespan = dict(ns.lifespan, **{key: {'count': current.count + 1, 'ages': current.ages + [val]}}) -%}
```

## Whitespace Control

- `{%- -%}` — strip whitespace both sides (use inside loops to avoid blank lines)
- `{%- %}` — strip before only
- `{% -%}` — strip after only
- Output lines (markdown content) need `%}` (no trailing dash) to emit the newline
- Use `>-` scalar in YAML for multiline template variables (strips trailing newline)

## `>-` Scalar for Multiline Templates

```yaml
value_template: >-
  {% set v = states('sensor.foo') | float(0) %}
  {{ (v * 1.1) | round(2) }}
```

## Looping Over States

```jinja2
{%- for s in states.sensor
    | selectattr('entity_id', 'search', '_battery_plus')
    | rejectattr('entity_id', 'search', '_low')
    | rejectattr('state', 'in', ['unavailable', 'unknown']) -%}
  {%- set v = s.state | float(100) -%}
{%- endfor -%}
```

## Dict/List Filters

```jinja2
items | map(attribute='btype') | unique | sort
items | selectattr('btype', 'eq', 'AA') | map(attribute='count') | sum
items | sort(attribute='count', reverse=true)
```

## Testing

Use **Developer Tools > Template** in HA UI to test before committing.
Templates that reference `states.sensor` need HA running with real entities.

## Confidence Labels (live research outputs)

- 🟢 Verified live — confirmed against fetched source
- 🟡 Reasonable inference — consistent with live source, not directly stated
- 🔴 Speculative — not verified; flag before applying to production
