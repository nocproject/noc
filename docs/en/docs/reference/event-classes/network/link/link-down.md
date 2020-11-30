---
uuid: 358bf8ed-81ce-4e92-8d05-adc3817edbda
---
# Network | Link | Link Down

Link Down

## Symptoms

Connection lost

## Probable Causes

Administrative action, cable damage, hardware or software error either from this or from another side

## Recommended Actions

Check configuration, both sides of links and hardware

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
interface | interface_name | {{ yes }} | Affected interface

## Alarms

### Raising alarms

`Network | Link | Link Down` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| Link \| Link Down](../../../alarm-classes/network/link/link-down.md) | dispose
