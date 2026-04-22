# Evening AI Summary Automation — Structured Output Design
**Date:** 2026-04-15  
**Author:** Vision (AI & Emerging Tech Specialist)  
**For Implementation By:** Iron Man  
**Status:** Ready for implementation

## Context

This automation uses Home Assistant 2026.x's `ai_task.generate_data` action with the `structure` parameter to return **typed, deterministic output** instead of free-text LLM responses. The structured approach makes automation branching predictable and eliminates parsing failures.

**Key Benefits:**
- ✅ Typed fields accessible via `result.data.{field_name}`
- ✅ No need to parse markdown/JSON from free-text responses
- ✅ Deterministic automation logic — if fields exist, they're valid strings
- ✅ LLM constrained to return only the requested structure

**Deployment Details:**
- Ollama running at `http://localhost:11434` with model `llama3.2:3b`
- Two HA integrations configured: "Ollama Chat" and "Ollama Control" (dual-config pattern)
- Person entities: `person.jeff`, `person.patricia`
- Notification services: `notify.mobile_app_jeff`, `notify.mobile_app_patricia`
- Primary modes: `input_select.presence_mode` (Home/Away/Vacation), `input_select.time_of_day`
- Weather entity: `weather.forecast_home`
- Lock entities: `lock.touchscreen_deadbolt_front_door`, `lock.touchscreen_deadbolt_back_door`, `lock.touchscreen_deadbolt_kitchen_entry`

---

## Complete Automation YAML

**File:** `home-assistant/config/automations/evening_ai_summary.yaml`

```yaml
---
alias: "Evening AI Summary"
description: >-
  Daily evening summary using ai_task.generate_data with structured output.
  Sends a typed summary to Jeff and Patricia at 21:00 when presence_mode is Home.
  Uses weather, lock states, and mode data to generate contextual insights.

trigger:
  - platform: time
    at: "21:00:00"

condition:
  - condition: state
    entity_id: input_select.presence_mode
    state: "Home"

action:
  - action: ai_task.generate_data
    data:
      task_name: "evening_summary"
      instructions: >-
        You are a smart home assistant providing a brief evening summary to the homeowners.
        
        Current Status:
        - Jeff is {{ states('person.jeff') }}
        - Patricia is {{ states('person.patricia') }}
        - Presence Mode: {{ states('input_select.presence_mode') }}
        - Time of Day: {{ states('input_select.time_of_day') }}
        - Guest Mode: {{ states('input_boolean.guest_mode') }}
        - Work from Home Mode: {{ states('input_boolean.work_from_home_mode') }}
        - Weather: {{ state_attr('weather.forecast_home', 'temperature') }}°{{ state_attr('weather.forecast_home', 'temperature_unit') }}, {{ states('weather.forecast_home') }}
        - Front Door Lock: {{ states('lock.touchscreen_deadbolt_front_door') }}
        - Back Door Lock: {{ states('lock.touchscreen_deadbolt_back_door') }}
        - Kitchen Entry Lock: {{ states('lock.touchscreen_deadbolt_kitchen_entry') }}
        
        Generate a concise evening summary with:
        1. A friendly 2-sentence home status (presence, weather, general vibe)
        2. A one-line security note (lock status — mention only if any are unlocked)
        3. A short note about tomorrow based on current modes (e.g., WFH mode on, guest mode active)
        
        Keep it natural and conversational. Don't repeat data verbatim — synthesize it into useful insights.
      structure:
        summary:
          type: string
          description: "2-sentence friendly home status summary"
        security_note:
          type: string
          description: "One-line lock/security status — mention only if attention needed"
        tomorrow_note:
          type: string
          description: "Short note about tomorrow based on current modes/schedule"
    response_variable: evening_data

  - action: notify.mobile_app_jeff
    data:
      title: "🏡 Evening Summary"
      message: >-
        {{ evening_data.data.summary }}
        
        🔒 {{ evening_data.data.security_note }}
        
        📅 {{ evening_data.data.tomorrow_note }}

  - action: notify.mobile_app_patricia
    data:
      title: "🏡 Evening Summary"
      message: >-
        {{ evening_data.data.summary }}
        
        🔒 {{ evening_data.data.security_note }}
        
        📅 {{ evening_data.data.tomorrow_note }}

mode: single
```

---

## Structure Parameter Format (HA 2026.x)

The `structure` parameter uses a **JSON Schema-like format** to define the expected output:

```yaml
structure:
  field_name:
    type: string | number | boolean | object | array
    description: "Human-readable field purpose (helps LLM understand intent)"
    # Optional: enum, min, max, items (for arrays/objects)
```

