---
uuid: 71faba70-4890-455b-af5b-295215979359
---
# Network | Link | DOM | Warning: Out of Threshold

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

`Network | Link | DOM | Warning: Out of Threshold` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| Link \| DOM \| Warning: Out of Threshold](../../../../alarm-classes/network/link/dom/warning-out-of-threshold.md) | dispose
