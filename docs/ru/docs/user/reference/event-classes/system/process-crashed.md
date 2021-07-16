---
uuid: 60740366-04b9-41e0-b9b9-33f083276c89
---
# System | Process Crashed

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
name | str | {{ yes }} | Process name
pid | str | {{ no }} | Process PID
status | str | {{ no }} | Exit status

## Alarms

### Raising alarms

`System | Process Crashed` events may raise following alarms:

Alarm Class | Description
--- | ---
[System \| Process Crashed](../../alarm-classes/system/process-crashed.md) | dispose