**Key Points:**
1. **Type enforcement:** LLM output is validated against the schema
2. **Description is critical:** Guides the LLM on what content to generate for each field
3. **Access pattern:** `response_variable.data.field_name` in templates
4. **Failure handling:** If LLM can't generate valid structure, action fails (automation stops)

**Supported Types:**
- `string` — Text content (most common)
- `number` — Numeric values
- `boolean` — True/false
- `object` — Nested structures (use sparingly)
- `array` — Lists (use sparingly)

**Best Practice:** Keep structures flat (3-5 string fields) for best LLM reliability.

---

## Fallback Handling

If `ai_task` is unavailable (Ollama down, integration broken), the automation will fail silently. For production resilience, add a `try`/`catch` pattern:

```yaml
action:
  - choose:
      - conditions:
          - condition: template
            value_template: "{{ is_state('conversation.ollama_control', 'unavailable') }}"
        sequence:
          - action: notify.mobile_app_jeff
            data:
              title: "🏡 Evening Summary (Fallback)"
              message: >-
                Home: {{ states('input_select.presence_mode') }}, {{ states('input_select.time_of_day') }}
                Weather: {{ state_attr('weather.forecast_home', 'temperature') }}°
                Locks: {% if is_state('lock.touchscreen_deadbolt_front_door', 'unlocked') %}⚠️ Front unlocked{% endif %}
          - action: notify.mobile_app_patricia
            data:
              title: "🏡 Evening Summary (Fallback)"
              message: >-
                Home: {{ states('input_select.presence_mode') }}, {{ states('input_select.time_of_day') }}
                Weather: {{ state_attr('weather.forecast_home', 'temperature') }}°
                Locks: {% if is_state('lock.touchscreen_deadbolt_front_door', 'unlocked') %}⚠️ Front unlocked{% endif %}
    default:
      - action: ai_task.generate_data
        # ... (full action from above)
```

**Note for Iron Man:** I've kept the primary YAML simple for clarity. If you want the fallback version, use the `choose` pattern above.

---

## Implementation Checklist

- [ ] Verify Ollama integration "Ollama Control" is configured and available
- [ ] Test `ai_task.generate_data` manually in Developer Tools → Actions
- [ ] Create file: `home-assistant/config/automations/evening_ai_summary.yaml`
- [ ] Restart Home Assistant or reload automations
- [ ] Test trigger manually at 21:00 or use Developer Tools → Automations → Run
- [ ] Verify notifications arrive on both phones with structured content
- [ ] Monitor HA logs for any `ai_task` errors on first run

---

## Expected Output Example

**Title:** 🏡 Evening Summary

**Message:**
```
Everyone's home and settled in for the evening. Weather is mild at 72°F with clear skies — perfect for a quiet night.

🔒 All entry points secured — front, back, and kitchen locks engaged.

📅 Work from Home mode is active — your office setup is ready for tomorrow morning.
```

---

## Why This Pattern Matters

Traditional LLM automations rely on free-text parsing:
```yaml
# OLD WAY — brittle, parsing-dependent
- action: conversation.process
  data:
    text: "Summarize home status"
  response_variable: result
- action: notify.mobile_app_jeff
  data:
    message: "{{ result.response.speech.plain.speech }}"  # ← unstructured blob
```

**Problems:**
- LLM might return markdown, bullet lists, or variable formats
- No guarantee of specific information (locks? weather? modes?)
- Parsing failures break automations
- Can't branch logic on specific fields

**New `structure` pattern:**
```yaml
# NEW WAY — typed, deterministic
- action: ai_task.generate_data
  data:
    structure:
      security_status: { type: string }
  response_variable: result
- condition: template
  value_template: "{{ 'unlocked' in result.data.security_status }}"
  # ← Reliable conditional logic!
```

**Benefits:**
- Guaranteed field presence
- Type safety (string/number/boolean)
- LLM constrained to requested format
- Automation logic is predictable

---

## Next Steps After Implementation

1. **Monitor first run** — Check HA logs for `ai_task` execution time (should be <5 seconds with llama3.2:3b)
2. **Iterate prompt** — Refine `instructions` based on actual LLM output quality
3. **Add conditional logic** — Use `result.data.security_note` to trigger extra actions (e.g., send critical alert if locks unlocked)
4. **Expand structure** — Add fields like `battery_warnings`, `maintenance_items` as needed

---

**Ready for Iron Man to implement.** Questions? Ping Vision via squad:yen label.
