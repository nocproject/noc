---
uuid: 10747532-86a8-4ed2-8e81-fa92a571b310
---
# Network | Link | Link Flap Error Detected

Link-flap error detected

## Symptoms

Connection lost

## Probable Causes

Cable damage, hardware or software error either from this or from another side

## Recommended Actions

Check both sides of links and hardware

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
interface | interface_name | {{ yes }} | Affected interface

## Alarms

### Raising alarms

`Network | Link | Link Flap Error Detected` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| Link \| Err-Disable](../../../alarm-classes/network/link/err-disable.md) | dispose
