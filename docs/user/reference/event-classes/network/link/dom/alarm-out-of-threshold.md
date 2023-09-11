---
uuid: cc37a2fd-857d-4351-85ef-35caa572875c
---
# Network | Link | DOM | Alarm: Out of Threshold

DOM above or below threshold exceeded

## Symptoms

Connection lost

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
interface | str | {{ yes }} | Physical port
threshold | str | {{ no }} | Threshold type
sensor | str | {{ no }} | Measured name
ovalue | str | {{ no }} | Operating value
tvalue | str | {{ no }} | Threshold value

## Alarms

### Raising alarms

`Network | Link | DOM | Alarm: Out of Threshold` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| Link \| DOM \| Alarm: Out of Threshold](../../../../alarm-classes/network/link/dom/alarm-out-of-threshold.md) | dispose
